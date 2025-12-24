---
title: Google Sheets API Research
---

## Overview

Google Sheets API를 Claude Code 환경에서 사용하기 위한 조사 결과.

- Authentication: ADC, Service Account, OAuth
- Values API: 셀 값 읽기/쓰기
- Formatting API: 셀 서식, 테두리, 배경색
- Pivot Table API: 피벗 테이블 생성/수정

## Authentication Methods

### 1. Application Default Credentials (ADC) with gcloud

gcloud CLI를 사용한 로컬 개발 환경에 가장 적합한 방법.

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets
```

Note: `cloud-platform` scope는 gcloud ADC 명령어 필수 요구사항.

Quota project 설정 (필수):
```bash
gcloud auth application-default set-quota-project <PROJECT_ID>
```

동작 방식:
- 브라우저에서 Google 계정 로그인
- 로그인 후 credential JSON 파일 자동 생성
  - Linux: `~/.config/gcloud/application_default_credentials.json`
  - Windows: `%APPDATA%\gcloud\application_default_credentials.json`
- google-auth 라이브러리가 자동으로 해당 파일 인식

Python 코드:
```python
import google.auth
from googleapiclient.discovery import build

credentials, project = google.auth.default(
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=credentials)
```

장점:
- 환경변수 설정 불필요 (gcloud가 자동 관리)
- 사용자 계정 권한으로 접근 (별도 공유 불필요)
- 로컬 개발에 최적

단점:
- 토큰 만료 시 재인증 필요
- 자동화 스크립트에 부적합

### 2. Service Account

서버/자동화 환경에 적합한 방법.

설정 방법:
1. GCP Console에서 Service Account 생성
2. JSON 키 파일 다운로드
3. 환경변수 설정:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

Python 코드:
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

credentials = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=credentials)
```

장점:
- 토큰 만료 없음 (자동 갱신)
- 자동화/백그라운드 작업에 적합
- 환경변수로 credential 경로 지정 가능

단점:
- Spreadsheet를 Service Account 이메일에 공유해야 함
- JSON 키 파일 보안 관리 필요

### 3. OAuth 2.0 Client ID

데스크톱 앱/개인 사용에 적합한 방법.

설정 방법:
1. GCP Console에서 OAuth Client ID 생성 (Desktop App)
2. credentials.json 다운로드
3. 최초 실행 시 브라우저 인증

Python 코드 (gspread 사용):
```python
import gspread

gc = gspread.oauth()  # 최초 실행 시 브라우저 인증
sh = gc.open("Spreadsheet Name")
```

장점:
- 한번 인증 후 토큰 저장
- 사용자 권한으로 접근

단점:
- 최초 인증 시 브라우저 필요
- credentials.json 파일 관리 필요

## Available Scopes

| Scope | Permission | Sensitivity |
|-------|-----------|-------------|
| `spreadsheets` | See, edit, create, delete all spreadsheets | Sensitive |
| `spreadsheets.readonly` | See all spreadsheets | Sensitive |
| `drive.file` | Access only app-specific files | Non-sensitive |
| `drive` | Full Drive access | Restricted |
| `drive.readonly` | Read all Drive files | Restricted |

Full scope URLs:
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/spreadsheets.readonly`
- `https://www.googleapis.com/auth/drive.file`

## Recommended Approach for Claude Code

Claude Code CLI 환경에서는 두 가지 방식 권장:

### Option A: ADC (개인 사용)

```bash
# 1회 설정
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/spreadsheets

# Python 코드에서 자동 인식
credentials, project = google.auth.default()
```

장점: 환경변수 설정 불필요, 본인 계정 권한 사용

### Option B: Service Account (자동화/공유)

```bash
# 환경변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

장점: 토큰 갱신 불필요, 자동화에 적합
주의: Spreadsheet에 Service Account 이메일 공유 필요

## ADC Credential Search Order

google-auth 라이브러리가 credential을 찾는 순서:

1. `GOOGLE_APPLICATION_CREDENTIALS` 환경변수
2. gcloud application-default credentials 파일
3. GCP 리소스 연결 서비스 계정 (Compute Engine 등)

## Libraries

### google-auth + google-api-python-client

공식 Google 라이브러리. 저수준 API 직접 호출.

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### gspread

Sheets API 래퍼 라이브러리. 고수준 인터페이스 제공.

```bash
pip install gspread
```

ADC와 함께 사용:
```python
import gspread
from google.auth import default

credentials, project = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
gc = gspread.authorize(credentials)
```

## Conclusion

Claude Code 환경 권장 설정:

1. 개인 사용: `gcloud auth application-default login` 사용
2. 자동화/팀 공유: Service Account + 환경변수

두 방식 모두 google-auth 라이브러리의 ADC를 통해 자동 credential 인식 가능.
코드에서 `google.auth.default()` 호출만으로 인증 처리.

## Test Scripts

### test_auth.py

인증 및 API 연결 테스트용 스크립트.

```python
#!/usr/bin/env python3
"""Test Google Sheets API authentication with ADC credentials."""

import sys

def test_auth():
    """Test ADC authentication and basic Sheets API call."""
    try:
        import google.auth
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install google-auth google-api-python-client")
        return False

    # Test 1: Load credentials
    print("[1] Loading ADC credentials...")
    try:
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        print(f"    OK - Project: {project or '(not set)'}")
    except Exception as e:
        print(f"    FAIL - {e}")
        return False

    # Test 2: Build service
    print("[2] Building Sheets API service...")
    try:
        service = build('sheets', 'v4', credentials=credentials)
        print("    OK")
    except Exception as e:
        print(f"    FAIL - {e}")
        return False

    # Test 3: API call (if spreadsheet_id provided)
    if len(sys.argv) > 1:
        spreadsheet_id = sys.argv[1]
        print(f"[3] Reading spreadsheet metadata: {spreadsheet_id}")
        try:
            result = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields='properties.title,sheets.properties.title'
            ).execute()
            title = result.get('properties', {}).get('title', 'Unknown')
            sheets = [s['properties']['title'] for s in result.get('sheets', [])]
            print(f"    OK - Title: {title}")
            print(f"    Sheets: {sheets}")
        except HttpError as e:
            print(f"    FAIL - HTTP {e.resp.status}: {e.reason}")
            return False
    else:
        print("[3] Skipped - No spreadsheet_id provided")
        print("    Usage: python test_auth.py <spreadsheet_id>")

    print("\nAuthentication test passed.")
    return True

if __name__ == '__main__':
    success = test_auth()
    sys.exit(0 if success else 1)
```

실행:
```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python test_auth.py <spreadsheet_id>
```

### test_read.py

셀 데이터 읽기 테스트용 스크립트.

```python
#!/usr/bin/env python3
"""Test reading cell data from Google Sheets."""

import sys

def test_read(spreadsheet_id: str, range_name: str = 'A1:E10'):
    """Read cell data from spreadsheet."""
    import google.auth
    from googleapiclient.discovery import build

    credentials, _ = google.auth.default(
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=credentials)

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    print(f"Range: {range_name}")
    print(f"Rows: {len(values)}")
    print("---")
    for i, row in enumerate(values):
        print(f"[{i}] {row}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_read.py <spreadsheet_id> [range]")
        sys.exit(1)

    spreadsheet_id = sys.argv[1]
    range_name = sys.argv[2] if len(sys.argv) > 2 else 'A1:E10'
    test_read(spreadsheet_id, range_name)
```

실행:
```bash
uv run --no-project --with google-auth --with google-api-python-client \
    python test_read.py <spreadsheet_id> 'A1:E10'
```

## API Structure

Google Sheets API는 두 가지 주요 endpoint 그룹으로 구성:

| Endpoint | 용도 | 사용 예 |
|----------|------|---------|
| `spreadsheets.values.*` | 셀 값 읽기/쓰기 | read, update, append, clear |
| `spreadsheets.batchUpdate` | 서식, 피벗테이블, 시트 조작 | formatting, pivot, merge |

## Formatting API (batchUpdate)

### API Endpoint

```
POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate
```

### Request Types

| Request Type | 용도 |
|--------------|------|
| `UpdateCellsRequest` | 셀 값 + 서식 업데이트 |
| `RepeatCellRequest` | 범위에 동일 서식 반복 적용 |
| `UpdateBordersRequest` | 테두리 설정 |
| `AddBandingRequest` | 행/열 번갈아 색상 |
| `AddConditionalFormatRuleRequest` | 조건부 서식 |
| `MergeCellsRequest` | 셀 병합 |

### CellFormat Structure

```json
{
  "backgroundColor": {
    "red": 1.0,
    "green": 0.9,
    "blue": 0.0,
    "alpha": 1.0
  },
  "borders": {
    "top": {"style": "SOLID", "color": {"red": 0, "green": 0, "blue": 0}},
    "bottom": {"style": "SOLID"},
    "left": {"style": "SOLID"},
    "right": {"style": "SOLID"}
  },
  "textFormat": {
    "foregroundColor": {"red": 0, "green": 0, "blue": 0},
    "fontFamily": "Arial",
    "fontSize": 10,
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false
  },
  "horizontalAlignment": "LEFT",
  "verticalAlignment": "MIDDLE",
  "wrapStrategy": "WRAP"
}
```

### Border Styles

| Style | Description |
|-------|-------------|
| `NONE` | 테두리 없음 |
| `SOLID` | 실선 |
| `SOLID_MEDIUM` | 중간 두께 실선 |
| `SOLID_THICK` | 두꺼운 실선 |
| `DASHED` | 점선 |
| `DOTTED` | 점선 (더 작은 점) |
| `DOUBLE` | 이중선 |

### Horizontal Alignment

| Value | Description |
|-------|-------------|
| `LEFT` | 왼쪽 정렬 |
| `CENTER` | 가운데 정렬 |
| `RIGHT` | 오른쪽 정렬 |

### Example: Set Background Color

```python
request = {
    "repeatCell": {
        "range": {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 1,
            "startColumnIndex": 0,
            "endColumnIndex": 5
        },
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {
                    "red": 0.2,
                    "green": 0.6,
                    "blue": 0.9
                }
            }
        },
        "fields": "userEnteredFormat.backgroundColor"
    }
}

service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={"requests": [request]}
).execute()
```

### Example: Set Borders

```python
request = {
    "updateBorders": {
        "range": {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 5
        },
        "top": {"style": "SOLID", "color": {"red": 0, "green": 0, "blue": 0}},
        "bottom": {"style": "SOLID", "color": {"red": 0, "green": 0, "blue": 0}},
        "left": {"style": "SOLID", "color": {"red": 0, "green": 0, "blue": 0}},
        "right": {"style": "SOLID", "color": {"red": 0, "green": 0, "blue": 0}},
        "innerHorizontal": {"style": "SOLID", "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
        "innerVertical": {"style": "SOLID", "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
    }
}

service.spreadsheets().batchUpdate(
    spreadsheetId=spreadsheet_id,
    body={"requests": [request]}
).execute()
```

### Example: Bold Header Row

```python
request = {
    "repeatCell": {
        "range": {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 1
        },
        "cell": {
            "userEnteredFormat": {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            }
        },
        "fields": "userEnteredFormat.textFormat.bold,userEnteredFormat.backgroundColor"
    }
}
```

### Range Specification

batchUpdate에서 범위 지정 시 A1 notation 대신 GridRange 사용:

```json
{
  "sheetId": 0,
  "startRowIndex": 0,
  "endRowIndex": 10,
  "startColumnIndex": 0,
  "endColumnIndex": 5
}
```

- `sheetId`: 시트 ID (첫 번째 시트는 보통 0)
- Index는 0-based, end는 exclusive

### Getting Sheet ID

```python
def get_sheet_id(spreadsheet_id: str, sheet_name: str) -> int:
    """Get sheet ID by name."""
    service = get_sheets_service()
    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties'
    ).execute()

    for sheet in result.get('sheets', []):
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']

    raise ValueError(f"Sheet not found: {sheet_name}")
```

## Pivot Table API

### Overview

Pivot Table은 `spreadsheets.batchUpdate`의 `UpdateCellsRequest`를 통해 생성.

### PivotTable Structure

```json
{
  "source": {
    "sheetId": 0,
    "startRowIndex": 0,
    "startColumnIndex": 0,
    "endRowIndex": 100,
    "endColumnIndex": 10
  },
  "rows": [
    {
      "sourceColumnOffset": 0,
      "showTotals": true,
      "sortOrder": "ASCENDING"
    }
  ],
  "columns": [
    {
      "sourceColumnOffset": 1,
      "showTotals": true
    }
  ],
  "values": [
    {
      "sourceColumnOffset": 2,
      "summarizeFunction": "SUM"
    }
  ],
  "filterSpecs": [
    {
      "columnOffsetIndex": 3,
      "filterCriteria": {
        "visibleValues": ["value1", "value2"]
      }
    }
  ]
}
```

### Summarize Functions

| Function | Description |
|----------|-------------|
| `SUM` | 합계 |
| `COUNT` | 개수 |
| `COUNTA` | 비어있지 않은 셀 개수 |
| `AVERAGE` | 평균 |
| `MAX` | 최대값 |
| `MIN` | 최소값 |
| `MEDIAN` | 중앙값 |
| `PRODUCT` | 곱 |
| `STDEV` | 표준편차 |
| `VAR` | 분산 |

### Example: Create Pivot Table

```python
def create_pivot_table(
    spreadsheet_id: str,
    source_sheet_id: int,
    source_range: dict,
    target_sheet_id: int,
    target_row: int,
    target_col: int,
    rows: list,
    values: list,
    columns: list = None
):
    """Create a pivot table."""
    service = get_sheets_service()

    pivot_table = {
        "source": {
            "sheetId": source_sheet_id,
            **source_range
        },
        "rows": [
            {"sourceColumnOffset": r, "showTotals": True}
            for r in rows
        ],
        "values": [
            {"sourceColumnOffset": v["col"], "summarizeFunction": v.get("func", "SUM")}
            for v in values
        ]
    }

    if columns:
        pivot_table["columns"] = [
            {"sourceColumnOffset": c, "showTotals": True}
            for c in columns
        ]

    request = {
        "updateCells": {
            "rows": [
                {
                    "values": [
                        {"pivotTable": pivot_table}
                    ]
                }
            ],
            "start": {
                "sheetId": target_sheet_id,
                "rowIndex": target_row,
                "columnIndex": target_col
            },
            "fields": "pivotTable"
        }
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()
```

### Pivot Table Limitations

- 수정: 새 PivotTable 정의로 덮어쓰기
- 삭제: 해당 셀 비우기 (clear)
- 전용 modify/delete request 없음

## References

- [Google Sheets API Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
- [google-auth library](https://googleapis.dev/python/google-auth/latest/user-guide.html)
- [gspread Authentication](https://docs.gspread.org/en/latest/oauth2.html)
- [Cell Formatting](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells)
- [Pivot Tables](https://developers.google.com/sheets/api/guides/pivot-tables)
- [batchUpdate Requests](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request)
