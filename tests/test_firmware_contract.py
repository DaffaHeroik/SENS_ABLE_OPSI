import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMWARE_DIR = ROOT / "firmware" / "SENS_ABLE_Data_Collector"


class FirmwareContractTests(unittest.TestCase):
    def test_original_sketch_is_preserved(self):
        original = (FIRMWARE_DIR / "SENS_ABLE_Data_Collector_v6_4_original.ino").read_bytes()
        uploaded = Path("/home/ubuntu/upload/pasted_content.txt").read_bytes()
        self.assertEqual(original, uploaded)

    def test_supported_sketch_keeps_dataset_reference_column(self):
        source = (FIRMWARE_DIR / "SENS_ABLE_Data_Collector_v6_4.ino").read_text()
        self.assertIn("GlukosaRef", source)
        self.assertIn("Gula Darah Referensi (mg/dL) dari Glukometer", source)
        self.assertIn("#define MAX_SAMPLES 1200", source)
        self.assertIn("#define MIN_SAMPLES 100", source)

    def test_supported_sketch_does_not_auto_format_littlefs(self):
        source = (FIRMWARE_DIR / "SENS_ABLE_Data_Collector_v6_4.ino").read_text()
        self.assertIn("LittleFS.begin(false)", source)
        self.assertNotIn("LittleFS.begin(true)", source)


if __name__ == "__main__":
    unittest.main()
