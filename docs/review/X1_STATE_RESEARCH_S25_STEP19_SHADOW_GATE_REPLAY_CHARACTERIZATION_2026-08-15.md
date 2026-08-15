# X1 State-Research S25 STEP19-Shadow-Gate-Replay-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS (CHARAKTERISIERUNG) / ZIELLAUF BLOCKED

Basis-Commit: `4ddc622bd4c80903cccaddb1a9ef800a1bdbf965`

Branch: `codex/x1-state-research-s25-step19-shadow-gate-replay-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_shadow_gate_replay.py`

## Zweck und Grenzen

S25 bindet den aktuellen Vertrag des mit 70 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung oder Reparatur erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `0a91b7e836679b3611c9650d1a3c1385768911329e266fdaff54681e16cc09ad`
- Zeilen: 70
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen und Berechnung

## Bestehender Schwellenblocker

Das Skript definiert:

- `START_CAPITAL = 10000.0`
- `THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]`

Der ausführbare Pfad liest `THRESHOLDS` jedoch nie. Stattdessen verwendet er zweimal den nirgendwo definierten Singularnamen `THRESHOLD`:

1. `df["mean_shadow_risk"] <= THRESHOLD`
2. `print("threshold:", THRESHOLD)`

Es existiert kein Store, Funktionsparameter oder Import für `THRESHOLD`. Sobald mindestens ein Trade gematcht wurde und `df.sort_values("trade_index")` erfolgreich ist, propagiert deshalb deterministisch:

`NameError: name 'THRESHOLD' is not defined`

Der Fehler tritt vor dem ersten `print()` und vor beiden `to_csv()`-Aufrufen auf. Der direkte Erfolgsvertrag und CSV-Inhaltsfingerprints sind daher nicht erreichbar und werden in S25 nicht erfunden.

## Input-, Zeit- und Row-Vertrag vor dem Blocker

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
- `pnl` als `float`
- `win` als `int(float(pnl) > 0)`
- `mean_shadow_risk` als `float` des arithmetischen Fenstermittelwerts

Anschließend wird das DataFrame aufsteigend nach `trade_index` sortiert. Erst danach wird der nicht definierte Singularname ausgewertet.

## Statisch gebundener, nicht erreichbarer Replay-Vertrag

Falls eine fachlich autorisierte Singularschwelle bereitgestellt würde, enthält der nachgelagerte Code statisch folgende Operationen:

- `kept = mean_shadow_risk <= THRESHOLD`
- Kept-Frame als `.copy()`
- Equity ab `10000.0` über kumulatives PnL
- kumulatives Equity-Peak
- absoluter und prozentualer Drawdown
- Gewinner `pnl > 0`, Verluste `pnl <= 0`
- Profit Factor mit `inf` bei Gross Loss null
- formatierte Replay-Zusammenfassung auf Stdout

Vorgesehene Writer-Reihenfolge:

1. `reports/step18/step19_shadow_gate_replay_trades.csv`, `index=False`
2. `reports/step18/step19_shadow_gate_replay_kept_trades.csv`, `index=False`

Das Skript erzeugt `reports/step18` nicht selbst. Da der Schwellenblocker früher auftritt, werden diese Writer im direkten Lauf derzeit nie erreicht.

## Dynamisch gebundene Fehler- und Nichtmutationsverträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout und ohne Dateisystemänderung.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Mit gematchten Trades propagiert der ungebundene Singularname `NameError` vor Stdout, CSVs oder neuen Verzeichnissen. Beide Inputs bleiben unverändert. Stdout ist leer, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
4. Ohne gematchtes Zeitfenster besitzt das leere DataFrame keine Spalte `trade_index`. `sort_values("trade_index")` propagiert bereits `KeyError` vor dem späteren `NameError`, vor Stdout und vor Outputs. Beide Inputs bleiben unverändert.

## Charakterisierungsgate

`tests/state_research/test_step19_shadow_gate_replay_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl, Konstanten und ungebundener Singularname
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder, Sortierung und Missing-Window-Skip
5. statische Replay-Formeln, Writer-Pfade, Writer-Reihenfolge und vorgesehene Stdout-Ordnung
6. gematchter Fixture-`NameError` vor Stdout und Outputs samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError` vor dem Schwellenblocker

Gate-Test-SHA-256: `2856281ce276bd0d1e9b63d5d34705121f4c3d5e9d25e082126887f4c66d07d7`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S25-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 113/113 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der tatsächlich erreichbare Import-/Direktlauf- und Fehlervertrag von `analyze_step19_shadow_gate_replay.py` ist statisch und synthetisch gebunden. Das Zielskript ist in seinem aktuellen Zustand nicht replay-fähig: Der gematchte Pfad endet immer am ungebundenen `THRESHOLD`, beide dokumentierten CSV-Ausgaben sind unerreichbar.

S25 autorisiert weder eine Schwellenwahl noch einen Sweep, eine Writer-Reparatur oder eine Entrypoint-Einkapselung, die den Defekt verdecken würde.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S25A-STEP19-SHADOW-GATE-REPLAY-SCHWELLENAUTHORITY-ENTSCHEIDUNG**. Es muss ausdrücklich geklärt werden, ob das Skript eine einzelne autoritative Schwelle verwenden oder das vorhandene `THRESHOLDS`-Raster ausführen soll und wie die zwei festen Outputpfade bei einem Raster zu behandeln wären. Erst nach dieser fachlichen Entscheidung darf eine Reparatur spezifiziert werden; eine Entrypoint-Einkapselung ist bis dahin nicht der nächste Schritt.
