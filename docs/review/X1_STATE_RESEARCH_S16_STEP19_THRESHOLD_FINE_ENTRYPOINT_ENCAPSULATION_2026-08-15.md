# X1 State-Research S16 STEP19-Threshold-Fine-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `7a7cbc34128893787164c73574795bc80b93d022`

Branch: `codex/x1-state-research-s16-step19-threshold-fine-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_threshold_fine.py`

## Zweck

S16 beseitigt für das in S15 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Schwellen, Partitionen, Kennzahlen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S15-Baseline-SHA-256: `ece62b2ddeb36ab9668ddb66b1ca6abaa87afd0c7b38bb3f068e48b1773e316f`
- S16-SHA-256: `b2d829fc68a24896ad624253b52bb74079ac842c71e4d335148dbb55af38d8de`
- Umfang S15 → S16: 56 → 62 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen
- Trades ohne Snapshot weiterhin übersprungen
- Row-Felder weiterhin `trade_index`, `pnl`, `win`, `mean_shadow_risk`
- Startkapital weiterhin fest `10000.0`
- Schwellenraster weiterhin exakt `0.35`, `0.375`, `0.40`, `0.425`, `0.45`, `0.475`, `0.50`
- Kept weiterhin inklusiv mit `mean_shadow_risk <= threshold`
- Blocked-Anzahl weiterhin `len(df) - len(kept)`
- Gewinner weiterhin `pnl > 0`, Verluste weiterhin `pnl <= 0`
- Equity, Peak und Drawdown weiterhin in ursprünglicher Trade-Reihenfolge
- Profit Factor weiterhin Division durch absoluten Gross Loss oder `inf` bei Gross Loss null
- Total-PnL weiterhin zwei, Winrate, Profit Factor und Max Drawdown weiterhin vier Nachkommastellen
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `1c3545547a356868cd90d756a86d3cdd0693404ab5c7bc72563fe22342fa2b83`

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
3. Ohne gematchtes Zeitfenster wird weiterhin ausschließlich der Header ausgegeben. Danach propagiert der erste Zugriff auf `mean_shadow_risk` ungefangen `KeyError`; beide Inputs bleiben unverändert.

S16 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_threshold_fine_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl, Startkapital und festes Schwellenraster
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
4. inklusives Lebenszeitfenster, Row-Felder, Win-Label und Missing-Window-Skip
5. Keep-Partition, Equity, Drawdown, Gewinner-/Verlustpartition, Profit Factor, Ausgabeformat und Nichtwriter-Vertrag
6. stiller, nichtmutierender Import
7. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
8. unveränderte Missing-Input-Pfade
9. unveränderter No-Matched-Window-Pfad nach ausschließlich dem Header

Gate-Test-SHA-256: `bd1d7499e7c69346fd289e69808e61b4f901b7022620c3d7457a6239e36709f3`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S16-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 69/69 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_threshold_fine.py` ist import-sicher, ohne seinen direkten Schwellen-, Partitions-, Kennzahlen-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S17-STEP19-GATE-QUALITY-CHARAKTERISIERUNGSGATE** für `analyze_step19_gate_quality.py`. Es ist mit 59 Zeilen der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Zeitzuordnung, Gate-Partitionen, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
