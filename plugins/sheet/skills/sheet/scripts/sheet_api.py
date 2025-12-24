#!/usr/bin/env python3
"""Google Sheets API operations."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import get_sheets_service, parse_spreadsheet_url


def get_spreadsheet_info(spreadsheet_id: str) -> dict:
    """
    Get spreadsheet metadata.

    Args:
        spreadsheet_id: Spreadsheet ID or URL

    Returns:
        dict: Spreadsheet info (id, title, sheets, url)
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


def read_range(
    spreadsheet_id: str,
    range_name: str,
    value_render: str = 'FORMATTED_VALUE'
) -> dict:
    """
    Read values from a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range
        value_render: FORMATTED_VALUE, UNFORMATTED_VALUE, or FORMULA

    Returns:
        dict: Range data (range, values, rows, cols)
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


def read_ranges(
    spreadsheet_id: str,
    ranges: list,
    value_render: str = 'FORMATTED_VALUE'
) -> list:
    """
    Read values from multiple ranges in one request.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        ranges: List of A1 notation ranges
        value_render: FORMATTED_VALUE, UNFORMATTED_VALUE, or FORMULA

    Returns:
        list: List of range data dicts
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
        value_input: USER_ENTERED or RAW

    Returns:
        dict: Update result
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    body = {'values': values}

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
        value_input: USER_ENTERED or RAW

    Returns:
        dict: Batch update result
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
        range_name: A1 notation range (data appended after last row)
        values: 2D list of values to append
        value_input: USER_ENTERED or RAW

    Returns:
        dict: Append result
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    body = {'values': values}

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


# =============================================================================
# Formatting Functions (batchUpdate API)
# =============================================================================

def get_sheet_id(spreadsheet_id: str, sheet_name: str = None) -> int:
    """
    Get sheet ID by name. If sheet_name is None, return first sheet ID.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        sheet_name: Sheet name (optional)

    Returns:
        int: Sheet ID
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    result = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields='sheets.properties'
    ).execute()

    sheets = result.get('sheets', [])
    if not sheets:
        raise ValueError("No sheets found")

    if sheet_name is None:
        return sheets[0]['properties']['sheetId']

    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']

    raise ValueError(f"Sheet not found: {sheet_name}")


def parse_a1_to_grid_range(range_str: str, sheet_id: int) -> dict:
    """
    Convert A1 notation to GridRange.

    Args:
        range_str: A1 notation (e.g., 'A1:E10', 'B2:D5')
        sheet_id: Sheet ID

    Returns:
        dict: GridRange
    """
    import re

    # Remove sheet name if present
    if '!' in range_str:
        range_str = range_str.split('!')[1]

    def col_to_index(col: str) -> int:
        result = 0
        for c in col.upper():
            result = result * 26 + (ord(c) - ord('A') + 1)
        return result - 1

    # Parse range (e.g., A1:E10)
    match = re.match(r'^([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)$', range_str)
    if match:
        start_col, start_row, end_col, end_row = match.groups()
        return {
            'sheetId': sheet_id,
            'startRowIndex': int(start_row) - 1,
            'endRowIndex': int(end_row),
            'startColumnIndex': col_to_index(start_col),
            'endColumnIndex': col_to_index(end_col) + 1
        }

    # Parse single cell (e.g., A1)
    match = re.match(r'^([A-Za-z]+)(\d+)$', range_str)
    if match:
        col, row = match.groups()
        col_idx = col_to_index(col)
        row_idx = int(row) - 1
        return {
            'sheetId': sheet_id,
            'startRowIndex': row_idx,
            'endRowIndex': row_idx + 1,
            'startColumnIndex': col_idx,
            'endColumnIndex': col_idx + 1
        }

    raise ValueError(f"Invalid range: {range_str}")


def parse_color(color) -> dict:
    """
    Parse color to RGB dict.

    Args:
        color: Hex string (#RRGGBB), tuple (r,g,b), or dict

    Returns:
        dict: Color with red, green, blue (0.0-1.0)
    """
    if isinstance(color, dict):
        return color

    if isinstance(color, str):
        color = color.lstrip('#')
        r = int(color[0:2], 16) / 255
        g = int(color[2:4], 16) / 255
        b = int(color[4:6], 16) / 255
        return {'red': r, 'green': g, 'blue': b}

    if isinstance(color, (list, tuple)):
        return {'red': color[0], 'green': color[1], 'blue': color[2]}

    raise ValueError(f"Invalid color: {color}")


def set_background_color(
    spreadsheet_id: str,
    range_name: str,
    color,
    sheet_name: str = None
) -> dict:
    """
    Set background color for a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range
        color: Hex (#RRGGBB), tuple (r,g,b 0-1), or dict
        sheet_name: Sheet name (optional, uses first sheet if None)

    Returns:
        dict: Result with updated range
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)
    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    grid_range = parse_a1_to_grid_range(range_name, sheet_id)
    bg_color = parse_color(color)

    request = {
        "repeatCell": {
            "range": grid_range,
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": bg_color
                }
            },
            "fields": "userEnteredFormat.backgroundColor"
        }
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()

    return {'range': range_name, 'color': bg_color}


def set_borders(
    spreadsheet_id: str,
    range_name: str,
    style: str = 'SOLID',
    color = '#000000',
    sheet_name: str = None,
    outer_only: bool = False
) -> dict:
    """
    Set borders for a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range
        style: NONE, SOLID, SOLID_MEDIUM, SOLID_THICK, DASHED, DOTTED, DOUBLE
        color: Border color
        sheet_name: Sheet name (optional)
        outer_only: If True, only set outer borders (no inner)

    Returns:
        dict: Result
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)
    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    grid_range = parse_a1_to_grid_range(range_name, sheet_id)
    border_color = parse_color(color)

    border = {"style": style, "color": border_color}

    request = {
        "updateBorders": {
            "range": grid_range,
            "top": border,
            "bottom": border,
            "left": border,
            "right": border
        }
    }

    if not outer_only:
        request["updateBorders"]["innerHorizontal"] = border
        request["updateBorders"]["innerVertical"] = border

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()

    return {'range': range_name, 'style': style}


def set_text_format(
    spreadsheet_id: str,
    range_name: str,
    bold: bool = None,
    italic: bool = None,
    font_size: int = None,
    font_color = None,
    sheet_name: str = None
) -> dict:
    """
    Set text format for a range.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range
        bold: Bold text
        italic: Italic text
        font_size: Font size in points
        font_color: Text color
        sheet_name: Sheet name (optional)

    Returns:
        dict: Result
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)
    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    grid_range = parse_a1_to_grid_range(range_name, sheet_id)

    text_format = {}
    fields = []

    if bold is not None:
        text_format['bold'] = bold
        fields.append('userEnteredFormat.textFormat.bold')

    if italic is not None:
        text_format['italic'] = italic
        fields.append('userEnteredFormat.textFormat.italic')

    if font_size is not None:
        text_format['fontSize'] = font_size
        fields.append('userEnteredFormat.textFormat.fontSize')

    if font_color is not None:
        text_format['foregroundColor'] = parse_color(font_color)
        fields.append('userEnteredFormat.textFormat.foregroundColor')

    if not fields:
        raise ValueError("At least one format option required")

    request = {
        "repeatCell": {
            "range": grid_range,
            "cell": {
                "userEnteredFormat": {
                    "textFormat": text_format
                }
            },
            "fields": ",".join(fields)
        }
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()

    return {'range': range_name, 'format': text_format}


def format_as_table(
    spreadsheet_id: str,
    range_name: str,
    header_color = '#4285F4',
    border_color = '#000000',
    sheet_name: str = None
) -> dict:
    """
    Format range as a table with header styling and borders.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        range_name: A1 notation range (first row is header)
        header_color: Header background color
        border_color: Border color
        sheet_name: Sheet name (optional)

    Returns:
        dict: Result
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)
    sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
    grid_range = parse_a1_to_grid_range(range_name, sheet_id)
    h_color = parse_color(header_color)
    b_color = parse_color(border_color)

    # Header range (first row only)
    header_range = grid_range.copy()
    header_range['endRowIndex'] = header_range['startRowIndex'] + 1

    requests = [
        # Header background and bold
        {
            "repeatCell": {
                "range": header_range,
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": h_color,
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                    }
                },
                "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold,userEnteredFormat.textFormat.foregroundColor"
            }
        },
        # All borders
        {
            "updateBorders": {
                "range": grid_range,
                "top": {"style": "SOLID", "color": b_color},
                "bottom": {"style": "SOLID", "color": b_color},
                "left": {"style": "SOLID", "color": b_color},
                "right": {"style": "SOLID", "color": b_color},
                "innerHorizontal": {"style": "SOLID", "color": {"red": 0.8, "green": 0.8, "blue": 0.8}},
                "innerVertical": {"style": "SOLID", "color": {"red": 0.8, "green": 0.8, "blue": 0.8}}
            }
        }
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

    return {'range': range_name, 'formatted': True}


# =============================================================================
# Pivot Table Functions
# =============================================================================

def create_pivot_table(
    spreadsheet_id: str,
    source_range: str,
    target_cell: str,
    rows: list,
    values: list,
    columns: list = None,
    source_sheet: str = None,
    target_sheet: str = None
) -> dict:
    """
    Create a pivot table.

    Args:
        spreadsheet_id: Spreadsheet ID or URL
        source_range: Source data range (A1 notation)
        target_cell: Where to place pivot table (e.g., 'G1')
        rows: List of column offsets for row grouping
        values: List of dicts with 'col' and 'func' (SUM, COUNT, AVERAGE, etc.)
        columns: List of column offsets for column grouping (optional)
        source_sheet: Source sheet name (optional)
        target_sheet: Target sheet name (optional, defaults to source)

    Returns:
        dict: Result

    Example:
        create_pivot_table(
            spreadsheet_id='...',
            source_range='A1:D100',
            target_cell='F1',
            rows=[0],  # Group by first column
            values=[{'col': 2, 'func': 'SUM'}]  # Sum of third column
        )
    """
    service = get_sheets_service()
    spreadsheet_id = parse_spreadsheet_url(spreadsheet_id)

    source_sheet_id = get_sheet_id(spreadsheet_id, source_sheet)
    target_sheet_id = get_sheet_id(spreadsheet_id, target_sheet) if target_sheet else source_sheet_id

    source_grid = parse_a1_to_grid_range(source_range, source_sheet_id)
    target_grid = parse_a1_to_grid_range(target_cell, target_sheet_id)

    pivot_table = {
        "source": source_grid,
        "rows": [
            {"sourceColumnOffset": r, "showTotals": True, "sortOrder": "ASCENDING"}
            for r in rows
        ],
        "values": [
            {"sourceColumnOffset": v['col'], "summarizeFunction": v.get('func', 'SUM')}
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
            "rows": [{"values": [{"pivotTable": pivot_table}]}],
            "start": {
                "sheetId": target_sheet_id,
                "rowIndex": target_grid['startRowIndex'],
                "columnIndex": target_grid['startColumnIndex']
            },
            "fields": "pivotTable"
        }
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]}
    ).execute()

    return {'source': source_range, 'target': target_cell, 'created': True}


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
    read_parser.add_argument("-o", "--output", help="Output file")
    read_parser.add_argument(
        "--format", choices=['json', 'csv', 'table'],
        default='table', help="Output format (default: table)"
    )
    read_parser.add_argument(
        "--render", choices=['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA'],
        default='FORMATTED_VALUE', help="Value render option"
    )

    # Update command
    update_parser = subparsers.add_parser("update", help="Update range values")
    update_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    update_parser.add_argument("range", help="A1 notation range")
    update_parser.add_argument("-f", "--file", required=True,
                               help="Input JSON file with 'values' key")

    # Append command
    append_parser = subparsers.add_parser("append", help="Append rows")
    append_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    append_parser.add_argument("range", help="A1 notation range")
    append_parser.add_argument("-f", "--file", required=True,
                               help="Input JSON file with 'values' key")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear range values")
    clear_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    clear_parser.add_argument("range", help="A1 notation range")

    # Format: background color
    bgcolor_parser = subparsers.add_parser("bgcolor", help="Set background color")
    bgcolor_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    bgcolor_parser.add_argument("range", help="A1 notation range")
    bgcolor_parser.add_argument("color", help="Color (hex: #RRGGBB)")
    bgcolor_parser.add_argument("--sheet", help="Sheet name")

    # Format: borders
    border_parser = subparsers.add_parser("border", help="Set borders")
    border_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    border_parser.add_argument("range", help="A1 notation range")
    border_parser.add_argument("--style", default="SOLID",
                               choices=['NONE', 'SOLID', 'SOLID_MEDIUM', 'SOLID_THICK', 'DASHED', 'DOTTED', 'DOUBLE'],
                               help="Border style")
    border_parser.add_argument("--color", default="#000000", help="Border color")
    border_parser.add_argument("--outer-only", action="store_true", help="Only outer borders")
    border_parser.add_argument("--sheet", help="Sheet name")

    # Format: text
    text_parser = subparsers.add_parser("textfmt", help="Set text format")
    text_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    text_parser.add_argument("range", help="A1 notation range")
    text_parser.add_argument("--bold", action="store_true", help="Bold text")
    text_parser.add_argument("--italic", action="store_true", help="Italic text")
    text_parser.add_argument("--size", type=int, help="Font size")
    text_parser.add_argument("--color", help="Font color")
    text_parser.add_argument("--sheet", help="Sheet name")

    # Format: table style
    table_parser = subparsers.add_parser("table", help="Format as table")
    table_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    table_parser.add_argument("range", help="A1 notation range")
    table_parser.add_argument("--header-color", default="#4285F4", help="Header color")
    table_parser.add_argument("--border-color", default="#000000", help="Border color")
    table_parser.add_argument("--sheet", help="Sheet name")

    # Pivot table
    pivot_parser = subparsers.add_parser("pivot", help="Create pivot table")
    pivot_parser.add_argument("spreadsheet", help="Spreadsheet ID or URL")
    pivot_parser.add_argument("source", help="Source range (A1 notation)")
    pivot_parser.add_argument("target", help="Target cell (e.g., G1)")
    pivot_parser.add_argument("--rows", required=True, help="Row columns (comma-separated offsets, e.g., 0,1)")
    pivot_parser.add_argument("--values", required=True, help="Value columns (col:func, e.g., 2:SUM,3:COUNT)")
    pivot_parser.add_argument("--columns", help="Column columns (comma-separated offsets)")
    pivot_parser.add_argument("--source-sheet", help="Source sheet name")
    pivot_parser.add_argument("--target-sheet", help="Target sheet name")

    args = parser.parse_args()

    if args.command == "info":
        info = get_spreadsheet_info(args.spreadsheet)
        print(f"Title: {info['title']}")
        print(f"ID: {info['id']}")
        print(f"Sheets: {', '.join(info['sheets'])}")
        print(f"URL: {info['url']}")

    elif args.command == "read":
        data = read_range(args.spreadsheet, args.range, args.render)

        if args.format == 'json':
            output = json.dumps(data, indent=2, ensure_ascii=False)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Saved to {args.output}")
            else:
                print(output)

        elif args.format == 'csv':
            import csv
            import io

            if args.output:
                with open(args.output, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in data['values']:
                        writer.writerow(row)
                print(f"Saved to {args.output}")
            else:
                output = io.StringIO()
                writer = csv.writer(output)
                for row in data['values']:
                    writer.writerow(row)
                print(output.getvalue(), end='')

        else:  # table
            print(f"Range: {data['range']}")
            print(f"Size: {data['rows']} rows x {data['cols']} cols")
            print("---")
            for i, row in enumerate(data['values']):
                print(f"[{i}] {row}")

    elif args.command == "update":
        with open(args.file, encoding='utf-8') as f:
            input_data = json.load(f)

        values = input_data.get('values', input_data)
        result = update_range(args.spreadsheet, args.range, values)
        print(f"Updated: {result['updated_cells']} cells in {result['updated_range']}")

    elif args.command == "append":
        with open(args.file, encoding='utf-8') as f:
            input_data = json.load(f)

        values = input_data.get('values', input_data)
        result = append_rows(args.spreadsheet, args.range, values)
        print(f"Appended: {result['updated_rows']} rows, {result['updated_cells']} cells")
        print(f"Range: {result['updated_range']}")

    elif args.command == "clear":
        result = clear_range(args.spreadsheet, args.range)
        print(f"Cleared: {result['cleared_range']}")

    elif args.command == "bgcolor":
        result = set_background_color(args.spreadsheet, args.range, args.color, args.sheet)
        print(f"Background color set: {args.range}")

    elif args.command == "border":
        result = set_borders(
            args.spreadsheet, args.range,
            style=args.style, color=args.color,
            sheet_name=args.sheet, outer_only=args.outer_only
        )
        print(f"Borders set: {args.range} ({args.style})")

    elif args.command == "textfmt":
        result = set_text_format(
            args.spreadsheet, args.range,
            bold=args.bold if args.bold else None,
            italic=args.italic if args.italic else None,
            font_size=args.size,
            font_color=args.color,
            sheet_name=args.sheet
        )
        print(f"Text format set: {args.range}")

    elif args.command == "table":
        result = format_as_table(
            args.spreadsheet, args.range,
            header_color=args.header_color,
            border_color=args.border_color,
            sheet_name=args.sheet
        )
        print(f"Table formatted: {args.range}")

    elif args.command == "pivot":
        # Parse rows
        rows = [int(r.strip()) for r in args.rows.split(',')]

        # Parse values (format: col:func or just col)
        values = []
        for v in args.values.split(','):
            if ':' in v:
                col, func = v.split(':')
                values.append({'col': int(col), 'func': func.upper()})
            else:
                values.append({'col': int(v), 'func': 'SUM'})

        # Parse columns if provided
        columns = None
        if args.columns:
            columns = [int(c.strip()) for c in args.columns.split(',')]

        result = create_pivot_table(
            args.spreadsheet, args.source, args.target,
            rows=rows, values=values, columns=columns,
            source_sheet=args.source_sheet, target_sheet=args.target_sheet
        )
        print(f"Pivot table created: {args.source} -> {args.target}")
