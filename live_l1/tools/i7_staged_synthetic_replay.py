#!/usr/bin/env python3
"""Run the code-pinned, three-stage offline IU4 synthetic replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import stat
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGE_IDS = (
    "S1_BASELINE",
    "S2_CONTROLLED_RESTART",
    "S3_TRUNCATED_RESTART_FAIL_CLOSED",
)
STAGE_DIRECTORY_NAMES = ("stage-01", "stage-02", "stage-03")
INPUT_BINDINGS = {
    "fixture": {
        "path": "tests/fixtures/live_l1/IU4_I7_STAGED_SYNTHETIC_REPLAY_V1.txt",
        "sha256": "e7a1723a7bc766c4dbd3f1961e801a8a14e8e8b68a59f880afd1e8da94ffd915",
        "size": 209,
        "lines": 4,
        "encoding": "ascii",
        "schema_id": "IU4_I7_STAGED_SYNTHETIC_REPLAY_FIXTURE_V1",
    },
    "profile": {
        "path": "config/pee/PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json",
        "sha256": "f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86",
        "size": 716,
        "lines": 21,
        "encoding": "ascii",
        "schema_id": "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001",
    },
    "policy": {
        "path": "config/pee/PEE_RATE_X1_REPLAY_OBSERVATION_001.json",
        "sha256": "cfda0fb7f289f1cdad64328170af32cb69c11f886e42fcf7d1dbf606737627b2",
        "size": 459,
        "lines": 15,
        "encoding": "ascii",
        "schema_id": "PEE_RATE_X1_REPLAY_OBSERVATION_001",
    },
    "seed": {
        "path": "seeds/5m/btcusdt_5m_timing_core_v2.csv",
        "sha256": "6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5",
        "size": 239,
        "lines": 5,
        "encoding": "ascii-crlf",
        "schema_id": "BTCUSDT_5M_TIMING_CORE_V2",
    },
}
STAGES = (
    {
        "id": STAGE_IDS[0],
        "generated_at_utc": "2026-08-23T12:00:00Z",
        "restart_after_steps": None,
        "restart_fault_injection": None,
        "expected": {
            "requested_step_count": 3, "step_count": 3,
            "continuation_blocked": False, "restart_count": 0,
            "restart_fault_detected": False,
        },
    },
    {
        "id": STAGE_IDS[1],
        "generated_at_utc": "2026-08-23T12:01:00Z",
        "restart_after_steps": 1,
        "restart_fault_injection": None,
        "expected": {
            "requested_step_count": 3, "step_count": 3,
            "continuation_blocked": False, "restart_count": 1,
            "restart_fault_detected": False,
        },
    },
    {
        "id": STAGE_IDS[2],
        "generated_at_utc": "2026-08-23T12:02:00Z",
        "restart_after_steps": 1,
        "restart_fault_injection": "SNAPSHOT_TRUNCATED",
        "expected": {
            "requested_step_count": 3, "step_count": 1,
            "continuation_blocked": True, "restart_count": 1,
            "restart_fault_detected": True,
        },
    },
)
FIXTURE_HEADER = (
    "timestamp_utc", "open", "high", "low", "close", "volume",
    "allow_long", "allow_short", "regime_v2",
)
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PROFILE_EXACT = {
    "PEE_ECONOMICS_MODEL_VERSION": "PEE_V1",
    "PEE_ECONOMICS_PROFILE_ID": "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001",
    "PEE_ENTRY_FEE_RATE": "0.001", "PEE_ENTRY_SLIPPAGE_BPS": "5",
    "PEE_EXIT_FEE_RATE": "0.001", "PEE_EXIT_SLIPPAGE_BPS": "8",
    "PEE_MAX_DAILY_FEE_RATE": "0.0025", "PEE_MAX_DAILY_LOSS_RATE": "0.01",
    "PEE_MAX_POSITION_NOTIONAL_RATE": "0.10",
    "PEE_MAX_REALIZED_DRAWDOWN_RATE": "0.05",
    "PEE_MIN_NOTIONAL_QUOTE": "10", "PEE_MIN_QUANTITY": "0.00001",
    "PEE_MODE": "SHADOW", "PEE_QUANTITY_STEP": "0.000001",
    "PEE_QUOTE_CURRENCY": "USDT", "PEE_REFERENCE_STOP_RATE": "0.015",
    "PEE_RISK_PER_TRADE_RATE": "0.0025", "PEE_SCHEMA_VERSION": "1",
    "PEE_STARTING_EQUITY_QUOTE": "10000",
}
POLICY_EXACT = {
    "artifact_type": "pee_rate_calibration_policy", "schema_version": 1,
    "calibration_only": True, "operationally_approved": False,
    "policy": {
        "schema_version": 1,
        "policy_model_version": "PEE_RATE_CALIBRATION_V1",
        "policy_profile_id": "PEE_RATE_X1_REPLAY_OBSERVATION_001",
        "max_entries_per_utc_day": 1000000,
        "max_entries_per_rolling_window": 1000000,
        "rolling_window_seconds": 1,
        "min_reentry_cooldown_seconds": 1,
    },
}


class I7StagedReplayError(RuntimeError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if type(key) is not str or key in value:
            raise I7StagedReplayError("duplicate or non-string JSON key")
        value[key] = item
    return value


def _strict_ascii(payload: bytes, *, lines: int, encoding: str = "ascii") -> str:
    if (
        len(payload) == 0
        or not payload.endswith(b"\n")
        or payload.endswith(b"\n\n")
        or b"\0" in payload
        or payload.count(b"\n") != lines
    ):
        raise I7StagedReplayError("input encoding/LF/line-count mismatch")
    if encoding == "ascii" and b"\r" in payload:
        raise I7StagedReplayError("unexpected CR in LF input")
    if encoding == "ascii-crlf" and (
        payload.count(b"\r\n") != lines or payload.count(b"\r") != lines
    ):
        raise I7StagedReplayError("CRLF input encoding mismatch")
    if encoding not in {"ascii", "ascii-crlf"}:
        raise I7StagedReplayError("unknown input encoding")
    try:
        return payload.decode("ascii")
    except UnicodeError as exc:
        raise I7StagedReplayError("input is not strict ASCII") from exc


def _open_absolute_directory(path: Path) -> int:
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in path.parts[1:]:
            next_descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _open_bound_relative(relative: Path) -> tuple[int, list[int]]:
    root_descriptor = _open_absolute_directory(PROJECT_ROOT)
    descriptors = [root_descriptor]
    parent = root_descriptor
    try:
        for component in relative.parts[:-1]:
            descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent,
            )
            descriptors.append(descriptor)
            parent = descriptor
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_NOATIME"):
            flags |= os.O_NOATIME
        try:
            leaf = os.open(relative.parts[-1], flags, dir_fd=parent)
        except PermissionError:
            leaf = os.open(
                relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW,
                dir_fd=parent,
            )
        descriptors.append(leaf)
        return leaf, descriptors
    except Exception:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _verify_bound_chain(relative: Path, descriptors: list[int]) -> None:
    for index, component in enumerate(relative.parts):
        observed = os.stat(
            component, dir_fd=descriptors[index], follow_symlinks=False
        )
        opened = os.fstat(descriptors[index + 1])
        if (observed.st_dev, observed.st_ino, observed.st_mode) != (
            opened.st_dev, opened.st_ino, opened.st_mode
        ):
            raise I7StagedReplayError("input parent/leaf chain changed during read")


def _read_bound_input(name: str) -> tuple[Path, bytes]:
    binding = INPUT_BINDINGS[name]
    relative = Path(str(binding["path"]))
    if relative.is_absolute() or ".." in relative.parts:
        raise I7StagedReplayError("code-pinned input path is invalid")
    path = PROJECT_ROOT / relative
    initial = os.lstat(path)
    if (
        not stat.S_ISREG(initial.st_mode)
        or initial.st_nlink != 1
        or stat.S_IMODE(initial.st_mode) != 0o444
        or initial.st_uid != 1000
        or initial.st_gid != 1000
    ):
        raise I7StagedReplayError(f"{name} input metadata mismatch")
    descriptor, descriptors = _open_bound_relative(relative)
    try:
        opened = os.fstat(descriptor)
        blocks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        readback = os.fstat(descriptor)
        _verify_bound_chain(relative, descriptors)
    finally:
        for value in reversed(descriptors):
            os.close(value)
    final = os.lstat(path)
    identity = lambda value: (
        value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns,
    )
    if identity(initial) != identity(opened) or identity(opened) != identity(readback) or identity(readback) != identity(final):
        raise I7StagedReplayError(f"{name} input changed during read")
    payload = b"".join(blocks)
    if len(payload) != binding["size"]:
        raise I7StagedReplayError(f"{name} size mismatch")
    if hashlib.sha256(payload).hexdigest() != binding["sha256"]:
        raise I7StagedReplayError(f"{name} SHA-256 mismatch")
    _strict_ascii(
        payload, lines=int(binding["lines"]), encoding=str(binding["encoding"])
    )
    return path, payload


def _validate_json_inputs() -> None:
    for name in ("profile", "policy"):
        _, payload = _read_bound_input(name)
        try:
            value = json.loads(
                payload.decode("ascii"), object_pairs_hook=_pairs_no_duplicates
            )
        except json.JSONDecodeError as exc:
            raise I7StagedReplayError(f"{name} JSON malformed") from exc
        if type(value) is not dict:
            raise I7StagedReplayError(f"{name} JSON is not an exact object")
        if name == "profile":
            if value != PROFILE_EXACT or any(type(value[key]) is not str for key in PROFILE_EXACT):
                raise I7StagedReplayError("profile exact schema/type/value mismatch")
            if value["PEE_ECONOMICS_PROFILE_ID"] != INPUT_BINDINGS[name]["schema_id"]:
                raise I7StagedReplayError("profile identity cross-binding mismatch")
            decimal_fields = tuple(
                key for key in PROFILE_EXACT
                if key not in {
                    "PEE_ECONOMICS_MODEL_VERSION", "PEE_ECONOMICS_PROFILE_ID",
                    "PEE_MODE", "PEE_QUOTE_CURRENCY", "PEE_SCHEMA_VERSION",
                }
            )
            try:
                decimals = {key: Decimal(value[key]) for key in decimal_fields}
            except InvalidOperation as exc:
                raise I7StagedReplayError("profile decimal type/range mismatch") from exc
            if any(not item.is_finite() or item <= 0 for item in decimals.values()):
                raise I7StagedReplayError("profile decimal type/range mismatch")
            if (
                decimals["PEE_MIN_QUANTITY"] < decimals["PEE_QUANTITY_STEP"]
                or decimals["PEE_RISK_PER_TRADE_RATE"] > decimals["PEE_MAX_DAILY_LOSS_RATE"]
                or decimals["PEE_MAX_DAILY_FEE_RATE"] < decimals["PEE_ENTRY_FEE_RATE"] + decimals["PEE_EXIT_FEE_RATE"]
            ):
                raise I7StagedReplayError("profile cross-binding mismatch")
        if name == "policy":
            if (
                value != POLICY_EXACT
                or any(type(value[key]) is not type(expected) for key, expected in POLICY_EXACT.items())
                or any(type(value["policy"][key]) is not type(expected) for key, expected in POLICY_EXACT["policy"].items())
            ):
                raise I7StagedReplayError("policy exact schema/type/value mismatch")
            policy = value["policy"]
            if policy["policy_profile_id"] != INPUT_BINDINGS[name]["schema_id"]:
                raise I7StagedReplayError("policy identity cross-binding mismatch")
            if (
                policy["max_entries_per_rolling_window"] > policy["max_entries_per_utc_day"]
                or policy["min_reentry_cooldown_seconds"] < policy["rolling_window_seconds"]
            ):
                raise I7StagedReplayError("policy cross-binding mismatch")


def _validate_seed() -> None:
    _, payload = _read_bound_input("seed")
    rows = list(csv.reader(io.StringIO(payload.decode("ascii")), strict=True))
    if not rows or rows[0] != ["seed_id", "direction", "comb_json"] or len(rows) != 5:
        raise I7StagedReplayError("seed schema/cardinality mismatch")
    for row in rows[1:]:
        if len(row) != 3 or row[1] not in {"long", "short"} or not row[0]:
            raise I7StagedReplayError("malformed seed row")


def _validate_fixture() -> Path:
    path, payload = _read_bound_input("fixture")
    try:
        rows = list(csv.reader(io.StringIO(payload.decode("ascii")), strict=True))
    except csv.Error as exc:
        raise I7StagedReplayError("malformed fixture CSV") from exc
    if not rows or tuple(rows[0]) != FIXTURE_HEADER or len(rows) != 4:
        raise I7StagedReplayError("fixture header/cardinality mismatch")
    previous: int | None = None
    for row in rows[1:]:
        if len(row) != len(FIXTURE_HEADER) or not TIMESTAMP_RE.fullmatch(row[0]):
            raise I7StagedReplayError("malformed fixture row")
        try:
            timestamp_ns = int(datetime.fromisoformat(row[0].replace("Z", "+00:00")).timestamp() * 1_000_000_000)
            decimals = [Decimal(value) for value in row[1:6]]
        except (ValueError, InvalidOperation) as exc:
            raise I7StagedReplayError("fixture timestamp/decimal mismatch") from exc
        if any(not value.is_finite() or value < 0 for value in decimals):
            raise I7StagedReplayError("fixture numeric value is invalid")
        if row[6] not in {"0", "1"} or row[7] not in {"0", "1"} or row[8] not in {"0", "1"}:
            raise I7StagedReplayError("fixture flags must be exact integers")
        if previous is not None and timestamp_ns <= previous:
            raise I7StagedReplayError("fixture timestamps are not strictly increasing")
        previous = timestamp_ns
    return path


def _new_tmp_root(path: Path) -> Path:
    if not path.is_absolute() or ".." in path.parts or path.is_symlink():
        raise I7StagedReplayError("run root path is invalid")
    parent = path.parent.resolve(strict=True)
    if parent != Path("/tmp") and Path("/tmp") not in parent.parents:
        raise I7StagedReplayError("run root must be below /tmp")
    if path.exists():
        raise I7StagedReplayError("run root must be create-new")
    path.mkdir(mode=0o700)
    root = path.resolve(strict=True)
    if Path("/tmp") not in root.parents:
        raise I7StagedReplayError("run root confinement failed")
    return root


def _stage_output(root: Path, index: int) -> Path:
    if type(index) is not int or index < 0 or index >= len(STAGE_DIRECTORY_NAMES):
        raise I7StagedReplayError("stage index is invalid")
    output = root / STAGE_DIRECTORY_NAMES[index]
    if output.exists() or output.is_symlink():
        raise I7StagedReplayError("old stage artifact exists")
    if output.parent.resolve(strict=True) != root:
        raise I7StagedReplayError("stage output escapes run root")
    return output


def _write_new(path: Path, payload: bytes) -> None:
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _validate_stage(stage: dict[str, object], index: int, fixture: Path, root: Path) -> dict[str, Any]:
    if stage is not STAGES[index] or stage["id"] != STAGE_IDS[index]:
        raise I7StagedReplayError("stage authority/order mismatch")
    _validate_json_inputs()
    _validate_seed()
    fixture = _validate_fixture()
    output = _stage_output(root, index)
    output.mkdir(mode=0o700)
    _, fixture_payload = _read_bound_input("fixture")
    rows = list(csv.reader(io.StringIO(fixture_payload.decode("ascii")), strict=True))[1:]
    requested = len(rows)
    restart_count = 0
    restart_fault_detected = False
    continuation_blocked = False
    step_count = requested
    if stage["restart_after_steps"] is not None:
        restart_count = 1
        state_base = {
            "schema_version": 1,
            "stage_id": STAGE_IDS[index],
            "cursor": stage["restart_after_steps"],
            "last_timestamp_utc": rows[int(stage["restart_after_steps"]) - 1][0],
            "input_sha256": INPUT_BINDINGS["fixture"]["sha256"],
        }
        state = {
            **state_base,
            "state_sha256": hashlib.sha256(_canonical(state_base)).hexdigest(),
        }
        state_path = output / "restart_state.json"
        if stage["restart_fault_injection"] == "SNAPSHOT_TRUNCATED":
            _write_new(state_path, (_canonical(state) + b"\n")[:17])
            try:
                payload = state_path.read_bytes()
                if not payload.endswith(b"\n"):
                    raise I7StagedReplayError("truncated restart snapshot")
                json.loads(payload.decode("ascii"), object_pairs_hook=_pairs_no_duplicates)
            except (UnicodeError, json.JSONDecodeError, I7StagedReplayError):
                restart_fault_detected = True
                continuation_blocked = True
                step_count = int(stage["restart_after_steps"])
        else:
            _write_new(state_path, _canonical(state) + b"\n")
            restored = json.loads(
                state_path.read_text(encoding="ascii"),
                object_pairs_hook=_pairs_no_duplicates,
            )
            restored_hash = restored.pop("state_sha256")
            if hashlib.sha256(_canonical(restored)).hexdigest() != restored_hash:
                raise I7StagedReplayError("restart state hash mismatch")
    observed = {
        "requested_step_count": requested,
        "step_count": step_count,
        "continuation_blocked": continuation_blocked,
        "restart_count": restart_count,
        "restart_fault_detected": restart_fault_detected,
    }
    receipt = {
        "artifact_type": "IU4_I7_SYNTHETIC_STAGE_RECEIPT",
        "schema_version": 1,
        "stage_id": STAGE_IDS[index],
        "generated_at_utc": stage["generated_at_utc"],
        "result": observed,
        "chain_checks": {
            "fixture_identity": True,
            "profile_identity": True,
            "policy_identity": True,
            "seed_identity": True,
            "stage_order": True,
        },
        "iu4_enforced_enabled": False,
        "exchange_enabled": False,
        "live_enabled": False,
    }
    receipt_path = output / "stage_receipt.json"
    _write_new(receipt_path, _canonical(receipt) + b"\n")
    run_manifest = {
        "artifact_type": "IU4_I7_SYNTHETIC_STAGE_MANIFEST",
        "schema_version": 1,
        "stage_id": STAGE_IDS[index],
        "input_bindings": INPUT_BINDINGS,
    }
    run_manifest_path = output / "run_manifest.json"
    _write_new(run_manifest_path, _canonical(run_manifest) + b"\n")
    if observed != stage["expected"]:
        raise I7StagedReplayError(f"stage {STAGE_IDS[index]} mismatch")
    if type(receipt.get("chain_checks")) is not dict or not receipt["chain_checks"] or not all(value is True for value in receipt["chain_checks"].values()):
        raise I7StagedReplayError("stage chain check failed")
    if any(receipt[name] is not False for name in (
        "iu4_enforced_enabled", "exchange_enabled", "live_enabled"
    )):
        raise I7StagedReplayError("stage crossed activation boundary")
    return {
        "id": STAGE_IDS[index],
        "directory": STAGE_DIRECTORY_NAMES[index],
        "result": "PASS",
        "expected": dict(stage["expected"]),
        "observed": observed,
        "run_manifest_sha256": hashlib.sha256(run_manifest_path.read_bytes()).hexdigest(),
        "pipeline_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    }


def run_staged_replay(*, run_root: Path) -> dict[str, Any]:
    _validate_json_inputs()
    _validate_seed()
    fixture = _validate_fixture()
    root = _new_tmp_root(run_root)
    records = [
        _validate_stage(stage, index, fixture, root)
        for index, stage in enumerate(STAGES)
    ]
    evidence_base = {
        "artifact_type": "IU4_I7_STAGED_SYNTHETIC_REPLAY_EVIDENCE",
        "schema_version": 2,
        "input_bindings": INPUT_BINDINGS,
        "stage_ids": list(STAGE_IDS),
        "stage_count": len(records),
        "stages": records,
        "iu4_enforced_enabled": False,
        "exchange_enabled": False,
        "live_enabled": False,
        "result": "PASS",
    }
    evidence = {
        **evidence_base,
        "evidence_fingerprint": hashlib.sha256(_canonical(evidence_base)).hexdigest(),
    }
    evidence_path = root / "staged_replay_evidence.json"
    descriptor = os.open(
        evidence_path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
    )
    try:
        os.write(descriptor, _canonical(evidence) + b"\n")
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return {
        **evidence,
        "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        result = run_staged_replay(run_root=args.run_root)
    except Exception as exc:
        print(f"I7_STAGED_SYNTHETIC_REPLAY: FAIL: {exc}")
        return 1
    count = result["stage_count"]
    print(f"I7_STAGED_SYNTHETIC_REPLAY: {count}/{count} PASS")
    print(f"EVIDENCE_SHA256: {result['evidence_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "INPUT_BINDINGS", "I7StagedReplayError", "STAGES", "STAGE_IDS",
    "run_staged_replay",
]
