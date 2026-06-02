import requests
import pandas as pd
import os

def fetch_and_save_nav(scheme_code, name):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            df = pd.DataFrame(data['data'])
            # The API returns 'date' and 'nav'
            df['scheme_code'] = scheme_code
            df['scheme_name'] = name
            
            output_dir = os.path.join("data", "raw")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{scheme_code}_{name.replace(' ', '_')}_nav.csv")
            
            df.to_csv(output_path, index=False)
            print(f"Successfully saved NAV data for {name} ({scheme_code}) to {output_path}")
        else:
            print(f"No data found for {name} ({scheme_code})")
    else:
        print(f"Failed to fetch data for {name} ({scheme_code}). Status code: {response.status_code}")

if __name__ == "__main__":
    schemes = [
        {"code": 125497, "name": "HDFC Top 100 Direct"},
        {"code": 119551, "name": "SBI Bluechip"},
        {"code": 120503, "name": "ICICI Bluechip"},
        {"code": 118632, "name": "Nippon Large Cap"},
        {"code": 119092, "name": "Axis Bluechip"},
        {"code": 120841, "name": "Kotak Bluechip"}
    ]
    
    for scheme in schemes:
        fetch_and_save_nav(scheme['code'], scheme['name'])
