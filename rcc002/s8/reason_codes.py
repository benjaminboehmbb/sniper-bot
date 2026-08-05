"""Fail-closed error taxonomy for RCC-002 S8_EXPORT.

Every rejection raised by ``rcc002.s8`` code is one of the typed errors
below. There is no bare ``Exception``, ``AssertionError``, or uncaught
``KeyError``/``TypeError`` escape path in this package's public API: a
caller either receives a valid result or one of these errors.
"""

from __future__ import annotations


class S8Error(Exception):
    """Base class for every fail-closed RCC-002 S8 rejection."""


class FieldRegistryError(S8Error):
    """The certified field ownership/leakage registry is violated."""


class ViewProjectionError(S8Error):
    """A view projection contains an unknown, misowned, or leaking field."""


class RowReconciliationError(S8Error):
    """S8_rows != S7_rows, or row identity/order/value was not preserved."""


class CanonicalizationError(S8Error):
    """A value cannot be represented under RCC_JSON_CANONICALIZATION_V1."""


class IdentityError(S8Error):
    """A deterministic identity preimage is incomplete or malformed."""


class ManifestValidationError(S8Error):
    """A manifest fails structural or semantic validation."""


class PublicationStateError(S8Error):
    """An illegal build/publication state or state transition."""


class PublicationError(S8Error):
    """Atomic publication cannot proceed (overwrite, missing parent, etc.)."""


class ArtifactClassificationError(S8Error):
    """A release artifact does not resolve to exactly one artifact class."""


__all__ = [
    "S8Error",
    "ArtifactClassificationError",
    "CanonicalizationError",
    "FieldRegistryError",
    "IdentityError",
    "ManifestValidationError",
    "PublicationError",
    "PublicationStateError",
    "RowReconciliationError",
    "ViewProjectionError",
]
