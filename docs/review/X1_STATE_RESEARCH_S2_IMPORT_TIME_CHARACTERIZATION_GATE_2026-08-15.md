# X1 State-Research S2 Import-Time-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `22bccc97fe478da36de7efc6539c453d33f38ea3`

Branch: `codex/x1-state-research-s2-import-time-characterization-gate-2026-08-15`

Ziel: `scripts/state_research/analyze_step18_predictive_power.py`

## Zweck

S2 bindet das bestehende Verhalten des kleinsten stdout-only Import-Zeit-Ausführers aus der in S1 kartierten STEP18- bis STEP20E-Kohorte. Dieses Gate verändert das Zielskript und seine Mathematik nicht. Es schafft die Voraussetzung für eine spätere, separat freizugebende reine Entry-Point-Einkapselung.

IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Gebundene Quellidentität

- Quell-SHA-256: `49f992538ada5ab7ce795aecdd33eced7b6d6e68199998eeb49292807b88e2ad`
- Quellumfang: 21 Zeilen
- Entry-Point vor der Einkapselung: Ausführung auf Modulebene, kein Main-Guard
- Fester Input: `live_logs/passive_shadow_risk_snapshots.csv`
- Datei-Outputs: keine
- Konsolenausgabe: ja

## Gebundener Berechnungs- und Ausgabeumfang

Das Skript liest den festen Input genau einmal mit `pandas.read_csv`. Anschließend ruft es `describe()` in dieser Reihenfolge auf:

1. `shadow_risk_score`
2. `regime_mismatch_score`
3. `atr_stress_score`
4. `adverse_score_pressure`

Die Ausgabe beginnt mit `---- STEP18 DISTRIBUTIONS ----`, enthält für jede Spalte Namen, `describe()`-Darstellung und Trennzeile und endet mit `DONE`.

Für die isolierte Fixture-Ausführung gilt:

- Stdout-Zeilen: 16
- Stdout-Bytes: 238
- Stdout-SHA-256: `7a50a1c59d6541da387a6939600f075a48a3b23cd37fbb5eaf25d3f0787987f5`

## Fail-closed-Vertrag

Wenn `read_csv` den Input nicht bereitstellen kann, propagiert `FileNotFoundError` unverändert. Vor diesem Fehler wird keine Konsolenausgabe erzeugt. Das Gate ergänzt keinen Fallback, erzeugt keine Ersatzdaten und schwächt keine Eingabeanforderung ab.

## Testisolation

`tests/state_research/test_analyze_step18_predictive_power_characterization.py` enthält sechs Prüfungen:

1. Quellhash und Zeilenzahl
2. heutige Import-Zeit-Ausführung und exakt ein fester CSV-Read
3. Spaltenbestand und Reihenfolge
4. Abwesenheit von Datei-Schreiboperationen
5. exakter Fixture-Read und exakte Konsolenausgabe
6. fail-closed Missing-Input-Verhalten vor Stdout

Die dynamischen Charakterisierungsprüfungen verwenden `runpy.run_path` mit einem ausschließlich im Test injizierten Pandas-Modul. `read_csv` greift dabei nie auf reale Dateien zu: Ein Fixture liefert entweder ein kontrolliertes In-Memory-Objekt oder löst kontrolliert `FileNotFoundError` aus. Es werden keine Research-Inputs oder Reports verändert.

## Verifikation

Verwendeter vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- S2-Charakterisierung: 6/6 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS

Der lokale System-Python besitzt kein NumPy und ist daher nicht der gültige vollständige Regression-Runtime. Mit dem bereits vorhandenen gebündelten Runtime liefen dieselben Regressionstests ohne Fehler; es wurden keine Abhängigkeiten installiert oder verändert.

## Ergebnis

Der aktuelle Vertrag ist vollständig genug gebunden, um die importseitige Ausführung anschließend ohne Rechenänderung hinter einen expliziten Einstiegspunkt zu verschieben. Das Gate autorisiert noch keine Änderung des Zielskripts.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S3-PREDICTIVE-POWER-ENTRYPOINT-EINKAPSELUNG**. Dabei werden ausschließlich die bestehenden Anweisungen in `main()` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. Fester Input, Spaltenreihenfolge, `describe()`-Aufrufe, Stdout und Missing-Input-Verhalten müssen gegenüber diesem Gate identisch bleiben.
