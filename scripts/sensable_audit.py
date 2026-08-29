from pathlib import Path
import pandas as pd

repo = Path('/home/ubuntu/SENS_ABLE_OPSI')
df = pd.read_csv(repo / 'data/sensable_final.csv')
print('rows', len(df))
print('columns', len(df.columns))
print('missing_total', int(df.isna().sum().sum()))
print('missing_by_column', {k: int(v) for k, v in df.isna().sum().items() if v})
print('diabetes_counts', {str(k): int(v) for k, v in df['Diabetes'].value_counts().sort_index().items()})
print('unique_names', int(df['Nama'].nunique()))
print('duplicate_full_rows', int(df.duplicated().sum()))
print('duplicate_name_rows', int(df.duplicated('Nama', keep=False).sum()))
print('duplicate_name_values', df.loc[df.duplicated('Nama', keep=False), 'Nama'].value_counts().to_dict())
print('gender_age_bmi_conflicts', int(df.groupby(['Nama', 'Usia', 'BMI']).Gender.nunique().gt(1).sum()))
print('range_checks', {
    'age_outside_0_120': int((~df['Usia'].between(0, 120)).sum()),
    'bmi_nonpositive': int((df['BMI'] <= 0).sum()),
    'glucose_nonpositive': int((df['GlukosaRef'] <= 0).sum()),
    'spo2_outside_0_100': int((~df['SpO2_est'].between(0, 100)).sum()),
    'hr_nonpositive': int((df['HR_est'] <= 0).sum()),
})
print('sensitive_columns', [c for c in ['Nama', 'Usia', 'Gender', 'GlukosaRef', 'Diabetes'] if c in df.columns])
print('high_cardinality_identifiers', df['Nama'].nunique(), 'of', len(df))
