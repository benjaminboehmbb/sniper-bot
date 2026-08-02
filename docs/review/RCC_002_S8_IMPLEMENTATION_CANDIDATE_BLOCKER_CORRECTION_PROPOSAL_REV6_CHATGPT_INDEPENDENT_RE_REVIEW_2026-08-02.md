# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Revision 6 - ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-REV6-CHATGPT-IRR-001` |
| Review date | `2026-08-02` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Targeted independent re-review of correction proposal Revision 6 |
| Repository baseline represented by package | `b5a6aa627571777c9a1580c4ea09428f92d6c1d9` |
| Review package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REV6_REVIEW_INPUT_2026-08-02.zip` |
| Review package SHA-256 | `cc2ee7cea7f0feb2fd1af486004cd162c8e477c7bf083319c3ef34ff0b5a4efa` |
| Proposal | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_2026-08-02.md` |
| Proposal SHA-256 | `60ea3152b1446218d7754611f31a9460bb2a94fee3f7395d10dfdedefde30955` |
| Primary finding reviewed | `S8-CAND-TRACK1-GATE-B01` |
| Process finding reviewed | `S8-CAND-TRACK1-PROC-001` |
| Final decision | `REJECT` |

## 1. Review scope and restrictions

This was a read-only review of Revision 6 and the supplied snapshot. The
review assessed:

1. whether the five reported predecessor-suite failures are correctly
   identified and classified;
2. whether the proposed five-file additive repair can make the mandatory
   RCC-002 gate mechanically green;
3. whether the proposed `37 -> 42` Track 1 scope and `179 -> 184` ledger
   transition are consistent with the candidate's existing exact-scope
   verifiers;
4. whether the two proposed historical-replay adapters have sufficient
   inputs and interfaces to reproduce the certified predecessor assertions;
5. whether the proposed gate-scope declaration is itself mechanically
   governed; and
6. whether the supplied package excludes the protected builder.

No project file in the review snapshot was modified. No dependency was
installed. No network access, staging, committing, pushing, dataset activity,
or publication activity was performed.

The protected path `scripts/build_rcc002_spec_bundle.py` is absent from the
review snapshot. It was not read, hashed, inspected, opened, executed,
imported, copied, renamed, modified, staged, or packaged during this review.

## 2. Package and proposal integrity

The package passed the following checks:

- archive SHA-256 matched the supplied value;
- no absolute or parent-traversal archive member was present;
- no symbolic link was present;
- the protected builder was absent;
- the proposal SHA-256 matched
  `60ea3152b1446218d7754611f31a9460bb2a94fee3f7395d10dfdedefde30955`;
- the proposal was ASCII-only, LF-only, free of a BOM and trailing
  whitespace, had balanced Markdown fences, exactly one final newline, and
  529 lines; and
- the snapshot contained the represented 37-file Track 1 candidate and 33
  S8 candidate Python files.

## 3. Findings that Revision 6 diagnoses correctly

### 3.1 The five failures are real and historically caused

The two S8-RR-003 failures were independently executed and reproduced:

| Test | Independent result |
|---|---|
| `Case01ValidPositiveControl.test_full_repo_state_passes` | `ERROR: current_ledger_count_mismatch` |
| `ResourceHandlingRegression.test_no_resource_warning_on_successful_run` | `ERROR: current_ledger_count_mismatch` |

The local review environment did not contain the pinned review-only
`jsonschema==4.26.0` dependency, so the three decorated S8-RR-002 tests were
not counted as independently executed. Their reported failures were instead
confirmed directly from the certified source and candidate bytes:

| Contract | Certified predecessor expectation | Candidate value |
|---|---|---|
| Data Pipeline SHA-256 | `0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad` | `98608db199c525a2a7fcd05f2bff29c73ccad135b02fc0cd10fe180ca03b2e13` |
| Data Pipeline version in RM profile | `0.8.0` | `0.9.0` |
| RM version in RM profile | `0.9.0` | `0.9.1` |
| S8-RR-003 current ledger count | `145` | `179` |

This evidence supports Revision 6's core diagnosis: the predecessor pairs
encode correct point-in-time literals but read unversioned live paths, so the
authorized DP, RM, and root-ledger advancement makes their live-tree positive
controls fail.

### 3.2 The four certified predecessor files remain unchanged in the snapshot

The following snapshot hashes match their previously certified values:

| Path | SHA-256 |
|---|---|
| `scripts/rcc002/verify_s8rr002_artifacts.py` | `2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335` |
| `tests/rcc002/test_s8rr002_manifest_correction.py` | `2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4` |
| `scripts/rcc002/verify_s8rr003_normative_ledger.py` | `48c92bae7c8b5bd51c965fcd48917ffe0a3ee84c9dfe32bd490abab88f9b6cea` |
| `tests/rcc002/test_s8rr003_normative_ledger.py` | `07afd3045f60c8b1cf8109da8b2b4162c3b4d664dfb4108662d0fec005cbdbce` |

The historical-ledger copy also hashes to the certified 145-entry ledger
value:

`469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`

Revision 6 is therefore correct not to rewrite the predecessor literals merely
to match the successor live tree.

## 4. New findings

### 4.1 `S8-CAND-BCP-REV6-B01` - BLOCKER - the redefined gate has no executable routing mechanism

Revision 6 Section 6.4 excludes
`test_s8rr002_manifest_correction.py` and
`test_s8rr003_normative_ledger.py` from the live-tree pass/fail gate while
retaining both files unchanged under `tests/rcc002/`.

The five proposed artifacts contain:

- two frozen specification copies;
- one JSON gate-scope declaration; and
- two additive test modules.

They do not contain an executable gate runner, discovery hook, package loader,
CI definition, or other mechanism that consumes the declaration and changes
test selection. Python's existing command

```text
python -m unittest discover -s tests/rcc002 -p "test_*.py"
```

will continue to discover and execute both original predecessor modules. The
two new adapters add tests; they do not prevent the five existing failures.
Consequently, the same flat command remains red after all five proposed files
are added.

The proposal therefore does not close the gate it was written to repair. A
non-executable JSON declaration cannot redefine `unittest` discovery by
itself.

#### Required disposition

A successor proposal must define one exact, executable and versioned gate
authority. At minimum it must:

1. name the exact command that replaces flat discovery;
2. provide the executable runner or equivalent governed configuration that
   consumes an exact module partition;
3. prove every current-state module and both replay adapters execute exactly
   once;
4. prove the two predecessor modules remain directly runnable for historical
   audit but are not accidentally run against the live tree by the current
   gate;
5. reject missing, extra, duplicate, reordered, unsafe, or misclassified
   modules; and
6. receive the architecture/specification/certification authority that
   Revision 6 itself correctly recognizes as necessary for a cross-cutting
   governance redefinition.

Until that mechanism exists and is independently demonstrated, the mandatory
gate cannot be reported green.

### 4.2 `S8-CAND-BCP-REV6-B02` - BLOCKER - the proposed 42/184 state contradicts the unchanged exact-scope contracts

Revision 6 classifies items 38-42 as Track 1 additions and changes the ledger
arithmetic to 184, but simultaneously states that no existing Track 1 path
from items 1-37 is edited and that only root `SHA256SUMS` gains five lines.
Those statements cannot all be true.

The current candidate contains independent hardcoded contracts:

| Artifact | Current hardcoded contract |
|---|---|
| `RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` | 37 total, 3 modified, 34 new |
| `verify_s8candbcp_rev2_track1_normative_scope.py` | `EXPECTED_TOTAL = 37`, `EXPECTED_NEW = 34` and exact 37-entry tuple |
| `RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json` | 179 successor entries |
| `verify_s8candbcp_rev2_normative_ledger.py` | `EXPECTED_ADDED = 34`, `EXPECTED_SUCCESSOR = 179` |

Both existing verifiers independently pass the current 37/179 candidate.
After adding items 38-42 and changing only root `SHA256SUMS` to 184:

- the Track 1 scope manifest and verifier still omit all five files;
- the exact Track 1 inventory still reports 37 rather than 42;
- the normative-ledger scope manifest still reports 179;
- the normative-ledger verifier rejects the 184-entry ledger; and
- the relevant mutation tests no longer prove the successor contract being
  proposed.

Thus the repair is not purely additive. It necessarily modifies previously
listed Track 1 governance artifacts and causes additional count-neutral hash
replacements in the successor ledger. Revision 6's exact file counts, change
classifications, sequencing, and ledger-delta statement are incomplete.

#### Required disposition

A successor proposal must provide one exhaustive exact inventory that includes
every required modification. It must update and re-review at least the Track 1
scope manifest/verifier/test contract and the normative-ledger scope
manifest/verifier/test contract as necessary, then recompute the true ledger
arithmetic including every added path and every replaced digest. Independent
hardcoded expectations must remain separate from the mutable manifests.

### 4.3 `S8-CAND-BCP-REV6-ARCH-001` - MAJOR - the S8-RR-003 replay input is incomplete

Revision 6 item 42 says the S8-RR-003 adapter depends only on the existing
145-entry historical ledger copy and substitutes that file for live
`SHA256SUMS`.

The certified verifier does more than parse the ledger. Its
`run_verification(repo_root)` function also:

1. loads the certified scope manifest beneath `repo_root`;
2. requires the exact 145 paths and certified RM digest;
3. loads the earlier 110-entry historical evidence copy;
4. requires the 110-entry and 145-entry ledgers to differ; and
5. hashes every one of the 145 declared target files beneath `repo_root`.

Substituting only the root ledger is therefore insufficient. The current live
DP and RM files do not match the 145-entry ledger, and a temporary replay root
containing only that ledger cannot pass target verification. The proposal does
not require item 42 to use items 38-39, construct a complete deterministic
historical root, or define a safe verified overlay for all 145 targets.

The S8-RR-002 verifier presents a related interface issue: its relevant paths
are module-level `REPO` constants rather than parameters. Merely importing its
functions does not retarget all file reads. A replay adapter needs an explicit,
testable strategy for isolated path injection or a complete temporary replay
root without modifying the certified module.

#### Required disposition

The proposal must specify exact replay-root construction and provenance for
every file read by both certified verifiers. It must demonstrate the original
end-to-end positive controls against those roots, not merely reimplement a
subset of assertions or call selected pure helpers. Negative controls must
prove that substitution of current DP, RM, or ledger bytes fails.

### 4.4 `S8-CAND-BCP-REV6-TEST-001` - MAJOR - the gate-scope declaration is unauthenticated policy

Item 40 decides which tests count toward the mandatory gate. That is a
security- and certification-sensitive policy boundary: a forged category can
hide an arbitrary failing module.

Revision 6 gives item 40 no independent hardcoded consumer, no exact-schema
verifier, and no mutation-test contract. Its two adapter modules are explicitly
exempted from the normal nine-case scope-verifier mutation minimum. This leaves
the proposed gate partition self-declared and mechanically unaudited.

#### Required disposition

The executable gate authority required by `S8-CAND-BCP-REV6-B01` must enforce
an independently hardcoded exact module set and exact metadata. Tests must
cover at least missing, extra, duplicate, reordered, unsafe, wrong-category,
unknown-module, adapter-omission, and valid-positive-control cases.

## 5. Assessment of the process finding

Revision 6 appropriately discloses `S8-CAND-TRACK1-PROC-001` and does not
claim that a historical access can be undone. The supplied snapshot excludes
the protected file, and this review did not access it.

The review cannot independently attest to actions taken in the external
proposal-preparation session beyond the evidence supplied. The process finding
therefore remains a disclosure and clean-session obligation; it is not closed
by approval or rejection of the technical architecture.

## 6. Decision

Revision 6 correctly diagnoses why five predecessor positive controls fail
after an authorized successor advancement. It also correctly rejects rewriting
the certified historical literals.

The proposed repair does not, however, close the blocker:

- flat discovery remains red because no executable routing mechanism exists;
- the claimed 42/184 state contradicts the unchanged hardcoded 37/179 scope
  contracts;
- the S8-RR-003 replay lacks the historical target tree required by the
  certified end-to-end verifier; and
- the gate-scope policy has no independent mechanical authority or mutation
  coverage.

No Revision 6 implementation artifacts are authorized by this review. The
37-file Track 1 candidate remains not reviewable and not certifiable. Track 2,
dataset generation, dataset publication, and deployment remain unauthorized.

REJECT
