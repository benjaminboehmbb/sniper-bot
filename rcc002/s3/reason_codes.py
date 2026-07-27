"""S3 indicator reason-code severity registry.

Transcribed verbatim from Indicator Specification §20.2 (Reason-Code-Vertrag)
and §20.3 (Nichtkritische Sonderfälle). Unlike Data Validation's `DV_` codes
(which needed the DVSEV-001 correction), every one of these 14 `IND_` codes
already carries an explicit Standard-Severity in the certified text itself
— no equivalent gap exists here.

`indicator_reason_code_registry_version=1.0.0` (§20.2).
"""

from __future__ import annotations

from typing import Iterable

from rcc002.reason_codes import Severity

INDICATOR_REASON_CODE_REGISTRY_VERSION = "1.0.0"

# §20.2, the eleven invalidating/informational reason codes.
INDICATOR_REASON_CODE_SEVERITY: dict[str, Severity] = {
    "IND_WARMUP_INCOMPLETE": Severity.INFO,
    "IND_INPUT_INVALID": Severity.ERROR,
    "IND_WINDOW_CROSSES_MARKET_SEGMENT": Severity.ERROR,
    "IND_WINDOW_CROSSES_INDICATOR_SEGMENT": Severity.ERROR,
    "IND_SYNTHETIC_INPUT_DISALLOWED": Severity.ERROR,
    "IND_STATE_MISSING": Severity.CRITICAL,
    "IND_STATE_MISMATCH": Severity.CRITICAL,
    "IND_NONFINITE_RESULT": Severity.CRITICAL,
    "IND_RANGE_INVARIANT_FAILED": Severity.CRITICAL,
    "IND_PROFILE_MISMATCH": Severity.CRITICAL,
    "IND_SCHEMA_MISMATCH": Severity.CRITICAL,
    # §20.3: non-critical special cases with a defined numeric value; the
    # affected field remains valid.
    "IND_STOCH_FLAT_WINDOW": Severity.INFO,
    "IND_CCI_ZERO_MAD": Severity.INFO,
    "IND_ADX_ZERO_TR": Severity.INFO,
}

assert len(INDICATOR_REASON_CODE_SEVERITY) == 14

# §20.2: codes for which x_valid is forced to False whenever active (per the
# certified table's own "x_valid" column) — distinct from the §20.3 special
# cases, which are explicitly non-invalidating.
INVALIDATING_REASON_CODES: frozenset[str] = frozenset(
    {
        "IND_WARMUP_INCOMPLETE",
        "IND_INPUT_INVALID",
        "IND_WINDOW_CROSSES_MARKET_SEGMENT",
        "IND_WINDOW_CROSSES_INDICATOR_SEGMENT",
        "IND_SYNTHETIC_INPUT_DISALLOWED",
        "IND_STATE_MISSING",
        "IND_STATE_MISMATCH",
        "IND_NONFINITE_RESULT",
        "IND_RANGE_INVARIANT_FAILED",
        "IND_PROFILE_MISMATCH",
        "IND_SCHEMA_MISMATCH",
    }
)

# Implementation-owned, versioned, self-defined reason-code ordering profile
# — same governance disposition as `rcc002.reason_codes.
# REASON_CODE_PRIORITY_PROFILE_ID` (see Step-4/Step-5 readiness review,
# 2026-07-27): §20.2 claims list order follows "einer versionierten, im
# Register enthaltenen Priorität", but the printed §20.2 table carries no
# priority column. This binding does NOT resolve that at the specification
# level — it is an implementation-level decision only, disclosed as such,
# accepted because ordering has no effect on `x_valid`, severity, or any
# build effect.
INDICATOR_REASON_CODE_PRIORITY_PROFILE_ID = "RCC002_S3_REASON_CODE_PRIORITY_V1"


def sort_indicator_reason_codes(codes: Iterable[str]) -> list[str]:
    """Deterministic ordering: severity descending, then code name ascending."""
    return sorted(
        codes,
        key=lambda code: (-INDICATOR_REASON_CODE_SEVERITY[code].value, code),
    )
