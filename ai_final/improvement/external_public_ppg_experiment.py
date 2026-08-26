"""Evaluate external public PPG data as an honest augmentation experiment.

This script does not alter the canonical SENS-Able dataset or model. It extracts
unit-robust signal summaries from the public STU PPG dataset, evaluates a fixed
model on public subjects, and tests whether adding public subjects improves a
shared-feature RF on held-out SENS-Able subjects. All SENS-Able folds are split
by SubjectID; public subjects are never used as SENS-Able test subjects.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import wfdb
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[2]
SENS_DATA = ROOT / "data" / "processed" / "sensable_validation.csv"
DEFAULT_REPORT = ROOT / "reports" / "external_public_ppg_experiment.json"
TARGET = "GlukosaRef"
MMOL_TO_MGDL = 18.0182

SHARED_FEATURES = [
    "Age", "Weight_kg", "Height_cm", "BMI", "IR_CV", "IR_Range_Rel",
    "RED_CV", "RED_Range_Rel", "IR_RED_Mean_Ratio", "HR_bpm",
]


def metric_dict(y_true, prediction):
    return {
        "mae_mg_dL": round(float(mean_absolute_error(y_true, prediction)), 4),
        "rmse_mg_dL": round(float(np.sqrt(mean_squared_error(y_true, prediction))), 4),
        "median_absolute_error_mg_dL": round(float(median_absolute_error(y_true, prediction)), 4),
        "r2": round(float(r2_score(y_true, prediction)), 4),
    }


def safe_ratio(numerator: float, denominator: float) -> float:
    if not np.isfinite(numerator) or not np.isfinite(denominator) or abs(denominator) < 1e-12:
        return float("nan")
    return float(numerator / abs(denominator))


def channel_summary(signal: np.ndarray) -> tuple[float, float, float, float]:
    values = np.asarray(signal, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return (float("nan"),) * 4
    return (float(np.mean(values)), float(np.std(values)), float(np.min(values)), float(np.max(values)))


def parse_glucose_mmol(annotation: wfdb.Annotation) -> float:
    for note in annotation.aux_note:
        match = re.search(r"GLY\s+([-+]?\d+(?:\.\d+)?)\s*mmol/L", note, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    raise ValueError("No GLY mmol/L annotation found")


def parse_comment(comments: list[str], key: str) -> str:
    prefix = key.lower() + ":"
    for comment in comments:
        if comment.lower().startswith(prefix):
            return comment.split(":", 1)[1].strip()
    return ""


def build_public_frame(public_root: Path, qc_records_path: Path) -> tuple[pd.DataFrame, dict]:
    qc = pd.read_csv(qc_records_path)
    qc["record_passes"] = qc["record_passes"].astype(str).str.lower().eq("true")
    qc["ir_both_usable"] = qc["ir_both_usable"].astype(str).str.lower().eq("true")
    qc_lookup = qc.set_index(["subject", "record"])
    rows = []
    total = 0
    parse_failures = 0
    quality_excluded = 0
    for subject_dir in sorted(public_root.glob("Subject_*")):
        for header in sorted(subject_dir.glob("*.hea")):
            total += 1
            record = header.with_suffix("")
            key = (subject_dir.name, record.name)
            if key not in qc_lookup.index or not bool(qc_lookup.loc[key, "record_passes"]):
                quality_excluded += 1
                continue
            try:
                signals, fields = wfdb.rdsamp(str(record))
                annotation = wfdb.rdann(str(record), "atr")
                glucose_mmol = parse_glucose_mmol(annotation)
                signal_map = {name: signals[:, i] for i, name in enumerate(fields["sig_name"])}
                stats = {name: channel_summary(signal_map.get(name, np.array([]))) for name in ["IR1", "IR2", "R1", "R2", "G1", "G2"]}
                ir_means = [stats[name][0] for name in ["IR1", "IR2"] if np.isfinite(stats[name][0])]
                red_means = [stats[name][0] for name in ["R1", "R2"] if np.isfinite(stats[name][0])]
                green_means = [stats[name][0] for name in ["G1", "G2"] if np.isfinite(stats[name][0])]
                ir_cv = [safe_ratio(stats[name][1], stats[name][0]) for name in ["IR1", "IR2"]]
                red_cv = [safe_ratio(stats[name][1], stats[name][0]) for name in ["R1", "R2"]]
                green_cv = [safe_ratio(stats[name][1], stats[name][0]) for name in ["G1", "G2"]]
                ir_range = [safe_ratio(stats[name][3] - stats[name][2], stats[name][0]) for name in ["IR1", "IR2"]]
                red_range = [safe_ratio(stats[name][3] - stats[name][2], stats[name][0]) for name in ["R1", "R2"]]
                age = float(parse_comment(fields["comments"], "age"))
                height = float(parse_comment(fields["comments"], "height"))
                weight = float(parse_comment(fields["comments"], "weight"))
                hr = float(qc_lookup.loc[key, "hr_median_bpm"])
                rows.append({
                    "SubjectID": f"public_{subject_dir.name}",
                    "source": "public_stuba_ppg",
                    "Age": age,
                    "Weight_kg": weight,
                    "Height_cm": height,
                    "BMI": weight / (height / 100.0) ** 2,
                    "IR_CV": float(np.nanmean(ir_cv)),
                    "IR_Range_Rel": float(np.nanmean(ir_range)),
                    "RED_CV": float(np.nanmean(red_cv)),
                    "RED_Range_Rel": float(np.nanmean(red_range)),
                    "IR_RED_Mean_Ratio": float(np.nanmean(ir_means) / np.nanmean(red_means)),
                    "HR_bpm": hr,
                    TARGET: glucose_mmol * MMOL_TO_MGDL,
                    "record": record.name,
                })
            except (OSError, ValueError, KeyError, IndexError, ZeroDivisionError):
                parse_failures += 1
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError("No usable public records were parsed")
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=SHARED_FEATURES + [TARGET]).reset_index(drop=True)
    stats = {
        "records_seen": total,
        "records_retained_after_qc_and_parse": int(len(frame)),
        "records_quality_excluded": quality_excluded,
        "records_parse_failed": parse_failures,
        "subjects_retained": int(frame["SubjectID"].nunique()),
        "glucose_min_mg_dL": round(float(frame[TARGET].min()), 4),
        "glucose_max_mg_dL": round(float(frame[TARGET].max()), 4),
    }
    return frame, stats


def build_sensable_frame() -> pd.DataFrame:
    frame = pd.read_csv(SENS_DATA)
    return pd.DataFrame({
        "SubjectID": frame["SubjectID"],
        "source": "sensable",
        "Age": frame["Usia"].astype(float),
        "Weight_kg": frame["Berat_kg"].astype(float),
        "Height_cm": frame["Tinggi_cm"].astype(float),
        "BMI": frame["BMI"].astype(float),
        "IR_CV": frame["IR_Std"].astype(float) / frame["IR_Mean"].abs().clip(lower=1e-12),
        "IR_Range_Rel": (frame["IR_Max"] - frame["IR_Min"]) / frame["IR_Mean"].abs().clip(lower=1e-12),
        "RED_CV": frame["RED_Std"].astype(float) / frame["RED_Mean"].abs().clip(lower=1e-12),
        "RED_Range_Rel": (frame["RED_Max"] - frame["RED_Min"]) / frame["RED_Mean"].abs().clip(lower=1e-12),
        "IR_RED_Mean_Ratio": frame["IR_Mean"].astype(float) / frame["RED_Mean"].abs().clip(lower=1e-12),
        "HR_bpm": frame["HR_est"].astype(float),
        TARGET: frame[TARGET].astype(float),
    }).replace([np.inf, -np.inf], np.nan)


def evaluate_fixed_rf(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> dict:
    estimator = RandomForestRegressor(
        n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42, n_jobs=1
    )
    estimator.fit(train[features], train[TARGET])
    return metric_dict(test[TARGET], estimator.predict(test[features]))


def evaluate_public_cv(public: pd.DataFrame) -> dict:
    groups = public["SubjectID"]
    splitter = GroupKFold(n_splits=min(5, int(groups.nunique())))
    predictions = np.full(len(public), np.nan)
    for train_idx, test_idx in splitter.split(public, public[TARGET], groups):
        predictions[test_idx] = RandomForestRegressor(
            n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42, n_jobs=1
        ).fit(public.iloc[train_idx][SHARED_FEATURES], public.iloc[train_idx][TARGET]).predict(public.iloc[test_idx][SHARED_FEATURES])
    return {"rows": int(len(public)), "subjects": int(groups.nunique()), "metrics": metric_dict(public[TARGET], predictions)}


def evaluate_weighted_public_augmentation(sensable: pd.DataFrame, public: pd.DataFrame) -> dict:
    groups = sensable["SubjectID"]
    splitter = GroupKFold(n_splits=min(5, int(groups.nunique())))
    weights = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
    outputs = {}
    for public_weight in weights:
        predictions = np.full(len(sensable), np.nan)
        for train_idx, test_idx in splitter.split(sensable, sensable[TARGET], groups):
            train_sens = sensable.iloc[train_idx].copy()
            train_sens["_sample_weight"] = 1.0
            public_train = public.copy()
            public_train["_sample_weight"] = public_weight
            mixed_train = pd.concat([public_train, train_sens], ignore_index=True)
            estimator = RandomForestRegressor(
                n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42, n_jobs=1
            )
            estimator.fit(
                mixed_train[SHARED_FEATURES], mixed_train[TARGET], sample_weight=mixed_train["_sample_weight"]
            )
            predictions[test_idx] = estimator.predict(sensable.iloc[test_idx][SHARED_FEATURES])
        outputs[f"public_weight_{public_weight:g}"] = metric_dict(sensable[TARGET], predictions)
    return outputs


def evaluate_sensable_holdout(sensable: pd.DataFrame, public: pd.DataFrame) -> dict:
    groups = sensable["SubjectID"]
    splitter = GroupKFold(n_splits=min(5, int(groups.nunique())))
    results = {"sensable_only_shared_features": [], "public_plus_sensable_shared_features": []}
    predictions = {key: np.full(len(sensable), np.nan) for key in results}
    for train_idx, test_idx in splitter.split(sensable, sensable[TARGET], groups):
        train_sens = sensable.iloc[train_idx]
        test_sens = sensable.iloc[test_idx]
        predictions["sensable_only_shared_features"][test_idx] = RandomForestRegressor(
            n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42, n_jobs=1
        ).fit(train_sens[SHARED_FEATURES], train_sens[TARGET]).predict(test_sens[SHARED_FEATURES])
        mixed_train = pd.concat([public, train_sens], ignore_index=True)
        predictions["public_plus_sensable_shared_features"][test_idx] = RandomForestRegressor(
            n_estimators=200, max_depth=6, min_samples_leaf=2, random_state=42, n_jobs=1
        ).fit(mixed_train[SHARED_FEATURES], mixed_train[TARGET]).predict(test_sens[SHARED_FEATURES])
    return {"folded_metrics": {key: metric_dict(sensable[TARGET], value) for key, value in predictions.items()}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-root", type=Path, required=True, help="Extracted wfdb_data directory")
    parser.add_argument("--qc-records", type=Path, required=True, help="qc_records.csv from Zenodo record")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    public, public_stats = build_public_frame(args.public_root, args.qc_records)
    sensable = build_sensable_frame()
    result = {
        "experiment": "external public PPG augmentation without changing canonical SENS-Able model",
        "source": {
            "title": "Photoplethysmography (PPG) Dataset for Non-Invasive Blood Glucose Monitoring",
            "doi": "10.5281/zenodo.21978226",
            "url": "https://zenodo.org/records/21978226",
            "license": "CC0",
            "downloaded_archive_sha256": "6dde49ce143d3cd05983f461dcc4f5f02548b20ebfe28aff49b4c17e14c3a82c",
            "target_conversion": "annotation GLY in mmol/L multiplied by 18.0182 to mg/dL; no SENS-Able label was changed",
        },
        "public_dataset": public_stats,
        "sensable_dataset": {"rows": int(len(sensable)), "subjects": int(sensable["SubjectID"].nunique())},
        "features": SHARED_FEATURES,
        "validation": {
            "public_only": "5-fold GroupKFold by public SubjectID",
            "sensable_holdout": "5-fold GroupKFold by SENS-Able SubjectID; public rows only enter training folds",
            "no_target_leakage": True,
            "no_synthetic_data": True,
            "canonical_model_unchanged": True,
        },
        "public_only": evaluate_public_cv(public),
        "sensable_holdout": evaluate_sensable_holdout(sensable, public),
        "weighted_public_augmentation": evaluate_weighted_public_augmentation(sensable, public),
        "interpretation": "External data is evaluated as an augmentation experiment only. It is not merged into the canonical processed dataset and is not used to claim clinical performance.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
