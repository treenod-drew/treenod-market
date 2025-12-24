# traincf_production

Train CF game event data. All tables share common event schema (see index.md).

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| appstatechange | App state changes | state (foreground/background) |
| register | New registrations | source |
| stageclose | Stage completions | stage_id, result |
| stagestart | Stage starts | stage_id |

## Common Queries

### New Users
```sql
SELECT COUNT(DISTINCT uid) FROM traincf_production.register WHERE dt = 'YYYY-MM-DD'
```

### Stage Completion
```sql
SELECT
  gameData:stage_id,
  COUNT(*) as plays,
  SUM(CASE WHEN gameData:result = 'win' THEN 1 ELSE 0 END) as wins
FROM traincf_production.stageclose
WHERE dt = 'YYYY-MM-DD'
GROUP BY gameData:stage_id
```
