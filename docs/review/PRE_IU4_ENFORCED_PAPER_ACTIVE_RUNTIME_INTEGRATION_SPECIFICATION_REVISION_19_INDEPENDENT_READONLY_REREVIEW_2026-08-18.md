# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-19 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-19-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Root verifiziert:** `/home/benja/projects/sniper-bot`
- **HEAD:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **Divergenz:** `main` ist exakt sechs Commits voraus (`0 6` für `origin/main...main`)
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel-Revision:** `19`
- **Reviewziel SHA-256:** `191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b`
- **Reviewziel Zeilen:** `4161`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_18_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `6134a0e039b00281f6b5b97f3780af06d1ff6c348f4ef4fa1cb917345b481af9`
- **Controlling Resolution Zeilen:** `486`
- **Controlling V18 Review:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_18_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md`
- **Controlling V18 Review SHA-256:** `8efb96b2e48c7ab3090e9aba7b2e71bcb421fdeabb269fc937970344e29fa427`
- **Controlling V18 Review Zeilen:** `482`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik, Scope und Aussagegrenze

`AGENTS.md`, die vollständige übergebene Scope-/Preservation-Anweisung, das
vollständige Reviewziel, die vollständige Revision-18-Resolution und der
vollständige unabhängige V18-Review wurden selbst gelesen. Die Resolution wurde
nur als Finding-Mapping, nicht als Beweis verwendet. Die unabhängigen Reviews
und Resolutions der Revisionen 15, 16 und 17 wurden für die vollständige Kette
`V18-H1 → V17-H1 → V16-H1 → V15-H1` geprüft. Bereits geschlossene ältere
Verträge wurden auf Preservation geprüft.

Die Prüfung war statisch, unabhängig, adversarial und nicht auf Closure
gerichtet. Sie modellierte alle zwölf finalen Endpunkte der sechs gerichteten
AF_UNIX-SEQPACKET-Verbindungen, sichtbare und nur kernel-in-flight gehaltene
Referenzen, SCM_RIGHTS, `pidfd_getfd`, Optionsmutation, Queueing,
Guard-/Map-/Link-Lifetime und die vollständige Ordnung
`OPEN → BOOTSTRAP → RELEASED`. Zusätzlich wurde die weitergeltende
Seccomp-Listener-Ownership und deren Bootstrap-Transfer end-to-end in die neue
globale Sendesperre eingesetzt.

Primäre Autorität war ausschließlich Linux `v6.18`:

- [`kernel/bpf/bpf_lsm.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/kernel/bpf/bpf_lsm.c),
  Zeilen 17–31, 33–49, 109–132, 222–283 und 298–396, für Erzeugung und
  Verifier-Allowlist der BPF-LSM-Hooks, Disabled-/Sleepable-Sets sowie
  `sk_storage_get/delete` und den Tracing-Helper-Fallback;
- [`include/linux/lsm_hook_defs.h`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/include/linux/lsm_hook_defs.h),
  Zeilen 209, 321–326, 334 und 341, für die exakten Signaturen von
  `file_receive`, `unix_stream_connect`, `socket_post_create`,
  `socket_sendmsg` und `socket_setsockopt`;
- [`net/socket.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/net/socket.c),
  Zeilen 504–516, 737–742, 1590–1632, 1742–1756 und 2327–2359, für
  FD-Installation, `socket_post_create` vor FD-Sichtbarkeit,
  `socket_sendmsg` vor Protokollübergabe und `socket_setsockopt` vor
  Cgroup-/Protokollmutation;
- [`net/unix/af_unix.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/net/unix/af_unix.c),
  Zeilen 1555–1728 und 1759–1801, für Erzeugung von `newsk`, den
  `security_unix_stream_connect(sk,other,newsk)`-Hook vor Einreihung des
  Accept-SKB und vor `accept`-Graft/FD;
- [`net/core/filter.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/net/core/filter.c)
  und [`kernel/trace/bpf_trace.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/kernel/trace/bpf_trace.c),
  insbesondere `bpf_sock_from_file_proto` und
  `BPF_FUNC_sock_from_file`/`BPF_FUNC_sk_storage_get`, für die
  `file_receive(file) → socket → sock-storage`-Prüfung;
- [`net/core/scm.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/net/core/scm.c),
  Zeilen 356–406 und 503–548, sowie
  [`include/net/scm.h`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/include/net/scm.h),
  Zeilen 110–116, für `SCM_RIGHTS → scm_recv_one_fd → receive_fd`;
- [`fs/file.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/fs/file.c),
  Zeilen 1343–1397, für `security_file_receive(file)` vor
  FD-Allokation, Usercopy und `fd_install`;
- [`kernel/pid.c`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/kernel/pid.c),
  Zeilen 816–834, für `pidfd_getfd → receive_fd(file,NULL,O_CLOEXEC)`;
- [`include/uapi/linux/bpf.h`](https://raw.githubusercontent.com/torvalds/linux/refs/tags/v6.18/include/uapi/linux/bpf.h),
  Zeilen 172–220, 930–935 und 1369–1375, für die Map-Update-UAPI, Pin-/
  Referenz-Lifetime und die tatsächlich verfügbaren Update-Flags.

Der Review-Host läuft mit Linux/WSL `6.18.33.2-microsoft-standard-WSL2` und
besitzt `/sys/kernel/btf/vmlinux`; die lokale Konfiguration enthält
`CONFIG_BPF_SYSCALL=y`, `CONFIG_BPF_LSM=y`, `CONFIG_CGROUP_BPF=y` und
`CONFIG_SECURITY_NETWORK=y`. Die aktive Ziel-LSM-Liste war lokal nicht als
produktiver Capability-PASS belegbar. Diese Beobachtung ersetzt daher nicht
den von der Spezifikation verlangten Zielsystem-Fingerprint.

Es wurden keine Runtime-, R3-, State-, Workstation-, Scheduler-, Exchange-,
Live-, Research- oder Git-Mutationen und keine Tests mit Writes ausgeführt.
Es gab kein Stage, Commit, Fetch oder Push. `scripts/state_research` blieb
geschlossen. `scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch
ausgeführt oder verändert. Fremde untracked Artefakte, die Spezifikation und
alle früheren Records blieben unangetastet. Einzige Mutation ist dieser
Review-Record.

---

## 2. Urteil und Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| `V19-H1` | HIGH | OPEN | Die globale BOOTSTRAP-Sperre verweigert jedem Session-Cgroup-Task ausnahmslos jeden `sendmsg`/`sendmmsg`, während der weiterhin bindende Trip-Vertrag den vom Trading-Leader erzeugten Seccomp-Listener-FD erst danach über einen Bootstrap-Transferkanal an den Broker übergeben muss. Kein ausführbarer alternativer Ownership-/Inheritance-/`pidfd_getfd`-Pfad und keine sicher verengte Ausnahme ist spezifiziert. |
| `V19-H2` | HIGH | OPEN | Die Freigabe verlangt eine exakte monotone Compare-and-Exchange `BOOTSTRAP→RELEASED` über den einzigen schreibbaren Map-FD, bindet aber weder Maplayout noch eine reale Kernel-/UAPI-Primitive. `BPF_MAP_UPDATE_ELEM` bietet Existenzbedingungen, keine expected-old-Value-CAS; Lookup plus Update wäre nicht die behauptete atomare Transition. |

```text
BLOCKER: 0
HIGH: 2
MEDIUM: 0
LOW: 0

SPECIFICATION_RESULT: REVISION_19_REVIEWED
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Revision 19 enthält einen technisch tragfähigen socketlokalen BPF-LSM-Ansatz
gegen `V18-H1`. Die zugrunde gelegten Hooks und Kernelreihenfolgen existieren.
Der neue Kontrollpfad ist als Gesamtablauf jedoch nicht ausführbar und seine
Release-Linearisierung nicht reproduzierbar spezifiziert. Deshalb darf weder
`V18-H1` noch die davon abhängige Kette geschlossen werden.

---

## 3. Positiver Kernelbefund / No-Findings

### 3.1 BPF-LSM-Attachbarkeit und Helper

Linux v6.18 erzeugt in `kernel/bpf/bpf_lsm.c:17–31` für alle nicht
ausgeschlossenen Definitionen aus `lsm_hook_defs.h` attachbare
`bpf_lsm_<hook>`-Ziele. Keiner der fünf V19-Hooks steht im Disabled-Set
(`bpf_lsm.c:33–49`). Die exakten Hooks existieren in
`lsm_hook_defs.h:209,321–326,334,341`.

`bpf_lsm_func_proto()` erlaubt LSM-Programmen
`BPF_FUNC_sk_storage_get/delete` (`bpf_lsm.c:222–243`) und fällt für weitere
Tracing-Helper auf `tracing_prog_func_proto()` zurück
(`bpf_lsm.c:278–282`). Dort sind `BPF_FUNC_sock_from_file` und die
Tracing-SK-Storage-Protos gebunden (`bpf_trace.c:1711–1717`). Damit kann
`file_receive(struct file *)` ein Socket-File in `struct socket *` umsetzen,
dessen `sock->sk` prüfen und die sock-lokale Storage lesen. Für
`socket_post_create`, `unix_stream_connect`, `socket_setsockopt` und
`socket_sendmsg` liefern die Hookargumente den benötigten `struct socket *`
beziehungsweise `struct sock *` direkt. Kein Finding zur behaupteten
grundsätzlichen Attach-/Helper-Verfügbarkeit.

### 3.2 Tagging vor Userspace-FD-Sichtbarkeit

`__sock_create()` ruft nach dem Protokoll-Create
`security_socket_post_create()` auf und gibt erst danach das Socket zurück
(`net/socket.c:1590–1632`). `__sys_socket()` ruft `sock_map_fd()` erst danach
auf (`1742–1756`); `sock_map_fd()` installiert den FD erst in Zeile 515.

Für die akzeptierte AF_UNIX-Stream-/SEQPACKET-Seite erzeugt
`unix_stream_connect()` `newsk` in `af_unix.c:1587–1592`, ruft den Hook mit
diesem `newsk` in `1657–1661` auf und reiht das Accept-SKB erst in
`1710–1715` ein. `unix_accept()` graftet `newsk` erst in `1759–1801` auf das
Userspace-Socket. Die V19-Annahme, das serverseitige `newsk` vor
Userspace-FD-Sichtbarkeit zu taggen, ist damit bestätigt. Kein Finding.

### 3.3 `socket_setsockopt`-Linearisierung

`do_sock_setsockopt()` ruft in `net/socket.c:2337–2339` zuerst
`security_socket_setsockopt(sock,level,optname)` auf. Erst danach folgen das
Cgroup-Sockopt-Programm (`2341–2346`) und der SOL_SOCKET-/Protokollpfad
(`2352–2359`). Der LSM-Hook erfasst damit auch einen nach FD-Lookup nur noch
kernel-in-flight gehaltenen Caller vor Optionsmutation. Die V19-Auflösung von
V18s lokalem Set/Get-/Snapshot-Race ist an dieser einzelnen Grenze technisch
plausibel. Kein Finding zu Hook-Reihenfolge oder den zwölf
`INIT→SEALED`-Endpunktgrenzen.

### 3.4 `file_receive` für SCM_RIGHTS und `pidfd_getfd`

Beim SCM_RIGHTS-Empfang ruft `scm_detach_fds()` für jedes File
`scm_recv_one_fd()` (`net/core/scm.c:356–378`), das unmittelbar
`receive_fd()` aufruft (`include/net/scm.h:110–116`). `receive_fd()` ruft
`security_file_receive(file)` vor `get_unused_fd_flags`, Usercopy und
`fd_install` auf (`fs/file.c:1358–1381`). `pidfd_getfd()` führt ebenfalls
`receive_fd(file,NULL,O_CLOEXEC)` aus (`kernel/pid.c:816–834`). Damit liegt
`file_receive` auf beiden verlangten Akquisitionspfaden vor neuer
Userspace-FD-Sichtbarkeit. Kein Finding.

### 3.5 Bootstrap-Send-Gate vor Queueing

`__sock_sendmsg()` ruft `security_socket_sendmsg()` vor
`sock_sendmsg_nosec()` und damit vor der Protokollimplementierung auf
(`net/socket.c:737–742`). Ein `-EPERM` aus dem LSM-Hook erreicht weder AF_UNIX-
SCM-Verarbeitung noch Queueing. Die behauptete technische Position des Gates
ist korrekt. Finding `V19-H1` betrifft nicht die Hookposition, sondern die
fehlende Ausnahme-/Ownership-Ordnung für einen weiterhin zwingenden
Bootstrap-Transfer.

### 3.6 Pin-, Link-, Map- und Sock-Storage-Lifetime

Die BPF-UAPI erklärt, dass ein Objekt erst nach Schließen aller FDs und
Wegfall aller gepinnten oder attachten Referenzen deallokiert wird
(`include/uapi/linux/bpf.h:930–935`). Gepinnte Links/Programme/Maps können den
Guard deshalb über den Loader-FD hinaus tragen; SK-Storage folgt dem
`struct sock` bis zu Socket-/Map-Zerstörung. Unter den ausdrücklich
ausgeschlossenen privilegierten Co-Tenants und den verweigerten bpffs-/BPF-
Rechten der Rollen wurde kein zusätzlicher Lifetime-Bypass gefunden. Cleanup
muss Pins/Links erst nach bewiesener Endpoint-Zerstörung entfernen, wie V19
bereits fordert.

---

## 4. Finding `V19-H1` — Absolute BOOTSTRAP-Sendsperre kollidiert mit dem zwingenden Listener-FD-Transfer

**Normative Evidenz:**

- Zeilen 1130–1147 verlangen weiterhin: Der Trading-Leader installiert den
  Seccomp-Filter mit `NEW_LISTENER|WAIT_KILLABLE_RECV`, übergibt den einmalig
  erzeugten Listener-FD über den nur im Bootstrap vorhandenen Transferkanal an
  den Broker, schließt seine Kopie und erst dann darf nur der Broker den
  Listener halten. `CONTINUE` und `NOTIF_ADDFD` sind verboten.
- Zeilen 1496–1507 hängen den globalen LSM-Guard vor jeder Rolle und jedem
  Socket an.
- Zeilen 1509–1520 binden die Session-Cgroup und die Bootstrap-TIDs.
- Zeilen 1522–1532 verweigern im Zustand `BOOTSTRAP` **jeden**
  `sendmsg`-/`sendmmsg`-Pfad **jedes** Session-Cgroup-Tasks, unabhängig von FD,
  Ziel, Message, Controlbuffer und TID; diese Grenze gilt vor den
  Rollen-Seccomp-Filtern.
- Zeilen 2247–2260 verlangen nochmals, dass `BOOTSTRAP` vor Rollen/Sockets
  hergestellt und bis nach durablem OPEN beibehalten wird.
- Zeilen 2967–2971 bestätigen den Broker als alleinigen Besitzer des
  Seccomp-Notification-Listeners.
- Zeilen 4057–4065 und 4093–4105 wiederholen die globale Sperre und die
  einmalige nachgelagerte Freigabe in Completion.

**Ausführungskonflikt:**

1. Der Listener-FD entsteht nach Installation des Trading-Filters im
   Trading-Leader; er kann daher nicht bereits als Broker-Eigentum attestiert
   sein.
2. Der Vertrag verlangt eine Übergabe und anschließend das Schließen der
   Leader-Kopie. Ein „Transferkanal“ für einen Linux-FD benötigt einen
   spezifizierten Kernelpfad: typischerweise SCM_RIGHTS/`sendmsg`, alternativ
   einen ausdrücklich geordneten Inheritance- oder `pidfd_getfd`-Pfad.
3. Befindet sich der Trading-Leader wie für die Session vorgesehen in der
   Session-Cgroup, beendet der globale `socket_sendmsg`-Hook einen
   SCM_RIGHTS-Transfer bereits vor der Protokollübergabe mit `-EPERM`.
4. V19 spezifiziert weder einen Listener-FD-spezifischen, vor dem Runtime-
   Endpoint-Queueing sicher unterscheidbaren Sendpfad noch Broker-Inheritance,
   einen vor Cgroup-Eintritt abgeschlossenen Ownership-Transfer oder einen
   `pidfd_getfd`-Ablauf mit den notwendigen Ptrace-/Seccomp-/Lifetime-Grenzen.
5. Eine pauschale `sendmsg`-Ausnahme würde die gerade geschlossene V18-H1-
   Grenze wieder öffnen: Derselbe Bootstrap-Caller könnte Runtime-Endpunkte in
   einer fremden Queue parken. Eine sichere Ausnahme muss deshalb an eine
   kernelprüfbare Listener-File-Identität, exakte Peers, genau einmalige
   Ownership-Transition und Reihenfolge vor Runtime-Socket-Erzeugung gebunden
   sein.

Das Verhalten ist fail-closed, erzeugt also keinen unmittelbar freigegebenen
unsicheren Runtime-Pfad. Der spezifizierte Startup kann aber seine zwingende
Broker-Listener-Invariante nicht erreichen. Eine Implementierung müsste den
Vertrag erfinden oder die globale Sperre aufweichen. Das ist ein offenes
`HIGH` und verhindert Closure.

**Erforderliche Resolution:**

Revision 20 muss einen einzigen reproduzierbaren Pfad normieren. Bevorzugt
wird eine vor Session-Cgroup-`BOOTSTRAP` und vor jedem Runtime-Socket
abgeschlossene, genau einmalige Listener-Ownership-Transition mit exakten
PID/TID/Startzeit-/File-Identitäten; alternativ ist eine LSM-Ausnahme nur dann
zulässig, wenn sie kernel-seitig ausschließlich den gebundenen Seccomp-
Listener-FD, den gebundenen Trading→Broker-Peer, leeren Datenanteil, exakt ein
SCM_RIGHTS-File, eine Nonce und genau einen erfolgreichen Transfer akzeptiert.
Nach dem Transfer muss jede weitere Ausnahme irreversibel geschlossen und die
Leader-Kopie bewiesen geschlossen sein. Der End-to-end-Fault-/Capability-Test
muss Wiederholung, falsches File, zusätzliche FDs, falschen Peer, abweichende
Controlbytes, Stop/Crash und Transfer vor/nach der erlaubten Phase injizieren.

---

## 5. Finding `V19-H2` — `BOOTSTRAP→RELEASED`-CAS ist an keine reale BPF-Map-Primitive gebunden

**Normative Evidenz:**

- Zeilen 1496–1503 führen eine unspezifizierte Session-State-Map ein.
- Zeilen 1593–1600 verlangen, dass der Guard für den Snapshot den exakten
  Session-State `BOOTSTRAP` attestiert.
- Zeilen 1612–1626 verlangen nach durablem OPEN über den einzigen
  schreibbaren Map-FD genau eine monotone Compare-and-Exchange
  `BOOTSTRAP→RELEASED` auf der exakten Session-Nonce und danach das Schließen
  dieses FDs. Zweites Release, Rücktransition oder Map-Mutation sollen
  terminal sein.
- Zeilen 2258–2263 und 4064–4066 machen exakt diese Transition zur einzigen
  Senderfreigabe.
- Zeilen 2083–2086 verlangen im Test `BOOTSTRAP` bis durable OPEN und danach
  einen genau einmaligen Release, nennen aber ebenfalls keine ausführbare
  Primitive.

**Reale UAPI-Grenze:**

Linux v6.18 dokumentiert für `BPF_MAP_UPDATE_ELEM` nur `BPF_ANY`,
`BPF_NOEXIST`, `BPF_EXIST` und `BPF_F_LOCK`
(`include/uapi/linux/bpf.h:189–220,1369–1375`). `BPF_NOEXIST` und `BPF_EXIST`
testen ausschließlich die Existenz des Keys, nicht den erwarteten alten Wert.
Ein Map-FD bietet deshalb keine allgemeine Userspace-Operation
„ersetze nur, falls alter Wert exakt BOOTSTRAP ist“.

V19 bindet weder:

- Maptyp, Key-/Value-Größe, Alignment und Byteordnung;
- die Relation zwischen Session-Nonce und Map-Key/-Value;
- einen `BPF_F_MMAPABLE`-Array-Map-Pfad mit definierter atomarer
  Userspace-Instruktion und Memory-Order;
- einen separaten BPF-Hook-/Syscall-Trigger, in dem ein BPF-Programm eine
  echte `cmpxchg` auf dem Map-Value ausführt;
- noch eine andere Kernel-/ioctl-/kfunc-Primitive mit expected-old-Wert,
  Rückgabesemantik und linearer Fehlerklassifikation.

`BPF_MAP_LOOKUP_ELEM` gefolgt von `BPF_MAP_UPDATE_ELEM(BPF_EXIST)` ist kein
Compare-and-Exchange. Zwischen Lookup und Update kann sich der Wert ändern;
auch ohne konkurrierenden berechtigten Writer ist diese Zweischrittfolge nicht
die normative einzelne Kernel-Linearisierung und kann „zweites Release“ oder
„Rückkehr“ nicht auf die behauptete Weise erkennen. Das Schließen des letzten
schreibbaren FDs nachher repariert die fehlende Release-Primitive nicht.

Auch dieses Defizit ist fail-closed, solange eine Implementierung nicht
eigenmächtig eine schwächere Updatefolge verwendet. Es verhindert jedoch die
reproduzierbare Umsetzung und den geforderten exactly-once-Test. Severity ist
`HIGH`.

**Erforderliche Resolution:**

Revision 20 muss Maptyp und vollständiges ABI normieren und eine tatsächlich
verfügbare atomare Primitive binden. Geeignete Varianten sind beispielsweise
eine passend ausgerichtete mmapbare Array-Map mit einer klar gebundenen
Userspace-Atomic-CAS und Acquire/Release-Semantik, sofern Kernel/UAPI und
Architektur dies für genau diesen Maptyp nachweisbar erlauben, oder ein exakt
gebundener Kernel/BPF-Trigger, der die CAS im Programm ausführt und dem Guard
den alten Wert authentisch zurückmeldet. PASS muss getrennt `expected=OPEN`,
`expected=BOOTSTRAP`, doppelten Release, falsche Nonce, Guard-Crash vor/nach
Linearisation, Pin-/FD-Reopen, Linkverlust und alle Rücktransitionen prüfen.

---

## 6. Finding-Kette V18-H1 / V17-H1 / V16-H1 / V15-H1

| Finding | V19-Teilbefund | End-to-end-Status |
|---|---|---|
| `V18-H1` | Socketlokales Tag, globales `socket_setsockopt`-Seal, `file_receive` und BOOTSTRAP-Send-Gate adressieren den kernel-in-flight Fremdhalter technisch. | **NICHT GESCHLOSSEN.** Der notwendige Setup-Kontrollpfad ist wegen `V19-H1` nicht ausführbar und der Release wegen `V19-H2` nicht operational gebunden. |
| `V17-H1` | Post-Filter-Options-/Queue-/FD-/OFD-/Lock-Snapshot und zwölf Seals bleiben erhalten. | **NICHT END-TO-END GESCHLOSSEN.** Seine Closure hängt an einem erreichbaren, monoton freigegebenen V19-Guard. |
| `V16-H1` | Zwei Phasen, fixierte TID-/Files-Table-Topologie und Rights-Freeze-TSYNC bleiben erhalten. | **NICHT END-TO-END GESCHLOSSEN.** Der neue globale Kontrollpfad ist noch nicht ausführbar spezifiziert. |
| `V15-H1` | Alle sechs Kanäle, zwölf Endpunkte, `SO_PASSRIGHTS=0`, Prequeue-EPERM und Cleanup bleiben normativ erhalten. | **NICHT END-TO-END GESCHLOSSEN.** Die Senderfreigabe kann nicht über den behaupteten CAS bewiesen werden. |

Die positive Kernelprüfung reicht nicht für Closure: Ein Security-Mechanismus
muss nicht nur an geeigneten Hooks liegen, sondern sein gesamter
Installations-, Ownership-, Bootstrap-, Release- und Cleanup-Pfad muss ohne
eine neue ungeschriebene Ausnahme ausführbar sein.

---

## 7. Preservation-Prüfung

| Grenze | Ergebnis |
|---|---|
| Sechs gerichtete Runtime-Kanäle / zwölf finale Endpunkte | Bewahrt; V19 Zeilen 1534–1546 und 1558–1578. |
| `SO_PASSRIGHTS=0` als Prequeue-Autorität | Bewahrt; alle zwölf Endpunkte werden versiegelt, alle sechs Empfänger bleiben fachliche Autorität. |
| Fixierte Empfänger-TID-/Files-Table-Topologie und TSYNC-Rights-Freeze | Bewahrt; Zeilen 1548–1587. |
| Post-filter `getsockopt==0`, `scm_fds:0`, leere Queue, FD/OFD/Lock-Snapshot | Bewahrt; Zeilen 1589–1600. |
| Totalabbruch, Endpoint-/Queue-Zerstörung, keine Same-Session-Retry | Bewahrt; Zeilen 1602–1610 und 1901–1940. |
| V15-Signal-Envelope / `WAIT_KILLABLE_RECV` / Listener-Single-Owner | Inhaltlich bewahrt; gerade seine Listener-Übergabe deckt `V19-H1` auf. |
| V14-B1 monotones Broker-Control-Word und Renewal-/Close-Autorität | Keine Regression gefunden. |
| V14-B2 vollständige Nachrichten-/Rollenmatrix | Keine Regression gefunden. |
| V14-H1 endliche Close-FSM | Keine Regression gefunden. |
| V13-B2 ausschließlich PREPARE→CLOSED→durable COMMIT als clean | Keine Regression gefunden. |
| V12/V11 keine Pipe-Daten-/Referenzbildung im Terminalpfad | Keine Regression gefunden. |
| V10 Topologie-/Writer-Single-Ownership | Keine Regression gefunden. |
| Single-Owner-, Decimal-, Execution-Economics-, Restart-/Recovery- und Versionsgrenzen | Keine Regression gefunden. |
| Implementierungs-/ENFORCED-/Exchange-/Live-Sperre | Bewahrt; V19 Zeilen 4137–4161. |

Es wurde kein zusätzlicher sicherheitskritischer Bypass in den zwölf
Endpoint-Seals, in `file_receive`, in der `SO_PASSRIGHTS`-Prequeue-Semantik
oder in der Pin-/Link-Lifetime gefunden. Diese No-Findings heben `V19-H1` und
`V19-H2` nicht auf.

---

## 8. Identitäts- und Scope-Abschluss

Die fail-closed Eingangsidentitäten wurden vor inhaltlicher Wertung bestätigt:

```text
REPOSITORY_ROOT=/home/benja/projects/sniper-bot
HEAD=c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN=c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN=89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
ORIGIN_MAIN_DOTDOT_MAIN=0 6

SPEC_V19_LINES=4161
SPEC_V19_SHA256=191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b

V18_RESOLUTION_LINES=486
V18_RESOLUTION_SHA256=6134a0e039b00281f6b5b97f3780af06d1ff6c348f4ef4fa1cb917345b481af9

V18_INDEPENDENT_REVIEW_LINES=482
V18_INDEPENDENT_REVIEW_SHA256=8efb96b2e48c7ab3090e9aba7b2e71bcb421fdeabb269fc937970344e29fa427
```

Kettenidentitäten:

```text
V17_REVIEW_SHA256=b976df15ac62ef642ce5d1e6bca88bd8ad8c4ef3595c94aa931dd31ea8ce33d8
V17_REVIEW_LINES=361
V17_RESOLUTION_SHA256=5b56d248174ae96c8dbdcdaafce611acb2d18a5e7ae24a49a1fe8ffb0953fce2
V17_RESOLUTION_LINES=363
V16_REVIEW_SHA256=85068c49739e5016ff9ec0a614e3dcdac97a352594cc3839cf7ce8414e5f80df
V16_REVIEW_LINES=330
V16_RESOLUTION_SHA256=25a94fb235e172a9c298abd2d07f8d1f635260e01b1a6c99e070f0facf9ce041
V16_RESOLUTION_LINES=321
V15_REVIEW_SHA256=8276a4eba8f89b7f929ccd29211d631b57a46862684542a8db5fe7baef65c477
V15_REVIEW_LINES=282
V15_RESOLUTION_SHA256=d4377470cb3298619a312267feba8bbe3a22a1bd702567b97d788fc22a075879
V15_RESOLUTION_LINES=342
```

Die vorbestehende untracked Menge wurde nicht bereinigt oder verändert. Der
abschließende Status darf gegenüber dem Eingang ausschließlich diesen neuen
Review-Record zusätzlich zeigen. Hash und Zeilenzahl des Records werden nach
der Erstellung extern gemessen und in der Übergabe berichtet; ein Dokument
kann seinen eigenen finalen Hash nicht zirkelfrei enthalten.

---

## 9. Ausdrücklicher nächster Schritt

Der nächste zulässige Schritt ist **nicht** Implementierung, R3, Runtime,
Workstation oder ENFORCED-Aktivierung. Er ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-19-REREVIEW-RESOLUTION`

Diese Resolution muss `V19-H1` und `V19-H2` vollständig auf eine neue
Spezifikationsrevision abbilden: einen ausführbaren, genau einmaligen
Seccomp-Listener-Ownership-Transfer unter dem Bootstrap-Send-Gate und eine
konkret an Linux-UAPI/Maplayout/Memory-Order gebundene atomare
`BOOTSTRAP→RELEASED`-Transition. Danach ist ein neues unabhängiges read-only
Re-Review des vollständigen neuen Spezifikationshashes erforderlich.

