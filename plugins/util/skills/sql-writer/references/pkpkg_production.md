# pkpkg_production

PKPK Global game event data. All tables share common event schema (see index.md).

## Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| activation | User activations | - |
| adventurestageclose | Adventure stage completions | stage_id, result |
| adventurestagestart | Adventure stage starts | stage_id |
| boast | Boast/share events | boast_type |
| buyitem | Item purchases | item_id, price |
| buymoneys | Currency purchases | amount, price |
| changeoption | Settings changes | option_key |
| deactivation | User deactivations | reason |
| dragonupgrade | Dragon upgrades | dragon_id, level |
| equipadventure | Adventure equipment | equip_id |
| equipharvest | Harvest equipment | equip_id |
| exclude_uid | Excluded users | reason |
| exposebutton | Button exposures | button_id |
| firstappstartprogress | First launch progress | step |
| firstentergameprogress | First game entry progress | step |
| firstloginstart | First login events | - |
| gatherstageclose | Gather stage completions | stage_id |
| getreward | Reward claims | reward_type, amount |
| idfa | IDFA consent events | consent |
| itemharvest | Item harvests | item_id, amount |
| login | User logins | session_id |
| menuopen | Menu opens | menu_id |
| mission | Mission events | mission_id, status |
| normalstageclose | Normal stage completions | stage_id, result |
| normalstagestart | Normal stage starts | stage_id |
| openchapter | Chapter unlocks | chapter_id |
| permission | Permission events | permission_type |
| powerup | Power-up events | powerup_id |
| register | New registrations | source |
| social | Social interactions | social_type |
| stageclose | Generic stage completions | stage_id |
| stagestart | Generic stage starts | stage_id |
| summon | Summon/gacha events | summon_type, result |
| useexistbutton | UI button usage | button_id |
| vegetableshop | Vegetable shop events | item_id |
| videoad | Video ad views | ad_type, completed |

## Common Queries

### Active Users
```sql
SELECT COUNT(DISTINCT uid) FROM pkpkg_production.login WHERE dt = 'YYYY-MM-DD'
```

### Stage Clear Rate
```sql
SELECT
  gameData:stage_id,
  COUNT(*) as attempts,
  SUM(CASE WHEN gameData:result = 'clear' THEN 1 ELSE 0 END) as clears
FROM pkpkg_production.normalstageclose
WHERE dt = 'YYYY-MM-DD'
GROUP BY gameData:stage_id
```
