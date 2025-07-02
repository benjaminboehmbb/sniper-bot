import pandas as pd
import matplotlib.pyplot as plt
from strategies.filters import RSIFilter, MA200Filter, BollingerFilter, MACDFilter
from sim_trader import SimTrader
from pricefeed import CSVPriceFeed
from itertools import combinations

# Konfiguration
data_folder = "data"
initial_capital = 10000
fee = 0.001
slippage = 0.0005

# Verfügbare Filter
filter_classes = {
    "RSI": RSIFilter,
    "MA200": MA200Filter,
    "BOLL": BollingerFilter,
    "MACD": MACDFilter,
}

results = []

# Teste alle möglichen Filterkombinationen
for r in range(1, len(filter_classes) + 1):
    for combo in combinations(filter_classes.keys(), r):
        feed = CSVPriceFeed(data_folder)
        feed.load_data()
        df = feed.data.copy()

        # Filter nacheinander anwenden
        valid_indices = pd.Series([True] * len(df))
        for name in combo:
            f = filter_classes[name](df)
            valid_indices &= f.get_signal()

        df = df[valid_indices].copy()

        # Backtest starten
        trader = SimTrader(initial_balance=initial_capital, fee=fee, slippage=slippage)
        for i in range(1, len(df)):
            prev_close = df.iloc[i - 1]['close']
            curr_close = df.iloc[i]['close']
            if curr_close > prev_close:
                trader.buy(df.iloc[i])
            elif curr_close < prev_close:
                trader.sell(df.iloc[i])

        roi = (trader.balance - initial_capital) / initial_capital * 100
        results.append({
            "Filter-Kombination": " + ".join(combo),
            "Anzahl Trades": trader.num_trades,
            "ROI Gesamt (%)": round(roi, 2),
            "Endkapital ($)": round(trader.balance, 2),
        })

# Ergebnisse anzeigen und speichern
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="ROI Gesamt (%)", ascending=False)
results_df.to_csv("strategy_results.csv", index=False)
print(results_df)

# Ergebnisse visualisieren
plt.figure(figsize=(12, 7))
plt.barh(results_df["Filter-Kombination"], results_df["ROI Gesamt (%)"])
plt.xlabel("ROI (%)")
plt.title("Strategie-ROI je Filterkombination")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()



