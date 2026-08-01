# RCC-002 S8-RR-002 Correction Candidate Certification Decision

## Document control

| Field | Value |
|---|---|
| Certification ID | `RCC-002-S8RR002-CAND-CERT-001` |
| Decision date | `2026-08-01` |
| Repository branch | `main` |
| Repository baseline | `b5278e8549fab0e72ffd6ffc53f09c5c53d4305a` |
| Correction ID | `RCC-002-S8RR002-BCP-001-REV2` |
| Readiness findings | `S8-RR2-B01`, `S8-RR2-B02` |
| Candidate architecture finding | `S8RR002-CAND-ARCH-001` - closed |
| Status | `CERTIFIED FOR CONTROLLED COMMIT` |

## 1. Certification decision

The reviewed RCC-002 S8-RR-002 blocker-correction candidate is certified for
controlled commit and push.

This decision certifies exactly the 30-file correction payload staged on top
of:

```text
b5278e8549fab0e72ffd6ffc53f09c5c53d4305a
```

The certification decision itself is a separate governance artifact and is
not included in the 30-file payload identity in Section 3.

This certification does not authorize:

- S8 production implementation;
- dataset generation or publication;
- live trading or production deployment;
- any file outside the certified payload and this certification decision.

## 2. Certified scope

The certified candidate implements the approved Revision 2 correction by:

1. defining `DatasetManifest.views` as the exact ordered six-view RCC-002
   registry snapshot;
2. defining `DatasetManifest.specification_profile` as the exact ordered
   seven-document current specification profile;
3. introducing Dataset Manifest Schema `1.0.1` without modifying historical
   Dataset Manifest Schema `1.0.0` or its fixtures;
4. updating Reproducibility and Manifest to `0.9.0` and correcting its
   normative Dataset Manifest example;
5. providing two distinct positive `1.0.1` fixtures, 21 negative fixtures,
   and a machine-readable case ledger;
6. pinning the Draft 2020-12 review dependency locally and outside production
   requirements;
7. defining and enforcing an exact versioned 11-input and 30-output verifier
   scope;
8. providing mechanical verification and independent focused mutation tests.

No S0-S7 scientific formula, leakage rule, deterministic data value or
production implementation is changed by this correction.

## 3. Certified payload identity

```text
staged_file_count=30
staged_patch_sha256=f526c4fb7908a96a251e6e60cb1657e662fc7b601518f6313d9ec36cba3234ba
staged_file_list_sha256=7d6c02596c775954bbad2365cc47f71c0c930bb3dab2b7b2dd74c08ed7b6bd04
```

The patch identity was computed from:

```text
git diff --cached --binary --no-ext-diff
```

The file-list identity was computed from the lexicographically sorted output
of:

```text
git diff --cached --name-only
```

The protected repository-local untracked file
`scripts/build_rcc002_spec_bundle.py` is excluded from the certified payload
and remains unstaged.

## 4. Independent review evidence

| Evidence | Verdict | SHA-256 |
|---|---|---|
| `RCC_002_S8RR002_CORRECTION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` | `REJECT` - superseded after focused repair | `bc78bf2e0f6b77ab0df1a3a6b32e024fb84f6afe116931a95ca6b9a7309d5054` |
| `RCC_002_S8RR002_CORRECTION_CANDIDATE_CHATGPT_INDEPENDENT_RE_REVIEW_2026-08-01.md` | `APPROVE` | `1458f771b55bcae7da2ae2616a40b6718ec1337f0480a4a2f717a96b61157397` |
| `RCC_002_S8RR002_CORRECTION_CANDIDATE_GEMINI_INDEPENDENT_RE_REVIEW_2026-08-01.md` | `APPROVE` | `9870adae473c6d5ada8747a61f0ad5ae2b1ffd2d275f41284ebbdda8a9d8ef02` |

The initial ChatGPT review accepted the substantive normative, schema and
fixture correction but rejected incomplete scope enforcement and an
incomplete candidate inventory under `S8RR002-CAND-ARCH-001`.

The focused repair changed only:

- the versioned scope manifest;
- the correction verifier;
- the focused and mutation test file.

Both independent re-reviews conclude that
`S8RR002-CAND-ARCH-001` is closed and identify no remaining blocking, major
or minor finding.

## 5. Live repository verification

The following gates were executed in `/home/benja/projects/sniper-bot` after
both independent approvals and before this decision:

| Gate | Result |
|---|---|
| Branch | `main` |
| Baseline `HEAD` | `b5278e8549fab0e72ffd6ffc53f09c5c53d4305a` |
| Baseline `origin/main` | exact match |
| Review dependency | `jsonschema==4.26.0` |
| Correction verifier | `PASS` |
| Candidate SHA-256 inventory | `30/30` |
| Registered views | `6/6` |
| Specification profile | `7/7` |
| Positive fixtures | 2 files and 2 distinct payloads |
| Negative fixtures | `21/21` rejected |
| Targeted Python compilation | `PASS` |
| RCC-002 unit tests | `659/659 PASS` |
| TD-005 regression tests | `170/170 PASS` |
| `git diff --cached --check` | `PASS` |
| Unstaged tracked changes | none |
| Staged payload file count | exactly 30 |
| Staged patch identity | exact match to Section 3 |
| Staged file-list identity | exact match to Section 3 |
| Protected builder | untracked and unstaged |

## 6. Certified deterministic identities

| Artifact | SHA-256 |
|---|---|
| Reproducibility and Manifest `0.9.0` | `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1` |
| Versioned verifier scope | `7253c44c9d342e6a26e356d07f1ca37efcb43b843d93636e9e7e1594530c840c` |
| Dataset Manifest Schema `1.0.1` | `52380b9b6c9244308e03fc3c900d48b118735aa84e5e634d0a83396822e674a3` |
| Correction verifier | `2c67bfddc0b99a3a07497240a2e6c26dbc2dd41674ade898eb00b25ef38d9335` |
| Focused and mutation tests | `2b977dc2952058ee1381723332786fcd252534c0a8de560c64af932fb46abaf4` |
| Review dependency pin | `756cc9e506ae4ee1a6f6c0507088b5cfc0dc8ba350fb2d2d46f1ffa72033adb6` |

Historical Dataset Manifest Schema `1.0.0`, its two positive fixtures and
Stage Manifest Schema `1.0.0` retain their certified immutable hashes.

## 7. Finding disposition

| Finding | Final disposition |
|---|---|
| `S8-RR2-B01` | Corrected and independently approved |
| `S8-RR2-B02` | Corrected and independently approved |
| `S8RR002-CAND-ARCH-001` | Closed by exact scope and inventory repair |

No blocking, major or minor finding remains open within the certified scope.

## 8. Conditions of effectiveness

This certification becomes effective only if:

1. this certification file is added with mode `100644`;
2. the final staged state contains the certified 30-file payload plus only
   this certification decision, for exactly 31 staged files;
3. the 30-file payload patch and file-list identities remain exactly those in
   Section 3 when the certification file is excluded from the calculation;
4. `git diff --cached --check` remains clean;
5. the commit has parent
   `b5278e8549fab0e72ffd6ffc53f09c5c53d4305a`;
6. the commit is pushed to `origin/main`;
7. local `HEAD` and `origin/main` match after push;
8. `scripts/build_rcc002_spec_bundle.py` remains untracked and unstaged.

Any change to the certified 30-file payload invalidates this decision until
the payload identity and all affected gates are re-established.

## 9. Required next sequence

After the certified commit and push:

1. regenerate the S8 implementation input from the new certified `HEAD`;
2. repeat the S8 implementation-readiness review;
3. begin S8 production implementation only after an explicit `READY`
   verdict.

Dataset publication remains separately prohibited.

## 10. Final decision

```text
CERTIFIED
```

The RCC-002 S8-RR-002 correction candidate is approved for controlled commit
and push under the conditions in Section 8.
