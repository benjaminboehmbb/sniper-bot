# I7 R5-F2 V18 P2C-T-B1 Startup Authority Dependency Closure Proposal

Datum: 2026-09-01

```text
DOCUMENT_CLASSIFICATION: NONAUTHORITATIVE_P2C_T_STARTUP_AUTHORITY_DEPENDENCY_CLOSURE_PROPOSAL
P2C_T_B1_BLOCKER: P2C-T-B1-STARTUP-AUTHORITY-DEPENDENCY-MISSING-AT-CURRENT-BASE
P2C_T_B1_CLASSIFICATION: MANDATORY_SEPARATELY_PUBLISHED_P2C_PREREQUISITE_DEPENDENCY
PREFERRED_RESOLUTION_PATH: A
P1_OWNED: NO
SHARED_P1_P2C_WORKSTREAM_REQUIRED: NO
P2C_OR_I6_CORRECTION_CASCADE_REQUIRED: NO
PUBLICATION_AUTHORITY: NO
MUTATION_AUTHORITY: NO
TEST_AUTHORITY: NO
STAGING_AUTHORITY: NO
COMMIT_AUTHORITY: NO
PUSH_AUTHORITY: NO
EVIDENCE_AUTHORITY: NO
ACCEPTANCE_AUTHORITY: NO
EXECUTION_AUTHORITY: NO
LIVE_AUTHORITY: NO
EXCHANGE_AUTHORITY: NO
```

## 1. Zweck, Status und Beweisgrenze

Dieses Dokument ist ein nichtautorativer Dependency-Closure-Kandidat. Es
bindet den beim isolierten P2C-T festgestellten Startup-Authority-Blocker und
schlägt einen minimalen, nichtüberlappenden Resolution-Weg vor. Es erteilt
keine Scope-Erweiterung und keine Mutation-, Test-, Staging-, Commit-, Push-,
Publication-, Evidence-, Acceptance-, Execution-, Live- oder
Exchange-Authority.

Frühere Testausgaben sind ausschließlich Blockerhinweise. Die nachstehenden
File-Exact-Bindungen wurden unmittelbar aus Repository, Git-Objektbestand,
HEAD und Worktree abgeleitet. Ein späteres Review muss sie erneut unabhängig
lesen; dieses Proposal ist kein Ersatz für diese Rereview.

## 2. Kanonische Repositorybasis vor Kandidatenerstellung

| Bindung | File-exakter Wert |
|---|---|
| Repository | `/home/benja/projects/sniper-bot` |
| Branch | `main` |
| HEAD | `9efc0301c632eadc87b69f7cb4269772ca20fab5` |
| main | `9efc0301c632eadc87b69f7cb4269772ca20fab5` |
| origin/main | `9efc0301c632eadc87b69f7cb4269772ca20fab5` |
| Parent | `47f0d450565ae3c791e0f0dd81726fad08752d0b` |
| Index | leer, 0 Records |
| Tracked unstaged | 5 |
| Untracked | 85 |
| Working-Tree-Records | 90 |
| Index-Lock | abwesend |
| Merge/Rebase/Cherry-pick/Revert/Bisect | jeweils abwesend |

### 2.1 Statusidentität

```text
SHA-256: 494f9dde7bb0111cd664251b2efc057fd7db2b52bc2f2bb84f164f9d0ba0717f
Bytes: 7782
Records: 90
```

### 2.2 Worktree-Content-Manifest

```text
SHA-256: 02b8ff77944ea3af5a3b9c312ccc9adca7504fcb2cea4865f77e2b78dadc327e
Bytes: 13632
Zeilen: 90
```

### 2.3 Untracked-Manifest

```text
SHA-256: 453f074942afbffa6197ea50fe20a46c0f228f61747d793b35e8753449ec1b5a
Bytes: 13693
Zeilen: 85
```

Die Erstellung dieses Proposal-Kandidaten verändert anschließend
ausschließlich die Untracked-/Working-Tree-Anzahl und die davon abgeleiteten
Manifestidentitäten. Sie ändert weder HEAD noch main, origin/main, Index oder
einen bestehenden Pfad.

## 3. P2C-Kandidatenidentitäten

| Rolle | Pfad | SHA-256 | Bytes | Zeilen | Mode | UID:GID | Device/Inode | Links | Typ | Encoding/BOM | Terminal-LF | Git/HEAD |
|---|---|---|---:|---:|---|---|---|---:|---|---|---|---|
| P2C-Implementierung | `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | 299085 | 6033 | `0444` | `1000:1000` | `2096/10750` | 1 | regulär, kein Symlink | UTF-8/kein BOM | exakt vorhanden | untracked/ABSENT |
| P2C-Test | `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | 255265 | 5307 | `0444` | `1000:1000` | `2096/10749` | 1 | regulär, kein Symlink | UTF-8/kein BOM | exakt vorhanden | untracked/ABSENT |

Beide Pfade bleiben untracked und sind nicht Teil eines durch dieses Proposal
autorisierten Prerequisite-Stagings.

## 4. Blocker

```text
P2C-T-B1-STARTUP-AUTHORITY-DEPENDENCY-MISSING-AT-CURRENT-BASE
```

Die P2C-Implementierung und ihr Test verlangen
`IU4RestartRecoveryAuthorizationV1`. Die veröffentlichte HEAD-Version von
`live_l1/core/paper_iu4_startup_gate.py` definiert und exportiert diese
Identität nicht. Die aktuelle Worktree-Version definiert sie, war im
isolierten P2C-T aber als fremde tracked-unstaged Identität ausgeschlossen.

## 5. Startup-Gate-Identitäten

### 5.1 HEAD

```text
Path: live_l1/core/paper_iu4_startup_gate.py
SHA-256: 86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753
Git-Blob: faf51735cf22a1279993a735c87439f516c1d9a1
Bytes: 21869
Zeilen: 600
Git-Mode: 100644
IU4RestartRecoveryAuthorizationV1: ABSENT
```

### 5.2 Worktree

```text
Path: live_l1/core/paper_iu4_startup_gate.py
SHA-256: c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd
Git-Blob: f7da370d9f8e3538907cf14a91d39aa538bf3462
Bytes: 37668
Zeilen: 919
Worktree-Mode: 0444
UID/GID: 1000:1000
Device/Inode: 2096/34523
Linkzahl: 1
Typ: reguläre Datei, kein Symlink
Encoding: UTF-8 ohne BOM
CR/CRLF: 0
Terminales LF: exakt vorhanden
Git-Status: tracked modified
HEAD-zu-Worktree-Diff: +319/-0
```

Der vollständige Diff ist additiv und umfasst gemeinsam zusätzliche
Standardbibliotheksimporte für den strikten Loader, zusätzliche Startup-
Reason-Codes, `IU4ActivationAuthorizationV2`,
`RESTART_RECOVERY_OPERATIONS`, `IU4RestartRecoveryAuthorizationV1`,
`load_external_authorization()` und die zugehörigen `__all__`-Exporte.

Die Klasse ist als `@dataclass(frozen=True)` in den Worktree-Zeilen 395 bis
494 definiert und wird in `__all__` in Zeile 908 exportiert. In HEAD ist weder
ihre Definition noch ihr Export vorhanden.

## 6. Vollständiger Restart-Authorization-Vertrag

Die Klasse besitzt keine Basisklasse. Der generierte Dataclass-Constructor
bindet exakt folgende 34 Felder in dieser Reihenfolge:

1. `schema_version`
2. `restart_recovery_authorization_id`
3. `operator`
4. `decision_timestamp_utc`
5. `stop_recovery_reason`
6. `previous_kill_level`
7. `secured_logs_manifest_sha256`
8. `last_state_timestamp_utc`
9. `no_open_intents_confirmed`
10. `environment_check_sha256`
11. `repository_commit_sha`
12. `coordinator_id`
13. `economics_config_fingerprint`
14. `throttle_policy_fingerprint`
15. `runtime_control_fingerprint`
16. `pre_attempt_ledger_tip`
17. `startup_attempt_id`
18. `source_authority_commit_anchor`
19. `source_authority_generation_id`
20. `expected_transaction_sequence`
21. `expected_journal_head`
22. `expected_snapshot_fingerprint`
23. `operation`
24. `completion_prepare_event_id`
25. `completion_prepare_fingerprint`
26. `completion_operation_type`
27. `planned_authority_generation_id`
28. `completion_source_authority_anchor`
29. `target_core_fingerprint`
30. `expected_target_schema`
31. `expected_target_path`
32. `expected_commit_type`
33. `valid_from_utc`
34. `valid_until_utc`

`from_record()` akzeptiert ausschließlich ein `Mapping`, dessen Feldmenge
exakt der Dataclass-Feldmenge entspricht, und ruft danach den vollständigen
Constructor-/Validierungsvertrag auf. Fehlende und unbekannte Felder werden
abgewiesen.

`canonical_payload()` bindet alle Felder außer der abgeleiteten Authorization-
ID. `authorization_fingerprint` bildet SHA-256 über kanonisches ASCII-JSON mit
sortierten Keys und kompakten Separatoren. `to_record()` ergänzt die
Authorization-ID wieder. Die ID lautet deterministisch:

```text
IU4-RESTART-RECOVERY-V1-<SHA-256-des-kanonischen-Payloads>
```

Eine nichtleere, abweichende vorgegebene ID wird abgewiesen.

### 6.1 Zulässige Operationen

```text
RESTART_ONLY
RECOVER_AND_RESTART
COMPLETE_AUTHORITY_PREPARE
RECONCILE_TERMINAL_GAP
```

Jede andere Operation wird fail-closed abgewiesen.

### 6.2 Validierungs- und Sentinel-Grenzen

Die Klasse validiert fail-closed Schema-Version 1, erforderliche Textfelder,
vollständige Commit-/SHA-Identitäten, `no_open_intents_confirmed is True`,
nichtnegative Sequenz, Operation, Completion-Felder und -Sentinels,
Genesis-Bindungen, vier UTC-Zeitstempel, ein zunehmendes Gültigkeitsfenster
und die deterministische Authorization-ID. Der Vertrag bindet Startup
Attempt, Pre-State, Journal, Ledger, Authority Generation/Anchor,
Coordinator, Repository, Environment und Completion-Zielidentitäten. Ein
Validierungsfehler erzeugt keine Start-, Recovery-, Lifecycle- oder
Coordinator-Authority.

### 6.3 Direkte und transitive Abhängigkeiten

Die Klasse verwendet ausschließlich bereits innerhalb derselben Datei
vorhandene Validierungs-, Timestamp-, JSON-, Hash- und Dataclass-Helfer sowie
die in derselben Worktree-Erweiterung eingefügten Restart-Konstanten und
Reason-Codes.

Die einzigen lokalen Modulimporte des Startup-Gate-Moduls sind
`live_l1.core.paper_entry_throttle.canonical_utc_timestamp` und
`live_l1.state.paper_atomic_coordinator.PaperAtomicCoordinator`. Beide Module
und Symbole sind am aktuellen HEAD verfügbar. Die Klasse braucht keine der
anderen vier tracked-unstaged Dateien und keine weitere untracked Datei.

## 7. Produktive Consumer und Authority-Bindungen

Die P2C-Implementierung konsumiert die Klasse an genau zwei Stellen:

1. `consume_restart_authorization()` importiert die Klasse ab Zeile 5292;
2. `complete_authority_prepare()` importiert sie ab Zeile 5667.

Beide Consumer prüfen den exakten Typ mit `type(...) is ...`; Mappings,
Subklassen und Lookalikes sind nicht akzeptiert. Gemeinsam binden sie
Operation, Operator, Repository-Commit, Coordinator, Log- und Environment-
Manifeste, Economics-/Throttle-/Runtime-Fingerprints, Startup Attempt,
Gültigkeitsfenster, Pre-State, Transaction Sequence, Journal Head, Ledger
Tip, Authority Generation/Anchor, einmalige Lifecycle-Ledger-Consumption und
offene PREPARE-/Completion-Zielidentitäten. Recovery und Completion sind
keine Loop-Start-Autorität.

## 8. Vollständige statische Testzuordnung

Der Helper `_restart_authorization()` steht in den Testzeilen 388 bis 416 und
importiert die Klasse in Zeile 389. Folgende 15 Tests erreichen die Klasse
über diesen Helper, teils über `_authorization()` oder
`_terminal_gap_material()`:

1. `test_nested_consumption_resource_causes_are_stable_and_preterminally_null`
2. `test_nested_gap_publication_resource_is_postterminally_exact_and_retryable`
3. `test_recover_and_restart_consumes_once_materializes_without_transaction`
4. `test_recovery_materialization_complete_fault_grid`
5. `test_restart_authorization_is_bound_to_trusted_environment_before_consumption`
6. `test_restart_consumption_resource_error_is_classified`
7. `test_restart_preconsumption_lifecycle_view_resources_are_classified_without_mutation`
8. `test_terminal_cleanup_resource_does_not_replace_primary_extension_failure`
9. `test_terminal_gap_after_kill_crash_requires_fresh_authority_and_reuses_exact_kill`
10. `test_terminal_gap_complete_fault_grid_preserves_exact_boundaries`
11. `test_terminal_gap_lifecycle_extension_before_lock_never_commits_kill`
12. `test_terminal_gap_requires_death_reap_then_commits_one_emergency_kill`
13. `test_terminal_lifecycle_lock_resource_error_is_classified_before_kill`
14. `test_terminal_lifecycle_unlock_and_close_resources_preserve_kill_and_gap`
15. `test_terminal_preconsumption_lifecycle_reads_are_classified_without_follow_on_mutation`

Der sechzehnte Test
`test_genesis_prepare_completion_requires_fresh_consumed_authority` beginnt in
Zeile 5201 und importiert und konstruiert die Klasse unmittelbar ab Zeile
5202. Damit sind alle 16 beobachteten Importfehler statisch vollständig
derselben fehlenden HEAD-Identität zugeordnet.

## 9. Fünf tracked-unstaged Fremdpfade

| Pfad | HEAD SHA-256 | HEAD Blob | HEAD Bytes/Zeilen | Worktree SHA-256 | Worktree Blob | WT Bytes/Zeilen | Diff +/- | Device/Inode |
|---|---|---|---|---|---|---|---|---|
| `live_l1/core/execution.py` | `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3` | `946e353070e7d12d7824338a6c8edf8a3e90322a` | `31600/951` | `85a9acb238dafd3adf5fd8bf57153772d3c7b41559943bdcce5336e3b60dcb5e` | `f321543f44acfc456fc4d0d07f9ccad038570ddd` | `46687/1386` | `+637/-202` | `2096/9286` |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | `12af0a3bbf90c1dc3254d68d617a246aaa60ffa2` | `50554/1411` | `e4db22642b628fe4b84cf0d2daa9ecd846208138eaa3868a02a56ddf9f75ee6c` | `0d363db2c38af649c28ab998fbd4e9212abd0ae1` | `68147/1947` | `+747/-211` | `2096/10943` |
| `live_l1/core/paper_iu4_adapter.py` | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` | `c7b2d3924e789e22013f9c84924d4804ce5064e5` | `24824/641` | `1fac2629a0ebdd889825f496e9273c358ffe7596c2173d307ce1d1eb7e9bd6a6` | `9ea724407c9a3bd48fd51231e1ff8f6f8bd37b1e` | `77178/1896` | `+1258/-3` | `2096/34521` |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `f81045347e82b981bd721bf1c4bbe0133feb8a36146f6440358983cac2ad6d4e` | `134a8e86dbb16a04a8d531448cb66ede7174360c` | `15298/403` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | `6cd5f6bfa62f8dbd8d3c94f121f91fa842696969` | `16619/438` | `+36/-1` | `2096/34697` |
| `live_l1/core/paper_iu4_startup_gate.py` | `86b191afb7725d613898d6911b543a84e9e0ada1f9c59822e3c47107272a6753` | `faf51735cf22a1279993a735c87439f516c1d9a1` | `21869/600` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | `f7da370d9f8e3538907cf14a91d39aa538bf3462` | `37668/919` | `+319/-0` | `2096/34523` |

Für alle fünf Worktree-Pfade gilt:

```text
Mode: 0444
UID/GID: 1000:1000
Device: 2096
Linkzahl: 1
Typ: reguläre Datei, kein Symlink
Encoding: UTF-8 ohne BOM
CR/CRLF: 0
Terminales LF: exakt vorhanden
Git-Status: tracked modified
```

Nur die Startup-Gate-Datei ist technisch für den vorliegenden Blocker
erforderlich. Die anderen vier Pfade bleiben Fremdzustand und ausgeschlossen.

## 10. Closure-Entscheidung

```text
P2C_T_B1_CLASSIFICATION: MANDATORY_SEPARATELY_PUBLISHED_P2C_PREREQUISITE_DEPENDENCY
P1_OWNED: NO
SHARED_P1_P2C_WORKSTREAM_REQUIRED: NO
P2C_OR_I6_CORRECTION_CASCADE_REQUIRED: NO
PREFERRED_RESOLUTION_PATH: A
```

Nach Bereitstellung der vollständigen gebundenen Startup-Gate-Worktree-
Identität sind sämtliche statisch auflösbaren Imports und Symbole der beiden
P2C-Dateien gegen den aktuellen Base verfügbar. Es besteht kein weiterer
statisch nachweisbarer Dependency-Blocker. Diese statische Closure beweist
keinen funktionalen, Runtime- oder Regressionstest-PASS.

## 11. Weg A — bevorzugte minimale Prerequisite-Resolution

Der einzige physische Source-Pfad eines späteren
P2C-T-B1-Prerequisite-Publication-Scope ist:

```text
live_l1/core/paper_iu4_startup_gate.py
SHA-256: c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd
Bytes: 37668
Zeilen: 919
Git-Blob: f7da370d9f8e3538907cf14a91d39aa538bf3462
```

Ein partielles Staging nur der Klasse ist unzulässig. Git publiziert den
vollständigen Blob. Dieser enthält gemeinsam die bereits I2–I6-gebundenen
Authorization-V2-, Restart-Authorization-, Reason-Code-, Loader- und
Export-Erweiterungen. Der vollständige Blob kann technisch eigenständig gegen
den aktuellen HEAD bereitgestellt werden, weil seine direkten und transitiven
Modulabhängigkeiten dort vorhanden sind.

Die übrigen vier tracked-unstaged Pfade bleiben ausgeschlossen. Die beiden
P2C-Dateien bleiben bis zur eigenen P2C-Publication untracked und dürfen in
einem Prerequisite-Staging nicht enthalten sein. Auch alle anderen
Working-Tree-Records bleiben ausgeschlossen.

Dieses Proposal ist ein separater Governance-Add. Seine Erstellung gibt ihm
keine Staging- oder Publication-Authority. Eine spätere Aufnahme erfordert
eine eigene unabhängige File-Exact-Rereview und ein neues ausdrücklich
autorisiertes Staging-Manifest.

## 12. Weg B — fail-closed Rückfallweg

Stellt eine spätere unabhängige Review oder Testvalidierung doch eine nicht
isolierbare direkte oder transitive Abhängigkeit fest, darf kein B1-Staging
erfolgen. Dann ist eine neue koordinierte Prerequisite-Publication-Closure
erforderlich, die sämtliche zusätzlich erforderlichen Pfade file-exakt bindet
und deren Ownership gegenüber P1 und P2C auflöst. Dieses Proposal autorisiert
diesen Weg nicht.

## 13. Weg C — separat mandatierte Korrekturkaskade

Erfordert die Resolution eine Änderung der historischen P2C-Test-,
I6-Evidence- oder sonstigen gebundenen Governance-Identitäten, ist eine neue
separat mandatierte Korrekturkaskade erforderlich. Sie muss sämtliche
Whole-file-Hashes, abhängigen Governancebindungen und Acceptance-Grenzen neu
berechnen. Eine solche Kaskade darf nicht stillschweigend erfolgen und wird
durch dieses Proposal nicht autorisiert.

## 14. Zwingende Gates vor einem erneuten P2C-T

### B1-G-R — Proposal-Rereview

Unabhängige File-Exact-Rereview dieses Kandidaten einschließlich physischer
Dateiidentität, Grundlagen, Tabellen, Scope, Authority-Aussagen und
Fail-closed-Grenzen.

### B1-R — Source- und Scope-Review

Unabhängige read-only Review der Startup-Gate-HEAD-/Worktree-Identitäten, des
vollständigen Diffs, des Klassenvertrags, aller Consumer, Tests,
Abhängigkeiten und der Ein-Pfad-Scope-Abgrenzung.

### B1-T — isolierte Testvalidierung

Eine neue ausdrückliche Autorisierung muss mindestens binden:

- temporären Tree aus dem dann aktuellen HEAD;
- Overlay ausschließlich der gebundenen Startup-Gate-Datei;
- separates Overlay der beiden P2C-Dateien nur für die fokussierte
  P2C-Testvalidierung;
- Syntax-/Import-Origin-Prüfungen ohne kanonische Artefakte;
- Startup-Gate-Tests;
- fokussierte P2C-Suite;
- Dependency-, Lifecycle-Ledger-, Atomic-v1-, Atomic-v2- und
  Regressions-Suiten;
- fail-closed Abbruch bei erster nicht freigegebener Abweichung;
- validierten vollständigen Temp-Cleanup;
- abschließende unveränderte kanonische Statusattestation.

### B1-S — Staging

Neues file-exaktes Staging-Manifest, neue Human-Autorisierung und expliziter
Ausschluss aller nicht gebundenen Pfade.

### B1-C — Commit

Eigener lokaler Commit erst nach erneuter Index-, Blob-, Manifest- und
Fremdzustandsattestation.

### B1-P — Push

Eigener Fast-forward-Push erst nach neuer ausdrücklicher Human-Autorisierung
und erneuter lokaler Precondition-Prüfung.

### B1-A — Post-Push-Attestation

Unabhängige lokale und ausdrücklich begrenzte Remote-Attestation des
veröffentlichten Prerequisite-Commits.

### G0-R und P2C-T-R

Nach B1-A ist eine erneuerte Scope- und Base-Attestation erforderlich. Erst
danach darf ein neuer vollständiger P2C-Testvalidierungsversuch separat
beantragt werden.

## 15. Fortbestehende Verbote und offene Grenzen

```text
P2C_T_RETRY_AUTHORIZED: NO
P2C_S_AUTHORIZED: NO
P2C_C_AUTHORIZED: NO
P2C_P_AUTHORIZED: NO
P2C_A_AUTHORIZED: NO
G0: NOT_READY
P1_AUTHORIZED: NO
G2_AUTHORIZED: NO
E1: OPEN_FAIL_CLOSED
E2: OPEN_FAIL_CLOSED
E3: OPEN_FAIL_CLOSED
I7_EVIDENCE_BOUNDARY: OPEN_FAIL_CLOSED
I7_ACCEPTANCE_BOUNDARY: OPEN_FAIL_CLOSED
I7_EXECUTION_BOUNDARY: OPEN_FAIL_CLOSED
LIVE_BOUNDARY: OPEN_FAIL_CLOSED
EXCHANGE_BOUNDARY: OPEN_FAIL_CLOSED
```

Keine Aussage dieses Dokuments ist eine selbstständige Evidence oder
Acceptance. Keine Recovery-, Completion- oder Lifecycle-Aussage autorisiert
einen Loop-Start. Keine I7-, Live- oder Exchange-Grenze wird geschlossen.
