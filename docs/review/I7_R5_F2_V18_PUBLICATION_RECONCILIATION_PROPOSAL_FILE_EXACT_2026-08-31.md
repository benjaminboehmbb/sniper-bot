# I7 R5-F2 / V18 Publication Reconciliation Proposal — File Exact — 2026-08-31

```text
DOCUMENT_CLASS: NONAUTHORITATIVE_CORRECTION_AND_PUBLICATION_RECONCILIATION_PROPOSAL
I7_R5_F2_V18_PUBLICATION_RECONCILIATION_STATUS: PROPOSAL_ONLY
I7_PREPARATION_PUBLICATION_READINESS: NOT_READY
I7_EVIDENCE_AUTHORITY: NO
I7_ACCEPTANCE_AUTHORITY: NO
I7_EXECUTION_AUTHORITY: NO
I7_LIVE_AUTHORITY: NO
I7_EXCHANGE_AUTHORITY: NO
```

## 1. Zweck, Grundlage und harte Grenze

Dieses Dokument ist ausschließlich ein lokaler, nichtautoritativer Korrektur-
und Publication-Reconciliation-Kandidat. Es bindet den am 2026-08-31 lokal
gelesenen Zustand des kanonischen WSL-Repositorys
`/home/benja/projects/sniper-bot` bei `HEAD`
`d1e865f29f507fcf7eb405c3be7da4a8946b9861`.

Die Erstellung dieses Dokuments autorisiert und behauptet insbesondere nicht:

- keine Änderung einer bestehenden Datei;
- keine Ausführung eines Tests, Gates, Runners, Collectors oder Replays;
- keinen Netzwerk-, SSH-, QMP-, VM-, BPF-, LSM-, cgroup-, Namespace-,
  Privilege-, Live- oder Exchange-Zugriff;
- kein Staging, keinen Commit und keinen Push;
- keine I7-Evidence-, Acceptance-, Execution-, Live- oder Exchange-Authority;
- keine raw-artifact-file-exakte Rekonstruktion des verlorenen V18-Workspaces.

Die elf nachstehend gebundenen Eingabedateien wurden ausschließlich gelesen,
gehasht und statisch geprüft. Das vorliegende Dokument bindet seinen eigenen
Inhalt nicht selbstreferenziell. Seine Whole-file-Identität ist nach der
Erstellung separat und extern festzustellen.

## 2. Aktueller Repository- und Membership-Kontext

```text
CANONICAL_REPOSITORY: /home/benja/projects/sniper-bot
BRANCH: main
HEAD: d1e865f29f507fcf7eb405c3be7da4a8946b9861
LOCAL_MAIN: d1e865f29f507fcf7eb405c3be7da4a8946b9861
LOCAL_ORIGIN_MAIN: d1e865f29f507fcf7eb405c3be7da4a8946b9861
PREEXISTING_WORKTREE_STATUS_RECORDS: 121
STAGED_RECORDS: 0
```

Die 121 vorbestehenden Working-Tree-Records sind fremder beziehungsweise
vorbestehender Zustand. Dieses Proposal erteilt keinerlei Autorität, sie
zusammenzufassen, zu verändern, zu stagen oder in einen späteren Commit
aufzunehmen. Acht der elf gebundenen Eingaben sind untracked. Das
transcriptgebundene Profil sowie der reviewed Supervisor und sein Test sind
bereits getrackt.

## 3. File-exakte aktuelle Identitäten

Für alle elf Dateien gilt am gelesenen Zustand:

- reguläre Datei, kein Symlink;
- Linkzahl 1;
- Mode `0444`;
- UID/GID `1000:1000`;
- Device 2096;
- Zeilenangabe gemäß `wc -l`;
- Bytes und SHA-256 über den vollständigen Dateiinhalt.

### 3.1 Sieben technische I7-Dateien

| Rolle | Pfad | Git | Bytes | Zeilen | SHA-256 | Inode |
|---|---|---|---:|---:|---|---:|
| Gate-Manifest | `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | untracked | 8896 | 178 | `a96ddc05124e3a95312833c281e86155b1c1f1710d9845b1da7cf64f74799719` | 33136 |
| Workstation-Schema | `config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json` | untracked | 10209 | 166 | `12228780102d62dee3f0982507642b648e9defc6edc095739df6e38fa8dbf62d` | 2738 |
| Replay-Fixture | `tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt` | untracked | 209 | 4 | `e7a1723a7bc766c4dbd3f1961e801a8a14e8e8b68a59f880afd1e8da94ffd915` | 10773 |
| File-Exact-Harness | `live_l1/tools/i7_file_exact_harness.py` | untracked | 95036 | 2188 | `15c9883518cc8c30c76aaf496c271444a97386e629c3683a782672347db11941` | 36133 |
| Observer-Evaluator | `live_l1/tools/i7_file_exact_observer.py` | untracked | 39238 | 974 | `0e427702d48dd8dba2a657a41d6b33e8cfe88441e42dad205b11f67aa68d7bca` | 2104 |
| Staged Replay | `live_l1/tools/i7_staged_synthetic_replay.py` | untracked | 22528 | 569 | `6272941ba902a6a4422d9f906a12a8a7baa6cad687258be23dfcad699bf8d653` | 36194 |
| Preparation-Fokustest | `tests/live_l1/test_i7_file_exact_preparation.py` | untracked | 69768 | 1340 | `3047b84435636dbd3d6b5174ccabf630a00009c376b406d3d76b03f7b3cf3ecd` | 32787 |

### 3.2 Resolution, Profil und getrackter reviewed Supervisor

| Rolle | Pfad | Git | Bytes | Zeilen | SHA-256 | Inode |
|---|---|---|---:|---:|---|---:|
| PRE-I7-Resolution | `docs/review/PRE_IU4_I7_PREPARATION_RESOLUTION_FILE_EXACT_2026-08-23.md` | untracked | 44562 | 621 | `1bbeaf26e99c64f506bddff0251dc3c991d97ce154f3931a4f0a420ce47b1b31` | 32753 |
| Transcriptgebundenes Profil | `docs/review/I7_R5_F2_CANONICAL_IMPLEMENTATION_PROFILE_TRANSCRIPT_BOUND_V1.md` | tracked | 14844 | 205 | `3d3a1973b63c20e65ff006fb453e1613560f2ed813e1223bd78ac741974dd542` | 33220 |
| Reviewed Engineering-Supervisor | `live_l1/tools/i7_reviewed_test_supervisor.py` | tracked | 12012 | 344 | `577fa5995dc514ea2de75a1af7d0cacb5f149fe5b520f5895fc6b747d5a2fb46` | 25317 |
| Reviewed Supervisor-Test | `tests/live_l1/test_i7_reviewed_test_supervisor.py` | tracked | 1461 | 42 | `9463a186ac9f05ec67f5893e0bda1a1d0f6757ee4b84e2debcd6f88b0ab9e41a` | 25318 |

Das transcriptgebundene Profil bleibt eine bereits publizierte historische
P0-Referenz. Für den Preparation-Fokustest bindet es weiterhin die vor der
P1-T-Korrektur geltende Identität `5141b498d7a4638879a7154819bc407a77149a685ca0809b6ab5a98554363aa5`, während dieses Proposal
die projizierte korrigierte P1-Identität `3047b84435636dbd3d6b5174ccabf630a00009c376b406d3d76b03f7b3cf3ecd` bindet.
Das Profil ist weder aktueller P1-Identitätspfad noch Mutationsziel.
Observer, Workstation-Schema und Replay-Fixture bleiben gegenüber der
finalen Resolution-5-Tabelle unverändert.

## 4. Historischer Resolution-5-Stand und aktueller V18-Stand

Die Tabellen `Finaler technischer Resolution-5-Sieben-Dateien-Stand vor
Dokumentbindung` in der PRE-I7-Resolution sind ausschließlich als historischer
Resolution-5-Stand zu lesen. Sie besitzen keine Autorität für die heutigen
vier geänderten Dateien.

| Pfad | Historischer R5-SHA-256 | Aktueller V18-SHA-256 | R5/V18-Zeilen |
|---|---|---|---:|
| `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | `7eea67c93ecd70fbecd043daea7a74c5ce07548c08b4546c4fe477f6c0de50a5` | `a96ddc05124e3a95312833c281e86155b1c1f1710d9845b1da7cf64f74799719` | 178/178 |
| `live_l1/tools/i7_file_exact_harness.py` | `c0c48f31c9af4484667048987587d769abe30933f3625a1a4064d55f986e1967` | `15c9883518cc8c30c76aaf496c271444a97386e629c3683a782672347db11941` | 2110/2188 |
| `live_l1/tools/i7_staged_synthetic_replay.py` | `7b7a51185c00c8322e1b4bcdb86703b2d07f309eb9b8e84f81a4394e35e9c8cd` | `6272941ba902a6a4422d9f906a12a8a7baa6cad687258be23dfcad699bf8d653` | 569/569 |
| `tests/live_l1/test_i7_file_exact_preparation.py` | `3a12f70485bec0c19d2b874853582a958e8be7872ff22dc9ff8c8f55bcd9be6e` | `3047b84435636dbd3d6b5174ccabf630a00009c376b406d3d76b03f7b3cf3ecd` | 1319/1340 |

Die in der PRE-I7-Resolution eingebetteten Closure-JSON-Records binden bereits
die aktuellen V18-Identitäten. Die spätere Resolution-5-Tabelle derselben
Datei bindet dagegen die vorangehenden historischen Identitäten. Deshalb darf
keine dieser beiden Darstellungen ohne eine neue separate Resolution als
alleinige Publication-Authority behandelt werden.

Die historischen R5-Dateiinhalte sind im aktuellen Git-Objektbestand nicht
als diese sieben Kandidaten publiziert. Der verlorene V18-Workspace enthält
keine erneut lesbaren 309 Raw-Traces oder abgeleiteten Manifestdateien. Eine
byteweise R5-zu-V18-Diff-Rekonstruktion und eine raw-artifact-file-exakte
V18-Attestation sind daher aus den aktuell verfügbaren Eingaben nicht
ableitbar. Zulässig ist nur die statische Konformitätsbewertung der heutigen
Dateien gegen die dokumentierten R5-Findings und das transcriptgebundene
Profil.

## 5. Statische semantische Reconciliation

### 5.1 Aktueller eingebetteter R5-F2-Pfad

Der aktuelle File-Exact-Harness enthält einen eingebetteten, codegehashten
Supervisor-/Worker-Vertrag. Statisch sichtbar sind insbesondere:

- der terminale Resultatkanal ist eine Pipe;
- nur der feste Supervisor erbt den terminalen Writer;
- der unittest-Worker läuft mit `close_fds=True` und erbt den Writer nicht;
- Worker-stdout und Worker-stderr werden nicht als Ergebnisautorität geparst;
- der Worker besitzt keinen Nonce-, Gate- oder Run-ID-State;
- Erfolg wird erst nach exakter Prüfung von `testsRun`, Failures, Errors,
  Skips, Unexpected Successes und Expected Failures erreicht;
- der Parent bindet exakt ein strict-JSON-Frame an Gate, Run-ID, Nonce,
  Supervisor-PID, Supervisor-Hash, Startmodule und Counts;
- Timeout, TERM, KILL, Reaping und Prozessgruppenrest werden fail-closed
  ausgewertet.

Diese statische Beobachtung ist keine Testevidence und keine Behauptung, dass
alle Runtime-, Kernel- oder adversarialen Eigenschaften frisch ausgeführt
wurden. Das V18-Profil bleibt
`TRANSCRIPT_BOUND_NONAUTHORITATIVE_DESIGN_INPUT`.

### 5.2 Reviewed Engineering-Supervisor

Der getrackte `i7_reviewed_test_supervisor.py` pinnt vier historische
Resolution-5-Hashes und wertet eine unittest-Zusammenfassung aus stdout/stderr
aus. Er bezeichnet sein Ergebnis selbst korrekt als
`ENGINEERING_EVIDENCE_ONLY` mit Threat Model `REVIEWED_TEST_CODE`.

Er ist weder der aktuelle eingebettete R5-F2-Supervisor noch ein zulässiger
paralleler I7-Autoritätspfad. Sein Test liegt im aktiven Pfad
`tests/live_l1/`, besitzt drei Testmethoden und ist nicht Bestandteil des
gepinnten 37-Modul-/584-Test-Census im aktuellen Gate-Manifest. Seine
Pin-Prüfung ist gegenüber vier heutigen Kandidatenidentitäten stale.

Verbindliche Proposal-Klassifikation:

```text
I7_REVIEWED_TEST_SUPERVISOR_CLASSIFICATION: HISTORICAL_ENGINEERING_EVIDENCE_ONLY
UPDATE_AS_CURRENT_I7_AUTHORITY: NO
REPLACE_EMBEDDED_R5_F2_SUPERVISOR: NO
ALLOW_PARALLEL_I7_AUTHORITY_PATH: NO
ACTIVE_TEST_CENSUS_MEMBERSHIP_RESOLVED: NO
LATER_HISTORIZATION_MUTATION_REQUIRED: YES
```

Eine spätere, separat autorisierte Mutation muss Supervisor und Test aus dem
aktiven I7-/Testpfad entfernen oder in einen ausdrücklich geprüften
historischen Pfad überführen. Dieses Proposal legt keinen Zielpfad fest und
autorisiert keine Verschiebung, Löschung oder Änderung.

### 5.3 Profilstatus

Das transcriptgebundene Profil ist in `HEAD` publiziert, enthält intern aber
weiterhin den Ableitungsstatus `nicht publizierter In-memory-Kandidat`. Dieser
Text darf nur als historischer Status zum Ableitungszeitpunkt verstanden
werden. Er ist keine aktuelle Publication-Statusautorität und darf nicht durch
stillschweigende Änderung des bereits attestierten Profilinhalts korrigiert
werden.

## 6. Vollständiger späterer Publication-Scope

Publication darf nicht als pauschales Staging der 121 Working-Tree-Records
erfolgen. Der Scope ist in getrennte, jeweils neu zu autorisierende Klassen zu
zerlegen.

### P0 — Bereits publizierte Referenzidentitäten, nicht erneut zu stagen

- `docs/review/I7_R5_F2_CANONICAL_IMPLEMENTATION_PROFILE_TRANSCRIPT_BOUND_V1.md`
  bei Blob `79a760ddcd4f4e2eb1e52594ab16f71d4b013791`;
- `live_l1/tools/i7_reviewed_test_supervisor.py` ausschließlich als später zu
  historisierender getrackter Altstand;
- `tests/live_l1/test_i7_reviewed_test_supervisor.py` ausschließlich als später
  zu historisierender getrackter Altstand;
- die bereits getrackten Closure-Grundlagen `live_l1/__init__.py` und
  `tests/live_l1/__init__.py` sowie die im Replay-Manifest gepinnten bestehenden
  Profile-, Policy- und Seed-Eingaben, sofern eine neue Read-only-Attestation
  ihre beabsichtigten Git-Identitäten bestätigt.

### P1 — Minimaler neuer I7-Preparation-Publication-Scope

Exakt die folgenden acht gegenwärtig untracked Pfade bilden den minimalen
technischen und dokumentarischen I7-Preparation-Kandidaten:

1. `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json`
2. `config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json`
3. `tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt`
4. `live_l1/tools/i7_file_exact_harness.py`
5. `live_l1/tools/i7_file_exact_observer.py`
6. `live_l1/tools/i7_staged_synthetic_replay.py`
7. `tests/live_l1/test_i7_file_exact_preparation.py`
8. `docs/review/PRE_IU4_I7_PREPARATION_RESOLUTION_FILE_EXACT_2026-08-23.md`

Das vorliegende Reconciliation-Proposal ist nach eigener unabhängiger
Read-only-Rereview ein neunter möglicher Add-Pfad. Es darf nicht vor einer
extern gebundenen Whole-file-Identität und einer separaten Rereview gestaged
werden.

### P2 — Upstream-Governance- und I6-Publication-Prerequisite

Die PRE-I7-Resolution bindet in Abschnitt F1 exakt 31 Specification-/I1–I6-
Governance-Records mit Pfad, SHA-256 und Zeilenzahl sowie sechs I6-
Implementierungs-/Evidence-Identitäten. Soweit diese Identitäten am späteren
Publication-OID nicht bereits getrackt und file-exakt erreichbar sind, bilden
sie einen vorgelagerten, getrennt zu prüfenden und getrennt zu autorisierenden
Publication-Prerequisite-Scope.

Keiner dieser Pfade darf aufgrund dieses Proposals automatisch in P1
aufgenommen werden. Vor P1-Staging ist durch eine neue Read-only-Attestation
für jeden F1-/I6-Pfad festzustellen: `TRACKED_AT_BASE`, `REQUIRES_SEPARATE_ADD`,
`IDENTITY_MISMATCH` oder `UNAVAILABLE`. Jeder andere Status als
`TRACKED_AT_BASE` blockiert P1, bis eine separate Human-Entscheidung vorliegt.

### P3 — Historisierung des reviewed Supervisors

Die spätere Historisierung der zwei bereits getrackten Pfade ist ein eigener
Mutation-, Review-, Test- und Commit-Scope. Sie darf weder mit P1 vermischt
noch durch Änderung der sieben technischen I7-Dateien kaschiert werden.

### P4 — Ausdrücklich ausgeschlossen

- alle übrigen vorbestehenden Working-Tree-Records;
- die zehn geänderten aktiven Runtime-Dateien, solange keine getrennte
  Publication- und Runtime-Regression-Authority vorliegt;
- andere I1–I6-, Terminal-Lease-, IU4-, RCC-002- oder Hilfsartefakte ohne
  explizite P2-Einstufung;
- `.git`, Git-Locks, lokale Config-, Ignore-, PYC-, Cache-, Run-, `/tmp`- und
  Transcriptartefakte;
- V18-Controller-, Raw-Trace- oder Manifestrekonstruktionen, die nicht mehr
  file-exakt vorhanden sind.

## 7. Erforderliche getrennte Gates vor Publication

Jedes folgende Gate benötigt eine neue ausdrückliche Human-Autorisierung. Ein
PASS eines Gates autorisiert niemals automatisch das nächste.

### G0 — Scope- und Base-Attestation

- HEAD, Branch, Index und Remote-Tracking lokal ohne Netzwerk binden;
- P0–P4 file-exakt klassifizieren;
- die 31 F1- und sechs I6-Identitäten gegen den vorgesehenen Base-OID prüfen;
- sicherstellen, dass kein fremder Working-Tree-Record in den Scope gelangt.

### G1 — Unabhängige Read-only-Rereview dieses Proposals

- Whole-file-Hash, Bytes, Zeilen, Encoding, terminales LF und Metadaten dieses
  Dokuments extern binden;
- alle elf Eingabeidentitäten und die historischen/aktuellen Tabellen neu
  lesen und unabhängig vergleichen;
- `PUBLICATION_RECONCILIATION_PROPOSAL_READY` oder `NOT_READY` entscheiden.

### G2 — Separat autorisierte Korrektur-/Historisierungsmutation

- reviewed Supervisor und Test aus dem aktiven I7-/Testpfad historisieren;
- den 37/584-Census entweder unverändert wiederherstellen oder durch eine neue
  separat mandatierte Census-Revision ersetzen;
- keine parallele I7-Ergebnisautorität schaffen;
- keine Änderung der sieben technischen Dateien ohne neues File-Exact-Mandat.

### G3 — Statische Validierung

Erst nach G2 und mit neuer Testautorität:

- AST-/Syntaxprüfung der finalen Pythondateien;
- strict-JSON-Prüfung der finalen JSONdateien;
- file-exakte Hash-/Mode-/Owner-/Link-/LF-Prüfung;
- Import-/Effect-Closure-Plan;
- `git diff --check` und `git diff --cached --check` nur im ausdrücklich
  autorisierten Scope.

### G4 — Fokussierte und adversariale Tests

Erst mit separater Testautorität und raw-artifact-preserving Runroot:

- exakt zwölf Preparation-Testmethoden;
- Preparation-Harness mindestens zweimal mit identischem Semantic Root und
  verschiedenen Run Roots;
- exakt drei Replay-Stufen;
- R5-F1/F2/F3/F4/F8 sowie fortgeltende R4-F5/F7 und R3-F6 adversarial;
- Timeout-, TERM-, KILL-, Reaping-, Preservation- und Git-/Ignore-Semantik;
- vollständige stdout-/stderr-/RC-/PID-/Lineage-/Raw-Artifact-Bindung.

Vergangene Transcriptwerte dürfen nicht als frischer G4-PASS wiederverwendet
werden.

### G5 — Unabhängige Evidence-/Acceptance-Rereview

- G3-/G4-Rohartefakte unabhängig file-exakt prüfen;
- klare Trennung zwischen Preparation-Evidence und E1–E3;
- kein Selbstzertifizieren durch den Implementierungsworkstream.

### G6 — Staging

- nur ein zuvor genehmigtes, file-exaktes P1-/Proposal-Manifest stagen;
- P2 und P3 nur in getrennten ausdrücklich genehmigten Staging-Sets;
- staged diff, Blobidentitäten, Modes und Fremdpfadausschluss attestieren.

### G7 — Commit

- neuer Human-Commitauftrag mit exakter Parent-OID, Tree-Erwartung,
  Commitnachricht und Identität;
- kein Amend, Rebase, Merge oder History-Rewrite ohne separate Autorität.

### G8 — Push

- neuer Human-Pushauftrag mit exaktem Ref, Expected-Old-OID und New-OID;
- Netzwerkzugriff ausschließlich innerhalb dieses einzelnen Auftrags;
- kein Tag- oder Nebenref-Push.

### G9 — Post-Push-Attestation

- Remote-Ref separat read-only attestieren;
- lokale Remote-Tracking-Synchronisierung nur mit eigener Autorität;
- transiente Credentials, Agents, Sockets und Sessions separat bereinigen.

## 8. E1–E3 bleiben offen und fail-closed

```text
E1_CAPABILITY_RUNNER_AND_COMPLETE_SCENARIO_MANIFEST: OPEN
E2_REAL_DISPOSABLE_WORKSTATION_VM_SSH_PRIVILEGE_COORDINATES_AND_HUMAN_AUTHORITY: OPEN
E3_INDEPENDENT_PROCESS_KERNEL_BPF_VM_COLLECTOR: OPEN
```

P0–P4 und G0–G9 betreffen ausschließlich eine mögliche Preparation-
Publication. Selbst eine vollständige Preparation-Publication schließt E1–E3
nicht und autorisiert keinen realen Capability-, Workstation-, Collector-,
Activation-, Live- oder Exchange-Lauf.

## 9. Proposal-Entscheidung

```text
CURRENT_SEVEN_FILE_IDENTITIES_BOUND: YES_READONLY
PRE_I7_RESOLUTION_REQUIRED_AS_EIGHTH_CANDIDATE: YES
R5_TABLES_CLASSIFIED_AS_HISTORICAL: YES
CURRENT_V18_CLOSURE_IDENTITIES_PUBLICATION_AUTHORITATIVE: NO
R5_TO_V18_BYTE_EXACT_DELTA_RECONSTRUCTED: NO
REVIEWED_SUPERVISOR_CLASSIFIED: HISTORICAL_ENGINEERING_EVIDENCE_ONLY
REVIEWED_SUPERVISOR_ACTIVE_PATH_RESOLVED: NO
UPSTREAM_F1_I6_PUBLICATION_CLOSURE_AT_BASE_ATTESTED: NO
E1_E2_E3: OPEN_FAIL_CLOSED
I7_PREPARATION_PUBLICATION_READINESS: NOT_READY
PROPOSAL_READY_FOR_SEPARATE_INDEPENDENT_READONLY_REREVIEW: YES_AFTER_EXTERNAL_SELF_IDENTITY_BINDING
```

Dieses Proposal endet ohne Publication-, Evidence-, Acceptance- oder
Execution-Entscheidung. Keine frühere einmalige Autorisierung darf für einen
der nachfolgenden Schritte wiederverwendet werden.
