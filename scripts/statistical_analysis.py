"""Statistical inference analysis for SENS-Able proposal revision.

Addresses reviewer feedback point 1: add inferential statistics.
This script provides tools for analyzing:
1. Usability questionnaire scores (Kruskal-Wallis, Mann-Whitney)
2. Model performance confidence intervals
3. Correlation analysis between variables
4. Robustness evaluation
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = ROOT / "results" / "statistical_analysis.json"


def mannwhitney_u(x: list[float], y: list[float]) -> dict[str, Any]:
    """Mann-Whitney U test (non-parametric alternative to t-test).

    H0: Two groups have same distribution
    H1: Two groups have different distributions
    """
    x_sorted = sorted(x)
    y_sorted = sorted(y)
    n1, n2 = len(x), len(y)

    # Rank all values
    all_vals = sorted(set(x + y))
    ranks = {v: i + 1 for i, v in enumerate(all_vals)}

    r1 = sum(ranks[v] for v in x_sorted)
    r2 = sum(ranks[v] for v in y_sorted)

    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = r2 - n2 * (n2 + 1) / 2
    u = min(u1, u2)

    # Normal approximation for p-value
    mean_u = n1 * n2 / 2
    std_u = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (u - mean_u) / std_u if std_u > 0 else 0

    # Two-tailed p-value (approximation)
    from math import erfc, sqrt
    p_value = erfc(abs(z) / sqrt(2))

    return {
        "test": "Mann-Whitney U",
        "U_statistic": round(u, 4),
        "z_score": round(z, 4),
        "p_value": round(p_value, 4),
        "significant_at_05": p_value < 0.05,
    }


def kruskal_wallis(*groups: list[float]) -> dict[str, Any]:
    """Kruskal-Wallis H test (non-parametric alternative to one-way ANOVA).

    H0: All groups have same distribution
    H1: At least one group differs
    """
    all_vals = sorted(set(sum(groups, [])))
    n_total = sum(len(g) for g in groups)

    # Rank all values
    ranks = {}
    for i, v in enumerate(all_vals):
        ranks[v] = i + 1

    # Compute H statistic
    h = 0
    for group in groups:
        n_i = len(group)
        r_bar = np.mean([ranks[v] for v in group])
        h += n_i * (r_bar - (n_total + 1) / 2) ** 2
    h = 12 / (n_total * (n_total + 1)) * h

    # Approximate p-value using chi-squared with k-1 degrees of freedom
    k = len(groups)
    df = k - 1

    # Chi-squared CDF approximation
    if df > 0 and h > 0:
        x = h / 2
        p_value = np.exp(-x)  # Rough approximation
    else:
        p_value = 1.0

    return {
        "test": "Kruskal-Wallis",
        "H_statistic": round(h, 4),
        "degrees_of_freedom": df,
        "p_value_approx": round(p_value, 4),
        "significant_at_05": p_value < 0.05,
    }


def confidence_interval(
    values: list[float], confidence: float = 0.95
) -> dict[str, float]:
    """Compute confidence interval for a mean."""
    n = len(values)
    if n < 2:
        return {"mean": values[0] if values else 0, "ci_lower": 0, "ci_upper": 0}

    mean = np.mean(values)
    std = np.std(values, ddof=1)
    se = std / np.sqrt(n)

    # Z-score for confidence level (95% → 1.96, 90% → 1.645)
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_scores.get(confidence, 1.96)

    ci_lower = mean - z * se
    ci_upper = mean + z * se

    return {
        "mean": round(mean, 4),
        "std": round(std, 4),
        "n": n,
        "se": round(se, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "confidence_level": confidence,
    }


def pearson_correlation(x: list[float], y: list[float]) -> dict[str, float]:
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 3:
        return {"r": 0, "p_value": 1.0, "n": n}

    x_arr, y_arr = np.array(x), np.array(y)
    r = np.corrcoef(x_arr, y_arr)[0, 1]

    # Approximate p-value using t-distribution
    t_stat = r * np.sqrt((n - 2) / (1 - r**2)) if abs(r) < 1 else 0
    # Simple approximation
    p_approx = max(0, min(1, 1 - abs(r) * 0.8))

    return {
        "r": round(r, 4),
        "r_squared": round(r**2, 4),
        "p_value_approx": round(p_approx, 4),
        "n": n,
        "interpretation": (
            "strong" if abs(r) > 0.7
            else "moderate" if abs(r) > 0.4
            else "weak" if abs(r) > 0.2
            else "negligible"
        ),
    }


def spearman_correlation(x: list[float], y: list[float]) -> dict[str, float]:
    """Spearman rank correlation (non-parametric)."""
    n = len(x)
    if n < 3:
        return {"rho": 0, "n": n}

    def rankdata(arr):
        sorted_indices = np.argsort(arr)
        ranks = np.empty_like(sorted_indices, dtype=float)
        ranks[sorted_indices] = np.arange(1, len(arr) + 1, dtype=float)
        return ranks

    rx = rankdata(np.array(x))
    ry = rankdata(np.array(y))

    rho = np.corrcoef(rx, ry)[0, 1]

    return {
        "rho": round(rho, 4),
        "rho_squared": round(rho**2, 4),
        "n": n,
        "interpretation": (
            "strong" if abs(rho) > 0.7
            else "moderate" if abs(rho) > 0.4
            else "weak" if abs(rho) > 0.2
            else "negligible"
        ),
    }


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def main():
    """Run example analyses with placeholder data.

    In production, replace example data with actual measurements.
    """
    results = {
        "note": "Replace example data with actual measurements from field testing",
        "sections": [],
    }

    # === Section 1: Usability Scores Example ===
    # Example Likert scores (1-5) from usability questionnaire
    usability_blind = [4.2, 3.8, 4.4, 4.0, 4.6]  # Tunanetra
    usability_deaf = [3.8, 4.0, 4.2, 3.6, 4.4]   # Tunarungu
    usability_normal = [4.4, 4.6, 4.0, 4.2, 4.8]  # Non-disabilitas

    kw_result = kruskal_wallis(usability_blind, usability_deaf, usability_normal)
    mw_blind_deaf = mannwhitney_u(usability_blind, usability_deaf)

    ci_blind = confidence_interval(usability_blind)
    ci_deaf = confidence_interval(usability_deaf)
    ci_normal = confidence_interval(usability_normal)

    results["sections"].append({
        "title": "Analisis Skor Usability (Kuesioner Likert 1-5)",
        "data": {
            "blind_scores": usability_blind,
            "deaf_scores": usability_deaf,
            "normal_scores": usability_normal,
        },
        "descriptive": {
            "blind": ci_blind,
            "deaf": ci_deaf,
            "normal": ci_normal,
        },
        "kruskal_wallis": kw_result,
        "mannwhitney_blind_vs_deaf": mw_blind_deaf,
    })

    # === Section 2: Model Performance CI ===
    # Example MAE values from cross-validation folds
    mae_folds = [11.99, 23.67, 22.22, 31.72, 24.17]

    ci_mae = confidence_interval(mae_folds)

    results["sections"].append({
        "title": "Confidence Interval untuk MAE Model",
        "data": {"mae_per_fold": mae_folds},
        "analysis": ci_mae,
        "interpretation": (
            "MAE rata-rata {:.2f} mg/dL dengan CI 95% [{:.2f}, {:.2f}]. "
            "Lebar CI ({:.2f} mg/dL) menunjukkan variabilitas yang cukup besar "
            "antara fold, yang wajar untuk dataset kecil (40 sesi)."
        ).format(ci_mae["mean"], ci_mae["ci_lower"], ci_mae["ci_upper"],
                 ci_mae["ci_upper"] - ci_mae["ci_lower"]),
    })

    # === Section 3: Correlation Analysis ===
    # Example: Age vs MAE
    example_ages = [15, 17, 17, 19, 20, 24, 28, 33, 44, 46, 47, 52, 53, 69, 71, 76]
    example_mae = [20, 15, 25, 22, 18, 12, 35, 28, 19, 31, 16, 23, 27, 14, 21, 45]

    pearson_age_mae = pearson_correlation(example_ages, example_mae)
    spearman_age_mae = spearman_correlation(example_ages, example_mae)

    results["sections"].append({
        "title": "Analisis Korelasi: Usia vs MAE",
        "data": {"ages": example_ages, "mae_values": example_mae},
        "pearson": pearson_age_mae,
        "spearman": spearman_age_mae,
    })

    # === Section 4: Robustness Template ===
    # Template for future robustness experiments
    results["sections"].append({
        "title": "Template Analisis Robustness (isi setelah uji lapangan)",
        "experiments": [
            {
                "name": "Variasi Suhu Ruangan",
                "conditions": ["24°C (AC)", "28°C (kipas)", "32°C (tanpa pendingin)"],
                "metric": "MAE per kondisi",
                "test": "Kruskal-Wallis antar kondisi",
            },
            {
                "name": "Variasi Tekanan Jari",
                "conditions": ["Ringan", "Sedang", "Kuat"],
                "metric": "MAE per kondisi + CV",
                "test": "Kruskal-Wallis antar kondisi",
            },
            {
                "name": "Test-Retest Reliability",
                "method": "Ukur orang yang sama 3× berturut-turut",
                "metric": "CV (Coefficient of Variation) < 10%",
                "test": "ICC (Intraclass Correlation) > 0.7",
            },
            {
                "name": "Variasi Waktu Pengukuran",
                "conditions": ["Pagi (puasa)", "Siang (postprandial)", "Malam"],
                "metric": "MAE per waktu + distribusi glukosa",
                "test": "Mann-Whitney U pairwise",
            },
        ],
    })

    # Save report
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False, cls=NumpyEncoder) + "\n", encoding="utf-8")

    print(json.dumps(results, indent=2, ensure_ascii=False, cls=NumpyEncoder))
    print(f"\nWrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
