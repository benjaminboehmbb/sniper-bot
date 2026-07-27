"""Central RCC-002 Data Validation reason-code severity registry.

Transcribed verbatim from `RCC_002_DATA_VALIDATION_2026-07-23.md` §16.3
"Reason-Code-Severity-Register" (added by correction cycle `RCC-002-DVSEV-001`,
Version 0.5.0, certified 2026-07-27; bundle
`docs/review/RCC_002_DVSEV001_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md`,
SHA-256 `8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee`).

This module is the single source of truth for reason-code severity across
the whole `rcc002` package (S0, S1, S2, and later stages): no stage-local
module may hardcode a reason code's severity independently of
`REASON_CODE_SEVERITY` below.

Two things this module deliberately does NOT resolve, because the certified
specification explicitly leaves them open (§25.1, "Offene
Implementierungsparameter", vor `Approved for Implementation` festzulegen):

- `REASON_CODE_PRIORITY_PROFILE_ID` / `sort_reason_codes`: §16.2 requires
  `quality_reason_codes` to be sorted by "einer versionierten
  Reason-Code-Priorität", but §25.1 lists the "Reason-Code-Prioritätsregister"
  itself as still open. This module self-defines one deterministic, versioned
  ordering (severity descending, then reason code ascending) under the
  implementation-owned profile ID below — the same kind of self-defined,
  versioned, implementation-delegated profile already used elsewhere in this
  package (e.g. `rcc002.s1.row_id.SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID`).
  This is NOT a resolution of §25.1's own open governance parameter at the
  specification level; it is only this implementation's chosen, disclosed,
  versioned technical ordering, pending any future formal spec-level decision.
- `QUALITY_RULE_VERSION`: see its own docstring below.
"""

from __future__ import annotations

import enum
from typing import Iterable


class Severity(enum.IntEnum):
    """Data Validation §16.1 severity taxonomy, in ascending strength.

    IntEnum ordering matches §16.1's own table order and the "höchste
    Severity" language used throughout (§15, §16.2): CRITICAL is the
    strongest, INFO the weakest.
    """

    INFO = 0
    WARN = 1
    ERROR = 2
    CRITICAL = 3


# Data Validation §16.3, transcribed verbatim (32 codes, matching §16.2's
# Mindestcodes list exactly in set and order). `DV_FILE_SUSPECTED_ROW_LIMIT_
# TRUNCATION`'s value here is its *Standardfall* (default) severity per §16.3
# row 5; the conditional escalation to CRITICAL (§6.3: "Bei einer
# vorgelagerten Datei mit mehr Zeilen oder einem erwarteten längeren
# Zeitbereich ist dieser Befund CRITICAL") remains the caller's
# responsibility (see rcc002.s0.integrity.check_spreadsheet_truncation_boundary),
# exactly as before this registry existed — the registry supplies the
# default, not an override of the certified escalation rule.
REASON_CODE_SEVERITY: dict[str, Severity] = {
    "DV_FILE_MISSING": Severity.ERROR,
    "DV_FILE_EMPTY": Severity.ERROR,
    "DV_FILE_CORRUPT": Severity.CRITICAL,
    "DV_CHECKSUM_MISMATCH": Severity.CRITICAL,
    "DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION": Severity.ERROR,
    "DV_SCHEMA_REQUIRED_COLUMN_MISSING": Severity.CRITICAL,
    "DV_SCHEMA_UNEXPECTED_COLUMN": Severity.WARN,
    "DV_PARSE_TIMESTAMP_FAILED": Severity.CRITICAL,
    "DV_PARSE_NUMERIC_FAILED": Severity.CRITICAL,
    "DV_TIME_NOT_UTC": Severity.CRITICAL,
    "DV_TIME_MISALIGNED": Severity.CRITICAL,
    "DV_TIME_OUT_OF_RANGE": Severity.ERROR,
    "DV_DUPLICATE_IDENTICAL_COLLAPSED": Severity.INFO,
    "DV_DUPLICATE_CONFLICT": Severity.CRITICAL,
    "DV_SOURCE_CONFLICT_RESOLVED": Severity.INFO,
    "DV_GAP_DETECTED": Severity.WARN,
    "DV_GAP_UNEXPLAINED": Severity.ERROR,
    "DV_TIME_GAP_SEGMENT_STARTED": Severity.INFO,
    "DV_NUMERIC_NONFINITE": Severity.CRITICAL,
    "DV_OHLC_INVARIANT_FAILED": Severity.CRITICAL,
    "DV_VOLUME_NEGATIVE": Severity.CRITICAL,
    "DV_VOLUME_ZERO_OBSERVED": Severity.WARN,
    "DV_ANOMALY_EXTREME_CANDLE_RETURN": Severity.WARN,
    "DV_ANOMALY_EXTREME_HIGH_LOW_RANGE": Severity.WARN,
    "DV_ANOMALY_EXTREME_VOLUME": Severity.WARN,
    "DV_ANOMALY_ZERO_VOLUME_CLUSTER": Severity.WARN,
    "DV_ANOMALY_REPEATED_IDENTICAL_OHLC": Severity.WARN,
    "DV_ANOMALY_PARTITION_BOUNDARY_JUMP": Severity.WARN,
    "DV_SYNTHETIC_ROW_NONCANONICAL": Severity.CRITICAL,
    "DV_APPROVED_WARNING_ACTIVE": Severity.INFO,
    "DV_ROW_RECONCILIATION_FAILED": Severity.CRITICAL,
    "DV_SCHEMA_FINGERPRINT_MISMATCH": Severity.CRITICAL,
}

assert len(REASON_CODE_SEVERITY) == 32  # §16.2/§16.3: exactly 32 registered codes


# Implementation-owned, versioned, self-defined reason-code ordering profile.
#
# GOVERNANCE DECISION RECORD (implementation-level, not a specification
# change): reviewed 2026-07-27 as part of the Step-4 completeness review
# (item A). §24.1 Nr. 3 names "Prioritäten" in the same certified sentence
# as "Severities" ("alle Reason Codes, Prioritäten, Severities und
# Buildwirkungen registriert sind"), which could be read as requiring the
# same formal registration weight Severity received via `RCC-002-DVSEV-001`.
# Decision: `REASON_CODE_PRIORITY_PROFILE_ID` is ACCEPTED for the current
# Step-4 scope as a valid, versioned, implementation-owned binding — NOT
# elevated to a certified normative priority register, and NOT a resolution
# of §25.1's own open "Reason-Code-Prioritätsregister" parameter at the
# specification level. Rationale: unlike severity, this ordering has no
# effect on `quality_status`, `quality_gate_pass`, any build effect, or any
# scientific output — it only determines the presentation order of an
# already-well-formed `quality_reason_codes` list. Should this profile ever
# need to change in a way that affects any of those outputs, that would be
# a different, certification-relevant decision requiring its own review
# cycle, not a mere version bump of this constant.
REASON_CODE_PRIORITY_PROFILE_ID = "RCC002_S2_REASON_CODE_PRIORITY_V1"


def sort_reason_codes(codes: Iterable[str]) -> list[str]:
    """Deterministically sort reason codes per `REASON_CODE_PRIORITY_PROFILE_ID`.

    Ordering: severity descending (CRITICAL, ERROR, WARN, INFO), then reason
    code name ascending as a stable, alphabetic tiebreak. Satisfies §16.2's
    requirement that the order "darf nicht von Threadplanung,
    Eingabedateireihenfolge oder Hash-Iteration abhängen" — the result
    depends only on the (severity, code name) pair, never on iteration or
    insertion order.
    """
    return sorted(
        codes,
        key=lambda code: (-REASON_CODE_SEVERITY[code].value, code),
    )


def derive_quality_status(active_codes: Iterable[str]) -> str:
    """Data Validation §15: `quality_status` from the highest active severity.

    "kein aktiver Code oder ausschließlich `INFO` ergibt `PASS`; höchste
    Severity `WARN` ergibt `WARN`; höchste Severity `ERROR` ergibt `ERROR`;
    höchste Severity `CRITICAL` ergibt `CRITICAL`."
    """
    severities = [REASON_CODE_SEVERITY[code] for code in active_codes]
    if not severities or max(severities) is Severity.INFO:
        return "PASS"
    return max(severities).name


# --- quality_rule_version -----------------------------------------------
#
# Data Validation §15 defines `quality_rule_version` as "Version des
# angewandten Qualitätsregelwerks" (version of the applied quality ruleset).
# §25.1 lists "Validierungsregelprofil und `quality_rule_version`" as an open
# implementation parameter that must be versioned before `Approved for
# Implementation`.
#
# Reported value and rationale (per explicit instruction, stated before use):
#
#   QUALITY_RULE_VERSION = "RCC002_QUALITY_RULE_V1"
#
# Rationale:
#   1. Format follows this project's own established convention for
#      versioned, implementation-owned profile identifiers
#      (`RCC002_<SCOPE>_V<N>`), already used for
#      `RCC002_S0_LEGACY_ALIAS_MIGRATION_V1`, `RCC002_S1_SOURCE_ROW_ID_V1`,
#      `RCC002_S1_LEGACY_ALIAS_MIGRATION_V1`.
#   2. Scope: "V1" of this identifier denotes the complete S2 quality
#      ruleset as implemented in `rcc002.s2` — i.e. the reason-code severity
#      register (this module), the row-level validation checks (schema,
#      timestamp, duplicate, OHLC/volume, gap/segment, anomaly), and the
#      `quality_status`/`quality_gate_pass` derivation logic — taken as one
#      versioned whole, exactly matching "Version des angewandten
#      Qualitätsregelwerks" (the ruleset as *applied*, not merely the
#      severity table in isolation).
#   3. Independent versioning axis: per the DVSEV-001 Architecture Integrity
#      Review (Observations DVSEV001-AIR-O1/O2), severity/quality-rule
#      changes are the correct domain of `quality_rule_version`, not of
#      `schema_id`/`schema_version` (§7.4's Schema-Fingerprint), which tracks
#      field-level structural schema identity instead. `QUALITY_RULE_VERSION`
#      is therefore deliberately independent of `rcc002.constants`'
#      `STAGE_SCHEMA_VERSION` for S2.
#   4. Determinism/traceability: any future change to `REASON_CODE_SEVERITY`,
#      to the anomaly thresholds, or to any other S2 validation rule MUST be
#      accompanied by a new `RCC002_QUALITY_RULE_V<N+1>` value — this value
#      must never be silently reused across a behavioural change, per this
#      family's fail-closed/reproducibility principles (Reproducibility and
#      Manifest, determinism/point-in-time correctness).
#   5. This constant is an implementation decision, not a specification
#      change: it does not modify any certified specification file, and it
#      is explicitly the kind of implementation-delegated parameter §25.1
#      anticipates being fixed at implementation time.
QUALITY_RULE_VERSION = "RCC002_QUALITY_RULE_V1"
