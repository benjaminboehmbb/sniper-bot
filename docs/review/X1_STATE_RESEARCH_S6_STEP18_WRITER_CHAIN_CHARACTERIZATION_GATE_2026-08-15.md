# X1 State-Research S6 STEP18-Writer-Chain-Charakterisierungsgate

Datum: 2026-08-15

Status: PASS

Basis-Commit: `0a2e6694e819aed84c06753fdf16d2a55be6e061`

Branch: `codex/x1-state-research-s6-step18-writer-chain-characterization-gate-2026-08-15`

Ziele:

- `scripts/state_research/build_step18_core_pipeline.py`
- `scripts/state_research/analyze_step18_clusters.py`

## Zweck

S6 bindet die vollständige dateischreibende STEP18-Kette, bevor deren Import-Zeit-Ausführung verändert werden darf:

`passive_shadow_risk_snapshots.csv` → Core-Pipeline → `step18_core_metrics.csv` → Cluster-Analyse

Das Gate verändert weder Zielskripte noch Berechnungen. Sämtliche Ausführungen verwenden ausschließlich ein synthetisches Input-Fixture in einem temporären Verzeichnis. Reale Research-Daten und vorhandene Reports werden nicht gelesen oder verändert. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quellidentitäten und Entry-Points

| Skript | Zeilen | SHA-256 | Entry-Point |
|---|---:|---|---|
| `build_step18_core_pipeline.py` | 135 | `05bbf39e66bd87ede3902165c070847f25b86bee9c31f6d52a212b5f7d7a3ae9` | Import-Zeit-Ausführung |
| `analyze_step18_clusters.py` | 80 | `ada1aea9358dff4b543a90e1ee1761ab39b6aec4623bbdb170825fb51dfcf0ce` | Import-Zeit-Ausführung |

Die Core-Pipeline erzeugt `reports/step18` bereits vor dem Versuch, ihren festen Input zu lesen. Die Cluster-Analyse erzeugt kein Verzeichnis und erwartet die Core-Ausgabe an ihrem festen Pfad.

## Writer-Kette und Outputs

Core-Input:

- `live_logs/passive_shadow_risk_snapshots.csv`

Core-Outputs:

1. `reports/step18/step18_core_metrics.csv`
2. `reports/step18/step18_regime_summary.csv`
3. `reports/step18/step18_boundary_events.csv`
4. `reports/step18/step18_collapse_events.csv`
5. `reports/step18/step18_sustainable_topologies.csv`

Cluster-Input:

- `reports/step18/step18_core_metrics.csv`

Cluster-Outputs:

1. `reports/step18/step18_top_boundary_clusters.csv`
2. `reports/step18/step18_top_collapse_clusters.csv`
3. `reports/step18/step18_top_sustainable_clusters.csv`
4. `reports/step18/step18_cluster_summary.csv`

Die Cluster-Analyse verändert keine der fünf Core-Ausgaben. Nach dem vollständigen Lauf existieren exakt der synthetische Input und diese neun Outputs.

## Synthetischer Berechnungsvertrag

Das fünfzeilige Fixture bildet bewusst vier Regime ab:

- `collapse_risk`
- `boundary_stress`
- `sustainable`
- zwei `neutral`-Zeilen

Gebunden werden unter anderem:

- 23 Spalten und fünf Zeilen in `step18_core_metrics.csv`
- vier Zeilen in beiden Regime-/Cluster-Summaries
- je fünf Zeilen in den sechs Top-/Event-Dateien
- erster Boundary-Cluster: `tick-boundary`
- erster Collapse-Cluster: `tick-collapse`
- erster Sustainable-Cluster: `tick-sustainable`

## Kanonische Fingerprints

CSV-Fingerprints werden über UTF-8-Text mit auf `LF` normalisierten Zeilenenden gebildet. Dadurch sind sie nicht von Windows- oder Linux-Zeilenenden abhängig.

| Artefakt | SHA-256 |
|---|---|
| Core-Stdout | `82d731ea08544b2221d0bb0f2b6d3208953c0420259b0c00fd6cbf2b9b2231c8` |
| Cluster-Stdout | `ab31fff40acefb92a171b8c92296bf9fda99a319414f488f7be88cd15e65aa69` |
| `step18_core_metrics.csv` | `5dc9a669dbce1761e1f47d9d959c6c7f29fa6f19913a852286519ea87a25cf5f` |
| `step18_regime_summary.csv` | `9224ad812b32d0e20e893028cfdda3dc8b3cb0db17bc7ef44b1aa0406827b71d` |
| `step18_boundary_events.csv` | `28d4a1da686d894d8893eb6813ace1883f0062fd69178084311cac8ccb5b8444` |
| `step18_collapse_events.csv` | `52b984bac4c1d95165276aaba0c71e4588aa770c9436dcb118737f74b24dbfa4` |
| `step18_sustainable_topologies.csv` | `1a7068e49bfc7f10827fd97403a0812a777355b4630dab72f7670f1072ac379f` |
| `step18_top_boundary_clusters.csv` | `5fc303bc3b62fdd02e034bc164444b63f8d94cba18d4e4fbcf04b01b6263678b` |
| `step18_top_collapse_clusters.csv` | `8cda5f6c40affa325d93a60d8ec997cacb4503e7d9915f22497dbcb653b834e0` |
| `step18_top_sustainable_clusters.csv` | `4ddcc764a68a98a2b572075877dfdfe9edbdee45a74dcbae4a2ec293adc1fd3e` |
| `step18_cluster_summary.csv` | `e40b7b7837bd32065667438915a28a423b957c679925e7e5a6aceeefd234c616` |

## Fail-closed- und Seiteneffektverträge

Core-Pipeline ohne Input:

- Exit-Code ungleich null und `FileNotFoundError`
- kein Stdout und keine Datei
- `reports/step18` wird vor dem Fehler als leeres Verzeichnis erzeugt

Cluster-Analyse ohne Core-Metrics:

- Exit-Code ungleich null und `FileNotFoundError`
- kein Stdout
- keine Datei und kein Verzeichnis wird erzeugt

Core-Pipeline mit fehlenden deklarierten Spalten:

- `ValueError` mit `Missing required columns`
- Input unverändert, keine Outputdatei
- `reports/step18` existiert leer

## Festgestellte implizite Pflichtspalte

Die Core-Pipeline greift auf `shadow_risk_level` zu, führt diese Spalte aber nicht in ihrer Liste `required`. Ein Input mit allen fünf deklarierten Pflichtspalten, jedoch ohne `shadow_risk_level`, passiert daher die explizite Prüfung und endet anschließend fail-closed mit `KeyError`.

S6 dokumentiert diesen bestehenden Vertrag und schwächt ihn nicht ab. Eine fachliche Korrektur der Pflichtspaltenliste wäre eine separate Änderung und ist nicht Bestandteil der Entry-Point-Einkapselung.

## Testumfang

`tests/state_research/test_step18_writer_chain_characterization.py` enthält zehn Prüfungen:

1. beide Quellidentitäten und Zeilenzahlen
2. beide Import-Zeit-Entry-Points
3. Core-Verzeichniserzeugung vor Input-Read
4. Kettenpfade und Writer-Anzahlen 5+4
5. deklarierte und implizite Core-Pflichtspalten
6. erfolgreiche End-to-End-Kette, Nichtmutation, Schemas, Zeilenzahlen, Sortierung und Fingerprints
7. Core-Missing-Input-Seiteneffekt
8. Cluster-Missing-Input ohne Seiteneffekt
9. fehlende deklarierte Pflichtspalten
10. implizit fehlendes `shadow_risk_level`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Neues S6-Gate: 10/10 PASS
- Gesamte State-Research-Testkohorte: 26/26 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskripte verändert: 0
- Reale Research-Inputs oder vorhandene Reports gelesen/verändert: 0

## Ergebnis

Die vollständige STEP18-Writer-Kette ist mit ihren Datenflüssen, neun Outputs, kanonischen Fingerprints und Fehlseiteneffekten gebunden. S6 autorisiert noch keine Änderung der Zielskripte.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S7-STEP18-WRITER-CHAIN-ENTRYPOINT-EINKAPSELUNG**. Beide bestehenden Abläufe werden jeweils vollständig in ein parameterloses `main()` verschoben und per Main-Guard abgeschirmt. Direkte Ketten-Fingerprints und sämtliche Fail-closed-Verträge müssen identisch bleiben; Imports müssen anschließend ohne Inputzugriff, Stdout oder Verzeichniserzeugung möglich sein. Die implizite `shadow_risk_level`-Pflicht bleibt dabei bewusst unverändert.
