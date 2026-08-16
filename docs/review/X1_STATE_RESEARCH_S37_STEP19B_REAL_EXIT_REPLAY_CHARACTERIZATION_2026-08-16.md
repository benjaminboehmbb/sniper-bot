# X1 State-Research S37 STEP19B-Real-Exit-Replay-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / STEP19 DYNAMIC EXIT NOT VALIDATED

Basis-Commit: `b0f8af4135c3fa7e279b72b80d225d6387ca890d`

Branch: `codex/x1-state-research-s37-step19b-real-exit-replay-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step19B_real_exit_replay.py`

## Zweck und Grenzen

S37 bindet den bestehenden Direktlauf-, Match-, Trigger-, Replay-PnL-, Statistik-, CSV-, Stdout- und Fehlervertrag von `analyze_step19B_real_exit_replay.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

`docs/research/STEP19B_dynamic_risk_exit_validation.md` dokumentiert nach drei positiven 200k-Fenstern eine 500k-Validierung mit schlechterem PnL, Profit Factor und Drawdown. Der Endstatus lautet deshalb `STEP19 Dynamic Exit: not validated`. Das Skript und die feste Konfiguration stellen keine robuste eigenständige Trading-Regel und keine Live-Freigabe dar.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entrypoint-Status

- SHA-256: `414fe6edbf7a315351b86f9973f2c633c0a055e448c30352ffe300c896686ffc`
- Zeilen: 115
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit drei CSV-Reads, fünf UTC-Konvertierungen, Replay, Statistik, Stdout und potenziellem CSV-Writer

Feste Konstanten:

- `START_CAPITAL = 10000.0`
- `THRESHOLD = 0.50`
- `CONSECUTIVE = 3`

S37 erklärt diese feste Konfiguration weder zur autoritativen noch zur live-fähigen Einstellung.

## Fester Input- und Zeitvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/trade_lifecycle_snapshots.csv`
3. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge, jeweils mit `utc=True`:

1. Trades `entry_timestamp_utc`
2. Trades `exit_timestamp_utc`
3. Lifecycle `timestamp_utc`
4. Lifecycle `entry_timestamp_utc`
5. Shadow `timestamp_utc`

Fehlende Inputs propagieren `FileNotFoundError` in exakt dieser Read-Reihenfolge vor jeder Stdout-Ausgabe.

## Trade-, Zeitfenster- und Merge-Vertrag

Lifecycle-Zeilen werden je Trade durch exakte Gleichheit von `entry_timestamp_utc` und durch einen case-insensitiven Side-Vergleich ausgewählt. Shadow-Zeilen werden über das inklusive vollständige Trade-Lifetime-Fenster ausgewählt:

```text
entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc
```

Ist Lifecycle- oder Shadow-Ausschnitt leer, gilt:

- `replay_pnl = float(original pnl)`
- `exit_type = ORIGINAL_NO_LIFECYCLE`

Der historische Labelwert `ORIGINAL_NO_LIFECYCLE` wird also auch bei vorhandenem Lifecycle, aber fehlendem Shadow-Ausschnitt verwendet.

Bei zwei nichtleeren Ausschnitten werden beide nach `timestamp_utc` sortiert und mit `pandas.merge_asof` verbunden:

- Schlüssel: `timestamp_utc`
- Richtung: `nearest`
- Toleranz: `2min`
- nicht gematchte `shadow_risk_score`: `fillna(0.0)`

## High-Streak- und Triggervertrag

Ein Snapshot ist ausschließlich bei strikt exklusiver Überschreitung high:

```text
shadow_risk_score > 0.50
```

Ein Wert exakt `0.50` ist nicht high. Zustandswechsel bilden getrennte True-/False-Gruppen. Die kumulierte Integerdarstellung zählt innerhalb von True-Gruppen `1, 2, 3, ...`; False-Gruppen bleiben bei `0`.

Der Trigger enthält Rows mit `streak >= 3`. Bei mindestens einer solchen Row wird stets `trigger.iloc[0]`, also der erste qualifizierende Lifecycle-Snapshot, verwendet.

Ohne Trigger bleiben Original-PnL und `exit_type = ORIGINAL_EXIT` erhalten.

## Replay-PnL- und Row-Vertrag

Am ersten Trigger werden `entry_price`, `current_price` und `position_size` als Float gelesen.

Long:

```text
replay_pnl = (current_price - entry_price) * position_size
```

Jeder normalisierte Side-Wert ungleich `long` nimmt ohne weitere Validierung den Else-Zweig:

```text
replay_pnl = (entry_price - current_price) * position_size
```

Der Trigger setzt `exit_type = STEP19B_DYNAMIC_EXIT`.

Jede Trade-Row erzeugt exakt eine Ergebnis-Row mit fester Schlüsselreihenfolge:

1. `trade_index` als Integer
2. `side` kleingeschrieben
3. `original_pnl` als Float
4. `replay_pnl`
5. `exit_type`

Anschließend werden alle Rows nach `trade_index` aufsteigend sortiert.

## Kennzahlenvertrag

Nach der Sortierung werden in dieser Reihenfolge ergänzt:

1. `win = int(replay_pnl > 0)`
2. `equity = 10000.0 + replay_pnl.cumsum()`
3. `peak = equity.cummax()`
4. `dd_abs = peak - equity`
5. `dd_pct = dd_abs / peak`

Weitere Verträge:

- Gewinner: `replay_pnl > 0`
- Verluste: `replay_pnl < 0`
- Null-PnL gehört zu keiner Summe
- Profit Factor: Gross Profit geteilt durch absoluten Gross Loss
- Profit Factor `inf`, wenn Gross Loss null ist

## Stdout- und Writer-Vertrag

Der erfolgreiche Stdout beginnt mit einer Leerzeile und enthält:

1. Überschrift `STEP19B REAL EXIT REPLAY`
2. Threshold, Consecutive, Tradezahl und Dynamic-Exit-Zahl
3. Final Equity, Total PnL, Return, Winrate, Profit Factor und beide Max-Drawdown-Werte
4. eine nach `exit_type` gruppierte `count`-/`mean`-/`sum`-Tabelle für `replay_pnl`
5. nach erfolgreichem Writer die `written:`-Zeile

Gebundene synthetische Kennzahlen:

- Trades: `4`
- Dynamic Exits: `1`
- Final Equity: `9964.0`
- Total PnL: `-36.0`
- Return: `-0.0036`
- Winrate: `0.25`
- Profit Factor: `0.4545`
- Max Drawdown absolut: `40.0`
- Max Drawdown prozentual: `0.004`

Die Gruppentabelle enthält:

- `ORIGINAL_EXIT`: Count `1`, Mean `-40.0`, Sum `-40.0`
- `ORIGINAL_NO_LIFECYCLE`: Count `2`, Mean `5.0`, Sum `10.0`
- `STEP19B_DYNAMIC_EXIT`: Count `1`, Mean `-6.0`, Sum `-6.0`

Fester Writer:

- Pfad: `reports/step18/step19B_real_exit_replay.csv`
- `index=False`
- keine automatische Erzeugung von `reports/step18`

Die CSV besitzt nach Sortierung und Ableitungen zehn Spalten:

```text
trade_index,side,original_pnl,replay_pnl,exit_type,win,equity,peak,dd_abs,dd_pct
```

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-, Lifecycle- und Shadow-CSV propagieren nacheinander `FileNotFoundError` vor Stdout und ohne Dateisystemmutation.
2. Eine leere Trades-CSV mit gültigem Header führt beim `sort_values("trade_index")` des leeren `DataFrame(rows)` zu `KeyError` vor Stdout und Writer.
3. Bei vollständigen Inputs, aber fehlendem `reports/step18`, werden Statistiken und Groupby-Tabelle ausgegeben. Danach propagiert der Writer `OSError`; die abschließende `written:`-Zeile fehlt.
4. Ein ungültiger erster Trade-Entry-Zeitstempel propagiert Pandas `DateParseError` während der ersten UTC-Konvertierung vor Stdout.
5. Im erfolgreichen Lauf bleiben alle drei synthetischen Inputs SHA-256-identisch; ausschließlich die fest benannte Output-CSV entsteht.

## Charakterisierungsgate

`tests/state_research/test_step19b_real_exit_replay_characterization.py` umfasst elf Prüfungen:

1. Quellidentität, Zeilenzahl, drei Konstanten und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. Entry-/Side-Matching, inklusives Shadow-Fenster, Merge und Missing-Match-Exit
4. strikt exklusive High-Schwelle, Streak, erster Trigger und alle Exit-Typen
5. Preis-/Size-Konvertierung, Long-/Nicht-Long-PnL und Row-Schema
6. Sortierung, Kennzahlen, Stdout, Groupby und Writervertrag
7. erfolgreicher synthetischer Direktlauf samt exaktem Stdout, CSV und Input-Nichtmutation
8. alle drei Missing-Input-Pfade in Read-Reihenfolge
9. Empty-Trades-`KeyError` vor Stdout
10. Missing-Output-Directory-`OSError` nach Statistiken und vor `written:`
11. fehlerhafter erster Zeitstempel vor Stdout und ohne Mutation

Gate-Test-SHA-256: `d497f6b89a149736efe27296a83d75a3baaeb83b5030fde2980d06d0e3373deb`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S37-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 185/185 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der direkt erreichbare Vertrag von `analyze_step19B_real_exit_replay.py` ist statisch und synthetisch gebunden. S37 verändert weder feste Konfiguration, Match-/Streak-/Triggerlogik, Replay-PnL, Kennzahlen, CSV, Stdout noch Fehlerpfade und erteilt keinerlei IU4-, Live-L1-, Exchange-, Live- oder Produktionsfreigabe. Der fachliche Status bleibt `NOT VALIDATED`.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S38-STEP19B-REAL-EXIT-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S38 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle elf S37-Verträge müssen vollständig erhalten bleiben; Live-L1, Exchange und Live bleiben gesperrt.
