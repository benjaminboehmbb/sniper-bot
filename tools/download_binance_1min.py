#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Binance 1m Downloader (Spot/Futures) mit Resume, Rate-Limit, Merge.
OUTPUT:
  - data/raw/*.csv  (Chunk-Dateien)
  - data/btcusdt_1m_spot.csv (zusammengeführt, duplikatfrei, sortiert)
"""

import os, sys, time, argparse
from datetime import datetime, timezone, timedelta
from dateutil import parser as dtparser
import pandas as pd
import requests

SPOT_ENDPOINT = "https://api.binance.com/api/v3/klines"
FUTU_ENDPOINT = "https://fapi.binance.com/fapi/v1/klines"

def to_ms(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)

def parse_date(s: str) -> datetime:
    if s.lower() == "today":
        return datetime.utcnow().replace(tzinfo=timezone.utc).replace(microsecond=0)
    return dtparser.parse(s).astimezone(timezone.utc)

def ensure_dirs():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("config", exist_ok=True)

def pick_endpoint(market: str) -> str:
    m = market.lower()
    if m == "spot":
        return SPOT_ENDPOINT
    if m in ("futures","usdt_perp","perp"):
        return FUTU_ENDPOINT
    raise ValueError("market must be 'spot' or 'futures'")

def fetch_klines(session, endpoint, symbol, start_ms, end_ms, limit=1000, sleep_sec=0.6, max_retries=8):
    params = dict(symbol=symbol, interval="1m", startTime=start_ms, endTime=end_ms, limit=limit)
    for attempt in range(1, max_retries+1):
        try:
            r = session.get(endpoint, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(sleep_sec * attempt); continue
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt >= max_retries: raise
            time.sleep(sleep_sec * attempt)
    return []

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

def existing_chunks(prefix):
    return sorted([os.path.join("data","raw",f) for f in os.listdir("data/raw")
                   if f.startswith(prefix) and f.endswith(".csv")])

def infer_resume_start_from_chunks(prefix):
    files = existing_chunks(prefix)
    if not files: return None
    try:
        tail = pd.read_csv(files[-1]).tail(1)
        if len(tail):
            last_open_ms = int(tail["open_time"].iloc[0])
            return datetime.utcfromtimestamp((last_open_ms//1000)+60).replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None

def merge_all(prefix, out_path):
    files = existing_chunks(prefix)
    if not files:
        print("WARN: keine Chunks vorhanden zum Mergen."); return
    dfs = []
    for f in files:
        try: dfs.append(pd.read_csv(f))
        except Exception as e: print(f"WARN: Problem beim Lesen {f}: {e}")
    if not dfs: 
        print("WARN: keine lesbaren Chunks."); return
    big = pd.concat(dfs, ignore_index=True)
    big = big.drop_duplicates(subset=["open_time"]).sort_values("open_time").reset_index(drop=True)
    big.to_csv(out_path, index=False)
    print(f"[OK] Zusammengeführt: {out_path} | Rows={len(big):,}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--market", default="spot", choices=["spot","futures"])
    ap.add_argument("--start", required=True, help="z.B. 2017-08-17 oder today")
    ap.add_argument("--end", default="today")
    ap.add_argument("--out", default=None)
    ap.add_argument("--chunk-mins", type=int, default=1000)  # max 1000 pro Request
    ap.add_argument("--sleep-sec", type=float, default=0.6)
    ap.add_argument("--max-retries", type=int, default=8)
    args = ap.parse_args()

    ensure_dirs()
    endpoint = pick_endpoint(args.market)
    start_dt = parse_date(args.start)
    end_dt   = parse_date(args.end)
    if end_dt <= start_dt:
        print("ERROR: end <= start"); sys.exit(2)

    out_path = args.out or os.path.join("data", f"{args.symbol.lower()}_1m_{args.market.lower()}.csv")
    prefix = f"{args.symbol.lower()}_{args.market.lower()}_1m_"

    resume_dt = infer_resume_start_from_chunks(prefix)
    if resume_dt and resume_dt > start_dt:
        print(f"[RESUME] Start verschoben auf {resume_dt.isoformat()} (basierend auf vorhandenen Chunks)")
        start_dt = resume_dt

    session = requests.Session()
    LIMIT = min(1000, args.chunk_mins)
    cur = start_dt
    total_rows = 0
    req = 0
    print(f"== Download {args.symbol} 1m ({args.market}) von {start_dt} bis {end_dt} ==")
    while cur < end_dt:
        chunk_end = min(cur + timedelta(minutes=LIMIT), end_dt)
        start_ms, end_ms = to_ms(cur), to_ms(chunk_end) - 1
        try:
            kl = fetch_klines(session, endpoint, args.symbol.upper(), start_ms, end_ms,
                              limit=1000, sleep_sec=args.sleep_sec, max_retries=args.max_retries)
            if not kl:
                cur = cur + timedelta(minutes=LIMIT); time.sleep(args.sleep_sec); continue
            df = klines_to_df(kl)
        except Exception as e:
            print(f"WARN: Fetch-Fehler {e}; skip {cur}..{chunk_end}")
            cur = cur + timedelta(minutes=LIMIT); time.sleep(args.sleep_sec*2); continue

        if df.empty:
            cur = cur + timedelta(minutes=LIMIT); time.sleep(args.sleep_sec); continue

        first_ts = int(df["open_time"].iloc[0]); last_ts = int(df["open_time"].iloc[-1])
        fpath = os.path.join("data","raw", f"{prefix}{first_ts}_{last_ts}.csv")
        df.to_csv(fpath, index=False)
        total_rows += len(df); req += 1
        pct = ((cur - start_dt).total_seconds() / (end_dt - start_dt).total_seconds())*100
        print(f"[{req}] {cur}..{chunk_end} | +{len(df)} rows | total={total_rows:,} | {pct:5.2f}%")
        # nächster Start = letzte Kline + 60s
        cur = datetime.utcfromtimestamp((last_ts//1000)+60).replace(tzinfo=timezone.utc)
        time.sleep(args.sleep_sec)

    merge_all(prefix, out_path)
    print("[DONE]")

if __name__ == "__main__":
    main()
