from pathlib import Path
import wfdb

ROOT = Path('/tmp/sensable_public_datasets/stuba/extracted/wfdb_data')
record = ROOT / 'Subject_001' / 'data000001'
signals, fields = wfdb.rdsamp(str(record))
ann = wfdb.rdann(str(record), 'atr')
print('shape', signals.shape)
print('sig_name', fields['sig_name'])
print('fs', fields['fs'], 'units', fields['units'])
print('comments', fields['comments'])
print('ann_sample', ann.sample.tolist())
print('ann_symbol', ann.symbol)
print('ann_aux_note', ann.aux_note)
print('first_row', signals[0].tolist())
