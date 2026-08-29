"""Train the frozen SENS-Able V0.1 model for offline inspection.

Evaluation must be performed separately with GroupKFold before this artifact
is used. This script never uses GlukosaRef as an input feature.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "ai_final" / "config" / "model_contract_v0_1.json"
DATA_FILE = ROOT / "data" / "processed" / "sensable_validation.csv"
ARTIFACT = ROOT / "ai_final" / "artifacts" / "glucose_model_v0_1.joblib"
METADATA = ROOT / "ai_final" / "artifacts" / "glucose_model_v0_1_metadata.json"
TARGET = "GlukosaRef"


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    features = list(contract["features"])
    frame = pd.read_csv(DATA_FILE)
    required = {TARGET, "SubjectID", *features}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if TARGET in features:
        raise AssertionError("GlukosaRef must not be a model feature")
    X = frame[features].apply(pd.to_numeric, errors="raise")
    y = frame[TARGET].astype(float).to_numpy()
    if X.isna().any().any() or np.any(~np.isfinite(y)):
        raise ValueError("Training data contains missing or non-finite values")
    params = contract["models"]["random_forest"]
    model = RandomForestRegressor(
        n_estimators=int(params["n_estimators"]),
        max_depth=int(params["max_depth"]),
        min_samples_leaf=int(params["min_samples_leaf"]),
        random_state=int(params["random_state"]),
        n_jobs=int(params["n_jobs"]),
    )
    model.fit(X, y)
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACT)
    METADATA.write_text(json.dumps({
        "version": contract["version"],
        "task": "glucose_regression",
        "target": TARGET,
        "features": features,
        "model": "RandomForestRegressor",
        "parameters": params,
        "training_rows": int(len(frame)),
        "training_subjects": int(frame["SubjectID"].nunique()),
        "evaluation_report": "reports/model_comparison.json",
        "warning": "Full-data artifact for offline inspection only; not clinical validation and not directly executable on Arduino.",
    }, indent=2) + "\n", encoding="utf-8")
    print(f"trained_rows={len(frame)}")
    print(f"trained_subjects={frame['SubjectID'].nunique()}")
    print(f"artifact={ARTIFACT}")
    print(f"metadata={METADATA}")


if __name__ == "__main__":
    main()
