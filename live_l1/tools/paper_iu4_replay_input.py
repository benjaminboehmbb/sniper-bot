#!/usr/bin/env python3
"""Build strict IU-4 replay JSONL from an existing structured L1 log."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any

from live_l1.core.paper_iu4_shadow_harness import IU4ShadowIntentStepV1
from live_l1.state.paper_artifacts import canonical_decimal
from live_l1.tools.paper_economics_shadow_sidecar import (
    PaperEconomicsSidecarError,
    ParsedLogEvent,
    parse_l1_log_line,
)
from live_l1.tools.paper_iu4_replay_evidence import (
    IU4ReplayEvidenceError,
    IU4ReplayEvidenceReasonCode,
    IU4ReplayJsonlExportV1,
    publish_immutable_bytes,
    write_iu4_replay_jsonl,
)


REFERENCE_STOP_CONTEXT = Context(
    prec=50,
    rounding=ROUND_HALF_EVEN,
    Emin=-999999,
    Emax=999999,
)
ONE = Decimal("1")


class IU4ReplayInputBuilderReasonCode:
    SOURCE_INVALID = "PEE_IU4_REPLAY_SOURCE_INVALID"
    EVENT_INVALID = "PEE_IU4_REPLAY_SOURCE_EVENT_INVALID"
    EVENT_MISSING = "PEE_IU4_REPLAY_SOURCE_EVENT_MISSING"
    CONFIG_INVALID = "PEE_IU4_REPLAY_BUILDER_CONFIG_INVALID"
    OUTPUT_INVALID = "PEE_IU4_REPLAY_BUILDER_OUTPUT_INVALID"
    OUTPUT_CONFLICT = "PEE_IU4_REPLAY_BUILDER_OUTPUT_CONFLICT"
    SOURCE_CHANGED = "PEE_IU4_REPLAY_SOURCE_CHANGED"
    WRITE_FAILED = "PEE_IU4_REPLAY_BUILDER_WRITE_FAILED"


class IU4ReplayInputBuilderError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class IU4ReplayInputBuildV1:
    source_path: Path
    source_sha256: str
    source_size_bytes: int
    source_non_empty_lines: int
    parsed_event_count: int
    market_event_count: int
    intent_event_count: int
    replay: IU4ReplayJsonlExportV1
    manifest_path: Path
    manifest_sha256: str
    manifest_newly_written: bool
    manifest_already_exists: bool


@dataclass
class _TickSource:
    market: ParsedLogEvent | None = None
    intent: ParsedLogEvent | None = None


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _decimal_text(value: object, field_name: str) -> Decimal:
    if not isinstance(value, str) or not value.strip():
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.CONFIG_INVALID,
            f"{field_name} must be a non-empty decimal string",
        )
    try:
        result = Decimal(value.strip())
    except (InvalidOperation, ValueError) as exc:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.CONFIG_INVALID,
            f"{field_name} is not a valid decimal string",
        ) from exc
    if not result.is_finite():
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.CONFIG_INVALID,
            f"{field_name} must be finite",
        )
    return result


def _tick(event: ParsedLogEvent) -> int:
    raw = event.fields.get("tick", "")
    try:
        value = int(raw)
    except ValueError as exc:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"{event.event} line {event.line_number} has no integer tick",
        ) from exc
    if value < 0 or str(value) != raw:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"{event.event} line {event.line_number} has a non-canonical tick",
        )
    return value


def _required_field(event: ParsedLogEvent, field_name: str) -> str:
    value = event.fields.get(field_name, "").strip()
    if not value:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"{event.event} line {event.line_number} misses {field_name}",
        )
    return value


def _candidate_stop_price(
    *,
    intent: str,
    reference_price: Decimal,
    reference_stop_rate: Decimal,
) -> Decimal | None:
    if intent == "HOLD":
        return None
    multiplier = REFERENCE_STOP_CONTEXT.subtract(
        ONE,
        reference_stop_rate,
    ) if intent == "BUY" else REFERENCE_STOP_CONTEXT.add(
        ONE,
        reference_stop_rate,
    )
    return REFERENCE_STOP_CONTEXT.multiply(reference_price, multiplier)


def _candidate_trade_id(
    *,
    source_intent_id: str,
    system_state_id: str,
    source_tick: int,
    timestamp_utc: str,
    intent: str,
    reference_price: Decimal,
    reference_stop_price: Decimal,
) -> str:
    identity = {
        "source_intent_id": source_intent_id,
        "system_state_id": system_state_id,
        "source_tick": source_tick,
        "timestamp_utc": timestamp_utc,
        "intent": intent,
        "reference_price": canonical_decimal(reference_price),
        "reference_stop_price": canonical_decimal(reference_stop_price),
    }
    return f"PEE-IU4-TRADE-{_sha256(_canonical_json(identity))}"


def _step_from_pair(
    *,
    market: ParsedLogEvent,
    intent_event: ParsedLogEvent,
    replay_tick: int,
    reference_stop_rate: Decimal,
) -> IU4ShadowIntentStepV1:
    source_tick = _tick(market)
    if _tick(intent_event) != source_tick:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            "joined market and intent ticks differ",
        )
    if market.system_state_id != intent_event.system_state_id:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            "joined market and intent system_state_id values differ",
        )
    source_intent_id = intent_event.intent_id.strip()
    if not source_intent_id:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"intent_fused line {intent_event.line_number} misses intent_id",
        )
    intent = _required_field(intent_event, "intent_final").upper()
    if intent not in ("BUY", "SELL", "HOLD"):
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"intent_fused line {intent_event.line_number} has invalid intent_final",
        )
    price_text = _required_field(market, "reference_price_text")
    try:
        reference_price = Decimal(price_text)
    except (InvalidOperation, ValueError) as exc:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"market_snapshot line {market.line_number} has invalid reference_price_text",
        ) from exc
    if not reference_price.is_finite() or reference_price <= 0:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"market_snapshot line {market.line_number} has nonpositive reference_price_text",
        )
    if canonical_decimal(reference_price) != price_text:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
            f"market_snapshot line {market.line_number} price text is not canonical",
        )
    stop = _candidate_stop_price(
        intent=intent,
        reference_price=reference_price,
        reference_stop_rate=reference_stop_rate,
    )
    trade_id = "" if stop is None else _candidate_trade_id(
        source_intent_id=source_intent_id,
        system_state_id=market.system_state_id,
        source_tick=source_tick,
        timestamp_utc=_required_field(market, "timestamp_utc"),
        intent=intent,
        reference_price=reference_price,
        reference_stop_price=stop,
    )
    return IU4ShadowIntentStepV1(
        schema_version=1,
        source_intent_id=source_intent_id,
        intent_final=intent,
        intent_reason_code=_required_field(intent_event, "reason_code"),
        target_system_state_id=market.system_state_id,
        timestamp_utc=_required_field(market, "timestamp_utc"),
        tick_id=replay_tick,
        reference_price=reference_price,
        reference_stop_price=stop,
        trade_id=trade_id,
    )


def _parse_source(
    raw: bytes,
    *,
    reference_stop_rate: Decimal,
) -> tuple[tuple[IU4ShadowIntentStepV1, ...], dict[str, int]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.SOURCE_INVALID,
            "L1 source log must be UTF-8",
        ) from exc
    contexts: dict[tuple[str, int], _TickSource] = {}
    completed_keys: set[tuple[str, int]] = set()
    steps: list[IU4ShadowIntentStepV1] = []
    non_empty = parsed = markets = intents = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        non_empty += 1
        try:
            event = parse_l1_log_line(line, line_number)
        except PaperEconomicsSidecarError as exc:
            raise IU4ReplayInputBuilderError(
                IU4ReplayInputBuilderReasonCode.SOURCE_INVALID,
                f"invalid L1 log line {line_number}: {exc}",
            ) from exc
        parsed += 1
        if event.event not in ("market_snapshot", "intent_fused"):
            continue
        event_tick = _tick(event)
        key = (event.system_state_id, event_tick)
        if key in completed_keys:
            raise IU4ReplayInputBuilderError(
                IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
                f"duplicate completed market/intent key at line {line_number}",
            )
        context = contexts.setdefault(key, _TickSource())
        if event.event == "market_snapshot":
            markets += 1
            if event.category != "L2" or context.market is not None:
                raise IU4ReplayInputBuilderError(
                    IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
                    f"duplicate or non-L2 market_snapshot at line {line_number}",
                )
            context.market = event
        else:
            intents += 1
            if event.category != "L3" or context.intent is not None:
                raise IU4ReplayInputBuilderError(
                    IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
                    f"duplicate or non-L3 intent_fused at line {line_number}",
                )
            context.intent = event
        if context.market is not None and context.intent is not None:
            steps.append(
                _step_from_pair(
                    market=context.market,
                    intent_event=context.intent,
                    replay_tick=len(steps) + 1,
                    reference_stop_rate=reference_stop_rate,
                )
            )
            completed_keys.add(key)
            contexts.pop(key)
    if contexts:
        first_key = next(iter(contexts))
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_MISSING,
            f"unpaired market/intent event for system_state_id={first_key[0]} tick={first_key[1]}",
        )
    if not steps:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.EVENT_MISSING,
            "source log contains no complete market/intent pairs",
        )
    return tuple(steps), {
        "source_non_empty_lines": non_empty,
        "parsed_event_count": parsed,
        "market_event_count": markets,
        "intent_event_count": intents,
    }


def _output_error(exc: IU4ReplayEvidenceError) -> IU4ReplayInputBuilderError:
    if exc.reason_code == IU4ReplayEvidenceReasonCode.ORDER_INVALID:
        reason_code = IU4ReplayInputBuilderReasonCode.EVENT_INVALID
    elif exc.reason_code == IU4ReplayEvidenceReasonCode.OUTPUT_CONFLICT:
        reason_code = IU4ReplayInputBuilderReasonCode.OUTPUT_CONFLICT
    else:
        reason_code = IU4ReplayInputBuilderReasonCode.OUTPUT_INVALID
    return IU4ReplayInputBuilderError(reason_code, exc.detail)


def build_iu4_replay_input_from_l1_log(
    *,
    source_path: str | Path,
    output_path: str | Path,
    manifest_path: str | Path,
    reference_stop_rate: str,
) -> IU4ReplayInputBuildV1:
    source = Path(source_path)
    if not source.is_file() or source.is_symlink():
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.SOURCE_INVALID,
            "L1 source log must be a regular, non-symlink file",
        )
    output_candidate = Path(output_path)
    manifest_candidate = Path(manifest_path)
    if output_candidate.is_symlink() or manifest_candidate.is_symlink():
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.OUTPUT_INVALID,
            "replay and manifest outputs must not be symlinks",
        )
    source = source.resolve()
    output = output_candidate.resolve()
    manifest = manifest_candidate.resolve()
    if len({source, output, manifest}) != 3:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.OUTPUT_INVALID,
            "source, replay output, and manifest paths must differ",
        )
    stop_rate = _decimal_text(reference_stop_rate, "reference_stop_rate")
    if stop_rate <= 0 or stop_rate >= 1:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.CONFIG_INVALID,
            "reference_stop_rate must be greater than zero and less than one",
        )

    raw = source.read_bytes()
    source_hash = _sha256(raw)
    steps, statistics = _parse_source(raw, reference_stop_rate=stop_rate)
    if source.read_bytes() != raw:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.SOURCE_CHANGED,
            "L1 source log changed during replay construction",
        )
    try:
        replay = write_iu4_replay_jsonl(steps=steps, output_path=output)
    except IU4ReplayEvidenceError as exc:
        raise _output_error(exc) from exc
    manifest_base: dict[str, Any] = {
        "artifact_type": "PEE_IU4_REPLAY_INPUT_MANIFEST",
        "schema_version": 1,
        "source": {
            "logical_name": source.name,
            "sha256": source_hash,
            "size_bytes": len(raw),
            **statistics,
        },
        "builder": {
            "reference_stop_rate": canonical_decimal(stop_rate),
            "tick_policy": "STRICT_SEQUENTIAL_FROM_ONE",
            "price_authority": "market_snapshot.reference_price_text",
        },
        "replay": {
            "logical_name": replay.output_path.name,
            "sha256": replay.output_sha256,
            "size_bytes": replay.size_bytes,
            "line_count": replay.line_count,
            "first_timestamp_utc": steps[0].timestamp_utc,
            "last_timestamp_utc": steps[-1].timestamp_utc,
            "first_tick_id": steps[0].tick_id,
            "last_tick_id": steps[-1].tick_id,
        },
    }
    manifest_record = {
        **manifest_base,
        "manifest_fingerprint": _sha256(_canonical_json(manifest_base)),
    }
    manifest_payload = _canonical_json(manifest_record) + b"\n"
    try:
        manifest_new, manifest_existing = publish_immutable_bytes(
            output_path=manifest,
            payload=manifest_payload,
        )
    except IU4ReplayEvidenceError as exc:
        raise _output_error(exc) from exc
    if source.read_bytes() != raw:
        raise IU4ReplayInputBuilderError(
            IU4ReplayInputBuilderReasonCode.SOURCE_CHANGED,
            "L1 source log changed during replay publication",
        )
    return IU4ReplayInputBuildV1(
        source_path=source,
        source_sha256=source_hash,
        source_size_bytes=len(raw),
        source_non_empty_lines=statistics["source_non_empty_lines"],
        parsed_event_count=statistics["parsed_event_count"],
        market_event_count=statistics["market_event_count"],
        intent_event_count=statistics["intent_event_count"],
        replay=replay,
        manifest_path=manifest,
        manifest_sha256=_sha256(manifest_payload),
        manifest_newly_written=manifest_new,
        manifest_already_exists=manifest_existing,
    )


__all__ = [
    "IU4ReplayInputBuildV1",
    "IU4ReplayInputBuilderError",
    "IU4ReplayInputBuilderReasonCode",
    "build_iu4_replay_input_from_l1_log",
]
