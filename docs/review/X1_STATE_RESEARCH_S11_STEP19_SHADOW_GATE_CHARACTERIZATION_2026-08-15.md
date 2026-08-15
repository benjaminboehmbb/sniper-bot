# X1 State-Research S11 STEP19-Shadow-Gate-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `aef1fba815c6ce3fd365a418ddf8a55d508b237a`

Branch: `codex/x1-state-research-s11-step19-shadow-gate-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_shadow_gate.py`

## Zweck und Grenzen

S11 bindet den aktuellen Vertrag des mit 44 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `ae4d8d8fc8dccdc5fd454d6ed1069d44bb0abcbf06a6d6c4a8e3471feee07a0e`
- Zeilen: 44
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen, Berechnung und potenziellem Stdout

## Feste Input- und Zeitverträge

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Pro Trade wird kein einzelnes Entry-Snapshot gewählt. Das Skript bildet das vollständige inklusive Lebenszeitfenster:

- `shadow.timestamp_utc >= trade.entry_timestamp_utc`
- `shadow.timestamp_utc <= trade.exit_timestamp_utc`

Trades ohne Snapshot im Fenster werden übersprungen.

## Row- und Schwellenvertrag

Jeder gematchte Trade erzeugt exakt:

- `pnl` als `float`
- `win` als `int(float(pnl) > 0)`
- `mean_shadow_risk` als `float` des arithmetischen Fenstermittelwerts

Die Schwellen werden in dieser festen Reihenfolge durchlaufen:

`[0.50, 0.60, 0.70, 0.80]`

Pro Schwelle gilt:

- kept: `mean_shadow_risk <= threshold`
- blocked: `mean_shadow_risk > threshold`

Der Grenzwert selbst bleibt damit im Kept-Bestand.

## Stdout-Vertrag

Vor dem Sweep schreibt das Skript eine Leerzeile, `TOTAL TRADES: <n>` und eine weitere Leerzeile. Pro Schwelle folgen:

- Schwellenwert
- Anzahl Kept-Trades
- Anzahl Blocked-Trades
- Kept-PnL-Summe, auf zwei Stellen gerundet
- Kept-Winrate, auf vier Stellen gerundet
- Leerzeile

Das Skript schreibt keine Dateien.

Das Erfolgsfixture umfasst:

- vier gematchte Trades mit mittlerem Risiko `0.5`, `0.6`, `0.7`, `0.8`
- positive und negative PnLs
- beide inklusiven Fenstergrenzen
- einen Trade ohne Shadow-Fenster, der übersprungen wird

Ergebnis:

- Return-Code 0
- leeres Stderr
- unverändertes Input-Manifest
- `TOTAL TRADES: 4`
- alle vier Schwellenblöcke
- Stdout-SHA-256: `e2868a8d9a760d9b3f75ddf4434d4bc048a82066782864c43d90fec24dc8acfb`

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout und ohne Dateisystem-Seiteneffekt.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster wird zunächst exakt `TOTAL TRADES: 0` ausgegeben. Beim ersten Schwellenfilter propagiert anschließend der Zugriff auf die fehlende Spalte `mean_shadow_risk` ungefangen `KeyError`. Beide Inputs bleiben unverändert.

S11 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_shadow_gate_characterization.py` umfasst acht Prüfungen:

1. Quellidentität und Zeilenzahl
2. Import-Zeit-Ausführer ohne Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder und Missing-Window-Skip
5. feste Schwellen, vollständige Kept/Blocked-Partition, Rundungen und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-Teiloutput und `KeyError`

Gate-Test-SHA-256: `d8857bd854b23596fc0d14dbcdc618554e681fe7e143f743b916a0a7907b8586`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S11-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 50/50 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige Direktlauf-, Sweep-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_shadow_gate.py` ist statisch und synthetisch gebunden. S11 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S12-STEP19-SHADOW-GATE-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Read-Reihenfolge, Lebenszeitfenster, Schwellenpartition, Rundungen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
