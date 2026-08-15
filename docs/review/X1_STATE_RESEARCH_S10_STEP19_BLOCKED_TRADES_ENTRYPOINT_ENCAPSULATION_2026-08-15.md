# X1 State-Research S10 STEP19-Blocked-Trades-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `297a90fdb50409decef0d6488ef3ba7fc94873f5`

Branch: `codex/x1-state-research-s10-step19-blocked-trades-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_blocked_trades.py`

## Zweck

S10 beseitigt für das in S9 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitfenster, Row-Felder, Filter, Gruppierungen, Aggregationen, Sortierungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S9-Baseline-SHA-256: `2b1f132f7de99f49a0af5c7a9a138fcf842ae2760d2d3b5bf52d86e957cd1c12`
- S10-SHA-256: `376e0a01572aec43fc377a4a282dc58aca12b649ae81510bfcd49976e6798ef5`
- Umfang S9 → S10: 35 → 41 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin Entry, Exit, Shadow
- Shadow-Fenster weiterhin inklusiv an beiden Grenzen
- Trades ohne Snapshot weiterhin übersprungen
- `mean_shadow_risk` weiterhin arithmetischer Fenstermittelwert
- Blocked-Filter weiterhin strikt `mean_shadow_risk > 0.5`
- Side-Gruppierung weiterhin vor Exit-Reason-Gruppierung
- beide `pnl`-Aggregationen weiterhin `count`, `mean`, `sum`
- nur Exit-Reason-Ausgabe weiterhin aufsteigend nach `sum` sortiert
- weiterhin keine Datei-Schreiboperation
- synthetischer Stdout-SHA-256 weiterhin `4c0c24b3d840037590bdd871cd683aa1ca5afca71bc7ca5feb01d2ef6ea67dfb`

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
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError`; der erste Input bleibt unverändert.
3. Ohne gematchtes Shadow-Zeitfenster propagiert der Zugriff auf die fehlende DataFrame-Spalte `mean_shadow_risk` weiterhin ungefangen `KeyError` vor Stdout.

S10 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_blocked_trades_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität und Zeilenzahl
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. keine Top-Level-Reads oder Aufrufe
4. feste Input- und Zeitkonvertierungsreihenfolge innerhalb `main()`
5. inklusives Zeitfenster, Mittelwert und strikter `> 0.5`-Filter
6. Gruppierungs-, Aggregations-, Sortierungs- und Nichtwriter-Vertrag
7. stiller, nichtmutierender Import
8. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
9. unveränderte Missing-Input- und No-Matched-Window-Pfade

Gate-Test-SHA-256: `a98804efaface46da4fedf0ba33faaaee265384155d059cad0831bc0b714ef4c`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S10-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 42/42 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

`analyze_step19_blocked_trades.py` ist import-sicher, ohne seinen direkten Analyse-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S11-STEP19-SHADOW-GATE-CHARAKTERISIERUNGSGATE** für `analyze_step19_shadow_gate.py`. Es ist mit 44 Zeilen der kleinste verbleibende STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Entry-Snapshot-Zuordnung, Gate-Schwelle, Gruppierungen, Stdout, Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
