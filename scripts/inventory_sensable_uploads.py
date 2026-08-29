from pathlib import Path
import hashlib
import pandas as pd

root = Path('/home/ubuntu/upload')
files = sorted([p for p in root.iterdir() if p.is_file()])
for path in files:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    try:
        if path.suffix.lower() == '.xlsx':
            sheets = pd.ExcelFile(path).sheet_names
            print(f'{path.name}\tXLSX\tsheets={sheets}\tsha={digest}')
            for sheet in sheets:
                df = pd.read_excel(path, sheet_name=sheet)
                print(f'  sheet={sheet!r}\trows={len(df)}\tcols={len(df.columns)}\theader={list(df.columns)}')
        else:
            df = pd.read_csv(path)
            print(f'{path.name}\tCSV\trows={len(df)}\tcols={len(df.columns)}\tsha={digest}')
            print(f'  header={list(df.columns)}')
            if 'Nama' in df.columns:
                print(f'  names={df["Nama"].nunique()}\tlabels={df["Diabetes"].value_counts(dropna=False).to_dict() if "Diabetes" in df.columns else "n/a"}')
    except Exception as exc:
        print(f'{path.name}\tERROR\t{type(exc).__name__}: {exc}\tsha={digest}')
