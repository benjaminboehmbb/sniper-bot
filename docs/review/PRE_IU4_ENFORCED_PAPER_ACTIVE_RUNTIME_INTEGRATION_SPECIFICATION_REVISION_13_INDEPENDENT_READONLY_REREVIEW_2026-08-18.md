# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-13 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-13-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel SHA-256:** `e8c14a631928914c823a046dc5a85972dfccbbbd48e41897e66926db3e5f1f66`
- **Reviewziel Zeilen:** `3077`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_12_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `81ae636320ce2f5446677e8f0027383888de8074b25d17947d7982e10343c5c5`
- **Controlling Resolution Zeilen:** `216`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik und Aussagegrenze

`AGENTS.md`, das vollständige Reviewziel und die vollständige controlling
Resolution wurden zeilenweise gelesen. Ergänzend wurden die normativen
Autoritäten `LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
`LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md`,
`PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md` sowie die einschlägigen
L1-C-/L1-D-Regeln gegen die behaupteten Preservation-Grenzen geprüft.

Die Prüfung war statisch und adversarial. Sie modellierte insbesondere Task-
Preemption, die Self→Guardian→Broker→Close-Fehlerfolge, PIDFD-/Seccomp-Autorität,
Liveness-Writer-Referenzen, Renewal-/Trip-/Orderly-Close-CAS-Races, fehlende
Worker-Persistenz, Startup-Reklassifikation, Capability-/Fault-/Preflight-
Abdeckung, Versionsfamilien und Nichtfreigaben.

Es wurden keine Runtime-, R3-, Research- oder Git-Mutationen und keine Tests mit
Writes ausgeführt. `scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch
verändert. Reviewziel und controlling Resolution wurden nicht verändert.

---

## 2. Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| V13-B1 | BLOCKER | OPEN | Der Gewinner des lokalen Trip-Latch kann vor dem ersten PIDFD-Syscall unbegrenzt descheduled/stallend bleiben, während Shim und Broker weiter renewen; keine definierte `TERMINAL_FAILSTOP_ASSERTED`-Variante wird erreicht. |
| V13-B2 | BLOCKER | OPEN | Ein Trip nach durablem `RUNTIME_SESSION_CLOSE`, aber vor Broker-`RUNNING→CLOSED`, kann bei verlorener KILL-Persistenz als geschlossene Session überleben und den vorgeschriebenen Terminal-Gap-Startup-Lock umgehen. |

```text
BLOCKER: 2
HIGH: 0
MEDIUM: 0
LOW: 0
```

---

## 3. Findings

### V13-B1 — Lokaler Latch und erster Kernelaufruf sind nicht unteilbar

**Evidenz:**

- Zeilen 992–1006 setzen zuerst den prozesslokalen Latch und führen erst danach
  `pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)` aus; die weiteren Fallbacks
  existieren nur, wenn der TID weiter ausgeführt wird.
- Zeilen 1034–1040 lassen Guardian und Shim ausschließlich das globale Control
  Word beziehungsweise ausbleibende Broker-Approvals beobachten.
- Zeilen 1053–1063 machen den lokalen Latch zwar zur Side-Effect-Sperre, koppeln
  die Timerbeendigung aber weiterhin an Broker-CAS oder ausbleibende Approval.
- Zeilen 1135–1138 binden feste CPU-/Scheduling-Eigenschaften nur für
  Guardian/Broker/Shim, nicht für den Trip auslösenden Trading-TID.
- Zeilen 1169–1207 und 1209–1244 verlangen weder Zertifizierungs- noch
  Startup-Probes, die exakt nach erfolgreicher lokaler Latch-CAS und vor Eintritt
  in `pidfd_send_signal` nur den Gewinner-TID anhalten/deschedulen, während Shim,
  Guardian und Broker gesund weiterlaufen.
- Zeilen 2044–2057 definieren `TERMINAL_FAILSTOP_ASSERTED` ausschließlich über
  Broker-CAS plus Kill, eine angenommene PIDFD-Kill-Anforderung, Lease-Expiry oder
  `SECCOMP_RET_KILL_PROCESS`; der lokale Latch allein erfüllt keine Variante.
- Zeilen 2219–2235 und 2259–2267 behandeln Latch und Syscallfolge sprachlich als
  zusammenhängende Kette, spezifizieren aber keine kernel-sichtbare atomare
  Kopplung oder Beobachtung des lokalen Latch durch den Renewal-Pfad.
- Zeilen 2889–2896 prüfen Whole-Child-Stop und einen bereits vor dem Trip
  blockierten Trading-Thread, nicht das neue Post-Latch/Pre-Syscall-Fenster.

**Konkreter Angriffspfad:**

1. Ein Trading-TID erkennt EMERGENCY und gewinnt die one-way Latch-CAS.
2. Der Scheduler descheduled oder stallt genau diesen TID vor der ersten
   `pidfd_send_signal`-Instruktion auf unbestimmte Zeit. Dafür ist weder ein
   verbotener Syscall noch ein neuer Task/FD nötig.
3. Self-, Guardian- und Broker-PIDFD wurden nicht signalisiert; der Liveness-FD
   wurde nicht geschlossen, daher entsteht kein HUP.
4. Guardian und Broker bleiben gesund und sehen weiterhin Control Word RUNNING.
   Der Broker erzeugt Renewal-CAS/Approvals; der Shim verlängert die Lease.
5. Die lokale Sperre verhindert zwar weitere gegatete Side Effects, aber keine
   der normativen Varianten für `TERMINAL_FAILSTOP_ASSERTED` tritt innerhalb
   `100 ms` ein und der nach L1-C geforderte EMERGENCY-Prozess-Exit ist nicht
   sichergestellt.

Die Aussage „erster Kernelaufruf nach Latch“ ordnet nur den Fall, in dem der TID
den Syscall tatsächlich erreicht. Sie schließt das Scheduling-Fenster nicht.
Erforderlich ist eine kontinuierlich ausführbare, vom Gewinner-TID unabhängige
Beobachtung des lokalen Trip-Zustands, die Renewals spätestens innerhalb des
gebundenen Envelopes stoppt, plus der entsprechende Fault-/Preflight-Nachweis.

### V13-B2 — Durable Session CLOSE kann einen späteren terminalen Trip verbergen

**Evidenz:**

- Zeilen 789–794 klassifizieren nur ein OPEN **ohne** passenden CLOSE oder Gap
  als unclean.
- Zeilen 1076–1086 schreiben zuerst `RUNTIME_SESSION_CLOSE` durable und führen
  erst danach Broker-`RUNNING→CLOSED` aus; zugleich ist jedes HUP vor dieser CAS
  zwingend ein terminaler Trip.
- Zeilen 1022–1051 erlauben bei diesem Trip ausdrücklich verlorene Eventfd-
  Notifications, verlorenen Worker-Request oder Broker-Crash nach CAS; damit ist
  ein persistierter KILL nicht garantiert.
- Startup-Schritt 9 in Zeilen 1325–1329 blockiert offene PREPAREs und
  **unclosed** Runtime Sessions, besitzt aber keinen durable Marker für
  „Session CLOSE vorhanden, Broker-CLOSED nie erreicht, TERMINATING gewann“.
- Zeilen 2062–2070 und 2286–2296 begründen Terminal-Gap-Recovery mit einer
  unclosed Session; diese Voraussetzung ist im beschriebenen Race bereits durch
  den vorab geschriebenen CLOSE-Record verloren.
- Zeilen 2866–2870 verlangen korrekt HUP→TERMINATING vor CLOSED, prüfen aber
  weder die dadurch ungültig gewordene bereits durable CLOSE-Klassifikation noch
  den nächsten Startup bei verlorenem Worker-Request. Zeile 2938 ordnet CLOSE
  nur hinter Reconciliation, nicht hinter den Broker-CLOSED-Nachweis.
- Die controlling Resolution schreibt in Zeilen 96–102 dieselbe Reihenfolge
  „durable Session CLOSE, danach Broker CLOSED“ vor und enthält ebenfalls keinen
  zweiten durable Completion-/Abort-Marker.

**Konkreter Angriffspfad:**

1. Das Trading-Child ist gegatet; State/Journal wurden reconciled und ein
   passender `RUNTIME_SESSION_CLOSE` ist bereits durable.
2. Vor Annahme oder CAS des `ORDERLY_CLOSE` verliert der Prozess den letzten
   Liveness-Writer, etwa durch den ausdrücklich fail-safe zulässigen rohen Close,
   Guardian-Tod oder Child-Termination.
3. Der Broker linearisiert korrekt `RUNNING→TERMINATING`; `RUNNING→CLOSED` ist
   danach verboten.
4. Der Broker→Worker-KILL-Request geht verloren oder der terminale Journal-Write
   scheitert, beides vom Vertrag tolerierte Safety-Fälle.
5. Nach Prozessende existiert im Lifecycle Ledger weiterhin das passende
   `RUNTIME_SESSION_CLOSE`, aber weder ein KILL noch ein durable Nachweis, dass
   Broker-CLOSED nie erreicht wurde.
6. Der nächste Startup sieht deshalb keine „unclosed Session“ und kann die
   vorgeschriebene `TERMINAL_UNKNOWN`-/`RECONCILE_TERMINAL_GAP`-Sperre umgehen.

Damit kann eine terminale monotone Eskalation persistenzseitig als clean shutdown
fehlklassifiziert werden. Ein crash-sicherer Close benötigt einen getrennten
durablen Prepare/Intent- und Final-Commit-Zustand (oder eine äquivalente
nachweisbar fail-closed Reihenfolge), sodass nur ein nach Broker-CLOSED durable
finalisierter Record den Startup als clean freigibt; Trip/Crash vor Finalisierung
muss weiterhin Terminal-Gap-Recovery erzwingen.

---

## 4. Mapping der Vorfindings

| Vorfinding | Ergebnis in Revision 13 | Begründung |
|---|---|---|
| V12-B1 | CLOSED im engen ursprünglichen Umfang | Die Liveness-Pipe überträgt keine Daten; weder Trading noch Broker dürfen Pipe-Read/-Write/Datentransfer ausführen. Der problematische Pipe-Page-/Reclaim-Pfad liegt nicht mehr vor der PIDFD-Folge. V13-B1 ist ein neuer vorgelagerter Scheduling-/Beobachtungsbefund. |
| V11-B1 | CLOSED / obsolet | Freie Userbuffer, `copy_from_user` und Pipe-Write-`struct file`-Referenzen sind aus dem Sicherheitsweg entfernt. |
| V11-M1 | CLOSED / preserved | I2, Dateiscope, Abnahmekriterien und Closing Step verwenden konsistent Profile V7, Session V8, Guardian V6, Broker V3, Shim V4 und Capability V6. |
| V10-B1 | CLOSED / preserved | Feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS, Post-Ready-Task-/FD-/Referenzsperren und letzte Writer-Inventur bleiben normativ. |
| V9-B1 | CLOSED für alle zurückkehrenden Syscall-Ergebnisse; End-to-End durch V13-B1 offen | `EINTR`, `ESRCH`, `EPERM`, `EBADF` und unbekannte Fehler laufen ohne Retry zur nächsten Stufe; Close wird nicht wiederholt. Nicht geschlossen ist der neue Fall, dass der erste Syscall gar nicht erreicht wird. |
| V9-M1 | CLOSED / preserved | `MFD_ALLOW_SEALING`, initiale Seals 0 und beide exakten Seal-Transitionen einschließlich bewusst fehlendem `F_SEAL_WRITE` bleiben vollständig. |
| V8-H1 | CLOSED / preserved | Separater attestierter Broker bleibt alleiniger Control-Word-Writer; Trading besitzt nur RO-Map und keinen Worker-IPC-FD; Worker prüft TERMINATING/Sequenz/Peer selbst. |
| ältere B2/M1/RM1/RB2/RB3/NH1/NH2/NM1/NM2 | PRESERVED | DIRECT-/RECOVERED-Provenance, NONE-Sentinels, neue RESTART_ONLY-Consumption, Authority-/Journal-Roots, Atomic V2/Loss Cluster, Single Owner, Legacy exit-only, Execution-Control-Parität und Scope-/Freigabegrenzen wurden nicht regressiert. |

---

## 5. Positive Bestätigungen ohne Finding

- Die eingefrorenen HEAD-, Spec- und Resolution-Identitäten sowie beide
  Zeilenzahlen stimmten bei Reviewbeginn exakt.
- Kein Pipe-Read, Pipe-Write oder sonstiger Datentransfer ist im terminalen
  Sicherheitsweg autorisiert; der Kanal ist Close-only und dauerhaft leer.
- Wenn der Trip-TID weiterläuft, ist Self-PIDFD-`SIGKILL` der erste Syscall nach
  dem lokalen Latch; alle zurückkehrenden Fehlerklassen erreichen ohne Retry
  Guardian, Broker und den einmaligen Linux-Close.
- Die drei PIDFD-Aufrufe sind mit klassischen Seccomp-Skalarprüfungen für FD,
  Signal, Null-`siginfo` und Flags technisch ausdrückbar; Ziel-/Startzeitbindung,
  Signal-0-Probe, CLOEXEC und FD-Reuse-Sperre ergänzen die Identitätsgrenze.
- Die Last-Writer-Grenze schließt Fork/Clone/Files-Table-Split, Duplication,
  SCM_RIGHTS, procfd, pidfd_getfd, io_uring, epoll-Halter und neue FD-Erzeugung
  ein. Es wurde kein verbleibender konkreter zweiter Writerpfad gefunden.
- Renewal-vor-Trip und Trip-vor-Renewal sind durch die Control-Word-CAS und die
  vorvalidierte absolute Expiry sauber linearisiert; stale Approvals dürfen den
  letzten gebundenen Expiry-Zeitpunkt nicht verlängern.
- Memfd-Bootstrap, sole-RW-Broker-Map, `F_SEAL_FUTURE_WRITE` und anschließendes
  `F_SEAL_SEAL` sind technisch kohärent; `F_SEAL_WRITE` bleibt korrekt abwesend.
- Capability-Zertifizierung und Startup-Probes sind als endliche, hashgebundene
  Envelope-Verträge formuliert und behaupten keine universelle Reap- oder
  Scheduler-Obergrenze. Abgesehen von V13-B1/V13-B2 sind Signal-/Close-, HUP-,
  Renewal-, Worker-, Map-/Seal- und Topologie-Faults breit abgedeckt.
- Single Owner, kein Dual Write, Decimal-Economics, Legacy exit-only, Atomic V2
  samt Loss Cluster, Execution-Control-Parität, Guard-/Exit-Sicherheit,
  Aktivierungslocks, Datei-Scope und Nichtfreigaben stimmen mit den geprüften
  normativen Autoritäten überein.
- Windows bleibt ohne separat reviewte suspend-aware Kernel-Self-Death-Primitive
  ausdrücklich unsupported und fail closed.
- Die Spezifikation enthält keinen Selbsthash-Zyklus. Implementierung,
  ENFORCED-Aktivierung, Exchange und Live bleiben ausdrücklich nicht freigegeben.

---

## 6. Gesamturteil

```text
REREVIEW_RESULT: NOT_READY
BLOCKER: 2
HIGH: 0
MEDIUM: 0
LOW: 0
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Revision 13 schließt V12-B1 im ursprünglichen Pipe-Write-Sinn. Die zwei neuen
Blocker verhindern jedoch eine lückenlose terminale Fail-stop- und
Restart-Recovery-Aussage. Vor einem READY sind eine neue eindeutig versionierte
Spezifikationsrevision, ein Resolution-Record und ein erneutes unabhängiges
Review des vollständigen neuen Hashes erforderlich.
