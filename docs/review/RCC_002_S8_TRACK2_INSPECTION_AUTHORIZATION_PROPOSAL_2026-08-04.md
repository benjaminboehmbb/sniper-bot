# RCC-002 S8 Track 2 Inspection Authorization Proposal

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-TRACK2-IAP-001` |
| Proposal date | `2026-08-04` |
| Proposal class | Governance authorization request for controlled read-only inspection; no implementation authority |
| Repository branch | `main` |
| Baseline commit | `fd7bda0e8d9dd143aa183874148db56109494908` |
| Controlling proposal | `RCC-002-S8-CAND-BCP-001-REV9` (`docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV9_2026-08-02.md`) |
| Controlling certification | `RCC-002-S8-TRACK1-REV9-CERT-001` (`docs/certification/RCC_002_S8_TRACK1_REV9_IMPLEMENTATION_CERTIFICATION_DECISION_2026-08-03.md`) |
| Status | `PROPOSED FOR ONE INDEPENDENT REVIEW` |
| Authorization | None: no Track 2 inspection, import, execution, mutation, staging, commit, or push |

## 1. Purpose

This proposal requests exactly one grant of authority: a controlled,
read-only inspection of the RCC-002 S8 Track 2 candidate. It does not
request, and does not grant, any authority to repair, mutate, execute,
import, stage, commit, or push any Track 2 artifact.

The proposal exists because Track 2 currently has no inspection authority
of any kind. `RCC-002-S8-CAND-BCP-001-REV9` Section 3.5 and Section 11.2
step 17 defer any Track 2 work until after Track 1 certification, and the
certification decision's Section 6 (Limitations) explicitly excludes
"Track 2 implementation or inspection" from what it authorizes. Track 1
certification is complete, which satisfies the sequencing precondition,
but no separate Track 2 authority has yet been proposed or reviewed. This
document is that proposal.

## 2. Baseline and controlling authority

### 2.1 Baseline commit

`fd7bda0e8d9dd143aa183874148db56109494908`

This is the current `HEAD` of `main` and is identical to `origin/main` at
proposal time. The tracked worktree and index are clean at this baseline.

### 2.2 Controlling proposal

`RCC-002-S8-CAND-BCP-001-REV9`, approved under its Section 12.1 gate by
the independent Gemini re-review recorded in
`docs/review/RCC_002_S8_REV9_GEMINI_PROPOSAL_REREVIEW_2026-08-03.md`
(final verdict `APPROVE`). Section 3.5 of that proposal defines the
`excluded_track2_candidate_modules` category (11 entries) and states that
these files "remain the separate Track 2 implementation candidate and
obtain their own gate only after Track 1 certification and an authorized
Track 2 correction cycle." Section 11.2 step 17 restates the same
sequencing precondition.

### 2.3 Controlling certification

`RCC-002-S8-TRACK1-REV9-CERT-001`, recorded in
`docs/certification/RCC_002_S8_TRACK1_REV9_IMPLEMENTATION_CERTIFICATION_DECISION_2026-08-03.md`,
with decision `CERTIFIED FOR CONTROLLED COMMIT`. Its Section 6
(Limitations) states that the certification does not authorize "Track 2
implementation or inspection" and does not authorize "access to the
protected builder." Its Section 4 confirms the certified architecture
treats the 11 excluded Track 2 candidate modules as excluded, and confirms
that `scripts/build_rcc002_spec_bundle.py` is not certified and remains
outside every authorized scope.

## 3. Why Track 2 may not currently be inspected or repaired

1. No proposal has ever requested inspection authority for Track 2. The
   controlling proposal only defines Track 2 as an excluded category for
   Track 1 discovery purposes; it does not authorize reading, importing,
   executing, or reasoning about Track 2 file contents.
2. The controlling certification affirmatively withholds inspection
   authority for Track 2 as a named limitation, not merely by omission.
3. Track 1's own runner and positive-control B contract require that the
   11 excluded Track 2 paths under `tests/rcc002/s8/` are never statted,
   opened, read, hashed, imported, loaded, or executed by Track 1
   machinery. Ad hoc inspection outside a reviewed proposal would place
   the repository in a state inconsistent with that certified boundary
   and would not itself be bound by any equivalent access-guard contract.
4. Repairing Track 2 before it has been inspected, catalogued, and
   assessed against specification would repeat the exact failure mode the
   governing AFML/backtest-integrity and system-execution policies guard
   against: undocumented, unreviewed change to code that later becomes
   evidence. Track 2 must first be observed under a reviewed, bounded
   authority before any correction proposal can be written, exactly as
   Track 1 was corrected only after `RCC-002-S8-CAND-BCP-001-REV9` fixed
   every path, count, and policy decision in advance.
5. `scripts/build_rcc002_spec_bundle.py` is explicitly outside every
   scope, policy, ledger, package, test, and evidence set under the
   controlling proposal, and is explicitly excluded from the controlling
   certification. Any Track 2 activity, inspection included, must
   preserve that exclusion without exception.

Until this proposal (or a successor) is reviewed and approved, Track 2
remains formally unauthorized for any access, and no correction of Track
2 may be attempted.

## 4. Requested authority

### 4.1 In scope

Exactly one authority is requested: read-only inspection of the following
two paths and their contents, for the sole purpose of producing the
deliverables listed in Section 5:

- `rcc002/s8/`
- `tests/rcc002/s8/`

Read-only inspection means: opening and reading file contents; computing
cryptographic digests of file contents; enumerating file and directory
paths; performing static (non-executing) analysis of source text, such as
parsing import statements or cross-referencing identifiers against
specification documents, without importing or executing the files as
code.

### 4.2 Explicit exclusion of the protected builder

`scripts/build_rcc002_spec_bundle.py` is excluded from this proposal's
scope in every respect. Under the requested authority, and under any
authority that may follow it, this file must not be opened, read, hashed,
imported, executed, or modified. This exclusion is unconditional and does
not expire with a later Track 2 correction proposal unless a future,
separately reviewed proposal explicitly names this file and requests
authority over it.

### 4.3 Explicit prohibitions

The requested authority does not include, and no later step described in
Section 6 may be taken to include by implication:

1. Import of any Track 2 module or file as executable code.
2. Execution of any Track 2 file, test, or script, including via
   `unittest` discovery, direct invocation, or any subprocess.
3. Mutation of any Track 2 file: no edit, rename, move, delete, or
   content change of any kind.
4. Mutation of any file outside `rcc002/s8/` and `tests/rcc002/s8/`.
5. `git add` or any other staging operation against any Track 2 path or
   any other repository path.
6. `git commit` of any kind.
7. `git push` of any kind.
8. Any access, in any form, to `scripts/build_rcc002_spec_bundle.py`.

## 5. Deliverables authorized for later production

Under the read-only inspection authority requested by this proposal (once
approved), the following deliverables may be produced. Each deliverable
is itself a document or ledger artifact, not a code change:

1. Exact `LC_ALL=C`-ordered path list of all files under `rcc002/s8/` and
   `tests/rcc002/s8/`.
2. SHA-256 ledger over the exact byte contents of those files as found.
3. Static dependency analysis of Track 2 source text (import and
   reference graph), performed without importing or executing any Track 2
   file.
4. Mapping of Track 2 files to the relevant RCC-002 specification
   documents under `docs/specifications/`.
5. A findings register describing observed discrepancies, gaps, or risks
   relative to specification, without proposing or performing any fix.
6. An explicit decision, recorded in the findings register or a
   companion document, on whether a separate Track 2 correction proposal
   is required, and if so, what its scope should be.

None of these deliverables may include or imply authorization to modify,
stage, commit, or push any Track 2 file, nor to import or execute any
Track 2 file, nor to access the protected builder.

## 6. Gate order

The following sequence is fixed and non-circular. No step may be taken
before the step preceding it has completed, and no step grants the
authority of a later step:

1. Proposal review: exactly one independent review of this document.
2. Read-only inspection: performed only after Section 1 review approval,
   strictly bounded by Section 4.
3. Findings: production of the Section 5 deliverables from the read-only
   inspection.
4. Separate correction proposal: if the findings register concludes one
   is required, a new, separately filed proposal document describing the
   exact Track 2 correction architecture, following the same pattern as
   `RCC-002-S8-CAND-BCP-001-REV9` did for Track 1.
5. Independent review of that correction proposal.
6. Explicit implementation authority: granted only by an `APPROVE`
   verdict on step 5, and only for the exact architecture reviewed.
7. Implementation review: independent review of the byte-finalized
   implementation candidate produced under step 6.
8. Certification: a separate certification decision, following the same
   pattern as `RCC-002-S8-TRACK1-REV9-CERT-001`.
9. Separate commit and push authorizations: granted only after
   certification, as distinct, explicit steps.

Each step's authority is scoped to that step alone. Approval of the
proposal review (step 1) does not carry forward into approval of the
correction proposal review (step 5); approval of step 5 does not carry
forward into certification (step 8); certification does not itself
authorize commit or push (step 9).

## 7. Authorization boundary

This proposal, by itself, authorizes nothing. It is a request for review.
It does not authorize:

- inspection of `rcc002/s8/` or `tests/rcc002/s8/`;
- any access to `scripts/build_rcc002_spec_bundle.py`;
- import, execution, or mutation of any Track 2 file;
- staging, commit, or push of any repository change.

The only action this proposal's approval enables is the read-only
inspection described in Section 4, strictly bounded by Sections 4.2 and
4.3. Every subsequent step in Section 6 requires its own separate,
explicit authorization and may not be inferred from this proposal or from
approval of an earlier step.

PROPOSED FOR ONE INDEPENDENT REVIEW
