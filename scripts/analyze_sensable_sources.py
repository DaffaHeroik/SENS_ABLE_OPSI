from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path('/home/ubuntu/upload')
frames = []
for path in sorted(ROOT.iterdir()):
    if not path.is_file():
        continue
    if path.suffix.lower() == '.xlsx':
        book = pd.ExcelFile(path)
        for sheet in book.sheet_names:
            frame = pd.read_excel(path, sheet_name=sheet)
            frame['__source'] = f'{path.name}::{sheet}'
            frames.append(frame)
    else:
        frame = pd.read_csv(path)
        frame['__source'] = path.name
        frames.append(frame)

base_cols = [c for c in frames[0].columns if c != '__source']
all_df = pd.concat(frames, ignore_index=True)
for col in base_cols:
    if col == 'Nama' or col == 'Gender':
        all_df[col] = all_df[col].astype('string').str.strip()
    else:
        all_df[col] = pd.to_numeric(all_df[col], errors='coerce')

# Normalize numeric representation so 57 and 57.0 compare equally.
key_df = all_df[base_cols].copy()
for col in base_cols:
    if col not in {'Nama', 'Gender'}:
        key_df[col] = key_df[col].round(8)
key_df['Nama'] = key_df['Nama'].str.casefold()
all_df['__key'] = key_df.astype('string').fillna('<NA>').agg('|'.join, axis=1)

print('file_count', len(frames))
print('combined_rows', len(all_df))
print('unique_normalized_rows', all_df['__key'].nunique())
print('duplicate_rows_removed_if_normalized', len(all_df) - all_df['__key'].nunique())
print('source_summary')
for source, frame in all_df.groupby('__source', sort=False):
    print(source, 'rows=', len(frame), 'unique_norm_rows=', frame['__key'].nunique(), 'sha=', hashlib.sha256((ROOT / source.split('::')[0]).read_bytes()).hexdigest()[:12])

unique = all_df.drop_duplicates('__key', keep='first').copy()
print('unique_labels', unique['Diabetes'].value_counts(dropna=False).to_dict())
print('unique_names', unique['Nama'].nunique())
print('duplicate_name_rows', int(unique.duplicated('Nama', keep=False).sum()))
print('duplicate_name_values', unique.loc[unique.duplicated('Nama', keep=False), 'Nama'].value_counts().to_dict())
print('potential_sensor_outliers')
checks = {
    'HR_est_outside_40_180': ~unique['HR_est'].between(40, 180),
    'SpO2_outside_70_100': ~unique['SpO2_est'].between(70, 100),
    'IR_Mean_below_10000': unique['IR_Mean'] < 10000,
    'RED_Mean_nonpositive': unique['RED_Mean'] <= 0,
    'IR_Min_gt_IR_Max': unique['IR_Min'] > unique['IR_Max'],
    'RED_Min_gt_RED_Max': unique['RED_Min'] > unique['RED_Max'],
    'glucose_outside_20_600': ~unique['GlukosaRef'].between(20, 600),
}
for name, mask in checks.items():
    print(name, int(mask.sum()), unique.loc[mask, ['Nama', 'GlukosaRef', 'HR_est', 'SpO2_est', 'IR_Mean', 'RED_Mean']].to_dict('records'))

print('duplicate_name_records')
print(unique.loc[unique.duplicated('Nama', keep=False), ['Nama', 'Usia', 'Gender', 'GlukosaRef', 'SuhuTubuh', 'HR_est', 'IR_Mean', 'RED_Mean']].to_string(index=False))
