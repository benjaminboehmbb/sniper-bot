"""Pure truth-table helpers for RCC-002 S6."""

from __future__ import annotations

from rcc002.s6.constants import GateState


def derive_gate_state(
    *,
    gate_valid: bool,
    allow_long: bool,
    allow_short: bool,
) -> GateState:
    """Apply the exact GateState truth rule from RG specification §18.4."""

    for name, value in (
        ("gate_valid", gate_valid),
        ("allow_long", allow_long),
        ("allow_short", allow_short),
    ):
        if type(value) is not bool:
            raise ValueError(f"{name} must be Boolean")
    if not gate_valid:
        if allow_long or allow_short:
            raise ValueError("an invalid gate cannot allow a direction")
        return GateState.INVALID
    if allow_long and allow_short:
        return GateState.ALLOW_BOTH
    if allow_long:
        return GateState.ALLOW_LONG_ONLY
    if allow_short:
        return GateState.ALLOW_SHORT_ONLY
    return GateState.BLOCK_BOTH


__all__ = ["derive_gate_state"]
