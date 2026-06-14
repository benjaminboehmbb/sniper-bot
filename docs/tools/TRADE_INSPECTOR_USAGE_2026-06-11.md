# TRADE INSPECTOR - USAGE GUIDE
Date: 2026-06-11

## Purpose

Trade Inspector is the primary post-trade analysis framework for Live L1.

Goals:

- Inspect individual trades
- Explain trade outcomes
- Analyze regime context
- Evaluate exit quality
- Generate aggregate intelligence
- Build ML-ready datasets
- Prevent dataset leakage
- Prepare future model training

The framework is designed for deterministic analysis and reproducible research.

-------------------------------------------------------------------------------

## Required Inputs

Archive:

- trades_l1.jsonl
- execution_audit.jsonl
- l1_paper.log

Market Data:

- data/l1_full_run.csv

-------------------------------------------------------------------------------

## Version History

### V1

Base trade inspection.

Features:

- trade extraction
- trade summaries
- audit context

### V1A

Quality assessment.

Features:

- quality score
- quality class
- positive factors
- negative factors

### V1B

Trade path layer.

Features:

- MFE
- MAE
- best price
- worst price
- bars held

### V1C

Counterfactual analysis.

Features:

- 15m
- 1h
- 4h
- 24h
- 72h
- 168h

Metrics:

- future return
- opportunity loss
- exit efficiency

### V1E

Diagnosis confidence layer.

Features:

- confidence
- evidence score
- impact score
- priority score

### V2

Regime context layer.

Features:

- entry regime
- exit regime
- ATR state
- MA200 state
- MFI state
- regime changes

### V2A

Stable Trade ID layer.

Format:

T_YYYYMMDD_HHMMSS_SIDE_SYMBOL

Example:

T_20170829_220900_LONG_BTCUSDT

Purpose:

- chart mapping
- deterministic references
- archive consistency

### V2B

Human Label layer.

Examples:

- otter
- trout
- salmon
- perch
- pike
- mullet

Rules:

- unique assignment
- never reused
- deterministic registry

Files:

config/trade_inspector/human_labels.txt

config/trade_inspector/trade_label_registry.csv

-------------------------------------------------------------------------------

## Aggregate Intelligence

### V3

Aggregate Intelligence Layer

Outputs:

- global summary
- regime performance
- risk performance
- root cause ranking
- improvement candidates

### V3A

Aggregate CSV Export

Output directory:

reports/trade_inspector/

### V3B

Root Cause Attribution

Purpose:

Quantify contribution of:

- early_exit
- entry_filter_quality
- risk_management
- high_adverse_move

### V3C

Trade Family Layer

Trade Family Group Examples:

- aligned_good_risk
- exit_risk_trap
- chop_context

Trade Family Examples:

- long_bull_good_atr_early_exit_aligned
- short_bear_good_atr_early_exit_aligned

-------------------------------------------------------------------------------

## Machine Learning Pipeline

### V4

ML Dataset Builder

Outputs:

- train
- validation
- test
- manifest

Targets:

- winner
- loser
- pnl
- pnl_pct
- quality
- future returns

### V4A

Split Quality Validation

Checks:

- split sizes
- train share
- validation share
- test share

Warnings:

- dataset too small
- empty validation split
- empty test split

### V4B

Feature Preparation

Outputs:

- encoded features
- model-ready dataset
- feature catalog

### V4C

Dataset Leakage Audit

Purpose:

Prevent future information leakage.

Blocked Examples:

- pnl
- pnl_pct
- future returns
- diagnosis outputs
- counterfactual outputs

Only pre-entry information should be used for future predictive models.

-------------------------------------------------------------------------------

## Feature Importance

### V5

Feature Importance Engine

Current Method:

- absolute Pearson correlation

Purpose:

Estimate predictive strength of:

- regime signals
- ATR state
- risk state
- family groups
- entry context

Current Status:

Research only.

Small datasets are not statistically reliable.

-------------------------------------------------------------------------------

## Standard Commands

Single Trade:

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir ARCHIVE \
  --market-csv data/l1_full_run.csv \
  --trade-index 1

Aggregate Report:

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir ARCHIVE \
  --market-csv data/l1_full_run.csv \
  --aggregate

Aggregate CSV Export:

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir ARCHIVE \
  --market-csv data/l1_full_run.csv \
  --export-aggregate-csv-dir reports/trade_inspector/output

Leakage Audit:

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir ARCHIVE \
  --market-csv data/l1_full_run.csv \
  --export-leakage-audit-dir data/ml/leakage_audit

Feature Importance:

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir ARCHIVE \
  --market-csv data/l1_full_run.csv \
  --export-feature-importance-dir data/ml/feature_importance

-------------------------------------------------------------------------------

## Interpretation Guidelines

High Opportunity Loss:

- exit likely too early

Low Exit Efficiency:

- exit quality poor

Good ATR + High Winrate:

- risk environment favorable

Bad ATR + Low Winrate:

- risk environment unfavorable

Regime Flip During Trade:

- potential source of losses

Trade Family Analysis:

- preferred method for pattern discovery

-------------------------------------------------------------------------------

## Current Limitation

Current archive:

- 9 trades

ML conclusions are NOT statistically reliable.

Use V5 outputs only for:

- framework validation
- pipeline testing
- feature sanity checks

Do not use for production model training.

-------------------------------------------------------------------------------

## Next Major Step

After Workstation runtime completes:

V5A Large Archive Evaluation

Goals:

- hundreds or thousands of trades
- stable statistics
- reliable feature importance
- family-level intelligence
- future ML model development

