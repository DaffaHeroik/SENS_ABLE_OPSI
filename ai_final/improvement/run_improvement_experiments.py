"""Run the controlled improvement experiment from the AI-final folder."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT / "scripts" / "improve_glucose_model.py"), run_name="__main__")
