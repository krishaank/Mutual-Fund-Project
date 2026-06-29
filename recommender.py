"""\nrecommender.py\nPart of the Bluestock Mutual Fund Analytics Capstone Project.\n"""\n\nimport pandas as pd
import sqlite3
import argparse

def recommend_funds(risk_appetite):
    print(f"Generating recommendations for Risk Appetite: {risk_appetite}")
    
    # Map input to database risk_category
    risk_mapping = {
        'Low': ['Low', 'Low to Moderate'],
        'Moderate': ['Moderate', 'Moderately High'],
        'High': ['High', 'Very High']
    }
    
    allowed_risks = risk_mapping.get(risk_appetite, [])
    if not allowed_risks:
        print("Invalid risk appetite. Please choose from: Low, Moderate, High")
        return
    
    try:
        scorecard = pd.read_csv('data/processed/fund_scorecard.csv')
    except FileNotFoundError:
        print("Error: fund_scorecard.csv not found. Please run Performance Analytics first.")
        return
        
    conn = sqlite3.connect('bluestock_mf.db')
    query = f"SELECT scheme_name, risk_category, category FROM dim_fund"
    dim_fund = pd.read_sql(query, conn)
    conn.close()
    
    # Merge and filter
    merged = pd.merge(scorecard, dim_fund, on='scheme_name')
    filtered = merged[merged['risk_category'].isin(allowed_risks)]
    
    if len(filtered) == 0:
        print(f"No funds found matching risk categories {allowed_risks}")
        return
        
    # Get top 3 by Sharpe Ratio
    top_3 = filtered.sort_values(by='Sharpe_Ratio', ascending=False).head(3)
    
    print("\n" + "="*60)
    print(f" Top 3 Recommended Funds ({risk_appetite} Risk)")
    print("="*60)
    
    for i, row in top_3.iterrows():
        print(f"{row['scheme_name']}")
        print(f"   - Category: {row['category']} | Risk: {row['risk_category']}")
        print(f"   - Sharpe Ratio: {row['Sharpe_Ratio']:.2f}")
        print(f"   - 3-Year CAGR: {row['CAGR_3yr']*100:.2f}%")
        print("-" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mutual Fund Recommender")
    parser.add_argument('--risk', type=str, choices=['Low', 'Moderate', 'High'], required=True, help="Risk Appetite")
    args = parser.parse_args()
    
    recommend_funds(args.risk)
