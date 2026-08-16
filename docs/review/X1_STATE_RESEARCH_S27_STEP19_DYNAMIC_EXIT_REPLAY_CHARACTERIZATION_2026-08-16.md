# X1 State-Research S27 STEP19-Dynamic-Exit-Replay-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG)

Basis-Commit: `08c2ad2b03feb5e14c525481b18b4c95605274f4`

Branch: `codex/x1-state-research-s27-step19-dynamic-exit-replay-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step19_dynamic_exit_replay.py`

## Zweck und Grenzen

S27 bindet den bestehenden Direktlauf-, Berechnungs-, Ausgabe- und Fehlervertrag von `analyze_step19_dynamic_exit_replay.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entry-Point-Status

- SHA-256: `f13c4366b15cc59ce7db9329d269a17aa9aa9d09a04e343e7f35de0f029a3bb9`
- Zeilen: 76
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit CSV-Reads, Berechnung und Stdout
- Datei-Writer oder Verzeichniserzeugung: keine

## Fester Input- und Zeitvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge:

1. Trade-`entry_timestamp_utc`
2. Trade-`exit_timestamp_utc`
3. Shadow-`timestamp_utc`

Für jede Konfiguration und jeden Trade wird ein `.copy()` des Shadow-Fensters gebildet. Das Fenster ist an Entry und Exit inklusiv. Trades ohne Snapshot im Fenster werden übersprungen.

Das Skript sortiert weder Trades noch Shadow-Snapshots. Streaks werden deshalb in der vorhandenen Zeilenreihenfolge der Shadow-CSV berechnet. S27 dokumentiert diese bestehende Reihenfolgeabhängigkeit, ohne sie fachlich zu bestätigen oder zu verändern.

## Feste Konfigurationsreihenfolge

Das Skript führt exakt vier Konfigurationen in dieser Reihenfolge aus:

1. Schwelle `0.50`, mindestens `3` aufeinanderfolgende High-Snapshots
2. Schwelle `0.50`, mindestens `5` aufeinanderfolgende High-Snapshots
3. Schwelle `0.60`, mindestens `3` aufeinanderfolgende High-Snapshots
4. Schwelle `0.60`, mindestens `5` aufeinanderfolgende High-Snapshots

Es gibt keine CLI-, Environment- oder Dateikonfiguration und keinen zusätzlichen Rasterpunkt.

## Trigger- und Replay-PnL-Vertrag

Ein Snapshot ist ausschließlich bei `shadow_risk_score > threshold` high. Gleichheit mit der Schwelle ist nicht high.

Die Streak-Berechnung:

- wandelt `high` in Integer um,
- gruppiert zusammenhängende Runs anhand jedes Wahrheitswertwechsels,
- zählt innerhalb jedes Runs kumulativ,
- triggert, sobald irgendein Streak `>= consecutive` erreicht.

Ein unterbrochener High-Run wird zurückgesetzt; getrennte High-Snapshots werden nicht aufsummiert.

Konservative bestehende Replay-Annahme:

- Trigger vorhanden: `replay_pnl = 0.0`
- kein Trigger: finales Trade-PnL unverändert als Float

Die Annahme modelliert keinen Intratrade-Exitpreis. Ein Replay-Trade ist Gewinner ausschließlich bei `replay_pnl > 0`; Trigger-Nullen und originales Null-PnL sind keine Gewinner.

Jede erzeugte Row enthält in fester Reihenfolge:

1. `pnl`
2. `win`
3. `triggered`

## Kennzahlen- und Stdout-Vertrag

Startkapital: `10000.0`.

Pro Konfiguration werden berechnet:

- Equity als Startkapital plus kumulatives Replay-PnL,
- Peak als kumulatives Equity-Maximum,
- prozentualer Drawdown relativ zum Peak,
- Gewinner mit `pnl > 0`,
- Verluste ausschließlich mit `pnl < 0`,
- Profit Factor aus Gross Profit geteilt durch absoluten Gross Loss,
- Profit Factor `inf`, wenn Gross Loss null ist.

Der Direktlauf schreibt ausschließlich Stdout. Header:

```text
threshold,consecutive,trades,early_exits,total_pnl,winrate,pf,max_dd_pct
```

Danach folgt genau eine Zeile pro Konfiguration. PnL besitzt zwei Dezimalstellen; Winrate, Profit Factor und maximaler Drawdown besitzen vier Dezimalstellen.

Der erfolgreiche synthetische Fixture-Lauf bindet:

```text
0.5,3,5,3,-20.00,0.0000,0.0000,0.0020
0.5,5,5,1,40.00,0.2000,1.6667,0.0059
0.6,3,5,2,80.00,0.2000,5.0000,0.0020
0.6,5,5,1,40.00,0.2000,1.6667,0.0059
```

Erfolgs-Stdout-SHA-256: `a8c1b354dc05d20484944afda1a9fe50641e82bb63acd478669987d58b9cfcc2`.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-CSV propagiert `FileNotFoundError` vor Stdout und ohne Dateisystemänderung.
2. Vorhandene Trades-CSV bei fehlender Shadow-CSV propagiert `FileNotFoundError` vor Stdout; die erste CSV bleibt unverändert.
3. Wenn kein Trade ein Shadow-Fenster besitzt, wird der Header ausgegeben. Im ersten Konfigurationslauf besitzt das leere DataFrame keine Spalte `pnl`; der Equity-Zugriff propagiert `KeyError: pnl`, bevor eine Konfigurationszeile ausgegeben wird.
4. Im erfolgreichen Lauf bleiben beide synthetischen Inputs SHA-256-identisch; es entstehen keine Dateien oder Verzeichnisse.

## Charakterisierungsgate

`tests/state_research/test_step19_dynamic_exit_replay_characterization.py` umfasst neun Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital und Konfigurationsreihenfolge
2. Import-Zeit-Ausführer und reiner Stdout-Vertrag ohne Writer
3. feste Read-, UTC-Konvertierungs- und Header-Reihenfolge
4. inklusives Fenster, `.copy()`, Missing-Window-Skip und fehlende Sortierung
5. striktes High-Prädikat, Streak-Reset, Trigger und konservatives Replay-PnL
6. Equity, Drawdown, Verlustpartition, Profit Factor und Formatierung
7. erfolgreicher synthetischer Direktlauf samt Stdout-Fingerprint und Nichtmutation
8. beide Missing-Input-Pfade in Read-Reihenfolge
9. No-Matched-Windows-`KeyError` nach ausschließlich dem Header

Gate-Test-SHA-256: `a5fe9487b7a5253fa68f3c3188ed28d1f35a4ef2310d1c4938743494c6097f9c`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S27-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 128/128 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der vollständige direkt erreichbare Vertrag von `analyze_step19_dynamic_exit_replay.py` ist statisch und synthetisch gebunden. Der verbleibende technische Blocker ist die unmittelbare Ausführung beim Import; S27 ändert weder die wissenschaftliche Exit-Annahme noch die bestehende Reihenfolgeabhängigkeit oder den leeren-DataFrame-Fehler.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S28-STEP19-DYNAMIC-EXIT-REPLAY-ENTRYPOINT-EINKAPSELUNG**. S28 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle neun S27-Verträge müssen unverändert bleiben.
