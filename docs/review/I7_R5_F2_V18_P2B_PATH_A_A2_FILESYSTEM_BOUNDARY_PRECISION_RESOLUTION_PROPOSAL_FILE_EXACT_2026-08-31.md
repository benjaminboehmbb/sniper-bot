# I7 R5 F2 V18 P2B Path A A2 Filesystem Boundary Precision Resolution Proposal

Date: 2026-08-31

Classification:

NONAUTHORITATIVE_P2B_PATH_A_A2_FILESYSTEM_BOUNDARY_PRECISION_RESOLUTION_PROPOSAL

This file is a nonauthoritative proposal only. It grants no Test, Evidence,
Acceptance, Staging, Commit, Push, Publication, Execution, Live, or Exchange
authority. The precision resolution described here is proposed and is not
accepted or authorized by creation of this file.

## 1. Canonical repository and pre-creation state

Canonical repository:

    /home/benja/projects/sniper-bot

The state read immediately before creation was:

| Binding | Value |
|---|---|
| Branch | main |
| HEAD | bafb2f4de22811e2bf171060cf3f18a4d32e769d |
| main | bafb2f4de22811e2bf171060cf3f18a4d32e769d |
| origin/main | bafb2f4de22811e2bf171060cf3f18a4d32e769d |
| Parent | d1e865f29f507fcf7eb405c3be7da4a8946b9861 |
| Staged records | 0 |
| Tracked unstaged records | 10 |
| Untracked records | 92 |
| Working Tree records | 102 |
| Index lock | ABSENT |

The complete pre-creation status NUL stream is bound as:

| Property | Value |
|---|---|
| SHA-256 | d5aeb20f1aec25368de8b0cc8e55790d42a1c7f58f9f7a0948c7574cc6285d29 |
| Bytes | 8449 |

The complete pre-creation content-preservation manifest uses one
LF-terminated row per record:

    <status2>\t<whole-file-sha256>\t<path>\n

Rows are sorted lexicographically by path and concatenated without
additional bytes.

| Property | Value |
|---|---|
| SHA-256 | a45bad7bcee51e927ae56cc33abd0254caff50308bde0c1457805581792e2947 |
| Bytes | 15079 |
| Lines | 102 |

All 102 preexisting records are excluded from this creation and must remain
byte- and membership-preserved. Only this proposal may become the 103rd
Working Tree record.

Expected post-creation state:

| State | Count |
|---|---:|
| Staged records | 0 |
| Tracked unstaged records | 10 |
| Untracked records | 93 |
| Working Tree records | 103 |

## 2. Bound Path A scope reconciliation proposal

| Property | Value |
|---|---|
| Path | docs/review/I7_R5_F2_V18_P2B_PATH_A_DEPENDENCY_PUBLICATION_CLOSURE_SCOPE_RECONCILIATION_PROPOSAL_FILE_EXACT_2026-08-31.md |
| SHA-256 | ac4c2882861365c7807f8781ec69912baac531405303b316baef9042311e46ac |
| Bytes | 35221 |
| Lines | 371 |
| Mode | 0444 |
| UID:GID | 1000:1000 |
| Device/Inode | 2096/10868 |
| Links | 1 |
| Git status | untracked |

The scope proposal remains nonauthoritative. It grants no Path A
Publication ownership or later-gate authority.

## 3. Bound A2 blocker reconciliation proposal

| Property | Value |
|---|---|
| Path | docs/review/I7_R5_F2_V18_P2B_PATH_A_A2_FILESYSTEM_BOUNDARY_BLOCKER_RECONCILIATION_PROPOSAL_FILE_EXACT_2026-08-31.md |
| SHA-256 | abebea3a5e8660258b894104eaa2b89567c51cdfb0a5cd0e617d3fd0d55ab897 |
| Bytes | 13133 |
| Lines | 392 |
| Encoding | UTF-8 without BOM, ASCII-only |
| CR bytes | 0 |
| Terminal LF | exactly one |
| Mode | 0444 |
| UID:GID | 1000:1000 |
| Device/Inode | 2096/10870 |
| Links | 1 |
| Type | regular file, not a symlink |
| Git status | untracked |

The independent decision bound to that proposal is:

    I7_R5_F2_V18_P2B_PATH_A_A2_FILESYSTEM_BOUNDARY_BLOCKER_RECONCILIATION_PROPOSAL_READY

That READY result only accepts the blocker proposal as a nonauthoritative
reconciliation basis. It does not resolve the blocker and grants no
authority.

## 4. Bound Path A Test identities

### 4.1 Lifecycle ledger persistence Test

| Property | Value |
|---|---|
| Path | tests/live_l1/test_iu4_lifecycle_ledger.py |
| SHA-256 | f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093 |
| Bytes | 3940 |
| Lines | 50 |
| Mode | 0444 |
| UID:GID | 1000:1000 |
| Device/Inode | 2096/80611 |
| Links | 1 |
| Git status | untracked |

The file-exact side-effect bindings are:

| Line | Binding |
|---:|---|
| 4 | Imports tempfile. |
| 6 | Imports Path from pathlib. |
| 11 | Each unittest Test case creates a new tempfile.TemporaryDirectory. |
| 12 | Resolves that Test case's isolated temporary root. |
| 13 | Constructs IU4LifecycleLedgerV1 against that root. |
| 14 | Initializes the persistent ledger below that root. |
| 15 | Cleans up that root after the Test case. |
| 23 onward | Ledger operations write records below the current Test root. |
| 46 | Reads the isolated Test record. |
| 47 | Writes the intentional manipulation below the same Test root. |
| 48 | Verifies fail-closed behavior. |
| 50 | Contains a guarded, unexecuted unittest.main call. |

setUp and tearDown run for each executed unittest Test case. This proposal
does not claim that one directory is shared by an entire later Test suite.
The proposed precision permits at most one active, Test-case-owned
TemporaryDirectory per Test case. That root must be cleaned after that Test
case.

### 4.2 Focused paper artifact Test candidate

| Property | Value |
|---|---|
| Path | tests/live_l1/test_paper_artifacts_i6_dependencies.py |
| SHA-256 | 5a268abd386de90ec3ba1ce7c9b98f847494814ee66fc04d31c1fcc4e8caa53e |
| Bytes | 12635 |
| Lines | 307 |
| Mode | 0444 |
| UID:GID | 1000:1000 |
| Device/Inode | 2096/10866 |
| Links | 1 |
| Git status | untracked |

This candidate is in-memory only. Its only Repository imports are:

- live_l1.state.paper_artifacts
- live_l1.core.paper_economics

### 4.3 Focused loss cluster Test candidate

| Property | Value |
|---|---|
| Path | tests/live_l1/test_loss_cluster_i6_transitions.py |
| SHA-256 | fff45d2dfa972a8a820a2a9deba4535927dea9847af54395153ee98fb69ecd13 |
| Bytes | 9223 |
| Lines | 246 |
| Mode | 0444 |
| UID:GID | 1000:1000 |
| Device/Inode | 2096/10972 |
| Links | 1 |
| Git status | untracked |

This candidate is in-memory only. Its only Repository import is:

- live_l1.state.loss_cluster

The two focused candidates remain classified as:

    NONAUTHORITATIVE_P2B_PATH_A_TEST_CLOSURE_CANDIDATE

Availability of any Test file is not Test PASS or Test authority.

## 5. Bound A2 blocker and cause

The earlier independent A2 decision remains:

    I7_R5_F2_V18_P2B_PATH_A_A2_SOURCE_TEST_DIFF_EFFECT_CONSUMER_REREVIEW_NOT_READY

The blocker remains:

    A2-T3-TEMPORARY-FILESYSTEM-BOUNDARY-B1

Its cause was a blanket A2 requirement that all three Path A Tests be free
of filesystem writes and temporary files or directories.

The file-exact facts are:

1. The two new focused Test candidates satisfy absolute side-effect freedom.

2. The existing lifecycle ledger Test is a persistence Test. Realistic
   verification of ledger initialization, record chaining, tamper detection,
   cleanup, and fail-closed behavior requires isolated temporary filesystem
   state.

3. Current lifecycle Test access stays under Test-case-owned temporary roots.
   It does not address productive Repository, State, Runtime, Live, or
   Exchange paths.

4. The lifecycle Test operations remain real filesystem side effects. They
   are not reclassified as in-memory operations.

5. The boundary conflict can be resolved only by assigning the absolute
   side-effect-free boundary precisely. It cannot be resolved by denying or
   relabeling the lifecycle Test operations.

This proposal does not itself close the blocker.

## 6. Proposed precise resolution of Test boundaries

This section defines the proposed precision. It remains nonauthoritative
until independently accepted and followed by a newly authorized A2
rereview.

### 6.1 Absolute boundary for the two focused in-memory Tests

The following absolute restrictions continue to apply to:

    tests/live_l1/test_paper_artifacts_i6_dependencies.py
    tests/live_l1/test_loss_cluster_i6_transitions.py

They may perform:

- no filesystem reads or writes;
- no temporary-file or temporary-directory operations;
- no network access;
- no process starts;
- no sleeps;
- no randomness;
- no current-time access;
- no environment-dependent operations;
- no Runtime, Startup, Shadow, Terminal, Live, or Exchange access;
- no Repository imports beyond their individually bound allowlists.

These restrictions are not relaxed by the lifecycle persistence-Test
exception.

### 6.2 Narrow exception for the existing lifecycle persistence Test

Only under a later, separately authorized A3 Test execution may the following
narrow exception apply to:

    tests/live_l1/test_iu4_lifecycle_ledger.py

The complete exception is:

1. Each unittest Test case may create exactly one
   tempfile.TemporaryDirectory in setUp.

2. At most one such temporary root may be active for that Test case at any
   time.

3. Every ledger file, record, intentional Test manipulation, and cleanup
   action must remain below that Test-case-owned root.

4. tearDown must clean the temporary root for that Test case.

5. No fixed productive path may be opened, created, changed, renamed, or
   deleted.

6. Access remains prohibited to all of the following:

   - productive State paths;
   - Runtime-run directories;
   - Repository files outside the temporary root;
   - Live or Exchange state;
   - user configurations;
   - credentials;
   - network resources.

7. The exception applies only to later execution of this exact bound
   lifecycle ledger Test identity.

8. It does not apply to Source code, another Test, or a productive Runtime
   path.

9. It grants no current Test execution authority.

Sequential execution of multiple unittest Test cases may therefore create
multiple distinct temporary roots over time. The permitted unit is one
isolated active root per Test case, not one shared root for the whole suite.

### 6.3 Boundary for a later A2 rereview

A later, newly authorized A2 rereview remains completely read-only:

- no Tests;
- no unittest discovery;
- no Repository imports;
- no temporary files or directories;
- no compilation;
- no bytecode generation;
- no Runtime execution.

The proposed lifecycle exception may not be used by an A2 rereview. It is
relevant only to a later, separately authorized A3 Test execution.

## 7. Other independently observed A2 results

The following were independently observed read-only, but do not grant Test
or Publication authority:

- all six Source and Test paths were file-exact;
- Source diffs were exactly 439/0, 115/0, and 438/0;
- all 54 closure paths and identities matched;
- classification totals were 33/10/11;
- six Source roots produced a nine-path forward Import closure;
- all 48 direct derivation edges were present;
- all 841 Git-visible Python files were statically parseable;
- the two focused Tests respected their Repository-import allowlists;
- the two focused Tests had no side-effect markers;
- Artifact changes were additive and fail-closed;
- Loss Cluster transitions were pure and revisioned;
- strict V2 deserialization and legacy-v1 migration were bound;
- Path A, P2B, P2C, and excluded Consumer ownership sets remained separate;
- the Index was empty and no Index lock existed.

A later A2 rereview must derive every one of these findings again from the
current Repository. This proposal cannot be reused as file evidence.

## 8. Proposed effect and explicit non-effect

### 8.1 Proposed precision effect

If independently accepted, the proposal would establish only:

- absolute side-effect freedom for the two new focused Tests;
- one-Test-case-at-a-time TemporaryDirectory scope for the existing
  lifecycle persistence Test;
- continued prohibition of productive filesystem, Runtime, Live, and
  Exchange access;
- a contradiction-free boundary for a later newly authorized read-only A2
  rereview.

### 8.2 Explicit non-effect

This proposal causes and authorizes none of the following:

- Source or Test modification;
- Test execution;
- Test PASS;
- Evidence or Acceptance;
- an A2 READY decision;
- A3 authorization;
- staging;
- commit;
- push;
- Publication;
- Execution;
- Live action;
- Exchange action.

The blocker remains formally open until both conditions occur:

1. this precision resolution is independently accepted as a
   nonauthoritative reconciliation basis; and

2. a subsequent newly authorized A2 rereview independently reaches READY
   under the precise boundary.

Current formal status:

    A2-T3-TEMPORARY-FILESYSTEM-BOUNDARY-B1: OPEN

## 9. Fail-closed status

| Gate or boundary | Status |
|---|---|
| A2 | NOT_READY |
| A2-T3-TEMPORARY-FILESYSTEM-BOUNDARY-B1 | OPEN |
| A3 | NOT_AUTHORIZED |
| A4 | NOT_AUTHORIZED |
| A5 | NOT_AUTHORIZED |
| A6 | NOT_AUTHORIZED |
| A7 | NOT_AUTHORIZED |
| A8 | NOT_AUTHORIZED |
| A9 | NOT_AUTHORIZED |
| PATH_A_TEST_CLOSED | NO |
| PATH_A_STAGING_READY | NO |
| PATH_A_COMMIT_READY | NO |
| PATH_A_PUBLICATION_READY | NO |
| P2B-R | NOT_READY |
| P2B-T | NOT_AUTHORIZED |
| P2B-S | NOT_AUTHORIZED |
| P2B-C | NOT_AUTHORIZED |
| P2B-P | NOT_AUTHORIZED |
| P2B-A | NOT_AUTHORIZED |
| Path B | NOT_AUTHORIZED |
| P2C | NOT_AUTHORIZED |
| P1 | NOT_AUTHORIZED |
| P3 | NOT_AUTHORIZED |
| G0 | NOT_READY |
| G2 | NOT_AUTHORIZED |
| E1 | OPEN_FAIL_CLOSED |
| E2 | OPEN_FAIL_CLOSED |
| E3 | OPEN_FAIL_CLOSED |
| I7 Evidence | OPEN_FAIL_CLOSED |
| I7 Acceptance | OPEN_FAIL_CLOSED |
| Execution | OPEN_FAIL_CLOSED |
| Live | OPEN_FAIL_CLOSED |
| Exchange | OPEN_FAIL_CLOSED |

No gate changes state due to creation of this proposal.

## 10. Proposal limits and next required gate

This nonauthoritative proposal does not:

- execute or authorize a Test;
- import a Repository module;
- compile Source or Test code;
- create bytecode;
- create a temporary file or directory;
- modify an existing file;
- stage a path;
- create a commit;
- push, fetch, or access a network;
- create Evidence or Acceptance;
- authorize Publication, Execution, Live, or Exchange activity.

A later independent local read-only file-exact rereview must re-read this
proposal, every bound identity, the current Repository state, and the Test
boundary directly.

Even a READY rereview would not itself close
A2-T3-TEMPORARY-FILESYSTEM-BOUNDARY-B1, would not make A2 READY, would not
authorize A3, and would not grant any mutation or Publication authority.

Only after an independent READY rereview may a new explicit human
authorization request a repeated read-only A2 review under this precise
boundary.
