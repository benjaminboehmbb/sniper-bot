# RCC-002 SCR-004 Full Specification Bundle

## Paketmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Vollständige Eingabe für den fokussierten Scientific Consistency Re-Review |
| Speicherort | `docs/review/` |
| Dateiname | `RCC_002_SCR_004_FULL_SPEC_BUNDLE_2026-07-23.md` |
| Datum | `2026-07-23` |
| Status | Review Input – Not Yet Reviewed |
| Enthaltene Spezifikationen | 7 |

## Reviewauftrag

Dieses Paket dient dem fokussierten Scientific Consistency Re-Review
der Korrekturen zu `SCR-003-B01`, `SCR-003-B02`, `SCR-003-m01`
und `SCR-003-m02` einschließlich ihrer Querwirkungen.

Das Paket begründet noch keine Freigabe, Certification oder
Implementierungsfreigabe.

---

# Eingebettetes Dokument 1 von 7

## Quelldatei: `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`

# RCC-002 Data Pipeline Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Wissenschaftliche und technische Kernspezifikation |
| Dokument-ID | `RCC_002_DATA_PIPELINE_SPECIFICATION` |
| Version | 0.5.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Speicherort im Repository | `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` |
| Geltungsbereich | Kanonische Forschungsdatenpipeline für BTCUSDT und spätere weitere Assets/Zeitebenen |
| Primäre Abhängigkeiten | `Master_Analysis_Blueprint.md`; historische BTC-Pipeline; GS-Pipeline-Artefakte; RCC-002-Nachfolgespezifikationen |
| Referenziert durch | künftige RCC-002-Implementierung; Analyse-Runner; SimTrader; Live-/Paper-Trading-Paritätsprüfung; Dataset Manifest |
| Autoritative Sprache | Englisch für Code, Schemas und Feldnamen; Deutsch für die normative Erläuterung |

### Review-Nachweis

| Review | Status | Ergebnis |
|---|---|---|
| Interne Struktur- und Konsistenzprüfung | Bestanden mit Überarbeitung | Stufenverträge, Leakage-Schutz, Qualitätsflag-Propagation, Korrekturregeln und Publication Gate ergänzt beziehungsweise präzisiert |
| Scientific Consistency Review | Nicht bestanden; dritte Korrektur eingearbeitet | Frühere Befunde geschlossen; `SCR-003-B01` aus `RCC-002-SCR-003` in Version 0.5.0 korrigiert; fokussierter Re-Review ausstehend |
| Architecture Integrity Review | Ausstehend | Nach bestandenem fokussierten Scientific Consistency Re-Review |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach abgeschlossener finaler Konsolidierung und Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert die übergeordnete Architektur, die verbindlichen
Schnittstellen und die wissenschaftlichen Kontrollanforderungen der
RCC-002-Datenpipeline.

Die Pipeline muss aus historischen und aktuellen OHLCV-Rohdaten einen
reproduzierbaren, kausalen und manifestgebundenen Datensatz erzeugen, der
gleichzeitig verwendbar ist für:

- wissenschaftliche Strategieforschung,
- deterministische Backtests,
- Paper Trading,
- spätere Live-Trading-Parität,
- Regime- und Zustandsanalysen,
- Forward-Return- und Label-Analysen,
- unabhängige Reproduktion und Auditierung.

Dieses Dokument definiert bewusst nicht sämtliche mathematischen
Schwellenwerte und Versionen einzelner Indikatoren, Signaltransformationen,
Regimemodelle oder Labels. Diese werden in nachgeordneten Spezifikationen
festgelegt. Dieses Dokument definiert jedoch verbindlich, wie diese
Komponenten zusammenwirken müssen.

## 2. Normative Begriffe

Die Begriffe `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` und `MAY` sind
normativ zu verstehen:

- `MUST`: zwingende Anforderung;
- `MUST NOT`: zwingendes Verbot;
- `SHOULD`: begründeter Standardfall;
- `SHOULD NOT`: nur mit dokumentierter Ausnahme zulässig;
- `MAY`: optionale, aber zulässige Ausprägung.

## 3. Geltungsbereich

RCC-002 umfasst die vollständige Datenverarbeitung von unveränderten
Quellartefakten bis zu konsumfertigen Forschungs-, Backtest- und
Live-/Paper-Views.

Enthalten sind:

1. Rohdatenaufnahme und Quellidentität.
2. Normalisierung von Zeit, Schema und Datentypen.
3. Datenvalidierung und kontrollierte Lückenbehandlung.
4. Berechnung kausaler Rohindikatoren.
5. Versionierte Signaltransformation.
6. Reine Marktregimeklassifikation.
7. Getrennte Long-/Short-Handels-Gates.
8. Forward Returns und Forschungslabels.
9. Export in manifestgebundene Artefakte.
10. Qualitäts-, Reproduzierbarkeits- und Publication Gates.

Nicht enthalten sind:

- konkrete Entry- und Exit-Entscheidungen einer Strategie;
- Positionsgrößensteuerung;
- Order-Routing;
- Börsenadapter;
- Live-Execution-State;
- Portfoliosteuerung;
- Strategieparameteroptimierung.

Diese nachgelagerten Systeme dürfen RCC-002-Artefakte konsumieren, aber ihre
Entscheidungslogik darf nicht rückwirkend in die Datenpipeline einfließen.

## 4. Evidenzbasis und Legacy-Befunde

RCC-002 basiert auf der Rekonstruktion mindestens zweier historischer
Pipeline-Generationen.

### 4.1 Historische BTC-Pipeline

Verifizierter Datenfluss:

```text
data/btcusdt_1m_spot_filled.csv
→ build_price_data_with_signals.py
→ data/price_data_with_signals.csv
→ tools/add_regime.py
→ data/price_data_with_signals_regime.csv
```

Verifizierte Eigenschaften:

- 2.721.034 Zeilen der zwölf binären Signalspalten wurden gegen den
  historischen Builder geprüft.
- Ergebnis: null Abweichungen.
- 1.048.575 Zeilen der vier Regimefelder wurden gegen `tools/add_regime.py`
  mit `adx_min=15.0` geprüft.
- Ergebnis: null Abweichungen.

Die historischen Signale waren:

```text
rsi_signal
macd_signal
bollinger_signal
ma200_signal
stoch_signal
atr_signal
ema50_signal
adx_signal
cci_signal
mfi_signal
obv_signal
roc_signal
```

Die historische Regimelogik war:

```text
bull:
close > ma200
ema50 > ma200
roc > 0
adx >= 15

bear:
close < ma200
ema50 < ma200
roc < 0
adx >= 15

sonst:
side
```

### 4.2 GS-Pipeline

Die spätere GS-Generation führte unter anderem ein:

- kontinuierliche Signalwerte im Bereich `[-1, +1]`;
- stärkere Trennung von Rohindikator und Signaltransformation;
- vereinfachte Regimeklassifikation;
- getrennte Felder `allow_long` und `allow_short`;
- zusätzliche Forward-Return-Felder;
- assetübergreifende Verwendung.

Der ursprüngliche BTC-GS-Datensatz ist nicht vollständig verfügbar. Deshalb
darf RCC-002 keine nicht verifizierbare Behauptung über dessen exakte
historische Erzeugung als gesicherte Tatsache behandeln.

### 4.3 Konsequenz für RCC-002

RCC-002 übernimmt weder die historische BTC-Pipeline noch die GS-Pipeline
unverändert.

Stattdessen gilt:

- Legacy-Logik wird als versionierbare Referenz erhalten.
- Neue kanonische Logik wird modular spezifiziert.
- Regime und Handels-Gates werden getrennt.
- Datenqualität und Warm-up werden explizit modelliert.
- Labels werden strikt von Live-/Paper-Features getrennt.
- jeder Build wird vollständig manifestiert.

## 5. Architekturprinzipien

### 5.1 Trennung der Verantwortlichkeiten

Jede Pipeline-Stufe besitzt genau eine primäre Verantwortung.

Eine Stufe darf keine fachlich fremde Entscheidung implizit übernehmen.

Beispiele:

- ADX darf als Rohindikator berechnet werden.
- Ob ADX einen Gate-Zustand beeinflusst, gehört in ein Gate-Profil.
- Forward Returns dürfen in S7 berechnet werden.
- Sie dürfen niemals in S0 bis S6 einfließen.

### 5.2 Determinismus

Identische Eingabebytes, identische Codeversion und identische Konfiguration
müssen dieselben semantischen Ausgaben erzeugen.

Zulässige physische Unterschiede, etwa Parquet-Metadaten oder
Kompressionsdetails, müssen durch getrennte semantische und physische Hashes
erkennbar sein.

Nichtdeterministische Operationen sind unzulässig, sofern sie nicht:

- explizit registriert,
- mit festem Seed versehen,
- vollständig manifestiert und
- durch Reproduktionstests abgesichert sind.

### 5.3 Point-in-Time-Korrektheit

Für jede Zeile mit Entscheidungszeitpunkt `t` dürfen S0 bis S6 ausschließlich
Informationen verwenden, die spätestens zu `t` verfügbar waren.

Unzulässig sind insbesondere:

- zentrierte Rolling Windows;
- rückwirkend berechnete Glättungen mit Zukunftswerten;
- Backfill aus zukünftigen Zeilen;
- interpolierte Marktwerte über Lücken;
- normalisierte Features mit Statistiken aus dem Gesamtdatensatz;
- Regimepersistenz, die zukünftige Zustände zur rückwirkenden Glättung nutzt.

### 5.4 Fail-Closed

Wenn eine Pflichtinformation ungültig, unbekannt, nicht warmgelaufen oder
nicht reproduzierbar ist, muss die betroffene Stufe fail-closed reagieren.

Für Handels-Gates bedeutet dies grundsätzlich:

```text
allow_long = 0
allow_short = 0
```

Eine Ausnahme ist nur über ein explizites, versioniertes Forschungsprofil
zulässig und darf niemals stillschweigend aktiviert werden.

### 5.5 Unveränderlichkeit und Lineage

Quellartefakte, Zwischenartefakte und veröffentlichte Datensätze dürfen nach
ihrer Veröffentlichung nicht still überschrieben werden.

Eine Korrektur erzeugt:

- ein neues versioniertes Artefakt;
- eine neue Identität;
- eine dokumentierte Eltern-Kind-Beziehung;
- einen Korrekturgrund;
- einen neuen Manifestnachweis.

### 5.6 Konfigurierbarkeit ohne implizite Semantik

Parameter müssen in versionierten Konfigurationen liegen.

Dateinamen, Verzeichnisnamen, Hostnamen oder Ausführungsreihenfolge dürfen
keine versteckte fachliche Bedeutung tragen.

Jeder Build muss mindestens folgende Identitäten referenzieren:

- Datenprofil;
- Indikatorprofil;
- Signalprofil;
- Regimeprofil;
- Gate-Profil;
- Labelprofil;
- Manifestprofil.

### 5.7 Qualitätsflag-Propagation

Qualitäts- und Gültigkeitsinformationen dürfen nicht beim Übergang zwischen
Pipeline-Stufen verloren gehen.

Jede nachgelagerte Stufe muss relevante vorgelagerte Felder entweder:

1. unverändert weiterführen oder
2. in eine dokumentierte, strengere Gültigkeitsentscheidung überführen.

Eine Stufe darf einen ungültigen oder unbekannten Eingangszustand nicht
stillschweigend als gültigen neutralen Zustand interpretieren.

## 6. Kanonischer Datenfluss

Die RCC-002-Pipeline besteht aus:

1. `S0_SOURCE`: unveränderte Quellartefakte und Quellenmanifest.
2. `S1_NORMALIZED`: kanonische Zeit-, Feld- und Typnormalisierung.
3. `S2_VALIDATED`: validierte Zeitreihe und Qualitätsflags.
4. `S3_INDICATORS`: Rohindikatoren und Qualitätsmasken.
5. `S4_SIGNALS`: versionierte Signaltransformationen.
6. `S5_REGIMES`: reine Marktklassifikationen.
7. `S6_GATES`: getrennte Handelsfreigaben und Gate-Gründe.
8. `S7_LABELS`: Forward Returns und Forschungslabels.
9. `S8_EXPORT`: konsumfertige, manifestgebundene Datensätze.

### 6.1 Verbindliche Stufenverträge

Jede Stufe muss definieren:

- akzeptierte Eingabeschemaversion;
- erzeugte Ausgabeschemaversion;
- Pflichtfelder;
- Datentypen;
- Primärschlüssel;
- Sortierungsanforderung;
- Warm-up-Regel;
- Null- und Invaliditätssemantik;
- Fehlerverhalten;
- Zeilenzahl-Invariante;
- Komponenten-ID und Komponenten-Version.

Eine Stufe darf Eingaben mit unbekannter oder inkompatibler Schemaversion
nicht stillschweigend verarbeiten.

## 7. Stufenspezifikation

### 7.1 S0_SOURCE – Rohdatenaufnahme

S0 enthält unveränderte Quellartefakte.

Pflichtanforderungen:

- Quellbytes werden nicht modifiziert.
- Für jede Quelldatei wird SHA-256 berechnet.
- Quelle, Markt, Symbol, Intervall und Abrufmethode werden dokumentiert.
- Abrufzeit und nach Möglichkeit Provider-Revisionsstand werden dokumentiert.
- Archiv- oder Kompressionsformate werden als Quellartefakt erhalten.
- Dekomprimierte Ableitungen erhalten eigene Artefaktidentitäten.

S0 muss mindestens folgende Provenienzfelder bereitstellen:

```text
source_snapshot_id
source_provider
market_type
symbol
interval
source_retrieved_at_utc
source_file_name
source_byte_sha256
source_revision
```

`source_revision` darf null sein, wenn der Provider keine Revision ausweist.
Dieser Zustand muss explizit als unbekannt markiert werden.

### 7.2 S1_NORMALIZED – Normalisierung

S1 normalisiert:

- Zeitstempel nach UTC;
- Feldnamen;
- Datentypen;
- Intervallbezeichnung;
- Markttyp;
- Symbolbezeichnung;
- numerische Darstellung.

Der kanonische Primärschlüssel lautet mindestens:

```text
market_type
symbol
interval
open_time
```

Wenn mehrere Provider innerhalb eines noch nicht konsolidierten Datensatzes
vorkommen, wird `provider` Teil des Primärschlüssels.

Für 1-Minuten-Bars gilt:

```text
close_time = open_time + 60 Sekunden - 1 Millisekunde
```

sofern die Quellsemantik dieselbe geschlossene Kerzenkonvention verwendet.

S1 darf:

- keine fehlenden Bars erzeugen;
- keine Preise interpolieren;
- keine Duplikate willkürlich entfernen;
- keine Indikatoren berechnen.

### 7.3 S2_VALIDATED – Validierung und kanonische Zeitreihe

S2 führt mindestens folgende Prüfungen aus:

- Primärschlüsseleindeutigkeit;
- strenge Sortierung;
- Intervallausrichtung;
- Zeitlückenerkennung;
- Duplikaterkennung;
- OHLC-Konsistenz;
- nichtnegative Volumina;
- endliche numerische Werte;
- Quellüberlappungen;
- Providerkonflikte;
- monotone Segmentbildung.

Die kanonische S2-Lückenpolitik lautet:

- S2 darf fehlende Markt-Bars nicht als echte OHLCV-Beobachtungen erzeugen.
- Die kanonische validierte Marktansicht bleibt beobachtungsbasiert und
  enthält ausschließlich reale oder nach einer expliziten
  Quellenkorrekturspolitik ausgewählte Quell-Bars.
- Jede zeitliche Unterbrechung erzeugt eine neue `segment_id`.
- Rolling Windows und zeitabhängige Transformationen dürfen
  Segmentgrenzen nicht überschreiten.
- Ein optionales regelmäßiges Zeitraster darf ausschließlich als getrennte
  Diagnose- oder Monitoring-View erzeugt werden.
- Synthetische Rasterzeilen müssen mindestens
  `is_observed_bar=0`, `synthetic_bar=1`,
  `market_values_valid=0` und `quality_gate_pass=0` tragen.
- Synthetische Rasterzeilen dürfen keine erfundenen OHLCV-Werte als gültige
  Marktbeobachtung ausweisen und dürfen nicht in kanonische
  Forschungs-, Backtest-, Paper- oder Live-Views gelangen.

Die S2-Ausgabe enthält mindestens:

```text
segment_id
is_observed_bar
synthetic_bar
duplicate_flag
gap_before
gap_after
ohlc_valid
volume_valid
timestamp_valid
source_conflict
market_values_valid
quality_gate_pass
quality_reason_mask
```

S2 darf Quellkonflikte nicht still durch „letzte Zeile gewinnt“ lösen.

Jede automatische Auswahlregel muss:

- explizit konfiguriert;
- deterministisch;
- manifestiert;
- separat testbar sein.

### 7.4 S3_INDICATORS – Indikatorberechnung

S3 berechnet ausschließlich Rohindikatoren und deren Gültigkeitszustände.

S3 muss:

- nur S2-freigegebene Marktwerte verwenden;
- segmentweise berechnen;
- Warm-up je Indikator explizit ausweisen;
- jeden Indikator mit eindeutiger ID und Version berechnen;
- Formeln und Parameter in der Indicator Specification referenzieren;
- numerische Bibliotheks- und Versionsabhängigkeiten dokumentieren.

S3 darf keine Handelsfreigaben oder Forward Labels erzeugen.

Für jeden Indikator `x` sind mindestens vorgesehen:

```text
x
x_valid
x_warmup_complete
x_quality_mask
```

Falls mehrere Implementierungen desselben Indikators unterstützt werden,
müssen sie unterschiedliche Komponenten-IDs besitzen.

### 7.5 S4_SIGNALS – Signaltransformation

S4 transformiert Rohindikatoren in standardisierte Signale.

RCC-002 muss mindestens zwei klar getrennte Signalprofilklassen unterstützen:

1. eine versionierte Legacy-Reproduktion binärer Signale;
2. ein kanonisches kontinuierliches Signalprofil.

Zulässiger Wertebereich kontinuierlicher Richtungssignale:

```text
-1.0 <= signal <= 1.0
```

Dabei gilt:

- `+1`: maximal bullische Ausprägung;
- `0`: neutral;
- `-1`: maximal bearische Ausprägung.

Nichtdirektionale Größen wie ATR oder ADX dürfen nicht ohne explizite
Transformation als Richtungssignal bezeichnet werden.

Ein nichtdirektionales Signal muss semantisch getrennt werden, beispielsweise:

```text
atr_quality
trend_strength
volatility_state
```

Jede Signaltransformation muss:

- kausal;
- monoton oder ausdrücklich als nichtmonoton dokumentiert;
- begrenzt;
- null- und invaliditätssicher;
- versioniert;
- unabhängig testbar sein.

### 7.6 S5_REGIMES – Marktklassifikation

S5 beschreibt den Markt, nicht die Strategieentscheidung.

Jedes Regimemodell muss:

- eine Modell-ID und Version besitzen;
- ausschließlich S0-bis-S4-Daten verwenden;
- kausal sein;
- unbekannte und ungültige Zustände explizit ausweisen;
- Rohzustand und gegebenenfalls persistierten Zustand trennen;
- seine Übergangslogik dokumentieren.

Mindestens zulässige Zustände:

```text
bull
bear
side
unknown
invalid
```

Historische BTC- und GS-Regimelogiken bleiben als reproduzierbare
Vergleichsmodelle zulässig, gelten aber nicht automatisch als RCC-002-Standard.

### 7.7 S6_GATES – Handelsfreigaben

S6 muss Marktdatenqualität und das gewählte registrierte Gate-Profil in
getrennte Long-/Short-Entscheidungsfelder überführen.

Regime-, Trendstärke-, Volatilitäts-, Liquiditäts- oder weitere
Zustandsbedingungen dürfen nur durch ein explizit registriertes und
versioniertes Gate-Profil einfließen.

Eine bloße Verfügbarkeit eines solchen Feldes erzeugt keine implizite
Gate-Bedingung.

Pflichtausgabe:

```text
allow_long
allow_short
gate_profile_id
gate_profile_version
gate_reason_mask
gate_inputs_valid
```

Dabei gilt:

- `allow_long` und `allow_short` sind getrennte Entscheidungen.
- Ein Zustand darf beide Richtungen blockieren.
- Ein Forschungsprofil darf beide Richtungen erlauben.
- Ungültige Pflichtinputs müssen fail-closed behandelt werden.
- Gate-Gründe müssen maschinenlesbar sein.
- Die Anwendung eines ausgewählten Profils muss deterministisch sein.

Mehrere Profilbedingungen dürfen zu einer Gate-Entscheidung beitragen, jedoch
nur, wenn ihre Aggregationsregel registriert, versioniert und eindeutig ist.

`model` bezeichnet in RCC-002 das S5-Regimemodell. `profile` bezeichnet die
aktive S6-Gatepolicy.

### 7.8 S7_LABELS – Forward Returns und Labels

S7 darf Zukunftsinformationen verwenden, aber ausschließlich zur Erzeugung
klar gekennzeichneter Forschungsziele.

S7-Felder müssen ein reserviertes Präfix tragen:

```text
label_
```

Mindestens vorgesehen:

```text
label_forward_return_5m
label_forward_return_15m
label_forward_return_30m
label_forward_return_60m
label_forward_return_240m
```

Optional zulässig:

```text
label_long_return_*
label_short_return_*
label_mfe_*
label_mae_*
label_barrier_*
label_outcome_*
```

S7-Felder dürfen niemals:

- in S0 bis S6 zurückpropagieren;
- in Live-/Paper-Feature-Views enthalten sein;
- für Point-in-Time-Gates verwendet werden;
- ohne explizite Forschungsfreigabe exportiert werden.

### 7.9 S8_EXPORT – Konsumartefakte

S8 erzeugt getrennte Views für:

- Research;
- Backtest;
- Paper;
- Live;
- Label Research;
- Audit und Reproduktion.

Jede View muss eine positive Feld-Allowlist besitzen.

Insbesondere darf die Live-/Paper-View keine Felder enthalten, deren Namen mit
`label_` beginnen.

## 8. Datenformate

### 8.1 Kanonisches Speicherformat

Bevorzugtes Format für große Tabellen:

```text
Parquet
```

CSV darf verwendet werden für:

- kleine Prüfextrakte;
- menschenlesbare Diagnosen;
- Legacy-Kompatibilität;
- externe Vergleichstests.

CSV darf nicht alleiniger kanonischer Speicher großer RCC-002-Datensätze sein,
wenn dadurch Datentyp-, Nullwert- oder Performanceprobleme entstehen.

### 8.2 Partitionierung

Partitionierung darf keine fachliche Semantik verändern.

Zulässige Partitionsmerkmale:

- Markt;
- Symbol;
- Intervall;
- Jahr;
- Monat;
- Pipeline-Stufe;
- Dataset-Version.

Partitionsgrenzen dürfen:

- keine Rolling-Berechnung ohne Warm-up-Kontext erzwingen;
- keine Segmentgrenzen verdecken;
- keine Zeilenreihenfolge semantisch verändern.

Partitionierte und unpartitionierte Verarbeitung müssen semantisch identische
Ergebnisse liefern.

## 9. Schema- und Namensregeln

Alle kanonischen Feldnamen verwenden:

```text
lower_snake_case
```

Zeitfelder müssen ihre Semantik erkennen lassen:

```text
open_time
close_time
event_time
available_at
generated_at
```

Boolesche Qualitätsfelder verwenden vorzugsweise:

```text
is_*
has_*
*_valid
*_complete
*_pass
```

IDs und Versionen müssen getrennt sein:

```text
component_id
component_version
schema_id
schema_version
profile_id
profile_version
```

Eine fachliche Bedeutungsänderung benötigt eine neue Komponenten- oder
Schemaversion.

## 10. Warm-up, Nullwerte und Gültigkeitsmasken

Warm-up-Zeilen dürfen nicht still als neutrale Marktzustände gelten.

Für jede abgeleitete Größe muss unterscheidbar sein:

1. gültiger numerischer Wert;
2. fachlich neutraler Wert;
3. Warm-up noch nicht abgeschlossen;
4. ungültige Eingabe;
5. Datenlücke oder Segmentgrenze;
6. Berechnungsfehler.

`NaN`, `0` und `false` dürfen nicht austauschbar verwendet werden.

Ein Vergleich mit `NaN`, der technisch `false` ergibt, darf nicht automatisch
als fachliches Signal `0` interpretiert werden.

## 11. Manifest und Provenienz

Jeder Build muss ein maschinenlesbares Manifest erzeugen.

Das Manifest enthält mindestens:

- `dataset_id`;
- `build_id`;
- Build-Zeitpunkt in UTC;
- Symbol, Markt und Intervall;
- Quellartefakte und Quellchecksummen;
- Code-Commit;
- Status des Git-Worktrees;
- Python- und Bibliotheksversionen;
- Konfigurationshashes;
- Schema- und Komponenten-Versionen;
- Zeilenanzahlen je Stufe;
- Zeitbereich je Stufe;
- Qualitätsmetriken;
- Warnungen und Fehler;
- Artefaktpfade;
- semantische und physische Hashes;
- Review- und Freigabestatus.

Das Manifest darf keine Geheimnisse enthalten.

### 11.1 Quellkorrekturen und Revisionshistorie

Wenn ein Provider historische Daten korrigiert oder ersetzt, muss die neue
Fassung:

- einen neuen `source_snapshot_id`;
- neue Quellartefakthashes;
- einen Revisionsgrund;
- eine Beziehung zur ersetzten Fassung;
- einen neuen nachgelagerten Build erzeugen.

## 12. Qualitäts-Gates

Jede Stufe besitzt ein eigenes Publication Gate.

Eine Stufe darf nur veröffentlicht werden, wenn:

- ihr Schema gültig ist;
- Pflichtfelder vollständig sind;
- Schlüssel- und Sortierungsregeln erfüllt sind;
- Zeilenzahlveränderungen erklärt sind;
- deterministische Tests bestanden wurden;
- bekannte Invaliditätszustände quantifiziert sind;
- das Manifest aktualisiert ist.

Der gesamte Dataset Build darf nur veröffentlicht werden, wenn:

1. alle Pflichtschemas erfüllt sind;
2. alle kritischen S2-Prüfungen bestanden wurden;
3. Zeilenzahlveränderungen vollständig erklärt sind;
4. keine unerlaubten Zukunftsdaten in S0 bis S6 vorkommen;
5. Warm-up- und Invalid-Zustände korrekt markiert sind;
6. Manifest und Checksummen vollständig sind;
7. ein deterministischer Vergleichsbuild bestanden wurde;
8. Live-/Paper-Allowlist keine S7-Felder enthält.

## 13. Reproduzierbarkeitsprüfungen

Mindestens erforderlich:

### R1 – Wiederholung auf demselben Gerät

Zwei Clean Builds mit identischen Inputs müssen semantisch identisch sein.

### R2 – Wiederholung auf einem zweiten Gerät

Ein zweites Gerät muss denselben semantischen Dataset-Fingerprint erzeugen.

Physische Artefakthashes dürfen nur dann abweichen, wenn die Abweichung durch
zulässige Container- oder Kompressionsdetails erklärt wird.

### R3 – Partitionierungsparität

Partitionierter und unpartitionierter Build müssen semantisch identisch sein.

### R4 – Chunking-Parität

Unterschiedliche Chunk-Größen dürfen keine fachlichen Ergebnisse verändern.

### R5 – Point-in-Time-Test

Eine Änderung an Zeilen nach Zeitpunkt `t` darf S0-bis-S6-Werte bei `t` nicht
verändern.

### R6 – Legacy-Reproduktion

Registrierte Legacy-Profile müssen die verifizierten historischen
Signal- beziehungsweise Regimeausgaben innerhalb der definierten
Vergleichsmenge reproduzieren.

## 14. Fehler- und Wiederanlaufverhalten

Ein fehlgeschlagener Build darf keine teilweise erzeugten Artefakte als final
veröffentlichen.

Erforderlich sind:

- temporäre Ausgabepfade;
- atomare Veröffentlichung;
- Stage-Status;
- Fehlerklassifikation;
- wiederaufnehmbare Stufen;
- unveränderliche veröffentlichte Artefakte;
- Quarantäne unvollständiger Ergebnisse.

Ein Resume darf nur erfolgen, wenn:

- Eingaben unverändert sind;
- Konfiguration unverändert ist;
- Codeidentität unverändert ist;
- bereits erzeugte Stufenartefakte ihre Prüfungen bestehen.

## 15. Forschungs- und Produktionsparität

Research, Backtest, Paper und Live müssen dieselben kausalen
Transformationskomponenten verwenden können.

Unterschiede dürfen nur durch explizite View- oder Profilwahl entstehen.

Beispiele:

- Research darf S7-Labels enthalten.
- Backtests dürfen Kostenmodelle ergänzen.
- Paper und Live dürfen ausschließlich explizit freigegebene Felder
  konsumieren, die in S0 bis S6 erzeugt wurden.
- Paper und Live müssen identische Feature-, Signal-, Regime- und
  Gate-Versionen verwenden, sofern kein dokumentierter A/B-Test vorliegt.

Eine separate, manuell nachgebaute Live-Indikatorlogik ist unzulässig, wenn
sie nicht automatisch gegen die kanonische Pipeline geprüft wird.

## 16. Erweiterbarkeit

Neue Assets, Intervalle oder Indikatoren dürfen die Kernverträge nicht
brechen.

Erweiterungen müssen:

- eigene Profile oder Komponenten-IDs erhalten;
- bestehende Felder nicht still umdeuten;
- Schemamigrationen dokumentieren;
- bestehende Reproduktionstests weiterhin bestehen;
- neue asset- oder intervallspezifische Warm-up-Regeln ausweisen.

Assetübertragung darf nicht als wissenschaftliche Gleichwertigkeit
missverstanden werden.

Ein für BTC definiertes Profil ist auf ETH oder andere Assets nur nach
expliziter Validierung zulässig.

## 17. Sicherheits- und Governance-Regeln

- Rohdaten und veröffentlichte Builds müssen standardmäßig schreibgeschützt
  behandelt werden.
- Kanonische Builds müssen in versionierten, schreibgeschützten Zielpfaden
  veröffentlicht werden.
- Temporäre Dateien dürfen nicht als veröffentlichte Artefakte referenziert
  werden.
- Zugangsdaten dürfen weder in Daten noch in Manifesten gespeichert werden.
- Jeder manuelle Eingriff benötigt einen Audit-Eintrag.
- Jede fachliche Regeländerung benötigt eine Versionsänderung und einen
  neuen Build.
- Ein Dataset darf nicht allein anhand eines Dateinamens als kanonisch gelten.

## 18. Abnahmekriterien für RCC-002

RCC-002 ist als Spezifikation implementierungsbereit, wenn:

1. alle nachgeordneten Spezifikationen vorliegen;
2. jede Stufe einen eindeutigen Vertrag besitzt;
3. alle mathematischen Komponenten versioniert sind;
4. Warm-up-, Invaliditäts- und Lückensemantik eindeutig sind;
5. Regime und Gate logisch getrennt sind;
6. S7-Leakage technisch ausgeschlossen ist;
7. Manifest und Identitätssystem vollständig spezifiziert sind;
8. Reproduzierbarkeitstests definiert sind;
9. Publication Gates definiert sind;
10. offene Entscheidungen entweder geschlossen oder ausdrücklich als
    Implementierungsparameter registriert sind;
11. Scientific Consistency Review bestanden ist;
12. Architecture Integrity Review bestanden ist;
13. Editorial Pass bestanden ist;
14. Internal Certification bestanden ist;
15. Claude Independent Architecture Review abgeschlossen ist;
16. Gemini Independent Scientific and Adversarial Audit abgeschlossen ist;
17. ChatGPT Final Consolidation abgeschlossen ist;
18. alle wesentlichen Befunde geschlossen sind;
19. der Status `Baseline V1 Certified` dokumentiert ist.

## 19. Nachgeordnete Spezifikationen

Verbindlich vorgesehen:

```text
RCC_002_DATA_VALIDATION_2026-07-23.md
RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md
RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md
RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md
RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
```

Diese Dokumente dürfen die hier definierten Architekturgrenzen präzisieren,
aber nicht stillschweigend verändern.

## 20. Offene Entscheidungen

Vor Status `Approved for Implementation` bleiben mindestens folgende Punkte
explizit zu schließen oder als versionierte Implementierungsprofile
festzulegen:

- kanonisches physisches Parquet-Schema;
- konkretes Partitionierungs- und Verzeichnislayout;
- Bibliotheksauswahl oder kontrollierte Eigenimplementierung je Indikator;
- konkrete Float-Toleranzen für unabhängige Referenzimplementierungen;
- JSON-Schema-Dateien und Schema-Versionsstrategie;
- technischer Build-Einstiegspunkt;
- Lockdateiformat und ausführbare Umgebungsdefinition.

Die fachlichen Regeln für Gap-Handling, Zeitsemantik, Indikatoren, Signale,
Regime, Gates, Horizonte und Kosten sind in den nachgeordneten
Spezifikationen bereits festgelegt und dürfen nicht als offene
Implementierungsentscheidung neu interpretiert werden.

## 21. Aktueller Freigabestatus

Version 0.3.0 enthielt die Korrekturen aus `RCC-002-SCR-001` für:

- SCR-B01 – kanonische S2-Lückenpolitik;
- SCR-B02 – S6-Ausgabevertrag;
- SCR-B03 – S7-Präfixvertrag.

Der Re-Review `RCC-002-SCR-002` bestätigte diese drei Befunde sowie die acht
Korrekturen der abhängigen Spezifikationen als geschlossen.

Er identifizierte für dieses Dokument:

- SCR-RR-B01 – widersprüchliche Liquiditätsverantwortung in S6;
- SCR-RR-m01 – veraltete Liste der nächsten Schritte.

Version 0.4.0 korrigiert beide Befunde:

- Marktdatenqualität und das gewählte registrierte Gate-Profil bilden den
  verpflichtenden S6-Kern.
- Regime-, Trendstärke-, Volatilitäts-, Liquiditäts- und weitere Bedingungen
  sind nur über explizit registrierte und versionierte Profile zulässig.
- Die Arbeitsfolge wurde auf den Stand nach `RCC-002-SCR-002` aktualisiert.

Der fokussierte Re-Review `RCC-002-SCR-003` bestätigte `SCR-RR-B01`,
`SCR-RR-B02` und `SCR-RR-m01` als geschlossen.

Für dieses Dokument identifizierte er `SCR-003-B01`: Die dokumentierte
Review- und Freigabesequenz wich von der verbindlichen
RCC-002-Prüfpipeline ab.

Version 0.5.0 korrigiert diesen Befund:

- Architecture Integrity Review folgt erst nach bestandenem fokussierten
  Scientific Consistency Re-Review.
- Editorial Pass folgt auf den Architecture Integrity Review.
- Internal Certification folgt auf den Editorial Pass.
- Claude Independent Architecture Review folgt auf die Internal
  Certification.
- Gemini Independent Scientific and Adversarial Audit folgt auf das
  Claude-Review.
- ChatGPT Final Consolidation folgt auf den Gemini-Audit.
- Baseline V1 Certified wird erst nach Schließung aller wesentlichen Befunde
  erreicht.
- Die Implementierung beginnt erst nach zertifizierter Baseline.

Sie ist noch nicht zur Implementierung freigegeben.

Der Status bleibt bis zum bestandenen fokussierten Scientific Consistency
Re-Review:

```text
SCR-003-Corrected Draft – Re-Review Pending
```

Nächste vorgeschriebene Schritte:

1. Korrektur von `SCR-003-B02`, `SCR-003-m01` und `SCR-003-m02` in den
   betroffenen Spezifikationen.
2. Aktualisierung aller betroffenen Dokumentversionen, Abhängigkeiten,
   Review-Nachweise und Änderungsprotokolle.
3. Neues vollständiges Spezifikationspaket aus allen sieben aktuellen
   Dokumenten.
4. Fokussierter Scientific Consistency Re-Review von `SCR-003-B01`,
   `SCR-003-B02`, `SCR-003-m01` und `SCR-003-m02` sowie ihrer Querwirkungen.
5. Architecture Integrity Review.
6. Editorial Pass.
7. Internal Certification.
8. Claude Independent Architecture Review.
9. Gemini Independent Scientific and Adversarial Audit.
10. ChatGPT Final Consolidation und Korrektur.
11. Baseline V1 Certified.
12. Implementierungsfreigabe und anschließende Implementierung, primär mit
    Claude Code.

---

# Eingebettetes Dokument 2 von 7

## Quelldatei: `RCC_002_DATA_VALIDATION_2026-07-23.md`

# RCC-002 Data Validation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-DV |
| Titel | Data Validation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Dateiname | `RCC_002_DATA_VALIDATION_2026-07-23.md` |
| Version | 0.2.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.5.0 |
| Geltungsbereich | S0_SOURCE, S1_NORMALIZED und S2_VALIDATED der RCC-002-Datenpipeline |
| Referenziert durch | RCC-002-Implementierung; Dataset Manifest; Pipeline Quality Gates; Reproduzierbarkeitsprüfung |
| Autoritative Sprache | Englisch für Code, Schemas, Feldnamen und Fehlercodes; Deutsch für normative Erläuterungen |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Interne Strukturprüfung | Bestanden | Kapitel, Nummerierung und Querverweise konsistent |
| Methodische Konsistenzprüfung | Bestanden | Fail-closed, Point-in-Time-Korrektheit und Lineage durchgängig berücksichtigt |
| Regelkonfliktprüfung | Bestanden | Duplikat-, Lücken-, Korrektur- und Veröffentlichungsregeln eindeutig priorisiert |
| Vollständigkeitsprüfung | Bestanden | Datei-, Schema-, Zeitachsen-, OHLCV-, Qualitäts- und Reconciliation-Prüfungen enthalten |
| Scientific Consistency Review | Nicht bestanden; Korrektur eingearbeitet | `SCR-003-B02` aus `RCC-002-SCR-003` in Version 0.2.0 korrigiert; fokussierter Re-Review ausstehend |

## 1. Zweck

Dieses Dokument definiert die verbindliche Validierung von Roh- und
normalisierten Marktdaten innerhalb der RCC-002-Datenpipeline.

Ziel ist nicht, Marktdaten nachträglich plausibel erscheinen zu lassen, sondern:

- technische Beschädigungen sicher zu erkennen,
- beobachtete Marktereignisse von Datenfehlern zu unterscheiden,
- jede Korrektur oder Ableitung nachvollziehbar zu machen,
- unerklärte Zeilenverluste und Trunkierungen auszuschließen,
- eine belastbare Grundlage für Indikatoren, Signale, Regime und Labels zu
  schaffen.

Keine nachgelagerte Strategie- oder Modellqualität kann Fehler in S0 bis S2
kompensieren. Deshalb arbeitet diese Validierung bei strukturellen und
semantischen Kernfehlern standardmäßig fail-closed.

## 2. Normative Begriffe

`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` und `MAY` besitzen dieselbe normative
Bedeutung wie im übergeordneten RCC-002-Dokument.

Zusätzlich gelten:

- **Beobachtete Kerze:** direkt aus einer dokumentierten Quelle übernommene
  Marktbeobachtung.
- **Synthetische Kerze:** deterministisch erzeugte Ersatzzeile ohne direkte
  Marktbeobachtung.
- **Lücke:** mindestens ein erwarteter Zeitindex ohne beobachtete Kerze.
- **Identisches Duplikat:** mehrere Zeilen mit demselben kanonischen Schlüssel
  und identischem kanonischem Inhalt.
- **Konfligierendes Duplikat:** mehrere Zeilen mit demselben kanonischen
  Schlüssel, aber unterschiedlichen kanonischen Werten.
- **Kanonischer Build:** vollständig validierter, manifestgebundener und
  veröffentlichter Pipeline-Build.
- **Quarantäne:** isolierter Zustand für fehlerhafte oder ungeklärte Artefakte,
  die nicht nachgelagert konsumiert werden dürfen.

## 3. Validierungsgrundsätze

### 3.1 Keine stille Reparatur

RCC-002 MUST NOT:

- ungültige Werte still ersetzen,
- konflikthafte Duplikate willkürlich auswählen,
- Lücken ohne Kennzeichnung füllen,
- Zeitstempel ohne protokollierte Regel verschieben,
- Zeilen ohne dokumentierten Reason Code entfernen,
- numerische Parsing-Fehler in Nullwerte umwandeln.

### 3.2 Beobachtung und Interpretation trennen

Ungewöhnliche, aber technisch mögliche Marktwerte dürfen nicht allein aufgrund
statistischer Auffälligkeit gelöscht werden.

Beispielsweise können folgende Werte reale Marktereignisse darstellen:

- sehr große Returns,
- extremes Volumen,
- lange Kerzen,
- sprunghafte Volatilität,
- Nullvolumen in einzelnen Intervallen.

Solche Werte werden geprüft und gegebenenfalls markiert. Automatische
Verwerfung ist nur bei einer objektiv verletzten Invariante zulässig.

### 3.3 Unveränderliche Rohdaten

S0-Artefakte MUST byteweise unverändert bleiben. Normalisierung, Deduplizierung
oder Typkonvertierung erfolgt ausschließlich in neu erzeugten S1-Artefakten.

### 3.4 Vollständige Reconciliation

Jede Veränderung von:

- Dateizahl,
- Bytezahl,
- Zeilenzahl,
- Zeitbereich,
- Spaltenzahl,
- Nullwertzahl

MUST zwischen den Pipeline-Stufen erklärt und im Manifest dokumentiert werden.

### 3.5 Validierungsreihenfolge

Prüfungen MUST in dieser Reihenfolge erfolgen:

1. Artefakt- und Dateiintegrität.
2. Parsing und Basisschema.
3. Datentypen und kanonische Schlüssel.
4. Zeitachse und Abdeckung.
5. Duplikate und Quellkollisionen.
6. OHLCV-Invarianten.
7. Plausibilitäts- und Anomalieflags.
8. Reconciliation.
9. Publication Gate.

Spätere Prüfungen dürfen einen früheren kritischen Fehler nicht überschreiben.

## 4. Validierungsprofile

RCC-002 definiert drei Profile.

### 4.1 `SOURCE_AUDIT`

Zweck:

- unveränderte S0-Artefakte inventarisieren,
- Dateivollständigkeit und Checksummen prüfen,
- Quellmetadaten erfassen.

Dieses Profil verändert keine Daten.

### 4.2 `CANONICAL_BUILD`

Zweck:

- S1 normalisieren,
- S2 validieren,
- kanonische beobachtete Marktzeitreihe erzeugen.

Dieses Profil ist streng. Kritische Fehler blockieren den Build.

### 4.3 `DIAGNOSTIC_RESEARCH`

Zweck:

- ungeklärte oder historische Legacy-Dateien untersuchen,
- Fehlerverteilung und Rekonstruktionsmöglichkeiten analysieren.

Ausgaben dieses Profils MUST als nichtkanonisch markiert werden und dürfen
nicht versehentlich als Produktions- oder Referenzdaten dienen.

## 5. Eingabevertrag

### 5.1 Mindestmetadaten je Quelle

Vor dem Parsing MUST mindestens bekannt sein:

| Feld | Anforderung |
|---|---|
| `provider` | Datenanbieter, z. B. Binance |
| `market_type` | z. B. Spot oder Futures |
| `symbol` | z. B. BTCUSDT |
| `interval` | z. B. `1m` |
| `timezone` | Quellzeitzone; kanonisch später UTC |
| `expected_start` | erwarteter erster Intervallbeginn |
| `expected_end` | erwarteter letzter Intervallbeginn |
| `retrieved_at_utc` | Abrufzeitpunkt |
| `source_format` | Dateityp und Schemafamilie |
| `source_location` | dokumentierte Herkunft |
| `license_or_terms_ref` | Referenz auf Nutzungsbedingungen, sofern relevant |

Fehlende Identitäts- oder Zeitmetadaten blockieren `CANONICAL_BUILD`.

### 5.2 Erwartetes Quelldateiinventar

Bei monatlich oder täglich partitionierten Quellen MUST vor dem Einlesen eine
erwartete Dateiliste erzeugt werden.

Für jede erwartete Periode werden erfasst:

- erwarteter Dateiname,
- vorhanden/nicht vorhanden,
- Dateigröße,
- Quellchecksumme, falls angeboten,
- lokal berechnete Checksumme,
- Downloadstatus,
- Extraktionsstatus.

Eine fehlende erwartete Partition ist mindestens `ERROR`. Sie wird erst dann
auf `WARN` herabgestuft, wenn die Quelle für diesen Zeitraum nachweislich keine
Daten bereitstellt und dies als genehmigte Ausnahme dokumentiert wurde.

## 6. Dateiintegrität

### 6.1 Zulässige Dateizustände

Jedes S0-Artefakt erhält genau einen Zustand:

- `RECEIVED_UNVERIFIED`,
- `VERIFIED`,
- `MISSING`,
- `CORRUPT`,
- `CHECKSUM_MISMATCH`,
- `EXTRACTION_FAILED`,
- `QUARANTINED`.

Nur `VERIFIED` darf regulär in S1 eingehen.

### 6.2 Pflichtprüfungen

Für jede Datei MUST geprüft werden:

- Datei existiert,
- Datei ist regulär lesbar,
- Größe ist größer als null,
- Format oder Archiv kann geöffnet werden,
- erwartete interne Datei ist vorhanden,
- Header ist vorhanden und parsebar,
- lokale SHA-256-Checksumme wurde berechnet,
- angebotene Anbieterchecksumme stimmt, sofern verfügbar,
- keine unerwarteten zusätzlichen Nutzdaten wurden still übernommen.

### 6.3 Spreadsheet-Grenzprüfung

Tabellen mit folgenden verdächtigen Zeilenzahlen MUST einen speziellen
Trunkierungsbefund erzeugen:

- 65.535 Datenzeilen plus Kopfzeile,
- 1.048.575 Datenzeilen plus Kopfzeile,
- andere bekannte Format- oder Toolgrenzen.

Der Fehlercode lautet:

`DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`.

Bei einer vorgelagerten Datei mit mehr Zeilen oder einem erwarteten längeren
Zeitbereich ist dieser Befund `CRITICAL`.

XLSX, XLS und ODS sind als kanonische S0-bis-S2-Transformationsformate
unzulässig.

## 7. Parsing und kanonisches Schema

### 7.1 Pflichtfelder

Das S1-Mindestschema lautet:

| Feld | Kanonischer Typ | Null zulässig |
|---|---|---:|
| `open_time` | UTC timestamp oder `int64` UTC epoch | nein |
| `close_time` | UTC timestamp oder `int64` UTC epoch | nein |
| `open` | `float64` | nein |
| `high` | `float64` | nein |
| `low` | `float64` | nein |
| `close` | `float64` | nein |
| `volume` | `float64` | nein |
| `quote_volume` | `float64` | ja, wenn Quelle nicht liefert |
| `trade_count` | nullable `int64` | ja, wenn Quelle nicht liefert |
| `source_id` | string | nein |
| `source_row_id` | string oder `int64` | nein |

### 7.2 Numerisches Parsing

Numerische Felder MUST:

- ohne localeabhängige Mehrdeutigkeit gelesen werden,
- `NaN`, `+Inf` und `-Inf` erkennen,
- ungültige Zeichenfolgen als Parsing-Fehler melden,
- ohne vorherige Rundung in den kanonischen Typ überführt werden.

Ein Parsing-Fehler in einem OHLCV-Pflichtfeld ist `CRITICAL`.

### 7.3 Zusätzliche Quellfelder

Zusätzliche Felder MAY erhalten bleiben, wenn:

- ihre Semantik dokumentiert ist,
- sie einen registrierten kanonischen Namen erhalten,
- sie keine Pflichtfelder überschreiben,
- Datentyp und Nullsemantik definiert sind.

Nicht registrierte Zusatzfelder MUST im Schema-Report erscheinen.

### 7.4 Schema-Fingerprint

Jedes S1- und S2-Artefakt MUST einen Schema-Fingerprint besitzen, der mindestens
berücksichtigt:

- geordnete Feldnamen,
- Datentypen,
- Nullzulässigkeit,
- Primärschlüssel,
- Schemaversion.

## 8. Zeitsemantik

### 8.1 Kanonische Zeitzone

Alle kanonischen Zeitstempel MUST UTC darstellen. Naive Zeitstempel ohne
nachweisbare Quellzeitzone sind für `CANONICAL_BUILD` unzulässig.

### 8.2 Kerzenidentität

Der kanonische Primärschlüssel einer Einzelasset-Zeitreihe lautet:

`(market_type, symbol, interval, open_time)`.

Bei Multi-Provider-Daten kommt `provider` hinzu, solange noch keine
freigegebene Konsolidierung erfolgt ist.

### 8.3 Intervallausrichtung

Für BTCUSDT `1m` gilt:

- `open_time` liegt exakt auf einer UTC-Minute,
- aufeinanderfolgende erwartete `open_time`-Werte unterscheiden sich um
  60 Sekunden,
- `close_time` entspricht der dokumentierten Anbietersemantik,
- eine abweichende Endzeitkonvention wird normalisiert, aber nicht geraten.

Die allgemeine Regel lautet:

`open_time % interval_duration == 0`

für epochbasierte Zeitstempel.

### 8.4 Entscheidungszeitpunkt

S2 MUST unterscheiden:

- Intervallbeginn,
- Intervallende,
- Zeitpunkt, zu dem eine geschlossene Kerze verfügbar ist.

Indikatoren oder Signale für Kerze `t` dürfen im späteren Handel erst nach dem
definierten Verfügbarkeitszeitpunkt dieser Kerze verwendet werden.

### 8.5 Sortierung

S1 und S2 MUST nach dem vollständigen kanonischen Schlüssel aufsteigend
sortiert sein.

Unsortierte Quelldaten dürfen in S1 deterministisch sortiert werden, sofern:

- die ursprüngliche Reihenfolge über `source_row_id` erhalten bleibt,
- der Befund protokolliert wird,
- keine konflikthaften Schlüssel verdeckt werden.

## 9. Abdeckung und erwartete Zeilenzahl

### 9.1 Inklusive Grenzen

Wenn `expected_start` und `expected_end` jeweils Intervallbeginne und beide
inklusive sind, lautet die erwartete Zeilenzahl:

`expected_rows = ((expected_end - expected_start) / interval_duration) + 1`

Die Division MUST ohne Rest aufgehen.

### 9.2 Pflichtvergleich

Für jede Stufe werden dokumentiert:

- erwartete Zeilen,
- gelesene Zeilen,
- parsebare Zeilen,
- eindeutige Schlüssel,
- ausgegebene Zeilen,
- erste und letzte Zeit,
- fehlende Intervalle,
- zusätzliche Intervalle außerhalb des erwarteten Bereichs.

### 9.3 Bereichsüberschreitung

Zeilen vor `expected_start` oder nach `expected_end` dürfen nicht still
verworfen werden.

Sie werden:

- bei falscher Konfiguration als Konfigurationsfehler behandelt oder
- bei unerwarteten Quelldaten separat ausgewiesen und quarantänisiert.

## 10. Duplikate und Quellkollisionen

### 10.1 Identische Duplikate

Identische Duplikate MAY in S1 deterministisch auf eine Zeile reduziert werden,
wenn:

- alle kanonischen Werte identisch sind,
- alle Quellreferenzen erhalten bleiben,
- Anzahl und Zeitpunkte protokolliert werden,
- die Deduplizierungsregel versioniert ist.

Der Reason Code lautet:

`DV_DUPLICATE_IDENTICAL_COLLAPSED`.

### 10.2 Konfligierende Duplikate

Konfligierende Duplikate sind in `CANONICAL_BUILD` `CRITICAL`.

Sie dürfen nur durch eine separat genehmigte, deterministische
Quellenprioritätsregel aufgelöst werden. Diese Regel MUST dokumentieren:

- bevorzugte Quelle,
- Begründung,
- Vergleichsfelder,
- verworfene Werte,
- betroffene Zeitpunkte,
- Regelversion.

Ohne diese Regel bricht der Build ab.

### 10.3 Überlappende Partitionen

Überlappungen zwischen Tages-, Monats- oder Update-Dateien werden vor einer
Deduplizierung vollständig gezählt und klassifiziert.

Eine typische Update-Überlappung gilt nicht automatisch als harmlos; ihre Werte
müssen identisch sein oder nach einer genehmigten Revisionsregel verarbeitet
werden.

## 11. Lückenerkennung

### 11.1 Definition

Eine Lücke liegt vor, wenn zwischen zwei gültigen kanonischen Schlüsseln
mindestens ein erwarteter Intervallbeginn fehlt.

Für jede Lücke MUST erfasst werden:

- `gap_start`,
- `gap_end`,
- `missing_intervals`,
- vorherige und nächste vorhandene Kerze,
- betroffene Quellpartitionen,
- bekannte Anbieter- oder Marktereignisse,
- Klassifikation,
- Genehmigungsstatus.

### 11.2 Lückenklassen

Zulässige Klassen:

- `SOURCE_FILE_MISSING`,
- `SOURCE_ROW_MISSING`,
- `PROVIDER_OUTAGE_CONFIRMED`,
- `MARKET_NOT_AVAILABLE`,
- `PARSING_LOSS`,
- `FILTERING_LOSS`,
- `UNKNOWN`.

`PARSING_LOSS`, `FILTERING_LOSS` und `UNKNOWN` sind im kanonischen
Publication Gate mindestens `ERROR`; ungeklärte systematische Lücken sind
`CRITICAL`.

### 11.3 Kanonische Lückenpolitik

Der kanonische beobachtete S2-Datensatz MUST ausschließlich beobachtete Kerzen
enthalten. Fehlende Marktbeobachtungen werden nicht im selben Artefakt durch
synthetische Kerzen ersetzt.

Damit bleiben:

- tatsächlich beobachtete Daten,
- diagnostizierte Lücken,
- optionale Kontinuitätsableitungen

fachlich getrennt.

### 11.4 Optionale Kontinuitätsansicht

Eine separate synthetisch vervollständigte Ansicht MAY erzeugt werden, wenn ein
nachgelagerter Algorithmus eine regelmäßige Zeitachse zwingend benötigt.

Dann gelten mindestens:

- eigener Artefaktname und eigene View-ID,
- `quality_is_synthetic = true`,
- `quality_gap_id`,
- dokumentierte Erzeugungsregel,
- keine Überschreibung beobachteter Kerzen,
- Ausschluss aus kanonischen Returns und Labels als Standard,
- gesonderte Sensitivitätsanalyse.

Eine übliche synthetische OHLC-Regel wie
`open = high = low = close = previous_close` und `volume = 0` ist erst nach
separater Freigabe zulässig; dieses Dokument genehmigt sie nicht automatisch.

## 12. OHLCV-Invarianten

### 12.1 Harte Preisregeln

Für jede beobachtete Kerze MUST gelten:

- `open > 0`,
- `high > 0`,
- `low > 0`,
- `close > 0`,
- `high >= open`,
- `high >= close`,
- `high >= low`,
- `low <= open`,
- `low <= close`.

Eine Verletzung ist `CRITICAL`.

### 12.2 Volumenregeln

MUST gelten:

- `volume >= 0`,
- `quote_volume >= 0`, sofern vorhanden,
- `trade_count >= 0`, sofern vorhanden,
- `trade_count` ist ganzzahlig.

Negatives Volumen oder negativer Trade Count ist `CRITICAL`.

Nullvolumen ist nicht automatisch ungültig, erzeugt aber:

`DV_VOLUME_ZERO_OBSERVED`.

Häufigkeit, zeitliche Cluster und Zusammenhang mit Lücken oder
Anbieterstörungen MUST im Report erscheinen.

### 12.3 Optionale Konsistenzprüfungen

Wenn die Quelle zusätzliche Felder liefert, SHOULD geprüft werden:

- `quote_volume` gegenüber Preis- und Basisvolumengrößenordnung,
- Taker-Buy-Volumen gegen Gesamtvolumen,
- Trade Count gegen Nullvolumen,
- Anbieter-ID oder Sequenznummer auf Kontinuität.

Diese Prüfungen dürfen ohne belastbare exakte Invariante zunächst Warnungen
erzeugen, aber keine realen Marktdaten automatisch löschen.

## 13. Anomalieerkennung

### 13.1 Zweck

Anomalieerkennung dient der Untersuchung, nicht der stillen Datenbereinigung.

### 13.2 Mindestflags

S2 SHOULD mindestens erzeugen:

- extreme absolute Kerzenrendite,
- extreme High-Low-Range,
- extremes Volumen,
- ungewöhnlich langer Nullvolumen-Cluster,
- identische OHLC-Werte über ungewöhnlich viele Kerzen,
- Preis- oder Volumensprung an Partitionsgrenzen.

### 13.3 Schwellenwerte

Schwellenwerte MUST:

- robust und kausal berechnet werden,
- pro Asset und Intervall konfiguriert sein,
- ihre Warm-up-Periode ausweisen,
- nicht aus dem späteren Testzeitraum optimiert werden.

Anomalieflags dürfen die Originalwerte nicht verändern.

### 13.4 Externe Bestätigung

Bei kritischen Auffälligkeiten MAY eine unabhängige Quelle zur Bestätigung
verwendet werden.

Die externe Quelle, der Vergleichszeitpunkt und das Ergebnis werden im
Validierungsreport dokumentiert. Ein externer Vergleich ersetzt nicht die
Lineage der Primärquelle.

## 14. Nullwerte und fehlende Werte

### 14.1 Pflichtfelder

Nullwerte in Primärschlüssel-, Zeit- oder OHLCV-Pflichtfeldern sind
`CRITICAL`.

### 14.2 Optionale Felder

Nullwerte in optionalen Quellfeldern sind zulässig, wenn:

- die Quelle das Feld für den gesamten Datensatz nicht liefert oder
- die Nullsemantik explizit dokumentiert ist.

Mischungen aus vorhandenen und fehlenden Werten müssen gezählt und untersucht
werden.

### 14.3 Kein implizites Auffüllen

Forward Fill, Backward Fill, Mittelwert-Imputation oder Nullersetzung sind in
S1 und im kanonischen beobachteten S2-Artefakt verboten.

## 15. Qualitätsfelder

S2 MUST mindestens folgende Qualitätsinformationen bereitstellen:

| Feld | Bedeutung |
|---|---|
| `quality_is_observed` | Zeile stammt aus einer beobachteten Quellkerze |
| `quality_is_synthetic` | Zeile wurde synthetisch erzeugt |
| `quality_has_source_conflict` | Quellkollision vorhanden |
| `quality_gap_before` | Mindestens ein erwartetes Intervall vor dieser Zeile fehlt |
| `quality_gap_after` | Mindestens ein erwartetes Intervall nach dieser Zeile fehlt |
| `quality_anomaly_flags` | maschinenlesbare Anomaliecodes |
| `quality_status` | aggregierter Status |
| `quality_rule_version` | Version der angewandten Qualitätsregeln |

Für den kanonischen beobachteten S2-Datensatz gilt:

- `quality_is_observed = true`,
- `quality_is_synthetic = false`.

Nachgelagerte Rolling-Berechnungen müssen zusätzlich erkennen können, ob ihr
Eingabefenster eine Lückengrenze überschreitet.

## 16. Severity- und Reason-Code-System

### 16.1 Severity

| Severity | Bedeutung | Buildwirkung |
|---|---|---|
| `INFO` | dokumentierter Normalzustand | keine Blockierung |
| `WARN` | Auffälligkeit ohne nachgewiesene Integritätsverletzung | Veröffentlichung möglich, wenn akzeptiert |
| `ERROR` | relevante Qualitätsverletzung | Veröffentlichung standardmäßig blockiert |
| `CRITICAL` | strukturelle oder semantische Kernverletzung | sofortiger Abbruch oder Quarantäne |

### 16.2 Reason-Code-Regeln

Jeder Reason Code MUST:

- stabil und maschinenlesbar sein,
- mit `DV_` beginnen,
- genau eine primäre Bedeutung besitzen,
- eine Standard-Severity besitzen,
- betroffene Artefakte und Zeilen referenzieren können.

Mindestcodes:

- `DV_FILE_MISSING`,
- `DV_FILE_EMPTY`,
- `DV_FILE_CORRUPT`,
- `DV_CHECKSUM_MISMATCH`,
- `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`,
- `DV_SCHEMA_REQUIRED_COLUMN_MISSING`,
- `DV_SCHEMA_UNEXPECTED_COLUMN`,
- `DV_PARSE_TIMESTAMP_FAILED`,
- `DV_PARSE_NUMERIC_FAILED`,
- `DV_TIME_NOT_UTC`,
- `DV_TIME_MISALIGNED`,
- `DV_TIME_OUT_OF_RANGE`,
- `DV_DUPLICATE_IDENTICAL_COLLAPSED`,
- `DV_DUPLICATE_CONFLICT`,
- `DV_GAP_DETECTED`,
- `DV_GAP_UNEXPLAINED`,
- `DV_OHLC_INVARIANT_FAILED`,
- `DV_VOLUME_NEGATIVE`,
- `DV_VOLUME_ZERO_OBSERVED`,
- `DV_ROW_RECONCILIATION_FAILED`,
- `DV_SCHEMA_FINGERPRINT_MISMATCH`.

## 17. Reconciliation zwischen Stufen

### 17.1 S0 zu S1

MUST dokumentiert werden:

`source_rows = parsed_rows + rejected_rows`

und:

`parsed_rows = normalized_rows + duplicate_rows_removed + out_of_scope_rows`

Jeder Summand benötigt eine nichtnegative Ganzzahl und gegebenenfalls
Reason-Code-Aufschlüsselung.

### 17.2 S1 zu S2

Standardmäßig gilt:

`s2_observed_rows = s1_unique_valid_rows`

Abweichungen sind nur zulässig, wenn jede betroffene Zeile mit Reason Code und
Quellreferenz dokumentiert ist.

### 17.3 Zeitachsen-Reconciliation

MUST gelten:

`expected_intervals = observed_unique_intervals + missing_intervals`

für den definierten inklusiven Zeitraum.

Zusätzliche Intervalle außerhalb des Zeitraums werden separat gezählt und
dürfen die Gleichung nicht verdecken.

## 18. Inkrementelle Aktualisierung

### 18.1 Source Snapshot

Jede Aktualisierung erzeugt einen neuen unveränderlichen Source Snapshot.

### 18.2 Überlappungsfenster

Ein inkrementeller Download SHOULD ein konfiguriertes Überlappungsfenster mit
dem bisherigen Ende enthalten, um:

- nachträgliche Anbieteränderungen,
- unvollständige letzte Partitionen,
- Downloadgrenzen

zu erkennen.

### 18.3 Revisionsvergleich

Überlappende Schlüssel werden feldweise verglichen.

Bei Änderungen MUST dokumentiert werden:

- alter Wert,
- neuer Wert,
- Quelle und Abrufzeit beider Versionen,
- Anzahl betroffener Kerzen,
- frühester und spätester Änderungszeitpunkt,
- Rebuild-Reichweite.

Eine Änderung bestehender Quelldaten erzeugt einen neuen Build; der alte Build
bleibt unverändert.

### 18.4 Unvollständige laufende Kerzen

Noch nicht abgeschlossene Kerzen dürfen nicht in einen kanonischen historischen
S2-Build aufgenommen werden.

Der Abschlussstatus richtet sich nach der dokumentierten
Provider-Zeitsemantik, nicht allein nach lokalem Empfang.

## 19. Validierungsoutputs

Jeder Lauf MUST mindestens erzeugen:

1. `validation_summary.json`
2. `validation_findings.csv` oder gleichwertiges Parquet-Artefakt
3. `gap_report.csv`
4. `duplicate_report.csv`
5. `schema_report.json`
6. `row_reconciliation.json`
7. `source_inventory.json`
8. aktualisierten Manifestabschnitt

### 19.1 `validation_summary.json`

Mindestfelder:

- `validation_run_id`,
- `build_id`,
- `profile`,
- `rule_version`,
- `started_at_utc`,
- `completed_at_utc`,
- `status`,
- Findings je Severity,
- erste und letzte Zeit,
- erwartete und tatsächliche Zeilen,
- Lückenanzahl und fehlende Intervalle,
- Duplikatanzahl nach Klasse,
- synthetische Zeilen,
- Schema-Fingerprint,
- Artefaktchecksummen.

### 19.2 Findings

Jedes Finding enthält:

- `finding_id`,
- `reason_code`,
- `severity`,
- `stage`,
- `artifact_id`,
- optionalen Zeilen- oder Zeitbezug,
- beobachteten Wert,
- erwartete Regel,
- Status,
- genehmigte Ausnahme,
- Auflösungsreferenz.

## 20. Publication Gate

Ein S2-Artefakt darf nur als kanonisch veröffentlicht werden, wenn:

1. alle erwarteten S0-Partitionen vorhanden oder genehmigt ausgenommen sind;
2. alle verwendeten S0-Dateien `VERIFIED` sind;
3. Pflichtschema und Datentypen vollständig stimmen;
4. Zeitstempel UTC, eindeutig und korrekt ausgerichtet sind;
5. keine ungeklärten konflikthaften Duplikate bestehen;
6. keine harte OHLCV-Invariante verletzt ist;
7. alle Lücken vollständig inventarisiert und klassifiziert sind;
8. keine synthetische Zeile im beobachteten kanonischen Artefakt enthalten ist;
9. Reconciliation-Gleichungen exakt erfüllt sind;
10. Startzeit, Endzeit und Zeilenzahl mit dem Manifest übereinstimmen;
11. Schema- und Artefaktchecksummen erzeugt wurden;
12. kein nicht genehmigtes `ERROR` oder `CRITICAL` offen ist.

Der Gate-Status lautet genau:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` benötigt eine versionierte
Ausnahmeentscheidung mit Verantwortlichem, Begründung und Geltungsbereich.

## 21. Testanforderungen

### 21.1 Unit Tests

Mindestens erforderlich:

- gültige Einzelkerze;
- jede OHLC-Verletzung separat;
- negative und null Volumina;
- ungültige numerische Werte;
- UTC- und Alignment-Fälle;
- identische und konflikthafte Duplikate;
- Einzel- und Mehrfachlücken;
- inklusive Zeilenzahlformel;
- Spreadsheet-Zeilenlimit-Erkennung;
- Schema-Fingerprint;
- Reason-Code- und Severity-Mapping.

### 21.2 Property-Based Tests

SHOULD geprüft werden:

- Sortierung verändert keine eindeutigen Inhalte;
- Deduplizierung identischer Zeilen ist idempotent;
- erneute Validierung eines unveränderten S2-Artefakts erzeugt identische
  Ergebnisse;
- Reconciliation bleibt für zufällige gültige Zeitreihen erfüllt;
- eingefügte Lücken werden vollständig und exakt erkannt.

### 21.3 Golden Fixtures

Es MUST kleine versionierte Referenzdatensätze geben für:

- vollständig gültige Zeitreihe;
- jede kritische Fehlerklasse;
- genehmigte Provider-Lücke;
- Partition mit Überlappung;
- historische Excel-Trunkierung;
- inkrementelle Quellrevision.

Erwartete Reports und Exit-Codes werden gemeinsam mit den Fixtures versioniert.

### 21.4 Integration Tests

Mindestens erforderlich:

- vollständiger S0-bis-S2-Minibuild;
- Abbruch bei korrupter Partition;
- Abbruch bei konflikthaftem Duplikat;
- erfolgreicher Build mit identischem Duplikat und vollständiger Lineage;
- erfolgreicher beobachteter Build mit dokumentierter Lücke;
- getrennte Erzeugung einer optionalen synthetischen Kontinuitätsansicht;
- deterministischer Wiederholungsbuild.

## 22. Legacy-Validierung

### 22.1 Historische Signaldatei

Die verifizierte Übereinstimmung der zwölf Signalregeln über 2.721.034 Zeilen
belegt die Signaltransformation, nicht automatisch:

- vollständige Rohdatenabdeckung;
- fehlerfreie Zeitachse;
- korrekte Warm-up-Behandlung;
- Abwesenheit von Quelllücken.

Diese Punkte müssen bei einer Legacy-Reproduktion separat geprüft werden.

### 22.2 Historische Regimedatei

Die null Regelabweichungen über 1.048.575 Datenzeilen bestätigen die
Regimeberechnung innerhalb des vorhandenen Ausschnitts.

Die exakte Zeilenzahl an der Excel-Grenze und die längere vorgelagerte
Signaldatei erzwingen jedoch:

- Status `NON_CANONICAL_LEGACY_ARTIFACT`;
- Finding `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION`;
- keine Verwendung als vollständige RCC-002-Referenz;
- reproduzierbaren Neubau der Regimefelder aus einer vollständigen validierten
  Eingabe.

### 22.3 Legacy-Vergleich

RCC-002 MUST Legacy-Ergebnisse nicht durch Überschreiben historischer Dateien
„reparieren“.

Stattdessen werden getrennt erhalten und vergleichend dokumentiert:

- Originalartefakt;
- rekonstruierter Legacy-Build;
- neuer RCC-002-Build.

## 23. Implementierungsanforderungen

Die Implementierung MUST:

- als eigenständig testbare Module strukturiert sein;
- Konfigurationen statt fest codierter Projektpfade verwenden;
- atomar schreiben;
- temporäre Dateien nach Fehlern eindeutig markieren;
- strukturierte Exit-Codes liefern;
- keine Warnung ausschließlich als Terminaltext verlieren;
- bei kritischen Fehlern einen von null verschiedenen Exit-Code liefern;
- Reports vor einem kontrollierten Abbruch vollständig schreiben, soweit
  technisch sicher möglich;
- existierende kanonische Artefakte nicht still überschreiben.

Die Implementierung SHOULD Streaming oder partitionierte Verarbeitung
unterstützen, ohne dass sich Validierungsregeln gegenüber einem vollständigen
In-Memory-Build ändern.

## 24. Abnahmekriterien

`RCC_002_DATA_VALIDATION` ist implementierungsreif, wenn:

1. alle Regeln in maschinenlesbare Prüfverträge überführt sind;
2. alle Reason Codes registriert sind;
3. Severity und Buildwirkung eindeutig sind;
4. Golden Fixtures vollständig vorliegen;
5. Unit-, Property- und Integrationstests bestanden sind;
6. die BTCUSDT-1m-Rohdaten vollständig inventarisiert wurden;
7. erwartete Zeilenzahl und Zeitabdeckung unabhängig verifiziert wurden;
8. die Legacy-Trunkierung reproduzierbar erkannt wird;
9. ein deterministischer S0-bis-S2-Vollbuild auf der Workstation bestanden ist;
10. Manifest und Reconciliation ohne offene Fehler vollständig sind.

## 25. Offene Implementierungsparameter

Folgende Werte werden erst in der versionierten Konfiguration festgelegt:

- exakter kanonischer UTC-Timestamp-Typ;
- Parquet-Kompression und Row-Group-Größe;
- Partitionsgröße;
- Länge des inkrementellen Überlappungsfensters;
- statistische Schwellenwerte für nicht destruktive Anomalieflags;
- zulässige genehmigte Provider-Ausnahmen;
- Aufbewahrungsdauer temporärer und quarantänisierter Artefakte.

Diese Parameter dürfen die normativen Invarianten dieses Dokuments nicht
abschwächen.

## 26. Freigabestatus und nächster Schritt

Diese Spezifikation wurde vor ihrer ersten Ausgabe intern auf methodische,
logische, strukturelle und terminologische Konsistenz geprüft.

Der fokussierte Re-Review `RCC-002-SCR-003` identifizierte
`SCR-003-B02`: Die Metadaten referenzierten weiterhin Data Pipeline
Version 0.2.0, obwohl eine neuere übergeordnete Spezifikation maßgeblich war.

Version 0.2.0 korrigiert die übergeordnete Abhängigkeit auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.5.0
```

Die fachlichen Validierungsregeln wurden dabei nicht verändert.

Sie ist noch nicht wissenschaftlich zertifiziert. Der Status bleibt:

```text
SCR-003-Corrected Draft – Re-Review Pending
```

Nächster fachlicher Schritt:

Fokussierter Scientific Consistency Re-Review von `SCR-003-B02` gemeinsam
mit der vollständigen korrigierten RCC-002-Spezifikationsfamilie.

---

# Eingebettetes Dokument 3 von 7

## Quelldatei: `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`

# RCC-002 Indicator Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-IS |
| Titel | Indicator Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Version | 0.2.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.5.0 |
| Direkte Abhängigkeit | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.2.0 |
| Geltungsbereich | S3_INDICATORS der RCC-002-Datenpipeline |
| Referenziert durch | Signaltransformation; Regime- und Gate-Spezifikation; Labels; Backtest; Paper-/Live-Parität |
| Autoritative Sprache | Mathematische Definitionen und englische Feldnamen sind normativ; deutsche Erläuterungen dienen der fachlichen Präzisierung |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Kapitel und Indikatorregister vollständig |
| Formel- und Indexprüfung | Bestanden | Fenstergrenzen, Seeds und erste gültige Zeitpunkte explizit |
| Nullfallprüfung | Bestanden | Division-durch-null- und Flat-Market-Fälle definiert |
| Kausalitätsprüfung | Bestanden | Keine zentrierten oder zukunftsbezogenen Berechnungen |
| Lücken- und Partitionsprüfung | Bestanden | State Reset, State Carry und Rebuild-Reichweite definiert |
| Legacy-Trennungsprüfung | Bestanden | Reproduktion und neuer kanonischer Standard bleiben getrennt |
| Scientific Consistency Review | Nicht bestanden; Korrektur eingearbeitet | `SCR-003-B02` aus `RCC-002-SCR-003` in Version 0.2.0 korrigiert; fokussierter Re-Review ausstehend |

## 1. Zweck

Dieses Dokument definiert die kanonischen mathematischen und technischen
Berechnungsregeln der RCC-002-Indikatoren.

Es beseitigt insbesondere Mehrdeutigkeiten bei:

- Glättungsverfahren,
- Initialisierung und Seed-Werten,
- Rolling-Window-Grenzen,
- Standardabweichungsdefinition,
- Nullnennern,
- Warm-up,
- Datenlücken,
- Partitionsübergängen,
- numerischer Präzision,
- Legacy-Reproduktion.

Ziel ist, dass dieselben validierten OHLCV-Daten auf Workstation, Notebook,
Backtest, Paper Trading und Live-System dieselben Indikatorwerte erzeugen.

## 2. Geltungsbereich

### 2.1 Enthaltene kanonische Indikatoren

RCC-002 spezifiziert:

1. Simple Moving Average 200.
2. Exponential Moving Average 50.
3. Relative Strength Index 14 nach Wilder.
4. MACD 12/26 mit Signal 9 und Histogramm.
5. Bollinger Bands 20/2.
6. Stochastic %K 14.
7. Average True Range 14 nach Wilder.
8. Rate of Change 12.
9. On-Balance Volume.
10. Commodity Channel Index 20.
11. Money Flow Index 14.
12. Average Directional Index 14 nach Wilder.

### 2.2 Nicht enthalten

Nicht Gegenstand dieses Dokuments sind:

- bullish/bearish/neutral Signalgrenzen,
- Gewichtung oder Kombination von Indikatoren,
- Marktregime,
- Long-/Short-Gates,
- Strategie-Entry oder -Exit,
- Positionsgröße,
- Forward Returns oder Labels.

Diese Entscheidungen gehören in nachgelagerte Spezifikationen.

## 3. Normative Konventionen

### 3.1 Zeitindex

`t` bezeichnet die Position einer vollständig geschlossenen, validierten und
zeitlich geordneten Kerze.

Für jeden Indikatorwert bei `t` dürfen ausschließlich Daten mit Index
`i <= t` verwendet werden.

### 3.2 Preise und Volumen

Es gelten:

- `O_t`: Open,
- `H_t`: High,
- `L_t`: Low,
- `C_t`: Close,
- `V_t`: Basisasset-Volumen.

Alle Eingaben stammen aus S2_VALIDATED.

### 3.3 Fenster

Ein Rolling Window der Länge `n` bei `t` umfasst einschließlich beider Grenzen:

`[t - n + 1, ..., t]`

Es enthält exakt `n` zeitlich zusammenhängende gültige Beobachtungen.

`min_periods` MUST dem vollständigen Fenster `n` entsprechen, sofern bei einem
Indikator keine abweichende Regel ausdrücklich definiert ist.

### 3.4 Numerische Präzision

Berechnungen MUST mindestens IEEE-754 `float64` verwenden.

Zwischenergebnisse dürfen:

- nicht auf Anzeigepräzision gerundet,
- nicht in `float32` herabgestuft,
- nicht durch formatierte Textwerte ersetzt

werden.

Rundung ist nur in nichtkanonischen Berichten zulässig.

### 3.5 Ungültiger Wert

Ein noch nicht berechenbarer oder qualitätsbedingt ungültiger Indikatorwert
wird als `NaN` gespeichert und durch ein separates Validitätsfeld ausgewiesen.

`0` ist ein fachlicher Wert und darf nicht allgemein für „ungültig“ verwendet
werden.

### 3.6 Kausalität

Unzulässig sind:

- `center=True`,
- negative Shifts zur Feature-Bildung,
- Backward Fill,
- Normalisierung gegen zukünftige oder vollständige Datensatzstatistiken,
- rückwirkende Neuberechnung früherer Regime- oder Signalzustände anhand
  späterer Werte.

## 4. Eingabevertrag

### 4.1 Pflichtfelder

S3 benötigt:

- `open_time`,
- `open`,
- `high`,
- `low`,
- `close`,
- `volume`,
- `quality_is_observed`,
- `quality_is_synthetic`,
- Lücken- und Qualitätsinformationen aus S2.

### 4.2 Eingabeinvarianten

Vor S3 MUST gelten:

- Zeitindex streng aufsteigend,
- Primärschlüssel eindeutig,
- OHLCV-Invarianten bestanden,
- keine nicht endlichen Pflichtwerte,
- Qualitätsstatus vorhanden,
- Schema-Fingerprint freigegeben.

S3 darf eine unvalidierte Rohdatei nicht direkt konsumieren.

### 4.3 Synthetische Kerzen

Kanonische Indikatoren werden standardmäßig ausschließlich auf beobachteten
Kerzen berechnet.

Indikatoren auf einer synthetischen Kontinuitätsansicht benötigen:

- eigene Build- und View-ID,
- eigene Indikatorprofil-ID,
- explizite Kennzeichnung,
- getrennte Sensitivitätsanalyse.

Sie dürfen kanonische beobachtete Indikatoren nicht überschreiben.

## 5. Indikatorregister

| ID | Kanonische Felder | Parameter | Eingaben |
|---|---|---|---|
| `SMA_CLOSE_V1` | `sma_close_200` | `n=200` | `close` |
| `EMA_CLOSE_V1` | `ema_close_50` | `n=50` | `close` |
| `RSI_WILDER_V1` | `rsi_wilder_14` | `n=14` | `close` |
| `MACD_EMA_V1` | `macd_line_12_26`, `macd_signal_line_12_26_9`, `macd_hist_12_26_9` | `fast=12`, `slow=26`, `signal=9` | `close` |
| `BBANDS_POP_V1` | `bb_mid_20`, `bb_upper_20_2`, `bb_lower_20_2`, `bb_width_20_2` | `n=20`, `k=2`, `ddof=0` | `close` |
| `STOCH_K_V1` | `stoch_k_14` | `n=14` | `high`, `low`, `close` |
| `ATR_WILDER_V1` | `true_range`, `atr_wilder_14` | `n=14` | `high`, `low`, `close` |
| `ROC_SIMPLE_V1` | `roc_close_12_pct` | `n=12` | `close` |
| `OBV_V1` | `obv` | Seed `0` | `close`, `volume` |
| `CCI_MAD_V1` | `typical_price`, `cci_20` | `n=20`, constant `0.015` | `high`, `low`, `close` |
| `MFI_V1` | `mfi_14` | `n=14` | `high`, `low`, `close`, `volume` |
| `ADX_WILDER_V1` | `plus_di_14`, `minus_di_14`, `dx_14`, `adx_wilder_14` | `n=14` | `high`, `low`, `close` |

Jede Änderung einer Formel, Initialisierung, Nullfallregel oder
Warm-up-Semantik benötigt eine neue Indikator-ID oder Major-Version.

## 6. Gemeinsame Hilfsdefinitionen

### 6.1 Simple Moving Average

Für eine Serie `X` und Fenster `n`:

`SMA_n(X)_t = (1 / n) * sum(X_i, i=t-n+1...t)`

Der erste gültige Wert liegt bei `t = n - 1`, sofern die Serie am Index `0`
beginnt und das Fenster qualitätsgültig ist.

### 6.2 Kanonische EMA

Für Periode `n`:

`alpha = 2 / (n + 1)`

Seed:

`EMA_n(X)_(n-1) = SMA_n(X)_(n-1)`

Rekursion für `t >= n`:

`EMA_n(X)_t = alpha * X_t + (1 - alpha) * EMA_n(X)_(t-1)`

Vor `t = n - 1` ist die EMA `NaN`.

Diese Seed-Regel ist normativ. Eine Bibliotheksfunktion darf nur verwendet
werden, wenn sie exakt dieselben Werte erzeugt.

### 6.3 Wilder Average

Für eine nichtnegative Serie `X` und Periode `n`:

Seed:

`WilderAvg_n(X)_s = mean(X_i, i=s-n+1...s)`

Rekursion:

`WilderAvg_n(X)_t = ((n - 1) * WilderAvg_n(X)_(t-1) + X_t) / n`

Der Indikatorabschnitt legt jeweils fest, welcher Index `s` das erste
vollständige Seed-Fenster beendet.

### 6.4 Wilder Smoothed Sum

Für Directional Movement werden geglättete Summen verwendet.

Seed:

`WilderSum_n(X)_s = sum(X_i, i=s-n+1...s)`

Rekursion:

`WilderSum_n(X)_t = WilderSum_n(X)_(t-1) - WilderSum_n(X)_(t-1)/n + X_t`

## 7. Simple Moving Average 200

### 7.1 Definition

`sma_close_200_t = SMA_200(C)_t`

### 7.2 Gültigkeit

Erster mathematisch gültiger Wert:

`t = 199`

Er ist nur qualitätsgültig, wenn alle 200 Kerzen beobachtet, gültig und
zeitlich zusammenhängend sind.

### 7.3 Nullfall

Da alle Close-Preise positiv sein müssen, existiert kein zulässiger
Division-durch-null-Fall.

## 8. Exponential Moving Average 50

### 8.1 Definition

`ema_close_50_t = EMA_50(C)_t`

mit:

`alpha = 2 / 51`

### 8.2 Seed

`ema_close_50_49 = mean(C_0...C_49)`

### 8.3 Gültigkeit

Erster mathematisch gültiger Wert:

`t = 49`

Nach einer Datenlücke wird der EMA-Zustand zurückgesetzt. Ein neuer gültiger
Seed benötigt 50 aufeinanderfolgende qualitätsgültige Kerzen.

## 9. Relative Strength Index 14

### 9.1 Preisänderung

Für `t >= 1`:

`delta_t = C_t - C_(t-1)`

`gain_t = max(delta_t, 0)`

`loss_t = max(-delta_t, 0)`

### 9.2 Seed

Die ersten 14 Änderungen sind:

`delta_1...delta_14`

Damit:

`avg_gain_14 = mean(gain_1...gain_14)`

`avg_loss_14 = mean(loss_1...loss_14)`

### 9.3 Rekursion

Für `t >= 15`:

`avg_gain_t = ((13 * avg_gain_(t-1)) + gain_t) / 14`

`avg_loss_t = ((13 * avg_loss_(t-1)) + loss_t) / 14`

### 9.4 RSI

Wenn `avg_gain_t > 0` und `avg_loss_t > 0`:

`RS_t = avg_gain_t / avg_loss_t`

`rsi_wilder_14_t = 100 - 100 / (1 + RS_t)`

### 9.5 Nullfälle

- Wenn `avg_gain_t = 0` und `avg_loss_t = 0`, dann RSI `= 50`.
- Wenn `avg_gain_t > 0` und `avg_loss_t = 0`, dann RSI `= 100`.
- Wenn `avg_gain_t = 0` und `avg_loss_t > 0`, dann RSI `= 0`.

### 9.6 Gültigkeit

Erster gültiger Wert:

`t = 14`

Es werden damit 15 Close-Preise und 14 Preisänderungen benötigt.

## 10. MACD 12/26/9

### 10.1 Fast und Slow EMA

`ema_fast_t = EMA_12(C)_t`

`ema_slow_t = EMA_26(C)_t`

### 10.2 MACD-Linie

`macd_line_12_26_t = ema_fast_t - ema_slow_t`

Erster gültiger Wert:

`t = 25`

### 10.3 Signallinie

Die Signallinie ist eine kanonische EMA 9 der gültigen MACD-Linie.

Seed:

`macd_signal_line_12_26_9_33 = mean(macd_line_25...macd_line_33)`

Rekursion ab `t = 34` mit:

`alpha_signal = 2 / 10`

### 10.4 Histogramm

`macd_hist_12_26_9_t = macd_line_12_26_t - macd_signal_line_12_26_9_t`

Erster gültiger Signal- und Histogrammwert:

`t = 33`

### 10.5 Qualitätsregel

Fast EMA, Slow EMA und Signal-EMA müssen aus derselben lückenfreien
Beobachtungssequenz stammen.

## 11. Bollinger Bands 20/2

### 11.1 Mittellinie

`bb_mid_20_t = SMA_20(C)_t`

### 11.2 Populationsstandardabweichung

`variance_t = (1/20) * sum((C_i - bb_mid_20_t)^2, i=t-19...t)`

`std_pop_20_t = sqrt(variance_t)`

Damit gilt ausdrücklich:

`ddof = 0`

### 11.3 Bänder

`bb_upper_20_2_t = bb_mid_20_t + 2 * std_pop_20_t`

`bb_lower_20_2_t = bb_mid_20_t - 2 * std_pop_20_t`

### 11.4 Bandbreite

`bb_width_20_2_t = (bb_upper_20_2_t - bb_lower_20_2_t) / bb_mid_20_t`

Da Close-Preise positiv sind, muss `bb_mid_20_t > 0` gelten.

### 11.5 Gültigkeit

Erster gültiger Wert aller Bollinger-Felder:

`t = 19`

## 12. Stochastic %K 14

### 12.1 Fensterextreme

`lowest_low_14_t = min(L_i, i=t-13...t)`

`highest_high_14_t = max(H_i, i=t-13...t)`

### 12.2 Definition

Wenn:

`highest_high_14_t > lowest_low_14_t`

dann:

`stoch_k_14_t = 100 * (C_t - lowest_low_14_t) / (highest_high_14_t - lowest_low_14_t)`

### 12.3 Flat-Window-Fall

Wenn:

`highest_high_14_t = lowest_low_14_t`

dann:

- `stoch_k_14_t = 50`,
- Qualitätsflag `IND_STOCH_FLAT_WINDOW`.

Der Wert 50 beschreibt fehlende Lageinformation innerhalb eines vollständig
flachen Fensters und ist nicht „ungültig“.

### 12.4 Gültigkeit

Erster gültiger Wert:

`t = 13`

## 13. True Range und Average True Range 14

### 13.1 True Range

Für den ersten Index einer lückenfreien Sequenz:

`true_range_0 = H_0 - L_0`

Für `t >= 1`:

`true_range_t = max(H_t - L_t, abs(H_t - C_(t-1)), abs(L_t - C_(t-1)))`

### 13.2 ATR-Seed

`atr_wilder_14_13 = mean(true_range_0...true_range_13)`

### 13.3 Rekursion

Für `t >= 14`:

`atr_wilder_14_t = ((13 * atr_wilder_14_(t-1)) + true_range_t) / 14`

### 13.4 Gültigkeit

- `true_range` ist ab dem ersten Index einer lückenfreien Sequenz gültig.
- `atr_wilder_14` ist erstmals bei `t = 13` gültig.

Nach einer Lücke wird `C_(t-1)` nicht über die Lücke hinweg verwendet. Die
erste Kerze der neuen Sequenz beginnt erneut mit `H_t - L_t`.

## 14. Rate of Change 12

### 14.1 Definition

`roc_close_12_pct_t = 100 * (C_t / C_(t-12) - 1)`

### 14.2 Gültigkeit

Erster gültiger Wert:

`t = 12`

Es werden 13 Close-Preise benötigt.

`C_(t-12)` muss aufgrund der S2-Preisregeln größer als null sein.

## 15. On-Balance Volume

### 15.1 Seed

Am ersten Index einer lückenfreien Sequenz:

`obv_0 = 0`

### 15.2 Rekursion

Für `t >= 1`:

- Wenn `C_t > C_(t-1)`, dann `obv_t = obv_(t-1) + V_t`.
- Wenn `C_t < C_(t-1)`, dann `obv_t = obv_(t-1) - V_t`.
- Wenn `C_t = C_(t-1)`, dann `obv_t = obv_(t-1)`.

### 15.3 Gültigkeit und Vergleichbarkeit

OBV ist ab dem Seed gültig.

Der absolute OBV-Wert hängt vom Startpunkt der Sequenz ab. Deshalb MUST:

- der Seed-Zeitpunkt dokumentiert,
- bei kanonischen Vollbuilds derselbe Datensatzanfang verwendet,
- bei Partitionen der exakte Zustand übernommen

werden.

Nach einer echten Datenlücke beginnt für die neue unabhängige Sequenz ein neuer
OBV-Seed bei null. Ein `obv_segment_id` MUST die Vergleichsgrenze ausweisen.

## 16. Commodity Channel Index 20

### 16.1 Typical Price

`typical_price_t = (H_t + L_t + C_t) / 3`

### 16.2 Fenstermean

`tp_sma_20_t = mean(typical_price_i, i=t-19...t)`

### 16.3 Mean Absolute Deviation

`tp_mad_20_t = (1/20) * sum(abs(typical_price_i - tp_sma_20_t), i=t-19...t)`

Die Abweichungen beziehen sich auf den Mittelwert desselben aktuellen
20-Kerzen-Fensters.

### 16.4 Definition

Wenn `tp_mad_20_t > 0`:

`cci_20_t = (typical_price_t - tp_sma_20_t) / (0.015 * tp_mad_20_t)`

### 16.5 Flat-Window-Fall

Wenn `tp_mad_20_t = 0`:

- `cci_20_t = 0`,
- Qualitätsflag `IND_CCI_ZERO_MAD`.

### 16.6 Gültigkeit

- `typical_price` ist ab der ersten gültigen Kerze verfügbar.
- `cci_20` ist erstmals bei `t = 19` gültig.

## 17. Money Flow Index 14

### 17.1 Typical Price und Raw Money Flow

`typical_price_t = (H_t + L_t + C_t) / 3`

`raw_money_flow_t = typical_price_t * V_t`

### 17.2 Gerichteter Money Flow

Für `t >= 1`:

- Wenn `typical_price_t > typical_price_(t-1)`, dann:
  - `positive_flow_t = raw_money_flow_t`
  - `negative_flow_t = 0`
- Wenn `typical_price_t < typical_price_(t-1)`, dann:
  - `positive_flow_t = 0`
  - `negative_flow_t = raw_money_flow_t`
- Bei Gleichheit:
  - `positive_flow_t = 0`
  - `negative_flow_t = 0`

### 17.3 14-Perioden-Summen

`positive_sum_14_t = sum(positive_flow_i, i=t-13...t)`

`negative_sum_14_t = sum(negative_flow_i, i=t-13...t)`

### 17.4 MFI

Wenn beide Summen positiv sind:

`money_flow_ratio_t = positive_sum_14_t / negative_sum_14_t`

`mfi_14_t = 100 - 100 / (1 + money_flow_ratio_t)`

### 17.5 Nullfälle

- Wenn beide Summen null sind, dann MFI `= 50`.
- Wenn `positive_sum_14_t > 0` und `negative_sum_14_t = 0`, dann MFI `= 100`.
- Wenn `positive_sum_14_t = 0` und `negative_sum_14_t > 0`, dann MFI `= 0`.

### 17.6 Gültigkeit

Der erste gültige Wert liegt bei:

`t = 14`

Begründung: Für die 14 gerichteten Flows `1...14` werden 15
Typical-Price-Werte `0...14` benötigt.

## 18. Average Directional Index 14

### 18.1 True Range

Für `t >= 1`:

`TR_t = max(H_t - L_t, abs(H_t - C_(t-1)), abs(L_t - C_(t-1)))`

### 18.2 Directional Movement

`up_move_t = H_t - H_(t-1)`

`down_move_t = L_(t-1) - L_t`

Dann:

- Wenn `up_move_t > down_move_t` und `up_move_t > 0`:
  - `plus_dm_t = up_move_t`
  - `minus_dm_t = 0`
- Wenn `down_move_t > up_move_t` und `down_move_t > 0`:
  - `plus_dm_t = 0`
  - `minus_dm_t = down_move_t`
- Andernfalls:
  - `plus_dm_t = 0`
  - `minus_dm_t = 0`

Bei Gleichheit von positiven `up_move_t` und `down_move_t` werden beide auf
null gesetzt.

### 18.3 Geglättete 14er-Summen

Am Index `t = 14`:

`tr_sum_14_14 = sum(TR_i, i=1...14)`

`plus_dm_sum_14_14 = sum(plus_dm_i, i=1...14)`

`minus_dm_sum_14_14 = sum(minus_dm_i, i=1...14)`

Für `t >= 15` gilt jeweils die Wilder-Sum-Rekursion:

`smoothed_t = smoothed_(t-1) - smoothed_(t-1)/14 + current_t`

### 18.4 Directional Indicators

Wenn `tr_sum_14_t > 0`:

`plus_di_14_t = 100 * plus_dm_sum_14_t / tr_sum_14_t`

`minus_di_14_t = 100 * minus_dm_sum_14_t / tr_sum_14_t`

Wenn `tr_sum_14_t = 0`, werden beide DI-Werte auf `0` gesetzt und
`IND_ADX_ZERO_TR` markiert.

### 18.5 Directional Index

Wenn:

`plus_di_14_t + minus_di_14_t > 0`

dann:

`dx_14_t = 100 * abs(plus_di_14_t - minus_di_14_t) / (plus_di_14_t + minus_di_14_t)`

Wenn die Summe null ist:

`dx_14_t = 0`

### 18.6 ADX-Seed

Der erste ADX ist der Mittelwert der ersten 14 gültigen DX-Werte:

`adx_wilder_14_27 = mean(dx_14_i, i=14...27)`

### 18.7 ADX-Rekursion

Für `t >= 28`:

`adx_wilder_14_t = ((13 * adx_wilder_14_(t-1)) + dx_14_t) / 14`

### 18.8 Gültigkeit

- `plus_di_14`, `minus_di_14` und `dx_14`: erstmals `t = 14`.
- `adx_wilder_14`: erstmals `t = 27`.

Es werden 28 aufeinanderfolgende Kerzen für den ersten ADX benötigt.

## 19. Warm-up-Matrix

| Feld | Erster gültiger Index | Erforderliche Kerzen |
|---|---:|---:|
| `typical_price` | 0 | 1 |
| `true_range` | 0 | 1 |
| `obv` | 0 | 1 |
| `roc_close_12_pct` | 12 | 13 |
| `stoch_k_14` | 13 | 14 |
| `atr_wilder_14` | 13 | 14 |
| `rsi_wilder_14` | 14 | 15 |
| `mfi_14` | 14 | 15 |
| `plus_di_14`, `minus_di_14`, `dx_14` | 14 | 15 |
| `bb_*_20_2` | 19 | 20 |
| `cci_20` | 19 | 20 |
| `macd_line_12_26` | 25 | 26 |
| `adx_wilder_14` | 27 | 28 |
| `macd_signal_line_12_26_9`, `macd_hist_12_26_9` | 33 | 34 |
| `ema_close_50` | 49 | 50 |
| `sma_close_200` | 199 | 200 |

Die Indizes beziehen sich auf den Beginn einer lückenfreien Sequenz.

## 20. Gültigkeits- und Qualitätsfelder

### 20.1 Feldbezogene Gültigkeit

Für jedes kanonische Indikatorfeld MUST ein maschinenlesbarer Gültigkeitsstatus
vorliegen.

Zulässige Umsetzung:

- einzelnes Boolean-Feld je Indikator oder
- kompakte strukturierte Validitätsmaske mit registriertem Schema.

### 20.2 Mindestgründe für Ungültigkeit

- `IND_WARMUP_INCOMPLETE`,
- `IND_INPUT_INVALID`,
- `IND_WINDOW_CROSSES_GAP`,
- `IND_SYNTHETIC_INPUT_DISALLOWED`,
- `IND_STATE_MISSING`,
- `IND_NONFINITE_RESULT`.

### 20.3 Nichtkritische Sonderfälle

- `IND_STOCH_FLAT_WINDOW`,
- `IND_CCI_ZERO_MAD`,
- `IND_ADX_ZERO_TR`.

Diese Sonderfälle besitzen definierte numerische Werte und sind nicht
automatisch ungültig.

### 20.4 Bereichsprüfungen

MUST gelten:

- `0 <= rsi_wilder_14 <= 100`,
- `0 <= stoch_k_14 <= 100`,
- `atr_wilder_14 >= 0`,
- `0 <= mfi_14 <= 100`,
- `0 <= plus_di_14 <= 100`,
- `0 <= minus_di_14 <= 100`,
- `0 <= dx_14 <= 100`,
- `0 <= adx_wilder_14 <= 100`,
- `bb_upper_20_2 >= bb_mid_20 >= bb_lower_20_2`,
- `bb_width_20_2 >= 0`.

Eine Verletzung nach zulässiger Float-Toleranz ist `CRITICAL`.

## 21. Datenlücken und Segmentierung

### 21.1 Grundregel

Kein kanonischer Rolling- oder rekursiver Zustand darf eine echte Datenlücke
stillschweigend überbrücken.

### 21.2 Segment-ID

S3 MUST eine `indicator_segment_id` führen.

Eine neue Segment-ID beginnt:

- am Datensatzanfang,
- nach jeder erkannten Zeitlücke,
- nach einem qualitätsungültigen Pflichtwert,
- nach einem expliziten State Reset.

### 21.3 Rolling-Indikatoren

Nach Segmentbeginn werden Rolling-Indikatoren erst nach ihrem vollständigen
Warm-up wieder gültig.

### 21.4 Rekursive Indikatoren

EMA, RSI, ATR, OBV und ADX werden nach Segmentbeginn gemäß ihren Seed-Regeln
neu initialisiert.

Dadurch werden keine unbekannten Marktbewegungen über eine Lücke implizit als
unveränderte Zustände behandelt.

### 21.5 Sensitivitätsanalyse

Spätere Forschung MAY alternative Lückenpolitiken prüfen. Jede Alternative
benötigt:

- eigene Profil-ID,
- eigenen Build,
- getrennte Ergebnisse,
- Vergleich gegen die kanonische Reset-Regel.

## 22. Partitionierte Berechnung

### 22.1 Äquivalenzanforderung

Ein partitionierter Vollbuild MUST nach feldspezifischer Toleranz dieselben
Werte erzeugen wie ein serieller Build über dieselben lückenfreien Eingaben.

### 22.2 Rolling State

Für reine Rolling-Indikatoren MAY die nächste Partition die erforderlichen
vorherigen Beobachtungen als Overlap lesen.

Der Overlap wird nicht doppelt ausgegeben.

### 22.3 Rekursiver State

Rekursive Indikatoren benötigen einen expliziten State Snapshot.

Dieser enthält mindestens:

- letzte kanonische Schlüsselposition,
- Segment-ID,
- EMA-Zustände,
- RSI Average Gain und Average Loss,
- ATR-Zustand,
- OBV-Zustand,
- ADX geglättete TR-/DM-Summen und ADX-Zustand,
- erforderliche vorherige OHLC-/Typical-Price-Werte,
- noch nicht abgeschlossene Warm-up-Puffer und Warm-up-Zähler,
- State-Schemaversion,
- Checksumme.

### 22.4 State-Sicherheit

Ein State Snapshot darf nur verwendet werden, wenn:

- Parent-Build-ID stimmt,
- vorherige Partition erfolgreich validiert wurde,
- Schlüssel direkt anschließt,
- State-Checksumme stimmt,
- Profil- und Indikatorversionen identisch sind.

Andernfalls wird der Build abgebrochen oder ein dokumentierter neuer
Segment-Seed begonnen. Ein stiller Fallback ist unzulässig.

## 23. Inkrementelle Neuberechnung

### 23.1 Neue Daten ohne historische Revision

Neue, direkt anschließende Kerzen MAY mit dem validierten End-State des
vorherigen Builds berechnet werden.

### 23.2 Historische Revision

Wird eine historische Kerze geändert, gelten:

- Rolling-Indikatoren müssen mindestens ab der frühesten geänderten Kerze bis
  zum Ende ihres maximalen Einflussfensters neu berechnet werden.
- Rekursive Indikatoren müssen ab der frühesten geänderten Kerze bis zum Ende
  des Datensatzes neu berechnet werden.
- Abhängige Signale, Regime, Gates und Labels müssen entsprechend invalidiert
  und neu erzeugt werden.

Eine angenommene numerische „Konvergenz“ rekursiver Indikatoren darf im
kanonischen Build nicht als Ersatz für die vollständige Neuberechnung dienen.

## 24. Legacy-Kompatibilitätsprofil

### 24.1 Zweck

Das Profil `LEGACY_BTC_SIGNAL_BUILDER_V1` dient ausschließlich der
reproduzierbaren historischen Vergleichsrechnung.

Es ist nicht der kanonische RCC-002-Indikatorstandard.

### 24.2 Verifizierte Legacy-Grundlage

Der historische Builder:

`archive/HISTORICAL_K3_K10_2026-01-06/scripts_legacy_from_root/build_price_data_with_signals.py`

stimmt bei den zwölf daraus abgeleiteten Signalspalten über 2.721.034 geprüfte
Zeilen ohne Abweichung mit der vorhandenen Datei überein.

### 24.3 Relevante Legacy-Abweichungen

Das Legacy-Profil reproduziert unter anderem:

- RSI über Pandas `ewm(alpha=1/14, adjust=False)` ohne kanonischen
  Wilder-SMA-Seed,
- MACD-EMAs über `ewm(span=n, adjust=False)` mit Pandas-Startwert,
- Bollinger-Standardabweichung mit Pandas-Standard `ddof=1`,
- ATR als einfacher Rolling Mean des True Range,
- ADX über Rolling-Summen und anschließenden Rolling Mean,
- teilweise aufgefüllte Warm-up-Werte,
- implizite Signalwerte `0` bei nicht berechenbaren Vergleichen.

### 24.4 Trennungsregeln

Legacy-Werte MUST:

- eigene Profil- und Feldbezeichner besitzen,
- getrennt von RCC-002-Kanonicalwerten gespeichert werden,
- im Manifest als Legacy markiert sein,
- nicht unbemerkt in neue Signale oder Regime eingehen.

Ein Vergleichsdatensatz MAY beide Profile enthalten, wenn jede Spalte eindeutig
zugeordnet ist.

## 25. Bibliotheksunabhängigkeit

### 25.1 Formel ist autoritativ

Keine externe Indikatorbibliothek ist alleinige fachliche Referenz.

Eine Bibliothek MAY verwendet werden, wenn Konformitätstests belegen, dass sie
für:

- Seed,
- Rekursion,
- Fenstergrenzen,
- Nullfälle,
- Warm-up,
- Lückenverhalten

dieselben Ergebnisse wie diese Spezifikation erzeugt.

### 25.2 Versionsbindung

Verwendete Versionen von Python, NumPy, Pandas, PyArrow und optionalen
Indikatorbibliotheken MUST im Manifest dokumentiert und in der
Ausführungsumgebung fixiert werden.

## 26. Ausgabevertrag

### 26.1 Pflichtausgaben

S3 erzeugt:

- kanonische Indikatorfelder,
- Gültigkeitsinformationen,
- Qualitäts- und Sonderfallflags,
- `indicator_profile_id`,
- `indicator_profile_version`,
- `indicator_segment_id`,
- Schema-Fingerprint,
- State Snapshot je abgeschlossener Partition,
- Indikator-Validierungsbericht.

### 26.2 Keine Zeilenänderung

S3 darf im kanonischen beobachteten Datensatz:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keinen OHLCV-Wert verändern.

Es muss gelten:

`S3_rows = S2_rows`

und der kanonische Schlüssel jeder Zeile muss identisch bleiben.

### 26.3 Spaltenreihenfolge

Die Spaltenreihenfolge MUST deterministisch und schemaversioniert sein.

## 27. Testanforderungen

### 27.1 Unit Tests

Für jeden Indikator sind erforderlich:

- minimaler gültiger Input,
- Warm-up unmittelbar vor und am ersten gültigen Index,
- konstante Preisserie,
- streng steigende Serie,
- streng fallende Serie,
- wechselnde Serie,
- Nullvolumenfälle,
- definierte Nullnenner,
- Lücke und State Reset,
- nicht endliche Eingabe,
- Bereichsinvarianten.

### 27.2 Handberechnete Golden Fixtures

Jeder Indikator benötigt mindestens einen kleinen, unabhängig berechneten
Golden Fixture mit:

- Eingangswerten,
- Zwischengrößen,
- erwarteten Ausgabewerten,
- zulässiger Toleranz.

Für RSI und ADX müssen Seed und mindestens zwei Rekursionsschritte enthalten
sein.

### 27.3 Referenzvergleich

SHOULD zusätzlich erfolgen:

- Vergleich gegen mindestens eine unabhängige Implementierung,
- dokumentierte Analyse jeder Abweichung,
- keine Anpassung der kanonischen Formel allein zur Übereinstimmung mit einer
  Bibliothek.

### 27.4 Kausalitätstest

Für jeden Indikator MUST gelten:

Wenn alle Eingaben bis einschließlich `t` unverändert bleiben und ausschließlich
Werte nach `t` verändert werden, darf sich der Indikatorwert bei `t` nicht
ändern.

### 27.5 Partitionsparität

Ein identischer Datensatz wird:

- seriell,
- in Monatspartitionen,
- in künstlich ungleich großen Partitionen

berechnet. Die Ergebnisse müssen innerhalb der definierten Toleranz
übereinstimmen.

### 27.6 Legacy-Golden-Test

Das Legacy-Profil MUST die bekannten historischen Indikator- und Signalwerte
innerhalb der dokumentierten Legacy-Semantik reproduzieren.

## 28. Numerische Toleranzen

### 28.1 Kanonischer Wiederholungsbuild

Bei identischer Umgebung und identischer Serialisierung wird
Checksum-Gleichheit erwartet.

### 28.2 Unabhängiger Implementierungsvergleich

Standardtoleranz für endliche `float64`-Werte:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Abweichende feldspezifische Toleranzen benötigen:

- dokumentierte Begründung,
- registrierte Feldzuordnung,
- Testabdeckung,
- Freigabe.

### 28.3 Grenzwertentscheidungen

Signal- oder Gate-Entscheidungen an Schwellenwerten dürfen nicht durch
Berichtsrundung erfolgen. Sie verwenden die ungerundeten kanonischen Werte.

## 29. Validierungsbericht

Der S3-Bericht enthält mindestens:

- Build- und Profil-ID,
- Indikatorversionen,
- Zeilenzahl,
- erste und letzte Zeit,
- ersten gültigen Index je Feld und Segment,
- Anzahl gültiger und ungültiger Werte,
- Ungültigkeitsgründe,
- Sonderfallflags,
- Minimal- und Maximalwerte,
- Bereichsverletzungen,
- Segment- und Lückenanzahl,
- State-Snapshot-Prüfungen,
- Partitionsparität,
- Golden-Test-Ergebnisse,
- Output-Checksumme.

## 30. Publication Gate

S3 darf nur veröffentlicht werden, wenn:

1. S2 vollständig freigegeben ist,
2. Eingabeschema und Schema-Fingerprint stimmen,
3. alle Indikatorversionen registriert sind,
4. keine Zeile oder kein OHLCV-Wert verändert wurde,
5. Warm-up und Gültigkeitsmasken korrekt sind,
6. keine nicht endlichen gültigen Indikatorwerte bestehen,
7. alle Bereichsinvarianten bestanden sind,
8. Lücken zu neuen Segmenten führen,
9. State Snapshots valide sind,
10. Golden- und Kausalitätstests bestanden sind,
11. serieller und partitionierter Build übereinstimmen,
12. Manifest und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

## 31. Abnahmekriterien

`RCC_002_INDICATOR_SPECIFICATION` ist implementierungsreif, wenn:

1. alle Formeln in unabhängigen Tests abgebildet sind,
2. Seeds und Warm-up-Grenzen durch Golden Fixtures bestätigt sind,
3. Nullfälle vollständig getestet sind,
4. Lücken- und Segmentverhalten getestet ist,
5. State Snapshot und Partitionsparität getestet sind,
6. kanonisches und Legacy-Profil strikt getrennt sind,
7. der BTCUSDT-1m-Vollbuild auf der Workstation bestanden ist,
8. ein unabhängiger Rebuild dieselben Ergebnisse erzeugt,
9. keine offene kritische Inkonsistenz besteht,
10. Manifest und Knowledge Lineage vollständig sind.

## 32. Freigabestatus und nächster Schritt

Diese Spezifikation wurde vor ihrer ersten Ausgabe intern auf mathematische,
methodische, strukturelle und terminologische Konsistenz geprüft.

Der fokussierte Re-Review `RCC-002-SCR-003` identifizierte
`SCR-003-B02`: Die Metadaten referenzierten veraltete Versionen der
übergeordneten Data Pipeline Specification und der direkten Data Validation
Specification.

Version 0.2.0 korrigiert die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.5.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.2.0
```

Die mathematischen und technischen Indikatorregeln wurden dabei nicht
verändert.

Sie ist noch nicht wissenschaftlich zertifiziert. Der Status bleibt:

```text
SCR-003-Corrected Draft – Re-Review Pending
```

Nächster fachlicher Schritt:

Fokussierter Scientific Consistency Re-Review von `SCR-003-B02` gemeinsam
mit der vollständigen korrigierten RCC-002-Spezifikationsfamilie.

---

# Eingebettetes Dokument 4 von 7

## Quelldatei: `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`

# RCC-002 Signal Transformation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-ST |
| Titel | Signal Transformation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Dateiname | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Version | 0.2.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.5.0 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.2.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.2.0 |
| Geltungsbereich | S4_SIGNALS der RCC-002-Datenpipeline |
| Referenziert durch | Regime- und Gate-Spezifikation; Strategieforschung; Backtest; Paper-/Live-Parität |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs und mathematische Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Profile, Rollen und Feldgruppen vollständig |
| Vorzeichenprüfung | Bestanden | `+1` durchgängig long-supportive, `-1` durchgängig short-supportive |
| Rollenprüfung | Bestanden | Richtung, Trend, Volatilität und Trendstärke getrennt |
| Grenzwertprüfung | Bestanden | Gleichheit, Nullfälle, Clipping und Ungültigkeit definiert |
| Kausalitätsprüfung | Bestanden | Nur aktuelle und vergangene S3-Werte verwendet |
| Legacy-Trennungsprüfung | Bestanden | Historische Reproduktion überschreibt keine kanonischen Signale |
| Scientific Consistency Review | Nicht bestanden; Korrektur eingearbeitet | `SCR-003-B02` aus `RCC-002-SCR-003` in Version 0.2.0 korrigiert; fokussierter Re-Review ausstehend |

## 1. Zweck

Dieses Dokument definiert, wie kanonische S3-Indikatoren in standardisierte,
maschinenlesbare S4-Signale und Zustandsmerkmale transformiert werden.

Es löst insbesondere folgende historische Probleme:

- binäre Legacy-Signale bildeten fast ausschließlich bullish Bedingungen ab,
- `0` bedeutete gleichzeitig neutral, bearish oder nicht berechenbar,
- ATR und ADX wurden teilweise wie Richtungssignale behandelt,
- Trendfilter und Entry-Timing waren nicht sauber getrennt,
- dieselben Feldnamen konnten Indikatorlinien und Handelssignale bezeichnen,
- kontinuierliche GS-Scores waren nicht vollständig versioniert erhalten.

S4 erzeugt keine Trades. Es beschreibt ausschließlich die aus Indikatoren
ableitbare Evidenz zum Zeitpunkt `t`.

## 2. Geltungsbereich

### 2.1 Enthalten

S4 umfasst:

- Signalrollen und Vorzeichenkonvention,
- diskrete Richtungssignale,
- kontinuierliche Richtungsscores,
- Trendzustände,
- Volatilitätszustände,
- Trendstärkezustände,
- Validität und Qualitätsflags,
- Legacy-Kompatibilitätsprofile,
- Output- und Testverträge.

### 2.2 Nicht enthalten

Nicht Gegenstand dieses Dokuments sind:

- Kombination mehrerer Signale zu einer Strategie,
- Entry- oder Exit-Regeln,
- Regimeklassifikation,
- Long-/Short-Handelsfreigabe,
- Cooldown oder Loss-Cluster-Gates,
- Positionsgröße,
- Gewinn- oder Verlustlabels.

Insbesondere ist ein positives Signal keine automatische Handelsfreigabe.

## 3. Grundsemantik

### 3.1 Richtungsvorzeichen

Für alle kanonischen diskreten Richtungssignale und kontinuierlichen
Richtungsscores gilt:

- `+1`: unterstützt eine Long-Hypothese,
- `0`: neutral beziehungsweise keine gerichtete Evidenz,
- `-1`: unterstützt eine Short-Hypothese.

Diese Bedeutung darf profilübergreifend nicht invertiert werden.

### 3.2 Ungültigkeit

Ungültigkeit wird als `null`/`NaN` plus Validitätsfeld dargestellt.

Ungültigkeit darf nicht als:

- `0`,
- `-1`,
- `false`

kodiert werden, wenn dadurch Neutralität, Short-Evidenz oder ein schwacher
Zustand vorgetäuscht würde.

### 3.3 Signalrollen

Jedes S4-Feld gehört genau einer Rolle an:

| Rolle | Bedeutung | Zulässiger Wertebereich |
|---|---|---|
| `DIRECTION_DISCRETE` | diskrete Long-/Short-Evidenz | `{-1, 0, +1}` |
| `DIRECTION_SCORE` | kontinuierliche Long-/Short-Evidenz | `[-1, +1]` |
| `TREND_STATE` | Richtung eines Preis-/Trendverhältnisses | `{-1, 0, +1}` oder `[-1,+1]` |
| `VOLATILITY_STATE` | relative Volatilität ohne Handelsrichtung | `{-1,0,+1}` oder `[-1,+1]` |
| `TREND_STRENGTH` | richtungslose Trendstärke | `[0,1]` |
| `VALIDITY` | fachliche Berechenbarkeit | Boolean/Reason Code |

`VOLATILITY_STATE` und `TREND_STRENGTH` dürfen nicht ohne eine separat
spezifizierte Regel als Long- oder Short-Stimme summiert werden.

## 4. Profile

### 4.1 `RCC_DISCRETE_V1`

Erzeugt:

- diskrete Mean-Reversion-Signale,
- diskrete Momentum-/Volumen-Signale,
- diskrete Trendzustände,
- diskrete Volatilitäts- und Trendstärkezustände.

### 4.2 `RCC_CONTINUOUS_V1`

Erzeugt dimensionslose kontinuierliche Scores mit festen, versionierten
Transformationen.

Diese Scores sind Forschungsfeatures. Ihre Definition genehmigt weder ihre
Gewichtung noch ihre Verwendung in einer Strategie.

### 4.3 `LEGACY_BTC_BINARY_V1`

Reproduziert die zwölf historisch verifizierten 0/1-Signalspalten.

Das Profil ist ausschließlich für:

- Reproduktion,
- Vergleich,
- Knowledge Lineage

zulässig.

### 4.4 Profilkombination

Ein Build MAY mehrere Profile parallel erzeugen, wenn:

- Feldnamen eindeutig sind,
- jede Spalte eine Profil-ID trägt oder über das Schema zugeordnet ist,
- kein Profil ein anderes überschreibt,
- das Manifest alle aktiven Profile aufführt.

Diskrete und kontinuierliche Profile sind parallele Repräsentationen. Ein
diskretes Feld darf nicht nachträglich aus dem Vorzeichen seines
kontinuierlichen Gegenstücks abgeleitet werden. Insbesondere können strikte
diskrete Grenzwerte an einem exakten Schwellenwert neutral sein, während der
kontinuierliche Score dort bereits einen definierten Ankerwert erreicht.

## 5. Eingabevertrag

### 5.1 Pflichtfelder aus S3

S4 verwendet:

- `close`,
- `volume`,
- `sma_close_200`,
- `ema_close_50`,
- `rsi_wilder_14`,
- `macd_hist_12_26_9`,
- `bb_mid_20`,
- `bb_upper_20_2`,
- `bb_lower_20_2`,
- `stoch_k_14`,
- `atr_wilder_14`,
- `roc_close_12_pct`,
- `obv`,
- `cci_20`,
- `mfi_14`,
- `adx_wilder_14`,
- S3-Gültigkeitsinformationen,
- `indicator_segment_id`.

Zusätzlich berechnet S4 kausal:

- SMA 200 des gültigen ATR innerhalb desselben Segments,
- SMA 50 des gültigen OBV innerhalb desselben Segments,
- Summe des Volumens über 50 gültige Kerzen.

Diese S4-Hilfsgrößen sind Teil des Signalprofils und keine nachträgliche
Änderung der S3-Indikatorformeln.

### 5.2 Eingabeinvarianten

S4 MUST:

- ausschließlich freigegebene S3-Artefakte konsumieren,
- Schema- und Profilversion prüfen,
- den kanonischen Schlüssel unverändert erhalten,
- Segmentgrenzen respektieren,
- keine ungültigen S3-Werte transformieren.

## 6. Gemeinsame Funktionen

### 6.1 Clipping

`clip(x, a, b) = min(max(x, a), b)`

### 6.2 Vorzeichenfunktion

`sign3(x)`:

- `+1`, wenn `x > 0`,
- `0`, wenn `x = 0`,
- `-1`, wenn `x < 0`.

Float-Gleichheit wird auf dem ungerundeten kanonischen Wert geprüft.

### 6.3 Sichere Division

Eine kontinuierliche Transformation mit Nenner `d` ist regulär gültig, wenn:

`d > 0`

Definierte Nullfälle werden im jeweiligen Abschnitt geregelt. Es darf kein
willkürliches globales Epsilon in die fachliche Formel eingefügt werden.

### 6.4 Vollständige Rolling Windows

S4-Rolling-Hilfsgrößen verwenden:

- ausschließlich dasselbe `indicator_segment_id`,
- vollständige Fenster,
- `min_periods = window`,
- keine synthetischen oder ungültigen Inputs im kanonischen Profil.

## 7. Feldregister

### 7.1 Diskrete Richtungssignale

| Feld | Rolle | Quelle |
|---|---|---|
| `sig_rsi_mr_d` | `DIRECTION_DISCRETE` | RSI 14 |
| `sig_macd_momentum_d` | `DIRECTION_DISCRETE` | MACD-Histogramm |
| `sig_bollinger_mr_d` | `DIRECTION_DISCRETE` | Bollinger Bands |
| `sig_stoch_mr_d` | `DIRECTION_DISCRETE` | Stochastic %K |
| `sig_cci_mr_d` | `DIRECTION_DISCRETE` | CCI |
| `sig_mfi_mr_d` | `DIRECTION_DISCRETE` | MFI |
| `sig_obv_momentum_d` | `DIRECTION_DISCRETE` | OBV relativ zu SMA 50 |
| `sig_roc_momentum_d` | `DIRECTION_DISCRETE` | ROC 12 |

### 7.2 Diskrete Zustände

| Feld | Rolle | Quelle |
|---|---|---|
| `state_ma200_trend_d` | `TREND_STATE` | Close relativ zu SMA 200 |
| `state_ema50_trend_d` | `TREND_STATE` | Close relativ zu EMA 50 |
| `state_atr_relative_d` | `VOLATILITY_STATE` | ATR 14 relativ zu ATR-SMA 200 |
| `state_adx_strength_d` | `TREND_STRENGTH` | ADX 14 relativ zu 25 |

### 7.3 Kontinuierliche Felder

| Feld | Rolle |
|---|---|
| `score_rsi_mr_c` | `DIRECTION_SCORE` |
| `score_macd_momentum_c` | `DIRECTION_SCORE` |
| `score_bollinger_mr_c` | `DIRECTION_SCORE` |
| `score_stoch_mr_c` | `DIRECTION_SCORE` |
| `score_cci_mr_c` | `DIRECTION_SCORE` |
| `score_mfi_mr_c` | `DIRECTION_SCORE` |
| `score_obv_momentum_c` | `DIRECTION_SCORE` |
| `score_roc_momentum_c` | `DIRECTION_SCORE` |
| `score_ma200_trend_c` | `TREND_STATE` |
| `score_ema50_trend_c` | `TREND_STATE` |
| `score_atr_relative_c` | `VOLATILITY_STATE` |
| `score_adx_strength_c` | `TREND_STRENGTH` |

Suffixe:

- `_d`: diskret,
- `_c`: kontinuierlich.

## 8. RSI-Transformation

### 8.1 Diskret

Für gültigen `rsi_wilder_14_t`:

- wenn RSI `< 30`: `sig_rsi_mr_d = +1`,
- wenn RSI `> 70`: `sig_rsi_mr_d = -1`,
- andernfalls: `sig_rsi_mr_d = 0`.

Bei exakt 30 oder 70 ist das Signal neutral.

### 8.2 Kontinuierlich

`score_rsi_mr_c = clip((50 - rsi_wilder_14) / 20, -1, +1)`

Damit gilt:

- RSI 30 oder niedriger: maximal long-supportive,
- RSI 50: neutral,
- RSI 70 oder höher: maximal short-supportive.

## 9. MACD-Transformation

### 9.1 Diskret

`sig_macd_momentum_d = sign3(macd_hist_12_26_9)`

Damit:

- positives Histogramm: `+1`,
- negatives Histogramm: `-1`,
- exakt null: `0`.

### 9.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_macd_momentum_c = clip(macd_hist_12_26_9 / atr_wilder_14, -1, +1)`

Die ATR-Normalisierung macht das Histogramm dimensionslos und reduziert reine
Preisniveaueffekte.

Wenn ATR `= 0`:

- MACD-Histogramm `= 0`: Score `= 0`,
- MACD-Histogramm `!= 0`: ungültig mit
  `SIG_MACD_ZERO_ATR_CONFLICT`.

## 10. Bollinger-Transformation

### 10.1 Diskret

- Wenn `close < bb_lower_20_2`: `sig_bollinger_mr_d = +1`.
- Wenn `close > bb_upper_20_2`: `sig_bollinger_mr_d = -1`.
- Andernfalls: `sig_bollinger_mr_d = 0`.

Bei exakter Berührung eines Bandes ist das Signal neutral.

### 10.2 Kontinuierlich

Definiere:

`half_band_width = bb_upper_20_2 - bb_mid_20`

Wenn `half_band_width > 0`:

`score_bollinger_mr_c = clip((bb_mid_20 - close) / half_band_width, -1, +1)`

Damit:

- unteres Band: `+1`,
- Mittellinie: `0`,
- oberes Band: `-1`.

Wenn `half_band_width = 0`:

- `close = bb_mid_20`: Score `= 0`,
- andernfalls: ungültig mit `SIG_BB_ZERO_WIDTH_CONFLICT`.

## 11. Stochastic-Transformation

### 11.1 Diskret

- Wenn `stoch_k_14 < 20`: `sig_stoch_mr_d = +1`.
- Wenn `stoch_k_14 > 80`: `sig_stoch_mr_d = -1`.
- Andernfalls: `sig_stoch_mr_d = 0`.

Bei exakt 20 oder 80 ist das Signal neutral.

### 11.2 Kontinuierlich

`score_stoch_mr_c = clip((50 - stoch_k_14) / 30, -1, +1)`

Stochastic 20 entspricht `+1`, 50 entspricht `0`, 80 entspricht `-1`.

## 12. CCI-Transformation

### 12.1 Diskret

- Wenn `cci_20 < -100`: `sig_cci_mr_d = +1`.
- Wenn `cci_20 > +100`: `sig_cci_mr_d = -1`.
- Andernfalls: `sig_cci_mr_d = 0`.

Bei exakt `-100` oder `+100` ist das Signal neutral.

### 12.2 Kontinuierlich

`score_cci_mr_c = clip(-cci_20 / 100, -1, +1)`

CCI `-100` entspricht `+1`; CCI `+100` entspricht `-1`.

## 13. MFI-Transformation

### 13.1 Diskret

- Wenn `mfi_14 < 20`: `sig_mfi_mr_d = +1`.
- Wenn `mfi_14 > 80`: `sig_mfi_mr_d = -1`.
- Andernfalls: `sig_mfi_mr_d = 0`.

Bei exakt 20 oder 80 ist das Signal neutral.

### 13.2 Kontinuierlich

`score_mfi_mr_c = clip((50 - mfi_14) / 30, -1, +1)`

MFI 20 entspricht `+1`, 50 entspricht `0`, 80 entspricht `-1`.

## 14. OBV-Transformation

### 14.1 Hilfsgrößen

Innerhalb desselben Segments:

`obv_sma_50_t = mean(obv_i, i=t-49...t)`

`volume_sum_50_t = sum(volume_i, i=t-49...t)`

### 14.2 Diskret

`sig_obv_momentum_d = sign3(obv - obv_sma_50)`

### 14.3 Kontinuierlich

Wenn `volume_sum_50 > 0`:

`score_obv_momentum_c = clip((obv - obv_sma_50) / volume_sum_50, -1, +1)`

Wenn `volume_sum_50 = 0`:

- `obv = obv_sma_50`: Score `= 0`,
- andernfalls: ungültig mit `SIG_OBV_ZERO_VOLUME_CONFLICT`.

### 14.4 Gültigkeit

Beide OBV-Transformationen benötigen 50 gültige OBV- und Volumenwerte
innerhalb desselben Segments.

## 15. ROC-Transformation

### 15.1 Diskret

`sig_roc_momentum_d = sign3(roc_close_12_pct)`

### 15.2 Kontinuierlich

Definiere die aktuelle ATR-Quote:

`atr_fraction_t = atr_wilder_14_t / close_t`

und den ROC als Dezimalreturn:

`roc_fraction_t = roc_close_12_pct_t / 100`

Wenn `atr_fraction_t > 0`:

`score_roc_momentum_c = clip(roc_fraction_t / atr_fraction_t, -1, +1)`

Wenn `atr_fraction_t = 0`:

- ROC `= 0`: Score `= 0`,
- ROC `!= 0`: ungültig mit `SIG_ROC_ZERO_ATR_CONFLICT`.

## 16. MA200-Trendzustand

### 16.1 Diskret

`state_ma200_trend_d = sign3(close - sma_close_200)`

### 16.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_ma200_trend_c = clip((close - sma_close_200) / atr_wilder_14, -1, +1)`

Wenn ATR `= 0`:

- `close = sma_close_200`: Score `= 0`,
- andernfalls: ungültig mit `SIG_MA200_ZERO_ATR_CONFLICT`.

### 16.3 Rolle

Dieses Feld ist ein Trendzustand, kein Entry-Timing-Signal.

## 17. EMA50-Trendzustand

### 17.1 Diskret

`state_ema50_trend_d = sign3(close - ema_close_50)`

### 17.2 Kontinuierlich

Wenn `atr_wilder_14 > 0`:

`score_ema50_trend_c = clip((close - ema_close_50) / atr_wilder_14, -1, +1)`

Wenn ATR `= 0`:

- `close = ema_close_50`: Score `= 0`,
- andernfalls: ungültig mit `SIG_EMA50_ZERO_ATR_CONFLICT`.

### 17.3 Rolle

Dieses Feld ist ein Trendzustand, kein Entry-Timing-Signal.

## 18. ATR-Volatilitätszustand

### 18.1 Hilfsgröße

Innerhalb desselben Segments:

`atr_sma_200_t = mean(atr_wilder_14_i, i=t-199...t)`

### 18.2 Diskret

`state_atr_relative_d = sign3(atr_wilder_14 - atr_sma_200)`

Damit:

- `+1`: ATR oberhalb des 200er-ATR-Mittels,
- `0`: exakt gleich,
- `-1`: ATR unterhalb des Mittels.

Das Vorzeichen beschreibt hohe oder niedrige relative Volatilität, nicht
Long- oder Short-Richtung.

### 18.3 Kontinuierlich

Wenn `atr_wilder_14 > 0` und `atr_sma_200 > 0`:

`score_atr_relative_c = clip(log(atr_wilder_14 / atr_sma_200) / log(2), -1, +1)`

Interpretation:

- ATR doppelt so hoch wie Referenz oder höher: `+1`,
- identische ATR: `0`,
- ATR halb so hoch wie Referenz oder niedriger: `-1`.

Wenn beide Werte null sind:

`score_atr_relative_c = 0`

Wenn `atr_wilder_14 = 0` und `atr_sma_200 > 0`:

`score_atr_relative_c = -1`

Wenn `atr_wilder_14 > 0` und `atr_sma_200 = 0`, ist der Zustand mit
`SIG_ATR_RATIO_ZERO_CONFLICT` ungültig. Dieser Fall verletzt bei einem
vollständigen nichtnegativen 200er-Fenster zugleich eine
Berechnungskonsistenzannahme und muss untersucht werden.

### 18.4 Gültigkeit

Der Zustand benötigt 200 gültige ATR-Werte innerhalb desselben Segments.

## 19. ADX-Trendstärkezustand

### 19.1 Diskret

- Wenn `adx_wilder_14 > 25`: `state_adx_strength_d = 1`.
- Wenn `adx_wilder_14 <= 25`: `state_adx_strength_d = 0`.

Dieses Feld besitzt kein negatives Richtungsvorzeichen.

### 19.2 Kontinuierlich

`score_adx_strength_c = clip((adx_wilder_14 - 15) / 10, 0, 1)`

Damit:

- ADX `<= 15`: `0`,
- ADX `= 20`: `0.5`,
- ADX `>= 25`: `1`.

### 19.3 Rolle

ADX beschreibt Trendstärke. Die Trendrichtung stammt nicht aus ADX, sondern
aus getrennten Trend- oder Regimefeldern.

## 20. Diskrete Regelmatrix

| Feld | `+1` | `0` | `-1` |
|---|---|---|---|
| `sig_rsi_mr_d` | RSI `<30` | RSI `30...70` | RSI `>70` |
| `sig_macd_momentum_d` | Hist `>0` | Hist `=0` | Hist `<0` |
| `sig_bollinger_mr_d` | Close `< lower` | innerhalb inkl. Bänder | Close `> upper` |
| `sig_stoch_mr_d` | %K `<20` | `%K 20...80` | %K `>80` |
| `sig_cci_mr_d` | CCI `<-100` | CCI `-100...100` | CCI `>100` |
| `sig_mfi_mr_d` | MFI `<20` | MFI `20...80` | MFI `>80` |
| `sig_obv_momentum_d` | OBV `> SMA50` | gleich | OBV `< SMA50` |
| `sig_roc_momentum_d` | ROC `>0` | ROC `=0` | ROC `<0` |
| `state_ma200_trend_d` | Close `> SMA200` | gleich | Close `< SMA200` |
| `state_ema50_trend_d` | Close `> EMA50` | gleich | Close `< EMA50` |
| `state_atr_relative_d` | ATR `> ATR-SMA200` | gleich | ATR `< ATR-SMA200` |

`state_adx_strength_d` verwendet ausschließlich `{0,1}`.

## 21. Kontinuierliche Score-Invarianten

MUST gelten:

- alle `DIRECTION_SCORE`-Felder liegen in `[-1,+1]`,
- Trend-Scores liegen in `[-1,+1]`,
- `score_atr_relative_c` liegt in `[-1,+1]`,
- `score_adx_strength_c` liegt in `[0,1]`,
- kein gültiger Score ist `NaN` oder unendlich,
- Clipping wird nach der vollständigen ungerundeten Transformation angewandt.

Clipping darf nicht als Ersatz für einen ungültigen Nenner verwendet werden.

## 22. Warm-up und erste Verfügbarkeit

| Transformation | Zusätzlicher S4-Warm-up |
|---|---:|
| RSI diskret/kontinuierlich | keiner nach gültigem RSI |
| MACD diskret | keiner nach gültigem Histogramm |
| MACD kontinuierlich | gültiges Histogramm und ATR |
| Bollinger diskret/kontinuierlich | keiner nach gültigen Bollinger-Feldern |
| Stochastic diskret/kontinuierlich | keiner nach gültigem %K |
| CCI diskret/kontinuierlich | keiner nach gültigem CCI |
| MFI diskret/kontinuierlich | keiner nach gültigem MFI |
| OBV diskret/kontinuierlich | 50 gültige OBV-/Volumenwerte |
| ROC diskret | keiner nach gültigem ROC |
| ROC kontinuierlich | gültiger ROC und ATR |
| MA200 diskret | gültiger SMA200 |
| MA200 kontinuierlich | gültiger SMA200 und ATR |
| EMA50 diskret | gültiger EMA50 |
| EMA50 kontinuierlich | gültiger EMA50 und ATR |
| ATR relativ | 200 gültige ATR-Werte |
| ADX Stärke | keiner nach gültigem ADX |

Nach einer Segmentgrenze beginnt jeder zusätzliche Rolling-Warm-up erneut.

## 23. Validität und Reason Codes

### 23.1 Pflichtfelder

S4 MUST je Transformation ausweisen:

- gültig/ungültig,
- Profil-ID,
- Profilversion,
- Signalrolle,
- Reason Code bei Ungültigkeit oder Sonderfall.

### 23.2 Mindestcodes

- `SIG_INPUT_INVALID`,
- `SIG_WARMUP_INCOMPLETE`,
- `SIG_WINDOW_CROSSES_GAP`,
- `SIG_PROFILE_MISMATCH`,
- `SIG_NONFINITE_RESULT`,
- `SIG_MACD_ZERO_ATR_CONFLICT`,
- `SIG_BB_ZERO_WIDTH_CONFLICT`,
- `SIG_OBV_ZERO_VOLUME_CONFLICT`,
- `SIG_ROC_ZERO_ATR_CONFLICT`,
- `SIG_MA200_ZERO_ATR_CONFLICT`,
- `SIG_EMA50_ZERO_ATR_CONFLICT`,
- `SIG_ATR_RATIO_ZERO_CONFLICT`.

### 23.3 Propagation

Ist ein erforderlicher S3-Indikator ungültig, ist die abhängige
S4-Transformation ebenfalls ungültig.

Ein nachgelagerter gültiger numerischer Ausdruck darf einen ungültigen
Inputstatus nicht verdecken.

## 24. Keine Aggregation in S4

S4 MUST NOT automatisch:

- Signale summieren,
- Stimmen zählen,
- Mehrheiten bilden,
- Gewichte anwenden,
- Entry-Schwellen prüfen,
- Long-/Short-Freigaben erzeugen.

Eine spätere Strategie darf beispielsweise nur ausgewählte
`DIRECTION_DISCRETE`-Felder zu einem Timing-Score kombinieren. Diese Auswahl
und Gewichtung benötigt jedoch eine eigene versionierte Strategie- oder
Gate-Spezifikation.

## 25. Legacy-Profil

### 25.1 Felder

`LEGACY_BTC_BINARY_V1` erzeugt exakt:

- `legacy_rsi_signal`,
- `legacy_macd_signal`,
- `legacy_bollinger_signal`,
- `legacy_ma200_signal`,
- `legacy_stoch_signal`,
- `legacy_atr_signal`,
- `legacy_ema50_signal`,
- `legacy_adx_signal`,
- `legacy_cci_signal`,
- `legacy_mfi_signal`,
- `legacy_obv_signal`,
- `legacy_roc_signal`.

### 25.2 Regeln

Auf den Legacy-Indikatorwerten:

- `legacy_rsi_signal = 1`, wenn Legacy-RSI `< 30`, sonst `0`.
- `legacy_macd_signal = 1`, wenn Legacy-MACD-Histogramm `> 0`, sonst `0`.
- `legacy_bollinger_signal = 1`, wenn Close `<` Legacy-BB-Lower, sonst `0`.
- `legacy_ma200_signal = 1`, wenn Close `>` Legacy-MA200, sonst `0`.
- `legacy_stoch_signal = 1`, wenn Legacy-Stochastic `< 20`, sonst `0`.
- `legacy_atr_signal = 1`, wenn Legacy-ATR `>` Legacy-ATR-Rolling-Mean-200,
  sonst `0`.
- `legacy_ema50_signal = 1`, wenn Close `>` Legacy-EMA50, sonst `0`.
- `legacy_adx_signal = 1`, wenn Legacy-ADX `> 25`, sonst `0`.
- `legacy_cci_signal = 1`, wenn Legacy-CCI `< -100`, sonst `0`.
- `legacy_mfi_signal = 1`, wenn Legacy-MFI `< 20`, sonst `0`.
- `legacy_obv_signal = 1`, wenn Legacy-OBV `>` Legacy-OBV-Rolling-Mean-50,
  sonst `0`.
- `legacy_roc_signal = 1`, wenn Legacy-ROC `> 0`, sonst `0`.

### 25.3 Historische Warm-up-Semantik

Zur exakten Reproduktion verwendet das Legacy-Profil die historisch
verifizierte Semantik einschließlich:

- `fillna`-Verhalten des Builders,
- Vergleichen mit `NaN`, die `False` und damit `0` ergaben,
- Legacy-Rolling- und EWM-Definitionen.

Diese Semantik ist im kanonischen RCC-Profil unzulässig.

### 25.4 Empirischer Status

Die zwölf Regeln wurden über 2.721.034 vorhandene Zeilen mit null Abweichungen
gegen `data/price_data_with_signals.csv` validiert.

Dies bestätigt das Legacy-Profil, nicht die wissenschaftliche Eignung der
Regeln als neuer Standard.

### 25.5 Keine implizite Short-Inversion

Ein historisches 0/1-Signal darf nicht automatisch durch:

`short_signal = 1 - long_signal`

in ein Short-Signal umgewandelt werden.

„Bullish Bedingung nicht erfüllt“ ist nicht gleichbedeutend mit „bearish
Bedingung erfüllt“.

## 26. Verhältnis zur bestehenden L1-Logik

Die bisherige L1-Architektur verwendet unter anderem:

- RSI,
- Bollinger,
- Stochastic,
- CCI

als Timing-Score und:

- MA200,
- MFI,
- ATR

in getrennten Filter- oder Qualitätsrollen.

RCC-002 bewahrt diese Trennbarkeit durch Rollenmetadaten. Dieses Dokument
übernimmt jedoch keine konkrete bestehende Entry-, Exit- oder Score-Regel.

Eine spätere Vergleichsimplementierung MUST klar ausweisen:

- verwendetes Signalprofil,
- ausgewählte Felder,
- Score-Regel,
- Filter,
- Schwellenwerte,
- zeitliche Persistenzbedingungen.

## 27. Partitions- und Rebuild-Regeln

### 27.1 Partitionsparität

S4-Rolling-Hilfsgrößen benötigen entweder:

- korrektes Overlap oder
- validierten State.

Ein partitionierter S4-Build MUST innerhalb der definierten Toleranz mit einem
seriellen Build übereinstimmen.

### 27.2 Historische Revision

Bei geänderten S3-Werten:

- unmittelbar abhängige Transformationen werden ab der ersten Änderung neu
  berechnet,
- OBV-SMA-50 und Volumensumme-50 werden bis zum Ende ihres Einflussfensters
  neu berechnet,
- ATR-SMA-200 wird bis zum Ende seines Einflussfensters neu berechnet,
- nachgelagerte Regime, Gates und Strategieresultate werden invalidiert.

### 27.3 Segmentänderung

Ändert sich eine Lückenklassifikation oder Segmentgrenze, wird S4 ab dem
betroffenen Segmentbeginn vollständig neu berechnet.

## 28. Ausgabevertrag

### 28.1 Pflichtmetadaten

S4 erzeugt:

- `signal_profile_id`,
- `signal_profile_version`,
- `signal_schema_version`,
- Rollenregister,
- Validitätsfelder,
- Reason Codes,
- Transformationsbericht,
- Output-Checksumme.

### 28.2 Zeileninvariante

S4 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S3-Werte verändern.

Es muss gelten:

`S4_rows = S3_rows`

und alle kanonischen Schlüssel müssen unverändert bleiben.

### 28.3 Typen

- Diskrete Richtungssignale: nullable signed integer.
- Diskrete Trendzustände: nullable signed integer.
- Diskrete ADX-Stärke: nullable unsigned integer oder Boolean mit
  dokumentierter Semantik.
- Kontinuierliche Scores: `float64`.
- Validität: Boolean plus Reason Code.

## 29. Testanforderungen

### 29.1 Grenzwerttests

Für jede diskrete Regel MUST getestet werden:

- knapp unter Schwelle,
- exakt auf Schwelle,
- knapp über Schwelle,
- ungültiger Input.

### 29.2 Vorzeichentests

MUST gelten:

- überverkaufte Mean-Reversion-Zustände erzeugen positive Evidenz,
- überkaufte Mean-Reversion-Zustände erzeugen negative Evidenz,
- positives Momentum erzeugt positive Evidenz,
- negatives Momentum erzeugt negative Evidenz,
- ATR und ADX erzeugen keine Short-/Long-Richtung.

### 29.3 Kontinuierliche Ankerwerte

Mindestens zu testen:

- RSI 30/50/70,
- Stochastic 20/50/80,
- MFI 20/50/80,
- CCI -100/0/+100,
- Close auf BB-Lower/Mid/Upper,
- ADX 15/20/25,
- ATR-Verhältnis 0.5/1/2,
- positive, negative und null normalisierte Momentumwerte.

### 29.4 Monotonietests

Innerhalb des nicht geclippten Bereichs MUST gelten:

- fallender RSI erhöht den Mean-Reversion-Long-Score,
- steigender CCI senkt den Mean-Reversion-Long-Score,
- steigendes MACD-Histogramm erhöht den Momentumscore,
- steigender Close-Abstand über MA/EMA erhöht den Trendscore,
- steigender ADX erhöht oder erhält den Trendstärkescore.

### 29.5 Kausalitätstest

Änderungen nach Zeitpunkt `t` dürfen kein S4-Feld bei `t` verändern.

### 29.6 Legacy-Golden-Test

Das Legacy-Profil MUST die zwölf historischen Signalspalten über den bekannten
Datensatz mit null Regelabweichungen reproduzieren.

### 29.7 Rollen-Sicherheitstest

Ein Schema- oder Aggregationsvalidator MUST verhindern, dass Felder mit Rolle:

- `VOLATILITY_STATE`,
- `TREND_STRENGTH`

ohne explizite Transformationsregel als `DIRECTION_DISCRETE` oder
`DIRECTION_SCORE` behandelt werden.

## 30. Numerische Toleranzen

Für unabhängige `float64`-Vergleiche gelten standardmäßig:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Diskrete Entscheidungen werden aus ungerundeten Werten gebildet.

Ein Wert innerhalb numerischer Vergleichstoleranz zur Schwelle wird nicht
automatisch als gleich behandelt. Falls eine Schwellen-Hysterese erforderlich
ist, muss sie separat spezifiziert und versioniert werden.

## 31. Transformationsbericht

Der Bericht enthält mindestens:

- Build-, Profil- und Schemaversion,
- Eingabe- und Ausgabezeilen,
- gültige und ungültige Werte je Feld,
- Häufigkeit `-1`, `0`, `+1` je diskretem Feld,
- Minimum, Maximum, Mittelwert und Quantile je kontinuierlichem Feld,
- Clipping-Anteil bei `-1` und `+1`,
- Reason-Code-Häufigkeiten,
- erste gültige Zeit je Feld und Segment,
- Rollenregisterprüfung,
- Kausalitäts- und Partitionsparität,
- Legacy-Vergleich,
- Output-Checksumme.

Ein sehr hoher Clipping-Anteil ist kein automatischer Fehler, erzeugt aber ein
Review-Finding.

## 32. Publication Gate

S4 darf nur veröffentlicht werden, wenn:

1. S3 vollständig freigegeben ist,
2. alle aktiven Profile registriert sind,
3. Vorzeichen- und Rollenregeln bestanden sind,
4. alle diskreten Werte im zulässigen Wertebereich liegen,
5. alle kontinuierlichen Werte im zulässigen Wertebereich liegen,
6. ungültige Inputs korrekt propagiert wurden,
7. keine nicht endlichen gültigen Scores bestehen,
8. Zeilen und vorgelagerte Felder unverändert sind,
9. Grenzwert-, Ankerwert-, Monotonie- und Kausalitätstests bestanden sind,
10. partitionierter und serieller Build übereinstimmen,
11. Legacy- und RCC-Felder strikt getrennt sind,
12. Manifest, Rollenregister und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

## 33. Abnahmekriterien

`RCC_002_SIGNAL_TRANSFORMATION` ist implementierungsreif, wenn:

1. alle Transformationen als eigenständige Funktionen testbar sind,
2. jede Transformation eine feste Profil- und Feldversion besitzt,
3. Grenzwerte und Gleichheitsfälle vollständig getestet sind,
4. kontinuierliche Ankerwerte und Nullfälle getestet sind,
5. Rollen-Sicherheit technisch erzwungen wird,
6. Legacy-Reproduktion bestanden ist,
7. Lücken- und Partitionsparität bestanden sind,
8. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist,
9. keine ungeklärten Regel- oder Vorzeichenkonflikte bestehen,
10. Manifest und Knowledge Lineage vollständig sind.

## 34. Freigabestatus und nächster Schritt

Diese Spezifikation wurde vor ihrer ersten Ausgabe intern auf methodische,
mathematische, strukturelle und terminologische Konsistenz geprüft.

Der fokussierte Re-Review `RCC-002-SCR-003` identifizierte
`SCR-003-B02`: Die Metadaten referenzierten veraltete Versionen der
übergeordneten Data Pipeline Specification sowie der direkten Data Validation
und Indicator Specifications.

Version 0.2.0 korrigiert die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.5.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.2.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.2.0
```

Die fachlichen Signaltransformationen wurden dabei nicht verändert.

Sie ist noch nicht wissenschaftlich zertifiziert. Der Status bleibt:

```text
SCR-003-Corrected Draft – Re-Review Pending
```

Nächster fachlicher Schritt:

Fokussierter Scientific Consistency Re-Review von `SCR-003-B02` gemeinsam
mit der vollständigen korrigierten RCC-002-Spezifikationsfamilie.

---

# Eingebettetes Dokument 5 von 7

## Quelldatei: `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`

# RCC-002 Regime and Gate Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-RG |
| Titel | Regime and Gate Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Version | 0.3.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.5.0 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.2.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.2.0; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.2.0 |
| Geltungsbereich | S5_REGIMES und S6_GATES der RCC-002-Datenpipeline |
| Referenziert durch | Strategieforschung; Backtests; Regimeanalyse; Paper-/Live-Parität; spätere adaptive Steuerung |
| Autoritative Sprache | Englische Feldnamen, Profil-IDs, Zustände und Regeln sind normativ; deutsche Erläuterungen präzisieren die Semantik |

### Review-Nachweis

| Prüfung | Status | Ergebnis |
|---|---|---|
| Struktur- und Nummerierungsprüfung | Bestanden | Regime-, Kontext- und Gate-Ebenen vollständig |
| Verantwortlichkeitstrennung | Bestanden | Marktklassifikation, Trendstärke, Volatilität und Handelsfreigabe getrennt |
| State-Machine-Prüfung | Bestanden | Initialisierung, Persistenz, Übergänge und Segment-Reset eindeutig |
| Fail-closed-Prüfung | Bestanden | Ungültige oder unbekannte Zustände blockieren aktivierte Gates |
| Kausalitätsprüfung | Bestanden | Keine zukunftsbezogenen Regime- oder Gate-Regeln |
| Legacy-Trennungsprüfung | Bestanden | Historische und GS-nahe Vergleichsprofile bleiben nichtkanonische Referenzen |
| Strategietrennungsprüfung | Bestanden | L1-Timing, MFI-Filter, Cooldown und Exit-Regeln nicht in S5/S6 verschoben |
| Scientific Consistency Review | Nicht bestanden; zweite Korrektur eingearbeitet | Frühere Befunde geschlossen; `SCR-003-B01` und `SCR-003-B02` aus `RCC-002-SCR-003` in Version 0.3.0 korrigiert; fokussierter Re-Review ausstehend |
| Architecture Integrity Review | Ausstehend | Nach bestandenem fokussierten Scientific Consistency Re-Review |
| Editorial Pass | Ausstehend | Nach bestandenem Architecture Integrity Review |
| Internal Certification | Ausstehend | Nach bestandenem Editorial Pass |
| Claude Independent Architecture Review | Ausstehend | Erst nach Internal Certification |
| Gemini Independent Scientific and Adversarial Audit | Ausstehend | Erst nach bestandenem Claude-Review |
| ChatGPT Final Consolidation | Ausstehend | Erst nach abgeschlossenem Gemini-Audit |
| Baseline V1 Certified | Nicht erreicht | Erst nach Schließung aller wesentlichen Befunde |

## 1. Zweck

Dieses Dokument definiert:

1. die kausale Beschreibung des Marktregimes in S5 und
2. die davon getrennte Erzeugung von Long-/Short-Freigaben in S6.

Die Spezifikation verhindert, dass:

- eine Marktbezeichnung automatisch als Handelsentscheidung gilt,
- ADX als Richtungsindikator missverstanden wird,
- Volatilität ein implizites Long-/Short-Vorzeichen erhält,
- bestehende Strategieparameter in die Datenpipeline einwandern,
- Regimeregeln anhand späterer Performance rückwirkend umbenannt werden,
- ungültige Daten als neutrales oder handelbares Regime erscheinen.

## 2. Geltungsbereich

### 2.1 Enthalten

Enthalten sind:

- Trendrichtungsregime,
- persistiertes effektives Regime,
- richtungslose Trendstärke,
- relative Volatilität,
- Datenqualitäts-Gate,
- offene Forschungsfreigabe,
- trendgerichtete Gate-Profile,
- Gate-Komposition,
- Reason Codes,
- Legacy- und Vergleichsprofile,
- Tests, Reports und Publication Gates.

### 2.2 Nicht enthalten

Nicht enthalten sind:

- Timing-Score aus RSI, Bollinger, Stochastic und CCI,
- MFI-Entry-Filter,
- Entry-Persistenz einer konkreten Strategie,
- Cooldown,
- Loss-Cluster-Gate,
- TP, SL oder Time-Stop,
- Exit-Regeln,
- Positionsgröße und Kapitalallokation,
- Equity- oder Portfolio-Gates,
- endgültige Aktivierung eines Forschungs-Gates im Live-Betrieb.

Diese Elemente benötigen eigene Strategie-, Execution- oder Risk-Spezifikationen.

## 3. Verantwortlichkeitsebenen

### 3.1 S5 – Marktklassifikation

S5 beantwortet ausschließlich:

- Welche langfristige Trendrichtung ist zum Zeitpunkt `t` beobachtbar?
- Wie stark ist der Trend?
- Liegt die aktuelle ATR oberhalb oder unterhalb ihrer Referenz?
- Ist der Zustand gültig und ausreichend warmgelaufen?

### 3.2 S6 – Handelsfreigabe

S6 beantwortet:

- Darf eine nachgelagerte Strategie Long-Signale prüfen?
- Darf eine nachgelagerte Strategie Short-Signale prüfen?
- Welche Gate-Regel erlaubt oder blockiert die jeweilige Richtung?

### 3.3 Strategieebene

Die Strategieebene entscheidet:

- ob ein konkretes Entry-Signal vorliegt,
- welche Timing-Signale kombiniert werden,
- welche Persistenz ein Entry benötigt,
- ob MFI oder andere Signale als Filter gelten,
- wann eine Position geschlossen wird.

Ein `allow_long = true` erzeugt keinen Long-Trade.

## 4. Vorzeichen- und Zustandssemantik

### 4.1 Trendrichtung

Zulässige Werte:

- `BULL`,
- `SIDE`,
- `BEAR`,
- `UNKNOWN`.

### 4.2 Trendstärke

Zulässige Werte:

- `WEAK`,
- `DEVELOPING`,
- `STRONG`,
- `UNKNOWN`.

Trendstärke besitzt keine Long-/Short-Richtung.

### 4.3 Relative Volatilität

Zulässige Werte:

- `BELOW_REFERENCE`,
- `AT_REFERENCE`,
- `ABOVE_REFERENCE`,
- `UNKNOWN`.

Relative Volatilität besitzt keine Long-/Short-Richtung.

### 4.4 Gate

Long und Short werden getrennt als Boolean gespeichert:

- `allow_long`,
- `allow_short`.

Ein Gate darf beide Richtungen:

- erlauben,
- blockieren

oder nur eine Richtung erlauben.

## 5. Profile und Status

### 5.1 `RCC_TREND_REGIME_RAW_V1`

Kanonische kausale Rohklassifikation anhand:

- Close relativ zu SMA 200,
- kausaler SMA-200-Slope über 1.440 Minuten.

### 5.2 `RCC_TREND_REGIME_PERSISTED_V1`

Persistierte Zustandsmaschine auf Basis des Rohregimes mit:

`confirm_bars = 3`

### 5.3 `RCC_CONTEXT_V1`

Ergänzt:

- ADX-Trendstärke,
- ATR-Relativzustand.

Diese Felder ändern die Regimebezeichnung nicht.

### 5.4 `GATE_RESEARCH_OPEN_V1`

Erlaubt bei gültiger Daten- und Featurelage beide Richtungen.

Dies ist das kanonische Standardprofil für unvoreingenommene
Strategieforschung, weil es keine ungeprüfte Regimezensur einführt.

### 5.5 `GATE_TREND_ALIGNED_V1`

Forschungsprofil:

- effektives Bull-Regime erlaubt Long,
- effektives Bear-Regime erlaubt Short,
- Side und Unknown blockieren beide Richtungen.

ADX wird in diesem Profil nicht als Mindestbedingung verwendet.

### 5.6 `GATE_TREND_STRENGTH_ALIGNED_V1`

Forschungsprofil:

- wie `GATE_TREND_ALIGNED_V1`,
- zusätzlich ADX `> 15`.

Dieses Profil muss vor einer produktiven Aktivierung separat falsifiziert und
Out-of-Sample validiert werden.

### 5.7 Legacy- und Rekonstruktionsprofile

- `LEGACY_BTC_REGIME_V1`,
- `GS_REGIME_RECONSTRUCTION_V1`.

Diese Profile dienen Vergleich und Lineage. Sie sind nicht automatisch
kanonische RCC-002-Gates.

## 6. Eingabevertrag

### 6.1 Pflichtfelder

S5 benötigt:

- `open_time`,
- `close`,
- `sma_close_200`,
- `state_atr_relative_d`,
- `score_atr_relative_c`,
- `adx_wilder_14`,
- `state_adx_strength_d`,
- `score_adx_strength_c`,
- S2-, S3- und S4-Gültigkeitsfelder,
- `indicator_segment_id`.

Optionale Vergleichs- und Transparenzfelder:

- `state_ma200_trend_d`,
- `state_ema50_trend_d`,
- `sig_roc_momentum_d`.

Legacy- oder Rekonstruktionsprofile dürfen zusätzliche profilgebundene
Pflichtfelder verlangen. Diese werden nicht zu allgemeinen
RCC-TREND-REGIME-Pflichtfeldern.

### 6.2 S5-Hilfsgröße

S5 berechnet den kausalen SMA-200-Slope:

`ma200_slope_1440_pct_t = 100 * (sma_close_200_t / sma_close_200_(t-1440) - 1)`

Voraussetzungen:

- beide SMA-Werte gültig,
- beide Werte größer als null,
- alle erforderlichen Zeitpunkte gehören zum selben Segment,
- zwischen den Vergleichspunkten liegt keine Datenlücke.

### 6.3 S6-Pflichtfelder

S6 benötigt:

- S5-Rohregime,
- S5-effektives Regime,
- Trendstärke,
- Volatilitätszustand,
- Datenqualitätsstatus,
- aktive Gate-Profil-ID und Version.

### 6.4 Eingabeinvarianten

S5 und S6 MUST:

- ausschließlich freigegebene vorgelagerte Artefakte konsumieren,
- Schema- und Profilversionen prüfen,
- kanonische Schlüssel unverändert erhalten,
- Segmentgrenzen respektieren,
- ungültige Inputs nicht als neutral interpretieren.

## 7. Rohregime

### 7.1 Bull

`regime_raw = BULL`, wenn gleichzeitig:

- `close > sma_close_200`,
- `ma200_slope_1440_pct > 0`.

### 7.2 Bear

`regime_raw = BEAR`, wenn gleichzeitig:

- `close < sma_close_200`,
- `ma200_slope_1440_pct < 0`.

### 7.3 Side

`regime_raw = SIDE`, wenn alle erforderlichen Inputs gültig sind und weder die
Bull- noch die Bear-Regel vollständig erfüllt ist.

Insbesondere Side:

- Close oberhalb SMA200 bei nichtpositivem Slope,
- Close unterhalb SMA200 bei nichtnegativem Slope,
- exakte Preisgleichheit,
- exakter Slope null.

### 7.4 Unknown

`regime_raw = UNKNOWN`, wenn:

- SMA200 oder Slope ungültig ist,
- Warm-up unvollständig ist,
- das Fenster eine Lücke überschreitet,
- ein erforderlicher Input nicht endlich ist,
- Profil- oder Segmentkonsistenz fehlt.

### 7.5 Exklusivität

Für jede gültige Zeile gilt genau eine Klasse:

`BULL XOR SIDE XOR BEAR`

`UNKNOWN` ist ausschließlich ein Invalid-/Unavailable-Zustand.

## 8. Warm-up

### 8.1 SMA200

Der erste SMA200 ist innerhalb eines neuen Segments am Index:

`199`

gültig.

### 8.2 Slope

Der erste Slope benötigt zusätzlich 1.440 Minuten Abstand.

Damit liegt der erste mögliche Rohregimewert innerhalb eines lückenfreien
1-Minuten-Segments am Index:

`199 + 1440 = 1639`

Erforderlich sind 1.640 aufeinanderfolgende Kerzen.

### 8.3 Persistiertes Regime

Das effektive Regime benötigt anschließend drei identische gültige Rohzustände.

Der früheste mögliche effektive Zustand liegt daher am Index:

`1641`

### 8.4 Segmentwechsel

Nach jeder Segmentgrenze beginnt der vollständige Warm-up erneut.

## 9. Persistierte Regime-Zustandsmaschine

### 9.1 Zweck

Das persistierte Regime reduziert kurzzeitige Zustandswechsel, ohne
Zukunftsdaten zu verwenden.

### 9.2 Zustandsvariablen

- `regime_effective`,
- `regime_candidate`,
- `regime_candidate_count`,
- `regime_transition_flag`,
- `regime_transition_from`,
- `regime_transition_to`.

### 9.3 Initialisierung

Am Segmentanfang:

- `regime_effective = UNKNOWN`,
- `regime_candidate = UNKNOWN`,
- `regime_candidate_count = 0`.

### 9.4 Verarbeitung eines gültigen Rohzustands

Für `regime_raw_t` in `{BULL, SIDE, BEAR}`:

1. Wenn `regime_raw_t = regime_candidate_(t-1)`:
   - setze `regime_candidate_count =
     min(regime_candidate_count_(t-1) + 1, 3)`.
2. Andernfalls:
   - setze `regime_candidate = regime_raw_t`,
   - setze `regime_candidate_count = 1`.
3. Wenn:
   - `regime_candidate_count >= 3` und
   - `regime_candidate != regime_effective`,
   dann wird `regime_effective = regime_candidate`.
4. Andernfalls bleibt `regime_effective` unverändert.

### 9.5 Verarbeitung von Unknown

Wenn `regime_raw_t = UNKNOWN`:

- `regime_effective_t = UNKNOWN`,
- Candidate und Count werden zurückgesetzt,
- beide Richtungen werden in fail-closed Gates blockiert.

Nach Rückkehr gültiger Daten beginnt die Dreifachbestätigung neu.

### 9.6 Übergangszeitpunkt

Ein Übergang wird auf der dritten bestätigenden geschlossenen Kerze wirksam.

Die Gate-Wirkung darf frühestens nach dem Verfügbarkeitszeitpunkt dieser Kerze
verwendet werden.

Bei einem tatsächlichen Wechsel gilt:

- `regime_transition_flag = true`,
- `regime_transition_from` enthält den vorherigen effektiven Zustand,
- `regime_transition_to` enthält den neuen effektiven Zustand.

Ohne Wechsel gilt:

- `regime_transition_flag = false`,
- From und To sind `null`.

### 9.7 Keine rückwirkende Umschreibung

Die ersten beiden Candidate-Kerzen behalten das vorherige effektive Regime.
Nach der dritten Bestätigung werden frühere Zeilen nicht rückwirkend geändert.

## 10. Trendstärke

### 10.1 Definition

Auf gültigem `adx_wilder_14`:

- ADX `<= 15`: `trend_strength = WEAK`,
- ADX `> 15` und `<= 25`: `trend_strength = DEVELOPING`,
- ADX `> 25`: `trend_strength = STRONG`.

### 10.2 Unknown

Bei ungültigem ADX:

`trend_strength = UNKNOWN`

### 10.3 Richtungsfreiheit

`STRONG` bedeutet nicht Bull und nicht Bear.

Trendrichtung und Trendstärke dürfen nur durch eine explizite Gate-Regel
kombiniert werden.

## 11. Relative Volatilität

### 11.1 Definition

Auf gültigem `state_atr_relative_d`:

- `-1`: `volatility_relative = BELOW_REFERENCE`,
- `0`: `volatility_relative = AT_REFERENCE`,
- `+1`: `volatility_relative = ABOVE_REFERENCE`.

### 11.2 Unknown

Bei ungültigem ATR-Relativzustand:

`volatility_relative = UNKNOWN`

### 11.3 Richtungsfreiheit

`ABOVE_REFERENCE` ist weder bullish noch bearish.

Die bestehende L1-Erkenntnis, dass ATR-Kontexte unterschiedliche
Entry-Schwellen benötigen können, gehört in eine separat versionierte
Strategieregel und nicht in die S5-Regimebezeichnung.

## 12. S5-Ausgabefelder

S5 erzeugt mindestens:

- `regime_raw`,
- `regime_effective`,
- `regime_candidate`,
- `regime_candidate_count`,
- `regime_transition_flag`,
- `regime_transition_from`,
- `regime_transition_to`,
- `ma200_slope_1440_pct`,
- `trend_strength`,
- `volatility_relative`,
- `regime_model_id`,
- `regime_model_version`,
- `regime_valid`,
- `regime_reason_codes`.

Optionale transparente Evidenzfelder:

- `regime_price_above_ma200`,
- `regime_price_below_ma200`,
- `regime_slope_positive`,
- `regime_slope_negative`.

## 13. Datenqualitäts-Gate

### 13.1 Zweck

Vor jeder Richtungsregel wird ein gemeinsames Datenqualitäts-Gate angewandt.

### 13.2 `data_gate_pass`

`data_gate_pass = true` nur, wenn:

- aktuelle S2-Zeile freigegeben ist,
- kanonischer Schlüssel und Segmentzuordnung konsistent sind,
- keine aktive kritische Qualitätsverletzung vorliegt.

S3-, S4-, Regime- oder ADX-Felder werden erst durch die jeweils konsumierende
Strategie beziehungsweise Richtungsregel geprüft. Dadurch bleibt
`GATE_RESEARCH_OPEN_V1` auch während des S3-/S4-/S5-Warm-ups eine tatsächlich
offene Datenqualitätsbaseline, ohne ungültige Strategiefeatures als gültig
umzudefinieren.

### 13.3 Fail-closed

Wenn `data_gate_pass = false`:

- `allow_long = false`,
- `allow_short = false`.

Dies gilt unabhängig vom gewählten Richtungs-Gate.

## 14. `GATE_RESEARCH_OPEN_V1`

### 14.1 Zweck

Dieses Profil stellt eine unzensierte, aber qualitätsgesicherte
Forschungsbaseline bereit.

### 14.2 Regeln

Wenn `data_gate_pass = true`:

- `allow_long = true`,
- `allow_short = true`.

Andernfalls:

- beide `false`.

### 14.3 Status

Dieses Profil ist der kanonische RCC-002-Standardexport für allgemeine
Strategieforschung.

Es ist kein Live-Risikogate.

## 15. `GATE_TREND_ALIGNED_V1`

### 15.1 Long

`allow_long = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BULL`.

### 15.2 Short

`allow_short = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BEAR`.

### 15.3 Side und Unknown

Bei:

- `SIDE`,
- `UNKNOWN`

werden beide Richtungen blockiert.

### 15.4 ADX

ADX beeinflusst dieses Profil nicht.

Damit kann der isolierte Effekt reiner Trendrichtung untersucht werden.

## 16. `GATE_TREND_STRENGTH_ALIGNED_V1`

### 16.1 Mindeststärke

Zulässige Stärke:

- `DEVELOPING`,
- `STRONG`.

Dies entspricht:

`adx_wilder_14 > 15`

### 16.2 Long

`allow_long = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BULL`,
- `trend_strength in {DEVELOPING, STRONG}`.

### 16.3 Short

`allow_short = true`, wenn:

- `data_gate_pass = true`,
- `regime_effective = BEAR`,
- `trend_strength in {DEVELOPING, STRONG}`.

### 16.4 Blockierung

Beide Richtungen werden blockiert bei:

- Side,
- Unknown,
- Weak,
- unbekannter Trendstärke,
- fehlgeschlagenem Daten-Gate.

## 17. Gate-Komposition

### 17.1 Ausgewähltes Profil

Pro S6-View ist genau ein Richtungsprofil aktiv:

- Research Open,
- Trend Aligned,
- Trend Strength Aligned

oder ein später registriertes Profil.

### 17.2 Kompositionsregel

Für jede Richtung:

`final_allow_direction = data_gate_pass AND profile_allow_direction`

### 17.3 Keine implizite Priorität

Mehrere Richtungsprofile dürfen nicht still durch AND oder OR kombiniert
werden.

Eine kombinierte Policy benötigt:

- eigene Gate-ID,
- eigene Version,
- explizite Wahrheitstabelle,
- eigene Tests.

### 17.4 Long-/Short-Unabhängigkeit

Long und Short werden getrennt berechnet und protokolliert.

Eine blockierte Long-Richtung impliziert keine Short-Freigabe und umgekehrt.

## 18. Gate-Ausgabefelder

Jede S6-View erzeugt:

- `allow_long`,
- `allow_short`,
- `data_gate_pass`,
- `gate_state`,
- `gate_reason_codes_long`,
- `gate_reason_codes_short`,
- `gate_profile_id`,
- `gate_profile_version`,
- `gate_valid`,
- `gate_evaluated_at`,
- referenzierte Regime- und Kontextversion.

`gate_state` besitzt:

- `ALLOW_BOTH`,
- `ALLOW_LONG_ONLY`,
- `ALLOW_SHORT_ONLY`,
- `BLOCK_BOTH`,
- `INVALID`.

Für das jeweils aktive Profil gilt:

- `INVALID`, wenn dessen erforderliche Daten oder Zustände nicht berechenbar
  sind; beide Richtungen sind `false` und `gate_valid = false`.
- `BLOCK_BOTH`, wenn alle erforderlichen Zustände gültig sind, die Policy aber
  keine Richtung erlaubt; `gate_valid = true`.

Ein Unknown-Regime führt daher bei trendgerichteten Profilen zu `INVALID`, beim
regimeunabhängigen `GATE_RESEARCH_OPEN_V1` jedoch nicht.

## 19. Reason Codes

### 19.1 Daten- und Statuscodes

- `GATE_DATA_QUALITY_FAILED`,
- `GATE_INPUT_INVALID`,
- `GATE_WARMUP_INCOMPLETE`,
- `GATE_SEGMENT_RESET`,
- `GATE_REGIME_UNKNOWN`,
- `GATE_TREND_STRENGTH_UNKNOWN`,
- `GATE_PROFILE_MISMATCH`,
- `GATE_STATE_INVALID`.

### 19.2 Richtungsblockierungen

- `GATE_LONG_BLOCKED_SIDE`,
- `GATE_LONG_BLOCKED_BEAR`,
- `GATE_LONG_BLOCKED_WEAK_TREND`,
- `GATE_SHORT_BLOCKED_SIDE`,
- `GATE_SHORT_BLOCKED_BULL`,
- `GATE_SHORT_BLOCKED_WEAK_TREND`.

### 19.3 Freigabecodes

- `GATE_LONG_ALLOWED_RESEARCH_OPEN`,
- `GATE_SHORT_ALLOWED_RESEARCH_OPEN`,
- `GATE_LONG_ALLOWED_BULL`,
- `GATE_SHORT_ALLOWED_BEAR`,
- `GATE_LONG_ALLOWED_BULL_WITH_STRENGTH`,
- `GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH`.

Reason Codes werden als geordnete maschinenlesbare Liste gespeichert.

## 20. Gate-Reason-Priorität

Wenn mehrere Blockierungsgründe vorliegen, gilt für den primären Reason Code:

1. ungültiger State oder Profilfehler,
2. Datenqualitätsfehler,
3. Warm-up oder Segment-Reset,
4. Unknown-Regime oder Unknown-Stärke,
5. Regimerichtung,
6. Trendstärke,
7. sonstige profilbezogene Blockierung.

Alle zusätzlichen Gründe bleiben in der vollständigen Reason-Code-Liste
erhalten.

## 21. Historisches BTC-Regime

### 21.1 Profil

`LEGACY_BTC_REGIME_V1`

### 21.2 Regeln

Bull:

- Close `>` Legacy-MA200,
- Legacy-EMA50 `>` Legacy-MA200,
- Legacy-ROC `> 0`,
- Legacy-ADX `>= 15`.

Bear:

- Close `<` Legacy-MA200,
- Legacy-EMA50 `<` Legacy-MA200,
- Legacy-ROC `< 0`,
- Legacy-ADX `>= 15`.

Sonst:

- Side.

### 21.3 Ausgaben

- `legacy_market_regime`,
- `legacy_regime_signal`,
- `legacy_regime_bull`,
- `legacy_regime_bear`.

### 21.4 Empirischer Status

Die Regeln stimmen über die vorhandenen 1.048.575 Datenzeilen ohne Abweichung
mit der historischen Regimedatei überein.

Die Datei ist wegen ihrer exakten Excel-Grenzgröße und der längeren
vorgelagerten Signaldatei als wahrscheinlich abgeschnittenes
`NON_CANONICAL_LEGACY_ARTIFACT` zu behandeln.

### 21.5 Architektonische Einordnung

Das Legacy-Regime koppelt:

- Trendrichtung,
- Momentum,
- Trendstärke

in einer Klassifikation.

RCC-002 erhält es zur Reproduktion, übernimmt diese Kopplung aber nicht als
kanonische Architektur.

## 22. GS-Rekonstruktionsprofil

### 22.1 Status

`GS_REGIME_RECONSTRUCTION_V1` ist eine rekonstruierte Vergleichshypothese.

Sie ist nicht empirisch vollständig bestätigt, weil der ursprüngliche
kanonische BTC-GS-Datensatz nicht vollständig erhalten ist.

### 22.2 Rekonstruierte Grundstruktur

Nach bisherigem Evidenzstand:

- Regimerichtung über Close relativ zu MA200 und MA200-Slope,
- Long-/Short-Freigaben separat,
- ADX als Gate- oder Stärkeinformation,
- keine unveränderte Übernahme der historischen BTC-Kopplung.

### 22.3 Kennzeichnung

Jede Ausgabe dieses Profils MUST:

- `reconstruction_status = HYPOTHESIS`,
- Evidenzquellen,
- offene Unsicherheiten,
- rekonstruierte Parameter

im Manifest dokumentieren.

Sie darf nicht als verifizierte historische Wahrheit bezeichnet werden.

## 23. Verhältnis zur bestehenden L1-Baseline

### 23.1 Aktuelle empirische Referenz

Die bestehende L1-Baseline nutzt:

- MA200 als Long-/Short-Trendfilter,
- MFI als gerichteten Entry-Filter,
- ATR als Qualitätskontext für unterschiedliche Timing-Schwellen,
- einen Timing-Score aus RSI, Bollinger, Stochastic und CCI.

### 23.2 Trennung in RCC-002

Davon gehören:

- MA200-Marktzustand grundsätzlich in S5,
- ATR-Relativzustand grundsätzlich in S5,
- Timing-Score, MFI-Filter und ATR-abhängige Entry-Schwellen in die
  Strategieebene.

### 23.3 Keine automatische Übernahme

Die profitable L1-Baseline belegt nicht automatisch, dass
`GATE_TREND_STRENGTH_ALIGNED_V1` überlegen ist.

Die bisherigen Regimeauswertungen basieren auf bereits ausgewählten Trades und
sind deshalb keine unverzerrte Bewertung aller blockierten und erlaubten
Marktzeitpunkte.

Eine Gate-Aktivierung benötigt eine separate Counterfactual-Analyse.

## 24. Counterfactual-Gate-Evaluation

### 24.1 Zweck

Ein Gate muss nicht nur die ausgeführten Trades analysieren, sondern auch:

- welche Baseline-Trades es erlaubt hätte,
- welche Baseline-Trades es blockiert hätte,
- welche Gewinne und Verluste jeweils betroffen wären,
- wie sich Tradezahl und Marktphasenabdeckung verändern.

### 24.2 Pflichtgruppen

Für jedes Kandidatengate:

1. `ALLOWED_AND_TRADED`,
2. `BLOCKED_BUT_BASELINE_TRADED`,
3. `ALLOWED_NO_BASELINE_ENTRY`,
4. `INVALID_OR_UNKNOWN`.

### 24.3 Mindestmetriken

- Tradezahl,
- Return,
- Profit Factor,
- Winrate,
- Max Drawdown,
- durchschnittlicher PnL,
- Long/Short getrennt,
- Regime und Volatilitätskontext,
- Zeitfensterstabilität,
- Anteil blockierter Gewinner und Verlierer,
- längste Blockierungssequenz.

### 24.4 Keine In-Sample-Aktivierung

Ein Gate darf nicht allein anhand desselben Zeitraums ausgewählt und bewertet
werden.

Erforderlich sind:

- Entwicklungszeitraum,
- Validierungszeitraum,
- unberührter Testzeitraum,
- Walk-Forward- oder vergleichbare zeitgerechte Prüfung.

## 25. Falsifikationskriterien

Ein Forschungs-Gate gilt als nicht ausreichend gestützt, wenn mindestens eine
der folgenden Bedingungen eintritt:

- Verbesserung stammt nur aus einem einzelnen Zeitfenster,
- Tradezahl sinkt so stark, dass Ergebnisse statistisch nicht belastbar sind,
- Drawdown verschlechtert sich wesentlich,
- Profit Factor steigt nur durch wenige extreme Gewinner,
- Long oder Short wird strukturell unzureichend abgedeckt,
- Gate blockiert überproportional robuste Gewinner,
- Ergebnisse brechen bei kleinen Schwellenänderungen zusammen,
- Wirkung verschwindet nach Gebühren und Slippage,
- Vorteil besteht nur auf zur Auswahl verwendeten Daten,
- Unknown- oder Side-Anteil verhindert praktisch den Betrieb.

Konkrete numerische Akzeptanzgrenzen werden vor den Gate-Experimenten in einem
separaten Testplan präregistriert.

## 26. Kausalität und Verfügbarkeit

### 26.1 Kerzenschluss

Regime und Gates bei `t` verwenden ausschließlich vollständig geschlossene und
verfügbare Kerzen bis einschließlich `t`.

### 26.2 Früheste Nutzung

Ein bei Kerze `t` berechneter Gate-Zustand darf frühestens nach dem
Verfügbarkeitszeitpunkt der geschlossenen Kerze `t` verwendet werden.

### 26.3 Keine Zukunftsbestätigung

Unzulässig sind:

- zentrierte Slope-Fenster,
- spätere Preisbewegungen zur Bestätigung früherer Regime,
- rückwirkende Umbenennung von Übergangsperioden,
- Forward Returns als Regimeinput,
- nachträgliches Glätten mit zukünftigen Zuständen.

## 27. Lücken und Segmente

### 27.1 Segment-Reset

Bei einer S2-/S3-Segmentgrenze:

- Slope-Warm-up beginnt neu,
- Rohregime bleibt bis dahin Unknown,
- persistierte State Machine wird zurückgesetzt,
- fail-closed Gates blockieren beide Richtungen.

### 27.2 Keine State-Übernahme über Lücken

Ein effektives Bull- oder Bear-Regime darf nicht über eine ungeklärte
Datenlücke fortgeführt werden.

### 27.3 Synthetische Ansicht

Regime auf synthetischen Kontinuitätsdaten benötigt:

- eine eigene Profil-ID,
- einen eigenen Build,
- eine separate Sensitivitätsanalyse.

Es darf das kanonische beobachtete Regime nicht überschreiben.

## 28. Partitionierte Berechnung

### 28.1 State Snapshot

Der S5-State Snapshot enthält mindestens:

- letzte Schlüsselposition,
- Segment-ID,
- letzte 1.440 erforderlichen SMA200-Kontextwerte oder äquivalenten validierten
  Rolling State,
- `regime_effective`,
- `regime_candidate`,
- `regime_candidate_count`,
- Kontextzustände,
- Modell- und State-Schemaversion,
- Checksumme.

### 28.2 Anschlussprüfung

State darf nur übernommen werden, wenn:

- Parent-Build-ID stimmt,
- Schlüssel unmittelbar anschließt,
- kein Gap vorliegt,
- Modellversion identisch ist,
- State-Checksumme stimmt.

### 28.3 Parität

Serielle und partitionierte Berechnung MUST identische diskrete Zustände und
innerhalb der Float-Toleranz identische Slope-Werte erzeugen.

## 29. Historische Revision

Bei einer Änderung von OHLCV-, Indikator- oder Signaldaten:

- Slope wird ab der frühesten betroffenen Abhängigkeit neu berechnet,
- Rohregime wird ab dem ersten betroffenen Zeitpunkt neu berechnet,
- die persistierte State Machine wird ab diesem Punkt bis zum Datensatzende
  neu abgespielt,
- alle abhängigen Gate-Views werden neu erzeugt,
- nachgelagerte Strategie- und Labelartefakte werden invalidiert.

Pfadabhängige Regime dürfen nicht nur lokal zeilenweise korrigiert werden.

## 30. Zeilen- und Dateninvarianten

S5 und S6 dürfen:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine vorgelagerten Werte verändern.

Es muss gelten:

`S5_rows = S4_rows`

`S6_rows = S5_rows`

Alle kanonischen Schlüssel bleiben identisch.

## 31. Testanforderungen für S5

### 31.1 Rohregime-Wahrheitstabelle

Mindestens zu testen:

- Preis über SMA und Slope positiv → Bull,
- Preis unter SMA und Slope negativ → Bear,
- Preis über SMA und Slope null/negativ → Side,
- Preis unter SMA und Slope null/positiv → Side,
- Preis gleich SMA → Side,
- ungültiger Preis, SMA oder Slope → Unknown.

### 31.2 Slope

Tests:

- positiver, negativer und null Slope,
- exakte 1.440-Minuten-Distanz,
- unvollständiger Warm-up,
- Lücke innerhalb des Fensters,
- Segmentwechsel,
- Division durch ungültigen oder nichtpositiven SMA.

### 31.3 State Machine

Mindestens:

- Initialisierung mit drei gleichen Zuständen,
- Candidate-Wechsel vor Bestätigung,
- bestätigter Bull-Side-, Side-Bear- und Bear-Bull-Übergang,
- Unknown-Reset,
- keine rückwirkende Änderung,
- Partitionsgrenze während Candidate Count 1 oder 2.

### 31.4 Kontextzustände

- ADX 15, knapp über 15, 25 und knapp über 25,
- ATR relativ `-1`, `0`, `+1`,
- ungültige Inputs.

## 32. Testanforderungen für S6

### 32.1 Research Open

- gültige Daten → beide erlaubt,
- ungültige Daten → beide blockiert.

### 32.2 Trend Aligned

- Bull → nur Long,
- Bear → nur Short,
- Side → beide blockiert,
- Unknown → beide blockiert.

### 32.3 Trend Strength Aligned

- Bull + Developing/Strong → nur Long,
- Bear + Developing/Strong → nur Short,
- Bull/Bear + Weak → beide blockiert,
- Unknown-Stärke → beide blockiert.

### 32.4 Reason Codes

Für jede Wahrheitstabellenzeile werden geprüft:

- Boolean-Ausgaben,
- `gate_state`,
- primärer Reason Code,
- vollständige Reason-Code-Liste.

### 32.5 Richtungsunabhängigkeit

Blockierung einer Richtung darf die Gegenrichtung nur freigeben, wenn deren
eigene Regel vollständig erfüllt ist.

## 33. Kausalitäts-, Paritäts- und Property-Tests

MUST geprüft werden:

- Änderungen nach `t` verändern S5/S6 bei `t` nicht,
- identische Inputs erzeugen identische Outputs,
- Rohregime ist bei gültigen Inputs exklusiv,
- persistiertes Regime besitzt immer genau einen Zustand,
- Candidate Count ist nie negativ,
- Unknown setzt Candidate State deterministisch zurück,
- fail-closed Daten-Gate erlaubt nie eine Richtung bei ungültigem Zustand,
- serielle und partitionierte Berechnung stimmen überein.

## 34. Regime- und Gate-Bericht

Der Bericht enthält mindestens:

- Build-, Modell- und Profilversionen,
- Zeilenzahl und Zeitbereich,
- ersten gültigen Roh- und effektiven Regimezeitpunkt,
- Roh- und Effektivverteilung,
- Übergangsmatrix,
- Anzahl und Dauer der Regimeepisoden,
- Candidate-Abbrüche vor Bestätigung,
- Trendstärkeverteilung je Regime,
- Volatilitätsverteilung je Regime,
- `allow_long`-/`allow_short`-Anteile,
- Blockierungsgründe,
- Unknown- und Warm-up-Anteil,
- Segment-Resets,
- Partitions- und Kausalitätstests,
- Legacy-Vergleich,
- Checksummen.

## 35. Publication Gate S5

S5 darf nur veröffentlicht werden, wenn:

1. S4 freigegeben ist,
2. Regime- und Kontextprofile registriert sind,
3. Slope und Warm-up korrekt sind,
4. Rohregime-Wahrheitstabelle bestanden ist,
5. State-Machine-Tests bestanden sind,
6. Unknown korrekt propagiert wird,
7. keine Lücke überbrückt wird,
8. serielle und partitionierte Berechnung übereinstimmen,
9. Zeilen und vorgelagerte Werte unverändert sind,
10. Manifest, State-Schema und Checksummen vollständig sind.

## 36. Publication Gate S6

S6 darf nur veröffentlicht werden, wenn:

1. S5 freigegeben ist,
2. Gate-Profil registriert ist,
3. Daten-Gate fail-closed arbeitet,
4. Long-/Short-Wahrheitstabellen bestanden sind,
5. Reason Codes vollständig sind,
6. keine ungültige Zeile eine Richtung erlaubt,
7. Gate-Komposition eindeutig ist,
8. serielle und partitionierte Berechnung übereinstimmen,
9. Zeilen und vorgelagerte Werte unverändert sind,
10. Manifest und Checksummen vollständig sind.

Der jeweilige Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

## 37. Abnahmekriterien

`RCC_002_REGIME_AND_GATE_SPECIFICATION` ist implementierungsreif, wenn:

1. Roh- und Persistenzregime vollständig implementiert und getestet sind,
2. Trendstärke und Volatilität richtungsfrei bleiben,
3. alle Gate-Profile getrennt testbar sind,
4. Daten-Gate und Unknown fail-closed arbeiten,
5. State Snapshot und Partitionsparität bestanden sind,
6. Legacy-Reproduktion und GS-Rekonstruktionsstatus dokumentiert sind,
7. Counterfactual-Evaluationspipeline spezifiziert ist,
8. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist,
9. keine offene kritische Regel- oder Rolleninkonsistenz besteht,
10. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind.

## 38. Freigabe und Aktivierung

### 38.1 Spezifikationsfreigabe

Die technische Spezifikation eines Gate-Profils bedeutet nicht seine
Freigabe für Paper oder Live.

### 38.2 Forschungsstatus

Bis zum Abschluss der Counterfactual- und Out-of-Sample-Validierung gelten:

- `GATE_RESEARCH_OPEN_V1`: kanonische Forschungsbaseline,
- `GATE_TREND_ALIGNED_V1`: Forschungskandidat,
- `GATE_TREND_STRENGTH_ALIGNED_V1`: Forschungskandidat.

### 38.3 Produktive Aktivierung

Eine Aktivierung benötigt:

- präregistrierten Testplan,
- vollständige Vergleichsläufe,
- Scientific Consistency Review,
- Architecture Integrity Review,
- Editorial Pass,
- Internal Certification,
- Claude Independent Architecture Review,
- Gemini Independent Scientific and Adversarial Audit,
- ChatGPT Final Consolidation,
- Status `Baseline V1 Certified`,
- dokumentierte Freigabe,
- versionierte Konfigurationsänderung.

## 39. Freigabestatus und nächster Schritt

Diese Version enthält die Korrekturen aus `RCC-002-SCR-001` für:

- SCR-E01 – beschädigtes Falsifikationskriterium,
- SCR-E02 – beschädigte Passage zur synthetischen Regimeansicht.

Die vollständige Datei wurde danach erneut auf methodische, logische,
strukturelle, terminologische und State-Machine-Konsistenz geprüft.

Der fokussierte Re-Review `RCC-002-SCR-003` bestätigte die früheren
Regime- und Gate-Befunde als geschlossen. Er identifizierte für dieses
Dokument:

- `SCR-003-B01`: Die Review- und Freigabefolge war unvollständig und nannte
  Gemini vor Claude.
- `SCR-003-B02`: Die Metadaten referenzierten veraltete Versionen der
  übergeordneten und direkten Abhängigkeiten.

Version 0.3.0:

- übernimmt die vollständige verbindliche Review- und Freigabesequenz;
- ordnet Claude vor Gemini ein;
- ergänzt Internal Certification, ChatGPT Final Consolidation und
  `Baseline V1 Certified`;
- aktualisiert Data Pipeline auf Version 0.5.0;
- aktualisiert Data Validation, Indicator und Signal Transformation jeweils
  auf Version 0.2.0.

Die fachlichen Regime- und Gate-Regeln wurden dabei nicht verändert.

Sie ist noch nicht wissenschaftlich zertifiziert. Der Status bleibt:

`SCR-003-Corrected Draft – Re-Review Pending`.

Nächster vorgeschriebener Schritt:

Fokussierter Scientific Consistency Re-Review von `SCR-003-B01` und
`SCR-003-B02` gemeinsam mit der vollständigen korrigierten
RCC-002-Spezifikationsfamilie.

---

# Eingebettetes Dokument 6 von 7

## Quelldatei: `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`

# RCC-002 Label and Forward Return Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-LF |
| Titel | Label and Forward Return Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md` |
| Version | 0.2.0 |
| Datum | 2026-07-23 |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.5.0 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.2.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.2.0; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.2.0; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version 0.3.0 |
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
| Scientific Consistency Review | Nicht bestanden; Korrektur eingearbeitet | `SCR-003-B01` und `SCR-003-B02` aus `RCC-002-SCR-003` in Version 0.2.0 korrigiert; fokussierter Re-Review ausstehend |
| Architecture Integrity Review | Ausstehend | Nach bestandenem fokussierten Scientific Consistency Re-Review |
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

S7-Felder MUST:

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

`RCC_FORWARD_HORIZONS_V1` enthält:

| ID | Minuten | Fachlicher Kontext |
|---|---:|---|
| `H001` | 1 | unmittelbar nächste Kerze |
| `H005` | 5 | sehr kurzfristig |
| `H015` | 15 | kurzfristig |
| `H060` | 60 | eine Stunde |
| `H240` | 240 | vier Stunden |
| `H1440` | 1.440 | ein Tag |

### 4.2 Erweiterung

Weitere Horizonte benötigen:

- registrierte Horizon-ID,
- exakte Intervalldefinition,
- aktualisierte Schema- und Labelprofilversion,
- Tests,
- dokumentierte Rebuild-Auswirkung.

### 4.3 Kein implizites Resampling

Ein Horizont von 60 Minuten bedeutet nicht automatisch eine 1h-OHLC-Kerze.

Er bezeichnet in dieser Spezifikation 60 aufeinanderfolgende 1-Minuten-
Intervalle auf der kanonischen 1m-Zeitachse.

## 5. Eingabevertrag

### 5.1 Pflichtfelder

S7 benötigt:

- `open_time`,
- `close_time`,
- `open`,
- `high`,
- `low`,
- `close`,
- S2-Qualitätsfelder,
- Segment-ID,
- kanonischen Schlüssel,
- S6-Build- und Schemaidentität.

### 5.2 Eingabeinvarianten

Vor S7 MUST gelten:

- S6 ist freigegeben,
- Zeilen sind streng zeitlich sortiert,
- Schlüssel sind eindeutig,
- OHLCV-Werte sind gültig,
- Segmentgrenzen sind bekannt,
- keine synthetischen Kerzen befinden sich im kanonischen beobachteten Profil.

### 5.3 Feature-Unabhängigkeit

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

Zusätzliche Profile MAY definieren:

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

Ein Deadband MAY als eigenes Profil eingeführt werden, wenn:

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

Zusätzliche Analyseprofile MAY berechnen:

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

Ein separates Labelprofil MAY später den 60-Minuten-Short-Timeout exakt
modellieren.

## 16. Barrier-Suche

### 16.1 Reihenfolge über Kerzen

Kerzen werden chronologisch von `t+1` bis `t+h` geprüft.

### 16.2 Open-Gap-Priorität

Der Open-Preis einer Kerze ist zeitlich vor deren unbekannter
Intrabar-High-/Low-Reihenfolge beobachtbar.

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

- `barrier_first_hit_bar`,
- `barrier_first_hit_time`,
- `barrier_outcome`.

Offset `1` bezeichnet Kerze `t+1`.

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

`LBL_WINDOW_CROSSES_GAP`

### 17.4 Tail

Für die letzten `h` Zeilen eines Datensatzes fehlen regulär vollständige
Zukunftsdaten.

Diese Werte sind ungültig mit:

`LBL_FUTURE_HORIZON_INCOMPLETE`

Sie werden nicht mit null aufgefüllt und nicht entfernt.

### 17.5 Synthetische Kerzen

Kanonische Labels dürfen keine synthetischen Zukunftskerzen verwenden.

Ein separates Sensitivitätsprofil benötigt eine eigene Labelprofil-ID.

## 18. Label-Validitätsfelder

Für jede Familie und jeden Horizont MUST mindestens verfügbar sein:

- `label_valid_h`,
- `label_reason_codes_h`,
- `label_available_at_h`,
- `label_horizon_bars_h`,
- `label_segment_id_h`.

Wenn mehrere Label-Familien unterschiedliche Voraussetzungen besitzen, werden
familienbezogene Validitätsfelder verwendet.

Ein globales `label_valid` darf unterschiedliche Gültigkeiten nicht verdecken.

## 19. Reason Codes

Mindestcodes:

- `LBL_INPUT_INVALID`,
- `LBL_FUTURE_HORIZON_INCOMPLETE`,
- `LBL_WINDOW_CROSSES_GAP`,
- `LBL_SYNTHETIC_INPUT_DISALLOWED`,
- `LBL_ENTRY_PRICE_INVALID`,
- `LBL_EXIT_PRICE_INVALID`,
- `LBL_NONFINITE_RESULT`,
- `LBL_COST_PROFILE_UNKNOWN`,
- `LBL_HORIZON_PROFILE_UNKNOWN`,
- `LBL_BARRIER_PROFILE_UNKNOWN`,
- `LBL_BARRIER_BOTH_HIT`,
- `LBL_SCHEMA_MISMATCH`,
- `LBL_PROFILE_MISMATCH`.

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

### 20.4 Profilkollisionen

Werden mehrere Kosten- oder Barrier-Profile in derselben View gespeichert,
MUST der Feldname einen eindeutigen registrierten Profil-Tag enthalten.

Alternativ werden getrennte Views mit identischem Basisschema und jeweils
genau einem Profil erzeugt. Zwei semantisch unterschiedliche Felder dürfen
niemals denselben Namen tragen.

## 21. Output-Profile

### 21.1 `FORWARD_RETURNS_GROSS_V1`

Enthält:

- Close-to-Close Long/Short,
- Next-Open-to-Close Long/Short,
- Log Returns.

### 21.2 `FORWARD_RETURNS_COST_PROXY_V1`

Ergänzt Net-Proxy-Returns für registrierte Kostenprofile.

### 21.3 `FORWARD_EXCURSIONS_V1`

Enthält MFE, MAE und erste Extrem-Offsets.

### 21.4 `DIRECTION_LABELS_V1`

Enthält Brutto- und optional kostenbereinigte Richtungslabels.

### 21.5 `BARRIER_LABELS_V1`

Enthält Barrier-Outcomes und Trefferzeitpunkte.

### 21.6 Profilkombination

Mehrere Profile dürfen parallel erzeugt werden, wenn:

- Felder eindeutig sind,
- Profil- und Kosten-IDs dokumentiert sind,
- Gültigkeit je Familie erhalten bleibt.

## 22. Zeilen- und Dateninvarianten

S7 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S6-Felder verändern.

Es muss gelten:

`S7_rows = S6_rows`

und alle kanonischen Schlüssel bleiben identisch.

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

Serielle und partitionierte S7-Berechnung MUST:

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

Training, Validierung und Test MUST chronologisch getrennt werden.

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
erzeugen, MAY nach einer Splitgrenze ein Embargo verwendet werden.

Embargo-Länge und Begründung müssen präregistriert werden.

### 25.5 Überlappende Labels

Forward Labels benachbarter Minuten überlappen stark.

Analysen und Unsicherheitsschätzungen MUST diese serielle Abhängigkeit
berücksichtigen. Die rohe Zeilenzahl darf nicht als Zahl unabhängiger
Beobachtungen interpretiert werden.

## 26. Feature-/Label-Trennung

### 26.1 Training View

Eine ML-Training-View enthält:

- freigegebene Features aus S0 bis S6,
- explizit ausgewählte S7-Labels,
- Split- und Purge-Metadaten.

### 26.2 Live-/Paper-View

Eine Live-/Paper-View verwendet eine positive Feld-Allowlist aus S0 bis S6.

Sie MUST sämtliche:

- `fwd_*`,
- `label_*`,
- `barrier_*`

Felder ausschließen.

### 26.3 Automatischer Leakage-Test

Der Leakage-Test MUST fehlschlagen, wenn:

- ein S7-Präfix in einer Live-/Paper-View vorkommt,
- ein Feature erst nach dem Entscheidungszeitpunkt verfügbar ist,
- Splitgrenzen von Labelhorizonten überschritten werden,
- Labelstatistiken zur Feature-Normalisierung verwendet werden.

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

Vor Kosten MUST gelten:

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

MUST gelten:

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

S7 erzeugt mindestens:

- `label_profile_id`,
- `label_profile_version`,
- `label_schema_version`,
- `horizon_registry_id`,
- aktive Kostenprofil-IDs,
- aktive Barrier-Profil-IDs,
- familienbezogene Validitätsfelder,
- S7-Bericht,
- Schema-Fingerprint,
- Output-Checksumme.

Alle Outputfelder müssen über das Schema eindeutig ihrer:

- Familie,
- Richtung,
- Preisreferenz,
- Kostenbasis,
- Horizon-ID

zugeordnet sein.

## 37. Publication Gate

S7 darf nur veröffentlicht werden, wenn:

1. S6 vollständig freigegeben ist,
2. alle Horizonte und Profile registriert sind,
3. Entry-, Exit- und Horizon-Indizes korrekt sind,
4. Long-/Short-Vorzeichenprüfung bestanden ist,
5. Kostenprofile Bruttowerte nicht überschreiben,
6. Gap- und Tail-Regeln korrekt sind,
7. Barrier-Ambiguität erhalten bleibt,
8. keine nicht endlichen gültigen Labels bestehen,
9. Zeilen und S0-bis-S6-Werte unverändert sind,
10. serielle und partitionierte Berechnung übereinstimmen,
11. Leakage- und Allowlist-Tests bestanden sind,
12. Manifest, Schema und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

## 38. Abnahmekriterien

`RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION` ist implementierungsreif,
wenn:

1. alle Return-Familien handberechnet getestet sind,
2. jeder Horizont auf Off-by-one-Fehler geprüft ist,
3. Long-/Short-Symmetrie bestanden ist,
4. Kostenproxy und Bruttowerte getrennt sind,
5. MFE/MAE und Barrier-Logik vollständig getestet sind,
6. Gap-, Tail- und Segmentregeln bestanden sind,
7. Purging und Split-Grenzen getestet sind,
8. S8-Live-/Paper-Allowlist S7 vollständig ausschließt,
9. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist,
10. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind.

## 39. Freigabestatus und nächster Schritt

Diese Spezifikation wurde vor ihrer ersten Ausgabe intern auf methodische,
mathematische, strukturelle und terminologische Konsistenz geprüft.

Der fokussierte Re-Review `RCC-002-SCR-003` identifizierte für dieses
Dokument:

- `SCR-003-B01`: Die Reviewfolge war unvollständig und nannte Gemini vor
  Claude.
- `SCR-003-B02`: Die Metadaten referenzierten veraltete Versionen der
  übergeordneten und direkten Abhängigkeiten.

Version 0.2.0:

- übernimmt die vollständige verbindliche Review- und Freigabesequenz;
- ordnet Claude vor Gemini ein;
- ergänzt Internal Certification, ChatGPT Final Consolidation und
  `Baseline V1 Certified`;
- aktualisiert Data Pipeline auf Version 0.5.0;
- aktualisiert Data Validation, Indicator und Signal Transformation jeweils
  auf Version 0.2.0;
- aktualisiert Regime and Gate auf Version 0.3.0.

Die fachlichen Label- und Forward-Return-Regeln wurden dabei nicht verändert.

Sie ist noch nicht wissenschaftlich zertifiziert. Der Status bleibt:

`SCR-003-Corrected Draft – Re-Review Pending`.

Nächster fachlicher Schritt:

Fokussierter Scientific Consistency Re-Review von `SCR-003-B01` und
`SCR-003-B02` gemeinsam mit der vollständigen korrigierten
RCC-002-Spezifikationsfamilie.

---

# Eingebettetes Dokument 7 von 7

## Quelldatei: `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`

# RCC-002 Reproducibility and Manifest Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Normative technische und wissenschaftliche Spezifikation |
| Speicherort | `docs/specifications/` |
| Dateiname | `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` |
| Dokument-ID | `RCC-002-RM` |
| Version | `0.4.0` |
| Datum | `2026-07-23` |
| Status | SCR-003-Corrected Draft – Re-Review Pending |
| Geltungsbereich | RCC-002-Datenpipeline, Stufen S0–S8 |
| Verbindlichkeit | Normativ für die RCC-002-Implementierung |
| Primäre Abhängigkeit | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version `0.5.0` |
| Fachliche Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version `0.2.0`; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version `0.2.0`; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version `0.2.0`; `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, Version `0.3.0`; `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`, Version `0.2.0` |
| Referenziert durch | RCC-002-Implementierungsplan; RCC-002-Build- und Prüfwerkzeuge; RCC-002-Dataset-Release-Dokumentation |
| Vorgesehene Reviews | Scientific Consistency Review; Architecture Integrity Review; Editorial Pass; Internal Certification; Claude Independent Architecture Review; Gemini Independent Scientific and Adversarial Audit; ChatGPT Final Consolidation; Baseline V1 Certified |

## Review Evidence

### Internal Review

Vor der ersten Ausgabe wurden geprüft:

- methodische Vollständigkeit der Reproduzierbarkeitsanforderungen;
- Trennung von Daten-, Code-, Konfigurations-, Spezifikations- und Umgebungsprovenienz;
- Zirkelfreiheit der Identitäts- und Hashbildung;
- Trennung deterministischer Build-Identitäten von Laufzeitidentitäten;
- Unterscheidung von Bytegleichheit und semantischer Gleichheit;
- Konsistenz mit den RCC-002-Stufen S0–S8;
- Regeln für atomare Veröffentlichung, Wiederaufnahme und Quarantäne;
- geräteübergreifende Reproduktion auf X1, G15 und Workstation;
- Geheimnisbereinigung und Datenschutz;
- Testbarkeit und maschinelle Validierbarkeit;
- Terminologie, Querverweise und normative Sprache.

Ergebnis: Keine bekannte methodische oder logische Blockade für den ursprünglichen Draft-Status.

### Scientific Consistency Review

Der gemeinsame Scientific Consistency Review der RCC-002-Spezifikationsfamilie vom `2026-07-23` wurde in
`docs/review/RCC_002_SPECIFICATION_FAMILY_SCR_REPORT_2026-07-23.md` dokumentiert.

Für dieses Dokument wurden die Befunde `SCR-B04`, `SCR-B05`, `SCR-M01`, `SCR-M02`, `SCR-M03` und `SCR-M04` als korrekturpflichtig übernommen. Version `0.2.0`:

- verwendet den vollständigen registrierten kanonischen Primärschlüssel;
- trennt semantischen Inhalt von physischem Layout;
- bindet JSON-Kanonisierung an RFC 8785/JCS und zusätzliche RCC-Regeln;
- präzisiert die Vorabbildung des `source_snapshot_id`;
- begrenzt E3 auf identische persistierte Artefakte oder identische vollständige Vorabbildungen;
- führt das versionierte Umgebungsidentitätsprofil `RCC_BUILD_ENV_IDENTITY_V1` ein.

Status nach Korrektur: fokussierter SCR-Re-Review ausstehend.

Der Re-Review `RCC-002-SCR-002` bestätigte die sechs vorgenannten Befunde als
geschlossen und identifizierte `SCR-RR-B02`: Physische `artifact_id`s
propagierten in logisch definierte `build_id` und `dataset_id`. Version `0.3.0`
trennt deshalb logische Build- und Dataset-Identität von der physischen
Artefaktmenge und ersetzt für neue Builds
`RCC_BUILD_ENV_IDENTITY_V1` durch das semantisch begrenzte
`RCC_BUILD_ENV_IDENTITY_V2`. Erneuter fokussierter Re-Review: ausstehend.

Der fokussierte Re-Review `RCC-002-SCR-003` bestätigte die früheren Befunde
als geschlossen und identifizierte:

- `SCR-003-B01`: Die Review- und Freigabesequenz wich von der verbindlichen
  RCC-002-Prüfpipeline ab.
- `SCR-003-B02`: Abhängigkeitsversionen waren innerhalb der
  Spezifikationsfamilie veraltet.
- `SCR-003-m01`: Das ID-Beispiel für `dataset_artifact_set_id` fehlte.
- `SCR-003-m02`: Die Unveränderlichkeitsregel war für neue physische
  Artefaktmengen mehrdeutig.

Version `0.4.0` korrigiert alle vier Befunde. Erneuter fokussierter
Re-Review: ausstehend.

### Noch ausstehend

- fokussierter Scientific Consistency Re-Review der korrigierten Befunde;
- Architecture Integrity Review;
- Editorial Pass;
- Internal Certification;
- Claude Independent Architecture Review;
- Gemini Independent Scientific and Adversarial Audit;
- ChatGPT Final Consolidation;
- Baseline V1 Certified;
- Release- und Implementierungsfreigabe.

---

## 1. Zweck

Dieses Dokument definiert, wie jeder RCC-002-Datenstand eindeutig identifiziert, rekonstruiert, geprüft, veröffentlicht und auditiert wird.

Ein RCC-002-Artefakt gilt nur dann als reproduzierbar, wenn mindestens nachvollziehbar ist:

1. aus welchen Quelldaten es entstand;
2. welcher Code verwendet wurde;
3. welche Konfiguration galt;
4. welche Spezifikationsstände verbindlich waren;
5. in welcher Software- und Ausführungsumgebung der Build lief;
6. welche Vorgängerartefakte verarbeitet wurden;
7. welche Prüfungen bestanden wurden;
8. welche Ausgabeartefakte mit welchen Prüfsummen veröffentlicht wurden.

Die Spezifikation verlangt keine bloße Wiederholung eines Dateinamens. Reproduzierbarkeit ist eine überprüfbare Beziehung zwischen Eingaben, Transformationslogik, Umgebung, Ausführung und Ergebnissen.

---

## 2. Normative Begriffe

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **DARF** sind normativ.

| Begriff | Definition |
|---|---|
| Artefakt | Eine gespeicherte Eingabe, Zwischenstufe, Ausgabe, Konfiguration, Prüfausgabe oder Dokumentationseinheit |
| Datenartefakt | Tabellen-, Ereignis-, Parquet-, CSV- oder vergleichbarer Datenbestand |
| Source Snapshot | Unveränderliche, exakt referenzierte Fassung der externen oder rohen Eingabedaten |
| Build | Deterministisch beschriebene Transformation definierter Eingaben mit definiertem Code, Konfiguration und Spezifikationsprofil |
| Run | Konkrete Ausführung eines Builds zu einem bestimmten Zeitpunkt und auf einer bestimmten Umgebung |
| Manifest | Maschinenlesbarer Herkunfts-, Identitäts-, Prüf- und Veröffentlichungsnachweis |
| Bytegleichheit | Identische Bytefolge und damit identischer Datei-Hash |
| Semantische Gleichheit | Gleiche kanonische Dateninhalte trotz möglicherweise unterschiedlicher Containerbytes |
| Dataset Lineage | Abstammung von Datenartefakten über alle Verarbeitungsstufen |
| Knowledge Lineage | Abstammung wissenschaftlicher Regeln, Entscheidungen, Hypothesen und Spezifikationen |
| Publication | Atomare Freigabe eines vollständig geprüften Artefakts |
| Quarantäne | Abgetrennter Status für unvollständige, fehlerhafte oder nicht freigegebene Ergebnisse |

---

## 3. Geltungsbereich

Die Regeln gelten für:

- S0 – Source Acquisition;
- S1 – Raw Normalization;
- S2 – Data Validation;
- S3 – Indicator Computation;
- S4 – Signal Transformation;
- S5 – Regime Classification;
- S6 – Trading Gates;
- S7 – Labels and Forward Returns;
- S8 – Export and Publication;
- zugehörige Prüfberichte, Schemata, Konfigurationen und Manifeste.

Sie gelten für:

- vollständige Builds;
- inkrementelle Builds;
- Wiederholungs- und Reparatur-Builds;
- Forschungsprofile;
- Kandidaten-Releases;
- zertifizierte Releases.

Live- und Paper-Trading-Zustände dürfen auf RCC-002-Daten referenzieren, gehören aber nicht automatisch zum RCC-002-Dataset-Build.

---

## 4. Reproduzierbarkeitsmodell

RCC-002 unterscheidet vier Ebenen:

| Ebene | Frage | Primärer Nachweis |
|---|---|---|
| Provenienz | Woher stammen Regeln und Daten? | Lineage und Referenzen |
| Identität | Welcher logische Build beziehungsweise Run ist gemeint? | IDs |
| Integrität | Wurden Inhalte verändert? | Prüfsummen und Signaturen |
| Reproduktion | Kann das Ergebnis erneut erzeugt und verglichen werden? | Rebuild-Protokoll und Gleichheitsprüfung |

Keine einzelne Prüfsumme ersetzt das vollständige Modell.

---

## 5. Identitätssystem

### 5.1 Erforderliche IDs

| ID | Gegenstand | Deterministisch |
|---|---|---:|
| `dataset_id` | Logischer veröffentlichter RCC-002-Datenstand | Ja |
| `source_snapshot_id` | Unveränderliche Quelldatenfassung | Ja |
| `build_id` | Logische Transformationsdefinition einschließlich Eingaben | Ja |
| `artifact_id` | Identität eines einzelnen gespeicherten Artefakts aus semantischem Inhalt und physischem Layout | Ja |
| `dataset_artifact_set_id` | Physische Identität der veröffentlichten Artefaktmenge eines Datasets | Ja |
| `run_id` | Konkrete Ausführung | Nein |
| `manifest_id` | Konkreter kanonischer Manifestinhalt | Ja |

### 5.2 ID-Format

Empfohlenes Format:

```text
<type>:sha256:<64 lowercase hex characters>
```

Beispiele:

```text
source:sha256:<digest>
build:sha256:<digest>
artifact:sha256:<digest>
dataset:sha256:<digest>
dataset-artifact-set:sha256:<digest>
manifest:sha256:<digest>
```

`run_id` MUSS als nichtdeterministische Laufzeitidentität erkennbar sein:

```text
run:<UTC timestamp>:<UUIDv7-or-UUIDv4>
```

### 5.3 Source Snapshot ID

Die Vorabbildung des `source_snapshot_id` MUSS ausschließlich quellinhaltliche und semantische Abrufmerkmale enthalten:

- Quellenbezeichnung;
- Markt und Symbol;
- Datenfrequenz;
- normierte Liste aller Quelldateien;
- SHA-256 jeder Quelldatei;
- kanonische semantische Abrufparameter, die Auswahl oder Bedeutung der gelieferten Daten verändern;
- Abdeckungszeitraum;
- Quellenversions- oder Revisionskennung, soweit verfügbar.

Provider-Revisionskennungen und semantische Abrufparameter MÜSSEN die Identität beeinflussen. Abrufzeitpunkt, lokaler Speicherpfad, Hostname, Benutzername, Transport-Retrys und Cache-Ort sind Run- beziehungsweise Provenienzmetadaten und DÜRFEN den `source_snapshot_id` NICHT verändern.

### 5.4 Build ID

Der `build_id` MUSS aus einer kanonischen Vorabbildung berechnet werden, die mindestens enthält:

- `source_snapshot_id` oder geordnete logische Parent-Identitäten aus
  `semantic_sha256` und zugehöriger Schema-ID;
- Code-Commit;
- Dirty-Patch-Hash, falls der Arbeitsbaum nicht sauber ist;
- kanonischen Konfigurations-Hash;
- Spezifikationsprofil mit Dokument-IDs und Versionen;
- Pipeline-Profil;
- Schema-IDs;
- `environment_identity_profile_id` und Hash der nach diesem Profil relevanten deterministischen Umgebungsparameter;
- Transformationsstufe oder Stufenbereich.

Nicht Bestandteil der Build-ID sind:

- Start- oder Endzeitpunkt des Runs;
- Hostname;
- zufällige UUID;
- temporärer Pfad;
- `manifest_id`;
- Hash des Manifests, das den `build_id` enthält.

Damit wird eine zirkuläre Hashdefinition ausgeschlossen.

### 5.5 Run ID

Der `run_id` identifiziert eine konkrete Ausführung desselben logischen Builds. Zwei Runs dürfen denselben `build_id`, aber niemals denselben `run_id` besitzen.

Der Run-Datensatz MUSS enthalten:

- `run_id`;
- `build_id`;
- Start- und Endzeit in UTC;
- Host- und Umgebungsinformationen;
- Prozessstatus;
- Ausführungsparameter;
- Prüf- und Veröffentlichungsstatus.

### 5.6 Artifact ID

Die `artifact_id` MUSS ein konkretes gespeichertes Artefakt identifizieren. Sie darf nicht allein aus Dateiname, Pfad oder semantischem Fingerprint entstehen.

Für Datenartefakte umfasst die Vorabbildung mindestens:

- kanonische Schema-ID;
- `semantic_sha256`;
- `physical_layout_sha256`;
- Byte-Hash des gespeicherten Containers;
- Zeilenanzahl;
- logische Zeitabdeckung.

Der `semantic_sha256` identifiziert den logischen Tabelleninhalt. Der `physical_layout_sha256` identifiziert dessen physische Anordnung. Dadurch erhalten semantisch gleiche, aber physisch unterschiedlich partitionierte oder serialisierte Artefakte unterschiedliche `artifact_id`s, bleiben jedoch über denselben `semantic_sha256` als E2-gleich erkennbar.

### 5.7 Dataset ID

Die `dataset_id` identifiziert die veröffentlichte logische Gesamtheit der S8-Artefakte. Ihre Vorabbildung MUSS enthalten:

- geordnete Liste logischer Dataset-Komponenten mit `logical_name`,
  Schema-ID, `semantic_sha256`, Zeilenanzahl und logischer Zeitabdeckung;
- Release-Schema-ID;
- Dataset-Profil;
- relevanten `build_id`;
- Qualitätsstatus;
- Spezifikationsprofil.

`artifact_id`, `physical_layout_sha256`, `byte_sha256`, Dateipfad,
Partitionierungsstruktur und Writerprofil DÜRFEN den `dataset_id` NICHT
beeinflussen.

### 5.8 Dataset Artifact Set ID

Die `dataset_artifact_set_id` identifiziert die konkrete physische
Veröffentlichungsmenge eines logischen Datasets. Ihre Vorabbildung MUSS
enthalten:

- `dataset_id`;
- geordnete Liste der veröffentlichten `artifact_id`s;
- Veröffentlichungs- beziehungsweise Layoutprofil;
- vollständige Partitions- und Dateigrenzen.

Eine reine Repartitionierung oder Neuverpackung behält bei semantisch
identischen Inhalten denselben `dataset_id`, erzeugt aber eine neue
`dataset_artifact_set_id`.

### 5.9 Manifest ID

Der `manifest_id` wird erst berechnet, nachdem alle anderen deterministischen IDs im Manifest feststehen.

Berechnung:

1. Manifestinhalt ohne Feld `manifest_id` kanonisieren;
2. SHA-256 der kanonischen Bytes berechnen;
3. Ergebnis als `manifest_id` einsetzen;
4. das vollständige Manifest speichern;
5. zusätzlich den Byte-Hash der gespeicherten Manifestdatei protokollieren.

Der `manifest_id` und der Byte-Hash der finalen Datei dürfen verschieden sein, weil das Feld `manifest_id` selbst erst nach der Vorabbildung ergänzt wird.

---

## 6. Hash- und Kanonisierungsregeln

### 6.1 Standardalgorithmus

SHA-256 ist der verbindliche Mindeststandard.

Andere Hashalgorithmen dürfen ergänzend gespeichert werden, ersetzen SHA-256 jedoch nicht.

### 6.2 Kanonisches JSON

Kanonisches JSON MUSS RFC 8785, JSON Canonicalization Scheme (JCS), verwenden. Vor der JCS-Serialisierung gelten zusätzlich folgende RCC-002-Vorverarbeitungsregeln:

- UTF-8 ohne BOM verwenden;
- alle Strings und Objektschlüssel in Unicode NFC normalisieren;
- Objektschlüssel nach JCS sortieren;
- keine semantisch irrelevanten Leerzeichen enthalten;
- Arrays grundsätzlich in ihrer vorhandenen Reihenfolge erhalten;
- Mengenähnliche Arrays nur dann sortieren, wenn ihr Schema eine eindeutige Sortierregel und einen vollständigen Sortierschlüssel registriert;
- Zeilenende LF verwenden;
- nichtendliche Zahlen (`NaN`, `Infinity`, `-Infinity`) verbieten;
- Zeitstempel im UTC-Format mit `Z` speichern;
- fachliche Dezimalwerte als kanonische Dezimalstrings serialisieren.

Verbindliches Profil:

```text
profile_id=RCC_JSON_CANONICALIZATION_V1
base_standard=RFC8785/JCS
encoding=UTF-8
unicode_preprocessing=NFC
non_finite_numbers=forbidden
domain_decimals=canonical_decimal_strings
array_order=schema-defined-or-preserved
```

Für `RCC_JSON_CANONICALIZATION_V1` MÜSSEN Golden Fixtures mit erwarteten kanonischen Bytes und SHA-256-Digests versioniert werden. Implementierungen MÜSSEN diese Fixtures vor einer Veröffentlichung ohne Abweichung bestehen.

### 6.3 Fließkommazahlen

Konfigurationen MÜSSEN fachliche Dezimalparameter als kanonische Dezimalstrings serialisieren. Das Format MUSS ein optionales Minuszeichen, mindestens eine Ganzzahlziffer und nur bei Bedarf einen Dezimalpunkt mit einer oder mehreren Nachkommastellen verwenden. Führende Pluszeichen, Exponenten, unnötige führende Nullen und unnötige nachgestellte Nullen sind verboten; `-0` wird als `0` serialisiert.

Binäre Fließkommawerte in Datenartefakten werden nicht durch JSON-Dezimalstrings ersetzt. Ihre kanonische Wertedarstellung MUSS im registrierten Tabellen-Fingerprint-Profil feldweise definiert sein.

### 6.4 Konfigurationskanonisierung

Vor der Hashbildung MUSS:

- die effektive, vollständig aufgelöste Konfiguration verwendet werden;
- Vererbung und Defaults aufgelöst sein;
- die Reihenfolge nichtsemantischer Schlüssel normalisiert sein;
- jeder Wert mit Typ erhalten bleiben;
- jede Maßeinheit explizit sein;
- jedes Geheimnis entfernt oder durch einen nichtumkehrbaren Referenzbezeichner ersetzt sein.

Nicht erlaubt:

- Hash nur der vom Nutzer überschriebenen Werte;
- Hash eines Dateipfads statt des Inhalts;
- Speicherung von API-Schlüsseln, Tokens oder Passwörtern;
- Ersetzung eines Geheimnisses durch dessen ungesalzenen Hash, wenn dadurch Wörterbuchangriffe möglich werden.

### 6.5 Zeit und Zeitzonen

Alle Manifestzeitpunkte MÜSSEN UTC verwenden.

Zeitstempel dürfen die `run_id` und den Run-Nachweis beeinflussen, aber keine deterministische `build_id`.

---

## 7. Bytegleichheit und semantische Gleichheit

### 7.1 Bytegleichheit

Bytegleichheit liegt vor, wenn zwei Dateien denselben SHA-256-Bytehash besitzen.

Sie ist für folgende Artefakte anzustreben:

- kanonische JSON-Manifeste;
- reine Textkonfigurationen;
- JSON-Schemata;
- kleine normative CSV-Tabellen bei vollständig fixierter Serialisierung.

### 7.2 Parquet-Einschränkung

Parquet-Dateien können trotz identischer Tabelleninhalte unterschiedliche Bytes besitzen, beispielsweise durch:

- Bibliotheksversionen;
- Writer-Metadaten;
- Kompressionsversionen;
- Row-Group-Grenzen;
- Dictionary-Encoding;
- Dateimetadaten.

Deshalb MUSS RCC-002 für tabellarische Daten neben dem Datei-Bytehash einen semantischen Fingerprint speichern.

### 7.3 Semantischer Fingerprint

Der semantische Fingerprint MUSS mindestens berücksichtigen:

- normierte Spaltenreihenfolge;
- logische Datentypen;
- definierte Nullrepräsentation;
- vollständigen registrierten kanonischen Primärschlüssel;
- kanonische Zeilenreihenfolge nach diesem Primärschlüssel;
- Zeilenanzahl;
- Werte einschließlich expliziter Fließkommaregel;
- Schema-Version.

Für kanonische RCC-002-Marktdaten ist der Primärschlüssel und damit die Sortierreihenfolge:

1. `market_type`;
2. `symbol`;
3. `interval`;
4. `open_time`.

Für noch nicht konsolidierte Multi-Provider-Daten MUSS `provider` als weiterer Schlüsselbestandteil registriert werden. Andere Tabellen MÜSSEN ihren vollständigen Primärschlüssel im Schema registrieren; eine optionale oder implizite Ereignis-ID ist unzulässig.

Der `semantic_sha256` DARF folgende physische Merkmale NICHT berücksichtigen:

- Dateigrenzen;
- Verzeichnis- oder Partitionierungsstruktur;
- Row-Group-Grenzen;
- Kompressionsalgorithmus oder -stufe;
- Dictionary-Encoding;
- Writer-Version;
- Container-Metadaten.

Diese Merkmale MÜSSEN separat in einem `physical_layout_sha256` erfasst werden. Dessen Vorabbildung MUSS mindestens Dateigrenzen, Partitionsschlüssel und -werte, Row-Group-Profil, Kompressionsprofil, Writerprofil und relevante Containerparameter enthalten.

### 7.4 Gleichheitsklassen

| Klasse | Anforderung |
|---|---|
| E0 | Keine Gleichheitsaussage |
| E1 | Schema und Zeilenanzahl gleich |
| E2 | Semantischer Fingerprint gleich |
| E3 | Bytehash gleich |

Veröffentlichte RCC-002-Daten MÜSSEN mindestens E2 erreichen.

Ein bereits persistiertes unveränderliches Manifest oder JSON-Schema MUSS bei jeder späteren Verifikation E3 erreichen. Separat erzeugte Run Manifeste verschiedener Runs müssen wegen `run_id` und Laufzeitstempeln nicht bytegleich sein. E3 zwischen zwei Erzeugungen ist nur dann verpflichtend, wenn ihre vollständige kanonische Vorabbildung einschließlich aller Laufzeitfelder identisch ist.

---

## 8. Manifestarchitektur

### 8.1 Manifesttypen

RCC-002 MUSS mindestens folgende Manifesttypen unterstützen:

| Manifest | Zweck |
|---|---|
| Source Manifest | Externe Quelle und Rohdaten-Snapshot |
| Stage Manifest | Ein- und Ausgaben einer Stufe S0–S8 |
| Run Manifest | Konkrete Ausführung und Umgebung |
| Dataset Manifest | Gesamter veröffentlichter Datenstand |
| Review Manifest | Reviews, Befunde und Freigaben |
| Reproduction Manifest | Ergebnis eines unabhängigen Rebuilds |

### 8.2 Gemeinsame Pflichtfelder

Jedes Manifest MUSS enthalten:

```json
{
  "manifest_schema_id": "string",
  "manifest_type": "string",
  "manifest_id": "string",
  "created_at_utc": "string",
  "producer": {
    "component": "string",
    "version": "string"
  },
  "project": "RCC-002",
  "status": "string"
}
```

`created_at_utc` gehört zum Manifestnachweis, aber nicht zur deterministischen Build-Vorabbildung.

### 8.3 Stage Manifest

Jede Stufe MUSS dokumentieren:

- `stage_id`;
- `stage_version`;
- `build_id`;
- `run_id`;
- Parent-Artefakte;
- Ausgabeartefakte;
- effektive Konfiguration;
- Codeprovenienz;
- Spezifikationsprofil;
- Schema-IDs;
- Zeilen- und Zeitbereichsstatistiken;
- Validierungsergebnisse;
- Warnungen;
- Fehlerstatus;
- Veröffentlichungsstatus.

### 8.4 Dataset Manifest

Das Dataset Manifest MUSS mindestens enthalten:

```json
{
  "dataset_id": "dataset:sha256:<digest>",
  "dataset_artifact_set_id": "dataset-artifact-set:sha256:<digest>",
  "dataset_profile": "rcc002-canonical",
  "build_id": "build:sha256:<digest>",
  "source_snapshot_ids": [],
  "artifacts": [],
  "stages": [],
  "schemas": [],
  "specification_profile": [],
  "code_provenance": {},
  "configuration": {},
  "environment_reference": {},
  "quality_summary": {},
  "dataset_lineage": {},
  "knowledge_lineage": {},
  "publication": {},
  "reviews": []
}
```

### 8.5 JSON Schema

Jeder Manifesttyp MUSS durch ein versioniertes JSON Schema validiert werden.

Die Schema-ID MUSS:

- eindeutig;
- versioniert;
- unveränderlich nach Release;
- im Manifest referenziert

sein.

Ein Manifest, das sein Schema nicht erfüllt, DARF NICHT veröffentlicht werden.

---

## 9. Codeprovenienz

### 9.1 Pflichtfelder

```json
{
  "repository": "<repository URL or canonical repository identifier>",
  "commit_sha": "<40-hex commit>",
  "branch_observed": "<informational>",
  "worktree_clean": true,
  "dirty_patch_sha256": null,
  "submodules": [],
  "entrypoint": "<module or command>",
  "code_profile": "<profile id>"
}
```

### 9.2 Commit und Branch

Der Commit-SHA ist normativ. Der Branchname ist nur informativ, da sich Branchzeiger verändern können.

### 9.3 Dirty Worktree

Kanonische Release-Builds SOLLEN aus einem sauberen Arbeitsbaum entstehen.

Falls ein Forschungsbuild aus einem nicht sauberen Arbeitsbaum erfolgt:

- `worktree_clean` MUSS `false` sein;
- ein kanonischer Patch MUSS gesichert werden;
- dessen SHA-256 MUSS in die Build-ID eingehen;
- unversionierte relevante Dateien MÜSSEN eingeschlossen werden;
- der Build DARF nicht als zertifizierter Release gelten, solange die Änderungen nicht versioniert sind.

### 9.4 Generierter Code

Generierter Code MUSS mit Generatorversion, Eingabeartefakten und Ausgabehash dokumentiert werden.

---

## 10. Umgebungsprovenienz

### 10.1 Pflichtumfang

Der Run-Nachweis MUSS mindestens erfassen:

- Betriebssystem und Version;
- WSL-Version beziehungsweise Kernel, falls zutreffend;
- Python-Version, für RCC-002 Zielbaseline Python 3.12;
- Paketlock oder vollständige Paketliste;
- Architektur;
- CPU-Modell;
- Threadkonfiguration;
- Locale;
- Zeitzone;
- relevante Umgebungsvariablen;
- NumPy-, Pandas-, PyArrow- und BLAS-Versionen;
- Kompressionsbibliotheken;
- Random-Seed-Register;
- Hardwarebeschleuniger, falls verwendet.

### 10.2 Deterministisches Umgebungsidentitätsprofil

Ob und welche Umgebungsmerkmale den `build_id` beeinflussen, wird ausschließlich durch ein versioniertes Allowlist-Profil bestimmt.

Das für logisch-semantische Build-Identität verbindliche Profil lautet:

```text
profile_id=RCC_BUILD_ENV_IDENTITY_V2
```

`RCC_BUILD_ENV_IDENTITY_V2` MUSS enthalten:

- Python-Haupt- und Nebenversion;
- Hash der gesperrten Python-Pakete und relevanten nativen Numerikbibliotheken;
- Zeitzone `UTC`;
- kanonisches Locale-Profil;
- registriertes numerisches Präzisions- und Rundungsprofil;
- registrierte Thread- und BLAS-Determinismusparameter;
- registriertes semantisches Numerik- und Fingerprintprofil.

Writer-, Kompressions-, Row-Group-, Partitionierungs- und sonstige
Containerprofile MÜSSEN in der physischen Artefaktprovenienz und im
`physical_layout_sha256` stehen. Sie DÜRFEN den logischen `build_id` NICHT
beeinflussen.

Folgende Merkmale sind standardmäßig ausschließlich Run-Metadaten und DÜRFEN unter `RCC_BUILD_ENV_IDENTITY_V2` den `build_id` NICHT beeinflussen:

- Hostname;
- Benutzername;
- absolute lokale Pfade;
- Start- und Endzeit des Runs;
- CPU-Modell;
- Gerätename.

Ein solches Merkmal darf nur durch eine neue versionierte Profil-ID aufgenommen werden, wenn reproduzierbare Evidenz seine semantische Relevanz nachweist. Profiländerungen DÜRFEN NICHT still erfolgen.

### 10.3 Paketumgebung

Ein ungeprüftes `pip freeze` allein ist nicht ausreichend, wenn:

- lokale Pfade enthalten sind;
- transitive native Bibliotheken fehlen;
- nicht reproduzierbare VCS-Referenzen verwendet werden.

Der Reproduktionssatz SOLL enthalten:

- Lockdatei;
- `pip freeze`;
- Python-Version;
- native Bibliotheksinformationen;
- Container- oder Environment-Definition, falls vorhanden.

### 10.4 Locale und Zeitzone

Builds MÜSSEN unabhängig von lokalen Geräteeinstellungen UTC und definierte numerische Formate verwenden.

Die Umgebung SOLL setzen:

```text
TZ=UTC
LC_ALL=C.UTF-8
LANG=C.UTF-8
```

### 10.5 Threads und numerische Bibliotheken

Threadzahl und BLAS-Backend MÜSSEN protokolliert werden, wenn sie Reduktionsreihenfolgen oder Ergebnisse beeinflussen können.

Für zertifizierte Rebuilds SOLLEN die deterministisch relevanten Threadparameter fixiert sein.

### 10.6 Geheimnisse

Manifeste DÜRFEN NICHT enthalten:

- API-Schlüssel;
- Passwörter;
- Zugriffstokens;
- private Schlüssel;
- vollständige Verbindungszeichenfolgen;
- personenbezogene Zugangsdaten.

Erlaubt sind abstrakte Secret-Referenzen wie:

```text
secret_ref:binance_public_market_data
```

---

## 11. Dataset Lineage

### 11.1 Grundsatz

Jedes Datenartefakt MUSS seine direkten Eltern referenzieren. Aus den direkten Beziehungen MUSS ein vollständiger gerichteter azyklischer Graph rekonstruierbar sein.

### 11.2 Lineage-Knoten

Ein Knoten MUSS enthalten:

- `artifact_id`;
- Artefakttyp;
- Stufe;
- Schema-ID;
- Bytehash;
- semantischen Fingerprint;
- Dateigröße;
- Zeilenanzahl;
- Spaltenanzahl;
- Zeitbereich;
- Symbolbereich;
- Partitionsinformationen;
- Status.

### 11.3 Lineage-Kanten

Eine Kante MUSS enthalten:

- Parent-`artifact_id`;
- Child-`artifact_id`;
- Transformation;
- `build_id`;
- `run_id`;
- Filter- oder Selektionsinformation;
- gegebenenfalls Revisionsbeziehung.

### 11.4 Vollständigkeitsregel

Ein veröffentlichtes Artefakt ohne vollständig auflösbare Elternkette bis zu einem Source Snapshot ist unzulässig.

### 11.5 S0–S8-Abdeckung

Die Lineage MUSS sichtbar machen:

```text
Source Snapshot
→ S0 Acquisition
→ S1 Normalization
→ S2 Validation
→ S3 Indicators
→ S4 Signals
→ S5 Regime
→ S6 Gates
→ S7 Labels
→ S8 Published Dataset
```

Ausgelassene Stufen MÜSSEN explizit als nicht anwendbar begründet werden.

### 11.6 Historische Artefakte

Rekonstruierte oder mutmaßlich abgeschnittene historische Artefakte MÜSSEN entsprechend markiert werden:

```text
provenance_status: reconstructed
integrity_status: historically_verified | partially_verified | suspected_truncated
canonical: false
```

Die bekannte historische Regime-Datei mit 1.048.575 Datenzeilen darf wegen des starken Excel-Trunkierungsindizes nicht als kanonische RCC-002-Quelle behandelt werden.

---

## 12. Knowledge Lineage

### 12.1 Zweck

Knowledge Lineage dokumentiert nicht nur, welcher Code lief, sondern warum eine Regel existiert und auf welcher Evidenz sie beruht.

### 12.2 Pflichtobjekte

Knowledge Lineage MUSS enthalten:

- Spezifikationsdokumente mit Dokument-ID und Version;
- wissenschaftliche Entscheidungen;
- Annahmen;
- Hypothesen;
- bekannte Unsicherheiten;
- historische Rekonstruktionen;
- empirische Verifikationen;
- verworfene Alternativen, soweit entscheidungsrelevant;
- Reviewbefunde;
- Freigabeentscheidungen.

### 12.3 Spezifikationsprofil

Das kanonische RCC-002-Profil MUSS mindestens die Versionen folgender Dokumente referenzieren:

- Data Pipeline Specification;
- Data Validation Specification;
- Indicator Specification;
- Signal Transformation Specification;
- Regime and Gate Specification;
- Label and Forward Return Specification;
- Reproducibility and Manifest Specification.

Eine bloße Dateinennung ohne Dokument-ID und Version ist nicht ausreichend.

### 12.4 Entscheidungsobjekt

Empfohlenes Format:

```json
{
  "decision_id": "RCC-002-DEC-<number>",
  "title": "string",
  "status": "proposed|accepted|rejected|superseded",
  "effective_from_specification_profile": "string",
  "evidence": [],
  "assumptions": [],
  "alternatives": [],
  "supersedes": [],
  "review_records": []
}
```

### 12.5 Verifizierte historische Erkenntnisse

Die Knowledge Lineage SOLL die bereits empirisch bestätigten Rekonstruktionen referenzieren:

- zwölf historische BTC-Signalregeln mit null Abweichungen über 2.721.034 Zeilen;
- historische Regimeregeln mit null Abweichungen über 1.048.575 Zeilen;
- Trunkierungsverdacht der historischen Regimedatei;
- Trennung historischer binärer Signale von späteren kontinuierlichen GS-Scores;
- bewusste modulare Trennung von Regime und Handels-Gates in RCC-002.

Diese Evidenz begründet Architekturentscheidungen, ersetzt aber keine RCC-002-Neuvalidierung.

---

## 13. Artefaktinventar

Jeder Build MUSS ein Inventar führen:

| Feld | Bedeutung |
|---|---|
| `logical_name` | Stabile fachliche Bezeichnung |
| `artifact_id` | Identität des gespeicherten Artefakts |
| `relative_path` | Pfad innerhalb des Reproduktionssatzes |
| `media_type` | Dateityp |
| `schema_id` | Logisches Schema |
| `byte_sha256` | Hash der gespeicherten Datei |
| `semantic_sha256` | Hash des kanonischen Inhalts |
| `physical_layout_sha256` | Hash von Partitionierung, Dateigrenzen und Containerprofil |
| `size_bytes` | Dateigröße |
| `row_count` | Zeilenzahl |
| `min_timestamp_utc` | Frühester Datenzeitpunkt |
| `max_timestamp_utc` | Spätester Datenzeitpunkt |
| `publication_status` | Status |

Absolute lokale Pfade dürfen ergänzend im Run Manifest stehen, dürfen aber nicht die portable Artefaktidentität definieren.

---

## 14. Build- und Publikationszustände

### 14.1 Zustandsmodell

| Status | Bedeutung |
|---|---|
| `planned` | Build definiert, nicht gestartet |
| `running` | Ausführung aktiv |
| `validating` | Ausgaben vorhanden, Prüfungen aktiv |
| `failed` | Build oder Pflichtprüfung fehlgeschlagen |
| `quarantined` | Artefakte isoliert, nicht freigegeben |
| `candidate` | Prüfungen bestanden, Freigabe ausstehend |
| `published` | Atomar veröffentlicht |
| `superseded` | Durch neueren Datenstand ersetzt |
| `withdrawn` | Nach Veröffentlichung zurückgezogen |

### 14.2 Atomare Veröffentlichung

Ein Build MUSS zunächst in einem eindeutigen temporären Verzeichnis schreiben.

Veröffentlichung darf erst erfolgen, wenn:

- alle Pflichtartefakte existieren;
- alle Prüfsummen berechnet sind;
- alle Manifest-Schemata gültig sind;
- alle Pflichtprüfungen bestanden sind;
- kein Parent-Artefakt fehlt;
- das Dataset Manifest vollständig ist.

Die Veröffentlichung MUSS durch atomare Umbenennung oder ein funktional gleichwertiges Commit-Verfahren erfolgen.

### 14.3 Kein stilles Überschreiben

Ein bereits veröffentlichter `dataset_artifact_set_id` und sämtliche ihm
zugeordneten Artefakte sind unveränderlich.

Eine semantisch identische Neuverpackung oder Repartitionierung DARF denselben
`dataset_id` behalten, MUSS jedoch einen neuen `dataset_artifact_set_id`
erzeugen.

Bestehende Artefaktmengen und ihre Dateien DÜRFEN dabei NICHT überschrieben,
ersetzt oder still verändert werden.

Ein neuer Inhalt MUSS:

- eine neue Identität erhalten;
- die Vorgängerversion über `supersedes` referenzieren;
- die alte Fassung erhalten.

### 14.4 Teilergebnisse

Teilergebnisse dürfen für Diagnosezwecke erhalten bleiben, MÜSSEN jedoch als `failed` oder `quarantined` markiert werden und DÜRFEN NICHT unter einem finalen Veröffentlichungspfad erscheinen.

---

## 15. Inkrementelle Builds und Revisionen

### 15.1 Inkrementelle Erweiterung

Ein inkrementeller Build MUSS dokumentieren:

- Basis-`dataset_id`;
- neu hinzugefügten Zeitbereich;
- überlappenden Prüfbereich;
- geänderte Source Snapshots;
- betroffene Partitionen;
- unveränderte Partitionen;
- neue Gesamtidentität.

### 15.2 Indikator-Warm-up

Inkrementelle Berechnung MUSS für rollierende und rekursive Indikatoren genügend historische Vorlaufdaten laden.

Der Manifestnachweis MUSS unterscheiden:

- geladener Berechnungsbereich;
- veröffentlichter Zielbereich;
- verworfener Warm-up-Bereich.

### 15.3 Revision externer Quelldaten

Wenn der Anbieter historische Quelldaten revidiert:

- entsteht ein neuer `source_snapshot_id`;
- betroffene Nachfahren erhalten neue IDs;
- die Revision MUSS dokumentiert werden;
- frühere Datenstände bleiben unverändert erhalten;
- `supersedes` und Revisionsgrund MÜSSEN gesetzt werden.

### 15.4 Partielle Wiederverwendung

Wiederverwendete Partitionen MÜSSEN per Hash verifiziert werden. Ein Pfad- oder Dateinamensvergleich reicht nicht aus.

---

## 16. Geräteübergreifende Reproduktion

### 16.1 Zielgeräte

RCC-002 muss grundsätzlich auf folgenden Projektgeräten nachvollziehbar sein:

- X1 Carbon;
- G15/AR15;
- Workstation.

Die Workstation bleibt für vollständige Mehrmillionen-Zeilen-Builds das bevorzugte Ausführungsgerät. Das darf die Portabilität der Spezifikation nicht einschränken.

### 16.2 Gleichheitserwartung

| Situation | Erwartung |
|---|---|
| Gleicher Code, gleiche Lockdatei, identisches `RCC_BUILD_ENV_IDENTITY_V2` | E2 verpflichtend; E3 für Datencontainer nur bei identischem physischen Layoutprofil |
| Unterschiedliche Geräte, sonst identisches Umgebungsidentitätsprofil | E2 verpflichtend; Host- und CPU-Unterschiede allein erzeugen keine neue Build-ID |
| Unabhängige Implementierung derselben Formel | Fachlich definierte Toleranzprüfung plus identische Klassifikationen |
| Unterschiedliche Bibliotheksversionen | Kein Gleichheitsanspruch ohne dokumentierte Kompatibilitätsprüfung |

### 16.3 Numerische Toleranzen

Toleranzen dürfen nur für den Vergleich unabhängiger oder technisch abweichender Implementierungen genutzt werden.

Ein wiederholter Build in derselben gesperrten Umgebung SOLL exakte semantische Gleichheit liefern.

Toleranzen MÜSSEN:

- pro Feld oder Feldklasse festgelegt;
- wissenschaftlich begründet;
- absolut und/oder relativ angegeben;
- vor dem Vergleich definiert;
- im Reproduction Manifest protokolliert

sein.

Toleranzen dürfen keine Regime-, Gate- oder Labelabweichungen verdecken.

### 16.4 Cross-Device-Protokoll

Ein Gerätevergleich MUSS enthalten:

- Quell- und Zielgerät;
- `build_id`;
- beide `run_id`s;
- Umgebungsdifferenzen;
- Bytevergleich;
- semantischen Vergleich;
- Feldtoleranzbericht;
- Klassifikationsvergleich;
- Ergebnisstatus.

---

## 17. Reproduktionssatz

Ein vollständiger Reproduktionssatz MUSS enthalten:

1. Dataset Manifest;
2. alle Stage Manifests;
3. Run Manifest;
4. Source Manifest oder auflösbare Quellenreferenzen;
5. Code-Commit und gegebenenfalls Dirty Patch;
6. effektive Konfiguration;
7. Lock- und Umgebungsdateien;
8. JSON-Schemata;
9. Spezifikationsprofil;
10. Artefaktinventar;
11. Prüfsummenliste;
12. Validierungsberichte;
13. dokumentierten Build-Einstiegspunkt;
14. Rebuild-Anweisung;
15. Review- und Freigabestatus.

### 17.1 Rebuild-Einstiegspunkt

Die Implementierung MUSS einen nichtinteraktiven Einstiegspunkt anbieten.

Konzeptionelles Beispiel:

```bash
PYTHONPATH=. python3 -m scripts.build_rcc002 \
  --config configs/rcc002/canonical.json \
  --source-manifest manifests/source/<source_snapshot_id>.json \
  --output-root build/rcc002
```

Der endgültige Befehl wird durch die Implementierung festgelegt und MUSS im Manifest wortgetreu gespeichert werden.

### 17.2 Offline-Reproduktion

Wenn Quelldaten lizenz- oder größenbedingt nicht gebündelt werden können, MUSS der Reproduktionssatz wenigstens:

- eindeutige Quellenreferenzen;
- Prüfsummen;
- Abrufparameter;
- erwartete Größen;
- Zeitabdeckung;
- Integritätsprüfungen

enthalten.

---

## 18. Validierung und Tests

### 18.1 Manifesttests

Pflichttests:

- JSON-Schema gültig;
- alle Pflichtfelder vorhanden;
- alle IDs syntaktisch gültig;
- `manifest_id` korrekt;
- keine zirkuläre ID-Abhängigkeit;
- alle Referenzen auflösbar;
- keine Geheimnisse;
- UTC-Zeitstempel gültig;
- Statusübergänge gültig.

### 18.2 Artefakttests

- Datei vorhanden;
- Bytehash korrekt;
- semantischer Fingerprint korrekt;
- Schema korrekt;
- Zeilenzahl korrekt;
- Zeitbereich korrekt;
- Spaltenreihenfolge korrekt;
- Parent-Beziehung korrekt.

### 18.3 Lineagetests

- Graph azyklisch;
- jedes veröffentlichte Artefakt bis zur Quelle rückverfolgbar;
- keine verwaisten Knoten;
- keine widersprüchlichen Parent-Beziehungen;
- Stage-Reihenfolge fachlich zulässig;
- alle Spezifikationsreferenzen auflösbar.

### 18.4 Rebuildtests

Mindestens:

- Wiederholungsbuild auf demselben Gerät;
- Clean-Environment-Build;
- Cross-Device-Semantikvergleich;
- absichtliche Inputänderung erzeugt neue Build-ID;
- reine Run-Zeitänderung verändert nicht die Build-ID;
- Konfigurationsänderung erzeugt neue Build-ID;
- Dirty Patch erzeugt neue Build-ID;
- Manifeständerung erzeugt neue Manifest-ID, aber keine rückwirkende Zirkularität.

### 18.5 Negativtests

Die Tests MÜSSEN fehlschlagen bei:

- manipuliertem Artefakt;
- fehlendem Parent;
- falschem Hash;
- ungültigem Schema;
- Geheimnis im Manifest;
- unbekannter Spezifikationsversion;
- stillem Überschreiben;
- unzulässiger Statusfolge;
- nichtkanonischem Zeitstempel;
- ungeklärtem historischen Artefakt als kanonischer Quelle.

---

## 19. Fehlerbehandlung und Wiederaufnahme

### 19.1 Fehlgeschlagener Build

Bei Fehler MUSS:

- der Runstatus `failed` werden;
- die fehlerhafte Stufe dokumentiert werden;
- der Fehlerbericht erhalten bleiben;
- kein finaler Dataset-Pfad veröffentlicht werden;
- vorhandene Teilartefakte quarantänisiert oder kontrolliert entfernt werden.

### 19.2 Wiederaufnahme

Eine Wiederaufnahme darf nur bereits abgeschlossene Stufen wiederverwenden, wenn:

- Parent-Hashes unverändert sind;
- Build-Vorabbildung unverändert ist;
- Artefakthashes stimmen;
- Stage Manifest gültig ist;
- Wiederverwendung im neuen Run Manifest dokumentiert wird.

### 19.3 Wiederholungsversuch

Jeder Versuch erhält eine neue `run_id`. Der `build_id` bleibt gleich, solange die deterministischen Eingaben gleich bleiben.

### 19.4 Quarantäne

Quarantänisierte Artefakte:

- dürfen nicht von produktiven Verbrauchern aufgelöst werden;
- müssen einen Grund enthalten;
- müssen den verursachenden Run referenzieren;
- dürfen nach Korrektur nicht still in-place freigegeben werden.

---

## 20. Audit und Berichterstattung

### 20.1 Auditbericht

Ein Release-Audit MUSS kompakt ausweisen:

- Dataset-ID;
- Build-ID;
- Run-ID des Veröffentlichungsbuilds;
- Source-Snapshot-IDs;
- Code-Commit;
- Spezifikationsprofil;
- Konfigurationshash;
- Umgebungsprofil;
- Artefakte und Prüfsummen;
- Qualitätsprüfungen;
- Lineage-Status;
- Reviewstatus;
- bekannte Einschränkungen;
- Freigabeentscheidung.

### 20.2 Maschinen- und menschenlesbare Form

Die maschinenlesbaren JSON-Manifeste sind normativ.

Ein menschenlesbarer Markdown- oder HTML-Bericht SOLL daraus generiert werden. Bei Widerspruch gilt das validierte maschinenlesbare Manifest.

### 20.3 Logaufbewahrung

Logs MÜSSEN:

- einem `run_id` zugeordnet;
- zeitlich in UTC;
- gegen Vermischung mehrerer Runs geschützt;
- frei von Geheimnissen;
- nach Retentionsregeln archiviert

sein.

---

## 21. Review- und Freigabenachweise

### 21.1 Review Record

```json
{
  "review_id": "string",
  "review_type": "internal|scr|architecture|editorial|certification|external|consolidation",
  "reviewer": "string",
  "reviewer_system": "human|chatgpt|gemini|claude|other",
  "reviewed_artifacts": [],
  "started_at_utc": "string",
  "completed_at_utc": "string",
  "status": "pending|passed|passed_with_findings|failed",
  "findings": [],
  "resolution_references": []
}
```

### 21.2 Unabhängige KI-Reviews

Claude- und Gemini-Reviews werden erst eingetragen, nachdem sie tatsächlich
durchgeführt wurden.

Bis dahin MUSS gelten:

```text
reviewer_system: claude
status: pending
```

beziehungsweise:

```text
reviewer_system: gemini
status: pending
```

Ergebnisse DÜRFEN NICHT erfunden, vorweggenommen oder als bestanden markiert werden.

### 21.3 Reviewartefakte

Jeder externe Reviewnachweis SOLL enthalten:

- geprüftes Dokument oder Dataset mit Hash;
- verwendete Reviewanweisung;
- System- und Modellbezeichnung;
- Datum;
- vollständige Befunde;
- Klassifikation der Befunde;
- Auflösung jedes wesentlichen Befunds;
- Re-Review-Status.

### 21.4 Freigabesequenz

Für die RCC-002-Spezifikationsfamilie gilt:

1. Specification Draft;
2. Internal Review;
3. Scientific Consistency Review;
4. Architecture Integrity Review;
5. Editorial Pass;
6. Internal Certification;
7. Claude Independent Architecture Review;
8. Gemini Independent Scientific and Adversarial Audit;
9. ChatGPT Final Consolidation;
10. Baseline V1 Certified;
11. Release- und Implementierungsfreigabe;
12. Implementierung, primär mit Claude Code.

---

## 22. Sicherheit und Datenschutz

### 22.1 Zulässige Provenienzdaten

Technische Hostinformationen dürfen protokolliert werden, soweit sie für Reproduktion oder Audit relevant sind.

### 22.2 Datenminimierung

Nicht erforderliche personenbezogene Informationen SOLLEN nicht erfasst werden.

Benutzernamen und absolute Home-Pfade SOLLEN in veröffentlichten Manifesten durch portable Bezeichner ersetzt werden.

### 22.3 Signierte Manifeste

Kryptografische Signaturen sind für RCC-002 optional.

Sie werden empfohlen, wenn:

- Artefakte extern verteilt werden;
- mehrere Organisationen beteiligt sind;
- Manipulationsschutz über Dateihashes hinaus benötigt wird.

Eine Signatur ersetzt weder Prüfsummen noch Lineage.

---

## 23. Empfohlene Verzeichnisstruktur

```text
manifests/
  schemas/
  sources/
  stages/
  runs/
  datasets/
  reviews/
  reproductions/

build/
  rcc002/
    temporary/
    quarantine/
    candidates/

data/
  rcc002/
    releases/
      <dataset_id>/

reports/
  rcc002/
    validation/
    lineage/
    reproducibility/
    reviews/
```

Die Implementierung darf abweichende Pfade verwenden, sofern:

- die Namensräume eindeutig bleiben;
- keine Runtime-Module durch gleichnamige Dokumentationsordner dupliziert werden;
- alle Pfade im Manifest portabel referenziert werden;
- temporäre, quarantänisierte und veröffentlichte Ergebnisse klar getrennt sind.

---

## 24. Minimales kanonisches Dataset-Manifest

```json
{
  "manifest_schema_id": "rcc002.dataset-manifest/1.0.0",
  "manifest_type": "dataset",
  "manifest_id": "manifest:sha256:<computed-after-preimage>",
  "created_at_utc": "2026-07-23T00:00:00Z",
  "producer": {
    "component": "rcc002-manifest-builder",
    "version": "<implementation version>"
  },
  "project": "RCC-002",
  "status": "candidate",
  "dataset_id": "dataset:sha256:<digest>",
  "dataset_artifact_set_id": "dataset-artifact-set:sha256:<digest>",
  "build_id": "build:sha256:<digest>",
  "publication_run_id": "run:<timestamp>:<uuid>",
  "dataset_profile": "rcc002-canonical",
  "source_snapshot_ids": [
    "source:sha256:<digest>"
  ],
  "code_provenance": {
    "repository": "<repository identifier>",
    "commit_sha": "<commit>",
    "worktree_clean": true,
    "dirty_patch_sha256": null,
    "entrypoint": "<entrypoint>"
  },
  "configuration": {
    "profile": "<profile>",
    "canonical_sha256": "<digest>",
    "secret_fields_removed": true
  },
  "specification_profile": [
    {
      "document_id": "RCC-002-DP",
      "version": "<version>",
      "sha256": "<digest>"
    },
    {
      "document_id": "RCC-002-RM",
      "version": "0.4.0",
      "sha256": "<digest>"
    }
  ],
  "environment_identity": {
    "profile_id": "RCC_BUILD_ENV_IDENTITY_V2",
    "canonical_sha256": "<digest>"
  },
  "artifacts": [
    {
      "logical_name": "<name>",
      "artifact_id": "artifact:sha256:<digest>",
      "relative_path": "<relative path>",
      "schema_id": "<schema>",
      "byte_sha256": "<digest>",
      "semantic_sha256": "<digest>",
      "physical_layout_sha256": "<digest>",
      "size_bytes": 0,
      "row_count": 0,
      "min_timestamp_utc": "<timestamp>",
      "max_timestamp_utc": "<timestamp>",
      "publication_status": "candidate"
    }
  ],
  "quality_summary": {
    "manifest_schema_valid": true,
    "artifact_hashes_valid": true,
    "dataset_lineage_complete": true,
    "knowledge_lineage_complete": true,
    "required_tests_passed": true
  },
  "reviews": [
    {
      "reviewer_system": "claude",
      "status": "pending"
    },
    {
      "reviewer_system": "gemini",
      "status": "pending"
    }
  ],
  "publication": {
    "status": "candidate",
    "published_at_utc": null,
    "supersedes": []
  }
}
```

Der Beispielzeitstempel ist kein vorgegebener realer Buildzeitpunkt. Implementierungen MÜSSEN reale Werte einsetzen.

---

## 25. Veröffentlichungs-Gate

Ein RCC-002-Dataset darf nur `published` werden, wenn:

- [ ] Source Manifest vorhanden und gültig;
- [ ] alle Source Snapshots per SHA-256 verifiziert;
- [ ] Codeprovenienz vollständig;
- [ ] Arbeitsbaum sauber oder Dirty Patch vollständig dokumentiert;
- [ ] effektive Konfiguration kanonisiert und gehasht;
- [ ] Spezifikationsprofil vollständig;
- [ ] Umgebungsprovenienz vollständig;
- [ ] alle Stage Manifests gültig;
- [ ] alle Artefakte inventarisiert;
- [ ] alle Bytehashes gültig;
- [ ] alle semantischen Fingerprints gültig;
- [ ] Dataset Lineage vollständig und azyklisch;
- [ ] Knowledge Lineage vollständig;
- [ ] alle Datenvalidierungen bestanden;
- [ ] alle Schema- und Manifesttests bestanden;
- [ ] kein Pflichtartefakt quarantänisiert;
- [ ] Veröffentlichungsziel frei von stiller Überschreibung;
- [ ] atomare Veröffentlichung möglich;
- [ ] bekannte Einschränkungen dokumentiert;
- [ ] erforderliche Review- und Freigabestufe erreicht.

Ein einzelnes fehlgeschlagenes Pflichtkriterium blockiert die Veröffentlichung.

---

## 26. Akzeptanzkriterien der Implementierung

Die RCC-002-Reproduzierbarkeitsimplementierung ist akzeptabel, wenn:

1. ein vollständiger Build automatisch alle erforderlichen Manifeste erzeugt;
2. IDs ohne zirkuläre Abhängigkeit berechnet werden;
3. Zeitstempel und Run-UUIDs die deterministische Build-ID nicht verändern;
4. jede deterministische Eingabeänderung eine neue Build-ID erzeugt;
5. jedes veröffentlichte Artefakt bis zur Quelle rückverfolgbar ist;
6. jede wissenschaftliche Transformationsregel auf ein Spezifikationsobjekt zurückgeführt werden kann;
7. gleiche Inhalte geräteübergreifend mindestens E2 erreichen;
8. Parquet-Byteunterschiede nicht fälschlich als Inhaltsabweichung gelten;
9. ein Clean-Rebuild mit dokumentiertem Einstiegspunkt möglich ist;
10. fehlgeschlagene Builds keine finalen Ausgaben veröffentlichen;
11. alte Releases unveränderlich bleiben;
12. Geheimnisse aus Manifesten ausgeschlossen werden;
13. JSON-Schemata sämtliche Manifesttypen maschinell prüfen;
14. Claude- und Gemini-Reviewstatus nur anhand realer Reviews aktualisiert werden;
15. der vollständige Veröffentlichungs-Gate automatisiert geprüft wird;
16. der semantische Fingerprint den vollständigen registrierten Primärschlüssel `(market_type, symbol, interval, open_time)` und bei unkonsolidierten Multi-Provider-Daten zusätzlich `provider` verwendet;
17. physische Partitionierung und Containerparameter ausschließlich in `physical_layout_sha256`, nicht in `semantic_sha256`, eingehen;
18. die JSON-Kanonisierung die Golden Fixtures von `RCC_JSON_CANONICALIZATION_V1` bytegenau besteht;
19. `source_snapshot_id` weder Abrufzeit noch lokalen Pfad enthält;
20. `build_id` ausschließlich die Allowlist von `RCC_BUILD_ENV_IDENTITY_V2` verwendet;
21. E3 nur für dasselbe persistierte Artefakt oder bei identischer vollständiger kanonischer Vorabbildung verlangt wird;
22. Änderungen von Bytehash, physischem Layout oder `artifact_id` bei
    unverändertem semantischem Inhalt weder `build_id` noch `dataset_id`
    verändern;
23. jede Änderung der veröffentlichten physischen Artefaktmenge eine neue
    `dataset_artifact_set_id` erzeugt.

---

## 27. Offene Implementierungsentscheidungen

Folgende Punkte sind vor oder während der Implementierung festzulegen, ohne die wissenschaftliche Architektur dieses Dokuments zu ändern:

- konkrete JSON-Schema-Dateinamen und Versionsstrategie;
- genaue kanonische Tabellen-Hashimplementierung;
- Parquet-Writerprofil einschließlich Row-Group- und Kompressionsparametern;
- Lockdateiformat;
- konkrete CLI des Build-Einstiegspunkts;
- Retentionsdauer für Logs und quarantänisierte Builds;
- optionaler Einsatz signierter Manifeste;
- technische Ablage großer Source Snapshots;
- konkrete numerische Toleranzen für unabhängige Referenzimplementierungen.

Diese Entscheidungen MÜSSEN vor einem zertifizierten Dataset-Release dokumentiert werden.

---

## 28. Abgrenzung

Dieses Dokument:

- definiert keine Handelsstrategie;
- ersetzt keine Datenvalidierungsregeln;
- verändert keine Indikatorformeln;
- verändert keine Signal-, Regime-, Gate- oder Labeldefinition;
- zertifiziert noch keinen konkreten Datensatz;
- behauptet keine bereits durchgeführten Claude- oder Gemini-Reviews.

Es definiert die verbindliche Nachweis- und Reproduzierbarkeitsarchitektur, innerhalb der diese fachlichen Regeln umgesetzt werden.

---

## 29. Schlussbestimmung

RCC-002 betrachtet einen Datensatz erst dann als wissenschaftlich und technisch belastbar, wenn Dateninhalt, Transformationslogik, Herkunft, Umgebung, Konfiguration, Spezifikationsstand und Qualitätsstatus gemeinsam nachweisbar sind.

Der normative Kern lautet:

```text
Source provenance
+ code provenance
+ canonical configuration
+ specification profile
+ environment record
+ complete dataset lineage
+ complete knowledge lineage
+ validated artifacts
+ reproducible publication
= auditable RCC-002 dataset
```

Diese Version enthält die Korrekturen der dem Dokument zugeordneten Befunde
aus `RCC-002-SCR-001`, `RCC-002-SCR-002` und `RCC-002-SCR-003`.

Version `0.4.0`:

- übernimmt die vollständige verbindliche Review- und Freigabesequenz;
- aktualisiert sämtliche Spezifikationsabhängigkeiten;
- ergänzt das ID-Beispiel für `dataset_artifact_set_id`;
- präzisiert die Unveränderlichkeit bereits veröffentlichter
  `dataset_artifact_set_id`s und ihrer Artefakte;
- erlaubt semantisch identische Neuverpackungen nur mit neuem
  `dataset_artifact_set_id`;
- hält Claude- und Gemini-Reviews bis zu ihrer tatsächlichen Durchführung auf
  `pending`.

Sie gilt bis zum erneuten fokussierten Scientific Consistency Re-Review als:

`SCR-003-Corrected Draft – Re-Review Pending`

und begründet noch keine wissenschaftliche Freigabe, Certification oder
Implementierungsfreigabe.

---
