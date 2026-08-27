# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-17 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-17-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Root verifiziert:** `/home/benja/projects/sniper-bot`
- **HEAD:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **Divergenz:** `main` ist exakt sechs Commits voraus (`0 6` für `origin/main...main`)
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel-Revision:** `17`
- **Reviewziel SHA-256:** `ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64`
- **Reviewziel Zeilen:** `3865`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_16_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `25a94fb235e172a9c298abd2d07f8d1f635260e01b1a6c99e070f0facf9ce041`
- **Controlling Resolution Zeilen:** `321`
- **Controlling V16 Review:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_16_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md`
- **Controlling V16 Review SHA-256:** `85068c49739e5016ff9ec0a614e3dcdac97a352594cc3839cf7ce8414e5f80df`
- **Controlling V16 Review Zeilen:** `330`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik und Aussagegrenze

`AGENTS.md`, das vollständige Reviewziel, die vollständige controlling
Revision-16-Resolution, der vollständige unabhängige V16-Review sowie die
Revision-15-Resolution und der unabhängige V15-Review wurden gelesen. Die
Resolution wurde ausschließlich als Finding-Mapping, nicht als Beweis
verwendet. Ergänzend wurden die höherrangigen Autoritäten
`LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
`LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md`, `LIVE_DESIGN_L0_STATE_MODEL.md`,
`LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md`,
`LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md`,
`LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md` und
`PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md` geprüft. Die
Revision-8- bis Revision-14-Finding-/Resolution-Ketten wurden für V8-H1,
V9-B1/M1, V10-B1, V11-B1/M1, V12-B1, V13-B1/B2 und V14-B1/B2/H1
herangezogen.

Die Prüfung war statisch, unabhängig und adversarial. Für V16-H1 wurden
insbesondere final-role `listen`/`connect`/`accept4`, der standardmäßig aktive
`SO_PASSRIGHTS`-Zustand, fehlende Listener-Vererbungsautorität, Set/Get am
akzeptierten Empfangssocket, die Bootstrap-Sendesperre, `scm_fds`-/Queue-
Snapshots, die zeitliche Installation der Rollenfilter, eine erneute
`setsockopt(...,SO_PASSRIGHTS,1)`-Operation, Rechtepakete in jedem Setup-
Interleaving, alle sechs Kanäle, Receiver-`SIGSTOP`/-Crash vor `recvmsg`,
Sender-Close/-Crash, SKB-/file-/OFD-/Lock-Lebensdauer und den NULL/0-
Controlbuffer als Defense in Depth modelliert. Signal-/Notification-,
Control-Word-, Renewal-, Close-, Recovery-, Single-Owner-, Decimal- und
Versionsverträge wurden auf Regression geprüft.

Primäre technische Autorität war der Upstream-Linux-Commit
[`77cbe1a6d8730a07f99f9263c2d5f2304cf5e830`](https://github.com/torvalds/linux/commit/77cbe1a6d8730a07f99f9263c2d5f2304cf5e830).
Er belegt den Default `sk_scm_rights=1`, die Set/Get-Option und für AF_UNIX-
Stream/SEQPACKET die Prüfung des Peer-Empfangssockets vor
`skb_queue_tail()`: Bei vorhandenem `SCM_RIGHTS` und deaktiviertem
`sk_scm_rights` endet der Send mit `-EPERM` und der nicht eingereihte SKB wird
freigegeben. Die lokale Review-UAPI definiert `SO_PASSRIGHTS=83`; der
Review-Host läuft mit Linux/WSL
`6.18.33.2-microsoft-standard-WSL2`. Diese lokale Beobachtung ersetzt nicht
den später vorgeschriebenen Capability-Fingerprint des Zielsystems.

Es wurden keine Runtime-, R3-, State-, Workstation-, Scheduler-, Exchange-,
Live-, Research- oder Git-Mutationen und keine Tests mit Writes ausgeführt.
`scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch ausgeführt oder
verändert. `scripts/state_research` blieb geschlossen; es wurde kein S45
angelegt. Fremde untracked Artefakte, Spezifikation und Resolution blieben
unangetastet. Einzige Mutation ist dieser Review-Record.

---

## 2. Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| `V17-H1` | HIGH | OPEN | `SO_PASSRIGHTS=0`, `scm_fds: 0` und leere Queue werden geprüft, bevor die Rollenfilter `setsockopt` irreversibel sperren. Zwischen letztem Snapshot und Filterfinalisierung/OPEN kann ein finaler Empfänger oder ein TID mit derselben Files Table `SO_PASSRIGHTS` wieder aktivieren und der Sender Rights einreihen. Die Spezifikation verlangt danach keinen erneuten Options-/Queue-/OFD-Nachweis. Damit ist die V16-H1-Barriere im Bootstrap nicht monoton und nicht frei von TOCTOU. |

```text
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
```

---

## 3. Finding

### V17-H1 — Snapshot der Rights-Barriere liegt vor ihrer OS-erzwungenen Unveränderlichkeit

**Evidenz im Reviewziel:**

- Zeilen 1431–1441 erzeugen die Kanäle erst zwischen den bereits gestarteten
  finalen Rollenprozessen. Damit existieren die Empfangsprozesse und ihre
  TIDs, bevor die Endpunktoption und die endgültigen Rollenfilter vollständig
  gebunden sind.
- Zeilen 1443–1453 setzen und lesen `SO_PASSRIGHTS=0` am finalen akzeptierten
  Empfangsendpunkt und prüfen anschließend `scm_fds: 0` sowie eine leere
  Queue. Das sind korrekte Zustandsbeobachtungen, aber nur Snapshots.
- Zeilen 1454–1456 ordnen ausdrücklich **erst nach** der vollständigen
  Sechs-Kanal-Barriere die Finalisierung der Rollenfilter und den
  `RUNTIME_SESSION_OPEN` an.
- Zeilen 1463–1465 sperren `setsockopt` nur „nach Ready“. Es fehlt eine
  normative, OS-erzwungene Sperre vom letzten Set/Get-/Queue-Snapshot bis zur
  vollständigen Filterinstallation auf jedem TID, der den Endpoint benutzen
  kann.
- Zeilen 1642–1646 binden erneut Set/Get, verbotene Sends, `scm_fds: 0`, leere
  Queue und **post-Ready** gesperrtes `setsockopt`, verlangen aber keinen
  zweiten Options- und Queue-Nachweis nach nachgewiesener irreversibler
  Filterabdeckung.
- Zeilen 1798–1810 und 1829–1847 beweisen die richtige post-Ready-
  `EPERM`-/Stop-/Crash-Semantik, injizieren jedoch nicht den entscheidenden
  Setup-Race „Set/Get und Queue-Snapshot bestanden; Option vor
  Filterfinalisierung wieder aktiviert; Rights danach vor OPEN queued“.
- Zeilen 2793–2800 nehmen die früheren Snapshots in OPEN und Capability-
  Fingerprint auf. Das Hashen einer Beobachtung verhindert keine spätere
  Mutation zwischen Beobachtung und OPEN.
- Zeilen 3606–3617 verlangen für Provisionsabweichungen nur, dass sie vor
  Ready blockieren, und prüfen Rights-Sends erst post-Ready gegen den
  angenommenen Guard. Der Mutations-/Send-Race während der Guard-
  Finalisierung fehlt.
- Zeilen 3773–3813 wiederholen Set/Get, Pre-Send-Barriere, post-Ready-Sperre
  und Completion-Evidenz, schließen die dazwischen liegende
  Filterinstallationsgrenze aber nicht.

**Bestätigte reale Linux-Semantik:**

Revision 17 wählt für den stationären Runtime-Zustand die richtige Primitive.
Der Upstream-Kernel initialisiert AF_UNIX-Sockets kompatibilitätsbedingt mit
aktivem Rights-Empfang. `setsockopt(SOL_SOCKET,SO_PASSRIGHTS,0)` setzt den
Zustand des konkreten Empfangssockets. Beim AF_UNIX-Stream-/SEQPACKET-Send
prüft der Kernel `other->sk_scm_rights`, bevor er den SKB in
`other->sk_receive_queue` einreiht; bei `0` setzt er `EPERM` und gibt den SKB
über den Fehlerpfad frei. Die Spezifikation ist daher korrekt, weder Default
noch Listener-Vererbung zu vertrauen und den final akzeptierten Socket als
Autorität zu verwenden.

Dies macht die Option selbst jedoch nicht monoton. Solange ein Prozess/TID mit
Zugriff auf den finalen Empfangs-FD noch `setsockopt` ausführen darf, kann er
den Boolean wieder auf `1` setzen. Klassisches Seccomp kann Level und Optname
skalargleich sperren, aber erst nachdem der Filter tatsächlich auf jeden
relevanten TID angewandt wurde. Ein früherer `getsockopt==0`- und
`scm_fds==0`-Nachweis beweist den Zustand nach dieser späteren Mutation nicht.

**Konkreter Ausführungspfad:**

1. Ein finaler Empfänger führt das vorgeschriebene Set/Get aus. Der externe
   Bootstrap-Nachweis beobachtet `SO_PASSRIGHTS=0`, `scm_fds: 0` und eine leere
   Queue.
2. Vor Finalisierung der Rollenfilter ruft derselbe finale Rollenprozess oder
   ein anderer TID mit Zugriff auf dieselbe Files Table
   `setsockopt(receiver_fd,SOL_SOCKET,SO_PASSRIGHTS,1)` auf. Die spätere
   post-Ready-Sperre ist noch nicht wirksam. Die Mutation benötigt weder einen
   neuen FD noch einen von klassischem Seccomp dereferenzierbaren Pointer.
3. Der gebundene Sender sendet im selben Bootstrapfenster ein
   `SCM_RIGHTS`-CMSG. Die textuelle Aussage „sendmsg unzulässig“ ist vor
   Rollenfilterfinalisierung keine Kernelgrenze. AF_UNIX sieht den erneut
   aktivierten Empfängerzustand, übernimmt die file-Referenzen und reiht den
   SKB ein.
4. Die Rollenfilter werden danach finalisiert und OPEN übernimmt den bereits
   vorher erzeugten `scm_fds: 0`-/Queue-Snapshot. Revision 17 verlangt keinen
   erneuten Options-, Queue-, FDINFO-, OFD- und Lock-Nachweis **nach**
   bestätigter vollständiger Filterabdeckung und unmittelbar vor OPEN.
5. Stoppt oder crasht der Empfänger nun vor `recvmsg` und schließt/stirbt der
   Sender, hält der wartende SKB dieselbe file-/OFD-/Lock-Referenz wie in
   V16-H1. Der NULL/0-Controlbuffer kann ohne Empfängerfortschritt weiterhin
   nicht wirken.

Der Race setzt nicht voraus, dass `SO_PASSRIGHTS=0` falsch implementiert ist.
Er nutzt ausschließlich die von der Spezifikation selbst angeordnete
Reihenfolge „Snapshot zuerst, unveränderliche Filtergrenze danach“. Dieselbe
Klasse bloßer Callsite-/Bootstrap-Vertrauensannahmen wurde in den früheren
V8-H1- und V14-B1-Ketten für sicherheitsentscheidende mutable Autoritäten
nicht akzeptiert.

**Impact und erforderliche Resolution:**

Der Pfad öffnet keinen neuen wirtschaftlichen Side Effect nach einer
terminalen Trip-CAS und ist deshalb kein Blocker der V15-B1-Klasse. Er kann
aber die in-flight SKB-/OFD-/Lock-Referenz aus V16-H1 trotz formal bestandenem
OPEN wiederherstellen und Recovery-/Writer-Fencing unbeschränkt blockieren.
Die Severity bleibt daher HIGH.

Eine neue eindeutig versionierte Spezifikationsrevision muss die Setup-
Transition total ordnen. Mindestens erforderlich sind:

1. Set/Get `SO_PASSRIGHTS=0` am finalen akzeptierten Empfangssocket;
2. danach irreversible `setsockopt`-Sperre auf **jedem** TID/Prozess, der über
   die gebundene Files Table Zugriff auf den Endpoint besitzt, mit
   nachgewiesener TSYNC-/Rollenfilterabdeckung;
3. erst nach dieser Unveränderlichkeitsgrenze ein letzter gebundener
   `getsockopt==0`-, `scm_fds: 0`-, Queue-, FD-/FDINFO-, OFD- und Lock-
   Nachweis für alle sechs Kanäle;
4. kein Sender-Release und kein `RUNTIME_SESSION_OPEN` vor diesem letzten
   Nachweis;
5. bei irgendeinem zuvor queued Paket ein fail-closed Bootstrap-Abbruch mit
   nachgewiesener Socket-/Queue-Zerstörung und vollständiger Freigabe aller
   file-/OFD-/Lock-Referenzen, bevor ein neuer Versuch zulässig wäre;
6. Fault-/Capability-/Startup-Trials, die `SO_PASSRIGHTS=1` und Rights-Sends an
   jeder Grenze vor, während und nach der Filterinstallation sowie auf allen
   sechs Kanälen injizieren. PASS verlangt entweder KILL_PROCESS vor Mutation
   oder einen endgültigen post-Filter-Snapshot ohne Queue-/Referenzrest.

Eine bloße erneute textuelle Sendesperre, ein weiterer Snapshot vor der
Filtergrenze oder allein post-Ready ausgeführte Rights-Trials schließt diesen
TOCTOU-Pfad nicht.

---

## 4. Mapping von V16-H1 und V15-B1

| Controlling Finding | Ergebnis in Revision 17 | Begründung |
|---|---|---|
| `V16-H1` | NICHT END-TO-END GESCHLOSSEN / durch `V17-H1` offen | Der stationäre post-Ready-Kernelpfad ist korrekt: `SO_PASSRIGHTS=0` liefert bei Rights `EPERM` vor Queueing und benötigt keinen Empfängerfortschritt. Die Bootstrap-Transition bindet jedoch Queue-/Optionszustand vor dessen OS-erzwungener Unveränderlichkeit und kann daher einen wartenden Rights-SKB in OPEN übernehmen. |
| `V15-H1` | NICHT END-TO-END GESCHLOSSEN / durch `V17-H1` offen | NULL/0-Controlbuffer verhindert nach ausgeführtem Receive eine Empfänger-FD-Installation. Ohne geschlossene Bootstrap-Barriere bleibt die pre-Receive-SKB-Lebensdauer möglich. |
| `V15-B1` | CLOSED / preserved | Signal-Envelope, NEW_LISTENER plus WAIT_KILLABLE_RECV, Listener-Ready-/Receive-Fehlerklassifikation, Broker-CAS und Lease-Fail-stop werden durch Revision 17 nicht abgeschwächt. |

### 4.1 Positiver No-Finding-Nachweis für den stationären Rights-Pfad

- Der finale akzeptierte Empfangssocket ist zutreffend die Autorität; der
  Listenerzustand und eine unbewiesene Vererbung werden nicht verwendet.
- Bei tatsächlich unverändertem `SO_PASSRIGHTS=0` liegt der Upstream-
  `-EPERM`-Pfad vor `skb_queue_tail()`. Kurzzeitig im Syscall erworbene
  Referenzen werden über den SKB-Fehlerpfad freigegeben; nach Return bleibt
  keine queued Receiver-Referenz.
- Post-Ready sperrt die Rollenmatrix `setsockopt` und bindet feste Endpunkt-FDs,
  Richtungen und Peeridentitäten. Ein Rights-Send ist terminal und nicht
  retrybar.
- Die kombinierte Receiver-Stop/-Crash- plus Sender-Close/-Crash-Matrix ist
  nach erfolgreicher Herstellung dieser stationären Grenze vollständig und
  verlangt keine Empfängerfortsetzung.
- Der NULL/0-Controlbuffer und `MSG_CTRUNC` bleiben sinnvoll als getrennter
  Defense-in-Depth-Nachweis, werden nicht mehr als reguläre Prequeue-Autorität
  missverstanden.

Diese positiven Befunde schließen ausschließlich den stationären Zustand und
nicht die in `V17-H1` beschriebene Setup-Transition.

---

## 5. Preservation-Matrix

| Vorfinding/Vertrag | Ergebnis | Evidenz |
|---|---|---|
| V14-B1 | CLOSED / preserved | Kein writable Same-Process-Trip-Latch existiert; der Kernel-Request und die externe Broker-CAS bleiben die Trip-Autorität. |
| V14-B2 | CLOSED / preserved | Beide Worker-ACKs, beide Approval-Empfänger, alle sechs Nachrichtentypen und feste FD-/Richtungsallowlists sind vorhanden; Payloadprüfung bleibt Userspace-Aufgabe. |
| V14-H1 | CLOSED / preserved | Endliche Close-FSM, absolute Deadlines, byteidentische Retries, exactly-once PREPARE/COMMIT und polling-basierte COMMITTED-Konvergenz bleiben vollständig. |
| V13-B2 | CLOSED / preserved | Nur PREPARE→Broker-CLOSED→durable COMMIT ist clean; PREPARE oder CLOSED ohne COMMIT bleibt unclean und erzwingt Terminal-Gap-Recovery. |
| V12-B1 / V11-B1 | CLOSED / preserved | Der Terminal-Sicherheitsweg enthält weiterhin keinen Pipe-Read/-Write/-Datentransfer, Userbuffer-, Pipe-Page-, Reclaim- oder temporären Writerpfad. |
| V11-M1 | CLOSED / preserved | Profil, Session, I2, Dateiscope, Tests und Completion-Gates verwenden konsistent die Revision-17-Vertragsfamilie. |
| V10-B1 | CLOSED im Liveness-Writer-Scope; `V17-H1` getrennt | Feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS und Writer-FD-Referenzsperre bleiben erhalten. Das neue Finding betrifft die Bootstrap-Transition der sechs erlaubten Rollenkanäle. |
| V9-B1 | CLOSED / preserved | Self→Guardian→Broker→Liveness-Close bleibt für jeden zurückkehrenden Fehler ohne Retry erhalten; der Normalpfad bleibt vom Request-TID unabhängig. |
| V9-M1 | CLOSED / preserved | Exakte Memfd-Flags, initialer Seal-State 0, Zwischen- und finaler Seal-State bleiben gebunden. |
| V8-H1 | CLOSED im Control-Word-/Worker-Scope; Prinzip für `V17-H1` relevant | Broker bleibt alleiniger RW-Mapper/Control-Word-Writer; Trading besitzt nur RO und keinen Worker-FD; Worker prüft State, Sequenz und Peer. Die nicht monotone Socketoption-Transition ist davon getrennt. |
| Single Owner / No Dual Write | PRESERVED | OFF/SHADOW bleiben Legacy-owned; ENFORCED PEE besitzt allein Economics/State, Legacy bleibt nur gebundene exit-only Ausnahme. |
| Decimal / PEE Economics | PRESERVED | Canonical Price Text erreicht Decimal ohne Float-Roundtrip; Quantity, Fill, Fees, Settlement, Account und Audit bleiben aus committed Decimal-Artefakten ableitbar. |
| Atomic V2 / Loss Cluster | PRESERVED | OPEN/CLOSE/ENTRY_VETO/PROGRESS und KILL-Ordnungsraum binden S2, Account, Loss Cluster, Throttle, S4V2 und Cursor atomar beziehungsweise journal-first. |
| Execution Control | PRESERVED | Pure Control, Triggerpriorität, OFF/SHADOW-Parität und das Verbot synthetischer Opposing Intents bleiben normativ. |
| Authority / Recovery / Genesis | PRESERVED außer Implementation-Readiness | Ledger Tip und Commit Anchor bleiben getrennt; DIRECT/RECOVERED, NONE-Sentinels, RESTART_ONLY, PREPARE-Completion und Terminal-Gap-Recovery bleiben fail closed. `V17-H1` kann jedoch weiterhin Writer-Fencing/Recovery-Locks halten und verhindert deshalb READY. |
| L0/L1 Kill / Restart | PRESERVED | Kill-Level bleiben monoton, HARD/EMERGENCY stoppen, Auto-Recovery bleibt verboten und Restart benötigt manuelle, durable verbrauchte Autorisierung. |
| Version family | PRESERVED | `IU4RuntimeControlProfileV11`, Session V12, ControlWord V3, SignalEnvelope V1, KernelTripRequest V2, SelfKill V4, CloseProtocol V5, ChannelProvisioning V2, Guardian V10, Broker V7, Shim V8, Worker V4 und Capability V10 sind konsistent. |
| Nichtfreigaben | PRESERVED | Dokument ist keine Implementierung, keine Aktivierung und keine Exchange-/Live-Freigabe; Windows bleibt ohne separat reviewte äquivalente Primitive unsupported. |

Es wurde kein weiterer konkreter Signal-, Renewal-, CAS-, Close-,
Single-Owner-, Dual-Write-, Decimal-, Atomic-V2-, Loss-Cluster-, Authority-,
Genesis-, Startup-, Monitoring-, Reason-Code- oder Freigabebypass gefunden.
Die positiven Preservation-Befunde schließen `V17-H1` nicht.

---

## 6. Gesamturteil und Nichtfreigaben

```text
REREVIEW_RESULT: NOT_READY
SPECIFICATION_REVISION: 17
BLOCKER: 0
HIGH: 1
MEDIUM: 0
LOW: 0
V16_H1_CLOSED: NO_DUE_TO_V17_H1
V15_H1_CLOSED: NO_DUE_TO_V17_H1
V15_B1_CLOSED_STATUS_PRESERVED: YES
V14_B1_CLOSED_STATUS_PRESERVED: YES
V14_B2_CLOSED_STATUS_PRESERVED: YES
V14_H1_CLOSED_STATUS_PRESERVED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES_WITH_V17_H1_DISTINGUISHED
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

Revision 17 wählt die richtige Linux-Primitive und schließt V16-H1 für einen
bereits vollständig hergestellten und unveränderlichen Runtime-Endpunkt. Die
Spezifikation ordnet den letzten Options-/Queue-Snapshot jedoch vor die
OS-erzwungene `setsockopt`-Sperre. Deshalb kann dieselbe queued Rights-
Referenz im Bootstrapfenster wieder entstehen und anschließend mit einem
veralteten PASS-Snapshot in OPEN übernommen werden. Wegen des offenen HIGH-
Findings ist die Spezifikation nicht READY und darf keine Implementierung oder
Aktivierung autorisieren.

---

## 7. Nächster zulässiger Schritt

Erforderlich sind eine Revision-17-Rereview-Resolution, eine neue eindeutig
versionierte Spezifikationsrevision 18 und danach ein unabhängiges read-only
Re-Review des vollständigen neuen Hashes. Die Korrektur muss die
`SO_PASSRIGHTS=0`-Herstellung, vollständige per-TID-Filterabdeckung und den
letzten Options-/Queue-/OFD-Nachweis in dieser Reihenfolge monoton verbinden
und die Setup-Races auf allen sechs Kanälen injizieren.

Der unmittelbar nächste Arbeitsstrang ist daher ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-17-REREVIEW-RESOLUTION`

Bis zu einem unabhängigen PASS einer späteren vollständigen Revision bleiben
Implementierung, IU4 ENFORCED, Exchange und Live gesperrt.

---

## 8. Scope- und Integritätsnachweis

```text
REVIEW_RECORD_ONLY_MUTATION: YES
SPECIFICATION_MUTATED: NO
CONTROLLING_RESOLUTION_MUTATED: NO
CONTROLLING_V16_REVIEW_MUTATED: NO
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
Kernelquellen sowie die Anlage dieses Records. Abschließend werden
Repository-Root, HEAD/main/origin-Divergenz, die kontrollierenden
Dokumenthashes/-zeilen, Markdown-Struktur, Whitespace, Review-Record-Hash/-
zeilen und der exklusive Mutationsscope erneut geprüft.
