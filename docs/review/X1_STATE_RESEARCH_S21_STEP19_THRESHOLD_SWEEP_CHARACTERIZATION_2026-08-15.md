# X1 State-Research S21 STEP19-Threshold-Sweep-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `e4955ebf564927946d75eb92e4df9865313b01f9`

Branch: `codex/x1-state-research-s21-step19-threshold-sweep-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_threshold_sweep.py`

## Zweck und Grenzen

S21 bindet den aktuellen Vertrag des mit 60 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `20e0f9b1480915db12c7b9ca1c5d19bd8a316e6dae8687b002ced35f56ca0168`
- Zeilen: 60
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

Ein PnL exakt `0` ist kein Gewinn.

## Schwellen- und Partitionsvertrag

Das feste Raster läuft in dieser Reihenfolge:

1. `0.40`
2. `0.45`
3. `0.50`
4. `0.55`
5. `0.60`
6. `0.65`
7. `0.70`

Für jede Schwelle werden Trades mit `mean_shadow_risk <= threshold` behalten. Exakte Grenzgleichheit bleibt damit im Kept-Set. `blocked` wird ausschließlich als `len(df) - len(kept)` ausgegeben.

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

Die Ausgabe beginnt exakt mit einer Leerzeile. Danach folgt:

`threshold,trades,blocked,total_pnl,winrate,pf,max_dd_pct`

Anschließend wird je Schwelle genau eine CSV-artige Zeile ausgegeben. Die Schwelle verwendet die normale Float-Darstellung; Total-PnL wird mit zwei, Winrate, Profit Factor und Max Drawdown werden mit vier Nachkommastellen formatiert.

Das Erfolgsfixture bindet alle sieben exakten Schwellen, beide inklusiven Zeitfenstergrenzen, positive, negative und Null-PnL-Trades, den `inf`-Zweig ohne Gross Loss, einen oberhalb des Rasters blockierten Trade sowie einen Trade ohne Shadow-Fenster.

Ausgewählte Zeilen:

- `0.4,1,7,100.00,1.0000,inf,0.0000`
- `0.5,3,5,50.00,0.3333,2.0000,0.0050`
- `0.7,7,1,90.00,0.4286,2.1250,0.0050`

Das Skript schreibt keine Dateien. Beide synthetischen Inputs bleiben byte-identisch. Erfolgs-Stdout-SHA-256: `06160c5cc30d60c80b2d02d638b15aeb9c87d78acdb9d40456821ba193309057`.

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster wird zunächst ausschließlich die führende Leerzeile und der Header ausgegeben. Danach propagiert der erste Zugriff auf `mean_shadow_risk` ungefangen `KeyError`; beide Inputs bleiben unverändert.

S21 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_threshold_sweep_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital und festes Schwellenraster
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Keep-Partition, Equity, Drawdown, Gewinner-/Verlustpartition, Profit Factor, Ausgabeformat und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError` nach führender Leerzeile und Header

Gate-Test-SHA-256: `f62fd6ebd68294f674bbee457d718559f47abbddf3fde2fa44ce525895f30e86`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S21-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 95/95 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige aktuelle Direktlauf-, Schwellen-, Partitions-, Kennzahlen-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_threshold_sweep.py` ist statisch und synthetisch gebunden. S21 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S22-STEP19-THRESHOLD-SWEEP-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Startkapital, Schwellenraster, Partitionen, Kennzahlen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
