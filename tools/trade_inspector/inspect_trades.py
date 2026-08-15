#!/usr/bin/env python3
# tools/trade_inspector/inspect_trades.py
# Trade Inspector V1D.
# Read-only trade diagnosis tool.
# Human analysis + ML feature export.
# ASCII-only.

from __future__ import annotations

import argparse
import importlib as _importlib
from pathlib import Path
from typing import Any

_EXPORTS_BY_OWNER = (
    (
        "aggregate_csv",
        (
            "aggregate_group_rows",
            "aggregate_top_improvement_rows",
            "avg",
            "compute_root_cause_attribution",
            "export_aggregate_csvs",
            "export_root_cause_attribution_csv",
            "group_rows",
            "group_stats",
            "parse_cause_weights",
        ),
    ),
    (
        "archive_intake",
        (
            "count_valid_jsonl",
            "run_archive_intake_validation",
        ),
    ),
    (
        "cli_orchestration",
        (
            "DEFAULT_ARCHIVE_DIR",
            "DEFAULT_LABEL_LIST",
            "DEFAULT_LABEL_REGISTRY",
            "DEFAULT_MARKET_CSV",
            "main",
        ),
    ),
    (
        "console_reporting",
        (
            "print_aggregate_intelligence",
            "print_group_table",
            "print_root_cause_attribution",
            "print_summary",
            "print_top_improvement_candidates",
            "print_trade_family_summary",
            "print_trade_report",
        ),
    ),
    ("csv_persistence", ("write_csv_rows",)),
    (
        "cross_archive_feature_importance",
        ("export_cross_archive_feature_importance",),
    ),
    ("cross_archive_root_cause", ("export_cross_archive_root_cause",)),
    (
        "cross_archive_signal_discovery",
        ("export_cross_archive_signal_discovery",),
    ),
    (
        "feature_preparation",
        (
            "NON_FEATURE_COLUMNS",
            "TARGET_COLUMNS",
            "build_category_maps",
            "build_feature_catalog",
            "build_model_ready_rows",
            "export_feature_preparation",
            "is_number_like",
        ),
    ),
    (
        "feature_importance",
        (
            "export_feature_importance",
            "feature_importance_rows",
            "pearson_abs",
        ),
    ),
    (
        "feature_discovery",
        (
            "classify_signal_reliability",
            "classify_signal_support",
            "discover_pair_groups",
            "discover_signal_groups",
            "export_predictive_signal_discovery",
            "safe_rate",
        ),
    ),
    (
        "feature_stability",
        (
            "export_feature_stability",
            "median",
            "stability_class",
            "std",
        ),
    ),
    ("global_trade_database", ("export_global_trade_database",)),
    (
        "inspection_primitives",
        (
            "parse_ts",
            "safe_float",
            "safe_int",
            "safe_text",
            "ts_key",
        ),
    ),
    (
        "label_registry",
        (
            "assign_human_labels",
            "load_human_labels",
            "load_label_registry",
            "save_label_registry",
        ),
    ),
    (
        "leakage_audit",
        (
            "HIGH_LEAKAGE_EXACT",
            "HIGH_LEAKAGE_PREFIXES",
            "MEDIUM_LEAKAGE_EXACT",
            "SAFE_ID_COLUMNS",
            "audit_feature_leakage",
            "export_leakage_audit_dataset",
        ),
    ),
    (
        "ml_dataset",
        (
            "add_ml_targets",
            "build_ml_dataset_rows",
            "dataset_split_from_trade_id",
            "evaluate_split_quality",
            "export_ml_dataset",
            "print_kv",
            "print_split_quality",
        ),
    ),
    (
        "multi_archive_loader",
        (
            "export_multi_archive_loader",
            "load_archive_registry_md",
            "load_rows_for_archive",
            "market_price",
            "market_timestamp",
            "parse_key_value_log",
            "parse_market_rows",
            "read_jsonl",
        ),
    ),
    (
        "path_diagnosis",
        (
            "FUTURE_WINDOWS_MIN",
            "calculate_counterfactuals",
            "calculate_trade_path",
            "compute_confidence_layer",
            "compute_diagnosis",
            "compute_quality_score",
            "interpretation_flags",
            "quality_flags",
            "score_band",
            "signed_diagnosis",
            "trade_pnl_from_price",
        ),
    ),
    ("raw_ml_csv", ("export_ml_csv",)),
    ("regression_validation", ("run_builtin_regression_validation",)),
    (
        "regime_identity_rows",
        (
            "build_ml_row",
            "build_regime_index",
            "build_rows",
            "build_trade_family",
            "build_trade_id",
            "chart_time",
            "compact_trade_time",
            "extract_regime_features",
            "find_matching_entry_exit",
        ),
    ),
)

__all__ = tuple(
    sorted(
        _export_name
        for _owner_name, _export_names in _EXPORTS_BY_OWNER
        for _export_name in _export_names
    )
)

_owner_prefix = f"{__package__}." if __package__ else ""
for _owner_name, _export_names in _EXPORTS_BY_OWNER:
    _owner_module = _importlib.import_module(f"{_owner_prefix}{_owner_name}")
    for _export_name in _export_names:
        globals()[_export_name] = getattr(_owner_module, _export_name)

if __name__ == "__main__":
    raise SystemExit(main())
