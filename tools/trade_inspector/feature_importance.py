from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import avg
    from .csv_persistence import write_csv_rows
    from .feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from .inspection_primitives import safe_float, safe_text
    from .leakage_audit import audit_feature_leakage
    from .ml_dataset import build_ml_dataset_rows
else:
    from aggregate_csv import avg
    from csv_persistence import write_csv_rows
    from feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from inspection_primitives import safe_float, safe_text
    from leakage_audit import audit_feature_leakage
    from ml_dataset import build_ml_dataset_rows


def pearson_abs(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0

    mx = avg(xs)
    my = avg(ys)

    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs)
    den_y = sum((y - my) ** 2 for y in ys)

    if den_x <= 0 or den_y <= 0:
        return 0.0

    return abs(num / ((den_x ** 0.5) * (den_y ** 0.5)))


def feature_importance_rows(
    training_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    target_column: str,
) -> list[dict[str, Any]]:
    target_by_trade_id = {
        safe_text(row.get("trade_id")): safe_float(row.get(target_column), 0.0)
        for row in target_rows
    }

    if not training_rows:
        return []

    blocked = {"trade_id", "human_label", "ml_split"}
    features = [col for col in training_rows[0].keys() if col not in blocked]

    output: list[dict[str, Any]] = []

    for feature in features:
        xs: list[float] = []
        ys: list[float] = []

        for row in training_rows:
            trade_id = safe_text(row.get("trade_id"))
            if trade_id not in target_by_trade_id:
                continue
            xs.append(safe_float(row.get(feature), 0.0))
            ys.append(target_by_trade_id[trade_id])

        score = pearson_abs(xs, ys)

        output.append({
            "target_column": target_column,
            "feature_name": feature,
            "importance_score": score,
            "rows_used": len(xs),
            "method": "absolute_pearson_correlation",
        })

    output.sort(key=lambda row: safe_float(row.get("importance_score"), 0.0), reverse=True)
    return output


def export_feature_importance(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

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
        all_importance.extend(feature_importance_rows(training_rows, target_rows, target))

    write_csv_rows(output_dir / "feature_importance_v5.csv", all_importance)

    for target in main_targets:
        target_rows_out = [row for row in all_importance if safe_text(row.get("target_column")) == target]
        write_csv_rows(output_dir / f"feature_importance_v5_{target}.csv", target_rows_out)

    rows_total = len(model_ready_rows)
    status = "PASS" if rows_total >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_feature_importance" if rows_total < 30 else "none"

    manifest = [{
        "engine_version": "v5",
        "rows_total": rows_total,
        "allowed_features": len(allowed_features),
        "targets_evaluated": len(main_targets),
        "method": "absolute_pearson_correlation",
        "model_training": "not_performed",
        "feature_importance_status": status,
        "feature_importance_warning": warning,
    }]

    write_csv_rows(output_dir / "feature_importance_v5_manifest.csv", manifest)

    print("Feature importance export directory:", output_dir)
    print("feature_importance_status:", status)
    print("feature_importance_warning:", warning)
    print("rows_total:", rows_total)
    print("allowed_features:", len(allowed_features))
    print("targets_evaluated:", len(main_targets))
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
