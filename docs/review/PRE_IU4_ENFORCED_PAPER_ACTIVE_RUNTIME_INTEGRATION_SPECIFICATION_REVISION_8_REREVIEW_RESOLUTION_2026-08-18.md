# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-8 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-8 REREVIEW FINDING RESOLVED IN REVISION 9 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V8-Hash:** `d5459835b42dc4c4b4b31b24403c7aa0b7f59ea9035154bafeefbf3fab32d197`
- **Revision-7-Rereview-Resolution-Record:** `9bcbd50d83e391265d108e70b4451552d7379a3bdbdffb86d875447d1e70dbae`
- **Resolution-Zielhash V9:** `fc9a947274395a38fd287411ec171c1b1dc624f8ddfc7364ce3437ecf93e91b1`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet das einzige offene High-Finding des unabhängigen
read-only Re-Reviews der Revision 8 konkreten normativen Korrekturen in
Revision 9 zu.

Es zertifiziert die Korrektur nicht selbst. Der Resolutionstatus lautet
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V9-Hashes darf das Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V8-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V8_SHA256: d5459835b42dc4c4b4b31b24403c7aa0b7f59ea9035154bafeefbf3fab32d197
REVISION_7_RESOLUTION_SHA256: 9bcbd50d83e391265d108e70b4451552d7379a3bdbdffb86d875447d1e70dbae
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V8-Re-Review | V9-Resolution |
|---|---|---|
| V8-H1 nicht erzwingbare Thread-/Seccomp-/Worker-Request-Autorität | OPEN | separate Native-Broker-Prozessgrenze, OS-erzwungene Mapping-Rechte und receiverseitiger CAS-Nachweis |

Das V8-Re-Review schloss V7-B1 vollständig. Der Timing-/Last-/Observer- und
Uninterruptible-I/O-Teil von V7-H1 wurde ebenfalls geschlossen. Offen blieb nur
die technische Erzwingbarkeit der Control-Word- und Worker-Request-Autorität.
Alle älteren Findings blieben geschlossen.

---

## 3. Bestätigter Konflikt V8-H1

Revision 8 legte den Native Shim als Thread in den Trading-Prozess und erklärte
ihn zum einzigen writable Control-Word-Mapper. Linux-Mappings und ihre
Schreibrechte gehören jedoch zum Prozessadressraum, nicht zu einem einzelnen
Thread. Eine für den Shim writable Map war daher auch für die anderen Threads
desselben Prozesses adressierbar; die Aussage „Python erhält keine writable
Map“ stellte keine OS-erzwungene Writer-Grenze her.

Zusätzlich durfte der Trading-/Python-Thread für `terminal_trip()` ein
`sendmsg` auf dem Worker-FD ausführen. Klassisches Seccomp kann FD und skalare
Syscall-Argumente prüfen, aber weder den userspace `msghdr`/Iovec-Inhalt noch
den aufrufenden nativen Funktionspfad dereferenzieren. Die behauptete
Beschränkung auf genau den vorgesehenen Worker-Payload war damit nicht durch
den beschriebenen Filter implementierbar. Der Worker prüfte außerdem nicht
selbst als notwendige Annahmebedingung, dass das Control Word bereits exakt
TERMINATING mit der gebundenen Trip-Sequenz war.

---

## 4. Normative Resolution in Revision 9

### 4.1 Echte Prozessgrenze für den einzigen Runtime-Writer

Revision 9 führt `TerminalNativeTripBrokerV1` als separaten, single-threaded,
attestierten Native-Prozess ein. Nach der Genesis-Initialisierung ist
ausschließlich dieser Broker Runtime-Writer von
`TerminalLeaseControlWordV2`.

Die Bootstrap-Reihenfolge ist ausführbar festgelegt:

1. Der Launcher erzeugt und initialisiert das anonyme Memfd ohne eigene
   writable Map.
2. Der frisch geforkte Broker erzeugt seine einzige writable Shared Map und
   bestätigt Adresse und Inode.
3. Der Launcher setzt danach
   `F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_FUTURE_WRITE|F_SEAL_SEAL`.
4. Guardian, Worker und Trading-Prozess mit Native Shim erhalten ausschließlich
   read-only Maps; ihre Memfd-FDs werden vor Ready geschlossen.
5. `/proc/<pid>/maps`, Memfd-Inode, Seals und Mapping-Rechte sämtlicher
   beteiligter Prozesse werden extern attestiert. Jede weitere writable Map,
   jeder unbekannte Mapper oder fehlende Seal verhindert Session OPEN.

Der Broker setzt vor Ready `PR_SET_DUMPABLE=0`, leert seine Capability-Sets und
setzt `no_new_privs`. Ptrace-/Yama-Policy, fehlende privilegierte Co-Tenants und
die Verbote von `ptrace`, `process_vm_writev`, `/proc/.../mem`, Mapping-Rechte-
Änderungen, Namespace-Wechsel, `fork`, `clone` und `exec` gehören zum gebundenen
Capability-Envelope.

Damit ist die Writer-Trennung nicht mehr thread-lokale API-Kapselung, sondern
eine prozess- und mappingrechtlich prüfbare Grenze.

### 4.2 Inhaltsloser Trading-Trip-Trigger

Der Trading-Prozess besitzt weder eine writable Control-Word-Map noch einen
Worker-IPC-FD. `terminal_trip()` setzt zuerst einen irreversiblen lokalen
Request-Latch und schreibt danach genau einen atomaren Acht-Byte-Record auf das
Write-Ende einer dedizierten nonblocking
`pipe2(O_NONBLOCK|O_CLOEXEC)`-Einbahnverbindung zum Broker.

Jeder beliebige Acht-Byte-Inhalt hat dieselbe einzige Bedeutung
`REQUEST_TERMINATION`; der Inhalt wird nicht interpretiert. Weil acht Byte
kleiner als `PIPE_BUF` sind, ist der Record atomar. Seccomp muss nur die
tatsächlich prüfbaren skalaren Argumente FD und `count=8` prüfen. Ein roher oder
wiederholter zulässiger Write kann ausschließlich denselben fail-safe Trip
vorziehen. Eine Payload- oder Callsite-Prüfung durch BPF wird nicht mehr
behauptet.

Eine volle Pipe bedeutet, dass bereits ein ungelesener Trip-Record vorliegt.
Ein geschlossener Kanal oder Broker-Tod stoppt alle weiteren Renewal Approvals
und lässt die bereits armed Kernel-Lease expirieren. Kein Triggerfehler erlaubt
Latch-Rücknahme oder fachliche Fortsetzung.

### 4.3 Broker-linearisiertes Renewal und Trip

Guardian-Renewals laufen über ein exklusives nonblocking
`SOCK_SEQPACKET`-Socketpair zum Broker. Nur der Broker führt die Renewal-CAS
`(RUNNING,n,0)→(RUNNING,n+1,0)` aus. Erst danach sendet er eine exakt große,
vor der CAS validierte `TerminalBrokerRenewalApprovalV1` über ein zweites
exklusives Socketpair an `TerminalKernelLeaseShimV3`.

Der Shim besitzt nur die read-only Control-Word-Map und die prozesslokale
Self-Death-Timer-Autorität. Er akzeptiert nur den gebundenen Broker-Peer, exakte
Struct-Länge, vollständige Credentials und dieselbe Control-Word-Sequenz. Eine
vor Trip linearisierte Approval darf ausschließlich die bereits gebundene
absolute Expiry von höchstens `now_at_broker_validation+25 ms` setzen. Nach
TERMINATING erzeugt der Broker keine Approval mehr.

Der Broker priorisiert einen lesbaren Trip-Record vor weiteren Renewals und ist
der einzige Ausführer der CAS
`(RUNNING,n,0)→(TERMINATING,n,1)`. Erst nach einer neuen erfolgreichen Trip-CAS
sendet er die Guardian-/Shim-Notifications und höchstens einen Worker-Request.
Stall oder Tod des Brokers vor oder nach der CAS stoppt Approvals; die armed
Lease bleibt der unabhängige Fail-stop-Pfad.

### 4.4 Worker-Request wird am Empfänger autorisiert

Der Broker→Worker-Kanal ist ausschließlich zwischen diesen beiden Prozessen
geöffnet. Der Trading-Prozess besitzt keine Kopie. `SO_PASSCRED` ist aktiv und
der Worker verlangt pro Nachricht kernel-erzeugte `SCM_CREDENTIALS` der
gebundenen Broker-PID/UID/GID.

Vor jedem Journal-I/O akzeptiert der Worker ausschließlich:

- exakt `sizeof(TerminalWorkerKillRequestV2)` ohne Truncation, fremde
  Ancillary-FDs oder unbekannte Flags;
- den gebundenen Broker-Peer und die gebundene Session/Control Event ID;
- passende Transaction Sequence, Journal Head und State Fingerprint;
- einen eigenen Acquire-Load der read-only Control-Word-Map mit exakt
  `(TERMINATING,n,1)`;
- dieselbe Renewal-Sequenz und Broker-Generation im Request.

RUNNING, CLOSED, falsche Sequenz/Generation, fremder Peer, abweichender Payload
oder zweiter Request wird ohne Mutation fail closed verworfen. Damit wird die
Kausalität „Worker-Request ausschließlich nach neuer erfolgreicher Trip-CAS“
am unabhängigen Empfänger geprüft. Die Spezifikation behauptet nicht mehr,
dass Seccomp den `msghdr`-Payload oder den Callsite-Pfad erkennen könne.

### 4.5 Versionierung und Capability-Nachweis

Der geänderte Vertrag ist additiv und eindeutig versioniert als:

- `IU4RuntimeControlProfileV3`;
- Runtime Session Envelope V4;
- `TerminalParentGuardianV3`;
- `TerminalNativeTripBrokerV1`;
- `TerminalKernelLeaseShimV3`;
- `TerminalLeaseControlWordV2`;
- `TerminalLeaseCapabilityProfileV2`;
- `TerminalBrokerRenewalApprovalV1`;
- `TerminalWorkerKillRequestV2`.

Das Capability-Profil bindet zusätzlich Broker-Binär-/Filterhash, Memfd-Seals,
vollständige Prozess-Mappings, Ptrace-/Yama-Grenzen, beide Renewal-Kanäle,
Trip-Request-Pipe, Notification-Eventfds, Broker→Worker-Peer sowie getrennte
Broker-CAS- und Guardian-Dispatch-Budgets von jeweils 5 ms.

Die Pflichtmatrix enthält insbesondere Broker-Stall/-Tod vor und nach CAS,
zweite writable Map, unbekannten Mapper, Seal-Tamper, neuen writable `mmap` nach
`F_SEAL_FUTURE_WRITE`, rohe/wiederholte Trip-Records, fremden Worker-Peer,
RUNNING/CLOSED am Worker, Sequenz-/Generation-Mismatch, verlorenen
Broker→Worker-Request und beide Trip-/Renewal-Linearization-Reihenfolgen.

**Betroffene V9-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 16.2.1, 17, 18, 19, 20,
21.7, 23 und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Bewahrung der geschlossenen Findings

Revision 9 bewahrt ausdrücklich:

- V7-B1: globaler Trip und Renewal bleiben auf demselben atomischen Control
  Word linearisiert; Worker-/IPC-/Notification-Ausfall verhindert den
  Fail-stop nicht;
- das endliche, exakt berechenbare Timing-/Last-/Observer-Envelope und die
  Trennung von Single-Thread-I/O und vollständigem Child-Stop;
- nicht übertragbare DIRECT-Genesis-Continuation und zwingendes
  `RESTART_ONLY` nach Prozesswechsel oder recovered Completion;
- exakte Genesis-NONE-Sentinels und PREPARE-Completion ohne Loop-Start;
- journal-first Terminal-Gap-Reconciliation und Exactly-once Control Event ID;
- Worker Lease/Fencing vor Recovery;
- ehrliche Trennung von Termination-Anforderung, pending Signal und Process
  Reaping ohne feste Reap-Deadline;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- vollständige Authority-Root-/Generation-/PREPARE-Tamper-Tests;
- vollständige S4-/Loss-/Throttle-/Progress-Handoffs sowie alle bestehenden
  ENFORCED-, Production-, Exchange- und Aktivierungsgrenzen.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_8_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
V7_B1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTION_APPLIED: YES
REVISION_9_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-9-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass ausschließlich der separate Broker eine writable Control-Word-Map
   besitzt und die Memfd-Seals/Bootstrap-/Ptrace-Grenzen technisch ausführbar
   und vollständig sind;
2. dass jeder zulässige Trading-Pipe-Record nur fail-safe wirkt und kein
   Trading-Thread Worker-IPC- oder Renewal-Autorität besitzt;
3. dass Broker-Renewal, Trip-CAS und Shim-Timer-Update in beiden Race-
   Reihenfolgen keine Verlängerung nach TERMINATING zulassen;
4. dass der Worker die Broker-Credentials und den TERMINATING-/Trip-/Renewal-
   Nachweis vor Journal-I/O unabhängig und fail closed prüft;
5. dass Broker-Stall/-Tod, Worker-/IPC-/Notification-Ausfall und volle/
   geschlossene Trip-Pipe innerhalb des endlichen Capability-Envelopes sicher
   enden;
6. dass sämtliche zuvor geschlossenen Findings und Scope-Grenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
