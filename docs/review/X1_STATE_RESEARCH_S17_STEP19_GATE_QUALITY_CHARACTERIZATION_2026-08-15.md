# X1 State-Research S17 STEP19-Gate-Quality-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `017452aa3a266a6a7fd5c26fa49b7caa58dedb60`

Branch: `codex/x1-state-research-s17-step19-gate-quality-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_gate_quality.py`

## Zweck und Grenzen

S17 bindet den aktuellen Vertrag des mit 59 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `3069392f6c459d2dc54db1278bfa575756228e007159b8da80dff91b9f9a11e8`
- Zeilen: 59
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

- `pnl` als `float`
- `win` als `int(pnl > 0.0)`
- `mean_shadow_risk` als `float` des arithmetischen Fenstermittelwerts

Damit ist ein PnL exakt `0` kein Gewinn.

## Gate- und Gruppenvertrag

Die Gruppenbildung erfolgt ausschließlich durch:

- `HIGH_RISK`, wenn `mean_shadow_risk > 0.50`
- andernfalls `LOW_RISK`

Ein Risikomittelwert exakt `0.50` gehört damit zu `LOW_RISK`.

Die Auswertung iteriert über `df.groupby("group")` ohne abweichende Sortierparameter. Im synthetischen Zwei-Gruppen-Fall erscheint deshalb `HIGH_RISK` vor `LOW_RISK`.

Innerhalb jeder Gruppe gilt:

- Gewinner: `pnl > 0`
- Verluste: `pnl <= 0`, einschließlich Null-PnL
- `gross_profit = sum(pnl)` der Gewinner
- `gross_loss = abs(sum(pnl))` der Verluste
- Profit Factor: `gross_profit / gross_loss`, falls `gross_loss > 0`, sonst `float("inf")`

## Stdout- und Nichtmutationsvertrag

Je Gruppe werden in fester Reihenfolge ausgegeben:

1. führende Leerzeile
2. `GROUP:`
3. `trades:`
4. `winrate:` mit `round(..., 4)`
5. `avg_pnl:` mit `round(..., 2)`
6. `gross_profit:` mit `round(..., 2)`
7. `gross_loss:` mit `round(..., 2)`
8. `profit_factor:` mit `round(..., 4)`
9. abschließende Leerzeile

Das Erfolgsfixture bindet:

- eine exakte `0.50`-Grenzgleichheit in `LOW_RISK`
- positive, negative und Null-PnL-Trades
- einen `HIGH_RISK`-`inf`-Zweig ohne Gross Loss
- einen endlichen `LOW_RISK`-Profit-Factor
- beide inklusiven Zeitfenstergrenzen
- einen Trade ohne Shadow-Fenster

Ausgewählte Ergebnisse:

- `HIGH_RISK`: 2 Trades, Winrate `1.0`, Avg PnL `5.0`, Gross Loss `0.0`, Profit Factor `inf`
- `LOW_RISK`: 3 Trades, Winrate `0.3333`, Avg PnL `2.0`, Gross Loss `4.0`, Profit Factor `2.5`

Das Skript schreibt keine Dateien. Beide synthetischen Inputs bleiben byte-identisch. Erfolgs-Stdout-SHA-256: `0bf31b04f63da292728641b31840f772101014f5221aeb30aa66255aa729a8d6`.

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster besitzt das leere DataFrame keine Spalte `mean_shadow_risk`. Die Gruppen-Zuweisung propagiert ungefangen `KeyError` vor Stdout; beide Inputs bleiben unverändert.

S17 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_gate_quality_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl und feste `0.50`-Gruppengrenze
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Gruppenbildung, Gewinner-/Verlustpartition, Profit Factor, Ausgabeordnung und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError` vor Stdout

Gate-Test-SHA-256: `c2e5807419891c6abd13783c3ca3921203a2c6934d1e595715cab741bf6836d1`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S17-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 77/77 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige aktuelle Direktlauf-, Gate-, Gruppen-, Kennzahlen-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_gate_quality.py` ist statisch und synthetisch gebunden. S17 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S18-STEP19-GATE-QUALITY-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, `0.50`-Gate, Gruppierung, Kennzahlen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
