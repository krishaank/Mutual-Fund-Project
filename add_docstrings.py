import os

scripts = [
    "data_ingestion.py", 
    "generate_eda.py", 
    "generate_performance_analytics.py", 
    "generate_advanced_analytics.py", 
    "recommender.py", 
    "app.py"
]

for script in scripts:
    if os.path.exists(script):
        with open(script, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.startswith('"""'):
            docstring = f'"""\\n{script}\\nPart of the Bluestock Mutual Fund Analytics Capstone Project.\\n"""\\n\\n'
            with open(script, 'w', encoding='utf-8') as f:
                f.write(docstring + content)
            print(f"Added docstring to {script}")
