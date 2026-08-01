# RCC-002 S8-RR-003 Normative Ledger Proposal Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR003-NLBCP-INDEPENDENT-REVIEW-001` |
| Review date | `2026-08-01` |
| Review class | Independent scientific and architecture review |
| Repository baseline | `42d70c03fbcac55bbe0782e1ac105299eafccfaf` |
| Review package | `RCC_002_S8RR003_NORMATIVE_LEDGER_PROPOSAL_REVIEW_INPUT_2026-08-01.zip` |
| Review package SHA-256 | `fc2480f65303eabf3c2caece569ffa86a3614a7bebdb278ac9c0b345986b2ab4` |
| Primary target | `RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md` |
| Triggering review | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md` |
| Finding in scope | `S8-RR3-B01` |
| Reviewer | Independent Claude-based review agent |
| Final decision | `REJECT` |

The review-package digest was supplied by the repository owner and was not
independently recomputed from the ZIP because the review operated on its
already extracted, read-only snapshot.

## 1. Exact scope and restrictions

This review assessed only whether the proposed normative-ledger lifecycle and
integrity correction is complete, deterministic, non-circular and suitable to
authorize generation of the later five-file correction candidate.

The review was read-only:

- no project file was created, modified, deleted, renamed or moved;
- no dependency was installed or updated;
- no file was staged, committed or pushed;
- no network access or external browsing was used;
- no S8 production code was created;
- no dataset was generated or published;
- the protected `scripts/build_rcc002_spec_bundle.py` was confirmed absent
  from the isolated snapshot and was not searched for outside that snapshot;
- only passive diagnostic commands were used;
- no Python interpreter was invoked, avoiding `__pycache__` creation.

All material counts, overlaps and hash claims were re-derived from the
snapshot bytes rather than accepted from the proposal.

## 2. Evidence inspected

The review inspected:

1. the complete primary proposal;
2. the triggering S8-RR-003 readiness review;
3. repository-root `SHA256SUMS`;
4. `RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
5. the current RM `0.9.0` specification;
6. `verify_s8rr002_artifacts.py`;
7. `test_s8rr002_manifest_correction.py`;
8. the S8BCP-001 Revision 2 architecture review, resolution,
   correction-verification and certification evidence that defines the root
   ledger meaning;
9. the S8-RR-002 proposal, review and certification chain relevant to its 30
   correction outputs;
10. `rcc002/IMPLEMENTATION_BLOCKERS.md` and
    `requirements-rcc002-review.txt`;
11. relevant repository directory inventories.

## 3. Independent results

### 3.1 Trigger and authority

`S8-RR3-B01` is real and blocking. The triggering review explicitly records:

```text
S8 IMPLEMENTATION READINESS: NOT READY
IMPLEMENTATION AUTHORIZATION: DENIED UNTIL BLOCKER CLOSURE
```

Prior certified documents independently state that repository-root
`SHA256SUMS` is the certified S8BCP-001 Revision 2 normative-bundle ledger and
not a complete implementation or test-tree inventory.

The following claims were independently reproduced:

| Check | Result |
|---|---|
| Root-ledger SHA-256 | `a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43` |
| Ledger entries | 110 |
| Unique ledger paths | 110 |
| Path ordering | strict `LC_ALL=C` lexical order |
| Historical RM digest | `22d6460f16f7f70e677a40dcd4e428e3739d9bb37fb0f7340512cca1b1ebb382` |
| Current RM `0.9.0` digest | `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1` |
| `sha256sum -c SHA256SUMS` | 109 `OK`, exactly one RM failure |

No unsupported authority claim was identified.

### 3.2 Exact successor scope arithmetic

The reviewer independently extracted:

- 110 unique historical root-ledger paths;
- 30 unique `correction_candidate_outputs` from the S8-RR-002 scope;
- six unique S8-RR-003 lifecycle paths from the proposal.

The only overlap between the 110 historical paths and 30 S8-RR-002 outputs is:

```text
docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md
```

The six S8-RR-003 paths overlap neither earlier set. The exact union therefore
contains:

```text
110 + 30 - 1 + 6 = 145 paths
```

The union accounts for RM `0.9.0`, Dataset Manifest Schema `1.0.1`, both
positive fixtures, all 21 negative fixtures, `CASE_LEDGER.json`, the S8-RR-002
scope, verifier, tests and review-only dependency pin.

Two of the six S8-RR-003 paths already exist: the triggering readiness review
and the proposal. The four future paths are correctly absent because they
belong to the later correction candidate.

No unjustified path inclusion or omission was identified.

### 3.3 Lifecycle design

The lifecycle design is materially sound:

- the old ledger can be preserved byte-for-byte under the proposed versioned
  evidence path;
- its fixed SHA-256 makes silent historical rewriting detectable;
- the new root ledger supersedes it prospectively;
- the historical copy is explicitly prohibited from acting as a current-tree
  ledger;
- exclusion of root `SHA256SUMS` from its own entries avoids self-reference;
- the scope file contains paths but no file hashes, so including it in the new
  ledger introduces no circular hash dependency;
- verifier and test files need not embed the future root-ledger digest;
- later independent reviews and certification evidence are explicitly outside
  the frozen successor scope;
- normative-bundle, full-repository and package-transport integrity remain
  clearly distinguished.

No lifecycle or circularity defect was found.

### 3.4 Machine-readable scope

The proposed three source arrays and deduplicated `current_ledger_paths` array
are independently derivable from fixed artifacts. The proposal prohibits
directory discovery, recursive scans, naming heuristics and mutable globs as
scope authority.

The path and hash authorities remain separated: the scope manifest defines
membership, while root `SHA256SUMS` defines file-byte hashes.

One minor schema-hygiene issue remains. The proposed structurally different
scope manifest reuses `scope_schema_version: "1"` from the S8-RR-002 scope
without saying whether this version is global or scoped to `scope_id`. This is
recorded as `IR-F03`.

### 3.5 Ledger format

The prose requirements for ASCII, LF, two-space separation, `./`-prefixed POSIX
paths, exact membership, ordering, regular files, symlink rejection, self
exclusion and content hashes are coherent.

The literal regular expression in Section 5 item 3 is not coherent:

```text
^[0-9a-f]{64}  \\./[^\\r\\n]+$
```

Parsed literally:

1. `\\.` requires a literal backslash followed by an arbitrary character,
   rather than a literal period;
2. `[^\\r\\n]` excludes literal backslash plus the ordinary letters `r` and
   `n`, rather than excluding actual CR and LF bytes.

It therefore rejects every valid `./`-prefixed ledger line and wrongly rejects
ordinary repository paths containing `r` or `n`. It also fails to express the
intended CR/LF exclusion.

This deterministic contradiction is `IR-F01`, a blocker.

### 3.6 Verifier architecture

The required verification order is fail-closed:

1. validate scope metadata;
2. compare each category with independent hardcoded lists;
3. independently derive the 145-path union;
4. reject duplicates and invalid overlap;
5. parse and validate all ledger lines;
6. require exact ordered equality;
7. only then read and hash the declared target files.

This mirrors the already certified S8-RR-002 verifier pattern. No recursive
discovery is necessary. Protected-builder exclusion can be implemented as a
literal path-membership prohibition without reading the protected file.

No additional material TOCTOU, path-alias, symlink, encoding or parser defect
was found beyond the broken format regex.

### 3.7 Mutation-test adequacy

All required functional categories have coverage:

| Category | Proposed mutation numbers |
|---|---|
| Missing | 2, 3, 4, 15, 20 |
| Extra | 5, 16 |
| Duplicate | 6, 7, 17 |
| Reordered | 8, 9, 18 |
| Unsafe path | 11, 12, 13 |
| Malformed | 10, 19 |
| Self-reference | 14 |
| Symlink | 21 |
| Historical integrity | 24 |
| Stale RM | 23 |
| Wrong digest | 22 |
| Protected builder | 25 |

Section 5 also requires ASCII-only bytes, LF-only line endings and exactly one
final newline. The mutation list does not explicitly test CRLF, a missing or
extra final newline, or a non-ASCII byte. This is `IR-F02`, a minor finding.

### 3.8 Change boundary and process

The proposed five payload files are sufficient and minimal:

```text
SHA256SUMS
docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt
docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json
scripts/rcc002/verify_s8rr003_normative_ledger.py
tests/rcc002/test_s8rr003_normative_ledger.py
```

The committed readiness review and proposal can remain immutable inputs. No
specification, schema, fixture, S0-S7 implementation or production dependency
requires modification.

The controlled sequence correctly requires proposal review, candidate
generation, verification, independent candidate review, certification,
controlled commit, regenerated implementation input and repeated readiness.

No S8 implementation or dataset publication is authorized.

## 4. Findings

| ID | Severity | Location | Summary |
|---|---|---|---|
| `IR-F01` | BLOCKER | Section 5 item 3 | Literal regex rejects all valid ledger lines and does not express CR/LF exclusion |
| `IR-F02` | MINOR | Section 8 | No explicit ASCII, CRLF or final-newline mutations |
| `IR-F03` | MINOR | Section 4.3 | Scope schema version reuse is not qualified |
| `IR-F04` | INFORMATIONAL | Document-control chain | Git ancestry cannot be re-derived without `.git` in the review snapshot |
| `IR-F05` | INFORMATIONAL | Section 7 | Protected-builder membership check has no earlier implementation precedent |

### 4.1 IR-F01 - Broken ledger-line regular expression

Severity: **BLOCKER**

Location: proposal Section 5 item 3.

Evidence:

```text
^[0-9a-f]{64}  \\./[^\\r\\n]+$
```

The expression requires a literal backslash before the path and treats `r`
and `n` as forbidden path characters. It cannot match a valid line beginning
with `./`.

Impact: a verifier implementing the contract literally must reject all 145
valid successor-ledger lines and can never report `PASS`.

Required correction: replace the expression with an unambiguous grammar that
requires 64 lowercase hexadecimal characters, exactly two ASCII spaces, a
literal `./` prefix, and a path body excluding backslash plus actual CR/LF
bytes. Re-check the corrected literal character by character before re-review.

### 4.2 IR-F02 - Missing file-format mutations

Severity: **MINOR**

Location: proposal Section 8.

Evidence: Section 5 item 1 requires ASCII text, LF line endings and exactly one
final newline, but none of the 25 listed mutations explicitly tests these
conditions.

Impact: a test suite could satisfy the listed mutation contract without proving
that the parser enforces all declared file-format invariants.

Required correction: add explicit mutations for CRLF, missing final newline,
extra final newline and non-ASCII bytes.

### 4.3 IR-F03 - Ambiguous scope-schema version namespace

Severity: **MINOR**

Location: proposal Section 4.3.

Evidence: both the existing S8-RR-002 scope and the proposed structurally
different S8-RR-003 scope use `scope_schema_version: "1"`.

Impact: a future generic consumer could incorrectly assume that identical
schema-version strings imply identical JSON shapes.

Required correction: either use a distinct schema version for the new shape or
state explicitly that `scope_schema_version` is local to each `scope_id` and
does not identify a global common JSON schema.

### 4.4 IR-F04 - Snapshot lacks Git ancestry evidence

Severity: **INFORMATIONAL**

The proposal, triggering review and review snapshot carry successive baseline
hashes. Their ordering is plausible but cannot be cryptographically re-derived
inside an archive without `.git` history.

Required correction: none. Continue verifying ancestry during controlled
repository import.

### 4.5 IR-F05 - New protected-builder exclusion check

Severity: **INFORMATIONAL**

No earlier verifier contains this exact protected-builder exclusion check. It
is nevertheless mechanically simple and requires only path-string comparison,
not access to the protected file.

Required correction: none.

## 5. Confirmation of read-only mode

The reviewer explicitly confirmed that no repository file was modified,
created, deleted, renamed or moved. No dependencies, Git operations, network
access, S8 production code or dataset activity occurred. The protected builder
was confirmed absent from the snapshot and was never read, hashed or executed.

## 6. Explicit scope of decision

This decision applies only to the S8-RR-003 normative-ledger correction
proposal. It does not:

- authorize generation of the five-file correction candidate;
- authorize S8 production implementation;
- authorize dataset publication;
- certify any future correction artifact;
- replace the later independent candidate review required after proposal
  approval.

## 7. Final decision and rationale

The problem statement, authority chain, 145-path arithmetic, lifecycle design,
scope model, verifier architecture and five-file change boundary are materially
sound and independently reproducible.

The literal ledger-line regular expression is nevertheless a blocker because
it makes the contract unsatisfiable when implemented as written. Two minor
findings should be closed in the same revision: explicit file-format mutations
and a clear scope-schema version namespace.

The proposal must be revised and independently re-reviewed before any
five-file correction candidate is generated.

REJECT
