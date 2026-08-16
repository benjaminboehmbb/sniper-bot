# X1 State-Research S25C STEP19-Shadow-Gate-Replay-Schwellenbindungsreparatur

Datum: 2026-08-16

Status: PASS (REPARATUR UND SYNTHETISCHES CHARAKTERISIERUNGSGATE)

Basis-Commit: `f37a4d7f758aa2e5bd0cc0ae0f342e2bae14c19a`

Branch: `codex/x1-state-research-s25c-step19-shadow-gate-replay-threshold-binding-repair-2026-08-16`

Ziel: `scripts/state_research/analyze_step19_shadow_gate_replay.py`

## Zweck und Grenzen

S25C implementiert ausschließlich die in S25B spezifizierte Top-Level-Bindung für genau eine explizite diagnostische Schwelle. Der bisher ungebundene Singularname `THRESHOLD` ist dadurch im gültigen Direktlauf definiert; das tote Raster `THRESHOLDS` ist entfernt.

Es wurde keine `main()`-Funktion und kein Main-Guard eingeführt. Der bestehende Top-Level-Ausführer bleibt erhalten. Reale Research-Inputs wurden weder gelesen noch verändert; sämtliche dynamischen Prüfungen verwenden ausschließlich synthetische CSVs in temporären Verzeichnissen. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Implementierte Schwellenbindung

Der direkte Aufruf erfordert nun:

```text
python scripts/state_research/analyze_step19_shadow_gate_replay.py --threshold <FLOAT>
```

Die Top-Level-Bindung verwendet `argparse` und führt vor dem ersten `pandas.read_csv` folgende Prüfungen aus:

1. `--threshold` ist erforderlich,
2. `action="append"` macht Mehrfachangaben erkennbar,
3. der Wert muss als `float` parsebar sein,
4. genau ein Wert muss vorhanden sein,
5. der Wert muss mit `math.isfinite` endlich sein,
6. der Wert muss im geschlossenen Intervall `[0.0, 1.0]` liegen,
7. erst danach wird `THRESHOLD` gebunden.

Es gibt keinen Default, Environment-Fallback, Store-Zugriff, Datei-Fallback oder Rasterpfad. Der ehemalige Name `THRESHOLDS` kommt im Zielskript nicht mehr vor.

## Fail-closed-Vertrag

Vor Research-Inputzugriff, Replay-Stdout und Outputerzeugung enden mit Exit-Code 2:

- fehlendes `--threshold`,
- `--threshold` ohne Wert,
- nicht numerischer Wert,
- `nan`, `inf`, `+inf` und `-inf`,
- Wert unter `0.0` oder über `1.0`,
- mehrfache `--threshold`-Angabe,
- unbekannte zusätzliche Argumente.

Die negativen Infinity-Grenze wird als `--threshold=-inf` an die fachliche Endlichkeitsprüfung gebunden. Die getrennte Form `--threshold -inf` wird von `argparse` bereits als wertloses Argument fail-closed abgewiesen. Beide Pfade greifen auf keine Research-Datei zu.

`--help` endet mit Exit-Code 0 und gibt die Usage aus, ebenfalls vor jedem Research-Zugriff.

## Erfolgsvertrag

Die Schreibweisen `--threshold 0.40` und `--threshold=0.40` führen auf identischen synthetischen Inputs zu byte-identischen CSV-Artefakten und identischem Stdout.

Der bestehende Replay-Vertrag bleibt erhalten:

- Keep-Prädikat `mean_shadow_risk <= THRESHOLD`,
- inklusive Entry-/Exit-Lebenszeitfenster,
- Sortierung nach `trade_index`,
- unveränderte Equity-, Drawdown-, Winrate- und Profit-Factor-Berechnung,
- unveränderte Stdout-Feldreihenfolge,
- Writer mit `index=False` in unveränderter Reihenfolge,
- feste Outputpfade:
  - `reports/step18/step19_shadow_gate_replay_trades.csv`,
  - `reports/step18/step19_shadow_gate_replay_kept_trades.csv`.

Die gültigen Grenzen `0.0` und `1.0` werden mit synthetischen Rows geprüft, deren `mean_shadow_risk` jeweils exakt auf der Schwelle liegt. Beide werden wegen des inklusiven Keep-Prädikats behalten. `0.40` ist ausschließlich repräsentative Testeingabe und kein Default oder wissenschaftlich autorisierter Trading-Schwellwert.

## Bewusst unveränderte Altverträge

S25C repariert keine unabhängigen Fehler oder Pfadverträge:

- bei gültiger Schwelle propagiert eine fehlende Trades-CSV weiterhin zuerst `FileNotFoundError`,
- bei gültiger Schwelle propagiert eine fehlende Shadow-CSV weiterhin nach dem ersten Read `FileNotFoundError`,
- ohne gematchtes Zeitfenster propagiert weiterhin `KeyError: trade_index`,
- `reports/step18` wird weiterhin nicht automatisch erzeugt,
- Import-Sicherheit wird weiterhin nicht hergestellt,
- keine Writer-Transaktionalität oder Pfadparametrisierung wurde ergänzt.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step19_shadow_gate_replay_characterization.py` umfasst nun 13 Prüfungen:

1. neue Quellidentität, Einzelbindung, Validierungstexte und Bindung vor den Reads,
2. weiterhin Top-Level-Ausführer ohne `main()` oder Main-Guard,
3. unveränderte Input- und UTC-Konvertierungsreihenfolge,
4. unverändertes inklusives Fenster, Row-Schema, Sortierung und Missing-Window-Skip,
5. unveränderte Replay-Formeln, Writer und Stdout-Reihenfolge,
6. fehlende Schwelle und `--help` vor Research-Zugriff,
7. wertlose, nicht numerische und unbekannte Argumente,
8. nicht endliche und außerhalb des Intervalls liegende Werte,
9. Mehrfachangabe ohne Last-value-wins,
10. erfolgreicher Innenwert `0.40` in beiden CLI-Schreibweisen samt Artefaktparität,
11. erfolgreiche inklusive Grenzen `0.0` und `1.0`,
12. unveränderte Missing-Input-Reihenfolge bei gültiger Schwelle,
13. unveränderter No-Matched-Window-`KeyError` bei gültiger Schwelle.

Zielskript-SHA-256: `f725690becd42d18f63eab224bff47286c1023521d7b64dd260d7550206b2ebb`

Zielskript-Zeilen: 86

Gate-Test-SHA-256: `693cf1454597d8549dfca5f5a1ad37915f55b66c5b25df67a5bd19cbe5101d0f`

## Verifikation

Test-Runtime: Python 3.14.4 mit einer ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht. Repo-`.venv`, Repo-Dateien und Netzwerk blieben für die Runtime-Bereitstellung unverändert.

- Fokussiertes S25C-Gate: 13/13 PASS
- Gesamte State-Research-Testkohorte: 118/118 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

Ausgeführte maßgebliche Befehle:

```text
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest tests.state_research.test_step19_shadow_gate_replay_characterization
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest discover -s tests/state_research -p 'test_*.py'
env PYTHONPATH=/tmp/sniper-bot-s25c-runtime .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
```

Ein vorangegangener Kohortenversuch mit der Repo-Runtime Pandas 2.3.3 wurde nicht als PASS gewertet, weil deren abweichendes `groupby(observed=...)`-Verhalten einen unveränderten STEP18-Stdout-Fingerprint verändert. Die maßgebliche Verifikation verwendet deshalb wie die vorherigen Stufen Pandas 3.0.1.

## Ergebnis

Der Schwellenblocker ist fail-closed repariert. Ein gültiger direkter Replay erfordert genau einen expliziten endlichen Schwellenwert in `[0.0, 1.0]`; ungültige Aufrufe erreichen keine Research-Inputs. Raster, Default, wissenschaftliche Trading-Autorisierung und Entrypoint-Einkapselung wurden nicht eingeführt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S26-STEP19-SHADOW-GATE-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S26 kapselt ausschließlich den nun charakterisierten Top-Level-Vertrag hinter `main() -> None` und Main-Guard ein und muss alle 13 S25C-Verträge einschließlich des erforderlichen `--threshold`-Parameters, der Fail-closed-Argumentpfade, der Erfolgsartefakte und der Altfehler unverändert erhalten.
