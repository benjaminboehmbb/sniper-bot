# TSV DATA MODEL V1

Date:
2026-06-22

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Document Type:
Scientific Data Model Specification

Status:
SPECIFICATION ONLY

Implementation Status:
NOT IMPLEMENTED

---

# 1. Purpose

This document defines the first formal data model for the Trade State Vector (TSV).

The TSV is the primary state representation used by the State Space Intelligence Platform.

The purpose of this document is to define:

- schema
- dimensions
- provenance
- versioning
- validation rules
- allowed usage
- forbidden usage

before implementation begins.

---

# 2. Core Definition

A Trade State Vector represents the observable state of one active trade at one lifecycle snapshot.

It is not an execution decision.

It is not an exit signal.

It is not a trading rule.

It is a scientific state representation.

---

# 3. Input Source

Primary input:

runtime trade lifecycle snapshots.

Expected source file example:

runtime_runs/paper_4300000_2026-06-22/trade_lifecycle_snapshots.csv

Optional joined sources:

- closed trade list
- execution audit
- passive shadow risk snapshots
- passive shadow close accounting
- passive shadow entry multipliers

Optional sources may only be used if they do not introduce lookahead leakage.

---

# 4. TSV V1 Dimensions

TSV V1 consists of four independent dimensions:

- Progress
- Compatibility
- Stability
- Confidence

Each dimension must be normalized to a numeric range:

0.0 to 1.0

Interpretation:

0.0 = weak / poor / unfavorable

1.0 = strong / favorable / structurally healthy

No dimension may implicitly overwrite or modify another dimension.

---

# 5. Dimension 1: Progress

## Purpose

Progress describes whether the trade is developing in the economically favorable direction.

## Candidate Inputs

- unrealized_pnl
- unrealized_pnl_delta
- unrealized_pnl_acceleration
- duration
- side

## Interpretation

High Progress means the trade is already moving in the intended economic direction.

Low Progress means the trade is stagnating or moving against the position.

## Governance Rule

Progress must only use information available at or before the lifecycle snapshot timestamp.

---

# 6. Dimension 2: Compatibility

## Purpose

Compatibility describes whether the current market context remains structurally compatible with the trade direction.

## Candidate Inputs

- side
- market_regime
- ma200_signal
- regime direction
- direction compatibility flags

## Interpretation

High Compatibility means the trade direction and market structure agree.

Low Compatibility means the trade is structurally misaligned with the current market context.

## Governance Rule

Compatibility must avoid duplicate counting of equivalent information.

Example:

market_regime and ma200_signal may be highly redundant and should not both be blindly weighted as independent evidence.

---

# 7. Dimension 3: Stability

## Purpose

Stability describes whether the trade state is evolving in a stable or unstable way.

## Candidate Inputs

- regime_changed_since_entry
- score_delta_since_entry
- score_volatility
- repeated state reversals
- later optional health or recovery metrics

## Interpretation

High Stability means the trade state remains structurally coherent.

Low Stability means the trade is unstable, deteriorating, or frequently changing state.

## Governance Rule

Stability should represent state dynamics, not final trade outcome.

---

# 8. Dimension 4: Confidence

## Purpose

Confidence describes the quality of the original entry context.

## Candidate Inputs

- entry_score
- entry_atr_quality
- entry_mfi_signal
- entry_signal_strength
- entry_regime_context

## Interpretation

High Confidence means the trade began from a strong entry context.

Low Confidence means the trade began from a weak or ambiguous entry context.

## Important Limitation

Confidence is expected to be less predictive than Progress or Compatibility based on STI findings.

It should remain separated from live trade evolution.

---

# 9. Required TSV Schema

Every TSV record must contain at minimum:

- tsv_id
- tsv_version
- runtime_id
- trade_id
- snapshot_id
- timestamp_utc
- tick
- side
- progress
- compatibility
- stability
- confidence
- source_file
- source_row_index
- created_at_utc
- generator_name
- generator_version

---

# 10. Optional TSV Fields

Optional fields may include:

- progress_raw
- compatibility_raw
- stability_raw
- confidence_raw
- progress_components_json
- compatibility_components_json
- stability_components_json
- confidence_components_json
- market_regime
- current_score
- entry_score
- unrealized_pnl
- duration_sec
- atr_quality
- ma200_signal
- mfi_signal
- final_trade_pnl
- final_trade_result
- exit_reason

Optional final-trade fields may only be used for offline analysis and labeling.

They must not be used as input features for TSV construction.

---

# 11. TSV Identifier

The TSV identifier must be deterministic.

Recommended construction:

stable_hash(
  runtime_id,
  trade_id,
  snapshot_id,
  timestamp_utc,
  tsv_version
)

A TSV ID must not depend on row order unless row order is explicitly part of the provenance model.

---

# 12. Runtime Identifier

Each TSV dataset must contain a runtime identifier.

Example:

paper_4300000_2026-06-22

The runtime_id links TSV outputs to:

- source runtime directory
- trade file
- lifecycle snapshot file
- execution audit
- generated analysis outputs

---

# 13. Provenance Model

Every TSV must be traceable back to the source lifecycle snapshot.

Required provenance chain:

runtime archive

-> lifecycle snapshot

-> TSV builder

-> TSV record

No TSV may be accepted without source traceability.

---

# 14. Versioning

TSV versions must be explicit.

Initial version:

TSV v1.0

Future examples:

TSV v1.1
Adds Recovery dimension.

TSV v1.2
Adds Health dimension.

TSV v1.3
Adds Persistence dimension.

TSV v2.0
Adds probabilistic forecasts and uncertainty estimates.

Version changes must document:

- added fields
- removed fields
- changed formulas
- changed normalization
- changed validation rules

---

# 15. No-Lookahead Rule

TSV construction must be strictly no-lookahead.

Allowed:

- current snapshot data
- previous snapshot data
- entry state
- historical state evolution up to current timestamp

Forbidden:

- final pnl
- exit reason
- future snapshots
- future regime states
- post-exit labels
- any value derived from trade outcome

Exception:

Final trade outcome may be joined later for offline evaluation labels only.

It must remain clearly separated from TSV feature construction.

---

# 16. Determinism Rule

Given identical inputs, configuration, and code version, the TSV builder must produce identical outputs.

Required:

- stable ordering
- deterministic hashing
- explicit runtime_id
- explicit TSV version
- explicit generator version

---

# 17. Validation Rules

A TSV dataset must pass the following checks:

- all required columns exist
- no duplicate tsv_id values
- all dimension values between 0.0 and 1.0
- all records have runtime_id
- all records have trade_id
- all records have snapshot_id
- all records have timestamp_utc
- no required dimension is null
- source traceability fields are present
- TSV version is constant within one dataset unless explicitly allowed
- no final outcome fields were used in feature construction

---

# 18. Allowed Usage

TSV may be used for:

- state-space construction
- trajectory analysis
- transition analysis
- clustering
- basin analysis
- scientific monitoring
- offline hypothesis generation
- offline forecasting research
- knowledge extraction

---

# 19. Forbidden Usage

TSV V1 may not be used for:

- live exits
- live entries
- position size changes
- risk overrides
- execution blocking
- automatic trade intervention

without a separate validated execution approval process.

---

# 20. Output Formats

Preferred output formats:

- CSV for inspection
- Parquet for large-scale analysis
- JSON manifest for metadata
- Markdown summary for scientific documentation

Recommended files:

tsv_dataset_v1.csv

tsv_dataset_v1.parquet

tsv_dataset_v1_manifest.json

tsv_dataset_v1_summary.md

---

# 21. Manifest Requirements

Every TSV dataset must be accompanied by a manifest containing:

- runtime_id
- source_files
- row_counts
- trade_count
- snapshot_count
- tsv_count
- tsv_version
- generator_name
- generator_version
- created_at_utc
- validation_status
- validation_errors
- validation_warnings
- input_hashes
- output_hashes

---

# 22. Scientific Interpretation

TSV does not claim to predict the future.

TSV describes the present state of a trade.

Predictive use must be validated separately.

The correct interpretation is:

At timestamp t, the trade had state vector:

[Progress, Compatibility, Stability, Confidence]

Any relationship between this vector and later outcomes is an empirical research finding, not part of the TSV definition itself.

---

# 23. Relationship To STI Findings

The initial TSV V1 structure is motivated by Scientific Runtime Investigation findings:

- Progress showed strong information value.
- Compatibility showed strong information value.
- Stability contributed meaningful but weaker information.
- Confidence was less predictive but remains useful as separate entry-context information.

These findings motivate the dimension selection but do not hard-code trading decisions.

---

# 24. Relationship To SSI

SSI uses TSV as its primary state representation.

TSV is not the full SSI platform.

TSV is the input language for:

- state space construction
- trajectory modeling
- transition graphs
- clustering
- basin analysis
- forecasting
- knowledge extraction

---

# 25. Final Rule

TSV is a scientific representation layer.

It must remain observable, reproducible, versioned, traceable, and separated from execution until independently validated.

