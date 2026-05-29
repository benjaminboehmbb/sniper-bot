from pathlib import Path
import pandas as pd
import numpy as np

REPORT_DIR = Path("reports/step18")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SHADOW_PATH = Path("live_logs/passive_shadow_risk_snapshots.csv")

df = pd.read_csv(SHADOW_PATH)

required = [
    "current_score",
    "shadow_risk_score",
    "meta_state_score",
    "market_regime",
    "atr_quality",
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["shadow_risk_level"] = pd.to_numeric(df["shadow_risk_level"], errors="coerce").fillna(0.0)
df["current_score"] = pd.to_numeric(df["current_score"], errors="coerce").fillna(0.0)
df["meta_state_score"] = pd.to_numeric(df["meta_state_score"], errors="coerce").fillna(0.0)

df["collapse_exposure"] = pd.to_numeric(df["shadow_risk_score"], errors="coerce").fillna(0.0).clip(0.0, 1.0)

df["score_pressure"] = df["current_score"].abs() / 4.0

df["atr_stress"] = np.where(df["atr_quality"].astype(str).str.lower().str.contains("bad"), 1.0, 0.0)

df["regime_stress"] = np.where(
    df["market_regime"].astype(str).str.lower().str.contains("bear"),
    1.0,
    0.0,
)

df["boundary_tension"] = (
    0.45 * df["score_pressure"]
    + 0.35 * df["collapse_exposure"]
    + 0.20 * df["atr_stress"]
)

df["coherence_score"] = 1.0 - df["boundary_tension"].clip(0.0, 1.0)

df["recovery_strength"] = (
    df["coherence_score"]
    * (1.0 - df["collapse_exposure"])
    * (1.0 - 0.5 * df["atr_stress"])
).clip(0.0, 1.0)

df["overload_pressure"] = (
    df["collapse_exposure"]
    + df["atr_stress"]
    + df["score_pressure"]
) / 3.0

df["dissipation_efficiency"] = (
    df["recovery_strength"] / (1.0 + df["overload_pressure"])
).clip(0.0, 1.0)

df["sustainable_efficiency"] = (
    df["coherence_score"]
    * df["dissipation_efficiency"]
).clip(0.0, 1.0)

conditions = [
    df["collapse_exposure"] >= 0.70,
    df["boundary_tension"] >= 0.70,
    df["sustainable_efficiency"] >= 0.60,
]

choices = [
    "collapse_risk",
    "boundary_stress",
    "sustainable",
]

df["step18_regime"] = np.select(conditions, choices, default="neutral")

core_cols = [
    "tick_id",
    "timestamp_utc",
    "side",
    "position",
    "price",
    "current_score",
    "market_regime",
    "atr_quality",
    "shadow_risk_score",
    "shadow_risk_name",
    "meta_state_score",
    "meta_state_bucket",
    "collapse_exposure",
    "score_pressure",
    "atr_stress",
    "regime_stress",
    "boundary_tension",
    "coherence_score",
    "recovery_strength",
    "overload_pressure",
    "dissipation_efficiency",
    "sustainable_efficiency",
    "step18_regime",
]

core_cols = [c for c in core_cols if c in df.columns]
core_df = df[core_cols].copy()

core_df.to_csv(REPORT_DIR / "step18_core_metrics.csv", index=False)

summary = (
    core_df.groupby("step18_regime")
    .mean(numeric_only=True)
    .reset_index()
)
summary.to_csv(REPORT_DIR / "step18_regime_summary.csv", index=False)

core_df.sort_values("boundary_tension", ascending=False).head(500).to_csv(
    REPORT_DIR / "step18_boundary_events.csv", index=False
)

core_df.sort_values("collapse_exposure", ascending=False).head(500).to_csv(
    REPORT_DIR / "step18_collapse_events.csv", index=False
)

core_df.sort_values("sustainable_efficiency", ascending=False).head(500).to_csv(
    REPORT_DIR / "step18_sustainable_topologies.csv", index=False
)

print("DONE")
print(REPORT_DIR / "step18_core_metrics.csv")
print(REPORT_DIR / "step18_regime_summary.csv")
