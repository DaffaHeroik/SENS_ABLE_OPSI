"""
SENS-Able: Training Script v3
Smart Health Monitor Inklusif berbasis AI

Strategi:
- TRAIN: PIMA Indians Diabetes (768 sampel, public dataset)
- VALIDATE: SENS-Able sensor data (33 sampel, data sendiri)
- Deploy ke ESP32 via TensorFlow Lite Micro

Sesuai proposal: "Model AI dilatih dengan dataset PPG publik"
Data sendiri digunakan sebagai VALIDASI, bukan training.

Usage: python3 train.py
Requirements: pip install scikit-learn pandas numpy
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score
import pickle
import json
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

# ============================================================
# CONFIG
# ============================================================
ROOT = Path(__file__).resolve().parent
SENSABLE_FILE = ROOT / 'data' / 'processed' / 'sensable_validation.csv'

# Fitur yang dipakai model (common features)
TRAIN_FEATURES = ['Age', 'BMI', 'Glucose']
SENSABLE_MAP = {
    'Age': 'Usia',
    'BMI': 'BMI',
    'Glucose': 'GlukosaRef'
}


# ============================================================
# 1. LOAD DATA
# ============================================================
def load_pima():
    """Load PIMA Indians Diabetes (training data)."""
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']
    df = pd.read_csv(url, names=cols)
    return df


def load_sensable():
    """Load SENS-Able data (validation data)."""
    df = pd.read_csv(SENSABLE_FILE)
    return df


# ============================================================
# 2. TRAIN MODEL
# ============================================================
def train_model(X_train, y_train):
    """Train Random Forest on PIMA data."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        max_depth=5,
        random_state=42
    )
    model.fit(X_scaled, y_train)

    # Cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1_scores = []
    acc_scores = []
    for train_idx, test_idx in skf.split(X_train, y_train):
        # Fit preprocessing only on each training fold to avoid validation leakage.
        cv_scaler = StandardScaler()
        X_fold_train = cv_scaler.fit_transform(X_train[train_idx])
        X_fold_test = cv_scaler.transform(X_train[test_idx])
        model_cv = RandomForestClassifier(
            n_estimators=100, class_weight='balanced',
            max_depth=5, random_state=42
        )
        model_cv.fit(X_fold_train, y_train[train_idx])
        y_pred = model_cv.predict(X_fold_test)
        f1_scores.append(f1_score(y_train[test_idx], y_pred))
        acc_scores.append(accuracy_score(y_train[test_idx], y_pred))

    return model, scaler, {
        'cv_accuracy': np.mean(acc_scores),
        'cv_f1': np.mean(f1_scores),
        'cv_accuracy_std': np.std(acc_scores),
        'cv_f1_std': np.std(f1_scores),
    }


# ============================================================
# 3. VALIDATE ON SENSABLE DATA
# ============================================================
def validate(model, scaler, df_sensable):
    """Validate model on SENS-Able sensor data."""
    # Map SENS-Able features to PIMA features
    X_val = df_sensable[[SENSABLE_MAP[f] for f in TRAIN_FEATURES]].values.astype(float)
    y_val = df_sensable['Diabetes'].values.astype(int)

    X_val_scaled = scaler.transform(X_val)
    y_pred = model.predict(X_val_scaled)
    y_proba = model.predict_proba(X_val_scaled)[:, 1]

    acc = accuracy_score(y_val, y_pred)
    cm = confusion_matrix(y_val, y_pred)
    f1 = f1_score(y_val, y_pred, zero_division=0)

    return {
        'accuracy': acc,
        'f1': f1,
        'confusion_matrix': cm.tolist(),
        'predictions': y_pred.tolist(),
        'probabilities': y_proba.tolist(),
        'actual': y_val.tolist(),
    }


# ============================================================
# 4. GLUCOSE THRESHOLD BASELINE
# ============================================================
def glucose_baseline(df_sensable):
    """Simple glucose threshold as baseline."""
    glukosa = df_sensable['GlukosaRef'].values.astype(float)
    y = df_sensable['Diabetes'].values.astype(int)

    best_acc = 0
    best_t = 0
    for t in range(80, 200, 5):
        yp = (glukosa >= t).astype(int)
        acc = accuracy_score(y, yp)
        if acc > best_acc:
            best_acc = acc
            best_t = t

    yp = (glukosa >= best_t).astype(int)
    cm = confusion_matrix(y, yp)

    return {
        'threshold': best_t,
        'accuracy': best_acc,
        'confusion_matrix': cm.tolist(),
    }


# ============================================================
# 5. EXPORT
# ============================================================
def export_model(model, scaler, metrics, filename='model.pkl'):
    """Save model and scaler."""
    with open(filename, 'wb') as f:
        pickle.dump({'model': model, 'scaler': scaler, 'metrics': metrics}, f)
    print(f"  📁 Model saved: {filename}")


def export_report(metrics_train, metrics_val, baseline, filename='report.json'):
    """Export training report."""
    report = {
        'model': 'RandomForestClassifier',
        'features': TRAIN_FEATURES,
        'training': {
            'dataset': 'PIMA Indians Diabetes',
            'samples': int(metrics_train.get('n_samples', 768)),
            'cv_accuracy': round(metrics_train['cv_accuracy'] * 100, 1),
            'cv_f1': round(metrics_train['cv_f1'], 3),
        },
        'validation': {
            'dataset': 'SENS-Able (data sendiri)',
            'samples': int(metrics_val.get('n_samples', 33)),
            'accuracy': round(metrics_val['accuracy'] * 100, 1),
            'f1': round(metrics_val['f1'], 3),
            'confusion_matrix': metrics_val['confusion_matrix'],
        },
        'baseline_glucose_threshold': baseline,
    }
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  📁 Report saved: {filename}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🔬 SENS-Able Training v3")
    print("   Train: PIMA (public) | Validate: SENS-Able (sendiri)")
    print("=" * 60)

    # --- Load data ---
    print("\n📂 Loading data...")
    df_pima = load_pima()
    df_sens = load_sensable()
    print(f"  PIMA: {len(df_pima)} sampel (0: {(df_pima['Outcome']==0).sum()}, 1: {(df_pima['Outcome']==1).sum()})")
    print(f"  SENS-Able: {len(df_sens)} sampel (0: {(df_sens['Diabetes']==0).sum()}, 1: {(df_sens['Diabetes']==1).sum()})")

    # --- Train on PIMA ---
    print("\n📊 Training pada PIMA Indians Diabetes...")
    X_train = df_pima[TRAIN_FEATURES].values
    y_train = df_pima['Outcome'].values
    model, scaler, train_metrics = train_model(X_train, y_train)
    train_metrics['n_samples'] = len(y_train)

    print(f"  ✅ Cross-validation Results:")
    print(f"     Accuracy: {train_metrics['cv_accuracy']*100:.1f}% ± {train_metrics['cv_accuracy_std']*100:.1f}%")
    print(f"     F1 Score: {train_metrics['cv_f1']:.3f} ± {train_metrics['cv_f1_std']:.3f}")

    # --- Feature importance ---
    print(f"\n  📊 Feature Importance:")
    imp = model.feature_importances_
    for i, (feat, score) in enumerate(zip(TRAIN_FEATURES, imp)):
        bar = "█" * max(1, int(score * 60))
        print(f"    {i+1}. {feat:15s} {score:.4f} {bar}")

    # --- Validate on SENS-Able ---
    print(f"\n📊 Validasi pada SENS-Able Data (data sendiri)...")
    val_metrics = validate(model, scaler, df_sens)
    val_metrics['n_samples'] = len(df_sens)

    print(f"  ✅ Validation Results:")
    print(f"     Accuracy: {val_metrics['accuracy']*100:.1f}%")
    print(f"     F1 Score: {val_metrics['f1']:.3f}")
    cm = np.array(val_metrics['confusion_matrix'])
    if cm.shape == (2, 2):
        print(f"     Confusion: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")

    # Show per-sample predictions
    print(f"\n  📋 Prediksi per sampel:")
    print(f"  {'No':>3} {'Nama':25s} {'Gluk':>6} {'Aktual':>7} {'Prediksi':>9} {'Prob':>6} {'Match':>6}")
    print(f"  {'-'*65}")
    for i, row in df_sens.iterrows():
        actual = int(row['Diabetes'])
        pred = val_metrics['predictions'][i]
        prob = val_metrics['probabilities'][i]
        match = "✅" if actual == pred else "❌"
        subject = str(row.get('SubjectID', row.get('Nama', f'row-{i+1}')))
        print(f"  {i+1:3d} {subject:25s} {row['GlukosaRef']:>6} {'Diabetes' if actual==1 else 'Sehat':>7} {'Diabetes' if pred==1 else 'Sehat':>9} {prob:>6.2f} {match:>6}")

    # --- Glucose threshold baseline ---
    print(f"\n📊 Baseline: Glukosa Threshold")
    baseline = glucose_baseline(df_sens)
    print(f"  Best threshold: >= {baseline['threshold']}")
    print(f"  Accuracy: {baseline['accuracy']*100:.0f}%")
    cm_b = np.array(baseline['confusion_matrix'])
    if cm_b.shape == (2, 2):
        print(f"  Confusion: TN={cm_b[0][0]} FP={cm_b[0][1]} FN={cm_b[1][0]} TP={cm_b[1][1]}")

    # --- Export ---
    print(f"\n📦 Export...")
    export_model(model, scaler, train_metrics, str(ROOT / 'model.pkl'))
    export_report(train_metrics, val_metrics, baseline, str(ROOT / 'report.json'))

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"📋 RINGKASAN")
    print(f"{'='*60}")
    print(f"✅ Model dilatih pada PIMA (768 sampel, public)")
    print(f"✅ Model divalidasi pada SENS-Able (33 sampel, sendiri)")
    print(f"✅ Akurasi training CV: {train_metrics['cv_accuracy']*100:.1f}%")
    print(f"✅ Akurasi validasi: {val_metrics['accuracy']*100:.1f}%")
    print(f"")
    print(f"💡 Strategi ini lebih valid karena:")
    print(f"   - Data training (PIMA) terpisah dari data validasi (SENS-Able)")
    print(f"   - Model belajar dari pola umum diabetes (768 sampel)")
    print(f"   - Data sensor sendiri jadi test set nyata")
    print(f"   - Tidak overfitting pada data kecil")
    print(f"")
    print(f"💡 LANGKAH SELANJUTNYA:")
    print(f"   1. Tambah data SENS-Able (target 100+ sampel)")
    print(f"   2. Retrain dengan fitur sensor lengkap")
    print(f"   3. Convert ke TensorFlow Lite")
    print(f"   4. Deploy ke ESP32 via TinyML")
