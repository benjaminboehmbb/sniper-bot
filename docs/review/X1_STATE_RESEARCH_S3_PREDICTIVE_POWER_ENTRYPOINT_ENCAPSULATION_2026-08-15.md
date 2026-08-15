# X1 State-Research S3 Predictive-Power-Entry-Point-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `a5de0243c66f72e9b5aeb8f7c620329a95c2d7c5`

Branch: `codex/x1-state-research-s3-predictive-power-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step18_predictive_power.py`

## Zweck

S3 beseitigt für den in S2 charakterisierten STEP18-Vertreter ausschließlich die Ausführung beim Import. Die bestehende Berechnung wurde unverändert in `main()` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Kennzahlen, Pandas-Aufrufe, Ausgabezeilen, Fehlerbehandlungen oder Research-Daten verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S2-Baseline-SHA-256: `49f992538ada5ab7ce795aecdd33eced7b6d6e68199998eeb49292807b88e2ad`
- S3-SHA-256: `e32bd3d6545d92d210e317bf9f6db43aa353238f265108cd8b1c558c1b213751`
- Umfang vor S3: 21 Zeilen
- Umfang nach S3: 27 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderte Verträge

- Fester Input: `live_logs/passive_shadow_risk_snapshots.csv`
- Genau ein `pandas.read_csv`
- Spaltenreihenfolge:
  1. `shadow_risk_score`
  2. `regime_mismatch_score`
  3. `atr_stress_score`
  4. `adverse_score_pressure`
- Für jede Spalte genau ein `describe()`
- Keine Datei-Schreiboperation
- Fixture-Stdout: 16 Zeilen, 238 Bytes
- Fixture-Stdout-SHA-256: `7a50a1c59d6541da387a6939600f075a48a3b23cd37fbb5eaf25d3f0787987f5`
- Fehlender Input propagiert `FileNotFoundError` vor jeder Ausgabe

## Neuer Import-Sicherheitsvertrag

Bei einem Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` gilt jetzt:

- null `read_csv`-Aufrufe
- null Stdout
- keine Report- oder Inputmutation
- `main` ist als aufrufbarer expliziter Einstiegspunkt verfügbar

Der direkte Skriptlauf über `__main__` bleibt gegenüber S2 ausgabe- und fehleridentisch.

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Aktualisiertes State-Research-Gate: 7/7 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS

Die Tests verwenden ausschließlich ein injiziertes In-Memory-Pandas-Fixture. Kein realer Research-Input wurde gelesen, erzeugt oder verändert.

## Ergebnis

`analyze_step18_predictive_power.py` ist nun import-sicher, ohne seinen direkten Laufvertrag oder seine Mathematik zu verändern. S3 gilt nur für dieses eine Skript und autorisiert keine automatische Änderung der übrigen 21 Import-Zeit-Ausführer.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S4-STEP18-STDOUT-PAIR-CHARAKTERISIERUNGSGATE** für `analyze_step18_buckets.py` und `analyze_step18_trade_lifetime.py`. Beide sind stdout-only, benötigen aber zwei feste Eingaben und werden deshalb gemeinsam zuerst durch AST-, Fixture-, Ausgabe- und Missing-Input-Verträge gebunden. Erst danach darf ihre Entry-Point-Einkapselung separat erfolgen.
