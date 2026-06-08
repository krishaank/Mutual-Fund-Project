-- 1. Top 5 funds by AUM
SELECT 
    f.fund_house,
    f.scheme_name,
    f.category,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for a specific fund (e.g., HDFC Top 100 - 125497)
SELECT 
    d.year,
    d.month,
    f.scheme_name,
    AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.nav_date = d.date_id
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE n.amfi_code = '125497'
GROUP BY d.year, d.month, f.scheme_name
ORDER BY d.year, d.month;

-- 3. SIP Year-over-Year (YoY) Growth
WITH YearlySIP AS (
    SELECT 
        d.year,
        SUM(t.amount_inr) as total_sip_inflow
    FROM fact_transactions t
    JOIN dim_date d ON t.transaction_date = d.date_id
    WHERE t.transaction_type = 'SIP'
    GROUP BY d.year
)
SELECT 
    year,
    total_sip_inflow,
    LAG(total_sip_inflow) OVER (ORDER BY year) as prev_year_inflow,
    ((total_sip_inflow - LAG(total_sip_inflow) OVER (ORDER BY year)) / LAG(total_sip_inflow) OVER (ORDER BY year)) * 100 as yoy_growth_pct
FROM YearlySIP;

-- 4. Total transaction amount by State
SELECT 
    state,
    COUNT(tx_id) as total_transactions,
    SUM(amount_inr) as total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio < 1%
SELECT 
    amfi_code,
    fund_house,
    scheme_name,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Top 5 Performing Equity Funds (1-Year Return)
SELECT 
    f.scheme_name,
    f.category,
    p.return_1yr_pct,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.category = 'Equity'
ORDER BY p.return_1yr_pct DESC
LIMIT 5;

-- 7. Monthly Comparison: SIP vs Lumpsum Inflows
SELECT 
    d.year,
    d.month,
    SUM(CASE WHEN t.transaction_type = 'SIP' THEN t.amount_inr ELSE 0 END) as sip_amount,
    SUM(CASE WHEN t.transaction_type = 'Lumpsum' THEN t.amount_inr ELSE 0 END) as lumpsum_amount
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_id
WHERE t.transaction_type IN ('SIP', 'Lumpsum')
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 8. Highest Sharpe Ratio funds with 'Low' or 'Moderate' Risk
SELECT 
    f.scheme_name,
    f.risk_category,
    p.sharpe_ratio,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.risk_category IN ('Low', 'Moderate')
ORDER BY p.sharpe_ratio DESC
LIMIT 10;

-- 9. Total AUM managed by each Fund Manager
SELECT 
    f.fund_manager,
    COUNT(f.amfi_code) as total_funds_managed,
    SUM(p.aum_crore) as total_aum_managed
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
GROUP BY f.fund_manager
ORDER BY total_aum_managed DESC;

-- 10. Funds with severe Maximum Drawdown (> 20%)
SELECT 
    f.scheme_name,
    f.category,
    p.max_drawdown_pct,
    p.return_1yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.max_drawdown_pct < -20.0
ORDER BY p.max_drawdown_pct ASC;
