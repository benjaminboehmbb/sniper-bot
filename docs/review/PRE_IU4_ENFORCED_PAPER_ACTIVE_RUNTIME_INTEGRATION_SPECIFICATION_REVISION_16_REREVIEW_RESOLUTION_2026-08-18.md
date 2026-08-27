# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-16 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-16 REREVIEW FINDING RESOLVED IN REVISION 17 — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand / HEAD / main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **main gegenüber origin/main:** `0 behind / 6 ahead`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V16-Hash:** `093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f`
- **Unabhängig geprüfte V16-Zeilen:** `3760`
- **Revision-16-Independent-Rereview-Record:** `85068c49739e5016ff9ec0a614e3dcdac97a352594cc3839cf7ce8414e5f80df`
- **Revision-16-Independent-Rereview-Zeilen:** `330`
- **Controlling Revision-15-Resolution:** `d4377470cb3298619a312267feba8bbe3a22a1bd702567b97d788fc22a075879`
- **Controlling Revision-15-Resolution-Zeilen:** `342`
- **Resolution-Zielhash V17:** `ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64`
- **Resolution-Zielzeilen V17:** `3865`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet das einzige offene Finding `V16-H1` des unabhängigen
read-only Re-Reviews der Revision 16 einer normativen Korrektur in Revision 17
zu. Das Finding betrifft eine in der AF_UNIX-Receive Queue fortbestehende
`SCM_RIGHTS`-Referenz, wenn der Empfänger nach einem erfolgreichen `sendmsg`,
aber vor `recvmsg`, stoppt oder dauerhaft stallt.

Dieses Resolution-Protokoll zertifiziert die Korrektur nicht selbst. Der
Resolutionstatus lautet `RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein
neues unabhängiges read-only Re-Review des vollständigen V17-Hashes darf
`V16-H1` schließen oder die Spezifikation als READY bewerten.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Vorhandene untracked Benutzerartefakte wurden nicht bereinigt,
überschrieben oder gestaged.

---

## 2. Ausgang des unabhängigen V16-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V16_SHA256: 093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f
SPEC_V16_LINES: 3760
REVISION_15_RESOLUTION_SHA256: d4377470cb3298619a312267feba8bbe3a22a1bd702567b97d788fc22a075879
REVISION_16_REREVIEW_SHA256: 85068c49739e5016ff9ec0a614e3dcdac97a352594cc3839cf7ce8414e5f80df
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V16-Re-Review | V17-Resolution |
|---|---|---|
| `V16-H1` | NULL/0-Controlbuffer autocloset Rights erst bei einem tatsächlich vollendeten `recvmsg` oder bei Queue-Zerstörung. Bis dahin kann ein gestoppter Empfänger das receive-queue-SKB samt file-/OFD-/Lock-Referenz nach Sender-Close/-Crash unbeschränkt halten. | Jeder finale Empfangsendpunkt erhält vor dem ersten Send attestiert `SO_PASSRIGHTS=0`. AF_UNIX weist einen Rights-Send mit `EPERM` ab und verwirft das SKB vor dem Queueing. Stop/Crash des Empfängers benötigt dadurch keinen Receive-Fortschritt mehr. |

Das Re-Review bestätigte `V15-B1` als geschlossen. `V15-H1` blieb allein über
den engeren in-flight-Queue-Fall `V16-H1` offen. Revision 17 verändert den
Signal-/Seccomp-Notification-Vertrag nicht und bewahrt die Schließung von
`V15-B1`.

---

## 3. Bestätigter technischer Konflikt

Revision 16 beseitigte die Mutation der Empfänger-FD-Tabelle: Ein
`recvmsg` mit `msg_control=NULL` und `msg_controllen=0` installiert keinen
userspace-sichtbaren Rights-FD und lässt den Kernel die nicht zustellbaren
Rights schließen. Dieser Vertrag begann jedoch erst beim Receive.

Bei einem davor erfolgreichen AF_UNIX-`sendmsg` übernimmt der Kernel bereits
file-Referenzen in das Socket-SKB. Solange der Empfänger kein `recvmsg`
ausführt und Socket beziehungsweise Queue fortbestehen, hält dieses SKB die
Open-File-Description und damit gegebenenfalls Locks oder andere
Lebensdauerwirkungen. Sender-Close oder Sender-Crash beseitigt diese separate
Queue-Referenz nicht. Ein gestoppter oder dauerhaft stallender Empfänger macht
den V16-Autoclose-Vertrag deshalb zeitlich unbeschränkt.

Klassisches Seccomp kann den `msghdr`-Pointer des erlaubten `sendmsg` nicht
dereferenzieren. Eine senderseitige Aussage „kein `SCM_RIGHTS`“ ist damit
weiterhin keine Kernel-Enforcement-Grenze.

Die gebundene Linux-Familie besitzt hierfür `SO_PASSRIGHTS`. Der Upstream-
Commit
[`77cbe1a6d8730a07f99f9263c2d5f2304cf5e830`](https://github.com/torvalds/linux/commit/77cbe1a6d8730a07f99f9263c2d5f2304cf5e830)
führte die Option für AF_UNIX ein. Sie ist aus Kompatibilitätsgründen
standardmäßig aktiviert. Wird sie am Empfangssocket auf `0` gesetzt, lehnt
AF_UNIX einen Send mit `SCM_RIGHTS` mit `EPERM` ab und gibt das nicht
eingereihte SKB frei. Dabei eventuell innerhalb des Syscalls kurzzeitig
erworbene file-Referenzen müssen vor dem Syscall-Return freigegeben sein.

Die Resolution darf daher weder auf den Kernel-Default noch auf unbekannte
Vererbung eines Listenerzustands vertrauen. Autoritativ ist ausschließlich der
nach `accept4` gesetzte und zurückgelesene Zustand des finalen
Empfangsendpunkts.

---

## 4. Resolution von V16-H1

### 4.1 Pre-Send-Kernelbarriere

1. `TerminalRuntimeChannelProvisioningV2` setzt für jeden der sechs Kanäle
   bereits am Listener `SO_PASSRIGHTS=0`, behandelt diesen Zustand aber nur
   als Defense in Depth. Eine Vererbung auf den akzeptierten Socket wird nicht
   vorausgesetzt (Spezifikation Zeilen 1443–1457).
2. Nach `accept4` setzt der endgültige Empfänger auf dem **finalen
   Empfangsendpunkt** erneut `setsockopt(SOL_SOCKET, SO_PASSRIGHTS, 0)` und
   verlangt beim unmittelbaren `getsockopt` exakt `0`. Fehler,
   `ENOPROTOOPT`/`EOPNOTSUPP` oder ein anderer Rücklesewert verhindern Ready
   und OPEN (Zeilen 1443–1464).
3. Bis Peeridentität und Rights-Disabled-Zustand attestiert sind, ist jeder
   Runtime-/Applikations-Send normativ verboten. Erst die vollständige
   Barriere aller sechs Kanäle erlaubt Rollenfilter-Finalisierung und
   `RUNTIME_SESSION_OPEN` (Zeilen 1449–1456).
4. Vor OPEN müssen `/proc/<receiver>/fdinfo/<fd>` exakt `scm_fds: 0` und die
   gebundene Queue-Inventur einen leeren Anfangszustand zeigen. Kein bereits
   wartendes Ancillary-SKB darf in die Runtime übernommen werden (Zeilen
   1452–1456).
5. Nach Ready beendet jeder `setsockopt`-Versuch den betreffenden TGID mit
   `SECCOMP_RET_KILL_PROCESS`. Kein Rollenprozess kann die Option erneut
   aktivieren (Zeilen 1458–1464).

### 4.2 Kernel-/Capability-Bindung

1. Revision 17 bindet Linux mindestens 6.16, den exakten Kernel-/WSL-Build,
   UAPI/Headers, die `SO_PASSRIGHTS`-Implementierungsidentität und Upstream-
   Commit `77cbe1a6d8730a07f99f9263c2d5f2304cf5e830` in
   `TerminalLeaseCapabilityProfileV10` (Zeilen 1625–1649).
2. Unbekannter Support, abweichende Set/Get-Semantik oder eine nicht gebundene
   Kernelimplementierung bleibt fail closed. Der frühere NULL/0-Controlbuffer
   ist ausdrücklich kein zulässiger Fallback für fehlendes `SO_PASSRIGHTS`
   (Zeilen 1458–1463).
3. Die primäre Erfolgssemantik lautet für einen syntaktisch gültigen
   Rights-Fault: `sendmsg == -1`, `errno == EPERM`, kein Einreihen in die
   Receive Queue, `scm_fds == 0` und keine nach Return fortbestehende file-/
   OFD-/Lock-Referenz (Zeilen 1501–1514).
4. `EPERM` ist in der totalen Transport-FSM terminal und nicht retrybar. Bei
   einem Fault ist es der erwartete Kernelbarrierenachweis; bei einer
   fachlichen Nachricht ist es ein Capability-/Protokollkonflikt (Zeilen
   1571–1584).

### 4.3 Defense in Depth

Jeder Empfänger behält `msg_control=NULL` und `msg_controllen=0`. Dieser
Receive-Autoclose-Pfad ist in Revision 17 nur noch Defense in Depth, falls ein
Fault-Fixture die primäre Barriere künstlich umgeht. Regulär erreicht kein
Rights-Paket `recvmsg`; `MSG_CTRUNC` ist weiterhin terminal und kein Auftrag
für einen mit den Rollenfiltern kollidierenden Userspace-Cleanup (Zeilen
1521–1535).

### 4.4 Stop-/Crash-totaler Nachweis

Capability-, Startup-, Fault- und Completion-Gates prüfen jeden der sechs
Kanäle mit einzelnen und mehreren CMSGs sowie einem bis `SCM_MAX_FD` FDs. Die
Matrix kombiniert:

- Empfänger-`SIGSTOP` oder Empfänger-Crash vor jedem `recvmsg`;
- Sender-Close oder Sender-Crash nach dem fehlgeschlagenen Send;
- alle CMSG-Reihenfolgen und gebundene Last-/FD-Limits;
- exaktes, nicht retrybares `EPERM` vor Queueing;
- dauerhaftes `scm_fds: 0`;
- byteidentische Queue-, FD-, FDINFO-, OFD- und Lock-Inventuren;
- einen getrennten künstlichen Guard-Bypass für den NULL/0-Controlbuffer-
  Autoclose-Nachweis.

Kein Empfängerfortschritt ist für den primären PASS mehr erforderlich. Das
schließt genau die von `V16-H1` benannte unbeschränkte Queue-Lebensdauer
(Spezifikation Zeilen 1729–1734, 1798–1813, 1829–1848, 3605–3619 und
3771–3816).

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Autoritäts- und Fehlerwirkung

| Grenze | Normative Autorität | Zulässiges Ergebnis |
|---|---|---|
| Listener | `SO_PASSRIGHTS=0`, nur Defense in Depth | keine Vererbungsbehauptung |
| finaler akzeptierter Empfangsendpunkt | Set/Get exakt `0` vor erstem Send | Voraussetzung für Ready |
| alle sechs Endpunkte | Peerbindung, Rights-Barriere, `scm_fds: 0`, leere Queue | Voraussetzung für OPEN |
| gültiger Rights-Fault | Kernel prüft Peer-`SO_PASSRIGHTS=0` | `EPERM`, kein Queueing |
| Empfänger stoppt/stirbt vor Receive | kein SKB wurde eingereiht | kein Empfängerfortschritt nötig |
| Sender schließt/stirbt | syscall-interne Referenzen bereits freigegeben | keine OFD-/Lock-Lebensdauer |
| post-Ready `setsockopt` | Rollen-Seccomp | `SECCOMP_RET_KILL_PROCESS` |
| künstlicher Guard-Bypass | NULL/0-Controlbuffer | Autoclose, `MSG_CTRUNC`, terminal |
| abweichende Beobachtung | `PEE_IU4_TERMINAL_CHANNEL_ANCILLARY_INVALID` | kein OPEN oder terminal fail closed |

Die Barriere ist receiverseitig, weil genau der Empfangssocket die
Queue-Autorität besitzt. Sie beansprucht nicht, dass klassisches Seccomp den
`msghdr` inspiziert. Sie beansprucht ebenso wenig, dass im Kernel vor dem
`SO_PASSRIGHTS`-Check überhaupt keine transienten `fget`-Referenzen entstehen;
verlangt wird ihre vollständige Freigabe vor dem `sendmsg`-Return und das
Ausbleiben jeder queued oder danach fortbestehenden Referenz.

---

## 6. Versionierung und Preservation

Die Revision-17-Vertragsfamilie lautet exakt:

- `IU4RuntimeControlProfileV11`;
- Runtime Session Envelope V12;
- `TerminalLeaseControlWordV3`;
- `TerminalTradingSignalEnvelopeV1`;
- `TerminalKernelTripRequestV2`;
- `TerminalSelfKillEntryV4`;
- `RuntimeSessionCloseProtocolV5`;
- `TerminalRuntimeChannelProvisioningV2`;
- `TerminalParentGuardianV10`;
- `TerminalNativeTripBrokerV7`;
- `TerminalKernelLeaseShimV8`;
- `TerminalPersistenceWorkerV4`;
- `TerminalLeaseCapabilityProfileV10`;
- die unveränderten sechs Close-Nachrichtenschemas V3/V2.

Revision 17 bewahrt ausdrücklich:

- `V15-B1`: vollständiges Signal-Envelope,
  `SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV` und terminale Klassifikation jedes
  Listener-Ready-/Receive-Fehlers;
- `V14-H1`: endliche Close-FSM, absolute Deadlines, byteidentische Retries,
  exactly-once PREPARE-/COMMIT-Mutation und polling-basierte Approval-
  Konvergenz;
- `V13-B2`: ausschließlich Broker-CLOSED plus durable COMMIT ist clean;
- `V12-B1`/`V11-B1`: kein Pipe-Read/-Write/-Transfer und kein temporärer
  Liveness-Writerpfad;
- `V10-B1`: feste TID-/Files-Table-Topologie und vollständige post-Ready
  Task-/FD-/Writer-Referenzsperre;
- `V9-B1`: Self→Guardian→Broker-PIDFD→Liveness-Close bleibt die terminale
  Fallback-Reihenfolge;
- Single Owner, No Dual Write, Decimal/PEE Economics, Atomic V2/Loss Cluster,
  Execution Control, Authority/Recovery/Genesis und L0/L1 Kill/Restart;
- Windows und jede Plattform ohne separat reviewte äquivalente
  Kernelprimitive bleiben unsupported und fail closed;
- Implementierung, IU4 ENFORCED, Exchange und Live bleiben nicht freigegeben.

---

## 7. Formale Verifikation und Scope-Nachweis

Die vollständige Revision-17-Spezifikation besitzt nach Abschluss:

```text
SPEC_V17_PATH: docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPEC_V17_LINES: 3865
SPEC_V17_SHA256: ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64
```

Ausgeführt wurden ausschließlich read-only beziehungsweise dokumentbezogene
Prüfungen: `sha256sum`, `wc -l`, Versions-/State-/Finding-Referenzsuche,
Markdown-Tabellen-/Fence-/Inline-Code-Delimiterprüfung, Whitespace-Prüfung und
Git-Status-/HEAD-/Branch-Prüfung. Es wurden keine Runtime- oder Write-Tests
ausgeführt, weil dieser Schritt ausschließlich eine Paper-
Spezifikationsresolution ist.

```text
REVISION_16_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 1/1
V16_H1_RESOLVED_PENDING_REREVIEW: YES
V15_B1_CLOSED_STATUS_PRESERVED: YES
V15_H1_QUEUE_GAP_ADDRESSED_BY_V16_H1_RESOLUTION: YES
V14_H1_CLOSED_STATUS_PRESERVED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
RUNTIME_OR_STATE_MUTATION: NO
WORKSTATION_R3_MUTATION_OR_RETRY: NO
RESEARCH_MUTATION: NO
GIT_STAGE_COMMIT_FETCH_PUSH: NO
SPECIFICATION_REVISION_17_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der einzige beabsichtigte Dokument-Scope dieser Resolution besteht aus der
Revision-17-Spezifikation und diesem neuen Resolution-Record. Bestehende
untracked Artefakte bleiben unangetastet. Das Resolution-Protokoll enthält
keinen zirkulären Selbsthash.

---

## 8. Resolution-Urteil und nächster zulässiger Schritt

```text
RESOLUTION_RESULT: RESOLVED_PENDING_INDEPENDENT_REREVIEW
SPECIFICATION_REVISION: 17
SPECIFICATION_READY_FOR_INDEPENDENT_REREVIEW: YES
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-17-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen V17-Hash
`ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64`
prüfen. Erst er darf `V16-H1` schließen oder READY erklären. Bis dahin bleiben
Implementierung, Aktivierung, Exchange und Live gesperrt.
