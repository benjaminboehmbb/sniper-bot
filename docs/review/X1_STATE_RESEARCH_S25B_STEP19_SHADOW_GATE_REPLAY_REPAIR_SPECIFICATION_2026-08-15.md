# X1 State-Research S25B STEP19-Shadow-Gate-Replay-Reparaturspezifikation

Datum: 2026-08-15

Status: PASS (REPARATURSPEZIFIKATION) / IMPLEMENTIERUNG AUSSTEHEND

Basis-Commit: `5a9b7899085b83cb063dde858903d9ff2f100254`

Branch: `codex/x1-state-research-s25b-step19-shadow-gate-replay-repair-specification-2026-08-15`

Ziel einer späteren Implementierung: `scripts/state_research/analyze_step19_shadow_gate_replay.py`

## Zweck und Grenzen

S25B spezifiziert die kleinste zulässige Reparatur des in S25 charakterisierten ungebundenen Singularnamens `THRESHOLD`. Sie setzt die S25A-Entscheidung um: Der Replay verarbeitet pro Aufruf genau eine explizite diagnostische Schwelle, besitzt keinen Default und führt kein Raster aus.

S25B verändert oder führt das Zielskript nicht aus. Reale Research-Inputs werden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wird nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt. Eine Entrypoint-Einkapselung ist vor der Reparatur weiterhin unzulässig.

## Autoritativer Aufrufvertrag

Der spätere direkte Aufruf lautet:

```text
python scripts/state_research/analyze_step19_shadow_gate_replay.py --threshold <FLOAT>
```

Vertrag für `--threshold`:

1. Der Parameter ist erforderlich.
2. Der Parameter muss genau einmal vorkommen.
3. Der Wert muss durch Python als `float` parsebar sein.
4. Der Wert muss endlich sein; `nan`, `inf`, `+inf` und `-inf` sind ungültig.
5. Der Wert muss im geschlossenen Intervall `[0.0, 1.0]` liegen.
6. Es gibt keinen numerischen Default.
7. Es gibt keinen Environment-, Datei-, Store- oder Konstanten-Fallback.
8. Die Schreibweisen `--threshold 0.40` und `--threshold=0.40` sind gleichwertig.

`--help` darf als rein informativer Aufruf vor jedem Research-Zugriff mit Exit-Code 0 enden. Es ist kein Replay-Lauf und benötigt deshalb keinen Schwellenwert.

## Bindungs- und Validierungsreihenfolge

Die spätere Reparatur muss `argparse` verwenden und die Schwelle vollständig binden und validieren, bevor der erste `pandas.read_csv`-Aufruf erreichbar ist.

Autoritative Reihenfolge:

1. Argumentparser erzeugen.
2. `--threshold` als erforderliches, wiederholungserkennendes Float-Argument deklarieren.
3. Argumente parsen.
4. exakt ein Vorkommen prüfen,
5. Endlichkeit prüfen,
6. Intervall `[0.0, 1.0]` prüfen,
7. den validierten Wert an den Singularnamen `THRESHOLD` binden,
8. erst danach den bestehenden Replay-Pfad betreten.

Der derzeit tote Rastername `THRESHOLDS` ist im Zuge der Reparatur zu entfernen. Es darf weder eine Schleife über Schwellenwerte noch eine Auswahl aus diesem Raster eingeführt werden.

Die Argumentbindung bleibt in dieser Reparatur am bestehenden Top Level. S25B autorisiert weder eine `main()`-Funktion noch einen Main-Guard. Die spätere Entrypoint-Einkapselung ist eine eigene Stufe nach repariertem und neu charakterisiertem Direktlauf.

## Fail-closed-Vertrag

Die folgenden Aufrufe müssen vor jedem Inputzugriff, vor Stdout des Replays, vor Outputverzeichnis- oder Dateierzeugung und ohne Inputmutation mit `SystemExit(2)` beziehungsweise Prozess-Exit-Code 2 enden:

- fehlendes `--threshold`,
- `--threshold` ohne Wert,
- nicht numerischer Wert,
- `nan`, `inf`, `+inf` oder `-inf`,
- Wert kleiner als `0.0`,
- Wert größer als `1.0`,
- mehrfach angegebenes `--threshold`,
- unbekannte zusätzliche Argumente.

Die Diagnose wird durch `argparse` nach Stderr geschrieben. Für die fachlichen Validierungsfehler müssen stabile, prüfbare Kernaussagen verwendet werden:

- Mehrfachangabe: `--threshold must be provided exactly once`
- nicht endlicher Wert: `--threshold must be finite`
- Intervallverletzung: `--threshold must be between 0.0 and 1.0 inclusive`

Die standardisierten `argparse`-Meldungen für fehlende, wertlose, nicht numerische oder unbekannte Argumente bleiben zulässig. Vollständige Usage-Fingerprints werden nicht über Python-Patchstände hinweg autorisiert; Exit-Code, Stream, Fehlerklasse und die relevanten Argumentnamen sind zu binden.

## Erfolgsvertrag nach der Reparatur

Mit genau einer gültigen Schwelle gilt weiterhin der in S25 statisch gebundene Einzel-Replay-Vertrag:

- Keep-Prädikat: `mean_shadow_risk <= THRESHOLD`,
- Block-Prädikat: logisches Komplement des Keep-Prädikats,
- identische Trade-/Shadow-Read-Reihenfolge,
- identische inklusive Trade-Lebenszeitfenster,
- identische Row-Felder und Sortierung,
- identische Equity-, Drawdown-, Winrate- und Profit-Factor-Berechnung,
- identische Stdout-Feldreihenfolge,
- identische Writer-Reihenfolge und `index=False`,
- identische feste Outputpfade:
  - `reports/step18/step19_shadow_gate_replay_trades.csv`,
  - `reports/step18/step19_shadow_gate_replay_kept_trades.csv`.

Die ausgegebene Zeile `threshold:` enthält den validierten Floatwert. Die Schwelle ist ein Offline-Szenarioparameter und keine wissenschaftlich validierte oder produktive Trading-Regel.

Die Grenzen `0.0` und `1.0` sind gültig und müssen in synthetischen Fixtures explizit geprüft werden. Ein repräsentativer Innenwert `0.40` muss ausschließlich als Testeingabe geprüft werden; daraus entsteht keine Default- oder Methodenauthority.

## Bewusst unveränderte Altverträge

Die Reparatur darf ausschließlich den Schwellenblocker beheben. Folgende bestehende Verträge bleiben unverändert:

- fehlende Trades-CSV propagiert bei gültiger Schwelle zuerst `FileNotFoundError`,
- fehlende Shadow-CSV propagiert nach erfolgreichem ersten Read `FileNotFoundError`,
- kein gematchtes Zeitfenster propagiert weiterhin `KeyError: trade_index`,
- `reports/step18` wird nicht automatisch erzeugt,
- Outputdateien werden weiterhin erst am Ende und in bestehender Reihenfolge geschrieben,
- Import-Sicherheit wird noch nicht hergestellt.

Insbesondere autorisiert S25B keine Reparatur des leeren-Match-Pfads, keine Writer-Transaktionalität, keine Pfadparametrisierung und kein `mkdir`.

## Erforderliches synthetisches Implementierungsgate

Eine spätere Implementierungsstufe muss das S25-Gate aktualisieren und mindestens folgende Prüfungen ohne reale Research-Inputs binden:

1. Quellstruktur: `THRESHOLDS` entfernt, validierter Singularname vor dem ersten Read gebunden, weiterhin kein `main()` und kein Main-Guard.
2. fehlende Schwelle: Exit 2, Stderr-Diagnose, leeres Replay-Stdout, null Reads und null Writes.
3. wertlose, nicht numerische und unbekannte Argumente: jeweils Exit 2 vor Research-Zugriff.
4. `nan`, beide Infinity-Vorzeichen sowie untere und obere Intervallverletzung: Exit 2 mit gebundener Kernaussage.
5. doppelte Angabe: Exit 2 statt Last-value-wins.
6. `--help`: Exit 0 ohne Research-Zugriff oder Mutation.
7. gültige Grenzen `0.0` und `1.0`: korrekte inklusive Keep-Partition auf synthetischen Inputs.
8. repräsentativer Innenwert `0.40`: erfolgreicher Direktlauf, korrekte Partition, Kennzahlen, Stdout und beide CSVs.
9. Gleichwertigkeit der getrennten und der `=`-Schreibweise.
10. unveränderte Missing-Input-Reihenfolge bei gültiger Schwelle.
11. unveränderter No-Matched-Window-`KeyError` bei gültiger Schwelle.
12. SHA-256-Nichtmutation aller synthetischen Inputs.

Zusätzlich sind die gesamte State-Research-Testkohorte und die TD-005-Regression auszuführen.

## Nicht autorisiert

S25B autorisiert nicht:

- einen numerischen Default oder eine bevorzugte Schwelle,
- die Ausführung des vollständigen Schwellenrasters,
- neue oder schwellenqualifizierte Raster-Outputs,
- reale Research-Inputs,
- Änderungen an Live-L1, Exchange, Live oder IU4,
- Entrypoint-Einkapselung,
- sonstige Fehlerbehebungen oder Refactorings im Zielskript.

## Verifikation dieser Spezifikationsstufe

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- S25A-Commit per Fast-forward in `main`: PASS
- Bestehendes fokussiertes S25-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 113/113 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Die Reparatur ist vollständig spezifiziert: Genau ein expliziter endlicher Floatwert im Intervall `[0.0, 1.0]` wird vor jedem Research-Zugriff fail-closed gebunden. Es existieren weder Default noch Rasterpfad. Alle fachlich unabhängigen Altfehler und die Entrypoint-Struktur bleiben für spätere, getrennte Stufen unverändert.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S25C-STEP19-SHADOW-GATE-REPLAY-SCHWELLENBINDUNGSREPARATUR**. S25C implementiert ausschließlich den spezifizierten erforderlichen `--threshold`-Vertrag am bestehenden Top Level und aktualisiert das synthetische Charakterisierungsgate. Eine Entrypoint-Einkapselung bleibt auch in S25C unzulässig.
