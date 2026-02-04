---
name: s3-uploader
description: Upload files to S3 and invalidate CloudFront cache. Use when user needs to (1) upload HTML/files to treenod-static-origin bucket, (2) invalidate CloudFront cache, or (3) generate doc.treenod.com URLs. Primarily for HTML files, but supports CSS, JS, images.
---

## Setup

### Configure AWS Credentials

**Option A: Claude Code Settings (Recommended)**

Add to `~/.claude/settings.json` (macOS/Linux/WSL) or `%USERPROFILE%\.claude\settings.json` (Windows):

```json
{
  "environmentVariables": {
    "AWS_ACCESS_KEY_ID": "your-access-key",
    "AWS_SECRET_ACCESS_KEY": "your-secret-key"
  }
}
```

**Option B: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

**Option C: AWS CLI**

```bash
aws configure
```

The skill automatically detects credentials from any of these sources.

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_BUCKET` | `treenod-static-origin` | S3 bucket name |
| `S3_PREFIX` | `doc.treenod.com/data/` | S3 key prefix |
| `CLOUDFRONT_DISTRIBUTION_ID` | `EYDV6OWEIIKXK` | CloudFront distribution |
| `PUBLIC_URL_BASE` | `https://doc.treenod.com/data/` | Public URL base |

## Notes

- **boto3 auto-install**: The skill automatically installs boto3 if not found on first run.
- **Cross-platform**: Works on Windows, macOS, Linux, and WSL.
- **Credential auto-load**: Automatically loads AWS credentials from Claude Code settings if not in environment.

## Commands

Run from skill directory.

### upload - Upload file to S3

```bash
python scripts/s3_upload.py upload <file_path>                              # Upload file
python scripts/s3_upload.py upload <file_path> --invalidate                 # Upload + invalidate cache
python scripts/s3_upload.py upload <file_path> --force                      # Skip duplicate check
python scripts/s3_upload.py upload <file_path> --key custom.html            # Custom S3 key name
python scripts/s3_upload.py upload <file_path> --auto-name                  # Auto-generate filename
python scripts/s3_upload.py upload <file_path> --auto-name --description dau-report  # With description
```

**Output:**
```
Uploading report.html -> report.html
Uploaded: s3://treenod-static-origin/doc.treenod.com/data/report.html
URL: https://doc.treenod.com/data/report.html
```

With `--auto-name`:
```
Auto-naming enabled
Current branch: feature/user-retention
Enter report description (e.g., 'dau-report', 'weekly-analysis'): weekly-summary

Uploading report.html -> feature-user-retention_weekly-summary_2024-01-28.html
Uploaded: s3://treenod-static-origin/doc.treenod.com/data/feature-user-retention_weekly-summary_2024-01-28.html
URL: https://doc.treenod.com/data/feature-user-retention_weekly-summary_2024-01-28.html
```

With `--invalidate`:
```
Uploading report.html -> report.html
Uploaded: s3://treenod-static-origin/doc.treenod.com/data/report.html

Invalidating cache for 1 file(s)
Invalidated: /report.html (ID: I2J3K4L5M6N7O8)
URL: https://doc.treenod.com/data/report.html
```

Duplicate handling (without `--force`):
```
File already exists: report.html
Size: 245.3 KB, Modified: 2024-01-28 14:30
URL: https://doc.treenod.com/data/report.html

Options:
  [1] Overwrite
  [2] Rename to: report_2024-01-28.html
  [3] Custom name
  [4] Cancel

Choose [1-4]:
```

### invalidate - Invalidate CloudFront cache

```bash
python scripts/s3_upload.py invalidate <filename> [<filename2> ...]
```

**Output:**
```
Invalidating cache for 2 file(s)
Invalidated: /file1.html, /file2.html (ID: I3K5M7N9P1Q3R5)
```

### delete - Delete file from S3

```bash
# Interactive mode (prompts for confirmation)
python scripts/s3_upload.py delete <filename>

# Force delete (no confirmation, useful in non-interactive environments)
python scripts/s3_upload.py delete <filename> --force
```

**Output (interactive):**
```
Delete file: report.html
URL: https://doc.treenod.com/data/report.html
Confirm deletion? (yes/no): yes
Deleted: s3://treenod-static-origin/doc.treenod.com/data/report.html
```

**Output (force):**
```
Deleted: s3://treenod-static-origin/doc.treenod.com/data/report.html
```

### list - List uploaded files

```bash
python scripts/s3_upload.py list
```

**Output:**
```
Files in s3://treenod-static-origin/doc.treenod.com/data/

Filename                    Size      Modified             URL
report.html                 245.3 KB  2024-01-28 14:30     https://doc.treenod.com/data/report.html
dashboard.html              89.7 KB   2024-01-26 16:42     https://doc.treenod.com/data/dashboard.html
styles.css                  12.5 KB   2024-01-27 10:15     https://doc.treenod.com/data/styles.css

Total: 3 files
```

## Supported File Types

Automatic content-type detection:

| Extension | Content-Type |
|-----------|--------------|
| `.html` | `text/html` |
| `.css` | `text/css` |
| `.js` | `application/javascript` |
| `.json` | `application/json` |
| `.png` | `image/png` |
| `.jpg`, `.jpeg` | `image/jpeg` |
| `.gif` | `image/gif` |
| `.svg` | `image/svg+xml` |
| Others | `application/octet-stream` |

## Workflow

### Upload with auto-naming (recommended)

```bash
python scripts/s3_upload.py upload report.html --auto-name --invalidate
# Prompts for description, generates: {branch}_{description}_{date}.html
```

Example output: `https://doc.treenod.com/data/main_dau-analysis_2024-01-28.html`

### First upload (manual name)

```bash
python scripts/s3_upload.py upload report.html
```

Output: `https://doc.treenod.com/data/report.html`

### Re-upload (update existing file)

```bash
# Interactive - prompts for overwrite or rename
python scripts/s3_upload.py upload report.html --invalidate

# Force overwrite
python scripts/s3_upload.py upload report.html --force --invalidate
```

### Upload with dependencies

```bash
python scripts/s3_upload.py upload index.html --invalidate
python scripts/s3_upload.py upload styles.css --invalidate
python scripts/s3_upload.py upload script.js --invalidate
```

## Troubleshooting

### Error: Unable to locate credentials

Configure AWS credentials in one of these ways:
1. Add to `~/.claude/settings.json` (see Setup section)
2. Run `aws configure`
3. Set environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### Error: Delete failed: EOF when reading a line

Use `--force` flag to skip confirmation prompt:
```bash
python scripts/s3_upload.py delete filename.html --force
```

