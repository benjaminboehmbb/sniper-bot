import pandas as pd
import matplotlib.pyplot as plt

def load_trade_history(path='results/trade_history.csv'):
    print(f"Lade Trade-Historie aus: {path}")
    df = pd.read_csv(path, parse_dates=['entry_time', 'exit_time'])
    return df

def analyze_trades(df):
    total_trades = len(df)
    winning_trades = df[df['profit'] > 0]
    losing_trades = df[df['profit'] <= 0]
    
    win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
    avg_profit = df['profit'].mean() if total_trades > 0 else 0
    total_return = df['profit'].sum() if total_trades > 0 else 0
    
    # Max Drawdown (vereinfacht als min kumulativer Summe von Profit)
    df['cumulative_profit'] = df['profit'].cumsum()
    max_drawdown = (df['cumulative_profit'].min() or 0) * 100
    
    print(f"Anzahl Trades: {total_trades}")
    print(f"Trefferquote: {win_rate:.2f} %")
    print(f"Durchschnittlicher Gewinn/Verlust pro Trade: {avg_profit:.4f}")
    print(f"Gesamtrendite (Summe Profit): {total_return:.4f}")
    print(f"Maximaler Drawdown: {max_drawdown:.2f}%")
    
    return df, win_rate, avg_profit, total_return, max_drawdown

def plot_trade_analysis(df):
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2,2,1)
    df['profit'].hist(bins=50)
    plt.title("Verteilung der Gewinne/Verluste je Trade")
    plt.xlabel("Profit")
    plt.ylabel("Anzahl Trades")
    
    plt.subplot(2,2,2)
    df['cumulative_profit'].plot()
    plt.title("Kumulierte Profit-Entwicklung")
    plt.xlabel("Trade-Index")
    plt.ylabel("Kumulativer Profit")
    
    plt.subplot(2,2,3)
    win_loss_counts = df['profit'] > 0
    win_loss_counts.value_counts().plot(kind='bar')
    plt.title("Anzahl Gewinn- vs. Verlust-Trades")
    plt.xticks([0,1], ['Verlust', 'Gewinn'], rotation=0)
    plt.ylabel("Anzahl Trades")
    
    plt.subplot(2,2,4)
    df['profit'].rolling(window=50).mean().plot()
    plt.title("Gleitender Durchschnitt des Profits (Fenster=50 Trades)")
    plt.xlabel("Trade-Index")
    plt.ylabel("Durchschnittlicher Profit")
    
    plt.tight_layout()
    plt.show()

def main():
    df = load_trade_history()
    df, win_rate, avg_profit, total_return, max_drawdown = analyze_trades(df)
    plot_trade_analysis(df)

if __name__ == "__main__":
    main()


