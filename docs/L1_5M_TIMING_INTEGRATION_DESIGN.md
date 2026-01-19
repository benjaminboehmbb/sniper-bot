# L1 Integration Design: 5m Timing Cores (BTCUSDT)

Datum: 2026-01-19
Scope: L1 Paper-Trading Architektur (read-only Design)
Status: DRAFT v1 (Design, kein Code)

## Ziel

Die qualifizierten 5m Timing-Cores (LONG/SHORT) sollen in L1 als read-only Entscheidungsbausteine
integriert werden, ohne die GS-Engine oder die qualifizierten Core-Definitionen zu veraendern.

## Inputs (read-only)

A) 5m Timing Core (SHORT)
- docs/5M_TIMING_CORE_SHORT.md
- seeds/5m/btcusdt_5m_short_timing_core_v1.csv

B) 5m Timing Core (LONG)
- docs/5M_TIMING_CORE_LONG.md
- seeds/5m/btcusdt_5m_long_timing_core_v1.csv

C) Dataset / Time-Standard
- TIME_STANDARD.md ist verbindlich
- 5m Daten entstehen aus 1m (Builder v1.0) und sind GS-kompatibel

## Grundprinzip (Integration ohne Vermischung)

- 1m bleibt Generalist (Trend/Mix, GS-Kern).
- 5m bleibt Spezialist (Timing / Mean-Reversion).
- In L1 werden Signale getrennt berechnet und erst in einem Meta-Schritt zusammengefuehrt.

## L1 Datenfluss (konzeptionell)

1) Market Data Ingest (1m)
- L1 nutzt 1m Ticks als primären Loop-Takt.

2) 5m Aggregation (online)
- L1 aggregiert intern 1m -> 5m Bars (OHLC + Volume sum).
- Signals werden pro 5m Bar berechnet (RSI, STOCH, MFI) im gleichen Domain-Format wie GS.
- Regime/allow_long/allow_short werden aus den vorhandenen Labels genutzt (oder in L1 repliziert),
  aber Gate-Mode bleibt konzeptionell "auto".

3) Timing-Core Scoring (5m)
- Fuer LONG: evaluiere alle Seeds aus btcusdt_5m_long_timing_core_v1.csv
- Fuer SHORT: evaluiere alle Seeds aus btcusdt_5m_short_timing_core_v1.csv
- Output ist ein "timing_vote" pro Richtung:
  - best_seed_id
  - vote_strength (z.B. normalisiert 0..1)
  - vote_direction in {long, short, none}

4) Meta-Decision (1m + 5m)
- 5m Vote ist ein Filter/Confirmation fuer 1m Intents.
- Beispiel-Regel (nur Design):
  - L1 erzeugt Intent aus 1m.
  - Wenn Intent=BUY, dann nur zulassen wenn 5m LONG vote_strength >= threshold und allow_long==1.
  - Wenn Intent=SELL, dann nur zulassen wenn 5m SHORT vote_strength >= threshold und allow_short==1.
  - Wenn beide Richtungen gleichzeitig stark sind: "none" (no-trade) oder Prioritaetsregel.

5) Guards/Cost Controls (bestehend)
- existing guards bleiben unveraendert (cooldowns, daily limits, rolling 6h).
- 5m Integration darf keine Guard-Bypasses erzeugen.

## Schnittstellen (minimal)

- TimingEngine.evaluate_5m(bar_5m) -> TimingVote
- MetaDecision.merge(intent_1m, timing_vote, allow_flags) -> intent_final

Diese Schnittstellen sind konzeptionell; konkrete Implementierung folgt erst nach Design-Review.

## Determinismus & Logging

- Jede L1 Entscheidung loggt:
  - timestamp_utc
  - intent_1m_raw
  - timing_vote (direction, strength, seed_id)
  - allow_long/allow_short flags
  - intent_final + reason_code
- Ziel: Nachvollziehbarkeit und spätere Auditfaehigkeit.

## Safety / Governance

- Die qualifizierten Timing-Cores sind read-only.
- Aenderungen nur ueber neue Versionen (v2...) + Qualifizierung.
- Kein Parallel-Run und keine Code-Aenderung waehrend aktiver L1 Runs.

