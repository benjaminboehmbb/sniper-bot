# RCC-002 S8-RR-003 Normative-Ledger Correction Candidate ChatGPT Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR003-CAND-CHATGPT-IR-001` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Independent correction-candidate review |
| Repository baseline | `6f5a71ffdf6851aa99ba2c7946dabe34fee6dd00` |
| Candidate package | `RCC_002_S8RR003_NORMATIVE_LEDGER_CORRECTION_CANDIDATE_REVIEW_INPUT_2026-08-01.zip` |
| Candidate package SHA-256 | `39405786b9fa6febbf19d402da435e1dbbfa0d804b89504a1d73b88b9f3bc428` |
| Certified comparison archive | `sniper-bot-6f0f840.zip` |
| Comparison archive SHA-256 | `e61fedfeb9ebe192e9690dda07aebf71af7e3c662d838d6f5bd82bee35e0f0c9` |
| Approved proposal | `RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md` |
| Approved proposal SHA-256 | `d81166a734fad826b96737d4cc9eddca621017b0497ca22b90b5102817f26554` |
| Approving proposal re-review SHA-256 | `7a3330cb0017aa9555ab120ebe694fd5a187b894fd8e8799aaf601fcff26fea4` |
| Finding in scope | `S8-RR3-B01` |
| Final decision | `REJECT` |

## 1. Exact review scope and restrictions

This review assessed the five-file correction candidate against the approved
Revision 2 contract. It covered package safety, change-boundary integrity,
historical-ledger preservation, exact successor scope, root-ledger identity,
verifier architecture, mutation coverage and executable evidence.

The review used only the extracted candidate snapshot and the previously
provided certified `6f0f840` source archive. No live repository was accessed.
No network access or dependency installation was used. No source file in the
candidate snapshot was modified. No S8 production code was created and no
dataset was published.

The protected file `scripts/build_rcc002_spec_bundle.py` was absent from the
candidate package and was not accessed.

## 2. Evidence inspected

The review inspected:

- the complete candidate package inventory;
- the complete certified comparison archive inventory;
- `SHA256SUMS`;
- the byte-exact historical ledger evidence copy;
- the S8-RR-002 versioned correction scope;
- the new S8-RR-003 versioned ledger scope;
- the approved Proposal Revision 2;
- the approving proposal re-review;
- `scripts/rcc002/verify_s8rr003_normative_ledger.py`;
- `tests/rcc002/test_s8rr003_normative_ledger.py`;
- all 145 files declared by the successor ledger.

## 3. Package and change-boundary results

### 3.1 Package safety

The ZIP path check passed. The package contained 1,626 regular files and no
absolute or parent-traversal entry. The protected builder was absent.

### 3.2 Full-tree comparison

A complete byte-hash comparison against certified archive `6f0f840` found:

- zero removed paths;
- one modified path: `SHA256SUMS`;
- nine added paths.

Five added paths are the known committed S8-RR-003 governance chain:

```text
docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md
docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md
docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-08-01.md
docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md
docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_INDEPENDENT_RE_REVIEW_2026-08-01.md
```

Their hashes match the committed governance evidence exactly. The remaining
four additions plus the modified root ledger are exactly the five authorized
candidate payload paths. No unexpected candidate path was found.

## 4. Historical ledger and exact successor scope

### 4.1 Historical evidence

The historical evidence copy has SHA-256:

```text
a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43
```

It is byte-identical to the former certified root ledger, contains exactly 110
sorted unique entries and preserves the stale RM digest:

```text
22d6460f16f7f70e677a40dcd4e428e3739d9bb37fb0f7340512cca1b1ebb382
```

### 4.2 Scope arithmetic

The three categories were independently reconstructed from repository files:

```text
historical normative paths: 110
S8-RR-002 correction outputs: 30
S8-RR-003 lifecycle outputs: 6
only overlap: RM specification path
deduplicated current union: 145
```

Therefore the approved arithmetic is correct:

```text
110 + 30 - 1 + 6 = 145
```

All four arrays in the new scope are lexically sorted, unique and exactly equal
to the independently reconstructed sets. The protected builder and root-ledger
self-entry are absent.

## 5. Successor root-ledger results

The successor root ledger has SHA-256:

```text
0eeb83894451607e17521eb97c475bc44146af5de52860788b9cb39e472ec3bc
```

Independent parsing confirmed:

- ASCII encoding;
- LF line endings;
- exactly one final newline;
- exactly 145 non-empty entries;
- exact lowercase SHA-256 grammar;
- exactly two ASCII separator spaces;
- literal `./` path prefixes;
- strict lexical path order;
- no duplicate line or path;
- no unsafe path;
- no symlink target;
- no root-ledger self-entry;
- exact path equality with the 145-path scope;
- exact hashes for all 145 declared targets.

The current RM digest is correctly updated to:

```text
23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1
```

Independent `sha256sum -c SHA256SUMS` verification returned 145 OK results and
zero non-OK results.

## 6. Verifier and test execution

### 6.1 Verifier

The candidate verifier returned deterministic `PASS` output with counts
`110/30/6/145/145` and the required historical-ledger and current-RM hashes.

### 6.2 Focused tests

All 30 focused test methods passed. They cover the 29 required cases plus one
supplementary arithmetic check.

### 6.3 Complete suites

Independent execution produced:

```text
focused S8-RR-003 tests: 30 passed
RCC-002 discovery: 689 run, 28 skipped, zero failures
TD-005 regression discovery: 170 passed
in-memory syntax compilation: PASS
```

The 28 skips are the pre-existing S8-RR-002 schema tests guarded by the
review-only `jsonschema==4.26.0` dependency, which was unavailable in the
isolated review environment. No dependency was installed during this review.
The repository owner separately reported a dependency-complete 689-test pass.

## 7. Findings

### 7.1 `S8RR003-CAND-ARCH-001` - MAJOR

**Location:**

- Proposal Revision 2, Section 4.3;
- `scripts/rcc002/verify_s8rr003_normative_ledger.py`,
  `validate_scope_metadata()` and `validate_scope_categories()`;
- `tests/rcc002/test_s8rr003_normative_ledger.py`, case 10.

**Contract:**

Revision 2 states that the scope metadata must be exact and that the scope
manifest must not contain file hashes. Hash authority belongs exclusively to
the root ledger, apart from the specifically authorized historical-ledger hash
metadata field.

**Evidence:**

`validate_scope_metadata()` checks that required keys exist and have expected
values, but it never requires exact top-level key-set equality. It also does
not reject an additional SHA-256-bearing field.

Two independent in-memory mutations were applied to the valid scope:

```text
unexpected_metadata_accepted=True
rogue_file_sha256_accepted=True
```

The second mutation added an unauthorized field containing a 64-character
lowercase hexadecimal value. All scope metadata, category and protected-path
validators accepted it.

Case 10 changes one expected metadata value. It does not test an extra key or
an unauthorized additional hash value.

**Impact:**

The scope manifest and root ledger are both permitted correction payloads. An
out-of-contract extra scope field can therefore be inserted while the scope
file's root-ledger digest is updated consistently. The final target-hash gate
then cannot detect the semantic contract violation. The verifier can report
`PASS` for a scope containing a prohibited second hash-authority value.

This defeats the approved exact-metadata and single-hash-authority boundary.
Certification must not rely on the current verifier.

**Required correction:**

1. Define the exact 14-key top-level scope schema independently in the
   verifier.
2. Require the parsed scope to be a JSON object with exact key-set equality.
3. Reject every missing or additional key before category processing.
4. Require category fields to be arrays of ASCII repository-relative strings.
5. Prove that the only 64-hex value anywhere in the scope is the exact
   `historical_ledger_sha256` value at its authorized field.
6. Add mutations for an extra ordinary metadata key and an extra SHA-256 field.
7. Add a full-chain mutation in which the scope bytes and corresponding root
   ledger digest are changed together; the verifier must reject before target
   hashing.

### 7.2 `S8RR003-CAND-IMPL-001` - MINOR

**Location:**

`scripts/rcc002/verify_s8rr003_normative_ledger.py`, lines associated with
historical evidence, scope-manifest and root-ledger reads.

**Evidence:**

The focused and complete RCC-002 executions emitted three `ResourceWarning`
messages for unclosed binary file objects created by direct
`open(path, 'rb').read()` expressions.

**Impact:**

The current command-line run terminates successfully, so ledger correctness is
not affected. The implementation nevertheless leaks file descriptors during a
longer-lived import/test process and produces non-clean verification evidence.

**Required correction:**

Use context managers or `Path.read_bytes()` for all three reads. Add a focused
warning-sensitive execution check that produces no `ResourceWarning`.

### 7.3 `S8RR003-CAND-IMPL-002` - MINOR

**Location:**

- `validate_scope_metadata()`;
- `validate_scope_categories()`;
- `main()` exception handling.

**Evidence:**

Independent type mutations produced:

```text
non_object_scope: TypeError
non_list_category: TypeError
```

`main()` catches only `VerificationError`. These malformed but valid JSON
shapes therefore escape the deterministic failure-report path and can produce
a traceback instead of the required single deterministic failure object.

**Impact:**

The verifier fails closed and emits no `PASS`, but it does not meet the
approved requirement to identify every failed invariant through its controlled
deterministic output.

**Required correction:**

Validate the scope root and category JSON types explicitly and convert all such
contract failures into named `VerificationError` invariants. Add non-object and
non-array mutation tests.

## 8. Closure assessment

The candidate correctly preserves the certified historical ledger, constructs
the intended exact 145-path successor scope and produces a byte-correct root
ledger. Its current clean inputs verify 145/145.

However, `S8RR003-CAND-ARCH-001` shows that the required mechanical verifier is
not complete for the approved exact-scope and hash-authority contract. Two
additional implementation defects also require focused correction.

The candidate is therefore not certifiable in its current form.

## 9. Required focused repair boundary

A repair may change only:

```text
SHA256SUMS
scripts/rcc002/verify_s8rr003_normative_ledger.py
tests/rcc002/test_s8rr003_normative_ledger.py
```

The scope manifest, historical evidence copy and every other repository file
must remain byte-identical. `SHA256SUMS` may change only to record the repaired
verifier and test-file hashes; its 145-path ordered scope must remain unchanged.

After repair, repeat independent candidate review before certification.

## 10. Authorization boundary

This rejection does not authorize S8 production implementation or dataset
publication. It does not alter the approved proposal. It only blocks
certification of the current five-file candidate pending the focused repair and
independent re-review.

## 11. Final decision and rationale

The normative data and ledger are correct, but the verifier accepts a forbidden
extension of the exact scope and hash-authority model. Because the verifier is
the mechanical certification gate, this is a major unresolved defect.

REJECT
