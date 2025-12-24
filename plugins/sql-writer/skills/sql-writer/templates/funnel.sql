-- Funnel Analysis Template
-- Calculate conversion through sequential steps

WITH funnel_events AS (
    SELECT
        uid,
        action_type,
        MIN(event_time) as first_event_time
    FROM ${database}_silver.user_action
    WHERE log_date BETWEEN '${start_date}' AND '${end_date}'
        AND action_type IN (${funnel_steps})  -- e.g., 'app_open', 'tutorial_start', 'tutorial_complete', 'first_game'
    GROUP BY uid, action_type
),

step_1 AS (
    SELECT DISTINCT uid, first_event_time
    FROM funnel_events
    WHERE action_type = '${step_1}'
),

step_2 AS (
    SELECT DISTINCT f.uid, f.first_event_time
    FROM funnel_events f
    JOIN step_1 s1 ON f.uid = s1.uid AND f.first_event_time >= s1.first_event_time
    WHERE f.action_type = '${step_2}'
),

step_3 AS (
    SELECT DISTINCT f.uid, f.first_event_time
    FROM funnel_events f
    JOIN step_2 s2 ON f.uid = s2.uid AND f.first_event_time >= s2.first_event_time
    WHERE f.action_type = '${step_3}'
),

step_4 AS (
    SELECT DISTINCT f.uid, f.first_event_time
    FROM funnel_events f
    JOIN step_3 s3 ON f.uid = s3.uid AND f.first_event_time >= s3.first_event_time
    WHERE f.action_type = '${step_4}'
)

SELECT
    '${step_1}' as step_name,
    1 as step_order,
    COUNT(*) as user_count,
    1.0 as conversion_from_prev,
    1.0 as conversion_from_first
FROM step_1

UNION ALL

SELECT
    '${step_2}' as step_name,
    2 as step_order,
    COUNT(*) as user_count,
    COUNT(*) / (SELECT COUNT(*) FROM step_1) as conversion_from_prev,
    COUNT(*) / (SELECT COUNT(*) FROM step_1) as conversion_from_first
FROM step_2

UNION ALL

SELECT
    '${step_3}' as step_name,
    3 as step_order,
    COUNT(*) as user_count,
    COUNT(*) / (SELECT COUNT(*) FROM step_2) as conversion_from_prev,
    COUNT(*) / (SELECT COUNT(*) FROM step_1) as conversion_from_first
FROM step_3

UNION ALL

SELECT
    '${step_4}' as step_name,
    4 as step_order,
    COUNT(*) as user_count,
    COUNT(*) / (SELECT COUNT(*) FROM step_3) as conversion_from_prev,
    COUNT(*) / (SELECT COUNT(*) FROM step_1) as conversion_from_first
FROM step_4

ORDER BY step_order
