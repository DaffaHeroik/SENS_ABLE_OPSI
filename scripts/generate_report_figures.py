"""Generate all charts and figures for the SENS-Able OPSI report.

Run: python3 scripts/generate_report_figures.py
Output: results/figures/ (PNG files for the report)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "sensable_final.csv"
FIG_DIR = ROOT / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Use a clean style
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.facecolor": "white",
    "axes.facecolor": "#fafafa",
    "axes.grid": True,
    "grid.alpha": 0.3,
})

# ===== Load data =====
df = pd.read_csv(RAW_CSV)

# ===== Figure 1: Distribusi Glukosa =====
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Histogram
colors_hist = ["#2ecc71", "#f39c12", "#e74c3c"]
glucose = df["GlukosaRef"]
bins = [70, 100, 126, 200]
labels_hist = ["Normal (<100)", "Pre-DM (100-125)", "DM (≥126)"]
counts = [((glucose >= 70) & (glucose < 100)).sum(),
          ((glucose >= 100) & (glucose < 126)).sum(),
          (glucose >= 126).sum()]

bars = axes[0].bar(labels_hist, counts, color=colors_hist, edgecolor="white", linewidth=1.5)
for bar, count in zip(bars, counts):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 str(count), ha="center", fontweight="bold", fontsize=13)
axes[0].set_ylabel("Jumlah Responden")
axes[0].set_title("Distribusi Kategori Glukosa")

# Box plot
bp = axes[1].boxplot([glucose], widths=0.5, patch_artist=True,
                     boxprops=dict(facecolor="#3498db", alpha=0.7))
axes[1].scatter(np.ones(len(glucose)), glucose, alpha=0.5, s=30, color="#2c3e50", zorder=5)
axes[1].set_xticklabels(["GlukosaRef (mg/dL)"])
axes[1].set_ylabel("mg/dL")
axes[1].set_title("Distribusi Nilai Glukosa")
axes[1].axhline(y=100, color="#f39c12", linestyle="--", alpha=0.7, label="Normal threshold (100)")
axes[1].axhline(y=126, color="#e74c3c", linestyle="--", alpha=0.7, label="DM threshold (126)")
axes[1].legend(fontsize=9, loc="upper right")

plt.suptitle("Figur 1 — Distribusi Data Glukosa (40 Sesi, 32 Responden)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig1_glucose_distribution.png", bbox_inches="tight")
plt.close()
print("✓ fig1_glucose_distribution.png")


# ===== Figure 2: Scatter Plot — Fitur vs Glukosa (Top 6) =====
top_features = [
    ("Tinggi_cm", "Tinggi (cm)"),
    ("Berat_kg", "Berat (kg)"),
    ("BMI", "BMI (kg/m²)"),
    ("TerakhirMakan_jam", "Terakhir Makan (jam)"),
    ("Usia", "Usia (tahun)"),
    ("IR_Mean", "IR Mean"),
]

fig, axes = plt.subplots(2, 3, figsize=(14, 9))
for idx, (col, label) in enumerate(top_features):
    ax = axes[idx // 3][idx % 3]
    corr = df[col].corr(df["GlukosaRef"])
    color = "#2ecc71" if corr > 0.3 else "#e74c3c" if corr < -0.3 else "#3498db"
    ax.scatter(df[col], df["GlukosaRef"], alpha=0.6, s=40, c=color, edgecolors="white")
    # Trend line
    z = np.polyfit(df[col].values, df["GlukosaRef"].values, 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[col].min(), df[col].max(), 100)
    ax.plot(x_line, p(x_line), "--", color=color, alpha=0.8, linewidth=1.5)
    ax.set_xlabel(label)
    ax.set_ylabel("Glukosa (mg/dL)")
    ax.set_title(f"r = {corr:.3f}")

plt.suptitle("Figur 2 — Korelasi Fitur dengan Glukosa Referensi", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig2_feature_correlation.png", bbox_inches="tight")
plt.close()
print("✓ fig2_feature_correlation.png")


# ===== Figure 3: Actual vs Predicted (from model evaluation) =====
with open(ROOT / "results" / "glucometer_validation.json") as f:
    val = json.load(f)

preds = val["predictions"]
actual = [p["reference_glucose_mg_dL"] for p in preds]
predicted = [p["predicted_glucose_mg_dL"] for p in preds]

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

# Scatter actual vs predicted
axes[0].scatter(actual, predicted, alpha=0.7, s=50, c="#3498db", edgecolors="white", zorder=5)
min_val = min(min(actual), min(predicted)) - 5
max_val = max(max(actual), max(predicted)) + 5
axes[0].plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Prediksi Ideal (y=x)")
axes[0].set_xlabel("Glukosa Referensi (mg/dL)")
axes[0].set_ylabel("Glukosa Prediksi (mg/dL)")
axes[0].set_title("Actual vs Prediksi (R² = 0.061)")
axes[0].legend()
axes[0].set_xlim(min_val, max_val)
axes[0].set_ylim(min_val, max_val)

# Residual plot
residuals = [a - p for a, p in zip(actual, predicted)]
axes[1].scatter(predicted, residuals, alpha=0.7, s=50, c="#e74c3c", edgecolors="white", zorder=5)
axes[1].axhline(y=0, color="black", linewidth=1.5, linestyle="-")
axes[1].set_xlabel("Glukosa Prediksi (mg/dL)")
axes[1].set_ylabel("Residual (Referensi - Prediksi)")
axes[1].set_title("Residual Plot")

plt.suptitle("Figur 3 — Evaluasi Model Regresi Glukosa (Random Forest V0.1)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig3_model_evaluation.png", bbox_inches="tight")
plt.close()
print("✓ fig3_model_evaluation.png")


# ===== Figure 4: Feature Importance =====
feature_names = [
    "Usia", "Berat_kg", "Tinggi_cm", "BMI", "TerakhirMakan_jam",
    "SuhuTubuh", "SuhuAmbient", "HR_est", "SpO2_est",
    "IR_Mean", "IR_Min", "IR_Max", "IR_Std", "IR_RMS",
    "RED_Mean", "RED_Min", "RED_Max", "RED_Std", "RED_RMS",
    "Ratio_AC", "Ratio_DC", "Samples",
]

# Approximate feature importance from correlation analysis
corr_with_glucose = []
for col in feature_names:
    if col in df.columns:
        c = abs(df[col].corr(df["GlukosaRef"]))
        corr_with_glucose.append(c if not np.isnan(c) else 0)
    else:
        corr_with_glucose.append(0)

# Sort
sorted_idx = np.argsort(corr_with_glucose)[::-1][:12]
sorted_names = [feature_names[i] for i in sorted_idx]
sorted_vals = [corr_with_glucose[i] for i in sorted_idx]

fig, ax = plt.subplots(figsize=(10, 6))
colors_bar = ["#e74c3c" if v > 0.3 else "#f39c12" if v > 0.2 else "#3498db" for v in sorted_vals]
bars = ax.barh(range(len(sorted_names)), sorted_vals, color=colors_bar, edgecolor="white", height=0.7)
ax.set_yticks(range(len(sorted_names)))
ax.set_yticklabels(sorted_names)
ax.set_xlabel("|Korelasi Pearson| dengan Glukosa")
ax.set_title("Figur 4 — Feature Importance (Korelasi Absolut dengan Glukosa)")
ax.invert_yaxis()
for bar, val in zip(bars, sorted_vals):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=10)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig4_feature_importance.png", bbox_inches="tight")
plt.close()
print("✓ fig4_feature_importance.png")


# ===== Figure 5: Model Comparison =====
with open(ROOT / "results" / "model_comparison.json") as f:
    mc = json.load(f)

model_names = [m["model"] for m in mc["models"]]
mae_vals = [m["overall"]["mae_mg_dL"] for m in mc["models"]]
r2_vals = [m["overall"]["r2"] for m in mc["models"]]
rmse_vals = [m["overall"]["rmse_mg_dL"] for m in mc["models"]]

# Rename for display
display_names = ["Baseline\n(Rata-rata)", "Linear\nRegression", "Random Forest\n(200 trees)"]

fig, axes = plt.subplots(1, 3, figsize=(14, 5))

# MAE
colors_model = ["#95a5a6", "#e74c3c", "#2ecc71"]
bars = axes[0].bar(display_names, mae_vals, color=colors_model, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, mae_vals):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.2f}", ha="center", fontweight="bold", fontsize=11)
axes[0].set_ylabel("MAE (mg/dL)")
axes[0].set_title("Mean Absolute Error")
axes[0].set_ylim(0, max(mae_vals) * 1.15)

# RMSE
bars = axes[1].bar(display_names, rmse_vals, color=colors_model, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, rmse_vals):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.2f}", ha="center", fontweight="bold", fontsize=11)
axes[1].set_ylabel("RMSE (mg/dL)")
axes[1].set_title("Root Mean Square Error")
axes[1].set_ylim(0, max(rmse_vals) * 1.15)

# R²
bars = axes[2].bar(display_names, r2_vals, color=colors_model, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, r2_vals):
    ypos = bar.get_height() + 0.02 if val >= 0 else bar.get_height() - 0.15
    axes[2].text(bar.get_x() + bar.get_width()/2, ypos,
                 f"{val:.4f}", ha="center", fontweight="bold", fontsize=11)
axes[2].set_ylabel("R² Score")
axes[2].set_title("Coefficient of Determination")
axes[2].axhline(y=0, color="black", linewidth=0.8)

plt.suptitle("Figur 5 — Perbandingan Model Regresi Glukosa", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig5_model_comparison.png", bbox_inches="tight")
plt.close()
print("✓ fig5_model_comparison.png")


# ===== Figure 6: System Architecture =====
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")

# Title
ax.text(7, 7.6, "SENS-Able — Arsitektur Sistem", fontsize=16, fontweight="bold",
        ha="center", va="center")

# Boxes
box_style = dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#2c3e50", linewidth=2)
sensor_box = dict(boxstyle="round,pad=0.4", facecolor="#e8f5e9", edgecolor="#27ae60", linewidth=2)
process_box = dict(boxstyle="round,pad=0.4", facecolor="#e3f2fd", edgecolor="#2980b9", linewidth=2)
output_box = dict(boxstyle="round,pad=0.4", facecolor="#fce4ec", edgecolor="#e74c3c", linewidth=2)
ai_box = dict(boxstyle="round,pad=0.4", facecolor="#fff3e0", edgecolor="#f39c12", linewidth=2)

# Sensor layer
ax.text(3.5, 6, "MAX30102\n(PPG Sensor)", fontsize=10, ha="center", va="center",
        bbox=sensor_box)
ax.text(7, 6, "MLX90614\n(IR Suhu)", fontsize=10, ha="center", va="center",
        bbox=sensor_box)
ax.text(10.5, 6, "User Input\n(Age, Weight)", fontsize=10, ha="center", va="center",
        bbox=sensor_box)

# ESP32
ax.text(7, 4.3, "ESP32 Microcontroller\n(MCU Utama)\n─────────────────\nBaca sensor → Hitung 22 fitur\n→ Proses data → Jalankan AI",
        fontsize=10, ha="center", va="center", bbox=box_style, fontfamily="monospace")

# AI Model
ax.text(7, 2.5, "Random Forest AI\n200 Decision Trees\n→ Prediksi Glukosa\n→ Klasifikasi Status",
        fontsize=10, ha="center", va="center", bbox=ai_box)

# Output layer
ax.text(2.5, 0.8, "📺 OLED\n(Visual)", fontsize=10, ha="center", va="center", bbox=output_box)
ax.text(7, 0.8, "🔊 Speaker\n(Audio)", fontsize=10, ha="center", va="center", bbox=output_box)
ax.text(11.5, 0.8, "📳 Vibromotor\n(Haptic)", fontsize=10, ha="center", va="center", bbox=output_box)

# Arrows
arrow_props = dict(arrowstyle="->", color="#2c3e50", lw=2)
ax.annotate("", xy=(7, 5.1), xytext=(3.5, 5.5), arrowprops=arrow_props)
ax.annotate("", xy=(7, 5.1), xytext=(7, 5.5), arrowprops=arrow_props)
ax.annotate("", xy=(7, 5.1), xytext=(10.5, 5.5), arrowprops=arrow_props)
ax.annotate("", xy=(7, 3.3), xytext=(7, 3.7), arrowprops=arrow_props)
ax.annotate("", xy=(2.5, 1.4), xytext=(5.5, 2.1), arrowprops=arrow_props)
ax.annotate("", xy=(7, 1.4), xytext=(7, 2.1), arrowprops=arrow_props)
ax.annotate("", xy=(11.5, 1.4), xytext=(8.5, 2.1), arrowprops=arrow_props)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig6_system_architecture.png", bbox_inches="tight")
plt.close()
print("✓ fig6_system_architecture.png")


# ===== Figure 7: Dataset Overview (demographics) =====
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Age distribution
axes[0, 0].hist(df["Usia"], bins=10, color="#3498db", edgecolor="white", linewidth=1.5, alpha=0.8)
axes[0, 0].set_xlabel("Usia (tahun)")
axes[0, 0].set_ylabel("Frekuensi")
axes[0, 0].set_title("Distribusi Usia Responden")

# Gender
gender_counts = df["Gender"].value_counts()
axes[0, 1].pie(gender_counts.values, labels=["Laki-laki", "Perempuan"],
               colors=["#3498db", "#e91e63"], autopct="%1.0f%%",
               startangle=90, textprops={"fontsize": 12})
axes[0, 1].set_title("Distribusi Gender")

# BMI
bmi_cats = pd.cut(df["BMI"], bins=[0, 18.5, 25, 30, 100],
                  labels=["Kurus (<18.5)", "Normal (18.5-25)", "Gemuk (25-30)", "Obese (>30)"])
bmi_counts = bmi_cats.value_counts()
colors_bmi = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]
bmi_ordered = [bmi_counts.get(c, 0) for c in ["Kurus (<18.5)", "Normal (18.5-25)", "Gemuk (25-30)", "Obese (>30)"]]
bmi_labels = ["Kurus\n(<18.5)", "Normal\n(18.5-25)", "Gemuk\n(25-30)", "Obese\n(>30)"]
bars = axes[1, 0].bar(bmi_labels, bmi_ordered, color=colors_bmi, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, bmi_ordered):
    if val > 0:
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                         str(val), ha="center", fontweight="bold", fontsize=12)
axes[1, 0].set_ylabel("Jumlah")
axes[1, 0].set_title("Distribusi BMI")

# Age vs Glucose
colors_scatter = ["#2ecc71" if g < 100 else "#f39c12" if g < 126 else "#e74c3c" for g in df["GlukosaRef"]]
axes[1, 1].scatter(df["Usia"], df["GlukosaRef"], c=colors_scatter, s=50, edgecolors="white", alpha=0.7)
axes[1, 1].set_xlabel("Usia (tahun)")
axes[1, 1].set_ylabel("Glukosa (mg/dL)")
axes[1, 1].set_title("Usia vs Glukosa")
legend_elements = [
    mpatches.Patch(color="#2ecc71", label="Normal (<100)"),
    mpatches.Patch(color="#f39c12", label="Pre-DM (100-125)"),
    mpatches.Patch(color="#e74c3c", label="DM (≥126)"),
]
axes[1, 1].legend(handles=legend_elements, fontsize=9, loc="upper right")

plt.suptitle("Figur 7 — Profil Demografis Responden", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIG_DIR / "fig7_demographics.png", bbox_inches="tight")
plt.close()
print("✓ fig7_demographics.png")

print(f"\n✅ Semua figur tersimpan di: {FIG_DIR}")
print(f"Total: 7 figur untuk laporan OPSI")
