#pragma once

// SENS-Able AI V0.1 physical-device contract.
// This header documents the exact feature order. It is not the model itself.
// GlukosaRef is deliberately absent because it is the glucometer target.

#include <stddef.h>

static constexpr size_t SENSABLE_FEATURE_COUNT = 22;

static const char* const SENSABLE_FEATURE_NAMES[SENSABLE_FEATURE_COUNT] = {
    "Usia",
    "Berat_kg",
    "Tinggi_cm",
    "BMI",
    "TerakhirMakan_jam",
    "SuhuTubuh",
    "SuhuAmbient",
    "HR_est",
    "SpO2_est",
    "IR_Mean",
    "IR_Min",
    "IR_Max",
    "IR_Std",
    "IR_RMS",
    "RED_Mean",
    "RED_Min",
    "RED_Max",
    "RED_Std",
    "RED_RMS",
    "Ratio_AC",
    "Ratio_DC",
    "Samples",
};

struct SensableModelInputV01 {
    float values[SENSABLE_FEATURE_COUNT];
};

// V0.1 uses a scikit-learn joblib artifact and therefore cannot be called
// directly from Arduino. Implement this function only after converting and
// validating an embedded model with the exact same feature order.
