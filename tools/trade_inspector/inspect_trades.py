#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1D.
# Read-only trade diagnosis tool.
# Human analysis + ML feature export.
# ASCII-only.

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import (
        aggregate_group_rows,
        aggregate_top_improvement_rows,
        avg,
        compute_root_cause_attribution,
        export_aggregate_csvs,
        export_root_cause_attribution_csv,
        group_rows,
        group_stats,
        parse_cause_weights,
    )
    from .archive_intake import count_valid_jsonl, run_archive_intake_validation
    from .csv_persistence import write_csv_rows
    from .feature_preparation import (
        NON_FEATURE_COLUMNS,
        TARGET_COLUMNS,
        build_category_maps,
        build_feature_catalog,
        build_model_ready_rows,
        export_feature_preparation,
        is_number_like,
    )
    from .inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key
    from .label_registry import (
        assign_human_labels,
        load_human_labels,
        load_label_registry,
        save_label_registry,
    )
    from .leakage_audit import (
        HIGH_LEAKAGE_EXACT,
        HIGH_LEAKAGE_PREFIXES,
        MEDIUM_LEAKAGE_EXACT,
        SAFE_ID_COLUMNS,
        audit_feature_leakage,
        export_leakage_audit_dataset,
    )
    from .ml_dataset import (
        add_ml_targets,
        build_ml_dataset_rows,
        dataset_split_from_trade_id,
        evaluate_split_quality,
        export_ml_dataset,
        print_kv,
        print_split_quality,
    )
    from .path_diagnosis import (
        FUTURE_WINDOWS_MIN,
        calculate_counterfactuals,
        calculate_trade_path,
        compute_confidence_layer,
        compute_diagnosis,
        compute_quality_score,
        interpretation_flags,
        quality_flags,
        score_band,
        signed_diagnosis,
        trade_pnl_from_price,
    )
    from .raw_ml_csv import export_ml_csv
    from .regime_identity_rows import (
        build_ml_row,
        build_regime_index,
        build_rows,
        build_trade_family,
        build_trade_id,
        chart_time,
        compact_trade_time,
        extract_regime_features,
        find_matching_entry_exit,
    )
else:
    from aggregate_csv import (
        aggregate_group_rows,
        aggregate_top_improvement_rows,
        avg,
        compute_root_cause_attribution,
        export_aggregate_csvs,
        export_root_cause_attribution_csv,
        group_rows,
        group_stats,
        parse_cause_weights,
    )
    from archive_intake import count_valid_jsonl, run_archive_intake_validation
    from csv_persistence import write_csv_rows
    from feature_preparation import (
        NON_FEATURE_COLUMNS,
        TARGET_COLUMNS,
        build_category_maps,
        build_feature_catalog,
        build_model_ready_rows,
        export_feature_preparation,
        is_number_like,
    )
    from inspection_primitives import parse_ts, safe_float, safe_int, safe_text, ts_key
    from label_registry import (
        assign_human_labels,
        load_human_labels,
        load_label_registry,
        save_label_registry,
    )
    from leakage_audit import (
        HIGH_LEAKAGE_EXACT,
        HIGH_LEAKAGE_PREFIXES,
        MEDIUM_LEAKAGE_EXACT,
        SAFE_ID_COLUMNS,
        audit_feature_leakage,
        export_leakage_audit_dataset,
    )
    from ml_dataset import (
        add_ml_targets,
        build_ml_dataset_rows,
        dataset_split_from_trade_id,
        evaluate_split_quality,
        export_ml_dataset,
        print_kv,
        print_split_quality,
    )
    from path_diagnosis import (
        FUTURE_WINDOWS_MIN,
        calculate_counterfactuals,
        calculate_trade_path,
        compute_confidence_layer,
        compute_diagnosis,
        compute_quality_score,
        interpretation_flags,
        quality_flags,
        score_band,
        signed_diagnosis,
        trade_pnl_from_price,
    )
    from raw_ml_csv import export_ml_csv
    from regime_identity_rows import (
        build_ml_row,
        build_regime_index,
        build_rows,
        build_trade_family,
        build_trade_id,
        chart_time,
        compact_trade_time,
        extract_regime_features,
        find_matching_entry_exit,
    )


DEFAULT_ARCHIVE_DIR = Path("live_logs/archive/P79A_pre_run_2026-06-10")
DEFAULT_MARKET_CSV = Path("data/l1_full_run.csv")

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


DEFAULT_LABEL_LIST = Path("config/trade_inspector/human_labels.txt")
DEFAULT_LABEL_REGISTRY = Path("config/trade_inspector/trade_label_registry.csv")


def print_trade_report(
    idx: int,
    trade: dict[str, Any],
    entry: dict[str, Any] | None,
    exit_: dict[str, Any] | None,
    audit_rows: list[dict[str, Any]],
    regime_index: dict[str, dict[str, Any]],
    timestamps: list[str],
    prices: list[float],
    label_map: dict[str, str],
) -> None:
    row = build_ml_row(idx, trade, entry, exit_, audit_rows, regime_index, timestamps, prices, label_map)

    print("=" * 80)
    print(f"TRADE REPORT #{idx}")
    print("=" * 80)

    print("")
    print("TRADE SUMMARY")
    print("-" * 80)
    for key in [
        "trade_id",
        "human_label",
        "symbol",
        "entry_time_chart",
        "exit_time_chart",
        "side",
        "entry_timestamp_utc",
        "exit_timestamp_utc",
        "duration_sec",
        "entry_price",
        "exit_price",
        "pnl",
        "pnl_pct",
        "exit_reason",
    ]:
        if key in row:
            print_kv(key, row.get(key, ""))
        else:
            print_kv(key, trade.get(key, ""))

    print("")
    print("TRADE DIAGNOSIS")
    print("-" * 80)
    for key in [
        "overall_score", "overall_score_band",
        "entry_score", "entry_score_band", "entry_diagnosis",
        "exit_score", "exit_score_band", "exit_diagnosis",
        "risk_score", "risk_score_band", "risk_diagnosis",
        "root_cause", "root_cause_weight",
        "additional_cause_1", "additional_cause_1_weight",
        "additional_cause_2", "additional_cause_2_weight",
        "cause_weights",
        "root_cause_confidence",
        "evidence_score",
        "evidence_count",
        "impact_score",
        "priority_score",
        "priority",
        "diagnosis_reliability",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("EVIDENCE")
    print("-" * 80)
    evidence = safe_text(row.get("evidence_items"))
    if evidence:
        for item in evidence.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("KEY FINDINGS")
    print("-" * 80)
    findings = safe_text(row.get("key_findings"))
    if findings:
        for item in findings.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("IMPROVEMENT OPTIONS")
    print("-" * 80)
    options = safe_text(row.get("improvement_options"))
    if options:
        for item in options.split("|"):
            print(f"- {item}")
    else:
        print("none")

    print("")
    print("QUALITY ASSESSMENT")
    print("-" * 80)
    for key in ["quality_score", "quality_class", "positive_factors", "negative_factors"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("TRADE PATH")
    print("-" * 80)
    for key in ["path_available", "bars_held", "best_price_during_trade", "worst_price_during_trade", "mfe_abs", "mfe_pct", "mae_abs", "mae_pct"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("REGIME CONTEXT")
    print("-" * 80)
    for key in [
        "entry_regime_label",
        "exit_regime_label",
        "entry_risk_label",
        "exit_risk_label",
        "entry_score_at_entry",
        "entry_score_at_exit",
        "entry_ma200_signal",
        "entry_mfi_signal",
        "entry_atr_signal",
        "regime_aligned",
        "risk_good_at_entry",
        "regime_changed_during_trade",
        "has_entry_regime_context",
        "has_exit_regime_context",
    ]:
        print_kv(key, row.get(key, ""))

    print("")
    print("COUNTERFACTUAL 24H CORE")
    print("-" * 80)
    for key in ["cf_return_24h_pct", "best_future_return_24h_pct", "exit_efficiency_24h_pct", "opportunity_loss_24h_pct"]:
        print_kv(key, row.get(key, ""))

    print("")
    print("INTERPRETATION FLAGS")
    print("-" * 80)
    for key in ["high_mfe_flag", "high_mae_flag", "early_exit_flag", "good_exit_flag", "entry_problem_flag", "exit_problem_flag"]:
        print_kv(key, row.get(key, ""))

    print("")


def print_summary(rows: list[dict[str, Any]]) -> None:
    class_counts: dict[str, int] = {}
    root_counts: dict[str, int] = {}
    winners = losers = flats = 0
    total_pnl = 0.0

    for row in rows:
        cls = safe_text(row.get("quality_class"))
        root = safe_text(row.get("root_cause"))
        class_counts[cls] = class_counts.get(cls, 0) + 1
        root_counts[root] = root_counts.get(root, 0) + 1
        winners += safe_int(row.get("is_winner"), 0)
        losers += safe_int(row.get("is_loser"), 0)
        flats += safe_int(row.get("is_flat"), 0)
        total_pnl += safe_float(row.get("pnl"), 0.0)

    print("TRADE INSPECTOR SUMMARY")
    print("-" * 80)
    print_kv("trades", len(rows))
    print_kv("winners", winners)
    print_kv("losers", losers)
    print_kv("flats", flats)
    print_kv("total_pnl", total_pnl)

    print("")
    print("QUALITY CLASS COUNTS")
    print("-" * 80)
    for key in ["excellent", "good", "acceptable", "weak", "bad"]:
        print_kv(key, class_counts.get(key, 0))

    print("")
    print("ROOT CAUSE COUNTS")
    print("-" * 80)
    for key, value in sorted(root_counts.items(), key=lambda item: item[1], reverse=True):
        print_kv(key, value)



def print_group_table(title: str, groups: dict[str, list[dict[str, Any]]], sort_key: str, reverse: bool = True) -> None:
    print("")
    print(title)
    print("-" * 80)

    table = []
    for name, items in groups.items():
        stats = group_stats(items)
        table.append((name, stats))

    table.sort(key=lambda item: safe_float(item[1].get(sort_key), 0.0), reverse=reverse)

    print("group,count,winrate,total_pnl,avg_pnl,avg_pnl_pct,avg_exit_eff_24h,avg_opp_loss_24h,avg_overall")
    for name, stats in table:
        print(
            f"{name},"
            f"{stats['count']},"
            f"{stats['winrate']:.4f},"
            f"{stats['total_pnl']:.8f},"
            f"{stats['avg_pnl']:.8f},"
            f"{stats['avg_pnl_pct']:.8f},"
            f"{stats['avg_exit_efficiency_24h_pct']:.8f},"
            f"{stats['avg_opportunity_loss_24h_pct']:.8f},"
            f"{stats['avg_overall_score']:.2f}"
        )



def print_trade_family_summary(rows: list[dict[str, Any]]) -> None:
    print_group_table(
        "PERFORMANCE BY TRADE FAMILY GROUP",
        group_rows(rows, "trade_family_group"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY TRADE FAMILY",
        group_rows(rows, "trade_family"),
        "total_pnl",
        reverse=True,
    )

def print_top_improvement_candidates(rows: list[dict[str, Any]], limit: int = 20) -> None:
    print("")
    print("TOP IMPROVEMENT CANDIDATES")
    print("-" * 80)
    print("rank,human_label,trade_id,root_cause,priority,priority_score,impact_score,confidence,opp_loss_24h,pnl,regime,risk")

    ranked = sorted(
        rows,
        key=lambda row: (
            safe_float(row.get("priority_score"), 0.0),
            safe_float(row.get("impact_score"), 0.0),
            safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
        ),
        reverse=True,
    )

    for rank, row in enumerate(ranked[:limit], start=1):
        print(
            f"{rank},"
            f"{safe_text(row.get('human_label'))},"
            f"{safe_text(row.get('trade_id'))},"
            f"{safe_text(row.get('root_cause'))},"
            f"{safe_text(row.get('priority'))},"
            f"{safe_text(row.get('priority_score'))},"
            f"{safe_text(row.get('impact_score'))},"
            f"{safe_text(row.get('root_cause_confidence'))},"
            f"{safe_float(row.get('opportunity_loss_24h_pct'), 0.0):.8f},"
            f"{safe_float(row.get('pnl'), 0.0):.8f},"
            f"{safe_text(row.get('entry_regime_label'))},"
            f"{safe_text(row.get('entry_risk_label'))}"
        )



def print_root_cause_attribution(rows: list[dict[str, Any]]) -> None:
    attribution = compute_root_cause_attribution(rows)

    print("")
    print("ROOT CAUSE ATTRIBUTION")
    print("-" * 80)
    print(
        "root_cause,"
        "cause_share,"
        "weighted_trades,"
        "neg_pnl_share,"
        "opp_loss_share,"
        "impact_share,"
        "priority_share,"
        "priority_contribution"
    )

    for row in attribution:
        print(
            f"{safe_text(row.get('root_cause'))},"
            f"{safe_float(row.get('cause_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('trade_count_weighted'), 0.0):.4f},"
            f"{safe_float(row.get('negative_pnl_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('opportunity_loss_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('impact_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('priority_share_pct'), 0.0):.4f},"
            f"{safe_float(row.get('priority_contribution'), 0.0):.4f}"
        )


def print_aggregate_intelligence(rows: list[dict[str, Any]]) -> None:
    print("TRADE INSPECTOR V3 AGGREGATE INTELLIGENCE")
    print("=" * 80)

    stats = group_stats(rows)

    print("")
    print("GLOBAL SUMMARY")
    print("-" * 80)
    print_kv("trades", stats["count"])
    print_kv("winners", stats["winners"])
    print_kv("losers", stats["losers"])
    print_kv("winrate", f"{stats['winrate']:.4f}")
    print_kv("total_pnl", f"{stats['total_pnl']:.8f}")
    print_kv("avg_pnl", f"{stats['avg_pnl']:.8f}")
    print_kv("avg_pnl_pct", f"{stats['avg_pnl_pct']:.8f}")
    print_kv("avg_exit_efficiency_24h_pct", f"{stats['avg_exit_efficiency_24h_pct']:.8f}")
    print_kv("avg_opportunity_loss_24h_pct", f"{stats['avg_opportunity_loss_24h_pct']:.8f}")
    print_kv("avg_overall_score", f"{stats['avg_overall_score']:.2f}")

    print_group_table(
        "ROOT CAUSE RANKING",
        group_rows(rows, "root_cause"),
        "count",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY ENTRY REGIME",
        group_rows(rows, "entry_regime_label"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY ENTRY RISK LABEL",
        group_rows(rows, "entry_risk_label"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY REGIME ALIGNMENT",
        group_rows(rows, "regime_aligned"),
        "total_pnl",
        reverse=True,
    )

    print_group_table(
        "PERFORMANCE BY PRIORITY",
        group_rows(rows, "priority"),
        "priority_score",
        reverse=True,
    )

    print_trade_family_summary(rows)

    print_top_improvement_candidates(rows, limit=20)
    print_root_cause_attribution(rows)


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


def safe_rate(num: float, den: float) -> float:
    return num / den if den else 0.0


def discover_signal_groups(rows: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    groups = group_rows(rows, group_key)
    global_stats = group_stats(rows)
    global_winrate = safe_float(global_stats.get("winrate"), 0.0)
    global_avg_pnl_pct = safe_float(global_stats.get("avg_pnl_pct"), 0.0)

    output: list[dict[str, Any]] = []

    for group_name, items in groups.items():
        stats = group_stats(items)

        count = safe_int(stats.get("count"), 0)
        winrate = safe_float(stats.get("winrate"), 0.0)
        avg_pnl_pct = safe_float(stats.get("avg_pnl_pct"), 0.0)
        avg_opp = safe_float(stats.get("avg_opportunity_loss_24h_pct"), 0.0)
        avg_exit_eff = safe_float(stats.get("avg_exit_efficiency_24h_pct"), 0.0)

        winrate_edge = winrate - global_winrate
        pnl_edge = avg_pnl_pct - global_avg_pnl_pct

        support_score = min(100.0, count * 10.0)
        edge_score = max(0.0, (winrate_edge * 100.0) + (pnl_edge * 1000.0))
        quality_score = max(0.0, min(100.0, support_score * 0.35 + edge_score * 0.65))

        if count < 3:
            status = "LOW_SUPPORT"
        elif quality_score >= 60:
            status = "PROMISING"
        elif quality_score >= 35:
            status = "WATCH"
        else:
            status = "WEAK"

        support_class = classify_signal_support(count)
        reliability_score, reliability_class, warning_level, minimum_required_support = classify_signal_reliability(
            len(rows),
            count,
            status,
        )

        output.append({
            "group_key": group_key,
            "group": group_name,
            "count": count,
            "support_count": count,
            "minimum_required_support": minimum_required_support,
            "support_class": support_class,
            "reliability_score": reliability_score,
            "reliability_class": reliability_class,
            "warning_level": warning_level,
            "winrate": winrate,
            "global_winrate": global_winrate,
            "winrate_edge": winrate_edge,
            "avg_pnl_pct": avg_pnl_pct,
            "global_avg_pnl_pct": global_avg_pnl_pct,
            "pnl_edge": pnl_edge,
            "avg_opportunity_loss_24h_pct": avg_opp,
            "avg_exit_efficiency_24h_pct": avg_exit_eff,
            "support_score": support_score,
            "edge_score": edge_score,
            "discovery_score": quality_score,
            "discovery_status": status,
        })

    output.sort(key=lambda row: safe_float(row.get("discovery_score"), 0.0), reverse=True)
    return output



def classify_signal_support(count: int) -> str:
    if count < 3:
        return "VERY_LOW"
    if count < 10:
        return "LOW"
    if count < 30:
        return "MEDIUM"
    return "HIGH"


def classify_signal_reliability(rows_total: int, count: int, discovery_status: str) -> tuple[int, str, str, int]:
    minimum_required_support = 30

    if rows_total < minimum_required_support:
        return 0, "NOT_ACTIONABLE", "DATASET_TOO_SMALL", minimum_required_support

    support_ratio = (count / rows_total) if rows_total else 0.0

    score = 0

    if count >= 30:
        score += 40
    elif count >= 10:
        score += 25
    elif count >= 3:
        score += 10

    if support_ratio >= 0.20:
        score += 20
    elif support_ratio >= 0.10:
        score += 10

    if discovery_status == "PROMISING":
        score += 30
    elif discovery_status == "WATCH":
        score += 15

    score = max(0, min(100, score))

    if score >= 70:
        return score, "ACTIONABLE_CANDIDATE", "LOW", minimum_required_support
    if score >= 40:
        return score, "WATCH_ONLY", "MEDIUM", minimum_required_support
    return score, "NOT_ACTIONABLE", "HIGH", minimum_required_support



def discover_pair_groups(rows: list[dict[str, Any]], key_a: str, key_b: str) -> list[dict[str, Any]]:
    combined_rows: list[dict[str, Any]] = []

    for row in rows:
        out = dict(row)
        out[f"{key_a}__{key_b}"] = f"{safe_text(row.get(key_a))}__{safe_text(row.get(key_b))}"
        combined_rows.append(out)

    return discover_signal_groups(combined_rows, f"{key_a}__{key_b}")


def export_predictive_signal_discovery(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

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
        all_discoveries.extend(result)
        write_csv_rows(output_dir / f"predictive_signal_discovery_by_{key}.csv", result)

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
        all_discoveries.extend(result)
        write_csv_rows(output_dir / f"predictive_signal_discovery_by_{key_a}__{key_b}.csv", result)

    all_discoveries.sort(key=lambda row: safe_float(row.get("discovery_score"), 0.0), reverse=True)
    write_csv_rows(output_dir / "predictive_signal_discovery_v6_all.csv", all_discoveries)
    write_csv_rows(output_dir / "predictive_signal_discovery_v6_top.csv", all_discoveries[:50])

    promising = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "PROMISING")
    watch = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "WATCH")
    low_support = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "LOW_SUPPORT")
    not_actionable = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "NOT_ACTIONABLE")
    watch_only = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "WATCH_ONLY")
    actionable = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "ACTIONABLE_CANDIDATE")
    high_warning = sum(1 for row in all_discoveries if safe_text(row.get("warning_level")) in {"HIGH", "DATASET_TOO_SMALL"})

    status = "PASS" if len(rows) >= 30 else "WARN"
    warning = "dataset_too_small_for_reliable_signal_discovery" if len(rows) < 30 else "none"

    manifest = [{
        "engine_version": "v6a",
        "rows_total": len(rows),
        "groups_evaluated": len(all_discoveries),
        "promising_groups": promising,
        "watch_groups": watch,
        "low_support_groups": low_support,
        "not_actionable_groups": not_actionable,
        "watch_only_groups": watch_only,
        "actionable_candidate_groups": actionable,
        "high_warning_groups": high_warning,
        "minimum_required_support": 30,
        "discovery_status": status,
        "discovery_warning": warning,
        "method": "group_edge_vs_global_baseline_with_reliability_layer",
    }]

    write_csv_rows(output_dir / "predictive_signal_discovery_v6_manifest.csv", manifest)

    print("Predictive signal discovery export directory:", output_dir)
    print("discovery_status:", status)
    print("discovery_warning:", warning)
    print("rows_total:", len(rows))
    print("groups_evaluated:", len(all_discoveries))
    print("promising_groups:", promising)
    print("watch_groups:", watch)
    print("low_support_groups:", low_support)
    print("not_actionable_groups:", not_actionable)
    print("watch_only_groups:", watch_only)
    print("actionable_candidate_groups:", actionable)
    print("high_warning_groups:", high_warning)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)






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
        "statistical_interpretation_allowed": statistical_allowed,
    }]
    write_csv_rows(output_dir / "global_trades_v7c_manifest.csv", manifest)

    print("Global trade database export directory:", output_dir)
    print("archive_id:", archive_id)
    print("global_trades:", len(global_rows))
    for path in sorted(output_dir.glob("*")):
        print(" -", path)


def run_builtin_regression_validation(args: Any) -> int:
    archive_dir = Path(args.archive_dir)
    market_csv = Path(args.market_csv)

    print("TRADE INSPECTOR V7H REGRESSION VALIDATION")
    print("archive_dir:", archive_dir)
    print("market_csv:", market_csv)
    print("")

    errors: list[str] = []

    trades = read_jsonl(archive_dir / "trades_l1.jsonl")
    audit_rows = read_jsonl(archive_dir / "execution_audit.jsonl")
    log_rows = parse_key_value_log(archive_dir / "l1_paper.log")
    regime_index = build_regime_index(log_rows)
    timestamps, prices = parse_market_rows(market_csv)
    label_list = load_human_labels(Path(args.label_list))
    existing_registry = load_label_registry(Path(args.label_registry))
    label_map = assign_human_labels(trades, label_list, existing_registry)

    rows = build_rows(trades, audit_rows, regime_index, timestamps, prices, label_map)

    print("CHECK trades:", len(trades))
    print("CHECK audit_events:", len(audit_rows))
    print("CHECK regime_events:", len(log_rows))
    print("CHECK market_rows:", len(timestamps))
    print("CHECK rows:", len(rows))

    if len(trades) != 9:
        errors.append(f"expected 9 trades, got {len(trades)}")

    if len(rows) != 9:
        errors.append(f"expected 9 built rows, got {len(rows)}")

    all_discoveries: list[dict[str, Any]] = []

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

    for key in group_keys:
        all_discoveries.extend(discover_signal_groups(rows, key))

    pair_specs = [
        ("entry_regime_label", "entry_risk_label"),
        ("entry_regime_label", "entry_atr_signal"),
        ("entry_risk_label", "regime_aligned"),
        ("entry_ma200_signal", "entry_mfi_signal"),
        ("entry_score_at_entry", "entry_risk_label"),
        ("trade_family_group", "entry_risk_label"),
    ]

    for key_a, key_b in pair_specs:
        all_discoveries.extend(discover_pair_groups(rows, key_a, key_b))

    groups_evaluated = len(all_discoveries)
    not_actionable = sum(1 for row in all_discoveries if safe_text(row.get("reliability_class")) == "NOT_ACTIONABLE")
    high_warning = sum(1 for row in all_discoveries if safe_text(row.get("warning_level")) in {"HIGH", "DATASET_TOO_SMALL"})
    watch_groups = sum(1 for row in all_discoveries if safe_text(row.get("discovery_status")) == "WATCH")

    print("CHECK signal_groups_evaluated:", groups_evaluated)
    print("CHECK signal_not_actionable:", not_actionable)
    print("CHECK signal_high_warning:", high_warning)
    print("CHECK signal_watch_groups:", watch_groups)

    if groups_evaluated != 57:
        errors.append(f"expected 57 signal groups, got {groups_evaluated}")

    if not_actionable != 57:
        errors.append(f"expected 57 NOT_ACTIONABLE groups, got {not_actionable}")

    if high_warning != 57:
        errors.append(f"expected 57 high warning groups, got {high_warning}")

    if watch_groups != 6:
        errors.append(f"expected 6 WATCH groups, got {watch_groups}")

    archive_id = safe_text(args.archive_id) or "P79A_pre_run_2026-06-10"
    global_rows: list[dict[str, Any]] = []

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
        out["local_trade_id"] = local_trade_id
        out["global_trade_id"] = f"{archive_id}::{local_trade_id}"
        global_rows.append(out)

    global_id_count = sum(1 for row in global_rows if safe_text(row.get("global_trade_id")))

    print("CHECK global_trade_rows:", len(global_rows))
    print("CHECK global_trade_ids:", global_id_count)

    if len(global_rows) != 9:
        errors.append(f"expected 9 global trade rows, got {len(global_rows)}")

    if global_id_count != 9:
        errors.append(f"expected 9 global trade ids, got {global_id_count}")

    root_attribution = compute_root_cause_attribution(rows)

    print("CHECK root_cause_groups:", len(root_attribution))

    if len(root_attribution) != 4:
        errors.append(f"expected 4 root cause groups, got {len(root_attribution)}")

    if errors:
        print("")
        print("REGRESSION: FAIL")
        for err in errors:
            print("ERROR:", err)
        return 1

    print("")
    print("REGRESSION: PASS")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--market-csv", default=str(DEFAULT_MARKET_CSV))
    parser.add_argument("--trade-index", type=int)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--export-ml-csv", default="")
    parser.add_argument("--export-aggregate-csv-dir", default="")
    parser.add_argument("--export-ml-dataset-dir", default="")
    parser.add_argument("--export-feature-prep-dir", default="")
    parser.add_argument("--export-leakage-audit-dir", default="")
    parser.add_argument("--export-feature-importance-dir", default="")
    parser.add_argument("--export-feature-stability-dir", default="")
    parser.add_argument("--export-signal-discovery-dir", default="")
    parser.add_argument("--export-global-trades-dir", default="")
    parser.add_argument("--export-cross-archive-root-cause-dir", default="")
    parser.add_argument("--export-cross-archive-feature-importance-dir", default="")
    parser.add_argument("--export-cross-archive-signal-discovery-dir", default="")
    parser.add_argument("--export-multi-archive-loader-dir", default="")
    parser.add_argument("--archive-registry-md", default="docs/trade_inspector/V7B_ARCHIVE_REGISTRY_P79A_2026-06-14.md")
    parser.add_argument("--archive-id", default="P79A_pre_run_2026-06-10")
    parser.add_argument("--label-list", default=str(DEFAULT_LABEL_LIST))
    parser.add_argument("--label-registry", default=str(DEFAULT_LABEL_REGISTRY))
    parser.add_argument("--update-label-registry", action="store_true")
    parser.add_argument("--run-regression-tests", action="store_true")
    parser.add_argument("--archive-intake-dir", default="")
    parser.add_argument("--run-archive-intake", action="store_true")
    args = parser.parse_args()

    if args.run_regression_tests:
        return run_builtin_regression_validation(args)

    if args.run_archive_intake:
        if not args.archive_intake_dir:
            raise SystemExit("--archive-intake-dir is required with --run-archive-intake")
        return run_archive_intake_validation(args)

    archive_dir = Path(args.archive_dir)
    trades = read_jsonl(archive_dir / "trades_l1.jsonl")
    audit_rows = read_jsonl(archive_dir / "execution_audit.jsonl")
    log_rows = parse_key_value_log(archive_dir / "l1_paper.log")
    regime_rows = log_rows
    regime_index = build_regime_index(regime_rows)
    timestamps, prices = parse_market_rows(Path(args.market_csv))
    label_list = load_human_labels(Path(args.label_list))
    existing_registry = load_label_registry(Path(args.label_registry))
    label_map = assign_human_labels(trades, label_list, existing_registry)

    if args.update_label_registry:
        save_label_registry(Path(args.label_registry), label_map)

    print("TRADE INSPECTOR V6")
    print("archive_dir:", archive_dir)
    print("trades:", len(trades))
    print("audit_events:", len(audit_rows))
    print("regime_events:", len(regime_rows))
    print("market_rows:", len(timestamps))
    print("human_labels_loaded:", len(label_list))
    print("label_registry_entries:", len(label_map))
    print("")

    rows = build_rows(trades, audit_rows, regime_index, timestamps, prices, label_map)

    if args.trade_index is not None:
        if args.trade_index < 1 or args.trade_index > len(trades):
            raise SystemExit(f"Invalid trade index: {args.trade_index}")
        trade = trades[args.trade_index - 1]
        entry, exit_ = find_matching_entry_exit(trade, audit_rows)
        print_trade_report(args.trade_index, trade, entry, exit_, audit_rows, regime_index, timestamps, prices, label_map)
        return 0

    if args.summary:
        print_summary(rows)
        return 0

    if args.aggregate:
        print_aggregate_intelligence(rows)
        return 0

    if args.export_ml_csv:
        export_ml_csv(rows, Path(args.export_ml_csv))
        return 0

    if args.export_aggregate_csv_dir:
        export_aggregate_csvs(rows, Path(args.export_aggregate_csv_dir))
        return 0

    if args.export_ml_dataset_dir:
        export_ml_dataset(rows, Path(args.export_ml_dataset_dir))
        return 0

    if args.export_feature_prep_dir:
        export_feature_preparation(rows, Path(args.export_feature_prep_dir))
        return 0

    if args.export_leakage_audit_dir:
        export_leakage_audit_dataset(rows, Path(args.export_leakage_audit_dir))
        return 0

    if args.export_feature_importance_dir:
        export_feature_importance(rows, Path(args.export_feature_importance_dir))
        return 0

    if args.export_feature_stability_dir:
        export_feature_stability(rows, Path(args.export_feature_stability_dir))
        return 0

    if args.export_signal_discovery_dir:
        export_predictive_signal_discovery(rows, Path(args.export_signal_discovery_dir))
        return 0

    if args.export_global_trades_dir:
        export_global_trade_database(rows, Path(args.export_global_trades_dir), args.archive_id)
        return 0

    cross_archive_export_requested = (
        args.export_cross_archive_root_cause_dir
        or args.export_cross_archive_feature_importance_dir
        or args.export_cross_archive_signal_discovery_dir
    )

    if cross_archive_export_requested and args.archive_registry_md:
        registry_rows = load_archive_registry_md(Path(args.archive_registry_md))
        cross_rows = []
        errors = []

        for registry_row in registry_rows:
            if str(registry_row.get("include_in_v7", "")).strip().lower() != "yes":
                continue

            source_archive_id = str(registry_row.get("archive_id", "")).strip()
            source_archive_path = Path(str(registry_row.get("archive_path", "")).strip())

            try:
                loaded_rows = load_rows_for_archive(
                    source_archive_id,
                    source_archive_path,
                    Path(args.market_csv),
                    Path(args.label_list),
                    Path(args.label_registry),
                )
                cross_rows.extend(loaded_rows)
            except Exception as exc:
                errors.append(f"{source_archive_id}: {exc}")

        if errors:
            raise SystemExit("Cross-archive load failed: " + " | ".join(errors))

        rows = cross_rows
        args.archive_id = "MULTI_ARCHIVE_REGISTRY"
        print("cross_archive_registry:", args.archive_registry_md)
        print("cross_archive_rows:", len(rows))
        print("cross_archive_archives:", len(registry_rows))
        print("")

    if args.export_cross_archive_root_cause_dir:
        export_cross_archive_root_cause(rows, Path(args.export_cross_archive_root_cause_dir), args.archive_id)
        return 0

    if args.export_cross_archive_feature_importance_dir:
        export_cross_archive_feature_importance(rows, Path(args.export_cross_archive_feature_importance_dir), args.archive_id)
        return 0

    if args.export_cross_archive_signal_discovery_dir:
        export_cross_archive_signal_discovery(rows, Path(args.export_cross_archive_signal_discovery_dir), args.archive_id)
        return 0

    if args.export_multi_archive_loader_dir:
        export_multi_archive_loader(
            Path(args.archive_registry_md),
            Path(args.export_multi_archive_loader_dir),
            Path(args.market_csv),
            Path(args.label_list),
            Path(args.label_registry),
        )
        return 0

    print("No selection provided.")
    print("Examples:")
    print("python3 tools/trade_inspector/inspect_trades.py --trade-index 1")
    print("python3 tools/trade_inspector/inspect_trades.py --summary")
    print("python3 tools/trade_inspector/inspect_trades.py --aggregate")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-csv data/processed/trade_inspector/ml_v3.csv")
    print("python3 tools/trade_inspector/inspect_trades.py --export-aggregate-csv-dir reports/trade_inspector/aggregate_v3a")
    print("python3 tools/trade_inspector/inspect_trades.py --export-ml-dataset-dir data/ml/trade_inspector_v4")
    print("python3 tools/trade_inspector/inspect_trades.py --export-feature-prep-dir data/ml/trade_inspector_v4b")
    print("python3 tools/trade_inspector/inspect_trades.py --export-leakage-audit-dir data/ml/trade_inspector_v4c")
    print("python3 tools/trade_inspector/inspect_trades.py --export-feature-importance-dir data/ml/trade_inspector_v5")
    print("python3 tools/trade_inspector/inspect_trades.py --export-feature-stability-dir data/ml/trade_inspector_v5c")
    print("python3 tools/trade_inspector/inspect_trades.py --export-signal-discovery-dir data/ml/trade_inspector_v6")
    print("python3 tools/trade_inspector/inspect_trades.py --export-global-trades-dir outputs/trade_inspector/v7 --archive-id P79A_pre_run_2026-06-10")
    print("python3 tools/trade_inspector/inspect_trades.py --export-cross-archive-root-cause-dir outputs/trade_inspector/v7d --archive-id P79A_pre_run_2026-06-10")
    print("python3 tools/trade_inspector/inspect_trades.py --export-cross-archive-feature-importance-dir outputs/trade_inspector/v7e --archive-id P79A_pre_run_2026-06-10")
    print("python3 tools/trade_inspector/inspect_trades.py --export-cross-archive-signal-discovery-dir outputs/trade_inspector/v7f --archive-id P79A_pre_run_2026-06-10")
    print("python3 tools/trade_inspector/inspect_trades.py --export-multi-archive-loader-dir outputs/trade_inspector/v7g --archive-registry-md docs/trade_inspector/V7B_ARCHIVE_REGISTRY_P79A_2026-06-14.md")
    print("python3 tools/trade_inspector/inspect_trades.py --run-regression-tests")
    print("python3 tools/trade_inspector/inspect_trades.py --run-archive-intake --archive-intake-dir live_logs/archive/P79A_pre_run_2026-06-10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
