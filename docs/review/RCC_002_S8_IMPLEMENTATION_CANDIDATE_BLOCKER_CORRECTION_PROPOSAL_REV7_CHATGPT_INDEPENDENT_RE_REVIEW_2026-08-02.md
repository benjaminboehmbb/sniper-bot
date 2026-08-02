# RCC-002 S8 Implementation Candidate Blocker Correction Proposal Revision 7 - ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-BCP-REV7-CHATGPT-IRR-001` |
| Review date | `2026-08-02` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Targeted independent re-review of correction proposal Revision 7 |
| Repository baseline | `5a15b5963bcf2e701ec15dbf7fcc79872caa7ff5` |
| Review package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_CORRECTION_PROPOSAL_REV7_REVIEW_INPUT_2026-08-02.zip` |
| Review package SHA-256 | `c0bcae8593f8ea5dcd7ea4391f69704852b075732c90494f882dec6a4e01125c` |
| Proposal | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV7_2026-08-02.md` |
| Proposal SHA-256 | `7946fff01560698294e322ecea0dec30c90f5d976b7b3805ea9161e157120ff6` |
| Controlling prior review | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV6_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-02.md` |
| Controlling prior review SHA-256 | `be576d0c3c132602fddcc9196f703c58a8f0b94611152f28d56665cf8d9f082f` |
| Final decision | `REJECT` |

## 1. Exact review scope and restrictions

This was a read-only scientific and architecture re-review of Revision 7.
The review asked whether the proposal completely and unambiguously closes:

- `S8-CAND-BCP-REV6-B01`;
- `S8-CAND-BCP-REV6-B02`;
- `S8-CAND-BCP-REV6-ARCH-001`; and
- `S8-CAND-BCP-REV6-TEST-001`.

The review also checked whether the proposed gate, historical replay roots,
scope inventories, ledger arithmetic, verification boundaries, and adoption
sequence form one executable, fail-closed, reviewable architecture.

No repository file was modified, staged, committed, pushed, generated, or
published during this review. No dependency was installed or updated. No
network access was used. No S8 production code or dataset was created.

The protected file `scripts/build_rcc002_spec_bundle.py` was confirmed absent
from the review package. It was not read, hashed, inspected, opened, executed,
imported, copied, renamed, modified, staged, packaged, or used as evidence.

## 2. Package integrity and static checks

The following checks passed:

1. The package SHA-256 matched
   `c0bcae8593f8ea5dcd7ea4391f69704852b075732c90494f882dec6a4e01125c`.
2. Archive member paths were relative and contained no traversal component.
3. No symbolic link was present.
4. The protected builder was absent.
5. The proposal SHA-256 matched
   `7946fff01560698294e322ecea0dec30c90f5d976b7b3805ea9161e157120ff6`.
6. The proposal was ASCII-only, LF-only, free of trailing whitespace, had
   balanced Markdown fences, exactly one final newline, and 1192 lines.
7. The package contained 33 S8 candidate Python files, as declared.

## 3. Independently reproduced facts

### 3.1 Test-module population

Static enumeration found 57 existing `tests/rcc002/test_*.py` modules in the
snapshot. Removing the two certified historical modules leaves 55 existing
current-state modules. Adding the proposed gate-scope mutation-test module
would yield 56 current-state modules. Adding two replay adapters and retaining
two audit-only historical modules would yield 60 classified modules.

Therefore the numerical partition `60 = 56 + 2 + 2` is arithmetically
plausible. This does not cure the missing exact module inventory identified in
finding `S8-CAND-BCP-REV7-B01`.

### 3.2 Certified predecessor test coverage

Static AST enumeration found:

- 28 test methods in
  `tests/rcc002/test_s8rr002_manifest_correction.py`; and
- 41 test methods in
  `tests/rcc002/test_s8rr003_normative_ledger.py`.

The latter includes both
`test_full_repo_state_passes` and
`test_no_resource_warning_on_successful_run`, in addition to the mutation
coverage certified with S8-RR-003.

### 3.3 S8-RR-002 replay arithmetic

The certified S8-RR-002 scope contains 11 immutable reference inputs and 30
candidate outputs. The categories are disjoint, so their union contains 41
paths. The verifier, test module, Data Pipeline specification, and RM
specification are four paths in that union. The exact remainder is therefore:

`41 - 4 = 37`

It is not 39.

### 3.4 Ledger and governance path

The candidate `SHA256SUMS` contains 179 entries. `CLAUDE.md` is not one of
those entries. It is also not one of the 145 certified baseline-ledger paths.

## 4. Positive architecture assessment

Revision 7 makes substantial progress:

- it selects one named gate command;
- it distinguishes current-state, replay-adapter, and audit-only categories;
- it introduces a separately verified gate-scope document;
- it gives S8-RR-002 an isolated subprocess replay root;
- it gives S8-RR-003 a parameterized isolated root;
- it includes negative controls for historical/live divergence; and
- it updates the intended Track 1 and successor-ledger arithmetic.

These are useful architectural decisions. They are not sufficient for
approval because the binding policy and completion sequence remain incomplete,
and one replay adapter drops certified coverage.

## 5. Findings

### 5.1 `S8-CAND-BCP-REV7-B01` - BLOCKER - The exact 60-module gate partition is absent

Revision 7 claims an exact, hardcoded, independently verified 60-module
partition, but Section 5.4 contains placeholders rather than lists:

```text
current_state_modules             [ ...56 entries, LC_ALL=C order... ]
historical_replay_adapter_modules [ ...2 entries, LC_ALL=C order... ]
historical_audit_only_modules     [ ...2 entries, LC_ALL=C order... ]
```

The proposal then says the exact lists appear in Sections 5.3 and 7. They do
not. Section 5.3 defines category semantics. Section 7 is a Track 1 artifact
inventory, not an exact inventory of the 60 test modules.

This is not a presentational omission. The missing list is the policy that the
new scope manifest, independent verifier, gate runner, and mutation tests are
supposed to implement. Without it, an implementer must rediscover or choose
which 56 modules are current-state. Two implementations can satisfy the same
counts while running different suites. The claimed gate is therefore not
fully specified and cannot yet be independently reviewed.

Required correction:

1. Enumerate all 60 repository-relative test-module paths explicitly.
2. Assign each path to exactly one of the three categories.
3. Provide the exact path-to-dotted-module transformation used by the runner.
4. Require LC_ALL=C lexical ordering and category disjointness.
5. Prohibit ellipses, derived placeholders, or count-only acceptance.
6. Make the scope manifest, verifier, runner, and mutation tests hardcode or
   compare against that same explicit policy without importing one another's
   authority.

Disposition: `S8-CAND-BCP-REV6-B01` and
`S8-CAND-BCP-REV6-TEST-001` are not closed.

### 5.2 `S8-CAND-BCP-REV7-B02` - BLOCKER - The required `CLAUDE.md` adoption is outside the certified scope and sequence

Section 5.9 requires `CLAUDE.md` to be changed so that the new gate becomes the
documented authoritative command. Revision 7 places that change after
independent review and certification. However:

- `CLAUDE.md` is absent from the 45-entry Track 1 inventory;
- it is absent from the successor-ledger plan;
- it is absent from the byte-finalization sequence;
- it is not a baseline-ledger path; and
- the proposal calls itself an interim authority while also stating that it
  does not take effect merely by existing.

The sequence therefore certifies one byte set and then requires a governance
mutation outside that certified byte set before the gate is actually adopted.
That is a post-certification change to the governing contract. It also makes
the stated 45-file and 187-entry totals incomplete if `CLAUDE.md` is part of
this correction cycle.

If `CLAUDE.md` is included in this cycle, the current proposal's own category
rules imply at least 46 Track 1 files: 4 modified and 42 new. Because
`CLAUDE.md` is absent from the 145-entry baseline ledger, it would also add a
successor-ledger path. Subject to a full exact-set recomputation, the apparent
ledger total becomes 188 rather than 187.

Required correction: select exactly one closed architecture.

Option A:

1. Include `CLAUDE.md` in the exact Track 1 inventory.
2. Byte-finalize it before verification and independent review.
3. Include it in the scope manifest and successor ledger.
4. Recompute all category and ledger counts from exact sets.
5. Certify the complete adopted governance state once, without a later
   repository mutation.

Option B:

1. Define a separate, exact governance-adoption cycle with its own inventory,
   verifier, review, ledger treatment, and certification.
2. State that the new gate is not authoritative and Track 1 is not complete
   until that cycle closes.
3. Remove the internally contradictory interim-authority claim.

Disposition: `S8-CAND-BCP-REV6-B02` is not closed.

### 5.3 `S8-CAND-BCP-REV7-ARCH-001` - MAJOR - The S8-RR-003 replay adapter weakens the certified suite

Revision 7 correctly observes that
`verify_s8rr003_normative_ledger.run_verification(repo_root)` can be retargeted
to an isolated root. That proves path isolation for the verifier function. It
does not prove equivalence to the complete certified test module.

The proposed authoritative gate classifies the original
`tests/rcc002/test_s8rr003_normative_ledger.py` as audit-only and does not run
it. The replacement adapter calls `run_verification(tmp)`, asserts selected
result fields, and performs one ledger-count negative control. Static
enumeration shows that the excluded certified module has 41 test methods.

The adapter does not execute or reproduce all of those assertions. In
particular, merely checking the result fields does not reproduce
`test_no_resource_warning_on_successful_run`, which promotes
`ResourceWarning` to an error. It also does not preserve the certified
scope-mutation battery. Section 6.4's claim that both adapters reproduce every
original certified assertion end-to-end is therefore false.

Required correction:

1. Execute the complete, byte-identical S8-RR-003 test module against an
   isolated historical root, or provide an independently reviewable adapter
   that demonstrably reproduces all 41 certified test methods.
2. Preserve the `ResourceWarning` regression assertion.
3. Preserve the complete scope and ledger mutation coverage.
4. Add a negative control proving that omission of any certified test method
   is detected by the gate policy.
5. Correct the proposal's end-to-end-equivalence claim.

Disposition: `S8-CAND-BCP-REV6-ARCH-001` is not closed.

### 5.4 `S8-CAND-BCP-REV7-ARCH-002` - MAJOR - S8-RR-002 replay construction has an exact-count error

Section 6.2 says that, after separately handling the verifier, test module,
Data Pipeline specification, and RM specification, 39 files remain from the
certified S8-RR-002 scope.

Independent set arithmetic gives:

```text
immutable reference inputs = 11
candidate outputs          = 30
category overlap           = 0
scope union                = 41
separately handled paths   = 4
remaining paths            = 37
```

The prose descriptions that follow do not resolve the mismatch. An exact
historical replay must be based on path sets, not an incorrect loop count.

Required correction:

1. Replace 39 with the independently derived exact remainder of 37.
2. Enumerate the 37 remaining paths or define an exact set subtraction from
   the two certified category lists.
3. Require the adapter to prove the union is 41, the categories are disjoint,
   the four special paths are members, and the resulting remainder is 37
   before copying any file.
4. Add mutations for a missing path, an extra path, overlap, and a special
   path absent from the certified union.

Disposition: the S8-RR-002 portion of
`S8-CAND-BCP-REV6-ARCH-001` is not fully closed.

### 5.5 `S8-CAND-BCP-REV7-TEST-001` - MAJOR - Runner semantics lack direct mutation coverage

Section 10 tests the proposed gate-scope verifier, but it does not directly
test the behavior of `scripts/rcc002/run_s8candbcp_gate.py`. A valid scope
verifier does not prove that the runner loads the exact 58 executable modules,
loads each once, never loads either audit-only module, and propagates every
failure.

Required correction: add focused runner tests that prove at least:

1. scope verification completes before any test module is imported;
2. exactly 58 executable modules are loaded, once each;
3. both audit-only modules are never loaded;
4. an import failure produces a non-zero gate result;
5. a test failure or error produces a non-zero gate result;
6. an unknown, duplicate, missing, or reclassified module fails closed; and
7. a fully conforming synthetic partition produces success.

Disposition: `S8-CAND-BCP-REV6-TEST-001` is not closed.

## 6. Finding summary

| Finding | Severity | Result |
|---|---|---|
| `S8-CAND-BCP-REV7-B01` | BLOCKER | Exact 60-module policy is missing |
| `S8-CAND-BCP-REV7-B02` | BLOCKER | Required governance adoption is outside scope and certification |
| `S8-CAND-BCP-REV7-ARCH-001` | MAJOR | S8-RR-003 replay drops certified coverage |
| `S8-CAND-BCP-REV7-ARCH-002` | MAJOR | S8-RR-002 replay remainder is 37, not 39 |
| `S8-CAND-BCP-REV7-TEST-001` | MAJOR | Gate runner itself lacks direct tests |

## 7. Required next submission

A successor proposal must:

1. contain the exact 60-module partition with no placeholders;
2. place the `CLAUDE.md` governance change inside a closed, pre-certification
   scope or define a complete separate adoption cycle;
3. preserve all 41 certified S8-RR-003 test assertions in historical replay;
4. correct the S8-RR-002 remainder to 37 and prove it mechanically;
5. directly mutation-test gate-runner behavior;
6. recompute every file and ledger count from exact path sets; and
7. undergo a new independent scientific and architecture re-review before
   any Track 1 certification or Track 2 implementation repair proceeds.

## 8. Scope of decision

This decision concerns only Revision 7 of the correction proposal. It does not
reject the underlying objective of replacing flat discovery with a classified,
historically replayable gate. It rejects the present proposal because the
binding module policy is absent, the adoption mutation is outside the certified
scope, historical coverage is weakened, and exact construction/test obligations
remain incomplete.

No Track 1 certification, Track 2 repair, S8 implementation authorization,
dataset generation, dataset publication, deployment, or production use is
authorized by this review.

REJECT
