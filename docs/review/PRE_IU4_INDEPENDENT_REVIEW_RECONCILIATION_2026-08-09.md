# Pre-IU-4 Independent Review Reconciliation

Date: 2026-08-09

Code baseline: `263049df549cc9c9ef2698c983cd0b87590f596b`

Inputs:

- `PRE_IU4_REPOSITORY_QUALITY_AUDIT_2026-08-09.md`
- `PRE_IU4_CLAUDE_INDEPENDENT_REVIEW_2026-08-09.md`
- `PRE_IU4_ANTIGRAVITY_INDEPENDENT_REVIEW_2026-08-09.md`

Unified verdict: **NOT READY TO START IU-4 IMPLEMENTATION**

This verdict is caused by one confirmed active-runtime safety blocker and two
high-priority design decisions. It is not a rejection of the accepted IU-3
economics work, which both independent reviews classified as keep/required.

## Reconciled decisions

| Item | Local audit | Claude | Antigravity | Final decision |
|---|---|---|---|---|
| PEE economics/account/artifacts | KEEP_REQUIRED_IU4 | KEEP | KEEP_REQUIRED_IU4 | KEEP_REQUIRED_IU4 |
| Four online builders | KEEP_FUTURE_ISOLATED | KEEP | KEEP_FUTURE_ISOLATED | KEEP_FUTURE_ISOLATED |
| `cost_guards.py` | ARCHIVE_CANDIDATE_AFTER_REVIEW | REFACTOR | migrate protections, then archive | REFACTOR_FIRST; ARCHIVE_LATER |
| Two SSI orphan runners | ARCHIVE_CANDIDATE_AFTER_REVIEW | outside mandate | ARCHIVE_CANDIDATE | ARCHIVE_AFTER_PROVENANCE_MANIFEST |
| Step-18 research campaign | REVIEW_BY_CAMPAIGN | outside mandate | ARCHIVE | ARCHIVE_AFTER_DEPENDENCY_MANIFEST |
| SSI/Trade Inspector surfaces | REVIEW_HIGH_RISK | outside mandate | CONSOLIDATE/TEST | SEPARATE CONSOLIDATION TRACK |
| Pre-execution guard | not identified in initial inventory | BLOCKER | no disagreement | FIX BEFORE IU-4 |

## Locally reproduced facts

### Confirmed safety blocker

`live_l1/core/loop.py` calls `apply_paper_execution()` before
`evaluate_guards()`. The latter only updates/logs the kill level after the
execution call. Repository search found no caller of the enforcing
`apply_guards()` function. Therefore `gate_mode=closed` and an existing HARD or
EMERGENCY level do not enforce a pre-execution denial in the active loop.

### Confirmed orphan candidates

Repository-wide search found the two SSI runner class definitions and June
progress-document mentions, but no import, instantiation, CLI entrypoint, or
runtime consumer. This is sufficient for a dated archive move after a manifest;
it is not grounds for irreversible deletion.

### Confirmed test gap, with precise wording

No Python test under `tests/` references SSI, Trade Inspector, either runner, or
their package imports. This is a static test-reachability finding; it does not
claim measured line coverage from a coverage tool.

### Step-18 dependency caution

Later Step-19 and Step-20 research scripts consume files under
`reports/step18/`. The five Step-18 scripts may be archived as a coherent
campaign, but their scripts, inputs, outputs, hashes, and downstream report-path
dependencies must be recorded together. Moving only the scripts without a
manifest would weaken reproducibility.

## Required order of work

1. Create a dedicated safety-fix branch from the reviewed code baseline.
2. Enforce the authoritative guard before `apply_paper_execution()` and add
   denial tests for `closed`, HARD, and EMERGENCY.
3. Decide the profile-bound replacement for daily/6-hour rate limits and
   cooldown behavior.
4. Specify the float-execution to Decimal-PEE ownership transition.
5. Add the two medium restart-safety corrections identified by Claude.
6. Re-run live and regression suites; keep Exchange and Live locked.
7. Create a separate cleanup branch for the two SSI runners and Step-18 campaign
   archive, each with provenance manifests and post-move verification.
8. Start IU-4 only after the safety/design gates above are closed.

## Deletion policy

No file is approved for immediate deletion. Confirmed legacy assets move first
to a dated archive. Deletion, if ever justified, requires a later explicit
decision after hashes, provenance, and green verification exist.
