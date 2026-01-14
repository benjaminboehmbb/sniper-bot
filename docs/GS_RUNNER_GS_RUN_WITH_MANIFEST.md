# GS Runner (gs_run_with_manifest) — gs-runner-v1.0

Tag: gs-runner-v1.0  
Purpose: Deterministic single-eval runner for engine/simtraderGS with:
- manifest write (inputs + derived gate stats)
- input preflight (timestamp monotonic, signal domain, optional all-zero fail)
- one evaluation write (gs_eval_*.json)

## Canonical invocation (WSL)
Always run from repo root and prefer module execution (avoids "No module named engine"):

python3 -m tools.gs_run_with_manifest \
  --price-csv <CSV> \
  --direction <long|short> \
  --comb-json "<DICT>" \
  --fee-roundtrip 0.0004 \
  --tp 0.04 --sl 0.02 --max-hold 1440 --enter-z 1.0 --exit-z 0.0 \
  --preflight-rows 200000 --preflight-offset 0 \
  --fail-on-all-zero-signals

## Outputs
- results/GS/meta/run_manifest_<UTC>.json
- results/GS/meta/gs_eval_<UTC>.json

## Gates (auto)
The runner derives effective gate mode from direction:
- direction=long  -> effective_gate_mode=allow_long
- direction=short -> effective_gate_mode=allow_short

Manifest contains:
gates:
  allow_long: {present, rows_checked, ones, allow_rate}
  allow_short: {present, rows_checked, ones, allow_rate}
  effective_gate_mode: "allow_long"|"allow_short"

## Non-negotiables / Guards
- Run via "python3 -m ..." from repo root (WSL).
- Preflight must pass before eval is accepted.
- Signals are consumed via *_signal contract (comb keys are mapped via KEYMAP).
- enter_z/exit_z are recorded in manifest; fee_roundtrip recorded; tp/sl/max_hold recorded.

## Known failure modes (prevented)
- Wrong working dir -> engine import fails. Use module form.
- Copying shell lines into .py -> syntax errors. Keep shell separate.
