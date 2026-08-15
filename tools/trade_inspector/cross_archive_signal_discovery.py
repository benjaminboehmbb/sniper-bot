from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .feature_discovery import discover_pair_groups, discover_signal_groups
    from .inspection_primitives import safe_float, safe_text
else:
    from csv_persistence import write_csv_rows
    from feature_discovery import discover_pair_groups, discover_signal_groups
    from inspection_primitives import safe_float, safe_text


def export_cross_archive_signal_discovery(rows: list[dict[str, Any]], output_dir: Path, archive_id: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_archive_ids = sorted({str(row.get("archive_id", "")).strip() for row in rows if str(row.get("archive_id", "")).strip()})
    archive_count = len(source_archive_ids)
    statistical_allowed = "yes" if archive_count >= 2 and len(rows) >= 30 else "no"
    export_mode = "multi_archive_analysis" if archive_count >= 2 else "single_archive_infrastructure_validation"

    group_keys = [
        "entry_regime_label",
        "entry_risk_label",
        "regime_aligned",
        "risk_good_at_entry",
        "entry_score_at_entry",
        "entry_atr_signal",
        "entry_ma200_signal",
        "entry_mfi_signal",
        "trade_family_group",
        "trade_family",
    ]

    all_discoveries: list[dict[str, Any]] = []

    for key in group_keys:
        result = discover_signal_groups(rows, key)
        enriched = []
        for item in result:
            out = dict(item)
            out["archive_scope"] = "single_archive_validation"
            out["archive_count"] = 1
            out["source_archive_id"] = archive_id
            out["statistical_interpretation_allowed"] = statistical_allowed
            out["minimum_recommended_archives"] = 2
            out["minimum_recommended_trades"] = 30
            enriched.append(out)
        all_discoveries.extend(enriched)
        write_csv_rows(output_dir / f"cross_archive_signal_discovery_v7f_by_{key}.csv", enriched)

    pair_specs = [
        ("entry_regime_label", "entry_risk_label"),
        ("entry_regime_label", "entry_atr_signal"),
        ("entry_risk_label", "regime_aligned"),
        ("entry_ma200_signal", "entry_mfi_signal"),
        ("entry_score_at_entry", "entry_risk_label"),
        ("trade_family_group", "entry_risk_label"),
    ]

    for key_a, key_b in pair_specs:
        result = discover_pair_groups(rows, key_a, key_b)
        enriched = []
        for item in result:
            out = dict(item)
            out["archive_scope"] = "single_archive_validation"
            out["archive_count"] = 1
            out["source_archive_id"] = archive_id
            out["statistical_interpretation_allowed"] = statistical_allowed
            out["minimum_recommended_archives"] = 2
            out["minimum_recommended_trades"] = 30
            enriched.append(out)
        all_discoveries.extend(enriched)
        write_csv_rows(output_dir / f"cross_archive_signal_discovery_v7f_by_{key_a}__{key_b}.csv", enriched)

    all_discoveries.sort(key=lambda row: safe_float(row.get("discovery_score"), 0.0), reverse=True)

    write_csv_rows(output_dir / "cross_archive_signal_discovery_v7f_all.csv", all_discoveries)
    write_csv_rows(output_dir / "cross_archive_signal_discovery_v7f_top.csv", all_discoveries[:50])

    promising = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "PROMISING")
    watch = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "WATCH")
    low_support = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "LOW_SUPPORT")
    not_actionable = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "NOT_ACTIONABLE")
    watch_only = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "WATCH_ONLY")
    actionable = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "ACTIONABLE_CANDIDATE")
    high_warning = sum(1 for row in all_discoveries if safe_text(row.get("warning_level")) in {"HIGH", "DATASET_TOO_SMALL"})

    status = "PASS" if len(rows) >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_cross_archive_signal_discovery" if len(rows) < 30 else "none"

    manifest = [{
        "engine_version": "v7f",
        "archive_id": archive_id,
        "archive_count": archive_count,
        "rows_total": len(rows),
        "groups_evaluated": len(all_discoveries),
        "promising_groups": promising,
        "watch_groups": watch,
        "low_support_groups": low_support,
        "not_actionable_groups": not_actionable,
        "watch_only_groups": watch_only,
        "actionable_candidate_groups": actionable,
        "high_warning_groups": high_warning,
        "mode": export_mode,
        "method": "group_edge_vs_global_baseline_with_reliability_layer",
        "signal_discovery_status": status,
        "signal_discovery_warning": warning,
        "statistical_interpretation_allowed": statistical_allowed,
        "minimum_recommended_archives": 2,
        "minimum_recommended_trades": 30,
    }]

    write_csv_rows(output_dir / "cross_archive_signal_discovery_v7f_manifest.csv", manifest)

    summary_path = output_dir / "v7f_cross_archive_signal_discovery_summary.md"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# V7F CROSS-ARCHIVE SIGNAL DISCOVERY SUMMARY\n\n")
        fh.write("Status: infrastructure export\n\n")
        fh.write(f"archive_id: {archive_id}\n")
        fh.write(f"archive_count: {archive_count}\n")
        fh.write(f"rows_total: {len(rows)}\n")
        fh.write(f"groups_evaluated: {len(all_discoveries)}\n")
        fh.write(f"promising_groups: {promising}\n")
        fh.write(f"watch_groups: {watch}\n")
        fh.write(f"not_actionable_groups: {not_actionable}\n")
        fh.write(f"actionable_candidate_groups: {actionable}\n\n")
        fh.write("Important limitation:\n\n")
        fh.write("This output validates the V7F infrastructure only.\n")
        fh.write(f"statistical_interpretation_allowed: {statistical_allowed}\n")

    print("Cross-archive signal discovery export directory:", output_dir)
    print("archive_id:", archive_id)
    print("rows_total:", len(rows))
    print("groups_evaluated:", len(all_discoveries))
    print("promising_groups:", promising)
    print("watch_groups:", watch)
    print("low_support_groups:", low_support)
    print("not_actionable_groups:", not_actionable)
    print("watch_only_groups:", watch_only)
    print("actionable_candidate_groups:", actionable)
    print("high_warning_groups:", high_warning)
    print("signal_discovery_status:", status)
    print("signal_discovery_warning:", warning)
    for path in sorted(output_dir.glob("*")):
        print(" -", path)
