from __future__ import annotations

from pathlib import Path
from typing import Any

if __package__:
    from .csv_persistence import write_csv_rows
    from .inspection_primitives import safe_float, safe_int, safe_text
else:
    from csv_persistence import write_csv_rows
    from inspection_primitives import safe_float, safe_int, safe_text


def avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        value = safe_text(row.get(key)) or "UNKNOWN"
        groups.setdefault(value, []).append(row)
    return groups


def group_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pnl_values = [safe_float(row.get("pnl"), 0.0) for row in rows]
    pnl_pct_values = [safe_float(row.get("pnl_pct"), 0.0) for row in rows]
    exit_eff_values = [safe_float(row.get("exit_efficiency_24h_pct"), 0.0) for row in rows]
    opp_values = [safe_float(row.get("opportunity_loss_24h_pct"), 0.0) for row in rows]
    overall_values = [safe_float(row.get("overall_score"), 0.0) for row in rows]

    winners = sum(1 for row in rows if safe_int(row.get("is_winner"), 0) == 1)
    losers = sum(1 for row in rows if safe_int(row.get("is_loser"), 0) == 1)

    return {
        "count": len(rows),
        "winners": winners,
        "losers": losers,
        "winrate": winners / len(rows) if rows else 0.0,
        "total_pnl": sum(pnl_values),
        "avg_pnl": avg(pnl_values),
        "avg_pnl_pct": avg(pnl_pct_values),
        "avg_exit_efficiency_24h_pct": avg(exit_eff_values),
        "avg_opportunity_loss_24h_pct": avg(opp_values),
        "avg_overall_score": avg(overall_values),
    }


def parse_cause_weights(value: object) -> dict[str, float]:
    text = safe_text(value)
    output: dict[str, float] = {}

    if not text:
        return output

    for part in text.split("|"):
        if "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        key = safe_text(key)
        weight = safe_float(raw_value, 0.0)
        if key:
            output[key] = weight

    return output


def compute_root_cause_attribution(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[str, dict[str, float]] = {}

    for row in rows:
        pnl = safe_float(row.get("pnl"), 0.0)
        opportunity_loss = safe_float(row.get("opportunity_loss_24h_pct"), 0.0)
        impact_score = safe_float(row.get("impact_score"), 0.0)
        priority_score = safe_float(row.get("priority_score"), 0.0)
        cause_weights = parse_cause_weights(row.get("cause_weights"))

        for cause, weight in cause_weights.items():
            share = weight / 100.0
            bucket = totals.setdefault(cause, {
                "cause_weight_sum": 0.0,
                "trade_count_weighted": 0.0,
                "negative_pnl_contribution": 0.0,
                "opportunity_loss_contribution": 0.0,
                "impact_contribution": 0.0,
                "priority_contribution": 0.0,
            })

            bucket["cause_weight_sum"] += weight
            bucket["trade_count_weighted"] += share
            bucket["negative_pnl_contribution"] += max(0.0, -pnl) * share
            bucket["opportunity_loss_contribution"] += opportunity_loss * share
            bucket["impact_contribution"] += impact_score * share
            bucket["priority_contribution"] += priority_score * share

    total_weight = sum(v["cause_weight_sum"] for v in totals.values())
    total_neg = sum(v["negative_pnl_contribution"] for v in totals.values())
    total_opp = sum(v["opportunity_loss_contribution"] for v in totals.values())
    total_impact = sum(v["impact_contribution"] for v in totals.values())
    total_priority = sum(v["priority_contribution"] for v in totals.values())

    output: list[dict[str, Any]] = []

    for cause, values in totals.items():
        output.append({
            "root_cause": cause,
            "cause_weight_sum": values["cause_weight_sum"],
            "cause_share_pct": values["cause_weight_sum"] / total_weight if total_weight else 0.0,
            "trade_count_weighted": values["trade_count_weighted"],
            "negative_pnl_contribution": values["negative_pnl_contribution"],
            "negative_pnl_share_pct": values["negative_pnl_contribution"] / total_neg if total_neg else 0.0,
            "opportunity_loss_contribution": values["opportunity_loss_contribution"],
            "opportunity_loss_share_pct": values["opportunity_loss_contribution"] / total_opp if total_opp else 0.0,
            "impact_contribution": values["impact_contribution"],
            "impact_share_pct": values["impact_contribution"] / total_impact if total_impact else 0.0,
            "priority_contribution": values["priority_contribution"],
            "priority_share_pct": values["priority_contribution"] / total_priority if total_priority else 0.0,
        })

    output.sort(key=lambda row: safe_float(row.get("priority_contribution"), 0.0), reverse=True)
    return output


def export_root_cause_attribution_csv(rows: list[dict[str, Any]], output_dir: Path) -> None:
    write_csv_rows(
        output_dir / "aggregate_root_cause_attribution.csv",
        compute_root_cause_attribution(rows),
    )


def aggregate_group_rows(rows: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []

    for group_name, items in group_rows(rows, group_key).items():
        stats = group_stats(items)
        output.append({
            "group_key": group_key,
            "group": group_name,
            "count": stats["count"],
            "winners": stats["winners"],
            "losers": stats["losers"],
            "winrate": stats["winrate"],
            "total_pnl": stats["total_pnl"],
            "avg_pnl": stats["avg_pnl"],
            "avg_pnl_pct": stats["avg_pnl_pct"],
            "avg_exit_efficiency_24h_pct": stats["avg_exit_efficiency_24h_pct"],
            "avg_opportunity_loss_24h_pct": stats["avg_opportunity_loss_24h_pct"],
            "avg_overall_score": stats["avg_overall_score"],
        })

    output.sort(key=lambda row: safe_float(row.get("total_pnl"), 0.0), reverse=True)
    return output


def aggregate_top_improvement_rows(rows: list[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            safe_float(row.get("priority_score"), 0.0),
            safe_float(row.get("impact_score"), 0.0),
            safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
        ),
        reverse=True,
    )

    output: list[dict[str, Any]] = []
    for rank, row in enumerate(ranked[:limit], start=1):
        output.append({
            "rank": rank,
            "human_label": safe_text(row.get("human_label")),
            "trade_id": safe_text(row.get("trade_id")),
            "root_cause": safe_text(row.get("root_cause")),
            "priority": safe_text(row.get("priority")),
            "priority_score": safe_int(row.get("priority_score"), 0),
            "impact_score": safe_int(row.get("impact_score"), 0),
            "root_cause_confidence": safe_int(row.get("root_cause_confidence"), 0),
            "opportunity_loss_24h_pct": safe_float(row.get("opportunity_loss_24h_pct"), 0.0),
            "exit_efficiency_24h_pct": safe_float(row.get("exit_efficiency_24h_pct"), 0.0),
            "pnl": safe_float(row.get("pnl"), 0.0),
            "pnl_pct": safe_float(row.get("pnl_pct"), 0.0),
            "entry_regime_label": safe_text(row.get("entry_regime_label")),
            "entry_risk_label": safe_text(row.get("entry_risk_label")),
            "regime_aligned": safe_int(row.get("regime_aligned"), 0),
            "regime_changed_during_trade": safe_int(row.get("regime_changed_during_trade"), 0),
            "entry_score_at_entry": safe_int(row.get("entry_score_at_entry"), 0),
            "entry_time_chart": safe_text(row.get("entry_time_chart")),
            "exit_time_chart": safe_text(row.get("exit_time_chart")),
        })

    return output


def export_aggregate_csvs(rows: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    global_stats = group_stats(rows)
    write_csv_rows(output_dir / "aggregate_global_summary.csv", [{
        "trades": global_stats["count"],
        "winners": global_stats["winners"],
        "losers": global_stats["losers"],
        "winrate": global_stats["winrate"],
        "total_pnl": global_stats["total_pnl"],
        "avg_pnl": global_stats["avg_pnl"],
        "avg_pnl_pct": global_stats["avg_pnl_pct"],
        "avg_exit_efficiency_24h_pct": global_stats["avg_exit_efficiency_24h_pct"],
        "avg_opportunity_loss_24h_pct": global_stats["avg_opportunity_loss_24h_pct"],
        "avg_overall_score": global_stats["avg_overall_score"],
    }])

    group_keys = [
        "root_cause",
        "entry_regime_label",
        "entry_risk_label",
        "regime_aligned",
        "priority",
        "quality_class",
        "overall_score_band",
        "trade_family_group",
        "trade_family",
    ]

    for key in group_keys:
        write_csv_rows(
            output_dir / f"aggregate_by_{key}.csv",
            aggregate_group_rows(rows, key),
        )

    write_csv_rows(
        output_dir / "aggregate_top_improvement_candidates.csv",
        aggregate_top_improvement_rows(rows, limit=100),
    )

    export_root_cause_attribution_csv(rows, output_dir)

    print("Aggregate CSV export directory:", output_dir)
    print("files:")
    for path in sorted(output_dir.glob("*.csv")):
        print("-", path)
