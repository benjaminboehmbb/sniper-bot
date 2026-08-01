# RCC-002 S8 Implementation Candidate Blocker Correction Proposal

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001` |
| Proposal date | `2026-08-01` |
| Proposal class | Correction planning only (no implementation) |
| Target artifact | The rejected, uncommitted S8 implementation candidate |
| Candidate baseline (repository HEAD at review time) | `5b135e9b9a844193bc5fa817576514f784974614` |
| Candidate baseline branch | `main` |
| Candidate baseline `origin/main` | `5b135e9b9a844193bc5fa817576514f784974614` |
| Expected uncommitted worktree state at proposal time | `?? rcc002/s8/`, `?? scripts/build_rcc002_spec_bundle.py`, `?? tests/rcc002/s8/` |
| Controlling independent review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling review SHA-256 | `cf82b9463b8288e7665df1dd45811c3ddd46dacd754e7825d9c973fbcc60579d` |
| Controlling review decision | `REJECT` |
| Authoritative readiness decision | `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md` |
| Findings addressed | `S8-CAND-B01`, `S8-CAND-B02`, `S8-CAND-B03`, `S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`, `S8-CAND-STATE-001`, `S8-CAND-DOC-001` |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` is a pre-existing untracked protected
file. It was not read, hashed, inspected, opened, executed, imported,
copied, renamed, deleted, modified, staged, or packaged in the preparation
of this proposal. It appears in this document only in this explicit
exclusion statement and in the passive `git status` listing reproduced
above.

## 1. Purpose and scope

This document is a **correction proposal**, not a repair, not a
specification amendment, and not an implementation-readiness decision. It
does not modify any repository file. It defines, for every finding in the
controlling independent review, an exact correction requirement and an
exact verification requirement, organized into two explicit tracks:

1. a **normative correction track** for `S8-CAND-B02` (the View-schema
   fingerprint contract gap), which is a specification-level blocker and
   cannot be closed by implementation choice; and
2. an **implementation repair track** for the remaining eight findings,
   which are implementation-level defects correctable within the existing
   normative contract.

This proposal explicitly distinguishes four separate, non-substitutable
decisions, none of which this document grants:

| Decision | Granted by this proposal? | Who grants it |
|---|---|---|
| Proposal approval (this document's plan is sound) | No -- pending | Project owner / governance review |
| Normative fingerprint contract certification (Track 1 output) | No | Specification owner + Scientific + Architecture certification gates |
| Implementation-repair authorization (Track 2 work may begin) | No | Project owner, gated on item above for `S8-CAND-B02`-dependent work |
| Candidate re-certification / S8 readiness re-confirmation | No | A new independent scientific and architecture re-review (Section 9) |

RR-004's `READY` verdict for S8 implementation **within the authorized
boundary** is not revoked by the controlling review and is not revoked by
this proposal. What remains withheld is certification of *this specific
candidate*, and, independently, any dataset generation, publication, or
deployment.

## 2. Baseline and evidence used

- Repository branch `main`, HEAD and `origin/main` both
  `5b135e9b9a844193bc5fa817576514f784974614`, verified before drafting.
- Worktree state verified to contain exactly the expected three untracked
  paths, with the protected builder excluded from all analysis.
- Controlling review SHA-256 verified to match the value supplied for this
  task before any finding was transcribed into this proposal.
- Specification sections read for grounding: Data Pipeline Specification
  SS6.2 (canonical stage/view schema register), SS6.3 (schema ownership),
  SS6.4 (compatibility rules), SS7.9.2 (canonical allowlist hash
  preimage, the closest existing precedent for a fully specified S8
  identity preimage); Reproducibility and Manifest Specification SS5, SS6
  (hash/canonicalization rules), SS8.7 (canonical stage/view schema
  register), SS13 (artifact inventory), SS14 (build/publication states),
  SS26 (acceptance criteria), SS27 (open implementation decisions).
- The nine findings and independent mutation matrix in the controlling
  review were treated as authoritative and are mapped, not re-derived, in
  Section 4.

No implementation file was executed, imported, or modified to prepare this
proposal. Read-only inspection only.

## 3. Absolute constraint on `S8-CAND-B02`

`S8-CAND-B02` is a **normative-contract blocker**, not an implementation
defect. The current candidate's `schema_fingerprint_sha256` (in
`rcc002/s8/views.py`, `ViewDefinition.schema_fingerprint_sha256`) is
explicitly self-documented in its own docstring as a disclosed,
unregistered placeholder pending specification-owner confirmation. The
controlling review confirms by independent mutation that this placeholder
is not sensitive to allowed producer stages or to the allowlist identity,
so two views with materially different logical contracts can receive the
same fingerprint.

This proposal does **not** invent, infer, or silently select a
replacement preimage. Instead, Section 5 defines exactly which certified
specifications and machine-readable artifacts must be corrected, by the
specification owner, through the normative correction and certification
process already established for this repository's other RCC-002
corrections (the same class of process visible in the S8-RR-002 and
S8-RR-003 correction chains already certified in this repository), before
any implementation code may emit a real `schema_fingerprint_sha256` value.

**Fail-closed sequencing rule:** the implementation repair track
(Section 6) may correct `S8-CAND-B01`, `S8-CAND-B03`,
`S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`,
`S8-CAND-TEST-001`, `S8-CAND-STATE-001`, and `S8-CAND-DOC-001`
independently of `S8-CAND-B02`, because none of those eight findings
depend on the View-schema fingerprint preimage. **No corrected candidate
may be resubmitted for independent review or certification, and no
implementation code may compute or emit a non-placeholder
`schema_fingerprint_sha256`, until the Track 1 normative correction is
certified** (Section 5.6). A candidate that closes the other eight
findings but still emits any `schema_fingerprint_sha256` value -- placeholder
or otherwise -- without a certified preimage contract remains blocked on
`S8-CAND-B02` and is not certifiable.

## 4. Finding-to-correction-to-verification map

| Finding | Severity | Track | Exact correction requirement | Exact verification requirement | Affected file(s) |
|---|---|---|---|---|---|
| `S8-CAND-B01` | BLOCKER | 2 | Replace delegated `sort_keys=True` (Unicode scalar order) with actual RFC 8785 property-name ordering by UTF-16 code unit, applied after NFC preprocessing; reject any post-NFC duplicate property name instead of silently overwriting it. | Versioned external golden fixtures (Section 6.9) including a non-BMP UTF-16-vs-scalar ordering case and an NFC-collision negative case; an independent oracle that does not itself use Python's native string sort; full focused/RCC-002/TD-005 regression re-run. | `rcc002/s8/canonical.py`; `rcc002/s0/source_identity.py:45-71` (shared canonicalization primitive -- see Section 7 boundary note); `tests/rcc002/s8/test_canonical.py`; new fixture file (Section 6.9). |
| `S8-CAND-B02` | BLOCKER | **1 (normative), then 2** | Stop emitting any View-schema fingerprint until the specification owner defines and certifies the complete logical-schema-contract preimage (Section 5). No implementation-chosen formula may be substituted. | Independent literal or fixture evidence for the certified preimage (Section 5.5); a mutation test proving two views with identical schema identity/fields but different allowed producer stages or allowlist identity produce *different* fingerprints once the certified formula is implemented. | `rcc002/s8/views.py:97-119`; `rcc002/s8/manifests/dataset.py` `_views_block()`; plus the normative artifacts listed in Section 5.4. |
| `S8-CAND-B03` | BLOCKER | 2 | Validate the complete `dataset_artifact_set_id` against `^dataset-artifact-set:sha256:[0-9a-f]{64}$` before deriving any filesystem path; require the resolved target to be a direct child of the resolved `publish_root`; verify resolved-parent containment before `os.rename`. | Traversal (`../escaped`), absolute-path, malformed-digest, symlink, and out-of-root-staging mutation tests, each proving rejection *before* any filesystem action; regression re-run. | `rcc002/s8/publication.py:60-89`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-ARCH-001` | MAJOR | 2 | Replace `replace("\\","/").lstrip("./")` with the single canonical portable-path grammar (Section 6.4/Section 4 row below) applied *before* registry matching; remove at most one literal leading `./`, never strip repeatedly, never silently convert backslashes. | Mutation tests for `/SHA256SUMS`, `../SHA256SUMS`, `.\SHA256SUMS` (and equivalents), each proving rejection, not silent classification. | `rcc002/s8/artifact_class.py:80-107`; `tests/rcc002/s8/test_artifact_class.py`. |
| `S8-CAND-ARCH-002` | MAJOR | 2 | Define one strict canonical portable-path grammar (Section 6.4) that rejects all C0 controls, DEL, CR/LF, empty path segments, `.`/`..` components, absolute paths, drive paths, and backslashes; reuse this single grammar at every boundary (classification, identity, ledger, manifest, publication) instead of the current narrower helper. | Grammar tests at the helper boundary, the ledger boundary (`"safe\nforged"` must be rejected, not accepted as one path producing two lines), and the publication boundary; regression re-run. | `rcc002/s8/validation.py:52-66`; `rcc002/s8/publication.py:102-116`; `tests/rcc002/s8/test_validation.py`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-IMPL-001` | MAJOR | 2 | Centralize complete ID-grammar validators (exact regex per ID kind, not `startswith`) and apply them to every referenced ID (`build_id`, `artifact_id`, `dataset_id`, `dataset_artifact_set_id`, `source_snapshot_id`) before use in any preimage; enforce non-negative `row_count` and ordered `(start <= end)` `logical_time_coverage` in `DatasetComponent.as_preimage()` identically to `DataArtifactIdentity`; validate/canonicalize `PublishedDataArtifact.relative_path` with the Section 6.4 grammar before it enters the Dataset Artifact Set preimage or sort. | A combined mutation reproducing the review's case (malformed `build_id`, `row_count=-1`, reversed `logical_time_coverage`) and proving `dataset_id()` now raises; per-ID-kind malformed-grammar negative tests; a `PublishedDataArtifact` unsafe-relative-path negative test. | `rcc002/s8/identity.py:205-263,281-346`; `tests/rcc002/s8/test_identity.py`. |
| `S8-CAND-TEST-001` | MAJOR | 2 | Add a machine-readable, versioned canonicalization fixture file (external to test source) with fixed expected canonical bytes and SHA-256 digests, including the non-BMP-ordering and NFC-collision cases; make the implementation test *and* a genuinely independent oracle (not reusing Python's native string sort) both consume the same external fixture. | The fixture file loads and validates in isolation; both consumers reproduce byte-identical results against it; CI-style re-run of the focused suite shows the previously-passing-but-wrong case now fails until `S8-CAND-B01` is corrected, then passes. | New fixture artifact (Section 6.9); `tests/rcc002/s8/test_canonical.py`. |
| `S8-CAND-STATE-001` | MINOR | 2 | Change the final-path helper to require membership in `PUBLICATION_PATH_STATES` (`published`, `superseded`, `withdrawn`) rather than only excluding `failed`/`quarantined`; keep `require_publishable()` as the separate candidate-to-published transition gate, unchanged. | Mutation tests proving `planned`, `running`, `validating`, and `candidate` are now rejected from the final-path helper, in addition to the already-tested `failed`/`quarantined` rejection. | `rcc002/s8/states.py` (`require_not_diagnostic_only`); `rcc002/s8/publication.py` (`require_not_diagnostic_publication`); `tests/rcc002/s8/test_states.py`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-DOC-001` | INFORMATIONAL | 2 | Correct the next candidate implementation report to state 33 files (21 + 12), not 32. No code change. | Manual count check of the corrected report against `find rcc002/s8 tests/rcc002/s8 -name "*.py" | wc -l` (33), reproduced in the re-review. | Implementation report text only (not a repository source file). |

## 5. Track 1 -- Normative correction track (`S8-CAND-B02`)

### 5.1 Exact affected specifications and sections

| Document | Section | Current state | Required change |
|---|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | SS6.2 "Kanonisches Stufenschemaregister" | States generically that a schema identity includes field names, types, nullability, field order, primary key, sort contract, owner stage, enum/reason-code registries, and compatibility rules, but gives no single combined, hashable preimage structure for a *View* schema fingerprint specifically. | Add an explicit cross-reference from SS6.2 to the new View-schema fingerprint preimage definition (proposed new SS7.9.5, below), or extend SS6.2 itself with the exact preimage JSON shape reused for every logical schema kind (stage and view). |
| `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` | SS7.9 "S8_EXPORT" (new subsection, proposed `SS7.9.5 "Kanonische View-Schema-Fingerprint-Bildung"`, immediately after the existing SS7.9.4 "View-Invarianten und Negativtests") | No such subsection exists. SS7.9.2 defines the allowlist-hash preimage only; SS7.9.3 gives the materialized field lists; SS7.9.4 gives invariants and negative tests. There is no SS7.9.x defining `schema_fingerprint_sha256`. | Add a new subsection defining, in the same style and rigor as SS7.9.2 (an explicit JSON preimage block, RFC 8785/JCS canonicalization, one literal SHA-256 per view, and the field/stage order treated as part of the preimage), the exact `schema_fingerprint_sha256` preimage for all six registered views. |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | SS8.7 "Kanonisches Stufen- und View-Schemaregister" | Requires a manifest to reference, per view, "logischen Schema-Fingerprint" separately from the allowlist hash, but does not itself define the fingerprint's preimage; it delegates schema ownership to the Data Pipeline Specification (SS8.8). | Update SS8.7's prose to point at the new Data Pipeline SS7.9.5 by exact section number once approved; do not duplicate the preimage definition here (preserves the existing SS8.8 ownership split: Data Pipeline owns logical schema/view contracts, RM owns manifest/physical/publication contracts). |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | SS13 "Artefaktinventar" | Defines `schema_fingerprint_sha256` only as "Hash des vollstaendigen logischen Schemavertrags" (hash of the complete logical schema contract), distinct from `field_registry_sha256` and `view_allowlist_sha256`, with no preimage detail. | No structural change required; this section's field definition is already correct and is the authoritative confirmation that the fingerprint must be a *distinct*, *complete* hash, not a subset already covered by the other two hash fields. Retain as-is; reference it from the new SS7.9.5 as the field's normative purpose statement. |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` | SS26.1 item 6, SS27.1 | Require schema/fingerprint/compatibility proofs and Golden Fixtures to be versioned and fixed "vor `Approved for Implementation`"; SS27.1 explicitly lists the S8BCP-001 Rev2 items that are *closed* and may not be reopened -- the View-schema logical fingerprint is **not** among them. | No structural change; this proposal's Track 1 output is precisely the missing item SS27.1 already anticipates ("konkrete Schema-IDs, Versionen, Fingerprints und Kompatibilitaetsregeln", "Golden Fixtures fuer JSON-, Konfigurations-, Tabellen- und ID-Bildung") for the View-schema fingerprint specifically. Confirms this is a new, correctly-scoped normative correction, not a reopening of a closed decision. |

### 5.2 Exact logical-contract dimensions required in the fingerprint preimage

Per Data Pipeline Specification SS6.2 (what a logical schema identity is)
and RM SS8.7 (what a View manifest entry must reference), the certified
preimage must be sensitive to, at minimum, every dimension below. This is
a list of *dimensions the specification owner must decide how to encode*,
not a proposed JSON structure -- Section 3 forbids this proposal from
choosing the encoding:

1. `schema_id` and `schema_version` (already present in the candidate's
   placeholder; retain).
2. Ordered field names (already present in the candidate's placeholder;
   retain -- this is the "Feldreihenfolge fuer kanonische Fingerprints"
   requirement in SS6.2).
3. **Allowed producer stages**, ordered (`allowed_producer_stages`) --
   currently omitted; the independent mutation in the controlling review
   demonstrates two views differing only in this dimension collide.
4. **Field owner stage per field** -- currently omitted; SS8.7 explicitly
   requires "Eigentuemerstufe jedes Feldes" in the manifest's per-view
   reference.
5. **Leakage class per field** -- currently omitted; SS8.7 explicitly
   requires "Leakage-Klasse jedes Feldes".
6. **The View allowlist identity** (`allowlist_sha256`, or the
   equivalent full allowlist preimage it is derived from) -- currently
   omitted; the independent mutation demonstrates two views differing
   only in allowlist identity collide.
7. **Field types and nullability**, per SS6.2's definition of what a
   schema identity is -- not modeled at all in the candidate's row schema
   today at the S8 boundary; the specification owner must decide whether
   this is encoded per-field or inherited by reference to the S0-S7
   stage schemas already registered in SS6.2's table.
8. **Primary key and sort contract** -- SS6.2 requires this for any
   logical schema; for S8 views this is the canonical
   `(market_type, symbol, interval, open_time)` key (SS7.3, extended
   with `provider` for unconsolidated multi-provider data); the
   specification owner must decide whether the key is restated in the
   preimage or referenced by a fixed profile ID.
9. **Applied compatibility profile** -- SS8.7 requires "angewandtes
   Kompatibilitaetsprofil" to be referenced per view; not present in the
   candidate's placeholder at all.
10. **Enum and reason-code registry versions** relevant to fields
    included in the view, per SS6.2's "Enum- und Reason-Code-Register"
    schema-identity dimension.

The specification owner may determine that some of these dimensions are
represented *by reference* (a registry/profile ID plus its own certified
hash) rather than restated in full inside the preimage, provided the
resulting fingerprint is still fully sensitive to a change in any of
them, consistent with the field-registry-digest precedent already
established for `field_registry_sha256`.

### 5.3 Version bump and compatibility consequences

Per Data Pipeline Specification SS6.4 (semantic versioning for logical
stage/view schemas):

- Adding the missing dimensions in Section 5.2 to the fingerprint
  preimage changes the *fingerprint value* for every existing view but
  does not, by itself, change any field's name, type, nullability, or
  semantics. This is consistent with a **Minor** version bump of the
  View-schema register entries under SS6.4's rule ("additive optionale
  Felder ohne Aenderung bestehender Semantik") **only if** the six
  existing `schema_id`/`schema_version` pairs and their certified
  `allowlist_sha256` values (already independently verified correct by
  both RR-004 and the controlling review) are left unchanged; the
  *fingerprint field itself* is new machine-readable evidence, not a
  schema-breaking change.
- If the specification owner instead decides any dimension in
  Section 5.2 requires restating field types/nullability not currently
  captured anywhere in the S0-S7 stage schema register, and that
  restatement surfaces a previously-undetected mismatch with the actual
  S0-S7 implementation, that discovery would independently trigger
  SS6.4's **Major** version rule and must be routed back through
  standard stage-schema correction, not folded into this View-schema
  fingerprint correction.
- `audit` (View Schema `2.0.0`) and `label-research` (View Schema
  `1.0.0`) already differ in `schema_version` for unrelated reasons
  (SS8.7); the new fingerprint contract must not conflate this
  pre-existing version difference with the fingerprint-formula
  correction itself. Both views' fingerprints will change value under the
  new formula; neither view's `schema_id`/`schema_version` changes as a
  result of this correction alone.
- Per SS27.3, any change with effect on "logische Stufen- oder
  View-Schemas" or "Identitaetsvorabbildungen" must re-run the affected
  Scientific, Architecture, and Certification gates. This correction
  affects both, and Section 5.6 below applies SS27.3 directly.

### 5.4 Required machine-readable registry or profile artifact

A new, versioned, machine-readable artifact is required -- analogous in
form and rigor to the existing
`registries/rcc002/release/release_artifact_class_registry.v1.json` and
to the embedded field-ownership registry already certified in Data
Pipeline Specification SS7.9.1 -- that either:

- (a) is embedded directly in the new Data Pipeline SS7.9.5 subsection as
  a normative JSON block (matching the existing style of SS7.9.1 and
  SS7.9.2), analogous in form to `RCC002_S8_FIELD_OWNERSHIP_V1`; or
- (b) is a standalone registry file under `registries/rcc002/` (for
  example `registries/rcc002/release/s8_view_schema_fingerprint_profile.v1.json`),
  referenced by ID and version from the new SS7.9.5 subsection, if the
  specification owner determines the preimage is large or reused enough
  to warrant a separate file (as was done for
  `RCC002_S8_FIELD_OWNERSHIP_V1`-adjacent registries under
  `registries/rcc002/source/` and `registries/rcc002/release/`).

Either form is acceptable to this proposal; the choice between (a) and
(b) is a specification-owner decision, not an implementation decision,
because it affects how `field_registry_sha256`-style mechanical
re-derivation would work for the new artifact. Whichever form is chosen,
the artifact must, at minimum:

- declare an explicit `profile_id`/`registry_id` and version;
- enumerate, per view (in the certified SS8.7 order), every dimension
  from Section 5.2 in a form from which a canonical preimage can be
  mechanically constructed (the same pattern already used successfully
  for the SS7.9.2 allowlist preimage);
- provide the resulting six literal `schema_fingerprint_sha256` values,
  independently computable and checkable, exactly as SS8.7's existing
  table already provides six literal `allowlist_sha256` values.

### 5.5 Required literal or versioned fixture evidence

- Six literal `schema_fingerprint_sha256` values (one per registered
  view, in SS8.7 order), published in the normative document or registry
  artifact itself -- not only inside test code -- mirroring how the six
  `allowlist_sha256` values are already published in SS8.7's table today.
- At least one golden preimage example, fully expanded (not only the
  final hash), for one non-label view and one label view, so an
  independent implementer can reconstruct the canonicalization
  byte-for-byte, mirroring the existing SS7.9.2/SS7.9.3 pattern.
- A negative-evidence case demonstrating that two views differing only
  in `allowed_producer_stages` or only in allowlist identity must
  resolve to different fingerprints, as literal expected values (not
  merely as a textual rule), so the corresponding mutation test
  (Section 4 row for `S8-CAND-B02`) has an external oracle to check
  against, consistent with `S8-CAND-TEST-001`'s requirement that golden
  evidence must not be self-contained in test code.

### 5.6 Review, certification, and readiness gates

Per RM SS27.3, this correction affects logical View schemas and an
identity preimage and therefore must pass, in order, before any
implementation may consume the new formula:

1. **Specification drafting** by the specification owner, producing the
   SS7.9.5 subsection (or equivalent) and the artifact in Section 5.4,
   using the same drafting/review process already used for the
   S8-RR-002 and S8-RR-003 correction chains in this repository
   (proposal to specification owner and reviewers).
2. **Internal review** of the drafted specification text and artifact
   for internal consistency with SS6.2, SS6.4, SS8.7, and SS13 (which
   this proposal has cross-referenced above), matching this repository's
   existing "Internal Review" gate pattern used for prior RM revisions.
3. **Scientific consistency review**, confirming the preimage dimensions
   in Section 5.2 do not silently alter any certified scientific
   transformation, label, or leakage-classification rule -- this
   correction must remain purely an identity/manifest-layer change.
4. **Architecture review**, confirming the new preimage's ownership
   split matches SS8.8 (Data Pipeline owns the logical view contract;
   RM continues to own the manifest field that carries the resulting
   hash), and that the chosen artifact form (Section 5.4, option a or b)
   is structurally consistent with the existing registry/schema
   directory layout.
5. **Independent mechanical verification** of the six literal fingerprint
   values in Section 5.5, by the same style of independent re-derivation
   already used for the six `allowlist_sha256` values (compute from the
   published preimage, compare byte-for-byte to the published literal).
6. **Certification** of the resulting specification revision and
   artifact as a normal RCC-002 correction cycle output (proposal ->
   review -> certification, as already practiced for
   `RCC-002-S8RR002-BCP-001-REV2` and `RCC-002-S8RR003-NLBCP-001-REV2`).
7. Only after step 6 is complete may the implementation repair track
   implement the certified formula in `rcc002/s8/views.py` and
   `rcc002/s8/manifests/dataset.py`, and only after that implementation
   is itself repaired and re-tested may a new candidate be submitted for
   the independent scientific and architecture re-review required by
   Section 9 of this proposal and Section 8 of the controlling review.

### 5.7 Explicit prohibition on implementing an unapproved fingerprint formula

Until Section 5.6 step 6 is complete:

- No implementation file may compute or emit a real (non-placeholder)
  `schema_fingerprint_sha256` value.
- No implementation-owned default, heuristic, or "reasonable guess" for
  the preimage may be substituted, including but not limited to: hashing
  only the dimensions already present in the current placeholder;
  reusing `allowlist_sha256` as a stand-in; or hashing the full
  `ViewDefinition` object's Python representation.
- If implementation work on the other eight findings (Track 2) reaches a
  point where a `schema_fingerprint_sha256` value would otherwise be
  required (for example, to fully populate `_views_block()` in
  `rcc002/s8/manifests/dataset.py`), the corrected candidate must either
  leave that field visibly and explicitly blocked (for example, by
  raising a typed error identifying the open normative dependency) rather
  than emit any value, or the Dataset Manifest builder work itself must
  be deferred until Section 5.6 is complete. This proposal does not
  decide which of those two options the implementer takes; it only
  prohibits emitting a value.

## 6. Track 2 -- Implementation repair track

This track addresses `S8-CAND-B01`, `S8-CAND-B03`, `S8-CAND-ARCH-001`,
`S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`,
`S8-CAND-STATE-001`, and `S8-CAND-DOC-001`. None of these require a
specification change; all are implementation corrections within the
already-certified RR-004 boundary (Sections 9-10 of RR-004).

### 6.1 Actual RFC 8785/JCS UTF-16 property ordering (`S8-CAND-B01`)

- Replace the delegated `json.dumps(..., sort_keys=True)` ordering
  (Unicode scalar order) with property-name ordering by UTF-16 code
  unit, computed after NFC normalization, matching RFC 8785 exactly.
  Because Python's native string comparison is scalar-value order, this
  requires an explicit UTF-16 code-unit comparison key (for example,
  comparing each key's UTF-16BE-encoded byte sequence), not a native
  `sorted()` call on `str` keys.
- This is a shared primitive: `rcc002/s8/canonical.py` currently
  delegates to `rcc002.s0.source_identity.canonical_json_bytes`
  (`rcc002/s0/source_identity.py:45-71`). Section 7 below addresses the
  boundary question of whether the fix belongs in the shared S0 function
  (affecting `source_snapshot_id` computation too) or in a new S8-local
  canonicalizer that no longer delegates.

### 6.2 Rejection of post-NFC duplicate keys (`S8-CAND-B01`)

- The current implementation builds the canonicalized-string dict via a
  Python dict comprehension, which silently keeps the last-written value
  when two distinct pre-NFC keys normalize to the same string. Replace
  this with an explicit collision check that raises a typed
  `CanonicalizationError` (or equivalent) the moment two keys collide
  after NFC normalization, before any value is discarded.

### 6.3 Versioned external canonicalization golden fixtures (`S8-CAND-B01`, `S8-CAND-TEST-001`)

- A new fixture artifact, external to test source code, containing:
  - the exact input object(s), including the non-BMP key-ordering case
    (`U+E000` vs. `U+1F600`) and the NFC-collision case
    (`U+00E9` vs. `U+0065 U+0301`) from the controlling review;
  - the exact expected canonical bytes for each valid case;
  - the exact expected SHA-256 digest for each valid case;
  - an explicit "must reject" marker for the collision case, with the
    expected error condition, not an expected byte output.
- Both the corrected implementation's own test and a genuinely
  independent oracle (Section 6.7) must load and check against this same
  external fixture, so neither can silently re-encode the same mistaken
  assumption twice.

### 6.4 Complete ID grammar validators (`S8-CAND-IMPL-001`)

- Centralize one validator per registered ID kind
  (`source:sha256:[0-9a-f]{64}`, `build:sha256:[0-9a-f]{64}`,
  `artifact:sha256:[0-9a-f]{64}`, `dataset:sha256:[0-9a-f]{64}`,
  `dataset-artifact-set:sha256:[0-9a-f]{64}`,
  `manifest:sha256:[0-9a-f]{64}`, `run:.+`), each checking the *complete*
  grammar, not merely a `startswith` prefix test.
- Apply every validator at every point the corresponding ID kind is
  accepted as a parameter, including `build_id_value` in
  `dataset_id()` and every ID referenced inside
  `DataArtifactIdentity`/`PublishedDataArtifact`/`DatasetComponent`.

### 6.5 Publication-root and staging-root containment (`S8-CAND-B03`)

- Covered in Section 4's `S8-CAND-B03` row; restated here for
  completeness of the implementation track: validate the full
  `dataset_artifact_set_id` grammar, then resolve both the staging path
  and the computed target path with the platform's real-path resolution,
  and require the target's resolved parent to equal the resolved
  `publish_root` before any `os.rename` call.

### 6.6 Symlink, traversal, absolute-path, and malformed-ID rejection (`S8-CAND-B03`, `S8-CAND-ARCH-001`, `S8-CAND-IMPL-001`)

- Every path- or ID-accepting boundary identified in this proposal
  (publication target derivation, artifact classification, ID
  validators, portable-path grammar) must explicitly test and reject:
  a symlinked intermediate or leaf path component, `..` traversal
  segments, absolute paths (POSIX and Windows-drive forms), and
  malformed IDs that pass a prefix check but fail full-grammar
  validation.

### 6.7 One strict canonical portable-path grammar reused everywhere (`S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`)

- Define exactly one portable-path grammar function (a single source of
  truth) that rejects: all C0 control characters and DEL; CR and LF;
  empty path segments; `.` and `..` segments; absolute paths; Windows
  drive-letter paths; and backslashes. This grammar replaces both the
  current narrower `require_portable_relative_path` in
  `rcc002/s8/validation.py` and the ad hoc `replace`/`lstrip` logic in
  `rcc002/s8/artifact_class.py`.
- Reuse this single function at every boundary: artifact classification
  (before registry matching), identity preimages (`relative_path`
  fields), release-ledger generation, manifest field validation, and
  publication path derivation. No boundary may implement its own partial
  variant.

### 6.8 Release-ledger control-character/newline rejection (`S8-CAND-ARCH-002`)

- `build_release_ledger()` must reject (via the Section 6.7 grammar,
  applied before interpolation) any path containing CR, LF, or other
  control characters, so a single file entry cannot expand into more
  than one ledger line and no forged-looking line can be constructed
  from a single artifact's declared path.

### 6.9 Consistent count and logical-time coverage validation (`S8-CAND-IMPL-001`)

- `DatasetComponent.as_preimage()` must enforce the same non-negative
  `row_count` check and the same `coverage_start <= coverage_end` check
  already present for `DataArtifactIdentity.as_preimage()`, so the two
  dataclasses cannot silently diverge in strictness.

### 6.10 Relative-path validation before identity hashing (`S8-CAND-IMPL-001`)

- `PublishedDataArtifact.relative_path` must pass the Section 6.7 grammar
  before it is used for sorting (`dataset_artifact_set_id`'s
  `(relative_path, logical_name)` sort key) or included in the Dataset
  Artifact Set preimage, so an unsafe path cannot enter a hashed identity
  preimage at all.

### 6.11 Final-path membership in `PUBLICATION_PATH_STATES` (`S8-CAND-STATE-001`)

- `require_not_diagnostic_only()` (in `rcc002/s8/states.py`) and
  `require_not_diagnostic_publication()` (in `rcc002/s8/publication.py`)
  must require the state to be a *member* of `PUBLICATION_PATH_STATES`
  (`published`, `superseded`, `withdrawn`), not merely *not* be `failed`
  or `quarantined`. `require_publishable()` (the `candidate`-to-published
  transition gate) is unaffected and must remain a separate function with
  its own separate contract.

### 6.12 All nine adverse mutations from the review, plus necessary boundary tests

Every row of the controlling review's independent mutation matrix
(Section 6 of the controlling review) must become a permanent regression
test in the corrected candidate:

1. Non-BMP JCS key-order pair -> expect UTF-16 JCS order, not Python
   scalar-value order.
2. Two keys colliding after NFC -> expect rejection, not silent value
   loss.
3. View with changed allowed stages and allowlist but identical schema
   identity/fields -> expect a **different** fingerprint (only testable
   once Track 1 is certified and implemented; until then this case
   remains open and must not be closed with a placeholder-based assertion).
4. Publication ID suffix `../escaped` -> expect rejection before any
   filesystem action, not a directory moved outside `publish_root`.
5. Absolute classifier path -> expect rejection, not classification as
   `RELEASE_LEDGER`.
6. Parent-traversal classifier path -> expect rejection, not
   classification as `RELEASE_LEDGER`.
7. Backslash classifier path -> expect rejection, not classification as
   `RELEASE_LEDGER`.
8. Ledger path containing LF -> expect rejection, not an extra ledger
   line.
9. Invalid `build_id` plus negative `row_count` plus reversed
   `logical_time_coverage`, submitted together -> expect rejection, not a
   deterministic Dataset ID.

Necessary additional boundary tests beyond the nine (to close the gap
that let all nine escape 185 passing tests in the first place, per
`S8-CAND-TEST-001`):

- symlinked staging/publication path rejection (adjacent to mutation 4,
  not literally reproduced in the review's table but named in Section 8
  of the controlling review's required repair boundary);
- malformed-digest (right prefix, wrong length/charset) rejection for
  every ID kind in Section 6.4, not only `dataset_artifact_set_id`;
  final-path state-membership tests for every non-`PUBLICATION_PATH_STATES`
  member, not only `failed`/`quarantined` (already partially covered by
  the existing candidate's `test_states.py`; extend rather than replace).

### 6.13 Focused S8, complete RCC-002, and TD-005 regression gates

After every Track 2 correction above (and, separately, after Track 1 is
certified and its formula is implemented), the corrected candidate must
re-pass, in this order:

1. the focused `tests/rcc002/s8` discovery suite, now including every
   test in Section 6.12, with an expected pass count strictly greater
   than the current 185 (new tests added, none removed without
   justification);
2. the complete `tests/rcc002` discovery suite;
3. the complete `tests/regression` (TD-005) discovery suite;
4. a repeated independent adverse-mutation pass, performed by the new
   reviewer in Section 9, outside the candidate tree, leaving no project
   artifact behind, exactly as the controlling review's own methodology
   already demonstrated.

No corrected candidate may claim closure of any finding in Section 4
without all four steps above passing.

## 7. File-level correction inventory

### 7.1 Existing candidate files that may be modified under this proposal

Modification of the following existing, currently-uncommitted candidate
files is contemplated by Track 2 of this proposal. No other repository
file may be modified under this proposal, and this proposal does not
itself modify any of them:

- `rcc002/s8/canonical.py`
- `rcc002/s8/publication.py`
- `rcc002/s8/artifact_class.py`
- `rcc002/s8/validation.py`
- `rcc002/s8/identity.py`
- `rcc002/s8/states.py`
- `rcc002/s8/views.py` (Track 1 dependency only -- the
  `schema_fingerprint_sha256` property itself may not be changed to emit
  a real value until Section 5.6 step 6 is complete; it may be changed
  earlier only to make its blocked status explicit, per Section 5.7)
- `rcc002/s8/manifests/dataset.py` (same Track 1 dependency note as
  above, for `_views_block()`)
- `tests/rcc002/s8/test_canonical.py`
- `tests/rcc002/s8/test_publication.py`
- `tests/rcc002/s8/test_artifact_class.py`
- `tests/rcc002/s8/test_validation.py`
- `tests/rcc002/s8/test_identity.py`
- `tests/rcc002/s8/test_states.py`
- `tests/rcc002/s8/test_views.py` (Track 1 dependency, same note)
- `tests/rcc002/s8/test_manifests.py` (Track 1 dependency, same note)

### 7.2 Boundary note: the shared S0 canonicalization primitive

`rcc002/s8/canonical.py` currently delegates to
`rcc002.s0.source_identity.canonical_json_bytes`
(`rcc002/s0/source_identity.py:45-71`), which is also the function
`source_snapshot_id` computation depends on. This proposal does **not**
decide whether the RFC 8785/JCS ordering fix (Section 6.1) is made:

- (a) inside the shared S0 function, which would also correct
  `source_snapshot_id`'s canonicalization (currently subject to the same
  non-conformance, though outside the S8 candidate's own authorized
  boundary and outside the nine findings in scope here); or
- (b) as a new, S8-local canonicalization function that stops delegating
  to S0 and duplicates a corrected implementation.

Option (a) is preferred on architectural grounds (single source of
truth, matching this repository's existing "reuse, do not duplicate"
convention) but touches `rcc002/s0/source_identity.py`, which is outside
the S8 candidate's file set and outside RR-004's S8 authorization
boundary. **This proposal flags the decision and does not make it.** If
option (a) is selected, the correction cycle for `S8-CAND-B01` must be
re-scoped to include `rcc002/s0/source_identity.py` and must trigger the
re-review already required by SS27.3 for any change to an identity
preimage (`source_snapshot_id` is a certified deterministic identity).
If option (b) is selected, the resulting duplication should itself be
flagged for a future consolidation proposal rather than left permanently
duplicated.

### 7.3 New fixture, registry, scope, or verifier artifacts required

| Artifact | Purpose | Track |
|---|---|---|
| Versioned canonicalization golden fixture (exact path and format is a specification/implementation-owner decision at drafting time; must live outside test source, e.g. under a `tests/fixtures/rcc002/` -style location consistent with existing repository convention) | External, non-self-referential evidence for `S8-CAND-B01`/`S8-CAND-TEST-001`, consumed by both the implementation test and an independent oracle | 2 |
| New Data Pipeline Specification subsection (proposed `SS7.9.5`) defining the View-schema fingerprint preimage | Normative preimage definition | 1 |
| New or extended machine-readable registry/profile artifact for the View-schema fingerprint (Section 5.4, option a or b) | Machine-readable, independently re-derivable source of the six certified fingerprint values | 1 |
| Six literal `schema_fingerprint_sha256` values plus at least one fully expanded golden preimage example | Independent verification evidence for the certified formula | 1 |
| A correction-scope manifest for this proposal's eventual implementation phase (matching this repository's established pattern of a versioned scope JSON for each correction cycle, as already used for S8-RR-002 and S8-RR-003) | Bounds the eventual repair candidate's changed-file set exactly, the same way prior correction cycles in this repository have been bounded | 1 and 2 (may be split into one scope per track, or one combined scope gated as in Section 8) |

This proposal does not create any of the artifacts in this table. It
enumerates what must be created, by whom (specification owner for Track
1 artifacts; implementer for Track 2 artifacts), and in what order
(Section 8).

## 8. Fail-closed sequencing

```text
                    +-----------------------------------------+
                    | Track 1: Normative correction (S8-CAND-B02) |
                    | Sections 5.1-5.6                             |
                    +-----------------------------------------+
                                     |
                     Specification drafting -> Internal review ->
                     Scientific review -> Architecture review ->
                     Independent mechanical verification ->
                     Certification  (Section 5.6, steps 1-6)
                                     |
                                     v
                    [ GATE: Track 1 certified? ]
                     NO  -------------------------------> STOP.
                     |                                    No implementation of the
                     |                                    fingerprint formula. No
                     |                                    real (non-placeholder)
                     |                                    schema_fingerprint_sha256
                     |                                    may be emitted (Section 5.7).
                     YES
                     |
                     v
     +----------------------------------------------------------------+
     | Track 2: Implementation repair (S8-CAND-B01, B03, ARCH-001/002,  |
     | IMPL-001, TEST-001, STATE-001, DOC-001 -- independent of Track 1 |
     | and MAY start in parallel with Track 1 drafting)                |
     | Sections 6.1-6.13                                                |
     +----------------------------------------------------------------+
                     |
                     v
     [ GATE: all eight Track-2 findings closed AND regression re-run    ]
     [        (focused S8 / complete RCC-002 / TD-005) all green?       ]
                     |
                     v
     +----------------------------------------------------------------+
     | View-schema fingerprint formula implementation (only after the  |
     | Track 1 gate above is YES) in rcc002/s8/views.py and             |
     | rcc002/s8/manifests/dataset.py                                   |
     +----------------------------------------------------------------+
                     |
                     v
     [ GATE: both tracks fully closed, all nine findings' verification  ]
     [        requirements (Section 4) satisfied?                      ]
                     |
                     v
          New independent scientific and architecture re-review
          (Section 9) of the corrected candidate
                     |
                     v
          [ Re-review decision: ACCEPT or REJECT ]
                     |
            ACCEPT --+-- REJECT --> back to the relevant track above
                     |
                     v
     Candidate certification (a separate act from this proposal and
     from the re-review itself; performed under this repository's
     standard certification process)
                     |
                     v
     S8 implementation remains bounded by RR-004 Sections 9-10.
     Dataset generation, publication, and deployment remain
     separately unauthorized regardless of certification (Section 9).
```

**The critical fail-closed rule, restated:** the path from "Track 1
drafted" to "fingerprint formula implemented" has exactly one gate, and
that gate requires certification (Section 5.6, step 6), not merely
proposal approval, not merely a passing review, and not merely
implementer confidence that a reasonable formula was chosen. Track 2 work
may proceed in parallel with Track 1 drafting precisely because it does
not depend on this gate; it must not be used to justify skipping the
gate for the one finding that does.

## 9. Preservation, prohibition, and re-review requirements

- **Historical preservation.** No certified historical artifact
  (including but not limited to the certified successor `SHA256SUMS`,
  the historical ledger evidence copy, any certified specification
  document at its currently-certified version and hash, and any
  certified registry or schema file) may be modified as part of either
  track unless an explicit versioned successor is drafted, reviewed, and
  certified through the normal correction-cycle process. This proposal
  does not itself modify, and does not authorize modifying, any such
  artifact.
- **No dataset generation, publication, or deployment.** Neither track
  authorizes generating or publishing a real dataset, nor live or paper
  production deployment. This remains true even after both tracks are
  closed and a corrected candidate is certified; certification of the S8
  *implementation* is a distinct decision from authorization to
  *generate or publish data with it*, which RR-004 also does not grant
  and which this proposal does not grant.
- **No S8 production code from this proposal.** This document contains
  no code, no pseudocode intended for direct inclusion, and no
  copy-pasteable implementation. Section 6's descriptions are correction
  *requirements*, not patches.
- **Mandatory new independent review.** Per the controlling review's own
  Section 8 (item 9) and this proposal's Section 8 gate, a new read-only
  independent scientific and architecture re-review is required after
  both tracks are closed, before any certification decision is made. The
  re-review must independently re-run the full adverse-mutation matrix
  (Section 6.12) outside the candidate tree, exactly as the controlling
  review did.
- **Decision separation, restated.** Proposal approval (this document),
  normative contract certification (Track 1 output), implementation
  repair authorization (Track 2 start), candidate re-certification (the
  Section 9 re-review's outcome), and S8/dataset readiness (RR-004,
  unaffected by this proposal in either direction) are five separate
  decisions. Approving this proposal approves only the *plan* in
  Sections 4 through 8; it does not itself grant any of the other four.

## 10. Restrictions honored while preparing this proposal

- No repository file was created, modified, staged, committed, or
  pushed.
- The existing S8 candidate (`rcc002/s8/`, `tests/rcc002/s8/`) was not
  modified, staged, committed, or pushed.
- No implementation code was run. No test was executed.
- No dependency was installed. No network access was used.
- No dataset was generated or published.
- No S8 production code was created.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified,
  staged, or packaged; it appears only in the document-control table's
  worktree-state row and in this restrictions section.
- All diagnostics performed to prepare this proposal were passive
  (branch/HEAD/origin/status checks, read-only file inspection,
  read-only search, and in-memory reasoning); none created a repository
  artifact.

## 11. Final statement

This proposal is a correction **plan**, addressing all nine findings in
`RCC-002-S8-CAND-CHATGPT-IR-001` with an exact correction and an exact
verification requirement each, organized so that the one
specification-level blocker (`S8-CAND-B02`) cannot be closed by
implementation choice and is explicitly gated behind a normative
correction and certification cycle, while the eight implementation-level
findings may be repaired independently and in parallel. It approves
nothing beyond itself: implementation of any correction described here,
generation or publication of any dataset, and any live or paper
deployment all remain separately unauthorized until the sequencing in
Section 8 and the requirements in Section 9 are satisfied in full.
