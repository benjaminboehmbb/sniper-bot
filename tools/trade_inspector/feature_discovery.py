from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .aggregate_csv import group_rows, group_stats
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_int, safe_text
else:
    from aggregate_csv import group_rows, group_stats
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_int, safe_text


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
