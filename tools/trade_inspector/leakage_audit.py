from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from .inspection_primitives import safe_text
    from .ml_dataset import build_ml_dataset_rows
else:
    from csv_persistence import write_csv_rows
    from feature_preparation import TARGET_COLUMNS, build_model_ready_rows
    from inspection_primitives import safe_text
    from ml_dataset import build_ml_dataset_rows


HIGH_LEAKAGE_PREFIXES = (
    "target_",
    "cf_return_",
    "cf_delta_vs_realized_",
    "best_future_return_",
    "opportunity_loss_",
    "exit_efficiency_",
)

HIGH_LEAKAGE_EXACT = {
    "pnl",
    "pnl_pct",
    "is_winner",
    "is_loser",
    "is_flat",
    "quality_score",
    "quality_class_encoded",
    "root_cause_encoded",
    "root_cause_weight",
    "additional_cause_1_encoded",
    "additional_cause_1_weight",
    "additional_cause_2_encoded",
    "additional_cause_2_weight",
    "impact_score",
    "priority_score",
    "priority_encoded",
    "overall_score",
    "overall_score_band_encoded",
    "entry_score",
    "exit_score",
    "risk_score",
    "entry_diagnosis",
    "exit_diagnosis",
    "risk_diagnosis",
    "root_cause_confidence",
    "evidence_score",
    "evidence_count",
    "diagnosis_reliability",
    "early_exit_flag",
    "good_exit_flag",
    "exit_problem_flag",
    "entry_problem_flag",
    "high_mfe_flag",
    "high_mae_flag",
    "mfe_abs",
    "mfe_pct",
    "mae_abs",
    "mae_pct",
    "best_price_during_trade",
    "worst_price_during_trade",
}

MEDIUM_LEAKAGE_EXACT = {
    "bars_held",
    "duration_sec",
    "exit_price",
    "exit_reason_encoded",
    "exit_regime_label_encoded",
    "exit_risk_label_encoded",
    "exit_score_at_exit",
    "exit_ma200_signal",
    "exit_mfi_signal",
    "exit_atr_signal",
    "regime_changed_during_trade",
}

SAFE_ID_COLUMNS = {
    "trade_id",
    "human_label",
    "ml_split",
}


def audit_feature_leakage(model_ready_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    if not model_ready_rows:
        return [], [], []

    columns = list(model_ready_rows[0].keys())
    report: list[dict[str, Any]] = []
    allowed_features: list[str] = []
    blocked_features: list[str] = []

    for col in columns:
        if col in SAFE_ID_COLUMNS:
            continue

        if col in TARGET_COLUMNS or any(col.startswith(prefix) for prefix in HIGH_LEAKAGE_PREFIXES):
            risk = "HIGH"
            reason = "target_or_future_information"
            allowed = 0
        elif col in HIGH_LEAKAGE_EXACT:
            risk = "HIGH"
            reason = "post_trade_outcome_or_diagnosis"
            allowed = 0
        elif col in MEDIUM_LEAKAGE_EXACT:
            risk = "MEDIUM"
            reason = "exit_or_in_trade_information"
            allowed = 0
        else:
            risk = "LOW"
            reason = "entry_or_static_feature"
            allowed = 1

        row = {
            "feature_name": col,
            "risk_level": risk,
            "reason": reason,
            "allowed_for_training": allowed,
        }
        report.append(row)

        if allowed == 1:
            allowed_features.append(col)
        else:
            blocked_features.append(col)

    return report, allowed_features, blocked_features


def export_leakage_audit_dataset(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, catalog = build_model_ready_rows(dataset_rows)
    leakage_report, allowed_features, blocked_features = audit_feature_leakage(model_ready_rows)

    training_columns = ["trade_id", "human_label", "ml_split"] + allowed_features
    target_columns = ["trade_id", "human_label", "ml_split"] + sorted(TARGET_COLUMNS)
    blocked_columns = ["trade_id", "human_label", "ml_split"] + blocked_features

    training_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []

    for row in model_ready_rows:
        training_rows.append({col: row.get(col, "") for col in training_columns if col in row})
        target_rows.append({col: row.get(col, "") for col in target_columns if col in row})
        blocked_rows.append({col: row.get(col, "") for col in blocked_columns if col in row})

    high_count = sum(1 for row in leakage_report if row["risk_level"] == "HIGH")
    medium_count = sum(1 for row in leakage_report if row["risk_level"] == "MEDIUM")
    low_count = sum(1 for row in leakage_report if row["risk_level"] == "LOW")

    high_in_training = sum(
        1 for row in leakage_report
        if row["risk_level"] == "HIGH" and row["allowed_for_training"] == 1
    )

    audit_status = "PASS" if high_in_training == 0 else "FAIL"
    leakage_score = high_count * 3 + medium_count

    write_csv_rows(output_dir / "trade_dataset_v4c_model_ready.csv", model_ready_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_training_features.csv", training_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_targets.csv", target_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_blocked_features.csv", blocked_rows)
    write_csv_rows(output_dir / "trade_dataset_v4c_leakage_report.csv", leakage_report)
    write_csv_rows(output_dir / "trade_dataset_v4c_feature_catalog.csv", catalog)

    manifest = [{
        "ml_dataset_version": "v4c",
        "rows_total": len(model_ready_rows),
        "total_features_audited": len(leakage_report),
        "allowed_features": len(allowed_features),
        "target_columns": len(TARGET_COLUMNS),
        "blocked_features": len(blocked_features),
        "high_risk_leakage_features": high_count,
        "medium_risk_leakage_features": medium_count,
        "low_risk_features": low_count,
        "high_risk_features_allowed_for_training": high_in_training,
        "leakage_score": leakage_score,
        "audit_status": audit_status,
        "purpose": "dataset_leakage_audit",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4c_manifest.csv", manifest)

    print("Leakage audit export directory:", output_dir)
    print("audit_status:", audit_status)
    print("allowed_features:", len(allowed_features))
    print("blocked_features:", len(blocked_features))
    print("high_risk_leakage_features:", high_count)
    print("medium_risk_leakage_features:", medium_count)
    print("low_risk_features:", low_count)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
