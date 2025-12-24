"""Jira issue operations via REST API v3."""

import requests
from utils import get_auth_headers, get_base_urls, save_to_file
from adf_converter import adf_to_markdown


def read_jira_issue(issue_key: str, output_file: str) -> dict:
    """
    Read Jira issue and save to markdown file.

    Args:
        issue_key: Jira issue key (e.g., "PROJECT-123")
        output_file: Path to save markdown output

    Returns:
        dict: Issue metadata

    Process:
        1. Fetch issue with all required fields
        2. Convert fields to markdown format
        3. Save to file

    Raises:
        requests.HTTPError: If API request fails
    """
    _, jira_url = get_base_urls()
    headers = get_auth_headers()

    url = f"{jira_url}/rest/api/3/issue/{issue_key}"
    params = {
        "fields": "summary,status,description,assignee,reporter,"
                  "comment,worklog,issuelinks,created,updated,priority,parent",
        "expand": "renderedFields"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    fields = data['fields']

    # Build markdown content
    markdown = format_jira_issue_markdown(data)

    # Save to file
    save_to_file(markdown, output_file)

    return {
        "key": data['key'],
        "summary": fields['summary'],
        "status": fields['status']['name']
    }


def format_jira_issue_markdown(issue_data: dict) -> str:
    """
    Format Jira issue data as markdown.

    Args:
        issue_data: Full issue response from API

    Returns:
        str: Formatted markdown content
    """
    fields = issue_data['fields']
    key = issue_data['key']

    sections = []

    # Header
    sections.append(f"# {key}: {fields['summary']}\n")

    # Metadata
    sections.append("## Metadata\n")
    sections.append(f"- **Status:** {fields['status']['name']}")
    sections.append(f"- **Created:** {fields['created']}")
    sections.append(f"- **Updated:** {fields['updated']}")

    if fields.get('priority'):
        sections.append(f"- **Priority:** {fields['priority']['name']}")

    if fields.get('assignee'):
        assignee = fields['assignee']
        sections.append(f"- **Assignee:** {assignee['displayName']} ({assignee['emailAddress']})")
    else:
        sections.append("- **Assignee:** Unassigned")

    if fields.get('reporter'):
        reporter = fields['reporter']
        sections.append(f"- **Reporter:** {reporter['displayName']}")

    if fields.get('parent'):
        parent = fields['parent']
        parent_key = parent['key']
        parent_summary = parent['fields']['summary']
        sections.append(f"- **Parent:** [{parent_key}] {parent_summary}")

    sections.append("")

    # Description
    sections.append("## Description\n")
    if fields.get('description'):
        desc_markdown = adf_to_markdown(fields['description'])
        sections.append(desc_markdown)
    else:
        sections.append("*No description*")

    sections.append("")

    # Linked Issues
    if fields.get('issuelinks'):
        sections.append("## Linked Issues\n")
        for link in fields['issuelinks']:
            link_type = link['type']['name']

            if 'outwardIssue' in link:
                linked = link['outwardIssue']
                relation = link['type']['outward']
                sections.append(
                    f"- **{relation}:** [{linked['key']}] {linked['fields']['summary']} "
                    f"({linked['fields']['status']['name']})"
                )
            elif 'inwardIssue' in link:
                linked = link['inwardIssue']
                relation = link['type']['inward']
                sections.append(
                    f"- **{relation}:** [{linked['key']}] {linked['fields']['summary']} "
                    f"({linked['fields']['status']['name']})"
                )

        sections.append("")

    # Comments
    if fields.get('comment') and fields['comment']['total'] > 0:
        sections.append("## Comments\n")
        for comment in fields['comment']['comments']:
            author = comment['author']['displayName']
            created = comment['created']

            sections.append(f"### {author} - {created}\n")

            if isinstance(comment.get('body'), dict):
                comment_markdown = adf_to_markdown(comment['body'])
            else:
                comment_markdown = comment.get('body', '*No content*')

            sections.append(comment_markdown)
            sections.append("")

    # Work Logs
    if fields.get('worklog') and fields['worklog']['total'] > 0:
        sections.append("## Work Logs\n")

        total_seconds = 0
        for worklog in fields['worklog']['worklogs']:
            author = worklog['author']['displayName']
            time_spent = worklog['timeSpent']
            started = worklog['started']
            total_seconds += worklog['timeSpentSeconds']

            sections.append(f"- **{author}** - {time_spent} - {started}")

        # Summary
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        sections.append(f"\n**Total Time Logged:** {hours}h {minutes}m")
        sections.append("")

    return "\n".join(sections)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Jira issue operations")
    parser.add_argument("issue_key", help="Jira issue key (e.g., PROJECT-123)")
    parser.add_argument("-o", "--output", help="Output markdown file (default: <issue_key>.md)")

    args = parser.parse_args()

    output_file = args.output or f"{args.issue_key}.md"
    result = read_jira_issue(args.issue_key, output_file)
    print(f"✓ Issue '{result['key']}: {result['summary']}' saved to {output_file}")
