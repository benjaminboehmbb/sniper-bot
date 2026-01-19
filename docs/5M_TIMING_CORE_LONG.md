# 5m Timing Core (LONG) - QUALIFIED v1

Datum: 2026-01-19
Instrument: BTCUSDT
Timeframe: 5m
Engine: tools.gs_run_with_manifest (gate=auto) + engine/simtraderGS.py
Status: QUALIFIED (robust, reproduzierbar)

## Zweck

Dieser Core definiert einen spezialisierten 5m-Oszillator/Timing-Pfad fuer LONG.
Er ist als stabiler, reproduzierbarer Alpha-Baustein gedacht und dient als Grundlage fuer:
- 5m Timing Research (weiterfuehrende Kombinationen nur kontrolliert)
- spaetere Ensemble-/Meta-Integration neben dem 1m-Generalistenpfad
- spaetere L1/L2-Planung (read-only Nutzung der Ergebnisse)

## Dataset

Verwendeter 5m GS-Datensatz (FROM 1m, GS-kompatibel):
archive/POST_GS_5m_2026-01-14/btcusdt_5m_2026-01-07/simtraderGS/btcusdt_5m_price_2017_2025_GS_FROM_1m_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv

Zeitstandard:
- TIME_STANDARD.md ist verbindlich (ns intern / timestamp_utc operativ)

## Fixe Run-Parameter (Baseline)

- direction: long
- gate: auto (mandatory)
- fee_roundtrip: 0.0004
- tp/sl: 0.04 / 0.02
- max_hold_bars: 288
- enter_z: 1.0
- exit_z: 0.0
- preflight_rows: 200000
- preflight_offset: 0

## Seed-Core Definition (v1)

Quelle:
seeds/5m/btcusdt_5m_long_timing_core_v1.csv

Seeds:
- C01_rsi_stoch_06  : {'rsi': 0.6, 'stoch': 0.6}
- C02_rsi_stoch_08  : {'rsi': 0.8, 'stoch': 0.8}

## Qualifizierung - Befunde

A) Reproduzierbarkeit
- Seed-Replay (LONG) ist deterministisch und reproduziert Ergebnisse bit-identisch.

B) TP-Robustheit (tp in {0.03, 0.04, 0.05} bei sl=0.02)
- Beide Seeds bleiben positiv (ROI>0, Sharpe>0).
- Plateau zwischen 0.04 und 0.05, leicht besser bei 0.03.

C) Hold-Robustheit (max_hold in {192, 288, 384} bei tp/sl=0.04/0.02)
- Ergebnisse sind invariant: ROI/Trades/Sharpe/Winrate unveraendert.
- Schluss: max_hold ist praktisch nicht bindend (Exits ueber TP/SL/Exit-Logik).

## Regeln (verbindlich)

- Dieser Core ist read-only (kein stilles Aendern der Seeds oder Baseline-Parameter).
- Erweiterungen erfolgen nur ueber neue Versionen (v2, v3 ...) und muessen separat qualifiziert werden.
- Der LONG-Core ist bewusst klein gehalten (2 Seeds) zur Vermeidung von Verwässerung.

