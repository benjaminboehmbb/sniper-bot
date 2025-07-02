import pandas as pd
import os
from indicators import calculate_indicators
from filters import apply_filters
from simtrader_csv import SimTrader

# CSV-Datei mit Kursdaten
CSV_PATH = "C:/btc_data/merged/price_data.csv"

# Ergebnisordner
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Strategien definieren (mehr kannst du später hinzufügen)
strategies = {
    "RSI<30": [{"type": "rsi", "params": {"period": 14, "threshold": 30}}],
    "MACD_Bullish": [{"type": "macd", "params": {"signal": "bullish"}}],
    "MA200_Filter": [{"type": "ma200", "params": {}}],
    "Bollinger_Breakout": [{"type": "bollinger", "params": {"mult": 2}}],
}

# Daten einlesen
print(f"📥 Lade Kursdaten aus: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)

# Stelle sicher, dass timestamp korrekt formatiert ist
if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="raise")
    except Exception:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

df = df.dropna(subset=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Indikatoren berechnen
df = calculate_indicators(df)

results = []

for name, strategy_filters in strategies.items():
    print(f"\n🔎 Teste Strategie: {name}")
    df_strategy = df.copy()
    df_strategy = apply_filters(df_strategy, strategy_filters)

    trader = SimTrader(df_strategy)
    trader.run()
    trades = trader.trades

    if not trades:
        print("⚠️  Keine Trades generiert.")
        continue

    # ROI und Trefferquote berechnen
    start_balance = 10000
    end_balance = trader.balance
    roi = (end_balance - start_balance) / start_balance * 100
    winning_trades = [t for t in trades if t.get("profit", 0) > 0]
    hit_rate = len(winning_trades) / len(trades) * 100 if trades else 0

    results.append({
        "Strategie": name,
        "Anzahl Trades": len(trades),
        "Trefferquote (%)": round(hit_rate, 2),
        "ROI (%)": round(roi, 2),
        "Endkapital ($)": round(end_balance, 2)
    })

# Ergebnisse als DataFrame anzeigen und speichern
df_results = pd.DataFrame(results)
print("\n📊 Statistische Auswertung der Strategien:")
print(df_results)

df_results.to_csv(os.path.join(RESULTS_DIR, "strategy_results.csv"), index=False)
print(f"\n💾 Ergebnisse gespeichert unter {RESULTS_DIR}/strategy_results.csv")

