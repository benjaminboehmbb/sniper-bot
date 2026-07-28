# RCC-002 S5 Claude Corrected Re-Review

| Feld | Wert |
|---|---|
| Dokumentklasse | Fokussierte unabhängige Re-Review (Correction Verification) |
| Geltungsbereich | `S4_SIGNALS -> S5_REGIMES` (`rcc002/s5/*`, `tests/rcc002/s5/*`) |
| Reviewer | Claude (Sonnet 5), unabhängig |
| Datum | 2026-07-28 |
| Reviewpaket | `/tmp/rcc002-s5-claude-rereview-20260728` (entpackt) |
| Vorherige Reviews | `RCC_002_S5_CLAUDE_INDEPENDENT_REVIEW_2026-07-28.md` (eigene Erstreview, CLD-S5-001…005); `RCC_002_S5_GEMINI_INDEPENDENT_REVIEW_2026-07-28.md` (FIND-S5-CRIT-01, MAJ-01, MIN-01, EDIT-01); beide als Evidenz-Input behandelt, nicht als normative Autorität |
| Normative Grundlage | `RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` (unverändert, SHA-256 identisch zur Erstreview verifiziert), Bundle-Manifest, Certification Decision, zusätzlich `RCC_002_S5_IMPLEMENTATION_READINESS_REVIEW_2026-07-28.md` §§10.1/10.4 gemäß explizitem Auftrag |
| Methodik | Diff der gesamten `rcc002/s5/`- und `tests/rcc002/s5/`-Bäume gegen die Erstreview-Kopie; erneute vollständige Testausführung; unabhängige Live-Reproduktion aller drei strittigen Verhaltensweisen (Segmentgrenze nach bestätigtem Regime, Container-Aliasing, `REG_EFFECTIVE_UNCONFIRMED`-Grenzfälle) direkt am Code, nicht nur am Diff |

## 0. Integrität und Testausführung

- Diff der normativen Dokumente (`RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`, Certification Decision, Implementation Readiness Review) gegen die Erstreview-Kopie: **keine Abweichung** — die normative Grundlage ist unverändert.
- `sha256sum -c docs/review/RCC_002_S5_CORRECTED_RE_REVIEW_SHA256SUMS_2026-07-28.txt` im Reviewpaket: **alle 34 Einträge OK**, unabhängig nachgerechnet.
- Eigene Testausführung (nicht nur Behauptung übernommen):
  ```
  python -m unittest discover -s tests/rcc002/s5 -p "test_*.py"   -> Ran 69 tests, OK
  python -m unittest discover -s tests/rcc002    -p "test_*.py"   -> Ran 475 tests, OK
  ```
  Deckt sich exakt mit Abschnitt 4 der `INDEPENDENT_REVIEW_RESOLUTION`.
- Diff zeigt: genau zwei funktionale Codeänderungen (`compute.py`) plus ein Kommentar (`constants.py`); `schema.py`, `state.py`, `formulas.py`, `reason_codes.py`, `__init__.py` sind **byte-identisch** zur Erstreview-Fassung.

## 1. Korrektur `REG_EFFECTIVE_UNCONFIRMED` gegen §12.7.1

**Diff** (`rcc002/s5/compute.py:421-426`):
```diff
- if effective is RegimeState.UNKNOWN:
+ if (
+     raw is not RegimeState.UNKNOWN
+     and effective is RegimeState.UNKNOWN
+ ):
      reasons.append("REG_EFFECTIVE_UNCONFIRMED")
```

Spezifikationswortlaut §12.7.1: *"`REG_EFFECTIVE_UNCONFIRMED`, solange **ein gültiger Rohzustand** noch keinen ersten effektiven Zustand bestätigt hat"* — die Korrektur bindet den Code jetzt exakt an die im Wortlaut genannte Vorbedingung (`raw` gültig) UND die Nachbedingung (`effective` noch nicht bestätigt). Das ist eine präzise, minimale Korrektur ohne Nebenwirkungen auf andere Reason Codes.

**Live-Verifikation (eigener Lauf, nicht nur Test übernommen):**
```
Index 0 (raw=UNKNOWN, Warm-up):     reasons = ('REG_WARMUP_INCOMPLETE',)              # kein EFFECTIVE_UNCONFIRMED mehr
Index 1439 (raw=UNKNOWN, Warm-up):  reasons = ('REG_WARMUP_INCOMPLETE',)              # kein EFFECTIVE_UNCONFIRMED
Index 1440 (raw=SIDE, unbestätigt): reasons = ('REG_EFFECTIVE_UNCONFIRMED',)          # korrekt vorhanden
```
Neue Regressionstests `test_pre_slope_warmup` (assertNotIn) und `test_first_slope_is_at_index_1440` (assertIn) fixieren exakt diese Grenze. **CLD-S5-002 ist vollständig und korrekt behoben.**

## 2. Trennung der S5-Dictionary-Container von den S4-Containern

**Diff** (`rcc002/s5/compute.py:70-79`, `_copy_s4_values`):
```diff
- return {name: getattr(row, name) for name in _S4_FIELD_NAMES}
+ values = {name: getattr(row, name) for name in _S4_FIELD_NAMES}
+ values["indicators"] = dict(row.indicators)
+ values["signals"] = dict(row.signals)
+ return values
```

**Prüfung der Vollständigkeit:** `indicators` (`S3Row`) und `signals` (`S4Row`) sind die *einzigen* `dict`-typisierten Felder in der gesamten `S3Row`/`S4Row`-Vererbungskette (verifiziert per Grep über `rcc002/s3/schema.py` und `rcc002/s4/schema.py`); beide enthalten ausschließlich `frozen`-Dataclass-Werte (`IndicatorField`, `SignalField`), sodass eine flache Kopie (kein `deepcopy` nötig) genügt, um Container-Aliasing vollständig zu unterbinden.

**Live-Verifikation, Vorher/Nachher:**
```
Altes Paket:  out.indicators is source.indicators -> True   (Aliasing bestätigt reproduzierbar)
Neues Paket:  out.indicators is source.indicators -> False
              out.indicators.clear(); out.signals.clear()
              source.indicators weiterhin populiert: True
              source.signals weiterhin populiert:    True
```
Der neue Regressionstest `test_output_dictionaries_do_not_alias_upstream` prüft exakt dieses Verhalten. **Der von Gemini als FIND-S5-CRIT-01 gemeldete Effekt war real und ist jetzt vollständig behoben.**

*Anmerkung zur Einordnung:* Gemini zitierte §5.8 ("Row-Preservation-Prinzip") als verletzte Regel. Bei eigener Lektüre von §5.8 im Bundle stellt sich heraus, dass §5.8 ausschließlich das Nicht-Entfernen/-Zusammenführen/-Umordnen von **Zeilen** regelt, nicht die Speicherreferenz-Semantik von In-Memory-Python-Objekten zwischen Pipeline-Stufen. Eine textlich exakt einschlägige Normklausel für Heap-Referenzidentität existiert im Bundle nicht (auch §5.5 "Unveränderlichkeit und Lineage" adressiert veröffentlichte Artefakte, nicht Prozess-interne Objektreferenzen). Die Reklassifizierung von CRITICAL auf **MINOR** in der Resolution ist daher nach dem in diesem Reviewprozess verlangten strikt textbasierten Maßstab (jeder Befund braucht eine zitierbare Spezifikationsregel) nachvollziehbar; der Befund selbst war unabhängig von der Einstufung sachlich korrekt und die Korrektur ist vollständig.

## 3. Neue Regressionstests

| Test | Datei:Zeile | Prüft |
|---|---|---|
| `test_output_dictionaries_do_not_alias_upstream` | `test_compute.py:50-60` | Container-Nichtaliasing (Punkt 2) |
| `test_pre_slope_warmup` (erweitert) | `test_compute.py:62-68` | `REG_EFFECTIVE_UNCONFIRMED` **fehlt** während reinem Warm-up |
| `test_first_slope_is_at_index_1440` (erweitert) | `test_compute.py:70-77` | `REG_EFFECTIVE_UNCONFIRMED` **vorhanden** bei gültigem, aber unbestätigtem Rohregime |
| `test_partition_at_segment_boundary_matches_serial` (erweitert) | `test_compute.py:264-273` | Segmentgrenze nach bestätigtem `SIDE`: `transition_flag=True`, `from=SIDE`, `to=UNKNOWN` — genau der in CLD-S5-001 beanstandete Fall, jetzt explizit als Sollverhalten fixiert |
| `test_segment_reset_is_reported_once` (erweitert) | `test_compute.py:320-326` | Segmentgrenze **ohne** je bestätigtes Regime: `transition_flag=False`, `from=to=None` — das explizite Gegenstück aus §9.6 Satz 3 |

Alle fünf Tests wurden von mir unabhängig gegen den Live-Code nachvollzogen (nicht nur gelesen), inklusive eines selbst konstruierten Zusatzfalls (Segmentwechsel *gleichzeitig* mit `quality_gate_pass=false` auf derselben Zeile, siehe Abschnitt 5, FIND-S5-MAJ-01) außerhalb der vorhandenen Testsuite. Die Tests sind präzise, minimal und testen exakt die zuvor strittigen Grenzen — keine Overfitting-Symptome (z. B. keine Tests, die nur den aktuellen Codepfad ohne Bezug zu einer konkreten Spezifikationsregel abbilden).

## 4. Independent Review Resolution gegen den exakten normativen Wortlaut

### 4.1 CLD-S5-001 — Resolution: "Not confirmed / rejected". Eigene Neubewertung: **Ich schließe mich der Zurückweisung an; mein ursprünglicher Befund war unzutreffend.**

Erneute Lektüre von §9.6 (vollständiger Wortlaut, wie vom Auftraggeber zitiert):

> „Der Wechsel eines zuvor gültigen effektiven Zustands nach UNKNOWN ist ein tatsächlicher Übergang und wird mit `transition_to=UNKNOWN` protokolliert. Der erstmalige bestätigte Wechsel von UNKNOWN nach BULL, SIDE oder BEAR wird ebenfalls protokolliert. Am Segmentanfang mit vorherigem und aktuellem Zustand UNKNOWN liegt kein Übergang vor. Ohne Wechsel gilt: `regime_transition_flag = false`, From und To sind null."

Die Textstruktur ist: (a) eine **allgemeine Regel** ohne Ausnahme für Segmentgrenzen ("ein zuvor gültiger effektiver Zustand nach UNKNOWN ist ein tatsächlicher Übergang"), gefolgt von (b) einer **eng gefassten, expliziten Ausnahme** ausschließlich für den Fall, dass der vorherige Zustand *bereits* UNKNOWN war. Wäre beabsichtigt gewesen, jede Segmentgrenze unconditional von der Übergangsprotokollierung auszunehmen, wäre die spezifische Formulierung "mit vorherigem **und aktuellem** Zustand UNKNOWN" überflüssig — es hätte genügt zu sagen "am Segmentanfang liegt nie ein Übergang vor". Diese Textökonomie spricht eindeutig gegen meine ursprüngliche Lesart.

§9.3 ("Am Segmentanfang: `regime_effective = UNKNOWN`") und §27.1 ("persistierte State Machine wird zurückgesetzt") pinnen den **Zustandswert** am Segmentanfang und das **laufende, in die Zukunft wirkende** Verhalten des Mechanismus (Candidate/Count/Effective für alle Folgezeilen). Beides ist erfüllt: `regime_effective` der Grenzzeile selbst ist korrekt `UNKNOWN`, und `regime_candidate`/`regime_candidate_count` werden korrekt auf `UNKNOWN`/`0` zurückgesetzt (live verifiziert). Die einmalige historische Übergangsannotation auf exakt dieser einen Zeile (`regime_transition_from`) ist kein fortwirkender State, der künftige Zeilen beeinflusst — sie ist ein terminaler Audit-Eintrag, der mit einem "Reset" des Mechanismus nicht in Widerspruch steht.

**Live-Nachvollzug beider Halbfälle von §9.6, Satz 1 und Satz 3, im korrigierten Code:**
```
Fall A — Segmentgrenze NACH bestätigtem SIDE:
  effective(vorher)=SIDE -> Grenzzeile: flag=True, from=SIDE, to=UNKNOWN   [§9.6 Satz 1: "tatsächlicher Übergang"]

Fall B — Segmentgrenze OHNE je bestätigtes Regime (erste 3 Zeilen der Serie):
  effective(vorher)=UNKNOWN -> Grenzzeile: flag=False, from=None, to=None [§9.6 Satz 3: "kein Übergang"]
```
Beide Fälle sind jetzt explizit regressionsgetestet (Abschnitt 3). **Ich nehme CLD-S5-001 hiermit zurück.** Die ursprüngliche Einstufung als CRITICAL beruhte auf einer zu starken Gewichtung von §9.3/§27.1 gegenüber der spezifischeren, unmittelbar einschlägigen Regel in §9.6. Empfehlung (rein editorisch, keine Code-Korrektur): §9.6 oder §27 um ein ausgearbeitetes Beispiel für genau diesen Fall ("bestätigtes Regime unmittelbar vor einer Segmentgrenze") ergänzen, um diese Auslegungsfrage für künftige unabhängige Reviews dauerhaft zu schließen.

### 4.2 CLD-S5-003 — Resolution: "Not confirmed / rejected". Eigene Neubewertung: **Zurückweisung nachvollzogen und akzeptiert.**

Die Erstreview hatte §10.4 der Implementation Readiness Review nicht vollständig erfasst (Lektüre endete bei §10.3). Nachlese in diesem Reviewpaket:

> „§10.4 State hash: `state_payload_sha256` is lowercase SHA-256 over UTF-8 canonical JSON of **all snapshot fields** except `state_payload_sha256`."

kombiniert mit §10.1, die `state_profile_id`, `state_profile_version`, `state_hash_profile_id`, `state_hash_profile_version` explizit als Teil der State-Identität registriert. Da §28.1 der zertifizierten Spezifikation den Snapshot-Feldsatz ausdrücklich als Minimum ("enthält mindestens") definiert und §6.3 des Data-Pipeline-Dokuments profilgebundene Erweiterungsfelder zulässt, sofern Feldname, Typ/Nullbarkeit, Erzeugerstufe und Profil/Version registriert sind — was für alle vier Zusatzfelder zutrifft (eigene Profil-IDs `RCC002_S5_SMA200_CONTEXT_V1` / `RCC002_S5_STATE_HASH_V1`, jeweils Version `1.0.0`, in `constants.py` registriert) — ist die Einbeziehung dieser Felder in die Hash-Nutzlast eine legitime, vor der Implementierung getroffene Konkretisierung eines von der Spezifikation offen gelassenen Parameters, nicht ein eigenmächtiger Normverstoß. Ich akzeptiere diese Auflösung.

*Verbleibende, nicht blockierende Empfehlung:* Die zertifizierte Spezifikation selbst (§28.2) verweist bislang nicht auf diese Konkretisierung. Eine unabhängige Drittimplementierung, die ausschließlich das zertifizierte Bundle liest (ohne Kenntnis der Readiness Review), könnte diese Entscheidung nicht reproduzieren. Empfehlung: In einer künftigen Spezifikationsrevision §28.2 um einen Verweis auf die registrierten Profile `RCC002_S5_SMA200_CONTEXT_V1`/`RCC002_S5_STATE_HASH_V1` und die Hash-Scope-Regel ergänzen. Kein Blocker für diese Implementierung.

### 4.3 Gemini FIND-S5-MAJ-01 ("REG_SEGMENT_RESET wird unterdrückt") — Resolution: "Not confirmed / rejected". Eigene Neubewertung: **Zurückweisung bestätigt, selbst nachgeprüft.**

Eigener Test außerhalb der vorhandenen Suite: Zeile mit **gleichzeitigem** Segmentwechsel und `quality_gate_pass=false`:
```
reasons = ('REG_INPUT_QUALITY_GATE_FAILED', 'REG_WINDOW_CROSSES_INDICATOR_SEGMENT', 'REG_SEGMENT_RESET')
```
`REG_SEGMENT_RESET` bleibt in jeder untersuchten Kombination erhalten; die Reason-Liste in `compute.py` ist eine reine Akkumulationsstruktur (`list.append`/`list.extend`), kein Code-Pfad entfernt bereits hinzugefügte Codes. Die Behauptung einer Unterdrückung ist am Code nicht nachvollziehbar.

### 4.4 Gemini FIND-S5-MIN-01 ("Kontext-Reason-Codes sollten mit REG_INPUT_INVALID kombiniert werden") — Resolution: "Not confirmed / rejected". Eigene Neubewertung: **Zurückweisung bestätigt.**

§12.7.2 verlangt wörtlich "ausschließlich" (`trend_strength_reason_codes` enthält *ausschließlich* `REG_TREND_STRENGTH_INPUT_INVALID`; `volatility_relative_reason_codes` *ausschließlich* `REG_VOLATILITY_INPUT_INVALID`). Eine Beimischung von `REG_INPUT_INVALID` wäre eine direkte Verletzung dieser Exklusivitätsregel und würde zudem gegen die in Prüfpunkt 7 der Erstreview bestätigte Zieltrennung verstoßen. Gemini's eigener Vorschlag steht im Widerspruch zum Spezifikationswortlaut, den er selbst zitiert.

### 4.5 Gemini FIND-S5-EDIT-01 — kein Handlungsbedarf, bestätigt.

## 5. Alle ursprünglichen Claude-Befunde CLD-S5-001 bis CLD-S5-005

| ID | Ursprüngliche Einstufung | Resolution-Status | Eigene Neubewertung |
|---|---|---|---|
| CLD-S5-001 | CRITICAL | Not confirmed | **Zurückgenommen** — §9.6 trägt die aktuelle Implementierung; beide Halbfälle jetzt regressionsgetestet |
| CLD-S5-002 | MINOR | Confirmed, korrigiert | **Bestätigt behoben**, live verifiziert |
| CLD-S5-003 | MINOR | Not confirmed | **Zurückweisung akzeptiert** unter Berücksichtigung von Readiness-Review §§10.1/10.4; nur editorische Restempfehlung an die Spezifikation |
| CLD-S5-004 | EDITORIAL | Accepted, Kommentar ergänzt | **Bestätigt erledigt** |
| CLD-S5-005 | EDITORIAL (Prozesshinweis) | Accepted, Checksummen-Manifest ergänzt | **Bestätigt erledigt** — Manifest selbst unabhängig nachgerechnet (Abschnitt 0) |

## 6. Verbleibender CRITICAL-/MAJOR-Befund?

**Nein.** Nach vollständiger, eigenständiger Nachprüfung aller sechs Claude- und vier Gemini-Befunde sowie einer erneuten, wortlautgenauen Prüfung aller zwölf ursprünglichen Prüfpunkte (Schema/Feldreihenfolge, Slope-Formel, Wahrheitstabelle, State-Machine/Übergänge inkl. Segmentgrenze, Nullbarkeit, Kontextgültigkeit, Reason-Code-Registry, State-Snapshot/Hash/Parität, S4-Erhaltung, Fail-Closed-Ablehnung, Testabdeckung, S6-Ausschluss) besteht kein offener CRITICAL- oder MAJOR-Befund mehr:

- Der einzige tatsächlich reale CRITICAL-Befund (Gemini FIND-S5-CRIT-01, Container-Aliasing) ist vollständig behoben und regressionsgetestet.
- Der einzige tatsächlich reale MINOR-Befund mit Korrekturbedarf (CLD-S5-002) ist vollständig behoben und regressionsgetestet.
- Der ursprüngliche CRITICAL-Befund CLD-S5-001 hält der erneuten, durch §9.6 geschärften Prüfung nicht stand und wird zurückgenommen.
- CLD-S5-003 ist durch eine legitime, spezifikationskonforme Vorimplementierungs-Konkretisierung (Readiness Review §§10.1/10.4) abgedeckt.
- Gemini FIND-S5-MAJ-01 und FIND-S5-MIN-01 sind am Code widerlegt.

Alle 475 Tests der `rcc002`-Suite (inkl. 69 S5-spezifischer Tests) laufen fehlerfrei; keine Datei wurde im Rahmen dieser Re-Review verändert.

## Abschlussentscheidung

**APPROVED**

Begründung: Beide tatsächlich bestätigten Implementierungsmängel (Container-Aliasing, überbreite `REG_EFFECTIVE_UNCONFIRMED`-Anwendung) sind mit minimalen, präzisen Codeänderungen behoben und durch neue, gezielte Regressionstests dauerhaft abgesichert. Der schwerwiegendste ursprüngliche Befund (CLD-S5-001) erweist sich bei erneuter, durch den expliziten Verweis auf §9.6 geschärfter Lektüre als korrekte, spezifikationskonforme Implementierung; die Rücknahme wurde unabhängig am Code für beide in §9.6 genannten Fälle nachvollzogen. CLD-S5-003 ist durch eine im Rahmen des dokumentierten, mehrstufigen Governance-Prozesses dieses Projekts legitime Vorimplementierungsentscheidung gedeckt. Es verbleiben ausschließlich zwei nicht blockierende editorische Empfehlungen an die Spezifikationsdokumentation selbst (§9.6/§27 um ein Beispiel ergänzen; §28.2 auf die registrierten State-/Hash-Profile verweisen) — keine, die eine Korrektur der Implementierung erfordern.
