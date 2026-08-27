# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-5 REREVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REVISION-5 REREVIEW FINDINGS RESOLVED IN REVISION 6 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V5-Hash:** `a544b0a83b4b6f13df8cb3f3bd6d75b4836655fb4108a6d85b992f4e598e7dde`
- **V5-Resolution-Record:** `8761522371f0722a93b9d28173fc42892f372c9913bea6c18bbf0623e6efd5f1`
- **Resolution-Zielhash V6:** `d0781659f5ccfdf446473238b29c1a51fa2203179e368d431cb5e5ffd5a28d54`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker und das High-Finding des unabhängigen
read-only Re-Reviews der Revision 5 konkreten normativen Korrekturen in
Revision 6 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V6-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V5-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V5_SHA256: a544b0a83b4b6f13df8cb3f3bd6d75b4836655fb4108a6d85b992f4e598e7dde
V5_RESOLUTION_SHA256: 8761522371f0722a93b9d28173fc42892f372c9913bea6c18bbf0623e6efd5f1
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 1
MEDIUM: 0
LOW: 0
```

Status der vier Findings aus dem V4-Re-Review:

| Finding | V5-Re-Review | V6-Resolution |
|---|---|---|
| B1 autorisierte PREPARE-Fertigstellung | OPEN | Genesis-Provenance und post-completion Restart geschlossen spezifiziert |
| B2 durable KILL/stale Snapshot | CLOSED | unverändert bewahrt |
| H1 Deadline bei nichtkooperativem I/O | OPEN | OS-erzwungener Parent-Guardian-Lebensdauervertrag |
| M1 Authority-Root-Testlücke | CLOSED | unverändert bewahrt |

Die älteren Findings `RB2`, `RB3`, `NH1`, `NH2`, `NM1` und `NM2` blieben
geschlossen. `RM1 Clean Genesis` blieb wegen des unten aufgelösten
post-completion Widerspruchs offen.

---

## 3. Resolution des Blockers

### B1 — Recovered Genesis konnte die Erststartausnahme widersprüchlich nutzen

**Bestätigter Konflikt:** V5 verlangte nach erfolgreicher
`COMPLETE_AUTHORITY_PREPARE`-Operation Prozessende und für den späteren Start
eine neue `RESTART_ONLY`-Authorization. Die allgemeine Clean-Genesis-
Erststartausnahme unterschied jedoch nicht eindeutig zwischen einem direkt im
ursprünglichen Prozess committeten Genesis und einem nach PREPARE-Crash
fertiggestellten COMMIT. Zusätzlich war die genaue Source-Authority-Belegung
des Genesis-Completion-Consumption-Records nicht über alle Vertragsstellen
widerspruchsfrei festgelegt.

**Resolution in V6:**

- jeder Authority-COMMIT bindet kanonisch genau eine Completion Provenance;
- `DIRECT` bindet ursprüngliche Operation, Prozess und Approval und ist nur
  ohne Completion-Consumption zwischen PREPARE und COMMIT zulässig;
- `RECOVERED_AFTER_PREPARE` bindet Completion-Authorization,
  Consumption-Event, Startup Attempt und vorherigen Ledger Tip;
- vorhandenes Completion-Consumption verbietet `DIRECT`; fehlendes exakt
  passendes Consumption verbietet `RECOVERED_AFTER_PREPARE`;
- die Erststartausnahme gilt nur für einen attestierten
  `ATOMIC_GENESIS_COMMIT` mit `DIRECT`, ohne Completion-Consumption und ohne
  frühere `RUNTIME_SESSION_OPEN` derselben Generation;
- ein recovered Completion-Prozess startet keinen Loop und beendet sich nach
  COMMIT; der nächste Prozess benötigt exakt eine neue `RESTART_ONLY`-
  Authorization und deren einmaliges durable Consumption;
- Activation Authorization und die bereits verbrauchte Completion-
  Authorization sind kein Ersatz;
- der Genesis-Completion-Consumption-Record enthält an den normalen
  Source-Authority-Feldpositionen exakt
  `source_authority_commit_anchor=NONE` und
  `source_authority_generation_id=NONE`, dazu Target Generation und
  PREPARE-Event-ID/-Fingerprint;
- diese Sentinels sind kanonische Payloadfelder; fehlende, leere oder
  abweichende Werte sind ungültig;
- Pflicht-Negativtests decken Provenance-Fälschung, Sentinel-Abweichung,
  recovered Startup ohne neue Freigabe, Wiederverwendung der Completion-
  Authorization und eine angeblich direkte Genesis mit früherer Runtime
  Session ab.

Damit sind unmittelbarer Genesis-Erststart und Startup nach autorisierter
PREPARE-Fertigstellung getrennte, nicht überlappende Protokollpfade.

**Betroffene V6-Abschnitte:** 7.6, 7.7, 7.7.1, 7.7.2, 9, 9.3, 17, 18,
21.5, 21.7 und 23.

**Abhängiges älteres Finding:** `RM1 Clean Genesis` ist normativ adressiert und
muss im neuen unabhängigen Review erneut geschlossen werden.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des High Findings

### H1 — Watchdog-Lebensdauer und Kill-Capability waren nach OPEN nicht fail-stop

**Bestätigter Konflikt:** V5 verlangte zwar einen getrennten Exit-Watchdog,
band den Trading-Prozess nach dem Ready-Handshake aber nicht OS-erzwungen an
dessen weitere Existenz und Kill-Berechtigung. Tod oder Capability-Verlust des
Watchdogs nach `RUNTIME_SESSION_OPEN` konnte deshalb den nachfolgenden
EMERGENCY-Exitvertrag unwirksam machen.

**Resolution in V6:**

- `TerminalParentGuardianV1` startet und besitzt den Trading-Prozess als
  tatsächliches OS-Child beziehungsweise als exklusiver Windows-Job-Owner;
- Linux/WSL verwendet `PR_SET_PDEATHSIG/SIGKILL`, anschließenden Parent-PID-
  und Startzeit-Race-Check sowie PIDFD- und Credentials-Bindung;
- ein minimales attestiertes Native-/Seccomp-Profil verhindert nach Ready
  Credential-/Capability-Wechsel, `fork`/`exec` und blockierende Guardian-
  Syscalls; das Child kann `PDEATHSIG` oder seine gebundene Identität danach
  nicht lösen;
- Windows verwendet ein exklusiv vom Guardian gehaltenes Job Object mit
  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, nicht vererbbarem Handle und ohne
  Breakaway;
- Guardian-Tod beziehungsweise Job-Handle-Schluss beendet das Trading-Child
  kernel-seitig und unabhängig von Python- oder Trading-Thread-Kooperation;
- Guardian prüft Zielidentität, Kill-Handle und Capability monoton spätestens
  alle `TERMINAL_GUARDIAN_LEASE_MAX_MS=25`; ein Fehlschlag beendet den
  Guardian und löst dadurch die Kernel-Todbindung aus;
- fehlende OS-Primitive, Reparenting, PID-Reuse, nicht exklusiver Job-Handle,
  ungültige Ready-Bindung oder Lease-Maximum ungleich `25` verhindert Session
  OPEN;
- Session OPEN und Audit binden Guardian-/Child-PID samt Startzeiten,
  OS-Lease-Typ/-Identifier, Credentials-/Capability-Fingerprint, Lease-Nonce
  und letzte monotone Capability-Probe;
- Persistence Worker und potenziell blockierender Datei-I/O bleiben vom
  I/O-freien Guardian getrennt;
- Fault Injection tötet den Guardian und entzieht/invalidiert Kill-Capability
  nach OPEN; das Trading-Child muss ohne Kooperation spätestens innerhalb der
  unveränderten `100 ms`-Obergrenze enden.

Damit hängt der terminale Exit weder von der fortdauernden Kooperation des
Trading-Prozesses noch von einem lediglich logisch vorhandenen Watchdog ab.

**Betroffene V6-Abschnitte:** 6.3, 7.8, 16.2.1, 17, 18, 19, 20, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Bewahrung der geschlossenen Findings

Revision 6 bewahrt ausdrücklich:

- den autorisierten, nicht loop-startenden PREPARE-Completion-Pfad;
- journal-first Terminal-Gap-Reconciliation und Exactly-once Control Event ID;
- Worker Lease/Fencing vor Recovery;
- die monotone unveränderliche `100 ms`-Exit-Obergrenze und nonblocking IPC;
- vollständige Authority-Root-/Generation-/PREPARE-Tamper-Tests;
- selbstreferenzfreie Authority-Generationen und getrennte Ledger-Tip-/
  Authority-Anchor-Sichten;
- vollständige S4-/Loss-/Throttle-/Progress-Handoffs und alle bestehenden
  ENFORCED-, Production-, Exchange- und Aktivierungsgrenzen.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_5_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
PREVIOUSLY_CLOSED_V4_FINDINGS_PRESERVED: 2/2
OLDER_FINDINGS_NORMATIVELY_ADDRESSED: 7/7
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_6_HASHED: YES
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

## 7. Nächster zulässiger Schritt

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-6-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. die vollständige Nichtüberlappung von DIRECT-Genesis-Erststart und
   recovered post-completion Restart;
2. die exakten Genesis-Consumption-Sentinels und Provenance-Negativtests;
3. die ausführbare OS-Parent-/Job-Bindung einschließlich Guardian-Tod und
   post-OPEN Capability-Verlust;
4. die Bewahrung aller zuvor geschlossenen Findings und Scope-Grenzen.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
