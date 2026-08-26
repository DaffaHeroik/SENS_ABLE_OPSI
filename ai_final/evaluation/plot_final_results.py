"""Generate final V0.1 figures from the root reporting pipeline."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
runpy.run_path(str(ROOT / "scripts" / "plot_model_results.py"), run_name="__main__")
