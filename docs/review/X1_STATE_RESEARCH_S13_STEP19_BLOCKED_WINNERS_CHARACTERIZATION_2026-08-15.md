# X1 State-Research S13 STEP19-Blocked-Winners-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `cc079207f54e5cfdc889a19504d9f9aedc00fe95`

Branch: `codex/x1-state-research-s13-step19-blocked-winners-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_blocked_winners.py`

## Zweck und Grenzen

S13 bindet den aktuellen Vertrag des mit 45 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `fee296edf91a8f38d41f1f57fb8fbc560d607968fa326c2a3e905bbfe45b6644`
- Zeilen: 45
- Feste Konstante: `THRESHOLD = 0.40`
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen, Berechnung und potenziellem Stdout

## Input-, Zeit- und Row-Vertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Das vollständige Shadow-Lebenszeitfenster ist an Entry und Exit inklusiv. Trades ohne Snapshot im Fenster werden übersprungen.

Jeder gematchte Trade erzeugt:

- `trade_index` als `int`
- `side`
- `pnl` als `float`
- `exit_reason`
- `mean_shadow_risk` als `float` des arithmetischen Fenstermittelwerts

## Blocked-/Winner-/Loser-Partition

- Blocked: `mean_shadow_risk > THRESHOLD`
- Blocked-Winner: zusätzlich `pnl > 0`
- Blocked-Loser: zusätzlich `pnl <= 0`

Damit gilt:

- Ein Risikomittelwert exakt `0.40` ist nicht blockiert.
- Ein Blocked-Trade mit PnL exakt `0` zählt zu den Losern.

## Stdout- und Aggregationsvertrag

Zuerst werden ausgegeben:

- Anzahl aller Blocked-Trades
- Anzahl und PnL-Summe der Blocked-Winner, Summe auf zwei Stellen gerundet
- Anzahl und PnL-Summe der Blocked-Loser, Summe auf zwei Stellen gerundet

Danach folgen nur für Blocked-Winner:

1. Gruppierung nach `side` mit `count`, `mean`, `sum`
2. Gruppierung nach `exit_reason` mit `count`, `mean`, `sum`, absteigend nach `sum` sortiert

Das Skript schreibt keine Dateien.

Das Erfolgsfixture umfasst:

- einen Trade exakt an der Risikogrenze, der unblocked bleibt
- zwei Blocked-Winner mit unterschiedlichen Seiten und Exit-Gründen
- einen negativen Blocked-Loser
- einen Null-PnL-Blocked-Loser
- einen Trade ohne Shadow-Fenster, der übersprungen wird
- beide inklusiven Fenstergrenzen

Ergebnis:

- `blocked_total: 4`
- `blocked_winners: 2 sum_pnl: 13.0`
- `blocked_losers: 2 sum_pnl: -3.0`
- Return-Code 0 und leeres Stderr
- unverändertes Input-Manifest und keine Outputs
- Stdout-SHA-256: `353a9ce33e95ad176e95bb0436841dee245726fd3be3ab02ca4493430294722b`

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster besitzt das leere DataFrame keine Spalte `mean_shadow_risk`. Der erste Blocked-Filter propagiert ungefangen `KeyError` vor Stdout; beide Inputs bleiben unverändert.

S13 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_blocked_winners_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl und fester Threshold
2. Import-Zeit-Ausführer ohne Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder und Missing-Window-Skip
5. Blocked-/Winner-/Loser-Partition, Gruppierungen, Aggregation, Sortierung und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError` vor Stdout

Gate-Test-SHA-256: `4bd0b5b5302219405425739a26fe58d37b088b55f2380c8a6abd743e53e6d3b8`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S13-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 59/59 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige Direktlauf-, Partitions-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_blocked_winners.py` ist statisch und synthetisch gebunden. S13 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S14-STEP19-BLOCKED-WINNERS-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, feste `0.40`-Grenze, Partitionen, Gruppierungen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
