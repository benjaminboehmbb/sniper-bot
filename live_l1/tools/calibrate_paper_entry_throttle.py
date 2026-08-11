#!/usr/bin/env python3
"""Deterministic, read-only full-history paper-entry throttle calibration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from live_l1.core.paper_economics import authorize_entry, settle_trade
from live_l1.core.paper_economics_shadow import load_shadow_settings
from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    EntryThrottleReasonCode,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
    apply_accepted_entry,
    canonical_utc_timestamp,
    evaluate_entry_throttle,
)


ARTIFACT_TYPE = "PEE_RATE_FULL_HISTORY_CALIBRATION"
MODEL_VERSION = "PEE_RATE_CALIBRATION_V1"


class ThrottleCalibrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceTrade:
    index: int
    trade_id: str
    side: str
    entry_timestamp_utc: str
    exit_timestamp_utc: str
    reference_entry_price: Decimal
    reference_exit_price: Decimal


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _regular_file(path: str | Path, name: str) -> Path:
    candidate = Path(path)
    if not candidate.is_file() or candidate.is_symlink():
        raise ThrottleCalibrationError(f"{name} must be a regular non-symlink file")
    return candidate.resolve()


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ThrottleCalibrationError(f"invalid JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ThrottleCalibrationError(f"JSON root must be an object: {path}")
    return value


def _jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    raise ThrottleCalibrationError(
                        f"blank JSONL line {line_number}: {path}"
                    )
                value = json.loads(line, parse_float=Decimal)
                if not isinstance(value, dict):
                    raise ThrottleCalibrationError(
                        f"JSONL line {line_number} is not an object: {path}"
                    )
                records.append(value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ThrottleCalibrationError(f"invalid JSONL: {path}") from exc
    if not records:
        raise ThrottleCalibrationError(f"JSONL is empty: {path}")
    return records


def _utc(value: object, field_name: str) -> tuple[str, datetime]:
    try:
        canonical = canonical_utc_timestamp(value, field_name)
    except Exception as exc:
        raise ThrottleCalibrationError(f"invalid {field_name}") from exc
    parsed = datetime.fromisoformat(canonical[:-1] + "+00:00")
    return canonical, parsed


def _positive_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ThrottleCalibrationError(f"{field_name} must be numeric")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as exc:
        raise ThrottleCalibrationError(f"{field_name} must be numeric") from exc
    if not result.is_finite() or result <= 0:
        raise ThrottleCalibrationError(f"{field_name} must be finite and positive")
    return result


def _load_source_trades(
    execution_path: Path,
    trades_path: Path,
) -> tuple[tuple[SourceTrade, ...], int, int]:
    executions = _jsonl(execution_path)
    trades = _jsonl(trades_path)
    entries = [record for record in executions if record.get("event") == "ENTRY_ACCEPTED"]
    exits = [record for record in executions if record.get("event") == "EXIT_EXECUTED"]
    if len(entries) != len(exits) or len(entries) != len(trades):
        raise ThrottleCalibrationError(
            "entry, exit, and closed-trade counts must match exactly"
        )
    unknown_events = {
        str(record.get("event"))
        for record in executions
        if record.get("event") not in ("ENTRY_ACCEPTED", "EXIT_EXECUTED")
    }
    if unknown_events:
        raise ThrottleCalibrationError(
            "execution log contains unknown events: " + ",".join(sorted(unknown_events))
        )

    entry_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for record in entries:
        timestamp, _ = _utc(record.get("timestamp_utc"), "entry timestamp")
        side = str(record.get("side", "")).strip().upper()
        key = (timestamp, side)
        if side not in ("LONG", "SHORT") or key in entry_by_key:
            raise ThrottleCalibrationError("entry identity is invalid or duplicated")
        if record.get("position_before") != "FLAT":
            raise ThrottleCalibrationError("accepted entry did not start from FLAT")
        entry_by_key[key] = record

    normalized: list[SourceTrade] = []
    seen_trade_ids: set[str] = set()
    previous_entry: datetime | None = None
    previous_exit: datetime | None = None
    for index, record in enumerate(trades, start=1):
        trade_id = str(record.get("trade_id", "")).strip()
        side = str(record.get("side", "")).strip().upper()
        entry_timestamp, entry_dt = _utc(
            record.get("entry_timestamp_utc"), "trade entry timestamp"
        )
        exit_timestamp, exit_dt = _utc(
            record.get("exit_timestamp_utc"), "trade exit timestamp"
        )
        key = (entry_timestamp, side)
        source_entry = entry_by_key.get(key)
        if (
            not trade_id
            or trade_id in seen_trade_ids
            or side not in ("LONG", "SHORT")
            or source_entry is None
            or exit_dt <= entry_dt
            or (previous_entry is not None and entry_dt <= previous_entry)
            or (previous_exit is not None and entry_dt < previous_exit)
        ):
            raise ThrottleCalibrationError("closed-trade identity or ordering is invalid")
        entry_price = _positive_decimal(record.get("entry_price"), "entry_price")
        exit_price = _positive_decimal(record.get("exit_price"), "exit_price")
        source_price = _positive_decimal(source_entry.get("price"), "source entry price")
        if entry_price != source_price:
            raise ThrottleCalibrationError("execution/trade entry price parity failed")
        normalized.append(
            SourceTrade(
                index=index,
                trade_id=trade_id,
                side=side,
                entry_timestamp_utc=entry_timestamp,
                exit_timestamp_utc=exit_timestamp,
                reference_entry_price=entry_price,
                reference_exit_price=exit_price,
            )
        )
        seen_trade_ids.add(trade_id)
        previous_entry = entry_dt
        previous_exit = exit_dt
    return tuple(normalized), len(entries), len(exits)


def _integer_list(value: object, name: str) -> tuple[int, ...]:
    if not isinstance(value, list) or not value:
        raise ThrottleCalibrationError(f"{name} must be a non-empty list")
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 1 for item in value):
        raise ThrottleCalibrationError(f"{name} values must be positive integers")
    if len(set(value)) != len(value):
        raise ThrottleCalibrationError(f"{name} values must be unique")
    return tuple(value)


def _load_candidate_set(path: Path) -> dict[str, Any]:
    record = _json_object(path)
    expected_keys = {
        "artifact_type",
        "schema_version",
        "calibration_only",
        "operationally_approved",
        "candidate_set_id",
        "rolling_window_seconds",
        "sensitivity",
        "profiles",
    }
    if set(record) != expected_keys:
        raise ThrottleCalibrationError("candidate set fields are missing or unknown")
    if (
        record.get("artifact_type") != "pee_rate_calibration_candidate_set"
        or record.get("schema_version") != 1
        or record.get("calibration_only") is not True
        or record.get("operationally_approved") is not False
    ):
        raise ThrottleCalibrationError("candidate set is not calibration-only")
    rolling = record.get("rolling_window_seconds")
    if isinstance(rolling, bool) or not isinstance(rolling, int) or rolling < 1:
        raise ThrottleCalibrationError("rolling_window_seconds must be positive")
    sensitivity = record.get("sensitivity")
    if not isinstance(sensitivity, dict) or set(sensitivity) != {
        "max_entries_per_utc_day",
        "max_entries_per_rolling_window",
        "min_reentry_cooldown_seconds",
    }:
        raise ThrottleCalibrationError("sensitivity fields are invalid")
    for key in sensitivity:
        _integer_list(sensitivity[key], f"sensitivity.{key}")
    profiles = record.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ThrottleCalibrationError("profiles must be a non-empty list")
    identities: set[str] = set()
    for profile in profiles:
        if not isinstance(profile, dict) or set(profile) != {
            "policy_profile_id",
            "max_entries_per_utc_day",
            "max_entries_per_rolling_window",
            "min_reentry_cooldown_seconds",
            "classification",
        }:
            raise ThrottleCalibrationError("candidate profile fields are invalid")
        identity = str(profile.get("policy_profile_id", "")).strip()
        if not identity or identity in identities:
            raise ThrottleCalibrationError("candidate profile identity is invalid")
        identities.add(identity)
        for key in (
            "max_entries_per_utc_day",
            "max_entries_per_rolling_window",
            "min_reentry_cooldown_seconds",
        ):
            value = profile.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ThrottleCalibrationError(f"candidate {key} must be positive")
    return record


def _event_id(policy: PaperEntryThrottlePolicy, trade: SourceTrade) -> str:
    return "PEE-RATE-CAL-" + _sha256(
        _canonical_json(
            {
                "policy_fingerprint": policy.policy_fingerprint,
                "source_trade_id": trade.trade_id,
                "entry_timestamp_utc": trade.entry_timestamp_utc,
            }
        )
    )


def _evaluate_policy(
    trades: Sequence[SourceTrade],
    *,
    policy_profile_id: str,
    daily_limit: int,
    rolling_limit: int,
    rolling_window_seconds: int,
    cooldown_seconds: int,
) -> dict[str, Any]:
    policy = PaperEntryThrottlePolicy(
        schema_version=1,
        policy_model_version=MODEL_VERSION,
        policy_profile_id=policy_profile_id,
        max_entries_per_utc_day=daily_limit,
        max_entries_per_rolling_window=rolling_limit,
        rolling_window_seconds=rolling_window_seconds,
        min_reentry_cooldown_seconds=cooldown_seconds,
    )
    first_day = trades[0].entry_timestamp_utc[:10]
    state = PaperEntryThrottleState.initial(policy, utc_day=first_day)
    accepted_indexes: list[int] = []
    blocked_trade_ids: list[str] = []
    reason_counts: Counter[str] = Counter()
    decisions: list[dict[str, Any]] = []
    for trade in trades:
        decision = evaluate_entry_throttle(
            state,
            policy,
            entry_timestamp_utc=trade.entry_timestamp_utc,
        )
        decisions.append(
            {
                "source_trade_id": trade.trade_id,
                "entry_timestamp_utc": trade.entry_timestamp_utc,
                "entry_allowed": decision.entry_allowed,
                "reason_codes": list(decision.reason_codes),
            }
        )
        if not decision.entry_allowed:
            if not decision.exit_allowed:
                raise ThrottleCalibrationError("throttle blocked an exit")
            blocked_trade_ids.append(trade.trade_id)
            reason_counts.update(decision.reason_codes)
            continue
        event = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=state.total_accepted_entry_count + 1,
            entry_event_id=_event_id(policy, trade),
            previous_entry_event_id=state.last_entry_event_id,
            entry_timestamp_utc=trade.entry_timestamp_utc,
            policy_model_version=policy.policy_model_version,
            policy_profile_id=policy.policy_profile_id,
            policy_fingerprint=policy.policy_fingerprint,
        )
        state = apply_accepted_entry(state, policy, event)
        accepted_indexes.append(trade.index)
    blocked_count = len(blocked_trade_ids)
    return {
        "policy": policy.to_record(),
        "policy_fingerprint": policy.policy_fingerprint,
        "accepted_entry_count": len(accepted_indexes),
        "blocked_entry_count": blocked_count,
        "blocked_entry_percentage": _decimal_text(
            Decimal(blocked_count) * Decimal("100") / Decimal(len(trades))
        ),
        "reason_counts": dict(sorted(reason_counts.items())),
        "blocked_trade_ids": blocked_trade_ids,
        "accepted_trade_indexes": accepted_indexes,
        "decision_replay_sha256": _sha256(_canonical_json(decisions)),
        "final_throttle_state_fingerprint": state.state_fingerprint,
    }


def _economics_metrics(
    trades: Sequence[SourceTrade],
    accepted_indexes: set[int],
    *,
    config: Any,
    reference_stop_rate: Decimal,
) -> dict[str, Any]:
    equity = config.starting_equity_quote
    peak = equity
    total_fees = Decimal("0")
    total_net_pnl = Decimal("0")
    max_drawdown_rate = Decimal("0")
    settled_count = 0
    rejected_count = 0
    for trade in trades:
        if trade.index not in accepted_indexes:
            continue
        stop_multiplier = (
            Decimal("1") - reference_stop_rate
            if trade.side == "LONG"
            else Decimal("1") + reference_stop_rate
        )
        authorization = authorize_entry(
            side=trade.side,
            realized_equity_quote=equity,
            reference_entry_price=trade.reference_entry_price,
            reference_stop_price=trade.reference_entry_price * stop_multiplier,
            config=config,
        )
        if not authorization.allowed or authorization.quote is None:
            rejected_count += 1
            continue
        settlement = settle_trade(
            entry_quote=authorization.quote,
            reference_exit_price=trade.reference_exit_price,
            equity_before_quote=equity,
            peak_realized_equity_before_quote=peak,
            config=config,
        )
        settled_count += 1
        total_fees += settlement.total_fees_quote
        total_net_pnl += settlement.net_pnl_quote
        equity = settlement.equity_after_quote
        peak = settlement.peak_realized_equity_after_quote
        max_drawdown_rate = max(max_drawdown_rate, settlement.realized_drawdown_rate)
    return {
        "settled_trade_count": settled_count,
        "economics_rejected_count": rejected_count,
        "total_fees_quote": _decimal_text(total_fees),
        "total_net_pnl_quote": _decimal_text(total_net_pnl),
        "final_equity_quote": _decimal_text(equity),
        "peak_realized_equity_quote": _decimal_text(peak),
        "max_realized_drawdown_rate": _decimal_text(max_drawdown_rate),
    }


def _metrics_delta(candidate: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "settled_trade_count": int(candidate["settled_trade_count"])
        - int(baseline["settled_trade_count"]),
        "total_fees_quote": _decimal_text(
            Decimal(str(candidate["total_fees_quote"]))
            - Decimal(str(baseline["total_fees_quote"]))
        ),
        "total_net_pnl_quote": _decimal_text(
            Decimal(str(candidate["total_net_pnl_quote"]))
            - Decimal(str(baseline["total_net_pnl_quote"]))
        ),
        "final_equity_quote": _decimal_text(
            Decimal(str(candidate["final_equity_quote"]))
            - Decimal(str(baseline["final_equity_quote"]))
        ),
        "max_realized_drawdown_rate": _decimal_text(
            Decimal(str(candidate["max_realized_drawdown_rate"]))
            - Decimal(str(baseline["max_realized_drawdown_rate"]))
        ),
    }


def _source_distribution(
    trades: Sequence[SourceTrade], rolling_window_seconds: int
) -> dict[str, Any]:
    timestamps = [
        datetime.fromisoformat(trade.entry_timestamp_utc[:-1] + "+00:00")
        for trade in trades
    ]
    daily_counts = Counter(timestamp.date().isoformat() for timestamp in timestamps)
    gaps = sorted(
        int((current - previous).total_seconds())
        for previous, current in zip(timestamps, timestamps[1:])
    )
    rolling_counts = []
    for timestamp in timestamps:
        window_start = timestamp - timedelta(seconds=rolling_window_seconds)
        rolling_counts.append(
            sum(1 for candidate in timestamps if window_start < candidate <= timestamp)
        )

    def percentile(percent: int) -> int:
        if not gaps:
            return 0
        index = (len(gaps) - 1) * percent // 100
        return gaps[index]

    return {
        "entry_count": len(trades),
        "days_with_entries": len(daily_counts),
        "daily_entry_count_histogram": {
            str(key): value
            for key, value in sorted(Counter(daily_counts.values()).items())
        },
        "max_entries_per_utc_day": max(daily_counts.values()),
        "rolling_window_seconds": rolling_window_seconds,
        "max_entries_per_rolling_window": max(rolling_counts),
        "inter_entry_gap_seconds": {
            "minimum": gaps[0] if gaps else 0,
            "p10": percentile(10),
            "median": percentile(50),
            "p90": percentile(90),
            "maximum": gaps[-1] if gaps else 0,
        },
    }


def _sensitivity_results(
    trades: Sequence[SourceTrade], candidate_set: Mapping[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    rolling_window_seconds = int(candidate_set["rolling_window_seconds"])
    sensitivity = candidate_set["sensitivity"]
    non_binding = 1_000_000
    results: dict[str, list[dict[str, Any]]] = {}
    specifications = (
        ("max_entries_per_utc_day", sensitivity["max_entries_per_utc_day"]),
        (
            "max_entries_per_rolling_window",
            sensitivity["max_entries_per_rolling_window"],
        ),
        (
            "min_reentry_cooldown_seconds",
            sensitivity["min_reentry_cooldown_seconds"],
        ),
    )
    for field, values in specifications:
        rows: list[dict[str, Any]] = []
        for value in values:
            daily = value if field == "max_entries_per_utc_day" else non_binding
            rolling = (
                value if field == "max_entries_per_rolling_window" else non_binding
            )
            cooldown = (
                value if field == "min_reentry_cooldown_seconds" else 1
            )
            result = _evaluate_policy(
                trades,
                policy_profile_id=f"SENSITIVITY_{field}_{value}",
                daily_limit=daily,
                rolling_limit=rolling,
                rolling_window_seconds=rolling_window_seconds,
                cooldown_seconds=cooldown,
            )
            rows.append(
                {
                    "value": value,
                    "accepted_entry_count": result["accepted_entry_count"],
                    "blocked_entry_count": result["blocked_entry_count"],
                    "blocked_entry_percentage": result[
                        "blocked_entry_percentage"
                    ],
                    "reason_counts": result["reason_counts"],
                    "decision_replay_sha256": result["decision_replay_sha256"],
                }
            )
        results[field] = rows
    return results


def build_calibration_report(
    *,
    execution_log_path: str | Path,
    trades_log_path: str | Path,
    iu3_manifest_path: str | Path,
    economics_profile_path: str | Path,
    candidate_set_path: str | Path,
    expected_execution_sha256: str,
    expected_trades_sha256: str,
    expected_iu3_manifest_sha256: str,
    expected_source_sha256: str,
    calibration_git_commit: str,
    generated_at_utc: str,
) -> dict[str, Any]:
    execution_path = _regular_file(execution_log_path, "execution_log_path")
    trades_path = _regular_file(trades_log_path, "trades_log_path")
    manifest_path = _regular_file(iu3_manifest_path, "iu3_manifest_path")
    profile_path = _regular_file(economics_profile_path, "economics_profile_path")
    candidates_path = _regular_file(candidate_set_path, "candidate_set_path")
    hashes = {
        "execution_log": _sha256_file(execution_path),
        "trades_log": _sha256_file(trades_path),
        "iu3_manifest": _sha256_file(manifest_path),
        "economics_profile": _sha256_file(profile_path),
        "candidate_set": _sha256_file(candidates_path),
    }
    expected = {
        "execution_log": expected_execution_sha256.lower(),
        "trades_log": expected_trades_sha256.lower(),
        "iu3_manifest": expected_iu3_manifest_sha256.lower(),
    }
    for name, expected_hash in expected.items():
        if hashes[name] != expected_hash:
            raise ThrottleCalibrationError(f"{name} SHA-256 mismatch")

    manifest = _json_object(manifest_path)
    source = manifest.get("source_csv")
    normalized = manifest.get("normalized_market_slice")
    runtime = manifest.get("runtime")
    sidecar = manifest.get("sidecar")
    if not all(isinstance(value, Mapping) for value in (source, normalized, runtime, sidecar)):
        raise ThrottleCalibrationError("IU3 manifest misses required objects")
    if (
        source.get("sha256") != expected_source_sha256.lower()
        or runtime.get("return_code") != 0
        or sidecar.get("issues") != 0
        or sidecar.get("observation_ids_match_integrated") is not True
    ):
        raise ThrottleCalibrationError("IU3 manifest is not accepted evidence")

    profile = _json_object(profile_path)
    settings = load_shadow_settings({key: str(value) for key, value in profile.items()})
    if settings.config is None or settings.reference_stop_rate is None:
        raise ThrottleCalibrationError("economics profile is invalid")
    candidate_set = _load_candidate_set(candidates_path)
    trades, entry_count, exit_count = _load_source_trades(execution_path, trades_path)
    if runtime.get("executed_actions") != {
        "CLOSE_LONG": exit_count,
        "OPEN_LONG": entry_count,
    }:
        raise ThrottleCalibrationError("IU3 manifest execution parity failed")

    baseline_metrics = _economics_metrics(
        trades,
        {trade.index for trade in trades},
        config=settings.config,
        reference_stop_rate=settings.reference_stop_rate,
    )
    profiles: list[dict[str, Any]] = []
    for specification in candidate_set["profiles"]:
        evaluation = _evaluate_policy(
            trades,
            policy_profile_id=specification["policy_profile_id"],
            daily_limit=specification["max_entries_per_utc_day"],
            rolling_limit=specification["max_entries_per_rolling_window"],
            rolling_window_seconds=candidate_set["rolling_window_seconds"],
            cooldown_seconds=specification["min_reentry_cooldown_seconds"],
        )
        metrics = _economics_metrics(
            trades,
            set(evaluation.pop("accepted_trade_indexes")),
            config=settings.config,
            reference_stop_rate=settings.reference_stop_rate,
        )
        profiles.append(
            {
                "classification": specification["classification"],
                **evaluation,
                "economics": metrics,
                "delta_vs_unthrottled": _metrics_delta(metrics, baseline_metrics),
                "calibration_only": True,
                "operationally_approved": False,
            }
        )

    generated_at = canonical_utc_timestamp(generated_at_utc, "generated_at_utc")
    report_base = {
        "artifact_type": ARTIFACT_TYPE,
        "schema_version": 1,
        "status": "CALIBRATION_COMPLETE_PROFILE_APPROVAL_REQUIRED",
        "generated_at_utc": generated_at,
        "calibration_git_commit": calibration_git_commit.strip().lower(),
        "inputs": {
            "execution_log": {
                "logical_name": execution_path.name,
                "sha256": hashes["execution_log"],
            },
            "trades_log": {
                "logical_name": trades_path.name,
                "sha256": hashes["trades_log"],
            },
            "iu3_manifest": {
                "logical_name": manifest_path.name,
                "sha256": hashes["iu3_manifest"],
                "git_commit": manifest.get("git_commit"),
            },
            "source_csv_sha256": expected_source_sha256.lower(),
            "economics_profile": {
                "logical_name": profile_path.name,
                "sha256": hashes["economics_profile"],
                "profile_id": settings.config.economics_profile_id,
                "config_fingerprint": settings.config.config_fingerprint,
            },
            "candidate_set": {
                "logical_name": candidates_path.name,
                "sha256": hashes["candidate_set"],
                "candidate_set_id": candidate_set["candidate_set_id"],
            },
        },
        "source_scope": {
            "valid_minutes": normalized.get("rows_written"),
            "first_timestamp_utc": str(normalized.get("first_timestamp_utc")),
            "last_timestamp_utc": str(normalized.get("last_timestamp_utc")),
            "entry_count": entry_count,
            "exit_count": exit_count,
            "closed_trade_count": len(trades),
        },
        "distribution": _source_distribution(
            trades, int(candidate_set["rolling_window_seconds"])
        ),
        "unthrottled_economics": baseline_metrics,
        "sensitivity": _sensitivity_results(trades, candidate_set),
        "candidate_profiles": profiles,
        "interpretation": {
            "economics_scope": (
                "isolated PEE V1 settlement; account/S4 guards intentionally excluded "
                "to measure throttle-only deltas"
            ),
            "non_distorting_profiles": [
                profile["policy"]["policy_profile_id"]
                for profile in profiles
                if profile["blocked_entry_count"] == 0
            ],
            "approval_required": True,
            "automatic_operational_selection": False,
            "iu4_enforced_authorized": False,
            "exchange_authorized": False,
            "live_authorized": False,
        },
    }
    return {
        **report_base,
        "report_fingerprint": _sha256(_canonical_json(report_base)),
    }


def publish_report(path: str | Path, report: Mapping[str, Any]) -> tuple[Path, str]:
    output = Path(path)
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise ThrottleCalibrationError("output must be a regular non-symlink file")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise ThrottleCalibrationError("output parent must already exist")
    payload = _canonical_json(report) + b"\n"
    digest = _sha256(payload)
    if output.exists():
        if output.read_bytes() != payload:
            raise ThrottleCalibrationError("existing output differs; overwrite refused")
        return output.resolve(), digest
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(output.parent), prefix=f".{output.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, output)
        return output.resolve(), digest
    except FileExistsError as exc:
        if output.read_bytes() != payload:
            raise ThrottleCalibrationError(
                "concurrent output differs; overwrite refused"
            ) from exc
        return output.resolve(), digest
    finally:
        temporary.unlink(missing_ok=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-log", required=True)
    parser.add_argument("--trades-log", required=True)
    parser.add_argument("--iu3-manifest", required=True)
    parser.add_argument("--economics-profile", required=True)
    parser.add_argument("--candidate-set", required=True)
    parser.add_argument("--expected-execution-sha256", required=True)
    parser.add_argument("--expected-trades-sha256", required=True)
    parser.add_argument("--expected-iu3-manifest-sha256", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--calibration-git-commit", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    report = build_calibration_report(
        execution_log_path=args.execution_log,
        trades_log_path=args.trades_log,
        iu3_manifest_path=args.iu3_manifest,
        economics_profile_path=args.economics_profile,
        candidate_set_path=args.candidate_set,
        expected_execution_sha256=args.expected_execution_sha256,
        expected_trades_sha256=args.expected_trades_sha256,
        expected_iu3_manifest_sha256=args.expected_iu3_manifest_sha256,
        expected_source_sha256=args.expected_source_sha256,
        calibration_git_commit=args.calibration_git_commit,
        generated_at_utc=args.generated_at_utc,
    )
    output, digest = publish_report(args.output, report)
    print(
        json.dumps(
            {
                "status": report["status"],
                "output": str(output),
                "sha256": digest,
                "report_fingerprint": report["report_fingerprint"],
                "entries": report["source_scope"]["entry_count"],
                "profiles": [
                    {
                        "policy_profile_id": profile["policy"][
                            "policy_profile_id"
                        ],
                        "blocked": profile["blocked_entry_count"],
                        "decision_replay_sha256": profile[
                            "decision_replay_sha256"
                        ],
                    }
                    for profile in report["candidate_profiles"]
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
