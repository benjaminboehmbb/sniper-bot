# X1 State-Research S23 STEP19-Entry-Gate-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `f7eba6063d122eb90c2f0443684cacdf24acd647`

Branch: `codex/x1-state-research-s23-step19-entry-gate-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_entry_gate.py`

## Zweck und Grenzen

S23 bindet den aktuellen Vertrag des mit 64 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `fded5b2a284fcf311bbcb2285314a1a160d6e1cc988b0964a54aa94e0417ab5f`
- Zeilen: 64
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen, Berechnung und potenziellem Stdout

## Input- und Zeitvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Shadow-`timestamp_utc`

Der Trade-Exit wird nicht gelesen oder konvertiert. Für jeden Trade werden alle Shadow-Zeilen mit `timestamp_utc <= entry_timestamp_utc` gefiltert. Anschließend wird mit `.tail(1)` die letzte Zeile in bestehender Input-Reihenfolge gewählt.

Das Skript sortiert die Shadow-Daten nicht zusätzlich. Existiert bis einschließlich Entry kein Snapshot, wird der Trade übersprungen. Der gewählte Ein-Zeilen-Frame wird über `snap.iloc[0]` aufgelöst.

## Row-, Korrelations- und Schwellenvertrag

Jeder eligible Trade erzeugt:

- `pnl` als `float`
- `win` als `int(pnl > 0.0)`
- `entry_shadow_risk` als `float` des gewählten Snapshots

Ein PnL exakt `0` ist kein Gewinn.

Vor dem Schwellenraster werden mit `pandas.Series.corr` und Standardparametern in dieser Reihenfolge berechnet:

1. `entry_shadow_risk` gegen `pnl`
2. `entry_shadow_risk` gegen `win`

Das feste Raster läuft in dieser Reihenfolge:

1. `0.35`
2. `0.40`
3. `0.45`
4. `0.50`
5. `0.55`
6. `0.60`

Für jede Schwelle werden Trades mit `entry_shadow_risk <= threshold` behalten. Exakte Grenzgleichheit bleibt damit im Kept-Set. `blocked` ist `len(df) - len(kept)`.

Innerhalb des Kept-Sets gilt:

- Gewinner: `pnl > 0`
- Verluste: `pnl <= 0`, einschließlich Null-PnL
- Profit Factor: Gross Profit geteilt durch absoluten Gross Loss, falls dieser positiv ist, sonst `inf`

## Stdout- und Nichtmutationsvertrag

Die Ausgabe beginnt mit einer Leerzeile, `ENTRY_RISK vs PNL`, dem ersten Korrelationswert und einer weiteren Leerzeile. Danach folgen `ENTRY_RISK vs WIN`, der zweite Korrelationswert, eine Leerzeile und der Header:

`threshold,trades,blocked,total_pnl,winrate,pf`

Je Schwelle folgt eine CSV-artige Zeile. Total-PnL wird mit zwei, Winrate und Profit Factor werden mit vier Nachkommastellen formatiert.

Das Erfolgsfixture bindet alle sechs exakten Schwellen, eine exakte Entry-Zeitgleichheit, positive, negative und Null-PnL-Trades, `inf` und endlichen Profit Factor, einen oberhalb des Rasters blockierten Trade sowie einen Trade ohne verfügbaren Entry-Snapshot.

Ausgewählte Zeilen:

- `0.35,1,6,100.00,1.0000,inf`
- `0.5,4,3,90.00,0.5000,2.8000`
- `0.6,6,1,100.00,0.5000,2.4286`

Das Skript schreibt keine Dateien. Beide synthetischen Inputs bleiben byte-identisch. Erfolgs-Stdout-SHA-256: `69019689e29dd09d7e680a6120ba6ed7bfdde391329932e844fa597e62059e24`.

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne eligible Entry-Snapshot besitzt das leere DataFrame keine Spalte `entry_shadow_risk`. Das Skript gibt zunächst ausschließlich eine Leerzeile und `ENTRY_RISK vs PNL` aus; anschließend propagiert die erste Korrelation ungefangen `KeyError`. Beide Inputs bleiben unverändert.

S23 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_entry_gate_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl und festes Schwellenraster
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusive Entry-Zuordnung, `.tail(1)`, `.iloc[0]`, Row-Felder und Missing-Snapshot-Skip
5. Korrelationen, Keep-Partition, Gewinner-/Verlustpartition, Profit Factor, Ausgabeordnung und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Eligible-Snapshot-`KeyError` nach ausschließlich Leerzeile und erster Überschrift

Gate-Test-SHA-256: `68eaf162a6989e48a17c0d244ea5ddb7c2186bbe444b885ddc71f368f22d677f`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S23-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 104/104 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige aktuelle Direktlauf-, Entry-Zuordnungs-, Korrelations-, Schwellen-, Partitions-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_entry_gate.py` ist statisch und synthetisch gebunden. S23 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S24-STEP19-ENTRY-GATE-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Entry-Snapshot-Zuordnung, Korrelationen, Schwellenraster, Partitionen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
