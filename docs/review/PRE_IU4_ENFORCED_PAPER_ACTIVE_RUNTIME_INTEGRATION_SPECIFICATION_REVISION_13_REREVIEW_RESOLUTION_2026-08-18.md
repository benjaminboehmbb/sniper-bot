# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-13 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-13 REREVIEW FINDINGS RESOLVED IN REVISION 14 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V13-Hash:** `e8c14a631928914c823a046dc5a85972dfccbbbd48e41897e66926db3e5f1f66`
- **Revision-13-Independent-Rereview-Record:** `e5cc26270b743d7e2cad211c8322d4b197e92f6e65de344f46b3ea52449f06b1`
- **Revision-12-Rereview-Resolution-Record:** `81ae636320ce2f5446677e8f0027383888de8074b25d17947d7982e10343c5c5`
- **Resolution-Zielhash V14:** `ec7e86923e1fc440208dd0b65f4215e22badd62dcfb69e2c0d2e17b7457293e5`
- **Resolution-Zielzeilen V14:** `3293`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die zwei Blocker des unabhängigen read-only Re-Reviews
der Revision 13 konkreten normativen Korrekturen in Revision 14 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V14-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V13-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V13_SHA256: e8c14a631928914c823a046dc5a85972dfccbbbd48e41897e66926db3e5f1f66
REVISION_12_RESOLUTION_SHA256: 81ae636320ce2f5446677e8f0027383888de8074b25d17947d7982e10343c5c5
REVISION_13_REREVIEW_SHA256: e5cc26270b743d7e2cad211c8322d4b197e92f6e65de344f46b3ea52449f06b1
REREVIEW_RESULT: NOT_READY
BLOCKER: 2
HIGH: 0
MEDIUM: 0
LOW: 0
```

| Finding | V13-Re-Review | V14-Resolution |
|---|---|---|
| V13-B1 Post-Latch/Pre-Syscall-Fenster ist nur für den Gewinner-TID sichtbar | OPEN | `TerminalTripLatchV2` wird vom reservierten Native Shim unabhängig spätestens alle 1 ms beobachtet; TRIPPED stoppt Timerverlängerungen ohne Gewinner-TID-Fortschritt |
| V13-B2 Durable CLOSE liegt vor Broker-CLOSED und kann Terminal-Gap verbergen | OPEN | `RuntimeSessionCloseProtocolV2`: durable PREPARE → Broker-CLOSED → durable COMMIT; ausschließlich COMMIT ist clean |

Das V13-Re-Review schloss V12-B1 im ursprünglichen Pipe-Write-Sinn und
bestätigte die Bewahrung von V11-B1, V11-M1, V10-B1, V9-B1, V9-M1, V8-H1 und
den älteren Authority-/State-/Execution-Verträgen. Die zwei neuen Findings
betrafen ausschließlich das vorgelagerte Scheduling-Fenster und die durable
Close-Reihenfolge.

---

## 3. Resolution von V13-B1

### Post-Latch/Pre-Syscall-Stall ließ Renewals weiterlaufen

**Bestätigter Konflikt:** Revision 13 setzte zuerst einen rein lokalen Latch
und rief danach Self-PIDFD-`SIGKILL` auf. Wurde ausschließlich der Gewinner-TID
zwischen beiden Schritten angehalten, sahen Guardian, Broker und Shim weiterhin
Control Word RUNNING. Renewals und Timerverlängerungen konnten unbeschränkt
fortgesetzt werden; der lokale Latch allein erfüllte keine Variante von
`TERMINAL_FAILSTOP_ASSERTED`.

**Resolution in V14:**

1. Der lokale Latch wird exakt als lock-free
   `_Atomic uint64_t TerminalTripLatchV2` mit `CLEAR=0` und `TRIPPED=1`
   versioniert. Jeder terminale Entry linearisiert als erste Mutation per
   release-CAS ausschließlich CLEAR→TRIPPED; Reset ist unzulässig und jeder
   andere Wert gilt fail-safe als TRIPPED.
2. Alle fachlichen Gates führen unmittelbar vor jedem Side Effect einen
   Acquire-Load aus und blockieren bei jedem Wert ungleich CLEAR.
3. Der bereits reservierte `TerminalKernelLeaseShimV5` ist ein vom Gewinner-
   TID unabhängiger kontinuierlicher Observer. Auf fester reservierter CPU
   prüft er den Latch spätestens alle `1 ms`, vor jeder Approval-Validierung und
   unmittelbar vor jedem `timer_settime`.
4. Nach Beobachtung von TRIPPED/INVALID verwirft der Shim dauerhaft alle
   vorhandenen und späteren Broker-Approvals. Er verlängert oder disarmt den
   bereits armed Timer nicht; die letzte absolute Expiry bleibt höchstens
   `now_at_broker_validation+25 ms`.
5. Linearisiert die Latch-CAS erst nach der letzten Acquire-Prüfung, aber vor
   einem bereits begonnenen `timer_settime`, darf höchstens die schon
   vorvalidierte 25-ms-Expiry gesetzt werden. Die nächste Prüfung sperrt jede
   weitere Verlängerung.
6. Wird nur der Gewinner-TID unmittelbar nach CAS und vor dem ersten PIDFD-
   Syscall angehalten, stoppt der gesunde Shim die Timerverlängerung. Wird das
   gesamte Child samt Shim angehalten, läuft der kernel-armed Timer ohne
   Userspace-Fortschritt ab.
7. Capability- und Per-Startup-Matrizen enthalten dafür getrennte
   deterministische Trials über alle Heartbeat-Phasen. PASS verlangt Shim-
   Beobachtung innerhalb 1 ms, keine folgende Timerverlängerung, kernel-seitige
   Signalerzeugung und null Side-Effect-Fortschritt ohne Gewinner-TID-
   Fortsetzung.
8. OPEN und Evidenz binden Latch-Adresse, Alignment, Initialwert, Lock-free-
   Nachweis, Acquire-/Release-Semantik, Shim-TID, CPU, Intervall, letzte
   Beobachtung und letzten zulässigen Timer-Expiry.

Damit hängt der Fail-stop nach erfolgreicher erster Mutation nicht mehr davon
ab, dass der mutierende Trading-TID den ersten PIDFD-Syscall erreicht.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution von V13-B2

### Durable Session CLOSE konnte eine spätere TERMINATING-CAS verbergen

**Bestätigter Konflikt:** Revision 13 schrieb den einzigen
`RUNTIME_SESSION_CLOSE` vor Broker-`RUNNING→CLOSED`. Gewann anschließend ein
Trip und ging der KILL-Write verloren, blieb dennoch ein passender CLOSE im
Ledger. Der nächste Startup konnte die Session dadurch als clean klassifizieren
und die vorgeschriebene Terminal-Gap-Sperre umgehen.

**Resolution in V14:**

1. `RuntimeSessionCloseProtocolV2` ersetzt den einzelnen CLOSE durch die
   getrennten Records `RUNTIME_SESSION_CLOSE_PREPARE` und
   `RUNTIME_SESSION_CLOSE_COMMIT`.
2. Nach vollständiger Reconciliation sendet Guardian genau einen
   `TerminalGuardianOrderlyCloseRequestV2` an den Broker. Der Broker bleibt
   während der asynchronen PREPARE-Persistenz in RUNNING und priorisiert
   weiterhin HUP/Trip vor Renewal und Close.
3. Der Broker sendet nonblocking
   `TerminalWorkerClosePrepareRequestV1`. Der Worker schreibt PREPARE über
   seinen vorab geöffneten exklusiven Lifecycle-Append-Handle und bestätigt
   den durable Fingerprint mit `TerminalWorkerClosePrepareAckV1`.
4. PREPARE ist ausdrücklich kein passender CLOSE. Trip, Crash oder Fehler vor
   Broker-CLOSED lässt PREPARE ohne COMMIT und damit die Session unclean.
5. Nur nach gültigem PREPARE-ACK und weiterhin exakt `(RUNNING,n,0)` darf der
   Broker `RUNNING→CLOSED` linearisierten. TERMINATING→CLOSED bleibt verboten.
   CLOSED ist der globale logische Side-Effect-Close-Zeitpunkt; alle Trading-
   Gates lehnen ihn ab.
6. Nach CLOSED bleiben Timer armed, Trading gegatet und die OS-Bindungen aktiv.
   Der Broker fordert über `TerminalWorkerCloseCommitRequestV1` den COMMIT an.
   Der Worker akzeptiert ihn ausschließlich bei eigenem Acquire-Load CLOSED und
   bestätigt erst nach durablem Append mit `TerminalWorkerCloseCommitAckV1`.
7. Erst nach Validierung dieses ACK sendet der Broker
   `TerminalBrokerCloseCommitApprovalV1` an Shim und Guardian. Erst diese
   Approval erlaubt Timer-Disarm und Trading-Exit.
8. COMMIT-Writefehler, Broker-/Worker-Crash oder verlorenes ACK nach CLOSED
   erzeugt keine Approval. Der Timer läuft mangels Renewals aus; PREPARE ohne
   COMMIT erzwingt beim Folgestart `TERMINAL_UNKNOWN` und
   `RECONCILE_TERMINAL_GAP`.
9. Ausschließlich der vollständige Pfad PREPARE → Broker-CLOSED → durable COMMIT
   ist clean. Startup, Monitoring, Reason Codes, Fault-Matrix und Completion-
   Gate verwenden dieselbe Definition.
10. Die sechs Close-Nachrichten besitzen disjunkte Type-Konstanten, feste
    Struct-Längen, Nonces, Peer-Credentials und PREPARE-/CLOSED-/COMMIT-
    Bindungen. Der KILL-Pfad bleibt davon strikt getrennt.

Damit kann kein vor Broker-CLOSED persistierter Record mehr einen späteren
terminalen Gewinner als clean shutdown maskieren.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Versionierung und Bewahrung geschlossener Findings

Der geänderte Vertrag ist eindeutig versioniert als:

- `IU4RuntimeControlProfileV8`;
- Runtime Session Envelope V9;
- neuer `TerminalTripLatchV2`;
- neuer `RuntimeSessionCloseProtocolV2`;
- `TerminalSelfKillEntryV2`;
- `TerminalLeaseCapabilityProfileV7`;
- `TerminalParentGuardianV7`;
- `TerminalNativeTripBrokerV4`;
- `TerminalKernelLeaseShimV5`.

Unverändert beziehungsweise weiterhin gültig bleiben
`TerminalTripLivenessPipeV1`, `TerminalTradingTaskTopologyV1`,
`TerminalLeaseControlWordV2`, `TerminalBrokerRenewalApprovalV1` und
`TerminalWorkerKillRequestV2`.

Revision 14 bewahrt ausdrücklich:

- V12-B1/V11-B1: kein Pipe-Read/-Write/-Datentransfer und kein Userbuffer-,
  Pipe-Page-, Reclaim- oder temporärer Writerpfad im Terminal-Sicherheitsweg;
- V11-M1: I2 und sämtliche Completion-Gates referenzieren dieselbe aktuelle
  Vertragsfamilie;
- V10-B1: feste TID-/Files-Table-Topologie, TSYNC-KILL_PROCESS sowie vollständige
  Post-Ready-Task-/FD-/Writer-Referenzsperre;
- V9-B1: vollständige PIDFD-Fehlerfolge und einmaliger Close ohne Retry;
- V9-M1: exakte Memfd-Erzeugung und Seal-State-Machine;
- V8-H1: separater Broker als alleiniger Control-Word-Writer, Trading nur RO,
  kein Trading-Worker-FD und receiverseitige Worker-Prüfung;
- alle DIRECT-/Recovery-/Genesis-, Authority-, Handoff-, Atomic-State-, Loss-,
  Throttle-, Execution-Control- und L0/L1-Sicherheitsverträge;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- sämtliche Implementierungs-, ENFORCED-, Exchange- und Live-Nichtfreigaben.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_13_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 2/2
HIGH_FINDINGS_MAPPED: 0/0
MEDIUM_FINDINGS_MAPPED: 0/0
LOW_FINDINGS_MAPPED: 0/0
V13_B1_RESOLVED_PENDING_REREVIEW: YES
V13_B2_RESOLVED_PENDING_REREVIEW: YES
V12_B1_CLOSED_STATUS_PRESERVED: YES
V11_B1_CLOSED_STATUS_PRESERVED: YES
V11_M1_CLOSED_STATUS_PRESERVED: YES
V10_B1_CLOSED_STATUS_PRESERVED: YES
V9_B1_CLOSED_STATUS_PRESERVED: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_14_HASHED: YES
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

## 7. Nächster zulässiger Schritt

Der nächste zulässige Schritt ist ausschließlich:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-14-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass der Shim `TerminalTripLatchV2` unabhängig vom Gewinner-TID spätestens
   alle 1 ms und unmittelbar vor jeder Timerverlängerung beobachtet;
2. dass ein Halt exakt nach Latch-CAS und vor Self-PIDFD-Syscall ohne Gewinner-
   TID-Fortschritt jede weitere Timerverlängerung stoppt und das Kernel-Signal
   innerhalb des gebundenen Envelopes erzeugt;
3. dass der Latch keine Renewal-/Worker-Autorität besitzt und Control Word V2
   weiterhin die einzige globale CAS-Autorität bleibt;
4. dass PREPARE kein clean CLOSE ist und ausschließlich ein nach Broker-CLOSED
   durable COMMIT die Session beim Startup schließt;
5. dass Trip/HUP vor CLOSED gegen Close korrekt linearisiert und jeder Crash/
   Writefehler vor COMMIT unclosed bleibt;
6. dass Timer-Disarm und Child-Exit ohne gültige brokerbestätigte Commit-
   Approval unerreichbar sind;
7. dass die sechs Close-Nachrichten, Worker-State-Prüfungen, Peerbindungen und
   KILL-/Close-Type-Trennung vollständig ausführbar sind;
8. dass Capability-/Preflight-/Fault-Matrizen beide Findings und ihre Race-
   Grenzen deterministisch abdecken;
9. dass I2 und sämtliche `IMPLEMENTATION_COMPLETE`-Gates ausschließlich die
   aktuelle V14-Vertragsfamilie referenzieren;
10. dass V12-B1, V11-B1, V11-M1, V10-B1, V9-B1, V9-M1, V8-H1 und alle älteren
    Closures sowie Scope- und Freigabegrenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
