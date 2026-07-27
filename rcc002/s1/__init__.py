"""S1_NORMALIZED — canonical time-, field-, and type-normalization.

Per RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md §7.2: S1 normalizes
timestamps to UTC, field names, data types, interval designation, market
type, symbol designation, and numeric representation. S1 MUST NOT: create
missing bars, interpolate prices, arbitrarily remove duplicates, or compute
indicators. Those are S2 (Data Validation §7.3 onward) or S3 (Indicator)
responsibilities, out of scope for this subpackage.

`source_snapshot_id` is carried through from S0 unchanged (Data Validation
§7.1: "S0; durch S1 unverändert übernommen") — this subpackage never
computes it; see rcc002/IMPLEMENTATION_BLOCKERS.md for why that computation
is deferred to a later roadmap step.
"""
