# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-18 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-18 REREVIEW FINDING RESOLVED IN REVISION 19 — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand / HEAD / main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **main gegenüber origin/main:** `0 behind / 6 ahead`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V18-Hash:** `6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663`
- **Unabhängig geprüfte V18-Zeilen:** `4028`
- **Revision-18-Independent-Rereview-Record:** `8efb96b2e48c7ab3090e9aba7b2e71bcb421fdeabb269fc937970344e29fa427`
- **Revision-18-Independent-Rereview-Zeilen:** `482`
- **Controlling Revision-17-Resolution:** `5b56d248174ae96c8dbdcdaafce611acb2d18a5e7ae24a49a1fe8ffb0953fce2`
- **Controlling Revision-17-Resolution-Zeilen:** `363`
- **Resolution-Zielhash V19:** `191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b`
- **Resolution-Zielzeilen V19:** `4161`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet das einzige offene Finding `V18-H1` des unabhängigen
read-only Re-Reviews der Revision 18 einer normativen Korrektur in Revision 19
zu. Das Finding betrifft keine Fehlfunktion des Linux-`SO_PASSRIGHTS=0`-
Prequeue-Guards und keine unvollständige TSYNC-Abdeckung der vier Rollen-TGIDs.
Offen war eine globale Setup-Lücke: Ein fremder Prozess konnte vor der lokalen
Filtergrenze einen Endpoint erwerben, einen `setsockopt(SO_PASSRIGHTS=1)`-
Syscall nach FD-Auflösung anhalten, den sichtbaren FD schließen und den
Optionssyscall erst nach dem autoritativen Snapshot fortsetzen. Weder
`/proc/<pid>/fd` noch eine unoperationalisierte „Kernel-
Socketreferenzansicht“ erfasste die nur vom laufenden Syscall gehaltene
`struct file` atomar.

Revision 19 ersetzt diese Beobachtungsannahme durch eine konkrete monotone
Kernelgrenze. Sie verwendet einen global angehängten BPF-LSM-Guard mit
socketlokalem `BPF_MAP_TYPE_SK_STORAGE`, einem vor Userspace-FD-Sichtbarkeit
erzeugten Session-Tag, globalem `socket_setsockopt`-Fence, globalem
`file_receive`-Fence und einem bis nach durablem Session OPEN geschlossenen
`socket_sendmsg`-Gate.

Dieses Resolution-Protokoll zertifiziert die Korrektur nicht selbst. Sein
Status lautet `RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues
unabhängiges read-only Re-Review des vollständigen V19-Hashes darf `V18-H1`
und damit die abhängigen Findings `V17-H1`, `V16-H1` und `V15-H1` schließen
oder READY erklären.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Vorhandene untracked Benutzerartefakte wurden nicht bereinigt,
überschrieben oder gestaged.

---

## 2. Ausgang des unabhängigen V18-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V18_SHA256: 6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663
SPEC_V18_LINES: 4028
REVISION_17_RESOLUTION_SHA256: 5b56d248174ae96c8dbdcdaafce611acb2d18a5e7ae24a49a1fe8ffb0953fce2
REVISION_18_REREVIEW_SHA256: 8efb96b2e48c7ab3090e9aba7b2e71bcb421fdeabb269fc937970344e29fa427
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V18-Re-Review | V19-Resolution |
|---|---|---|
| `V18-H1` | Der prozesslokale Set/Get→Rights-Freeze-TSYNC→Rollenfilter→Snapshot-Pfad war korrekt. Ein fremder, nach FD-Lookup blockierter `setsockopt`-Caller konnte seine sichtbare FD-Kopie schließen, den hostweiten Snapshot passieren und `SO_PASSRIGHTS=1` erst danach mutieren. | Revision 19 taggt den Socket vor jeder Userspace-FD-Sichtbarkeit. `security_socket_setsockopt()` erreicht den globalen BPF-LSM-Hook nach FD-Auflösung, aber vor Optionskopie/-mutation. Genau ein gebundener Bootstrap-TID versiegelt den Socket atomar `INIT→SEALED`; jeder andere oder spätere Caller erhält global `-EPERM`. `file_receive` verhindert externe Akquisition, und `socket_sendmsg` verhindert bis nach durablem OPEN jede Bootstrap-Übertragung/Queueing-Möglichkeit. |

Der unabhängige Review bestätigte den stationären Linux-Pfad: Bei
unverändertem `SO_PASSRIGHTS=0` liefert ein AF_UNIX-Rights-Send `EPERM` vor dem
Einreihen in die Receive Queue; der nicht eingereihte SKB gibt transiente
file-/OFD-/Lock-Referenzen frei. Revision 19 bewahrt diesen Pfad und macht die
Voraussetzung `SO_PASSRIGHTS==0` global monoton.

---

## 3. Bestätigter Konflikt und erforderliche Linearisierung

Der V18-Ablauf erlaubte dieses Interleaving:

1. Vor den finalen Rollenfiltern gelangt eine Endpoint-Kopie in einen fremden
   Prozess.
2. Ein fremder TID beginnt
   `setsockopt(receiver_fd,SOL_SOCKET,SO_PASSRIGHTS,1,...)`; der Kernel löst
   den FD auf und hält `struct file`.
3. Der TID blockiert vor User-Optionskopie/-mutation, ein anderer TID schließt
   den sichtbaren FD.
4. Rollen-TSYNC, `/proc`-Inventur und Options-/Queue-/OFD-Snapshot melden PASS.
5. Der fremde TID setzt nach Snapshot fort und mutiert `SO_PASSRIGHTS=1`.
6. Nach Senderfreigabe kann ein Rights-SKB eingereiht werden; ein gestoppter
   Empfänger hält dessen file-/OFD-/Lock-Referenzen ohne Obergrenze.

Eine Resolution muss daher nicht versuchen, die verborgene Referenz besser zu
scannen. Sie muss deren Wirkung an einem Hook linearisieren, der auf dem
Socket selbst liegt, für jeden Prozess gilt und vor der eigentlichen Mutation
ausgeführt wird. Außerdem darf vor dieser Grenze keine Endpoint-Referenz in
einer fremden SCM_RIGHTS-Queue geparkt werden.

Die Linux-Syscall-Reihenfolge erfüllt diese Anforderung: Nach FD-Lookup ruft
`do_sock_setsockopt()` zuerst `security_socket_setsockopt(sock,level,optname)`
auf. Erst nach dessen Erfolg folgen Cgroup-Sockopt, Userwertkopie,
Protokollpfad und eigentliche Optionsmutation. Ein BPF-LSM-Programm am Hook
entscheidet deshalb auch über einen Caller, der den sichtbaren FD bereits
geschlossen hat und nur noch die vom Syscall gehaltene `struct file` besitzt.

---

## 4. Resolution von V18-H1

### 4.1 Globale Guard-Installation vor jeder Rolle und jedem Socket

`TerminalRuntimeSocketLSMGuardV1` wird vor Rollen- oder Socket-Erzeugung als
globales BPF LSM angehängt. Revision 19 bindet:

- `socket_post_create`;
- `unix_stream_connect`;
- `socket_setsockopt`;
- `socket_sendmsg`;
- `file_receive`;
- `BPF_MAP_TYPE_SK_STORAGE`;
- dedizierte Session-Cgroup-ID, Session-Nonce und exakte Bootstrap-TID-/TGID-/
  Startzeitidentitäten;
- Kernel-Build, BTF, aktive LSM-Liste, Program-/Map-/Link-IDs, Program Tags,
  Pin-Inodes und private bpffs-Mountidentität.

Programme, Maps und BPF Links müssen vor dem ersten Runtime-Socket erfolgreich
geladen, global angehängt und gepinnt sein. Fehlendes `CONFIG_BPF_LSM`,
`CONFIG_SECURITY_NETWORK`, BTF, SK-STORAGE, Helper-/Hook-Support oder fehlendes
`bpf` in der aktiven LSM-Liste verhindert OPEN ohne Fallback. Eine
Userspace-/Seccomp-Nachbildung ist nicht äquivalent.

Normative Spezifikationsreferenzen: Zeilen 230–247, 468–486 und 1493–1512.

### 4.2 Socketlokaler Tag vor FD-Sichtbarkeit

`socket_post_create` erzeugt auf jedem aus der dedizierten Session-Cgroup
stammenden AF_UNIX-SEQPACKET-Socket einen socketlokalen Guard-State, bevor der
erzeugende Syscall einen FD an Userspace zurückgibt.
`unix_stream_connect` überträgt denselben Session-Schutz auf das serverseitige
`newsk`, bevor `connect`/`accept4` erfolgreich werden kann. Tag- oder Storage-
Fehler liefern `-EPERM`; ein ungetaggter Socket kann kein Runtime-Endpunkt
werden.

Der Tag ist an `struct sock`, nicht an einen FD-Slot oder Prozess gebunden. Er
überlebt FD-Close/-Dup, SCM_RIGHTS, `pidfd_getfd`, Prozess- und Namespace-
Grenzen und verschwindet erst mit dem Socket selbst.

Normative Spezifikationsreferenz: Zeilen 1513–1520.

### 4.3 Externe Endpoint-Akquisition und Bootstrap-Queueing sperren

Der globale `file_receive`-Hook verweigert `receive_fd()` für jedes geschützte
Runtime-Socket mit `-EPERM`. Dies erfasst sowohl SCM_RIGHTS-Empfang als auch
`pidfd_getfd`. `/proc/<pid>/fd`-/Ptrace-Akquisition bleibt zusätzlich durch
`PR_SET_DUMPABLE=0`, leere Capability-Sets, Ptrace-/Yama-Policy und den
ausdrücklichen Ausschluss privilegierter Co-Tenants gesperrt.

Solange Session-State `BOOTSTRAP` gilt, verweigert der globale
`socket_sendmsg`-Hook jeden `sendmsg`-/`sendmmsg`-Pfad eines Session-Cgroup-
Tasks vor der Protokollübergabe. Das gilt unabhängig von FD, Ziel, `msghdr`,
Controlbuffer und TID. Vor der Versiegelung kann daher weder eine fachliche
Nachricht noch ein Runtime-Endpoint als SCM_RIGHTS in einer fremden Queue
geparkt werden.

Normative Spezifikationsreferenz: Zeilen 1521–1533.

### 4.4 Globales Options-Seal am Socket

Auf jedem der zwölf verbleibenden finalen Sender- und Empfangssockets erlaubt
`socket_setsockopt` genau einen Initialisierungsvorgang mit
`SO_PASSRIGHTS=0`; der Empfangswert bleibt zusätzlich fachliche Prequeue-
Autorität:

- Caller ist der exakt gebundene single-threaded Bootstrap-TID;
- Socket-State ist exakt `INIT`;
- Level/Optname sind exakt `SOL_SOCKET|SO_PASSRIGHTS`;
- der LSM-Hook führt vor jeder Optionskopie/-mutation atomar
  `INIT→SEALED` aus.

Danach erhält jeder konkurrierende, fremde, wiederholte oder spätere
`setsockopt`-Caller global `-EPERM`. Der Hook liest den Userwert nicht; der
Owner muss nach Syscall-Return sofort `getsockopt(SO_PASSRIGHTS)==0` beweisen.
Ein fehlerhafter, unterbrochener oder mit `1` ausgeführter Erstaufruf macht den
versiegelten Socket unbrauchbar und zerstört den gesamten Startup. Ein
nachträglicher Korrekturaufruf ist verboten.

Weil der erlaubte Setter single-threaded ist, kann derselbe TID bei einem
Block vor oder nach dem LSM-Hook nicht zugleich bis zum Snapshot
fortschreiten. Jeder andere TID wird global verweigert. Damit existiert kein
Post-Snapshot-Mutationscaller.

Normative Spezifikationsreferenz: Zeilen 1558–1583.

### 4.5 Defense in Depth und autoritativer Snapshot

Die bisherige lokale Grenze bleibt zusätzlich erhalten:

- vollständige Empfänger-TID-/Files-Table-Topologie;
- `TerminalRuntimeChannelRightsFreezeFilterV2` per TSYNC auf jedem
  Empfänger-TID;
- `SECCOMP_RET_KILL_PROCESS` für jeden Rollen-`setsockopt`;
- vollständige finale Rollenfilter;
- danach `getsockopt(SO_PASSRIGHTS)==0`, `scm_fds: 0`, leere Queue und keine
  lokalen FD-/FDINFO-/OFD-/Lock-Reste;
- absenter Receive-Controlbuffer als weitere Defense in Depth.

Der Snapshot bindet zusätzlich alle zwölf Socket-Tags, `SEALED`, genau einen
erfolgreichen Init-Hook, aktive Link-/Program-/Map-Identitäten und Session-
State `BOOTSTRAP`. Ein hostweiter `/proc`-Scan bleibt nur diagnostisch. Er ist
keine Exklusivitäts-, Quieszenz- oder PASS-Autorität mehr.

Normative Spezifikationsreferenz: Zeilen 1580–1600.

### 4.6 Durable OPEN vor Senderrelease

Revision 18 ließ die relative Ordnung von Senderfreigabe und OPEN nicht
eindeutig genug. Revision 19 ordnet nun strikt:

1. Guard/Tag/Seal, TSYNC, Rollenfilter und Snapshot PASS;
2. `RUNTIME_SESSION_OPEN` mit allen Guard-/Endpointidentitäten durable
   schreiben;
3. bestätigte Durability;
4. ausschließlich der single-threaded Guard führt einmalig und atomar
   `BOOTSTRAP→RELEASED` aus;
5. erst dann lässt `socket_sendmsg` die durch Rollenfilter skalar erlaubten
   sechs Runtime-Endpunkte passieren;
6. der Guard schließt den letzten schreibbaren Map-FD.

Rollen besitzen keine Link-/Map-FDs, BPF-/Admin-Capabilities, `bpf`-, bpffs-,
Mount- oder Detach-Autorität. Links und Pins bleiben bis zur bewiesenen
Endpoint-Zerstörung aktiv. Release vor OPEN, zweiter Release, Rücktransition,
Linkverlust oder Map-Mutation ist terminal. OPEN ohne Release bleibt unclosed
und darf keinen fachlichen Send ausführen.

Normative Spezifikationsreferenzen: Zeilen 1612–1636 und 2247–2267.

### 4.7 Totaler Fehlerpfad

Bei jeder Abweichung bleibt der Session-State `BOOTSTRAP`; der globale Send-
Hook verhindert deshalb neue Queue-Referenzen. Launcher/Guard terminieren alle
vier Rollen und schließen Listener-/Launcher-FDs. PASS des Cleanup verlangt:

- Socket-/Queue-Zerstörung;
- null SKB-/file-/OFD-/Lock-Referenz;
- weiterhin aktive Guard-Links während der Zerstörung;
- keine Wiederverwendung von Prozess, Session-Nonce oder Endpoint;
- ausschließlich einen vollständig neuen Startup-Versuch.

Ein externer Holder kann nicht entstanden sein: Bootstrap-Transfer scheitert
am Send-Hook, SCM-/pidfd-Empfang am `file_receive`-Hook, `/proc`-/Ptrace-
Akquisition an der gebundenen Credential-Grenze und jede dennoch laufende
Optionsmutation am socketlokalen Seal.

Normative Spezifikationsreferenz: Zeilen 1602–1610.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Setup-FSM und Race-Abdeckung

| Phase | Monotone Kernelgrenze | Autoritativer Nachweis | Fehlerfolge |
|---|---|---|---|
| `LSM_ATTACHED` | globale BPF-LSM-Links vor Runtimeobjekten | Hook-/BTF-/Program-/Map-/Link-/Pin-Identitäten | kein Socket/keine Rolle starten |
| `BOOTSTRAP` | alle Session-`sendmsg`/`sendmmsg` global `-EPERM` | Session-Cgroup/Nonce/State | kein Queueing möglich |
| `ENDPOINTS_TAGGED` | SK-STORAGE-Tag vor FD-Sichtbarkeit | zwölf richtige Socket-Tags | Endpoint verwerfen |
| `RIGHTS_SEALED` | einmalig `INIT→SEALED` im globalen Setsockopt-Hook | genau ein Init-Hook plus Get `0` | alle Endpoints zerstören |
| `RIGHTS_FROZEN` | TSYNC killt jeden Rollen-`setsockopt` | komplette TID-/Filterhashmenge | Rollen terminieren |
| `ROLES_FROZEN` | finale FD-/Task-/Transfer-Allowlist | Rollenfilter-/FD-Inventur | Startup abbrechen |
| `SNAPSHOT_PASSED` | LSM-Seal bleibt aktiv; Send-Gate bleibt geschlossen | Option/Queue/OFD/Lock plus Guard-State | kein OPEN bei Abweichung |
| `OPEN_DURABLE` | Sessionrecord ist durable, Send-Gate noch geschlossen | durable Record/Fingerprint | unclosed bei Releasefehler |
| `RELEASED` | einmalig `BOOTSTRAP→RELEASED` | Guard-CAS/Map-FD-Close | normaler Runtime-Send erlaubt |

Der V18-H1-Caller wird in jeder möglichen Lage geschlossen:

| Lage des fremden Callers | Revision-19-Wirkung |
|---|---|
| vor Socket-Erzeugung | kein Endpoint existiert; Guard ist bereits global attached |
| Erwerb per SCM_RIGHTS/pidfd | Bootstrap-Send oder `file_receive` liefert `-EPERM` |
| Erwerb per `/proc`/Ptrace | dumpable/capability/ptrace-Grenze verweigert Akquisition |
| FD aufgelöst, vor LSM-Hook blockiert | nach Fortsetzung liest LSM den socketlokalen `SEALED`-State und liefert `-EPERM` |
| LSM-Hook bereits passiert | nur der gebundene single-threaded Setter kann passieren; er kann den Startup nicht gleichzeitig fortführen |
| nach Snapshot, vor durablem OPEN | Seal verweigert Mutation; Send-Gate bleibt `BOOTSTRAP` |
| nach durablem OPEN, vor Release | Seal verweigert Mutation; Send-Gate bleibt `BOOTSTRAP` |
| nach Release | Seal und `file_receive` bleiben global aktiv; Rollenfilter und `SO_PASSRIGHTS=0` verhindern Rights-Queueing |

---

## 6. Fault-, Capability-, Evidence- und Completion-Gates

Revision 19 verlangt je Kanal den exakten V18-H1-Trial:

1. externer Akquisitionsversuch via SCM_RIGHTS, `pidfd_getfd` und `/proc/fd`;
2. `setsockopt(SO_PASSRIGHTS=1)` nach FD-Auflösung und vor LSM-Hook anhalten;
3. sichtbaren FD schließen;
4. `/proc`-Inventur und finalen Snapshot ausführen;
5. Caller nach Snapshot fortsetzen;
6. Caller nochmals nach durablem OPEN vor Release fortsetzen;
7. Variante mit Endpointmigration zwischen bereits inventarisierten Prozessen;
8. Variante mit fehlendem/falschem Tag, Link-/Map-/Pin-Verlust, falschem
   Bootstrap-TID, doppeltem Seal, Release vor OPEN, doppeltem Release und
   Rücktransition;
9. jeweils ein bis `SCM_MAX_FD` Rights plus mehrere CMSG-Reihenfolgen;
10. Empfänger-Stop/-Crash und Sender-Close/-Crash.

PASS verlangt stets:

- Akquisition/Transfer endet am `file_receive`-/Bootstrap-Send-Hook mit
  `-EPERM`, oder der bereits laufende Optionscaller endet am `SEALED`-
  Setsockopt-Hook vor Optionskopie/-mutation mit `-EPERM`;
- `SO_PASSRIGHTS=0`, `scm_fds: 0`, Queue, FD-/FDINFO-/OFD-/Lock-State bleiben
  unverändert;
- kein SKB hält eine Rights-/Endpointreferenz;
- OPEN wird durable vor Release;
- genau eine `BOOTSTRAP→RELEASED`-Transition findet statt;
- jeder Setup-Rest führt zu totalem Cleanup ohne Same-Session-Retry.

Die Capability-Matrix bindet zusätzlich die vollständige BPF-LSM-/BTF-/SK-
STORAGE-Helpermatrix und alle Program-/Map-/Link-/Pin-Identitäten. Evidence
bindet Guard-State, Tags, Seal-Zähler, verweigerte Hook-Aufrufe, durable OPEN-
Zeit, Release-Zeit und letzten schreibbaren Map-FD-Close. Completion fordert
dieselben Werte; ein `/proc`-Scan allein darf kein Gate erfüllen.

Normative Spezifikationsreferenzen: Zeilen 1797–1835, 1904–1934,
2004–2024, 2053–2075, 3303–3316, 3877–3895 und 4057–4109.

---

## 7. Versionierung und Preservation

Die Revision-19-Vertragsfamilie lautet exakt:

- `IU4RuntimeControlProfileV13`;
- Runtime Session Envelope V14;
- `TerminalLeaseControlWordV3`;
- `TerminalTradingSignalEnvelopeV1`;
- `TerminalKernelTripRequestV2`;
- `TerminalSelfKillEntryV4`;
- `RuntimeSessionCloseProtocolV7`;
- `TerminalRuntimeChannelProvisioningV4`;
- `TerminalTradingTaskTopologyV2`;
- `TerminalRuntimeReceiverTaskTopologyV2`;
- `TerminalRuntimeChannelRightsFreezeFilterV2`;
- `TerminalRuntimeSocketLSMGuardV1`;
- `TerminalParentGuardianV12`;
- `TerminalNativeTripBrokerV9`;
- `TerminalKernelLeaseShimV10`;
- `TerminalPersistenceWorkerV6`;
- `TerminalLeaseCapabilityProfileV12`;
- die unveränderten sechs Close-Nachrichtenschemas V3/V2.

Revision 19 bewahrt ausdrücklich:

- `V15-B1`: Signal-Envelope, `WAIT_KILLABLE_RECV`, Broker-CAS und terminale
  Listener-Ready-/Receive-Fehlerklassifikation;
- `V14-B1`: kein writable Same-Process-Trip-Latch; der Broker bleibt monotone
  Trip-Autorität;
- `V14-B2`: beide Worker-ACKs, beide Approval-Empfänger und alle sechs
  Richtung-/FD-/Payloadbindungen;
- `V14-H1`: endliche Close-FSM, absolute Deadlines, byteidentische Retries und
  exactly-once PREPARE-/COMMIT-Mutation;
- `V13-B2`: ausschließlich PREPARE→Broker-CLOSED→durable COMMIT ist clean;
- `V12-B1`/`V11-B1`: kein Pipe-Read/-Write/-Transfer im terminalen
  Sicherheitsweg;
- `V10-B1`: feste TID-/Files-Table-Topologie und Writer-Referenzsperre;
- `V9-B1`: Self→Guardian→Broker-PIDFD→Liveness-Close-Fallback;
- `V9-M1`: exakte Memfd-Create-/Seal-Zustandsmaschine;
- `V8-H1`: Broker-only RW Control Word und workerseitige Requestprüfung;
- Single Owner, No Dual Write, Decimal/PEE Economics, Atomic V2/Loss Cluster,
  Execution Control, Authority/Recovery/Genesis und L0/L1 Kill/Restart;
- Windows und jede Plattform ohne separat reviewte äquivalente
  Kernelprimitive bleiben unsupported und fail closed;
- Implementierung, IU4 ENFORCED, Exchange und Live bleiben nicht freigegeben.

V18-H1, V17-H1, V16-H1 und V15-H1 gelten in diesem Resolution-Arbeitsstrang
nur als `RESOLVED_PENDING_INDEPENDENT_REREVIEW`, nicht als unabhängig
geschlossen.

Normative Spezifikationsreferenz der Versionsfamilie: Zeilen 517–531.

---

## 8. Formale Verifikation und Scope-Nachweis

Die vollständige Revision-19-Spezifikation besitzt nach Abschluss:

```text
SPEC_V19_PATH: docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPEC_V19_LINES: 4161
SPEC_V19_SHA256: 191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b
```

Ausgeführt wurden ausschließlich read-only beziehungsweise dokumentbezogene
Prüfungen: `sha256sum`, `wc -l`, Versions-/State-/Finding-Referenzsuche,
Markdown-Tabellen-/Fence-/Inline-Code-Delimiterprüfung, Whitespace-Prüfung und
Git-Status-/HEAD-/Branch-Prüfung. Primäre Linux-Kernelquellen wurden read-only
zur Hook- und Syscall-Reihenfolge geprüft. Es wurden keine Runtime- oder
Write-Tests ausgeführt, weil dieser Schritt ausschließlich eine Paper-
Spezifikationsresolution ist.

```text
REVISION_18_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 1/1
V18_H1_RESOLVED_PENDING_REREVIEW: YES
V17_H1_RESOLVED_PENDING_REREVIEW: YES
V16_H1_RESOLVED_PENDING_REREVIEW: YES
V15_H1_RESOLVED_PENDING_REREVIEW: YES
V15_B1_CLOSED_STATUS_PRESERVED: YES
V14_B1_CLOSED_STATUS_PRESERVED: YES
V14_B2_CLOSED_STATUS_PRESERVED: YES
V14_H1_CLOSED_STATUS_PRESERVED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES
V9_B1_CLOSED_STATUS_PRESERVED: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CONTROL_WORD_WORKER_SCOPE_PRESERVED: YES
SINGLE_OWNER_PRESERVED: YES
NO_DUAL_WRITE_PRESERVED: YES
DECIMAL_BOUNDARY_PRESERVED: YES
ATOMIC_V2_LOSS_CLUSTER_PRESERVED: YES
EXECUTION_CONTROL_PRESERVED: YES
RUNTIME_OR_STATE_MUTATION: NO
WORKSTATION_R3_MUTATION_OR_RETRY: NO
RESEARCH_MUTATION: NO
STATE_RESEARCH_S45_CREATED: NO
GIT_STAGE_COMMIT_FETCH_PUSH: NO
SPECIFICATION_REVISION_19_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der einzige beabsichtigte Dokument-Scope dieser Resolution besteht aus der
Revision-19-Spezifikation und diesem neuen Resolution-Record. Bestehende
untracked Artefakte blieben unangetastet. Das Resolution-Protokoll enthält
keinen zirkulären Selbsthash.

---

## 9. Resolution-Urteil und nächster zulässiger Schritt

```text
RESOLUTION_RESULT: RESOLVED_PENDING_INDEPENDENT_REREVIEW
SPECIFICATION_REVISION: 19
SPECIFICATION_READY_FOR_INDEPENDENT_REREVIEW: YES
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-19-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen V19-Hash
`191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b`
prüfen. Er muss insbesondere verifizieren, dass die gewählten BPF-LSM-Hooks
und SK-STORAGE-Helper auf dem gebundenen Kernel tatsächlich attachbar sind,
dass `socket_setsockopt` vor jeder Optionskopie/-mutation linearisiert, dass
`file_receive` SCM_RIGHTS und `pidfd_getfd` erfasst, dass der Bootstrap-
`socket_sendmsg`-Gate jede vorzeitige Queueing-/Transfermöglichkeit sperrt und
dass durable OPEN strikt vor dem einmaligen Release liegt.

Erst dieser unabhängige Review darf `V18-H1`, `V17-H1`, `V16-H1` und `V15-H1`
schließen oder READY erklären. Bis dahin bleiben Implementierung, Aktivierung,
Exchange und Live gesperrt.
