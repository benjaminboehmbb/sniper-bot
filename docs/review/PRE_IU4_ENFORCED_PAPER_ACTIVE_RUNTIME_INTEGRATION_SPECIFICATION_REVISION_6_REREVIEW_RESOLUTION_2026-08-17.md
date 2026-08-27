# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-6 REREVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REVISION-6 REREVIEW FINDINGS RESOLVED IN REVISION 7 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V6-Hash:** `d0781659f5ccfdf446473238b29c1a51fa2203179e368d431cb5e5ffd5a28d54`
- **V6-Resolution-Record:** `b4cdc8c698977628683b9681f68921b47235ef5d356419c452de4e867fb3f425`
- **Resolution-Zielhash V7:** `a9e10855a18bce9131863482ae1473f37d201576c193c7fc775e0fdfe6e0798f`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker, das High- und das Medium-Finding des
unabhängigen read-only Re-Reviews der Revision 6 konkreten normativen
Korrekturen in Revision 7 zu.

Es zertifiziert die Korrekturen nicht selbst. Alle Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V7-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V6-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V6_SHA256: d0781659f5ccfdf446473238b29c1a51fa2203179e368d431cb5e5ffd5a28d54
V6_RESOLUTION_SHA256: b4cdc8c698977628683b9681f68921b47235ef5d356419c452de4e867fb3f425
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 1
MEDIUM: 1
LOW: 0
```

| Finding | V6-Re-Review | V7-Resolution |
|---|---|---|
| B1 DIRECT-Genesis über Prozesswechsel | OPEN | Prozessinstanz-/Attempt-/Ephemeral-Nonce-Bindung und Crash-Negativtest |
| H1 Guardian-Stall und unbelegbare Reap-Deadline | OPEN | kernel-armed Self-Death-Lease, synchroner Side-Effect-Gate und ehrliche Termination-/Reap-Grenze |
| N1 falsche Reviewidentität | OPEN | Revision-7-Reviewziel und externe Hashbindung korrigiert |

Die zuvor geschlossenen Findings B2 und M1 blieben geschlossen. `RM1 Clean
Genesis` blieb ausschließlich wegen B1 offen; `RB2`, `RB3`, `NH1`, `NH2`,
`NM1` und `NM2` blieben geschlossen.

---

## 3. Resolution des Blockers

### B1 — DIRECT-Genesis-Ausnahme war nach Prozesswechsel wiederverwendbar

**Bestätigter Konflikt:** V6 band der DIRECT-COMMIT zwar an die ursprüngliche
Prozess-ID, verlangte beim späteren Ausnahmecheck aber keine Gleichheit mit der
aktuell laufenden Prozessinstanz. Nach Crash zwischen DIRECT-COMMIT und
`RUNTIME_SESSION_OPEN` hätte ein neuer Prozess denselben COMMIT weiterhin als
DIRECT ohne frühere Session sehen und die Erststartausnahme nutzen können.

**Resolution in V7:**

- DIRECT-COMMIT bindet zusätzlich `direct_process_instance_id`,
  `genesis_operation_attempt_id` und `direct_continuation_nonce_hash`;
- die Prozessinstanz wird kanonisch aus Boot-ID, PID, OS-Prozessstartzeit und
  Launch-ID gebildet;
- die rohe CSPRNG-Continuation-Nonce bleibt nur im Speicher der ursprünglichen
  Prozessinstanz und wird nie persistiert;
- unmittelbar vor Session OPEN müssen aktuelle Prozessinstanz, Genesis-
  Operation-Attempt und Nonce-Preimage exakt der COMMIT-Bindung entsprechen;
- die Ausnahme gilt nur in derselben ununterbrochenen Prozessinstanz und nur
  einmal;
- Prozessende, Crash, `exec`, PID-Reuse oder Nonce-Verlust lässt den DIRECT-
  COMMIT als Authority bestehen, beendet aber die Ausnahme unwiderruflich;
- jede neue Prozessinstanz benötigt `RESTART_ONLY` und genau ein durable
  `RESTART_AUTH_CONSUME`;
- ein Pflicht-Negativtest crasht exakt nach DIRECT-COMMIT und vor Session OPEN
  und prüft Prozesswechsel, PID-Reuse, Boot-/Startzeit-/Launch-ID-, Attempt-
  und Nonce-Mismatch; nur die unverändert lebende Originalinstanz darf genau
  einmal ohne Restart-Consumption fortsetzen.

Damit ist die Clean-Genesis-Ausnahme keine Eigenschaft des dauerhaft
persistierten DIRECT-COMMIT allein, sondern eine nicht übertragbare
Continuation derselben lebenden Genesis-Prozessinstanz.

**Betroffene V7-Abschnitte:** 7.6, 7.7.1, 9, 9.3, 21.5, 21.7 und 23.

**Abhängiges älteres Finding:** `RM1 Clean Genesis` ist normativ adressiert und
muss im neuen unabhängigen Review erneut geschlossen werden.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des High Findings

### H1 — Guardian konnte Stillstand nicht selbst erkennen; Reaping war zu stark behauptet

**Bestätigter Konflikt:** PDEATHSIG und Windows Kill-on-close greifen bei Tod
beziehungsweise Handle-Schluss, nicht aber bei einem lebenden gestoppten oder
suspendierten Guardian. Die 25-ms-Lease war selbstüberwacht: Ein stehender
Guardian konnte seine verpasste Probe nicht erkennen. Außerdem belegten weder
Linux `SIGKILL` bei uninterruptible Kernel-I/O noch asynchrone Windows-
Termination tatsächliches Process Reaping innerhalb 100 ms.

**Resolution in V7:**

- `TerminalKernelLeaseShimV1` wird als attestierter nativer Minimalteil vor
  Session OPEN verpflichtend;
- Linux/WSL armed vor Ready einen POSIX-Prozesstimer auf `CLOCK_BOOTTIME` mit
  `SIGEV_SIGNAL/SIGKILL` und absoluter Expiry;
- Guardian-Heartbeat erfolgt alle 10 ms; jede Renewal folgt erst auf
  Zielidentitäts-/Kill-Capability-Probe und setzt die Expiry höchstens auf
  `now+25 ms`;
- bei Guardian-Tod, `SIGSTOP`, Suspend, Native-Stall oder Capability-Verlust
  fehlt die Renewal und der bereits armed Kernel-Timer erzeugt das harte
  Signal ohne Guardian-Selbstdiagnose, Python, GIL oder schedulable Callback;
- ein Child-/Guardian-Seccomp-Vertrag verhindert Aufhebung oder Verlängerung
  von PDEATHSIG, Timer, Signal, Credentials und Prozessbindung;
- der Trading-Prozess prüft zusätzlich eine read-only Guardian-Lease vor jeder
  Snapshot-Akzeptanz, jedem Intent-/Execution-Side-Effect und nach jedem
  potenziell blockierenden Syscall; stale oder nichtmonotone Lease sperrt
  irreversibel;
- `TERMINAL_FAILSTOP_ASSERTED` ist exakt definiert als entweder Latch plus
  harte Termination-Anforderung oder expirierte Kernel-Lease plus kernel-
  erzeugtes hartes Signal;
- `TERMINAL_ACTION_MAX_MS=100` begrenzt ausschließlich diesen Fail-stop, nicht
  tatsächliches OS-Reaping;
- `TERMINAL_PROCESS_REAP_MAX_MS=UNBOUNDED_BY_PROTOCOL` dokumentiert die
  physische Grenze; ein pending hard kill erlaubt keinen Trading-Pfad, kein
  Clean Close und keinen Auto-Restart;
- ein versionsgebundener Kernel-Timer-Capability-/Stress-Preflight muss Clock-
  Auflösung, absolute Expiry und Signal-Generation unter Last und Stop-
  Injection innerhalb des Sicherheitsbudgets belegen, sonst bleibt OPEN
  gesperrt;
- Windows Job Object und Waitable Timer allein werden ausdrücklich als nicht
  ausreichend eingestuft. `WINDOWS_ENFORCED_SESSION_SUPPORTED=NO`, bis ein
  separat spezifizierter und unabhängig reviewter suspend-aware Kernel-Self-
  Death-Capability-Nachweis vorliegt;
- Fault Injection umfasst Guardian-/Child-`SIGSTOP`, Suspend, Stall,
  Capability-Verlust, Timer-/Clock-/Signal-/Shim-Tamper und getrennte Prüfung
  von Signal-Anforderung versus Reap-Status.

Die Plattformgrenze ist gegen die primären API-Beschreibungen für Linux-
[`timer_create`](https://man7.org/linux/man-pages/man2/timer_create.2.html),
Windows-[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
und Windows-[`TerminateProcess`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess)
formuliert. Die spätere Implementierung muss die tatsächlich gebundene Kernel-
und Workstation-Capability separat beweisen.

**Betroffene V7-Abschnitte:** 6.3, 7.8, 16.2.1, 17, 18, 19, 20, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Resolution des Medium Findings

### N1 — Abschnitt 24 verwies auf den falschen Revisionshash

**Bestätigter Konflikt:** Die V6-Spezifikation forderte am Ende irrtümlich ein
erneutes Review des bereits verworfenen Revision-5-Hashes.

**Resolution in V7:** Abschnitt 24 nennt ausschließlich
`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-7-INDEPENDENT-READONLY-REREVIEW`
des vollständigen Revision-7-Artefakts. Um einen Selbsthash-Zyklus zu
vermeiden, bindet dieses separate Resolution-Protokoll den exakten V7-Hash.

**Betroffene V7-Abschnitte:** 2 und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 6. Bewahrung der geschlossenen Findings

Revision 7 bewahrt ausdrücklich:

- recovered Genesis mit exakten NONE-Sentinels und zwingendem neuen
  `RESTART_ONLY` nach Completion;
- den autorisierten, nicht loop-startenden PREPARE-Completion-Pfad;
- journal-first Terminal-Gap-Reconciliation und Exactly-once Control Event ID;
- Worker Lease/Fencing vor Recovery;
- vollständige Authority-Root-/Generation-/PREPARE-Tamper-Tests;
- selbstreferenzfreie Authority-Generationen und getrennte Ledger-Tip-/
  Authority-Anchor-Sichten;
- vollständige S4-/Loss-/Throttle-/Progress-Handoffs und alle bestehenden
  ENFORCED-, Production-, Exchange- und Aktivierungsgrenzen.

---

## 7. Vollständigkeits- und Scope-Nachweis

```text
REVISION_6_REREVIEW_FINDINGS_MAPPED: 3/3
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 1/1
LOW_FINDINGS_MAPPED: 0/0
PREVIOUSLY_CLOSED_V5_FINDINGS_PRESERVED: 2/2
OLDER_FINDINGS_NORMATIVELY_ADDRESSED: 7/7
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_7_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Es wurden keine Runtime-Tests ausgeführt, weil ausschließlich Dokumentation
geändert wurde. Formale Datei-, Whitespace-, Hash- und Git-Scope-Prüfungen sind
zulässig; eine semantische Zertifizierung durch den Resolution-Autor ist es
nicht.

---

## 8. Nächster zulässiger Schritt

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-7-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass DIRECT nach Crash/Prozesswechsel vor Session OPEN nicht übertragbar
   ist und die ursprüngliche Prozessinstanz genau einmal fortsetzen kann;
2. dass die Kernel-Self-Death-Lease nicht von der Liveness ihres Guardians
   abhängt und Guardian-/Child-Stop innerhalb des Capability-Envelopes fail-
   stop auslöst;
3. dass Termination-Anforderung, Safety-Latch, pending Signal und tatsächliches
   Reaping nirgends erneut vermischt werden;
4. dass nicht äquivalente Plattformen fail closed bleiben;
5. dass B2, M1 und alle älteren geschlossenen Findings bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
