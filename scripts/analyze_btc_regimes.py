import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


def utc_now_datestr() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def detect_timestamp_column(df: pd.DataFrame) -> str:
    candidates = [
        "timestamp",
        "open_time",
        "datetime",
        "date",
        "time",
        "close_time",
    ]
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    raise ValueError(
        "No timestamp column found. Expected one of: "
        + ", ".join(candidates)
        + f". Actual columns: {list(df.columns)}"
    )


def detect_close_column(df: pd.DataFrame) -> str:
    candidates = [
        "close",
        "Close",
        "close_price",
        "price_close",
        "c",
    ]
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in [c.lower() for c in candidates]:
        if candidate in lower_map:
            return lower_map[candidate]
    raise ValueError(
        "No close column found. Expected one of: "
        + ", ".join(candidates)
        + f". Actual columns: {list(df.columns)}"
    )


def load_market_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    ts_col = detect_timestamp_column(df)
    close_col = detect_close_column(df)

    df = df[[ts_col, close_col]].copy()
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True, errors="coerce")
    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")

    df = (
        df.dropna(subset=[ts_col, close_col])
        .sort_values(ts_col)
        .drop_duplicates(ts_col)
        .rename(columns={ts_col: "timestamp_utc", close_col: "close"})
        .set_index("timestamp_utc")
    )

    if df.empty:
        raise ValueError("Loaded dataframe is empty after timestamp/close cleanup.")

    return df


def resample_daily(df_1m: pd.DataFrame) -> pd.DataFrame:
    daily = df_1m["close"].resample("1D").last().dropna().to_frame()
    daily["ret_1d"] = daily["close"].pct_change()
    return daily


def rolling_efficiency_ratio(close: pd.Series, window: int) -> pd.Series:
    net_move = close.diff(window).abs()
    total_move = close.diff().abs().rolling(window).sum()
    er = net_move / total_move.replace(0.0, np.nan)
    return er.clip(lower=0.0, upper=1.0)


def rolling_trend_score(close: pd.Series, window: int) -> pd.Series:
    ret = close.pct_change(window)
    ema_fast = close.ewm(span=max(3, window // 3), adjust=False).mean()
    ema_slow = close.ewm(span=max(5, window), adjust=False).mean()
    ema_component = (ema_fast / ema_slow) - 1.0
    score = 0.7 * ret + 0.3 * ema_component
    return score


def build_features(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy()

    out["ret_7d"] = out["close"].pct_change(7)
    out["ret_14d"] = out["close"].pct_change(14)
    out["ret_30d"] = out["close"].pct_change(30)
    out["ret_60d"] = out["close"].pct_change(60)
    out["ret_90d"] = out["close"].pct_change(90)

    out["vol_14d"] = out["ret_1d"].rolling(14).std() * math.sqrt(365.0)
    out["vol_30d"] = out["ret_1d"].rolling(30).std() * math.sqrt(365.0)

    out["eff_14d"] = rolling_efficiency_ratio(out["close"], 14)
    out["eff_30d"] = rolling_efficiency_ratio(out["close"], 30)
    out["eff_60d"] = rolling_efficiency_ratio(out["close"], 60)

    out["trend_score_30d"] = rolling_trend_score(out["close"], 30)
    out["trend_score_90d"] = rolling_trend_score(out["close"], 90)

    peak_180d = out["close"].rolling(180, min_periods=20).max()
    out["drawdown_180d"] = (out["close"] / peak_180d) - 1.0

    out["rolling_high_30d"] = out["close"].rolling(30, min_periods=10).max()
    out["rolling_low_30d"] = out["close"].rolling(30, min_periods=10).min()
    out["range_ratio_30d"] = (out["rolling_high_30d"] / out["rolling_low_30d"]) - 1.0

    return out


@dataclass(frozen=True)
class Thresholds:
    crisis_drawdown: float = -0.35
    crisis_ret_30d: float = -0.18
    bull_ret_90d: float = 0.25
    bear_ret_90d: float = -0.20
    side_ret_30d: float = 0.08
    high_vol: float = 0.90
    low_efficiency: float = 0.28
    high_efficiency: float = 0.45
    recovery_ret_30d: float = 0.12
    recovery_ret_90d: float = -0.10


def classify_row(row: pd.Series, th: Thresholds) -> str:
    required = ["ret_30d", "ret_90d", "vol_30d", "eff_30d"]
    for col in required:
        if pd.isna(row[col]):
            return "UNCLASSIFIED"

    ret_30d = float(row["ret_30d"])
    ret_90d = float(row["ret_90d"])
    vol_30d = float(row["vol_30d"])
    eff_30d = float(row["eff_30d"])
    drawdown_180d = float(row["drawdown_180d"]) if not pd.isna(row["drawdown_180d"]) else 0.0

    if drawdown_180d <= th.crisis_drawdown and ret_30d <= th.crisis_ret_30d:
        return "CRISIS_EVENT"

    if ret_90d >= th.bull_ret_90d and eff_30d >= th.high_efficiency:
        return "UP_TREND_HIGH_VOL" if vol_30d >= th.high_vol else "UP_TREND_LOW_VOL"

    if ret_90d <= th.bear_ret_90d and eff_30d >= th.high_efficiency:
        return "DOWN_TREND_HIGH_VOL" if vol_30d >= th.high_vol else "DOWN_TREND_LOW_VOL"

    if ret_30d >= th.recovery_ret_30d and ret_90d > th.recovery_ret_90d and eff_30d >= th.low_efficiency:
        return "RECOVERY_PHASE"

    if abs(ret_30d) <= th.side_ret_30d or eff_30d <= th.low_efficiency:
        return "SIDEWAYS_HIGH_VOL" if vol_30d >= th.high_vol else "SIDEWAYS_LOW_VOL"

    if ret_90d > 0.0:
        return "UP_TREND_HIGH_VOL" if vol_30d >= th.high_vol else "UP_TREND_LOW_VOL"

    if ret_90d < 0.0:
        return "DOWN_TREND_HIGH_VOL" if vol_30d >= th.high_vol else "DOWN_TREND_LOW_VOL"

    return "SIDEWAYS_LOW_VOL"


def classify_features(features: pd.DataFrame, th: Thresholds) -> pd.DataFrame:
    out = features.copy()
    out["regime_label_raw"] = out.apply(lambda row: classify_row(row, th), axis=1)
    return out


def smooth_labels(labels: pd.Series, persistence_days: int) -> pd.Series:
    labels = labels.fillna("UNCLASSIFIED").copy()

    smoothed: List[str] = []
    candidate_label = None
    candidate_run = 0

    for i, label in enumerate(labels.tolist()):
        if i == 0:
            smoothed.append(label)
            candidate_label = label
            candidate_run = 1
            continue

        prev_smoothed = smoothed[-1]

        if label == candidate_label:
            candidate_run += 1
        else:
            candidate_label = label
            candidate_run = 1

        if label != prev_smoothed and candidate_run < persistence_days:
            smoothed.append(prev_smoothed)
        else:
            smoothed.append(label)

    return pd.Series(smoothed, index=labels.index, name="regime_label")


def build_segments(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []

    if df.empty:
        return pd.DataFrame(
            columns=[
                "segment_id",
                "regime_label",
                "start_utc",
                "end_utc",
                "days",
                "start_price",
                "end_price",
                "return_pct",
            ]
        )

    segment_id = 1
    current_label = df.iloc[0][label_col]
    start_ts = df.index[0]
    start_price = float(df.iloc[0]["close"])

    prev_ts = start_ts
    prev_price = start_price

    for ts, row in df.iloc[1:].iterrows():
        label = row[label_col]
        price = float(row["close"])

        if label != current_label:
            rows.append(
                {
                    "segment_id": segment_id,
                    "regime_label": current_label,
                    "start_utc": start_ts,
                    "end_utc": prev_ts,
                    "days": int((prev_ts - start_ts).days) + 1,
                    "start_price": start_price,
                    "end_price": prev_price,
                    "return_pct": (prev_price / start_price) - 1.0,
                }
            )
            segment_id += 1
            current_label = label
            start_ts = ts
            start_price = price

        prev_ts = ts
        prev_price = price

    rows.append(
        {
            "segment_id": segment_id,
            "regime_label": current_label,
            "start_utc": start_ts,
            "end_utc": prev_ts,
            "days": int((prev_ts - start_ts).days) + 1,
            "start_price": start_price,
            "end_price": prev_price,
            "return_pct": (prev_price / start_price) - 1.0,
        }
    )

    out = pd.DataFrame(rows)
    out["start_utc"] = pd.to_datetime(out["start_utc"], utc=True)
    out["end_utc"] = pd.to_datetime(out["end_utc"], utc=True)
    return out


def summarize_labels(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    return (
        df.groupby(label_col)
        .agg(
            num_days=("close", "size"),
            mean_ret_30d=("ret_30d", "mean"),
            mean_ret_90d=("ret_90d", "mean"),
            mean_vol_30d=("vol_30d", "mean"),
            mean_eff_30d=("eff_30d", "mean"),
            mean_drawdown_180d=("drawdown_180d", "mean"),
        )
        .reset_index()
        .sort_values("num_days", ascending=False)
    )


def latest_phase_snapshot(df: pd.DataFrame, label_col: str) -> Dict[str, object]:
    latest = df.iloc[-1]
    latest_ts = df.index[-1]

    def safe_float(value: object) -> Optional[float]:
        if pd.isna(value):
            return None
        return float(value)

    return {
        "as_of_utc": latest_ts.isoformat(),
        "close": safe_float(latest["close"]),
        "regime_label": str(latest[label_col]),
        "ret_7d": safe_float(latest["ret_7d"]),
        "ret_30d": safe_float(latest["ret_30d"]),
        "ret_90d": safe_float(latest["ret_90d"]),
        "vol_30d": safe_float(latest["vol_30d"]),
        "eff_30d": safe_float(latest["eff_30d"]),
        "drawdown_180d": safe_float(latest["drawdown_180d"]),
        "trend_score_30d": safe_float(latest["trend_score_30d"]),
        "trend_score_90d": safe_float(latest["trend_score_90d"]),
    }


def save_markdown_report(
    out_path: Path,
    csv_path: Path,
    daily_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    segments_df: pd.DataFrame,
    latest_snapshot: Dict[str, object],
    label_col: str,
    persistence_days: int,
) -> None:
    lines: List[str] = []

    lines.append("# BTC Regime Analysis Report")
    lines.append("")
    lines.append("## Input")
    lines.append("")
    lines.append(f"- source_csv: `{csv_path}`")
    lines.append(f"- start_utc: `{daily_df.index.min().isoformat()}`")
    lines.append(f"- end_utc: `{daily_df.index.max().isoformat()}`")
    lines.append(f"- daily_rows: `{len(daily_df)}`")
    lines.append(f"- label_column: `{label_col}`")
    lines.append(f"- persistence_days: `{persistence_days}`")
    lines.append("")

    lines.append("## Latest Phase Snapshot")
    lines.append("")
    for key, value in latest_snapshot.items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")

    lines.append("## Regime Summary")
    lines.append("")
    if summary_df.empty:
        lines.append("No summary rows generated.")
    else:
        lines.append("| regime_label | num_days | mean_ret_30d | mean_ret_90d | mean_vol_30d | mean_eff_30d | mean_drawdown_180d |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for _, row in summary_df.iterrows():
            lines.append(
                "| {label} | {num_days} | {r30:.4f} | {r90:.4f} | {vol:.4f} | {eff:.4f} | {dd:.4f} |".format(
                    label=row[label_col],
                    num_days=int(row["num_days"]),
                    r30=float(row["mean_ret_30d"]),
                    r90=float(row["mean_ret_90d"]),
                    vol=float(row["mean_vol_30d"]),
                    eff=float(row["mean_eff_30d"]),
                    dd=float(row["mean_drawdown_180d"]),
                )
            )
    lines.append("")

    lines.append("## Regime Segments")
    lines.append("")
    if segments_df.empty:
        lines.append("No segments generated.")
    else:
        lines.append("| segment_id | regime_label | start_utc | end_utc | days | start_price | end_price | return_pct |")
        lines.append("| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |")
        for _, row in segments_df.iterrows():
            lines.append(
                "| {segment_id} | {label} | {start_utc} | {end_utc} | {days} | {start_price:.2f} | {end_price:.2f} | {ret:.4f} |".format(
                    segment_id=int(row["segment_id"]),
                    label=row["regime_label"],
                    start_utc=pd.Timestamp(row["start_utc"]).isoformat(),
                    end_utc=pd.Timestamp(row["end_utc"]).isoformat(),
                    days=int(row["days"]),
                    start_price=float(row["start_price"]),
                    end_price=float(row["end_price"]),
                    ret=float(row["return_pct"]),
                )
            )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Deterministic rule-based regime detection.")
    lines.append("- Designed for both historical segmentation and current phase detection.")
    lines.append("- Labels are smoothed to reduce noisy one-day flips.")
    lines.append("- Threshold tuning can later be tied to strategy performance by regime.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic BTC regime analysis for historical segmentation and current phase detection."
    )
    parser.add_argument("--csv", required=True, help="Path to BTC market CSV.")
    parser.add_argument("--outdir", default="analysis_outputs", help="Output directory.")
    parser.add_argument("--tag", default="", help="Optional output filename tag.")
    parser.add_argument(
        "--persistence-days",
        type=int,
        default=5,
        help="Minimum number of daily observations required before switching to a new regime label.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    csv_path = Path(args.csv).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    date_tag = utc_now_datestr()
    name_tag = f"_{args.tag}" if args.tag else ""

    df_1m = load_market_data(csv_path)
    daily = resample_daily(df_1m)
    features = build_features(daily)

    thresholds = Thresholds()
    classified = classify_features(features, thresholds)
    classified["regime_label"] = smooth_labels(classified["regime_label_raw"], args.persistence_days)

    label_col = "regime_label"

    export_df = classified.reset_index()
    segments_df = build_segments(classified.dropna(subset=[label_col]), label_col=label_col)
    summary_df = summarize_labels(classified.dropna(subset=[label_col]), label_col=label_col)
    latest_snapshot = latest_phase_snapshot(classified.dropna(subset=[label_col]), label_col=label_col)

    features_out = outdir / f"btc_regime_daily_features{name_tag}_{date_tag}.csv"
    segments_out = outdir / f"btc_regime_segments{name_tag}_{date_tag}.csv"
    summary_out = outdir / f"btc_regime_summary{name_tag}_{date_tag}.csv"
    latest_out = outdir / f"btc_regime_latest{name_tag}_{date_tag}.json"
    report_out = outdir / f"btc_regime_report{name_tag}_{date_tag}.md"

    export_df.to_csv(features_out, index=False)
    segments_df.to_csv(segments_out, index=False)
    summary_df.to_csv(summary_out, index=False)

    latest_payload = {
        "source_csv": str(csv_path),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "label_column": label_col,
        "persistence_days": args.persistence_days,
        "latest_phase": latest_snapshot,
        "thresholds": thresholds.__dict__,
    }
    latest_out.write_text(json.dumps(latest_payload, indent=2), encoding="utf-8")

    save_markdown_report(
        out_path=report_out,
        csv_path=csv_path,
        daily_df=daily,
        summary_df=summary_df,
        segments_df=segments_df,
        latest_snapshot=latest_snapshot,
        label_col=label_col,
        persistence_days=args.persistence_days,
    )

    print(f"[OK] features: {features_out}")
    print(f"[OK] segments: {segments_out}")
    print(f"[OK] summary:  {summary_out}")
    print(f"[OK] latest:   {latest_out}")
    print(f"[OK] report:   {report_out}")


if __name__ == "__main__":
    main()