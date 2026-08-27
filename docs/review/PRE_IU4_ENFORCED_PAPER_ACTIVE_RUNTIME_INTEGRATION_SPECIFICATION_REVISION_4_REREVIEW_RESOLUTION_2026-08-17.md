# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVISION-4 REREVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REVISION-4 REREVIEW FINDINGS RESOLVED IN REVISION 5 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V4-Hash:** `fe9f6872403754961919941ed05436bfbea7ba013da63486c1b006efb24362fe`
- **V4-Resolution-Record:** `a0bc599e6e19a010c275de31cb0983c5fa4dda351e1ecb719df747ed6806400b`
- **Resolution-Zielhash V5:** `a544b0a83b4b6f13df8cb3f3bd6d75b4836655fb4108a6d85b992f4e598e7dde`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die zwei Blocker, das High- und das Medium-Finding des
unabhängigen read-only Re-Reviews der Revision 4 konkreten normativen
Korrekturen in Revision 5 zu.

Es zertifiziert die Korrekturen nicht selbst. Jeder Resolutionstatus lautet
`RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges read-only
Re-Review des vollständigen V5-Hashes darf ein Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V4-Re-Reviews

Die exakten Prüfidentitäten wurden vor und nach dem Review bestätigt:

```text
HEAD: c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
SPEC_V4_SHA256: fe9f6872403754961919941ed05436bfbea7ba013da63486c1b006efb24362fe
V4_RESOLUTION_SHA256: a0bc599e6e19a010c275de31cb0983c5fa4dda351e1ecb719df747ed6806400b
REREVIEW_RESULT: NOT_READY
BLOCKER: 2
HIGH: 1
MEDIUM: 1
LOW: 0
```

Status der vier Findings aus dem V3-Re-Review:

| Finding | V4-Re-Review | V5-Resolution |
|---|---|---|
| B1 Record↔Target-Hash-Zyklus | CLOSED | unverändert bewahrt |
| B2 Ledger Tip/Authority Anchor | CLOSED | unverändert bewahrt |
| H1 unpersistierbarer terminaler KILL | OPEN | journal-first Recovery und harter Exit-Vertrag |
| L1 Tick-Deeskalationsmatrix | CLOSED | unverändert bewahrt |

Von den sieben älteren Findings waren sechs geschlossen. `RM1 Clean Genesis`
blieb ausschließlich wegen des fehlenden autorisierten PREPARE-
Fertigstellungspfads offen.

---

## 3. Resolution der Blocker

### B1 — Kein autorisierter Pfad zum Fertigstellen eines offenen PREPARE

**Bestätigter Konflikt:** V4 verlangte nach einem Crash zwischen PREPARE und
COMMIT eine neue Restart/Recovery Authorization. Deren Operationen enthielten
jedoch keine PREPARE-Fertigstellung. `RECOVER_AND_RESTART` durfte nur einen
bereits committeten Atomic-Journal-Head materialisieren und die erlaubte
Startup-Attempt-Extension ließ keinen Authority-COMMIT zu.

**Resolution in V5:**

- neue exklusive Operation `COMPLETE_AUTHORITY_PREPARE`;
- exakte Bindung an PREPARE-Event-ID/Fingerprint, Operationstyp, geplante
  Authority Generation, Source Authority, Target-Core-Fingerprint,
  Target-Schema/-Pfad und genau einen korrespondierenden COMMIT-Typ;
- bei Genesis ohne Source Authority sind ausschließlich kanonische
  `NONE`-/`EMPTY`-/`NO_ATOMIC_STATE`-Sentinels zulässig;
- die Operation ist nur bei genau einem offenen hashgültigen PREPARE ohne
  COMMIT erlaubt;
- ein vorhandener Target State wird exakt geprüft, ein fehlender ausschließlich
  aus der gebundenen Core-Payload materialisiert;
- erst nach read-only Reconciliation wird genau der passende COMMIT angehängt;
- keine Business-/Safety-Neuentscheidung und kein anderer PREPARE sind
  zulässig;
- die Startup-Attempt-Extension erlaubt für diese Operation nach genau einem
  Consumption Record genau einen passenden Authority-COMMIT;
- ein bereits bestehender COMMIT wird nie dupliziert;
- jeder Crash vor COMMIT verlangt eine neue Authorization, bewahrt aber
  PREPARE und Generation;
- die Completion-Operation startet niemals einen Loop und beendet sich nach
  COMMIT; der spätere Start benötigt eine neue `RESTART_ONLY`-Authorization;
- Activation Authorization ist für diese reine Maintenance-Operation weder
  erforderlich noch eine mögliche Ersatzfreigabe.

Damit können Genesis, beide Handoffs und V1→V2-Migration nach jedem
PREPARE/Target/COMMIT-Crashpunkt exakt fertiggestellt werden, ohne die
ursprüngliche Entscheidung umzudeuten.

**Betroffene V5-Abschnitte:** 7.6, 7.7.1, 9, 9.3, 13.6, 18, 20, 21.5,
21.7 und 23.

**Abhängiges älteres Finding:** `RM1 Clean Genesis` ist normativ adressiert und
muss im neuen unabhängigen Review erneut geschlossen werden.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

### B2 — Durable KILL-Journal mit stale Snapshot war nicht ausführbar geordnet

**Bestätigter Konflikt:** Der Coordinator committed zuerst den Journalrecord
und ersetzt danach den Snapshot. V4 verwendete einen vorhandenen terminalen
KILL nur bei bereits reconciled State. Beim Crash nach durable Journal, aber vor
Snapshot Replace, wäre der erste KILL bereits autoritativ, der
Wiederverwendungszweig aber nicht erreichbar gewesen; ein zweiter KILL hätte
Exactly-once verletzt.

**Resolution in V5:** `RECONCILE_TERMINAL_GAP` arbeitet strikt journal-first:

1. alten Persistence Worker als beendet oder durch höheren Fencing-Token vom
   Journal ausgeschlossen beweisen;
2. vollständige Journal-Kette ab Session OPEN vor jeder Snapshot-Wertung
   validieren;
3. nach einem hashgültigen durable terminalen KILL dieser Session suchen;
4. existiert genau einer, dessen `state_after` idempotent materialisieren und
   exakt seine Control Event ID verwenden;
5. nur bei vollständiger Abwesenheit eines terminalen KILL und exakt
   reconciled Journal-/Snapshot-Basis einen neuen konservativen EMERGENCY-KILL
   committen;
6. bei ungültigem Tail, mehreren widersprüchlichen terminalen Records oder
   uneindeutigem State-before ohne Mutation blockieren;
7. erst nach vollständiger Reconciliation den Gap Record schreiben.

Ein Crash nach KILL-Journal, nach Snapshot Replace oder vor Gap Record führt
dadurch immer zur Wiederverwendung derselben Event ID und niemals zu einem
zweiten KILL. Ein verspätet durable Worker-Write besitzt dieselbe vorab
sessiongebundene Event ID; Worker-Lease/Fencing verhindert Writes nach Beginn
der Recovery.

**Betroffene V5-Abschnitte:** 7.8, 16.2.1, 17, 18, 19, 20, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des High Findings

### H1 — Terminale Write-Deadline begrenzte L1C „sofort“ nicht normativ

**Bestätigter Konflikt:** V4 nannte eine gebundene Deadline, definierte aber
weder maximale Dauer und monotone Zeitquelle noch einen ausführbaren Umgang mit
nichtkooperativ blockierendem I/O.

**Resolution in V5:**

- unveränderliche Protokollobergrenze `TERMINAL_EXIT_MAX_MS=100`;
- Profile dürfen ausschließlich ganzzahlige `1..100 ms` wählen;
- Zeitmessung nur über `time.monotonic_ns()` oder nachgewiesen äquivalente
  monotone OS-Clock;
- `TerminalPersistenceWorkerV1` besitzt als isolierter Prozess den potenziell
  blockierenden Journal-I/O;
- der Trading-Prozess verwendet nur einen vorab geöffneten nonblocking IPC-
  Kanal und führt im EMERGENCY-Pfad keinen Datei-, Flush- oder Snapshot-Syscall
  aus;
- `TerminalExitWatchdogV1` ist ein davon getrennter Supervisor ohne Journal-I/O
  und erzwingt den harten Parent-Exit spätestens an der Deadline;
- Session OPEN bindet Worker/Watchdog-IDs, Ready-Nonces, IPC, Parent-PID,
  monotone Clock, Deadline, einmaligen Emergency-Lease und Control Event ID;
- fehlender Ready-Handshake, ungültige Deadline/Clock oder Resource Reserve
  verhindert Loop-Start;
- bei EMERGENCY werden fachliche Verarbeitung zuerst gestoppt, Watchdog
  aktiviert und exakt ein nonblocking Request mit vorab gebundener Event ID
  versandt;
- Worker akzeptiert nur eine exakt state-/sequence-/sessiongebundene Payload;
- ACK, Write, Worker oder IPC können die 100-ms-Prozessgrenze nicht verlängern;
- ein verspäteter Worker-Commit bleibt dieselbe Event ID und wird später
  journal-first reconciled;
- Watchdog beendet/fenced den alten Worker; Recovery beginnt erst nach
  nachgewiesenem Worker-Tod oder wirksamem Lease-Fencing.

Damit hängt der Exit des Trading-Prozesses nicht von der kooperativen Rückkehr
eines blockierenden Datei-I/O ab.

**Betroffene V5-Abschnitte:** 6.3, 7.8, 9, 16.2.1, 17, 18, 19, 20, 21.7 und
23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Resolution des Medium Findings

### M1 — Authority-Abstammung aktueller Atomic States war nicht vollständig getestet

**Bestätigter Konflikt:** V4 verlangte eine lückenlose State-/Journal-Historie
vom im Authority-COMMIT gebundenen Target State, forderte aber keine expliziten
Root- und Tamper-Negativtests.

**Resolution in V5:** Die Pflichtmatrix verlangt nun:

- `state_before` der ersten Atomic-V2-Transaktion stimmt exakt mit dem im
  Authority-COMMIT gebundenen Target-State-Fingerprint überein;
- initiale Transaction Sequence und Journal-Head-Basis stimmen exakt;
- jede spätere Tick-/Control-Transition bewahrt Generation ID und PREPARE-
  Fingerprint;
- manipulierte Generation oder PREPARE-Bindung wird abgelehnt;
- eine intern lückenlose Journalkette mit falschem Genesis-/Handoff-Root wird
  abgelehnt;
- ein nicht vom committed Root erreichbarer aktueller Snapshot wird abgelehnt;
- Replay und Recovery bewahren dieselbe Authority-Abstammung.

**Betroffene V5-Abschnitte:** 7.7.1, 17.3, 20, 21.6, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 6. Bewahrung bereits geschlossener Findings

Revision 5 bewahrt ausdrücklich:

- selbstreferenzfreie Business/Generation/Core/PREPARE/State/COMMIT-
  Fingerprint-Domänen;
- getrennte Ledger-Tip-, Authority-Anchor- und Generation-Sichten;
- vollständige S4-/Loss-/Throttle-/Progress-Handoffs;
- additives S4V2 und terminale Capability-Matrix;
- getrennte Tick-, Control- und Lifecycle-Ordnungsräume;
- ausschließlich `risk_escalation=NONE_TO_SOFT` im Tick;
- Pre-Accept-Mutationsgrenze;
- committed Entry Quote und Settlement ohne Re-Authorization;
- vollständigen Legacy-Write-/Sidecar-Ausschluss in ENFORCED;
- Atomic Progress Cursor und Legacy-exit-only Control Binding;
- Production-, Exchange- und Aktivierungsgrenzen.

---

## 7. Vollständigkeits- und Scope-Nachweis

```text
REVISION_4_REREVIEW_FINDINGS_MAPPED: 4/4
BLOCKERS_MAPPED: 2/2
HIGH_FINDINGS_MAPPED: 1/1
MEDIUM_FINDINGS_MAPPED: 1/1
LOW_FINDINGS_MAPPED: 0/0
PREVIOUSLY_CLOSED_V3_FINDINGS_PRESERVED: 3/3
OLDER_FINDINGS_NORMATIVELY_ADDRESSED: 7/7
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_5_HASHED: YES
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

## 8. Nächster Gate

Der nächste zulässige Schritt ist:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-5-INDEPENDENT-READONLY-REREVIEW`

Das neue Re-Review muss den vollständigen V5-Hash prüfen und insbesondere
belegen, dass:

- jeder offene PREPARE mit exakt einer passenden Authorization/Generation und
  genau einem COMMIT fertigstellbar ist;
- keine Completion-Operation einen Loop startet oder bereits committed
  Authority dupliziert;
- ein durable KILL-Journal mit stale Snapshot vor jeder Ersatzentscheidung
  idempotent materialisiert wird;
- der alte Persistence Worker vor Journalprüfung sicher beendet oder gefenced
  ist;
- der Trading-Prozess auch bei nichtkooperativ blockierendem Worker-I/O
  spätestens innerhalb der unveränderlichen 100-ms-Grenze endet;
- die Journalkette jedes aktuellen State exakt am committed Authority-Target
  verwurzelt ist und Tampering fail closed bleibt.

Erst ein bestandenes unabhängiges Re-Review kann die Spezifikation als
implementierungsbereit bewerten. Terminales R3, bestandene Final Attestation
und eine separate ausdrückliche Implementierungsfreigabe bleiben auch danach
zwingend.
