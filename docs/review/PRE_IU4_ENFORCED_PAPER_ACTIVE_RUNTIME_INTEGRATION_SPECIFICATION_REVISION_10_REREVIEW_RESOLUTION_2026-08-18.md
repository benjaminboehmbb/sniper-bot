# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-10 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-10 REREVIEW FINDING RESOLVED IN REVISION 11 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V10-Hash:** `559e4679ab3927cc169c92ac91fada4294e5574a07bf78bf07c771cd0f2731d2`
- **Revision-9-Rereview-Resolution-Record:** `80ea15f6b38a29b17ca691c74df255a8a2c3f037b98af821a8817debca0a20e0`
- **Resolution-Zielhash V11:** `a84efdb53f324d2e67f214d64edce1665a8e4a39525e93b7d94b441fc777607d`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker des unabhängigen read-only Re-Reviews der
Revision 10 konkreten normativen Korrekturen in Revision 11 zu.

Es zertifiziert die Korrektur nicht selbst. Der Resolutionstatus lautet
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V11-Hashes darf das Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V10-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V10_SHA256: 559e4679ab3927cc169c92ac91fada4294e5574a07bf78bf07c771cd0f2731d2
REVISION_9_RESOLUTION_SHA256: 80ea15f6b38a29b17ca691c74df255a8a2c3f037b98af821a8817debca0a20e0
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 0
MEDIUM: 0
LOW: 0
```

| Finding | V10-Re-Review | V11-Resolution |
|---|---|---|
| V10-B1 Post-OPEN-Fork kann letzten Pipe-Writer festhalten | OPEN | feste Task-/FD-Topologie, TSYNC-Prozessbildungssperre und vollständige Writer-Referenzgrenze |

Das V10-Re-Review bestätigte die eigentliche Trip-Returnwertmaschine aus
V9-B1, ließ dessen übergeordnete no-record-HUP-Garantie wegen V10-B1 aber noch
nicht vollständig schließen. V9-M1 wurde vollständig geschlossen. V8-H1 und
sämtliche übrigen älteren Findings blieben geschlossen beziehungsweise
bewahrt.

---

## 3. Resolution des Blockers

### V10-B1 — Post-OPEN-Prozessbildung konnte den letzten Writer festhalten

**Bestätigter Konflikt:** Revision 10 band bei OPEN genau ein Trading-Write-
Ende und ein Broker-Read-Ende. Bei `TRIP_RECORD_NOT_PROVEN` schloss der native
Entry den Writer und stützte einen der beiden unabhängigen Fail-stop-Pfade auf
Broker-HUP/EOF nach Verlust des letzten Writers. Die Trading-/Python-Seccomp-
Matrix sperrte jedoch weder `fork`, `vfork`, prozesserzeugendes `clone` noch
`clone3`. `CLOEXEC` verhindert keine Vererbung über diese Syscalls. Ein nach
OPEN erzeugtes Child konnte deshalb den Writer offen halten; bei gleichzeitig
fehlerhaftem Self-PIDFD-Signal blieb Broker-HUP/EOF aus und Renewals konnten
theoretisch fortgesetzt werden.

**Resolution in V11:**

1. `TerminalTradingTaskTopologyV1` bindet vor Ready exakt den Trading-TGID,
   sämtliche TIDs, Startzeiten und Rollen, den Shim-TID, den Session-Cgroup-
   und PID-Namespace-Fingerprint sowie alle Basis- und Rollenfilterhashes.
2. Jeder Trading-/Python-/Shim-TID muss per `kcmp(...,KCMP_FILES,...)` exakt
   dieselbe Files Table wie der Trading-Leader nachweisen. Fehlende
   Berechtigung oder ein unbekannter/abweichender Task blockiert OPEN.
3. Nach Erzeugung aller benötigten Threads wird ein gemeinsamer Basisfilter per
   `SECCOMP_FILTER_FLAG_TSYNC` auf die vollständige TID-Menge angewandt. Er
   sperrt ohne Flag-Ausnahme `fork`, `vfork`, `clone`, `clone3`, `unshare`,
   `setns`, `execve`, `execveat` und `close_range`.
4. Klassisches `clone` hat bewusst keine Thread-Ausnahme. Alle Threads und
   Pools müssen vor Filterung existieren. `clone3` ist vollständig gesperrt,
   weil klassisches Seccomp seine pointerreferenzierte Argumentstruktur nicht
   dereferenzieren kann.
5. Jeder verbotene Taskbildungsversuch endet exakt mit
   `SECCOMP_RET_KILL_PROCESS`. Ein bloßes Userspace-`EPERM`, ein Callback oder
   eine behauptete Pointerprüfung ist keine Sicherheitsgrenze.
6. Die Writer-FD-Oberfläche ist eine Default-deny-Allowlist. Der Writer darf
   ausschließlich als skalares FD-Argument von nonblocking
   `write(writer_fd,buf,8)` oder `close(writer_fd)` auftreten. Nach Ready ist
   zusätzlich jeder FD-erzeugende Syscall gesperrt, sodass die nach `close`
   freie numerische Writer-FD-Nummer bis zum Prozessende nicht wiederverwendet
   werden kann.
7. Verboten sind insbesondere `dup*`, beide `F_DUPFD`-Varianten,
   `pidfd_getfd`, neue File-Opens einschließlich `/proc/self/fd`,
   `SCM_RIGHTS` über `sendmsg`/`recvmsg`, io_uring, Legacy-AIO,
   pointerbasierte FD-Multiplexer und writerbezogene epoll-/splice-/tee-/
   vmsplice-/sendfile-/copy_file_range-/vector-I/O-/fcntl-/ioctl-Operationen.
   Jeder Writer-Referenzbildungsversuch endet ebenfalls mit
   `SECCOMP_RET_KILL_PROCESS`.
8. Vor OPEN werden `/proc/<pid>/fd`, `/proc/<pid>/fdinfo`, Cgroup- und
   Taskinventur vollständig gebunden. Unbekannte Pipe-Inode-Referenzen,
   io_uring-FDs oder writerbezogene epoll-`tfd`-Einträge verhindern OPEN;
   Bootstrap-Transfer-Sockets sind geschlossen und verbleibende Unix-Peers
   exakt inventarisiert. Danach binden Trading-`PR_SET_DUMPABLE=0`, leere
   Capability-Sets, `no_new_privs` und die Ptrace-/Yama-Policy auch externe
   `pidfd_getfd`-Versuche aus dem zulässigen Envelope aus.
9. Weil sämtliche bestehenden Trading-TIDs dieselbe Files Table teilen und
   kein neuer Task oder Kernel-FD-Halter entstehen kann, entfernt der atomare
   Slot-Entzug mit einmaligem Linux-`close` tatsächlich die letzte Writer-
   Referenz. Ein fehlerhaftes Self-PIDFD-Signal lässt deshalb den unabhängigen
   Broker-HUP-/EOF-Pfad weiterhin wirken.
10. Capability Profile und Pflicht-Fault-Matrix führen jeden Taskbildungs- und
    Writer-Referenzweg in einem frischen Probe-TGID unter den produktiven
    Filtern aus. Bei gleichzeitig erzwungenem Self-PIDFD-Fehler dürfen kein
    Child, TID, Files-Table-Split oder Writer-Halter entstehen;
    `SECCOMP_RET_KILL_PROCESS` muss den gesamten TGID beenden und der dadurch
    verlorene letzte Writer innerhalb `5 ms` als Broker-HUP/EOF-Trip-CAS
    linearisiert werden. Der getrennte Self-PIDFD-Fehler-/no-record-Close-Trial
    bleibt zusätzlich Pflicht.

Damit ist die HUP-Strecke keine nur beim Bootstrap beobachtete Annahme mehr,
sondern ein über die gesamte OPEN-Session OS-erzwungener Task-, Files-Table-
und Writer-Referenzvertrag.

**Betroffene V11-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 16.2.1, 17, 19, 20, 23
und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Versionierung und Bewahrung geschlossener Findings

Der geänderte Vertrag ist eindeutig versioniert als:

- `IU4RuntimeControlProfileV5`;
- Runtime Session Envelope V6;
- `TerminalParentGuardianV5`;
- `TerminalTripRequestPipeV3`;
- `TerminalLeaseCapabilityProfileV4`;
- neuer `TerminalTradingTaskTopologyV1`.

Unverändert beziehungsweise weiterhin gültig bleiben
`TerminalNativeTripBrokerV2`, `TerminalKernelLeaseShimV3`,
`TerminalLeaseControlWordV2`, `TerminalBrokerRenewalApprovalV1` und
`TerminalWorkerKillRequestV2`.

Revision 11 bewahrt ausdrücklich:

- die in V10 korrigierte vollständige Trip-Write-Returnwertmaschine,
  `SIGPIPE=SIG_IGN`, einmaligen Close ohne EINTR-Retry und den Self-PIDFD-
  Fallback;
- V9-M1: exakte `MFD_CLOEXEC|MFD_ALLOW_SEALING`-Erzeugung, initialen
  Seal-State 0 und sämtliche erlaubten Seal-Transitionen;
- V8-H1: Broker-Prozessgrenze, alleinige Broker-RW-Map, kein Trading-Worker-FD
  und receiverseitige Worker-Prüfung der erfolgreichen Trip-CAS;
- das endliche Timing-/Last-/Observer-Envelope und die Trennung von
  Termination-Anforderung und physischem Reaping;
- DIRECT-/Recovery-/Genesis-, Authority-, Handoff-, Atomic-State-, Loss-,
  Throttle-, Execution-Control- und L0/L1-Sicherheitsverträge;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- sämtliche bestehenden Implementierungs-, ENFORCED-, Exchange- und Live-
  Nichtfreigaben.

---

## 5. Vollständigkeits- und Scope-Nachweis

```text
REVISION_10_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 0/0
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
V9_B1_FULL_ERROR_DOMAIN_ADDRESSED_PENDING_REREVIEW: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTION_APPLIED: YES
REVISION_11_HASHED: YES
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

## 6. Nächster zulässiger Schritt

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-11-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass die vollständige TID-Menge vor Writer-Freigabe existiert und die
   gemeinsame Files Table per `KCMP_FILES` technisch ausführbar gebunden ist;
2. dass TSYNC und die gestapelten Rollenfilter für sämtliche TIDs gelten und
   weder klassisches `clone` noch `clone3` eine Prozess-/Thread-Ausnahme hat;
3. dass jeder Taskbildungsversuch mit `SECCOMP_RET_KILL_PROCESS` endet, ohne
   einen Child-/Thread-Writer zu hinterlassen;
4. dass die Default-deny-Syscallmatrix jede zweite Kernel-Referenz auf den
   Writer verhindert und keine nicht dereferenzierbare BPF-Payload behauptet;
5. dass der kombinierte Post-OPEN-Taskbildungs-/Self-PIDFD-Fehler-Fault und der
   getrennte no-record-Close-/HUP-Fault jeweils deterministisch bestehen;
6. dass V9-B1, V9-M1, V8-H1 und sämtliche älteren geschlossenen Findings sowie
   alle Scope- und Freigabegrenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
