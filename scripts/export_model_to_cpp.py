"""
Export SENS-Able Glucose Random Forest Model to C++ Header for ESP32.

This script converts the scikit-learn RandomForestRegressor to a C++ header
file that can be compiled directly into Arduino/ESP32 firmware.

Usage: python3 scripts/export_model_to_cpp.py
"""

import json
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "results" / "glucose_model_v0_1.joblib"
OUTPUT_PATH = ROOT / "firmware" / "model_glucose_inference.h"


def tree_to_cpp(tree, feature_names, indent=0):
    """Convert a single decision tree to C++ if-else code."""
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]

    def recurse(node, depth):
        indent_str = "  " * depth
        if tree_.feature[node] != -2:  # Not a leaf
            fname = feature_name[node].replace("[", "_").replace("]", "")
            threshold = tree_.threshold[node]
            left = recurse(tree_.children_left[node], depth + 1)
            right = recurse(tree_.children_right[node], depth + 1)
            return (
                f"{indent_str}if (input[{feature_names.index(feature_name[node])}] <= {threshold:.6f}f) {{\n"
                f"{left}\n"
                f"{indent_str}}} else {{\n"
                f"{right}\n"
                f"{indent_str}}}"
            )
        else:  # Leaf node
            value = tree_.value[node][0][0]
            return f"{indent_str}return {value:.6f}f;"

    return recurse(0, 0)


def generate_cpp_header(model, feature_names, n_features):
    """Generate complete C++ header with embedded model."""
    
    n_trees = len(model.estimators_)
    n_classes = 1  # Regression
    
    cpp_code = f"""#pragma once
// SENS-Able Glucose Prediction Model v0.1
// Auto-generated from scikit-learn RandomForestRegressor
// DO NOT EDIT MANUALLY - regenerate with: python3 scripts/export_model_to_cpp.py
//
// Features ({n_features}):
// {', '.join(feature_names)}
//
// Model: RandomForestRegressor (n_estimators={n_trees})
// Target: Glucose (mg/dL)

#include <stddef.h>

// Number of input features
#define GLUCOSE_MODEL_FEATURES {n_features}

// Number of trees in the forest
#define GLUCOSE_MODEL_TREES {n_trees}

// Feature names for documentation
static const char* GLUCOSE_FEATURE_NAMES[GLUCOSE_MODEL_FEATURES] = {{
"""
    
    for i, name in enumerate(feature_names):
        cpp_code += f'    "{name}",\n'
    
    cpp_code += """};

// ============================================================
// Decision Tree Functions
// ============================================================

"""
    
    # Generate each tree as a separate function
    for i, estimator in enumerate(model.estimators_):
        cpp_code += f"static float tree_{i}(const float input[{n_features}]) {{\n"
        cpp_code += tree_to_cpp(estimator, feature_names)
        cpp_code += "\n}\n\n"
    
    # Generate the main prediction function
    cpp_code += f"""// ============================================================
// Main Prediction Function
// ============================================================

/**
 * Predict glucose level from sensor features.
 * 
 * @param features Array of {n_features} sensor features
 * @return Predicted glucose in mg/dL
 */
float predict_glucose(const float features[{n_features}]) {{
    float sum = 0.0f;
"""
    
    for i in range(n_trees):
        cpp_code += f"    sum += tree_{i}(features);\n"
    
    cpp_code += f"""
    // Average across all trees
    return sum / {n_trees}.0f;
}}

/**
 * Interpret glucose level for user feedback.
 * 
 * @param glucose Glucose value in mg/dL
 * @return Status: 0=Normal, 1=Pre-diabetic, 2=Diabetic, 3=Low (Hypoglycemia)
 */
int interpret_glucose(float glucose) {{
    if (glucose < 70.0f) {{
        return 3;  // Hypoglycemia - DANGER
    }} else if (glucose < 100.0f) {{
        return 0;  // Normal
    }} else if (glucose < 126.0f) {{
        return 1;  // Pre-diabetic
    }} else {{
        return 2;  // Diabetic range
    }}
}}

/**
 * Get text description of glucose status.
 */
const char* glucose_status_text(int status) {{
    switch (status) {{
        case 0: return "Normal";
        case 1: return "Pre-diabetic";
        case 2: return "Diabetic";
        case 3: return "LOW!";
        default: return "Unknown";
    }}
}}
"""
    
    return cpp_code


def main():
    print("Loading model...")
    model = joblib.load(MODEL_PATH)
    
    # Feature names from model_contract
    feature_names = [
        "Usia", "Berat_kg", "Tinggi_cm", "BMI", "TerakhirMakan_jam",
        "SuhuTubuh", "SuhuAmbient", "HR_est", "SpO2_est",
        "IR_Mean", "IR_Min", "IR_Max", "IR_Std", "IR_RMS",
        "RED_Mean", "RED_Min", "RED_Max", "RED_Std", "RED_RMS",
        "Ratio_AC", "Ratio_DC", "Samples"
    ]
    
    n_features = len(feature_names)
    n_trees = len(model.estimators_)
    
    print(f"Model: RandomForestRegressor")
    print(f"Trees: {n_trees}")
    print(f"Features: {n_features}")
    
    # Generate C++ header
    cpp_code = generate_cpp_header(model, feature_names, n_features)
    
    # Write to file
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(cpp_code, encoding="utf-8")
    
    print(f"\nGenerated: {OUTPUT_PATH}")
    print(f"File size: {len(cpp_code)} bytes")
    print(f"\nTo use in Arduino:")
    print(f"  1. Include: #include \"model_glucose_inference.h\"")
    print(f"  2. Call: float glucose = predict_glucose(features);")
    print(f"  3. Interpret: int status = interpret_glucose(glucose);")


if __name__ == "__main__":
    main()
