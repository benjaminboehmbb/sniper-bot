
import ast, os, numpy as np, pandas as pd
# Settings (bewährt):
THR=0.60; COOLDOWN=0; REQUIRE_MA200=True
MIN_TR=50; MAX_TR=50000; TAKE=200
price="data/price_data_with_signals.csv"
strat="data/strategies_k3_shard1.csv"
outdir="results/3er"; os.makedirs(outdir, exist_ok=True)

df=pd.read_csv(price, index_col=0); df.index=pd.to_datetime(df.index,errors="coerce"); df=df[df.index.notna()]
close=df.get("close", pd.Series(index=df.index, dtype=float)).to_numpy(dtype=float)
dates=df.index
# Gate
if REQUIRE_MA200 and "ma200_signal" in df.columns:
    gate=df["ma200_signal"].astype(int).to_numpy()
elif REQUIRE_MA200 and ("close" in df.columns and "ma200" in df.columns):
    gate=(df["close"].to_numpy(float)>df["ma200"].to_numpy(float)).astype(int)
else:
    gate=np.ones(len(df),int)

def rmm(a):
    a=a.astype(float); med=np.nanmedian(a); a=np.where(np.isnan(a),med,a)
    q1,q99=np.percentile(a,1),np.percentile(a,99)
    lo,hi=(q1,q99) if np.isfinite(q1) and np.isfinite(q99) and q99>q1 else (np.nanmin(a),np.nanmax(a))
    if not(np.isfinite(lo) and np.isfinite(hi) and hi>lo): return np.zeros_like(a)
    a=np.clip(a,lo,hi); return (a-lo)/(hi-lo)

# Pre-normalize all *_signal columns once
sig_cols=[c for c in df.columns if c.endswith("_signal")]
norm={c:rmm(df[c].to_numpy()) for c in sig_cols}

def map_keys(d):
    # Map basisnamen -> *_signal, lässt *_signal unverändert
    m={}
    for k,v in d.items():
        kk = k if k.endswith("_signal") else f"{k}_signal"
        m[kk]=float(v)
    return m

def simulate(combo):
    avail=[k for k in combo if k in norm]
    if not avail: return 0,0.0,0.0,0.0
    sw=sum(abs(combo[k]) for k in avail) or 1.0
    w={k:combo[k]/sw for k in avail}
    s=np.zeros(len(df),float)
    for k in avail: s += w[k]*norm[k]
    inpos=False; entry=None; last=None; trades=[]; n=len(s)
    for i in range(n-1):
        if inpos:
            hold=(dates[i]-dates[entry]).total_seconds()/60.0
            if s[i]<THR or hold>=240:
                e=entry; x=i+1 if i+1<n else i
                ep=close[e+1] if e+1<n else close[e]; xp=close[x]
                pnl=(xp/ep)-1.0 if np.isfinite(ep) and ep!=0 else 0.0
                trades.append(pnl); inpos=False; entry=None; last=dates[x]; continue
        else:
            if last is not None and (dates[i]-last).total_seconds()/60.0<COOLDOWN: continue
            if s[i]>THR and gate[i]==1:
                inpos=True; entry=i
    if inpos and entry is not None:
        e=entry; x=n-1; ep=close[e+1] if e+1<n else close[e]; xp=close[x]
        trades.append((xp/ep)-1.0 if np.isfinite(ep) and ep!=0 else 0.0)
    num=len(trades); total=float(np.sum(trades)) if num else 0.0
    avg=float(total/num) if num else 0.0; win=float(np.mean(np.array(trades)>0)) if num else 0.0
    return num,total,avg,win

sdf=pd.read_csv(strat).head(TAKE)
rows=[]; kept=0
for cs in sdf["Combination"].tolist():
    try:
        d=ast.literal_eval(cs); 
        if not isinstance(d,dict): continue
    except Exception:
        continue
    combo=map_keys(d)
    n,t,a,w=simulate(combo)
    if MIN_TR<=n<=MAX_TR:
        rows.append({"Combination": str(combo), "num_trades":n, "total_pnl":t, "avg_pnl":a, "winrate":w})
        kept+=1

import datetime as dt
ts=dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
out=os.path.join(outdir, f"strategy_results_long_fastmapped_{ts}.csv")
if rows:
    pd.DataFrame(rows).to_csv(out, index=False)
    print("saved:", out, "rows:", len(rows))
else:
    print("no strategies in band after mapping")
print("checked:", len(sdf), "kept:", kept)
