# RCC-002 S8-RR-003 Normative Ledger Proposal Revision 2 Independent Re-Review

## 1. Document control

| Field | Value |
|---|---|
| Report ID | `RCC-002-S8RR003-NLBCP-001-REV2-INDEPENDENT-RE-REVIEW-001` |
| Review date | `2026-08-01` |
| Review class | Independent scientific and architecture re-review |
| Reviewer | Independent Claude-based review agent |
| Working directory | `/mnt/c/Users/benja/Downloads/sniper-bot-1342aa1-s8rr003-proposal-rev2-review` |
| Repository baseline (supplied) | `1342aa1007cc0b15c41e9379a09e9a6217a60e7f` |
| Repository baseline verification | Not independently reproducible: no `.git` directory exists in the extracted snapshot, so this commit identity cannot be cryptographically re-derived from within the snapshot. This mirrors the prior review's `IR-F04` and is not a new defect. |
| Review package (supplied name) | `RCC_002_S8RR003_NORMATIVE_LEDGER_PROPOSAL_REV2_REVIEW_INPUT_2026-08-01.zip` |
| Review package SHA-256 (supplied) | `4a1ec4db4b03b65d78d127e29ad50a3df9708fb4808249520921f3e460f1c095` |
| Review package verification | Not independently reproducible: no ZIP archive is present in the extracted snapshot (the working directory is itself the already-extracted content), so the archive-level digest cannot be recomputed from the snapshot. The same limitation was documented and accepted by the controlling rejecting review. |
| Primary target | `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md` |
| Target SHA-256 (supplied) | `d81166a734fad826b96737d4cc9eddca621017b0497ca22b90b5102817f26554` |
| Target SHA-256 (independently computed) | `d81166a734fad826b96737d4cc9eddca621017b0497ca22b90b5102817f26554` -- MATCH |
| Controlling prior proposal | `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md` |
| Controlling prior proposal SHA-256 (independently computed) | `1cde003e451a4f2106314f8bad14365f2913b495a9b0a5d644226bfac7cf2504` (not separately supplied for comparison; recorded for traceability) |
| Controlling rejecting review | `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling review SHA-256 (supplied) | `c492efe58537c24c6c1fbb6efe2ccbcc1789f30d0d65c718d6e5284fc9c69a2a` |
| Controlling review SHA-256 (independently computed) | `c492efe58537c24c6c1fbb6efe2ccbcc1789f30d0d65c718d6e5284fc9c69a2a` -- MATCH |
| Findings under closure review | `IR-F01` (BLOCKER), `IR-F02` (MINOR), `IR-F03` (MINOR) |
| Final decision | `APPROVE` |

## 2. Exact scope and restrictions

This re-review evaluated only whether Revision 2 of the S8-RR-003
normative-ledger blocker correction proposal fully closes `IR-F01`, `IR-F02`
and `IR-F03` as raised by the controlling rejecting review, and whether
Revision 2 introduces any new contradiction, ambiguity, unverifiable
requirement, circular dependency, scope defect or unsafe authorization.

The review was conducted strictly within the following bounds:

- only the extracted snapshot at the working directory above was inspected;
- no file outside the snapshot was read, hashed, executed or searched for;
- the absence of `scripts/build_rcc002_spec_bundle.py` was confirmed only
  inside the snapshot, and no probe of the live repository was performed;
- no project file was created, modified, deleted, renamed or moved;
- no dependency was installed or updated;
- no network access or external browsing was used;
- no file was staged, committed or pushed;
- no S8 production code was created and no dataset was published;
- only passive read-only diagnostics (file reads, hashing, grep, and
  in-memory Python parsing/regex/arithmetic checks) were performed;
- exactly one review report was created outside the snapshot, at the
  required output path; no other filesystem write occurred.

## 3. Evidence inspected

The following snapshot artifacts were read and, where applicable,
independently hashed or parsed:

1. `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md`
   (original, rejected proposal) -- full text read, SHA-256 computed.
2. `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_INDEPENDENT_REVIEW_2026-08-01.md`
   (controlling rejecting review) -- full text read, SHA-256 computed and
   matched against the supplied value.
3. `docs/review/RCC_002_S8RR003_NORMATIVE_LEDGER_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-08-01.md`
   (Revision 2, target) -- full text read, SHA-256 computed and matched
   against the supplied value.
4. A full unified diff between the original proposal and Revision 2, to
   independently confirm the boundary of what Revision 2 actually changed.
5. Root `SHA256SUMS` (110 lines) -- read, parsed, hashed, and verified with
   `sha256sum -c`.
6. `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`
   (the 30-entry S8-RR-002 correction-candidate-output scope) -- read and
   parsed.
7. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
   (current RM `0.9.0`) -- hashed independently.
8. Directory listings of `docs/review/`, `docs/review/evidence/`,
   `scripts/rcc002/`, `tests/rcc002/`, `rcc002/` and the repository root, to
   confirm presence/absence of specific paths.
9. A snapshot-wide search for `build_rcc002_spec_bundle` (by filename and by
   text occurrence) to confirm the protected builder is absent and is
   referenced in the proposal only as an exclusion clause.

No file outside this list, and no file outside the snapshot, was consulted.

## 4. Independent results for every mandatory check

### 4.A Evidence integrity

- Target Revision 2 document SHA-256 independently computed as
  `d81166a734fad826b96737d4cc9eddca621017b0497ca22b90b5102817f26554`,
  matching the supplied Target SHA-256 exactly.
- Controlling rejecting review SHA-256 independently computed as
  `c492efe58537c24c6c1fbb6efe2ccbcc1789f30d0d65c718d6e5284fc9c69a2a`,
  matching the supplied Controlling Review SHA-256 exactly.
- The original proposal, the rejecting review and Revision 2 are all present
  in `docs/review/` and were read in full.
- The repository baseline commit hash and the review-package ZIP SHA-256
  cannot be reproduced from inside the extracted snapshot, because no `.git`
  history and no ZIP archive exist inside it. This is an expected property
  of a read-only extracted snapshot, not a defect, and mirrors the prior
  review's informational finding `IR-F04`.
- `scripts/build_rcc002_spec_bundle.py` was confirmed absent from the
  snapshot by filename search. The only textual occurrence of
  `build_rcc002_spec_bundle` anywhere in the inspected evidence is the
  exclusion clause in Revision 2 Section 6, which instructs that the file
  must not be read, hashed, inspected, executed, modified, staged,
  committed, packaged or deleted. The live repository was not probed.

### 4.B IR-F01 closure

The exact literal regex quoted in Revision 2 Section 5 item 3 (and
identically repeated in the Section 1.1 disposition table) is:

```text
^[0-9a-f]{64}  \./[^\\\r\n]+$
```

This was extracted byte-for-byte from the file (not retyped from the
proposal's prose) and confirmed identical at both locations in the document.

Independent regex-semantics derivation:

- `^` / `$` anchor the full line.
- `[0-9a-f]{64}` requires exactly 64 lowercase hexadecimal characters.
- the two literal space characters between `{64}` and `\.` require exactly
  two ASCII spaces.
- `\.` is an escaped period, i.e. a literal `.`; followed by literal `/`.
  Together this requires a literal `./` prefix.
- `[^\\\r\n]+` is a negated character class containing three escape
  sequences: `\\` (a literal backslash), `\r` (an actual CR byte), and `\n`
  (an actual LF byte). The class therefore excludes backslash, CR and LF,
  and admits one or more of any other character.

This was verified computationally (Python `re`, compiled from the exact
extracted bytes):

| Test input | Result |
|---|---|
| 64 lowercase hex + two spaces + `./docs/review/foo.md` | MATCH |
| 64 lowercase hex + two spaces + `./SHA256SUMS` | MATCH |
| Path containing a backslash (`docs\review\foo.md`) | NO MATCH (rejected) |
| Path containing an actual CR byte | NO MATCH (rejected) |
| Path containing an actual embedded LF byte | NO MATCH (rejected) |
| One space instead of two | NO MATCH (rejected) |
| Three spaces instead of two | NO MATCH (rejected) |
| Uppercase hex digest | NO MATCH (rejected) |
| Path missing the `./` prefix | NO MATCH (rejected) |

For comparison, the original (rejected) proposal's literal regex, extracted
the same way from its file, is:

```text
^[0-9a-f]{64}  \\./[^\\r\\n]+$
```

Compiled and tested against the same valid canonical line, this pattern
returns NO MATCH -- independently reproducing the rejecting review's finding
that the original grammar rejects every valid ledger line. The double
backslash before `.` (`\\.` = literal backslash + any character) and the
character class `[^\\r\\n]` (excluding backslash, the letter `r` and the
letter `n`, rather than CR/LF bytes) are both absent from the Revision 2
text; Revision 2 contains a single backslash before `.` and proper `\r`/`\n`
escapes inside the class.

Conclusion: the Revision 2 regex accepts the required canonical line and
rejects backslash paths and literal CR/LF bytes in the path, and the
double-escaped grammar from the rejected proposal is gone.

**IR-F01: CLOSED.**

### 4.C IR-F02 closure

Section 8 of Revision 2 was parsed programmatically. It contains a
contiguous, sequentially numbered list from item 1 to item 29 -- exactly 29
enumerated mutation cases, with no gaps or duplicate numbers.

Items 26-29 explicitly read:

```text
26. CRLF line endings;
27. missing final newline;
28. more than one final newline;
29. non-ASCII byte in the digest, separator or path.
```

These four items directly cover the three file-format invariants stated in
Section 5 item 1 (ASCII text, LF line endings, exactly one final newline):
item 29 exercises the ASCII requirement, item 26 exercises the LF-only
requirement, and items 27/28 exercise both directions of the "exactly one
final newline" requirement (too few and too many). This closes the gap the
controlling review identified, where none of the original 25 mutations
exercised these invariants.

**IR-F02: CLOSED.**

### 4.D IR-F03 closure

Revision 2 Section 4.3 adds an explicit paragraph:

```text
For this correction family, scope_schema_version is explicitly local to the
named scope_id. It does not identify a global JSON shape shared with other
RCC-002 verifier scopes. Therefore version 1 denotes the first schema of
RCC002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1, independently of the differently
shaped S8-RR-002 scope.
```

This directly and unambiguously states that `scope_schema_version` is a
per-`scope_id` local version, not a shared global common-schema version, and
explicitly distinguishes the new S8-RR-003 scope shape from the differently
shaped, pre-existing S8-RR-002 scope (independently confirmed to have a
structurally different JSON shape in
`docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`).
The reuse of the literal string `"1"` in both scope files no longer implies
any shared schema, because the convention is now explicit. No residual
ambiguity was found.

**IR-F03: CLOSED.**

### 4.E Scope and lifecycle correctness

The successor-ledger arithmetic was independently reproduced end to end
from the actual snapshot files (not from the proposal's assertions):

- Root `SHA256SUMS` contains exactly 110 lines, all matching the canonical
  entry grammar, all unique, already in strict ordinal (`LC_ALL=C`-equivalent)
  lexical order. Its own SHA-256 is `a34e5139dadfdfa9d72210ac12b733b0493b00c8396f8e48680634dfb5988e43`,
  matching the certified historical identity cited in Revision 2 Section 2
  and the `historical_ledger_sha256` value in the Section 4.3 metadata block.
- `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`
  contains exactly 30 unique entries in `correction_candidate_outputs`.
- The intersection of the 110-path set and the 30-path set contains exactly
  one path: `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`.
  This was independently computed as a set intersection, not read from
  prose.
- The six S8-RR-003 lifecycle paths listed in Revision 2 Section 4.2 are
  pairwise unique and disjoint from both the 110-path and 30-path sets.
- The union of all three sets, computed independently, contains exactly
  145 unique paths:

  ```text
  110 + 30 - 1 + 6 = 145
  ```

  This reproduces the proposal's arithmetic exactly, using only files
  physically present in the snapshot.
- 29 of the 30 S8-RR-002 outputs are newly unique relative to the 110-path
  historical set (`30 - 1 overlap = 29`), matching the "29 newly unique
  S8-RR-002 output paths" claim in Revision 2 Sections 10 and elsewhere.
- Of the six S8-RR-003 lifecycle paths, exactly two currently exist on disk
  (the triggering readiness review and this Revision 2 proposal itself),
  and the remaining four (the historical-evidence copy, the scope manifest,
  the verifier, and the test module) are correctly absent, because they are
  outputs of the not-yet-generated correction candidate. This is internally
  consistent with "this proposal itself makes no repository change."
- Revision 2's six-path list names only the Revision 2 proposal file, not
  the original (superseded) proposal file. Neither the original proposal
  nor the rejecting review appears anywhere in the 110-path set, the
  30-path set, or the six-path set. They are referenced only in Revision
  2's document-control header (`Supersedes`, `Controlling review` fields),
  confirming they are treated as historical Git-governance evidence outside
  the 145-entry successor ledger, exactly as Revision 2 Section 4.2 states
  in prose.
- Lexical order: the 110-path historical set is confirmed already sorted.
  Path safety: none of the 110, 30, or six paths contain an absolute-path
  prefix, a backslash, an empty path component, or a `..` component
  (independently checked programmatically).
- Uniqueness: all three source sets and their union are free of duplicates
  (145 unique paths, no repeats).
- Self-entry exclusion: `SHA256SUMS` (as `./SHA256SUMS` or bare) does not
  appear in any of the 110, 30, or six-path sets, confirming the "no
  self-hash" principle is upheld in the scope construction.
- Hash authority: the 30-path scope JSON and the six-path lifecycle list
  contain only paths, no embedded file hashes; hash authority remains
  solely with root `SHA256SUMS`, consistent with Section 4.3's separation
  of path membership from hash authority.
- No circular dependency: the scope manifest (a future output, one of the
  145) will contain paths but no hashes, so its own eventual inclusion in
  the ledger does not require the ledger's own future hash to be known in
  advance. The `SHA256SUMS` self-exclusion additionally rules out the
  ledger needing to hash itself.
- The future correction candidate is restricted to exactly five payload
  files (Section 6): `SHA256SUMS`, the historical-evidence copy, the scope
  manifest JSON, the verifier script, and the test module. This is
  unchanged from the original proposal and internally consistent with the
  six-path lifecycle set (four of the six lifecycle paths are among the
  five payload files; the fifth payload file, `SHA256SUMS`, is not part of
  the six-path lifecycle list because it is already accounted for via the
  "no self-hash" principle and the 110-path historical set's supersession).
- The protected builder, `scripts/build_rcc002_spec_bundle.py`, does not
  appear in the 110-path set, the 30-path set, the six-path lifecycle set,
  or the five-file payload list. Its only appearance anywhere in the
  inspected evidence is the exclusion clause in Section 6.
- A live `sha256sum -c SHA256SUMS` run against the current (pre-correction)
  repository tree independently reproduced the exact problem statement: 109
  entries verify `OK` and exactly one entry -- the RM specification --
  fails, because the current RM file hashes to
  `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1` while
  the still-unmodified root ledger records the stale
  `22d6460f16f7f70e677a40dcd4e428e3739d9bb37fb0f7340512cca1b1ebb382`. This
  confirms the underlying blocker condition is real and, as expected, still
  unresolved in the repository tree, since Revision 2 is a proposal only and
  makes no repository change.

### 4.F Authorization boundary

- Revision 2 Section 1, Section 10, Section 11 and Section 14 are unchanged
  from the original proposal in substance and explicitly state that
  approval authorizes only generation of the five-file correction
  candidate, not S8 implementation or dataset publication.
- Section 10 and Section 11 unchanged in substance require an independent
  candidate review and a certification step before controlled commit, and
  Section 11 item 9 requires repeating the S8 implementation-readiness
  review before S8 implementation may begin (item 10 requires an explicit
  `READY` result and explicit implementation authorization).
- Section 12 (explicit exclusions) and the closing statement of Section 14
  are unchanged from the original proposal and state that the proposal
  itself makes no repository change and grants no S8 production authority.
  This was independently confirmed by observing that none of the five
  future payload files or four future lifecycle-set files exist yet in the
  snapshot.

## 5. Closure assessment for IR-F01, IR-F02, IR-F03

| Finding | Original severity | Disposition claimed by Revision 2 | Independent re-derivation | Status |
|---|---|---|---|---|
| `IR-F01` | BLOCKER | CLOSED | Regex extracted byte-for-byte and compiled; matches canonical lines, rejects backslash/CR/LF; original double-escaped grammar independently confirmed absent | **CLOSED** |
| `IR-F02` | MINOR | CLOSED | Section 8 independently parsed: exactly 29 sequential items, with items 26-29 explicitly covering CRLF, missing final newline, extra final newline, and non-ASCII bytes | **CLOSED** |
| `IR-F03` | MINOR | CLOSED | Section 4.3 independently read: explicit, unambiguous statement that `scope_schema_version` is local to `scope_id`, not a global common-schema version | **CLOSED** |

All three findings that gated approval of the prior revision are
independently confirmed closed in Revision 2.

## 6. Scope/lifecycle assessment

The 145-entry successor-ledger contract is internally consistent and was
independently reproduced from the actual snapshot files, not from the
proposal's prose: 110 (historical) + 30 (S8-RR-002 outputs) - 1 (single RM
overlap) + 6 (S8-RR-003 lifecycle paths) = 145 unique, lexically orderable,
duplicate-free, path-safe entries, with `SHA256SUMS` correctly self-excluded
and the protected builder correctly absent from every scope category. The
six-path lifecycle set correctly substitutes the Revision 2 proposal path
for the superseded original proposal path without changing cardinality or
the 145-path union, and the original proposal and its rejecting review are
correctly excluded from the successor ledger as historical governance
evidence. No circular hash dependency exists, because the scope manifest
carries only paths (no hashes) and the ledger excludes itself.

## 7. New findings

One presentational (non-normative) observation was noted and is recorded
below for completeness, but it is not assessed as a defect:

- The illustrative six-path list in Revision 2 Section 4.2 is not itself in
  strict `LC_ALL=C` lexical order (the readiness-review filename sorts
  after the Revision 2 proposal filename under ordinal comparison, because
  `_` (0x5F) sorts after `R` (0x52) at the first differing character).
  Section 4.2 does not itself assert that this illustrative list is
  lexically ordered -- the lexical-order requirement is explicitly scoped
  to the `s8rr003_lifecycle_outputs` array inside the future scope
  manifest (Section 4.3) and to the final root ledger (Section 5 item 8),
  neither of which exists yet to be checked. This ordering was already
  present, unchanged, in the original (rejected) proposal's equivalent
  list and was not flagged by the controlling rejecting review. It is not
  a new defect introduced by Revision 2 and carries no impact given the
  absence of an explicit ordering claim at that location.

No new contradiction, ambiguity, unverifiable requirement, circular
dependency, scope defect or unsafe authorization was identified in
Revision 2 beyond the above non-defect observation. No blocker or major
finding from the controlling review was silently downgraded: `IR-F01`,
`IR-F02` and `IR-F03` are assessed CLOSED on independently reproduced
evidence, and `IR-F04`/`IR-F05` remain informational-only with no required
correction, consistent with Revision 2's own disposition table.

## 8. Confirmation of non-modification

No project file within the reviewed snapshot was created, modified,
deleted, renamed or moved during this review. No dependency was installed
or updated. No file was staged, committed or pushed. No network access or
external browsing was used. No S8 production code was created and no
dataset was generated or published. All verification was performed with
passive read-only commands (file reads, `sha256sum`, `grep`, `diff`, and
in-memory Python parsing/regex/arithmetic that read but never wrote
repository files). The protected file `scripts/build_rcc002_spec_bundle.py`
was confirmed absent from the snapshot by name search only; it was never
read, hashed, executed, or otherwise accessed. Exactly one new file was
created by this review: the present report, at the required output path
outside the snapshot.

## 9. Explicit approval boundary

This decision applies only to the Revision 2 S8-RR-003 normative-ledger
correction proposal contract. It does not:

- authorize generation of the five-file correction candidate on its own --
  candidate generation remains gated on this proposal's approval per the
  controlled sequence in Revision 2 Section 11;
- authorize S8 production implementation;
- authorize dataset publication;
- certify any future correction artifact;
- replace the later independent candidate review, certification, or the
  later repeated S8 implementation-readiness review that Revision 2 itself
  requires before S8 implementation may begin.

Revision 2 itself makes no repository change and grants no S8 production
authority; this was independently confirmed by observing that none of the
five payload files or four not-yet-existing lifecycle-set files exist in
the current snapshot tree.

## 10. Final decision and rationale

All three findings that blocked the prior revision are independently
confirmed closed: `IR-F01`'s ledger-line regular expression now compiles
and behaves exactly as specified (accepting canonical lines, rejecting
backslash paths and CR/LF bytes), `IR-F02`'s mutation-test contract now
enumerates exactly 29 cases including the four previously missing
file-format mutations, and `IR-F03`'s scope-schema-version convention is
now explicitly and unambiguously scoped per `scope_id`. The 145-entry
successor-ledger arithmetic, the single-overlap claim, the six-path
lifecycle set, the five-file payload boundary, path-safety, uniqueness,
self-hash exclusion, and protected-builder exclusion were all
independently reproduced from the snapshot's actual files rather than
accepted from the proposal's assertions, and all reproduced exactly as
claimed. The authorization boundary remains unchanged and correctly
narrow: Revision 2 authorizes only generation of the five-file correction
candidate, not S8 implementation or dataset publication, both of which
remain explicitly gated behind independent candidate review, certification,
and a later repeated S8 readiness review. No new blocking or major defect
was found; the single observation recorded in Section 7 is presentational,
pre-existing, and non-normative.

Because `IR-F01`, `IR-F02` and `IR-F03` are all demonstrably closed, the
145-entry lifecycle contract is internally consistent and independently
reproducible, and no new blocking or major defect remains, this proposal
Revision 2 satisfies the decision rule for approval.

APPROVE
