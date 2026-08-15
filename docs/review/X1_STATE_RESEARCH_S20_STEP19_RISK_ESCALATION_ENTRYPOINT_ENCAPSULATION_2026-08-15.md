# X1 State-Research S20 STEP19-Risk-Escalation-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `14fc37d12825794698b722b749e54e723985236d`

Branch: `codex/x1-state-research-s20-step19-risk-escalation-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_risk_escalation.py`

## Zweck

S20 beseitigt für das in S19 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Eligibility-Regeln, Row-Felder, High-Risk-Grenzen, Projektionen, Korrelationen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S19-Baseline-SHA-256: `2b0eafa4c5b8f94509b608d0ecc026ba5bc7f0032bf33459a9e9a1b639df1fe9`
- S20-SHA-256: `11563e497ff72f4e9e95cc2a32656d2b0128594660b4e4a63be11d9b754480c4`
- Umfang S19 → S20: 60 → 66 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Eine AST-Prüfung bestätigt die vollständige Identität des alten Top-Level-Laufzeitbodys mit dem neuen `main()`-Body.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen und mit `.copy()` materialisiert
- Trades mit weniger als drei Snapshots weiterhin übersprungen
- `entry_risk` weiterhin aus `s.iloc[0]` ohne zusätzliche Sortierung
- Row-Felder weiterhin `win`, `pnl`, `entry_risk`, `max_risk`, `mean_risk`, `high_risk_count`, `high_risk_pct`
- Win-Label weiterhin strikt `pnl > 0`
- High-Risk-Count und -Anteil weiterhin strikt `shadow_risk_score > 0.5`
- Gewinnerprojektion weiterhin `win == 1`, Verliererprojektion weiterhin `win == 0`
- projizierte Risikofelder und deren Reihenfolge weiterhin unverändert
- Korrelationen weiterhin `mean_risk`, `max_risk`, `high_risk_pct` jeweils gegen `pnl` mit `Series.corr`
- Ausgabeordnung, Leerzeilen, Beschriftungen und Pandas-Series-Rendering weiterhin unverändert
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `b8a823f50b41e113d1617a3785c9faecb019136ee1b15961cb2f017c491f5cff`

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
3. Ohne eligible Zeitfenster besitzt das leere DataFrame weiterhin keine Spalte `win`. Das Skript gibt ausschließlich eine Leerzeile und `WINNERS` aus; anschließend propagiert die Gewinnerselektion ungefangen `KeyError`. Beide Inputs bleiben unverändert.

S20 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_risk_escalation_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl, Drei-Snapshot-Minimum und feste High-Risk-Grenze
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
4. inklusives Lebenszeitfenster, `.copy()`, Row-Felder und erster Snapshot
5. Gewinner-/Verliererprojektion, Korrelationen, Ausgabeordnung und Nichtwriter-Vertrag
6. stiller, nichtmutierender Import
7. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
8. unveränderte Missing-Input-Pfade
9. unveränderter No-Eligible-Window-`KeyError` nach ausschließlich Leerzeile und `WINNERS`

Gate-Test-SHA-256: `e9a9380bd15a6325eb508abe9c2205987790bc329627e721c0b6f58359bd3dd9`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S20-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 87/87 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S19 → S20: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_risk_escalation.py` ist import-sicher, ohne seinen direkten Eligibility-, High-Risk-, Projektions-, Korrelations-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S21-STEP19-THRESHOLD-SWEEP-CHARAKTERISIERUNGSGATE** für `analyze_step19_threshold_sweep.py`. Es ist mit 60 Zeilen der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Zeitzuordnung, Schwellenraster, Partitionen, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
