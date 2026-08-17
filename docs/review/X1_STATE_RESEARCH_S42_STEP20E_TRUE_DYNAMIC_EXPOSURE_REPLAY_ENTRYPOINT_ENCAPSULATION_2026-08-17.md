# X1 State-Research S42 STEP20E-True-Dynamic-Exposure-Replay-Entrypoint-Einkapselung

Datum: 2026-08-17

Status: PASS / STEP20E NOT VALIDATED

Basis-Commit: `e85cdf217aecf3fd4b1f7798496c18a769a1f292`

S41-Vertrags-Commit: `836d612165a44c351d10a737b8c9ca2a8fd3ce76`

Branch: `codex/x1-state-research-s42-step20e-true-dynamic-exposure-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py`

## Zweck und Grenzen

S42 beseitigt ausschließlich die Ausführung beim Import. Der in S41 charakterisierte Top-Level-Laufzeitbody wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. `START_CAPITAL` bleibt unveränderte Modulkonstante.

Die bestehenden Definitionen `update_multiplier(...)` und `stats(pnl_col)` lagen innerhalb der früheren Laufzeitsequenz. Beide wurden deshalb als lokale Bestandteile AST-identisch mit in `main()` verschoben.

Es wurden keine Inputs, UTC-Konvertierungen, Trade-/Side-Matches, Zeitfenster, Merge-Parameter, Streaks, Schwellen, Multiplikatoren, Segment-PnL-Berechnungen, Reduktionszählungen, Statistiken, Rundungen, Stdout-Zeilen, Verteilungen, CSV-Spalten, Writer oder Fehlerpfade verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP20E bleibt fachlich `NOT VALIDATED`. Die technische Einkapselung erteilt keine Produktions-, Live- oder Methodenfreigabe.

## Recovery-Baseline

Vor S42 wurde der Recovery-Branch `codex/spark-divergence-recovery-2026-08-17` per Fast-forward in `main` integriert. Der Git-Tree des Basis-Commits `e85cdf2` ist exakt identisch zum S41-Tree. Die drei Spark-Abweichungen bleiben ausschließlich als nachvollziehbare Revert-Historie erhalten; sie sind nicht Bestandteil des S42-Dateistands.

## Quell- und Laufzeitidentität

- S41-Baseline-SHA-256: `14667ea1f44d380e807523a0a71402b3786eeafff306d7ee3e4a8f44d29438ee`
- S42-SHA-256: `2d9e3eb1e32745661cfcbea8e840c0916465c579345da4b8a5e018570aa0ff08`
- Umfang S41 → S42: 177 → 178 Zeilen
- S41-Top-Level-Laufzeitbody und S42-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `4400afd463d3d071c888484b01823bc4869d46cdfdf7001de696bd629155ef4d`

Der AST-Fingerprint bindet die vollständige frühere Laufzeitsequenz ab dem ersten Trades-Read einschließlich drei CSV-Reads, fünf UTC-Konvertierungen, beider lokalen Funktionsdefinitionen, Trade-Schleife, Match-/Merge-/Streak-/Multiplikatorsemantik, Segment- und Final-PnL, Reduktionszählung, Sortierung, Statistik, Stdout, Verteilungen und Writer.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte historische Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py
```

Die Hilfsfunktionen werden erst innerhalb eines `main()`-Laufs definiert und sind nach einem reinen Import nicht im Modul-Namespace exponiert.

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe;
- null UTC-Konvertierungen;
- null Trade-/Snapshot-Matches;
- null Streak-, Multiplikator-, Segment-PnL- oder Statistikberechnungen;
- null Stdout;
- null Stderr;
- null Dateien;
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar; `update_multiplier` und `stats` sind vor diesem Aufruf nicht im Modul-Namespace vorhanden.

## Vollständig erhaltener S41-Vertrag

Alle elf S41-Verträge bleiben im direkten Lauf erhalten:

1. `START_CAPITAL = 10000.0`, beide Funktionsdefinitionen in ursprünglicher Sequenz und unveränderter Direktausführungsvertrag.
2. feste Read-Reihenfolge Trades, Lifecycle, Shadow sowie fünf UTC-Konvertierungen mit `utc=True`.
3. strikt exklusive Schwellen `>0.30`, `>0.50`, `>0.70`, drei konsekutive Treffer, Reset und monotoner `min`-Multiplikator `1.0/0.5/0.25/0.1`.
4. exaktes Entry-/case-insensitives Side-Matching, inklusives Shadow-Fenster, Default-Pfad und `merge_asof(nearest, tolerance=2min)` mit `fillna(0.0)`.
5. Segment-PnL vor Multiplikatorupdate, Finalsegment, einmalige Reduktionszählung pro Snapshot, sechsteiliges Row-Schema und Sortierung nach `trade_index`.
6. lokale `stats`-Closure über `df`, beide Statistikaufrufe, beide Verteilungen, Stdout und fester Writer ohne `mkdir`.
7. identischer synthetischer Erfolgs-Stdout, sortierte CSV und Input-Nichtmutation.
8. identische `FileNotFoundError`-Pfade für alle drei fehlenden Inputs in fester Read-Reihenfolge vor Stdout.
9. identischer Empty-Trades-`KeyError` auf `trade_index` vor Statistik, Stdout und Writer.
10. identischer Missing-Output-Directory-`OSError` nach Statistik und Verteilungen, aber vor `written:`.
11. identischer `DateParseError` für den ersten ungültigen Trade-Entry-Zeitstempel vor Stdout und ohne Mutation.

Die gebundenen synthetischen Kernergebnisse bleiben:

- Original: Final Equity `10040.0`, Total PnL `40.0`, Profit Factor `1.4`, Max Drawdown `80.0 / 0.0079`.
- STEP20E: Final Equity `9983.65`, Total PnL `-16.35`, Profit Factor `0.2922`, Max Drawdown `23.1 / 0.0023`.
- Replay-PnLs `3.5`, `3.25`, `-3.1`, `-20.0`.
- Final-Multiplikatoren `0.5`, `0.25`, `0.1`, `1.0`; Reduktionen `1`, `1`, `1`, `0`.

Der Writer bleibt `reports/step18/step20E_true_dynamic_exposure_replay.csv` mit `index=False` und ohne automatische Verzeichniserzeugung.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step20e_true_dynamic_exposure_replay_characterization.py` umfasst nun zwölf Prüfungen. Die elf S41-Prüfungen wurden an den `main()`-Body und die lokalen Funktionsdefinitionen angepasst und vollständig erhalten. Hinzugekommen ist:

12. stiller, nichtmutierender Import ohne Reads, Konvertierungen, Berechnungen, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene;
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf;
- keine Top-Level-Reads oder Top-Level-Ausführungscalls;
- genau die lokalen Funktionen `update_multiplier` und `stats` in ursprünglicher Reihenfolge;
- AST-Identität des vollständigen S41-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `e71661626f462289b21054f4c463055b9a832e126d81e0eb5c2a7dc7a4ce5a3a`

## Verifikation

Referenzruntime: Python 3.14 mit der ausschließlich temporär unter `/tmp` bereitgestellten lokalen Cache-Schicht NumPy `2.3.5` / Pandas `3.0.1`, entsprechend S40/S41.

- fokussiertes S42-Gate: 12/12 PASS;
- gesamte State-Research-Testkohorte: 210/210 PASS;
- bestehende Regression-Suite: 170/170 PASS;
- Laufzeit-AST-Identität S41 → S42: PASS;
- `git diff --check`: PASS;
- reale Research-Inputs gelesen oder verändert: 0;
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0.

Unter der Repo-`.venv` mit Pandas `2.3.3` scheitert unabhängig von S42 weiterhin genau der ältere STEP18-Buckets-Stdout-Vertrag durch versionsabhängige Warnungs- und Formatierungsbytes. Das fokussierte S42-Gate besteht auch dort 12/12. Für die kohortenweite Vergleichbarkeit ist die bereits dokumentierte Referenzruntime autoritativ.

## Ergebnis

`analyze_step20E_true_dynamic_exposure_replay.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Matches, Streaks, Multiplikatoren, Segment-PnL, Reduktionszählung, Kennzahlen, CSV, Stdout, Verteilungen und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `NOT VALIDATED`; IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S43-IMPORT-SAFETY-CLOSURE-AUDIT**. S43 revidiert ausschließlich statisch und read-only die vollständige Kohorte der 43 getrackten Dateien unter `scripts/state_research/`, bestätigt den Abschluss der ursprünglichen 22 Import-Zeit-Ausführer, aktualisiert den Kohorten-Fingerprint und weist verbleibende Main-Guard-, Import-Seiteneffekt- oder Evidenzlücken aus. S43 verändert keine Research-Skripte und liest keine realen Research-Inputs.
