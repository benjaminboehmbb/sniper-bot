# Pre-IU-4 Independent Review Packet

Date: 2026-08-09

Read-only review target: `263049df549cc9c9ef2698c983cd0b87590f596b`

Audit branch: `codex/pre-iu4-quality-audit-2026-08-09`

## Rules for both reviewers

- Review only; do not edit, format, move, delete, stage, or commit files.
- Do not inspect or rely on the untracked user-owned file
  `scripts/build_rcc002_spec_bundle.py`.
- IU-4, Exchange access, and Live activation remain locked.
- Static zero-import status is not proof of dead code; account for CLI,
  scheduled, dynamically loaded, and research entrypoints.
- Every finding must contain: severity, exact path and line, evidence or
  reproduction, consequence, and the smallest safe correction.
- Use severities `BLOCKER`, `HIGH`, `MEDIUM`, or `LOW`; return `NO FINDING` when
  a reviewed area is sound.

## Shared primary scope

```text
live_l1/
scripts/run_live_l1_paper.py
config/pee/
tests/live_l1/
docs/LIVE_PAPER_ECONOMICS_*V1.md
docs/review/PRE_IU4_REPOSITORY_QUALITY_AUDIT_2026-08-09.md
```

Pay particular attention to:

```text
live_l1/state/paper_account.py
live_l1/state/paper_artifacts.py
live_l1/core/paper_economics.py
live_l1/core/paper_economics_shadow.py
live_l1/core/paper_economics_shadow_runtime.py
live_l1/guards/cost_guards.py
live_l1/core/gate_builder.py
live_l1/core/regime_builder.py
live_l1/core/regime_v2_builder.py
live_l1/core/signal_builder.py
```

## Claude review mandate

Evaluate correctness and operational/economic safety:

1. Decimal and unit consistency across quote, fees, PnL, equity, loss, and
   drawdown.
2. Persistent-account invariants, idempotency, identity/parity, atomic writes,
   restart/recovery, duplicate event handling, and partial/corrupt artifacts.
3. Whether every entry has one authoritative profile-bound guard and stable
   reason codes.
4. Whether SHADOW-to-IU-4 promotion can alter existing intent, S2/S4, execution,
   or Live behavior before explicit authorization.
5. Whether `cost_guards.py` contains any safety rule that is absent from the new
   guard, or instead creates a conflicting second source of truth.
6. Missing boundary, failure-injection, or restart tests required before IU-4.

Return a final verdict: `READY_FOR_IU4_DESIGN`, `READY_WITH_CONDITIONS`, or
`NOT_READY`, followed by the ordered prerequisites.

## Antigravity review mandate

Evaluate architecture, minimalism, and repository order:

1. Map the actual IU-4 dependency closure and identify duplicated abstractions,
   parallel sources of truth, unreachable code, and unnecessary indirection.
2. Validate the proposed classifications `KEEP_REQUIRED_IU4`,
   `KEEP_FUTURE_ISOLATED`, and `ARCHIVE_CANDIDATE_AFTER_REVIEW`.
3. Determine whether the four online builders are cleanly isolated from IU-4.
4. Review the two apparent SSI orphan runners:
   `tools/ssi/decision_engine/decision_engine_runner.py` and
   `tools/ssi/decision_evidence/decision_evidence_runner.py`, including dynamic
   and documented consumers.
5. Assess the 104-file `tools/ssi/` and 53-file `tools/trade_inspector/` surfaces
   for missing tests, duplicated framework code, and consolidation boundaries.
6. Propose the smallest campaign-level archive wave for
   `scripts/state_research/`; preserve reproducibility and provenance.

Return a final verdict: `MINIMAL_ENOUGH_FOR_IU4`, `CONSOLIDATE_BEFORE_IU4`, or
`ARCHITECTURAL_BLOCKER`, followed by an exact file decision table.

## Required output template

```text
Reviewer/tool and version:
Reviewed commit:
Verdict:

Findings:
- [SEVERITY] Title
  Path: exact/path.py:line
  Evidence/reproduction:
  Consequence:
  Smallest safe correction:

File decisions:
- exact/path.py — KEEP | REFACTOR | ARCHIVE | REMOVE — reason

Prerequisites before IU-4:
1. ...

Explicitly reviewed with no finding:
- ...
```

## Reconciliation rule

No reviewer recommendation is applied automatically. Conflicting decisions are
resolved against repository evidence, tests, accepted PEE documents, and the
smallest reversible change. Archive precedes deletion; a removal requires a
separate explicit decision and green post-change verification.
