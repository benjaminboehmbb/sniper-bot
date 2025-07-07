import subprocess

def run_step(command, step_name):
    print(f"--- Starte Schritt: {step_name} ---")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"!!! Fehler bei Schritt: {step_name} !!!")
        exit(1)
    else:
        print(f"--- Schritt {step_name} erfolgreich abgeschlossen ---\n")

def main():
    steps = [
        ("python auto_download_validate_merge.py", "Daten Download + Validierung + Merge"),
        ("python calculate_indicators.py", "Indikatorberechnung"),
        ("python simtrader.py", "SimTrader Backtest & Trade-Historie"),
        ("python analyze_trade_history.py", "Analyse der Trade-Historie"),
    ]

    for cmd, name in steps:
        run_step(cmd, name)

if __name__ == "__main__":
    main()
