import pandas as pd
import os
from datetime import datetime

from pricefeed import CSVPriceFeed
from sim_trader import SimTrader
from strategies.combined_strategy import CombinedStrategy
from strategies.filters.rsi_filter import RSIFilter
from strategies.filters.ma200_filter import MA200Filter
from strategies.filters.bollinger_filter import BollingerFilter
from strategies.filters.macd_filter import MACDFilter

def run_backtest_on_df(df, filters):
    feed = CSVPriceFeed(df=df)  # angepasste Variante, akzeptiert DataFrame direkt
    strategy = CombinedStrategy(filters=filters)
    trader = SimTrader(price_feed=feed, strategy=strategy, starting_balance=10000)
    trader.run()

    trades = trader.get_trades()
    final_balance = trader.get_balance()
    total_pnl = final_balance - 10000
    num_trades = len(trades)
    avg_pnl = total_pnl / num_trades if num_trades > 0 else 0
    wins = [t for t in trades if t['pnl'] > 0]
    winrate = len(wins) / num_trades * 100 if num_trades > 0 else 0

    return {
        'Trades': num_trades,
        'Winrate (%)': round(winrate, 2),
        'Total PnL': round(total_pnl, 2),
        'Avg PnL': round(avg_pnl, 2),
        'Final Balance': round(final_balance, 2)
    }

def load_month_data(folder, pattern, year, month):
    files = sorted([
        f for f in os.listdir(folder)
        if f.startswith(pattern) and f.endswith(".csv")
    ])
    month_str = f"{year}-{month:02d}"
    matching = [os.path.join(folder, f) for f in files if month_str in f]
    if not matching:
        return None
    df = pd.concat([pd.read_csv(f, header=None) for f in matching])
    df.columns = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].sort_values(by='timestamp')

def main():
    folder = "data"
    pattern = "BTCUSDT-5m"
    months = [(2023, m) for m in range(1, 6)]  # Januar bis Mai
    rsi_thresholds = [25, 30, 35]
    use_ma200_options = [False, True]
    use_bb_options = [False, True]
    use_macd_options = [False, True]

    results = []

    for rsi_thresh in rsi_thresholds:
        for use_ma200 in use_ma200_options:
            for use_bb in use_bb_options:
                for use_macd in use_macd_options:

                    filters = [RSIFilter(threshold=rsi_thresh)]
                    name_parts = [f"RSI<{rsi_thresh}"]

                    if use_ma200:
                        filters.append(MA200Filter())
                        name_parts.append("MA200")
                    if use_bb:
                        filters.append(BollingerFilter())
                        name_parts.append("BB")
                    if use_macd:
                        filters.append(MACDFilter())
                        name_parts.append("MACD")

                    combo_name = " + ".join(name_parts)

                    for year, month in months:
                        df = load_month_data(folder, pattern, year, month)
                        if df is None:
                            print(f"⚠️ Keine Daten für {year}-{month:02d}")
                            continue

                        result = run_backtest_on_df(df, filters)
                        result.update({
                            'Strategy': combo_name,
                            'Year': year,
                            'Month': month
                        })
                        print(f"{combo_name} auf {year}-{month:02d}: {result['Total PnL']} USDT mit {result['Trades']} Trades")
                        results.append(result)

    df_results = pd.DataFrame(results)
    df_pivot = df_results.pivot_table(
        index=['Strategy'],
        columns=['Year', 'Month'],
        values='Total PnL',
        fill_value=0
    )

    print("\n📊 Gesamtvergleich (Total PnL pro Monat):")
    print(df_pivot.to_string())

    # Optional: speichern
    df_pivot.to_csv("strategy_monthly_comparison.csv")

if __name__ == "__main__":
    main()
