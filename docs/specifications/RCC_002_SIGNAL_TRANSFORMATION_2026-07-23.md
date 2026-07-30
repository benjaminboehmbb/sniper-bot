# RCC-002 Signal Transformation Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-ST |
| Titel | Signal Transformation Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Dateiname | `RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md` |
| Version | 0.4.2 |
| Datum | 2026-07-23 |
| Status | S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.8.0 |
| Direkte Abhängigkeiten | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.6.0; `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md`, Version 0.4.3 |
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
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B03`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 korrigiert `SCR-005-B01` und `SCR-005-M01`; SCR-006 ausstehend |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.1, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| AIR4-MIN-01 Correction | `RCC-002-AIR-004` Minor Finding behoben | Version 0.4.2, 2026-07-27: Clarified that PASS_WITH_APPROVED_EXCEPTIONS carve-outs are exhaustive and cannot be extended by approval alone. |
| S8 Blocker Correction | Abhängigkeiten nachgezogen | Normativer Inhalt unverändert; Abhängigkeiten auf Data Pipeline 0.8.0 und Data Validation 0.6.0 aktualisiert; Re-Review ausstehend. |

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

Ungültigkeit wird im logischen S4-Schema ausschließlich als `null` plus
feldbezogenes Validitätsfeld dargestellt.

Ein internes IEEE-754-`NaN` darf während einer Berechnung vorübergehend
verwendet werden. Vor Schema-Validierung, Fingerprinting oder Veröffentlichung
muss es jedoch in logisches `null` überführt werden. `NaN`, `+Inf` und `-Inf`
sind keine zulässigen gültigen oder veröffentlichten S4-Werte.

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

### 4.1 Kanonisches Gesamtprofil

Die erste kanonische S4-Baseline lautet:

```text
signal_profile_id=RCC002_CANONICAL_SIGNALS_V1
signal_profile_version=1.0.0
signal_schema_id=rcc002.stage.s4-signals
signal_schema_version=1.0.0
signal_schema_ref=rcc002.stage.s4-signals/1.0.0
```

`signal_schema_id` ist unversioniert. `signal_schema_ref` wird ausschließlich
als `<signal_schema_id>/<signal_schema_version>` abgeleitet.

Das Gesamtprofil erzeugt gemeinsam und atomar:

- die diskreten Felder aus `RCC_DISCRETE_V1`;
- die kontinuierlichen Felder aus `RCC_CONTINUOUS_V1`;
- für jedes erzeugte Feld die zugehörigen Begleitfelder;
- die fünf verbindlichen Profil- und Schemametadaten.

Ein kanonischer S4-Build darf nicht nur eine nicht ausgewiesene Teilmenge
dieses Gesamtprofils unter derselben Schema-ID veröffentlichen.

### 4.2 `RCC_DISCRETE_V1`

Erzeugt:

- diskrete Mean-Reversion-Signale,
- diskrete Momentum-/Volumen-Signale,
- diskrete Trendzustände,
- diskrete Volatilitäts- und Trendstärkezustände.

### 4.3 `RCC_CONTINUOUS_V1`

Erzeugt dimensionslose kontinuierliche Scores mit festen, versionierten
Transformationen.

Diese Scores sind Forschungsfeatures. Ihre Definition genehmigt weder ihre
Gewichtung noch ihre Verwendung in einer Strategie.

### 4.4 `LEGACY_BTC_BINARY_V1`

Reproduziert die zwölf historisch verifizierten 0/1-Signalspalten.

Das Profil ist ausschließlich für:

- Reproduktion,
- Vergleich,
- Knowledge Lineage

zulässig.

Das Legacy-Profil gehört nicht zum kanonischen S4-Ausgangsschema. Es wird als
separates Vergleichsartefakt mit eigener Schema-ID veröffentlicht:

```text
rcc002.comparison.s4-legacy-btc-binary/1.0.0
```

### 4.5 Profilkombination

Ein Build MAY mehrere Profile parallel berechnen, wenn:

- Feldnamen eindeutig sind,
- jede Spalte eine Profil-ID trägt oder über das Schema zugeordnet ist,
- kein Profil ein anderes überschreibt,
- das Manifest alle aktiven Profile aufführt;
- kanonische S4-Ausgabe und Legacy-Vergleichsartefakt getrennte
  Schema- und Artefaktidentitäten besitzen.

Das kanonische S4-Artefakt enthält ausschließlich das kanonische
Gesamtprofil. Ein Legacy-Artefakt darf nicht unter
`rcc002.stage.s4-signals/1.0.0` veröffentlicht werden.

Diskrete und kontinuierliche Profile sind parallele Repräsentationen. Ein
diskretes Feld darf nicht nachträglich aus dem Vorzeichen seines
kontinuierlichen Gegenstücks abgeleitet werden. Insbesondere können strikte
diskrete Grenzwerte an einem exakten Schwellenwert neutral sein, während der
kontinuierliche Score dort bereits einen definierten Ankerwert erreicht.

## 5. Eingabevertrag

### 5.1 Akzeptiertes Eingangsschema

S4 akzeptiert für die erste Baseline ausschließlich:

```text
rcc002.stage.s3-indicators/1.0.0
```

Eine unbekannte Major-Version wird fail-closed abgelehnt. Eine neuere
Minor-Version darf nur aufgrund einer registrierten S4-Kompatibilitätsregel
akzeptiert werden.

### 5.2 Pflichtfelder aus S3

S4 verwendet:

- `market_type`;
- `symbol`;
- `interval`;
- `open_time`;
- `market_segment_id`;
- `indicator_segment_id`;
- `quality_gate_pass`;
- `close`;
- `volume`;
- `sma_close_200`;
- `ema_close_50`;
- `rsi_wilder_14`;
- `macd_hist_12_26_9`;
- `bb_mid_20`;
- `bb_upper_20_2`;
- `bb_lower_20_2`;
- `stoch_k_14`;
- `atr_wilder_14`;
- `roc_close_12_pct`;
- `obv`;
- `cci_20`;
- `mfi_14`;
- `adx_wilder_14`;
- zu jedem verwendeten Indikator `x` die S3-Begleitfelder
  `x_valid`, `x_warmup_complete` und `x_reason_codes`.

Zusätzlich berechnet S4 kausal:

- SMA 200 des gültigen ATR innerhalb desselben Segments,
- SMA 50 des gültigen OBV innerhalb desselben Segments,
- Summe des Volumens über 50 gültige Kerzen.

Diese S4-Hilfsgrößen sind Teil des Signalprofils und keine nachträgliche
Änderung der S3-Indikatorformeln.

### 5.3 Eingabeinvarianten

S4 MUST:

- ausschließlich freigegebene S3-Artefakte konsumieren,
- `signal_profile_id` aus der semantischen Buildkonfiguration bestimmen,
- S3-Schema-, Indikatorprofil-, Segmentprofil- und numerische Profilversion
  prüfen,
- den kanonischen Schlüssel unverändert erhalten,
- die Sortierung `(market_type, symbol, interval, open_time)` unverändert
  erhalten,
- `market_segment_id` und `indicator_segment_id` unverändert durchreichen,
- Segmentgrenzen respektieren,
- keine ungültigen S3-Werte transformieren,
- `quality_gate_pass=false` als blockierenden Eingangsstatus behandeln.

S4 darf keine neue Markt- oder Indikatorsegment-ID erzeugen. Ein zusätzlicher
Rolling-Warm-up in S4 verändert weder `market_segment_id` noch
`indicator_segment_id`; er wirkt ausschließlich auf die feldbezogene
S4-Gültigkeit.

### 5.4 Primärschlüssel und Zeilenreihenfolge

Der logische Primärschlüssel bleibt:

```text
(market_type, symbol, interval, open_time)
```

Die kanonische Sortierung bleibt:

```text
market_type ASC, symbol ASC, interval ASC, open_time ASC
```

Wenn S3 noch nicht konsolidierte Multi-Provider-Daten enthält, MUSS
`provider` als zusätzlicher registrierter Schlüsselbestandteil unmittelbar
vor `market_type` geführt werden. Nach dokumentierter Providerkonsolidierung
entfällt `provider` aus dem Schlüssel, bleibt aber als Provenienzfeld erhalten.

`timeframe` ist kein Aliasfeld des kanonischen S4-Schemas. Ein historischer
Eingang mit `timeframe` MUSS vor S3 durch ein versioniertes Migrationsprofil
nach `interval` überführt werden; S4 selbst darf keine stille Umbenennung
vornehmen.

Duplikate, Schlüsseländerungen oder eine Änderung der semantischen
Zeilenreihenfolge sind blockierende Fehler.

### 5.5 Eingangsablehnung

S4 bricht vor einer fachlichen Transformation ab, wenn mindestens eine der
folgenden Bedingungen erfüllt ist:

- inkompatible oder unbekannte S3-Schema-ID;
- fehlendes Pflichtfeld;
- nicht registrierter Datentyp oder nicht registrierte Nullbarkeit;
- ungültiger Primärschlüssel;
- nichtkanonische Sortierung;
- fehlende S3-Profilmetadaten;
- unbekannte Reason-Code-Registry;
- widersprüchliche S3-Begleitfelder;
- nicht veröffentlichter oder nicht bestandener S3-Publication-Status.

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
- ausschließlich Werte mit `quality_gate_pass=true`,
- ausschließlich erforderliche Eingaben mit `x_valid=true`,
- keine synthetischen oder ungültigen Inputs im kanonischen Profil.

Ein Fenster darf weder eine `market_segment_id`- noch eine
`indicator_segment_id`-Grenze überschreiten.

### 6.5 Auswertungsreihenfolge

Für jedes S4-Feld gilt:

1. Schema- und Profilverträglichkeit prüfen;
2. erforderliche S3-Begleitfelder prüfen;
3. zusätzlichen S4-Warm-up prüfen;
4. Sonder- und Nullnennerfall prüfen;
5. ungerundete Transformation berechnen;
6. gegebenenfalls clippen;
7. Endlichkeit und Wertebereich prüfen;
8. Wert, `y_valid` und `y_reason_codes` gemeinsam serialisieren.

Eine spätere Prüfung darf einen zuvor festgestellten invalidierenden Grund
nicht verdecken.

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

### 7.4 Kanonische S4-Feld- und Begleitfeld-Allowlist

Das kanonische S4-Ausgangsschema enthält alle S3-Felder unverändert und genau
die in diesem Abschnitt registrierten S4-Felder.

Für jedes der folgenden 24 Basisfelder `y` erzeugt S4 genau:

```text
y
y_valid
y_reason_codes
```

#### 7.4.1 Diskrete Basisfelder

| Feld | Logischer Typ | Nullbar | Rolle | Eigentümer |
|---|---|---:|---|---|
| `sig_rsi_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_macd_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_bollinger_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_stoch_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_cci_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_mfi_mr_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_obv_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `sig_roc_momentum_d` | `Int8` | ja | `DIRECTION_DISCRETE` | `S4_SIGNALS` |
| `state_ma200_trend_d` | `Int8` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `state_ema50_trend_d` | `Int8` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `state_atr_relative_d` | `Int8` | ja | `VOLATILITY_STATE` | `S4_SIGNALS` |
| `state_adx_strength_d` | `Int8` | ja | `TREND_STRENGTH` | `S4_SIGNALS` |

`state_adx_strength_d` verwendet trotz seines `Int8`-Typs ausschließlich
`{0,1}`. Alle übrigen diskreten Felder verwenden ausschließlich
`{-1,0,+1}`.

#### 7.4.2 Kontinuierliche Basisfelder

| Feld | Logischer Typ | Nullbar | Rolle | Eigentümer |
|---|---|---:|---|---|
| `score_rsi_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_macd_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_bollinger_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_stoch_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_cci_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_mfi_mr_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_obv_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_roc_momentum_c` | `Float64` | ja | `DIRECTION_SCORE` | `S4_SIGNALS` |
| `score_ma200_trend_c` | `Float64` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `score_ema50_trend_c` | `Float64` | ja | `TREND_STATE` | `S4_SIGNALS` |
| `score_atr_relative_c` | `Float64` | ja | `VOLATILITY_STATE` | `S4_SIGNALS` |
| `score_adx_strength_c` | `Float64` | ja | `TREND_STRENGTH` | `S4_SIGNALS` |

#### 7.4.3 Begleitfelder

Für jedes registrierte Basisfeld `y` gilt:

| Feldmuster | Logischer Typ | Nullbar | Eigentümer | Semantik |
|---|---|---:|---|---|
| `y_valid` | `Boolean` | nein | `S4_SIGNALS` | fachliche Verwendbarkeit von `y` |
| `y_reason_codes` | geordnete Liste `Utf8` | nein | `S4_SIGNALS` | deterministische Gründe und Hinweise |

Eine leere Reason-Code-Liste wird als leere Liste, nicht als `null`,
serialisiert.

### 7.5 S4-Metadaten

S4 erzeugt einmal je Zeile folgende nicht nullbaren Metadaten:

| Feld | Logischer Typ | Normativer Wert |
|---|---|---|
| `signal_profile_id` | `Utf8` | `RCC002_CANONICAL_SIGNALS_V1` |
| `signal_profile_version` | `Utf8` | `1.0.0` |
| `signal_schema_id` | `Utf8` | `rcc002.stage.s4-signals` |
| `signal_schema_version` | `Utf8` | `1.0.0` |
| `signal_schema_ref` | `Utf8` | `rcc002.stage.s4-signals/1.0.0` |

Der vollständig qualifizierte Ausgangsschemabezeichner lautet:

```text
rcc002.stage.s4-signals/1.0.0
```

### 7.6 Kanonische Feldreihenfolge

Die kanonische Reihenfolge lautet:

1. alle Felder von `rcc002.stage.s3-indicators/1.0.0` in unveränderter
   S3-Reihenfolge;
2. `signal_profile_id`;
3. `signal_profile_version`;
4. `signal_schema_id`;
5. `signal_schema_version`;
6. die 24 Basisfelder in der Reihenfolge aus den Abschnitten 7.4.1 und 7.4.2;
7. unmittelbar nach jedem Basisfeld `y` die Felder `y_valid` und
   `y_reason_codes`.

Nicht registrierte Zusatzfelder, Legacy-Felder oder alternative
Begleitfeldnamen machen das Artefakt nicht kanonisch.

### 7.7 Schema-Fingerprint

Der S4-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen;
- Nullbarkeit;
- Feldrollen;
- Eigentümerstufen;
- Primärschlüssel und Sortierung;
- Schema-ID und Schemaversion;
- Profil-ID und Profilversion;
- Reason-Code-Register und dessen Version;
- Wertebereiche und Nullsemantik;
- Kompatibilitätsregeln.

### 7.8 Kompatibilitäts- und Migrationsregeln

Für `rcc002.stage.s4-signals` gilt semantische Versionierung:

- Patch: ausschließlich redaktionelle oder nichtsemantische Metadatenkorrektur;
- Minor: additive optionale Felder ohne Änderung bestehender Semantik;
- Major: Entfernung, Umbenennung, Typänderung, Rollenänderung, neue
  Nullsemantik, Schlüsseländerung oder fachliche Bedeutungsänderung.

Eine neue Minor-Version wird nur akzeptiert, wenn der Konsument sie in einer
registrierten Kompatibilitätsregel freigibt. Unbekannte Major-Versionen sind
fail-closed abzulehnen.

Historische Namen wie `rsi_signal`, `macd_signal`, `atr_signal` oder
`adx_signal` sind keine kanonischen Aliase. Ihre Semantik ist
profilabhängig und darf nicht durch bloße Umbenennung migriert werden.

### 7.9 Verbotene S4-Ausgaben

S4 darf insbesondere keine der folgenden fachlichen Ausgaben erzeugen:

- `market_regime`;
- `regime_state`;
- `regime_raw_state`;
- `regime_persisted_state`;
- `allow_long`;
- `allow_short`;
- `data_gate_pass`;
- `gate_state`;
- `gate_valid`;
- Forward Returns;
- Labels;
- Strategieentscheidungen.

Regime entstehen ausschließlich in S5, Handels-Gates ausschließlich in S6
und Zukunftsinformation ausschließlich in S7. Damit bleibt der korrigierte
S5-/S6-Vertrag aus `AIR-001-B03` frei von konkurrierenden S4-Ausgaben.

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

### 23.1 Verbindliches Validitätsprofil

Das Validitätsprofil lautet:

```text
signal_validity_profile_id=RCC002_SIGNAL_VALIDITY_V1
signal_validity_profile_version=1.0.0
signal_reason_code_registry_version=1.0.0
```

### 23.2 Wahrheitsregel

Für jedes Basisfeld `y` gilt:

```text
y_valid =
    schema_compatible
    AND profile_compatible
    AND quality_gate_pass
    AND all_required_s3_inputs_valid
    AND additional_s4_warmup_complete
    AND denominator_or_defined_null_case_valid
    AND result_is_finite
    AND result_in_registered_range
```

Wenn `y_valid=false`, muss `y=null` sein.

Wenn `y_valid=true`, muss:

- `y` nicht null;
- `y` endlich;
- `y` im registrierten Wertebereich;
- `y_reason_codes` frei von invalidierenden Codes

sein.

Ein definierter mathematischer Nullfall mit explizitem gültigem Ergebnis, etwa
MACD-Histogramm null bei ATR null, ist gültig und erhält den jeweils
definierten Wert. Ein nicht definierter oder widersprüchlicher Nullfall ist
ungültig.

### 23.3 Pflichtfelder

S4 MUST je Transformation ausweisen:

- `y`;
- `y_valid`;
- `y_reason_codes`;
- Profil-ID und Profilversion über die verbindlichen S4-Metadaten;
- Signalrolle über das versionierte Feldregister.

### 23.4 Verbindliches Reason-Code-Register

| Priorität | Code | Invalidierend | Bedeutung |
|---:|---|---:|---|
| 10 | `SIG_SCHEMA_MISMATCH` | ja | S3- oder S4-Schema inkompatibel |
| 20 | `SIG_PROFILE_MISMATCH` | ja | Profil-ID oder Profilversion inkompatibel |
| 30 | `SIG_INPUT_QUALITY_GATE_FAILED` | ja | `quality_gate_pass=false` |
| 40 | `SIG_INPUT_INVALID` | ja | mindestens ein erforderliches S3-Feld ungültig |
| 50 | `SIG_WARMUP_INCOMPLETE` | ja | zusätzliches S4-Fenster unvollständig |
| 60 | `SIG_WINDOW_CROSSES_INDICATOR_SEGMENT` | ja | Fenster würde eine Segmentgrenze überschreiten |
| 70 | `SIG_MACD_ZERO_ATR_CONFLICT` | ja | MACD ungleich null bei ATR null |
| 80 | `SIG_BB_ZERO_WIDTH_CONFLICT` | ja | Close weicht bei Bandbreite null von BB-Mid ab |
| 90 | `SIG_OBV_ZERO_VOLUME_CONFLICT` | ja | OBV-Abweichung bei Volumensumme null |
| 100 | `SIG_ROC_ZERO_ATR_CONFLICT` | ja | ROC ungleich null bei ATR-Quote null |
| 110 | `SIG_MA200_ZERO_ATR_CONFLICT` | ja | MA200-Abstand ungleich null bei ATR null |
| 120 | `SIG_EMA50_ZERO_ATR_CONFLICT` | ja | EMA50-Abstand ungleich null bei ATR null |
| 130 | `SIG_ATR_RATIO_ZERO_CONFLICT` | ja | positive aktuelle ATR bei ATR-Referenz null |
| 140 | `SIG_NONFINITE_RESULT` | ja | Ergebnis ist `NaN` oder unendlich |
| 150 | `SIG_RANGE_INVARIANT_FAILED` | ja | Ergebnis verletzt registrierten Wertebereich |

Die Priorität ist Bestandteil der Registry-Version.

### 23.5 Deterministische Reihenfolge und Serialisierung

`y_reason_codes` ist:

- eine geordnete Liste;
- frei von Duplikaten;
- nach aufsteigender Registry-Priorität sortiert;
- bei fehlenden Codes eine leere Liste;
- niemals `null`.

Unbekannte Codes sind unter Registry-Version `1.0.0` unzulässig.

Eine Implementierung darf mehrere zutreffende Codes sammeln. Sie darf jedoch
keinen Folgecode berechnen, dessen Prüfung selbst einen ungültigen
Zwischenwert auswerten würde. Beispielsweise wird nach einem fehlenden
Eingangswert kein arithmetischer Nichtendlichkeitsfehler künstlich erzeugt.

### 23.6 Propagation

Ist ein erforderlicher S3-Indikator ungültig, ist die abhängige
S4-Transformation ebenfalls ungültig.

Ein nachgelagerter gültiger numerischer Ausdruck darf einen ungültigen
Inputstatus nicht verdecken.

Nicht invalidierende S3-Hinweiscodes bleiben in ihren S3-Begleitfeldern
unverändert erhalten. S4 kopiert sie nicht und erfindet keine
gleichnamigen S4-Codes.

### 23.7 Feldbezogene Eingangsabhängigkeiten

Die Gültigkeit eines S4-Feldes hängt ausschließlich von seinen registrierten
Eingängen ab. Ein ungültiger, aber fachlich nicht benötigter S3-Indikator darf
ein anderes S4-Feld nicht global invalidieren.

Beispiele:

- ungültiger MFI invalidiert keine RSI-Transformation;
- ungültiger ATR invalidiert den diskreten MACD-Wert nicht, wohl aber den
  kontinuierlichen MACD-Score;
- unvollständiger ATR-SMA-200-Warm-up invalidiert nur
  `state_atr_relative_d` und `score_atr_relative_c`.

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

### 28.1 Erzeugtes Ausgangsschema

S4 erzeugt ausschließlich:

```text
rcc002.stage.s4-signals/1.0.0
```

Das Ausgangsschema besteht aus:

1. allen S3-Feldern unverändert;
2. den vier S4-Metadaten aus Abschnitt 7.5;
3. den 24 S4-Basisfeldern aus Abschnitt 7.4;
4. genau zwei Begleitfeldern je S4-Basisfeld.

Rollenregister, Reason-Code-Register, Transformationsbericht und
Output-Checksumme sind registrierte Begleitartefakte oder Manifestinhalte.
Sie werden nicht als unstrukturierte Tabellenfelder wiederholt.

### 28.2 Zeileninvariante

S4 darf:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keine S0-bis-S3-Werte verändern.

Es muss gelten:

`S4_rows = S3_rows`

und alle kanonischen Schlüssel müssen unverändert bleiben. Dies
konkretisiert für S4 das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

Zusätzlich muss die zeilenweise Reconciliation für jedes durchgereichte
S3-Feld semantische Gleichheit bestätigen.

### 28.3 Typen und Nullbarkeit

Die logischen Typen und Nullbarkeiten sind ausschließlich jene aus Abschnitt
7.4:

- diskrete Basisfelder: nullable `Int8`;
- kontinuierliche Basisfelder: nullable `Float64`;
- `y_valid`: nicht nullbares `Boolean`;
- `y_reason_codes`: nicht nullbare geordnete Liste `Utf8`;
- S4-Metadaten: nicht nullbares `Utf8`.

Alternative physische Typen sind nur zulässig, wenn sie das registrierte
logische Schema verlustfrei und deterministisch repräsentieren.

### 28.4 Segment- und Gültigkeitsinvariante

S4 muss `market_segment_id` und `indicator_segment_id` byte- beziehungsweise
zeichenidentisch durchreichen.

Es gilt:

```text
S4.market_segment_id = S3.market_segment_id
S4.indicator_segment_id = S3.indicator_segment_id
```

Ein S4-Feld darf in einem zusätzlichen Warm-up-Bereich ungültig sein, ohne
einen neuen Segmentbezeichner zu erzeugen.

### 28.5 Komponentenidentität

Die normative Komponentenidentität lautet:

```text
component_id=RCC002_S4_SIGNAL_TRANSFORMER
component_version=0.3.0
```

Die Implementierung manifestiert zusätzlich:

- Source-Tree- oder Commit-Identität;
- `semantic_build_configuration_sha256`;
- numerisches Profil;
- Eingabe- und Ausgangsschema-Fingerprint;
- Profil- und Registry-Versionen.

### 28.6 Fehlerverhalten

Ein stageweiter Schema-, Profil-, Schlüssel- oder Sortierungsfehler bricht S4
fail-closed ab.

Ein feldbezogener mathematischer oder Warm-up-Fehler invalidiert nur die
registrierten abhängigen S4-Felder, sofern das Eingangsschema als Ganzes
gültig bleibt.

### 28.7 Keine implizite S5-/S6-Erweiterung

S5 konsumiert `rcc002.stage.s4-signals/1.0.0`. S4 darf deshalb weder
Regimezustände vorwegnehmen noch Felder mit S5- oder S6-Eigentum erzeugen.

Die genaue S5-/S6-Zustands- und Gate-Semantik wird ausschließlich in der
Regime- und Gate-Spezifikation festgelegt. Ein später geändertes S5- oder
S6-Schema verändert nicht automatisch den S4-Vertrag.

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

### 29.8 Schema- und Vertragsprüfung

Mindestens erforderlich sind:

- Annahme von `rcc002.stage.s3-indicators/1.0.0`;
- Ablehnung unbekannter S3- oder S4-Major-Versionen;
- exakte S4-Spaltenallowlist und Spaltenreihenfolge;
- exakte logische Typen und Nullbarkeit;
- unveränderte S3-Felder und Primärschlüssel;
- `S4_rows = S3_rows`;
- unveränderte `market_segment_id`;
- unveränderte `indicator_segment_id`;
- vollständige vier S4-Metadaten;
- exakt zwei Begleitfelder je Basisfeld;
- keine Legacy-, S5-, S6- oder S7-Felder im kanonischen S4-Artefakt;
- Ablehnung unbekannter Reason Codes;
- deterministische Reason-Code-Reihenfolge.

### 29.9 Validitäts- und Nulltests

Für jedes S4-Basisfeld sind zu testen:

- gültiger Minimalfall;
- ungültiger erforderlicher S3-Input;
- irrelevanter ungültiger S3-Input;
- `quality_gate_pass=false`;
- unvollständiger zusätzlicher S4-Warm-up;
- Segmentgrenze innerhalb eines potenziellen Fensters;
- definierter Nullnennerfall;
- widersprüchlicher Nullnennerfall;
- nicht endliches Zwischenergebnis;
- Wertebereichsverletzung;
- `y=null` genau dann, wenn `y_valid=false`;
- leere statt nuller Reason-Code-Liste bei gültigem Standardfall.

### 29.10 Property-Based Tests

SHOULD geprüft werden:

- spätere Eingangswerte verändern kein früheres S4-Feld;
- zusätzliche physische Partitionierung verändert keine S4-Semantik;
- jedes gültige Basisfeld ist endlich und liegt im registrierten Bereich;
- jedes ungültige Basisfeld ist logisch `null`;
- kein invalidierender Reason Code tritt bei `y_valid=true` auf;
- kein Basisfeld besitzt ein nullbares `y_valid` oder `y_reason_codes`;
- kein Rolling Window überschreitet eine Indikatorsegmentgrenze;
- Mean-Reversion-Transformationen besitzen die dokumentierte Monotonie;
- Trendstärke und Volatilität werden nicht als Richtung umgedeutet.

## 30. Numerische Toleranzen

Das normative numerische Profil lautet:

```text
signal_numeric_profile_id=RCC002_FLOAT64_SIGNAL_NUMERICS_V1
signal_numeric_profile_version=1.0.0
```

Für unabhängige `float64`-Vergleiche gelten standardmäßig:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Diskrete Entscheidungen werden aus ungerundeten Werten gebildet.

Ein Wert innerhalb numerischer Vergleichstoleranz zur Schwelle wird nicht
automatisch als gleich behandelt. Falls eine Schwellen-Hysterese erforderlich
ist, muss sie separat spezifiziert und versioniert werden.

### 30.1 Vergleichsregel

Für unabhängige Implementierungen gilt komponentenweise:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Logische Nullwerte werden nur positionsgleich mit logischen Nullwerten
verglichen. Diskrete Basisfelder, Validitätsfelder, Reason Codes, Profilfelder
und Schemafelder müssen exakt übereinstimmen.

### 30.2 Operations- und Determinismusgrenzen

Vor `Approved for Implementation` müssen versioniert festgelegt sein:

- Reihenfolge nicht assoziativer Float-Operationen;
- zulässige oder deaktivierte FMA-Nutzung;
- Parallelreduktionsregeln für Rolling-Fenster;
- Behandlung von Subnormalwerten;
- Konvertierung interner `NaN`- und Inf-Werte;
- Referenzimplementierung der Golden Fixtures;
- numerisch wirksame Bibliotheken und Versionen.

Eine Änderung dieser Regeln verändert mindestens das numerische Profil und
erfordert erneute Golden-, Kausalitäts- und Partitionsparitätstests.

## 31. Transformationsbericht

Der Bericht enthält mindestens:

- Build-, Profil- und Schemaversion,
- Eingabe- und Ausgangsschema-ID,
- S3- und S4-Schema-Fingerprint,
- `semantic_build_configuration_sha256`,
- Signal-, Validitäts- und numerisches Profil,
- Reason-Code-Registry-Version,
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
12. das S4-Schema exakt `rcc002.stage.s4-signals/1.0.0` erfüllt,
13. jedes Basisfeld exakt seine beiden Begleitfelder besitzt,
14. Reason Codes ausschließlich aus Registry-Version `1.0.0` stammen,
15. `market_segment_id` und `indicator_segment_id` unverändert sind,
16. keine S5-, S6- oder S7-Felder enthalten sind,
17. Manifest, Rollenregister und Checksummen vollständig sind,
18. Property-Tests bestanden sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder
Schemafehler noch falsche Feldwerte, unzulässige Nullwerte, Segmentfehler,
nicht endliche gültige Werte, Rollenverletzungen oder eine fehlgeschlagene
Reconciliation überstimmen.

Die in diesem Abschnitt aufgeführten Ausnahmefälle für
`PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht
aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne
zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen
Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine
menschliche Genehmigung allein erweitert nicht den normativen
Ausnahmeumfang.

## 33. Offene Implementierungsparameter

### 33.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständiges maschinenlesbares S4-Schema;
- vollständiges Signalrollen- und Reason-Code-Register;
- kanonische Profil- und Komponentenregister;
- vollständige Eingangsabhängigkeit je S4-Feld;
- logische Typen, Nullbarkeit und Feldreihenfolge;
- Schema-Fingerprinting- und Kompatibilitätsregeln;
- numerisches Determinismusprofil;
- gebundene numerisch wirksame Bibliotheken und Versionen;
- feldbezogene Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- S3→S4-Reconciliation;
- Test- und Abnahmekriterien.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Werte, Gültigkeit, Schema, Profile oder Reproduzierbarkeit
beeinflussen.

### 33.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer Zwischenartefakte;
- technisch gleichwertige Speicherorte.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Signalwerte noch Gültigkeit, Reason Codes, logisches S4-Schema,
`build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 34. Abnahmekriterien

### 34.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. alle logischen S3-Eingangs- und S4-Ausgangsfelder mit Typ, Nullsemantik,
   Eigentümerstufe und Reihenfolge festgelegt sind;
2. jede Transformation eine feste Profil- und Feldversion besitzt;
3. alle Formeln, Grenzwerte, Gleichheits-, Warm-up- und Nullfälle eindeutig
   sind;
4. `y_valid` und `y_reason_codes` maschinenlesbar definiert sind;
5. Rollen-Sicherheit und S5-/S6-Abgrenzung vollständig spezifiziert sind;
6. Schema-, Profil-, Registry-, Komponenten- und numerische IDs versioniert
   sind;
7. semantische und physische Konfiguration getrennt sind;
8. Golden-, Unit-, Property-, Schema-, Rollen-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
9. Publication Gate und Manifestvertrag vollständig sind;
10. kanonisches und Legacy-Profil strikt getrennt sind;
11. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
12. keine offene Entscheidung fachliche Werte, Gültigkeit, logisches Schema
    oder Identitätsvorabbildungen verändern kann.

### 34.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Transformationen als eigenständige Funktionen testbar sind;
2. Grenzwert-, Ankerwert-, Nullfall- und Golden-Tests bestanden sind;
3. Rollen-Sicherheit technisch erzwungen wird;
4. Legacy-Reproduktion bestanden ist;
5. Schema-, Segment-, Kausalitäts- und Partitionsparität bestanden sind;
6. der BTCUSDT-1m-Vollbuild auf der Workstation erfolgreich ist;
7. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
8. keine Zeile und kein S3-Feld verändert wurde;
9. Manifest und Knowledge Lineage vollständig sind;
10. keine ungeklärten Regel-, Vorzeichen- oder Schnittstellenkonflikte
    bestehen;
11. das S4-Publication-Gate automatisiert bestanden ist.

## 35. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die AIR-001-Korrekturen aus Version 0.3.0 und
korrigiert zusätzlich:

- `SCR-005-B01` – vollständiger Schlüssel
  `(market_type, symbol, interval, open_time)`, Multi-Provider-Regel und
  Ausschluss von `timeframe`;
- `SCR-005-M01` – getrennte S4-Schema-ID, Schemaversion und abgeleitete
  Schemareferenz.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
Version 0.4.0

RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md
Version 0.4.0
```

Die Befunde sind erst geschlossen, wenn alle abhängigen Spezifikationen
konsistent aktualisiert, neu paketiert und erneut geprüft sind.

Der aktuelle Status lautet:

```text
S8BCP-001 Revision 2 Corrected Candidate – Re-Review Pending
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
