"""
Master Pipeline Script for Bluestock Mutual Fund Analytics
Executes the end-to-end data pipeline:
1. Data Ingestion (SQLite Star Schema Creation)
2. EDA Generation
3. Performance Analytics (Sharpe, Alpha, Beta)
4. Advanced Analytics (VaR, CVaR, Cohorts)
"""

import os
import subprocess
import sys

def run_script(script_name):
    """Helper function to execute a Python script and capture its output."""
    print(f"\\n{'='*50}")
    print(f"Running: {script_name}")
    print(f"{'='*50}")
    try:
        # Use the same python executable that is running this script
        subprocess.run([sys.executable, script_name], check=True)
        print(f"Successfully completed: {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}")
        sys.exit(1)

def main():
    print("Starting Bluestock Mutual Fund Analytics Pipeline...")
    
    # 1. Data Ingestion
    run_script(os.path.join("scripts", "etl_pipeline.py"))
    
    # 2. EDA Generation (Generates notebook and PNGs)
    run_script(os.path.join("scripts", "generate_eda.py"))
    
    # 3. Performance Analytics (Generates notebook, scorecard, alpha/beta)
    run_script(os.path.join("scripts", "compute_metrics.py"))
    
    # 4. Advanced Analytics (Generates notebook, VaR/CVaR, HHI)
    run_script(os.path.join("scripts", "generate_advanced_analytics.py"))
    
    print("\\nPipeline Execution Complete!")
    print("You can now launch the dashboard using: streamlit run app.py")

if __name__ == "__main__":
    main()
