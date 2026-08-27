# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-19 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-19 REREVIEW FINDINGS RESOLVED IN REVISION 20 — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand / HEAD / main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **main gegenüber origin/main:** `0 behind / 6 ahead`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V19-Hash:** `191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b`
- **Unabhängig geprüfte V19-Zeilen:** `4161`
- **Revision-19-Independent-Rereview-Record:** `256013a0e247097e1a47550d7669ca68fe5390484fe6b7464da7fdf5b3f0f4ca`
- **Revision-19-Independent-Rereview-Zeilen:** `444`
- **Controlling Revision-18-Resolution:** `6134a0e039b00281f6b5b97f3780af06d1ff6c348f4ef4fa1cb917345b481af9`
- **Controlling Revision-18-Resolution-Zeilen:** `486`
- **Resolution-Zielhash V20:** `18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0`
- **Resolution-Zielzeilen V20:** `4409`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die beiden offenen HIGH-Findings `V19-H1` und
`V19-H2` des unabhängigen read-only Re-Reviews der Revision 19 vollständig
einer normativen Korrektur in Revision 20 zu.

`V19-H1` betraf keinen Fehler des globalen `socket_sendmsg`-Hooks. Gerade seine
ausnahmslose BOOTSTRAP-Sperre war korrekt. Unausführbar war die weiterhin
behauptete Übergabe des vom Trading-Leader erzeugten Seccomp-Listener-FDs über
einen nicht näher definierten Bootstrap-Transferkanal an den Broker. Jeder
Sockettransfer hätte denselben globalen Send-Gate passieren müssen.

`V19-H2` betraf keinen fehlenden Wunsch nach Monotonie, sondern das Fehlen
einer realen Linux-Primitive. `BPF_MAP_UPDATE_ELEM` besitzt keine
expected-old-Value-CAS-Semantik. Lookup plus Update kann die behauptete
`BOOTSTRAP→RELEASED`-Linearisierung nicht herstellen.

Revision 20 entfernt beide Annahmen. Der Listener wird genau einmal per
`pidfd_getfd` in einem eng gebundenen, vor jeder Runtime-Socket-Erzeugung
irreversibel geschlossenen Handoff-Fenster dupliziert. Die Phase wird
ausschließlich durch programmseitige BPF-CMPXCHG in den gebundenen
`file_receive`- und `socket_shutdown`-LSM-Hooks verändert; ab Rollenstart existiert kein
Userspace-writable Phase-Map-FD.

Dieses Resolution-Protokoll zertifiziert die Korrektur nicht selbst. Sein
Status lautet `RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues
unabhängiges read-only Re-Review des vollständigen V20-Hashes darf die beiden
V19-Findings und die abhängige Kette `V18-H1 → V17-H1 → V16-H1 → V15-H1`
schließen oder READY erklären.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Vorhandene untracked Benutzerartefakte wurden nicht bereinigt,
überschrieben oder gestaged.

---

## 2. Ausgang des unabhängigen V19-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V19_SHA256: 191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b
SPEC_V19_LINES: 4161
REVISION_18_RESOLUTION_SHA256: 6134a0e039b00281f6b5b97f3780af06d1ff6c348f4ef4fa1cb917345b481af9
REVISION_19_REREVIEW_SHA256: 256013a0e247097e1a47550d7669ca68fe5390484fe6b7464da7fdf5b3f0f4ca
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 2
MEDIUM: 0
LOW: 0
```

| Finding | V19-Re-Review | V20-Resolution |
|---|---|---|
| `V19-H1` | Der globale Send-Gate verweigerte jedem Session-Cgroup-Task jeden `sendmsg`/`sendmmsg`, während der Trading-Leader den Seccomp-Listener weiterhin über einen Bootstrap-Transferkanal an den Broker übergeben sollte. Kein alternativer ausführbarer Ownership-Pfad war definiert. | `TerminalSeccompListenerHandoffV2` verwendet keinen Socket. Der Broker dupliziert den reservierten Listener-Quell-FD per `pidfd_getfd`; der `file_receive`-Hook erzwingt genau einmal durch `LISTENER_HANDOFF→LISTENER_RECEIVED`. ACK läuft über einen vor Fork geerbten Eventfd. Trading schließt den Quell-FD und widerruft Ptrace/Dumpable vor jeder Runtime-Socket-Erzeugung. Der Send-Gate bleibt ohne Ausnahme geschlossen. |
| `V19-H2` | Eine exakte Userspace-CAS über den einzigen schreibbaren Map-FD wurde gefordert, obwohl die Map-Update-UAPI nur `ANY`, `NOEXIST`, `EXIST` und `F_LOCK`, aber keine expected-old-CAS bereitstellt. | `TerminalRuntimeSocketGuardPhaseV2` ist ein einzelnes ausgerichtetes `u64` in einer userspace-read-only und eingefrorenen Array-Map. Nur BPF-LSM-Hooks führen `BPF_ATOMIC\|BPF_DW\|BPF_CMPXCHG` aus. `file_receive` bindet Handoff→Received, `SHUT_RD` Received→BOOTSTRAP und `SHUT_RDWR` BOOTSTRAP→RELEASED. Lookup+Update und jeder Userspace-Writer sind verboten. |

Der unabhängige Review bestätigte bereits die Positionen und grundsätzliche
Attachbarkeit von `socket_post_create`, `unix_stream_connect`,
`socket_setsockopt`, `socket_sendmsg` und `file_receive`, außerdem
`pidfd_getfd → receive_fd → file_receive`. Revision 20 bewahrt diese
No-Findings und ergänzt genau die fehlenden ausführbaren Kontrollgrenzen.

---

## 3. Resolution von V19-H1

### 3.1 Unveränderte globale Sendesperre

Revision 20 fügt keine `sendmsg`-/`sendmmsg`-Ausnahme hinzu. Der globale
`socket_sendmsg`-Hook verweigert in den Phasen `LISTENER_HANDOFF`,
`LISTENER_RECEIVED` und `BOOTSTRAP` jeden Sendepfad eines Session-Cgroup-Tasks vor der
Protokollübergabe. FD, Ziel, `msghdr`, Controlbuffer, Prozess und TID ändern
diese Entscheidung nicht.

Damit bleibt der Kern der V19-Grenze erhalten:

- kein fachliches Paket vor durablem OPEN;
- kein SCM_RIGHTS-Paket in einer internen oder fremden Queue;
- kein Listenertransfer über AF_UNIX;
- kein Endpointtransfer vor Seal/Freeze/Snapshot;
- keine ungeschriebene privilegierte Bootstrap-Ausnahme.

Normative Spezifikationsreferenzen: Zeilen 248–260, 509–516 und 1658–1665.

### 3.2 `TerminalSeccompListenerHandoffV2`

Der Handoff beginnt in Phase `LISTENER_HANDOFF`, bevor irgendein Runtime-Socket
existiert. Broker und der noch single-threaded Trading-Leader besitzen bereits
gebundene PID-/Startzeitidentitäten in der Session-Cgroup. Die Files-Table
beider Prozesse ist exakt inventarisiert:

- Trading hält den reservierten Listener-Quell-FD frei;
- Broker hält den nach Linux-Niedrigst-FD-Allokation erwarteten Ziel-FD frei;
- Broker besitzt den gebundenen Trading-PIDFD;
- beide besitzen genau den vor Fork geerbten ACK-Eventfd auf festen FDs;
- keine Rolle besitzt zu diesem Zeitpunkt ein Runtime-Socket.

Die einzige zugelassene Ptrace-Konfiguration ist Linux-Yama
`ptrace_scope=1` bei gleichen Real-Credentials. Trading setzt einmalig
`PR_SET_PTRACER` auf die gebundene Broker-PID. Jeder andere Yama-Modus, andere
Credentials, ein zweiter Ptracer oder ein privilegierter Co-Tenant verhindert
den Startup.

Normative Spezifikationsreferenzen: Zeilen 437–444, 1105–1113 und 1173–1192.

### 3.3 Genau eine Listener-Duplikation

Trading installiert als einziger TID den gebundenen Seccomp-Filter mit
`NEW_LISTENER|WAIT_KILLABLE_RECV`. Der Kernelreturn muss exakt im reservierten
Quell-FD landen. Danach ruft ausschließlich der gebundene Broker-Bootstrap-TID
genau einmal auf:

```text
pidfd_getfd(trading_pidfd, listener_source_fd, 0)
```

Der Broker-Bootstrap-Seccomp-Filter erlaubt nur dieses skalare Tupel. Genau-
einmal kann Seccomp allein jedoch nicht zählen. Deshalb prüft der globale
`file_receive`-Hook zusätzlich exakten Broker-TGID/TID/Startzeit/Cgroup und
den nicht-socketartigen Filetyp und führt vor FD-Allokation die BPF-CMPXCHG
`LISTENER_HANDOFF→LISTENER_RECEIVED` aus. Nur der Gewinner erhält `0`; jeder
zweite, andere oder wiederholte Receive-Versuch sieht den falschen Altwert und
erhält `-EPERM`.

Geschützte Runtime-Sockets und der Guard-Control-Socket bleiben disjunkt und
erhalten weiterhin `-EPERM`. Diese Zulassung ist kein generischer
`pidfd_getfd`-Bypass. Der Return-FD muss exakt dem reservierten niedrigsten
freien Broker-Ziel-FD entsprechen. Scheitert `receive_fd` nach der CMPXCHG,
bleibt `LISTENER_RECEIVED` terminal und die Session darf nicht retried werden.

Normative Spezifikationsreferenz: Zeilen 1194–1211.

### 3.4 ACK, Single Owner und irreversible Revocation

Der Broker prüft Listener-Inode, Anon-Inode-Typ, Filterhash, Session-Nonce und
Ready-Nonce. Er signalisiert Erfolg ausschließlich über den geerbten Eventfd.
Erst nach passendem ACK:

1. schließt Trading den Listener-Quell-FD;
2. beweist der externe Observer dessen Abwesenheit;
3. setzt Trading exakt `PR_SET_PTRACER=0`;
4. setzt Trading exakt `PR_SET_DUMPABLE=0`;
5. setzt auch Broker `PR_SET_DUMPABLE=0`;
6. leeren beide alle Capability-Sets und setzen `no_new_privs`;
7. sperren finale Filter `pidfd_getfd`, Ptrace-/Dumpable-Lockerung,
   Listener-Erzeugung, FD-Duplikation und Transfer;
8. belegt der externe Observer genau einen Listener-Halter: den Broker-Ziel-FD.

Erst danach darf der Kernel die Phase von `LISTENER_RECEIVED` nach `BOOTSTRAP`
wechseln. Bis zu dieser
Grenze verweigert `socket_post_create` jedes Session-
`AF_UNIX|SOCK_SEQPACKET`-Runtime-Socket. Ein Fehler oder Halt an irgendeiner
Stelle zerstört den Startup ohne Retry derselben Session.

Normative Spezifikationsreferenzen: Zeilen 1213–1238 und 1619–1648.

**Resolutionstatus V19-H1:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution von V19-H2

### 4.1 Reales Phase-ABI

`TerminalRuntimeSocketGuardPhaseV2` besitzt exakt dieses normative Layout:

```text
map_type: BPF_MAP_TYPE_ARRAY
key_size: 4
key: u32(0)
max_entries: 1
value_size: 8
value_alignment: 8
value: u64 phase
initial_value: LISTENER_HANDOFF = 0
LISTENER_RECEIVED: 1
BOOTSTRAP: 2
RELEASED: 3
```

Die Phase-Map wird mit `map_flags=0` erzeugt. Für die Array-Map ist der
Initialwert kernelbedingt null; es ist daher kein Userspace-Initialupdate
erforderlich. Der Guard lädt die einzigen beiden schreibenden
`file_receive`-/`socket_shutdown`-BPF-Hookprogramme und führt
noch vor Rollenstart über den dafür schreibberechtigten Create-FD
`BPF_MAP_FREEZE` aus. Danach schließt er diesen FD und öffnet ausschließlich
über `BPF_OBJ_GET` mit `file_flags=BPF_F_RDONLY` einen Lese-FD. Dadurch kann
kein späterer BPF-Syscall den Map-State verändern, während das bereits
geladene BPF-Programm weiterhin auf seinen Map-Value schreiben darf.

Die Konfiguration liegt getrennt in einer vor Freeze vollständig befüllten
Map. Sie bindet Session-Nonce, Cgroup-ID, Guard-TGID/TID/Startzeit und den
Socket-Cookie des einzigen Phase-Control-Sockets. Autoritative Phase ist nur
das einzelne `u64`; es existiert kein mehrfeldriger Publikationsvertrag.

Normative Spezifikationsreferenzen: Zeilen 499–516 und 1601–1617.

### 4.2 Kerneltrigger über `socket_shutdown`

Revision 20 hängt einen sechsten BPF-LSM-Link an `socket_shutdown`. Der Guard
erzeugt ein unverbundenes `AF_UNIX|SOCK_DGRAM|SOCK_CLOEXEC`-Control-Socket,
das vor Rollenstart disjunkt als `PHASE_CONTROL` getaggt wird. Nur der exakt
gebundene Guard-TID darf `shutdown` darauf aufrufen.

Der LSM-Hook liegt vor dem eigentlichen Socket-Protokoll-Shutdown. Sein
BPF-Programm führt direkt auf dem ausgerichteten Map-Value eine atomare
Compare-and-Exchange mit dem Linux-BPF-Instruktionsencoding
`BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` aus:

| Guard-Aufruf | erwarteter Altwert | Zielwert |
|---|---:|---:|
| `shutdown(control_fd,SHUT_RD)` | `LISTENER_RECEIVED=1` | `BOOTSTRAP=2` |
| `shutdown(control_fd,SHUT_RDWR)` | `BOOTSTRAP=2` | `RELEASED=3` |

Bei erfolgreicher CMPXCHG gibt der Hook absichtlich `-EINPROGRESS` zurück.
Der darunterliegende Socket-Shutdown wird deshalb nicht ausgeführt. Der Guard
akzeptiert ausschließlich dieses `errno` zusammen mit dem unmittelbar
gelesenen Zielwert. Falscher Altwert, falscher TID, Socket-Cookie oder
`how`-Wert liefert `-EALREADY` beziehungsweise `-EPERM` und mutiert nichts.

Normative Spezifikationsreferenzen: Zeilen 1585–1632.

### 4.3 Kein Userspace-CAS und kein TOCTOU

Explizit keine Phase-Transition sind:

- `BPF_MAP_UPDATE_ELEM` mit `BPF_ANY`;
- `BPF_NOEXIST` oder `BPF_EXIST`;
- `BPF_F_LOCK`;
- Lookup plus späteres Update;
- mmap-/Userspace-Atomic auf Map-Speicher;
- Pin-Reopen;
- Schreiben über einen vermeintlich letzten Map-FD.

Damit entfällt die beanstandete Userspace-TOCTOU vollständig. Bei jeder
Transition gibt es weder einen schreibbaren Phase-Map-FD noch einen
userspace-seitigen erwarteten Altwert. Verglichen und geschrieben wird in
einer einzigen Kernel-BPF-Instruktion am selben acht Byte großen Value.

Die Capability bindet Kernel/BTF, Hook-Attach, Verifierlog, JIT-/Program-Tag,
Map-ID/-Flags/-Freeze, Value-Größe/-Ausrichtung und das tatsächlich erzeugte
CMPXCHG-Encoding. Eine Architektur oder Toolchain, die diese Instruktion nicht
exakt erzeugt und verifiziert, ist kein zulässiger Capability-PASS.

Normative Spezifikationsreferenzen: Zeilen 1934–1982 und 2052–2093.

### 4.4 Strikte Release-Reihenfolge

Die integrierte Release-Ordnung lautet:

1. genau ein `file_receive` linearisiert vor FD-Installation
   `LISTENER_HANDOFF→LISTENER_RECEIVED`;
2. `LISTENER_RECEIVED→BOOTSTRAP` erst nach Listener-Single-Ownership und
   irreversibler Ptrace-/Dumpable-Revocation;
3. sämtliche Runtime-Kanäle erst in `BOOTSTRAP` erzeugen;
4. alle zwölf Endpunkte taggen und `INIT→SEALED` mit `SO_PASSRIGHTS=0`
   abschließen;
5. Receiver-TSYNC, finale Rollenfilter und post-filter Snapshot abschließen;
6. `RUNTIME_SESSION_OPEN` durable schreiben;
7. erst nach bestätigter Durability `shutdown(control_fd,SHUT_RDWR)`;
8. nur die kernelinterne CMPXCHG `BOOTSTRAP→RELEASED` öffnet die sechs
   skalar erlaubten Runtime-Sendepfade.

Release vor OPEN, doppelter Release, falscher Altwert, Rücktransition,
Linkverlust, Freezeverlust oder eine andere Mapmutation ist terminal. OPEN
ohne Release bleibt unclosed und kann keine fachliche Nachricht senden.

Normative Spezifikationsreferenzen: Zeilen 1722–1763 und 2430–2462.

**Resolutionstatus V19-H2:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Integrierte Setup-FSM

| Phase | Kernelgrenze | Autoritativer Nachweis | Fehlerfolge |
|---|---|---|---|
| `GUARD_ATTACHED` | sechs BPF-LSM-Links aktiv | Hook-/BTF-/Program-/Map-/Link-/Pin-Identitäten | keine Rolle starten |
| `LISTENER_HANDOFF` | Runtime-Socket-Create und jeder Session-Send verweigert | Phase `0`, Cgroup/Nonce, Control-Socket-Cookie | neuer Startup erforderlich |
| `LISTENER_RECEIVED` | genau ein `file_receive`-CMPXCHG `0→1` vor FD-Installation | reservierte Quell-/Ziel-FDs, Listener-Inode/Filterhash | kein zweiter Receive; bei Folgfehler Abbruch |
| `HANDOFF_REVOKED` | Trading-FD geschlossen, Ptracer/Dumpable/Capabilities entzogen | genau ein Broker-Halter | kein BOOTSTRAP bei Abweichung |
| `BOOTSTRAP` | Shutdown-Hook-CMPXCHG `1→2`, Send-Gate weiter geschlossen | `EINPROGRESS`, gelesener Wert `2` | kein Runtime-Send |
| `ENDPOINTS_SEALED` | zwölf `INIT→SEALED`, Receiver-TSYNC und Rollenfilter | Tags, Get `0`, Filterhashes | totaler Endpoint-Cleanup |
| `SNAPSHOT_PASSED` | Seals und Send-Gate bleiben aktiv | Queue/FD/OFD/Lock plus Guard-State | kein OPEN bei Abweichung |
| `OPEN_DURABLE` | Sessionrecord durable, Send-Gate noch geschlossen | Record/Fingerprint | unclosed bei Releasefehler |
| `RELEASED` | Shutdown-Hook-CMPXCHG `2→3` | `EINPROGRESS`, gelesener Wert `3` | normaler Runtime-Send erlaubt |

Es gibt in dieser FSM keinen Sockettransfer vor `RELEASED` und keine Phase,
in der Userspace die Phasen-Map schreiben kann.

---

## 6. Fault-, Capability-, Evidence- und Completion-Gates

Revision 20 verlangt für `TerminalSeccompListenerHandoffV2` mindestens:

1. Yama-Modi ungleich `ptrace_scope=1`;
2. falsche Real-Credentials und Broker-PID/-Startzeit/-PIDFD;
3. falschen, zweiten oder mehrfachen `PR_SET_PTRACER`;
4. falschen Trading-Quell- oder Broker-Ziel-FD;
5. jedes abweichende `pidfd_getfd`-Argument und einen zweiten Aufruf;
6. unerwarteten Return-FD;
7. fehlendes, fremdes oder mehrfaches Eventfd-ACK;
8. Trading-FD-Closefehler;
9. Halt/Crash jedes Beteiligten an jeder Handoff-Grenze;
10. fehlgeschlagene `PR_SET_PTRACER=0`-/`PR_SET_DUMPABLE=0`-Revocation;
11. mehr als einen Listener-Halter;
12. jeden Runtime-Socket-Erzeugungs- und `sendmsg`-Versuch vor BOOTSTRAP.

Revision 20 verlangt für `TerminalRuntimeSocketGuardPhaseV2` mindestens:

1. fehlendes oder falsches `file_receive`-/`socket_shutdown`-Attach;
2. falschen Control-Socket/-Cookie/-Guard-TID;
3. `SHUT_WR`, vertauschte, doppelte oder rückwärts gerichtete Transitionen;
4. Release vor durablem OPEN;
5. jeden `BPF_MAP_UPDATE_ELEM`-, mmap-, Lookup+Update- und `BPF_F_LOCK`-Pfad;
6. von null abweichende Create-Flags, fehlendes `BPF_MAP_FREEZE`, einen nicht
   geschlossenen Create-FD oder fehlendes read-only
   `BPF_OBJ_GET|BPF_F_RDONLY`;
7. falsche Mapart, Key-/Value-Größe, Ausrichtung oder Anzahl Einträge;
8. ein Programm ohne exaktes `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`;
9. abweichendes Hook-`errno` oder ausgeführten Protokoll-Shutdown;
10. Pin-/Link-/Mapverlust vor Endpoint-Zerstörung.

PASS verlangt genau einen Broker-Listener-Halter, null Runtime-Sockets und null
Session-Send während `LISTENER_HANDOFF|LISTENER_RECEIVED|BOOTSTRAP`; danach
genau die drei gebundenen Kernel-CMPXCHG-Transitionen. Jeder andere Fall bricht den Startup ohne
Same-Session-Retry ab.

Evidence bindet Quell-/Ziel-FD, PIDFD, ACK, Ptracer/Dumpable, Halterinventur,
Phase-/Config-Map-ID/-Flags/-Freeze, Control-Socket-Cookie,
`socket_shutdown`-Program-Tag, Verifier-/JIT-CMPXCHG-Nachweis,
Transitionsergebnisse/-zeiten, durable OPEN und Senderfreigabe. Capability-,
Per-Startup- und Completion-Gates verlangen dieselben Werte.

Normative Spezifikationsreferenzen: Zeilen 1994–1999, 2052–2095, 2168–2200,
2190–2252, 3496–3519, 4082–4106 und 4279–4309.

---

## 7. Versionierung und Preservation

Die Revision-20-Vertragsfamilie lautet exakt:

- `IU4RuntimeControlProfileV14`;
- Runtime Session Envelope V15;
- `TerminalLeaseControlWordV3`;
- `TerminalTradingSignalEnvelopeV1`;
- `TerminalKernelTripRequestV2`;
- `TerminalSelfKillEntryV4`;
- `TerminalSeccompListenerHandoffV2`;
- `RuntimeSessionCloseProtocolV8`;
- `TerminalRuntimeChannelProvisioningV5`;
- `TerminalTradingTaskTopologyV2`;
- `TerminalRuntimeReceiverTaskTopologyV3`;
- `TerminalRuntimeChannelRightsFreezeFilterV3`;
- `TerminalRuntimeSocketLSMGuardV2`;
- `TerminalRuntimeSocketGuardPhaseV2`;
- `TerminalParentGuardianV13`;
- `TerminalNativeTripBrokerV10`;
- `TerminalKernelLeaseShimV11`;
- `TerminalPersistenceWorkerV7`;
- `TerminalLeaseCapabilityProfileV13`;
- die unveränderten sechs Close-Nachrichtenschemas V3/V2.

Revision 20 bewahrt ausdrücklich:

- V19s globales `socket_setsockopt`-Seal und die zwölf `INIT→SEALED`-Grenzen;
- V19s `file_receive`-Fence für geschützte Runtime-Sockets;
- V19s ausnahmslosen Send-Gate vor durablem OPEN;
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

`V19-H1`, `V19-H2`, `V18-H1`, `V17-H1`, `V16-H1` und `V15-H1` gelten in
diesem Resolution-Arbeitsstrang nur als
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`, nicht als unabhängig geschlossen.

Normative Spezifikationsreferenz der Versionsfamilie: Zeilen 551–566.

---

## 8. Linux-UAPI- und Hook-Bindung

Die dokumentbezogene Prüfung band die neuen Primitiven an Linux v6.18:

- `include/uapi/linux/bpf.h` definiert `BPF_ATOMIC`, `BPF_CMPXCHG`,
  `BPF_F_RDONLY`, `BPF_OBJ_GET` und `BPF_MAP_FREEZE`;
- die BPF-ISA definiert 64-Bit-CMPXCHG als atomaren Vergleich gegen den
  erwarteten Wert und bedingten Austausch desselben Map-Values;
- `BPF_MAP_FREEZE` verlangt einen schreibberechtigten FD, sperrt danach
  spätere syscallseitige Map-Mutationen, nicht jedoch den Zugriff des bereits
  geladenen Programms; deshalb wird zuerst gefroren, dann der Create-FD
  geschlossen und erst danach read-only wieder geöffnet;
- `socket_shutdown(struct socket *,int)` ist ein BPF-LSM-attachbarer Hook und
  entscheidet vor dem eigentlichen Socket-Shutdown;
- `pidfd_getfd` verwendet `receive_fd`, dessen `file_receive`-Hook vor neuer
  Userspace-FD-Installation liegt.

Die lokale BTF des Review-Hosts `6.18.33.2-microsoft-standard-WSL2` enthält
`socket_shutdown` und `security_socket_shutdown`. Die lokalen UAPI-Header
bestätigten `BPF_ATOMIC`, `BPF_CMPXCHG`, `BPF_OBJ_GET`, `BPF_F_RDONLY` und
`BPF_MAP_FREEZE`. Das ist keine Zielsystem-Capability-Zertifizierung; Revision
20 fordert weiterhin den exakten produktiven Kernel-/BTF-/Verifier-/JIT-
Fingerprint und bleibt bei jeder Abweichung fail closed.

---

## 9. Formale Verifikation und Scope-Nachweis

Die vollständige Revision-20-Spezifikation besitzt nach Abschluss:

```text
SPEC_V20_PATH: docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPEC_V20_LINES: 4409
SPEC_V20_SHA256: 18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0
```

Ausgeführt wurden ausschließlich read-only beziehungsweise dokumentbezogene
Prüfungen: `sha256sum`, `wc -l`, Versions-/State-/Finding-Referenzsuche,
Markdown-Tabellen-/Fence-/Inline-Code-Delimiterprüfung, Whitespace-Prüfung,
Git-Status-/HEAD-/Branch-Prüfung sowie read-only Linux-UAPI-/BTF-/Kernel-
Dokumentationsprüfung. Es wurden keine Runtime- oder Write-Tests ausgeführt,
weil dieser Schritt ausschließlich eine Paper-Spezifikationsresolution ist.

```text
REVISION_19_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 2/2
V19_H1_RESOLVED_PENDING_REREVIEW: YES
V19_H2_RESOLVED_PENDING_REREVIEW: YES
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
SPECIFICATION_REVISION_20_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der einzige beabsichtigte Dokument-Scope dieser Resolution besteht aus der
Revision-20-Spezifikation und diesem neuen Resolution-Record. Bestehende
untracked Artefakte blieben unangetastet. Das Resolution-Protokoll enthält
keinen zirkulären Selbsthash.

---

## 10. Resolution-Urteil und nächster zulässiger Schritt

```text
RESOLUTION_RESULT: RESOLVED_PENDING_INDEPENDENT_REREVIEW
SPECIFICATION_REVISION: 20
SPECIFICATION_READY_FOR_INDEPENDENT_REREVIEW: YES
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-20-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen V20-Hash
`18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0`
prüfen. Er muss insbesondere verifizieren:

1. dass `TerminalSeccompListenerHandoffV2` ohne `sendmsg`-Ausnahme ausführbar
   ist und genau einen Broker-Listener-Halter erzeugt;
2. dass kein Runtime-Socket vor vollständiger Ptrace-/Dumpable-Revocation
   entstehen kann;
3. dass `file_receive` die einzelne zulässige Listener-Duplikation vor
   FD-Installation durch `LISTENER_HANDOFF→LISTENER_RECEIVED` genau einmal
   erzwingt und jeden zweiten Receive verweigert;
4. dass `socket_shutdown` auf dem gebundenen Kernel als BPF-LSM-Hook
   attachbar ist und vor dem Protokoll-Shutdown entscheidet;
5. dass `map_flags=0 → BPF_MAP_FREEZE → Create-FD-Close →
   BPF_OBJ_GET|BPF_F_RDONLY` ausführbar ist und danach Userspace-Writes
   sperrt, während das gebundene LSM-Programm die Map per 64-Bit-CMPXCHG
   verändern kann;
6. dass Verifier/JIT exakt `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` auf dem
   ausgerichteten Array-Map-Value zulassen;
7. dass die drei Kernel-Hook-Transitionen nur in der spezifizierten Reihenfolge
   stattfinden und durable OPEN strikt vor RELEASED liegt;
8. dass V19s Socket-Tag, Options-Seal, `file_receive`, Send-Gate,
   `SO_PASSRIGHTS=0`, TSYNC-, Snapshot- und Cleanup-Grenzen unverändert bleiben.

Erst dieser unabhängige Review darf `V19-H1`, `V19-H2` und die abhängige
Finding-Kette schließen oder READY erklären. Bis dahin bleiben
Implementierung, Aktivierung, Exchange und Live gesperrt.
