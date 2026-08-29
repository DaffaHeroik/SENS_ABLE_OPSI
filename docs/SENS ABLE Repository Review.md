# SENS ABLE Repository Review

**Repository:** [`DaffaHeroik/SENS_ABLE_OPSI`](https://github.com/DaffaHeroik/SENS_ABLE_OPSI)  
**Review date:** 26 August 2026  
**Review scope:** Repository structure, documentation, Python syntax, reproducibility, dataset quality, privacy exposure, and ML-evaluation validity.  
**Change policy:** The repository was inspected only; no GitHub files or commits were modified.

## Executive Summary

The repository has a clear research concept and a small, understandable structure. The main `train.py` workflow is syntactically valid and runs successfully when its documented Python dependencies are installed. However, the project is **not ready for public release as a health-monitoring or diagnostic system**. The most urgent issue is privacy: the public repository contains identifiable names together with age, gender, glucose readings, diabetes labels, and raw sensor measurements. The reported validation accuracy is also materially misleading because the 33-row validation set contains only one positive case, while the model detects zero positive cases (`F1 = 0.0`, `TP = 0`).

## Repository Map

| Area | Current contents | Assessment |
|---|---|---|
| Documentation | `README.md`, `docs/planning.md`, `docs/chat_history.md`, `docs/proposal.pdf` | Good project context, but the documentation overstates readiness and does not sufficiently explain privacy or medical limitations. |
| ML scripts | `train.py`, `train_v1.py`, `train_v2.py` | Three historical workflows create ambiguity; only `train.py` matches the current `data/` layout. |
| Dataset | `data/sensable_final.csv` | 33 rows, 26 columns, 30 unique names, 32 negative and 1 positive label; contains direct identifiers and sensitive health data. |
| Generated output | `report.json` | Consistent with the current `train.py` result, but it records a weak evaluation that should not be summarized mainly as accuracy. |
| Deployment | No `.ino`, `model.tflite`, `model.h`, or ESP32 source is tracked | The ESP32/TinyML stage remains planned rather than implemented. |
| Project configuration | `.gitignore`; no `requirements.txt`, `pyproject.toml`, CI workflow, or test suite | Reproduction and automated quality checks are incomplete. |

The repository currently has four commits on `main`, is public, and has a clean working tree in the inspected clone. The latest commit updates the planning document rather than adding the embedded deployment implementation.

## Findings

### CRITICAL — Public exposure of identifiable health data

`data/sensable_final.csv` is committed to a **public** repository and includes `Nama`, `Usia`, `Gender`, `GlukosaRef`, `Diabetes`, and detailed sensor measurements. The dataset contains 33 rows and 30 unique names; several names occur more than once, and at least one name/age/BMI grouping has conflicting gender values. This is a privacy risk even if the data was collected for a school project. The CSV should not remain publicly accessible in its current form.

**Recommended action:** Immediately make the repository private or remove the dataset from public access. Replace names with random subject IDs, remove unnecessary quasi-identifiers, obtain and document consent for the intended publication scope, and remove the sensitive file from Git history—not only from the latest commit. If the repository has already been cloned, history rewriting cannot guarantee that old copies disappear, so treat the published data as exposed.

### CRITICAL — Validation result does not demonstrate diabetes detection

The current report shows 90.9% accuracy on 33 samples, but the confusion matrix is `[[30, 2], [1, 0]]`: **zero true positives**, one false negative, and `F1 = 0.0`. The 97% glucose-threshold baseline also detects zero positive cases. Because 32 of 33 labels are negative, a classifier can obtain high accuracy by mostly predicting “healthy.” The result therefore does not support the claim that the system reliably detects diabetes.

**Recommended action:** Do not headline the 90.9% or 97% accuracy. Report sensitivity/recall, specificity, precision, F1, balanced accuracy, and the confusion matrix, with an explicit limitation that the positive class has only one sample. Collect a sufficiently powered, ethically approved, clinically referenced dataset and use subject-level, leakage-free evaluation. Do not describe the model as a diagnostic device.

### CRITICAL — Measurement and scientific claims are ahead of the evidence

The README describes glucose measurement through MAX30102 PPG and lists diabetes-monitoring behavior, but the repository does not contain calibration data, reference-device comparisons, uncertainty analysis, an ESP32 implementation, or a medical-safety boundary. The planning document marks calibration, respondent testing, analysis, deployment, and final reporting as incomplete.

**Recommended action:** Reframe the current project as a research prototype. Complete sensor calibration against appropriate reference devices, document protocol and consent, analyze error and uncertainty, and add a prominent disclaimer that outputs are not medical advice or a diagnosis. Only make performance claims that are supported by completed experiments.

### WARNING — Cross-validation preprocessing leakage

In `train.py`, `StandardScaler` is fitted on the full PIMA dataset before the cross-validation folds are created. The held-out fold therefore influences the scaling parameters. The effect may be small, but it makes the reported cross-validation estimate technically optimistic. The model is also a random forest, for which standardization is not required.

**Recommended action:** Either remove scaling for the random forest or evaluate a `Pipeline` containing the scaler and estimator so preprocessing is fitted inside each fold. Keep all model-selection decisions inside the training folds.

### WARNING — No pinned dependency or reproducible environment

The README gives a one-line `pip install` command, but the repository has no `requirements.txt`, `pyproject.toml`, lock file, Python-version declaration, or test command. `train.py` also downloads the PIMA CSV directly from a mutable external URL at runtime, without a pinned revision, checksum, local copy, timeout, or clear offline fallback.

**Recommended action:** Add a minimal `requirements.txt` with tested versions, declare a supported Python version, record the data source and retrieval date, pin or vendor a verified dataset copy when licensing permits, and add a reproducible command such as `make train` or a documented virtual-environment workflow.

### WARNING — Historical scripts are not reproducible from the repository root

`train_v1.py` and `train_v2.py` expect `sensable_final.csv` in the repository root, while the tracked file is `data/sensable_final.csv`. Their usage text also refers to filenames that do not exist. `train_v2.py` describes TensorFlow Lite conversion but exports a text instruction sheet rather than a real TFLite model.

**Recommended action:** Mark v1 and v2 explicitly as archived, correct or remove their stale usage instructions, or make each script runnable from a documented command. Keep one canonical training entry point and separate experimental scripts from the supported workflow.

### WARNING — Documentation and artifact state are inconsistent

The README’s repository tree lists `model.pkl`, but the artifact is ignored by `.gitignore` and is not tracked. A fresh clone therefore cannot load or inspect the trained model without rerunning the training script and downloading the external dataset. The README also presents the model as if it were already an available repository artifact.

**Recommended action:** Either document `model.pkl` as a generated local artifact and remove it from the static repository tree, or publish a versioned artifact only after reviewing privacy, supply-chain, and compatibility implications. Add a model metadata file containing training data version, feature order, preprocessing, Python/library versions, and evaluation limitations.

### WARNING — No tests, CI, or automated data validation

The repository contains no unit tests, data-schema checks, lint configuration, or GitHub Actions workflow. The training script assumes required columns exist, assumes labels are binary integers, suppresses all warnings globally, and does not fail with a clear validation message when the dataset schema changes.

**Recommended action:** Add tests for CSV schema, label values, missing values, feature mapping, prediction shape, and report generation. Add a CI job that runs syntax checks, tests, and a small offline smoke test. Replace global warning suppression with targeted handling.

### INFO — Data provenance needs a formal, privacy-safe record

`docs/chat_history.md` describes manual deletion, imputation, and deduplication decisions, including average-value imputation for some temperature values. This is useful provenance, but it is informal and includes more personal context than should be needed in a public repository.

**Recommended action:** Create a privacy-safe data card describing collection protocol, inclusion/exclusion rules, missing-value handling, label definition, repeated-measurement policy, consent status, and known limitations. Store raw identifiable data outside the public repository.

## Verification Performed

| Check | Result |
|---|---|
| Repository discovery | Found `DaffaHeroik/SENS_ABLE_OPSI`. |
| Git state | `main` matches `origin/main`; working tree clean. |
| Python syntax | `python3 -m py_compile train.py train_v1.py train_v2.py` passed. |
| Main workflow | Ran successfully in an isolated copy after installing the documented dependencies. |
| Current output | Reproduced 75.1% PIMA CV accuracy, 0.691 CV F1, 90.9% SENS-Able accuracy, `F1 = 0.0`, and `TP = 0`. |
| Dataset audit | 33 rows, 26 columns, no missing values, 32/1 class split, 30 unique names, six duplicate-name rows, and one name/age/BMI gender conflict. |
| Basic secret scan | No obvious API-key, password, token, or private-key pattern found. This does not replace a full historical secret scan. |

## Prioritized Next Steps

1. **Protect the dataset now:** make the repository private or remove and anonymize the public dataset; rewrite Git history if the data must no longer be retrievable from commits.
2. **Correct the scientific framing:** replace accuracy-first claims with the full confusion matrix and class-imbalance limitation; label the system as a non-diagnostic research prototype.
3. **Finish the evidence chain:** perform reference-device calibration, document consent and protocol, and collect enough positive and negative cases for meaningful subject-level evaluation.
4. **Make training reproducible:** add dependency/version files, schema validation, a pinned data source, and an offline smoke test.
5. **Consolidate the codebase:** select `train.py` as the supported entry point and archive or repair v1/v2.
6. **Add deployment only after validation:** track the actual ESP32 sketch and TFLite/TFLite Micro artifact only after the model and sensor claims have been validated.

## Overall Status

**❌ Not production-ready and not safe for public release in its current form.** The code is a workable early research scaffold, but privacy protection and evaluation validity must be addressed before further public sharing or claims of health-monitoring accuracy.

## References

[1]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI "SENS ABLE GitHub repository"
[2]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/README.md "SENS ABLE README"
[3]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/train.py "SENS ABLE main training script"
[4]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/data/sensable_final.csv "SENS ABLE dataset"
[5]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/report.json "SENS ABLE training report"
[6]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/docs/planning.md "SENS ABLE project plan"
[7]: https://github.com/DaffaHeroik/SENS_ABLE_OPSI/blob/main/docs/chat_history.md "SENS ABLE data-processing history"
