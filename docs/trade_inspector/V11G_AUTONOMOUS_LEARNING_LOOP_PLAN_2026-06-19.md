# V11G AUTONOMOUS LEARNING LOOP PLAN

Date: 2026-06-19
Device: G15 / Workstation
Environment: WSL
Scope: Trade Inspector V11G

## Objective

V11G coordinates the complete V11 learning pipeline.

V11A evaluates replay results.
V11B updates validation evidence.
V11C builds the research knowledge base.
V11D checks knowledge consistency.
V11E tracks knowledge evolution.
V11F prioritizes hypotheses.
V11G orchestrates the full loop.

## Input

Primary input:

- v10f_replay_execution_results.csv

## Output

- V11A output directory
- V11B output directory
- V11C output directory
- V11D output directory
- V11E output directory
- V11F output directory
- v11g_autonomous_learning_loop_manifest.csv
- V11G_AUTONOMOUS_LEARNING_LOOP_REPORT_2026-06-19.md

## Execution Rules

- Run V11A first.
- Run V11B only if V11A succeeds.
- Run V11C only if V11B succeeds.
- Run V11D and V11E after V11C.
- Run V11F only if V11D and V11E succeed.
- Stop on failed required step.

## Guardrail

V11G does not modify strategy logic.
V11G does not execute replay.
V11G only coordinates the V11 learning pipeline.

