# Claude Code Internal Marketplace Research

## Overview

Claude Code plugins enable packaging and sharing customizations including slash commands, subagents, MCP servers, and hooks. Marketplaces provide centralized catalogs for plugin discovery, version management, and distribution.

## Plugin Components

### Included Elements
- Slash commands: Custom `/command` invocations
- Subagents: Specialized AI agents for specific tasks
- MCP servers: Model Context Protocol integrations
- Hooks: Event-driven automation scripts
- Skills: Markdown-based knowledge and workflow definitions

### Plugin Directory Structure
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── commands/                 # Slash commands
├── agents/                   # Subagent definitions
├── hooks/                    # Hook scripts
├── skills/                   # Skill definitions
│   └── skill-name/
│       └── SKILL.md
└── README.md
```

### plugin.json Schema
```json
{
  "name": "plugin-name",
  "description": "Plugin description",
  "author": {
    "name": "Author Name",
    "email": "email@domain.com"
  }
}
```

## Marketplace Structure

### marketplace.json Schema

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "marketplace-identifier",
  "description": "Marketplace description",
  "owner": {
    "name": "Organization Name",
    "email": "contact@org.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "Plugin description",
      "version": "1.0.0",
      "author": {
        "name": "Author",
        "email": "author@org.com"
      },
      "source": "./plugins/plugin-name",
      "category": "development",
      "homepage": "https://github.com/org/repo",
      "tags": ["optional-tags"]
    }
  ]
}
```

### Required Fields
- `name`: Marketplace identifier (kebab-case)
- `owner`: Object with `name` and `email`
- `plugins`: Array of plugin entries

### Plugin Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Plugin identifier (kebab-case) |
| source | Yes | Path or source object |
| description | No | Plugin description |
| version | No | Semantic version |
| author | No | Author object |
| category | No | Category classification |
| homepage | No | URL to documentation |
| tags | No | Array of string tags |
| strict | No | Require plugin.json (default: true) |

### Source Types

```json
// Relative path
"source": "./plugins/plugin-name"

// GitHub repository
"source": {
  "source": "github",
  "repo": "owner/repo-name",
  "ref": "main"
}

// Git URL
"source": {
  "source": "url",
  "url": "https://github.com/org/repo.git"
}
```

## GitHub Repository Setup

### Directory Structure for Private Marketplace
```
org-marketplace/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── atlassian-skill/
│   ├── document-hoarder/
│   └── sql-writer/
├── README.md
└── .gitignore
```

### Authentication
- Uses existing git/GitHub authentication
- Private repos require user access to repository
- Supports SSH keys and personal access tokens

## User Commands

### Marketplace Management
```bash
# Add GitHub marketplace
/plugin marketplace add org/repo-name

# Add Git URL marketplace
/plugin marketplace add https://git.company.com/plugins.git

# List marketplaces
/plugin marketplace list

# Update marketplace
/plugin marketplace update marketplace-name
```

### Plugin Installation
```bash
# Install from marketplace
/plugin install plugin-name@marketplace-name

# Interactive browsing
/plugin
```

## Enterprise Configuration

### Managed Settings Location
- macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
- Linux/WSL: `/etc/claude-code/managed-settings.json`
- Windows: `C:\ProgramData\ClaudeCode\managed-settings.json`

### Strict Marketplace Restriction
```json
{
  "strictKnownMarketplaces": [
    {
      "source": "github",
      "repo": "company/approved-plugins",
      "ref": "main"
    }
  ]
}
```

When `strictKnownMarketplaces` is configured:
- Users can only add marketplaces from the allowed list
- Provides security control for enterprise environments

## Auto-Update Behavior
- Official marketplaces: Auto-update enabled by default
- Third-party marketplaces: Auto-update disabled by default
- Can disable globally via `DISABLE_AUTOUPDATER` environment variable

## Converting Skills to Plugins

### Current Skill Structure (Your Skills)
```
~/.claude/skills/
├── atlassian/
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── document-hoarder/
│   └── SKILL.md
└── sql-writer/
    ├── SKILL.md
    ├── scripts/
    └── templates/
```

### Converting to Plugin Structure
```
plugin-name/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── skill-name/
        ├── SKILL.md
        ├── scripts/
        ├── references/
        └── templates/
```

## Key Findings

### Advantages of Internal Marketplace
1. Centralized skill/plugin distribution
2. Version control and tracking
3. Access control via GitHub repository permissions
4. Automatic updates for organization members
5. Standardized plugin discovery

### Considerations
1. Private GitHub repo requires all users have access
2. Skills need restructuring into plugin format
3. Enterprise settings allow enforcing marketplace restrictions
4. Each plugin needs `.claude-plugin/plugin.json` manifest

### Comparison: Skills vs Plugins
| Aspect | Skills | Plugins |
|--------|--------|---------|
| Location | `~/.claude/skills/` | Via marketplace |
| Distribution | Manual copy | Automated via `/plugin` |
| Versioning | Manual | Built-in |
| Updates | Manual | Automatic option |
| Discovery | Manual | Marketplace catalog |
| Dependencies | None | Can include MCP servers |

## References
- https://claude.com/blog/claude-code-plugins
- https://code.claude.com/docs/en/plugin-marketplaces
- Official marketplace: `anthropics/claude-plugins-public`
