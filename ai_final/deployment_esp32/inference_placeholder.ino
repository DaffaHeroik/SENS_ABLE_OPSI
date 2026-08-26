#include "model_contract_v0_1.h"

// This is intentionally a placeholder. It confirms the feature contract but
// does not produce a glucose prediction until an embedded model is validated.

void setup() {
  Serial.begin(115200);
  Serial.println("SENS-Able AI V0.1 contract loaded");
  Serial.print("Expected feature count: ");
  Serial.println(SENSABLE_FEATURE_COUNT);
  Serial.println("Inference is not enabled: convert and validate the model first.");
}

void loop() {
  delay(1000);
}
