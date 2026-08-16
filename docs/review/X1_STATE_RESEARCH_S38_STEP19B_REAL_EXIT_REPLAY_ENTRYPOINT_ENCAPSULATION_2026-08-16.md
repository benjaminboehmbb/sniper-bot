# X1 State-Research S38 STEP19B-Real-Exit-Replay-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / STEP19 DYNAMIC EXIT NOT VALIDATED

Basis-Commit: `6d0dfb4af823859ddccd50862bec41be9cd384f8`

Branch: `codex/x1-state-research-s38-step19b-real-exit-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step19B_real_exit_replay.py`

## Zweck und Grenzen

S38 beseitigt ausschließlich die Ausführung beim Import. Der in S37 charakterisierte Top-Level-Laufzeitbody wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. `START_CAPITAL`, `THRESHOLD` und `CONSECUTIVE` bleiben unveränderte Modulkonstanten.

Es wurden keine Inputs, Zeitkonvertierungen, Trade-/Side-Matches, Fenster, Streaks, Schwellen, Trigger, Exit-Typen, PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen, Groupby-Ausgaben, CSV-Spalten oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP19 Dynamic Exit bleibt `NOT VALIDATED`. Die technische Einkapselung ändert weder die fehlende Generalisierung im dokumentierten 500k-Fenster noch den Status als nicht robuste eigenständige Trading-Regel.

## Quell- und Laufzeitidentität

- S37-Baseline-SHA-256: `414fe6edbf7a315351b86f9973f2c633c0a055e448c30352ffe300c896686ffc`
- S38-SHA-256: `293a8384997a113e916ea45f1c82904a07ca835d7c83372223d77bcdf041db70`
- Umfang S37 → S38: 115 → 121 Zeilen
- S37-Top-Level-Laufzeitbody und S38-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `93b636ea0508bb669c58a59378742771009fc00d7dde1f719c19f97fba3103aa`

Der AST-Fingerprint bindet die vollständige frühere Laufzeitsequenz ab dem ersten Trades-Read einschließlich fünf UTC-Konvertierungen, Trade-Schleife, Match-/Merge-/Streak-/Triggersemantik, aller Exit-Typen, Replay-PnL, Sortierung, zehn CSV-Spalten, Kennzahlen, Stdout, Groupby und Writer. Die sechs zusätzlichen Quellzeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte historische Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step19B_real_exit_replay.py
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null UTC-Konvertierungen,
- null Trade-/Snapshot-Matches,
- null Streak-, Trigger- oder Replay-PnL-Berechnungen,
- null Statistik- oder Groupby-Berechnungen,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar.

## Vollständig erhaltener S37-Vertrag

Alle elf S37-Verträge bleiben im direkten Lauf erhalten:

1. `START_CAPITAL = 10000.0`, `THRESHOLD = 0.50`, `CONSECUTIVE = 3` sowie der direkte Ausführungsvertrag.
2. feste Read-Reihenfolge Trades, Lifecycle, Shadow und feste fünfteilige UTC-Konvertierungsreihenfolge mit `utc=True`.
3. exaktes Entry-/case-insensitives Side-Matching, inklusives Shadow-Fenster, `merge_asof(nearest, tolerance=2min)` und `fillna(0.0)`.
4. strikt exklusive High-Schwelle, gruppierte True-Streaks, erster Trigger und die drei Exit-Typen.
5. Floatkonvertierung von Entry-, Current-Price und Size, Long-/Nicht-Long-PnL, Original-PnL-Pfade sowie fünfteilige Basis-Row.
6. Sortierung nach `trade_index`, fünf Ableitungsspalten, Kennzahlen, Stdout, Groupby und fester CSV-Writer ohne `mkdir`.
7. identischer synthetischer Erfolgs-Stdout, sortierte zehnspaltige CSV und Input-Nichtmutation.
8. identische `FileNotFoundError`-Pfade für alle drei fehlenden Inputs in fester Read-Reihenfolge vor Stdout.
9. identischer Empty-Trades-`KeyError` auf `trade_index` vor Stdout und Writer.
10. identischer Missing-Output-Directory-`OSError` nach Statistiken und Groupby, aber vor `written:`.
11. identischer `DateParseError` für den ersten ungültigen Trade-Entry-Zeitstempel vor Stdout und ohne Mutation.

Die gebundenen synthetischen Kernergebnisse bleiben:

- vier Trades, ein Dynamic Exit,
- Final Equity `9964.0`, Total PnL `-36.0`, Return `-0.0036`,
- Winrate `0.25`, Profit Factor `0.4545`,
- Max Drawdown absolut `40.0`, prozentual `0.004`,
- Exit-Type-Summen `-40.0`, `10.0`, `-6.0`.

Fester Writer bleibt `reports/step18/step19B_real_exit_replay.csv` mit `index=False` und ohne automatische Verzeichniserzeugung.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step19b_real_exit_replay_characterization.py` umfasst nun zwölf Prüfungen. Die elf S37-Prüfungen wurden an den `main()`-Body angepasst und vollständig erhalten. Hinzugekommen ist:

12. stiller, nichtmutierender Import ohne Reads, Konvertierungen, Berechnungen, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S37-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `41329d989a5ef39d976a7d7aeefcf49bb1b4d0f45fbea44f4449cc6c3640525e`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S38-Gate: 12/12 PASS
- Gesamte State-Research-Testkohorte: 186/186 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S37 → S38: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19B_real_exit_replay.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Feste Konfiguration, Matches, Streaks, Trigger, Exit-Typen, Replay-PnL, Kennzahlen, CSV, Stdout, Groupby und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `NOT VALIDATED`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S39-STEP20D-DYNAMIC-EXPOSURE-SCALING-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py`. Zunächst werden Inputs, Match-/Merge-/Streak-/Multiplikatorsemantik, rückwirkendes PnL, Kennzahlen, CSV-/Stdout-Ausgaben, Nichtmutation und Fehlerpfade ausschließlich statisch und mit synthetischen temporären CSVs gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
