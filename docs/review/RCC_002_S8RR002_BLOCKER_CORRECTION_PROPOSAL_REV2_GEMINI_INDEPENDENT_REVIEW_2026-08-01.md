# RCC-002 S8-RR-002 Blocker Correction Proposal Revision 2 Gemini Independent Review

## Document control

| Field | Value |
|---|---|
| Review date | `2026-08-01` |
| Reviewer | Independent Gemini scientific and architecture reviewer |
| Review environment | Google Antigravity 2.0 |
| Model | Gemini 3.1 Pro (High) |
| Review mode | Strict read-only independent review |
| Repository snapshot | `ebd6862e0af704bc9199eb9330a5501d0c690833` |
| Source archive SHA-256 | `90bf6044c3fb6d3e7b89078a68153d7d08b7c6760d9fe05337783b81e9026ef0` (owner-provided) |
| Target | `RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |

## 1. Review identity and scope

This review independently assessed whether Revision 2 completely resolves
`S8-RR2-B01` and `S8-RR2-B02` without introducing new defects.

The reviewed folder was an immutable archive snapshot. Because it was created
with `git archive`, absence of `.git` metadata was expected. The protected
untracked file `scripts/build_rcc002_spec_bundle.py` was deliberately excluded
and was not part of the review scope.

## 2. Evidence inspected

- `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md`
- `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_2026-07-31.md`
- `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-07-31.md`
- `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md`
- `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_INDEPENDENT_RE_REVIEW_2026-07-31.md`
- all seven current RCC-002 specification documents under
  `docs/specifications/`
- `schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json`
- `requirements.txt`

The prior independent re-review was treated as supporting evidence, not as a
substitute for inspection of the underlying repository artifacts.

## 3. Independent verification results

### 3.1 Dataset Manifest views

The Data Pipeline specification registers exactly six distinct ordered S8
views: Research Features, Backtest Inputs, Paper, Live, Label Research and
Audit. Revision 2 correctly requires this exact ordered registry snapshot and
eliminates the erroneous sixfold repetition of Audit View V2.

### 3.2 Specification profile

The canonical ordered seven-document profile and its current versions were
independently checked. Revision 2 correctly requires the exact current profile
and updates the Run Manifest entry to `RCC-002-RM` version `0.9.0`.

### 3.3 Run Manifest version transition

The proposed transition from Run Manifest `0.8.0` to `0.9.0` is internally
consistent with the normative change and the repository's versioning
precedent.

### 3.4 Dataset Manifest Schema 1.0.1

The proposal introduces Schema `1.0.1` non-destructively and preserves the
certified `1.0.0` schema and its historical fixtures as immutable artifacts.
The proposed `prefixItems` plus `items: false` design can enforce the exact
ordered profiles under JSON Schema Draft 2020-12.

### 3.5 Normative example and fixtures

The proposed Section 24 correction and new positive `1.0.1` fixtures are
structurally and normatively aligned with the restricted six-view and
seven-specification profiles.

### 3.6 Literal specification hashes

The literal SHA-256 values proposed for all six non-self specification entries
were independently checked against the baseline and matched the corresponding
documents.

### 3.7 Run Manifest self-entry

Revision 2 uses an explicitly labelled all-zero digest only for the Run
Manifest self-entry. This convention is distinguishable from a real file
digest and removes the circular self-hash dependency.

### 3.8 Deterministic identity

The proposed ordering, literal non-self hashes, labelled self-entry convention
and post-finalization fixture generation establish an acyclic and deterministic
dataset-identity definition.

### 3.9 Verifier scope

Revision 2 requires the explicit versioned
`RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json` input instead of uncontrolled
directory traversal. Historical artifacts, Dataset Manifest `1.0.0` and the
unrelated stage-manifest same-name field are excluded from current positive
validation where required.

### 3.10 Review dependency

Revision 2 correctly pins `jsonschema==4.26.0` in the review-only dependency
file and requires `Draft202012Validator`. Production `requirements.txt` remains
outside the proposed dependency change.

### 3.11 Schema fingerprint

The `schema_fingerprint_sha256` preimage recipe remains less algorithmically
explicit than the allowlist-hash recipe. Revision 2 safely avoids inventing a
registry-level constant and delegates the value to the defined semantic layer.
This is informational and does not block the correction cycle.

### 3.12 S8 authorization boundary

Revision 2 continues to prohibit S8 production code and dataset publication.
It requires correction, verification, independent review, certification and a
repeated S8 readiness decision before implementation may proceed.

No new cross-document contradiction, hidden scope expansion, invalid version
transition, unverifiable requirement or deterministic-identity defect was
identified.

## 4. Closure of first-review findings

| Finding | Original severity | Closure assessment |
|---|---:|---|
| `S8RR002-PR-SCI-001` | MAJOR | Closed. Run Manifest is correctly increased to `0.9.0`. |
| `S8RR002-PR-SCI-002` | MINOR | Closed. Six literal non-self hashes and one labelled self-entry zero digest are required. |
| `S8RR002-PR-ARCH-001` | MINOR | Closed. Verification uses an explicit versioned JSON scope manifest. |
| Validator dependency | Open | Closed. `jsonschema==4.26.0` is pinned for review use. |
| `S8RR002-PR-ARCH-004` | MINOR | Closed. Future family evolution is distinguished from the exact closed current profile. |
| `S8RR002-PR-ARCH-002` | INFORMATIONAL | Closed / not applicable. The stage-manifest name collision is excluded from scope. |

## 5. New findings

### 5.1 `S8RR002-REV2-GEM-SCI-001` -- INFORMATIONAL

**Location:**
`docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`

The historical Run Manifest document omitted a changelog entry for the
`0.7.2` to `0.8.0` transition. No correction is required for approval of this
proposal. It may be backfilled editorially when `0.9.0` is generated.

### 5.2 `S8RR002-REV2-GEM-SCI-002` -- INFORMATIONAL

**Location:** Proposal Revision 2, Section 4.2.

The `schema_fingerprint_sha256` preimage definition is less algorithmically
explicit than the allowlist-hash recipe. No correction is required for this
proposal because Revision 2 does not invent an unsupported registry constant
and correctly delegates the value.

## 6. Read-only confirmation

No files were modified, created or deleted during the Gemini review. No
production code was authorized or written. Verification was conducted using
read-only inspection and passive diagnostic checks against the snapshot.

## 7. Final decision

Revision 2 fully and deterministically resolves `S8-RR2-B01` and
`S8-RR2-B02`. It defines exact ordered profiles, correct versioning, literal
non-self hashes, a labelled self-entry convention and a closed versioned
verification scope while preserving historical artifacts. All material
findings from the first independent review are closed. The two remaining
observations are informational and do not require correction before the
approved correction cycle.

APPROVE
