"""Common utilities for S3 uploader."""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

# Auto-install boto3 if not available
try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("boto3 not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])
    import boto3
    from botocore.exceptions import ClientError
    print("boto3 installed successfully.")


def load_aws_credentials_from_claude_settings():
    """
    Load AWS credentials from Claude Code settings file.
    Supports both Windows and macOS/Linux.

    Returns:
        tuple: (access_key_id, secret_access_key) or (None, None)
    """
    # Try different settings file locations
    settings_paths = []

    # Windows: %USERPROFILE%\.claude\settings.json
    if sys.platform == 'win32':
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            settings_paths.append(Path(user_profile) / '.claude' / 'settings.json')

    # Unix-like (macOS, Linux, WSL): ~/.claude/settings.json
    home = Path.home()
    settings_paths.append(home / '.claude' / 'settings.json')

    # WSL can also access Windows settings
    if 'microsoft' in os.uname().release.lower():
        # Try multiple common Windows user directories
        try:
            # Try to find all user directories in /mnt/c/Users/
            users_dir = Path('/mnt/c/Users')
            if users_dir.exists():
                for user_dir in users_dir.iterdir():
                    if user_dir.is_dir():
                        claude_settings = user_dir / '.claude' / 'settings.json'
                        if claude_settings.exists():
                            settings_paths.append(claude_settings)
        except:
            pass

    # Search for settings file
    for settings_path in settings_paths:
        try:
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                    # Extract AWS credentials from environment variables
                    # Support both 'env' and 'environmentVariables' keys
                    env_vars = settings.get('environmentVariables') or settings.get('env', {})
                    access_key = env_vars.get('AWS_ACCESS_KEY_ID')
                    secret_key = env_vars.get('AWS_SECRET_ACCESS_KEY')

                    if access_key and secret_key:
                        return access_key, secret_key
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            continue

    return None, None


def get_config():
    """Load configuration from environment variables."""
    return {
        'bucket': os.getenv('S3_BUCKET', 'treenod-static-origin'),
        'prefix': os.getenv('S3_PREFIX', 'doc.treenod.com/data/'),
        'distribution_id': os.getenv('CLOUDFRONT_DISTRIBUTION_ID', 'EYDV6OWEIIKXK'),
        'public_url_base': os.getenv('PUBLIC_URL_BASE', 'https://doc.treenod.com/data/'),
    }


def get_s3_client():
    """
    Get S3 client using environment credentials.
    Falls back to Claude Code settings file if env vars not set.
    """
    # First check environment variables
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # If not in environment, try loading from Claude settings
    if not access_key or not secret_key:
        access_key, secret_key = load_aws_credentials_from_claude_settings()

        if access_key and secret_key:
            # Set environment variables for this session
            os.environ['AWS_ACCESS_KEY_ID'] = access_key
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key

    # boto3 automatically uses AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    return boto3.client('s3')


def get_cloudfront_client():
    """
    Get CloudFront client using environment credentials.
    Falls back to Claude Code settings file if env vars not set.
    """
    # Ensure credentials are loaded (same logic as get_s3_client)
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not access_key or not secret_key:
        access_key, secret_key = load_aws_credentials_from_claude_settings()

        if access_key and secret_key:
            os.environ['AWS_ACCESS_KEY_ID'] = access_key
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key

    return boto3.client('cloudfront')


def get_content_type(filename):
    """Get content type from filename extension."""
    ext = filename.lower().split('.')[-1]

    content_types = {
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'svg': 'image/svg+xml',
        'ico': 'image/x-icon',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'ttf': 'font/ttf',
    }

    return content_types.get(ext, 'application/octet-stream')


def build_s3_key(filename, prefix=None):
    """Build S3 key from filename and prefix."""
    config = get_config()
    prefix = prefix or config['prefix']
    prefix = prefix.lstrip('/').rstrip('/') + '/'
    return f"{prefix}{filename}"


def build_public_url(filename):
    """Build public URL for filename."""
    config = get_config()
    base = config['public_url_base'].rstrip('/') + '/'
    return f"{base}{filename}"


def file_exists_in_s3(filename, bucket=None, prefix=None):
    """Check if file exists in S3."""
    config = get_config()
    bucket = bucket or config['bucket']
    s3_key = build_s3_key(filename, prefix)
    s3_client = get_s3_client()

    try:
        s3_client.head_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise


def get_file_metadata(filename, bucket=None, prefix=None):
    """Get metadata for file in S3."""
    config = get_config()
    bucket = bucket or config['bucket']
    s3_key = build_s3_key(filename, prefix)
    s3_client = get_s3_client()

    try:
        response = s3_client.head_object(Bucket=bucket, Key=s3_key)
        return {
            'size': response['ContentLength'],
            'last_modified': response['LastModified'],
        }
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        raise


def format_size(size_bytes):
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_git_branch():
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
        # Sanitize branch name for filename
        branch = re.sub(r'[^\w\-]', '-', branch)
        return branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def generate_filename(original_filename, description=None):
    """
    Generate filename with pattern: {branch}_{description}_{date}.{ext}

    Args:
        original_filename: Original file name
        description: Report description (optional, will prompt if None)

    Returns:
        str: Generated filename
    """
    from pathlib import Path

    # Get extension
    path = Path(original_filename)
    ext = path.suffix

    # Get branch name
    branch = get_git_branch()
    if not branch:
        branch = 'unknown'

    # Get description
    if description is None:
        print("\nAuto-naming enabled")
        print(f"Current branch: {branch}")
        description = input("Enter report description (e.g., 'dau-report', 'weekly-analysis'): ").strip()

        if not description:
            print("Description required for auto-naming")
            return None

    # Sanitize description
    description = re.sub(r'[^\w\-]', '-', description)

    # Generate filename
    date = datetime.now().strftime('%Y-%m-%d')
    filename = f"{branch}_{description}_{date}{ext}"

    return filename
