# RCC-002 DVSEV-001 — Reason-Code-Severity Correction Proposal

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Gezielter Spezifikationskorrekturzyklus (Investigation & Proposal) |
| Dokument-ID | `RCC-002-DVSEV-001` |
| Titel | Reason-Code-Severity-Register — Korrekturvorschlag für `RCC_002_DATA_VALIDATION` §16 |
| Version | 1.0.0 (Vorschlag, nicht verbindlich) |
| Datum | 2026-07-27 |
| Status | Vorschlag zur Prüfung — **nicht in die zertifizierte Spezifikation übernommen**; keine Implementierungsdatei geändert |
| Speicherort im Repository | `docs/review/RCC_002_DVSEV_001_REASON_CODE_SEVERITY_CORRECTION_PROPOSAL_2026-07-27.md` |
| Auslöser | Während der RCC-002-Implementierung, Schritt 4 (S2-Validierung), festgestellte normative Lücke: fehlende Standard-Severity-Zuordnung für 26 von 32 registrierten Reason Codes gemäß `RCC_002_DATA_VALIDATION` §16.2 und §24.1(3) |
| Betroffenes Dokument | `RCC_002_DATA_VALIDATION_2026-07-23.md`, aktuelle Version `0.4.2` |
| Indirekt betroffene Dokumente | `RCC_002_INDICATOR_SPECIFICATION`, `RCC_002_SIGNAL_TRANSFORMATION`, `RCC_002_REGIME_AND_GATE_SPECIFICATION`, `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION`, `RCC_002_REPRODUCIBILITY_AND_MANIFEST` (Version-Zitat-Kette) |
| Autoritative Sprache | Deutsch für normative Erläuterung; Englisch für Reason Codes, Feldnamen und Konstanten |

Dieses Dokument ist eine **Untersuchung und ein Korrekturvorschlag**. Es
verändert keine zertifizierte Spezifikationsdatei und keine
Implementierungsdatei. Es dient ausschließlich der Vorlage zur Prüfung und
Freigabeentscheidung.

---

## 1. Vollständiger Vorschlag: Data Validation §16.3 „Reason-Code-Severity-Register"

Der folgende Abschnitt ist als wortwörtlich einfügbarer Vorschlag formuliert,
zur Einfügung unmittelbar nach §16.2 („Reason-Code-Regeln") und vor §17
(„Reconciliation zwischen Stufen") in `RCC_002_DATA_VALIDATION_2026-07-23.md`.

> ### 16.3 Reason-Code-Severity-Register
>
> Jeder in §16.2 registrierte Reason Code besitzt genau eine
> Standard-Severity gemäß nachfolgendem Register. Dieses Register erfüllt
> die in §16.2 geforderte Eigenschaft „eine Standard-Severity besitzen" und
> die Abnahmevoraussetzung §24.1 Nr. 3 vollständig.
>
> Für Reason Codes, deren Severity bereits an anderer Stelle dieses
> Dokuments normativ explizit festgelegt ist, übernimmt dieses Register
> unverändert den dort festgelegten Wert. Das Register ersetzt keine dieser
> Festlegungen; es konsolidiert sie an einer Stelle.
>
> | # | Reason Code | Standard-Severity | Normative Referenz |
> |---:|---|---|---|
> | 1 | `DV_FILE_MISSING` | `ERROR` | §5.2 (mindestens `ERROR`; Herabstufung auf `WARN` nur bei genehmigter, dokumentierter Ausnahme) |
> | 2 | `DV_FILE_EMPTY` | `ERROR` | §5.2 analog; §6.1 (nur `VERIFIED` darf regulär in S1 eingehen) |
> | 3 | `DV_FILE_CORRUPT` | `CRITICAL` | §6.2 (strukturelle Öffnungs-/Parsefehler); §16.1 |
> | 4 | `DV_CHECKSUM_MISMATCH` | `CRITICAL` | §6.2; §16.1 |
> | 5 | `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION` | `ERROR` im Standardfall; `CRITICAL` bei vorgelagerter Evidenz für mehr Zeilen oder einen erwarteten längeren Zeitbereich | §6.3 (Eskalationsregel bleibt unverändert bestehen) |
> | 6 | `DV_SCHEMA_REQUIRED_COLUMN_MISSING` | `CRITICAL` | §14.1 (Nullwerte in Primärschlüssel-, Zeit- oder OHLCV-Pflichtfeldern) |
> | 7 | `DV_SCHEMA_UNEXPECTED_COLUMN` | `WARN` | §7.3 (Berichtspflicht ohne Blockierungswirkung) |
> | 8 | `DV_PARSE_TIMESTAMP_FAILED` | `CRITICAL` | §14.1 |
> | 9 | `DV_PARSE_NUMERIC_FAILED` | `CRITICAL` | §7.2 |
> | 10 | `DV_TIME_NOT_UTC` | `CRITICAL` | §8.1 (unzulässig für `CANONICAL_BUILD`); §14.1 |
> | 11 | `DV_TIME_MISALIGNED` | `CRITICAL` | §8.3; §14.1 |
> | 12 | `DV_TIME_OUT_OF_RANGE` | `ERROR` | §9.3 (aktive Behandlungspflicht statt stillem Verwerfen) |
> | 13 | `DV_DUPLICATE_IDENTICAL_COLLAPSED` | `INFO` | §10.1 (genehmigte, deterministische, verlustfreie Operation) |
> | 14 | `DV_DUPLICATE_CONFLICT` | `CRITICAL` | §10.2 |
> | 15 | `DV_SOURCE_CONFLICT_RESOLVED` | `INFO` | §15.2 (dokumentierter, genehmigt aufgelöster Zustand) |
> | 16 | `DV_GAP_DETECTED` | `WARN` | §11.1 (unklassifizierter Befund; spezifischere Klassifikation kann eskalieren) |
> | 17 | `DV_GAP_UNEXPLAINED` | `ERROR` | §11.2 (`UNKNOWN`-Klasse: mindestens `ERROR`; `CRITICAL` bei nachgewiesener Systematik) |
> | 18 | `DV_TIME_GAP_SEGMENT_STARTED` | `INFO` | §11.3.1 (normale, dokumentierte Folge der Segmentbildungsregel) |
> | 19 | `DV_NUMERIC_NONFINITE` | `CRITICAL` | §14.1 (funktionale Gleichwertigkeit zu Nullwert in OHLCV-Pflichtfeld) |
> | 20 | `DV_OHLC_INVARIANT_FAILED` | `CRITICAL` | §12.1 |
> | 21 | `DV_VOLUME_NEGATIVE` | `CRITICAL` | §12.2 |
> | 22 | `DV_VOLUME_ZERO_OBSERVED` | `WARN` | §12.2 (nicht automatisch ungültig, aber aktive Beobachtungspflicht) |
> | 23 | `DV_ANOMALY_EXTREME_CANDLE_RETURN` | `WARN` | §13.1, §13.3 (Untersuchungszweck; keine Wertveränderung) |
> | 24 | `DV_ANOMALY_EXTREME_HIGH_LOW_RANGE` | `WARN` | §13.1, §13.3 |
> | 25 | `DV_ANOMALY_EXTREME_VOLUME` | `WARN` | §13.1, §13.3 |
> | 26 | `DV_ANOMALY_ZERO_VOLUME_CLUSTER` | `WARN` | §13.1, §13.3 |
> | 27 | `DV_ANOMALY_REPEATED_IDENTICAL_OHLC` | `WARN` | §13.1, §13.3 |
> | 28 | `DV_ANOMALY_PARTITION_BOUNDARY_JUMP` | `WARN` | §13.1, §13.3 |
> | 29 | `DV_SYNTHETIC_ROW_NONCANONICAL` | `CRITICAL` | §11.4; Data Pipeline §7.3 (Ausschluss synthetischer Zeilen aus kanonischen Views) |
> | 30 | `DV_APPROVED_WARNING_ACTIVE` | `INFO` | §20 (dokumentierte, genehmigte Nichtblockierung eines `WARN`) |
> | 31 | `DV_ROW_RECONCILIATION_FAILED` | `CRITICAL` | §3.4; §17 (Reconciliation-Gleichungen) |
> | 32 | `DV_SCHEMA_FINGERPRINT_MISMATCH` | `CRITICAL` | §7.4 (fail-closed bei unbekannter Major-Version) |
>
> Die in Zeilen 3, 4, 5, 6, 8, 9, 10, 11, 12, 14, 17, 19, 20, 21, 29 und 31
> ausgewiesene Severity ist bereits an der zitierten Stelle explizit
> normiert oder folgt unmittelbar und ohne Auslegungsspielraum aus §14.1.
> Die verbleibenden Zuordnungen sind Gegenstand dieses Korrekturzyklus und
> unterliegen der Freigabe durch die zuständige Prüfinstanz.

---

## 2. Vollständige normative Tabelle aller 32 Reason Codes (Prüftabelle)

Diese Tabelle stellt dieselben 32 Zuordnungen wie Abschnitt 1 dar, ergänzt
um die Herkunftskategorie und eine Kurzbegründung, zur erleichterten
Prüfung. Sie ist kein Bestandteil des Einfügevorschlags selbst.

| Reason Code | Severity | Herkunft | Begründung (ausschließlich bestehende Buildwirkungen/Fail-closed-Regeln/Validierungssemantik/Governance) |
|---|---|---|---|
| `DV_FILE_MISSING` | `ERROR` | Neu | §5.2 fixiert für exakt diesen Fall bereits „mindestens `ERROR`". |
| `DV_FILE_EMPTY` | `ERROR` | Neu | Funktional identische Wirkung wie `DV_FILE_MISSING` — Datei erreicht nie `VERIFIED` (§6.1). |
| `DV_FILE_CORRUPT` | `CRITICAL` | Neu | Strukturelle Kernverletzung im Sinne §16.1; Datei erreicht nie `VERIFIED`. |
| `DV_CHECKSUM_MISMATCH` | `CRITICAL` | Neu | Nachgewiesene Bytintegritätsverletzung; gleiche Einstufung wie `DV_FILE_CORRUPT`. |
| `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION` (Standardfall) | `ERROR` | Neu (Eskalation bereits bestehend) | Nicht selbst-widerlegter Trunkierungsverdacht ist eine relevante, standardmäßig blockierende Qualitätsverletzung; Eskalation zu `CRITICAL` bleibt §6.3 vorbehalten. |
| `DV_SCHEMA_REQUIRED_COLUMN_MISSING` | `CRITICAL` | Neu | Fehlende Pflichtspalte macht jede Zeile per Konstruktion zu einem Nullwert-Fall in einem Pflichtfeld (§14.1). |
| `DV_SCHEMA_UNEXPECTED_COLUMN` | `WARN` | Neu | §7.3 verlangt nur Bericht, keine Blockierung. |
| `DV_PARSE_TIMESTAMP_FAILED` | `CRITICAL` | Bereits explizit (Brücke) | §14.1 „Zeit-Pflichtfelder"; identisch zur bereits implementierten Einstufung in Schritt 3. |
| `DV_PARSE_NUMERIC_FAILED` | `CRITICAL` | Bereits explizit | §7.2 wörtlich. |
| `DV_TIME_NOT_UTC` | `CRITICAL` | Neu | §8.1 „unzulässig für `CANONICAL_BUILD`"; Zeit-Pflichtfeld-Kategorie §14.1. |
| `DV_TIME_MISALIGNED` | `CRITICAL` | Neu | Gleiche Zeit-Pflichtfeld-Kategorie wie `DV_TIME_NOT_UTC`. |
| `DV_TIME_OUT_OF_RANGE` | `ERROR` | Neu | §9.3 verlangt aktive Klärung statt stillen Verwerfens; kein Hinweis auf reine `WARN`-Einstufung. |
| `DV_DUPLICATE_IDENTICAL_COLLAPSED` | `INFO` | Neu | §10.1 beschreibt eine genehmigte (MAY), deterministische, verlustfreie Operation — entspricht §16.1 `INFO` wörtlich. |
| `DV_DUPLICATE_CONFLICT` | `CRITICAL` | Bereits explizit | §10.2 wörtlich. |
| `DV_SOURCE_CONFLICT_RESOLVED` | `INFO` | Neu | §15.2 beschreibt einen bereits genehmigt aufgelösten, dokumentierten Zustand. |
| `DV_GAP_DETECTED` | `WARN` | Neu | Generischer, noch unklassifizierter Befund (§11.1); spezifischere Klassen tragen ggf. höhere Severity. |
| `DV_GAP_UNEXPLAINED` | `ERROR` | Neu | Entspricht der `UNKNOWN`-Lückenklasse, für die §11.2 „mindestens `ERROR`" fixiert. |
| `DV_TIME_GAP_SEGMENT_STARTED` | `INFO` | Neu | §11.3.1 beschreibt eine normale, dokumentierte, erwartete Buchungsfolge, keine Verletzung. |
| `DV_NUMERIC_NONFINITE` | `CRITICAL` | Neu | Ein nicht-endlicher Wert in einem OHLCV-Pflichtfeld ist funktional gleichwertig zu einem Nullwert (§14.1). |
| `DV_OHLC_INVARIANT_FAILED` | `CRITICAL` | Bereits explizit | §12.1 wörtlich. |
| `DV_VOLUME_NEGATIVE` | `CRITICAL` | Bereits explizit | §12.2 wörtlich. |
| `DV_VOLUME_ZERO_OBSERVED` | `WARN` | Neu | §12.2: „nicht automatisch ungültig", aber Häufigkeits-/Cluster-Berichtspflicht — aktive Beobachtung, keine reine `INFO`. |
| `DV_ANOMALY_EXTREME_CANDLE_RETURN` | `WARN` | Neu | §13.1 „dient der Untersuchung, nicht der stillen Datenbereinigung"; §13.3 keine Wertveränderung. |
| `DV_ANOMALY_EXTREME_HIGH_LOW_RANGE` | `WARN` | Neu | Wie oben. |
| `DV_ANOMALY_EXTREME_VOLUME` | `WARN` | Neu | Wie oben. |
| `DV_ANOMALY_ZERO_VOLUME_CLUSTER` | `WARN` | Neu | Wie oben. |
| `DV_ANOMALY_REPEATED_IDENTICAL_OHLC` | `WARN` | Neu | Wie oben. |
| `DV_ANOMALY_PARTITION_BOUNDARY_JUMP` | `WARN` | Neu | Wie oben. |
| `DV_SYNTHETIC_ROW_NONCANONICAL` | `CRITICAL` | Neu | §11.4 und Data Pipeline §7.3 verbieten synthetische Zeilen in kanonischen Views explizit — Verletzung der View-Isolationsarchitektur. |
| `DV_APPROVED_WARNING_ACTIVE` | `INFO` | Neu | §20: dokumentierte, versionierte, genehmigte Nichtblockierung eines `WARN` — per Definition ein dokumentierter Normalzustand. |
| `DV_ROW_RECONCILIATION_FAILED` | `CRITICAL` | Neu | §3.4 zählt „Vollständige Reconciliation" zu den fünf Validierungsgrundsätzen; §17 fixiert MUST-Gleichungen. |
| `DV_SCHEMA_FINGERPRINT_MISMATCH` | `CRITICAL` | Neu | §7.4 „Unbekannte Major-Versionen werden fail-closed abgelehnt" — strukturell gleichwertiger Fall. |

**Verteilung der 26 neu zugeordneten Severities**: 8× `CRITICAL`, 3× `ERROR`,
8× `WARN`, 7× `INFO`.

---

## 3. Interner Konsistenzcheck gegen alle bestehenden Normstellen

Für jeden der 32 Codes wurde geprüft, ob die vorgeschlagene Severity einer
bereits bestehenden expliziten oder impliziten normativen Aussage in
`RCC_002_DATA_VALIDATION` widerspricht. Ergebnis je Code:

| Code | Geprüfte Normstellen | Ergebnis |
|---|---|---|
| `DV_FILE_MISSING` | §5.2, §6.1 | Konsistent — Vorschlag übernimmt §5.2 direkt |
| `DV_FILE_EMPTY` | §5.2, §6.1, §6.2 | Konsistent — keine gegenläufige Aussage vorhanden |
| `DV_FILE_CORRUPT` | §6.1, §6.2, §16.1 | Konsistent |
| `DV_CHECKSUM_MISMATCH` | §6.1, §6.2, §16.1 | Konsistent |
| `DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION` | §6.3 | Konsistent — Eskalationsregel bleibt unverändert; nur der bislang undefinierte Standardfall wird ergänzt |
| `DV_SCHEMA_REQUIRED_COLUMN_MISSING` | §7.1, §14.1 | Konsistent |
| `DV_SCHEMA_UNEXPECTED_COLUMN` | §7.3 | Konsistent — §7.3 nennt nur Berichtspflicht |
| `DV_PARSE_TIMESTAMP_FAILED` | §14.1 | Konsistent — bereits in Schritt 3 identisch angewandt |
| `DV_PARSE_NUMERIC_FAILED` | §7.2 | Konsistent — wörtliche Übernahme |
| `DV_TIME_NOT_UTC` | §8.1, §14.1 | Konsistent |
| `DV_TIME_MISALIGNED` | §8.3, §14.1 | Konsistent |
| `DV_TIME_OUT_OF_RANGE` | §9.3, §20 Nr. 12 | Konsistent — `ERROR` blockiert Publication Gate Kriterium 12 wie gefordert |
| `DV_DUPLICATE_IDENTICAL_COLLAPSED` | §10.1, §16.1 | Konsistent |
| `DV_DUPLICATE_CONFLICT` | §10.2 | Konsistent — wörtliche Übernahme |
| `DV_SOURCE_CONFLICT_RESOLVED` | §15.2, §16.1 | Konsistent |
| `DV_GAP_DETECTED` | §11.1, §11.2 | Konsistent — als generischer Befund unterhalb der klassenspezifischen §11.2-Mindestsätze eingeordnet, ohne diese zu unterlaufen |
| `DV_GAP_UNEXPLAINED` | §11.2 | Konsistent — „mindestens `ERROR`" wörtlich übernommen |
| `DV_TIME_GAP_SEGMENT_STARTED` | §11.3.1 | Konsistent |
| `DV_NUMERIC_NONFINITE` | §14.1 | Konsistent |
| `DV_OHLC_INVARIANT_FAILED` | §12.1 | Konsistent — wörtliche Übernahme |
| `DV_VOLUME_NEGATIVE` | §12.2 | Konsistent — wörtliche Übernahme |
| `DV_VOLUME_ZERO_OBSERVED` | §12.2 | Konsistent — „nicht automatisch ungültig" widerspricht `WARN` nicht (`WARN` ≠ Blockierung) |
| `DV_ANOMALY_EXTREME_CANDLE_RETURN` … `_PARTITION_BOUNDARY_JUMP` (6 Codes) | §13.1–§13.3 | Konsistent — Untersuchungszweck und Verbot der Wertveränderung entsprechen exakt der `WARN`-Definition |
| `DV_SYNTHETIC_ROW_NONCANONICAL` | §11.4, Data Pipeline §7.3 | Konsistent |
| `DV_APPROVED_WARNING_ACTIVE` | §20 | Konsistent |
| `DV_ROW_RECONCILIATION_FAILED` | §3.4, §17 | Konsistent |
| `DV_SCHEMA_FINGERPRINT_MISMATCH` | §7.4 | Konsistent |

Zusätzlich geprüft und **ohne Konflikt befunden**:

- **§15.1 / §15** (`quality_status`-Formel: „höchste registrierte Severity
  aller aktiven `quality_reason_codes`"): Das Register macht diese Formel
  für alle 32 Codes erstmals vollständig deterministisch berechenbar; keine
  bestehende Formel wird verändert.
- **§20 Kriterium 12** („kein `ERROR` oder `CRITICAL` offen ist") und
  §20-Ausnahmeregel („darf weder einen aktiven zeilenbezogenen `ERROR` oder
  `CRITICAL` überstimmen"): Beide Formulierungen sind bereits abschließend
  (erschöpfend, nicht illustrativ) formuliert — anders als die vor
  `AIR4-MIN-01` bestehenden Carve-out-Formulierungen in Indicator/Signal
  Transformation. Es besteht **kein** Bedarf an einer analogen Korrektur in
  §20 selbst; dies wurde als Anschlussprüfung erwogen und hiermit
  ausgeräumt.
- **§25.1** (offene Implementierungsparameter): Das dort genannte
  „Reason-Code-**Prioritäts**register" (Sortierreihenfolge) bleibt
  unberührt und weiterhin offen. Dieser Korrekturzyklus behandelt
  ausschließlich **Severity**, nicht Priorität/Sortierreihenfolge.
- **Lückenklassen nach §11.2** (`SOURCE_FILE_MISSING`, `PARSING_LOSS` usw.):
  Diese sind eine separate Taxonomie ohne `DV_`-Präfix und nicht Teil von
  `quality_reason_codes`. Sie sind nicht Gegenstand dieses Registers und
  werden hierdurch nicht verändert.

---

## 4. Identifizierte Widersprüche

**Es wurde kein direkter Widerspruch zwischen einer vorgeschlagenen
Severity und einer bestehenden expliziten Normaussage gefunden.**

Vier Zuordnungen stützen sich auf eine vergleichsweise schwächere, indirekte
Ableitung (funktionale Analogie statt wörtlicher Regel) und werden als
**gesondert zu bestätigende Einzelentscheidungen** markiert, nicht als
Widerspruch:

1. `DV_TIME_OUT_OF_RANGE` (`ERROR`) — §9.3 nennt zwei mögliche
   Behandlungspfade (Konfigurationsfehler vs. Quarantäne), aber keine
   einheitliche Severity für beide.
2. `DV_GAP_DETECTED` (`WARN`) — als generischer, noch unklassifizierter
   Befund von §11.2 abgegrenzt; die Abgrenzung selbst ist keine im Dokument
   explizit gezogene Trennlinie.
3. `DV_FILE_EMPTY` (`ERROR`) — durch funktionale Gleichsetzung mit
   `DV_FILE_MISSING` abgeleitet, nicht durch eine eigene Normstelle.
4. `DV_VOLUME_ZERO_OBSERVED` (`WARN`) — Abgrenzung gegenüber `INFO` beruht
   auf der Berichtspflicht (§12.2), nicht auf einer expliziten
   Severity-Nennung.

Diese vier sind keine Fehler, sondern die Stellen mit dem geringsten
direkten Textbeleg; sie werden hier explizit hervorgehoben, damit die
Freigabeentscheidung gezielt darauf gerichtet werden kann.

---

## 5. Minimal erforderliche Spezifikationsänderung

Ausschließlich:

- Einfügung von §16.3 „Reason-Code-Severity-Register" gemäß Abschnitt 1,
  unmittelbar nach §16.2 und vor §17, in
  `RCC_002_DATA_VALIDATION_2026-07-23.md`.
- Aktualisierung der Dokumentmetadaten (Version, Review-Nachweis-Tabelle)
  desselben Dokuments gemäß Abschnitt 6.

Keine andere Zeile, Tabelle oder Regel in `RCC_002_DATA_VALIDATION` wird
verändert. Kein anderes zertifiziertes Spezifikationsdokument erhält
inhaltliche Änderungen — nur die in Abschnitt 6 gelisteten mechanischen
Versionszitat-Aktualisierungen.

---

## 6. Korrekturbündel- und Versionsvorschlag

### 6.1 Versionsvorschlag

| Dokument | Aktuell | Vorschlag | Klasse | Begründung |
|---|---|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.7.1` | `0.7.1` (unverändert) | — | Zitiert `RCC-002-DV` nicht (Wurzel der Abhängigkeitskette) |
| `RCC_002_DATA_VALIDATION` | `0.4.2` | `0.5.0` | **Minor** | Additive, normativ neue Inhalte (Severity-Register), die eine bereits bestehende Pflichtangabe (§16.2, §24.1 Nr. 3) vervollständigen, ohne bestehende Semantik zu verändern — gleiche Einstufungslogik wie zuvor bei Reproducibility §8.7.1/§18.4 (0.6.0 → 0.7.0) angewandt |
| `RCC_002_INDICATOR_SPECIFICATION` | `0.4.3` | `0.4.3` (unverändert) | Zitat-Fix | Nur Aktualisierung der `RCC-002-DV`-Versionsangabe im Kopf |
| `RCC_002_SIGNAL_TRANSFORMATION` | `0.4.2` | `0.4.2` (unverändert) | Zitat-Fix | Wie oben |
| `RCC_002_REGIME_AND_GATE_SPECIFICATION` | `0.5.1` | `0.5.1` (unverändert) | Zitat-Fix | Wie oben |
| `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION` | `0.4.1` | `0.4.1` (unverändert) | Zitat-Fix | Wie oben |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST` | `0.7.1` | `0.7.2` | **Patch** | Mechanische Aktualisierung von Kopfzeile („Fachliche Abhängigkeiten") und §12.3-Tabelle auf `RCC-002-DV` `0.5.0`; gleiche Einstufung wie beim vorangegangenen Korrekturzyklus (`0.7.0` → `0.7.1`) |

Die Einordnung als **Minor** statt **Patch** für `RCC_002_DATA_VALIDATION`
folgt derselben Regel wie in `RCC_002_DATA_PIPELINE_SPECIFICATION` §6.4
(„Minor: additive … ohne Änderung bestehender Semantik") bereits in diesem
Projekt angewandt.

### 6.2 Betroffene Zitatstellen (mechanisch zu aktualisieren)

| Dokument | Zeile/Stelle | Alt | Neu |
|---|---|---|---|
| `RCC_002_INDICATOR_SPECIFICATION` | Kopfzeile „Direkte Abhängigkeit" | `RCC_002_DATA_VALIDATION…, Version 0.4.2` | `…, Version 0.5.0` |
| `RCC_002_SIGNAL_TRANSFORMATION` | Kopfzeile „Direkte Abhängigkeiten" | `…Version 0.4.2` (DV-Anteil) | `…Version 0.5.0` |
| `RCC_002_REGIME_AND_GATE_SPECIFICATION` | Kopfzeile „Direkte Abhängigkeiten" | `…Version 0.4.2` (DV-Anteil) | `…Version 0.5.0` |
| `RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION` | Kopfzeile „Direkte Abhängigkeiten" | `…Version 0.4.2` (DV-Anteil) | `…Version 0.5.0` |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST` | Kopfzeile „Fachliche Abhängigkeiten" | `…Version 0.4.2` (DV-Anteil) | `…Version 0.5.0` |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST` | §12.3-Tabelle, Zeile `RCC-002-DV` | `0.4.2` | `0.5.0` |

### 6.3 Downstream-Wirkung auf die `rcc002`-Implementierung (nur zur Kenntnis — nicht jetzt umzusetzen)

- `rcc002/s0/integrity.py`: `TruncationFinding.severity` müsste im
  Standardfall (bisher `None`) künftig `"ERROR"` liefern.
- `tests/rcc002/s0/test_integrity.py::test_severity_unspecified_without_upstream_evidence`
  müsste entsprechend angepasst werden.
- Für Schritt 4 (S2) wird ein zentrales Severity-Register-Modul empfohlen,
  das §16.3 direkt abbildet; die bestehenden lokalen `critical`-Flags in
  `rcc002/s1/numeric.py` sind mit den hier vorgeschlagenen Werten für
  `DV_PARSE_NUMERIC_FAILED`/`DV_PARSE_TIMESTAMP_FAILED` bereits konsistent
  und müssten nicht rückwirkend geändert werden, sollten aber aus diesem
  zentralen Modul beziehen, um künftiges Auseinanderlaufen zu vermeiden.

Keine dieser Codeänderungen wird in diesem Schritt vorgenommen.

### 6.4 Ablauf der Bündelerstellung (vorgesehen, noch nicht ausgeführt)

1. Freigabeentscheidung zu Abschnitt 1 (ggf. mit Korrekturen an den vier in
   Abschnitt 4 markierten Einzelfällen).
2. Einfügung von §16.3 in `RCC_002_DATA_VALIDATION_2026-07-23.md`;
   Versionsfeld und Review-Nachweis-Tabelle aktualisieren (neue Zeile:
   „Reason-Code-Severity-Korrekturzyklus — `RCC-002-DVSEV-001` umgesetzt,
   Version 0.5.0, 2026-07-27").
3. Mechanische Zitataktualisierung in den fünf in Abschnitt 6.2 gelisteten
   Dokumenten; Versionsfeld von `RCC_002_REPRODUCIBILITY_AND_MANIFEST` auf
   `0.7.2`.
4. Neuerstellung von Bündel und Manifest unter einem neuen Dateipaar
   (Namenskonvention konsistent mit `RCC_002_C1_CORRECTED_FULL_SPEC_BUNDLE`
   / `RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE`, z. B.
   `RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_<Datum>.md` und zugehöriges
   `..._MANIFEST_<Datum>.md`).
5. Unabhängige Hash-Neuberechnung, Byte-exakter Round-Trip-Rebuild.
6. Gezielter (nicht vollumfänglicher) Re-Review, beschränkt auf: (a)
   Konsistenz von §16.3 mit allen zitierten Bestandsregeln; (b)
   vollständige, eindeutige Berechenbarkeit von `quality_status` und
   `quality_gate_pass` für alle 32 Codes; (c) Bestätigung, dass die vier in
   Abschnitt 4 markierten Einzelfälle explizit geprüft wurden.
7. Erst danach: Fortsetzung der Implementierung von Schritt 4 (S2) unter
   Verwendung des freigegebenen Registers.

---

Dieser Vorschlag ist zur Prüfung vorgelegt. Keine Datei außerhalb dieses
neuen Dokuments wurde erstellt oder verändert; die zertifizierte
Spezifikation, alle abhängigen Spezifikationsdokumente und der gesamte
`rcc002`-Implementierungscode bleiben unverändert.
