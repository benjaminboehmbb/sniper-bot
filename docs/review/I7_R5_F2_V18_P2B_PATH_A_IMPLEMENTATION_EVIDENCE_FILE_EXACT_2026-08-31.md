# I7 R5-F2 V18 P2B Path A Implementation Evidence - File-Exact - 2026-08-31

## 1. Classification and authority

~~~text
DOCUMENT_CLASSIFICATION:NONAUTHORITATIVE_P2B_PATH_A_A3_IMPLEMENTATION_EVIDENCE_CANDIDATE
A3_IMPLEMENTATION_SIDE_TEST_RESULT:PASS
A3_COMPLETE_TEST_MANIFEST_DECISION:READY
PATH_A_PUBLICATION_AUTHORITY:NONE
A4_STAGING_AUTHORITY:NONE
P2B_ACCEPTANCE_AUTHORITY:NONE
I7_EVIDENCE_AUTHORITY:NONE
I7_ACCEPTANCE_AUTHORITY:NONE
EXECUTION_AUTHORITY:NONE
LIVE_AUTHORITY:NONE
EXCHANGE_AUTHORITY:NONE
~~~

This candidate documents only the observed locally isolated A3 execution. It
is implementation-side evidence and is not self-accepting. Historical PASS or
READY values are not reused as new Acceptance. Before an independent
file-exact rereview, this candidate is neither publication-authoritative nor
staging-authoritative.

A4 remains blocked until this candidate has been independently accepted
file-exactly and a new explicit human authorization defines the
nonoverlapping staging manifest. G0 remains NOT_READY. P1, P2C and G2 remain
unauthorized. E1-E3 and all I7 Evidence, Acceptance, Execution, Live and
Exchange boundaries remain open and fail-closed.

## 2. Repository and Base binding

~~~text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:bafb2f4de22811e2bf171060cf3f18a4d32e769d
MAIN:bafb2f4de22811e2bf171060cf3f18a4d32e769d
ORIGIN_MAIN:bafb2f4de22811e2bf171060cf3f18a4d32e769d
PARENT:d1e865f29f507fcf7eb405c3be7da4a8946b9861
STAGED_RECORDS:0
TRACKED_UNSTAGED_RECORDS:10
UNTRACKED_RECORDS:93
WORKING_TREE_RECORDS:103
STATUS_SHA256:9a5426c2d1ec2a6e0153668eb799d54afcb1c80b6447f7d886a62cdb9ed0e38b
STATUS_BYTES:8566
STATUS_RECORDS:103
~~~

The canonical Worktree content manifest format was one LF-terminated line per
record, sorted lexicographically by path:

~~~text
<status2>\t<whole-file-sha256>\t<path>\n
CONTENT_MANIFEST_SHA256:d38cc02abdf21ee4cfffce22ab40282f5c9415d4ce13623a12a41230fd0d9c8c
CONTENT_MANIFEST_BYTES:15261
CONTENT_MANIFEST_LINES:103
~~~

## 3. File-exact governance foundations

| Role | Path | Whole-file SHA-256 |
|---|---|---|
| Path A closure scope | docs/review/I7_R5_F2_V18_P2B_PATH_A_DEPENDENCY_PUBLICATION_CLOSURE_SCOPE_RECONCILIATION_PROPOSAL_FILE_EXACT_2026-08-31.md | ac4c2882861365c7807f8781ec69912baac531405303b316baef9042311e46ac |
| A2 blocker reconciliation | docs/review/I7_R5_F2_V18_P2B_PATH_A_A2_FILESYSTEM_BOUNDARY_BLOCKER_RECONCILIATION_PROPOSAL_FILE_EXACT_2026-08-31.md | abebea3a5e8660258b894104eaa2b89567c51cdfb0a5cd0e617d3fd0d55ab897 |
| Accepted A2 precision resolution | docs/review/I7_R5_F2_V18_P2B_PATH_A_A2_FILESYSTEM_BOUNDARY_PRECISION_RESOLUTION_PROPOSAL_FILE_EXACT_2026-08-31.md | 659ce2a57e3776f25fc510d051c2ddc1ed58979607e373aab4595fcc939d71d3 |

~~~text
ACCEPTED_PREDECESSOR_DECISION:I7_R5_F2_V18_P2B_PATH_A_A2_SOURCE_TEST_DIFF_EFFECT_CONSUMER_REREVIEW_READY
OBSERVED_A3_DECISION:I7_R5_F2_V18_P2B_PATH_A_A3_COMPLETE_TEST_MANIFEST_READY
~~~

Neither decision supplies publication or staging authority.

## 4. Six-path Path A overlay

| Path | Whole-file SHA-256 | Bytes | Lines | Delta |
|---|---|---:|---:|---|
| live_l1/state/iu4_lifecycle_ledger.py | d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337 | 18211 | 438 | ADD |
| live_l1/state/loss_cluster.py | 4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55 | 18475 | 521 | MODIFICATION_FROM_BASE |
| live_l1/state/paper_artifacts.py | 3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946 | 57620 | 1575 | MODIFICATION_FROM_BASE |
| tests/live_l1/test_iu4_lifecycle_ledger.py | f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093 | 3940 | 50 | ADD |
| tests/live_l1/test_loss_cluster_i6_transitions.py | fff45d2dfa972a8a820a2a9deba4535927dea9847af54395153ee98fb69ecd13 | 9223 | 246 | ADD |
| tests/live_l1/test_paper_artifacts_i6_dependencies.py | 5a268abd386de90ec3ba1ce7c9b98f847494814ee66fc04d31c1fcc4e8caa53e | 12635 | 307 | ADD |

The overlay manifest used one LF-terminated line per path, sorted
lexicographically:

~~~text
100644<SPACE><whole-file-sha256><SPACE><path><LF>
OVERLAY_MANIFEST_SHA256:4ddec3664e295f062d5ad0f81c429302fe37c92e5679f0a073aee8cfa9284f12
OVERLAY_MANIFEST_BYTES:680
OVERLAY_MANIFEST_LINES:6
~~~

## 5. Execution-only Base regression bindings

These Base-identical Tests were execution-only and are not Path A
publication-owned additions.

| Path | Whole-file SHA-256 |
|---|---|
| tests/live_l1/test_loss_cluster_state.py | 0a7823175eb55d39d22d0576e1d58296d4b5123028e0fbfff561c1a6b642fe35 |
| tests/live_l1/test_paper_account.py | 88bb788e0cd816dbb9d724f18de5f73b6e10c4aaacaf2049632b78d184fb9641 |
| tests/live_l1/test_paper_position.py | c11678a2f43312922e0733e070887275932b7fa907de1577c213422c3c1bb26a |
| tests/live_l1/test_paper_economics_profile_candidate.py | 6bd98a2dea644aef77238c2dfd1cab1dcfe4a73fc59e442a2b2414871fdd6c14 |
| tests/live_l1/test_pre_execution_guards.py | 38192c5f96814bb0b3899e08453d3764cc1a14f9a7af52de218d4a2e0280248c |

## 6. A3 preflight and static closure

The local preflight freshly confirmed the bound Branch, refs, Parent, empty
Index, absent Index lock, absent Merge/Rebase/Cherry-pick/Revert/Bisect state,
both manifests and every governance, Source, Test and overlay identity.

All 54 closure paths parsed statically without Repository imports.

~~~text
FULL_CLOSURE_PATHS:54
TRACKED_IDENTICAL_AT_BASE:33
TRACKED_MODIFIED_FROM_BASE:10
UNTRACKED_IN_WORKTREE:11
IDENTITY_MISMATCH:0
UNAVAILABLE:0
SOURCE_ROOTS:6
DIRECT_DERIVATION_EDGES:48
FORWARD_IMPORT_CLOSURE_PATHS:9
~~~

## 7. Isolated Publication Tree and import closure

The Publication Tree was materialized only from local Git object
bafb2f4de22811e2bf171060cf3f18a4d32e769d and the six-path overlay.

~~~text
ADDS:4
MODIFICATIONS_FROM_BASE:2
DELETIONS:0
MISSING_BASE_PATHS:0
TOTAL_DELTA_PATHS:6
~~~

Its minimal Path A forward-import closure contained exactly:

1. live_l1/core/paper_economics.py
2. live_l1/state/iu4_lifecycle_ledger.py
3. live_l1/state/loss_cluster.py
4. live_l1/state/paper_artifacts.py

The static Test import audit found 23 local direct Test-import edges. Every
target resolved inside the isolated Publication Tree.

## 8. Compilation boundary

Of the 54 closure paths, 45 were materialized by Base plus Path A. Together
with the eight Test modules, 50 unique paths compiled successfully. All
bytecode stayed below the validated external A3 temporary root. The canonical
Repository received no bytecode or Test artifact.

These nine untracked downstream/consumer paths were intentionally absent,
uncompiled and unimported:

1. live_l1/core/paper_iu4_runtime_gate.py
2. live_l1/state/paper_iu4_recovery_projection.py
3. live_l1/tools/validate_terminal_lease_capability.py
4. tests/live_l1/test_paper_atomic_coordinator_v2.py
5. tests/live_l1/test_paper_iu4_adapter_v2.py
6. tests/live_l1/test_paper_iu4_execution_seam_v2.py
7. tests/live_l1/test_paper_iu4_recovery_projection.py
8. tests/live_l1/test_paper_iu4_runtime_gate.py
9. tests/live_l1/test_terminal_lease_capability.py

Their absence positively proves the nonoverlapping Path A boundary and is not
a Compilation gap.

## 9. Exact Test manifest and result

Exactly these eight modules ran together without unittest discovery:

1. tests/live_l1/test_iu4_lifecycle_ledger.py
2. tests/live_l1/test_paper_artifacts_i6_dependencies.py
3. tests/live_l1/test_loss_cluster_i6_transitions.py
4. tests/live_l1/test_loss_cluster_state.py
5. tests/live_l1/test_paper_account.py
6. tests/live_l1/test_paper_position.py
7. tests/live_l1/test_paper_economics_profile_candidate.py
8. tests/live_l1/test_pre_execution_guards.py

~~~text
STATICALLY_BOUND_TEST_METHODS:105
EXECUTED_TESTS:105
PASSED:105
FAILURES:0
ERRORS:0
UNEXPECTED_SKIPS:0
RETURN_CODE:0
OBSERVED_RUNTIME_SECONDS:0.038
TEST_OUTPUT_SHA256:a41ff8b447f73ea62ce61cc563b06453fddd43049cef576189873569befcd62f
~~~

Observed unittest terminus:

~~~text
Ran 105 tests in 0.038s

OK
~~~

The path-bounded git diff --check, untracked whitespace checks and
git diff --cached --check passed. No P2B-external Worktree Source and no P2C,
Loop, Adapter, Startup, Shadow, Terminal, Live or Exchange Worktree path was
needed.

## 10. Temporary boundary and preservation

The validated temporary root was:

~~~text
/tmp/i7-r5-f2-v18-p2b-path-a-a3.ei9nazdx
~~~

It was confirmed immediately below /tmp with the required prefix before use
and removal, then completely removed.

Post-execution state:

~~~text
HEAD:bafb2f4de22811e2bf171060cf3f18a4d32e769d
MAIN:bafb2f4de22811e2bf171060cf3f18a4d32e769d
ORIGIN_MAIN:bafb2f4de22811e2bf171060cf3f18a4d32e769d
STAGED_RECORDS:0
TRACKED_UNSTAGED_RECORDS:10
UNTRACKED_RECORDS:93
WORKING_TREE_RECORDS:103
STATUS_SHA256:9a5426c2d1ec2a6e0153668eb799d54afcb1c80b6447f7d886a62cdb9ed0e38b
STATUS_BYTES:8566
STATUS_RECORDS:103
CONTENT_MANIFEST_SHA256:d38cc02abdf21ee4cfffce22ab40282f5c9415d4ce13623a12a41230fd0d9c8c
CONTENT_MANIFEST_BYTES:15261
CONTENT_MANIFEST_LINES:103
CANONICAL_ARTIFACT_SET_UNCHANGED:YES
NETWORK_ACTIONS:0
STAGING_ACTIONS:0
COMMITS:0
PUSHES:0
FETCHES:0
PULLS:0
~~~

## 11. Fail-closed conclusion

~~~text
A3_IMPLEMENTATION_SIDE_TEST_RESULT:PASS
A3_COMPLETE_TEST_MANIFEST_DECISION:READY
A4:NOT_AUTHORIZED
PATH_A_PUBLICATION:NOT_AUTHORIZED
G0:NOT_READY
P1:NOT_AUTHORIZED
P2C:NOT_AUTHORIZED
G2:NOT_AUTHORIZED
E1:OPEN
E2:OPEN
E3:OPEN
I7_EVIDENCE_BOUNDARY:OPEN_FAIL_CLOSED
I7_ACCEPTANCE_BOUNDARY:OPEN_FAIL_CLOSED
EXECUTION_BOUNDARY:OPEN_FAIL_CLOSED
LIVE_BOUNDARY:OPEN_FAIL_CLOSED
EXCHANGE_BOUNDARY:OPEN_FAIL_CLOSED
~~~

This candidate asserts no Evidence Acceptance, Staging, Publication,
Execution, Live or Exchange authority.
