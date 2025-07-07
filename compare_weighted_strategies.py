import pandas as pd
from simtrader_csv_core import SimTrader

# Beispiel: einzelne Filter-Signale als Spalten simulieren oder aus Indikatoren berechnen
def create_signals(df):
    # Dummy-Signale: Werte zwischen 0 und 1, hier nur beispielhaft
    df["rsi_signal"] = (50 - df["RSI"]) / 50  # je niedriger RSI, desto höher Signal (max 1)
    df["macd_signal"] = (df["MACD"] - df["MACD_signal"]).apply(lambda x: 1 if x > 0 else 0)
    df["bollinger_signal"] = ((df["close"] < df["BB_lower"]).astype(float))
    return df

# Kombiniert die Signale entsprechend der Gewichtungen (dict mit Spaltenname -> Gewicht 0..1)
def combine_signals(df, weights):
    combined = pd.Series(0.0, index=df.index)
    for signal, weight in weights.items():
        if signal in df.columns:
            combined += df[signal] * weight
        else:
            print(f"Warnung: Signalspalte '{signal}' nicht gefunden.")
    # Normiere auf [0, 1], falls Summe der Gewichte > 1
    total_weight = sum(weights.values())
    if total_weight > 1:
        combined = combined / total_weight
    df["combined_signal"] = combined
    return df

def test_weighted_strategies(df, weight_combinations):
    results = []
    for i, weights in enumerate(weight_combinations):
        print(f"\nTeste Kombination {i+1}: {weights}")
        df_test = df.copy()
        df_test = combine_signals(df_test, weights)
        
        trader = SimTrader(df_test, initial_balance=10000)
        trader.run(signal_column="combined_signal", threshold_entry=0.7, threshold_exit=0.3)
        
        trades = trader.get_trade_history()
        roi = (trader.get_balance() - 10000) / 10000 * 100
        win_rate = (trades["profit"] > 0).mean() * 100 if not trades.empty else 0
        
        results.append({
            "Kombination": str(weights),
            "Anzahl Trades": len(trades),
            "Trefferquote (%)": round(win_rate, 2),
            "ROI (%)": round(roi, 2),
            "Endkapital ($)": round(trader.get_balance(), 2),
        })
        
    df_results = pd.DataFrame(results)
    df_results.to_csv("results/weighted_strategy_results.csv", index=False)
    print("\nAlle Ergebnisse gespeichert in results/weighted_strategy_results.csv")
    print(df_results)

def main():
    # Beispiel: Daten laden - bitte sicherstellen, dass Indikatoren (RSI, MACD, BB) schon berechnet sind!
    df = pd.read_csv("C:/btc_data/merged/price_data.csv", parse_dates=["open_time"])
    
    # Beispiel-Signale erzeugen (du kannst deine echten Signale anpassen)
    df = create_signals(df)
    
    # Definiere Gewichtungen für verschiedene Kombis (Beispiele)
    weight_combinations = [
        {"rsi_signal": 1.0},
        {"macd_signal": 1.0},
        {"bollinger_signal": 1.0},
        {"rsi_signal": 0.5, "macd_signal": 0.5},
        {"rsi_signal": 0.7, "bollinger_signal": 0.3},
        {"rsi_signal": 0.3, "macd_signal": 0.3, "bollinger_signal": 0.4},
    ]
    
    test_weighted_strategies(df, weight_combinations)

if __name__ == "__main__":
    main()
