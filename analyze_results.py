import pandas as pd
import matplotlib.pyplot as plt

# 🔁 Pfad zur CSV-Datei mit gespeicherten Ergebnissen (muss aus compare_strategies.py kommen)
RESULT_CSV = "strategy_results.csv"

def plot_bar_chart(df, column, title, top_n=10):
    sorted_df = df.sort_values(by=column, ascending=False).head(top_n)
    plt.figure(figsize=(12, 6))
    plt.barh(sorted_df['Name'], sorted_df[column], edgecolor='black')
    plt.xlabel(column)
    plt.title(title)
    plt.gca().invert_yaxis()  # Beste oben
    plt.tight_layout()
    plt.show()

def main():
    try:
        df = pd.read_csv(RESULT_CSV)
    except FileNotFoundError:
        print(f"❌ Datei '{RESULT_CSV}' nicht gefunden. Bitte zuerst compare_strategies.py ausführen.")
        return

    print("\n📊 Top-Strategien (PnL, Winrate, Trades):")

    # 🔢 Übersicht: beste nach Gewinn
    plot_bar_chart(df, 'Total PnL (USDT)', 'Top Strategien nach Gesamtgewinn')

    # 📈 Beste nach Winrate
    plot_bar_chart(df, 'Winrate (%)', 'Top Strategien nach Gewinnrate')

    # 📊 Aktivste nach Anzahl Trades
    plot_bar_chart(df, 'Trades', 'Strategien mit den meisten Trades')

if __name__ == "__main__":
    main()
