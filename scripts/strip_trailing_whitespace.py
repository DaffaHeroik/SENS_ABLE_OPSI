from pathlib import Path

root = Path('/home/ubuntu/SENS_ABLE_OPSI')
paths = [
    root / 'MEMORY.md',
    root / 'docs' / 'ml_modeling_plan_summary.md',
    root / 'docs' / 'opsi_stage2_recheck_plan.md',
    root / 'docs' / 'proposal_recheck_OPSI2025.md',
    root / 'docs' / 'proposal_revision_draft.md',
    root / 'docs' / 'model_building_guide.md',
    root / 'reports' / 'modeling_v0_1_summary.md',
    root / 'reports' / 'opsi_stage2_report_framework.md',
]
for path in paths:
    text = path.read_text(encoding='utf-8')
    cleaned = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    path.write_text(cleaned, encoding='utf-8')
    print(path)
