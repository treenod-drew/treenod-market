"""Common utilities for Atlassian API operations."""

import os
import base64


def get_auth_headers() -> dict:
    """
    Create authentication headers from environment variables.

    Returns:
        dict: Headers with Basic Auth and content type

    Raises:
        EnvironmentError: If required env vars are missing
    """
    email = os.environ.get('ATLASSIAN_USER_EMAIL')
    api_token = os.environ.get('ATLASSIAN_API_TOKEN')

    if not email or not api_token:
        raise EnvironmentError(
            "Missing required environment variables: "
            "ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN"
        )

    auth_string = f"{email}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')

    return {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def get_base_urls() -> tuple:
    """
    Get Confluence and Jira base URLs from environment.

    Returns:
        tuple: (confluence_url, jira_url)

    Raises:
        EnvironmentError: If JIRA_URL is not set
    """
    jira_url = os.environ.get('JIRA_URL', '').rstrip('/')

    if not jira_url:
        raise EnvironmentError("Missing required environment variable: JIRA_URL")

    # Confluence is on the same domain
    confluence_url = jira_url.replace('/jira', '').rstrip('/')

    return confluence_url, jira_url


def save_to_file(content: str, filepath: str) -> None:
    """
    Save content to file with UTF-8 encoding.

    Args:
        content: Content to save
        filepath: Output file path

    Raises:
        IOError: If file cannot be written
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def load_from_file(filepath: str) -> str:
    """
    Load content from file with UTF-8 encoding.

    Args:
        filepath: Input file path

    Returns:
        str: File content

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()
