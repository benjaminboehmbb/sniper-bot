# X1 State-Research S14 STEP19-Blocked-Winners-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `3890b43bc3e022e9dca09ee41ba613db0f1d25e9`

Branch: `codex/x1-state-research-s14-step19-blocked-winners-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_blocked_winners.py`

## Zweck

S14 beseitigt für das in S13 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Schwellen, Partitionen, Gruppierungen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S13-Baseline-SHA-256: `fee296edf91a8f38d41f1f57fb8fbc560d607968fa326c2a3e905bbfe45b6644`
- S14-SHA-256: `f62a34fd96055610a222dab685f62b50b316755be362176043ea197d4cc6908a`
- Umfang S13 → S14: 45 → 51 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Lebenszeitgrenzen
- Trades ohne Snapshot weiterhin übersprungen
- Row-Felder weiterhin `trade_index`, `side`, `pnl`, `exit_reason`, `mean_shadow_risk`
- Schwelle weiterhin fest `0.40`
- Blocked weiterhin strikt `mean_shadow_risk > 0.40`
- Blocked Winners weiterhin `pnl > 0`
- Blocked Losers weiterhin `pnl <= 0`, einschließlich Null-PnL
- Gewinner-Gruppierung weiterhin zuerst nach `side`, dann nach `exit_reason`
- Aggregationen weiterhin `count`, `mean`, `sum`
- Exit-Reason-Ausgabe weiterhin absteigend nach `sum`
- PnL-Summen weiterhin auf zwei Stellen gerundet
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `353a9ce33e95ad176e95bb0436841dee245726fd3be3ab02ca4493430294722b`

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
3. Ohne gematchtes Zeitfenster propagiert der erste Zugriff auf `mean_shadow_risk` weiterhin ungefangen `KeyError` vor Stdout; beide Inputs bleiben unverändert.

S14 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_blocked_winners_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl und feste Schwelle
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. keine Top-Level-Reads oder Aufrufe
4. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
5. inklusives Lebenszeitfenster, Row-Felder und Missing-Window-Skip
6. Blocked-, Gewinner-, Verlierer-, Gruppierungs- und Nichtwriter-Vertrag
7. stiller, nichtmutierender Import
8. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
9. unveränderte Missing-Input- und No-Matched-Window-Pfade

Gate-Test-SHA-256: `c769b3040d167480c539662979af0b0f0d9a12ba31461eb5192c58e86c7d619d`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S14-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 60/60 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

`analyze_step19_blocked_winners.py` ist import-sicher, ohne seinen direkten Schwellen-, Partitions-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S15-STEP19-THRESHOLD-FINE-CHARAKTERISIERUNGSGATE** für `analyze_step19_threshold_fine.py`. Es ist mit 56 Zeilen der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Zeitzuordnung, Schwellenraster, Partitionen, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
