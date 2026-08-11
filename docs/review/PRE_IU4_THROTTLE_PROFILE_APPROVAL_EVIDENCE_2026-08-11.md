# Pre-IU-4 Throttle Profile Approval Evidence — 2026-08-11

## Status

**PROFILE APPROVED; RUNTIME NOT ACTIVATED**

The user explicitly approved the gate phrase
`IU4-THROTTLE-PROFIL OBSERVED-BOUNDARY FREIGEBEN` on 2026-08-11.

This approval selects one immutable throttle profile. It does not authorize
runtime activation, IU4 ENFORCED, Exchange access, or Live trading.

## Approved profile

- Artifact: `config/pee/PEE_RATE_OBSERVED_BOUNDARY_001.json`
- Artifact SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`
- Policy profile ID: `PEE_RATE_OBSERVED_BOUNDARY_001`
- Policy model version: `PEE_RATE_V1`
- Maximum accepted entries per UTC day: `2`
- Maximum accepted entries per rolling six-hour window: `2`
- Rolling window: `21,600 seconds`
- Minimum re-entry cooldown: `10,800 seconds`
- Policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`

The artifact records `profile_approved=true` while all activation and external
authority fields remain false:

- `runtime_activated=false`
- `iu4_enforced_authorized=false`
- `exchange_authorized=false`
- `live_authorized=false`

## Calibration binding

The approved numeric values match
`PEE_RATE_OBSERVED_BOUNDARY_CANDIDATE_001` exactly. The operational profile
uses a new stable model/profile identity, so its fingerprint intentionally
differs from the calibration candidate fingerprint.

- Calibration report SHA-256:
  `c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8`
- Calibration report fingerprint:
  `22da65f4b9752f71cd26807a798f7e674f1236a02aec73a190e5252c8d40092d`
- Calibration candidate fingerprint:
  `e70b2051a211934a7e276bc1488c516e0ecf1b9444ce5f41f81c276458f3b225`
- Accepted-entry decision replay SHA-256:
  `65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b`
- Full-history effect at the approved thresholds: `0 / 111` accepted entries
  blocked; no fee, PnL, drawdown, or trade-count delta.

## Fail-closed boundary

The approved artifact is structurally distinct from the calibration-only
observation policies. The existing X1 replay loader rejects it. Therefore this
approval cannot silently activate the profile in the current replay or runtime
path. A later, separately authorized integration must explicitly load the
approved artifact, bind its exact fingerprint, and retain all startup, account,
S4, atomicity, and exit-always-allowed gates.

## Verification

```text
.venv/bin/python -m unittest \
  tests.live_l1.test_approved_paper_entry_throttle_profile
Ran 5 tests — OK

.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
Ran 276 tests — OK

.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
Ran 170 tests — OK
```

JSON validation, `py_compile`, and `git diff --check` passed. The profile and
its tests were committed as `db92429`.

## Next gate

The next controlled step is an offline IU4 SHADOW replay integration using the
exact approved profile and fingerprint. It must not activate IU4 ENFORCED,
Exchange, or Live. A successful X1 smoke replay must precede a fresh
workstation full-history validation.
