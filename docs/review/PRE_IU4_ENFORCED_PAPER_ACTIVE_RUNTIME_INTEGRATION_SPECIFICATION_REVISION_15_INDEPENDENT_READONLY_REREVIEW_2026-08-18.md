# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-15 INDEPENDENT READ-ONLY REREVIEW

- **Datum:** 2026-08-18
- **Reviewtyp:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-15-INDEPENDENT-READONLY-REREVIEW`
- **Kanonisches Repository:** `/home/benja/projects/sniper-bot`
- **Repository-Root verifiziert:** `/home/benja/projects/sniper-bot`
- **HEAD:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **main:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **origin/main:** `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`
- **Divergenz:** `main` ist exakt sechs Commits voraus (`0 6` für `origin/main...main`)
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Reviewziel-Revision:** `15`
- **Reviewziel SHA-256:** `34637e2e51b63f8d386d0eb04acf74bd34a1e805eaea317e156cd87f5eece25a`
- **Reviewziel Zeilen:** `3558`
- **Controlling Resolution:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_14_REREVIEW_RESOLUTION_2026-08-18.md`
- **Controlling Resolution SHA-256:** `2fb968c6c4f832f5d1b37a0a9b56b7988b5c158b45c519583a167df92bebd67e`
- **Controlling Resolution Zeilen:** `390`
- **Controlling V14 Review:** `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_14_INDEPENDENT_READONLY_REREVIEW_2026-08-18.md`
- **Controlling V14 Review SHA-256:** `ce5d0f80105ba5a25f7dd33177299d80f1d494143a67ebe7d433776d05f803d3`
- **Controlling V14 Review Zeilen:** `299`
- **Gesamturteil:** `NOT_READY`

---

## 1. Methodik und Aussagegrenze

`AGENTS.md`, das vollständige Reviewziel, die vollständige controlling
Resolution und der vollständige unabhängige V14-Review-Record wurden gelesen.
Ergänzend wurden die höherrangigen Autoritäten
`LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
`LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md`, `LIVE_DESIGN_L0_STATE_MODEL.md`,
`LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md`,
`LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md`,
`LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md` und
`PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md` gegen die
Preservation-Behauptungen geprüft. Die einschlägigen Vorfinding-Records wurden
zur ursprünglichen Bedeutung von V13-B2, V12-B1, V11-B1/M1, V10-B1,
V9-B1/M1 und V8-H1 herangezogen.

Die Prüfung war statisch, unabhängig und adversarial. Für die neue V15-Grenze
wurden insbesondere die realen Linux-Verträge für Seccomp-Filterstapel,
`SECCOMP_RET_USER_NOTIF`, `NEW_LISTENER`, `TSYNC`, Notification-Abbruch durch
Signale, `SECCOMP_IOCTL_NOTIF_RECV|ID_VALID`, Filterpräzedenz, Unix-
`SOCK_SEQPACKET`, `SO_PASSCRED`, `SCM_RIGHTS` und `MSG_CMSG_CLOEXEC` geprüft.
Primäre technische Referenzen waren die
[Linux-Kernel-Seccomp-Dokumentation](https://docs.kernel.org/userspace-api/seccomp_filter.html),
die Linux-man-pages zu
[`seccomp(2)`](https://man7.org/linux/man-pages/man2/seccomp.2.html),
[`seccomp_unotify(2)`](https://man7.org/linux/man-pages/man2/seccomp_unotify.2.html),
[`unix(7)`](https://man7.org/linux/man-pages/man7/unix.7.html) und
[`recvmsg(2)`](https://man7.org/linux/man-pages/man2/recvmsg.2.html).

Modelliert wurden der Halt nach Notification, der Notification-Abbruch vor und
nach Broker-Receive, der Halt nach Syscall-Return und vor dem ersten Fallback,
Broker-Stall vor/nach Control-Word-CAS, Whole-child-Stop, Listener-/Filter-
Vererbung, alle sechs Close-Typen, beide ACKs, beide Approval-Empfänger, alle
ControlWord-V3-Stufen, nonblocking Fehler, absolute Deadlines, Retries,
Duplikate, Crashes und Startup-Klassifikation.

Es wurden keine Runtime-, R3-, State-, Workstation-, Scheduler-, Research- oder
Git-Mutationen und keine Tests mit Writes ausgeführt. Das ausdrücklich
ausgeschlossene `scripts/build_rcc002_spec_bundle.py` wurde weder gelesen noch
verändert oder ausgeführt. Fremde untracked Artefakte, Reviewziel und
Resolution-Record blieben unangetastet. Einzige zulässige Mutation ist dieser
neu angelegte Review-Record.

---

## 2. Finding-Übersicht

| ID | Severity | Status | Kurzbefund |
|---|---|---|---|
| V15-B1 | BLOCKER | OPEN | Eine `SECCOMP_RET_USER_NOTIF`-Notification ist vor Broker-Receive durch ein Signal abbrechbar. Der dadurch zurückkehrende Request-TID kann vor dem Fallback gestoppt werden, während Control Word RUNNING, Broker-Renewals und andere Trading-TIDs weiterlaufen. Die behauptete OS-monotone Trip-Grenze und V14-B1-Closure sind damit nicht end-to-end belegt. |
| V15-H1 | HIGH | OPEN | Die Rollenmatrix behauptet `SCM_RIGHTS` default-deny, obwohl Seccomp `msghdr` nicht dereferenziert und `recvmsg` den übertragenen Open-File-Description-Referenz bereits in die Empfänger-FD-Tabelle installiert, bevor Userspace sie ablehnt. Ein totaler Dispose-/Close-Vertrag fehlt und kollidiert mit den Close-Verboten der Rollenfilter. |

```text
BLOCKER: 1
HIGH: 1
MEDIUM: 0
LOW: 0
```

---

## 3. Findings

### V15-B1 — Signalabbruch kann die angeblich monotone Kernel-Notification löschen

**Evidenz im Reviewziel:**

- Zeilen 359–365 binden den Filter exakt an
  `SECCOMP_FILTER_FLAG_NEW_LISTENER`; eine Signal-/Notification-Abbruchmaschine
  oder eine bindende Signalmaske/-disposition ist nicht Teil des Profils.
- Zeilen 980–1012 behaupten, der Kernel erzeuge mit Syscall-Eintritt eine vom
  Trading-Adressraum nicht löschbare Notification. Der Broker behandelt nur
  eine erfolgreich empfangene passende Notification und einen anschließend
  ungültigen ID als Trip.
- Zeilen 1022–1030 nennen den Request nach Kernelannahme ausdrücklich
  „OS-monoton“ und lassen andere Trading-TIDs bis zur Broker-CAS allein über das
  weiterhin RUNNING lesende Control Word zu.
- Zeilen 1143–1176 legen Fallbacks erst **nach Rückkehr** des intercepteten
  Self-PIDFD-Aufrufs in denselben Request-TID. Es existiert kein unabhängiger
  Observer für das Fenster nach Rückkehr und vor Guardian-PIDFD-Fallback.
- Zeilen 1355–1361 und 2499–2515 erlauben dem Broker nur den normalen
  epoll/`NOTIF_RECV|ID_VALID`-Pfad. `NOTIF_RECV`-`ENOENT`/`EINTR` nach einer
  abgebrochenen Pending-Notification und ein vor Receive vollständig
  verschwundener Event besitzen keine terminale Klassifikation.
- Zeilen 1479–1484, 1522–1524, 1552–1557, 1601–1614 und 3273–3277 testen den
  Halt nach erzeugter Notification bei erhaltener Broker-Sichtbarkeit, nicht
  den Linux-Fall „Notification durch Signal abgebrochen, Syscall zurückgekehrt,
  Request-TID vor Fallback angehalten“.

**Reale Linux-Semantik:**

Die Kernel-Dokumentation beschreibt den notifier-wartenden Task als durch
Signale unterbrechbar; die Notification kann dadurch abgebrochen werden.
`SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV` schützt nicht den hier entscheidenden
Zeitraum: Nichtfatale Signale werden erst **nach** erfolgreichem Receive durch
den Supervisor zurückgestellt, während Signale vor Receive normal behandelt
werden. `seccomp_unotify(2)` nennt für `NOTIF_RECV` ausdrücklich den Fall, dass
der Zieltask während Notification-Erzeugung getötet oder sein blockierter
Syscall durch einen Signalhandler unterbrochen wurde. Bei `SA_RESTART` kann eine
neue Notification entstehen; ohne einen solchen vollständigen, gebundenen
Vertrag darf sie nicht als garantiert gelten.

**Konkreter Ausführungspfad:**

1. Ein Trading-TID ruft als ersten Kernelaufruf den gebundenen
   `pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)` auf. Der Filter erzeugt eine
   Pending-User-Notification; der Broker hat sie noch nicht per
   `SECCOMP_IOCTL_NOTIF_RECV` übernommen.
2. Ein nichtfataler, behandelte Signal unterbricht den signal-interruptiblen
   Wait. Der Kernel bricht die Notification ab. Je nach Disposition kehrt der
   Syscall zurück oder wird neu gestartet; V15 bindet weder Signalmaske,
   Disposition noch eine totale Abbruch-/Restart-Zustandsmaschine.
3. Im Returnfall wird der Request-TID unmittelbar vor dem ersten
   Guardian-PIDFD-Fallback angehalten. Dies ist derselbe Fortschrittsverlust,
   den die Spezifikation für andere Post-Linearization-Fenster ausschließen
   will.
4. Der Broker besitzt keine empfangene Notification und kann bei vollständig
   verschwundenem Event weder Argumente validieren noch TERMINATING setzen.
   Control Word bleibt RUNNING; Guardian und Broker bleiben gesund und erzeugen
   weitere Renewals/Approvals; der Shim verlängert den Timer.
5. Andere Trading-TIDs lesen RUNNING und dürfen weitere Side Effects beginnen.
   Weder PIDFD-Fallback, Liveness-HUP noch Lease-Expiry ist erzwungen.

Damit ist „Kernelannahme“ nicht der behauptete irreversible Request-
Linearization-Point. Eine Resolution benötigt eine tatsächlich totale
Signal-/Notification-Abbruchsemantik einschließlich des pre-Receive-Fensters,
Broker-Receive-Fehlern, Restart/Duplicate-Fällen und Halt unmittelbar nach jeder
möglichen Rückkehr, mit eigener Fault-/Capability-/Startup-Evidenz. Eine bloße
`ID_VALID`-Prüfung nach erfolgreichem Receive oder allein
`WAIT_KILLABLE_RECV` schließt den beschriebenen Pfad nicht.

### V15-H1 — Ancillary-FD-Ablehnung erfolgt erst nach einer FD-Tabellenmutation

**Evidenz im Reviewziel:**

- Zeilen 1329–1342 definieren sechs feste `SOCK_SEQPACKET`-Kanäle mit
  `SO_PASSCRED` und verlangen daher einen Ancillary-Empfangspuffer.
- Zeilen 1343–1353 erklären `SCM_RIGHTS` im Rollenfilterabschnitt zu
  default-deny, obwohl derselbe Vertrag `sendmsg`/`recvmsg` nur anhand fester FDs
  und skalarer Flags filtern kann.
- Zeilen 1363–1368 erkennen korrekt an, dass klassisches Seccomp `msghdr` und
  Payload nicht dereferenziert, und verschieben die Ancillary-Prüfung in den
  Empfänger-Userspace. Zu diesem Zeitpunkt ist ein empfangener `SCM_RIGHTS`-FD
  aber bereits installiert.
- Zeilen 2495–2525 verbieten insbesondere Guardian und Broker `close` und geben
  auch für Shim/Worker keinen normativen Dispose-Pfad für unerwartet installierte
  FDs an. `MSG_CMSG_CLOEXEC` setzt nur CLOEXEC und verhindert die Installation
  nicht.
- Zeilen 1084–1124, 1469–1475, 1563–1569 und 3295–3306 verlangen zugleich, dass
  nach Ready kein `SCM_RIGHTS`-Transfer, keine neue FD-Nummer und keine neue
  Kernelreferenz entstehen darf.
- Zeilen 1515–1530, 1603–1614 und 3319–3330 injizieren fremde Ancillary-Daten,
  verlangen aber nicht den Nachweis, dass alle bereits empfangenen Deskriptoren
  geschlossen wurden und keine Open-File-Description-Referenz oder Sperre
  fortbesteht.

**Reale Linux-Semantik und Auswirkung:**

`unix(7)` definiert `SCM_RIGHTS` semantisch als Duplikation einer Referenz auf
eine Open File Description in die FD-Tabelle des Empfängers. Nur wegen zu
kleinem/fehlendem Controlbuffer oder `RLIMIT_NOFILE` überschüssige FDs schließt
der Kernel automatisch. Ein in den bereitgestellten Buffer passender FD bleibt
installiert, auch wenn Userspace danach Type, Credentials oder Ancillary-Inhalt
als ungültig klassifiziert. `MSG_CMSG_CLOEXEC` ändert nur das Close-on-exec-Bit.

Damit kann ein malformed Paket eines gebundenen Peers vor der
Userspace-Ablehnung eine zusätzliche Listener-, PIDFD-, Socket-, Journal- oder
Lock-Referenz im Empfänger erzeugen. Das widerspricht der festen post-Ready
FD-/Writer-Referenzgrenze; insbesondere ist „vor jeder Mutation validieren“ für
diese Kernelmutation sachlich falsch. Die Spezifikation benötigt entweder eine
nachweislich alle Rights durch den Kernel verwerfende Receive-Bufferstrategie
oder einen vollständigen, seccomp-kompatiblen Dispose-Vertrag für jeden
empfangenen FD, einschließlich CTRUNC/mehrerer CMSGs, Close-Fehlern, Prozesscrash
und Negativtests der Postmortem-FD-/Lock-Inventur. Erst dann ist die behauptete
skalare Seccomp-/Userspace-Trennung end-to-end ausführbar.

---

## 4. Mapping der controlling Findings

| Vorfinding | Ergebnis in Revision 15 | Begründung |
|---|---|---|
| V14-B1 | NICHT END-TO-END GESCHLOSSEN / durch V15-B1 offen | Writable Same-Process-Latch und Post-CAS-Stall sind entfernt. Die Ersatzgrenze ist jedoch vor Broker-Receive signal-abbrechbar; nach Syscall-Return hängt Fail-stop wieder vom Fortschritt desselben Request-TID ab. |
| V14-B2 | STRUKTURELL WEITGEHEND GESCHLOSSEN / durch V15-H1 nicht vollständig implementation-ready | Beide ACKs, beide Approval-Empfänger und sechs Typen sind vorhanden; Seccomp wird für Payload nicht mehr beansprucht. Die Ancillary-FD-Kernelmutation vor Userspace-Validierung besitzt aber keinen totalen Cleanup-Vertrag. |
| V14-H1 | CLOSED / preserved | CLOSING/CLOSED/COMMITTED/CLOSED_FAILSTOP, absolute Deadlines, byteidentische Retries, idempotente Worker-Mutationen, getrennte Prepare-/CommitAck-Verlustfolgen und polling-basierte Approval-Konvergenz bilden eine endliche Close-FSM. |

---

## 5. Preservation der älteren Findings und Grundverträge

| Vorfinding/Vertrag | Ergebnis | Evidenz |
|---|---|---|
| V13-B2 | CLOSED / preserved | Zeilen 857–874 und 1256–1318 lassen nur PREPARE → Broker-CLOSED → durable COMMIT clean werden; PREPARE oder CLOSED ohne COMMIT bleibt unclean. |
| V12-B1 | CLOSED / preserved | Zeilen 1032–1043 und 1126–1133 halten die Liveness-Pipe leer; im Terminal-Sicherheitsweg existiert kein Pipe-Read/-Write/-Datentransfer. |
| V11-B1 | CLOSED / obsolet | Kein frei wählbarer Userbuffer, `copy_from_user`, Pipe-Page- oder Write-`struct file`-Pfad liegt vor der fatalen Aktion. |
| V11-M1 | CLOSED / preserved | Zeilen 412–422, 3029–3039 und 3482–3515 verwenden konsistent die V15-Vertragsfamilie. |
| V10-B1 | CLOSED im ursprünglichen Writer-/Fork-Scope; V15-H1 ist neue Ancillary-Lücke | Feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS und enumerierte Post-Ready-Erzeugungssperren bleiben erhalten; unerwartete empfangene Rights sind separat durch V15-H1 offen. |
| V9-B1 | CLOSED für alle zurückkehrenden PIDFD-Ergebnisse; End-to-End durch V15-B1 offen | Zeilen 1143–1176 erhalten Self→Guardian→Broker→einmaligen Close ohne Retry. Offen ist der neue Halt nach signalbedingter Rückkehr der intercepteten ersten Stufe. |
| V9-M1 | CLOSED / preserved | Zeilen 907–941 binden `MFD_CLOEXEC\|MFD_ALLOW_SEALING`, initiale Seals 0 und beide exakten `F_ADD_SEALS`-Transitionen. |
| V8-H1 | CLOSED im Control-Word-/Worker-Scope | Broker bleibt alleiniger RW-Mapper/Writer, Trading besitzt nur RO und keinen Worker-FD; Worker prüft State, Sequenz und Peer receiverseitig. |
| Single Owner / No Dual Write | PRESERVED | Zeilen 227–266, 270–301 und 1980–2004 halten Legacy und Atomic PEE mode-spezifisch disjunkt. |
| Decimal / PEE Economics | PRESERVED | Zeilen 232–240, 2109–2231 und 2322–2385 halten Canonical Decimal Economics ohne Float-Roundtrip und ohne Fallback-Quantity. |
| Atomic V2 / Loss Cluster | PRESERVED | Zeilen 2142–2318 ordnen Entry Quote, Account, Loss Cluster, S4V2 und Cursor in gemeinsame Transaktionen. |
| Execution Control | PRESERVED | Zeilen 2057–2105 definieren pure Control, Triggerpriorität, OFF/SHADOW-Parität und keine synthetischen Opposing Intents. |
| Authority/Recovery/Genesis | PRESERVED | Ledger Tip und Authority Anchor bleiben getrennt; DIRECT/RECOVERED, NONE-Sentinels, RESTART_ONLY und journal-first Recovery bleiben explizit. |
| L0/L1 Kill/Restart | PRESERVED außer offenem V15-B1-Fail-stop | Kein Auto-Recovery, monotone Kill-Level, HARD/EMERGENCY-Abbruch und manuelle Restart-Autorisierung bleiben normativ; V15-B1 verhindert den vollständigen EMERGENCY-Nachweis. |

Es wurde kein weiterer konkreter Dual-Write-, Decimal-, Atomic-V2-, Loss-
Cluster-, Execution-Control-, Handoff-, Genesis-, Authority-Root- oder Startup-
Bypass gefunden. Whole-child-Stop ist konzeptionell fail-safe, weil der Shim
mitstoppt und der bereits armed Kernel-Timer weiterläuft. Ebenso sind
Post-Broker-CAS-Stalls fail-safe, weil ab TERMINATING keine Approval entsteht.
Diese positiven Befunde schließen V15-B1/V15-H1 nicht.

---

## 6. Gesamturteil und Nichtfreigaben

```text
REREVIEW_RESULT: NOT_READY
SPECIFICATION_REVISION: 15
BLOCKER: 1
HIGH: 1
MEDIUM: 0
LOW: 0
V14_B1_CLOSED: NO
V14_B2_CLOSED: NO
V14_H1_CLOSED: YES
V13_B2_CLOSED_STATUS_PRESERVED: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES_WITH_NEW_V15_H1_DISTINGUISHED
V9_B1_RETURN_PATH_PRESERVED: YES
V9_B1_END_TO_END_FAILSTOP: NO_DUE_TO_V15_B1
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

Revision 15 schließt die zuvor fehlenden Close-Kanäle und die endliche Close-
Transport-FSM im Kern. Sie beseitigt auch den writable In-Process-Latch.
Der neue Seccomp-Notification-Ersatz besitzt jedoch keine vollständige reale
Linux-Signalabbruchsemantik, und die Ancillary-FD-Grenze verwechselt Erkennung
nach `recvmsg` mit Verhinderung der bereits erfolgten FD-Tabellenmutation.
Mindestens eine neue eindeutig versionierte Spezifikationsrevision, ein
Resolution-Record und ein unabhängiges Re-Review des vollständigen neuen Hashes
sind erforderlich. Implementierung, IU4 ENFORCED, Exchange und Live bleiben
ausdrücklich nicht freigegeben.
