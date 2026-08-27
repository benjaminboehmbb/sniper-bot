# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-18 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-18-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Root verifiziert:** `/home/benja/projects/sniper-bot`
- **HEAD:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **Divergenz:** `main` ist exakt sechs Commits voraus (`0 6` für `origin/main...main`)
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel-Revision:** `18`
- **Reviewziel SHA-256:** `6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663`
- **Reviewziel Zeilen:** `4028`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_17_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `5b56d248174ae96c8dbdcdaafce611acb2d18a5e7ae24a49a1fe8ffb0953fce2`
- **Controlling Resolution Zeilen:** `363`
- **Controlling V17 Review:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_17_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md`
- **Controlling V17 Review SHA-256:** `b976df15ac62ef642ce5d1e6bca88bd8ad8c4ef3595c94aa931dd31ea8ce33d8`
- **Controlling V17 Review Zeilen:** `361`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik und Aussagegrenze

`AGENTS.md`, das vollständige Reviewziel, die vollständige controlling
Revision-17-Resolution und der vollständige unabhängige V17-Review wurden
selbst gelesen. Die Resolution wurde ausschließlich als Finding-Mapping, nicht
als Beweis verwendet. Die unabhängigen Reviews und Resolutions der Revisionen
15 und 16 wurden für die vollständige Kette V15-H1 → V16-H1 → V17-H1 geprüft.
Ergänzend wurden die höherrangigen Autoritäten
`LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
`LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md`, `LIVE_DESIGN_L0_STATE_MODEL.md`,
`LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md`,
`LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md`,
`LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md` und
`PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md` herangezogen. Die
älteren Finding-/Resolution-Ketten wurden auf Preservation der bereits
geschlossenen V8-H1-, V9-B1/M1-, V10-B1-, V11-B1/M1-, V12-B1-, V13-B2- und
V14-B1/B2/H1-Verträge geprüft.

Die Prüfung war statisch, unabhängig und adversarial. Für V17-H1, V16-H1 und
V15-H1 wurden die zweiphasige Empfänger-Task-/Endpointtopologie, Set/Get
`SO_PASSRIGHTS=0`, Rights-Freeze-TSYNC, finale Rollenfilter, versteckte
Endpoint-Duplikate, externe Halter, der hostweite `/proc`-/Kernel-
Ownership-Nachweis, der post-filter Options-/`scm_fds`-/Queue-/FD-/OFD-/Lock-
Snapshot, jede Grenze bis OPEN, Senderfreigabe, Prozess-Termination,
Queue-Zerstörung und das Same-Session-Retry-Verbot für alle sechs Kanäle
modelliert. Signal-/Notification-, Control-Word-, Renewal-, Close-, Startup-,
Capability-, Fault-, Completion-, Recovery-, Single-Owner-, Decimal- und
Versionsverträge wurden auf Regression geprüft.

Primäre Linux-Autoritäten waren:

- der Upstream-Commit
  [`77cbe1a6d8730a07f99f9263c2d5f2304cf5e830`](https://github.com/torvalds/linux/commit/77cbe1a6d8730a07f99f9263c2d5f2304cf5e830)
  für `SO_PASSRIGHTS`, dessen Default, Set/Get und die AF_UNIX-Prüfung vor dem
  Queueing;
- Linux `v6.18`
  [`net/socket.c`](https://raw.githubusercontent.com/torvalds/linux/v6.18/net/socket.c)
  für die vom Syscall gehaltene `struct file`-Referenz nach FD-Auflösung und
  vor `do_sock_setsockopt()`;
- Linux `v6.18`
  [`net/core/sock.c`](https://raw.githubusercontent.com/torvalds/linux/v6.18/net/core/sock.c)
  für die Reihenfolge User-Option-Copy, Socket-Lock und Mutation von
  `sk_scm_rights`;
- die Kernel-Dokumentation zu
  [`/proc`](https://www.kernel.org/doc/html/latest/filesystems/proc.html) für
  Prozess-FD-Verzeichnisse und `fdinfo`; sowie
- die Linux-`seccomp(2)`-Dokumentation zu
  [`SECCOMP_FILTER_FLAG_TSYNC`](https://man7.org/linux/man-pages/man2/seccomp.2.html),
  die TSYNC auf die Threads des aufrufenden Prozesses begrenzt.

Die lokale Review-UAPI definiert `SO_PASSRIGHTS=83`; der Review-Host läuft mit
Linux/WSL `6.18.33.2-microsoft-standard-WSL2`. Diese lokale Beobachtung ersetzt
nicht den vorgeschriebenen Zielsystem-Capability-Fingerprint.

Es wurden keine Runtime-, R3-, State-, Workstation-, Scheduler-, Exchange-,
Live-, Research- oder Git-Mutationen und keine Tests mit Writes ausgeführt.
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch ausgeführt oder
verändert. `scripts/state_research` blieb geschlossen; es wurde kein S45
angelegt. Fremde untracked Artefakte, Spezifikation, frühere Reviews und
Resolution blieben unangetastet. Einzige Mutation ist dieser Review-Record.

---

## 2. Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| `V18-H1` | HIGH | OPEN | Die vier Rollen-TGIDs werden gegen `setsockopt` und FD-Erzeugung eingefroren, der nachgelagerte hostweite Ownership-Nachweis ist aber keine spezifizierte atomare Kernelbarriere gegen bereits aufgelöste, nur noch in fremden Syscalls gehaltene Endpoint-`struct file`-Referenzen. Ein externer Holder kann vor der Inventur `setsockopt(...,SO_PASSRIGHTS,1)` beginnen, nach FD-Auflösung und vor Options-Copy/Mutation blockieren, seinen sichtbaren FD schließen und nach dem finalen Snapshot fortsetzen. `/proc/<pid>/fd` sieht diese Referenz nicht; die nicht definierte „Kernel-Socketreferenzansicht“ bindet weder API noch in-flight-Referenzzählung, Quieszenz oder Freeze. Damit kann der Optionszustand nach dem autoritativen Snapshot wieder mutieren. |

```text
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

---

## 3. Positiver Befund zur Revision-17-Resolution

Revision 18 korrigiert den in V17-H1 beanstandeten inneren Rollen-Race
substanziell:

- Zeilen 1478–1487 frieren vor der Endpunktkonfiguration TGID, vollständige
  TID-/Startzeitmenge und Files-Table-Identität ein und sperren weitere Task-
  oder Files-Table-Erzeugung per TSYNC/KILL_PROCESS.
- Zeilen 1494–1499 erzeugen zuerst alle Empfangsendpunkte eines TGID, setzen
  dann am jeweils akzeptierten finalen Empfangssocket `SO_PASSRIGHTS=0` und
  lesen den Wert unmittelbar zurück. Listenerzustand und Vererbung sind keine
  Autorität.
- Zeilen 1501–1509 installieren danach einen eigenen, irreversiblen
  `setsockopt`-KILL_PROCESS-Filter per TSYNC auf allen vorab inventarisierten
  Empfänger-TIDs. Dieser Filter liegt nun vor jedem finalen Rollenfilter.
- Zeilen 1511–1517 stapeln erst anschließend die finalen Rollenfilter auf allen
  vier TGIDs und sperren neue FDs, Duplikation, Connect/Accept, FD-Transfer und
  nicht gebundene Sends.
- Zeilen 1527–1535 legen den autoritativen Options-/`scm_fds`-/Queue-/FD-/OFD-/
  Lock-Snapshot ausdrücklich **nach** vollständiger Filterabdeckung.
- Zeilen 1537–1550 verlangen bei jedem Residuum Totalabbruch,
  Prozess-Termination, Socket-/Queue-Zerstörung, Referenzfreigabe und einen
  vollständig neuen Startup-Versuch. Vor PASS bleibt jeder Sender gesperrt.

Damit kann kein TID innerhalb eines der vier korrekt inventarisierten Rollen-
TGIDs nach Rights-Freeze `SO_PASSRIGHTS` zurück auf `1` setzen. Die
V17-H1-Reihenfolge „Snapshot vor Unveränderlichkeitsgrenze“ ist innerhalb
dieses geschlossenen Rollenuniversums beseitigt. Das neue Finding betrifft
nicht diese TSYNC-Semantik, sondern die davor mögliche Weitergabe an einen
Prozess außerhalb des TSYNC- und finalen Rollenfilteruniversums und die nicht
atomar spezifizierte Fremdhalter-Inventur.

---

## 4. Finding

### V18-H1 — Hostweiter Ownership-Snapshot schließt in-flight Fremdreferenzen und spätere Optionsmutation nicht monoton aus

**Evidenz im Reviewziel:**

- Zeilen 1462–1476 erzeugen zwölf finale FDs für sechs Verbindungen und
  schließen danach Listener-/Bootstrap-/abgelehnte Connect-FDs. Die
  „ausschließlich zwölf“-Aussage ist an dieser Stelle noch keine
  hostweit erzwungene Referenzbarriere.
- Zeilen 1478–1487 sagen ausdrücklich, dass die erste Topologiephase noch
  keine FD-Erzeugungssperre behauptet. Die Task-/Files-Table-Sperre deckt die
  vier Rollen-TGIDs ab, aber keinen bereits existierenden fremden Prozess.
- Zeilen 1501–1509 machen `setsockopt` ausschließlich auf den TIDs der vier
  Empfänger-TGIDs unveränderlich. TSYNC kann definitionsgemäß keine Threads
  eines anderen Prozesses filtern.
- Zeilen 1511–1516 sperren Duplikation und FD-Transfer in den Rollenprozessen
  erst nach Existenz und Konfiguration der finalen Endpunkte. Eine vorher an
  einen externen Prozess gelangte Referenz wird dadurch nicht widerrufen.
- Zeilen 1517–1525 verlangen anschließend eine hostweite Inventur über alle
  `/proc/<pid>/fd`-Mengen und eine „Kernel-Socketreferenzansicht“. Die
  Spezifikation definiert für Letztere weder konkretes Kernel-/UAPI-Interface,
  Referenztyp und Zählregel noch einen atomaren Snapshot, eine globale
  Prozessquieszenz oder eine bis OPEN gehaltene Referenz-Erzeugungssperre.
- Zeilen 1527–1535 führen danach getrennte `getsockopt`, `scm_fds`, Queue,
  FD/FDINFO, OFD und Lock-Beobachtungen aus. Ohne Freeze fremder Holder sind
  diese seriellen Beobachtungen kein einziger linearer Kernelzustand.
- Zeilen 1537–1547 terminieren im Fehlerfall die vier finalen Rollenprozesse
  und schließen Launcher-/Listenerkopien. Ein fremder Prozess mit bereits
  aufgelöster Endpoint-`struct file`-Referenz ist nicht als
  Terminationsziel gebunden und kann die Socket-/Queue-Zerstörung verhindern.
- Zeilen 1548–1561 behaupten, zwischen Snapshot und OPEN könne kein Endpoint
  `SO_PASSRIGHTS` erneut aktivieren. Diese Schlussfolgerung folgt nur für die
  vier gefilterten TGIDs, nicht für einen externen in-flight Syscall.
- Zeilen 1911–1929 und 1948–1973 prüfen TSYNC-Abdeckung, versteckte
  Endpoint-Duplikation, Rights-Sends, Snapshotgrenzen, Abbruch und
  Referenzfreigabe. Es fehlt der konkrete Trial „fremder Holder löst FD im
  Kernel auf, schließt den letzten sichtbaren FD, bleibt vor der
  Optionsmutation blockiert und setzt nach Ownership-/Options-Snapshot fort“.
- Zeilen 2136–2144 machen dieselbe nicht operational definierte systemweite
  Ownership-Inventur zum Startup-Gate. Hash-/Evidence-Bindung kann eine nicht
  atomare oder unvollständige Beobachtung nicht in eine Kernelbarriere
  verwandeln.
- Zeilen 3750–3768 injizieren versteckte Duplikation und Übertragung, aber
  verlangen nur Blockierung oder Erkennung. Sie spezifizieren weder die
  Erkennung kernel-only gehaltener `struct file`-Referenzen noch das Einfrieren
  externer Prozesse während aller anschließenden Messungen bis OPEN.
- Zeilen 3924–3976 übernehmen diese Annahmen in Completion. Der Completion-
  Gate beweist daher die behauptete globale Exklusivität nicht.

**Bestätigte reale Linux-Semantik:**

Der Upstream-`SO_PASSRIGHTS`-Guard selbst ist geeignet: Bei AF_UNIX Stream und
SEQPACKET prüft der Sendepfad den aktuellen `sk_scm_rights`-Wert des
Peer-Sockets vor `skb_queue_tail()` und liefert bei Rights plus `0` `EPERM`.
Der Fehlerpfad gibt den nicht eingereihten SKB frei. Revision 18 setzt die
Option am richtigen, akzeptierten Empfangssocket und friert die Mutation für
die vier Rollenprozesse korrekt ein.

Der Linux-`setsockopt`-Syscall löst den FD jedoch zuerst zu einer gehaltenen
`struct file`-Referenz auf. Erst danach erreicht er `do_sock_setsockopt()` und
den allgemeinen Socket-Optionspfad. Für Integer-Optionen kopiert
`sk_setsockopt()` den Userwert, bevor der Socket-Lock genommen und
`sk_scm_rights` geschrieben wird. Ein Thread kann damit nach erfolgreicher
FD-Auflösung, aber vor Options-Copy oder Mutation blockieren. Schließt ein
anderer Thread den sichtbaren Deskriptor, bleibt die vom laufenden Syscall
gehaltene `struct file` gültig.

`/proc/<pid>/fd` bildet die offenen Deskriptoren der Files Table ab. Eine nur
noch durch den Kernelstack eines laufenden Syscalls gehaltene `struct file`
besitzt keinen dafür erforderlichen sichtbaren FD-Eintrag. Ein sequenzieller
Scan aller Prozess-FD-Verzeichnisse ist außerdem kein atomarer hostweiter
Snapshot. Eine zusätzliche Kernelinstrumentierung könnte Referenzzahlen und
in-flight Operationen prinzipiell beobachten; Revision 18 benennt und bindet
aber weder eine solche Primitive noch deren Vollständigkeit, Linearisation,
Racefreiheit und Fail-closed-Fähigkeit. Die bloße Bezeichnung
„Kernel-Socketreferenzansicht“ ist deshalb kein reproduzierbarer Capability-
oder Completion-Beweis.

**Konkreter Ausführungspfad:**

1. Vor der finalen Rollenfiltergrenze gelangt eine Kopie eines akzeptierten
   Empfangsendpunkts an einen bereits existierenden Prozess außerhalb der vier
   Rollen-TGIDs. Revision 18 behauptet für diese Phase keine universelle
   Endpoint-FD-Erzeugungs-/Transferbarriere.
2. Ein Thread dieses Prozesses beginnt
   `setsockopt(receiver_fd,SOL_SOCKET,SO_PASSRIGHTS,1,...)`. Der Kernel löst den
   FD auf und hält die zugehörige `struct file`; der Thread blockiert danach
   kontrolliert beim Lesen des User-Optionswerts, beispielsweise an einer
   faultenden Userseite, noch bevor `sk_scm_rights` geschrieben wird.
3. Ein zweiter Thread schließt den sichtbaren Endpoint-FD. Der laufende Syscall
   behält seine Kernelreferenz, aber `/proc/<pid>/fd` zeigt keinen Endpoint-FD
   mehr. Die Spezifikation besitzt keine konkret gebundene API, die genau
   diese in-flight Referenz erkennen und bis OPEN stilllegen muss.
4. Die vier Rollen-TGIDs bestehen Rights-Freeze und finale Rollenfilter. Der
   hostweite FD-Scan sowie der post-filter `getsockopt==0`-, `scm_fds: 0`-,
   Queue-, FD-/OFD-/Lock-Snapshot können PASS liefern: Die Optionsmutation ist
   noch nicht ausgeführt und kein Rights-SKB ist eingereiht.
5. Nach diesem autoritativen Snapshot setzt der externe Thread fort. Er wird
   von keinem Rollen-TSYNC-Filter erfasst, nimmt den Socket-Lock und setzt
   `sk_scm_rights=1` auf demselben Empfangssocket. Revision 18 verlangt keinen
   weiteren Snapshot nach dieser Fortsetzung und besitzt keine externe
   Quieszenzbarriere bis OPEN.
6. Nach Senderfreigabe kann ein erlaubter Sender `SCM_RIGHTS` einreihen. Wird
   der Empfänger vor `recvmsg` gestoppt oder beendet und schließt der Sender
   seine eigene Referenz, hält der Receiver-SKB die file-/OFD-/Lock-Referenz.
   Der NULL/0-Controlbuffer und Autoclose können ohne Empfängerfortschritt nicht
   wirken. V16-H1 und V15-H1 sind damit wieder erreichbar.

Der Pfad benötigt keinen Fehler in `SO_PASSRIGHTS`, TSYNC oder AF_UNIX. Er
nutzt ausschließlich die Lücke zwischen prozesslokal vollständiger Filterung
und einer nur beobachtenden, nicht operational/atomar gebundenen hostweiten
Exklusivitätsbehauptung. Derselbe Grundsatz gilt bei einer wandernden externen
FD-Kopie während eines sequenziellen `/proc`-Scans: Ohne Freeze oder atomare
globale Primitive kann „bei jedem gelesenen PID kein FD“ nicht zu „zu einem
gemeinsamen Zeitpunkt existierte kein fremder Holder“ hochgestuft werden.

**Impact und erforderliche Resolution:**

Der Pfad erzeugt keinen neuen wirtschaftlichen Side Effect nach terminaler
Trip-CAS und ist deshalb kein Blocker der V15-B1-Klasse. Er kann jedoch trotz
formal bestandenem OPEN einen Rights-SKB und damit eine unbeschränkt lebende
file-/OFD-/Lock-Referenz herstellen, Queue-Zerstörung, Writer-Fencing und
Recovery blockieren. Die Severity ist HIGH.

Eine neue eindeutig versionierte Spezifikationsrevision muss eine konkrete,
OS-erzwungene globale Endpoint-Exklusivitäts- und Quieszenzgrenze definieren.
Mindestens erforderlich sind:

1. Endpoints dürfen vor der irreversiblen Transfer-/Duplikationssperre niemals
   ein Schutzuniversum verlassen, das alle möglichen Holder und
   `setsockopt`-Caller umfasst; alternativ sind alle Endpoints nach jeder
   transferfähigen Bootstrapphase zu zerstören und ausschließlich unter der
   bereits endgültigen Grenze neu zu erzeugen.
2. Falls externe Prozesse technisch Endpointzugriff erlangen können, muss
   eine konkrete Kernel-/LSM-/Namespace-/Cgroup-/Brokerprimitive deren weitere
   FD-Akquisition, Duplikation, Übertragung und `setsockopt`-Mutation erfassen.
   Der Name der Primitive, Kernel-/UAPI-Version, Argumente, Fehlersemantik,
   Scope und Capability-Fingerprint müssen normativ gebunden sein.
3. Vor dem finalen Snapshot müssen alle vor der Filtergrenze begonnenen
   Endpoint-Syscalls gequiesced oder terminal abgebrochen sein. Der Beweis muss
   FD-less, nur im Kernel gehaltene `struct file`-Referenzen und wartende
   Optionsmutationen einschließen, nicht nur `/proc/<pid>/fd`, Socket-Inodes
   oder offene Files-Table-Einträge.
4. Ownership-, Options-, `scm_fds`-, Queue-, FD/FDINFO-, OFD- und Lock-Zustand
   müssen unter einer gemeinsamen bis nach durablem OPEN gehaltenen
   Linearisation/Freigabegrenze beobachtet werden. Ein sequenzieller
   hostweiter Scan ohne Stilllegung genügt nicht.
5. Senderfreigabe muss nach dem finalen monotonen Beweis und eindeutig nach
   oder atomar mit durablem `RUNTIME_SESSION_OPEN` geordnet sein; zwischen
   Beweis und Freigabe darf kein externer Referenz- oder Mutationspfad
   wiederaufleben.
6. Der Fehlerpfad muss auch jeden externen Holder/in-flight Caller sicher
   beenden oder dessen Endpointreferenz widerrufen und erst nach bewiesener
   Socket-/Queue-/file-/OFD-/Lock-Zerstörung einen vollständig neuen Startup
   erlauben. Same-Session-Retry bleibt verboten.
7. Für jeden der sechs Kanäle ist der konkrete Fault-Trial erforderlich:
   externer Endpoint-Halter, `setsockopt(SO_PASSRIGHTS=1)` nach FD-Auflösung
   angehalten, sichtbarer FD geschlossen, `/proc`-Inventur ausgeführt,
   Fortsetzung nach dem bisherigen finalen Snapshot versucht. PASS verlangt,
   dass die Akquisition unmöglich war, der Caller vor Mutation terminal endet
   oder der noch unter derselben globalen Grenze liegende Beweis OPEN
   fail closed verhindert. Derselbe Trial ist mit Endpointmigration zwischen
   bereits gescannten Prozessen auszuführen.

Eine unversionierte „Kernel-Sicht“, ein größerer `/proc`-Scan, ein zweiter
serieller Snapshot oder allein die korrekte TSYNC-Abdeckung der vier
Rollen-TGIDs schließt V18-H1 nicht.

---

## 5. Interleaving- und Gate-Matrix

| Grenze | Normativer positiver Befund | Offene adversariale Grenze |
|---|---|---|
| Vor Endpoint-Erzeugung | Rollen-TGIDs, TIDs und Files Tables werden fixiert; weitere Task-/Files-Table-Erzeugung wird gesperrt. | Die erste Phase behauptet keine FD-Sperre und kontrolliert keine bereits existierenden Fremdprozesse. |
| Endpoint-Erzeugung/Attestation | Finale Rollen verbinden/akzeptieren, `SO_PEERCRED` und Startzeit werden gebunden; Bootstrap-FDs werden geschlossen. | Ein vor finalen Filtern herausgelangter Endpoint wird nicht kernel-seitig widerrufen. |
| Set/Get `SO_PASSRIGHTS=0` | Richtiger finaler Empfangssocket wird gesetzt und gelesen. | Externer in-flight Caller kann eine spätere `=1`-Mutation vorbereiten. |
| Rights-Freeze-TSYNC | Jeder vorab inventarisierte TID aller vier Empfänger-TGIDs erhält KILL_PROCESS für jedes `setsockopt`. | TSYNC erreicht keinen Thread eines fremden TGID. |
| Finale Rollenfilter | Neue FDs, Transfer, Connect/Accept und nicht gebundene Sends der Rollen werden gesperrt. | Bereits aufgelöste fremde `struct file` und vor Filterung übertragene Kopien bleiben gültig. |
| Hostweite Ownership-Inventur | Fremde sichtbare FDs sollen fail closed erkannt werden. | `/proc` ist seriell; Kernelreferenzansicht, atomare Linearisation und Fremdprozess-Freeze sind undefiniert. |
| Post-filter Snapshot | Option, `scm_fds`, Queue, FDs/OFDs/Locks werden nach Rollenfilterung erneut geprüft. | Ein blockierter externer Syscall kann erst nach dieser Messung mutieren. |
| PASS → durable OPEN → Senderrelease | Keine Rollenfilter-/FD-Topologieänderung soll stattfinden. | Die globale Fremdhalter-/in-flight-Sperre wird nicht bis OPEN gehalten; Release und OPEN sind in Zeilen 1548–1550 nicht eindeutig gegeneinander linearisiert. |
| Fehlerpfad | Vier Rollen werden terminiert, Endpoints zerstört, Same-Session-Retry verboten. | Fremder Holder/Caller ist nicht zwingend terminiert; totale Zerstörung ist daher nicht beweisbar. |
| Post-OPEN Rights-Send | Bei unverändertem `SO_PASSRIGHTS=0` liefert der Kernel `EPERM` vor Queueing. | Nach externer Mutation auf `1` ist genau diese Voraussetzung falsch. |

---

## 6. Closure-Mapping V17-H1 / V16-H1 / V15-H1

| Controlling Finding | Ergebnis in Revision 18 | Begründung |
|---|---|---|
| `V17-H1` | NICHT END-TO-END GESCHLOSSEN / durch `V18-H1` offen | Innerhalb der vier Rollen-TGIDs ist die richtige monotone Reihenfolge hergestellt: Set/Get → Rights-Freeze-TSYNC → finale Rollenfilter → letzter Snapshot. Der nachgelagerte globale Exklusivitätsbeweis kann aber externe in-flight Caller nicht reproduzierbar und atomar ausschließen. |
| `V16-H1` | NICHT END-TO-END GESCHLOSSEN / durch `V18-H1` offen | Der stationäre Kernelguard liefert nur solange `EPERM` vor Queueing, wie der Empfängerwert `0` bleibt. Ein ungefilterter externer Caller kann ihn nach dem Snapshot auf `1` setzen und die wartende SKB-/OFD-Lebensdauer wiederherstellen. |
| `V15-H1` | NICHT END-TO-END GESCHLOSSEN / durch `V18-H1` offen | NULL/0-Controlbuffer plus Kernel-Autoclose verhindern eine installierte Empfänger-FD erst nach ausgeführtem `recvmsg`. Sie begrenzen einen bereits queued Rights-SKB bei gestopptem/totem Empfänger nicht. |
| `V15-B1` | CLOSED / preserved | Signal-Envelope, NEW_LISTENER plus WAIT_KILLABLE_RECV, Listener-Ready-/Receive-Fehlerklassifikation, Broker-CAS und Lease-Fail-stop wurden nicht abgeschwächt. |

### 6.1 Positiver No-Finding-Nachweis im vollständig geschlossenen Rollenuniversum

- Alle sechs Kanäle besitzen getrennte finale Rollen-Endpunkte und feste
  Sender-/Empfängerzuordnung.
- Set/Get erfolgt autoritativ am akzeptierten Empfangsendpunkt, nicht nur am
  Listener; `SO_PASSCRED=0` und `msg_control=NULL/msg_controllen=0` bleiben
  zusätzliche Defense in Depth.
- Die Rights-Freeze-Filter sind stapelbar, irreversibel, vor den finalen
  Rollenfiltern wirksam und beenden jedes `setsockopt` des betroffenen TGID
  unabhängig von Pointer/FD/Level/Optname mit KILL_PROCESS.
- Task- und Files-Table-Neubildung ist vor Endpointbindung gesperrt; neue TIDs,
  partielle TSYNC-Abdeckung und Filterhashabweichung verhindern PASS.
- Der letzte Options-/Queue-/FD-/OFD-/Lock-Snapshot liegt korrekt nach den
  Rollenfiltern. Pre-filter-Pakete müssen erkannt werden und führen zu totalem
  Bootstrap-Abbruch ohne Same-Session-Retry.
- Bei tatsächlich unverändertem `SO_PASSRIGHTS=0` bleibt der post-OPEN
  AF_UNIX-`EPERM`-Pfad vor Queueing empfängerfortschrittsunabhängig; Sender-
  Close/-Crash hinterlässt dann keine Rights-SKB-/OFD-/Lock-Referenz.

Diese positiven Befunde schließen ausschließlich das durch die vier Rollen-
TSYNC-Grenzen vollständig erfasste Universum und nicht V18-H1.

---

## 7. Preservation-Matrix

| Vorfinding/Vertrag | Ergebnis | Evidenz |
|---|---|---|
| V14-B1 | CLOSED / preserved | Kein writable Same-Process-Trip-Latch existiert; Kernel-Notification und externe Broker-CAS bleiben Trip-Autorität. |
| V14-B2 | CLOSED / preserved | Beide Worker-ACKs, beide Approval-Empfänger, alle sechs Nachrichtentypen und feste FD-/Richtungsallowlists bleiben vollständig; Payloadvalidierung bleibt Userspace-Pflicht. |
| V14-H1 | CLOSED / preserved | Endliche Close-FSM, absolute Deadlines, byteidentische Retries, exactly-once PREPARE/COMMIT und polling-basierte COMMITTED-Konvergenz bleiben erhalten. |
| V13-B2 | CLOSED / preserved | Nur PREPARE→Broker-CLOSED→durable COMMIT ist clean; jede Lücke bleibt unclosed und erzwingt Terminal-Gap-Recovery. |
| V12-B1 / V11-B1 | CLOSED / preserved | Der Terminal-Sicherheitsweg enthält keinen Pipe-Read/-Write/-Datentransfer, Userbuffer-, Pipe-Page-, Reclaim- oder temporären Writerpfad. |
| V11-M1 | CLOSED / preserved | Profil, Session, I2, Dateiscope, Tests und Completion verwenden konsistent die Revision-18-Vertragsfamilie. |
| V10-B1 | CLOSED im Liveness-Writer-Scope; `V18-H1` getrennt | Feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS und Writer-FD-Referenzsperre bleiben erhalten. Das offene Finding betrifft Endpoint-Referenzen eines fremden Prozesses. |
| V9-B1 | CLOSED / preserved | Self→Guardian→Broker→Liveness-Close bleibt für jeden zurückkehrenden Fehler ohne Retry erhalten; der Normalpfad bleibt vom Request-TID unabhängig. |
| V9-M1 | CLOSED / preserved | Exakte Memfd-Flags, initialer Seal-State 0, Zwischen- und finaler Seal-State bleiben gebunden. |
| V8-H1 | CLOSED im Control-Word-/Worker-Scope; Prinzip für `V18-H1` relevant | Broker bleibt alleiniger RW-Mapper/Control-Word-Writer; Trading ist RO und besitzt keinen Worker-FD; Worker prüft State, Sequenz und Peer. Externe Socketreferenzen sind davon getrennt. |
| Single Owner / No Dual Write | PRESERVED | OFF/SHADOW bleiben Legacy-owned; ENFORCED PEE besitzt allein Economics/State, Legacy bleibt nur gebundene exit-only Ausnahme. |
| Decimal / PEE Economics | PRESERVED | Canonical Price Text erreicht Decimal ohne Float-Roundtrip; Quantity, Fill, Fees, Settlement, Account und Audit bleiben aus committed Decimal-Artefakten ableitbar. |
| Atomic V2 / Loss Cluster | PRESERVED | OPEN/CLOSE/ENTRY_VETO/PROGRESS und KILL-Ordnungsraum binden S2, Account, Loss Cluster, Throttle, S4V2 und Cursor atomar beziehungsweise journal-first. |
| Execution Control | PRESERVED | Pure Control, Triggerpriorität, OFF/SHADOW-Parität und das Verbot synthetischer Opposing Intents bleiben normativ. |
| Authority / Recovery / Genesis | PRESERVED außer Implementation-Readiness | Ledger Tip und Commit Anchor bleiben getrennt; DIRECT/RECOVERED, NONE-Sentinels, RESTART_ONLY, PREPARE-Completion und Terminal-Gap-Recovery bleiben fail closed. V18-H1 kann Recovery-/Writer-Fencing-Referenzen halten und verhindert READY. |
| L0/L1 Kill / Restart | PRESERVED | Kill-Level bleiben monoton, HARD/EMERGENCY stoppen, Auto-Recovery bleibt verboten und Restart benötigt manuelle, durable verbrauchte Autorisierung. |
| Version family | PRESERVED | `IU4RuntimeControlProfileV12`, Session V13, ControlWord V3, SignalEnvelope V1, KernelTripRequest V2, SelfKill V4, CloseProtocol V6, ChannelProvisioning V3, ReceiverTaskTopology V1, RightsFreeze V1, Guardian V11, Broker V8, Shim V9, Worker V5 und Capability V11 sind konsistent. |
| Nichtfreigaben | PRESERVED | Dokument ist keine Implementierung, Aktivierung oder Exchange-/Live-Freigabe; Windows bleibt ohne separat reviewte äquivalente Primitive unsupported. |

Es wurde kein weiterer konkreter Signal-, Renewal-, CAS-, Close-,
Single-Owner-, Dual-Write-, Decimal-, Atomic-V2-, Loss-Cluster-, Authority-,
Genesis-, Monitoring-, Reason-Code- oder Freigabebypass gefunden. Capability-,
Startup-, Fault- und Completion-Gates spiegeln die Revision-18-Vertragsfamilie
konsistent, erben aber die fehlende Operationalisierung/Linearisation des
hostweiten Ownership-Beweises. Die positiven Preservation-Befunde schließen
`V18-H1` nicht.

---

## 8. Gesamturteil und Nichtfreigaben

```text
REREVIEW_RESULT: NOT_READY
SPECIFICATION_REVISION: 18
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
V17_H1_CLOSED: NO_DUE_TO_V18_H1
V16_H1_CLOSED: NO_DUE_TO_V18_H1
V15_H1_CLOSED: NO_DUE_TO_V18_H1
V15_B1_CLOSED_STATUS_PRESERVED: YES
V14_B1_CLOSED_STATUS_PRESERVED: YES
V14_B2_CLOSED_STATUS_PRESERVED: YES
V14_H1_CLOSED_STATUS_PRESERVED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES_WITH_V18_H1_DISTINGUISHED
V9_B1_CLOSED_STATUS_PRESERVED: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CONTROL_WORD_WORKER_SCOPE_PRESERVED: YES
SINGLE_OWNER_PRESERVED: YES
NO_DUAL_WRITE_PRESERVED: YES
DECIMAL_BOUNDARY_PRESERVED: YES
ATOMIC_V2_LOSS_CLUSTER_PRESERVED: YES
EXECUTION_CONTROL_PRESERVED: YES
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Revision 18 schließt den V17-H1-Race innerhalb der vollständig inventarisierten
vier Rollen-TGIDs: `SO_PASSRIGHTS=0`, Rights-Freeze-TSYNC, finale Rollenfilter
und letzter Snapshot sind dort richtig geordnet. Die Spezifikation ersetzt
den früheren lokalen TOCTOU jedoch durch eine unbelegte globale
Exklusivitätsannahme. Weder `/proc/<pid>/fd` noch die unoperationalisierte
„Kernel-Socketreferenzansicht“ beweisen atomar, dass kein fremder in-flight
Syscall eine Endpoint-`struct file` hält und den Optionswert nach dem Snapshot
ändern kann. Wegen des offenen HIGH-Findings ist Revision 18 nicht READY und
darf keine Implementierung oder Aktivierung autorisieren.

---

## 9. Nächster zulässiger Schritt

Der unmittelbar nächste Arbeitsstrang ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-18-REREVIEW-RESOLUTION`

Diese Resolution muss V18-H1 in eine neue eindeutig versionierte Revision 19
überführen. Revision 19 muss den hostweiten Ownership-Nachweis durch eine
konkrete monotone OS-Grenze ersetzen oder operationalisieren, externe und nur
kernel-in-flight gehaltene Referenzen einschließen, alle möglichen Holder bis
OPEN quiescen/fencen und die beschriebenen Fault-Trials für alle sechs Kanäle
normativ binden. Danach ist ein unabhängiges read-only Re-Review des
vollständigen neuen Revision-19-Hashes erforderlich.

Bis zu einem unabhängigen PASS einer späteren vollständigen Revision bleiben
Implementierung, IU4 ENFORCED, Exchange und Live gesperrt.

---

## 10. Scope- und Integritätsnachweis

```text
REVIEW_RECORD_ONLY_MUTATION: YES
SPECIFICATION_MUTATED: NO
CONTROLLING_RESOLUTION_MUTATED: NO
CONTROLLING_V17_REVIEW_MUTATED: NO
RUNTIME_OR_STATE_MUTATION: NO
WORKSTATION_R3_MUTATION_OR_RETRY: NO
SCHEDULER_OR_EXCHANGE_MUTATION: NO
RESEARCH_MUTATION: NO
STATE_RESEARCH_S45_CREATED: NO
BUILD_RCC002_SPEC_BUNDLE_READ_OR_EXECUTED: NO
GIT_STAGE_COMMIT_FETCH_PUSH: NO
TESTS_WITH_WRITES: NO
SELF_CERTIFIED_READY: NO
```

Ausgeführt wurden ausschließlich read-only Repository-/Dokumentprüfungen,
lokale UAPI-/Kernelidentitätsprüfungen, read-only Abrufe primärer Linux-
Kernelquellen sowie die Anlage dieses Records. Repository-Root,
HEAD/main/origin-Divergenz, die kontrollierenden Dokumenthashes/-zeilen,
Markdown-Struktur, Whitespace, Review-Record-Hash/-zeilen und der exklusive
Mutationsscope wurden abschließend erneut geprüft.
