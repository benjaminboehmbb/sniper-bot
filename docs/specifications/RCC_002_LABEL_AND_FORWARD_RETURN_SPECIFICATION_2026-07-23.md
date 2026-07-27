# RCC-002 Label and Forward Return Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-LF |
| Titel | Label and Forward Return Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Version | 0.4.1 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.5.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.4.2; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version 0.5.1 |
| Geltungsbereich | S7_LABELS der RCC-002-Datenpipeline |
| Referenziert durch | Strategieevaluation; ML-Datensätze; Counterfactual Gate Evaluation; Walk-Forward- und Robustheitsanalysen |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs, Horizonte und mathematische Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Return-, Excursion-, Direction- und Barrier-Familien vollständig |
| Zeitindexprüfung | Bestanden | Entry-, Exit-, Horizont- und Verfügbarkeitszeitpunkte eindeutig |
| Long-/Short-Vorzeichenprüfung | Bestanden | Positive Werte bedeuten in beiden Richtungen Gewinn |
| Leakage-Prüfung | Bestanden | S7-Felder technisch und semantisch von S0–S6 getrennt |
| Lücken- und Tail-Prüfung | Bestanden | Gap Crossing und unvollständige Zukunftshorizonte ungültig |
| Kostenprüfung | Bestanden | Brutto- und Kostenproxy getrennt; Projektbaseline versioniert |
| Intrabar-Prüfung | Bestanden | Gleichzeitige TP-/SL-Berührung als mehrdeutig markiert |
| Split-Prüfung | Bestanden | Purging und Embargo für überlappende Horizonte definiert |
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-B02`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert `SCR-005-M01` und materialisiert `AIR-005-H01`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert die ausschließlich zukunftsbezogene S7-Stufe der
RCC-002-Datenpipeline.

S7 erzeugt:

- deskriptive Forward Returns,
- ausführungsnahe Return-Proxys,
- getrennte Long-/Short-Ergebnisse,
- Maximum Favorable Excursion und Maximum Adverse Excursion,
- diskrete Richtungslabels,
- optionale Barrier-Labels,
- Label-Gültigkeit und Verfügbarkeitszeitpunkte.

S7 darf keine vorgelagerten Features, Signale, Regime oder Gates verändern.

## 2. Zentrale Sicherheitsgrenze

### 2.1 Einzige zukunftsberechnende Stufe

S7 ist die einzige reguläre RCC-002-Stufe, die Werte nach Zeitpunkt `t`
zur Berechnung einer Zeile `t` verwenden darf.

### 2.2 Verbotene Verwendung

S7-Felder dürfen nicht als Input verwendet werden für:

- S0 bis S6,
- Live- oder Paper-Trading-Entscheidungen,
- Indikatoren,
- Signaltransformationen,
- Regime,
- Gates,
- Feature-Normalisierung,
- Auswahl eines Entry-Signals zum selben historischen Zeitpunkt.

### 2.3 Technische Isolation

S7-Felder müssen:

- eigene Präfixe besitzen,
- in einem registrierten S7-Schema liegen,
- durch S8-Allowlist aus Live-/Paper-Views ausgeschlossen werden,
- bei Schema-Verletzung den Build fail-closed abbrechen.

## 3. Normative Zeitsemantik

### 3.1 Signalzeitpunkt

Zeile `t` beschreibt den Zustand nach dem vollständigen Schluss der Kerze `t`.

### 3.2 Deskriptive Preisreferenz

Close-to-Close-Returns verwenden:

- Startpreis `C_t`,
- Endpreis `C_(t+h)`.

Sie beschreiben Marktbewegung, nicht unmittelbar ausführbare Strategie-PnL.

### 3.3 Ausführungsnahe Preisreferenz

Next-Open-to-Close-Returns verwenden:

- Entry-Preisproxy `O_(t+1)`,
- Exit-Preisproxy `C_(t+h)`.

Für `h = 1`:

- Entry `O_(t+1)`,
- Exit `C_(t+1)`.

### 3.4 Horizont

`h` bezeichnet die Anzahl 1-Minuten-Intervalle nach der Signalkerze.

Der Horizon-Endpunkt ist:

`t + h`

### 3.5 Label-Verfügbarkeit

Ein Label mit Horizont `h` ist frühestens verfügbar, nachdem Kerze `t+h`
vollständig geschlossen und validiert wurde.

Mindestfeld:

`label_available_at_h = close_time_(t+h)`

Ein Trainings- oder Evaluationsprozess darf das Label vorher nicht als bekannt
behandeln.

## 4. Horizon-Registry

### 4.1 Kanonische Horizonte

Das allein verbindliche Register lautet:

```text
horizon_registry_id=RCC002_FORWARD_HORIZONS_V1
horizon_registry_version=1.0.0
```

Es enthält:

| ID | Minuten | Fachlicher Kontext |
|---|---:|---|
| `H001` | 1 | unmittelbar nächste Kerze |
| `H005` | 5 | sehr kurzfristig |
| `H015` | 15 | kurzfristig |
| `H060` | 60 | eine Stunde |
| `H240` | 240 | vier Stunden |
| `H1440` | 1.440 | ein Tag |

Die zugehörigen Suffixe lauten exakt:

| Horizon-ID | Feldsuffix |
|---|---|
| `H001` | `_h001` |
| `H005` | `_h005` |
| `H015` | `_h015` |
| `H060` | `_h060` |
| `H240` | `_h240` |
| `H1440` | `_h1440` |

Ein 30-Minuten-Horizont gehört nicht zu Version `1.0.0`.

### 4.2 Erweiterung

Weitere Horizonte benötigen:

- registrierte Horizon-ID,
- exakte Intervalldefinition,
- neue Horizon-Registry-Version,
- aktualisierte Schema- und Labelprofilversion,
- Tests,
- erneuten Scientific Consistency Review,
- erneuten Architecture Integrity Review,
- dokumentierte Rebuild-Auswirkung.

### 4.3 Kein implizites Resampling

Ein Horizont von 60 Minuten bedeutet nicht automatisch eine 1h-OHLC-Kerze.

Er bezeichnet in dieser Spezifikation 60 aufeinanderfolgende 1-Minuten-
Intervalle auf der kanonischen 1m-Zeitachse.

## 5. Eingabevertrag

### 5.1 Eingangsschema

S7 akzeptiert ausschließlich:

```text
rcc002.stage.s6-gates/1.0.0
```

Eine unbekannte oder inkompatible Major-Version ist fail-closed abzulehnen.
Eine kompatible Minor-Version darf nur über eine registrierte
Kompatibilitätsregel akzeptiert werden.

S7 erzeugt:

```text
rcc002.stage.s7-labels/1.0.0
```

### 5.2 Pflichtfelder

S7 konsumiert aus dem S6-Eingang mindestens:

| Feld | Logischer Typ | Eigentümerstufe | Verwendung in S7 |
|---|---|---|---|
| `market_type` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Marktidentität |
| `symbol` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Marktidentität |
| `interval` | `Utf8` | `S1_NORMALIZED` | Primärschlüssel und Horizon-Interpretation |
| `open_time` | UTC-Timestamp in Millisekunden | `S1_NORMALIZED` | Primärschlüssel und Signalzeitpunkt |
| `close_time` | UTC-Timestamp in Millisekunden | `S1_NORMALIZED` | Verfügbarkeitszeitpunkt der Signalkerze |
| `open` | `Float64` | `S1_NORMALIZED` | Next-Open-Entry und Barrier-Suche |
| `high` | `Float64` | `S1_NORMALIZED` | MFE und Barrier-Suche |
| `low` | `Float64` | `S1_NORMALIZED` | MAE und Barrier-Suche |
| `close` | `Float64` | `S1_NORMALIZED` | Close-to-Close und Horizon-Exit |
| `market_segment_id` | `Utf8` | `S2_VALIDATED` | verbindliche Grenze jedes Zukunftsfensters |
| `quality_is_observed` | `Boolean` | `S2_VALIDATED` | Ausschluss nicht beobachteter Bars |
| `quality_is_synthetic` | `Boolean` | `S2_VALIDATED` | Ausschluss synthetischer Bars |
| `quality_timestamp_valid` | `Boolean` | `S2_VALIDATED` | Zeitachsenvalidität |
| `quality_ohlc_valid` | `Boolean` | `S2_VALIDATED` | OHLC-Gültigkeit |
| `quality_market_values_valid` | `Boolean` | `S2_VALIDATED` | Marktwertgültigkeit |
| `quality_gate_pass` | `Boolean` | `S2_VALIDATED` | kanonische Datenfreigabe |
| `quality_reason_codes` | geordnete Liste `Utf8` | `S2_VALIDATED` | Lineage und Invaliditätsdiagnose |
| `quality_rule_version` | `Utf8` | `S2_VALIDATED` | verwendetes Qualitätsregelwerk |
| `gate_schema_id` | `Utf8` | `S6_GATES` | Eingangsschemaidentität |
| `gate_schema_version` | `Utf8` | `S6_GATES` | Eingangsschemaversion |
| `gate_schema_ref` | `Utf8` | `S6_GATES` | Qualifizierte Eingangsschemareferenz |

Der vollständige Eingang bleibt das registrierte S6-Schema. Die Tabelle
benennt die S7-fachlich benötigte Teilmenge und erlaubt nicht, den übrigen
S6-Vertrag zu entfernen oder umzudeuten.

### 5.3 Eingabeinvarianten

Vor S7 müssen gelten:

- S6 ist freigegeben,
- `gate_schema_id=rcc002.stage.s6-gates`,
- `gate_schema_version=1.0.0`,
- Zeilen sind streng zeitlich sortiert,
- Schlüssel sind eindeutig,
- der kanonische Schlüssel
  `(market_type, symbol, interval, open_time)` ist vollständig,
- bei unkonsolidierten Multi-Provider-Daten ist zusätzlich `provider`
  unmittelbar vor `market_type` im Schlüssel und in der Sortierreihenfolge
  enthalten,
- `interval=1m`,
- Segmentgrenzen sind bekannt,
- S0-bis-S6-Felder entsprechen ihren registrierten Eigentümerstufen,
- keine unbekannten Felder werden stillschweigend als S7-Input interpretiert.

Die Gültigkeit jeder einzelnen Zukunftskerze wird anschließend
familienbezogen geprüft. Eine ungültige Zukunftskerze darf nicht durch eine
gültige Signalkerze überstimmt werden.

### 5.4 Segmentvertrag

Für alle kanonischen S7-Familien ist `market_segment_id` aus S2 die
verbindliche zeitliche Marktsegmentgrenze.

`indicator_segment_id` aus S3 darf:

- für nachgelagerte Featureanalysen durchgereicht werden,
- nicht die S7-Marktsegmentgrenze ersetzen,
- nicht verwendet werden, um ein Zukunftsfenster über eine
  `market_segment_id`-Grenze zu erlauben.

Ein gültiges Zukunftsfenster benötigt für jede Bar von der Signalkerze `t`
bis zur letzten von der Familie verwendeten Zukunftskerze dieselbe
`market_segment_id`.

### 5.5 Qualitätsvertrag

Für jede von einer Label-Familie verwendete Preiszeile muss gelten:

```text
quality_gate_pass = true
quality_is_observed = true
quality_is_synthetic = false
quality_timestamp_valid = true
quality_ohlc_valid = true
quality_market_values_valid = true
```

Die S7-Stufe darf `quality_gate_pass` weder neu bilden noch überstimmen.

Ein qualitätsbedingt ungültiges Zukunftsfenster erzeugt:

- null in allen betroffenen numerischen S7-Feldern,
- `INVALID` in betroffenen Barrier-Outcome-Feldern,
- `*_valid_h=false`,
- mindestens einen passenden registrierten Reason Code.

### 5.6 Feature-Unabhängigkeit

Forward Returns werden ausschließlich aus Preis- und Qualitätsfeldern
berechnet.

Sie dürfen nicht von:

- aktuellem Signal,
- Regime,
- Gate,
- späterem Trade

abhängen. Diese Felder dienen erst nachgelagerten Gruppierungen.

## 6. Gemeinsame Return-Konvention

### 6.1 Long

Für Entry `P_entry` und Exit `P_exit`:

`long_return = P_exit / P_entry - 1`

### 6.2 Short

Für ein linear abgerechnetes Short-Exposure:

`short_return = (P_entry - P_exit) / P_entry`

Damit:

`short_return = -long_return`

bei identischen Entry-/Exit-Preisen und vor Kosten.

### 6.3 Vorzeichen

Für beide Richtungen gilt:

- positiver Return = Gewinn,
- null = unverändert,
- negativer Return = Verlust.

### 6.4 Prozentdarstellung

Kanonische Return-Felder werden als Dezimalbruch gespeichert:

- `0.01` = 1 %,
- `-0.02` = -2 %.

Berichte dürfen zusätzlich Prozentwerte anzeigen, aber nicht anstelle der
kanonischen Dezimalwerte speichern.

## 7. Close-to-Close Forward Returns

### 7.1 Long

Für jeden Horizont `h`:

`fwd_cc_long_ret_h_t = C_(t+h) / C_t - 1`

### 7.2 Short

`fwd_cc_short_ret_h_t = (C_t - C_(t+h)) / C_t`

Damit:

`fwd_cc_short_ret_h_t = -fwd_cc_long_ret_h_t`

### 7.3 Log Return

Optionaler deskriptiver Log Return:

`fwd_cc_log_ret_h_t = log(C_(t+h) / C_t)`

Für eine Short-Richtung:

`fwd_cc_short_log_ret_h_t = -fwd_cc_log_ret_h_t`

### 7.4 Verwendung

Close-to-Close-Returns eignen sich für:

- deskriptive Marktanalysen,
- Signal-Outcome-Analysen,
- richtungsneutrale Vergleichsforschung.

Sie sind kein unmittelbarer Execution-Return.

## 8. Next-Open-to-Close Forward Returns

### 8.1 Long

`fwd_noc_long_ret_h_t = C_(t+h) / O_(t+1) - 1`

### 8.2 Short

`fwd_noc_short_ret_h_t = (O_(t+1) - C_(t+h)) / O_(t+1)`

### 8.3 Gültigkeit

Erforderlich sind:

- Kerze `t+1` vollständig vorhanden,
- Kerze `t+h` vollständig vorhanden,
- alle Kerzen von `t+1` bis `t+h` im selben gültigen Segment.

### 8.4 Interpretation

Dieses Label ist ein ausführungsnaher Preisproxy, aber keine vollständige
Orderausführungssimulation.

Es modelliert nicht:

- Intrabar-Latenz,
- Orderbuchtiefe,
- Partial Fills,
- variable Slippage,
- Funding,
- Liquidation,
- Positionsgrößenwirkung.

## 9. Kostenprofile

### 9.1 Brutto zuerst

Bruttoreturns bleiben immer erhalten.

Kostenbereinigte Felder werden zusätzlich erzeugt und dürfen Bruttowerte nicht
überschreiben.

### 9.2 Projekt-Baseline

`COST_PROXY_FEE_RT_0004_V1`:

- `fee_roundtrip = 0.0004`,
- `slippage_roundtrip = 0`,
- `total_cost_fraction = 0.0004`.

Dies entspricht der aktuellen Projektbaseline von 0,04 % Roundtrip-Fee.

### 9.3 Konfigurierbares Slippage-Profil

Zusätzliche Profile dürfen definieren:

- Entry-Slippage,
- Exit-Slippage,
- Roundtrip-Slippage,
- asymmetrische Long-/Short-Kosten.

Jedes Profil benötigt eine eigene ID und Version.

### 9.4 Linearer Kostenproxy

Für beide Richtungen:

`net_proxy_return = gross_return - total_cost_fraction`

Feldnamen müssen `net_proxy` enthalten.

### 9.5 Einschränkung

Der lineare Kostenproxy ist keine exakte Börsenabrechnung.

Er dient:

- konsistenten Sensitivitätsanalysen,
- Vergleich mit der bestehenden Fee-Konvention,
- Vorfilterung offensichtlich zu kleiner Bruttoeffekte.

Backtests und Execution Layer bleiben für reale Kostenmodellierung
autoritativ.

## 10. Forward Excursions

### 10.1 Zukunftsfenster

Für Next-Open-Entry und Horizont `h`:

`future_window_h = [t+1, ..., t+h]`

Entry:

`P_entry = O_(t+1)`

### 10.2 Long MFE

`fwd_long_mfe_h_t = max(H_i, i=t+1...t+h) / P_entry - 1`

### 10.3 Long MAE

`fwd_long_mae_h_t = min(L_i, i=t+1...t+h) / P_entry - 1`

Wegen `L_(t+1) <= O_(t+1)` gilt:

`fwd_long_mae_h_t <= 0`

### 10.4 Short MFE

`fwd_short_mfe_h_t = (P_entry - min(L_i, i=t+1...t+h)) / P_entry`

### 10.5 Short MAE

`fwd_short_mae_h_t = (P_entry - max(H_i, i=t+1...t+h)) / P_entry`

Wegen `H_(t+1) >= O_(t+1)` gilt:

`fwd_short_mae_h_t <= 0`

Entsprechend gilt für gültige Fenster:

- `fwd_long_mfe_h_t >= 0`,
- `fwd_short_mfe_h_t >= 0`.

### 10.6 Zeit bis Extrem

Zusätzlich:

- `fwd_long_mfe_first_bar_h`,
- `fwd_long_mae_first_bar_h`,
- `fwd_short_mfe_first_bar_h`,
- `fwd_short_mae_first_bar_h`.

Bei mehrfach identischem Extrem wird der erste auftretende Bar-Offset
gespeichert.

Der erste zukünftige Bar besitzt Offset `1`.

## 11. Richtungslabels

### 11.1 Bruttolabel

Für einen Return `r`:

- `+1`, wenn `r > 0`,
- `0`, wenn `r = 0`,
- `-1`, wenn `r < 0`.

Felder:

- `label_cc_long_direction_h`,
- `label_cc_short_direction_h`,
- `label_noc_long_direction_h`,
- `label_noc_short_direction_h`.

### 11.2 Kostenbereinigtes Label

Auf dem Net-Proxy-Return:

- `+1`, wenn `net_proxy_return > 0`,
- `0`, wenn `net_proxy_return = 0`,
- `-1`, wenn `net_proxy_return < 0`.

### 11.3 Kein globaler Deadband

RCC-002 verwendet keinen undokumentierten neutralen Toleranzbereich um null.

Ein Deadband darf als eigenes Profil eingeführt werden, wenn:

- Schwelle präregistriert ist,
- Kostenbezug dokumentiert ist,
- Robustheit separat getestet wird.

## 12. Quantitative Return-Buckets

### 12.1 Zweck

Quantile oder feste Return-Buckets dürfen für Analyse und ML erzeugt werden,
aber nicht implizit aus dem gesamten Datensatz gelernt werden.

### 12.2 Feste Buckets

Ein festes Bucket-Profil benötigt:

- explizite Grenzen,
- Richtung,
- Return-Familie,
- Horizont,
- Kostenprofil.

### 12.3 Datengetriebene Buckets

Quantilgrenzen dürfen ausschließlich auf dem Trainingszeitraum bestimmt
werden.

Dieselben gespeicherten Grenzen werden unverändert auf Validierung und Test
angewandt.

Die Verwendung vollständiger Datensatzquantile ist Leakage.

## 13. Barrier-Label-Grundmodell

### 13.1 Parameter

Ein Barrier-Profil definiert:

- Entry-Preisreferenz,
- Take-Profit-Distanz,
- Stop-Loss-Distanz,
- maximalen Horizont,
- Long-/Short-Richtung,
- Intrabar-Ambiguitätsregel,
- Kostenprofil.

### 13.2 Long-Barrieren

Bei Entry `P_entry`:

`long_tp_price = P_entry * (1 + tp_fraction)`

`long_sl_price = P_entry * (1 - sl_fraction)`

### 13.3 Short-Barrieren

`short_tp_price = P_entry * (1 - tp_fraction)`

`short_sl_price = P_entry * (1 + sl_fraction)`

### 13.4 Ereignisse

Zulässige Outcomes:

- `TP_FIRST`,
- `SL_FIRST`,
- `TIMEOUT`,
- `AMBIGUOUS_BOTH_HIT`,
- `INVALID`.

## 14. Intrabar-Ambiguität

### 14.1 Problem

Mit OHLC-Daten ist die Reihenfolge von High und Low innerhalb derselben Kerze
nicht bekannt.

Wenn in derselben 1m-Kerze sowohl TP als auch SL berührt werden, kann nicht
bestimmt werden, welche Barriere zuerst erreicht wurde.

### 14.2 Kanonische Regel

Der kanonische Barrier-Outcome lautet:

`AMBIGUOUS_BOTH_HIT`

Die Beobachtung darf nicht automatisch als Gewinn oder Verlust klassifiziert
werden.

### 14.3 Sensitivitätsprofile

Zusätzliche Analyseprofile dürfen berechnen:

- `PESSIMISTIC_SL_FIRST`,
- `OPTIMISTIC_TP_FIRST`.

Diese Ergebnisse bleiben getrennt und dürfen den kanonischen Ambiguous-Status
nicht überschreiben.

### 14.4 Keine zufällige Reihenfolge

Eine zufällige TP-/SL-Reihenfolge ist im kanonischen Build unzulässig.

## 15. L1-Vergleichsprofil

### 15.1 Profil-ID

`L1_BARRIER_TP050_SL020_V1`

### 15.2 Parameter

- Entry-Proxy: `O_(t+1)`,
- TP: `0.05`,
- SL: `0.02`,
- Richtung: Long und Short getrennt,
- maximale Horizonte aus der registrierten Horizon-Liste,
- Intrabar-Regel: `AMBIGUOUS_BOTH_HIT`.

### 15.3 Status

Dieses Profil dient dem Vergleich mit der bestehenden L1-Baseline.

Es ersetzt nicht:

- den tatsächlichen L1-Execution Layer,
- signalabhängige Exits,
- Short-Time-Stop,
- Gebührenberechnung im Backtest.

### 15.4 Short-Time-Stop

Der bestehende Short-Time-Stop von 60 Minuten ist eine Execution-Regel und
wird nicht still in das allgemeine Barrier-Profil integriert.

Ein separates Labelprofil darf später den 60-Minuten-Short-Timeout exakt
modellieren.

## 16. Barrier-Suche

### 16.1 Reihenfolge über Kerzen

Kerzen werden chronologisch von `t+1` bis `t+h` geprüft.

### 16.2 Open-Gap-Priorität

Der Open-Preis einer Kerze ist zeitlich vor deren unbekannter Intrabar-
High-/Low-Reihenfolge beobachtbar.

Deshalb wird pro Zukunftskerze zuerst geprüft:

- Long: `open >= long_tp_price` oder `open <= long_sl_price`,
- Short: `open <= short_tp_price` oder `open >= short_sl_price`.

Wird eine Barriere bereits durch den Open-Preis überschritten, gilt diese
Barriere als zuerst getroffen. Erst wenn der Open-Preis zwischen beiden
Barrieren liegt, werden High und Low geprüft.

### 16.3 Erster eindeutiger Treffer

- Nur TP in einer Kerze berührt → `TP_FIRST`.
- Nur SL in einer Kerze berührt → `SL_FIRST`.
- Beide in derselben ersten Trefferkerze → `AMBIGUOUS_BOTH_HIT`.
- Keine Barriere bis Horizontende → `TIMEOUT`.

Die Ambiguitätsregel gilt nur, wenn der Open-Preis keine Barriere bereits
eindeutig ausgelöst hat.

### 16.4 Treffer-Offsets

Gespeichert werden:

- richtungs- und profilspezifisches `barrier_*_first_hit_bar_*_h`,
- richtungs- und profilspezifisches `barrier_*_first_hit_time_*_h`,
- richtungs- und profilspezifisches `barrier_*_outcome_*_h`.

Offset `1` bezeichnet Kerze `t+1`.

Die exakten kanonischen Feldschablonen stehen in Abschnitt 20.8.

## 17. Gültigkeit eines Forward Labels

### 17.1 Vollständiger Horizont

Ein Label ist nur gültig, wenn alle erforderlichen Kerzen bis `t+h`
vorhanden und validiert sind.

### 17.2 Segmentregel

Signalkerze, Entry-Kerze und alle Zukunftskerzen müssen zum selben
beobachteten Segment gehören.

### 17.3 Lücken

Überschreitet ein Zukunftsfenster eine Lücke:

- Return ungültig,
- Excursion ungültig,
- Direction Label ungültig,
- Barrier Label `INVALID`.

Reason Code:

`LBL_WINDOW_CROSSES_MARKET_SEGMENT`

### 17.4 Tail

Für die letzten `h` Zeilen eines Datensatzes fehlen regulär vollständige
Zukunftsdaten.

Diese Werte sind ungültig mit:

`LBL_FUTURE_HORIZON_INCOMPLETE`

Diese Zeilen werden nicht entfernt und nicht durch synthetische Ersatzzeilen
ersetzt; die betroffenen Feldwerte folgen der Nullsemantik aus §18.3.

### 17.5 Synthetische Kerzen

Kanonische Labels dürfen keine synthetischen Zukunftskerzen verwenden.

Ein separates Sensitivitätsprofil benötigt eine eigene Labelprofil-ID.

## 18. Label-Validitätsfelder

### 18.1 Familienbezogene Gültigkeit

Für jeden registrierten Horizont werden exakt folgende
Gültigkeitsfeldschablonen expandiert:

| Feldschablone | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `fwd_cc_valid_h` | `Boolean` | Nein | Gültigkeit der Close-to-Close-Familie |
| `fwd_cc_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Close-to-Close-Familie |
| `fwd_cc_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des CC-Fensters |
| `fwd_noc_valid_h` | `Boolean` | Nein | Gültigkeit der Next-Open-to-Close-Familie |
| `fwd_noc_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der NOC-Familie |
| `fwd_noc_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des NOC-Fensters |
| `fwd_excursion_valid_h` | `Boolean` | Nein | Gültigkeit der Excursion-Familie |
| `fwd_excursion_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Excursion-Familie |
| `fwd_excursion_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des Excursion-Fensters |
| `label_cc_direction_valid_h` | `Boolean` | Nein | Gültigkeit der CC-Richtungslabels |
| `label_cc_direction_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der CC-Richtungslabels |
| `label_cc_direction_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität der CC-Richtungslabels |
| `label_noc_direction_valid_h` | `Boolean` | Nein | Gültigkeit der NOC- und Net-Proxy-Richtungslabels |
| `label_noc_direction_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der NOC-Richtungslabels |
| `label_noc_direction_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität der NOC-Richtungslabels |
| `barrier_valid_h` | `Boolean` | Nein | Gültigkeit der Long-/Short-Barrier-Familie |
| `barrier_reason_codes_h` | geordnete Liste `Utf8` | Nein | Gründe der Barrier-Familie |
| `barrier_label_segment_id_h` | `Utf8` | Ja | bestätigte Segmentidentität des Barrier-Fensters |

Der abschließende Platzhalter `_h` wird ausschließlich durch einen Suffix
aus Abschnitt 4.1 ersetzt.

Beispiel:

```text
fwd_cc_valid_h060
fwd_cc_reason_codes_h060
fwd_cc_label_segment_id_h060
```

### 18.2 Gemeinsame Horizon-Metadaten

Für jeden Horizont werden außerdem erzeugt:

| Feldschablone | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `label_horizon_bars_h` | `UInt16` | Nein | registrierte Zahl der 1m-Intervalle |
| `label_available_at_h` | UTC-Timestamp in Millisekunden | Ja | frühester Zeitpunkt, zu dem Ergebnis oder Invalidität vollständig bestimmbar ist |

Für ein vollständiges Horizon-Ende gilt:

```text
label_available_at_h = close_time_(t+h)
```

Bei `LBL_FUTURE_HORIZON_INCOMPLETE` gilt:

```text
label_available_at_h = null
```

### 18.3 Nullsemantik

Wenn ein familienbezogenes `*_valid_h=false` ist:

- alle numerischen Felder dieser Familie und dieses Horizonts sind `null`;
- alle diskreten Richtungsfelder dieser Familie und dieses Horizonts sind
  `null`;
- Barrier-Outcomes lauten `INVALID`;
- Barrier-Trefferbar und -zeit sind `null`;
- die zugehörige Reason-Code-Liste enthält mindestens einen invalidierenden
  Code;
- die familienbezogene Segment-ID ist `null`, wenn keine einzige gültige
  Segmentidentität für das vollständige Fenster bestätigt werden kann.

Ein globales `label_valid` oder `label_valid_h` ist unzulässig, weil es
unterschiedliche Familienvoraussetzungen verdecken würde.

### 18.4 Reason-Code-Listen

Alle familienbezogenen Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

## 19. Reason Codes

### 19.1 Registry-Identität

```text
label_reason_code_registry_version=1.0.0
```

### 19.2 Verbindliches Register

| Priorität | Code | Ebene oder Familie | Wirkung |
|---:|---|---|---|
| 10 | `LBL_SCHEMA_MISMATCH` | Stufe | Buildabbruch |
| 20 | `LBL_PROFILE_MISMATCH` | Stufe | Buildabbruch |
| 30 | `LBL_HORIZON_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 40 | `LBL_COST_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 50 | `LBL_BARRIER_PROFILE_UNKNOWN` | Stufe | Buildabbruch |
| 60 | `LBL_INTERVAL_UNSUPPORTED` | Stufe | Buildabbruch |
| 100 | `LBL_INPUT_INVALID` | alle | invalidierend |
| 110 | `LBL_FUTURE_HORIZON_INCOMPLETE` | alle | invalidierend |
| 120 | `LBL_WINDOW_CROSSES_MARKET_SEGMENT` | alle | invalidierend |
| 130 | `LBL_FUTURE_BAR_QUALITY_FAILED` | alle | invalidierend |
| 140 | `LBL_SYNTHETIC_INPUT_DISALLOWED` | alle | invalidierend |
| 150 | `LBL_ENTRY_PRICE_INVALID` | NOC, Excursion, Direction, Barrier | invalidierend |
| 160 | `LBL_EXIT_PRICE_INVALID` | CC, NOC, Direction | invalidierend |
| 170 | `LBL_NONFINITE_RESULT` | numerische Familien | invalidierend |
| 180 | `LBL_BARRIER_BOTH_HIT` | Barrier | gültiger Informationscode |
| 190 | `LBL_BARRIER_TIMEOUT` | Barrier | gültiger Informationscode |

`LBL_WINDOW_CROSSES_GAP` ist ein historischer Alias und im kanonischen
Schema `rcc002.stage.s7-labels/1.0.0` nicht zulässig. Die kanonische
Segmentverletzung lautet `LBL_WINDOW_CROSSES_MARKET_SEGMENT`.

### 19.3 Bildung

Stageweite Profil- oder Schemafehler erzeugen kein teilweise veröffentlichtes
S7-Zeilenartefakt.

Zeilenbezogene Reason Codes werden familien- und horizonspezifisch gebildet.
Alle sicher feststellbaren Gründe bleiben erhalten, soweit ihre Ermittlung
keine fachliche Auswertung auf ungültigen Werten erfordert.

Bei einer unvollständigen Zukunft gilt ausschließlich:

```text
LBL_FUTURE_HORIZON_INCOMPLETE
```

für die wegen des fehlenden Endes nicht auswertbaren Familien.

Bei einer vorhandenen, aber segmentüberschreitenden Zukunft gilt:

```text
LBL_WINDOW_CROSSES_MARKET_SEGMENT
```

Qualitäts- und Synthetic-Codes dürfen zusätzlich aufgenommen werden, wenn die
betroffene Bar sicher bestimmbar ist.

`LBL_BARRIER_BOTH_HIT` und `LBL_BARRIER_TIMEOUT` sind mit
`barrier_valid_h=true` vereinbar.

## 20. Feldbenennung

### 20.1 Horizontsuffix

Horizonte verwenden das Registry-Suffix:

- `_h001`,
- `_h005`,
- `_h015`,
- `_h060`,
- `_h240`,
- `_h1440`.

### 20.2 Beispiele

- `fwd_cc_long_ret_h060`,
- `fwd_cc_short_ret_h060`,
- `fwd_noc_long_ret_h060`,
- `fwd_noc_short_ret_h060`,
- `fwd_noc_long_net_proxy_fee_rt_0004_h060`,
- `fwd_long_mfe_h060`,
- `fwd_long_mae_h060`,
- `label_noc_long_direction_h060`,
- `barrier_long_outcome_tp050_sl020_h060`.

### 20.3 Präfixschutz

Nur S7 darf regulär Felder mit folgenden Präfixen erzeugen:

- `fwd_`,
- `label_`,
- `barrier_`.

Diese Präfixregel ist eine zusätzliche Schutzschicht. Die autoritative
Leakage-Klassifikation entsteht aus:

```text
field_owner_stage=S7_LABELS
```

Ein S7-Feld bleibt unabhängig von seinem Namen ein S7-Feld.

### 20.4 Kanonische Basisfelder

Die nicht horizonspezifischen S7-Basisfelder lauten exakt:

| Feld | Logischer Typ | Nullbar | Eigentümer |
|---|---|:---:|---|
| `label_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_schema_ref` | `Utf8` | Nein | `S7_LABELS` |
| `horizon_registry_id` | `Utf8` | Nein | `S7_LABELS` |
| `horizon_registry_version` | `Utf8` | Nein | `S7_LABELS` |
| `cost_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `cost_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `barrier_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `barrier_profile_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_reason_code_registry_version` | `Utf8` | Nein | `S7_LABELS` |
| `label_numeric_profile_id` | `Utf8` | Nein | `S7_LABELS` |
| `label_numeric_profile_version` | `Utf8` | Nein | `S7_LABELS` |

### 20.5 Return-Feldschablonen

Für jeden registrierten Horizont werden exakt erzeugt:

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `fwd_cc_long_ret_h` | `Float64` | Ja |
| `fwd_cc_short_ret_h` | `Float64` | Ja |
| `fwd_cc_log_ret_h` | `Float64` | Ja |
| `fwd_cc_short_log_ret_h` | `Float64` | Ja |
| `fwd_noc_long_ret_h` | `Float64` | Ja |
| `fwd_noc_short_ret_h` | `Float64` | Ja |
| `fwd_noc_long_net_proxy_fee_rt_0004_h` | `Float64` | Ja |
| `fwd_noc_short_net_proxy_fee_rt_0004_h` | `Float64` | Ja |

### 20.6 Excursion-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `fwd_long_mfe_h` | `Float64` | Ja |
| `fwd_long_mae_h` | `Float64` | Ja |
| `fwd_short_mfe_h` | `Float64` | Ja |
| `fwd_short_mae_h` | `Float64` | Ja |
| `fwd_long_mfe_first_bar_h` | `UInt16` | Ja |
| `fwd_long_mae_first_bar_h` | `UInt16` | Ja |
| `fwd_short_mfe_first_bar_h` | `UInt16` | Ja |
| `fwd_short_mae_first_bar_h` | `UInt16` | Ja |

### 20.7 Richtungslabel-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `label_cc_long_direction_h` | `Int8` | Ja |
| `label_cc_short_direction_h` | `Int8` | Ja |
| `label_noc_long_direction_h` | `Int8` | Ja |
| `label_noc_short_direction_h` | `Int8` | Ja |
| `label_noc_long_net_proxy_fee_rt_0004_direction_h` | `Int8` | Ja |
| `label_noc_short_net_proxy_fee_rt_0004_direction_h` | `Int8` | Ja |

Zulässige gültige Werte sind ausschließlich:

```text
-1
0
1
```

### 20.8 Barrier-Feldschablonen

| Feldschablone | Logischer Typ | Nullbar |
|---|---|:---:|
| `barrier_long_outcome_tp050_sl020_h` | Enum `BarrierOutcome` | Nein |
| `barrier_short_outcome_tp050_sl020_h` | Enum `BarrierOutcome` | Nein |
| `barrier_long_first_hit_bar_tp050_sl020_h` | `UInt16` | Ja |
| `barrier_short_first_hit_bar_tp050_sl020_h` | `UInt16` | Ja |
| `barrier_long_first_hit_time_tp050_sl020_h` | UTC-Timestamp in Millisekunden | Ja |
| `barrier_short_first_hit_time_tp050_sl020_h` | UTC-Timestamp in Millisekunden | Ja |

`BarrierOutcome` verwendet ausschließlich:

```text
TP_FIRST
SL_FIRST
TIMEOUT
AMBIGUOUS_BOTH_HIT
INVALID
```

### 20.9 Deterministische Schablonenexpansion

In allen Schablonen wird der abschließende Platzhalter `_h` durch genau einen
registrierten Suffix ersetzt.

Beispiel:

```text
fwd_noc_long_ret_h060
barrier_long_outcome_tp050_sl020_h060
label_noc_direction_reason_codes_h060
```

Die vollständige S7-Feldmenge ist das kartesische Produkt aus:

1. den Basisfeldern aus Abschnitt 20.4,
2. allen Feldschablonen aus den Abschnitten 18.1, 18.2 und 20.5 bis 20.8,
3. allen sechs Suffixen aus Abschnitt 4.1.

Diese Expansion ist normativ und erzeugt keine optionalen oder impliziten
Felder.

### 20.10 Profilkollisionen

Werden mehrere Kosten- oder Barrier-Profile in derselben View gespeichert,
muss der Feldname einen eindeutigen registrierten Profil-Tag enthalten.

Alternativ werden getrennte Views mit identischem Basisschema und jeweils
genau einem Profil erzeugt. Zwei semantisch unterschiedliche Felder dürfen
niemals denselben Namen tragen.

Version `1.0.0` des kanonischen S7-Schemas enthält genau das Kostenprofil
`COST_PROXY_FEE_RT_0004_V1` und das Barrier-Profil
`L1_BARRIER_TP050_SL020_V1`. Ein weiteres Profil benötigt eine neue
kompatible Schemaversion oder eine getrennte registrierte Label-Research-View.

## 21. Output-Profile

### 21.1 Kanonisches Gesamtprofil

Die erste Baseline verwendet genau:

```text
label_profile_id=RCC002_CANONICAL_LABELS_V1
label_profile_version=1.0.0
label_schema_id=rcc002.stage.s7-labels
label_schema_version=1.0.0
label_schema_ref=rcc002.stage.s7-labels/1.0.0
horizon_registry_id=RCC002_FORWARD_HORIZONS_V1
horizon_registry_version=1.0.0
cost_profile_id=COST_PROXY_FEE_RT_0004_V1
cost_profile_version=1.0.0
barrier_profile_id=L1_BARRIER_TP050_SL020_V1
barrier_profile_version=1.0.0
label_reason_code_registry_version=1.0.0
label_numeric_profile_id=RCC002_FLOAT64_LABEL_NUMERICS_V1
label_numeric_profile_version=1.0.0
```

### 21.2 Enthaltene Familien

`RCC002_CANONICAL_LABELS_V1` enthält gemeinsam:

- Close-to-Close-Returns;
- Next-Open-to-Close-Returns;
- Log Returns;
- lineare Net-Proxy-Returns;
- Long-/Short-MFE und -MAE;
- erste Extrem-Offsets;
- Brutto- und Net-Proxy-Richtungslabels;
- Long-/Short-Barrier-Outcomes;
- familienbezogene Gültigkeit, Reason Codes und Segmentidentität;
- Horizon-Bars und Verfügbarkeitszeitpunkte.

Bezeichnungen wie `FORWARD_RETURNS_GROSS_V1`,
`FORWARD_RETURNS_COST_PROXY_V1`, `FORWARD_EXCURSIONS_V1`,
`DIRECTION_LABELS_V1` und `BARRIER_LABELS_V1` bezeichnen
Auswertungsfamilien, aber keine konkurrierenden kanonischen
S7-Stufenschemas.

### 21.3 Komponentenidentität

```text
component_id=RCC002_S7_LABEL_BUILDER
component_version=0.3.0
```

Die Implementierung manifestiert zusätzlich:

- Source-Tree- oder Commit-Identität;
- Eingangs- und Ausgangsschema-Fingerprint;
- Label-, Horizon-, Kosten-, Barrier- und Reason-Code-Profilversionen;
- numerisches Determinismusprofil;
- semantischen Konfigurationshash.

### 21.4 Schema-Kompatibilität

Für S7 gilt semantische Versionierung:

- Patch: keine logische Schema- oder Semantikänderung;
- Minor: ausschließlich registrierte rückwärtskompatible Erweiterung;
- Major: inkompatible Feld-, Typ-, Null-, Enum- oder Bedeutungsänderung.

Eine Implementierung darf unbekannte Felder oder unbekannte Major-Versionen
nicht still akzeptieren.

## 22. Zeilen- und Dateninvarianten

S7 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S6-Felder verändern.

Es muss gelten:

```text
S7_rows = S6_rows
S7_primary_keys = S6_primary_keys
S7_primary_key_order = S6_primary_key_order
S7_market_segment_id = S6_market_segment_id
S7_fields_owned_by_S0_to_S6 = S6_fields
```

und alle kanonischen Schlüssel bleiben identisch. Dies konkretisiert für S7
das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

S7 darf ausschließlich die in `rcc002.stage.s7-labels/1.0.0`
registrierten Erweiterungsfelder hinzufügen. Nicht registrierte Zusatzfelder,
alternative Aliasfelder oder eine zweite konkurrierende Horizon-Registry
machen das Artefakt nicht kanonisch.

Tail- oder Gap-Labels bleiben als ungültige Werte in ihren ursprünglichen
Zeilen erhalten.

## 23. Partitionierte Berechnung

### 23.1 Forward Overlap

Eine Partition benötigt bis zu:

`max_horizon = 1440`

zukünftige Kerzen als Read-Only-Overlap.

### 23.2 Keine Doppelausgabe

Overlap-Zeilen dienen nur der Labelberechnung und werden nicht doppelt
ausgegeben.

### 23.3 Letzte Partition

Unvollständige Tail-Horizonte der letzten Partition bleiben ungültig.

### 23.4 Parität

Serielle und partitionierte S7-Berechnung muss:

- identische Gültigkeit,
- identische diskrete Outcomes,
- innerhalb der Float-Toleranz identische Returns und Excursions

erzeugen.

## 24. Inkrementelle Aktualisierung

### 24.1 Neue Daten

Bei Datenfortschreibung werden zuvor ungültige Tail-Labels neu berechnet,
sobald ihr vollständiger Zukunftshorizont verfügbar ist.

Mindestens die letzten `max_horizon` bisherigen Zeilen werden erneut geprüft.

### 24.2 Historische Preiskorrektur

Wird Kerze `k` geändert, müssen für jeden Horizont alle Labelzeilen neu geprüft
werden, deren:

- Entry,
- Exit,
- Excursion Window oder
- Barrier Window

Kerze `k` enthält.

Für das Gesamtprofil ist mindestens der Bereich:

`[k - max_horizon, ..., k]`

zu invalidieren und neu zu berechnen.

### 24.3 Segmentänderung

Ändert sich eine Lücke oder Segmentgrenze, werden alle Zukunftsfenster neu
berechnet, die die betroffene Grenze erreichen können.

## 25. Dataset Splits

### 25.1 Zeitgerechte Splits

Training, Validierung und Test müssen chronologisch getrennt werden.

Zufälliges Row-Shuffling vor der Split-Bildung ist für zeitabhängige Labels
unzulässig.

### 25.2 Boundary Crossing

Ein Trainingssample bei `t` darf nicht verwendet werden, wenn sein
Labelhorizont in den Validierungs- oder Testzeitraum hineinreicht.

### 25.3 Purging

Vor jeder nachfolgenden Splitgrenze werden Samples entfernt, deren
Zukunftsfenster die Grenze überschreitet.

Die Purge-Länge richtet sich nach dem tatsächlich verwendeten maximalen
Horizont.

### 25.4 Embargo

Wenn Modell- oder Auswahlverfahren zusätzliche zeitliche Abhängigkeiten
erzeugen, darf nach einer Splitgrenze ein Embargo verwendet werden.

Embargo-Länge und Begründung müssen präregistriert werden.

### 25.5 Überlappende Labels

Forward Labels benachbarter Minuten überlappen stark.

Analysen und Unsicherheitsschätzungen müssen diese serielle Abhängigkeit
berücksichtigen. Die rohe Zeilenzahl darf nicht als Zahl unabhängiger
Beobachtungen interpretiert werden.

## 26. Feature-/Label-Trennung

### 26.1 Verbindliche S8-Viewklassen

Der übergeordnete S8-Vertrag reserviert:

| `schema_id` | `schema_version` | `schema_ref` | S7 zulässig | `allowlist_sha256` |
|---|---|---|:---:|---|
| `rcc002.view.research-features` | `1.0.0` | `rcc002.view.research-features/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.backtest-inputs` | `1.0.0` | `rcc002.view.backtest-inputs/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.paper` | `1.0.0` | `rcc002.view.paper/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.live` | `1.0.0` | `rcc002.view.live/1.0.0` | Nein | `2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` |
| `rcc002.view.label-research` | `1.0.0` | `rcc002.view.label-research/1.0.0` | Ja | `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` |
| `rcc002.view.audit` | `1.0.0` | `rcc002.view.audit/1.0.0` | Ja | `3c29f3219e65ca87df199a52dc8d15b54a6ea28884a863d1479d27e8a2401b56` |

Die Data-Pipeline-Spezifikation ist Eigentümerin der positiven Feld-Allowlist
jeder View. Die vorliegende Spezifikation ist Eigentümerin der
S7-Feldprovenienz.

Die sechs Allowlists sind in
`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.7.1`,
Abschnitt 7.9 vollständig expandiert. Die dortige Registry
`RCC002_S8_FIELD_OWNERSHIP_V1`, Version `1.0.0`, ordnet jedem Feld genau eine
Eigentümerstufe und Leakage-Klasse zu. Abweichende lokale Listen sind
unzulässig.

### 26.2 Label-Research-View

Eine ML- oder Outcome-View mit S7-Inhalten verwendet ausschließlich:

```text
rcc002.view.label-research/1.0.0
```

Sie enthält:

- explizit freigegebene Felder aus S0 bis S6;
- explizit ausgewählte und einzeln erlaubte S7-Felder;
- Split- und Purge-Metadaten aus einem registrierten Forschungsvertrag.

Eine Wildcard oder pauschale Freigabe aller zukünftigen S7-Felder ist
unzulässig.

### 26.3 Live-, Paper-, Backtest- und Feature-Views

Diese Views verwenden ausschließlich positive Feld-Allowlists aus S0 bis S6.

Sie müssen primär jedes Feld ausschließen, dessen registrierte
Erzeugerstufe lautet:

```text
S7_LABELS
```

Zusätzlich müssen sie sämtliche Felder mit folgenden Präfixen ausschließen:

- `fwd_*`,
- `label_*`,
- `barrier_*`

Die Präfixprüfung ersetzt weder Feldprovenienz noch positive Allowlist.
Unbekannte Felder und Felder ohne registrierte Eigentümerstufe werden
fail-closed abgelehnt.

### 26.4 Automatischer Leakage-Test

Der Leakage-Test muss fehlschlagen, wenn:

- ein Feld mit `field_owner_stage=S7_LABELS` in einer Research-Feature-,
  Backtest-Input-, Live- oder Paper-View vorkommt,
- ein S7-Präfix in einer dieser Views vorkommt,
- ein unbekanntes Feld durch eine positive Allowlist gelangt,
- ein Feld ohne registrierte Erzeugerstufe freigegeben wird,
- ein Feature erst nach dem Entscheidungszeitpunkt verfügbar ist,
- Splitgrenzen von Labelhorizonten überschritten werden,
- Labelstatistiken zur Feature-Normalisierung verwendet werden.

Der Test muss außerdem nachweisen, dass alle in
`rcc002.stage.s7-labels/1.0.0` registrierten Felder für Live und Paper
abgelehnt werden, auch wenn ein Testfeld absichtlich kein reserviertes Präfix
trägt.

## 27. Counterfactual Gate Evaluation

### 27.1 Unabhängige Outcome-Basis

Forward Returns werden für alle gültigen Zeitpunkte berechnet, unabhängig
davon, ob ein Gate oder Signal aktiv war.

### 27.2 Gruppierung erst nach Berechnung

Erst nach der unabhängigen S7-Berechnung dürfen Outcomes gruppiert werden nach:

- `allow_long`,
- `allow_short`,
- Regime,
- Signalzustand,
- Gate-Profil.

### 27.3 Vermeidung selektiver Labels

Es ist unzulässig, Forward Labels nur für erlaubte oder tatsächlich gehandelte
Zeilen zu erzeugen.

Dies würde die Counterfactual-Analyse verzerren.

## 28. Verhältnis zum Backtest

### 28.1 Label

Ein S7-Label beantwortet eine fest definierte Zukunftsfrage.

### 28.2 Backtest

Ein Backtest modelliert:

- Signalpersistenz,
- tatsächliche Entry-Zeit,
- Positionszustand,
- konkurrierende Exits,
- Cooldown,
- Kosten,
- Kapitalentwicklung.

### 28.3 Keine Ergebnisgleichsetzung

Forward-Return- oder Barrier-Label-Performance darf nicht als identisch mit
Strategieperformance dargestellt werden.

S7 dient:

- Hypothesengenerierung,
- Outcome-Analyse,
- ML-Zielbildung,
- Vorprüfung.

Die Strategievalidierung bleibt separat.

## 29. Legacy- und GS-Lineage

### 29.1 Historische BTC-Pipeline

Der verifizierte historische BTC-Builder erzeugte Indikatoren und
Signalspalten, aber die bisher untersuchte Datei belegt keine vollständig
versionierte kanonische Forward-Return-Stufe.

### 29.2 GS-Dateinamen

Erhaltene GS-Pfade enthalten Bezeichnungen wie:

`GS_PLUS_FORWARD_WITH_SIGNALS`

Dateinamen allein belegen jedoch nicht:

- Forward-Formel,
- Horizont,
- Entry-/Exit-Referenz,
- Kosten,
- Gap-Handling,
- Label-Verfügbarkeit.

### 29.3 Rekonstruktionsstatus

Eine GS-Forward-Rekonstruktion erhält:

`GS_FORWARD_RECONSTRUCTION_V1`

und Status:

`HYPOTHESIS`

bis Builder oder empirisch validierbare Datensätze die Regeln bestätigen.

## 30. Numerische Präzision

### 30.1 Datentyp

Returns, Log Returns und Excursions verwenden mindestens `float64`.

### 30.2 Keine Zwischenrundung

Entry-, Exit-, Extrem- und Kostenberechnungen werden nicht zwischengerundet.

### 30.3 Vergleichstoleranz

Für unabhängige Implementierungsvergleiche:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Diskrete Labels und Barrier-Outcomes müssen exakt übereinstimmen.

### 30.4 Numerisches Determinismusprofil

Vor `Approved for Implementation` muss ein registriertes numerisches Profil
mindestens festlegen:

- IEEE-754-`Float64` als Berechnungsdomäne;
- Operationsreihenfolge jeder Formel;
- Verhalten bei Division durch null;
- Konvertierung nicht endlicher Resultate in `null` plus Reason Code;
- FMA-Regel;
- Parallelreduktionsregel für Minima und Maxima;
- Behandlung von `-0.0`;
- Logarithmusimplementierung und gebundene numerische Bibliothek;
- exakte Vergleichsregeln für Barrieren und Richtungslabels;
- Referenztoleranzen für unabhängige Implementierungen.

Die erste Baseline reserviert:

```text
label_numeric_profile_id=RCC002_FLOAT64_LABEL_NUMERICS_V1
label_numeric_profile_version=1.0.0
```

Eine Änderung, die diskrete Outcomes, Gültigkeit oder numerische Werte
außerhalb der Referenztoleranzen verändern kann, ist eine semantische
Konfigurationsänderung.

## 31. Testanforderungen – Returns

### 31.1 Handberechnete Fälle

Mindestens:

- steigender Preis,
- fallender Preis,
- unveränderter Preis,
- Long und Short,
- Close-to-Close,
- Next-Open-to-Close,
- Kostenproxy,
- mehrere Horizonte.

### 31.2 Vorzeichenidentität

Vor Kosten muss gelten:

`short_return = -long_return`

für dieselben linearen Entry-/Exit-Referenzen.

### 31.3 Horizon Index

Für jeden Horizont wird geprüft, dass exakt `t+h` verwendet wird und kein
Off-by-one-Fehler besteht.

### 31.4 Tail

Die letzten `h` Zeilen sind für Horizont `h` ungültig, sofern keine späteren
Daten im selben Build verfügbar sind.

## 32. Testanforderungen – Excursions

Mindestens:

- Extrem in erster Zukunftskerze,
- Extrem in letzter Zukunftskerze,
- mehrfach identisches Extrem,
- ausschließlich steigende Serie,
- ausschließlich fallende Serie,
- Gap Crossing,
- Long-/Short-Symmetrie.

MFE-/MAE-Werte werden gegen handberechnete High-/Low-Fenster geprüft.

## 33. Testanforderungen – Barrieren

Mindestens:

- TP in erster Kerze,
- SL in erster Kerze,
- TP vor SL über verschiedene Kerzen,
- SL vor TP über verschiedene Kerzen,
- beide in derselben Kerze,
- Open-Gap über TP beziehungsweise unter SL,
- Open-Gap für Short unter TP beziehungsweise über SL,
- keine Barriere bis Timeout,
- Treffer exakt auf Barriere,
- Long und Short,
- Gap Crossing,
- unvollständiger Tail.

Eine exakte Berührung zählt als Treffer:

- Long TP: `high >= tp_price`,
- Long SL: `low <= sl_price`,
- Short TP: `low <= tp_price`,
- Short SL: `high >= sl_price`.

## 34. Property-, Leakage- und Paritätstests

### 34.1 Property-Tests

Es muss gelten:

- Änderungen nach `t+h` verändern Label `t,h` nicht,
- Änderungen innerhalb des Zukunftsfensters dürfen ausschließlich betroffene
  Labels ändern,
- S7 verändert keine S0-bis-S6-Felder,
- ungültige Zukunftsfenster erzeugen keine numerischen gültigen Labels,
- Live-/Paper-Allowlist enthält keine S7-Felder,
- serielle und partitionierte Berechnung stimmen überein,
- neue Daten vervollständigen nur zuvor unvollständige Tail-Horizonte oder
  davon abhängige Artefakte,
- identische Inputs und Profile erzeugen identische Outputs.

Zusätzlich werden systematisch generierte gültige OHLC-Sequenzen geprüft auf:

- endliche gültige Returns;
- `fwd_cc_short_ret_h = -fwd_cc_long_ret_h`;
- `fwd_noc_short_ret_h = -fwd_noc_long_ret_h`;
- Long- und Short-MFE größer oder gleich null;
- Long- und Short-MAE kleiner oder gleich null;
- Extrem-Offsets im Intervall `1...h`;
- ausschließlich registrierte Direction- und Barrier-Enums.

### 34.2 Schema- und Registry-Tests

Mindestens:

- Annahme von `rcc002.stage.s6-gates/1.0.0`;
- Ablehnung unbekannter S6-Major-Versionen;
- Ausgabe von `rcc002.stage.s7-labels/1.0.0`;
- exakte S7-Basisfeld-Allowlist;
- vollständige Expansion aller Feldschablonen über sechs Horizonte;
- exakte Feldreihenfolge;
- exakte logische Typen und Nullbarkeit;
- exakte Eigentümerstufe `S7_LABELS`;
- exakte Leakage-Klasse `FUTURE_OUTCOME`;
- Ablehnung unbekannter Horizon-, Kosten-, Barrier- und Reason-Code-Profile;
- Ablehnung nicht registrierter Zusatzfelder;
- Schema-Fingerprint-Parität.

### 34.3 Gültigkeits- und Reason-Code-Tests

Mindestens:

- unvollständiger Tail;
- Wechsel von `market_segment_id`;
- ungültige Zukunftskerze;
- synthetische Zukunftskerze;
- ungültiger Entry-Preis;
- ungültiger Exit-Preis;
- nicht endliches Resultat;
- Barrier-Ambiguität;
- Barrier-Timeout;
- leere Reason-Code-Liste bei vollständig gültigem Ergebnis;
- Deduplikation und Prioritätssortierung;
- numerische Nullwerte bei familienbezogener Invalidität;
- `INVALID` für ungültige Barrier-Outcomes.

### 34.4 Leakage-Tests

Für jede der folgenden Views wird jedes registrierte S7-Feld einzeln als
negativer Testfall injiziert:

- `rcc002.view.research-features/1.0.0`;
- `rcc002.view.backtest-inputs/1.0.0`;
- `rcc002.view.paper/1.0.0`;
- `rcc002.view.live/1.0.0`.

Jede Injektion muss unabhängig vom Feldnamen aufgrund von
`field_owner_stage=S7_LABELS` abgelehnt werden.

Zusätzlich werden Testfelder mit den Präfixen `fwd_`, `label_` und `barrier_`
bei fehlender oder absichtlich falscher Eigentümermetadaten abgelehnt.

### 34.5 Reconciliation- und Paritätstests

Mindestens:

- S6→S7-Zeilenzahl;
- Primärschlüssel und Sortierung;
- `market_segment_id`;
- unveränderte S0-bis-S6-Felder;
- serielle gegen partitionierte Berechnung;
- Vollbuild gegen inkrementellen Rebuild;
- Referenzimplementierung gegen Produktionsimplementierung;
- identische semantische Konfiguration bei unterschiedlicher physischer
  Publikationskonfiguration;
- erwartete ID-Wirkung semantischer und physischer
  Konfigurationsänderungen.

## 35. S7-Bericht

Der Bericht enthält mindestens:

- Build-, Schema- und Profilversionen,
- aktive Horizonte,
- Kosten- und Barrier-Profile,
- Zeilenzahl und Zeitbereich,
- gültige und ungültige Labels je Familie und Horizont,
- Tail-Invalidität,
- Gap-Crossing-Invalidität,
- Return-Verteilungen,
- Long-/Short-Symmetrieprüfung,
- MFE-/MAE-Verteilungen,
- Barrier-Outcome-Verteilungen,
- Ambiguous-Anteil,
- verfügbare Labelzeitpunkte,
- Partitionsparität,
- Leakage-Test,
- Output-Checksumme.

## 36. Ausgabevertrag

### 36.1 Logisches Ausgangsschema

S7 erzeugt ausschließlich:

```text
rcc002.stage.s7-labels/1.0.0
```

Das Schema enthält:

1. alle Felder aus `rcc002.stage.s6-gates/1.0.0` unverändert und in
   unveränderter Reihenfolge;
2. die S7-Basisfelder aus Abschnitt 20.4;
3. je Horizon-Suffix die expandierten Felder aus den Abschnitten 18.1, 18.2
   und 20.5 bis 20.8.

### 36.2 Kanonische Feldreihenfolge

Nach den unveränderten S6-Feldern lautet die S7-Reihenfolge:

1. Basisfelder in Tabellenreihenfolge aus Abschnitt 20.4;
2. Horizonte in Reihenfolge `H001`, `H005`, `H015`, `H060`, `H240`,
   `H1440`;
3. innerhalb jedes Horizonts:
   - gemeinsame Horizon-Metadaten,
   - Close-to-Close-Gültigkeit und Werte,
   - Next-Open-to-Close-Gültigkeit und Werte,
   - Excursion-Gültigkeit und Werte,
   - CC- und NOC-Richtungslabel-Gültigkeit und Werte,
   - Barrier-Gültigkeit und Werte.

Die maschinenlesbare Schemaregistry muss diese Reihenfolge vollständig
expandiert enthalten. Eine Implementierung darf die Tabellenreihenfolge nicht
aus eigener Zweckmäßigkeit verändern.

### 36.3 Eigentum und Leakage-Klasse

Für jedes neu erzeugte Feld gilt:

```text
field_owner_stage=S7_LABELS
leakage_class=FUTURE_OUTCOME
live_allowed=false
paper_allowed=false
backtest_input_allowed=false
research_feature_allowed=false
label_research_allowed=true
```

Die konkrete Aufnahme in eine Label-Research- oder Audit-View benötigt
zusätzlich die positive S8-Allowlist.

### 36.4 Schema-Fingerprint

Der logische S7-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Eigentümerstufe und Leakage-Klasse;
- Primärschlüssel und Sortierung;
- Horizon- und Profilzuordnung;
- Enum- und Reason-Code-Register;
- Feld- und Nullsemantik;
- Schema-Kompatibilitätsregeln.

### 36.5 Reconciliation

Vor Veröffentlichung werden mindestens geprüft:

```text
S7_rows = S6_rows
S7_keys_sha256 = S6_keys_sha256
S7_upstream_fields_semantic_sha256 = S6_fields_semantic_sha256
S7_market_segments_sha256 = S6_market_segments_sha256
```

Eine Abweichung ist ein Publication-Blocker.

### 36.6 Manifestpflicht

Das S7-Stage-Manifest referenziert mindestens:

- Eingangs- und Ausgangsschema-ID samt Version und Fingerprint;
- Komponenten-ID und Version;
- Label-, Horizon-, Kosten-, Barrier-, Reason-Code- und Numerikprofile;
- `semantic_build_configuration_sha256`;
- Code- und Umgebungsidentität;
- Eingangs- und Ausgangsartefakte;
- Reconciliation-Ergebnisse;
- S7-Bericht;
- semantische Output-Checksumme;
- physischen Artefaktbezug.

## 37. Konfiguration und offene Implementierungsparameter

### 37.1 Semantische Build-Konfiguration

Zur `semantic_build_configuration` gehören mindestens:

- Labelprofil;
- Horizon-Registry;
- Kostenprofil;
- Barrier-Profil;
- Intrabar-Ambiguitätsregel;
- Preisreferenzen;
- Return- und Excursion-Formeln;
- Gültigkeits- und Segmentregeln;
- Reason-Code-Registry;
- numerisches Determinismusprofil;
- logische S7-Schema-ID und Version;
- S8-Leakage- und Viewverträge;
- inkrementelle Invalidierungsregeln.

Der Hash:

```text
semantic_build_configuration_sha256
```

beeinflusst `build_id` und damit die Identität des logischen Datasetinhalts.

### 37.2 Physische Veröffentlichungskonfiguration

Zur `physical_publication_configuration` gehören innerhalb eines zuvor
freigegebenen physischen Profils:

- Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- temporäre Speicherorte;
- Retention technischer Zwischenartefakte;
- technisch gleichwertige Zielpfade.

Der Hash:

```text
physical_publication_configuration_sha256
```

beeinflusst ausschließlich physische Layout- und Artefaktidentitäten. Eine
reine Neuverpackung darf weder S7-Werte noch Gültigkeit, Reason Codes,
`build_id` oder `dataset_id` verändern.

### 37.3 Vor `Approved for Implementation` festzulegen

Vor Implementierungsfreigabe müssen versioniert vorliegen:

- vollständiges maschinenlesbares S7-Schema;
- vollständig expandiertes S7-Feldregister;
- Horizon-, Label-, Kosten-, Barrier-, Enum- und Reason-Code-Register;
- S7- und S8-Kompatibilitätsregeln;
- positive logische S8-View-Allowlists;
- numerisches Determinismusprofil und gebundene Bibliotheken;
- Referenztoleranzen;
- Golden Fixtures und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- Identitätsvorabbildungen;
- S6→S7-Reconciliation;
- Test- und Abnahmekriterien.

### 37.4 Während der Implementierung konkretisierbar

Während der Implementierung dürfen ausschließlich die physischen Parameter
aus Abschnitt 37.2 innerhalb freigegebener Profile konkretisiert werden.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen, Leakage-Schutz oder numerische
Determinismusregeln muss die betroffenen Review-Gates erneut durchlaufen.

## 38. Publication Gate

S7 darf nur veröffentlicht werden, wenn:

1. S6 vollständig freigegeben ist,
2. das Eingangsschema exakt `rcc002.stage.s6-gates/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s7-labels/1.0.0` erfüllt,
4. alle Horizonte, Profile, Enums und Reason Codes registriert sind,
5. Feldschablonen vollständig und eindeutig expandiert sind,
6. Entry-, Exit- und Horizon-Indizes korrekt sind,
7. Long-/Short-Vorzeichenprüfung bestanden ist,
8. Kostenprofile Bruttowerte nicht überschreiben,
9. Segment-, Qualitäts- und Tail-Regeln korrekt sind,
10. Barrier-Ambiguität erhalten bleibt,
11. keine nicht endlichen gültigen Labels bestehen,
12. familienbezogene Null- und Gültigkeitsinvarianten erfüllt sind,
13. Zeilen, Primärschlüssel, Segmente und S0-bis-S6-Werte unverändert sind,
14. serielle und partitionierte Berechnung übereinstimmen,
15. inkrementeller Rebuild und Vollbuild semantisch übereinstimmen,
16. stufenbasierte Leakage- und positive Allowlist-Tests bestanden sind,
17. kein S7-Feld in Research-Feature-, Backtest-Input-, Paper- oder
    Live-Views enthalten ist,
18. Reconciliation, Manifest, Schema und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder einen
Schema-, Profil-, Horizon-, Gültigkeits-, Segment-, Leakage-, Reason-Code-,
Reconciliation- oder Identitätsfehler überstimmen.

## 39. Abnahmekriterien

### 39.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. der S6-Eingangsvertrag vollständig festgelegt ist;
2. genau ein S7-Schema und ein Horizon-Register gelten;
3. alle S7-Basisfelder und Feldschablonen vollständig registriert sind;
4. alle Return-, Excursion-, Direction- und Barrier-Regeln eindeutig sind;
5. Gültigkeit, Nullsemantik, Segmentgrenzen und Verfügbarkeit
   widerspruchsfrei sind;
6. Reason Codes und Enums vollständig versioniert sind;
7. stufenbasierter Leakage-Schutz und positive S8-Allowlists spezifiziert
   sind;
8. semantische und physische Konfiguration getrennt sind;
9. numerisches Determinismusprofil und Referenztoleranzen feststehen;
10. Golden-, Unit-, Property-, Leakage-, Schema-, Reconciliation- und
    Integrationstestverträge vollständig sind;
11. Split-, Purge- und Embargoverträge festgelegt sind;
12. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
13. keine offene Entscheidung fachliche Werte, Gültigkeit, logische Schemas,
    Leakage-Schutz oder Identitätsvorabbildungen verändern kann.

### 39.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Return-Familien handberechnet getestet sind;
2. jeder Horizont auf Off-by-one-Fehler geprüft ist;
3. Long-/Short-Symmetrie bestanden ist;
4. Kostenproxy und Bruttowerte getrennt sind;
5. MFE/MAE und Barrier-Logik vollständig getestet sind;
6. Qualitäts-, Tail- und Segmentregeln bestanden sind;
7. Purging und Split-Grenzen getestet sind;
8. S8-Live-/Paper-Allowlist S7 vollständig ausschließt;
9. stufenbasierte Leakage-Tests sämtliche S7-Felder erkennen;
10. serielle, partitionierte, inkrementelle und unabhängige
    Referenzberechnung übereinstimmen;
11. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
12. S6→S7-Reconciliation vollständig besteht;
13. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind;
14. das S7-Publication-Gate automatisiert bestanden ist.

## 40. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die in Version 0.3.0 geschlossenen
AIR-001-Korrekturen und korrigiert zusätzlich:

- `SCR-005-M01` – unversionierte `schema_id`, getrennte
  `schema_version` und abgeleitete `schema_ref`;
- `AIR-005-H01` – versionsgebundene, vollständig expandierte positive
  S8-Feld-Allowlists einschließlich Eigentümerstufe, Leakage-Klasse,
  Erzeugerstufe, SHA-256 und Fail-closed-Negativtests.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0

RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
Version 0.4.0

RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
Version 0.5.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. vollständige interne Qualitätskontrolle;
2. neues vollständiges Spezifikationspaket;
3. Scientific Consistency Re-Review 006;
4. nur bei bestandenem SCR-006: fokussierter Architecture Integrity
   Re-Review;
5. Editorial Pass;
6. Internal Certification;
7. Claude Independent Architecture Review;
8. Gemini Independent Scientific and Adversarial Audit;
9. ChatGPT Final Consolidation;
10. `Baseline V1 Certified`;
11. Implementierungsfreigabe.
