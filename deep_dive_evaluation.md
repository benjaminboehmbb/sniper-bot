# Deep-Dive (Long) – Auswertung

## 1. Datengrundlage
- Ordner: deep_out_7A
- Dateien: strategy_results*.csv, metrics*.csv, combined_*, errors_*

## 2. Auswahl-Kriterien (Version 1)
- num_trades ≥ __
- Winrate (Wilson 95% Lower Bound) ≥ __
- ROI > 0 bei Fees=__, Slippage=__
- Zeit-Slice-Stabilität: __
- Regime-Stabilität: __
- Max Drawdown ≤ __
- Kosten-Stresstest: __

## 3. Ranking (Top N)
- Tabelle mit Spalten: id, Combination, ROI, num_trades, winrate, accuracy

## 4. Stabilitätschecks
- Monats-Heatmap
- Rolling-Winrate
- Nachbarschaft (±10% Weights)

## 5. Risiko-Kennzahlen
- MaxDD, ROI/MaxDD, ggf. Sharpe (falls Renditeserie vorhanden)

## 6. Kosten/Slippage-Sensitivität
- Baseline vs. +50%

## 7. Erkenntnisse & Entscheidungen
- Kandidatenliste (A/B/C)
- “No-Gos” & Gründe
- Offene Fragen
