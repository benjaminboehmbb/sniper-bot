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

__all__ = (
    "DEFAULT_ARCHIVE_DIR",
    "DEFAULT_LABEL_LIST",
    "DEFAULT_LABEL_REGISTRY",
    "DEFAULT_MARKET_CSV",
    "FUTURE_WINDOWS_MIN",
    "HIGH_LEAKAGE_EXACT",
    "HIGH_LEAKAGE_PREFIXES",
    "MEDIUM_LEAKAGE_EXACT",
    "NON_FEATURE_COLUMNS",
    "SAFE_ID_COLUMNS",
    "TARGET_COLUMNS",
    "add_ml_targets",
    "aggregate_group_rows",
    "aggregate_top_improvement_rows",
    "assign_human_labels",
    "audit_feature_leakage",
    "avg",
    "build_category_maps",
    "build_feature_catalog",
    "build_ml_dataset_rows",
    "build_ml_row",
    "build_model_ready_rows",
    "build_regime_index",
    "build_rows",
    "build_trade_family",
    "build_trade_id",
    "calculate_counterfactuals",
    "calculate_trade_path",
    "chart_time",
    "classify_signal_reliability",
    "classify_signal_support",
    "compact_trade_time",
    "compute_confidence_layer",
    "compute_diagnosis",
    "compute_quality_score",
    "compute_root_cause_attribution",
    "count_valid_jsonl",
    "dataset_split_from_trade_id",
    "discover_pair_groups",
    "discover_signal_groups",
    "evaluate_split_quality",
    "export_aggregate_csvs",
    "export_cross_archive_feature_importance",
    "export_cross_archive_root_cause",
    "export_cross_archive_signal_discovery",
    "export_feature_importance",
    "export_feature_preparation",
    "export_feature_stability",
    "export_global_trade_database",
    "export_leakage_audit_dataset",
    "export_ml_csv",
    "export_ml_dataset",
    "export_multi_archive_loader",
    "export_predictive_signal_discovery",
    "export_root_cause_attribution_csv",
    "extract_regime_features",
    "feature_importance_rows",
    "find_matching_entry_exit",
    "group_rows",
    "group_stats",
    "interpretation_flags",
    "is_number_like",
    "load_archive_registry_md",
    "load_human_labels",
    "load_label_registry",
    "load_rows_for_archive",
    "main",
    "market_price",
    "market_timestamp",
    "median",
    "parse_cause_weights",
    "parse_key_value_log",
    "parse_market_rows",
    "parse_ts",
    "pearson_abs",
    "print_aggregate_intelligence",
    "print_group_table",
    "print_kv",
    "print_root_cause_attribution",
    "print_split_quality",
    "print_summary",
    "print_top_improvement_candidates",
    "print_trade_family_summary",
    "print_trade_report",
    "quality_flags",
    "read_jsonl",
    "run_archive_intake_validation",
    "run_builtin_regression_validation",
    "safe_float",
    "safe_int",
    "safe_rate",
    "safe_text",
    "save_label_registry",
    "score_band",
    "signed_diagnosis",
    "stability_class",
    "std",
    "trade_pnl_from_price",
    "ts_key",
    "write_csv_rows",
)

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
    from .cli_orchestration import (
        DEFAULT_ARCHIVE_DIR,
        DEFAULT_LABEL_LIST,
        DEFAULT_LABEL_REGISTRY,
        DEFAULT_MARKET_CSV,
        main,
    )
    from .console_reporting import (
        print_aggregate_intelligence,
        print_group_table,
        print_root_cause_attribution,
        print_summary,
        print_top_improvement_candidates,
        print_trade_family_summary,
        print_trade_report,
    )
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
    from .regression_validation import run_builtin_regression_validation
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
    from cli_orchestration import (
        DEFAULT_ARCHIVE_DIR,
        DEFAULT_LABEL_LIST,
        DEFAULT_LABEL_REGISTRY,
        DEFAULT_MARKET_CSV,
        main,
    )
    from console_reporting import (
        print_aggregate_intelligence,
        print_group_table,
        print_root_cause_attribution,
        print_summary,
        print_top_improvement_candidates,
        print_trade_family_summary,
        print_trade_report,
    )
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
    from regression_validation import run_builtin_regression_validation
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
if __name__ == "__main__":
    raise SystemExit(main())
