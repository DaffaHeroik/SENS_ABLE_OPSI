"""Evaluate the physical-device AI model with subject-grouped cross-validation."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold, cross_val_predict

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "ai_final" / "config" / "model_contract_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
REPORT_FILE = ROOT / "ai_final" / "evaluation" / "evaluation_v0_1.json"
PREDICTIONS_FILE = ROOT / "ai_final" / "evaluation" / "predictions_v0_1.csv"
TARGET = "GlukosaRef"


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    features = list(contract["features"])
    frame = pd.read_csv(DATA_FILE)
    X = frame[features].apply(pd.to_numeric, errors="raise")
    y = frame[TARGET].astype(float)
    groups = frame["SubjectID"]
    params = contract["models"]["random_forest"]
    model = RandomForestRegressor(
        n_estimators=int(params["n_estimators"]),
        max_depth=int(params["max_depth"]),
        min_samples_leaf=int(params["min_samples_leaf"]),
        random_state=int(params["random_state"]),
        n_jobs=int(params["n_jobs"]),
    )
    cv = GroupKFold(n_splits=min(int(contract["validation"]["n_splits"]), int(groups.nunique())))
    predictions = cross_val_predict(model, X, y, cv=cv, groups=groups)
    prediction_frame = pd.DataFrame({
        "SubjectID": frame["SubjectID"],
        "reference_glucose_mg_dL": y,
        "predicted_glucose_mg_dL": np.round(predictions, 4),
    })
    prediction_frame["absolute_error_mg_dL"] = np.round((prediction_frame["reference_glucose_mg_dL"] - prediction_frame["predicted_glucose_mg_dL"]).abs(), 4)
    prediction_frame.to_csv(PREDICTIONS_FILE, index=False, float_format="%.4f")
    report = {
        "version": contract["version"],
        "model": "RandomForestRegressor",
        "target": {"column": TARGET, "meaning": "glucometer reference", "unit": "mg/dL", "used_as_feature": False},
        "dataset": {"rows": int(len(frame)), "subjects": int(groups.nunique()), "features": features},
        "validation": {"method": "5-fold GroupKFold by SubjectID", "no_synthetic_data": True, "no_target_leakage": TARGET not in features},
        "metrics": {
            "mae_mg_dL": round(float(mean_absolute_error(y, predictions)), 4),
            "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y, predictions))), 4),
            "median_absolute_error_mg_dL": round(float(median_absolute_error(y, predictions)), 4),
            "r2": round(float(r2_score(y, predictions)), 4),
        },
        "predictions_file": str(PREDICTIONS_FILE.relative_to(ROOT)),
        "warning": "Exploratory pilot result; not clinical validation or a medical device claim.",
    }
    REPORT_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {REPORT_FILE}")
    print(f"Wrote {PREDICTIONS_FILE}")


if __name__ == "__main__":
    main()
