from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .feature_importance import feature_importance_rows
    from .feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from .inspection_primitives import safe_float, safe_text
    from .leakage_audit import audit_feature_leakage
    from .ml_dataset import build_ml_dataset_rows
else:
    from csv_persistence import write_csv_rows
    from feature_importance import feature_importance_rows
    from feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from inspection_primitives import safe_float, safe_text
    from leakage_audit import audit_feature_leakage
    from ml_dataset import build_ml_dataset_rows


def export_cross_archive_feature_importance(rows: list[dict[str, Any]], output_dir: Path, archive_id: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_archive_ids = sorted({str(row.get("archive_id", "")).strip() for row in rows if str(row.get("archive_id", "")).strip()})
    archive_count = len(source_archive_ids)
    statistical_allowed = "yes" if archive_count >= 2 and len(rows) >= 30 else "no"
    export_mode = "multi_archive_analysis" if archive_count >= 2 else "single_archive_infrastructure_validation"

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, _catalog = build_model_ready_rows(dataset_rows)
    _leakage_report, allowed_features, _blocked_features = audit_feature_leakage(model_ready_rows)

    training_columns = ["trade_id", "human_label", "ml_split"] + allowed_features
    target_columns = ["trade_id", "human_label", "ml_split"] + sorted(TARGET_COLUMNS)

    training_rows = [
        {col: row.get(col, "") for col in training_columns if col in row}
        for row in model_ready_rows
    ]

    target_rows = [
        {col: row.get(col, "") for col in target_columns if col in row}
        for row in model_ready_rows
    ]

    main_targets = [
        "target_winner",
        "target_loser",
        "target_quality_good",
        "target_quality_bad",
        "target_opportunity_loss_high",
        "target_exit_efficiency_high",
        "target_pnl_pct",
        "target_future_return_24h_pct",
        "target_future_return_72h_pct",
    ]

    all_importance: list[dict[str, Any]] = []

    for target in main_targets:
        target_importance = feature_importance_rows(training_rows, target_rows, target)
        for item in target_importance:
            out = dict(item)
            out["archive_scope"] = "single_archive_validation"
            out["archive_count"] = 1
            out["source_archive_id"] = archive_id
            out["statistical_interpretation_allowed"] = statistical_allowed
            out["minimum_recommended_archives"] = 2
            out["minimum_recommended_trades"] = 30
            all_importance.append(out)

    all_importance.sort(key=lambda row: safe_float(row.get("importance_score"), 0.0), reverse=True)

    write_csv_rows(output_dir / "cross_archive_feature_importance_v7e.csv", all_importance)

    for target in main_targets:
        target_rows_out = [row for row in all_importance if safe_text(row.get("target_column")) == target]
        write_csv_rows(output_dir / f"cross_archive_feature_importance_v7e_{target}.csv", target_rows_out)

    rows_total = len(model_ready_rows)
    status = "PASS" if rows_total >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_cross_archive_feature_importance" if rows_total < 30 else "none"

    manifest = [{
        "engine_version": "v7e",
        "archive_id": archive_id,
        "archive_count": archive_count,
        "rows_total": rows_total,
        "allowed_features": len(allowed_features),
        "targets_evaluated": len(main_targets),
        "importance_rows": len(all_importance),
        "method": "absolute_pearson_correlation_after_leakage_audit",
        "model_training": "not_performed",
        "mode": export_mode,
        "feature_importance_status": status,
        "feature_importance_warning": warning,
        "statistical_interpretation_allowed": statistical_allowed,
        "minimum_recommended_archives": 2,
        "minimum_recommended_trades": 30,
    }]

    write_csv_rows(output_dir / "cross_archive_feature_importance_v7e_manifest.csv", manifest)

    summary_path = output_dir / "v7e_cross_archive_feature_importance_summary.md"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# V7E CROSS-ARCHIVE FEATURE IMPORTANCE SUMMARY\n\n")
        fh.write("Status: infrastructure export\n\n")
        fh.write(f"archive_id: {archive_id}\n")
        fh.write(f"archive_count: {archive_count}\n")
        fh.write(f"rows_total: {rows_total}\n")
        fh.write(f"allowed_features: {len(allowed_features)}\n")
        fh.write(f"targets_evaluated: {len(main_targets)}\n")
        fh.write(f"importance_rows: {len(all_importance)}\n\n")
        fh.write("Important limitation:\n\n")
        fh.write("This output validates the V7E infrastructure only.\n")
        fh.write(f"statistical_interpretation_allowed: {statistical_allowed}\n")

    print("Cross-archive feature importance export directory:", output_dir)
    print("archive_id:", archive_id)
    print("rows_total:", rows_total)
    print("allowed_features:", len(allowed_features))
    print("targets_evaluated:", len(main_targets))
    print("importance_rows:", len(all_importance))
    print("feature_importance_status:", status)
    print("feature_importance_warning:", warning)
    for path in sorted(output_dir.glob("*")):
        print(" -", path)
