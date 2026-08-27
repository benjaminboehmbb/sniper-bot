# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-11 REREVIEW RESOLUTION

- **Datum:** 2026-08-18
- **Status:** REVISION-11 REREVIEW FINDINGS RESOLVED IN REVISION 12 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V11-Hash:** `a84efdb53f324d2e67f214d64edce1665a8e4a39525e93b7d94b441fc777607d`
- **Revision-10-Rereview-Resolution-Record:** `74039d71fb92d1d4dd6cd97d2e96a904874a8419bdeffc85a455f2090308c562`
- **Resolution-Zielhash V12:** `3b46f32ed460033bce6d81284a2f9e4d211b48962dd7c5e552658a38a4c445a3`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet den Blocker und das Medium-Finding des unabhängigen
read-only Re-Reviews der Revision 11 konkreten normativen Korrekturen in
Revision 12 zu.

Es zertifiziert die Korrekturen nicht selbst. Beide Resolutionstatus lauten
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V12-Hashes darf die Findings schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V11-Re-Reviews

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V11_SHA256: a84efdb53f324d2e67f214d64edce1665a8e4a39525e93b7d94b441fc777607d
REVISION_10_RESOLUTION_SHA256: 74039d71fb92d1d4dd6cd97d2e96a904874a8419bdeffc85a455f2090308c562
REREVIEW_RESULT: NOT_READY
BLOCKER: 1
HIGH: 0
MEDIUM: 1
LOW: 0
```

| Finding | V11-Re-Review | V12-Resolution |
|---|---|---|
| V11-B1 Erlaubter Raw-Write kann User-Page-/Pipe-Lock-Referenz unbeschränkt halten | OPEN | exakt pointergebundener, vorgefaulteter und gelockter Record-/Readbuffer plus negative Pointer- und concurrent-lock Faults |
| V11-M1 Obsolete Guardian-/Pipe-/Capability-Versionen in I2 und Abschlussgate | OPEN | vollständige Vereinheitlichung auf aktuelle V12-Vertragsfamilie |

Das V11-Re-Review schloss V10-B1 für den konkreten Fork-/FD-Vererbungsweg.
V9-B1s Returnwertmaschine blieb geschlossen, der end-to-end Fail-stop war aber
wegen V11-B1 erneut nicht vollständig nachgewiesen. V9-M1, V8-H1 und sämtliche
übrigen älteren Findings blieben geschlossen beziehungsweise bewahrt.

---

## 3. Resolution des Blockers

### V11-B1 — Frei wählbarer Write-Buffer konnte den Fallback blockieren

**Bestätigter Konflikt:** Revision 11 erlaubte allen Trading-/Python-Threads
`write(writer_fd, arbitrary_buf, 8)`. `O_NONBLOCK` verhindert nur das Warten auf
Pipe-Kapazität. Nach FD-Auflösung konnte `copy_from_user` auf einer nicht
residenten, file-backed oder userfaultfd-gesteuerten Page blockieren und dabei
eine `struct file`-Referenz beziehungsweise den Pipe-Lock halten. Ein zweiter
`terminal_trip()` konnte dadurch vor Returnwertklassifikation, Close und Self-
PIDFD-Fallback stecken bleiben. Selbst nach Close konnte die bestehende
Kernelreferenz HUP/EOF verhindern.

**Resolution in V12:**

1. `TerminalTripRecordBufferV1` ist eine eigene System-Page im Trading-
   Prozess. Sie wird mit exakt `MAP_PRIVATE|MAP_ANONYMOUS|MAP_POPULATE`
   erzeugt, vollständig vorbeschrieben/-gelesen, per `mlock` gelockt und per
   `mincore` plus `/proc/<pid>/smaps` als vollständig resident bestätigt.
2. Der einzige Acht-Byte-Record liegt an einem gebundenen aligned Offset. Nach
   Initialisierung wird die gesamte Page exakt `PROT_READ`; writable Aliases
   verhindern Ready. Adresse, Offset, Mapping-ID, Protection und Content-
   Fingerprint werden vor dem BPF-Build gebunden.
3. `TerminalBrokerTripReadBufferV1` ist eine getrennte, ebenfalls vollständig
   vorgefaultete und gelockte Broker-Page. Sie bleibt ausschließlich für
   `copy_to_user` `PROT_READ|PROT_WRITE`; der single-threaded Broker liest nur
   `read(trip_pipe_read_fd,broker_trip_read_ptr,8)`.
4. Der Trading-BPF erlaubt den Writer ausschließlich als
   `write(writer_fd,terminal_trip_record_ptr,8)` oder `close(writer_fd)`. Er
   vergleicht den 64-Bit-Pointerwert über dessen High-/Low-Words sowie Native-/
   x32-ABI, FD und Count. Der Broker-BPF bindet spiegelbildlich seinen Read-
   Pointer und Count.
5. Klassisches Seccomp dereferenziert weder Pointer noch Bufferinhalt und
   behauptet keine Callsite-Grenze. Jeder abweichende Pointer wird vor
   FD-Auflösung mit `SECCOMP_RET_KILL_PROCESS` abgewiesen; ein beliebiger Inhalt
   des festen Records ist immer nur `REQUEST_TERMINATION`.
6. Nach Ready sind sämtliche Mapping-, Remapping-, Protection-, Pkey-, Lock-/
   Unlock-, Reclamation-, Migration-, userfaultfd-/`UFFDIO_*`- und unbekannten
   äquivalenten Operationen gesperrt. NUMA-Policy, deaktivierte automatische
   NUMA-Migration und ausgeschlossener Memory-Hotplug sind gebunden. Fehlender
   Prefault, `mlock`, Residency-/smaps-Beleg, finale Protection oder Pointer-
   BPF-Bindung verhindert OPEN.
7. Ein bereits laufender erlaubter Exact-Buffer-Write kann noch vorübergehend
   seine eigene `struct file`-Referenz halten, besitzt aber keine
   userfaultbare oder reclaimbare User-Page mehr. Er ist selbst bereits ein
   vollständiger Trip-Record-Versuch.
8. Capability Profile V5 verlangt unter maximaler gebundener Pipe-Lock-
   Konkurrenz innerhalb `5 ms` entweder exakt acht committed Bytes,
   beweisbares EAGAIN-pending oder die Freigabe der temporären Referenz mit
   wirksamem HUP/EOF.
9. Pflichttrials kombinieren den bereits nach FD-Auflösung laufenden Exact-
   Buffer-Raw-Write mit `terminal_trip()`, concurrent Close und erzwungenem
   Self-PIDFD-Fehler. Der Raw-Write selbst muss als Trip-CAS linearisiert oder
   HUP/EOF innerhalb `5 ms` wirksam werden; Record-/Read-Buffer-Page-Faults
   müssen exakt null sein.
10. Separate negative Trials verwenden gültige alternative, file-backed,
    nicht residente, unmapped und userfaultfd-registrierte Pointer. Sie müssen
    vor FD-Auflösung per `SECCOMP_RET_KILL_PROCESS` enden und dürfen keine neue
    Pipe-/`struct file`-Referenz erzeugen.

Damit besitzt kein Trading-/Python-Thread mehr die Autorität, einen Pipe-Write
mit frei wählbarem Userbuffer zu beginnen. Die ausführbare Grenze ist der
skalare Pointerwert; Residency und Lock des gebundenen Buffers werden separat
OS-seitig attestiert.

**Betroffene V12-Abschnitte:** 2, 6.3, 7.8, 7.8.1, 16.2.1, 17, 19, 20, 23
und 24.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des Medium Findings

### V11-M1 — Obsolete Vertragsversionen in Implementierungs-/Abschlussgates

**Bestätigter Konflikt:** Revision 11 definierte bereits Parent Guardian V5,
Trip Request Pipe V3, Capability Envelope V4 und
`TerminalTradingTaskTopologyV1`. I2 und die finalen
`IMPLEMENTATION_COMPLETE`-Kriterien verlangten teilweise weiterhin Guardian
V4, Pipe V2 und Capability V3 und ließen die Task Topology aus.

**Resolution in V12:**

- I2 verlangt jetzt ausdrücklich Parent Guardian V5, Native Trip Broker V2,
  Kernel-Self-Death-Lease-Shim V3, Control Word V2, Trip Request Pipe V4,
  `TerminalTradingTaskTopologyV1`, `TerminalTripRecordBufferV1`,
  `TerminalBrokerTripReadBufferV1` und Capability Envelope V5.
- Die finalen `IMPLEMENTATION_COMPLETE`-Kriterien verwenden dieselbe Familie
  und verlangen die pointergebundenen Buffer samt No-record-Close/HUP- und
  Self-PIDFD-Fallback.
- Sämtliche alten V4-/V2-/V3-Referenzen in diesen normativen Gates wurden
  entfernt. Die weiterhin unveränderten Komponenten behalten bewusst ihre
  gültigen Versionen.

**Betroffene V12-Abschnitte:** 20 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Versionierung und Bewahrung geschlossener Findings

Der geänderte Vertrag ist eindeutig versioniert als:

- `IU4RuntimeControlProfileV6`;
- Runtime Session Envelope V7;
- `TerminalTripRequestPipeV4`;
- `TerminalLeaseCapabilityProfileV5`;
- neuer `TerminalTripRecordBufferV1`;
- neuer `TerminalBrokerTripReadBufferV1`.

Unverändert beziehungsweise weiterhin gültig bleiben
`TerminalParentGuardianV5`, `TerminalNativeTripBrokerV2`,
`TerminalKernelLeaseShimV3`, `TerminalTradingTaskTopologyV1`,
`TerminalLeaseControlWordV2`, `TerminalBrokerRenewalApprovalV1` und
`TerminalWorkerKillRequestV2`.

Revision 12 bewahrt ausdrücklich:

- V10-B1: feste TID-Menge, gemeinsame Files Table, TSYNC-Prozessbildungssperre,
  Post-OPEN-FD-Erzeugungs-/Duplikationssperre und KILL_PROCESS;
- V9-B1: vollständige Trip-Write-Returnwertmaschine, `SIGPIPE=SIG_IGN`,
  einmaligen Close ohne EINTR-Retry und Self-PIDFD-Fallback;
- V9-M1: exakte Memfd-Erzeugung und Seal-State-Machine;
- V8-H1: Broker-Prozessgrenze, alleinige Broker-RW-Map, kein Trading-Worker-FD
  und receiverseitige Worker-Prüfung der Trip-CAS;
- alle DIRECT-/Recovery-/Genesis-, Authority-, Handoff-, Atomic-State-, Loss-,
  Throttle-, Execution-Control- und L0/L1-Sicherheitsverträge;
- Windows fail closed ohne separat reviewte äquivalente Kernelprimitive;
- sämtliche Implementierungs-, ENFORCED-, Exchange- und Live-Nichtfreigaben.

---

## 6. Vollständigkeits- und Scope-Nachweis

```text
REVISION_11_REREVIEW_FINDINGS_MAPPED: 2/2
BLOCKERS_MAPPED: 1/1
HIGH_FINDINGS_MAPPED: 0/0
MEDIUM_FINDINGS_MAPPED: 1/1
LOW_FINDINGS_MAPPED: 0/0
V10_B1_CLOSED_STATUS_PRESERVED: YES
V9_B1_FULL_ERROR_DOMAIN_ADDRESSED_PENDING_REREVIEW: YES
V9_M1_CLOSED_STATUS_PRESERVED: YES
V8_H1_CLOSED_STATUS_PRESERVED: YES
OLDER_CLOSED_FINDINGS_PRESERVED: YES
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_12_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-12-INDEPENDENT-READONLY-REREVIEW`

Er muss mindestens prüfen:

1. dass beide Buffer vor Filteraktivierung vollständig vorgefaultet, gelockt,
   resident und mit den normativen finalen Protections gebunden sind;
2. dass Writer- und Broker-BPF den 64-Bit-Pointerwert, FD, Count, Architektur
   und ABI klassisch-Seccomp-ausführbar prüfen, ohne Pointer oder Inhalt zu
   dereferenzieren;
3. dass jeder abweichende Pointer vor FD-Auflösung per KILL_PROCESS endet und
   keine temporäre Pipe-/`struct file`-Referenz erlangt;
4. dass kein erlaubter Mapping-, Unlock-, Reclamation- oder userfaultfd-Pfad
   Residency oder Pointeridentität nach Ready ändern kann;
5. dass Exact-Buffer-Write, Pipe-Lock, concurrent terminaler Request/Close und
   Self-PIDFD-Fehler in beiden Linearization-Reihenfolgen innerhalb der
   Einzelbudgets enden;
6. dass I2 und sämtliche `IMPLEMENTATION_COMPLETE`-Gates nur die aktuelle
   Vertragsfamilie referenzieren;
7. dass V10-B1, V9-B1, V9-M1, V8-H1 und sämtliche älteren Closures sowie alle
   Scope- und Freigabegrenzen bewahrt sind.

Bis zu einem unabhängigen PASS bleiben Implementierung, ENFORCED-Aktivierung,
Exchange und Live-Betrieb nicht freigegeben.
