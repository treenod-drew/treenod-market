---
name: sql-writer
description: Write and validate Databricks SQL queries for game analytics. Use when user needs to (1) query game event data from Databricks, (2) analyze user behavior metrics (retention, funnel, DAU), (3) explore table schemas, (4) validate SQL syntax, or (5) get sample data from production tables. Covers litemeta, linkpang, pkpkg, matchflavor, matchwitch, traincf games.
---

## Prerequisites

Environment variables: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`

## Scripts

Run from skill directory (`~/.claude/skills/sql-writer/`).

### schema.py - Table Metadata

```bash
uv run scripts/schema.py <table>                          # Get schema
uv run scripts/schema.py --list-databases                 # List databases
uv run scripts/schema.py --list-tables <database>         # List tables
```

### validate.py - Query Validation

```bash
uv run scripts/validate.py -q "<sql>"                     # Validate query
uv run scripts/validate.py -f query.sql --check-tables    # Check tables exist
```

### sample.py - Execute Query

Requires partition filter (`dt`, `log_date`) to prevent full table scans.

```bash
uv run scripts/sample.py -q "SELECT * FROM table WHERE dt = '2024-01-01' LIMIT 10"
uv run scripts/sample.py -f query.sql --limit 100 --output results.csv
uv run scripts/sample.py -q "..." --no-filter-check       # Skip filter check (caution)
```

## References

See `references/index.md` for database overview and common schema.

Database catalogs in `references/`:
- `litemeta_production.md` - 46 tables
- `linkpang_production.md` - 39 tables
- `pkpkg_production.md` - 36 tables
- `matchflavor_production.md` - 10 tables
- `matchwitch_production.md` - 4 tables
- `traincf_production.md` - 4 tables

## Workflow

1. **Understand** - Parse request: project, metrics, date range
2. **Search** - Check catalog for relevant tables
3. **Validate** - Run `schema.py` to confirm columns
4. **Sample** - Test query with `sample.py` (use partition filter)
5. **Deliver** - Provide query + tables used + assumptions

## Safety

- Read-only: SELECT, EXPLAIN, DESCRIBE, SHOW only
- Partition filter required by default
- 60s timeout, 10000 row limit
