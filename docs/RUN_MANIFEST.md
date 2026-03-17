# Run Manifest (GS v2 candidate)

Purpose: Provide auditability for backtest runs without modifying engine/simtraderGS.py (GS v1 remains read-only).

Local template (not committed; results/ is gitignored):
- results/GS/meta/run_manifest_template.json

Intended use:
- External runner/tool writes a concrete manifest file per run:
  results/GS/meta/run_manifest_<UTC>.json

Minimum fields:
- git_commit, repo_root
- engine file sha256
- price_csv path, timestamp_col, window offset/rows
- direction, use_forward, enter_z/exit_z, tp/sl/max_hold
- fee_roundtrip, slippage_model (explicit 0 unless modeled)

Status:
- Template created locally on 2026-01-14
- No engine changes performed
