#!/usr/bin/env python3
# ASCII-only.
# Summarize robustness and support quality of state transition graph.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--edge-summary", default="reports/trade_lifecycle/state_transition_graph_edges_summary_STEP9A_FULL_43M.csv")
    p.add_argument("--node-summary", default="reports/trade_lifecycle/state_transition_graph_nodes_summary_STEP9A_FULL_43M.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def support_class(n: int) -> str:
    if n >= 30:
        return "HIGH_SUPPORT"
    if n >= 10:
        return "MEDIUM_SUPPORT"
    if n >= 5:
        return "LOW_SUPPORT"
    return "VERY_LOW_SUPPORT"


def main() -> int:
    args = parse_args()

    edge_path = Path(args.edge_summary)
    node_path = Path(args.node_summary)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not edge_path.exists():
        raise SystemExit(f"ERROR: missing edge summary: {edge_path}")
    if not node_path.exists():
        raise SystemExit(f"ERROR: missing node summary: {node_path}")

    edges = pd.read_csv(edge_path)
    nodes = pd.read_csv(node_path)

    edges["support_class"] = edges["count"].apply(lambda v: support_class(int(v)))
    nodes["support_class"] = nodes["outgoing_edges"].apply(lambda v: support_class(int(v)))

    robust_edges = edges[
        (edges["count"] >= 5)
        & (edges["unique_trades"] >= 3)
    ].copy()

    robust_nodes = nodes[
        (nodes["outgoing_edges"] >= 5)
        & (nodes["unique_trades"] >= 3)
    ].copy()

    best_edges = robust_edges.sort_values(
        ["avg_final_pnl", "winrate_final", "count"],
        ascending=[False, False, False],
    )

    worst_edges = robust_edges.sort_values(
        ["avg_final_pnl", "winrate_final", "count"],
        ascending=[True, True, False],
    )

    best_nodes = robust_nodes.sort_values(
        ["avg_final_pnl", "final_winrate", "outgoing_edges"],
        ascending=[False, False, False],
    )

    worst_nodes = robust_nodes.sort_values(
        ["avg_final_pnl", "final_winrate", "outgoing_edges"],
        ascending=[True, True, False],
    )

    out_edges = out_dir / f"state_graph_quality_edges_{args.label}.csv"
    out_nodes = out_dir / f"state_graph_quality_nodes_{args.label}.csv"

    robust_edges.to_csv(out_edges, index=False)
    robust_nodes.to_csv(out_nodes, index=False)

    print("STATE GRAPH QUALITY SUMMARY COMPLETE")
    print(f"edges_total: {len(edges)}")
    print(f"edges_robust: {len(robust_edges)}")
    print(f"nodes_total: {len(nodes)}")
    print(f"nodes_robust: {len(robust_nodes)}")
    print(f"edges_csv: {out_edges}")
    print(f"nodes_csv: {out_nodes}")
    print()

    print("BEST ROBUST EDGES")
    print(best_edges.head(25).to_string(index=False))
    print()

    print("WORST ROBUST EDGES")
    print(worst_edges.head(25).to_string(index=False))
    print()

    print("BEST ROBUST NODES")
    print(best_nodes.head(25).to_string(index=False))
    print()

    print("WORST ROBUST NODES")
    print(worst_nodes.head(25).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
