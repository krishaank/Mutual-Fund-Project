"""\ndata_ingestion.py\nPart of the Bluestock Mutual Fund Analytics Capstone Project.\n"""\n\nimport pandas as pd
import os

def check_anomalies(df, name):
    print(f"\n--- Anomalies for {name} ---")
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("Missing values found:")
        print(null_counts[null_counts > 0])
    else:
        print("No missing values found.")
        
    # Check for duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        print(f"Duplicate rows found: {dup_count}")
    else:
        print("No duplicate rows found.")

def main():
    data_dir = os.path.join("data", "raw")
    csv_files = [
        "01_fund_master.csv",
        "02_nav_history.csv",
        "03_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv",
        "05_category_inflows.csv",
        "06_industry_folio_count.csv",
        "07_scheme_performance.csv",
        "08_investor_transactions.csv",
        "09_portfolio_holdings.csv",
        "10_benchmark_indices.csv"
    ]
    
    dataframes = {}
    
    # 1. Load datasets and print basic info
    for file in csv_files:
        file_path = os.path.join(data_dir, file)
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found.")
            continue
            
        print(f"\n{'='*50}\nLoading: {file}\n{'='*50}")
        df = pd.read_csv(file_path)
        dataframes[file] = df
        
        print(f"Shape: {df.shape}\n")
        print("Data Types:")
        print(df.dtypes)
        print("\nHead:")
        print(df.head())
        
        check_anomalies(df, file)
        
    # 2. Explore fund master
    if "01_fund_master.csv" in dataframes:
        print("\n\n" + "="*50)
        print("EXPLORING FUND MASTER")
        print("="*50)
        fm_df = dataframes["01_fund_master.csv"]
        
        if 'fund_house' in fm_df.columns:
            print(f"\nUnique Fund Houses ({fm_df['fund_house'].nunique()}):")
            print(fm_df['fund_house'].unique()[:5], "...")
            
        if 'category' in fm_df.columns:
            print(f"\nUnique Categories ({fm_df['category'].nunique()}):")
            print(fm_df['category'].unique())
            
        if 'sub_category' in fm_df.columns:
            print(f"\nUnique Sub-Categories ({fm_df['sub_category'].nunique()}):")
            print(fm_df['sub_category'].unique()[:5], "...")
            
        if 'risk_grade' in fm_df.columns:
            print(f"\nUnique Risk Grades:")
            print(fm_df['risk_grade'].unique())
            
    # 3. Validate AMFI codes
    if "01_fund_master.csv" in dataframes and "02_nav_history.csv" in dataframes:
        print("\n\n" + "="*50)
        print("VALIDATING AMFI CORES")
        print("="*50)
        fm_df = dataframes["01_fund_master.csv"]
        nav_df = dataframes["02_nav_history.csv"]
        
        # Determine the scheme code column name
        fm_code_col = 'scheme_code' if 'scheme_code' in fm_df.columns else None
        nav_code_col = 'scheme_code' if 'scheme_code' in nav_df.columns else None
        
        if not fm_code_col:
            # Try to guess
            if 'amfi_code' in fm_df.columns: fm_code_col = 'amfi_code'
            elif 'Scheme_Code' in fm_df.columns: fm_code_col = 'Scheme_Code'
            
        if not nav_code_col:
            if 'amfi_code' in nav_df.columns: nav_code_col = 'amfi_code'
            elif 'Scheme_Code' in nav_df.columns: nav_code_col = 'Scheme_Code'
            
        if fm_code_col and nav_code_col:
            fm_codes = set(fm_df[fm_code_col].dropna().unique())
            nav_codes = set(nav_df[nav_code_col].dropna().unique())
            
            missing_in_nav = fm_codes - nav_codes
            missing_in_fm = nav_codes - fm_codes
            
            summary = []
            summary.append("--- Data Quality Summary ---")
            summary.append(f"Total unique AMFI codes in Fund Master: {len(fm_codes)}")
            summary.append(f"Total unique AMFI codes in NAV History: {len(nav_codes)}")
            
            if len(missing_in_nav) == 0:
                summary.append("Validation PASS: All codes in Fund Master exist in NAV History.")
            else:
                summary.append(f"Validation FAIL: {len(missing_in_nav)} codes from Fund Master are MISSING in NAV History.")
                summary.append(f"Sample missing codes: {list(missing_in_nav)[:5]}")
                
            if len(missing_in_fm) > 0:
                summary.append(f"Note: There are {len(missing_in_fm)} codes in NAV History that are not in Fund Master.")
                
            summary_text = "\n".join(summary)
            print(summary_text)
            
            # Write summary to file
            with open("data_quality_summary.txt", "w") as f:
                f.write(summary_text)
            print("\nSaved Data Quality Summary to data_quality_summary.txt")
        else:
            print("Could not find scheme_code column in one or both dataframes.")
            print(f"Fund Master columns: {fm_df.columns.tolist()}")
            print(f"NAV History columns: {nav_df.columns.tolist()}")

if __name__ == "__main__":
    main()
