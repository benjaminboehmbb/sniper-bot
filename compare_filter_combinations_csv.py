import pandas as pd
from filters import apply_filters
from indicators import calculate_indicators
from simtrader_csv_core import SimTrader
import os

CSV_PATH = "C:/btc_data/merged/price_data.csv"
INITIAL_BALANCE = 10000
RESULT_PATH = "results/combination_results.csv"

FILTER_COMBINATIONS = [
    ["RSI"],
    ["MACD"],
    ["MA200"],
    ["RSI", "MA200"],
    ["RSI", "Bollinger"],
    ["MACD", "MA200"],
    ["RSI", "MACD"],
    ["RSI", "MACD", "MA200", "Bollinger"]
]

def evaluate_combination(df, combination):
    filtered_df = apply_filters(df.copy(), combination)
    trader = SimTrader(filtered_df, filters=combination)
    trader.run()
    trades = trader.get_trade_history()
    final_balance = trader.balance
    roi = (final_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100
    win_trades = [t for t in trades if t["profit"] > 0]
    winrate = len(win_trades) / len(trades) * 100 if trades else 0
    return {
        "Kombination": " + ".join(combination),
        "Anzahl Trades": len(trades),
        "Trefferquote (%)": round(winrate, 2),
        "ROI (%)": round(roi, 2),
        "Endkapital ($)": round(final_balance, 2)
    }


def main():
    print(f"📅 Lade Kursdaten aus: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = calculate_indicators(df)

    results = []
    for combo in FILTER_COMBINATIONS:
        print(f"\n🔎 Teste Kombination: {' + '.join(combo)}")
        result = evaluate_combination(df, combo)
        results.append(result)

    results_df = pd.DataFrame(results)
    print("\n📊 Statistische Auswertung der Kombinationen:")
    print(results_df)
    os.makedirs("results", exist_ok=True)
    results_df.to_csv(RESULT_PATH, index=False)
    print(f"\n💾 Ergebnisse gespeichert unter {RESULT_PATH}")

if __name__ == "__main__":
    main()
