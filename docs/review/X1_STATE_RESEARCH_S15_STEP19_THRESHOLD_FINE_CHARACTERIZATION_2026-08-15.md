# X1 State-Research S15 STEP19-Threshold-Fine-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `c4fa5d6dc6a70961d09dc4bedd9c278011075de6`

Branch: `codex/x1-state-research-s15-step19-threshold-fine-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_threshold_fine.py`

## Zweck und Grenzen

S15 bindet den aktuellen Vertrag des mit 56 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `ece62b2ddeb36ab9668ddb66b1ca6abaa87afd0c7b38bb3f068e48b1773e316f`
- Zeilen: 56
- Feste Konstante: `START_CAPITAL = 10000.0`
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
- `pnl` als `float`
- `win` als `int(float(pnl) > 0)`
- `mean_shadow_risk` als `float` des arithmetischen Fenstermittelwerts

Damit ist ein PnL exakt `0` kein Gewinn.

## Schwellen- und Partitionsvertrag

Das feste Raster läuft in dieser Reihenfolge:

1. `0.35`
2. `0.375`
3. `0.40`
4. `0.425`
5. `0.45`
6. `0.475`
7. `0.50`

Für jede Schwelle werden Trades mit `mean_shadow_risk <= threshold` behalten. Eine exakte Grenzgleichheit bleibt damit im Kept-Set. `blocked` wird ausschließlich als `len(df) - len(kept)` ausgegeben.

Die Reihenfolge der gematchten Trades bleibt für die kumulative Equity- und Drawdown-Berechnung erhalten.

## Kennzahlenvertrag

Für jede Schwelle gilt:

- `equity = 10000.0 + pnl.cumsum()`
- `peak = equity.cummax()`
- `dd_pct = (peak - equity) / peak`
- Gewinner: `pnl > 0`
- Verluste: `pnl <= 0`, einschließlich Null-PnL
- `gross_profit = sum(pnl)` der Gewinner
- `gross_loss = abs(sum(pnl))` der Verluste
- Profit Factor: `gross_profit / gross_loss`, falls `gross_loss > 0`, sonst `float("inf")`
- Winrate: arithmetischer Mittelwert der binären `win`-Spalte
- Max Drawdown: Maximum von `dd_pct`

## Stdout- und Nichtmutationsvertrag

Die erste Zeile lautet exakt:

`threshold,trades,blocked,total_pnl,winrate,pf,max_dd_pct`

Danach folgt je Schwelle genau eine CSV-artige Zeile. Die Schwelle verwendet die normale Float-Darstellung; Total-PnL wird mit zwei, Winrate, Profit Factor und Max Drawdown werden mit vier Nachkommastellen formatiert.

Das Erfolgsfixture bindet alle sieben exakten Schwellen, beide inklusiven Zeitfenstergrenzen, positive, negative und Null-PnL-Trades, den `inf`-Zweig ohne Gross Loss, einen oberhalb des Rasters blockierten Trade sowie einen Trade ohne Shadow-Fenster.

Ausgewählte Zeilen:

- `0.35,1,7,100.00,1.0000,inf,0.0000`
- `0.4,3,5,50.00,0.3333,2.0000,0.0050`
- `0.5,7,1,90.00,0.4286,2.1250,0.0050`

Das Skript schreibt keine Dateien. Beide synthetischen Inputs bleiben byte-identisch. Erfolgs-Stdout-SHA-256: `1c3545547a356868cd90d756a86d3cdd0693404ab5c7bc72563fe22342fa2b83`.

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster wird zunächst nur der Header ausgegeben. Danach propagiert der erste Zugriff auf `mean_shadow_risk` ungefangen `KeyError`; beide Inputs bleiben unverändert.

S15 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_threshold_fine_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital und festes Schwellenraster
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Keep-Partition, Equity, Drawdown, Gewinner-/Verlustpartition, Profit Factor, Ausgabeformat und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError` nach ausschließlich dem Header

Gate-Test-SHA-256: `0d47d95c89ec4108b0435200d6161397885f2a63f27430a4b12698ad5048cc74`

## Verifikation

Berichtskonsistente temporäre Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S15-Gate: 8/8 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Gesamte State-Research-Testkohorte: 68/68 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

Der zunächst bestehende Kohortenfehler in `test_step18_writer_chain_characterization.py` wurde nach ausdrücklicher S15A-Freigabe ausschließlich im Test korrigiert: Eingefangener STEP18-Stdout wird vor dem Fingerprint-Vergleich auf POSIX-Slashes normalisiert. Die beiden STEP18-Zielskripte, ihr tatsächlicher Stdout und alle neun CSV-Fingerprints blieben unverändert. Die S15A-Verifikation ist im separaten S15A-Bericht gebunden.

## Ergebnis

Der vollständige aktuelle Direktlauf-, Schwellen-, Partitions-, Kennzahlen-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_threshold_fine.py` ist statisch und synthetisch gebunden. Das fokussierte S15-Gate, die gesamte State-Research-Testkohorte und die bestehende Regression-Suite sind PASS. S15 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung am Zielskript.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S16-STEP19-THRESHOLD-FINE-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Startkapital, Schwellenraster, Partitionen, Kennzahlen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
