# PRE-IU4 I7 Preparation Resolution 4 — File Exact

## Urteil, Grenzen und controlling Findings

```text
I7_PREPARATION_RESOLUTION_4: COMPLETE
I7_PREPARATION_STATUS: BLOCKED_PENDING_EXTERNAL_INPUTS
I7_VALIDATION_EXECUTED:NO
I8_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

`COMPLETE` bedeutet ausschließlich: Die sechs Findings R4-F1, R4-F2, R4-F4,
R4-F5, R4-F7 und R4-F8 der unabhängigen File-Exact-Rereview von Resolution 3
sind innerhalb der acht genehmigten Dateien geschlossen. R3-F3 und R3-F6
bleiben regressionsgebunden geschlossen. Es ist kein I7-Validierungs-,
Aktivierungs- oder Produktionsurteil und keine Selbstzertifizierung.

Die folgenden drei externen Grenzen bleiben ausdrücklich fail-closed offen:

- E1: kein unabhängig akzeptierter realer Capability-Runner und kein
  vollständiges Szenariomanifest;
- E2: keine real befüllten disposable Host-/VM-/QMP-/SSH-/Privilege-
  Koordinaten und keine menschliche Autorität;
- E3: kein unabhängiger realer Prozess-/Kernel-/BPF-/VM-Collector.

Controlling Rereview: Task `01a0326d-d364-7b60-8079-4df396f5367b`, Host
`local`, Ergebnis `I7_PREPARATION_RESOLUTION_3_INDEPENDENT_ACCEPTANCE:
NOT_READY`. Zusätzlich vollständig read-only gebunden: Resolution 3 Task
`01a03252-6551-7c60-90f5-554cce1901b0`, vorausgehende Rereview Task
`01a03245-03dc-7890-8427-54602479b034`, Resolution 2 Task
`01a02fd3-26a1-7792-ba8c-f98dac17df52`, I7-Preparation Task
`01a02f75-1b59-7f20-9df0-cf1de9ff8adc` und externe I6-Acceptance Task
`01a02f64-a5b1-79d2-ace9-193e730b0135`.

## F1 — Governance-Closure

Die terminale Specification-/I1–I6-Kette ist nachstehend vollständig mit
Pfad, Rolle, SHA-256 und Zeilenzahl gebunden. Alle Hashes sind vollständig.

| Phase/Rolle | Pfad | SHA-256 | Zeilen |
|---|---|---|---:|
| Specification | `docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md` | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` | 4605 |
| Spec independent rereview | `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md` | `6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c` | 752 |
| Spec terminal handoff | `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_TERMINAL_R3_HANDOFF_2026-08-19.md` | `0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e` | 140 |
| Spec final attestation | `docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_FINAL_R3_ATTESTATION_2026-08-19.md` | `587c5a5ffed271534d661c6c816781eb8443d5c6318fe14d26b1947d21340851` | 179 |
| I1 mandate | `docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_FILE_EXACT_MANDATE_2026-08-19.md` | `2b235193bb7d2986cac3a42e3b078569e1c5e1070e315f6b6b99cc99823bad4a` | 296 |
| I1 evidence | `docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_IMPLEMENTATION_EVIDENCE_2026-08-19.md` | `24328abbb0e918b0ff5009e32cb026b8624c26dd2bc66fcae49789df55f4b856` | 318 |
| I1 terminal independent rereview | `docs/review/PRE_IU4_I1_CHARACTERIZATION_PURE_CONTROL_EXTRACTION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2_2026-08-19.md` | `adc13abbec3a0458d712df729c2732bce8897be7ecf991a312839616e9687804` | 391 |
| I2 mandate | `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_FILE_EXACT_MANDATE_2026-08-19.md` | `bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517` | 311 |
| I2 evidence | `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_EVIDENCE_2026-08-19.md` | `950b5b2aa11f3163f0aa1f49f03528ce688de1a5c7506cd12b905dadc55bd516` | 1215 |
| I2 review resolution | `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REVIEW_RESOLUTION_2026-08-20.md` | `fbaf549867ea70ef1214204851da52b530bbf47e80762bd37086cdedec86ba53` | 158 |
| I2 collector supplemental decision | `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_COLLECTOR_SUPPLEMENTAL_FILE_EXACT_MANDATE_DECISION_2026-08-20.md` | `a69bced4751ebbd608b0ff081079f5021c5f57430ec93c478e6b0b90c6c76228` | 171 |
| I2 terminal independent rereview | `docs/review/PRE_IU4_I2_LIFECYCLE_LEDGER_RUNTIME_GATE_AUTHORIZATION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_2026-08-20.md` | `5a59ad8c97ebae85148661fe0e3bedab643c7f12ae2c8d4e87272447c0616679` | 300 |
| I3 mandate | `docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_FILE_EXACT_MANDATE_2026-08-20.md` | `775aeb62e6ff0a1ca3af970970053b43d176f1122560774f184ecf40a8fcced5` | 558 |
| I3 evidence | `docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `20846284ffad9e8b755dd6a3b74f963d8d2c6ee1519fafdd0bc1275f2e33c390` | 463 |
| I3 terminal resolution | `docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_REREVIEW_5_EVIDENCE_PRECISION_RESOLUTION_FILE_EXACT_2026-08-20.md` | `00fb12135197a5fa8aefa8bf149c03904b9440d7909eb5a218cde5cfa38f7b5d` | 156 |
| I3 terminal independent rereview | `docs/review/PRE_IU4_I3_ATOMIC_STATE_TRANSACTION_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_6_2026-08-20.md` | `03790420534e38c7e36d1824a472dfd80763340dacec8847ddf5072d55db0c9f` | 191 |
| I4 mandate | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_2026-08-20.md` | `e4039400d24781c9d1911b7b7448e49773d92e7134f8ecee1042cdf47438c3f1` | 601 |
| I4 mandate terminal rereview | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_2_2026-08-20.md` | `b83d869b38b0afeafaad41e98240ffec5a66af6f6175c8f0572092ad14b5ee7e` | 250 |
| I4 evidence | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `068c2ba2661031843a13dd3f2c4684f9340f432b90b192b6b7492dae8968270d` | 403 |
| I4 terminal resolution | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_REREVIEW_2_EVIDENCE_PRECISION_RESOLUTION_FILE_EXACT_2026-08-20.md` | `e77900fae23617facaf04b2078e3a4662c8d805733a00063db1bcb4f553522d3` | 168 |
| I4 terminal independent rereview | `docs/review/PRE_IU4_I4_ADAPTER_REQUEST_V2_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md` | `c6d8bbcb35572a364b74a47eb9ad817240a8b0cce70e514942bb674d3861c38b` | 191 |
| I5 durable-denial mandate revision | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_2026-08-20.md` | `a688773cc10dd6c573e7c019245639c010a3b0abb49fb301249aeebeba182a91` | 633 |
| I5 durable-denial mandate rereview | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_FILE_EXACT_MANDATE_REVISION_INDEPENDENT_READONLY_REREVIEW_2_2026-08-20.md` | `934bf4a9010aff61796cc2c7c09f54380c5527546bea6e4bc25b5a17933bfd59` | 242 |
| I5 durable-denial resolution | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-20.md` | `4512288b16541f659b434000114853f05e457acf5df4e3e779c14b03d44b2985` | 237 |
| I5 active-seam evidence | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `33d18b64bc92d0f5631d3a8306010e8889bb69085d7ce4e77c36c1fd1e185b65` | 633 |
| I5 durable-denial independent rereview | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_DURABLE_DENIAL_PROVENANCE_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md` | `9031ec6ef31d61787d46082dab50c59823bb0ba45155cba2b9abc5928f6d96d9` | 246 |
| I5 active-seam resolution, distinct identity | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_REREVIEW_2_RESOLUTION_FILE_EXACT_2026-08-20.md` | `4a11786ef353b84ad9384da3fd35fcb1857fc323d9f1fb963e7155dd4da0766e` | 224 |
| I5 active-seam independent rereview, distinct identity | `docs/review/PRE_IU4_I5_ACTIVE_EXECUTION_SEAM_IMPLEMENTATION_INDEPENDENT_READONLY_FILE_EXACT_REREVIEW_3_2026-08-20.md` | `5b825372b313ead079ef0680e8410a552a2e72d05a0f4abb7e1fa88739212496` | 277 |
| I6 mandate | `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_2026-08-20.md` | `9d9bdacb5f907f9e9927dc7c7d3ecec25718ccb448b6f69acff0ad6baf1a4dc6` | 1281 |
| I6 terminal mandate rereview | `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_MANDATE_INDEPENDENT_READONLY_REREVIEW_5_2026-08-21.md` | `f5cd16f783322f18b98475fa9912183bc4d1f960e147eee1e1065f3aba58f9fe` | 268 |
| I6 evidence | `docs/review/PRE_IU4_I6_RECOVERY_MONITORING_PROJECTION_FILE_EXACT_IMPLEMENTATION_EVIDENCE_2026-08-20.md` | `5a733d7deb9d34633bea8718bda8e0749558810426e5985f8f3335b500789834` | 1074 |

Die zwei zuvor vertauschten I5-Paare sind damit über ihre unterschiedlichen
Pfade, Rollen, vollständigen Hashes und Zeilenzahlen eindeutig getrennt.

Externe I6-Acceptance: `I6_INDEPENDENT_ACCEPTANCE: READY`, Task-ID wie oben;
I6-Evidence-Payload
`a0681ceee96ecb22c3441ca0e225b8891f6368eb33b8d737b46f760e4c731cd7`.

| I6 Implementierungsdatei | SHA-256 | Zeilen |
|---|---|---:|
| `live_l1/state/paper_atomic_coordinator.py` | `b8ce5ba89016cac8e34ee2646f3bf9746b2909fa3b7c9e1ef6c74557c3aaffcb` | 6020 |
| `live_l1/state/models.py` | `b9bc3b9a598fefeef83a2905432daf924ccf54e9701f313e2af99a6a8e833f53` | 125 |
| `live_l1/state/state_store.py` | `b742131ba8af8e9c34157244de5cd743a045b7ae985dd4b502486e71fd2011c9` | 594 |
| `live_l1/state/paper_iu4_recovery_projection.py` | `b12f3ece36dea4a83faddee5db43c1964884ba25a03bacaae476d22cdea77946` | 6033 |
| `tests/live_l1/test_paper_iu4_recovery_projection.py` | `57a45dbf6b6bc56152c8c328c0d15992ab0345278cb6fa30667b6e902183e1c9` | 5307 |
| I6 Evidence | `5a733d7deb9d34633bea8718bda8e0749558810426e5985f8f3335b500789834` | 1074 |

## Historischer Resolution-2-Stand (nicht autoritativ)

Die folgenden Abschnitte F2–F7 und ihre damaligen Run-Attestations bleiben als
historische Resolution-2-Evidence erhalten. Sie werden durch die autoritative
Resolution-3-Closure weiter unten ersetzt; insbesondere sind historische
Run-Roots nicht als frisch identisch reproduzierbar behauptet.

### F2 — Gepinnter Harness und Importabschluss

- CLI besitzt keinen Manifest- oder Schema-Pfadparameter. Nur die kanonischen
  Pfade werden akzeptiert; Manifest SHA
  `d3f5e0b8540b3a2ab5cb9b2c5256a06cd0490477b966bcd0dab81dd3035324f1`
  und Schema SHA
  `c864c809a541fd13a52c63cd6e7e536532dd8ff1b5c6c96cc3d5463edf96e612`
  sind codegepinnt. Mode 0644, UID/GID 1000, no-symlink, no-hardlink,
  nofollow/readback und Schema-ID werden geprüft.
- JSON ist ASCII, CR/NUL-frei, single-terminal-LF, duplicate-key-fail-closed;
  exakte Builtin-Typen verhindern Bool-as-Int, missing und unknown fields.
- Startmodule, Gate-IDs und Counts sind zusätzlich codegepinnt.
- Relative/from/alias Imports, lokale Missing Edges, nichtliterale
  `importlib`/`__import__`, aufgerufene `getattr`-Importkonstruktionen,
  Forbidden-Module, Symlinks und resolved-realpath-Escapes sind fail-closed.
- Implizite Paketinitialisierer werden vollständig aufgenommen. Der aktuelle
  37-Start-Census besitzt 104 Dateien, 262 syntaktische Kanten und 144
  zusätzliche implizite Initializer-Kanten, insgesamt 406. Resolution 1 hatte
  die 104 Dateien auf 98 reduziert und 271 syntaktische Kanten behauptet.
- File identities binden Pfad, Realpath, SHA-256, Größe, Mode, UID/GID,
  Device/Inode. Plan und alle Quellen werden unmittelbar vor Spawn erneut
  gelesen und verglichen.

### F3 — Safe Partition, Census und Prozessgruppen

- Der historische Satz bleibt ausschließlich `full_live_census_only`: 37
  Starts, 584 echte statisch abgeleitete Cases, kein Ausführungsclaim.
- Nach dem strengeren Abschluss enthält er 1 dynamische Importkante
  (`test_paper_iu4_recovery_projection.py:2272`), 1 unaufgelöste lokale
  Namespacekante (`test_safe_launch_iu4_shadow_runtime_gate.py` nach
  `live_l1.tools`) und 61 konservative Effektkanten. Alle 37 Starts bleiben
  im Manifest explizit deferred; insbesondere Guardian und Persistence Worker.
- Ausführbar sind nur Preparation (6 Dateien/7 Kanten/12 Cases) und Replay
  (2 Dateien/1 Kante/3 Stufen); beide haben 0 forbidden, 0 dynamic,
  0 unresolved und 0 deferred effect edges.
- Jeder Gate-Prozess erhält eine neue Session/Prozessgruppe. Monotone per-Gate-
  und globale Timeouts führen ohne Retry über TERM, begrenztes Warten, KILL,
  `communicate`/`wait` und Gruppen-Leakprüfung zum vollständigen Reap.
- Der adversariale Test startet ausschließlich einen synthetischen Child und
  Grandchild, beide TERM-resistent; KILL/Reap und kein Rest-PID wurden bestätigt.
  Kein Guardian- oder anderer deferred Start wurde ausgeführt.

### F4 — Observer

Snapshot-V2 bindet exact schema/artifact, Contract-ID, Run-ID, Rolle PRE/POST,
Sequenz 0/1, `captured_at_ns`, Observer-SHA, vollständige geordnete Kategorien
und kanonischen Snapshot-Hash. PRE und POST müssen verschieden und zeitlich
monoton sein. Im PRE vorhandene run-owned Ressourcen sind unzulässig;
vorbestehende Ressourcen müssen im POST bytegleich vorhanden sein; jedes
Residuum, Fremd-Owner oder Observerwechsel ist FAIL.

Cleanup-Ziele binden `resource_type`, `stable_id`, Fingerprint, `owner_run_id`,
Source-Snapshot-Hash und eine eng erlaubte Operation. CLI-Eingänge und Output
liegen no-symlink/traversal-frei unter einem gebundenen existierenden
`/tmp`-Runroot. Der Evaluator sammelt und löscht keine reale Ressource; E3
bleibt offen.

### F5 — Workstation-Contract

Schema-V2 ist code-/hashgepinnt, besitzt keine unbekannten Felder oder
operativen Defaults und verlangt Host/Kernel/Boot/LSM/BTF/vmlinux/bpffs,
cgroup, vier Namespaces, Yama, VM/QEMU/QMP, SSH/Key/known_hosts, Compiler,
Linker, sudo, Privilege-/Suspend-/BPF-/LSM-/cgroup-/namespace-, Observer-,
Restore-/Reboot-/Discard- und Cleanup-Autoritäten.

17 eindeutige file-backed Inputrollen werden mit absolutem traversal-freiem
Pfad, Confinement-Root, SHA-256, Größe, Mode, UID/GID, Device/Inode,
Symlink-/Hardlinkfreiheit, nofollow/open/fstat/readback/lstat und
Permissions geprüft. World-writable, Owner-, Hash-, Mode-, Alias- und
Private-Key-Konflikte schließen fail-closed. Bei fehlender `O_NOATIME`-
Berechtigung ist ein Readback nur zulässig, wenn atime und alle übrigen
Identitätsmetadaten exakt unverändert bleiben.

Capability-Szenarien und Startup-Szenarien sind eindeutige ID-Listen. Totals
werden ausschließlich als `len(ids)*10000` und `len(startup_ids)*32`
hergeleitet. Resolution 2 enthält keinen realen Contract; E2 und E1 bleiben
offen.

### F6 — Replay

Stage-IDs und Reihenfolge sind codegepinnt; Verzeichnisnamen sind separate
Konstanten und erhalten nie Autorität aus Stage-IDs. Create-new `/tmp`-Root,
no-symlink/resolve/confinement und create-new Stage-Artefakte verhindern
Traversal, absolute Escapes und Wiederverwendung.

Fixture, Economics-Profile, Policy und Seed sind mit Pfad, SHA-256, Größe,
Zeilen, Encoding und Schema-ID gebunden und werden vor jeder Stage erneut
nofollow/fstat/readback/lstat-validiert. Fixture-CSV erzwingt Header,
Kardinalität, UTC-Sekunden, monotone Timestamps, endliche `Decimal`-Werte und
exakte Integerflags. Seed ist explizit ASCII/CRLF mit terminalem LF gebunden;
die übrigen Inputs sind ASCII/LF. JSON duplicate keys, malformed rows, alte
Artefakte und Inputabweichungen sind FAIL.

S1 verarbeitet 3/3; S2 serialisiert, hashprüft und restauriert nach Schritt 1
und verarbeitet 3/3; S3 trunciert den gebundenen Restartstate, erkennt den
Fehler, verarbeitet 1/3 und setzt `continuation_blocked=true`. Kein ENFORCED,
Exchange oder Live.

### F7 — Preservation und finale Evidence

Vor und nach jedem Gate enumeriert der Harness über identische Git-config-/
ignore-Semantik tracked, untracked und ignored Dateien, jedoch nie `.git`.
Gebunden werden Membership, Bytes, Mode, UID/GID, Device/Inode, Linkcount,
ns-atime/mtime/ctime und Symlinkziel. Verbotene Quellinhalte und PYC-Inhalte
werden explizit ausgeschlossen, ihre Metadaten bleiben gebunden. NUL-Porcelain
und Git-config-Hashes sind Teil des Manifests. Byte-, Metadaten-, bereits
untracked- und ignored-Änderungen verändern den Vergleich.

`repository_output_count` ist die reale Zahl geänderter Pfade, nicht konstant.
Gate-Evidence bindet RC, Counts, stdout/stderr, Import-/Effektclosure,
Pre/Post-Preservation und Leak/Cleanup. Danach bindet eine finale Attestation
Gate-Evidence und alle bis dahin vorhandenen Artefakthashes. Ihre exakte
Payloadgrenze ist der kanonische Attestation-Base ohne das eigene
`attestation_sha256`-Feld; es gibt keinen Selbstreferenzclaim.

### Historisch ausgeführte Resolution-2-Commands und Ergebnisse

Alle Python-Läufe: frische `/tmp`-Wurzel, `PYTHONDONTWRITEBYTECODE=1`, eigenes
`PYTHONPYCACHEPREFIX`, `TMPDIR`, isoliertes `HOME` und explizites
`GIT_CONFIG_GLOBAL=/home/benja/.gitconfig` bei Harnessläufen.

1. Statische Plans:
   - Preparation: 6 Dateien, 7 Kanten, 12 Cases, 0/0/0/0; RC 0.
   - Replay: 2 Dateien, 1 Kante, 3 Stufen, 0/0/0/0; RC 0.
   - Census: 37 Starts, 104 Dateien, 406 Gesamtkanten, 584 Cases, 1 dynamic,
     1 unresolved, 61 effects; ausschließlich deferred, nicht ausgeführt.
2. Fokustest diagnostisch 1: 12 gestartet, 3 Errors, RC 1; kein PASS.
3. Fokustest diagnostisch 2: 12 gestartet, 1 Error, RC 1; kein PASS.
4. Finaler Fokustest: 12/12, RC 0, keine Failure/Error/Skip.
5. Preparation-Harness: 12/12, RC 0; Gate-Evidence-Payload
   `296efea84fc2e1e40e48bccf8e1412e5d4dc7af1796e62a014ce33c04bd4fe4f`;
   Gate-Evidence-Datei
   `b477c8def23f1cfb1be1022eba6ee077d4eb79ba3ab5a7770898a4b1cd088b2c`;
   finale Attestation
   `865d210f698519131184620780708e33206aa7df37d13580af3804230217d0ea`.
6. Replay-Harness: 3/3, RC 0; Gate-Evidence-Payload
   `2ecfd833cbc664febc687630263d06d7cead6aa842e5a6442c33860809303b11`;
   Gate-Evidence-Datei
   `080ff6c6d82c87f077635c51ac1a3d74c2cb4b23fbf04ec1e1aa4e11fb02d8c9`;
   finale Attestation
   `6b1c12581f0075eab236656ddfa11a8748a06d3d2c8f2e3fa3df6db26057c8cf`.
7. Beide Harnessläufe: Preservation
   `1658acf37943eee763efe785f181225f36aa94cdfbc0f3ff44971ee54879cc8c`
   vor/nach identisch, `repository_output_count=0`, Gruppen gereapt.
8. `py_compile` exakt vier Resolution-Pythondateien: RC 0, exakt vier PYC nur
   unter `/tmp/iu4-i7-r2-compile.fBkSqJ/pycache`.
9. AST 4/4 und striktes JSON 2/2: RC 0.
10. `git diff --check`: RC 0; `git diff --cached --check`: RC 0.
11. Full `tests/live_l1`, 584-Census, Capability, Workstation, Collector und
    Regression wurden nicht ausgeführt. Regression ist nicht anwendbar, weil
    kein aktiver Runtime-Code verändert wurde.

### Historischer Resolution-2-Sieben-Dateien-Stand

| Pfad | SHA-256 | Zeilen |
|---|---|---:|
| `live_l1/tools/i7_file_exact_harness.py` | `46c46ab8f03238db954198e3baf985ddd8efdc73581a64312dc33d828bced5dc` | 1053 |
| `live_l1/tools/i7_staged_synthetic_replay.py` | `e89d10c1a8b6a1061b9599360d5b2533a0b90fad19c6fedad308024ca31ad5be` | 457 |
| `live_l1/tools/i7_file_exact_observer.py` | `baaf6d9a1aee48a4a4f89b64f8bb4f684eeecfcd0cf1b45b30c79a204187e65f` | 424 |
| `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | `d3f5e0b8540b3a2ab5cb9b2c5256a06cd0490477b966bcd0dab81dd3035324f1` | 163 |
| `config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json` | `c864c809a541fd13a52c63cd6e7e536532dd8ff1b5c6c96cc3d5463edf96e612` | 139 |
| `tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt` | `e7a1723a7bc766c4dbd3f1961e801a8a14e8e8b68a59f880afd1e8da94ffd915` | 4 |
| `tests/live_l1/test_i7_file_exact_preparation.py` | `a0694c793012dae493de8fe2b007cc29ec3893c9ddd6b784922f6cb54b68f1b7` | 557 |

Dieses Dokument ist der achte Scope-Pfad. Sein Whole-file-Hash und seine
Zeilenzahl werden nach dem Einsetzen der einzigen finalen Binding-Zeile extern
berichtet. Payload ist exakt der gesamte Dateiinhalt bis unmittelbar vor der
finalen Binding-Zeile, einschließlich des LF der vorherigen Leerzeile. Die
Binding-Zeile selbst und ihr terminales LF sind ausgeschlossen.

### Historische Resolution-2-Preservation

- I6-Sechs-Dateien: 6/6 exakt; I6-Preservation: 22/22 exakt.
- Freeze-Manifest:
  `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16`,
  60 Zeilen, 0444.
- Freeze-Tar:
  `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037`,
  1318/1318 eindeutige Einträge, gzip PASS, 0444.
- Fremdzustandsbasis ohne acht Scope-Dateien: 10 modified, 132 untracked,
  0 staged, 142 Einträge; NUL-SHA
  `b25c5f1e1244cac1c61f015e2c6a36798d5cd707cc05b8c61923c8d068c62987`;
  Byte-/Metadaten-SHA
  `3d74bb8ac2aefbe26f62a210c262eced70a50bb1f695f10de7f18871a4ff7fea`.
- Keine Git-Mutation, kein Cleanup fremder Artefakte, kein Repository-PYC,
  keine operativen Verzeichnisse und keine ignorierten eigenen Reste.

## Autoritative Resolution-3-Closure R3-F1 bis R3-F8

### R3-F1 — Dynamic-Alias-Closure

Assignment, AnnAssign, NamedExpr, Tuple/List-Unpacking und mehrstufige
Aliasbindungen für `importlib.import_module`, `__import__` und `getattr`
werden verfolgt. Attribute, Subscripts, Lambda-, Default- und Closure-Bindungen
sowie Rebinding/Schattennamen werden konservativ als konkrete dynamic Findings
mit Pfad, Zeile, Spalte, Symbol, Call, Reason und Ziel gebunden. Die drei
Rereview-Reproduktionen und acht zusätzliche Varianten sind adversarial grün;
Unsicherheit wird nicht als resolved akzeptiert.

### R3-F2 — Authentische unittest-Ergebnisautorität

Der feste Child-Runner lädt `unittest` programmgesteuert. Ein vor Spawn mit
`O_EXCL|O_NOFOLLOW`, Mode 0600 und gebundener Device/Inode-Identität erzeugter
FD-Kanal bindet Nonce, Gate, Startmodule, Expected Count, Child-PID und Run-ID.
Der Parent akzeptiert ausschließlich exact JSON ohne duplicate keys mit exakt
12 Tests sowie je 0 Failures, Errors, Skips, Unexpected Successes und Expected
Failures. Bare, fake, fremde und multiple Summarys liefern niemals Autorität;
Replay oder Nonce/PID/Gate/Count-Abweichung ist FAIL.

### R3-F3 — Git-/Ignore-Semantik

System/global/local Git-Konfiguration, `core.excludesFile`, das implizite
`XDG_CONFIG_HOME/git/ignore` und `.git/info/exclude` werden mit Pfad,
Present/Absent, SHA-256, Mode, UID/GID, Device/Inode und ns-Metadaten gebunden.
Der Child erhält isoliertes HOME, aber explizit dieselbe wirksame
`XDG_CONFIG_HOME`-/`GIT_CONFIG_GLOBAL`-Semantik. Normal und isoliert besitzen
denselben NUL-Status; `.claude/settings.local.json` erscheint nicht zusätzlich.
Der semantische Git-config-Hash schließt Ignore-Inhalte ein und ändert sich bei
abweichender Ignore-Semantik; der rohe Config-NUL-Hash bleibt separat sichtbar.

### R3-F4 — Observer Authority, Freshness und Parent Chains

Contract-ID ist ausschließlich `IU4_I7_OBSERVER_SNAPSHOT_V2`. Ein create-new
Runroot unter `/tmp` erzeugt exklusiv Nonce/Sentinel und leitet die Run-ID als
`SHA256(contract_id NUL nonce)` her. Sentinel, Root Device/Inode, Owner, Mode
0700 und Freshnessfenster sind gebunden; stale, consumed und reused Roots sind
FAIL. PRE/POST und Cleanup verwenden dieselbe Authority. Jeder Input-/Output-
Parent wird FD-relativ mit `O_DIRECTORY|O_NOFOLLOW` geöffnet und nach Nutzung
gegen Parent-Swap revalidiert; Snapshot-Replay, arbitrary IDs, Parent-Symlinks
und Hardlinks sind FAIL. E3 bleibt offen: der Evaluator sammelt nichts real.

### R3-F5 — Workstation Parent-Chain-Confinement

Alle 17 file-backed Rollen binden zusätzlich Root Mode, UID/GID, Device und
Inode. Vom gebundenen Root bis zum Leaf wird jede Komponente FD-relativ
nofollow geöffnet; Parents müssen Directory, erwarteter Owner/Device und nicht
group/world-writable sein. Leaf ist regular, nlink 1 und vollständig
fstat/readback/stat-gebunden. Innen-/Außen-/Nested-Symlink, Parent-Swap,
Hardlink, world-writable Root sowie falscher Owner/Mode sind adversarial FAIL.

### R3-F6 — Replay Exact Schema

Profile und Policy besitzen vollständige exakte Feldmengen, Builtin-Typen,
Werte und Cross-Bindings. Unknown, missing, nested-extra, wrong-type und
Cross-Binding-Abweichungen bleiben auch mit passend neu berechnetem Inputhash
FAIL. Alle vier Inputs werden vor jeder Stage über vollständige nofollow-
Descriptor-Ketten erneut hash-/metadata-validiert; LF/CRLF-Verträge bleiben
unverändert. S1=3/3, S2=3/3, S3=1/3 und continuation-blocked=true.

### R3-F7 — Vollständige Closure-Topologie

Jeder Closure-Record bindet sortierte Kanten mit `from_path`, `from_module`,
`to_path`, `to_module`, `edge_type`, `resolution_status`, Zeile und Spalte.
Forbidden, dynamic, unresolved und effects sind sortierte konkrete Listen;
Counts werden ausschließlich aus diesen Listen hergeleitet.

Preparation bindet sechs Dateien und sieben resolved/topology Kanten:

1. Harness -> `live_l1/__init__.py`, implicit-init.
2. Observer -> `live_l1/__init__.py`, implicit-init.
3. Replay -> `live_l1/__init__.py`, implicit-init.
4. Fokustest -> Harness, direct.
5. Fokustest -> Observer, direct.
6. Fokustest -> Replay, direct.
7. Fokustest -> `tests/live_l1/__init__.py`, implicit-init.

Damit: 3 syntaktische + 4 implizite Kanten, 0 forbidden/dynamic/unresolved/
effects. Replay bindet zwei Dateien und exakt eine implicit-init-Kante, ebenfalls
0/0/0/0. Der nicht ausgeführte 37-Start-Census bleibt historisch als 262
syntaktische + 144 implizite resolved Kanten, 1 dynamic, 1 unresolved und 61
effects vollständig deferred. Resolution 3 hat keine lokale Importkante
hinzugefügt; ein frischer Census-/584-Lauf wurde ausdrücklich nicht ausgeführt.

### R3-F8 — Deterministic Semantic Root und Run Attestation Root

`deterministic_semantic_root` bindet nur normalisierte Gate-ID, exakte Counts,
authentisches Resultat ohne PID/Nonce/Run-ID, vollständige Closure,
Preservation-/Git-Semantik, Cleanup/Leak und PASS. Zeiten, PIDs, zufällige IDs,
temporäre absolute Pfade und volatile unittest-Dauer fehlen dort.
`run_attestation_root` bindet zusätzlich Raw-Artefaktmanifest, stdout/stderr,
ns-Zeiten, PID, Nonce, Run-ID und Runroot. Zwei frische äquivalente Preparation-
Läufe ergaben denselben Semantic Root
`6dedb70f47b67b96789aa9ec34498f400c8da9301a0594106691750bd0a21f7a`,
aber verschiedene Run Roots
`5dd7b74a32cd315e546def7d84e4db81a6f4e82a63f26fe2b1f42c2b84a9169e`
und `ca6ade42b87d5b16d4fa22a963a5c9ae3b8855213a92a36b7e5b232d38db1647`.
Replay: Semantic Root
`f7de07f8d33922b0ed90b411cab328f43d132e7d54a6d71bff934bf3e8140cc1`,
Run Root `bf25e7d8ff0c53fad24e6e1fee5e8c8d23147a40335c82b4c4d6c98c62a26661`.
Semantik-/Closure-Tamper ändert den Semantic Root; Raw-Tamper mindestens den
Run Root. Historische Resolution-2-Run-Roots bleiben nur damalige Belege.

## Autoritative Resolution-4-Closure

R4-F1 verfolgt Rückgabewerte benannter lokaler Funktionen sowie `IfExp`,
`BoolOp`, verschachtelte Call-/Lambda-/Container-Ausdrücke und Rebindings
konservativ. Unsichere wertliefernde Kombinationen erzeugen konkrete dynamic
Findings; harmlose Factory-/IfExp-/BoolOp-Gegenbeispiele bleiben finding-frei.

R4-F2 verwendet keinen seek-/truncate-fähigen Resultatdatenträger mehr. Der
Parent liest genau einen terminalen strict-JSON-Record aus einer Pipe. Nur der
codegehashte feste Supervisor erbt deren Writer; der eigentliche unittest-
Worker läuft mit `close_fds=True` und prüft zusätzlich, dass der Writer-FD
geschlossen ist. Mehrfach-/Teilwrites, Fremdpräfixe, Duplicate JSON, Replay,
Nonce-/Gate-/PID-/Run-/Startsatz-/Count-Abweichung und jeder nicht-null
Failure/Error/Skip/Unexpected-/Expected-Failure-Count sind FAIL.

R4-F4 leitet die Run-ID aus kanonischem Contract, Nonce, create-new Root-
Device/Inode und create-new Sentinel-Device/Inode ab. Authority bindet Root und
Sentinel einschließlich Owner/Mode. Snapshotordnung ist
`created_at_ns <= PRE < POST`, freshness-begrenzt und rollengebunden;
identische Authority-/Snapshotpaare sind nur einmal konsumierbar. Der CLI-
Completion-Sentinel sperrt zusätzlich prozessübergreifende Wiederverwendung.

R4-F5 bindet für alle 17 Rollen eine exakte geordnete `parent_chain` von `/`
bis zum Leaf-Parent mit logischem Pfad, Komponente, Device, Inode, UID/GID,
Mode und Directory-Art. Sämtliche Opens und Revalidierungen sind descriptor-
relativ mit `O_NOFOLLOW`; die komplette Kette einschließlich lexikalischem
Root-Eintrag wird vor Leaf-Nutzung und nach Read revalidiert. Root-/Parent-Swap,
Symlink innen/außen/nested, Hardlink, unsicherer Parent und Metadata-Tamper
sind FAIL.

R4-F7 bindet die zwei frischen lokalen Closure-Records nachstehend vollständig.
Alle Counts werden in Code aus den serialisierten Listen/Kanten hergeleitet und
vor semantischer Nutzung erneut verifiziert. Leere Finding-Listen sind
ausdrücklich enthalten. Die historische 37/584-Topologie bleibt deferred und
wurde nicht ausgeführt.

<!-- BEGIN_PREPARATION_CLOSURE_RECORD_JSON -->
{"dynamic_import_count":0,"dynamic_imports":[],"edge_count":7,"edges":[{"call":"package-initializer","column":0,"edge_type":"implicit_init","from_module":"live_l1.tools.i7_file_exact_harness","from_path":"live_l1/tools/i7_file_exact_harness.py","line":0,"reason":"implicit-package-initializer","resolution_status":"RESOLVED","symbol":"","to_module":"live_l1","to_path":"live_l1/__init__.py"},{"call":"package-initializer","column":0,"edge_type":"implicit_init","from_module":"live_l1.tools.i7_file_exact_observer","from_path":"live_l1/tools/i7_file_exact_observer.py","line":0,"reason":"implicit-package-initializer","resolution_status":"RESOLVED","symbol":"","to_module":"live_l1","to_path":"live_l1/__init__.py"},{"call":"package-initializer","column":0,"edge_type":"implicit_init","from_module":"live_l1.tools.i7_staged_synthetic_replay","from_path":"live_l1/tools/i7_staged_synthetic_replay.py","line":0,"reason":"implicit-package-initializer","resolution_status":"RESOLVED","symbol":"","to_module":"live_l1","to_path":"live_l1/__init__.py"},{"call":"direct","column":0,"edge_type":"direct","from_module":"tests.live_l1.test_i7_file_exact_preparation","from_path":"tests/live_l1/test_i7_file_exact_preparation.py","line":18,"reason":"resolved-local-import","resolution_status":"RESOLVED","symbol":"live_l1.tools.i7_file_exact_harness","to_module":"live_l1.tools.i7_file_exact_harness","to_path":"live_l1/tools/i7_file_exact_harness.py"},{"call":"direct","column":0,"edge_type":"direct","from_module":"tests.live_l1.test_i7_file_exact_preparation","from_path":"tests/live_l1/test_i7_file_exact_preparation.py","line":19,"reason":"resolved-local-import","resolution_status":"RESOLVED","symbol":"live_l1.tools.i7_file_exact_observer","to_module":"live_l1.tools.i7_file_exact_observer","to_path":"live_l1/tools/i7_file_exact_observer.py"},{"call":"direct","column":0,"edge_type":"direct","from_module":"tests.live_l1.test_i7_file_exact_preparation","from_path":"tests/live_l1/test_i7_file_exact_preparation.py","line":20,"reason":"resolved-local-import","resolution_status":"RESOLVED","symbol":"live_l1.tools.i7_staged_synthetic_replay","to_module":"live_l1.tools.i7_staged_synthetic_replay","to_path":"live_l1/tools/i7_staged_synthetic_replay.py"},{"call":"package-initializer","column":0,"edge_type":"implicit_init","from_module":"tests.live_l1.test_i7_file_exact_preparation","from_path":"tests/live_l1/test_i7_file_exact_preparation.py","line":0,"reason":"implicit-package-initializer","resolution_status":"RESOLVED","symbol":"","to_module":"tests.live_l1","to_path":"tests/live_l1/__init__.py"}],"effect_edge_count":0,"effect_edges":[],"file_count":6,"forbidden_edge_count":0,"forbidden_edges":[],"implicit_initializer_edge_count":4,"semantic_files":[{"logical_path":"live_l1/__init__.py","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","size":0},{"logical_path":"live_l1/tools/i7_file_exact_harness.py","sha256":"15c9883518cc8c30c76aaf496c271444a97386e629c3683a782672347db11941","size":95036},{"logical_path":"live_l1/tools/i7_file_exact_observer.py","sha256":"0e427702d48dd8dba2a657a41d6b33e8cfe88441e42dad205b11f67aa68d7bca","size":39238},{"logical_path":"live_l1/tools/i7_staged_synthetic_replay.py","sha256":"6272941ba902a6a4422d9f906a12a8a7baa6cad687258be23dfcad699bf8d653","size":22528},{"logical_path":"tests/live_l1/__init__.py","sha256":"6e07d0dd2cea69b640c5a06402ab0ae7417fdd15dea6f1a6d89c66ad81fc6070","size":45},{"logical_path":"tests/live_l1/test_i7_file_exact_preparation.py","sha256":"3047b84435636dbd3d6b5174ccabf630a00009c376b406d3d76b03f7b3cf3ecd","size":69768}],"start_modules":["tests.live_l1.test_i7_file_exact_preparation"],"syntactic_edge_count":3,"topology_edge_count":7,"unresolved_local_import_count":0,"unresolved_local_imports":[]}
<!-- END_PREPARATION_CLOSURE_RECORD_JSON -->

<!-- BEGIN_REPLAY_CLOSURE_RECORD_JSON -->
{"dynamic_import_count":0,"dynamic_imports":[],"edge_count":1,"edges":[{"call":"package-initializer","column":0,"edge_type":"implicit_init","from_module":"live_l1.tools.i7_staged_synthetic_replay","from_path":"live_l1/tools/i7_staged_synthetic_replay.py","line":0,"reason":"implicit-package-initializer","resolution_status":"RESOLVED","symbol":"","to_module":"live_l1","to_path":"live_l1/__init__.py"}],"effect_edge_count":0,"effect_edges":[],"file_count":2,"forbidden_edge_count":0,"forbidden_edges":[],"implicit_initializer_edge_count":1,"semantic_files":[{"logical_path":"live_l1/__init__.py","sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","size":0},{"logical_path":"live_l1/tools/i7_staged_synthetic_replay.py","sha256":"6272941ba902a6a4422d9f906a12a8a7baa6cad687258be23dfcad699bf8d653","size":22528}],"start_modules":["live_l1.tools.i7_staged_synthetic_replay"],"syntactic_edge_count":0,"topology_edge_count":1,"unresolved_local_import_count":0,"unresolved_local_imports":[]}
<!-- END_REPLAY_CLOSURE_RECORD_JSON -->

R4-F8 verwendet für den Semantic Root ausschließlich logische Rollen/Pfade,
Inhaltshashes, semantische Modes/Membership, Gate-Ergebnis, obige Closure-
Topologie/-Findings, abgeleitete Counts und Preservation-Semantik. Absolute
temporäre Pfade, PID, Nonce, Run-ID, Device/Inode, UID/GID, atime/mtime/ctime
und Duration fehlen. Der Run Root bindet zusätzlich das vollständige rohe
Artefakthashmanifest, rohe Preservation-Manifeste, stdout/stderr, Prozessgruppe,
PID, Nonce, Run-ID, Runroot, Zeiten und den Semantic Root. Historische Run
Roots bleiben ausschließlich damalige Belege.

R3-F3 und R3-F6 bleiben CLOSED. E1–E3 bleiben offen.

## Resolution-4-Gates

- statische Freigabe: AST 4/4, strict JSON 2/2; lokale Closures 0/0/0/0;
- Fokustest: 12/12, RC 0, 0 Failure/Error/Skip;
- Preparation-Harness zweimal: jeweils 12/12, RC 0, Preservation 0;
- Replay-Harness: 3/3, RC 0, Preservation 0;
- `py_compile`: 4/4, exakt vier PYC ausschließlich unter
  `/tmp/iu4-i7-r4-static-final.h8OUvd/pycache`;
- `git diff --check` und `git diff --cached --check`: RC 0;
- adversariale Matrix: 8/8 Gruppen PASS für R4-F1/F2/F4/F5/F7/F8 sowie
  R3-F3/F6;
- Preparation Semantic Root:
  `e5fb1b775d3fc044a30a7fbcb2fc7837885dfa127eb05e0a122adb9bcf74c297`;
  Run Roots
  `5df9fca02352398de39557ba0a7112b966384672c70a29be83ed8adccaaec40d`
  und
  `10e28ae0c9e44dd2bf2a85ae6884178ea3d60cc44daf4bb36e8ad36f80884a6b`;
- Replay Semantic Root:
  `579d9e356528b43b0087ac56a4a9f4470f0c253ab3c634f59dfcb1e73ef507f0`;
  Run Root
  `4e592140fa050511c7713c347e2421675999e1f64e5af25246e4b2ee7a3b1bbf`;
- diagnostische Fehlversuche vor den gezählten Schlussläufen: ein Wrapper ohne
  exportierte `RUN_ROOT`, ein absichtlich von create-new abgewiesener bereits
  angelegter Root, ein fail-closed Worker-Test wegen einer anschließend
  präzisierten HOME-/Git-Ignore-Testannahme sowie eine unittest-Auswahl mit
  zwei falschen Klassennamen. Keiner wurde als Gate-PASS gewertet;
- kein Full-Discovery, kein 37/584-Census, kein Capability-, Guardian-, Kernel-,
  Workstation-, Collector- oder realer Ressourcenlauf;
- Regression nicht anwendbar: kein aktiver Runtime-Code verändert.

## Finaler technischer Sieben-Dateien-Stand vor Dokumentbindung

| Pfad | SHA-256 | Zeilen |
|---|---|---:|
| `live_l1/tools/i7_file_exact_harness.py` | `03f2e6e3541de9a71d0621f60f5eefec91f6dbd083557ac05d741bf15968db2b` | 1914 |
| `live_l1/tools/i7_staged_synthetic_replay.py` | `7b7a51185c00c8322e1b4bcdb86703b2d07f309eb9b8e84f81a4394e35e9c8cd` | 569 |
| `live_l1/tools/i7_file_exact_observer.py` | `e99874c3053e0ac61d6f5dd90f5f40a89f0d403fec23349e8788cfb2e7570515` | 788 |
| `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | `03d4674eac3dde7ea5332e1dffae347304856dfe88dcbde9f04ffc50545d49e2` | 173 |
| `config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json` | `12228780102d62dee3f0982507642b648e9defc6edc095739df6e38fa8dbf62d` | 166 |
| `tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt` | `e7a1723a7bc766c4dbd3f1961e801a8a14e8e8b68a59f880afd1e8da94ffd915` | 4 |
| `tests/live_l1/test_i7_file_exact_preparation.py` | `b4c9ed3e898793ea2ecbbbd2075fdb8457b3d2efd351714ea149909a2b1dd4b7` | 1097 |

F1-Governance bleibt 31/31, I6 6/6 und Preservation 22/22. Freeze-Manifest
bleibt `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16`
/ 60 / 0444; Freeze-Tar bleibt
`3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037`
/ gzip PASS / 1318/1318 / 0444. E1–E3 bleiben vollständig offen.

## Autoritative Resolution-5-Closure

Resolution 5 schließt ausschließlich die fünf Findings der unabhängigen
Resolution-4-Rereview. R4-F5, R4-F7 und R3-F6 bleiben unverändert CLOSED;
E1–E3 bleiben vollständig offen und wurden nicht ausgeführt oder fingiert.

### R5-F1 — Dynamic Alias

Die Wertflussanalyse bindet nun zusätzlich GeneratorExp, List/Set/DictComp,
Container-/Subscript-/Attributextraktion und unbekannte Call-Rückgaben, sobald
Funktion, Positions- oder Keywordargumente gefährlich gebunden sind. Dies
deckt `next`, `iter`, `map`, `SimpleNamespace`, `partial`, `operator`,
verschachtelte Returns, AsyncFunctionDef/Methoden, Decorators, Branch-Joins und
Rebinding ab. Konkrete dynamic Findings ersetzen jeden unsicheren
`dynamic=0/unresolved=0`-Pfad. Harmlose Generator-/Namespace-/Comprehension-
Gegenbeispiele bleiben finding-frei. Die zusätzliche Bypassmatrix enthält
neben den controlling Reproduktionen 13 weitere gefährliche und drei weitere
harmlose Flows.

### R5-F2 — Authentische unittest-Autorität

Worker-stdout/stderr enthalten keinerlei Ergebnisautorität und werden weder
als JSON geladen noch in Counts übersetzt. Nur der codegehashte feste
Supervisor besitzt den terminalen Pipe-Writer. Der unittest-Worker erbt ihn
nicht, läuft mit `close_fds=True`, besitzt keinen Nonce-/Gate-/Run-ID-State und
erreicht den festen Erfolgsterminus ausschließlich nach eigener exakter
Prüfung von testsRun/failures/errors/skips/unexpectedSuccesses/
expectedFailures. BaseException-, `SystemExit(0)`- und der zusätzlich gefundene
`SystemExit(73)`-Importabbruch erreichen den Terminus nicht. Import-time Fake-
JSON + `os._exit(0)`, RC0 ohne Tests, stdout/stderr spoof, duplicate JSON,
Monkeypatch sowie FD-/Environment-Angriffe liefern keinen terminalen Frame.
Der Parent akzeptiert weiterhin exakt ein duplicate-key-freies strict-JSON-
Frame mit Nonce/Gate/PID/Run-ID/Startsatz/Counts und lauter Null-Fehlercounts.
Timeout, TERM/KILL/Reap, kein Retry und Prozessgruppen-Leaktest bleiben
unverändert.

### R5-F3 — Git-/Ignore-Membership

Normale, gebundene isolierte Child- und finale Membership werden ohne
Filterung, Normalisierung oder Sonderbehandlung irgendeines Eintrags exakt
verglichen. Der Test belegt normal `150 == 150` und NUL-identische Bytes; ein
ungebundenes isoliertes HOME zeigt diagnostisch 151 einschließlich
`.claude/settings.local.json` und ist kein PASS. System-, global-, XDG- und
lokale Configquellen, `core.excludesFile`, implizites XDG-Ignore,
`.git/info/exclude`, command-scope Config und deren Presence/Content/Mode/
Owner/Device/Inode/Zeiten liegen vollständig im Raw-Run-Record. Der Child
erhält dieselbe `_bound_git_environment`-Semantik wie der Produkt-Harness.

### R5-F4 — Atomarer Observer-Konsum

`_bound_tmp_root` erzeugt per O_EXCL/O_NOFOLLOW vor Authority-, PRE-, POST-,
Plan-Read oder Output einen fsync-gebundenen dauerhaften IN_PROGRESS-Sentinel.
Jede vorhandene IN_PROGRESS- oder COMPLETED-Autorität wird abgewiesen; auch
Crash, Partial-Sentinel und Post-output/Pre-completion-Crash öffnen kein
Replayfenster. Die absolute Descriptor-Kette von `/` über Parent und Runroot
bleibt bis nach COMPLETED/fsync offen. PRE/POST/Plan/Output/Completion verwenden
diese gepinnte Root-Autorität descriptor-relativ und revalidieren die gesamte
lexikalische Kette. Concurrent-Zweitprozess, Crash-Neuprozess, Root-Swap,
Parent-Swap, Symlink/Hardlink, stale Authority und partieller Abschluss sind
fail-closed. Run-ID, created_at_ns <= PRE < POST, Rollen, Sequenzen und
Crossbindings bleiben erhalten.

### R5-F8 — Hostneutraler Semantic Root

Das Gate-Manifest wird auf logische Rollen, relative Pfade, Inhaltsregeln und
Gates kanonisiert; canonical_repository sowie rohe UID/GID werden nur roh
gebunden. Git-Konfiguration wird ohne `--show-origin`-Hostpfade als geordnete
effektive Key/Value-Bedeutung kanonisiert, während vollständige Rawbytes,
Origins und Metadaten im Run Root bleiben. Semantic Material enthält weder
absolute Repo-/HOME-/XDG-/tmp-Pfade noch UID/GID, Device/Inode, Zeiten, PID,
Nonce, Run-ID oder Duration. Closure, Test-/Resultatcounts, Gate-Regeln,
Membership, Ignore-Wirkung und nicht-selbstreferenzielle Preservation-Inhalte
bleiben semantic-bound. Das Evidence-Dokument selbst ist membership-/rollen-
gebunden, aber sein Inhalt und seine Größe liegen zur Vermeidung der
Selbstreferenz ausschließlich im vollständigen Raw Run Root.

## Resolution-5-Gates

- statische Freigabe: AST 4/4, strict JSON 2/2, exakt 12 Testmethoden;
- lokale Closures: Preparation 6/7 = 3+4, Replay 2/1 = 0+1, jeweils
  forbidden/dynamic/unresolved/effect 0/0/0/0;
- fokussierter Schlusslauf: 12/12, RC0, keine Failure/Error/Skip/Warning;
- Preparation zweimal: 12/12, RC0, Preservation 0, gemeinsamer Semantic Root
  `8e8fb454bca828788d553976236272d64c7b6479a8b248e07fccf393de6ac2dd`,
  verschiedene Run Roots
  `3063ce6980a01520ef3a35937d2e2998082e0c06235e740742b034472d43ce4a`
  und
  `d6184b123569052fb7692aff381d693e4a163e44c90c1792448cead9ff9d0c60`;
- Replay: 3/3, RC0, Preservation 0, Semantic Root
  `af10cebf2fa8331463b34a34adc218864abe9a0cbebbeeff52bba2bb44acdba9`,
  Run Root
  `e91b30f2c3f4c457f223caacccb2c3a291485766e26bbe1ecd7fa8d7b6ec0d32`;
- adversariale Matrix: 8/8 PASS für R5-F1/F2/F3/F4/F8, R4-F5/F7 und
  R3-F6;
- `py_compile`: 4/4, exakt vier PYC ausschließlich unter `/tmp`;
- `git diff --check` und `git diff --cached --check`: RC0;
- diagnostisch, nicht als PASS gezählt: ungebundenes HOME 151, initialer
  Analyzer-Selbstreferenz-False-Positive, alte Closure-Record-Abbrüche,
  ResourceWarning-Vorlauf sowie der zusätzlich geschlossene SystemExit(73)-
  Bypass;
- kein Full-Discovery, kein 37/584-Census, kein Capability-/Guardian-/Kernel-/
  Workstation-/Collector-/Live-/Exchange-Lauf; kein aktiver Runtime-Code
  verändert, daher Regression-Suite nicht anwendbar.

## Finaler technischer Resolution-5-Sieben-Dateien-Stand vor Dokumentbindung

| Pfad | SHA-256 | Zeilen |
|---|---|---:|
| `live_l1/tools/i7_file_exact_harness.py` | `c0c48f31c9af4484667048987587d769abe30933f3625a1a4064d55f986e1967` | 2110 |
| `live_l1/tools/i7_staged_synthetic_replay.py` | `7b7a51185c00c8322e1b4bcdb86703b2d07f309eb9b8e84f81a4394e35e9c8cd` | 569 |
| `live_l1/tools/i7_file_exact_observer.py` | `0e427702d48dd8dba2a657a41d6b33e8cfe88441e42dad205b11f67aa68d7bca` | 974 |
| `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | `7eea67c93ecd70fbecd043daea7a74c5ce07548c08b4546c4fe477f6c0de50a5` | 178 |
| `config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json` | `12228780102d62dee3f0982507642b648e9defc6edc095739df6e38fa8dbf62d` | 166 |
| `tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt` | `e7a1723a7bc766c4dbd3f1961e801a8a14e8e8b68a59f880afd1e8da94ffd915` | 4 |
| `tests/live_l1/test_i7_file_exact_preparation.py` | `3a12f70485bec0c19d2b874853582a958e8be7872ff22dc9ff8c8f55bcd9be6e` | 1319 |

Governance bleibt 31/31, I6 6/6, Preservation 22/22. Freeze-Manifest
bleibt `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16`
/ 60 / 0444; Freeze-Tar bleibt
`3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037`
/ gzip PASS / 1318/1318 / 0444.

Nächster Schritt ist ausschließlich eine neue separate unabhängige read-only
File-Exact-Rereview der Resolution 5. Erst ein danach separat autorisierter
Workstream darf E1–E3 real binden.

EVIDENCE_PAYLOAD_SHA256:8c931e72b45e2eaabaa40a65f57218cb7df5b4a646a8047e7491dc16ffb27edd
