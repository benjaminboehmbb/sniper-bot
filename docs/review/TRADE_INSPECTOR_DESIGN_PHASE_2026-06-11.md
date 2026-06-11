# TRADE INSPECTOR DESIGN PHASE

Date: 2026-06-11

## Objective

Design a precise Trade Inspector for detailed post-trade analysis.

The purpose is to understand every trade in detail, prevent hidden logic errors, and enable targeted strategy improvements.

This phase is design only.

No runtime code changes.

## Core Principle

Every trade must become explainable.

For each trade, the inspector should answer:

- Why did the trade open?
- Why did it close?
- Which signals were active?
- Which regime was active?
- Was the trade technically valid?
- Was the trade strategically useful?
- Did the trade reveal a weakness?

## Initial Scope

Target module:

tools/trade_inspector/

Initial mode:

CLI-based analysis

No GUI.

No HTML.

No charts in the first version.

## Primary Inputs

Required files:

- live_logs/trades_l1.jsonl
- live_logs/execution_audit.jsonl
- live_logs/l1_paper.log
- data/l1_full_run.csv
- seeds/5m/btcusdt_5m_timing_core_v2.csv

Optional later:

- passive_shadow_risk_snapshots.csv
- passive_shadow_entry_multipliers.csv
- passive_shadow_close_accounting.csv
- trade_lifecycle_snapshots.csv

## Trade Selection

Supported selection modes:

- by trade index
- by entry timestamp
- by exit timestamp
- by side
- by worst PnL
- by best PnL
- by time range

First implementation should support:

- trade index
- worst trades
- best trades

## Required Output Per Trade

For each selected trade, output:

- trade index
- side
- entry timestamp
- exit timestamp
- duration
- entry price
- exit price
- pnl
- exit reason

## Required Context At Entry

At entry timestamp, show:

- snapshot id
- price
- allow_long
- allow_short
- intent_1m_raw
- intent_final
- reason_code
- vote_5m_direction
- vote_5m_seed_id
- vote_5m_strength
- regime_label
- risk_label
- entry_score
- ma200_signal
- atr_signal
- mfi_signal

## Required Context At Exit

At exit timestamp, show:

- action
- reason
- position_before
- position_after
- entry_price
- exit price
- exit timestamp
- exit reason

## Required Quality Flags

The inspector should flag:

- missing audit entries
- missing entry context
- missing exit context
- inconsistent timestamps
- negative duration
- unexpected position transition
- trade without matching audit events
- audit events without matching trade
- suspicious short duration
- suspicious long duration
- large loss
- repeated loss cluster

## Analysis Categories

Each trade should be classified into one of these categories:

- clean_winner
- clean_loser
- technical_issue
- regime_mismatch
- weak_entry
- weak_exit
- time_stop_case
- loss_cluster_case
- needs_manual_review

## First Version Deliverables

Create later:

tools/trade_inspector/inspect_trades.py

Expected CLI examples:

python3 tools/trade_inspector/inspect_trades.py --trade-index 17

python3 tools/trade_inspector/inspect_trades.py --worst 10

python3 tools/trade_inspector/inspect_trades.py --best 10

## Output Format

First version:

plain text

Later versions:

- CSV summary
- Markdown report
- HTML report
- chart-based trade view

## Design Constraints

ASCII-only.

No emojis.

No runtime mutation.

Read-only analysis.

No changes to live logs.

No changes to live state.

No assumptions without file evidence.

## Risk Avoidance

The inspector must never modify:

- live_logs/
- live_state/
- data/
- seeds/

The tool is strictly read-only.

## Recommended Build Sequence

Step 1:

Parse trades_l1.jsonl.

Step 2:

Parse execution_audit.jsonl.

Step 3:

Match each trade to entry and exit audit events.

Step 4:

Extract entry and exit context.

Step 5:

Print one detailed trade report.

Step 6:

Add best/worst ranking.

Step 7:

Add quality flags.

Step 8:

Add markdown export.

## Acceptance Criteria

The first working version is accepted only if:

- it reads trades correctly
- it matches audit events correctly
- it explains entry and exit
- it detects missing context
- it is read-only
- it produces deterministic output
- it runs on archived P79A artifacts

## Initial Test Dataset

Use archived P79A completed artifacts:

live_logs/archive/P79A_completed_2026-06-11/

Primary files:

- trades_l1.jsonl
- execution_audit.jsonl
- l1_paper.log

This avoids touching the currently active P82 runtime.

## Conclusion

Trade Inspector Design Phase started.

This tool is considered strategically important for future error prevention, trade quality review, and targeted strategy improvement.
