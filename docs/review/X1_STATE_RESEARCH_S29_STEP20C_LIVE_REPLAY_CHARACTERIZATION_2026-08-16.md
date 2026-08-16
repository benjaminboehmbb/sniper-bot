# X1 State-Research S29 STEP20C-Live-Replay-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / HISTORISCHES MODELL NOT VALIDATED

Basis-Commit: `e01c474ecc1ba2efbba3c58a6c563c3758b9e662`

Branch: `codex/x1-state-research-s29-step20c-live-replay-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step20C_live_replay.py`

## Zweck und Grenzen

S29 bindet den bestehenden Direktlauf-, Berechnungs-, Ausgabe- und Fehlervertrag von `analyze_step20C_live_replay.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

Der Dateiname und die historische Überschrift „LIVE-COMPATIBLE“ stellen keine Live-Freigabe dar. `docs/research/STATE_RESEARCH_FINAL_STATUS.md` und `docs/research/STEP20_FINAL_SUMMARY.md` bewerten STEP20C als `NOT VALIDATED` beziehungsweise nicht ausreichend prädiktiv. S29 charakterisiert ausschließlich ein historisches Offline-Research-Skript.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `7c3f1488c565fad9c3cd72f401ce747d63e9ecfe4af982552271a09c0f3e2841`
- Zeilen: 94
- Main-Guard: keiner
- Funktionsdefinitionen: genau `calc_stats(pnl_col)`
- Import-Verhalten: unmittelbarer Laufversuch mit CSV-Reads vor Erreichen der Funktionsdefinition
- Writer: eine feste CSV, ohne Verzeichniserzeugung

## Fester Input- und Zeitvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Shadow-`timestamp_utc`

Ein Trade-Exitzeitpunkt wird weder gelesen noch konvertiert. Für jeden Trade filtert das Skript alle Shadow-Zeilen mit `timestamp_utc <= entry_timestamp_utc` und wählt anschließend `.tail(1)`.

Diese Auswahl ist entry-inklusiv, aber nicht nach Timestamp sortiert. Autoritativ ist deshalb die letzte geeignete Zeile in der bestehenden CSV-Reihenfolge, nicht zwingend der zeitlich neueste Snapshot. Ein synthetischer unsortierter Fixture-Lauf bindet, dass bei den geeigneten Risiken `0.90`, `0.10`, `0.40` die letzte CSV-Zeile mit Risiko `0.40` gewählt wird, obwohl `0.90` den neuesten Timestamp besitzt.

Trades ohne geeigneten Pre-Entry-Snapshot werden übersprungen. Die erzeugten Replay-Rows werden anschließend nach `trade_index` aufsteigend sortiert.

## Exposure- und PnL-Vertrag

Das Entry-Risiko wird als Float gelesen. Die Multiplikatoren sind inklusiv an beiden Grenzen:

- Risiko `<= 0.30`: Multiplikator `1.00`
- Risiko `> 0.30` und `<= 0.50`: Multiplikator `0.50`
- Risiko `> 0.50`: Multiplikator `0.25`

Scaled PnL:

```text
scaled_pnl = original_pnl * multiplier
```

Jede erzeugte Row enthält in fester Reihenfolge:

1. `trade_index` als Integer
2. `side` unverändert aus der Trades-CSV
3. `original_pnl` als Float
4. `entry_shadow_risk` als Float
5. `multiplier`
6. `scaled_pnl`

## Statistikvertrag

`calc_stats(pnl_col)` greift auf das globale, nach `trade_index` sortierte DataFrame `df` zu. Die Funktion wird zuerst für `original_pnl`, danach für `scaled_pnl` aufgerufen.

Startkapital: `10000.0`.

Gebundene Berechnungen:

- Equity als Startkapital plus kumulatives PnL,
- Peak als kumulatives Equity-Maximum,
- absoluter und prozentualer Drawdown,
- Gewinner mit PnL `> 0`,
- Verluste mit PnL `< 0`,
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

Die historische Spezifikation `docs/research/STEP20C_live_replay_spec.md` nennt zusätzlich `avg_pnl` und `trade_count` als erforderliche Outputmetriken. Der bestehende Code liefert `avg_pnl` nicht und führt `trade_count` nicht im Statistik-Dictionary; er druckt lediglich einmal die Gesamtzahl `trades`. S29 dokumentiert diese Abweichung und repariert sie nicht.

## Stdout- und Writer-Vertrag

Der erfolgreiche Lauf druckt in Reihenfolge:

1. führende Leerzeile und Überschrift `STEP20C LIVE-COMPATIBLE REPLAY`,
2. Anzahl der Replay-Trades,
3. sieben ORIGINAL-Kennzahlen,
4. sieben STEP20C-Kennzahlen,
5. nach Multiplikator aufsteigend sortierte `value_counts()`-Series,
6. nach erfolgreichem Writer die `written:`-Zeile.

Alle Kennzahlen werden nach Konvertierung zu Float mit `round(..., 4)` ausgegeben. Pandas 3.0.1 druckt die Multiplier-Series mit Indexname `multiplier`, Series-Name `count` und `dtype: int64`.

Erfolgs-Stdout-SHA-256: `f6278aafabf111b4ec3b39ad4f6cd67f6f594258284c8f9af8680f21aa0abad6`.

Fester Writer:

- Pfad: `reports/step18/step20C_live_replay.csv`
- `index=False`
- keine automatische Erzeugung von `reports/step18`

Der synthetische Erfolgsoutput besitzt sortierte Trade-Indizes `1, 2, 3`, Entry-Risiken `0.30, 0.50, 0.51`, Multiplikatoren `1.0, 0.5, 0.25` und Scaled PnLs `100.0, -25.0, 10.0`.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout und ohne Dateisystemänderung.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; die erste CSV bleibt unverändert.
3. Ohne geeignete Pre-Entry-Snapshots besitzt das leere DataFrame keine Spalte `trade_index`; `sort_values("trade_index")` propagiert `KeyError` vor Stdout, Funktionsdefinition und Writer.
4. Bei vollständigen Inputs, aber fehlendem `reports/step18`, werden Überschrift, beide Statistikblöcke und die Multiplier-Verteilung ausgegeben. Danach propagiert der Writer `OSError`; die abschließende `written:`-Zeile bleibt aus.
5. Im erfolgreichen Lauf bleiben beide synthetischen Inputs SHA-256-identisch; ausschließlich die fest benannte Output-CSV entsteht.

## Charakterisierungsgate

`tests/state_research/test_step20c_live_replay_characterization.py` umfasst elf Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital, Funktions- und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. inklusive Pre-Entry-Auswahl, `.tail(1)`, Missing-Snapshot-Skip und Trade-Sortierung
4. Multiplikatorgrenzen, Scaled PnL und Row-Schema
5. globale `calc_stats`-Semantik, Kennzahlen und Key-Reihenfolge
6. Stdout-Labels, Writer-Pfad, Writer-Reihenfolge und fehlendes `mkdir`
7. erfolgreicher synthetischer Direktlauf samt Stdout-, CSV- und Nichtmutationsvertrag
8. explizite unsortierte Snapshot-Probe für die CSV-Reihenfolgeabhängigkeit
9. beide Missing-Input-Pfade in Read-Reihenfolge
10. No-Eligible-Snapshot-`KeyError` vor Stdout
11. Missing-Output-Directory-`OSError` nach Statistiken und vor `written:`

Gate-Test-SHA-256: `488879f03b5a5e5089a1680ad203b901a2829143412fbcc515abdb5caeb768be`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S29-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 140/140 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der vollständige direkt erreichbare Vertrag von `analyze_step20C_live_replay.py` ist statisch und synthetisch gebunden. Der verbleibende technische Blocker ist die unmittelbare Ausführung beim Import. S29 korrigiert weder die CSV-Reihenfolgeabhängigkeit noch die historischen Spezifikationsabweichungen oder den fehlenden Outputverzeichnisvertrag und erteilt keinerlei Live-Freigabe.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S30-STEP20C-LIVE-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S30 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle elf S29-Verträge müssen unverändert bleiben; Live-L1, Exchange und Live bleiben gesperrt.
