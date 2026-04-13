# Run Manifest (GS v2 candidate)

Purpose: Provide auditability for backtest runs without modifying engine/simtraderGS.py (GS v1 remains read-only).

Local template (not committed; results/ is gitignored):
- results/GS/meta/run_manifest_template.json

Intended use:
- External runner/tool writes a concrete manifest file per run:
  results/GS/meta/run_manifest_<UTC>.json

Minimum fields:
- git_commit, repo_root
- engine file sha256
- price_csv path, timestamp_col, window offset/rows
- direction, use_forward, enter_z/exit_z, tp/sl/max_hold
- fee_roundtrip, slippage_model (explicit 0 unless modeled)

Status:
- Template created locally on 2026-01-14
- No engine changes performed
# CURRENT WORKSTATE (MASTER ANALYSIS)

## CONTEXT
- Device: G15 (WSL)
- Project: Sniper-Bot (Master Analysis Blueprint)
- Ziel: funktionierende, robuste, reproduzierbare Strategieentwicklung

## DATA BASIS (VERBINDLICH)
- File: data/l1_full_run.csv
- Enthält:
  - Signals: *_signal (12 Stück)
  - Regime: regime_v2
  - Gates: allow_long, allow_short

## STATUS SIGNIFICANT FINDINGS

### 1. Frühere Fehlerursache
- Falsche Datei verwendet (price_data_with_signals.csv existiert hier nicht)
- Vermischung verschiedener Ansätze
→ RESULT: inkonsistente Runs / 0 Trades

### 2. Gate Analyse
- Global:
  - allow_long ≈ 30%
  - allow_short ≈ 27%
- Window (200k):
  - allow_long ≈ 45%
  - allow_short ≈ 36%
→ Gate funktioniert korrekt

### 3. Signalstruktur
- Signale vorhanden (-1 / 0 / +1)
- Score:
  - max: 6
  - min: -8
  - mean: ~0.88
→ ausreichend Dynamik vorhanden

### 4. Aktuelle Entry-Logik (intent.py)
FLAT:
- BUY → 3x score >= 1
- SELL → 3x score <= -1

LONG:
- SELL → 2x score <= -2

SHORT:
- BUY → 1x score >= 2

→ Logik ist NICHT zu streng

## CURRENT PROBLEM
- Trotz funktionierendem:
  - Gate
  - Signalbasis
  - Score-Verteilung

→ entstehen keine sinnvollen Trades in Analyse-Runs

## NEXT FOCUS
- Analysepfad vs L1-Logik strikt trennen
- prüfen:
  - wird intent.py überhaupt im Run verwendet?
  - nutzt analyze-Skript dieselbe Score-Logik?
  - existiert ein Mismatch zwischen:
    → Backtest-Logik vs Live-Intent-Logik

## RULES (VERBINDLICH)
- KEINE Vermischung von:
  - alten Runs
  - GS-Pfaden
  - anderen Datensätzen
- Jede Änderung wird hier dokumentiert
- Jeder Run basiert auf:
  - exakt definierter Datei
  - exakt definierter Logik

## CURRENT ACTIVE PATHS
- data_file: data/l1_full_run.csv
- intent_file: live_l1/core/intent.py
- manifest_file: docs/RUN_MANIFEST.md

## SCORE DIAGNOSTIC (CONFIRMED)
- Current score = simple sum of 12 signal columns
- Observed distribution is dense around -1..+3
- score >= 4 occurs 557457 times in data/l1_full_run.csv
- Conclusion:
  - current score is not selective enough
  - current score behaves like mass activity, not high-quality conviction
  - current intent trigger logic on top of this score cannot produce sniper-quality entries reliably

## DECISION
- Stop further threshold tweaking on current raw summed score
- Next step must be score redesign / signal normalization, not more minor parameter changes

## BREAKTHROUGH RUN (CONFIRMED)
- Data: data/l1_full_run.csv
- Score redesign:
  - removed raw sum of all 12 signals
  - new score uses only:
    - rsi_signal
    - bollinger_signal
    - stoch_signal
    - cci_signal
    - mfi_signal
- Result on 2000 ticks:
  - final_equity: 10523.97
  - total_pnl: 523.97
  - return_pct: 0.0524
  - num_trades: 38
  - winrate: 0.7368
  - profit_factor: 2.8151
  - max_drawdown_pct: 0.0136
- Conclusion:
  - entry/timing-only score is the first confirmed positive direction
  - raw full-signal sum should remain abandoned

## VALIDATION RUN (5000 TICKS)
- Result:
  - final_equity: 10723.80
  - total_pnl: 723.80
  - return_pct: 0.0724
  - num_trades: 86
  - winrate: 0.6628
  - profit_factor: 1.6555
  - max_drawdown_pct: 0.0218
- Interpretation:
  - strategy remains profitable on extended window
  - edge persists beyond initial 2000-tick test
  - degradation vs 2000-tick run is expected and acceptable

## VALIDATION RUN (10000 TICKS)
- Result:
  - final_equity: 12220.86
  - total_pnl: 2220.86
  - return_pct: 0.2221
  - num_trades: 148
  - winrate: 0.7027
  - profit_factor: 2.2842
  - max_drawdown_pct: 0.0315
- Interpretation:
  - strong and stable profitability confirmed
  - performance improves with longer sample
  - entry-signal-only approach validated as core design

## VALIDATION RUN (10000 TICKS, OFFSET 50000)
- Data: data/l1_full_run_offset_50k_with_header.csv
- Result:
  - final_equity: 11424.13
  - total_pnl: 1424.13
  - return_pct: 0.1424
  - num_trades: 143
  - winrate: 0.7273
  - profit_factor: 2.4477
  - max_drawdown_pct: 0.0169
- Interpretation:
  - profitability confirmed on shifted data segment
  - entry-signal-only design shows robustness beyond first window
