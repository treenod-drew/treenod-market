-- Retention Analysis Template
-- Calculate D0-DN retention for a cohort

WITH cohort AS (
    -- Define cohort: users who performed action X on cohort_date
    SELECT DISTINCT
        uid,
        MIN(log_date) as cohort_date
    FROM ${database}_silver.user_action
    WHERE log_date BETWEEN '${start_date}' AND '${end_date}'
        AND action_type = '${cohort_action}'  -- e.g., 'first_login', 'tutorial_complete'
    GROUP BY uid
),

activity AS (
    -- Get all login activity for cohort users
    SELECT DISTINCT
        a.uid,
        a.log_date as activity_date
    FROM ${database}_silver.user_action a
    WHERE a.log_date >= '${start_date}'
        AND a.action_type = 'login'
)

SELECT
    c.cohort_date,
    DATEDIFF(a.activity_date, c.cohort_date) as day_n,
    COUNT(DISTINCT c.uid) as cohort_size,
    COUNT(DISTINCT a.uid) as retained_users,
    COUNT(DISTINCT a.uid) / COUNT(DISTINCT c.uid) as retention_rate
FROM cohort c
LEFT JOIN activity a
    ON c.uid = a.uid
    AND a.activity_date >= c.cohort_date
    AND DATEDIFF(a.activity_date, c.cohort_date) <= ${max_day_n}  -- e.g., 30
GROUP BY c.cohort_date, DATEDIFF(a.activity_date, c.cohort_date)
ORDER BY c.cohort_date, day_n
