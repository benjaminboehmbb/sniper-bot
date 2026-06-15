# TRADE INSPECTOR COMMAND REFERENCE

Date: 2026-06-14

Current source of truth:

tools/trade_inspector/inspect_trades.py

Current architecture version:

V7F

---

# STANDARD VARIABLES

Archive:

live_logs/archive/P79A_pre_run_2026-06-10

Market data:

data/l1_full_run.csv

---

# BASIC INSPECTION

## Single Trade Report

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --trade-index 1

---

## Trade Summary

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --summary

---

## Aggregate Intelligence

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --aggregate

---

# V4 ML DATASET EXPORTS

## V4 ML CSV

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-ml-csv data/ml/trade_inspector_v4/trades.csv

---

## V4A ML Dataset

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-ml-dataset-dir data/ml/trade_inspector_v4

---

## V4B Feature Preparation

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-feature-prep-dir data/ml/trade_inspector_v4b

---

## V4C Leakage Audit

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-leakage-audit-dir data/ml/trade_inspector_v4c

---

# V5 FEATURE ANALYSIS

## V5 Feature Importance

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-feature-importance-dir data/ml/trade_inspector_v5

---

## V5C Feature Stability

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-feature-stability-dir data/ml/trade_inspector_v5c

---

# V6 SIGNAL DISCOVERY

## V6 Predictive Signal Discovery

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-signal-discovery-dir data/ml/trade_inspector_v6

---

## V6A Reliability Layer Validation

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-signal-discovery-dir outputs/trade_inspector/v6a/P79A_2026-06-14

---

# V7 CROSS-ARCHIVE INTELLIGENCE

Required archive id:

--archive-id P79A_pre_run_2026-06-10

---

## V7C Global Trade Database

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-global-trades-dir outputs/trade_inspector/v7/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

---

## V7D Cross-Archive Root Cause

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-cross-archive-root-cause-dir outputs/trade_inspector/v7d/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

---

## V7E Cross-Archive Feature Importance

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-cross-archive-feature-importance-dir outputs/trade_inspector/v7e/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

---

## V7F Cross-Archive Signal Discovery

python3 tools/trade_inspector/inspect_trades.py \
  --archive-dir live_logs/archive/P79A_pre_run_2026-06-10 \
  --market-csv data/l1_full_run.csv \
  --export-cross-archive-signal-discovery-dir outputs/trade_inspector/v7f/P79A_2026-06-14 \
  --archive-id P79A_pre_run_2026-06-10

---

# CURRENT STATUS

Completed:

- V1
- V2
- V3
- V4
- V5
- V5C
- V6
- V6A
- V7A
- V7B
- V7C
- V7D
- V7E
- V7F

Current bottleneck:

- archive count
- trade count

Current reference archive:

P79A_pre_run_2026-06-10

Current trade count:

9

Current development device:

G15 / AR15

Current runtime device:

Workstation
