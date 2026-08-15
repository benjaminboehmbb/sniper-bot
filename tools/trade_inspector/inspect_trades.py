#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1D.
# Read-only trade diagnosis tool.
# Human analysis + ML feature export.
# ASCII-only.

from __future__ import annotations

import argparse
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
    from .cross_archive_feature_importance import export_cross_archive_feature_importance
    from .cross_archive_root_cause import export_cross_archive_root_cause
    from .cross_archive_signal_discovery import export_cross_archive_signal_discovery
    from .feature_preparation import (
        NON_FEATURE_COLUMNS,
        TARGET_COLUMNS,
        build_category_maps,
        build_feature_catalog,
        build_model_ready_rows,
        export_feature_preparation,
        is_number_like,
    )
    from .feature_importance import export_feature_importance, feature_importance_rows, pearson_abs
    from .feature_discovery import (
        classify_signal_reliability,
        classify_signal_support,
        discover_pair_groups,
        discover_signal_groups,
        export_predictive_signal_discovery,
        safe_rate,
    )
    from .feature_stability import export_feature_stability, median, stability_class, std
    from .global_trade_database import export_global_trade_database
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
    from .multi_archive_loader import (
        export_multi_archive_loader,
        load_archive_registry_md,
        load_rows_for_archive,
        market_price,
        market_timestamp,
        parse_key_value_log,
        parse_market_rows,
        read_jsonl,
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
    from cross_archive_feature_importance import export_cross_archive_feature_importance
    from cross_archive_root_cause import export_cross_archive_root_cause
    from cross_archive_signal_discovery import export_cross_archive_signal_discovery
    from feature_preparation import (
        NON_FEATURE_COLUMNS,
        TARGET_COLUMNS,
        build_category_maps,
        build_feature_catalog,
        build_model_ready_rows,
        export_feature_preparation,
        is_number_like,
    )
    from feature_importance import export_feature_importance, feature_importance_rows, pearson_abs
    from feature_discovery import (
        classify_signal_reliability,
        classify_signal_support,
        discover_pair_groups,
        discover_signal_groups,
        export_predictive_signal_discovery,
        safe_rate,
    )
    from feature_stability import export_feature_stability, median, stability_class, std
    from global_trade_database import export_global_trade_database
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
    from multi_archive_loader import (
        export_multi_archive_loader,
        load_archive_registry_md,
        load_rows_for_archive,
        market_price,
        market_timestamp,
        parse_key_value_log,
        parse_market_rows,
        read_jsonl,
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
