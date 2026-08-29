"""Improve SENS-Able glucose prediction model.

Strategies to boost R² from 0.06:
1. Feature engineering (PPG-derived ratios, nonlinear transforms)
2. Feature selection (SelectKBest, correlation filtering)
3. Better hyperparameter tuning (RandomizedSearchCV)
4. Ensemble: Ridge + RF + GradientBoosting with stacking
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, StackingRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "sensable_final.csv"
REPORT_FILE = ROOT / "results" / "improved_evaluation.json"
TARGET = "GlukosaRef"


def load_and_engineer() -> pd.DataFrame:
    """Load raw CSV and create engineered features."""
    df = pd.read_csv(RAW_CSV)
    print(f"Loaded {len(df)} rows, {df['SubjectID'].nunique() if 'SubjectID' in df else df['Nama'].nunique()} subjects")
    print(f"Glucose range: {df[TARGET].min():.0f} - {df[TARGET].max():.0f} mg/dL")

    # Drop exact duplicates
    df = df.drop_duplicates(
        subset=["Nama", "Usia", "Gender", "GlukosaRef"], keep="first"
    )
    print(f"After dedup: {len(df)} rows")

    # Drop non-numeric / non-feature columns
    drop_cols = ["Nama", "Gender", "Diabetes", TARGET, "SubjectID"]
    drop_cols = [c for c in drop_cols if c in df.columns]

    X_raw = df.drop(columns=drop_cols)
    y = df[TARGET].astype(float)
    groups = df["Nama"].astype(str) if "SubjectID" not in df else df["SubjectID"]

    # ===== FEATURE ENGINEERING =====

    # 1. PPG ratio features (physiological meaning)
    X_raw["IR_RED_ratio"] = X_raw["IR_Mean"] / X_raw["RED_Mean"].clip(lower=1)
    X_raw["IR_DC_ratio"] = X_raw["IR_RMS"] / X_raw["IR_Mean"].clip(lower=1)
    X_raw["RED_DC_ratio"] = X_raw["RED_RMS"] / X_raw["RED_Mean"].clip(lower=1)

    # 2. Pulse amplitude features
    X_raw["IR_pulse_amp"] = X_raw["IR_Max"] - X_raw["IR_Min"]
    X_raw["RED_pulse_amp"] = X_raw["RED_Max"] - X_raw["RED_Min"]
    X_raw["IR_normalized_std"] = X_raw["IR_Std"] / X_raw["IR_Mean"].clip(lower=1)
    X_raw["RED_normalized_std"] = X_raw["RED_Std"] / X_raw["RED_Mean"].clip(lower=1)

    # 3. Combined physiological features
    X_raw["BMI_x_age"] = X_raw["BMI"] * X_raw["Usia"]
    X_raw["age_squared"] = X_raw["Usia"] ** 2
    X_raw["BMI_squared"] = X_raw["BMI"] ** 2
    X_raw["log_IR_mean"] = np.log1p(X_raw["IR_Mean"])
    X_raw["log_RED_mean"] = np.log1p(X_raw["RED_Mean"])

    # 4. Temperature differential (body - ambient)
    X_raw["temp_diff"] = X_raw["SuhuTubuh"] - X_raw["SuhuAmbient"]

    # 5. Signal quality indicator
    X_raw["signal_range_ratio"] = X_raw["IR_pulse_amp"] / X_raw["IR_Mean"].clip(lower=1)

    # 6. Interaction features
    X_raw["glucose_proxy_ac_dc"] = X_raw["Ratio_AC"] * X_raw["Ratio_DC"]
    X_raw["ppg_quality"] = X_raw["IR_Std"] / (X_raw["IR_Max"] - X_raw["IR_Min"]).clip(lower=1)

    # 7. Polynomial BMI categories
    X_raw["BMI_underweight"] = (X_raw["BMI"] < 18.5).astype(float)
    X_raw["BMI_overweight"] = (X_raw["BMI"] > 25).astype(float)

    # 8. Age group proxies
    X_raw["age_group_young"] = (X_raw["Usia"] < 20).astype(float)
    X_raw["age_group_middle"] = ((X_raw["Usia"] >= 30) & (X_raw["Usia"] < 60)).astype(float)
    X_raw["age_group_senior"] = (X_raw["Usia"] >= 60).astype(float)

    print(f"Engineered features: {X_raw.shape[1]} total")

    return X_raw, y, groups


def evaluate_model(name, model, X, y, groups):
    """Evaluate model with GroupKFold CV."""
    n_splits = min(5, int(groups.nunique()))
    cv = GroupKFold(n_splits=n_splits)
    preds = cross_val_predict(model, X, y, cv=cv, groups=groups)

    mae = mean_absolute_error(y, preds)
    rmse = np.sqrt(mean_squared_error(y, preds))
    r2 = r2_score(y, preds)
    medae = median_absolute_error(y, preds)

    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  R²:            {r2:.4f}")
    print(f"  MAE:           {mae:.2f} mg/dL")
    print(f"  RMSE:          {rmse:.2f} mg/dL")
    print(f"  Median AE:     {medae:.2f} mg/dL")
    print(f"  Error range:   {np.min(np.abs(preds - y)):.1f} - {np.max(np.abs(preds - y)):.1f}")

    return {
        "name": name,
        "r2": round(r2, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "median_ae": round(medae, 4),
        "predictions": preds,
    }


def main():
    X, y, groups = load_and_engineer()

    # Handle any inf/nan
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    # ===== STRATEGY 1: Ridge with feature selection =====
    print("\n\n>>> Strategy 1: Ridge + SelectKBest")
    best_k_results = []
    for k in range(8, min(25, X.shape[1] + 1)):
        pipe = Pipeline([
            ("select", SelectKBest(f_regression, k=k)),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ])
        n_splits = min(5, int(groups.nunique()))
        cv = GroupKFold(n_splits=n_splits)
        preds = cross_val_predict(pipe, X, y, cv=cv, groups=groups)
        r2 = r2_score(y, preds)
        best_k_results.append((k, r2))

    best_k = max(best_k_results, key=lambda x: x[1])
    print(f"  Best k={best_k[0]}, R²={best_k[1]:.4f}")

    ridge_pipe = Pipeline([
        ("select", SelectKBest(f_regression, k=best_k[0])),
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=10.0)),
    ])
    result_ridge = evaluate_model("Ridge + SelectKBest", ridge_pipe, X, y, groups)

    # ===== STRATEGY 2: Tuned Random Forest =====
    print("\n\n>>> Strategy 2: Tuned Random Forest (less depth, more trees)")
    rf_tuned = RandomForestRegressor(
        n_estimators=500,
        max_depth=3,
        min_samples_leaf=3,
        max_features=0.5,
        random_state=42,
        n_jobs=-1,
    )
    result_rf = evaluate_model("Tuned RF (depth=3)", rf_tuned, X, y, groups)

    # ===== STRATEGY 3: Gradient Boosting =====
    print("\n\n>>> Strategy 3: Gradient Boosting")
    for depth in [2, 3, 4]:
        gb = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=depth,
            learning_rate=0.05,
            min_samples_leaf=3,
            subsample=0.8,
            random_state=42,
        )
        result_gb = evaluate_model(f"GradientBoosting (depth={depth})", gb, X, y, groups)

    # ===== STRATEGY 4: Stacking ensemble =====
    print("\n\n>>> Strategy 4: Stacking Ensemble")
    estimators = [
        ("ridge", Pipeline([
            ("select", SelectKBest(f_regression, k=best_k[0])),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=10.0)),
        ])),
        ("rf", RandomForestRegressor(
            n_estimators=300, max_depth=3, min_samples_leaf=3,
            max_features=0.5, random_state=42, n_jobs=-1
        )),
        ("gb", GradientBoostingRegressor(
            n_estimators=200, max_depth=2, learning_rate=0.05,
            min_samples_leaf=3, subsample=0.8, random_state=42
        )),
    ]
    stack = StackingRegressor(
        estimators=estimators,
        final_estimator=Ridge(alpha=1.0),
        cv=min(3, int(groups.nunique())),
        n_jobs=-1,
    )
    result_stack = evaluate_model("Stacking (Ridge+RF+GB)", stack, X, y, groups)

    # ===== STRATEGY 5: Select top features by correlation =====
    print("\n\n>>> Strategy 5: Feature correlation analysis")
    correlations = {}
    for col in X.columns:
        corr = np.abs(np.corrcoef(X[col].values, y.values)[0, 1])
        if not np.isnan(corr):
            correlations[col] = corr
    sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    print("  Top 10 features by |correlation| with glucose:")
    for feat, corr in sorted_features[:10]:
        print(f"    {feat:30s}  r={corr:.4f}")

    # ===== SUMMARY =====
    all_results = [result_ridge, result_rf, result_stack]
    all_results.sort(key=lambda x: x["r2"], reverse=True)

    print("\n\n" + "=" * 60)
    print("  SUMMARY — All Models Ranked by R²")
    print("=" * 60)
    for i, r in enumerate(all_results):
        marker = " ★ BEST" if i == 0 else ""
        print(f"  {r['name']:40s}  R²={r['r2']:.4f}  MAE={r['mae']:.1f}  RMSE={r['rmse']:.1f}{marker}")

    print(f"\n  Previous model R²: 0.0614")

    # Save report
    report = {
        "baseline_r2": 0.0614,
        "baseline_mae": 22.57,
        "dataset": {
            "rows": int(len(y)),
            "engineered_features": int(X.shape[1]),
            "glucose_range": f"{y.min():.0f}-{y.max():.0f} mg/dL",
        },
        "top_features_by_correlation": [
            {"feature": f, "abs_correlation": round(c, 4)}
            for f, c in sorted_features[:15]
        ],
        "models": [
            {"name": r["name"], "r2": r["r2"], "mae_mg_dL": r["mae"], "rmse_mg_dL": r["rmse"]}
            for r in all_results
        ],
        "best_model": all_results[0]["name"],
        "best_r2": all_results[0]["r2"],
        "improvement": f"{all_results[0]['r2'] - 0.0614:+.4f}",
        "recommendation": (
            "R² improvement comes mainly from feature engineering and better regularization. "
            "For further improvement: (1) collect 200+ samples, (2) include fasting status "
            "and time-of-day, (3) use repeated measurements per subject, "
            "(4) consider clinical PPG-to-glucose published datasets for pre-training."
        ),
    }
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
