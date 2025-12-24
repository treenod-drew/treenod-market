# matchflavor_production

Match Flavor game event data. All tables share common event schema (see index.md).

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| achievement | Achievement unlocks | achievement_id |
| appstatechange | App state changes | state (foreground/background) |
| funnel | Funnel tracking | id, name |
| heartbeat | Session heartbeats | - |
| item | Item events | item_id, action |
| money | Currency events | currency_type, amount |
| pageview | Page view events | page_id |
| register | New registrations | source |
| stageclose | Stage completions | stage_id, result |
| stagestart | Stage starts | stage_id |

## Common Queries

### Active Users
```sql
SELECT COUNT(DISTINCT uid) FROM matchflavor_production.register WHERE dt = 'YYYY-MM-DD'
```

### Stage Funnel
```sql
SELECT
  'start' as step, COUNT(DISTINCT uid) as users
FROM matchflavor_production.stagestart WHERE dt = 'YYYY-MM-DD'
UNION ALL
SELECT
  'close' as step, COUNT(DISTINCT uid) as users
FROM matchflavor_production.stageclose WHERE dt = 'YYYY-MM-DD'
```
