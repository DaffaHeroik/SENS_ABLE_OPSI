"""Run the fixed-feature ablation experiment from the AI-final folder."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT / "scripts" / "feature_ablation_glucose.py"), run_name="__main__")
