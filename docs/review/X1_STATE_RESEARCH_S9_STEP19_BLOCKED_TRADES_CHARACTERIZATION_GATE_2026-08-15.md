# X1 State-Research S9 STEP19-Blocked-Trades-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `3824c66b9d163109c02d8b431a0fbcaefe19609b`

Branch: `codex/x1-state-research-s9-step19-blocked-trades-characterization-gate-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_blocked_trades.py`

## Zweck und Grenzen

S9 bindet den aktuellen Vertrag des mit 35 Zeilen kleinsten verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführers, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde weder geändert noch gegen reale Research-Daten ausgeführt. Alle dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `2b1f132f7de99f49a0af5c7a9a138fcf842ae2760d2d3b5bf52d86e957cd1c12`
- Zeilen: 35
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit Dateizugriffen, Berechnung und potenziellem Stdout

Ein Import ist damit weiterhin keine sichere Symbolinspektion.

## Feste Input- und Zeitverträge

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

Zeitkonvertierungsreihenfolge, jeweils mit `utc=True`:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Pro Trade wird das Shadow-Fenster inklusiv gebildet:

- `shadow.timestamp_utc >= trade.entry_timestamp_utc`
- `shadow.timestamp_utc <= trade.exit_timestamp_utc`

Trades ohne Snapshot im inklusiven Fenster werden übersprungen.

## Row-, Filter- und Aggregationsvertrag

Für jeden gematchten Trade entstehen exakt:

- `side` aus dem Trade
- `pnl` aus dem Trade
- `exit_reason` aus dem Trade
- `mean_shadow_risk` als arithmetischer Mittelwert von `shadow_risk_score` im inklusiven Fenster

Der Blocked-Filter lautet strikt:

`mean_shadow_risk > 0.5`

Der Grenzwert `0.5` ist damit nicht blockiert.

Stdout enthält nacheinander:

1. Gruppierung nach `side`, `pnl`-Aggregation `count`, `mean`, `sum`
2. eine Leerzeile
3. Gruppierung nach `exit_reason`, dieselbe `pnl`-Aggregation, anschließend aufsteigend nach `sum` sortiert

Das Skript enthält keine Datei-Schreiboperation.

## Synthetischer Erfolgsvertrag

Das Fixture bindet ausdrücklich:

- zwei blockierte BUY-Trades
- einen blockierten SELL-Trade
- einen Trade mit exakt `mean_shadow_risk == 0.5`, der nicht blockiert wird
- einen Trade ohne Shadow-Zeitfenster, der übersprungen wird
- beide inklusiven Zeitgrenzen
- mehrere Exit-Gründe und die Sortierung nach PnL-Summe

Ergebnis:

- Return-Code 0
- leeres Stderr
- unverändertes Input-Manifest
- keine Output-Dateien
- Stdout-SHA-256: `4c0c24b3d840037590bdd871cd683aa1ca5afca71bc7ca5feb01d2ef6ea67dfb`

## Fail-closed-Verträge

1. Fehlt der erste Input, propagiert `FileNotFoundError` für die Trades-CSV vor Stdout und ohne Dateisystem-Seiteneffekt.
2. Existiert nur die Trades-CSV, propagiert `FileNotFoundError` für die Shadow-CSV vor Stdout; der erste Input bleibt unverändert.
3. Trifft kein Trade ein Shadow-Zeitfenster, besitzt das aus der leeren Row-Liste erzeugte DataFrame keine Spalte `mean_shadow_risk`. Der Zugriff propagiert ungefangen `KeyError` vor Stdout; beide Inputs bleiben unverändert.

S9 behebt oder lockert keinen dieser Verträge.

## Charakterisierungsgate

`tests/state_research/test_step19_blocked_trades_characterization.py` umfasst acht Prüfungen:

1. Quellidentität und Zeilenzahl
2. Import-Zeit-Ausführer ohne Main-Guard
3. feste Input- und Zeitkonvertierungsreihenfolge
4. inklusives Zeitfenster, Mittelwert und strikter `> 0.5`-Filter
5. beide Gruppierungen, Aggregationen, Sortierung und fehlende Datei-Writer
6. erfolgreicher Fixture-Stdout samt Input-Nichtmutation
7. beide Missing-Input-Pfade in Read-Reihenfolge
8. No-Matched-Window-`KeyError`

Gate-Test-SHA-256: `004aa848e0a8a345f57dfae0908f9819d61f3d9fc98abf6380f851790125786c`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S9-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 41/41 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Der vollständige aktuelle Direktlauf- und Fail-closed-Vertrag von `analyze_step19_blocked_trades.py` ist mit statischen und synthetischen Belegen gebunden. S9 autorisiert keine Mathematik-, Filter-, Pfad-, Ausgabe- oder Fehleränderung.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S10-STEP19-BLOCKED-TRADES-ENTRYPOINT-EINKAPSELUNG**. Der bestehende Top-Level-Ablauf darf ausschließlich in ein parameterloses `main()` plus Main-Guard verschoben werden. Direkter Stdout-Fingerprint, Read-Reihenfolge, `> 0.5`-Grenze, Aggregationen und sämtliche Fail-closed-Pfade müssen unverändert bleiben; ein Import muss anschließend ohne Reads, Stdout oder Dateisystem-Seiteneffekte möglich sein.
