# X1 State-Research S40 STEP20D-Dynamic-Exposure-Scaling-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE

Basis-Commit: `9b37f3f9dcf26bcd33e0f1fda73c9e82f0b2785a`

Branch: `codex/x1-state-research-s40-step20d-dynamic-exposure-scaling-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py`

## Zweck und Grenzen

S40 beseitigt ausschließlich die Ausführung beim Import. Der in S39 charakterisierte Top-Level-Laufzeitbody wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. `START_CAPITAL` bleibt unveränderte Modulkonstante.

Die bestehenden Definitionen `multiplier_from_streaks(risk_series)` und `calc_stats(pnl_col)` lagen innerhalb der früheren Laufzeitsequenz nach den CSV-Reads beziehungsweise nach der DataFrame-Erzeugung. Beide wurden deshalb als lokale Bestandteile AST-identisch mit in `main()` verschoben.

Es wurden keine Inputs, Zeitkonvertierungen, Trade-/Side-Matches, Fenster, Streaks, Schwellen, Multiplikatoren, rückwirkenden PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen, Verteilungen, CSV-Spalten oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP20D v1 bleibt ein methodisch optimistischer Proof of Concept. Die technische Einkapselung macht die rückwirkende Anwendung des finalen Multiplikators weder live-akkurat noch produktionsgeeignet.

## Quell- und Laufzeitidentität

- S39-Baseline-SHA-256: `04bdee183f4854753068851361867cc34283bd77204ac2af1e1adc51365c1fd0`
- S40-SHA-256: `40809ef7a8b70fd73dc33ab342baa1b195a576729328657cef0f2a5ca7a851ca`
- Umfang S39 → S40: 128 → 134 Zeilen
- S39-Top-Level-Laufzeitbody und S40-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `3fae083f08461d5f1ca53ee213871ea3709ec20f137c9ae557c3587ac1893b85`

Der AST-Fingerprint bindet die vollständige frühere Laufzeitsequenz ab dem ersten Trades-Read einschließlich fünf UTC-Konvertierungen, beider lokalen Funktionsdefinitionen, Trade-Schleife, Match-/Merge-/Streak-/Multiplikatorsemantik, rückwirkendem PnL, Sortierung, Statistik, Stdout, Verteilung und Writer. Die sechs zusätzlichen Quellzeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte historische Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py
```

Die Hilfsfunktionen werden erst innerhalb eines `main()`-Laufs definiert und sind nach einem reinen Import nicht als Replay-Zwischenzustände exponiert.

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null UTC-Konvertierungen,
- null Trade-/Snapshot-Matches,
- null Streak- oder Multiplikatorberechnungen,
- null rückwirkende PnL- oder Statistikberechnungen,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar; `multiplier_from_streaks` und `calc_stats` sind vor diesem Aufruf nicht im Modul-Namespace vorhanden.

## Vollständig erhaltener S39-Vertrag

Alle elf S39-Verträge bleiben im direkten Lauf erhalten:

1. `START_CAPITAL = 10000.0`, beide Funktionsdefinitionen in ursprünglicher Sequenz und direkter Ausführungsvertrag.
2. feste Read-Reihenfolge Trades, Lifecycle, Shadow sowie fünf UTC-Konvertierungen mit `utc=True`.
3. strikt exklusive Schwellen `>0.30`, `>0.50`, `>0.70`, drei konsekutive Treffer, Reset und monotoner `min`-Multiplikator `1.0/0.5/0.25/0.1`.
4. exaktes Entry-/case-insensitives Side-Matching, inklusives Shadow-Fenster, Default `1.0` und `merge_asof(nearest, tolerance=2min)` mit `fillna(0.0)`.
5. rückwirkendes `scaled_pnl = original_pnl * final_multiplier`, fünfteilige Row und Sortierung nach `trade_index`.
6. globale DataFrame-Semantik innerhalb der lokalen `calc_stats`-Closure, beide Statistikaufrufe, Stdout, Verteilung und fester Writer ohne `mkdir`.
7. identischer synthetischer Erfolgs-Stdout, sortierte CSV und Input-Nichtmutation.
8. identische `FileNotFoundError`-Pfade für alle drei fehlenden Inputs in fester Read-Reihenfolge vor Stdout.
9. identischer Empty-Trades-`KeyError` auf `trade_index` vor Statistik, Stdout und Writer.
10. identischer Missing-Output-Directory-`OSError` nach beiden Statistikblöcken und Verteilung, aber vor `written:`.
11. identischer `DateParseError` für den ersten ungültigen Trade-Entry-Zeitstempel vor Stdout und ohne Mutation.

Die gebundenen synthetischen Kernergebnisse bleiben:

- Original: Final Equity `10040.0`, Total PnL `40.0`, Profit Factor `1.4`, Max Drawdown `80.0 / 0.0079`.
- STEP20D: Final Equity `10014.0`, Total PnL `14.0`, Profit Factor `1.35`, Max Drawdown `36.0 / 0.0036`.
- Multiplikatoren `0.5,0.25,0.1,1.0`, Scaled PnLs `50.0,-20.0,4.0,-20.0`.

Fester Writer bleibt `reports/step18/step20D_dynamic_exposure_scaling.csv` mit `index=False` und ohne automatische Verzeichniserzeugung.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step20d_dynamic_exposure_scaling_characterization.py` umfasst nun zwölf Prüfungen. Die elf S39-Prüfungen wurden an den `main()`-Body und die lokalen Funktionsdefinitionen angepasst und vollständig erhalten. Hinzugekommen ist:

12. stiller, nichtmutierender Import ohne Reads, Konvertierungen, Berechnungen, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- genau die lokalen Funktionen `multiplier_from_streaks` und `calc_stats` in ursprünglicher Reihenfolge,
- AST-Identität des vollständigen S39-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `3f6eaca487a9177d104ca5e9deabc1fb46d8cef78d9417ad57a06cbbaf8e19f6`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S40-Gate: 12/12 PASS
- Gesamte State-Research-Testkohorte: 198/198 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S39 → S40: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step20D_dynamic_exposure_scaling.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Matches, Streaks, Multiplikatoren, rückwirkendes PnL, Kennzahlen, CSV, Stdout, Verteilung und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S41-STEP20E-TRUE-DYNAMIC-EXPOSURE-REPLAY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py`. Zunächst werden Inputs, Match-/Merge-/Streak-/Segment-PnL-Semantik, Kennzahlen, CSV-/Stdout-Ausgaben, Nichtmutation und Fehlerpfade ausschließlich statisch und mit synthetischen temporären CSVs gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
