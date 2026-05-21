#!/usr/bin/env python3
# ASCII-only.
# Research-only probabilistic state transition graph builder.
# Does not affect trading logic.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--health-csv", default="reports/trade_lifecycle/trade_health_detail_STEP9A_FULL_43M.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    p.add_argument("--min-support", type=int, default=3)
    return p.parse_args()


def bucket_health(v: float) -> str:
    if v <= -80:
        return "H_NEG_EXTREME"
    if v <= -55:
        return "H_NEG_STRONG"
    if v <= -25:
        return "H_NEG"
    if v < 5:
        return "H_NEUTRAL"
    if v < 35:
        return "H_POS"
    if v < 70:
        return "H_POS_STRONG"
    return "H_EXTREME_POS"


def bucket_delta(v: float) -> str:
    if v <= -80:
        return "D_COLLAPSE_EXTREME"
    if v <= -30:
        return "D_COLLAPSE"
    if v < 10:
        return "D_FLAT"
    if v < 50:
        return "D_RECOVER"
    return "D_SURGE"


def bucket_pnl(v: float) -> str:
    if v <= -500:
        return "PNL_SEVERE_NEG"
    if v <= -200:
        return "PNL_MAJOR_NEG"
    if v <= -50:
        return "PNL_NEG"
    if v < 0:
        return "PNL_SMALL_NEG"
    if v < 50:
        return "PNL_SMALL_POS"
    if v < 200:
        return "PNL_POS"
    return "PNL_STRONG_POS"


def score_sign(v: int) -> str:
    if v > 0:
        return "SCORE_POS"
    if v < 0:
        return "SCORE_NEG"
    return "SCORE_ZERO"


def make_state(row: pd.Series) -> str:
    return "|".join(
        [
            str(row["side"]).lower(),
            str(row["market_regime"]).lower(),
            str(row["atr_quality"]).lower(),
            bucket_health(float(row["trade_health_score"])),
            bucket_delta(float(row["health_delta"])),
            bucket_pnl(float(row["unrealized_pnl"])),
            score_sign(int(row["current_score"])),
        ]
    )


def classify_edge(row: pd.Series) -> str:
    pnl_delta = float(row["to_pnl"]) - float(row["from_pnl"])
    health_delta = float(row["to_health"]) - float(row["from_health"])

    if pnl_delta >= 100 and health_delta > 0:
        return "RECOVERY_ACCELERATION"
    if pnl_delta >= 50:
        return "RECOVERY"
    if pnl_delta <= -100 and health_delta < 0:
        return "COLLAPSE_ACCELERATION"
    if pnl_delta <= -50:
        return "COLLAPSE"
    if health_delta > 20:
        return "HEALTH_IMPROVING"
    if health_delta < -20:
        return "HEALTH_DEGRADING"
    return "STABLE_OR_NOISE"


def main() -> int:
    args = parse_args()

    in_path = Path(args.health_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing health csv: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "timestamp_utc",
        "side",
        "duration_sec",
        "market_regime",
        "atr_quality",
        "current_score",
        "unrealized_pnl",
        "pnl_delta",
        "trade_health_score",
        "trade_health_state",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()

    # Recompute health_delta from consecutive snapshots per trade.
    df = df.sort_values(["trade_id", "duration_sec"]).reset_index(drop=True)
    df["health_delta"] = (
        df.groupby("trade_id")["trade_health_score"]
        .diff()
        .fillna(0.0)
    )

    df["state_node"] = df.apply(make_state, axis=1)

    edges = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("duration_sec").reset_index(drop=True)

        if len(g) < 2:
            continue

        final_pnl = float(g.iloc[-1]["unrealized_pnl"])
        final_health = float(g.iloc[-1]["trade_health_score"])

        for i in range(1, len(g)):
            prev = g.iloc[i - 1]
            cur = g.iloc[i]

            edges.append(
                {
                    "trade_id": trade_id,
                    "side": str(cur["side"]).lower(),
                    "from_duration_sec": float(prev["duration_sec"]),
                    "to_duration_sec": float(cur["duration_sec"]),
                    "from_state": str(prev["state_node"]),
                    "to_state": str(cur["state_node"]),
                    "from_regime": str(prev["market_regime"]).lower(),
                    "to_regime": str(cur["market_regime"]).lower(),
                    "from_health": float(prev["trade_health_score"]),
                    "to_health": float(cur["trade_health_score"]),
                    "from_pnl": float(prev["unrealized_pnl"]),
                    "to_pnl": float(cur["unrealized_pnl"]),
                    "pnl_delta": float(cur["unrealized_pnl"]) - float(prev["unrealized_pnl"]),
                    "health_delta": float(cur["trade_health_score"]) - float(prev["trade_health_score"]),
                    "final_trade_pnl": final_pnl,
                    "final_health": final_health,
                    "final_win": int(final_pnl > 0),
                }
            )

    edge_df = pd.DataFrame(edges)

    if edge_df.empty:
        raise SystemExit("ERROR: no state transitions found")

    edge_df["edge_class"] = edge_df.apply(classify_edge, axis=1)

    edge_summary = (
        edge_df.groupby(["side", "from_state", "to_state"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            transition_probability_denominator=("from_state", "count"),
            avg_pnl_delta=("pnl_delta", "mean"),
            sum_pnl_delta=("pnl_delta", "sum"),
            avg_health_delta=("health_delta", "mean"),
            avg_to_pnl=("to_pnl", "mean"),
            avg_to_health=("to_health", "mean"),
            winrate_final=("final_win", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
    )

    # Denominator per from_state, not per edge.
    denom = (
        edge_df.groupby(["side", "from_state"], dropna=False)
        .agg(from_state_count=("trade_id", "count"))
        .reset_index()
    )

    edge_summary = edge_summary.drop(columns=["transition_probability_denominator"])
    edge_summary = edge_summary.merge(denom, on=["side", "from_state"], how="left")
    edge_summary["transition_probability"] = edge_summary["count"] / edge_summary["from_state_count"]

    edge_summary = edge_summary[edge_summary["count"] >= args.min_support].copy()

    edge_summary["edge_risk_class"] = edge_summary.apply(
        lambda r: (
            "HIGH_RECOVERY_EDGE"
            if float(r["avg_pnl_delta"]) >= 50 and float(r["winrate_final"]) >= 0.60
            else (
                "HIGH_COLLAPSE_EDGE"
                if float(r["avg_pnl_delta"]) <= -50 and float(r["winrate_final"]) <= 0.40
                else (
                    "STABLE_PROFIT_EDGE"
                    if float(r["avg_final_pnl"]) > 0 and float(r["winrate_final"]) >= 0.60
                    else (
                        "STABLE_LOSS_EDGE"
                        if float(r["avg_final_pnl"]) < 0 and float(r["winrate_final"]) <= 0.40
                        else "MIXED_EDGE"
                    )
                )
            )
        ),
        axis=1,
    )

    node_summary = (
        edge_df.groupby(["side", "from_state"], dropna=False)
        .agg(
            outgoing_edges=("to_state", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_from_pnl=("from_pnl", "mean"),
            avg_from_health=("from_health", "mean"),
            avg_next_pnl_delta=("pnl_delta", "mean"),
            avg_next_health_delta=("health_delta", "mean"),
            final_winrate=("final_win", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_final_pnl"])
    )

    node_summary = node_summary[node_summary["outgoing_edges"] >= args.min_support].copy()

    detail_path = out_dir / f"state_transition_graph_edges_detail_{args.label}.csv"
    edge_summary_path = out_dir / f"state_transition_graph_edges_summary_{args.label}.csv"
    node_summary_path = out_dir / f"state_transition_graph_nodes_summary_{args.label}.csv"

    edge_df.to_csv(detail_path, index=False)
    edge_summary.to_csv(edge_summary_path, index=False)
    node_summary.to_csv(node_summary_path, index=False)

    print("STATE TRANSITION GRAPH COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"edges: {len(edge_df)}")
    print(f"edge_summary_rows: {len(edge_summary)}")
    print(f"node_summary_rows: {len(node_summary)}")
    print(f"detail_csv: {detail_path}")
    print(f"edge_summary_csv: {edge_summary_path}")
    print(f"node_summary_csv: {node_summary_path}")
    print()

    print("BEST RECOVERY EDGES")
    print(
        edge_summary.sort_values(
            ["avg_pnl_delta", "winrate_final", "count"],
            ascending=[False, False, False],
        )
        .head(30)
        .to_string(index=False)
    )
    print()

    print("WORST COLLAPSE EDGES")
    print(
        edge_summary.sort_values(
            ["avg_pnl_delta", "winrate_final", "count"],
            ascending=[True, True, False],
        )
        .head(30)
        .to_string(index=False)
    )
    print()

    print("BEST NODES")
    print(
        node_summary.sort_values(
            ["avg_final_pnl", "final_winrate", "outgoing_edges"],
            ascending=[False, False, False],
        )
        .head(30)
        .to_string(index=False)
    )
    print()

    print("WORST NODES")
    print(
        node_summary.sort_values(
            ["avg_final_pnl", "final_winrate", "outgoing_edges"],
            ascending=[True, True, False],
        )
        .head(30)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
