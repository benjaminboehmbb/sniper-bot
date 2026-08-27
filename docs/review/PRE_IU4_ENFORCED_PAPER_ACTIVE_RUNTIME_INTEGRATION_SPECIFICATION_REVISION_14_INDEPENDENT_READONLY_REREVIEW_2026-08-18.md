# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-14 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-14-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel SHA-256:** `ec7e86923e1fc440208dd0b65f4215e22badd62dcfb69e2c0d2e17b7457293e5`
- **Reviewziel Zeilen:** `3293`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_13_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `bc26a687f48c601999d6f27840da1326012bad2142a937045d80e86481edcd0f`
- **Controlling Resolution Zeilen:** `269`
- **Controlling Independent V13 Review:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_13_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md`
- **Controlling Independent V13 Review SHA-256:** `e5cc26270b743d7e2cad211c8322d4b197e92f6e65de344f46b3ea52449f06b1`
- **Controlling Independent V13 Review Zeilen:** `224`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik und Aussagegrenze

`AGENTS.md`, das vollständige Reviewziel, die vollständige controlling
Resolution und der vollständige unabhängige V13-Review-Record wurden
zeilenweise gelesen. Ergänzend wurden die normativen Autoritäten
`LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
`LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md`,
`PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md` sowie die einschlägigen
L1-C-/L1-D-Regeln gegen die behaupteten Preservation-Grenzen geprüft.

Die Prüfung war statisch, unabhängig und adversarial. Sie modellierte
insbesondere reale Prozessadressraum- und Seccomp-Grenzen, Acquire-/Release-
und CAS-Linearization, Halt exakt nach Latch-CAS, Last-Approval-/`timer_settime`-
Races, Whole-child-Stop, alle sechs Close-Nachrichten, Nonblocking-Socket- und
ACK-Fehler, Worker-Append-Autorität, HUP/Trip gegen PREPARE/CLOSED/COMMIT,
Startup-Klassifikation, PIDFD-/Writer-Referenzgrenzen, Capability-/Fault-/
Preflight-Abdeckung, Versionsfamilien und Nichtfreigaben.

Es wurden keine Runtime-, R3-, Research- oder Git-Mutationen und keine Tests mit
Writes ausgeführt. `scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch
verändert. Reviewziel, controlling Resolution und V13-Review-Record wurden nicht
verändert. Angelegt wurde ausschließlich dieser ausdrücklich beauftragte
Review-Record.

---

## 2. Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| V14-B1 | BLOCKER | OPEN | `TerminalTripLatchV2` liegt writable im gemeinsamen Trading-Prozessadressraum. Ein beliebiger bereits vorhandener Trading-/Python-/Native-TID kann TRIPPED ohne Syscall wieder auf CLEAR speichern; Seccomp und gebundene Callsite-Hashes erzwingen die behauptete Irreversibilität nicht. |
| V14-B2 | BLOCKER | OPEN | Die normative Broker-Rollenfiltermatrix kann den vorgeschriebenen Close-Pfad nicht ausführen: PrepareAck-`recvmsg` ist nicht erlaubt, Broker→Guardian-Approval-`sendmsg` fehlt, und die behauptete CommitAck-Payloadbeschränkung ist mit klassischem Seccomp nicht prüfbar. |
| V14-H1 | HIGH | OPEN | Die genau-einmaligen nonblocking Close-Sends und insbesondere ein verlorenes Prepare-ACK besitzen keine totale Fehlerzustandsmaschine; vor CLOSED können Renewals unbegrenzt weiterlaufen, obwohl der Text für „irgendein ACK fehlt“ fälschlich CLOSED voraussetzt. |

```text
BLOCKER: 2
HIGH: 1
MEDIUM: 0
LOW: 0
```

---

## 3. Findings

### V14-B1 — Die lokale Trip-Latch-Irreversibilität ist nicht prozessintern erzwingbar

**Evidenz:**

- Zeilen 347–351 verlangen `terminal_trip_latch_reset_allowed=false`, einen
  unabhängigen Shim-Observer und höchstens 1 ms Poll-Intervall.
- Zeilen 930–939 legen die einzige Latch-Instanz als writable
  `_Atomic uint64_t` in **demselben** Prozessadressraum aller Trading-/Python-
  TIDs und des Shim an. Als Writer-Grenze werden lediglich gebundene Callsite-
  und Binärhashes genannt; getrennte Mapping-Rechte oder eine
  prozessübergreifende Write-Authority existieren für diesen Latch nicht.
- Zeilen 941–961 machen gerade den beobachteten Wert TRIPPED zur Voraussetzung
  dafür, dass der Shim Approvals dauerhaft verwirft und keine weitere
  Timerverlängerung ausführt.
- Zeilen 1154–1165 und 2402–2412 verwenden denselben Latch als unmittelbare
  fachliche Side-Effect-Sperre und als vom Gewinner-TID unabhängige Brücke zum
  Lease-Fail-stop.
- Zeilen 2295–2315 sperren Syscalls, Mapping-Änderungen und FD-Autorität, können
  aber keinen gewöhnlichen Store eines bereits existierenden TID auf bereits
  writable Prozessspeicher filtern. Ein Speicherstore tritt nicht in Seccomp
  ein.
- Zeilen 3231–3241 erklären den 1-ms-Observer dennoch zum vollständigen
  Implementierungsnachweis gegen verlorene Notifications und PIDFD-Fehler.

**Konkreter Angriffspfad:**

1. Ein Trading-TID gewinnt wie vorgeschrieben die release-CAS
   `CLEAR→TRIPPED` und wird exakt danach, vor dem ersten Self-PIDFD-Syscall,
   angehalten.
2. Ein anderer bereits vorhandener TID desselben Trading-Prozesses speichert
   atomar oder roh `CLEAR` an die gebundene Latch-Adresse. Das benötigt weder
   Syscall, neuen Task, neue Map noch FD und wird von keinem beschriebenen
   Seccomp-Filter gesehen.
3. Control Word bleibt RUNNING, weil weder PIDFD, HUP noch Broker-CAS erreicht
   wurde. Guardian und Broker erzeugen deshalb weiter gültige Renewals und
   Approvals.
4. Der Shim liest wieder CLEAR, verwirft Approvals nicht dauerhaft und darf den
   Timer weiter verlängern. Die fachlichen Gates lesen ebenfalls CLEAR und
   können weitere Side Effects zulassen.
5. Damit werden sowohl die one-way-Monotonie als auch die V13-B1-Resolution und
   `TERMINAL_FAILSTOP_ASSERTED` umgangen.

Die bloße Bindung erwarteter Callsite-Hashes ist dieselbe thread-lokale
Vertrauensannahme, die bei V8-H1 für eine writable Control-Word-Map ausdrücklich
als nicht OS-erzwingbar verworfen wurde. Für einen sicherheitsentscheidenden,
vom untrusted/komplexen Trading-Prozess les- und schreibbaren Latch benötigt die
Spezifikation entweder eine tatsächlich getrennte Write-/Monotonie-Autorität
oder eine explizit engere, mit den bisherigen adversarialen Raw-Operation-
Annahmen kompatible und unabhängig reviewte Vertrauensgrenze.

### V14-B2 — Broker-Filter und sechs Close-Nachrichten widersprechen einander

**Evidenz:**

- Zeilen 793–798 binden alle sechs Close-Nachrichtentypen mit exakten Längen,
  Typkonstanten und Peerwegen.
- Zeilen 1188–1196 verlangen, dass der Broker
  `TerminalWorkerClosePrepareAckV1` empfängt und validiert, bevor er
  RUNNING→CLOSED linearisiert.
- Zeilen 1206–1218 verlangen danach CommitRequest, CommitAck sowie je eine
  `TerminalBrokerCloseCommitApprovalV1` an Shim **und Guardian** über die
  jeweiligen Socketkanäle.
- Zeilen 2276–2282 erlauben dem Broker dagegen `sendmsg` nur an Shim und Worker
  und `recvmsg` am Worker-FD ausdrücklich ausschließlich für
  `TerminalWorkerCloseCommitAckV1`. Weder PrepareAck-Receive noch
  Broker→Guardian-Approval-Send ist enthalten. Der erwähnte Guardian-Eventfd-
  `write` kann die gebundene fixed-size Approval mit PREPARE-/COMMIT-/CLOSED-
  Identitäten nicht ersetzen.
- Zeilen 1132–1134 erkennen zutreffend an, dass ein klassischer Seccomp-Filter
  einen `msghdr`-Payload nicht dereferenzieren kann. Daher kann die Filterregel
  „ausschließlich CommitAckV1“ technisch nur den skalaren Worker-FD erlauben,
  nicht aber CommitAck von PrepareAck unterscheiden; bei wörtlicher Umsetzung
  fehlt PrepareAck, bei FD-only-Umsetzung ist die behauptete Filtergrenze falsch.
- Die Rollen- und Dateiscope-Zusammenfassungen in Zeilen 2255–2259 und
  2703–2705 führen den Broker weiterhin nur als Sender von Renewal Approvals und
  Worker-KILL-Requests und schließen die neue Close-Autorität nicht in den
  ausführbaren Rollenvertrag ein.

**Konkreter Ausführungspfad:**

1. Guardian sendet einen gültigen OrderlyCloseRequest; Broker sendet den
   PrepareRequest und Worker persistiert PREPARE.
2. Der Worker sendet den obligatorischen PrepareAck. Die normative Broker-
   Allowlist besitzt hierfür keinen zulässigen Receive-Pfad. Bei wörtlicher
   Default-deny-Umsetzung endet der Close vor der CLOSED-CAS.
3. Wird die Regel stattdessen als bloße Worker-FD-Freigabe umgesetzt, kann
   Seccomp die behauptete CommitAck-Exklusivität nicht leisten; die tatsächliche
   Authority verschiebt sich unbeschrieben in Broker-Userspace-Validierung.
4. Selbst wenn CLOSED und durable COMMIT erreicht würden, besitzt der Broker
   keinen erlaubten `sendmsg` zum Guardian. Ohne die gebundene Approval darf der
   Guardian den Child-Exit nicht autorisieren.

Damit ist `RuntimeSessionCloseProtocolV2` in der verbindlichen Rollenfiltermatrix
nicht implementierbar. Eine Korrektur muss die vollständige FD-/Richtungs-
Allowlist für beide Worker-ACKs und beide Approval-Empfänger angeben und
Payload-/Type-Prüfungen ausdrücklich dem jeweiligen Userspace-Empfänger statt
klassischem Seccomp zuordnen.

### V14-H1 — Nonblocking Close-Transport und ACK-Verlust sind nicht total geordnet

**Evidenz:**

- Zeilen 1178–1186 verlangen für Guardian→Broker und Broker→Worker jeweils genau
  einen fixed-size, nonblocking Send, definieren aber keine Returnwertmaschine
  für `EAGAIN`, `EINTR`, weitere Sendfehler beziehungsweise Peer-Close.
- Zeilen 1188–1196 erlauben CLOSED erst nach PrepareAck. Vor diesem ACK bleibt
  das Control Word RUNNING.
- Zeilen 904–925 lassen in RUNNING weiterhin alle 10 ms Renewal-CAS und
  Approvals zu; ein fehlender PrepareAck stoppt diese nicht.
- Zeilen 1206–1218 spezifizieren auch CommitRequest, CommitAck und zwei
  Approvals als exactly-once Sends, wiederum ohne vollständige Send-/Receive-
  Fehlerfolge.
- Zeilen 1220–1223 behaupten für jedes fehlende ACK, wegen CLOSED würden keine
  Renewals mehr entstehen und PREPARE bliebe ohne COMMIT. Das trifft auf ein
  fehlendes **PrepareAck** nicht zu, weil CLOSED gerade noch nicht erreicht ist.
  Für ein nach durablem COMMIT verlorenes **CommitAck** ist außerdem COMMIT
  bereits vorhanden und wird nach Zeilen 830–838 beim Startup als clean
  klassifiziert; auch dort ist „PREPARE ohne COMMIT“ falsch.
- Die 10.000-Trial-Matrix in Zeilen 1295–1312 und die 32-Phasen-Probes in Zeilen
  1369–1391 enthalten Crash/Trip vor CLOSED, COMMIT-Writefehler und Crash nach
  COMMIT, aber keinen expliziten Queue-full-/EAGAIN-Fall und keinen getrennten
  Verlust von PrepareAck, CommitAck oder einer der beiden finalen Approvals.

**Konkreter Fehlerpfad:**

1. Der Worker hat PREPARE durable geschrieben, aber sein nonblocking
   PrepareAck-Send liefert etwa `EAGAIN`, oder der Ack geht mit einem Peer-
   Fehler verloren.
2. Der Broker darf ohne Ack nicht auf CLOSED wechseln. Der Guardian hat seinen
   genau einmaligen Request bereits verbraucht; weder Retry, Timeout noch
   terminale Eskalation ist spezifiziert.
3. Control Word bleibt RUNNING. Der gesunde Guardian/Broker/Shim-Pfad renewt
   den Timer weiter, während das Trading-Child zwar gegatet, aber unbegrenzt
   alive bleibt. Die in Zeilen 1220–1223 behauptete CLOSED-/Lease-Expiry-Folge
   wird nie erreicht.
4. Ein analog verlorenes CommitAck führt dagegen nach bereits durablem COMMIT
   zu CLOSED plus Timer-Expiry und einem beim Startup als clean geltenden
   Ledger. Dieser andere Zustand wird vom pauschalen Text nicht unterschieden.

Das ist kein neuer Trading-Side-Effect-Bypass wie V14-B1, aber ein offener
Runtime-Close- und Fault-Injection-Vertrag. Erforderlich sind pro Nachricht eine
vollständige endliche Return-/Timeout-/Peer-Close-Zustandsmaschine, eindeutige
idempotente Retry- oder terminale Eskalationsregeln und getrennte Trials für
jede verlorene Request-/Ack-/Approval-Grenze.

---

## 4. Mapping der Vorfindings

| Vorfinding | Ergebnis in Revision 14 | Begründung |
|---|---|---|
| V13-B1 | NICHT END-TO-END GESCHLOSSEN / durch V14-B1 offen | Release-CAS, Acquire-Observer, 1-ms-Poll und Last-Expiry-Race schließen den ursprünglichen Gewinner-TID-Stall nur, solange TRIPPED monoton bleibt. Die gemeinsame writable Prozessadresse besitzt keine durchsetzbare Reset-Sperre. |
| V13-B2 | STRUKTURELL CLOSED / Ausführung durch V14-B2 und V14-H1 blockiert | PREPARE ist nicht clean; CLOSED liegt vor dem einzigen clean machenden durable COMMIT. Damit kann ein Trip vor CLOSED nicht mehr durch ein vorab clean klassifiziertes Record verdeckt werden. Der neue Close-Pfad ist jedoch wegen Kanal-/Filter- und Fehlersemantik nicht implementation-ready. |
| V12-B1 | CLOSED / preserved | Die Liveness-Pipe bleibt dauerhaft leer; kein Pipe-Read/-Write/-Datentransfer und damit kein Userbuffer-, Pipe-Page-, Reclaim- oder temporärer Writerpfad liegt im Terminal-Sicherheitsweg. |
| V11-B1 | CLOSED / obsolet | Freie Userbuffer und Pipe-Write-`struct file`-Referenzen bleiben aus dem Sicherheitsweg entfernt. |
| V11-M1 | CLOSED / preserved | I2 und Completion-Gates referenzieren konsistent Profile V8, Session V9, Guardian V7, Broker V4, Shim V5, Capability V7, SelfKill V2, Latch V2 und CloseProtocol V2. |
| V10-B1 | CLOSED / preserved | Feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS, Post-Ready-Task-/FD-/Referenzsperren und letzte Writer-Inventur bleiben normativ. |
| V9-B1 | CLOSED / preserved | Alle zurückkehrenden PIDFD-Fehler erreichen ohne Retry Self→Guardian→Broker→den einmaligen Liveness-Close; Pipe-Datentransfer bleibt ausgeschlossen. |
| V9-M1 | CLOSED / preserved | `MFD_ALLOW_SEALING`, initiale Seals 0 und die exakten `F_SEAL_FUTURE_WRITE`-/`F_SEAL_SEAL`-Transitionen bleiben vollständig. |
| V8-H1 | im engen Control-Word-/Worker-Scope CLOSED; Sicherheitsprinzip durch V14-B1 regressiert | Der Broker bleibt alleiniger Control-Word-Writer, Trading besitzt nur RO-Control-Map und keinen Worker-FD, und Worker prüft den KILL-CAS receiverseitig. V14-B1 führt jedoch erneut eine sicherheitsentscheidende writable Same-Process-Authority ein. |
| ältere B2/M1/RM1/RB2/RB3/NH1/NH2/NM1/NM2 | PRESERVED | DIRECT-/RECOVERED-Provenance, NONE-Sentinels, neue RESTART_ONLY-Consumption, Authority-/Journal-Roots, Atomic V2/Loss Cluster, Single Owner, Legacy exit-only, Execution-Control-Parität und Scope-/Freigabegrenzen wurden nicht regressiert. |

---

## 5. Positive Bestätigungen ohne Finding

- Die eingefrorenen HEAD-, Spec-, Resolution- und V13-Review-Identitäten sowie
  alle drei Zeilenzahlen stimmten bei Reviewbeginn und unmittelbar vor Anlage
  dieses Records exakt.
- Unter der Annahme eines monotonen Latch ist die release-CAS/acquire-Load-
  Kopplung kohärent. Der unabhängige 1-ms-Shim-Observer, die Prüfung vor Approval
  und unmittelbar vor `timer_settime` sowie die höchstens 25 ms alte absolute
  Expiry schließen das V13-Preemption-Fenster konzeptionell.
- Ein Whole-child-Stop hält zwar auch den Shim an, verhindert aber keine
  kernel-seitige Timer-Expiry; tatsächliches Reaping wird weiterhin korrekt
  nicht zeitlich behauptet.
- PREPARE→Broker-CLOSED→durable COMMIT ordnet die persistente Clean-
  Klassifikation grundsätzlich richtig. HUP/Trip vor CLOSED kann kein cleanes
  COMMIT erzeugen; CLOSED ohne COMMIT bleibt unclosed.
- Kein Pipe-Read, Pipe-Write oder sonstiger Datentransfer ist im terminalen
  Sicherheitsweg autorisiert. Self-PIDFD-`SIGKILL` bleibt der erste Kernelaufruf
  nach dem Latch; alle zurückkehrenden Fehlerklassen erreichen Guardian, Broker
  und den einmaligen Linux-Close.
- Die PIDFD-Aufrufe sind mit klassischen Seccomp-Skalarprüfungen für FD, Signal,
  Null-`siginfo` und Flags technisch ausdrückbar. Ziel-/Startzeitbindung,
  Signal-0-Probe, CLOEXEC, feste Tasktopologie und FD-Reuse-Sperre ergänzen die
  Identitätsgrenze.
- Es wurde kein neuer konkreter zweiter Liveness-Writerpfad gefunden. Fork/
  Clone/Files-Table-Split, Duplication, SCM_RIGHTS, procfd, pidfd_getfd,
  io_uring, epoll-Halter und neue FD-Erzeugung bleiben gesperrt.
- Renewal-vor-Trip und Trip-vor-Renewal sind im globalen Control Word sauber per
  CAS linearisiert; stale Approvals dürfen nur die bereits vorvalidierte
  absolute Expiry setzen. Memfd-Bootstrap, sole-RW-Broker-Map und Seal-
  Zustandsmaschine bleiben technisch kohärent.
- Capability V7 ist weiterhin ein endlicher, hashgebundener Envelope und
  behauptet keine universelle Scheduler- oder Reap-Garantie. Abgesehen von
  V14-B1/V14-B2/V14-H1 sind Signal-, HUP-, Renewal-, Worker-, Map-/Seal- und
  Topologie-Faults breit und deterministisch abgedeckt.
- Die aktuelle Versionsfamilie ist in Runtime-Profil, Session Envelope, I2,
  Dateiscope, Implementation-Complete-Gates und Closing Step konsistent. Die
  Spezifikation enthält keinen Selbsthash-Zyklus.
- Single Owner, kein Dual Write, Decimal-Economics, Legacy exit-only, Atomic V2
  samt Loss Cluster, Execution-Control-Parität, Guard-/Exit-Sicherheit,
  Aktivierungslocks, Datei-Scope und Nichtfreigaben stimmen mit den geprüften
  normativen Autoritäten überein.
- Windows bleibt ohne separat reviewte äquivalente Kernelprimitive unsupported
  und fail closed. Implementierung, ENFORCED-Aktivierung, Exchange und Live
  bleiben ausdrücklich nicht freigegeben.

---

## 6. Gesamturteil

```text
REREVIEW_RESULT: NOT_READY
BLOCKER: 2
HIGH: 1
MEDIUM: 0
LOW: 0
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Revision 14 korrigiert die Grundideen beider V13-Blocker: ein unabhängiger
Observer ersetzt den Fortschrittsbedarf des Gewinner-TID, und ausschließlich
ein nach CLOSED durable gewordener COMMIT klassifiziert die Session als clean.
Die neue lokale Latch-Autorität ist jedoch nicht irreversibel erzwingbar, die
Broker-Filtermatrix kann den vorgeschriebenen Close-Pfad nicht ausführen und
die nonblocking Close-/ACK-Fehlerfolge ist nicht vollständig. Vor einem READY
sind eine neue eindeutig versionierte Spezifikationsrevision, ein Resolution-
Record und ein erneutes unabhängiges Review des vollständigen neuen Hashes
erforderlich.
