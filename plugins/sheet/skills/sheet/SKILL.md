---
name: sheet
description: Read, update, and format Google Sheets spreadsheets via API. Use when users need to (1) Read cell data from spreadsheets, (2) Update cell values, (3) Append rows to sheets, (4) Format cells (background color, borders, text style), (5) Create pivot tables, or (6) Export data to JSON/CSV format.
---

# Google Sheets API Skill

Read and update Google Sheets spreadsheets using Python scripts and uv package manager.

## Prerequisites

### 1. Install gcloud CLI

설치 가이드: https://cloud.google.com/sdk/docs/install-sdk

```bash
# Linux (Debian/Ubuntu)
sudo apt-get install apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli

# macOS
brew install google-cloud-sdk

# Windows
# https://cloud.google.com/sdk/docs/install-sdk 에서 설치 파일 다운로드
```

### 2. Authentication Setup (one-time)

```bash
# gcloud 초기화 (최초 1회)
gcloud init

# ADC 로그인
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets

# quota project 설정 (팀 공용 프로젝트)
gcloud auth application-default set-quota-project data-470906
```

Credential 파일 위치:
- Linux/macOS: `~/.config/gcloud/application_default_credentials.json`
- Windows: `%APPDATA%\gcloud\application_default_credentials.json`

### Execution Pattern

```bash
uv run --no-project --with google-auth --with google-api-python-client python scripts/sheet_api.py [command] [args]
```

## Available Commands

### Get Spreadsheet Info

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py info <spreadsheet_id_or_url>
```

### Read Range

```bash
# Table format (default)
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read <spreadsheet> <range>

# JSON format
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read <spreadsheet> <range> --format json -o output.json

# CSV format
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read <spreadsheet> <range> --format csv -o output.csv
```

### Update Range

```bash
# Prepare JSON file with values
echo '{"values": [["A", "B"], [1, 2]]}' > data.json

uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py update <spreadsheet> <range> -f data.json
```

### Append Rows

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py append <spreadsheet> <range> -f rows.json
```

### Clear Range

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py clear <spreadsheet> <range>
```

## Formatting Commands

### Background Color

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py bgcolor <spreadsheet> <range> '#4285F4'

# With sheet name
    python scripts/sheet_api.py bgcolor <spreadsheet> <range> '#FF0000' --sheet 'Sheet1'
```

### Borders

```bash
# Default solid borders
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py border <spreadsheet> <range>

# Custom style
    python scripts/sheet_api.py border <spreadsheet> <range> --style SOLID_THICK --color '#000000'

# Outer borders only
    python scripts/sheet_api.py border <spreadsheet> <range> --outer-only
```

Border styles: `NONE`, `SOLID`, `SOLID_MEDIUM`, `SOLID_THICK`, `DASHED`, `DOTTED`, `DOUBLE`

### Text Format

```bash
# Bold
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py textfmt <spreadsheet> <range> --bold

# Multiple options
    python scripts/sheet_api.py textfmt <spreadsheet> <range> --bold --italic --size 14 --color '#FF0000'
```

### Format as Table

헤더 스타일링 + 테두리 한번에 적용:

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py table <spreadsheet> <range>

# Custom colors
    python scripts/sheet_api.py table <spreadsheet> <range> --header-color '#34A853' --border-color '#000000'
```

## Pivot Table

```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py pivot <spreadsheet> <source_range> <target_cell> \
        --rows 0 --values '2:SUM'

# Multiple rows and values
    python scripts/sheet_api.py pivot <spreadsheet> 'A1:D100' 'F1' \
        --rows 0,1 --values '2:SUM,3:COUNT' --columns 4
```

Options:
- `--rows`: Column offsets for row grouping (0-indexed, comma-separated)
- `--values`: Column:Function pairs (e.g., `2:SUM,3:AVERAGE`)
- `--columns`: Column offsets for column grouping (optional)
- `--source-sheet`, `--target-sheet`: Sheet names (optional)

Summarize functions: `SUM`, `COUNT`, `COUNTA`, `AVERAGE`, `MAX`, `MIN`, `MEDIAN`

## A1 Notation

| Notation | Description |
|----------|-------------|
| `A1` | Single cell |
| `A1:B5` | Range |
| `Sheet1!A1:B5` | Range in specific sheet |
| `A:A` | Entire column |
| `1:1` | Entire row |

## Output Formats

### table (default)

```
Range: Sheet1!A1:C3
Size: 3 rows x 3 cols
---
[0] ['Name', 'Score', 'Grade']
[1] ['Alice', 95, 'A']
[2] ['Bob', 87, 'B']
```

### json

```json
{
  "range": "Sheet1!A1:C3",
  "values": [
    ["Name", "Score", "Grade"],
    ["Alice", 95, "A"],
    ["Bob", 87, "B"]
  ],
  "rows": 3,
  "cols": 3
}
```

### csv

```
Name,Score,Grade
Alice,95,A
Bob,87,B
```

## Script Modules

- `scripts/utils.py` - Authentication, service builder
- `scripts/sheet_api.py` - Sheets operations and CLI

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 | Expired credentials | Re-run `gcloud auth application-default login` |
| 403 | No access | Share spreadsheet with your account |
| 404 | Not found | Check spreadsheet ID |

## Troubleshooting

### Credentials expired

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets
```

### Quota project error

```bash
gcloud auth application-default set-quota-project data-470906
```
