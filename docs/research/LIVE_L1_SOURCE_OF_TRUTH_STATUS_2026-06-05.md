# LIVE L1 Source of Truth Status - 2026-06-05

## Ergebnis

Die Source of Truth fuer data/l1_full_run.csv ist aktuell nicht vollstaendig rekonstruierbar.

## Sicher bewiesen

allow_long = 1 entspricht exakt:

regime_v1 == 1

allow_short = 1 entspricht exakt:

regime_v1 == -1

Validierung:

long mismatches: 0

short mismatches: 0

## Nicht bewiesen

Die exakte Erzeugung von:

- regime_v1
- regime_v2
- 12 Signalspalten

ist nicht im aktiven Repository nachweisbar.

## Widerlegte Annahmen

Folgende Rekonstruktionen reproduzieren data/l1_full_run.csv nicht ausreichend:

- GS-kompatibler signal_builder.py
- aktueller regime_builder.py
- regime_v2_builder.py aus build_regime_v2_from_v1.py
- gate_builder.py auf Basis von regime_v2
- gs_build_asymmetric_gate.py als Gate-Quelle

## Entscheidung

Keine Integration der Online Builder in loop.py.

P1 Online Readiness bleibt blockiert, bis die echte Erzeugungskette von data/l1_full_run.csv gefunden wird.

## Sicherer Weiterarbeitsmodus

Erlaubt:

- Execution Engine verbessern
- Logging verbessern
- Audits schreiben
- Persistenz verbessern
- Analysewerkzeuge bauen

Nicht erlaubt:

- Online-Signale produktiv integrieren
- Online-Regime produktiv integrieren
- Online-Gates produktiv integrieren

## Fazit

Die aktuelle CSV bleibt Source of Truth fuer Paper-Betrieb.

Die Online-Rekonstruktion wird gestoppt, um keine unvalidierte Produktionslogik einzubauen.
