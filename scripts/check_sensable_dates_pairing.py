from pathlib import Path
import pandas as pd

root = Path('/home/ubuntu/SENS_ABLE_OPSI/data/raw')
files = sorted(p for p in root.iterdir() if p.is_file() and not p.name.startswith('MANIFEST') and (p.suffix.lower() in {'.csv', '.xlsx'} or p.name == 'sensable_dataset100'))
print('file_count', len(files))
for path in files:
    if path.suffix.lower() == '.xlsx':
        sources = [(sheet, pd.read_excel(path, sheet_name=sheet)) for sheet in pd.ExcelFile(path).sheet_names]
    else:
        sources = [('csv', pd.read_csv(path))]
    for sheet, frame in sources:
        date_cols = [c for c in frame.columns if any(token in str(c).lower() for token in ('date', 'tanggal', 'waktu', 'time', 'timestamp'))]
        glucose_cols = [c for c in frame.columns if any(token in str(c).lower() for token in ('gluk', 'glucose', 'gula'))]
        print(path.name, sheet, 'rows=', len(frame), 'columns=', len(frame.columns), 'date_like=', date_cols, 'glucose_like=', glucose_cols, 'glukosa_ref_nonnull=', int(frame['GlukosaRef'].notna().sum()) if 'GlukosaRef' in frame else 'MISSING')
