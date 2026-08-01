# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 3

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV3` |
| Proposal date | `2026-08-01` |
| Proposal class | Correction planning only (no implementation) |
| Revision | `3` (supersedes Revision 2) |
| Target artifact | The rejected, uncommitted S8 implementation candidate |
| Candidate baseline (repository HEAD at drafting time) | `ee3cfed5e9487ef75c94e9ac06292ec41c896e88` |
| Candidate baseline branch | `main` |
| Candidate baseline `origin/main` | `ee3cfed5e9487ef75c94e9ac06292ec41c896e88` |
| Expected uncommitted worktree state at drafting time | `?? rcc002/s8/`, `?? scripts/build_rcc002_spec_bundle.py`, `?? tests/rcc002/s8/` |
| Superseded proposal (Revision 2) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md` |
| Revision 2 SHA-256 | `8007db898b4d0ce000a82fb3a5ebaf3e6cbd6cd6895ec6ecc2c4c12b2ffe96d4` |
| Controlling re-review (Revision 2 rejection) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV2_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-01.md` |
| Controlling re-review decision | `REJECT` |
| Prior proposal-review (Revision 1 rejection) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling candidate review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Authoritative readiness decision | `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md` |
| Original candidate findings addressed | `S8-CAND-B01`, `S8-CAND-B02`, `S8-CAND-B03`, `S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`, `S8-CAND-STATE-001`, `S8-CAND-DOC-001` |
| Revision 1 review findings addressed | `S8-CAND-BCP-B01`, `S8-CAND-BCP-B02`, `S8-CAND-BCP-ARCH-001`, `S8-CAND-BCP-ARCH-002`, `S8-CAND-BCP-IMPL-001`, `S8-CAND-BCP-DOC-001` |
| Revision 2 re-review findings addressed | `S8-CAND-BCP-REV2-B01`, `S8-CAND-BCP-REV2-B02`, `S8-CAND-BCP-REV2-ARCH-001`, `S8-CAND-BCP-REV2-ARCH-002`, `S8-CAND-BCP-REV2-ARCH-003`, `S8-CAND-BCP-REV2-ARCH-004`, `S8-CAND-BCP-REV2-DOC-001` |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` is a pre-existing untracked protected
file. It was not read, hashed, inspected, opened, executed, imported,
copied, renamed, deleted, modified, staged, or packaged in the preparation
of this proposal. It appears in this document only in this explicit
exclusion statement and in the passive `git status` listing reproduced
above.

## 1. Purpose and scope of Revision 3

This document is a **correction proposal**, not a repair, not a
specification amendment, and not an implementation-readiness decision. It
does not modify, create, delete, or rename any repository file. Revision 3
exists solely to close the seven findings raised by the independent
re-review of Revision 2 (`RCC-002-S8-CAND-BCP-CHATGPT-IR-002`, `REJECT`),
while preserving every Revision 2 decision the re-review confirmed as
sound (Section 7 of the re-review):

1. the shared canonicalization authority `rcc002/canonical.py`, with `S0`
   and `S8` both delegating to it;
2. the prohibition on a permanent S8-local canonicalization duplicate;
3. the exact canonicalization golden-fixture path and identity;
4. the complete run-ID grammar, including UUID version/variant
   constraints and real calendar validation;
5. the centralized portable-path grammar reused at every boundary;
6. the two-track fail-closed separation between normative correction
   (Track 1) and implementation repair (Track 2);
7. the prohibition on emitting a real `schema_fingerprint_sha256` before
   Track 1 certification;
8. the prohibition on dataset generation, publication, or deployment at
   any point in this proposal.

Nothing in this list is weakened by any Revision 3 correction below.
Revision 3's changes are corrective and additive: every count Revision 2
got wrong is now independently reproduced and fixed; every schema or scope
left extensible is now closed; every omitted file is now included; every
temporally impossible dependency is now resequenced; the version-locking
gap is closed; and the omitted normative-ledger successor is now a full
subtrack of Track 1.

## 2. Baseline and evidence used

- Repository branch `main`, HEAD and `origin/main` both
  `ee3cfed5e9487ef75c94e9ac06292ec41c896e88`, verified before drafting.
- Worktree state verified to contain exactly the expected three untracked
  paths, with the protected builder excluded from all analysis.
- The Revision 2 SHA-256 and the controlling re-review's own citations
  were independently recomputed and matched before any finding was
  transcribed into this revision.
- **Independent re-derivation of the disputed fixture counts** (not taken
  from the re-review's prose alone):
  - `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json`:
    parsed and counted **6** `views[].schema_fingerprint_sha256` entries
    (all-zero) plus **1** `artifacts[].schema_fingerprint_sha256` entry
    (all-zero) = **7** placeholders total.
  - `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json`:
    parsed and counted **6** `views[].schema_fingerprint_sha256` entries
    (all-zero) plus **2** `artifacts[].schema_fingerprint_sha256` entries
    (both all-zero, one per each of its two `artifacts[]` entries) =
    **8** placeholders total.
  - `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
    Section 24: read in full, confirming exactly **6** `views[]` and
    **1** `artifacts[]` all-zero `schema_fingerprint_sha256` values
    (**7** total), and confirming the specification's own text
    (transcribed verbatim in Section 6.1 below) already normatively
    distinguishes this from the separate, permanent,
    explicitly-labelled `RCC-002-RM/0.9.0` self-hash zero placeholder in
    the same example's `specification_profile` array.
  - Root `SHA256SUMS`: confirmed **145** entries at drafting time, current
    SHA-256 `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`;
    confirmed present entries for both specification documents, both
    Dataset Manifest schemas (`1.0.0`, `1.0.1`), the complete `1.0.0` and
    `1.0.1` fixture families, `release_artifact_class_registry.v1.json`,
    `RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`, and
    `verify_s8rr003_normative_ledger.py`; confirmed no root-ledger
    self-entry exists.
  - `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/CASE_LEDGER.json`:
    parsed and counted exactly **21** `cases` entries, matching the 21
    negative fixture files on disk.

No implementation file was executed, imported, or modified to prepare
this revision. Read-only inspection only.

## 3. Absolute constraint on the View-schema-fingerprint formula (unchanged)

This proposal does not invent, infer, or silently select the actual
View-schema-fingerprint preimage formula. That choice belongs exclusively
to the independently reviewed and certified Track 1 normative correction
artifact (Section 6). Revision 3 makes the *contract surrounding* that
formula exact (affected documents, exact successor versions, exact
registry container schema, exact fixture sets, exact scopes, and an
acyclic drafting sequence); it still does not choose the formula, and it
still prohibits any implementation from emitting a real
`schema_fingerprint_sha256` before Track 1 certification (Section 6.9).

## 4. Revision 3 closure matrix (Revision 2 re-review findings)

| Finding | Severity | Revision 2 gap | Revision 3 closure section |
|---|---|---|---|
| `S8-CAND-BCP-REV2-B01` | BLOCKER | Missing exact replacement counts (7 in RM SS24, 7 in `1.0.2/minimal-valid.json`, 8 in `1.0.2/complete-valid.json`); no explicit artifact-to-view semantic-equality requirement; RM self-hash rule not distinguished from View-fingerprint placeholders. | Section 6.1 |
| `S8-CAND-BCP-REV2-B02` | BLOCKER | Registry and both scope contracts were exact-labelled but left extensible ("at minimum", open negative-fixture count, unenumerated scope paths). | Section 6.4, Section 6.5, Section 8 |
| `S8-CAND-BCP-REV2-ARCH-001` | MAJOR | Track 2 file boundary (Section 8.3) omitted `rcc002/s8/manifests/run.py` and `rcc002/s8/manifests/stage.py`, which Section 7.3's own application boundary required. | Section 8.2 |
| `S8-CAND-BCP-REV2-ARCH-002` | MAJOR | Declared sequence required certified document hashes before the only certification step. | Section 6.6 |
| `S8-CAND-BCP-REV2-ARCH-003` | MAJOR | Data Pipeline `0.9.0` was called exact while also "subject to later owner confirmation", reopening the version decision. | Section 6.3 |
| `S8-CAND-BCP-REV2-ARCH-004` | MAJOR | No successor treatment for the certified 145-entry root ledger, which two Track 1 edits (Data Pipeline, RM) and thirty-three new Track 1 artifacts make stale. | Section 6.7 |
| `S8-CAND-BCP-REV2-DOC-001` | MINOR | "Future entries" wording on the seven-document specification profile; incorrect historical fixture counts; schema-const-vs-fixture-hash conflation. | Section 6.1, Section 6.3, Section 6.6, Section 9 |

Every row above is closed by an exact decision in the section cited, not
by a restatement of the requirement.

## 5. Finding-to-correction-to-verification map (all nine original candidate findings, carried forward unchanged)

This map is unchanged in substance from Revision 2 Section 5 (which was
unchanged in substance from Revision 1 Section 4); it is not reproduced a
third time in full here to keep this revision focused on the seven new
findings. The nine original findings
(`S8-CAND-B01`, `S8-CAND-B02`, `S8-CAND-B03`, `S8-CAND-ARCH-001`,
`S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`,
`S8-CAND-STATE-001`, `S8-CAND-DOC-001`) remain mapped exactly as in
Revision 2, with two file-boundary corrections carried into Section 8.2 of
this revision: `S8-CAND-IMPL-001`'s and `S8-CAND-TEST-001`'s affected-file
lists now explicitly include `rcc002/s8/manifests/run.py` and
`rcc002/s8/manifests/stage.py`, consistent with the run-ID grammar
(Section 7.3) already applying to both.

## 6. Track 1 - Normative correction track

### 6.1 Exact downstream fingerprint replacement matrix (closes `S8-CAND-BCP-REV2-B01`)

**The RM self-hash rule, transcribed verbatim from the currently certified
specification text (SS24, immediately following the JSON example), is
the controlling precedent for this entire section and must not be
reopened or reinterpreted:**

> Der sha256-Wert des specification_profile-Eintrags RCC-002-RM/0.9.0 ist
> ausschliesslich ein expliziter Nullwert-Platzhalter (64 Nullzeichen) fuer
> die unvermeidliche Selbstreferenz dieses Dokuments auf sich selbst; er
> ist kein realer Dateihash und darf niemals als solcher interpretiert
> werden. Alle sechs uebrigen specification_profile-Eintraege verwenden
> reale, literale SHA-256-Dateihashes der referenzierten Dokumente in
> ihrer jeweils genannten Version. Konkrete Fixtures werden erst nach
> Finalisierung der RCC-002-RM-Bytes erzeugt und MUESSEN fuer alle sieben
> Dokumente, einschliesslich RCC-002-RM, reale SHA-256-Werte enthalten;
> kein anderer specification_profile-Digest in diesem Beispiel oder in
> einer Fixture darf ein Platzhalter sein.

This rule governs exactly one field: the `specification_profile[]` entry
for RM's own document identity, in the SS24 *prose example* only, and it
is **permanent by design** (a document cannot hash its own not-yet-final
bytes). It does not apply to, and must never be confused with, any
`views[].schema_fingerprint_sha256` or `artifacts[].schema_fingerprint_sha256`
value anywhere, because View fingerprints are never self-referential: they
identify a *View schema contract*, not the RM document that describes the
contract's existence. Every View fingerprint placeholder, in every
artifact below, must become a real literal; the RM self-hash placeholder
in the SS24 prose example alone remains a permanent, explicitly labelled
zero, and even that placeholder must be replaced with a real value in
every *generated fixture* (as the transcribed rule already requires).

**Exact replacement counts and locations, independently reproduced, not
merely asserted:**

| Artifact | Placeholder count found | Exact composition | Required Track 1 replacement |
|---|---|---|---|
| RM SS24 prose example, `views[]` | 6 | One per registered view, in SS8.7 order | All 6 replaced with the certified literal for that view |
| RM SS24 prose example, `artifacts[]` | 1 | The example's single `audit-v2` `DATA_ARTIFACT` entry | Replaced with the certified literal for `rcc002.view.audit/2.0.0` |
| RM SS24 prose example, `specification_profile[]` `RCC-002-RM` self-entry | 1 | Permanent, explicitly labelled self-hash placeholder (see quoted rule above) | **Not replaced.** Remains the explicit zero placeholder in the prose example, by design, forever. |
| RM SS24 -- **total View-fingerprint replacements** | -- | -- | **Exactly 7** (6 `views[]` + 1 `artifacts[]`). The specification-profile self-hash placeholder is a separate, non-View, permanently-zero contract and is excluded from this count. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` | 7 (structurally identical to the certified `1.0.1` minimal fixture: 6 `views[]` + 1 `artifacts[]`) | 6 `views[]` entries, 1 `artifacts[]` entry (`audit-v2`) | **Exactly 7** replacements: all 6 `views[].schema_fingerprint_sha256` const-bound to their certified literal (Section 6.4), plus the 1 `artifacts[].schema_fingerprint_sha256` set to the literal for `rcc002.view.audit/2.0.0` (matching its `schema_ref`). This fixture's `specification_profile[]` carries **no** self-hash placeholder: fixtures are generated only after RM's bytes are byte-finalized (Section 6.6) and therefore, per the quoted rule, must carry RM's own real hash too, not the example's placeholder. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` | 8 (structurally identical to the certified `1.0.1` complete fixture: 6 `views[]` + 2 `artifacts[]`) | 6 `views[]` entries, 2 `artifacts[]` entries (`audit-v2`, `label-research-v1`) | **Exactly 8** replacements: all 6 `views[].schema_fingerprint_sha256` const-bound to their certified literal, plus both `artifacts[].schema_fingerprint_sha256` values set to the literal matching each entry's own `schema_ref` (`rcc002.view.audit/2.0.0` for `audit-v2`; `rcc002.view.label-research/1.0.0` for `label-research-v1` -- **these two values are expected to differ from each other**, because the two artifacts reference different views with different certified fingerprints; a fixture that gives them the same literal is itself defective). This fixture's `specification_profile[]` likewise carries RM's real finalized hash, no placeholder. |

**Mandatory semantic-equality rule (mechanically verified, not merely
documented):** for every `artifacts[]` entry, in every Dataset Manifest
`1.0.2` instance (the two certified positive fixtures and any future real
manifest), `schema_fingerprint_sha256` **must** equal the literal
`schema_fingerprint_sha256` recorded in the `views[]` entry -- equivalently,
in the fingerprint registry (Section 6.4) -- whose `schema_ref` equals the
artifact's own `schema_ref`. This is exactly the semantic (not structural)
binding already required by Revision 2 Section 6.1 for `artifacts[]`
(because `artifacts[]` is a variable-length, variable-order array, unlike
the fixed six-entry `views[]` `prefixItems`), now stated as a single
unambiguous equality rule instead of prose. The Track 1 mechanical
verifier (Section 6.8) checks this rule against both certified positive
fixtures as part of certification; it is not optional evidence.

**Historical preservation, restated for this section specifically:** the
`1.0.1` schema and both `1.0.1` positive fixtures (each already carrying
their now-confirmed 7 and 8 all-zero placeholders respectively) remain
byte-for-byte preserved and are never edited to carry real values. Only
the new `1.0.2` schema and new `1.0.2` fixtures carry real literals. RM
`0.9.0`'s own currently certified bytes (the version this Section 6.1
quotes from) are likewise preserved via the repository's existing
git-history-based specification-versioning convention (Section 6.3);
`0.9.0` is superseded by `0.9.1` in the working tree, not deleted from
history.

### 6.2 Exact logical-contract dimensions required in the fingerprint preimage (unchanged, carried forward)

Per Data Pipeline Specification SS6.2 and RM SS8.7, the certified preimage
must be sensitive to, at minimum, the ten dimensions enumerated in
Revision 1 Section 5.2 and Revision 2 Section 6.2 (schema identity,
ordered fields, allowed producer stages, per-field owner stage, per-field
leakage class, allowlist identity, field types/nullability, primary
key/sort contract, applied compatibility profile, and enum/reason-code
registry versions). This proposal continues to prescribe *that* the
formula must be sensitive to each dimension, and, as of Revision 3,
prescribes the exact *container* in which each dimension is recorded
(Section 6.4); it still does not prescribe the exact preimage-hashing
algorithm itself (Section 3).

### 6.3 Exact successor versions, binding and non-reopenable (closes `S8-CAND-BCP-REV2-ARCH-003`, restates `S8-CAND-BCP-ARCH-001` closure)

**These four versions are binding for this correction contract. None of
them is subject to later, unreviewed change. If the specification owner
determines during Track 1 drafting that a different version is required
for any of the four, that determination itself constitutes a change to
this proposal's contract and requires a new proposal revision and a new
independent review before Track 1 artifact generation may proceed with
the different version.** This sentence, not any weaker one, is the entire
content of the version decision; Revision 2's "final version confirmation
remains the specification owner's decision during drafting" sentence,
which the re-review correctly identified as reopening the decision, is
withdrawn and replaced by this paragraph.

| Object | Current | Binding exact successor |
|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.8.0` | **`0.9.0`**, binding |
| `RCC-002-RM` (Reproducibility and Manifest Specification) | `0.9.0` | **`0.9.1`**, binding |
| View-schema-fingerprint registry/profile artifact | Does not exist | **`RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1`, version `1.0.0`**, binding |
| `rcc002.dataset-manifest` schema | `1.0.1` (certified; `1.0.0` separately certified and preserved) | **`1.0.2`**, binding |
| `rcc002.view.*` View schema identities | `1.0.0`/`1.0.0`/`1.0.0`/`1.0.0`/`1.0.0`/`2.0.0` | **Unchanged** -- no View schema receives a version bump from this correction (Revision 2 Section 6.3's rationale is unchanged and is not repeated here) |

**Rationale for each binding version is unchanged from Revision 2
Section 6.3** (Data Pipeline: additive new normative subsection, Minor-tier
document bump by analogy to RM's own most recent comparably-scoped jump;
RM: cross-reference-only edit, smallest defined increment; registry: first
version, no predecessor; Dataset Manifest: closes a validation gap without
retyping any field, Patch-tier successor by direct analogy to the
certified `1.0.0`-to-`1.0.1` precedent). Revision 3 changes only the
*bindingness* of these values, not their derivation.

**Specification-document versioning convention, stated explicitly because
it governs how "preserve certified historical artifacts" applies to
Data Pipeline and RM specifically:** this repository versions
specification *documents* in place, at a stable file path named by
original creation date (for example
`docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`,
whose content has already been revised across multiple certified versions
up to the current `0.9.0` under this one path). The document's internal
version metadata and its "Korrekturvermerk" (correction-note) sections
record its revision history; the superseded byte content is preserved via
git history, not as a second live file. This is the opposite convention
from schemas and fixtures, which this repository versions by path
(`1.0.1.schema.json` coexisting with `1.0.2.schema.json`;
`dataset-manifest/1.0.1/` coexisting with `dataset-manifest/1.0.2/`).
Track 1 therefore **edits** Data Pipeline and RM in place at their
existing paths (Section 6.8's byte-finalization step 3 and step 4), while
**adding** new, separately versioned paths for the registry, schema, and
fixtures (Section 6.8's steps 1 and 6-7). Section 8.2's exact Track 1
inventory reflects this distinction directly: two "modified" specification
paths, thirty-three "new" paths.

**Current seven-document specification profile is closed, with no
"future entries" residue (closes part of `S8-CAND-BCP-REV2-DOC-001`):**
the specification profile consumed by the Dataset Manifest schema's
`specification_profile` `prefixItems` is, and after this correction
remains, **exactly** the seven named documents
(`RCC_002_DATA_PIPELINE_SPECIFICATION`, `RCC-002-DV`, `RCC-002-IS`,
`RCC-002-ST`, `RCC-002-RG`, `RCC-002-LF`, `RCC-002-RM`) at the versions in
the table above (five of the seven -- `RCC-002-DV`, `RCC-002-IS`,
`RCC-002-ST`, `RCC-002-RG`, `RCC-002-LF` -- are entirely unaffected by
this correction and retain their current certified versions and hashes
unchanged: `0.6.0`, `0.4.3`, `0.4.2`, `0.5.1`, `0.5.0` respectively).
Admitting an eighth document, or a different named document, to this
profile is out of scope for this correction and would itself require a
new proposal revision; there is no "future entries" placeholder anywhere
in this profile, in the Dataset Manifest `1.0.2` schema, or in this
proposal.

**Deterministic dependency and ordering consequences, restated as binding
because the versions above are now binding:**

1. The Dataset Manifest `1.0.2` schema's `specification_profile`
   `prefixItems` update exactly two `version` consts (`0.8.0` -> `0.9.0`
   for `RCC_002_DATA_PIPELINE_SPECIFICATION`; `0.9.0` -> `0.9.1` for
   `RCC-002-RM`) and leave the other five untouched.
2. Section 6.6 defines the exact acyclic order in which these binding
   versions' bytes are finalized before the schema and fixtures that
   depend on their resulting hashes are drafted.

### 6.4 Exact closed fingerprint-registry contract (closes part of `S8-CAND-BCP-REV2-B02`)

This section defines the registry's exact structural container: every
top-level key, every `views[]` entry key, every JSON type, every array's
exact order and length, and every object's `additionalProperties` policy.
**There is no "at minimum" language anywhere in this section.** The keys
and types below are the complete, closed set. A future need for an
additional key, a different type, or a different nesting is a change to
this contract and requires a new proposal revision and re-review; it is
never silently permitted.

This section defines the registry's *container schema* only -- what data
is stored and how it is shaped and typed. It does not define the
algorithm that combines the stored `field_contract` entries and other
dimensions into the literal `schema_fingerprint_sha256` value; that
algorithm is Track 1's own normative drafting content (the new Data
Pipeline SS7.9.5), reserved to the specification owner under Section 3.
This distinction is the same one this repository's certified manifest
JSON Schemas already draw between a field's *type* (for example,
`manifest_id` matching `^manifest:sha256:[0-9a-f]{64}$`) and the
*algorithm* that produces its value (RM SS5.9's prose, not the schema).

- **Exact path:** `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json`.
- **Exact top-level key set (7 keys, `additionalProperties: false`):**

  | Key | Type | Exact value or constraint |
  |---|---|---|
  | `registry_id` | string | `const`: `"RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1"` |
  | `registry_version` | string | `const`: `"1.0.0"` |
  | `project` | string | `const`: `"RCC-002"` |
  | `status` | string | `enum`: `["draft", "candidate_for_normative_review", "certified"]`; must equal `"certified"` at the moment Track 1 certification (Section 6.8, step 10) completes |
  | `owning_specification` | object | exact 3-key object (below) |
  | `canonicalization_profile_id` | string | `const`: `"RCC_JSON_CANONICALIZATION_V1"` |
  | `views` | array | exactly 6 items, in the SS8.7 order (`research-features`, `backtest-inputs`, `paper`, `live`, `label-research`, `audit`); each item is the exact `views[]` object shape below |

- **Exact `owning_specification` object (3 keys, `additionalProperties: false`):**
  `id` (string, `const`: `"RCC_002_DATA_PIPELINE_SPECIFICATION"`),
  `version` (string, `const`: `"0.9.0"`),
  `section` (string, `const`: `"7.9.5"`).

- **Exact `views[]` entry object (12 keys, `additionalProperties: false`):**

  | Key | Type | Exact constraint |
  |---|---|---|
  | `view_id` | string | `enum`: `["research-features", "backtest-inputs", "paper", "live", "label-research", "audit"]` |
  | `schema_id` | string | one of the six certified `rcc002.view.*` schema IDs (SS8.7) |
  | `schema_version` | string | the certified version for that `view_id` (`1.0.0` for the four non-label views and `label-research`; `2.0.0` for `audit`) |
  | `schema_ref` | string | `<schema_id>/<schema_version>`, mechanically derived, not independently settable |
  | `allowed_producer_stages` | array of strings | ordered; each item one of the nine `StageId` values; length 7 for the four non-label views and `S0_SOURCE`..`S6_GATES`; length 8 for `label-research`/`audit`, additionally including `S7_LABELS` last |
  | `stage_schema_refs` | array of strings | ordered, one entry per `allowed_producer_stages` item, each of the form `<stage schema_id>/<stage schema_version>` per the already-certified Data Pipeline SS6.2 stage-schema table; this is the exact "by reference" representation of the field-type/nullability/enum-registry dimension (Section 6.2): those dimensions are not restated per field in this registry, they are inherited by reference to the already-certified upstream stage schemas named here |
  | `s7_eligible` | boolean | `false` for the four non-label views; `true` for `label-research` and `audit` |
  | `field_contract` | array of objects | ordered; length exactly 232 for the four non-label views, exactly 534 for `label-research` and `audit`; each item is the exact 3-key object `{"field_name": string, "field_owner_stage": string, "leakage_class": string}` (the identical shape already used by the certified SS7.9.2 allowlist preimage's `fields[]` entries -- reused, not reinvented) |
  | `primary_key_fields` | array of strings | the canonical ordered primary key, `["market_type", "symbol", "interval", "open_time"]`, extended with a leading `"provider"` element only if and when unconsolidated multi-provider data is registered (unchanged from the currently certified single-provider scope: all six `views[]` entries currently carry the four-element form) |
  | `compatibility_profile_id` | string | a registered compatibility-profile identifier; for this correction's initial scope, the fixed value `"RCC002_VIEW_SCHEMA_COMPATIBILITY_V1"` for all six views, denoting the SS6.4 semantic-versioning rule set already normatively in force |
  | `allowlist_sha256` | string | the already-certified literal for that view (`2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e` for the four non-label views; `0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc` for `label-research`/`audit`) -- copied from SS8.7, not recomputed independently by this registry |
  | `schema_fingerprint_sha256` | string | 64-character lowercase hex digest; the new certified literal for that view, produced by the Track 1 drafting act this proposal does not perform (Section 3) |

No key in either object above may be omitted, renamed, retyped, or
supplemented without a new proposal revision. `additionalProperties: false`
is mechanically meaningful for both objects because both key sets above
are complete and closed, resolving the re-review's specific objection that
an open key set makes `additionalProperties: false` non-meaningful.

### 6.5 Exact Dataset Manifest 1.0.2 fixture contract (closes remainder of `S8-CAND-BCP-REV2-B02`)

**Exact positive fixture list (2 files, complete):**

1. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json`
2. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json`

**Exact negative fixture list: exactly 22 files, the 21 cases ported
byte-structurally from `1.0.1` (same rejection class and description,
version fields updated to `1.0.2`) plus exactly one new case,
`wrong-view-fingerprint-hash.json`. No other new case is authorized under
this proposal; a different count or a different new case name requires a
new proposal revision.**

| # | Filename | Rejection class | Origin |
|---|---|---|---|
| 1 | `absolute-path.json` | `absolute_path` | ported from `1.0.1` |
| 2 | `duplicate-specification.json` | `duplicate_specification` | ported from `1.0.1` |
| 3 | `duplicate-view.json` | `duplicate_view` | ported from `1.0.1` |
| 4 | `extra-property.json` | `extra_property` | ported from `1.0.1` |
| 5 | `invalid-id.json` | `invalid_id` | ported from `1.0.1` |
| 6 | `invalid-timestamp.json` | `invalid_timestamp` | ported from `1.0.1` |
| 7 | `missing-required-field.json` | `missing_required_field` | ported from `1.0.1` |
| 8 | `missing-specification.json` | `missing_specification` | ported from `1.0.1` |
| 9 | `missing-view.json` | `missing_view` | ported from `1.0.1` |
| 10 | `path-traversal.json` | `path_traversal` | ported from `1.0.1` |
| 11 | `reordered-specification.json` | `reordered_specification` | ported from `1.0.1` |
| 12 | `reordered-view.json` | `reordered_view` | ported from `1.0.1` |
| 13 | `secret-like-field.json` | `secret_like_field` | ported from `1.0.1` |
| 14 | `secret-like-value.json` | `secret_like_value` | ported from `1.0.1` |
| 15 | `stale-specification-version.json` | `stale_specification_version` | ported from `1.0.1` |
| 16 | `unknown-specification.json` | `unknown_specification` | ported from `1.0.1` |
| 17 | `unknown-view.json` | `unknown_view` | ported from `1.0.1` |
| 18 | `wrong-schema-identity.json` | `wrong_schema_identity` | ported from `1.0.1` |
| 19 | `wrong-schema-version.json` | `wrong_schema_version` | ported from `1.0.1` (description updated: constant is now `1.0.2`) |
| 20 | `wrong-type-nullability.json` | `wrong_type_nullability` | ported from `1.0.1` |
| 21 | `wrong-view-allowlist-hash.json` | `wrong_view_allowlist_hash` | ported from `1.0.1` |
| 22 | `wrong-view-fingerprint-hash.json` | `wrong_view_fingerprint_hash` | **new**: `views[0]` (`research-features`) carries a different registered view's certified `schema_fingerprint_sha256` literal instead of its own, mirroring case 21's structure exactly for the new field |

**Exact `CASE_LEDGER.json` requirement:** one `docs`-adjacent JSON file at
`tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json`,
structurally identical to the certified `1.0.1` ledger (`ledger_schema_version`,
`manifest_type`, `manifest_schema_ref`, `cases`), with
`manifest_schema_ref` updated to `"rcc002.dataset-manifest/1.0.2"` and
`cases` containing **exactly 22 entries**, one per filename in the table
above, each with the `rejection_class` and a `description` (the 21 ported
descriptions may be copied verbatim except where they name the schema
version constant, per case 19 above; the 22nd is new, as specified).

**Byte-for-byte preservation, exact and unconditional:** every file under
`schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json`,
`schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json`,
`tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/` (12 files: 2
positive, 10 negative), and
`tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/` (24 files: 2
positive, 21 negative, 1 case ledger) is preserved byte-for-byte. Track 1
adds new paths under `.../1.0.2/`; it edits no byte of any `1.0.0` or
`1.0.1` artifact.

### 6.6 Acyclic Track 1 byte-finalization and certification sequence (closes `S8-CAND-BCP-REV2-ARCH-002`)

The re-review correctly identified that Revision 2's sequence required
"now-certified" document hashes at a step before certification (the only
certification act) had occurred. Revision 3 resolves this by
distinguishing two different, non-circular concepts that Revision 2
conflated:

- **byte-finalization**: a document's or artifact's content is fixed
  (no further edits), making its SHA-256 a fixed, computable fact; and
- **certification**: the formal, later review-and-approval act that
  declares a *complete, mutually consistent set* of already
  byte-finalized artifacts fit for use.

A byte-finalized document's hash is available to any artifact drafted
after it, regardless of whether formal certification of the whole set has
yet occurred. This is precisely the mechanism the currently certified RM
SS24 text already uses for its own seven-document
`specification_profile` (Section 6.1): six entries carry real hashes of
already byte-finalized documents; only the document's own,
inherently-impossible-before-itself self-hash remains a permanent
placeholder. Revision 3 generalizes this existing, already-certified
pattern instead of inventing a new one.

**Exact sequence (acyclic; each step's inputs are limited to prior steps'
outputs):**

1. Draft the fingerprint contract and registry container (Section 6.4)
   with `status: "draft"`.
2. Independently derive and freeze the six literal `schema_fingerprint_sha256`
   values, per the (not-yet-chosen-by-this-proposal, Section 3) certified
   formula, once that formula itself is drafted as part of step 1's
   content; record them in the registry.
3. Draft and **byte-finalize** Data Pipeline `0.9.0` (new SS7.9.5,
   extended SS6.2 cross-reference) -- "byte-finalize" means the document's
   content is frozen and its SHA-256 is now a fixed, computable fact, not
   that it has been certified.
4. Draft and **byte-finalize** RM `0.9.1` (SS8.7 cross-reference, SS24
   View-fingerprint replacement per Section 6.1), preserving the SS24
   self-hash convention for RM's own `specification_profile` entry in the
   *prose example* unchanged (Section 6.1).
5. Compute the real SHA-256 document hashes of the now byte-finalized
   Data Pipeline `0.9.0` and RM `0.9.1` files. These are **fixture
   document hashes**, consumed by fixture payloads (step 7); they are a
   distinct concept from the **schema ID/version consts** in step 6, which
   are literal strings (`"0.9.0"`, `"0.9.1"`) baked into the JSON Schema
   itself and require no hash at all. Revision 2 conflated these two;
   Revision 3 does not.
6. Draft the Dataset Manifest `1.0.2` schema (Section 6.4's registry is
   independent of this step; this step is the schema in
   Section 6.5/Section 8), using the fixed schema-identity ID/version
   consts (`"0.9.0"`, `"0.9.1"` as literal strings, from Section 6.3 --
   available since Section 6.3's versions are binding from the start of
   drafting, not dependent on step 5) and the six frozen View-fingerprint
   literals from step 2 (available since step 2, not dependent on step 5
   either). This step does **not** require step 5's document hashes at
   all, because the schema only const-binds ID/version strings, never
   document hashes.
7. Generate the `1.0.2` fixtures (Section 6.1, Section 6.5), which **do**
   require step 5's real document hashes, because fixture payloads (unlike
   the schema) carry actual `specification_profile[].sha256` values,
   including RM's own real hash (Section 6.1's rule: fixtures, unlike the
   SS24 prose example, never carry a placeholder for any of the seven
   documents).
8. Run exact-scope verification (Section 6.8, Section 8) over the complete,
   now mutually consistent set from steps 1-7.
9. Perform independent scientific and architecture review of the complete
   set.
10. **Certify** the complete set together as one correction-cycle output,
    updating the registry's `status` to `"certified"`.

Step 6 no longer depends on step 5, resolving the re-review's exact
objection; step 7 depends on step 5, and step 5 depends only on steps 3-4,
which depend only on steps 1-2 -- no step depends on step 8, 9, or 10, so
certification is never a dependency of any artifact-generation step,
eliminating the circularity.

If the project instead intends genuinely separate, sequential
certification acts for Data Pipeline and RM individually before schema
and fixture drafting (rather than one combined certification at step 10),
that is a different process than the one this proposal specifies, and
choosing it requires a new proposal revision that declares the separate
acts explicitly and repeats review and certification after every
downstream hash change -- this proposal does not adopt that alternative.

### 6.7 Certified normative-ledger successor cycle (closes `S8-CAND-BCP-REV2-ARCH-004`)

The certified root `SHA256SUMS` currently contains exactly 145 sorted,
unique entries (current SHA-256
`469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`,
independently confirmed at drafting time, Section 2), mechanically bound
by the certified S8-RR-003 scope and verifier
(`docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`,
`scripts/rcc002/verify_s8rr003_normative_ledger.py`). Track 1 modifies two
already-ledgered paths (Data Pipeline and RM specification documents,
Section 6.3) and adds thirty-three new normative paths (Section 8.2).
Neither the ledger nor its scope/verifier is self-updating; both require
an explicit successor cycle, following exactly the precedent this
repository already established when S8-RR-003 itself superseded a
110-entry historical ledger with the current 145-entry one.

**Historical evidence copy:**

- Exact path:
  `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`.
- Exact content requirement: a byte-for-byte copy of the current root
  `SHA256SUMS` as it exists at the moment Track 1 ledger drafting begins.
- Exact hash-derivation requirement: the copy's own SHA-256 is **not**
  asserted by this proposal as a fixed literal (this proposal is
  read-only planning, not Track 1 execution); it **must** be computed
  mechanically, at Track 1 drafting time, as the SHA-256 of the then-current
  root `SHA256SUMS` bytes, and recorded as the expected value in the
  ledger scope manifest below. At the moment this Revision 3 proposal was
  drafted, that value would have been
  `469236e8459a9ad86d3434a67a81f037a699e076c6a8af8b0a887ecb60a30302`
  (Section 2); Track 1 execution must independently recompute it against
  whatever the root ledger's actual bytes are when drafting begins, not
  copy this proposal's informational citation.

**Exact successor-set arithmetic:**

```text
baseline entries                                 = 145
replaced (same path, new hash; Data Pipeline
  and RM specification documents, Section 6.3)   =   2  (count-neutral: path count unchanged)
added (new Track 1 paths, Section 8.2)           =  33
removed                                          =   0
-----------------------------------------------------
successor entries = 145 + 33 - 0                 = 178
```

The 2 replaced entries do not change the total count (same path, updated
hash); they are listed separately from the 33 additions, which are the
exact new-path list in Section 8.2's Track 1 inventory (registry, schema,
fixtures, case ledger, Track 1 scope manifest and verifier, and the four
ledger-subtrack artifacts themselves, all self-inventoried per Section 8).

**Exact successor ledger paths:** the successor `SHA256SUMS` contains
exactly the union of the current 145 entries and the 33 new Track 1 paths
enumerated in Section 8.2, each entry's path in strict `LC_ALL=C` lexical
order, exactly as the current 145-entry ledger and its S8-RR-003
predecessor already enforce. **Root-ledger self-entry exclusion is
preserved**: `SHA256SUMS` never lists itself, exactly as today.
**Protected-builder exclusion is preserved**:
`scripts/build_rcc002_spec_bundle.py` is never listed, is never read,
hashed, or otherwise accessed by any part of this ledger successor cycle,
and appears in this section only in this exclusion statement.

**Required ledger scope manifest, verifier, and tests:**

- Scope manifest:
  `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json`,
  structured exactly like the certified `RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`
  precedent: `scope_schema_version`, `scope_id`
  (`"RCC002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1"`), `correction_id`
  (`"RCC-002-S8CANDBCP-REV2-LEDGER"`), the historical ledger's expected
  SHA-256 (derived per above, not hardcoded by this proposal), the exact
  145-entry baseline path set, the exact 33-entry added-path set
  (Section 8.2), the exact 2-entry replaced-path set, and the exact
  178-entry successor union, each independently re-derivable and
  cross-checked for consistency (baseline union new minus removed equals
  successor).
- Verifier: `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`,
  following the certified `verify_s8rr003_normative_ledger.py` pattern
  exactly: independent hardcoded expected path lists (not read from the
  scope manifest as ground truth), rejection of missing, extra,
  duplicated, reordered, unsafe, stale, self-referential, or undeclared
  entries, and a single deterministic JSON result object on stdout.
- Focused mutation tests: `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py`,
  covering at minimum: a missing successor entry; an extra undeclared
  entry; a duplicate entry; a reordered entry; an unsafe (absolute or
  traversal) path; a stale digest for one of the two replaced
  specification paths; and a root-ledger self-entry injection.
- Independent re-review and certification: the ledger successor is
  reviewed and certified together with the rest of the Track 1 set at
  Section 6.6 step 9-10, not as a separate, earlier, or later act.

**Scope boundary, stated explicitly:** this ledger successor cycle covers
Track 1 (normative) artifacts only, per the re-review's own framing ("the
successor ledger must cover all changed and new **Track 1** normative
artifacts"). Track 2 files remain part of the uncommitted, uncertified S8
candidate and are out of scope for this ledger cycle; Track 2's own scope
manifest and verifier (Section 8.3) are governance evidence about
authorized file boundaries, not ledgered release artifacts, and are not
added to `SHA256SUMS` by this proposal.

### 6.8 Review, certification, and readiness gates (updated to reference the acyclic sequence)

1. Steps 1-7 of Section 6.6 (drafting and byte-finalization).
2. Internal review of the drafted text and artifacts, including the
   ledger successor (Section 6.7), for internal consistency with SS6.2,
   SS6.4, SS8.7, and SS13.
3. Scientific consistency review, confirming the preimage dimensions do
   not silently alter any certified scientific transformation, label, or
   leakage-classification rule.
4. Architecture review, confirming the ownership split (SS8.8), the
   Section 6.4 registry container schema, and the Section 6.7 ledger
   successor were followed exactly as specified.
5. Independent mechanical verification of the six literal fingerprints,
   the two golden preimages (Section 6.2's carried-forward "exactly two"
   requirement), the Section 6.1 semantic-equality rule against both
   positive `1.0.2` fixtures, and the Section 6.7 ledger successor
   arithmetic.
6. Step 8 of Section 6.6 (exact-scope verification over the complete set,
   including the ledger scope/verifier).
7. Step 9 of Section 6.6 (independent scientific and architecture review
   of the complete set).
8. Step 10 of Section 6.6 (certification of the complete set together,
   including the ledger successor).
9. Only after step 8 above is complete may the implementation repair
   track implement the certified formula, and only after that
   implementation is itself repaired and re-tested may a new candidate be
   submitted for the independent re-review required by Section 10.

### 6.9 Explicit prohibition on implementing an unapproved fingerprint formula (unchanged)

Unchanged from Revision 1 Section 5.7 and Revision 2 Section 6.7: until
Section 6.8 step 8 is complete, no implementation file may compute or
emit a real `schema_fingerprint_sha256` value; no implementation-owned
default, heuristic, or "reasonable guess" may be substituted; a blocked
Track 2 candidate must leave the field visibly and explicitly blocked
rather than emit any value.

## 7. Track 2 - Implementation repair track (unchanged in substance; file-boundary fix in Section 8.2)

Sections 7.1 (shared canonicalization authority), 7.2 (canonicalization
golden fixture), 7.3 (run-ID grammar), 7.4 (portable-path grammar), and
7.5 (regression gates) of this track are **unchanged from Revision 2
Sections 7.1-7.5**, which the re-review did not fault on their own
technical content (Section 7 of the re-review lists the run-ID grammar,
UUID constraints, calendar validation, and centralized portable-path
grammar among the confirmed strengths). The only Track 2 correction in
Revision 3 is the file-boundary fix, applied in Section 8.2: the run-ID
validator's application boundary (Revision 2 Section 7.3) already named
`rcc002/s8/manifests/run.py` and `rcc002/s8/manifests/stage.py` alongside
`rcc002/s8/identity.py` and `rcc002/s8/manifests/dataset.py`; Section 8.2
below now includes both previously omitted files in the exact Track 2
inventory, so the exact scope and the application boundary agree.

All nine adverse mutations, the Revision 1 and Revision 2 boundary-test
additions, and the mutation battery in Revision 2 Section 7.6 remain
required unchanged, extended by: run-ID grammar positive/negative test
methods added to the existing `TestRunManifest` and `TestStageManifest`
classes already present in `tests/rcc002/s8/test_manifests.py` (no new
test file is required for this specific gap, because that file was
already in the Track 2 scope and already provides per-manifest-type test
classes; only the two *implementation* files it tests were missing from
the file boundary).

## 8. Exact scope, path inventories, and consolidated matrix

This section closes the exhaustive-inventory portion of
`S8-CAND-BCP-REV2-B02` and all of `S8-CAND-BCP-REV2-ARCH-001`.

### 8.1 Scope-manifest topology (unchanged decision from Revision 2, now filled with exact inventories)

Two separate, versioned scope manifests, one per track, each with its own
mechanical verifier, each self-inventoried (listing its own manifest and
verifier paths within its own category), unchanged in principle from
Revision 2 Section 8.1. Revision 3 adds the ledger scope/verifier
(Section 6.7) as a third Track-1-family artifact pair, kept as its own
scope manifest rather than merged into the Track 1 normative scope
manifest, because the ledger's independent hardcoded expected lists must
remain checkable without re-parsing the (larger, content-focused) Track 1
normative scope manifest -- the same separation-of-concerns argument
Revision 2 already used to justify two manifests instead of one.

### 8.2 Exact Track 1 inventory (normative track: fingerprint contract, Dataset Manifest successor, normative-ledger successor)

**Exact total: 36 files (3 modified, 33 new). Category and per-category
counts below; the combined list is in strict lexical (`LC_ALL=C`) order.**

**Modified (3):**

1. `SHA256SUMS` (root ledger successor, Section 6.7)
2. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` (`0.8.0` -> `0.9.0`)
3. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` (`0.9.0` -> `0.9.1`)

**New -- fingerprint registry (1):**

4. `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json`

**New -- Dataset Manifest 1.0.2 schema (1):**

5. `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json`

**New -- Dataset Manifest 1.0.2 fixtures (25: 2 positive, 22 negative, 1 case ledger):**

6. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json`
7. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json`
8. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json`
9. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/absolute-path.json`
10. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-specification.json`
11. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-view.json`
12. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/extra-property.json`
13. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-id.json`
14. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-timestamp.json`
15. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-required-field.json`
16. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-specification.json`
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-view.json`
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/path-traversal.json`
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-specification.json`
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-view.json`
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-field.json`
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-value.json`
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/stale-specification-version.json`
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-specification.json`
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-view.json`
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-identity.json`
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-version.json`
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-type-nullability.json`
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-allowlist-hash.json`
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json`

**New -- Track 1 normative scope manifest and verifier, self-inventoried (2):**

31. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`
32. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`

**New -- normative-ledger successor subtrack, self-inventoried (4):**

33. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt`
34. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json`
35. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`
36. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py`

**The Track 1 mechanical verifier's own hardcoded expected-inventory
declaration must equal this Section 8.2 list exactly: 3 modified paths, 33
new paths, 36 total, matching the Section 6.7 arithmetic's `added = 33`
term precisely (the fingerprint-family 29 new artifacts [items 4-32] plus
the 4 ledger-subtrack new artifacts [items 33-36] = 33).**

### 8.3 Exact Track 2 inventory (implementation track)

**Exact total: 23 files (20 modified, 3 new), reconciling the omission the
re-review identified. Combined list in strict lexical order.**

**New (3):**

1. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json`
2. `rcc002/canonical.py`
3. `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py`

**Modified -- shared/S0 (2):**

4. `rcc002/s0/source_identity.py`
5. `tests/rcc002/s0/test_source_identity.py`

**Modified -- S8 implementation, including the two previously omitted
manifest builders (10):**

6. `rcc002/s8/artifact_class.py`
7. `rcc002/s8/canonical.py`
8. `rcc002/s8/identity.py`
9. `rcc002/s8/manifests/dataset.py` (Track 1 dependency, Section 6.9)
10. `rcc002/s8/manifests/run.py` (Track 1 dependency for its own run-ID field, but its Section 7.3 run-ID grammar correction is Track-1-independent)
11. `rcc002/s8/manifests/stage.py` (same note as `run.py`)
12. `rcc002/s8/publication.py`
13. `rcc002/s8/states.py`
14. `rcc002/s8/validation.py`
15. `rcc002/s8/views.py` (Track 1 dependency, Section 6.9)

**Modified -- S8 tests (8):**

16. `tests/rcc002/s8/test_artifact_class.py`
17. `tests/rcc002/s8/test_canonical.py`
18. `tests/rcc002/s8/test_identity.py`
19. `tests/rcc002/s8/test_manifests.py` (Track 1 dependency for `dataset.py`/`views.py` coverage; Track-1-independent for its `run.py`/`stage.py` run-ID coverage)
20. `tests/rcc002/s8/test_publication.py`
21. `tests/rcc002/s8/test_states.py`
22. `tests/rcc002/s8/test_validation.py`
23. `tests/rcc002/s8/test_views.py` (Track 1 dependency, Section 6.9)

**No other repository file may be modified under either track, and this
proposal does not itself modify any of them.**

### 8.4 Exact hardcoded-verifier requirements (closes remainder of `S8-CAND-BCP-REV2-B02`)

Both the Track 1 verifier (`scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`)
and the Track 2 verifier (`scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py`),
and the ledger verifier (`scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py`),
must each:

1. hold their own expected path lists and counts (Section 8.2's 36/3/33,
   Section 8.3's 23/20/3, Section 6.7's 178/145/33/2/0) as independent
   hardcoded constants inside the verifier's own source, never read from
   the corresponding scope manifest as ground truth;
2. compare the hardcoded expected list against the scope manifest's
   declared list and against the actual repository tree, requiring exact
   list equality in both comparisons;
3. reject, fail-closed, any missing, extra, duplicated, reordered,
   miscategorized, unsafe (absolute, traversal, backslash, or
   otherwise non-portable), undeclared, or truncated inventory entry, in
   either comparison; and
4. emit a single deterministic pass/fail result identifying the exact
   invariant violated on failure, matching the certified
   `verify_s8rr003_normative_ledger.py` pattern this section's
   requirements are directly modeled on.

### 8.5 Consolidated version/path/artifact matrix (updated)

| Item | Exact value |
|---|---|
| Data Pipeline Specification successor version | `0.9.0` (binding, Section 6.3) |
| RM successor version | `0.9.1` (binding, Section 6.3) |
| View-schema-fingerprint registry path | `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` |
| View-schema-fingerprint registry identity/version | `RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1` / `1.0.0` (binding) |
| Dataset Manifest successor schema version | `1.0.2` (binding) |
| Dataset Manifest successor schema path | `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` |
| Dataset Manifest `1.0.2` positive fixtures | exactly 2 (Section 8.2 items 6-7); 7 and 8 real View-fingerprint replacements respectively (Section 6.1) |
| Dataset Manifest `1.0.2` negative fixtures | exactly 22 (Section 6.5) |
| Dataset Manifest `1.0.2` case ledger entries | exactly 22 (Section 6.5) |
| View schema identities/versions | Unchanged: `research-features`/`1.0.0`, `backtest-inputs`/`1.0.0`, `paper`/`1.0.0`, `live`/`1.0.0`, `label-research`/`1.0.0`, `audit`/`2.0.0` |
| Canonicalization shared-authority module | `rcc002/canonical.py` (unchanged from Revision 2) |
| Canonicalization golden fixture path | `tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json` (unchanged) |
| Run-ID grammar | Revision 2 Section 7.3, unchanged |
| Golden preimage example count | Exactly two, everywhere in this document (Section 6.2) |
| Literal fingerprint count | Exactly six (registry) plus exact per-artifact replacement counts (Section 6.1) |
| Track 1 scope manifest / verifier | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` / `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` |
| Track 2 scope manifest / verifier | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json` / `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py` |
| Ledger historical copy / scope / verifier / tests | Section 6.7, four artifacts, Section 8.2 items 33-36 |
| Track 1 exact file count | 36 (3 modified, 33 new) |
| Track 2 exact file count | 23 (20 modified, 3 new) |
| Successor root ledger entry count | 178 (145 baseline + 33 added - 0 removed) |

## 9. Documentation corrections applied throughout (closes remainder of `S8-CAND-BCP-REV2-DOC-001`)

- The current seven-document specification profile is stated as exactly
  seven closed entries everywhere in this document (Section 6.3); no
  "future entries" phrase appears anywhere in Revision 3.
- Every historical positive-fixture fingerprint count in this document is
  the independently reproduced value (7 for `1.0.1`/`1.0.2` minimal, 8 for
  `1.0.1`/`1.0.2` complete; Section 2, Section 6.1), not the Revision 2
  values (1 and 2) that the re-review found false.
- The fingerprint registry's exact key sets (Section 6.4) leave no
  "at minimum", owner-extensible, or optional-unreviewed wording; any
  future key addition requires a new proposal revision, stated explicitly
  in Section 6.4's own text.
- Section 6.6 explicitly distinguishes schema ID/version consts (literal
  strings, no hash, available immediately once Section 6.3's versions are
  binding) from fixture document-hash inputs (require step 5's
  byte-finalized-document hashing), removing the Revision 2 conflation the
  re-review identified.
- "Exactly two" golden preimage examples is stated once, in Section 6.2,
  and not restated with different wording (no "at least one" phrasing
  appears anywhere in this document).

## 10. Fail-closed sequencing (updated diagram)

```text
                    +-----------------------------------------------+
                    | Track 1: Normative correction                   |
                    | Sections 6.1-6.9                                 |
                    | (fingerprint contract + Dataset Manifest 1.0.2   |
                    |  successor + normative-ledger successor)         |
                    +-----------------------------------------------+
                                     |
     Acyclic byte-finalization sequence (Section 6.6, steps 1-7) ->
     Internal review -> Scientific review -> Architecture review ->
     Independent mechanical verification (including ledger
     arithmetic, Section 6.7) -> Independent re-review ->
     Certification of the complete set together (Section 6.8,
     steps 1-8; Section 6.6, steps 8-10)
                                     |
                                     v
                    [ GATE: Track 1 certified? ]
                     NO  -------------------------------> STOP.
                     |                                    No implementation of the
                     |                                    fingerprint formula. No
                     |                                    real schema_fingerprint_sha256
                     |                                    may be emitted (Section 6.9).
                     |                                    No successor SHA256SUMS is
                     |                                    published (Section 6.7).
                     YES
                     |
                     v
     +---------------------------------------------------------------+
     | Track 2: Implementation repair (Section 7; exact 23-file        |
     | inventory, Section 8.3 -- independent of Track 1 and MAY start  |
     | in parallel with Track 1 drafting)                               |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: all Track-2 findings closed AND regression re-run       ]
     [        (focused S8 / complete RCC-002 / S0 identity / TD-005)  ]
     [        all green (Section 7.5, unchanged)?                     ]
                     |
                     v
     +---------------------------------------------------------------+
     | View-schema fingerprint formula implementation (only after the |
     | Track 1 gate above is YES) in rcc002/s8/views.py and             |
     | rcc002/s8/manifests/dataset.py                                   |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: both tracks fully closed, all sixteen findings' (nine    ]
     [        original, six Revision-1-review, seven Revision-2-       ]
     [        re-review minus one already-closed-by-B02-being-shared)  ]
     [        verification requirements satisfied?                     ]
                     |
                     v
          New independent scientific and architecture re-review
          of the corrected candidate, including a fresh
          proposal-conformance check against this Revision 3 document
                     |
                     v
          [ Re-review decision: ACCEPT or REJECT ]
                     |
            ACCEPT --+-- REJECT --> back to the relevant track above
                     |
                     v
     Candidate certification (a separate act from this proposal and
     from the re-review itself)
                     |
                     v
     S8 implementation remains bounded by RR-004 Sections 9-10.
     Dataset generation, publication, and deployment remain
     separately unauthorized regardless of certification (Section 11).
```

## 11. Preservation, prohibition, and re-review requirements (unchanged in substance, restated for Revision 3)

- **Historical preservation.** No certified historical artifact --
  including Data Pipeline `0.8.0` and RM `0.9.0` themselves (preserved via
  git history under the specification-document versioning convention,
  Section 6.3), the certified Dataset Manifest `1.0.0` and `1.0.1`
  schemas and their complete fixture families (Section 6.5), the current
  145-entry `SHA256SUMS` (preserved as an immutable historical evidence
  copy, Section 6.7), and the certified S8-RR-003 ledger scope/verifier
  (unmodified; superseded, not edited, by the new Section 6.7 artifacts)
  -- may be modified except through an explicit versioned successor
  certified through the normal correction-cycle process. This proposal
  does not itself modify, and does not authorize modifying, any such
  artifact.
- **No dataset generation, publication, or deployment**, at any point in
  this proposal, including after both tracks close and a corrected
  candidate is certified.
- **No S8 production code from this proposal.**
- **Mandatory new independent review** after both tracks close, before
  any certification decision, re-running the complete adverse-mutation
  matrix (Revision 1 Section 6.12, Revision 2 Section 7.6, and this
  revision's Section 6.7 ledger mutation battery) outside the candidate
  tree.
- **Decision separation, restated.** Proposal approval (this document),
  normative contract certification (Track 1 output, including the
  fingerprint contract, the Dataset Manifest successor, and the
  normative-ledger successor), implementation repair authorization
  (Track 2 start), candidate re-certification (the required re-review's
  outcome), and S8/dataset readiness (RR-004, unaffected by this proposal
  in either direction) remain five separate decisions. Approving this
  proposal approves only the plan in Sections 5 through 10; it does not
  itself grant any of the other four.

## 12. Restrictions honored while preparing this revision

- No repository file was created, modified, deleted, renamed, staged,
  committed, or pushed.
- The existing S8 candidate (`rcc002/s8/`, `tests/rcc002/s8/`) was not
  modified, staged, committed, or pushed.
- No implementation code was run. No test was executed.
- No dependency was installed. No network access was used.
- No dataset was generated or published.
- No S8 production code was created.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified,
  staged, or packaged; it appears only in the document-control table's
  worktree-state row, Section 6.7's exclusion statement, and this
  restrictions section.
- All diagnostics performed to prepare this revision were passive
  (branch/HEAD/origin/status checks, read-only file inspection, read-only
  JSON parsing and counting, hash computation over already-existing
  files, and in-memory reasoning); none created a repository artifact.
- The only filesystem write performed while preparing this revision was
  this single output Markdown file, outside the repository, in
  `/mnt/c/Users/benja/Downloads/`.

## 13. Final statement

Revision 3 closes all seven findings raised against Revision 2
(`S8-CAND-BCP-REV2-B01`, `S8-CAND-BCP-REV2-B02`,
`S8-CAND-BCP-REV2-ARCH-001`, `S8-CAND-BCP-REV2-ARCH-002`,
`S8-CAND-BCP-REV2-ARCH-003`, `S8-CAND-BCP-REV2-ARCH-004`,
`S8-CAND-BCP-REV2-DOC-001`) with exact, independently re-derived counts,
exact closed schemas, exact exhaustive path inventories, a resequenced
acyclic byte-finalization order, a binding version table, and a full
normative-ledger successor subtrack -- while preserving every Revision 2
decision the re-review confirmed as sound and continuing to withhold the
one decision that has never belonged to this proposal: the actual
View-schema-fingerprint preimage formula, reserved exclusively for the
independently reviewed and certified Track 1 normative correction
artifact (Section 3).

**This proposal, by itself, does not authorize and does not perform S8
implementation repair, View-schema-fingerprint formula selection or
emission, corrected-candidate resubmission, dataset generation, dataset
publication, or live or paper deployment. Every one of those actions
remains unauthorized unless and until the sequencing in Section 10 and
the requirements in Section 11 are satisfied in full, through acts
entirely separate from, and later than, this proposal document itself.**
