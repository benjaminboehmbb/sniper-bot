# RCC-002 S8-RR-002 Blocker Correction Proposal Revision 2 Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR002-BCP-001-REV2-INDEPENDENT-REVIEW` |
| Review date | `2026-07-31` |
| Reviewer role | Independent scientific and architecture reviewer |
| Repository baseline | `105fdc996097b622b6fba776fbcb2fc1aea8330e` |
| Branch state | `main`; `HEAD` and `origin/main` identical |
| Only untracked file | `scripts/build_rcc002_spec_bundle.py` |
| Baseline verdict | `MATCH` |
| Reviewed proposal | `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md` |
| Superseded proposal | `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_2026-07-31.md` |
| Prior review | `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-07-31.md` |
| Prior verdict | `REJECT` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |
| Review mode | Read-only; no repository writes, subagents, network access or S8 implementation |

## 1. Independence statement

This re-review was performed independently of Revision 2 authorship and the
prior rejection review. Every closure claim was re-derived from primary
repository sources and the repository test suites. No repository file was
modified, staged or committed. No S8 implementation or proposed correction
artifact was generated.

The protected untracked
`scripts/build_rcc002_spec_bundle.py` remained untouched.

## 2. Baseline verification

The verified state was:

```text
branch: main
HEAD: 105fdc996097b622b6fba776fbcb2fc1aea8330e
origin/main: 105fdc996097b622b6fba776fbcb2fc1aea8330e
status: ?? scripts/build_rcc002_spec_bundle.py
```

The five most recent commits were:

```text
105fdc9 Revise RCC-002 S8 manifest correction proposal
d4b4bef Record independent review of S8 manifest proposal
3605d1d Propose RCC-002 S8 manifest blocker corrections
d2a51ed Record RCC-002 S8 readiness blockers
fd0a8aa Implement and certify RCC-002 S8 blocker corrections
```

The two latest commits added only the prior independent review and Proposal
Revision 2. Specifications, schemas, fixtures, the readiness review, the
original proposal and the historical verifier remained unchanged.

## 3. Evidence inspected

- all four S8-RR-002 readiness, proposal and proposal-review documents;
- all seven current RCC-002 specification documents;
- Dataset Manifest Schema `1.0.0` and its positive fixtures;
- Stage Manifest Schema `1.0.0` and its complete-valid fixture;
- `scripts/rcc002/verify_s8bcp001_artifacts.py`;
- production `requirements.txt`;
- root `SHA256SUMS`;
- the repository Python environment package inventory.

## 4. Commands and exact results

| Check | Result |
|---|---|
| Baseline branch, hashes, status and log | Exact expected match |
| Six non-self specification hashes | All values exactly match Revision 2 Section 4.3 |
| Existing RM `0.9.0` references | None; version is unused and collision-free |
| Stale `0.8.1` in Revision 2 | None |
| Production `requirements.txt` | No `jsonschema`; unchanged |
| `import jsonschema` in current environment | `ModuleNotFoundError`; dependency is not silently pre-satisfied |
| Root integrity ledger | All entries pass |
| RCC-002 test suite | 631 tests pass |
| Regression suite | 170 tests pass |
| Compile check | Clean exit |
| Final worktree status | Only the protected builder remains untracked |
| Historical verifier hash | Matches the root ledger and prior reviewed bytes |

The historical verifier was inspected read-only and was not executed
unscoped against the complete working tree.

## 5. Independent reproduction of the blockers

### 5.1 S8-RR2-B01

The authoritative ordered view registry is:

1. `rcc002.view.research-features/1.0.0`;
2. `rcc002.view.backtest-inputs/1.0.0`;
3. `rcc002.view.paper/1.0.0`;
4. `rcc002.view.live/1.0.0`;
5. `rcc002.view.label-research/1.0.0`;
6. `rcc002.view.audit/2.0.0`.

The first four entries use allowlist hash:

```text
2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e
```

The final two entries use:

```text
0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc
```

This contract agrees across the relevant Data Pipeline, Reproducibility and
Label and Forward Return sections.

Reproducibility Section 24 and both positive Dataset Manifest `1.0.0`
fixtures instead contain six identical Audit View V2 entries. Schema `1.0.0`
accepts the array because it requires only at least six generic view
references. The blocker is confirmed.

### 5.2 S8-RR2-B02

The current seven-document profile is:

1. `RCC_002_DATA_PIPELINE_SPECIFICATION/0.8.0`;
2. `RCC-002-DV/0.6.0`;
3. `RCC-002-IS/0.4.3`;
4. `RCC-002-ST/0.4.2`;
5. `RCC-002-RG/0.5.1`;
6. `RCC-002-LF/0.5.0`;
7. `RCC-002-RM/0.8.0`.

Section 24 and both positive Dataset Manifest `1.0.0` fixtures instead use
`RCC-002-SPEC-0` through `RCC-002-SPEC-6`, each at `1.0.0`. Schema `1.0.0`
accepts the generic references. The blocker is confirmed.

Revision 2 correctly preserves the defective `1.0.0` artifacts as frozen
history and defines the prospective corrected `1.0.1` and RM `0.9.0`
contract.

## 6. Closure of prior findings

### S8RR002-PR-SCI-001

| Field | Value |
|---|---|
| Prior severity | `MAJOR` |
| Disposition | `CLOSED` |

Revision 2 changes Reproducibility and Manifest from `0.8.0` to `0.9.0`.
This matches the document's own precedent: a minor increase introduces new
normative content, while patch increases are reserved for mechanical
follow-up without independent normative change. Version `0.9.0` is unused and
does not collide with an existing version. No stale `0.8.1` reference remains
in Revision 2.

### S8RR002-PR-SCI-002

| Field | Value |
|---|---|
| Prior severity | `MINOR` |
| Disposition | `CLOSED` |

Revision 2 contains an explicit literal-hash table for the six non-self
documents and permits exactly one labelled all-zero placeholder for the
`RCC-002-RM/0.9.0` self-entry in Section 24.

All six literal hashes were independently recomputed and matched. Positive
fixtures are separate artifacts generated only after RM `0.9.0` is final, so
they can reference all seven real hashes without an identity cycle.

### S8RR002-PR-ARCH-001

| Field | Value |
|---|---|
| Prior severity | `MINOR` |
| Disposition | `CLOSED` |

Revision 2 requires a committed, versioned verifier scope manifest and
explicitly prohibits unscoped `Path.rglob`, `os.walk`, shell `find` or
equivalent full-tree traversal.

The scope manifest is a path contract, not a self-hashing ledger. Candidate
byte hashes are recorded later in a separate inventory. The design is
portable outside a Git working tree and does not create self-hash
circularity.

### Validator dependency checklist item

| Field | Value |
|---|---|
| Prior disposition | `OPEN` |
| Disposition | `CLOSED` |

Revision 2 pins `jsonschema==4.26.0` in a separate
`requirements-rcc002-review.txt`, requires
`jsonschema.Draft202012Validator`, schema self-validation and exact installed
version enforcement. The dependency is limited to review, test and
certification. Production `requirements.txt` remains unchanged.

The network-isolated reviewer could not independently confirm the exact
package release or Draft 2020-12 conformance. Under the review instructions,
this is a bounded evidence caveat rather than a proposal defect and must be
confirmed during dependency installation.

### S8RR002-PR-ARCH-004

| Field | Value |
|---|---|
| Prior severity | `MINOR` |
| Disposition | `CLOSED` |

Revision 2 clearly states that "at least" governs future specification-family
growth across new profile revisions. Each declared current manifest profile
is exact, ordered and closed. Future growth requires an explicit profile and
schema revision.

### S8RR002-PR-ARCH-002

| Field | Value |
|---|---|
| Prior severity | `INFORMATIONAL` |
| Disposition | `CLOSED / NOT APPLICABLE` |

The Stage Manifest field with the same name is explicitly identified as
semantically distinct and outside the correction scope. Its schema was
independently rechecked and does not exhibit either blocker.

### Historical verifier scope

| Field | Value |
|---|---|
| Prior disposition | `OPEN` |
| Disposition | `CLOSED` |

Revision 2 records that the historical verifier is meaningful only for its
curated correction-bundle input, not for an arbitrary complete repository
working tree. The frozen historical verifier itself remains unchanged.

### S8RR002-PR-ARCH-003

| Field | Value |
|---|---|
| Prior severity | `INFORMATIONAL` |
| Disposition | `NOT APPLICABLE` |

The pre-existing illustrative drift in Reproducibility Section 8.5 remains
explicitly outside the two-blocker correction scope and is not concealed.

All previously open findings are closed.

## 7. New scientific findings

### S8RR002-REV2-SCI-001

| Field | Value |
|---|---|
| Severity | `INFORMATIONAL` |
| Disposition | `NOT APPLICABLE` |

The current RM document lacks a changelog paragraph for its historical
`0.7.2` to `0.8.0` transition even though that transition introduced
substantial normative content.

This pre-existing knowledge-lineage gap does not undermine Revision 2. It
reinforces rather than contradicts the use of a minor version increase for
new normative content.

Required correction: none for Proposal Revision 2. Optionally backfill the
missing `0.8.0` changelog paragraph when RM `0.9.0` is generated, provided the
addition is explicitly editorial and does not expand the correction scope.

### S8RR002-REV2-SCI-002

| Field | Value |
|---|---|
| Severity | `INFORMATIONAL` |
| Disposition | `NOT APPLICABLE` |

Revision 2 says `schema_fingerprint_sha256` remains governed by existing
fingerprint rules. The specifications currently define the field
descriptively but do not contain a complete preimage or computation
algorithm comparable to the fully specified allowlist-hash procedure.

Revision 2 nevertheless makes the correct design choice: it does not invent
a registry-level fingerprint constant and assigns exact reconciliation to
the semantic layer.

Required correction: none for Proposal Revision 2. The eventual RM `0.9.0`
correction record may clarify that the exact fingerprint preimage remains an
already tracked pre-implementation item rather than an already settled rule.

## 8. Architecture and identity findings

No new `BLOCKER`, `CRITICAL`, `MAJOR` or `MINOR` architecture or identity
finding was identified.

The review specifically confirmed:

- all six non-self document IDs, versions, order and hashes;
- strict separation between registry `views` and physical `artifacts`;
- appropriate use of Draft 2020-12 `prefixItems` and `items: false`;
- correct separation of JSON Schema digest-format validation from
  cross-document exact-hash reconciliation;
- explicit and sound `schema_fingerprint_sha256` treatment;
- deterministic distinction between the Section 24 RM self-hash placeholder
  and the seven literal fixture hashes;
- absence of identity cycles;
- review-only validator dependency and unchanged production requirements;
- absence of S8 production code requirements in this correction cycle;
- adequate negative-case and rejection-ledger requirements;
- preservation of historical Schema `1.0.0` bytes;
- no expansion beyond the two readiness blockers;
- consistency among Revision 2 Sections 4 through 8.

## 9. Re-review checklist

| # | Question | Disposition |
|---|---|---|
| 1 | Are `views` and `artifacts` unambiguously separate? | `CLOSED` |
| 2 | Are all six views and their order correct? | `CLOSED` |
| 3 | Is the seven-document profile correct and updated to RM `0.9.0`? | `CLOSED` |
| 4 | Is Dataset Manifest Schema `1.0.1` the correct treatment? | `CLOSED` |
| 5 | Is RM `0.9.0` consistent with the versioning precedent? | `CLOSED` |
| 6 | Are Section 24 hash rules deterministic and self-reference-safe? | `CLOSED` |
| 7 | Are historical `1.0.0` bytes and evidence preserved? | `CLOSED` |
| 8 | Can all declared invalid cases fail closed? | `CLOSED`, contingent on candidate verification |
| 9 | Is `jsonschema==4.26.0` explicit, pinned, local and review-only? | `CLOSED`, with disclosed evidence caveat |
| 10 | Does the versioned scope remove traversal ambiguity? | `CLOSED` |
| 11 | Are S0-S7 science and deterministic values unchanged? | `CLOSED` |
| 12 | Is every identity edge cycle-free? | `CLOSED` |
| 13 | Are the Stage Manifest field and Section 8.5 drift correctly excluded? | `CLOSED` |
| 14 | Is the correction set minimal and complete? | `CLOSED` |

## 10. Residual risks

- The two new informational observations are optional editorial precision
  improvements and do not gate design approval.
- Exact availability and conformance of `jsonschema==4.26.0` must be confirmed
  when the review dependency is installed.
- All proposed candidate artifacts remain intentionally unbuilt. Their
  correctness must be independently reviewed after generation.
- S0-S7 integrity remains reproduced: 631 RCC-002 tests, 170 regression
  tests, compile check and root SHA ledger all pass.

## 11. Final verdict

Every finding left open by the prior rejection review is independently
verified as closed. The two new observations are informational and require no
proposal correction. No new `BLOCKER`, `CRITICAL`, `MAJOR` or `MINOR`
finding was identified. The design is deterministic and executable.

S8 implementation and dataset publication remain prohibited pending
generation and independent review of the corrected candidate artifacts,
certification and an explicit later S8 readiness `READY` verdict.

APPROVE
