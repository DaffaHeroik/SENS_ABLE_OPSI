import json
from pathlib import Path

root = Path('/tmp/sensable_complete_run')
validation = json.loads((root / 'reports' / 'glucometer_validation.json').read_text())
comparison = json.loads((root / 'reports' / 'model_comparison.json').read_text())
quality = json.loads((root / 'data' / 'processed' / 'quality_report.json').read_text())
print('glucometer_validation=', validation.get('evaluation'))
print('comparison_rows=', comparison['dataset']['rows'])
print('comparison_subjects=', comparison['dataset']['unique_subjects'])
print('selected=', comparison['selected_exploratory_model'])
for model in comparison['models']:
    print(model['model'], model['overall'])
print('quality_processed_rows=', quality.get('processed_rows'))
print('quality_excluded_rows=', quality.get('excluded_rows'))
print('artifact_bytes=', (root / 'models' / 'glucose_model_v0_1.joblib').stat().st_size)
print('figures=', len(list((root / 'reports' / 'figures').glob('*.png'))))
