# RCC-002 S5 Implementation Record

Date: 2026-07-28

Scope: `S4_SIGNALS -> S5_REGIMES` only

Implementation status: corrected after independent code review

Publication status: not asserted by this record

## 1. Binding baseline

- Repository baseline: `7249bd69746a348ffc76d5232fd4a3b054f1fcd9`
- Certified specification bundle SHA-256:
  `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee`
- Certified manifest SHA-256:
  `176d99582ebff741d5d45b7fccc76a49b5b1d267ce350d867d4f64c17c6a8297`
- Certification decision SHA-256:
  `d07068f32e1741d0821fe430542e10625105f4d8ef6d87aa47ea7766be93e2e0`
- Readiness decision:
  `IMPLEMENTATION READY — S5 ONLY`

No S6 gate, strategy, return, label or barrier field is implemented.

## 2. Implemented contracts

- Exact 21-field `rcc002.stage.s5-regimes/1.0.0` extension.
- Binary64 SMA200 slope at the exact 1,440-minute reference.
- `BULL`, `SIDE`, `BEAR`, `UNKNOWN` raw classification.
- Three-closed-bar persisted state machine with nullable transition endpoints.
- True transitions from a valid state to `UNKNOWN` and from `UNKNOWN` to the
  first confirmed valid state.
- Independent ADX trend-strength and S4 ATR-relative context validity.
- Exact ten-code S5 reason registry with field-local reason separation.
- Row-, key-, order- and S4-value preservation.
- Gap and segment fail-closed handling.
- Check-summed `rcc002.state.s5-regimes/1.0.0` continuation snapshot.
- Serial/partition parity, including a partition at a segment boundary.

## 3. Added source files

| File | SHA-256 |
|---|---|
| `rcc002/s5/__init__.py` | `2dfff57ebf1d78975c9ecef85f5f365f9a5169916554d8a83e4cc223a2db5dee` |
| `rcc002/s5/compute.py` | `049734962957908fe9e5cdd76c9a9abb0a63e767bbebdac43e4b3c5636a5f206` |
| `rcc002/s5/constants.py` | `31746655354dfd6e57f7569a7de1fb544bd2a689f375fd22319ad421637901bd` |
| `rcc002/s5/formulas.py` | `19bd54e3043409d63d81b4701df2cf6abf1a34bac571054e98af9bb8817be05d` |
| `rcc002/s5/reason_codes.py` | `eea4d65831315f7f7314f8973464d0eb761bda49b95c8abf7c4cf3d099b8cb3a` |
| `rcc002/s5/schema.py` | `d2f875675c31b38b8d55ab8ff3f095537fb4fdd0cf17b72d5c8929747ff15bf6` |
| `rcc002/s5/state.py` | `ad2ecc9a89c30d8e76448c98b285fbca74ae423338d4a37b35430b291098e973` |

## 4. Added test files

| File | SHA-256 |
|---|---|
| `tests/rcc002/s5/__init__.py` | `839a2c72d1227c53b91b88cfacd498f980f7777b61f54870ab5a953997b27303` |
| `tests/rcc002/s5/test_compute.py` | `e870b66fd7038576837a82e42107de346a2cf1a371c40d4368f173e0d3ff3b98` |
| `tests/rcc002/s5/test_formulas.py` | `bfc72fed56b7114531fb6922577b54093f33a86f05a0677041cab5ef981ab2b5` |
| `tests/rcc002/s5/test_golden_fixtures.py` | `e5441304fd3cb351ed613806420eec8d12496bd35222bafdc7eba2671303e14b` |
| `tests/rcc002/s5/test_schema.py` | `7df5436b41eda223af0c166170d040e38f486d684421029b797ce0fa62f2de60` |
| `tests/rcc002/s5/test_state.py` | `af7c2afde3bf2681a9d763e6bd3ff59d1443854688ff16b73ddd962f35c28428` |

## 5. Verification results

Executed in a clean extraction of the supplied implementation input:

```text
python3 -m compileall -q rcc002 tests/rcc002
PASS

python3 -m unittest discover -s tests/rcc002/s5 -t .
Ran 69 tests
OK

python3 -m unittest discover -s tests/rcc002 -t .
Ran 475 tests
OK
```

The separately reported local `tests/regression` collection was not present
in the supplied implementation archive. The installation command runs it in
the target repository before any commit is permitted.

## 6. Protected repository state

The pre-existing untracked file
`scripts/build_rcc002_spec_bundle.py` is outside this package and must remain
unmodified and uncommitted unless separately authorized.

## 7. Independent-review corrections

The first independent Claude and Gemini reviews returned `REJECTED`.
Following direct normative adjudication:

- `REG_EFFECTIVE_UNCONFIRMED` is now emitted only when `regime_raw` is valid
  and the first effective regime remains unconfirmed, matching specification
  section 12.7.1.
- S5 receives independent `indicators` and `signals` dictionary containers,
  preventing downstream mutation from aliasing an upstream in-memory row.
- External comparison tolerances are documented as external verification
  constants; internal threshold decisions remain exact.
- Tests explicitly bind the segment-transition rule from specification
  section 9.6: a previously valid effective regime changing to `UNKNOWN` is
  a transition, while `UNKNOWN` to `UNKNOWN` at a segment start is not.

The complete finding adjudication is recorded separately in
`RCC_002_S5_INDEPENDENT_REVIEW_RESOLUTION_2026-07-28.md`.

## 8. Corrected independent re-review

The corrected implementation received two focused independent re-reviews:

| Reviewer | Decision | Report SHA-256 |
|---|---|---|
| Claude | `APPROVED` | `ba855165235580e660689f8d0ef8c1fb5f9058e91b56ed484899e5ce57dbd8e9` |
| Gemini | `APPROVED` | `58ba14463185824d3b066152d6e9c6d489695731b924c3a88d5dc88451ef8757` |

Both reviewers independently confirmed:

- the corrected `REG_EFFECTIVE_UNCONFIRMED` condition;
- separation of the S5 dictionary containers from upstream S4 containers;
- the normative segment-transition interpretation from section 9.6;
- the context-reason exclusivity rule from section 12.7.2;
- the registered State and hash profiles;
- absence of remaining `CRITICAL` or `MAJOR` findings.

The target X1 subsequently passed:

```text
S5:        69 tests
RCC-002:  475 tests
Regression: 170 tests
```

No code or specification change occurred after these test runs and before the
independent re-reviews.
