from pathlib import Path
import pandas as pd

INPUT_PATH = Path("reports/step18/step18_core_metrics.csv")
OUT_DIR = Path("reports/step18")

df = pd.read_csv(INPUT_PATH)

print(f"rows: {len(df)}")

# ----------------------------------------
# TOP BOUNDARY TENSION
# ----------------------------------------

boundary_df = (
    df.sort_values(
        "boundary_tension",
        ascending=False,
    )
    .head(250)
)

boundary_out = OUT_DIR / "step18_top_boundary_clusters.csv"
boundary_df.to_csv(boundary_out, index=False)

# ----------------------------------------
# TOP COLLAPSE EXPOSURE
# ----------------------------------------

collapse_df = (
    df.sort_values(
        "collapse_exposure",
        ascending=False,
    )
    .head(250)
)

collapse_out = OUT_DIR / "step18_top_collapse_clusters.csv"
collapse_df.to_csv(collapse_out, index=False)

# ----------------------------------------
# TOP SUSTAINABLE STATES
# ----------------------------------------

sustainable_df = (
    df.sort_values(
        "sustainable_efficiency",
        ascending=False,
    )
    .head(250)
)

sustainable_out = OUT_DIR / "step18_top_sustainable_clusters.csv"
sustainable_df.to_csv(sustainable_out, index=False)

# ----------------------------------------
# REGIME SUMMARY
# ----------------------------------------

summary_df = (
    df.groupby("step18_regime")
    .agg({
        "meta_state_score": "mean",
        "collapse_exposure": "mean",
        "boundary_tension": "mean",
        "coherence_score": "mean",
        "overload_pressure": "mean",
        "sustainable_efficiency": "mean",
    })
    .reset_index()
)

summary_out = OUT_DIR / "step18_cluster_summary.csv"
summary_df.to_csv(summary_out, index=False)

print("DONE")
print(boundary_out)
print(collapse_out)
print(sustainable_out)
print(summary_out)
