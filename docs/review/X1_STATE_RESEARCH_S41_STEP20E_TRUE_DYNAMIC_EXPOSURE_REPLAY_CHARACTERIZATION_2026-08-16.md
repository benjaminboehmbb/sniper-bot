# X1 State-Research S41 STEP20E-True-Dynamic-Exposure-Replay-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / STEP20E NOT VALIDATED

Basis-Commit: `826bfee47800f4d4c91ac5ac3e51a961d8f0334c`

Branch: `codex/x1-state-research-s41-step20e-true-dynamic-exposure-replay-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py`

## Zweck und Grenzen

S41 bindet den bestehenden Direktlauf-, Match-, Multiplikator-, Segment-PnL-, Statistik-, CSV-, Stdout- und Fehlervertrag von `analyze_step20E_true_dynamic_exposure_replay.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

STEP20E korrigiert die rückwirkende PnL-Anwendung von STEP20D v1, indem Expositionsreduktionen zeitabhängig auf nachfolgende Segmente angewendet werden. `docs/research/STEP20D_dynamic_exposure_scaling_spec.md`, `STEP20_FINAL_SUMMARY.md` und `STATE_RESEARCH_FINAL_STATUS.md` bewerten den Ansatz dennoch ausdrücklich als `NOT VALIDATED`: PnL, Profit Factor und Winrate verschlechterten sich; die Drawdown-Verbesserung genügte nicht.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entrypoint-Status

- SHA-256: `14667ea1f44d380e807523a0a71402b3786eeafff306d7ee3e4a8f44d29438ee`
- Zeilen: 177
- Main-Guard: keiner
- Funktionsdefinitionen in Reihenfolge: `update_multiplier(...)`, `stats(pnl_col)`
- Import-Verhalten: unmittelbarer Laufversuch mit drei CSV-Reads und fünf UTC-Konvertierungen vor der ersten Funktionsdefinition; danach Segment-Replay, Statistik, Stdout und potenzieller CSV-Writer
- Feste Konstante: `START_CAPITAL = 10000.0`

## Input-, Zeit- und Matchvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/trade_lifecycle_snapshots.csv`
3. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge, jeweils mit `utc=True`:

1. Trades Entry
2. Trades Exit
3. Lifecycle Snapshot
4. Lifecycle Entry
5. Shadow Snapshot

Lifecycle-Zeilen werden durch exakte Entry-Zeitgleichheit und case-insensitives Side-Matching ausgewählt. Das Shadow-Fenster ist an Entry und Exit inklusiv. Bei fehlendem Lifecycle- oder Shadow-Ausschnitt bleiben Original-PnL, `reductions = 0` und `final_multiplier = 1.0` erhalten.

Nichtleere Ausschnitte werden sortiert über `merge_asof` mit `direction="nearest"`, `tolerance="2min"` und anschließendem `fillna(0.0)` verbunden. Das Merge-Ergebnis wird erneut nach `timestamp_utc` sortiert.

## Multiplikatorvertrag

`update_multiplier` verwaltet drei konsekutive Streaks mit strikt exklusiven Schwellen `>0.30`, `>0.50`, `>0.70`. Exakte Schwellenwerte setzen den jeweiligen Streak zurück.

Ab drei Treffern gelten über `min(current, level)` die Obergrenzen:

- `0.50`
- `0.25`
- `0.10`

Zurückgegeben werden alle drei aktualisierten Streakzähler und der neue Multiplikator. Ein bereits reduzierter Multiplikator kann nicht wieder steigen.

## Segment-PnL- und Reduktionsvertrag

Der Entry-Preis stammt aus `merged.iloc[0]["entry_price"]`. `prev_price` startet am Entry-Preis, `current_mult` bei `1.0`, Replay-PnL bei `0.0` und Reduktionen bei `0`.

Für jeden Lifecycle-Snapshot gilt die feste Reihenfolge:

1. `current_price` und `shadow_risk_score` als Float lesen.
2. Segment-PnL zwischen `prev_price` und `current_price` mit dem vor dem Snapshot gültigen `current_mult` berechnen.
3. Segment-PnL addieren und `prev_price` aktualisieren.
4. Erst danach `update_multiplier` aufrufen.
5. `reductions` genau einmal erhöhen, wenn der neue Multiplikator kleiner als der vorherige ist.

Long-Segment:

```text
(current_price - prev_price) * current_mult
```

Jeder Side-Wert ungleich `long` verwendet:

```text
(prev_price - current_price) * current_mult
```

Nach allen Snapshots wird ein finales Segment zwischen dem letzten `current_price` und `trade["exit_price"]` mit dem finalen Multiplikator berechnet. Der Code verwendet bei Segmenten bewusst keine `position_size`; S41 bindet diese bestehende Mathematik, ohne sie fachlich zu legitimieren oder zu ändern.

Wenn mehrere Stufen in einem Snapshot gleichzeitig fallen, wird aufgrund des Vergleichs vor/nach dem einzelnen `update_multiplier`-Aufruf nur eine Reduktion gezählt.

## Row-, Sortier- und Statistikvertrag

Jeder Trade erzeugt in fester Reihenfolge:

1. `trade_index`
2. `side`
3. `original_pnl`
4. `replay_pnl`
5. `reductions`
6. `final_multiplier`

Anschließend wird nach `trade_index` aufsteigend sortiert.

`stats(pnl_col)` berechnet Equity, Peak, absoluten/prozentualen Drawdown, Gewinner `>0`, Verluste `<0` und Profit Factor mit `inf`-Fallback. Das siebenfeldrige Dictionary wird zuerst für `original_pnl`, danach für `replay_pnl` erzeugt.

## Stdout- und Writer-Vertrag

Der Stdout enthält in Reihenfolge:

1. führende Leerzeile und Überschrift,
2. Tradezahl,
3. sieben ORIGINAL-Kennzahlen,
4. sieben STEP20E-Kennzahlen,
5. sortierte Final-Multiplier-Verteilung,
6. sortierte Reduktionsanzahl-Verteilung,
7. nach erfolgreichem Writer `written:`.

Gebundene synthetische Kennzahlen:

| Kennzahl | Original | STEP20E |
| --- | ---: | ---: |
| Final Equity | 10040.0 | 9983.65 |
| Total PnL | 40.0 | -16.35 |
| Return | 0.004 | -0.0016 |
| Winrate | 0.5 | 0.5 |
| Profit Factor | 1.4 | 0.2922 |
| Max Drawdown absolut | 80.0 | 23.1 |
| Max Drawdown prozentual | 0.0079 | 0.0023 |

Die synthetischen Replay-PnLs sind `3.5`, `3.25`, `-3.1`, `-20.0`; Final-Multiplikatoren `0.5`, `0.25`, `0.1`, `1.0`; Reduktionen `1`, `1`, `1`, `0`.

Fester Writer:

- `reports/step18/step20E_true_dynamic_exposure_replay.csv`
- `index=False`
- keine automatische Verzeichniserzeugung

## Fehler- und Nichtmutationsverträge

1. Alle drei fehlenden Inputs propagieren `FileNotFoundError` in fester Read-Reihenfolge vor Stdout.
2. Leere Trades führen beim Sortieren des leeren DataFrames zu `KeyError("trade_index")` vor Statistik, Stdout und Writer.
3. Fehlendes `reports/step18` propagiert nach beiden Statistikblöcken und Verteilungen `OSError`; `written:` fehlt.
4. Ungültiger erster Entry-Zeitstempel propagiert `DateParseError` vor Stdout.
5. Im Erfolg bleiben alle drei Inputs byte-identisch; ausschließlich die feste Output-CSV entsteht.

## Charakterisierungsgate

`tests/state_research/test_step20e_true_dynamic_exposure_replay_characterization.py` umfasst elf Prüfungen:

1. Quellidentität, Konstante, Funktionen und Import-Zeit-Status
2. Read- und UTC-Konvertierungsreihenfolge
3. Multiplikatorschwellen, Streaks, Reset und Monotonie
4. Match, Fenster, Merge und Default-Pfad
5. Segmentreihenfolge, Finalsegment, Reduktionszählung, fehlende Position-Size-Nutzung und Row-Schema
6. Statistik, beide Verteilungen und Writer
7. synthetischer Erfolg mit exaktem Stdout, CSV und Nichtmutation
8. drei Missing-Input-Pfade
9. Empty-Trades-Fehler
10. Missing-Output-Directory-Fehler
11. fehlerhafter erster Zeitstempel

Gate-Test-SHA-256: `f16512e03a7aaafcbe9d954a8330a7b5aa88187b70e9201dbf29534f1f89e595`

## Verifikation

- Fokussiertes S41-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 209/209 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- Gesperrter Builder gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der direkt erreichbare STEP20E-Vertrag ist statisch und synthetisch gebunden. S41 verändert keine Mathematik oder Schnittstelle und erteilt keinerlei IU4-, Live-L1-, Exchange-, Live- oder Produktionsfreigabe. Der fachliche Status bleibt `NOT VALIDATED`.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S42-STEP20E-TRUE-DYNAMIC-EXPOSURE-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S42 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody einschließlich beider Funktionsdefinitionen AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle elf S41-Verträge müssen vollständig erhalten bleiben.
