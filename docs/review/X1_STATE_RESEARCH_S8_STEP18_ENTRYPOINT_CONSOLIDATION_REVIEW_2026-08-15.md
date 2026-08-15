# X1 State-Research S8 STEP18-Entrypoint-Konsolidierungsreview

Datum: 2026-08-15

Status: PASS

Entscheidung: NO-GO für eine gemeinsame STEP18-CLI oder Fünfer-Orchestrierung

Basis-Commit: `b3f9f68583b21ba936ed057e41abd79897956bef`

Branch: `codex/x1-state-research-s8-step18-entrypoint-consolidation-review-2026-08-15`

## Zweck und Scope

S8 prüft, ob die fünf in S3, S5 und S7 import-sicher gemachten STEP18-Skripte eine fachlich begründete gemeinsame CLI- oder Orchestrierungsnaht benötigen. Der Review verändert keine Research-Skripte, Pfade, Mathematik, Outputs oder Fehlerverträge.

IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt. Reale Research-Daten wurden weder gelesen noch verändert.

## Gebundene Entrypoints

| Rolle | Skript | SHA-256 | Zeilen | Input | Seiteneffekt |
|---|---|---|---:|---|---|
| Einzelanalyse | `analyze_step18_predictive_power.py` | `e32bd3d6545d92d210e317bf9f6db43aa353238f265108cd8b1c558c1b213751` | 27 | Passive-Shadow-CSV | Stdout |
| Einzelanalyse | `analyze_step18_buckets.py` | `89fe1b9cdd1c28027c07775b4e2520a077b0206becf31782b21cff8d882f64ec` | 55 | Trades-Auto-CSV, Passive-Shadow-CSV | Stdout |
| Einzelanalyse | `analyze_step18_trade_lifetime.py` | `1f9b0d69bff434a84ad8a45243b241ec77dc24412b553645840701dfd02e2af1` | 64 | Trades-Auto-CSV, Passive-Shadow-CSV | Stdout |
| Writer Stufe 1 | `build_step18_core_pipeline.py` | `57a819ed2fb04f075e059b5dc60cf4fba3b2c284b4b27e0120f30e01512fcf98` | 141 | Passive-Shadow-CSV | `reports/step18` plus fünf CSVs und Stdout |
| Writer Stufe 2 | `analyze_step18_clusters.py` | `65918c7346b1819862dc17db2124768f0de6c8ca45daa93b0a846a4cbc80c5a3` | 86 | `step18_core_metrics.csv` | vier CSVs und Stdout |

Pfadlegende:

- Passive-Shadow-CSV: `live_logs/passive_shadow_risk_snapshots.csv`
- Trades-Auto-CSV: `live_logs/trades_l1_auto_analysis.csv`

## Gemeinsame Minimalform

Alle fünf Skripte besitzen genau:

- ein parameterloses `main()`
- einen Main-Guard
- null Cross-Imports innerhalb der Fünfergruppe
- import-sichere Top-Level-Struktur

Ein kombinierter Import-Probe in einem leeren temporären Verzeichnis bestätigte für alle fünf zusammen:

- null Stdout
- null Stderr
- null Dateien
- null Verzeichnisse
- fünf aufrufbare `main`-Objekte

Diese Minimalform ist eine gemeinsame technische Konvention, aber noch keine gemeinsame fachliche Pipeline.

## Abhängigkeitsgraph

Die einzige Artefaktkante innerhalb der Fünfergruppe lautet:

`build_step18_core_pipeline.py` → `reports/step18/step18_core_metrics.csv` → `analyze_step18_clusters.py`

Die drei stdout-only Analysen:

- konsumieren kein Artefakt der Writer-Kette
- erzeugen kein Artefakt für einen anderen STEP18-Entrypoint
- besitzen unterschiedliche Inputmengen und Auswertungslogiken
- sind untereinander reihenfolgeunabhängig

Damit existiert eine Zweierkette und drei unabhängige Einzelanalysen, keine Fünferkette.

## Konsolidierungsbewertung

### Nicht ausreichende Gemeinsamkeiten

Die Gemeinsamkeiten `pandas`, feste lokale Pfade und parameterloses `main()` rechtfertigen keinen neuen Owner. Eine gemeinsame CLI würde keinen aktuell duplizierten Dispatcher, keine bestehende Importkante und keinen nachgewiesenen Bedienvertrag ersetzen.

### Risiken einer Fünfer-Orchestrierung

Eine neue Orchestrierung würde erstmals:

- drei unabhängige stdout-only Analysen mit neun Datei-Outputs koppeln
- eine neue globale Ausführungs- und Fehlerreihenfolge definieren
- bislang getrennte Missing-Input-Verträge zusammenziehen
- Stdout-Reihenfolge und Teilfehlersemantik neu festlegen müssen
- einen neuen Owner ohne bestehenden Consumer oder nachgewiesene Anforderung schaffen

Das wäre eine Architekturerweiterung und keine reine Konsolidierung.

### Core/Cluster-Paar

Das Core/Cluster-Paar ist bereits durch die feste Artefaktkante eindeutig geordnet. S6 und S7 binden die vollständige Kette, Fingerprints und Fail-closed-Semantik. Ein zusätzlicher Wrapper würde derzeit nur einen zweiten Aufrufpfad hinzufügen, ohne einen bestehenden zu ersetzen.

## Entscheidung

**NO-GO für eine gemeinsame STEP18-CLI oder Fünfer-Orchestrierung.**

Die fünf separaten import-sicheren Entrypoints bleiben die kleinste und präziseste Architektur. Auch für das Core/Cluster-Paar wird aktuell kein Wrapper eingeführt, weil kein konkreter Consumer, kein erforderlicher atomarer Laufvertrag und kein zu ersetzender bestehender Dispatcher belegt ist.

Eine spätere Orchestrierung benötigt vor Implementierung mindestens:

1. einen benannten Consumer
2. eine verbindliche Auswahl der auszuführenden Teilanalysen
3. definierte Fehler-, Teiloutput- und Wiederanlaufsemantik
4. einen Output-/Stdout-Paritätsvertrag
5. ein Charakterisierungsgate für den bisherigen direkten Aufrufpfad

## S8-Gate

`tests/state_research/test_step18_entrypoint_consolidation_review.py` umfasst sechs Prüfungen:

1. Quellidentität und Zeilenzahl aller fünf Entrypoints
2. einheitliche parameterlose `main()`-/Main-Guard-Minimalform
3. weiterhin unterschiedliche feste Inputverträge
4. Seiteneffektklassen und einzige Core/Cluster-Artefaktkante
5. Abwesenheit von Cross-Imports oder gemeinsamem Orchestrator-Owner
6. kombinierter stiller und nichtmutierender Import-Probe

Gate-Test-SHA-256: `c0655f5a0f4a25a16c9160bd2850619cd8dede344764ce21bbc7846443693888`

## Verifikation

Vollständiger Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes S8-Gate: 6/6 PASS
- Gesamte State-Research-Testkohorte: 33/33 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Research-Skripte verändert: 0
- Reale Research-Inputs gelesen oder verändert: 0
- `git diff --check`: PASS

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S9-STEP19-BLOCKED-TRADES-CHARAKTERISIERUNGSGATE** für `analyze_step19_blocked_trades.py`. Es ist mit 35 Zeilen der kleinste der 17 verbleibenden historischen STEP19- bis STEP20E-Import-Zeit-Ausführer. Das Gate bindet zunächst feste Inputs, zeitliche Snapshot-Zuordnung, Filter, beide Gruppierungen, Stdout und Missing-Input-Verhalten mit synthetischen Fixtures. Erst danach darf eine reine Entrypoint-Einkapselung geprüft werden.
