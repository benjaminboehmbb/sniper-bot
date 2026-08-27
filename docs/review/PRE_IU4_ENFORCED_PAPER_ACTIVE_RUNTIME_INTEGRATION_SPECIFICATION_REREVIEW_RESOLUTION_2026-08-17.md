# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REREVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REREVIEW FINDINGS RESOLVED IN REVISION 3 — NEW INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V2-Hash:** `b330d6cb45c418dd937adaf8f483337b8cba2e250a8150c6b0d43e25bcbfc348`
- **V2-Resolution-Record:** `11191fe358433b9ea56dd8836f9f77619a5b7ea2266adfd1d614f54a3152640a`
- **Resolution-Zielhash V3:** `3a12e977bc7fe64b0341dc4ca5b5f562fef18598b8afedae5f4d4dbdd6bd23c6`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck und Aussagegrenze

Dieses Dokument ordnet die drei Restfindings und vier Neufindings des
unabhängigen read-only Re-Reviews der Revision 2 konkreten normativen
Korrekturen in Revision 3 zu.

Es zertifiziert seine eigenen Korrekturen nicht. Jeder Resolutionstatus lautet
deshalb `RESOLVED_PENDING_INDEPENDENT_REREVIEW`. Erst ein neues unabhängiges
read-only Re-Review des vollständigen V3-Hashes darf ein Finding schließen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden in diesem Resolution-Schritt verändert.

---

## 2. Ausgang des unabhängigen V2-Re-Reviews

Das Re-Review des exakten V2-Hashes endete mit:

```text
REREVIEW_RESULT: NOT_READY
RESIDUAL_BLOCKER: 2
NEW_HIGH: 2
RESIDUAL_OR_NEW_MEDIUM: 3
LOW: 0
```

Als geschlossen bestätigt wurden die ursprünglichen Findings zu:

- HARD-/EMERGENCY-Semantik;
- vollständigem committed Entry Quote;
- vollständigem Ausschluss von Legacy-Writes und Legacy-Progress in ENFORCED;
- positiongebundener Legacy-exit-only Control Binding.

Die folgenden sieben Findings blieben offen oder entstanden aus der vertieften
Prüfung. Keines wurde herabgestuft oder verworfen.

---

## 3. Resolution der residualen Blocker

### RB2 — Restart Authorization war nicht dauerhaft als verbraucht belegt

**Bestätigter Konflikt:** Revision 2 erklärte eine
`IU4RestartRecoveryAuthorizationV1` nach Verwendung für verbraucht, definierte
aber keinen crash-sicheren, kanonischen Consumption-State. Dieselbe
`RESTART_ONLY`-Datei hätte nach erneutem Prozessstart wieder akzeptiert werden
können.

**Resolution in V3:**

- additives append-only `IU4LifecycleLedgerV1` mit Hash-Kette, monotoner
  Sequence, exklusivem Writer und create-new/File-/Directory-`fsync`;
- genau ein durable `RESTART_AUTH_CONSUME` vor Recovery oder Loop-Freigabe;
- global eindeutige Authorization-ID und Bindung an Payload, Operation,
  Verantwortlichen, Pre-State, Journal Head und vorherigen Lifecycle Head;
- Crash vor dem durable Record verbraucht nicht;
- Crash nach dem durable Record hält die Authorization für immer verbraucht,
  auch wenn der Loop nie startet;
- Head-Rekonstruktion erfolgt read-only aus der Record-Kette;
- gleiche ID mit anderer Payload ist ein harter Ledger-Konflikt;
- jeder weitere Versuch nach Consumption benötigt eine neue manuelle
  Authorization.

**Betroffene V3-Abschnitte:** 7.6, 7.7, 9, 18, 19, 20, 21.5 und 21.7.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

### RB3 — Owner Epoch und vollständiges Legacy-S4 waren nicht kanonisch

**Bestätigter Konflikt:** Revision 2 verlangte einen persistierten
`state_owner_epoch`, spezifizierte aber keine kanonische Legacy-Persistenz
dafür. Außerdem fehlten in der vollständigen Handoff-Abbildung die L0-Felder
`loss_today` und `anomaly_counter`.

**Resolution in V3:**

- der Owner Epoch wird ausschließlich aus dem letzten gültigen
  Lifecycle-Genesis-/Handoff-Record abgeleitet;
- Environment, Modus, isolierter Atomic Snapshot und Legacy-State dürfen den
  Owner nicht allein behaupten;
- Atomic State, Authorization und Handoff Manifest binden Lifecycle Sequence,
  Head und Fingerprint;
- `IU4LegacySafetySnapshotV1` bildet die Legacy-Handoff-Sicht, ist aber
  ausdrücklich keine Owner-Autorität;
- jede Richtung bildet `kill_level`, `cooldown_until_utc`, `trades_today`,
  `loss_today`, `anomaly_counter`, `trades_6h`,
  `last_trade_timestamp_utc` und Reason Codes vollständig ab;
- fehlende oder implizit defaultete Werte blockieren Genesis, Migration und
  beide Handoff-Richtungen;
- spätere additive Legacy-State-/Store-Anpassungen wurden ausdrücklich in den
  Implementierungsscope aufgenommen.

**Betroffene V3-Abschnitte:** 7.2, 7.7, 8.3, 9, 9.1, 13.1, 13.2, 13.6,
17, 18, 19, 21.6, 21.7 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 4. Resolution des residualen Medium Findings

### RM1 — Clean Genesis war nicht vollständig und nicht crash-sicher

**Bestätigter Konflikt:** Das V2-Genesis-Manifest nannte S4 nur allgemein und
definierte weder sämtliche S4-Werte noch eine durable GENESIS-
Materialisierungsreihenfolge.

**Resolution in V3:**

- vollständiges `PaperRiskStateS4V2` einschließlich aller Legacy-/L0-Felder,
  Capabilities, Reasons und Fingerprints;
- explizite Bindung von S2 FLAT, Loss Cluster, Throttle, Progress, Journal
  Sequence 0, leerem Journal und allen Cross-State-Fingerprints;
- `ATOMIC_GENESIS` als Write-ahead Lifecycle-Record vor der atomaren
  Snapshot-Publikation;
- File- und Directory-`fsync` an beiden durable Grenzen;
- abschließende read-only Reconciliation;
- Crash vor Record erzeugt keine Genesis;
- Crash nach Record lässt eine verbrauchte, unvollständige Lifecycle-Operation
  zurück, die nur mit neuer Restart/Recovery Authorization und exakt derselben
  Payload materialisiert werden darf;
- dieselben Grundsätze gelten für `LEGACY_GENESIS`, beide Handoffs und
  V1→V2-Migration.

**Betroffene V3-Abschnitte:** 7.7, 9, 9.3, 13.2, 13.6, 18, 21.6, 21.7 und
23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 5. Resolution der neuen High Findings

### NH1 — S4V1 konnte terminale HARD-/EMERGENCY-Capability nicht darstellen

**Bestätigter Konflikt:** Der bestehende `PaperRiskStateS4V1`-Vertrag verlangt
invariant `exit_allowed=true`, während HARD den Loop und EMERGENCY den Prozess
ohne weitere automatisierte Exit-Auswertung beenden müssen.

**Resolution in V3:**

- S4V1 bleibt unverändert und ist in `AtomicPaperStateV2` unzulässig;
- additives `PaperRiskStateS4V2` mit vollständigen Safety-Werten;
- getrennte `entry_allowed`- und `exit_evaluation_allowed`-Capabilities;
- `runtime_directive` ist exakt `CONTINUE`, `STOP_LOOP` oder `EXIT_PROCESS`;
- NONE/SOFT/HARD/EMERGENCY besitzen eine verbindliche Capability-Matrix;
- HARD und EMERGENCY setzen `exit_evaluation_allowed=false` und lösen keinen
  automatischen Exit aus;
- KILL materialisiert genau die zum Kill-Level gehörende S4V2-Capability;
- Reason Codes, Monitoring und Pflicht-Tests wurden versionsbewusst ergänzt.

**Betroffene V3-Abschnitte:** 8.3, 9.3, 13.1, 13.2, 16.2, 17, 18, 19,
20, 21.4 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

### NH2 — Ein-Transaktions-Modell war für kombinierte Ereignisse mehrdeutig

**Bestätigter Konflikt:** V2 verlangte eine Transaktion pro Tick und definierte
OPEN, CLOSE, KILL, ENTRY_VETO und PROGRESS als disjunkte Typen. CLOSE plus SOFT
oder ENTRY_VETO plus terminalem KILL waren nicht eindeutig repräsentierbar.

**Resolution in V3:**

- drei getrennte Ordnungsräume: Tick-Transaktion, KILL-Control-Transaktion und
  Lifecycle-Record;
- genau ein Tick-`primary_effect` aus OPEN, CLOSE, ENTRY_VETO oder PROGRESS;
- optionale nichtterminale NONE-/SOFT-Risk-Transition im selben Tick-Commit;
- KILL besitzt eigene Control Event ID und keinen Progress Cursor;
- CLOSE plus SOFT wird in genau einer CLOSE-Tick-Transaktion committed;
- terminales KILL vor durable Tick-Commit verwirft den Tick;
- terminales KILL nach durable Tick-Commit materialisiert zuerst den bereits
  autoritativen Tick und folgt danach als eigene Control-Transaktion;
- OPEN ist bei pending KILL verboten;
- ENTRY_VETO plus KILL folgt derselben expliziten Pre-/Post-Commit-Ordnung.

**Betroffene V3-Abschnitte:** 10.2, 10.3, 13.4, 16.2, 17, 21.1, 21.4 und
21.7.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 6. Resolution der neuen Medium Findings

### NM1 — Transaktionspflicht war vor Snapshot-Akzeptanz zu absolut

**Bestätigter Konflikt:** V2 verlangte für jeden ENFORCED-Tick eine
Transaktion. Binding-, State-, Schema-, Authorization- oder Ressourcenfehler
können jedoch fail closed auftreten, bevor ein Snapshot mutierende Autorität
erhalten darf.

**Resolution in V3:**

- explizite Zustände `OBSERVED_PRE_ACCEPT`, `REJECTED_PRE_ACCEPT`, `ACCEPTED`,
  `COMMITTED` und `TERMINAL`;
- Pre-Accept-Fehler erzeugen weder Journal-Record noch Cursor-Fortschritt noch
  fachliche State-Mutation;
- nur stabile nichtautoritative Diagnose-Evidence ist zulässig;
- nach Akzeptanz gilt genau ein Tick-Commit oder der explizit geordnete
  terminale KILL-Fall;
- Fehler vor durable Journal Write lassen Replay erst nach manuell
  autorisiertem Restart zu;
- ein bereits durable Journal-Record wird exakt materialisiert und nie
  fachlich neu entschieden;
- Resource-Fehlersemantik und Tests binden dieselbe Akzeptanzgrenze.

**Betroffene V3-Abschnitte:** 10.3, 13.4, 18, 21.1 und 21.7.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

### NM2 — Fault Injection deckte Lifecycle-Operationen nicht ab

**Bestätigter Konflikt:** V2 prüfte OPEN/CLOSE/PROGRESS/KILL/ENTRY_VETO, aber
nicht Genesis, beide Handoffs, V1→V2-Migration, Recovery-Materialisierung oder
Restart-Authorization-Consumption.

**Resolution in V3:** Die Pflichtmatrix enthält nun Crashpunkte:

- vor und nach `RESTART_AUTH_CONSUME` einschließlich Duplicate-/Payload-
  Konflikt;
- an jeder durable Grenze von Atomic und Legacy Genesis;
- nach Source-Reconciliation, Lifecycle-Record und Target-Publikation beider
  Handoff-Richtungen;
- vor und nach V1→V2-Migration und Recovery-Materialisierung;
- bei konkurrierendem Lifecycle-Writer, doppelter Event-ID sowie Sequence- und
  Hash-Chain-Konflikt;
- bei kombinierten Tick-/KILL-Ereignissen und sämtlichen Pre-Accept-
  Fehlerklassen;
- mit Recovery-Invarianten für getrennte Event IDs, vollständige S4-/Owner-
  Parität und dauerhaft verbrauchte Authorizations.

**Betroffene V3-Abschnitte:** 7.6, 7.7, 9.3, 13.4, 13.6 und 21.7.

**Resolutionstatus:** `RESOLVED_PENDING_INDEPENDENT_REREVIEW`.

---

## 7. Vollständigkeits- und Scope-Nachweis

```text
REREVIEW_FINDINGS_MAPPED: 7/7
RESIDUAL_BLOCKERS_MAPPED: 2/2
NEW_HIGH_FINDINGS_MAPPED: 2/2
MEDIUM_FINDINGS_MAPPED: 3/3
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_3_HASHED: YES
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

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-3-INDEPENDENT-READONLY-REREVIEW`

Das neue Re-Review muss den vollständigen V3-Hash prüfen, alle sieben Findings
gegen Spezifikation, normative L0/L1-Autoritäten und beobachteten Code erneut
bewerten und den Resolution-Record selbst auf Vollständigkeit prüfen.

Erst ein bestandenes unabhängiges Re-Review kann die Spezifikation als
implementierungsbereit bewerten. Terminales R3, bestandene Final Attestation
und eine separate ausdrückliche Implementierungsfreigabe bleiben auch danach
zwingend.
