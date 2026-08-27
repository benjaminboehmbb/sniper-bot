# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-15 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-15 REREVIEW FINDINGS RESOLVED IN REVISION 16 — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V15-Hash:** `34637e2e51b63f8d386d0eb04acf74bd34a1e805eaea317e156cd87f5eece25a`
- **Unabhängig geprüfte V15-Zeilen:** `3558`
- **Revision-15-Independent-Rereview-Record:** `8276a4eba8f89b7f929ccd29211d631b57a46862684542a8db5fe7baef65c477`
- **Revision-15-Independent-Rereview-Zeilen:** `282`
- **Controlling Revision-14-Resolution:** `2fb968c6c4f832f5d1b37a0a9b56b7988b5c158b45c519583a167df92bebd67e`
- **Controlling Revision-14-Resolution-Zeilen:** `390`
- **Controlling Independent V14 Review:** `ce5d0f80105ba5a25f7dd33177299d80f1d494143a67ebe7d433776d05f803d3`
- **Controlling Independent V14 Review-Zeilen:** `299`
- **Resolution-Zielhash V16:** `093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f`
- **Resolution-Zielzeilen V16:** `3760`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die offenen Findings `V15-B1` und `V15-H1` des
unabhängigen read-only Re-Reviews der Revision 15 konkreten normativen
Korrekturen in Revision 16 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V16-Hashes darf die Findings schließen oder READY
erklären.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Untracked Benutzerartefakte wurden nicht bereinigt, überschrieben
oder gestaged.

---

## 2. Ausgang des unabhängigen V15-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V15_SHA256: 34637e2e51b63f8d386d0eb04acf74bd34a1e805eaea317e156cd87f5eece25a
SPEC_V15_LINES: 3558
REVISION_14_RESOLUTION_SHA256: 2fb968c6c4f832f5d1b37a0a9b56b7988b5c158b45c519583a167df92bebd67e
REVISION_14_REREVIEW_SHA256: ce5d0f80105ba5a25f7dd33177299d80f1d494143a67ebe7d433776d05f803d3
REVISION_15_REREVIEW_SHA256: 8276a4eba8f89b7f929ccd29211d631b57a46862684542a8db5fe7baef65c477
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V15-Re-Review | V16-Resolution |
|---|---|---|
| V15-B1 | `SECCOMP_RET_USER_NOTIF` kann vor Broker-Receive signalbedingt abbrechen; der zurückkehrende Request-TID kann vor dem Fallback stoppen, während RUNNING/Renewals fortbestehen | vollständiges vor-TID-Signal-Envelope, NEW_LISTENER plus WAIT_KILLABLE_RECV, gesperrte Signaländerungen und terminale Klassifikation jedes Listener-Ready-/Receive-Fehlers |
| V15-H1 | `SCM_RIGHTS` installiert FDs vor Userspace-Ablehnung; ein totaler Cleanup-Vertrag fehlt und kollidiert mit den Rollenfiltern | final-role `connect`/`accept` mit `SO_PEERCRED`, `SO_PASSCRED=0`, absenter Receive-Controlbuffer, kernelseitiger Rights-Autoclose und FD-/Lock-Inventurnachweis |

---

## 3. Resolution von V15-B1

### Signalabbruch vor Broker-Receive

**Bestätigter Konflikt:** Revision 15 behandelte die Kernel-Erzeugung einer
Seccomp-User-Notification als irreversiblen lokalen Request-Zeitpunkt. Linux
blockiert den Ziel-TID dabei jedoch signal-interruptible. Vor erfolgreichem
Broker-Receive kann ein Signal die Notification abbrechen; ohne vollständigen
Signalvertrag konnte der Syscall zurückkehren und derselbe Request-TID vor dem
ersten PIDFD-Fallback angehalten werden. `WAIT_KILLABLE_RECV` allein schützt
nur die Phase nach erfolgreichem Supervisor-Receive und hätte dieses Fenster
nicht geschlossen.

**Resolution in V16:**

1. `TerminalTradingSignalEnvelopeV1` wird vom noch einzigen Trading-Leader vor
   Filterinstallation und vor jeder weiteren TID-Erzeugung hergestellt. Alle
   blockierbaren Signale werden maskiert, userdefinierte Handler und
   `SA_RESTART`-Dispositionen entfernt; Signalset, Dispositionen und die
   einelementige TID-Menge werden attestiert (Spezifikation Zeilen 1017–1024).
2. Jede spätere Änderung durch `rt_sigaction`, `rt_sigprocmask`, `sigaltstack`,
   `signalfd*` oder einen nicht exakt gebundenen Signal-Erzeugungssyscall endet
   unter dem gestapelten default-deny-Filter mit
   `SECCOMP_RET_KILL_PROCESS`. Alle späteren TIDs erben die Maske. Kein
   blockierbares Signal kann dadurch post-Ready einen Handler-Return erzeugen
   (Zeilen 1026–1038 und 2670–2694).
3. `TerminalKernelTripRequestV2` verwendet die kombinierte Installation
   `SECCOMP_FILTER_FLAG_NEW_LISTENER|SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV`.
   Fehlender Kernel-Support oder eine abweichende Flag-Akzeptanz verhindert
   OPEN. Vor Receive schützt die geerbte Signalmaske; nach Receive stellt
   WAIT_KILLABLE_RECV nichtfatale Signale zurück (Zeilen 1040–1064).
4. `SIGKILL` bleibt nichtmaskierbar und beendet den Trading-TGID fail-safe.
   `SIGSTOP` stoppt den gesamten TGID einschließlich Shim; ohne verarbeitete
   Approval läuft die bereits armed Kernel-Lease aus. `SIGCONT` ändert die
   blockierte Maske nicht. Ein synchron-fataler Kernel-Fault darf nur
   terminieren, nicht in einen Handler zum Trip-Entry zurückkehren (Zeilen
   1031–1038).
5. Sobald der Listener readable/HUP/ERR meldet, ist jedes
   `SECCOMP_IOCTL_NOTIF_RECV`-Ergebnis total klassifiziert: ein Erfolg wird
   normal validiert; `ENOENT`, `EINTR`, `EAGAIN`, ABI-/Short- oder unbekannte
   Fehler werden konservativ als Terminal Trip behandelt. Kein solcher Fehler
   darf als verschwundenes Event übersprungen werden (Zeilen 1065–1077).
6. Ein signalbedingter Return oder eine `SA_RESTART`-Duplikatnotification ist
   innerhalb des Capability-Envelopes nicht zulässig. Wird ein solcher Pfad in
   der Kernel-/Startup-Probe dennoch beobachtet, verhindert er OPEN;
   post-OPEN ist er Capability-Verlust und terminal (Zeilen 1079–1087).
7. `TerminalLeaseCapabilityProfileV9`, die 10.000-Trial-Zertifizierung, die
   32-Phasen-Startup-Probes, Fault Injection und Completion-Gates injizieren
   jedes blockierbare Signal vor und nach Receive, negative Handler-/Unmask-
   Versuche, `SIGKILL`, `SIGSTOP`, alle Listener-Receive-Fehler und den Halt
   unmittelbar an jeder Grenze. Kein Einzel- oder Messfehler ist PASS (Zeilen
   1553–1767, 3440–3457 und 3699–3703).

Damit hängt das pre-Receive-Fenster nicht mehr vom Fortschritt desselben
Request-TID ab: blockierbare Signalhandler können nicht laufen; unmaskierbare
Signale terminieren oder stoppen den gesamten TGID und aktivieren den bereits
bestehenden Lease-Fail-stop. Nach Listener-Sichtbarkeit klassifiziert der
externe Broker auch einen verlorenen/abgebrochenen Receive terminal.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution von V15-H1

### Ancillary-FD-Mutation vor Userspace-Ablehnung

**Bestätigter Konflikt:** Revision 15 verwendete `SO_PASSCRED` und einen
Ancillary-Controlbuffer, behauptete zugleich aber `SCM_RIGHTS` default-deny.
Klassisches Seccomp kann den referenzierten `msghdr` nicht dereferenzieren.
Ein in den Controlbuffer passender Rights-FD wird deshalb bereits in die
Empfänger-FD-Tabelle installiert, bevor Userspace den CMSG-Inhalt ablehnt.
Guardian, Broker und andere Rollen durften anschließend keinen allgemeinen
`close` ausführen; ein totaler Dispose-Vertrag fehlte.

**Resolution in V16:**

1. `TerminalRuntimeChannelProvisioningV1` ersetzt alle vor Fork erzeugten
   Socketpairs. Erst nachdem die finalen Guardian-/Broker-/Shim-/Worker-
   Prozesse mit gebundener PID/Startzeit existieren, bindet der finale
   Empfänger einen session-/rollen-/richtungsgebundenen abstrakten AF_UNIX-
   Listener; der finale Sender verbindet und der finale Empfänger akzeptiert
   exakt eine nonblocking `SOCK_SEQPACKET`-Verbindung (Zeilen 1406–1417).
2. Beide Endpunkte prüfen vor Ready `SO_PEERCRED` und die separate PID-
   Startzeit gegen die erwartete finale Rolle. Fremde oder mehrere Connects
   blockieren. Nach Attestation werden Listener-, Bootstrap- und abgelehnte
   FDs geschlossen; Reconnect und Runtime-`accept`/`connect` bleiben verboten
   (Zeilen 1411–1425).
3. `SO_PASSCRED` muss überall exakt `0` sein. Per-message
   `SCM_CREDENTIALS` entfällt; die feste Peeridentität stammt aus der
   nach finalem Rollenstart aufgebauten Verbindung und ist Bestandteil von
   OPEN (Zeilen 988–993, 1418–1425 und 2948–2953).
4. Jeder native Empfänger ruft `recvmsg` ausschließlich mit
   `msg_control=NULL` und `msg_controllen=0` auf. Nach dem bindenden
   Linux-`unix(7)`-Vertrag schließt der Kernel wegen des fehlenden Buffers nicht
   zustellbare `SCM_RIGHTS`-FDs automatisch. Kein userspace-sichtbarer neuer FD
   und keine Empfänger-Open-File-Description darf den Syscall-Return überleben
   (Zeilen 1459–1469).
5. `MSG_CTRUNC` oder irgendein Ancillary-Inhalt ist nach abgeschlossener
   Kernel-Disposition ein terminaler Protokollfehler vor fachlicher Mutation,
   kein Userspace-Cleanup-Auftrag. Die Rollenfilter müssen deshalb keinen
   allgemeinen `close` erlauben (Zeilen 1463–1481).
6. Capability-, Startup-, Fault- und Completion-Gates injizieren auf jedem der
   sechs Kanäle fremde Connects, falsche `SO_PEERCRED`-/Startzeiten,
   `SO_PASSCRED=1`, nichtleere Controlbuffer, jede CMSG-Reihenfolge und ein bis
   `SCM_MAX_FD` Rights-FDs. Der externe Observer verlangt identische FD-/
   FDINFO-Inventur vor/nach `recvmsg` und keine fortbestehende Lock- oder
   Open-File-Description-Referenz nach Schließen der Senderreferenz (Zeilen
   1718–1725, 3511–3518 und 3675–3708).

Damit wird die bereits kernelwirksame Rights-Installation nicht nachträglich
als Seccomp-Verhinderung umgedeutet. Der Empfänger stellt keinen Controlbuffer
bereit; Linux verwirft und schließt die nicht zustellbaren Rights innerhalb
des Receive-Pfads. Userspace sieht nur `MSG_CTRUNC`, eskaliert terminal und
benötigt keine mit den Rollenfiltern kollidierende FD-Dispose-Schleife.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Konsistente Autoritäts- und Fehlerwirkung

### 5.1 Signal-/Trip-Matrix

| Grenze | Kernel-/Prozesswirkung | Broker-/Lease-Wirkung | Zulässiges Ergebnis |
|---|---|---|---|
| blockierbares Signal vor Broker-Receive | bleibt unter geerbter vollständiger Maske pending; kein Handler-Return | Notification bleibt empfangbar | Broker-CAS nach TERMINATING |
| blockierbares Signal nach Broker-Receive | WAIT_KILLABLE_RECV stellt nichtfatal zurück | Broker validiert/CAS/Kill läuft weiter | Broker-CAS nach TERMINATING |
| `SIGKILL` | TGID terminiert | keine weitere Approval | fail-safe |
| `SIGSTOP` | ganzer TGID inklusive Shim stoppt | armed Lease läuft ohne Approval aus | pending `SIGKILL`, fail-safe |
| Listener ready, Receive `ENOENT|EINTR|EAGAIN|unknown` | Request-TID-Fortschritt wird nicht benötigt | Fehler selbst ist Terminal Trip | TERMINATING oder CLOSED_FAILSTOP |
| verbotene Signalzustandsänderung | `SECCOMP_RET_KILL_PROCESS` | Approval endet, Lease bleibt armed | fail-safe |

### 5.2 Kanal-/Ancillary-Matrix

| Grenze | Pflichtvertrag | Fehlerfolge |
|---|---|---|
| Provisioning | final-role connect/accept, exakt ein Peer, `SO_PEERCRED` plus PID-Startzeit | kein Ready/OPEN |
| Runtime Endpoint | feste FD/Inode/Richtung, `SO_PASSCRED=0`, kein Reconnect | terminaler Kanalfehler |
| Receive | `msg_control=NULL`, `msg_controllen=0`, exakt gebundener Payloadbuffer | Abweichung terminal |
| `SCM_RIGHTS`/fremdes CMSG | Kernel-Autoclose, `MSG_CTRUNC`, keine fachliche Mutation | terminaler Protokollfehler |
| Post-Receive-Inventur | keine neue FD-/FDINFO-/Open-File-Description-/Lock-Referenz | kein PASS bei Abweichung |

### 5.3 Rollenautorität

| Rolle | Signal-/Trip-Autorität | Kanalautorität | Unzulässige Abkürzung |
|---|---|---|---|
| Trading/Python | geerbte blockierte Maske, nur drei gebundene PIDFD-Kill-Stufen | keine Runtime-Kanäle | kein Handler/Unmask/Signal-Syscall, kein Listener |
| Broker V6 | alleiniger Listener und Control-Word-RW-Writer | zwei Receives, vier Sends, feste SO_PEERCRED-Peers | kein CONTINUE/ADDFD, kein Journal, kein Controlbuffer |
| Guardian V9 | Parent-/Child-Kill und Renewal | GB_REQUEST send, BG_CLOSE_APPROVAL receive | kein Control-Word-Write, kein allgemeiner FD-Cleanup |
| Shim V7 | armed Kernel-Lease, RO-Control-Word | zwei Approval-Receives | kein Signalzustandswechsel, kein allgemeiner FD-Cleanup |
| Worker V3 | kein Trip-Write; Journal/Lifecycle exklusiv | BW_REQUEST receive, WB_ACK send | kein Control-Word-Write, kein allgemeiner FD-Cleanup |

---

## 6. Versionierung und Preservation

Die Revision-16-Vertragsfamilie lautet exakt:

- `IU4RuntimeControlProfileV10`;
- Runtime Session Envelope V11;
- `TerminalLeaseControlWordV3`;
- `TerminalTradingSignalEnvelopeV1`;
- `TerminalKernelTripRequestV2`;
- `TerminalSelfKillEntryV4`;
- `RuntimeSessionCloseProtocolV4`;
- `TerminalRuntimeChannelProvisioningV1`;
- `TerminalParentGuardianV9`;
- `TerminalNativeTripBrokerV6`;
- `TerminalKernelLeaseShimV7`;
- `TerminalPersistenceWorkerV3`;
- `TerminalLeaseCapabilityProfileV9`;
- die unveränderten sechs Close-Nachrichtenschemas V3/V2.

Revision 16 bewahrt ausdrücklich:

- V14-H1: endliche Close-FSM, absolute Deadlines, byteidentische Retries,
  exactly-once PREPARE-/COMMIT-Mutation und polling-basierte Approval-
  Konvergenz;
- V13-B2: PREPARE ist nicht clean; ausschließlich Broker-CLOSED plus durable
  COMMIT ist beim Startup clean;
- V12-B1/V11-B1: kein Pipe-Read/-Write/-Datentransfer und kein Userbuffer-,
  Pipe-Page-, Reclaim- oder temporärer Writerpfad im Terminal-Sicherheitsweg;
- V11-M1: I2, Dateiscope, Tests und Completion-Gates referenzieren dieselbe
  aktuelle V16-Vertragsfamilie;
- V10-B1: feste TID-/Files-Table-Topologie, spätere TSYNC-KILL_PROCESS-Sperre
  und vollständige Post-Ready-Task-/Writer-Referenzsperre;
- V9-B1: Self-PIDFD-`SIGKILL` bleibt der erste Kernelaufruf; jeder zulässige
  zurückkehrende Kernel-/Listenerfehler führt ohne Retry zur nächsten
  terminalen Stufe;
- V9-M1: exakte Memfd-Erzeugung, initialer Seal-State und beide
  `F_ADD_SEALS`-Transitionen;
- V8-H1: separater Broker als alleiniger Control-Word-Writer, Trading nur RO,
  kein Trading-Worker-FD und receiverseitige Worker-Prüfung;
- Single Owner, No Dual Write, Decimal/PEE Economics, Atomic V2/Loss Cluster,
  Execution Control, Authority/Recovery/Genesis und L0/L1 Kill/Restart;
- Whole-child-Stop bleibt fail-safe, weil der Shim mitstoppt und die bereits
  armed Kernel-Lease ohne Userspace-Fortschritt ausläuft;
- Windows und jede Plattform ohne separat reviewte äquivalente
  Kernelprimitive bleiben unsupported und fail closed;
- Implementierung, IU4 ENFORCED, Live-L1, Exchange und Live bleiben nicht
  freigegeben.

---

## 7. Formale Verifikation und Scope-Nachweis

Die vollständige Revision-16-Spezifikation besitzt nach Abschluss:

```text
SPEC_V16_PATH: docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPEC_V16_LINES: 3760
SPEC_V16_SHA256: 093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f
```

Ausgeführt wurden ausschließlich read-only beziehungsweise dokumentbezogene
Prüfungen: `sha256sum`, `wc -l`, Versions-/State-/Finding-Referenzsuche,
Markdown-Tabellen-Spaltenprüfung, Inline-Code-Delimiterprüfung,
Whitespace-Prüfung und Git-Status-/HEAD-/Branch-Prüfung. Es wurden keine
Runtime- oder Write-Tests ausgeführt, weil dieser Schritt ausschließlich eine
Paper-Spezifikationsresolution ist.

```text
REVISION_15_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 1/1
V15_B1_RESOLVED_PENDING_REREVIEW: YES
V15_H1_RESOLVED_PENDING_REREVIEW: YES
V14_H1_CLOSED_STATUS_PRESERVED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES
V9_B1_RETURN_PATH_PRESERVED: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
RUNTIME_OR_STATE_MUTATION: NO
WORKSTATION_R3_MUTATION_OR_RETRY: NO
RESEARCH_MUTATION: NO
GIT_STAGE_COMMIT_PUSH: NO
SPECIFICATION_REVISION_16_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

---

## 8. Resolution-Urteil und nächster zulässiger Schritt

```text
RESOLUTION_RESULT: RESOLVED_PENDING_INDEPENDENT_REREVIEW
SPECIFICATION_REVISION: 16
SPECIFICATION_READY_FOR_INDEPENDENT_REREVIEW: YES
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-16-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen V16-Hash
`093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f`
prüfen. Erst er darf V15-B1 und V15-H1 schließen oder READY erklären. Bis
dahin bleiben Implementierung, Aktivierung, Exchange und Live gesperrt.
