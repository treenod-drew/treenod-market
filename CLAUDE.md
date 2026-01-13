## Treenod Plugin Marketplace Repository

This is the source of truth for Treenod Claude Code plugins.

### Structure

```
plugins/util/
├── .claude-plugin/plugin.json    # Plugin manifest
└── skills/
    ├── atlassian/                # Confluence and Jira API integration
    ├── document-hoarder/         # Confluence documentation fetcher
    ├── sheet/                    # Google Sheets API integration
    ├── skill-creator/            # Guide for creating Claude Code skills
    └── sql-writer/               # Databricks SQL query generator
```

### Development Workflow (Maintainer)

1. Edit plugin files directly in this repo
2. Test: skills are loaded when Claude Code runs here
3. Update version in both files (semantic versioning):
   - `plugins/util/.claude-plugin/plugin.json`
   - `.claude-plugin/marketplace.json`
4. Commit and push to distribute to team

### Distribution (Team Members)

```bash
/plugin marketplace add treenod/treenod-claude-plugins
/plugin install util@treenod-plugins
/plugin update util@treenod-plugins
```

### Available Skills

| Skill | Description |
|-------|-------------|
| atlassian | Confluence and Jira API integration |
| document-hoarder | Confluence documentation fetcher |
| sheet | Google Sheets API integration |
| skill-creator | Guide for creating Claude Code skills |
| sql-writer | Databricks SQL query generator |

### Prerequisites

- atlassian/document-hoarder: `ATLASSIAN_USER_EMAIL`, `ATLASSIAN_API_TOKEN`, `JIRA_URL`
- sheet: Google Cloud project with Sheets API, `gcloud` CLI
- sql-writer: Databricks workspace access
