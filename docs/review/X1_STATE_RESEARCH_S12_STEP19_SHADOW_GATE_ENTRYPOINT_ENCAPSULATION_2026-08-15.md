# X1 State-Research S12 STEP19-Shadow-Gate-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `e8163da3a4368ce43f730fbb4fbcd4a8f5857a6f`

Branch: `codex/x1-state-research-s12-step19-shadow-gate-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_shadow_gate.py`

## Zweck

S12 beseitigt für das in S11 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Schwellen, Partitionen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S11-Baseline-SHA-256: `ae4d8d8fc8dccdc5fd454d6ed1069d44bb0abcbf06a6d6c4a8e3471feee07a0e`
- S12-SHA-256: `7d397773c00399ca725e59d176d7af2143df6638c4af73ac2666b2a54639ea96`
- Umfang S11 → S12: 44 → 50 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen
- Trades ohne Snapshot weiterhin übersprungen
- Row-Felder weiterhin `pnl`, `win`, `mean_shadow_risk`
- Schwellenfolge weiterhin `[0.50, 0.60, 0.70, 0.80]`
- Kept weiterhin `<= threshold`, Blocked weiterhin `> threshold`
- Kept-PnL weiterhin auf zwei Stellen gerundet
- Kept-Winrate weiterhin auf vier Stellen gerundet
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `e2868a8d9a760d9b3f75ddf4434d4bc048a82066782864c43d90fec24dc8acfb`

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
3. Ohne gematchtes Zeitfenster wird weiterhin zunächst exakt `TOTAL TRADES: 0` ausgegeben. Der erste Zugriff auf `mean_shadow_risk` propagiert anschließend ungefangen `KeyError`; beide Inputs bleiben unverändert.

S12 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_shadow_gate_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität und Zeilenzahl
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. keine Top-Level-Reads oder Aufrufe
4. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
5. inklusives Lebenszeitfenster, Row-Felder und Missing-Window-Skip
6. Schwellen-, Partitionierungs-, Rundungs- und Nichtwriter-Vertrag
7. stiller, nichtmutierender Import
8. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
9. unveränderte Missing-Input- und No-Matched-Window-Pfade

Gate-Test-SHA-256: `cdb12ebce8e2ef389a8d0a53cb4fd69311212e5b75792a3177c38b3ae975e7c6`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S12-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 51/51 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

`analyze_step19_shadow_gate.py` ist import-sicher, ohne seinen direkten Sweep-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S13-STEP19-BLOCKED-WINNERS-CHARAKTERISIERUNGSGATE** für `analyze_step19_blocked_winners.py`. Es ist mit 45 Zeilen der kleinste verbleibende STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden Inputs, Zeitzuordnung, Gewinnerfilter, Schwellenlogik, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
