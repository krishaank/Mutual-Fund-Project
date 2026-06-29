"""\ngenerate_performance_analytics.py\nPart of the Bluestock Mutual Fund Analytics Capstone Project.\n"""\n\nimport os
import sqlite3
import nbformat as nbf

def create_notebook():
    nb = nbf.v4.new_notebook()
    cells = []
    
    # 1. Introduction
    cells.append(nbf.v4.new_markdown_cell("""# Day 4: Advanced Performance Analytics
This notebook calculates risk-adjusted performance metrics, alpha/beta regressions, max drawdowns, and a composite Fund Scorecard for 40 mutual fund schemes.
"""))

    # 2. Setup
    cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

os.makedirs('../reports/images', exist_ok=True)
conn = sqlite3.connect('../bluestock_mf.db')

# Constants
RF_RATE = 0.065 # 6.5% RBI Repo Rate proxy
TRADING_DAYS = 252
"""))

    # 3. Load NAV and Benchmarks
    cells.append(nbf.v4.new_markdown_cell("""## 1. Daily Returns and Benchmarks"""))
    cells.append(nbf.v4.new_code_cell("""# Load NAV Data
query = '''
SELECT n.nav_date, n.nav, f.amfi_code, f.scheme_name, f.category, f.expense_ratio_pct
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
'''
nav_df = pd.read_sql(query, conn)
nav_df['nav_date'] = pd.to_datetime(nav_df['nav_date'])

# Pivot to compute returns easily
nav_pivot = nav_df.pivot_table(index='nav_date', columns='scheme_name', values='nav').sort_index()

# Compute Daily Returns
returns_df = nav_pivot.pct_change().dropna(how='all')

# Load Benchmark Data
benchmarks = pd.read_csv('../data/processed/10_benchmark_indices_cleaned.csv')
benchmarks['date'] = pd.to_datetime(benchmarks['date'])
benchmarks = benchmarks.pivot_table(index='date', columns='index_name', values='close_value')
benchmarks_returns = benchmarks.pct_change().dropna(how='all')
"""))

    # 4. CAGR Calculation
    cells.append(nbf.v4.new_markdown_cell("""## 2. CAGR Calculation (1yr, 3yr, 5yr)
Formula: $\\text{CAGR} = \\left(\\frac{NAV_{end}}{NAV_{start}}\\right)^{\\frac{1}{n}} - 1$"""))
    cells.append(nbf.v4.new_code_cell("""def compute_cagr(series, years):
    end_date = series.index[-1]
    start_date = end_date - pd.DateOffset(years=years)
    try:
        closest_start = series.index[series.index.searchsorted(start_date)]
        nav_end = series.iloc[-1]
        nav_start = series.loc[closest_start]
        if pd.isna(nav_end) or pd.isna(nav_start) or nav_start == 0:
            return np.nan
        return (nav_end / nav_start) ** (1/years) - 1
    except IndexError:
        return np.nan

cagr_data = []
for scheme in nav_pivot.columns:
    series = nav_pivot[scheme].dropna()
    if len(series) == 0: continue
    cagr_1 = compute_cagr(series, 1)
    cagr_3 = compute_cagr(series, 3)
    cagr_5 = compute_cagr(series, 5)
    cagr_data.append({'scheme_name': scheme, 'CAGR_1yr': cagr_1, 'CAGR_3yr': cagr_3, 'CAGR_5yr': cagr_5})

cagr_df = pd.DataFrame(cagr_data).set_index('scheme_name')
"""))

    # 5. Sharpe and Sortino
    cells.append(nbf.v4.new_markdown_cell("""## 3. Sharpe & Sortino Ratios
**Sharpe Ratio:** $\\frac{R_p - R_f}{\\sigma_p} \\times \\sqrt{252}$

**Sortino Ratio:** Same, but denominator is downside deviation."""))
    cells.append(nbf.v4.new_code_cell("""sharpe_sortino_data = []

for scheme in returns_df.columns:
    ret = returns_df[scheme].dropna()
    if len(ret) == 0: continue
    
    # Annualized Return
    ann_return = ret.mean() * TRADING_DAYS
    
    # Sharpe
    ann_vol = ret.std() * np.sqrt(TRADING_DAYS)
    sharpe = (ann_return - RF_RATE) / ann_vol if ann_vol != 0 else np.nan
    
    # Sortino
    downside_ret = ret[ret < 0]
    downside_vol = downside_ret.std() * np.sqrt(TRADING_DAYS)
    sortino = (ann_return - RF_RATE) / downside_vol if downside_vol != 0 else np.nan
    
    sharpe_sortino_data.append({
        'scheme_name': scheme,
        'Ann_Return': ann_return,
        'Ann_Volatility': ann_vol,
        'Sharpe_Ratio': sharpe,
        'Sortino_Ratio': sortino
    })

risk_df = pd.DataFrame(sharpe_sortino_data).set_index('scheme_name')
"""))

    # 6. Alpha and Beta
    cells.append(nbf.v4.new_markdown_cell("""## 4. Alpha and Beta (OLS Regression)
We regress each fund's daily returns against Nifty 100."""))
    cells.append(nbf.v4.new_code_cell("""alpha_beta_data = []

# Align dates
nifty100_ret = benchmarks_returns['NIFTY100'].dropna()

for scheme in returns_df.columns:
    fund_ret = returns_df[scheme].dropna()
    aligned = pd.concat([fund_ret, nifty100_ret], axis=1).dropna()
    
    if len(aligned) < 50:
        continue
        
    x = aligned['NIFTY100']
    y = aligned[scheme]
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    beta = slope
    alpha = intercept * TRADING_DAYS # Annualized alpha
    
    alpha_beta_data.append({
        'scheme_name': scheme,
        'Alpha': alpha,
        'Beta': beta
    })

ab_df = pd.DataFrame(alpha_beta_data).set_index('scheme_name')
ab_df.to_csv('../data/processed/alpha_beta.csv')
"""))

    # 7. Max Drawdown
    cells.append(nbf.v4.new_markdown_cell("""## 5. Maximum Drawdown
Min(NAV / Running_Max - 1)"""))
    cells.append(nbf.v4.new_code_cell("""drawdown_data = []

for scheme in nav_pivot.columns:
    series = nav_pivot[scheme].dropna()
    if len(series) == 0: continue
    
    running_max = series.cummax()
    drawdown = (series / running_max) - 1
    max_dd = drawdown.min()
    
    drawdown_data.append({
        'scheme_name': scheme,
        'Max_Drawdown': max_dd
    })

dd_df = pd.DataFrame(drawdown_data).set_index('scheme_name')
"""))

    # 8. Fund Scorecard
    cells.append(nbf.v4.new_markdown_cell("""## 6. Composite Fund Scorecard
Weighting:
- 30% x 3Yr Return Rank
- 25% x Sharpe Rank
- 20% x Alpha Rank
- 15% x Expense Ratio Rank (Inverse)
- 10% x Max DD Rank (Inverse)"""))
    cells.append(nbf.v4.new_code_cell("""# Combine all metrics
metrics_df = cagr_df.join([risk_df, ab_df, dd_df])

# Bring in expense ratio
exp_df = nav_df[['scheme_name', 'expense_ratio_pct']].drop_duplicates().set_index('scheme_name')
metrics_df = metrics_df.join(exp_df)

# Drop missing for ranking
score_df = metrics_df[['CAGR_3yr', 'Sharpe_Ratio', 'Alpha', 'expense_ratio_pct', 'Max_Drawdown']].dropna()

# Ranks (Higher is better for Return, Sharpe, Alpha; Lower is better for Exp Ratio, Max DD)
rank_ret = score_df['CAGR_3yr'].rank(pct=True)
rank_sharpe = score_df['Sharpe_Ratio'].rank(pct=True)
rank_alpha = score_df['Alpha'].rank(pct=True)
rank_exp = score_df['expense_ratio_pct'].rank(pct=True, ascending=False)
rank_dd = score_df['Max_Drawdown'].rank(pct=True) # Max DD is negative, so closer to 0 (higher value) is better!

score_df['Score'] = (
    0.30 * rank_ret +
    0.25 * rank_sharpe +
    0.20 * rank_alpha +
    0.15 * rank_exp +
    0.10 * rank_dd
) * 100

score_df = score_df.sort_values('Score', ascending=False)
score_df.to_csv('../data/processed/fund_scorecard.csv')
score_df.head(10)
"""))

    # 9. Benchmark Comparison
    cells.append(nbf.v4.new_markdown_cell("""## 7. Benchmark Comparison Chart (Top 5 Funds vs Benchmarks)
Plotting the Top 5 scored funds against Nifty 50 and Nifty 100."""))
    cells.append(nbf.v4.new_code_cell("""top_5 = score_df.head(5).index.tolist()

# Get data for last 3 years
end_date = nav_pivot.index[-1]
start_date = end_date - pd.DateOffset(years=3)

plot_data = nav_pivot[top_5].loc[start_date:end_date].copy()

# Normalize
plot_data = (plot_data / plot_data.iloc[0]) * 100

bench_plot = benchmarks[['NIFTY50', 'NIFTY100']].loc[start_date:end_date].copy()
if len(bench_plot) > 0:
    bench_plot = (bench_plot / bench_plot.iloc[0]) * 100
    plot_data = plot_data.join(bench_plot)

plt.figure(figsize=(14, 8))
for col in top_5:
    plt.plot(plot_data.index, plot_data[col], label=col, linewidth=2)

if 'NIFTY50' in plot_data.columns:
    plt.plot(plot_data.index, plot_data['NIFTY50'], label='Nifty 50', color='black', linestyle='--', linewidth=2.5)
if 'NIFTY100' in plot_data.columns:
    plt.plot(plot_data.index, plot_data['NIFTY100'], label='Nifty 100', color='gray', linestyle=':', linewidth=2.5)

plt.title('Top 5 Funds vs Benchmarks (3-Year Normalized NAV)')
plt.ylabel('Normalized NAV (Base 100)')
plt.xlabel('Date')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('../reports/images/benchmark_comparison.png')
plt.show()

# Tracking Error Computation for Top 5 against Nifty 50
print("Tracking Error (vs Nifty 50):")
nifty50_ret = benchmarks_returns['NIFTY50'].loc[start_date:end_date]
for f in top_5:
    fund_ret = returns_df[f].loc[start_date:end_date]
    aligned = pd.concat([fund_ret, nifty50_ret], axis=1).dropna()
    if len(aligned) > 0:
        te = (aligned[f] - aligned['NIFTY50']).std() * np.sqrt(TRADING_DAYS)
        print(f"{f}: {te*100:.2f}%")
"""))

    nb['cells'] = cells
    
    with open('notebooks/Performance_Analytics.ipynb', 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print("Performance_Analytics.ipynb generated successfully.")

if __name__ == '__main__':
    create_notebook()
