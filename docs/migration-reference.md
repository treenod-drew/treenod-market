# Skill to Plugin Migration Reference

## Migration Strategy

- Source: `~/.claude/skills/` (current skills)
- Target: This project (`treenod-market/` → rename to `treenod-claude-plugins/`)
- Approach: Copy skills to plugin structure, keep source intact

## Current Skill Locations

Source: `~/.claude/skills/`

## Atlassian Skill

### Current Structure
```
~/.claude/skills/atlassian/
├── SKILL.md
├── CHANGELOG.md
├── page.md
├── scripts/
│   ├── utils.py
│   ├── adf_converter.py
│   ├── confluence_api.py
│   ├── jira_api.py
│   └── debug_adf.py
├── references/
│   └── api_reference.md
└── docs/
    ├── RESEARCH_DOCUMENT.md
    ├── SPEC.md
    ├── adf-converter-spec.md
    ├── test_confluence.py
    ├── test_jira.py
    └── *.json
```

### Target Structure
```
plugins/atlassian/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── atlassian/
        ├── SKILL.md
        ├── CHANGELOG.md
        ├── page.md
        ├── scripts/
        ├── references/
        └── docs/
```

## Document Hoarder Skill

### Current Structure
```
~/.claude/skills/document-hoarder/
└── SKILL.md
```

### Target Structure
```
plugins/document-hoarder/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── document-hoarder/
        └── SKILL.md
```

## SQL Writer Skill

### Current Structure
```
~/.claude/skills/sql-writer/
├── SKILL.md
├── query_level_reach.sql
├── scripts/
│   ├── utils.py
│   ├── schema.py
│   ├── validate.py
│   └── sample.py
├── templates/
│   ├── retention.sql
│   ├── funnel.sql
│   └── cohort.sql
├── references/
│   ├── index.md
│   ├── litemeta_production.md
│   ├── linkpang_production.md
│   ├── pkpkg_production.md
│   ├── matchflavor_production.md
│   ├── matchwitch_production.md
│   └── traincf_production.md
└── docs/
    └── workflow.md
```

### Target Structure
```
plugins/sql-writer/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── sql-writer/
        ├── SKILL.md
        ├── query_level_reach.sql
        ├── scripts/
        ├── templates/
        ├── references/
        └── docs/
```

## Migration Commands

```bash
# Create directory structure (run from project root)
mkdir -p .claude
mkdir -p .claude-plugin
mkdir -p plugins/atlassian/.claude-plugin
mkdir -p plugins/atlassian/skills
mkdir -p plugins/document-hoarder/.claude-plugin
mkdir -p plugins/document-hoarder/skills
mkdir -p plugins/sql-writer/.claude-plugin
mkdir -p plugins/sql-writer/skills

# Copy skills from user scope
cp -r ~/.claude/skills/atlassian plugins/atlassian/skills/
cp -r ~/.claude/skills/document-hoarder plugins/document-hoarder/skills/
cp -r ~/.claude/skills/sql-writer plugins/sql-writer/skills/
```

## plugin.json Templates

### atlassian
```json
{
  "name": "atlassian",
  "description": "Read and update Confluence pages and Jira issues via REST APIs with automatic ADF to Markdown conversion",
  "author": {
    "name": "Treenod Dev Team",
    "email": "dev@treenod.com"
  }
}
```

### document-hoarder
```json
{
  "name": "document-hoarder",
  "description": "Fetch and organize Confluence documentation into local markdown files",
  "author": {
    "name": "Treenod Dev Team",
    "email": "dev@treenod.com"
  }
}
```

### sql-writer
```json
{
  "name": "sql-writer",
  "description": "Write and validate Databricks SQL queries for game analytics",
  "author": {
    "name": "Treenod Dev Team",
    "email": "dev@treenod.com"
  }
}
```

## Path Updates Required

Check SKILL.md files for script paths. Current paths like:
```bash
python scripts/confluence_api.py
```

Should work if skill directory structure is preserved under `skills/<name>/`.

## Validation After Migration

```bash
# Verify marketplace.json
python -m json.tool .claude-plugin/marketplace.json

# Verify each plugin.json
python -m json.tool plugins/atlassian/.claude-plugin/plugin.json
python -m json.tool plugins/document-hoarder/.claude-plugin/plugin.json
python -m json.tool plugins/sql-writer/.claude-plugin/plugin.json

# Verify skill files exist
ls plugins/*/skills/*/SKILL.md
```

## Post-Migration Workflow

After migration, maintainer works directly in this repo:
1. Edit plugin files
2. Test by running Claude Code in this directory
3. Commit and push to distribute
4. Team members: `/plugin update`
