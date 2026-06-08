# Data Dictionary - Bluestock Mutual Fund Analytics

This document serves as the central data dictionary for the Star Schema database (`bluestock_mf.db`) developed for the Bluestock Mutual Fund Analytics Capstone Project.

## 1. Dimension Tables

### `dim_fund`
Master lookup table containing descriptive attributes for all mutual fund schemes.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT (PK) | Unique 6-digit identifier assigned by AMFI. | `fund_master.csv` |
| `fund_house` | TEXT | Asset Management Company (AMC) managing the fund. | `fund_master.csv` |
| `scheme_name` | TEXT | Official name of the mutual fund scheme. | `fund_master.csv` |
| `category` | TEXT | Broad asset class (e.g., Equity, Debt, Hybrid). | `fund_master.csv` |
| `sub_category` | TEXT | Specific focus within category (e.g., Large Cap, Liquid). | `fund_master.csv` |
| `plan` | TEXT | Investment plan type (Regular or Direct). | `fund_master.csv` |
| `launch_date` | DATE | Inception date of the mutual fund scheme. | `fund_master.csv` |
| `benchmark` | TEXT | Benchmark index used to compare performance. | `fund_master.csv` |
| `expense_ratio_pct` | REAL | Annual fee charged by the AMC (as a percentage). | `fund_master.csv` |
| `exit_load_pct` | REAL | Fee charged for premature redemption (as a percentage). | `fund_master.csv` |
| `min_sip_amount` | REAL | Minimum INR amount required to start a SIP. | `fund_master.csv` |
| `min_lumpsum_amount` | REAL | Minimum INR amount required for lumpsum investment. | `fund_master.csv` |
| `fund_manager` | TEXT | Lead portfolio manager for the scheme. | `fund_master.csv` |
| `risk_category` | TEXT | Risk grading (e.g., Low, Moderate, High, Very High). | `fund_master.csv` |
| `sebi_category_code` | TEXT | Standardized classification code defined by SEBI. | `fund_master.csv` |

### `dim_date`
Calendar table to optimize time-series analysis and grouping.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `date_id` | TEXT (PK) | Date string in YYYY-MM-DD format. | Generated via Script |
| `date` | DATE | The exact calendar date. | Generated via Script |
| `year` | INTEGER | Calendar year. | Generated via Script |
| `month` | INTEGER | Calendar month (1-12). | Generated via Script |
| `quarter` | INTEGER | Calendar quarter (1-4). | Generated via Script |
| `is_weekday` | INTEGER | Boolean flag (1=Monday-Friday, 0=Weekend). | Generated via Script |

---

## 2. Fact Tables

### `fact_nav`
Stores the daily historical Net Asset Value (price) for each scheme.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `nav_id` | INTEGER (PK)| Auto-incrementing primary key. | Auto-generated |
| `amfi_code` | TEXT (FK) | Foreign key linking to `dim_fund`. | `nav_history.csv` |
| `nav_date` | DATE (FK) | Foreign key linking to `dim_date`. | `nav_history.csv` |
| `nav` | REAL | The Net Asset Value per unit on the given date. | `nav_history.csv` |
| `daily_return_pct` | REAL | Percentage change in NAV from the previous trading day. | `nav_history.csv` |

### `fact_transactions`
Log of every individual investment and redemption made by users.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `tx_id` | INTEGER (PK)| Auto-incrementing primary key. | Auto-generated |
| `investor_id` | TEXT | Unique identifier for the retail investor. | `investor_transactions.csv` |
| `transaction_date` | DATE (FK) | Foreign key linking to `dim_date`. | `investor_transactions.csv` |
| `amfi_code` | TEXT (FK) | Foreign key linking to `dim_fund`. | `investor_transactions.csv` |
| `transaction_type` | TEXT | Type of investment (SIP, Lumpsum, or Redemption). | `investor_transactions.csv` |
| `amount_inr` | REAL | The monetary value of the transaction in INR. | `investor_transactions.csv` |
| `state` | TEXT | State of residence of the investor. | `investor_transactions.csv` |
| `city` | TEXT | City of residence of the investor. | `investor_transactions.csv` |
| `city_tier` | TEXT | Tier classification of the city (e.g., Tier 1, Tier 2). | `investor_transactions.csv` |
| `age_group` | TEXT | Demographic age bracket of the investor. | `investor_transactions.csv` |
| `gender` | TEXT | Gender of the investor. | `investor_transactions.csv` |
| `annual_income_lakh`| REAL | Declared annual income of the investor in Lakhs. | `investor_transactions.csv` |
| `payment_mode` | TEXT | Method of payment (e.g., Net Banking, UPI). | `investor_transactions.csv` |
| `kyc_status` | TEXT | Verification status (Verified or Pending). | `investor_transactions.csv` |

### `fact_performance`
Stores aggregated financial and risk metrics calculated per fund.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `perf_id` | INTEGER (PK)| Auto-incrementing primary key. | Auto-generated |
| `amfi_code` | TEXT (FK) | Foreign key linking to `dim_fund`. | `scheme_performance.csv` |
| `return_1yr_pct` | REAL | 1-Year trailing annualized return. | `scheme_performance.csv` |
| `return_3yr_pct` | REAL | 3-Year trailing annualized return. | `scheme_performance.csv` |
| `return_5yr_pct` | REAL | 5-Year trailing annualized return. | `scheme_performance.csv` |
| `benchmark_3yr_pct` | REAL | 3-Year annualized return of the benchmark index. | `scheme_performance.csv` |
| `alpha` | REAL | Excess return of the fund relative to the benchmark. | `scheme_performance.csv` |
| `beta` | REAL | Volatility of the fund relative to the overall market. | `scheme_performance.csv` |
| `sharpe_ratio` | REAL | Risk-adjusted return metric (Return minus Risk-Free Rate / Std Dev).| `scheme_performance.csv` |
| `sortino_ratio` | REAL | Similar to Sharpe, but only penalizes downside volatility. | `scheme_performance.csv` |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of returns (Volatility). | `scheme_performance.csv` |
| `max_drawdown_pct` | REAL | Maximum observed peak-to-trough drop in NAV. | `scheme_performance.csv` |
| `aum_crore` | REAL | Total Assets Under Management in Crores. | `scheme_performance.csv` |
| `expense_ratio_pct` | REAL | The current expense ratio of the fund. | `scheme_performance.csv` |
| `morningstar_rating`| INTEGER | 1 to 5 star rating assigned by Morningstar. | `scheme_performance.csv` |
| `risk_grade` | TEXT | Risk classification text. | `scheme_performance.csv` |
| `expense_ratio_anomaly`| INTEGER | 1 if expense ratio was outside SEBI range, 0 otherwise. | Data Cleaning Output |
| `negative_sharpe` | INTEGER | 1 if the sharpe ratio is below 0, 0 otherwise. | Data Cleaning Output |

### `fact_aum`
Tracks the macro-level Assets Under Management for entire fund houses over time.

| Column Name | Data Type | Business Definition | Source Reference |
| :--- | :--- | :--- | :--- |
| `aum_id` | INTEGER (PK)| Auto-incrementing primary key. | Auto-generated |
| `date` | DATE (FK) | Foreign key linking to `dim_date`. | `aum_by_fund_house.csv` |
| `fund_house` | TEXT | Asset Management Company (AMC). | `aum_by_fund_house.csv` |
| `aum_lakh_crore` | REAL | Assets Under Management represented in Lakh Crores. | `aum_by_fund_house.csv` |
| `aum_crore` | REAL | Assets Under Management converted to Crores. | `aum_by_fund_house.csv` |
| `num_schemes` | INTEGER | Total number of individual schemes managed by the AMC. | `aum_by_fund_house.csv` |
