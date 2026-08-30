# I7 R5-F2 Canonical Implementation Profile — Transcript-Bound V1

- Logischer Kandidatenname: `I7_R5_F2_CANONICAL_IMPLEMENTATION_PROFILE_TRANSCRIPT_BOUND_V1.md`
- Statusgrundlage: `CANONICAL_IMPLEMENTATION_PROFILE_REREVIEW_READY`
- Beweisklasse: `TRANSCRIPT_BOUND_NONAUTHORITATIVE_DESIGN_INPUT`
- Publikationsstatus: nicht publizierter In-memory-Kandidat

Belegklassen:

- `T-FULL`: vollständiger Terminalrecord erhalten.
- `T-HASH`: Inhalt verloren; nur terminal ausgegebene Counts, Bytes und SHA-256 erhalten.
- `C-GATE`: durch den byte-exakten Controllervertrag und dessen erfolgreichen Exit gebunden.
- `P-BOUND`: zuvor veröffentlichte und attestierte Repositoryidentität.

PTY-Dekodierung: Eine Sequenz aus letztem Zeichen, CRLF, `ESC[23;80H` und demselben ersten Fortsetzungszeichen repräsentiert genau ein Zeichen. Alle unten gebundenen SHA-256-Werte besitzen exakt 64 Hexzeichen.
## 1. Messlaufidentität

| Feld | Wert | Beleg |
|---|---|---|
| Controller | `I7_R5_F2_RUNTIME_SYSCALL_CLOSURE_MEASUREMENT_CONTROLLER_V18.sh` | C-GATE |
| Controllerbytes | 91356 | T-FULL |
| Controller-SHA-256 | `2dbfe02a5ca7321ccc96cb2556c5319c7080754b6eb320eaf80291dac50ddd68` | T-FULL |
| Kodierung | ASCII/UTF-8 ohne BOM und ohne terminales LF; letztes Byte 49 | T-FULL |
| Syntax | vollständiges `bash -n`-PASS | T-FULL |
| Workspace | `/tmp/i7-r5-f2-closure-measurement-v18.skaWAE6v6ikd` | T-FULL |
| Controller-/Tracer-/Namespace-Starts | jeweils genau 1 | T-FULL |
| Controller-/Measurement-/Worker-Exitcode | jeweils 0 | T-FULL |
| PID-1-Reaper | `PID1_REAPER_FINAL=PASS` | T-FULL |
| Python-Freigabe | `PYTHON_EXEC_AUTHORIZATION=CONSUMED` | T-FULL |
| Abschluss | `MEASUREMENT_CLOSURE_READY` | T-FULL |

Der Lauf ist ausschließlich nichtautoritative Design-Eingabe und besitzt keine I7-Evidence-, Acceptance- oder Execution-Authority.

## 2. Transcriptbindung und Verfügbarkeit

- Kanonischer Transcriptpfad: `C:\Users\benja\.codex\sessions\2026\08\28\rollout-2026-08-28T10-46-23-01a0478c-792d-7511-99d7-42e79aaefdd3.jsonl`
- CommandExecution-ID: `exec-ba1f0944-b7d9-43e4-9056-4f9a33f12abe`
- Prozess-ID: 31443
- stdout: 89892 UTF-8-Bytes
- stdout-SHA-256: `ec29a4393c0273b2cfc17957ac4be2cf1a1ce6350d711d8072f9d337673bd0e6`
- Truncation-Markierungen: 0
- PTY-Überlappungen: 581 erkannt, 581 eindeutig dekodiert, 0 verbleibend
- dekodierte SHA-Operanden: 368, davon 0 mit einer Länge ungleich 64
- `FAILURE_PRESERVATION_BEGIN`: genau 1
- `FAILURE_PRESERVATION_END`: genau 1
- `FAILURE_TRACE`-Identitätsrecords: genau 309
- `MEASUREMENT_CLOSURE_READY`: genau 1

Der ursprüngliche Workspace ist `ENOENT`. `/tmp` ist ein instanzgebundenes `tmpfs`; der Controller enthält keinen `rm`-, `rmdir`-, `unlink`- oder Cleanup-Pfad. Es existiert keine vollständige Workspacekopie im WSL-Dateisystem oder Windows-Benutzerprofil. Die Rohtraces und abgeleiteten Manifestdateien können nicht erneut gelesen oder gehasht werden.

## 3. Pakete, Runtime und ELF

| Komponente | Bindung | Beleg |
|---|---|---|
| `strace` DEB | `6.19+ds-0ubuntu5`, amd64, 677520 Bytes, SHA `aa530bb652e46beaf92d5c916403182a5ac6b2ba79a94f18e5b9da45d1799ee5` | T-FULL |
| `libunwind8` DEB | `1.8.3-0ubuntu1`, amd64, 59630 Bytes, SHA `7a9978fadf0940f45500ced0fba219cb5954f322a31068b7b32ad04f3ddc5c3f` | T-FULL |
| `bash-builtins` DEB | `5.3-2ubuntu1`, amd64, 197790 Bytes, SHA `35a38ea4a3b98495e9bd54e030899e68e217c1bc941faa9fc8ad7c1dced0af29`, Abhängigkeit `bash (= 5.3-2ubuntu1)` | T-FULL/C-GATE |
| private `strace` | 2370264 Bytes, SHA `f47342683309e807bca57d6d89b82f94a9b39aa614e9c28c2b67cefbc35eee58` | C-GATE |
| `fdflags` | 14688 Bytes, Mode 0755, UID/GID 0:0, SHA `80bec3c173979f1383cbec2a79813fe61a0a7d5ee98234876dc23d96146f41df` | T-FULL |
| `fdflags` ELF | ELF64 little-endian x86-64, Typ DYN, SONAME `fdflags`, kein Interpreter, ausschließlich `DT_NEEDED=libc.so.6` | C-GATE |
| `fdflags`-Closure | 3 Records, 351 Bytes, SHA `c9b8c2050ce3ab4cad0617ede829f2026a6c88e3b7d6c4eb65c7ebc3f1b1cf46` | T-FULL |
| private `strace`-Closure | 8 Records, SHA `ee40d3c8579c5a98fd33dcdd7e83a3e6221195aff7c16cda430a2c030541ba50` | T-HASH |
| `/usr/bin/bash` | 1540520 Bytes, SHA `3efccc187bafa75ff1e37d246270ab3e7aa559f242c7a52bf3ec2a1b5450bdbd` | C-GATE |
| `/usr/bin/python3.14` | 7481192 Bytes, SHA `b8d8288faefdd300201f43fcf00f6f539a27218eeed3a3dff5ab10b9c4c99700` | C-GATE |
| Kernel | x86_64, `6.18.33.2-microsoft-standard-WSL2` | C-GATE |
| Kernel-Konfiguration | SHA `30e49f5d4d0a53d46f4f8056ecca9ab0be08e7949cf058f961d779e023f752b5` | T-FULL |
| Namespace-Funktion | SHA `d9a06da9666209a6996aab90ca9cad8a1466956420d16580c6e198b10e43d3e9` | T-FULL |

Alle Pakete wurden ausschließlich privat extrahiert; keine systemweite Installation oder APT-Konfigurationsänderung erfolgte.

## 4. Repository- und Dokumenteingaben

| Pfad | Identität | Beleg |
|---|---|---|
| `config/pee/IU4_I7_FILE_EXACT_GATES_V1.json` | 8896 Bytes, SHA `a96ddc05124e3a95312833c281e86155b1c1f1710d9845b1da7cf64f74799719`, Device 2096, Inode 33136, Mode 0444, UID/GID 1000:1000, Linkzahl 1 | P-BOUND |
| `live_l1/tools/i7_file_exact_harness.py` | 95036 Bytes, SHA `15c9883518cc8c30c76aaf496c271444a97386e629c3683a782672347db11941`, Device 2096, Inode 36133, Mode 0444, UID/GID 1000:1000, Linkzahl 1 | P-BOUND |
| `live_l1/tools/i7_staged_synthetic_replay.py` | 22528 Bytes, SHA `6272941ba902a6a4422d9f906a12a8a7baa6cad687258be23dfcad699bf8d653`, Device 2096, Inode 36194, Mode 0444, UID/GID 1000:1000, Linkzahl 1 | P-BOUND |
| `tests/live_l1/test_i7_file_exact_preparation.py` | 69476 Bytes, SHA `5141b498d7a4638879a7154819bc407a77149a685ca0809b6ab5a98554363aa5`, Device 2096, Inode 32787, Mode 0444, UID/GID 1000:1000, Linkzahl 1 | C-GATE/P-BOUND |
| `docs/review/PRE_IU4_I7_PREPARATION_RESOLUTION_FILE_EXACT_2026-08-23.md` | 44562 Bytes, SHA `aba166d0dc61539178798ccaa0ad549ae88db02d54dd777ffe7f7f748f8e82be`, Device 2096, Inode 32753, Mode 0444, UID/GID 1000:1000, Linkzahl 1 | T-FULL |
| PREPARATION-Record | 3793 Bytes, SHA `3ce24edcaef20dd5c6cac32136104a1cc3fc756f78b72d5023ddef373e036262` | T-FULL |
| REPLAY-Record | 1009 Bytes, SHA `ec363fb685913dad49592edf4be58379aa407142011680f9d235c1742e568972` | T-FULL |
| PYC-Manifest | 3831 Records, SHA `409dce545e54f92676d1e826d55c4103a1bede850d5bb165d4c8e0e2838fa751` | P-BOUND |

Das Workstation-Schema bindet Mode 292; die Git-Status-Recordcount-Pins lauten normal/isoliert/ungebunden 121/121/122.

## 5. Git-Konfiguration und Mounts

- `/home/benja/.gitconfig`: 62 Bytes, SHA `f7e14abf77d5ef0feaf62f03e2c12b80acae7e375388fc2b03ee2757177289e5`, Mode 0644, UID/GID 1000:1000, Device 2096, Inode 1006, Linkzahl 1.
- `/home/benja/.config/git/ignore`: 31 Bytes, SHA `1a377e8e10315d1e8b44caf5bfe181da8320a024e4f3316b1cf1d91f9db274b3`, Mode 0644, UID/GID 1000:1000, Device 2096, Inode 72839, Linkzahl 1.
- PID 1 öffnete beide Dateien `O_RDONLY|FD_CLOEXEC`.
- Die Bind-Quellen waren `/proc/1/fd/<FD>` und wurden mit `mount --no-canonicalize --bind` verwendet.
- Beide Child-Mounts besaßen VFS `ro,nosuid,nodev,noexec`; die FS-Optionen blieben getrennt gebunden.
- Device, Inode, Mode, Eigentum, Linkzahl, Größe, Realpath, Readback und SHA stimmten zwischen Host-FD und Child-Ziel überein.
- Beide FDs wurden vor `CONTINUE` genau einmal geschlossen, waren anschließend abwesend und wurden nicht an den Worker vererbt.
- Worker-Environment: `GIT_CONFIG_GLOBAL=/home/benja/.gitconfig` und `XDG_CONFIG_HOME=/home/benja/.config`.
- `/home/benja/.config/git/config` und `/etc/gitconfig` waren vor Workerfreigabe abwesend.

## 6. Namespace-, Sysfs- und Resolverprofil

- Private Mount-, PID- und Netzwerk-Namespaces; Mount-Propagation rekursiv private.
- Parent-Sysfs: shared, VFS/FS `rw`.
- Parent-Resolver-Mount: shared `rw`.
- Namespace-PID 1: root-eigener Reaper; Bootstrap: erstes und einziges anfängliches Child, Namespace-PID 2.
- Sichtbarer Child-Sysfs-Mount: private, VFS `ro,nosuid,nodev,noexec`, FS `ro`.
- Vollständige Child-Sysfs-Menge: 2 Records, SHA `6e3d8d39213ef59223e23c2ab7645085fb15612d63ee28543d7b8fb8f91dc915`.
- Shadowed Child-Sysfs-Menge: 1 Record, SHA `bc5ee40624a25072c1d2bcf2151a051c6b9839059b169d2848688323497ca1e2`.
- Der geerbte shadowed Sysfs-Record blieb VFS/FS `rw`.
- Resolver: genau 1 Record, SHA `96f8086cc84f6a6652beff111b2c6de09985b4274597850c5c6b58c219261639`.
- Resolverziel `/mnt/wsl/resolv.conf`, Alias `/etc/resolv.conf`, identische `stat -L`-Identität.
- Resolver-Mount: private tmpfs, VFS `ro,nosuid,nodev,noexec`, FS `rw,size=64k,mode=700`.
- Resolverdatei: 0 Bytes, Mode 0444, UID/GID 0:0.

## 7. Netzwerk- und Sicherheitsprofil

- Child-Netzwerkmanifest: 1900 Bytes, SHA `5eb8dccabf6e1575f32f24cb8cf5d5b433cdda5883d4567e19637a5d83a8a460`.
- Ausschließlich Interface `lo`; `lo` administrativ DOWN (`flags=0x8`).
- Keine weiteren Interfaces.
- 0 IPv4-/IPv6-Adressen.
- 0 Routen.
- 0 Neighbour-Records.
- Resolverinhalt 0 Bytes.
- 0 geerbte Socket-FDs.
- `no_new_privs=1`.
- Seccomp-Filter verfügbar.
- Die Parent-Netzwerk-, Mount-, Resolver- und Sysfs-Zustände blieben im Stable-Manifest unverändert.

## 8. Parent-Unverändertheit

| Phase | Rohmanifest | Stable-Manifest | NUD-State-Manifest |
|---|---|---|---|
| BEFORE | 4516 Bytes, SHA `da11da04219850a45788604288dd0b206455a3f464f2247b133e00cae8d2ba70` | 4498 Bytes, SHA `da64f5bb3edc2121b41028aa7be02212382b09382f928a890d8983644a4a7a90` | 162 Bytes, SHA `7f2aa44dcef9cb8f48ee625ba52f38f551e5b8dd926dc2bdef94be5030fb6238` |
| DURING | 4520 Bytes, SHA `88cc1a1739adcc109fb26496637c19ccc6d8b2fa023ffd0f8e6b1e80eca27a03` | identisch zu BEFORE | 166 Bytes, SHA `fd737e7c9a5d4ae14e7509e665ee621c657806a010c1752154ef8ca92e73857b` |
| AFTER | identisch zu DURING | identisch zu BEFORE | identisch zu DURING |

Stable BEFORE=DURING=AFTER. Der ausschließlich volatile Unterschied lag im gültigen Neighbor-NUD-State. Familie, Recordcount, `dst`, `dev`, `lladdr` sowie alle übrigen nicht-volatilen Neighbor-, Namespace-, Interface-, Adress-, Routing-, Rule-, Resolver-, Sysfs- und Mountfelder blieben unverändert.

## 9. Prozess-, Signal- und Reapingprofil

- `PID1_REAPER_FINAL=PASS`, Worker-RC 0, Reaping bis `ECHILD`, finale Prozessmenge ausschließlich PID 1.
- TERM, INT, HUP und QUIT wurden höchstens einmal an die Worker-Prozessgruppe weitergegeben.
- Genau 1 Primärworker.
- Genau 8 Supervisor-Nachkommen.
- Genau 8 Worker-Nachkommen.
- Genau 1 Observer.
- Genau 1 Timeout-Child.
- Genau 1 Timeout-Grandchild.
- Insgesamt 19 klassifizierte testinterne Python-Nachkommen.
- Insgesamt 20 Python-Execs.
- 0 unklassifizierte Python-Execs und 0 Python-Exec-Rejections.
- Host-/Namespace-PIDs wurden bijektiv gebunden; Prozesskanten wurden ausschließlich am kanonischen Tracezeilenanfang erfasst.
- Test 12 bestätigte Readiness, unveränderten 0,3-Sekunden-Haupttimeout, SIGTERM, Grace, SIGKILL, Prozessgruppenfreiheit und vollständiges Reaping.

## 10. Testprofil

Alle zwölf gebundenen Methoden wurden gestartet und mit PASS abgeschlossen:

1. `test_01_manifest_schema_and_exact_types`
2. `test_02_package_relative_alias_and_missing_local_imports`
3. `test_03_dynamic_import_constructions_fail_closed`
4. `test_04_forbidden_alias_and_census_partition`
5. `test_05_replay_pinning_traversal_hash_malformed_and_old_artifacts`
6. `test_06_pre_post_roles_sequence_and_distinctness`
7. `test_07_observer_contract_run_hash_and_preowned_invariants`
8. `test_08_cleanup_binding_and_tmp_confinement`
9. `test_09_contract_schema_duplicate_path_and_symlink_boundaries`
10. `test_10_contract_hardlink_mode_owner_hash_and_permission_boundaries`
11. `test_11_capability_ids_and_counts_are_derived_not_asserted`
12. `test_12_timeout_group_reap_preservation_diff_and_attestation`

Ergebnis: 12 PASS, 0 Failures, 0 Errors.

Teststreams:

- stdout: 3069 Bytes, SHA `f6ebd6656f6e4b176d6be4471e3c58e66b44e07e945f1686f8c2c5e887a036da`.
- stderr: 2311 Bytes, SHA `b3fbef67f0957d26b4856824135e674d960a27e186672b6374a2f1da5fbb0d5d`.

## 11. Kanonische Closure-Ergebnisse

| Artefakt | Records | Bytes | SHA-256 | Beleg |
|---|---:|---:|---|---|
| Raw-Trace-Dateiliste | 309 | 3306 | `638f9658e6d068cdc5188667ef7af236981a7952e7a16ad72cace4671bdabf9c` | T-HASH |
| Trace-Identitätsmanifest | 309 | 27813 | `4cd939980382018abd0469516e8e07e35757ee9eb01d83de28aab75a92e30ae3` | T-HASH |
| Python-Exec-Lineage/argv | 944 | 135682 | `417ffe8a204936e5a6300b2ac823efa6300cd1a9815ca52ae8026a69231389b5` | T-HASH |
| Host-/Namespace-PID-Crossbindings | 308 | 9656 | `40ae1d0dcc4ac8117548a1f82070d37f23150ad7e402e1534a374aa540fdf908` | T-HASH |
| Prozessidentitäten | 274 | 24591 | `80495f65a05df5b67a003e2e9e3be723c72e3e5e008bbd06980a133aafddd09c` | T-HASH |
| Prozesskanten | 308 | 4666 | `7454507bf05250e9cce1f8fc9f8f6260d5c689d062951e3af41427652fad6cc2` | T-HASH |
| Python-Exec-Rollen | 20 | 48332 | `9a75cdc29525031cbfc181860b4f47db17c11491205ee8c55d2b3c29c21deec8` | T-HASH |
| Python-Exec-Rejections | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | T-HASH |
| Syscalls nach Prozessphase | 9021 | 313008 | `e8f278383ffa314f757173c11ce5847bd4e7de05281a2abfc20034403ae89064` | T-HASH |
| Prozess-/Signalübergänge | 1356 | 10858177 | `e33e70ae49791cb8c86fff546c9ccbd7a5ef8f5c27b9e558242389475c446d1f` | T-HASH |
| Datei-/FD-Pfade | 4846 | 449067 | `d5c9498042fbd40900bcb7d5fd809d7c73cdd2ffbc998a8d97653cd213423ff4` | T-HASH |
| Python-/Erweiterungsmodule | 2909 | 208651 | `9c14f5e74ad9c4795806f9baaaf1e9e4788d3a692bd91c32d472e22ff961b094` | T-HASH |
| Beobachtete ELF-Dateien | 101 | 3712 | `572a74154e08acb1b8172cd2d7e7b38befcf1f05332c59df7c0a183ab64f25a8` | T-HASH |
| Rekursive ELF-Closure | 103 | 12015 | `032c8b6f22979e52f37b592286d02d7ac9dab070f59692246385dae6ae8d4b11` | T-HASH |
| Fehlgeschlagene Pfadauflösungen | 13455 | 2624488 | `141341f8cff52856478f2260b93340602677460105cd03468b37f1f5d9184e36` | T-HASH |

Alle 15 Zeilen wurden nach deterministischer PTY-Überlappungsdekodierung mit exakt 64-stelligen SHA-256-Werten aus dem kanonischen Transcript gebunden.

## 12. Geltungsgrenze

Dieses Profil ist eine `TRANSCRIPT_BOUND_NONAUTHORITATIVE_DESIGN_INPUT`-Darstellung. Es ist keine raw-artifact-file-exakte Attestation: Die verlorenen 309 Rohtraces und abgeleiteten Manifestdateien wurden nicht erneut gelesen oder gehasht.

Vollständige Terminalrecords sind als `T-FULL`, ausschließlich terminal ausgegebene Count-/Byte-/SHA-Bindungen als `T-HASH`, erfolgreiche Controllervertragsprüfungen als `C-GATE` und zuvor veröffentlichte Repositoryidentitäten als `P-BOUND` gekennzeichnet.

Es wurden keine fehlenden Rohrecords erfunden. Das Profil besitzt keine I7-Evidence-, Acceptance- oder Execution-Authority. Aus ihm wurde keine Source-, Test-, Controller-, Policy-, Schema-, Profil-, Evidence- oder Authority-Publikation abgeleitet. Bei dieser Kandidatenableitung wurde keine Datei erzeugt oder verändert.
