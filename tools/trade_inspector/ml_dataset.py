from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_int, safe_text
else:
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_int, safe_text


def print_kv(label: str, value: object) -> None:
    print(f"{label}: {value}")


def add_ml_targets(row: dict[str, Any]) -> dict[str, Any]:
    pnl = safe_float(row.get("pnl"), 0.0)
    pnl_pct = safe_float(row.get("pnl_pct"), 0.0)
    overall_score = safe_int(row.get("overall_score"), 0)
    exit_eff = safe_float(row.get("exit_efficiency_24h_pct"), 0.0)
    opp_loss = safe_float(row.get("opportunity_loss_24h_pct"), 0.0)
    mae_pct = safe_float(row.get("mae_pct"), 0.0)
    mfe_pct = safe_float(row.get("mfe_pct"), 0.0)

    return {
        "target_winner": 1 if pnl > 0 else 0,
        "target_loser": 1 if pnl < 0 else 0,
        "target_flat": 1 if abs(pnl) < 1e-12 else 0,
        "target_positive_pct": 1 if pnl_pct > 0 else 0,
        "target_quality_good": 1 if overall_score >= 60 else 0,
        "target_quality_bad": 1 if overall_score < 40 else 0,
        "target_exit_efficiency_high": 1 if exit_eff >= 0.6 else 0,
        "target_exit_efficiency_low": 1 if exit_eff < 0.3 else 0,
        "target_opportunity_loss_high": 1 if opp_loss >= 0.02 else 0,
        "target_adverse_move_high": 1 if mae_pct <= -0.01 else 0,
        "target_favorable_move_present": 1 if mfe_pct > 0 else 0,
        "target_pnl": pnl,
        "target_pnl_pct": pnl_pct,
        "target_future_return_24h_pct": safe_float(row.get("cf_return_24h_pct"), 0.0),
        "target_future_return_72h_pct": safe_float(row.get("cf_return_72h_pct"), 0.0),
        "target_future_return_168h_pct": safe_float(row.get("cf_return_168h_pct"), 0.0),
    }


def dataset_split_from_trade_id(trade_id: str) -> str:
    total = sum(ord(ch) for ch in trade_id)
    bucket = total % 100

    if bucket < 70:
        return "train"
    if bucket < 85:
        return "validation"
    return "test"


def build_ml_dataset_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dataset_rows: list[dict[str, Any]] = []

    for row in rows:
        out = dict(row)
        out.update(add_ml_targets(row))
        out["ml_split"] = dataset_split_from_trade_id(safe_text(row.get("trade_id")))
        out["ml_dataset_version"] = "v4a"
        dataset_rows.append(out)

    return dataset_rows



def evaluate_split_quality(dataset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts: dict[str, int] = {"train": 0, "validation": 0, "test": 0}

    for row in dataset_rows:
        split = safe_text(row.get("ml_split"))
        if split in split_counts:
            split_counts[split] += 1

    total = len(dataset_rows)
    warnings: list[str] = []

    if total < 30:
        warnings.append("dataset_too_small_for_reliable_ml")

    for split in ["train", "validation", "test"]:
        if split_counts[split] == 0:
            warnings.append(f"empty_{split}_split")

    if split_counts["train"] > 0 and split_counts["validation"] > 0 and split_counts["test"] > 0:
        status = "PASS"
    elif total < 30:
        status = "WARN"
    else:
        status = "FAIL"

    return {
        "split_quality_status": status,
        "split_quality_warnings": "|".join(warnings) if warnings else "none",
        "rows_total": total,
        "rows_train": split_counts["train"],
        "rows_validation": split_counts["validation"],
        "rows_test": split_counts["test"],
        "train_share": split_counts["train"] / total if total else 0.0,
        "validation_share": split_counts["validation"] / total if total else 0.0,
        "test_share": split_counts["test"] / total if total else 0.0,
    }


def print_split_quality(split_quality: dict[str, Any]) -> None:
    print("")
    print("ML SPLIT QUALITY")
    print("-" * 80)
    for key in [
        "split_quality_status",
        "split_quality_warnings",
        "rows_total",
        "rows_train",
        "rows_validation",
        "rows_test",
        "train_share",
        "validation_share",
        "test_share",
    ]:
        print_kv(key, split_quality.get(key, ""))


def export_ml_dataset(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_rows = build_ml_dataset_rows(rows)

    all_path = output_dir / "trade_dataset_v4a.csv"
    write_csv_rows(all_path, dataset_rows)

    for split in ["train", "validation", "test"]:
        split_rows = [row for row in dataset_rows if safe_text(row.get("ml_split")) == split]
        write_csv_rows(output_dir / f"trade_dataset_v4a_{split}.csv", split_rows)

    split_quality = evaluate_split_quality(dataset_rows)
    print_split_quality(split_quality)

    manifest_rows = [{
        "ml_dataset_version": "v4a",
        "split_quality_status": split_quality["split_quality_status"],
        "split_quality_warnings": split_quality["split_quality_warnings"],
        "rows_total": split_quality["rows_total"],
        "rows_train": split_quality["rows_train"],
        "rows_validation": split_quality["rows_validation"],
        "rows_test": split_quality["rows_test"],
        "train_share": split_quality["train_share"],
        "validation_share": split_quality["validation_share"],
        "test_share": split_quality["test_share"],
        "target_columns": "|".join([
            "target_winner",
            "target_loser",
            "target_quality_good",
            "target_quality_bad",
            "target_exit_efficiency_high",
            "target_opportunity_loss_high",
            "target_pnl",
            "target_pnl_pct",
            "target_future_return_24h_pct",
            "target_future_return_72h_pct",
            "target_future_return_168h_pct",
        ]),
        "feature_scope": "trade|path|counterfactual|diagnosis|confidence|regime|family",
        "split_method": "deterministic_trade_id_ascii_bucket",
    }]

    write_csv_rows(output_dir / "trade_dataset_v4a_manifest.csv", manifest_rows)

    print("ML dataset export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
