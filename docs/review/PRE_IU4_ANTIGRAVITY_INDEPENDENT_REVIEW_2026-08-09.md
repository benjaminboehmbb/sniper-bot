# Pre-IU-4 Antigravity Independent Review

Date: 2026-08-09

Reviewer/tool: Antigravity CLI 1.1.11, Gemini 3.1 Pro (High)

Reviewed code commit: `263049df549cc9c9ef2698c983cd0b87590f596b`

Audit context commits: `ea19fa75931b83a8409f4c36f7ec9bec27f96b3d`,
`7d21bbf`

Verdict: **CONSOLIDATE_BEFORE_IU4**

## Review controls

Antigravity ran in plan and terminal-sandbox mode. The project permission set
was limited to repository reads and named read-only inspection commands. The
untracked user-owned file `scripts/build_rcc002_spec_bundle.py` was explicitly
excluded. No repository file was modified by Antigravity.

Optional interaction-data collection was disabled during first-run setup. The
user explicitly approved external read-only transmission to Antigravity.

## Findings

### 1. MEDIUM — unconsolidated, testless analysis/framework surfaces

Path: `tools/ssi/decision_engine/decision_engine_runner.py:12`

The 104-file `tools/ssi/` and 53-file `tools/trade_inspector/` surfaces contain
no local `test_*.py` modules. Antigravity found no repository consumer for:

- `tools/ssi/decision_engine/decision_engine_runner.py`
- `tools/ssi/decision_evidence/decision_evidence_runner.py`

Consequence: unnecessary maintenance surface and probable dead framework code.

Recommendation: archive the two orphan runners after recording provenance and
define consolidation/test boundaries for the remaining two tool surfaces.

### 2. MEDIUM — conflicting cost-guard source of truth

Paths:

- `live_l1/guards/cost_guards.py:28`
- `live_l1/guards/cost_guards.py:30`
- `live_l1/state/paper_artifacts.py:773`

Hard-coded floats and trade limits in `cost_guards.py` conflict with the newer
Decimal, profile-bound guard authority. Antigravity independently agrees with
Claude that daily/6-hour trade caps and cooldown protection must not disappear
when the legacy file is retired.

Recommendation: migrate or explicitly supersede those protections before
archiving `cost_guards.py`.

## File decisions

| Path | Antigravity decision | Reason |
|---|---|---|
| `live_l1/core/paper_economics.py` | KEEP_REQUIRED_IU4 | Required Decimal economics authority. |
| `live_l1/state/paper_account.py` | KEEP_REQUIRED_IU4 | Required persistent-account transition logic. |
| `live_l1/state/paper_artifacts.py` | KEEP_REQUIRED_IU4 | Required versioned account/trade artifacts. |
| `live_l1/core/gate_builder.py` | KEEP_FUTURE_ISOLATED | Cleanly isolated future online builder. |
| `live_l1/core/regime_builder.py` | KEEP_FUTURE_ISOLATED | Cleanly isolated future online builder. |
| `live_l1/core/regime_v2_builder.py` | KEEP_FUTURE_ISOLATED | Cleanly isolated future online builder. |
| `live_l1/core/signal_builder.py` | KEEP_FUTURE_ISOLATED | Cleanly isolated future online builder. |
| `tools/ssi/decision_engine/decision_engine_runner.py` | ARCHIVE_CANDIDATE | No static or dynamic consumer identified. |
| `tools/ssi/decision_evidence/decision_evidence_runner.py` | ARCHIVE_CANDIDATE | No static or dynamic consumer identified. |
| Five Step-18 research scripts | ARCHIVE_CAMPAIGN_CANDIDATE | Smallest coherent historical research wave. |

The five proposed Step-18 scripts are:

- `scripts/state_research/analyze_step18_buckets.py`
- `scripts/state_research/analyze_step18_clusters.py`
- `scripts/state_research/analyze_step18_predictive_power.py`
- `scripts/state_research/analyze_step18_trade_lifetime.py`
- `scripts/state_research/build_step18_core_pipeline.py`

## Agreements with Claude

- Do not archive `cost_guards.py` before preserving or deliberately replacing
  its rate/cooldown protections.
- Keep `paper_account.py`, `paper_artifacts.py`, and `paper_economics.py`.
- Keep the four online builders isolated for future use.
- No disagreement was reported regarding Claude's active-execution or
  persistence findings; they were outside Antigravity's assigned minimalism
  mandate.

## Antigravity prerequisites before IU-4

1. Preserve provenance and archive the completed Step-18 campaign as the first
   minimal research wave.
2. Archive the two confirmed orphan SSI runners.
3. Migrate or supersede rate/cooldown protections before retiring
   `cost_guards.py`.
4. Define consolidation and test boundaries for SSI and Trade Inspector.

## Explicitly reviewed without a finding

- `live_l1/core/gate_builder.py`
- `live_l1/core/regime_builder.py`
- `live_l1/core/regime_v2_builder.py`
- `live_l1/core/signal_builder.py`

All four remain outside the active runtime dependency closure.
