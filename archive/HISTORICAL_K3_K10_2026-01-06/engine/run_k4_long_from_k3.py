#!/usr/bin/env python3
import os
import sys
import subprocess


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    analyze_path = os.path.join(script_dir, "analyze_template.py")
    data_path = os.path.join(project_root, "data", "price_data_with_signals_regime.csv")
    strategies_path = os.path.join(project_root, "data", "strategies_k4_from_k3_top1000_long.csv")
    output_dir = os.path.join(project_root, "results", "k4_long_from_k3_top1000")

    os.makedirs(output_dir, exist_ok=True)

    print("Running K4 long analysis from K3 top1000 (G15)...")
    print("Data:        %s" % data_path)
    print("Strategies:  %s" % strategies_path)
    print("Output dir:  %s" % output_dir)
    print("Engine:      %s" % analyze_path)

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
        "--num-procs", "14",
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
        print("Error: analyze_template.py returned non-zero exit code %d" % result.returncode)
        sys.exit(result.returncode)

    print("Done. K4 long analysis finished.")


if __name__ == "__main__":
    main()
