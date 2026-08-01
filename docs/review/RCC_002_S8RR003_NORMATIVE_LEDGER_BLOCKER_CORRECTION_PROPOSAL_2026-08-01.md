# RCC-002 S8-RR-003 Normative Ledger Blocker Correction Proposal

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8RR003-NLBCP-001` |
| Date | `2026-08-01` |
| Repository baseline | `f1b9bcfaf5528d756f8e9199c7105889fbaaf1ea` |
| Trigger | `RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md` |
| Finding in scope | `S8-RR3-B01` |
| Change class | Focused normative-ledger lifecycle and integrity correction |
| S8 implementation | Prohibited |
| Dataset publication | Prohibited |
| Status | Proposed for independent scientific and architecture review |

## 1. Decision requested

Approve one focused correction cycle that:

1. preserves the certified S8BCP-001 Revision 2 root ledger byte-for-byte as
   versioned historical evidence;
2. replaces the repository-root `SHA256SUMS` with a current, exact-scope
   normative-bundle ledger;
3. defines the successor ledger as an exact ordered set of 145 paths;
4. binds the successor ledger to a versioned machine-readable scope manifest;
5. adds an independent mechanical verifier and mutation tests that fail on
   every missing, extra, duplicate, reordered, unsafe or hash-inconsistent
   entry;
6. obtains focused independent review and certification before controlled
   commit;
7. regenerates the S8 implementation input and repeats S8 readiness before any
   S8 production code is created.

This proposal does not authorize S8 implementation or dataset publication.

## 2. Problem statement

The repository-root `SHA256SUMS` is explicitly designated by the certified
S8BCP-001 Revision 2 review chain as the normative-bundle ledger. Its certified
byte identity is:

```text
a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43
```

The ledger contains 110 lexically sorted, unique paths. It records the
pre-S8-RR-002 hash for the Reproducibility and Manifest specification:

```text
22d6460f16f7f70e677a40dcd4e428e3739d9bb37fb0f7340512cca1b1ebb382
```

The certified current RM `0.9.0` byte identity is:

```text
23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1
```

Consequently, the current repository cannot satisfy both of its authoritative
claims:

- RM `0.9.0` is the certified current manifest contract; and
- the repository-root normative ledger verifies the current normative bundle.

The S8-RR-002 correction scope certified the new RM, Dataset Manifest Schema
`1.0.1`, fixtures and verifier, but it did not version, withdraw, replace or
supersede the older root ledger. A package-local checksum inventory can prove
transport integrity but cannot resolve this nested normative contradiction.

## 3. Governing principles

### 3.1 No silent historical rewrite

The old root ledger must not disappear or be represented as if it had always
contained the current hashes. Before the root path is replaced, its exact bytes
must be copied to:

```text
docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt
```

The historical evidence file must:

- be byte-identical to the old root `SHA256SUMS`;
- have SHA-256
  `a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43`;
- use mode `100644`;
- remain a historical record and never be evaluated as a current-tree ledger.

### 3.2 One current root authority

After the transition, repository-root `SHA256SUMS` remains the single current
normative-bundle ledger. It supersedes the old root ledger prospectively. The
historical evidence copy retains the old certified identity and meaning.

The successor ledger is not a complete inventory of the implementation source
tree. Its scope is exactly the versioned normative and normative-verification
set defined in Section 4. Complete repository and package integrity remain the
responsibility of Git identity, controlled import checks and package-local
inventories.

### 3.3 No self-hash

The successor root `SHA256SUMS` must not list itself. This prevents a circular
hash definition. The exact-scope manifest lists the files hashed by the root
ledger, not the root ledger itself.

### 3.4 Frozen scope boundary

The successor ledger scope is frozen when the correction candidate is
generated. Independent re-reviews and the later certification decision are
post-freeze governance evidence and are not retroactively inserted into the
same root ledger. Their integrity is established by their own hashes, Git
commits and review-package inventories.

Any later normative change must perform another explicit ledger transition;
it must not silently leave the current root authority stale.

## 4. Exact successor scope

### 4.1 Set construction

The successor ledger path set must be generated from the following three
explicit inputs and then deduplicated:

1. all 110 repository-relative paths contained in the certified historical
   root ledger;
2. all 30 exact `correction_candidate_outputs` in
   `RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
3. the six S8-RR-003 lifecycle and verification paths listed in Section 4.2.

The RM specification path is the only overlap between sets 1 and 2. Therefore:

```text
110 + 30 - 1 + 6 = 145 exact successor entries
```

No directory scan, recursive discovery, naming heuristic or mutable glob may
define this scope.

### 4.2 Six S8-RR-003 paths

The following six paths must be added to the exact successor set:

```text
docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-08-01.md
docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md
docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt
docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json
scripts/rcc002/verify_s8rr003_normative_ledger.py
tests/rcc002/test_s8rr003_normative_ledger.py
```

### 4.3 Scope categories

The versioned scope manifest must preserve the provenance of the 145 paths in
three lexically sorted arrays:

- `historical_normative_paths`: the exact 110-path set from the old ledger;
- `s8rr002_correction_outputs`: the exact 30-path list from the certified
  S8-RR-002 scope;
- `s8rr003_lifecycle_outputs`: the exact six paths in Section 4.2.

It must also contain an exact deduplicated `current_ledger_paths` array of 145
paths. The manifest metadata must be exactly:

```json
{
  "scope_schema_version": "1",
  "scope_id": "RCC002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1",
  "correction_id": "RCC-002-S8RR003-NLBCP-001",
  "finding_in_scope": "S8-RR3-B01",
  "ledger_path": "SHA256SUMS",
  "historical_ledger_sha256": "a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43",
  "path_ordering": "LC_ALL=C lexical order, repository-relative POSIX paths",
  "entry_format": "lowercase SHA-256, two spaces, ./-prefixed path",
  "expected_current_entry_count": 145,
  "consumed_by": "scripts/rcc002/verify_s8rr003_normative_ledger.py"
}
```

The scope manifest must not contain file hashes. Hash authority belongs to the
root ledger. This separation keeps the path contract independently mutable in
tests without duplicating the hash ledger.

## 5. Successor ledger format

The new root `SHA256SUMS` must satisfy all of the following:

1. ASCII text, LF line endings, exactly one final newline;
2. exactly 145 non-empty lines;
3. each line matches `^[0-9a-f]{64}  \\./[^\\r\\n]+$`;
4. exactly two ASCII spaces separate digest and path;
5. every path is repository-relative POSIX syntax prefixed by `./`;
6. no absolute path, backslash, empty component, `.` component or `..`
   component;
7. no duplicate path and no duplicate line;
8. paths are in strict `LC_ALL=C` lexical order;
9. its path set equals `current_ledger_paths` exactly;
10. `SHA256SUMS` itself is absent from the entries;
11. every declared path exists as a regular, non-symlink file;
12. every digest equals the SHA-256 of the corresponding current file bytes;
13. RM uses the certified current hash
    `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1`;
14. `sha256sum -c SHA256SUMS` verifies exactly 145 of 145 entries.

The successor root ledger receives a new byte identity. That identity must not
be invented in this proposal; it must be computed from the finalized candidate
and recorded in its review and certification evidence.

## 6. Required implementation artifacts

The correction candidate may modify or create only these five payload files:

```text
SHA256SUMS
docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt
docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json
scripts/rcc002/verify_s8rr003_normative_ledger.py
tests/rcc002/test_s8rr003_normative_ledger.py
```

The already committed readiness review and this proposal are immutable inputs
to the correction candidate. No specification, schema, registry, fixture,
S0-S7 implementation file, production requirement file or prior review file
may change during this focused correction.

The protected untracked file
`scripts/build_rcc002_spec_bundle.py` must not be read, hashed, inspected,
executed, modified, staged, committed, packaged or deleted.

## 7. Mechanical verifier contract

The verifier must use only Python standard-library dependencies and must run
from the repository root as:

```text
python3 scripts/rcc002/verify_s8rr003_normative_ledger.py
```

It must emit one deterministic JSON object to standard output. A successful
result must include at least:

```json
{
  "result": "PASS",
  "scope_id": "RCC002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1",
  "historical_entry_count": 110,
  "s8rr002_output_count": 30,
  "s8rr003_output_count": 6,
  "current_ledger_entry_count": 145,
  "verified_entry_count": 145,
  "historical_ledger_sha256": "a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43",
  "current_rm_sha256": "23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1"
}
```

Before reading any ledger target file, the verifier must:

1. load and validate the scope manifest;
2. compare all metadata to hardcoded expected constants;
3. compare each source category to an independently hardcoded exact list;
4. derive the exact 145-path union independently;
5. reject duplicates, cross-category inconsistencies and unexpected overlap;
6. parse and validate all root-ledger lines;
7. require exact ordered path-list equality between ledger and scope.

Only after those gates pass may it read the 145 declared target files and
verify their hashes. It must never discover target files through `rglob`,
recursive `glob`, `os.walk`, `find` or directory traversal.

The verifier must additionally prove:

- the historical evidence copy has the exact old ledger SHA-256;
- the historical copy contains exactly 110 sorted unique entries;
- the old RM digest is present only in the historical copy;
- the current root ledger contains the certified RM `0.9.0` digest;
- the root ledger does not list itself;
- the current root ledger and historical copy are not byte-identical;
- all five permitted correction payload paths are correctly classified;
- no protected builder path appears in any scope category or ledger.

On any failure, it must exit non-zero, emit no `PASS`, and identify the failed
invariant without printing file contents.

## 8. Required focused tests

The test module must exercise the verifier through pure functions and isolated
temporary directories. At minimum it must cover:

1. valid unmodified 110/30/6/145 positive control;
2. missing historical path;
3. missing S8-RR-002 correction output;
4. missing S8-RR-003 lifecycle output;
5. extra current ledger path;
6. duplicate within a category;
7. duplicate or invalid overlap across categories;
8. reordered category;
9. reordered current union;
10. incorrect scope metadata;
11. absolute path;
12. parent traversal;
13. backslash path;
14. root-ledger self-entry;
15. missing ledger entry;
16. extra ledger entry;
17. duplicate ledger entry;
18. reordered ledger entry;
19. malformed digest or separator;
20. missing target file;
21. symlink target;
22. wrong target digest;
23. stale RM digest from the historical ledger;
24. altered historical evidence bytes;
25. protected builder path injection.

Mutation tests must operate on in-memory copies or temporary directories and
must not modify repository files.

## 9. Verification and certification gates

Before certification, the repository owner must run and preserve exact results
for:

```text
python3 scripts/rcc002/verify_s8rr003_normative_ledger.py
python3 -m compileall -q rcc002 scripts/rcc002 tests/rcc002
python3 -m unittest tests.rcc002.test_s8rr003_normative_ledger -v
python3 -m unittest discover -s tests/rcc002 -p 'test_*.py'
python3 -m unittest discover -s tests/regression -p 'test_*.py'
git diff --check
```

Certification must additionally verify:

- exactly five correction payload files changed;
- the old ledger historical copy has the required fixed SHA-256;
- the new ledger has exactly 145 entries and verifies 145/145;
- all pre-existing files outside the root ledger remain byte-identical;
- this proposal and the triggering readiness review remain byte-identical;
- no S8 production code or dataset was created;
- the protected builder remains untouched and outside the staged set.

## 10. Independent review obligations

Independent scientific and architecture review must verify all of the
following before candidate certification:

1. the old root ledger really was authoritative for the certified
   S8BCP-001 Revision 2 normative bundle;
2. the historical evidence copy is byte-exact and preserves that meaning;
3. the 145-path union arithmetic and only-overlap claim are independently
   reproduced;
4. all 29 newly unique S8-RR-002 output paths are present;
5. all six S8-RR-003 paths are present;
6. the exact-scope design has no circular hash dependency;
7. the freeze boundary for later review and certification evidence is clear;
8. the verifier rejects all required mutations before reporting `PASS`;
9. the correction changes only the five permitted payload files;
10. no scientific formula, deterministic dataset value or S8 behavior changes.

Approval of this proposal authorizes only generation of the focused five-file
correction candidate. It does not authorize controlled commit until that
candidate is independently re-reviewed and certified.

## 11. Controlled sequence

The required sequence is:

1. commit and push this proposal alone;
2. obtain independent scientific and architecture review of the proposal;
3. if approved, generate only the five-file correction candidate;
4. execute the verifier, focused tests and full regression gates;
5. obtain independent candidate review;
6. certify the exact staged candidate;
7. commit and push the certified correction;
8. regenerate the certified source archive and S8 implementation input;
9. repeat S8 implementation-readiness review;
10. begin S8 implementation only if that later review states explicit
    `READY` and grants implementation authorization.

Any rejection or material finding returns the process to the relevant review
step. Findings must not be silently repaired after approval without another
independent review of the changed candidate.

## 12. Explicit exclusions

This correction must not:

- create `rcc002/s8/` or any S8 production module;
- generate, publish or claim a real dataset;
- change S0-S7 formulas, schemas or deterministic values;
- change RM `0.9.0`, Dataset Manifest Schema `1.0.1` or its fixtures;
- alter any historical ledger or historical review artifact in place;
- broaden the root ledger into an undocumented complete-repository inventory;
- use directory traversal as the normative scope definition;
- include the root ledger in its own entries;
- touch the protected untracked builder.

## 13. Acceptance criteria

`S8-RR3-B01` is eligible for closure only when all of the following are true:

- the old root ledger is preserved byte-for-byte under the required versioned
  evidence path;
- the successor root ledger has the approved 145-path exact scope;
- the successor ledger verifies 145/145 against current certified bytes;
- RM `0.9.0` has the exact certified hash in the successor ledger;
- the versioned scope, verifier and focused tests pass independent review;
- the exact five-file payload is certified, committed and pushed;
- a regenerated implementation input contains the corrected root ledger;
- a later repeated S8 readiness review independently returns `READY`.

Until all criteria are met:

```text
S8 IMPLEMENTATION READINESS: NOT READY
S8 IMPLEMENTATION AUTHORIZATION: DENIED
DATASET PUBLICATION AUTHORIZATION: DENIED
```

## 14. Proposed decision

Approve the focused normative-ledger lifecycle and integrity correction as
specified above for independent scientific and architecture review.

This proposal itself makes no repository change and grants no S8 production
authority.
