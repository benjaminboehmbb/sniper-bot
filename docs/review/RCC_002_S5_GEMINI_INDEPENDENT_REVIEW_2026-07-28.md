# Unabhängiger Zweitprüfer-Bericht: Scientific-Consistency-, Architecture-Integrity- und Implementation-Review der RCC-002 S5-Implementierung

**Reviewer:** Gemini (Independent Scientific & Architecture Auditor)  
**Datum:** 28. Juli 2026  
**Prüfgegenstand:** Paket `RCC_002_S5_INDEPENDENT_REVIEW_PACKAGE_2026-07-28.zip`  
**Prüfgrundlage:** Zertifizierte Spezifikation, Manifest und Certification Decision (normative Dokumentensuite 2026-07-27)  

---

## Executive Summary & Independent Findings Matrix

Als unabhängiger Zweitprüfer wurde eine vollständige, source-basierte Evaluierung der RCC-002 S5-Regime-Implementierung durchgeführt. Die Review basiert exklusiv auf der normativ zertifizierten Spezifikation (einschließlich des zertifizierten Spec-Bundles `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee` und des Manifests). Readiness-Reviews und Implementation Records wurden gemäß Prüfauftrag bewusst ignoriert.

### Übersicht der Findings

| Finding ID | Kategorie | Datei / Funktion | Normative Verletzung | Auswirkung |
| :--- | :--- | :--- | :--- | :--- |
| **FIND-S5-CRIT-01** | **CRITICAL** | `rcc002/s5/compute.py` (`compute_regimes`) | Verletzung der kanonischen Row-Preservation & Unveränderlichkeits-Garantie (S3/S4 Passthrough) | **In-Place-Mutation von Quell-Dictionaries:** `_copy_s4_values` reicht verschachtelte mutable Dictionaries (`indicators`, `signals`) per Referenz weiter, wodurch Nachfolgestufen vorgelagerte S3/S4-Daten modifizieren können. |
| **FIND-S5-MAJ-01** | **MAJOR** | `rcc002/s5/compute.py` (`compute_regimes`) | Inkonsistente Behandlung von `REG_SEGMENT_RESET` bei Checkpoint-Continuation | Bei Wiederaufnahme eines Zustands nach einem Segment-Reset wird der Reason Code `REG_SEGMENT_RESET` am ersten Folgebalken unterschlagen, wodurch serielle und partitionierte Parität divergierten. |
| **FIND-S5-MIN-01** | **MINOR** | `rcc002/s5/compute.py` (`_context_fields`) | Unvollständige Reason-Code-Priorisierung bei Feld-lokaler Invalidation | Bei Fehler in ADX/ATR-Formeln wird nur der generische Code erzeugt; fehlende Kombination mit `REG_INPUT_INVALID` im lokalen Kontext. |
| **FIND-S5-EDIT-01** | **EDITORIAL** | `rcc002/s5/constants.py` | Redundante String-Konstantendeklarationen | Abweichende Zeilenumbrüche in String-Formattierungen ohne funktionale Auswirkung. |

---

## Detaillierte Befundanalysen

### FIND-S5-CRIT-01 (CRITICAL): Mutable Dictionary Reference Leakage in S4-Passthrough
* **Datei & Funktion:** `rcc002/s5/compute.py`, Funktion `_copy_s4_values` / `compute_regimes`
* **Verletzte normative Regel:** Normatives Row-Preservation-Prinzip (Spezifikation Abs. 5.8 & Abs. 6.3). Nachgelagerte Stufen dürfen vorgelagerte Felder weder im Wert noch in ihren Datenstrukturen verändern oder modifizierbare Referenzen darauf halten.
* **Auswirkung:** `_copy_s4_values(row)` führt ein flaches Unpacking/Copying der S4Row-Felder durch. Die komplexen Attribute `indicators` (aus S3) und `signals` (aus S4) sind Python-`dict`-Objekte. Durch die flache Kopie verweisen die erzeugten `S5Row`-Instanzen auf dieselben Heap-Dictionaries wie die Eingabe-`S4Row`. Wenn ein Konsument von `S5Row.signals` oder `S5Row.indicators` eine Mutation vornimmt (z. B. `row.signals["sig_rsi_mr_d"] = ...`), wird das vorgelagerte S4/S3-In-Memory-Objekt zerstört. Dies bricht die Unveränderlichkeits-Invariante der Pipeline.
* **Erforderliche Korrektur:** In `_copy_s4_values` bzw. in der Schema-Konstruktion von `S5Row` müssen mutable Dictionary-Strukturen tief kopiert (`copy.deepcopy`) oder in unmutierbare Mapping-Proxies (`types.MappingProxyType`) umgewandelt werden.

### FIND-S5-MAJ-01 (MAJOR): Unterdrückung von `REG_SEGMENT_RESET` bei Wiederaufnahme via Checkpoint State
* **Datei & Funktion:** `rcc002/s5/compute.py`, Funktion `compute_regimes` (Zeilen 200–225)
* **Verletzte normative Regel:** S5 State-Continuation & Partition Parity (Abschnitt 8 & Prüfpunkt 8). Partitionierte und serielle Ausführung müssen exakt identische Zeilen-Flags und Reason Codes liefern.
* **Auswirkung:** Wenn ein Chunk über `prior_state` fortgesetzt wird und ein vertrauenswürdiger Segmentwechsel vorliegt (`accepted=False`, `trusted_segment_boundary=True`), wird `initial_segment_reset` gesetzt. Die Schleife setzt bei `index == 0` zwar `segment_reset = True`, fügt `REG_SEGMENT_RESET` jedoch in bestimmten Fallback-Verzweigungen nicht deterministisch in `regime_reason_codes` ein, falls gleichzeitig ein Input-Fehler vorliegt. Dadurch unterscheidet sich die Reason-Code-Liste der partitionierten Ausführung von einem seriellen Durchlauf über das gesamte Segment.
* **Erforderliche Korrektur:** Die Flag-Evaluierung für `REG_SEGMENT_RESET` muss strikt unabhängig von nachfolgenden Input-Gültigkeitsprüfungen an den Anfang der Reason-Code-Akkumulation gestellt werden.

### FIND-S5-MIN-01 (MINOR): Unvollständige Reason-Code-Kombination in `_context_fields`
* **Datei & Funktion:** `rcc002/s5/compute.py`, Funktion `_context_fields`
* **Verletzte normative Regel:** Kontextgültigkeit & Reason-Code-Priorisierung (Spezifikation Abs. 7.6 & Prüfpunkt 6/7).
* **Auswirkung:** Wenn `adx_wilder_14` ungültig ist, wird ausschließlich `REG_TREND_STRENGTH_INPUT_INVALID` zugewiesen. Zwar ist dies feld-lokal korrekt, jedoch sollte bei vorgelagerten Schema-/Gate-Fehlern die direkte Herkunft dokumentiert werden.
* **Erforderliche Korrektur:** Harmonisierung der Kontext-Reason-Codes mit der Prioritäten-Matrix aus `REASON_CODE_REGISTRY`.

---

## Prüfpunkte-Evaluierung (12/12 Punkte)

### 1. Exaktes S5-Schema & S4-Durchleitung
* **Status:** PASS (mit Minor Finding CRIT-01 bezüglich Dictionaries)
* **Analyse:** `S5Row` erweitert `S4Row` um exakt 21 kanonische Felder in der normierten Reihenfolge (`regime_raw` bis `regime_reason_codes`). Alle S4-Basis- und Metadatenfelder werden vollständig durchgereicht.

### 2. SMA200-Slope über exakt 1.440 Minuten
* **Status:** PASS
* **Analyse:** Die Formel $100 \times \left(\frac{\text{SMA200}_t}{\text{SMA200}_{t-1440}} - 1\right)$ ist in `rcc002/s5/formulas.py` exakt umgesetzt. Operationsreihenfolge (Division, Subtraktion von 1.0, Multiplikation mit 100.0) und Behandlungslogik für unvollständigen Warm-up ($< 1.440$ Balken im Kontext) entsprechen der Spezifikation.

### 3. Vollständige Rohregime-Wahrheitstabelle
* **Status:** PASS
* **Analyse:** Die Klassifikation in `classify_raw_regime` hält die normative Wahrheitstabelle strikt ein:
  * `BULL`: $\text{Close} > \text{SMA200}$ UND $\text{Slope} > 0.0$
  * `BEAR`: $\text{Close} < \text{SMA200}$ UND $\text{Slope} < 0.0$
  * `SIDE`: Alle übrigen gütigen Fälle (inkl. Vorzeichen-Symmetrien an $0.0$)
  * `UNKNOWN`: Bei ungültigem Input/Slope.

### 4. Persistierte Drei-Balken-Zustandsmaschine
* **Status:** PASS
* **Analyse:** `_advance_confirmation` steuert den Übergang akkurat:
  * Sättigung des Candidate-Counters bei exakt 3 Balken.
  * Sofortiger Reset des Counters auf 1 bei Candidate-Wechsel.
  * Bei `RegimeState.UNKNOWN` Übergang des effektiven Regimes auf `UNKNOWN` unter Setzen der Transition-Flags.

### 5. Nullbarkeit und Konsistency der Transition-Felder
* **Status:** PASS
* **Analyse:** `regime_transition_from` und `regime_transition_to` sind genau dann ungleich `None`, wenn `regime_transition_flag == True` ist. Die Invariantenprüfung in `S5Row.__post_init__` erzwingt dies strikt.

### 6. Feldbezogene Kontextgültigkeit für ADX und ATR
* **Status:** PASS
* **Analyse:** `trend_strength` (ADX) und `volatility_relative` (ATR) besitzen eigene `_valid`-Flags und `_reason_codes`-Tupel. Ein ungültiger ADX-Wert entwertet nur das `trend_strength`-Feld, beeinflusst jedoch nicht das Hauptregime (und umgekehrt).

### 7. Reason-Code-Ziele & Prioritäten
* **Status:** PASS
* **Analyse:** Das Register umfasst exakt 10 Codes mit aufsteigenden Prioritäten (30 bis 120). Die Normalisierung (`normalize_reason_codes`) dedupliziert und sortiert deterministisch.

### 8. State-Snapshot, Canonical JSON & Parität
* **Status:** PASS (mit Major Finding MAJ-01)
* **Analyse:** `RegimeStateSnapshot` erzeugt einen deterministischen SHA-256-Checksummen-Hash über ein sortiertes Canonical-JSON-Payload (separators `,` und `:`). Manipulierte Checksummen führen zur Ablehnung des Prior-State (`prior_state_accepted=False`).

### 9. Kausalität & Reproduzierbarkeit
* **Status:** PASS
* **Analyse:** Keine Zukunfts-Sichtung (No-Lookahead). Erweitere Testserien verändern historische Prefix-Ergebnisse nicht. Row-Preservation bezüglich Zeilenanzahl ist gegeben.

### 10. Stage-weite Vertragsablehnung vs. zeilenweises UNKNOWN
* **Status:** PASS
* **Analyse:** Schema-Mismatches, ungültige Intervalle oder Symbol-Mischungen führen zu sofortigen Exceptions (`ValueError`/`TypeError`) auf Stage-Ebene. Qualitatsgate-Fehler einzelner Zeilen führen zu zeilenweisem `RegimeState.UNKNOWN` mit `REG_INPUT_QUALITY_GATE_FAILED`.

### 11. Testabdeckung & Grenzfälle
* **Status:** PASS
* **Analyse:** Die Unit-Tests in `tests/rcc002/s5/` decken Golden-Path-, Warm-up-, Transition-, Denominator-Zero- und Checksum-Tampering-Fälle gut ab.

### 12. Verbotene Logik (S6/Gate/Strategy/Return/Barrier)
* **Status:** PASS
* **Analyse:** Der S5-Code enthält keinerlei Freigabelogik (`allow_long`, `allow_short`), Strategie-Parameter, Barrier-Evaluierungen oder Forward-Return-Berechnungen. Die Modulgrenzen sind strikt gewahrt.

---

## Abschlussentscheidung

Aufgrund des kritischen Befunds **FIND-S5-CRIT-01** (Mutable Reference Leakage vorgelagerter S3/S4 Data-Structures) sowie des Major-Befunds **FIND-S5-MAJ-01** lautet das finale Prüfurteil:

**REJECTED**

---
*Anmerkung:* Gemäß der Guardrails und Anweisungen wurden keine Dateien im Prüfpaket modifiziert und keine Korrekturen direkt im Quellcode angewendet. Dieser Bericht wurde unter dem vorgeschriebenen Dateinamen `RCC_002_S5_GEMINI_INDEPENDENT_REVIEW_2026-07-28.md` gerendert.
