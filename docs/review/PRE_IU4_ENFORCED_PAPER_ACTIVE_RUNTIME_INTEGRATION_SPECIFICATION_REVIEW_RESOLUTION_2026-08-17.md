# PRE-IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION — REVIEW RESOLUTION

- **Datum:** 2026-08-17
- **Status:** REVIEW FINDINGS RESOLVED IN REVISION 2 — INDEPENDENT REREVIEW REQUIRED
- **Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Reviewziel:** `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md`
- **Unabhängig geprüfter V1-Hash:** `50f569fb907b757d61308af9cd2c7b0dc2ff60853000564d75f3d4015f8e5d56`
- **Resolution-Zielhash V2:** `b330d6cb45c418dd937adaf8f483337b8cba2e250a8150c6b0d43e25bcbfc348`
- **Implementierungsfreigabe:** NEIN
- **ENFORCED-/Exchange-/Live-Freigabe:** NEIN

---

## 1. Zweck

Dieses Dokument ordnet jedes Finding des unabhängigen read-only Reviews der
Revision 1 einer konkreten normativen Korrektur in Revision 2 zu.

Es zertifiziert die Korrekturen nicht selbst. Die Resolution gilt erst nach
einem neuen unabhängigen read-only Review des vollständigen V2-Hashes als
geschlossen.

Weder Runtime-Code noch R3-Output, reale Research-Inputs, Profile oder aktive
State-Artefakte wurden im Resolution-Schritt verändert.

---

## 2. Reviewausgang

Das unabhängige Review des exakten V1-Hashes endete mit:

```text
REVIEW_RESULT: NOT_READY
BLOCKER: 3
HIGH: 3
MEDIUM: 1
LOW: 0
```

Die Findings wurden anschließend lokal gegen die zitierten L0/L1-Autoritäten
und Runtime-Schnittstellen reproduziert. Kein Finding wurde herabgestuft oder
als nicht anwendbar verworfen.

---

## 3. Resolution der Blocker

### B1 — HARD/EMERGENCY widersprachen L0/L1

**Bestätigter Konflikt:** V1 behandelte jeden Kill-Level als Entry-Sperre mit
weiterhin zulässigen Exits. L0/L1 verlangen dagegen:

- `SOFT`: keine neuen Orders;
- `HARD`: Trading-Loop sofort stoppen;
- `EMERGENCY`: Prozess sofort beenden und kein Auto-Restart.

**Resolution in V2:**

- Exits bleiben nur unter nichtterminalen Entry-Sperren fail safe.
- HARD beendet den Loop vor weiterer Snapshot-/Intent-/Exit-Verarbeitung.
- EMERGENCY beendet den Prozess.
- Eine offene PEE-Position bleibt autoritativ OPEN und kann nur nach dem
  manuellen L1-D-Restart-/Recovery- und gegebenenfalls Kill-Reset-Prozess
  fortgesetzt werden.
- Testmatrix, Fehlersemantik und Rollback wurden entsprechend korrigiert.

**Betroffene V2-Abschnitte:** 4, 7.5, 9, 9.2, 15, 16.2, 18, 21.4, 22.3 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

### B2 — Startup-Recovery war nicht L1-D-konform manuell autorisiert

**Bestätigter Konflikt:** Eine Boolean-Flag plus Activation Authorization
bildete Ursachenanalyse, gesicherte Logs, bekannte Kill-Level, dokumentierten
State, ausgeschlossene offene Intents, Environment-Prüfung, verantwortlichen
Operator und manuelle Restart-Entscheidung nicht ab.

**Resolution in V2:**

- additive `IU4RestartRecoveryAuthorizationV1`;
- getrennter Payload-/Trust-Anchor-Vertrag;
- Operation exakt `RESTART_ONLY` oder `RECOVER_AND_RESTART`;
- Bindung an Verantwortlichen, Stopgrund, Log-Manifest, Environment-Check,
  Pre-State, Journal Head, Profile und Gültigkeitsfenster;
- Activation Authorization allein kann keine Recovery auslösen;
- Recovery darf ausschließlich einen bereits durable committeten Journal-Head
  deterministisch wieder als Snapshot materialisieren;
- jede Authorization ist pre-state-gebunden und nach Verwendung verbraucht;
- Clean Genesis ist die einzige ausdrücklich attestierte Erststart-Ausnahme.

**Betroffene V2-Abschnitte:** 7.6, 8.3, 9, 17, 18, 19, 20, 21.5, 22 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

### B3 — Handoff ignorierte S4, Loss Cluster und Throttle

**Bestätigter Konflikt:** Die V1-Matrix verglich nur Legacy S2 mit Atomic S2.
Kill-Level, Cooldown, Loss-Cluster-Pause, Throttle-Heads und Rollback konnten
dadurch verloren gehen.

**Resolution in V2:**

- persistierter `state_owner_epoch` (`LEGACY` oder `PEE`);
- `IU4StateHandoffManifestV1` für `LEGACY_TO_PEE` und `PEE_TO_LEGACY`;
- vollständige Matrix aus Owner Epoch, Legacy S2, Atomic S2 und Safety Heads;
- höherer Kill-Level gewinnt; HARD/EMERGENCY verhindern Loop-Start;
- späterer Cooldown gewinnt;
- Legacy Loss Cluster ist beim ersten Handoff die autoritative Quelle;
- strengere nichtautoritative Pause darf nicht still verworfen werden;
- Legacy Trade-Zähler/Cooldown müssen verlustfrei in Atomic Throttle abgebildet
  werden oder ENFORCED bleibt gesperrt;
- direkter Rollback auf stale Legacy-Risk-State ist verboten;
- Legacy-exit-only hält Legacy S4/Loss bis zum Close autoritativ und verlangt
  anschließend einen vollständigen neuen Handoff.

**Betroffene V2-Abschnitte:** 4, 7.2, 8.3, 9.1, 9.2, 10, 13, 17, 18, 21.6,
22.3 und 23.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

---

## 4. Resolution der High Findings

### H1 — Settlement besaß kein vollständiges gespeichertes Entry Quote

**Bestätigter Konflikt:** `settle_trade()` benötigt ein vollständiges
`EntryEconomicsQuote`; S2 V2 enthält nur eine Teilmenge. Der V1-Text verbot eine
Neuberechnung, spezifizierte aber kein speicherbares Quote-Artefakt.

**Resolution in V2:**

- additives `EntryEconomicsQuoteArtifactV1` in `paper_artifacts.py`;
- vollständige kanonische Decimal-Serialisierung und Quote Fingerprint;
- OPEN committed S2, vollständiges Quote, Throttle und Progress gemeinsam;
- Atomic S2 OPEN verlangt genau ein Quote, FLAT verlangt `null`;
- gemeinsame S2-/Quote-Felder müssen exakt identisch sein;
- CLOSE deserialisiert genau das committed Quote;
- erneutes `authorize_entry()` beim Close ist ausdrücklich verboten;
- `paper_artifacts.py` wurde in den späteren Dateiscope aufgenommen.

**Betroffene V2-Abschnitte:** 13.1, 13.2, 13.3, 14, 15, 17, 19, 20, 21.3 und
23.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

### H2 — Execution Seam erfasste nicht alle Legacy-Schreibpfade

**Bestätigter Konflikt:** Ein Branch nur um `apply_paper_execution()` hätte
weiterhin Legacy `state.last_*`, S2/S4, `persist_state()`, Loss Cluster und
passive Sidecars geschrieben.

**Resolution in V2:**

- vollständige mode-basierte Side-Effect-Tabelle;
- ENFORCED verbietet Legacy Execution, Loss Mutation, S2/S4-Mutation,
  `persist_state()`, Trade-/Audit-Schreiben, passive Sidecars und Shadow
  Observer;
- gemeinsame Market-/Regime-/Intent-Logs bleiben nur read-only zulässig;
- `AtomicProgressCursorV1` übernimmt Snapshot-/Tick-/Intent-Fortschritt;
- neuer Transaktionstyp `PROGRESS` für ansonsten nicht mutierende Ticks;
- OPEN/CLOSE/KILL/ENTRY_VETO tragen auf mutierenden Ticks denselben Cursor;
- jeder ENFORCED-Tick besitzt genau eine Atomic-V2-Transaktion;
- Testmatrix verlangt Negativnachweise für alle Legacy-Writes.

**Betroffene V2-Abschnitte:** 4, 10.1, 10.2, 13.1, 13.3, 14, 15, 17, 18, 19,
20, 21.1 und 21.7.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

### H3 — Legacy exit-only hatte keine eindeutige Control-Quelle

**Bestätigter Konflikt:** V1 verbot ungebundene Environment-Defaults, erlaubte
für die Legacy-Altposition aber die bestehende Resolver-Semantik ohne eigenen
Vertrag.

**Resolution in V2:**

- additives, positiongebundenes `IU4LegacyExitOnlyControlBindingV1`;
- explizite TP-/SL-/Time-stop-/Opposing-intent- und Loss-Cluster-Werte;
- Bindung an Config-/Environment-Quelle, Position und Fingerprint;
- keine Defaults;
- fehlende historische Konfiguration erzwingt manuelle Recovery-/Exit-
  Entscheidung;
- das PEE Runtime-Control-Profil darf die Altposition nicht rückwirkend
  umdefinieren;
- HARD/EMERGENCY verhindern auch den Legacy-exit-only-Loop.

**Betroffene V2-Abschnitte:** 7.2, 9.2, 11, 18, 21.2 und 22.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

---

## 5. Resolution des Medium Findings

### M1 — Clean Genesis band nicht den vollständigen Schutzstate

**Resolution in V2:** Das Genesis-Manifest bindet nun zusätzlich:

- Coordinator-/System-State-ID und Owner Epoch;
- vollständiges S2 FLAT;
- explizites S4 samt Kill-Level und Reasons;
- Loss Cluster samt Revision;
- Throttle-Heads und Cooldown;
- Progress Cursor;
- Transaction Sequence 0, leeren Journal Head und nachgewiesen leeres Journal;
- alle Cross-State-Fingerprints und Pfade;
- Abwesenheit konkurrierender Heads;
- Operator, Zeitpunkt und getrennte Approval Reference.

Kein Genesis-Feld darf aus einem Runtime-Default ergänzt werden.

**Betroffene V2-Abschnitte:** 9.3, 13.5, 18, 21.6 und 22.

**Resolutionstatus:** `RESOLVED_PENDING_REREVIEW`.

---

## 6. Zusätzliche Konsistenzschärfungen

Die Resolution schließt zusätzlich folgende unmittelbar abhängige Lücken:

- Triggerpriorität wurde exakt auf die charakterisierte Legacy-Reihenfolge
  festgelegt;
- Activation Authorization V2 bindet Owner Epoch, Handoff/Genesis und bei
  Bedarf die Legacy-exit-only-Control-Binding;
- Monitoring und Audit binden Restart Authorization, Handoff, Entry Quote und
  Progress Cursor;
- Rollback ist ein expliziter Safety-State-Handoff, kein Modusschalter;
- neue stabile Reason Codes unterscheiden Restart, Recovery, Handoff Safety,
  Owner Epoch, Entry Quote und Progress Conflict.

---

## 7. Verification Boundary

Der Resolution-Schritt erlaubt genau folgende Aussage:

```text
REVIEW_FINDINGS_MAPPED: 7/7
NORMATIVE_RESOLUTIONS_APPLIED: YES
REVISION_2_HASHED: YES
INDEPENDENT_REREVIEW_PASSED: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Es wurden keine Runtime-Tests ausgeführt, weil ausschließlich Dokumentation
geändert wurde. Formale Datei-, Whitespace-, Hash- und Git-Scope-Prüfungen sind
zulässig; eine semantische Zertifizierung durch den Autor ist es nicht.

---

## 8. Nächster Gate

Der nächste zulässige Schritt ist:

`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-INDEPENDENT-READONLY-REREVIEW`

Das Re-Review muss den vollständigen V2-Hash prüfen und jedes der sieben
ursprünglichen Findings entweder als geschlossen oder mit präzisem
Restfinding bewerten. Erst ein bestandenes Re-Review kann die Spezifikation in
einen review-fähigen Abschlusszustand überführen; R3-Final-Attestation und eine
separate Implementierungsfreigabe bleiben danach weiterhin erforderlich.
