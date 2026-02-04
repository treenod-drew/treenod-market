#!/usr/bin/env python3
"""S3 file uploader with CloudFront cache invalidation."""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    get_config,
    get_s3_client,
    get_cloudfront_client,
    get_content_type,
    format_size,
    build_s3_key,
    build_public_url,
    file_exists_in_s3,
    get_file_metadata,
    generate_filename,
)


def suggest_rename(filename, iteration=1):
    """Suggest renamed version of file."""
    path = Path(filename)
    stem = path.stem
    suffix = path.suffix
    today = datetime.now().strftime('%Y-%m-%d')

    if iteration == 1:
        return f"{stem}_{today}{suffix}"
    else:
        return f"{stem}_{today}_{iteration}{suffix}"


def handle_duplicate(filename, metadata, force):
    """Handle duplicate file. Returns (should_upload, new_filename)."""
    if force:
        return True, filename

    print(f"\nFile already exists: {filename}")
    print(f"Size: {format_size(metadata['size'])}, Modified: {metadata['last_modified'].strftime('%Y-%m-%d %H:%M')}")
    print(f"URL: {build_public_url(filename)}")

    suggested = suggest_rename(filename)
    print("\nOptions:")
    print("  [1] Overwrite")
    print(f"  [2] Rename to: {suggested}")
    print("  [3] Custom name")
    print("  [4] Cancel")

    while True:
        choice = input("\nChoose [1-4]: ").strip()

        if choice == '1':
            return True, filename
        elif choice == '2':
            iteration = 1
            new_name = suggested
            while file_exists_in_s3(new_name):
                iteration += 1
                new_name = suggest_rename(filename, iteration)
            return True, new_name
        elif choice == '3':
            custom = input("Enter filename: ").strip()
            if not custom:
                print("Invalid filename")
                continue
            if not Path(custom).suffix:
                custom += Path(filename).suffix
            return True, custom
        elif choice == '4':
            return False, None
        else:
            print("Invalid choice")


def upload_file(file_path, key_name=None, auto_name=False, description=None,
                force=False, invalidate=False):
    """Upload file to S3."""
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return False

    config = get_config()
    bucket = config['bucket']

    local_filename = os.path.basename(file_path)

    # Determine upload filename
    if auto_name:
        upload_filename = generate_filename(local_filename, description)
        if not upload_filename:
            return False
    else:
        upload_filename = key_name or local_filename

    # Check duplicate
    if not force and file_exists_in_s3(upload_filename):
        metadata = get_file_metadata(upload_filename)
        should_upload, new_filename = handle_duplicate(upload_filename, metadata, force)

        if not should_upload:
            print("Upload cancelled")
            return False

        upload_filename = new_filename

    s3_key = build_s3_key(upload_filename)

    try:
        s3_client = get_s3_client()
        content_type = get_content_type(upload_filename)

        print(f"\nUploading {local_filename} -> {upload_filename}")

        s3_client.upload_file(
            file_path,
            bucket,
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )

        print(f"Uploaded: s3://{bucket}/{s3_key}")

        if invalidate:
            invalidate_cache([upload_filename])

        public_url = build_public_url(upload_filename)
        print(f"URL: {public_url}")

        return True

    except Exception as e:
        print(f"Upload failed: {e}")
        return False


def invalidate_cache(filenames):
    """Invalidate CloudFront cache."""
    config = get_config()
    distribution_id = config['distribution_id']

    paths = [f"/{f}" for f in filenames]

    try:
        cf_client = get_cloudfront_client()

        print(f"\nInvalidating cache for {len(filenames)} file(s)")

        response = cf_client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': f"s3upload-{datetime.now().isoformat()}"
            }
        )

        inv_id = response['Invalidation']['Id']
        print(f"Invalidated: {', '.join(paths)} (ID: {inv_id})")

        return True

    except Exception as e:
        print(f"Invalidation failed: {e}")
        return False


def delete_file(filename, force=False):
    """Delete file from S3."""
    config = get_config()
    bucket = config['bucket']
    s3_key = build_s3_key(filename)

    try:
        s3_client = get_s3_client()

        # Check if file exists
        if not file_exists_in_s3(filename):
            print(f"File not found: {filename}")
            return False

        # Confirm deletion
        if not force:
            print(f"\nDelete file: {filename}")
            print(f"URL: {build_public_url(filename)}")

            # Check if stdin is available (interactive mode)
            if not sys.stdin.isatty():
                print("Error: Non-interactive mode requires --force flag")
                return False

            confirm = input("Confirm deletion? (yes/no): ").strip().lower()

            if confirm not in ['yes', 'y']:
                print("Deletion cancelled")
                return False

        s3_client.delete_object(Bucket=bucket, Key=s3_key)
        print(f"Deleted: s3://{bucket}/{s3_key}")

        return True

    except Exception as e:
        print(f"Delete failed: {e}")
        return False


def list_files():
    """List files in S3 bucket."""
    config = get_config()
    bucket = config['bucket']
    prefix = config['prefix']

    try:
        s3_client = get_s3_client()

        print(f"\nFiles in s3://{bucket}/{prefix}\n")

        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            print("No files found")
            return

        print(f"{'Filename':<30} {'Size':<10} {'Modified':<20} {'URL'}")
        print("-" * 100)

        for obj in response['Contents']:
            key = obj['Key']
            filename = key.replace(prefix, '')

            if not filename:
                continue

            size = format_size(obj['Size'])
            modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M')
            url = build_public_url(filename)

            print(f"{filename:<30} {size:<10} {modified:<20} {url}")

        count = len([o for o in response['Contents'] if o['Key'] != prefix])
        print(f"\nTotal: {count} files")

    except Exception as e:
        print(f"List failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='S3 file uploader')
    subparsers = parser.add_subparsers(dest='command')

    # Upload
    upload_parser = subparsers.add_parser('upload')
    upload_parser.add_argument('file')
    upload_parser.add_argument('--key', help='Custom S3 key name')
    upload_parser.add_argument('--auto-name', action='store_true', help='Auto-generate filename with branch and description')
    upload_parser.add_argument('--description', help='Report description for auto-naming')
    upload_parser.add_argument('--force', action='store_true', help='Skip duplicate check')
    upload_parser.add_argument('--invalidate', action='store_true', help='Invalidate cache')

    # Invalidate
    inv_parser = subparsers.add_parser('invalidate')
    inv_parser.add_argument('files', nargs='+')

    # Delete
    delete_parser = subparsers.add_parser('delete')
    delete_parser.add_argument('file', help='Filename to delete')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')

    # List
    list_parser = subparsers.add_parser('list')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'upload':
        success = upload_file(
            args.file,
            key_name=args.key,
            auto_name=args.auto_name,
            description=args.description,
            force=args.force,
            invalidate=args.invalidate
        )
        sys.exit(0 if success else 1)

    elif args.command == 'invalidate':
        success = invalidate_cache(args.files)
        sys.exit(0 if success else 1)

    elif args.command == 'delete':
        success = delete_file(args.file, force=args.force)
        sys.exit(0 if success else 1)

    elif args.command == 'list':
        list_files()
        sys.exit(0)


if __name__ == '__main__':
    main()
