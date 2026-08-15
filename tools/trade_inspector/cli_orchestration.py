"""Command-line orchestration for the Trade Inspector facade."""

from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .aggregate_csv import export_aggregate_csvs
    from .archive_intake import run_archive_intake_validation
    from .console_reporting import print_aggregate_intelligence, print_summary, print_trade_report
    from .cross_archive_feature_importance import export_cross_archive_feature_importance
    from .cross_archive_root_cause import export_cross_archive_root_cause
    from .cross_archive_signal_discovery import export_cross_archive_signal_discovery
    from .feature_discovery import export_predictive_signal_discovery
    from .feature_importance import export_feature_importance
    from .feature_preparation import export_feature_preparation
    from .feature_stability import export_feature_stability
    from .global_trade_database import export_global_trade_database
    from .label_registry import (
        assign_human_labels,
        load_human_labels,
        load_label_registry,
        save_label_registry,
    )
    from .leakage_audit import export_leakage_audit_dataset
    from .ml_dataset import export_ml_dataset
    from .multi_archive_loader import (
        export_multi_archive_loader,
        load_archive_registry_md,
        load_rows_for_archive,
        parse_key_value_log,
        parse_market_rows,
        read_jsonl,
    )
    from .raw_ml_csv import export_ml_csv
    from .regression_validation import run_builtin_regression_validation
    from .regime_identity_rows import (
        build_regime_index,
        build_rows,
        find_matching_entry_exit,
    )
else:
    from aggregate_csv import export_aggregate_csvs
    from archive_intake import run_archive_intake_validation
    from console_reporting import print_aggregate_intelligence, print_summary, print_trade_report
    from cross_archive_feature_importance import export_cross_archive_feature_importance
    from cross_archive_root_cause import export_cross_archive_root_cause
    from cross_archive_signal_discovery import export_cross_archive_signal_discovery
    from feature_discovery import export_predictive_signal_discovery
    from feature_importance import export_feature_importance
    from feature_preparation import export_feature_preparation
    from feature_stability import export_feature_stability
    from global_trade_database import export_global_trade_database
    from label_registry import (
        assign_human_labels,
        load_human_labels,
        load_label_registry,
        save_label_registry,
    )
    from leakage_audit import export_leakage_audit_dataset
    from ml_dataset import export_ml_dataset
    from multi_archive_loader import (
        export_multi_archive_loader,
        load_archive_registry_md,
        load_rows_for_archive,
        parse_key_value_log,
        parse_market_rows,
        read_jsonl,
    )
    from raw_ml_csv import export_ml_csv
    from regression_validation import run_builtin_regression_validation
    from regime_identity_rows import (
        build_regime_index,
        build_rows,
        find_matching_entry_exit,
    )


DEFAULT_ARCHIVE_DIR = Path("live_logs/archive/P79A_pre_run_2026-06-10")
DEFAULT_MARKET_CSV = Path("data/l1_full_run.csv")


DEFAULT_LABEL_LIST = Path("config/trade_inspector/human_labels.txt")
DEFAULT_LABEL_REGISTRY = Path("config/trade_inspector/trade_label_registry.csv")


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
        args.archive_dir = args.archive_intake_dir
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


__all__ = [
    "DEFAULT_ARCHIVE_DIR",
    "DEFAULT_LABEL_LIST",
    "DEFAULT_LABEL_REGISTRY",
    "DEFAULT_MARKET_CSV",
    "main",
]
