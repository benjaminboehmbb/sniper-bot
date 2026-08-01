# RCC-002 S8 Implementation Candidate ChatGPT Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8-CAND-CHATGPT-IR-001` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Independent implementation-candidate review |
| Repository baseline | `ceed9de11aeb07b37b3da8f9baf8f9c3af844004` |
| Candidate package | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_REVIEW_INPUT_2026-08-01.zip` |
| Candidate package SHA-256 | `1246a675ae5b3aeb17289c9167d603dcfbab80494e1261a6d7ae922b035cb15f` |
| Controlling readiness review | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md` |
| Readiness review SHA-256 | `16876c0815e3735e64b2eacfd85199b5b7c2c5046488482b51389359218d0ee3` |
| Review mode | Read-only |
| Final decision | `REJECT` |

## 1. Scope and restrictions

This review independently assessed the uncommitted S8 implementation candidate
against the certified RCC-002 specifications and the implementation boundary in
RR-004 Sections 9 and 10.

The review did not authorize or perform dataset generation, publication,
deployment, staging, committing, or pushing. The protected untracked file
`scripts/build_rcc002_spec_bundle.py` was absent from the package and was not
accessed.

The extracted review copy was not modified. Test execution used
`PYTHONDONTWRITEBYTECODE=1` and `python3 -B`; mutation checks used only in-memory
objects and temporary directories outside the extracted package.

## 2. Package integrity and inventory

The package hash matched the supplied value. ZIP member names passed the
absolute-path and parent-traversal check. The protected builder was absent.

The candidate contains exactly 33 Python files and no non-Python candidate
files:

- 21 files under `rcc002/s8/`;
- 12 files under `tests/rcc002/s8/`.

The implementation report says "32 new files" while its own enumerated list is
21 plus 12. This is a reporting-count defect only; the archive itself contains
the complete 33-file set.

## 3. Evidence inspected

The review inspected:

- all 21 S8 implementation files;
- all 12 focused S8 test files;
- RR-004 and its authorized implementation/test boundaries;
- the Data Pipeline Specification, especially Sections 6.2 and 7.9;
- the Reproducibility and Manifest Specification, especially Sections 5, 6,
  8.7, 13, 14, 18, 26 and 27;
- all six manifest schemas used by the builders;
- the certified release artifact-class registry;
- the existing S0 canonicalization implementation wrapped by S8;
- the complete focused, RCC-002 and TD-005 test suites.

## 4. Positive results

The following candidate areas were independently found coherent within the
reviewed scope:

- the field registry is centralized rather than duplicated across views;
- the six view orders and 232/534 field counts match the certified registry;
- the two certified allowlist hashes are independently checked at import;
- S7 fields are excluded from the four non-label views;
- `audit` correctly uses View Schema `2.0.0` despite the unrelated stale
  top-level constant;
- row identity, count, order and value reconciliation is explicit and
  fail-closed for the tested mutations;
- Dataset Manifest production is restricted to Schema `1.0.1`;
- manifest builders validate their output against the certified JSON Schemas;
- semantic and physical dataset identities are represented by separate
  builders;
- ordinary candidate publication, collision rejection and gate checks work for
  the tested valid inputs;
- no real dataset was created or published by the candidate tests.

These positive results are not sufficient for certification because the
findings below affect canonical identity, logical schema identity and final
publication safety.

## 5. Findings

### 5.1 `S8-CAND-B01` - BLOCKER - canonical JSON is not RFC 8785/JCS

Location:

- `rcc002/s8/canonical.py`, which delegates all JSON canonicalization to
  `rcc002.s0.source_identity.canonical_json_bytes`;
- `rcc002/s0/source_identity.py:45-71`;
- `tests/rcc002/s8/test_canonical.py`.

The delegated implementation normalizes strings and then uses
`json.dumps(..., sort_keys=True)`. Python sorts strings by Unicode scalar value.
RFC 8785/JCS sorts object-property names by UTF-16 code units. Those orders
differ for non-BMP keys.

Independent mutation:

```text
input keys: U+E000 and U+1F600
candidate bytes: {"U+E000":1,"U+1F600":2}
JCS order:       {"U+1F600":2,"U+E000":1}
result: candidate differs from RFC 8785/JCS
```

The review also supplied two distinct input keys, precomposed `U+00E9` and
decomposed `U+0065 U+0301`. NFC makes them identical, and the dict
comprehension silently drops one value instead of rejecting the post-NFC key
collision.

This violates RM 0.9.0 Section 6.2, which requires RFC 8785/JCS and NFC, and
RR-004 mandatory tests 7 and 8. The candidate's "independent" oracle repeats
Python's `sorted()` rule, so it is not independent for the normative ordering
boundary and does not detect this defect.

Impact: deterministic IDs, manifest IDs, configuration hashes and schema
fingerprints may differ across conforming implementations or silently lose a
property. The implementation cannot be certified while this identity primitive
is non-conformant.

Required correction:

1. implement actual RFC 8785 property ordering after NFC preprocessing;
2. reject duplicate property names created by NFC normalization;
3. add versioned golden fixtures with expected bytes and SHA-256 values,
   including a non-BMP UTF-16 ordering case and an NFC-key-collision negative
   case;
4. bind the tests to those external fixtures rather than another implementation
   using Python's native string sort.

### 5.2 `S8-CAND-B02` - BLOCKER - an unregistered placeholder is emitted as the logical View-schema fingerprint

Location:

- `rcc002/s8/views.py:98-119`;
- `rcc002/s8/manifests/dataset.py`, `_views_block()`.

The code explicitly describes `schema_fingerprint_sha256` as a placeholder
pending specification-owner confirmation. Its preimage contains only profile
label, schema ID, schema version and ordered field names. It omits required
logical-contract dimensions, including allowed producer stages, field owner
stage, leakage class, allowlist identity and compatibility profile.

Independent mutation constructed two `ViewDefinition` values with identical
schema identity and ordered fields but different allowed producer stages and
different allowlist hashes. The candidate produced the same
`schema_fingerprint_sha256` for both.

This conflicts with:

- Data Pipeline Specification Section 6.2, where a logical schema includes
  types, nullability, field order, primary key, sort contract, owner stages,
  registries and compatibility rules;
- Data Pipeline Specification Section 7.9.2, which places schema identity and
  the allowlist hash in the overarching View-schema fingerprint;
- RM Section 8.7, which requires owner stages, leakage classes and the applied
  compatibility profile for each View;
- RM Section 13, which defines the schema fingerprint as the hash of the
  complete logical schema contract.

The placeholder is not dormant: every generated Dataset Manifest receives it
through `_views_block()`. RR-004 states that no new normative schema-identity
decision is needed and forbids silent reinterpretation. A candidate cannot
resolve the missing contract by inventing an implementation-owned profile.

Required correction: stop emitting a placeholder. The exact complete
View-schema fingerprint profile and its versioned preimage must be resolved by
the specification owner, certified, implemented and tested against independent
literal or fixture evidence before candidate certification resumes.

### 5.3 `S8-CAND-B03` - BLOCKER - atomic publication permits target-path traversal

Location: `rcc002/s8/publication.py:60-89`.

`publish_atomically()` checks only the ID prefix. It does not require the suffix
to be exactly 64 lowercase hexadecimal characters. The suffix is joined
directly to `publish_root`.

Reproduced mutation:

```text
dataset_artifact_set_id = dataset-artifact-set:sha256:../escaped
publish_root            = <temp>/publish
returned target         = <temp>/publish/../escaped
observable result       = staging directory moved outside publish_root
```

All publication gates were true and the state was `candidate`; the operation
succeeded. This violates the portable identity format, atomic-publication
containment, and RR-004 mandatory no-silent-overwrite/atomic-publication test
boundary. A caller-supplied sandbox is not a safety boundary if an accepted ID
can escape it.

Required correction:

- validate the complete ID with
  `^dataset-artifact-set:sha256:[0-9a-f]{64}$`;
- require the staging directory to be a direct, resolved descendant of the
  resolved publication root;
- derive the target only from the validated digest and verify resolved-parent
  containment before rename;
- add traversal, absolute, malformed-digest, symlink and out-of-root staging
  mutation tests.

### 5.4 `S8-CAND-ARCH-001` - MAJOR - artifact classification normalizes unsafe paths into valid registry paths

Location: `rcc002/s8/artifact_class.py:80-107`.

`replace("\\", "/").lstrip("./")` is not path validation. It strips any
leading combination of dots and slashes and converts prohibited backslashes.
The following three unsafe paths were all accepted and classified as
`RELEASE_LEDGER`:

```text
/SHA256SUMS
../SHA256SUMS
.\SHA256SUMS
```

This contradicts the documented fail-closed classifier and permits different
unsafe inputs to collapse onto the same registry identity.

Required correction: validate a repository-relative POSIX path before registry
matching. If a leading `./` convenience form is supported, remove exactly one
literal `./`; do not use `lstrip` and do not convert a prohibited separator.

### 5.5 `S8-CAND-ARCH-002` - MAJOR - release-ledger generation accepts line-breaking paths

Locations:

- `rcc002/s8/validation.py:52-66`;
- `rcc002/s8/publication.py:102-116`.

The portable-path helper does not reject control characters, empty components,
`.` components or newlines. `build_release_ledger()` interpolates the accepted
path directly into a line-oriented ledger.

Reproduced mutation:

```text
path: "safe\nforged"
result: one file produces two ledger lines
```

This makes the ledger grammar ambiguous and can create a forged-looking line.
The same path helper is reused by publication and inventory validation.

Required correction: define and enforce a single canonical portable-path
grammar that rejects all C0 controls, DEL, CR/LF, empty segments, `.` and `..`,
absolute/drive paths and backslashes. Add exact grammar tests at the helper,
ledger and publication boundaries.

### 5.6 `S8-CAND-IMPL-001` - MAJOR - identity builders accept invalid IDs and invalid dataset component ranges

Location: `rcc002/s8/identity.py:205-263, 281-346`.

Several references are checked only with `startswith`, not with the complete
registered ID grammar. `DatasetComponent.as_preimage()` also omits the
non-negative row-count and coverage-order checks already present for
`DataArtifactIdentity`.

The review passed all of the following together:

```text
build_id_value = build:sha256:not-a-digest
row_count = -1
logical_time_coverage = (5, 1)
```

`dataset_id()` returned a deterministic Dataset ID instead of failing. Similar
prefix-only validation exists for artifact and dataset IDs, and
`PublishedDataArtifact.relative_path` is not checked with the portable-path
validator before entering the exact Dataset Artifact Set preimage.

Required correction: centralize full ID-format validators, apply them to every
referenced ID, enforce non-negative counts and ordered coverage consistently,
and validate/canonicalize every relative path before sorting or hashing.

### 5.7 `S8-CAND-TEST-001` - MAJOR - mandatory golden evidence is self-contained in test code, not versioned fixtures

RM Section 6.2 requires versioned Golden Fixtures containing expected canonical
bytes and SHA-256 digests. RR-004 mandatory test 8 requires JCS, NFC, decimal,
timestamp and non-finite golden cases. The 33-file candidate contains no fixture
file; expected values are embedded in `test_canonical.py`, and its independent
oracle repeats the implementation's incorrect key ordering.

This is both an evidence gap and the reason `S8-CAND-B01` survived 185 focused
tests.

Required correction: add a machine-readable, versioned canonicalization fixture
with externally fixed bytes/digests and negative cases, and make both the
implementation test and an actually independent oracle consume it.

### 5.8 `S8-CAND-STATE-001` - MINOR - the final-path helper does not enforce its declared publication-state set

Locations:

- `rcc002/s8/states.py`, `PUBLICATION_PATH_STATES` and
  `require_not_diagnostic_only()`;
- `rcc002/s8/publication.py`, `require_not_diagnostic_publication()`.

The module declares that only `published`, `superseded` and `withdrawn` may
legitimately be referenced under a final publication path. The helper rejects
only `failed` and `quarantined`, therefore also permits `planned`, `running`,
`validating` and `candidate` in that final-path context.

Required correction: make the final-path helper require membership in
`PUBLICATION_PATH_STATES`; keep the separate `require_publishable()` candidate
gate for the atomic transition.

### 5.9 `S8-CAND-DOC-001` - INFORMATIONAL - candidate file count is misstated

The implementation report says 32 new files but lists and packages 33. Correct
the report in the next candidate summary. No archive content is missing.

## 6. Independent mutation matrix

| Mutation | Expected | Candidate result | Review result |
|---|---|---|---|
| Non-BMP JCS key-order pair | UTF-16 JCS order | Python scalar-value order | FAIL |
| Two keys colliding after NFC | Reject duplicate canonical key | One value silently discarded | FAIL |
| View allowed stages and allowlist changed | Schema fingerprint changes | Fingerprint unchanged | FAIL |
| Publication ID suffix `../escaped` | Reject before filesystem action | Directory moved outside root | FAIL |
| Absolute classifier path | Reject | Classified as release ledger | FAIL |
| Parent-traversal classifier path | Reject | Classified as release ledger | FAIL |
| Backslash classifier path | Reject | Classified as release ledger | FAIL |
| Ledger path containing LF | Reject | Extra ledger line emitted | FAIL |
| Invalid build ID plus negative count/reversed coverage | Reject | Dataset ID produced | FAIL |

All mutations were performed outside the candidate tree and left no project
artifact behind.

## 7. Test execution

The review used the pinned review dependency `jsonschema==4.26.0` from an
existing isolated dependency directory.

| Command class | Result |
|---|---|
| Focused S8 discovery | 185/185 PASS |
| Complete RCC-002 discovery | 885/885 PASS |
| TD-005 regression discovery | 170/170 PASS |
| Independent adverse mutations | 9/9 defects reproduced |

The original suites passing is credible and independently reproduced. Their
pass status does not rebut the findings because the adverse inputs above are
absent from the candidate tests.

## 8. Required repair and re-review boundary

At minimum, the repair cycle must cover:

1. actual RFC 8785/JCS canonicalization and external golden fixtures;
2. a certified complete View-schema fingerprint contract, with no placeholder;
3. complete ID grammar validation and publication-root containment;
4. strict portable-path validation at classification, identity, ledger,
   manifest and publication boundaries;
5. consistent dataset component count/time validation;
6. final-path state enforcement;
7. mutation tests reproducing every finding in Section 6;
8. repeated focused, complete RCC-002 and TD-005 test runs;
9. a new read-only independent scientific and architecture re-review.

The repair must not access the protected builder, generate or publish a real
dataset, or silently modify certified normative artifacts. If the complete
View-schema fingerprint preimage is not already authoritatively fixed, that
item requires a focused normative correction and certification before the
implementation repair can be approved.

## 9. Non-modification confirmation

No file inside the extracted candidate package was created, modified, deleted,
renamed or moved during this review. No dataset was generated or published. No
live or paper deployment occurred. No dependency was installed into the
candidate. No repository staging, commit or push was performed.

## 10. Final decision

The candidate demonstrates substantial correct work in view derivation,
leakage exclusion, reconciliation, manifest structure and ordinary test paths.
However, it currently accepts a filesystem-escaping publication identity,
implements non-conformant canonical JSON, and emits a disclosed unregistered
placeholder as a normative logical-schema fingerprint. These are independent
blocking defects. Additional unsafe path and identity-validation defects make
controlled certification impossible in the current state.

This decision rejects only the implementation candidate. It does not revoke
RR-004 readiness authorization for a corrected S8 implementation within the
authorized boundary, and it does not authorize dataset publication or
deployment.

REJECT
