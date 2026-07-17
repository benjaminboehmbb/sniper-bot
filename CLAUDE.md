# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Sniper-Bot is a BTCUSDT algorithmic trading research project. It has three largely independent
Python code paths that must not be confused:

1. **`engine/simtraderGS.py`** — the "Gold Standard" (GS) backtest evaluator. Consumes discrete
   `*_signal` columns (-1/0/+1) from a price CSV, computes `score = Σ(weight_i * signal_i)`, and
   simulates LONG/SHORT entries/exits against `enter_z`/`exit_z` thresholds. This file is treated
   as **frozen/read-only** ("GS v1 remains read-only") — new evaluation logic goes into a v2, not
   into this file. `engine/validators.py` holds related input validation.
2. **`live_l1/`** — the live/paper-trading engine ("L1"). Contains the real-time loop
   (`live_l1/core/loop.py`), regime detection, intent fusion, execution, guards, state
   persistence/recovery, and operational tooling (`live_l1/tools/`). This is what actually runs
   against live or paper market data. Its design is staged L0 → L1 → L1B → L1C → L1D → L1E → L2,
   documented under `docs/LIVE_DESIGN_*.md` (L0 = minimal live loop / state model, L1 = paper
   trading + guards + observability, L2 = start conditions and live-readiness).
3. **`run_engine/`** — a separate, newer "canonical state" run loop under active architectural
   consolidation (see Governance below). `run_engine/main.py` currently drives a synthetic/dry-run
   tick stream through `RunLoop` (`run_engine/core/loop.py`), which owns `CanonicalState` /
   `CanonicalEnforcer` and delegates to per-concern engines: `state`, `regime`, `strategy`,
   `position`, `trade_lifecycle`, `risk`, `execution`, `pnl`, `performance`. The *Active Runtime
   Boundary* for this engine is defined as the AST-import closure from `run_engine.main` — treat
   any module outside that closure as inactive/archived, not as dead code to casually revive.

Strategy selection results from the GS research pipeline (K3 → K12 raster search over signal
combinations) live under `strategies/GS/LONG_FINAL/` and `strategies/GS/SHORT_FINAL/` and are
marked **FROZEN — DO NOT MODIFY**; treat them as inputs, not editable artifacts. `scripts/` and
`tools/` hold the (large, one-off-style) analysis scripts used to produce/inspect GS runs
(`analyze_GS_k*.py`, `gs_*.py`, regime/timing/audit scripts). `data/`, `results/`, `logs/`,
`archive/` (bare) and other output directories are git-ignored — large CSVs and run artifacts are
local-only and generally won't exist in a fresh checkout.

## Commands

Environment: a `.venv` exists at the repo root with `numpy`, `pandas`, `PyYAML`, `requests`
installed (`requirements.txt`). No `pytest` — tests use stdlib `unittest`.

```bash
source .venv/bin/activate

# Run the automated regression suite (TD-005) — the primary test suite in this repo
python -m unittest discover -s tests/regression -p "test_*.py"

# Run a single regression test module / case
python -m unittest tests.regression.test_foundational
python -m unittest tests.regression.test_foundational.SomeTestClass.test_some_case

# live_l1 operational self-tests (not under tests/)
python -m unittest live_l1.tools.test_operational_profiles
python -m unittest live_l1.tools.test_unattended_operation
python -m unittest live_l1.tools.test_monitor_failure_injection

# ad hoc tool tests
python -m unittest tools.test_p44_polarity_aware_timing
python -m unittest tools.test_p34_strict_timing_direction
python -m unittest tools.test_timing_5m_v2_minimal

# Run the run_engine dry-run loop directly (synthetic price stream, Ctrl+C to stop)
python -m run_engine.main
```

`tests/regression/` is the TD-005 automated regression suite: it replays controlled-condition
ticks through the live `run_engine.RunLoop` via `observation.NonInterferenceObserver` and compares
against a certified reference baseline — it never modifies or bypasses `run_engine/` runtime
semantics, only observes it. If you touch `run_engine/core/*`, run this suite.

There is no lint/format/build tooling configured (no `pyproject.toml`, `setup.cfg`, or CI config
in the repo) — match existing code style in the file you're editing.

## Governance / documentation-driven process

`docs/` (650+ files) is not incidental — this repo runs on an unusually formal, binding
spec-driven process for anything touching `run_engine/`. Before making non-trivial changes there,
be aware of the pattern even if you don't reproduce it in full:

- Each change to the active runtime typically flows through staged, individually-filed documents:
  Functional Requirement / Dependency / Capability-Gap Analysis → Architecture → Specification →
  Implementation → Final Certification, stored under `docs/architecture/{analysis,design,
  specifications,implementation,certification}/`. Certifications independently re-derive and
  re-verify claims rather than trusting the implementation's own report.
- `docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_*.md` is the living
  list of deferred/known issues (TD-xxx) with an owning target phase — check it before assuming
  something is an unknown bug.
- `docs/governance/` holds platform-wide standards (SCG_00x = Scientific Compute/Dataset/
  Evidence/Decision/Knowledge Governance) and `docs/governance/README.md` explains the structure.
- Cross-cutting, binding **research/strategy policies** live in `docs/POLICIES/` (mostly German,
  marked `verbindlich` = binding) and take priority in this order on conflict: **AFML alignment**
  (`AFML_ALIGNMENT_SNIPER_BOT.md`, overfitting/backtest-integrity per López de Prado) → **Strategy
  Realism** (`STRATEGY_REALISM_GUIDE_SNIPER_BOT.md`, realistic costs/slippage/turnover, per Chan)
  → **ML Usage/Validation** (`ML4T_USAGE_GUIDE_SNIPER_BOT.md`, `ml_validation_policy.md` — no
  lookahead, no black-box ML as a substitute for research) → **System & Execution**
  (`SYSTEM_EXECUTION_GUIDE_SNIPER_BOT.md`, per Hilpisch — architecture/logging/state-management
  are mandatory, not optimization details). `backtest_integrity_policy.md`'s core rule: *a
  backtest that structurally cannot fail is worthless*.
- `docs/POLICIES/TIME_STANDARD.md` is binding for both GS and L1: raw/internal data uses int64 ns
  since epoch (`timestamp_ns`), all GS/L1 CSV outputs and logs use ISO-8601 UTC seconds
  (`timestamp_utc`); resampling/aggregation must operate on `timestamp_ns`.
- Both 1m and 5m are active, binding analysis timeframes (5m introduced 2026-01-19 after a
  validated transfer test); each has its own seeds/baselines/K3–K12 paths and both are subject to
  identical GS policies (`docs/POLICIES/README.md`).

Given the scale of this governance layer, don't invent new top-level doc categories or certify
your own change — if a task looks like it demands a full Architecture/Specification/Certification
chain, flag that to the user rather than silently generating one.

## Notes

- Repository docs/comments/config are frequently a German/English mix; match the language already
  used in the file/section you're editing rather than translating wholesale.
- `main` (empty file at repo root) and the `run_engine/main.py` `__main__` block both wire up
  `RunLoop`; `run_engine/main.py`'s module-level `main()` is the actual current entry point.

## Project-specific working rules

1. Repository understanding first.
   Before proposing architectural or implementation changes, understand the existing repository and reuse existing components whenever reasonable.

2. Architecture authority.
   Never change architectural decisions, governance rules, ADRs or scientific methodology on your own. If a requested implementation appears to conflict with them, stop and explicitly explain the conflict.

3. Scope discipline.
   Implement only the requested scope. Do not perform unrelated refactorings or "cleanup" work unless explicitly requested.

4. Preserve architecture.
   Prefer extending existing architecture over introducing parallel implementations, duplicate modules or alternative frameworks.

5. Complete deliverables.
   When generating code or documentation, always provide complete files rather than partial snippets whenever practical.

6. Validation after implementation.
   After code changes, recommend the appropriate validation steps (unit tests, regression tests, import validation, git diff --check) before considering the task complete.

7. Documentation discipline.
   Do not invent new documentation categories or governance documents. Reuse the existing documentation structure unless the user explicitly requests structural changes.

8. Scientific integrity.
   Preserve determinism, reproducibility and traceability. Never introduce hidden randomness, look-ahead bias or undocumented behavioural changes.

9. Communication.
   Keep responses concise, objective and technically precise. Distinguish observations from assumptions.
