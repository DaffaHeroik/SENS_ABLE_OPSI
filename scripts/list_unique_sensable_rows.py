from pathlib import Path
import pandas as pd

ROOT = Path('/home/ubuntu/upload')
frames = []
for path in sorted(ROOT.iterdir()):
    if not path.is_file():
        continue
    if path.suffix.lower() == '.xlsx':
        for sheet in pd.ExcelFile(path).sheet_names:
            frame = pd.read_excel(path, sheet_name=sheet)
            frame['source'] = f'{path.name}::{sheet}'
            frames.append(frame)
    else:
        frame = pd.read_csv(path)
        frame['source'] = path.name
        frames.append(frame)
base = [c for c in frames[0].columns if c != 'source']
df = pd.concat(frames, ignore_index=True)
for c in base:
    if c in ('Nama', 'Gender'):
        df[c] = df[c].astype('string').str.strip()
    else:
        df[c] = pd.to_numeric(df[c], errors='coerce')
key = df[base].copy()
key['Nama'] = key['Nama'].str.casefold()
for c in base:
    if c not in ('Nama', 'Gender'):
        key[c] = key[c].round(8)
df['key'] = key.astype('string').fillna('<NA>').agg('|'.join, axis=1)
unique = df.drop_duplicates('key', keep='first').copy()
unique['sensor_flag'] = (
    (unique['HR_est'] > 180) |
    (unique['IR_Mean'] < 10000) |
    (unique['RED_Mean'] < 10000) |
    (unique['SuhuTubuh'] <= 0) |
    (unique['IR_Min'] <= 0) |
    (unique['RED_Min'] <= 0)
)
cols = ['Nama','Usia','Gender','GlukosaRef','SuhuTubuh','HR_est','SpO2_est','IR_Mean','IR_Min','RED_Mean','RED_Min','sensor_flag']
print(unique.sort_values(['sensor_flag','Nama','GlukosaRef'], ascending=[False,True,True])[cols].to_string(index=False))
print('\nCounts:', {'unique': len(unique), 'sensor_flag': int(unique.sensor_flag.sum()), 'clean_candidate': int((~unique.sensor_flag).sum())})
