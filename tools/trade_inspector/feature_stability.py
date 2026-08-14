from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import avg
    from .csv_persistence import write_csv_rows
    from .feature_importance import feature_importance_rows
    from .feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from .inspection_primitives import safe_float, safe_text
    from .leakage_audit import audit_feature_leakage
    from .ml_dataset import build_ml_dataset_rows
else:
    from aggregate_csv import avg
    from csv_persistence import write_csv_rows
    from feature_importance import feature_importance_rows
    from feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from inspection_primitives import safe_float, safe_text
    from leakage_audit import audit_feature_leakage
    from ml_dataset import build_ml_dataset_rows


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = avg(values)
    return (sum((v - m) ** 2 for v in values) / (len(values) - 1)) ** 0.5


def stability_class(score: float) -> str:
    if score >= 90:
        return "elite"
    if score >= 75:
        return "stable"
    if score >= 50:
        return "moderate"
    if score >= 25:
        return "weak"
    return "unstable"


def export_feature_stability(rows: list[dict[str, Any]], output_dir: Path) -> None:
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

    targets = [
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

    by_feature: dict[str, list[dict[str, Any]]] = {}
    matrix: dict[str, dict[str, Any]] = {}

    for target in targets:
        importance = feature_importance_rows(training_rows, target_rows, target)

        for rank, row in enumerate(importance, start=1):
            feature = safe_text(row.get("feature_name"))
            score = safe_float(row.get("importance_score"), 0.0)

            by_feature.setdefault(feature, []).append({
                "target": target,
                "importance": score,
                "rank": rank,
            })

            matrix.setdefault(feature, {"feature_name": feature})
            matrix[feature][target] = score
            matrix[feature][f"{target}_rank"] = rank

    stability_rows: list[dict[str, Any]] = []

    for feature, items in by_feature.items():
        importances = [safe_float(item.get("importance"), 0.0) for item in items]
        ranks = [safe_float(item.get("rank"), 0.0) for item in items]

        top10_count = sum(1 for r in ranks if r <= 10)
        top20_count = sum(1 for r in ranks if r <= 20)

        importance_mean = avg(importances)
        importance_median = median(importances)
        importance_std = std(importances)
        rank_mean = avg(ranks)
        rank_std = std(ranks)

        score = 0.0
        score += min(60.0, importance_mean * 100.0)
        score += (top10_count / len(targets)) * 25.0
        score += (top20_count / len(targets)) * 15.0
        score -= min(25.0, importance_std * 100.0)
        score = max(0.0, min(100.0, score))

        stability_rows.append({
            "feature_name": feature,
            "importance_mean": importance_mean,
            "importance_median": importance_median,
            "importance_std": importance_std,
            "rank_mean": rank_mean,
            "rank_std": rank_std,
            "target_count": len(items),
            "top10_count": top10_count,
            "top20_count": top20_count,
            "stability_score": score,
            "stability_class": stability_class(score),
        })

    stability_rows.sort(key=lambda row: safe_float(row.get("stability_score"), 0.0), reverse=True)

    matrix_rows = list(matrix.values())
    matrix_rows.sort(key=lambda row: safe_text(row.get("feature_name")))

    write_csv_rows(output_dir / "feature_stability_v5c.csv", stability_rows)
    write_csv_rows(output_dir / "feature_stability_v5c_target_matrix.csv", matrix_rows)

    class_counts: dict[str, int] = {}
    for row in stability_rows:
        cls = safe_text(row.get("stability_class"))
        class_counts[cls] = class_counts.get(cls, 0) + 1

    status = "PASS" if len(model_ready_rows) >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_stability" if len(model_ready_rows) < 30 else "none"

    manifest = [{
        "engine_version": "v5c",
        "rows_total": len(model_ready_rows),
        "features_analyzed": len(stability_rows),
        "targets_analyzed": len(targets),
        "elite_features": class_counts.get("elite", 0),
        "stable_features": class_counts.get("stable", 0),
        "moderate_features": class_counts.get("moderate", 0),
        "weak_features": class_counts.get("weak", 0),
        "unstable_features": class_counts.get("unstable", 0),
        "stability_status": status,
        "stability_warning": warning,
        "method": "multi_target_absolute_pearson_stability",
    }]

    write_csv_rows(output_dir / "feature_stability_v5c_manifest.csv", manifest)

    print("Feature stability export directory:", output_dir)
    print("stability_status:", status)
    print("stability_warning:", warning)
    print("rows_total:", len(model_ready_rows))
    print("features_analyzed:", len(stability_rows))
    print("targets_analyzed:", len(targets))
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
