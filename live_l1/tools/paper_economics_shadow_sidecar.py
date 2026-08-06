#!/usr/bin/env python3
"""Read-only L1 log sidecar for Paper Execution Economics shadow analysis.

The sidecar never imports or calls the active L1 loop or execution module.  It
joins already-written market, intent, and execution log events, evaluates PEE
entry economics, and writes a separate deterministic report when requested.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from live_l1.core.paper_economics_shadow import (
    MODE_SHADOW,
    ShadowEconomicsSettings,
    add_legacy_execution_outcome,
    load_shadow_settings,
    observe_shadow_entry_candidate,
)


SIDECAR_SCHEMA_VERSION = 1


class SidecarReasonCode:
    LOG_LINE_MALFORMED = "PEE_SHADOW_SOURCE_LOG_LINE_MALFORMED"
    EVENT_TICK_INVALID = "PEE_SHADOW_SOURCE_EVENT_TICK_INVALID"
    MARKET_EVENT_MISSING = "PEE_SHADOW_SOURCE_MARKET_EVENT_MISSING"
    INTENT_EVENT_MISSING = "PEE_SHADOW_SOURCE_INTENT_EVENT_MISSING"
    DUPLICATE_OBSERVATION = "PEE_SHADOW_DUPLICATE_OBSERVATION"
    CONFIG_FILE_INVALID = "PEE_SHADOW_CONFIG_FILE_INVALID"
    INPUT_OUTPUT_COLLISION = "PEE_SHADOW_INPUT_OUTPUT_COLLISION"


class PaperEconomicsSidecarError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


@dataclass(frozen=True)
class ParsedLogEvent:
    line_number: int
    timestamp_utc: str
    sequence: int
    category: str
    event: str
    severity: str
    system_state_id: str
    intent_id: str
    fields: Mapping[str, str]


@dataclass(frozen=True)
class SidecarIssue:
    reason_code: str
    line_number: int
    system_state_id: str
    tick: Optional[int]
    detail: str

    def to_record(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code,
            "line_number": self.line_number,
            "system_state_id": self.system_state_id,
            "tick": self.tick,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class SidecarObservationRecord:
    observation_id: str
    system_state_id: str
    tick: int
    source_market_sequence: int
    source_intent_sequence: int
    source_execution_sequence: int
    fields: Mapping[str, Any]

    def to_record(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "system_state_id": self.system_state_id,
            "tick": self.tick,
            "source_market_sequence": self.source_market_sequence,
            "source_intent_sequence": self.source_intent_sequence,
            "source_execution_sequence": self.source_execution_sequence,
            "fields": dict(self.fields),
        }


@dataclass(frozen=True)
class SidecarStatistics:
    non_empty_lines: int
    parsed_events: int
    malformed_lines: int
    market_events: int
    intent_events: int
    execution_events: int
    entry_candidates: int
    observations: int
    issues: int

    def to_record(self) -> dict[str, int]:
        return {
            name: int(getattr(self, name))
            for name in self.__dataclass_fields__
        }


@dataclass(frozen=True)
class SidecarReport:
    schema_version: int
    source_id: str
    source_sha256: str
    settings_mode: str
    settings_reason_code: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    observations: tuple[SidecarObservationRecord, ...]
    issues: tuple[SidecarIssue, ...]
    statistics: SidecarStatistics

    def to_record(self, *, include_report_id: bool = True) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "artifact_type": "pee_shadow_sidecar_report",
            "source_id": self.source_id,
            "source_sha256": self.source_sha256,
            "settings_mode": self.settings_mode,
            "settings_reason_code": self.settings_reason_code,
            "economics_profile_id": self.economics_profile_id,
            "economics_model_version": self.economics_model_version,
            "config_fingerprint": self.config_fingerprint,
            "statistics": self.statistics.to_record(),
            "observations": [item.to_record() for item in self.observations],
            "issues": [item.to_record() for item in self.issues],
        }
        if include_report_id:
            result["report_id"] = self.report_id
        return result

    @property
    def report_id(self) -> str:
        payload = self.to_record(include_report_id=False)
        return _canonical_sha256(payload)


@dataclass
class _TickContext:
    market: Optional[ParsedLogEvent] = None
    intent: Optional[ParsedLogEvent] = None


@dataclass
class _MutableStatistics:
    non_empty_lines: int = 0
    parsed_events: int = 0
    malformed_lines: int = 0
    market_events: int = 0
    intent_events: int = 0
    execution_events: int = 0
    entry_candidates: int = 0

    def freeze(self, *, observations: int, issues: int) -> SidecarStatistics:
        return SidecarStatistics(
            non_empty_lines=self.non_empty_lines,
            parsed_events=self.parsed_events,
            malformed_lines=self.malformed_lines,
            market_events=self.market_events,
            intent_events=self.intent_events,
            execution_events=self.execution_events,
            entry_candidates=self.entry_candidates,
            observations=observations,
            issues=issues,
        )


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_l1_log_line(raw_line: str, line_number: int) -> ParsedLogEvent:
    tokens = raw_line.strip().split()
    values: dict[str, str] = {}
    for token in tokens:
        key, separator, value = token.partition("=")
        if not separator or not key or key in values:
            raise PaperEconomicsSidecarError(
                SidecarReasonCode.LOG_LINE_MALFORMED,
                f"line {line_number} contains a malformed or duplicate key token",
            )
        values[key] = value

    required = (
        "timestamp_utc",
        "seq",
        "category",
        "event",
        "severity",
        "system_state_id",
    )
    missing = [name for name in required if name not in values]
    if missing:
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.LOG_LINE_MALFORMED,
            f"line {line_number} misses keys: {','.join(missing)}",
        )
    try:
        sequence = int(values["seq"])
    except ValueError as exc:
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.LOG_LINE_MALFORMED,
            f"line {line_number} seq is not an integer",
        ) from exc
    if sequence < 1:
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.LOG_LINE_MALFORMED,
            f"line {line_number} seq must be positive",
        )

    core_keys = set(required) | {"intent_id"}
    fields = {key: value for key, value in values.items() if key not in core_keys}
    return ParsedLogEvent(
        line_number=line_number,
        timestamp_utc=values["timestamp_utc"],
        sequence=sequence,
        category=values["category"],
        event=values["event"],
        severity=values["severity"],
        system_state_id=values["system_state_id"],
        intent_id=values.get("intent_id", ""),
        fields=fields,
    )


def _event_tick(event: ParsedLogEvent) -> Optional[int]:
    raw = event.fields.get("tick")
    if raw is None:
        return None
    try:
        tick = int(raw)
    except ValueError:
        return None
    return tick if tick >= 0 else None


def analyze_l1_log_text(
    text: str,
    *,
    settings: ShadowEconomicsSettings,
    source_id: str,
) -> SidecarReport:
    """Analyze L1 log text without changing the source or active runtime."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")
    source_name = str(source_id).strip()
    if not source_name:
        raise ValueError("source_id must not be empty")

    input_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    contexts: dict[tuple[str, int], _TickContext] = {}
    observations: list[SidecarObservationRecord] = []
    issues: list[SidecarIssue] = []
    seen_observation_ids: set[str] = set()
    statistics = _MutableStatistics()

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        statistics.non_empty_lines += 1
        try:
            event = parse_l1_log_line(raw_line, line_number)
        except PaperEconomicsSidecarError as exc:
            statistics.malformed_lines += 1
            issues.append(
                SidecarIssue(
                    reason_code=exc.reason_code,
                    line_number=line_number,
                    system_state_id="",
                    tick=None,
                    detail=exc.detail,
                )
            )
            continue
        statistics.parsed_events += 1

        relevant = event.event in ("market_snapshot", "intent_fused", "execution")
        if not relevant:
            continue
        tick = _event_tick(event)
        if tick is None:
            issues.append(
                SidecarIssue(
                    reason_code=SidecarReasonCode.EVENT_TICK_INVALID,
                    line_number=event.line_number,
                    system_state_id=event.system_state_id,
                    tick=None,
                    detail=f"{event.event} has no valid tick",
                )
            )
            continue

        key = (event.system_state_id, tick)
        context = contexts.setdefault(key, _TickContext())
        if event.event == "market_snapshot":
            statistics.market_events += 1
            context.market = event
            continue
        if event.event == "intent_fused":
            statistics.intent_events += 1
            context.intent = event
            continue

        statistics.execution_events += 1
        if context.market is None:
            issues.append(
                SidecarIssue(
                    reason_code=SidecarReasonCode.MARKET_EVENT_MISSING,
                    line_number=event.line_number,
                    system_state_id=event.system_state_id,
                    tick=tick,
                    detail="execution cannot be joined to market_snapshot",
                )
            )
        if context.intent is None:
            issues.append(
                SidecarIssue(
                    reason_code=SidecarReasonCode.INTENT_EVENT_MISSING,
                    line_number=event.line_number,
                    system_state_id=event.system_state_id,
                    tick=tick,
                    detail="execution cannot be joined to intent_fused",
                )
            )
        if context.market is None or context.intent is None:
            contexts.pop(key, None)
            continue

        market = context.market
        intent = context.intent
        current_position = intent.fields.get("current_position", "")
        intent_final = intent.fields.get("intent_final", "")
        if current_position.strip().upper() == "FLAT" and intent_final.strip().upper() in (
            "BUY",
            "SELL",
        ):
            statistics.entry_candidates += 1
        observation = observe_shadow_entry_candidate(
            settings=settings,
            current_position=current_position,
            intent_final=intent_final,
            reference_entry_price=market.fields.get("price", ""),
            tick_id=tick,
            snapshot_id=market.fields.get("snapshot_id", ""),
            timestamp_utc=market.fields.get("timestamp_utc", market.timestamp_utc),
            intent_id=intent.intent_id,
        )
        if observation is not None:
            if observation.observation_id in seen_observation_ids:
                issues.append(
                    SidecarIssue(
                        reason_code=SidecarReasonCode.DUPLICATE_OBSERVATION,
                        line_number=event.line_number,
                        system_state_id=event.system_state_id,
                        tick=tick,
                        detail=f"duplicate observation {observation.observation_id}",
                    )
                )
            else:
                seen_observation_ids.add(observation.observation_id)
                fields = add_legacy_execution_outcome(
                    observation,
                    legacy_action=event.fields.get("action", ""),
                    legacy_executed=event.fields.get("executed", "0") == "1",
                    legacy_position_before=event.fields.get("position_before", ""),
                    legacy_position_after=event.fields.get("position_after", ""),
                )
                observations.append(
                    SidecarObservationRecord(
                        observation_id=observation.observation_id,
                        system_state_id=event.system_state_id,
                        tick=tick,
                        source_market_sequence=market.sequence,
                        source_intent_sequence=intent.sequence,
                        source_execution_sequence=event.sequence,
                        fields=fields,
                    )
                )
        contexts.pop(key, None)

    config = settings.config
    frozen_statistics = statistics.freeze(
        observations=len(observations),
        issues=len(issues),
    )
    return SidecarReport(
        schema_version=SIDECAR_SCHEMA_VERSION,
        source_id=source_name,
        source_sha256=input_sha256,
        settings_mode=settings.mode,
        settings_reason_code=settings.reason_code,
        economics_profile_id="" if config is None else config.economics_profile_id,
        economics_model_version="" if config is None else config.economics_model_version,
        config_fingerprint="" if config is None else config.config_fingerprint,
        observations=tuple(observations),
        issues=tuple(issues),
        statistics=frozen_statistics,
    )


def analyze_l1_log_path(
    path: str | Path,
    *,
    settings: ShadowEconomicsSettings,
    source_id: Optional[str] = None,
) -> SidecarReport:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    return analyze_l1_log_text(
        text,
        settings=settings,
        source_id=source_path.name if source_id is None else source_id,
    )


def load_settings_json(path: str | Path) -> ShadowEconomicsSettings:
    config_path = Path(path)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.CONFIG_FILE_INVALID,
            f"cannot read valid JSON config from {config_path}",
        ) from exc
    if not isinstance(payload, dict):
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.CONFIG_FILE_INVALID,
            "sidecar config JSON root must be an object",
        )
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in payload.items()):
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.CONFIG_FILE_INVALID,
            "sidecar config keys and values must all be strings",
        )
    return load_shadow_settings(payload)


def write_report_atomic(
    report: SidecarReport,
    output_path: str | Path,
    *,
    source_path: Optional[str | Path] = None,
) -> Path:
    destination = Path(output_path)
    if source_path is not None and destination.resolve() == Path(source_path).resolve():
        raise PaperEconomicsSidecarError(
            SidecarReasonCode.INPUT_OUTPUT_COLLISION,
            "sidecar output must not overwrite its source log",
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        report.to_record(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(destination.parent),
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return destination


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only PEE shadow analysis of an existing structured L1 log.",
    )
    parser.add_argument("--input-log", required=True)
    parser.add_argument("--config-json", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--source-id", default="")
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    settings = load_settings_json(args.config_json)
    report = analyze_l1_log_path(
        args.input_log,
        settings=settings,
        source_id=args.source_id.strip() or None,
    )
    write_report_atomic(
        report,
        args.output_report,
        source_path=args.input_log,
    )
    print("PEE SHADOW SIDECAR")
    print("report_id:", report.report_id)
    print("source_sha256:", report.source_sha256)
    print("observations:", report.statistics.observations)
    print("issues:", report.statistics.issues)
    print("output_report:", args.output_report)
    return 0 if settings.mode == MODE_SHADOW and settings.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PaperEconomicsSidecarError",
    "ParsedLogEvent",
    "SIDECAR_SCHEMA_VERSION",
    "SidecarIssue",
    "SidecarObservationRecord",
    "SidecarReasonCode",
    "SidecarReport",
    "SidecarStatistics",
    "analyze_l1_log_path",
    "analyze_l1_log_text",
    "load_settings_json",
    "parse_l1_log_line",
    "write_report_atomic",
]
