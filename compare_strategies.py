from pricefeed import CSVPriceFeed
from sim_trader import SimTrader
from strategies.combined_strategy import CombinedStrategy

from strategies.filters.rsi_filter import RSIFilter
from strategies.filters.ma200_filter import MA200Filter
from strategies.filters.bollinger_filter import BollingerFilter
from strategies.filters.macd_filter import MACDFilter

import pandas as pd


def run_backtest(filter_combo, combo_name):
    feed = CSVPriceFeed("data/BTCUSDT_5min_clean.csv", datetime_col='timestamp', time_format='ms')
    strategy = CombinedStrategy(filters=filter_combo)
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
        'Name': combo_name,
        'Trades': num_trades,
        'Winrate (%)': round(winrate, 2),
        'Total PnL (USDT)': round(total_pnl, 2),
        'Avg PnL per Trade': round(avg_pnl, 2),
        'Final Balance': round(final_balance, 2)
    }


def main():
    results = []

    rsi_thresholds = [25, 30, 35, 40]
    use_ma200_options = [False, True]
    use_bb_options = [False, True]
    use_macd_options = [False, True]

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
                    print(f"Teste Kombination: {combo_name}")
                    result = run_backtest(filters, combo_name)
                    results.append(result)

    # ✅ Speicherung der Ergebnisse für analyse_results.py
    df = pd.DataFrame(results)
    df.to_csv("strategy_results.csv", index=False)

    # ✅ Textausgabe zur Kontrolle
    print("\nVergleich der Strategien:")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
