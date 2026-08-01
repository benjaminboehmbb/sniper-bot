# RCC-002 S8-RR-002 Correction Candidate ChatGPT Independent Re-Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR002-CAND-CR-002` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Targeted independent re-review after verifier-scope repair |
| Repository baseline | `af8d031b3e987e5738191fba0396d36a7df88c9e` |
| Candidate package | `RCC_002_S8RR002_CORRECTION_CANDIDATE_REREVIEW_INPUT_2026-08-01.zip` |
| Candidate package SHA-256 | `f95378189f45998d217c7516dd7fc5dbb2f8d6482d64cce7fb469cec6e2b2327` |
| Controlling prior review | `RCC_002_S8RR002_CORRECTION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling prior review SHA-256 | `bc78bf2e0f6b77ab0df1a3a6b32e024fb84f6afe116931a95ca6b9a7309d5054` |
| Finding re-reviewed | `S8RR002-CAND-ARCH-001` |
| Readiness findings | `S8-RR2-B01`, `S8-RR2-B02` |
| Final decision | `APPROVE` |

## 1. Executive decision

The focused repair fully closes the sole major finding from the first
candidate review, `S8RR002-CAND-ARCH-001`.

The versioned scope is now validated against exact independently hardcoded
metadata and exact closed path lists. The verifier derives its fixture read
sets from the validated scope, rejects undeclared fixture files before any
fixture-byte read, and emits a stable SHA-256 inventory containing all 30
generated or modified correction-candidate files.

The exact mutation that previously produced a false `PASS` was repeated
independently. Removing `wrong-schema-identity.json` from the scope while
leaving the fixture untouched now raises `VerificationError` before a `PASS`
report or truncated inventory can be emitted.

No new blocking, major or minor scientific or architecture finding was
identified. The corrected candidate is approved for the next certification
step. This approval is not itself certification and does not authorize S8
production code or dataset publication.

## 2. Package and baseline verification

The supplied package matched the owner-reported SHA-256 exactly. ZIP path
safety passed, 1,800 ZIP entries were inspected, and 1,504 source files were
extracted into an isolated review directory.

The protected untracked file
`scripts/build_rcc002_spec_bundle.py` was absent from the package and was not
read, hashed, inspected or executed during this re-review.

The package contained the controlling prior rejection review with the exact
required SHA-256:

```text
bc78bf2e0f6b77ab0df1a3a6b32e024fb84f6afe116931a95ca6b9a7309d5054
```

The corrected Run Manifest `0.9.0` bytes retained the exact pre-repair
SHA-256:

```text
23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1
```

## 3. Repair-boundary verification

All 41 scoped paths in the repaired package were compared byte-for-byte with
the rejected candidate. Exactly the three authorized repair files changed:

1. `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
2. `scripts/rcc002/verify_s8rr002_artifacts.py`;
3. `tests/rcc002/test_s8rr002_manifest_correction.py`.

Their repaired SHA-256 values are:

| Artifact | SHA-256 |
|---|---|
| Scope manifest | `7253c44c9d342e6a26e356d07f1ca37efcb43b843d93636e9e7e1594530c840c` |
| Correction verifier | `2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335` |
| Focused and mutation tests | `2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4` |

The other 27 candidate outputs and all 11 immutable reference inputs were
byte-identical to the already reviewed rejected candidate. Therefore the
previously accepted scientific, normative, schema, fixture, literal-hash and
Ajv Draft 2020-12 evidence remains applicable without alteration.

No normative Run Manifest text, Schema `1.0.1`, fixture, case-ledger,
dependency-pin, historical artifact, S0-S7 implementation or S8 production
artifact changed in this repair.

## 4. Closure of `S8RR002-CAND-ARCH-001`

### 4.1 Exact closed scope

The repaired verifier defines independent expected constants for:

- all required scope metadata;
- the exact 11 immutable reference-input paths;
- the exact 30 correction-candidate output paths.

`validate_scope()` now enforces exact list equality, including deterministic
order and category membership. It also rejects missing, extra, duplicate,
absolute, non-POSIX and parent-traversal paths and confirms every declared
path exists.

An independent reconstruction of the required candidate set used the six
non-fixture candidate artifacts plus every file under the new Dataset
Manifest `1.0.1` fixture directory. It produced exactly 30 paths. The scope
manifest matched this independently reconstructed set with no missing or
extra entry.

### 4.2 Scope-driven fixture reads

The positive and negative fixture read sets are now derived by
`derive_fixture_paths_from_scope()` from the validated candidate-output list.
The two remaining `Path.glob()` calls are confined to name-only enumeration
of the positive and negative `1.0.1` fixture directories. They are used only
to reject an undeclared on-disk fixture before fixture bytes are read; they do
not supply the verifier read set.

Instrumented verifier execution recorded no undeclared byte read. Forty
unique scoped paths were byte-read. The only declared path not content-parsed
was the controlling Revision 2 proposal; its exact membership, category and
existence were validated. This is consistent with its role as the controlling
reference rather than a mechanically parsed contract input and is not a
finding.

### 4.3 Complete stable candidate inventory

The verifier now asserts an exact 30-entry candidate list before inventory
construction and an exact 30-entry inventory afterward. The emitted
inventory includes the three previously omitted artifacts:

- the scope manifest itself;
- the correction verifier;
- the focused and mutation test file.

Two independent verifier executions produced byte-identical JSON reports.
The report SHA-256 was:

```text
aa1087171191d514a6d6117571e8474208b464d6a89da805e31a1f3c9f1c46a1
```

The report recorded two positive fixture files, two distinct positive
payloads, 21 rejected negative fixtures, four immutable historical artifacts,
six views, seven specification-profile entries and 30 candidate inventory
entries.

### 4.4 Exact prior-review mutation

The prior review mutation was reproduced independently in memory:

```text
tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-identity.json
```

The path was removed from `correction_candidate_outputs` while the fixture
remained on disk. The repaired verifier rejected the scope with an exact
missing-entry error. No `PASS` output or partial candidate inventory was
emitted. The fixture remained present and retained SHA-256:

```text
e7008f18d5d5aeef467d5b802c9867df381083af1bdb12244d61054d7d8b47a9
```

This directly falsifies the failure mode demonstrated in the prior review.

### 4.5 Mutation-test coverage

The added `S8RR002ScopeMutationTests` independently covers:

1. removed immutable input;
2. removed candidate output;
3. undeclared fixture on disk;
4. extra candidate path in scope;
5. duplicate within one category;
6. duplicate across categories;
7. absolute path;
8. parent traversal;
9. required path in the wrong category;
10. incorrect scope metadata;
11. the exact prior-review incomplete-inventory mutation;
12. the valid unmutated 11/30 positive control.

All 12 mutation and positive-control tests passed. Together with the 16
pre-existing focused correction tests, the focused file contains 28 passing
tests.

## 5. Independent execution results

The Python validation dependency was installed into an isolated temporary
target from the unchanged review-only pin `jsonschema==4.26.0`. The production
`requirements.txt` was not changed.

| Check | Independent result |
|---|---:|
| Candidate package SHA-256 | `MATCH` |
| ZIP path safety | `PASS` |
| Protected builder exclusion | `PASS` |
| Three-file repair boundary | `PASS` |
| Independent 30-path candidate reconstruction | `PASS` |
| Repaired verifier | `PASS` |
| Exact prior-review mutation | `REJECTED AS REQUIRED` |
| Focused and mutation tests | `28/28 PASS` |
| Complete RCC-002 suite | `659/659 PASS` |
| TD-005 regression suite | `170/170 PASS` |
| Targeted Python compilation | `PASS` |
| Scoped UTF-8 BOM and CRLF check | `41/41 PASS` |
| Candidate inventory | `30/30` |
| Distinct positive fixture payloads | `2/2` |
| Negative fixtures rejected | `21/21` |

No reviewed source-artifact bytes were modified during this re-review.

## 6. Findings and process observations

### 6.1 Material findings

No blocking, major or minor finding remains open.

`S8RR002-CAND-ARCH-001` is closed.

### 6.2 Prior protected-file process deviation

The earlier implementation-session `md5sum` read of the protected builder
remains disclosed in the prior review. The repair session reported no further
access, and the protected file is absent from the re-review package. No new
process deviation was observed during this re-review.

## 7. Final decision

The repaired candidate enforces the approved closed verification scope,
derives fixture reads from that scope, rejects the exact previously accepted
scope omission, and emits the complete deterministic 30-file SHA-256
inventory. The repair is confined to the three authorized architecture and
test artifacts, and all focused and full regression evidence passes.

The correction candidate is approved for certification. Certification must
still be performed as a separate controlled step, followed by a repeated S8
implementation-readiness review. S8 production implementation and dataset
publication remain prohibited until that repeated review explicitly returns
`READY`.

APPROVE
