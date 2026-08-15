# X1 State-Research S5 STEP18-Stdout-Paar-Entry-Point-Einkapselung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `af44bfa9a7e211eff109750b42a0485472acfb75`

Branch: `codex/x1-state-research-s5-step18-stdout-pair-entrypoint-encapsulation-2026-08-15`

Ziele:

- `scripts/state_research/analyze_step18_buckets.py`
- `scripts/state_research/analyze_step18_trade_lifetime.py`

## Zweck

S5 beseitigt für die zwei in S4 charakterisierten stdout-only STEP18-Skripte ausschließlich die Ausführung beim Import. Jeder bestehende Ablauf wurde unverändert in ein parameterloses `main()` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Feste Pfade, Read-Reihenfolge, Pandas-Operationen, Mathematik, Stdout, Fehlerverhalten und Nichtmutation bleiben unverändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentitäten

| Skript | S4-Baseline-SHA-256 | S5-SHA-256 | Zeilen S4 → S5 |
|---|---|---|---:|
| `analyze_step18_buckets.py` | `42a1a0ba5c432c1ca00eef4b6416485a503a57db5825307ad857f70713919d44` | `89fe1b9cdd1c28027c07775b4e2520a077b0206becf31782b21cff8d882f64ec` | 49 → 55 |
| `analyze_step18_trade_lifetime.py` | `8f235b82746faa50ebd4ea6bdd33104717ee6b821c92c46453299056db3e1600` | `1f9b0d69bff434a84ad8a45243b241ec77dc24412b553645840701dfd02e2af1` | 58 → 64 |

Die sechs zusätzlichen Zeilen je Skript entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Unveränderte Direktlaufverträge

Beide Skripte lesen weiterhin exakt in dieser Reihenfolge:

1. `live_logs/trades_l1_auto_analysis.csv`
2. `live_logs/passive_shadow_risk_snapshots.csv`

Buckets-Vertrag:

- Snapshot-Zuordnung, Skip-Pfad, Row-Aufbau, feste Cut-Bins und drei Aggregationen unverändert
- Fixture-Stdout-SHA-256 weiterhin `4253c8fec7c481c68c4a74763d5d86adcf7dd99ea67869c9c51da98d04f223a0`

Trade-Lifetime-Vertrag:

- inklusives Lebenszeitfenster, Skip-Pfad, Risiko-/Meta-State-Aggregate und sechs Korrelationen unverändert
- Fixture-Stdout-SHA-256 weiterhin `bb2c4166fe44f1b76b99398c99fda29a40cee6c8e24902d8c32007c26c5db61c`

Für beide gilt weiterhin:

- keine Datei-Schreiboperation
- identische Fixture-Manifeste vor und nach dem Direktlauf
- fehlender erster Input führt vor Stdout zu `FileNotFoundError`

## Neuer Import-Sicherheitsvertrag

Bei einem Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` gilt nun für beide Skripte:

- null CSV-Lesezugriffe
- null Stdout
- null erzeugte oder veränderte Dateien
- `main` ist als aufrufbarer expliziter Einstiegspunkt verfügbar

Die Import-Probes werden absichtlich in leeren temporären Verzeichnissen ohne `live_logs` ausgeführt. Ihr Erfolg beweist, dass die festen Inputs erst durch einen expliziten `main()`-Aufruf benötigt werden.

## Aktualisiertes Gate

`tests/state_research/test_step18_stdout_pair_characterization.py` umfasst nach S5 neun Prüfungen:

1. neue Quellidentitäten und Zeilenzahlen
2. genau je ein parameterloses `main()` und ein Main-Guard
3. feste Reads ausschließlich innerhalb von `main()`
4. Buckets/Cut/Aggregationsvertrag
5. sechs Trade-Lifetime-Korrelationspaare
6. Abwesenheit von Datei-Schreibern
7. beide direkten Fixture-Ausgaben und Nichtmutation
8. beide stillen, nichtmutierenden Import-Pfade
9. fail-closed Missing-First-Input-Verhalten im Direktlauf

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Aktualisiertes Paar-Gate: 9/9 PASS
- Gesamte State-Research-Testkohorte: 16/16 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0

## Ergebnis

`analyze_step18_buckets.py` und `analyze_step18_trade_lifetime.py` sind import-sicher, ohne ihren direkten Laufvertrag oder ihre Mathematik zu verändern. Zusammen mit S3 sind damit alle drei stdout-only STEP18-Analyseskripte abgeschirmt. S5 autorisiert keine Änderung der beiden dateischreibenden STEP18-Skripte.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S6-STEP18-WRITER-CHAIN-CHARAKTERISIERUNGSGATE** für `build_step18_core_pipeline.py` und `analyze_step18_clusters.py`. Das Gate muss die Abhängigkeit Core-Pipeline → Core-Metrics → Cluster-Ausgaben, alle neun Datei-Outputs, Verzeichniserzeugung, Input-/Output-Manifeste und Missing-Input-Seiteneffekte zunächst isoliert binden. Erst danach darf über Entry-Point-Einkapselung der Writer entschieden werden.
