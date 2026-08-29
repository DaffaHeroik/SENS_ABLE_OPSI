import json
from pathlib import Path

import numpy as np
import pandas as pd

root = Path('/home/ubuntu/SENS_ABLE_OPSI')
frame = pd.read_csv(root / 'data/processed/sensable_validation.csv')
report = json.loads((root / 'reports/model_comparison.json').read_text())
rf = next(item for item in report['models'] if item['model'] == 'RandomForestRegressor')
features = report['dataset']['feature_columns']
frame['prediction'] = rf['predictions']
frame['abs_error'] = (frame['GlukosaRef'] - frame['prediction']).abs()
print('rows', len(frame))
print('subjects', frame['SubjectID'].nunique())
print('target_summary', frame['GlukosaRef'].describe().round(4).to_dict())
print('target_unique', sorted(frame['GlukosaRef'].unique().tolist()))
print('target_duplicates', int(frame['GlukosaRef'].duplicated().sum()))
print('target_range', float(frame['GlukosaRef'].max() - frame['GlukosaRef'].min()))
print('feature_constant_or_low_variance')
for col in features:
    numeric = pd.to_numeric(frame[col], errors='coerce')
    print(col, 'nunique=', int(numeric.nunique()), 'std=', round(float(numeric.std()), 6), 'missing=', int(numeric.isna().sum()))
print('correlation_with_target')
correlations = frame[features + ['GlukosaRef']].corr(numeric_only=True)['GlukosaRef'].drop('GlukosaRef').sort_values(key=lambda s: s.abs(), ascending=False)
for col, value in correlations.items():
    print(col, round(float(value), 6))
print('largest_errors')
for _, row in frame.sort_values('abs_error', ascending=False).head(10).iterrows():
    print(row['SubjectID'], 'ref=', row['GlukosaRef'], 'pred=', round(row['prediction'], 4), 'abs_error=', round(row['abs_error'], 4), 'imputed_body=', row.get('SuhuTubuh_Imputed'), 'imputed_ambient=', row.get('SuhuAmbient_Imputed'), 'samples=', row.get('Samples'))
