# LIVE DESIGN — IU4 ENFORCED PAPER ACTIVE RUNTIME INTEGRATION SPECIFICATION

- **Spezifikations-ID:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-V21`
- **Datum:** 2026-08-19
- **Status:** REVISION 21 — REVISION-20 REREVIEW RESOLUTION APPLIED; INDEPENDENT REREVIEW REQUIRED
- **Geprüfter Repository-Basisstand:** `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595`
- **Geltungsbereich:** `live_l1` Paper Runtime, ausschließlich `OFF`, `SHADOW` und zukünftiges `ENFORCED PAPER`
- **Exchange-/Echtgeld-Live-Freigabe:** NEIN

---

## 1. Zweck und Entscheidung

Diese Spezifikation definiert den kleinsten zulässigen Integrationsweg, mit dem
die bereits implementierten Decimal-Paper-Komponenten zukünftig die aktive
`live_l1`-Runtime im Modus `ENFORCED` übernehmen dürfen.

Sie schließt den dokumentierten Gap zwischen:

- der aktiven Legacy-Paper-Ausführung in `live_l1/core/loop.py` und
  `live_l1/core/execution.py`,
- dem reinen IU4-Startup-Vertrag,
- dem heute ausschließlich `OFF`/`SHADOW` erlaubenden aktiven Runtime-Bridge,
- dem `PaperIU4Adapter`,
- dem `PaperAtomicCoordinator`,
- S2 V2, Paper Account, Entry Throttle und Decimal Paper Execution Economics.

Die zentrale Entscheidung lautet:

> Im Modus `ENFORCED PAPER` existiert genau ein wirtschaftlicher und
> persistierender Owner: Decimal PEE über den atomaren IU4-Pfad. Der Legacy-Pfad
> darf denselben Trade weder öffnen, bemessen, abrechnen, persistieren noch als
> autoritative Economics loggen.

Dieses Dokument ist eine Spezifikation, keine Implementierung, keine
R3-Attestation und keine Betriebsfreigabe. Kein Runtime-Modus wird durch seine
Existenz aktiviert.

---

## 2. Normative Autorität und Konfliktordnung

Bei Widersprüchen gilt folgende Reihenfolge:

1. eingefrorene L0/L1-Sicherheits-, State-, Recovery- und Review-Regeln,
   insbesondere `LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`,
   `LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md`,
   `LIVE_DESIGN_L0_STATE_MODEL.md`,
   `LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md` und
   `LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md`;
2. `LIVE_DESIGN_PAPER_EXECUTION_ECONOMICS_V1.md`;
3. `PRE_IU4_FLOAT_DECIMAL_OWNERSHIP_DECISION_2026-08-09.md`;
4. diese Integrationsspezifikation für die aktive IU4-Runtime-Verkabelung;
5. akzeptierte, versionsgebundene PRE-IU4-Verträge und Evidenz für einzelne
   Komponenten;
6. der aktuelle Code als beobachteter Implementierungsstand, nicht als
   Berechtigung, höherrangige Regeln abzuschwächen.

Bestehende L0/L1-Dokumente werden nicht still geändert. Diese Spezifikation ist
ein eigenständiger Post-L1-Schritt mit eigenem späterem Implementierungs- und
Abnahmeverfahren.

Revision 2 adressierte die Findings des unabhängigen read-only Reviews des V1-Hashes
`50f569fb907b757d61308af9cd2c7b0dc2ff60853000564d75f3d4015f8e5d56`.
Sie beansprucht keine Selbstzertifizierung; ein erneutes unabhängiges Review des
neuen vollständigen Hashes bleibt Pflicht.

Revision 3 adressierte die Rest- und Neufindings des unabhängigen Re-Reviews des
V2-Hashes `b330d6cb45c418dd937adaf8f483337b8cba2e250a8150c6b0d43e25bcbfc348`.
Auch diese Resolution benötigt ein neues unabhängiges Review ihres vollständigen
Hashes.

Revision 4 adressiert die Rest- und Neufindings des unabhängigen read-only
Re-Reviews des V3-Hashes
`3a12e977bc7fe64b0341dc4ca5b5f562fef18598b8afedae5f4d4dbdd6bd23c6`.
Insbesondere trennt sie den veränderlichen Ledger Tip von der committed
Authority Generation, beseitigt die Record/Target-Hash-Selbstreferenz und
definiert terminales Fail-closed-Verhalten bei nicht persistierbarem KILL.
Auch Revision 4 benötigt ein neues unabhängiges Review ihres vollständigen
Hashes.

Revision 5 adressiert die Rest- und Neufindings des unabhängigen read-only
Re-Reviews des V4-Hashes
`fe9f6872403754961919941ed05436bfbea7ba013da63486c1b006efb24362fe`.
Sie autorisiert die exakte Fertigstellung offener Authority-PREPAREs, ordnet
Terminal-Gap-Recovery journal-first, begrenzt den EMERGENCY-Exit unabhängig von
blockierendem I/O und schließt die Authority-Root-Testlücke. Auch Revision 5
benötigt ein neues unabhängiges Review ihres vollständigen Hashes.

Revision 6 adressiert die letzten Befunde des unabhängigen read-only Re-Reviews
des V5-Hashes
`a544b0a83b4b6f13df8cb3f3bd6d75b4836655fb4108a6d85b992f4e598e7dde`.
Sie bindet die Clean-Genesis-Erststartausnahme an eine eindeutige Completion-
Provenance und ersetzt den alleinstehenden Watchdog durch einen OS-erzwungenen
Parent-Guardian-Lebensdauervertrag. Auch Revision 6 benötigt ein neues
unabhängiges Review ihres vollständigen Hashes.

Revision 7 adressiert die Rest- und Neufindings des unabhängigen read-only
Re-Reviews des V6-Hashes
`d0781659f5ccfdf446473238b29c1a51fa2203179e368d431cb5e5ffd5a28d54`.
Sie bindet die DIRECT-Genesis-Ausnahme an dieselbe lebende Prozessinstanz,
ersetzt die selbstüberwachte Guardian-Lease durch eine kernel-armed
Self-Death-Lease samt synchroner Side-Effect-Sperre, grenzt Termination-
Anforderung und physisches Process Reaping voneinander ab und korrigiert die
Reviewidentität. Auch Revision 7 benötigt ein neues unabhängiges Review ihres
vollständigen Hashes.

Revision 8 adressiert die Rest- und Neufindings des unabhängigen read-only
Re-Reviews des V7-Hashes
`a9e10855a18bce9131863482ae1473f37d201576c193c7fc775e0fdfe6e0798f`.
Sie verbindet den EMERGENCY-Latch und jede Lease-Renewal durch ein einziges
prozessübergreifendes atomisches Control Word, definiert den nicht verlierbaren
Child→Guardian-/Shim-Trip und ersetzt den unbestimmten Worst-Case-Preflight
durch ein endliches, exakt berechenbares Capability-Envelope. Auch Revision 8
benötigt ein neues unabhängiges Review ihres vollständigen Hashes.

Revision 9 adressiert das verbleibende High-Finding des unabhängigen read-only
Re-Reviews des V8-Hashes
`d5459835b42dc4c4b4b31b24403c7aa0b7f59ea9035154bafeefbf3fab32d197`.
Sie ersetzt die nicht erzwingbare thread-exklusive Control-Word- und
Worker-Request-Autorität durch einen separaten attestierten Native Trip Broker,
OS-erzwungene Memfd-Mapping-Rechte und einen vom Worker selbst geprüften
Trip-CAS-Nachweis. Auch Revision 9 benötigt ein neues unabhängiges Review ihres
vollständigen Hashes.

Revision 10 adressiert den Blocker und das Medium-Finding des unabhängigen
read-only Re-Reviews des V9-Hashes
`fc9a947274395a38fd287411ec171c1b1dc624f8ddfc7364ce3437ecf93e91b1`.
Sie ergänzt für jeden nicht sicher übertragenen Trip-Pipe-Record einen
kernel-seitigen Self-PIDFD-/broker-sichtbaren HUP-Fallback und bindet die
Memfd-Erzeugung samt initialem Seal-State und jeder erlaubten Seal-Transition
vollständig. Auch Revision 10 benötigt ein neues unabhängiges Review ihres
vollständigen Hashes.

Revision 11 adressiert den Blocker des unabhängigen read-only Re-Reviews des
V10-Hashes
`559e4679ab3927cc169c92ac91fada4294e5574a07bf78bf07c771cd0f2731d2`.
Sie schließt jede Post-OPEN-Prozess-/Thread-Erzeugung und jede alternative
Kernel-Referenz auf das Trip-Pipe-Write-Ende durch eine feste vor OPEN
attestierte Task-/FD-Topologie und vollständig sperrende Seccomp-/FD-
Capability-Grenzen. Damit bleibt der HUP-/EOF-Pfad auch bei erzwungenem
Self-PIDFD-Fehler OS-erzwungen ausführbar. Auch Revision 11 benötigt ein neues
unabhängiges Review ihres vollständigen Hashes.

Revision 12 adressiert den Blocker und das Medium-Finding des unabhängigen
read-only Re-Reviews des V11-Hashes
`a84efdb53f324d2e67f214d64edce1665a8e4a39525e93b7d94b441fc777607d`.
Sie ersetzt die frei wählbare Pipe-Write-/Read-Bufferoberfläche durch exakt
adressgebundene, vorgefaultete und gelockte native Acht-Byte-Buffer, sperrt jede
abweichende Pointer- oder Mappingoperation kernel-seitig und vereinheitlicht
alle Implementierungs- und Abschlussgates auf die aktuelle Vertragsfamilie.
Auch Revision 12 benötigt ein neues unabhängiges Review ihres vollständigen
Hashes.

Revision 13 adressiert den Blocker des unabhängigen read-only Re-Reviews des
V12-Hashes
`3b46f32ed460033bce6d81284a2f9e4d211b48962dd7c5e552658a38a4c445a3`.
Sie entfernt jeden Pipe-Write aus dem terminalen Sicherheitsweg, macht die
unmittelbare Self-PIDFD-`SIGKILL`-Anforderung zum ersten Kernelaufruf nach dem
lokalen Latch und verwendet die dauerhaft leere Pipe ausschließlich als
Close-only-Liveness-Kanal hinter zwei weiteren PIDFD-Kill-Fallbacks. Damit
existieren weder Pipe-Page-Allokation noch Reclaim-/Write-/Bufferpfade vor einer
kernel-seitigen Fatal-Action. Auch Revision 13 benötigt ein neues unabhängiges
Review ihres vollständigen Hashes.

Revision 14 adressiert die zwei Blocker des unabhängigen read-only Re-Reviews
des V13-Hashes
`e8c14a631928914c823a046dc5a85972dfccbbbd48e41897e66926db3e5f1f66`.
Sie macht den lokalen Trip-Latch für den bereits reservierten Native Shim
kontinuierlich sichtbar, sodass ein Halt des Gewinner-TID unmittelbar nach der
Latch-CAS keine Timer-Renewal offenhält. Außerdem ersetzt sie den voreiligen
durable Session CLOSE durch PREPARE, Broker-CLOSED und erst danach einen
durablen CLOSE-COMMIT; nur dieser Commit klassifiziert die Session als clean.
Auch Revision 14 benötigt ein neues unabhängiges Review ihres vollständigen
Hashes.

Revision 15 adressiert die zwei Blocker und das High-Finding des unabhängigen
read-only Re-Reviews des V14-Hashes
`ec7e86923e1fc440208dd0b65f4215e22badd62dcfb69e2c0d2e17b7457293e5`.
Sie entfernt den nicht OS-erzwingbar monotonen writable In-Process-Latch und
ersetzt ihn durch eine kernel-erzeugte Seccomp-User-Notification, deren
Listener und monotone Trip-Autorität ausschließlich der separate Broker
besitzt. Sie vervollständigt außerdem die skalare Seccomp- und die getrennte
Userspace-Payloadautorität aller Close-Kanäle und definiert eine endliche,
idempotente Fehlerzustandsmaschine für Requests, ACKs und beide Approvals.
Auch Revision 15 benötigt ein neues unabhängiges Review ihres vollständigen
Hashes und zertifiziert sich nicht selbst.

Revision 16 adressiert den Blocker und das High-Finding des unabhängigen
read-only Re-Reviews des V15-Hashes
`34637e2e51b63f8d386d0eb04acf74bd34a1e805eaea317e156cd87f5eece25a`.
Sie schließt das pre-Receive-Signalabbruchfenster der Seccomp-Notification
durch `SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV`, einen vor jeder weiteren
TID-Erzeugung vollständig gebundenen Signalzustand und terminale Broker-
Klassifikation jedes Listener-Ready-/Receive-Fehlers. Sie ersetzt außerdem
per-message `SO_PASSCRED`/`SCM_CREDENTIALS` durch nach Start der finalen
Rollenprozesse aufgebaute, feste `SO_PEERCRED`-Verbindungen. Jeder Runtime-
Receive besitzt absichtlich keinen Ancillary-Controlbuffer, sodass übertragene
`SCM_RIGHTS`-Deskriptoren kernelseitig geschlossen werden und kein
userspace-sichtbarer FD den Syscall-Return überlebt. Auch Revision 16 benötigt
ein neues unabhängiges Review ihres vollständigen Hashes und zertifiziert sich
nicht selbst.

Revision 17 adressiert das verbleibende High-Finding des unabhängigen
read-only Re-Reviews des V16-Hashes
`093207ce1fbef6d09a372d250f23d17181f0974408632354b53c463048c30c0f`.
Sie ersetzt die erst bei `recvmsg` wirksame alleinige Rights-Entsorgung durch
eine vor Ready attestierte Kernel-Barriere: Jeder endgültige
AF_UNIX-Empfangsendpunkt muss `SO_PASSRIGHTS=0` besitzen. Linux weist dadurch
jeden `SCM_RIGHTS`-Send mit `EPERM` ab und verwirft das Paket vor dem Einreihen
in die Receive Queue. Ein gestoppter oder abgestürzter Empfänger kann daher
keine übertragene file-/Open-File-Description-/Lock-Referenz festhalten. Der
absente Receive-Controlbuffer bleibt nur Defense in Depth. Auch Revision 17
benötigt ein neues unabhängiges Review ihres vollständigen Hashes und
zertifiziert sich nicht selbst.

Revision 18 adressiert das verbleibende High-Finding des unabhängigen
read-only Re-Reviews des V17-Hashes
`ffcff6348b2427ec69a227ca36035a92b2e723664f14b692a1aba9bfef112b64`.
Sie verschiebt den letzten `SO_PASSRIGHTS=0`-, Queue-, FDINFO-, OFD- und
Lock-Nachweis hinter eine irreversible, per TSYNC auf sämtliche bereits
vollständig fixierten Empfänger-TIDs installierte `setsockopt`-Sperre. Erst
dieser post-Filter-Snapshot darf die gestoppten Sender freigeben und
`RUNTIME_SESSION_OPEN` autorisieren. Jeder vorher eingereihte Queue-Rest
bricht den gesamten Startup-Versuch ab und verlangt nachgewiesene Socket-/
Queue-Zerstörung sowie vollständige Referenzfreigabe. Auch Revision 18
benötigt ein neues unabhängiges Review ihres vollständigen Hashes und
zertifiziert sich nicht selbst.

Revision 19 adressiert das verbleibende High-Finding des unabhängigen
read-only Re-Reviews des V18-Hashes
`6d87fbe8921ff7d430bc05b1ed25b060013a866be710986d50b64c9898822663`.
Sie ersetzt den sequenziellen hostweiten `/proc`-/Referenzsnapshot als
Sicherheitsgrenze durch `TerminalRuntimeSocketLSMGuardV1`: einen vor jeder
Rollen- und Socket-Erzeugung global angehängten BPF-LSM-Vertrag. Seine
socketlokale Kernelmarkierung entsteht vor Userspace-FD-Sichtbarkeit; der
LSM-Hook `socket_setsockopt` linearisiert und versiegelt den einzigen
Bootstrap-Setzvorgang vor jeder Optionskopie/-mutation und verweigert danach
weltweit jeden weiteren `setsockopt` auf dem geschützten Socket. Eine zweite
LSM-Grenze verweigert bis nach durablem `RUNTIME_SESSION_OPEN` jeden
Session-`sendmsg`/`sendmmsg`-Pfad. Sender werden erst durch eine einmalige
kernelgebundene `BOOTSTRAP→RELEASED`-Transition freigegeben. Damit können
weder ein fremder, nur kernel-in-flight gehaltener Options-Caller noch ein
vorab in einer fremden Queue geparkter Endpoint-/Rights-SKB den finalen
Nachweis überleben. Auch Revision 19 benötigt ein neues unabhängiges Review
ihres vollständigen Hashes und zertifiziert sich nicht selbst.

Revision 20 adressiert die zwei High-Findings des unabhängigen read-only
Re-Reviews des V19-Hashes
`191e9761c20d691d4015b6385ebe5a761b0210c2193d7d4b3cbfae7f388ba22b`.
Sie entfernt den widersprüchlichen `sendmsg`-basierten Seccomp-Listener-
Transfer vollständig: Der Broker dupliziert den exakt reservierten Listener-
FD einmalig per `pidfd_getfd` innerhalb eines minimalen, vor jeder Runtime-
Socket-Erzeugung irreversibel geschlossenen Ptrace-/Dumpable-Fensters. Sie
ersetzt außerdem die nicht an Linux-UAPI gebundene Userspace-Map-CAS durch
eine programmseitige `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`-Transition im globalen
`socket_shutdown`-LSM-Hook auf einer für Userspace eingefrorenen Phasen-Map.
Der Session-`sendmsg`-Gate bleibt dadurch ohne Bootstrap-Ausnahme vollständig
geschlossen. Auch Revision 20 benötigt ein neues unabhängiges Review ihres
vollständigen Hashes und zertifiziert sich nicht selbst.

Revision 21 adressiert das verbleibende High-Finding des unabhängigen
read-only Re-Reviews des V20-Hashes
`18f9bacc3a3d12acddbe1e090ef95a29d0b830078b0539b48146f477bfdbeee0`.
Sie ersetzt die vom richtigen Guard zu früh ausführbaren direkten
`LISTENER_RECEIVED→BOOTSTRAP`- und `BOOTSTRAP→RELEASED`-Transitionen durch
eine sechsstufige, kernelgebundene Grant-FSM. Ein separater
`TerminalHandoffRevocationAttestorV1` muss zuerst
`HANDOFF_REVOKED_GRANTED` erzeugen; der Persistence Owner muss nach dem
durablen OPEN-Commit getrennt `OPEN_DURABLE_GRANTED` erzeugen. Der Guard kann
keinen dieser Grants selbst ausstellen und darf sie nur durch zwei
nachgelagerte CMPXCHG-Transitionen konsumieren. Damit scheitert derselbe
korrekte Guard-Aufruf vor dem fremd ausgestellten Grant ohne Phase-Mutation,
Runtime-Socket- oder Sendewirkung. Auch Revision 21 benötigt ein neues
unabhängiges Review ihres vollständigen Hashes und zertifiziert sich nicht
selbst.

---

## 3. Voraussetzungen und Aussagegrenzen

### 3.1 Voraussetzungen für eine spätere Implementierung

Vor der ersten Codeänderung müssen alle folgenden Bedingungen erfüllt sein:

1. terminaler R3-Handoff liegt vor;
2. der eingefrorene Postrun-Validator wurde gemäß Operational Freeze exakt
   einmal auf dem terminalen Artefakt ausgeführt;
3. die Final Attestation bewertet R3 als `PASS`;
4. Code-, Input-, Profil- und Evidence-Identitäten sind vollständig;
5. ein eigenes, dateigenaues Implementierungsmandat wurde erteilt.

Ein noch laufender, abgebrochener, unvollständiger oder nicht attestierter R3
ist kein PASS und autorisiert keine Implementierung.

### 3.2 Voraussetzungen für eine spätere Aktivierung

Zusätzlich zur implementierten und zertifizierten Integration werden benötigt:

- ein neues, ausdrücklich für `ENFORCED PAPER` genehmigtes Economics-Profil;
- ein ausdrücklich runtime-aktiviertes und IU4-ENFORCED-autorisiertes
  Throttle-Profil;
- ein genehmigtes Runtime-Control-Profil für Stop- und Exit-Semantik;
- eine vollständige Activation Authorization V2;
- bestandene Fault-Injection-, Full-Suite-, Regression- und Workstation-Gates;
- unabhängige Reviews auf exakt demselben Commit und Evidence-Stand;
- eine separate menschliche Betriebsfreigabe.

### 3.3 Nicht behauptete Ergebnisse

Diese Spezifikation beweist weder Profitabilität noch Exchange-Tauglichkeit,
Orderausführungsqualität, künftige Live-Performance oder R3-Erfolg.

---

## 4. Harte Systeminvarianten

Die spätere Implementierung muss alle folgenden Invarianten gleichzeitig
erfüllen:

1. **Single Owner:** Pro Modus existiert genau ein autoritativer
   Execution-/Economics-/State-Owner.
2. **Kein Dual Write:** Legacy S2/S4/Trade-Log und atomarer PEE-State dürfen
   niemals denselben Trade parallel autoritativ verändern.
3. **Decimal Boundary:** Canonical Price, Quantity, Fill, Fee, Notional,
   Settlement, Equity und realisierte PnL passieren keine Float-Rückkonvertierung.
4. **Float nur für Strategie/Trigger:** Bestehende Float-Semantik darf für
   Strategie- und reine Triggerentscheidungen erhalten bleiben, ist aber keine
   wirtschaftliche Autorität.
5. **Entries fail closed:** Fehlende, ungültige, unvollständige, abgelaufene
   oder widersprüchliche Daten blockieren neue Entries.
6. **Exits fail safe innerhalb des laufenden Loops:** SOFT-, Account-,
   Throttle-, Loss-Cluster- und andere reine Entry-Sperren blockieren keine
   risikoreduzierenden Exits. `HARD` beendet dagegen gemäß L0/L1 den
   Trading-Loop sofort; `EMERGENCY` beendet den Prozess. Unter diesen beiden
   terminalen Kill-Leveln wird kein weiterer automatischer Exit berechnet.
7. **Exactly once und terminal fail closed:** OPEN, CLOSE, PROGRESS,
   persistierbare KILLs und zustandsverändernde Entry-Vetos sind idempotent und
   journalgebunden. Ist ein terminaler KILL wegen desselben Ressourcenfehlers
   nicht persistierbar, erzwingt die bereits durable Runtime Session den
   gesperrten nächsten Startup und eine manuelle Terminal-Gap-Reconciliation.
8. **Keine automatische Promotion:** `SHADOW` wird niemals automatisch zu
   `ENFORCED`.
9. **Keine Production-Rechte:** `PRODUCTION`, Exchange und echte Orders bleiben
   unabhängig vom IU4-Modus gesperrt.
10. **Keine stillen Defaults:** In `ENFORCED` existiert kein Fallback für
    Profil, Preis, Stop, Quantity, Fee, Slippage, Zeitlimit oder Autorisierung.
11. **Gebundene Identität:** Commit, Symbol, Coordinator, Economics, Throttle,
    Runtime Control, R3-Attestation und Freigabe müssen dieselbe autorisierte
    Identitätskette bilden.
12. **Reproduzierbare Projektion:** Audit- und Legacy-Kompatibilitätsausgaben
    werden ausschließlich aus bereits committeten Decimal-Artefakten abgeleitet.
13. **Monotone Schutzübernahme:** Moduswechsel, Restart, Recovery, Genesis oder
    Rollback dürfen Kill-Level, Cooldown, Loss-Cluster-Pause oder Throttle-Heads
    weder verlieren noch still zurücksetzen.

---

## 5. Betriebsmodi und Ownership

| Modus | Execution Owner | Economics/State Owner | Adapter-Mutation | Zulässigkeit |
|---|---|---|---:|---|
| `OFF` | Legacy | Legacy | nein | bestehender Pfad |
| `SHADOW` | Legacy | Legacy | nein | bestehender Pfad plus isolierte read-only Beobachtung |
| `ENFORCED` + PEE-State | IU4 Execution Control + Adapter | Atomic Decimal PEE | ja | nur nach vollständigem Gate |
| `ENFORCED` + Legacy-Open | Legacy exit-only | Legacy nur für diese Altposition | nein für PEE-Entries | temporärer Handoff-Zustand |
| unbekannt/mehrdeutig | keiner | keiner | nein | Startup FAIL |

### 5.1 `OFF`

- Bestehende Legacy-Semantik bleibt unverändert.
- Kein IU4-Coordinator-State wird mutiert.
- Eine Activation Authorization ist unzulässig.

### 5.2 `SHADOW`

- Legacy bleibt alleiniger Execution- und State-Owner.
- Der IU4-Observer arbeitet nur auf einem gebundenen, isolierten Sandbox-State.
- Source S2, S4, Account, Throttle und Trade-Ergebnis bleiben unverändert.
- Die vorhandenen Shadow-Akzeptanzverträge bleiben bindend.

### 5.3 `ENFORCED`

- `PaperIU4Adapter` und `PaperAtomicCoordinator` bilden den einzigen
  mutierenden Paper-Ausführungspfad.
- `apply_paper_execution()` darf für PEE-Positionen weder direkt noch indirekt
  aufgerufen werden.
- `position_size=1.0` ist in diesem Pfad nicht erreichbar.
- Legacy Economics, Legacy Fee-Abzug und Legacy Trade-Logging sind nur noch
  nichtautoritative Kompatibilitätsausgaben nach erfolgreichem Atomic Commit.

### 5.4 Ungültiger Modus

Leere oder unbekannte Moduswerte dürfen nur als `OFF` behandelt werden, wenn
der Operator keinen IU4-Modus angefordert hat. Jeder explizite ungültige Wert
führt zu `SAFE_LAUNCH: FAIL`.

---

## 6. Profil- und Konfigurationsautorität

### 6.1 Economics

`PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001` ist eine angenommene
**SHADOW-Paper-Baseline**. Sein `PEE_MODE=SHADOW` und seine dokumentierte
Freigabe dürfen nicht still zu ENFORCED umgedeutet werden.

Vor Aktivierung ist ein neues, unveränderliches ENFORCED-Profil mit eigener ID,
kanonischem Fingerprint und ausdrücklicher Operational Approval erforderlich.
Die numerischen Werte können nach separater Entscheidung identisch sein; die
Freigabeidentität darf es nicht still sein.

### 6.2 Entry Throttle

Ein Profil mit `runtime_activated=false` oder
`iu4_enforced_authorized=false` ist für ENFORCED unzulässig. Das vorhandene
Shadow-/Observed-Boundary-Profil darf nicht in place umgeschrieben werden.

### 6.3 Runtime Control

TP, SL, LONG/SHORT Time-stop und Opposing-intent-Verhalten werden in einem
neuen, versionierten `IU4RuntimeControlProfileV15` gebunden. Das Profil enthält
mindestens:

- `schema_version`;
- `runtime_control_profile_id`;
- `symbol`;
- LONG- und SHORT-TP-Regel;
- LONG- und SHORT-SL-Regel;
- LONG- und SHORT-Time-stop in Sekunden;
- Opposing-intent-Exit-Regel;
- Stop-Preis-/Rundungsregel für PEE-Sizing;
- Loss-Cluster-Lookback, Mindestanzahl Verluste und Anzahl zu blockierender
  Entry-Kandidaten;
- `terminal_write_deadline_ms` als Integer `1..100`; `100 ms` ist die
  unveränderliche Protokollobergrenze für durable Write **oder irreversible
  Termination-Anforderung/Safety-Latch** und darf durch kein Profil erhöht
  werden; sie ist ausdrücklich keine Process-Reap-Garantie;
- `terminal_parent_guardian_required=true`;
- `terminal_kernel_self_death_lease_required=true`;
- `terminal_control_word_schema=TerminalLeaseControlWordV3`;
- `terminal_trip_broker_required=true`;
- `terminal_trip_liveness_pipe_schema=TerminalTripLivenessPipeV1`;
- `terminal_trip_liveness_pipe_permanently_empty=true`;
- `terminal_trip_liveness_pipe_write_allowed=false`;
- `terminal_trip_liveness_pipe_close_fallback=true`;
- `terminal_self_kill_entry_schema=TerminalSelfKillEntryV4`;
- `terminal_kernel_trip_request_schema=TerminalKernelTripRequestV2`;
- `terminal_kernel_trip_request_transport=SECCOMP_RET_USER_NOTIF`;
- `terminal_kernel_trip_request_listener_owner=BROKER_ONLY`;
- `terminal_kernel_trip_request_filter_flags=SECCOMP_FILTER_FLAG_NEW_LISTENER|SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV`;
- `terminal_kernel_trip_request_filter_inheritance=LEADER_BEFORE_ANY_ADDITIONAL_TRADING_TID`;
- `terminal_kernel_trip_listener_handoff_schema=TerminalSeccompListenerHandoffV2`;
- `terminal_kernel_trip_listener_handoff_transport=PIDFD_GETFD_EXACT_ONCE`;
- `terminal_kernel_trip_listener_handoff_yama_ptrace_scope=1`;
- `terminal_kernel_trip_listener_handoff_source_fd=FIXED_RESERVED`;
- `terminal_kernel_trip_listener_handoff_destination_fd=FIXED_LOWEST_FREE`;
- `terminal_kernel_trip_listener_handoff_ack=INHERITED_EVENTFD_FIXED_FD`;
- `terminal_kernel_trip_listener_handoff_runtime_socket_creation_allowed=false`;
- `terminal_kernel_trip_listener_handoff_close_order=BROKER_DUPLICATES_THEN_TRADING_CLOSES_THEN_PTRACER_AND_DUMPABLE_REVOKED`;
- `terminal_kernel_trip_request_continue_allowed=false`;
- `terminal_trading_signal_envelope_schema=TerminalTradingSignalEnvelopeV1`;
- `terminal_pre_tid_blockable_signal_mask=ALL_BLOCKABLE_SIGNALS`;
- `terminal_post_ready_signal_mask_change_allowed=false`;
- `terminal_post_ready_signal_disposition_change_allowed=false`;
- `terminal_post_ready_signal_generation_allowed=false`;
- `terminal_user_notif_pre_receive_interrupt_allowed=false`;
- `terminal_listener_ready_receive_error_action=TERMINAL_TRIP`;
- `terminal_shared_writable_trip_latch_allowed=false`;
- `terminal_self_kill_first=true`;
- `terminal_self_pidfd_failstop_required=true`;
- `terminal_self_pidfd_signal=SIGKILL`, `terminal_self_pidfd_siginfo=NULL` und
  `terminal_self_pidfd_flags=0`;
- `terminal_guardian_pidfd_fallback_required=true`;
- `terminal_guardian_pidfd_signal=SIGKILL`,
  `terminal_guardian_pidfd_siginfo=NULL` und `terminal_guardian_pidfd_flags=0`;
- `terminal_broker_pidfd_fallback_required=true`;
- `terminal_broker_pidfd_signal=SIGKILL`, `terminal_broker_pidfd_siginfo=NULL`
  und `terminal_broker_pidfd_flags=0`;
- `terminal_trip_fallback_order=SELF_PIDFD_SIGKILL_THEN_GUARDIAN_PIDFD_SIGKILL_THEN_BROKER_PIDFD_SIGKILL_THEN_LIVENESS_CLOSE`;
- `terminal_fixed_task_topology_required=true`;
- `terminal_post_ready_task_creation_allowed=false`;
- `terminal_post_ready_fd_creation_allowed=false`;
- `terminal_post_ready_fd_reference_creation_allowed=false`;
- `terminal_trading_task_topology_schema=TerminalTradingTaskTopologyV2`;
- `terminal_task_filter_apply_mode=SECCOMP_FILTER_FLAG_TSYNC`;
- `terminal_forbidden_task_or_writer_reference_action=SECCOMP_RET_KILL_PROCESS`;
- `terminal_trip_liveness_fd_syscall_allowlist=CLOSE_ONLY`;
- `runtime_session_close_protocol_schema=RuntimeSessionCloseProtocolV8`;
- `runtime_channel_provisioning_schema=TerminalRuntimeChannelProvisioningV6`;
- `runtime_channel_transport=CONNECTED_AF_UNIX_SOCK_SEQPACKET`;
- `runtime_channel_peer_authentication=SO_PEERCRED_AT_FINAL_ROLE_CONNECT`;
- `runtime_channel_so_passcred_allowed=false`;
- `runtime_channel_so_passrights=0`;
- `runtime_channel_so_passrights_authority=FINAL_ACCEPTED_RECEIVER_ENDPOINT`;
- `runtime_channel_so_passrights_inheritance_reliance=false`;
- `runtime_channel_pre_ready_send_allowed=false`;
- `runtime_channel_receiver_task_topology_schema=TerminalRuntimeReceiverTaskTopologyV3`;
- `runtime_channel_rights_freeze_filter_schema=TerminalRuntimeChannelRightsFreezeFilterV3`;
- `runtime_channel_rights_freeze_apply_mode=SECCOMP_FILTER_FLAG_TSYNC`;
- `runtime_channel_rights_freeze_action=SECCOMP_RET_KILL_PROCESS`;
- `runtime_channel_rights_freeze_requires_fixed_tid_set=true`;
- `runtime_channel_final_snapshot_order=AFTER_RIGHTS_FREEZE_ALL_TIDS_AND_FINAL_ROLE_FILTERS`;
- `runtime_channel_final_snapshot_endpoint_ownership=SOCKET_LOCAL_LSM_TAG_SEAL_AND_GLOBAL_FILE_RECEIVE_FENCE`;
- `runtime_channel_host_proc_scan_authority=DIAGNOSTIC_ONLY_NOT_LINEARIZATION`;
- `runtime_channel_socket_lsm_guard_schema=TerminalRuntimeSocketLSMGuardV3`;
- `runtime_channel_socket_lsm_attach=GLOBAL_BPF_LSM_BEFORE_CONTROL_SOCKET_AND_RUNTIME_ROLE_CREATION`;
- `runtime_channel_socket_lsm_hooks=socket_post_create|unix_stream_connect|socket_setsockopt|socket_sendmsg|socket_shutdown|file_receive`;
- `runtime_channel_socket_lsm_storage=BPF_MAP_TYPE_SK_STORAGE`;
- `runtime_channel_socket_tag_before_userspace_fd=true`;
- `runtime_channel_socket_lsm_bootstrap_setter=EXACT_SINGLE_TID_TGID_STARTTIME_CGROUP`;
- `runtime_channel_socket_lsm_init_transition=INIT_TO_SEALED_ON_FIRST_AUTHORIZED_SETSOCKOPT_HOOK`;
- `runtime_channel_socket_lsm_all_final_endpoints_sealed=true`;
- `runtime_channel_socket_lsm_post_seal_setsockopt_action=NEGATIVE_EPERM_GLOBAL`;
- `runtime_channel_socket_lsm_runtime_socket_creation_phase=BOOTSTRAP_ONLY`;
- `runtime_channel_socket_lsm_phase_schema=TerminalRuntimeSocketGuardPhaseV3`;
- `runtime_channel_socket_lsm_phase_states=LISTENER_HANDOFF|LISTENER_RECEIVED|HANDOFF_REVOKED_GRANTED|BOOTSTRAP|OPEN_DURABLE_GRANTED|RELEASED`;
- `runtime_channel_socket_lsm_phase_map=BPF_MAP_TYPE_ARRAY_KEY0_ALIGNED_U64`;
- `runtime_channel_socket_lsm_phase_map_userspace_write_allowed=false`;
- `runtime_channel_socket_lsm_phase_map_create_flags=0`;
- `runtime_channel_socket_lsm_phase_map_freeze=BPF_MAP_FREEZE_BEFORE_ANY_PHASE_TRANSITION_OR_RUNTIME_SOCKET`;
- `runtime_channel_socket_lsm_phase_map_post_freeze_access=BPF_OBJ_GET_WITH_BPF_F_RDONLY`;
- `runtime_channel_socket_lsm_phase_transition_hooks=file_receive|socket_shutdown`;
- `runtime_channel_socket_lsm_phase_transition_atomic=BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`;
- `runtime_channel_socket_lsm_phase_control_socket=GUARD_ONLY_TAGGED_AF_UNIX_DGRAM`;
- `runtime_channel_socket_lsm_handoff_grant_control_socket=REVOCATION_ATTESTOR_ONLY_TAGGED_AF_UNIX_DGRAM`;
- `runtime_channel_socket_lsm_open_grant_control_socket=PERSISTENCE_OWNER_ONLY_TAGGED_AF_UNIX_DGRAM`;
- `runtime_channel_socket_lsm_grant_authority_shared_with_guard=false`;
- `runtime_channel_socket_lsm_guard_shutdown_allowlist=PHASE_CONTROL_FIXED_FD_WITH_SHUT_RD_OR_SHUT_RDWR`;
- `runtime_channel_socket_lsm_attestor_shutdown_allowlist=HANDOFF_GRANT_CONTROL_FIXED_FD_WITH_SHUT_WR_ONCE`;
- `runtime_channel_socket_lsm_persistence_shutdown_allowlist=OPEN_GRANT_CONTROL_FIXED_FD_WITH_SHUT_WR_ONCE`;
- `runtime_channel_socket_lsm_bootstrap_send_phase=LISTENER_HANDOFF_AND_LISTENER_RECEIVED_AND_HANDOFF_REVOKED_GRANTED_AND_BOOTSTRAP_AND_OPEN_DURABLE_GRANTED_DENY_ALL_SESSION_SENDMSG`;
- `runtime_channel_socket_lsm_listener_receive_transition=LISTENER_HANDOFF_TO_LISTENER_RECEIVED_ONCE_IN_EXACT_FILE_RECEIVE_HOOK`;
- `runtime_channel_socket_lsm_handoff_grant_transition=LISTENER_RECEIVED_TO_HANDOFF_REVOKED_GRANTED_BY_EXACT_REVOCATION_ATTESTOR`;
- `runtime_channel_socket_lsm_listener_close_transition=HANDOFF_REVOKED_GRANTED_TO_BOOTSTRAP_ONCE_BY_GUARD`;
- `runtime_channel_socket_lsm_open_grant_transition=BOOTSTRAP_TO_OPEN_DURABLE_GRANTED_BY_EXACT_PERSISTENCE_OWNER_AFTER_DURABLE_OPEN`;
- `runtime_channel_socket_lsm_release_transition=OPEN_DURABLE_GRANTED_TO_RELEASED_ONCE_BY_GUARD`;
- `runtime_channel_socket_lsm_grant_state_opens_gate=false`;
- `runtime_channel_socket_lsm_detach_allowed=false`;
- `runtime_channel_socket_lsm_link_lifetime=BEFORE_SOCKET_CREATE_THROUGH_ENDPOINT_DESTRUCTION`;
- `runtime_channel_external_inflight_setsockopt_allowed=false`;
- `runtime_channel_sender_release_order=AFTER_DURABLE_RUNTIME_SESSION_OPEN_AND_PERSISTENCE_GRANT_AND_GUARD_BPF_CMPXCHG_RELEASE`;
- `runtime_channel_bootstrap_queue_residue_action=DESTROY_ALL_ENDPOINTS_AND_ABORT_STARTUP`;
- `runtime_channel_rights_send_result=EPERM_BEFORE_RECEIVE_QUEUE`;
- `runtime_channel_fdinfo_scm_fds_required=0`;
- `runtime_channel_post_freeze_setsockopt_allowed=false`;
- `runtime_channel_post_ready_setsockopt_allowed=false`;
- `runtime_channel_recv_control_buffer=ABSENT_ZERO`;
- `runtime_channel_received_rights_survival_allowed=false`;
- `runtime_channel_rights_disposal=KERNEL_PREQUEUE_REJECT_WITH_RECVMSG_AUTOCLOSE_DEFENSE_IN_DEPTH`;
- `runtime_session_close_prepare_record=RUNTIME_SESSION_CLOSE_PREPARE`;
- `runtime_session_close_commit_record=RUNTIME_SESSION_CLOSE_COMMIT`;
- `runtime_session_close_commit_requires_broker_closed=true`;
- `runtime_session_close_control_states=RUNNING|CLOSING|CLOSED|COMMITTED|TERMINATING|CLOSED_FAILSTOP`;
- `runtime_session_close_retry_identity=SAME_SESSION_NONCE_PHASE_AND_BYTES`;
- `runtime_session_close_pre_closed_phase_timeout_ms=100`;
- `runtime_session_close_post_closed_phase_timeout_ms=20`;
- `runtime_session_close_receiver_poll_max_ms=10`;
- `terminal_timer_disarm_before_close_commit_allowed=false`;
- `terminal_trading_exit_before_close_commit_allowed=false`;
- `terminal_control_memfd_create_flags=MFD_CLOEXEC|MFD_ALLOW_SEALING`;
- `terminal_control_memfd_initial_seals=0`;
- `terminal_control_memfd_final_seals=F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_FUTURE_WRITE|F_SEAL_SEAL`;
- `terminal_guardian_heartbeat_interval_ms=10`;
- `terminal_guardian_lease_max_ms=25`; dieser Wert ist unveränderlich und darf
  durch kein Profil erhöht werden;
- `terminal_broker_trip_cas_max_ms=5`;
- `terminal_guardian_trip_dispatch_max_ms=5`;
- `terminal_kernel_signal_generation_budget_ms=25`;
- `terminal_failstop_max_ms=100`;
- `terminal_capability_profile_id` und
  `terminal_capability_profile_fingerprint`;
- `terminal_process_reap_deadline_claimed=false`;
- `terminal_persistence_worker_required=true`;
- `runtime_control_fingerprint`.

Die Revision-21-Vertragsfamilie lautet damit exakt:
`IU4RuntimeControlProfileV15`, Runtime Session Envelope V16,
`TerminalLeaseControlWordV3`, `TerminalTradingSignalEnvelopeV1`,
`TerminalKernelTripRequestV2`, `TerminalSelfKillEntryV4`,
`TerminalSeccompListenerHandoffV2`, `RuntimeSessionCloseProtocolV8`,
`TerminalRuntimeChannelProvisioningV6`,
`TerminalRuntimeReceiverTaskTopologyV3`,
`TerminalRuntimeChannelRightsFreezeFilterV3`,
`TerminalRuntimeSocketLSMGuardV3`,
`TerminalRuntimeSocketGuardPhaseV3`,
`TerminalHandoffRevocationAttestorV1`,
`TerminalParentGuardianV13`, `TerminalNativeTripBrokerV10`,
`TerminalKernelLeaseShimV11`, `TerminalPersistenceWorkerV8` und
`TerminalLeaseCapabilityProfileV14` sowie die Close-Nachrichten
`TerminalGuardianOrderlyCloseRequestV3`,
`TerminalWorkerClosePrepareRequestV2`, `TerminalWorkerClosePrepareAckV2`,
`TerminalWorkerCloseCommitRequestV2`, `TerminalWorkerCloseCommitAckV2` und
`TerminalBrokerCloseCommitApprovalV2`.

Environment-Defaults aus `_resolve_tp_sl_pct()` oder
`_resolve_time_stop_sec()` sind in ENFORCED verboten. Bestehende Werte dürfen
nur als dokumentierte Paritätskandidaten in ein separat genehmigtes Profil
übernommen werden.

Dasselbe gilt für die heutigen festen Loss-Cluster-Werte. Die etablierte
Semantik ist das Paritätsziel, aber ENFORCED liest keine unversionierten
Modulkonstanten als operative Policy.

Der PEE-Referenz-Stop wird aus Canonical Decimal Price und dem gebundenen
Control-Profil berechnet. Er darf nicht aus einem Float rekonstruiert und nicht
aus dem SHADOW-Fallback `PEE_REFERENCE_STOP_RATE` übernommen werden.

### 6.4 Operational Profile

Für ENFORCED ist exakt `L1_OPERATIONAL_PROFILE=PAPER` erforderlich.
`PRODUCTION`, `DEVELOPMENT`, `RECOVERY`, fehlende und unbekannte explizite Werte
werden abgelehnt.

Die heutige allgemeine Fallback-Semantik „ungültig ⇒ PAPER“ darf das IU4-Gate
nicht passieren. Der mode-neutrale IU4-Bridge prüft deshalb den rohen
Environment-Wert strikt, bevor ein normalisierter Profile Summary als Autorität
verwendet wird. `OFF`-Verhalten außerhalb IU4 bleibt dadurch unverändert.

---

## 7. Activation Authorization V2 und Trust Boundary

### 7.1 Versionierung

`IU4ActivationAuthorizationV1` bleibt ein unveränderter historischer Vertrag.
Er bindet weder Runtime-Control-Profil noch R3-/Release-Evidenz vollständig und
ist deshalb für die aktive ENFORCED-Integration nicht ausreichend.

Die Implementierung führt `IU4ActivationAuthorizationV2` additiv ein. V1 darf
in OFF/SHADOW-Tests weiter gelesen werden, wird für ENFORCED aber mit einem
stabilen Reason Code abgelehnt.

### 7.2 Pflichtfelder von V2

V2 enthält mindestens alle V1-Identitäten sowie:

- `schema_version=2`;
- `authorization_id` als Hash der kanonischen Payload;
- `authorization_reference`;
- `approved_mode=ENFORCED`;
- `repository_commit_sha` als vollständige 40-stellige SHA;
- Coordinator-ID und Symbol;
- Economics-Profil-ID, Modellversion, Fingerprint und Approval-ID;
- Throttle-Profil-ID, Modellversion, Fingerprint und Approval-ID;
- Runtime-Control-Profil-ID und Fingerprint;
- erwarteter State Owner Epoch;
- erwartete `authority_generation_id` und deren committed
  `authority_commit_anchor`;
- Lifecycle-Policy-ID und Fingerprint, jedoch keinen veränderlichen aktuellen
  Ledger Tip;
- Handoff- oder Genesis-Manifest-ID und SHA-256;
- bei Legacy exit-only die positiongebundene Control-Binding-ID und SHA-256;
- Spezifikations-ID;
- R3-Final-Attestation-ID und SHA-256;
- Implementation-/Test-Evidence-Manifest-ID und SHA-256;
- `valid_from_utc` und `valid_until_utc`.

Unbekannte oder fehlende Felder sind unzulässig. Die kanonische
Serialisierung verwendet sortierte JSON-Schlüssel, eindeutige Stringformen und
SHA-256.

### 7.3 Externe Bereitstellung

Die Authorization-Payload wird über einen expliziten absoluten Pfad geladen,
beispielsweise `L1_IU4_ACTIVATION_AUTHORIZATION_PATH`. Sie liegt außerhalb:

- des Git-Checkouts,
- des Atomic-State-Verzeichnisses,
- der Runtime-Logs und
- aller durch den Bot beschreibbaren Projekt-Outputs.

Der Loader akzeptiert nur eine reguläre, nicht über Symlink aufgelöste Datei.
Fehlende oder unsichere Dateirechte blockieren ENFORCED.

### 7.4 Unabhängiger Trust Anchor

`trusted_authorization_id` wird separat provisioniert, beispielsweise über
`L1_IU4_TRUSTED_AUTHORIZATION_ID`. Er darf niemals aus derselben Payload
berechnet, aus deren Dateinamen abgeleitet oder automatisch übernommen werden.

Payload-ID und Trust Anchor müssen exakt übereinstimmen. Es gibt keinen
Fallback, keine „latest“-Suche und keine Auswahl mehrerer Authorizations.

### 7.5 Gültigkeit während der Runtime

- Beim Startup muss die Authorization zeitlich gültig sein.
- Vor jedem neuen Entry wird ihre Gültigkeit erneut geprüft.
- Ablauf oder Bindungsverlust blockiert neue Entries, beendet aber keine
  bestehende Position gewaltsam.
- Risikoreduzierende Exits bleiben zulässig, solange der Loop nicht durch
  `HARD` oder `EMERGENCY` gemäß L0/L1 beendet werden muss.
- Ein neuer Prozessstart benötigt erneut eine gültige Authorization.

### 7.6 Manuelle Restart/Recovery Authorization V1

Die Activation Authorization ersetzt keine Restart-/Recovery-Freigabe. Jede
ENFORCED-Wiederaufnahme nach einem Stop und jede Coordinator-Recovery außerhalb
des laufenden Trading-Loops benötigt zusätzlich eine separat provisionierte
`IU4RestartRecoveryAuthorizationV1` und einen unabhängigen Trust Anchor.

Der Vertrag enthält mindestens:

- `schema_version=1` und content-hash-basierte
  `restart_recovery_authorization_id`;
- dokumentierten Verantwortlichen und Entscheidungszeitpunkt;
- Stop-/Recovery-Grund und vorherigen Kill-Level;
- Hash eines Manifests der gesicherten relevanten Logs;
- dokumentierten letzten State-Zeitpunkt;
- Bestätigung `no_open_intents_confirmed=true`;
- Hash eines Environment-Checks für Uhr, Ressourcen, Konfiguration und Logging;
- Repository Commit, Coordinator-ID und sämtliche Profilfingerprints;
- exakten `pre_attempt_ledger_tip`, global eindeutige Authorization-ID und
  `startup_attempt_id`; bei bestehender Authority außerdem committed
  `authority_commit_anchor` und `authority_generation_id`; nur bei der
  Fertigstellung eines Genesis-PREPARE sind stattdessen exakt die kanonischen
  Payloadfelder `source_authority_commit_anchor=NONE` und
  `source_authority_generation_id=NONE` zulässig;
- erwartete Pre-Recovery Transaction Sequence, Journal Head und
  Snapshot-Fingerprint; nur bei Genesis-PREPARE ohne bestehenden Atomic State
  sind die kanonischen Sentinels `sequence=0`, `journal_head=EMPTY` und
  `snapshot=NO_ATOMIC_STATE` zulässig;
- exakt eine zulässige Operation: `RESTART_ONLY`, `RECOVER_AND_RESTART`,
  `COMPLETE_AUTHORITY_PREPARE` oder `RECONCILE_TERMINAL_GAP`;
- bei `COMPLETE_AUTHORITY_PREPARE` zusätzlich exakte offene PREPARE-Event-ID
  und -Fingerprint, Operationstyp, geplante Authority Generation, Source
  Authority Anchor, Target-Core-Fingerprint, erwartetes Target-Schema/-Pfad
  sowie den einzig zulässigen korrespondierenden COMMIT-Typ;
- `valid_from_utc` und `valid_until_utc`.

Payload und Trust Anchor werden analog zur Activation Authorization getrennt
bereitgestellt. Eine Boolean-Flag, die Activation Authorization oder ein
Operatorname allein genügen nicht.

`RECOVER_AND_RESTART` darf ausschließlich einen bereits durable committeten
Journal-Head deterministisch wieder als Snapshot materialisieren. Diese
Operation darf keinen Journaleintrag erzeugen, verändern, überspringen oder
fachlichen State erfinden. Damit ist sie eine manuell freigegebene
Wiederherstellung des committeten Zustands und keine automatische
Fehlerkorrektur. `RECONCILE_TERMINAL_GAP` ist davon getrennt; sie darf nur den
in Abschnitt 16.2.1 vorgeschriebenen konservativen EMERGENCY-Control-Record
erzeugen und startet niemals einen Loop.

`COMPLETE_AUTHORITY_PREPARE` ist ebenfalls getrennt. Sie ist ausschließlich
zulässig, wenn genau ein offener, hashgültiger Authority-PREPARE ohne COMMIT
existiert und sämtliche Authorization-Felder exakt damit übereinstimmen. Die
Operation darf nur:

1. einen bereits vorhandenen Target State gegen PREPARE und Core-Payload
   prüfen oder den fehlenden Target State exakt daraus materialisieren;
2. diesen Target State read-only reconciliieren;
3. genau den im Vertrag benannten korrespondierenden Authority-COMMIT anhängen.

Sie darf keine Business-/Safety-Werte neu entscheiden, keinen anderen PREPARE
abschließen und keinen Loop starten. Nach erfolgreichem COMMIT beendet sich der
Prozess. Ein späterer Start benötigt eine neue `RESTART_ONLY`-Authorization.
Existiert der COMMIT bereits, ist der PREPARE nicht mehr offen; dann wird kein
zweiter COMMIT erzeugt und `COMPLETE_AUTHORITY_PREPARE` ist unzulässig.

Vor jeder Recovery, PREPARE-Fertigstellung oder Loop-Freigabe wird die
Authorization durch genau einen durable `RESTART_AUTH_CONSUME`-Record im
Lifecycle Ledger verbraucht. Erst nach
durable Write und Directory-`fsync` darf Startup fortfahren. Danach ist dieselbe
Authorization-ID für immer unzulässig, auch wenn der Prozess vor Loop-Start
abstürzt. Der nächste Versuch benötigt eine neue manuelle Entscheidung und eine
neue Authorization.

Ein Crash vor dem durable Consumption Record verbraucht die Authorization
nicht. Ein Crash danach lässt den Record autoritativ; der aktuelle Ledger Tip
wird read-only aus der Hash-Kette rekonstruiert und die alte Authorization
bleibt verbraucht. Gleiche Authorization-ID mit anderer Payload ist ein harter
Ledger-Konflikt.

Der Consumption Record verändert nur den `ledger_tip`, niemals die committed
`authority_generation_id` oder den `authority_commit_anchor`. Der Startup darf
nach Consumption nur fortfahren, wenn die vollständige Kette ab dem exakt
autorisierten `pre_attempt_ledger_tip` ausschließlich die für dieselbe
`startup_attempt_id` zulässigen Records enthält: genau ein
`RESTART_AUTH_CONSUME`; danach abhängig von der autorisierten Operation
entweder optional `RECOVERY_MATERIALIZATION`, genau ein passender Authority-
COMMIT, die Terminal-Gap-Records oder bei tatsächlichem Loop-Start die Runtime-
Session-Records. Diese Alternativen dürfen nicht vermischt werden. State oder
Authorization werden wegen eines nicht-ownerverändernden Appends nicht
umgeschrieben; ein Authority-COMMIT verändert Generation/Anchor dagegen erst
nach erfolgreicher Target-Reconciliation.

Jeder Restart-/Recovery-Versuch loggt vollständig die in L1-D geforderten
Restart-Daten. Als Erststart ohne vorherigen Restart-State gilt ausschließlich
die unmittelbare In-Process-Fortsetzung einer attestierten Clean Genesis mit
`completion_provenance=DIRECT`: Aktuelle Prozessinstanz, Genesis-Operation-
Attempt und nur im Speicher gehaltene Continuation Nonce müssen exakt der
COMMIT-Bindung entsprechen; außerdem dürfen weder Completion-Consumption
zwischen PREPARE und COMMIT noch eine frühere Runtime Session derselben
Generation existieren. Prozessende, Crash, `exec`, PID-Reuse oder Verlust der
rohen Continuation Nonce beendet diese Ausnahme unwiderruflich. Ein durch
`COMPLETE_AUTHORITY_PREPARE` abgeschlossener Genesis-COMMIT ist niemals diese
Ausnahme: Der Completion-Prozess endet, und der nächste Prozess benötigt exakt
eine neue, durable verbrauchte `RESTART_ONLY`-Authorization.

### 7.7 IU4 Lifecycle Ledger V1

Ein neues `IU4LifecycleLedgerV1` ist die einzige kanonische Autorität für
Owner Epoch und einmalige Lifecycle-Freigaben. Es ist kein Economics-, S2-, S4-
oder Runtime-Journal.

Das Ledger ist:

- append-only und hash-verkettet;
- durch monotone `lifecycle_sequence` geordnet;
- pro Record über `lifecycle_event_id`, vorherigen Record-Fingerprint und
  Payload-Fingerprint gebunden;
- unter einem exklusiven Prozess-Lock und mit create-new, File-`fsync` und
  Directory-`fsync` geschrieben;
- ohne veränderlichen „used“-Schalter aus der vollständigen Record-Kette
  auswertbar.

Aus derselben validen Kette werden drei ausdrücklich getrennte Sichten
abgeleitet:

- `ledger_tip`: Fingerprint des letzten Records beliebigen Typs; verändert
  sich bei jedem Append und wird niemals in einen fachlichen State-Fingerprint
  aufgenommen;
- `authority_commit_anchor`: Fingerprint des letzten gültigen
  Authority-`COMMIT`-Records; verändert sich nur nach vollständig
  materialisierter Genesis, Handoff oder Migration;
- `authority_generation_id`: vorab deterministisch aus Approval, Manifest,
  Source Authority, Operation und `target_business_payload_fingerprint`
  gebildete ID der committed State-Generation.

Owner Epoch und aktive State-Generation werden ausschließlich aus dem letzten
gültigen Authority-`COMMIT` abgeleitet. Nicht-ownerverändernde Records dürfen
den State oder eine Activation Authorization deshalb nicht invalidieren.

Verbindliche Authority-Record-Paare sind:

- `LEGACY_GENESIS_PREPARE` / `LEGACY_GENESIS_COMMIT`;
- `ATOMIC_GENESIS_PREPARE` / `ATOMIC_GENESIS_COMMIT`;
- `LEGACY_TO_PEE_HANDOFF_PREPARE` / `LEGACY_TO_PEE_HANDOFF_COMMIT`;
- `PEE_TO_LEGACY_HANDOFF_PREPARE` / `PEE_TO_LEGACY_HANDOFF_COMMIT`;
- `ATOMIC_V1_TO_V2_MIGRATION_PREPARE` /
  `ATOMIC_V1_TO_V2_MIGRATION_COMMIT`.

Nicht-ownerverändernde Record-Typen sind mindestens:

- `RESTART_AUTH_CONSUME`;
- `RECOVERY_MATERIALIZATION`;
- `RUNTIME_SESSION_OPEN`;
- `RUNTIME_SESSION_CLOSE_PREPARE`;
- `RUNTIME_SESSION_CLOSE_COMMIT`;
- `TERMINAL_GAP_RECONCILIATION`.

`RESTART_AUTH_CONSUME` enthält mindestens Authorization-ID/Fingerprint,
Operation, Verantwortlichen, Startup-Attempt-ID, Pre-State, Pre-Journal-Head,
exakten `pre_attempt_ledger_tip`, Source Authority Generation/Anchor und
Consumption Timestamp. Ausschließlich bei
`operation=COMPLETE_AUTHORITY_PREPARE` für einen Genesis-PREPARE ohne bisherige
Authority enthält der Record exakt
`source_authority_commit_anchor=NONE`,
`source_authority_generation_id=NONE`, die geplante
`target_authority_generation_id` sowie PREPARE-Event-ID/Fingerprint. Diese
Sentinels sind Teil der kanonischen Payload und ihres Fingerprints, keine
fehlenden Felder. Eine Authorization-ID darf in der gesamten Kette höchstens
einmal vorkommen.

#### 7.7.1 Selbstreferenzfreie Authority-Generation

Der `PREPARE`-Record bindet mindestens:

- Commit, Coordinator, Symbol, Manifest-/Approval-ID und deren Fingerprints;
- vorherigen und geplanten neuen Owner Epoch;
- Source-State-Schema, Pfad und vollständigen Fingerprint;
- geplante `authority_generation_id`;
- kanonische Target-Core-Payload und `target_state_core_fingerprint`;
- vollständige S2-, S4V2-, Loss-Cluster-, Throttle- und Progress-Werte samt
  Cross-State-Fingerprints;
- Operator, UTC-Zeitpunkt und eindeutige Lifecycle Event ID.

Zuerst wird eine kanonische Target-Business-Payload aus sämtlichen fachlichen,
Safety-, Schema-, Journal- und Pfadfeldern gebildet. Sie enthält keinerlei
Authority-Generation-, PREPARE-, COMMIT- oder Ledger-Felder. Ihr Fingerprint
geht gemeinsam mit Operation, Source Authority, Manifest und Approval in die
`authority_generation_id` ein. Erst danach entsteht die Target-Core-Payload
aus Business Payload plus Generation ID. Sie schließt den erst nach PREPARE
bestimmbaren `authority_prepare_record_fingerprint`, den daraus gebildeten
Aggregate-Fingerprint sowie jeden `ledger_tip` oder zukünftigen
`COMMIT`-Fingerprint aus.

Nach durable PREPARE wird der Target State materialisiert. Sein Envelope bindet
`authority_generation_id` und `authority_prepare_record_fingerprint`; sein
vollständiger State-Fingerprint umfasst Core-Payload und Envelope. Der
anschließende `COMMIT`-Record bindet PREPARE-Fingerprint, vollständigen
Target-State-Fingerprint und eine erfolgreiche read-only Reconciliation.
Der Target State bindet den COMMIT-Fingerprint ausdrücklich nicht.

Jeder Authority-COMMIT bindet außerdem genau eine Completion Provenance:

- `DIRECT`: PREPARE, Target-Publikation und COMMIT gehören zur ursprünglichen
  autorisierten Authority-Operation; zwischen PREPARE und COMMIT existiert kein
  `RESTART_AUTH_CONSUME` für `COMPLETE_AUTHORITY_PREPARE`. Der COMMIT bindet
  ursprüngliche Operation-/Prozess-ID und Approval sowie
  `direct_process_instance_id`, `genesis_operation_attempt_id` und
  `direct_continuation_nonce_hash`. Die Prozessinstanz wird kanonisch aus
  Boot-ID, PID, OS-Prozessstartzeit und Launch-ID gebildet. Die rohe, aus dem
  gebundenen OS-CSPRNG stammende Continuation Nonce bleibt ausschließlich im
  Speicher dieser Prozessinstanz, wird nie persistiert und muss unmittelbar
  vor Session OPEN als Preimage des gebundenen Hashes bestätigt werden.
- `RECOVERED_AFTER_PREPARE`: Der COMMIT wurde durch
  `COMPLETE_AUTHORITY_PREPARE` erzeugt und bindet deren Authorization-ID,
  Consumption-Event-ID, Startup-Attempt-ID und vorherigen Ledger Tip.

Eine Provenance darf nicht aus Prozesszustand oder Dateiexistenz geraten
werden; sie ist Bestandteil der kanonischen COMMIT-Payload und des COMMIT-
Fingerprints. Existiert ein passender Completion-Consumption-Record, ist
`DIRECT` unzulässig. Fehlt er, ist `RECOVERED_AFTER_PREPARE` unzulässig.
`DIRECT` berechtigt außerdem keinen beliebigen späteren Prozess: Ohne exakte
aktuelle Prozessinstanz-/Attempt-/Nonce-Übereinstimmung gilt derselbe COMMIT
zwar weiterhin als Authority-COMMIT, seine Erststartausnahme ist jedoch
erloschen und vor Loop-Start ist `RESTART_ONLY` zwingend.

Damit ist die Reihenfolge azyklisch:

```text
target business -> generation ID -> target core -> PREPARE fingerprint
                -> full target state -> COMMIT fingerprint
```

Erst der durable `COMMIT` macht Owner Epoch und Authority Generation wirksam.
Ein PREPARE ohne passenden COMMIT blockiert jeden Loop als unvollständige
Authority-Operation. Vor dem COMMIT bleibt bei einem Handoff der bisherige
Owner kanonisch; der vorbereitete Target State ist nicht aktivierbar. Bei
Genesis existiert bis zum COMMIT kein Owner. Recovery darf ausschließlich die
im PREPARE gebundene Target-Core-Payload materialisieren und denselben COMMIT
abschließen; dafür ist zwingend die in Abschnitt 7.6 definierte
`COMPLETE_AUTHORITY_PREPARE`-Authorization erforderlich. Jede Abweichung
erfordert eine neue manuelle Entscheidung.

Weder Environment, Modus, Legacy S2/S4 noch ein isolierter Atomic Snapshot darf
Owner oder Generation allein behaupten. Der aktive State bindet
`authority_generation_id` und `authority_prepare_record_fingerprint`; der
Ledger-COMMIT bindet umgekehrt dessen vollständigen Fingerprint. Die
Reconciliation prüft diese gerichtete Beziehung und den extern abgeleiteten
`authority_commit_anchor`.

Nach späteren Trading-Transaktionen darf der aktuelle State-Fingerprint
naturgemäß vom im Authority-COMMIT gebundenen initialen Target State abweichen.
Er ist nur gültig, wenn eine lückenlose Journal-/State-Historie von genau diesem
committeten Target State zum aktuellen Head führt und jede Transition dieselbe
`authority_generation_id` sowie denselben PREPARE-Fingerprint bewahrt. Ein
Authority-Wechsel innerhalb einer Tick-/Control-Transaktion ist verboten.

#### 7.7.2 Nicht-ownerverändernde Ledger-Erweiterungen

`RESTART_AUTH_CONSUME`, `RECOVERY_MATERIALIZATION` und Runtime-Session-Records
verändern nur den `ledger_tip`. Sie binden jeweils den vorherigen Tip, die
stabile `authority_generation_id`, den `authority_commit_anchor` und ihre eigene
Operation, werden aber weder in Atomic/Legacy State zurückgebunden noch als
Owner-Wechsel interpretiert. Einzige Ausnahme ist der Consumption Record zur
Fertigstellung eines Genesis-PREPARE vor der ersten Authority: Er bindet an
derselben Feldposition die in Abschnitt 7.7 definierten exakten `NONE`-
Sentinels plus geplante Target Generation und PREPARE-Identität. Leere oder
weggelassene Felder sind auch dort ungültig.

Eine Activation Authorization bindet die stabile Authority Generation und den
Commit Anchor. Eine Restart/Recovery Authorization bindet zusätzlich den
exakten `pre_attempt_ledger_tip`. Nach Append wird nicht auf Gleichheit mit
diesem alten Tip geprüft, sondern auf eine lückenlose, hashgültige und für
dieselbe `startup_attempt_id` erlaubte Extension. Unbekannte, konkurrierende
oder anders gebundene Zwischenrecords blockieren den Startup.

### 7.8 Runtime Session Envelope V16

Vor Eintritt in einen ENFORCED-Loop wird genau ein `RUNTIME_SESSION_OPEN`
durable geschrieben. Er bindet Session-/Startup-Attempt-ID, Authority
Generation/Commit Anchor, Atomic State, Journal Head/Sequence, Profile,
Resource-Reserve-Check, vorreservierten nonblocking IPC-Kanal, festes
Write-Budget, aufgelöste Termination-Latch-Deadline `1..100 ms`, monotone
Clock-Quelle sowie
Persistence-Worker-/Parent-Guardian-/Native-Trip-Broker-ID, einmaligen
Coordinator-Emergency-Lease, vorab geöffneten exklusiven Lifecycle-Close-
Append-Handle samt Inode/Writer-Lease, vorab festgelegte Control Event ID,
Trading-Child-PID/-Startzeit und getrennte Ready-Nonces. Zusätzlich bindet OPEN
den verifizierten OS-Lease-Typ, die
Guardian-PID/-Startzeit, den PIDFD- beziehungsweise Job-Object-Identifier,
Credentials-/Capability-Fingerprint, Lease-Nonce,
Kernel-Self-Death-Timer-ID/-Clock/-Signal, gebundene Trading-Self-, Guardian-
und Broker-PIDFDs jeweils samt Ziel-PID/-Startzeit und `SIGKILL`-Probe,
Native-Shim-Fingerprint,
Heartbeat-Sequenz, absolute erste Lease-Expiry, Control-Word-Memfd-/Schema-
Identität, `memfd_create`-Flags, initiale/intermediäre/finale Memfd-Seals und pro
Prozess nachgewiesene Mapping-Rechte,
`TerminalTripLivenessPipeV1`-Enden/-Inode/-Capacity, leeren Initialzustand und
dauerhaftes Write-Verbot sowie Guardian-/Shim-Eventfd-Identitäten, den einzigen
Seccomp-User-Notification-Listener samt Inode, Filterhash und alleiniger
Broker-Ownership, `TerminalTradingSignalEnvelopeV1` mit vollständiger
blockierbarer Signalmaske, Dispositionstabelle, Installationsreihenfolge und
dem kombinierten NEW_LISTENER-/WAIT_KILLABLE_RECV-Filterhash,
`TerminalSeccompListenerHandoffV2` mit reserviertem Trading-Quell-FD,
reserviertem Broker-Ziel-FD, Trading-/Broker-PIDFD, exakt einmaligem
`pidfd_getfd`, geerbtem ACK-Eventfd, Ptrace-/Dumpable-Reihenfolge und
irreversibler Handoff-Close-Evidenz, außerdem
`TerminalHandoffRevocationAttestorV1` samt Executable-/Filterhash,
TGID/TID/Startzeit, Cgroup, einzigem `HANDOFF_REVOCATION_GRANT_CONTROL`-
Socket-Cookie und genau den Transitionen
`LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED→BOOTSTRAP`, die getrennten
Guardian→Broker-, Broker→Guardian-, Broker→Shim-Renewal-, Broker→Shim-Close-,
Broker→Worker- und Worker→Broker-Verbindungen aus
`TerminalRuntimeChannelProvisioningV6` samt abstrakten Bootstrap-Adressen,
Connect-/Accept-Provenance, `SO_PEERCRED` beider Endpunkte,
`SOCK_SEQPACKET`-Inodes/FDs und dem Nachweis `SO_PASSCRED=0`, außerdem pro
finalem Empfangsendpunkt `SO_PASSRIGHTS=0`, Set/Get-Reihenfolge,
`TerminalRuntimeReceiverTaskTopologyV3`, dem vor finalem Snapshot auf allen
Empfänger-TIDs per TSYNC installierten
`TerminalRuntimeChannelRightsFreezeFilterV3`, dessen BPF-Hash/Filterzahl,
den danach vollständig gestapelten finalen Rollenfiltern und systemweiter
Endpoint-Ownership-Inventur,
post-Filter `getsockopt==0`, `scm_fds: 0`, leerer Queue, unveränderter FD-/
OFD-/Lock-Inventur, gebundener Persistence-Owner-/
`OPEN_DURABILITY_GRANT_CONTROL`-Identität und der erst aus der erfolgreichen
Commit-Fortsetzung zulässigen geplanten Grant-/Senderfreigabe sowie bereits ab Freeze-
Grenze gesperrtem `setsockopt`, Broker-Binär-/Filterhash und
Worker-IPC-Peerbindung sowie den vor Ready erzeugten Broker-epoll-FD mit
vollständiger fester `tfd`-/Event-Maske für Trip-Listener, Liveness-Read-Ende,
`GB_REQUEST` und `WB_ACK` sowie nach Ready verbotenem `epoll_ctl`, außerdem
`RuntimeSessionCloseProtocolV8` mit PREPARE-/COMMIT-Schemahashes,
`TerminalGuardianOrderlyCloseRequestV3`,
`TerminalWorkerClosePrepareRequestV2`, `TerminalWorkerClosePrepareAckV2`,
`TerminalWorkerCloseCommitRequestV2`, `TerminalWorkerCloseCommitAckV2` und
`TerminalBrokerCloseCommitApprovalV2` samt exakten Struct-Längen/Type-
Konstanten/Peerwegen sowie
`TerminalTradingTaskTopologyV2` mit TGID, vollständiger TID-/Startzeit-/Rollen-
Menge, Native-Shim-TID, gemeinsamen `KCMP_FILES`-Ergebnissen, TSYNC-
Basisfilterhash, per-role Filterhashes, Session-Cgroup-/PID-Namespace-
Fingerprint, vollständiger FD-/FDINFO-Inventur und dem Nachweis, dass außerhalb
des einzigen Trading-FD-Slots keine Pipe-Writer- oder sonstige Kernel-Referenz
existiert, sowie `TerminalSelfKillEntryV4` mit exakt gebundener
Self→Guardian→Broker→Liveness-Close-Fallbackordnung, PIDFD-Nummern und
per-role Seccomp-BPF-Hashes, `TerminalKernelTripRequestV2` mit exakt
interceptetem Self-PIDFD-/Signal-/Null-`siginfo`-/Flags-Tupel, Notification-
Filterhash, Listener-FD/-Inode, Broker-Ready-Nonce und dem Nachweis, dass kein
Trading-/Guardian-/Shim-/Worker-TID den Listener besitzt, außerdem
`terminal_guardian_heartbeat_interval_ms=10`,
`terminal_guardian_lease_max_ms=25` und
`terminal_process_reap_deadline_claimed=false`. Scheitert dieser Write, die
Reserve, die OS-Bindung, das nachweisliche Armen der Self-Death-Lease oder einer
der unabhängigen Ready-Handshakes, startet der Loop nicht.

Der Ready-Nachweis umfasst das in Abschnitt 7.8.2 definierte, versionsgebundene
`TerminalLeaseCapabilityProfileV14`. Ein universeller Scheduler-Worst-Case wird
nicht behauptet. Stattdessen muss das aktuelle System exakt innerhalb des
endlichen zertifizierten Capability-Envelopes liegen und dessen deterministische
PASS-Regel erfüllen; sonst bleibt OPEN gesperrt.

`RuntimeSessionCloseProtocolV8` besitzt zwei getrennte durable Records. Nach
geordnetem Ende, durablem Abschluss aller Tick-/Control-Writes und
abschließender Reconciliation darf zunächst ausschließlich
`RUNTIME_SESSION_CLOSE_PREPARE` geschrieben werden. PREPARE bindet Session,
Reconciliation-/Journal-Head, live Child-PID/-Startzeit/-PIDFD, Worker-Fencing-
Token, erwartetes Control Word `(CLOSING,n,0)`, Close-Nonce und die geplante
COMMIT-Event-ID. PREPARE ist ausdrücklich **kein** passender CLOSE und hält die
Session bei jedem Crash, Trip oder Writefehler unclean.

Erst nach der in diesem Abschnitt definierten erfolgreichen Broker-CAS auf
`(CLOSED,n,0)` darf genau ein `RUNTIME_SESSION_CLOSE_COMMIT` durable werden. Er
bindet PREPARE-Fingerprint, Broker-CLOSED-Control-Word, Broker-Generation,
Guardian-Credentials/Nonce und die bestätigte Child-Liveness. Ausschließlich
dieser COMMIT klassifiziert die Session als clean. Ein OPEN ohne passenden
CLOSE-COMMIT oder `TERMINAL_GAP_RECONCILIATION`, insbesondere OPEN plus
CLOSE-PREPARE ohne COMMIT, ist beim nächsten Startup ein autoritativer
unclean-session Befund. Er wird konservativ als `TERMINAL_UNKNOWN` mit Entry-
und Exit-Auswertung gesperrt behandelt und erlaubt keinen Loop.

Der `TerminalParentGuardianV13` ist der tatsächliche OS-Parent des Trading-
Prozesses und bleibt von vor OPEN bis nach durable CLOSE-COMMIT ununterbrochen
gebunden. Zusätzlich besitzt der Trading-Prozess vor OPEN eine bereits
kernel-seitig armed `TerminalKernelSelfDeathLeaseV1`.

Globaler Terminal-, Close- und Renewal-State werden durch genau ein
prozessübergreifendes, lock-free `_Atomic uint64_t` namens
`TerminalLeaseControlWordV3` linearisiert. Ein writable Trip-Latch im Trading-
Adressraum existiert nicht. Das Control Word liegt in einem vor OPEN erzeugten
anonymen Memfd und enthält ausschließlich die Terminal-States RUNNING,
CLOSING, CLOSED, COMMITTED, TERMINATING und CLOSED_FAILSTOP, monotone
`renewal_sequence` und
einmalige `trip_sequence`. Bits 63..61 kodieren
`RUNNING=0/CLOSING=1/CLOSED=2/COMMITTED=3/TERMINATING=4/CLOSED_FAILSTOP=5`;
6 und 7 sind INVALID. Bit 60 ist `trip_sequence={0,1}`, Bits 59..0 sind die
unsigned `renewal_sequence`; Überlauf blockiert ohne Wraparound.

Erlaubt sind ausschließlich die Kette RUNNING→CLOSING→CLOSED→COMMITTED mit
jeweils unverändertem `(n,0)`, `RUNNING|CLOSING→(TERMINATING,n,1)` und
`(CLOSED,n,0)→(CLOSED_FAILSTOP,n,1)`. Renewals dürfen nur
RUNNING oder CLOSING auf derselben State-Stufe inkrementieren; Trading-Gates
akzeptieren ausschließlich RUNNING. CLOSING hält das Child side-effect-frei,
renewt die Lease aber während des begrenzten PREPARE-Protokolls weiter.
CLOSED, COMMITTED, TERMINATING und CLOSED_FAILSTOP erzeugen keine Renewal-
Approval. Keine Transition aus TERMINATING oder CLOSED_FAILSTOP und keine
Rücktransition in RUNNING/CLOSING ist zulässig.

Ein separater single-threaded `TerminalNativeTripBrokerV10` ist nach der
Genesis-Initialisierung der einzige Runtime-Writer dieses Words. Die Linux/WSL-
Bootstrap-Zustandsmaschine ist exakt:

1. Der Launcher ruft
   `memfd_create("iu4-terminal-control-v3", MFD_CLOEXEC|MFD_ALLOW_SEALING)` auf.
   Jeder zusätzliche/unbekannte Flag, fehlendes `MFD_ALLOW_SEALING` oder
   fehlendes `MFD_CLOEXEC` ist fail closed.
2. Unmittelbar danach muss `fcntl(F_GET_SEALS)` exakt `0` liefern. Ein initiales
   `F_SEAL_SEAL` oder irgendein anderer Seal verhindert den Startup.
3. Der Launcher führt `ftruncate` auf exakt eine gebundene System-Page aus,
   schreibt vor jeder Freigabe den kanonischen initialen RUNNING-Wert einmalig
   per vollständigem acht-Byte-`pwrite` an den gebundenen Offset und erzeugt
   selbst keine writable Map.
4. Der frisch geforkte Broker erzeugt die einzige `MAP_SHARED`-Map mit
   `PROT_READ|PROT_WRITE`, bestätigt Adresse, Länge, Offset und Inode und schließt
   danach seinen Memfd-FD; nur die bestehende Map bleibt writable.
5. Der Launcher ruft exakt
   `fcntl(F_ADD_SEALS, F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_FUTURE_WRITE)` auf.
   Der folgende `F_GET_SEALS` muss exakt diese drei Bits und ausdrücklich nicht
   `F_SEAL_WRITE|F_SEAL_SEAL` zeigen.
6. Danach ruft der Launcher exakt `fcntl(F_ADD_SEALS, F_SEAL_SEAL)` auf. Der
   finale `F_GET_SEALS` muss exakt
   `F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_FUTURE_WRITE|F_SEAL_SEAL` zeigen.
   Weitere Seal-Transitionen sind verboten; `F_SEAL_WRITE` bleibt abwesend,
   weil die vor `F_SEAL_FUTURE_WRITE` bestehende Broker-Map schreiben muss.
7. Erst nach dem finalen Seal-State erzeugt der Launcher ausschließlich
   getrennte read-only Consumer-Maps für Guardian, Trading-Prozess mit Native
   Shim und Worker, schließt alle Consumer-Memfd-FDs und startet diese Prozesse.

Guardian, Trading-Prozess, Shim und Worker erben keine writable Map und können
wegen `F_SEAL_FUTURE_WRITE` keine neue writable Map erzeugen. Der Broker darf
keinen Prozess oder Thread erzeugen und weder `execve` noch `execveat`
ausführen. `/proc/<pid>/maps`, Memfd-Inode/-Größe,
Create-Flags, jeder beobachtete Seal-State und Mapping-Rechte jedes Prozesses
werden vor OPEN extern attestiert. Ein abweichender Returncode, Teilwrite,
fehlender/zusätzlicher Seal, eine weitere writable Map oder ein unbekannter
Mapper verhindert OPEN. `atomic_is_lock_free`, Größe, Alignment, Endianness und
acquire/release-CAS-Semantik sind Teil des Capability-Fingerprints.

Außerhalb des nachfolgend vollständig definierten einmaligen
`TerminalSeccompListenerHandoffV2`-Fensters gelten vor Broker-Ready
`PR_SET_DUMPABLE=0`, `PR_SET_PTRACER=0`, leere Capability-Sets und
`no_new_privs`; `ptrace`, `process_vm_writev`, `/proc/.../mem` und Namespace-
Wechsel sind in allen beteiligten Filtern unzulässig. Der Capability-Nachweis
bindet Linux-Yama exakt an `ptrace_scope=1`, dieselben Real-Credentials und den
Ausschluss jedes privilegierten Co-Tenants. Jeder andere Yama-Modus, eine
fehlende Yama-LSM-Aktivierung oder eine nicht exakte Ptrace-Policy verhindert
OPEN.

Der Guardian sendet alle `10 ms` genau eine monotone Renewal Message über die
exklusive nonblocking `SOCK_SEQPACKET`-Verbindung `GB_REQUEST` an den Broker. Session-ID,
Heartbeat-Sequenz, geprüfter PIDFD-Zielprozess, Capability-Proof-Fingerprint
und absolute Expiry sind gebunden. Beide Renewal-Verbindungen wurden nach
Start der finalen Rollenprozesse gemäß `TerminalRuntimeChannelProvisioningV6`
aufgebaut; `SO_PEERCRED` beider Endpunkte bindet die exakte Sender-/Empfänger-
PID/UID/GID samt separat geprüfter PID-Startzeit und Ready-Nonce. `SO_PASSCRED`
ist deaktiviert, jeder finale Empfangsendpunkt besitzt vor dem ersten Send
attestiert `SO_PASSRIGHTS=0`, und keine Runtime-Message erwartet
`SCM_CREDENTIALS` oder `SCM_RIGHTS`.
Der Broker verwirft Replay, Gap, abweichende feste Peeridentität, Session oder
Expiry über `now+25 ms`. Für eine gültige Message
erhöht ausschließlich er das gesamte Control Word per CAS exakt von
`(RUNNING|CLOSING,n,0)` auf derselben State-Stufe nach
`(RUNNING|CLOSING,n+1,0)`. Nach erfolgreicher CAS sendet er genau
eine fixed-size Renewal Approval mit derselben vor der CAS validierten absoluten
Expiry, Session und neuen Sequenz als exakt
`sizeof(TerminalBrokerRenewalApprovalV1)` über eine zweite exklusive
nonblocking `SOCK_SEQPACKET`-Verbindung an den
`TerminalKernelLeaseShimV11`. Der Shim hat nur die read-only Map, akzeptiert
ausschließlich den gebundenen Broker-Peer, exakte Struct-Länge ohne
`MSG_TRUNC|MSG_CTRUNC` und ohne überlebende Ancillary-FDs. Er setzt den Timer nur,
wenn sein Acquire-Load noch exakt RUNNING oder CLOSING mit dieser Sequenz
zeigt. Linearisiert
danach ein Trip vor `timer_settime`, darf der Shim
ausschließlich die bereits bestätigte absolute Expiry setzen; sie liegt
weiterhin höchstens bei `now_at_broker_validation+25 ms` und kann den Trip
nicht nach hinten verlängern. Nach TERMINATING, CLOSED, COMMITTED oder
CLOSED_FAILSTOP erzeugt der Broker keine weitere Renewal Approval. In
TERMINATING darf der Shim die Expiry nur verkürzen, nie verlängern oder
disarmen. In CLOSED bleibt der Timer armed, bis der Broker nach validiertem
durablem CLOSE-COMMIT-ACK das Control Word nach COMMITTED linearisiert.
COMMITTED ist die monotone brokerbestätigte Commit-Approval-Autorität; die zwei
Approval-Nachrichten sind idempotente Wakeups und keine zusätzliche Wahrheit.

`TerminalTradingSignalEnvelopeV1` wird vom frisch gestarteten, zu diesem
Zeitpunkt einzigen Trading-Leader **vor** Filterinstallation und vor Erzeugung
jedes weiteren Trading-/Python-/Shim-TID hergestellt. Der Leader setzt per
`rt_sigprocmask(SIG_SETMASK,...)` die vollständige Menge aller blockierbaren
Signale und entfernt sämtliche userdefinierten Handler/`SA_RESTART`-
Dispositionen. Der exakte Signalset-Hash, jede Disposition und die zu diesem
Zeitpunkt einelementige `/proc/self/task`-Menge werden extern attestiert. Alle
späteren TIDs erben dieselbe Maske; keiner besitzt einen Signalhandler.

Nach Herstellung dieses Envelopes sind `rt_sigaction`, `rt_sigprocmask`,
`sigaltstack`, `signalfd`, `signalfd4` und sämtliche Signal-Erzeugungssyscalls
des Trading-TGID außer den drei exakt gebundenen
`pidfd_send_signal(...,SIGKILL,NULL,0)`-Stufen durch den gestapelten
default-deny-Filter mit `SECCOMP_RET_KILL_PROCESS` gesperrt. Dasselbe gilt für
libc-/pthread-Aufrufe über ihre zugrunde liegenden Syscalls. Kein blockierbares
Signal kann deshalb post-Ready zugestellt werden oder einen
Notification-Wait unterbrechen. `SIGKILL` beendet den TGID fail-safe;
`SIGSTOP` stoppt den gesamten TGID einschließlich Shim, sodass keine Approval
verarbeitet wird und die bereits armed Kernel-Lease ausläuft. Ein späteres
`SIGCONT` ändert die blockierte Maske nicht. Synchronous-fatal Kernel-Faults
dürfen ausschließlich zur Prozessbeendigung führen, niemals zu einem Handler-
Return in den Trip-Entry.

`TerminalKernelTripRequestV2` ist keine Speicherstruktur, sondern die
kernel-erzeugte Seccomp-Notification für den exakt gebundenen ersten
Kernelaufruf `pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)` des
`TerminalSelfKillEntryV4`. Ihre Listener-Übergabe folgt ausschließlich
`TerminalSeccompListenerHandoffV2`; ein Socket-, `sendmsg`-, `sendmmsg`-,
SCM_RIGHTS- oder `/proc/fd`-Transfer ist verboten und besitzt keine Ausnahme
im globalen Send-Gate.

Vor Beginn des Handoffs existieren Broker und der noch single-threaded
Trading-Leader bereits mit gebundenen PID-/Startzeitidentitäten in der
Session-Cgroup. Der Broker besitzt den vorab gebundenen Trading-PIDFD und hält
eine exakt inventarisierte Files-Table, deren reservierter Listener-Ziel-FD
der nach Linux-Niedrigst-FD-Allokation nächste freie Slot ist. Der Trading-
Leader hält ausschließlich den exakt reservierten Listener-Quell-FD frei,
bestätigt `ptrace_scope=1`, gleiche Real-Credentials, seine noch bestehende
Owner-Dumpable-Eigenschaft und setzt einmalig
`prctl(PR_SET_PTRACER,broker_pid)`. Während dieses Fensters verbietet der
globale Guard im Phase-State `LISTENER_HANDOFF` jede Erzeugung eines
`AF_UNIX|SOCK_SEQPACKET`-Runtime-Sockets; im gesamten Session-Cgroup bleibt
zusätzlich jeder `sendmsg`/`sendmmsg` gesperrt.

Der Trading-Leader installiert anschließend vor Erzeugung irgendeines weiteren
Trading-/Python-/Shim-TID den Filter mit
`SECCOMP_FILTER_FLAG_NEW_LISTENER|SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV`.
Fehlt `WAIT_KILLABLE_RECV` im gebundenen Kernel oder wird die Flag-Kombination
nicht exakt akzeptiert, ist die Capability unzulässig und OPEN bleibt
gesperrt. Der Return-FD muss exakt dem reservierten Quell-FD entsprechen. Der
Broker ruft danach aus seinem exakt gebundenen Bootstrap-TID genau einmal
`pidfd_getfd(trading_pidfd,listener_source_fd,0)` auf. Sein Bootstrap-Seccomp-
Filter erlaubt nur dieses skalare Tupel. Der globale `file_receive`-Hook prüft
zusätzlich exakten Broker-TGID/TID/Startzeit/Cgroup und den nicht-socketartigen
Filetyp und führt **vor** FD-Allokation genau eine BPF-CMPXCHG
`LISTENER_HANDOFF→LISTENER_RECEIVED` aus. Nur der Gewinner erhält `0`; jeder
zweite, andere oder wiederholte Receive-Versuch sieht den falschen Altwert und
erhält `-EPERM`. Geschützte Runtime-Sockets und der Guard-Control-Socket
bleiben disjunkt und weiterhin `-EPERM`. Der Rückgabe-FD muss exakt dem
reservierten Broker-Ziel-FD entsprechen. Scheitert `receive_fd` nach der
CMPXCHG, bleibt `LISTENER_RECEIVED` terminal und der Startup wird ohne Retry
abgebrochen.

Der Broker prüft Listener-Inode, Anon-Inode-Typ, Filterhash, Session-Nonce und
Ready-Nonce und signalisiert die vollständige Übernahme ausschließlich über
ein vor Fork geerbtes, festes ACK-Eventfd; auch dieses Verfahren verwendet
kein Socket. Erst nach dem passenden ACK schließt der Trading-Leader seinen
Quell-FD, beweist dessen Abwesenheit und ruft in dieser Reihenfolge exakt
`prctl(PR_SET_PTRACER,0)` und `prctl(PR_SET_DUMPABLE,0)` auf. Der Broker setzt
ebenfalls `PR_SET_DUMPABLE=0`; beide leeren anschließend alle Capability-Sets,
setzen `no_new_privs` und installieren die finalen Filter, die `pidfd_getfd`,
erneute `prctl`-Lockerung, Listener-Erzeugung, FD-Duplikation und FD-Transfer
vollständig sperren. Ein externer Observer muss jetzt genau einen Listener-
Halter, den Broker-Ziel-FD, und null Trading-/Launcher-/Guardian-/Worker-Halter
belegen.

Nur nach diesem Nachweis darf der separate, single-threaded und hashgebundene
`TerminalHandoffRevocationAttestorV1` auf seinem ausschließlich von ihm
gehaltenen `HANDOFF_REVOCATION_GRANT_CONTROL`-Socket exakt
`shutdown(...,SHUT_WR)` ausführen. Der `socket_shutdown`-LSM-Hook prüft
Attestor-TGID/TID/Startzeit/Cgroup, Socket-Tag/-Cookie, Session-Nonce, `how`
und den Altwert und linearisiert genau einmal
`LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED`. Der Guard besitzt weder diesen
Socket noch diese Grant-Autorität. Erst aus `HANDOFF_REVOKED_GRANTED` darf der
Guard auf seinem disjunkten `PHASE_CONTROL`-Socket per `SHUT_RD` genau
`HANDOFF_REVOKED_GRANTED→BOOTSTRAP` konsumieren. Erst danach dürfen Runtime-
Sockets entstehen. Ein Fehler, falscher FD, zweiter Aufruf, fehlendes ACK,
nicht geschlossener Quell-FD, fehlgeschlagene Ptrace-/Dumpable-Revocation,
abweichende Halterinventur, fehlender Grant oder vertauschte Autorität
zerstört den Startup ohne Retry derselben Session. Erst hinter dieser
irreversiblen Grenze erzeugt der Leader
die exakt attestierte feste TID-Menge; jeder neue TID muss den Filter erben.
Nach vollständiger TID-Erzeugung wird der separate TSYNC-Basisfilter auf alle
TIDs angewandt und sperrt jede weitere Taskbildung. `/proc/<tid>/status`,
Filterzahl und ein negativer Self-PIDFD-Probe-Child belegen die identische
Notification-Abdeckung jedes TID. Nur der Broker hält den Listener; neue
Listener, Filterlockerung, `SECCOMP_USER_NOTIF_FLAG_CONTINUE` und
`SECCOMP_IOCTL_NOTIF_ADDFD` sind verboten.

Mit Eintritt des Self-PIDFD-Syscalls blockiert der Kernel den aufrufenden TID
und erzeugt eine nicht vom Trading-Adressraum beschreibbare Notification.
Vor Broker-Receive verhindert das geerbte Signal-Envelope jede zustellbare
blockierbare Signalunterbrechung; nach erfolgreichem Receive stellt
`WAIT_KILLABLE_RECV` nichtfatale Signale bis zur Antwort zurück. Der Broker
validiert Arch, Syscallnummer und alle vier skalaren Argumente.
`SECCOMP_IOCTL_NOTIF_ID_VALID` ist nur eine Liveness-Prüfung: ein
inzwischen ungültiger ID nach empfangener, sonst exakt passender Notification
gilt wegen möglichem Task-Exit ebenso fail-safe als Trip und wird nicht
verworfen. Sobald der Listener in `epoll_wait` readable/HUP/ERR gemeldet wurde,
ist außerdem **jedes** Ergebnis von `SECCOMP_IOCTL_NOTIF_RECV` total: Erfolg
wird normal validiert; `ENOENT`, `EINTR`, `EAGAIN`, ein Short-/ABI-Fehler oder
jeder unbekannte Fehler wird konservativ als Terminal Trip klassifiziert und
niemals als „kein Event“ übersprungen. In RUNNING oder CLOSING linearisiert der
Broker genau eine CAS nach
TERMINATING, stoppt ab diesem
Punkt Renewals und fordert anschließend selbst über seinen gebundenen Child-
PIDFD `SIGKILL` an. Er antwortet niemals CONTINUE. Ein Halt des aufrufenden TID
nach Kernelannahme und ein Whole-child-Stop können weder Notification noch CAS
oder Broker-Kill verhindern. Stirbt oder stallt der Broker, entstehen keine
Approvals und die bereits armed Lease läuft kernel-seitig aus. Schließt der
Listener vor Notification-Annahme und kehrt der Self-PIDFD-Aufruf deshalb mit
einem Fehler zurück, führt derselbe TID ohne Retry die Guardian-/Broker-PIDFD-
und Liveness-Close-Fallbacks aus; der fehlende Broker kann keine Approval mehr
erzeugen. Ein Return wegen eines blockierbaren Signalhandlers ist innerhalb
des gebundenen Envelopes unmöglich. `SA_RESTART`-bedingte Duplikat-
Notifications sind daher kein zulässiger Runtime-Pfad; falls der Kernel- oder
Signal-Probe sie dennoch erzeugt, verhindert dies OPEN beziehungsweise gilt
post-OPEN als Capability-Verlust mit terminaler Trip-Klassifikation.

Trifft eine gültige Notification erst in CLOSED ein, linearisiert der Broker
`CLOSED→CLOSED_FAILSTOP` und fordert denselben Child-PIDFD-Kill an; ein bereits
laufender Worker-Append entscheidet ausschließlich durch seinen durablen
COMMIT, ob der Folgestart clean ist. In COMMITTED bleibt der State unverändert
clean und der Broker fordert nur die physische Child-Termination an. In
TERMINATING oder CLOSED_FAILSTOP ist die Notification ein idempotentes
Duplikat ohne zweite State-Transition oder zweiten Worker-Request.

Vor dem Kernel-Eintritt existiert bewusst kein behaupteter Trip-Zustand und
keine writable lokale Sicherheitsautorität. Wird nur der aufrufende TID davor
angehalten, ist noch kein `TerminalKernelTripRequestV2` entstanden; wird das
gesamte Child davor angehalten, kann der Shim keine Approval mehr verarbeiten
und der armed Timer läuft aus. Nach Kernelannahme ist der Request dagegen
OS-monoton: kein vorhandener Trading-TID kann ihn durch Store, Mapping-, FD-
oder Syscalloperation zurücknehmen. Alle fachlichen Gates lesen unmittelbar
vor jedem Side Effect ausschließlich das read-only Control Word und akzeptieren
nur RUNNING.

`TerminalTripLivenessPipeV1` wird vor Ready mit
`pipe2(O_NONBLOCK|O_CLOEXEC)` erzeugt. Nach dem Schließen aller Bootstrap-
Kopien besitzt der Trading-Prozess exakt das einzige Write-Ende und der Broker
exakt das einzige Read-Ende; Inode, FD-Nummern, Pipe-Capacity, exklusiver Besitz
und der leere Initialzustand sind in OPEN gebunden. Diese Pipe ist kein
Nachrichtenkanal: Von ihrer Erzeugung bis zum Prozessende ist jeder `write`,
`writev`, `splice`, `vmsplice` oder äquivalente Datentransfer auf ihr Write-Ende
verboten. Der Broker liest sie ebenfalls nie. Damit kann für diesen Kanal weder
eine Pipe-Page allokiert noch User-Payload kopiert werden. Seine einzigen
zulässigen Runtime-Ereignisse sind Verlust des letzten Writers und daraus
entstehendes `POLLHUP|POLLERR`; ein beobachtetes `POLLIN` oder Pipe-Byte ist
unmöglich und wird deshalb ebenfalls fail-safe als Terminal Trip behandelt.

Nach Bootstrap verbieten die endgültigen Filter in Trading und Broker weiterhin
vollständig `mmap`, `munmap`, `mremap`, `mprotect`, `pkey_mprotect`, `mlock`,
`mlock2`, `munlock`, `munlockall`, `madvise`, `process_madvise`,
`remap_file_pages`, `userfaultfd`, alle `ioctl(UFFDIO_*)`, `mbind`,
`set_mempolicy`, `migrate_pages`, `move_pages` und jede äquivalente unbekannte
Mapping-, Migration- oder Page-Reclamation-Operation. Die letzte FD-Inventur
darf keinen userfaultfd-FD enthalten. Kernel-/WSL-Build, Page Size,
Memlock-Limit, NUMA-Policy, deaktivierte automatische NUMA-Migration und
ausgeschlossener Memory-Hotplug bleiben Capability- und OPEN-Bestandteil; sie
sind jedoch keine Voraussetzung für einen Pipe-Write, weil kein solcher
Syscall im Terminal-Sicherheitsweg existiert.

Der einzige Liveness-Writer ist nicht nur ein Bootstrap-Snapshot. Vor Übergabe des
Write-Endes wird `TerminalTradingTaskTopologyV2` vollständig erzeugt und danach
irreversibel eingefroren. Es bindet exakt einen Trading-TGID, die vollständige
sortierte Menge aller zugehörigen TIDs samt Startzeiten und Rollen, den Native-
Shim-TID, die je Rolle gestapelten Seccomp-BPF-Hashes, den Session-Cgroup- und
PID-Namespace-Fingerprint sowie die gemeinsame Files-Table-Identität. Jeder
Trading-/Python-/Shim-TID muss gegenüber dem Trading-Leader bei einer vor
Ready ausgeführten `kcmp(...,KCMP_FILES,...)`-Prüfung exakt Gleichheit liefern;
ein nicht verfügbares oder nicht autorisiertes `kcmp` ist kein PASS. Damit
existiert innerhalb des TGID genau eine gemeinsame Deskriptortabelle, nicht je
Thread eine verdeckte Kopie.

Ein gemeinsamer, mit `SECCOMP_FILTER_FLAG_TSYNC` auf sämtliche bereits
existierenden Trading-/Python-/Shim-TIDs angewandter Basisfilter verbietet vor
Ready und danach vollständig `fork`, `vfork`, `clone`, `clone3`, `unshare`,
`setns`, `execve`, `execveat` und `close_range`. Klassisches `clone` besitzt
keine Flag-Ausnahme; insbesondere wird weder eine Prozess- noch eine spätere
Thread-Erzeugung erlaubt. `clone3` wird vollständig gesperrt, weil klassisches
Seccomp die referenzierte `struct clone_args` nicht dereferenzieren kann. Alle
benötigten Threads, Pools und nativen Rollen müssen deshalb vor diesem Filter
existieren. Weitere rollenbezogene Filter dürfen den gemeinsamen Basisfilter
nur stapeln und verschärfen, niemals ersetzen oder lockern. TSYNC-Fehler,
abweichende TID-Mengen oder ein nach Filterung hinzugekommener Task verhindern
Ready und OPEN. Jeder verbotene Taskbildungsversuch verwendet exakt
`SECCOMP_RET_KILL_PROCESS`; ein bloßes `EPERM`, Userspace-Callback oder
filterbarer Pointerinhalt wird nicht als Sicherheitsgrenze verwendet.

Nach Übergabe und Schließen sämtlicher Bootstrap-Kopien sind außerdem alle
alternativen Erzeugungswege für eine zusätzliche Kernel-Referenz auf das
Write-Ende gesperrt: `dup`, `dup2`, `dup3`, `pidfd_getfd`, `F_DUPFD`,
`F_DUPFD_CLOEXEC`, `open`, `openat`, `openat2`, `creat`,
`open_by_handle_at`, `sendmsg`/`sendmmsg` und `recvmsg`/`recvmmsg` in
Trading-/Python-Threads sowie `io_uring_setup`, `io_uring_register` und
`io_uring_enter`, Legacy-AIO, `poll`, `ppoll`, `select`, `pselect6` und jeder
FD-Multiplexer mit einer durch Seccomp nicht dereferenzierbaren FD-Liste sind
unzulässig. `read`, `write`, `splice`, `tee`, `vmsplice`, `sendfile`,
`copy_file_range`, `readv`, `writev`, `fcntl` und `ioctl` werden bei einem
skalaren Liveness-FD-Argument ebenfalls abgelehnt. `epoll_ctl` bleibt für
andere vorab gebundene Runtime-FDs zulässig, wird aber bei
`fd==trip_liveness_write_fd` durch das skalare FD-Argument abgelehnt. Damit kann
das Write-Ende weder über `/proc/self/fd`,
`SCM_RIGHTS`, eine io_uring-Fixed-File-Tabelle noch eine zweite FD-Nummer
festgehalten werden. Auch diese Writer-Referenzbildungsversuche verwenden
exakt `SECCOMP_RET_KILL_PROCESS`. Die Trading-/Python-Rollenfilter sind
default-deny-Allowlisten: Der Liveness-Writer-FD darf in der gesamten gebundenen
Syscall-Oberfläche ausschließlich als skalares erstes Argument von
`close(trip_liveness_write_fd)` erscheinen. Jeder andere Syscall oder jedes
andere FD-Argument mit dieser Nummer führt vor FD-Auflösung exakt zu
`SECCOMP_RET_KILL_PROCESS`; insbesondere gibt es keine Pointer-, Count- oder
Payload-Ausnahme für `write`. Nach Ready ist außerdem jeder FD-erzeugende Syscall unzulässig,
einschließlich neuer Files, Sockets, Accepts, Pipes, Event-/Signal-/Timer-FDs,
epoll-/inotify-/fanotify-/userfault-/pidfds, Memfds, perf-/BPF-/Filesystem-
Kontext-FDs und Message Queues. Die kernelversionsgebundene Syscallmatrix ist
default deny und muss sämtliche FD-liefernden Syscalls enumerieren; ein
unbekannter neuer Syscall bleibt gesperrt. Damit kann die nach `close` freie
numerische Writer-FD-Nummer bis zum Prozessende nicht wiederverwendet werden.
Der Bootstrap-Nachweis enumeriert unmittelbar vor OPEN
sämtliche `/proc/<pid>/fd` und `/proc/<pid>/fdinfo` des abgeschlossenen
Session-Cgroups und lehnt unbekannte Prozesse, TIDs, Pipe-Inode-Referenzen,
io_uring-FDs oder writerbezogene epoll-`tfd`-Einträge ab. Sämtliche Bootstrap-
Transfer-Sockets sind geschlossen; verbleibende Unix-Sockets und Peerrollen
sind exakt inventarisiert und haben nie den Pipe-Writer übertragen. Das
Trading-Child setzt nach der letzten `KCMP_FILES`-/FD-Inventur und vor Ready
`PR_SET_DUMPABLE=0`, leert sämtliche Capability-Sets und setzt `no_new_privs`;
die gestapelten Filter verbieten jede spätere Lockerung sowie Credential- oder
Namespace-Wechsel. Zusammen mit der gebundenen Ptrace-/Yama-Policy verhindert
dies auch externes `pidfd_getfd` durch nicht autorisierte Prozesse. Das
zulässige Envelope schließt weiterhin privilegierte Co-Tenants aus.

Erst nach exakt diesem Topologie-, Files-Table-, Referenz- und Filter-Nachweis
darf Ready bestätigt werden. Ab OPEN kann deshalb kein Child, kein neuer
Thread und kein anderer Kernel-FD-Halter den letzten Writer bewahren. Weil kein
Pipe-Write erlaubt ist, kann beim atomaren Slot-Entzug weder eine bereits
laufende Writer-`struct file`-Referenz noch Pipe-Page-Allokation, Cgroup-Charge,
Direct Reclaim, Compaction, Writeback oder `copy_from_user` vorliegen. Der
einmalige rohe `close` entfernt die einzige gemeinsame FD-Tabellenreferenz; ein
Close-Retry ist auch bei `EINTR` wegen möglicher FD-Wiederverwendung verboten.

Der `TerminalParentGuardianV13` übergibt dem Trading-Prozess vor Ready drei
vorab geöffnete PIDFDs: Self-PIDFD auf den Trading-Prozess, Guardian-PIDFD auf
den tatsächlichen Parent und Broker-PIDFD auf den gebundenen Broker. Ziel-PID,
Startzeit, erfolgreiche Signal-0-Probe und die ausschließlich erlaubte
Operation `pidfd_send_signal(bound_pidfd,SIGKILL,NULL,0)` sind für jeden der
drei Deskriptoren in OPEN und im BPF-Hash gebunden. Kein anderer Signalwert,
`siginfo`-Pointer, Flag oder Ziel-PIDFD ist zulässig.

`TerminalSelfKillEntryV4::terminal_trip()` führt keine lokale Mutation aus.
Sein **erster Kernelaufruf** ist exakt
`pidfd_send_signal(self_pidfd,SIGKILL,NULL,0)`. Der gebundene, an alle TIDs
vererbte NEW_LISTENER-/WAIT_KILLABLE_RECV-Filter
erzeugt dafür `TerminalKernelTripRequestV2` per `SECCOMP_RET_USER_NOTIF`; im
regulären Pfad wird der Syscall weder ausgeführt noch an den TID zurückgegeben.
Erst die Kernelannahme dieser Notification ist der lokale Request-
Linearization-Point. Die globale Trip-Linearization ist die anschließende
Broker-CAS nach TERMINATING.

Nur falls dieser erste Aufruf wegen geschlossenem/fehlerhaftem Listener oder
einer Kernel-/Filterabweichung überhaupt zurückkehrt, führt der Entry – für
jeden Returnwert einschließlich `0`, jeweils genau einmal und ohne Retry – die
folgenden fallbacks aus, solange der Thread noch ausgeführt wird:

1. `pidfd_send_signal(guardian_pidfd,SIGKILL,NULL,0)`;
2. `pidfd_send_signal(broker_pidfd,SIGKILL,NULL,0)`;
3. atomarer Exchange des einzigen `trip_liveness_write_fd`-Slots gegen `-1`
   und genau ein roher `close` auf dem entnommenen FD.

Jede erfolgreiche Self-Signal-Anforderung stoppt den Side-Effect-Prozess hart.
Jede erfolgreiche Guardian-Signal-Anforderung beendet die Renewal-Quelle;
jede erfolgreiche Broker-Signal-Anforderung beendet Approval und Control-Word-
Fortschritt. Bei Rückkehr – einschließlich `EINTR`, `ESRCH`, `EPERM`, `EBADF`
oder unbekanntem Fehler – wird die nächste Stufe ausgeführt; ein Erfolg wird
nicht durch Userspace-Bestätigung oder Reap-Warten relativiert. Der abschließende
Close wird nie wiederholt. Die Liveness-Pipe war zu diesem Zeitpunkt seit ihrer
Erzeugung leer und unbeschrieben; daher kann der Close nicht hinter einer
diesem Kanal zuzurechnenden Pipe-Page-Allokation, Writer-Copy oder temporären
Write-Referenz warten. Bleibt der Broker gesund, beobachtet er HUP. Ist er
gestoppt, tot oder dauerhaft nicht schedulable, kann er unabhängig vom Close
keine neue Renewal-CAS oder Approval erzeugen. Kein Returnwert erlaubt eine
Rücknahme des kernel-seitigen Request-Fakts, weiteren Gate-Eintritt oder
Session CLOSE-COMMIT.

Der Broker priorisiert `POLLHUP`, `POLLERR` und das unmögliche `POLLIN` der
`TerminalTripLivenessPipeV1` vor weiteren Renewals; er liest keine Pipe-Daten.
Für eine gültige Seccomp-Notification oder HUP/POLLERR/POLLIN führt er in
RUNNING oder CLOSING genau einmal die CAS
`(RUNNING|CLOSING,n,0)→(TERMINATING,n,1)` aus. Linearisiert
eine bereits in Bearbeitung befindliche Renewal zuerst, bleibt nur deren
vorvalidierte Restlaufzeit von höchstens `25 ms`; linearisiert der Trip zuerst,
scheitert jede folgende Renewal-CAS. Erst nach der neuen erfolgreichen Trip-CAS
schreibt der Broker best effort auf getrennte Guardian-/Shim-Eventfds und sendet
genau einen fixed-size KILL-Request über den ausschließlich zwischen Broker und
Persistence Worker geöffneten `SOCK_SEQPACKET`-Kanal. Der Trading-Prozess
besitzt keinen Worker-IPC-FD. Volle/geschlossene Eventfds, ein verlorener
Worker-Request oder Broker-Crash nach der CAS beeinträchtigen die Safety nicht:
Guardian liest das Control Word vor jedem Heartbeat und spätestens alle
`10 ms`, der Shim vor jeder Timer-Renewal, und der armed Timer läuft ohne neue
Approval ab. Der Guardian fordert bei TERMINATING sofort über den gebundenen
PIDFD harte Termination an. Ein vor dieser CAS erfolgreich gesendetes
Broker-`SIGKILL` ist ebenfalls fail-safe: Der Broker kann dann keine weitere
Approval erzeugen, und der bereits armed Timer läuft spätestens mit der letzten
gebundenen Expiry ab.

Der Worker mappt das Control Word read-only und akzeptiert den Request nur als
exakt `sizeof(TerminalWorkerKillRequestV2)` mit
`msg_control=NULL/msg_controllen=0`, ohne `MSG_TRUNC|MSG_CTRUNC`, ohne
Ancillary-Inhalt oder unbekannte Flags vom per `SO_PEERCRED` gebundenen
Broker-Peer. Vor jedem
Journal-I/O führt er einen Acquire-Load aus
und verlangt exakt `(TERMINATING,n,1)` mit derselben im Request gebundenen
Renewal-Sequenz, Session-ID, Control Event ID und Broker-Generation. Ein
Request bei RUNNING/CLOSING/CLOSED/COMMITTED/CLOSED_FAILSTOP, eine abweichende
Sequenz oder ein anderer Peer wird
ohne Mutation fail closed verworfen. Damit ist die Kausalität „Worker-Request
nur nach neuer erfolgreicher Trip-CAS“ receiverseitig ausführbar geprüft; sie
wird nicht als durch Seccomp dereferenzierbarer `msghdr`-Payload behauptet.

Für das geordnete Close akzeptiert der Worker zunächst in Control Word CLOSING
nur exakt `sizeof(TerminalWorkerClosePrepareRequestV2)` mit disjunkter Message-
Type-Konstante, Session, Reconciliation-/Journal-Head, Close-Nonce und Broker-
Generation. Er schreibt ausschließlich `RUNTIME_SESSION_CLOSE_PREPARE` über
den vorab geöffneten Lifecycle-Handle und antwortet nach durablem Append mit
`TerminalWorkerClosePrepareAckV2`. Ein byteidentisches Duplikat derselben
Session/Nonce/Phase erzeugt keinen zweiten Record, sondern dieselbe ACK erneut.
Das erzeugt keine CLOSED- oder Clean-Klassifikation.

Davon und vom KILL-Pfad strikt getrennt akzeptiert der Worker in Control Word CLOSED nur exakt
`sizeof(TerminalWorkerCloseCommitRequestV2)` vom selben gebundenen Broker-Peer.
Dieser Request besitzt eine disjunkte Message-Type-Konstante und bindet
CLOSE-PREPARE-Fingerprint, Session, Close-Nonce, `(CLOSED,n,0)` und Broker-
Generation. Er autorisiert ausschließlich den Lifecycle-Record
`RUNTIME_SESSION_CLOSE_COMMIT`, niemals einen KILL- oder State-Write. Der Worker
antwortet erst nach durablem Commit mit exakt
`TerminalWorkerCloseCommitAckV2`. Ein byteidentisches Duplikat erzeugt keinen
zweiten COMMIT, sondern dieselbe ACK erneut; jeder Request in
RUNNING/CLOSING/TERMINATING, jede abweichende Bindung oder ein konfliktärer
zweiter COMMIT wird ohne Mutation abgewiesen.

Der Trading-Prozess ruft denselben nativen Gate-Entry unmittelbar vor jeder
Snapshot-Akzeptanz, jedem Intent-/Execution-Side-Effect und nach Rückkehr aus
jedem potenziell blockierenden Syscall auf. Er prüft Control Word, read-only
Lease-Sequenz und absolute Expiry. Jeder State ungleich RUNNING sowie eine
stale, rückläufige oder übersprungene Lease blockiert atomar und ist durch
spätere Heartbeats nicht
heilbar. Ist nur der Trading-Thread vor dem Trip blockiert, darf der Shim
weiter renewen; das ist kein Lease-Fehler, weil der Thread währenddessen keinen
Side Effect ausführt. Nach Kernelannahme eines Trip-Requests blockiert der
aufrufende TID im Kernel; die externe Broker-CAS sperrt alle anderen Gates und
verhindert jede weitere Renewal. Das harte Signal wird deshalb unabhängig von
der Rückkehr des aufrufenden Trading-TID erzeugt.

Weder Trading-Prozess noch Persistence Worker besitzen ein Recht, Control Word,
Timer, Lease-Seite, Guardian, Signal oder Frist zu lösen, zu ersetzen oder zu
verlängern. Einzige Signal-Ausnahmen sind die drei fest gebundenen Self-,
Guardian- und Broker-PIDFDs des Trading-Prozesses mit exakt `SIGKILL`,
`siginfo=NULL` und `flags=0`; sie können ausschließlich den Trading-Prozess
selbst, die Renewal-Quelle oder den Approval-Writer fail-safe terminieren. Der Trading-Prozess besitzt
insbesondere weder writable Control-Word-Map noch Broker→Worker- oder
Guardian→Broker-FD. Eine Plattform ohne
nachweisbare Kernel-Self-Death-Primitive oder ohne die beschriebenen
prozessgetrennten Mapping-/Peer-Grenzen darf keine Runtime Session öffnen.

Bei geordnetem Ende bleibt das Trading-Child zunächst alive, vollständig
gegatet und side-effect-frei. Nach abschließender Reconciliation sendet der
Guardian dem Broker über den gebundenen Kanal einen fixed-size
`TerminalGuardianOrderlyCloseRequestV3` mit Session-ID, Reconciliation-/
Journal-Head, live Child-PID/-Startzeit/-PIDFD-Identität, erwarteter Renewal-
Sequenz, Close-Nonce und Guardian-Credential/Nonce. Der Guardian wiederholt bei
unklarer Zustellung ausschließlich dieselben Bytes mit derselben Nonce bis zur
absoluten 100-ms-Request-Deadline. Der Broker akzeptiert den ersten gültigen
Request ausschließlich in RUNNING und linearisiert vor Worker-I/O
`RUNNING→CLOSING`. Ein byteidentisches Duplikat in CLOSING bindet dieselbe
Operation; jede andere Session, Nonce oder Payload ist ein terminaler Konflikt.
Nach CLOSING sendet der Broker den logisch einen, transportseitig bis zur
absoluten Deadline byteidentisch wiederholbaren
`TerminalWorkerClosePrepareRequestV2` an den Worker.

Der Worker schreibt über seinen vorab geöffneten Lifecycle-Handle genau
`RUNTIME_SESSION_CLOSE_PREPARE` und antwortet erst nach durablem Append mit
`TerminalWorkerClosePrepareAckV2` samt PREPARE-Fingerprint. Der Broker
validiert Peer, exakte Länge, Nonce, Reconciliation und Fingerprint. Nur wenn
Control Word weiterhin exakt `(CLOSING,n,0)` ist und kein vorrangiger
Trip-/HUP-/Notification-Befund vorliegt, linearisiert er exakt eine CAS
`(CLOSING,n,0)→(CLOSED,n,0)`; aus TERMINATING ist CLOSED unzulässig. Gewinnt ein
Trip/HUP vor dieser CAS, bleibt PREPARE ohne COMMIT und damit autoritativ
unclean.

Die erfolgreiche Broker-CAS auf CLOSING ist der globale Pre-Close-Gate-
Zeitpunkt; ab ihr kann kein neuer fachlicher Tick-, Intent-, Execution- oder
State-Side-Effect beginnen. Die spätere Broker-CAS auf CLOSED ist der globale
logische Close- und COMMIT-Berechtigungszeitpunkt. Ein späterer kernel-seitiger
Trip-Request oder Child-Exit kann deshalb nur noch die physische
Termination vorziehen und die Session nicht wieder öffnen. Clean wird sie
trotzdem ausschließlich durch einen danach durable gewordenen CLOSE-COMMIT;
scheitert dieser, bleibt sie unclean.

Auch nach bestätigtem Broker-CLOSED bleiben Timer armed, Child alive/gegatet
und OS-/Self-Death-Bindung aktiv. Der Broker sendet nun über den bereits
gebundenen `BW_REQUEST`-`SOCK_SEQPACKET` den logisch einen, transportseitig bis
zur absoluten Deadline byteidentisch wiederholbaren fixed-size
`TerminalWorkerCloseCommitRequestV2`, der PREPARE, CLOSED-Control-Word,
Broker-Generation und Close-Nonce bindet. Der Worker akzeptiert ihn nur bei
eigenem Acquire-Load exakt `(CLOSED,n,0)`, schreibt genau den gebundenen
`RUNTIME_SESSION_CLOSE_COMMIT` und antwortet erst nach durablem Commit mit
`TerminalWorkerCloseCommitAckV2` samt Commit-Fingerprint. Der Broker validiert
Peer, exakte Länge, Nonce und Fingerprint und linearisiert erst dann
`CLOSED→COMMITTED`. Danach sendet er je eine fixed-size
`TerminalBrokerCloseCommitApprovalV2` über die getrennten Broker→Shim-Close-
und Broker→Guardian-Close-Kanäle. Shim und Guardian akzeptieren ausschließlich
den gebundenen Broker-Peer und passende PREPARE-/COMMIT-/COMMITTED-Identitäten.
Die Nachrichten beschleunigen die Reaktion; die brokerbestätigte, monotone
Approval-Autorität ist COMMITTED im read-only Control Word.

Scheitert der COMMIT-Write, stirbt ein Beteiligter oder bleibt ein ACK aus,
erreicht das Control Word COMMITTED nicht; weil CLOSED keine Renewals erzeugt,
läuft der armed Timer aus. Erst ein Acquire-Load COMMITTED erlaubt dem Shim den
Timer-Disarm und dem Guardian den Trading-Exit; bei empfangener Approval muss
deren Payload zusätzlich vollständig passen. Bleibt eine Approval-Nachricht
aus, erkennen Shim spätestens nach `1 ms` und Guardian spätestens nach `10 ms`
COMMITTED selbst. Diese State-Stufe ist bereits die ausschließlich vom Broker
nach gültigem CommitAck gesetzte Approval-Autorität. Das dadurch entstehende Liveness-HUP wird in COMMITTED plus
durablem CLOSE-COMMIT nur als erwarteter Exit-Nachweis geprüft.
HUP/POLLERR/POLLIN vor CLOSED ist dagegen ein Terminal Trip; CLOSED ohne
CLOSE-COMMIT ist niemals ein clean shutdown. Der Guardian löst OS- und Self-
Death-Bindung erst nach CLOSE-COMMIT und bestätigtem Trading-Child-Exit.
Guardian und Session binden außerdem
den einmaligen Worker-Lease/Fencing-Token. Nach ungeordnetem Trading- oder
Guardian-Exit muss der Guardian, ersatzweise der Recovery-Pfad, den Worker
terminieren oder dessen Lease fencen. Ein späterer Startup darf weder Recovery
noch einen neuen Worker beginnen, solange Prozessende und Entzug des alten
Journal-Schreibrechts nicht über PID/Startzeit, Ready-Nonce, Fencing-Token und
exklusiven Coordinator-Lock eindeutig bewiesen sind.

#### 7.8.1 Close-Kanal-, LSM-, Seccomp- und Fehlerzustandsvertrag V8

Vor Rollen- oder Socket-Erzeugung lädt ein separater, single-threaded
`TerminalRuntimeSocketLSMGuardV3` exakt die hashgebundenen BPF-LSM-Programme
und hängt sie systemweit als BPF Links an `socket_post_create`,
`unix_stream_connect`, `socket_setsockopt`, `socket_sendmsg`,
`socket_shutdown` und `file_receive`. Programme,
`BPF_MAP_TYPE_SK_STORAGE`, Phasen-/Konfigurations-Maps und
Links werden in einer privaten bpffs-Instanz gepinnt. Kernel-Build, BTF,
Programm-/Map-/Link-IDs, Program Tags, Pin-Inodes und erwartete Attach-Targets
werden vor jeder weiteren Phase attestiert. Fehlen `CONFIG_BPF_LSM`,
`CONFIG_SECURITY_NETWORK`, BTF, `BPF_MAP_TYPE_SK_STORAGE`, einer der Hooks oder
die benötigten Helper, scheitert Attach/Pin oder ist `bpf` nicht in der aktiven
LSM-Liste, bleibt Session OPEN fail closed. Eine Userspace- oder
Seccomp-Emulation ist kein Fallback.

`TerminalRuntimeSocketGuardPhaseV3` liegt als exakt ein Element in einer
`BPF_MAP_TYPE_ARRAY` mit `key=u32(0)`, exakt acht Byte großem und acht Byte
ausgerichtetem `u64`-Value. Seine einzigen gültigen Werte sind
`LISTENER_HANDOFF=0`, `LISTENER_RECEIVED=1`,
`HANDOFF_REVOKED_GRANTED=2`, `BOOTSTRAP=3`,
`OPEN_DURABLE_GRANTED=4` und `RELEASED=5`.
Die Map wird mit `map_flags=0` erzeugt; der Kernel initialisiert den einzigen
Array-Value auf null. Der Guard lädt die einzigen beiden schreibenden
BPF-Hookprogramme für `file_receive` und `socket_shutdown`,
friert die Map noch vor jeder Phase-Transition und jedem Runtime-Socket über den dafür erforderlichen
Create-FD per `BPF_MAP_FREEZE` irreversibel für Userspace-Updates ein, schließt
den Create-FD und öffnet ausschließlich einen Lese-FD über
`BPF_OBJ_GET` mit `file_flags=BPF_F_RDONLY`. Ab Rollenstart existiert kein
Userspace-writable Phase-Map-FD. Programme lesen und mutieren ausschließlich
dieses eine Wort. Die sessiongebundene Konfiguration
liegt in einer getrennten vor jeder Transition eingefrorenen Map und bindet
Session-Nonce, Cgroup-ID sowie für Guard, Revocation Attestor und Persistence
Owner jeweils Executable-/Filterhash, TGID/TID/Startzeit und den Socket-Cookie
ihres einzigen Control-Sockets.

Der Guard legt zuerst eine dedizierte Session-Cgroup mit unveränderlicher
Cgroup-ID und Session-Nonce an. Jede nachfolgende Bootstrap-Autorität wird vor
ihrem ersten freigegebenen Syscall in diese Cgroup gebunden; eine spätere
Migration ist verboten.

Der Launcher bindet den bereits gestarteten Guard und erzeugt Revocation
Attestor sowie Persistence Owner zunächst als getrennte single-threaded
Bootstrap-Autoritäten; alle drei hält er an separaten
ererbten Eventfd-Barrieren. Nach erfolgreichem Link-Attach erstellt jede
Autorität aus ihrem exakt vorbefüllten Identitätskontext genau ein eigenes
unverbundenes `AF_UNIX|SOCK_DGRAM|SOCK_CLOEXEC`-Control-Socket. Der
`socket_post_create`-Hook markiert sie disjunkt als `PHASE_CONTROL`,
`HANDOFF_REVOCATION_GRANT_CONTROL` und `OPEN_DURABILITY_GRANT_CONTROL`.
Danach werden ihre Cookies in die Konfigurations-Map übernommen, sämtliche
Nicht-Owner-Kopien geschlossen und extern ausgeschlossen, Phasen- und
Konfigurations-Map eingefroren und die Create-FDs geschlossen. Erst dann darf
eine Transition oder weitere Rollen-/Socket-Erzeugung beginnen. Gemeinsame
Files Tables, spätere Inheritance, `dup*`, `fork`/`clone`, SCM_RIGHTS,
`pidfd_getfd` und `/proc/fd` für diese Sockets sind verboten.

Die Seccomp-Filter erlauben dem Guard ausschließlich `shutdown` auf seinem
festen `PHASE_CONTROL`-FD mit `SHUT_RD` oder `SHUT_RDWR`, dem Attestor
ausschließlich Aufrufe auf seinem festen
`HANDOFF_REVOCATION_GRANT_CONTROL`-FD mit `SHUT_WR` und dem Persistence Owner
ausschließlich Aufrufe auf seinem festen
`OPEN_DURABILITY_GRANT_CONTROL`-FD mit `SHUT_WR`. Jeder abweichende FD-/`how`-
Wert, jede andere Rolle und jeder generische `shutdown`-Pfad endet
kernel-seitig mit `SECCOMP_RET_KILL_PROCESS`. Die LSM-Phase bleibt trotzdem
die exactly-once Autorität; Seccomp allein zählt keine Aufrufe.

Das `socket_shutdown`-Programm führt direkt auf dem Map-Value eine vom Loader
offline und im JIT verifizierte `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` aus. Exakt fünf
Transitionen sind zulässig:

1. Broker-`file_receive`: `LISTENER_HANDOFF→LISTENER_RECEIVED`;
2. Revocation Attestor, Grant-Socket, `SHUT_WR`:
   `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED`;
3. Guard, Phase-Socket, `SHUT_RD`:
   `HANDOFF_REVOKED_GRANTED→BOOTSTRAP`;
4. Persistence Owner, Grant-Socket, `SHUT_WR`:
   `BOOTSTRAP→OPEN_DURABLE_GRANTED`;
5. Guard, Phase-Socket, `SHUT_RDWR`:
   `OPEN_DURABLE_GRANTED→RELEASED`.

Bei erfolgreichem Compare-and-Exchange gibt der jeweilige LSM-Hook
absichtlich `-EINPROGRESS` zurück, sodass der Socket-Protokollpfad nie
ausgeführt wird; die aufrufende Autorität akzeptiert ausschließlich dieses
`errno` plus den unmittelbar gelesenen Zielwert. Ein falscher Altwert,
falscher TID, Socket, Cookie, Session-/Cgroup-Kontext oder `how`-Wert sowie
ein zweiter, vertauschter oder rückwärts gerichteter Versuch liefert
`-EALREADY` beziehungsweise `-EPERM`, mutiert nichts und beendet den Startup
fail closed. Der Guard kann keinen Grant erzeugen; ein Grant-Aussteller kann
keinen Guard-Übergang ausführen. Lookup+Update, Userspace-CAS,
`BPF_MAP_UPDATE_ELEM` und `BPF_F_LOCK` sind ausdrücklich keine Transition.

Ausschließlich in `BOOTSTRAP` erzeugt
`socket_post_create` für ein aus dieser Cgroup kommendes
`AF_UNIX|SOCK_SEQPACKET`-Socket atomar einen
socketlokalen `TerminalRuntimeSocketGuardStateV1`-Eintrag, bevor der erzeugende
Syscall einen FD an Userspace zurückgeben kann. `unix_stream_connect`
überträgt den geschützten Session-Tag auf das serverseitige `newsk`, bevor
`connect`/`accept4` erfolgreich werden kann. Fehlender, doppelter oder nicht
passender Tag sowie Storage-Allokationsfehler liefern `-EPERM`; das Socket
wird nie als Runtime-Endpunkt akzeptiert. Der Tag lebt bis zur Freigabe des
`struct sock` im Kernel und ist weder durch FD-Close/-Dup, SCM_RIGHTS,
`pidfd_getfd`, `/proc/<pid>/fd`, Namespacewechsel noch Prozessende entfernbar.
In `LISTENER_HANDOFF`, `LISTENER_RECEIVED`, `HANDOFF_REVOKED_GRANTED`,
`OPEN_DURABLE_GRANTED` oder `RELEASED` verweigert der Hook jede neue
Session-`AF_UNIX|SOCK_SEQPACKET`-Erzeugung mit `-EPERM`; ab den finalen
Rollenfiltern bleibt sie zusätzlich per Seccomp gesperrt.

Der systemweite `file_receive`-Hook verweigert `receive_fd()` für jeden
geschützten Runtime-Socket mit `-EPERM`. Das umfasst sowohl SCM_RIGHTS-Empfang
als auch `pidfd_getfd`. Die exakt einmalige, nicht-socketartige Listener-
Duplikation aus `TerminalSeccompListenerHandoffV2` ist die einzige disjunkte
`file_receive`-Zulassung: Nur der gebundene Broker-Task darf durch erfolgreiche
BPF-CMPXCHG `LISTENER_HANDOFF→LISTENER_RECEIVED` passieren; zusätzlich
bleiben nach ihrer Revocation `PR_SET_DUMPABLE=0`, leere Capability-Sets,
Ptrace-/Yama-Grenzen und der Ausschluss privilegierter Co-Tenants bindend. Der
systemweite `socket_sendmsg`-Hook verweigert während Phase
`LISTENER_HANDOFF`, `LISTENER_RECEIVED`, `HANDOFF_REVOKED_GRANTED`,
`BOOTSTRAP` **und** `OPEN_DURABLE_GRANTED` **jeden**
`sendmsg`-/`sendmmsg`-Pfad eines
Session-Cgroup-Tasks vor der Protokollübergabe mit `-EPERM`, unabhängig von
FD, Ziel, `msghdr`, Controlbuffer und aufrufendem TID. Dadurch kann vor der
Versiegelung weder ein fachliches Paket noch ein Runtime-Endpoint als
SCM_RIGHTS in einer internen oder fremden Queue abgelegt werden. Diese beiden
Hook-Grenzen gelten bereits vor jeder Rollen-Seccomp-Installation.

`TerminalRuntimeChannelProvisioningV6` erzeugt danach alle Runtime-Kanäle erst,
nachdem Guardian, Broker, Shim und Worker als ihre finalen Rollenprozesse mit
gebundener PID/Startzeit existieren. Für jeden Kanal bindet der endgültige
Empfänger einen eigenen zufälligen, session-/rollen-/richtungsgebundenen
abstrakten AF_UNIX-Namen, ruft `listen` auf, der endgültige Sender verbindet
per nonblocking `SOCK_SEQPACKET`, und ausschließlich der endgültige Empfänger
ruft `accept4(SOCK_NONBLOCK|SOCK_CLOEXEC)` auf. Beide finalen Endpunkte müssen
vor Ready per `getsockopt(SO_PEERCRED)` exakt die erwartete Peer-PID/-UID/-GID
und über `/proc/<pid>/stat` dieselbe gebundene Startzeit nachweisen. Ein
fremder Connect, mehrere akzeptierte Verbindungen, abweichende Credentials,
Startzeit oder Socket-Guard-Tag verhindern Ready. Listener-, Bootstrap- und
abgelehnte Connect-FDs werden danach geschlossen; exakt zwölf finale
Sender-/Empfänger-FDs der sechs gerichteten Verbindungen dürfen verbleiben.

Vor jeder Endpunktkonfiguration wird
`TerminalRuntimeReceiverTaskTopologyV3` vollständig hergestellt. Für
Guardian, Broker, Shim und Worker bindet sie TGID, vollständige sortierte
TID-/Startzeitmenge, Files-Table-Identität und die per TSYNC installierte
`SECCOMP_RET_KILL_PROCESS`-Sperre jeder weiteren Task- oder
Files-Table-Erzeugung. Alle benötigten TIDs existieren vorher. Ein TSYNC-
Fehler, ein nachträglicher TID oder eine nicht inventarisierte lokale Kopie
bricht den Startup ab; eine externe Akquisition wird unabhängig davon bereits
durch den LSM-Guard verweigert.

Nach Aufbau aller Verbindungen muss der jeweilige Owner-TID **jeden der zwölf
verbleibenden finalen Sender- und Empfangsendpunkte** exakt einmal mit
`setsockopt(SOL_SOCKET,SO_PASSRIGHTS,0)` initialisieren und unmittelbar
`getsockopt==0` beweisen; auf den sechs Empfangsendpunkten ist dieser Wert
zusätzlich die fachliche Prequeue-Autorität. Auf jedem geschützten Endpunkt
erlaubt der globale `socket_setsockopt`-Hook genau einen Aufruf: ausschließlich
der vorab gebundene single-threaded Bootstrap-TID des Endpoint-Owners,
ausschließlich im socketlokalen Zustand `INIT`, ausschließlich
`SOL_SOCKET|SO_PASSRIGHTS`. Noch
im LSM-Hook und damit **vor** BPF-Cgroup-Sockopt, User-Optionskopie,
Protokollpfad oder Socket-Lock vollzieht eine atomare Compare-and-Exchange die
irreversible Transition `INIT→SEALED`. Jeder konkurrierende, wiederholte,
fremde oder nachgelagerte `setsockopt` auf diesem Socket liefert systemweit
`-EPERM`, unabhängig davon, welcher Prozess den FD oder nur eine bereits durch
FD-Lookup gehaltene `struct file` besitzt. Der Hook liest den Userwert
absichtlich nicht. Der Owner muss nach Rückkehr sofort
`getsockopt(SO_PASSRIGHTS)==0` beweisen; Fehler, Interrupt, `=1` oder unklarer
Return zerstört den gesamten Startup, weil ein versiegeltes Socket nicht
korrigiert oder retried werden darf. Der single-threaded Setter kann den
Startup nicht zugleich bis zum Snapshot fortführen, solange sein eigener
Optionssyscall vor oder nach dem LSM-Hook blockiert.

Danach installiert jeder Empfänger-TGID zusätzlich
`TerminalRuntimeChannelRightsFreezeFilterV3` mit
`SECCOMP_FILTER_FLAG_TSYNC` auf jeden TID der fixierten Topologie. Er beendet
jeden `setsockopt` mit `SECCOMP_RET_KILL_PROCESS` und bleibt Defense in Depth
innerhalb der Rollen. Anschließend werden sämtliche finalen Rollenfilter
gestapelt. Ab dort sind lokale FD-Erzeugung/-Duplikation, `accept`/`connect`,
FD-Transfer und abweichende Socketziele irreversibel gesperrt. TSYNC-Returns,
TID-Mengen, Filterzahlen und BPF-Hashes werden attestiert.

Erst hinter BPF-LSM-Tag/Seal, Rights-Freeze und finalen Rollenfiltern liest
jeder Empfänger alle Endpunkte erneut und verlangt
`getsockopt(SO_PASSRIGHTS)==0`. `/proc/<receiver>/fdinfo/<fd>` muss exakt
`scm_fds: 0`, die Receive-Queue-Inventur leer und die lokale FD-/FDINFO-/OFD-/
Lock-Inventur frei von Bootstrap-Resten sein. Zusätzlich muss der Guard für
alle zwölf finalen Endpunkte den richtigen, unveränderten `SEALED`-Tag, genau einen
erfolgreichen Init-Hook, null verweigerte Mutation mit Side Effect,
Session-State `BOOTSTRAP` und aktive Link-/Program-/Map-Identitäten belegen.
Ein hostweiter `/proc`-Scan bleibt nur diagnostische Defense in Depth und ist
weder Exklusivitäts-, Quieszenz- noch PASS-Autorität; FD-lose in-flight
Referenzen sind durch den socketlokalen LSM-Hook wirksam gefenct, nicht durch
einen Snapshot angeblich sichtbar gemacht.

Ist irgendein Endpunkt, Tag, Hook, Link, Optionswert, Filterstatus,
`scm_fds`-, Queue-, FD-, OFD- oder Lock-Nachweis abweichend, wird kein OPEN
geschrieben und Session-State bleibt `BOOTSTRAP`. Der weiterhin globale
Send-Hook verhindert jede neue Queue-Referenz. Launcher und Guard terminieren
sämtliche vier Rollen; alle Listener-/Launcher-FDs werden geschlossen. PASS
verlangt danach Socket-/Queue-Zerstörung, null verbleibende SKB-/file-/OFD-/
Lock-Referenz und weiterhin aktive Guard-Links. Derselbe Prozess, dieselbe
Session-Nonce oder dieselben Endpunkte dürfen nicht retried werden. Nur ein
vollständig neuer Startup ist zulässig.

Bei vollständigem PASS schreibt ausschließlich der Persistence Owner
`RUNTIME_SESSION_OPEN` einschließlich Guard-, Grant-, Tag-, Seal-, Filter-,
Endpoint-, Queue- und Session-State-Identitäten durable. Er muss Datei und bei
Erzeugung/Rename das Parent Directory synchronisieren, den Record danach
read-only byte- und hashgleich zurücklesen und Ledger Tip, Authority Commit
Anchor, Session-Nonce, Startup Attempt und Writer-Fencing erneut binden. Nur
aus derselben ununterbrochenen erfolgreichen Commit-Fortsetzung darf sein
gebundener TID auf `OPEN_DURABILITY_GRANT_CONTROL` `SHUT_WR` ausführen. Der
LSM-Hook linearisiert dann genau einmal
`BOOTSTRAP→OPEN_DURABLE_GRANTED`. Dieser Grant öffnet selbst keinen Sendepfad.

Erst nach dem gelesenen Grant-Zielwert plus `-EINPROGRESS` ruft der
single-threaded Guard auf seinem disjunkten `PHASE_CONTROL`-Socket
`SHUT_RDWR` auf. Der Hook linearisiert genau einmal
`OPEN_DURABLE_GRANTED→RELEASED`. Erst der gelesene Zielwert `RELEASED`
zusammen mit diesem exakten Return lässt `socket_sendmsg` auf den sechs
geschützten, durch finale Rollenfilter skalar erlaubten Runtime-Endpunkten
passieren. Ein Guard-Aufruf aus `BOOTSTRAP` scheitert ohne Mutation. Kein
Rollenprozess und auch der Guard besitzt einen Userspace-writable Phase-Map-
FD; niemand besitzt `CAP_BPF`, `CAP_SYS_ADMIN`, `CAP_SYS_RESOURCE`, `bpf`-,
bpffs-, Mount- oder Detach-Autorität. Phase-Map, Konfigurations-Map, Link und
Pins bleiben bis zur nachgewiesenen Endpoint-Zerstörung aktiv. Grant vor
durablem OPEN, Guard-Release vor Grant, zweiter Release-Versuch,
`BPF_MAP_UPDATE_ELEM`, Lookup+Update,
Rückkehr nach `BOOTSTRAP`, Linkverlust oder Map-Mutation außerhalb des
gebundenen Hook-CMPXCHG erzwingt terminalen Fail-stop. Ein OPEN ohne Release
darf keinen fachlichen Send ausführen und wird beim Folgestart als unclosed
Session behandelt.

Die Schutz- und Vertrauensgrenze ist ausdrücklich geteilt. Der BPF-LSM-Guard
erzwingt Phase, exakte Identität, Socketbindung, Einmaligkeit, monotone
CMPXCHG und Gatewirkung. `TerminalHandoffRevocationAttestorV1` ist die einzige
TCB-Autorität für die Richtigkeit der Revocation-/Ein-Halter-Evidence; der
Persistence Owner ist die einzige TCB-Autorität für die erfolgreiche
Durable-OPEN-Commit-Fortsetzung. Der Guard ist ausschließlich Consumer beider
Grants. Der Kernel-Hook behauptet weder, `/proc`-/Halter-Evidence selbst
rekonstruiert zu haben, noch, aus Userspace-Payloads Filesystem-Durability
abzuleiten. Kernel-erzwungen sind die getrennten Ausstelleridentitäten,
unübertragbaren Control-Sockets, exakte Phasen, Einmaligkeit und die
Unmöglichkeit eines Guard-Bypasses ohne fremden Grant. Ein kompromittierter
Kernel, kompromittierter Grant-Aussteller oder privilegierter Co-Tenant liegt
außerhalb des Schutzmodells; ein fehlerhafter Guard liegt innerhalb und kann
ohne Grant weder BOOTSTRAP noch RELEASED erreichen. Executable-/Filterhashes,
single-threaded Topologie, fehlendes Dynamic Loading/`exec`, getrennte Files
Tables und die vollständige Grant-Evidence sind Capability-, OPEN- und
Completion-Pflicht.

Jeder Crash-/Stop-Grenzfall ist total. Ein Fehler vor dem Revocation Grant
lässt `LISTENER_RECEIVED`; ein verlorener Grant-Return oder Crash danach lässt
`HANDOFF_REVOKED_GRANTED`. Beide Zustände verweigern Runtime-Sockets und
Sends. Ein verlorener Guard-Return nach dem Bootstrap-CMPXCHG lässt
`BOOTSTRAP`; ohne konsistente externe Bestätigung wird der Startup bereinigt,
und der Send-Gate bleibt geschlossen. Ein Fehler vor dem Durability Grant
lässt `BOOTSTRAP`; ein verlorener Grant-Return oder Crash danach lässt
`OPEN_DURABLE_GRANTED`. Beide verweigern Sends. Ein verlorener Guard-Return
nach Release lässt den kernelautoritativen Wert `RELEASED`; Rollen dürfen
trotzdem erst nach konsistentem externen Phase-/OPEN-Nachweis in den Loop
eintreten. Jeder unklare Zustand beendet alle Rollen fail closed. Kein Grant
darf zurückgenommen, retried, in eine andere Session übernommen oder ohne
vollständige Prozess-/Endpoint-/Queue-Zerstörung verworfen werden.

`SO_PASSRIGHTS` ist ab Linux 6.16 durch Upstream-Commit
`77cbe1a6d8730a07f99f9263c2d5f2304cf5e830` gebunden. Linux ruft
`security_socket_setsockopt()` nach FD-Auflösung, aber vor dem eigentlichen
Optionspfad und dessen Userkopie/Mutation auf. Genau dieser Hook ist die
globale Linearisation für sichtbare wie nur kernel-in-flight gehaltene
Referenzen. Unterstützt Kernel/UAPI die Option oder die gebundene LSM-/BPF-
Kette nicht exakt, bleibt OPEN fail closed. Ein Fallback auf Receive-
Controlbuffer, `/proc`-Scan, wiederholten Snapshot oder ausschließlich
prozesslokale TSYNC-Filter ist verboten.

Die bereits vor Rights-Freeze geschlossenen Listen-, Bootstrap- und
abgelehnten Connect-FDs dürfen nicht neu entstehen; Runtime-Reconnect,
`accept`, `connect` und FD-Transfer sind nach den finalen Rollenfiltern
verboten. Jeder verbleibende
Endpunkt besitzt eine feste, in OPEN gebundene FD-Nummer, Inode, Richtung und
Peeridentität. `SO_PASSCRED` muss auf jedem Endpunkt exakt `0` sein. Diese
Provisionsreihenfolge ist erforderlich, weil `SO_PEERCRED` die Credentials des
Prozesses zum Zeitpunkt von `connect`/`listen` bindet; ein vor dem Fork
erzeugtes oder nachträglich per `SCM_RIGHTS` übertragenes Socketpair ist kein
zulässiger Ersatz. Es gilt folgende vollständige Kanalautorität:

| Kanal | einziger Sender | einziger Empfänger | zulässige Runtime-Typen |
|---|---|---|---|
| `GB_REQUEST` | Guardian | Broker | `TerminalGuardianRenewalV1`, `TerminalGuardianOrderlyCloseRequestV3` |
| `BG_CLOSE_APPROVAL` | Broker | Guardian | `TerminalBrokerCloseCommitApprovalV2` |
| `BS_RENEWAL_APPROVAL` | Broker | Shim | `TerminalBrokerRenewalApprovalV1` |
| `BS_CLOSE_APPROVAL` | Broker | Shim | `TerminalBrokerCloseCommitApprovalV2` |
| `BW_REQUEST` | Broker | Worker | `TerminalWorkerKillRequestV2`, `TerminalWorkerClosePrepareRequestV2`, `TerminalWorkerCloseCommitRequestV2` |
| `WB_ACK` | Worker | Broker | `TerminalWorkerClosePrepareAckV2`, `TerminalWorkerCloseCommitAckV2` |

Die Rollenfilter erlauben ausschließlich: Guardian `sendmsg(GB_REQUEST)` und
`recvmsg(BG_CLOSE_APPROVAL)`; Broker `recvmsg(GB_REQUEST|WB_ACK)`,
`sendmsg(BG_CLOSE_APPROVAL|BS_RENEWAL_APPROVAL|BS_CLOSE_APPROVAL|BW_REQUEST)`
und `SECCOMP_IOCTL_NOTIF_RECV|ID_VALID` am einzigen Trip-Listener; Worker
`recvmsg(BW_REQUEST)` und `sendmsg(WB_ACK)`; Shim
`recvmsg(BS_RENEWAL_APPROVAL|BS_CLOSE_APPROVAL)`. Für `sendmsg` sind skalar nur
der feste FD und `MSG_DONTWAIT|MSG_NOSIGNAL`, für `recvmsg` nur der feste FD
und `MSG_DONTWAIT` erlaubt. `MSG_CMSG_CLOEXEC` ist nicht nötig und unzulässig,
weil kein Controlbuffer existiert. Falsche Richtung, anderer FD,
`sendmmsg`/`recvmmsg`, Runtime-`accept`/`connect`, Listener-Weitergabe,
CONTINUE und ADDFD enden default-deny; Trip-/Writer-Referenzverstöße verwenden
`SECCOMP_RET_KILL_PROCESS`. Klassisches Seccomp behauptet ausdrücklich nicht,
einen im `msghdr` versteckten `SCM_RIGHTS`-CMSG senderseitig erkennen zu
können.

Die Kernel-Barriere ist die primäre Ancillary-Autorität. Bei einem im
Userspace-`msghdr` verborgenen `SCM_RIGHTS`-CMSG prüft AF_UNIX den
`SO_PASSRIGHTS=0`-Zustand des Peer-Empfangssockets, gibt dem Sender
deterministisch `EPERM` zurück und verwirft das zugehörige SKB, bevor es in die
Receive Queue gelangt. Die Kernel-Implementierung darf während des Syscalls
kurzzeitig file-Referenzen aufnehmen; vor dem `sendmsg`-Return müssen diese
vollständig freigegeben sein. Auch ein unmittelbar vor jedem `recvmsg`
gestoppter, abgestürzter oder dauerhaft stallender Empfänger hält daher nach
Sender-Close/-Crash keine übertragene file-, Open-File-Description- oder
Lock-Referenz. Ein erfolgreicher Runtime-Send mit Rights, ein queued
`scm_fds>0` oder ein anderer Return als das gebundene `EPERM` ist ein
Capability-Konflikt und verhindert OPEN beziehungsweise führt post-OPEN
terminal fail closed.

Der Broker wartet ausschließlich mit `epoll_wait` am in OPEN gebundenen epoll-
FD, der vor Ready genau Trip-Listener, Liveness-Read-Ende, `GB_REQUEST` und
`WB_ACK` registriert. Seccomp bindet epoll-FD, vorallokierte Eventbuffer-Adresse,
`maxevents` und Timeout als skalare Argumente; `epoll_ctl`, `poll` und jede
pointervariable FD-Liste sind nach Ready verboten. Der Broker priorisiert pro
Batch Trip-Listener und Liveness-HUP zuerst, gültige Renewals danach und
Close-Requests/-ACKs zuletzt.

Klassisches Seccomp dereferenziert weder `msghdr` noch `iovec` und behauptet
daher ausdrücklich **keine** Payload-, Längen-, Type- oder Ancillary-Prüfung.
Zusätzlich zur vorgelagerten `SO_PASSRIGHTS=0`-Barriere ruft jeder gebundene
native Empfänger `recvmsg` mit exakt
`msg_control=NULL` und `msg_controllen=0` auf. Nach Linux-`unix(7)` schließt
der Kernel deshalb jeden wegen fehlenden Controlbuffer nicht übergebbaren
`SCM_RIGHTS`-FD automatisch; kein userspace-sichtbarer neuer FD und keine
Open-File-Description-Referenz des Empfängers darf den Syscall-Return
überleben. Dieser Pfad ist ausschließlich Defense in Depth für eine bereits
als Capability-Verlust zu behandelnde Abweichung; regulär erreicht kein
Rights-Paket `recvmsg`. `MSG_CTRUNC` bleibt ein terminaler Protokollfehler,
kein Cleanup-Auftrag. Der externe FD-/FDINFO-/Lock-Observer muss vor Send,
nach dem gebundenen `EPERM` und nach jedem Receive dieselbe Inventur sowie
`scm_fds: 0` beweisen; ein eigener Runtime-`close`-Pfad für empfangene FDs
existiert nicht.

Jeder Empfänger validiert nach dieser abgeschlossenen Kernel-Disposition und
vor jeder fachlichen Mutation den `recvmsg`-Returnwert als exakt die gebundene
Struct-Länge, genau eine Paketgrenze, keine
`MSG_TRUNC|MSG_CTRUNC|MSG_OOB`, den bereits in OPEN gebundenen
`SO_PEERCRED`-Peer, **keine** Ancillary-Daten sowie Type-Konstante,
Schema-Version, Session-ID, Close-Nonce, Phase, Broker-/Guardian-Generation,
Control-Word-State/-Sequenz, Reconciliation-/Journal-Head und die jeweils
vorherigen PREPARE-/COMMIT-Fingerprints. Jede Close-Struktur bindet zusätzlich
ihre unveränderliche absolute `CLOCK_BOOTTIME`-Phasendeadline und den kanonischen
Payload-Digest. Die sechs Close-Typen sind disjunkt;
`TerminalBrokerCloseCommitApprovalV2` wird mit identischen autoritativen Bytes
an beide Approval-Empfänger gesendet. Ein KILL-Typ kann niemals als Close-Typ
und ein ACK niemals als Request akzeptiert werden.

Die Broker-Close-FSM ist vollständig und endlich:

| Zustand | globale State-Stufe | erwartetes Ereignis | Erfolg | Deadline-/Fehlerfolge |
|---|---|---|---|---|
| `IDLE` | RUNNING | Guardian CloseRequest | CAS nach CLOSING | Request-Timeout beim Guardian: Renewals stoppen, harte Termination; kein PREPARE |
| `PREPARE_SEND` | CLOSING | PrepareRequest zustellen | `PREPARE_ACK_WAIT` | 100 ms, dann CAS nach TERMINATING |
| `PREPARE_ACK_WAIT` | CLOSING | gültiger PrepareAck | CAS nach CLOSED | 100 ms, dann CAS nach TERMINATING; PREPARE bleibt unclean |
| `COMMIT_SEND` | CLOSED | CommitRequest zustellen | `COMMIT_ACK_WAIT` | 20 ms, dann CAS nach CLOSED_FAILSTOP |
| `COMMIT_ACK_WAIT` | CLOSED | gültiger CommitAck | CAS nach COMMITTED | 20 ms, dann CAS nach CLOSED_FAILSTOP |
| `APPROVAL_FANOUT` | COMMITTED | beide Approval-Sends | `COMPLETE` | je 20 ms; danach polling-basierte COMMITTED-Konvergenz, kein Rollback |
| `COMPLETE` | COMMITTED | Child-Exit/HUP | Sessionende | HUP ist erwartete Evidenz |
| `FAILED_PRE_CLOSED` | TERMINATING | keine Close-Fortsetzung | Lease-Expiry/Kill | Startup unclean, auch mit PREPARE |
| `FAILED_POST_CLOSED` | CLOSED_FAILSTOP | keine Approval | Lease-Expiry/Kill | Startup entscheidet ausschließlich nach durablem COMMIT |

Jede Deadline ist eine bei Phaseneintritt aus `CLOCK_BOOTTIME` berechnete
absolute Frist; ein Retry setzt sie niemals zurück. Während CLOSING verarbeitet
der Broker Trip-Notification/HUP zuerst, dann Renewals, dann Close-I/O. Dadurch
bleibt die Lease während des endlichen PREPARE-Pfads armed, aber alle Trading-
Gates sind bereits geschlossen. Ab CLOSED existiert keine Renewal mehr.

Für jeden der sechs Nachrichtentypen gilt dieselbe totale Transportregel:

1. `sendmsg==sizeof(struct)` bedeutet möglicherweise zugestellt und wechselt
   Request/ACK in den Wait-Zustand; fehlende Antwort darf denselben Sender bis
   zur absoluten Deadline zu einem byteidentischen Retry veranlassen.
2. `EINTR` und `EAGAIN|EWOULDBLOCK` bedeuten unbekannt/nicht zugestellt und
   führen nur zu einem Retry derselben Session, Nonce, Phase und Bytes. Ein
   neuer Event, eine neue Nonce oder ein Deadline-Reset ist verboten.
3. `0`, positiver Short-Send, `EPERM`, `EMSGSIZE`, `EPIPE`, `ECONNRESET`, anderer
   Fehler, `POLLHUP|POLLERR` oder Deadline-Ablauf führen vor COMMITTED sofort
   in den zur globalen State-Stufe gehörenden FAILED-Zustand.
   `EPERM` wird niemals retried: Bei einem Fault-Injection-Rights-Paket ist es
   der erwartete Nachweis der Kernel-Barriere, bei einer fachlichen Nachricht
   ein terminaler Capability-/Protokollkonflikt.
   SOCK_SEQPACKET-Short-Send gilt als Kernel-/Capability-Konflikt, nicht als
   fortsetzbarer Rest-Write. In APPROVAL_FANOUT bleibt COMMITTED irreversibel;
   der Delivery-Fehler wird gebunden protokolliert und die Empfänger
   konvergieren nur über ihren Control-Word-Poll oder die OS-Fail-stop-Folge.
4. Receive-`EINTR` setzt denselben Wait fort; `EAGAIN|EWOULDBLOCK` wartet nur
   bis zur bestehenden Deadline. Short/oversize/truncated, falscher Typ, Peer,
   State, Nonce, Session, Phase, Fingerprint oder Ancillary-Inhalt ist ein
   terminaler Protokollfehler und wird nie als fremde Nachricht übersprungen.
5. Ein byteidentisches Request-Duplikat lässt der Worker höchstens denselben
   bereits durablen PREPARE/COMMIT finden oder einmal schreiben und sendet
   dieselbe ACK erneut. Ein byteidentisches ACK-Duplikat nach akzeptierter Phase
   wird ignoriert; ein konfliktäres Duplikat eskaliert. Broker, Worker,
   Guardian und Shim speichern pro Session/Nonce die letzte akzeptierte Phase.
6. Für Request und beide Worker-ACKs gilt damit at-least-once Transport plus
   idempotente exactly-once Mutation; ein behauptetes exactly-once Send gibt es
   nicht. Für die beiden finalen Approvals ist genau-einmalige Zustellung ohne
   weitere ACK-Runde ausdrücklich nicht behauptet: byteidentische Retries sind
   idempotent, und das polling-sichtbare COMMITTED-Control-Word ist die
   verlustfreie Autorität.
7. Broker-/Worker-/Guardian-/Shim-Crash, Peer-Close und Queue-full sind keine
   Wartezustände ohne Ende. Vor CLOSED entsteht TERMINATING und PREPARE bleibt
   unclean. Nach CLOSED entsteht CLOSED_FAILSTOP, keine Approval wird wirksam
   und der Timer läuft aus. Ist COMMIT bereits durable, klassifiziert ein
   Folgestart ausschließlich PREPARE→Broker-CLOSED→COMMIT als clean, auch wenn
   CommitAck oder Approval verloren ging; ohne COMMIT bleibt er unclean. Nach
   COMMITTED kann kein Transportfehler den cleanen Record oder die Gate-Sperre
   zurücknehmen.

Kann der Broker den Fehler selbst verarbeiten, führt er die genannte CAS nach
TERMINATING beziehungsweise CLOSED_FAILSTOP aus. Stirbt oder stoppt der Broker
vor der CAS, bleibt der zuletzt sichtbare State RUNNING, CLOSING oder CLOSED
unverändert; dies ist keine Fortsetzungserlaubnis: Es entstehen keine weiteren
Approvals, der Shim akzeptiert nach Ablauf keine stale Lease und der armed
Timer erzeugt das harte Signal. Worker-HUP wird vom lebenden Broker wie der
entsprechende Phasenfehler behandelt. Guardian-Tod stoppt Requests und
Renewals; Shim-Tod stoppt Timerverlängerungen. Diese Crash-Folgen verwenden
keinen Restart desselben Protokolls und keine neue Nonce.

#### 7.8.2 Terminal Lease Capability Envelope V14

`TerminalLeaseCapabilityProfileV14` ist ein hashgebundener, endlicher
Ausführbarkeitsvertrag, kein allgemeiner Echtzeitbeweis. Er bindet mindestens:

- Kernel-/WSL-Build, Architektur, Boot-Konfiguration, Page Size,
  `CLOCK_BOOTTIME`-Auflösung und POSIX-Timer-/Signal-Capabilities sowie Linux
  mindestens 6.16, UAPI-Wert/Quellidentität von `SO_PASSRIGHTS` und Upstream-
  Commit `77cbe1a6d8730a07f99f9263c2d5f2304cf5e830`;
- aktive LSM-Liste mit `bpf`, `CONFIG_BPF_LSM`, `CONFIG_SECURITY_NETWORK`,
  BTF-/`vmlinux`-Identität, BPF-LSM-/SK-STORAGE-Helpermatrix, exakte
  `socket_post_create`-, `unix_stream_connect`-, `socket_setsockopt`-,
  `socket_sendmsg`-, `socket_shutdown`- und `file_receive`-Attach-Targets sowie
  `security_socket_shutdown` vor dem Socket-Protokollpfad, Program-/Map-/Link-
  IDs, Program Tags, Pin-Pfade/-Inodes und private bpffs-Mountidentität von
  `TerminalRuntimeSocketLSMGuardV3`;
- Guardian-, Revocation-Attestor-, Persistence-Owner-, Native-Trip-Broker-,
  Native-Shim-, Compiler-/Linker-,
  libc-/libatomic- und Seccomp-Artefakthashes;
- nachgewiesenes lock-free `_Atomic uint64_t`, Alignment, Endianness,
  exakt `MFD_CLOEXEC|MFD_ALLOW_SEALING`, initialen Seal-State 0, beide
  `F_ADD_SEALS`-Transitionen, finalen Seal-State, vollständige prozessbezogene
  Mapping-Rechte, alle sechs in Abschnitt 7.8.1 getrennten verbundenen
  Runtime-Kanäle samt finaler Connect-/Accept-Provenance, abstrakten Bootstrap-
  Adressen, `SO_PEERCRED`, `SO_PASSCRED=0`, fehlendem Receive-Controlbuffer,
  am Listener und autoritativ an jedem akzeptierten finalen Empfangsendpunkt
  gesetztem und zurückgelesenem `SO_PASSRIGHTS=0`, verbotenem Vererbungs-
  Vertrauen, `TerminalRuntimeReceiverTaskTopologyV3` mit festem TGID/TID-/
  Files-Table-/Endpunktinventar und irreversibler Taskbildungssperre,
  `TerminalRuntimeSocketLSMGuardV3` mit vor FD-Sichtbarkeit erzeugtem
  socketlokalem Session-Tag, exakt einer atomaren `INIT→SEALED`-Transition,
  globalem post-Seal-`setsockopt=-EPERM`, `file_receive=-EPERM`, dauerhaftem
  Send-Gate in `LISTENER_HANDOFF|LISTENER_RECEIVED|HANDOFF_REVOKED_GRANTED|BOOTSTRAP|OPEN_DURABLE_GRANTED`, mit
  `map_flags=0` erzeugter,
  kernel-nullinitialisierter und vor jeder Transition/Runtime-Socket-Erzeugung
  per Create-FD eingefrorener
  `BPF_MAP_TYPE_ARRAY`-Phasen-Map, danach geschlossenem Create-FD und nur per
  `BPF_OBJ_GET|BPF_F_RDONLY` geöffnetem Lese-FD, exakt verifiziertem
  `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`, einmaligem
  `LISTENER_HANDOFF→LISTENER_RECEIVED` im exakten `file_receive`, einmaligem
  `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED` durch den disjunkten
  `TerminalHandoffRevocationAttestorV1`, anschließendem
  `HANDOFF_REVOKED_GRANTED→BOOTSTRAP` ausschließlich durch den Guard,
  einmaligem `BOOTSTRAP→OPEN_DURABLE_GRANTED` ausschließlich durch den
  Persistence Owner nach durablem OPEN und anschließendem
  `OPEN_DURABLE_GRANTED→RELEASED` ausschließlich durch den Guard; außerdem
  drei nicht transferierbaren, disjunkt getaggten Control-Sockets mit exakt
  gebundenen Owner-TGID/TID/Startzeiten, Cookies, Cgroup und `how`,
  `TerminalRuntimeChannelRightsFreezeFilterV3` mit erfolgreichem TSYNC auf
  jedem Empfänger-TID, BPF-Hash und `SECCOMP_RET_KILL_PROCESS` für jeden
  `setsockopt`, danach vollständiger finaler Rollenfilterabdeckung und
  **danach** erneutem
  `getsockopt==0`, `scm_fds: 0`, leerer
  Queue und unveränderter FD-/FDINFO-/OFD-/Lock-Inventur, verbotener
  Senderfreigabe vor durablem OPEN und LSM-Release sowie totaler Socket-/Queue-
  Zerstörung bei jedem Residuum; ein hostweiter `/proc`-Scan bleibt
  nichtautoritative Diagnose,
  Trip-Liveness-Pipe-, Seccomp-Listener-, Broker-epoll- und Eventfd-Inodes samt
  fester `tfd`-Registrierung;
- Trading-Self-, Guardian- und Broker-PIDFD jeweils mit Ziel, Startzeit,
  Signal-0-Probe und exakt erlaubtem
  `pidfd_send_signal(...,SIGKILL,NULL,0)`, außerdem exklusiver Liveness-Pipe-
  Enden-Besitz, dauerhaft leerer Kanal und rohe Linux-`close`-Semantik;
- `TerminalTradingSignalEnvelopeV1` mit genau einem TID bei Herstellung,
  vollständiger blockierbarer Signalmaske, handlerfreier Dispositionstabelle,
  Vererbung an jede spätere TID, exakter Sperre aller post-Ready Signalzustands-
  und Signal-Erzeugungssyscalls sowie nachgewiesenem Kernel-Support für
  `SECCOMP_FILTER_FLAG_WAIT_KILLABLE_RECV`;
- `TerminalSeccompListenerHandoffV2` mit Yama `ptrace_scope=1`, exakt einem
  gebundenen `PR_SET_PTRACER(broker_pid)`, fixem Quell-/Ziel-FD, genau einem
  `pidfd_getfd(...,0)`, atomarem `LISTENER_HANDOFF→LISTENER_RECEIVED` vor
  FD-Installation, ACK über den geerbten Eventfd, genau einem Broker-
  Listener-Halter und der vor jeder Runtime-Socket-Erzeugung abgeschlossenen
  `PR_SET_PTRACER=0`-/`PR_SET_DUMPABLE=0`-/Capability-/Seccomp-Revocation;
- `TerminalTradingTaskTopologyV2` mit vollständiger TGID/TID-/Startzeit-/Rollen-
  Menge, gemeinsamem `KCMP_FILES`-Nachweis, Session-Cgroup-/PID-Namespace-
  Fingerprint, TSYNC-Basisfilter und allen gestapelten Rollenfilterhashes;
- `TerminalRuntimeReceiverTaskTopologyV3` für Guardian, Broker, Shim und Worker
  mit vollständigen TID-/Files-Table-/Endpunktmengen, eingefrorener
  Tasktopologie und dem Nachweis, dass der Rights-Freeze-Filter jede relevante
  TID vor dem letzten Options-/Queue-Snapshot erreicht;
- exakte Kernel-Ablehnung aller Post-Ready-Taskbildungs-Syscalls sowie jeder
  FD-Erzeugungs-, FD-Duplikations-, `/proc/self/fd`-Reopen-, Trading-/Writer-
  `SCM_RIGHTS`-, io_uring- und writerbezogenen epoll-Referenzbildung aus
  Abschnitt 7.8; für die erlaubten Rollenkanäle ersetzt der totale
  `SO_PASSRIGHTS=0`-Prequeue-Reject-Nachweis aus Abschnitt 7.8.1 eine
  unzutreffende senderseitige Seccomp-Payloadbehauptung; NULL/0-Controlbuffer-
  Autoclose bleibt ausschließlich Defense in Depth;
- die vollständige kernelversionsgebundene Default-deny-Syscallmatrix, in der
  der Liveness-Writer ausschließlich beim einmaligen `close` als skalares
  FD-Argument vorkommt und jede Schreib-/Transferoperation
  `SECCOMP_RET_KILL_PROCESS` auslöst;
- `TerminalSelfKillEntryV4` mit nachgewiesener Reihenfolge
  Self-PIDFD-`SIGKILL` → Guardian-PIDFD-`SIGKILL` → Broker-PIDFD-`SIGKILL` →
  atomarer Liveness-FD-Entzug und einmaliger Close, ohne Pipe-Read oder -Write;
- `TerminalKernelTripRequestV2` mit vor jeder weiteren TID-Erzeugung
  installiertem NEW_LISTENER-/WAIT_KILLABLE_RECV-Filterhash, nachgewiesener Vererbung an alle
  Trading-TIDs, anschließendem separatem TSYNC-Basisfilter, einzigem
  Broker-Listener, exaktem Self-PIDFD-/SIGKILL-/Null-/0-Tupel, verbotenem
  CONTINUE/ADDFD, Notification-ID-Validierung, terminaler Klassifikation jedes
  Listener-Ready-/Receive-Fehlers und dem Nachweis, dass kein anderer Prozess
  oder TID Listener- oder Trip-Reset-Autorität besitzt;
- `RuntimeSessionCloseProtocolV8` mit vollständigen PREPARE-/COMMIT-Schemas,
  exklusivem Lifecycle-Append-Handle, allen sechs fixed-size Request-/Ack-/
  Approval-Strukturen und Peerbindungen, Broker-CLOSED-Evidenz zwischen beiden
  Records und der Sperre von Timer-Disarm und Child-Exit vor durablem CLOSE-
  COMMIT, der vollständigen Kanal-/Seccomp-/Userspace-Matrix, allen absoluten
  Deadlines und der endlichen Fehlerzustandsmaschine aus Abschnitt 7.8.1;
- die vollständige Sperre jeder post-Ready Mapping-, Remapping-, Protection-,
  Reclamation-, Migration-, Unlock- oder userfaultfd-/`UFFDIO_*`-Operation,
  die gebundene NUMA-Policy, deaktivierte automatische NUMA-Migration,
  ausgeschlossenen Memory-Hotplug sowie die exakte Native-/x32-ABI-Grenze;
- Broker- und Trading-`PR_SET_DUMPABLE=0`, leere Capability-Sets,
  `no_new_privs`, effektive Ptrace-/Yama-Policy und Ausschluss privilegierter
  Co-Tenants;
- feste CPU-Affinity für Guardian/Broker/Shim, Scheduling-Class/-Priority,
  `mlockall`-Status und Cgroup-Limits für CPU, Memory, PIDs und File
  Descriptors; CPU-Hotplug oder Abweichung dieser Werte ist außerhalb des
  Envelopes;
- die unveränderlichen Budgets `heartbeat_interval_ms=10`,
  `lease_expiry_ms=25`, `broker_trip_cas_max_ms=5`,
  `guardian_trip_dispatch_max_ms=5`,
  `kernel_signal_generation_budget_ms=25` und `failstop_max_ms=100`;
- IDs/Fingerprints von Lastgenerator, Fault Fixture, Kernel-Signal-Observer,
  Side-Effect-Sentinel und vollständigem Testmanifest.

Die vollständige Capability-Zertifizierung verwendet je Szenario exakt
`10_000` deterministische Trials. Die Trip-Zeitpunkte decken den 10-ms-
Heartbeat-Zyklus in aufsteigenden Mikrosekunden-Offsets vollständig ab. Das
Manifest führt mindestens aus: Guardian-`SIGKILL`, Guardian-`SIGSTOP`,
Guardian-Capability-Verlust, Broker-Stall/-Tod, Shim-Stall, gesamtes Child-
`SIGSTOP`, Trip bei blockiertem Persistence Worker, verlorenen Broker→Worker-
Request, fremden Worker-Peer, writable-Map-Tamper, fehlendes
`MFD_ALLOW_SEALING`, initiales `F_SEAL_SEAL`, abweichende
`F_ADD_SEALS`-Transitionen, erfolgreiche Self-PIDFD-Signalanforderung,
Self-PIDFD-Fehler mit erfolgreicher Guardian-Signalanforderung, Self- und
Guardian-PIDFD-Fehler mit erfolgreicher Broker-Signalanforderung, Fehler aller
drei PIDFD-Signale mit Liveness-Close/HUP, Close-`EINTR` ohne Retry, jeden
verbotenen Pipe-Write/-Transfer, jede verbotene Post-OPEN-Task-/FD-
Referenzbildung, Halt nur des Request-TID nach kernel-erzeugter Seccomp-
Notification und vor Broker-Receive bei gesundem Guardian/Broker/Shim, jedes
blockierbare Signal vor und nach Broker-Receive, `SA_RESTART`-/Handler-
Installations- und Signal-Unmask-Versuche, Listener-Ready mit `NOTIF_RECV`-
`ENOENT|EINTR|EAGAIN` sowie unbekanntem Fehler,
Whole-child-Stop sowohl vor als auch nach Notification-Erzeugung, Liveness-HUP
in RUNNING/CLOSING, Liveness-HUP erst nach COMMITTED plus CLOSE-COMMIT,
Crash/Trip nach CLOSE-PREPARE aber vor Broker-CLOSED, CLOSE-COMMIT-Writefehler
nach Broker-CLOSED, für jeden der sechs Close-Typen getrennt `EINTR`, `EAGAIN`,
Short/invalid, Peer-HUP, Timeout, Duplicate und verlorene Zustellung, fremde
  Yama-Modi ungleich `ptrace_scope=1`, falsche Real-Credentials, fehlendes/
  doppeltes/abweichendes `PR_SET_PTRACER`, falsche reservierte Quell-/Ziel-FDs,
  `pidfd_getfd` mit falschem PIDFD/Quell-FD/Flags, zweitem Aufruf oder
  unerwartetem Return-FD, fehlendes/falsches Eventfd-ACK, Trading-Quell-FD-
  Closefehler, fehlgeschlagene Ptrace-/Dumpable-Revocation, mehr als einen
  Listener-Halter und jeden Runtime-Socket-Erzeugungsversuch in
  `LISTENER_HANDOFF`; ferner fremde Connects, fehlendem/falschem Socket-Tag,
  BPF-Link-/Program-/Map-/Pin-Verlust,
  abweichender Cgroup-/Bootstrap-TID-Bindung, fehlgeschlagener oder doppelter
  `INIT→SEALED`-Transition, `setsockopt(SO_PASSRIGHTS=1)` des erlaubten Setters,
  fremdem und nur kernel-in-flight gehaltenem `setsockopt` vor und nach Seal,
  falschem Control-Socket/-Cookie/-Guard-TID/-`shutdown`-`how`, fehlendem oder
  abweichendem `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG`, Userspace-Map-Update,
  Lookup+Update, fehlendem/doppeltem
  `LISTENER_HANDOFF→LISTENER_RECEIVED`,
  richtigem Guard-`SHUT_RD` vor `HANDOFF_REVOKED_GRANTED`, richtigem Guard-
  `SHUT_RDWR` vor `OPEN_DURABLE_GRANTED`, Revocation Grant vor vollständiger
  Handoff-Revocation, Durability Grant vor durablem OPEN, vertauschten Guard-/
  Grant-Sockets oder Aussteller-TIDs, doppeltem/rückwärts gerichtetem Grant
  oder Release sowie
  `sendmsg`/`sendmmsg` vor Release; außerdem abweichende/fehlende
  `SO_PASSRIGHTS`-Set/Get-Ergebnisse, erneutes `SO_PASSRIGHTS=1` und Rights-Sends
  vor, während und nach jeder Rights-Freeze-TSYNC-Grenze,
  vor/während/nach finaler Rollenfilterabdeckung und nach durablem OPEN vor
  Release, partiellen/fehlgeschlagenen TSYNC, TID-Race, versteckter Socket-
  Inode-Kopie in derselben oder einer fremden Session-Files-Table,
  veraltetem Snapshot, Queue-Residuum mit vollständigem Bootstrap-Abbruch sowie
  `SCM_RIGHTS` mit einem bis `SCM_MAX_FD` FDs, mehreren
CMSGs, vor `recvmsg` gestopptem/abgestürztem Empfänger, Sender-Close/-Crash
und absentem Controlbuffer sowie
Trip/Renewal- und Orderly-Close/Renewal-CAS in beiden Linearization-
Reihenfolgen.
Während jedes Trials laufen alle nicht reservierten CPUs bei 100 %
synthetischer Last; das reservierte Guardian-/Broker-/Shim-CPU-Set enthält
keine fremden runnable Tasks. Memory steht bei
90 % des gebundenen Cgroup-Limits mit mindestens 64 MiB vorreservierter
Terminal-Reserve, File Descriptors stehen bei Limit minus 16 und der Worker-
I/O-Blocker ist aktiv. Abweichende oder nicht messbare Last ist kein PASS.

PASS ist ausschließlich dann berechenbar, wenn in **jedem** Trial:

1. keine Broker-Renewal-CAS oder Shim-Timerverlängerung nach einer erfolgreichen
   Trip-CAS, CLOSED/CLOSED_FAILSTOP oder nach akzeptiertem Broker-PIDFD-
   `SIGKILL` committed;
2. bei gesundem Broker Liveness-HUP/POLLERR/POLLIN innerhalb `5 ms` per
   Trip-CAS linearisiert wird und der gesunde Guardian nach dieser
   CAS/Notification innerhalb weiterer `5 ms` den PIDFD-Kill anfordert;
3. `TerminalSelfKillEntryV4` vor jeder Pipe-Operation zuerst Self-PIDFD-
   `SIGKILL` anfordert und bei jedem zurückkehrenden Fehler ohne Retry exakt in
   der gebundenen Reihenfolge Guardian-PIDFD, Broker-PIDFD und zuletzt den
   einmaligen Liveness-Close ausführt. Spätestens eine akzeptierte
   kernel-seitige Fatal-Action oder bei vollständigem PIDFD-Fehler HUP muss
   innerhalb des gebundenen `5-ms`-Dispatchbudgets vorliegen;
4. bei Halt/Deschedule ausschließlich des Request-TID unmittelbar nach
   kernel-erzeugter `TerminalKernelTripRequestV2`-Notification der externe
   Broker die Notification ohne TID-Fortschritt validiert, nach TERMINATING
   linearisiert, selbst den Child-PIDFD-Kill anfordert und keine folgende
   Approval mehr erzeugt; bei Broker-Ausfall muss die letzte armed Expiry das
   Kernel-Signal erzeugen. Vor Receive muss jedes blockierbare Signal pending
   bleiben, nach Receive muss WAIT_KILLABLE_RECV jeden nichtfatalen Abbruch
   verhindern; `SIGKILL` terminiert und `SIGSTOP` lässt ohne Shim-Fortschritt
   die Lease auslaufen. Jeder Listener-Ready-/Receive-Fehler muss ohne
   Request-TID-Fortschritt dieselbe terminale CAS auslösen;
5. CLOSE-PREPARE allein bei Crash, Trip oder CLOSE-COMMIT-Writefehler niemals
   als clean gilt; nur PREPARE → Broker-CLOSED → durable COMMIT ist beim
   Startup clean, und nur ein validierter COMMIT-ACK mit COMMITTED erlaubt
   Timer-Disarm und Child-Exit. Jeder Abbruch vor durablem COMMIT muss beim
   nächsten Startup `TERMINAL_UNKNOWN`/Terminal-Gap-Recovery erzwingen;
6. kein Post-OPEN-Versuch einen Prozess, Thread, eine abweichende Files-Table,
   einen neuen FD oder eine zweite Kernel-Referenz auf den Writer erzeugt;
   jeder Versuch muss am exakt gebundenen Kernel-Filter mit
   `SECCOMP_RET_KILL_PROCESS` enden. Der
   externe Observer muss belegen, dass kein neuer Task/Writer entstand, der
   gesamte Probe-TGID beendet wurde und der Broker den letzten Writer als
   HUP vor jeder weiteren Approval erkannte;
7. jeder Write, Read oder Datentransfer auf einem Ende der Liveness-Pipe vor
   FD-Auflösung mit `SECCOMP_RET_KILL_PROCESS` endet; der externe Observer muss
   null Pipe-Bytes, null Pipe-Pages und null temporäre Write-Referenzen belegen;
8. bei gleichzeitigem `terminal_trip()`, Fehler aller drei PIDFD-Signale und
   maximaler gebundener Broker-Poll-/Pipe-Lock-Konkurrenz der einzige
   Liveness-Writer entzogen wird. Ein gesunder Broker muss HUP innerhalb `5 ms`
   vor weiterer Approval linearisiert haben; ein gestoppter oder toter Broker
   darf keine weitere Approval erzeugen;
9. bei verlorener Notification oder Guardian-/Broker-/Shim-Stall das Kernel-Signal
   spätestens `25 ms` nach Lease-Expiry, damit spätestens `50 ms` nach letzter
   gültiger Renewal, erzeugt wird;
10. `TERMINAL_FAILSTOP_ASSERTED` spätestens `100 ms` nach Trip beziehungsweise
   erkanntem Capability-Verlust gilt;
11. der Request-TID ab Kernelannahme im Seccomp-Wait blockiert, ab Trip-CAS kein
   Side-Effect-Sentinel fortschreitet und weder eine Transition von
   TERMINATING nach RUNNING, CLOSING oder CLOSED noch
   `CLOSED_FAILSTOP→COMMITTED` erreichbar ist;
12. alle Kernel-Zeitpunkte vom gebundenen externen Observer vollständig
   vorliegen. Percentile, Mittelwerte, Retry eines fehlgeschlagenen Trials oder
   fehlende Messpunkte sind unzulässig;
13. der globale `TerminalRuntimeSocketLSMGuardV3` vor jeder Phase-Transition
   und Runtime-Socket-Erzeugung
   angehängt und bis zur Endpoint-Zerstörung unverändert aktiv bleibt. Während
   `LISTENER_HANDOFF` darf kein Runtime-Socket entstehen; genau ein
   `TerminalSeccompListenerHandoffV2` muss mit festem Quell-/Ziel-FD, genau
   einem `pidfd_getfd`, genau einem kernelinternen
   `LISTENER_HANDOFF→LISTENER_RECEIVED`, Eventfd-ACK, Trading-FD-Close,
   Ptrace-/Dumpable-Revocation, genau einem durch
   `TerminalHandoffRevocationAttestorV1` ausgestellten
   `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED` und danach genau einem Guard-
   `HANDOFF_REVOKED_GRANTED→BOOTSTRAP` enden. Der Session-Send-Gate darf dabei
   keine Ausnahme besitzen. Ein richtiger Guard-Aufruf vor dem Attestor-Grant
   muss ohne Phase-Mutation und Runtime-Socket-Wirkung scheitern. Die
   eingefrorene Phasen-Map darf ausschließlich durch
   die gebundenen `file_receive`- und `socket_shutdown`-Hooks mittels
   verifiziertem `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` mutieren; jeder Userspace-
   Updatepfad muss scheitern. Danach muss jeder der sechs Runtime-Kanäle aus
   finalem Rollen-`connect`/`accept` stammen, beide
   `SO_PEERCRED`-Sichten/PID-Startzeiten exakt stimmen und alle zwölf Sockets
   vor FD-Sichtbarkeit den richtigen Session-Tag besitzen. Exakt der gebundene
   single-threaded Setter darf einmal `INIT→SEALED` auslösen und muss danach
   `SO_PASSRIGHTS=0` lesen; jeder fremde, konkurrierende oder wiederholte
   `setsockopt`, auch mit bereits aufgelöster FD-loser `struct file`, muss am
   globalen LSM-Hook vor Mutation mit `-EPERM` enden. Zusätzlich muss der
   Rights-Freeze-Filter per TSYNC sämtliche Empfänger-TIDs erreichen. Erst der
   daran anschließende `getsockopt==0`-, `scm_fds: 0`-, Queue-, FD-/FDINFO-/
   OFD-/Lock-Nachweis darf durable OPEN autorisieren. Der Persistence Owner
   muss danach aus derselben erfolgreichen Sync-/Directory-Sync-/Readback-
   Fortsetzung genau `BOOTSTRAP→OPEN_DURABLE_GRANTED` ausstellen; dieser Grant
   öffnet keinen Send. Sendefähigkeit bleibt bis zur danach einmaligen Guard-
   Transition `OPEN_DURABLE_GRANTED→RELEASED` kernelweit gesperrt. Ein
   richtiger Guard-`SHUT_RDWR` aus `BOOTSTRAP` muss ohne Mutation scheitern.
   `msg_control=NULL` und `msg_controllen=0` gelten zusätzlich. Bei jedem
   injizierten `SCM_RIGHTS`-/Multi-CMSG-Paket muss `sendmsg` vor dem Queueing
   mit exakt `EPERM` enden. Das gilt auch, wenn der Empfänger vor `recvmsg`
   `SIGSTOP` erhält oder stirbt und der Sender danach seine eigene Referenz
   schließt oder abstürzt. Receive Queue, Empfänger-FD-/FDINFO-Inventur und
   Locks bleiben unverändert; nach `sendmsg`-Return darf weder eine im SKB
   gehaltene noch eine andere Empfänger-/Open-File-Description-/Lock-Referenz
   fortbestehen. Ein künstlich umgangener Kernel-Guard muss im Defense-in-
   Depth-Pfad weiterhin `MSG_CTRUNC` ohne fachliche Mutation und ohne
   überlebende Referenz liefern.

Vor jedem Session OPEN läuft zusätzlich in einem wegwerfbaren Probe-Child für
jedes der Szenarien Guardian-`SIGSTOP`, Broker-Stall/-Tod, Shim-Stall,
erfolgreiches Self-PIDFD-Signal, Self-Fehler mit erfolgreichem Guardian-Signal,
Self-/Guardian-Fehler mit erfolgreichem Broker-Signal sowie Fehler aller drei
PIDFD-Signale mit erfolgreichem Liveness-Close/HUP exakt 32 über den Heartbeat-
Zyklus verteilte Trials. Dieselben 32 Phasenpunkte werden zusätzlich für (a)
`terminal_trip()` plus Fehler aller drei PIDFD-Signale bei maximaler gebundener
Broker-Poll-/Pipe-Lock-Konkurrenz, (b) jeden verbotenen Write-/Read-/Transfer-
Syscall auf der Liveness-Pipe mit erwarteter `SECCOMP_RET_KILL_PROCESS`-Action
und (c) Orderly-Close gegen gleichzeitige Renewal ausgeführt. Weitere getrennte
32-Phasen-Serien halten (d) ausschließlich den Request-TID exakt nach
kernel-erzeugter Notification und vor Broker-Receive an, während
Guardian/Broker/Shim gesund bleiben, und injizieren (e) an jeder der sechs
Close-Grenzen `EINTR`, `EAGAIN`, Queue-full, Short/invalid, Peer-HUP, Timeout,
Crash, Verlust und byteidentische beziehungsweise konfliktäre Duplikate,
(f) jedes blockierbare Signal vor Broker-Receive und nach Broker-Receive samt
negativen Handler-/Unmask-/`SA_RESTART`-Versuchen sowie allen Listener-Ready-
Receive-Fehlern und (g) für jeden Kanal ein bis `SCM_MAX_FD` angebotene FDs,
mehrere CMSG-Reihenfolgen, `SO_PASSRIGHTS=1` plus Rights-Send an jeder Grenze
vor/während/nach LSM-Seal, TSYNC und finalen Rollenfiltern sowie nach durablem
OPEN vor Release, partielle Filterabdeckung, neu auftauchende TIDs,
versteckte Endpoint-Duplikation/-Übertragung, pre-Filter-PASS mit danach
eingereihtem Paket, vollständigen Bootstrap-Abbruch und Referenzfreigabe,
Empfänger-`SIGSTOP`/-Crash vor `recvmsg`, Sender-Close/-Crash, erwartetes
`EPERM`, dauerhaftes `scm_fds: 0`, den separaten `MSG_CTRUNC`-Defense-in-Depth-
Pfad und fremde Bootstrap-Connects. Serie (h) reproduziert V18-H1 auf jedem
Kanal exakt: Ein externer Prozess versucht den Endpoint per SCM_RIGHTS,
`pidfd_getfd` und `/proc/fd` zu erwerben; sein
`setsockopt(SO_PASSRIGHTS=1)` wird nach FD-Auflösung vor dem LSM-Hook
angehalten, der sichtbare FD geschlossen, eine `/proc`-Inventur ausgeführt und
der Caller erst nach Snapshot sowie nochmals nach durablem OPEN fortgesetzt.
Eine zweite Variante migriert den FD zwischen bereits inventarisierten
Prozessen. PASS verlangt, dass Akquisition/Transfer am `file_receive`-/
Bootstrap-`socket_sendmsg`-Hook mit `-EPERM` endet oder der bereits laufende
Optionscaller am socketlokalen `SEALED`-Hook vor jeder Optionskopie/-mutation
`-EPERM` erhält. In allen Varianten bleiben `SO_PASSRIGHTS=0`, `scm_fds: 0`,
Queue, OFD und Locks unverändert. Der externe Observer muss für (a) null
Pipe-Bytes, null Pipe-Pages und HUP/CAS innerhalb
`5 ms` bei gesundem Broker, für (b) null neue Pipe-/`struct file`-Referenzen und
für (c) exakt RUNNING→CLOSING→CLOSED→COMMITTED vor Trading-Exit belegen. Für
(d) muss der Broker die Notification ohne Request-TID-Fortschritt nach
TERMINATING linearisiert und den PIDFD-Kill angefordert haben; ein zusätzlicher
Whole-child-Stop muss dieselbe Broker- oder Lease-Fail-stop-Folge zeigen. Für
(e) darf ausschließlich PREPARE→Broker-CLOSED→durable COMMIT beim Startup clean
werden; Mutationen bleiben exactly once, Retries verwenden dieselben Bytes und
jeder frühere Abbruch bleibt beim simulierten Folgestart fail closed. Für (f)
darf kein blockierbares Signal den Request-TID zum Fallback zurückkehren
lassen; SIGKILL/SIGSTOP und jeder Receive-Fehler müssen terminal enden. Für
(g) müssen `SO_PEERCRED`, die vollständige TID-Abdeckung des irreversiblen
Rights-Freeze-Filters, **post-filter** `SO_PASSRIGHTS=0`, `scm_fds: 0`, leere
Queue und unveränderte FD-/FDINFO-/OFD-/Lock-Inventur vor Senderfreigabe,
`EPERM` vor Queueing sowie fehlende SKB-/OFD-Referenzen nach Sender-Close/-
Crash belegt sein. Jeder Setup-Rest muss Socket-/Queue-Zerstörung,
Referenzfreigabe und Abbruch ohne Retry derselben Session zeigen; zusätzlich
bleibt der nachgelagerte kernelseitige Autoclose ohne Runtime-`close`
nachzuweisen. Für (h) müssen Guard-Attach/Tag/Seal unverändert, sämtliche
unerlaubten Akquisitions-/Mutationsaufrufe `-EPERM`, Send-State bis nach
  durablem OPEN `OPEN_DURABLE_GRANTED`, weiterhin null erfolgreiche Sends und
  der genau einmalige anschließende Release nachgewiesen sein. Serie (i) führt
  `TerminalSeccompListenerHandoffV2` an jedem
Schritt mit den gebundenen Fehlern aus Abschnitt 7.8.2 aus und verlangt bei
PASS genau einen Broker-Listener-Halter, geschlossenen Trading-Quell-FD,
widerrufene Ptrace-/Dumpable-Autorität, null Runtime-Sockets und null
  `sendmsg`-Aufruf. Serie (j) prüft alle fünf Phase-Transitionen, alle sechs
  Zustände, die drei disjunkten Control-Sockets, falsches `how`, falsche
  TID/Startzeit/Cgroup/Session/Cookies, vertauschte Guard-/Ausstellerrollen,
  doppelten/rückwärts gerichteten Versuch und alle Userspace-Map-Writewege.
  Insbesondere müssen richtige Guard-Aufrufe vor dem jeweils fremd
  ausgestellten Grant ohne Phase-Mutation, Runtime-Socket- oder Sendewirkung
  scheitern; ein Grant allein öffnet keine Gatewirkung. Nur der exakte Hook-
  CMPXCHG darf das ausgerichtete Phase-Wort verändern. Fehlt eine der beiden
  Serien oder irgendein Messpunkt,
verhindert dies OPEN. Zusätzlich versucht ein
wegwerfbares Probe-Child unter exakt den produktiven TSYNC-/Rollenfiltern bei
gleichzeitig erzwungenen Fehlern aller drei PIDFD-Signale nach Ready jeweils `fork`, `vfork`,
`clone` und `clone3` sowie jede gebundene FD-Erzeugungs- und
Referenzbildungsvariante in einem
eigenen frischen Probe-TGID. PASS
verlangt, dass kein Child, TID, Files-Table-Split oder Writer-Halter entsteht,
`SECCOMP_RET_KILL_PROCESS` den gesamten Probe-TGID kernel-seitig beendet, der
dadurch verlorene letzte Writer Broker-HUP innerhalb `5 ms` als Trip-CAS
linearisiert und keine weitere Approval entsteht. TID-/FD-Inventur unmittelbar
vor dem Versuch und die vom
externen Parent beobachtete Postmortem-Inventur müssen den nicht entstandenen
Task/Writer belegen. Der getrennte Fehler-aller-drei-PIDFDs-/HUP-Trial bleibt
zusätzlich Pflicht; keiner der beiden Nachweise darf den anderen ersetzen. Ein
separater state-/
journalfreier Bootstrap-Probe prüft exakt die erlaubten Memfd-Create-Flags und
Seal-State-Transitionen sowie jeden genannten negativen Seal-Fall. Das aktuelle
System muss
Profilfingerprint, Cgroup, Affinity, Scheduling, Clock-Auflösung, Binärhashes
und sämtliche Einzelgrenzen exakt bestätigen. Der Probe-Child teilt keine
Runtime Session, State- oder Journal-FDs. Ein Fehler, Timeout oder
Environment-Mismatch blockiert OPEN ohne Fallback. Diese endliche Zertifizierung
begründet ausschließlich den benannten Capability-Envelope; sie wird nirgends
als universeller Worst Case bezeichnet.

---

## 8. Mode-neutraler Active Runtime Bridge

### 8.1 Einzige aktive Gate-Autorität

Ein neues Modul `live_l1/core/paper_iu4_runtime_gate.py` wird die einzige aktive
Bridge für `OFF`, `SHADOW` und `ENFORCED`.

Es besitzt:

- strikte Modus- und Operational-Profile-Auflösung;
- Git-/Commit-Bindung;
- Profil- und Fingerprint-Prüfung;
- Authorization-V2-Loader und Trust-Prüfung;
- Coordinator- und Reconciliation-Bindung;
- Legacy-/Atomic-Handoff-Klassifikation;
- `assert_current_binding()`;
- stabile Startup-Logfelder.

### 8.2 Keine parallele Shadow-Wahrheit

`paper_iu4_shadow_runtime_gate.py` darf nach Migration keine zweite
Profil-, Git-, Coordinator- oder Entscheidungslogik enthalten. Es wird entweder:

1. zu einer dünnen OFF/SHADOW-Kompatibilitätsfassade, die an den mode-neutralen
   Gate delegiert, oder
2. nach nachgewiesener Verbraucherfreiheit in einem eigenen Schritt entfernt.

Eine direkte Erweiterung der Shadow-spezifischen Implementierung um einen
versteckten ENFORCED-Zweig ist unzulässig.

### 8.3 Runtime-Gate-Ergebnis

Das Gate-Ergebnis enthält mindestens:

- Modus und Owner-Klassifikation;
- `passed`;
- `adapter_execution_enabled`;
- `shadow_observation_enabled`;
- `state_mutation_allowed`;
- `entry_allowed`, `exit_evaluation_allowed` und `runtime_directive`;
- Reason Codes;
- Repository Commit;
- alle Profilidentitäten;
- Activation- und gegebenenfalls Restart/Recovery-Authorization-ID;
- Atomic-State-Fingerprint und Transaction Sequence;
- Owner Epoch, `authority_generation_id`, `authority_commit_anchor`, aktueller
  `ledger_tip`, Runtime-Session-Status, Handoff-/Genesis-Manifest-ID und
  Legacy-Handoff-Status.

### 8.4 Git-Bindung

ENFORCED erfordert:

- exakten autorisierten HEAD-Commit;
- keine tracked Änderungen;
- keine untracked Python-/Konfigurationsdateien unter aktiven Import- und
  Konfigurationswurzeln, insbesondere `live_l1/` und den verwendeten
  Profilpfaden;
- keine von außerhalb des autorisierten Checkouts importierte Runtime-Kopie.

Unabhängige, nicht importierbare User-Artefakte außerhalb dieser Wurzeln dürfen
nicht automatisch gelöscht oder verändert werden.

---

## 9. Startup- und Handoff-Sequenz

`safe_launch.py` führt die Schritte in exakt dieser Reihenfolge aus:

1. Repository-Root kanonisch auflösen.
2. rohen IU4-Modus und rohes Operational Profile strikt lesen.
3. `PRODUCTION` und ungültige Profile abweisen.
4. bestehende Startup-Validierung ausführen.
5. Legacy S2/S4/Loss-Cluster ausschließlich zur Handoff-Klassifikation laden
   und validieren; nichts initialisieren oder mutieren.
6. Atomic Coordinator, Profile und Control Profile laden.
7. einen read-only Atomic Reconciliation Report erzeugen.
8. Lifecycle Ledger vollständig validieren; `ledger_tip`,
   `authority_commit_anchor`, `authority_generation_id`, Owner Epoch, offene
   PREPAREs und Runtime Sessions getrennt ableiten.
9. jeden offenen Authority-PREPARE oder eine Runtime Session ohne exakt
   passendes `RUNTIME_SESSION_CLOSE_COMMIT` fail closed klassifizieren;
   `RUNTIME_SESSION_CLOSE_PREPARE` allein sowie Broker-CLOSED ohne COMMIT sind
   ausdrücklich unclosed. Kein normaler Loop-Start ist dann zulässig.
10. angeforderte Operation und zugehörige Restart/Recovery Authorization
    zunächst read-only laden. Feststellen, ob Clean Genesis, `RESTART_ONLY`,
    `RECOVER_AND_RESTART`, `COMPLETE_AUTHORITY_PREPARE` oder
    `RECONCILE_TERMINAL_GAP` vorliegt. Ein offener PREPARE erlaubt
    ausschließlich `COMPLETE_AUTHORITY_PREPARE`.
11. nur für einen später loop-fähigen normalen Startup Activation Authorization
    V2 und getrennten Trust Anchor read-only gegen
    Commit/Profile/Control/R3/Evidence und den stabilen Authority Commit Anchor
    vorprüfen. `COMPLETE_AUTHORITY_PREPARE` und
    `RECONCILE_TERMINAL_GAP` verlangen keine Activation Authorization und
    dürfen unter keinen Umständen zum Loop fortschreiten.
12. die Clean-Genesis-Erststartausnahme nur dann anwenden, wenn der letzte
    Authority Record ein attestierter `ATOMIC_GENESIS_COMMIT` mit
    `completion_provenance=DIRECT` ist, kein Completion-Consumption-Record in
    seiner PREPARE→COMMIT-Kette liegt und noch nie ein `RUNTIME_SESSION_OPEN`
    für diese Generation existierte **und** aktuelle OS-Prozessinstanz,
    Genesis-Operation-Attempt und in-memory Continuation-Nonce-Preimage exakt
    `direct_process_instance_id`, `genesis_operation_attempt_id` und
    `direct_continuation_nonce_hash` des COMMIT bestätigen. Diese Prüfung darf
    nur in derselben ununterbrochenen Prozessinstanz unmittelbar nach DIRECT-
    COMMIT erfolgen. In jedem anderen Fall, insbesondere nach Prozesswechsel,
    Crash/`exec`, Nonce-Verlust oder bei `RECOVERED_AFTER_PREPARE`, die
    manuelle Restart/Recovery Authorization und ihren getrennten Trust Anchor
    gegen L1-D, Pre-State, exakten `pre_attempt_ledger_tip`, Authority
    Generation/Anchor, Startup Attempt und Environment prüfen; nach Genesis-
    Completion ist exakt `RESTART_ONLY` erforderlich.
13. jede nach Schritt 12 erforderliche Authorization durch genau einen
    `RESTART_AUTH_CONSUME`-Record am erwarteten Tip durable verbrauchen; die
    eng begrenzte DIRECT-Clean-Genesis-Erststartausnahme erzeugt keinen
    erfundenen Consumption Record. `RECOVERED_AFTER_PREPARE` ist von dieser
    Ausnahme kategorisch ausgeschlossen. Dasselbe gilt für jede neue
    Prozessinstanz nach einem DIRECT-COMMIT.
14. nur bei `RECOVER_AND_RESTART` den bereits committeten Journal-Head
    deterministisch als Snapshot materialisieren, read-only verifizieren und
    danach einen `RECOVERY_MATERIALIZATION`-Record anhängen.
15. bei `COMPLETE_AUTHORITY_PREPARE` vorhandenen Target State prüfen oder exakt
    materialisieren, read-only reconciliieren, genau den passenden COMMIT
    anhängen und ohne Loop-Start beenden.
16. bei `RECONCILE_TERMINAL_GAP` den Vertrag aus Abschnitt 16.2 vollständig
    ausführen und ohne Loop-Start beenden.
17. vollständige Atomic- und Lifecycle-Reconciliation erneut ausführen; die
    seit `pre_attempt_ledger_tip` entstandene Kette darf nur Records derselben
    `startup_attempt_id` enthalten.
18. Activation Authorization endgültig gegen Authority Generation/Anchor und
    den reconciled State prüfen; Gleichheit mit dem veränderlichen Ledger Tip
    ist weder gefordert noch zulässig.
19. vollständige S2/S4/Loss/Throttle-Handoff-Matrix auswerten.
20. `HARD` beendet den Startup vor Loop-Eintritt; `EMERGENCY` beendet den
    Prozess. Eine manuelle Kill-Deeskalation ist eine getrennte, explizite und
    vor dem Restart persistierte/attestierte Operation.
21. `TerminalRuntimeSocketLSMGuardV3` systemweit an alle sechs Hooks anhängen,
    Links/Maps pinnen, Guard, `TerminalHandoffRevocationAttestorV1` und
    Persistence Owner als getrennte single-threaded Bootstrap-Autoritäten an
    ihren Eventfd-Barrieren binden und exakt je ein disjunkt getaggtes
    `PHASE_CONTROL`-, `HANDOFF_REVOCATION_GRANT_CONTROL`- und
    `OPEN_DURABILITY_GRANT_CONTROL`-Socket erstellen. Erst nach geschlossenen
    Nicht-Owner-Kopien, vollständigen Identitäten/Cookies und externer
    Halterinventur die mit `map_flags=0` erzeugte initial nullwertige
    Phasen-Map sowie die Konfigurations-Map über ihre Create-FDs einfrieren,
    diese FDs schließen und nur `BPF_F_RDONLY`-Lese-FDs wieder öffnen.
    BPF-CMPXCHG/JIT sowie sämtliche Hook-/BTF-/Program-/Map-/Socket-/Cgroup-
    Identitäten attestieren und Phase `LISTENER_HANDOFF` herstellen, bevor
    eine Transition, weitere Rolle oder ein Runtime-Socket entsteht.
22. `TerminalSeccompListenerHandoffV2` vollständig ausführen: exakt einen
    Listener per gebundenem `pidfd_getfd` vom reservierten Trading-Quell-FD in
    den reservierten Broker-Ziel-FD duplizieren, über den geerbten Eventfd
    bestätigen, den Trading-FD schließen, `PR_SET_PTRACER=0`,
    `PR_SET_DUMPABLE=0`, leere Capabilities und finale Bootstrap-Filter
    nachweisen; der erfolgreiche `file_receive` muss zuvor genau
    `LISTENER_HANDOFF→LISTENER_RECEIVED` linearisiert haben. Erst nach
    vollständiger Revocation-/Ein-Halter-Evidence darf ausschließlich der
    Attestor per `SHUT_WR` genau
    `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED` ausstellen. Erst danach darf
    der Guard per `SHUT_RD` genau
    `HANDOFF_REVOKED_GRANTED→BOOTSTRAP` konsumieren. Bis dahin darf
    kein Runtime-Socket existieren; `sendmsg` bleibt ausnahmslos gesperrt.
23. `TerminalRuntimeChannelProvisioningV6` vollständig ausführen: alle
    Endpunkte bereits vor FD-Sichtbarkeit taggen, pro finalem Endpoint exakt
    `INIT→SEALED` plus `SO_PASSRIGHTS=0` beweisen, Empfänger-TSYNC und finale
    Rollenfilter installieren und erst dann den letzten Options-/Queue-/FD-/
    OFD-/Lock-Snapshot erheben. Jeder Rest lässt den globalen Send-Gate
    geschlossen, zerstört alle Endpunkte, terminiert die Rollen und beendet
    diesen Startup-Versuch.
24. Resource Reserve prüfen und ausschließlich nach PASS von Schritt 23 durch
    den Persistence Owner `RUNTIME_SESSION_OPEN` durable schreiben, Datei und
    erforderliches Parent Directory synchronisieren, den Record read-only
    byte-/hashgleich zurücklesen und alle Chain-/Fencing-Bindungen erneuern;
    bis dahin muss `socket_sendmsg` für die gesamte Session `-EPERM` liefern.
25. Ausschließlich aus derselben erfolgreichen Durable-Commit-Fortsetzung
    durch den Persistence Owner per `SHUT_WR` genau
    `BOOTSTRAP→OPEN_DURABLE_GRANTED` ausstellen. Dieser Grant darf keinen
    Sendepfad öffnen.
26. Ausschließlich danach durch den Guard per `SHUT_RDWR` im
    `socket_shutdown`-LSM-Hook genau einmal
    `OPEN_DURABLE_GRANTED→RELEASED` linearisiert ausführen und erst so die
    sechs Sendepfade freigeben; ein Userspace-Map-Writer existiert nicht.
27. `assert_current_binding()` einschließlich Session-/Chain-Konsistenz
    unmittelbar vor Loop-Start erneut ausführen.
28. Startup-Entscheidung, Restart-Freigabe und alle Identitäten loggen.
29. genau einen bestehenden L1-Loop starten; kein zweiter paralleler Loop.

Recovery ist eine manuell freigegebene State-Materialisierung, aber keine
Entry-Freigabe. Weder eine Boolean-Flag noch die Activation Authorization darf
sie allein auslösen.

### 9.1 Handoff-Matrix

Der Modus allein bestimmt nicht den State Owner. Der kanonische
`state_owner_epoch` ist genau `LEGACY` oder `PEE` und wird ausschließlich aus
dem letzten gültigen Authority-COMMIT-Record abgeleitet. Weder ein
Legacy- noch ein Atomic-Statefeld darf diese Autorität ersetzen. Jeder
Owner-Wechsel benötigt ein `IU4StateHandoffManifestV1` und das dazu exakt
passende PREPARE-/COMMIT-Paar. Das Manifest bindet mindestens:

- Richtung `LEGACY_TO_PEE` oder `PEE_TO_LEGACY`;
- Commit, Symbol, Coordinator und System-State-ID;
- vollständige Legacy- und Atomic-Pfade/Schemas, aktuelle Source-/Competing-
  State-Fingerprints sowie geplante Target-Business-/Core-Fingerprints; der
  erst nach PREPARE bestimmbare vollständige Target-State-Fingerprint steht
  ausschließlich im COMMIT;
- S2; vollständiges S4 mit `kill_level`, `cooldown_until_utc`,
  `trades_today`, `loss_today`, `anomaly_counter`, `trades_6h`,
  `last_trade_timestamp_utc` und Reason Codes; Loss Cluster; Throttle; und
  Progress Cursor;
- vorherigen und neuen Owner Epoch;
- vorherigen `authority_commit_anchor`, geplante `authority_generation_id`
  und `target_state_core_fingerprint`;
- vollständige deterministische Abbildung jedes S4-Felds und aller übrigen
  Safety Heads;
- verantwortlichen Operator, Zeitpunkt und Approval Reference.

Für den Legacy-Owner wird ein `IU4LegacySafetySnapshotV1` als kanonisch
fingergeprintete Handoff-Sicht erzeugt. Es enthält die vollständigen oben
genannten S4-Felder sowie S2-, Loss-Cluster-, Throttle-/Cooldown-, Progress-
und Authority-Generation-Bindungen. Es ist eine Zustandsprojektion, nicht die
Owner-Epoch-Autorität. Für den Atomic Owner bindet `AtomicPaperStateV2`
dieselben vollständigen Werte, `authority_generation_id` und
`authority_prepare_record_fingerprint`, aber keinen Ledger Tip oder
COMMIT-Fingerprint.

Die vollständige Matrix lautet:

| Owner Epoch | Legacy S2 | Atomic S2 | Safety Heads | Entscheidung |
|---|---|---|---|---|
| `LEGACY` | OPEN | FLAT | valid | Legacy exit-only; keine PEE-Entries |
| `LEGACY` | OPEN | OPEN | beliebig | FAIL: Dual Open |
| `LEGACY` | FLAT | FLAT | vollständig gemappt | `LEGACY_TO_PEE` nur mit Handoff Manifest |
| `LEGACY` | FLAT | OPEN | beliebig | FAIL: Atomic Open ohne PEE Owner Epoch |
| `PEE` | FLAT | OPEN | vollständig konsistent | PEE Resume nach manuellem Restart |
| `PEE` | FLAT | FLAT | vollständig konsistent | PEE FLAT zulässig |
| `PEE` | OPEN | beliebig | beliebig | FAIL: stale/konkurrierender Legacy Open |
| beliebig | corrupt/missing/unknown | beliebig | beliebig | FAIL, außer attestierte Clean Genesis |
| beliebig | beliebig | corrupt/missing/unknown | beliebig | FAIL |

Für Safety Heads gelten zusätzlich:

1. Der effektive Kill-Level ist der höhere nach
   `NONE < SOFT < HARD < EMERGENCY`; ein Konflikt wird nie durch Auswahl des
   niedrigeren Levels gelöst.
2. `HARD` und `EMERGENCY` erlauben keinen Loop-Start. Eine Deeskalation erfolgt
   nur manuell, explizit und vor dem neuen Restart.
3. Der spätere Cooldown-Zeitpunkt gewinnt. Ein nicht vergleichbarer oder
   ungültiger Cooldown blockiert den Handoff.
4. Beim ersten `LEGACY_TO_PEE` ist der validierte Legacy-Loss-Cluster die
   autoritative Quelle. Ein Shadow-Atomic-Loss-Cluster ist nicht autoritativ
   und darf nur durch das Handoff Manifest ausdrücklich verworfen werden.
5. Weist der nichtautoritative Atomic-State eine strengere Pause auf, muss das
   Manifest entweder diese strengere Pause übernehmen oder den Konflikt
   begründet blockieren; stilles Zurücksetzen ist verboten.
6. Legacy Trade-Zähler/Cooldown werden deterministisch in den genehmigten
   Atomic Throttle überführt. Ist keine verlustfreie Abbildung möglich, bleibt
   ENFORCED gesperrt.
7. Nach einem PEE Owner Epoch ist ein direkter Start von OFF/SHADOW mit stale
   Legacy-Risk-State verboten. `PEE_TO_LEGACY` muss S4, Loss Cluster, relevante
   Throttle-/Cooldown-Heads und Progress Cursor zuerst explizit projizieren und
   attestieren.
8. Fehlende, implizit auf Default gesetzte oder nicht verlustfrei abbildbare
   Werte für `loss_today` oder `anomaly_counter` blockieren Genesis, Migration
   und beide Handoff-Richtungen ebenso wie jeder andere S4-Konflikt.

### 9.2 Legacy exit-only

Für eine valide offene Schema-1-Position gilt:

- keine PEE-Position wird erfunden oder geöffnet;
- keine PEE-Quantity, Fill, Fee oder PnL wird rückwirkend erzeugt;
- alle neuen Entry-Intents werden blockiert;
- nur die bestehende Legacy-Exit-Semantik unter einem
  `IU4LegacyExitOnlyControlBindingV1` darf die Altposition schließen;
- der Abschluss wird `economics_incomplete` und `legacy_exit_only` markiert;
- Legacy S4 und Loss Cluster bleiben bis zum Abschluss autoritativ;
- nach erfolgreichem Close beendet sich der Prozess kontrolliert;
- danach ist ein vollständiger `LEGACY_TO_PEE`-Handoff erforderlich;
- erst ein neuer Startup mit erneut bestandener Reconciliation und Handoff darf
  PEE-Entries zulassen.

`IU4LegacyExitOnlyControlBindingV1` bindet die explizit aufgelösten LONG/SHORT
TP-, SL- und Time-stop-Werte, Opposing-intent-Regel, Loss-Cluster-Policy,
Environment-/Config-Quelle, Position-Fingerprint und einen kanonischen
Fingerprint. Es gibt keine Defaults. Fehlt die historische Konfiguration, wird
kein automatischer Legacy-Exit simuliert; die Position verlangt eine manuelle
Recovery-/Exit-Entscheidung.

Das ENFORCED Runtime-Control-Profil darf eine Legacy-Altposition nicht
rückwirkend umdefinieren. Die Legacy-exit-only-Bindung ist ein eigener,
positiongebundener Vertrag.

Liegt der effektive Kill-Level bei `HARD` oder `EMERGENCY`, startet auch der
Legacy-exit-only-Loop nicht. L0/L1 Restart- und manuelle Reset-Regeln gelten
unverändert.

Ein automatischer Owner-Wechsel innerhalb desselben Prozesses ist unzulässig.

### 9.3 Clean Genesis

Fehlender Legacy-State darf nicht still als FLAT interpretiert werden. Eine
Clean Genesis benötigt ein separates, hashgebundenes Initialisierungsmanifest,
das mindestens bindet:

- Symbol, Starting Equity und sämtliche Profile/Fingerprints;
- Coordinator-ID, System-State-ID und `state_owner_epoch=PEE`;
- S2 FLAT einschließlich vollständigem Fingerprint;
- vollständiges `PaperRiskStateS4V2` mit explizitem `kill_level`,
  `cooldown_until_utc`, `trades_today`, `loss_today`, `anomaly_counter`,
  `trades_6h`, `last_trade_timestamp_utc`, Reason Codes,
  Capability-Feldern und Fingerprint;
- leeren, explizit versionierten Loss Cluster samt Revision/Fingerprint;
- initiale Throttle-Heads, Cooldown und Fingerprint;
- initialen Progress Cursor;
- Transaction Sequence `0`, leeren Journal Head und nachgewiesen leeres
  Journal-Verzeichnis;
- alle Cross-State-Fingerprints und State-Pfade;
- Abwesenheit konkurrierender Legacy-/Atomic-Heads;
- Operator, Zeitpunkt und getrennte Approval Reference.

Genesis und Aktivierung sind getrennte autorisierte Operationen. Kein Feld darf
aus einem Runtime-Default ergänzt werden.

Die Atomic Genesis ist eine crash-sichere Lifecycle-Operation, keine
Trading-Tick-Transaktion. Ihre Reihenfolge ist verbindlich:

1. exklusiven Lifecycle-/State-Initialisierungs-Lock erwerben;
2. leeres Journal, Transaction Sequence `0` und Abwesenheit konkurrierender
   State-/Owner-Heads nochmals validieren;
3. Target-Business-Payload fingerprinten, daraus `authority_generation_id` und
   anschließend die Target-Core-Payload deterministisch bilden;
4. genau einen `ATOMIC_GENESIS_PREPARE` mit Core-Fingerprint,
   Manifest-/Approval-Fingerprint und geplantem Owner Epoch durable schreiben
   und File sowie Directory `fsync`en;
5. den Atomic-V2-Snapshot mit Generation ID und PREPARE-Fingerprint atomar
   schreiben, ersetzen und File sowie Directory `fsync`en;
6. Snapshot, leeres Journal und alle Cross-State-Fingerprints read-only erneut
   reconciliieren;
7. genau einen `ATOMIC_GENESIS_COMMIT`, der PREPARE, vollständigen
   Target-State-Fingerprint und `completion_provenance=DIRECT` samt
   ursprünglicher Prozess-/Operation-/Approval-Bindung,
   `direct_process_instance_id`, `genesis_operation_attempt_id` und Hash der
   nur in dieser Prozessinstanz im Speicher gehaltenen Continuation Nonce
   enthält, durable schreiben und erneut reconciliieren. Erst dann existiert
   der PEE Owner Epoch.

Ein Crash vor durable PREPARE hinterlässt keine Genesis. Ein Crash nach PREPARE,
aber vor COMMIT, hinterlässt eine unvollständige Authority-Operation und keinen
aktiven Owner; der Prozess startet keinen Loop. Nur eine neue
`IU4RestartRecoveryAuthorizationV1` mit
`operation=COMPLETE_AUTHORITY_PREPARE` darf exakt die im PREPARE gebundene
Core-Payload idempotent materialisieren und denselben COMMIT abschließen; auch
dieser COMMIT muss `completion_provenance=RECOVERED_AFTER_PREPARE` sowie die
exakte Completion-Authorization-, Consumption-Event-, Startup-Attempt- und
Pre-Tip-Bindung enthalten. Danach startet sie keinen Loop; der folgende Start
benötigt eine neue `RESTART_ONLY`-Authorization. Jede
fachliche Abweichung erfordert eine neue Genesis-Entscheidung nach expliziter
Bereinigung außerhalb des Runtime-Prozesses. Für `LEGACY_GENESIS`, beide
Handoffs und `ATOMIC_V1_TO_V2_MIGRATION` gelten dieselben zweiphasigen,
selbstreferenzfreien `fsync`-, Reconciliation- und Recovery-Grundsätze.

---

## 10. Ein Loop, ein Execution Seam

Marktdaten, Feature-Build, Regime, 1m-Intent, 5m-Timing und Fusion bleiben eine
gemeinsame Pipeline. Nach dem finalen Fused Intent existiert genau ein
mode-abhängiger Execution Seam:

```text
market -> features -> regime -> fused intent -> pure execution control
                                             |
                         OFF/SHADOW ----------+--> Legacy execution
                                             |
                         ENFORCED ------------+--> IU4 Adapter -> Atomic Coordinator
```

Es ist unzulässig, den vollständigen Loop zu kopieren oder eine zweite aktive
Markt-/Intent-Pipeline für ENFORCED einzuführen.

In OFF/SHADOW muss die bestehende Reihenfolge einschließlich der heutigen
Shadow-Beobachtung erhalten bleiben. In ENFORCED wird Legacy Execution am
Execution Seam vollständig übersprungen, außer im expliziten Legacy-exit-only
Handoff.

### 10.1 Vollständige Side-Effect-Klassifikation

Der Seam umfasst nicht nur `apply_paper_execution()`, sondern jeden mutierenden
oder autoritativ wirkenden Consumer nach dem Fused Intent:

| Side Effect | OFF | SHADOW | ENFORCED PEE | Legacy exit-only |
|---|---:|---:|---:|---:|
| `apply_paper_execution()` | ja | ja | **nein** | nur Exit der gebundenen Altposition |
| Legacy Loss-Cluster-Mutation | ja | ja | **nein** | ja, bis Legacy Close |
| Legacy S2/S4-Mutation im Loop | ja | ja | **nein** | nur Altposition/Risk |
| `persist_state()` Schema 1 | ja | ja | **nein** | ja, bis kontrollierter Stop |
| Legacy Trade-/Execution-Audit | ja | ja | **nein** | nur als Legacy-exit-only |
| passive Legacy Lifecycle/Risk/Accounting Sidecars | ja | ja | **nein** | nur ausdrücklich Legacy-markiert |
| IU4 Shadow Observer/Sandbox | nein | ja | **nein** | nein |
| Atomic Coordinator V2 | nein | Source read-only | ja | nein |
| PEE Audit/Compatibility Projection | nein | Evidence only | ja, post-commit | nein |
| Progress Persistence | Legacy State | Legacy State | Atomic V2 | Legacy State |

Die Implementierung muss den gesamten Block nach dem Intent mode-abhängig
strukturieren. Ein bloßer Branch um `apply_paper_execution()` reicht nicht.
Insbesondere dürfen in ENFORCED keine späteren `state.last_*`-/S2-/S4-
Zuweisungen, kein `persist_state()` und keine Legacy-Sidecars mehr durchfallen.

Gemeinsame Market-, Regime- und Intent-Logs dürfen mode-neutral bleiben, wenn
sie keinen Legacy State mutieren und keine Economics-Autorität beanspruchen.

### 10.2 Atomic Progress Cursor

Der ENFORCED-Pfad darf den Resume-Cursor nicht weiter in Legacy S2/S4
persistieren. `AtomicPaperStateV2` enthält deshalb einen gebundenen
`AtomicProgressCursorV1` mit mindestens:

- letztem vollständig verarbeiteten Snapshot ID;
- letztem Timestamp UTC;
- letztem Tick ID;
- letztem Intent ID;
- Cursor Fingerprint.

`AtomicPaperTransactionV2` unterstützt zusätzlich `PROGRESS`. Für einen
akzeptierten Tick ohne OPEN/CLOSE/ENTRY_VETO committed `PROGRESS`
ausschließlich den Cursor und die daran gebundene S4-/Aggregate-Identität. Auf
einem mutierenden Tick tragen OPEN, CLOSE oder ENTRY_VETO denselben Cursor
atomar mit; es gibt keine zweite PROGRESS-Transaktion. KILL ist dagegen eine
Control-Transaktion und besitzt den Tick-Cursor nicht.

Ein Snapshot gilt erst nach diesem Commit als verarbeitet. Replay derselben
Snapshot-/Tick-Identität ist idempotent; gleiche Identität mit anderer Payload
ist ein Journal-Konflikt. Damit wird Legacy `persist_state()` in ENFORCED nicht
als versteckte Progress-Autorität benötigt.

### 10.3 Snapshot-Akzeptanzgrenze

Jeder beobachtete Snapshot besitzt genau einen der folgenden Zustände:

- `OBSERVED_PRE_ACCEPT`: gelesen, aber noch ohne mutierende Autorität;
- `REJECTED_PRE_ACCEPT`: Binding-, Authorization-, State-, Schema- oder
  Ressourcenprüfung ist vor Akzeptanz fehlgeschlagen;
- `ACCEPTED`: Identität, Binding, autoritativer State und die für den Commit
  notwendigen Ressourcen sind validiert;
- `COMMITTED`: genau eine Tick-Transaktion besitzt den Cursor;
- `TERMINAL`: ein HARD-/EMERGENCY-Control-Record beendet Loop oder Prozess.

Ein `REJECTED_PRE_ACCEPT` erzeugt weder Tick-Transaktion noch Cursor-Fortschritt
oder fachliche State-Mutation. Es darf ausschließlich stabile diagnostische
Evidence außerhalb der State-Autorität erzeugen. Dadurch gilt die
Exactly-once-Forderung nicht pauschal für jeden gelesenen ENFORCED-Tick,
sondern exakt für jeden `ACCEPTED` Snapshot.

Nach `ACCEPTED` muss der Snapshot genau eine Tick-Transaktion erhalten, sofern
nicht eine terminale KILL-Eskalation die noch uncommittete Tick-Verarbeitung
abwirft. Ein Fehler vor durable Journal Write lässt den Cursor unverändert und
der Snapshot darf nach manuell autorisiertem Restart erneut akzeptiert werden.
Existiert bereits ein durable Journal-Record, wird ausschließlich dieser exakt
materialisiert; eine zweite fachliche Entscheidung ist verboten.

---

## 11. Pure Execution Control

### 11.1 Verantwortlichkeit

Ein reines Modul `live_l1/core/paper_execution_control.py` extrahiert aus der
heutigen monolithischen Legacy-Funktion ausschließlich die Entscheidung:

- `NOOP`;
- `OPEN_LONG`;
- `OPEN_SHORT`;
- `CLOSE_LONG`;
- `CLOSE_SHORT`.

Es liefert zusätzlich einen stabilen Trigger Reason Code, aber:

- mutiert keinen State;
- berechnet keine Quantity;
- berechnet keine Fill-Preise, Fees oder PnL;
- schreibt keine Logs;
- liest oder schreibt keine Dateien;
- ruft keinen Adapter und keine Exchange-Schnittstelle auf.

### 11.2 Triggerpriorität

Für eine offene Position ist die Priorität verbindlich:

1. Price Exit mit der bestehenden side-spezifischen Semantik: LONG prüft TP
   (`price >= tp`) vor SL (`price <= sl`), SHORT prüft TP (`price <= tp`) vor
   SL (`price >= sl`);
2. Time-stop;
3. Opposing final intent;
4. HOLD/gleichgerichtetes Intent als NOOP.

Characterization Tests müssen diese Reihenfolge einschließlich Grenzwerten vor
der Extraktion gegen den Basisstand beweisen. Eine davon abweichende Beobachtung
ist ein Spezifikationskonflikt und stoppt das Implementierungspaket; sie wird
nicht still durch eine neue Priorität gelöst.

### 11.3 Parität

OFF und SHADOW müssen nach Extraktion für identische Inputs dieselben Actions,
Reasons und Positionstransitionen wie der Basisstand liefern. Erst danach darf
ENFORCED das reine Control-Ergebnis verwenden.

### 11.4 Kein synthetisches Opposing Intent

Ein autonomer TP-/SL-/Time-stop-Close darf nicht durch ein erfundenes BUY- oder
SELL-Intent simuliert werden. Der Adaptervertrag wird deshalb versioniert und
erhält eine explizite Control Action.

---

## 12. IU4 Adapter Request V2

`IU4AdapterRequestV1` bleibt unverändert für bestehende Tests und Shadow-
Harnesses. Die aktive Integration verwendet additiv `IU4AdapterRequestV2`.

V2 bindet mindestens:

- `schema_version=2`;
- `request_id` aus kanonischer Payload;
- Source Intent ID, final Intent und Intent Reason;
- explizite `control_action` und `control_reason_code`;
- erwarteten Atomic-State-Fingerprint und Transaction Sequence;
- target System State ID;
- Timestamp, Tick ID und Snapshot ID;
- Canonical `reference_price_text`;
- Decimal `reference_price` nur als direkt daraus erzeugten Wert;
- Decimal `reference_stop_price` für OPEN;
- Trade ID für OPEN/CLOSE;
- alle Economics-, Throttle- und Runtime-Control-Fingerprints;
- Authorization-ID.

Der Adapter validiert:

- Action passt zur aktuellen Position;
- OPEN passt zum finalen BUY/SELL-Intent;
- autonomer CLOSE benötigt keinen gefälschten Opposing Intent;
- State-, Profil-, Authorization- und Event-Identitäten stimmen;
- gleiche Request-ID mit abweichender Payload ist ein Konflikt.

V1 darf nicht als Fallback für aktive ENFORCED-Requests verwendet werden.

---

## 13. Atomarer State V2 und Loss-Cluster-Integration

### 13.1 Notwendige Versionierung

`AtomicPaperStateV1` bindet Position, Account, Throttle und S4, aber nicht den
autoritativen Loss-Cluster-State. Eine getrennte Loss-Cluster-Datei würde bei
CLOSE oder Entry-Veto wieder zwei Recovery-Wahrheiten erzeugen.

Die aktive Integration führt deshalb additiv ein:

- `AtomicPaperStateV2`;
- `AtomicPaperTransactionV2`;
- einen in den Aggregate Fingerprint einbezogenen `LossClusterStateV2`;
- eine S4-Bindung an dessen Fingerprint;
- Runtime-Control-/Loss-Cluster-Policy-ID und Fingerprint im Aggregate State;
- `state_owner_epoch=PEE`, `authority_generation_id`,
  `authority_prepare_record_fingerprint` und gebundene
  Handoff-/Genesis-Manifest-ID; weder Ledger Tip noch Authority-COMMIT-
  Fingerprint sind Teil des State-Fingerprints;
- einen `AtomicProgressCursorV1`;
- bei offener Position das vollständige committete Entry Quote.

V1-Artefakte werden nicht still als V2 interpretiert.

### 13.2 PaperRiskStateS4V2 und terminale Capability

`PaperRiskStateS4V1` bleibt für seine bestehenden Verbraucher unverändert. Da
V1 invariant `exit_allowed=true` verlangt, darf V1 keinen terminalen
HARD-/EMERGENCY-State des aktiven Atomic-V2-Aggregats repräsentieren. Nur das
additive `PaperRiskStateS4V2` ist in `AtomicPaperStateV2` zulässig.

S4V2 bindet mindestens:

- `schema_version=2`;
- `kill_level`, `cooldown_until_utc`, `trades_today`, `loss_today` als
  kanonischen Decimal String und `anomaly_counter`;
- `trades_6h` und `last_trade_timestamp_utc`;
- `entry_allowed` und `exit_evaluation_allowed`;
- `runtime_directive` als `CONTINUE`, `STOP_LOOP` oder `EXIT_PROCESS`;
- deterministische `reason_codes`;
- Position-, Account-, Throttle-, Loss-Cluster-, Progress-Cursor-,
  Runtime-Control-Fingerprints sowie `authority_generation_id`;
- Transaction Sequence, Journal Head und eigenen S4-Fingerprint.

Verbindliche Capability-Invarianten:

| Kill-Level | Entry | Exit-Auswertung | Runtime Directive |
|---|---:|---:|---|
| `NONE` | gemäß Guards | ja | `CONTINUE` |
| `SOFT` | nein | ja | `CONTINUE` |
| `HARD` | nein | nein | `STOP_LOOP` |
| `EMERGENCY` | nein | nein | `EXIT_PROCESS` |

Kein Runtime-Pfad darf `exit_evaluation_allowed` als automatischen Exit-Befehl
interpretieren. HARD/EMERGENCY führen gerade keine weitere automatisierte
Snapshot- oder Exit-Auswertung aus. Eine Deeskalation bleibt eine separate,
manuell autorisierte Lifecycle-/Control-Operation und ist niemals Folge eines
Ticks, Restarts oder Tageswechsels.

### 13.3 Committed Entry Economics Quote

`PositionStateS2V2` bleibt der Positionsvertrag, enthält aber nicht alle Felder
von `EntryEconomicsQuote`, die `settle_trade()` benötigt. Die aktive
Integration führt deshalb in `paper_artifacts.py` additiv ein
`EntryEconomicsQuoteArtifactV1` ein.

Das Artefakt:

- serialisiert jedes Feld des ursprünglichen `EntryEconomicsQuote` ohne
  Neuberechnung;
- verwendet ausschließlich kanonische Decimal Strings;
- bindet Economics Profile, Model und Config Fingerprint;
- besitzt einen kanonischen Quote Fingerprint;
- wird im OPEN-Journal und in `AtomicPaperStateV2.entry_quote` gespeichert.

Cross-State-Invarianten:

- S2 OPEN verlangt genau ein Entry Quote;
- S2 FLAT verlangt `entry_quote=null`;
- alle gemeinsamen S2-/Quote-Felder müssen exakt gleich sein;
- Quote, Position, Account und Runtime Profile müssen dieselben Identitäten
  tragen;
- CLOSE verwendet genau dieses gespeicherte Quote;
- erneutes `authorize_entry()` zur Rekonstruktion des Entry Quote beim Close
  ist verboten.

`settle_trade()` kann dadurch unverändert mit einem exakt aus dem Artefakt
deserialisierten `EntryEconomicsQuote` arbeiten. Eine Änderung von S2 V2 ist
nicht erforderlich; `paper_artifacts.py` gehört ausdrücklich zum späteren
Implementierungsscope.

### 13.4 Tick-, Control- und Lifecycle-Transaktionen

V2 trennt drei Ordnungsräume:

1. **Tick-Transaktion:** Genau eine pro `ACCEPTED` Snapshot besitzt dessen
   Cursor. Ihr `primary_effect` ist exakt `OPEN`, `CLOSE`, `ENTRY_VETO` oder
   `PROGRESS`. Sie darf optional ausschließlich
   `risk_escalation=NONE_TO_SOFT` atomar tragen.
2. **Control-Transaktion:** `KILL` besitzt eine eigene Control Event ID und
   keinen Progress Cursor. Sie darf dieselbe Tick ID als Ursache referenzieren,
   ist aber keine zweite Tick-Transaktion.
3. **Lifecycle-Record:** Genesis, Handoff, Migration, Restart-Consumption und
   Recovery-Materialisierung liegen ausschließlich im Lifecycle Ledger und
   sind keine Atomic Tick-/Control-Transaktionen.

Die Tick-Effekte sind:

- `OPEN`: S2 FLAT→OPEN, Entry Quote, accepted throttle event, Progress Cursor
  und gebundenes S4;
- `CLOSE`: Trade V2, Paper Account, S2 OPEN→FLAT, Entry Quote→null, Loss
  Cluster, Progress Cursor und S4;
- `ENTRY_VETO`: ausschließlich der reproduzierbare Loss-Cluster-Pausezähler
  plus Progress Cursor und davon abgeleitetes S4; S2, Account und accepted
  throttle bleiben gleich;
- `PROGRESS`: ausschließlich Progress Cursor und gebundene Aggregate-Identität.

`ENTRY_VETO` ist nur zulässig, wenn die etablierte Loss-Cluster-Semantik einen
Entry-Kandidaten blockiert und dabei `pause_entries_remaining` dekrementiert.
Andere Entry-Ablehnungen mutieren keinen autoritativen State.

Kombinierte Ereignisse sind eindeutig geordnet:

- CLOSE plus SOFT wird als eine CLOSE-Tick-Transaktion mit atomarer
  `risk_escalation=NONE_TO_SOFT` committed.
- Ohne Eskalation fehlt das Feld. `NONE→NONE` und `SOFT→SOFT` sind keine
  Transition; `SOFT→NONE`, `HARD→*` und `EMERGENCY→*` sind in einer
  Tick-Transaktion verboten. Jede Deeskalation benötigt den getrennten
  manuellen Control-/Restart-Vertrag.
- Eine vor Tick-Akzeptanz bekannte HARD-/EMERGENCY-Eskalation schreibt nur die
  KILL-Control-Transaktion; der Snapshot bleibt ohne Tick-Transaktion.
- Wird die terminale Eskalation nach Akzeptanz, aber vor durable Tick-Journal
  erkannt, wird der uncommittete Tick verworfen und nur KILL committed.
- Ist der Tick-Journal-Record bereits durable, bleibt er autoritativ und wird
  vollständig materialisiert; danach folgt genau eine KILL-Control-Transaktion
  mit eigener Event ID und optional derselben ursächlichen Tick ID.
- OPEN ist verboten, sobald eine KILL-Eskalation pending oder erkannt ist.
- Bei ENTRY_VETO plus terminalem KILL gewinnt KILL vor dem Veto-Commit. Ist der
  Veto-Record bereits durable, bleibt er exakt einmal wirksam und KILL folgt
  separat.

Damit bedeutet „genau eine“ genau eine Cursor-besitzende Tick-Transaktion pro
akzeptiertem, nicht vor Commit terminal verworfenem Snapshot, nicht genau einen
Journal-/Lifecycle-Record insgesamt.

### 13.5 CLOSE und Loss Cluster

Der CLOSE-Commit aktualisiert den Loss Cluster aus der autoritativen Decimal-
Netto-PnL des `TradeRecordV2`. Das Update ist Teil desselben Journaleintrags wie
Settlement, Account und S2-FLAT. Ein Crash kann dadurch weder PnL doppelt buchen
noch die Loss-Cluster-Schutzwirkung verlieren.

Im ENFORCED-Pfad werden neue Loss-Cluster-PnL-Werte ausschließlich aus
kanonischen Decimal Strings beziehungsweise `Decimal` erzeugt. Die bestehende
Float-Kompatibilität des Legacy-Stores ist keine zulässige wirtschaftliche
Eingangsgrenze für neue PEE-Trades.

### 13.6 Migration

- Atomic V1→V2 erfolgt nur über ein eigenes, offline geprüftes
  Migrationsartefakt.
- Automatische In-place-Migration beim Startup ist verboten.
- Eine offene oder widersprüchliche V1-Position blockiert die Migration.
- Legacy `LossClusterStateV2` darf nur nach Schema-, Checksum-, Pfad- und
  Reconciliation-Prüfung übernommen werden.
- Fehlender Loss-Cluster-State benötigt eine explizite Clean-Genesis-
  Entscheidung; `missing_allowed` ist in ENFORCED unzulässig.
- Owner Epoch, Authority Generation/Anchor, Progress Cursor und vollständige
  S4V2-Safety-Heads einschließlich `loss_today` und `anomaly_counter` sind Teil
  jeder Migration; eine positions-only Migration ist unzulässig.
- Die Migration schreibt zuerst
  `ATOMIC_V1_TO_V2_MIGRATION_PREPARE`, publiziert danach den mit Generation ID
  und PREPARE-Fingerprint gebundenen V2-State und schreibt erst nach
  erfolgreicher Reconciliation `ATOMIC_V1_TO_V2_MIGRATION_COMMIT`. Ein
  Teilzustand verlangt `COMPLETE_AUTHORITY_PREPARE` zur manuell autorisierten,
  idempotenten Fertigstellung exakt dieser Generation; stilles Wiederholen ist
  verboten.

---

## 14. Verbindliche ENFORCED-Entry-Sequenz

Für `FLAT` plus `OPEN_LONG` oder `OPEN_SHORT` gilt exakt:

1. aktuelle Gate-, Commit-, Authorization- und Profilbindung prüfen;
2. Atomic State laden und erwarteten Fingerprint/Sequence vergleichen;
3. Canonical Price Text als endlichen positiven Decimal validieren;
4. bestehenden Gate Mode und S4 Kill Level prüfen;
5. bestehende Pre-Execution-Guards prüfen;
6. Loss Cluster prüfen;
7. Paper-Account Loss/Fee/Drawdown-Grenzen prüfen;
8. Entry Throttle prüfen;
9. Decimal Reference Stop aus Control Profile berechnen;
10. PEE Authorization und risikobasierte Quantity berechnen;
11. bei Ablehnung stabile Denial Evidence schreiben;
12. bei Loss-Cluster-Veto gegebenenfalls genau eine `ENTRY_VETO`-Transaktion
    committen;
13. bei Annahme vollständige S2-V2-Open-Position und das vollständige
    `EntryEconomicsQuoteArtifactV1` direkt aus dem PEE Quote bauen;
14. OPEN aus S2, Entry Quote, accepted throttle event, Progress Cursor und S4
    unter einer Event-ID journalen;
15. Snapshot atomar publizieren;
16. Audit und Legacy-Kompatibilitätsprojektion erst aus dem Commit erzeugen.

Verbindliche Ablehnungsinvariante:

- S2, Paper Account und accepted throttle state bleiben unverändert;
- nur ein semantisch erforderliches `ENTRY_VETO` darf den Loss-Cluster-Zähler
  verändern;
- keine feste oder Ersatz-Quantity wird erzeugt.

Der Coordinator wiederholt Account-, Throttle-, Loss-Cluster- und
State-Invarianten beim Commit. Ein vorab berechnetes ALLOW allein reicht nicht.
Ein abgelehnter Entry ohne ENTRY_VETO committed den Tick als `PROGRESS`, sodass
der Input nach Restart nicht erneut als neuer Kandidat erscheint.

---

## 15. Verbindliche ENFORCED-Exit-Sequenz

Für eine autoritative PEE-Position gilt exakt:

1. Pure Execution Control bestimmt CLOSE/NOOP und Reason.
2. Entry-Blocker werden für CLOSE nicht als Veto verwendet.
3. Atomic S2 V2, das vollständige committed Entry Quote und Paper Account
   werden mit erwarteter Identität geladen.
4. Canonical Current Price Text wird direkt zu Decimal konvertiert.
5. PEE Settlement wird genau einmal aus dem gespeicherten
   `EntryEconomicsQuoteArtifactV1` und aktuellem Canonical Price erzeugt; eine
   erneute Entry-Autorisierung ist unzulässig.
6. `TradeRecordV2` wird vollständig aus committed Entry- und Settlement-
   Artefakten gebaut.
7. Loss Cluster wird aus Decimal-Netto-PnL reproduzierbar fortgeschrieben.
8. CLOSE journaled Trade V2, Account, Loss Cluster, S2 FLAT,
   `entry_quote=null`, Progress Cursor und S4 gemeinsam.
9. Snapshot wird atomar publiziert.
10. Audit und Compatibility Projection folgen erst nach dem Commit.

Ein Logfehler nach erfolgreichem Commit rollt den Trade nicht zurück. Der
Coordinator-Journal bleibt die Recovery-Autorität. Der Projection Cursor wird
als nachhinkend markiert; neue Entries bleiben gesperrt, bis die Projektion
reconciled ist. Weitere risikoreduzierende Exits bleiben unter nichtterminalen
Entry-Sperren möglich. Bei `HARD` oder `EMERGENCY` gelten stattdessen die
sofortigen L0/L1-Abbruchregeln.

---

## 16. KILL-, Guard- und Freigabesemantik

### 16.1 Guard-Reihenfolge

Für Entries ist die Reihenfolge verbindlich:

1. Runtime-/Authorization-Bindung;
2. State/Reconciliation;
3. Gate Mode und S4 Kill;
4. bestehende fachliche Pre-Execution-Guards;
5. Loss Cluster;
6. Paper Account;
7. Throttle;
8. PEE Authorization.

Ein späterer Guard darf einen früheren Blocker nicht überschreiben. Für die
Evidence wird der erste autoritative Blocker als primärer Reason Code und die
vollständige deterministische Liste als `reason_codes` gespeichert.

### 16.2 KILL

- KILL-Eskalationen werden bei verfügbarer Persistenz als eigene
  Coordinator-Control-Transaktion mit eindeutiger Control Event ID journaled;
  sie besitzen keinen Progress Cursor.
- Eine Deeskalation benötigt eine externe `authorization_reference`.
- Neustart, profitabler Tick oder Tageswechsel heben KILL nicht automatisch auf.
- `SOFT` blockiert neue Entries; der laufende Loop darf sichere Exits weiter
  verarbeiten.
- `HARD` beendet den Trading-Loop sofort. Es werden keine weiteren Snapshots,
  Intents oder automatischen Exits verarbeitet.
- `EMERGENCY` beendet den Prozess sofort und verbietet Auto-Restart.
- Jede erfolgreich persistierte KILL-Transition materialisiert
  `PaperRiskStateS4V2` mit der exakt zum Kill-Level gehörenden
  `exit_evaluation_allowed`- und `runtime_directive`-Capability.
- Eine unter HARD/EMERGENCY offen gebliebene Paper-Position bleibt im
  autoritativen State OPEN. Jede spätere Fortsetzung folgt L1-D, benötigt eine
  manuelle Restart/Recovery Authorization und gegebenenfalls eine getrennte
  explizite Kill-Deeskalation.

#### 16.2.1 Terminaler Persistenzfehler

Ein durch Disk-full, Permission, File-Descriptor-, Memory- oder vergleichbaren
Ressourcenfehler ausgelöster HARD/EMERGENCY-Fall kann denselben
Control-Journal-Write technisch unmöglich machen. Die Spezifikation behauptet
für diesen physisch unmöglichen Fall keinen dennoch durable KILL-Record.

Für EMERGENCY gilt die unveränderliche Protokollobergrenze
`TERMINAL_ACTION_MAX_MS=100`. Das Runtime-Control-Profil darf
`terminal_write_deadline_ms` nur als Integer `1..100` wählen. Bis zu dieser
Deadline muss entweder der terminale KILL durable sein oder
`TERMINAL_FAILSTOP_ASSERTED` gelten. Dieser Zustand ist exakt dann wahr, wenn
(a) die Broker-Control-Word-CAS `RUNNING|CLOSING→TERMINATING` committed und harte OS-
Termination über den Guardian-PIDFD angefordert wurde, (b) eine der gebundenen
Self-, Guardian- oder Broker-PIDFD-`SIGKILL`-Anforderungen kernel-seitig
angenommen wurde oder (c) nach kernel-erzeugtem
`TerminalKernelTripRequestV2`, Liveness-HUP,
Capability-Verlust, Broker-/Guardian-Stall oder committed Trip keine Broker-
Approval mehr durch den Shim in eine Timerverlängerung umgesetzt wurde, die
bereits armed Kernel-Self-Death-Lease expirierte und das nichtmaskierbare harte Signal kernel-seitig erzeugt
wurde oder (d) der gebundene TSYNC-/Rollenfilter wegen eines verbotenen Task-
oder Writer-Referenzbildungs-Syscalls exakt `SECCOMP_RET_KILL_PROCESS` auf den
gesamten Trading-TGID angewandt hat und der externe Observer die kernel-seitige
Fatal-Action ohne entstandenen Child-/Writer-Halter bestätigt. Variante (c)
benötigt weder Guardian-, Broker- noch Trading-Userspace-Fortschritt; Variante
(d) benötigt weder Self-PIDFD- noch Python-Fortschritt.
Gemessen wird ausschließlich mit einer monotonen Uhr
(`CLOCK_BOOTTIME` für die Linux/WSL-Self-Death-Lease, sonst eine nachgewiesen
äquivalente suspend-aware OS-Clock), niemals mit Wall Clock.

`TERMINAL_ACTION_MAX_MS` ist keine Behauptung, dass das OS den Prozess bis
dahin bereits gereapt hat. Ein Linux-Task in uninterruptible Kernel-I/O kann
ein bereits pending `SIGKILL` erst nach Rückkehr aus diesem Zustand vollenden;
auch eine fremdinitiierte Windows-Prozessterminierung ist asynchron. Deshalb
gilt normativ `TERMINAL_PROCESS_REAP_MAX_MS=UNBOUNDED_BY_PROTOCOL`. Diese
physische Grenze erlaubt keinen weiteren Trading-Pfad: Nach Trip-CAS oder stale
Lease sind Snapshot-Akzeptanz und sämtliche Side Effects irreversibel gesperrt,
die Runtime Session bleibt unclosed und jeder spätere Startup folgt der
Terminal-Gap-Recovery.

Vor Session OPEN müssen vier getrennte Hilfsprozesse und ein nativer Shim
bereit sein:

- `TerminalPersistenceWorkerV8` besitzt den vorreservierten Emergency-Journal-
  Handle, einen vorab geöffneten exklusiven Lifecycle-Append-Handle für die
  beiden Close-Records, einen einmaligen sessiongebundenen Coordinator-Emergency-Lease und
  führt als einziger den potenziell blockierenden Datei-I/O aus. Er besitzt
  allein `OPEN_DURABILITY_GRANT_CONTROL` und darf ausschließlich aus derselben
  erfolgreichen OPEN-Sync-/Directory-Sync-/Readback-/Rebind-Fortsetzung
  `BOOTSTRAP→OPEN_DURABLE_GRANTED` ausstellen;
- `TerminalHandoffRevocationAttestorV1` ist ein separater single-threaded,
  hashgebundener Evidence-Prozess ohne Phase-Control-, Journal-, Runtime-
  Socket- oder Send-Autorität. Er besitzt allein
  `HANDOFF_REVOCATION_GRANT_CONTROL` und darf ausschließlich nach vollständiger
  Listener-Revocation-/Ein-Halter-Evidence
  `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED` ausstellen;
- `TerminalParentGuardianV13` startet und besitzt den Trading-Prozess als
  tatsächliches OS-Child, besitzt dessen harte Kill-Capability und die monotone
  Deadline-Kontrolle und führt weder Journal-, Netzwerk- noch sonstigen
  potenziell blockierenden I/O aus;
- `TerminalNativeTripBrokerV10` ist ein separater single-threaded Native-Prozess,
  alleiniger writable Mapper und Writer des Control Words, alleiniger Besitzer
  des Seccomp-Notification-Listeners, Empfänger von Guardian-Renewals,
  Liveness-HUPs und beiden Worker-ACKs sowie alleiniger Sender von Renewal-
  Approvals, beiden Close-Approvals und Worker-KILL-/PREPARE-/COMMIT-Requests;
  er führt kein Journal-, Datei- oder externes Netzwerk-I/O und keine
  dynamische Codeausführung aus;
- `TerminalKernelLeaseShimV11` ist ein vor allen Python-Threads gestarteter,
  attestierter nativer Thread im Trading-Prozess. Er besitzt ausschließlich
  die bereits armed Self-Death-Lease und eine read-only Control-Word-Map,
  verarbeitet Broker-Renewal-/Close-Approvals und pollt COMMITTED ohne
  Python, GIL, Datei- oder Netzwerk-I/O.

Die Syscall-/Mapping-Autorität wird vor Ready pro Prozess und danach pro Thread
irreversibel getrennt:

- Guardian-Filter erlaubt auf fest gebundenen Deskriptoren nur monotone Clock,
  Control-Word-Read, `sendmsg` für Renewal oder Orderly-Close auf
  `GB_REQUEST`, Guardian-Trip-Eventfd-Read und `recvmsg` auf
  `BG_CLOSE_APPROVAL`
  sowie `pidfd_send_signal`; File-/Network-Open, `dup`, `close`, Credential-Wechsel,
  `fork`, `vfork`, `clone`, `clone3`, `unshare`, `setns`, `execve`, `execveat`
  und `close_range` sind unzulässig;
- Broker-Filter erlaubt nur monotone Clock, `recvmsg` an `GB_REQUEST` und
  `WB_ACK`, `epoll_wait` ausschließlich am vor Ready gebundenen Broker-epoll-
  FD mit festem vorallokiertem Eventbuffer; dessen unveränderliche
  Registrierungen umfassen Trip-Listener, Liveness-Read-Ende, `GB_REQUEST` und
  `WB_ACK`. `poll`/`ppoll`, `epoll_ctl` und `read` auf der Liveness-Pipe bleiben
  gesperrt. Weiter erlaubt sind lock-free CAS in seiner einzigen bestehenden
  writable Control-Word-Map, fixed-FD `sendmsg` an
  `BG_CLOSE_APPROVAL`, `BS_RENEWAL_APPROVAL`, `BS_CLOSE_APPROVAL` und
  `BW_REQUEST`, `SECCOMP_IOCTL_NOTIF_RECV|ID_VALID` ausschließlich am Trip-
  Listener sowie feste
  `write`-Syscalls auf Guardian-/Shim-Eventfds. Er verbietet `mmap`, `mprotect`,
  `pkey_mprotect`, `open`, neue Sockets, `dup`, `close`, Credential-Wechsel,
  `ptrace`, `process_vm_readv`, `process_vm_writev`, `fork`, `vfork`, `clone`,
  `clone3`, `unshare`, `setns`, `execve`, `execveat` und `close_range`;
- Shim-Filter erlaubt nur monotone Clock, `recvmsg` an den exklusiven
  `BS_RENEWAL_APPROVAL`- und `BS_CLOSE_APPROVAL`-FDs,
  Read am Shim-Trip-Eventfd und `timer_settime` für exakt die gebundene Timer-
  ID; Timer Create/Delete, fremde FDs, Files, neue Sockets, `fork`, `vfork`,
  `clone`, `clone3`, `unshare`, `setns`, `execve`, `execveat` und
  `close_range` sind unzulässig. Seine feste Schleife prüft das read-only
  Control Word vor Approval-Verarbeitung und unmittelbar vor `timer_settime`;
  TERMINATING, CLOSED oder CLOSED_FAILSTOP entfernt Timerverlängerung dauerhaft
  aus dem erreichbaren Pfad, COMMITTED erlaubt nach Fingerprintprüfung den
  einmaligen Disarm;
- alle Trading-/Python-Threads dürfen keinen Timer-, Renewal-, Worker-IPC- oder
  Mapping-/Fremdprozess-Rechte-Syscall ausführen; insbesondere sind `mmap` mit
  Schreibrecht auf den Control-Word-Inode, `mprotect`, `pkey_mprotect`,
  `ptrace`, `process_vm_writev` und `/proc/.../mem`-Open verboten. Der
  TSYNC-Basisfilter sperrt ohne
  Flag-Ausnahme `fork`, `vfork`, `clone`, `clone3`, `unshare`, `setns`,
  `execve`, `execveat` und `close_range`. Die Rollenfilter sperren zusätzlich
  `dup`, `dup2`, `dup3`, `pidfd_getfd`, die beiden `F_DUPFD`-Commands,
  sämtliche FD-erzeugenden Syscalls, `sendmsg`/`sendmmsg`,
  `recvmsg`/`recvmmsg`,
  `rt_sigaction`, `rt_sigprocmask`, `sigaltstack`, `signalfd`, `signalfd4` und
  alle nicht als exakte PIDFD-`SIGKILL`-Stufe gebundenen Signal-Erzeuger,
  io_uring, Legacy-AIO und pointerbasierte FD-Multiplexer sowie jeden Liveness-
  Writer-FD-Gebrauch außer exakt `close(trip_liveness_write_fd)`. `write` und
  jeder Datentransfer auf diesem FD enden mit `SECCOMP_RET_KILL_PROCESS`;
  `epoll_ctl` auf dem Liveness-Writer ist ebenfalls gesperrt. Der native
  Trip-Entry beginnt mit dem durch `SECCOMP_RET_USER_NOTIF` intercepteten
  `pidfd_send_signal(...,SIGKILL,NULL,0)` auf dem gebundenen Self-PIDFD; nur
  falls dieser Kernelaufruf zurückkehrt, folgen dieselben Aufrufe auf
  Guardian- und Broker-PIDFDs
  in dieser Reihenfolge und genau ein `close` auf ausschließlich dem
  Liveness-FD. Seccomp prüft nur die skalaren Argumente FD,
  Signal, Nullzeiger und Flags. Jeder rohe Gebrauch einer erlaubten Operation
  kann ausschließlich Trading, Renewal oder Approval fail-safe beenden oder
  Liveness-HUP erzeugen;
- alle gebundenen FDs sind `CLOEXEC`; die vollständige Duplikations-/Transfer-/
  Kernel-Registrierungsoberfläche des Liveness-Writers ist nach Abschnitt 7.8
  gesperrt und vor OPEN negativ geprüft. Der Broker→Worker-FD ist in keinem
  Trading-/Python-Thread geöffnet. Filter-BPF, TGID, vollständige TID-/Rollen-/
  Startzeitmenge, TSYNC-Ergebnis, gemeinsame `KCMP_FILES`-Identität,
  Session-Cgroup-/PID-Namespace-Fingerprint, erlaubte Syscall-/Argumentmatrix,
  vollständige FD-/FDINFO-Inventur, Liveness-Pipe-Enden/-Inode/-Leerzustand,
  Self-/Guardian-/Broker-PIDFD-Ziele und -Startzeiten,
  Trip-Listener-FD/-Inode/-Owner, Notification-Filter/-Tupel,
  `TerminalTradingSignalEnvelopeV1`, alle sechs Close-Kanal-FDs/-Inodes/-
  Richtungen samt finaler Connect-/Accept-Provenance, `SO_PEERCRED`,
  `SO_PASSCRED=0`, autoritativem `SO_PASSRIGHTS=0` auf jedem finalen
  Empfangsendpunkt, eingefrorener Empfänger-TID-/Files-Table-Topologie,
  vollständiger Rights-Freeze-TSYNC-Abdeckung und anschließendem
  `getsockopt==0`, `scm_fds: 0`, leerem Queue-, FD-/OFD-/Lock-Zustand vor
  Senderfreigabe sowie absentem Controlbuffer,
  Memfd-Create-Flags/-Seal-Transitionen und vollständige
  `/proc/<pid>/maps`-Evidenz sind Teil von Session OPEN und Capability-
  Fingerprint.

Die kontinuierliche Guardian-Bindung ist Kernel-erzwungen und
plattformabhängig exakt wie folgt:

- Linux/WSL: Das Trading-Child setzt unmittelbar nach `fork`/`spawn`
  `prctl(PR_SET_PDEATHSIG, SIGKILL)`, prüft danach die unveränderte
  Guardian-PID samt `/proc`-Startzeit erneut, und der Guardian hält einen
  passenden `pidfd` mit stabilen Credentials und erfolgreicher Signal-0-
  Capability-Probe. Der Native Shim armed zusätzlich vor Ready einen
  nichtmaskierbaren POSIX-Prozesstimer auf `CLOCK_BOOTTIME` mit
  `SIGEV_SIGNAL/SIGKILL` und absoluter Expiry. Jede vom Broker atomar
  akzeptierte und an den Shim weitergereichte Guardian-Renewal setzt diese
  höchstens auf `now+25 ms`; ohne Approval erzeugt der Kernel das
  Kill-Signal auch bei Guardian-`SIGSTOP`, Suspend oder Userspace-Stall. Nach
  Ready verbietet ein vorab attestiertes minimales Native-/Seccomp-Profil dem
  Guardian Credential-/Capability-Wechsel, jede Prozess-/Thread-Erzeugung und
  blockierende
  Syscalls; ein Child-Filter verbietet das Löschen oder Ändern von
  `PDEATHSIG`, Timer, Signal, Credential-/Capability-Bindung und Reparenting-/
  Namespace-Operationen. Ein Parentwechsel im Setup-Fenster verhindert Ready.
- Windows: Ein Job Object mit `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, nicht
  vererbbarem exklusivem Guardian-Handle und deaktiviertem Breakaway schützt
  nur gegen Guardian-Tod beziehungsweise Handle-Schluss. Es schützt nicht
  gegen einen lebenden suspendierten Guardian und belegt keine synchrone
  Reap-Deadline. Daher ist `WINDOWS_ENFORCED_SESSION_SUPPORTED=NO`, bis eine
  separat spezifizierte und unabhängig reviewte suspend-aware Kernel-Self-
  Death-Lease ohne schedulable Userspace-Callback dieselben Invarianten
  erfüllt. Job Object oder Waitable Timer allein genügen nicht; ohne diesen
  Capability-Nachweis wird Session OPEN fail closed abgelehnt.

Andere Plattformen benötigen eine separat spezifizierte äquivalente
Parent-Death- **und** suspend-aware Kernel-Self-Death-Primitive. Ein bloßer
Python-Heartbeat, eine Polling-Datei, ein nur vom Guardian kontrollierter Timer
oder eine freiwillige Child-Prüfung gilt nicht als äquivalent. Der Guardian
prüft Kill-Handle, Credentials und Zielidentität vor jeder Renewal. Bei
Capability-Verlust erneuert er die bereits armed Lease nicht und fordert
zusätzlich sofort harte Termination an. Guardian-Tod, `SIGSTOP`, Suspend,
Native-Stall, verpasste Capability-Prüfung, Reparenting oder PID-Reuse führt
dadurch spätestens mit der bestehenden Expiry zu
`TERMINAL_FAILSTOP_ASSERTED` durch pending hard kill; kein ausgefallener
Guardian muss sich selbst beenden, damit die Lease wirkt.

Die Plattformgrenze stützt sich auf die primären API-Verträge für Linux-
[`timer_create`](https://man7.org/linux/man-pages/man2/timer_create.2.html),
Linux-[Seccomp User Notification](https://docs.kernel.org/userspace-api/seccomp_filter.html),
Linux-[`seccomp_unotify(2)`](https://man7.org/linux/man-pages/man2/seccomp_unotify.2.html),
Linux-[`unix(7)`](https://man7.org/linux/man-pages/man7/unix.7.html),
Linux-[`SO_PASSRIGHTS`-Upstream-Commit](https://github.com/torvalds/linux/commit/77cbe1a6d8730a07f99f9263c2d5f2304cf5e830),
Linux-[BPF LSM](https://docs.kernel.org/bpf/prog_lsm.html),
Linux-[`BPF_MAP_TYPE_SK_STORAGE`](https://docs.kernel.org/bpf/map_sk_storage.html),
Linux-[LSM-Hook-Definitionen](https://github.com/torvalds/linux/blob/v6.18/include/linux/lsm_hook_defs.h),
Linux-[Socket-Syscall-Reihenfolge](https://github.com/torvalds/linux/blob/v6.18/net/socket.c),
Windows-[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
und Windows-[`TerminateProcess`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess).
Diese Quellen belegen Signal-/Termination-Anforderung, aber keine universelle
synchrone Reap-Obergrenze; die spätere Implementierung muss Kernel, Header und
Capability-Evidenz des tatsächlich gebundenen Systems erneut prüfen.

Der Trading-Prozess besitzt keinen Persistence-Worker-IPC-FD. Ausschließlich der
separate Broker kommuniziert über die vorab geöffneten nonblocking
`BW_REQUEST`-/`WB_ACK`-`SOCK_SEQPACKET`-Kanäle mit dem Worker. KILL-, PREPARE-
und COMMIT-Request sowie beide ACKs besitzen disjunkte feste Protocol-Structs;
die vollständige skalare Seccomp- und Userspace-Payloadmatrix aus Abschnitt
7.8.1 ist bindend. Beide Kanäle sind nach Start der finalen Broker-/Worker-
Prozesse verbunden, per `SO_PEERCRED` gebunden und besitzen
`SO_PASSCRED=0`; auf `BW_REQUEST` und `WB_ACK` besitzen die finalen
Empfangsendpunkte zusätzlich attestiert `SO_PASSRIGHTS=0` und `scm_fds: 0`.
Jeder Receive verwendet `msg_control=NULL` und `msg_controllen=0`.
Der Trading-Prozess führt im EMERGENCY-Pfad selbst keinen Datei-,
Flush-, Snapshot- oder Worker-IPC-Syscall aus. Session OPEN bindet Worker-,
Broker-, Guardian-, Shim- und Child-Identitäten/Ready-Nonces samt PID/
Startzeiten, OS-Lease-Typ/-Identifier, Credentials-/Capability-Fingerprint,
Native-Broker-/Shim-Fingerprints, Kernel-Timer-ID, Clock/Signal, Lease-Nonce,
Trading-Self-/Guardian-/Broker-PIDFDs samt Zielen, Startzeiten und Signalproben,
initiale Heartbeat-Sequenz/Expiry,
Control-Word-Memfd/Initialwert/Create-Flags/jede Seal-Transition und sämtliche
Mapping-Rechte, alle sechs verbundenen Runtime-Kanäle aus Abschnitt 7.8.1,
`TerminalTripLivenessPipeV1`-Enden/-Inode/-Capacity/-Exklusivbesitz,
dauerhaft leeren Kanal und vollständiges Write-Verbot, Guardian-/Shim-Eventfds,
`TerminalKernelTripRequestV2`-Listener-FD/-Inode/-Owner,
NEW_LISTENER-/WAIT_KILLABLE_RECV-Filterhash,
`TerminalTradingSignalEnvelopeV1`, TID-Vererbungs- und nachgelagertes
TSYNC-Ergebnis, interceptetes
Syscall-Tupel und verbotenes CONTINUE/ADDFD,
Broker→Worker-IPC, Seccomp-/FD-
Argumentmatrix, Capability-Profil-ID/-Fingerprint, Heartbeat-Intervall, Lease-
Maximum, Trip-/Signal-/Fail-stop-Budgets, Termination-Latch-Deadline und
`terminal_process_reap_deadline_claimed=false`.

Bei EMERGENCY ruft der Trading-Prozess ohne vorgelagerte Mutation den nativen
`terminal_trip()`-Entry auf. Sein erster Kernelaufruf ist die Self-PIDFD-
`SIGKILL`-Anforderung; der Kernel erzeugt daraus die nicht rücknehmbare
`TerminalKernelTripRequestV2`-Notification und blockiert den Request-TID. Der
externe Broker linearisiert daraufhin nach TERMINATING und fordert selbst den
Child-PIDFD-Kill an. Nur falls der erste Kernelaufruf zurückkehrt, folgen ohne
Retry Guardian-PIDFD-`SIGKILL`, Broker-PIDFD-
`SIGKILL` und zuletzt der Entzug des einzigen Liveness-Writers. Ein gesunder
Broker behandelt HUP als Trip; bei ausgefallenem Broker bleiben Approvals aus.
Wird der Request-TID nach Kernelannahme angehalten, arbeitet der externe Broker
ohne ihn weiter; bei Whole-child-Stop ebenso. Stirbt der Broker, bleiben
Approvals aus und der bereits armed Timer läuft aus. Vor Kernelannahme wird kein
Trip behauptet; ein Whole-child-Stop auch an dieser Grenze lässt den Timer ohne
Shim-Fortschritt auslaufen.
Die erfolgreiche Broker-CAS auf dem gemeinsamen Control Word ist der monotone
globale Klassifikationszeitpunkt und der irreversible
`TERMINATION_LATCHED`-Nachweis. Die CAS stoppt Broker-Renewals normativ; die
Broker-Eventfds benachrichtigen Guardian und Shim, und der Guardian fordert über
den gebundenen PIDFD harte Termination an. Selbst bei verlorenen Notifications
oder Broker-Crash nach der CAS erzeugt der Broker keine Approval mehr, der Shim
liest TERMINATING und der bereits armed Timer erzeugt ohne Verlängerung das
harte Signal. Stirbt oder stallt der Broker vor der CAS, bleiben ebenfalls
Approvals aus und dieselbe armed Lease läuft ab. Spätestens an der aufgelösten
Deadline muss daher der Guardian harte Termination angefordert oder der Kernel-
Lease-Timer das Signal erzeugt haben. Weil nur der isolierte Worker im
blockierenden Journal-I/O stehen kann, hängt die Termination-Anforderung weder
von Rückkehr dieses Syscalls noch von Python-Cleanup, GIL, Trading-Thread-
Scheduling oder Log-Flush ab.

Tatsächliches Reaping wird nicht zeitlich behauptet; fachliche Fortsetzung ist
durch das globale Control Word und synchrone Pre-Side-
Effect-Prüfungen ausgeschlossen. Worker, Broker und Guardian verwenden eine
vorab festgelegte Control Event ID; ein verspätet doch durable gewordener
Worker-Write bleibt dadurch genau derselbe, später journal-first zu
reconciliierende KILL.

Der Worker akzeptiert höchstens einen Request der gebundenen Session vom exakt
in OPEN per `SO_PEERCRED` und PID-Startzeit gebundenen Broker-Peer, mit
`msg_control=NULL`, `msg_controllen=0`, ohne `MSG_CTRUNC` und nur bei exakt
passender erwarteter Transaction
Sequence, Journal Head und State-Fingerprint. Zusätzlich muss sein eigener
Acquire-Load der read-only Control-Word-Map exakt TERMINATING, Trip-Sequenz 1
und dieselbe im Request enthaltene Renewal-Sequenz/Broker-Generation zeigen.
Nach Aktivierung des Emergency-Lease darf der Trading-Prozess keinen eigenen
Coordinator-Write mehr beginnen. Gleiche Event ID mit abweichender Payload,
fehlender Control-Word-Bindung oder ein zweiter Request werden fail closed
verworfen.

Die verbindliche Reihenfolge lautet:

1. vor jeder Persistenzoperation weitere Snapshot-/Intent-/Execution-
   Verarbeitung stoppen und ohne lokale Mutation `terminal_trip()` aufrufen;
   der erste Kernelaufruf Self-PIDFD-`SIGKILL` erzeugt die Seccomp-
   Notification. Nur bei Rückkehr folgen Guardian-PIDFD, Broker-PIDFD und der
   atomare FD-Slot-Entzug mit genau einem Liveness-`close`. Ein Pipe-Write
   existiert nicht; eine zweite Notification derselben Session ist fail-safe
   idempotent und erzeugt keinen zweiten globalen Trip;
2. der Broker verarbeitet eine gültige Trip-Notification, `POLLHUP`, `POLLERR`
   oder das unmögliche `POLLIN`
   der Liveness-Pipe vor jeder weiteren Renewal
   und führt genau einmal `RUNNING|CLOSING→TERMINATING` aus. Nur diese neue erfolgreiche
   CAS setzt global `EMERGENCY/TERMINATION_LATCHED`, erzeugt die beiden best-
   effort Guardian-/Shim-Notifications und exakt einen fixed-size KILL-Request
   mit vorab bestimmter Control Event ID an den Worker. „already TERMINATING“
   erzeugt weder Notification noch Worker-Request; jeder andere State ist ein
   fail-closed Konflikt. Liveness-/Eventfd-/IPC-Fehler ändern weder Control Word
   noch Timer; es gibt keine Pipe-Payload-Allokation und keinen Close-Retry;
3. meldet der Worker rechtzeitig einen durable Journal-Commit, das Ergebnis nur
   als Evidence übernehmen; Snapshot-Materialisierung ist für die sofortige
   Safety-Sperre/Termination-Anforderung nicht erforderlich und erfolgt gegebenenfalls später
   journal-first;
4. blockiert oder scheitert Worker/IPC beziehungsweise bleibt das ACK aus,
   niemals weitertraden, den Trip herabstufen, Guardian oder Self-Death-Lease
   deaktivieren oder über
   die Deadline hinaus warten; best-effort Reason/Exit Code nur auf einen
   bereits offenen nichtblockierenden Diagnosekanal ausgeben;
5. bei keinem EMERGENCY-Zweig einen `RUNTIME_SESSION_CLOSE_COMMIT` voraussetzen.
   Ein vorhandenes CLOSE-PREPARE bleibt unclean. Der
   Vertrag garantiert `TERMINAL_FAILSTOP_ASSERTED` spätestens 100 ms nach dem
   lokalen Request-Zeitpunkt beziehungsweise einem früher erkannten Capability-
   Verlust, ausdrücklich nicht das Process Reaping.

Der vor Loop-Eintritt durable `RUNTIME_SESSION_OPEN` macht das Fehlen des CLOSE-COMMIT
beim nächsten Startup sichtbar, ohne vom fehlgeschlagenen KILL-Write
abzuhängen. Eine unclosed Session setzt effektiv `TERMINAL_UNKNOWN`, blockiert
Entry und Exit-Auswertung und benötigt eine neue
`IU4RestartRecoveryAuthorizationV1` mit
`operation=RECONCILE_TERMINAL_GAP`.

Nach wiederhergestellter Persistenz arbeitet
`RECONCILE_TERMINAL_GAP` strikt journal-first unter exklusivem Coordinator- und
Lifecycle-Recovery-Lock:

1. alten Persistence Worker als beendet oder durch einen höheren
   Fencing-Token dauerhaft vom Journal ausgeschlossen beweisen; bis dahin ohne
   Mutation blockieren;
2. vollständige Journal-Kette ab dem in Session OPEN gebundenen Journal Head
   read-only validieren, bevor der Snapshot als aktuell oder stale
   klassifiziert wird;
3. nach einem hashgültigen durable terminalen KILL-Control-Record dieser
   Session suchen; sein Journal-Commit ist auch bei fehlendem oder stale
   Snapshot fachlich autoritativ;
4. existiert genau ein solcher Record, dessen `state_after` idempotent als
   Snapshot materialisieren, danach Journal/State vollständig reconciliieren
   und exakt diese Control Event ID binden; kein zweiter KILL ist zulässig;
5. existiert kein solcher Record, muss der letzte durable Journal Head exakt
   zum letzten committeten Snapshot passen; erst dann genau einen konservativen
   EMERGENCY-KILL-Control-Record append-only committen und dessen `state_after`
   materialisieren;
6. existieren mehrere widersprüchliche terminale Records, ein ungültiger
   Journal-Tail oder keine eindeutige State-before-Basis, ohne Mutation
   blockieren; insbesondere keinen Ersatz-KILL schreiben;
7. erst nach erfolgreicher Reconciliation
   `TERMINAL_GAP_RECONCILIATION` mit Session-ID, Fehler-/Log-Evidence,
   verwendetem Control Event, Journal Head und State-Fingerprint anhängen.

Die Operation startet keinen Loop. Ein Crash nach durable KILL-Journal, aber
vor Snapshot Replace, wiederholt beim nächsten autorisierten Versuch nur die
Materialisierung desselben `state_after`. Ein Crash nach Snapshot Replace, aber
vor Gap Record, bindet beim nächsten Versuch ebenfalls denselben KILL. Eine
spätere Deeskalation und Wiederaufnahme benötigen jeweils die bereits
vorgeschriebenen getrennten manuellen Entscheidungen und eine neue Restart
Authorization.

### 16.3 Profil-/Authorization-Ablauf

Ein Ablauf während offener Position setzt einen Entry-Blocker und ein
Monitoring-Alert. Er erzeugt keinen automatischen Market Exit und keinen
unjournaled State-Wechsel.

---

## 17. Audit, Monitoring und Compatibility Projection

### 17.1 Autoritative Auditfelder

Jeder ENFORCED-Entscheidungsdatensatz enthält mindestens:

- IU4-Modus und Owner;
- Repository Commit;
- Activation- und gegebenenfalls Restart/Recovery-Authorization-ID;
- Owner Epoch, Authority Generation/Commit Anchor, Ledger Tip, Runtime
  Session und Handoff-Manifest-ID;
- Economics-, Throttle- und Runtime-Control-Identitäten;
- Atomic Transaction Sequence, Event-ID und State Fingerprint;
- Snapshot-, Tick- und Intent-Identität;
- Control Action und Control Reason;
- Adapter Status, Action und Reason;
- Entry-/Exit-/Veto-/KILL-/PROGRESS-Typ;
- `entry_allowed`, `exit_evaluation_allowed`, `runtime_directive` und
  deterministische Reason Codes;
- Runtime-Session-/Parent-Guardian-/Native-Trip-Broker-ID, Guardian-/Broker-/
  Child-PID samt Startzeiten,
  OS-Lease-Typ/-Identifier, Credentials-/Capability-Fingerprint, Lease-Nonce,
  Native-Shim-/Kernel-Timer-Identität, Trading-Self-/Guardian-/Broker-PIDFD-
  Identitäten und Signalstatus,
  Control-Word-State/Trip-/Renewal-Sequenzen, Memfd-Create-Flags/jede Seal-
  Transition/Mapping-Rechte, `TerminalTradingSignalEnvelopeV1`, alle sechs
  verbundenen Close-/Renewal-Kanalidentitäten mit Connect-/Accept-Provenance,
  `SO_PEERCRED`, `SO_PASSCRED=0`, `SO_PASSRIGHTS=0`, Set/Get-Reihenfolge,
  Empfänger-TID-/Files-Table-Topologie, Rights-Freeze-TSYNC-Return/-Filterhash,
  finale Rollenfilterhashes, `TerminalSeccompListenerHandoffV2`-Quell-/Ziel-
  FD-/PIDFD-/ACK-/Ptracer-/Dumpable-/Halteridentitäten,
  `TerminalRuntimeSocketLSMGuardV3`-Program-/Map-/Link-/Pin-/Cgroup-
  Identitäten, eingefrorene Phase-/Config-Map, alle drei Control-Socket-
  Cookies/Tags/Owner-TGID/TID/Startzeiten/Cgroups,
  `socket_shutdown`-Hook und BPF-CMPXCHG-Instruktionsnachweis, socketlokale
  Tag-/Seal-Zustände, verweigerte
  `file_receive`-/`socket_setsockopt`-Versuche und OPEN→Release-Reihenfolge,
  **post-filter** `getsockopt==0`, `scm_fds: 0`, Queue-/FD-/OFD-/Lock-Status,
  einmalige `LISTENER_HANDOFF→LISTENER_RECEIVED`-,
  `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED`- und
  `HANDOFF_REVOKED_GRANTED→BOOTSTRAP`-Zeiten, vollständige Revocation-
  Attestor-Evidence, durable OPEN-/Sync-/Directory-Sync-/Readback-Zeit,
  einmalige `BOOTSTRAP→OPEN_DURABLE_GRANTED`- und
  `OPEN_DURABLE_GRANTED→RELEASED`-Zeit,
  Senderfreigabezeit, Bootstrap-Abbruch-/Zerstörungsstatus, Controlbuffer-
  Status, Prequeue-`EPERM`-
  und Defense-in-Depth-Autoclose-Nachweis, Liveness-Pipe-Enden/-Leerzustand/-Fallbackstatus und Notification-
  Eventfd-Identitäten,
  Broker→Worker-
  Peerbindung, Seccomp-/Capability-Profilfingerprint, letzte monotone
  Capability-Probe und Heartbeat-Sequenz/Expiry, Seccomp-Trip-Notification-ID/
  Kernelannahme-/Broker-Receive-/Validation-Zeit und letzter erlaubter Timer-Expiry,
  Self-/Guardian-/Broker-PIDFD-Signalzeiten/-Returnklassen,
  Liveness-FD-Entzug-/HUP-Zeit und, sofern
  erreicht, globale Broker-CAS-Klassifikationszeit, aufgelöste Termination-
  Latch-Deadline sowie getrennten
  Reap-Status ohne Reap-Deadline-Behauptung sowie Close-PREPARE-/Broker-CLOSED-/
  Close-COMMIT-Identitäten und Zeitpunkte;
- Authority-COMMIT-Completion-Provenance und, bei
  `RECOVERED_AFTER_PREPARE`, Completion-Authorization-/Consumption-ID;
- Projection Status.

Economic Values werden als kanonische Decimal Strings ausgegeben.

### 17.2 Legacy-Kompatibilitätsausgabe

- ist eindeutig `non_authoritative_projection=true` markiert;
- enthält die autoritative Transaction Event ID;
- wird niemals als Recovery-Input verwendet;
- rechnet keine Economics neu;
- darf nach Crash aus dem Journal idempotent wiederhergestellt werden.

### 17.3 Monitoring

Monitoring und Health Report prüfen im ENFORCED-Modus mindestens:

- Authorization-Gültigkeit;
- Profil-/Commit-Bindung;
- Journal-/Snapshot-Konsistenz;
- Projection Lag;
- S2/Account/Throttle/Loss Cluster/S4 Fingerprints;
- Entry-Quote- und Progress-Cursor-Fingerprint;
- Owner Epoch, Authority Generation/Commit Anchor, vollständige Ledger-Kette,
  offene PREPAREs, Runtime-Session und Handoff-Konsistenz;
- Authority-COMMIT-Root und lückenlose Journal-Abstammung des aktuellen State;
- Parent-Guardian-/Native-Trip-Broker-Ready-Status, OS-Lease-/Kill-Capability,
  Guardian-/Broker-/Child-Identität, armed Kernel-Self-Death-Timer, Native-
  Shim-Fingerprint, Trading-Self-/Guardian-/Broker-PIDFD-Ziele/-Startzeiten/
  Signalproben, Control-Word-State
  und Broker-CAS-Sequenzen, Memfd-Create-Flags/Seal-Transitionen/Mapping-Rechte,
  `TerminalTradingSignalEnvelopeV1` samt unveränderter Signalmaske,
  WAIT_KILLABLE_RECV und Listener-Receive-Fehlerstatus, alle sechs verbundenen
  Kanäle samt `SO_PEERCRED`, vollständiger Empfänger-TID- und Rights-Freeze-
  Filterabdeckung, finaler Rollenfilter- und Endpoint-Ownership-Abdeckung,
  post-filter `SO_PASSRIGHTS=0`, dauerhaftem `scm_fds: 0`,
  fehlendem Controlbuffer, unveränderter Queue-/FD-/FDINFO-/OFD-/Lock-Inventur und
  letztem Rights-Reject-Resultat, Liveness-Pipe-Enden/-Leerzustand/-HUP-Status und
  beide Notification-Eventfds, Broker→Worker-/Worker→Broker-Peerbindungen,
  Seccomp-Trip-Listener/-Notification und skalare Seccomp-/Userspace-
  Autoritätsmatrix, Capability-Envelope-Fingerprint sowie
  Close-FSM-Phase CLOSING/PREPARE/BROKER_CLOSED/COMMIT/COMMITTED/FAILED,
  Heartbeat-Intervall `10 ms`, Alter/Expiry der letzten Capability-Probe
  höchstens `25 ms`, monotone suspend-aware Clock, Trip-/Signal-/Fail-stop-
  Budgets, Termination-Latch-Deadline `1..100 ms`, Trip-/pending-Signal-/
  Reap-Status und unclosed Session-/Terminal-Gap-Status;
- Authority-COMMIT-Completion-Provenance und die Zulässigkeit der
  Clean-Genesis-Erststartausnahme;
- vollständige S4V2-Felder und terminale Capability-Invarianten;
- Entry- und Exit-Fähigkeit getrennt;
- Resource-/I/O-Fehler;
- unbekannte Schemas;
- Legacy-exit-only-Status.

`missing_allowed` ist für ENFORCED-Kernstate kein PASS.

---

## 18. Fehlerklassen und stabile Reason Codes

Bestehende präzisere Reason Codes bleiben erhalten. Neue Integrationsfehler
verwenden mindestens folgende stabile Familien:

| Reason Code | Bedeutung |
|---|---|
| `PEE_IU4_RUNTIME_MODE_INVALID` | expliziter Modus ungültig |
| `PEE_IU4_RUNTIME_PROFILE_INVALID` | Operational Profile fehlt/ist unzulässig |
| `PEE_IU4_RUNTIME_BINDING_MISMATCH` | Commit/Profile/State-Bindung abweichend |
| `PEE_IU4_AUTHORIZATION_SCHEMA_UNSUPPORTED` | Authorization V1/unknown für ENFORCED |
| `PEE_IU4_AUTHORIZATION_EVIDENCE_MISMATCH` | R3-/Release-Evidenz stimmt nicht |
| `PEE_IU4_RESTART_AUTHORIZATION_REQUIRED` | manueller Restart-Vertrag fehlt |
| `PEE_IU4_RESTART_AUTHORIZATION_CONSUMED` | Authorization-ID ist bereits durable verbraucht |
| `PEE_IU4_RECOVERY_AUTHORIZATION_MISMATCH` | Recovery-Vertrag passt nicht zum Pre-State |
| `PEE_IU4_LIFECYCLE_LEDGER_CONFLICT` | Sequence, Hash-Kette, Event-ID oder Owner-Ableitung widerspricht |
| `PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE` | Genesis/Handoff/Migration/Materialisierung ist nur teilweise publiziert |
| `PEE_IU4_AUTHORITY_PREPARE_INCOMPLETE` | PREPARE besitzt keinen gültigen Target State und COMMIT |
| `PEE_IU4_AUTHORITY_PREPARE_COMPLETION_REQUIRED` | offener PREPARE benötigt exakt gebundene Completion-Authorization |
| `PEE_IU4_AUTHORITY_COMMIT_MISMATCH` | COMMIT, PREPARE und vollständiger Target-State-Fingerprint widersprechen sich |
| `PEE_IU4_AUTHORITY_ROOT_MISMATCH` | Atomic Journal/Snapshot stammt nicht vom committed Authority-Target ab |
| `PEE_IU4_GENESIS_PROVENANCE_INVALID` | DIRECT/RECOVERED-Provenance oder ihre Consumption-Bindung ist widersprüchlich |
| `PEE_IU4_POST_COMPLETION_RESTART_REQUIRED` | ein durch PREPARE-Completion erzeugter Genesis-COMMIT versucht ohne neue RESTART_ONLY-Freigabe zu starten |
| `PEE_IU4_LIFECYCLE_EXTENSION_INVALID` | Ledger-Extension nach autorisiertem Pre-attempt Tip enthält fremde Records |
| `PEE_IU4_RUNTIME_SESSION_UNCLEAN` | Runtime Session besitzt weder gültigen CLOSE-COMMIT noch Gap-Reconciliation; CLOSE-PREPARE oder Broker-CLOSED allein bleiben unclean |
| `PEE_IU4_TERMINAL_PERSISTENCE_FAILED` | terminaler Control-Write war wegen Ressourcen-/I/O-Fehler unmöglich |
| `PEE_IU4_TERMINAL_GUARDIAN_INVALID` | Parent Guardian, Kernel-Self-Death-Lease, Kill-Capability, monotone Clock oder Ready-Bindung fehlt/ist ungültig |
| `PEE_IU4_TERMINAL_GUARDIAN_LOST` | Guardian starb, stoppte oder verlor Lease/Kill-Capability nach Session OPEN; Kernel-Lease muss `TERMINAL_FAILSTOP_ASSERTED` auslösen |
| `PEE_IU4_TERMINAL_CONTROL_WORD_CONFLICT` | Terminal-State, Trip-/Renewal-Sequenz oder CAS-Linearization ist ungültig; keine Renewal oder fachliche Fortsetzung zulässig |
| `PEE_IU4_TERMINAL_TRIP_REQUEST_INVALID` | Seccomp-Notification-Filter, Listener-Ownership, Syscall-Tupel, ID-Validierung oder monotone Broker-CAS ist nicht exakt belegt |
| `PEE_IU4_TERMINAL_SIGNAL_ENVELOPE_INVALID` | Signalmaske/-disposition, TID-Vererbung, WAIT_KILLABLE_RECV oder die Sperre späterer Signaländerungen ist nicht exakt belegt |
| `PEE_IU4_RUNTIME_SESSION_CLOSE_INCOMPLETE` | CLOSE-PREPARE besitzt keinen gebundenen Broker-CLOSED-Nachweis und durable CLOSE-COMMIT; Session bleibt unclean |
| `PEE_IU4_RUNTIME_SESSION_CLOSE_TRANSPORT_FAILED` | Close-Send/-Receive endete mit Short/invalid, Peer-HUP oder dauerhaftem Transportfehler und die FSM eskalierte |
| `PEE_IU4_RUNTIME_SESSION_CLOSE_TIMEOUT` | eine absolute Close-Phasendeadline lief ohne gültigen Zustandsfortschritt ab |
| `PEE_IU4_RUNTIME_SESSION_CLOSE_PROTOCOL_INVALID` | Type, Richtung, Länge, feste Peeridentität, Session, Nonce, Phase, State oder Fingerprint widerspricht der gebundenen Close-Matrix |
| `PEE_IU4_TERMINAL_CHANNEL_ANCILLARY_INVALID` | SO_PASSCRED ist aktiv, Empfänger-TID-/Freeze-TSYNC-Abdeckung fehlt, der post-filter SO_PASSRIGHTS-Wert ist nicht exakt 0, Sender wurde vor dem finalen Snapshot freigegeben, Prequeue-Reject liefert nicht EPERM, scm_fds/Queue ist nicht leer, Bootstrap-Zerstörung ist unvollständig, der Receive-Controlbuffer ist nicht leer, MSG_CTRUNC/Ancillary wurde akzeptiert oder eine FD-/OFD-/Lock-Referenz überlebt |
| `PEE_IU4_TERMINAL_HANDOFF_REVOCATION_UNPROVEN` | Revocation-/Ein-Halter-Evidence ist unvollständig oder der Attestor-Grant wurde zu früh, fremd oder mehrfach angefordert |
| `PEE_IU4_TERMINAL_OPEN_DURABILITY_UNPROVEN` | OPEN-Sync, Directory-Sync, Readback oder Chain-/Fencing-Rebind fehlt oder der Persistence-Grant wurde nicht aus derselben erfolgreichen Commit-Fortsetzung erzeugt |
| `PEE_IU4_TERMINAL_PHASE_GRANT_INVALID` | Phase, Control-Socket/-Cookie, Owner-TID/-Startzeit/-Cgroup, `how`, Grantreihenfolge oder Guard-Grant-Konsum widerspricht der sechsstufigen FSM |
| `PEE_IU4_TERMINAL_TRIP_CHANNEL_INVALID` | Liveness-Pipe, drei PIDFDs, Seccomp-Listener, Eventfds, sechs verbundene Runtime-Kanäle, SO_PEERCRED-/Peer-/Richtungsbindung oder exklusive FD-Autorität stimmen nicht |
| `PEE_IU4_TERMINAL_TRIP_DELIVERY_UNPROVEN` | Kernel-Notification/Broker-CAS/Kill oder die Self→Guardian→Broker→Liveness-Close-Rückkehrfolge ist nicht vollständig belegt |
| `PEE_IU4_TERMINAL_CONTROL_MAP_INVALID` | Memfd-Create-Flags, initiale/intermediäre/finale Seal-States, Prozess-Mapping-Rechte oder alleinige Broker-Writer-Autorität stimmen nicht |
| `PEE_IU4_TERMINAL_CAPABILITY_ENVELOPE_INVALID` | System, Profil, Last-/Fault-Manifest oder eine Einzelgrenze der endlichen Capability-Zertifizierung stimmt nicht |
| `PEE_IU4_TERMINAL_FAILSTOP_REAP_PENDING` | Trip-CAS plus Termination-Anforderung oder expirierte Kernel-Lease belegt den Fail-stop; tatsächliches OS-Reaping ist noch nicht bestätigt, Trading und Clean Close bleiben unzulässig |
| `PEE_IU4_PLATFORM_SELF_DEATH_UNSUPPORTED` | Plattform besitzt keinen attestierten suspend-aware Kernel-Self-Death-Vertrag; Session OPEN ist unzulässig |
| `PEE_IU4_TERMINAL_JOURNAL_AMBIGUOUS` | terminaler Journal-Tail oder State-before ist nicht eindeutig reconciliierbar |
| `PEE_IU4_TERMINAL_GAP_RECONCILIATION_REQUIRED` | unclean Session muss konservativ als EMERGENCY materialisiert werden |
| `PEE_IU4_CONTROL_PROFILE_REQUIRED` | Runtime-Control-Profil fehlt |
| `PEE_IU4_CONTROL_PROFILE_MISMATCH` | Control-Identität abweichend |
| `PEE_IU4_CONTROL_ACTION_INVALID` | Action passt nicht zu State/Intent |
| `PEE_IU4_HANDOFF_LEGACY_EXIT_ONLY` | valide Altposition, keine PEE-Entries |
| `PEE_IU4_HANDOFF_DUAL_OPEN_CONFLICT` | Legacy und Atomic gleichzeitig OPEN |
| `PEE_IU4_HANDOFF_GENESIS_REQUIRED` | fehlender State ohne attestierte Genesis |
| `PEE_IU4_HANDOFF_SAFETY_CONFLICT` | S4/Loss/Throttle/Cooldown nicht verlustfrei abbildbar |
| `PEE_IU4_HANDOFF_OWNER_EPOCH_INVALID` | Owner Epoch und State-Heads widersprechen sich |
| `PEE_IU4_S4_SCHEMA_UNSUPPORTED` | S4V1/unknown kann terminalen Atomic-V2-State nicht repräsentieren |
| `PEE_IU4_TICK_PRE_ACCEPT_REJECTED` | Snapshot wurde vor mutierender Akzeptanz fail closed abgewiesen |
| `PEE_IU4_ENTRY_BLOCKED` | Entry durch autoritativen Guard abgewiesen |
| `PEE_IU4_EXIT_RECOVERY_REQUIRED` | Exit benötigt Coordinator Recovery |
| `PEE_IU4_ENTRY_QUOTE_REQUIRED` | vollständiges committed Entry Quote fehlt |
| `PEE_IU4_PROGRESS_CONFLICT` | Snapshot-/Tick-Cursor widerspricht Journal |
| `PEE_IU4_PROJECTION_LAG` | Commit vorhanden, Projektion nicht aktuell |
| `PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED` | Atomic V1/unknown nicht aktivierbar |
| `PEE_IU4_RESOURCE_EXHAUSTED` | Memory/Disk/FD/OS-Ressource erschöpft |

Resource-Fehler werden nicht als Daten-, Paritäts- oder Policy-Fehler
fehlklassifiziert. Treten sie vor der Akzeptanzgrenze auf, wird der Snapshot
ohne Journal-/Cursor-Mutation `REJECTED_PRE_ACCEPT`. Nichtterminale Fehler
blockieren Entries; Exits bleiben soweit autoritativer State sicher lesbar und
der Snapshot anschließend vollständig akzeptierbar ist zulässig.
System-/Resource-Fehler, die gemäß L1C `EMERGENCY` auslösen, beenden dagegen den
Prozess und starten keinen automatischen Exit-Versuch. Kann der KILL wegen
desselben Fehlers nicht persistiert werden, gilt ausschließlich der
Runtime-Session-/Terminal-Gap-Vertrag aus Abschnitt 16.2.1; fehlende
Persistenz wird weder als erfolgreicher KILL noch als Clean Shutdown behauptet.

---

## 19. Dateiscope der späteren Implementierung

### 19.1 Neue Dateien

Voraussichtlich erforderlich und durch ein späteres Mandat einzeln zu
bestätigen:

- `live_l1/core/paper_iu4_runtime_gate.py`;
- `live_l1/core/paper_execution_control.py`;
- `live_l1/core/terminal_parent_guardian.py` als tatsächlicher OS-Parent/
  Supervisor mit Parent-Death-Bindung, monotoner Deadline, Heartbeat und harter
  Child-Termination sowie gebundenen Trading-Self-/Guardian-/Broker-PIDFDs;
- `live_l1/native/terminal_native_trip_broker.c` als separater attestierter
  single-threaded Prozess und einziger Control-Word-Writer sowie einziger
  Besitzer des Seccomp-Trip-Listeners, Empfänger beider Worker-ACKs und Sender
  von Renewal-/Close-Approvals sowie Worker-KILL-/PREPARE-/COMMIT-Requests;
- `live_l1/native/terminal_kernel_lease_shim.c` als minimaler attestierter
  Linux/WSL-Nativteil für `TerminalSelfKillEntryV4`,
  `TerminalTradingSignalEnvelopeV1`, den
  `SECCOMP_RET_USER_NOTIF`-Trip-Entry, dauerhaft leere
  `TerminalTripLivenessPipeV1`, Self→Guardian→Broker-PIDFD-Signalfallback und
  einmaligen Liveness-`close`, read-only Control-Word-Prüfung,
  exklusive Timer-Renewal,
  `CLOCK_BOOTTIME`-Self-Death-Timer und nichtmaskierbares Kill-Signal; andere
  Plattformimplementierungen benötigen einen separaten Review- und Capability-
  Nachweis;
- `live_l1/tools/validate_terminal_lease_capability.py` plus native Fault-
  Fixture und externer Signal-/Side-Effect-Observer für das exakt definierte
  `TerminalLeaseCapabilityProfileV14`;
- `live_l1/core/terminal_persistence_worker.py` als isolierter Besitzer des
  potenziell blockierenden Emergency-Journal-I/O;
- `live_l1/state/iu4_lifecycle_ledger.py` mit exklusivem Writer und
  read-only Reconciliation für Authority PREPARE/COMMIT, Consumption und
  Runtime Sessions;
- versionierte Handoff-/Genesis-/Restart-Recovery-Verträge und deren
  read-only Loader;
- fokussierte Tests für Guardian, Native Trip Broker, Lease Shim und
  Persistence Worker;
- versionierte, erst nach fachlicher Freigabe anzulegende ENFORCED-Profil- und
  Authorization-Schema-Artefakte.

### 19.2 Gezielte Änderungen

- `live_l1/tools/safe_launch.py`;
- `live_l1/core/loop.py`;
- `live_l1/core/execution.py` nur für die belegte Control-Extraktion und
  Legacy-Delegation;
- `live_l1/core/paper_iu4_startup_gate.py` für additive V2-Verträge;
- `live_l1/core/paper_iu4_adapter.py` für additive Request V2/Control Actions;
- `live_l1/state/paper_atomic_coordinator.py` für additive State/Transaction V2;
- `live_l1/state/paper_artifacts.py` für
  `EntryEconomicsQuoteArtifactV1`, `PaperRiskStateS4V2` und deren
  Fingerprint-/Schema-Verträge;
- `live_l1/state/models.py` für die additive vollständige Legacy-S4-
  Repräsentation, sofern die belegte Handoff-Projektion sie benötigt;
- `live_l1/state/loss_cluster.py` nur für pure, wiederverwendbare
  Transition-Funktionen;
- `live_l1/state/state_store.py` nur für vollständige explizite Handoff-
  Projektion einschließlich `loss_today`/`anomaly_counter` und den belegten
  Ausschluss von Schema-1-Persistenz in ENFORCED;
- Shadow Runtime/Observation Gate nur zur type-sicheren Delegation an die eine
  Runtime-Gate-Autorität;
- Recovery-, Reconciliation-, Schema- und Monitoring-Tools, soweit sie Atomic
  V2 und den neuen Owner lesen müssen;
- dazugehörige `tests/live_l1`-Module.

### 19.3 Grundsätzlich zu bewahren

Ohne separat nachgewiesenen Vertragsgap werden nicht neu implementiert oder
dupliziert:

- `paper_economics.py`;
- S2 V2/Paper Account/Trade V2-Verträge; das neue Entry-Quote-Artefakt ist
  additiv und ändert diese Verträge nicht;
- bestehende Canonical Price Carrier;
- bestehender Entry Throttle;
- Adapter-/Coordinator-V1-Verträge für bestehende Tests und Evidenz.

### 19.4 Ausgeschlossen

- Strategien und Signaldefinitionen;
- GS, `engine/` und `run_engine/`;
- Research-/RCC002-Pipelines;
- Exchange-/Broker-Code;
- Production Credentials;
- historische Trade-Neubewertung;
- große Refactorings außerhalb des Execution Seam;
- automatische Archivierung oder Löschung user-eigener Dateien.

---

## 20. Implementierungsreihenfolge

Nach R3-PASS und separater Freigabe erfolgt die Umsetzung nur in folgenden,
einzeln prüfbaren Paketen:

1. **I1 — Characterization und Pure Control Extraction**
   Noch keine ENFORCED-Verkabelung; OFF/SHADOW-Parität muss vollständig grün
   sein.
2. **I2 — Lifecycle Ledger, Runtime Gate und Authorization V2**
   Activation- und Restart/Recovery-Loader, Trust Boundaries, Profile Binding
  sowie selbstreferenzfreie Authority PREPARE/COMMIT, durable Consumption,
  PREPARE-Completion, Runtime Sessions, Terminal Parent Guardian V13, separater
  Native Trip Broker V10, Kernel-Self-Death-Lease-Shim V11, atomisches Control
  Word V3, `TerminalTripLivenessPipeV1`, `TerminalTradingTaskTopologyV2`,
  `TerminalTradingSignalEnvelopeV1`, `TerminalSelfKillEntryV4`,
  `TerminalKernelTripRequestV2`, `TerminalSeccompListenerHandoffV2`,
  `RuntimeSessionCloseProtocolV8`, `TerminalRuntimeChannelProvisioningV6`,
  `TerminalRuntimeSocketLSMGuardV3`, `TerminalRuntimeSocketGuardPhaseV3`,
  `TerminalHandoffRevocationAttestorV1`, `TerminalPersistenceWorkerV8`,
  Self-/Guardian-/Broker-PIDFD-Fallback, exakte Memfd-Seal-
  Zustandsmaschine, prozessgetrennte Trip-/Renewal-/Close-/Worker-Kanäle,
  drei disjunkte Phase-/Grant-Control-Sockets, Capability-Envelope V14 und
  vollständige Handoff-Klassifikation; Adapter
  bleibt deaktiviert.
3. **I3 — Atomic State/Transaction V2**
   S4V2, Entry Quote, Progress Cursor, Loss Cluster, Tick-/Control-Ordnungsraum,
   PROGRESS, ENTRY_VETO, Migration und Fault Injection; noch kein aktiver
   Loop-Consumer.
4. **I4 — Adapter Request V2**
   explizite Control Actions und autonome Exits auf synthetischem State.
5. **I5 — Active Execution Seam**
   vollständige mode-abhängige Delegation aller Side Effects im bestehenden
   Loop; ENFORCED weiterhin durch fehlende Betriebsautorisation gesperrt.
6. **I6 — Recovery, Monitoring und Projection**
   L1-D-konformer manueller Restart/Recovery, Owner-Epoch-Handoffs,
   journal-first Terminal-Gap-Reconciliation, Authority-Root-Prüfung,
   version-aware Tools und Replay der Projektionen.
7. **I7 — Vollständige lokale und Workstation-Validierung**.
8. **I8 — Unabhängige Review- und Aktivierungsentscheidung**.

Kein Paket darf durch einen großen Sammelcommit ersetzt werden. Jede Korrektur
erzeugt eine neue eindeutige Code-/Evidence-Identität.

---

## 21. Pflicht-Testmatrix

### 21.1 Modus und Owner

- OFF ruft ausschließlich Legacy auf.
- SHADOW ruft Legacy plus read-only Observer auf.
- ENFORCED ruft für PEE-Positionen niemals `apply_paper_execution()` auf.
- ENFORCED ruft niemals Legacy `persist_state()`, Legacy Loss-Cluster-Mutation,
  Legacy Trade-Logging oder passive Legacy-Sidecars auf.
- Jeder `ACCEPTED` Snapshot erhält genau eine Cursor-besitzende Tick-
  Transaktion, außer eine terminale KILL-Eskalation verwirft ihn vor durable
  Tick-Commit; `REJECTED_PRE_ACCEPT` erhält keine.
- Control- und Lifecycle-Records können dieselbe ursächliche Tick ID binden,
  sind aber keine zweite Tick-Transaktion.
- unbekannter Modus und ungültiges Operational Profile fail closed.
- kein Pfad erreicht Legacy-Fallback-Quantity `1.0` in ENFORCED.

### 21.2 Control-Parität

- LONG/SHORT TP;
- LONG/SHORT SL;
- LONG/SHORT Time-stop exakt an und unmittelbar vor der Grenze;
- Opposing intent;
- HOLD;
- autonome Exits ohne synthetisches Intent;
- Legacy-exit-only verwendet ausschließlich die positiongebundene explizite
  Control Binding und niemals Runtime-Defaults;
- unveränderte OFF/SHADOW Actions und Reasons auf zertifizierten Inputs.

### 21.3 Decimal und Economics

- raw source decimal text erreicht PEE ohne Float-Roundtrip;
- Entry Quantity entspricht exakt dem autorisierten Decimal Quote;
- OPEN persistiert das vollständige Entry Quote; CLOSE liest genau dieses
  Artefakt und ruft keine erneute Entry-Autorisierung auf;
- fehlende oder abweichende Quote-Felder blockieren Settlement;
- Fees und Slippage werden genau einmal angewandt;
- LONG/SHORT Settlement ist reproduzierbar;
- jede Economic-Ausgabe ist aus committed Decimal-Artefakten ableitbar.

### 21.4 Guards

- Gate closed und SOFT blockieren Entries, lassen im laufenden Loop sichere
  Exits zu;
- HARD beendet den Loop vor weiterer Snapshot-/Exit-Verarbeitung;
- EMERGENCY beendet den Prozess und startet nicht automatisch neu;
- S4V1 ist in Atomic V2 abgelehnt; S4V2 bildet NONE/SOFT/HARD/EMERGENCY exakt
  auf Entry-, Exit-Evaluations- und Runtime-Directive-Capabilities ab;
- CLOSE plus SOFT committed einmal atomar; CLOSE/ENTRY_VETO plus terminalem
  KILL folgt der in Abschnitt 13.4 definierte Pre-/Post-Journal-Ordnungsfall;
- Tick-Risk-Matrix erlaubt ausschließlich `NONE_TO_SOFT`; `SOFT_TO_NONE` und
  jede andere Deeskalation im Tick werden abgelehnt;
- Account-, Throttle- und Loss-Cluster-Reasons haben deterministische Priorität;
- Loss-Cluster ENTRY_VETO dekrementiert exakt einmal;
- andere Entry-Denials verändern S2, Account, Throttle und Loss Cluster nicht.

### 21.5 Authorization und Profile

- fehlend, malformed, unknown field, V1, falscher Trust Anchor;
- not-yet-valid und expired;
- Commit-, Symbol-, Coordinator-, Economics-, Throttle-, Control-, R3- und
  Evidence-Mismatch;
- ablaufende Authorization blockiert neue Entries, nicht Exits;
- SHADOW-only oder `runtime_activated=false` Profile werden abgelehnt.
- Restart ohne `IU4RestartRecoveryAuthorizationV1` wird abgelehnt;
- Recovery mit falschem Verantwortlichen, Log-/Environment-Manifest,
  Pre-State, Operation oder Trust Anchor wird abgelehnt;
- Activation Authorization allein kann Recovery nicht auslösen.
- Restart-/Recovery-Authorization wird vor Freigabe genau einmal durable im
  Lifecycle Ledger verbraucht; erneute Verwendung derselben ID wird abgelehnt;
- Crash vor Consumption lässt die Authorization unverbraucht, Crash danach
  verlangt eine neue Authorization.
- Consumption verschiebt nur den Ledger Tip; Authority Generation/Anchor und
  State-Fingerprint bleiben unverändert und die erlaubte Startup-Attempt-
  Extension wird vollständig validiert;
- fremder Zwischenrecord, falscher Pre-attempt Tip oder falsche Startup-
  Attempt-ID blockieren Restart und Recovery.
- offener Authority-PREPARE akzeptiert ausschließlich
  `COMPLETE_AUTHORITY_PREPARE` mit exakter PREPARE-/Generation-/Core-/Commit-
  Bindung; alle anderen Operationen werden abgelehnt;
- PREPARE-Fertigstellung materialisiert fehlenden Target State oder validiert
  den vorhandenen, schreibt genau einen passenden COMMIT, startet keinen Loop
  und verlangt für den späteren Start eine neue Authorization;
- ausschließlich ein Genesis-COMMIT mit `completion_provenance=DIRECT`, ohne
  Completion-Consumption in seiner PREPARE→COMMIT-Kette und ohne frühere
  Runtime Session derselben Generation **und** mit exakter Gleichheit von
  aktueller Prozessinstanz, Genesis-Operation-Attempt und in-memory Nonce-
  Preimage erhält genau einmal die eng begrenzte Clean-Genesis-
  Erststartausnahme;
- Crash/Prozessende/`exec` nach DIRECT-COMMIT und vor Session OPEN, neue
  Prozessinstanz, PID-Reuse, Boot-ID-/Startzeit-/Launch-ID-Mismatch, falscher
  Attempt oder verlorene/abweichende Continuation Nonce lassen den COMMIT als
  Authority bestehen, verweigern aber die Ausnahme und verlangen neue
  `RESTART_ONLY` plus Consumption;
- ein Genesis-COMMIT mit `RECOVERED_AFTER_PREPARE` wird ohne neue
  `RESTART_ONLY`-Authorization und passenden `RESTART_AUTH_CONSUME` abgelehnt;
  eine Activation Authorization oder die bereits verbrauchte Completion-
  Authorization genügt nicht;
- `COMPLETE_AUTHORITY_PREPARE` für Genesis schreibt im Consumption Record exakt
  `source_authority_commit_anchor=NONE`,
  `source_authority_generation_id=NONE`, Target Generation und PREPARE-
  Event-ID/-Fingerprint; fehlende, leere oder abweichende Sentinels werden
  abgelehnt;
- gefälschtes `DIRECT` bei vorhandenem Completion-Consumption sowie
  `RECOVERED_AFTER_PREPARE` ohne exakt gebundenes Consumption werden als
  widersprüchliche Provenance abgelehnt;
- falscher PREPARE, Target-Pfad/-Schema, Core-Fingerprint, Generation,
  COMMIT-Typ oder bereits bestehender COMMIT wird abgelehnt.

### 21.6 Handoff

- Legacy FLAT + Atomic FLAT;
- Legacy FLAT + Atomic OPEN Recovery;
- Legacy OPEN + Atomic FLAT exit-only;
- Legacy OPEN + Atomic OPEN conflict;
- S4-Kill-Konflikte wählen nie den niedrigeren Level;
- spätester Cooldown und Loss-Cluster-/Throttle-Heads bleiben erhalten;
- `loss_today`, `anomaly_counter` und alle übrigen S4V2-Felder werden in beide
  Richtungen verlustfrei und ohne Defaults abgebildet;
- `LEGACY_TO_PEE` und `PEE_TO_LEGACY` ohne vollständiges Handoff Manifest
  werden abgelehnt;
- stale Legacy Risk State nach PEE Owner Epoch wird abgelehnt;
- Clean Genesis bindet den vollständigen Atomic-V2-State und leeres Journal;
- Genesis, beide Handoffs und V1→V2-Migration verwenden PREPARE, Target-Core-
  Fingerprint, materialisierten Target State und COMMIT ohne Hash-Zyklus;
- PREPARE allein aktiviert keinen neuen Owner; erst COMMIT ändert Authority
  Generation und Owner Epoch;
- `state_before` der ersten Atomic-V2-Transaktion entspricht exakt dem im
  Authority-COMMIT gebundenen Target-State-Fingerprint samt initialer
  Sequence/Journal-Head-Basis;
- jede spätere Tick-/Control-Transition bewahrt `authority_generation_id` und
  `authority_prepare_record_fingerprint` exakt;
- manipulierte Generation/PREPARE-Bindung, eine intern lückenlose Journalkette
  mit falschem Genesis-/Handoff-Root und ein nicht vom COMMIT erreichbarer
  aktueller Snapshot werden abgelehnt;
- fehlender, korrupter und unbekannter State;
- Prozess beendet sich nach Legacy-exit-only Close und verlangt Neustart.

### 21.7 Fault Injection

Unterbrechung mindestens:

- vor und nach durable `RESTART_AUTH_CONSUME` einschließlich erneuter
  Verwendung derselben und abweichender Payload unter gleicher ID;
- bei `ATOMIC_GENESIS` vor PREPARE, nach durable PREPARE, vor Snapshot Replace,
  nach Snapshot Replace und vor/nach COMMIT;
- bei `LEGACY_GENESIS` und beiden Handoff-Richtungen nach Source-
  Reconciliation, nach durable PREPARE, vor Ziel-State-Publikation, nach
  Ziel-State-Publikation und vor/nach COMMIT;
- bei `ATOMIC_V1_TO_V2_MIGRATION` vor/nach PREPARE, Target-Publikation und
  COMMIT sowie bei `RECOVERY_MATERIALIZATION` vor/nach jedem durable Write;
- bei `COMPLETE_AUTHORITY_PREPARE` nach Consumption, bei fehlendem/vorhandenem
  Target State, nach Target-Publikation und vor/nach COMMIT; jeder Crash vor
  COMMIT verlangt eine neue Authorization, erzeugt aber keine neue Generation;
- bereits durable COMMIT nach Crash wird nie dupliziert und die
  Completion-Operation startet keinen Loop;
- nach recovered Genesis-COMMIT werden direkter Loop-Start, Wiederverwendung
  der Completion-Authorization und Start nur mit Activation Authorization
  abgelehnt; erst neue `RESTART_ONLY` plus exaktes Consumption erlaubt den
  Startup;
- manipulierte Genesis-Provenance, fehlende/abweichende NONE-Sentinels und eine
  angeblich direkte Genesis mit früherer Runtime Session werden abgelehnt;
- Crash, Prozessende und `exec` exakt nach DIRECT-Genesis-COMMIT und vor
  Session OPEN: Der nächste Prozess darf weder mit wiederverwendeter PID noch
  mit gelesener COMMIT-Payload die Ausnahme nutzen; nur neue `RESTART_ONLY`
  samt Consumption erlaubt den Start. Die unverändert lebende Original-
  Prozessinstanz mit richtigem Attempt und Nonce-Preimage darf dagegen exakt
  einmal fortsetzen;
- bei konkurrierendem Lifecycle-Writer, doppelter Event-ID, Sequence- und
  Hash-Chain-Abweichung;
- bei nicht-ownerveränderndem Append: Ledger Tip ändert sich, Authority
  Generation/Anchor und gebundener State bleiben exakt stabil;
- vor Journal Write;
- nach durable Journal Write;
- vor Snapshot Replace;
- nach Snapshot Replace;
- vor und nach Audit Projection;
- bei jedem OPEN-, CLOSE-, PROGRESS-, KILL- und ENTRY_VETO-Pfad;
- bei kombinierten CLOSE+SOFT-, CLOSE+terminal-KILL- und
  ENTRY_VETO+terminal-KILL-Ordnungsfällen;
- bei Pre-Accept Binding-, Schema-, State- und Authorization-Fehlern: kein
  Journal-Record, kein Cursor-Fortschritt, keine fachliche Mutation;
- bei Disk-full, Permission, File Descriptor und Memory-/Resource-Fehlern;
- Resource-/I/O-Fehler vor `RUNTIME_SESSION_OPEN`: kein Loop-Start;
- KILL-Write-Fehler nach `RUNTIME_SESSION_OPEN`: innerhalb höchstens `100 ms`
  kernel-erzeugter `TerminalKernelTripRequestV2` und Broker-
  `RUNNING|CLOSING→TERMINATING`-CAS, akzeptierter
  Self-/Guardian-/Broker-PIDFD-`SIGKILL` oder Liveness-HUP mit ausbleibender
  Approval, danach keine erfolgreiche
  Timerverlängerung,
  `TERMINAL_FAILSTOP_ASSERTED` durch PIDFD-Kill-Anforderung oder kernel-
  erzeugtes Signal, kein Session CLOSE-COMMIT; nächster Startup meldet
  `TERMINAL_UNKNOWN` und bleibt gesperrt;
- Worker/IPC fällt aus, während Guardian, Broker und Shim gesund bleiben:
  Broker-Trip-CAS verhindert trotzdem jede Renewal; Guardian liest TERMINATING
  und fordert Termination an. Derselbe Test mit vollem, geschlossenem oder
  absichtlich nicht gelesenem Guardian-/Shim-Notification-Eventfd muss über
  Control Word/Timer identisch fail-stop enden;
- Broker stallt oder stirbt vor Trip-CAS beziehungsweise nach Renewal-CAS:
  keine weitere Approval erreicht den Shim, der Request-TID bleibt nach
  Notification im Kernel blockiert und die armed Lease expirieren innerhalb
  des gebundenen Budgets;
- Memfd ohne exakt `MFD_CLOEXEC|MFD_ALLOW_SEALING`, mit initialem Seal ungleich
  0, fehlgeschlagenem/abweichendem `F_ADD_SEALS`, verfrühtem `F_SEAL_SEAL`,
  vorhandenem `F_SEAL_WRITE`, fehlendem finalen Pflicht-Seal, einer zweiten
  writable Map, writable Map in Guardian/Trading/Worker oder unbekanntem
  `/proc`-Mapper verhindert OPEN. Nach `F_SEAL_FUTURE_WRITE` scheitert jeder
  neue writable `mmap`-Versuch;
- Trip-/Renewal-Race wird in beiden atomaren Linearization-Reihenfolgen geprüft:
  Renewal-vor-Trip lässt höchstens die bereits gebundene 25-ms-Restlaufzeit,
  Trip-vor-Renewal lässt die Renewal-CAS scheitern; keine Ausführung erreicht
  `TERMINATING→RUNNING/CLOSING/CLOSED/COMMITTED` oder einen zweiten Worker-Request;
- unmittelbar nach kernel-erzeugter `TerminalKernelTripRequestV2`-Notification
  und vor Broker-Receive wird ausschließlich der Request-TID angehalten. Bei
  gesundem Broker muss dieser ohne Request-TID-Fortschritt nach TERMINATING
  linearisiert und selbst den Child-PIDFD-Kill angefordert haben. Derselbe
  Trial mit Broker-Stall verlangt ausbleibende Approvals und Lease-Expiry;
- für jedes blockierbare Signal wird getrennt unmittelbar vor Broker-Receive
  und nach erfolgreichem Broker-Receive geprüft, dass es pending bleibt und
  keinen Handler-/Fallback-Return erzeugt. Negative post-Ready-Aufrufe von
  `rt_sigaction`, `rt_sigprocmask`, `sigaltstack`, `signalfd*`, `kill`,
  `tkill`, `tgkill`, `rt_sigqueueinfo` und äquivalenten Signaloperationen
  müssen den TGID per `SECCOMP_RET_KILL_PROCESS` beenden. `SIGKILL` muss
  terminieren; `SIGSTOP` muss den ganzen TGID stoppen und die armed Lease ohne
  Approval expirieren lassen;
- sobald der Trip-Listener readable/HUP/ERR meldet, werden Erfolg,
  `NOTIF_RECV`-`ENOENT`, `EINTR`, `EAGAIN`, ABI-/Short- und unbekannte Fehler
  getrennt injiziert. Jeder Fall muss ohne Fortsetzung des Request-TID nach
  TERMINATING beziehungsweise CLOSED_FAILSTOP linearisiert werden und weitere
  Renewals/Approvals ausschließen;
- jeder `read`, `write`, vectored I/O, `splice`, `vmsplice`, `tee`, `sendfile`
  oder äquivalente Datentransfer irgendeines Trading-Threads oder Brokers auf
  der Liveness-Pipe endet vor FD-Auflösung mit
  `SECCOMP_RET_KILL_PROCESS`. Der externe Observer belegt null Pipe-Bytes, null
  Pipe-Pages und null temporäre Writer-Referenzen. Kein Trading-Thread besitzt
  den Worker-IPC-FD;
- ein `terminal_trip()` unter maximaler gebundener Broker-Poll-/Pipe-Lock-
  Konkurrenz wird mit Fehlern aller drei PIDFD-Signale geprüft. Innerhalb
  `5 ms` muss bei gesundem Broker Liveness-HUP als Trip-CAS linearisiert sein;
  bei gestopptem oder totem Broker darf keine weitere Approval entstehen;
- erfolgreiche Self-PIDFD-Anforderung, Self-Fehler mit erfolgreichem Guardian-
  PIDFD, Self-/Guardian-Fehler mit erfolgreichem Broker-PIDFD und Fehler aller
  drei Signale mit Liveness-Close/HUP werden getrennt geprüft. Jeder
  zurückkehrende Fehler einschließlich `EINTR`, `ESRCH`, `EPERM`, `EBADF` und
  unbekanntem `errno` muss ohne Retry die nächste Stufe erreichen. Close-
  `EINTR` wird als freigegebener FD ohne Close-Retry geprüft; Broker verarbeitet
  HUP/ERR/POLLIN vor jeder Renewal;
- nach OPEN wird unter den produktiven TSYNC-/Rollenfiltern und gleichzeitig
  erzwungenen Fehlern aller drei PIDFD-Signale jeder Prozess-/Thread-/Files-Table- und Writer-
  FD-Erzeugungs-/Referenzbildungsweg aus Abschnitt 7.8 versucht. Kein Versuch
  darf ein Child,
  einen TID, eine neue FD-Nummer, eine abweichende Files-Table, einen
  `SCM_RIGHTS`-Transfer, eine io_uring-Registrierung oder einen epoll-Halter des
  Writers erzeugen. Exakt `SECCOMP_RET_KILL_PROCESS` muss den gesamten TGID
  beenden; der dadurch verlorene letzte Writer muss Broker-HUP innerhalb
  `5 ms` als Trip-CAS linearisiert und jede weitere Approval verhindern. Ein
  separater Fehler-aller-drei-PIDFDs-/Liveness-
  Close-Trial muss weiterhin Broker-HUP innerhalb `5 ms` linearisiert
  zeigen; TID-, FD-/FDINFO- und Cgroup-Inventur belegen beide Pfade;
- falsches Self-/Guardian-/Broker-PIDFD-Ziel, PID-/Startzeitabweichung, fehlende
  Signal-0-Probe, andere Signalnummer, nicht-null `siginfo`, andere Flags,
  zusätzliche Pipe-Writer oder irgendein erlaubter Pipe-Write verhindern OPEN.
  Roher Close beziehungsweise eines der drei gebundenen Signale durch irgendeinen
  Trading-Thread kann ausschließlich fail-safe wirken;
- beim geordneten Ende bleibt das Trading-Child durch
  RUNNING→CLOSING, CLOSE-PREPARE und CLOSING→CLOSED hindurch alive und gegatet.
  Erst durable CLOSE-COMMIT, gültiger CommitAck und CLOSED→COMMITTED erlauben
  Timer-Disarm und Child-Exit; das anschließende HUP ist erwartete Evidenz.
  Crash/Trip nach PREPARE aber vor CLOSED, COMMIT-Writefehler nach CLOSED und
  Crash vor COMMIT müssen unclosed bleiben und beim Folgestart Terminal-Gap-
  Recovery erzwingen. HUP vor CLOSED muss TERMINATING linearisiert haben;
- für jeden der sechs Close-Typen und beide Approval-Empfänger werden getrennt
  `EINTR`, `EAGAIN|EWOULDBLOCK`/Queue-full, Send-0, positiver Short-Send,
  `EMSGSIZE`, `EPIPE`, `ECONNRESET`, Receive-Short/-Oversize/-TRUNC/-CTRUNC,
  falscher Type/Peer/Richtung/State/Nonce/Session/Fingerprint, Peer-Close/HUP,
  Timeout, Prozesscrash, verlorene Nachricht sowie byteidentisches und
  konfliktäres Duplikat injiziert. Jeder Retry verwendet dieselben Bytes und
  dieselbe absolute Deadline; PREPARE und COMMIT mutieren jeweils höchstens
  einmal. Vor CLOSED endet jeder Fehler in TERMINATING ohne Renewals; nach
  CLOSED in CLOSED_FAILSTOP ohne Approval. Verlorener CommitAck bei bereits
  durablem COMMIT ist beim Startup clean, aber in derselben Runtime nicht
  COMMITTED; verlorene Approvals konvergieren nach COMMITTED über die
  read-only Polls von Shim und Guardian;
- für `TerminalSeccompListenerHandoffV2` werden Yama-Modi ungleich
  `ptrace_scope=1`, falsche Real-Credentials, Broker-PID/-Startzeit-/PIDFD-
  Abweichung, falscher oder mehrfacher `PR_SET_PTRACER`, falscher reservierter
  Trading-Quell- oder Broker-Ziel-FD, `pidfd_getfd` mit jedem abweichenden
  skalaren Argument, zweiter Aufruf, unerwarteter Rückgabe-FD, fehlendes/
  fremdes/mehrfaches Eventfd-ACK, Trading-Closefehler, Halt/Crash jedes
  Beteiligten an jeder Grenze, fehlgeschlagene `PR_SET_PTRACER=0`-/
  `PR_SET_DUMPABLE=0`-Revocation und ein zweiter Listener-Halter injiziert.
  Jeder Fall muss ohne Runtime-Socket und ohne irgendeinen `sendmsg`-
  Ausnahmeweg den Startup derselben Session terminal abbrechen. Positiv muss
  genau der eine nicht-socketartige Listener-`pidfd_getfd`-Empfang mit
  `LISTENER_HANDOFF→LISTENER_RECEIVED` passieren, danach genau der Broker-
  Ziel-FD als alleiniger Halter verbleiben;
- für `TerminalRuntimeSocketGuardPhaseV3` werden fehlendes `file_receive`- oder
  `socket_shutdown`-Attach, jeder falsche der drei Control-Sockets/-Cookies/-
  Owner-TIDs/-Startzeiten/-Cgroups, falsches `SHUT_WR`, `SHUT_RD` oder
  `SHUT_RDWR`, vertauschte Guard-/Attestor-/Persistence-Autoritäten,
  oder doppelte Transitionen, jeder Userspace-`BPF_MAP_UPDATE_ELEM`-, mmap-,
  Lookup+Update- und `BPF_F_LOCK`-Versuch, von `0` abweichende Create-Flags,
  fehlendes `BPF_MAP_FREEZE`, nicht geschlossenen Create-FD, fehlendes
  `BPF_OBJ_GET|BPF_F_RDONLY`, abweichende Value-Größe/-Ausrichtung sowie ein
  nicht zu `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` übersetztes Programm injiziert.
  Nur Attestor-`SHUT_WR` nach vollständiger Handoff-Revocation darf
  `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED`, nur Guard-`SHUT_RD` aus diesem
  Grant `HANDOFF_REVOKED_GRANTED→BOOTSTRAP`, nur Persistence-`SHUT_WR` aus der
  erfolgreichen durable-OPEN-Fortsetzung
  `BOOTSTRAP→OPEN_DURABLE_GRANTED` und nur Guard-`SHUT_RDWR` aus diesem Grant
  `OPEN_DURABLE_GRANTED→RELEASED` mit `errno=EINPROGRESS` erzeugen. Richtige
  Guard-Aufrufe vor dem jeweiligen Grant müssen ohne Mutation scheitern; kein
  Grantzustand öffnet selbst das zugehörige Gate. Der zugrunde liegende
  Socket-Shutdown darf nie ausgeführt werden;
- für jeden der sechs Kanäle werden fehlender/falscher BPF-LSM-Tag oder Link,
  fremde/racing Connects, falsche `SO_PEERCRED`-/PID-Startzeit, aktiviertes
  `SO_PASSCRED`, nichtleerer Receive-Controlbuffer, fehlgeschlagenes/
  abweichendes `SO_PASSRIGHTS`-Set/Get, fremdes oder nach FD-Lookup angehaltenes
  `setsockopt(SO_PASSRIGHTS=1)`, SCM_RIGHTS-/Runtime-Socket-`pidfd_getfd`-/`/proc/fd`-
  Akquisition, einzelne/multiple `SCM_RIGHTS`-CMSGs vor/während/nach LSM-Seal,
  jedem Freeze-TSYNC und finalen Rollenfilter sowie nach durablem OPEN vor
  Release, partielle TSYNC-Abdeckung, TID-Race, versteckte Endpoint-
  Duplikation/-Übertragung, Queueing nach einem bestandenen Snapshot sowie ein
  bis `SCM_MAX_FD` angebotene FDs injiziert. Vor Ready muss jede Abweichung am
  globalen `file_receive`-/`socket_setsockopt`-/`socket_sendmsg`-Hook mit
  `-EPERM`, im Rollenfilter mit `SECCOMP_RET_KILL_PROCESS` oder im
  verbindlichen post-Filter-Snapshot enden; dann müssen alle Endpunkte zerstört,
  Referenzen freigegeben und der Startup ohne Same-Session-Retry abgebrochen
  werden. Post-Ready muss jeder Rights-Send auch bei
  vor `recvmsg` per `SIGSTOP` angehaltenem oder gecrashtem Empfänger exakt
  `EPERM` liefern und unretried terminal enden. Nach Sender-Close/-Crash
  bleiben Receive Queue, `scm_fds: 0`, FD-, FDINFO-, OFD- und Lock-Inventur
  byteidentisch. Der getrennte Defense-in-Depth-Trial umgeht den Guard
  künstlich und verlangt `MSG_CTRUNC` plus Kernel-Autoclose, ohne dass der
  Rollenfilter des Empfängers `close` erlauben muss;
- der Worker lehnt jeden KILL-Request bei Control Word
  RUNNING/CLOSING/CLOSED/COMMITTED/CLOSED_FAILSTOP, falscher Trip-/
  Renewal-Sequenz, falscher Broker-Generation oder fremdem Peer ohne Journal-
  Mutation ab; exakt TERMINATING plus gebundener Broker-Request wird höchstens
  einmal akzeptiert. Spiegelbildlich akzeptiert er den disjunkten Close-Commit-
  Request nur bei CLOSED und schreibt ausschließlich den gebundenen CLOSE-
  COMMIT; Type-/Peer-/Nonce-/PREPARE-/CLOSED-Abweichungen und Wiederholung
  bleiben mutationslos;
- falsche Session, gebundene `SO_PEERCRED`-/PID-Startzeit, Kanal-/Pipe-/Eventfd-Inode, Heartbeat-/Renewal-
  Sequenz, Capability Proof, Control-Word-State/Alignment/Lock-free-Status,
  Memfd-Create-Flags/Seal-Transitionen/Mapping-Rechte, einer der drei PIDFDs oder Seccomp-/
  FD-Argumentmatrix verhindern OPEN beziehungsweise Renewal;
- Parent Guardian und Native Lease Shim verwenden ausschließlich die gebundene
  suspend-aware monotone Clock; Wall-Clock-Sprünge ändern weder 10-ms-
  Heartbeat noch 25-ms-Expiry oder 100-ms-Termination-Latch-Deadline;
- Guardian-`SIGKILL`, normaler Guardian-Tod, `SIGSTOP`, Suspend und Native-
  Stall nach Session OPEN lassen die bereits armed Linux/WSL-Self-Death-Lease
  ohne Guardian-Selbstdiagnose expirieren und erzeugen `SIGKILL`;
- Verlust der Linux-PIDFD-/Credential-Capability verhindert die nächste
  Renewal und fordert zusätzlich sofort harte Termination an; stale,
  rückläufige oder übersprungene Heartbeat-Sequenz verhindert jede weitere
  Snapshot-Akzeptanz und jeden Side Effect;
- gesamtes Trading-Child-`SIGSTOP` stoppt auch den Shim und lässt den armed
  Timer expirieren. Ein vor Trip nur im uninterruptible I/O stehender Trading-
  Thread darf bei gesundem Broker/Shim weiter Renewal erhalten, kann aber
  keinen Side Effect ausführen und muss nach Rückkehr den Gate-Entry passieren.
  Erfolgt die kernel-seitige Trip-Notification vor dem I/O, blockiert ihr TID;
  Broker-CAS oder bei Broker-Ausfall ausbleibende Approval verhindert jede
  Timerverlängerung und das Signal wird pending;
  eine feste Reap-Dauer wird nie als PASS-Kriterium gemessen;
- die vollständigen `10_000` Trials je Capability-Szenario und die 32
  per-Startup-Probe-Trials je Pflichtszenario verwenden exakt Lastgrenzen,
  Phasenabdeckung, Observer und Einzelbudgets aus Abschnitt 7.8.2. Jeder
  Einzelverstoß, fehlende Messpunkt oder Environment-Mismatch verhindert OPEN;
- auf Windows verhindern fehlender independently reviewed suspend-aware
  Kernel-Self-Death-Capability-Nachweis, bloßes Job Object oder bloßer Waitable
  Timer Session OPEN; Job-Handle-Schluss/Tod bleibt separat charakterisiert;
- Parent-PID-Wechsel im PDEATHSIG-Setupfenster, Reparenting, PID-Reuse,
  nicht exklusiver Job-Handle, ungearmter/falscher Kernel-Timer, falsche
  Clock/Signal/Shim-Binary oder fehlende OS-Primitive verhindern Session OPEN;
- der Trading-Prozess führt im EMERGENCY-Pfad selbst keinen blockierenden
  Datei-/Flush-/Snapshot-Syscall aus; ausschließlich der isolierte Persistence
  Worker darf blockieren;
- verspätet durable Worker-Writes verwenden dieselbe vorab gebundene Control
  Event ID und werden journal-first ohne zweiten KILL reconciled;
- Worker lehnt falsche Session/Sequence/Journal-/State-Bindung, fehlenden
  TERMINATING-/Trip-Sequenz-Nachweis, fremden Broker-Peer, abweichende Payload
  unter derselben Event ID und jeden zweiten Emergency-Request ab;
- Terminal-Gap-Recovery beginnt erst nach nachgewiesenem Worker-Tod oder
  wirksamem Lease-Fencing; ein verspäteter alter Worker kann danach keinen
  Journalrecord mehr anhängen;
- `terminal_write_deadline_ms=0`, `101`, falsche Clock, fehlende Worker-/
  Guardian-/Broker-/Shim-Ready-Nonce, fehlender/falscher Self-/Guardian-/Broker-PIDFD,
  blockierender IPC, deaktivierbarer Guardian/
  Self-Death-Timer, `terminal_guardian_heartbeat_interval_ms` ungleich `10`,
  `terminal_guardian_lease_max_ms` ungleich `25`, Broker-Trip-CAS- oder
  Guardian-Dispatch-Budget ungleich `5`,
  Signal-Budget ungleich `25`, Fail-stop-Maximum ungleich `100`, fehlendes/
  abweichendes Capability-Profil oder behauptete Reap-Deadline
  verhindern Session OPEN beziehungsweise erzwingen Latch und harte
  Termination-Anforderung;
- `RECONCILE_TERMINAL_GAP` mit durable KILL-Journal und stale/fehlendem
  Snapshot materialisiert zuerst exakt dessen `state_after` und schreibt
  keinen zweiten KILL;
- ohne durable terminalen KILL, aber mit eindeutig reconciled Journal-/State-
  Basis, wird genau ein konservativer EMERGENCY-KILL committed;
- ungültiger Journal-Tail, mehrere widersprüchliche terminale Records oder
  uneindeutiger State-before blockieren ohne Ersatz-KILL;
- Crash nach KILL-Journal, nach Snapshot Replace und vor Gap Record bindet bei
  Wiederholung immer dieselbe Control Event ID;
- geordneter Stop schreibt `RUNTIME_SESSION_CLOSE_PREPARE` erst nach
  vollständiger State-/Journal-Reconciliation, verlangt danach Broker-CLOSED
  und schreibt erst dann `RUNTIME_SESSION_CLOSE_COMMIT`. Crash/Trip/Writefehler
  an jeder früheren Grenze bleibt beim nächsten Startup unclosed; Timer-Disarm
  und Trading-Exit vor COMMIT sind verboten.

Nach Recovery gelten je Ordnungsraum exakt die erwartete Tick-, Control- und
Lifecycle-Event-ID, keine Doppelbuchung, keine verlorene Schutzwirkung,
vollständige S4V2-/Owner-/Cross-State-Fingerprint-Parität und weiterhin
verbrauchte einmalige Authorizations.

### 21.8 Suites und Evidenz

- alle fokussierten IU4-/Live-L1-Tests;
- vollständige `tests/live_l1`-Suite;
- vollständige `tests/regression`-Suite;
- `py_compile` der geänderten Module;
- `git diff --check`;
- gestufter synthetischer Replay;
- genehmigter Workstation-Lauf mit Manifest, Hashes und Fault-Injection-Matrix;
- zwei unabhängige read-only Reviews desselben finalen Stands.

---

## 22. Aktivierungs- und Rollback-Regeln

### 22.1 Aktivierung

Aktivierung ist eine separate Operation nach Implementierung und Zertifizierung.
Sie erfordert einen expliziten Befehl, eine zeitlich gültige Authorization V2
und einen reconciled ENFORCED-State. Der Default bleibt `OFF`.

### 22.2 Kein Hot Switch

Ein laufender Prozess darf nicht zwischen OFF, SHADOW und ENFORCED wechseln.
Jeder Moduswechsel benötigt kontrollierten Stop, vollständige Reconciliation
und neuen Startup.

### 22.3 Rollback

- Bei FLAT darf ENFORCED kontrolliert gestoppt werden. Ein anschließender Start
  von `OFF` oder `SHADOW` benötigt zuvor einen vollständigen
  `PEE_TO_LEGACY`-Handoff von S4, Loss Cluster, Throttle/Cooldown und Progress;
  stale Legacy-State ist unzulässig.
- Bei offener PEE-Position darf kein Legacy-Prozess dieselbe Position übernehmen.
- Eine offene PEE-Position bleibt PEE-owned. Nach nichtterminalem Entry Lock
  kann sie PEE exit-only schließen. Nach HARD/EMERGENCY ist zunächst der
  manuelle L1-D-Restart-/Recovery- und Kill-Reset-Prozess erforderlich; erst
  danach darf derselbe PEE-Owner den Exit fortsetzen.
- Ein technischer Fehler führt abhängig von L1C zu Entry Lock, HARD oder
  EMERGENCY, niemals zu erfundener Legacy-Migration oder Auto-Recovery.
- Production/Exchange bleibt unabhängig davon aus.

---

## 23. Abnahmekriterien der Implementierung

Die Integration ist erst `IMPLEMENTATION_COMPLETE`, wenn:

- jedes Paket I1–I7 separat umgesetzt und abgenommen wurde;
- Single-Owner-Tests beweisen, dass kein Dual Write erreichbar ist;
- Atomic V2 vollständiges Entry Quote, Progress Cursor sowie alle Schutz- und
  Economics-Komponenten bindet;
- `PaperRiskStateS4V2` alle Legacy-S4-Felder und terminalen Capabilities ohne
  Defaults bindet;
- Lifecycle Ledger Owner Epoch, Genesis, beide Handoffs, Migration,
  Authorization-Consumption und Recovery über selbstreferenzfreie
  PREPARE/Target/COMMIT-Generationen crash-sicher ordnet;
- jeder offene Authority-PREPARE ausschließlich durch eine exakt gebundene,
  nicht loop-startende Completion-Operation fertiggestellt werden kann;
- Genesis-COMMIT-Provenance die DIRECT-Erststartausnahme eindeutig von
  `RECOVERED_AFTER_PREPARE` trennt, Completion-Consumption die kanonischen
  NONE-Sentinels bindet, DIRECT ausschließlich derselben lebenden
  Prozessinstanz/Operation/Nonce genau einmal offensteht und jeder Prozess nach
  DIRECT-Crash oder recovered Completion eine neue `RESTART_ONLY`-
  Authorization durable verbraucht;
- Ledger Tip und Authority Commit Anchor getrennt behandelt werden und
  nicht-ownerverändernde Records keinen State-Rebind erfordern;
- Runtime Session und Terminal-Gap-Reconciliation bei nicht persistierbarem
  KILL einen fail-closed nächsten Startup erzwingen und einen durable KILL mit
  stale Snapshot journal-first ohne Duplikat materialisieren;
- `RuntimeSessionCloseProtocolV8` ausschließlich PREPARE→Broker-CLOSED→durable
  COMMIT als clean akzeptiert, PREPARE/Broker-CLOSED ohne COMMIT als unclosed
  klassifiziert und Timer-Disarm/Child-Exit bis zu gültigem CommitAck,
  CLOSED→COMMITTED und brokerbestätigter Commit-Approval sperrt;
- die vollständige Kanal-/Rollenmatrix alle sechs Close-Typen, beide Worker-
  ACKs und beide Approval-Empfänger abbildet, Seccomp nur feste FDs/Richtungen/
  skalare Flags beansprucht und jeder Userspace-Empfänger Länge, Typ, Peer,
  gebundene `SO_PEERCRED`-Identität, Session, Nonce, State, Phase und
  Fingerprints prüft; `TerminalRuntimeSocketLSMGuardV3` muss vor jeder Phase-
  Transition und Runtime-Socket-Erzeugung global angehängt sein, alle Runtime-
  Sockets vor FD-
  Sichtbarkeit taggen, externe `receive_fd`-/`setsockopt`-Pfade verweigern und
  jeden Session-Send in `LISTENER_HANDOFF|LISTENER_RECEIVED|HANDOFF_REVOKED_GRANTED|BOOTSTRAP|OPEN_DURABLE_GRANTED` ohne Ausnahme sperren.
  `TerminalSeccompListenerHandoffV2` muss den Listener genau einmal über das
  gebundene `pidfd_getfd`-Tupel und Eventfd-ACK übernehmen und alle Ptrace-/
  Dumpable-/FD-Autoritäten vor Runtime-Socket-Erzeugung widerrufen.
  Der `file_receive`-Hook muss die einzige Listener-Duplikation durch
  `LISTENER_HANDOFF→LISTENER_RECEIVED` genau einmal erzwingen. Erst der
  getrennte `TerminalHandoffRevocationAttestorV1` darf nach Revocation
  `LISTENER_RECEIVED→HANDOFF_REVOKED_GRANTED` ausstellen; erst aus diesem
  Grant darf der Guard `HANDOFF_REVOKED_GRANTED→BOOTSTRAP` konsumieren.
  Jede Empfänger-TID-/Files-
  Table-Topologie muss zusätzlich vor Rights-Freeze vollständig fixiert sein,
  der `setsockopt`-KILL_PROCESS-Filter muss per TSYNC jeden Empfänger-TID
  erreichen, und ausschließlich der dann erhobene Snapshot darf durable OPEN
  autorisieren. Erst der Persistence Owner darf aus derselben erfolgreichen
  Sync-/Directory-Sync-/Readback-Fortsetzung
  `BOOTSTRAP→OPEN_DURABLE_GRANTED` ausstellen; der Grant selbst hält Sends
  gesperrt. Senderfreigabe darf nur durch das danach vom Guard im
  `socket_shutdown`-Hook einmalig ausgeführte
  `OPEN_DURABLE_GRANTED→RELEASED` erfolgen; jeder Userspace-Map-Writer ist
  verboten und
  jeder Rights-Send
  muss vor Queueing `EPERM` liefern und ohne SKB-/OFD-/Lock-Referenz enden;
  jeder Receive muss zusätzlich ohne Controlbuffer laufen und im getrennten
  Defense-in-Depth-Pfad nach Kernel-Autoclose eine unveränderte FD-/FDINFO-/
  Lock-Inventur besitzen;
- die endliche Close-FSM jede Request-/ACK-/Approval-Grenze für EINTR, EAGAIN/
  Queue-full, Short/invalid, HUP, Timeout, Crash, Retry, Idempotenz und
  Duplikate deterministisch besteht; kein Retry setzt Nonce oder Deadline
  zurück, PREPARE/COMMIT mutieren exactly once und jede Fehlerfolge endet in
  TERMINATING, CLOSED_FAILSTOP, COMMITTED oder COMPLETE;
- gemeinsames lock-free Control Word V3 mit ausschließlich im separaten Native
  Trip Broker bestehender writable Map, exakt erzeugtem/sealed Memfd, read-only
  Consumer-Maps, dauerhaft leerer `TerminalTripLivenessPipeV1`,
  `TerminalSelfKillEntryV4` mit Self→Guardian→Broker-PIDFD→Liveness-Close-
  Fallback, `TerminalKernelTripRequestV2` mit kernel-erzeugter Notification,
  `TerminalTradingSignalEnvelopeV1` und
  alleiniger Broker-Listener-/Trip-Autorität,
  `TerminalSeccompListenerHandoffV2`, `RuntimeSessionCloseProtocolV8`,
  getrennten Renewal-/Close-Kanälen und
  receiverseitiger Worker-Prüfung
  beweisen, dass ausschließlich die Broker-CAS einen Worker-Request autorisiert,
  nach `RUNNING|CLOSING→TERMINATING` keine Renewal committed, kein Pipe-Read/-Write im
  Terminal-Sicherheitsweg existiert und weder verlorene Notification noch
  vollständiger PIDFD-Signalfehler den Liveness-Fail-stop verhindert;
- das vollständige Signal-Envelope vor jeder TID-Erzeugung alle blockierbaren
  Signale maskiert, keine Handler/`SA_RESTART`-Disposition zulässt, jede
  spätere Masken-/Disposition-/Signal-Erzeugungsänderung kernel-seitig sperrt,
  `WAIT_KILLABLE_RECV` bindet und jeden Listener-Ready-/Receive-Fehler ohne
  Request-TID-Fortschritt terminal klassifiziert;
- `TerminalRuntimeChannelProvisioningV6` jeden Kanal erst zwischen den finalen
  Rollenprozessen verbindet, fremde Connects fail closed behandelt,
  `SO_PASSCRED=0`, auf jedem der zwölf finalen Endpunkte durch den globalen
  Socket-Guard exakt eine atomare `INIT→SEALED`-Initialisierung mit
  `SO_PASSRIGHTS=0` und auf den sechs Empfangsendpunkten zusätzlich dessen
  Prequeue-Autorität, danach auf der vollständigen fixierten Empfänger-TID-
  Menge eine Rights-Freeze-TSYNC-Sperre und erst nach finalen Rollenfiltern den
  autoritativen `getsockopt==0`-/`scm_fds: 0`-/Queue-/FD-/OFD-/Lock-Nachweis
  vor durablem OPEN erzwingt. `file_receive` muss externe Akquisition,
  `socket_setsockopt` auch FD-lose in-flight Mutation und `socket_sendmsg`
  jede Bootstrap-Übertragung verweigern. Der eingefrorene
  `TerminalRuntimeSocketGuardPhaseV3` darf ausschließlich per verifiziertem
  `BPF_ATOMIC|BPF_DW|BPF_CMPXCHG` im exakten `file_receive`- oder
  `socket_shutdown`-Hook wechseln; genau-einmal Listener-Receive, getrennte
  Revocation-/Durability-Grants, richtige Guard-Ablehnung vor jedem Grant und
  der erst danach mögliche Release müssen bewiesen sein. Jeder Setup-Rest muss alle
  Endpunkte/Prozesse zerstören,
  vollständige Referenzfreigabe belegen und den Startup ohne Same-Session-
  Retry abbrechen; bei `SCM_RIGHTS` bis `SCM_MAX_FD` auch unter Empfänger-
  Stop/-Crash und
  Sender-Close/-Crash exakt `EPERM` vor Queueing sowie keinerlei überlebende
  SKB-, Empfänger-FD-, Open-File-Description- oder Lock-Referenz zulässt;
- Parent Guardian V13, Native Trip Broker V10, Kernel-Self-Death-Lease-Shim V11,
  `TerminalTradingTaskTopologyV2` und synchrone Pre-Side-
  Effect-Prüfung bei Guardian-Tod, `SIGSTOP`/Suspend/Stall, Capability-Verlust
  oder gesundem Guardian plus Worker-Fehler spätestens nach `100 ms`
  `TERMINAL_FAILSTOP_ASSERTED` beweisen, ohne eine physisch unbelegbare Process-
  Reap-Deadline zu behaupten;
- das exakt gebundene `TerminalLeaseCapabilityProfileV14` in allen `10_000`
  Zertifizierungs- und 32 per-Startup Trials je Pflichtszenario ohne Einzel-
  oder Messfehler besteht; Environment-Abweichung bleibt fail closed;
- nicht nachweislich äquivalente Plattformen, insbesondere Windows nur mit Job
  Object/Waitable Timer, Session OPEN fail closed ablehnen;
- Authority-Root-/Generation-/PREPARE-Tamper-Tests die vollständige Abstammung
  jedes Atomic State vom committed Authority-Target beweisen;
- L0/L1-konforme HARD-/EMERGENCY- und manuelle Restart-/Recovery-Semantik
  nachgewiesen ist;
- beide Handoff-Richtungen sämtliche Safety Heads ohne Reset abbilden;
- alle Pflicht-Tests grün sind;
- R3-Final-Attestation, Commit, Profile und Evidence exakt gebunden sind;
- Workstation-Evidenz vollständig und hashgeprüft ist;
- unabhängige Reviews keine offenen kritischen oder hohen Findings enthalten;
- bekannte Restgrenzen dokumentiert sind.

Selbst dann bleibt `ENFORCED_ACTIVATION_AUTHORIZED=NO`, bis eine separate
menschliche Betriebsentscheidung vorliegt.

---

## 24. Aktueller Freigabestand

```text
SPECIFICATION_RESULT: REVISION_21_COMPLETE
SPECIFICATION_REVISION_20_REREVIEW_RESOLUTION_APPLIED: YES
SPECIFICATION_INDEPENDENT_REREVIEW_READY: YES
INDEPENDENT_REREVIEW_PASSED: NO
R3_FINAL_ATTESTATION_BOUND: NO
IMPLEMENTATION_READY: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_PROFILE_APPROVED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Die vorgeschalteten Schritte
`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-20-INDEPENDENT-READONLY-REREVIEW`
und
`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-20-REREVIEW-RESOLUTION`
sind abgeschlossen. Der nächste zulässige Schritt ist ausschließlich
`IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-21-INDEPENDENT-READONLY-REREVIEW`
des vollständigen Revision-21-Artefakts. Dessen exakter externer SHA-256 und
der Hash des controlling Revision-20-Resolution-Records werden im separaten
Review gebunden; die Spezifikation enthält keinen zirkulären Selbsthash.

Eine Implementierungsfreigabe darf erst nach geschlossenem Re-Review sowie
terminalem, bestandenem und final attestiertem R3 erfolgen.
