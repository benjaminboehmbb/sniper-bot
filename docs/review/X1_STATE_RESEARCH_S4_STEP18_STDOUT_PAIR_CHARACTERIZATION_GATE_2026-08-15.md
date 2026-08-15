# X1 State-Research S4 STEP18-Stdout-Paar-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `c3a5ea911bb2f0a2331aa2bd786a1cdf9715c1dc`

Branch: `codex/x1-state-research-s4-step18-stdout-pair-characterization-gate-2026-08-15`

Ziele:

- `scripts/state_research/analyze_step18_buckets.py`
- `scripts/state_research/analyze_step18_trade_lifetime.py`

## Zweck

S4 bindet das bestehende Verhalten der zwei verbleibenden stdout-only STEP18-Import-Zeit-Ausführer. Das Gate verändert weder Zielskripte noch Mathematik und schafft nur die überprüfbare Baseline für eine spätere, separat freizugebende Entry-Point-Einkapselung.

Es wurden keine realen Research-Daten gelesen oder verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentitäten

| Skript | Zeilen | SHA-256 | Entry-Point |
|---|---:|---|---|
| `analyze_step18_buckets.py` | 49 | `42a1a0ba5c432c1ca00eef4b6416485a503a57db5825307ad857f70713919d44` | Import-Zeit-Ausführung |
| `analyze_step18_trade_lifetime.py` | 58 | `8f235b82746faa50ebd4ea6bdd33104717ee6b821c92c46453299056db3e1600` | Import-Zeit-Ausführung |

Beide Skripte lesen auf Modulebene exakt in dieser Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

Beide sind stdout-only und enthalten keine Datei-Schreiboperation.

## Buckets-Vertrag

`analyze_step18_buckets.py`:

- normalisiert Trade-Entry- und Shadow-Zeitstempel mit `utc=True`
- ordnet jedem Trade den letzten Shadow-Snapshot mit `timestamp_utc <= entry_timestamp_utc` und `tail(1)` zu
- überspringt Trades ohne vorangehenden Snapshot
- bildet `pnl`, binäres `win` und `shadow_risk_score`
- verwendet feste Buckets `[0, 0.2, 0.4, 0.6, 0.8, 1.0]` mit `include_lowest=True`
- aggregiert je Bucket `trades=count(pnl)`, `avg_pnl=mean(pnl)` und `winrate=mean(win)`
- druckt ausschließlich die resultierende Summary mit umgebenden Leerzeilen

Der isolierte Fixture-Vertrag enthält bewusst einen Trade ohne vorherigen Snapshot und vier zuordenbare Trades über vier Risikobereiche.

- Fixture-Stdout-SHA-256: `4253c8fec7c481c68c4a74763d5d86adcf7dd99ea67869c9c51da98d04f223a0`

## Trade-Lifetime-Vertrag

`analyze_step18_trade_lifetime.py`:

- normalisiert Entry-, Exit- und Shadow-Zeitstempel mit `utc=True`
- verwendet das inklusive Zeitfenster `entry_timestamp_utc <= timestamp_utc <= exit_timestamp_utc`
- überspringt Trades ohne Snapshot im Lebenszeitfenster
- bildet `pnl`, binäres `win`, mittleres/maximales Shadow-Risiko und mittleren Meta-State
- druckt die Zahl gematchter Trades
- druckt exakt diese sechs Korrelationen:
  1. `mean_shadow_risk` gegen `pnl`
  2. `mean_shadow_risk` gegen `win`
  3. `max_shadow_risk` gegen `pnl`
  4. `max_shadow_risk` gegen `win`
  5. `mean_meta_state` gegen `pnl`
  6. `mean_meta_state` gegen `win`

Der isolierte Fixture-Vertrag enthält bewusst einen Trade ohne Lebenszeit-Snapshot und drei gematchte Trades mit kontrollierten Risiko-, Meta-State- und PnL-Werten.

- Fixture-Stdout-SHA-256: `bb2c4166fe44f1b76b99398c99fda29a40cee6c8e24902d8c32007c26c5db61c`

## Fail-closed- und Nichtmutationsvertrag

Für beide Skripte gilt:

- Fehlt bereits der erste feste Input, ist der Exit-Code ungleich null.
- `FileNotFoundError` nennt `live_logs/trades_l1_auto_analysis.csv`.
- Vor diesem Fehler entsteht kein Stdout.
- Vor und nach jedem erfolgreichen Fixture-Lauf sind Dateibestand und SHA-256-Manifest im Temp-Verzeichnis identisch.
- Es werden ausschließlich die zwei synthetischen Fixture-CSVs gelesen; keine Reportdatei wird erzeugt.

## Testisolation

`tests/state_research/test_step18_stdout_pair_characterization.py` enthält acht Prüfungen:

1. beide Quellidentitäten und Zeilenzahlen
2. Import-Zeit-Entry-Points und feste Read-Reihenfolge
3. Buckets/Cut/Aggregationsvertrag
4. sechs Trade-Lifetime-Korrelationspaare
5. Abwesenheit von Datei-Schreibern
6. Buckets-Fixture-Ausgabe und Nichtmutation
7. Trade-Lifetime-Fixture-Ausgabe und Nichtmutation
8. fail-closed Missing-First-Input-Verhalten

Die dynamischen Prüfungen starten die unveränderten Skripte als Unterprozesse im jeweiligen temporären Fixture-Verzeichnis. Die CSVs sind vollständig synthetisch; ihre Manifeste werden vor und nach dem Lauf verglichen.

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Neues S4-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 15/15 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskripte verändert: 0
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

Beide stdout-only STEP18-Skripte sind ausreichend charakterisiert, um ihre Import-Zeit-Ausführung anschließend ohne Rechenänderung hinter explizite Einstiegspunkte zu verschieben. S4 autorisiert diese Änderung noch nicht und gilt nicht für die dateischreibenden STEP18-Skripte.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S5-STEP18-STDOUT-PAIR-ENTRYPOINT-EINKAPSELUNG**. Dabei werden ausschließlich die bestehenden Abläufe beider Skripte jeweils in `main()` verschoben und mit einem Main-Guard abgeschirmt. Feste Pfade, Read-Reihenfolge, Mathematik, Stdout-Fingerprints, Fehlerverhalten und Nichtmutation müssen gegenüber S4 identisch bleiben.
