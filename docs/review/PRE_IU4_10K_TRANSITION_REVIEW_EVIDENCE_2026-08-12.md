# Pre-IU-4 10K Transition Review Evidence — 2026-08-12

## Status

**18/18 TRANSITIONS PROFESSIONALLY REVIEWED — PASS**

The user explicitly approved `IU4-10K-TRANSITIONEN-REVIEW FREIGEBEN` on
2026-08-12.

This review is bound to the complete X1 observation evidence at repository
commit `b35bac1acdb8127f62951aaa481b7a056bb48ee5`:

- observation records: `10,000/10,000`;
- observation evidence SHA-256:
  `aae4299709c1c52a853f574bf0931614e0d316d8d393758d3959b6f5f4f6f4f0`;
- observation evidence fingerprint:
  `d0253a180fd30a4e7a51e4ccc379933ddb476448668f7bee1a8dadc85d16ade9`;
- normalized market slice SHA-256:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`.

IU4 ENFORCED, Exchange, Live, and source-state mutation remained disabled.

## Transition contract result

- committed transitions: `18/18` reviewed;
- ordered pairs: `9 OPEN_LONG`, followed by `9 CLOSE_LONG`;
- transaction sequence: exact and gap-free `1..18`;
- unique request IDs: `18/18`;
- unique source-intent IDs: `18/18`;
- position-before parity failures: `0`;
- action parity failures: `0`;
- position-after parity failures: `0`;
- state-fingerprint chain breaks: `0`;
- previous/following NOOP boundary failures: `0`;
- guards: `18/18 guard_ok`;
- S4 state at transition: `18/18 SOFT`;
- final legacy/IU-4 position: `FLAT / FLAT`.

Every open was a confirmed `BUY` from `FLAT` with reason
`CONFIRMED_1M_BUY_5M_LONG`. Every close was a legacy autonomous exit derived
from source `HOLD`, translated to observed `SELL` only while the IU-4 sandbox
held `LONG`. All `9/9` autonomous exits matched the required side; suppression
count was `0`.

## Entry-throttle review

The approved policy permits at most two accepted entries per UTC day, two in a
rolling six-hour window, and requires a three-hour re-entry cooldown.

- minimum observed open-to-open gap: `20,340 seconds` (`5.65 hours`);
- required minimum: `10,800 seconds` (`3 hours`);
- maximum accepted opens in any UTC day: `2`;
- maximum accepted opens in any rolling six-hour window: `2`;
- daily opens: `2017-08-17=2`, `2017-08-18=2`, `2017-08-19=2`,
  `2017-08-20=2`, `2017-08-21=1`;
- throttle-contract violations: `0`.

## Trade-pair review

| Pair | Open tick | Close tick | Duration | Entry | Exit | Gross price return | Close reason |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 312 | 372 | 60 min | 4360 | 4400 | +0.917431% | LONG_TIME_STOP_HIT |
| 2 | 966 | 1026 | 60 min | 4311.18 | 4339 | +0.645299% | LONG_TIME_STOP_HIT |
| 3 | 1541 | 1601 | 60 min | 4291.47 | 4287.96 | -0.081790% | LONG_TIME_STOP_HIT |
| 4 | 1880 | 1940 | 60 min | 4343.23 | 4340.31 | -0.067231% | LONG_TIME_STOP_HIT |
| 5 | 3480 | 3540 | 60 min | 4039.84 | 4042.41 | +0.063616% | LONG_TIME_STOP_HIT |
| 6 | 3829 | 3889 | 60 min | 4076.12 | 4099 | +0.561318% | LONG_TIME_STOP_HIT |
| 7 | 4286 | 4346 | 60 min | 4111.26 | 4094.62 | -0.404742% | LONG_TIME_STOP_HIT |
| 8 | 5022 | 5082 | 60 min | 4101.13 | 4100 | -0.027553% | LONG_TIME_STOP_HIT |
| 9 | 6544 | 6568 | 24 min | 4019.99 | 3951.26 | -1.709706% | SL_LONG_HIT |

Eight closes occurred exactly at the 60-minute time-stop boundary. The ninth
closed after 24 minutes when the minute price crossed below the 1.5% long-stop
reference (`3959.69015`); observed close price was `3951.26`.

The gross price returns above are descriptive transition checks only. They do
not replace the Paper Economics fee, slippage, quantity, or settlement model
and are not profitability evidence.

## Independent cross-checks

- execution runtime log: `18/18` transitions matched tick, intent ID, action,
  before/after position, and reason;
- IU-4 observation runtime log: `18/18` matched sequence, tick, intent ID,
  action, position, and all three parity flags;
- normalized market CSV: `18/18` matched timestamp and exact decimal price;
- textual decimal variants such as `4360.0` versus canonical `4360` were
  compared numerically and were value-identical;
- transition immediately preceding/following record: `18/18` state
  fingerprints and transaction sequences continuous.

## Conclusion and scope boundary

No transition defect, throttle violation, ID mismatch, position divergence, or
state-chain discontinuity was found. The 18-transition set is suitable as the
reviewed X1 baseline for the next SHADOW gate.

This review does not authorize IU4 ENFORCED, Exchange, Live, or mutation of the
bound IU-4 source. The next gate should address the observation writer's
quadratic whole-file rewrite cost before a materially longer active
observation is attempted.
