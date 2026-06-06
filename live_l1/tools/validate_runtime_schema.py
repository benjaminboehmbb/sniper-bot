#!/usr/bin/env python3
# live_l1/tools/validate_runtime_schema.py
# P18B Live L1 runtime schema validator.
# ASCII-only. Read-only.

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_SCHEMA_VERSIONS = {0, 1}


@dataclass(frozen=True)
class SchemaCheck:
    name: str
    passed: bool
    detail: str


def _safe_int_or_none(value: object) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    bad = 0

    if not path.exists():
        return rows, bad

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if line == "":
                continue
            try:
                obj = json.loads(line)
            except Exception:
                bad += 1
                continue
            if not isinstance(obj, dict):
                bad += 1
                continue
            rows.append(obj)

    return rows, bad


def _read_json(path: Path) -> tuple[dict[str, Any] | None, int]:
    if not path.exists():
        return None, 0

    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, 1

    if not isinstance(obj, dict):
        return None, 1

    return obj, 0


def _schema_version(obj: dict[str, Any]) -> int | None:
    if "schema_version" not in obj:
        return 0
    return _safe_int_or_none(obj.get("schema_version"))


def _validate_rows(name: str, rows: list[dict[str, Any]], bad_json: int) -> SchemaCheck:
    if bad_json != 0:
        return SchemaCheck(name, False, f"bad_json_lines={bad_json}")

    unsupported = 0
    malformed = 0
    legacy = 0
    v1 = 0

    for row in rows:
        version = _schema_version(row)

        if version is None:
            malformed += 1
            continue

        if version == 0:
            legacy += 1
        elif version == 1:
            v1 += 1

        if version not in SUPPORTED_SCHEMA_VERSIONS:
            unsupported += 1

    if malformed:
        return SchemaCheck(name, False, f"malformed_schema_version_rows={malformed}")

    if unsupported:
        return SchemaCheck(name, False, f"unsupported_schema_version_rows={unsupported}")

    return SchemaCheck(name, True, f"rows={len(rows)} legacy_v0={legacy} schema_v1={v1}")


def _validate_json_file(name: str, obj: dict[str, Any] | None, bad_json: int) -> SchemaCheck:
    if bad_json != 0:
        return SchemaCheck(name, False, "bad_json")

    if obj is None:
        return SchemaCheck(name, True, "missing_allowed")

    version = _schema_version(obj)

    if version is None:
        return SchemaCheck(name, False, "malformed_schema_version")

    if version not in SUPPORTED_SCHEMA_VERSIONS:
        return SchemaCheck(name, False, f"unsupported_schema_version={version}")

    label = "legacy_v0" if version == 0 else "schema_v1"
    return SchemaCheck(name, True, label)


def validate_runtime_schema(
    *,
    audit_path: Path,
    trades_path: Path,
    s2_path: Path,
    loss_path: Path,
    s4_path: Path,
) -> list[SchemaCheck]:
    audit_rows, audit_bad = _read_jsonl(audit_path)
    trade_rows, trade_bad = _read_jsonl(trades_path)
    s2_rows, s2_bad = _read_jsonl(s2_path)
    loss_obj, loss_bad = _read_json(loss_path)
    s4_rows, s4_bad = _read_jsonl(s4_path)

    return [
        _validate_rows("execution_audit_schema", audit_rows, audit_bad),
        _validate_rows("trades_l1_schema", trade_rows, trade_bad),
        _validate_rows("s2_position_schema", s2_rows, s2_bad),
        _validate_json_file("loss_cluster_state_schema", loss_obj, loss_bad),
        _validate_rows("s4_risk_schema", s4_rows, s4_bad),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-log-path", default="live_logs/execution_audit.jsonl")
    parser.add_argument("--trades-path", default="live_logs/trades_l1.jsonl")
    parser.add_argument("--s2-position-path", default="live_state/s2_position.jsonl")
    parser.add_argument("--loss-cluster-state-path", default="live_state/loss_cluster_state.json")
    parser.add_argument("--s4-risk-path", default="live_state/s4_risk.jsonl")
    args = parser.parse_args()

    results = validate_runtime_schema(
        audit_path=Path(args.audit_log_path),
        trades_path=Path(args.trades_path),
        s2_path=Path(args.s2_position_path),
        loss_path=Path(args.loss_cluster_state_path),
        s4_path=Path(args.s4_risk_path),
    )

    print("P18B RUNTIME SCHEMA VALIDATION")
    print("")

    passed_all = True

    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status}: {item.name}: {item.detail}")
        if not item.passed:
            passed_all = False

    print("")
    print("RESULT:", "PASS" if passed_all else "FAIL")

    return 0 if passed_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
