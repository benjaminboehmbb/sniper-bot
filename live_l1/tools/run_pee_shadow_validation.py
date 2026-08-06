#!/usr/bin/env python3
"""Reproducible, isolated PEE IU-3 SHADOW validation runner."""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from live_l1.core.loop import run_l1_loop_step1234567
from live_l1.tools.paper_economics_shadow_sidecar import (
    analyze_l1_log_path,
    load_settings_json,
    parse_l1_log_line,
    write_report_atomic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SliceStatistics:
    source_rows_scanned: int
    invalid_rows_skipped: int
    valid_offset_rows_skipped: int
    rows_written: int
    first_timestamp_utc: str
    last_timestamp_utc: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _positive_price(value: object) -> bool:
    try:
        price = float(str(value).strip())
    except (TypeError, ValueError):
        return False
    return math.isfinite(price) and price > 0.0


def _normalized_fieldnames(source_fieldnames: list[str]) -> tuple[list[str], str]:
    if "timestamp_utc" in source_fieldnames:
        timestamp_source = "timestamp_utc"
        output = list(source_fieldnames)
    elif "open_time_iso" in source_fieldnames:
        timestamp_source = "open_time_iso"
        output = [
            "timestamp_utc" if name == "open_time_iso" else name
            for name in source_fieldnames
        ]
    else:
        raise ValueError("source CSV requires timestamp_utc or open_time_iso")
    if "close" not in source_fieldnames:
        raise ValueError("source CSV requires close")
    if len(set(output)) != len(output):
        raise ValueError("normalized CSV field names are not unique")
    return output, timestamp_source


def write_normalized_slice(
    *,
    source_path: Path,
    destination_path: Path,
    max_ticks: int,
    valid_row_offset: int,
) -> SliceStatistics:
    if max_ticks < 1:
        raise ValueError("max_ticks must be positive")
    if valid_row_offset < 0:
        raise ValueError("valid_row_offset must not be negative")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination_path.with_name(f".{destination_path.name}.tmp")
    scanned = invalid = offset_skipped = written = 0
    first_timestamp = last_timestamp = ""

    try:
        with source_path.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None:
                raise ValueError("source CSV has no header")
            output_fields, timestamp_source = _normalized_fieldnames(
                list(reader.fieldnames)
            )
            with temporary_path.open("w", encoding="utf-8", newline="") as target:
                writer = csv.DictWriter(
                    target,
                    fieldnames=output_fields,
                    extrasaction="ignore",
                    lineterminator="\n",
                )
                writer.writeheader()
                for source_row in reader:
                    scanned += 1
                    timestamp = str(source_row.get(timestamp_source, "")).strip()
                    if not timestamp or not _positive_price(source_row.get("close")):
                        invalid += 1
                        continue
                    if offset_skipped < valid_row_offset:
                        offset_skipped += 1
                        continue

                    output_row = dict(source_row)
                    if timestamp_source != "timestamp_utc":
                        output_row.pop(timestamp_source, None)
                    output_row["timestamp_utc"] = timestamp
                    writer.writerow(output_row)
                    written += 1
                    first_timestamp = first_timestamp or timestamp
                    last_timestamp = timestamp
                    if written == max_ticks:
                        break
                target.flush()
                os.fsync(target.fileno())
        if written != max_ticks:
            raise ValueError(
                f"source contains only {written} usable rows after offset; "
                f"required {max_ticks}"
            )
        os.replace(temporary_path, destination_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return SliceStatistics(
        source_rows_scanned=scanned,
        invalid_rows_skipped=invalid,
        valid_offset_rows_skipped=offset_skipped,
        rows_written=written,
        first_timestamp_utc=first_timestamp,
        last_timestamp_utc=last_timestamp,
    )


def _git_head() -> str:
    result = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _execution_statistics(log_path: Path) -> dict[str, Any]:
    integrated_ids: list[str] = []
    execution_events = executed_transitions = 0
    actions: dict[str, int] = {}
    non_empty_lines = 0
    with log_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            non_empty_lines += 1
            event = parse_l1_log_line(raw_line, line_number)
            if event.event == "paper_economics_shadow":
                observation_id = str(event.fields.get("observation_id", ""))
                if not observation_id:
                    raise ValueError("integrated SHADOW event misses observation_id")
                integrated_ids.append(observation_id)
            if event.event == "execution":
                execution_events += 1
                if event.fields.get("executed") == "1":
                    executed_transitions += 1
                    action = str(event.fields.get("action", ""))
                    actions[action] = actions.get(action, 0) + 1
    return {
        "log_lines": non_empty_lines,
        "execution_events": execution_events,
        "executed_transitions": executed_transitions,
        "executed_actions": dict(sorted(actions.items())),
        "integrated_observation_ids": integrated_ids,
    }


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    temporary_path = path.with_name(f".{path.name}.tmp")
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"
    try:
        with temporary_path.open("w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def run_validation(
    *,
    source_csv: Path,
    expected_source_sha256: str,
    profile_json: Path,
    seed_csv: Path,
    output_directory: Path,
    max_ticks: int,
    valid_row_offset: int,
    source_id: str,
) -> dict[str, Any]:
    expected_hash = expected_source_sha256.strip().lower()
    if len(expected_hash) != 64:
        raise ValueError("expected_source_sha256 must contain 64 hex characters")
    if output_directory.exists():
        raise FileExistsError(f"output directory already exists: {output_directory}")

    source_hash = _sha256_file(source_csv)
    if source_hash != expected_hash:
        raise ValueError(
            f"source SHA-256 mismatch: expected {expected_hash}, got {source_hash}"
        )

    settings = load_settings_json(profile_json)
    if not settings.ready or settings.config is None:
        raise ValueError(
            f"profile is not ready for SHADOW: {settings.reason_code} {settings.detail}"
        )
    profile_payload = _json_object(profile_json)
    output_directory.mkdir(parents=True)
    data_directory = output_directory / "data"
    log_directory = output_directory / "live_logs"
    state_directory = output_directory / "live_state"
    data_directory.mkdir()
    log_directory.mkdir()
    state_directory.mkdir()

    started_utc = _utc_now()
    market_path = data_directory / "market.csv"
    slice_statistics = write_normalized_slice(
        source_path=source_csv,
        destination_path=market_path,
        max_ticks=max_ticks,
        valid_row_offset=valid_row_offset,
    )
    market_hash = _sha256_file(market_path)
    log_path = log_directory / "l1.log"
    stdout_path = log_directory / "stdout.log"
    environment = {
        str(key): str(value)
        for key, value in profile_payload.items()
    }
    environment.update(
        {
            "L1_LOG_PATH": str(log_path),
            "L1_MARKET_CSV_PATH": str(market_path),
            "SEEDS_5M_CSV": str(seed_csv),
            "L1_DECISION_TICK_SECONDS": "0",
            "L1_REQUIRE_WSL": "0",
            "L1_AUDIT_LOG_PATH": str(log_directory / "execution.jsonl"),
            "L1_TRADE_LOG_PATH": str(log_directory / "trades.jsonl"),
            "L1_LOSS_CLUSTER_STATE_PATH": str(
                state_directory / "loss_cluster.json"
            ),
        }
    )
    previous_environment = os.environ.copy()
    try:
        os.environ.update(environment)
        with stdout_path.open("w", encoding="utf-8") as stdout_handle:
            with contextlib.redirect_stdout(stdout_handle):
                runtime_rc = run_l1_loop_step1234567(
                    str(output_directory),
                    max_ticks=max_ticks,
                )
    finally:
        os.environ.clear()
        os.environ.update(previous_environment)
    if runtime_rc != 0:
        raise RuntimeError(f"L1 SHADOW runtime failed with return code {runtime_rc}")

    sidecar_report_path = log_directory / "sidecar_report.json"
    sidecar_report = analyze_l1_log_path(
        log_path,
        settings=settings,
        source_id=source_id,
    )
    write_report_atomic(
        sidecar_report,
        sidecar_report_path,
        source_path=log_path,
    )
    execution = _execution_statistics(log_path)
    sidecar_ids = [item.observation_id for item in sidecar_report.observations]
    if execution["integrated_observation_ids"] != sidecar_ids:
        raise RuntimeError("integrated and sidecar observation IDs differ")
    if sidecar_report.statistics.issues != 0:
        raise RuntimeError(
            f"sidecar reported {sidecar_report.statistics.issues} issues"
        )

    output_hashes = {
        str(path.relative_to(output_directory)): _sha256_file(path)
        for path in (
            market_path,
            log_path,
            stdout_path,
            sidecar_report_path,
            state_directory / "s2_position.jsonl",
            state_directory / "s4_risk.jsonl",
        )
    }
    finished_utc = _utc_now()
    manifest = {
        "schema_version": RUN_SCHEMA_VERSION,
        "artifact_type": "pee_iu3_shadow_validation_manifest",
        "source_id": source_id,
        "git_commit": _git_head(),
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "source_csv": {
            "path": str(source_csv),
            "sha256": source_hash,
        },
        "normalized_market_slice": {
            **asdict(slice_statistics),
            "valid_row_offset": valid_row_offset,
            "sha256": market_hash,
        },
        "profile": {
            "path": str(profile_json),
            "file_sha256": _sha256_file(profile_json),
            "economics_profile_id": settings.config.economics_profile_id,
            "economics_model_version": settings.config.economics_model_version,
            "config_fingerprint": settings.config.config_fingerprint,
        },
        "seed_csv": {
            "path": str(seed_csv),
            "sha256": _sha256_file(seed_csv),
        },
        "runtime": {
            "return_code": runtime_rc,
            "max_ticks": max_ticks,
            **execution,
        },
        "sidecar": {
            "report_id": sidecar_report.report_id,
            "observations": sidecar_report.statistics.observations,
            "issues": sidecar_report.statistics.issues,
            "observation_ids_match_integrated": True,
        },
        "output_hashes": output_hashes,
    }
    manifest_path = output_directory / "run_manifest.json"
    _write_json_atomic(manifest_path, manifest)
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an isolated, hash-bound PEE IU-3 SHADOW validation.",
    )
    parser.add_argument("--source-csv", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--profile-json", required=True)
    parser.add_argument("--seed-csv", required=True)
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--max-ticks", required=True, type=int)
    parser.add_argument("--valid-row-offset", type=int, default=0)
    parser.add_argument("--source-id", required=True)
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    manifest = run_validation(
        source_csv=Path(args.source_csv).resolve(),
        expected_source_sha256=args.expected_source_sha256,
        profile_json=Path(args.profile_json).resolve(),
        seed_csv=Path(args.seed_csv).resolve(),
        output_directory=Path(args.output_directory).resolve(),
        max_ticks=args.max_ticks,
        valid_row_offset=args.valid_row_offset,
        source_id=args.source_id,
    )
    print("PEE IU-3 SHADOW VALIDATION")
    print("git_commit:", manifest["git_commit"])
    print("max_ticks:", manifest["runtime"]["max_ticks"])
    print("observations:", manifest["sidecar"]["observations"])
    print("issues:", manifest["sidecar"]["issues"])
    print("output_directory:", args.output_directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "SliceStatistics",
    "run_validation",
    "write_normalized_slice",
]
