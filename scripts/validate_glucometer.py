"""Validate glucose estimation against the glucometer reference column.

GlukosaRef is the target/reference only. It is never included in the model
features, which prevents label leakage.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "configs" / "glucose_model_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "reports" / "glucometer_validation.json"
REFERENCE_COLUMN = "GlukosaRef"
IDENTIFIER_COLUMNS = {
    "SubjectID", "Nama", "Gender", REFERENCE_COLUMN, "Diabetes",
    "SuhuTubuh_Imputed", "SuhuAmbient_Imputed",
}


def load_data() -> pd.DataFrame:
    frame = pd.read_csv(DATA_FILE)
    required = {REFERENCE_COLUMN, "SubjectID"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if frame[REFERENCE_COLUMN].isna().any():
        raise ValueError("GlukosaRef contains missing values")
    if (frame[REFERENCE_COLUMN] <= 0).any():
        raise ValueError("GlukosaRef must contain positive glucometer values")
    return frame


def main() -> None:
    frame = load_data()
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    feature_columns = list(config["features"])
    missing_features = sorted(set(feature_columns) - set(frame.columns))
    if missing_features:
        raise ValueError(f"Missing configured features: {missing_features}")
    if REFERENCE_COLUMN in feature_columns or set(config["excluded_from_features"]) & set(feature_columns):
        raise AssertionError("Target, identifiers, or provenance flags leaked into features")
    X = frame[feature_columns].apply(pd.to_numeric, errors="raise")
    y = frame[REFERENCE_COLUMN].astype(float)
    groups = frame["SubjectID"]
    n_splits = min(5, int(groups.nunique()))
    if n_splits < 2:
        raise ValueError("At least two unique subjects are required")

    params = config["models"]["random_forest"]
    estimator = RandomForestRegressor(
        n_estimators=int(params["n_estimators"]),
        max_depth=int(params["max_depth"]),
        min_samples_leaf=int(params["min_samples_leaf"]),
        random_state=int(params["random_state"]),
        n_jobs=int(params["n_jobs"]),
    )
    cv = GroupKFold(n_splits=n_splits)
    predictions = cross_val_predict(estimator, X, y, cv=cv, groups=groups)
    mae = mean_absolute_error(y, predictions)
    rmse = float(np.sqrt(mean_squared_error(y, predictions)))
    r2 = r2_score(y, predictions)
    report = {
        "target": {
            "column": REFERENCE_COLUMN,
            "meaning": "original glucometer reference supplied by project owner",
            "unit": "mg/dL",
            "used_as_feature": False,
        },
        "dataset": {
            "path": str(DATA_FILE.relative_to(ROOT)),
            "rows": int(len(frame)),
            "unique_subjects": int(groups.nunique()),
            "feature_columns": feature_columns,
            "temperature_imputation_rows": {
                "body": int(frame.get("SuhuTubuh_Imputed", pd.Series(dtype=int)).sum()),
                "ambient": int(frame.get("SuhuAmbient_Imputed", pd.Series(dtype=int)).sum()),
            },
        },
        "evaluation": {
            "method": "5-fold GroupKFold by SubjectID (or fewer folds when needed)",
            "model": "RandomForestRegressor",
            "config": str(CONFIG_FILE.relative_to(ROOT)),
            "mae_mg_dL": round(float(mae), 4),
            "rmse_mg_dL": round(rmse, 4),
            "median_absolute_error_mg_dL": round(float(median_absolute_error(y, predictions)), 4),
            "r2": round(float(r2), 4),
            "warning": "Exploratory only: the cleaned dataset is small and is not sufficient to establish clinical accuracy.",
        },
        "predictions": [
            {
                "SubjectID": str(subject),
                "reference_glucose_mg_dL": float(reference),
                "predicted_glucose_mg_dL": round(float(predicted), 4),
                "absolute_error_mg_dL": round(abs(float(reference) - float(predicted)), 4),
            }
            for subject, reference, predicted in zip(frame["SubjectID"], y, predictions)
        ],
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
