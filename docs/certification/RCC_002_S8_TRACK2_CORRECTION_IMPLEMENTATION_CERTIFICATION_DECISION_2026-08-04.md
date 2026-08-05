# RCC-002 S8 Track 2 Correction Implementation Certification Decision - Revision 2

## Document control

| Field | Value |
|---|---|
| Decision ID | `RCC-002-S8-TRACK2-CORRECTION-CERT-DRAFT-002` |
| Decision date | `2026-08-04` |
| Decision class | Exact-byte certification-decision draft |
| Repository | `/home/benja/projects/sniper-bot` |
| Branch | `main` |
| Repository baseline | `a6608a4ad7fa0acbd08ed8bee00211b9d14cff25` |
| Origin main | `a6608a4ad7fa0acbd08ed8bee00211b9d14cff25` |
| Runtime executable | `/home/benja/projects/sniper-bot/.venv/bin/python` |
| Runtime version | `Python 3.14.4` |
| Candidate identity SHA-256 | `7c1fc549064ea3d0bbe3607fb20f6a38aca8beecd35e9050cdfa595f7cadd51f` |
| Authorization decision path | `docs/review/RCC_002_S8_TRACK2_IMPLEMENTATION_AUTHORIZATION_DECISION_2026-08-04.md` |
| Authorization decision SHA-256 | `f712e64c6da1eacf2d006cf2f38248f763996d78262c03fdf20de86a6517261b` |
| Independent candidate-review verdict | `APPROVE` |
| Finding-closure-review verdict | `APPROVE` |
| Draft certification outcome | `CERTIFY SUBJECT TO INDEPENDENT REVIEW OF THIS DECISION` |
| Activation status | `PENDING INDEPENDENT REVIEW` |

ACTIVATION STATUS: PENDING INDEPENDENT REVIEW

## 1. Decision scope

This draft binds the byte-final RCC-002 S8 Track 2 correction candidate at
candidate identity
`7c1fc549064ea3d0bbe3607fb20f6a38aca8beecd35e9050cdfa595f7cadd51f`.

The candidate contains exactly 33 Track 2 files. Exactly eight authorized paths
changed and exactly 25 required-unchanged paths remain byte-identical to the
pre-implementation ledger. Mechanical verification of all 33 current candidate
files against the final SHA-256 ledger returned PASS.

This document is a certification-decision draft. It has no active authority
until one independent reviewer approves these exact decision bytes. Any byte
change to this decision after review requires a new review identity.

## 1.1 Prospective exact 40-file repository scope

This section defines a prospective boundary only. It grants no staging,
commit, or push authority. If this exact decision receives independent
approval and a later separate authorization permits a repository operation,
the complete repository scope is exactly 40 paths:

- 33 byte-final Track 2 candidate paths;
- 6 implementation/evidence paths;
- 1 independently approved certification decision copied byte-identically to
  `docs/certification/RCC_002_S8_TRACK2_CORRECTION_IMPLEMENTATION_CERTIFICATION_DECISION_2026-08-04.md`.

The exact count reconciliation is `40 = 33 + 6 + 1`.

The exact prospective path allowlist is:

1. `rcc002/s8/__init__.py`
2. `rcc002/s8/artifact_class.py`
3. `rcc002/s8/canonical.py`
4. `rcc002/s8/field_registry.py`
5. `rcc002/s8/identity.py`
6. `rcc002/s8/manifests/__init__.py`
7. `rcc002/s8/manifests/common.py`
8. `rcc002/s8/manifests/dataset.py`
9. `rcc002/s8/manifests/reproduction.py`
10. `rcc002/s8/manifests/review.py`
11. `rcc002/s8/manifests/run.py`
12. `rcc002/s8/manifests/source.py`
13. `rcc002/s8/manifests/stage.py`
14. `rcc002/s8/projection.py`
15. `rcc002/s8/publication.py`
16. `rcc002/s8/reason_codes.py`
17. `rcc002/s8/reconciliation.py`
18. `rcc002/s8/specification_profile.py`
19. `rcc002/s8/states.py`
20. `rcc002/s8/validation.py`
21. `rcc002/s8/views.py`
22. `tests/rcc002/s8/__init__.py`
23. `tests/rcc002/s8/test_artifact_class.py`
24. `tests/rcc002/s8/test_canonical.py`
25. `tests/rcc002/s8/test_field_registry.py`
26. `tests/rcc002/s8/test_identity.py`
27. `tests/rcc002/s8/test_manifests.py`
28. `tests/rcc002/s8/test_projection.py`
29. `tests/rcc002/s8/test_publication.py`
30. `tests/rcc002/s8/test_reconciliation.py`
31. `tests/rcc002/s8/test_states.py`
32. `tests/rcc002/s8/test_validation.py`
33. `tests/rcc002/s8/test_views.py`
34. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_AUTHORIZED_SCOPE_V1.json`
35. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_PRE_IMPLEMENTATION_LEDGER_2026-08-04.txt`
36. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_GATE_RESULTS_2026-08-04.txt`
37. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_FINAL_INVENTORY_2026-08-04.txt`
38. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_FINAL_SHA256_LEDGER_2026-08-04.txt`
39. `docs/review/RCC_002_S8_TRACK2_CORRECTION_IMPLEMENTATION_REPORT_2026-08-04.md`
40. `docs/certification/RCC_002_S8_TRACK2_CORRECTION_IMPLEMENTATION_CERTIFICATION_DECISION_2026-08-04.md`

The current byte-identical `rcc002/s8/__init__.py` is one of the 33 candidate
paths. Only its already-bound unchanged bytes are included. The separate IR-003
documentation correction to that path is excluded and remains unauthorized.

No path outside this exact 40-path allowlist may enter a later repository
operation under this decision.

## 2. Lifecycle provenance and baseline reconciliation

The exact lifecycle is a direct parent-child chain:

1. `fd7bda0e8d9dd143aa183874148db56109494908`
   - commit subject: `Certify RCC-002 S8 Track 1 Rev9 implementation`
   - role: Track 1 Rev9 certification commit and lifecycle predecessor.
2. `7ab00e06e91c35e5738698c25fa941fa50516fa0`
   - parent: `fd7bda0e8d9dd143aa183874148db56109494908`
   - commit subject: `Approve RCC-002 S8 Track 2 read-only inspection`
   - role: Track 2 read-only inspection approval and the pre-authorization
     baseline recorded by the proposal, proposal review, and authorization
     decision document.
3. `a6608a4ad7fa0acbd08ed8bee00211b9d14cff25`
   - parent: `7ab00e06e91c35e5738698c25fa941fa50516fa0`
   - commit subject: `Authorize RCC-002 S8 Track 2 correction implementation`
   - role: commit containing the authorization decision, implementation
     baseline, current `HEAD`, and current `origin/main`.

The authorization decision's recorded repository baseline of `7ab00e06...` is
therefore the parent state reviewed before the authorization commit. The
implementation evidence correctly binds `a6608a4...`, the child commit that
contains that authorization decision. These values describe consecutive
lifecycle states, not competing candidate baselines. This section disposes
IR-004 and IR-016 as lifecycle-provenance documentation matters. Neither
finding changes a candidate byte.

## 3. Repository evidence identities

The following repository evidence hashes were mechanically recomputed from the
current files:

- inspection authorization proposal:
  `bd46f00fe65bbeb0dc57d0c88c8ca6a10f2095ef9eeeab0ee69adb6b7b9cfb65`
- inspection authorization correction re-review:
  `f1a259862d7c914162ed346b929826047d4e5266643cff796f4c92e79ba83c2b`
- controlled read-only inspection report:
  `b6df563815d1fc077f585511f9a9e779793e9869acb9ca8830d426d1a23b1ec1`
- correction architecture proposal:
  `c4c93a48dfac32098d30af88b60f389a81c1fb3f6059f1327f8c02dd38218588`
- correction architecture proposal independent review:
  `b26f2e037a7df59aeef405f7874350cfae014ad03082b2d15d85dad22cb35da5`
- implementation authorization decision:
  `f712e64c6da1eacf2d006cf2f38248f763996d78262c03fdf20de86a6517261b`
- original Track 2 inventory:
  `c5925ad40fb6609f60fb98a6afcf482b31463a3e65858e4e1c3e22adb7b9b885`
- original Track 2 SHA-256 ledger:
  `47ef3f5aa9cd573cb9c7188192e2cb5755022c38e0c1d5730c1417be1e014d27`
- original Track 2 inventory summary:
  `47caaf9d74530e89d3e3d1eeda595a4f9a15e1379329dcd43169aa76e2c7311c`
- authorized correction scope:
  `f6f442df4d2f30095b01052601368df0a544c918d9342888bb6caca3cc0cc575`
- pre-implementation ledger:
  `1e4919eee94ebcffb5f14ad68139a15dbe22455ce783ebabaf837cb4042fb280`
- correction gate results:
  `692c53bc1aab715feeccb65fed06c8d8bcaa4cbe8db53f1ecc88de42af7a5707`
- correction implementation report:
  `2075b03a230ad15114e5ff44c279b68bd20bc97c2331354568eca10181aff971`
- final inventory:
  `625a439b67d614b9094003606c87572b7e87b7f53047a148d7f76a7262a6fe6f`
- final SHA-256 ledger:
  `2261006843d1ff5ee13d50370618d7ef02cc9ba5e90b63fdec47a0d2ad011c16`
- Track 1 Rev9 implementation certification decision:
  `e43dd214ca3dceb518c837e2a31c88c2f57d354f4260022c660e3b2d690adfbf`

All known cross-references among the authorization, scope, gate, report,
inventory, ledger, candidate review, and closure evidence reconcile to these
full 64-character values.

## 4. External review and closure evidence identities

The independent candidate review and its package are bound as follows:

- implementation-candidate review package:
  `0ec5254c09d3a9f6ebd962af5d21bbf03c0fb72595decd87ec530bcf69ad8bee`
- independent implementation-candidate review:
  `0e184142cef385b2cfd24d4bb0d0934701162c8650ebf85bd88b01e27dbb346a`
  with verdict `APPROVE`.

The complete finding-closure evidence is bound as follows:

- `BASELINE_STATE.txt`:
  `7607de87a445378b1a25268768b7ee23334569dd14219241cd0bf5fd9ae3e192`
- `IR001_RR002_BASELINE_REPLAY.json`:
  `88da4d559c32e89acb255f8ed3d06c7ca6a085371cc2d477d5fd19c9ec34fdc0`
- `IR001_RR002_BASELINE_REPLAY.log`:
  `800f992e3c2f463d3baa6b3a254c1b7efbc1d8b2250c2eadeca0d415e8c2a06a`
- `IR001_RR003_BASELINE_REPLAY.json`:
  `598c422548eb326f1fcff8b45915e6815e85709117f0f33cf240551dcf5391ec`
- `IR001_RR003_BASELINE_REPLAY.log`:
  `c9895fe96cf4cf7206181ac6df66ebfc52e4730f102f96c50818255a77118864`
- `IR002_IDENTITY_REPRODUCTION.json`:
  `48e0f858044359a6e5b18c508f8f1f01b550e6a5732f5f92c9fd6d0304750bfe`
- corrected finding-closure package:
  `1e363bc03d0d5a56efa00bcba25a15589a9cec1d864a42ab972fca2528c2567d`
- independent finding-closure review:
  `0ac62ec7e8195945ddb83149f0fb61cc3e5c5a312ed1ea9b9f2a80e9fb95c007`
  with verdict `APPROVE`.

The incomplete closure package identified by
`1aae7f715f3d0054cefff295bafaf0974cf65bcb74b007bec581a15a67a99459`
is explicitly superseded and must not be relied upon. The concrete cause was:
the writer attempted `git show HEAD:<path>` for untracked evidence and the
inner failure was not correctly propagated to the outer shell status.

## 5. Exact changed-path-list preimage

Serialization is lexicographically sorted ASCII repository paths with one LF
after every path, including the final path. The exact 246-byte preimage is:

```text
rcc002/s8/manifests/common.py
rcc002/s8/manifests/dataset.py
rcc002/s8/reconciliation.py
rcc002/s8/specification_profile.py
rcc002/s8/views.py
tests/rcc002/s8/test_manifests.py
tests/rcc002/s8/test_reconciliation.py
tests/rcc002/s8/test_views.py
```

SHA-256 of that exact preimage:

`e6391d32bee3c452bacbfe3cbe349c706c33164752fe6cbaf075b7c5b786ca08`

## 6. Exact candidate-identity preimage

Serialization is ASCII JSON with `sort_keys=true`, separators `(',', ':')`,
`ensure_ascii=true`, and no trailing newline. The exact 434-byte preimage is:

```text
{"authorized_scope_sha256":"f6f442df4d2f30095b01052601368df0a544c918d9342888bb6caca3cc0cc575","changed_path_list_sha256":"e6391d32bee3c452bacbfe3cbe349c706c33164752fe6cbaf075b7c5b786ca08","final_inventory_sha256":"625a439b67d614b9094003606c87572b7e87b7f53047a148d7f76a7262a6fe6f","final_ledger_sha256":"2261006843d1ff5ee13d50370618d7ef02cc9ba5e90b63fdec47a0d2ad011c16","repository_baseline":"a6608a4ad7fa0acbd08ed8bee00211b9d14cff25"}
```

SHA-256 of that exact preimage:

`7c1fc549064ea3d0bbe3607fb20f6a38aca8beecd35e9050cdfa595f7cadd51f`

Both hashes were independently reproduced mechanically before this draft was
written.

## 7. Gate evidence and RR diagnostics

The correction evidence records:

- compilation of 8 authorized files: PASS;
- imports of 5 authorized source modules: PASS;
- focused tests: 92 passed;
- complete Track 2 suite: 218 passed;
- current RCC-002 zero-failure boundary: 943 passed;
- exact candidate scope: 8 changed and 25 unchanged paths;
- final 33-file SHA-256 ledger recheck: PASS;
- protected-builder access attempts: 0.

The RR-002 and RR-003 diagnostic results are pre-existing live-tree
divergences of the Track 1 `historical_audit_only_modules`. They are not
certified signatures, are not candidate failures, and are not failure
allowances for any certified gate. The separate Track 1 historical replay
adapter modules are the artifacts recorded as PASS by Track 1 certification.

The diagnostic outcomes are:

- RR-002 original live-tree audit-only module: 28 tests, 3 failures, 0 errors.
  The three failure IDs are:
  - `tests.rcc002.test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_non_self_specification_hashes_are_literal_and_match_disk`
  - `tests.rcc002.test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_rm_specification_profile_exact_seven_order`
  - `tests.rcc002.test_s8rr002_manifest_correction.S8RR002ManifestCorrectionTests.test_verifier_end_to_end_passes`
- RR-003 original live-tree audit-only module: 41 tests, 0 failures, 2 errors.
  The two error IDs are:
  - `tests.rcc002.test_s8rr003_normative_ledger.Case01ValidPositiveControl.test_full_repo_state_passes`
  - `tests.rcc002.test_s8rr003_normative_ledger.ResourceHandlingRegression.test_no_resource_warning_on_successful_run`

The RR-002 observed Data Pipeline operand changed from
`98608db199c525a2a7fcd05f2bff29c73ccad135b02fc0cd10fe180ca03b2e13`
in the earlier REV6 diagnosis to
`c024dc4cc923acfabd43ff6ea810827151e3c09b4041dcfedaba0928139b423a`
at the current baseline. This is attributable to the Track 1 Rev9 advancement
of the tracked Data Pipeline specification between those lifecycle states. It
does not arise from a Track 2 candidate path and does not affect closure.

## 8. Post-closure state binding

The post-closure state artifact is:

`/home/benja/rcc002-s8-track2-finding-closure-2026-08-04/RCC_002_S8_TRACK2_POST_CLOSURE_STATE_2026-08-04.json`

Its mechanically recomputed SHA-256 is:

`b093bec544314566eaddc04015932d74278d5e40e111b4b140e011abadea2068`

The artifact binds all 33 current candidate file hashes, the unchanged final
ledger identity, the unchanged candidate identity, zero candidate-hash
mismatches, and `candidate_state_unchanged=true`. A fresh mechanical comparison
of its 33 path/hash pairs against current disk bytes returned PASS. It also
records that the closure command exported `PYTHONDONTWRITEBYTECODE=1` before
both replay invocations and that the capture performed no repository mutation.

## 9. Finding disposition

- IR-001: CLOSED. The raw RR-002 and RR-003 JSON and log artifacts bind every
  count and test ID and demonstrate candidate independence.
- IR-002: CLOSED. Both exact preimages and both mechanically reproduced hashes
  are bound inline in Sections 5 and 6.
- IR-003: OPEN AND OUTSIDE THE CANDIDATE. The stale documentation statement in
  `rcc002/s8/__init__.py` remains byte-identical and requires separate, narrow
  authorization. This decision neither repairs nor authorizes repair of it.
- IR-004: CLOSED AS LIFECYCLE-PROVENANCE DOCUMENTATION by Section 2. No candidate
  byte changes.
- IR-005 through IR-009: retained as observations under the independent
  candidate review. They do not invalidate the candidate and authorize no
  candidate change.
- IR-010: CLOSED by the exact diagnostic characterization in Section 7. The
  non-passing live-tree results are not called certified signatures.
- IR-011: CLOSED by the six full closure-artifact SHA-256 bindings in Section 4
  and both inline preimages in Sections 5 and 6.
- IR-012: CLOSED by the post-closure state artifact and fresh 33-path mechanical
  recheck bound in Section 8.
- IR-013: DISPOSED as a non-candidate observation by the Track 1 Rev9 Data
  Pipeline advancement explanation in Section 7.
- IR-014: retained as a non-blocking observation. The replay isolation counters
  are corroborative, not load-bearing certification proof. Raw logs,
  architecture exclusions, and zero Track 2 path involvement carry the result.
- IR-015: CLOSED by the explicit supersession identity and concrete failure
  propagation cause in Section 4.
- IR-016: CLOSED AS LIFECYCLE-PROVENANCE DOCUMENTATION together with IR-004 in
  Section 2. No candidate byte changes.

## 9.1 Independent decision-review rejection resolution

The predecessor decision at SHA-256
`1a898b2b6b553b36c2a02e1778570f9d5f3c7bbd39166d97f3963d7452d6e47d`
was rejected by independent review artifact SHA-256
`c1daf52f4cba0b1d9c262f40f2494999489e469b4817fcd47b09c560d63a5916`.

- `RCC2-T2-CDIR-F001` is addressed by the new immutable review package. It
  contains Base64-encoded exact evidence bytes, full SHA-256 values, byte
  counts, all 33 candidate files, all 6 implementation/evidence files,
  lifecycle commit objects, closure evidence, and prior independent reviews.
  A reviewer can reconstruct and hash every object without repository access.
- `RCC2-T2-CDIR-F002` is addressed by Section 1.1 and the complete exclusions
  in Section 11. The prospective scope is exactly `40 = 33 + 6 + 1` and is
  count-reconcilable.

Neither correction changes a Track 2 candidate byte or any repository file.

## 10. Draft certification decision

The evidence supports certification of exactly candidate identity
`7c1fc549064ea3d0bbe3607fb20f6a38aca8beecd35e9050cdfa595f7cadd51f`.

The draft outcome is:

`CERTIFY SUBJECT TO INDEPENDENT REVIEW OF THIS EXACT DECISION`

This outcome is not active. Activation requires an independent review verdict
of `APPROVE` over the exact bytes and SHA-256 of this decision. A `REJECT`
verdict stops the cycle for diagnosis. No authority may be inferred from this
draft while activation is pending.

## 11. Authorization boundary

This draft does not authorize staging, commit, push, deployment, publication,
dataset activity, paper operation, live operation, or production use. It does
not authorize repository mutation, candidate mutation, scope expansion, or
repair of IR-003.

### 11.1 Complete prospective repository exclusions

The following are excluded from the prospective 40-file repository scope:

- `scripts/build_rcc002_spec_bundle.py`;
- every external finding-closure artifact under
  `/home/benja/rcc002-s8-track2-finding-closure-2026-08-04/`;
- every external implementation-candidate independent-review file under
  `/home/benja/rcc002-s8-track2-independent-review-2026-08-04/`;
- every external finding-closure independent-review file under
  `/home/benja/rcc002-s8-track2-finding-closure-independent-review-2026-08-04/`;
- every superseded certification-decision review artifact under
  `/home/benja/rcc002-s8-track2-certification-preparation-2026-08-04/`;
- both REV2 certification-decision review artifacts under
  `/home/benja/rcc002-s8-track2-certification-preparation-2026-08-04-rev2/`;
- the controlling independent rejection-review artifact at
  `/mnt/c/Users/benja/Documents/Codex/2026-08-04/files-mentioned-by-the-user-rcc/outputs/RCC_002_S8_TRACK2_CERTIFICATION_DECISION_INDEPENDENT_REVIEW_2026-08-04.md`;
- every other external certification-decision review package or independent-
  review artifact, including any package used to review this decision;
- IR-003 and any separate correction to `rcc002/s8/__init__.py`; the existing
  unchanged bytes remain included only as one of the 33 candidate paths;
- every dataset, publication artifact, deployment artifact, and production
  artifact;
- every unrelated file and every path not enumerated in Section 1.1.

External evidence may be supplied to an independent reviewer but may not enter
the prospective repository operation. The protected-builder path is excluded
as a path-policy statement only; its file bytes and metadata are not evidence
and are not included in the review package.

Even after an independent `APPROVE` verdict activates this certification
decision, staging, commit, push, deployment, publication, dataset activity,
and production use remain outside this decision and require separate explicit
authority.

PROTECTED_BUILDER_ACCESSED=false
REPOSITORY_MUTATION=false
STAGED_FILES=0
TRACKED_CHANGES=0
ACTIVATION_STATUS=PENDING_INDEPENDENT_REVIEW
NEXT_ACTION=INDEPENDENT_REVIEW_OF_EXACT_DECISION_BYTES
