from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_text, ts_key
    from .label_registry import assign_human_labels, load_human_labels, load_label_registry
    from .regime_identity_rows import build_regime_index, build_rows
else:
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_text, ts_key
    from label_registry import assign_human_labels, load_human_labels, load_label_registry
    from regime_identity_rows import build_regime_index, build_rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        raise FileNotFoundError(
            "Missing file: "
            + str(path)
            + "\nUse --archive-dir to point to an archive containing trades_l1.jsonl and execution_audit.jsonl."
        )

    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            s = raw.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception as exc:
                raise ValueError(f"Bad JSON in {path} line {line_no}: {exc}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Non-object JSON in {path} line {line_no}")
            rows.append(obj)
    return rows


def market_timestamp(row: dict[str, Any]) -> str:
    for key in ("timestamp_utc", "timestamp", "open_time"):
        value = safe_text(row.get(key))
        if value:
            return ts_key(value)
    return ""


def market_price(row: dict[str, Any]) -> float:
    for key in ("close", "price", "close_price"):
        value = row.get(key)
        if value is not None and safe_text(value) != "":
            return safe_float(value, 0.0)
    return 0.0


def parse_market_rows(path: Path) -> tuple[list[str], list[float]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing market CSV: {path}")

    timestamps: list[str] = []
    prices: list[float] = []

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts = market_timestamp(row)
            price = market_price(row)
            if ts and price > 0:
                timestamps.append(ts)
                prices.append(price)

    return timestamps, prices


def parse_key_value_log(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            s = raw.strip()
            if "event=regime_snapshot" not in s:
                continue

            row: dict[str, Any] = {}
            parts = s.split()
            for part in parts:
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                row[key] = value

            if row:
                rows.append(row)

    return rows


def load_archive_registry_md(registry_path: Path) -> list[dict[str, str]]:
    if not registry_path.exists():
        raise SystemExit(f"Archive registry not found: {registry_path}")

    rows: list[dict[str, str]] = []
    table_lines: list[str] = []

    for line in registry_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)

    if len(table_lines) < 3:
        raise SystemExit(f"No markdown table found in archive registry: {registry_path}")

    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    data_lines = table_lines[2:]

    for line in data_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        row = dict(zip(header, cells))
        include_value = safe_text(row.get("include_in_v7")).lower()
        if include_value in {"yes", "1", "true", "y"}:
            rows.append(row)

    if not rows:
        raise SystemExit(f"No included archives found in registry: {registry_path}")

    return rows


def load_rows_for_archive(archive_id: str, archive_path: Path, market_csv: Path, label_list_path: Path, label_registry_path: Path) -> list[dict[str, Any]]:
    trades = read_jsonl(archive_path / "trades_l1.jsonl")
    audit_rows = read_jsonl(archive_path / "execution_audit.jsonl")
    log_rows = parse_key_value_log(archive_path / "l1_paper.log")
    regime_index = build_regime_index(log_rows)
    timestamps, prices = parse_market_rows(market_csv)
    label_list = load_human_labels(label_list_path)
    existing_registry = load_label_registry(label_registry_path)
    label_map = assign_human_labels(trades, label_list, existing_registry)

    rows = build_rows(trades, audit_rows, regime_index, timestamps, prices, label_map)

    enriched: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        local_trade_id = (
            row.get("trade_id")
            or row.get("stable_trade_id")
            or row.get("local_trade_id")
            or row.get("id")
            or f"T{idx:06d}"
        )
        out = dict(row)
        out["archive_id"] = archive_id
        out["archive_path"] = str(archive_path)
        out["local_trade_id"] = local_trade_id
        out["global_trade_id"] = f"{archive_id}::{local_trade_id}"
        out["v7g_archive_row_index"] = idx
        enriched.append(out)

    return enriched


def export_multi_archive_loader(
    registry_path: Path,
    output_dir: Path,
    market_csv: Path,
    label_list_path: Path,
    label_registry_path: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    registry_rows = load_archive_registry_md(registry_path)

    all_rows: list[dict[str, Any]] = []
    archive_summary: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for registry_row in registry_rows:
        archive_id = safe_text(registry_row.get("archive_id"))
        archive_path = Path(safe_text(registry_row.get("archive_path")))

        if not archive_id:
            errors.append({
                "archive_id": "",
                "archive_path": str(archive_path),
                "error": "missing_archive_id",
            })
            continue

        if not archive_path.exists():
            errors.append({
                "archive_id": archive_id,
                "archive_path": str(archive_path),
                "error": "archive_path_missing",
            })
            continue

        trades_path = archive_path / "trades_l1.jsonl"
        audit_path = archive_path / "execution_audit.jsonl"
        log_path = archive_path / "l1_paper.log"

        missing_inputs = []
        for required_path in [trades_path, audit_path, log_path]:
            if not required_path.exists():
                missing_inputs.append(str(required_path))

        if missing_inputs:
            errors.append({
                "archive_id": archive_id,
                "archive_path": str(archive_path),
                "error": "required_input_missing",
                "missing_inputs": "|".join(missing_inputs),
            })
            continue

        try:
            rows = load_rows_for_archive(
                archive_id,
                archive_path,
                market_csv,
                label_list_path,
                label_registry_path,
            )
        except Exception as exc:
            errors.append({
                "archive_id": archive_id,
                "archive_path": str(archive_path),
                "error": type(exc).__name__,
                "message": str(exc),
            })
            continue

        all_rows.extend(rows)

        archive_summary.append({
            "archive_id": archive_id,
            "archive_path": str(archive_path),
            "trade_count": len(rows),
            "run_label": safe_text(registry_row.get("run_label")),
            "created_at": safe_text(registry_row.get("created_at")),
            "source_device": safe_text(registry_row.get("source_device")),
            "strategy_profile": safe_text(registry_row.get("strategy_profile")),
            "status": "LOADED",
        })

    write_csv_rows(output_dir / "multi_archive_global_trades_v7g.csv", all_rows)
    write_csv_rows(output_dir / "multi_archive_registry_loaded_v7g.csv", archive_summary)
    write_csv_rows(output_dir / "multi_archive_loader_errors_v7g.csv", errors)

    archive_count = len(archive_summary)
    trade_count = len(all_rows)

    manifest = [{
        "engine_version": "v7g",
        "registry_path": str(registry_path),
        "archives_registered": len(registry_rows),
        "archives_loaded": archive_count,
        "trade_count": trade_count,
        "errors": len(errors),
        "mode": "multi_archive_loader",
        "statistical_interpretation_allowed": "yes" if archive_count >= 2 and trade_count >= 30 else "no",
        "minimum_recommended_archives": 2,
        "minimum_recommended_trades": 30,
    }]
    write_csv_rows(output_dir / "multi_archive_loader_v7g_manifest.csv", manifest)

    summary_path = output_dir / "v7g_multi_archive_loader_summary.md"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# V7G MULTI-ARCHIVE LOADER SUMMARY\n\n")
        fh.write("Status: infrastructure export\n\n")
        fh.write(f"registry_path: {registry_path}\n")
        fh.write(f"archives_registered: {len(registry_rows)}\n")
        fh.write(f"archives_loaded: {archive_count}\n")
        fh.write(f"trade_count: {trade_count}\n")
        fh.write(f"errors: {len(errors)}\n\n")
        fh.write("Interpretation rule:\n\n")
        if archive_count >= 2 and trade_count >= 30:
            fh.write("statistical_interpretation_allowed: yes\n")
        else:
            fh.write("statistical_interpretation_allowed: no\n")
            fh.write("\nCurrent output validates loader infrastructure only.\n")

    print("Multi-archive loader export directory:", output_dir)
    print("registry_path:", registry_path)
    print("archives_registered:", len(registry_rows))
    print("archives_loaded:", archive_count)
    print("trade_count:", trade_count)
    print("errors:", len(errors))
    for path in sorted(output_dir.glob("*")):
        print(" -", path)
