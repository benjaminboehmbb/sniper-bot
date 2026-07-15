"""TD005-IU-007: Execution-Environment Identity Realization Unit.

Realizes TD005-SO-005's own environment-identity recording behaviour:
captures the execution environment's own interpreter and third-party
numeric-library identity at the moment of each Replay Session's own
execution (TD005-ID-006: remains standalone, not folded into Replay or
Reference Baseline).

State model (TD005-SO-005, unmodified): Unrecorded -> Recorded.
A fresh record is produced per capture; never reused for a different
session (TD005-IU-007's own Forbidden interactions).

Traceability: TD005-SO-005; TD005-ARC-012; TD005-AD-004; TD005-ID-006.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentIdentity:
    state: str  # "Unrecorded" | "Recorded"
    session_id: str
    python_version: str
    platform_python_implementation: str
    numpy_version: str
    pandas_version: str


def capture(session_id: str) -> EnvironmentIdentity:
    """Capture identity at the moment of the associated Replay Session's own
    execution, not retroactively (TD005-IU-007's own Required behaviour).
    A fresh, independent import per call: never reuses a cached value from
    a different session."""
    import numpy
    import pandas

    return EnvironmentIdentity(
        state="Recorded",
        session_id=session_id,
        python_version=sys.version,
        platform_python_implementation=platform.python_implementation(),
        numpy_version=numpy.__version__,
        pandas_version=pandas.__version__,
    )


def identities_match(a: EnvironmentIdentity, b: EnvironmentIdentity) -> bool:
    """Whether reference and candidate were captured under the identical
    environment (used only for informational comparison; TD005-SO-011's own
    tolerance-bounded category, not this unit, absorbs small environment-
    induced numeric variation)."""
    return (
        a.python_version == b.python_version
        and a.numpy_version == b.numpy_version
        and a.pandas_version == b.pandas_version
    )
