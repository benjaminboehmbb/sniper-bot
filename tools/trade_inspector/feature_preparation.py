from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_text
    from .ml_dataset import build_ml_dataset_rows
else:
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_text
    from ml_dataset import build_ml_dataset_rows


NON_FEATURE_COLUMNS = {
    "trade_index",
    "trade_id",
    "human_label",
    "symbol",
    "entry_time_chart",
    "exit_time_chart",
    "entry_timestamp_utc",
    "exit_timestamp_utc",
    "flags",
    "positive_factors",
    "negative_factors",
    "cause_weights",
    "key_findings",
    "improvement_options",
    "evidence_items",
    "ml_dataset_version",
    "ml_split",
}

TARGET_COLUMNS = {
    "target_winner",
    "target_loser",
    "target_flat",
    "target_positive_pct",
    "target_quality_good",
    "target_quality_bad",
    "target_exit_efficiency_high",
    "target_exit_efficiency_low",
    "target_opportunity_loss_high",
    "target_adverse_move_high",
    "target_favorable_move_present",
    "target_pnl",
    "target_pnl_pct",
    "target_future_return_24h_pct",
    "target_future_return_72h_pct",
    "target_future_return_168h_pct",
}


def is_number_like(value: object) -> bool:
    if value is None:
        return False
    text = safe_text(value)
    if text == "":
        return False
    try:
        float(text)
        return True
    except Exception:
        return False


def build_category_maps(rows: list[dict[str, Any]], candidate_columns: list[str]) -> dict[str, dict[str, int]]:
    maps: dict[str, dict[str, int]] = {}

    for col in candidate_columns:
        values = sorted({safe_text(row.get(col)) for row in rows if safe_text(row.get(col)) != ""})
        maps[col] = {value: idx for idx, value in enumerate(values)}

    return maps


def build_feature_catalog(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    if not rows:
        return [], {}

    all_columns = list(rows[0].keys())

    numeric_features: list[str] = []
    categorical_features: list[str] = []

    for col in all_columns:
        if col in NON_FEATURE_COLUMNS or col in TARGET_COLUMNS:
            continue

        values = [row.get(col) for row in rows if safe_text(row.get(col)) != ""]
        if not values:
            continue

        if all(is_number_like(value) for value in values):
            numeric_features.append(col)
        else:
            categorical_features.append(col)

    category_maps = build_category_maps(rows, categorical_features)

    catalog: list[dict[str, Any]] = []

    for col in numeric_features:
        catalog.append({
            "feature_name": col,
            "feature_type": "numeric",
            "encoded_name": col,
            "category_count": 0,
            "include_for_model": 1,
        })

    for col in categorical_features:
        catalog.append({
            "feature_name": col,
            "feature_type": "categorical_label_encoded",
            "encoded_name": f"{col}_encoded",
            "category_count": len(category_maps.get(col, {})),
            "include_for_model": 1,
        })

    catalog.sort(key=lambda row: safe_text(row.get("encoded_name")))
    return catalog, category_maps


def build_model_ready_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    catalog, category_maps = build_feature_catalog(rows)

    feature_order = [safe_text(item.get("encoded_name")) for item in catalog]
    feature_sources = {safe_text(item.get("encoded_name")): item for item in catalog}

    output_rows: list[dict[str, Any]] = []

    for row in rows:
        out: dict[str, Any] = {
            "trade_id": safe_text(row.get("trade_id")),
            "human_label": safe_text(row.get("human_label")),
            "ml_split": safe_text(row.get("ml_split")),
        }

        for target in sorted(TARGET_COLUMNS):
            out[target] = row.get(target, "")

        for encoded_name in feature_order:
            item = feature_sources[encoded_name]
            source = safe_text(item.get("feature_name"))
            feature_type = safe_text(item.get("feature_type"))

            if feature_type == "numeric":
                out[encoded_name] = safe_float(row.get(source), 0.0)
            else:
                value = safe_text(row.get(source))
                out[encoded_name] = category_maps.get(source, {}).get(value, -1)

        output_rows.append(out)

    return output_rows, catalog


def export_feature_preparation(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)
    model_ready_rows, catalog = build_model_ready_rows(dataset_rows)

    write_csv_rows(output_dir / "trade_dataset_v4b_model_ready.csv", model_ready_rows)
    write_csv_rows(output_dir / "trade_dataset_v4b_feature_catalog.csv", catalog)

    for split in ["train", "validation", "test"]:
        split_rows = [row for row in model_ready_rows if safe_text(row.get("ml_split")) == split]
        write_csv_rows(output_dir / f"trade_dataset_v4b_model_ready_{split}.csv", split_rows)

    manifest = [{
        "ml_dataset_version": "v4b",
        "rows_total": len(model_ready_rows),
        "feature_count": len(catalog),
        "numeric_feature_count": sum(1 for row in catalog if safe_text(row.get("feature_type")) == "numeric"),
        "categorical_feature_count": sum(1 for row in catalog if safe_text(row.get("feature_type")) == "categorical_label_encoded"),
        "target_count": len(TARGET_COLUMNS),
        "purpose": "feature_importance_preparation",
        "model_training": "not_performed",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4b_feature_manifest.csv", manifest)

    print("Feature preparation export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
