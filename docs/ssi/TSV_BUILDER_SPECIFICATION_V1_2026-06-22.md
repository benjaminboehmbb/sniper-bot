# TSV BUILDER SPECIFICATION V1

Date:
2026-06-22

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Component:
TSV Builder

Classification:
Scientific Transformation Specification

Status:
SPECIFICATION ONLY

Implementation Status:
NOT IMPLEMENTED

---

# 1. Purpose

The TSV Builder is the reference transformation engine responsible for translating runtime observations into the canonical Trade State Vector (TSV) representation.

The TSV Builder defines the official language translation between runtime lifecycle data and the internal scientific representation used by SSI.

Its purpose is not analysis.

Its purpose is deterministic scientific transformation.

---

# 2. Scientific Role

Runtime observations are considered the raw observational language.

TSV is considered the canonical scientific language.

The TSV Builder therefore acts as the official compiler between both representations.

Runtime Observations

↓

TSV Builder

↓

Trade State Vector

↓

SSI

The builder itself never performs scientific interpretation.

It only constructs the representation.

---

# 3. Responsibilities

The TSV Builder SHALL

- load lifecycle observations
- validate runtime integrity
- construct TSV dimensions
- normalize dimension values
- attach provenance
- validate generated TSV records
- generate deterministic outputs
- create dataset manifests

The TSV Builder SHALL NOT

- classify trades
- predict outcomes
- generate forecasts
- perform clustering
- modify execution logic
- create trading signals

---

# 4. Inputs

Mandatory

- trade_lifecycle_snapshots.csv

Optional

- execution_audit.jsonl
- passive_shadow_close_accounting.csv
- passive_shadow_risk_snapshots.csv
- passive_shadow_entry_multipliers.csv

Optional sources may only enrich current-state information.

No future information may be introduced.

---

# 5. Internal Pipeline

Stage 1

Input Validation

↓

Stage 2

Runtime Parsing

↓

Stage 3

Feature Construction

↓

Stage 4

Dimension Construction

↓

Stage 5

Normalization

↓

Stage 6

TSV Assembly

↓

Stage 7

Validation

↓

Stage 8

Manifest Generation

↓

Stage 9

Output Writing

Each stage must be independently testable.

---

# 6. Feature Construction

Builder features represent observable quantities only.

Examples

- unrealized pnl
- pnl delta
- regime
- score
- duration
- side
- MA200
- ATR quality
- MFI

Derived features must always remain reproducible.

No hidden transformations are allowed.

---

# 7. Dimension Construction

The builder transforms raw features into

Progress

Compatibility

Stability

Confidence

Each dimension shall be constructed independently.

Dimension formulas must remain version-controlled.

---

# 8. Normalization

Every dimension must produce values between

0.0

and

1.0

Normalization functions must be deterministic.

Future normalization changes require a TSV version increment.

---

# 9. Provenance

Every generated TSV record shall include complete provenance.

Required information

- runtime_id
- trade_id
- snapshot_id
- timestamp
- generator_version
- TSV version
- source file
- source row

Every TSV record must be reproducible.

---

# 10. Validation

The builder performs structural validation before writing outputs.

Checks include

- required columns
- duplicate TSV identifiers
- missing values
- invalid normalization
- invalid provenance
- schema consistency
- deterministic ordering

Validation failures stop generation.

---

# 11. Outputs

Required outputs

tsv_dataset_v1.csv

tsv_dataset_v1.parquet

tsv_dataset_v1_manifest.json

tsv_dataset_v1_summary.md

No additional output files shall be produced by default.

---

# 12. Manifest

The manifest records

- runtime_id
- generator version
- TSV version
- row counts
- trade counts
- snapshot counts
- hashes
- validation status
- warnings
- errors

The manifest becomes the official scientific fingerprint of the dataset.

---

# 13. Determinism

The TSV Builder must produce identical outputs for identical inputs.

No randomness is allowed.

No timestamp-dependent logic is allowed.

No hidden caches are allowed.

No adaptive weighting is allowed.

---

# 14. Scientific Constraints

The TSV Builder is intentionally passive.

It observes.

It transforms.

It validates.

It documents.

It never interprets.

Scientific interpretation belongs to SSI Analytics.

---

# 15. Relationship to SSI

The TSV Builder is the entry point into the State Space Intelligence Platform.

No SSI module may consume runtime lifecycle snapshots directly.

All downstream SSI modules consume TSV datasets only.

This guarantees a single canonical scientific language across the platform.

---

# 16. Relationship to Execution

Execution

↓

Lifecycle Snapshots

↓

TSV Builder

↓

TSV Dataset

↓

SSI Analytics

↓

Scientific Knowledge

↓

Possible Future Recommendations

Execution is never modified by the TSV Builder.

---

# 17. Versioning

Builder versions are independent from TSV versions.

Builder Version

describes implementation.

TSV Version

describes representation.

Both versions must always be stored.

---

# 18. Testing Strategy

The builder must support

- unit tests
- schema validation
- deterministic regression tests
- runtime integration tests
- manifest validation
- provenance validation

No release is accepted without passing all builder validation tests.

---

# 19. Scientific Design Principle

The TSV Builder is not an analytics engine.

It is not a forecasting engine.

It is not an intelligence engine.

It is a scientific compiler that translates runtime observations into the canonical language of the State Space Intelligence Platform.

Its correctness is therefore more important than its complexity.

---

# 20. Final Principle

Inside SSI there shall exist exactly one canonical representation of runtime state.

That representation is the Trade State Vector (TSV).

The TSV Builder is the only component authorized to construct this representation.

All higher SSI modules shall consume TSV exclusively.

This guarantees consistency, reproducibility, explainability and long-term architectural stability across the complete State Space Intelligence Platform.

