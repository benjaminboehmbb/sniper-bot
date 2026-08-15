from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import compute_root_cause_attribution
    from .feature_discovery import discover_pair_groups, discover_signal_groups
    from .inspection_primitives import safe_text
    from .label_registry import assign_human_labels, load_human_labels, load_label_registry
    from .multi_archive_loader import parse_key_value_log, parse_market_rows, read_jsonl
    from .regime_identity_rows import build_regime_index, build_rows
else:
    from aggregate_csv import compute_root_cause_attribution
    from feature_discovery import discover_pair_groups, discover_signal_groups
    from inspection_primitives import safe_text
    from label_registry import assign_human_labels, load_human_labels, load_label_registry
    from multi_archive_loader import parse_key_value_log, parse_market_rows, read_jsonl
    from regime_identity_rows import build_regime_index, build_rows


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
