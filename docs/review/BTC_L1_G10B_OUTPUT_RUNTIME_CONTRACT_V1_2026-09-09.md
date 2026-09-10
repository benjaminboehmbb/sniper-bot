# BTC-L1 G10-B Output & Runtime Contract V1

Date (UTC): 2026-09-09
Status: APPROVED_FOR_ADOPTION

## A. Status, Befugnisse und Quellenbindungen
Alle neuen Schnittstellenfestlegungen in diesem Dokument sind als DRAFT_NOT_BINDING eingestuft. Sie sind vom Nutzer formal genehmigte Ausarbeitungen, entfalten jedoch keine formale Annahme, Implementierungsfreigabe oder Kennzahlenfreigabe.
Dieses Dokument und die JSON-Evidenz sind in einem JSON-/Markdown-Bindungsverfahren verknüpft, das die Integrität garantiert.

## B. Unverändert geltende angenommene Regeln
Die Festlegungen aus P01 bis P07 sowie alle bestehenden Berechnungsregeln aus der Evaluator-Klarstellung und dem Parser-/Numeric-Contract bleiben vollständig und unverändert gültig. Sie stehen hier nicht zur Disposition und werden im Folgenden nur über präzise Verweise angewendet, anstatt eine abweichende Kurzfassung zu erfinden.

## C. Gemeinsame Datentypen und Serialisierung
Alle Metrik- und Betragsfelder nutzen folgende Serialisierung:
- **Decimal:** Erfolgt nach Endlichkeitsprüfung über `str(value)` im angenommenen lokalen Kontext. Es findet keine zusätzliche Rundung, kein `normalize()`, keine Quantisierung und kein Float-Umweg statt. Eine dabei entstehende E-Notation ist zulässig.
- **Float64:** Erfolgt nach Endlichkeitsprüfung über `repr(float(value))` unter der gebundenen Runtime. Die genehmigte Decimal-zu-Float64-Konversion für Bootstrap-Inputs bleibt unverändert.
- **Zeitstempel:** Werden exakt als `YYYY-MM-DDTHH:MM:SSZ` formatiert. (P01 bleibt unverändert die Eingabegrammatik). Originaltoken bleiben im Audit erhalten.

## D. Trade- und Veto-Schemas

### Trade-Artefakt
- `schema_version`: String ("1.0.0")
- `run_id`: String (UUID-v4)
- `scenario`: String ("NOMINAL" oder "STRESS")
- `semantic_trade_id`: Integer (szenarioübergreifend stabil)
- `status`: String ("CLOSED")
- `entry_tick`, `exit_tick`: Integer
- `entry_utc_time`, `exit_utc_time`: String (YYYY-MM-DDTHH:MM:SSZ)
- `action`: String ("ENTRY_ACCEPTED")
- `side`: String ("LONG" oder "SHORT")
- `quantity`: Decimal-String
- `entry_reference_price`, `exit_reference_price`: Decimal-String
- `entry_execution_price`, `exit_execution_price`: Decimal-String
- `entry_fee`, `exit_fee`: Decimal-String
- `net_pnl`: Decimal-String
- `realized_equity_before_entry`: Decimal-String

### Veto-Artefakt
- `schema_version`: String ("1.0.0")
- `run_id`: String (UUID-v4)
- `scenario`: String ("NOMINAL" oder "STRESS")
- `semantic_trade_id`: Integer
- `action`: String ("ENTRY_VETOED")
- `veto_reason`: String
- `entry_tick`, `entry_utc_time`: Integer, String
- `exit_tick`, `exit_utc_time`: Integer, String (weist das Veto-Paar bis zum semantischen Exit nach)
- `applicable_state`: Object mit `daily_loss_rate`, `daily_fee_rate`, `realized_drawdown_rate`, `realized_high_water_mark`, `day_start_equity` (alle Decimal-Strings)

## E. Vollständige Controls-, Audit- und Reconciliation-Feldtabellen

### Controls (`controls.jsonl`)
Wird aufgezeichnet bei jedem relevanten `PRE_ENTRY` (auch bei Annahme), `POST_SETTLEMENT` und `DAY_CLOSE` (ohne tägliches Final-FLAT).
- `schema_version`, `run_id`, `scenario`
- `tick`: Integer
- `utc_time`: String
- `phase`: String
- `semantic_trade_id`: Integer (nullable)
- `current_equity`: Decimal-String
- `peak_equity`: Decimal-String
- `day_start_equity`: Decimal-String
- `cumulative_daily_net_pnl`: Decimal-String
- `cumulative_daily_fees`: Decimal-String
- `daily_loss`: Decimal-String (`max(0, -cumulative_daily_net_pnl)`)
- `daily_loss_rate`, `daily_fee_rate`, `realized_drawdown_rate`, `max_drawdown_to_date`: Decimal-Strings
- `daily_loss_limit`: Decimal-String (exakt "0.01")
- `daily_fee_limit`: Decimal-String (exakt "0.0025")
- `drawdown_limit`: Decimal-String (exakt "0.05" in beiden Szenarien)
- `entry_blocked`: Boolean
- `triggered_controls`: Array von Strings (ohne Duplikate in Reihenfolge: `DAILY_LOSS`, `DAILY_FEE`, `DRAWDOWN`). Gleichheit löst vorgeschriebene Sperren aus. Andere Erfordernisse bleiben bestehen.

### Audit (`input_audit.jsonl`)
- `schema_version`, `run_id`
- `classification`: String ("EMPTY_REFERENCE_ON_SEMANTIC_NOOP" oder "STANDARD")
- `tick`: Integer
- `semantic_trade_id`: Integer (nullable)
- `timestamp_original_token`: String
- `reference_original_token`: String
- `utc_time`: String
- `semantic_position_before`, `semantic_position_after`: String
- `action`: String
- `executed`: Integer
- `snapshot_line_number`, `execution_line_number`: Integer
- `snapshot_line_base64`, `execution_line_base64`: String
- `raw_value_cause`: String (nullable, bei P02 zwingend "UNKNOWN")
Leerer Referenzpreis nur beim gültigen semantischen NOOP unter sämtlichen übrigen Integritätsbedingungen. Ausgeführtes OPEN/CLOSE verlangt gültige Referenzen unabhängig vom Veto. Kein Float-Fallback.

### Reconciliation (`reconciliation.json`)
- Erwartete (vorab gebundene) und beobachtete Tick-Grenzen (`expected_first_tick`, `observed_first_tick`, `expected_last_tick`, `observed_last_tick`). Erwartete Werte nicht erfinden.
- `expected_tick_count`, `observed_tick_count` (`expected_tick_count` = 4374557)
- `expected_semantic_events`, `observed_semantic_events` (`expected_semantic_events` = 30621902)
- `expected_semantic_trade_count`, `observed_semantic_trade_count` (`expected_semantic_trade_count` = 563)
- `expected_event_stream_sha256`: String ("ffa200c601dc6c2bdda0492909d6518573af6de0b621deb91ee3c9f46d7022e3")
- `observed_event_stream_sha256`: String (exakt 64 kleine Hex-Zeichen)
- `scenarios` (NOMINAL, STRESS): `economically_closed_trades`, `complete_veto_pairs`, `total_reconciled_trades` (563), `unpaired_open_positions`, `double_classifications`, `missing_semantic_ids`, `unexpected_semantic_ids`, `semantic_final_position`, `economic_final_position`. Fehler müssen darstellbar bleiben (nichtnegative Fehlerzähler, nichtleere Mengen, Finalposition LONG/SHORT ist darstellbarer Fehlerwert).
- Unabhängige Prüfungen (Trade/Audit/Reihenfolge/S2/S4/Loss-Cluster) mit Evidenzreferenzen. Fehlende Evidenz = `NOT_VERIFIED` (niemals PASS). Historische Trade-Normalisierung bleibt PROVENANCE GAP (kein Ersatzalgorithmus).

## F. Result-Schema und vollständige nominale/Stress-Gates
Jedes Metrikobjekt (`net_pnl`, `final_equity`, `gross_profit`, `gross_loss`, `profit_factor`, `win_rate`, `max_drawdown`, `cagr`, `calmar`, `bootstrap_lcb95`) enthält:
`status`, `numeric_type`, `unit`, `value`, `reason`. 
Bei UNDEFINED ist `value=null` und `reason` der konkrete Grund. Kein NaN/Infinity. Undefinierte erforderliche Metriken bestehen ihr Gate nicht. Auch NOT_REQUIRED enthält alle fünf Felder.

**Nominale Gates:**
`net_pnl > 0`, `final_equity > 10000`, `gross_loss > 0`, `profit_factor > 1`, `bootstrap_lcb95 > 0`, `max_drawdown <= 0.05`, `cagr > 0`, `calmar > 0`, kein Kontrollbypass.

**Stress-Gates:**
`net_pnl > 0`, `final_equity > 10000`, `gross_loss > 0`, `profit_factor > 1`, `max_drawdown <= 0.10`, unveränderte operative Kontrollen, kein Kontrollbypass.

Für Stress: `cagr`, `calmar` (beide numeric_type=DECIMAL), `bootstrap_lcb95` (numeric_type=FLOAT64) erhalten `status="NOT_REQUIRED"`, `unit="RATIO"`, `value=null`, `reason="NOT_REQUIRED_BY_STRESS_GATES"`. Keine zusätzlichen Berechnungen dafür.

## G. Runtime-/Dependency-Bindungsverfahren
Runtime-/Dependency-/Evaluator-Identitäten müssen vor Beobachtung neuer Selektionskennzahlen gebunden sein. Das vollständige Manifest muss vor historischer Selektionsauswertung vorliegen. Es werden jetzt keine Versionen oder Pfade erfunden. Beim späteren Start werden die gebundenen Identitäten verifiziert.

## H. Datenrollen, Pfade, Fresh State und Abschlussvertrag
**Rollen:** Kanonischer Datensatz (historische Replay-Eingabe) und semantischer Stream (Evaluator-Eingabe). Getrennt nachweisen.
**Pfadvorschlag:** `/home/workstation/jobs/btc-l1-fast-replay-v4-cert-20260902/evaluator_results/<run_id>/`
- Laufverzeichnis exklusiv neu erstellen. Keine Überschreibung, keine Wiederverwendung alter Zustände.
- Teilartefakte als `.partial`. Nach Abbruch nur neuer Lauf.
**Abschluss (`completion.json`):**
- Wird zuletzt veröffentlicht.
- `run_id`, `status` (`COMPLETED_PASS`, `COMPLETED_FAIL`, `TECHNICAL_ERROR`)
- `metrics_released`: Boolean
- Verweis auf Manifest, getrennte Eingabeidentitäten.
- Artefaktliste (Pfad relativ zum Laufverzeichnis ohne "..", Bytes, SHA256). Kein Selbsthash.
COMPLETED_PASS/FAIL verlangen gültiges result.json, technische Integrität, `metrics_released=true` und keine `.partial`-Dateien. Ein wirtschaftliches FAIL ist technisch gültig.
TECHNICAL_ERROR = `metrics_released=false`. Fehlender Abschlussnachweis = unvollständig. Fehlende Fehlerdatei = kein Erfolgsnachweis. `result.json` erst nach allen Integritäts- und Reconciliation-Prüfungen freigeben. Bei Fehler vor Identitätsprüfung: Erwartete Bindung vs verifizierte Beobachtung trennen. Nicht verfügbare Beobachtungen dürfen null sein mit Fehlergrund; keine erfundenen Prüfungen. Keinen erwarteten Hash als geprüft ausgeben. Manifest- und externe Eingabepfade gesondert behandeln.

## I. Nicht ausgeführte Zusatz-Fixtures; Verweis auf unveränderte N01–N10
N01–N10 bleiben unverändert und NICHT AUSGEFÜHRT.
- **HALF_EVEN:** `prec=50`, `context.add(Decimal("1"), Decimal("5e-50"))` ergibt numerisch exakt 1.
- **Quantity-Floor:** 0.0000105 bei Schritt 0.000001 ergibt 0.000010.
- **Kanonische Equity:** `E0=10000`; `C1=4e-46`, `C2=8e-46`. Kanonisches `E2` rundet auf `10000+1e-45`. Iterative Addition bleibt 10000. Nur kanonischer Pfad darf wirtschaftliche Entscheidungen steuern. Kein produktives Legacy-Modul monkeypatchen.
- **N06:** Produktionsabbruch und diagnostische Signalprüfung unterscheiden.
- **N09:** Acht identische Float64-Werte; Mittelwert bitgleich `x=np.float64('1e-315')`. Keine bereits bewiesene Plattformfähigkeit behaupten: NICHT AUSGEFÜHRT.

## J. Review-Korrekturen K01–K08
Vorrangig eingearbeitet: Limits numerisch exakt in beiden Szenarien, Decimal über `str()` (E-Notation zulässig) und Float64 über `repr(float())`, Ausgabe-Zeitstempel strikt YYYY-MM-DDTHH:MM:SSZ, `daily_loss` als `max(0, -cumulative)`, Erwartung/Beobachtung strikt getrennt, komplettiertes Metrikobjekt (inkl. `NOT_REQUIRED`), Abschlussbedingungen verlangen technische Gültigkeit für Freigabe. Herkunft ist vom Nutzer formal angenommen, ohne juristische Wirkung. Bekannte Referenzhashes von noch ungeprüften Laufdateien unterschieden. Neue Pfade und Schemas nicht als angenommen ausgegeben.

## K. Offene Entscheidungen und verbleibende Qualifikationsauflagen
- Verbleibende Feldgrammatiken.
- Vollständige Fehler-/Veto-Abgrenzungen.
- Konkrete Runtime-/Dependency-/Eingabe-/Evidenzbindungen.
- Helper-Integration und synthetische Qualifikation.
Es wird keine vollständige Implementierungsbereitschaft behauptet. Neue Pfade und Schemas bleiben unangenommene Vorschläge (DRAFT_NOT_BINDING). P01–P07 stehen nicht erneut zur Genehmigung.

## L. Formale Annahmeaufzeichnung

```json
{
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "decision": "FORMALLY_ACCEPT_REVIEWED_OUTPUT_RUNTIME_CONTRACT",
  "date_utc": "2026-09-10",
  "review_recommendation": "APPROVE_FOR_FORMAL_ADOPTION",
  "review_source": "ANTIGRAVITY_WORKSTATION_REVIEW_REPORTED_BY_USER",
  "reviewed_markdown_sha256": "55bb42309a4337438c7fc8627265f0165135c867a3513b5414b88876ddf39719",
  "reviewed_json_sha256": "5cd8335345a7aaa0137dd9c7c670a30102a130caea9417724cb86500d0d11d9a",
  "scope": "Annahme der geprüften technischen Vertragsfestlegungen und Dokumentation dieser Annahme in genau diesen zwei Dateien",
  "technical_contract_and_calculation_rules_changed": false,
  "remaining_gates": "die weiterhin offenen Feldgrammatiken, Fehler-/Veto-Abgrenzungen, konkreten Runtime-/Dependency-/Eingabe-/Evidenzbindungen, Helper-Integration sowie Implementierungs- und Qualifikationsauflagen",
  "repository_publication_state": "NOT_COMMITTED_NOT_PUSHED_AT_ADOPTION_RECORDING",
  "implementation_authorized": false,
  "test_execution_authorized": false,
  "candidate_manifest_authorized": false,
  "commit_authorized": false,
  "push_authorized": false,
  "market_run_authorized": false,
  "selection_authorized": false,
  "review_correction": "Der unabhängige Review enthielt irrtümlich \">= 0.10\" für das finale Stress-Drawdown-Gate. Die geprüften Dateien enthielten bereits korrekt \"max_drawdown <= 0.10\". Die gezielte Leseprüfung bestätigte: 0.099999 PASS, 0.10 PASS, 0.100001 FAIL. Dies ist eine Korrektur der Review-Zusammenfassung, keine Änderung des Vertrags oder seiner Berechnungsregeln."
}
```

## M. Quellenidentitäten mit Commit, Pfad und vollständigem SHA256
- Commit: 0507981de9a819c8617428589df8636fa287fb1e
- `docs/review/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.md`
  SHA256: 628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e
- `docs/review/evidence/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.json`
  SHA256: 21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a
- `docs/review/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.md`
  SHA256: 7962f6d9dbd66b9c6e3ea3a66b46b60ac765821deabd7f00ed8b1536daaa6b53
- `docs/review/evidence/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.json`
  SHA256: 90b99bac40c7f640ba2df69e6f97a750e25b0762f83a8c6fc973184a3189e830
- `docs/review/BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08.md`
  SHA256: c7776c3ceac5939e3936b429e562830af9f0e90667a65405a0ba5f44a44ab5ff
- `docs/review/evidence/BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08.json`
  SHA256: 6d9dbd65a9e16042d95719016e9d0259b0b20eb2ca609674950012769918ef3c
