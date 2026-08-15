# X1 State-Research S19 STEP19-Risk-Escalation-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `8873444a683bc72261b97ef96573aa31430d5bda`

Branch: `codex/x1-state-research-s19-step19-risk-escalation-characterization-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_risk_escalation.py`

## Zweck und Grenzen

S19 bindet den aktuellen Vertrag des mit 60 Zeilen gemäß etablierter Provenienzreihenfolge nächsten historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `2b0eafa4c5b8f94509b608d0ecc026ba5bc7f0032bf33459a9e9a1b639df1fe9`
- Zeilen: 60
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen, Berechnung und potenziellem Stdout

## Input-, Zeit- und Eligibility-Vertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Das vollständige Shadow-Lebenszeitfenster ist an Entry und Exit inklusiv und wird anschließend mit `.copy()` materialisiert. Ein Trade wird übersprungen, wenn sein Fenster weniger als drei Shadow-Snapshots enthält.

Das Skript sortiert das gefilterte Fenster nicht zusätzlich. `entry_risk` verwendet daher ausdrücklich die erste Zeile des gefilterten Frames über `s.iloc[0]`.

## Row- und High-Risk-Vertrag

Jeder eligible Trade erzeugt:

- `win` als `int(pnl > 0)`
- `pnl` als `float`
- `entry_risk` als erster `shadow_risk_score`
- `max_risk` als Maximum des Fensters
- `mean_risk` als arithmetischer Mittelwert des Fensters
- `high_risk_count` als Anzahl der Werte strikt `> 0.5`
- `high_risk_pct` als Anteil der Werte strikt `> 0.5`

Ein Risikowert exakt `0.5` ist damit nicht high-risk. Ein PnL exakt `0` ist kein Gewinn.

## Gewinner-, Verlierer- und Korrelationsvertrag

Für die Ausgabe gilt:

- Gewinner: `win == 1`
- Verlierer: `win == 0`, einschließlich Null-PnL
- Beide Gruppen projizieren in identischer Reihenfolge `entry_risk`, `max_risk`, `mean_risk`, `high_risk_count`, `high_risk_pct` und geben deren Spaltenmittelwerte aus.

Danach werden auf dem vollständigen eligible DataFrame in dieser Reihenfolge berechnet:

1. `mean_risk` gegen `pnl`
2. `max_risk` gegen `pnl`
3. `high_risk_pct` gegen `pnl`

Die Berechnung verwendet jeweils unverändert `pandas.Series.corr` mit dessen Standardparametern.

## Stdout- und Nichtmutationsvertrag

Die Ausgabe beginnt mit einer Leerzeile und `WINNERS`, gefolgt vom Pandas-Series-Rendering der Gewinner-Mittelwerte. Danach folgen eine Leerzeile, `LOSERS`, das entsprechende Series-Rendering sowie eine weitere Leerzeile, `CORRELATIONS` und die drei beschrifteten Korrelationszeilen.

Das Erfolgsfixture bindet:

- zwei Gewinner und zwei Verlierer einschließlich eines Null-PnL-Trades
- die exakte `0.5`-High-Risk-Grenze
- beide inklusiven Zeitfenstergrenzen
- ein Zwei-Snapshot-Fenster, das übersprungen wird
- einen Trade ohne Shadow-Fenster
- unterschiedliche, endliche Korrelationswerte

Ausgewählte Ergebnisse:

- Gewinner-`entry_risk`: `0.300000`
- Gewinner-`high_risk_count`: `1.500000`
- Verlierer-`entry_risk`: `0.600000`
- Verlierer-`high_risk_count`: `0.500000`
- `mean_risk vs pnl`: `-0.031984651050360094`
- `max_risk vs pnl`: `-0.4880935300919764`
- `high_risk_pct vs pnl`: `0.242535625036333`

Das Skript schreibt keine Dateien. Beide synthetischen Inputs bleiben byte-identisch. Erfolgs-Stdout-SHA-256: `b8a823f50b41e113d1617a3785c9faecb019136ee1b15961cb2f017c491f5cff`.

## Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne eligible Zeitfenster besitzt das leere DataFrame keine Spalte `win`. Das Skript gibt zunächst exakt eine Leerzeile und `WINNERS` aus; anschließend propagiert die Gewinnerselektion ungefangen `KeyError`. Beide Inputs bleiben unverändert.

S19 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_risk_escalation_characterization.py` umfasst acht Prüfungen:

1. Quellidentität, Zeilenzahl, Drei-Snapshot-Minimum und feste High-Risk-Grenze
2. Import-Zeit-Ausführer ohne Main-Guard oder Funktionsdefinition
3. feste Input- und UTC-Konvertierungsreihenfolge
4. inklusives Lebenszeitfenster, `.copy()`, Row-Felder und erster Snapshot
5. Gewinner-/Verliererprojektion, Korrelationen, Ausgabeordnung und Nichtwriter-Vertrag
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Eligible-Window-`KeyError` nach ausschließlich Leerzeile und `WINNERS`

Gate-Test-SHA-256: `18b8e2fb3fe78e0e136fa8812963c2b313a677b7f997230146696d499fce9e1c`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S19-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 86/86 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige aktuelle Direktlauf-, Eligibility-, High-Risk-, Gruppen-, Korrelations-, Ausgabe- und Fail-closed-Vertrag von `analyze_step19_risk_escalation.py` ist statisch und synthetisch gebunden. S19 autorisiert keine Mathematik-, Pfad-, Schwellen-, Ausgabe- oder Fehleränderung.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S20-STEP19-RISK-ESCALATION-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Drei-Snapshot-Minimum, High-Risk-Grenze, Projektionen, Korrelationen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
