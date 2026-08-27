# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-3 REREVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REVISION-3 REREVIEW FINDINGS RESOLVED IN REVISION 4 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V3-Hash:** `3a12e977bc7fe64b0341dc4ca5b5f562fef18598b8afedae5f4d4dbdd6bd23c6`
- **V3-Resolution-Record:** `0eac11b364a3d37d2aef833bc6b871c0f762503e61e436f2ca690845c701a7c8`
- **Resolution-Zielhash V4:** `fe9f6872403754961919941ed05436bfbea7ba013da63486c1b006efb24362fe`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die zwei Blocker, das High- und das Low-Finding des
unabhängigen read-only Re-Reviews der Revision 3 konkreten normativen
Korrekturen in Revision 4 zu.

Es zertifiziert die Korrekturen nicht selbst. Jeder Resolutionstatus lautet
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V4-Hashes darf ein Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V3-Re-Reviews

Die exakten Prüfidentitäten wurden vor und nach dem Review bestätigt:

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V3_SHA256: 3a12e977bc7fe64b0341dc4ca5b5f562fef18598b8afedae5f4d4dbdd6bd23c6
V3_RESOLUTION_SHA256: 0eac11b364a3d37d2aef833bc6b871c0f762503e61e436f2ca690845c701a7c8
REREVIEW_RESULT: NOT_READY
BLOCKER: 2
HIGH: 1
MEDIUM: 0
LOW: 1
```

Status der sieben Findings aus dem V2-Re-Review:

| Finding | V3-Re-Review | V4-Resolution |
|---|---|---|
| RB2 Restart Consumption | OPEN | adressiert durch getrennten Ledger Tip und Startup-Attempt-Extension |
| RB3 Owner/S4-Handoff | OPEN | adressiert durch selbstreferenzfreien Authority Commit |
| RM1 Clean Genesis | OPEN | adressiert durch PREPARE/Target/COMMIT |
| NH1 S4V2 Capability | CLOSED | unverändert bewahrt |
| NH2 Tick-/Control-Ordnung | CLOSED | unverändert bewahrt |
| NM1 Pre-Accept-Grenze | CLOSED | unverändert bewahrt |
| NM2 Lifecycle Fault Injection | CLOSED | erweitert und unverändert bewahrt |

Die Resolution des vorherigen Schritts wurde im Review nur als Änderungsindex,
nicht als Beweis ihrer eigenen Claims verwendet.

---

## 3. Resolution der Blocker

### B1 — Kryptographischer Record↔Target-State-Zyklus

**Bestätigter Konflikt:** V3 verlangte, dass ein Genesis-, Handoff- oder
Migrationsrecord den vollständigen Target-State-Fingerprint bindet. Der Target
State sollte gleichzeitig den daraus entstehenden Lifecycle-Head binden. Damit
hing jeder Fingerprint vom jeweils anderen ab.

**Resolution in V4:**

- jede Authority-Operation wird in `PREPARE` und `COMMIT` getrennt;
- eine kanonische Target-Business-Payload enthält alle fachlichen, Safety-,
  Schema-, Journal- und Pfadfelder, aber keinerlei Authority-/Ledger-Felder;
- ihr Fingerprint bildet zusammen mit Source Authority, Operation, Manifest
  und Approval die deterministische `authority_generation_id`;
- Business Payload plus Generation ID ergeben die Target-Core-Payload;
- PREPARE bindet Generation ID und Target-Core-Fingerprint;
- der anschließend materialisierte Target State bindet Generation ID und
  PREPARE-Fingerprint, aber weder COMMIT-Fingerprint noch Ledger Tip;
- erst der COMMIT bindet PREPARE und vollständigen Target-State-Fingerprint;
- der Target State bindet den COMMIT nicht zurück;
- erst ein durable COMMIT aktiviert Generation und Owner Epoch;
- ein offener PREPARE blockiert jeden Loop und darf nur exakt gegen seine
  gebundene Core-Payload fertiggestellt werden.

Die Hash-Reihenfolge ist damit gerichtet und azyklisch:

```text
target business -> generation ID -> target core -> PREPARE fingerprint
                -> full target state -> COMMIT fingerprint
```

Nach späteren Trading-Transaktionen beweist eine lückenlose Journal-/State-
Historie die Abstammung vom im COMMIT gebundenen initialen Target State. Jede
Transition muss Generation ID und PREPARE-Fingerprint bewahren.

**Betroffene V4-Abschnitte:** 7.7.1, 9.1, 9.3, 13.1, 13.6, 18, 20, 21.6,
21.7 und 23.

**Geschlossene abhängige Findings nach erneutem Review zu bestätigen:** RB3
und RM1.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

### B2 — Nicht-ownerverändernde Records invalidierten exakte Head-Bindungen

**Bestätigter Konflikt:** `RESTART_AUTH_CONSUME` und
`RECOVERY_MATERIALIZATION` verschoben in V3 denselben Head, den State und
Activation Authorization exakt binden sollten. Nach ordnungsgemäßem
Consumption war ein Restart deshalb nicht mehr konsistent freigebbar.

**Resolution in V4:** Aus derselben Hash-Kette werden drei getrennte Sichten
abgeleitet:

- `ledger_tip`: letzter Record beliebigen Typs, verändert sich bei jedem
  Append und ist niemals Bestandteil eines fachlichen State-Fingerprints;
- `authority_commit_anchor`: letzter gültiger Authority-COMMIT, verändert sich
  nur bei Genesis, Handoff oder Migration;
- `authority_generation_id`: stabile ID der aktiven State-Generation.

Weitere normative Regeln:

- Activation Authorization bindet Generation und Commit Anchor, nicht den
  veränderlichen Ledger Tip;
- Restart/Recovery Authorization bindet zusätzlich den exakten
  `pre_attempt_ledger_tip` und eine eindeutige `startup_attempt_id`;
- Consumption verschiebt nur den Ledger Tip;
- nach Consumption wird die vollständige Extension ab dem autorisierten Tip
  geprüft, nicht Gleichheit mit dem alten Tip;
- zulässig sind nur die exakt zur Startup-Attempt-ID gehörenden Consumption-,
  Recovery-/Gap- und Runtime-Session-Records;
- unbekannte oder konkurrierende Zwischenrecords blockieren Startup;
- State und Authorization werden nach nicht-ownerverändernden Appends nicht
  umgeschrieben.

**Betroffene V4-Abschnitte:** 7.2, 7.6, 7.7, 7.7.2, 8.3, 9, 13.1, 17,
18, 20, 21.5, 21.7 und 23.

**Geschlossenes abhängiges Finding nach erneutem Review zu bestätigen:** RB2.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des High Findings

### H1 — Durable KILL war beim auslösenden Ressourcenfehler unerfüllbar

**Bestätigter Konflikt:** V3 verlangte für jede KILL-Eskalation eine durable
Control-Transaktion. Disk-full, Permission-, FD- oder Memory-Fehler können
jedoch genau diesen Write verhindern, während L1C den sofortigen terminalen
Stop verlangt.

**Resolution in V4:**

- vor Loop-Eintritt wird `RUNTIME_SESSION_OPEN` durable geschrieben;
- der Record bindet State/Journal, Authority, Startup Attempt, Resource Check,
  vorreservierten Emergency-Write-Handle, festes Budget und Write-Deadline;
- scheitert Session OPEN oder Reserve, startet kein Loop;
- ein terminaler Control-Write wird über die Reserve genau einmal und nur bis
  zur gebundenen Deadline versucht;
- bei Erfolg gelten der normale KILL-/State-Commit und die terminale Direktive;
- bei Write-Fehler oder Deadline wird nicht weitergetradet, herabgestuft oder
  unbeschränkt gewartet: in-memory EMERGENCY, best-effort Diagnose und
  sofortiger Prozess-Exit;
- in diesem Zweig wird kein `RUNTIME_SESSION_CLOSE` geschrieben;
- der nächste Startup erkennt die unclosed Session als `TERMINAL_UNKNOWN`,
  sperrt Entry/Exit-Auswertung und verlangt manuelle
  `RECONCILE_TERMINAL_GAP`-Authorization;
- nach Ressourcenwiederherstellung wird ein bereits durable terminaler KILL
  wiederverwendet oder andernfalls genau ein konservativer EMERGENCY-KILL
  materialisiert;
- `TERMINAL_GAP_RECONCILIATION` bindet Session, Evidence, Control Event und
  State; die Operation startet keinen Loop;
- spätere Deeskalation und Restart bleiben getrennte manuelle Entscheidungen.

V4 behauptet damit keinen physisch unmöglichen KILL-Write, garantiert aber
einen fail-closed nächsten Startup über einen bereits vorab durable
Session-Record.

**Betroffene V4-Abschnitte:** 4, 7.6, 7.7, 7.8, 9, 16.2, 17, 18, 19, 20,
21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Resolution des Low Findings

### L1 — `risk_transition=NONE` erlaubte keine eindeutige From→To-Matrix

**Bestätigter Konflikt:** V3 erlaubte eine Tick-Transition „nach NONE oder
SOFT“, obwohl eine Deeskalation niemals aus einem Tick folgen darf.

**Resolution in V4:**

- `risk_transition` entfällt;
- optional zulässig ist ausschließlich
  `risk_escalation=NONE_TO_SOFT`;
- ohne Eskalation fehlt das Feld;
- `NONE→NONE` und `SOFT→SOFT` sind keine Transition;
- `SOFT→NONE`, `HARD→*` und `EMERGENCY→*` sind im Tick verboten;
- jede Deeskalation benötigt den getrennten manuellen Control-/Restart-
  Vertrag;
- die Pflicht-Testmatrix enthält den expliziten Negativtest.

**Betroffene V4-Abschnitte:** 13.4 und 21.4.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 6. Bewahrung bereits geschlossener Findings

Revision 4 bewahrt die im V3-Re-Review bestätigten Verträge unverändert:

- additives `PaperRiskStateS4V2` und terminale Capability-Matrix;
- getrennte Tick-, Control- und Lifecycle-Ordnungsräume;
- Pre-Accept-/Reject-/Commit-/Terminal-Semantik;
- vollständige Lifecycle-Fault-Injection-Matrix.

Zusätzlich bleiben alle früher geschlossenen Verträge zu committed Entry Quote,
Legacy-Write-Ausschluss, Atomic Progress Cursor und Legacy-exit-only Control
Binding erhalten.

---

## 7. Vollständigkeits- und Scope-Nachweis

```text
REVISION_3_REREVIEW_FINDINGS_MAPPED: 4/4
BLOCKERS_MAPPED: 2/2
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 1/1
PREVIOUSLY_CLOSED_FINDINGS_PRESERVED: 4/4
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_4_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Es wurden keine Runtime-Tests ausgeführt, weil ausschließlich Dokumentation
geändert wurde. Formale Datei-, Whitespace-, Hash- und Git-Scope-Prüfungen sind
zulässig; eine semantische Zertifizierung durch den Resolution-Autor ist es
nicht.

---

## 8. Nächster Gate

Der nächste zulässige Schritt ist:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-4-INDEPENDENT-READONLY-REREVIEW`

Das neue Re-Review muss den vollständigen V4-Hash prüfen und insbesondere
belegen, dass:

- Generation-ID-, Target-Core-, PREPARE-, State- und COMMIT-Fingerprints
  azyklisch bestimmbar sind;
- aktuelle States über ihre Journal-Historie eindeutig vom Authority-COMMIT
  abstammen;
- nicht-ownerverändernde Records keinen State-/Authorization-Rebind benötigen;
- Startup-Attempt-Extensions keine fremden Records akzeptieren;
- unpersistierbare terminale KILLs den Prozess unverzüglich beenden und der
  nächste Startup ohne Auto-Deeskalation fail closed bleibt;
- Tick-Deeskalationen vollständig ausgeschlossen sind.

Erst ein bestandenes unabhängiges Re-Review kann die Spezifikation als
implementierungsbereit bewerten. Terminales R3, bestandene Final Attestation
und eine separate ausdrückliche Implementierungsfreigabe bleiben auch danach
zwingend.
