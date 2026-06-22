# SSI ANALYTICS V1A SPECIFICATION

Date:
2026-06-22

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Component:
SSI Analytics V1

Document Type:
Scientific Analytics Specification

Status:
SPECIFICATION ONLY

---

# 1. Purpose

SSI Analytics V1 analyzes the TSV state-space produced by SSI Builder V1.

The purpose is not to create trading rules.

The purpose is to extract reproducible scientific evidence from runtime trade-state evolution.

---

# 2. Architectural Boundary

SSI Builder V1 is responsible for producing validated TSV datasets.

SSI Analytics V1 is responsible for analyzing those TSV datasets.

SSI Analytics V1 SHALL NOT:

- modify runtime data
- modify execution logic
- create live exits
- create entry rules
- perform adaptive gating
- alter the Builder

---

# 3. Input Contract

Primary input:

outputs/ssi/.../tsv_dataset.csv

Current limitation:

The current lifecycle export does not contain persistent trade_id.

Therefore SSI Analytics V1A must operate on snapshot-level state-space analysis first.

Trajectory-level reconstruction is explicitly deferred.

---

# 4. Output Contract

SSI Analytics V1A shall produce:

- analytics manifest
- state-space summary
- dimension distribution summary
- state frequency table
- scientific Markdown report

Initial output directory:

outputs/ssi/analytics/v1a/

---

# 5. V1A Scope

Included:

- TSV dataset validation for analytics use
- state key construction
- state frequency analysis
- dimension distribution analysis
- side-based comparison
- analytics manifest generation
- scientific report generation

Excluded:

- forecasting
- clustering
- trajectory reconstruction
- basin detection
- adaptive execution
- live governance integration
- strategy optimization
- parameter tuning

---

# 6. Initial State Definition

A state is defined as a deterministic combination of selected TSV dimensions.

Initial V1A state key:

- side
- progress bucket
- compatibility bucket
- stability bucket
- confidence bucket

The exact column names must be discovered from the TSV dataset header.

No hard-coded assumptions may be made without validation.

---

# 7. Scientific Questions

SSI Analytics V1A answers:

1. Which states occur most frequently?
2. Which dimensions dominate the runtime state-space?
3. Are LONG and SHORT states structurally different?
4. Are compatibility and stability distributions asymmetric?
5. Which state regions are rare, dominant, unstable, or structurally important?
6. Is the TSV dataset sufficient for later transition and trajectory analysis?

---

# 8. Validation Requirements

The analytics pipeline must validate:

- input file exists
- input file is non-empty
- required columns are present
- row count is greater than zero
- state keys are reproducible
- output files are generated
- manifest is generated
- report is generated

Validation failure must stop the run with a clear ASCII-only error.

---

# 9. Proposed Files

Implementation files:

- tools/ssi/analytics/state_key.py
- tools/ssi/analytics/load_tsv.py
- tools/ssi/analytics/state_space_summary.py
- tools/ssi/analytics/manifest.py
- tools/ssi/analytics/report.py
- tools/ssi/analytics/run_analytics_v1a.py

Tests:

- tests/ssi/test_analytics_state_key.py
- tests/ssi/test_analytics_state_space_summary.py
- tests/ssi/test_analytics_manifest.py

---

# 10. Acceptance Criteria

SSI Analytics V1A is complete when:

- all proposed modules exist
- tests pass
- the real TSV dataset is analyzed
- manifest is generated
- summary tables are generated
- report is generated
- results are reproducible
- no Builder files are modified
- no execution files are modified
- git status is clean after commit and push

---

# 11. Final Principle

SSI Analytics V1A begins the transition from state representation to state-space intelligence.

It must remain scientific, read-only, reproducible and non-executing.
