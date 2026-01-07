# linkpang_production

Linkpang game event data. All tables share common event schema (see index.md).

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| access | App access events | - |
| achievement | Achievement unlocks | achievement_id |
| activation | User activations | - |
| appsflyer | Attribution data | media_source, campaign |
| arudesserttower | Aru dessert tower events | tower_level |
| buyproduct | IAP purchases | product_id, price |
| character | Character events | character_id |
| dailychallenge | Daily challenge events | challenge_id |
| deactivation | User deactivations | reason |
| episode | Episode progress | episode_id, status |
| exclude_uid | Excluded users | reason |
| funnel | Funnel tracking | id, name |
| gacha | Gacha pulls | gacha_type, result |
| goods | Goods transactions | goods_id, amount |
| hearttransaction | Heart currency events | amount, source |
| install | App installs | source |
| jeffexperiment | Jeff experiment events | experiment_id |
| lobbyactivity | Lobby interactions | activity_type |
| login | User logins | session_id |
| loungecollection | Lounge collection events | collection_id |
| loungeinventory | Lounge inventory events | item_id |
| muchaconcert | Mucha concert events | concert_id |
| nightfestival | Night festival events | festival_id |
| pageclose | Page close events | page_id |
| pageview | Page view events | page_id |
| profile | Profile updates | field |
| ranking | Ranking events | rank, score |
| register | New registrations | source |
| replay | Stage replays | stage_id |
| schedule | Schedule events | schedule_id |
| setting | Settings changes | setting_key |
| shop | Shop interactions | shop_type |
| stageclose | Stage completions | stage_id, result |
| stagecontinue | Stage continues | stage_id |
| stagestart | Stage starts | stage_id |
| stageturnaction | Turn actions | action_type |
| team | Team events | team_id |
| teamaction | Team actions | action_type |
| teamroom | Team room events | room_id |

## Common Queries

### Active Users
```sql
SELECT COUNT(DISTINCT uid) FROM linkpang_production.login WHERE dt = 'YYYY-MM-DD'
```

### Stage Completion Rate
```sql
SELECT
  gameData:stage_id,
  COUNT(DISTINCT CASE WHEN action = 'stageclose' THEN uid END) /
  COUNT(DISTINCT CASE WHEN action = 'stagestart' THEN uid END) as completion_rate
FROM linkpang_production.stagestart
WHERE dt = 'YYYY-MM-DD'
GROUP BY gameData:stage_id
```
