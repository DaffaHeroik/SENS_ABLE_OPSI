import json
from pathlib import Path

root = Path('/home/ubuntu/SENS_ABLE_OPSI')
report = json.loads((root / 'reports' / 'model_comparison.json').read_text())
print('selected=', report['selected_exploratory_model'])
for model in report['models']:
    print(model['model'], model['overall'])
print('artifact_exists=', (root / 'models' / 'glucose_model_v0_1.joblib').exists())
print('figures=', len(list((root / 'reports' / 'figures').glob('*.png'))))
