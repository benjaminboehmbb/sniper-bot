import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def utc_now_datestr() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_jsonl(path: Path) -> pd.DataFrame:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_no} in {path}: {exc}") from exc
    return pd.DataFrame(rows)


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return read_jsonl(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file type: {path}. Expected .csv or .jsonl")


def find_first_existing_column(df: pd.DataFrame, candidates: List[str], label: str) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    raise ValueError(
        f"Could not detect {label}. Expected one of {candidates}. Actual columns: {list(df.columns)}"
    )


def detect_trade_timestamp_columns(df: pd.DataFrame) -> Tuple[str, Optional[str]]:
    entry_candidates = [
        "entry_timestamp_utc",
        "entry_time_utc",
        "entry_time",
        "entry_timestamp",
        "open_time",
        "timestamp",
        "start_time",
    ]
    exit_candidates = [
        "exit_timestamp_utc",
        "exit_time_utc",
        "exit_time",
        "exit_timestamp",
        "close_time",
        "end_time",
    ]

    entry_col = find_first_existing_column(df, entry_candidates, "trade entry timestamp")
    exit_col = None
    try:
        exit_col = find_first_existing_column(df, exit_candidates, "trade exit timestamp")
    except ValueError:
        exit_col = None

    return entry_col, exit_col


def detect_side_column(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "side",
        "position_side",
        "direction",
        "trade_side",
        "pos_side",
    ]
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def detect_pnl_column(df: pd.DataFrame) -> str:
    candidates = [
        "pnl",
        "total_pnl",
        "net_pnl",
        "profit",
        "trade_pnl",
    ]
    return find_first_existing_column(df, candidates, "trade pnl column")


def detect_pnl_pct_column(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "pnl_pct",
        "return_pct",
        "trade_return_pct",
        "roi",
        "profit_pct",
    ]
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def detect_trade_id_column(df: pd.DataFrame) -> Optional[str]:
    candidates = [
        "trade_id",
        "id",
        "position_id",
        "system_state_id",
    ]
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def normalize_side(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "unknown"
    s = str(value).strip().lower()
    if s in ("long", "buy", "bull"):
        return "long"
    if s in ("short", "sell", "bear"):
        return "short"
    return s


def load_trades(trades_path: Path) -> pd.DataFrame:
    df = load_table(trades_path)

    if df.empty:
        raise ValueError(f"Trades file is empty: {trades_path}")

    entry_col, exit_col = detect_trade_timestamp_columns(df)
    pnl_col = detect_pnl_column(df)
    pnl_pct_col = detect_pnl_pct_column(df)
    side_col = detect_side_column(df)
    trade_id_col = detect_trade_id_column(df)

    out = df.copy()

    out[entry_col] = pd.to_datetime(out[entry_col], utc=True, errors="coerce")
    if exit_col is not None:
        out[exit_col] = pd.to_datetime(out[exit_col], utc=True, errors="coerce")
    out[pnl_col] = pd.to_numeric(out[pnl_col], errors="coerce")

    if pnl_pct_col is not None:
        out[pnl_pct_col] = pd.to_numeric(out[pnl_pct_col], errors="coerce")

    keep_cols = {
        "entry_timestamp_utc": entry_col,
        "pnl": pnl_col,
    }

    if exit_col is not None:
        keep_cols["exit_timestamp_utc"] = exit_col
    if pnl_pct_col is not None:
        keep_cols["pnl_pct"] = pnl_pct_col
    if side_col is not None:
        keep_cols["side"] = side_col
    if trade_id_col is not None:
        keep_cols["trade_id"] = trade_id_col

    rename_map = {v: k for k, v in keep_cols.items()}
    out = out[list(keep_cols.values())].rename(columns=rename_map)

    if "side" not in out.columns:
        out["side"] = "unknown"
    else:
        out["side"] = out["side"].map(normalize_side)

    if "trade_id" not in out.columns:
        out["trade_id"] = np.arange(1, len(out) + 1)

    out = out.dropna(subset=["entry_timestamp_utc", "pnl"]).sort_values("entry_timestamp_utc").reset_index(drop=True)

    if out.empty:
        raise ValueError("No valid trades after cleanup.")

    if "exit_timestamp_utc" not in out.columns:
        out["exit_timestamp_utc"] = pd.NaT

    if "pnl_pct" not in out.columns:
        out["pnl_pct"] = np.nan

    out["holding_minutes"] = (
        (out["exit_timestamp_utc"] - out["entry_timestamp_utc"]).dt.total_seconds() / 60.0
    )
    return out


def load_regimes(regime_features_path: Path) -> pd.DataFrame:
    df = pd.read_csv(regime_features_path)

    if df.empty:
        raise ValueError(f"Regime features file is empty: {regime_features_path}")

    ts_col = find_first_existing_column(
        df,
        ["timestamp_utc", "date", "datetime", "timestamp"],
        "regime timestamp column",
    )
    label_col = find_first_existing_column(
        df,
        ["regime_label", "regime_label_raw"],
        "regime label column",
    )

    out = df.copy()
    out[ts_col] = pd.to_datetime(out[ts_col], utc=True, errors="coerce")
    out = out.dropna(subset=[ts_col, label_col]).sort_values(ts_col).rename(
        columns={ts_col: "timestamp_utc", label_col: "regime_label"}
    )

    if out.empty:
        raise ValueError("No valid regime rows after cleanup.")

    keep_optional = [
        "close",
        "ret_7d",
        "ret_30d",
        "ret_90d",
        "vol_30d",
        "eff_30d",
        "drawdown_180d",
        "trend_score_30d",
        "trend_score_90d",
    ]
    keep_cols = ["timestamp_utc", "regime_label"] + [c for c in keep_optional if c in out.columns]
    out = out[keep_cols].copy()

    out["regime_day"] = out["timestamp_utc"].dt.floor("D")
    out = out.drop_duplicates(subset=["regime_day"], keep="last").reset_index(drop=True)

    return out


def assign_regimes_to_trades(trades: pd.DataFrame, regimes: pd.DataFrame) -> pd.DataFrame:
    regime_lookup = regimes[["regime_day", "regime_label"]].copy()
    regime_lookup = regime_lookup.rename(columns={"regime_day": "entry_day"})

    out = trades.copy()
    out["entry_day"] = out["entry_timestamp_utc"].dt.floor("D")

    out = out.merge(regime_lookup, on="entry_day", how="left")

    if out["regime_label"].isna().any():
        out["regime_label"] = out["regime_label"].fillna("UNMAPPED")

    return out


def calc_max_drawdown_from_trade_sequence(pnl_series: pd.Series, start_capital: float) -> Tuple[float, float]:
    equity = start_capital + pnl_series.fillna(0.0).cumsum()
    running_peak = equity.cummax()
    drawdown_abs = running_peak - equity
    max_dd_abs = float(drawdown_abs.max()) if len(drawdown_abs) > 0 else 0.0
    max_dd_pct = float((drawdown_abs / running_peak.replace(0.0, np.nan)).max()) if len(drawdown_abs) > 0 else 0.0

    if np.isnan(max_dd_abs):
        max_dd_abs = 0.0
    if np.isnan(max_dd_pct):
        max_dd_pct = 0.0

    return max_dd_abs, max_dd_pct


def summarize_trade_group(df: pd.DataFrame, start_capital: float) -> Dict[str, object]:
    pnl = df["pnl"].fillna(0.0)
    wins = pnl[pnl > 0.0]
    losses = pnl[pnl < 0.0]

    gross_profit = float(wins.sum())
    gross_loss_abs = float(abs(losses.sum()))
    total_pnl = float(pnl.sum())
    num_trades = int(len(df))
    winrate = float((pnl > 0.0).mean()) if num_trades > 0 else 0.0
    avg_pnl = float(pnl.mean()) if num_trades > 0 else 0.0

    if gross_loss_abs > 0.0:
        profit_factor = gross_profit / gross_loss_abs
    else:
        profit_factor = np.nan if gross_profit == 0.0 else np.inf

    max_dd_abs, max_dd_pct = calc_max_drawdown_from_trade_sequence(pnl, start_capital)

    pnl_std = float(pnl.std(ddof=0)) if num_trades > 0 else 0.0
    sharpe_like = float((avg_pnl / pnl_std) * math.sqrt(num_trades)) if pnl_std > 0.0 else np.nan

    avg_holding_minutes = float(df["holding_minutes"].dropna().mean()) if "holding_minutes" in df.columns else np.nan
    avg_pnl_pct = float(df["pnl_pct"].dropna().mean()) if "pnl_pct" in df.columns else np.nan

    return {
        "num_trades": num_trades,
        "gross_profit": gross_profit,
        "gross_loss_abs": gross_loss_abs,
        "total_pnl": total_pnl,
        "return_pct_vs_start_capital": float(total_pnl / start_capital) if start_capital != 0 else np.nan,
        "winrate": winrate,
        "profit_factor": profit_factor,
        "avg_pnl": avg_pnl,
        "avg_pnl_pct": avg_pnl_pct,
        "avg_holding_minutes": avg_holding_minutes,
        "max_drawdown_abs_seq": max_dd_abs,
        "max_drawdown_pct_seq": max_dd_pct,
        "sharpe_like": sharpe_like,
        "first_entry_utc": df["entry_timestamp_utc"].min(),
        "last_entry_utc": df["entry_timestamp_utc"].max(),
    }


def build_summary_tables(trades_with_regime: pd.DataFrame, start_capital: float) -> Tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows: List[Dict[str, object]] = []
    side_rows: List[Dict[str, object]] = []

    for regime_label, group in trades_with_regime.groupby("regime_label", sort=False):
        stats = summarize_trade_group(group, start_capital=start_capital)
        stats["regime_label"] = regime_label
        summary_rows.append(stats)

        for side, side_group in group.groupby("side", sort=False):
            side_stats = summarize_trade_group(side_group, start_capital=start_capital)
            side_stats["regime_label"] = regime_label
            side_stats["side"] = side
            side_rows.append(side_stats)

    summary_df = pd.DataFrame(summary_rows)
    side_df = pd.DataFrame(side_rows)

    if not summary_df.empty:
        summary_df = summary_df[
            [
                "regime_label",
                "num_trades",
                "gross_profit",
                "gross_loss_abs",
                "total_pnl",
                "return_pct_vs_start_capital",
                "winrate",
                "profit_factor",
                "avg_pnl",
                "avg_pnl_pct",
                "avg_holding_minutes",
                "max_drawdown_abs_seq",
                "max_drawdown_pct_seq",
                "sharpe_like",
                "first_entry_utc",
                "last_entry_utc",
            ]
        ].sort_values(["total_pnl", "profit_factor"], ascending=[False, False])

    if not side_df.empty:
        side_df = side_df[
            [
                "regime_label",
                "side",
                "num_trades",
                "gross_profit",
                "gross_loss_abs",
                "total_pnl",
                "return_pct_vs_start_capital",
                "winrate",
                "profit_factor",
                "avg_pnl",
                "avg_pnl_pct",
                "avg_holding_minutes",
                "max_drawdown_abs_seq",
                "max_drawdown_pct_seq",
                "sharpe_like",
                "first_entry_utc",
                "last_entry_utc",
            ]
        ].sort_values(["regime_label", "side"])

    return summary_df, side_df


def build_timeline_summary(trades_with_regime: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    for regime_label, group in trades_with_regime.groupby("regime_label", sort=False):
        grouped_days = (
            group.groupby(group["entry_timestamp_utc"].dt.floor("D"))
            .agg(
                num_trades=("trade_id", "size"),
                total_pnl=("pnl", "sum"),
                winrate=("pnl", lambda s: float((s > 0.0).mean()) if len(s) > 0 else 0.0),
            )
            .reset_index()
            .rename(columns={"entry_timestamp_utc": "entry_day"})
        )

        if grouped_days.empty:
            continue

        rows.append(
            {
                "regime_label": regime_label,
                "active_days_with_trades": int(len(grouped_days)),
                "mean_daily_trades": float(grouped_days["num_trades"].mean()),
                "max_daily_trades": int(grouped_days["num_trades"].max()),
                "mean_daily_pnl": float(grouped_days["total_pnl"].mean()),
                "best_daily_pnl": float(grouped_days["total_pnl"].max()),
                "worst_daily_pnl": float(grouped_days["total_pnl"].min()),
            }
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("mean_daily_pnl", ascending=False)
    return out


def save_markdown_report(
    out_path: Path,
    trades_path: Path,
    regimes_path: Path,
    mapped_trades: pd.DataFrame,
    summary_df: pd.DataFrame,
    side_df: pd.DataFrame,
    timeline_df: pd.DataFrame,
    start_capital: float,
) -> None:
    lines: List[str] = []

    lines.append("# Strategy by Regime Report")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- trades_file: `{trades_path}`")
    lines.append(f"- regimes_file: `{regimes_path}`")
    lines.append(f"- start_capital_for_regime_stats: `{start_capital}`")
    lines.append(f"- total_trades_loaded: `{len(mapped_trades)}`")
    lines.append("")

    lines.append("## Overall")
    lines.append("")
    overall = summarize_trade_group(mapped_trades, start_capital=start_capital)
    for key, value in overall.items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")

    lines.append("## Regime Summary")
    lines.append("")
    if summary_df.empty:
        lines.append("No regime summary rows generated.")
    else:
        lines.append("| regime_label | num_trades | total_pnl | return_pct_vs_start_capital | winrate | profit_factor | avg_pnl | avg_holding_minutes | max_drawdown_pct_seq | sharpe_like |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for _, row in summary_df.iterrows():
            lines.append(
                "| {regime} | {n} | {pnl:.4f} | {ret:.4f} | {wr:.4f} | {pf} | {avg_pnl:.4f} | {hold} | {mdd:.4f} | {sharpe} |".format(
                    regime=row["regime_label"],
                    n=int(row["num_trades"]),
                    pnl=float(row["total_pnl"]),
                    ret=float(row["return_pct_vs_start_capital"]),
                    wr=float(row["winrate"]),
                    pf="inf" if np.isinf(row["profit_factor"]) else f"{float(row['profit_factor']):.4f}" if pd.notna(row["profit_factor"]) else "nan",
                    avg_pnl=float(row["avg_pnl"]),
                    hold="nan" if pd.isna(row["avg_holding_minutes"]) else f"{float(row['avg_holding_minutes']):.2f}",
                    mdd=float(row["max_drawdown_pct_seq"]),
                    sharpe="nan" if pd.isna(row["sharpe_like"]) else f"{float(row['sharpe_like']):.4f}",
                )
            )
    lines.append("")

    lines.append("## Regime + Side Summary")
    lines.append("")
    if side_df.empty:
        lines.append("No regime-side rows generated.")
    else:
        lines.append("| regime_label | side | num_trades | total_pnl | winrate | profit_factor | avg_pnl |")
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
        for _, row in side_df.iterrows():
            lines.append(
                "| {regime} | {side} | {n} | {pnl:.4f} | {wr:.4f} | {pf} | {avg_pnl:.4f} |".format(
                    regime=row["regime_label"],
                    side=row["side"],
                    n=int(row["num_trades"]),
                    pnl=float(row["total_pnl"]),
                    wr=float(row["winrate"]),
                    pf="inf" if np.isinf(row["profit_factor"]) else f"{float(row['profit_factor']):.4f}" if pd.notna(row["profit_factor"]) else "nan",
                    avg_pnl=float(row["avg_pnl"]),
                )
            )
    lines.append("")

    lines.append("## Timeline Activity Summary")
    lines.append("")
    if timeline_df.empty:
        lines.append("No timeline summary rows generated.")
    else:
        lines.append("| regime_label | active_days_with_trades | mean_daily_trades | max_daily_trades | mean_daily_pnl | best_daily_pnl | worst_daily_pnl |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for _, row in timeline_df.iterrows():
            lines.append(
                "| {regime} | {days} | {mdt:.2f} | {xdt} | {mdp:.4f} | {bdp:.4f} | {wdp:.4f} |".format(
                    regime=row["regime_label"],
                    days=int(row["active_days_with_trades"]),
                    mdt=float(row["mean_daily_trades"]),
                    xdt=int(row["max_daily_trades"]),
                    mdp=float(row["mean_daily_pnl"]),
                    bdp=float(row["best_daily_pnl"]),
                    wdp=float(row["worst_daily_pnl"]),
                )
            )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Trades are mapped to regime by ENTRY DAY.")
    lines.append("- Regime performance is evaluated from actual realized trade outcomes.")
    lines.append("- This is the basis for later regime-aware gating and strategy switching.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze realized strategy performance by detected BTC regime."
    )
    parser.add_argument("--trades", required=True, help="Path to trades file (.jsonl or .csv).")
    parser.add_argument("--regimes", required=True, help="Path to regime daily features CSV from analyze_btc_regimes.py.")
    parser.add_argument("--outdir", default="analysis_outputs", help="Output directory.")
    parser.add_argument("--tag", default="", help="Optional filename tag.")
    parser.add_argument(
        "--start-capital",
        type=float,
        default=10000.0,
        help="Reference capital used for return_pct_vs_start_capital and sequence drawdown stats.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    trades_path = Path(args.trades).resolve()
    regimes_path = Path(args.regimes).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not trades_path.exists():
        raise FileNotFoundError(f"Trades file not found: {trades_path}")
    if not regimes_path.exists():
        raise FileNotFoundError(f"Regimes file not found: {regimes_path}")

    date_tag = utc_now_datestr()
    name_tag = f"_{args.tag}" if args.tag else ""

    trades = load_trades(trades_path)
    regimes = load_regimes(regimes_path)
    mapped_trades = assign_regimes_to_trades(trades, regimes)

    summary_df, side_df = build_summary_tables(mapped_trades, start_capital=args.start_capital)
    timeline_df = build_timeline_summary(mapped_trades)

    mapped_out = outdir / f"strategy_by_regime_trades{name_tag}_{date_tag}.csv"
    summary_out = outdir / f"strategy_by_regime_summary{name_tag}_{date_tag}.csv"
    side_out = outdir / f"strategy_by_regime_side_summary{name_tag}_{date_tag}.csv"
    timeline_out = outdir / f"strategy_by_regime_timeline{name_tag}_{date_tag}.csv"
    report_out = outdir / f"strategy_by_regime_report{name_tag}_{date_tag}.md"

    mapped_trades.to_csv(mapped_out, index=False)
    summary_df.to_csv(summary_out, index=False)
    side_df.to_csv(side_out, index=False)
    timeline_df.to_csv(timeline_out, index=False)

    save_markdown_report(
        out_path=report_out,
        trades_path=trades_path,
        regimes_path=regimes_path,
        mapped_trades=mapped_trades,
        summary_df=summary_df,
        side_df=side_df,
        timeline_df=timeline_df,
        start_capital=args.start_capital,
    )

    print(f"[OK] mapped_trades: {mapped_out}")
    print(f"[OK] regime_summary: {summary_out}")
    print(f"[OK] regime_side_summary: {side_out}")
    print(f"[OK] timeline_summary: {timeline_out}")
    print(f"[OK] report: {report_out}")


if __name__ == "__main__":
    main()