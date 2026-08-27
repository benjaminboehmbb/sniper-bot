# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-12 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-12 REREVIEW FINDING RESOLVED IN REVISION 13 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V12-Hash:** `3b46f32ed460033bce6d81284a2f9e4d211b48962dd7c5e552658a38a4c445a3`
- **Revision-11-Rereview-Resolution-Record:** `088943bd5a6605d5fae93628141c1b7ac54eca43ba86c9ddd25ba8b668f66ea9`
- **Resolution-Zielhash V13:** `e8c14a631928914c823a046dc5a85972dfccbbbd48e41897e66926db3e5f1f66`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker des unabhängigen read-only Re-Reviews der
Revision 12 konkreten normativen Korrekturen in Revision 13 zu.

Es zertifiziert die Korrektur nicht selbst. Der Resolutionstatus lautet
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V13-Hashes darf das Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V12-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V12_SHA256: 3b46f32ed460033bce6d81284a2f9e4d211b48962dd7c5e552658a38a4c445a3
REVISION_11_RESOLUTION_SHA256: 088943bd5a6605d5fae93628141c1b7ac54eca43ba86c9ddd25ba8b668f66ea9
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 0
MEDIUM: 0
LOW: 0
```

| Finding | V12-Re-Review | V13-Resolution |
|---|---|---|
| V12-B1 Nonblocking Pipe-Write besitzt weiterhin unbeschränkten Kernel-Ressourcenpfad | OPEN | Pipe-Write und Pipe-Read vollständig aus dem Terminal-Sicherheitsweg entfernt; Self-Kill-first plus zwei PIDFD-Fallbacks vor Close-only-Liveness-HUP |

Das V12-Re-Review bestätigte, dass die exakte Pointerbindung und die residenten,
gelockten Buffer den User-Page-Fault-Anteil von V11-B1 schließen. Es bestätigte
außerdem die aktuelle Versionsfamilie und ließ V10-B1, V9-B1, V9-M1, V8-H1
sowie sämtliche übrigen älteren Findings geschlossen. Der verbleibende Blocker
lag ausschließlich hinter der bereits erfolgreichen FD-/Pointer-Auflösung im
Kernel-Pipe-Pfad.

---

## 3. Resolution des Blockers

### V12-B1 — Pipe-Page-Allokation konnte vor Returnwert und Fallback blockieren

**Bestätigter Konflikt:** Auch ein `O_NONBLOCK`-Write mit residentem, gelocktem
Userbuffer kann nach `fdget` vor seiner Returnwertklassifikation eine Pipe-Page
allokieren, den Cgroup-Memory-Charge ausführen, in Direct Reclaim, Compaction
oder Writeback geraten oder auf Pipe-Lock und Scheduling warten. Die V12-
Capability-Trials und die vorreservierte 64-MiB-Reserve waren ein endlicher
Messvertrag, aber keine ausführbare Kernel-Obergrenze für diesen Pfad. Damit
konnte der Thread noch vor Close und Self-PIDFD-Fallback hängen bleiben.

**Resolution in V13:**

1. `TerminalTripRequestPipeV4` wird durch
   `TerminalTripLivenessPipeV1` ersetzt. Der Kanal ist von Erzeugung bis Ende
   dauerhaft leer und ausschließlich ein Close-only-Liveness-Kanal.
2. Trading darf auf dem Liveness-Writer nur exakt `close(fd)` ausführen. Jeder
   `write`, vectored I/O, `splice`, `vmsplice`, `tee`, `sendfile` oder
   äquivalente Datentransfer endet vor FD-Auflösung mit
   `SECCOMP_RET_KILL_PROCESS`. Der Broker pollt nur HUP/ERR/POLLIN und liest die
   Pipe nie. POLLIN ist unmöglich und wird fail-safe als Trip behandelt.
3. `TerminalSelfKillEntryV1::terminal_trip()` setzt zuerst den lokalen one-way
   Latch. Sein erster Kernelaufruf ist danach zwingend
   `pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)`.
4. Nur wenn dieser Aufruf überhaupt zurückkehrt, folgen ohne Retry und in fester
   Reihenfolge Guardian-PIDFD-`SIGKILL`, Broker-PIDFD-`SIGKILL` und zuletzt der
   atomare Entzug des einzigen Liveness-Writers mit genau einem rohen Close.
5. Self-Kill stoppt den Trading-Prozess; Guardian-Kill stoppt die Renewal-
   Quelle; Broker-Kill stoppt Approval und Control-Word-Fortschritt. Damit liegt
   vor jeder Pipe-Operation bereits eine kernel-seitig akzeptierte Fatal-Action
   vor, sofern eine der drei Signalanforderungen erfolgreich ist.
6. Scheitern alle drei PIDFD-Signale, wird der dauerhaft leere Writer
   geschlossen. Weil niemals ein Pipe-Write zulässig war, existieren dabei
   keine diesem Kanal zurechenbare Pipe-Page, kein Payload-Copy und keine
   temporäre Write-Referenz. Ein gesunder Broker erkennt HUP; ein gestoppter,
   toter oder dauerhaft nicht schedulable Broker kann unabhängig vom Close
   keine Approval erzeugen.
7. Close wird auch bei `EINTR` nie wiederholt. Post-Ready-Task-/FD-Erzeugung,
   Duplikation, Transfer und Kernel-Registrierung bleiben vollständig gesperrt,
   sodass kein zweiter Writer den HUP verhindern kann.
8. Das orderly-close-Protokoll wird passend geordnet: durable Session CLOSE und
   Reconciliation erfolgen bei lebendem, gegatetem Child; danach linearisiert
   der Broker RUNNING→CLOSED, erst dann werden Timer-Disarm und Child-Exit
   erlaubt. HUP vor CLOSED ist immer ein Trip, HUP nach CLOSED nur Exit-Evidenz.
9. Capability-, Fault- und Per-Startup-Matrizen prüfen die vier Signal-/Close-
   Fälle getrennt, Close-`EINTR`, jede verbotene Pipe-I/O-Klasse, null
   Pipe-Bytes/-Pages und die Orderly-Close/Renewal-Races.

Damit wurde nicht versucht, den Kernel-Ressourcenpfad eines Pipe-Writes enger
zu messen. Der problematische Syscall besitzt im Sicherheitsweg keinerlei
Autorität mehr; die primäre Fatal-Action wird vor dem einzigen verbleibenden
Pipe-Syscall angefordert.

**Betroffene V13-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 16.2.1, 17, 18, 19, 20,
22, 23 und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Versionierung und Bewahrung geschlossener Findings

Der geänderte Vertrag ist eindeutig versioniert als:

- `IU4RuntimeControlProfileV7`;
- Runtime Session Envelope V8;
- neuer `TerminalTripLivenessPipeV1`;
- neuer `TerminalSelfKillEntryV1`;
- `TerminalLeaseCapabilityProfileV6`;
- `TerminalParentGuardianV6`;
- `TerminalNativeTripBrokerV3`;
- `TerminalKernelLeaseShimV4`.

Unverändert beziehungsweise weiterhin gültig bleiben
`TerminalTradingTaskTopologyV1`, `TerminalLeaseControlWordV2`,
`TerminalBrokerRenewalApprovalV1` und `TerminalWorkerKillRequestV2`.

Revision 13 bewahrt ausdrücklich:

- V11-B1: frei wählbare Userbuffer und post-Ready Mapping-/Reclamation-Pfade
  erhalten keine Pipe-I/O-Autorität; das Finding wird zusätzlich durch
  vollständige Entfernung der Pipe-I/O obsolet;
- V11-M1: alle normativen Implementierungs- und Abschlussgates verwenden
  dieselbe aktuelle Vertragsfamilie;
- V10-B1: feste TID-Menge, gemeinsame Files Table, TSYNC-Prozessbildungssperre,
  Post-OPEN-FD-Erzeugungs-/Duplikationssperre und KILL_PROCESS;
- V9-B1: EINTR kann keinen still fortgesetzten Renewal-Pfad öffnen; jeder
  zurückkehrende PIDFD-Fehler fällt zur nächsten Stufe, Close wird nie
  wiederholt;
- V9-M1: exakte Memfd-Erzeugung und Seal-State-Machine;
- V8-H1: Broker-Prozessgrenze, alleinige Broker-RW-Map, kein Trading-Worker-FD
  und receiverseitige Worker-Prüfung der Trip-CAS;
- alle DIRECT-/Recovery-/Genesis-, Authority-, Handoff-, Atomic-State-, Loss-,
  Throttle-, Execution-Control- und L0/L1-Sicherheitsverträge;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- sämtliche Implementierungs-, ENFORCED-, Exchange- und Live-Nichtfreigaben.

---

## 5. Vollständigkeits- und Scope-Nachweis

```text
REVISION_12_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 0/0
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
V11_B1_USER_BUFFER_CLOSURE_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES
V9_B1_FULL_ERROR_DOMAIN_ADDRESSED_PENDING_REREVIEW: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTION_APPLIED: YES
REVISION_13_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-13-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass kein Pipe-Read, -Write oder Datentransfer im Terminal-Sicherheitsweg
   mehr erlaubt ist und die Liveness-Pipe bis Close garantiert leer bleibt;
2. dass der erste Kernelaufruf nach dem lokalen Latch zwingend Self-PIDFD-
   `SIGKILL` ist und jede zurückkehrende Fehlerklasse exakt Guardian-PIDFD,
   Broker-PIDFD und Liveness-Close erreicht;
3. dass alle drei PIDFDs Ziel, Startzeit, Signal-0-Probe, Signal, Nullzeiger und
   Flags ausführbar und fail-safe binden;
4. dass kein Post-Ready-Task, FD, Transfer oder Kernel-Halter den letzten
   Liveness-Writer bewahren kann;
5. dass HUP in RUNNING vor jeder Renewal TERMINATING linearisiert, Broker-Tod
   jede Approval beendet und HUP in CLOSED nur nach vollständig geordnetem
   Close auftreten kann;
6. dass Capability-/Fault-/Preflight-Matrizen null Pipe-Bytes/-Pages, alle vier
   Signal-/Close-Fälle, Close-`EINTR` und beide relevanten CAS-Races abdecken;
7. dass I2 und sämtliche `IMPLEMENTATION_COMPLETE`-Gates nur die aktuelle
   Vertragsfamilie referenzieren;
8. dass V11-B1, V11-M1, V10-B1, V9-B1, V9-M1, V8-H1 und sämtliche älteren
   Closures sowie alle Scope- und Freigabegrenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
