"""Search additional real-data candidates without target leakage.

All model selection happens inside inner GroupKFold splits. Engineered features
are deterministic transformations of sensor inputs only; no GlukosaRef value
is used to construct them.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "ai_final" / "config" / "model_contract_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "reports" / "robust_model_search.json"
TARGET = "GlukosaRef"


def metrics(y_true, prediction):
    return {
        "mae_mg_dL": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "median_absolute_error_mg_dL": round(float(median_absolute_error(y_true, prediction)), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    eps = 1e-9
    out["IR_Range"] = out["IR_Max"] - out["IR_Min"]
    out["RED_Range"] = out["RED_Max"] - out["RED_Min"]
    out["IR_CV"] = out["IR_Std"] / (out["IR_Mean"].abs() + eps)
    out["RED_CV"] = out["RED_Std"] / (out["RED_Mean"].abs() + eps)
    out["IR_RED_Mean_Ratio"] = out["IR_Mean"] / (out["RED_Mean"].abs() + eps)
    out["IR_RED_Std_Ratio"] = out["IR_Std"] / (out["RED_Std"].abs() + eps)
    return out


def evaluate_nested(name, estimator, parameter_grid, X, y, groups, outer_splits):
    predictions = np.full(len(y), np.nan, dtype=float)
    folds = []
    for fold, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        inner_groups = groups.iloc[train_idx]
        inner_cv = GroupKFold(n_splits=min(4, int(inner_groups.nunique())))
        search = GridSearchCV(
            estimator=estimator,
            param_grid=parameter_grid,
            scoring="neg_mean_absolute_error",
            cv=inner_cv.split(X.iloc[train_idx], y[train_idx], inner_groups),
            n_jobs=1,
            refit=True,
        )
        search.fit(X.iloc[train_idx], y[train_idx])
        fold_prediction = search.predict(X.iloc[test_idx])
        predictions[test_idx] = fold_prediction
        fold_metrics = metrics(y[test_idx], fold_prediction)
        fold_metrics.update({
            "fold": fold,
            "test_rows": int(len(test_idx)),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
            "best_params": search.best_params_,
            "inner_best_mae_mg_dL": round(float(-search.best_score_), 4),
        })
        folds.append(fold_metrics)
    return {"model": name, "overall": metrics(y, predictions), "folds": folds}


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    frame = pd.read_csv(DATA_FILE)
    base_features = list(contract["features"])
    engineered = add_engineered_features(frame)
    engineered_features = base_features + [
        "IR_Range", "RED_Range", "IR_CV", "RED_CV", "IR_RED_Mean_Ratio", "IR_RED_Std_Ratio"
    ]
    y = frame[TARGET].astype(float).to_numpy()
    groups = frame["SubjectID"]
    outer = GroupKFold(n_splits=min(5, int(groups.nunique())))
    outer_splits = list(outer.split(frame[base_features], y, groups))

    candidates = [
        (
            "TunedRandomForestEngineeredFeatures",
            RandomForestRegressor(random_state=42, n_jobs=1),
            {"n_estimators": [200], "max_depth": [3, 5, 8], "min_samples_leaf": [1, 2, 3], "max_features": [0.5, 1.0]},
            engineered[engineered_features],
        ),
        (
            "TunedGradientBoostingEngineeredFeatures",
            GradientBoostingRegressor(random_state=42),
            {"n_estimators": [50, 100], "learning_rate": [0.03, 0.05, 0.1], "max_depth": [1, 2], "min_samples_leaf": [2, 4]},
            engineered[engineered_features],
        ),
        (
            "TunedRidgeBaseFeatures",
            Pipeline([( "scale", StandardScaler()), ("model", Ridge())]),
            {"model__alpha": [0.1, 1.0, 10.0, 100.0]},
            frame[base_features],
        ),
    ]
    results = []
    for name, estimator, grid, X in candidates:
        results.append(evaluate_nested(name, estimator, grid, X, y, groups, outer_splits))
    best = min(results, key=lambda item: item["overall"]["mae_mg_dL"])
    report = {
        "experiment": "robust model search with deterministic sensor feature engineering",
        "target": {"column": TARGET, "used_as_feature": False},
        "dataset": {"rows": int(len(frame)), "unique_subjects": int(groups.nunique())},
        "validation": {"outer": "5-fold GroupKFold by SubjectID", "inner": "4-fold GroupKFold by SubjectID", "no_synthetic_data": True, "no_target_leakage": TARGET not in engineered_features},
        "engineered_features": [c for c in engineered_features if c not in base_features],
        "models": results,
        "best_exploratory_result": {"model": best["model"], "overall": best["overall"], "warning": "Exploratory only; do not promote without stable repeated validation and physical-device feasibility."},
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
