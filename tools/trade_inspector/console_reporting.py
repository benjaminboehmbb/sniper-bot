from __future__ import annotations

from typing import Any

if __package__:
    from .aggregate_csv import compute_root_cause_attribution, group_rows, group_stats
    from .inspection_primitives import safe_float, safe_int, safe_text
    from .ml_dataset import print_kv
    from .regime_identity_rows import build_ml_row
else:
    from aggregate_csv import compute_root_cause_attribution, group_rows, group_stats
    from inspection_primitives import safe_float, safe_int, safe_text
    from ml_dataset import print_kv
    from regime_identity_rows import build_ml_row


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
