import json
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class DatasetPipelineTests(unittest.TestCase):
    def test_processed_dataset_is_anonymized_and_complete(self):
        frame = pd.read_csv(ROOT / "data" / "processed" / "sensable_validation.csv")
        self.assertEqual(len(frame), 40)
        self.assertIn("SubjectID", frame.columns)
        self.assertNotIn("Nama", frame.columns)
        self.assertEqual(int(frame.isna().sum().sum()), 0)
        self.assertTrue((frame["GlukosaRef"] > 0).all())
        self.assertTrue(frame["SubjectID"].str.startswith("SUB-").all())
        self.assertIn("SuhuTubuh_Imputed", frame.columns)
        self.assertIn("SuhuAmbient_Imputed", frame.columns)
        self.assertEqual(int(frame["SuhuTubuh_Imputed"].sum()), 7)
        self.assertEqual(int(frame["SuhuAmbient_Imputed"].sum()), 6)
        self.assertTrue((frame.loc[frame["SuhuTubuh_Imputed"] == 1, "SuhuTubuh"] > 0).all())
        self.assertTrue((frame.loc[frame["SuhuAmbient_Imputed"] == 1, "SuhuAmbient"] > 0).all())

    def test_exclusion_log_has_reasons(self):
        excluded = pd.read_csv(ROOT / "data" / "processed" / "excluded_records.csv")
        self.assertEqual(len(excluded), 6)
        self.assertTrue(excluded["exclude_reason"].notna().all())
        self.assertTrue(excluded["exclude_reason"].ne("").all())
        self.assertTrue((excluded["exclude_reason"] == "low_optical_signal_capture").all())

    def test_glucometer_reference_is_not_a_feature(self):
        report = json.loads((ROOT / "reports" / "glucometer_validation.json").read_text())
        self.assertEqual(report["target"]["column"], "GlukosaRef")
        self.assertFalse(report["target"]["used_as_feature"])
        self.assertNotIn("GlukosaRef", report["dataset"]["feature_columns"])


if __name__ == "__main__":
    unittest.main()
