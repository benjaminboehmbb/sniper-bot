# Pre-IU-4 Repository Quality Audit

Date: 2026-08-09

Branch: `codex/pre-iu4-quality-audit-2026-08-09`

Reviewed code baseline: `263049df549cc9c9ef2698c983cd0b87590f596b`

Status: classification audit; no production file deleted, moved, or changed

## 1. Purpose and boundary

This audit creates a controlled checkpoint before IU-4 development. It identifies
which Python assets are required, future-only, review candidates, or already
archived. Static reachability is evidence, not an automatic deletion rule:
research and batch scripts are often intentional entrypoints and therefore have
no import consumer.

The untracked, user-owned file
`scripts/build_rcc002_spec_bundle.py` was explicitly excluded. It was not read,
changed, staged, or committed. IU-4, Exchange access, and Live remain locked.

## 2. Mechanical inventory

| Item | Count | Interpretation |
|---|---:|---|
| Tracked files | 1,765 | Repository is large and governance-heavy. |
| Tracked Python files | 726 | Main cleanup surface. |
| Python files already under `archive/` | 81 | Archiving has already begun. |
| Python parse failures | 0 | All tracked Python files are syntactically inspectable. |
| Tracked `scripts/` Python files | 158 | Mostly deliberate batch/research entrypoints. |
| Python test modules | 109 | Coverage is concentrated, not repository-wide. |
| Tracked Markdown files | 820 | Documentation consolidation is a separate later phase. |
| Exact duplicate Python groups | 1 | Both files are already historical archive files. |

The sole exact duplicate group is:

- `archive/HISTORICAL_K3_K10_2026-01-06/scripts_legacy_from_root/analyze_k7_short.py`
- `archive/HISTORICAL_K3_K10_2026-01-06/scripts_legacy_from_root/analyze_k8_short.py`

No active duplicate was found that is safe to remove immediately.

## 3. Classification decision

| Classification | Scope | Decision |
|---|---|---|
| `KEEP_REQUIRED_IU4` | `live_l1/core/paper_economics*.py`, `live_l1/state/paper_account.py`, `live_l1/state/paper_artifacts.py`, their state/runtime dependencies and tests | Required for the controlled IU-3 to IU-4 transition. |
| `KEEP_FUTURE_ISOLATED` | `gate_builder.py`, `regime_builder.py`, `regime_v2_builder.py`, `signal_builder.py`, `timing_5m_v2.py` and its test pair | Previously documented future online-feed/experimental assets; not dead merely because current imports are zero. |
| `KEEP_OPERATIONAL` | `scripts/run_live_l1_paper.py` and 17 `live_l1/tools/` operational tools | Explicit entrypoints or operational safety tooling. |
| `KEEP_OUT_OF_SCOPE` | `rcc002/`, `scripts/rcc002/`, `run_engine/`, `engine/`, existing `archive/` | Separate governed systems; no Pre-IU-4 cleanup mutation. |
| `REVIEW_HIGH_RISK` | 104 `tools/ssi/` files and 53 `tools/trade_inspector/` files | Large surfaces with no detected external test imports; independent architecture/minimalism review required. |
| `REVIEW_BY_CAMPAIGN` | 105 batch scripts and 43 `scripts/state_research/` scripts | Review by completed research campaign and reproducibility need, never by import count alone. |
| `ARCHIVE_CANDIDATE_AFTER_REVIEW` | `live_l1/guards/cost_guards.py` | Zero consumers/tests and duplicates the newer persistent-account guard with incompatible hard-coded float/ROI-unit limits. Do not integrate as-is. |
| `ARCHIVE_CANDIDATE_AFTER_REVIEW` | `tools/ssi/decision_engine/decision_engine_runner.py`, `tools/ssi/decision_evidence/decision_evidence_runner.py` | Only non-entrypoint modules with zero detected inbound imports beyond package boilerplate. External review must confirm no dynamic use. |
| `ARCHIVE_CANDIDATE_AFTER_REVIEW` | `seeds/5m/btcusdt_5m_short_timing_core_v1.csv.bak` | Non-archive backup artifact with content differing from the active CSV; preserve provenance before moving. |
| `REMOVE_NOW` | none | Current evidence is insufficient for irreversible deletion. |

## 4. IU-4-specific finding

`live_l1/guards/cost_guards.py` uses hard-coded float limits such as
`FEE_ROUNDTRIP_ASSUMED = 0.0004`, `MAX_TRADES_PER_DAY = 400`, and
`FEE_BUDGET_DAY = 0.12` in ROI units. The new
`live_l1/state/paper_artifacts.py::evaluate_account_entry_guard` is Decimal-
based, bound to the accepted economics profile, and evaluates persistent account
state. Combining both unchanged would create two competing sources of truth.

Recommendation: keep the profile-bound persistent-account guard as the IU-4
authority. Send `cost_guards.py` through independent review, then archive it or
extract only a separately justified safety invariant. Do not silently merge its
constants.

The four online builders remain future-only because the June review already
classified them as intended realtime-feed assets. IU-4 must not activate them.

## 5. Main quality risks

1. SSI and Trade Inspector contain 157 Python files in total, but this audit
   detected no external test imports for either subsystem. This is the largest
   current minimalism and maintainability risk.
2. The 148-file batch/state-research surface is historically valuable but too
   broad for the active working tree. Campaign-level provenance must be recorded
   before moving completed experiments into `archive/`.
3. Documentation volume (820 Markdown files) creates navigation cost. It should
   be consolidated only after code ownership and archive decisions are settled.
4. The three existing audit utilities under `tools/` overwrite older dated
   reports. Their source was inspected, but they were not executed in order to
   preserve historical evidence.

## 6. Verification baseline

Executed on the reviewed branch without changing production files:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
Ran 81 tests — OK

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -t .
Ran 170 tests — OK

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/rcc002 -t .
Ran 1012 tests — 1007 passed; 3 failures and 2 errors
```

The five RCC002 findings are existing historical-governance mismatches, not an
IU-4 regression: the tests still require specification versions `0.8.0` and
`0.9.0`, while the repository contains `0.9.0` and `0.9.1`, and the normative
ledger count therefore differs. RCC002 is out of this audit's mutation scope;
the mismatch must be handled in a separate governed RCC002 correction.

A single all-at-once pytest attempt also encountered the known package-name
collision between `tests/rcc002` and `rcc002`. The authoritative suite-specific
`unittest` commands above avoid that collection ambiguity.

## 7. Controlled next sequence

1. Obtain read-only Claude and Antigravity reviews using the companion review
   packet and the exact code baseline above.
2. Reconcile findings into one decision register: `KEEP`, `REFACTOR`, `ARCHIVE`,
   or `REMOVE`, each with evidence and owner.
3. First cleanup wave: only confirmed orphan runners, `cost_guards.py`, the seed
   backup, and one completed research campaign. Move to a dated archive; do not
   delete.
4. Re-run live, regression, and the relevant subsystem tests.
5. Only then begin IU-4 implementation on a separate IU-4 branch.

## 8. Readiness estimate

The project is not merely 5% before first controlled trading operation. The
data/economics foundation and IU-3 shadow validation are substantially advanced,
but IU-4 persistence integration, restart proof, operational controls, code
consolidation, and later exchange/live safety remain. A defensible current
estimate is approximately **55–65% toward a first tightly controlled paper/live
implementation**, but only **35–45% toward unattended real-money operation**.
These are engineering-readiness estimates, not performance or profitability
claims.
