# Atlassian API Reference

## Authentication

Both APIs use Basic Auth with API tokens:

```python
# Generate token at: https://id.atlassian.com/manage/api-tokens
auth_string = f"{email}:{api_token}"
base64_auth = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
headers = {"Authorization": f"Basic {base64_auth}"}
```

## Environment Variables

```bash
ATLASSIAN_USER_EMAIL=your_email@domain.com
ATLASSIAN_API_TOKEN=your_api_token
JIRA_URL=https://your-domain.atlassian.net
```

## Confluence API v2

Base URL: `https://{domain}.atlassian.net/wiki/api/v2`

**Get Page:**
```
GET /wiki/api/v2/pages/{pageId}?body-format=atlas_doc_format
```

**Update Page:**
```
PUT /wiki/api/v2/pages/{pageId}
Body: {id, status, title, spaceId, body, version}
```

Note: Version number must increment from current version.

**Create Page:**
```
POST /wiki/api/v2/pages
Body: {spaceId, status, title, parentId, body}
```

Body format:
```json
{
  "spaceId": "123456",
  "status": "current",
  "title": "New Page Title",
  "parentId": "789012",
  "body": {
    "representation": "atlas_doc_format",
    "value": "{\"version\":1,\"type\":\"doc\",\"content\":[...]}"
  }
}
```

**Get Page Descendants (all nested children):**
```
GET /wiki/api/v2/pages/{pageId}/descendants
Query params: limit (1-250, default 50), cursor
```

**Get Page Children (direct children only):**
```
GET /wiki/api/v2/pages/{pageId}/children
Query params: limit (1-250, default 50), cursor
```

Response format:
```json
{
  "results": [
    {"id": "123", "title": "Child Page", "status": "current", "parentId": "456"}
  ],
  "_links": {"next": "/wiki/api/v2/pages/...?cursor=..."}
}
```

**Upload Attachment (v1 API):**
```
POST /wiki/rest/api/content/{pageId}/child/attachment
Headers:
  X-Atlassian-Token: no-check
  Content-Type: multipart/form-data
Body (multipart):
  file: binary file content
  comment: optional description
```

Response:
```json
{
  "results": [{
    "id": "att123456",
    "title": "image.png",
    "_links": {
      "download": "/wiki/download/attachments/123456/image.png"
    }
  }]
}
```

## Jira API v3

Base URL: `https://{domain}.atlassian.net/rest/api/3`

**Get Issue:**
```
GET /rest/api/3/issue/{issueKey}
Query params: fields, expand
```

Useful fields: `summary,status,description,assignee,reporter,comment,worklog,issuelinks,created,updated,priority,labels`

**Update Issue:**
```
PUT /rest/api/3/issue/{issueKey}
Body: {fields: {...}, update: {...}}
```

Update with fields (direct replacement):
```json
{
  "fields": {
    "summary": "New Title",
    "description": {"version": 1, "type": "doc", "content": [...]},
    "labels": ["label1", "label2"]
  }
}
```

Update with operations (add/remove):
```json
{
  "update": {
    "labels": [
      {"add": "new-label"},
      {"remove": "old-label"}
    ]
  }
}
```

**Create Issue Link:**
```
POST /rest/api/3/issueLink
Body: {type, inwardIssue, outwardIssue}
```

Example:
```json
{
  "type": {"name": "Blocks"},
  "outwardIssue": {"key": "PROJECT-123"},
  "inwardIssue": {"key": "PROJECT-456"}
}
```

Common link types:
- `Blocks` / `is blocked by`
- `Cloners` / `is cloned by`
- `Duplicate` / `is duplicated by`
- `Relates`

## ADF Structure

Root structure:
```json
{
  "version": 1,
  "type": "doc",
  "content": [...]
}
```

Common node types:
- `paragraph` - Text with inline formatting
- `heading` - Levels 1-6 via `attrs.level`
- `bulletList` / `orderedList` - Contains `listItem` nodes
- `codeBlock` - Code with optional language in `attrs.language`
- `blockquote` - Quoted content
- `table` - Table with `tableRow`, `tableHeader`, `tableCell`
- `rule` - Horizontal line

Nested list structure (max depth 3):
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "Level 1"}]},
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Level 2"}]},
                {
                  "type": "bulletList",
                  "content": [
                    {
                      "type": "listItem",
                      "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": "Level 3"}]}
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Table structure:
```json
{
  "type": "table",
  "content": [
    {
      "type": "tableRow",
      "content": [
        {"type": "tableHeader", "content": [{"type": "paragraph", "content": [...]}]},
        {"type": "tableHeader", "content": [{"type": "paragraph", "content": [...]}]}
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {"type": "tableCell", "content": [{"type": "paragraph", "content": [...]}]},
        {"type": "tableCell", "content": [{"type": "paragraph", "content": [...]}]}
      ]
    }
  ]
}
```

Inline marks:
- `strong` - Bold
- `em` - Italic
- `code` - Inline code
- `strike` - Strikethrough
- `underline` - Underline
- `link` - Link with `attrs.href`

## Error Handling

HTTP status codes:
- 200: Success
- 400: Bad request (check params/version)
- 401: Authentication failed
- 403: Insufficient permissions
- 404: Resource not found
- 429: Rate limited (check Retry-After header)
- 500+: Server error (retry with backoff)

Retry pattern for 429 and 5xx:
```python
wait_time = min(retry_after * (2 ** attempt), 300)
```

## Rate Limiting

Monitor headers:
- `X-RateLimit-Remaining`
- `Retry-After`

Best practices:
- Request only needed fields
- Avoid `*all` in fields parameter
- Use pagination for comments/worklogs
- Implement exponential backoff
