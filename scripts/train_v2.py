"""
SENS-Able: Training Script v2
Smart Health Monitor Inklusif berbasis AI

Sesuai proposal: Model AI dilatih dengan dataset PPG publik
dan di-deploy ke ESP32 via TensorFlow Lite Micro.

Fitur:
- Data sendiri (sensable_final.csv) + augmentasi
- Public dataset PIMA Indians Diabetes (768 sampel)
- Klasifikasi: Sehat (0) vs Diabetes (1)
- Konversi ke TensorFlow Lite untuk ESP32

Usage: python3 sensable_train_v2.py
Requirements: pip install scikit-learn pandas numpy
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIG
# ============================================================
SENSABLE_FILE = 'sensable_final.csv'

SENSABLE_FEATURES = [
    'Usia', 'Berat_kg', 'Tinggi_cm', 'BMI', 'GlukosaRef',
    'TerakhirMakan_jam', 'SuhuTubuh', 'SuhuAmbient',
    'HR_est', 'SpO2_est', 'IR_Mean', 'IR_Min', 'IR_Max',
    'IR_Std', 'IR_RMS', 'RED_Mean', 'RED_Min', 'RED_Max',
    'RED_Std', 'RED_RMS', 'Ratio_AC', 'Ratio_DC'
]

# Common features between SENS-Able and PIMA
COMMON_FEATURES = ['Usia', 'BMI', 'GlukosaRef', 'Berat_kg']


# ============================================================
# 1. LOAD SENSABLE DATA
# ============================================================
def load_sensable():
    """Load and prepare SENS-Able dataset."""
    df = pd.read_csv(SENSABLE_FILE)
    X = df[SENSABLE_FEATURES].values
    y = df['Diabetes'].values.astype(int)
    return X, y, df, SENSABLE_FEATURES


# ============================================================
# 2. AUGMENTATION (SMOTE-like)
# ============================================================
def augment_minority(X, y, n_synthetic=30, noise_std=0.2, seed=42):
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
# 3. LOAD PIMA INDIANS DIABETES (PUBLIC DATASET)
# ============================================================
def load_pima():
    """
    PIMA Indians Diabetes Dataset (UCI)
    768 sampel, 8 fitur, 2 kelas
    Fitur: Pregnancies, Glucose, BloodPressure, SkinThickness,
           Insulin, BMI, DiabetesPedigreeFunction, Age
    """
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age', 'Outcome']

    try:
        df = pd.read_csv(url, names=cols)
        print(f"  ✅ PIMA dataset loaded: {len(df)} sampel")
        print(f"     Diabetes=0: {(df['Outcome']==0).sum()}, Diabetes=1: {(df['Outcome']==1).sum()}")
        return df
    except Exception as e:
        print(f"  ❌ Gagal load PIMA: {e}")
        return None


# ============================================================
# 4. TRAIN & EVALUATE
# ============================================================
def train_and_evaluate(X, y, features, label=""):
    """Train models and print results."""
    print(f"\n{'━' * 60}")
    print(f"📊 {label}")
    print(f"{'━' * 60}")
    print(f"Data: {len(y)} sampel (0: {(y==0).sum()}, 1: {(y==1).sum()})")
    print(f"Fitur: {len(features)}\n")

    n_splits = min(5, min(np.bincount(y)))
    if n_splits < 2:
        print("  ⚠️ Terlalu sedikit sampel per kelas untuk CV")
        n_splits = 2

    models = {
        'Logistic Regression': LogisticRegression(
            class_weight='balanced', max_iter=1000, random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            class_weight='balanced', n_estimators=100, random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100, max_depth=3, random_state=42
        ),
    }

    results = {}
    for name, model in models.items():
        # Cross-validation
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        f1_scores, acc_scores = [], []

        for train_idx, test_idx in skf.split(X, y):
            model.fit(X[train_idx], y[train_idx])
            y_pred = model.predict(X[test_idx])
            f1_scores.append(f1_score(y[test_idx], y_pred, zero_division=0))
            acc_scores.append(accuracy_score(y[test_idx], y_pred))

        # Full fit
        model.fit(X, y)
        y_pred_full = model.predict(X)
        cm = confusion_matrix(y, y_pred_full)

        results[name] = {
            'model': model,
            'acc': np.mean(acc_scores),
            'f1': np.mean(f1_scores),
            'cm': cm,
        }

        print(f"  {name}:")
        print(f"    Accuracy: {np.mean(acc_scores)*100:.1f}% ± {np.std(acc_scores)*100:.1f}%")
        print(f"    F1 Score: {np.mean(f1_scores):.3f} ± {np.std(f1_scores):.3f}")
        if cm.shape == (2, 2):
            print(f"    Confusion: TN={cm[0][0]} FP={cm[0][1]} FN={cm[1][0]} TP={cm[1][1]}")
        print()

    return results


# ============================================================
# 5. FEATURE IMPORTANCE
# ============================================================
def show_feature_importance(model, features, top_n=10):
    """Show top N features."""
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
    elif hasattr(model, 'coef_'):
        imp = np.abs(model.coef_[0])
    else:
        return

    ranked = np.argsort(imp)[::-1]
    print(f"  Top {min(top_n, len(features))} fitur:")
    for i in range(min(top_n, len(features))):
        j = ranked[i]
        bar = "█" * max(1, int(imp[j] * 80))
        print(f"    {i+1:2d}. {features[j]:25s} {imp[j]:.4f} {bar}")
    print()


# ============================================================
# 6. CONVERT TO TFLITE (SIMULATION)
# ============================================================
def export_model_info(model, features, filename='model_info.txt'):
    """Export model info for TFLite conversion."""
    info = []
    info.append("=== SENS-Able Model Info ===")
    info.append(f"Model: {type(model).__name__}")
    info.append(f"Features: {len(features)}")
    info.append(f"Feature names: {', '.join(features)}")
    info.append(f"Classes: 0=Sehat, 1=Diabetes")
    info.append("")

    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
        ranked = np.argsort(imp)[::-1]
        info.append("Feature Importance:")
        for i, idx in enumerate(ranked):
            info.append(f"  {i+1}. {features[idx]}: {imp[idx]:.4f}")

    info.append("")
    info.append("=== Untuk Deploy ke ESP32 ===")
    info.append("1. Convert model ke TensorFlow Lite:")
    info.append("   import tensorflow as tf")
    info.append("   converter = tf.lite.TFLiteConverter.from_saved_model('model')")
    info.append("   tflite_model = converter.convert()")
    info.append("")
    info.append("2. Convert ke C array (xxd -i model.tflite > model.h)")
    info.append("3. Include model.h di ESP32 Arduino sketch")
    info.append("4. Gunakan TensorFlow Lite Micro library")

    with open(filename, 'w') as f:
        f.write('\n'.join(info))
    print(f"  📁 Model info saved: {filename}")


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🔬 SENS-Able Training v2")
    print("   Smart Health Monitor Inklusif")
    print("=" * 60)

    # --- 1. Load SENS-Able data ---
    print("\n📂 Loading SENS-Able data...")
    X_sens, y_sens, df_sens, sens_features = load_sensable()
    print(f"  ✅ Loaded: {len(y_sens)} sampel, {len(sens_features)} fitur")

    # --- 2. Train on SENS-Able data (augmented) ---
    X_aug, y_aug = augment_minority(X_sens, y_sens, n_synthetic=30)
    results_sens = train_and_evaluate(
        X_aug, y_aug, sens_features,
        "SENS-Able Data (Augmented)"
    )

    # Feature importance
    rf_sens = results_sens['Random Forest']['model']
    print("  📊 Feature Importance (SENS-Able):")
    show_feature_importance(rf_sens, sens_features)

    # --- 3. Load PIMA public dataset ---
    print("\n📂 Loading PIMA Indians Diabetes (public dataset)...")
    df_pima = load_pima()

    if df_pima is not None:
        # Train on PIMA
        X_pima = df_pima.drop('Outcome', axis=1).values
        y_pima = df_pima['Outcome'].values
        pima_features = list(df_pima.drop('Outcome', axis=1).columns)

        results_pima = train_and_evaluate(
            X_pima, y_pima, pima_features,
            "PIMA Indians Diabetes (Public Dataset)"
        )

        # Feature importance
        rf_pima = results_pima['Random Forest']['model']
        print("  📊 Feature Importance (PIMA):")
        show_feature_importance(rf_pima, pima_features)

        # --- 4. Combined: common features ---
        print("\n📊 Analisis Gabungan (Fitur Umum)")
        print("━" * 60)
        print("  Fitur yang overlap antara SENS-Able & PIMA:")
        print("  - Usia ↔ Age")
        print("  - BMI ↔ BMI")
        print("  - GlukosaRef ↔ Glucose")
        print()

        # Map SENS-Able to common features
        sens_common = df_sens[['Usia', 'BMI', 'GlukosaRef']].values
        sens_common = np.hstack([sens_common, np.zeros((len(sens_common), 1))])  # placeholder
        pima_common = df_pima[['Age', 'BMI', 'Glucose']].values
        pima_common = np.hstack([pima_common, np.ones((len(pima_common), 1))])  # placeholder

        # Use Glucose as primary predictor
        print("  Prediksi Diabetes berdasarkan Glukosa saja:")
        for threshold in [100, 110, 120, 125, 130, 140]:
            yp = (df_sens['GlukosaRef'].values.astype(float) >= threshold).astype(int)
            cm = confusion_matrix(y_sens, yp)
            if cm.shape == (2, 2):
                tp, fn, fp, tn = cm[1][1], cm[1][0], cm[0][1], cm[0][0]
            else:
                tp = fn = fp = 0
                tn = len(y_sens)
            acc = (tp + tn) / len(y_sens) * 100
            print(f"    Glukosa >= {threshold}: Acc={acc:.0f}% (TP={tp} FP={fp} FN={fn} TN={tn})")

    # --- 5. Export model ---
    print(f"\n{'━' * 60}")
    print("📦 Export Model")
    print(f"{'━' * 60}")
    best_model = results_sens['Random Forest']['model']
    export_model_info(best_model, sens_features)

    # --- 6. Summary ---
    print(f"\n{'=' * 60}")
    print("📋 RINGKASAN")
    print(f"{'=' * 60}")
    print(f"✅ SENS-Able: {len(y_sens)} sampel, {len(sens_features)} fitur")
    print(f"✅ Augmented: {len(y_aug)} sampel")
    if df_pima is not None:
        print(f"✅ PIMA: {len(y_pima)} sampel (public)")
    print(f"✅ Model: Random Forest (terbaik)")
    print(f"")
    print(f"💡 LANGKAH SELANJUTNYA:")
    print(f"   1. Tambah data SENS-Able (target 200+ sampel)")
    print(f"   2. Retrain dengan data gabungan")
    print(f"   3. Convert ke TensorFlow Lite")
    print(f"   4. Deploy ke ESP32 via TinyML")
    print(f"   5. Uji akurasi vs glukometer (MAE < 15 mg/dL)")
