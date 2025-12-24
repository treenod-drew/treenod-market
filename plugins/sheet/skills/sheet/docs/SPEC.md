---
title: Google Sheets API Implementation Specification
---

## Overview

Google Sheets API를 사용하여 spreadsheet 읽기/쓰기를 위한 Python 스크립트 구현 명세.
`uv` 패키지 매니저를 사용하며, workspace 설정 없이 실행 가능 (`--no-project`, `--with` 플래그 사용).

## Requirements

### System Requirements

- Python 3.10+
- uv package manager
- Google Cloud SDK (gcloud) for authentication

### Authentication Setup

```bash
# 1. Login and set scopes
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets

# 2. Set quota project (required)
gcloud auth application-default set-quota-project <PROJECT_ID>
```

Credential 파일 위치: `~/.config/gcloud/application_default_credentials.json`

### Python Dependencies

- `google-auth` - Google authentication library
- `google-api-python-client` - Google API client

### Execution Pattern

```bash
uv run --no-project --with google-auth --with google-api-python-client python script_name.py [args]
```

## Architecture

### Module Structure

```
skills/sheet/
├── SKILL.md                    # Skill documentation
├── CHANGELOG.md                # Version history
├── docs/
│   ├── RESEARCH.md             # API research (auth, formatting, pivot)
│   └── SPEC.md                 # This file
└── scripts/
    ├── sheet_api.py            # Main API operations
    └── utils.py                # Common utilities
```

## Module Specifications

### 1. utils.py - Common Utilities

#### Purpose

인증 및 서비스 빌드를 위한 공통 유틸리티.

#### Functions

```python
def get_sheets_service():
    """
    Build Google Sheets API service with ADC credentials.

    Returns:
        googleapiclient.discovery.Resource: Sheets API service

    Raises:
        google.auth.exceptions.DefaultCredentialsError: If credentials not found

    Example:
        service = get_sheets_service()
        result = service.spreadsheets().get(spreadsheetId='...').execute()
    """
    import google.auth
    from googleapiclient.discovery import build

    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return build('sheets', 'v4', credentials=credentials)


def parse_spreadsheet_url(url: str) -> str:
    """
    Extract spreadsheet ID from Google Sheets URL.

    Args:
        url: Full Google Sheets URL or spreadsheet ID

    Returns:
        str: Spreadsheet ID

    Example:
        # Full URL
        parse_spreadsheet_url('https://docs.google.com/spreadsheets/d/1abc.../edit')
        # Returns: '1abc...'

        # Already an ID
        parse_spreadsheet_url('1abc...')
        # Returns: '1abc...'
    """
    import re

    # If already an ID (no slashes)
    if '/' not in url:
        return url

    # Extract from URL pattern
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    raise ValueError(f"Invalid spreadsheet URL: {url}")
```

### 2. sheet_api.py - Sheets Operations

#### Purpose

Google Sheets 읽기/쓰기 작업 처리.

#### Functions

```python
def get_spreadsheet_info(spreadsheet_id: str) -> dict:
    """
    Get spreadsheet metadata.

    Args:
        spreadsheet_id: Spreadsheet ID or URL

    Returns:
        dict: Spreadsheet info
            - id: Spreadsheet ID
            - title: Spreadsheet title
            - sheets: List of sheet names
            - url: Web URL

    Raises:
        googleapiclient.errors.HttpError: If API request fails
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='spreadsheetId,properties.title,sheets.properties.title,spreadsheetUrl'
    ).execute()

    return {
        'id': result['spreadsheetId'],
        'title': result['properties']['title'],
        'sheets': [s['properties']['title'] for s in result.get('sheets', [])],
        'url': result.get('spreadsheetUrl', '')
    }


def read_range(spreadsheet_id: str, range_name: str, value_render: str = 'FORMATTED_VALUE') -> dict:
    """
    Read values from a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range (e.g., 'Sheet1!A1:E10', 'A1:B5')
        value_render: How values should be rendered
            - FORMATTED_VALUE: As displayed (default)
            - UNFORMATTED_VALUE: Raw values
            - FORMULA: Formulas instead of calculated values

    Returns:
        dict: Range data
            - range: Actual range returned
            - values: 2D list of cell values
            - rows: Number of rows
            - cols: Number of columns (max)

    Example:
        data = read_range('1abc...', 'Sheet1!A1:C10')
        for row in data['values']:
            print(row)
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueRenderOption=value_render
    ).execute()

    values = result.get('values', [])

    return {
        'range': result.get('range', range_name),
        'values': values,
        'rows': len(values),
        'cols': max(len(row) for row in values) if values else 0
    }


def read_ranges(spreadsheet_id: str, ranges: list, value_render: str = 'FORMATTED_VALUE') -> list:
    """
    Read values from multiple ranges in one request.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        ranges: List of A1 notation ranges
        value_render: How values should be rendered

    Returns:
        list: List of range data dicts (same format as read_range)

    Example:
        data = read_ranges('1abc...', ['Sheet1!A1:B5', 'Sheet2!A1:C3'])
        for range_data in data:
            print(range_data['range'], range_data['values'])
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    result = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges,
        valueRenderOption=value_render
    ).execute()

    results = []
    for value_range in result.get('valueRanges', []):
        values = value_range.get('values', [])
        results.append({
            'range': value_range.get('range', ''),
            'values': values,
            'rows': len(values),
            'cols': max(len(row) for row in values) if values else 0
        })

    return results


def update_range(
    spreadsheet_id: str,
    range_name: str,
    values: list,
    value_input: str = 'USER_ENTERED'
) -> dict:
    """
    Update values in a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range
        values: 2D list of values to write
        value_input: How input should be interpreted
            - USER_ENTERED: Parse as if typed by user (default)
            - RAW: Store exactly as provided

    Returns:
        dict: Update result
            - updated_range: Range that was updated
            - updated_rows: Number of rows updated
            - updated_cols: Number of columns updated
            - updated_cells: Total cells updated

    Example:
        update_range('1abc...', 'Sheet1!A1:B2', [
            ['Name', 'Score'],
            ['Alice', 95]
        ])
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    body = {
        'values': values
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption=value_input,
        body=body
    ).execute()

    return {
        'updated_range': result.get('updatedRange', range_name),
        'updated_rows': result.get('updatedRows', 0),
        'updated_cols': result.get('updatedColumns', 0),
        'updated_cells': result.get('updatedCells', 0)
    }


def update_ranges(
    spreadsheet_id: str,
    data: list,
    value_input: str = 'USER_ENTERED'
) -> dict:
    """
    Update values in multiple ranges in one request.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        data: List of dicts with 'range' and 'values' keys
        value_input: How input should be interpreted

    Returns:
        dict: Batch update result
            - total_updated_rows: Total rows updated
            - total_updated_cols: Total columns updated
            - total_updated_cells: Total cells updated
            - total_updated_sheets: Number of sheets updated

    Example:
        update_ranges('1abc...', [
            {'range': 'Sheet1!A1:B2', 'values': [['A', 'B'], [1, 2]]},
            {'range': 'Sheet2!A1', 'values': [['Updated']]}
        ])
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    body = {
        'valueInputOption': value_input,
        'data': [
            {'range': d['range'], 'values': d['values']}
            for d in data
        ]
    }

    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()

    return {
        'total_updated_rows': result.get('totalUpdatedRows', 0),
        'total_updated_cols': result.get('totalUpdatedColumns', 0),
        'total_updated_cells': result.get('totalUpdatedCells', 0),
        'total_updated_sheets': result.get('totalUpdatedSheets', 0)
    }


def append_rows(
    spreadsheet_id: str,
    range_name: str,
    values: list,
    value_input: str = 'USER_ENTERED'
) -> dict:
    """
    Append rows to a sheet.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range (data appended after last row in range)
        values: 2D list of values to append
        value_input: How input should be interpreted

    Returns:
        dict: Append result
            - updated_range: Range where data was appended
            - updated_rows: Number of rows appended
            - updated_cells: Total cells updated

    Example:
        # Append to first empty row after A1
        append_rows('1abc...', 'Sheet1!A1', [
            ['New Row 1', 100],
            ['New Row 2', 200]
        ])
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    body = {
        'values': values
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption=value_input,
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    updates = result.get('updates', {})
    return {
        'updated_range': updates.get('updatedRange', ''),
        'updated_rows': updates.get('updatedRows', 0),
        'updated_cells': updates.get('updatedCells', 0)
    }


def clear_range(spreadsheet_id: str, range_name: str) -> dict:
    """
    Clear values in a range (keeps formatting).

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range to clear

    Returns:
        dict: Clear result
            - cleared_range: Range that was cleared
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    result = service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    return {
        'cleared_range': result.get('clearedRange', range_name)
    }
```

#### CLI Interface

```python
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Google Sheets operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Info command
    info_parser = subparsers.add_parser("info", help="Get spreadsheet info")
    info_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read range values")
    read_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    read_parser.add_argument("range", help="A1 notation range")
    read_parser.add_argument("-o", "--output", help="Output file (JSON)")
    read_parser.add_argument("--format", choices=['json', 'csv', 'table'],
                            default='table', help="Output format")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update range values")
    update_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    update_parser.add_argument("range", help="A1 notation range")
    update_parser.add_argument("-f", "--file", required=True,
                               help="Input file (JSON with 'values' key)")

    # Append command
    append_parser = subparsers.add_parser("append", help="Append rows")
    append_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    append_parser.add_argument("range", help="A1 notation range")
    append_parser.add_argument("-f", "--file", required=True,
                               help="Input file (JSON with 'values' key)")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear range values")
    clear_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    clear_parser.add_argument("range", help="A1 notation range")

    args = parser.parse_args()

    if args.command == "info":
        info = get_spreadsheet_info(args.spreadsheet)
        print(f"Title: {info['title']}")
        print(f"ID: {info['id']}")
        print(f"Sheets: {', '.join(info['sheets'])}")
        print(f"URL: {info['url']}")

    elif args.command == "read":
        data = read_range(args.spreadsheet, args.range)

        if args.format == 'json':
            output = json.dumps(data, indent=2, ensure_ascii=False)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)

        elif args.format == 'csv':
            import csv
            import sys

            writer = csv.writer(sys.stdout if not args.output else open(args.output, 'w'))
            for row in data['values']:
                writer.writerow(row)
            if args.output:
                print(f"Saved to {args.output}")

        else:  # table
            print(f"Range: {data['range']}")
            print(f"Size: {data['rows']} rows x {data['cols']} cols")
            print("---")
            for i, row in enumerate(data['values']):
                print(f"[{i}] {row}")

    elif args.command == "update":
        with open(args.file) as f:
            input_data = json.load(f)

        values = input_data.get('values', input_data)
        result = update_range(args.spreadsheet, args.range, values)
        print(f"Updated: {result['updated_cells']} cells in {result['updated_range']}")

    elif args.command == "append":
        with open(args.file) as f:
            input_data = json.load(f)

        values = input_data.get('values', input_data)
        result = append_rows(args.spreadsheet, args.range, values)
        print(f"Appended: {result['updated_rows']} rows, {result['updated_cells']} cells")
        print(f"Range: {result['updated_range']}")

    elif args.command == "clear":
        result = clear_range(args.spreadsheet, args.range)
        print(f"Cleared: {result['cleared_range']}")
```

## Usage Examples

```bash
# Get spreadsheet info
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py info 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q

# Read range (table format)
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'A1:E10'

# Read range (JSON output)
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'A1:E10' --format json -o data.json

# Read range (CSV output)
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py read 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'A1:E10' --format csv -o data.csv

# Update range
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py update 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'Sheet1!A1:B2' -f data.json

# Append rows
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py append 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'Sheet1!A1' -f rows.json

# Clear range
uv run --no-project --with google-auth --with google-api-python-client \
    python scripts/sheet_api.py clear 1DtDHpJlZcnof4jFgtOiRo1_6zjc1Z5LyHB_mGNozN_Q 'Sheet1!A1:B10'
```

## A1 Notation Reference

| Notation | Description |
|----------|-------------|
| `A1` | Single cell A1 |
| `A1:B5` | Range from A1 to B5 |
| `Sheet1!A1:B5` | Range in specific sheet |
| `A:A` | Entire column A |
| `1:1` | Entire row 1 |
| `A1:A` | Column A from row 1 |
| `Sheet1!A:B` | Columns A-B in Sheet1 |

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired credentials | Re-run `gcloud auth application-default login` |
| 403 Forbidden | No access to spreadsheet | Check spreadsheet sharing settings |
| 404 Not Found | Invalid spreadsheet ID | Verify spreadsheet ID |
| 400 Bad Request | Invalid range notation | Check A1 notation syntax |

### Error Handling Example

```python
from googleapiclient.errors import HttpError

try:
    data = read_range(spreadsheet_id, range_name)
except HttpError as e:
    if e.resp.status == 401:
        print("Authentication failed. Run: gcloud auth application-default login")
    elif e.resp.status == 403:
        print("No access. Share the spreadsheet with your account.")
    elif e.resp.status == 404:
        print("Spreadsheet not found. Check the ID.")
    else:
        print(f"API error: {e.resp.status} - {e.reason}")
```

## Implementation Checklist

- [x] Implement `utils.py`
  - [x] `get_sheets_service()`
  - [x] `parse_spreadsheet_url()`
- [x] Implement `sheet_api.py` - Values API
  - [x] `get_spreadsheet_info()`
  - [x] `read_range()`
  - [x] `read_ranges()`
  - [x] `update_range()`
  - [x] `update_ranges()`
  - [x] `append_rows()`
  - [x] `clear_range()`
- [x] Implement `sheet_api.py` - Formatting API
  - [x] `get_sheet_id()`
  - [x] `parse_a1_to_grid_range()`
  - [x] `parse_color()`
  - [x] `set_background_color()`
  - [x] `set_borders()`
  - [x] `set_text_format()`
  - [x] `format_as_table()`
- [x] Implement `sheet_api.py` - Pivot Table API
  - [x] `create_pivot_table()`
- [x] CLI interface
- [x] Create SKILL.md
- [x] Test with real spreadsheet
  - [x] Read operations
  - [x] Write operations
  - [x] Formatting operations
  - [x] Error handling

## API Reference

### Base URL

```
https://sheets.googleapis.com/v4/spreadsheets
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{spreadsheetId}` | Get spreadsheet metadata |
| GET | `/{spreadsheetId}/values/{range}` | Get range values |
| PUT | `/{spreadsheetId}/values/{range}` | Update range values |
| POST | `/{spreadsheetId}/values/{range}:append` | Append rows |
| POST | `/{spreadsheetId}/values/{range}:clear` | Clear range |
| GET | `/{spreadsheetId}/values:batchGet` | Get multiple ranges |
| POST | `/{spreadsheetId}/values:batchUpdate` | Update multiple ranges |
| POST | `/{spreadsheetId}:batchUpdate` | Formatting, pivot tables, sheet operations |

### Value Input Options

| Option | Description |
|--------|-------------|
| `USER_ENTERED` | Parse as if typed by user (formulas evaluated) |
| `RAW` | Store exactly as provided (no parsing) |

### Value Render Options

| Option | Description |
|--------|-------------|
| `FORMATTED_VALUE` | Values as displayed in UI |
| `UNFORMATTED_VALUE` | Raw values without formatting |
| `FORMULA` | Show formulas instead of results |
