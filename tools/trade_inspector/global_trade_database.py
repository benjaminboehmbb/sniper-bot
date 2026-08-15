from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
else:
    from csv_persistence import write_csv_rows


def export_global_trade_database(rows: list[dict[str, Any]], output_dir: Path, archive_id: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    global_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        local_trade_id = (
            row.get("trade_id")
            or row.get("stable_trade_id")
            or row.get("local_trade_id")
            or row.get("id")
            or f"T{idx:06d}"
        )

        global_trade_id = f"{archive_id}::{local_trade_id}"

        out = dict(row)
        out["archive_id"] = archive_id
        out["local_trade_id"] = local_trade_id
        out["global_trade_id"] = global_trade_id
        out["v7_global_row_index"] = idx

        global_rows.append(out)

    write_csv_rows(output_dir / "global_trades_v7c.csv", global_rows)

    summary_path = output_dir / "v7c_global_trade_database_summary.md"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# V7C GLOBAL TRADE DATABASE SUMMARY\n\n")
        fh.write("Status: infrastructure export\n\n")
        fh.write(f"archive_id: {archive_id}\n")
        fh.write(f"trade_count: {len(global_rows)}\n")
        fh.write("mode: single-archive validation\n\n")
        fh.write("Important limitation:\n\n")
        fh.write("This output validates the V7C infrastructure only.\n")
        fh.write("It must not be interpreted as statistically robust cross-archive analysis yet.\n")

    manifest = [{
        "archive_id": archive_id,
        "trade_count": len(global_rows),
        "output_file": "global_trades_v7c.csv",
        "summary_file": "v7c_global_trade_database_summary.md",
        "status": "infrastructure_validation",
        "statistical_interpretation_allowed": "no",
    }]
    write_csv_rows(output_dir / "global_trades_v7c_manifest.csv", manifest)

    print("Global trade database export directory:", output_dir)
    print("archive_id:", archive_id)
    print("global_trades:", len(global_rows))
    for path in sorted(output_dir.glob("*")):
        print(" -", path)
