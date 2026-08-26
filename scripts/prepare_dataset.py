"""Prepare the SENS-Able validation dataset from immutable raw inputs.

The script never edits files in data/raw. It writes an anonymized processed
copy, an exclusion log, a quality report, and a SHA-256 manifest.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

COLUMNS = [
    "Nama", "Usia", "Gender", "Berat_kg", "Tinggi_cm", "BMI", "Diabetes",
    "GlukosaRef", "TerakhirMakan_jam", "SuhuTubuh", "SuhuAmbient", "HR_est",
    "SpO2_est", "IR_Mean", "IR_Min", "IR_Max", "IR_Std", "IR_RMS",
    "RED_Mean", "RED_Min", "RED_Max", "RED_Std", "RED_RMS", "Ratio_AC",
    "Ratio_DC", "Samples",
]
NUMERIC_COLUMNS = [c for c in COLUMNS if c not in {"Nama", "Gender"}]


def read_raw_frames() -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    for path in sorted(RAW_DIR.iterdir()):
        if not path.is_file() or path.name.startswith("MANIFEST"):
            continue
        if path.suffix.lower() == ".xlsx":
            workbook = pd.ExcelFile(path)
            for sheet in workbook.sheet_names:
                frame = pd.read_excel(path, sheet_name=sheet)
                frame["_source"] = f"{path.name}::{sheet}"
                frames.append(frame)
        else:
            frame = pd.read_csv(path)
            frame["_source"] = path.name
            frames.append(frame)
    if not frames:
        raise FileNotFoundError("No CSV/XLSX files found in data/raw")
    return frames


def normalize(frames: list[pd.DataFrame]) -> pd.DataFrame:
    normalized: list[pd.DataFrame] = []
    for frame in frames:
        missing = sorted(set(COLUMNS) - set(frame.columns))
        extra = sorted(set(frame.columns) - set(COLUMNS) - {"_source"})
        if missing or extra:
            raise ValueError(f"Schema mismatch in {frame['_source'].iloc[0]}: missing={missing}, extra={extra}")
        item = frame[COLUMNS + ["_source"]].copy()
        item["Nama"] = item["Nama"].astype("string").str.strip()
        item["Gender"] = item["Gender"].astype("string").str.strip().str.upper()
        for column in NUMERIC_COLUMNS:
            item[column] = pd.to_numeric(item[column], errors="coerce")
        normalized.append(item)
    combined = pd.concat(normalized, ignore_index=True)
    combined["_row_key"] = (
        combined[COLUMNS]
        .assign(Nama=lambda x: x["Nama"].str.casefold())
        .astype("string")
        .fillna("<NA>")
        .agg("|".join, axis=1)
    )
    return combined


def classify_row(row: pd.Series) -> str:
    if row[COLUMNS].isna().any():
        return "missing_or_non_numeric_required_value"
    if row["GlukosaRef"] <= 0:
        return "invalid_glucose_reference"
    if row["Diabetes"] not in {0, 1}:
        return "invalid_diabetes_label"
    if row["SuhuTubuh"] <= 0:
        return "invalid_temperature_zero_or_negative"
    if row["HR_est"] <= 0:
        return "invalid_heart_rate"
    if row["SpO2_est"] < 70 or row["SpO2_est"] > 100:
        return "invalid_spo2_range"
    if row["IR_Mean"] < 10000 or row["RED_Mean"] < 10000:
        return "low_optical_signal_capture"
    if row["IR_Min"] > row["IR_Max"] or row["RED_Min"] > row["RED_Max"]:
        return "invalid_signal_range"
    return ""


def make_subject_id(name: str, age: float, gender: str) -> str:
    basis = f"{name.casefold().strip()}|{int(age)}|{gender.upper()}".encode("utf-8")
    return "SUB-" + hashlib.sha256(basis).hexdigest()[:10].upper()


def main() -> None:
    frames = read_raw_frames()
    combined = normalize(frames)
    unique = combined.drop_duplicates("_row_key", keep="first").copy()
    source_counts = combined.groupby("_row_key")["_source"].nunique().rename("source_file_count")
    unique = unique.join(source_counts, on="_row_key")
    unique["exclude_reason"] = unique.apply(classify_row, axis=1)

    excluded = unique[unique["exclude_reason"] != ""].copy()
    clean = unique[unique["exclude_reason"] == ""].copy()

    # Keep raw names out of the processed public-facing validation file.
    clean["SubjectID"] = [
        make_subject_id(name, age, gender)
        for name, age, gender in zip(clean["Nama"], clean["Usia"], clean["Gender"])
    ]
    clean = clean.drop(columns=["Nama", "_source", "_row_key", "exclude_reason", "source_file_count"])
    clean = clean[["SubjectID"] + COLUMNS[1:]]
    clean = clean.sort_values(["SubjectID", "GlukosaRef", "Samples"], kind="stable").reset_index(drop=True)

    excluded_out = excluded.drop(columns=["_row_key"])
    excluded_out = excluded_out.sort_values(["exclude_reason", "Nama"], kind="stable")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_path = PROCESSED_DIR / "sensable_validation.csv"
    excluded_path = PROCESSED_DIR / "excluded_records.csv"
    report_path = PROCESSED_DIR / "quality_report.json"
    clean.to_csv(clean_path, index=False, float_format="%.8g")
    excluded_out.to_csv(excluded_path, index=False, float_format="%.8g")

    report = {
        "raw_file_count": len(frames),
        "combined_rows": int(len(combined)),
        "normalized_unique_rows": int(len(unique)),
        "duplicate_rows_removed": int(len(combined) - len(unique)),
        "processed_rows": int(len(clean)),
        "excluded_rows": int(len(excluded)),
        "excluded_by_reason": {str(k): int(v) for k, v in excluded["exclude_reason"].value_counts().items()},
        "processed_subjects": int(clean["SubjectID"].nunique()),
        "processed_glucose_reference": {
            "column": "GlukosaRef",
            "meaning": "glucometer reference value in mg/dL, supplied by project owner",
            "min_mg_dL": float(clean["GlukosaRef"].min()),
            "max_mg_dL": float(clean["GlukosaRef"].max()),
        },
        "class_counts_preserved_for_reference": {str(k): int(v) for k, v in clean["Diabetes"].value_counts().sort_index().items()},
        "cleaning_rules": [
            "Trim text and parse numeric fields; fail on schema mismatch.",
            "Collapse exact duplicate records after numeric normalization.",
            "Exclude missing/non-numeric required values and invalid labels.",
            "Exclude zero/negative temperature, invalid heart rate/SpO2, invalid signal ranges, and optical captures with IR_Mean or RED_Mean below 10000.",
            "Do not impute sensor failures and do not change GlukosaRef values.",
            "Replace names with stable pseudonymous SubjectID in the processed file.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    manifest_lines = []
    for path in sorted(RAW_DIR.iterdir()):
        if path.is_file() and not path.name.startswith("MANIFEST"):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_lines.append(f"{digest}  {path.name}")
    (RAW_DIR / "MANIFEST.sha256").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"Wrote {clean_path}")
    print(f"Wrote {excluded_path}")
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
