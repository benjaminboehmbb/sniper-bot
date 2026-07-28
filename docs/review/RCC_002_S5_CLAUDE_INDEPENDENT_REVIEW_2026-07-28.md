# RCC-002 S5 Claude Independent Review

| Feld | Wert |
|---|---|
| Dokumentklasse | Independent Architecture / Specification / Implementation Review |
| Geltungsbereich | `S4_SIGNALS -> S5_REGIMES` (`rcc002/s5/*`, `tests/rcc002/s5/*`) |
| Reviewer | Claude (Sonnet 5), unabhängig, ohne Beteiligung an der Implementierung |
| Datum | 2026-07-28 |
| Reviewpaket | `RCC_002_S5_INDEPENDENT_REVIEW_PACKAGE_2026-07-28.zip`, entpackt unter `/tmp/rcc002-s5-claude-review-20260728` |
| Normative Grundlage | `RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` (eingebettetes Dokument 5/7: `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`, v0.5.1, §§1–13, 26–31), Bundle-Manifest, DVSEV-001-Zertifizierungsentscheidung |
| Behandlung von Readiness Review / Implementation Record | Ausschließlich als Behauptung; jede Aussage wurde am Quellcode und durch Testausführung unabhängig nachvollzogen |
| Methodik | Vollständige Lektüre von `rcc002/s5/{schema,constants,formulas,reason_codes,state,compute}.py` und `tests/rcc002/s5/*`; Ausführung der Testsuite (`python -m unittest discover -s tests/rcc002/s5`, 68/68 bestanden); gezielte Reproduktion von Grenzfällen außerhalb der vorhandenen Tests gegen den Live-Code |

## 0. Integritätsprüfung (unabhängig nachgerechnet)

- `sha256sum` von `docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md` ergibt `8a6ab7d7...86d9ee`, Zeilenzahl 14070, Bytes 501799 — **identisch** zu Manifest-Abschnitt 1/2. Die zitierte Spezifikationsgrundlage ist unverändert und korrekt referenziert.
- Alle sieben `rcc002/s5/*.py`- und sechs `tests/rcc002/s5/*.py`-Dateien wurden per `sha256sum` gegen die im Implementation Record (Abschnitt 3/4) genannten Prüfsummen verifiziert — **alle identisch**.
- Die im Reviewauftrag genannte Paket-SHA-256 (`22407564...4a04e69de5`) bezieht sich auf die ZIP-Datei selbst; da nur der bereits entpackte Inhalt vorliegt, konnte diese eine Prüfsumme **nicht** unabhängig nachgerechnet werden. Kein Befund daraus, nur Methodik-Hinweis.
- Der lokale Projekt-Checkout (`/home/benja/projects/sniper-bot`) enthält byte-identische Kopien von `rcc002/s3`, `rcc002/s4`, `rcc002/s5` (diff-verifiziert) und eine lauffähige `tests/rcc002`-Baumstruktur mit `.venv`; die Testausführung erfolgte dort, ohne dass eine Datei verändert wurde.

## 1. S4→S5-Schema und Feldreihenfolge (21 Felder)

`rcc002/s5/constants.py:79-101` (`REGIME_EXTENSION_FIELDS`, laufzeitgeprüft `== 21`, `constants.py:182-183`) und die Dataclass-Feldreihenfolge in `rcc002/s5/schema.py:24-45` (`S5Row(S4Row)`, Python-Dataclass-Vererbung garantiert Basisklassenfelder vor eigenen Feldern) stimmen exakt mit Spezifikation §12.2/§12.8 überein:

`regime_raw, regime_effective, regime_candidate, regime_candidate_count, regime_transition_flag, regime_transition_from, regime_transition_to, ma200_slope_1440_pct, trend_strength, trend_strength_valid, trend_strength_reason_codes, volatility_relative, volatility_relative_valid, volatility_relative_reason_codes, regime_model_id, regime_model_version, regime_schema_id, regime_schema_version, regime_schema_ref, regime_valid, regime_reason_codes`

`tests/rcc002/s5/test_schema.py:32-40` prüft dies aktiv gegen `dataclasses.fields(type(row))[-21:]`. S4-Feldreihenfolge wird über `S4Row`-Vererbung strukturell erzwungen, nicht nur behauptet. **Konform.**

## 2. Slope-Formel, Float64-Reihenfolge, 1.440-Minuten-Referenz, Warm-up, Gap/Segment

- `rcc002/s5/formulas.py:32-49`: `ratio = current/reference; offset = ratio - 1.0; result = 100.0 * offset` — exakt die in §6.3 vorgegebene binäre Operationsreihenfolge `100 * (a/b - 1)`. Golden-Value-Test `test_operation_order_golden_value` (`test_formulas.py:37-41`) pinnt das konkrete Float64-Bitmuster.
- Referenzfenster: `rcc002/s5/compute.py:386-395` verwendet `context[0]` als Referenz, `context` wird als gleitendes Fenster von maximal `SLOPE_LOOKBACK_BARS=1440` gültigen SMA200-Werten geführt (`compute.py:457-467`). Empirisch (eigener Testlauf gegen `test_certified_s3_warmup_indices`-Fixture, §8.1–8.3) bestätigt: erster `regime_raw` bei Index 1639, erstes `regime_effective` bei Index 1641 — exakt `199+1440=1639` bzw. `1641` gemäß §8.
- Segmentwechsel setzen `context`, `candidate`, `candidate_count` zurück (`compute.py:350-353`) und erzeugen `REG_WINDOW_CROSSES_INDICATOR_SEGMENT` + `REG_SEGMENT_RESET` (`compute.py:356-362`). Undeklarierte Zeitlücken und deklarierte Gaps ohne Segmentwechsel werden stagewert abgelehnt (`compute.py:143-165`, getestet in `test_declared_gap_without_segment_reset_is_rejected`).
- **Aber:** Der Segment-Reset setzt `effective` nicht zurück — siehe **CLD-S5-001** (kritisch, unten). Dies ist der einzige materielle Mangel in diesem Bereich; Slope-Formel, Fensterbreite und Warm-up-Arithmetik selbst sind korrekt.

## 3. Rohregime-Wahrheitstabelle

`rcc002/s5/formulas.py:52-64` (`classify_raw_regime`) implementiert exakt §7.1–§7.3: `BULL` nur bei `close>sma AND slope>0`, `BEAR` nur bei `close<sma AND slope<0`, sonst `SIDE` (inkl. Gleichheit, Slope=0, gemischtes Vorzeichen). Vollständig abgedeckt in `test_formulas.py:58-83` inkl. aller in §31.1 geforderten Grenzfälle. `UNKNOWN` wird ausschließlich in `compute.py` als Default-Zustand vor erfolgreicher Klassifikation vergeben, nie von `classify_raw_regime` selbst zurückgegeben — Exklusivität (§7.5) ist strukturell garantiert. **Konform.**

## 4. Dreifachbestätigung, Candidate-Sättigung, Übergänge

`_advance_confirmation` (`compute.py:252-294`) implementiert §9.4 korrekt: `new_count = min(count+1,3)` bei gleichem Candidate, sonst Reset auf 1; Übergang nur bei `new_count>=3 AND raw != effective`; die ersten zwei unbestätigten Candidate-Zeilen behalten das alte `effective` (§9.7, per Test `test_post_confirmation_candidate_remains_saturated` und `test_confirmed_bull_to_side_transition` bestätigt). `UNKNOWN`-Raw erzwingt sofortigen Reset ohne Dreifachbestätigung (§9.5), korrekt umgesetzt.

**Jedoch:** Der State-Machine-Reset bei einer echten S2-/S3-Segmentgrenze (§9.3 Initialisierung, §27.1) ist unvollständig — siehe **CLD-S5-001**. Dies betrifft exakt "Übergänge zwischen gültigen Zuständen und UNKNOWN", den in der Aufgabenstellung explizit benannten Prüfpunkt.

## 5. Nullbarkeit/Semantik `regime_transition_from`/`to`

Typisierung (`RegimeState | None`, `schema.py:30-31`) und Validator `_validate_transition` (`schema.py:131-148`) erzwingen korrekt: bei `transition_flag=False` müssen beide `None` sein; bei `True` müssen beide gesetzt, verschieden sein und `transition_to == regime_effective` gelten. Diese *strukturelle* Invariante ist wasserdicht. Das Problem liegt nicht in der Nullbarkeits-/Typmechanik, sondern darin, **wann** ein Übergang überhaupt ausgelöst wird (CLD-S5-001) — die Felder können strukturgültige, aber semantisch falsche Werte tragen.

## 6. Unabhängige TrendStrength-/VolatilityRelative-Gültigkeit

`_context_fields` (`compute.py:204-249`) berechnet beide Felder unabhängig vom Regimezustand; `trend_strength_valid = adx_wilder_14_valid`-Äquivalent und `volatility_relative_valid = state_atr_relative_d_valid`-Äquivalent sind erfüllt und werden **nicht** in die `regime_reason_codes`-Liste gemischt (getrennte Listen, nie zusammengeführt — Quellcode-Ebene, nicht nur Schema-Validator). Bestätigt durch `test_invalid_adx_only_invalidates_trend_context` und `test_invalid_atr_state_only_invalidates_volatility_context`. **Konform.**

## 7. Reason-Code-Registry, Zieltrennung, Vollständigkeit, Reihenfolge

Die zehn Codes und Prioritäten in `constants.py:122-163` sind bytegleich zu Spezifikationstabelle §12.7 (30…120, aufsteigend, laufzeitgeprüft `constants.py:184-189`). Zieltrennung ist über disjunkte `frozenset`s (`REGIME_REASON_CODES`, `TREND_STRENGTH_REASON_CODES`, `VOLATILITY_REASON_CODES`, `constants.py:172-180`) sowohl im Schema-Validator als auch im Compute-Pfad erzwungen. Determinismus/Duplikatfreiheit über `normalize_reason_codes` (`reason_codes.py:29-35`, `sorted(..., key=REASON_CODE_PRIORITY)`).

**Ein Befund zur Vollständigkeits-/Zutreffend-Semantik:** siehe **CLD-S5-002** (`REG_EFFECTIVE_UNCONFIRMED` wird breiter angewendet, als der Wortlaut von §12.7.1 nahelegt).

## 8. State-Snapshot, Canonical JSON, SHA-256, Anschlussprüfung, Ablehnung, Partitionsparität

- Canonical JSON: `sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False` (`state.py:46-53`), `state_payload_sha256` selbst wird aus dem Hash ausgeschlossen (`state.py:39-41`). Unabhängig durch `test_hash_matches_independent_canonical_json` reproduziert (eigene Neuimplementierung im Test, nicht Aufruf derselben Funktion) — starker Beleg für Konformität.
- Anschlussprüfung `_prior_state_status` (`compute.py:169-201`): prüft Typ, erneute Selbstvalidierung, Checksumme, `parent_build_id`, Schlüsselgleichheit, Zeitkontinuität (`last_open_time + INTERVAL_MILLISECONDS == first.open_time`) und Segmentgleichheit — bei jeder Abweichung Ablehnung mit vollständigem Warm-up-Neustart. Getestet: falscher Parent (`test_wrong_parent_rejects_prior_state`), Lücke (`test_noncontiguous_prior_state_rejected`), manipulierte Checksumme (`test_tampered_state_checksum_is_rejected`). **Konform.**
- Partitionsparität: `test_state_continuation_matches_full_build` und `test_partition_at_segment_boundary_matches_serial` vergleichen seriell vs. partitioniert per Gleichheit — bestehen, **aber genau dieser zweite Test maskiert CLD-S5-001** (siehe dort und Abschnitt 11).
- **CLD-S5-003** (Minor): Das Feldregister in §28.2 listet 17 Felder und formuliert "enthält mindestens" (erlaubt Supersets), nennt aber nicht, ob zusätzliche Felder Teil der SHA-256-Nutzlast sein dürfen/müssen. Die Implementierung hasht vier zusätzliche Profil-Identitätsfelder (`state_profile_id`, `state_profile_version`, `state_hash_profile_id`, `state_hash_profile_version`, `state.py:85-88`) mit. Für die interne Konsistenz ist das unschädlich (Werte sind pro Modellversion konstant, Tests bestehen), aber eine *unabhängige* Zweitimplementierung, die sich strikt an die 17-Felder-Tabelle hält, würde einen anderen Hash erzeugen — ein Interoperabilitätsrisiko für R2 (Wiederholung auf zweitem Gerät/zweiter Implementierung).

## 9. Erhaltung sämtlicher S4-Felder, Schlüssel, Reihenfolge, Segmente

`compute.py:45-47` erfasst `_S4_FIELD_NAMES` aus `dataclasses.fields(S4Row)`; `_copy_s4_values` (`compute.py:70-71`) kopiert diese unverändert in jede `S5Row`; am Ende von `compute_regimes` (`compute.py:486-498`) erfolgt eine **aktive Laufzeitprüfung** (nicht nur Test), die jedes S4-Feld auf Wertgleichheit zwischen Quelle und Ergebnis verifiziert und andernfalls `RuntimeError` wirft. `market_segment_id`/`indicator_segment_id` sind Teil dieser Menge. Dies ist eine ungewöhnlich robuste, über bloße Tests hinausgehende Absicherung. **Konform, vorbildlich umgesetzt.**

## 10. Stage-weite Input-Ablehnung, Fail-Closed

`_validate_input_rows` (`compute.py:109-166`) läuft vollständig **vor** jeder Zeilenverarbeitung und wirft bei: falschem Typ, Schema-/Profil-ID/Version-Abweichung, nicht-kanonischem Signal-Registry, leeren Schlüsselfeldern, falschem Interval, Mehrfachserien, nicht-monotoner/duplizierter Sortierung, undeklarierter Zeitlücke ohne Segmentreset, deklariertem Gap ohne Segmentreset. Kein Fall degradiert zu einer zeilenweisen `UNKNOWN`/`INVALID`-Zeile — echter Stage-Abbruch, konform zu §6.7 letzter Absatz. Fail-closed bei Data-Quality-Gate: `quality_gate_pass=false` erzwingt `REG_INPUT_QUALITY_GATE_FAILED` und damit `regime_raw=UNKNOWN`, unabhängig von sonstigen Werten (`compute.py:363-364`, getestet). **Konform**, mit der Einschränkung, dass Publication-Status-Prüfung und Registry-Versionsprüfung für Modell-/Reason-Code-Register (§6.7, weitere Spiegelstriche) außerhalb dieses reinen Compute-Pakets liegen dürften (kein S0–S2-Orchestrierungscode im Reviewpaket enthalten) — keine eigenständige Wertung möglich, daher kein Befund, nur Scope-Hinweis.

## 11. Testabdeckung, fehlerhafte Tests, unbelegte Behauptungen, False-Positive-Risiko

68/68 Tests bestehen (eigene Ausführung). Abdeckung von Wahrheitstabelle, Slope-Grenzfällen, State-Machine-Übergängen, Kontextzuständen, Schema-Validierung und Hash-Determinismus ist breit und größtenteils direkt an §31 orientiert.

**Konkretes False-Positive-Risiko identifiziert (zentraler Befund dieses Reviews):** `test_partition_at_segment_boundary_matches_serial` (`test_compute.py:220-250`) prüft Serien-/Partitionsparität an einer Segmentgrenze, **aber ausschließlich auf Zeilengleichheit (`first.rows + second.rows == full.rows`)**, nicht auf die inhaltliche Korrektheit von `regime_transition_flag/from/to` an der Grenzzeile selbst. Da der Fehler (CLD-S5-001) in *beiden* Berechnungspfaden identisch und deterministisch auftritt, **besteht der Paritätstest trotz des Fehlers** — ein Lehrbuchbeispiel dafür, dass Reproduzierbarkeitstests einen Determinismus-, aber keinen Korrektheitsnachweis liefern. `test_segment_reset_is_reported_once` (`test_compute.py:277-298`) testet einen Segmentwechsel ausschließlich in den ersten drei Zeilen der Serie, **bevor** überhaupt ein `regime_effective` bestätigt werden konnte (SMA200 dort noch nicht warmgelaufen) — der Test kann den Fehler daher grundsätzlich nicht auslösen. Kein vorhandener Test prüft explizit, dass `regime_transition_flag=False` (bzw. `transition_from=None`) gilt, wenn ein Segmentwechsel unmittelbar auf ein bereits bestätigtes, gültiges Regime folgt.

Die Implementation-Record-Behauptung "Gap and segment fail-closed handling" (Abschnitt 2) ist für `regime_effective`/`regime_valid`/`regime_reason_codes` selbst zutreffend, aber unvollständig bezüglich der Nebenfelder `regime_transition_flag/from`. Die Readiness-Review-Behauptung zu `REG_EFFECTIVE_UNCONFIRMED` (Zeile 321f.) wurde live gegen den Code verifiziert und ist als Beschreibung des *tatsächlichen* (nicht notwendigerweise spezifikationskonformen) Verhaltens zutreffend — siehe CLD-S5-002.

## 12. Ausschluss von S6-/Strategie-/Gate-/Return-/Label-/Barrier-Logik

`grep -rniE "gate_state|allow_long|allow_short|forward_return|label|barrier|GATE_TREND|GATE_RESEARCH|cooldown|mfi"` über `rcc002/s5/` und `tests/rcc002/s5/` liefert **keinen Treffer**. Keine ADX-Schwelle wird als Handelsfreigabe interpretiert (`classify_trend_strength` liefert nur ein Enum, keine Bool-Entscheidung); `close`/`sma`/`slope` werden ausschließlich für Regimeklassifikation, nie für Forward-Returns verwendet. **Vollständig konform.**

---

## Befunde

### CLD-S5-001 — CRITICAL
**Datei/Funktion:** `rcc002/s5/compute.py`, Funktion `compute_regimes`, Zeilen 314–332 (Vorschleifen-Initialisierung) und 337–353 (Schleifenkopf, `segment_reset`-Block); Kontrastfall korrekt implementiert in Zeilen 463–467.

**Verletzte Regel:** §9.3 ("Initialisierung — Am Segmentanfang: `regime_effective = UNKNOWN`, `regime_candidate = UNKNOWN`, `regime_candidate_count = 0`") und §27.1 ("Bei einer S2-/S3-Segmentgrenze: … persistierte State Machine wird zurückgesetzt") der `RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md`.

**Befund:** An einer Segmentgrenze — sowohl mitten in einem einzelnen `compute_regimes`-Aufruf als auch beim Fortsetzen über einen `prior_state`-Snapshot mit abweichender `market_segment_id`/`indicator_segment_id` ("trusted segment boundary", `_prior_state_status`, Zeilen 169–201) — werden `context`, `regime_candidate` und `regime_candidate_count` korrekt zurückgesetzt, **`effective` (der laufende `regime_effective`-Zustand) jedoch nicht**. Der alte, aus dem vorherigen Segment/Build stammende `effective`-Wert wird unverändert an `_advance_confirmation(raw=UNKNOWN, effective=<alt>, …)` (Zeile 401–410) übergeben. Da für `raw=UNKNOWN` gilt `transition = effective is not UNKNOWN` (Zeile 268), wird an der ersten Zeile jedes Segments, das auf ein bereits bestätigtes Regime folgt, fälschlich `regime_transition_flag=True` mit `regime_transition_from=<Regime des Vorsegments>`, `regime_transition_to=UNKNOWN` erzeugt — obwohl die Spezifikation für den Segmentanfang eine vollständige Reinitialisierung ohne "vorherigen" Zustand vorschreibt (§9.3) und einen Segmentreset explizit von einer Zustands*übergang* unterscheidet (eigener Reason Code `REG_SEGMENT_RESET`, §12.7.1, dessen eigene Beschreibung in `constants.py:151-154` lautet: "S5 state was reset **at an actual segment boundary**" — Reset, nicht Transition).

**Beleg (live gegen den Code reproduziert, nicht nur postuliert):**
```
row before boundary: effective = SIDE
row at boundary:     raw=UNKNOWN effective=UNKNOWN
                      transition_flag=True
                      transition_from=SIDE   <-- Regime aus dem VORHERIGEN Segment
                      transition_to=UNKNOWN
                      reasons=(REG_WARMUP_INCOMPLETE, REG_WINDOW_CROSSES_INDICATOR_SEGMENT,
                               REG_EFFECTIVE_UNCONFIRMED, REG_SEGMENT_RESET)
```
Reproduziert sowohl im seriellen Einzelaufruf als auch — bytegleich — im partitionierten Aufruf über `prior_state`. `regime_effective` und `regime_valid` selbst sind an dieser Zeile korrekt (`UNKNOWN`/`false`); betroffen sind ausschließlich die registrierten Ausgabefelder `regime_transition_flag`, `regime_transition_from`.

**Technische Auswirkung:**
1. Verletzt §27.2 ("Ein effektives Bull- oder Bear-Regime darf nicht über eine ungeklärte Datenlücke fortgeführt werden") im Geiste: Der Vorsegment-Zustand wird zwar nicht als *aktuelles* Regime fortgeführt, aber über `regime_transition_from` explizit über die Segmentgrenze hinweg in die neue Segment-Historie hinein exponiert.
2. Kontaminiert jede nachgelagerte Auswertung der Übergangshäufigkeit/-provenienz (z. B. "wie oft degradiert ein bestätigtes Regime live nach UNKNOWN") mit reinen Daten-/Segmentartefakten, die keine reale Marktzustandsänderung darstellen — ein Verstoß gegen die in `CLAUDE.md` referenzierte Backtest-Integrity-Policy ("a backtest that structurally cannot fail is worthless"), da hier ein struktureller Artefakt als inhaltliches Signal erscheint.
3. Der Fehler ist zu 100 % deterministisch reproduzierbar und tritt bei **jeder** realen Datenlücke/Segmentgrenze auf, die einem bereits bestätigten Regime folgt — in echten BTCUSDT-1m-Daten mit gelegentlichen Datenlücken kein Rand-, sondern ein Regelfall.
4. Die vorhandenen Paritätstests (§28.4/§33.2 "serielle und partitionierte Berechnung stimmen überein") geben trotz dieses Fehlers grünes Licht, da der Fehler in beiden Pfaden identisch reproduziert wird (siehe Abschnitt 11) — ein konkretes, nachgewiesenes False-Positive-Risiko der Zertifizierungskette.
5. Die Asymmetrie im selben Codepfad — der strukturell analoge Reset bei ungültigem `sma` innerhalb eines Segments (Zeilen 463–467) setzt `effective` korrekt zurück — zeigt, dass es sich um ein Implementierungsversehen und nicht um eine bewusste Designentscheidung handelt.

**Erforderliche Korrektur:** `effective` muss an jedem `segment_reset`-Punkt (sowohl im Vorschleifen-Setup bei `initial_segment_reset` als auch im Schleifenkopf bei einem erkannten Segmentwechsel) unconditional auf `RegimeState.UNKNOWN` gesetzt werden, **bevor** `_advance_confirmation` aufgerufen wird — analog zum bereits korrekten Verhalten in Zeilen 463–467. Ergänzend: `test_partition_at_segment_boundary_matches_serial` und `test_segment_reset_is_reported_once` um eine Fixture erweitern, die einen Segmentwechsel **nach** einem bereits bestätigten `regime_effective != UNKNOWN` erzwingt und explizit `regime_transition_flag=False`, `regime_transition_from=None`, `regime_transition_to=None` an der Resetzeile prüft.

---

### CLD-S5-002 — MINOR
**Datei/Funktion:** `rcc002/s5/compute.py`, Zeilen 415–416.

**Verletzte Regel (Auslegungsfrage):** §12.7.1 der Spezifikation: *"`REG_EFFECTIVE_UNCONFIRMED`, solange ein gültiger Rohzustand noch keinen ersten effektiven Zustand bestätigt hat"* — der Wortlaut ("ein gültiger Rohzustand … hat … bestätigt") legt nahe, dass der Code nur greifen soll, wenn `regime_raw` selbst bereits gültig ist (die in §12.5 explizit beschriebene 1–2-Zeilen-Verzögerung zwischen erstem gültigem Rohregime und erster Bestätigung).

**Befund:** Die Implementierung fügt `REG_EFFECTIVE_UNCONFIRMED` unconditional immer dann hinzu, wenn `effective is UNKNOWN` — unabhängig davon, ob `raw` selbst gültig ist. Live reproduziert: Bei Zeile 0 einer frischen Serie (SMA200 noch nicht warmgelaufen, `raw=UNKNOWN` wegen `REG_INPUT_INVALID`) erscheint zusätzlich `REG_EFFECTIVE_UNCONFIRMED` in `regime_reason_codes`, obwohl zu diesem Zeitpunkt gar kein "gültiger Rohzustand" vorliegt, der auf Bestätigung wartet. Dies gilt für den gesamten initialen Warm-up-Zeitraum (bei Standard-Parametrisierung ca. 1.640 Zeilen je Segment), nicht nur für die spezifisch in §12.5 beschriebene 2-Zeilen-Verzögerung.

Die "Implementation Readiness Review" (`docs/review/RCC_002_S5_IMPLEMENTATION_READINESS_REVIEW_2026-07-28.md:321-323`) beschreibt exakt dieses (weite) Verhalten als beabsichtigt ("applies only while no first valid effective regime has yet been confirmed") — die Behauptung wurde live gegen den Code verifiziert und trifft als *Verhaltensbeschreibung* zu. Als *Spezifikationsauslegung* bleibt sie gegenüber dem engeren Wortlaut von §12.7.1 zumindest ambig.

**Technische Auswirkung:** Kein Effekt auf `regime_valid`/`regime_effective` selbst (beide bleiben korrekt); Auswirkung ausschließlich auf die Vollständigkeits-/Präzisions-Semantik der Reason-Code-Liste während der Warm-up-Phase. Diagnosewerkzeuge, die `REG_EFFECTIVE_UNCONFIRMED` als spezifischen Marker für "Rohregime bereits gültig, Bestätigung ausstehend" interpretieren, würden während des allgemeinen SMA/Slope-Warm-ups falsch positive Treffer erhalten.

**Erforderliche Korrektur:** Spezifikationstext §12.7.1 präzisieren (klarstellen, ob der Code auch bei ungültigem Rohregime gelten soll), oder Implementierung auf `if raw is not RegimeState.UNKNOWN and effective is RegimeState.UNKNOWN` einschränken, falls die engere Lesart verbindlich gewählt wird. Kein Blocker für sich allein.

---

### CLD-S5-003 — MINOR
**Datei/Funktion:** `rcc002/s5/state.py`, Zeilen 67–89 (`RegimeStateSnapshot`, Felder `state_profile_id`, `state_profile_version`, `state_hash_profile_id`, `state_hash_profile_version`) und `_canonical`/`compute_state_hash`, Zeilen 26–53.

**Verletzte Regel:** §28.1/§28.2 der Spezifikation definieren den kanonischen State-Snapshot mit "mindestens" 17 benannten Feldern, treffen aber keine Aussage darüber, ob zusätzliche (nicht registrierte) Felder Teil der für `state_payload_sha256` gehashten Nutzlast sein dürfen.

**Befund:** Die Implementierung fügt vier zusätzliche, in §28.2 nicht registrierte Profil-Identitätsfelder hinzu und hasht sie mit (`_canonical` iteriert über *alle* Dataclass-Felder außer `state_payload_sha256`). Für die interne Konsistenz dieser einen Implementierung ist das unschädlich (Werte sind pro Modellversion konstant; alle State-Tests bestehen), aber eine spezifikationstreue *unabhängige* Zweitimplementierung (R2, "Wiederholung auf einem zweiten Gerät"), die sich strikt an die 17-Felder-Tabelle aus §28.2 hält, würde einen anderen SHA-256 für denselben logischen Zustand berechnen.

**Technische Auswirkung:** Potenzielles Interoperabilitäts-/Reproduzierbarkeitsrisiko bei einer unabhängigen Re-Implementierung oder einem plattformübergreifenden Vergleich, nicht bei der Nutzung dieser einen Implementierung selbst.

**Erforderliche Korrektur:** Spezifikation §28.2 um eine explizite Aussage ergänzen, ob/welche Erweiterungsfelder Teil der Hash-Nutzlast sein müssen, oder Implementierung auf exakt die registrierten 17 Felder plus explizit spezifizierte Erweiterungen beschränken.

---

### CLD-S5-004 — EDITORIAL
**Datei/Funktion:** `rcc002/s5/constants.py`, Zeilen 41–44 (`NUMERIC_PROFILE_ID`, `NUMERIC_PROFILE_VERSION`, `ABSOLUTE_TOLERANCE`, `RELATIVE_TOLERANCE`).

**Befund:** Diese gemäß §33.1 registrierten Werte werden innerhalb von `rcc002/s5/` nirgends referenziert (`grep` bestätigt keine Verwendung außer Deklaration/`__all__`). Das ist an sich korrekt, da §33.1 explizit exakte (nicht toleranzbasierte) interne Vergleiche verlangt und die Toleranzwerte nur für *externe* unabhängige Float64-Vergleiche (Reproduzierbarkeitsprüfungen R1/R2) gedacht sind, die vermutlich außerhalb dieses reinen Compute-Pakets liegen. Empfehlung: An geeigneter Stelle (Docstring oder Kommentar) den Verwendungszweck dieser Konstanten dokumentieren, um "toter Code" versus "für externe Verifikation reserviert" nicht verwechselbar zu machen.

---

### CLD-S5-005 — EDITORIAL
**Methodikhinweis, kein Code-Befund.** Die im Reviewauftrag genannte Paket-SHA-256 (`22407564a63a56a335477d4f3774c0976c62eb11e9d118a55098724a04e69de5`) konnte nicht gegen die Original-ZIP nachgerechnet werden, da nur der entpackte Inhalt bereitgestellt wurde. Empfehlung: Bei künftigen Reviewpaketen zusätzlich die ZIP-Datei selbst bereitstellen oder die Prüfsumme der entpackten Verzeichnisstruktur (z. B. `sha256sum`-Manifest je Datei) mitliefern.

---

## Zusammenfassung nach Prüfpunkt (1–12)

| # | Prüfpunkt | Status |
|---:|---|---|
| 1 | S4→S5-Schema, 21-Feld-Reihenfolge | Konform |
| 2 | Slope-Formel, Float64-Reihenfolge, 1440min, Warm-up | Konform bis auf Segmentbehandlung → CLD-S5-001 |
| 3 | Rohregime-Wahrheitstabelle | Konform |
| 4 | Dreifachbestätigung, Sättigung, Übergänge | Konform bis auf Segmentgrenze → CLD-S5-001 |
| 5 | Nullbarkeit/Semantik transition_from/to | Struktur konform; Inhalt an Segmentgrenze fehlerhaft (CLD-S5-001) |
| 6 | Unabhängige TrendStrength/VolatilityRelative-Gültigkeit | Konform |
| 7 | Reason-Code-Registry, Zieltrennung, Vollständigkeit | Konform bis auf CLD-S5-002 |
| 8 | State-Snapshot, JSON, SHA-256, Anschluss, Parität | Konform bis auf CLD-S5-003 |
| 9 | S4-Feld-/Schlüssel-/Reihenfolge-/Segmenterhaltung | Konform, laufzeitgeprüft |
| 10 | Stage-weite Ablehnung, Fail-Closed | Konform (im Scope des Pakets) |
| 11 | Testabdeckung/False-Positive-Risiko | Lücke identifiziert, direkt ursächlich für unentdecktes CLD-S5-001 |
| 12 | Ausschluss S6/Strategie/Gate/Return/Label/Barrier | Vollständig konform |

## Abschlussentscheidung

**REJECTED**

Begründung: CLD-S5-001 ist ein reproduzierbarer, deterministischer Verstoß gegen zwei explizite MUST-Regeln der verbindlichen Spezifikation (§9.3 Initialisierung, §27.1 Segment-Reset) in einem kanonisch registrierten S5-Ausgabefeld (`regime_transition_flag`/`regime_transition_from`), der bei jeder realistischen Datenlücke nach einem bestätigten Regime auftritt und von der vorhandenen Test- und Paritätsinfrastruktur nicht erkannt wird. Dies ist kein redaktionelles oder Abdeckungsproblem, sondern eine Korrektur der State-Machine-Reset-Logik selbst (`compute.py`, Vorschleifen-Setup und `segment_reset`-Block) plus ergänzende Regressionstests, bevor eine erneute Vorlage sinnvoll ist. CLD-S5-002 und CLD-S5-003 sind unabhängig davon zu klären, blockieren für sich allein aber keine Freigabe.
