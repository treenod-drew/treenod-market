"""Common utilities for Google Sheets API operations."""

import re


def get_sheets_service():
    """
    Build Google Sheets API service with ADC credentials.

    Returns:
        googleapiclient.discovery.Resource: Sheets API service

    Raises:
        google.auth.exceptions.DefaultCredentialsError: If credentials not found
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

    Raises:
        ValueError: If URL format is invalid
    """
    if '/' not in url:
        return url

    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)

    raise ValueError(f"Invalid spreadsheet URL: {url}")
