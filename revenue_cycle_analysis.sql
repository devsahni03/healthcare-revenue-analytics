-- =====================================================================
-- Healthcare Revenue & Operations Analytics
-- Dataset: 72,000 synthetic patient encounters (billing, payer, denials)
-- Author: Dev Sahni
-- =====================================================================

-- 1. TOP-LINE REVENUE SUMMARY
-- Total billed vs. actually collected, and the revenue leakage gap
SELECT
    ROUND(SUM(billed_amount) / 1e7, 2)                         AS total_billed_cr,
    ROUND(SUM(COALESCE(paid_amount, 0)) / 1e7, 2)               AS total_collected_cr,
    ROUND((SUM(billed_amount) - SUM(COALESCE(paid_amount, 0))) / 1e7, 2) AS revenue_leakage_cr,
    ROUND(
        100.0 * (SUM(billed_amount) - SUM(COALESCE(paid_amount, 0))) / SUM(billed_amount), 1
    ) AS leakage_pct
FROM encounters;


-- 2. DENIAL RATE OVERALL AND BY PAYER
-- Identifies which payers are driving denials -- actionable for negotiation/process fixes
SELECT
    payer,
    COUNT(*)                                                    AS total_claims,
    SUM(CASE WHEN claim_status = 'Denied' THEN 1 ELSE 0 END)    AS denied_claims,
    ROUND(100.0 * SUM(CASE WHEN claim_status = 'Denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS denial_rate_pct,
    ROUND(SUM(CASE WHEN claim_status = 'Denied' THEN billed_amount ELSE 0 END) / 1e7, 2) AS denied_revenue_cr
FROM encounters
GROUP BY payer
ORDER BY denial_rate_pct DESC;


-- 3. TOP DENIAL REASONS (ROOT CAUSE ANALYSIS)
-- Ranks denial reasons by revenue impact, not just count -- surfaces the highest-value fix first
SELECT
    denial_reason,
    COUNT(*)                                                    AS occurrences,
    ROUND(SUM(billed_amount) / 1e7, 2)                          AS revenue_at_risk_cr,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM encounters WHERE claim_status = 'Denied'), 1) AS pct_of_denials
FROM encounters
WHERE claim_status = 'Denied'
GROUP BY denial_reason
ORDER BY revenue_at_risk_cr DESC;


-- 4. DEPARTMENT-LEVEL CONTRIBUTION MARGIN
-- Billed vs. collected performance by department, joined against denial data using a subquery
SELECT
    e.department,
    COUNT(*)                                                    AS encounters,
    ROUND(SUM(e.billed_amount) / 1e7, 2)                        AS billed_cr,
    ROUND(SUM(COALESCE(e.paid_amount, 0)) / 1e7, 2)             AS collected_cr,
    ROUND(100.0 * SUM(COALESCE(e.paid_amount, 0)) / SUM(e.billed_amount), 1) AS collection_rate_pct,
    d.denial_rate_pct
FROM encounters e
JOIN (
    SELECT
        department,
        ROUND(100.0 * SUM(CASE WHEN claim_status = 'Denied' THEN 1 ELSE 0 END) / COUNT(*), 1) AS denial_rate_pct
    FROM encounters
    GROUP BY department
) d ON e.department = d.department
GROUP BY e.department
ORDER BY collection_rate_pct ASC;


-- 5. MONTHLY REVENUE LEAKAGE TREND
-- Tracks whether leakage is improving or worsening month over month
SELECT
    strftime('%Y-%m', service_date)                             AS month,
    ROUND(SUM(billed_amount) / 1e7, 2)                          AS billed_cr,
    ROUND(SUM(COALESCE(paid_amount, 0)) / 1e7, 2)               AS collected_cr,
    ROUND(100.0 * (SUM(billed_amount) - SUM(COALESCE(paid_amount, 0))) / SUM(billed_amount), 1) AS leakage_pct
FROM encounters
GROUP BY month
ORDER BY month;


-- 6. RECOVERY OPPORTUNITY SIZING
-- If denial rate for each payer was brought down to the best-performing payer's rate,
-- how much revenue could be recovered? (subquery pulls the benchmark rate)
SELECT
    payer,
    ROUND(SUM(billed_amount) / 1e7, 2) AS total_billed_cr,
    ROUND(
        (SUM(CASE WHEN claim_status = 'Denied' THEN billed_amount ELSE 0 END)
         - (SELECT MIN(min_rate.denial_rate) FROM (
                SELECT payer, 1.0 * SUM(CASE WHEN claim_status='Denied' THEN 1 ELSE 0 END)/COUNT(*) AS denial_rate
                FROM encounters GROUP BY payer
            ) min_rate) * SUM(billed_amount)
        ) / 1e7, 2
    ) AS estimated_recoverable_cr
FROM encounters
GROUP BY payer
ORDER BY estimated_recoverable_cr DESC;
