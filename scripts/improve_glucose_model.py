"""Run honest model-improvement experiments on SENS-Able V0.1 data.

Model selection happens inside an inner GroupKFold and final scores are
reported on an outer GroupKFold. No synthetic records are created and
GlukosaRef never appears in the feature matrix.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "configs" / "glucose_model_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "reports" / "model_improvement_experiment.json"
TARGET = "GlukosaRef"


def metric_row(y_true: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    return {
        "mae_mg_dL": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "median_absolute_error_mg_dL": round(float(median_absolute_error(y_true, prediction)), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def evaluate_nested(name, estimator, parameter_grid, X, y, groups, outer_splits, inner_splits):
    predictions = np.full(len(y), np.nan, dtype=float)
    folds = []
    for fold, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        group_train = groups.iloc[train_idx]
        inner = list(inner_splits(group_train, X_train, y_train))
        search = GridSearchCV(
            estimator=estimator,
            param_grid=parameter_grid,
            scoring="neg_mean_absolute_error",
            cv=inner,
            n_jobs=1,
            refit=True,
        )
        search.fit(X_train, y_train)
        fold_prediction = search.predict(X_test)
        predictions[test_idx] = fold_prediction
        metrics = metric_row(y_test, fold_prediction)
        metrics.update({
            "fold": fold,
            "test_rows": int(len(test_idx)),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
            "best_params": search.best_params_,
            "inner_best_mae_mg_dL": round(float(-search.best_score_), 4),
        })
        folds.append(metrics)
    return {
        "model": name,
        "overall": metric_row(y, predictions),
        "folds": folds,
        "predictions": [round(float(value), 4) for value in predictions],
    }


def evaluate_mean_baseline(y, groups, outer_splits):
    predictions = np.full(len(y), np.nan, dtype=float)
    folds = []
    for fold, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        fold_prediction = np.full(len(test_idx), float(y[train_idx].mean()))
        predictions[test_idx] = fold_prediction
        metrics = metric_row(y[test_idx], fold_prediction)
        metrics.update({
            "fold": fold,
            "test_rows": int(len(test_idx)),
            "test_subjects": int(groups.iloc[test_idx].nunique()),
        })
        folds.append(metrics)
    return {
        "model": "MeanBaseline",
        "overall": metric_row(y, predictions),
        "folds": folds,
        "predictions": [round(float(value), 4) for value in predictions],
    }


def main():
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    frame = pd.read_csv(DATA_FILE)
    features = list(config["features"])
    if TARGET in features or set(config["excluded_from_features"]) & set(features):
        raise AssertionError("Target, identifier, or provenance leakage in features")
    X = frame[features].apply(pd.to_numeric, errors="raise")
    y = frame[TARGET].astype(float).to_numpy()
    groups = frame["SubjectID"]
    outer = GroupKFold(n_splits=min(5, int(groups.nunique())))
    outer_splits = list(outer.split(X, y, groups))

    def make_inner(group_train, X_train, y_train):
        return GroupKFold(n_splits=min(4, int(group_train.nunique()))).split(X_train, y_train, group_train)

    rf = RandomForestRegressor(random_state=42, n_jobs=1)
    rf_grid = {
        "n_estimators": [200],
        "max_depth": [3, 5, 8, None],
        "min_samples_leaf": [1, 2, 3, 4],
        "max_features": [0.5, 1.0],
    }
    rf_select = Pipeline([
        ("select", SelectKBest(score_func=f_regression)),
        ("model", RandomForestRegressor(random_state=42, n_jobs=1)),
    ])
    rf_select_grid = {
        "select__k": [5, 8, 12, "all"],
        "model__n_estimators": [200],
        "model__max_depth": [3, 5, 8],
        "model__min_samples_leaf": [1, 2, 3],
        "model__max_features": [0.5, 1.0],
    }
    extra = ExtraTreesRegressor(random_state=42, n_jobs=1)
    extra_grid = {
        "n_estimators": [200],
        "max_depth": [3, 5, 8, None],
        "min_samples_leaf": [1, 2, 3, 4],
        "max_features": [0.5, 1.0],
    }

    results = [
        evaluate_mean_baseline(y, groups, outer_splits),
        evaluate_nested("TunedRandomForestRegressor", rf, rf_grid, X, y, groups, outer_splits, make_inner),
        evaluate_nested("TunedRandomForestWithFeatureSelection", rf_select, rf_select_grid, X, y, groups, outer_splits, make_inner),
        evaluate_nested("TunedExtraTreesRegressor", extra, extra_grid, X, y, groups, outer_splits, make_inner),
    ]
    best = min(results, key=lambda item: item["overall"]["mae_mg_dL"])
    report = {
        "experiment": "nested model improvement V0.1",
        "target": {"column": TARGET, "meaning": "glucometer reference in mg/dL", "used_as_feature": False},
        "dataset": {"rows": int(len(frame)), "unique_subjects": int(groups.nunique()), "features": features},
        "validation": {
            "outer": "5-fold GroupKFold by SubjectID",
            "inner": "4-fold GroupKFold by SubjectID inside each outer training fold",
            "selection_metric": "negative mean absolute error",
            "no_synthetic_data": True,
            "no_target_leakage": TARGET not in features,
        },
        "models": results,
        "best_exploratory_result": {
            "model": best["model"],
            "selection_rule": "lowest outer-test MAE in this exploratory comparison",
            "warning": "Do not treat this small-sample comparison as clinical validation or as a final deployment decision.",
        },
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
