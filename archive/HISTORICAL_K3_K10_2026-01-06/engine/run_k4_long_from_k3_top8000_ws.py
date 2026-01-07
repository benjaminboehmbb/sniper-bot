#!/usr/bin/env python3
import os
import sys
import subprocess


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    analyze_path = os.path.join(script_dir, "analyze_template.py")

    data_path = os.path.join(project_root, "data", "price_data_with_signals_regime.csv")

    strategies_path = os.path.join(
        project_root, "data", "strategies_k4_from_k3_top8000_long.csv"
    )

    output_dir = os.path.join(
        project_root, "results", "k4_long_from_k3_top8000"
    )

    os.makedirs(output_dir, exist_ok=True)

    print("Running K4 LONG from K3 TOP8000 (Workstation)...")
    print("Data:", data_path)
    print("Strategies:", strategies_path)
    print("Output:", output_dir)

    cmd = [
        sys.executable,
        analyze_path,
        "--data", data_path,
        "--strategies", strategies_path,
        "--sim", "long",
        "--k", "4",
        "--threshold", "0.60",
        "--cooldown", "0",
        "--require-ma200", "1",
        "--min-trades", "50",
        "--max-trades", "50000",
        "--num-procs", "30",     # Workstation nutzt 30 Threads
        "--progress-step", "2",
        "--save-trades", "0",
        "--normalize", "1",
        "--use-regime", "1",
        "--output-dir", output_dir,
    ]

    print("Command:")
    print(" ".join(cmd))

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Error: analyze_template returned", result.returncode)
        sys.exit(result.returncode)

    print("Done. K4 LONG top8000 run completed on Workstation.")


if __name__ == "__main__":
    main()
