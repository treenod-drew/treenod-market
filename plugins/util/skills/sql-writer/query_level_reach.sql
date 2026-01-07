-- Level Reach Rate by NRU Cohort (Oct/Nov/Dec 2025)
-- D+0, D+1, D+3 level 10-100 progression

WITH cohort AS (
  -- NRU cohort definition
  SELECT
    uid,
    MIN(dt) AS register_date,
    DATE_FORMAT(MIN(dt), 'yyyy-MM') AS cohort_month
  FROM litemeta_production.register
  WHERE dt BETWEEN '2025-10-01' AND '2025-12-11'
    AND (
      dt BETWEEN '2025-10-01' AND '2025-10-31'  -- Oct full
      OR dt BETWEEN '2025-11-01' AND '2025-11-30'  -- Nov full
      OR dt BETWEEN '2025-12-05' AND '2025-12-11'  -- Dec 5-11 only
    )
  GROUP BY uid
),

level_clear AS (
  -- First clear per user per level milestone
  SELECT
    s.uid,
    FLOOR(CAST(s.properties:stage AS INT) / 10) * 10 AS level_milestone,
    MIN(s.dt) AS clear_date
  FROM litemeta_production.stageclose s
  INNER JOIN cohort c ON s.uid = c.uid
  WHERE s.dt BETWEEN '2025-10-01' AND '2025-12-14'  -- D+3 buffer
    AND CAST(s.properties:result AS STRING) = 'clear'
    AND CAST(s.properties:stage AS INT) >= 10
    AND CAST(s.properties:stage AS INT) <= 100
  GROUP BY s.uid, FLOOR(CAST(s.properties:stage AS INT) / 10) * 10
),

user_level_day AS (
  -- Calculate day_n for each level clear
  SELECT
    c.uid,
    c.cohort_month,
    l.level_milestone,
    DATEDIFF(l.clear_date, c.register_date) AS day_n
  FROM cohort c
  LEFT JOIN level_clear l ON c.uid = l.uid
)

SELECT
  cohort_month,
  level_milestone,
  COUNT(DISTINCT uid) AS cohort_size,
  -- D+0 reach rate
  ROUND(
    COUNT(DISTINCT CASE WHEN day_n = 0 THEN uid END) * 100.0 / COUNT(DISTINCT uid),
    2
  ) AS d0_reach_pct,
  -- D+1 reach rate
  ROUND(
    COUNT(DISTINCT CASE WHEN day_n <= 1 THEN uid END) * 100.0 / COUNT(DISTINCT uid),
    2
  ) AS d1_reach_pct,
  -- D+3 reach rate
  ROUND(
    COUNT(DISTINCT CASE WHEN day_n <= 3 THEN uid END) * 100.0 / COUNT(DISTINCT uid),
    2
  ) AS d3_reach_pct
FROM user_level_day
WHERE level_milestone IS NOT NULL
GROUP BY cohort_month, level_milestone
ORDER BY cohort_month, level_milestone
