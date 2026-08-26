"""Measure the contribution of feature groups using fixed V0.1 RF settings."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "configs" / "glucose_model_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "reports" / "feature_ablation_experiment.json"
TARGET = "GlukosaRef"


def metrics(y_true, prediction):
    return {
        "mae_mg_dL": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "median_absolute_error_mg_dL": round(float(median_absolute_error(y_true, prediction)), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def evaluate(name, feature_columns, frame, y, groups, folds, params):
    X = frame[feature_columns].apply(pd.to_numeric, errors="raise")
    prediction = np.full(len(y), np.nan, dtype=float)
    fold_metrics = []
    for fold, (train_idx, test_idx) in enumerate(folds, start=1):
        model = RandomForestRegressor(
            n_estimators=int(params["n_estimators"]),
            max_depth=int(params["max_depth"]),
            min_samples_leaf=int(params["min_samples_leaf"]),
            random_state=int(params["random_state"]),
            n_jobs=1,
        )
        model.fit(X.iloc[train_idx], y[train_idx])
        fold_prediction = model.predict(X.iloc[test_idx])
        prediction[test_idx] = fold_prediction
        result = metrics(y[test_idx], fold_prediction)
        result["fold"] = fold
        fold_metrics.append(result)
    return {
        "feature_set": name,
        "features": feature_columns,
        "overall": metrics(y, prediction),
        "folds": fold_metrics,
    }


def main():
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    frame = pd.read_csv(DATA_FILE)
    features = list(config["features"])
    y = frame[TARGET].astype(float).to_numpy()
    groups = frame["SubjectID"]
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    folds = list(cv.split(frame[features], y, groups))
    ppg = [c for c in features if c.startswith(("IR_", "RED_", "Ratio_")) or c == "Samples"]
    physiology = [c for c in features if c in {"SuhuTubuh", "SuhuAmbient", "HR_est", "SpO2_est"}]
    context = [c for c in features if c in {"Usia", "Berat_kg", "Tinggi_cm", "BMI", "TerakhirMakan_jam"}]
    groups_to_test = {
        "all_features": features,
        "ppg_only": ppg,
        "ppg_temperature_vitals": ppg + physiology,
        "context_only": context,
    }
    params = config["models"]["random_forest"]
    results = [evaluate(name, cols, frame, y, groups, folds, params) for name, cols in groups_to_test.items()]
    best = min(results, key=lambda item: item["overall"]["mae_mg_dL"])
    report = {
        "experiment": "fixed Random Forest feature ablation V0.1",
        "target": {"column": TARGET, "used_as_feature": False},
        "dataset": {"rows": int(len(frame)), "unique_subjects": int(groups.nunique())},
        "validation": {"method": "5-fold GroupKFold by SubjectID", "no_synthetic_data": True, "no_target_leakage": TARGET not in features},
        "models": results,
        "best_exploratory_feature_set": best["feature_set"],
        "warning": "Feature ablation is exploratory on a small dataset; do not interpret the best feature set as clinically validated.",
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
