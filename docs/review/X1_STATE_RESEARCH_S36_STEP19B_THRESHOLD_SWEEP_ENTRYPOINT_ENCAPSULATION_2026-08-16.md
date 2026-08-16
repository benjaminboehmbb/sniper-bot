# X1 State-Research S36 STEP19B-Threshold-Sweep-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / STEP19 DYNAMIC EXIT NOT VALIDATED

Basis-Commit: `e00a26c9a2838fc767e3cc4314170cc8af4017fb`

Branch: `codex/x1-state-research-s36-step19b-threshold-sweep-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step19B_threshold_sweep.py`

## Zweck und Grenzen

S36 beseitigt ausschließlich die Ausführung beim Import. Der in S35 charakterisierte Top-Level-Laufzeitbody wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. `START_CAPITAL` und das feste Fünfer-`configs`-Raster bleiben unveränderte Modulkonstanten.

Es wurden keine Inputs, Zeitkonvertierungen, Trade-/Side-Matches, Fenster, Streaks, Schwellen, Trigger, PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP19 Dynamic Exit bleibt `NOT VALIDATED`. Die technische Einkapselung ändert weder die fehlende Generalisierung im dokumentierten 500k-Fenster noch den Status als nicht robuste eigenständige Trading-Regel.

## Quell- und Laufzeitidentität

- S35-Baseline-SHA-256: `98236fc02a9b65f85c7411e3d42d2caefe41bf06e0d4958542c498005db3e6fe`
- S36-SHA-256: `50742723a4000f5ef31c6e7f687f4986951beb84994fa3bd96eb4cb9637abc15`
- Umfang S35 → S36: 114 → 120 Zeilen
- S35-Top-Level-Laufzeitbody und S36-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `c01314f0f18f5b1070ce511f1fd3c09a3cb0bd3599f4fcfd144aa4afcae5e18d`

Der AST-Fingerprint bindet die vollständige frühere Laufzeitsequenz ab dem ersten Trades-Read einschließlich aller fünf UTC-Konvertierungen, Headerausgabe, Fünfer-Raster, Trade-Schleife, Merge-/Streak-/Triggersemantik, Replay-PnL, Kennzahlen und Ergebniszeilen. Die sechs zusätzlichen Quellzeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte historische Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step19B_threshold_sweep.py
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null UTC-Konvertierungen,
- null Trade-/Snapshot-Matches,
- null Streak-, Trigger- oder Replay-PnL-Berechnungen,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar.

## Vollständig erhaltener S35-Vertrag

Alle zehn S35-Verträge bleiben im direkten Lauf erhalten:

1. `START_CAPITAL = 10000.0`, das feste Raster `(0.5,3)`, `(0.5,5)`, `(0.6,3)`, `(0.6,5)`, `(0.7,3)` und der direkte Ausführungsvertrag.
2. feste Read-Reihenfolge Trades, Lifecycle, Shadow sowie fünf UTC-Konvertierungen mit `utc=True`.
3. exaktes Entry-/case-insensitives Side-Matching, inklusives Shadow-Fenster, Original-PnL-Default und `merge_asof(nearest, tolerance=2min)` mit `fillna(0.0)`.
4. strikt exklusive High-Schwelle, gruppierte True-Streaks und Auswahl des ersten `streak >= CONSECUTIVE`-Snapshots.
5. Floatkonvertierung von Entry-, Current-Price und Size, Long-/Nicht-Long-PnL, Triggerflag und Row-Schema.
6. Equity, Peak, Drawdown, Gewinner-/Verliererpartition, Profit Factor, Dynamic-Exit-Summe, Stdout-Header, Präzision, Reihenfolge und Writer-Abwesenheit.
7. identischer synthetischer Erfolgs-Stdout und vollständige Input-/Dateisystem-Nichtmutation.
8. identische `FileNotFoundError`-Pfade für alle drei fehlenden Inputs in fester Read-Reihenfolge vor Stdout.
9. identischer Empty-Trades-`KeyError` nach alleiniger Headerausgabe und ohne Mutation.
10. identischer `DateParseError` für den ersten ungültigen Trade-Entry-Zeitstempel vor Stdout und ohne Mutation.

Die gebundenen synthetischen Ergebniszeilen bleiben:

```text
0.5,3,2,-5.00,0.8571,0.0029
0.5,5,1,95.00,3.7143,0.0035
0.6,3,1,101.00,4.4828,0.0029
0.6,5,1,95.00,3.7143,0.0035
0.7,3,0,70.00,2.1667,0.0059
```

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step19b_threshold_sweep_characterization.py` umfasst nun elf Prüfungen. Die zehn S35-Prüfungen wurden an den `main()`-Body angepasst und vollständig erhalten. Hinzugekommen ist:

11. stiller, nichtmutierender Import ohne Reads, Konvertierungen, Berechnungen, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S35-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `0c6d8851d143758b43b6e2f2c77b45821954bf5bc3336e00ba5c09d27cdacb73`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S36-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 174/174 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S35 → S36: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19B_threshold_sweep.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Raster, Matches, Streaks, Trigger, Replay-PnL, Kennzahlen, Stdout und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `NOT VALIDATED`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S37-STEP19B-REAL-EXIT-REPLAY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step19B_real_exit_replay.py`. Zunächst werden Inputs, Match-/Merge-/Streak-/Exit-PnL-Semantik, Kennzahlen, CSV-/Stdout-Ausgaben, Nichtmutation und Fehlerpfade ausschließlich statisch und mit synthetischen temporären CSVs gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
