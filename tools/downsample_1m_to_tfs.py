#!/usr/bin/env python3
# tools/downsample_1m_to_tfs.py
"""
Downsample 1m BTCUSDT CSV to multiple target timeframes.

Usage examples:
  python tools/downsample_1m_to_tfs.py --in data/btcusdt_1m_spot_filled.csv --tfs 5T,15T,1H
  python tools/downsample_1m_to_tfs.py --in data/btcusdt_1m_spot_filled.csv --tfs 5T --drop-incomplete

Outputs:
  - data/btcusdt_5T_spot.csv, data/btcusdt_15T_spot.csv, data/btcusdt_1H_spot.csv (depending on args)
  - data/downsample_report.json (summary)
Notes:
  - Default behavior: keep all target candles and add column "complete" (True if no NaNs in price fields).
  - If --drop-incomplete is set, incomplete target candles are removed in output.
"""
import os, sys, json, argparse
from datetime import datetime, timezone
import pandas as pd
import numpy as np

AGG_COLS = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum",
    "quote_asset_volume": "sum",
    "number_of_trades": "sum",
    "taker_buy_base_asset_volume": "sum",
    "taker_buy_quote_asset_volume": "sum"
}

def tf_label_to_suffix(tf):
    # e.g. '5T' -> '5m', '1H' -> '1h'
    if tf.endswith('T'):
        return f"{int(tf[:-1])}m"
    if tf.endswith('H'):
        return f"{int(tf[:-1])}h"
    return tf

def ensure_out_dir():
    os.makedirs("data", exist_ok=True)

def load_df(path):
    df = pd.read_csv(path)
    # ensure open_time integer ms
    df['open_time'] = df['open_time'].astype('int64')
    # create datetime index in UTC
    df['_dt'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    df = df.set_index('_dt', drop=False)
    return df

def aggregate_to_tf(df, tf, drop_incomplete=False):
    # expected minutes per candle
    if tf.endswith('T'):
        minutes = int(tf[:-1])
    elif tf.endswith('H'):
        minutes = int(tf[:-1]) * 60
    else:
        raise ValueError("Unsupported tf format. Use e.g. 5T, 15T, 1H")

    # resample groups (label left, closed left)
    grp = df.resample(tf, label='left', closed='left')

    # custom aggregations: we need first valid open, last valid close
    def agg_group(g):
        if len(g) == 0:
            return pd.Series({
                'open_time': pd.NA, 'open_time_iso': pd.NA,
                'open': pd.NA, 'high': pd.NA, 'low': pd.NA, 'close': pd.NA,
                'volume': 0.0, 'quote_asset_volume': 0.0,
                'number_of_trades': 0, 'taker_buy_base_asset_volume': 0.0,
                'taker_buy_quote_asset_volume': 0.0,
                'complete': False
            })
        # first and last valid
        open_val = g['open'].dropna()
        close_val = g['close'].dropna()
        open_v = open_val.iloc[0] if len(open_val) else np.nan
        close_v = close_val.iloc[-1] if len(close_val) else np.nan
        high_v = g['high'].dropna().max() if len(g['high'].dropna()) else np.nan
        low_v = g['low'].dropna().min() if len(g['low'].dropna()) else np.nan
        volume_sum = float(g['volume'].fillna(0).sum())
        quote_sum = float(g['quote_asset_volume'].fillna(0).sum())
        trades_sum = int(g['number_of_trades'].fillna(0).sum())
        taker_base = float(g['taker_buy_base_asset_volume'].fillna(0).sum())
        taker_quote = float(g['taker_buy_quote_asset_volume'].fillna(0).sum())
        # open_time: first row's open_time (ms) if present else left bin * 1000
        first_open_time = int(g['open_time'].iloc[0]) if 'open_time' in g.columns and not pd.isna(g['open_time'].iloc[0]) else int(g.index[0].timestamp()*1000)
        iso = pd.to_datetime(first_open_time, unit='ms', utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")
        # completeness: require number of rows == expected minutes AND no NaNs in open/high/low/close across the group
        rows_present = len(g)
        non_nan_prices = g[['open','high','low','close']].notna().all(axis=1).sum()
        complete = (rows_present >= minutes) and (non_nan_prices == minutes)
        return pd.Series({
            'open_time': int(first_open_time),
            'open_time_iso': iso,
            'open': float(open_v) if pd.notna(open_v) else pd.NA,
            'high': float(high_v) if pd.notna(high_v) else pd.NA,
            'low': float(low_v) if pd.notna(low_v) else pd.NA,
            'close': float(close_v) if pd.notna(close_v) else pd.NA,
            'volume': volume_sum,
            'quote_asset_volume': quote_sum,
            'number_of_trades': trades_sum,
            'taker_buy_base_asset_volume': taker_base,
            'taker_buy_quote_asset_volume': taker_quote,
            'complete': bool(complete)
        })

    out = grp.apply(agg_group)
    # drop bins that are entirely after last timestamp (may occur)
    out = out.dropna(subset=['open_time'])
    out = out.reset_index(drop=True)
    if drop_incomplete:
        out = out[out['complete']==True].reset_index(drop=True)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True, help="input 1m CSV (filled)")
    ap.add_argument("--tfs", default="5T,15T,1H", help="comma separated target TFs (pandas offset aliases, e.g. 5T,15T,1H)")
    ap.add_argument("--drop-incomplete", action="store_true", help="drop incomplete target candles")
    args = ap.parse_args()

    infile = args.infile
    tfs = [t.strip() for t in args.tfs.split(",") if t.strip()]
    drop_incomplete = bool(args.drop_incomplete)

    ensure_out_dir()
    df = load_df(infile)
    report = {"infile": infile, "rows_1m": int(len(df)), "outputs": []}

    for tf in tfs:
        print(f"[INFO] Aggregating to {tf} ...")
        out_df = aggregate_to_tf(df, tf, drop_incomplete=drop_incomplete)
        suffix = tf_label_to_suffix(tf)
        out_name = f"data/btcusdt_{suffix}_spot.csv"
        # ensure columns order similar to 1m
        cols = ['open_time','open_time_iso','open','high','low','close','volume',
                'quote_asset_volume','number_of_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume','complete']
        out_df = out_df[cols]
        out_df.to_csv(out_name, index=False)
        num_out = len(out_df)
        num_complete = int(out_df['complete'].sum())
        report["outputs"].append({
            "tf": tf,
            "out_file": out_name,
            "rows": int(num_out),
            "complete_rows": int(num_complete),
            "incomplete_rows": int(num_out - num_complete)
        })
        print(f" -> wrote {out_name} | rows={num_out} complete={num_complete}")

    # write report
    report_path = "data/downsample_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("[DONE] report ->", report_path)

if __name__ == "__main__":
    main()
