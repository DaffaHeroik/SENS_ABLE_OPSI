"""Create research-ready plots from reports/model_comparison.json."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = ROOT / "reports" / "model_comparison.json"
PLOT_DIR = ROOT / "reports" / "figures"


def main() -> None:
    report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    y = np.array([item for item in next(model for model in report["models"] if model["model"] == "MeanBaseline")["predictions"]])
    references = None
    # Predictions are stored in original row order. Reconstruct references from
    # the processed data without changing the report schema.
    import pandas as pd
    frame = pd.read_csv(ROOT / "data" / "processed" / "sensable_validation.csv")
    references = frame[report["target"]["column"]].astype(float).to_numpy()

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    for model in report["models"]:
        name = model["model"]
        predictions = np.array(model["predictions"], dtype=float)
        errors = references - predictions

        fig, ax = plt.subplots(figsize=(7, 6), dpi=160)
        ax.scatter(references, predictions, s=38, alpha=0.85, color="#1769aa", edgecolor="white", linewidth=0.5)
        low = min(float(references.min()), float(predictions.min()))
        high = max(float(references.max()), float(predictions.max()))
        ax.plot([low, high], [low, high], linestyle="--", color="#b33a3a", linewidth=1.5, label="Prediksi ideal")
        ax.set_title(f"SENS-Able V0.1 — {name}")
        ax.set_xlabel("Glukosa referensi glucometer (mg/dL)")
        ax.set_ylabel("Prediksi model (mg/dL)")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(PLOT_DIR / f"actual_vs_predicted_{name.lower()}.png", bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=160)
        ax.axhline(0, color="#444444", linewidth=1)
        ax.bar(np.arange(len(errors)), errors, color=np.where(errors >= 0, "#278a5b", "#c44e52"), width=0.82)
        ax.set_title(f"Residual per sesi — {name}")
        ax.set_xlabel("Indeks sesi")
        ax.set_ylabel("Referensi − prediksi (mg/dL)")
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(PLOT_DIR / f"residuals_{name.lower()}.png", bbox_inches="tight")
        plt.close(fig)

    print(f"Wrote figures to {PLOT_DIR}")


if __name__ == "__main__":
    main()
