# TIME STANDARD POLICY (verbindlich)

Status: BINDING (GS + L1)
Gilt fuer: Datenimport, Dataset-Build (1m/5m/15m), GS-Runs, L1 Paper/Live
Ziel: Ein einheitlicher, zukunftssicherer Zeitstandard (ms/us/ns) ohne stille Fehler.

## 1) Grundprinzip (Two-Layer Standard)

Wir verwenden zwei Zeitebenen:

A) Data Layer (Rohdaten / interne Normalform)
- Format: int64 Nanosekunden seit Unix Epoch (UTC)
- Feldname: timestamp_ns
- Zweck: verlustfreie Normalisierung und zukunftssichere Verarbeitung (ms/us/ns)

B) Ops Layer (GS / L1 / Logs / CSV-Outputs)
- Format: ISO-8601 UTC, Sekundenaufloesung
- Feldname: timestamp_utc
- Beispiel: 2026-01-19T07:36:36Z
- Zweck: stabile, lesbare, deterministische Auswertung und Logs

Regel:
- Alle Resampling-/Aggregation-Operationen muessen auf timestamp_ns basieren.
- Alle GS/L1-CSV-Dateien muessen timestamp_utc enthalten (verbindlich).
- timestamp_ns darf optional zusaetzlich enthalten sein (Debug/Tracing), ist aber nicht Pflicht.

## 2) Import-Normalisierung (verbindlich)

Eingangstimestamps koennen in ms, us oder ns vorliegen. Beim Import gilt:

- ms  -> timestamp_ns = ts_ms * 1_000_000
- us  -> timestamp_ns = ts_us * 1_000
- ns  -> timestamp_ns = ts_ns

Verbot:
- Gemischte Einheiten innerhalb eines Datasets.
- Float-Timestamps (nur int64).
- Lokale Zeitzonen (immer UTC).

## 3) CSV Schema-Regel (GS / L1)

Verbindlich in GS-kompatiblen CSVs:
- timestamp_utc (ISO-8601, UTC, Sekunden)
- OHLCV Felder nach jeweiligem Dataset-Schema
- Alle Signal-/Regime-/Gate-Spalten gemaess GS-Definition

Optional:
- timestamp_ns (int64) fuer Debug/Tracing (empfohlen fuer Postmortems)

## 4) Resampling-Regeln (1m -> 5m etc.)

Resampling muss:
- auf timestamp_ns (UTC) erfolgen
- OHLC korrekt aggregieren
- Volume summieren
- Signals: last non-NaN innerhalb der Bar
- Regime und allow_long/allow_short: last non-NaN innerhalb der Bar
- Ergebnis: timestamp_utc auf Bar-Start oder Bar-Ende gem. Builder-Definition, aber konsistent und dokumentiert

## 5) Validation Gates (verbindlich)

Jedes gebaute Dataset muss vor Nutzung bestehen:
- timestamp_utc monotonic (strict increasing oder non-decreasing je nach Definition)
- keine Zeitluecken ausserhalb erwarteter Marktpausen (Krypto: i.d.R. keine)
- windowing konsistent (max_hold_bars basiert auf Bars, nicht Sekunden)
- Preflight in gs_run_with_manifest muss PASS sein

## 6) L1 Betrieb (verbindlich)

L1 verarbeitet intern:
- tick/time in UTC
- Persistenter State referenziert UTC-Zeit als ISO-8601
- Logs: timestamp_utc in ISO-8601 UTC

## 7) Migration / Bestand

Bestehende Datasets duerfen weiter genutzt werden, wenn:
- timestamp_utc korrekt und monotonic ist
- Einheit nicht gemischt ist (ms/us) oder bereits normalisiert
- Preflight PASS

Neue Datasets (ab heute):
- muessen diese Policy strikt erfuellen.

