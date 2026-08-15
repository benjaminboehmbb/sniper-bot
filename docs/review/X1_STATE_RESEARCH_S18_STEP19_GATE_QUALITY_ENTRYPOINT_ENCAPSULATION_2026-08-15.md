# X1 State-Research S18 STEP19-Gate-Quality-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `4beb520ec7bb5f9162f3d4f53b6933f4b2d9546a`

Branch: `codex/x1-state-research-s18-step19-gate-quality-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_gate_quality.py`

## Zweck

S18 beseitigt für das in S17 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Gate-Grenzen, Gruppen, Kennzahlen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S17-Baseline-SHA-256: `3069392f6c459d2dc54db1278bfa575756228e007159b8da80dff91b9f9a11e8`
- S18-SHA-256: `c252a248795dd2d41d385057b4ff41239e97552347a81551bfdc9ae6098bb961`
- Umfang S17 → S18: 59 → 64 Zeilen

Die fünf zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Main-Guard und notwendige Leerzeilen. Eine AST-Prüfung bestätigt die vollständige Identität des alten Top-Level-Laufzeitbodys mit dem neuen `main()`-Body.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen
- Trades ohne Snapshot weiterhin übersprungen
- Row-Felder weiterhin `pnl`, `win`, `mean_shadow_risk`
- Win-Label weiterhin strikt `pnl > 0.0`
- `HIGH_RISK` weiterhin strikt `mean_shadow_risk > 0.50`
- Grenzgleichheit bei `0.50` weiterhin `LOW_RISK`
- Gruppierung weiterhin `df.groupby("group")` ohne abweichende Sortierparameter
- Gewinner weiterhin `pnl > 0`, Verluste weiterhin `pnl <= 0`
- Profit Factor weiterhin Division durch absoluten Gross Loss oder `inf` bei Gross Loss null
- Ausgabeordnung, Leerzeilen und Rundungen weiterhin unverändert
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `0bf31b04f63da292728641b31840f772101014f5221aeb30aa66255aa729a8d6`

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe
- null Stdout
- null Stderr
- null Dateien
- null Verzeichnisse

Der parameterlose Einstiegspunkt `main` ist anschließend explizit aufrufbar.

## Unveränderte Fail-closed-Verträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; der erste Input bleibt unverändert.
3. Ohne gematchtes Zeitfenster besitzt das leere DataFrame weiterhin keine Spalte `mean_shadow_risk`. Die Gruppen-Zuweisung propagiert ungefangen `KeyError` vor Stdout; beide Inputs bleiben unverändert.

S18 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_gate_quality_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl und feste `0.50`-Gruppengrenze
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Gruppenbildung, Gewinner-/Verlustpartition, Profit Factor, Ausgabeordnung und Nichtwriter-Vertrag
6. stiller, nichtmutierender Import
7. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
8. unveränderte Missing-Input-Pfade
9. unveränderter No-Matched-Window-`KeyError` vor Stdout

Gate-Test-SHA-256: `a68847e16dd2740124d0a1492836935fc1265c96758035c7c45d45c6132e7c95`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S18-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 78/78 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S17 → S18: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_gate_quality.py` ist import-sicher, ohne seinen direkten Gate-, Gruppen-, Kennzahlen-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S19-STEP19-RISK-ESCALATION-CHARAKTERISIERUNGSGATE** für `analyze_step19_risk_escalation.py`. Es ist mit 60 Zeilen gemeinsam mit `analyze_step19_threshold_sweep.py` der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer und steht in der etablierten Provenienzreihenfolge zuerst. Zunächst werden feste Inputs, Zeitzuordnung, Eskalationspartitionen, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
