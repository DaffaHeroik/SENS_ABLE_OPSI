import json
from collections import Counter
from pathlib import Path

report=json.loads(Path('/home/ubuntu/SENS_ABLE_OPSI/reports/model_improvement_experiment.json').read_text())
for model in report['models']:
    print('\nMODEL', model['model'])
    print('overall', model['overall'])
    if model['folds'] and 'best_params' in model['folds'][0]:
        for fold in model['folds']:
            print('fold', fold['fold'], 'mae', fold['mae_mg_dL'], 'params', fold['best_params'])
        if any('select__k' in fold['best_params'] for fold in model['folds']):
            print('selected_k_counts', Counter(str(fold['best_params']['select__k']) for fold in model['folds']))
