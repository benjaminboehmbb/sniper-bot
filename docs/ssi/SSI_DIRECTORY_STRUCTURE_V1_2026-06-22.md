# SSI DIRECTORY STRUCTURE V1

Date:
2026-06-22

Project:
Sniper-Bot

Platform:
State Space Intelligence (SSI)

Status:
IMPLEMENTED STRUCTURE ONLY

---

# Purpose

This document defines the initial directory structure for the State Space Intelligence Platform.

SSI is separated from Trade Inspector and from live execution logic.

The structure is intentionally modular so that TSV construction, analytics, forecasting, knowledge extraction and common utilities remain clearly separated.

---

# Directory Structure

tools/ssi/

Main SSI source root.

tools/ssi/builder/

Responsible for TSV dataset construction.

Future modules:

- build_tsv_dataset.py
- dimension_progress.py
- dimension_compatibility.py
- dimension_stability.py
- dimension_confidence.py
- normalization.py
- validation.py
- manifest.py
- provenance.py

tools/ssi/analytics/

Responsible for state-space, trajectory, transition and clustering analyses.

Future modules:

- build_state_space.py
- analyze_trajectories.py
- build_transition_graph.py
- find_state_clusters.py

tools/ssi/forecasting/

Responsible for future state prediction research.

No execution integration.

tools/ssi/knowledge/

Responsible for converting validated SSI findings into structured scientific knowledge objects.

tools/ssi/common/

Shared SSI-only utilities.

tests/ssi/builder/

Tests for TSV Builder modules.

outputs/ssi/

Default output root for generated SSI artifacts.

outputs/ssi/archive/

Archive directory for old SSI outputs.

---

# Architecture Rule

No SSI module may modify live execution behavior.

No SSI module may directly generate trading actions.

All SSI modules operate on scientific artifacts only.

---

# Canonical Data Flow

Runtime Artifacts

-> TSV Builder

-> TSV Dataset

-> SSI Analytics

-> SSI Knowledge

Execution remains separated.

---

# Current Implementation Status

Created directories only.

No production SSI code has been implemented yet.

