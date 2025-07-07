import pandas as pd
from simtrader_csv_core import SimTrader

def create_test_data():
    # Beispiel-Daten: Zeitreihe mit Preisen und kombiniertem Signal (0..1)
    data = {
        "open_time": pd.date_range(start="2025-01-01 00:00", periods=20, freq="5min"),
        "close": [
            100, 102, 101, 103, 105,
            106, 104, 102, 101, 100,
            99,  98,  97,  96,  95,
            96,  97,  98,  99, 100,
        ],
        # kombiniertes Signal: Werte zwischen 0 und 1
        "combined_signal": [
            0.1, 0.2, 0.4, 0.5, 0.7,
            0.8, 0.9, 0.8, 0.6, 0.4,
            0.2, 0.1, 0.3, 0.5, 0.7,
            0.9, 0.8, 0.7, 0.5, 0.3,
        ],
    }
    return pd.DataFrame(data)

def main():
    df = create_test_data()
    trader = SimTrader(df, initial_balance=10000)
    # Run mit entry threshold 0.7, exit threshold 0.3
    trader.run(signal_column="combined_signal", threshold_entry=0.7, threshold_exit=0.3)
    
    print(f"Endkapital: ${trader.get_balance():.2f}")
    trades = trader.get_trade_history()
    print(trades)
    trader.export_results("results/test_trades.csv")
    print("Trades exportiert nach results/test_trades.csv")

if __name__ == "__main__":
    main()
