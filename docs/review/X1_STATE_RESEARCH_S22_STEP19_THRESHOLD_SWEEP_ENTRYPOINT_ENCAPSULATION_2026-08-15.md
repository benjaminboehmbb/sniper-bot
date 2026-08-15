# X1 State-Research S22 STEP19-Threshold-Sweep-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `c1d96667aa8cb1e7519d48c951cef9bfbcd648e0`

Branch: `codex/x1-state-research-s22-step19-threshold-sweep-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_threshold_sweep.py`

## Zweck

S22 beseitigt für das in S21 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Schwellen, Partitionen, Kennzahlen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S21-Baseline-SHA-256: `20e0f9b1480915db12c7b9ca1c5d19bd8a316e6dae8687b002ced35f56ca0168`
- S22-SHA-256: `fb335ac373dbfc1f70adeb75619a3d67fea58f3e7f545718bcd7090244286e5f`
- Umfang S21 → S22: 60 → 66 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Eine AST-Prüfung bestätigt die vollständige Identität des alten Top-Level-Laufzeitbodys mit dem neuen `main()`-Body.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen
- Trades ohne Snapshot weiterhin übersprungen
- Row-Felder weiterhin `trade_index`, `pnl`, `win`, `mean_shadow_risk`
- Startkapital weiterhin fest `10000.0`
- Schwellenraster weiterhin exakt `0.40`, `0.45`, `0.50`, `0.55`, `0.60`, `0.65`, `0.70`
- Kept weiterhin inklusiv mit `mean_shadow_risk <= threshold`
- Blocked-Anzahl weiterhin `len(df) - len(kept)`
- Gewinner weiterhin `pnl > 0`, Verluste weiterhin `pnl <= 0`
- Equity, Peak und Drawdown weiterhin in ursprünglicher Trade-Reihenfolge
- Profit Factor weiterhin Division durch absoluten Gross Loss oder `inf` bei Gross Loss null
- führende Leerzeile, Header und numerische Formatierung weiterhin unverändert
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `06160c5cc30d60c80b2d02d638b15aeb9c87d78acdb9d40456821ba193309057`

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
3. Ohne gematchtes Zeitfenster werden weiterhin ausschließlich die führende Leerzeile und der Header ausgegeben. Danach propagiert der erste Zugriff auf `mean_shadow_risk` ungefangen `KeyError`; beide Inputs bleiben unverändert.

S22 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_threshold_sweep_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl, Startkapital und festes Schwellenraster
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Keep-Partition, Equity, Drawdown, Gewinner-/Verlustpartition, Profit Factor, Ausgabeformat und Nichtwriter-Vertrag
6. stiller, nichtmutierender Import
7. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
8. unveränderte Missing-Input-Pfade
9. unveränderter No-Matched-Window-`KeyError` nach führender Leerzeile und Header

Gate-Test-SHA-256: `993df9b11a2adcbe4d028746bb81577ad686a5b30daa1a1f95defc74f4538972`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S22-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 96/96 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S21 → S22: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_threshold_sweep.py` ist import-sicher, ohne seinen direkten Schwellen-, Partitions-, Kennzahlen-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S23-STEP19-ENTRY-GATE-CHARAKTERISIERUNGSGATE** für `analyze_step19_entry_gate.py`. Es ist mit 64 Zeilen der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Zeitzuordnung, Entry-Gate-Partitionen, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
