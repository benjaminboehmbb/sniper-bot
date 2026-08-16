# X1 State-Research S26 STEP19-Shadow-Gate-Replay-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS

Basis-Commit: `8f865233412abeaeb5ef3a50583452ed7532527f`

Branch: `codex/x1-state-research-s26-step19-shadow-gate-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step19_shadow_gate_replay.py`

## Zweck und Grenzen

S26 beseitigt ausschließlich die Ausführung beim Import. Der in S25C vollständig charakterisierte Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Argumente, Schwellenprüfungen, Pfade, Zeitfenster, Row-Felder, Partitionen, Kennzahlen, Rundungen, Stdout-Zeilen, Writer oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quell- und Laufzeitidentität

- S25C-Baseline-SHA-256: `f725690becd42d18f63eab224bff47286c1023521d7b64dd260d7550206b2ebb`
- S26-SHA-256: `4e89b5111ad1d45cca17e2967ba654fb72f7f3690c5338d01611519cea93354f`
- Umfang S25C → S26: 86 → 92 Zeilen
- S25C-Top-Level-Laufzeitbody und S26-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `349371b3524c855ecb7865847bf86b99a052df3790e766887d989f3196250508`

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Der AST-Fingerprint bindet den vollständigen verschobenen Laufzeitbody einschließlich Argumentparser, Validierungsreihenfolge, Reads, Replay-Berechnung, Stdout und Writer.

## Neuer Entrypoint-Vertrag

Das Modul definiert genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Die diagnostische Schwelle bleibt ein erforderliches CLI-Argument und wird weiterhin innerhalb des Laufzeitbodys über `argparse` gelesen:

```text
python scripts/state_research/analyze_step19_shadow_gate_replay.py --threshold <FLOAT>
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null Argumentparsing,
- null CSV-Lesezugriffe,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar. Der Import autorisiert oder startet keinen Replay.

## Vollständig erhaltener S25C-Vertrag

Alle 13 S25C-Verträge bleiben im direkten Lauf erhalten:

1. `THRESHOLDS` bleibt entfernt; `THRESHOLD` wird vor Reads gebunden.
2. `--threshold` bleibt erforderlich.
3. Genau eine Angabe bleibt erforderlich; Mehrfachangaben scheitern statt Last-value-wins.
4. Nicht numerische Werte und unbekannte Argumente scheitern vor Research-Zugriff.
5. `nan`, beide Infinity-Vorzeichen und Werte außerhalb `[0.0, 1.0]` scheitern fail-closed.
6. `--help` endet vor Research-Zugriff mit Exit-Code 0.
7. Die Grenzen `0.0` und `1.0` bleiben gültig und inklusiv.
8. `--threshold 0.40` und `--threshold=0.40` bleiben artefaktidentisch.
9. Keep bleibt `mean_shadow_risk <= THRESHOLD`.
10. Read-, Zeitkonvertierungs-, Row- und Sortierreihenfolge bleiben unverändert.
11. Kennzahlen, Stdout und beide CSV-Outputs bleiben unverändert.
12. Missing-Input-Fehlerreihenfolge bleibt bei gültiger Schwelle unverändert.
13. No-Matched-Window propagiert weiterhin `KeyError: trade_index`.

Es gibt weiterhin keinen Schwellen-Default, keinen Rasterlauf, keine automatische Erzeugung von `reports/step18`, keine Writer-Transaktionalität und keine wissenschaftliche oder produktive Trading-Schwellenfreigabe.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step19_shadow_gate_replay_characterization.py` umfasst nun 14 Prüfungen. Die 13 S25C-Prüfungen wurden an den `main()`-Body angepasst und unverändert erhalten. Hinzugekommen ist:

14. stiller, nichtmutierender Import ohne Argumentparsing, Reads, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None`,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S25C-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `4986335175c92c3ae63eac6cb896a1db32901aececba8749ea22999b1e7f0b3a`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S26-Gate: 14/14 PASS
- Gesamte State-Research-Testkohorte: 119/119 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S25C → S26: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

Ausgeführte maßgebliche Befehle:

```text
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest tests.state_research.test_step19_shadow_gate_replay_characterization
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest discover -s tests/state_research -p 'test_*.py'
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
```

## Ergebnis

`analyze_step19_shadow_gate_replay.py` ist import-sicher, ohne den in S25C reparierten und charakterisierten Einzel-Schwellen-Replay zu verändern. Direkter Replay, Argumentfehler, Erfolgsartefakte und bestehende Altfehler bleiben vollständig gebunden.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S27-STEP19-DYNAMIC-EXIT-REPLAY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step19_dynamic_exit_replay.py`. Zunächst werden der 76-zeilige Import-Zeit-Ausführer, seine feste Schwelle, Zeitfenster, dynamische Exit-Logik, Kennzahlen, Outputs, Nichtmutation und Fehlerpfade ausschließlich synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
