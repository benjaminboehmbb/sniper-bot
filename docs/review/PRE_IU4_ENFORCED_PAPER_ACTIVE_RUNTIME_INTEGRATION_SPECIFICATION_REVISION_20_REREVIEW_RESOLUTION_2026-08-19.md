# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-20 REREVIEW RESOLUTION

- **Datum:** 2026-08-19
- **Status:** REVISION-20 REREVIEW FINDING MAPPED — REVISION 21 REQUIRED — NEW INDEPENDENT REREVIEW REQUIRED
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand / HEAD / main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **main gegenüber origin/main:** `0 behind / 6 ahead`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V20-Hash:** `18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0`
- **Unabhängig geprüfte V20-Zeilen:** `4409`
- **Revision-20-Independent-Rereview-Record:** `c40e5af0fb499d8611097409946bd38f2b813ab10a0b0425e9071c4712868338`
- **Revision-20-Independent-Rereview-Zeilen:** `401`
- **Controlling Revision-19-Resolution:** `edc0ca72c21bec1104cccd98c32bd37bb106bb708df9fd2893da31b951792fa0`
- **Controlling Revision-19-Resolution-Zeilen:** `561`
- **Geforderte Folgerevision:** `21`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument löst das einzige offene HIGH-Finding `V20-H1` des
unabhängigen read-only Re-Reviews der Revision 20 in verbindliche
Korrekturanforderungen für Revision 21 auf.

`V20-H1` bestreitet weder die reale Linux-BPF-CMPXCHG noch die
`pidfd_getfd`-/`file_receive`- oder `socket_shutdown`-Mechanik. Der Mangel
liegt in der Autorisierung der beiden Freigabeübergänge. Revision 20 prüft
beim richtigen Guard-Aufruf Altwert, Guard-TID, Control-Socket und `how`, aber
nicht, ob Listener-Revocation beziehungsweise durable OPEN bereits wirklich
bestätigt wurden. Deshalb ist derselbe Guard-Aufruf vor und nach der
Sachvoraussetzung kerneltechnisch ununterscheidbar.

Die Resolution behält die starke fail-closed Grenze bei. Revision 21 darf den
Befund weder durch eine weitere textuelle Sollreihenfolge noch durch einen
Userspace-Boolean, einen nachgelagerten Snapshot oder die bloße Einstufung des
Guards als fehlerfrei schließen. Stattdessen muss sie zwei monotone Grants
einführen, die von voneinander getrennten, gebundenen Autoritäten ausgestellt
werden und die der Guard nicht selbst erzeugen kann. Der Guard darf den
jeweiligen Phasenübergang erst aus dem bereits kernelgebundenen Grant-State
atomar konsumieren.

Dieses Resolution-Protokoll ändert die Spezifikation nicht und zertifiziert
Revision 21 nicht vorab. Sein Status lautet
`MAPPED_FOR_REVISION_21_PENDING_SPECIFICATION_AND_INDEPENDENT_REREVIEW`.
Erst eine neue eindeutig versionierte Spezifikation und danach ein
unabhängiges read-only Re-Review ihres vollständigen Hashes dürfen `V20-H1`
und die abhängige Finding-Kette schließen oder READY erklären.

Weder Runtime-Code noch Workstation-R3, Runtime State, reale Research-Inputs,
Profile, Scheduler, Exchange oder Live wurden verändert. Es wurden keine
Runtime-Tests, Workstation-Läufe, Retries, Git-Stage-, Commit-, Fetch- oder
Push-Operationen ausgeführt. `scripts/state_research` blieb geschlossen;
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch verändert oder
ausgeführt. Vorhandene untracked Benutzerartefakte wurden nicht bereinigt,
überschrieben oder gestaged.

---

## 2. Ausgang des unabhängigen V20-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V20_SHA256: 18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0
SPEC_V20_LINES: 4409
REVISION_19_RESOLUTION_SHA256: edc0ca72c21bec1104cccd98c32bd37bb106bb708df9fd2893da31b951792fa0
REVISION_20_REREVIEW_SHA256: c40e5af0fb499d8611097409946bd38f2b813ab10a0b0425e9071c4712868338
REREVIEW_RESULT: NOT_READY
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

| Finding | V20-Re-Review | Verbindliche Resolution für V21 |
|---|---|---|
| `V20-H1` | `LISTENER_RECEIVED→BOOTSTRAP` und `BOOTSTRAP→RELEASED` sind atomar, aber der `socket_shutdown`-Hook kann vollständige Handoff-Revocation beziehungsweise durable OPEN nicht von einem verfrühten korrekten Guard-Aufruf unterscheiden. | Zwei getrennte, nicht vom Guard ausstellbare Kernel-Grants erweitern die Phase-FSM. Eine gebundene Revocation-Attestor-Autorität erzeugt `HANDOFF_REVOKED_GRANTED`; ausschließlich der Persistence Owner erzeugt `OPEN_DURABLE_GRANTED` aus der erfolgreichen Durable-Commit-Fortsetzung. Der Guard kann nur diese bereits vorhandenen Grant-States per eigener CMPXCHG konsumieren. Ohne Grant scheitert derselbe korrekte Guard-Aufruf vor jeder Phase-Mutation. |

Der V20-Review bestätigte zugleich:

- der Listener-Handoff über `pidfd_getfd` benötigt keine `sendmsg`-Ausnahme;
- `file_receive` liegt vor neuer FD-Installation;
- eine eingefrorene Array-Map bleibt durch bereits geladene BPF-Programme
  atomar beschreibbar, obwohl Userspace sie nicht mehr mutieren kann;
- `socket_shutdown` entscheidet vor dem Protokollpfad und kann bei
  erfolgreicher Transition absichtlich `-EINPROGRESS` zurückgeben;
- die mechanischen V19-H1- und V19-H2-Probleme sind in Revision 20 gelöst.

Diese positiven Befunde sind in Revision 21 unverändert zu bewahren.

---

## 3. Resolution von V20-H1

### 3.1 Sechsstufige monotone Phase-FSM

Revision 21 muss `TerminalRuntimeSocketGuardPhaseV2` durch eine eindeutig neue
Version ersetzen. Der normative Map-Value bleibt ein einzelnes, ausgerichtetes
`u64` in einer vor Rollenstart für Userspace eingefrorenen
`BPF_MAP_TYPE_ARRAY`, besitzt aber exakt diese sechs Zustände:

```text
LISTENER_HANDOFF          = 0
LISTENER_RECEIVED         = 1
HANDOFF_REVOKED_GRANTED   = 2
BOOTSTRAP                 = 3
OPEN_DURABLE_GRANTED      = 4
RELEASED                  = 5
```

Andere Werte sind terminal ungültig. Rücktransitionen, Überspringen eines
Zustands, Wiederholung oder mehrfeldrige Publikation sind verboten. Ab
Rollenstart existiert weiterhin kein Userspace-writable Map-FD. Alle fünf
Transitionen sind programmseitige
`BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`-Operationen auf genau diesem Wort:

| Nr. | Autorität und Trigger | Erwarteter Altwert | Zielwert |
|---:|---|---:|---:|
| 1 | Broker-`file_receive` des exakt gebundenen Seccomp-Listeners | `LISTENER_HANDOFF=0` | `LISTENER_RECEIVED=1` |
| 2 | Revocation Attestor auf seinem gebundenen Grant-Control-Socket mit `SHUT_WR` | `LISTENER_RECEIVED=1` | `HANDOFF_REVOKED_GRANTED=2` |
| 3 | Guard auf dem Phase-Control-Socket mit `SHUT_RD` | `HANDOFF_REVOKED_GRANTED=2` | `BOOTSTRAP=3` |
| 4 | Persistence Owner auf seinem gebundenen Grant-Control-Socket mit `SHUT_WR` | `BOOTSTRAP=3` | `OPEN_DURABLE_GRANTED=4` |
| 5 | Guard auf dem Phase-Control-Socket mit `SHUT_RDWR` | `OPEN_DURABLE_GRANTED=4` | `RELEASED=5` |

Transition 3 kann damit selbst bei vollständig richtigem Guard-TID, Socket
und `SHUT_RD` nicht vor Transition 2 gewinnen. Transition 5 kann mit demselben
richtigen Guard und `SHUT_RDWR` nicht vor Transition 4 gewinnen. Falscher
Altwert muss ohne Mapmutation `-EALREADY` oder `-EPERM` liefern. Nur eine
erfolgreiche CMPXCHG liefert `-EINPROGRESS`; der Socket-Protokollpfad wird nie
ausgeführt.

### 3.2 Getrennte Grant-Autoritäten

Revision 21 muss drei disjunkte, nicht transferierbare Control-Sockets und
ihre Autoritäten binden:

1. `PHASE_CONTROL` gehört ausschließlich dem single-threaded Guard und darf
   nur die Transitionen 3 und 5 anfordern.
2. `HANDOFF_REVOCATION_GRANT_CONTROL` gehört ausschließlich einem separaten,
   single-threaded `TerminalHandoffRevocationAttestorV1`. Nur sein gebundener
   TGID/TID/Startzeit/Cgroup-Kontext darf Transition 2 anfordern.
3. `OPEN_DURABILITY_GRANT_CONTROL` gehört ausschließlich dem bereits
   autoritativen Persistence Owner. Nur sein gebundener Writer-TID im
   erfolgreichen Durable-Commit-Continuation-Pfad darf Transition 4
   anfordern.

Die vor Rollenstart eingefrorene Konfigurations-Map bindet für alle drei
Sockets jeweils Socket-Cookie, Typ, Owner-TGID/TID/Startzeit, Cgroup-ID,
Session-Nonce und erlaubtes `how`. Der `socket_post_create`-Hook versieht sie
mit drei disjunkten sk-storage-Tags. `file_receive`, `pidfd_getfd`,
`SCM_RIGHTS`, `/proc/<pid>/fd`, `dup*`, `fork`-/Files-Table-Weitergabe und
abweichende Inheritance dürfen keinen zweiten Halter erzeugen. Vor dem Freeze
muss die Bootstrap-Inheritance total geordnet und jeder Nicht-Owner-Halter
geschlossen und extern inventarisiert sein.

Der Hook entscheidet immer anhand von Phase, exaktem Socket-Tag/-Cookie,
exakter Ausstelleridentität, Session/Cgroup und `how`. Ein Guard-Aufruf auf
einem Grant-Socket, ein Grant-Aussteller auf `PHASE_CONTROL`, vertauschte
Sockets oder gleiche skalare Werte bei falscher Autorität liefern `-EPERM`
ohne Mutation.

### 3.3 `HANDOFF_REVOKED_GRANTED`

Der Revocation Attestor ist nicht der Guard und besitzt keine
Phase-Control-Autorität. Er darf Transition 2 ausschließlich aus einer
ununterbrochenen erfolgreichen Evidence-Fortsetzung anfordern, nachdem alle
folgenden Prädikate gebunden und positiv geprüft wurden:

1. der Broker hat den Listener am reservierten Ziel-FD empfangen und Inode,
   Anon-Inode-Typ, Filterhash, Session-Nonce und Ready-Nonce bestätigt;
2. das passende Eventfd-ACK wurde genau einmal verbraucht;
3. der Trading-Quell-FD ist geschlossen und extern abwesend;
4. Trading hat `PR_SET_PTRACER=0` und `PR_SET_DUMPABLE=0`, Broker hat
   `PR_SET_DUMPABLE=0`;
5. beide besitzen leere Capability-Sets, `no_new_privs` und ihre finalen
   Bootstrap-Filter;
6. `pidfd_getfd`, Ptrace-/Dumpable-Lockerung, Listener-Erzeugung,
   FD-Duplikation und FD-Transfer sind irreversibel gesperrt;
7. die Halterinventur zeigt genau den Broker-Ziel-FD und keinen weiteren
   Listener-Halter;
8. Guard-Links, Phase-/Config-Map und alle gebundenen Identitäten sind
   unverändert aktiv.

Der Attestor-Grant bedeutet ausschließlich: Diese Evidence wurde von der
separaten, hash- und TID-gebundenen Attestor-TCB erfolgreich abgeschlossen.
Die Spezifikation darf nicht behaupten, der BPF-Hook selbst habe
`/proc`-Inventur, Ptrace-Zustände oder Userspace-Evidence kryptographisch
rekonstruiert. Kernel-enforced ist die Trennung: Der Guard kann den Grant
nicht selbst erzeugen und ohne den Grant die BOOTSTRAP-CMPXCHG nicht gewinnen.

Nach erfolgreicher Transition 2 bleiben Runtime-Socket-Erzeugung und jeder
Session-Send weiterhin gesperrt. Erst Transition 3 öffnet ausschließlich die
Runtime-Socket-Provisionierung; der Send-Gate bleibt geschlossen.

### 3.4 `OPEN_DURABLE_GRANTED`

Der Durability Grant darf ausschließlich durch den Persistence Owner erzeugt
werden, der bereits das kanonische `RUNTIME_SESSION_OPEN` schreibt. Er ist
disjunkt vom Guard und besitzt keine Phase-Control-Autorität. Transition 4
darf nur aus derselben ununterbrochenen erfolgreichen Commit-Fortsetzung
erfolgen, nachdem:

1. alle zwölf Endpunkte `SEALED` sind und `SO_PASSRIGHTS=0` nach finaler
   Filterabdeckung erneut bestätigt wurde;
2. TID-/Files-Table-, TSYNC-, Rollenfilter-, Queue-, `scm_fds`-, FD-/FDINFO-,
   OFD- und Lock-Snapshots vollständig PASS sind;
3. Guard-/Tag-/Map-/Link-/Program-/Endpoint-Identitäten unverändert sind;
4. Resource Reserve und alle Startup-Prädikate PASS sind;
5. `RUNTIME_SESSION_OPEN` mit dem vollständigen Fingerprint geschrieben,
   dateispezifisch synchronisiert, das Parent Directory bei Erzeugung/Rename
   synchronisiert und anschließend read-only byte-/hashgleich zurückgelesen
   wurde;
6. Ledger Tip, Authority Commit Anchor, Session-Nonce, Startup Attempt und
   Writer-Fencing unmittelbar danach erneut aktuell gebunden sind;
7. kein Fehler, Signalreturn, Callback, Eventloop-Turn oder anderer
   Operationspfad zwischen dem letzten erfolgreichen Durability-/Readback-
   Ergebnis und dem Grant-Trigger liegt.

Der `OPEN_DURABLE_GRANTED`-State ist die kernelgebundene Aussage des
getrennten Persistence-Owner-TCB, dass genau dieser Commit erfolgreich war.
Die Spezifikation muss ausdrücklich festhalten, dass der BPF-Hook keine
Filesystem-Durability aus Userspace-Payloads ableitet. Kernel-enforced sind
Ausstellertrennung, exakte Identität, Zustand, Einmaligkeit und die
Unmöglichkeit des Guards, den Grant selbst zu erzeugen.

Nach Transition 4 bleibt `socket_sendmsg` für die gesamte Session weiterhin
gesperrt. Erst der Guard konsumiert den bereits vorhandenen Grant durch
Transition 5. Ein OPEN ohne Transition 4 oder ein Grant ohne Transition 5
bleibt unclosed und darf keinen fachlichen Send ausführen.

### 3.5 Socket- und Send-Gates

Revision 21 muss die Gate-Matrix exakt an die neue FSM anpassen:

| Phase | Runtime-Socket-Erzeugung | Session-`sendmsg`/`sendmmsg` | Zulässige nächste Autorität |
|---|---|---|---|
| `LISTENER_HANDOFF` | verweigert | verweigert | Broker-`file_receive` |
| `LISTENER_RECEIVED` | verweigert | verweigert | Revocation Attestor |
| `HANDOFF_REVOKED_GRANTED` | verweigert | verweigert | Guard `SHUT_RD` |
| `BOOTSTRAP` | ausschließlich geschützte Provisionierung | verweigert | Persistence Owner nach durable OPEN |
| `OPEN_DURABLE_GRANTED` | keine neue abweichende Provisionierung | verweigert | Guard `SHUT_RDWR` |
| `RELEASED` | nur bestehende versiegelte Endpunkte | ausschließlich sechs skalar erlaubte Pfade | keine weitere Transition |

Kein anderer Syscall, Map-Writer, Trigger, Retry oder Recoverypfad darf eine
Phase überspringen oder dieselbe Gatewirkung herstellen.

---

## 4. Explizite Vertrauens- und Schutzgrenze

Revision 21 muss ihre TCB ehrlich und vollständig benennen:

- Der BPF-LSM-Guard erzwingt Zustand, Identität, Socketbindung, Einmaligkeit,
  monotone CMPXCHG und Gatewirkung.
- Der `TerminalHandoffRevocationAttestorV1` ist die einzige TCB-Autorität für
  die Richtigkeit der Revocation-/Halter-Evidence.
- Der Persistence Owner ist die einzige TCB-Autorität für die Richtigkeit der
  Durable-OPEN-Commit-Fortsetzung.
- Der Guard ist nur Consumer beider Grants und darf deren Tatsachen nicht
  selbst attestieren.
- Ein kompromittierter Kernel, ein kompromittierter Grant-Aussteller oder ein
  privilegierter Co-Tenant bleibt außerhalb des behaupteten Schutzmodells.
  Ein fehlerhafter oder kompromittierter Guard bleibt dagegen innerhalb des
  Schutzmodells: Er kann ohne den fremd ausgestellten Grant weder BOOTSTRAP
  noch RELEASED erreichen.

Die ausführbaren Hashes, BTF-/Program-Tags, TID-/Startzeitidentitäten,
Control-Socket-Cookies, Seccomp-Filter und die Nichtübertragbarkeit der beiden
Ausstellerautoritäten müssen Bestandteil von Capability-, Startup-, OPEN- und
Completion-Evidence sein. Dynamic loading, `exec`, zusätzliche TIDs,
ptracebare Aussteller, gemeinsame Files Tables oder generische
`shutdown`-Allowances sind verboten.

Diese explizite TCB-Grenze ist erforderlich, weil ein BPF-LSM-Hook weder den
Inhalt einer beliebigen Userspace-Evidence selbst beweist noch aus einem
Guard-`shutdown` die vorangegangene Filesystem-Durability ableiten kann.
Revision 21 darf diese Aussage nicht erneut überdehnen.

---

## 5. Crash-, Stop- und Fehlerordnung

Jede Grenze der neuen FSM muss total geordnet sein:

1. Fehler oder Crash vor Transition 2 lässt Phase 1 bestehen; Runtime-Sockets
   und Sends bleiben kernel-seitig gesperrt. Kein Same-Session-Retry.
2. Erfolg von Transition 2 mit verlorenem Userspace-Return lässt Phase 2
   bestehen. Da Phase 2 noch keine Socket-Erzeugung erlaubt, ist der Zustand
   terminal fail closed.
3. Crash zwischen Transition 2 und 3 lässt Phase 2 bestehen; keine
   Provisionierung und kein Send.
4. Erfolg von Transition 3 mit verlorenem Return lässt Phase 3 bestehen. Die
   Session darf nicht anhand eines fehlenden lokalen ACK fortgesetzt werden;
   Send bleibt gesperrt und der Startup wird terminal bereinigt.
5. Fehler vor Transition 4 lässt Phase 3 bestehen; der globale Send-Gate
   verhindert jede Queuewirkung. Ein bereits partiell oder vollständig
   geschriebenes OPEN ohne Grant ist unclosed.
6. Erfolg von Transition 4 mit verlorenem Return lässt Phase 4 bestehen;
   Send bleibt gesperrt und kein zweiter Grant ist zulässig.
7. Crash zwischen Transition 4 und 5 lässt Phase 4 bestehen; kein fachlicher
   Send, Folgestart klassifiziert die Session als unclosed.
8. Erfolg von Transition 5 mit verlorenem Return lässt Phase 5 als
   autoritativ bestehen. Rollen dürfen erst nach konsistentem externen
   Phase-/OPEN-Nachweis in den Loop eintreten; jede Unsicherheit beendet alle
   Rollen fail closed.
9. Ein Attestor- oder Persistence-Grant aus falscher Phase, von falschem TID,
   falschem Socket, mit falschem `how` oder als zweiter Versuch mutiert nichts
   und beendet den Startup.
10. Cleanup darf die BPF-Links, Maps oder Pins erst nach Prozessende,
    Endpoint-/Queue-Zerstörung und vollständigem Referenznachweis entfernen.

Kein Fehlerpfad darf einen Grant zurücknehmen, wiederverwenden oder in eine
neue Session übernehmen.

---

## 6. Fault-, Capability-, Evidence- und Completion-Gates für Revision 21

Revision 21 muss mindestens folgende neue Trials ergänzen:

1. richtiger Guard-TID, richtiger Phase-Control-Socket und `SHUT_RD` in
   `LISTENER_RECEIVED` vor Revocation Grant: keine Mutation, keine
   Runtime-Socket-Erzeugung;
2. derselbe Aufruf nach Revocation Grant: genau einmal Phase 2→3;
3. richtiger Guard-TID, richtiger Phase-Control-Socket und `SHUT_RDWR` in
   `BOOTSTRAP` vor Durability Grant: keine Mutation, jeder Session-Send
   `-EPERM`;
4. derselbe Aufruf nach Durability Grant: genau einmal Phase 4→5;
5. Guard auf jedem Grant-Control-Socket sowie jeder Grant-Aussteller auf dem
   Phase-Control-Socket: `-EPERM`, keine Mutation;
6. vertauschte Grant-Sockets, Owner-TIDs, Startzeiten, Cgroups, Cookies,
   Session-Nonces und `how`-Werte;
7. Grant vor vollständiger Evidence in einem instrumentierten Attestor- oder
   Persistence-Owner-Build: der Ausstellerpfad darf den Trigger nicht
   erreichen; Capability bleibt FAIL;
8. Crash/Stop des Attestors vor und nach Transition 2 sowie Crash/Stop des
   Persistence Owners vor und nach Transition 4;
9. verlorener Return jedes der fünf CMPXCHG-Trigger;
10. doppelter, stale, fremder, rückwärts gerichteter und aus einer vorherigen
    Session stammender Grant;
11. FD-Duplikation, SCM_RIGHTS, `pidfd_getfd`, `/proc/fd`, `fork`, `clone`,
    `exec` und gemeinsame Files-Table gegen alle drei Control-Sockets;
12. BPF-Map-/Link-/Program-/Pin-Verlust oder Userspace-Map-Update in jeder
    der sechs Phasen;
13. Runtime-Socket-Erzeugung in Phase 0, 1 und 2 sowie Sendversuche in jeder
    Phase 0 bis 4;
14. nach Transition 4 manipuliertes oder fehlendes OPEN-Artefakt: terminaler
    Abbruch, kein Transition-5-Aufruf und kein Send;
15. vollständige alte Rights-Race-Matrix in Phase 3 und 4, einschließlich
    in-flight `setsockopt`, SCM_RIGHTS, Empfänger-Stop/-Crash und
    Sender-Close/-Crash.

PASS verlangt für frühe korrekte Guard-Aufrufe Ablehnung **vor**
Phasenmutation und vor jeder Endpoint-/Sendwirkung. PASS verlangt außerdem,
dass ausschließlich die richtige getrennte Ausstellerautorität den jeweils
fehlenden Grant erzeugen kann und dass der Grantzustand allein noch keine
geschützte Wirkung öffnet.

Evidence muss mindestens enthalten:

- alle sechs Phasenwerte und fünf CMPXCHG-Ergebnisse mit monotonic timestamps;
- drei Control-Socket-Cookies, Tags, Owner-TGID/TID/Startzeiten und Cgroup-ID;
- Executable-/Filter-/Program-/Map-/Link-/BTF-Fingerprints aller drei
  Autoritäten;
- vollständige Revocation-/Ein-Halter-Evidence vor Transition 2;
- OPEN-Bytes, Hash, Ledger-/Authority-Bindung, Sync-/Directory-Sync-/Readback-
  Resultate vor Transition 4;
- Phase 2 vor Transition 3 und Phase 4 vor Transition 5;
- null Runtime-Sockets vor Phase 3 und null erfolgreiche Session-Sends vor
  Phase 5;
- Crash-/Cleanup- und Referenzfreiheit für jeden terminalen Trial.

---

## 7. Versionierung und Preservation

Revision 21 muss mindestens folgende Typen eindeutig hochzählen:

- `IU4RuntimeControlProfileV15`;
- Runtime Session Envelope V16;
- `TerminalRuntimeSocketLSMGuardV3`;
- `TerminalRuntimeSocketGuardPhaseV3`;
- `TerminalHandoffRevocationAttestorV1`;
- `TerminalRuntimeChannelProvisioningV6`;
- `TerminalPersistenceWorkerV8`;
- `TerminalLeaseCapabilityProfileV14`.

Alle davon abhängigen Startup-, Evidence-, Fault-, Monitoring-, Reason-Code-,
Completion- und Package-Referenzen müssen dieselbe Vertragsfamilie verwenden.
Es darf keine normative V20-Vierphasen-FSM oder direkte
`LISTENER_RECEIVED→BOOTSTRAP`-/`BOOTSTRAP→RELEASED`-Transition übrig bleiben.

Revision 21 muss ausdrücklich bewahren:

- V20s socketfreien `TerminalSeccompListenerHandoffV2` über `pidfd_getfd` und
  Eventfd-ACK;
- V20s reale programmseitige BPF-CMPXCHG und die für Userspace eingefrorene
  Phase-Map;
- V19s globales Socket-Tag/Seal, `file_receive`-Fence und die zwölf
  `INIT→SEALED`-Grenzen;
- V19s ausnahmslosen Session-Send-Gate vor Release;
- `V15-B1`: Signal-Envelope, `WAIT_KILLABLE_RECV`, Broker-CAS und totale
  Listener-Ready-/Receive-Fehlerklassifikation;
- sämtliche älteren Close-, Trip-, Liveness-, Single-Owner-, No-Dual-Write-,
  Decimal-, Atomic-V2-, Loss-Cluster-, Execution-Control-, Authority-,
  Recovery-, Genesis- und L0/L1-Kill-/Restart-Closures;
- Windows und jede Plattform ohne separat reviewte äquivalente
  Kernelprimitive bleiben unsupported und fail closed;
- Implementierung, IU4 ENFORCED, Exchange und Live bleiben nicht freigegeben.

`V20-H1`, `V18-H1`, `V17-H1`, `V16-H1` und `V15-H1` dürfen im Resolution-
Arbeitsstrang nur als `MAPPED_PENDING_REVISION_21_AND_INDEPENDENT_REREVIEW`
geführt werden. Die bereits unabhängig bestätigte Schließung der unmittelbaren
V19-H1-Transferkollision und des realen V19-H2-CAS-Primitivteils bleibt
preserved.

---

## 8. Nicht ausreichende Scheinlösungen

Revision 21 schließt `V20-H1` ausdrücklich nicht durch:

- eine erneute textuelle Aussage „Guard ruft erst danach auf“;
- dieselbe Vierphasen-FSM mit zusätzlichen Logs;
- einen vom Guard selbst gesetzten Boolean, Eventfd, Memfd oder Mapwert;
- einen Userspace-writable Grant-/Phase-Map-FD;
- Lookup plus Update oder `BPF_MAP_UPDATE_ELEM` als CAS-Ersatz;
- einen post-hoc `/proc`-/FD-/Queue-Snapshot nach bereits geöffneter Phase;
- einen Grant, den Guard und Aussteller aus derselben TID, Files Table oder
  austauschbaren Control-Socket-Autorität erzeugen können;
- ein OPEN-Hashfeld ohne nachgewiesene Dateisynchronisation und Readback;
- einen Grantzustand, der bereits selbst Runtime-Sockets oder Sends freigibt;
- das stillschweigende Verschieben eines fehlerhaften Guards außerhalb des
  Schutzmodells.

---

## 9. Formale Scope- und Mapping-Verifikation

```text
REVISION_20_REREVIEW_FINDINGS_MAPPED: 1/1
BLOCKERS_MAPPED: 0/0
HIGH_FINDINGS_MAPPED: 1/1
V20_H1_MAPPED_FOR_REVISION_21: YES
V20_H1_INDEPENDENTLY_CLOSED: NO
V19_H1_MECHANICAL_TRANSFER_CONFLICT_CLOSED_STATUS_PRESERVED: YES
V19_H2_REAL_BPF_CAS_PRIMITIVE_CLOSED_STATUS_PRESERVED: YES
V18_H1_MAPPED_PENDING_REVISION_21_REREVIEW: YES
V17_H1_MAPPED_PENDING_REVISION_21_REREVIEW: YES
V16_H1_MAPPED_PENDING_REVISION_21_REREVIEW: YES
V15_H1_MAPPED_PENDING_REVISION_21_REREVIEW: YES
V15_B1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSURES_PRESERVED: YES
SINGLE_OWNER_PRESERVED: YES
NO_DUAL_WRITE_PRESERVED: YES
DECIMAL_BOUNDARY_PRESERVED: YES
ATOMIC_V2_LOSS_CLUSTER_PRESERVED: YES
EXECUTION_CONTROL_PRESERVED: YES
SPECIFICATION_MUTATED: NO
RUNTIME_OR_STATE_MUTATION: NO
WORKSTATION_R3_MUTATION_OR_RETRY: NO
SCHEDULER_OR_EXCHANGE_MUTATION: NO
RESEARCH_MUTATION: NO
STATE_RESEARCH_S45_CREATED: NO
BUILD_RCC002_SPEC_BUNDLE_READ_OR_EXECUTED: NO
GIT_STAGE_COMMIT_FETCH_PUSH: NO
TESTS_WITH_WRITES: NO
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der einzige beabsichtigte Write-Scope dieser Aufgabe ist dieser neue
Resolution-Record. Die Revision-20-Spezifikation, der V20-Review, die
V19-Resolution und alle bestehenden untracked Artefakte bleiben unverändert.
Das Resolution-Protokoll enthält keinen zirkulären Selbsthash.

---

## 10. Resolution-Urteil und nächste Schritte

```text
RESOLUTION_RESULT: MAPPED_FOR_REVISION_21_PENDING_SPECIFICATION_AND_INDEPENDENT_REREVIEW
CONTROLLING_SPECIFICATION_REVISION: 20
REQUIRED_NEXT_SPECIFICATION_REVISION: 21
SELF_CERTIFIED_READY: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Der unmittelbar nächste Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-21`

Revision 21 muss die in diesem Record definierte sechsstufige FSM, getrennte
Grant-Autoritäten, Gate-Matrix, TCB-Grenze, Crashordnung und Trials vollständig
in die kanonische Spezifikation integrieren und einen neuen vollständigen
Hash erzeugen.

Erst danach ist als eigener Schritt zulässig:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-21-INDEPENDENT-READONLY-REREVIEW`

Dieser unabhängige Review muss den vollständigen Revision-21-Hash prüfen und
insbesondere beweisen, dass ein richtiger Guard-Aufruf vor dem jeweils fremd
ausgestellten Grant ohne Phasenmutation scheitert, während der ordnungsgemäße
Happy Path alle fünf CMPXCHG-Transitionen genau einmal ausführt. Bis zu einem
positiven unabhängigen Urteil bleiben Implementierung, Aktivierung, Exchange
und Live gesperrt.
