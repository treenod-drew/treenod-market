# Treenod Internal Marketplace - Implementation Spec

## Objective

Create a private GitHub-hosted plugin marketplace for Treenod organization to distribute internal Claude Code skills and tools.

## Workflow Design

### Roles and Scopes

| Role | Location | Workflow |
|------|----------|----------|
| Maintainer | This repo (treenod-claude-plugins) | Edit directly, test locally, push to distribute |
| User | `~/.claude/plugins/` (user scope) | `/plugin install` from marketplace |

### Plugin Installation Scopes

| Scope | Location | Priority |
|-------|----------|----------|
| Project | `.claude/plugins/<name>/` | Highest |
| User | `~/.claude/plugins/<name>/` | Medium |
| Marketplace | Via `/plugin install` | Installs to user scope |

### Maintainer Development Workflow

```
treenod-claude-plugins/          (this repo - source of truth)
        ↓
    edit plugins directly
        ↓
    test in this directory (skills loaded from repo)
        ↓
    git commit && git push
        ↓
    team members: /plugin update
```

### User Installation Workflow

```bash
# First-time setup
/plugin marketplace add treenod/treenod-claude-plugins
/plugin install atlassian@treenod-plugins

# Updates
/plugin marketplace update treenod-plugins
/plugin update atlassian@treenod-plugins
```

## Repository Configuration

### Repository Details
- Name: `treenod-claude-plugins` (or similar)
- Visibility: Private
- Platform: GitHub

### Directory Structure
```
treenod-claude-plugins/
├── CLAUDE.md                     # Project context for maintainers
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── atlassian/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── atlassian/
│   │           ├── SKILL.md
│   │           ├── scripts/
│   │           ├── references/
│   │           └── docs/
│   ├── document-hoarder/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── document-hoarder/
│   │           └── SKILL.md
│   └── sql-writer/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── sql-writer/
│               ├── SKILL.md
│               ├── scripts/
│               ├── templates/
│               └── references/
├── README.md
└── .gitignore
```

## Marketplace Configuration

### marketplace.json

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "treenod-plugins",
  "description": "Internal Claude Code plugins for Treenod organization",
  "owner": {
    "name": "Treenod",
    "email": "dev@treenod.com"
  },
  "plugins": [
    {
      "name": "atlassian",
      "description": "Read and update Confluence pages and Jira issues via REST APIs with automatic ADF to Markdown conversion",
      "version": "1.0.0",
      "author": {
        "name": "Treenod Dev Team",
        "email": "dev@treenod.com"
      },
      "source": "./plugins/atlassian",
      "category": "productivity",
      "tags": ["confluence", "jira", "documentation"]
    },
    {
      "name": "document-hoarder",
      "description": "Fetch and organize Confluence documentation into local markdown files",
      "version": "1.0.0",
      "author": {
        "name": "Treenod Dev Team",
        "email": "dev@treenod.com"
      },
      "source": "./plugins/document-hoarder",
      "category": "productivity",
      "tags": ["confluence", "documentation"]
    },
    {
      "name": "sql-writer",
      "description": "Write and validate Databricks SQL queries for game analytics including retention, funnel, and DAU metrics",
      "version": "1.0.0",
      "author": {
        "name": "Treenod Dev Team",
        "email": "dev@treenod.com"
      },
      "source": "./plugins/sql-writer",
      "category": "data",
      "tags": ["databricks", "sql", "analytics"]
    }
  ]
}
```

### Plugin Manifests

Each plugin requires `.claude-plugin/plugin.json`:

```json
// plugins/atlassian/.claude-plugin/plugin.json
{
  "name": "atlassian",
  "description": "Read and update Confluence pages and Jira issues via REST APIs with automatic ADF to Markdown conversion",
  "author": {
    "name": "Treenod Dev Team",
    "email": "dev@treenod.com"
  }
}
```

## Implementation Steps

### Phase 1: Repository Setup

1. Create directory structure in this project
2. Create `CLAUDE.md` for maintainer context
3. Create `.claude-plugin/marketplace.json`
4. Create `.gitignore`

### Phase 2: Plugin Migration

For each skill in `~/.claude/skills/`:

1. Create plugin directory under `plugins/`
2. Create `.claude-plugin/plugin.json` manifest
3. Copy skill contents to `skills/<skill-name>/` subdirectory
4. Verify paths in SKILL.md are relative to skill directory
5. Test skill functionality in this repo

### Phase 3: Validation

1. Validate marketplace.json syntax
2. Verify all plugin source paths exist
3. Test skills work when Claude Code runs in this directory
4. Document prerequisites in README.md

### Phase 4: GitHub Distribution

1. Create private GitHub repository
2. Push this project to GitHub
3. Grant repository access to organization members
4. Team members install via `/plugin marketplace add`

## User Installation

### First-Time Setup
```bash
# Add marketplace
/plugin marketplace add treenod/treenod-claude-plugins

# View available plugins
/plugin

# Install desired plugins
/plugin install atlassian@treenod-plugins
/plugin install document-hoarder@treenod-plugins
/plugin install sql-writer@treenod-plugins
```

### Updates
```bash
# Refresh marketplace
/plugin marketplace update treenod-plugins

# Update installed plugins
/plugin update atlassian@treenod-plugins
```

## Access Control

### GitHub Repository Permissions
- Grant read access to all developers who need plugins
- Maintain write access for plugin maintainers

### Optional: Enterprise Restriction

For stricter control, configure managed settings on developer machines:

```json
// /etc/claude-code/managed-settings.json (Linux)
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "treenod/treenod-claude-plugins",
      "ref": "main"
    }
  ]
}
```

## Versioning Strategy

### Semantic Versioning
- MAJOR: Breaking changes to skill interface
- MINOR: New features, backward compatible
- PATCH: Bug fixes

### Changelog
Maintain CHANGELOG.md in each plugin:
```markdown
## 1.0.0 - 2024-12-19
- Initial marketplace release
- Migrated from local skill
```

## Plugin Requirements

### SKILL.md Format
```markdown
---
name: skill-name
description: Skill description for Claude
---

# Skill Title

Documentation content...
```

### Script Dependencies
- Document all dependencies in SKILL.md
- Use `uv run --no-project --with <deps>` pattern for Python
- Avoid global package installation requirements

## Testing Checklist

- [ ] marketplace.json validates against schema
- [ ] All plugin paths resolve correctly
- [ ] Each plugin has valid plugin.json
- [ ] Skills load correctly after installation
- [ ] Scripts execute with correct relative paths
- [ ] Documentation is accurate

## Maintenance

### Adding New Plugins
1. Create plugin directory structure
2. Add entry to marketplace.json
3. Create plugin.json manifest
4. Test installation
5. Update README.md

### Updating Existing Plugins
1. Update plugin files
2. Increment version in marketplace.json
3. Update CHANGELOG.md
4. Commit and push

## Risk Considerations

| Risk | Mitigation |
|------|------------|
| Broken scripts | Test before release, maintain changelog |
| Access issues | Clear documentation, verify GitHub access |
| Version conflicts | Semantic versioning, changelog |
| Path issues | Use relative paths, test after migration |

## Bug Fix History

### sql-writer v1.0.1 (2026-01-05)

#### Issue
`sample.py` added LIMIT clause to all queries, causing syntax errors for DESCRIBE/SHOW/EXPLAIN commands.

```sql
-- Failed query
DESCRIBE DETAIL global.litemeta_production.stageclose LIMIT 10
-- Error: Syntax error at or near 'LIMIT'
```

#### Root Cause
The `add_limit()` function in `sample.py` unconditionally appended LIMIT to all SQL statements, but DESCRIBE/SHOW/EXPLAIN commands do not support LIMIT clause.

#### Fix
Added check to skip LIMIT for unsupported commands:

```python
def add_limit(sql: str, limit: int) -> str:
    sql_stripped = sql.strip().rstrip(";")
    sql_upper = sql_stripped.upper()

    # Skip LIMIT for commands that don't support it
    no_limit_commands = ["DESCRIBE", "SHOW", "EXPLAIN"]
    if any(sql_upper.startswith(cmd) for cmd in no_limit_commands):
        return sql_stripped
    # ... rest of function
```

#### Files Changed
- `plugins/sql-writer/skills/sql-writer/scripts/sample.py`
- `.claude-plugin/marketplace.json` (version bump)
- `plugins/sql-writer/CHANGELOG.md` (created)

## Timeline Estimate

| Phase | Tasks |
|-------|-------|
| Phase 1 | Repository setup, structure creation |
| Phase 2 | Migrate atlassian, document-hoarder, sql-writer |
| Phase 3 | Testing and validation |
| Phase 4 | Documentation and rollout |

## Files to Create

```
treenod-claude-plugins/
├── CLAUDE.md
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── atlassian/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/atlassian/SKILL.md
│   │   ├── skills/atlassian/scripts/
│   │   ├── skills/atlassian/references/
│   │   └── skills/atlassian/docs/
│   ├── document-hoarder/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/document-hoarder/SKILL.md
│   └── sql-writer/
│       ├── .claude-plugin/plugin.json
│       ├── skills/sql-writer/SKILL.md
│       ├── skills/sql-writer/scripts/
│       ├── skills/sql-writer/templates/
│       └── skills/sql-writer/references/
├── README.md
└── .gitignore
```

## README.md Template

```markdown
# Treenod Claude Code Plugins

Internal plugin marketplace for Treenod organization.

## Installation

### Add Marketplace
\`\`\`bash
/plugin marketplace add treenod/treenod-claude-plugins
\`\`\`

### Install Plugins
\`\`\`bash
/plugin install atlassian@treenod-plugins
/plugin install document-hoarder@treenod-plugins
/plugin install sql-writer@treenod-plugins
\`\`\`

## Available Plugins

| Plugin | Description |
|--------|-------------|
| atlassian | Confluence and Jira integration |
| document-hoarder | Confluence documentation fetcher |
| sql-writer | Databricks SQL query generator |

## Prerequisites

### atlassian / document-hoarder
- `ATLASSIAN_USER_EMAIL`
- `ATLASSIAN_API_TOKEN`
- `JIRA_URL`

### sql-writer
- Databricks workspace access

## Support

Contact: dev@treenod.com
```
