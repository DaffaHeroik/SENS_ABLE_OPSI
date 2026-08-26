"""Compare leakage-safe glucose regression models and save the V0.1 artifact.

This pipeline uses only real SENS-Able data. GlukosaRef is the glucometer
reference target and never an input feature. SubjectID is used only for
GroupKFold grouping.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "configs" / "glucose_model_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "reports" / "model_comparison.json"
MODEL_DIR = ROOT / "models"
TARGET = "GlukosaRef"


def load_config() -> dict:
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    if config["target"]["column"] != TARGET:
        raise ValueError("Config target must be GlukosaRef")
    return config


def load_data(config: dict) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.Series]:
    frame = pd.read_csv(DATA_FILE)
    required = {"SubjectID", TARGET, *config["features"]}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    feature_columns = config["features"]
    X = frame[feature_columns].apply(pd.to_numeric, errors="raise")
    if X.isna().any().any():
        raise ValueError("Model features contain missing values")
    y = frame[TARGET].astype(float).to_numpy()
    if np.any(~np.isfinite(y)) or np.any(y <= 0):
        raise ValueError("GlukosaRef must contain finite positive values")
    if TARGET in feature_columns or set(config["excluded_from_features"]) & set(feature_columns):
        raise AssertionError("Target, identifiers, or provenance flags leaked into features")
    return frame, X, y, frame["SubjectID"]


def metric_row(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae_mg_dL": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "median_absolute_error_mg_dL": round(float(median_absolute_error(y_true, prediction)), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def fold_indices(cv: GroupKFold, X: pd.DataFrame, y: np.ndarray, groups: pd.Series):
    return list(cv.split(X, y, groups))


def evaluate_estimator(name: str, estimator_factory, X: pd.DataFrame, y: np.ndarray, groups: pd.Series, folds) -> dict:
    predictions = np.full(len(y), np.nan, dtype=float)
    fold_metrics = []
    for fold, (train_idx, test_idx) in enumerate(folds, start=1):
        estimator = estimator_factory()
        estimator.fit(X.iloc[train_idx], y[train_idx])
        fold_prediction = estimator.predict(X.iloc[test_idx])
        predictions[test_idx] = fold_prediction
        metrics = metric_row(y[test_idx], fold_prediction)
        metrics.update({
            "fold": fold,
            "test_rows": int(len(test_idx)),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
        })
        fold_metrics.append(metrics)
    return {
        "model": name,
        "overall": metric_row(y, predictions),
        "folds": fold_metrics,
        "predictions": [round(float(value), 4) for value in predictions],
    }


def evaluate_mean_baseline(X: pd.DataFrame, y: np.ndarray, groups: pd.Series, folds) -> dict:
    predictions = np.full(len(y), np.nan, dtype=float)
    fold_metrics = []
    for fold, (train_idx, test_idx) in enumerate(folds, start=1):
        fold_prediction = np.full(len(test_idx), float(y[train_idx].mean()))
        predictions[test_idx] = fold_prediction
        metrics = metric_row(y[test_idx], fold_prediction)
        metrics.update({
            "fold": fold,
            "test_rows": int(len(test_idx)),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
        })
        fold_metrics.append(metrics)
    return {
        "model": "MeanBaseline",
        "overall": metric_row(y, predictions),
        "folds": fold_metrics,
        "predictions": [round(float(value), 4) for value in predictions],
    }


def main() -> None:
    config = load_config()
    frame, X, y, groups = load_data(config)
    n_splits = min(int(config["validation"]["n_splits"]), int(groups.nunique()))
    if n_splits < 2:
        raise ValueError("At least two unique subjects are required")
    cv = GroupKFold(n_splits=n_splits)
    folds = fold_indices(cv, X, y, groups)

    rf_params = config["models"]["random_forest"]
    results = [
        evaluate_mean_baseline(X, y, groups, folds),
        evaluate_estimator(
            "LinearRegression",
            lambda: Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]),
            X, y, groups, folds,
        ),
        evaluate_estimator(
            "RandomForestRegressor",
            lambda: RandomForestRegressor(
                n_estimators=int(rf_params["n_estimators"]),
                max_depth=int(rf_params["max_depth"]),
                min_samples_leaf=int(rf_params["min_samples_leaf"]),
                random_state=int(rf_params["random_state"]),
                n_jobs=int(rf_params["n_jobs"]),
            ),
            X, y, groups, folds,
        ),
    ]
    best = min(results, key=lambda item: item["overall"]["mae_mg_dL"])

    # Fit the selected exploratory model on all processed rows for reproducible
    # offline inspection. This artifact is not clinical or embedded-ready.
    selected_model = RandomForestRegressor(
        n_estimators=int(rf_params["n_estimators"]),
        max_depth=int(rf_params["max_depth"]),
        min_samples_leaf=int(rf_params["min_samples_leaf"]),
        random_state=int(rf_params["random_state"]),
        n_jobs=int(rf_params["n_jobs"]),
    )
    selected_model.fit(X, y)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / "glucose_model_v0_1.joblib"
    metadata_path = MODEL_DIR / "glucose_model_v0_1_metadata.json"
    joblib.dump(selected_model, model_path)
    metadata_path.write_text(json.dumps({
        "version": config["version"],
        "task": config["task"],
        "target": TARGET,
        "features": config["features"],
        "model": best["model"],
        "trained_rows": int(len(frame)),
        "trained_subjects": int(groups.nunique()),
        "warning": "Exploratory artifact only; not clinical validation and not directly executable on Arduino/ESP32.",
    }, indent=2) + "\n", encoding="utf-8")

    report = {
        "config": str(CONFIG_FILE.relative_to(ROOT)),
        "target": {
            "column": TARGET,
            "meaning": "glucometer reference in mg/dL",
            "used_as_feature": False,
        },
        "dataset": {
            "path": str(DATA_FILE.relative_to(ROOT)),
            "rows": int(len(frame)),
            "unique_subjects": int(groups.nunique()),
            "feature_columns": config["features"],
            "temperature_imputation_rows": {
                "body": int(frame["SuhuTubuh_Imputed"].sum()),
                "ambient": int(frame["SuhuAmbient_Imputed"].sum()),
            },
        },
        "validation": {
            "method": f"{n_splits}-fold GroupKFold by SubjectID",
            "no_synthetic_data": True,
            "no_target_leakage": TARGET not in config["features"],
        },
        "models": results,
        "selected_exploratory_model": {
            "model": best["model"],
            "selection_metric": "lowest overall MAE under the fixed comparison",
            "artifact": str(model_path.relative_to(ROOT)),
            "metadata": str(metadata_path.relative_to(ROOT)),
        },
        "interpretation": "Exploratory comparison only; dataset size is insufficient for clinical accuracy claims or deployment decisions.",
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")
    print(f"Wrote {model_path}")
    print(f"Wrote {metadata_path}")


if __name__ == "__main__":
    main()
