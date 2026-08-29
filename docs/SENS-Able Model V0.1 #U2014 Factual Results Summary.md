# SENS-Able Model V0.1 — Factual Results Summary

**Dataset:** `data/processed/sensable_validation.csv`
**Task:** Glucose regression
**Target:** `GlukosaRef`, glucometer reference in mg/dL
**Subjects:** 32 `SubjectID`
**Sessions:** 40
**Validation:** 5-fold `GroupKFold` by `SubjectID`
**Synthetic data:** Not used
**Target leakage:** Not detected

## Dataset Quality

The raw sources contained 237 rows. After numeric normalization and duplicate collapse, 46 unique sessions remained. Six sessions were excluded because `IR_Mean` or `RED_Mean` was below the optical signal quality threshold. Seven zero body-temperature readings and six zero ambient-temperature readings were retained and imputed using the corresponding positive-observation mean. The imputation flags are stored in `SuhuTubuh_Imputed` and `SuhuAmbient_Imputed` and are excluded from model features. `GlukosaRef` values were not changed.

## Model Comparison

| Model | MAE (mg/dL) | RMSE (mg/dL) | Median absolute error (mg/dL) | R² |
|---|---:|---:|---:|---:|
| MeanBaseline | 24.2937 | 29.0975 | 23.9062 | -0.0856 |
| LinearRegression | 57.8532 | 71.9372 | 47.5700 | -5.6353 |
| RandomForestRegressor | **22.5716** | **27.0552** | **20.5580** | **0.0614** |

Random Forest has the lowest MAE in this fixed comparison and is therefore stored as the V0.1 exploratory artifact. The model was fitted on all 40 processed sessions only for reproducible offline inspection after cross-validated comparison. This fit must not be described as an independent test result.

## Interpretation

The Random Forest result is only slightly better than the mean baseline. The small positive R² does not establish clinical accuracy. The original proposal target of MAE below 15 mg/dL was not reached in this experiment. The dataset should therefore be presented as a pilot/early evaluation, not as a diagnostic validation or glucometer replacement.

## Reproduction

```bash
python3 scripts/prepare_dataset.py
python3 scripts/compare_glucose_models.py
python3 scripts/plot_model_results.py
python3 scripts/validate_glucometer.py
python3 -m unittest discover -s tests -v
```

The exact file hashes for this V0.1 state are stored in `reports/MANIFEST_v0_1.sha256`.
