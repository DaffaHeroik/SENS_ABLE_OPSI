import json
import unittest
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]


class ModelingPipelineTests(unittest.TestCase):
    def test_config_excludes_target_and_provenance_from_features(self):
        config = json.loads((ROOT / "configs" / "glucose_model_v0_1.json").read_text())
        features = set(config["features"])
        excluded = set(config["excluded_from_features"])
        self.assertEqual(config["target"]["column"], "GlukosaRef")
        self.assertNotIn("GlukosaRef", features)
        self.assertTrue({"SuhuTubuh_Imputed", "SuhuAmbient_Imputed"}.isdisjoint(features))
        self.assertTrue({"GlukosaRef", "SubjectID"}.issubset(excluded))

    def test_model_comparison_report_is_leakage_safe(self):
        report = json.loads((ROOT / "reports" / "model_comparison.json").read_text())
        self.assertTrue(report["validation"]["no_synthetic_data"])
        self.assertTrue(report["validation"]["no_target_leakage"])
        self.assertNotIn("GlukosaRef", report["dataset"]["feature_columns"])
        self.assertGreaterEqual(len(report["models"]), 3)
        self.assertEqual(report["selected_exploratory_model"]["model"], "RandomForestRegressor")

    def test_selected_artifact_matches_metadata(self):
        artifact = ROOT / "models" / "glucose_model_v0_1.joblib"
        metadata = json.loads((ROOT / "models" / "glucose_model_v0_1_metadata.json").read_text())
        model = joblib.load(artifact)
        self.assertEqual(metadata["target"], "GlukosaRef")
        self.assertEqual(metadata["model"], "RandomForestRegressor")
        self.assertEqual(metadata["trained_rows"], 40)
        self.assertEqual(metadata["trained_subjects"], 32)
        self.assertEqual(len(model.feature_importances_), len(metadata["features"]))

    def test_ai_final_contract_matches_canonical_contract(self):
        canonical = json.loads((ROOT / "configs" / "glucose_model_v0_1.json").read_text())
        physical = json.loads((ROOT / "ai_final" / "config" / "model_contract_v0_1.json").read_text())
        self.assertEqual(canonical["version"], physical["version"])
        self.assertEqual(canonical["features"], physical["features"])
        self.assertNotIn("GlukosaRef", physical["features"])
        self.assertEqual(len(physical["features"]), 22)

    def test_improvement_experiment_is_exploratory_and_leakage_safe(self):
        report = json.loads((ROOT / "reports" / "model_improvement_experiment.json").read_text())
        self.assertTrue(report["validation"]["no_synthetic_data"])
        self.assertTrue(report["validation"]["no_target_leakage"])
        self.assertEqual(report["dataset"]["rows"], 40)
        self.assertEqual(report["dataset"]["unique_subjects"], 32)
        self.assertEqual(report["best_exploratory_result"]["model"], "TunedRandomForestWithFeatureSelection")

    def test_ai_final_evaluation_matches_canonical_v01(self):
        evaluation = json.loads((ROOT / "ai_final" / "evaluation" / "evaluation_v0_1.json").read_text())
        self.assertEqual(evaluation["metrics"]["mae_mg_dL"], 22.5716)
        self.assertTrue(evaluation["validation"]["no_target_leakage"])


if __name__ == "__main__":
    unittest.main()
