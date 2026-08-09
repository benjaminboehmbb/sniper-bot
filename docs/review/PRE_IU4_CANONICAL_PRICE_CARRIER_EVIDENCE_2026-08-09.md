# Pre-IU-4 Canonical Price Carrier Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; NOT AN ECONOMICS ACTIVATION**

Branch: `codex/pre-iu4-canonical-price-carrier-2026-08-09`

IU-4, Exchange, and Live remain locked. The accepted PEE V1 profile and its
fingerprint are unchanged.

## Implemented scope

- `CSVMarketFeed` now reads the source `close` cell once as text.
- The existing strategy value is still produced through the unchanged float
  conversion.
- A separate `reference_price_text` is parsed and canonicalized directly with
  Decimal, without passing through binary float.
- `MarketSnapshot` and `FeatureSnapshot` carry that value additively.
- Missing, malformed, non-finite, zero, or negative source values produce an
  empty economic price carrier while preserving the existing legacy float
  behavior.
- A legacy/custom snapshot without `reference_price_text` remains compatible
  and produces an empty carrier. The feature builder never reconstructs
  authority using `str(float_price)`.
- `DummyMarketFeed` supplies deterministic canonical text for its synthetic
  price.

No active loop call, shadow observation, execution mutation, S2/S4 persistence,
Paper Account, throttle, fee, PnL, or mode switch was changed. OFF and SHADOW
therefore retain the existing execution owner and behavior.

## Precision proof

The focused test passes the CSV value
`12345.678901234567890123456789`. The new carrier retains that exact Decimal
value while the legacy float representation demonstrably differs. Equivalent
lexical forms such as `00100.12000` and `1.2300E+2` become stable canonical
strings `100.12` and `123` without a float round trip.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_canonical_price_carrier

Ran 7 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 118 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -t .

Ran 170 tests — OK
```

## Remaining boundary

The PEE shadow currently still receives `str(features.price)`. Switching shadow
or future enforced economics to `reference_price_text` is a separate change and
must fail closed when the carrier is empty. That change is not authorized or
implemented here.
