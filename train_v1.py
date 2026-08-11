"""
SENS-Able: Training Script
Smart Health Monitor Inklusif berbasis AI

Usage: python3 sensable_train.py
Requirements: pip install scikit-learn pandas numpy matplotlib
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIG
# ============================================================
DATA_FILE = 'sensable_final.csv'

FEATURES = [
    'Usia', 'Berat_kg', 'Tinggi_cm', 'BMI', 'GlukosaRef',
    'TerakhirMakan_jam', 'SuhuTubuh', 'SuhuAmbient',
    'HR_est', 'SpO2_est', 'IR_Mean', 'IR_Min', 'IR_Max',
    'IR_Std', 'IR_RMS', 'RED_Mean', 'RED_Min', 'RED_Max',
    'RED_Std', 'RED_RMS', 'Ratio_AC', 'Ratio_DC'
]

TARGET = 'Diabetes'

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 60)
print("🔬 SENS-Able Training")
print("=" * 60)

df = pd.read_csv(DATA_FILE)
X = df[FEATURES].values
y = df[TARGET].values.astype(int)

print(f"Dataset: {len(df)} sampel, {len(FEATURES)} fitur")
print(f"Kelas 0 (Sehat):   {(y == 0).sum()}")
print(f"Kelas 1 (Diabetes): {(y == 1).sum()}")

# ============================================================
# PREPROCESSING
# ============================================================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ============================================================
# AUGMENTATION (SMOTE-like for class imbalance)
# ============================================================
def augment_minority(X, y, n_synthetic=20, noise_std=0.25, seed=42):
    """Generate synthetic samples for minority class."""
    np.random.seed(seed)
    minority_idx = np.where(y == 1)[0]
    if len(minority_idx) == 0:
        return X, y

    X_syn = []
    for _ in range(n_synthetic):
        base = X[minority_idx[np.random.randint(len(minority_idx))]]
        noise = np.random.normal(0, noise_std, base.shape)
        X_syn.append(base + noise)

    X_aug = np.vstack([X, np.array(X_syn)])
    y_aug = np.concatenate([y, np.ones(n_synthetic, dtype=int)])
    return X_aug, y_aug


# ============================================================
# MODEL TRAINING
# ============================================================
def train_and_evaluate(X, y, label=""):
    """Train multiple models and print results."""
    print(f"\n{'─' * 60}")
    print(f"📊 {label}")
    print(f"{'─' * 60}")
    print(f"Data: {len(y)} sampel (0: {(y == 0).sum()}, 1: {(y == 1).sum()})\n")

    n_classes = len(np.unique(y))
    n_splits = min(5, min(np.bincount(y)))  # can't have more splits than min class count

    models = {
        'Logistic Regression': LogisticRegression(
            class_weight='balanced', max_iter=1000, random_state=42
        ),
        'Decision Tree': DecisionTreeClassifier(
            class_weight='balanced', random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            class_weight='balanced', n_estimators=100, random_state=42
        ),
    }

    results = {}

    for name, model in models.items():
        # Full fit for confusion matrix
        model.fit(X, y)
        y_pred_full = model.predict(X)
        cm = confusion_matrix(y, y_pred_full)

        # Cross-validation (only if enough samples per class)
        if n_splits >= 2:
            skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
            f1_scores = []
            acc_scores = []
            for train_idx, test_idx in skf.split(X, y):
                model.fit(X[train_idx], y[train_idx])
                y_pred = model.predict(X[test_idx])
                f1_scores.append(f1_score(y[test_idx], y_pred, zero_division=0))
                acc_scores.append(accuracy_score(y[test_idx], y_pred))
            cv_acc = np.mean(acc_scores)
            cv_f1 = np.mean(f1_scores)
            cv_acc_std = np.std(acc_scores)
            cv_f1_std = np.std(f1_scores)
        else:
            cv_acc = accuracy_score(y, y_pred_full)
            cv_f1 = f1_score(y, y_pred_full, zero_division=0)
            cv_acc_std = 0.0
            cv_f1_std = 0.0

        results[name] = {
            'model': model,
            'acc': cv_acc,
            'f1': cv_f1,
            'cm': cm,
        }

        print(f"  {name}:")
        print(f"    Accuracy: {cv_acc * 100:.1f}% ± {cv_acc_std * 100:.1f}%")
        print(f"    F1 Score: {cv_f1:.3f} ± {cv_f1_std:.3f}")
        if cm.shape == (2, 2):
            print(f"    Confusion: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")
        print()

    return results


# ============================================================
# FEATURE IMPORTANCE
# ============================================================
def show_feature_importance(model, features, top_n=10):
    """Show top N most important features."""
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
    elif hasattr(model, 'coef_'):
        imp = np.abs(model.coef_[0])
    else:
        return

    ranked = np.argsort(imp)[::-1]
    print(f"  Top {top_n} fitur:")
    for i in range(min(top_n, len(features))):
        j = ranked[i]
        bar = "█" * max(1, int(imp[j] * 80))
        print(f"    {i + 1:2d}. {features[j]:20s} {imp[j]:.4f} {bar}")
    print()


# ============================================================
# GLUCOSA THRESHOLD RULE
# ============================================================
def glucose_threshold_analysis(df, y):
    """Analyze glucose threshold as baseline."""
    print(f"{'─' * 60}")
    print(f"📊 Baseline: Glukosa Threshold")
    print(f"{'─' * 60}\n")

    glukosa = df['GlukosaRef'].values.astype(float)
    best_acc = 0
    best_t = 0

    for t in range(80, 200, 5):
        yp = (glukosa >= t).astype(int)
        cm = confusion_matrix(y, yp)
        if cm.shape == (2, 2):
            tp, fn = cm[1][1], cm[1][0]
            fp, tn = cm[0][1], cm[0][0]
        else:
            tp = fn = fp = 0
            tn = len(y)
        acc = (tp + tn) / len(y) * 100

        if acc > best_acc:
            best_acc = acc
            best_t = t

    # Show best
    yp = (glukosa >= best_t).astype(int)
    cm = confusion_matrix(y, yp)
    if cm.shape == (2, 2):
        tp, fn = cm[1][1], cm[1][0]
        fp, tn = cm[0][1], cm[0][0]
    else:
        tp = fn = fp = 0
        tn = len(y)

    print(f"  Best threshold: Glukosa >= {best_t}")
    print(f"  Accuracy: {best_acc:.0f}%")
    print(f"  TN={tn} FP={fp} FN={fn} TP={tp}")
    print()


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    # 1. Original data
    results_raw = train_and_evaluate(X_scaled, y, "Data Asli (33 sampel)")

    # 2. Augmented data
    X_aug, y_aug = augment_minority(X_scaled, y, n_synthetic=20)
    results_aug = train_and_evaluate(X_aug, y_aug, "Data Augmented (SMOTE-like)")

    # 3. Feature importance
    print(f"{'─' * 60}")
    print(f"📊 Feature Importance")
    print(f"{'─' * 60}\n")
    rf = results_aug['Random Forest']['model']
    show_feature_importance(rf, FEATURES)

    # 4. Glucose threshold baseline
    glucose_threshold_analysis(df, y)

    # 5. Summary
    print("=" * 60)
    print("📋 RINGKASAN")
    print("=" * 60)
    print(f"✅ Dataset: {len(df)} sampel, {len(FEATURES)} fitur")
    print(f"✅ Augmented: {len(y_aug)} sampel")
    print(f"✅ Model terbaik: Random Forest")
    print(f"")
    print(f"💡 REKOMENDASI:")
    print(f"   1. Kumpulkan 200+ sampel (target 30%+ diabetes)")
    print(f"   2. Retrain dengan data baru")
    print(f"   3. Konversi ke TensorFlow Lite")
    print(f"   4. Deploy ke ESP32 via TinyML")
    print(f"")
    print(f"📁 Model tersimpan di variabel: results_aug")
