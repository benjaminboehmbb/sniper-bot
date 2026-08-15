# X1 State-Research S24 STEP19-Entry-Gate-Entrypoint-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `1990608fa3e8c46151b65d9b09474425e97663d9`

Branch: `codex/x1-state-research-s24-step19-entry-gate-entrypoint-encapsulation-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_entry_gate.py`

## Zweck

S24 beseitigt für das in S23 charakterisierte STEP19-Skript ausschließlich die Ausführung beim Import. Der bestehende Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Pfade, Zeitzuordnungen, Row-Felder, Korrelationen, Schwellen, Partitionen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität

- S23-Baseline-SHA-256: `fded5b2a284fcf311bbcb2285314a1a160d6e1cc988b0964a54aa94e0417ab5f`
- S24-SHA-256: `e64700e37cfbb23d2f3a8c758a2e3d3bd26a4a2b2f603b098ffa35a635f2503a`
- Umfang S23 → S24: 64 → 70 Zeilen

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Eine AST-Prüfung bestätigt die vollständige Identität des alten Top-Level-Laufzeitbodys mit dem neuen `main()`-Body.

## Unveränderter Direktlaufvertrag

- Reads weiterhin zuerst Trades-Auto-CSV, dann Passive-Shadow-CSV
- UTC-Konvertierung weiterhin nur Trade-Entry und Shadow-Timestamp
- Snapshot-Selektion weiterhin `timestamp_utc <= entry_timestamp_utc`
- Auswahl weiterhin `.tail(1)` in bestehender Input-Reihenfolge ohne zusätzliche Sortierung
- Trades ohne verfügbaren Snapshot weiterhin übersprungen
- Auflösung weiterhin über `snap.iloc[0]`
- Row-Felder weiterhin `pnl`, `win`, `entry_shadow_risk`
- Win-Label weiterhin strikt `pnl > 0.0`
- Korrelationen weiterhin Entry-Risk gegen PnL und anschließend Entry-Risk gegen Win
- Schwellenraster weiterhin exakt `0.35`, `0.40`, `0.45`, `0.50`, `0.55`, `0.60`
- Kept weiterhin inklusiv mit `entry_shadow_risk <= threshold`
- Blocked-Anzahl weiterhin `len(df) - len(kept)`
- Gewinner weiterhin `pnl > 0`, Verluste weiterhin `pnl <= 0`
- Profit Factor weiterhin Division durch absoluten Gross Loss oder `inf` bei Gross Loss null
- Ausgabeordnung, Leerzeilen und numerische Formatierung weiterhin unverändert
- weiterhin keine Datei-Schreiboperation
- Erfolgs-Stdout-SHA-256 weiterhin `69019689e29dd09d7e680a6120ba6ed7bfdde391329932e844fa597e62059e24`

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
3. Ohne eligible Entry-Snapshot besitzt das leere DataFrame weiterhin keine Spalte `entry_shadow_risk`. Das Skript gibt ausschließlich eine Leerzeile und `ENTRY_RISK vs PNL` aus; anschließend propagiert die erste Korrelation ungefangen `KeyError`. Beide Inputs bleiben unverändert.

S24 behebt oder lockert keinen dieser Altverträge.

## Aktualisiertes Gate

`tests/state_research/test_step19_entry_gate_characterization.py` umfasst neun Prüfungen:

1. neue Quellidentität, Zeilenzahl und festes Schwellenraster
2. genau ein parameterloses `main() -> None` und ein Main-Guard
3. feste Input- und UTC-Konvertierungsreihenfolge innerhalb `main()`
4. inklusive Entry-Zuordnung, `.tail(1)`, `.iloc[0]`, Row-Felder und Missing-Snapshot-Skip
5. Korrelationen, Keep-Partition, Gewinner-/Verlustpartition, Profit Factor, Ausgabeordnung und Nichtwriter-Vertrag
6. stiller, nichtmutierender Import
7. erfolgreicher Direktlauf mit unverändertem Stdout-Fingerprint
8. unveränderte Missing-Input-Pfade
9. unveränderter No-Eligible-Snapshot-`KeyError` nach ausschließlich Leerzeile und erster Überschrift

Gate-Test-SHA-256: `051087e6836a8934111d63ab2eb9d26871fab729ab34bef04532a2e362186565`

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S24-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 105/105 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S23 → S24: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_entry_gate.py` ist import-sicher, ohne seinen direkten Entry-Zuordnungs-, Korrelations-, Schwellen-, Partitions-, Ausgabe- oder Fail-closed-Vertrag zu verändern.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S25-STEP19-SHADOW-GATE-REPLAY-CHARAKTERISIERUNGSGATE** für `analyze_step19_shadow_gate_replay.py`. Es ist mit 70 Zeilen der kleinste verbleibende historische STEP19- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden feste Inputs, Zeitzuordnung, Gate-Partitionen, Replay-Kennzahlen, beide CSV-Ausgaben, Stdout, Input-Nichtmutation und Fehlerpfade synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
