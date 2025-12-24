# Data Catalog Index

## Overview

This catalog documents tables available in Databricks for analytics queries.

## Databases

| Database | Description | Tables | Catalog |
|----------|-------------|--------|---------|
| litemeta_production | Litemeta game | 46 | [litemeta_production.md](litemeta_production.md) |
| linkpang_production | Linkpang game | 39 | [linkpang_production.md](linkpang_production.md) |
| pkpkg_production | PKPK Global game | 36 | [pkpkg_production.md](pkpkg_production.md) |
| matchflavor_production | Match Flavor game | 10 | [matchflavor_production.md](matchflavor_production.md) |
| matchwitch_production | Match Witch game | 4 | [matchwitch_production.md](matchwitch_production.md) |
| traincf_production | Train CF game | 4 | [traincf_production.md](traincf_production.md) |

## Common Schema

Most tables share this event log schema:

| Column | Type | Description |
|--------|------|-------------|
| dt | date | Event date (partition) |
| hr | int | Event hour (partition) |
| uid | string | User identifier |
| sequence | bigint | Event sequence number |
| timestamp | bigint | Event timestamp (ms) |
| action | string | Table name / action type |
| appName | string | Application name |
| appVersion | string | App version |
| authentication | string | Auth type (GUEST, etc.) |
| deviceCountry | string | Device country setting |
| deviceId | string | Device identifier |
| deviceInfo | string | Device model |
| deviceTime | string | Device local time |
| environment | string | LIVE / DEV |
| gameCountry | string | Game country setting |
| gameData | variant | Game-specific JSON data |
| properties | variant | Event properties JSON |
| osInfo | string | OS version |
| _country | string | Resolved country |

## Partition Strategy

All tables partitioned by:
- `dt` (date) - Primary partition
- `hr` (hour) - Secondary partition

Always filter by `dt` to avoid full table scans:
```sql
WHERE dt = '2024-01-01'
WHERE dt BETWEEN '2024-01-01' AND '2024-01-07'
```

## Quick Reference

### List Databases
```bash
uv run scripts/schema.py --list-databases
```

### List Tables
```bash
uv run scripts/schema.py --list-tables litemeta_production
```

### Get Table Schema
```bash
uv run scripts/schema.py litemeta_production.funnel
```

### Sample Query
```bash
uv run scripts/sample.py -q "SELECT * FROM litemeta_production.funnel WHERE dt = '2024-01-01' LIMIT 10"
```

## Generating New Catalogs

```bash
uv run scripts/schema.py --generate-catalog <database> -o catalog/<database>.md
```
