#!/usr/bin/env python3
"""Atomic Paper Account persistence and idempotent settlement recovery.

The settlement journal is written before the account snapshot.  Each journal
file is immutable and contains the complete V2 trade plus the expected account
state after that trade.  A restart can therefore finish an interrupted commit
without booking the trade twice.

IU-2 does not integrate this store into the active L1 runtime.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from live_l1.state.paper_artifacts import (
    ARTIFACT_SETTLEMENT,
    ArtifactReasonCode,
    PaperAccountState,
    PaperArtifactError,
    TradeRecordV2,
    apply_trade_to_account,
    artifact_schema_version,
    canonical_json_sha256,
)


class AccountStoreReasonCode:
    ACCOUNT_MISSING = "PEE_ACCOUNT_MISSING"
    ACCOUNT_ALREADY_INITIALIZED = "PEE_ACCOUNT_ALREADY_INITIALIZED"
    JSON_INVALID = "PEE_SCHEMA_JSON_INVALID"
    JOURNAL_CONFLICT = "PEE_RECONCILIATION_JOURNAL_CONFLICT"
    JOURNAL_GAP = "PEE_RECONCILIATION_JOURNAL_GAP"
    ACCOUNT_AHEAD_OF_JOURNAL = "PEE_RECONCILIATION_ACCOUNT_AHEAD_OF_JOURNAL"
    RECOVERY_REQUIRED = "PEE_RECONCILIATION_RECOVERY_REQUIRED"


class PaperAccountStoreError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedSettlementInterruption(RuntimeError):
    """Test-only interruption after durable journal write."""


@dataclass(frozen=True)
class SettlementEnvelopeV1:
    schema_version: int
    account_before_fingerprint: str
    trade: TradeRecordV2
    account_after: PaperAccountState

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_UNSUPPORTED,
                "SettlementEnvelopeV1 requires schema_version 1",
            )
        if not isinstance(self.account_before_fingerprint, str) or not self.account_before_fingerprint.strip():
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "account_before_fingerprint must not be empty",
            )
        object.__setattr__(
            self,
            "account_before_fingerprint",
            self.account_before_fingerprint.strip(),
        )
        if self.account_after.closed_trade_count != self.trade.settlement_sequence:
            raise PaperArtifactError(
                ArtifactReasonCode.SEQUENCE_MISMATCH,
                "envelope account and trade sequences differ",
            )
        if self.account_after.last_settled_trade_id != self.trade.trade_id:
            raise PaperArtifactError(
                ArtifactReasonCode.ACCOUNT_MISMATCH,
                "envelope account does not reference its trade",
            )
        if self.account_after.last_update_event_id != self.trade.settlement_event_id:
            raise PaperArtifactError(
                ArtifactReasonCode.ACCOUNT_MISMATCH,
                "envelope account does not reference its settlement event",
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "artifact_type": ARTIFACT_SETTLEMENT,
            "account_before_fingerprint": self.account_before_fingerprint,
            "trade": self.trade.to_record(),
            "account_after": self.account_after.to_record(),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "SettlementEnvelopeV1":
        artifact_schema_version(record, ARTIFACT_SETTLEMENT)
        trade_raw = record.get("trade")
        account_raw = record.get("account_after")
        if not isinstance(trade_raw, Mapping) or not isinstance(account_raw, Mapping):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "settlement envelope requires trade and account_after objects",
            )
        return cls(
            schema_version=record.get("schema_version"),
            account_before_fingerprint=record.get("account_before_fingerprint"),
            trade=TradeRecordV2.from_record(trade_raw),
            account_after=PaperAccountState.from_record(account_raw),
        )

    @property
    def envelope_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class SettlementCommitResult:
    account: PaperAccountState
    journal_path: Path
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


@dataclass(frozen=True)
class RecoveryResult:
    account: PaperAccountState
    journal_count: int
    recovered_settlement_count: int


@dataclass(frozen=True)
class ReconciliationReport:
    consistent: bool
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    account_trade_count: int
    journal_trade_count: int


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperAccountStoreError(
            AccountStoreReasonCode.JSON_INVALID,
            f"cannot read valid JSON object from {path}",
        ) from exc
    if not isinstance(value, dict):
        raise PaperAccountStoreError(
            AccountStoreReasonCode.JSON_INVALID,
            f"JSON root in {path} must be an object",
        )
    return value


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(str(directory), flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


class PaperAccountStore:
    """Single-writer store for one paper account and its settlement journal."""

    def __init__(self, root_directory: str | Path) -> None:
        self.root_directory = Path(root_directory)
        self.account_path = self.root_directory / "paper_account.json"
        self.settlement_directory = self.root_directory / "settlements"

    def initialize(self, state: PaperAccountState) -> PaperAccountState:
        if self.account_path.exists():
            existing = self.load_account()
            if existing == state:
                return existing
            raise PaperAccountStoreError(
                AccountStoreReasonCode.ACCOUNT_ALREADY_INITIALIZED,
                "paper account already exists with different state",
            )
        if self.settlement_directory.exists() and any(self.settlement_directory.glob("*.json")):
            raise PaperAccountStoreError(
                AccountStoreReasonCode.JOURNAL_CONFLICT,
                "cannot initialize account while settlement journal is non-empty",
            )
        _atomic_write_json(self.account_path, state.to_record())
        return state

    def load_account(self) -> PaperAccountState:
        if not self.account_path.exists():
            raise PaperAccountStoreError(
                AccountStoreReasonCode.ACCOUNT_MISSING,
                "paper account has not been initialized",
            )
        return PaperAccountState.from_record(_read_json_object(self.account_path))

    def _journal_path(self, trade: TradeRecordV2) -> Path:
        trade_hash = canonical_json_sha256({"trade_id": trade.trade_id})[:20]
        filename = f"{trade.settlement_sequence:020d}_{trade_hash}.json"
        return self.settlement_directory / filename

    def _load_envelope(self, path: Path) -> SettlementEnvelopeV1:
        return SettlementEnvelopeV1.from_record(_read_json_object(path))

    def _journal_envelopes(self) -> list[tuple[Path, SettlementEnvelopeV1]]:
        if not self.settlement_directory.exists():
            return []
        result = [
            (path, self._load_envelope(path))
            for path in sorted(self.settlement_directory.glob("*.json"))
        ]
        self._validate_journal_chain(result)
        return result

    @staticmethod
    def _validate_journal_chain(
        entries: list[tuple[Path, SettlementEnvelopeV1]],
    ) -> None:
        previous: Optional[SettlementEnvelopeV1] = None
        trade_ids: set[str] = set()
        for expected_sequence, (_, envelope) in enumerate(entries, start=1):
            trade = envelope.trade
            if trade.settlement_sequence != expected_sequence:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_GAP,
                    f"journal expected sequence {expected_sequence} but found {trade.settlement_sequence}",
                )
            if trade.trade_id in trade_ids:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_CONFLICT,
                    f"duplicate journal trade_id {trade.trade_id}",
                )
            trade_ids.add(trade.trade_id)
            if previous is None:
                if trade.previous_settled_trade_id != "":
                    raise PaperAccountStoreError(
                        AccountStoreReasonCode.JOURNAL_GAP,
                        "first journal trade must not reference a predecessor",
                    )
            else:
                if trade.previous_settled_trade_id != previous.trade.trade_id:
                    raise PaperAccountStoreError(
                        AccountStoreReasonCode.JOURNAL_GAP,
                        "journal previous-trade chain is broken",
                    )
                if envelope.account_before_fingerprint != previous.account_after.state_fingerprint:
                    raise PaperAccountStoreError(
                        AccountStoreReasonCode.JOURNAL_CONFLICT,
                        "journal account fingerprint chain is broken",
                    )
            previous = envelope

    def commit_trade(
        self,
        trade: TradeRecordV2,
        *,
        simulate_interruption_after_journal: bool = False,
    ) -> SettlementCommitResult:
        current = self.load_account()
        journal_path = self._journal_path(trade)

        if journal_path.exists():
            existing = self._load_envelope(journal_path)
            if existing.trade.record_fingerprint != trade.record_fingerprint:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_CONFLICT,
                    "same settlement identity contains different trade data",
                )
            if current == existing.account_after:
                return SettlementCommitResult(
                    account=current,
                    journal_path=journal_path,
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=False,
                )
            if current.state_fingerprint == existing.account_before_fingerprint:
                _atomic_write_json(self.account_path, existing.account_after.to_record())
                return SettlementCommitResult(
                    account=existing.account_after,
                    journal_path=journal_path,
                    newly_committed=False,
                    already_committed=False,
                    recovered_incomplete_commit=True,
                )
            raise PaperAccountStoreError(
                AccountStoreReasonCode.JOURNAL_CONFLICT,
                "existing journal does not match current or resulting account state",
            )

        account_after = apply_trade_to_account(current, trade)
        envelope = SettlementEnvelopeV1(
            schema_version=1,
            account_before_fingerprint=current.state_fingerprint,
            trade=trade,
            account_after=account_after,
        )
        _atomic_write_json(journal_path, envelope.to_record())

        if simulate_interruption_after_journal:
            raise SimulatedSettlementInterruption(
                "simulated interruption after durable settlement journal"
            )

        _atomic_write_json(self.account_path, account_after.to_record())
        return SettlementCommitResult(
            account=account_after,
            journal_path=journal_path,
            newly_committed=True,
            already_committed=False,
            recovered_incomplete_commit=False,
        )

    def reconciliation_report(self) -> ReconciliationReport:
        try:
            account = self.load_account()
            entries = self._journal_envelopes()
        except (PaperAccountStoreError, PaperArtifactError) as exc:
            reason = getattr(exc, "reason_code", AccountStoreReasonCode.JOURNAL_CONFLICT)
            return ReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(reason,),
                account_trade_count=0,
                journal_trade_count=0,
            )

        journal_count = len(entries)
        if account.closed_trade_count > journal_count:
            return ReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(AccountStoreReasonCode.ACCOUNT_AHEAD_OF_JOURNAL,),
                account_trade_count=account.closed_trade_count,
                journal_trade_count=journal_count,
            )
        if account.closed_trade_count < journal_count:
            return ReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(AccountStoreReasonCode.RECOVERY_REQUIRED,),
                account_trade_count=account.closed_trade_count,
                journal_trade_count=journal_count,
            )
        if entries and account != entries[-1][1].account_after:
            return ReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(ArtifactReasonCode.ACCOUNT_MISMATCH,),
                account_trade_count=account.closed_trade_count,
                journal_trade_count=journal_count,
            )
        if not entries and account.closed_trade_count != 0:
            return ReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(AccountStoreReasonCode.ACCOUNT_AHEAD_OF_JOURNAL,),
                account_trade_count=account.closed_trade_count,
                journal_trade_count=0,
            )
        return ReconciliationReport(
            consistent=True,
            entry_allowed=True,
            exit_allowed=True,
            reason_codes=(),
            account_trade_count=account.closed_trade_count,
            journal_trade_count=journal_count,
        )

    def recover(self) -> RecoveryResult:
        current = self.load_account()
        entries = self._journal_envelopes()
        journal_count = len(entries)

        if current.closed_trade_count > journal_count:
            raise PaperAccountStoreError(
                AccountStoreReasonCode.ACCOUNT_AHEAD_OF_JOURNAL,
                "account contains more settlements than the journal",
            )
        if current.closed_trade_count == journal_count:
            if entries and current != entries[-1][1].account_after:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_CONFLICT,
                    "account and latest journal state differ",
                )
            return RecoveryResult(
                account=current,
                journal_count=journal_count,
                recovered_settlement_count=0,
            )

        recovered = 0
        for _, envelope in entries[current.closed_trade_count :]:
            if current.state_fingerprint != envelope.account_before_fingerprint:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_CONFLICT,
                    "account does not match the next journal predecessor",
                )
            expected_after = apply_trade_to_account(current, envelope.trade)
            if expected_after != envelope.account_after:
                raise PaperAccountStoreError(
                    AccountStoreReasonCode.JOURNAL_CONFLICT,
                    "journal account_after cannot be reproduced",
                )
            _atomic_write_json(self.account_path, expected_after.to_record())
            current = expected_after
            recovered += 1

        return RecoveryResult(
            account=current,
            journal_count=journal_count,
            recovered_settlement_count=recovered,
        )


__all__ = [
    "AccountStoreReasonCode",
    "PaperAccountStore",
    "PaperAccountStoreError",
    "ReconciliationReport",
    "RecoveryResult",
    "SettlementCommitResult",
    "SettlementEnvelopeV1",
    "SimulatedSettlementInterruption",
]
