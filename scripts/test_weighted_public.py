from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
import sys
sys.path.insert(0, '/home/ubuntu/SENS_ABLE_OPSI/ai_final/improvement')
from external_public_ppg_experiment import build_public_frame, build_sensable_frame, SHARED_FEATURES

public, _ = build_public_frame(Path('/tmp/sensable_public_datasets/stuba/extracted/wfdb_data'), Path('/tmp/sensable_public_datasets/stuba/qc_records.csv'))
sens = build_sensable_frame()
groups=sens['SubjectID']
for weight in [0.05,0.1,0.25,0.5,1.0,2.0]:
    pred=np.full(len(sens),np.nan)
    for tr,te in GroupKFold(5).split(sens,sens['GlukosaRef'],groups):
        train_s=pd.concat([public.assign(_w=weight),sens.iloc[tr].assign(_w=1.0)],ignore_index=True)
        model=RandomForestRegressor(n_estimators=200,max_depth=6,min_samples_leaf=2,random_state=42,n_jobs=1)
        model.fit(train_s[SHARED_FEATURES],train_s['GlukosaRef'],sample_weight=train_s['_w'])
        pred[te]=model.predict(sens.iloc[te][SHARED_FEATURES])
    print(weight, round(mean_absolute_error(sens['GlukosaRef'],pred),4), round(np.sqrt(mean_squared_error(sens['GlukosaRef'],pred)),4), round(r2_score(sens['GlukosaRef'],pred),4))
