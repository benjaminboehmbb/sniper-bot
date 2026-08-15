import pandas as pd


def main() -> None:
    df = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

    cols = [
        "shadow_risk_score",
        "regime_mismatch_score",
        "atr_stress_score",
        "adverse_score_pressure",
    ]

    print()
    print("---- STEP18 DISTRIBUTIONS ----")
    print()

    for c in cols:
        print(c)
        print(df[c].describe())
        print()

    print("DONE")


if __name__ == "__main__":
    main()
