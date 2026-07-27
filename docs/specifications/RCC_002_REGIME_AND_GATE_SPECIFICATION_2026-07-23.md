# RCC-002 Regime and Gate Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-RG |
| Titel | Regime and Gate Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md` |
| Version | 0.5.1 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.5.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3; `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md`, Version 0.4.2 |
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
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-B03`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.5.0 korrigiert `SCR-005-B01`, `SCR-005-M01` und `SCR-005-M02`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.5.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
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

### 5.8 Profilversionen

Für die erste Baseline gilt:

| Profil-ID | Profilversion |
|---|---|
| `RCC_TREND_REGIME_RAW_V1` | `1.0.0` |
| `RCC_TREND_REGIME_PERSISTED_V1` | `1.0.0` |
| `RCC_CONTEXT_V1` | `1.0.0` |
| `GATE_RESEARCH_OPEN_V1` | `1.0.0` |
| `GATE_TREND_ALIGNED_V1` | `1.0.0` |
| `GATE_TREND_STRENGTH_ALIGNED_V1` | `1.0.0` |
| `LEGACY_BTC_REGIME_V1` | `1.0.0` |
| `GS_REGIME_RECONSTRUCTION_V1` | `1.0.0` |

Eine fachliche Regel-, Schwellen-, Persistenz- oder
Pflichtinputänderung benötigt mindestens eine neue Profilversion.

## 6. Eingabevertrag

### 6.1 Akzeptiertes S5-Eingangsschema

S5 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s4-signals/1.0.0
```

Eine unbekannte Major-Version wird fail-closed abgelehnt. Eine neuere
Minor-Version darf nur aufgrund einer registrierten S5-Kompatibilitätsregel
akzeptiert werden.

### 6.2 Pflichtfelder für S5

S5 benötigt:

- `market_type`;
- `symbol`;
- `interval`;
- `open_time`;
- `close_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- `quality_gate_pass`;
- `close`;
- `sma_close_200`;
- `sma_close_200_valid`;
- `sma_close_200_warmup_complete`;
- `sma_close_200_reason_codes`;
- `state_atr_relative_d`;
- `state_atr_relative_d_valid`;
- `state_atr_relative_d_reason_codes`;
- `score_atr_relative_c`;
- `score_atr_relative_c_valid`;
- `score_atr_relative_c_reason_codes`;
- `adx_wilder_14`;
- `adx_wilder_14_valid`;
- `adx_wilder_14_warmup_complete`;
- `adx_wilder_14_reason_codes`;
- `state_adx_strength_d`;
- `state_adx_strength_d_valid`;
- `state_adx_strength_d_reason_codes`;
- `score_adx_strength_c`;
- `score_adx_strength_c_valid`;
- `score_adx_strength_c_reason_codes`;
- die S3- und S4-Profil- und Schemametadaten.

Optionale Vergleichs- und Transparenzfelder:

- `state_ma200_trend_d`,
- `state_ema50_trend_d`,
- `sig_roc_momentum_d`.

Legacy- oder Rekonstruktionsprofile dürfen zusätzliche profilgebundene
Pflichtfelder verlangen. Diese werden nicht zu allgemeinen
RCC-TREND-REGIME-Pflichtfeldern.

### 6.3 S5-Hilfsgröße

S5 berechnet den kausalen SMA-200-Slope:

`ma200_slope_1440_pct_t = 100 * (sma_close_200_t / sma_close_200_(t-1440) - 1)`

Voraussetzungen:

- beide SMA-Werte gültig,
- beide Werte größer als null,
- alle erforderlichen Zeitpunkte gehören zum selben Segment,
- zwischen den Vergleichspunkten liegt keine Datenlücke.

### 6.4 Akzeptiertes S6-Eingangsschema

S6 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s5-regimes/1.0.0
```

Unbekannte Major-Versionen werden fail-closed abgelehnt.

### 6.5 S6-Pflichtfelder

S6 benötigt:

- alle unverändert durchgereichten S0-bis-S4-Felder;
- `regime_raw`;
- `regime_effective`;
- `regime_valid`;
- `regime_reason_codes`;
- `trend_strength`;
- `trend_strength_valid`;
- `trend_strength_reason_codes`;
- `volatility_relative`;
- `volatility_relative_valid`;
- `volatility_relative_reason_codes`;
- `regime_model_id`;
- `regime_model_version`;
- `regime_schema_id`;
- `regime_schema_version`;
- `regime_schema_ref`;
- die aktive Gate-Profil-ID und Gate-Profilversion aus der
  `semantic_build_configuration`.

### 6.6 Eingabeinvarianten

S5 und S6 MUST:

- ausschließlich freigegebene vorgelagerte Artefakte konsumieren,
- Schema- und Profilversionen prüfen,
- kanonische Schlüssel unverändert erhalten,
- die Sortierung `(market_type, symbol, interval, open_time)` unverändert
  erhalten,
- `market_segment_id` und `indicator_segment_id` unverändert durchreichen,
- Segmentgrenzen respektieren,
- ungültige Inputs nicht als neutral interpretieren.

Der logische Primärschlüssel bleibt in S5 und S6:

```text
(market_type, symbol, interval, open_time)
```

Wenn der Eingang noch nicht konsolidierte Multi-Provider-Daten enthält, MUSS
`provider` als zusätzlicher registrierter Schlüsselbestandteil unmittelbar
vor `market_type` geführt werden. State-, Reconciliation-, Fingerprint- und
Partitionierungsverträge MÜSSEN dieselbe Schlüsselvariante verwenden.

`timeframe` ist kein Aliasfeld eines kanonischen S5- oder S6-Schemas. Eine
Legacy-Migration nach `interval` MUSS vor S4 abgeschlossen sein.

### 6.7 Eingangsablehnung

Die jeweilige Stufe bricht vor einer fachlichen Verarbeitung ab bei:

- inkompatibler oder unbekannter Eingangsschema-ID;
- fehlendem Pflichtfeld;
- nicht registriertem Datentyp oder nicht registrierter Nullbarkeit;
- ungültigem Primärschlüssel;
- nichtkanonischer Sortierung;
- widersprüchlichen Gültigkeitsfeldern;
- unbekannter Profil-, Modell- oder Reason-Code-Registry-Version;
- nicht freigegebenem vorgelagertem Publication-Status.

Ein stageweiter Vertragsfehler wird nicht als zeilenweises `UNKNOWN` oder
`INVALID` weitergeführt, sondern führt zum fail-closed Abbruch der Stufe.

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

- `quality_gate_pass=false` ist,
- SMA200 oder Slope ungültig ist,
- Warm-up unvollständig ist,
- das Fenster eine Lücke überschreitet,
- `market_segment_id` oder `indicator_segment_id` nicht konsistent ist,
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

Der Wechsel eines zuvor gültigen effektiven Zustands nach `UNKNOWN` ist ein
tatsächlicher Übergang und wird mit `transition_to=UNKNOWN` protokolliert.
Der erstmalige bestätigte Wechsel von `UNKNOWN` nach `BULL`, `SIDE` oder
`BEAR` wird ebenfalls protokolliert.

Am Segmentanfang mit vorherigem und aktuellem Zustand `UNKNOWN` liegt kein
Übergang vor.

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

### 12.1 Erzeugtes Ausgangsschema

S5 erzeugt:

```text
rcc002.stage.s5-regimes/1.0.0
```

Das Ausgangsschema enthält alle S4-Felder unverändert und genau die
registrierten S5-Erweiterungsfelder dieses Abschnitts.

### 12.2 Kanonisches S5-Feldregister

| Feld | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|:---:|---|---|
| `regime_raw` | Enum `RegimeState` | Nein | `S5_REGIMES` | aktueller ungeglätteter Zustand |
| `regime_effective` | Enum `RegimeState` | Nein | `S5_REGIMES` | kausal persistierter Zustand |
| `regime_candidate` | Enum `RegimeState` | Nein | `S5_REGIMES` | aktuell zu bestätigender Zustand |
| `regime_candidate_count` | `UInt8` | Nein | `S5_REGIMES` | Anzahl aufeinanderfolgender Candidate-Bestätigungen, `0...3` |
| `regime_transition_flag` | `Boolean` | Nein | `S5_REGIMES` | tatsächlicher effektiver Zustandswechsel |
| `regime_transition_from` | Enum `RegimeState` | Ja | `S5_REGIMES` | vorheriger effektiver Zustand bei Übergang |
| `regime_transition_to` | Enum `RegimeState` | Ja | `S5_REGIMES` | neuer effektiver Zustand bei Übergang |
| `ma200_slope_1440_pct` | `Float64` | Ja | `S5_REGIMES` | kausaler SMA200-Slope |
| `trend_strength` | Enum `TrendStrength` | Nein | `S5_REGIMES` | richtungslose ADX-Klasse |
| `trend_strength_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit der Trendstärkeklasse |
| `trend_strength_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | Trendstärkegründe |
| `volatility_relative` | Enum `VolatilityRelative` | Nein | `S5_REGIMES` | richtungsloser ATR-Relativzustand |
| `volatility_relative_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit des Volatilitätszustands |
| `volatility_relative_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | Volatilitätsgründe |
| `regime_model_id` | `Utf8` | Nein | `S5_REGIMES` | aktive kanonische Modell-ID |
| `regime_model_version` | `Utf8` | Nein | `S5_REGIMES` | aktive Modellversion |
| `regime_schema_id` | `Utf8` | Nein | `S5_REGIMES` | `rcc002.stage.s5-regimes` |
| `regime_schema_version` | `Utf8` | Nein | `S5_REGIMES` | `1.0.0` |
| `regime_schema_ref` | `Utf8` | Nein | `S5_REGIMES` | `rcc002.stage.s5-regimes/1.0.0` |
| `regime_valid` | `Boolean` | Nein | `S5_REGIMES` | Gültigkeit von Roh- und Effektivregime |
| `regime_reason_codes` | geordnete Liste `Utf8` | Nein | `S5_REGIMES` | deterministische Regimegründe |

### 12.3 Kanonische Enum-Register

`RegimeState` verwendet ausschließlich:

```text
BULL
SIDE
BEAR
UNKNOWN
```

`TrendStrength` verwendet ausschließlich:

```text
WEAK
DEVELOPING
STRONG
UNKNOWN
```

`VolatilityRelative` verwendet ausschließlich:

```text
BELOW_REFERENCE
AT_REFERENCE
ABOVE_REFERENCE
UNKNOWN
```

Ein S5-Wert `INVALID` ist in keinem dieser Enums zulässig.

### 12.4 Modell- und Schemametadaten

Die erste kanonische Modellidentität lautet:

```text
regime_model_id=RCC002_TREND_CONTEXT_REGIME_V1
regime_model_version=1.0.0
regime_schema_id=rcc002.stage.s5-regimes
regime_schema_version=1.0.0
regime_schema_ref=rcc002.stage.s5-regimes/1.0.0
```

Die Modellidentität umfasst die Rohregime-, Persistenz- und Kontextregeln
dieses Dokuments. Legacy- oder GS-Rekonstruktionsmodelle verwenden eigene
Modell- und Schemaidentitäten.

### 12.5 Regimegültigkeit

Es gilt:

```text
regime_valid =
    required_regime_inputs_valid
    AND slope_warmup_complete
    AND segment_consistent
    AND result_finite
    AND regime_raw IN {BULL, SIDE, BEAR}
    AND regime_effective IN {BULL, SIDE, BEAR}
```

Wenn `regime_valid=false`, gilt:

- `regime_raw=UNKNOWN` oder `regime_effective=UNKNOWN`;
- mindestens ein invalidierender `regime_reason_code`;
- `UNKNOWN` wird nicht als `SIDE` interpretiert.

Während der ersten beiden gültigen Candidate-Kerzen kann
`regime_raw` bereits gültig sein, während `regime_effective=UNKNOWN` bleibt.
In diesem Initialisierungsfall ist `regime_valid=false`, bis erstmals ein
effektiver Zustand bestätigt wurde.

Die Gültigkeit von Trendstärke und Volatilität ist feldbezogen. Ein
ungültiger ADX-Kontext macht ein anderweitig berechenbares Regime nicht
ungültig.

### 12.6 Kontextgültigkeit

Für Trendstärke gilt:

```text
trend_strength_valid = adx_wilder_14_valid
```

Wenn `trend_strength_valid=false`:

```text
trend_strength=UNKNOWN
```

Für relative Volatilität gilt:

```text
volatility_relative_valid = state_atr_relative_d_valid
```

Wenn `volatility_relative_valid=false`:

```text
volatility_relative=UNKNOWN
```

### 12.7 S5-Reason-Code-Register

```text
regime_reason_code_registry_version=1.0.0
```

| Priorität | Code | Ziel | Invalidierend |
|---:|---|---|:---:|
| 30 | `REG_INPUT_QUALITY_GATE_FAILED` | Regime | Ja |
| 40 | `REG_INPUT_INVALID` | Regime | Ja |
| 50 | `REG_WARMUP_INCOMPLETE` | Regime | Ja |
| 60 | `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` | Regime | Ja |
| 70 | `REG_SLOPE_DENOMINATOR_INVALID` | Regime | Ja |
| 80 | `REG_NONFINITE_RESULT` | Regime | Ja |
| 90 | `REG_EFFECTIVE_UNCONFIRMED` | Regime | Ja |
| 100 | `REG_SEGMENT_RESET` | Regime | Ja |
| 110 | `REG_TREND_STRENGTH_INPUT_INVALID` | Trendstärke | Ja |
| 120 | `REG_VOLATILITY_INPUT_INVALID` | Volatilität | Ja |

Die drei Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

#### 12.7.1 Regime-Reason-Bildung

`regime_reason_codes` enthält alle sicher feststellbaren zutreffenden Codes:

- `REG_INPUT_QUALITY_GATE_FAILED` bei `quality_gate_pass=false`;
- `REG_INPUT_INVALID` bei ungültigem erforderlichem Preis- oder SMA-Input;
- `REG_WARMUP_INCOMPLETE` vor vollständigem Slope-Warm-up;
- `REG_WINDOW_CROSSES_INDICATOR_SEGMENT`, wenn die Slope-Abhängigkeit eine
  Segmentgrenze überschreiten würde;
- `REG_SLOPE_DENOMINATOR_INVALID` bei nichtpositivem oder ungültigem
  Vergleichs-SMA;
- `REG_NONFINITE_RESULT` bei nicht endlichem Rechenergebnis;
- `REG_EFFECTIVE_UNCONFIRMED`, solange ein gültiger Rohzustand noch keinen
  ersten effektiven Zustand bestätigt hat;
- `REG_SEGMENT_RESET` auf der ersten Zeile nach einem Segmentwechsel.

Bei vollständig gültigem Roh- und Effektivregime ohne zutreffenden Hinweis
ist die Liste leer.

#### 12.7.2 Kontext-Reason-Bildung

`trend_strength_reason_codes` enthält ausschließlich
`REG_TREND_STRENGTH_INPUT_INVALID`, wenn der erforderliche ADX-Input ungültig
ist; andernfalls ist die Liste leer.

`volatility_relative_reason_codes` enthält ausschließlich
`REG_VOLATILITY_INPUT_INVALID`, wenn der erforderliche ATR-Relativzustand
ungültig ist; andernfalls ist die Liste leer.

### 12.8 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle S4-Felder in unveränderter S4-Reihenfolge;
2. die S5-Felder in der Reihenfolge aus Abschnitt 12.2.

Nicht registrierte Zusatzfelder oder alternative Aliasfelder machen das
Artefakt nicht kanonisch.

Optionale transparente Evidenzfelder:

- `regime_price_above_ma200`,
- `regime_price_below_ma200`,
- `regime_slope_positive`,
- `regime_slope_negative`.

Diese Evidenzfelder gehören nicht zu
`rcc002.stage.s5-regimes/1.0.0`. Werden sie benötigt, müssen sie in einer
separaten registrierten Diagnose-View veröffentlicht werden.

### 12.9 Schema-Fingerprint und Kompatibilität

Der S5-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Feld- und Enum-Semantik;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Modell-, Schema- und Registry-Versionen;
- Reason-Code-Prioritäten;
- Kompatibilitätsregeln.

Für S5 gilt semantische Versionierung. Eine neue Minor-Version wird nur
aufgrund einer registrierten Kompatibilitätsregel akzeptiert. Unbekannte
Major-Versionen sind fail-closed abzulehnen.

### 12.10 Komponentenidentität

```text
component_id=RCC002_S5_REGIME_CLASSIFIER
component_version=0.4.0
```

Die Implementierung manifestiert zusätzlich Source-Tree- oder
Commit-Identität, numerisches Profil, Eingangs- und Ausgangsschema-Fingerprint
sowie Modell-, State- und Registry-Versionen.

## 13. Datenqualitäts-Gate

### 13.1 Zweck

Vor jeder Richtungsregel wird ein gemeinsames Datenqualitäts-Gate angewandt.

### 13.2 `data_gate_pass`

S6 bildet:

```text
data_gate_pass = quality_gate_pass
```

`data_gate_pass` ist damit die unveränderte S6-Entscheidungsabbildung des
kanonischen S2-Qualitäts-Gates. Es wird nicht aus Regime-, Signal-, ADX- oder
Strategiefeldern abgeleitet.

Diese Gleichheit gilt ausschließlich nach erfolgreicher stageweiter Prüfung
von Schema, Primärschlüssel, Sortierung und Segmentvertrag. Eine Verletzung
dieser Strukturverträge bricht S6 ab und erzeugt keine kanonische S6-Zeile.
Sie darf weder als `data_gate_pass=false` noch als `gate_state=INVALID`
zeilenweise serialisiert werden.

Die einzige normative Wahrheitstabelle lautet:

| Strukturvertrag | `quality_gate_pass` | Profilpflichtinputs | S6-Ergebnis |
|---|:---:|---|---|
| ungültig | beliebig | nicht ausgewertet | Stage-Abbruch; keine S6-Zeile |
| gültig | `false` | nicht ausgewertet | `data_gate_pass=false`; `gate_valid=true`; `BLOCK_BOTH` |
| gültig | `true` | gültig | `data_gate_pass=true`; profilspezifische Auswertung; `gate_valid=true` |
| gültig | `true` | ungültig | `data_gate_pass=true`; `gate_valid=false`; `INVALID` |

S3-, S4-, Regime- oder ADX-Felder werden erst durch die jeweils konsumierende
Strategie beziehungsweise Richtungsregel geprüft. Dadurch bleibt
`GATE_RESEARCH_OPEN_V1` auch während des S3-/S4-/S5-Warm-ups eine tatsächlich
offene Datenqualitätsbaseline, ohne ungültige Strategiefeatures als gültig
umzudefinieren.

### 13.3 Fail-closed

Wenn `data_gate_pass = false`:

- `allow_long = false`,
- `allow_short = false`,
- beide Richtungslisten enthalten `GATE_DATA_QUALITY_FAILED`.

Dies gilt unabhängig vom gewählten Richtungs-Gate.

Ein deterministisch festgestelltes `data_gate_pass=false` macht das Gate nicht
automatisch ungültig. Wenn alle zur Feststellung benötigten Felder gültig
waren, ist das Gate gültig ausgewertet und erhält:

```text
gate_valid=true
gate_state=BLOCK_BOTH
```

Nur ungültige profilabhängige Pflichtinputs bei strukturell gültigem Eingang
und `data_gate_pass=true` führen zeilenweise zu:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

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

Wenn `data_gate_pass` deterministisch gebildet wurde, bleibt
`gate_valid=true`. Bei `data_gate_pass=false` ist der Zustand
`BLOCK_BOTH`, nicht `INVALID`.

Ein ungültiges oder noch nicht bestätigtes Regime beeinflusst dieses Profil
nicht und wird deshalb nicht als Gate-Invalidität übernommen.

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

Bei gültigem:

- `SIDE`

werden beide Richtungen blockiert.

Das Ergebnis ist:

```text
gate_valid=true
gate_state=BLOCK_BOTH
```

Bei `data_gate_pass=true` und zugleich `UNKNOWN` oder `regime_valid=false`
sind die profilabhängigen Pflichtinputs ungültig. Das Ergebnis ist:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

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

Gültig mit `gate_state=BLOCK_BOTH` werden beide Richtungen blockiert bei:

- `SIDE`;
- `WEAK`;
- fehlgeschlagenem Daten-Gate.

Bei `data_gate_pass=true` werden beide Richtungen ungültig mit
`gate_state=INVALID` blockiert bei:

- `UNKNOWN`;
- `regime_valid=false`;
- unbekannter oder ungültiger Trendstärke;
- sonstigem ungültigem profilabhängigem Pflichtinput.

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

### 18.1 Erzeugtes Ausgangsschema

S6 erzeugt:

```text
rcc002.stage.s6-gates/1.0.0
```

Das Ausgangsschema enthält alle S5-Felder unverändert und genau die
registrierten S6-Erweiterungsfelder dieses Abschnitts.

### 18.2 Kanonisches S6-Feldregister

| Feld | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|:---:|---|---|
| `allow_long` | `Boolean` | Nein | `S6_GATES` | Long-Prüfung nach aktivem Profil erlaubt |
| `allow_short` | `Boolean` | Nein | `S6_GATES` | Short-Prüfung nach aktivem Profil erlaubt |
| `data_gate_pass` | `Boolean` | Nein | `S6_GATES` | Abbildung des kanonischen S2-Qualitäts-Gates |
| `gate_state` | Enum `GateState` | Nein | `S6_GATES` | zusammengefasster Gate-Zustand |
| `gate_reason_codes_long` | geordnete Liste `Utf8` | Nein | `S6_GATES` | Long-spezifische Gründe |
| `gate_reason_codes_short` | geordnete Liste `Utf8` | Nein | `S6_GATES` | Short-spezifische Gründe |
| `gate_profile_id` | `Utf8` | Nein | `S6_GATES` | aktive Gatepolicy |
| `gate_profile_version` | `Utf8` | Nein | `S6_GATES` | Version der aktiven Gatepolicy |
| `gate_schema_id` | `Utf8` | Nein | `S6_GATES` | `rcc002.stage.s6-gates` |
| `gate_schema_version` | `Utf8` | Nein | `S6_GATES` | `1.0.0` |
| `gate_schema_ref` | `Utf8` | Nein | `S6_GATES` | `rcc002.stage.s6-gates/1.0.0` |
| `gate_valid` | `Boolean` | Nein | `S6_GATES` | profilabhängige Auswertung vollständig gültig |
| `gate_evaluated_at` | UTC-Timestamp in Millisekunden | Nein | `S6_GATES` | Point-in-Time-Verfügbarkeit der ausgewerteten Zeile |
| `regime_model_id` | `Utf8` | Nein | `S5_REGIMES`, durchgereicht | referenziertes S5-Modell |
| `regime_model_version` | `Utf8` | Nein | `S5_REGIMES`, durchgereicht | referenzierte S5-Modellversion |

`regime_model_id` und `regime_model_version` werden nicht erneut erzeugt,
sondern unverändert aus S5 durchgereicht. Sie stehen in der kanonischen
S6-Pflichtausgabe, besitzen aber weiterhin S5-Eigentum.

### 18.3 Gate-State-Enum

`GateState` verwendet ausschließlich:

- `ALLOW_BOTH`,
- `ALLOW_LONG_ONLY`,
- `ALLOW_SHORT_ONLY`,
- `BLOCK_BOTH`,
- `INVALID`.

Ein zusätzlicher Wert `UNKNOWN` ist in `GateState` nicht zulässig.

### 18.4 Gate-State-Wahrheitsregel

```text
if gate_valid = false:
    gate_state = INVALID
    allow_long = false
    allow_short = false
elif allow_long = true and allow_short = true:
    gate_state = ALLOW_BOTH
elif allow_long = true and allow_short = false:
    gate_state = ALLOW_LONG_ONLY
elif allow_long = false and allow_short = true:
    gate_state = ALLOW_SHORT_ONLY
else:
    gate_state = BLOCK_BOTH
```

Für das jeweils aktive Profil gilt:

- `INVALID`, wenn dessen erforderliche Daten oder Zustände nicht berechenbar
  sind; beide Richtungen sind `false` und `gate_valid = false`.
- `BLOCK_BOTH`, wenn alle erforderlichen Zustände gültig sind, die Policy aber
  keine Richtung erlaubt; `gate_valid = true`.

Ein Unknown-Regime führt daher bei trendgerichteten Profilen zu `INVALID`, beim
regimeunabhängigen `GATE_RESEARCH_OPEN_V1` jedoch nicht.

### 18.5 Profilabhängige Pflichtinputs

Die profilabhängigen Pflichtinputs werden nur ausgewertet, wenn
`data_gate_pass=true`. Bei deterministisch festgestelltem
`data_gate_pass=false` endet die fachliche Auswertung mit einem gültigen
`BLOCK_BOTH`; ungültige nachgelagerte Profilinputs erzeugen in dieser Zeile
keine zusätzliche Gate-Invalidität.

| Gate-Profil | Erforderliche gültige Inputs |
|---|---|
| `GATE_RESEARCH_OPEN_V1` | `data_gate_pass` deterministisch gebildet |
| `GATE_TREND_ALIGNED_V1` | `data_gate_pass`, `regime_valid`, `regime_effective` |
| `GATE_TREND_STRENGTH_ALIGNED_V1` | `data_gate_pass`, `regime_valid`, `regime_effective`, `trend_strength_valid`, `trend_strength` |

`volatility_relative` ist in keinem der drei Baseline-Gateprofile
Pflichtinput. Seine bloße Verfügbarkeit erzeugt keine Gatebedingung.

### 18.6 Gate-Profil- und Schemametadaten

Für alle drei Baseline-Profile gilt:

```text
gate_profile_version=1.0.0
gate_schema_id=rcc002.stage.s6-gates
gate_schema_version=1.0.0
gate_schema_ref=rcc002.stage.s6-gates/1.0.0
```

Genau eine der folgenden Profil-IDs ist je S6-Artefakt aktiv:

```text
GATE_RESEARCH_OPEN_V1
GATE_TREND_ALIGNED_V1
GATE_TREND_STRENGTH_ALIGNED_V1
```

### 18.7 Point-in-Time-Semantik

Es gilt:

```text
gate_evaluated_at = close_time
```

`gate_evaluated_at` ist kein Build-Wanduhrzeitstempel. Eine Gateentscheidung
der Zeile `t` darf erst ab diesem Verfügbarkeitszeitpunkt konsumiert werden.

### 18.8 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle S5-Felder in unveränderter S5-Reihenfolge;
2. die S6-eigenen Felder aus Abschnitt 18.2 in Tabellenreihenfolge, wobei die
   bereits vorhandenen S5-Felder `regime_model_id` und
   `regime_model_version` nicht dupliziert werden.

Alternative Aliasfelder wie `gate_inputs_valid` oder `gate_reason_mask` sind
unzulässig.

### 18.9 Schema-Fingerprint und Kompatibilität

Der S6-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen und Nullbarkeit;
- Feld- und Enum-Semantik;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Profil-, Schema- und Registry-Versionen;
- Reason-Code-Prioritäten;
- Kompatibilitätsregeln.

Für S6 gilt semantische Versionierung. Unbekannte Major-Versionen sind
fail-closed abzulehnen. Neue Minor-Versionen benötigen eine registrierte
Kompatibilitätsregel.

### 18.10 Komponentenidentität

```text
component_id=RCC002_S6_GATE_EVALUATOR
component_version=0.4.0
```

Die Implementierung manifestiert zusätzlich Source-Tree- oder
Commit-Identität, Eingangs- und Ausgangsschema-Fingerprint, Gate-Profil und
Reason-Code-Registry-Version.

## 19. Reason Codes

### 19.1 Verbindliches Registry-Profil

```text
gate_reason_code_registry_version=1.0.0
```

### 19.2 Verbindliches S6-Reason-Code-Register

| Priorität | Code | Richtung | Klasse |
|---:|---|---|---|
| 30 | `GATE_INPUT_INVALID` | beide | invalidierend |
| 40 | `GATE_WARMUP_INCOMPLETE` | beide | invalidierend |
| 50 | `GATE_SEGMENT_RESET` | beide | invalidierend |
| 60 | `GATE_REGIME_UNKNOWN` | beide | invalidierend für trendgerichtete Profile |
| 70 | `GATE_TREND_STRENGTH_UNKNOWN` | beide | invalidierend für das Stärkeprofil |
| 80 | `GATE_STATE_INVALID` | beide | invalidierend |
| 90 | `GATE_DATA_QUALITY_FAILED` | beide | gültige Blockierung |
| 100 | `GATE_LONG_BLOCKED_SIDE` | Long | gültige Blockierung |
| 110 | `GATE_LONG_BLOCKED_BEAR` | Long | gültige Blockierung |
| 120 | `GATE_LONG_BLOCKED_WEAK_TREND` | Long | gültige Blockierung |
| 130 | `GATE_SHORT_BLOCKED_SIDE` | Short | gültige Blockierung |
| 140 | `GATE_SHORT_BLOCKED_BULL` | Short | gültige Blockierung |
| 150 | `GATE_SHORT_BLOCKED_WEAK_TREND` | Short | gültige Blockierung |
| 160 | `GATE_LONG_ALLOWED_RESEARCH_OPEN` | Long | Freigabe |
| 170 | `GATE_SHORT_ALLOWED_RESEARCH_OPEN` | Short | Freigabe |
| 180 | `GATE_LONG_ALLOWED_BULL` | Long | Freigabe |
| 190 | `GATE_SHORT_ALLOWED_BEAR` | Short | Freigabe |
| 200 | `GATE_LONG_ALLOWED_BULL_WITH_STRENGTH` | Long | Freigabe |
| 210 | `GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH` | Short | Freigabe |

Die Einstufung „invalidierend“ ist profilabhängig, soweit die Tabelle dies
ausdrücklich bestimmt. Ein Unknown-Regime invalidiert das Research-Open-Profil
nicht, weil dieses Profil das Regime nicht konsumiert.

### 19.3 Richtungsbezogene Bildung

`gate_reason_codes_long` enthält nur:

- richtungsneutrale System-, Daten- und Invaliditätscodes;
- Long-spezifische Blockierungs- oder Freigabecodes.

`gate_reason_codes_short` enthält nur:

- richtungsneutrale System-, Daten- und Invaliditätscodes;
- Short-spezifische Blockierungs- oder Freigabecodes.

Ein Long-spezifischer Code darf nicht in der Short-Liste erscheinen und
umgekehrt.

### 19.4 Deterministische Serialisierung

Beide Reason-Code-Listen sind:

- nicht null;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes als leere Liste serialisiert.

Unbekannte Codes sind unter Registry-Version `1.0.0` unzulässig.

## 20. Gate-Reason-Priorität

### 20.1 Primärer Reason Code

Der primäre Reason Code einer Richtung ist der erste Code ihrer sortierten
vollständigen Liste.

Ein separates Feld für den primären Reason Code wird in
`rcc002.stage.s6-gates/1.0.0` nicht geführt.

### 20.2 Vollständigkeit

Alle zutreffenden, sicher auswertbaren Gründe bleiben erhalten. Nach einem
stageweiten Schemafehler wird keine zeilenweise Gateausgabe erzeugt. Nach
einem zeilenweisen ungültigen Pflichtinput dürfen keine fachlichen
Folgeprüfungen künstliche Zusatzgründe erzeugen.

### 20.3 Konsistenz mit `gate_valid`

Wenn eine Richtungsliste einen für das aktive Profil invalidierenden Code
enthält:

```text
gate_valid=false
gate_state=INVALID
allow_long=false
allow_short=false
```

Codes der Klasse „gültige Blockierung“ sind mit `gate_valid=true` vereinbar.
Freigabecodes sind nur bei der jeweiligen `allow_* = true` zulässig.

### 20.4 Deterministische Auswertungsreihenfolge

S6 bildet die Reason-Code-Listen in folgender Reihenfolge:

1. Vor der Zeilenauswertung werden Schema-, Schlüssel-, Sortierungs- und
   Segmentvertrag stageweit geprüft. Ein Fehler bricht S6 ohne Zeilenausgabe
   ab.
2. Ist bei strukturell gültigem Eingang `data_gate_pass=false`, erhalten beide Listen ausschließlich
   `GATE_DATA_QUALITY_FAILED`; die Auswertung endet mit gültigem
   `BLOCK_BOTH`.
3. Bei `data_gate_pass=true` werden ausschließlich die Pflichtinputs des
   aktiven Profils geprüft.
4. Sind diese ungültig, werden die Invaliditätscodes nach Abschnitt 20.5
   gebildet; die Auswertung endet mit `INVALID`.
5. Sind alle Pflichtinputs gültig, werden für jede Richtung alle nicht
   erfüllten Policyprädikate als Blockierungscodes oder bei vollständig
   erfüllter Regel genau der registrierte Freigabecode ausgegeben.
6. Abschließend werden die Listen dedupliziert und nach Registry-Priorität
   sortiert.

### 20.5 Abbildung ungültiger S5-Zustände

Bei einem für das aktive Profil erforderlichen ungültigen Regime werden in
beide Richtungslisten aufgenommen:

- `GATE_WARMUP_INCOMPLETE`, wenn `regime_reason_codes`
  `REG_WARMUP_INCOMPLETE` oder `REG_EFFECTIVE_UNCONFIRMED` enthält;
- `GATE_SEGMENT_RESET`, wenn `regime_reason_codes`
  `REG_SEGMENT_RESET` oder `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` enthält;
- immer `GATE_REGIME_UNKNOWN`.

Bei ungültiger erforderlicher Trendstärke wird zusätzlich in beide Listen
aufgenommen:

```text
GATE_TREND_STRENGTH_UNKNOWN
```

Sonstige zeilenbezogene ungültige Pflichtinputs erzeugen:

```text
GATE_INPUT_INVALID
```

### 20.6 Abbildung gültiger Policyzustände

Für `GATE_RESEARCH_OPEN_V1` werden bei `data_gate_pass=true` exakt ausgegeben:

- Long: `GATE_LONG_ALLOWED_RESEARCH_OPEN`;
- Short: `GATE_SHORT_ALLOWED_RESEARCH_OPEN`.

Für `GATE_TREND_ALIGNED_V1` gilt:

| Regime | Long-Code | Short-Code |
|---|---|---|
| `BULL` | `GATE_LONG_ALLOWED_BULL` | `GATE_SHORT_BLOCKED_BULL` |
| `SIDE` | `GATE_LONG_BLOCKED_SIDE` | `GATE_SHORT_BLOCKED_SIDE` |
| `BEAR` | `GATE_LONG_BLOCKED_BEAR` | `GATE_SHORT_ALLOWED_BEAR` |

Für `GATE_TREND_STRENGTH_ALIGNED_V1` werden zunächst dieselben
Regimeblockierungen wie oben gebildet. Zusätzlich erzeugt `WEAK` für die
jeweilige Richtung den entsprechenden
`GATE_*_BLOCKED_WEAK_TREND`-Code.

Bei `DEVELOPING` oder `STRONG` und passender Regimerichtung ersetzt der
jeweilige Aligned-Freigabecode den profilspezifischen Freigabecode:

- Long: `GATE_LONG_ALLOWED_BULL_WITH_STRENGTH`;
- Short: `GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH`.

Eine Richtung mit mindestens einem Blockierungscode darf keinen Freigabecode
enthalten.

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

Diese Felder gehören ausschließlich zum separaten Vergleichsschema:

```text
rcc002.comparison.s5-legacy-btc-regime/1.0.0
```

Sie dürfen nicht im kanonischen
`rcc002.stage.s5-regimes/1.0.0` enthalten sein.

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

Sie verwendet ein separates registriertes Vergleichsschema und darf weder das
kanonische S5-Modell noch das kanonische S6-Gateartefakt überschreiben.

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

### 28.1 State-Snapshot-Schema

Der kanonische S5-State-Snapshot erfüllt:

```text
state_schema_id=rcc002.state.s5-regimes
state_schema_version=1.0.0
state_schema_ref=rcc002.state.s5-regimes/1.0.0
```

Der S5-State Snapshot enthält mindestens:

- `state_schema_id`;
- `state_schema_version`;
- `state_schema_ref`;
- `parent_build_id`;
- `market_type`;
- `symbol`;
- `interval`;
- `last_open_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- die letzten 1.440 gültigen SMA200-Kontextwerte oder einen semantisch
  äquivalenten registrierten Rolling State;
- `regime_effective`;
- `regime_candidate`;
- `regime_candidate_count`;
- `regime_model_id`;
- `regime_model_version`;
- `state_payload_sha256`.

### 28.2 State-Feldvertrag

| Feld | Logischer Typ | Nullbar |
|---|---|:---:|
| `state_schema_id` | `Utf8` | Nein |
| `state_schema_version` | `Utf8` | Nein |
| `state_schema_ref` | `Utf8` | Nein |
| `parent_build_id` | `Utf8` | Nein |
| `market_type` | `Utf8` | Nein |
| `symbol` | `Utf8` | Nein |
| `interval` | `Utf8` | Nein |
| `last_open_time` | UTC-Timestamp in Millisekunden | Nein |
| `market_segment_id` | `Utf8` | Nein |
| `indicator_segment_id` | `Utf8` | Nein |
| `sma200_context_state` | registrierter geordneter Float64-State | Nein |
| `regime_effective` | Enum `RegimeState` | Nein |
| `regime_candidate` | Enum `RegimeState` | Nein |
| `regime_candidate_count` | `UInt8` | Nein |
| `regime_model_id` | `Utf8` | Nein |
| `regime_model_version` | `Utf8` | Nein |
| `state_payload_sha256` | 64-stelliger Lowercase-Hex-String | Nein |

Für noch nicht konsolidierte Multi-Provider-Daten enthält der Snapshot
zusätzlich das nicht nullbare Feld `provider`. Seine Anwesenheit MUSS der
Schlüsselvariante des zugehörigen S5-Artefakts entsprechen.

Der konkrete semantische Inhalt von `sma200_context_state` muss vor
`Approved for Implementation` versioniert werden. Er muss die serielle
Slope-Berechnung exakt reproduzieren.

### 28.3 Anschlussprüfung

State darf nur übernommen werden, wenn:

- Parent-Build-ID stimmt,
- Schlüssel unmittelbar anschließt,
- kein Gap vorliegt,
- `market_segment_id` und `indicator_segment_id` unverändert fortgesetzt
  werden,
- Modellversion identisch ist,
- State-Schemaversion kompatibel ist,
- State-Checksumme stimmt.

Andernfalls wird der State verworfen und der vollständige S5-Warm-up neu
begonnen.

### 28.4 Parität

Serielle und partitionierte Berechnung MUST identische diskrete Zustände und
innerhalb der Float-Toleranz identische Slope-Werte erzeugen.

S6 ist zeilenweise und benötigt keinen eigenen rekursiven State Snapshot.
Physische Partitionierung darf seine Ausgaben nicht verändern.

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

Zusätzlich gilt zeilenweise:

```text
S5.market_segment_id = S4.market_segment_id
S5.indicator_segment_id = S4.indicator_segment_id
S6.market_segment_id = S5.market_segment_id
S6.indicator_segment_id = S5.indicator_segment_id
```

S5 und S6 dürfen weder:

- vorgelagerte Gültigkeitsfelder umdeuten;
- S4-Signalwerte verändern;
- neue Markt- oder Indikatorsegment-IDs erzeugen;
- Regime- oder Gatefelder unter Aliasnamen duplizieren;
- S7-Forward-Returns oder Labels erzeugen.

Eine zeilenweise Reconciliation muss für jedes durchgereichte vorgelagerte
Feld semantische Gleichheit bestätigen.

Dies konkretisiert für S5 und S6 das kanonische Row-Preservation-Prinzip
aus `RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

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

### 31.5 S5-Schema- und Gültigkeitstests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s4-signals/1.0.0`;
- Ablehnung unbekannter S4- oder S5-Major-Versionen;
- exakte S5-Spaltenallowlist und Spaltenreihenfolge;
- exakte Typen, Nullbarkeit und Enum-Werte;
- `S5_rows = S4_rows`;
- unveränderte S4-Felder und Primärschlüssel;
- unveränderte `market_segment_id` und `indicator_segment_id`;
- `UNKNOWN` statt eines unzulässigen Regimewerts `INVALID`;
- `regime_valid=false` während unbestätigter Initialisierung;
- feldbezogene Kontextgültigkeit unabhängig von `regime_valid`;
- deterministische S5-Reason-Code-Reihenfolge;
- State-Snapshot-Schema `rcc002.state.s5-regimes/1.0.0`;
- Ablehnung eines inkompatiblen oder nicht anschließenden State Snapshots.

## 32. Testanforderungen für S6

### 32.1 Research Open

- `data_gate_pass=true` → beide erlaubt, `ALLOW_BOTH`, `gate_valid=true`;
- deterministisches `data_gate_pass=false` → beide blockiert, `BLOCK_BOTH`,
  `gate_valid=true`;
- strukturell ungültiger Eingang → Stage-Abbruch, keine S6-Zeile.

### 32.2 Trend Aligned

- Bull → nur Long,
- Bear → nur Short,
- Side → beide blockiert, `BLOCK_BOTH`, `gate_valid=true`,
- Unknown → beide blockiert, `INVALID`, `gate_valid=false`.

### 32.3 Trend Strength Aligned

- Bull + Developing/Strong → nur Long,
- Bear + Developing/Strong → nur Short,
- Bull/Bear + Weak → beide blockiert, `BLOCK_BOTH`, `gate_valid=true`,
- Unknown-Stärke → beide blockiert, `INVALID`, `gate_valid=false`.

### 32.4 Reason Codes

Für jede Wahrheitstabellenzeile werden geprüft:

- Boolean-Ausgaben,
- `gate_state`,
- primärer Reason Code,
- vollständige Reason-Code-Liste.

### 32.5 Richtungsunabhängigkeit

Blockierung einer Richtung darf die Gegenrichtung nur freigeben, wenn deren
eigene Regel vollständig erfüllt ist.

### 32.6 S6-Schema- und Gültigkeitstests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s5-regimes/1.0.0`;
- Ablehnung unbekannter S5- oder S6-Major-Versionen;
- exakte S6-Spaltenallowlist und Spaltenreihenfolge;
- exakte Typen, Nullbarkeit und Gate-State-Enums;
- `S6_rows = S5_rows`;
- unveränderte S5-Felder und Primärschlüssel;
- `data_gate_pass = quality_gate_pass`;
- gültiges `BLOCK_BOTH` bei deterministischem Datenqualitätsfehler;
- `INVALID` ausschließlich bei `gate_valid=false`;
- keine Felder `gate_inputs_valid` oder `gate_reason_mask`;
- profilabhängige statt globale Pflichtinputs;
- `gate_evaluated_at = close_time`;
- deterministische, richtungsgetrennte Reason-Code-Listen;
- keine Long-Codes in der Short-Liste und keine Short-Codes in der
  Long-Liste.

## 33. Kausalitäts-, Paritäts- und Property-Tests

### 33.1 Numerisches Profil

Das normative numerische Profil für S5 lautet:

```text
regime_numeric_profile_id=RCC002_FLOAT64_REGIME_NUMERICS_V1
regime_numeric_profile_version=1.0.0
```

Für unabhängige `Float64`-Vergleiche gelten:

- `absolute_tolerance = 1e-12`;
- `relative_tolerance = 1e-10`.

Der Vergleich erfolgt komponentenweise nach:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Regime-, Kontext-, Gate-, Gültigkeits- und Reason-Code-Ausgaben müssen exakt
übereinstimmen. Schwellenentscheidungen verwenden ungerundete kanonische
Werte.

### 33.2 Verbindliche Eigenschaften

MUST geprüft werden:

- Änderungen nach `t` verändern S5/S6 bei `t` nicht,
- identische Inputs erzeugen identische Outputs,
- Rohregime ist bei gültigen Inputs exklusiv,
- persistiertes Regime besitzt immer genau einen Zustand,
- Candidate Count ist nie negativ,
- Unknown setzt Candidate State deterministisch zurück,
- fail-closed Daten-Gate erlaubt nie eine Richtung bei fehlgeschlagener
  Datenqualität,
- `gate_valid=false` impliziert `gate_state=INVALID`,
- `gate_state=INVALID` impliziert beide Richtungen `false`,
- `gate_state=BLOCK_BOTH` impliziert `gate_valid=true`,
- Gate-State und beide Richtungs-Booleans erfüllen exakt Abschnitt 18.4,
- jedes S5-Enum enthält ausschließlich registrierte Werte,
- serielle und partitionierte Berechnung stimmen überein.

## 34. Regime- und Gate-Bericht

Der Bericht enthält mindestens:

- Build-, Modell- und Profilversionen,
- S4-, S5- und S6-Schema-IDs und Schema-Fingerprints,
- State-Schema-ID und State-Fingerprint,
- `semantic_build_configuration_sha256`,
- Reason-Code-Registry-Versionen,
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
2. das Eingangsschema exakt `rcc002.stage.s4-signals/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s5-regimes/1.0.0` erfüllt,
4. Regime- und Kontextprofile registriert sind,
5. Slope und Warm-up korrekt sind,
6. Rohregime-Wahrheitstabelle bestanden ist,
7. State-Machine-Tests bestanden sind,
8. `UNKNOWN` und `regime_valid` korrekt gebildet sind,
9. Kontextgültigkeit feldbezogen gebildet ist,
10. keine Lücke oder Segmentgrenze überbrückt wird,
11. State Snapshots `rcc002.state.s5-regimes/1.0.0` erfüllen,
12. S5-Reason Codes ausschließlich aus der registrierten Registry stammen,
13. serielle und partitionierte Berechnung übereinstimmen,
14. Zeilen, Primärschlüssel, Segmente und vorgelagerte Werte unverändert sind,
15. Manifest, State-Schema und Checksummen vollständig sind.

## 36. Publication Gate S6

S6 darf nur veröffentlicht werden, wenn:

1. S5 freigegeben ist,
2. das Eingangsschema exakt `rcc002.stage.s5-regimes/1.0.0` erfüllt,
3. das Ausgangsschema exakt `rcc002.stage.s6-gates/1.0.0` erfüllt,
4. Gate-Profil und Profilversion registriert sind,
5. Daten-Gate fail-closed und exakt nach Abschnitt 13 arbeitet,
6. Long-/Short-Wahrheitstabellen bestanden sind,
7. `gate_valid`, `gate_state` und Richtungs-Booleans konsistent sind,
8. profilabhängige Pflichtinputs korrekt angewandt wurden,
9. Reason Codes vollständig, richtungsgetrennt und deterministisch sind,
10. keine ungültige Zeile eine Richtung erlaubt,
11. Gate-Komposition eindeutig ist,
12. `gate_evaluated_at = close_time` gilt,
13. keine veralteten Aliasfelder enthalten sind,
14. serielle und partitionierte Berechnung übereinstimmen,
15. Zeilen, Primärschlüssel, Segmente und vorgelagerte Werte unverändert sind,
16. Manifest und Checksummen vollständig sind.

Der jeweilige Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder einen
Schema-, Enum-, State-, Gültigkeits-, Segment-, Reason-Code- oder
Reconciliation-Fehler noch eine unzulässige Richtungsfreigabe überstimmen.

## 37. Offene Implementierungsparameter

### 37.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständige maschinenlesbare S5- und S6-Schemas;
- vollständige S5- und S6-Feld-, Enum- und Reason-Code-Register;
- Modell-, Profil-, Schema-, State- und Komponentenregister;
- exakter S5-State-Snapshot-Vertrag einschließlich
  `sma200_context_state`;
- Profilabhängigkeiten jedes Gate-Profils;
- numerisches Determinismusprofil für Slope und Rolling State einschließlich
  Operationsreihenfolge, FMA-Regel, Parallelreduktion, Subnormalwerten und
  Nichtendlichkeitskonvertierung;
- gebundene numerisch wirksame Bibliotheken und Versionen;
- Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- S4→S5- und S5→S6-Reconciliation;
- Schema-Kompatibilitäts- und Migrationsregeln;
- Test- und Abnahmekriterien.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Zustände, Gültigkeit, Schema, Profile oder Reproduzierbarkeit
beeinflussen.

### 37.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer State Snapshots;
- technisch gleichwertige Speicherorte.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Regime- und Gatewerte noch Gültigkeit, Reason Codes, logische S5-/S6-
Schemas, `build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 38. Abnahmekriterien

### 38.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. alle S4-Eingangs-, S5-Ausgangs- und S6-Ausgangsfelder mit Typ,
   Nullsemantik, Eigentümerstufe und Reihenfolge festgelegt sind;
2. alle Regime-, Kontext- und Gate-Enums eindeutig registriert sind;
3. Roh- und Persistenzregime vollständig spezifiziert sind;
4. `UNKNOWN`, `INVALID`, `BLOCK_BOTH`, `regime_valid` und `gate_valid`
   widerspruchsfrei getrennt sind;
5. Trendstärke und Volatilität richtungsfrei bleiben;
6. alle Gate-Profile und ihre Pflichtinputs getrennt festgelegt sind;
7. State-, Profil-, Schema-, Modell-, Komponenten- und Registry-IDs
   versioniert sind;
8. semantische und physische Konfiguration getrennt sind;
9. Golden-, Unit-, Property-, Schema-, State-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
10. Counterfactual-Evaluationspipeline und Falsifikationskriterien
    spezifiziert sind;
11. Publication Gates und Manifestverträge vollständig sind;
12. Legacy- und Rekonstruktionsprofile strikt vom kanonischen Modell getrennt
    sind;
13. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
14. keine offene Entscheidung fachliche Zustände, Gültigkeit, logische
    Schemas oder Identitätsvorabbildungen verändern kann.

### 38.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. Roh- und Persistenzregime vollständig implementiert und getestet sind;
2. alle Gate-Profile getrennt testbar sind;
3. Daten-Gate und profilabhängige Invalidität fail-closed arbeiten;
4. State Snapshot und Partitionsparität bestanden sind;
5. S5-/S6-Schema-, Enum-, Gültigkeits- und Reason-Code-Tests bestanden sind;
6. Legacy-Reproduktion und GS-Rekonstruktionsstatus dokumentiert sind;
7. BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
8. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
9. keine Zeile und kein vorgelagertes Feld verändert wurde;
10. Manifest, Dataset Lineage und Knowledge Lineage vollständig sind;
11. keine offene kritische Regel-, State- oder Rolleninkonsistenz besteht;
12. die S5- und S6-Publication-Gates automatisiert bestanden sind.

## 39. Freigabe und Aktivierung

### 39.1 Spezifikationsfreigabe

Die technische Spezifikation eines Gate-Profils bedeutet nicht seine
Freigabe für Paper oder Live.

### 39.2 Forschungsstatus

Bis zum Abschluss der Counterfactual- und Out-of-Sample-Validierung gelten:

- `GATE_RESEARCH_OPEN_V1`: kanonische Forschungsbaseline,
- `GATE_TREND_ALIGNED_V1`: Forschungskandidat,
- `GATE_TREND_STRENGTH_ALIGNED_V1`: Forschungskandidat.

### 39.3 Produktive Aktivierung

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

## 40. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.5.0 bewahrt die AIR-001-Korrekturen aus Version 0.4.0 und
korrigiert zusätzlich:

- `SCR-005-B01` – vollständiger S5-/S6-Schlüssel mit `market_type` und
  `interval`, Multi-Provider-Regel sowie angeglichener State-Vertrag;
- `SCR-005-M01` – getrennte Stage- und State-Schema-IDs, Versionen und
  abgeleitete Referenzen;
- `SCR-005-M02` – einzige normative Wahrheitstabelle für
  `data_gate_pass`, `BLOCK_BOTH`, `INVALID` und Stage-Abbruch.

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
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending
```

Nächste vorgeschriebene Schritte:

1. übrige abhängige Spezifikationen korrigieren;
2. vollständige interne Qualitätskontrolle;
3. neues vollständiges Spezifikationspaket;
4. fokussierter Scientific Consistency Re-Review;
5. fokussierter Architecture Integrity Re-Review;
6. Editorial Pass;
7. Internal Certification;
8. Claude Independent Architecture Review;
9. Gemini Independent Scientific and Adversarial Audit;
10. ChatGPT Final Consolidation;
11. `Baseline V1 Certified`;
12. Implementierungsfreigabe.
