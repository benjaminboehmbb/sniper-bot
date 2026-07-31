# RCC-002 S8BCP-001 Revision 2 Implementation Certification Decision

Date: 2026-07-30

Status: CERTIFIED FOR CONTROLLED COMMIT

## 1. Certification scope

This decision certifies the reviewed RCC-002 S8BCP-001 Revision 2
implementation correction for repository integration from S0 through S7.

It certifies exactly the 41-file implementation and review payload staged on
top of:

```text
d9e37cba304b049fa518e163810c53eb9c83fc13
```

The certification decision itself is a separate governance artifact and is
not included in the 41-file payload identity below.

This decision does not authorize:

- S8 implementation;
- dataset publication;
- live trading or production deployment;
- any file outside the certified payload and this certification record.

## 2. Certified payload identity

```text
staged_file_count=41
staged_patch_sha256=63ae399da6c3cf24db7c64ae0943c166eb360eab23cf14bd12984e3b634dd264
staged_file_list_sha256=54f1d2eb371f24c9f067d4857afbf8e42044a9fd1aa633c54c908d0ffbeacd49
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
`scripts/build_rcc002_spec_bundle.py` is excluded from the payload and remains
unmodified and unstaged.

## 3. Independent review evidence

| Evidence | Verdict | SHA-256 |
|---|---|---|
| `RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_REVIEW_2026-07-30.md` | `REJECT` - superseded after correction | `5c27a496f51c0f1768d15ec7245d634018d9263256bb8400659bd8df205102ab` |
| `RCC_002_S8BCP001_REV2_IMPLEMENTATION_SCIENTIFIC_RE_REVIEW_2026-07-30.md` | `APPROVE` | `e9e364974ff1313602e919b7fbf5c613cec2ea584cded7479b281e5179f219d7` |
| `RCC_002_S8BCP001_REV2_IMPLEMENTATION_ARCHITECTURE_REVIEW_2026-07-30.md` | `APPROVE_WITH_CONDITIONS` - superseded after correction | `e7af55a618ffb0382a1d96ffbd2b663413c44c6e14b86b7003c9436eb4571876` |
| `RCC_002_S8BCP001_REV2_IMPLEMENTATION_ARCHITECTURE_RE_REVIEW_2026-07-30.md` | `APPROVE` | `df26de5865592d6c4360fad00f2c2498b370ccd7fe485b55267e647f38fa3af6` |

The scientific and architecture resolutions are included in the certified
payload. All blocking findings from the superseded reviews are closed.

## 4. Live repository verification

The following gates were executed after controlled payload import into
`/home/benja/projects/sniper-bot` and before this decision:

| Gate | Result |
|---|---|
| Branch | `main` |
| Baseline `HEAD` | `d9e37cba304b049fa518e163810c53eb9c83fc13` |
| Baseline `origin/main` | exact match |
| Git ancestry `3c5bb520...` -> `d9e37cba...` | `PASS` |
| Payload dry-run before copy | exactly 41 new/modified files |
| Post-copy payload byte comparison | `PASS` |
| `git diff --check` | `PASS` |
| `python3 -m compileall -q rcc002 scripts/rcc002 tests/rcc002` | `PASS` |
| RCC-002 unit tests | 631/631 `PASS` |
| Repository regression tests | 170/170 `PASS` |
| Normative root `SHA256SUMS` | `PASS` |
| Staged diff check | `PASS` |
| Staged file count | exactly 41 |
| New file modes | all `100644` |

## 5. Provider evidence verification

The registered source-profile verifier was executed against:

```text
RCC_002_BINANCE_PROVIDER_EVIDENCE_INPUT_2026-07-30.zip
```

Result:

```text
archive_count=4
record_count=92160
source_row_id_unique_count=92160
2024 archives=MILLISECOND
2025 archives=MICROSECOND
s0_s1_normalization_parity=PASS for all archives
result=PASS
```

The millisecond-to-microsecond transition is therefore verified against the
real provider evidence, not inferred from timestamp magnitude.

## 6. Invalid verification invocation disposition

One attempted invocation of
`scripts/rcc002/verify_s8bcp001_artifacts.py` from the full repository was
discarded as invalid because that tool verifies the isolated normative
correction-bundle file set and intentionally rejects unrelated repository
paths. The resulting `.claude/settings.local.json` assertion was not a
candidate failure and is not used as certification evidence.

The correct repository-level normative artifact gate,
`sha256sum -c --quiet SHA256SUMS`, passed.

## 7. Certified implementation properties

The certified correction establishes:

- registered Binance Vision daily/monthly source identity and evidence-bound
  timestamp-unit selection;
- fail-closed archive, checksum, path, encoding, coverage, ordering, and
  collision validation;
- Source Snapshot V1 and Source Manifest 1.0.0 canonical identity;
- Source Row ID V2 and exact S1 source-coordinate validation;
- unchanged source-coordinate propagation through S2-S7;
- exact S3 `indicator_schema_ref` propagation and S4 consumer validation;
- deterministic downstream component-version and fingerprint updates;
- fail-closed prevention of registered `BINANCE_VISION` input through the
  historical generic ingestion path.

No indicator formula, regime/gate formula, label/forward-return computation,
or authorized S0-S7 scientific value was changed outside the reviewed scope.

## 8. Conditions of effectiveness

This certification becomes effective only if:

1. this certification file is added with mode `100644`;
2. the complete staged state contains the certified 41-file payload plus only
   this certification record;
3. `git diff --cached --check` remains clean;
4. the commit has parent
   `d9e37cba304b049fa518e163810c53eb9c83fc13`;
5. the commit is pushed to `origin/main`;
6. local `HEAD` and `origin/main` match after push;
7. `scripts/build_rcc002_spec_bundle.py` remains untracked and unstaged.

Any change to the certified payload invalidates this decision until the
payload identity and all affected gates are re-established.

## 9. Final decision

```text
CERTIFIED
```

The RCC-002 S8BCP-001 Revision 2 S0-S7 implementation correction is approved
for controlled commit and push under the conditions in Section 8.
