from pathlib import Path
import pandas as pd

root = Path('/home/ubuntu/upload')
frames = []
for path in sorted(root.iterdir()):
    if not path.is_file() or (path.suffix.lower() not in {'.csv', '.xlsx'} and path.name != 'sensable_dataset100'):
        continue
    if path.suffix.lower() == '.xlsx':
        for sheet in pd.ExcelFile(path).sheet_names:
            frame = pd.read_excel(path, sheet_name=sheet)
            frame['_source'] = f'{path.name}::{sheet}'
            frames.append(frame)
    else:
        frame = pd.read_csv(path)
        frame['_source'] = path.name
        frames.append(frame)
base = [c for c in frames[0].columns if c != '_source']
df = pd.concat(frames, ignore_index=True)
for col in base:
    if col in {'Nama', 'Gender'}:
        df[col] = df[col].astype('string').str.strip()
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')
key = df[base].copy()
key['Nama'] = key['Nama'].str.casefold()
for col in base:
    if col not in {'Nama', 'Gender'}:
        key[col] = key[col].round(8)
df['_key'] = key.astype('string').fillna('<NA>').agg('|'.join, axis=1)
unique = df.drop_duplicates('_key', keep='first')
valid_optical = (unique['IR_Mean'] >= 10000) & (unique['RED_Mean'] >= 10000)
valid_temp = unique['SuhuTubuh'] > 0
recoverable = valid_optical & ~valid_temp
unusable = ~valid_optical
print('unique_rows', len(unique))
print('valid_temperature_rows', int(valid_temp.sum()))
print('recoverable_zero_temperature_rows', int(recoverable.sum()))
print('unusable_optical_rows', int(unusable.sum()))
print('mean_valid_body_temperature', round(float(unique.loc[valid_temp, 'SuhuTubuh'].mean()), 6))
print('median_valid_body_temperature', round(float(unique.loc[valid_temp, 'SuhuTubuh'].median()), 6))
valid_ambient = unique['SuhuAmbient'] > 0
print('mean_valid_ambient_temperature', round(float(unique.loc[valid_ambient, 'SuhuAmbient'].mean()), 6))
print('median_valid_ambient_temperature', round(float(unique.loc[valid_ambient, 'SuhuAmbient'].median()), 6))
print('recoverable_records')
print(unique.loc[recoverable, ['Nama','Usia','GlukosaRef','SuhuTubuh','SuhuAmbient','IR_Mean','RED_Mean','_source']].to_string(index=False))
print('unusable_records')
print(unique.loc[unusable, ['Nama','Usia','GlukosaRef','SuhuTubuh','SuhuAmbient','HR_est','IR_Mean','RED_Mean','_source']].to_string(index=False))
