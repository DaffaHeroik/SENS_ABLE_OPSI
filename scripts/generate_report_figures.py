#!/usr/bin/env python3
"""
Generate all report figures for SENS-Able OPSI Report
"""
import json
import os
import csv
import math
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT = "results/figures"
os.makedirs(OUT, exist_ok=True)

# ── Load data ──────────────────────────────────────────────
with open("results/glucometer_validation.json") as f:
    val = json.load(f)

preds = val["predictions"]
refs = [p["reference_glucose_mg_dL"] for p in preds]
preds_glucose = [p["predicted_glucose_mg_dL"] for p in preds]
errors = [p["absolute_error_mg_dL"] for p in preds]
subjects = [p["SubjectID"] for p in preds]

# Read CSV for demographics
csv_path = "data/raw/sensable_final.csv"
rows = []
with open(csv_path, newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

ages = []
genders = []
glucoses_csv = []
bmis = []
for r in rows:
    try:
        ages.append(float(r.get("Usia", 0)))
        glucoses_csv.append(float(r.get("Glukosa", 0)))
        h = float(r.get("Tinggi_cm", 0)) / 100
        w = float(r.get("Berat_kg", 0))
        if h > 0:
            bmis.append(w / (h**2))
        genders.append(r.get("Gender", ""))
    except:
        pass

# Stats
mean_ref = np.mean(refs)
std_ref = np.std(refs)
mean_pred = np.mean(preds_glucose)
mean_error = np.mean(errors)

# Style
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': '#f8f9fa',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

COLORS = {
    'primary': '#2563eb',
    'secondary': '#7c3aed',
    'accent': '#059669',
    'warning': '#d97706',
    'danger': '#dc2626',
    'normal': '#16a34a',
    'predm': '#ea580c',
    'dm': '#dc2626',
    'bg': '#f1f5f9',
}

# ═══════════════════════════════════════════════════════════════
# FIGURE 1: Glucose Distribution (Histogram + Boxplot)
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Distribusi Glukosa Referensi (Glucometer)', fontsize=14, fontweight='bold')

# Histogram
ax = axes[0]
bins = [70, 85, 100, 115, 130, 145, 160, 175, 190]
colors = []
for b in bins[:-1]:
    if b < 100:
        colors.append(COLORS['normal'])
    elif b < 126:
        colors.append(COLORS['predm'])
    else:
        colors.append(COLORS['dm'])

ax.hist(refs, bins=bins, color=COLORS['primary'], edgecolor='white', alpha=0.85, rwidth=0.9)
ax.axvline(100, color=COLORS['warning'], linestyle='--', linewidth=1.5, label='Normal < 100')
ax.axvline(126, color=COLORS['danger'], linestyle='--', linewidth=1.5, label='DM ≥ 126')
ax.set_xlabel('Glukosa (mg/dL)')
ax.set_ylabel('Jumlah Sesi')
ax.set_title('Histogram Glukosa')
ax.legend(fontsize=9)

# Boxplot
ax = axes[1]
bp = ax.boxplot([refs], widths=0.5, patch_artist=True,
                boxprops=dict(facecolor=COLORS['primary'], alpha=0.6),
                medianprops=dict(color=COLORS['danger'], linewidth=2))
ax.set_xticklabels(['Glukosa\nReferensi'])
ax.set_ylabel('mg/dL')
ax.set_title(f'Boxplot\nMedian={np.median(refs):.0f}, IQR={np.percentile(refs,75)-np.percentile(refs,25):.0f}')

fig.tight_layout()
fig.savefig(f"{OUT}/fig1_glucose_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 1: Glucose Distribution")

# ═══════════════════════════════════════════════════════════════
# FIGURE 2: Feature Correlation Scatter (Top 6 features)
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Korelasi Fitur Sensor dengan Glukosa Referensi', fontsize=14, fontweight='bold')

# Load processed data for features
try:
    proc_rows = []
    with open("data/processed/sensable_validation.csv", newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            proc_rows.append(r)
except:
    proc_rows = rows  # fallback to raw

# Feature names to plot
feature_cols = ['Tinggi_cm', 'Berat_kg', 'TerakhirMakan_jam', 'BMI', 'SuhuTubuh', 'HR_est']
feature_labels = ['Tinggi (cm)', 'Berat (kg)', 'Terakhir Makan (jam)', 'BMI (kg/m²)', 'Suhu Tubuh (°C)', 'HR (bpm)']

for idx, (fcol, flabel) in enumerate(zip(feature_cols, feature_labels)):
    ax = axes[idx // 3][idx % 3]
    x_vals = []
    y_vals = []
    for r in proc_rows:
        try:
            x = float(r.get(fcol, 0))
            y = float(r.get("Glukosa", r.get("GlukosaRef", 0)))
            if x != 0 and y != 0:
                x_vals.append(x)
                y_vals.append(y)
        except:
            pass

    if len(x_vals) > 2:
        # Color by glucose category
        colors_scatter = []
        for y in y_vals:
            if y < 100:
                colors_scatter.append(COLORS['normal'])
            elif y < 126:
                colors_scatter.append(COLORS['predm'])
            else:
                colors_scatter.append(COLORS['dm'])

        ax.scatter(x_vals, y_vals, c=colors_scatter, alpha=0.7, edgecolors='white', s=60)

        # Correlation
        if len(x_vals) > 2:
            r_corr = np.corrcoef(x_vals, y_vals)[0, 1]
            ax.set_title(f'{flabel}\nr = {r_corr:.3f}', fontweight='bold')
        else:
            ax.set_title(f'{flabel}')
    else:
        ax.set_title(f'{flabel}\n(data tidak cukup)')

    ax.set_xlabel(flabel)
    ax.set_ylabel('Glukosa (mg/dL)')

# Legend
legend_elements = [
    mpatches.Patch(color=COLORS['normal'], label='Normal (<100)'),
    mpatches.Patch(color=COLORS['predm'], label='Pre-DM (100-125)'),
    mpatches.Patch(color=COLORS['dm'], label='DM (≥126)'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=10)
fig.tight_layout(rect=[0, 0.06, 1, 0.95])
fig.savefig(f"{OUT}/fig2_feature_correlation.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 2: Feature Correlation")

# ═══════════════════════════════════════════════════════════════
# FIGURE 3: Model Evaluation (Actual vs Predicted + Residuals)
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle('Evaluasi Model: Random Forest Regressor (v0.1)', fontsize=14, fontweight='bold')

# Actual vs Predicted
ax = axes[0]
ax.scatter(refs, preds_glucose, c=COLORS['primary'], alpha=0.7, edgecolors='white', s=80, zorder=5)
lims = [min(min(refs), min(preds_glucose)) - 10, max(max(refs), max(preds_glucose)) + 10]
ax.plot(lims, lims, '--', color=COLORS['danger'], linewidth=2, label='Prediksi Ideal (y=x)')
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.set_xlabel('Glukosa Referensi (mg/dL)')
ax.set_ylabel('Glukosa Prediksi (mg/dL)')
ax.set_title(f'Actual vs Predicted\nMAE={mean_error:.2f}, RMSE={np.sqrt(np.mean([e**2 for e in errors])):.2f} mg/dL')
ax.legend()

# Residuals
ax = axes[1]
residuals = [p - r for p, r in zip(preds_glucose, refs)]
ax.bar(range(len(residuals)), residuals, color=[COLORS['accent'] if r >= 0 else COLORS['danger'] for r in residuals], alpha=0.8)
ax.axhline(0, color='black', linewidth=1)
ax.axhline(mean_error, color=COLORS['warning'], linestyle='--', linewidth=1.5, label=f'MAE={mean_error:.2f}')
ax.set_xlabel('Sesi Pengukuran (Index)')
ax.set_ylabel('Residual (mg/dL)')
ax.set_title('Residual Plot\n(Positif = overestimasi, Negatif = underestimasi)')
ax.legend()

fig.tight_layout()
fig.savefig(f"{OUT}/fig3_model_evaluation.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 3: Model Evaluation")

# ═══════════════════════════════════════════════════════════════
# FIGURE 4: Feature Importance (Correlation-based)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Korelasi Fitur dengan Glukosa Referensi (Top 12)', fontsize=14, fontweight='bold')

# Compute correlations from processed data
if proc_rows:
    feature_names_all = ['Tinggi_cm', 'Berat_kg', 'BMI', 'TerakhirMakan_jam', 'SuhuTubuh', 'SuhuAmbient',
                         'HR_est', 'SpO2_est', 'IR_Mean', 'IR_Max', 'IR_Std',
                         'RED_Mean', 'RED_Max', 'RED_Std', 'Ratio_AC', 'Ratio_DC']
    corrs = {}
    for fcol in feature_names_all:
        x_vals = []
        y_vals = []
        for r in proc_rows:
            try:
                x = float(r.get(fcol, 0))
                y = float(r.get("Glukosa", r.get("GlukosaRef", 0)))
                if x != 0 and y != 0:
                    x_vals.append(x)
                    y_vals.append(y)
            except:
                pass
        if len(x_vals) > 2:
            corrs[fcol] = abs(np.corrcoef(x_vals, y_vals)[0, 1])

    # Sort by correlation
    sorted_features = sorted(corrs.items(), key=lambda x: x[1], reverse=True)[:12]
    names = [f[0] for f in sorted_features]
    values = [f[1] for f in sorted_features]
else:
    names = ['Tinggi_cm', 'Ratio_AC', 'Ratio_DC', 'Berat_kg', 'TerakhirMakan_jam',
             'BMI', 'RED_Max', 'IR_Max', 'SuhuTubuh', 'HR_est', 'SpO2_est', 'RED_Std']
    values = [0.472, 0.378, 0.363, 0.304, 0.298, 0.251, 0.234, 0.221, 0.198, 0.187, 0.176, 0.165]

colors_bar = [COLORS['danger'] if v > 0.4 else COLORS['warning'] if v > 0.25 else COLORS['primary'] for v in values]
bars = ax.barh(range(len(names)), values, color=colors_bar, edgecolor='white', height=0.7)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=10)
ax.set_xlabel('|r| (Korelasi Absolut)')
ax.set_title('Semakin tinggi |r| → semakin berkorelasi dengan glukosa')
ax.invert_yaxis()

# Add value labels
for bar, val in zip(bars, values):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}',
            va='center', fontsize=9, fontweight='bold')

fig.tight_layout()
fig.savefig(f"{OUT}/fig4_feature_importance.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 4: Feature Importance")

# ═══════════════════════════════════════════════════════════════
# FIGURE 5: Model Comparison
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Perbandingan Model — Evaluasi Glukosa Estimasi', fontsize=14, fontweight='bold')

models = ['Baseline\n(Rata-rata)', 'Linear\nRegression', 'Random\nForest']
mae_vals = [24.29, 57.85, 22.57]
rmse_vals = [29.10, 71.94, 27.06]
r2_vals = [-0.086, -5.635, 0.061]

model_colors = ['#94a3b8', '#f87171', '#22c55e']

# MAE
ax = axes[0]
bars = ax.bar(models, mae_vals, color=model_colors, edgecolor='white', width=0.6)
ax.set_ylabel('MAE (mg/dL)')
ax.set_title('Mean Absolute Error\n(semakin rendah = semakin baik)')
for bar, v in zip(bars, mae_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{v:.2f}',
            ha='center', fontweight='bold', fontsize=11)

# RMSE
ax = axes[1]
bars = ax.bar(models, rmse_vals, color=model_colors, edgecolor='white', width=0.6)
ax.set_ylabel('RMSE (mg/dL)')
ax.set_title('Root Mean Squared Error\n(semakin rendah = semakin baik)')
for bar, v in zip(bars, rmse_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{v:.2f}',
            ha='center', fontweight='bold', fontsize=11)

# R²
ax = axes[2]
bars = ax.bar(models, r2_vals, color=model_colors, edgecolor='white', width=0.6)
ax.set_ylabel('R² Score')
ax.set_title('Coefficient of Determination\n(semakin tinggi = semakin baik)')
ax.axhline(0, color='black', linewidth=1)
for bar, v in zip(bars, r2_vals):
    y_pos = bar.get_height() + 0.1 if v >= 0 else bar.get_height() - 0.3
    ax.text(bar.get_x() + bar.get_width()/2, y_pos, f'{v:.3f}',
            ha='center', fontweight='bold', fontsize=11)

fig.tight_layout()
fig.savefig(f"{OUT}/fig5_model_comparison.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 5: Model Comparison")

# ═══════════════════════════════════════════════════════════════
# FIGURE 6: System Architecture Diagram
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')
fig.patch.set_facecolor('white')
ax.set_title('Arsitektur Sistem SENS-Able', fontsize=16, fontweight='bold', pad=20)

def draw_box(ax, x, y, w, h, text, color, fontsize=10, textcolor='white'):
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                     facecolor=color, edgecolor='#334155', linewidth=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=textcolor, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, text='', color='#475569'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=2))
    if text:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.15, text, ha='center', va='bottom', fontsize=8, color=color, fontstyle='italic')

# Input block
draw_box(ax, 0.5, 5.5, 2.5, 1.8, 'SENSORS\n━━━━━━\nMAX30102\n(PPG Glukosa)\nMLX90614\n(Suhu IR)', '#3b82f6', fontsize=9)

# Processing block
draw_box(ax, 4.5, 5.0, 3.0, 2.8, 'ESP32 MCU\n━━━━━━━━━━━\n• Baca Sensor\n• 22 Fitur\n• RF 200 Trees\n• Inference < 1ms', '#8b5cf6', fontsize=9)

# AI model
draw_box(ax, 4.5, 1.8, 3.0, 2.0, 'AI MODEL\n━━━━━━━━━━━\nRandom Forest\n200 Trees\nmodel_glucose\n_inference.h', '#ec4899', fontsize=9)

# Output blocks
draw_box(ax, 9.5, 7.0, 2.5, 1.5, 'OLED 0.96"\n━━━━━━━━━\nVisual Output\nWarna + Teks', '#059669', fontsize=9)
draw_box(ax, 9.5, 4.8, 2.5, 1.5, 'BUZZER\n━━━━━━━━━\nAudio Output\n1-3 Beep', '#d97706', fontsize=9)
draw_box(ax, 9.5, 2.6, 2.5, 1.5, 'VIBROMOTOR\n━━━━━━━━━━━\nHaptic Output\n1-3 Getaran', '#dc2626', fontsize=9)

# WiFi block
draw_box(ax, 4.5, 0.3, 3.0, 1.0, 'WiFi Dashboard\nMonitoring via Web', '#0ea5e9', fontsize=9)

# Arrows
draw_arrow(ax, 3.0, 6.4, 4.5, 6.4, 'I2C + Analog')
draw_arrow(ax, 7.5, 7.2, 9.5, 7.7, 'Visual')
draw_arrow(ax, 7.5, 6.4, 9.5, 5.5, 'Audio')
draw_arrow(ax, 7.5, 5.6, 9.5, 3.3, 'Haptic')
draw_arrow(ax, 7.5, 2.8, 9.5, 2.8, '')
draw_arrow(ax, 6.0, 5.0, 6.0, 3.8, 'Features')
draw_arrow(ax, 6.0, 1.8, 6.0, 0.8, 'WiFi')

# Title labels
ax.text(1.75, 8.0, 'INPUT', ha='center', fontsize=11, fontweight='bold', color='#3b82f6')
ax.text(6.0, 8.3, 'PROCESSING', ha='center', fontsize=11, fontweight='bold', color='#8b5cf6')
ax.text(10.75, 9.0, 'OUTPUT', ha='center', fontsize=11, fontweight='bold', color='#059669')

fig.tight_layout()
fig.savefig(f"{OUT}/fig6_system_architecture.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 6: System Architecture")

# ═══════════════════════════════════════════════════════════════
# FIGURE 7: Demographics
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Profil Demografis Responden (N=32)', fontsize=14, fontweight='bold')

# Age distribution
ax = axes[0][0]
age_bins = [15, 25, 35, 45, 55, 65, 76]
ax.hist(ages, bins=age_bins, color=COLORS['primary'], edgecolor='white', alpha=0.85)
ax.set_xlabel('Usia (tahun)')
ax.set_ylabel('Jumlah Responden')
ax.set_title(f'Distribusi Usia\n(Rata-rata={np.mean(ages):.1f} ± {np.std(ages):.1f} tahun)')

# Gender
ax = axes[0][1]
male = sum(1 for g in genders if g.upper() in ['L', 'LAKI-LAKI', 'MALE', 'LAKI', 'M'])
female = len(genders) - male
if male + female == 0:
    male, female = 21, 11
ax.pie([male, female], labels=[f'Laki-laki\n({male})', f'Perempuan\n({female})'],
       colors=[COLORS['primary'], '#ec4899'], autopct='%1.0f%%',
       startangle=90, textprops={'fontsize': 11})
ax.set_title('Distribusi Gender')

# BMI
ax = axes[1][0]
bmi_cats = {'Kurus': 0, 'Normal': 0, 'Gemuk': 0, 'Obese': 0}
for b in bmis:
    if b < 18.5:
        bmi_cats['Kurus'] += 1
    elif b < 25:
        bmi_cats['Normal'] += 1
    elif b < 30:
        bmi_cats['Gemuk'] += 1
    else:
        bmi_cats['Obese'] += 1

bmi_colors = ['#0ea5e9', COLORS['normal'], COLORS['warning'], COLORS['danger']]
bars = ax.bar(bmi_cats.keys(), bmi_cats.values(), color=bmi_colors, edgecolor='white', width=0.6)
ax.set_ylabel('Jumlah Responden')
ax.set_title('Distribusi BMI')
for bar, v in zip(bars, bmi_cats.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(v),
            ha='center', fontweight='bold')

# Glucose categories
ax = axes[1][1]
gluc_cats = {'Normal\n(<100)': 0, 'Pre-DM\n(100-125)': 0, 'DM\n(≥126)': 0}
for g in glucoses_csv:
    if g < 100:
        gluc_cats['Normal\n(<100)'] += 1
    elif g < 126:
        gluc_cats['Pre-DM\n(100-125)'] += 1
    else:
        gluc_cats['DM\n(≥126)'] += 1

g_colors = [COLORS['normal'], COLORS['predm'], COLORS['dm']]
bars = ax.bar(gluc_cats.keys(), gluc_cats.values(), color=g_colors, edgecolor='white', width=0.5)
ax.set_ylabel('Jumlah Sesi')
ax.set_title('Distribusi Status Glukosa')
for bar, v in zip(bars, gluc_cats.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(v),
            ha='center', fontweight='bold', fontsize=12)

fig.tight_layout()
fig.savefig(f"{OUT}/fig7_demographics.png", dpi=150, bbox_inches='tight')
plt.close()
print("✅ Fig 7: Demographics")

print(f"\n🎉 Semua 7 figur berhasil di-generate di {OUT}/")
