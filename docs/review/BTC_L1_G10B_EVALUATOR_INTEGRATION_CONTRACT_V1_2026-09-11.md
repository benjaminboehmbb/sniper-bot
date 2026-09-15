# BTC-L1 G10-B Evaluator Integration Contract V1

**DOCUMENT_STATUS=APPROVED_FOR_ADOPTION**

Die formale Annahme ist in Abschnitt 20 aufgezeichnet. Alle Abschnitte vor Abschnitt 20 sind im Wortlaut des geprüften Entwurfsstands belassen; ihre Entwurfs-, Vorschlags- und Offen-Vermerke werden durch Abschnitt 20 zeitlich eingeordnet und nicht umgeschrieben.

Datum der Ausarbeitung (UTC): 2026-09-11

Datum der Annahme (UTC): 2026-09-15

Repository-Stand der Ausarbeitung: `65c91500e5c55c0cf75933e99801007f1fca556a`, Branch `main`, Arbeitsverzeichnis sauber

Gebundener Quellcommit für alle Quellenaussagen: `3c5927127a03de13d8c80a720f5c8b97a2a36789`

Maschinenlesbare Begleitdatei: `docs/review/evidence/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.json`

---

## 1. Status, Umfang und Abgrenzung

### 1.1 Status

Dieser Entwurf ist **DRAFT_NOT_BINDING**. Sämtliche hier enthaltenen Integrations-, Schema-, Pfad-, Diagnose- und Bindungsfestlegungen sind **unverbindliche Vorschläge** und **nicht formal angenommen**. Der Entwurf ist keine Annahme-, Implementierungs-, Qualifikations-, Test-, Manifest-, Selektions-, Staging-, Commit-, Push- oder Ausführungsfreigabe und behauptet **keine** Implementierungsbereitschaft.

Autorisiert ist ausschließlich die Erstellung dieser beiden Entwurfsdateien (`draft_file_creation`). Aus dieser Erstellungsberechtigung folgt keine weitere Freigabe.

**Statuszuordnung nach der Annahme.** Die beiden vorstehenden Absätze beschreiben den geprüften Entwurfsstand und werden durch Abschnitt 20 zeitlich eingeordnet, nicht umgeschrieben. Der aktuelle Status ist **APPROVED_FOR_ADOPTION**: die in diesem Dokument konkret ausformulierten neuen Vertragsfestlegungen einschließlich der Entscheidungen **D4 bis D17** sind formal angenommen; **D1 bis D3** bleiben ungelöste Definitions- und Qualifikationsauflagen; **B1 bis B14** bleiben offene konkrete Bindungen, deren Werte `null` bleiben; **V-19** bleibt zurückgestellt. Aus der Annahme folgt **keine** Implementierungs- oder Auswertungsfreigabe.

### 1.2 Umfang

Der Entwurf konsolidiert die technische Integrationsplanung eines **getrennten** G10-B-Evaluators, der den gebundenen Candidate- und Legacy-Code weder verändert noch monkeypatcht. Er umfasst Modulgrenzen und Datenfluss, das lokale Decimal-Kontextverfahren, die Helper-Zuordnung, Strom-, Parser- und Ledger-Regeln, die wirtschaftlichen Szenarien, Artefakte und Abschlussregeln, die Trennung von Integrität und wirtschaftlichem Gate sowie die Bindungsstufen BIND-0 bis BIND-4.

### 1.3 Abgrenzung zu den angenommenen Verträgen

Unverändert gültig und hier **nicht erneut zur Genehmigung gestellt**:

- die Festlegungen **P01 bis P07** des Parser-/Numeric-Contracts;
- die Festlegungen **K01 bis K08** sowie sämtliche Serialisierungs-, Schema-, Gate-, Pfad-, Fresh-State- und Abschlussregeln des Output-/Runtime-Contracts;
- sämtliche **Berechnungs-, Kosten-, Sizing-, Settlement-, Metrik- und Bootstrap-Regeln** der Evaluator-Klarstellung;
- die **Abschnitte 2 bis 8** des Field-/Helper-Contracts einschließlich Grammatikblock, Feldzuordnung, Prüf- und Diagnosereihenfolge, `reason`-Kreuztabelle, `EntryAuthorization`-Zuordnung und getrennter Behandlung ausserhalb dieser Rückgabe;
- die **Selektions-Gates** der Preregistration.

**V-19 bleibt zurückgestellt.** Es wird keine zweite Berechnungskette des modellierten Stop-Verlusts eingeführt, weder in einem Gate noch in der Reconciliation. Maßgeblich: Field-/Helper-Contract Abschnitt 9.3 und die dortige Formulierung, dass keine zusätzliche Berechnungskette als Vertragsvoraussetzung eingeführt wird.

Historische DRAFT-Formulierungen in den angenommenen Dokumenten setzen deren spätere Annahmeaufzeichnungen **nicht** ausser Kraft.

### 1.4 Referenzierte angenommene Vertragspaare

| Dokument | Markdown SHA256 | JSON SHA256 |
| --- | --- | --- |
| `BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07` | `628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e` | `21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a` |
| `BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08` | `7962f6d9dbd66b9c6e3ea3a66b46b60ac765821deabd7f00ed8b1536daaa6b53` | `90b99bac40c7f640ba2df69e6f97a750e25b0762f83a8c6fc973184a3189e830` |
| `BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08` | `c7776c3ceac5939e3936b429e562830af9f0e90667a65405a0ba5f44a44ab5ff` | `6d9dbd65a9e16042d95719016e9d0259b0b20eb2ca609674950012769918ef3c` |
| `BTC_L1_G10B_OUTPUT_RUNTIME_CONTRACT_V1_2026-09-09` | `e57c1970c30982db3fb8de9dc21e4c24378ff2747c64f7c207ef181c9627e7a9` | `ae518b6a05a30651bd064a9d82c3141db62ddb4c299897d3f9224218bcbe7f26` |
| `BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10` | `6f59d74ee7e2163f47ded5f6427114397ffe11e0db2a8dbc3c8a3dc3b64234cc` | `53a0928e6835480b1422b555313cd4b05f49608e627fde1a4ef33789bfe00828` |

---

## 2. Modulgrenzen und Datenfluss

Vorgeschlagene Ablage als eigenständiges Paket ohne Import von `loop`, `execution`, `market`, `logger`, `state_store`, `paper_artifacts` oder der Shadow- und IU4-Module. Einziger Legacy-Import im Produktionspfad ist `live_l1.core.paper_economics`.

Paket `live_l1/tools/g10b_evaluator/` mit `__init__.py` und `__main__.py`; Aufruf `python -m live_l1.tools.g10b_evaluator --manifest <pfad> --results-root <pfad>`; der Evaluator liest **keine** Umgebungsvariablen. Qualifikationstests liegen unter `tests/live_l1/` nach bestehender Konvention. Keine weiteren Module und keine weiteren Artefakte.

| Modul | Verantwortung |
| --- | --- |
| `run_context` | `run_id` erzeugen, Laufverzeichnis exklusiv anlegen, Manifest lesen und prüfen, Identitäten verifizieren (BIND-3) |
| `stream_reader` | binäres Lesen, Byteregeln, Hash und Zähler über alle Originalbytes |
| `event_parser` | Tokenisierung, Schlüsselprüfung, Auswahl der zwei interpretierten Ereignistypen |
| `field_grammar` | angenommene Feldgrammatiken, P01, P02, F1 bis F3, `symbol` nach Abschnitt 5 |
| `semantic_ledger` | Tickpaarung, lückenlose Nachfolgerfolge, Kreuztabelle, Zustandskontinuität, `semantic_trade_id`, Audit-Datensätze, Zeitfolge |
| `numeric_context` | Vorlagenkontexte und lokales Kontextverfahren nach Abschnitt 3 |
| `scenario_config` | Abbildung des PEE-Profils auf `PaperEconomicsConfig` je Szenario |
| `stop_mapping` | Legacy-Float-Stop-Abbildung an Schritt 6 der angenommenen Reihenfolge, einmal je semantischem OPEN |
| `scenario_account` | je Szenario: kanonisches Konto, Tageszähler, Kontrollen, Veto-Paarung, Positionskontrolle, Trade- und Veto-Zeilen, Controls-Datensätze |
| `helper_gateway` | einziger Aufrufort von `authorize_entry`, Klassifikation nach Field-/Helper-Contract Abschnitt 6 |
| `reconciliation` | interne und externe Prüfungen einschließlich der Neuableitung nach Abschnitt 8 |
| `metrics`, `bootstrap`, `gates` | Kennzahlen, Bootstrap unter P07, Gate-Auswertung |
| `artifacts` | `.partial`-Schreiben, Veröffentlichungsreihenfolge, Abschlussnachweis |
| `errors` | technische Fehlerklasse und `errors.jsonl` |

**Datenfluss:** `run_context` → `stream_reader` → `event_parser` → `field_grammar` → `semantic_ledger` → beide `scenario_account` gleichzeitig in Stromreihenfolge → Hash- und Zählabgleich bei EOF → `reconciliation` → `metrics` → `gates` → `artifacts`. Kennzahlen entstehen erst nach bestandener Reconciliation.

**Importtrennung als zu prüfende Integrationsanforderung.** Ein Paketverzeichnis verhindert technisch keinen Import. Zu erfüllen und zu prüfen sind: die Allowlist nach Abschnitt 10, eine Startprüfung des Import-Abschlusses, eine statische Importprüfung aller Evaluator-Module in der Qualifikation und die Aufzeichnung des Import-Abschlusses im Manifest. Status: zu prüfen, nicht geprüft.

---

## 3. Lokales Decimal-Kontextverfahren

Je Szenario und für den Parser existiert ein **Vorlagenkontext** mit exakt den angenommenen Einstellungen: `prec=50`, `ROUND_HALF_EVEN`, `Emin=-999999`, `Emax=999999`, `capitals=1`, `clamp=0`, Traps `InvalidOperation`, `DivisionByZero`, `Overflow`, `FloatOperation`, `Underflow`, `Subnormal`, `Clamped`; `Inexact` und `Rounded` nicht getrappt; alle neun Signalflaggen initial `False`. Vorlagen werden nie verändert.

Jede Recheneinheit läuft in genau einem Block `with decimal.localcontext(vorlage) as aktiv:`. Dieser Block setzt den Thread-Kontext auf eine **Kopie** der Vorlage und stellt den zuvor aktiven Kontext beim Verlassen wieder her, auch beim Verlassen durch eine Ausnahme. `setcontext` wird nicht verwendet; es gibt keine manuelle Wiederherstellung.

**Recheneinheiten:** je Tick die Dezimalkonstruktion und Wertprüfung des Parsers; je Szenario jede Behandlung eines semantischen OPEN, jedes semantischen CLOSE, des EOF sowie die Kennzahlen- und Gate-Bildung; die Serialisierung über `str(value)`, die der angenommene Output-/Runtime-Contract in Abschnitt C im angenommenen lokalen Kontext verlangt.

**Derselbe aktive Kontext für Kontextmethoden und Helper.** Innerhalb des Blocks verwendet der Evaluator ausschließlich die Methoden des `as`-Ziels `aktiv`, nie die der Vorlage und nie einen anderweitig beschafften Kontext. Die Hilfsfunktionen aus `paper_economics` rechnen mit Operatoren, die den aktuellen Thread-Kontext benutzen; innerhalb des Blocks ist das `aktiv`. Erste Handlung jedes Blocks ist die Prüfung `decimal.getcontext() is aktiv`; ein Fehlschlag ist technischer Abbruch mit `CONTEXT_IDENTITY_MISMATCH`. Innerhalb wirtschaftlichen Codes wird kein weiterer Block geöffnet, weil eine verschachtelte Kopie eigene Flaggen führen würde. `paper_economics` öffnet keinen Kontextblock; das Modul importiert aus `decimal` nur `Decimal`, `InvalidOperation` und `ROUND_FLOOR`.

**Flagübertrag.** Je Szenario und für den Parser wird ein Flagdatensatz mit neun Booleans geführt, initial `False`, nie gelöscht. Beim Betreten des Blocks werden die neun Werte in `aktiv.flags` geschrieben; beim Verlassen werden sie in einer `finally`-Klausel mit Oder in den Datensatz übernommen. Die `finally`-Klausel läuft auch nach einer durch einen Trap ausgelösten Ausnahme. Welche Flaggen eine Implementierung unmittelbar vor dem Auslösen setzt, wird **nicht** behauptet und bleibt Qualifikationsgegenstand.

**Keine pauschale Kontextunabhängigkeit.** Die Dezimalkonstruktion aus `reference_price_text`, die Endlichkeitsprüfung und der Positivitätsvergleich des Parsers laufen im Parserblock unter den angenommenen Einstellungen. Es wird **nicht** behauptet, dass diese Operationen unter allen zulässigen Eingaben signalfrei oder kontextunabhängig sind. Außerhalb jedes Blocks liegen nur Textgrammatiken, Ganzzahlparsen, die Float-Konversion von `price` und `entry_price`, Datei-Ein- und -Ausgabe, Hashing und die NumPy-Sequenz unter P07.

**Ausnahmen.** Ein getrapptes Signal erhebt innerhalb des Blocks eine Ausnahme; die `finally`-Klausel überträgt die Flaggen, der Block stellt den vorherigen Kontext wieder her, und der Evaluator führt die Ausnahme als technischen Abbruch mit Signalnamen und Rechenphase nach Field-/Helper-Contract Abschnitt 7.1.

---

## 4. Helper-Zuordnung

Keine Zeile gilt als qualifiziert. Alle Quellenangaben beziehen sich auf den gebundenen Quellcommit.

| Funktion, Quelle | Entscheidung | Noch erforderlicher Qualifikationsnachweis |
| --- | --- | --- |
| `PaperEconomicsConfig`, `live_l1/core/paper_economics.py` 159–325 | wiederverwenden, je Szenario eine Instanz | Nominal-`config_fingerprint` gleich `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`; Stress-Fingerprint vor Kennzahlen im Manifest |
| `model_fill_price`, 392–420 | wiederverwenden, ausschließlich im Kontextblock | Bitgleichheit mit Kontextmethoden für 5, 8 und 20 bps |
| `calculate_fee_quote`, 423–433 | wiederverwenden, ausschließlich im Kontextblock | Bitgleichheit mit `multiply` auf synthetischen Notionals |
| `floor_quantity_to_step`, 436–443 | wiederverwenden, ausschließlich im Kontextblock | angenommenes Fixture `0.0000105 → 0.000010`; Grenzfixture der Quotientenrundung als Beobachtung |
| `authorize_entry` mit `_build_entry_quote`, 545–619 und 446–542 | `authorize_entry` wiederverwenden, ausschließlich über `helper_gateway`; `_build_entry_quote` nie direkt | Fixtures je Zeile der Zuordnung 6.4 einschließlich Auffangregel |
| `settle_trade`, 622–715 | **nicht** im Produktionspfad; Netto-PnL evaluator-eigen aus `model_fill_price`, `calculate_fee_quote` und Kontextmethoden in vorgeschriebener Reihenfolge | Orakel für `net_pnl_quote` auf synthetischen Trades beider Seiten |
| `TradeRecordV2`, `apply_trade_to_account`, `PaperAccountState`, `evaluate_account_entry_guard`, `canonical_decimal`, `_utc_timestamp_seconds` in `live_l1/state/paper_artifacts.py` | **nicht** im Produktionspfad | Orakel nur auf Folgen, in denen iterative und kanonische Equity gleich sind |
| `observe_shadow_entry_candidate`, `load_shadow_settings` in `live_l1/core/paper_economics_shadow.py` | **nicht** wiederverwenden | entfällt |
| `live_l1/core/execution.py`, `logger._kv_escape`, `market._canonical_positive_decimal_text`, `state_store` | **nicht** importieren; die zwei Legacy-Float-Operationen der Stop-Abbildung werden wörtlich reproduziert; Legacy-`pnl`/`pnl_net` nur als Konsistenzevidenz | Float- und Plattformverhalten vor Beobachtung einfrieren; Escaping-Funktion nur als Fixture-Generator, nie als Decoder |

**Begründungen der Nichtverwendung, sachlich getrennt.** `settle_trade` bildet `equity_after = equity_before + net_pnl` (Zeile 685) und leitet Peak, Drawdown und Rate iterativ ab. `TradeRecordV2.from_economics` kopiert diese Werte unverändert; `TradeRecordV2.__post_init__` erzwingt in Zeile 1064 die Identität `equity_after_quote == equity_before_quote + net_pnl_quote`. `apply_trade_to_account` rechnet demgegenüber selbst **kanonisch**: `cumulative_pnl` (Zeile 1460), `realized_equity = starting_equity + cumulative_pnl` (Zeile 1461), Peak, Drawdown und Rate daraus (Zeilen 1462–1464); es verlangt vom Record lediglich dazu passende Werte. Die Aussage, `apply_trade_to_account` verlange selbst zwingend iterative Equity, wäre unzutreffend. Tragender Grund der Nichtverwendung ist die iterative Identität im **Record-Schema**: weichen iterativer und kanonischer Wert bei `prec=50` ab, erfüllt kein Record beide Prüfungen. Hinzu kommen der Modulkontext ohne P05/P06-Traps, fremde Schemafelder und ein Zeitstempelparser, der fremde Offsets annimmt statt sie abzulehnen.

**Profilabbildung, evaluator-eigen und nachvollziehbar.** `PEE_SCHEMA_VERSION → schema_version` als `int`, `PEE_ECONOMICS_MODEL_VERSION → economics_model_version`, `PEE_ECONOMICS_PROFILE_ID → economics_profile_id`, `PEE_QUOTE_CURRENCY → quote_currency`, `PEE_STARTING_EQUITY_QUOTE → starting_equity_quote`, `PEE_RISK_PER_TRADE_RATE → risk_per_trade_rate`, `PEE_MAX_POSITION_NOTIONAL_RATE → max_position_notional_rate`, `PEE_ENTRY_FEE_RATE → entry_fee_rate`, `PEE_EXIT_FEE_RATE → exit_fee_rate`, `PEE_ENTRY_SLIPPAGE_BPS → entry_slippage_bps`, `PEE_EXIT_SLIPPAGE_BPS → exit_slippage_bps`, `PEE_QUANTITY_STEP → quantity_step`, `PEE_MIN_QUANTITY → min_quantity`, `PEE_MIN_NOTIONAL_QUOTE → min_notional_quote`, `PEE_MAX_DAILY_LOSS_RATE → max_daily_loss_rate`, `PEE_MAX_DAILY_FEE_RATE → max_daily_fee_rate`, `PEE_MAX_REALIZED_DRAWDOWN_RATE → max_realized_drawdown_rate`. Nicht abgebildet: `PEE_MODE` und `PEE_REFERENCE_STOP_RATE`; Letzterer ist protokollseitig ausgeschlossen. Stress nutzt dieselbe Abbildung mit den vier angenommenen Kostenüberschreibungen. Der Fingerprint ist ein **zusätzlicher** Identitätscheck und ersetzt den Nachweis der vollständigen Feldabbildung nicht.

---

## 5. Strom, Parser und semantischer Ledger

### 5.1 Byteregeln des semantischen Stroms

Binäres Lesen ohne Textmodus und ohne Newline-Übersetzung. Der SHA256 läuft über **alle Dateibytes in Dateireihenfolge**, jedes Byte genau einmal, unabhängig von jeder Validierung; kein Byte wird entfernt, ersetzt oder normalisiert. Der Vergleich mit dem erwarteten Stream-Hash erfolgt bei EOF. Bricht der Lauf vor EOF ab, wird kein Teilhash als beobachteter Hash ausgegeben; das Feld bleibt `null` mit Fehlergrund.

Ein Ereignis ist die Bytefolge bis einschließlich `0x0A`; der Ereigniszähler ist die Anzahl der so terminierten Zeilen. Das letzte Byte der Datei muss `0x0A` sein, sonst technischer Abbruch wegen Trunkierung. Eine leere Zeile ist ein technischer Abbruch. Das Byte `0x0D` ist an jeder Position unzulässig und führt mit Zeilennummer und Byteoffset zum technischen Abbruch; belegt durch den Erzeuger, der jedes Wagenrücklaufzeichen als Literalfolge escapet und den Digest über die kanonische Zeile vor dem Dateischreiben bildet. Ebenfalls unzulässig sind `0x00` an jeder Position und eine Byte-Order-Mark am Dateianfang. Jede Zeile muss strikt als UTF-8 decodierbar sein.

Eine zeilenweite ASCII-Beschränkung wird für keinen der beiden interpretierten Ereignistypen behauptet; angenommen sind ausschließlich die **feldbezogenen** Grammatiken, und `symbol` ist dort offen.

### 5.2 `symbol`

Vorgeschlagen: `SYMBOL := "BTCUSDT"` als geschlossene Einermenge mit Ganzstringprüfung; jede Abweichung ist ein technischer Abbruch. Belege: der gebundene Runner setzt `L1_SYMBOL=BTCUSDT`, der Loop übernimmt den Wert aus der Laufkonfiguration, der Feed reicht ihn unverändert durch, und der final persistierte S2-Zustand der V4-Zertifizierung trägt `BTCUSDT`.

### 5.3 Zeitfolge einschließlich NOOP

Der Vergleich erfolgt auf den nach P01 decodierten ganzen Sekunden, nicht auf Tokens. Für jeden Tick `k > 1` gilt `t_k >= t_(k-1)` über alle Ticks einschließlich NOOP. Gleiche Zeitstempel sind zulässig; ein Tick ist über `tick` identifiziert. Ein rückläufiger Zeitstempel ist ein technischer Abbruch mit Tick und Zeilennummer. Die angenommene Kontoregel gegen Zeitregression bleibt unverändert bestehen. Bei NOOP mit offener Position muss `entry_timestamp_utc` dem gespeicherten OPEN-Token gleichen.

### 5.4 Audit-Datensätze

Zwingend nach P02: jeder Tick mit leerem `reference_price_text` auf gültigem semantischem NOOP mit `classification = EMPTY_REFERENCE_ON_SEMANTIC_NOOP` und `raw_value_cause = "UNKNOWN"`, `semantic_trade_id = null`. Zusätzlich vorgeschlagen: je ein Datensatz mit `classification = STANDARD` für jeden Tick mit ausgeführtem OPEN und für jeden Tick mit ausgeführtem CLOSE, mit gesetzter `semantic_trade_id` und `raw_value_cause = null`. Für sonstige NOOP-Ticks entsteht kein Datensatz. Alle Datensätze tragen beide Originalzeilen als Base64 und beide Originaltokens. Erwartete Anzahl: `1126` zuzüglich der Anzahl der P02-Ticks; sie wird in der Reconciliation als Evidenzreferenz geführt.

Die Zulassung eines positiv-null `price` ist nach der angenommenen Regel ohnehin nur auf genau diesen P02-Ticks möglich und begründet keinen eigenen Auslöser.

### 5.5 Stop-Audit, vorgeschlagene Schemaergänzung

Die Stop-Abbildung ist Teil des angenommenen Schritts 6 und wird nie vor Schritt 5 ausgeführt. Sie wird von dem Szenario berechnet, das Schritt 6 zuerst erreicht, einmal je semantischem OPEN gebildet, geprüft und vom zweiten Szenario unverändert wiederverwendet, weil sie szenariounabhängig ist. Erreicht kein Szenario Schritt 6, wird sie nicht berechnet.

Feste Prüfreihenfolge: (1) `legacy_entry = float(reference_price_text)` endlich; (2) Gleichheit mit dem Float des `entry_price`-Tokens ohne Toleranz; (3) `legacy_stop` aus `legacy_entry*(1.0-0.015)` bei LONG beziehungsweise `legacy_entry*(1.0+0.015)` bei SHORT endlich; (4) `Decimal.from_float(legacy_stop)` größer als der Decimal-Wert 0; (5) Richtung: unter dem exakten Dezimal-Entry bei LONG, darüber bei SHORT. Nach der verletzten Prüfung bleibt jeder spätere Wert unberechnet.

**Vorgeschlagene Ergänzung von `input_audit.jsonl`**, belegt nur in `STANDARD`-Datensätzen ausgeführter OPEN-Ticks, sonst `null`:

| Feld | Typ | Belegung |
| --- | --- | --- |
| `stop_mapping_state` | String | `COMPUTED` oder `NOT_COMPUTED_CONTROL_VETO_BOTH` |
| `legacy_entry_float` | String, `repr(float)` | nur bei `COMPUTED` |
| `legacy_sl_float` | String, `repr(float)` | nur bei `COMPUTED` |
| `legacy_stop_float` | String, `repr(float)` | nur bei `COMPUTED` |
| `stop_decimal` | Decimal-String, `str(Decimal.from_float(...))` | nur bei `COMPUTED` |
| `stop_side` | String `LONG` oder `SHORT` | bei jedem OPEN-Datensatz |

Vier unterscheidbare Fälle je semantischem OPEN: beide Szenarien mit Kontrollveto — `NOT_COMPUTED_CONTROL_VETO_BOTH`, Wertfelder `null`, zwei Veto-Zeilen mit `CONTROL_`-Grund; genau ein Szenario ohne Kontrollveto — `COMPUTED`, Wertfelder belegt; beide Szenarien ohne Kontrollveto — `COMPUTED`, beide Szenarien verwenden dieselben Werte; fehlerhafte Abbildung — kein finaler Audit-Datensatz, technischer Abbruch mit Diagnosedaten ausschließlich in der Fehlerdatei.

Bleibt die Abbildung in beiden Szenarien unberechnet, wird eine latente Abweichung nicht entdeckt; das ist beabsichtigt, weil der Wert dann nie in die Ökonomie eingeht, und bleibt über den Zustandswert sichtbar. Welche Szenarien die Abbildung verwendet haben, folgt ohne Zusatzfeld aus den Trade- und Veto-Zeilen. Die Auditfelder dienen der von der Klarstellung verlangten Aufbewahrung und werden von keinem Gate und keiner Reconciliation nachgerechnet.

---

## 6. Wirtschaftliche Szenarien

### 6.1 Zustand je Szenario

`C` kumulierter Netto-PnL ab dem Decimal-Wert 0; `E = add(E0, C)` mit `E0 = 10000`; `H` Höchststand ab 10000; `D_max` ab 0; `utc_day` anfangs **ungesetzt**; `daily_net`; `daily_fees`; `econ_position` als `None` oder `{semantic_trade_id, side, quote, E_before, entry_tick, entry_utc}`; `veto_open` als `None` oder `{semantic_trade_id, side, entry_tick, entry_utc, veto_reason, applicable_state}`; `closed_count`; `veto_pairs`; `gross_profit`; Negativsumme; Rückgabenliste. Alle Kontoentscheidungen, Sizing-Basen, Berichte und Gates lesen ausschließlich diese kanonische Serie.

### 6.2 Kontotag: Initialisierung, Gleichheit, Fortschritt, Rückschritt

Solange `utc_day` ungesetzt ist, wird **kein** Tagesvergleich ausgeführt. Beim **ersten** `PRE_ENTRY` eines Szenarios wird `utc_day = day(t)` gesetzt; `daily_net` und `daily_fees` starten bei null; die Tagesstart-Equity ist `subtract(E, 0) = E`. Es gibt keinen vorherigen Kontotag und deshalb **keinen** `DAY_CLOSE`.

Erst bei gesetztem `utc_day` werden für jedes Kontoereignis — also jede `PRE_ENTRY`-Bewertung eines semantischen OPEN und jedes Settlement eines wirtschaftlich akzeptierten CLOSE — die drei Fälle geprüft: `day(t) = utc_day` Gleichheit, Zähler akkumulieren; `day(t) > utc_day` Fortschritt, `DAY_CLOSE` für den bisherigen `utc_day` schreiben, Zähler auf null, `utc_day = day(t)`; `day(t) < utc_day` Rückschritt, technischer Abbruch wegen Tagesregression.

Ein wirtschaftlich akzeptierter CLOSE setzt eine zuvor eröffnete Position und damit einen initialisierten Kontotag voraus, weil jede Eröffnung eine `PRE_ENTRY`-Bewertung durchlaufen hat. Trifft ein CLOSE ohne passende offene Position oder bei ungesetztem `utc_day` ein, greift die bestehende Behandlung als Ledger-Inkonsistenz.

### 6.3 Semantisches OPEN, je Szenario

In der angenommenen Reihenfolge: (1) Strom- und Paarungsprüfung einschließlich Zustands-, Seiten- und Metadatenprüfung und Kreuztabelle; (2) Referenzpreisprüfung des OPEN-Snapshots mit Umwandlung in einen Dezimalwert; (3) Feld- und Metadatenprüfungen. Ledgerkontrolle: `econ_position` und `veto_open` müssen `None` sein, sonst technischer Abbruch wegen Ledger-Inkonsistenz. (4) Fortschreibung des Buchhaltungszustands und Prüfung der Kontobasen `E > 0`, `H > 0`, `day_start = subtract(E, daily_net) > 0`. Raten: `daily_loss = max(0, -daily_net)`, `daily_loss_rate = divide(daily_loss, day_start)`, `daily_fee_rate = divide(daily_fees, day_start)`, `dd_rate = divide(subtract(H, E), H)`. `PRE_ENTRY`-Datensatz mit allen angenommenen Feldern und `triggered_controls` in der Reihenfolge `DAILY_LOSS`, `DAILY_FEE`, `DRAWDOWN`. (5) Kontrollprüfung: bei erfülltem Limit `ENTRY_VETOED` mit gesetztem `veto_open`; die Schritte 6 und 7 entfallen. (6) Nur ohne Kontrollveto: Stop-Abbildung und Sizing-Eingaben, `authorize_entry` im Kontextblock. (7) Klassifikation nach der angenommenen Zuordnung, zusätzlich die evaluator-eigene Hebelkontrolle `entry_notional_quote <= E`. Erfolg setzt `econ_position` mit `E_before = E`; ein Helper-Veto setzt `veto_open`; Grenzcodes, Quote-Erstellungsfehler und Auffangregel sind technische Abbrüche.

### 6.4 `veto_reason` und Priorität

Geschlossene Menge: `CONTROL_DAILY_LOSS`, `CONTROL_DAILY_FEE`, `CONTROL_DRAWDOWN`, `PEE_QUANTITY_ZERO`, `PEE_QUANTITY_BELOW_MIN`, `PEE_NOTIONAL_BELOW_MIN`. Ein Kontrollveto geht dem Helper-Veto vor, weil der Helper bei Kontrollveto nach der angenommenen Reihenfolge nicht aufgerufen wird. Bei mehreren ausgelösten Kontrollen ist `veto_reason` das erste Element von `triggered_controls` in der angenommenen Reihenfolge, mit Präfix `CONTROL_`. **Alle** tatsächlich ausgelösten Kontrollen bleiben vollständig im `PRE_ENTRY`-Datensatz desselben Ticks und Szenarios erhalten.

### 6.5 Semantisches CLOSE einer akzeptierten Position

Paarung und Seite gegen `econ_position`, sonst technischer Abbruch. Tageswechsel nach Abschnitt 6.2; der Settlement-Tag ist `day(t)` des CLOSE. Es folgen `exit_fill`, `exit_fee`, Brutto- und Netto-PnL nach den angenommenen Formeln, dann `C = add(C, net)`, `E = add(E0, C)`, `H = max(H, E)`, `D = divide(subtract(H, E), H)`, `D_max = max(D_max, D)`; Fortschreibung von `gross_profit` oder Negativsumme; `return = divide(net, E_before)`; `daily_net += net` und `daily_fees += entry_fee + exit_fee` vollständig am Settlement-Tag; Trade-Zeile, `POST_SETTLEMENT`-Datensatz, `closed_count += 1`, `econ_position = None`.

### 6.6 Semantisches CLOSE eines Veto-Paares

Paarung und Seite gegen `veto_open`. Keine Settlement-Buchung, keine Gebühr, kein Netto-PnL, keine Änderung von `C`, `E`, `H`, `D`, `daily_net` oder `daily_fees`; **keine** Änderung von `utc_day`, auch wenn der CLOSE-Tag später liegt; **kein** Controls-Datensatz, weder `POST_SETTLEMENT` noch `DAY_CLOSE`; keine Kontoregel gegen Zeitregression, weil kein Kontoereignis vorliegt. Die Veto-Zeile wird mit `exit_tick` und `exit_utc_time` vervollständigt; `veto_reason` und `applicable_state` bleiben die des OPEN. `veto_pairs += 1`, `veto_open = None`.

### 6.7 `DAY_CLOSE`

Je Szenario ein Datensatz für jeden UTC-Tag, der Kontotag dieses Szenarios war: beim Wechsel von `utc_day` unmittelbar vor dem ersten Datensatz des neuen Tages, und bei EOF für den zuletzt gesetzten Kontotag. `tick` und `utc_time` sind die des letzten wirtschaftlichen Ereignisses des abgeschlossenen Tages, `semantic_trade_id` ist `null`, die Zähler und Raten tragen die Schlusswerte, `entry_blocked` und `triggered_controls` bewerten diesen Schlusszustand. NOOP-Ticks und Veto-CLOSE ändern `utc_day` nicht; Tage ohne wirtschaftliches Ereignis werden nie Kontotag und erhalten keinen Datensatz.

Dies beruht auf der vorgeschlagenen Lesart von „relevant“ im angenommenen Output-/Runtime-Contract, Abschnitt E, als „Tag mit aktivem Kontotag“. Der angenommene Wortlaut legt Phasennamen und Aufzeichnungspflicht fest, nicht jedoch den Auslöser, die Bedeutung von „relevant“, die Belegung von `tick` und `utc_time` oder die Behandlung ereignisloser Tage; eine Aufzeichnung an jeder im Strom beobachteten UTC-Tagesgrenze wäre mit demselben Wortlaut vereinbar und wird hier **nicht** vorgeschlagen. Die Formulierung „ohne tägliches Final-FLAT“ belegt nicht, dass ereignislose Tage keine Kontrollaufzeichnung erhalten; sie besagt nur, dass am Tagesende keine FLAT-Position verlangt wird.

### 6.8 EOF

Je Szenario: `econ_position` und `veto_open` sind `None`; `closed_count + veto_pairs = 563`; jede `semantic_trade_id` ist genau einmal klassifiziert; der letzte `DAY_CLOSE` ist geschrieben. Semantisch: finale Position FLAT, Tickzahl, Ereigniszahl und Stream-Hash gleich den Erwartungen.

### 6.9 Definiertheit der Metriken

`net_pnl`, `final_equity`, `gross_profit`, `gross_loss` und `max_drawdown` sind stets definiert; `profit_factor` bei `gross_loss > 0`; `win_rate` bei `n > 0`; `cagr` bei positiver Final Equity; `calmar` bei definiertem `cagr` und `max_drawdown > 0`; `bootstrap_lcb95` bei `n > 0`, wobei Konversionsfehler technisch und nicht undefiniert sind. Ein Gate auf einer undefinierten Metrik ist FAIL. Ein LCB95 von null, auch negativ null, oder ein negativer Wert ist ein **definierter** Wert; sein nominales Gate ist nicht bestanden, die Metrik ist nicht undefiniert.

`gross_loss = 0` impliziert eine nichtfallende Folge `C_i`, unter monotoner Rundung eine nichtfallende Folge `E_i` und damit `max_drawdown = 0`. Die **Umkehrung gilt nicht**: ein Trade mit negativem Netto-PnL erzwingt kein `D_i > 0`, weil `E_i` gerundet wird. Statisches Gegenbeispiel bei `prec=50`, `ROUND_HALF_EVEN`, `E0 = 10000` und einem geschlossenen wirtschaftlichen Trade mit hinreichend kleinem negativem Netto-PnL: die exakte Summe besitzt 51 signifikante Stellen — vier Vorkommastellen und 47 Nachkommastellen —, wird auf 10000 gerundet, und es ergeben sich `gross_loss > 0`, `max_drawdown = 0`, `profit_factor = 0` als definierter Wert und ein wegen des Drawdowns null undefinierter `calmar`. Bei einem negativen Netto-PnL von `-4e-46` ist die exakte Summe dagegen mit 50 Stellen noch exakt darstellbar; die Rundung tritt erst eine Größenordnung darunter ein. Die Asymmetrie zum Fixture des angenommenen Output-/Runtime-Contracts mit `+4e-46` entsteht, weil Werte unter 10000 vier und Werte ab 10000 fünf Vorkommastellen haben.

Jede Metrik erhält ihre eigenen Definitionsbedingungen; eine Formulierung „alle übrigen definiert“ wird nicht verwendet, weil sie gleichzeitig mögliche Undefiniertheiten übergehen würde. Alle Fälle undefinierter oder gate-verletzender Metriken sind wirtschaftliche Ergebnisse mit gültigem Ergebnisartefakt und freigegebenen Kennzahlen, kein technischer Abbruch. Stress-Objekte mit angenommenem Status `NOT_REQUIRED` bleiben unverändert.

---

## 7. Artefakte, Schemata und Abschluss

### 7.1 Pfade und Dateien

Laufverzeichnis nach angenommener Pfadstruktur: `/home/workstation/jobs/btc-l1-fast-replay-v4-cert-20260902/evaluator_results/<run_id>/`. Angenommene Dateinamen: `controls.jsonl`, `input_audit.jsonl`, `reconciliation.json`, `result.json`, `completion.json`.

**Vorgeschlagen:** `trades.jsonl` mit genau dem angenommenen Schema „Trade-Artefakt“ und `vetoes.jsonl` mit genau dem angenommenen Schema „Veto-Artefakt“; beide Szenarien in derselben Datei, unterschieden durch das angenommene Feld `scenario`; Reihenfolge aufsteigend nach `exit_tick`, bei gleichem `exit_tick` `NOMINAL` vor `STRESS`; die Zeile entsteht beim semantischen CLOSE, nie früher; das Paar `(scenario, semantic_trade_id)` ist je Datei eindeutig und erscheint nie in beiden Dateien; keine Felder über die angenommenen hinaus. Ebenfalls vorgeschlagen: `errors.jsonl`.

Alle JSONL-Zeilen: genau ein Objekt, Schlüssel sortiert, `ensure_ascii`, Trennzeichen Komma und Doppelpunkt ohne Leerzeichen, Zeilenende LF.

Der angenommene Vertrag legt für Trade- und Veto-Artefakte die **Schemata** fest, nicht jedoch Dateiname, Aufteilung oder Zeilenformat; er legt für den Fehlerfall die **Existenz** einer Fehlerdatei fest, nicht deren Namen oder Schema. Die hier genannten Namen sind Vorschläge.

### 7.2 Veröffentlichung, Fehlerbehandlung und Freigaberegel

**Regulärer Weg.** `run_id` wird als UUID-v4 erzeugt, **bevor** eine Dateisystemaktion stattfindet; danach wird `<results_root>/<run_id>/` exklusiv angelegt. Existiert das Verzeichnis oder kann es nicht exklusiv angelegt werden, wird nichts geschrieben, `run_id` und Ursache gehen auf die Standardfehlerausgabe, Rückgabewert `3`, kein Neuversuch mit anderer `run_id`. Alle Artefakte entstehen als `<name>.partial`. Fachliche Ergebnisartefakte werden in fester Reihenfolge umbenannt: `trades.jsonl`, `vetoes.jsonl`, `controls.jsonl`, `input_audit.jsonl`, `reconciliation.json`, `result.json`. Danach wird die Hashliste gebildet, `completion.json.partial` geschrieben und einmal in `completion.json` umbenannt.

**Trennung nach einem Fehler.** Nach einem technischen Fehler werden **keine weiteren fachlichen Ergebnisartefakte** veröffentlicht; bereits final benannte bleiben unverändert, noch nicht umbenannte bleiben `.partial`. Die begrenzte Fehlerbehandlung darf genau zweierlei: die Fehlerdatei `errors.jsonl.partial` abschließen und ihre **einmalige** Umbenennung in `errors.jsonl` versuchen; danach einen technischen Abschluss über `completion.json.partial` und dessen einmalige Umbenennung in `completion.json` versuchen. Keine bereits fehlgeschlagene Umbenennung wird wiederholt. Nach dem endgültigen Schließen der Fehlerdatei werden keine weiteren Fehleraufzeichnungen erzwungen; spätere Fehler werden auf der Standardfehlerausgabe gemeldet. Die Fehlerdatei wird nur geschlossen oder umbenannt, wenn sie aufgrund eines Fehlers **tatsächlich angelegt** wurde; kann sie beim ersten Fehler nicht angelegt werden, wird kein Abschluss versucht, der Fehler geht auf die Standardfehlerausgabe, Rückgabewert `3`.

**Gescheiterte Umbenennung der Fehlerdatei.** Scheitert die Umbenennung der bereits geschlossenen `errors.jsonl.partial`, bleibt sie unverändert erhalten und wird im technischen Abschluss unter diesem tatsächlichen Namen mit Bytes und Hash aufgeführt; der Umbenennungsfehler wird zusätzlich auf der Standardfehlerausgabe gemeldet; keine erneute Öffnung allein zur Dokumentation dieses Folgefehlers. Dies erlaubt ausschließlich einen technischen Abschluss mit `metrics_released=false`.

**Reservierte Abschlussnamen.** Ein Abschlussnachweis heißt ausschließlich `completion.json` und entsteht ausschließlich über `completion.json.partial`. Ist einer dieser beiden Namen unerwartet bereits belegt, wird nichts überschrieben und nichts entfernt, **kein alternativer Abschlussname** verwendet, die Kollision auf der Standardfehlerausgabe gemeldet und der Lauf ohne gültigen neuen Abschluss beendet, Rückgabewert `3`. Ist `completion.json.partial` nicht schreibbar oder die letzte Umbenennung nicht möglich, gilt dasselbe; der Lauf bleibt unvollständig.

**Bereits veröffentlichte Dateien.** Bei jedem Folgefehler bleiben bereits final benannte Dateien unverändert. Kein automatisches Löschen, Zurückbenennen oder Überschreiben. Bereits erfolgte Umbenennungen werden im Abschluss nicht als unerfolgt dargestellt, und nichts wird als final dargestellt, was `.partial` ist.

**Hashliste.** Die Hashliste enthält alle zum Zeitpunkt ihrer Bildung im Laufverzeichnis vorhandenen Dateien unter ihrem tatsächlichen Namen, final oder `.partial`, mit Bytes und SHA256. Beim **Bilden** der Liste bleiben beide Abschlussnamen — `completion.json` und `completion.json.partial` — ausgeschlossen, um jede direkte oder indirekte Selbsthash-Bindung zu vermeiden. Die Liste wird nach dem Anlegen der Abschlussdatei nicht mehr verändert.

**Prüfung eines erfolgreichen fertigen Laufs.** Für `COMPLETED_PASS` und `COMPLETED_FAIL` muss `completion.json.partial` nach der erfolgreichen Umbenennung **fehlen**. Beim Prüfen wird vom tatsächlichen Verzeichnisinhalt **nur** `completion.json` ausgenommen; eine zusätzlich liegengebliebene `completion.json.partial` zählt damit zum Verzeichnisinhalt, steht nicht in der Hashliste und macht den Lauf ungültig. Kennzahlen gelten nur dann als freigegeben, wenn `completion.json` existiert, parsebar ist, `status` den Wert `COMPLETED_PASS` oder `COMPLETED_FAIL` trägt, `metrics_released=true` ist, kein gelisteter Pfad auf `.partial` endet, `result.json` mit übereinstimmenden Bytes und SHA256 gelistet ist und die gelistete Menge genau dem Verzeichnisinhalt ohne `completion.json` entspricht. Eine final benannte `result.json` ohne diesen Abschlussnachweis ist keine Freigabe; ebenso wenig ein Abschluss mit `TECHNICAL_ERROR`, der eine final benannte `result.json` listet.

**Rückgabewerte des Evaluators, vorgeschlagen.** `0` für `COMPLETED_PASS` und `COMPLETED_FAIL`; `2` für `TECHNICAL_ERROR` mit geschriebenem Abschlussnachweis; `3` für einen unvollständigen Lauf ohne Abschlussnachweis. Dieser Rückgabewert ist nicht das Runtime-Gate der Preregistration, das den Replay-Runner betrifft.

### 7.3 `errors.jsonl`, vorgeschlagenes Schema

Genau eine Zeile trägt `error_role = PRIMARY` mit `sequence = 1`; sie ist die erste technische Ausnahme, die den Abbruch ausgelöst hat. Jede weitere Zeile ist `SECONDARY` und entsteht ausschließlich während der Abbruchbehandlung. Nach dem Primärfehler wird keine weitere Verarbeitung des Stroms oder der Konten versucht.

**Phasenmenge:** `IDENTITY`, `STREAM_READ`, `EVENT_PARSE`, `FIELD_GRAMMAR`, `PAIRING`, `SEMANTIC_LEDGER`, `ACCOUNT_DAY`, `CONTROLS`, `STOP_MAPPING`, `HELPER_AUTHORIZE`, `SETTLEMENT`, `RECONCILIATION`, `METRICS`, `BOOTSTRAP`, `GATES`, `ARTIFACT_WRITE`.

**Codemenge, erhalten aus den angenommenen Quellen und Verträgen:** `PEE_CONFIG_INVALID`, `PEE_INPUT_INVALID`, `PEE_INPUT_FLOAT_NOT_ALLOWED`, `PEE_SIDE_INVALID`, `PEE_PHASE_INVALID`, `PEE_STOP_DIRECTION_INVALID`, `PEE_RISK_LIMIT_EXCEEDED`, `PEE_NOTIONAL_LIMIT_EXCEEDED`, `PEE_CONFIG_FINGERPRINT_MISMATCH`, `HELPER_RESULT_UNCLASSIFIED`, `ECONOMIC_LEDGER_INCONSISTENCY`, `UNSUPPORTED_TIMESTAMP_PRECISION`. **Vorgeschlagen ergänzt:** `IDENTITY_MISMATCH`, `MANIFEST_INCOMPLETE`, `STREAM_BYTE_INADMISSIBLE`, `STREAM_TRUNCATED`, `STREAM_EMPTY_LINE`, `STREAM_DECODE_ERROR`, `STREAM_TIME_REGRESSION`, `EVENT_STRUCTURE_INVALID`, `LITERAL_NULL_TOKEN`, `FIELD_GRAMMAR_VIOLATION`, `FIELD_VALUE_INVALID`, `TICK_SEQUENCE_INVALID`, `PAIRING_INVALID`, `STATE_CONTINUITY_INVALID`, `REASON_CROSSTABLE_INVALID`, `ACCOUNT_BASE_INVALID`, `ACCOUNT_DAY_REGRESSION`, `STOP_MAPPING_INVALID`, `DECIMAL_SIGNAL_TRAPPED`, `NUMPY_FLOATING_POINT_ERROR`, `FLOAT64_CONVERSION_INVALID`, `CONTEXT_IDENTITY_MISMATCH`, `RECONCILIATION_MISMATCH`, `RECONCILIATION_NOT_VERIFIED`, `METRIC_NONFINITE`, `ARTIFACT_WRITE_FAILED`.

| Feld | Typ und erlaubte Werte | Nullable | Bedingung |
| --- | --- | --- | --- |
| `schema_version` | String, exakt `"1.0.0"` | nein | |
| `run_id` | String, UUID-v4 in kanonischer Kleinschreibung, 36 Zeichen | nein | gleich der `run_id` des Laufs |
| `sequence` | Integer ab 1 | nein | je Zeile um 1 steigend in Dateireihenfolge |
| `error_role` | String `PRIMARY` oder `SECONDARY` | nein | genau eine Zeile `PRIMARY`, diese hat `sequence = 1` |
| `caused_by_sequence` | Integer | ja | `null` genau bei `PRIMARY`; bei `SECONDARY` gleich `1` |
| `recorded_utc` | String im Format `YYYY-MM-DDTHH:MM:SSZ` | nein | Wanduhrzeit, nicht semantisch |
| `code` | String aus der Codemenge | nein | |
| `phase` | String aus der Phasenmenge | nein | |
| `location` | String `modul.funktion`, nicht leer | nein | |
| `scenario` | String `NOMINAL` oder `STRESS` | ja | nicht `null` in den Phasen `ACCOUNT_DAY`, `CONTROLS`, `STOP_MAPPING`, `HELPER_AUTHORIZE`, `SETTLEMENT`, `METRICS`, `BOOTSTRAP`, `GATES`; sonst `null` |
| `tick` | Integer ab 1 | ja | nicht `null`, wenn der Fehler einem Tick zugeordnet ist; `null` in `IDENTITY`, `RECONCILIATION`, `METRICS`, `BOOTSTRAP`, `GATES`, `ARTIFACT_WRITE` |
| `line_number` | Integer ab 1 | ja | nicht `null` bei Bezug auf eine Streamzeile in `STREAM_READ`, `EVENT_PARSE`, `FIELD_GRAMMAR`, `PAIRING`; sonst `null` |
| `byte_offset` | Integer ab 0 | ja | nicht `null` nur bei `STREAM_BYTE_INADMISSIBLE`, `STREAM_DECODE_ERROR`, `STREAM_TRUNCATED`; sonst `null` |
| `semantic_trade_id` | Integer ab 1 | ja | nicht `null`, wenn der Fehler einen bestimmten semantischen Trade betrifft |
| `signal_source` | String `DECIMAL` oder `NUMPY` | ja | `DECIMAL` genau bei `DECIMAL_SIGNAL_TRAPPED`, `NUMPY` genau bei `NUMPY_FLOATING_POINT_ERROR`; sonst `null` |
| `signal_name` | String; bei `DECIMAL` einer von `InvalidOperation`, `DivisionByZero`, `Overflow`, `Underflow`, `Subnormal`, `Clamped`, `Inexact`, `Rounded`, `FloatOperation`; bei `NUMPY` der Klassenname der Ausnahme | ja | nicht `null` genau dann, wenn `signal_source` nicht `null` ist |
| `signal_operation` | String; bei `DECIMAL` der Name der Kontextmethode oder `HELPER_OPERATOR`; bei `NUMPY` einer von `integers`, `mean`, `percentile`, `float64_conversion` | ja | wie `signal_name` |
| `signal_detail` | String, Ausnahmetext unverändert | ja | wie `signal_name` |
| `decimal_context_flags` | Objekt mit genau den neun Schlüsseln `InvalidOperation`, `DivisionByZero`, `Overflow`, `Underflow`, `Subnormal`, `Clamped`, `Inexact`, `Rounded`, `FloatOperation`, je Boolean | ja | nicht `null` genau dann, wenn der Fehler innerhalb eines Decimal-Kontextblocks entstand; Werte sind die Flaggen des aktiven Blocks nach dem Übertrag |
| `numpy_errstate` | Objekt mit genau den vier Schlüsseln `invalid`, `divide`, `over`, `under`, je String aus `ignore`, `warn`, `raise`, `call`, `print`, `log` | ja | nicht `null` genau in Phase `BOOTSTRAP`; Sollwerte `raise`, `raise`, `raise`, `ignore` |
| `exception_type` | String, Python-Klassenname | ja | nicht `null`, wenn eine zugrundeliegende Ausnahme existiert; `null` bei evaluator-eigenen Prüfungen ohne Ausnahmeobjekt |
| `helper_reason_code` | String oder `null` | ja | siehe Abschnitt 7.4 |
| `helper_findings` | Array von Strings oder `null` | ja | siehe Abschnitt 7.4 |
| `expected` | Objekt | ja | nicht `null` genau bei `IDENTITY_MISMATCH`, `MANIFEST_INCOMPLETE`, `RECONCILIATION_MISMATCH`, `RECONCILIATION_NOT_VERIFIED` |
| `observed` | Objekt | ja | wie `expected` |
| `diagnostics` | Objekt | ja | nicht `null` genau bei `STOP_MAPPING_INVALID` sowie bei `DECIMAL_SIGNAL_TRAPPED` in Phase `STOP_MAPPING` |
| `detail` | String, nicht leer | nein | |

**Unterfelder von `expected`:** `binding` String, nicht nullable, Manifestpfad der Bindung oder Name der Reconciliation-Prüfung; `value` String, nullable, `null` nur bei `MANIFEST_INCOMPLETE`; `source` String, nicht nullable, Manifestreferenz oder Vertragskennung.

**Unterfelder von `observed`:** `available` Boolean, nicht nullable; `value` String, nullable, `null` genau dann, wenn `available` den Wert `false` hat; `unavailable_reason` String aus `STREAM_NOT_FULLY_READ`, `FILE_MISSING`, `EVIDENCE_NOT_IN_MANIFEST`, `FIELD_MISSING`, `NOT_COMPUTED`, nullable, nicht `null` genau dann, wenn `available` den Wert `false` hat; `method` String aus `sha256_over_file_bytes`, `count_lf_terminated_lines`, `manifest_field_read`, `ledger_rederivation`, `artifact_count`, `self_report`, nicht nullable.

**Unterfelder von `diagnostics`:** `kind` String, exakt `"STOP_MAPPING"`, nicht nullable — dies ist die einzige definierte Form; `entry_reference_token` String, nicht nullable; `execution_entry_price_token` String, nicht nullable; `stop_side` String `LONG` oder `SHORT`, nicht nullable; `legacy_sl_text` String, exakt `"0.015"`, nicht nullable; `values` Objekt mit genau den Schlüsseln `legacy_entry_float`, `legacy_sl_float`, `legacy_stop_float`, `stop_decimal`, nicht nullable, je Schlüssel ein Objekt mit `state` String aus `NOT_COMPUTED`, `COMPUTED_FINITE`, `COMPUTED_NONFINITE`, nicht nullable, `value` String, nullable, nicht `null` genau bei `COMPUTED_FINITE`, für die drei Float-Werte als `repr(float)` und für `stop_decimal` als `str(Decimal)`, sowie `nonfinite_kind` String aus `NAN`, `POSITIVE_INFINITY`, `NEGATIVE_INFINITY`, nullable, nicht `null` genau bei `COMPUTED_NONFINITE`; `violated_check` String aus `LEGACY_ENTRY_NONFINITE`, `LEGACY_ENTRY_MISMATCH`, `LEGACY_STOP_NONFINITE`, `STOP_DECIMAL_NONPOSITIVE`, `STOP_DIRECTION_INVALID`, nullable, `null` nur bei `DECIMAL_SIGNAL_TRAPPED`; `check_index` Integer 1 bis 5, nullable, `null` genau dann, wenn `violated_check` `null` ist; `checks_passed` Array von Strings aus derselben Wertemenge in Prüfreihenfolge, nicht nullable, gegebenenfalls leer.

**Kein `NaN` und kein `Infinity`** und keine Zahltokens für diese Werte; nichtendliche Zwischenwerte erscheinen ausschließlich über `state` und `nonfinite_kind`. Diagnosedaten fließen nie in das Audit; die Auditfelder nach Abschnitt 5.5 werden nur für Abbildungen geschrieben, die alle fünf Prüfungen bestanden haben.

### 7.4 `helper_reason_code` und `helper_findings`

| Feld | Typ und erlaubte Werte | Nullable | Bedingung und Regel |
| --- | --- | --- | --- |
| `helper_reason_code` | String oder `null` | ja | Belegt in Phase `HELPER_AUTHORIZE`, wenn ein Rückgabeobjekt des Helpers vorlag. Liegt im Rückgabeobjekt ein Attribut `reason_code` vom Typ `str` vor, wird der String **unverändert** übernommen, auch wenn er nicht zur bekannten `ReasonCode`-Menge gehört. Fehlt das Attribut oder hat es einen anderen Typ, ist das Feld `null`; `detail` nennt dann den Attributnamen `reason_code` und den beobachteten Python-Typnamen. **Keine** automatische Konversion fehlerhafter Werte in einen String. Außerhalb dieser Bedingung `null`. Die bekannte `ReasonCode`-Menge bleibt für die fachliche Klassifikation nach der angenommenen Zuordnung verbindlich; ein unbekannter String ist dort weiterhin `HELPER_RESULT_UNCLASSIFIED` und wird durch diese Diagnoseerlaubnis **nicht** zulässig. |
| `helper_findings` | Array von Strings oder `null` | ja | Belegt in Phase `HELPER_AUTHORIZE`, wenn ein Rückgabeobjekt des Helpers vorlag. Liegt im Rückgabeobjekt ein Attribut `findings` als Tupel vor, dessen sämtliche Elemente vom Typ `str` sind, werden die Elemente in Reihenfolge **unverändert** als JSON-Array übernommen, gegebenenfalls als leeres Array. Fehlt das Attribut, ist es kein Tupel oder enthält es ein Element anderen Typs, ist das Feld `null`; `detail` nennt die Abweichung mit Attributnamen, beobachtetem Typ und bei Elementfehlern dem Index und Typ des ersten abweichenden Elements. **Keine** Konversion. Die Belegung ist **unabhängig** davon, ob `helper_reason_code` gültig, unbekannt oder `null` ist. Außerhalb dieser Bedingung `null`. |

**Belegter Umfang.** Nach diesem vorgeschlagenen Schema sind die vorstehend beschriebenen Fälle darstellbar: ein unbekannter `reason_code`-String; ein fehlendes oder falsch typisiertes `reason_code`-Attribut; ein fehlendes, falsch typisiertes oder in einem Element falsch typisiertes `findings`-Attribut; sowie jede Kombination dieser Fälle, da beide Felder unabhängig voneinander belegt werden. Solche Rückgaben bleiben damit als technischer Fehler mit `code = HELPER_RESULT_UNCLASSIFIED`, `phase = HELPER_AUTHORIZE` und `error_role = PRIMARY` berichtbar. Damit wird **keine** allgemeine Fehlerfreiheit des Fehlerschemas und **keine** Qualifikation behauptet; die synthetische Qualifikation steht aus.

Die angenommene Helper-Klassifikation und die Auffangregel bleiben unverändert. Es werden keine neuen Fehlercodes, Artefakte oder Diagnosefelder eingeführt.

### 7.5 `result.json`

Die zehn Metrikobjekte je Szenario sind genau die im angenommenen Output-/Runtime-Contract, Abschnitt F, festgelegten Objekte `net_pnl`, `final_equity`, `gross_profit`, `gross_loss`, `profit_factor`, `win_rate`, `max_drawdown`, `cagr`, `calmar`, `bootstrap_lcb95` mit den Feldern `status`, `numeric_type`, `unit`, `value`, `reason`. Keine neuen Metriken und keine neuen Selektions-Gates.

**Struktur, vorgeschlagen:** ein Objekt mit `schema_version` `"1.0.0"`, `run_id`, `scenarios` mit genau den Schlüsseln `NOMINAL` und `STRESS`, `integrity` und `all_gates_pass`. Je Szenario: `metrics`, `gates`, `control_evidence`, `all_gates_pass`. `integrity` enthält `reconciliation_ref` mit dem Wert `"reconciliation.json"` und `status` mit dem Wert `"PASS"`, weil die Datei nur nach bestandener Reconciliation entsteht.

**Gate-Eintrag:** `gate_id` String; `expression` String; `metric` String oder `null`; `threshold` Decimal-String oder `null`; `metric_status` String `DEFINED` oder `UNDEFINED` oder `null`; `compared_value` String oder `null`; `status` String `PASS` oder `FAIL`; `fail_reason` String aus `METRIC_UNDEFINED`, `VALUE_NOT_SATISFYING`, `CONTROL_EVIDENCE_FAILED` oder `null` bei `PASS`.

NOMINAL, in dieser Reihenfolge:

| `gate_id` | `expression` | `metric` | `threshold` |
| --- | --- | --- | --- |
| `NET_PNL_GT_0` | `net_pnl > 0` | `net_pnl` | `"0"` |
| `FINAL_EQUITY_GT_10000` | `final_equity > 10000` | `final_equity` | `"10000"` |
| `GROSS_LOSS_GT_0` | `gross_loss > 0` | `gross_loss` | `"0"` |
| `PROFIT_FACTOR_GT_1` | `profit_factor > 1` | `profit_factor` | `"1"` |
| `BOOTSTRAP_LCB95_GT_0` | `bootstrap_lcb95 > 0` | `bootstrap_lcb95` | `"0"` |
| `MAX_DRAWDOWN_LTE_0_05` | `max_drawdown <= 0.05` | `max_drawdown` | `"0.05"` |
| `CAGR_GT_0` | `cagr > 0` | `cagr` | `"0"` |
| `CALMAR_GT_0` | `calmar > 0` | `calmar` | `"0"` |
| `NO_CONTROL_BYPASS` | `control_evidence.all_pass == true` | `null` | `null` |

STRESS, in dieser Reihenfolge:

| `gate_id` | `expression` | `metric` | `threshold` |
| --- | --- | --- | --- |
| `NET_PNL_GT_0` | `net_pnl > 0` | `net_pnl` | `"0"` |
| `FINAL_EQUITY_GT_10000` | `final_equity > 10000` | `final_equity` | `"10000"` |
| `GROSS_LOSS_GT_0` | `gross_loss > 0` | `gross_loss` | `"0"` |
| `PROFIT_FACTOR_GT_1` | `profit_factor > 1` | `profit_factor` | `"1"` |
| `MAX_DRAWDOWN_LTE_0_10` | `max_drawdown <= 0.10` | `max_drawdown` | `"0.10"` |
| `NO_CONTROL_BYPASS` | `control_evidence.all_pass == true` | `null` | `null` |

Die Stress-Objekte `cagr`, `calmar` und `bootstrap_lcb95` behalten ihren angenommenen Status `NOT_REQUIRED` und erhalten kein Gate.

Für Metrik-Gates ist `metric_status` der Status des zugehörigen Metrikobjekts, `compared_value` dessen `value` und bei `UNDEFINED` `null`; der Vergleich erfolgt für Decimal-Metriken über `compare` im angenommenen Kontext und für `bootstrap_lcb95` als Float64-Vergleich mit null. Für `NO_CONTROL_BYPASS` sind `metric`, `threshold`, `metric_status` und `compared_value` **stets `null`**; `fail_reason` ist dort ausschließlich `CONTROL_EVIDENCE_FAILED` oder `null`.

**`control_evidence` je Szenario:** `all_pass` Boolean; `closed_with_blocked_pre_entry` Objekt mit `status` `PASS` oder `FAIL` und `count` Integer ab 0; `sizing_controls` Objekt mit `status` und `count` Integer ab 0 der verletzenden Trade-Zeilen; `helper_classification` Objekt mit `status` `PASS`, `qualification_report_id` String und `qualification_report_sha256` String aus dem Manifest. `all_pass` ist genau dann `true`, wenn alle drei Status `PASS` sind.

**`all_gates_pass`:** je Szenario die Konjunktion über alle Gate-Einträge dieses Szenarios mit `status = PASS`; auf Wurzelebene die Konjunktion von `scenarios.NOMINAL.all_gates_pass` und `scenarios.STRESS.all_gates_pass`. Beide sind Booleans ohne weitere Eingaben; `integrity.status` geht nicht ein.

`result.json` enthält **kein** Entscheidungswort. Der Evaluator gibt ausschließlich `COMPLETED_PASS`, `COMPLETED_FAIL` oder `TECHNICAL_ERROR` aus. Die Protokollentscheidung ist Schritt 8 des Auswahlverfahrens der Preregistration und wird dort im Ledger aufgezeichnet; sie ist kein Evaluator-Ausgang und keine Freigabe.

### 7.6 `completion.json`

Die angenommenen Felder bleiben unverändert: `run_id`, `status`, `metrics_released`, Verweis auf das Manifest, getrennte Eingabeidentitäten, Artefaktliste mit relativem Pfad ohne `..`, Bytes und SHA256, kein Selbsthash. **Vorgeschlagene Schemaergänzung:** `primary_error_sequence`, Integer, nullable, nur bei `TECHNICAL_ERROR` belegt, Verweis auf die `PRIMARY`-Zeile der Fehlerdatei.

---

## 8. Integrität, Reconciliation und Gate-Trennung

**Grundsatz.** Jede Inkonsistenz zwischen den Artefakten eines Laufs und jeder fehlende oder unpassende erforderliche Nachweis ist ein **Integritätsbefund** und verhindert die Freigabe des Ergebnisartefakts. Das bestehende Gate „kein Kontrollbypass“ wird ausschließlich auf integritätsgeprüften Artefakten ausgewertet und kennt keinen Status `NOT_VERIFIED`; `integrity.status` ist deshalb konstruktionsbedingt `PASS`.

**Integritätsblocker** (Phase Reconciliation, Ergebnis `TECHNICAL_ERROR`, kein `result.json`):

| Nr. | Befund |
| --- | --- |
| I1 | `PRE_ENTRY`-Zuordnung: Anzahl je Szenario ungleich `563`; `(scenario, semantic_trade_id)` fehlend oder doppelt; `PRE_ENTRY` ohne genau eine zugehörige Trade- oder Veto-Zeile; `tick` ungleich `entry_tick` |
| I2 | Anzahl `POST_SETTLEMENT` ungleich Anzahl der Trade-Zeilen mit `status = "CLOSED"`; `DAY_CLOSE`-Folge nicht konsistent zu den Wechseln des Kontotags |
| I3 | Gespeicherte Konto- und Tageswerte stimmen nicht mit der Neuableitung aus den kanonischen Werten überein |
| I4 | `daily_loss_limit`, `daily_fee_limit` oder `drawdown_limit` ungleich `"0.01"`, `"0.0025"`, `"0.05"` |
| I5 | Überlappende Intervalle `[entry_tick, exit_tick]` von Trade- oder Veto-Zeilen desselben Szenarios |
| I6 | Veto-Zeile mit `CONTROL_`-Grund ohne `entry_blocked = true`; Veto-Zeile mit `PEE_`-Grund ohne `entry_blocked = false`; `veto_reason` ungleich dem ersten Element von `triggered_controls` |
| I7 | Fehlende erforderliche Evidenz für eine unabhängige Prüfung, Ergebnis `NOT_VERIFIED` |
| I8 | Audit-Datensätze unvollständig oder überzählig gegenüber den P02-Ticks und den ausgeführten OPEN- und CLOSE-Ticks |
| I9 | Qualifikations- oder Identitätsbindung des Manifests bei der Reconciliation als unpassend erkannt |

Fehlende oder unpassende erforderliche Qualifikationsnachweise verhindern bereits den **Start** über `MANIFEST_INCOMPLETE` und andernfalls die Integritätsfreigabe; sie führen **nie** zu einem wirtschaftlichen `COMPLETED_FAIL`.

**Neuableitung zu I3, vorgeschlagener Ersatz für das bloße Wiederholen gespeicherter Vergleiche.** Je Szenario werden aus den Trade-Zeilen in wirtschaftlicher Schließreihenfolge `net_pnl`, `entry_fee`, `exit_fee` und `exit_utc_time` sowie aus Trade- und Veto-Zeilen `entry_tick` und `entry_utc_time` gelesen. Daraus werden im angenommenen Decimal-Kontext die kanonische Serie `C_i`, `E_i = E0 + C_i`, `H_i`, `D_i`, `D_max` sowie je Kontotag `daily_net` und `daily_fees` mit Settlement-Tag-Buchung **neu abgeleitet** und mit den gespeicherten Werten aller `PRE_ENTRY`-, `POST_SETTLEMENT`- und `DAY_CLOSE`-Datensätze, mit `realized_equity_before_entry` jeder Trade-Zeile und mit `applicable_state` jeder Veto-Zeile verglichen. Die Ableitung verwendet ausschließlich die angenommenen Kontoformeln und die aufgezeichneten Netto-Werte; Fills, Gebühren, Mengen und der modellierte Stop-Verlust werden **nicht** nachgerechnet. Der Eintrag heißt `controls_ledger_rederivation` in den unabhängigen Prüfungen des Reconciliation-Artefakts; dies ist eine vorgeschlagene Ergänzung der Prüfliste.

**Vergleichszuordnung.** Decimal-Strings der Konto-, Raten-, Preis-, Gebühren- und Mengenfelder werden beidseitig als Decimal konstruiert, auf Endlichkeit geprüft und über `compare` gleich 0 verglichen; Stringgleichheit ist nicht gefordert, weil die angenommene Serialisierung E-Notation zulässt. `entry_blocked` wird als JSON-Boolean gegen einen Boolean verglichen. `triggered_controls` wird als geordnete Liste mit gleicher Länge und elementweiser exakter Stringgleichheit verglichen. Ganzzahlfelder werden als Ganzzahlen verglichen. `run_id` wird als exakter String verglichen. Tokens geschlossener Wertemengen — `scenario`, `phase`, `status`, `action`, `side`, `classification`, `veto_reason`, `raw_value_cause`, `semantic_final_position`, `economic_final_position` — werden als exakte Strings verglichen. Ausgabe-Zeitstempel werden auf das Format `YYYY-MM-DDTHH:MM:SSZ` geprüft und exakt verglichen. Originaltokens und Base64-Felder werden exakt verglichen, Base64 zusätzlich auf gültige Decodierung. Hashfelder werden auf 64 kleine Hexzeichen geprüft und exakt verglichen. `null` ist nur gleich `null`; ein leerer String ist nie gleich `null`.

**Gate „kein Kontrollbypass“**, ausschließlich auf integritätsgeprüften Artefakten:

| Teilprüfung | Bedingung für `PASS` |
| --- | --- |
| `closed_with_blocked_pre_entry` | keine Trade-Zeile mit `status = "CLOSED"`, deren über `scenario`, `semantic_trade_id` und `tick = entry_tick` zugeordneter `PRE_ENTRY`-Datensatz `entry_blocked = true` oder eine nichtleere `triggered_controls`-Liste trägt |
| `sizing_controls` | je Trade-Zeile mit `status = "CLOSED"`: `quantity >= "0.00001"`; `quantity` ganzzahliges Vielfaches von `"0.000001"`; `quantity * entry_execution_price >= "10"`; `<= "0.10" * realized_equity_before_entry`; `<= realized_equity_before_entry`; Berechnung im angenommenen Decimal-Kontext |
| `helper_classification` | Verweis auf das Manifestfeld der Helper-Qualifikation; konstruktionsbedingt `PASS`, weil ein Lauf ohne gültige Qualifikation nicht startet; **keine** Nachrechnung |

Die Risikogrenze wird ausschließlich dort geprüft, wo der angenommene Vertrag sie verortet: im Erfolgsfall der `EntryAuthorization`-Zuordnung auf den Feldern der Helper-Quote selbst sowie über die technischen Abbrüche bei `PEE_RISK_LIMIT_EXCEEDED` und `PEE_NOTIONAL_LIMIT_EXCEEDED`. Es gibt **keine** Nachrechnung des modellierten Stop-Verlusts aus Artefaktdaten; V-19 bleibt zurückgestellt. Eine fehlende Qualifikation wird **nie** als bestandener Risikonachweis dargestellt.

**Zuordnung der Trade-Zeilen.** Das Trade-Artefakt enthält Zeilen mit `status = "CLOSED"`; der Feldwert `action = "ENTRY_ACCEPTED"` ist ein Attribut dieser Zeilen und keine eigene Zeilenart. Die interne Annahmeentscheidung am OPEN-Tick, der zugehörige `PRE_ENTRY`-Datensatz und die später geschlossene Trade-Zeile werden über `scenario`, `semantic_trade_id` und den Entry-Tick zugeordnet. Veto-Zeilen werden auf dieselbe Weise zugeordnet.

**Bedeutung eines dokumentierten Kontrollverstoßes.** Ein technisch abgeschlossener Bericht über einen Kontrollverstoß bei ansonsten vollständigen und konsistenten Nachweisen ist ein wirtschaftliches FAIL dieses Laufs und nichts weiter. Er ist **weder** eine Implementierungsqualifikation **noch** eine Betriebsfreigabe. Da eine wirtschaftliche Annahme trotz ausgelöster Kontrolle nur aus einem Defekt des Evaluators oder einer unqualifizierten Integration entstehen kann, ist ein solcher Befund vor jedem weiteren Lauf als Implementierungsbefund zu behandeln.

**Externe Prüfungen.** Die Abgleiche gegen Legacy-Trade-Log, Execution-Audit und die finalen S2-, S4- und Loss-Cluster-Zustände sind vorgeschlagene Prüfungen und keine bestandene Qualifikation. Jede ergibt `PASS`, `FAIL` oder `NOT_VERIFIED`; fehlende Evidenz bleibt `NOT_VERIFIED` und blockiert die Freigabe. Die fehlende historische Trade-Normalisierung mit dem bekannten Hash `46706ec9f6446eb5ceecf7782199a8a7fab8a7f91c318ce560f5daa83b98646c` bleibt eine **offengelegte Provenienzlücke**, wird als `PROVENANCE_GAP` und `NOT_VERIFIED` geführt, nicht durch einen Ersatzalgorithmus rekonstruiert und nicht durch Ereigniszahlen, Stream-Hash oder finale FLAT-Position als erledigt ausgegeben.

---

## 9. Bindungsstufen BIND-0 bis BIND-4

Fünf Stufen in strenger zeitlicher Folge. Der Evaluator bindet nichts; er verifiziert. Die Bezeichnung `T0` wird hier **nicht** verwendet; sie ist im Projekt dem prospektiven Start vorbehalten und wird durch diesen Entwurf nicht festgelegt.

| Stufe | Inhalt |
| --- | --- |
| **BIND-0**, bereits belegte Erwartungswerte | gebundener Quellcommit; kanonischer Datensatz `data/l1_full_run.csv` mit SHA256 `530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f`, `4374557` Zeilen, Zeitraum `2017-08-17 04:00:00+00:00` bis `2025-12-31 23:59:00+00:00`; Runner `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` mit SHA256 `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`; Seed `seeds/5m/btcusdt_5m_timing_core_v2.csv` mit SHA256 `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`; PEE-Profil mit SHA256 `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86` und Fingerprint `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`; Stream-Hash `ffa200c601dc6c2bdda0492909d6518573af6de0b621deb91ee3c9f46d7022e3`, `30621902` Ereignisse, `563` semantische Trades, finale Position FLAT; finale Zustandsvergleichswerte der V4-Zertifizierung; Sollzustände der Variablen aus Gruppe A und Gruppe B; `--max-ticks 4374557`. **Vorgeschlagen:** `expected_first_tick = 1` und `expected_last_tick = 4374557`; quellenseitig belegt sind der bei 1 beginnende Loop-Tick und die zertifizierten Endwerte, die Bindung selbst ist neu |
| **BIND-1a**, vorab festzulegende Laufparameter | `--repo` als Checkout des gebundenen Commits; `--data`; `--seed-rel`; `--semantic-out`; Zustände der Variablen aus Gruppe B; Zustandsverzeichnis `live_state` unter der Checkout-Wurzel |
| **BIND-1b**, erst nach dem Erzeugerlauf beobachtbar | Pfad, Bytes und SHA256 des semantischen Stream-Artefakts, des Legacy-Trade-Logs, des Execution-Audits sowie der finalen S2-, S4- und Loss-Cluster-Dateien; Runner-Ausgabezeilen, Rückgabewert, Start- und Endzeit UTC, Python-Identität des Laufs, Commit und Baumstatus |
| **BIND-2**, vollständiges Manifest vor jeder historischen Selektionsauswertung | BIND-0, BIND-1a, BIND-1b; Runtime-Dateibindung nach Abschnitt 10; Helper-Qualifikationsfeld nach Abschnitt 11; Stress-`config_fingerprint`; Manifest-SHA256. Vollständigkeitsregel: kein Pflichtfeld `null` |
| **BIND-3**, Verifikation beim Evaluator-Start | Manifest lesen und auf Vollständigkeit prüfen, sonst `MANIFEST_INCOMPLETE`; Laufverzeichnis exklusiv anlegen; `run_id` erzeugen; Selbstauskunft der Evaluierungsumgebung gegen BIND-2 vergleichen; alle Hashes neu berechnen und vergleichen; Variablenzustände gegen Gruppe A und Gruppe B prüfen; jede Abweichung `IDENTITY_MISMATCH` mit `expected` und `observed` |
| **BIND-4**, Verifikation während und nach dem Lauf | Stream-Hash, Ereigniszahl, erster und letzter Tick, Tradezahl und finale FLAT-Position gegen BIND-0; finale Zustände gegen die Vergleichswerte; unabhängige Prüfungen; erst danach Kennzahlen; der Abschlussnachweis verweist auf Manifestpfad und Manifest-SHA256 und führt erwartete und beobachtete Eingabeidentitäten getrennt |

**Gruppe A**, vom gebundenen Runner gesetzt, Sollzustand `GESETZT` mit dem dort stehenden Wert: `PYTHONDONTWRITEBYTECODE`, `PYTHONHASHSEED`, `TZ`, `L1_OPERATIONAL_PROFILE`, `L1_STARTUP_RECOVERY`, `L1_STARTUP_RECONCILIATION_GATE`, `L1_IU4_MODE`, `L1_IU4_SHADOW_OBSERVATION_ENABLED`, `PEE_MODE`, `L1_MARKET_CSV_PATH`, `SEEDS_5M_CSV`, `L1_SYMBOL`, `L1_GATE_MODE`, `L1_FEE_ROUNDTRIP`, `L1_DECISION_TICK_SECONDS`, `THRESH_5M`, `L1_TIMING_V2_SHADOW`, `L1_TIMING_V2_HISTORY_LEN`, `L1_TEST_FORCE_INTENTS`, `L1_TP_PCT`, `L1_SL_PCT`, `L1_LONG_TIME_STOP_SEC`, `L1_SHORT_TIME_STOP_SEC`.

**Gruppe B**, im gebundenen Laufzeitpfad gelesen und vom Runner nicht gesetzt; je Schlüssel wird der Zustand `GESETZT` mit Wert, `LEER` oder `UNGESETZT` aufgezeichnet: `L1_RESUME_AFTER_SNAPSHOT_ID` mit Sollzustand `UNGESETZT` oder `LEER`; `L1_AUDIT_LOG_PATH`, `L1_TRADE_LOG_PATH`, `L1_S2_POSITION_PATH`, `L1_LOSS_CLUSTER_STATE_PATH` und `L1_LOG_PATH`, bei `UNGESETZT` gilt der tatsächlich verwendete Pfad aus BIND-1b und **nie** ein Launcher-Standardwert; `L1_TRADES_WINDOW_HOURS`, `L1_TEST_FORCE_BUY_EVERY`, `L1_TEST_FORCE_SELL_EVERY`, `L1_TEST_FORCE_WARMUP_TICKS`, `L1_REQUIRE_WSL`, `L1_SIGNAL_WEIGHTS_JSON`, `L1_INTENT_DEBUG`, `L1_IU4_APPROVED_THROTTLE_PROFILE`, `L1_IU4_ATOMIC_STATE_DIRECTORY`, `L1_IU4_COORDINATOR_ID`, `L1_IU4_SYMBOL`, `L1_IU4_REPOSITORY_COMMIT`, `L1_IU4_SHADOW_OBSERVATION_EVIDENCE_PATH`, `L1_IU4_SHADOW_OBSERVATION_MAX_RECORDS`, `L1_IU4_SHADOW_OBSERVATION_WORK_DIRECTORY` sowie die siebzehn `PEE_`-Profilschlüssel und `PEE_REFERENCE_STOP_RATE`, jeweils mit Sollzustand `UNGESETZT`.

Es wird **keine** pauschale Speicherung beliebiger Umgebungsvariablen und **keiner** Zugangsdaten vorgeschlagen; nur die genannten Schlüssel werden aufgezeichnet. Die Vollständigkeit der Gruppe B gegen den gesamten gebundenen Laufzeitpfad beruht auf den gelesenen Modulen und ist in der Qualifikation statisch zu bestätigen.

Launcher-Standardwerte sind zu keinem Zeitpunkt Belegquelle für historische Artefaktpfade. Kein Reproduktionslauf wird durch diesen Entwurf autorisiert.

---

## 10. Runtime-Datei- und Importbindung

Alle konkreten Werte sind **OFFEN**. Festschreibung in BIND-2 durch Governance, Verifikation in BIND-3 durch Neuberechnung jedes SHA256 und Vergleich. Versions-Selbstauskünfte werden zusätzlich aufgezeichnet und **ersetzen** keine Dateibindung.

| Gegenstand | Bindungsfelder und Verfahren |
| --- | --- |
| Interpreter | `runtime.python.executable_path` als aufgelöster Realpfad des Interpreters, `runtime.python.executable_sha256`; falls gegen eine gemeinsame Python-Bibliothek gebunden, zusätzlich `runtime.python.shared_library_path` und `runtime.python.shared_library_sha256`; ob das zutrifft, ist OFFEN. Ergänzend die Selbstauskünfte zu Version, Implementierung und Plattform |
| Decimal-Backend | `runtime.decimal.backend` mit Wert `C` oder `PYTHON`; `runtime.decimal.backend_module_path` als Realpfad der tatsächlich geladenen Backend-Datei und `runtime.decimal.backend_sha256`; `runtime.decimal.frontend_path` und `runtime.decimal.frontend_sha256` für das Frontend-Modul. Ergänzend die Bibliotheksversions-Selbstauskunft, sofern vorhanden |
| NumPy | `runtime.numpy.roots` mit der Wurzelkennung `numpy` als Realpfad des Paketverzeichnisses und der Wurzelkennung `numpy.libs` als Geschwisterverzeichnis oder `null`; `runtime.numpy.file_manifest`; `runtime.numpy.manifest_sha256`; `runtime.numpy.dist_info_record_sha256`. Ergänzend die Versions-Selbstauskunft |
| Legacy-Helper | `legacy.paper_economics.path` mit Wert `live_l1/core/paper_economics.py` und `legacy.paper_economics.sha256` mit erwartetem Wert `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae`; `legacy.package_inits` für `live_l1/__init__.py` und `live_l1/core/__init__.py`, die am gebundenen Commit 0 Bytes umfassen |
| Evaluator | `evaluator.roots` mit der Wurzelkennung `evaluator` als Realpfad des Evaluator-Pakets; `evaluator.file_manifest`; `evaluator.manifest_sha256`; `evaluator.git_commit`; `evaluator.git_tree_clean` |
| Import-Abschluss | `runtime.import_closure` und `runtime.import_closure_sha256` |
| Dependency-Lock | `dependency_lock.path` und `dependency_lock.sha256` einer Lockdatei mit exakten Versionsfestlegungen und Hash-Einträgen je Distribution; `dependency_lock.installed_distributions` mit `name`, `version` und `record_sha256` je Distribution. Die vorhandene Anforderungsdatei des Repositoriums ist eine Entwicklungsvorgabe und **kein** Lock |

**Dateimanifest.** Wurzelkennungen bilden die geschlossene Menge `numpy`, `numpy.libs`, `evaluator`; der Schlüssel eines Eintrags ist das Paar aus Wurzelkennung und relativem Pfad, sodass gleiche relative Pfade aus verschiedenen Wurzeln nicht kollidieren. Erfasst wird jede reguläre Datei und jeder symbolische Link unterhalb der Wurzel, rekursiv, unter Auslassung von Verzeichnissen mit dem Namen `__pycache__`, ohne Verfolgung von Links. Ein Datensatz besteht aus genau sieben Werten in dieser Reihenfolge: `root_id`, `relative_path`, `entry_type` mit Wert `REGULAR` oder `SYMLINK`, `bytes`, `sha256`, `link_target`, `target_sha256`. Bei `REGULAR` sind `link_target` und `target_sha256` `null`; bei `SYMLINK` sind `bytes` und `sha256` `null`, `link_target` trägt den wörtlichen Linkinhalt und `target_sha256` den SHA256 der aufgelösten Zieldatei, sofern diese eine reguläre Datei ist, sonst `null`. Sortierung aufsteigend nach dem Paar aus Wurzelkennung und relativem Pfad als UTF-8-Bytefolgen. Serialisierung je Datensatz als JSON-Array der sieben Werte in dieser Reihenfolge mit `ensure_ascii` und den Trennzeichen Komma und Doppelpunkt ohne Leerzeichen, gefolgt von genau einem LF. Der Aggregat-SHA256 läuft über die UTF-8-Bytes aller so gebildeten Zeilen in Sortierreihenfolge.

**Importliste.** Erfasst wird nach den Importen des Evaluators jeder Eintrag der Modultabelle. Ein Datensatz besteht aus genau **neun** Werten in dieser Reihenfolge: `module_name`, `module_kind` mit Wert aus `SOURCE`, `EXTENSION`, `NAMESPACE`, `BUILTIN`, `FROZEN`, `reported_path` als der vom Importsystem gemeldete Dateipfad oder `null`, `file_path` als Realpfad oder `null`, `file_sha256` oder `null`, `cached_path` als gemeldeter Bytecode-Pfad oder `null`, `cached_exists` als Boolean, `cached_sha256` oder `null`, `namespace_paths` als sortiertes Array von Realpfaden oder `null`. Für nicht anwendbare Pfad- und Hashfelder wird ausdrücklich `null` verwendet; es findet keine Ersatzbelegung statt. Sortierung aufsteigend nach `module_name` als UTF-8-Bytefolge. Serialisierung je Datensatz als JSON-Array der neun Werte in dieser Reihenfolge mit denselben Regeln wie beim Dateimanifest und genau einem LF je Zeile. **Alle neun Felder** sind Bestandteil des Aggregats; der Aggregat-SHA256 läuft über die UTF-8-Bytes aller Zeilen in Sortierreihenfolge.

**Import-Allowlist.** Nach den Importen des Evaluators darf die Modultabelle unter dem Präfix `live_l1` genau die folgenden Einträge enthalten:

| Eintrag | Art | Bedingung |
| --- | --- | --- |
| `live_l1` | reguläres Elternpaket | Initialisierungsdatei mit 0 Bytes, wie am gebundenen Commit |
| `live_l1.core` | reguläres Elternpaket | Initialisierungsdatei mit 0 Bytes |
| `live_l1.tools` | Namespace-Paket ohne Initialisierungsdatei, wie am gebundenen Commit, oder reguläres Paket mit einer Initialisierungsdatei von 0 Bytes | im Namespace-Fall werden alle Pfadeinträge als Realpfade in `namespace_paths` aufgezeichnet |
| `live_l1.core.paper_economics` | erlaubter Helper | SHA256 wie gebunden |
| `live_l1.tools.g10b_evaluator` und dessen Untermodule | Evaluator-Paket | Dateien im Evaluator-Manifest |

Jeder andere Eintrag unter diesem Präfix — insbesondere `loop`, `execution`, `market`, `logger`, `state_store`, `intent`, `guards`, `paper_artifacts`, die Shadow- und IU4-Module und alle übrigen Werkzeuge — ist ein technischer Fehler beim Start. Eine Initialisierungsdatei eines Elternpakets mit mehr als 0 Bytes ist ebenfalls ein Fehler, weil sie Code ausführen würde. Es werden **keine** weiteren Legacy-Fachmodule freigegeben. `paper_artifacts` und die Shadow-Module werden ausschließlich im Qualifikationsprozess als Orakel importiert, nie im Produktionslauf.

**Grenzen der Abdeckung, ausdrücklich.** Weder die Modultabelle allein noch vorhandene Quelltext-Hashes belegen, welcher Bytecode tatsächlich ausgeführt wurde oder welche dynamischen Abhängigkeiten in den Prozess geladen sind. Vorhandene Bytecode-Cachedateien werden über `cached_path`, `cached_exists` und `cached_sha256` lediglich dokumentiert. **Das konkrete Verfahren zum Nachweis des tatsächlich geladenen Bytecodes und weiterer dynamischer Abhängigkeiten bleibt eine offene technische Qualifikations- und Bindungsfrage und ist vor einer entsprechenden Runtime-Freigabe zu schließen.** Es wird hierfür kein Ersatzmechanismus vorgeschlagen.

---

## 11. Helper-Qualifikationsbindung

`helper_qualification` ist ein **neues vorgeschlagenes Bindungsfeld** des Manifests in BIND-2 für eine Qualifikation, die die angenommenen Verträge bereits fordern: bestehende Hilfsfunktionen dürfen erst nach Qualifikation gegen die genehmigten Regeln wiederverwendet werden.

Teilfelder: `report_id`, `report_path`, `report_bytes` und `report_sha256` als Identität des Qualifikationsberichts; `result` mit dem geforderten Wert `PASS`; `scope.functions` mit genau den wiederverwendeten Funktionen `PaperEconomicsConfig`, `model_fill_price`, `calculate_fee_quote`, `floor_quantity_to_step`, `authorize_entry`; `scope.rules` mit der `EntryAuthorization`-Zuordnung einschließlich Auffangregel, den angenommenen numerischen Fixtures N01 bis N10, den Fixtures des Output-/Runtime-Contracts zu Rundung, Mengenschritt und kanonischer Equity, den Mitternachts- und Veto-Fällen, dem Subnormal-Erhalt und der Kontextwirkung auf die Helper-Operatoren; `helper_identity` mit den SHA256 der Helper-Datei und der Initialisierungsdateien; `evaluator_identity` mit Evaluator-Manifest-Hash und Import-Abschluss-Hash zum Zeitpunkt der Qualifikation; `runtime_identity` mit Interpreter-, Decimal-Backend-, NumPy-Manifest- und Dependency-Lock-Hash zum Zeitpunkt der Qualifikation; `numeric_conditions` mit den vollständigen Kontextparametern und Trap-Einstellungen nach P03 bis P06 und dem NumPy-Fehlerzustand nach P07; `qualified_at_utc` und `approval_state`.

**Gültigkeitsregel in BIND-3.** Die Qualifikation gilt nur, wenn `result` den Wert `PASS` trägt, `scope` die geforderten Funktionen und Regeln vollständig enthält, der Bericht unter dem angegebenen Pfad existiert und seine Bytes und sein SHA256 übereinstimmen und jede Identität mit den aktuellen Manifestwerten übereinstimmt. Jede Abweichung, ein fehlendes Teilfeld, ein bloßer Pfad oder eine beliebige Referenz ohne diese Übereinstimmungen ist **keine** bestandene Qualifikation und führt vor jeder Verarbeitung zu `MANIFEST_INCOMPLETE`. Konkrete Berichtswerte sind **OFFEN**; durch diesen Entwurf wird keine Qualifikation durchgeführt und kein Bericht erstellt.

---

## 12. Vorgeschlagene Schemaergänzungen, gesammelt

| Ort | Ergänzung |
| --- | --- |
| `input_audit.jsonl` | die sechs Stop-Felder nach Abschnitt 5.5 |
| `completion.json` | `primary_error_sequence` |
| Reconciliation-Artefakt | Eintrag `controls_ledger_rederivation` in den unabhängigen Prüfungen |
| Manifest | `helper_qualification`, die Runtime-Dateibindung und die Importliste nach den Abschnitten 10 und 11 |
| neue Dateien | `trades.jsonl`, `vetoes.jsonl`, `errors.jsonl` sowie die Struktur von `result.json` |

Sämtliche Einträge dieser Tabelle sind Vorschläge und nicht angenommen. Über die hier genannten hinaus werden keine Felder, Artefakte, Module, Prüfmechanismen oder Funktionen eingeführt.

---

## 13. Verfahrensvermerk

Im Verlauf der Ausarbeitung wurde eine Eigenschaftsprüfung des Standardbibliotheksmoduls `decimal` mit dem System-Python ausgeführt, obwohl das damalige Mandat ausschließlich lesend war. Dies ist bereits berichtet und wird hier ausschließlich als **Mandatsüberschreitung** festgehalten. Ihr Ergebnis ist **kein** Qualifikationsbeleg, wird für die Festlegungen dieses Entwurfs nicht verwendet und nicht erneut untersucht. Abschnitt 3 stützt sich allein auf die dokumentierte Kopiersemantik des lokalen Kontextblocks und dessen Wiederherstellung des zuvor aktiven Kontexts.

Davon getrennt ist die statische Quellenprüfung dieses Entwurfs: lesende Git-Operationen, Hashprüfungen getrackter Dateien und Textsuchen am gebundenen Quellcommit und am Repository-Stand der Ausarbeitung.

---

## 14. OFFENE_DEFINITIONEN

**Statuszuordnung nach der Annahme, siehe Abschnitt 20.** Die Einträge **D4 bis D17** sind durch Abschnitt 20 formal **angenommen**; ihre Führung in dieser Tabelle beschreibt den geprüften Entwurfsstand und wird nicht umgeschrieben. **Offen bleiben ausschließlich D1, D2 und D3** als ungelöste Definitions- und Qualifikationsauflagen.

| Nr. | Offene technische Definition |
| --- | --- |
| D1 | Verfahren zum Nachweis des tatsächlich ausgeführten Bytecodes und der tatsächlich geladenen dynamischen Abhängigkeiten einschließlich der Bewertung vorhandener Cachedateien; vor einer Runtime-Freigabe zu schließen; kein Ersatzmechanismus vorgeschlagen |
| D2 | Vollständigkeit der Variablengruppe B gegen den gesamten gebundenen Laufzeitpfad; bisher aus den gelesenen Modulen abgeleitet, statische Bestätigung offen |
| D3 | Welche Decimal-Signalflaggen eine Implementierung unmittelbar vor einem getrappten Signal setzt; bestimmt die Aussagekraft des Flagübertrags und des Diagnosefelds |
| D4 | Annahme der in Abschnitt 12 gesammelten Schemaergänzungen |
| D5 | Name, Format und Schema der Fehlerdatei; der angenommene Vertrag legt nur deren Existenz fest |
| D6 | Dateinamen, Aufteilung und Zeilenformat der Trade- und Veto-Artefakte; die Schemata selbst sind angenommen |
| D7 | Auslöser, Bedeutung von „relevant“, Belegung von `tick` und `utc_time` sowie Behandlung ereignisloser Tage beim `DAY_CLOSE` |
| D8 | Auswahl der Audit-Datensätze über die zwingenden P02-Ticks hinaus |
| D9 | `veto_reason`-Wertemenge und Prioritätsregel |
| D10 | Zuordnung des Befunds `closed_with_blocked_pre_entry` zum wirtschaftlichen Gate statt zur Integrität; mit dem angenommenen Wortlaut wäre auch die andere Zuordnung vereinbar |
| D11 | Behandlung eines Fehlschlags bei der Umbenennung der Fehlerdatei: der Befund erscheint nur auf der Standardfehlerausgabe und über den Dateinamen in der Artefaktliste, nicht in der Fehlerdatei selbst |
| D12 | Anordnung der Szenario- und Gate-Objekte im Ergebnisartefakt; die Feldmenge selbst ist angenommen |
| D13 | Byteregeln des Stroms über das Wagenrücklaufzeichen hinaus, namentlich Nullbyte, UTF-8-Decodierbarkeit und Byte-Order-Mark |
| D14 | `symbol`-Grammatik |
| D15 | Zeitregression an NOOP-Ticks auf Stromebene |
| D16 | Modulort und Einstiegspunkt des Evaluators sowie die technische Durchsetzung der Importtrennung |
| D17 | Bindung von `expected_first_tick` und `expected_last_tick` |

---

## 15. OFFENE_BINDUNGEN

**Statuszuordnung nach der Annahme, siehe Abschnitt 20.** Sämtliche Einträge **B1 bis B14 bleiben offen**; ihre konkreten Werte bleiben `null`. Die Annahme ergänzt **keine** noch fehlenden Verfahren, Identitäten oder Nachweise. Die vertraglich bestimmten Zeitpunkte bleiben unverändert: die erforderlichen Bindungen und Qualifikationen müssen jeweils **vor** dem Schritt erfüllt sein, den der Vertrag dafür bestimmt, insbesondere **vor der Beobachtung historischer Selektionskennzahlen** und nicht erst vor einem Live-Betrieb.

| Nr. | Noch unbekannter konkreter Bindungswert |
| --- | --- |
| B1 | Laufparameter aus BIND-1a: `--repo`, `--data`, `--seed-rel`, `--semantic-out`, Zustandsverzeichnis |
| B2 | Artefaktidentitäten aus BIND-1b: Pfad, Bytes und SHA256 von semantischem Stream, Legacy-Trade-Log, Execution-Audit sowie finalen S2-, S4- und Loss-Cluster-Dateien |
| B3 | Runner-Ausgabezeilen, Rückgabewert, Start- und Endzeit, Python-Identität, Commit und Baumstatus des Erzeugerlaufs |
| B4 | Zustände der Variablen aus Gruppe B |
| B5 | Interpreter: Realpfad und SHA256, gegebenenfalls gemeinsame Bibliothek |
| B6 | Decimal-Backend: Kennung, Realpfade und SHA256 von Backend und Frontend |
| B7 | NumPy: Wurzelpfade, vollständiges Dateimanifest, Aggregat-Hash, Distributionsnachweis |
| B8 | Evaluator: Wurzelpfad, Dateimanifest, Aggregat-Hash, Commit und Baumstatus |
| B9 | Import-Abschluss und dessen Aggregat-Hash |
| B10 | Dependency-Lock: Pfad, SHA256 und installierte Distributionen |
| B11 | Sämtliche Werte des Helper-Qualifikationsfelds einschließlich Berichtsidentität |
| B12 | Stress-`config_fingerprint` |
| B13 | Manifestpfad und Manifest-SHA256 |
| B14 | `run_id` und sämtliche Laufartefakte einschließlich ihrer Bytes und Hashes |

Keiner dieser Werte wird durch diesen Entwurf erhoben, berechnet, gehasht oder erfunden. Die fehlende historische Trade-Normalisierung ist keine offene Bindung, sondern eine offengelegte Provenienzlücke ohne Ersatz.

---

## 16. Statischer Konsistenzbefund

Geprüft wurde gegen die fünf angenommenen Vertragspaare und die am gebundenen Quellcommit gelesenen Quellstellen, ausschließlich statisch und ohne Ausführung.

- Berechnungsregeln, P01 bis P07 und Selektions-Gates sind unverändert; es wird kein zusätzliches Selektions-Gate eingeführt.
- Die Veto-Paarung ist vollständig: Veto-Zeilen entstehen nur beim semantischen CLOSE, und das Stromende verlangt je Szenario `563` gleich wirtschaftlich geschlossenen Trades zuzüglich vollständiger Veto-Paare.
- Kennzahlen werden erst nach der erforderlichen Integritäts- und Reconciliation-Prüfung freigegeben; fehlende Evidenz bleibt `NOT_VERIFIED` und blockiert.
- Die historische Trade-Normalisierung bleibt eine Provenienzlücke ohne Ersatzalgorithmus.
- V-19 bleibt zurückgestellt; es gibt keine zweite Berechnung des modellierten Stop-Verlusts.
- Die Wurzelmenge der Dateimanifeste ist geschlossen, und das Importformat umfasst genau neun Felder ohne fallweise Zusatzfelder.
- Fehlende oder unpassende Qualifikationsnachweise sind Start- oder Integritätsblocker und nie ein wirtschaftliches Ergebnis.

Verbleibende konkrete Widersprüche: **keine festgestellt** im genannten Prüfungsumfang. Verbleibende Abhängigkeiten sind die in Abschnitt 14 geführten offenen Definitionen, insbesondere die Lesart von „relevant“ beim `DAY_CLOSE` und die Zuordnung des Befunds `closed_with_blocked_pre_entry`; beide sind eindeutige Vorschläge, aber nicht angenommen.

---

## 17. JSON-/Markdown-Bindung

Die maschinenlesbare Begleitdatei `docs/review/evidence/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.json` enthält im Feld `contract_text` den **vollständigen** Text dieser Markdown-Datei einschließlich Titel, Quellenabschnitten und abschließendem Zeilenumbruch.

Geltungsbereich der Text- und Hashfelder:

- `markdown_sha256` ist der SHA256 der **vollständigen Bytes dieser Markdown-Datei**.
- `contract_text_sha256` ist der SHA256 der **UTF-8-Kodierung von `contract_text`** und bezieht sich damit auf **dieselben** vollständigen Markdown-Bytes.
- Beide Werte sind daher identisch; ihre Gleichheit ist der Nachweis der vollständigen und unveränderten Einbettung.
- `markdown_bytes` ist die Bytezahl derselben Markdown-Bytes.
- Die JSON-Datei enthält **keinen Hash ihrer selbst** und keine zyklische Hashbindung.
- Die JSON-Datei ist strikt gültiges JSON ohne `NaN` und ohne `Infinity`.

Diese Markdown-Datei wird als UTF-8 mit LF-Zeilenenden und abschließendem LF geführt.

---

## 18. Quellenidentitäten

**Gebundener Quellcommit:** `3c5927127a03de13d8c80a720f5c8b97a2a36789`

| Pfad | SHA256 |
| --- | --- |
| `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` | `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292` |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` |
| `live_l1/core/execution.py` | `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3` |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` |
| `live_l1/state/paper_artifacts.py` | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` |
| `live_l1/logs/logger.py` | `cbfb29708bc81bbf7f2d524abe10a21382213973f897038bc8c315bad1323cfd` |
| `live_l1/io/market.py` | `014bbf7328c4bd354fb8a254979ef463670e49557c5ed89e5628a3b35dc8cd0e` |
| `config/pee/PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json` | `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86` |

Weitere am selben Commit gelesene, in den angenommenen Verträgen nicht einzeln per SHA256 aufgeführte Quelldateien: `live_l1/core/clock.py`, `live_l1/core/intent.py`, `live_l1/core/paper_economics_shadow.py`, `live_l1/core/paper_economics_shadow_runtime.py`, `live_l1/core/paper_iu4_shadow_runtime_gate.py`, `live_l1/operational_profiles.py`, `live_l1/tools/safe_launch.py`, `live_l1/tools/startup_validator.py`, `tests/live_l1/test_paper_economics_profile_candidate.py`.

Die zehn Dateien der fünf angenommenen Vertragspaare sind mit ihren geprüften Identitäten in Abschnitt 1.4 aufgeführt und wurden vor und nach der Erstellung dieses Entwurfs auf unveränderte Bytes geprüft.

---

## 19. Schlussvermerk

**Zeitliche Einordnung.** Dieser Abschnitt beschreibt den geprüften Entwurfsstand und wird durch Abschnitt 20 zeitlich eingeordnet, nicht umgeschrieben. Der aktuelle Dokumentstatus ist **APPROVED_FOR_ADOPTION**; die formale Annahme und ihre Reichweite ergeben sich allein aus Abschnitt 20 und dem Statusvermerk im Dokumentkopf.

Dieser Entwurf ist **DRAFT_NOT_BINDING**. Sämtliche Integrations-, Schema-, Pfad-, Diagnose- und Bindungsfestlegungen sind unverbindliche Vorschläge. Die angenommenen Vertragspaare, P01 bis P07, K01 bis K08, sämtliche Berechnungsregeln und die Selektions-Gates bleiben unverändert und stehen nicht erneut zur Genehmigung. V-19 bleibt zurückgestellt.

Autorisiert ist ausschließlich die Erstellung dieser beiden Entwurfsdateien. Aus ihr folgt **keine** formale Annahme und **keine** Implementierungs-, Qualifikations-, Test-, Kandidatenmanifest-, Selektions-, Staging-, Commit-, Push-, Synchronisierungs- oder Market-Run-Freigabe. Kein historischer Final-OOS-Anspruch, kein prospektiver Startzeitpunkt und keine Paper-Trading- oder Live-Kapital-Freigabe folgen aus diesem Entwurf.

---

## 20. Formale Annahmeaufzeichnung

Datum der Annahme (UTC): **2026-09-15**, aufgezeichnet um `2026-09-15T16:03:52Z`.

### 20.1 Annahmeautorität und Gegenstand

Die Annahme beruht auf einer **ausdrücklichen Nutzerfreigabe in der laufenden Konversation**. Angenommen werden die in diesem Dokument konkret ausformulierten neuen Vertragsfestlegungen:

- Modulgrenzen, Datenfluss und Importtrennungsanforderung nach Abschnitt 2;
- das lokale Decimal-Kontextverfahren mit Vorlagenkontext, Blockbildung, Identitätsprüfung und Flagübertrag nach Abschnitt 3;
- die Helper-Zuordnung einschließlich der getrennten Begründungen der Nichtverwendung und der vollständigen Profilabbildung nach Abschnitt 4;
- die Strom-, Parser- und Ledger-Regeln einschließlich Byteregeln, `symbol`, Zeitfolge, Audit-Auswahl und Stop-Audit nach Abschnitt 5;
- die wirtschaftlichen Szenarien einschließlich Kontotag-Initialisierung, Gleichheits-, Fortschritts- und Rückschrittprüfung, Kontrollreihenfolge, `veto_reason`-Menge, Veto-Kontoneutralität, `DAY_CLOSE` und Definitheitsbedingungen nach Abschnitt 6;
- Artefakte, Schemata und Abschlussregeln einschließlich Veröffentlichungsreihenfolge, reservierter Abschlussnamen, Hashlisten- und Freigaberegel sowie der vollständigen Fehler-, Diagnose-, Helper-Diagnose- und Gate-Schemata nach Abschnitt 7;
- die Trennung von Integritätsblockern und wirtschaftlichem Kontroll-Gate einschließlich Neuableitung und Vergleichszuordnung nach Abschnitt 8;
- die Bindungsstufen BIND-0 bis BIND-4 mit den Variablengruppen A und B nach Abschnitt 9;
- die Runtime-Datei- und Importmanifestformate einschließlich Wurzelkennungen, Neun-Feld-Importdatensatz und Import-Allowlist nach Abschnitt 10;
- die Helper-Qualifikationsbindung als Feldstruktur und Gültigkeitsregel nach Abschnitt 11;
- die gesammelten Schemaergänzungen nach Abschnitt 12.

Damit sind die Entscheidungen **D4 bis D17** angenommen.

Technische Regeltexte, Grammatiken, Tabellen, Berechnungsregeln, Gates und Quellenbindungen sind **unverändert**. Diese Aufzeichnung ergänzt ausschließlich den Annahmevermerk, die Statuszuordnung und die Review-Korrektur.

### 20.2 Geprüft angenommene Ausgangsidentitäten

Angenommen wurden genau die geprüften Bytes des Entwurfsstands:

| Datei | Bytes | SHA256 |
| --- | --- | --- |
| `docs/review/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.md` | 82484 | `4952a5cc9be09f22b4c66bca42ff91b6dd334f5d1f935cff44e9174b3e147daf` |
| `docs/review/evidence/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.json` | 99462 | `b81cfb97af0d87f4cccdc76fff794fe36f267aa90012bd4d9a39ec36e39cba6b` |

Beide Werte wurden unmittelbar vor dieser Aufzeichnung erneut nachgerechnet und stimmten überein. Durch die Aufnahme dieses Abschnitts ändern sich die Bytes und Hashes beider Dateien; die in der JSON-Begleitdatei geführten Felder `markdown_sha256`, `contract_text_sha256` und `markdown_bytes` beziehen sich stets auf den **aktuellen** Markdown-Stand, während die Felder mit dem Präfix `reviewed_` die oben genannten **geprüften Ausgangsidentitäten** festhalten.

### 20.3 Review-Grundlage

Die vom Nutzer berichtete unabhängige Prüfung lautete **APPROVE_FOR_FORMAL_ADOPTION**. Ihr einziges Finding wurde durch eine gezielte Quellenprüfung widerlegt; siehe Abschnitt 20.4. Eine **zusätzliche vollständige Neuprüfung** des Dokuments wurde dabei **nicht** behauptet und wird hier nicht bescheinigt.

### 20.4 Review-Korrektur zum finalen Stress-Drawdown-Gate

Das beanstandete finale Stress-Gate war **bereits korrekt**. Die gezielte Leseprüfung der angenommenen Quellen ergab:

- **Operative Kontrolle:** neue wirtschaftliche Entries werden ab `realized_drawdown_rate >= 0.05` in **beiden** Szenarien blockiert; Exits bleiben stets erlaubt. Beleg: Evaluator-Klarstellung, „Block new entries at daily_loss_rate>=0.01, daily_fee_rate>=0.0025 or realized_drawdown_rate>=0.05 […] for both scenarios“ sowie „An exit always remains permitted even when it causes a limit to be exceeded“; ergänzend Output-/Runtime-Vertrag, Abschnitt E, `drawdown_limit` exakt `"0.05"` in beiden Szenarien.
- **Finales Stress-Gate:** `max_drawdown <= 0.10`, unverändert. Beleg: Output-/Runtime-Vertrag, Abschnitt F, Stress-Gates.
- **Ausdrückliche Trennung beider Regeln:** Evaluator-Klarstellung, „The stress result gate of DD<=0.10 does not relax the operative DD control of 0.05.“

Einordnung ausschließlich dieses einen Gates: `max_drawdown` gleich 0.099999 besteht, gleich 0.10 besteht, gleich 0.100001 besteht nicht. Diese Aussagen sind **keine** Gesamtlauffreigabe; der Lauf bleibt konjunktiv an alle übrigen Gates, den Kontrollnachweis und die vorgelagerte Integritäts- und Reconciliation-Prüfung gebunden.

Dies korrigiert **ausschließlich den Review**, nicht eine Vertragsregel. Die Zeile des Abschnitts 7.5 mit `max_drawdown <= 0.10` und die Schwelle `"0.10"` bleiben unverändert, ebenso die operative Bindung `"0.05"` in Abschnitt 8.

### 20.5 Statuszuordnung gegenüber den historischen Vermerken

| Gegenstand | Status nach dieser Annahme |
| --- | --- |
| Konkret ausformulierte neue Vertragsfestlegungen der Abschnitte 2 bis 12 | **ANGENOMMEN** |
| Entscheidungen D4 bis D17 aus Abschnitt 14 | **ANGENOMMEN** |
| D1, D2, D3 aus Abschnitt 14 | **OFFEN**, ungelöste Definitions- und Qualifikationsauflagen |
| B1 bis B14 aus Abschnitt 15 | **OFFEN**, konkrete Werte bleiben `null` |
| V-19 | **ZURÜCKGESTELLT**, unverändert |
| Entwurfs- und Vorschlagsformulierungen in den Abschnitten 1.1, 12, 14, 15 und 19 | beschreiben den geprüften Entwurfsstand; zeitlich eingeordnet, nicht umgeschrieben |
| Angenommene Vertragspaare, P01 bis P07, K01 bis K08, Berechnungsregeln, Selektions-Gates | **UNVERÄNDERT**, nicht erneut zur Genehmigung gestellt |

### 20.6 Verbleibende Auflagen

Ausdrücklich **nicht** geschlossen und **nicht** angenommen werden:

- **D1** — das Verfahren zum Nachweis des tatsächlich ausgeführten Bytecodes und der tatsächlich geladenen dynamischen Abhängigkeiten; vor einer entsprechenden Runtime-Freigabe zu schließen; kein Ersatzmechanismus;
- **D2** — die statische Bestätigung der Vollständigkeit der Variablengruppe B gegen den gesamten gebundenen Laufzeitpfad;
- **D3** — welche Decimal-Signalflaggen eine Implementierung unmittelbar vor einem getrappten Signal setzt;
- **B1 bis B14** — sämtliche konkreten Eingabe-, Evidenz-, Runtime-, Dependency-, Qualifikations- und Laufidentitäten; ihre Werte bleiben `null`, und es werden keine Verfahren, Identitäten oder Nachweise ergänzt;
- die tatsächliche Verwendung der Economics-Hilfsfunktionen und deren Qualifikation nach Abschnitt 11;
- sämtliche Implementierungs-, Qualifikations-, Test-, Manifest- und Ausführungsschritte jeder Art.

Die vertraglich bestimmten Zeitpunkte bleiben unverändert: erforderliche Bindungen und Qualifikationen müssen jeweils **vor** dem Schritt erfüllt sein, den der Vertrag dafür bestimmt, insbesondere **vor der Beobachtung historischer Selektionskennzahlen** und ausdrücklich nicht erst vor einem Live-Betrieb. Die fehlende historische Trade-Normalisierung bleibt eine offengelegte Provenienzlücke ohne Ersatz.

### 20.7 Reichweite der Annahme

Diese Annahme betrifft ausschließlich die fachlichen Vertragsfestlegungen dieses Dokuments und deren Aufzeichnung in genau diesen beiden Dateien. Aus ihr folgt **keine** Implementierungs-, Qualifikations-, Test-, Auswertungs-, Kandidatenmanifest-, Selektions-, Staging-, Commit-, Push-, Synchronisierungs- oder Market-Run-Freigabe. Kein historischer Final-OOS-Anspruch, kein prospektiver Startzeitpunkt und keine Paper-Trading- oder Live-Kapital-Freigabe folgen aus ihr. Die zehn Dateien der fünf angenommenen Vertragspaare bleiben unverändert; sie wurden vor und nach dieser Aufzeichnung geprüft.

```json
{
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "date_utc": "2026-09-15",
  "recorded_at_utc": "2026-09-15T16:03:52Z",
  "decision": "FORMALLY_ACCEPT_REVIEWED_EVALUATOR_INTEGRATION_CONTRACT",
  "document_status": "APPROVED_FOR_ADOPTION",
  "review_recommendation": "APPROVE_FOR_FORMAL_ADOPTION",
  "review_source": "INDEPENDENT_REVIEW_REPORTED_BY_USER",
  "review_single_finding_refuted_by_targeted_source_check": true,
  "additional_full_rereview_claimed": false,
  "reviewed_markdown_sha256": "4952a5cc9be09f22b4c66bca42ff91b6dd334f5d1f935cff44e9174b3e147daf",
  "reviewed_markdown_bytes": 82484,
  "reviewed_json_sha256": "b81cfb97af0d87f4cccdc76fff794fe36f267aa90012bd4d9a39ec36e39cba6b",
  "reviewed_json_bytes": 99462,
  "accepted_decisions": "D4_THROUGH_D17",
  "technical_contract_and_calculation_rules_changed": false,
  "predecessor_documents_changed": false,
  "not_closed": [
    "D1 Nachweisverfahren fuer ausgefuehrten Bytecode und dynamische Abhaengigkeiten",
    "D2 Vollstaendigkeit der Variablengruppe B",
    "D3 Decimal-Signalflaggen vor einem getrappten Signal",
    "B1 bis B14 konkrete Bindungen, Werte bleiben null",
    "tatsaechliche Helper-Verwendung und deren Qualifikation",
    "Implementierungs-, Qualifikations-, Test-, Manifest- und Ausfuehrungsschritte"
  ],
  "deferred_unchanged": "V-19",
  "review_correction": "Das beanstandete finale Stress-Drawdown-Gate war bereits korrekt. Operativ werden neue Entries ab realized_drawdown_rate >= 0.05 in beiden Szenarien blockiert; Exits bleiben erlaubt. Das finale Stress-Gate bleibt max_drawdown <= 0.10. Einordnung allein dieses Gates: 0.099999 PASS, 0.10 PASS, 0.100001 FAIL, keine Gesamtlauffreigabe. Dies korrigiert ausschliesslich den Review, keine Vertragsregel.",
  "binding_timing_rule": "Erforderliche Bindungen und Qualifikationen muessen vor den jeweils vertraglich bestimmten Schritten erfuellt sein, insbesondere vor der Beobachtung historischer Selektionskennzahlen, nicht erst vor Live-Betrieb.",
  "implementation_authorized": false,
  "evaluation_authorized": false,
  "qualification_authorized": false,
  "test_execution_authorized": false,
  "candidate_manifest_authorized": false,
  "selection_authorized": false,
  "staging_authorized": false,
  "commit_authorized": false,
  "push_authorized": false,
  "synchronization_authorized": false,
  "market_run_authorized": false
}
```
