# RCC-002 Implementation — Deferred Blockers

Historical record of specification gaps confirmed during implementation.
Both recorded gaps were closed normatively by S8BCP-001 Revision 2 and are
implemented for the registered Binance Vision Spot kline profile. This file
preserves the original findings and records their exact closure; it is not a
certification or governance document.

---

## Blocker 1 — Undefined canonical semantic retrieval parameters

**Blocks**: automatic `source_snapshot_id` derivation (Step 13) only.
**Does not block**: S0–S12 (Steps 2–12 treat `source_snapshot_id` as an
opaque, externally-supplied value; S1 explicitly carries it through
unchanged per Data Validation §7.1).

**References**: Data Pipeline §7.1 (line 593); Data Validation §18.1 (lines
972, 979); Reproducibility §5.3 (lines 262, 266), §17.2 (line 1454).

**Gap**: all six occurrences require "kanonische semantische
Abrufparameter" ("canonical semantic retrieval parameters") to influence
`source_snapshot_id`, but no document defines what these parameters are for
any provider — no registry table, no glossary entry (checked Data
Validation §2 and Reproducibility §2 in full), no worked example (checked
the Reproducibility §24 manifest JSON example, which only shows the
placeholder `"source:sha256:<digest>"`).

**Minimum amendment proposed** (not implemented, not decided by
implementation): add a registry subsection (e.g., Reproducibility §5.3.1)
enumerating, per registered `provider`/`source_format`, the exact field(s)
that qualify — including an explicit "none registered" entry where no such
axis exists.

---

## Blocker 2 — Undefined derivation of "actual coverage period" from S0 source bytes

**Blocks**: automatic `source_snapshot_id` derivation (Step 13) only.
**Does not block**: S0–S12, for the same reason as Blocker 1.

**References**: Reproducibility §5.3 (lines 263, 271–273); Data Validation
§18.1 (line 973, the possibly-related but separately-named "logische
Quellenabdeckung"); Data Pipeline §7.1 (lines 532–541, S0 has no row
schema); Data Validation §7.1 (lines 306–307, `open_time`/`close_time` are
first produced at S1, not S0).

**Gap**: Reproducibility §5.3 requires an S0-stage identity pre-image to
include a timestamp-coverage range, but Data Pipeline §7.1 and Data
Validation §7.1 jointly establish that S0 has no row/timestamp schema at
all — the fields such a range would come from do not exist until S1.

**Minimum amendment proposed** (architectural choice, not decided by
implementation — two mutually exclusive options presented):
- **Option A**: authorize a narrowly-scoped, pre-canonical timestamp read at
  S0 (new Data Pipeline §7.1 subsection), or
- **Option B**: amend Reproducibility §5.3 so the coverage-period component
  is derived from S1's normalized `open_time`/`close_time` range instead of
  "from the source bytes" directly.

---

## Status

| Blocker | Status | Confirmed by |
|---|---|---|
| 1. Semantic retrieval parameters | CLOSED — `RCC002_BINANCE_VISION_SPOT_KLINES_V1` | S8BCP-001 Revision 2 |
| 2. Coverage period from S0 bytes | CLOSED — restricted structural S0 coverage scan | S8BCP-001 Revision 2 |

Closure is profile-specific. New registered Binance Vision builds derive
`source_snapshot_id` from the exact Source Snapshot V1 preimage implemented in
`rcc002/s0/source_identity.py`. The legacy generic plain-CSV ingestion path
continues to accept caller-supplied historical identities and must not be used
to bypass the registered profile.
