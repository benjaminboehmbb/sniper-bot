import pandas as pd

def build_trade_history(trades_csv='results/trades.csv', output_csv='results/trade_history.csv'):
    print(f"Lade Trades aus: {trades_csv}")
    df = pd.read_csv(trades_csv, parse_dates=['timestamp'])
    print(f"Spaltennamen: {list(df.columns)}")

    # Prüfen, dass notwendige Spalten vorhanden sind
    required_cols = ['timestamp', 'price', 'type']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Spalte '{col}' nicht gefunden in trades.csv")

    # Sortieren nach Zeit, falls noch nicht geschehen
    df = df.sort_values('timestamp').reset_index(drop=True)

    trades = []
    position_open = False
    entry_time = None
    entry_price = None

    for idx, row in df.iterrows():
        signal = row['type'].strip().upper()
        price = row['price']
        time = row['timestamp']

        if signal == 'BUY' and not position_open:
            # Einstieg
            position_open = True
            entry_time = time
            entry_price = price
        elif signal == 'SELL' and position_open:
            # Ausstieg, Trade schließen
            exit_time = time
            exit_price = price
            profit = (exit_price - entry_price) / entry_price  # Prozentualer Gewinn/Verlust
            trades.append({
                'entry_time': entry_time,
                'entry_price': entry_price,
                'exit_time': exit_time,
                'exit_price': exit_price,
                'profit': profit
            })
            position_open = False
            entry_time = None
            entry_price = None
        else:
            # Signal ignorieren (z.B. doppeltes BUY oder SELL ohne vorheriges BUY)
            continue

    trade_history_df = pd.DataFrame(trades)
    print(f"Erstellte Trade-Historie mit {len(trade_history_df)} Trades.")

    trade_history_df.to_csv(output_csv, index=False)
    print(f"Trade-Historie gespeichert unter: {output_csv}")

if __name__ == '__main__':
    build_trade_history()
