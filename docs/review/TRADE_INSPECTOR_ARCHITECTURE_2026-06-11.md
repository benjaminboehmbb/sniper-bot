# TRADE INSPECTOR ARCHITECTURE

Date: 2026-06-11

## Objective

Define the architecture for a high-value Trade Inspector system.

The tool must support:

- human trade review
- systematic strategy improvement
- error prevention
- structured ML dataset generation
- future AI-assisted trade analysis

## Core Design Goal

The Trade Inspector must not only display trades.

It must make trades explainable, comparable and learnable.

## Architecture Levels

### Level 1

Trade Inspector

Purpose:

Explain individual trades.

Main question:

Why did this trade happen?

### Level 2

Trade Analytics

Purpose:

Compare groups of trades.

Main question:

Which recurring patterns exist?

### Level 3

Trade Intelligence

Purpose:

Derive improvement hypotheses.

Main question:

What should be changed or reviewed?

### Level 4

Trade Learning

Purpose:

Prepare structured data for ML and AI models.

Main question:

What can future models learn from the trade history?

## Human Output

Human reports must be optimized for:

- clarity
- practical review
- decision support
- error detection
- strategy improvement

Output formats:

- terminal text
- markdown report
- later HTML report

## Machine Output

Machine datasets must be optimized for:

- completeness
- reproducibility
- structured learning
- feature expansion
- downstream ML

Output formats:

- CSV
- JSONL
- Parquet later

## Required Data Layers

### Layer 1

Trade Summary

One row per trade.

Contains:

- trade index
- side
- entry time
- exit time
- duration
- entry price
- exit price
- pnl
- exit reason

### Layer 2

Entry Context

Contains:

- signals
- regime
- intent
- 5m vote
- score
- allow_long
- allow_short

### Layer 3

Exit Context

Contains:

- exit action
- exit reason
- position transition
- realized pnl
- trade duration

### Layer 4

Trade Path

Contains:

- MFE
- MAE
- max favorable move
- max adverse move
- price path during trade

### Layer 5

Pre-Trade Context

Windows:

- 1h before entry
- 6h before entry
- 24h before entry

Purpose:

Understand market setup.

### Layer 6

Post-Trade Context

Windows:

- 1h after exit
- 6h after exit
- 24h after exit
- 48h after exit

Purpose:

Evaluate exit quality.

## First Build Scope

V1 must be read-only.

V1 must use archived P79A artifacts.

No live runtime files should be modified.

Initial source:

live_logs/archive/P79A_completed_2026-06-11/

## Acceptance Criteria

V1 is accepted only if it can:

- load trades
- load audit events
- match entry and exit events
- explain one selected trade
- list best trades
- list worst trades
- detect missing audit context
- write no runtime state
- produce deterministic output

## Build Order

1. Create folder structure.

2. Implement trade loader.

3. Implement audit loader.

4. Implement trade-to-audit matcher.

5. Implement single-trade report.

6. Implement best/worst ranking.

7. Add quality flags.

8. Add machine dataset export.

9. Add markdown report export.

10. Add neighbourhood analysis.

## Future Extensions

Planned later:

- HTML report
- chart view
- trade clustering
- counterfactual exits
- ML feature dataset
- AI-assisted trade diagnosis

## Conclusion

This architecture defines the Trade Inspector as a long-term analysis and learning system.

It is a strategic tool for understanding trades, preventing repeated mistakes and improving the Sniper-Bot systematically.
