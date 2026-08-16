# X1 State-Research S35 STEP19B-Threshold-Sweep-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / STEP19 DYNAMIC EXIT NOT VALIDATED

Basis-Commit: `741cee0ef594be83072291c711bafc580ccf67ae`

Branch: `codex/x1-state-research-s35-step19b-threshold-sweep-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step19B_threshold_sweep.py`

## Zweck und Grenzen

S35 bindet den bestehenden Direktlauf-, Raster-, Replay-PnL-, Stdout- und Fehlervertrag von `analyze_step19B_threshold_sweep.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

`docs/research/STEP19B_dynamic_risk_exit_validation.md` dokumentiert zunächst drei richtungsgleiche 200k-Resultate, anschließend aber eine 500k-Validierung mit schlechterem PnL, Profit Factor und Drawdown. Der dokumentierte Endstatus lautet deshalb `STEP19 Dynamic Exit: not validated`. `shadow_risk_score` bleibt für Trade-Quality-Analyse informativ, ist aber keine robuste eigenständige Trading-Regel.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entrypoint-Status

- SHA-256: `98236fc02a9b65f85c7411e3d42d2caefe41bf06e0d4958542c498005db3e6fe`
- Zeilen: 114
- Main-Guard: keiner
- Funktionsdefinitionen: keine
- Import-Verhalten: unmittelbarer Laufversuch mit drei CSV-Reads, fünf UTC-Konvertierungen, Replay-Berechnung und potenziellem Stdout
- Writer: keiner; die Ergebnisse werden ausschließlich nach Stdout geschrieben

## Fester Input- und Zeitvertrag

Read-Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/trade_lifecycle_snapshots.csv`
3. `live_logs/passive_shadow_risk_snapshots.csv`

UTC-Konvertierungsreihenfolge, jeweils mit `utc=True`:

1. Trades `entry_timestamp_utc`
2. Trades `exit_timestamp_utc`
3. Lifecycle `timestamp_utc`
4. Lifecycle `entry_timestamp_utc`
5. Shadow `timestamp_utc`

Fehlende Inputs propagieren `FileNotFoundError` in exakt dieser Read-Reihenfolge vor jeder Stdout-Ausgabe.

## Konfigurationsraster

Das feste Raster läuft in dieser Reihenfolge:

| Schwelle | Konsekutive Snapshots |
| ---: | ---: |
| 0.5 | 3 |
| 0.5 | 5 |
| 0.6 | 3 |
| 0.6 | 5 |
| 0.7 | 3 |

Das Raster wird weder extern parametrisiert noch validiert. S35 charakterisiert nur diese fünf historischen Konfigurationen und erklärt keine davon zur autoritativen oder live-fähigen Einstellung.

## Trade-, Zeitfenster- und Merge-Vertrag

Für jeden Trade wird das ursprüngliche `pnl` zunächst als Float in `replay_pnl` übernommen; `triggered` startet bei `0`.

Lifecycle-Zeilen werden durch exakte Gleichheit von `entry_timestamp_utc` und durch einen case-insensitiven Side-Vergleich ausgewählt. Shadow-Zeilen werden über das inklusive vollständige Trade-Lifetime-Fenster ausgewählt:

```text
entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc
```

Sind Lifecycle- oder Shadow-Ausschnitt leer, findet kein Merge statt. Original-PnL und `triggered = 0` bleiben erhalten.

Andernfalls werden beide Ausschnitte nach `timestamp_utc` sortiert und mit `pandas.merge_asof` verbunden:

- Schlüssel: `timestamp_utc`
- Richtung: `nearest`
- Toleranz: `2min`
- nicht gematchte `shadow_risk_score`: `fillna(0.0)`

## High-Streak- und Triggervertrag

Ein Snapshot ist ausschließlich bei strikt exklusiver Überschreitung high:

```text
shadow_risk_score > THRESHOLD
```

Gleichheit mit der Schwelle ist nicht high. Zustandswechsel zwischen True und False bilden getrennte Gruppen. Innerhalb jeder Gruppe wird die Integerdarstellung von `high` kumuliert:

- True-Gruppen zählen `1, 2, 3, ...`,
- False-Gruppen bleiben wegen der kumulierten Nullen bei `0`.

Damit kann nur ein konsekutiver True-Run `streak >= CONSECUTIVE` erreichen. Aus allen qualifizierenden Rows wird stets `trigger.iloc[0]`, also der erste erreichende Lifecycle-Snapshot, verwendet.

## Replay-PnL- und Row-Vertrag

Am ersten Trigger werden `entry_price`, `current_price` und `position_size` als Float gelesen.

Long:

```text
replay_pnl = (current_price - entry_price) * position_size
```

Jeder normalisierte Side-Wert ungleich `long` nimmt ohne weitere Validierung den Else-Zweig:

```text
replay_pnl = (entry_price - current_price) * position_size
```

Nach einem Trigger gilt `triggered = 1`. Jede Eingabe-Trade-Row erzeugt je Konfiguration genau eine Ergebnis-Row mit fester Schlüsselreihenfolge:

1. `pnl`
2. `triggered`

## Kennzahlen- und Stdout-Vertrag

Startkapital: `10000.0`.

Gebundene Berechnungen je Konfiguration:

- Equity als Startkapital plus kumulatives Replay-PnL in Trades-Inputreihenfolge,
- Peak als kumulatives Equity-Maximum,
- Drawdown-Prozent je Row als `(peak - equity) / peak`,
- Gewinner mit PnL `> 0`,
- Verluste mit PnL `< 0`; Null-PnL gehört zu keiner der beiden Summen,
- Profit Factor als Gross Profit durch absoluten Gross Loss,
- Profit Factor `inf`, wenn Gross Loss null ist,
- `dynamic_exits` als Summe der binären `triggered`-Spalte.

Die feste Kopfzeile lautet:

```text
threshold,consecutive,dynamic_exits,total_pnl,pf,max_dd_pct
```

Danach folgt je Rastereintrag genau eine CSV-artige Zeile. Total PnL wird mit zwei, Profit Factor und Max Drawdown werden mit vier Nachkommastellen ausgegeben.

Das synthetische Erfolgsfixture bindet exakt:

```text
0.5,3,2,-5.00,0.8571,0.0029
0.5,5,1,95.00,3.7143,0.0035
0.6,3,1,101.00,4.4828,0.0029
0.6,5,1,95.00,3.7143,0.0035
0.7,3,0,70.00,2.1667,0.0059
```

Damit werden drei- und fünfteilige True-Runs, Long- und Short-Replay-PnL, der erste Trigger-Snapshot, case-insensitives Side-Matching sowie beide Default-Pfade für fehlende Lifecycle- beziehungsweise Shadow-Matches abgedeckt.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-, Lifecycle- und Shadow-CSV propagieren nacheinander `FileNotFoundError` vor Stdout und ohne Dateisystemmutation.
2. Eine leere Trades-CSV mit gültigem Header erlaubt zunächst die Headerausgabe; danach besitzt das leere `DataFrame(rows)` keine Spalte `pnl`, und die erste Konfiguration propagiert `KeyError`.
3. Ein ungültiger erster Trade-Entry-Zeitstempel propagiert Pandas `DateParseError` während der ersten UTC-Konvertierung vor Stdout.
4. Beim erfolgreichen Lauf bleiben alle drei synthetischen Inputs SHA-256-identisch; es entstehen weder Dateien noch Verzeichnisse.

## Charakterisierungsgate

`tests/state_research/test_step19b_threshold_sweep_characterization.py` umfasst zehn Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital, Raster und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. Entry-/Side-Matching, inklusives Shadow-Fenster, Default-PnL und `merge_asof`
4. strikt exklusive High-Schwelle, gruppierte True-Streaks und erste Triggerauswahl
5. Preis-/Size-Konvertierung, Long-/Nicht-Long-PnL, Triggerflag und Row-Schema
6. Kennzahlen, Stdout-Header, Formatpräzision, Reihenfolge und Writer-Abwesenheit
7. erfolgreicher synthetischer Direktlauf samt exaktem Stdout und Nichtmutation
8. alle drei Missing-Input-Pfade in Read-Reihenfolge
9. Empty-Trades-`KeyError` nach alleiniger Headerausgabe
10. fehlerhafter erster Zeitstempel vor Header und ohne Mutation

Gate-Test-SHA-256: `c47c73ee2e6a74c75f8a9878d4116927a64a8633770acb803a4a091568bbe6aa`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S35-Gate: 10/10 PASS
- Gesamte State-Research-Testkohorte: 173/173 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der direkt erreichbare Vertrag von `analyze_step19B_threshold_sweep.py` ist statisch und synthetisch gebunden. S35 verändert weder Raster, Triggerlogik, Replay-PnL, Kennzahlen noch Fehlerpfade und erteilt keinerlei IU4-, Live-L1-, Exchange-, Live- oder Produktionsfreigabe. Der fachliche Status bleibt `NOT VALIDATED`.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S36-STEP19B-THRESHOLD-SWEEP-ENTRYPOINT-EINKAPSELUNG**. S36 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle zehn S35-Verträge müssen vollständig erhalten bleiben; Live-L1, Exchange und Live bleiben gesperrt.
