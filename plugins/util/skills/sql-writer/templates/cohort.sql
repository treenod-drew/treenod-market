-- Cohort Analysis Template
-- Analyze metrics by user cohort (install date, first action date, etc.)

WITH cohort_definition AS (
    -- Define cohorts by first action date
    SELECT
        uid,
        DATE_TRUNC('${cohort_period}', MIN(log_date)) as cohort  -- 'week', 'month'
    FROM ${database}_silver.user_action
    WHERE log_date >= '${cohort_start_date}'
        AND action_type = '${cohort_action}'  -- e.g., 'first_login'
    GROUP BY uid
),

metrics AS (
    -- Calculate metrics per user per period
    SELECT
        a.uid,
        DATE_TRUNC('${metric_period}', a.log_date) as period,
        ${metric_aggregation}  -- e.g., 'COUNT(*) as action_count', 'SUM(revenue) as revenue'
    FROM ${database}_silver.user_action a
    WHERE a.log_date BETWEEN '${start_date}' AND '${end_date}'
        AND a.action_type IN (${metric_actions})
    GROUP BY a.uid, DATE_TRUNC('${metric_period}', a.log_date)
)

SELECT
    c.cohort,
    m.period,
    DATEDIFF('${cohort_period}', c.cohort, m.period) as periods_since_cohort,
    COUNT(DISTINCT c.uid) as cohort_size,
    COUNT(DISTINCT m.uid) as active_users,
    ${final_metric}  -- e.g., 'SUM(m.action_count) as total_actions'
FROM cohort_definition c
LEFT JOIN metrics m ON c.uid = m.uid AND m.period >= c.cohort
GROUP BY c.cohort, m.period
ORDER BY c.cohort, m.period
