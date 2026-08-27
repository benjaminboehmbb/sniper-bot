# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-7 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-7 REREVIEW FINDINGS RESOLVED IN REVISION 8 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V7-Hash:** `a9e10855a18bce9131863482ae1473f37d201576c193c7fc775e0fdfe6e0798f`
- **V7-Resolution-Record:** `9b98af549c6c7073b540f4050c79f53020455d5105fd349f010e714099428b21`
- **Resolution-Zielhash V8:** `d5459835b42dc4c4b4b31b24403c7aa0b7f59ea9035154bafeefbf3fab32d197`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker und das High-Finding des unabhängigen
read-only Re-Reviews der Revision 7 konkreten normativen Korrekturen in
Revision 8 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V8-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V7-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V7_SHA256: a9e10855a18bce9131863482ae1473f37d201576c193c7fc775e0fdfe6e0798f
V7_RESOLUTION_SHA256: 9b98af549c6c7073b540f4050c79f53020455d5105fd349f010e714099428b21
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V7-Re-Review | V8-Resolution |
|---|---|---|
| V7-B1 Child-Latch ohne Guardian-/Shim-Trip | OPEN | gemeinsames atomisches Control Word, nicht verlierbarer Trip und Renewal-CAS |
| V7-H1 nicht ausführbares Shim-/Preflight-Envelope | OPEN | thread-spezifische Syscall-Autorität und endliches exakt berechenbares Capability-Profil |

Das V6-Finding DIRECT über Prozesswechsel, die falsche Reviewidentität und
`RM1 Clean Genesis` wurden im V7-Re-Review geschlossen. B2, M1, RB2, RB3,
NH1, NH2, NM1 und NM2 blieben geschlossen.

---

## 3. Resolution des Blockers

### V7-B1 — EMERGENCY-Latch erreichte Guardian und Lease Shim nicht sicher

**Bestätigter Konflikt:** V7 setzte im Trading-Prozess nur einen lokalen
in-memory Latch und sandte den KILL-Request ausschließlich an den Persistence
Worker. Bei gesundem Guardian und Shim, aber fehlgeschlagenem Worker/IPC,
blieben Zielidentität und Kill-Capability gültig. Der Guardian konnte deshalb
weiter Heartbeats senden und der Shim den Timer erneuern. Weder harte
Termination noch Lease-Expiry war innerhalb 100 ms garantiert.

**Resolution in V8:**

- `TerminalLeaseControlWordV1` ist ein einziges prozessübergreifendes,
  nachweislich lock-free `_Atomic uint64_t` im anonymen Session-Memfd;
- das Bitlayout kodiert State, einmaligen Trip und monotone Renewal-Sequenz
  ohne Wraparound;
- ausschließlich der native Shim darf Renewal per CAS von
  `(RUNNING,n,0)` nach `(RUNNING,n+1,0)` committen;
- ausschließlich der native `terminal_trip()`-Entry darf
  `RUNNING→TERMINATING` mit `trip_sequence=1` committen;
- `terminal_trip()` ist die erste Mutation des EMERGENCY-Pfads, noch vor
  Eventfd-, Worker- oder Journal-I/O;
- Trip und Renewal konkurrieren auf demselben vollständigen Atomic Word. Eine
  zuerst linearisierte Renewal bindet höchstens die vorhandene absolute
  25-ms-Expiry; linearisiert Trip zuerst, scheitert jede folgende Renewal-CAS;
- ein nach Renewal-CAS ausgeführtes `timer_settime` darf nur die bereits vor
  der CAS validierte absolute Expiry setzen und kann einen dazwischen
  linearisierten Trip nicht nach hinten verlängern;
- Guardian und Shim besitzen zwei getrennte vorab geöffnete nonblocking Trip-
  Eventfds. Der native Trip-Entry signalisiert beide erst nach erfolgreicher
  CAS;
- Eventfd-Verlust, `EAGAIN`, Close oder Nichtlesen ist nicht sicherheits-
  kritisch: Guardian liest das Control Word vor jedem Heartbeat, Shim vor jeder
  Renewal, und der bereits armed Timer läuft ohne Renewal ab;
- Guardian fordert bei TERMINATING über den gebundenen PIDFD sofort harte
  Termination an; Shim darf die Expiry nur verkürzen, nie verlängern oder
  disarmen;
- Worker-Request bleibt genau einmal und best effort nach Trip-CAS; ein bereits
  TERMINATING-Pfad erzeugt weder zweite Notification noch zweiten Request;
- CLOSED ist nur nach durable Session CLOSE und bestätigtem Child-Exit aus
  RUNNING zulässig; `TERMINATING→RUNNING/CLOSED` ist unerreichbar;
- Pflicht-Fault-Injection deckt gesunden Guardian/Shim plus Worker-Ausfall,
  volle/geschlossene/verlorene Eventfds und beide Trip-/Renewal-
  Linearization-Reihenfolgen ab.

Damit hängt EMERGENCY nicht mehr von der erfolgreichen Zustellung einer
Child-Notification oder dem Persistence Worker ab. Der irreversible Trip
selbst stoppt Renewals.

**Betroffene V8-Abschnitte:** 6.3, 7.8, 16.2.1, 17, 18, 19, 20, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des High Findings

### V7-H1 — Shim-Autorität und Timing-Preflight waren nicht berechenbar

**Bestätigter Konflikt:** V7 legte den Shim in den Trading-Prozess, trennte aber
nicht exakt, welcher Thread Timer-Renewals und welcher Thread den Trip ausführen
darf. Authentisierung und Syscall-Grenzen des Renewal-Kanals fehlten. Der
verlangte „Worst-Case-Nachweis“ besaß weder festes Sicherheitsbudget noch
Lastgrenzen, Trialzahl oder Messdefinition. Außerdem vermischte der
Uninterruptible-I/O-Test einen einzelnen blockierten Trading-Thread mit einem
stillstehenden Gesamtprozess.

**Resolution in V8:**

- `TerminalParentGuardianV2`, `TerminalKernelLeaseShimV2` und Runtime Session
  Envelope V3 versionieren den geänderten Vertrag;
- der Shim ist ein vor Python gestarteter nativer Thread und alleiniger Timer-
  Renewal-Writer;
- Guardian, Shim und Trading-/Python-Threads erhalten getrennte irreversible
  Seccomp-Filter mit exakter Syscall-/FD-/Argumentmatrix;
- Guardian darf nur Clock, Control-Word-Read, Renewal-`sendmsg`, Trip-Eventfd-
  Read und `pidfd_send_signal` auf gebundenen Deskriptoren verwenden;
- Shim darf nur Clock, Renewal-`recvmsg`, Shim-Trip-Eventfd und
  `timer_settime` für exakt die gebundene Timer-ID verwenden;
- Trading-/Python-Threads besitzen keine Timer-/Renewal-Autorität. Der native
  Trip-Entry darf nur lock-free CAS, exakt acht Byte an die zwei festen
  Eventfds und die begrenzte Worker-Nachricht senden;
- Renewal verwendet ein exklusives nonblocking `SOCK_SEQPACKET`-Socketpair;
  Session, Sequenz, PIDFD-Ziel, Capability Proof, absolute Expiry, Socket-
  Inode, `SO_PEERCRED`, FD-Identitäten und Nonces sind gebunden;
- Replay, Gap, falsche Credentials/Session oder Expiry über `now+25 ms` wird
  verworfen;
- `TerminalLeaseCapabilityProfileV1` bindet Kernel/WSL, Architektur, Clock-
  Auflösung, Binär-/Toolchain-/Seccomp-Hashes, Atomic-/Mapping-Beweis, CPU-
  Affinity/Scheduler/`mlockall`, Cgroup-Limits, Stress-/Fault-/Observer-
  Artefakte und alle Zeitbudgets;
- feste Budgets sind Heartbeat 10 ms, Lease 25 ms, Trip Dispatch 5 ms,
  Kernel-Signalgeneration 25 ms und Fail-stop 100 ms;
- die vollständige Zertifizierung führt exakt 10 000 deterministische Trials
  je Pflichtszenario über alle Mikrosekunden-Offsets des Heartbeat-Zyklus aus;
- Lastgrenzen sind exakt: 100 % auf allen nicht reservierten CPUs, keine
  fremden runnable Tasks im Guardian-/Shim-CPU-Set, Memory 90 % des Cgroup-
  Limits mit 64 MiB Terminal-Reserve, FD-Limit minus 16 und blockierter Worker;
- PASS verlangt in jedem Trial: keine Renewal nach Trip, Guardian-Dispatch
  binnen 5 ms, Kernel-Signal spätestens 25 ms nach Expiry/50 ms nach letzter
  Renewal, Fail-stop binnen 100 ms, keine Side Effects und vollständige
  externe Kernel-Zeitpunkte. Percentile, Retry oder fehlende Messung sind kein
  PASS;
- vor jedem OPEN laufen in einem state-/journalfreien Probe-Child exakt 32
  phasenverteilte Trials je Guardian-Stop, Shim-Stall und vollem Eventfd;
- die Zertifizierung wird ausdrücklich nur als endliches Capability-Envelope,
  niemals als universeller Scheduler-Worst-Case bezeichnet;
- gesamtes Child-`SIGSTOP` stoppt den Shim und lässt den Timer expirieren. Ein
  nur vor Trip blockierter Trading-Thread darf bei gesundem Shim renewen, kann
  aber keine Side Effects ausführen; Trip vor dem Block stoppt jede Renewal und
  erzeugt das Signal unabhängig von der Thread-Rückkehr;
- jeder Profil-, Environment-, Last-, Mess- oder Einzelbudget-Mismatch
  verhindert Session OPEN ohne Fallback.

Damit sind Rollen, Kanäle, Testdomäne und PASS/FAIL-Regel vollständig
berechenbar, ohne aus einem endlichen Stresslauf einen universellen Worst Case
abzuleiten.

**Betroffene V8-Abschnitte:** 6.3, 7.8, 7.8.1, 16.2.1, 17, 18, 19, 20,
21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Bewahrung der geschlossenen Findings

Revision 8 bewahrt ausdrücklich:

- nicht übertragbare DIRECT-Genesis-Continuation und zwingendes
  `RESTART_ONLY` nach Prozesswechsel oder recovered Completion;
- exakte Genesis-NONE-Sentinels und PREPARE-Completion ohne Loop-Start;
- journal-first Terminal-Gap-Reconciliation und Exactly-once Control Event ID;
- Worker Lease/Fencing vor Recovery;
- ehrliche Trennung von Termination-Anforderung, pending Signal und Process
  Reaping ohne feste Reap-Deadline;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- vollständige Authority-Root-/Generation-/PREPARE-Tamper-Tests;
- selbstreferenzfreie Authority-Generationen und getrennte Ledger-Tip-/
  Authority-Anchor-Sichten;
- vollständige S4-/Loss-/Throttle-/Progress-Handoffs sowie alle bestehenden
  ENFORCED-, Production-, Exchange- und Aktivierungsgrenzen.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_7_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
PREVIOUSLY_CLOSED_V6_FINDINGS_PRESERVED: 2/2
OLDER_FINDINGS_NORMATIVELY_ADDRESSED: 9/9
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_8_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-8-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass Trip und Renewal auf demselben Atomic Word linearisiert sind und nach
   TERMINATING keine Renewal oder fachliche Fortsetzung erreichbar ist;
2. dass Worker-/IPC-/Eventfd-Ausfall bei gesundem Guardian/Shim den Fail-stop
   nicht verhindert;
3. dass Thread-/Seccomp-/FD-Autoritäten, Renewal-Authentisierung und Timer-
   Besitz ausführbar und widerspruchsfrei sind;
4. dass das endliche Capability-Envelope eine vollständig berechenbare
   Einzeltrial-PASS/FAIL-Regel besitzt und nicht als universeller Worst Case
   missverstanden wird;
5. dass Single-Thread-I/O, Gesamtprozess-Stop, Termination-Anforderung und Reap
   weiterhin sauber getrennt sind;
6. dass sämtliche zuvor geschlossenen Findings und Scope-Grenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
