# LIVE DESIGN — PAPER EXECUTION ECONOMICS V1

**Kurzname:** PEE V1  
**Dokumentstatus:** DESIGN CANDIDATE — bereit zur fachlichen Prüfung, nicht implementiert  
**Datum:** 2026-08-06  
**Geltungsbereich:** Post-L1 Paper-Trading-Architektur  
**Live-Freigabe:** NEIN  
**Implementierungsfreigabe:** NEIN — dieses Dokument beschreibt den nächsten kontrollierten Implementierungspfad; jedes Umsetzungspaket benötigt ein eigenes Mandat  

---

## 1. Entscheidung und Zweck

Paper Execution Economics V1 ist das nächste klar begrenzte Arbeitspaket nach dem aktuellen L1-Stand.

Ziel ist eine konservative, deterministische und vollständig auditierbare ökonomische Simulation für Paper-Trades. Ein Trade soll nicht mehr nur als LONG/SHORT-Zustandswechsel mit nomineller Stückzahl behandelt werden. Vor einem Einstieg müssen Kapital, Risikobudget, Stop-Distanz, Positionsobergrenze und Ausführungskosten zusammenpassen. Beim Ausstieg müssen Referenzpreis, modellierter Ausführungspreis, Gebühren, Slippage, Brutto-PnL und Netto-PnL getrennt und dimensionsrichtig ausgewiesen werden.

PEE V1 soll die vorhandene L1-Entscheidungslogik nicht verbessern oder verändern. Es schafft die belastbare Ausführungs- und Abrechnungsschicht, auf der spätere Live-Daten-, Broker- und Order-Arbeit sicher aufbauen kann.

Dieses Dokument ist bewusst ein eigener Post-L1-Designschritt. Es ändert keine eingefrorene L1-Entscheidung rückwirkend und stellt keine stillschweigende Fortsetzung der L1-Freigabe dar.

---

## 2. Einordnung in das Gesamtprojekt

### 2.1 Maßgebliche Grundlagen

PEE V1 folgt insbesondere diesen bestehenden Projektquellen:

- `Master_Analysis_Blueprint.md`: langfristiges Ziel eines modularen, austauschbaren und wissenschaftlich belastbaren Trading-Systems; risikobasierte Positionsgröße; Nutzung der Workstation für rechenintensive Validierung.
- `docs/architecture/SNIPER_BOT_ARCHITECTURE_CHARTER.md`: minimale, erklärbare Architektur; klare Eigentümerschaften; explizite Schemas; keine versteckten Seiteneffekte; Komplexität muss ihren Nutzen verdienen.
- `docs/POLICIES/STRATEGY_REALISM_GUIDE_SNIPER_BOT.md`: Beurteilung nach Kosten; konservative Kostenannahmen; Turnover und wirtschaftliche Umsetzbarkeit berücksichtigen.
- `docs/POLICIES/SYSTEM_EXECUTION_GUIDE_SNIPER_BOT.md`: Trennung von Strategie, Execution, Risiko und Monitoring; realistisches Paper-Trading vor Live-Trading; Fail-safe- und Kill-Switch-Verhalten.
- `docs/POLICIES/backtest_integrity_policy.md`: explizite Positionsgröße, Gebühren, Slippage, zeitlich kausale Ausführung und reproduzierbare Ergebnisse.
- `docs/LIVE_ROBUSTNESS_ROADMAP.md`: Execution-Realismus, Paper-Live Shadow Mode, Trade-Erklärbarkeit, Konfigurations-Snapshots und unabhängige Reviews als priorisierte Grundlagen.
- `docs/LIVE_DESIGN_L1_FREEZE_AND_OPERATIONAL_GUARD.md`, `docs/LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md` und `docs/LIVE_DESIGN_L1_EXIT_AND_REVIEW_PROTOCOL.md`: L1 ist eingefroren; Architekturänderungen benötigen ein neues Mandat; eine dokumentierte L1-Live-Freigabe liegt nicht vor.

Bei Widersprüchen gelten die bestehenden Policy- und Freeze-Regeln vor diesem Designkandidaten. Vor einer Implementierung müssen Konflikte ausdrücklich entschieden werden.

### 2.2 Warum dieses Paket jetzt den größten praktischen Nutzen bringt

Der aktuelle L1-Paperpfad kann Positionen deterministisch öffnen und schließen, Zustand persistieren, Neustarts behandeln und lange CSV-Replays durchführen. Ihm fehlt jedoch eine belastbare ökonomische Bedeutung:

- `position_size=1.0` ist derzeit ein technischer Platzhalter, keine kapital- oder risikobasierte Positionsgröße.
- Die konfigurierte Roundtrip-Gebühr wird im aktiven Loop nicht an die Paper-Ausführung übergeben.
- Die bestehende Netto-PnL-Berechnung zieht einen dimensionslosen Gebührenanteil direkt von einem absoluten Geld-PnL ab.
- Slippage, per-side fees, Notional, Equity, Drawdown und tägliches Risikobudget sind nicht Teil einer zusammenhängenden Abrechnung.
- vorhandene Cost-Guards sind nicht in den aktiven Entry-Pfad eingebunden.
- allgemeine Guards werden im aktuellen Ablauf erst nach dem Ausführungsschritt bewertet.

Damit kann der aktuelle Paperpfad technische Stabilität zeigen, aber noch keine realistische Aussage über Kapitalentwicklung, Risiko oder wirtschaftliche Ausführbarkeit liefern. PEE V1 schließt genau diese Lücke, ohne bereits Exchange-, Broker- oder Echtgeld-Komplexität einzuführen.

---

## 3. Scope

### 3.1 PEE V1 muss leisten

1. Eine explizite Paper-Kontobasis mit realisierter Equity führen.
2. Vor jedem neuen Entry eine risikobasierte, begrenzte Positionsgröße berechnen.
3. Adverse Slippage auf Entry und Exit deterministisch modellieren.
4. Gebühren je Ausführungsseite aus dem ausgeführten Notional berechnen.
5. Referenz-PnL, Execution-Brutto-PnL, Slippage-Kosten und Netto-PnL getrennt ausweisen.
6. Neue Entries vor der Ausführung durch Kosten-, Kapital- und Risiko-Gates autorisieren oder mit stabilem Reason Code ablehnen.
7. Offene Positionen trotz Entry-Sperre sicher schließen können.
8. Position, Paper-Konto, Trade-Log und Audit-Log nach Neustart eindeutig abgleichen.
9. Konfiguration, Schema und Rechenmodell über stabile Identitäten reproduzierbar machen.
10. Einen Shadow-Modus für wirkungsfreie Vergleichsläufe und einen getrennten Enforced-Modus bereitstellen.

### 3.2 Ausdrücklich nicht Teil von PEE V1

- keine Änderung der bestehenden Entry-Signale, Fusion, Persistenzregeln oder Exit-Trigger;
- keine Optimierung von Strategieparametern;
- keine Verwendung der State-Research-Ergebnisse für dynamische Positionsgröße;
- keine Portfolio- oder Multi-Asset-Allokation;
- keine dynamische Hebelsteuerung;
- keine Partial Fills, Orderbuchsimulation oder stochastische Latenzmodelle;
- kein echter Live-Datenfeed;
- kein Exchange-/Broker-Adapter und keine echten Orders;
- keine API-Schlüssel oder Produktions-Credentials;
- keine automatische Freigabe für Echtgeldbetrieb;
- kein Deployment;
- keine große Framework- oder Abstraktionsschicht ohne unmittelbaren V1-Nutzen.

V1 darf bewusst einfach sein. Die Einfachheit darf jedoch nicht durch versteckte Annahmen, dimensionsfalsche Berechnungen oder nicht reproduzierbare Defaults erkauft werden.

---

## 4. Architekturprinzipien

### 4.1 Eine Quelle pro Verantwortlichkeit

- **Intent/Fusion:** entscheidet weiterhin, ob ein LONG-/SHORT-Intent vorliegt.
- **Entry Authorization:** entscheidet, ob ein neuer Paper-Entry wirtschaftlich und risikoseitig zulässig ist.
- **Paper Economics:** berechnet deterministisch Fill, Fees, Quantity und Settlement; keine Strategieentscheidung.
- **S2 Position State:** bleibt Autorität für die offene Position und deren Entry-Basis.
- **Paper Account State:** wird Autorität für realisierte Equity und kumulierte Paper-Abrechnung.
- **S4 Risk State:** bleibt Autorität für Kill-/Risk-Modus und bestehende Risikozustände.
- **Trade Log:** ist append-only Nachweis abgeschlossener Trades, nicht führender Kontostand.
- **Audit Log:** erklärt Entscheidungen und Abweichungen, ist aber keine alternative State-Quelle.

Keine Kennzahl darf parallel in mehreren Modulen unabhängig berechnet werden.

### 4.2 Reine Berechnung, kontrollierte Seiteneffekte

Die ökonomischen Kernfunktionen müssen pure functions sein: gleiche Eingaben ergeben gleiche Ausgaben; keine Datei-, Zeit-, Netzwerk- oder Environment-Zugriffe innerhalb der Berechnung.

Lesen und Schreiben von Zustand sowie Logs bleibt an den bestehenden Runtime-Grenzen. Dadurch können die Rechenregeln isoliert getestet und später auch im Backtest oder in einem Broker-Adapter wiederverwendet werden.

### 4.3 Fail closed für Entries, fail safe für Exits

- Unvollständige, ungültige oder nicht versöhnte ökonomische Daten blockieren neue Entries.
- Eine bereits offene Position muss weiterhin geschlossen werden können.
- Ein Fehler im Entry-Economics-Pfad darf keine Ersatzgröße `1.0` und keinen kostenfreien Fallback erzeugen.
- PEE V1 erzwingt bei einem Economics-Fehler keine automatische Marktliquidation. Eine solche Policy wäre ein separates Design.

### 4.4 Explizite Versionierung

Änderungen an State- oder Log-Semantik erfolgen ausschließlich über eine neue Schema-Version und version-aware Leser. Bestehende Schema-1-Daten werden weder umgedeutet noch stillschweigend überschrieben.

### 4.5 Kein Live durch Namensähnlichkeit

`live_l1` bezeichnet heute einen Live-orientierten, deterministischen Replay-/Paperpfad. PEE V1 macht daraus keinen Echtgeld-Live-Bot. `PRODUCTION` bleibt gesperrt, bis eine eigenständige Live-Execution-Architektur mit separater Freigabe existiert.

---

## 5. Zielablauf

```text
Market-/Replay-Event
        |
        v
bestehende Signal- und Intent-Logik
        |
        v
bestehende Fusion / gewünschte Aktion
        |
        +--------------------------+
        | neuer Entry              | bestehender Exit
        v                          v
Pre-Entry Authorization       Exit-Trigger unverändert
        |                          |
        v                          v
Sizing + Entry Quote          Exit Quote
        |                          |
        +------------+-------------+
                     v
              Paper Execution
                     |
                     v
                Settlement
                     |
        +------------+-------------+
        |            |             |
        v            v             v
   S2 Position   Paper Account   Trade/Audit Log
```

Wichtig: Bei einem Exit gibt es keine erneute Entry-Autorisierung. Risk- oder Cost-Gates dürfen die Reduktion einer offenen Position nicht blockieren.

---

## 6. Verbindliches Rechenmodell

### 6.1 Einheiten

Alle Felder benötigen eine eindeutige Einheit im Namen oder Schema:

- Preise: Quote Currency pro Base Unit, z. B. USDT/BTC.
- Quantity: Base Asset Units, z. B. BTC.
- Notional und PnL: Quote Currency, z. B. USDT.
- Raten: Dezimalanteil, z. B. `0.0005` für 5 Basispunkte.
- Prozentwerte in Anzeigen: nur abgeleitete Werte; intern Dezimalanteile.
- Zeit: UTC und bestehende deterministische Tick-/Event-Identität.

`fee_rate`, `fee_quote` und `pnl_quote` dürfen niemals dasselbe Feld oder dieselbe Rechenrolle teilen.

### 6.2 Slippage

Für eine Slippage-Rate `s = slippage_bps / 10_000` gilt ein konservativer, richtungsabhängiger Fill:

```text
LONG entry fill  = reference_entry_price * (1 + s_entry)
LONG exit fill   = reference_exit_price  * (1 - s_exit)

SHORT entry fill = reference_entry_price * (1 - s_entry)
SHORT exit fill  = reference_exit_price  * (1 + s_exit)
```

Die V1-Slippage ist deterministisch und konfigurationsgetrieben. Sie modelliert keine Partial Fills und keine zufällige Verteilung. Eine spätere variable Slippage muss eine neue Modellversion erhalten.

### 6.3 Gebühren

Gebühren werden pro Ausführungsseite auf den absoluten ausgeführten Notional berechnet:

```text
entry_notional_quote = abs(quantity * entry_fill_price)
exit_notional_quote  = abs(quantity * exit_fill_price)

entry_fee_quote = entry_notional_quote * entry_fee_rate
exit_fee_quote  = exit_notional_quote  * exit_fee_rate
total_fees_quote = entry_fee_quote + exit_fee_quote
```

V1 verwendet keine dimensionslose Roundtrip-Gebühr als absoluten Geldbetrag. Ein vorhandener Legacy-Wert darf nur durch einen expliziten, dokumentierten Compatibility-Parser gelesen werden; intern werden per-side rates benutzt.

### 6.4 PnL-Zerlegung

Für Quantity `q > 0`:

```text
LONG reference_pnl_quote = q * (reference_exit_price - reference_entry_price)
LONG execution_gross_pnl_quote = q * (exit_fill_price - entry_fill_price)

SHORT reference_pnl_quote = q * (reference_entry_price - reference_exit_price)
SHORT execution_gross_pnl_quote = q * (entry_fill_price - exit_fill_price)

slippage_cost_quote = reference_pnl_quote - execution_gross_pnl_quote
net_pnl_quote = execution_gross_pnl_quote - total_fees_quote
```

Slippage wird durch die modellierten Fill-Preise bereits im Execution-Brutto-PnL erfasst und darf nicht ein zweites Mal vom Netto-PnL abgezogen werden.

### 6.5 Return-Kennzahlen

Mindestens folgende Nenner sind zu unterscheiden:

```text
net_return_on_entry_notional = net_pnl_quote / entry_notional_quote
net_return_on_equity_before  = net_pnl_quote / equity_before_quote
```

Ein unspezifisches `pnl_pct` darf nicht als Kontorendite interpretiert werden. Schema V2 muss die Bedeutung jedes Return-Feldes festlegen.

---

## 7. Positionsgröße und Risiko

### 7.1 Grundsatz

Die Positionsgröße wird aus realisierter Equity und dem modellierten Verlust bis zum Stop bestimmt. Unrealisierte Gewinne erhöhen in V1 die verfügbare Equity nicht.

```text
risk_budget_quote = realized_equity_quote * risk_per_trade_rate
```

Der modellierte Verlust je Base Unit umfasst:

- adverse Entry-Slippage,
- adverse Stop-Exit-Slippage,
- Entry-Fee,
- erwartete Stop-Exit-Fee,
- Preisverlust zwischen Entry-Fill und Stop-Fill.

```text
risk_quantity = risk_budget_quote / modeled_stop_loss_per_unit_quote
notional_cap_quote = realized_equity_quote * max_position_notional_rate
notional_cap_quantity = notional_cap_quote / entry_fill_price

raw_quantity = min(risk_quantity, notional_cap_quantity)
quantity = floor_to_step(raw_quantity, quantity_step)
```

V1 verwendet maximal 1x Notional-Bezug. Ein Hebel größer als 1 ist außerhalb des Scopes.

### 7.2 Stop-Grundlage

Die bestehende fachliche Stop-Regel bleibt unverändert. PEE V1 liest den daraus folgenden Referenz-Stoppreis und verwendet ihn für die Verlustschätzung. Es entscheidet nicht, wo der Stop liegen soll.

### 7.3 Entry-Ablehnung

Ein Entry wird unter anderem abgelehnt, wenn:

- Equity, Referenzpreis, Stoppreis oder Kostenprofil fehlen bzw. ungültig sind;
- Stop-Distanz nicht positiv oder richtungswidrig ist;
- modellierter Verlust pro Einheit nicht positiv ist;
- gerundete Quantity `<= 0` ist;
- Minimum Quantity oder Minimum Notional nicht erreicht wird;
- Risikobudget oder Notional Cap nach Rundung verletzt wird;
- Account-, Position- oder Schema-Reconciliation offen ist;
- Kill-/Risk-Modus neue Entries verbietet.

Es gibt keinen automatischen Ersatzwert.

### 7.4 Noch zu genehmigende numerische Baseline

Die vorhandenen Projektdokumente nennen Orientierungswerte, aber noch kein ausreichend eindeutiges PEE-V1-Profil. Vor `ENFORCED` müssen daher ausdrücklich beschlossen und versioniert werden:

- `starting_equity_quote` und Quote Currency;
- `risk_per_trade_rate`;
- `max_position_notional_rate`;
- `entry_fee_rate` und `exit_fee_rate`;
- `entry_slippage_bps` und `exit_slippage_bps`;
- `quantity_step`, `min_quantity`, `min_notional_quote`;
- tägliche Verlust-, Gebühren- und Drawdown-Grenzen;
- Verhalten beim UTC-Tageswechsel.

Die im Master Blueprint erwähnten Größenordnungen sind Kandidaten, keine automatische Freigabe. Die aktive Baseline erhält eine stabile `economics_profile_id` und einen Hash der kanonischen Konfiguration.

---

## 8. Trigger- und Strategieparität

PEE V1 trennt fachliche Trigger von wirtschaftlicher Abrechnung:

- Die bestehenden TP-, SL-, Time-Stop- und Signal-Exit-Trigger werden weiterhin anhand des bestehenden Referenzmarktpreises und des gespeicherten Referenz-Entry-Preises bewertet.
- Der modellierte Fill-Preis verändert die Abrechnung, nicht rückwirkend den Auslöser.
- Ein Enforced-Entry kann wegen Risiko oder Kosten ausfallen oder eine andere Quantity erhalten. Das ist eine beabsichtigte Execution-Entscheidung, keine Signaländerung.
- PEE V1 darf keine zusätzliche LONG-/SHORT-Meinung und keinen neuen Exit-Trigger erzeugen.

Diese Grenze ermöglicht einen aussagekräftigen Shadow-Vergleich: Intent- und Exit-Trigger-Parität müssen messbar bleiben, während Economics-Ergebnisse separat beobachtet werden.

---

## 9. Betriebsmodi

### 9.1 `OFF`

PEE V1 ist deaktiviert. Dieser Modus dient nur der kontrollierten Kompatibilität während der Einführung und darf nicht als ökonomisch realistischer Paperbetrieb bezeichnet werden.

### 9.2 `SHADOW`

- Economics Quote, Entry Authorization und hypothetisches Settlement werden berechnet und geloggt.
- Bestehende Positionseröffnung, Quantity und Abschlusslogik werden nicht beeinflusst.
- Abweichungen zwischen Legacy-Aktion und PEE-Entscheidung werden mit Reason Codes protokolliert.
- Shadow-Daten dürfen nicht als tatsächlich geführtes Paper-Konto interpretiert werden.

### 9.3 `ENFORCED`

- Entry Authorization, risikobasierte Quantity, modellierte Fills, Gebühren und Paper-Konto sind aktiv.
- Ungültige Economics blockieren neue Entries.
- Exits offener Positionen bleiben möglich.
- Aktivierung erfordert ein genehmigtes Profil, abgeschlossene Shadow-Abnahme und eine explizite Umsetzungs-/Betriebsfreigabe.

Es gibt keine automatische Promotion von `SHADOW` zu `ENFORCED`.

---

## 10. Guards und stabile Reason Codes

### 10.1 Reihenfolge vor einem Entry

Die Entry-Prüfung erfolgt vor jeder Zustandsänderung in fester Reihenfolge:

1. Modus und Konfiguration gültig;
2. Konfigurations- und Schema-Identität kompatibel;
3. Position/Account/Logs versöhnt;
4. bestehender Kill-/Risk-Modus erlaubt neue Entries;
5. Equity und Tageszustand gültig;
6. Drawdown-/Daily-Loss-Grenze nicht verletzt;
7. Kosten-/Fee-Budget nicht verletzt;
8. bestehende Rate-/Cooldown-/Gate-Regeln erfüllt;
9. Quantity und Notional gültig;
10. finaler Entry-Authorization-Entscheid.

Nach der Freigabe dürfen dieselben Guards nicht mit abweichender Logik erneut berechnet werden.

### 10.2 Reason-Code-Familien

Mindestens folgende stabilen Familien werden vorgesehen:

- `PEE_CONFIG_*`
- `PEE_SCHEMA_*`
- `PEE_RECONCILIATION_*`
- `PEE_ACCOUNT_*`
- `PEE_RISK_*`
- `PEE_COST_*`
- `PEE_QUANTITY_*`
- `PEE_AUTHORIZED`

Reason Codes sind maschinenlesbar und stabil. Freitext darf ergänzen, aber nicht die einzige Erklärung sein.

### 10.3 Risk-Modi

Für PEE V1 gilt:

- Risk-/Kill-Modi, die Entries sperren, verhindern jede neue Positionserhöhung.
- Sie blockieren keine Positionsreduktion.
- Automatische Zwangsliquidation ist nicht Bestandteil dieses Designs.
- Eine Freigabe aus einem Sperrmodus erfolgt nicht automatisch durch einen profitablen Tick oder Neustart.

---

## 11. Datenverträge

Die konkreten Python-Typen dürfen an bestehende Konventionen angepasst werden. Inhaltlich werden folgende Verträge benötigt.

### 11.1 `PaperEconomicsConfig`

- `schema_version`
- `economics_model_version`
- `economics_profile_id`
- `quote_currency`
- `starting_equity_quote`
- `risk_per_trade_rate`
- `max_position_notional_rate`
- `entry_fee_rate`
- `exit_fee_rate`
- `entry_slippage_bps`
- `exit_slippage_bps`
- `quantity_step`
- `min_quantity`
- `min_notional_quote`
- tägliche Loss-/Fee-Grenzen
- Drawdown-Grenze
- kanonischer `config_fingerprint`

### 11.2 `EntryEconomicsQuote`

- Richtung und Referenzzeit/-tick
- Referenz-Entry- und Referenz-Stoppreis
- modellierter Entry-Fill und Stop-Fill
- Equity vor Entry und Risikobudget
- modellierter Stopverlust je Einheit
- Risk Quantity, Cap Quantity, finale gerundete Quantity
- Entry Notional und erwartete Entry-/Stop-Fees
- erwarteter maximaler modellierter Verlust am Stop
- Profil-, Modell- und Config-Identität

### 11.3 `EntryAuthorization`

- `allowed: bool`
- finale Quantity, wenn erlaubt
- primärer Reason Code
- geordnete Liste aller Befunde
- Economics Quote oder expliziter Fehlerzustand
- deterministische Entscheidungsidentität

### 11.4 `TradeSettlement`

- Trade-/Position-Identität
- Richtung und Quantity
- Referenz-Entry/-Exit
- modellierter Entry-/Exit-Fill
- Entry-/Exit-Notional
- Entry-/Exit-Fee
- Referenz-PnL
- Execution-Brutto-PnL
- Slippage-Kosten
- Netto-PnL
- Notional- und Equity-Rendite
- Equity vor/nach Abschluss
- Peak Equity und Drawdown nach Abschluss
- Exit-Grund sowie Profil-/Config-/Modell-Identität

Alle Geldwerte müssen einheitlich als Quote-Currency-Werte und mit einer festgelegten Decimal-/Rundungsstrategie verarbeitet werden. Binäre Float-Arithmetik ohne definierte Rundungsgrenze darf nicht stillschweigend zur Kontobuchführung werden.

---

## 12. State-Modell und Recovery

### 12.1 S2 Position State V2

S2 bleibt die Quelle für die offene Position. Für eine PEE-Position benötigt Schema V2 mindestens:

- `trade_id` bzw. stabile Position-ID;
- `side`;
- `reference_entry_price`;
- `modeled_entry_fill_price`;
- `quantity`;
- `entry_notional_quote`;
- `entry_fee_quote`;
- `risk_budget_quote`;
- `modeled_stop_loss_quote`;
- `economics_profile_id` und `config_fingerprint`;
- Entry-Zeit und Entry-Tick;
- Referenz-Stopgrundlage.

Das vorhandene fachliche `entry_price` bleibt während der Migration eindeutig als Referenzpreis definiert. Ein Leser darf es nicht ohne Schema-Prüfung als Fill-Preis interpretieren.

### 12.2 Paper Account State V1

Ein einzelner neuer, atomar persistierter Paper-Account-State führt ausschließlich realisierte Kontowerte:

- `account_schema_version`;
- `account_id` und Quote Currency;
- `starting_equity_quote`;
- `realized_equity_quote`;
- `cumulative_net_pnl_quote`;
- `peak_realized_equity_quote`;
- `realized_drawdown_quote` und `realized_drawdown_rate`;
- UTC-Tagesidentität;
- `daily_net_pnl_quote` und `daily_fees_quote`;
- Anzahl abgeschlossener Trades;
- `last_settled_trade_id`;
- Profil-/Config-Identität;
- letzte Update-Event-Identität.

Unrealisierte PnL wird in V1 nicht in `realized_equity_quote` eingebucht.

### 12.3 Atomare Abschlussreihenfolge

Ein Trade-Abschluss benötigt einen deterministischen Settlement-Datensatz und eine idempotente Commit-Strategie. Zielzustand nach Recovery:

- jeder `trade_id` höchstens einmal im Konto verbucht;
- abgeschlossener Trade im Trade-Log vorhanden;
- Account `last_settled_trade_id` stimmt mit der verbuchten Reihenfolge überein;
- S2 ist FLAT oder enthält eine eindeutig andere, spätere Position;
- erneutes Verarbeiten desselben Events verdoppelt weder PnL noch Gebühren.

Die konkrete Write-Ahead-/Journal-Technik wird in Umsetzungspaket IU-2 festgelegt und getestet. Neue ad-hoc-Dateien ohne klare Recovery-Rolle sind unzulässig.

### 12.4 Legacy- und Fehlerfälle

- Schema-1-Zustände werden von einem expliziten, getesteten Kompatibilitätsleser erkannt.
- Eine offene Legacy-Position ohne Economics-Basis darf geschlossen werden.
- Für fehlende ökonomische Werte darf kein scheinpräziser Netto-PnL erfunden werden; der Abschluss wird als `economics_incomplete` markiert und neue Entries bleiben bis zur Reconciliation gesperrt.
- Eine automatische rückwirkende Neubewertung alter Trades ist nicht Teil von V1.
- Nicht unterstützte neuere Schemas führen zu Entry-Sperre, nicht zu stiller Normalisierung.

---

## 13. Trade- und Audit-Log Schema V2

Das neue Trade-Schema enthält mindestens:

- `schema_version`, `trade_id`, Strategy-/Git-/Config-Identitäten;
- Richtung, Entry-/Exit-Zeit und -Tick, Dauer, Exit-Grund;
- Quantity;
- Referenz-Entry/-Exit und modellierter Entry-/Exit-Fill;
- Entry-/Exit-Notional;
- Entry-/Exit-Fee und Total Fees;
- `reference_pnl_quote`;
- `execution_gross_pnl_quote`;
- `slippage_cost_quote`;
- `net_pnl_quote`;
- `net_return_on_entry_notional`;
- `net_return_on_equity_before`;
- Equity vor/nach Settlement, Peak und Drawdown;
- Risikobudget und modellierter Stopverlust beim Entry;
- `economics_profile_id`, Modellversion und Config Fingerprint;
- Economics-Vollständigkeitsstatus.

Schema V2 darf die vorhandenen Felder `pnl`, `pnl_pct`, `fee_roundtrip`, `pnl_net` und `pnl_pct_net` nicht stillschweigend neu interpretieren. Die Implementierung muss entweder:

1. V1- und V2-Zeilen mit versionsabhängiger Semantik lesen und die alten Namen in V2 klar als Kompatibilitätsfelder definieren, oder
2. ausschließlich neue eindeutige V2-Felder schreiben und alle Verbraucher version-aware aktualisieren.

Die Entscheidung fällt in IU-2 anhand der vorhandenen Verbraucher. Bevorzugt wird Variante 2, wenn keine zwingende Abwärtskompatibilität entgegensteht.

Audit-Events erfassen zusätzlich Autorisierungen, Ablehnungen, Reconciliation-Befunde, Moduswechsel und Konfigurationsabweichungen. Trade- und Audit-Log erfüllen unterschiedliche Rollen und werden nicht vermischt.

---

## 14. Konfiguration und Identität

### 14.1 Keine versteckten Produktionsdefaults

Im `ENFORCED`-Modus müssen alle kapital-, kosten- und risikorelevanten Werte aus einem genehmigten Profil stammen. Fehlende Werte verhindern den Start bzw. neue Entries. Nullkosten sind nur erlaubt, wenn ein ausdrücklich als Testprofil gekennzeichnetes Profil dies festlegt.

### 14.2 Kanonischer Fingerprint

Aus allen semantisch relevanten Economics-Feldern wird in stabiler Sortierung ein Fingerprint gebildet. Er wird in State, Trade-Log, Audit-Log und Run-Manifest gespeichert.

Ein Neustart mit offener Position und abweichendem Fingerprint darf nicht unbemerkt fortgesetzt werden. Exits bleiben möglich; neue Entries bleiben gesperrt, bis die Abweichung entschieden ist.

### 14.3 Schema-Unterstützung pro Artefakt

Die derzeit globale Betrachtung weniger Schema-Nummern reicht für eine Architekturentwicklung nicht aus. Unterstützte Versionen werden pro Artefakt festgelegt, zum Beispiel:

- S2 Position State;
- S4 Risk State;
- Paper Account State;
- Trade Log;
- Audit Event;
- Economics Config.

Gleiche Versionsnummern verschiedener Artefakte müssen nicht dieselbe Bedeutung haben.

---

## 15. Minimaler geplanter Code-Schnitt

### 15.1 Neue Verantwortlichkeiten

Voraussichtlich werden nur zwei kleine neue Kernbereiche benötigt:

- `live_l1/core/paper_economics.py`: pure Berechnungen und Datenverträge für Fill, Fees, Sizing, Authorization und Settlement.
- ein klar benanntes Paper-Account-State-Modul unter `live_l1/state/`: Laden, Validieren, atomisches Persistieren und Reconciliation des Kontos.

Die endgültigen Dateinamen werden vor IU-1 gegen vorhandene Namenskonventionen geprüft. Es wird kein generisches Framework und kein Plugin-System für diese V1 eingeführt.

### 15.2 Erwartete Integrationspunkte

Gezielte Änderungen werden voraussichtlich benötigt in:

- `live_l1/core/loop.py`: Pre-Entry Authorization vor Execution, Modusführung und Übergabe vollständiger Economics-Daten;
- `live_l1/core/execution.py`: Nutzung eines vorberechneten Quotes/Settlements statt eigener Gebührenlogik;
- `live_l1/guards/cost_guards.py`: entweder eindeutige Integration in die neue Autorisierung oder kontrollierte Ablösung nach Verbraucherprüfung;
- `live_l1/state/models.py`, `state_store.py` und `state_validation.py`: versionierte S2-/Account-Verträge;
- Schema-, Recovery-, Replay- und Validierungswerkzeuge, soweit sie die geänderten Artefakte lesen;
- fokussierte Tests unter der bestehenden Teststruktur.

### 15.3 Unberührte Bereiche

PEE V1 ändert nicht:

- bestehende Strategie- und Signaldefinitionen;
- Fusion und fachliche Intent-Erzeugung;
- Research-Pipelines einschließlich RCC002;
- `engine`-Backtestlogik;
- `run_engine`-Trockenlaufarchitektur;
- Produktionsfreigabe oder Exchange-Anbindung.

---

## 16. Umsetzung in einzeln abnehmbaren Paketen

### IU-1 — Pure Economics Core

**Inhalt:** Datenverträge, Rundungsstrategie, Fill-, Fee-, PnL- und Sizing-Funktionen sowie fokussierte Unit-Tests.  
**Keine Runtime-Integration.**

Abnahme:

- LONG-/SHORT-Symmetrie ist nachweisbar;
- Einheiten und Vorzeichen sind korrekt;
- Slippage wird genau einmal berücksichtigt;
- Gebühren skalieren mit ausgeführtem Notional;
- Quantity verletzt nach Rundung weder Risiko- noch Notional-Cap;
- ungültige Eingaben liefern explizite Fehler/Reason Codes statt Fallbacks.

### IU-2 — Schema, Account State und Recovery

**Inhalt:** S2 V2, Paper Account State, Trade-Schema V2, version-aware Leser und idempotente Settlement-/Recovery-Regeln.  
**Noch keine Enforced-Entries.**

Abnahme:

- Legacy-State wird eindeutig erkannt;
- künstlich unterbrochene Settlement-Schritte verdoppeln keine Buchung;
- unbekannte Schemas sperren Entries;
- offene Legacy-Position bleibt exitfähig;
- pro Artefakt ist die unterstützte Version explizit.

### IU-3 — Shadow-Integration

**Inhalt:** PEE-Berechnung im aktiven Loop ohne Wirkung auf Legacy-Aktionen; Differenz- und Audit-Logging.  
**Keine Änderung der tatsächlich ausgeführten Paper-Quantity.**

Abnahme:

- bestehende Intent-, Entry- und Exit-Trigger bleiben im Shadow-Vergleich identisch;
- jeder hypothetische Entry hat Quote oder stabilen Ablehnungsgrund;
- kein Shadow-Ergebnis verändert S2/S4 oder das Legacy-Trade-Ergebnis;
- Config Fingerprint und Modellversion sind in jedem Shadow-Datensatz vorhanden.

### IU-4 — Enforced Paper Economics

**Inhalt:** genehmigtes Profil, Pre-Entry Authorization, risikobasierte Quantity, modellierte Fills, Gebühren, Settlement und Paper Account.  
**Weiterhin CSV-/Paperbetrieb, keine Exchange.**

Abnahme:

- keine feste Fallback-Quantity;
- Guard-Reihenfolge liegt vor der Positionseröffnung;
- gesperrte Entries verändern weder Position noch Konto;
- Exits bleiben unter Entry-Sperre möglich;
- Konto, Position und Trade-Log stimmen nach Neustart überein;
- Netto-PnL lässt sich aus Logfeldern vollständig nachrechnen.

### IU-5 — Workstation-Validierung

**Inhalt:** gestufte, reproduzierbare Replay- und Recovery-Validierung auf der CPU-Workstation.  
**Keine Strategieoptimierung.**

Abnahme:

- kleine Smoke-/Invariant-Tests wurden vor langen Läufen bestanden;
- mindestens ein sinnvoller Lauf ab 200.000 Events/Ticks je freigegebenem Szenario;
- anschließend vollständiger historischer L1-Lauf, sofern Datensatz und Mandat vorliegen;
- mehrere deterministische Offsets/Startpunkte und Neustart-Szenarien;
- Run-Manifest mit Git-Identität, Dataset-Hash, Config Fingerprint, Befehl, Zeit und Output-Hashes;
- Ergebnisse werden archiviert, ohne Rohdaten oder große Outputs unkontrolliert ins Git-Repository aufzunehmen.

### IU-6 — Unabhängige Prüfung und Abschlussentscheidung

**Inhalt:** getrennte Read-only-Reviews des exakt gleichen Stands durch mindestens zwei unabhängige Reviewer sowie menschliche Abschlussentscheidung.

Vorgesehener Workflow:

1. Codex implementiert und liefert Scope, Diff, Tests, Manifeste und bekannte Grenzen.
2. Claude prüft unabhängig Rechenmodell, Risiko, Recovery und Policy-Konformität.
3. Antigravity prüft unabhängig Architektur, unnötige Komplexität, Testlücken und Live-Risiken.
4. Findings werden mit Schweregrad, Datei/Zeile, Begründung und Reproduktionsweg konsolidiert.
5. Korrekturen erzeugen eine neue eindeutige Code-/Evidence-Identität und werden erneut geprüft.
6. Der Implementierer zertifiziert seinen eigenen Stand nicht allein.

Abnahme ist genau eine dokumentierte Entscheidung:

- `PEE_V1_PAPER_FREIGEGEBEN`,
- `PEE_V1_NACHARBEIT`, oder
- `PEE_V1_GESTOPPT`.

Diese Entscheidung ist keine Echtgeld-Live-Freigabe.

---

## 17. Test- und Evidenzstandard für die spätere Umsetzung

### 17.1 Unit- und Invariant-Tests

Mindestens:

- Nullbewegung mit Kosten ergibt negativen Netto-PnL;
- Nullkosten/Nullslippage ergibt Execution-PnL gleich Referenz-PnL;
- höhere Fees oder Slippage verbessern niemals den Netto-PnL;
- LONG und SHORT liefern bei gespiegelten Preisen symmetrische Ergebnisse;
- Fee-Beträge sind bei gleicher Rate proportional zum Notional;
- Risk Quantity sinkt bei größerer Stop-Distanz oder höheren Kosten;
- Notional Cap und 1x-Grenze werden eingehalten;
- Rundung kann Risiko nie nach oben verletzen;
- Division durch null, NaN, Infinity und negative Werte werden abgelehnt;
- derselbe Settlement-Vorgang ist idempotent.

### 17.2 Integrations- und Recovery-Tests

Mindestens:

- Entry erlaubt / Entry abgelehnt;
- Exit bei Entry-Sperre;
- Neustart mit offener PEE-Position;
- Neustart während jeder kritischen Settlement-Phase;
- Config-Wechsel mit offener Position;
- unbekannte State-/Log-Version;
- Legacy-Position ohne Economics-Basis;
- UTC-Tageswechsel;
- Kill-/Risk-Modus vor Entry;
- Replay desselben Events ohne Doppelbuchung.

### 17.3 Shadow-Parität

Shadow-Abnahme vergleicht mindestens:

- Anzahl und Identität fachlicher Entry-Intents;
- Anzahl und Identität fachlicher Exit-Trigger;
- Positionstransitionen des Legacy-Pfads;
- hypothetische PEE-Autorisierungen und Ablehnungsgründe;
- wirtschaftliche Differenz zwischen Referenz- und Execution-PnL.

Eine Abweichung der Strategieentscheidung ist ein Fehler oder benötigt ein neues Designmandat.

### 17.4 Aussagegrenzen

PEE-V1-Läufe prüfen Execution Economics und Betriebsinvarianten. Sie beweisen keine zukünftige Profitabilität und ersetzen weder Walk-Forward- noch Regime-, Monte-Carlo- oder Live-Shadow-Validierung auf echten Marktdaten.

---

## 18. Nutzung der CPU-Workstation

Die Workstation soll gezielt die teuren, reproduzierbaren Validierungsschritte übernehmen:

- lange deterministische Replays;
- mehrere Startpunkte und Kostenprofile;
- Recovery-/Fault-Injection-Matrizen;
- Erzeugung abgeleiteter, manifestierter Analyse-Datensätze;
- spätere Walk-Forward-, Regime- und Robustheitsläufe.

Die Aufgabenteilung bleibt klar:

- Das Repository definiert Code, kleine Tests, Run-Spezifikation, Schema und Manifestformat.
- Die Workstation führt genehmigte lange Läufe aus.
- Jeder Lauf bindet Git-Identität, Dataset-Hash und Config Fingerprint.
- Große Rohdaten und Resultate liegen in dafür vorgesehenen Daten-/Archivbereichen, nicht ungeprüft im Quellcode-Commit.
- Ergebnisse werden erst nach Vollständigkeits- und Hashprüfung als Evidenz akzeptiert.
- API-Schlüssel und Live-Credentials werden nicht Bestandteil von Datensätzen oder Run-Manifests.

Hohe CPU-Auslastung ist kein Selbstzweck. Ein Lauf wird nur gestartet, wenn er eine vorher formulierte Frage, Abnahmebedingung oder Unsicherheit adressiert.

---

## 19. Minimalismus und Umgang mit Altlasten

PEE V1 folgt diesen Regeln:

1. Eine Economics-Formel existiert nur einmal im Kernmodul.
2. Bestehende Cost-Guard-Helfer werden entweder vollständig integriert oder nach nachgewiesener Verbraucherfreiheit in einem eigenen Schritt entfernt; keine parallelen Wahrheiten.
3. Compatibility-Code erhält einen klaren Zweck, unterstützte Eingangsversionen und eine dokumentierte spätere Entfernungsschwelle.
4. Keine abstrakte Broker-Schnittstelle, solange PEE V1 keinen Broker verwendet.
5. Keine dynamische Modellwahl, kein State-Research-Sizing und keine Portfolio-Engine in diesem Paket.
6. Keine kosmetische Großrefaktorierung während der funktionalen Einführung.
7. Nach einem strukturellen Refactoring folgt zuerst Stabilitätsnachweis, bevor neue Funktion hinzukommt.
8. Neue Dateien und Felder müssen eine eindeutige Eigentümerschaft und einen nachweisbaren Verbraucher besitzen.

---

## 20. Offene Entscheidungen vor IU-4

Folgende Punkte sind absichtlich nicht durch Annahmen geschlossen:

1. genehmigtes Kapital-, Risiko- und Kostenprofil mit konkreten Zahlen;
2. Quote Currency und Markt-/Instrumentannahmen der ersten V1;
3. Decimal- und Rundungsstrategie passend zur späteren Zielbörse;
4. genaue tägliche Loss-/Fee-/Drawdown-Grenzen und Reset-Semantik;
5. endgültige Trade-Log-V2-Kompatibilitätsvariante nach Verbraucherprüfung;
6. konkrete idempotente Settlement-/Journal-Technik nach kleinem Failure-Mode-Design;
7. Speicherort und Lifecycle großer Workstation-Artefakte;
8. eindeutiges neues Mandat für jede Implementierungseinheit.

IU-1 und IU-2 dürfen diese Punkte technisch vorbereiten, aber keine fachlichen Grenzwerte als angebliche Projektentscheidung festschreiben.

---

## 21. Definition of Done für PEE V1

PEE V1 ist erst abgeschlossen, wenn alle folgenden Bedingungen erfüllt sind:

- IU-1 bis IU-6 sind einzeln dokumentiert und abgenommen;
- ein genehmigtes, versioniertes Economics-Profil existiert;
- Shadow-Parität der Strategie-/Triggerlogik ist belegt;
- Enforced Paper Entries verwenden ausschließlich autorisierte risikobasierte Quantity;
- Gebühren, Slippage und Netto-PnL sind dimensionsrichtig und vollständig nachrechenbar;
- State, Account und Logs überstehen definierte Neustart-/Unterbrechungsszenarien ohne Doppelbuchung;
- Entries fail closed, Exits bleiben fail safe möglich;
- lange Workstation-Läufe besitzen vollständige Manifeste und überprüfte Artefakte;
- unabhängige Reviews sind auf dieselbe eindeutige Code-/Evidence-Version bezogen;
- kritische und hohe Findings sind geschlossen oder führen zu `NACHARBEIT`/`GESTOPPT`;
- bekannte Grenzen und Restunsicherheiten sind dokumentiert;
- `PRODUCTION` und echte Orders bleiben unverändert gesperrt.

---

## 22. Weg von PEE V1 zum ersten Live-Betrieb

PEE V1 ist ein notwendiger, aber nicht hinreichender Schritt zum Live-Bot. Nach einer Paper-Freigabe bleiben mindestens getrennte Meilensteine:

1. stabiler echter Markt-Datenfeed mit Reconnect, Stale-Data- und Zeitkontrollen;
2. Paper-Live Shadow Mode auf Echtzeitdaten über einen ausreichend langen Zeitraum;
3. versionierter Order-/Broker-Adapter mit Idempotenz, Rejection-, Partial-Fill- und Reconciliation-Verhalten;
4. Live-Position-/Balance-Abgleich mit der Exchange als externer Wahrheit;
5. Credential-, Secret-, Berechtigungs- und Notfallkonzept;
6. Live-Monitoring, Incident Logging, Alarmierung und manuell getesteter Kill-Prozess;
7. kleinstmögliche Kapitalstufe mit eigener formaler Freigabe und harten Limits.

Keiner dieser Schritte darf aus einer erfolgreichen PEE-V1-Abnahme automatisch abgeleitet werden.

---

## 23. Empfohlene unmittelbare Reihenfolge

1. Dieses Design fachlich prüfen und offene Einheiten-/Profilfragen kommentieren.
2. Ein eigenes Mandat ausschließlich für **IU-1 — Pure Economics Core** erteilen.
3. IU-1 implementieren und mit kleinen, schnellen Tests abnehmen.
4. Erst danach IU-2 mandatieren.
5. Shadow- und Enforced-Integration strikt getrennt halten.
6. Lange Workstation-Läufe erst nach bestandenen kleinen Tests und festem Run-Manifest starten.
7. Claude und Antigravity erst auf eine eindeutige, unveränderte Review-Basis ansetzen.

Damit bleibt der Weg zum ersten Live-Betrieb zügig, ohne mehrere nicht verifizierte Architekturänderungen gleichzeitig aufzubauen.

---

## 24. Aktueller Freigabestand

Mit Erstellung dieses Dokuments gilt ausschließlich:

- Das Design von Paper Execution Economics V1 ist als prüfbarer Kandidat dokumentiert.
- Der vorhandene Runtime-Code wurde dadurch nicht geändert.
- Es wurden keine Tests, Datensätze, Trading-Läufe oder Deployments ausgeführt.
- Es wurde keine Implementierung, kein Paper-Enforced-Betrieb und kein Live-Betrieb freigegeben.

**Nächste erforderliche Entscheidung:** fachliche Annahme oder Korrektur dieses Designs; danach ein eng begrenztes Implementierungsmandat nur für IU-1.
