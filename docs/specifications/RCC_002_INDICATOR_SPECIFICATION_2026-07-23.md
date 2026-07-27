# RCC-002 Indicator Specification

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Scientific Software Specification |
| Dokument-ID | RCC-002-IS |
| Titel | Indicator Specification |
| Speicherort im Repository | `docs/specifications/RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Dateiname | `RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md` |
| Version | 0.4.3 |
| Datum | 2026-07-23 |
| Status | SCR-005-Corrected Draft – Scientific Consistency Re-Review 006 Pending |
| Übergeordnetes Dokument | `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`, Version 0.7.1 |
| Direkte Abhängigkeit | `RCC_002_DATA_VALIDATION_2026-07-23.md`, Version 0.5.0 |
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
| Scientific Consistency Review | `RCC-002-SCR-004` bestanden | Die dort geprüften wissenschaftlichen Befunde sind geschlossen; erneuter fokussierter Review nach den semantisch relevanten AIR-001-Korrekturen erforderlich |
| Architecture Integrity Review | `RCC-002-AIR-001` nicht bestanden; Korrektur eingearbeitet | Version 0.3.0 korrigiert die diesem Dokument zugeordneten Teile von `AIR-001-B01`, `AIR-001-M01` und `AIR-001-M03`; dokumentübergreifender Re-Review ausstehend |
| Scientific Consistency Re-Review 005 | `RCC-002-SCR-005` nicht bestanden; Korrektur eingearbeitet | Version 0.4.0 vereinheitlicht die Schemaidentität gemäß `SCR-005-M01`; SCR-006 ausstehend |
| C1 Patch Release | `RCC-002-C1-SCR` bestanden mit Minor Findings | Version 0.4.1: patch release: normative clarification of Canonical Row Preservation semantics (C1) in §4.3 und §30 Kriterium 2. No intended behavioural change. |
| Minor Correction Cycle | `RCC-002-SCR-007-MinFV` umgesetzt | Version 0.4.2, 2026-07-27: Minor correction cycle: version, dependency, terminology, checklist and cross-reference consistency corrections. |
| AIR4-MIN-01 Correction | `RCC-002-AIR-004` Minor Finding behoben | Version 0.4.3, 2026-07-27: Clarified that PASS_WITH_APPROVED_EXCEPTIONS carve-outs are exhaustive and cannot be extended by approval alone. |

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

Kanonische Berechnungen und persistierte numerische Indikatorfelder MUST
IEEE-754 Binary64 (`float64`) gemäß dem registrierten numerischen Profil
verwenden.

Zwischenergebnisse dürfen:

- nicht auf Anzeigepräzision gerundet,
- nicht in `float32` herabgestuft,
- nicht durch formatierte Textwerte ersetzt,
- nicht ohne eigenes numerisches Profil in höherer Präzision berechnet und
  anschließend zurückkonvertiert

werden.

Rundung ist nur in nichtkanonischen Berichten zulässig.

### 3.5 Ungültiger Wert

Ein noch nicht berechenbarer oder qualitätsbedingt ungültiger Indikatorwert
wird im logischen S3-Schema als `null` gespeichert und durch sein separates
Validitätsfeld ausgewiesen.

Eine Implementierung darf während der Berechnung intern IEEE-754 `NaN`
verwenden, muss diesen Zustand vor der kanonischen Serialisierung jedoch
deterministisch in logisches `null` überführen. Unendliche Werte sind weder
intern als gültiges Ergebnis noch im kanonischen Ausgang zulässig.

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

### 4.1 Eingabeschema

S3 akzeptiert ausschließlich:

```text
rcc002.stage.s2-validated/1.0.0
```

und erzeugt:

```text
rcc002.stage.s3-indicators/1.0.0
```

Unbekannte Major-Versionen werden fail-closed abgelehnt. Additive optionale
Felder einer neueren Minor-Version dürfen nur bei einer registrierten
Kompatibilitätsregel übernommen werden.

### 4.2 Pflichtfelder

S3 benötigt:

- `source_snapshot_id`,
- `source_row_id`,
- `provider`,
- `market_type`,
- `symbol`,
- `interval`,
- `open_time`,
- `close_time`,
- `open`,
- `high`,
- `low`,
- `close`,
- `volume`,
- `market_segment_id`,
- `quality_is_observed`,
- `quality_is_synthetic`,
- `quality_has_source_conflict`,
- `quality_gap_before`,
- `quality_gap_after`,
- `quality_timestamp_valid`,
- `quality_ohlc_valid`,
- `quality_volume_valid`,
- `quality_market_values_valid`,
- `quality_status`,
- `quality_reason_codes`,
- `quality_rule_version`,
- `quality_gate_pass`.

Sämtliche S2-Felder werden mit identischem Namen, logischem Typ,
Nullverhalten und Wert unverändert in S3 weitergeführt.

### 4.3 Eingabeinvarianten

Vor S3 MUST gelten:

- Zeitindex streng aufsteigend,
- Primärschlüssel eindeutig,
- kanonischer Schlüssel
  `(market_type, symbol, interval, open_time)` vollständig,
- bei unkonsolidierten Multi-Provider-Daten zusätzlich `provider`
  unmittelbar vor `market_type` im Schlüssel und in der Sortierreihenfolge,
- OHLCV-Invarianten bestanden,
- keine nicht endlichen Pflichtwerte,
- sämtliche S2-Qualitätsfelder vorhanden und nicht null,
- `quality_gate_pass` deterministisch nach der Data Validation Specification
  berechnet,
- Schema-ID und Schema-Fingerprint freigegeben.

S3 darf eine unvalidierte Rohdatei nicht direkt konsumieren.

Jede S2-Eingabezeile muss einen gültigen und deterministisch nach der Data
Validation Specification berechneten booleschen `quality_gate_pass`-Wert
besitzen. Zeilen mit `quality_gate_pass=false` bleiben Teil des
kanonischen Datenstroms und des kanonischen S3-Artefakts; für sie werden
keine gültigen Indikatorwerte erzeugt und keine Indikatorwerte als gültig
veröffentlicht. Row Identity, Zeilenreihenfolge und `S3_rows = S2_rows`
bleiben davon unberührt. Diagnoseberechnungen dürfen zusätzliche
Informationen erzeugen, dürfen aber die kanonische
Row-Preservation-Semantik nicht verändern.

### 4.4 Synthetische Kerzen

Kanonische Indikatoren werden standardmäßig ausschließlich auf beobachteten
Kerzen berechnet.

Indikatoren auf einer synthetischen Kontinuitätsansicht benötigen:

- eigene Build- und View-ID,
- eigene Indikatorprofil-ID,
- explizite Kennzeichnung,
- getrennte Sensitivitätsanalyse.

Sie dürfen kanonische beobachtete Indikatoren nicht überschreiben.

### 4.5 Schlüssel, Sortierung und Zeileninvariante

S3 übernimmt den vollständigen S2-Primärschlüssel und dessen aufsteigende
Sortierung unverändert.

Es muss gelten:

```text
S3_rows = S2_rows
```

S3 darf keine Zeile hinzufügen, entfernen, duplizieren oder umsortieren.

## 5. Indikatorregister

Das kanonische Profil lautet:

```text
indicator_profile_id=RCC002_CANONICAL_INDICATORS_V1
indicator_profile_version=1.0.0
indicator_schema_id=rcc002.stage.s3-indicators
indicator_schema_version=1.0.0
indicator_schema_ref=rcc002.stage.s3-indicators/1.0.0
```

`indicator_schema_ref` ist die deterministisch abgeleitete qualifizierte
Referenz und kein konkurrierender Schema-ID-Wert.

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

Die positive Allowlist kanonischer numerischer S3-Indikatorfelder lautet in
dieser Reihenfolge:

1. `sma_close_200`;
2. `ema_close_50`;
3. `rsi_wilder_14`;
4. `macd_line_12_26`;
5. `macd_signal_line_12_26_9`;
6. `macd_hist_12_26_9`;
7. `bb_mid_20`;
8. `bb_upper_20_2`;
9. `bb_lower_20_2`;
10. `bb_width_20_2`;
11. `stoch_k_14`;
12. `true_range`;
13. `atr_wilder_14`;
14. `roc_close_12_pct`;
15. `obv`;
16. `typical_price`;
17. `cci_20`;
18. `mfi_14`;
19. `plus_di_14`;
20. `minus_di_14`;
21. `dx_14`;
22. `adx_wilder_14`.

Für jedes Feld `x` dieser Allowlist erzeugt S3 unmittelbar anschließend:

```text
x
x_valid
x_warmup_complete
x_reason_codes
```

Dabei gilt:

- `x` hat den logischen Typ nullable `Float64`;
- `x_valid` hat den nicht-nullbaren Typ Boolean;
- `x_warmup_complete` hat den nicht-nullbaren Typ Boolean;
- `x_reason_codes` hat den nicht-nullbaren Typ geordnete Liste aus
  UTF-8-Strings.

S3 ist Eigentümerstufe aller vier Felder jeder Indikatorgruppe.

Jede Änderung einer Formel, Initialisierung, Nullfallregel oder
Warm-up-Semantik benötigt eine neue Indikator-ID oder Major-Version.

Additive neue Indikatorgruppen benötigen mindestens eine neue Minor-Version
des S3-Schemas. Änderungen an Namen, Typen, Nullsemantik, Formeln,
Segmentierung oder Gültigkeitssemantik benötigen eine neue Major-Version.

Historische Namen wie `ma200`, `ema50`, `rsi`, `macd_hist`, `bb_upper`,
`bb_lower`, `bb_width`, `stoch_k`, `atr`, `roc`, `cci`, `mfi` oder `adx`
sind keine kanonischen S3-Aliasfelder. Sie dürfen nur innerhalb eines
registrierten Legacy-Profils verwendet werden. Eine bloße Umbenennung in ein
kanonisches Feld ist unzulässig, wenn Formel, Seed, Warm-up oder
Lückenverhalten nicht nachweislich identisch sind.

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

Vor `t = n - 1` ist die EMA logisch `null`. Eine interne
Berechnungsrepräsentation als `NaN` richtet sich nach Abschnitt 3.5.

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

### 6.5 Lokaler Segmentindex

Alle in den Formeln verwendeten Indizes beginnen innerhalb jeder
berechnungsfähigen `indicator_segment_id` erneut bei lokalem Index `0`.

Ein Wert mit lokalem Index `t` darf ausschließlich:

- qualitätsfreigegebene Zeilen derselben `market_segment_id`;
- Zeilen derselben `indicator_segment_id`;
- gegenwarts- oder vergangenheitsbezogene Werte mit lokalem Index `i <= t`

verwenden.

Globale Dateizeilennummern oder Partitionsgrenzen dürfen Seed, Warm-up oder
Fenstergrenzen nicht verändern.

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
OBV-Seed bei null. Die gemeinsame `indicator_segment_id` weist diese
Vergleichsgrenze aus. Ein paralleles Feld `obv_segment_id` ist unzulässig.

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

Begründung: Für die 14 gerichteten Flows `1...14` werden 15 Typical-Price-Werte
`0...14` benötigt.

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
| `bb_mid_20`, `bb_upper_20_2`, `bb_lower_20_2`, `bb_width_20_2` | 19 | 20 |
| `cci_20` | 19 | 20 |
| `macd_line_12_26` | 25 | 26 |
| `adx_wilder_14` | 27 | 28 |
| `macd_signal_line_12_26_9`, `macd_hist_12_26_9` | 33 | 34 |
| `ema_close_50` | 49 | 50 |
| `sma_close_200` | 199 | 200 |

Die Indizes beziehen sich auf den Beginn einer lückenfreien Sequenz.

## 20. Gültigkeits- und Qualitätsfelder

### 20.1 Feldbezogene Gültigkeit

Für jedes kanonische numerische Indikatorfeld `x` sind exakt die in
Abschnitt 5 definierten Begleitfelder vorgeschrieben:

```text
x_valid
x_warmup_complete
x_reason_codes
```

Eine alternative parallele Validitätsmaske ist im kanonischen S3-Schema
unzulässig.

`x_warmup_complete=true` gilt genau dann, wenn seit Beginn der aktuellen
berechnungsfähigen `indicator_segment_id` sämtliche für `x` erforderlichen
gültigen Beobachtungen oder rekursiven Seeds vorliegen.

Für eine Zeile mit `quality_gate_pass=false` gilt für jedes Indikatorfeld
`x_warmup_complete=false`, `x_valid=false` und `x=null`.

`x_valid=true` gilt genau dann, wenn:

- `quality_gate_pass=true`;
- `x_warmup_complete=true`;
- alle feldspezifischen Eingaben gültig sind;
- kein erforderliches Fenster eine `market_segment_id`- oder
  `indicator_segment_id`-Grenze überschreitet;
- ein erforderlicher rekursiver State vorhanden und verifiziert ist;
- das Ergebnis endlich ist;
- sämtliche feldspezifischen Bereichsinvarianten erfüllt sind.

In jedem anderen Fall gilt `x_valid=false` und `x=null`.

### 20.2 Reason-Code-Vertrag

`x_reason_codes` ist:

- eine nach registrierter Priorität deterministisch sortierte Liste;
- leer, wenn kein Reason Code aktiv ist;
- niemals null;
- ausschließlich auf das Feld `x` bezogen.

Das Register lautet:

```text
indicator_reason_code_registry_version=1.0.0
```

| Reason Code | Standard-Severity | `x_valid` | Bedeutung |
|---|---|:---:|---|
| `IND_WARMUP_INCOMPLETE` | `INFO` | `false` | Erforderlicher Seed oder vollständiges Fenster fehlt |
| `IND_INPUT_INVALID` | `ERROR` | `false` | Mindestens ein feldspezifischer Pflichtinput ist ungültig |
| `IND_WINDOW_CROSSES_MARKET_SEGMENT` | `ERROR` | `false` | Fenster überschreitet eine `market_segment_id`-Grenze |
| `IND_WINDOW_CROSSES_INDICATOR_SEGMENT` | `ERROR` | `false` | Fenster überschreitet eine `indicator_segment_id`-Grenze |
| `IND_SYNTHETIC_INPUT_DISALLOWED` | `ERROR` | `false` | Nicht zugelassene synthetische Eingabe |
| `IND_STATE_MISSING` | `CRITICAL` | `false` | Erwarteter rekursiver Fortsetzungsstate fehlt |
| `IND_STATE_MISMATCH` | `CRITICAL` | `false` | State passt nicht zu Build, Schema, Profil oder Schlüssel |
| `IND_NONFINITE_RESULT` | `CRITICAL` | `false` | Berechnung ergab `NaN`, `+Inf` oder `-Inf` |
| `IND_RANGE_INVARIANT_FAILED` | `CRITICAL` | `false` | Feldspezifische Bereichsinvariante verletzt |
| `IND_PROFILE_MISMATCH` | `CRITICAL` | `false` | Indikator- oder Segmentierungsprofil stimmt nicht |
| `IND_SCHEMA_MISMATCH` | `CRITICAL` | `false` | Eingabe-, Ausgabe- oder State-Schema stimmt nicht |

Die Listenreihenfolge folgt einer versionierten, im Register enthaltenen
Priorität und darf nicht von Threadplanung, Feldreihenfolge oder
Hash-Iteration abhängen.

### 20.3 Nichtkritische Sonderfälle

| Reason Code | Standard-Severity | Betroffene Felder | Definierter Wert |
|---|---|---|---:|
| `IND_STOCH_FLAT_WINDOW` | `INFO` | `stoch_k_14` | `50` |
| `IND_CCI_ZERO_MAD` | `INFO` | `cci_20` | `0` |
| `IND_ADX_ZERO_TR` | `INFO` | `plus_di_14`, `minus_di_14`, `dx_14`, gegebenenfalls `adx_wilder_14` | `0` gemäß ADX-Regeln |

Diese Sonderfälle besitzen definierte numerische Werte und sind nicht
automatisch ungültig. Der zugehörige Wert bleibt bei erfüllten übrigen Regeln
gültig, und der Sonderfallcode wird in `x_reason_codes` geführt.

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

### 20.5 Zeilenbezogene Metadaten

S3 ergänzt auf jeder Zeile exakt:

| Feld | Logischer Typ | Nullbar | Bedeutung |
|---|---|:---:|---|
| `indicator_profile_id` | UTF-8-String | Nein | Kanonische Profil-ID |
| `indicator_profile_version` | UTF-8-String | Nein | Semantische Profilversion |
| `indicator_schema_id` | UTF-8-String | Nein | `rcc002.stage.s3-indicators` |
| `indicator_schema_version` | UTF-8-String | Nein | `1.0.0` |
| `indicator_schema_ref` | UTF-8-String | Nein | `rcc002.stage.s3-indicators/1.0.0` |
| `indicator_segment_id` | UTF-8-String | Nein | Deterministische S3-Berechnungssegment-ID |

Diese Felder gehören S3. Gleichnamige Eingabefelder sind unzulässig, sofern
sie nicht im Rahmen einer explizit geprüften S3-Revalidierung exakt denselben
Wert tragen.

## 21. Datenlücken und Segmentierung

### 21.1 Grundregel

Kein kanonischer Rolling- oder rekursiver Zustand darf eine echte Datenlücke
stillschweigend überbrücken.

### 21.2 Segment-ID

S3 MUST eine `indicator_segment_id` führen.

Die kanonische Segmentierungsregel lautet:

```text
indicator_segment_profile_id=RCC002_INDICATOR_SEGMENTATION_V1
indicator_segment_profile_version=1.0.0
```

Eine neue `indicator_segment_id` beginnt:

- an der ersten Zeile jeder `market_segment_id`;
- wenn `quality_gate_pass` gegenüber der vorherigen Zeile wechselt;
- nach einem expliziten rekursiven State Reset.

Damit bildet jede `indicator_segment_id` eine maximale zusammenhängende
Zeilenfolge mit:

- genau einer `market_segment_id`;
- konstantem `quality_gate_pass`;
- unverändertem Segmentierungsprofil;
- keinem internen expliziten State Reset.

Die ID wird deterministisch aus:

- `market_segment_id`;
- erstem `open_time` der Indikatorsequenz;
- `quality_gate_pass` der Sequenz;
- `indicator_profile_id`;
- `indicator_profile_version`;
- `indicator_segment_profile_id`;
- `indicator_segment_profile_version`

gebildet. Zufällige UUIDs sind unzulässig.

Eine `indicator_segment_id` darf genau eine `market_segment_id` referenzieren
und niemals mehrere Marktsegmente zusammenführen.

Zeilen mit `quality_gate_pass=false` erhalten eine Segment-ID, dürfen aber
keinen gültigen Indikatorwert erzeugen. Die erste nachfolgende wieder
qualitätsgültige Zeile beginnt ein neues Indikatorsegment.

### 21.3 Rolling-Indikatoren

Nach Segmentbeginn werden Rolling-Indikatoren erst nach ihrem vollständigen
Warm-up wieder gültig. Kein Rolling Window darf eine
`indicator_segment_id`-Grenze überschreiten.

### 21.4 Rekursive Indikatoren

EMA, RSI, ATR, OBV und ADX werden nach Segmentbeginn gemäß ihren Seed-Regeln
neu initialisiert.

Dadurch werden keine unbekannten Marktbewegungen über eine Lücke implizit als
unveränderte Zustände behandelt.

MACD einschließlich seiner Signal-EMA wird ebenfalls vollständig innerhalb
des neuen Segments neu initialisiert.

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

Der logische State-Vertrag lautet:

```text
indicator_state_schema_id=rcc002.state.s3-indicators
indicator_state_schema_version=1.0.0
indicator_state_schema_ref=rcc002.state.s3-indicators/1.0.0
```

Dieser enthält mindestens:

- letzte kanonische Schlüsselposition,
- `market_segment_id`,
- `indicator_segment_id`,
- `indicator_profile_id`,
- `indicator_profile_version`,
- EMA-Zustände,
- RSI Average Gain und Average Loss,
- ATR-Zustand,
- OBV-Zustand,
- ADX geglättete TR-/DM-Summen und ADX-Zustand,
- erforderliche vorherige OHLC-/Typical-Price-Werte,
- noch nicht abgeschlossene Warm-up-Puffer und Warm-up-Zähler,
- `indicator_state_schema_id`,
- `indicator_state_schema_version`,
- `indicator_state_schema_ref`,
- Checksumme.

### 22.4 State-Sicherheit

Ein State Snapshot darf nur verwendet werden, wenn:

- Parent-Build-ID stimmt,
- vorherige Partition erfolgreich validiert wurde,
- Schlüssel direkt anschließt,
- State-Checksumme stimmt,
- Profil-, Schema-, Segmentierungs- und Indikatorversionen identisch sind.

Bei einem kanonischen Fortsetzungsbuild wird andernfalls abgebrochen.
Ein neuer Segment-Seed ist nur nach einer expliziten, manifestierten
State-Resetentscheidung zulässig und muss eine neue `indicator_segment_id`
beginnen. Ein stiller Fallback ist unzulässig.

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

Numerisch oder semantisch wirksame Bibliotheks- und Laufzeitversionen gehören
zum registrierten Umgebungs- und numerischen Determinismusprofil der
`semantic_build_configuration`. Writer-, Kompressions- oder reine
Containerparameter gehören dagegen zur
`physical_publication_configuration`.

## 26. Ausgabevertrag

### 26.1 Pflichtausgaben

S3 erzeugt exakt das logische Schema:

```text
rcc002.stage.s3-indicators/1.0.0
```

Das kanonische Zeilenschema enthält:

- sämtliche S2-Eingabefelder unverändert,
- `indicator_profile_id`,
- `indicator_profile_version`,
- `indicator_schema_id`,
- `indicator_schema_version`,
- `indicator_segment_id`,
- für jedes Feld `x` aus Abschnitt 5 die Gruppe
  `x`, `x_valid`, `x_warmup_complete`, `x_reason_codes`.

Zusätzlich erzeugt die Stufe als getrennte Artefakte oder
Manifestbestandteile:

- den S3-Schema-Fingerprint;
- State Snapshots je abgeschlossener Partition;
- den Indikator-Validierungsbericht.

### 26.2 Keine Zeilenänderung

S3 darf im kanonischen beobachteten Datensatz:

- keine Zeile hinzufügen,
- keine Zeile entfernen,
- keinen OHLCV-Wert verändern.

Es muss gelten:

`S3_rows = S2_rows`

und der kanonische Schlüssel jeder Zeile muss identisch bleiben. Dies
konkretisiert für S3 das kanonische Row-Preservation-Prinzip aus
`RCC_002_DATA_PIPELINE_SPECIFICATION` §5.8.

### 26.3 Spaltenreihenfolge

Die Spaltenreihenfolge lautet:

1. sämtliche S2-Felder in unveränderter S2-Schemareihenfolge;
2. `indicator_profile_id`;
3. `indicator_profile_version`;
4. `indicator_schema_id`;
5. `indicator_schema_version`;
6. `indicator_segment_id`;
7. die Indikatorgruppen in der Allowlist-Reihenfolge aus Abschnitt 5.

Innerhalb jeder Indikatorgruppe lautet die Reihenfolge:

```text
x
x_valid
x_warmup_complete
x_reason_codes
```

### 26.4 Schema-Fingerprint und Kompatibilität

Der S3-Schema-Fingerprint umfasst mindestens:

- geordnete Feldnamen;
- logische Datentypen;
- Nullbarkeit;
- Eigentümerstufe;
- Primärschlüssel;
- Sortierung;
- Schema-ID und Schemaversion;
- Indikator- und Profil-IDs;
- Reason-Code-Register;
- Segmentierungsprofil.

Unbekannte Major-Versionen sind fail-closed abzulehnen.

Nicht registrierte zusätzliche Felder, historische Aliasfelder oder
abweichende Begleitfeldnamen machen das Artefakt nicht kanonisch.

### 26.5 Verbotene S3-Ausgaben

S3 darf keine:

- Signale;
- Regime;
- Long-/Short-Gates;
- Forward Returns;
- Labels;
- Strategieentscheidungen;
- physischen Layoutidentitäten als fachliche Zeilenfelder

erzeugen.

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
- Bereichsinvarianten,
- `x_valid`,
- `x_warmup_complete`,
- deterministische `x_reason_codes`,
- logisches `null` bei `x_valid=false`.

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

### 27.7 Schema- und Segmenttests

Mindestens erforderlich:

- Annahme von `rcc002.stage.s2-validated/1.0.0`;
- Ablehnung unbekannter S2- oder S3-Major-Versionen;
- exakte S3-Spaltenallowlist und Spaltenreihenfolge;
- unveränderte S2-Felder und Primärschlüssel;
- `S3_rows = S2_rows`;
- deterministische `indicator_segment_id`;
- neue Indikatorsegment-ID an jeder `market_segment_id`-Grenze;
- neue Indikatorsegment-ID beim Wechsel von `quality_gate_pass`;
- neue Indikatorsegment-ID nach explizitem State Reset;
- kein gültiger Indikatorwert bei `quality_gate_pass=false`;
- kein Rolling Window über eine Markt- oder Indikatorsegmentgrenze;
- keine Zusammenführung mehrerer `market_segment_id`-Werte;
- Ablehnung historischer Aliasfelder im kanonischen S3-Ausgang;
- exakter State-Snapshot-Vertrag
  `rcc002.state.s3-indicators/1.0.0`.

### 27.8 Property-Based Tests

SHOULD geprüft werden:

- spätere Eingangswerte verändern keinen früheren Indikatorwert;
- zusätzliche physische Partitionierung verändert keine S3-Semantik;
- identische Eingaben und Profile erzeugen identische Segment-IDs;
- jeder gültige Wert ist endlich;
- jeder ungültige Wert ist logisch `null`;
- `x_valid=true` impliziert `x_warmup_complete=true`;
- kein Feld mit einem invalidierenden Reason Code besitzt `x_valid=true`;
- jede `indicator_segment_id` referenziert genau eine
  `market_segment_id`.

## 28. Numerische Toleranzen

Das normative numerische Profil lautet:

```text
indicator_numeric_profile_id=RCC002_FLOAT64_INDICATOR_NUMERICS_V1
indicator_numeric_profile_version=1.0.0
```

### 28.1 Kanonischer Wiederholungsbuild

Bei identischer Umgebung und identischer Serialisierung wird
Checksum-Gleichheit erwartet.

### 28.2 Unabhängiger Implementierungsvergleich

Standardtoleranz für endliche `float64`-Werte:

- `absolute_tolerance = 1e-12`,
- `relative_tolerance = 1e-10`.

Der Vergleich gilt komponentenweise nach:

```text
abs(a - b) <= absolute_tolerance
               + relative_tolerance * max(abs(a), abs(b))
```

Logische Nullwerte werden ausschließlich positionsgleich mit logischen
Nullwerten verglichen. `NaN`, `+Inf` oder `-Inf` gelten nicht als gültige
Vergleichswerte.

Abweichende feldspezifische Toleranzen benötigen:

- dokumentierte Begründung,
- registrierte Feldzuordnung,
- Testabdeckung,
- Freigabe.

### 28.3 Grenzwertentscheidungen

Signal- oder Gate-Entscheidungen an Schwellenwerten dürfen nicht durch
Berichtsrundung erfolgen. Sie verwenden die ungerundeten kanonischen Werte.

### 28.4 Operations- und Determinismusgrenzen

Die Implementierung muss vor `Approved for Implementation` festlegen und
versionieren:

- Reihenfolge nicht assoziativer Float-Operationen;
- zulässige oder deaktivierte FMA-Nutzung;
- Parallelreduktionsregeln;
- Behandlung von Subnormalwerten;
- Null- und Nichtendlichkeitskonvertierung;
- Referenzimplementierung für Golden Fixtures;
- gebundene numerische Bibliotheken und Versionen.

Eine Änderung dieser Regeln verändert mindestens das numerische Profil und
erfordert Determinismus-, Golden- und Partitionsparitätstests.

## 29. Validierungsbericht

Der S3-Bericht enthält mindestens:

- Build- und Profil-ID,
- Eingabe- und Ausgabeschema-ID,
- S2- und S3-Schema-Fingerprint,
- `semantic_build_configuration_sha256`,
- numerisches Profil,
- Segmentierungsprofil,
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
- Zuordnung jeder `indicator_segment_id` zu genau einer
  `market_segment_id`,
- Anzahl der Wechsel von `quality_gate_pass`,
- State-Snapshot-Prüfungen,
- Partitionsparität,
- Golden-Test-Ergebnisse,
- Output-Checksumme.

## 30. Publication Gate

S3 darf nur veröffentlicht werden, wenn:

1. S2 vollständig kanonisch veröffentlicht ist;
2. jede S2-Eingabezeile einen gültigen und deterministisch berechneten
   booleschen `quality_gate_pass`-Wert besitzt; Zeilen mit
   `quality_gate_pass=false` bleiben im kanonischen Datensatz, erzeugen
   keine gültigen Indikatorwerte, und die Row-Count- und
   Row-Identity-Invarianten bleiben erfüllt;
3. das Eingangsschema exakt
   `rcc002.stage.s2-validated/1.0.0` erfüllt;
4. das Ausgangsschema exakt
   `rcc002.stage.s3-indicators/1.0.0` erfüllt;
5. Eingabe- und Ausgabefingerprints stimmen;
6. alle Profil-, Schema-, Segmentierungs- und Indikatorversionen registriert
   sind;
7. keine Zeile, kein Primärschlüssel und kein S2-Feld verändert wurde;
8. `S3_rows = S2_rows` gilt;
9. für jedes Feld `x` die Begleitfelder vollständig und nicht null sind;
10. `x_valid`, `x_warmup_complete`, `x_reason_codes` und logische Nullwerte
    exakt nach Abschnitt 20 gebildet wurden;
11. keine nicht endlichen gültigen Indikatorwerte bestehen;
12. alle Bereichsinvarianten bestanden sind;
13. jede `indicator_segment_id` genau eine `market_segment_id` referenziert;
14. keine Berechnung eine Markt- oder Indikatorsegmentgrenze überschreitet;
15. State Snapshots das Schema
    `rcc002.state.s3-indicators/1.0.0` erfüllen;
16. Golden-, Schema-, Segment-, Kausalitäts- und Property-Tests bestanden
    sind;
17. serieller und partitionierter Build übereinstimmen;
18. keine historischen Aliasfelder oder nicht registrierten Zusatzfelder
    enthalten sind;
19. Manifest, Berichte und Checksummen vollständig sind.

Der Gate-Status lautet:

- `PASS`,
- `FAIL`,
- `PASS_WITH_APPROVED_EXCEPTIONS`.

`PASS_WITH_APPROVED_EXCEPTIONS` darf ausschließlich nicht blockierende,
vollständig dokumentierte Berichtsbefunde betreffen. Es darf weder ein
ungültiges S2-Feld noch einen regelwidrig gebildeten `x_valid`-Status, einen
Schemafehler, einen Segmentfehler, einen nicht endlichen gültigen Wert oder
eine fehlgeschlagene Reconciliation überstimmen.

Die in diesem Abschnitt aufgeführten Ausnahmefälle für
`PASS_WITH_APPROVED_EXCEPTIONS` sind abschließend. Kein hier nicht
aufgeführter Fall darf unter diesem Gate-Status genehmigt werden, ohne
zuvor eine normative Spezifikationsänderung, eine Versionsanhebung, einen
Review und eine erneute Zertifizierungsbewertung zu durchlaufen. Eine
menschliche Genehmigung allein erweitert nicht den normativen
Ausnahmeumfang.

## 31. Offene Implementierungsparameter

### 31.1 Vor `Approved for Implementation` festzulegen

Folgende semantische oder determinismusrelevante Festlegungen müssen
versioniert vorliegen:

- vollständiges maschinenlesbares S3-Schema;
- vollständiges Indikator- und Reason-Code-Register;
- `indicator_profile_id` und Profilversion;
- Segment-ID-Kanonisierungs- und Hashprofil;
- State-Snapshot-Schema und State-Checksum-Profil;
- numerisches Determinismusprofil einschließlich Operationsreihenfolge;
- gebundene Referenzbibliotheken und Versionen;
- feldbezogene Referenztoleranzen;
- Golden-Fixture-Inhalte und erwartete Resultate;
- Build-Einstiegspunktvertrag;
- Umgebungs- und Lockstrategie;
- Schema-Kompatibilitäts- und Migrationsregeln.

Diese Festlegungen gehören zur `semantic_build_configuration`, soweit sie
fachliche Werte, Validität, Segmentierung, Schema oder Reproduzierbarkeit
beeinflussen.

### 31.2 Während der Implementierung konkretisierbar

Innerhalb vorher festgelegter physischer Profile dürfen konkretisiert werden:

- physische Partitionsgrößen;
- Parquet-Row-Group-Größen;
- Kompressionsstufe;
- Writeroptimierungen;
- Cache- und temporäre Speicherorte;
- Retentionsparameter temporärer State Snapshots.

Diese Parameter gehören zur `physical_publication_configuration`. Sie dürfen
weder Indikatorwerte noch Gültigkeit, Segment-IDs, logisches S3-Schema,
`build_id` oder `dataset_id` verändern.

Jede spätere Änderung mit Wirkung auf fachliche Semantik, logische Schemas,
Identitätsvorabbildungen oder numerische Determinismusregeln muss die
betroffenen Review-Gates erneut durchlaufen.

## 32. Abnahmekriterien

### 32.1 Spezifikationsreife vor Implementierungsfreigabe

Die Spezifikation ist bereit für `Approved for Implementation`, wenn:

1. sämtliche logischen S2-Eingangs- und S3-Ausgangsfelder mit Typ,
   Nullsemantik, Eigentümerstufe und Reihenfolge festgelegt sind;
2. alle Formeln, Seeds, Warm-up-Grenzen und Nullfälle eindeutig sind;
3. alle `x_valid`-, `x_warmup_complete`- und `x_reason_codes`-Regeln
   maschinenlesbar definiert sind;
4. `market_segment_id` und `indicator_segment_id` eindeutig abgegrenzt sind;
5. Segment-, Profil-, Schema-, State- und numerische IDs versioniert sind;
6. semantische und physische Konfiguration getrennt sind;
7. Golden-, Unit-, Property-, Schema-, Segment-, Kausalitäts- und
   Integrationstestverträge vollständig sind;
8. Publication Gate und Manifestverträge vollständig sind;
9. kanonisches und Legacy-Profil strikt getrennt sind;
10. alle vorgeschriebenen internen und externen Review-Gates der
    Spezifikationsbaseline bestanden sind;
11. keine offene Entscheidung fachliche Werte, Gültigkeit, Segmentierung,
    logisches Schema oder Identitätsvorabbildungen verändern kann.

### 32.2 Abnahme der Implementierung

Die spätere Implementierung ist akzeptiert, wenn:

1. alle Golden Fixtures exakt innerhalb der registrierten Toleranzen bestanden
   sind;
2. sämtliche Unit-, Property-, Schema-, Segment-, Kausalitäts- und
   Integrationstests bestanden sind;
3. State Snapshot und Partitionsparität bestanden sind;
4. der BTCUSDT-1m-Vollbuild auf der Workstation bestanden ist;
5. ein unabhängiger Rebuild mindestens semantische Gleichheit erreicht;
6. keine Zeile und kein S2-Feld verändert wurde;
7. Schema-, Zeilen- und Segment-Reconciliation vollständig sind;
8. Manifest und Knowledge Lineage vollständig sind;
9. keine offene kritische Inkonsistenz besteht;
10. das S3-Publication-Gate automatisiert bestanden ist.

## 33. Freigabestatus und nächster Schritt

`RCC-002-SCR-004` bestätigte die dort geprüften wissenschaftlichen
Korrekturen als geschlossen.

Der vollständige Architecture Integrity Review `RCC-002-AIR-001` bewertete
die Spezifikationsfamilie als:

```text
NOT PASSED – ARCHITECTURE CORRECTIONS REQUIRED
```

Version 0.4.0 bewahrt die AIR-001-Korrekturen aus Version 0.3.0 und
korrigiert zusätzlich:

- `SCR-005-M01` – unversionierte `indicator_schema_id` und
  `indicator_state_schema_id`, getrennte Versionen sowie eindeutig
  abgeleitete qualifizierte Schemareferenzen.

Sie aktualisiert außerdem die Abhängigkeiten auf:

```text
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md
Version 0.7.0

RCC_002_DATA_VALIDATION_2026-07-23.md
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
