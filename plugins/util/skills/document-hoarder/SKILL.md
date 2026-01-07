---
name: document-hoarder
description: Fetch and organize Confluence documentation into local markdown files. Use when user wants to (1) download Confluence pages by URL or page ID, (2) update existing local docs from Confluence, (3) recursively fetch linked/child pages, (4) organize documentation into folder structures. Requires atlassian skill for Confluence API access.
---

# Document Hoarder

Fetch Confluence pages and organize them into structured local documentation.

## Prerequisites

- atlassian skill must be available for Confluence API access
- Environment variables configured: ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN, JIRA_URL

## Workflow

### Step 1: Identify Target

Accept one of:
- Confluence page URL (extract page ID from path `/pages/{page_id}/`)
- Page ID directly
- Local file path to update (read frontmatter for `page_id`)
- Document name to search

### Step 2: Fetch Page

```bash
uv run --no-project --with requests python /home/drew/.claude/skills/atlassian/scripts/confluence_api.py read {page_id} -o {output_path}
```

For multiple pages, spawn sub-agents in parallel:
```
Task(subagent_type="general-purpose", run_in_background=true, model="haiku")
```

Each sub-agent should:
1. Fetch the page using confluence_api.py
2. Read the saved file
3. Extract any Confluence links (pattern: `atlassian.net/wiki/spaces/.*/pages/(\d+)`)
4. Return: brief summary + list of found links

### Step 3: Handle Linked Pages

After sub-agents complete:
1. Collect all discovered Confluence links
2. Filter out already-fetched pages
3. Ask user: "Found N linked pages. Fetch them all?"
   - Yes: repeat Step 2 for new pages
   - No: proceed to Step 4
   - Selective: let user choose which to fetch

### Step 4: Organize Structure

After all pages fetched:
1. List all saved markdown files
2. Analyze content to determine logical grouping:
   - `core/` - operational documents
   - `training/` - tutorials, guides
   - `reference/` - technical references
   - `meetings/` - meeting notes, schedules
3. Create subdirectories and move files
4. Generate `index.md` with:
   - Folder structure overview
   - Links to all documents with descriptions
   - Recommended reading order if applicable

## Update Workflow

When user requests update to existing docs:

1. Identify target:
   - Specific file path: read its `page_id` from frontmatter
   - Folder: scan all .md files for `page_id` frontmatter
   - Page URL/ID: find matching local file or create new

2. Re-fetch and overwrite:
   ```bash
   uv run --no-project --with requests python /home/drew/.claude/skills/atlassian/scripts/confluence_api.py read {page_id} -o {existing_path}
   ```

3. Report changes (file modified timestamp comparison)

## Output Format

Each saved page includes YAML frontmatter:
```yaml
---
title: Page Title
page_id: 123456
version: 5
status: current
---
```

## Example Usage

User: "Fetch https://example.atlassian.net/wiki/spaces/TEAM/pages/12345/Guide"
1. Extract page_id: 12345
2. Determine output path from title or user preference
3. Fetch page
4. Check for linked pages
5. Ask user about linked pages
6. Organize and create index

User: "Update docs/training/databricks/"
1. Scan folder for .md files with page_id
2. Re-fetch each page
3. Report updated files
