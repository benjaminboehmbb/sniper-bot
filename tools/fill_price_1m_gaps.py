#!/usr/bin/env python3
# tools/fill_price_1m_gaps.py
"""
Fill 1m gaps in a BTCUSDT CSV.

Usage:
  # conservative: insert NaN rows for missing minutes (safe, fast)
  python tools/fill_price_1m_gaps.py --in data/btcusdt_1m_spot.csv --method pad

  # try to fetch missing klines from Binance REST and insert them
  python tools/fill_price_1m_gaps.py --in data/btcusdt_1m_spot.csv --method fetch

Outputs:
  - data/btcusdt_1m_spot_filled.csv     (repaired copy)
  - data/btcusdt_1m_spot_backup_<ts>.csv (original backup)
  - data/fill_report.json               (summary)
  - if fetch used: new chunk files written to data/raw/ and merged
"""
import os, sys, json, time, argparse
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import requests

SPOT_ENDPOINT = "https://api.binance.com/api/v3/klines"

def ts_ms_to_iso(ms):
    return datetime.utcfromtimestamp(int(ms)//1000).replace(tzinfo=timezone.utc).isoformat().replace("+00:00","Z")

def backup_file(path):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(path)
    out = os.path.join("data", f"{base.replace('.csv','')}_backup_{ts}.csv")
    os.makedirs("data", exist_ok=True)
    pd.read_csv(path).to_csv(out, index=False)
    return out

def find_gaps(ts_seconds):
    diffs = ts_seconds[1:] - ts_seconds[:-1]
    idx = np.where(diffs != 60)[0]
    gaps = []
    for i in idx:
        prev_s = int(ts_seconds[i])
        curr_s = int(ts_seconds[i+1])
        gap_min = int((curr_s - prev_s)//60)
        gaps.append((prev_s, curr_s, gap_min))
    return gaps

def pad_gaps(df, out_path):
    # assume df sorted by open_time asc
    first = int(df["open_time"].iloc[0])
    last  = int(df["open_time"].iloc[-1])
    full_ms = np.arange(first, last+1, 60000, dtype=np.int64)
    exist = df["open_time"].astype(np.int64).values
    missing_ms = np.setdiff1d(full_ms, exist)
    print(f"Missing rows to add: {len(missing_ms)}")
    if len(missing_ms)==0:
        df.to_csv(out_path, index=False)
        return {"added":0}
    # build empty frame with same columns
    cols = df.columns.tolist()
    empty = {c: [pd.NA]*len(missing_ms) for c in cols}
    empty["open_time"] = missing_ms
    empty["open_time_iso"] = [ts_ms_to_iso(m) for m in missing_ms]
    miss_df = pd.DataFrame(empty)[cols]
    # concat, sort, dedupe just in case
    big = pd.concat([df, miss_df], ignore_index=True).drop_duplicates(subset=["open_time"], keep="first")
    big = big.sort_values("open_time").reset_index(drop=True)
    big.to_csv(out_path, index=False)
    return {"added": int(len(missing_ms))}

def fetch_klines_for_range(session, symbol, start_ms, end_ms, sleep_sec=0.6, max_retries=8):
    results = []
    limit = 1000
    cur = start_ms
    while cur < end_ms:
        this_end = min(cur + (limit*60000) - 1, end_ms)
        params = {"symbol": symbol, "interval": "1m", "startTime": int(cur), "endTime": int(this_end), "limit": limit}
        for attempt in range(1, max_retries+1):
            try:
                r = session.get(SPOT_ENDPOINT, params=params, timeout=30)
                if r.status_code == 429:
                    time.sleep(sleep_sec * attempt); continue
                r.raise_for_status()
                data = r.json()
                if not data:
                    # nothing returned -> break to avoid infinite loop
                    cur = this_end + 60000
                    break
                results.extend(data)
                last_open = int(data[-1][0])
                # next minute after last returned
                cur = (last_open // 1000 + 1) * 1000
                time.sleep(sleep_sec)
                break
            except Exception as e:
                if attempt >= max_retries:
                    print("Fetch failed for range", cur, this_end, "err:", e)
                    cur = this_end + 60000
                    break
                time.sleep(sleep_sec * attempt)
    return results

def klines_to_df(klines):
    cols = [
        "open_time","open","high","low","close","volume",
        "close_time","quote_asset_volume","number_of_trades",
        "taker_buy_base_asset_volume","taker_buy_quote_asset_volume","ignore"
    ]
    df = pd.DataFrame(klines, columns=cols)
    for c in ["open","high","low","close","volume","quote_asset_volume",
              "taker_buy_base_asset_volume","taker_buy_quote_asset_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["open_time","close_time","number_of_trades"]:
        df[c] = pd.to_numeric(df[c], errors="coerce", downcast="integer")
    df["open_time_iso"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df = df.drop(columns=["ignore"])
    final_cols = [
        "open_time","open_time_iso","open","high","low","close","volume",
        "close_time","quote_asset_volume","number_of_trades",
        "taker_buy_base_asset_volume","taker_buy_quote_asset_volume"
    ]
    return df[final_cols]

def fetch_and_insert(df, gaps, symbol):
    session = requests.Session()
    fetched_rows = 0
    new_frames = []
    for prev_s, curr_s, gap_min in gaps:
        start_ms = (prev_s + 60) * 1000
        end_ms   = curr_s * 1000
        print(f"[FETCH] gap {gap_min}min -> {datetime.utcfromtimestamp(prev_s).isoformat()} .. {datetime.utcfromtimestamp(curr_s).isoformat()}")
        kl = fetch_klines_for_range(session, symbol, start_ms, end_ms)
        if kl:
            kdf = klines_to_df(kl)
            new_frames.append(kdf)
            fetched_rows += len(kdf)
        else:
            print("  -> no data returned for that gap (will remain)")
    if new_frames:
        insert_df = pd.concat(new_frames, ignore_index=True)
        big = pd.concat([df, insert_df], ignore_index=True).drop_duplicates(subset=["open_time"], keep="first")
        big = big.sort_values("open_time").reset_index(drop=True)
        return big, fetched_rows
    return df, 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--method", choices=["pad","fetch"], default="pad")
    args = ap.parse_args()

    infile = args.infile
    if not os.path.exists(infile):
        print("Input not found:", infile); sys.exit(2)

    backup = backup_file(infile)
    print("Backup written to", backup)

    df = pd.read_csv(infile)
    df = df.sort_values("open_time").reset_index(drop=True)
    ts = df["open_time"].astype("int64").values // 1000
    gaps = find_gaps(ts)
    report = {
        "infile": infile,
        "rows_before": int(len(df)),
        "num_gaps": len(gaps),
        "largest_gap_min": int(max([g[2] for g in gaps]) if gaps else 0),
        "method": args.method,
        "added_rows": 0,
        "fetched_rows": 0
    }

    out_path = os.path.join("data", os.path.basename(infile).replace(".csv","_filled.csv"))

    if args.method == "pad":
        res = pad_gaps(df, out_path)
        report["added_rows"] = int(res.get("added",0))
    else:
        # try to fetch and insert
        if not gaps:
            df.to_csv(out_path, index=False)
        else:
            big, fetched = fetch_and_insert(df, gaps, symbol="BTCUSDT")
            report["fetched_rows"] = int(fetched)
            report["rows_after_fetch"] = int(len(big))
            big.to_csv(out_path, index=False)

    # write report
    with open("data/fill_report.json","w",encoding="utf-8") as f:
        json.dump(report,f,indent=2,ensure_ascii=False)

    print("Done. Report: data/fill_report.json")
    print(report)

if __name__ == "__main__":
    main()
