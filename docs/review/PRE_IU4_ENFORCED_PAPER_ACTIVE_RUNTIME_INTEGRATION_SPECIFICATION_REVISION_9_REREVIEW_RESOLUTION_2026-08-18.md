# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-9 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-9 REREVIEW FINDINGS RESOLVED IN REVISION 10 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V9-Hash:** `fc9a947274395a38fd287411ec171c1b1dc624f8ddfc7364ce3437ecf93e91b1`
- **Revision-8-Rereview-Resolution-Record:** `87f620301b1930e11373c3b65a7bd4791b47cc33c27c987c774d807b64d9d183`
- **Resolution-Zielhash V10:** `559e4679ab3927cc169c92ac91fada4294e5574a07bf78bf07c771cd0f2731d2`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker und das Medium-Finding des unabhängigen
read-only Re-Reviews der Revision 9 konkreten normativen Korrekturen in
Revision 10 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V10-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V9-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V9_SHA256: fc9a947274395a38fd287411ec171c1b1dc624f8ddfc7364ce3437ecf93e91b1
REVISION_8_RESOLUTION_SHA256: 87f620301b1930e11373c3b65a7bd4791b47cc33c27c987c774d807b64d9d183
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 0
MEDIUM: 1
LOW: 0
```

| Finding | V9-Re-Review | V10-Resolution |
|---|---|---|
| V9-B1 Trip-Pipe-Write kann ohne Record fehlschlagen und Broker renewt weiter | OPEN | vollständige Returnwert-Zustandsmaschine plus Pipe-HUP und Self-PIDFD-`SIGKILL` |
| V9-M1 Memfd-Seal-Bootstrap ohne Erzeugungsflags und Zustandsübergänge | OPEN | exakte `memfd_create`-Flags, initialer Seal-State und zwei `F_ADD_SEALS`-Transitionen |

Das V9-Re-Review schloss V8-H1 vollständig. V7-B1 war für die ausdrücklich
beschriebenen full/closed/dead/stall-Pfade geschlossen, wurde aber durch V9-B1
für den unbeschriebenen no-record-Write-Error-Pfad partiell wieder geöffnet.
Alle übrigen älteren Findings blieben geschlossen.

---

## 3. Resolution des Blockers

### V9-B1 — Kein Fail-stop-Nachweis bei `EINTR` vor Trip-Record

**Bestätigter Konflikt:** Revision 9 setzte den lokalen Request-Latch und führte
danach genau einen nonblocking Acht-Byte-Write auf die Trip-Pipe aus. Für
`EAGAIN`, `EPIPE`, `EBADF`, Broker-Tod und erkannten Kanalverlust waren Folgen
beschrieben, nicht jedoch für `EINTR` vor jeder Datenübertragung oder andere
Returnwerte ohne nachweisbaren Record. Ein gesunder Broker konnte in diesem
Pfad ohne Trip-Record und mit offenem Writer weiter Renewals und Approvals
ausgeben. Der lokale Latch blockierte zwar fachliche Side Effects, belegte aber
keine OS-Termination innerhalb 100 ms.

**Resolution in V10:**

- `TerminalTripRequestPipeV2` bindet exakt das einzige Trading-Write-Ende und
  das einzige Broker-Read-Ende samt Inode, FD-Nummern, Capacity und geschlossenem
  Bootstrap-Scope;
- die prozessweite `SIGPIPE`-Disposition ist vor Ready exakt `SIG_IGN` und
  danach für `SIGPIPE` unveränderlich, sodass Reader-Verlust deterministisch
  als `EPIPE` in den nativen Fallback gelangt;
- `TerminalParentGuardianV4` übergibt dem Trading-Prozess einen vorab geöffneten
  Self-PIDFD, dessen Ziel exakt derselbe Trading-PID samt Startzeit ist;
- der Self-PIDFD wird per Signal 0 geprüft und erlaubt ausschließlich
  `pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)`;
- die Write-Zustandsmaschine akzeptiert ausschließlich exakt 8 als
  `TRIP_RECORD_COMMITTED` und EAGAIN/EWOULDBLOCK bei unveränderter reiner Trip-
  Pipe als `TRIP_RECORD_ALREADY_PENDING`;
- jeder andere Returnwert beziehungsweise jedes andere `errno`, ausdrücklich
  `EINTR`, `EPIPE`, `EBADF`, `EIO`, 0, Teilwrite, unbekanntes `errno` oder
  Identitätsverlust, ist `TRIP_RECORD_NOT_PROVEN`;
- bei `TRIP_RECORD_NOT_PROVEN` gibt es keinen Write-Retry: Der native Entry
  tauscht den einzigen Write-FD-Slot atomar gegen -1, schließt den vorherigen FD
  genau einmal und fordert danach genau einmal Self-PIDFD-`SIGKILL` an;
- der Linux-`close` wird auch nach gemeldetem `EINTR` nicht wiederholt, weil der
  FD bereits freigegeben sein kann und ein Retry einen wiederverwendeten FD
  treffen könnte;
- Broker V2 behandelt `POLLHUP`, `POLLERR` und EOF nach Verlust des einzigen
  Writers exakt wie einen Trip-Record und priorisiert sie vor Renewals;
- ein gesunder Broker linearisiert deshalb HUP/EOF per
  `RUNNING→TERMINATING`; ein toter/stallender Broker erzeugt keine Approvals;
- Pipe-HUP und Self-PIDFD-`SIGKILL` sind unabhängige Pfade. Ein Fehler des einen
  darf den anderen nicht verhindern;
- rohe Close- oder Self-Signal-Aufrufe irgendeines Trading-Threads können wegen
  der festen FD-/Signalargumente ausschließlich fail-safe wirken; eine BPF-
  Callsite- oder Payload-Dereferenzierung wird nicht behauptet;
- `TERMINAL_FAILSTOP_ASSERTED` umfasst jetzt zusätzlich die kernel-seitige
  Annahme des Self-PIDFD-`SIGKILL` und die nach Pipe-HUP ausbleibende Approval
  mit expirierter Self-Death-Lease;
- Capability-Zertifizierung und Startup-Probes enthalten `EINTR` vor Record,
  alle übrigen Returnwertklassen, Close-`EINTR`, erfolgreichen Self-PIDFD-Pfad
  sowie erzwungenen Self-PIDFD-Fehler mit erfolgreichem Broker-HUP.

Damit kann kein no-record-Write-Fehler einen gesunden Broker bei weiter
erneuerbarer Lease unsichtbar lassen.

**Betroffene V10-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 16.2.1, 17, 18, 19, 20,
21.7, 23 und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des Medium Findings

### V9-M1 — Memfd-Seal-Sequenz war ohne `MFD_ALLOW_SEALING` nicht ausführbar

**Bestätigter Konflikt:** Revision 9 verlangte nach der bestehenden Broker-RW-
Map `F_SEAL_GROW`, `F_SEAL_SHRINK`, `F_SEAL_FUTURE_WRITE` und `F_SEAL_SEAL`,
band die Memfd-Erzeugung aber nicht an `MFD_ALLOW_SEALING`. Ohne dieses Flag
besitzt ein Linux-memfd initial `F_SEAL_SEAL`, sodass spätere Seal-Erweiterungen
unmöglich sind. Initialer State, `F_ADD_SEALS`-Calls und erlaubte Transitionen
waren nicht vollständig definiert.

**Resolution in V10:**

Die Bootstrap-Zustandsmaschine ist jetzt exakt:

1. `memfd_create("iu4-terminal-control-v2",
   MFD_CLOEXEC|MFD_ALLOW_SEALING)`; jeder fehlende, zusätzliche oder unbekannte
   Flag ist fail closed.
2. Der erste `F_GET_SEALS` muss exakt 0 liefern.
3. `ftruncate` erzeugt exakt eine gebundene System-Page; ein vollständiger
   Acht-Byte-`pwrite` initialisiert den kanonischen RUNNING-Wert, ohne eine
   Launcher-RW-Map zu erzeugen.
4. Der Broker erzeugt die einzige bestehende
   `MAP_SHARED`-/`PROT_READ|PROT_WRITE`-Map und schließt seinen Memfd-FD.
5. Der Launcher führt exakt
   `F_ADD_SEALS(F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_FUTURE_WRITE)` aus. Der
   Zwischenstate muss exakt diese drei Bits und weder `F_SEAL_WRITE` noch
   `F_SEAL_SEAL` enthalten.
6. Danach wird exakt `F_ADD_SEALS(F_SEAL_SEAL)` ausgeführt. Der finale State
   muss exakt die vier Pflichtbits enthalten.
7. `F_SEAL_WRITE` bleibt absichtlich abwesend, weil die bereits bestehende
   Broker-Map weiter schreiben muss. Nach `F_SEAL_SEAL` ist jede weitere
   Transition verboten.
8. Erst danach werden read-only Consumer-Maps erzeugt, alle Consumer-Memfd-FDs
   geschlossen und Guardian, Worker und Trading-Prozess gestartet.

Create-Flags, jeder Seal-State, Returncodes, Inode/Größe, Mapping-Rechte und
negative Abweichungen sind Teil von Session OPEN, Capability-Fingerprint,
Monitoring und Pflicht-Fault-Matrix. Fehlendes `MFD_ALLOW_SEALING`, initiales
`F_SEAL_SEAL`, verfrühtes `F_SEAL_SEAL`, vorhandenes `F_SEAL_WRITE`, falsche
Transition, Teilwrite, zweite writable Map oder unbekannter Mapper verhindert
OPEN.

**Betroffene V10-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 17, 18, 19, 20, 21.7, 23
und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Versionierung und Bewahrung geschlossener Findings

Der geänderte Vertrag ist eindeutig versioniert als:

- `IU4RuntimeControlProfileV4`;
- Runtime Session Envelope V5;
- `TerminalParentGuardianV4`;
- `TerminalNativeTripBrokerV2`;
- `TerminalTripRequestPipeV2`;
- `TerminalLeaseCapabilityProfileV3`.

Unverändert beziehungsweise weiterhin gültig bleiben
`TerminalKernelLeaseShimV3`, `TerminalLeaseControlWordV2`,
`TerminalBrokerRenewalApprovalV1` und `TerminalWorkerKillRequestV2`.

Revision 10 bewahrt ausdrücklich:

- V8-H1: Broker-Prozessgrenze, alleinige Broker-RW-Map, kein Trading-Worker-FD,
  keine unmögliche Seccomp-Payload-/Callsite-Behauptung und unabhängige Worker-
  Prüfung von `(TERMINATING,n,1)`;
- V7-B1 für alle bisherigen Fehlerpfade und schließt zusätzlich die partielle
  no-record-Regression V9-B1 pending independent rereview;
- das endliche Timing-/Last-/Observer-Envelope und die Trennung von Single-
  Thread-I/O und vollständigem Child-Stop;
- nicht übertragbare DIRECT-Genesis-Continuation, exakte Genesis-Sentinels und
  zwingendes `RESTART_ONLY` nach Prozesswechsel oder recovered Completion;
- journal-first Terminal-Gap-Reconciliation und Exactly-once Control Event ID;
- Worker Lease/Fencing vor Recovery;
- Trennung von Termination-Anforderung, pending Signal und Reaping ohne feste
  Reap-Deadline;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- Authority-Root-/Generation-/PREPARE-Tamper-Tests, vollständige S4-/Loss-/
  Throttle-/Progress-Handoffs sowie alle bestehenden Aktivierungsgrenzen.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_9_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 0/0
MEDIUM_FINDINGS_MAPPED: 1/1
LOW_FINDINGS_MAPPED: 0/0
V8_H1_CLOSED_STATUS_PRESERVED: YES
V7_B1_FULL_ERROR_DOMAIN_ADDRESSED_PENDING_REREVIEW: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_10_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-10-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass jede Trip-Pipe-Write-Returnklasse vollständig und ohne unbeschränkten
   Retry entweder committed/pending oder `TRIP_RECORD_NOT_PROVEN` ist;
2. dass FD-Slot-Entzug, Linux-Close-/HUP-Semantik und Self-PIDFD-`SIGKILL`
   unabhängig verhindern, dass ein gesunder Broker nach no-record weiter
   renewt;
3. dass Self-PIDFD-, Pipe-Enden-, `SIGPIPE`- und Seccomp-Bindungen technisch
   ausführbar sind und rohe erlaubte Aufrufe ausschließlich fail-safe wirken;
4. dass `MFD_ALLOW_SEALING`, initialer Seal-State, beide `F_ADD_SEALS`-
   Transitionen, fehlendes `F_SEAL_WRITE` und finaler `F_SEAL_SEAL`-State auf
   Linux/WSL exakt ausführbar sind;
5. dass Capability-/Startup-Probes alle positiven und negativen neuen Pfade
   deterministisch mit Einzeltrial-PASS/FAIL abdecken;
6. dass V8-H1, V7-B1 und sämtliche älteren geschlossenen Findings sowie alle
   Scope- und Freigabegrenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
