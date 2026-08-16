# X1 State-Research S39 STEP20D-Dynamic-Exposure-Scaling-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE

Basis-Commit: `2e34962d05ef9546f4efa5e46685fd4345ec028c`

Branch: `codex/x1-state-research-s39-step20d-dynamic-exposure-scaling-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py`

## Zweck und Grenzen

S39 bindet den bestehenden Direktlauf-, Match-, Multiplikator-, rückwirkenden PnL-, Statistik-, CSV-, Stdout- und Fehlervertrag von `analyze_step20D_dynamic_exposure_scaling.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

`docs/research/STEP20D_dynamic_exposure_scaling_spec.md` bewertet STEP20D v1 als methodisch optimistischen Proof of Concept. Der aus dem vollständigen Trade-Lifetime-Verlauf ermittelte finale Multiplikator wird rückwirkend auf das gesamte Trade-PnL angewendet. Das ist nicht live-akkurat und darf keine Produktions- oder Live-Schlussfolgerung begründen.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entrypoint-Status

- SHA-256: `04bdee183f4854753068851361867cc34283bd77204ac2af1e1adc51365c1fd0`
- Zeilen: 128
- Main-Guard: keiner
- Funktionsdefinitionen in Reihenfolge: `multiplier_from_streaks(risk_series)`, `calc_stats(pnl_col)`
- Import-Verhalten: unmittelbarer Laufversuch mit drei CSV-Reads und fünf UTC-Konvertierungen vor der ersten Funktionsdefinition; danach Replay, Statistik, Stdout und potenzieller CSV-Writer
- Feste Konstante: `START_CAPITAL = 10000.0`

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

## Multiplikatorvertrag

`multiplier_from_streaks` startet mit drei Streakzählern bei `0` und dem Multiplikator `1.0`. Die Schwellen sind strikt exklusiv:

- `risk > 0.30`
- `risk > 0.50`
- `risk > 0.70`

Ein Wert exakt auf einer Schwelle setzt den jeweiligen Streak auf `0`. Ab drei konsekutiven Überschreitungen gilt:

| Streak | Multiplikator-Obergrenze |
| --- | ---: |
| `> 0.30` dreimal | `0.50` |
| `> 0.50` dreimal | `0.25` |
| `> 0.70` dreimal | `0.10` |

Die Aktualisierung verwendet stets `min(current, level)`. Der Multiplikator kann innerhalb eines Trades deshalb nur fallen und wird durch spätere niedrige Risiken nicht wieder erhöht.

Das Gate bindet zusätzlich Streak-Reset, exakte Schwellenwerte und alle vier möglichen finalen Multiplikatoren `1.0`, `0.5`, `0.25`, `0.1`.

## Trade-, Zeitfenster- und Merge-Vertrag

Lifecycle-Zeilen werden durch exakte Gleichheit von `entry_timestamp_utc` und durch einen case-insensitiven Side-Vergleich ausgewählt. Shadow-Zeilen werden über das inklusive vollständige Trade-Lifetime-Fenster ausgewählt:

```text
entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc
```

Ist Lifecycle- oder Shadow-Ausschnitt leer, gilt der Default-Multiplikator `1.0`.

Andernfalls werden beide Ausschnitte nach `timestamp_utc` sortiert und mit `pandas.merge_asof` verbunden:

- Schlüssel: `timestamp_utc`
- Richtung: `nearest`
- Toleranz: `2min`
- nicht gematchte `shadow_risk_score`: `fillna(0.0)`

Die resultierende Risk-Sequenz wird in Lifecycle-Reihenfolge an `multiplier_from_streaks` übergeben.

## Rückwirkender PnL- und Row-Vertrag

Das Original-PnL wird als Float gelesen. Danach gilt:

```text
scaled_pnl = original_pnl * final_multiplier
```

Diese rückwirkende Anwendung des erst nach Auswertung des gesamten Trade-Lifetime-Verlaufs bekannten Multiplikators ist die dokumentierte methodische Einschränkung.

Jeder Trade erzeugt eine Row mit fester Schlüsselreihenfolge:

1. `trade_index` als Integer
2. `side` kleingeschrieben
3. `original_pnl`
4. `final_multiplier`
5. `scaled_pnl`

Anschließend werden die Rows nach `trade_index` aufsteigend sortiert.

## Statistikvertrag

`calc_stats(pnl_col)` greift auf das globale, sortierte DataFrame `df` zu und wird zuerst für `original_pnl`, danach für `scaled_pnl` aufgerufen.

Gebundene Berechnungen:

- Equity als Startkapital plus kumulatives PnL,
- Peak als kumulatives Equity-Maximum,
- absoluter und prozentualer Drawdown,
- Gewinner mit PnL `> 0`, Verluste mit PnL `< 0`,
- Profit Factor als Gross Profit durch absoluten Gross Loss,
- Profit Factor `inf`, wenn Gross Loss null ist.

Das Statistik-Dictionary besitzt exakt diese Reihenfolge:

1. `final_equity`
2. `total_pnl`
3. `return_pct`
4. `winrate`
5. `profit_factor`
6. `max_drawdown_abs`
7. `max_drawdown_pct`

Die Ausgabe konvertiert jeden Statistikwert mit `float` und rundet auf vier Nachkommastellen.

## Stdout- und Writer-Vertrag

Der erfolgreiche Stdout beginnt mit einer Leerzeile und enthält:

1. Überschrift `STEP20D DYNAMIC EXPOSURE SCALING`
2. Tradezahl
3. sieben ORIGINAL-Kennzahlen
4. sieben STEP20D-Kennzahlen
5. nach Multiplikator aufsteigend sortierte `value_counts()`-Verteilung
6. nach erfolgreichem Writer die `written:`-Zeile

Gebundene synthetische Kennzahlen:

| Kennzahl | Original | STEP20D |
| --- | ---: | ---: |
| Final Equity | 10040.0 | 10014.0 |
| Total PnL | 40.0 | 14.0 |
| Return | 0.004 | 0.0014 |
| Winrate | 0.5 | 0.5 |
| Profit Factor | 1.4 | 1.35 |
| Max Drawdown absolut | 80.0 | 36.0 |
| Max Drawdown prozentual | 0.0079 | 0.0036 |

Die Multiplikatorverteilung enthält je eine Row für `0.10`, `0.25`, `0.50` und `1.00`.

Fester Writer:

- Pfad: `reports/step18/step20D_dynamic_exposure_scaling.csv`
- `index=False`
- keine automatische Erzeugung von `reports/step18`

Die Erfolgs-CSV besitzt sortierte Trade-Indizes `1,2,3,4`, Multiplikatoren `0.5,0.25,0.1,1.0` und Scaled PnLs `50.0,-20.0,4.0,-20.0`.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-, Lifecycle- und Shadow-CSV propagieren nacheinander `FileNotFoundError` vor Stdout und ohne Dateisystemmutation.
2. Eine leere Trades-CSV mit gültigem Header führt beim `sort_values("trade_index")` des leeren `DataFrame(rows)` zu `KeyError` vor Definition von `calc_stats`, Stdout und Writer.
3. Bei vollständigen Inputs, aber fehlendem `reports/step18`, werden beide Statistikblöcke und die Multiplikatorverteilung ausgegeben. Danach propagiert der Writer `OSError`; die abschließende `written:`-Zeile fehlt.
4. Ein ungültiger erster Trade-Entry-Zeitstempel propagiert Pandas `DateParseError` während der ersten UTC-Konvertierung vor Stdout.
5. Im erfolgreichen Lauf bleiben alle drei synthetischen Inputs SHA-256-identisch; ausschließlich die fest benannte Output-CSV entsteht.

## Charakterisierungsgate

`tests/state_research/test_step20d_dynamic_exposure_scaling_characterization.py` umfasst elf Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital, Funktionen und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. strikt exklusive Schwellen, konsekutive Streaks, Reset und monotoner Minimum-Multiplikator
4. Entry-/Side-Matching, inklusives Shadow-Fenster, Merge und Default-Multiplikator
5. rückwirkendes Scaled PnL, Row-Schema und Sortierung
6. Statistikvertrag, Ausgabereihenfolge, Verteilung und Writer
7. erfolgreicher synthetischer Direktlauf samt exaktem Stdout, CSV und Input-Nichtmutation
8. alle drei Missing-Input-Pfade in Read-Reihenfolge
9. Empty-Trades-`KeyError` vor Stdout
10. Missing-Output-Directory-`OSError` nach Statistiken und vor `written:`
11. fehlerhafter erster Zeitstempel vor Stdout und ohne Mutation

Gate-Test-SHA-256: `bb1e4992154037c4686727afc12b472f9941ee83c1fa3550bab422ebe9b6279d`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S39-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 197/197 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der direkt erreichbare Vertrag von `analyze_step20D_dynamic_exposure_scaling.py` ist statisch und synthetisch gebunden. S39 verändert weder Multiplikator-, Match-, rückwirkende PnL-, Statistik-, CSV-, Stdout- noch Fehlerverträge und erteilt keinerlei IU4-, Live-L1-, Exchange-, Live- oder Produktionsfreigabe. Der fachliche Status bleibt `PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE`.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S40-STEP20D-DYNAMIC-EXPOSURE-SCALING-ENTRYPOINT-EINKAPSELUNG**. S40 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody einschließlich beider Funktionsdefinitionen AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle elf S39-Verträge müssen vollständig erhalten bleiben; Live-L1, Exchange und Live bleiben gesperrt.
