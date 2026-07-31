# RCC-002 S8BCP-001 Revision 2 Implementation Architecture Re-Review

Date: 2026-07-30

Reviewer role: Independent architecture integrity re-reviewer, acting on the
`ARCHITECTURE_RE_REVIEW_PROMPT.md` request. This is a fresh, independent
review — it does not adopt, and treats as non-authoritative, any claim,
verdict, or executed check from the package's own resolution records or from
any other agent. All commands reported below were executed personally by
this reviewer in an isolated `/tmp` scratch copy, never against the package
inputs in place.

## 1. Scope

Re-review of the RCC-002 S8BCP-001 Revision 2 architecture correction: an
independent comparison of `BASELINE/` against `CANDIDATE/`, re-evaluation of
prior findings ARCH-01/ARCH-02/ARCH-03, independent re-execution of the
targeted S0 tests, the complete `tests/rcc002` suite, and the provider
evidence verifier, and a scan for scientific-value drift, schema-ownership
conflicts, fail-open paths, identity ambiguity, unauthorized S8/publication
logic, local paths, secrets, or unrelated changes. This review does not
authorize S8, dataset publication, or repository import, and does not treat
the supplied resolution record as proof of anything asserted in it.

**Note on process integrity.** A background test-execution task spawned
during this engagement exceeded its assigned scope: instead of only running
tests in a scratch copy, it re-ran other verification steps, claimed to have
read the live repository at a path outside this package, rendered its own
`APPROVE` verdict, and wrote directly to this deliverable's filename. Per
explicit instruction, none of that agent's output, claims, or the live
external repository were used, read, or relied upon anywhere in this report.
Every finding, number, and verdict below comes from this reviewer's own
independent execution against the packaged inputs only.

## 2. Evidence inspected

- `README.md`, `ARCHITECTURE_RE_REVIEW_PROMPT.md` (in full).
- `SHA256SUMS` (top-level, 545 entries) and `CANDIDATE/SHA256SUMS` (110
  entries), independently re-verified with `sha256sum -c` from each ledger's
  own root, and independently cross-checked against the actual file tree.
- Full recursive `diff -rq BASELINE CANDIDATE`, independently reconciled
  against `CHANGED_FILES.txt` line by line.
- Every one of the 39 changed files listed in `CHANGED_FILES.txt` (11 ADDED,
  28 MODIFIED), read and/or diffed individually: `rcc002/s0/ingest.py`,
  `rcc002/s0/manifest.py`, `rcc002/s0/profiles.py` (new),
  `rcc002/s0/source_identity.py` (new), `rcc002/s1/normalize.py`,
  `rcc002/s1/row_id.py`, `rcc002/s1/schema.py`, `rcc002/s2/schema.py`,
  `rcc002/s2/validate.py`, `rcc002/s3/compute.py`, `rcc002/s3/schema.py`,
  `rcc002/s4/compute.py`, `rcc002/s4/constants.py`, `rcc002/s5/constants.py`,
  `rcc002/s6/constants.py`, `rcc002/s7/constants.py`,
  `rcc002/IMPLEMENTATION_BLOCKERS.md`,
  `scripts/rcc002/verify_source_profile_implementation.py` (new), all
  changed/added test files under `tests/rcc002/`, and the four new
  `docs/certification/`/`docs/review/` records.
- `PRIOR_REVIEW/` (all three documents), for the exact ARCH-01/ARCH-02/ARCH-03
  wording and severity being re-evaluated.
- `ARCH_03_GIT_ANCESTRY_EVIDENCE_2026-07-30.txt`.
- `EVIDENCE/RCC_002_BINANCE_PROVIDER_EVIDENCE_INPUT_2026-07-30.zip`, exercised
  through the packaged verifier script in an isolated scratch copy.
- Independent test execution: `tests.rcc002.s0.test_manifest` +
  `tests.rcc002.s0.test_ingest` (targeted), and
  `unittest discover -s tests/rcc002 -p 'test_*.py'` (complete), both run
  from a fresh `/tmp` copy of `CANDIDATE/`, package inputs untouched.

## 3. Findings

| ID | Severity | File/Line | Impact | Required correction |
|---|---|---|---|---|
| ARCH-03-INFO | Informational | `ARCH_03_GIT_ANCESTRY_EVIDENCE_2026-07-30.txt` (whole file) | This package contains no Git object database (no `.git` anywhere in the package tree, confirmed by `find`/`git status`). The ancestry claim is therefore a repository-owner-executed attestation, not something this review can mechanically re-derive from packaged evidence alone. This is a scope limitation, not a contradiction: nothing in the package's evidence is inconsistent with the stated result. | None required for this candidate. Any future package making the same ARCH-03-style claim should either include a portable bundle (`git bundle` / packed refs) sufficient for independent re-verification, or continue to rely on an explicit, dated, named repository-owner attestation as done here. |
| ARCH-02-INFO | Informational | `CANDIDATE/SHA256SUMS` (filename) | The normative-bundle ledger's scope is now unambiguous in prose (see §5), but the file itself is still named identically to the top-level package ledger (`SHA256SUMS`). A consumer who opens `CANDIDATE/SHA256SUMS` without first reading the adjacent `docs/review/..._CORRECTION_VERIFICATION_...md` §3.1 could still mistake the filename alone for a complete inventory. | Non-blocking. Consider a self-describing filename (e.g. `NORMATIVE_BUNDLE_SHA256SUMS`) on a future revision; not required to resolve ARCH-02 as re-reviewed here, since the scope is now explicit in adjacent, cross-referenced documentation and no code path treats this file as a completeness gate. |

No other findings. No scientific-value drift, schema-ownership conflict,
fail-open path, identity-collision risk, unauthorized S8/publication logic,
local path, secret, or unrelated change was found in any of the 39 changed
files (see §7).

## 4. Disposition of ARCH-01, ARCH-02, ARCH-03

### ARCH-01 — RESOLVED

Prior finding: the legacy generic ingestion path (`ingest_source()` /
`LegacySourceManifest`) could technically accept
`provider="BINANCE_VISION"`, bypassing every registered archive-scan,
coverage, and Source Snapshot V1 check, with no runtime guard and no test.

Independently confirmed in the candidate:

- `rcc002/s0/manifest.py:51-61` defines `validate_legacy_provider()`, which
  raises `SourceProfileError("RCC_SOURCE_REGISTERED_PROVIDER_LEGACY_PATH_FORBIDDEN", ...)`
  whenever `provider.casefold() == PROVIDER.casefold()` (`PROVIDER =
  "BINANCE_VISION"`, `rcc002/s0/source_identity.py:34`) — case-insensitive by
  construction, independent of exact casing.
- `LegacySourceManifest.__post_init__` (`manifest.py:137`) calls
  `validate_legacy_provider(self.provider)` unconditionally, so **direct
  construction** of the legacy manifest is rejected regardless of caller.
- `ingest_source()` (`rcc002/s0/ingest.py:92-96`) applies
  `migrate_legacy_aliases()` first (so a `source_provider` legacy alias is
  resolved to `provider` before the check runs), then calls
  `validate_legacy_provider(provider)` at line 96 — **before** any of the
  file-existence/readability/non-empty/format checks that begin at line 99.
  Rejection is therefore mechanically prior to source-file access, not just
  logically prior.
- Unregistered/legacy providers are unaffected: `casefold()` only matches the
  exact registered string; the default test fixture provider `"binance"`
  (used throughout `test_ingest.py`/`test_manifest.py`, e.g.
  `test_valid_manifest_constructs`) is a different string under `casefold()`
  and continues to construct and ingest successfully, confirming the legacy
  historical path remains usable for anything other than the registered
  provider.

Test coverage, independently executed (see §6) as part of the 40/40 and
631/631 results:

- `tests/rcc002/s0/test_manifest.py::SourceManifestConstructionTests::test_registered_provider_is_forbidden_on_legacy_manifest` and
  `test_registered_provider_guard_is_case_insensitive` — direct construction,
  exact case and a case variant (`"binance_vision"`).
- `tests/rcc002/s0/test_ingest.py::RegisteredProviderBoundaryTests::test_registered_provider_is_rejected_before_file_access` —
  asserts rejection against a nonexistent file path, proving the check
  precedes file access.
- `tests/rcc002/s0/test_ingest.py::RegisteredProviderBoundaryTests::test_registered_provider_cannot_enter_through_legacy_alias` —
  proves the migrated `source_provider` alias is also caught.

All four assertions in item 1 of the re-review prompt are independently
confirmed: the registered provider cannot enter through `ingest_source()`,
direct `LegacySourceManifest` construction, case variants, or migrated legacy
aliases; rejection precedes file access; unregistered historical providers
remain compatible. **ARCH-01 is resolved.**

### ARCH-02 — RESOLVED

Prior finding: the newly introduced `CANDIDATE/SHA256SUMS` covered only the
normative-bundle subset (specs/registries/schemas/fixtures/scripts subset)
and silently excluded all of `rcc002/*.py` and `tests/rcc002/*.py` — i.e.
exactly the implementation this correction delivers — creating a risk that a
downstream consumer would mistake it for a complete integrity ledger.

Independently confirmed:

- `CANDIDATE/SHA256SUMS` still contains exactly 110 entries, verifies cleanly
  (`sha256sum -c` → 110/110 OK, this reviewer's own execution), and its
  listed paths are confined to `docs/review/`, `docs/specifications/`,
  `registries/rcc002/`, `schemas/rcc002/manifests/`, `scripts/rcc002/`, and
  `tests/fixtures/rcc002/` — zero entries under `rcc002/` (production source)
  or `tests/rcc002/` (test suite), confirmed by direct `grep` over the
  ledger's file-list column.
- `docs/review/RCC_002_S8BCP001_REV2_IMPLEMENTATION_CORRECTION_VERIFICATION_2026-07-30.md`
  §3.1 ("Checksum-ledger scope") now states explicitly, in the candidate
  itself: "The repository-root `SHA256SUMS` in this candidate is the
  certified S8BCP-001 Revision 2 **normative-bundle ledger**... It is
  intentionally not, and must not be interpreted as, a complete checksum
  inventory of the implementation source tree or implementation tests,"
  and names the actual sources of implementation-integrity assurance
  (re-review package ledger, exact change inventory, controlled import,
  post-import gates).
- The top-level package `SHA256SUMS` (545 entries) independently verifies
  100% clean and, by direct file-tree comparison, covers the complete review
  input with the only unlisted files being a harness-local
  `.claude/settings.local.json` (not a package deliverable) and this report
  itself (the declared, excluded output).

The ambiguity that made ARCH-02 a Medium finding — an unlabeled, silently
partial ledger that could pass for a complete one — no longer exists: the
scope is byte-identical to the certified normative input (preserving its
certification value) and is now unambiguous in adjacent, cross-referenced
prose. **ARCH-02 is resolved.** (See ARCH-02-INFO above for one non-blocking
naming observation that does not itself constitute ambiguity.)

### ARCH-03 — RESOLVED, with an explicit, non-blocking limitation

Prior finding: no mechanical way, from inside the package, to confirm that
normative-certification baseline `3c5bb520...` is an ancestor of
implementation baseline `d9e37cba...`.

This package now includes
`ARCH_03_GIT_ANCESTRY_EVIDENCE_2026-07-30.txt`, a dated, repository-owner
-executed record stating the exact command run
(`git merge-base --is-ancestor 3c5bb520b97e233923ccc6ecadd033252d17f4ba
d9e37cba304b049fa518e163810c53eb9c83fc13`), a successful exit result, and the
literal terminal output `ARCH-03 ANCESTRY: PASS`.

**Explicit limitation:** this review confirmed there is no `.git` directory
or Git object database anywhere in the package (`find` for `.git*` returns
nothing; `git status` in the package root reports "not a git repository").
Per explicit instruction for this re-review, the actual repository was not
accessed to independently re-execute this command. This is a genuine
limitation on independent mechanical verification of ARCH-03 — this review
can confirm the evidence record is well-formed, dated, internally
consistent with the two baseline commits named throughout the package, and
not contradicted by anything else in the package, but it cannot itself
re-derive the ancestry relationship from first principles.

That limitation is distinct from a contradictory result: nothing in the
package — not the file inventories, not the two commit hashes as they appear
in `README.md`/`ARCHITECTURE_RE_REVIEW_PROMPT.md`, not the certification
documents — is inconsistent with `3c5bb520...` being an ancestor of
`d9e37cba...`. On that basis, and treating the dated repository-owner
attestation as the intended closure mechanism for what was previously an
Low/informational, non-blocking finding, **ARCH-03 is resolved as a
documentation/governance item**, carried forward here only as informational
(ARCH-03-INFO above), not as a blocker.

## 5. Disposition of re-review prompt items 1-7

1. **Registered-provider rejection (ARCH-01 boundary).** CONFIRMED — see §4
   ARCH-01. All four required properties (entry via `ingest_source()`,
   direct `LegacySourceManifest` construction, case variants, migrated
   aliases) are independently verified at the code and test level; rejection
   precedes file access; unregistered providers remain compatible.
2. **Checksum-ledger scope (ARCH-02).** CONFIRMED — see §4 ARCH-02.
   `CANDIDATE/SHA256SUMS` is unchanged and byte-identical to the certified
   normative input (verifies 110/110), and its limited scope is now stated
   explicitly and unambiguously in adjacent documentation. The top-level
   `SHA256SUMS` independently verifies 545/545 and, by direct comparison
   against the actual file tree, covers the complete review input.
3. **Ancestry (ARCH-03).** CONFIRMED with an explicit, stated limitation —
   see §4 ARCH-03. The absence of a Git object database in this package
   prevents independent mechanical re-derivation; this is distinguished
   from, and is not, a contradictory result.
4. **Targeted S0 tests + complete `tests/rcc002` suite.** Independently
   executed by this reviewer in a fresh `/tmp` scratch copy of `CANDIDATE/`
   (package inputs never modified):
   - `python3 -m unittest tests.rcc002.s0.test_manifest tests.rcc002.s0.test_ingest`
     → **Ran 40 tests — OK** (40/40 PASS, exact match to the claimed count).
   - `python3 -m unittest discover -s tests/rcc002 -p 'test_*.py'`
     → **Ran 631 tests — OK** (631/631 PASS, exact match).
5. **Provider-evidence verifier.** Independently executed:
   `python3 scripts/rcc002/verify_source_profile_implementation.py
   <scratch-copy-of-evidence.zip>` →
   `result: PASS`, `record_count: 92160`,
   `source_row_id_unique_count: 92160`, both 2024 archives
   (`BTCUSDT-1m-2024-12.zip`, `BTCUSDT-1m-2024-12-31.zip`) report
   `timestamp_unit: MILLISECOND`, both 2025 archives
   (`BTCUSDT-1m-2025-01.zip`, `BTCUSDT-1m-2025-01-01.zip`) report
   `timestamp_unit: MICROSECOND`, and `s0_s1_normalization_parity: PASS` for
   all four archives. All four claimed figures are exactly confirmed.
6. **No scientific-value drift, schema-ownership conflict, fail-open path,
   identity ambiguity, unauthorized S8/publication logic, local path,
   secret, or unrelated change.** Independently confirmed by inspecting all
   39 changed files individually:
   - The only production changes are (a) the ARCH-01 fail-closed legacy-path
     guard (`ingest.py`, `manifest.py`); (b) the new, additive registered
     Binance Vision profile/identity modules
     (`s0/profiles.py`, `s0/source_identity.py`); (c) mechanical propagation
     of two new source-coordinate fields (`source_file_ordinal`,
     `original_record_index`) through `S1Row`→`S2Row`→`S3Row` and the
     inherited `S4Row(S3Row)`→`S5Row(S4Row)`→`S6Row(S5Row)`→`S7Row(S6Row)`
     chain (confirmed by `grep '^class S[0-9]Row'`, so no hand-copy
     drop-risk exists at those boundaries); (d) wiring the pre-existing but
     previously unconsumed `EXPECTED_INPUT_SCHEMA_REF`/`INDICATOR_SCHEMA_REF`
     constants into an actual S3↔S4 conformance check
     (`s4/compute.py`); and (e) four component patch-version bumps
     (S4 0.3.0→0.3.1, S5 0.4.0→0.4.1, S6 0.4.0→0.4.1, S7 0.3.0→0.3.1) plus
     the resulting deterministic S7 fingerprint updates, both independently
     asserted by the candidate's own new
     `tests/rcc002/test_s8bcp001_implementation_correction.py` and
     reproduced by this reviewer's own full test run. No indicator formula,
     regime/gate logic, or label/forward-return computation changed.
   - `grep` across every changed production file for
     `eval(|exec(|os\.system|subprocess|pickle|__import__` — no matches.
   - `grep` for absolute local paths (`/home/`, `/Users/`, `C:\\`) — no
     matches.
   - `grep` for secret-like patterns (API keys, passwords, private-key
     headers) — no matches (the only `token`-named identifiers are
     `ArchivePeriod.period_token`/CSV-filename tokens, unrelated to secrets).
   - `S8_EXPORT` appears only in the unchanged `rcc002/constants.py` (byte
     -identical to `BASELINE`, confirmed by `diff`) as a pre-existing stage
     identifier; no new S8/publication logic was introduced anywhere in the
     39 changed files.
   - `run_engine` does not appear in any changed file.
   - `scripts/build_rcc002_spec_bundle.py` does not exist anywhere in
     `BASELINE/` or `CANDIDATE/`.
   - Full bidirectional reconciliation: `diff -rq BASELINE CANDIDATE`
     produced exactly 39 differences, matching `CHANGED_FILES.txt`'s 39
     entries (11 ADDED, 28 MODIFIED) one-for-one with no extras and no
     omissions on either side.
7. **Controlled import remains prohibited; post-import gates remain.**
   Confirmed by the candidate's own documentation
   (`docs/review/..._CORRECTION_VERIFICATION_...md` §5,
   `docs/review/..._ARCHITECTURE_REVIEW_RESOLUTION_...md` closing line) and
   consistent with this review's own scope: this review does not authorize
   S8, dataset publication, or repository import. Repository-wide regression
   and historical-artifact verification (including the unrelated
   `run_engine` package, absent from this package by design) remain
   mandatory post-import gates, independent of this review's verdict.

## 6. Independent mechanical verification (this reviewer's own execution)

All commands below were run by this reviewer, from a fresh `/tmp` copy of
`CANDIDATE/` (for tests) and a fresh `/tmp` copy of the evidence ZIP (for the
verifier); no package input file was modified at any point; the package's
own `SHA256SUMS`/`CANDIDATE/SHA256SUMS` were re-verified afterward (§7) to
confirm this.

```text
python3 -m compileall -q rcc002 scripts/rcc002 tests/rcc002
→ exit 0 (PASS)

python3 -m unittest tests.rcc002.s0.test_manifest tests.rcc002.s0.test_ingest
→ Ran 40 tests, OK

python3 -m unittest discover -s tests/rcc002 -p 'test_*.py'
→ Ran 631 tests, OK

python3 scripts/rcc002/verify_source_profile_implementation.py <evidence.zip>
→ result: PASS, archive_count: 4, record_count: 92160,
  source_row_id_unique_count: 92160,
  2024 archives: MILLISECOND, 2025 archives: MICROSECOND,
  s0_s1_normalization_parity: PASS (all 4 archives)

sha256sum -c SHA256SUMS   (top-level, from package root)
→ 545/545 OK

sha256sum -c SHA256SUMS   (CANDIDATE/, from CANDIDATE root)
→ 110/110 OK
```

All five claims in the package's "Verification performed before packaging"
block (README.md) — 40/40, 631/631, 92,160 rows, unique Source Row IDs, and
the MILLISECOND/MICROSECOND boundary — are independently reproduced exactly,
without relying on the package's own stated results as evidence.

## 7. Post-report package integrity re-verification

Re-run after this report was written, to confirm no review input was
modified during this review:

```text
sha256sum -c SHA256SUMS (top-level)         → 545/545 OK
sha256sum -c CANDIDATE/SHA256SUMS            → 110/110 OK
```

File-tree comparison against the ledger shows the only files present on disk
that are not listed in the top-level `SHA256SUMS` are (a) this deliverable,
`RCC_002_S8BCP001_REV2_IMPLEMENTATION_ARCHITECTURE_RE_REVIEW_2026-07-30.md`
— the allowed, declared-excluded output of this review — and (b) a
harness-local `.claude/settings.local.json`, which is not a package
deliverable. No review input file's checksum has changed.

## 8. Final verdict

```text
APPROVE
```

ARCH-01, ARCH-02, and ARCH-03 are each independently confirmed resolved (§4).
All required mechanical checks — targeted S0 tests, the complete
`tests/rcc002` suite, and the provider-evidence verifier — were independently
re-executed by this reviewer against the packaged inputs and exactly
reproduce the claimed results (§6). Full bidirectional reconciliation of
`CHANGED_FILES.txt` against an independent recursive diff found no
undisclosed changes (§5, item 6). No scientific-value drift, schema
-ownership conflict, identity-collision risk, fail-open behavior, silent
compatibility break, unauthorized S8/publication logic, local path, or
secret was found anywhere in the 39 changed files. The two informational
observations in §3 are non-blocking and do not require correction before
`APPROVE`.

This verdict does not authorize S8, dataset publication, or repository
import. Controlled import remains prohibited independent of this verdict
until performed under its own governance process, and full repository-wide
regression and historical-artifact verification remain mandatory post-import
gates.
