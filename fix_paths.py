import os
import glob
import re

scripts_to_update = glob.glob('scripts/*.py') + glob.glob('dashboard/*.py') + ['run_pipeline.py']

for script in scripts_to_update:
    with open(script, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add pathlib and os if not there
    if 'import pathlib' not in content:
        content = re.sub(r'import pandas', 'import pandas\nimport pathlib\nimport os', content)
        content = re.sub(r'import sqlite3', 'import sqlite3\nimport pathlib\nimport os', content)
        content = re.sub(r'import streamlit', 'import streamlit\nimport pathlib\nimport os', content)

    if 'run_pipeline.py' not in script:
        # Define PROJECT_ROOT
        if 'PROJECT_ROOT' not in content:
            content = re.sub(r'(import .*?\n)+', r'\g<0>\nPROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()\n', content, count=1)
            
        # Replace DB_PATH = 'bluestock_mf.db'
        content = re.sub(r"DB_PATH = 'bluestock_mf.db'", "DB_PATH = PROJECT_ROOT / 'data' / 'db' / 'bluestock_mf.db'", content)
        content = re.sub(r"DB_PATH = \"bluestock_mf.db\"", "DB_PATH = PROJECT_ROOT / 'data' / 'db' / 'bluestock_mf.db'", content)
        content = re.sub(r"sqlite3.connect\('bluestock_mf.db'\)", "sqlite3.connect(PROJECT_ROOT / 'data' / 'db' / 'bluestock_mf.db')", content)
        
        # Replace data/processed
        content = re.sub(r"data/processed", "data/processed", content) # already correct if we use PROJECT_ROOT
        content = re.sub(r"'data/processed", "PROJECT_ROOT / 'data/processed", content)
        content = re.sub(r"\"data/processed", "PROJECT_ROOT / 'data/processed", content)
        
        # Replace notebooks/
        content = re.sub(r"'notebooks/.*?\.ipynb'", lambda m: f"PROJECT_ROOT / {m.group(0)}", content)
        
        # Replace reports/
        content = re.sub(r"'reports/.*?'", lambda m: f"PROJECT_ROOT / {m.group(0)}", content)
        content = re.sub(r"\"reports/.*?\"", lambda m: f"PROJECT_ROOT / {m.group(0)}", content)
        
    with open(script, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated paths in {script}")

