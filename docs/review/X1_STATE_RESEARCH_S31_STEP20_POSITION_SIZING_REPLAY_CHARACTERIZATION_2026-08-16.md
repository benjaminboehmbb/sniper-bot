# X1 State-Research S31 STEP20-Position-Sizing-Replay-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / VALIDATED RESEARCH RESULT / NOT LIVE COMPATIBLE

Basis-Commit: `1409c7a71dcdc9289f615f3ec406c1219b93aa11`

Branch: `codex/x1-state-research-s31-step20-position-sizing-replay-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step20_position_sizing_replay.py`

## Zweck und Grenzen

S31 bindet den bestehenden Direktlauf-, Berechnungs-, Ausgabe- und Fehlervertrag von `analyze_step20_position_sizing_replay.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

`docs/research/STATE_RESEARCH_FINAL_STATUS.md` bewertet STEP20A als `VALIDATED RESEARCH RESULT`, aber ausdrücklich als `NOT LIVE COMPATIBLE`, weil der vollständige Trade-Lifetime-Verlauf verwendet wird. S31 charakterisiert ausschließlich dieses historische Offline-Research-Skript und autorisiert keine Strategie-, IU4-, Live-L1-, Exchange- oder Live-Integration.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `b185c681497db4c83ea929b5fc8701d3e0d5fd37f097257c18dfafea9655e185`
- Zeilen: 94
- Main-Guard: keiner
- Funktionsdefinitionen: genau `stats(pnl_col)`
- Import-Verhalten: unmittelbarer Laufversuch mit CSV-Reads vor Erreichen der Funktionsdefinition
- Writer: eine feste CSV, ohne Verzeichniserzeugung

## Fester Input-, Zeit- und Fenstervertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Für jeden Trade wird das vollständige Shadow-Lebenszeitfenster mit beiden inklusiven Grenzen verwendet:

```text
entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc
```

Trades ohne Snapshot im Fenster werden übersprungen. Der Risikowert ist das arithmetische Mittel aller `shadow_risk_score`-Werte im Fenster. Diese Trade-Lifetime-Aggregation verwendet Post-Entry-Information und ist die dokumentierte Ursache dafür, dass STEP20A nicht live-kompatibel ist.

Die erzeugten Rows werden nach `trade_index` aufsteigend sortiert.

## Multiplikator- und PnL-Vertrag

Die Multiplikatoren sind inklusive an beiden Codegrenzen:

- Mean Risk `<= 0.30`: Multiplikator `1.00`
- Mean Risk `> 0.30` und `<= 0.50`: Multiplikator `0.50`
- Mean Risk `> 0.50`: Multiplikator `0.25`

Der Vergleich verwendet native Floatwerte ohne Rundung oder Toleranz. Synthetische Grenzfixtures verwenden deshalb Fenster mit identischen `0.30`- beziehungsweise `0.50`-Werten, sodass der jeweilige Mittelwert exakt dieselbe Floatrepräsentation wie die Codekonstante besitzt.

Scaled PnL:

```text
scaled_pnl = original_pnl * multiplier
```

Jede erzeugte Row enthält in fester Reihenfolge:

1. `trade_index` als Integer
2. `side` unverändert aus der Trades-CSV
3. `original_pnl` als Float
4. `mean_shadow_risk` als Float
5. `multiplier`
6. `scaled_pnl`

## Statistikvertrag

`stats(pnl_col)` greift auf das globale, nach `trade_index` sortierte DataFrame `df` zu. Die Funktion wird zuerst für `original_pnl`, danach für `scaled_pnl` aufgerufen.

Startkapital: `10000.0`.

Gebundene Berechnungen:

- Equity als Startkapital plus kumulatives PnL,
- Peak als kumulatives Equity-Maximum,
- absoluter und prozentualer Drawdown,
- Gewinner mit PnL `> 0`,
- Verluste mit PnL `< 0`,
- Profit Factor als Gross Profit durch absoluten Gross Loss,
- Profit Factor `inf`, wenn Gross Loss null ist.

Alle zurückgegebenen Werte werden explizit in Python-`float` konvertiert. Das Statistik-Dictionary besitzt exakt diese Reihenfolge:

1. `final_equity`
2. `total_pnl`
3. `return_pct`
4. `winrate`
5. `profit_factor`
6. `max_drawdown_abs`
7. `max_drawdown_pct`

## Stdout- und Writer-Vertrag

Der erfolgreiche Lauf druckt in Reihenfolge:

1. führende Leerzeile und Überschrift `STEP20A POSITION SIZING REPLAY`,
2. Anzahl der Replay-Trades,
3. sieben ORIGINAL-Kennzahlen,
4. sieben SCALED-Kennzahlen,
5. nach Multiplikator aufsteigend sortierte `value_counts()`-Series,
6. nach erfolgreichem Writer die `written:`-Zeile.

Alle Kennzahlen werden mit `round(value, 4)` ausgegeben. Pandas 3.0.1 druckt die Multiplier-Series mit Indexname `multiplier`, Series-Name `count` und `dtype: int64`.

Erfolgs-Stdout-SHA-256: `fa6029394588f7cd1384cea648b661a1c60b191ff0f55576f4fcfbd0c11dbe01`.

Fester Writer:

- Pfad: `reports/step18/step20_position_sizing_replay.csv`
- `index=False`
- keine automatische Erzeugung von `reports/step18`

Der synthetische Erfolgsoutput besitzt sortierte Trade-Indizes `1, 2, 3`, Mean Risks `0.30, 0.50, 0.51`, Multiplikatoren `1.0, 0.5, 0.25` und Scaled PnLs `100.0, -25.0, 10.0`.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout und ohne Dateisystemänderung.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; die erste CSV bleibt unverändert.
3. Ohne gematchte Trade-Lifetime-Fenster besitzt das leere DataFrame keine Spalte `trade_index`; `sort_values("trade_index")` propagiert `KeyError` vor Stdout, Funktionsdefinition und Writer.
4. Bei vollständigen Inputs, aber fehlendem `reports/step18`, werden Überschrift, beide Statistikblöcke und die Multiplier-Verteilung ausgegeben. Danach propagiert der Writer `OSError`; die abschließende `written:`-Zeile bleibt aus.
5. Im erfolgreichen Lauf bleiben beide synthetischen Inputs SHA-256-identisch; ausschließlich die fest benannte Output-CSV entsteht.

## Charakterisierungsgate

`tests/state_research/test_step20_position_sizing_replay_characterization.py` umfasst zehn Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital, Funktions- und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. inklusives Trade-Lifetime-Fenster, Mean Risk, Missing-Window-Skip und Trade-Sortierung
4. Multiplikatorgrenzen, Scaled PnL und Row-Schema
5. globale `stats`-Semantik, Floatkonvertierung, Kennzahlen und Key-Reihenfolge
6. Stdout-Labels, Writer-Pfad, Writer-Reihenfolge und fehlendes `mkdir`
7. erfolgreicher synthetischer Direktlauf samt Stdout-, CSV- und Nichtmutationsvertrag
8. beide Missing-Input-Pfade in Read-Reihenfolge
9. No-Matched-Window-`KeyError` vor Stdout
10. Missing-Output-Directory-`OSError` nach Statistiken und vor `written:`

Gate-Test-SHA-256: `089be07e0eb2a824b5ff01534bf6fa954f9ca3457a38bbdcb0718ccab12c5bcc`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S31-Gate: 10/10 PASS
- Gesamte State-Research-Testkohorte: 151/151 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der vollständige direkt erreichbare Vertrag von `analyze_step20_position_sizing_replay.py` ist statisch und synthetisch gebunden. Der verbleibende technische Blocker ist die unmittelbare Ausführung beim Import. S31 ändert weder die wissenschaftliche Trade-Lifetime-Annahme noch Writer- oder Fehlerverträge und erteilt keinerlei Live-Freigabe.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S32-STEP20-POSITION-SIZING-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S32 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody einschließlich `stats(pnl_col)` AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle zehn S31-Verträge müssen unverändert bleiben; Live-L1, Exchange und Live bleiben gesperrt.
