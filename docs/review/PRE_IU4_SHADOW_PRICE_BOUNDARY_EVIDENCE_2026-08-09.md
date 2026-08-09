# Pre-IU-4 Shadow Price Boundary Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; SHADOW ONLY**

Branch: `codex/pre-iu4-shadow-price-boundary-2026-08-09`

IU-4, Exchange, and Live remain locked. Legacy execution remains the sole
execution owner. The accepted PEE V1 profile and fingerprint are unchanged.

## Implemented boundary

- The active loop now passes `FeatureSnapshot.reference_price_text` to the PEE
  shadow bridge.
- It no longer recreates the shadow reference price with
  `str(features.price)` after binary-float parsing.
- Runtime bridge input is stripped but never replaced with a float fallback.
- Missing canonical price produces
  `PEE_SHADOW_REFERENCE_PRICE_MISSING`.
- Malformed, non-finite, zero, or negative direct shadow input produces
  `PEE_SHADOW_REFERENCE_PRICE_INVALID`.
- Both outcomes are deterministic shadow rejections with quantity `0`.
- When the PEE profile is valid, its profile/model/fingerprint provenance is
  retained in the rejection record.
- The resulting parity record may report that legacy executed while PEE shadow
  rejected. It does not provide a control output and cannot alter execution.

No sizing, guard, S2/S4, throttle, Paper Account, settlement, fee, PnL, or
legacy trade-log mutation was changed.

## Precision and non-interference proof

A focused active-loop test passes the CSV price
`12345.678901234567890123456789` and proves that the exact canonical text
reaches the shadow boundary. The legacy loop continues to receive its existing
float price.

A separate missing-carrier test proves all of the following simultaneously:

- PEE shadow denies with the stable missing-price reason;
- the accepted profile fingerprint remains present;
- the legacy outcome can still be `OPEN_LONG` / executed;
- the audit reports `PEE_SHADOW_LEGACY_EXECUTED_PEE_REJECTED`;
- no `allow_execution` control field is emitted.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_economics_shadow \
  tests.live_l1.test_paper_economics_shadow_runtime

Ran 21 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 121 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -t .

Ran 170 tests — OK
```

## Workstation consequence

The previous IU-3 full-history evidence remains valid evidence for its recorded
older commit and price boundary. It does **not** certify this new commit.

Before thresholds or IU-4 activation are considered, the workstation must rerun
the IU-3 shadow/full-history validation from the new integrated commit. The new
manifest must record the commit, dataset hash, unchanged PEE profile fingerprint,
command, reason counts, parity counts, output hashes, and ID parity. Expected
output hashes must not be copied from the older float-string boundary.
