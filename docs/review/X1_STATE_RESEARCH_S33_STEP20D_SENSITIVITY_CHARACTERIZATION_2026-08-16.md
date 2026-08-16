# X1 State-Research S33 STEP20D-Sensitivity-Charakterisierungsgate

Datum: 2026-08-16

Status: PASS (CHARAKTERISIERUNG) / PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE

Basis-Commit: `9d8d6c761be859541a8cff3a5b77cc22aa94215c`

Branch: `codex/x1-state-research-s33-step20d-sensitivity-characterization-2026-08-16`

Ziel: `scripts/state_research/analyze_step20D_sensitivity.py`

## Zweck und Grenzen

S33 bindet den bestehenden Direktlauf-, Berechnungs-, Stdout- und Fehlervertrag von `analyze_step20D_sensitivity.py`, bevor eine Entrypoint-Einkapselung erwogen wird.

`docs/research/STEP20D_dynamic_exposure_scaling_spec.md`, `docs/research/STEP20_FINAL_SUMMARY.md` und `docs/research/STATE_RESEARCH_FINAL_STATUS.md` bewerten STEP20D v1 übereinstimmend als methodisch optimistischen Proof of Concept. Der finale Multiplikator wird rückwirkend auf das vollständige Trade-PnL angewendet und simuliert keine zeitgerechte Exposurereduktion. Das Skript ist deshalb nicht live-akkurat und darf keine Produktions- oder Live-Schlussfolgerung begründen.

Das Zielskript wurde nicht verändert und ausschließlich über synthetische CSVs in temporären Verzeichnissen ausgeführt. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentität und Entrypoint-Status

- SHA-256: `49f37fe4d47e3205e4f6b1eb57cc67330fe2a81258f18d832aa3b849268e7636`
- Zeilen: 97
- Main-Guard: keiner
- Funktionsdefinitionen: genau `get_multiplier(risks, m030, m050, m070)`
- Import-Verhalten: drei CSV-Reads und fünf UTC-Konvertierungen werden vor der Funktionsdefinition unmittelbar ausgeführt; der verbleibende Laufzeitbody wird anschließend ebenfalls auf Modulebene ausgeführt
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

## Konfigurations- und Streak-Vertrag

Das feste Raster besitzt genau drei Einträge:

| Config | `m030` | `m050` | `m070` |
| --- | ---: | ---: | ---: |
| D1 | 0.50 | 0.25 | 0.10 |
| D2 | 0.75 | 0.50 | 0.25 |
| D3 | 1.00 | 0.50 | 0.25 |

`get_multiplier` startet bei `1.0` und zählt drei unabhängige konsekutive Streaks mit strikt exklusiven Schwellen:

- `r > 0.30`
- `r > 0.50`
- `r > 0.70`

Ein Wert exakt auf der Schwelle setzt den jeweiligen Streak auf null. Erst ab drei aufeinanderfolgenden Überschreitungen wird der entsprechende Konfigurationsmultiplikator mit `min(current, configured)` gebunden. Der Multiplikator kann dadurch innerhalb eines Aufrufs nur fallen und wird nach späteren niedrigen Risiken nicht wieder erhöht.

## Trade-, Zeitfenster- und Merge-Vertrag

Lifecycle-Zeilen werden je Trade durch exakte Gleichheit von `entry_timestamp_utc` und durch einen case-insensitiven Side-Vergleich ausgewählt. Shadow-Zeilen werden über das inklusive vollständige Trade-Lifetime-Fenster ausgewählt:

```text
entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc
```

Fehlen Lifecycle- oder Shadow-Zeilen, gilt ohne Merge der Default-Multiplikator `1.0`.

Andernfalls werden beide Ausschnitte nach `timestamp_utc` sortiert und mit `pandas.merge_asof` verbunden:

- Schlüssel: `timestamp_utc`
- Richtung: `nearest`
- Toleranz: `2min`
- nicht gematchte `shadow_risk_score`: `fillna(0.0)`

Die resultierende Risk-Sequenz wird in vorhandener Lifecycle-Reihenfolge an `get_multiplier` übergeben.

## Rückwirkender PnL- und Kennzahlenvertrag

Für jeden Trade und jede Konfiguration entsteht genau eine Row mit den Schlüsseln `pnl` und `mult`:

```text
pnl = float(trade["pnl"]) * final_multiplier
```

Diese Anwendung des erst nach Auswertung des vollständigen Trade-Lifetime-Verlaufs bekannten finalen Multiplikators auf das gesamte Trade-PnL ist die dokumentierte methodische Einschränkung von STEP20D v1.

Startkapital: `10000.0`.

Gebundene Kennzahlen:

- Equity als Startkapital plus kumulatives skaliertes PnL in Trades-Inputreihenfolge,
- Peak als kumulatives Equity-Maximum,
- maximaler prozentualer Drawdown als Maximum von `(peak - equity) / peak`,
- Gewinner mit PnL `> 0`, Verluste mit PnL `< 0`,
- Profit Factor als Gross Profit durch absoluten Gross Loss,
- Profit Factor `inf`, wenn Gross Loss null ist,
- Multiplikatorverteilung über `value_counts()`.

## Stdout-Vertrag

Die Kopfzeile ist fest:

```text
config,total_pnl,pf,max_dd_pct,m_010,m_025,m_050,m_075,m_100
```

Danach folgt je Rastereintrag genau eine CSV-artige Zeile in D1-, D2-, D3-Reihenfolge. Total PnL wird mit zwei, Profit Factor und Max Drawdown werden mit vier Nachkommastellen formatiert. Die fünf Multiplikatorzähler werden in der festen Reihenfolge `0.10`, `0.25`, `0.50`, `0.75`, `1.00` als Integer ausgegeben.

Das synthetische Erfolgsfixture bindet:

```text
D1,14.00,1.3500,0.0036,1,1,1,0,1
D2,25.00,1.4167,0.0050,0,1,1,1,1
D3,50.00,1.8333,0.0050,0,1,1,0,2
```

Es deckt 0.30-, 0.50- und 0.70-Streakbereiche, case-insensitives Lifecycle-Matching sowie den Default-Multiplikator eines Trades ohne Lifecycle-Match ab.

## Fehler- und Nichtmutationsverträge

1. Fehlende Trades-, Lifecycle- und Shadow-CSV propagieren nacheinander `FileNotFoundError` vor Stdout und ohne Dateisystemmutation.
2. Eine leere Trades-CSV mit gültigem Header erlaubt zunächst die Headerausgabe; danach besitzt das leere `DataFrame(rows)` keine Spalte `pnl` und propagiert im ersten D1-Durchlauf `KeyError`.
3. Ein ungültiger erster Trade-Entry-Zeitstempel propagiert Pandas `DateParseError` während der ersten UTC-Konvertierung vor Stdout.
4. Beim erfolgreichen Lauf bleiben alle drei synthetischen Inputs SHA-256-identisch; es entstehen weder Dateien noch Verzeichnisse.

## Charakterisierungsgate

`tests/state_research/test_step20d_sensitivity_characterization.py` umfasst zehn Prüfungen:

1. Quellidentität, Zeilenzahl, Startkapital, Raster, Funktions- und Import-Zeit-Status
2. feste Read- und UTC-Konvertierungsreihenfolge
3. strikt exklusive Schwellen, konsekutive Streaks und monotoner Minimum-Multiplikator
4. Trade-/Side-Matching, inklusives Shadow-Fenster, Default und `merge_asof`
5. rückwirkendes Scaled PnL, Row-Schema und Kennzahlen
6. Stdout-Header, Formatpräzision, Multiplikatorreihenfolge und Writer-Abwesenheit
7. erfolgreicher synthetischer Direktlauf samt exaktem Stdout und Nichtmutation
8. alle drei Missing-Input-Pfade in Read-Reihenfolge
9. Empty-Trades-`KeyError` nach alleiniger Headerausgabe
10. fehlerhafter erster Zeitstempel vor Header und ohne Mutation

Gate-Test-SHA-256: `a5356caf2884c016cd33869445cc7d4d05afe889adcf89b30eddead9a47b026d`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S33-Gate: 10/10 PASS
- Gesamte State-Research-Testkohorte: 162/162 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der direkt erreichbare Vertrag von `analyze_step20D_sensitivity.py` ist statisch und synthetisch gebunden. S33 verändert weder das feste D1-D3-Raster noch die methodisch optimistische rückwirkende PnL-Anwendung. Es erteilt keinerlei IU4-, Live-L1-, Exchange-, Live- oder Produktionsfreigabe.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S34-STEP20D-SENSITIVITY-ENTRYPOINT-EINKAPSELUNG**. S34 verschiebt ausschließlich den charakterisierten Top-Level-Laufzeitbody AST-identisch in `main() -> None` und ergänzt einen Main-Guard. Alle zehn S33-Verträge müssen vollständig erhalten bleiben; Live-L1, Exchange und Live bleiben gesperrt.
