from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import compute_root_cause_attribution
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_int, safe_text
else:
    from aggregate_csv import compute_root_cause_attribution
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_int, safe_text


def export_cross_archive_root_cause(rows: list[dict[str, Any]], output_dir: Path, archive_id: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_archive_ids = sorted({str(row.get("archive_id", "")).strip() for row in rows if str(row.get("archive_id", "")).strip()})
    archive_count = len(source_archive_ids)
    statistical_allowed = "yes" if archive_count >= 2 and len(rows) >= 30 else "no"
    export_mode = "multi_archive_analysis" if archive_count >= 2 else "single_archive_infrastructure_validation"

    enriched_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        local_trade_id = (
            row.get("trade_id")
            or row.get("stable_trade_id")
            or row.get("local_trade_id")
            or row.get("id")
            or f"T{idx:06d}"
        )
        global_trade_id = f"{archive_id}::{local_trade_id}"

        enriched_rows.append({
            "archive_id": archive_id,
            "local_trade_id": local_trade_id,
            "global_trade_id": global_trade_id,
            "trade_index": safe_int(row.get("trade_index"), idx),
            "symbol": safe_text(row.get("symbol")),
            "side": safe_text(row.get("side")),
            "entry_time_chart": safe_text(row.get("entry_time_chart")),
            "exit_time_chart": safe_text(row.get("exit_time_chart")),
            "pnl": safe_float(row.get("pnl"), 0.0),
            "pnl_pct": safe_float(row.get("pnl_pct"), 0.0),
            "quality_score": safe_int(row.get("quality_score"), 0),
            "quality_class": safe_text(row.get("quality_class")),
            "root_cause": safe_text(row.get("root_cause")) or "unknown_cause",
            "root_cause_weight": safe_int(row.get("root_cause_weight"), 0),
            "root_cause_confidence": safe_int(row.get("root_cause_confidence"), 0),
            "cause_weights": safe_text(row.get("cause_weights")),
            "opportunity_loss_24h_pct": safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
            "additional_cause_1": safe_text(row.get("additional_cause_1")),
            "additional_cause_1_weight": safe_int(row.get("additional_cause_1_weight"), 0),
            "additional_cause_2": safe_text(row.get("additional_cause_2")),
            "additional_cause_2_weight": safe_int(row.get("additional_cause_2_weight"), 0),
            "priority": safe_text(row.get("priority")),
            "priority_score": safe_int(row.get("priority_score"), 0),
            "impact_score": safe_int(row.get("impact_score"), 0),
            "trade_family": safe_text(row.get("trade_family")),
            "trade_family_group": safe_text(row.get("trade_family_group")),
            "entry_regime_label": safe_text(row.get("entry_regime_label")),
            "exit_regime_label": safe_text(row.get("exit_regime_label")),
            "entry_risk_label": safe_text(row.get("entry_risk_label")),
            "exit_risk_label": safe_text(row.get("exit_risk_label")),
        })

    attribution = compute_root_cause_attribution(enriched_rows)

    for row in attribution:
        row["archive_scope"] = "single_archive_validation"
        row["archive_count"] = 1
        row["source_archive_id"] = archive_id
        row["statistical_interpretation_allowed"] = statistical_allowed

    write_csv_rows(output_dir / "cross_archive_root_cause_trades_v7d.csv", enriched_rows)
    write_csv_rows(output_dir / "cross_archive_root_cause_attribution_v7d.csv", attribution)

    manifest = [{
        "engine_version": "v7d",
        "archive_id": archive_id,
        "archive_count": archive_count,
        "trade_count": len(enriched_rows),
        "root_cause_groups": len(attribution),
        "mode": export_mode,
        "statistical_interpretation_allowed": statistical_allowed,
        "minimum_recommended_archives": 2,
        "minimum_recommended_trades": 30,
    }]
    write_csv_rows(output_dir / "cross_archive_root_cause_v7d_manifest.csv", manifest)

    summary_path = output_dir / "v7d_cross_archive_root_cause_summary.md"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# V7D CROSS-ARCHIVE ROOT CAUSE SUMMARY\n\n")
        fh.write("Status: infrastructure export\n\n")
        fh.write(f"archive_id: {archive_id}\n")
        fh.write(f"archive_count: {archive_count}\n")
        fh.write(f"trade_count: {len(enriched_rows)}\n")
        fh.write(f"root_cause_groups: {len(attribution)}\n\n")
        fh.write("Important limitation:\n\n")
        fh.write("This output validates the V7D cross-archive analysis pipeline.\n")
        fh.write(f"statistical_interpretation_allowed: {statistical_allowed}\n")

    print("Cross-archive root cause export directory:", output_dir)
    print("archive_id:", archive_id)
    print("trades:", len(enriched_rows))
    print("root_cause_groups:", len(attribution))
    for path in sorted(output_dir.glob("*")):
        print(" -", path)
