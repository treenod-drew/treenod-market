# litemeta_production

Litemeta game event data. All tables share common event schema (see index.md).

## Tables

| Table | Purpose | Key Fields in gameData/properties |
|-------|---------|-----------------------------------|
| activation | User activations | - |
| appsflyer | Attribution data | media_source, campaign |
| authentication | Login events | auth_type |
| buyproduct | IAP purchases | product_id, price, currency |
| chapter | Chapter progress | chapter_id, status |
| cruisecup | Cruise cup events | cup_id, score |
| cruisepass | Cruise pass progress | pass_level, rewards |
| cubegencollecttarget | Cube collection | target_id, collected |
| dailystamprally | Daily stamp events | stamp_day, reward |
| deactivation | User deactivations | reason |
| deliveryoperation | Delivery events | delivery_id, status |
| exchange | Item exchanges | item_from, item_to, amount |
| exchangeimpression | Exchange UI views | exchange_type |
| exclude_uid | Excluded users | reason |
| failproduct | Failed purchases | product_id, error |
| frozentreasure | Frozen treasure events | treasure_id |
| funnel | Funnel tracking | id, name (step identifier) |
| getreward | Reward claims | reward_type, reward_id, amount |
| gokartracing | Go-kart events | race_id, position |
| goods | Goods transactions | goods_id, amount |
| guidequest | Guide quest progress | quest_id, step |
| impression | UI impressions | screen, element |
| itemeffect | Item usage effects | item_id, effect |
| levelclear | Level completions | level_id, score, stars |
| levelfail | Level failures | level_id, fail_reason |
| levelstart | Level starts | level_id, attempt |
| login | User logins | session_id |
| logout | User logouts | session_duration |
| luckyspin | Lucky spin events | spin_type, reward |
| missioncomplete | Mission completions | mission_id, reward |
| openbox | Box openings | box_type, rewards |
| piggybank | Piggy bank events | amount, action |
| playtime | Session duration | duration_seconds |
| profileupdate | Profile changes | field, old_value, new_value |
| puzzle | Puzzle gameplay | puzzle_id, moves, time |
| registration | New registrations | source, country |
| reward | Generic rewards | reward_type, amount |
| session | Session tracking | session_id, duration |
| shop | Shop interactions | shop_type, item_viewed |
| specialevent | Special events | event_id, participation |
| stageresult | Stage results | stage_id, result |
| subscription | Subscription events | plan_id, status |
| timedmission | Timed mission events | mission_id, time_left |
| tutorial | Tutorial progress | step, completed |
| useitem | Item usage | item_id, quantity |
| worldmap | World map events | area_id, action |

## Common Queries

### Active Users
```sql
SELECT COUNT(DISTINCT uid) FROM litemeta_production.login WHERE dt = 'YYYY-MM-DD'
```

### Revenue
```sql
SELECT SUM(gameData:price) FROM litemeta_production.buyproduct WHERE dt = 'YYYY-MM-DD'
```

### Level Funnel
```sql
SELECT properties:id, COUNT(DISTINCT uid)
FROM litemeta_production.funnel
WHERE dt = 'YYYY-MM-DD'
GROUP BY properties:id
```
