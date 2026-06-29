import glob

files = glob.glob('scripts/*.py') + glob.glob('dashboard/*.py')

for f_path in files:
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove any messed up docstrings and restore imports
    # I will just ensure import pandas is there for etl_pipeline, etc.
    if 'import pandas' not in content and 'etl_pipeline' in f_path:
        content = "import pandas\n" + content
    if 'import pandas' not in content and 'generate_eda' in f_path:
        content = "import pandas\n" + content
    
    # Strip everything before the first import
    import_idx = content.find('import ')
    if import_idx != -1:
        content = content[import_idx:]
    
    # Prepend clean docstring
    clean_doc = '"""Bluestock Mutual Fund Analytics Capstone Project."""\n\n'
    
    with open(f_path, 'w', encoding='utf-8') as f:
        f.write(clean_doc + content)
