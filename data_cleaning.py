import pandas as pd
import numpy as np
import os
import sqlite3
from sqlalchemy import create_engine, text

def clean_nav_history(raw_dir, proc_dir):
    print("Cleaning nav_history.csv...")
    df = pd.read_csv(os.path.join(raw_dir, "02_nav_history.csv"))
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort
    df = df.sort_values(by=['amfi_code', 'date'])
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'], keep='last')
    
    # Validate NAV > 0
    df = df[df['nav'] > 0]
    
    # Forward-fill missing dates for each amfi_code
    # Create a complete combination of all dates and all amfi_codes
    min_date = df['date'].min()
    max_date = df['date'].max()
    full_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    full_idx = pd.MultiIndex.from_product([df['amfi_code'].unique(), full_dates], names=['amfi_code', 'date'])
    df = df.set_index(['amfi_code', 'date']).reindex(full_idx).groupby(level=0).ffill().reset_index()
    
    df.to_csv(os.path.join(proc_dir, "02_nav_history_cleaned.csv"), index=False)
    return df

def clean_transactions(raw_dir, proc_dir):
    print("Cleaning investor_transactions.csv...")
    df = pd.read_csv(os.path.join(raw_dir, "08_investor_transactions.csv"))
    
    # Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Validate amount > 0
    df = df[df['amount_inr'] > 0]
    
    # Standardize transaction_type
    def std_type(t):
        t = str(t).upper().strip()
        if 'SIP' in t: return 'SIP'
        if 'LUMP' in t: return 'Lumpsum'
        if 'REDEMP' in t: return 'Redemption'
        return 'Unknown'
    df['transaction_type'] = df['transaction_type'].apply(std_type)
    
    # Check KYC status
    df['kyc_status'] = df['kyc_status'].apply(lambda x: x if x in ['Verified', 'Pending'] else 'Unknown')
    
    df.to_csv(os.path.join(proc_dir, "08_investor_transactions_cleaned.csv"), index=False)
    return df

def clean_performance(raw_dir, proc_dir):
    print("Cleaning scheme_performance.csv...")
    df = pd.read_csv(os.path.join(raw_dir, "07_scheme_performance.csv"))
    
    # Ensure numeric
    numeric_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'expense_ratio_pct', 'sharpe_ratio']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Check expense_ratio range (0.1% - 2.5%)
    # If out of bounds, maybe clip or just flag. We will clip/cap for cleaning.
    if 'expense_ratio_pct' in df.columns:
        df['expense_ratio_anomaly'] = (df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)
        df['expense_ratio_pct'] = df['expense_ratio_pct'].clip(0.1, 2.5)
        
    if 'sharpe_ratio' in df.columns:
        df['negative_sharpe'] = df['sharpe_ratio'] < 0
        
    df.to_csv(os.path.join(proc_dir, "07_scheme_performance_cleaned.csv"), index=False)
    return df

def copy_other_files(raw_dir, proc_dir):
    print("Processing remaining files...")
    files = [
        "01_fund_master.csv", "03_aum_by_fund_house.csv", "04_monthly_sip_inflows.csv",
        "05_category_inflows.csv", "06_industry_folio_count.csv", "09_portfolio_holdings.csv",
        "10_benchmark_indices.csv"
    ]
    dfs = {}
    for f in files:
        df = pd.read_csv(os.path.join(raw_dir, f))
        out_name = f.replace('.csv', '_cleaned.csv')
        df.to_csv(os.path.join(proc_dir, out_name), index=False)
        dfs[f] = df
    return dfs

def create_dim_date(nav_df, proc_dir):
    print("Creating dim_date...")
    dates = pd.DataFrame({'date': pd.to_datetime(nav_df['date'].unique())})
    dates = dates.sort_values('date').reset_index(drop=True)
    dates['date_id'] = dates['date'].dt.strftime('%Y-%m-%d')
    dates['year'] = dates['date'].dt.year
    dates['month'] = dates['date'].dt.month
    dates['quarter'] = dates['date'].dt.quarter
    dates['is_weekday'] = dates['date'].dt.dayofweek < 5
    
    dates.to_csv(os.path.join(proc_dir, "dim_date.csv"), index=False)
    return dates

def load_to_sqlite(proc_dir, db_path):
    print(f"Loading data to {db_path}...")
    
    # First, execute schema
    conn = sqlite3.connect(db_path)
    with open("schema.sql", "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()
    
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Mappings
    table_mappings = {
        "01_fund_master_cleaned.csv": "dim_fund",
        "dim_date.csv": "dim_date",
        "02_nav_history_cleaned.csv": "fact_nav",
        "08_investor_transactions_cleaned.csv": "fact_transactions",
        "07_scheme_performance_cleaned.csv": "fact_performance",
        "03_aum_by_fund_house_cleaned.csv": "fact_aum",
        # other tables can be loaded as flat tables if needed
    }
    
    for file_name, table_name in table_mappings.items():
        file_path = os.path.join(proc_dir, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            # Format dates for SQLite (strings YYYY-MM-DD)
            if 'date' in df.columns and table_name != 'dim_date':
                if table_name == 'fact_nav':
                    df['nav_date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                    df = df.drop(columns=['date'])
                else:
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            elif 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
            elif 'date' in df.columns and table_name == 'dim_date':
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                
            print(f"Loading {len(df)} rows into {table_name}...")
            df.to_sql(table_name, engine, if_exists='append', index=False)
            
    print("Database loading complete.")

if __name__ == "__main__":
    raw_dir = os.path.join("data", "raw")
    proc_dir = os.path.join("data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    
    nav_df = clean_nav_history(raw_dir, proc_dir)
    tx_df = clean_transactions(raw_dir, proc_dir)
    perf_df = clean_performance(raw_dir, proc_dir)
    other_dfs = copy_other_files(raw_dir, proc_dir)
    
    dim_date = create_dim_date(nav_df, proc_dir)
    
    db_path = "bluestock_mf.db"
    if os.path.exists(db_path):
        os.remove(db_path) # start fresh
        
    load_to_sqlite(proc_dir, db_path)
