# RCC-002 S7 Implementation Readiness Review

## 1. Entscheidung

**Status: APPROVED FOR IMPLEMENTATION**

Die zertifizierte RCC-002-Baseline definiert den S6→S7-Vertrag,
sämtliche sechs Horizonte, alle Label-Familien, Profile, Reason Codes,
Nullregeln, Segmentregeln und Leakage-Grenzen hinreichend eindeutig.
Es besteht kein offener fachlicher oder architektonischer Blocker für die
Implementierung des kanonischen S7-Profils.

Diese Entscheidung ist eine Implementierungsfreigabe, keine
Publikationszertifizierung eines vollständigen BTCUSDT-Datasets.

## 2. Prüfgrundlage

| Artefakt | SHA-256 |
|---|---|
| `RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` | `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` |
| `RCC_002_DVSEV001_CORRECTED_BUNDLE_MANIFEST_2026-07-27.md` | `176d99582ebff741d5d45b7fccc76a49b5b1d267ce350d867d4f64c17c6a8297` |
| `RCC_002_S6_IMPLEMENTATION_CERTIFICATION_DECISION_2026-07-30.md` | `e9dfc7922fe395658d20580d9a70d836b0bc8a1fcf38c9d4f37e7b167e5ae16a` |

Normativer S7-Vertrag:

- `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`,
  Version `0.4.1`;
- Eingang `rcc002.stage.s6-gates/1.0.0`;
- Ausgang `rcc002.stage.s7-labels/1.0.0`;
- Komponente `RCC002_S7_LABEL_BUILDER/0.3.0`.

## 3. Gebundene kanonische Profile

| Dimension | Verbindlicher Wert |
|---|---|
| Labelprofil | `RCC002_CANONICAL_LABELS_V1/1.0.0` |
| Horizon-Registry | `RCC002_FORWARD_HORIZONS_V1/1.0.0` |
| Horizonte | `H001`, `H005`, `H015`, `H060`, `H240`, `H1440` |
| Kostenprofil | `COST_PROXY_FEE_RT_0004_V1/1.0.0` |
| Barrier-Profil | `L1_BARRIER_TP050_SL020_V1/1.0.0` |
| Reason-Code-Registry | `1.0.0` |
| Numerikprofil | `RCC002_FLOAT64_LABEL_NUMERICS_V1/1.0.0` |

Unbekannte IDs oder Versionen führen vor jeder Zeilenausgabe zum
Buildabbruch.

## 4. Exaktes S7-Schema

S7 übernimmt sämtliche S6-Felder unverändert und in unveränderter
Reihenfolge.

Die S7-Erweiterung enthält exakt:

- 14 nicht horizonspezifische Metadatenfelder;
- 48 Felder je Horizont;
- sechs Horizonte;
- damit **302 neue logische Felder**.

Die 48 Horizon-Felder bestehen aus:

- 2 gemeinsamen Horizon-Metadaten;
- 18 familienbezogenen Validitäts-, Reason-Code- und Segmentfeldern;
- 8 Return-Feldern;
- 8 Excursion-Feldern;
- 6 Direction-Feldern;
- 6 Barrier-Feldern.

Die Python-Repräsentation gruppiert die 48 wiederholten Felder in
`HorizonLabels`. `flatten_s7_extension()` expandiert daraus deterministisch
die exakt geordnete physische 302-Feld-Erweiterung. Diese
Repräsentationsentscheidung ändert das logische Schema nicht.

Gebundener S7-Schema-Fingerprint:

```text
075ef38aac0a5de31eefdee6881139e2f8188e8b1722f7c577e9aaa83cad643a
```

## 5. Numerisches Determinismusprofil

Für die Implementierung werden folgende zuvor reservierten Details
verbindlich konkretisiert:

1. Berechnungsdomäne ist Python `float` als IEEE-754 Binary64.
2. Es findet keine Zwischenrundung statt.
3. FMA wird nicht verwendet.
4. Der kanonische lineare Long-Return wird als
   `(exit / entry) - 1.0` berechnet.
5. Der Short-Return wird als exakte binäre Negation des kanonischen
   Long-Returns materialisiert. Damit gilt die normative
   Long-/Short-Identität bitgenau.
6. Log Returns verwenden `math.log(exit / entry)`; Short ist die exakte
   Negation.
7. Der Net-Proxy wird als `gross - 0.0004` berechnet.
8. Minima und Maxima werden deterministisch über die chronologisch geordnete
   Zukunftssequenz bestimmt. Bei gleichen Extrema gewinnt der erste Offset.
9. `-0.0` wird als `+0.0` kanonisiert.
10. Division durch null, nicht positive Preisreferenzen und nicht endliche
    Ergebnisse führen zu familienlokaler Invalidität, `null` und dem
    passenden registrierten Reason Code.
11. Barrier- und Direction-Vergleiche erfolgen exakt, ohne Deadband.
12. Referenztoleranzen sind absolut `1e-12` und relativ `1e-10`;
    diskrete Ergebnisse müssen exakt übereinstimmen.

Gebundener semantischer Konfigurationshash:

```text
dcad27744de8fff0f29400d7f825ba89b6a9610f1f690449cdf6575c95bfb7b1
```

## 6. Zeit-, Segment- und Validitätsvertrag

- Horizon-Ende ist exakt `t+h` auf der 1m-Zeitachse.
- Ein vollständiges gültiges Fenster muss alle erwarteten Minuten enthalten.
- Signalkerze und Zukunftsfenster müssen dieselbe
  `market_segment_id` besitzen.
- Eine fehlende erwartete Minute bei vorhandenen späteren Daten ist
  `LBL_WINDOW_CROSSES_MARKET_SEGMENT`.
- Reicht der gelesene Datensatz nicht bis `t+h`, gilt ausschließlich
  `LBL_FUTURE_HORIZON_INCOMPLETE`.
- Synthetische oder qualitätsungültige Zukunftskerzen invalidieren die
  betroffenen Familien.
- Familieninvalidität setzt numerische und diskrete Werte auf `null`;
  Barrier-Outcomes werden `INVALID`.
- `label_available_at_h` ist bei vollständigem Horizon
  `close_time_(t+h)` und bei unvollständigem Tail `null`.
- Es gibt bewusst kein globales `label_valid`.

## 7. Partitionierung, inkrementelle Aktualisierung und Splits

- Eine Partition darf bis zu 1.440 Zukunftszeilen als Read-only-Overlap
  erhalten.
- `output_row_count` begrenzt die Ausgabe auf den eigenen Partitionspräfix;
  Overlap-Zeilen werden nicht doppelt ausgegeben.
- Eine Änderung an Bar `k` invalidiert mindestens
  `[k-1440, ..., k]`.
- Chronologische Samples werden vor einer Splitgrenze entfernt, wenn
  `t+h` die Grenze erreicht oder überschreitet.
- Zukunftslabels werden unabhängig von Signal-, Regime- und Gatezuständen
  für jede Zeile berechnet.

## 8. Leakage-Schutz

Jedes der 302 S7-Felder trägt:

```text
field_owner_stage=S7_LABELS
leakage_class=FUTURE_OUTCOME
live_allowed=false
paper_allowed=false
backtest_input_allowed=false
research_feature_allowed=false
label_research_allowed=true
```

Der fail-closed Guard lehnt zusätzlich reservierte `fwd_`, `label_` und
`barrier_`-Präfixe, Felder ohne Eigentümer und Felder außerhalb positiver
Allowlists ab.

## 9. Implementierungs- und Abnahmescope

Freigegeben sind:

- Formeln und Barrier-Suche;
- exakte Schema- und Registry-Expansion;
- familienlokale Validität und Reason Codes;
- Row Preservation und Containertrennung;
- serielle und partitionierte Berechnung;
- inkrementelle Invalidierungs- und Split-Purge-Helfer;
- Unit-, Golden-, Property-, Schema-, Leakage- und Paritätstests.

Vor einer späteren Produktionszertifizierung bleiben separat nachzuweisen:

- vollständiger BTCUSDT-1m-Workstation-Build;
- S7-Buildbericht und Verteilungen auf dem realen Dataset;
- vollständiges Stage-Manifest und Artefaktchecksummen;
- Vollbuild-/Inkremental-Reconciliation auf realen Artefakten;
- unabhängige Claude- und Gemini-Reviews;
- finale Implementierungszertifizierungsentscheidung.

## 10. Schlussurteil

```text
APPROVED FOR IMPLEMENTATION
```

Es gibt keinen offenen CRITICAL-, MAJOR- oder semantischen
Implementierungsblocker.
