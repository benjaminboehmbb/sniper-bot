# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-17 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-17 REREVIEW FINDING RESOLVED IN REVISION 18 — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand / HEAD / main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **main gegenüber origin/main:** `0 behind / 6 ahead`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V17-Hash:** `ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64`
- **Unabhängig geprüfte V17-Zeilen:** `3865`
- **Revision-17-Independent-Rereview-Record:** `b976df15ac62ef642ce5d1e6bca88bd8ad8c4ef3595c94aa931dd31ea8ce33d8`
- **Revision-17-Independent-Rereview-Zeilen:** `361`
- **Controlling Revision-16-Resolution:** `25a94fb235e172a9c298abd2d07f8d1f635260e01b1a6c99e070f0facf9ce041`
- **Controlling Revision-16-Resolution-Zeilen:** `321`
- **Resolution-Zielhash V18:** `6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663`
- **Resolution-Zielzeilen V18:** `4028`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet das einzige offene Finding `V17-H1` des unabhängigen
read-only Re-Reviews der Revision 17 einer normativen Korrektur in Revision 18
zu. Das Finding betrifft die nicht monotone Setup-Reihenfolge: Revision 17
erhob ihren letzten `SO_PASSRIGHTS=0`-/Queue-Snapshot, bevor `setsockopt` auf
allen relevanten TIDs irreversibel gesperrt und die finalen Rollenfilter
vollständig installiert waren.

Dieses Resolution-Protokoll zertifiziert die Korrektur nicht selbst. Der
Resolutionstatus lautet `RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein
neues unabhängiges read-only Re-Review des vollständigen V18-Hashes darf
`V17-H1` und damit `V16-H1`/`V15-H1` schließen oder READY erklären.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Vorhandene untracked Benutzerartefakte wurden nicht bereinigt,
überschrieben oder gestaged.

---

## 2. Ausgang des unabhängigen V17-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V17_SHA256: ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64
SPEC_V17_LINES: 3865
REVISION_16_RESOLUTION_SHA256: 25a94fb235e172a9c298abd2d07f8d1f635260e01b1a6c99e070f0facf9ce041
REVISION_17_REREVIEW_SHA256: b976df15ac62ef642ce5d1e6bca88bd8ad8c4ef3595c94aa931dd31ea8ce33d8
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V17-Re-Review | V18-Resolution |
|---|---|---|
| `V17-H1` | Set/Get `SO_PASSRIGHTS=0`, `scm_fds: 0` und leere Queue waren Snapshots vor der irreversiblen Filtergrenze. Zwischen Snapshot und Filter/OPEN konnte ein Empfänger-TID die Option reaktivieren und der Sender einen Rights-SKB einreihen. | Revision 18 fixiert zuerst alle Empfänger-TIDs/Files Tables, setzt Rights aus, installiert den Rights-Freeze per TSYNC auf alle TIDs, stapelt danach sämtliche finalen Rollenfilter, beweist hostweit exklusive Endpoint-Ownership und erhebt erst dann den autoritativen Options-/Queue-/OFD-/Lock-Snapshot. Senderfreigabe und OPEN folgen ausschließlich danach. |

Der unabhängige Review bestätigte den stationären Linux-Pfad ausdrücklich als
korrekt: Bei unverändertem `SO_PASSRIGHTS=0` liefert ein Rights-Send `EPERM`
vor `skb_queue_tail()` und der Fehlerpfad gibt das nicht eingereihte SKB samt
transienten file-Referenzen frei. Offen war allein die Setup-Transition.

---

## 3. Bestätigter Konflikt

Revision 17 ordnete:

1. Set/Get `SO_PASSRIGHTS=0` am final akzeptierten Empfangssocket;
2. `scm_fds: 0` und leere Queue prüfen;
3. danach Rollenfilter finalisieren;
4. danach `RUNTIME_SESSION_OPEN` schreiben.

Solange Schritt 3 nicht auf jedem TID vollendet war, blieb `setsockopt` eine
zulässige skalare Operation. Ein TID mit derselben Files Table konnte
`SO_PASSRIGHTS=1` setzen. Ein Sender konnte anschließend vor OPEN ein
`SCM_RIGHTS`-Paket einreihen. Der zuvor erhobene PASS-Snapshot wurde dadurch
stale; Revision 17 verlangte keinen zweiten Nachweis nach Filterinstallation.

Der Pfad benötigte weder einen Kernelfehler noch eine Seccomp-Dereferenzierung
des `msghdr`. Er verwendete ausschließlich die spezifizierte Reihenfolge. Ein
gestoppter Empfänger konnte den eingereihten SKB anschließend erneut ohne
zeitliche Obergrenze halten.

Revision 18 behandelt deshalb nicht nur den Optionswert, sondern die gesamte
Transition von veränderlichem Bootstrapzustand zu irreversibler Runtime-
Topologie als eine endliche, fail-closed Zustandsmaschine.

---

## 4. Resolution von V17-H1

### 4.1 Phase 1 — Empfänger-Tasktopologie einfrieren

`TerminalRuntimeReceiverTaskTopologyV1` bindet für Guardian, Broker, Shim und
Worker vor der Endpunktkonfiguration:

- TGID und vollständige sortierte TID-/Startzeitmenge;
- Files-Table-Identität;
- alle benötigten bereits existierenden TIDs;
- eine per TSYNC installierte `SECCOMP_RET_KILL_PROCESS`-Sperre jeder weiteren
  Task- oder Files-Table-Erzeugung.

Diese erste Phase sperrt bewusst noch nicht die für `listen`/`accept4`
benötigte FD-Erzeugung. Nachträglicher TID, TSYNC-Fehler oder abweichende
Files Table beendet den Startup (Spezifikation Zeilen 1479–1487).

### 4.2 Phase 2 — Endpunkte vollständig binden

Alle sechs final-role Verbindungen werden aufgebaut und gegenseitig per
`SO_PEERCRED` plus PID-Startzeit attestiert. Listener-, Bootstrap- und
abgelehnte Connect-FDs werden unmittelbar danach und vor Rights-Freeze
geschlossen. Exakt zwölf finale Sender-/Empfänger-FDs dürfen verbleiben
(Zeilen 1459–1477).

Für jeden Empfängerprozess werden **alle** ihm gehörenden akzeptierten
Empfangsendpunkte hergestellt, bevor der Prozess seinen Freeze-Filter
installiert. Jeder finale Empfangsendpunkt erhält
`setsockopt(SOL_SOCKET,SO_PASSRIGHTS,0)` plus unmittelbares
`getsockopt==0`. Listenerzustand und Vererbung bleiben nicht autoritativ
(Zeilen 1489–1500).

### 4.3 Phase 3 — Rights-Zustand irreversibel machen

`TerminalRuntimeChannelRightsFreezeFilterV1` wird für jeden der vier
Empfänger-TGIDs mit `SECCOMP_FILTER_FLAG_TSYNC` auf die vollständige zuvor
fixierte TID-Menge angewandt. Der Filter:

- beendet **jeden** `setsockopt` unabhängig von FD, Level, Optname oder
  Pointer mit `SECCOMP_RET_KILL_PROCESS`;
- bleibt irreversibel gestapelt und kann nicht gelockert oder entfernt werden;
- erlaubt `getsockopt` nur für feste Empfangs-FDs, `SOL_SOCKET`,
  `SO_PASSRIGHTS` und gebundene Ergebnisbuffer;
- bindet TSYNC-Return, TID-Menge, Filterzahl und BPF-Hash.

Die Sperre gilt damit bereits vor finalem Rollenfilter und Ready, nicht erst
post-OPEN (Zeilen 1502–1510 und 1557–1562).

### 4.4 Phase 4 — sämtliche Rollen- und FD-Transfergrenzen schließen

Nach erfolgreichem Rights-Freeze auf allen vier TGIDs werden sämtliche finalen
Guardian-/Broker-/Shim-/Worker-Rollenfilter per TSYNC gestapelt. Sie sperren
vor dem autoritativen Snapshot:

- neue FDs und Duplikation;
- `accept`/`connect` und externe Socketziele;
- FD-Transfer und nicht exakt auf die sechs festen Endpunkte gerichtete
  `sendmsg`-Aufrufe;
- jede neue Task-/Files-Table- oder Endpoint-Topologie.

Ein gebundener externer Observer inventarisiert danach aus dem Host-PID-
Namespace sämtliche Prozesse/TIDs innerhalb und außerhalb der Session-Cgroup,
alle `/proc/<pid>/fd`-Mengen und die Kernel-Socketreferenzansicht. Für jeden
Socket-Inode dürfen exakt die erwarteten zwei Endpunktrollen existieren.
Unzureichende Sichtbarkeit, Bootstrap-Kopie oder fremder Halter verhindert
PASS (Zeilen 1511–1525).

### 4.5 Phase 5 — autoritativer post-Filter-Snapshot

Erst hinter beiden irreversiblen Filterlagen und dem hostweiten Ownership-
Nachweis werden auf allen sechs Kanälen erneut gebunden:

- `getsockopt(SO_PASSRIGHTS)==0`;
- `/proc/<receiver>/fdinfo/<fd>` mit `scm_fds: 0`;
- leere Receive Queue;
- unveränderte FD-/FDINFO-/OFD-/Lock-Inventur;
- TGID/TID-/Files-Table-Identität;
- Rights-Freeze- und finale Rollenfilterhashes;
- systemweite Endpoint-Ownership-Inventur, Endpunkt-Inode, Messzeit und
  Session-Nonce.

Kein früherer Snapshot darf diese Evidenz ersetzen. Zwischen diesem Snapshot
und OPEN ist keine weitere Filter-, Task-, Files-Table- oder FD-
Topologieänderung zulässig (Zeilen 1527–1553).

### 4.6 Senderfreigabe, OPEN und totaler Fehlerpfad

Sender erhalten keine Runtime-Sendefreigabe vor globalem PASS aller sechs
Kanäle. Erst danach darf `RUNTIME_SESSION_OPEN` geschrieben werden.

Jeder abweichende Options-, Filter-, Ownership-, Queue-, FD-, OFD- oder
Lock-Nachweis führt zu:

1. keiner Senderfreigabe und keinem OPEN;
2. Termination aller vier finalen Rollenprozesse;
3. Schließen aller Launcher-/Listenerkopien;
4. externer Bestätigung der Socket-/Queue-Zerstörung und vollständigen
   file-/OFD-/Lock-Freigabe;
5. Verbot eines Retries mit denselben Prozessen, Endpunkten oder derselben
   Session-Nonce.

Weil finale Rollenfilter `close` einschränken dürfen, hängt dieser Cleanup
nicht vom Rollenfortschritt ab; Process Exit entzieht die Endpunkte
kernel-seitig. Nur ein vollständig neuer Startup-Versuch ist zulässig
(Zeilen 1537–1553).

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Setup-FSM und Race-Abdeckung

| Phase | Irreversible Grenze | Autoritativer Nachweis | Fehlerfolge |
|---|---|---|---|
| `TASKS_FROZEN` | keine neuen TIDs/Files Tables | TGID/TID-/Startzeit-/KCMP-Inventur | alle Rollen terminieren |
| `ENDPOINTS_BOUND` | Listener-/Bootstrap-Kopien geschlossen | exakt zwölf finale Endpunkt-FDs | Startup abbrechen |
| `RIGHTS_DISABLED` | finaler Empfängerwert zunächst 0 | erstes Set/Get, noch kein PASS-Snapshot | kein Senderrelease |
| `RIGHTS_FROZEN` | TSYNC-Filter killt jeden `setsockopt` | alle Empfänger-TIDs, BPF-Hash/Filterzahl | TGID-Kill/Startup-Abbruch |
| `ROLES_FROZEN` | finale Rollenfilter sperren FD-/Transferwege | alle Rollen-TIDs und Endpoint-Allowlist | Rollen terminieren |
| `OWNERSHIP_PROVEN` | keine fremde Endpoint-Referenz | hostweite Socket-Inode-Inventur | kein PASS bei Sichtlücke |
| `SNAPSHOT_PASSED` | vorherige Grenzen unverändert | post-filter Option/Queue/OFD/Lock | Senderrelease erlaubt |
| `OPEN` | durable Sessionidentität | Snapshot-/Filter-/Nonce-Bindung | Runtime darf beginnen |

Capability-, Startup-, Fault- und Completion-Gates injizieren auf jedem der
sechs Kanäle:

- `SO_PASSRIGHTS=1` und Rights-Send vor, während und nach jedem Rights-Freeze-
  TSYNC;
- dieselben Versuche vor, während und nach finaler Rollenfilterinstallation
  sowie nach letztem Snapshot vor OPEN;
- partiellen oder fehlgeschlagenen TSYNC und neu auftauchende TIDs;
- versteckte Endpoint-Duplikation/-Übertragung in gleiche, fremde Session-
  oder externe Files Tables;
- einen bestandenen pre-Filter-Snapshot mit anschließend eingereihtem
  Rights-Paket;
- Queue-Residuum, Empfänger-Stop/-Crash und Sender-Close/-Crash;
- vollständige Zerstörung/Freigabe und Verbot des Same-Session-Retry;
- den getrennten NULL/0-Controlbuffer-Autoclose als Defense in Depth.

PASS verlangt entweder `SECCOMP_RET_KILL_PROCESS` vor der Mutation oder einen
endgültigen post-role-filter Snapshot ohne Queue-/Referenzrest. Ein bloßer
pre-Filter-Snapshot, eine textuelle Sendesperre oder allein post-Ready
ausgeführte Rights-Trials sind kein PASS (Spezifikation Zeilen 1805–1815,
1874–1899, 1938–1962, 3749–3773 und 3921–3975).

---

## 6. Versionierung und Preservation

Die Revision-18-Vertragsfamilie lautet exakt:

- `IU4RuntimeControlProfileV12`;
- Runtime Session Envelope V13;
- `TerminalLeaseControlWordV3`;
- `TerminalTradingSignalEnvelopeV1`;
- `TerminalKernelTripRequestV2`;
- `TerminalSelfKillEntryV4`;
- `RuntimeSessionCloseProtocolV6`;
- `TerminalRuntimeChannelProvisioningV3`;
- `TerminalTradingTaskTopologyV2`;
- `TerminalRuntimeReceiverTaskTopologyV1`;
- `TerminalRuntimeChannelRightsFreezeFilterV1`;
- `TerminalParentGuardianV11`;
- `TerminalNativeTripBrokerV8`;
- `TerminalKernelLeaseShimV9`;
- `TerminalPersistenceWorkerV5`;
- `TerminalLeaseCapabilityProfileV11`;
- die unveränderten sechs Close-Nachrichtenschemas V3/V2.

Revision 18 bewahrt ausdrücklich:

- den korrekten stationären V16-H1-`SO_PASSRIGHTS=0`-/`EPERM`-Pfad;
- `V15-B1`: Signal-Envelope, WAIT_KILLABLE_RECV und terminale Klassifikation
  jedes Listener-Ready-/Receive-Fehlers;
- `V14-H1`: endliche Close-FSM, absolute Deadlines, byteidentische Retries und
  exactly-once PREPARE-/COMMIT-Mutation;
- `V13-B2`: ausschließlich Broker-CLOSED plus durable COMMIT ist clean;
- `V12-B1`/`V11-B1`: kein Pipe-Read/-Write/-Transfer und kein temporärer
  Liveness-Writerpfad;
- `V10-B1`: feste TID-/Files-Table-Topologie und post-Ready Task-/FD-/Writer-
  Referenzsperre;
- `V9-B1`: Self→Guardian→Broker-PIDFD→Liveness-Close-Fallback;
- Single Owner, No Dual Write, Decimal/PEE Economics, Atomic V2/Loss Cluster,
  Execution Control, Authority/Recovery/Genesis und L0/L1 Kill/Restart;
- Windows und jede Plattform ohne separat reviewte äquivalente
  Kernelprimitive bleiben unsupported und fail closed;
- Implementierung, IU4 ENFORCED, Exchange und Live bleiben nicht freigegeben.

---

## 7. Formale Verifikation und Scope-Nachweis

Die vollständige Revision-18-Spezifikation besitzt nach Abschluss:

```text
SPEC_V18_PATH: docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPEC_V18_LINES: 4028
SPEC_V18_SHA256: 6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663
```

Ausgeführt wurden ausschließlich read-only beziehungsweise dokumentbezogene
Prüfungen: `sha256sum`, `wc -l`, Versions-/State-/Finding-Referenzsuche,
Markdown-Tabellen-/Fence-/Inline-Code-Delimiterprüfung, Whitespace-Prüfung und
Git-Status-/HEAD-/Branch-Prüfung. Es wurden keine Runtime- oder Write-Tests
ausgeführt, weil dieser Schritt ausschließlich eine Paper-
Spezifikationsresolution ist.

```text
REVISION_17_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 1/1
V17_H1_RESOLVED_PENDING_REREVIEW: YES
V16_H1_RESOLVED_PENDING_REREVIEW: YES
V15_H1_RESOLVED_PENDING_REREVIEW: YES
V15_B1_CLOSED_STATUS_PRESERVED: YES
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
SPECIFICATION_REVISION_18_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der einzige beabsichtigte Dokument-Scope dieser Resolution besteht aus der
Revision-18-Spezifikation und diesem neuen Resolution-Record. Bestehende
untracked Artefakte bleiben unangetastet. Das Resolution-Protokoll enthält
keinen zirkulären Selbsthash.

---

## 8. Resolution-Urteil und nächster zulässiger Schritt

```text
RESOLUTION_RESULT: RESOLVED_PENDING_INDEPENDENT_REREVIEW
SPECIFICATION_REVISION: 18
SPECIFICATION_READY_FOR_INDEPENDENT_REREVIEW: YES
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-18-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen V18-Hash
`6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663`
prüfen. Erst er darf `V17-H1`, `V16-H1` und `V15-H1` schließen oder READY
erklären. Bis dahin bleiben Implementierung, Aktivierung, Exchange und Live
gesperrt.
