from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from tools.trade_inspector import aggregate_csv
from tools.trade_inspector import archive_intake as intake
from tools.trade_inspector import csv_persistence
from tools.trade_inspector import feature_importance
from tools.trade_inspector import feature_discovery
from tools.trade_inspector import feature_preparation
from tools.trade_inspector import feature_stability
from tools.trade_inspector import inspect_trades as inspector
from tools.trade_inspector import inspection_primitives as primitives
from tools.trade_inspector import label_registry
from tools.trade_inspector import leakage_audit
from tools.trade_inspector import ml_dataset
from tools.trade_inspector import path_diagnosis
from tools.trade_inspector import raw_ml_csv
from tools.trade_inspector import regime_identity_rows


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "tools" / "trade_inspector" / "inspect_trades.py"

ENTRY_TS = "2026-01-01T00:00:00+00:00"
EXIT_TS = "2026-01-01T00:02:00+00:00"
EXPECTED_ROW_SHA256 = "54fc961343d463d4e55d6489c70ec9ffcf3892acc9155b45b95e5f9408a2ce24"
EXPECTED_FIELD_ORDER_SHA256 = "76c7ca3b7c1b1e5652bc5ece60648fb23f2eb09e32553bef63ddbb22f385e795"
EXPECTED_ORDERED_ROW_SHA256 = "a79a164bbbeb5a1584e34aadc3c0c04f451445c94e9eec2e9b0e171aadadb60b"
S4_REGIME_CASES_SHA256 = "d37f242b767fa32d6ffdbbee148dfd820805f07bdbf0e310090f068659db7b4a"
S4_TRADE_FAMILY_CASES_SHA256 = "18a1d2ccbd54647b09077dace28af5c7795eb34c90ff64660901962e17c7acab"
S4_MULTI_ROW_SUMMARY_SHA256 = "b8f5f7bd37b5be8f6a2cc3ca3eccec2b932da183f07143959bfc6133dc41fd45"
S5_REGISTRY_SHA256 = "eb96ee7fca17655042c102a3162d5d8cdbfaf1bda4ac17789ff00be245b159d6"
S5_EMPTY_REGISTRY_SHA256 = "451b629a29c79d2735940170b9a228bba8e67f66a373881534267240a5b21475"
S5_ASSIGNMENT_SHA256 = "e4f22c64c51f3a8405edf7252de58d057b7f759c208fe25eb7b10767954f6ec6"
S5_CSV_ROWS_SHA256 = "d1cf0f439a99544239b70e95fca11b48485fa190889083c92497d051eed8a57c"
S5_PARTIAL_CSV_SHA256 = "64c0dea2e1c321cbbcbf78285b8704a51abbc6b0be3117c8c3208ac6082a3284"
S5_RAW_ML_CSV_SHA256 = "be6e308c2c2467a00f68a589f510e161d7414e4c815624c595c2aa8719173c29"
S5_RAW_ML_HEADER_SHA256 = "6a8d64f5cf94ddb6d5d53fa2c73f8cd5fd00c2191cd12849d51d02a3f9d6f85c"
S5D_AGGREGATE_ARTIFACT_SHA256 = {
    "aggregate_by_entry_regime_label.csv": "444f3135104d5db59c25f9238278f8d2c3171753aa03df9086c5c906318e297e",
    "aggregate_by_entry_risk_label.csv": "59635850e5544d1678b0900a207568a14c821d6f520e4c888c09baa4032a8ad4",
    "aggregate_by_overall_score_band.csv": "ed40fed361d3e53871b76611a2e0902da143c052ffef58533b1b6ab835d423af",
    "aggregate_by_priority.csv": "c04c2da04d8f90befd1facecc2dcb087cc707956de26ecabdd05ad52e76f4a2c",
    "aggregate_by_quality_class.csv": "6059f1334518898da1fbe0f70a14fd823b35653c639bad46e75556d8d97af692",
    "aggregate_by_regime_aligned.csv": "c963ddc782716568c05eaf0738193ff9378ea358e93bfec09bf5a08da793ab62",
    "aggregate_by_root_cause.csv": "af43230e510123d1ec07dee94a97dce530086195492d02bfb282b0e6553fa673",
    "aggregate_by_trade_family.csv": "07005bcfc3304fb9bf71233e0077d9560dff6b99150cdaaef1e7e93a9fe3dede",
    "aggregate_by_trade_family_group.csv": "eeef423cc6d382559ce3ed4d66a7a626c8c6a4d2708a1f5ca38ea1fbb6d4cd47",
    "aggregate_global_summary.csv": "59ea6e99813dd62b639afe7917b045fc37daa1317e7a41955db7be8c5cd8fa18",
    "aggregate_root_cause_attribution.csv": "330e09660421e0b5a178b308a6458242c9f8676ac9ce3e6e6f73927d18eff468",
    "aggregate_top_improvement_candidates.csv": "4e2b1fdc169e74a7695840eac490879014afec9b5f81825c9a3be47aea1b3ed9",
}
S5D_AGGREGATE_MANIFEST_SHA256 = "64e371f979cffe4ca2e01ad18d94fba14f0fea2a90755cb26f1de1a3b1ae1e98"
S5D_EMPTY_GLOBAL_SUMMARY_SHA256 = "4e0fcbcd6382b7330f800a27e4bee758b36434729406735abe18183d3b41870e"
S5D_EMPTY_MANIFEST_SHA256 = "94705901ba1a8aa982a011665f71480d353a066e83919fc930a429474a13a6c4"
S5E_ML_DATASET_ARTIFACT_SHA256 = {
    "trade_dataset_v4a.csv": "76b41d4813d9512fd660086866ce89c162cdfdeeb90740e758a5a9eac1f61df4",
    "trade_dataset_v4a_manifest.csv": "5d3df016b5266ada50bc4a56204d18cc7c70375715cc48fac980f009d1cd9629",
    "trade_dataset_v4a_test.csv": "5f08ba7342a7ff83fe050a77770f89e45b8f9300b8390c51fd96d58834654919",
    "trade_dataset_v4a_train.csv": "1c6274a814db00ffff5ab5f35d63aaa1bc660eef43185ce792109b29b2c1c969",
    "trade_dataset_v4a_validation.csv": "4cc320bf485a15e321c4e25303c7a8efbbf8b3aba38e38b323f2ec4dec196eec",
}
S5E_ML_DATASET_MANIFEST_SHA256 = "e9203c8dbef4325350d293e922b9968c417bf1089a822142d9ddd05765663686"
S5E_EMPTY_ML_MANIFEST_CSV_SHA256 = "5aa677b6250500aa3986259da909b636b6d8218d8c2fcf719eb66ecf9c8cadd2"
S5E_EMPTY_ML_DATASET_MANIFEST_SHA256 = "5b6728110f59af120e350655e535d98f16f7325f2cf50a9928bcc8a7037b76c8"
S5F_FEATURE_PREPARATION_ARTIFACT_SHA256 = {
    "trade_dataset_v4b_feature_catalog.csv": "e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667",
    "trade_dataset_v4b_feature_manifest.csv": "5f4ddd082187a4dde4b5686356760b877034127596ce556fdaac0000d9b820eb",
    "trade_dataset_v4b_model_ready.csv": "f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f",
    "trade_dataset_v4b_model_ready_test.csv": "814ea2f70122edeecb0f36b4c339d78d7aa0818275d3e805876603cbda4b889b",
    "trade_dataset_v4b_model_ready_train.csv": "5892adcd003f2fc0726bbf7ecd01fc1b637f68a147b1b3f194de45c3eec89f3e",
    "trade_dataset_v4b_model_ready_validation.csv": "ef987f0557ebcdea1c3dbc08ffb6c1d272d38d5669154e854019fefe0a74a624",
}
S5F_FEATURE_PREPARATION_MANIFEST_SHA256 = "627951215e9fe327e64f450234f09f376966a970a0fbdc20551876b5da604e9e"
S5F_EMPTY_FEATURE_MANIFEST_CSV_SHA256 = "b86ec7a1b1873770c10015c990c4aea583e9bc57631a5b9c1131d2a2455ade82"
S5F_EMPTY_FEATURE_PREPARATION_MANIFEST_SHA256 = "806b317c5793aa295f6648634e71031d49d4a6aa5af744998c8ee187cfdf4120"
S5G_LEAKAGE_AUDIT_ARTIFACT_SHA256 = {
    "trade_dataset_v4c_blocked_features.csv": "b56bad304ae083fe6c2d5a6172e7bf437e637516b1c3c221adf4a4f3fe255fb6",
    "trade_dataset_v4c_feature_catalog.csv": "e1a9817db5033c910f3e6c89b4becdcee0f35f8f03af05ccb3e35bb8dfb07667",
    "trade_dataset_v4c_leakage_report.csv": "a4f52df0c9396f899732b0cc4d590e1913865452c87fc5062cf347a747c352a9",
    "trade_dataset_v4c_manifest.csv": "07b13029f7de0e06387cb801947c952858c3f7df776bb8f6c971cd7c6c3a39fb",
    "trade_dataset_v4c_model_ready.csv": "f381baf1d039ded694828552dd90f8e37796ef13d95257cfb4e697a066beaa4f",
    "trade_dataset_v4c_targets.csv": "5c1a03588e1039b020199cb4a7ae1aa5c7011e56dce27d9e5a37abda49aa2d04",
    "trade_dataset_v4c_training_features.csv": "810c439fabe9cd0afecd6931044129bad743b0bccfaf045d6d8084bc1c6b5a3b",
}
S5G_LEAKAGE_AUDIT_MANIFEST_SHA256 = "960027b4b0a035f309decd610c88ea2a3f43c40c67f65b09bf3c6ce722c1cb6c"
S5G_EMPTY_LEAKAGE_MANIFEST_CSV_SHA256 = "3df387b8bcb32cade9870a54271187a90429dfd56256ad7ab499ed7fe8ef58de"
S5G_EMPTY_LEAKAGE_AUDIT_MANIFEST_SHA256 = "56e25192ef9f9e0bf5eb8588155c4e31b37d5d1819c402edb435280a016f241a"
S5H_FEATURE_IMPORTANCE_ARTIFACT_SHA256 = {
    "feature_importance_v5.csv": "3d0b7d717501abda8b9ca2b8923c137542a6892b9d0ce91225371aa033631208",
    "feature_importance_v5_manifest.csv": "7da05e42a2063959df060f14115948405ed3ffb267ceaaeacebd8d8a155a412c",
    "feature_importance_v5_target_exit_efficiency_high.csv": "2ea760565dc25a28abdc3d2ef53f9115489cf22f837d4436bb12a68712b97b5c",
    "feature_importance_v5_target_future_return_24h_pct.csv": "3ba3fc746c83c40cd83471d234d27c1af61667547e2a7efe6e3bdd39471fe009",
    "feature_importance_v5_target_future_return_72h_pct.csv": "27c1a66f6a20fbb9dd5ae2448d5b02b22079ce9962356bf2ad6cf2d0ef856f76",
    "feature_importance_v5_target_loser.csv": "18571ba0b8424372de4dcd639f7780d24602885447940e5b7cf740f74ea4a492",
    "feature_importance_v5_target_opportunity_loss_high.csv": "a72fbc2b0a5d344b007302a32af0770b758ac1f64b5f062da01613479a2df056",
    "feature_importance_v5_target_pnl_pct.csv": "cf0e8529066d5ecb33674c2766f81f6c2ff6edb007ba38a2d74152ee302e1435",
    "feature_importance_v5_target_quality_bad.csv": "64899183556b9fee75c05275f403737bdad50f990f3db8909cfe6a019384e485",
    "feature_importance_v5_target_quality_good.csv": "0d8e5de26a874dbca2f8ff79d5360e2770c73e467766dfee4f62bac3fdb7652a",
    "feature_importance_v5_target_winner.csv": "c12cbb10b7ad63862c1124d5a78776ad449fd236d49b3643a43a3dbab1c5f239",
}
S5H_FEATURE_IMPORTANCE_MANIFEST_SHA256 = "6fcba2761ac06c53a3a2ec407855546fb6b0d8dee039f7426fe6fa0012bf5ca3"
S5H_EMPTY_FEATURE_IMPORTANCE_MANIFEST_CSV_SHA256 = "d7aeacdb72b1c8a94e3c5821810fbdfa4be0ff92291f7fb085a3f380a20914c1"
S5H_EMPTY_FEATURE_IMPORTANCE_MANIFEST_SHA256 = "2567d4677cc4ee0e4f3d3368ae5ed103b1cd76726434387ca6f0228b7fb33efa"
S5I_FEATURE_STABILITY_ARTIFACT_SHA256 = {
    "feature_stability_v5c.csv": "e065376bcb0c8ac50034ecedc568f1f42757c4de3e2f3d5664cf1728b19676c1",
    "feature_stability_v5c_manifest.csv": "c596df9916a3f2232c52a972d772f17a9ad51c3b1a977e1cb2148dac89866b7e",
    "feature_stability_v5c_target_matrix.csv": "b1d3e3e6eb1dd0b5957a5c421f267dbc82021ad6e77f3e99b7e4e6a622561f3c",
}
S5I_FEATURE_STABILITY_MANIFEST_SHA256 = "052de759d98246fd11e5c77beac125edee974e75f6aea4e0a6b6d9375b36031e"
S5I_EMPTY_FEATURE_STABILITY_MANIFEST_CSV_SHA256 = "64f12c76958672da15694846fea8a67e4c99988381d0ae4d15076a2f561dd149"
S5I_EMPTY_FEATURE_STABILITY_MANIFEST_SHA256 = "34061f834ca1aca459872696beb07e10bf199072d318b06aa47057225b30c52a"
S5J_FEATURE_DISCOVERY_ARTIFACT_SHA256 = {
    "predictive_signal_discovery_by_entry_atr_signal.csv": "3ad2be8913f34a464764f8fbfae03f148b6378cf8fd285bd2503da8da0f7adca",
    "predictive_signal_discovery_by_entry_ma200_signal.csv": "9ed93eef28752fbd016c0aa1b733ee87bb8a40c0de0ad7fb389bd0ca7b618a9a",
    "predictive_signal_discovery_by_entry_ma200_signal__entry_mfi_signal.csv": "9d5d28abf849010899b211db6320846f230d7b91259163131e1191de7b4963d8",
    "predictive_signal_discovery_by_entry_mfi_signal.csv": "383bdc338f946ec3840f8588f5a7c51b6bbd9cbe0940e122ad613ef72195c54d",
    "predictive_signal_discovery_by_entry_regime_label.csv": "700bd46a5571f850ff87f8dfef882ed5e5d72f16a0822bda1bd75b4978ed5abe",
    "predictive_signal_discovery_by_entry_regime_label__entry_atr_signal.csv": "4f3bdf904ff3ffbdefcc48ff917c4d6c4f450781d3f50f8dd831aa1c3701e14f",
    "predictive_signal_discovery_by_entry_regime_label__entry_risk_label.csv": "cae53cc8bba6fa20eba91ebc97ef59333924ac3af8a094ab3b56f84757189714",
    "predictive_signal_discovery_by_entry_risk_label.csv": "fc97279e76e73c8a19dd9c091d58cc72514ccd5033057e3571f56115646dc368",
    "predictive_signal_discovery_by_entry_risk_label__regime_aligned.csv": "be976117d93ca9362fb5b40d0365de9497332bb9398e98daec71f137c3d24bea",
    "predictive_signal_discovery_by_entry_score_at_entry.csv": "5579db97ea8072ed1d3a8211528dfe1521aee7613980caf19920ad67ddf57bf6",
    "predictive_signal_discovery_by_entry_score_at_entry__entry_risk_label.csv": "156fcd8ae05328fcb3862587364a0eca2bc46875362a99b2dc73680e3f857dbe",
    "predictive_signal_discovery_by_regime_aligned.csv": "359d827266721f5abc107137684f7c5fcc567f27ad41cadeafb365b0a1b954bb",
    "predictive_signal_discovery_by_risk_good_at_entry.csv": "e7f18ab9126f8c4e8fdf318e5fa308eba87c217047b60389c2241f131bb5e932",
    "predictive_signal_discovery_by_trade_family.csv": "a36e72e74bc6946db311f33ad29d005b1cf4fb96f4c111f21b85bca72b32abab",
    "predictive_signal_discovery_by_trade_family_group.csv": "2e7ceb7c0b3a02272fa3e0ff382a9cac3f5a8deaa1eaec5a0422cd93375beacb",
    "predictive_signal_discovery_by_trade_family_group__entry_risk_label.csv": "73b0eaad9740672e4774b95d7a4c51d9bdc4a20fbdf5d45d33b133706b52ad90",
    "predictive_signal_discovery_v6_all.csv": "e23c6f8e368e6c4f7e61348dcf21eab14fb3e2bc278be91ddb70c9cd77e18e42",
    "predictive_signal_discovery_v6_manifest.csv": "3fdb191601b73f5e286299427055c8514412454905e88f1b44429a632019cd9a",
    "predictive_signal_discovery_v6_top.csv": "e23c6f8e368e6c4f7e61348dcf21eab14fb3e2bc278be91ddb70c9cd77e18e42",
}
S5J_FEATURE_DISCOVERY_MANIFEST_SHA256 = "6584edce59c245c9d269ff0e5bc9da94b2ec256f81ffab4761715c4bd7558da0"
S5J_EMPTY_FEATURE_DISCOVERY_MANIFEST_CSV_SHA256 = "309dd83128ca34f11abee60ddc337db67364b08bba07e881adb34cdb1f508e00"
S5J_EMPTY_FEATURE_DISCOVERY_MANIFEST_SHA256 = "f4a0db55691d25ce74b81075dfea479fff94a6bd0af18a777e4b134810438a3b"
S3_SCENARIO_SHA256 = {
    "long": "de903d536a9874756c6a74bd6325f8e8bfea20ee6157222923efe024a5863aa1",
    "short": "c9cd9800a4a4de3f2b64daf9c6ec3c7df328308615064c37aff5bc9441a23276",
    "missing_path": "c54567d7b491ea7bf5f52d7b3bdb1a6a3c7df8e7d2815cb3efc07746ff7126f1",
    "zero_pnl": "3ca07215b9a292188e019f10617e2c1537f384d049818b857cb7c583a3bb5f72",
    "invalid_duration": "12d34e43c7117698ea579014b503e539a8dff6bd07c3095ecaa2d9cc78656987",
}


def sample_trade() -> dict[str, object]:
    return {
        "symbol": "BTCUSDT",
        "side": "long",
        "entry_timestamp_utc": ENTRY_TS,
        "exit_timestamp_utc": EXIT_TS,
        "duration_sec": 120,
        "entry_price": 100.0,
        "exit_price": 102.0,
        "pnl": 2.0,
        "pnl_pct": 0.02,
        "exit_reason": "take_profit",
    }


def sample_audit_rows() -> list[dict[str, object]]:
    return [
        {
            "event": "ENTRY_ACCEPTED",
            "timestamp_utc": ENTRY_TS,
            "side": "short",
            "reason": "wrong_side_decoy",
        },
        {
            "event": "ENTRY_ACCEPTED",
            "timestamp_utc": ENTRY_TS,
            "side": "long",
            "reason": "signal",
            "position_before": "FLAT",
            "position_after": "LONG",
        },
        {
            "event": "EXIT_EXECUTED",
            "timestamp_utc": EXIT_TS,
            "side": "long",
            "reason": "take_profit",
            "position_after": "FLAT",
        },
    ]


def sample_market_path() -> tuple[list[str], list[float]]:
    base = datetime.fromisoformat(ENTRY_TS)
    minute_offsets = [0, 1, 2, 17, 62, 242, 1442, 4322, 10082]
    timestamps = [(base + timedelta(minutes=value)).isoformat() for value in minute_offsets]
    prices = [100.0, 105.0, 102.0, 103.0, 104.0, 106.0, 108.0, 110.0, 112.0]
    return timestamps, prices


def sample_short_market_path() -> tuple[list[str], list[float]]:
    timestamps, _ = sample_market_path()
    prices = [100.0, 95.0, 98.0, 97.0, 96.0, 94.0, 92.0, 90.0, 88.0]
    return timestamps, prices


def sample_regime_index() -> dict[str, dict[str, object]]:
    return inspector.build_regime_index(
        [
            {
                "timestamp_utc": ENTRY_TS,
                "regime_label": "bull",
                "risk_label": "good_atr",
                "entry_score": "2",
                "ma200_signal": "1",
                "mfi_signal": "1",
                "atr_signal": "1",
            },
            {
                "timestamp_utc": EXIT_TS,
                "regime_label": "bear",
                "risk_label": "bad_atr",
                "entry_score": "-1",
                "ma200_signal": "-1",
                "mfi_signal": "-1",
                "atr_signal": "-1",
            },
        ]
    )


def build_sample_row() -> dict[str, object]:
    trade = sample_trade()
    timestamps, prices = sample_market_path()
    trade_id = inspector.build_trade_id(trade)
    return inspector.build_rows(
        [trade],
        sample_audit_rows(),
        sample_regime_index(),
        timestamps,
        prices,
        {trade_id: "alpha"},
    )[0]


def s5d_aggregate_rows() -> list[dict[str, object]]:
    return [
        {
            "human_label": "alpha",
            "trade_id": "T-A",
            "root_cause": "early_exit",
            "priority": "HIGH",
            "priority_score": 90,
            "impact_score": 80,
            "root_cause_confidence": 85,
            "opportunity_loss_24h_pct": 0.20,
            "exit_efficiency_24h_pct": 0.30,
            "pnl": -2.5,
            "pnl_pct": -0.025,
            "entry_regime_label": "TREND",
            "entry_risk_label": "LOW",
            "regime_aligned": 1,
            "regime_changed_during_trade": 0,
            "entry_score_at_entry": 75,
            "entry_time_chart": "2026-01-01 00:00:00",
            "exit_time_chart": "2026-01-01 00:02:00",
            "quality_class": "GOOD",
            "overall_score_band": "HIGH",
            "trade_family_group": "MOMENTUM",
            "trade_family": "TF-A",
            "overall_score": 80,
            "is_winner": 0,
            "is_loser": 1,
            "cause_weights": "early_exit=70|regime_mismatch=30",
        },
        {
            "human_label": "beta",
            "trade_id": "T-B",
            "root_cause": "entry_quality",
            "priority": "MEDIUM",
            "priority_score": 60,
            "impact_score": 50,
            "root_cause_confidence": 70,
            "opportunity_loss_24h_pct": 0.10,
            "exit_efficiency_24h_pct": 0.50,
            "pnl": 4.0,
            "pnl_pct": 0.04,
            "entry_regime_label": "RANGE",
            "entry_risk_label": "HIGH",
            "regime_aligned": 0,
            "regime_changed_during_trade": 1,
            "entry_score_at_entry": 40,
            "entry_time_chart": "2026-01-02 00:00:00",
            "exit_time_chart": "2026-01-02 00:03:00",
            "quality_class": "WATCH",
            "overall_score_band": "MID",
            "trade_family_group": "REVERSION",
            "trade_family": "TF-B",
            "overall_score": 60,
            "is_winner": 1,
            "is_loser": 0,
            "cause_weights": "entry_quality=100",
        },
        {
            "human_label": "gamma",
            "trade_id": "T-C",
            "root_cause": "early_exit",
            "priority": "HIGH",
            "priority_score": 95,
            "impact_score": 70,
            "root_cause_confidence": 90,
            "opportunity_loss_24h_pct": 0.25,
            "exit_efficiency_24h_pct": 0.20,
            "pnl": -1.0,
            "pnl_pct": -0.01,
            "entry_regime_label": "TREND",
            "entry_risk_label": "LOW",
            "regime_aligned": 1,
            "regime_changed_during_trade": 0,
            "entry_score_at_entry": 80,
            "entry_time_chart": "2026-01-03 00:00:00",
            "exit_time_chart": "2026-01-03 00:01:00",
            "quality_class": "BAD",
            "overall_score_band": "LOW",
            "trade_family_group": "MOMENTUM",
            "trade_family": "TF-A",
            "overall_score": 40,
            "is_winner": 0,
            "is_loser": 1,
            "cause_weights": "early_exit=50|regime_mismatch=50",
        },
    ]


def s5e_ml_dataset_rows() -> list[dict[str, object]]:
    base = build_sample_row()
    specs = [
        {
            "trade_id": "A",
            "human_label": "train-row",
            "pnl": 2.0,
            "pnl_pct": 0.02,
            "overall_score": 80,
            "exit_efficiency_24h_pct": 0.70,
            "opportunity_loss_24h_pct": 0.01,
            "mae_pct": -0.005,
            "mfe_pct": 0.02,
            "cf_return_24h_pct": 0.01,
            "cf_return_72h_pct": 0.02,
            "cf_return_168h_pct": 0.03,
        },
        {
            "trade_id": "K",
            "human_label": "validation-row",
            "pnl": -1.5,
            "pnl_pct": -0.015,
            "overall_score": 30,
            "exit_efficiency_24h_pct": 0.20,
            "opportunity_loss_24h_pct": 0.04,
            "mae_pct": -0.02,
            "mfe_pct": 0.0,
            "cf_return_24h_pct": -0.01,
            "cf_return_72h_pct": -0.02,
            "cf_return_168h_pct": -0.03,
        },
        {
            "trade_id": "Z",
            "human_label": "test-row",
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "overall_score": 50,
            "exit_efficiency_24h_pct": 0.40,
            "opportunity_loss_24h_pct": 0.03,
            "mae_pct": -0.01,
            "mfe_pct": 0.01,
            "cf_return_24h_pct": 0.0,
            "cf_return_72h_pct": 0.01,
            "cf_return_168h_pct": 0.02,
        },
    ]
    rows: list[dict[str, object]] = []
    for spec in specs:
        row = dict(base)
        row.update(spec)
        rows.append(row)
    return rows


def build_s3_snapshot(
    trade: dict[str, object],
    timestamps: list[str],
    prices: list[float],
) -> dict[str, object]:
    entry = {"event": "ENTRY_ACCEPTED"}
    exit_row = {"event": "EXIT_EXECUTED"}
    path = inspector.calculate_trade_path(trade, timestamps, prices)
    counterfactuals = inspector.calculate_counterfactuals(trade, timestamps, prices)
    quality_score, quality_band, positives, negatives = inspector.compute_quality_score(
        trade,
        entry,
        exit_row,
    )
    interpretation = inspector.interpretation_flags(path, counterfactuals)
    diagnosis = inspector.compute_diagnosis(path, counterfactuals, float(trade.get("pnl", 0.0)))
    confidence = inspector.compute_confidence_layer(
        {
            "has_entry_audit": 1,
            "has_exit_audit": 1,
            **path,
            **counterfactuals,
            **interpretation,
            **diagnosis,
        }
    )
    return {
        "quality_flags": inspector.quality_flags(trade, entry, exit_row),
        "quality": {
            "score": quality_score,
            "band": quality_band,
            "positives": positives,
            "negatives": negatives,
        },
        "path": path,
        "counterfactuals": counterfactuals,
        "interpretation": interpretation,
        "diagnosis": diagnosis,
        "confidence": confidence,
    }


def s3_snapshot_sha256(snapshot: dict[str, object]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def canonical_sha256(value: object, *, sort_keys: bool = True) -> str:
    payload = json.dumps(
        value,
        sort_keys=sort_keys,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def s5e_expected_stdout(
    output_dir: Path,
    artifact_names: list[str],
    split_quality: dict[str, object],
) -> str:
    keys = [
        "split_quality_status",
        "split_quality_warnings",
        "rows_total",
        "rows_train",
        "rows_validation",
        "rows_test",
        "train_share",
        "validation_share",
        "test_share",
    ]
    return (
        "\nML SPLIT QUALITY\n"
        + "-" * 80
        + "\n"
        + "".join(f"{key}: {split_quality[key]}\n" for key in keys)
        + f"ML dataset export directory: {output_dir}\n"
        + "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


def s5f_expected_stdout(output_dir: Path, artifact_names: list[str]) -> str:
    return (
        f"Feature preparation export directory: {output_dir}\n"
        "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


def s5g_expected_stdout(
    output_dir: Path,
    artifact_names: list[str],
    *,
    allowed: int,
    blocked: int,
    high: int,
    medium: int,
    low: int,
) -> str:
    return (
        f"Leakage audit export directory: {output_dir}\n"
        "audit_status: PASS\n"
        f"allowed_features: {allowed}\n"
        f"blocked_features: {blocked}\n"
        f"high_risk_leakage_features: {high}\n"
        f"medium_risk_leakage_features: {medium}\n"
        f"low_risk_features: {low}\n"
        "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


def s5h_expected_stdout(
    output_dir: Path,
    artifact_names: list[str],
    *,
    status: str,
    warning: str,
    rows_total: int,
    allowed_features: int,
) -> str:
    return (
        f"Feature importance export directory: {output_dir}\n"
        f"feature_importance_status: {status}\n"
        f"feature_importance_warning: {warning}\n"
        f"rows_total: {rows_total}\n"
        f"allowed_features: {allowed_features}\n"
        "targets_evaluated: 9\n"
        "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


def s5i_expected_stdout(
    output_dir: Path,
    artifact_names: list[str],
    *,
    status: str,
    warning: str,
    rows_total: int,
    features_analyzed: int,
) -> str:
    return (
        f"Feature stability export directory: {output_dir}\n"
        f"stability_status: {status}\n"
        f"stability_warning: {warning}\n"
        f"rows_total: {rows_total}\n"
        f"features_analyzed: {features_analyzed}\n"
        "targets_analyzed: 9\n"
        "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


def s5j_expected_stdout(
    output_dir: Path,
    artifact_names: list[str],
    *,
    status: str,
    warning: str,
    rows_total: int,
    groups_evaluated: int,
    promising: int,
    watch: int,
    low_support: int,
    not_actionable: int,
    watch_only: int,
    actionable: int,
    high_warning: int,
) -> str:
    return (
        f"Predictive signal discovery export directory: {output_dir}\n"
        f"discovery_status: {status}\n"
        f"discovery_warning: {warning}\n"
        f"rows_total: {rows_total}\n"
        f"groups_evaluated: {groups_evaluated}\n"
        f"promising_groups: {promising}\n"
        f"watch_groups: {watch}\n"
        f"low_support_groups: {low_support}\n"
        f"not_actionable_groups: {not_actionable}\n"
        f"watch_only_groups: {watch_only}\n"
        f"actionable_candidate_groups: {actionable}\n"
        f"high_warning_groups: {high_warning}\n"
        "files:\n"
        + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_names))
    )


class TradeInspectorCharacterizationTests(unittest.TestCase):
    def test_compatibility_primitives_are_reexported_with_exact_conversion_rules(self) -> None:
        self.assertIs(inspector.safe_text, primitives.safe_text)
        self.assertIs(inspector.safe_float, primitives.safe_float)
        self.assertIs(inspector.safe_int, primitives.safe_int)
        self.assertIs(inspector.parse_ts, primitives.parse_ts)
        self.assertIs(inspector.ts_key, primitives.ts_key)

        cases = [
            (None, -9.0, -9),
            ("", -9.0, -9),
            ("1", 1.0, 1),
            ("1.0", 1.0, -9),
            ("bad", -9.0, -9),
            (True, 1.0, 1),
        ]
        for value, expected_float, expected_int in cases:
            with self.subTest(value=value):
                self.assertEqual(primitives.safe_float(value, -9.0), expected_float)
                self.assertEqual(primitives.safe_int(value, -9), expected_int)

    def test_jsonl_and_market_parsers_keep_current_acceptance_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            jsonl_path = root / "records.jsonl"
            jsonl_path.write_text('{"id": 1}\n\n{"id": 2}\n', encoding="utf-8")
            self.assertEqual(inspector.read_jsonl(jsonl_path), [{"id": 1}, {"id": 2}])

            bad_path = root / "bad.jsonl"
            bad_path.write_text('{"id": 1}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"line 2"):
                inspector.read_jsonl(bad_path)

            market_path = root / "market.csv"
            with market_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "close"])
                writer.writeheader()
                writer.writerow({"timestamp_utc": ENTRY_TS, "close": "100.5"})
                writer.writerow({"timestamp_utc": EXIT_TS, "close": "0"})
                writer.writerow({"timestamp_utc": "", "close": "102"})

            timestamps, prices = inspector.parse_market_rows(market_path)
            self.assertEqual(timestamps, [ENTRY_TS])
            self.assertEqual(prices, [100.5])

    def test_entry_matching_is_side_sensitive_and_exit_matching_is_timestamp_based(self) -> None:
        trade = sample_trade()
        audit_rows = sample_audit_rows()
        audit_rows[-1]["side"] = "short"

        entry, exit_row = inspector.find_matching_entry_exit(trade, audit_rows)

        self.assertIsNotNone(entry)
        self.assertEqual(entry["reason"], "signal")
        self.assertIsNotNone(exit_row)
        self.assertEqual(exit_row["reason"], "take_profit")

    def test_built_row_has_stable_semantic_fingerprint(self) -> None:
        row = build_sample_row()

        self.assertEqual(len(row), 127)
        self.assertEqual(row["trade_id"], "T_20260101_000000_LONG_BTCUSDT")
        self.assertEqual(row["quality_score"], 80)
        self.assertEqual(row["quality_class"], "good")
        self.assertEqual(row["bars_held"], 3)
        self.assertEqual(row["mfe_pct"], 0.05)
        self.assertEqual(row["opportunity_loss_24h_pct"], 0.06)
        self.assertEqual(row["root_cause"], "early_exit")
        self.assertEqual(row["priority"], "HIGH")
        self.assertEqual(row["regime_aligned"], 1)
        self.assertEqual(row["regime_changed_during_trade"], 1)
        self.assertEqual(row["trade_family_group"], "exit_after_regime_flip")

        payload = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), EXPECTED_ROW_SHA256)
        self.assertEqual(canonical_sha256(list(row), sort_keys=False), EXPECTED_FIELD_ORDER_SHA256)
        self.assertEqual(canonical_sha256(row, sort_keys=False), EXPECTED_ORDERED_ROW_SHA256)

    def test_s4_regime_index_and_feature_matrix(self) -> None:
        for name in [
            "find_matching_entry_exit",
            "build_regime_index",
            "extract_regime_features",
            "compact_trade_time",
            "chart_time",
            "build_trade_id",
            "build_trade_family",
            "build_ml_row",
            "build_rows",
        ]:
            with self.subTest(reexport=name):
                self.assertIs(getattr(inspector, name), getattr(regime_identity_rows, name))
        for registry_name in ["load_label_registry", "save_label_registry", "assign_human_labels"]:
            with self.subTest(registry_boundary=registry_name):
                self.assertFalse(hasattr(regime_identity_rows, registry_name))

        regime_rows = [
            {
                "timestamp_utc": ENTRY_TS,
                "regime_label": "stale",
                "risk_label": "bad_atr",
                "entry_score": "99",
                "ma200_signal": "9",
                "mfi_signal": "9",
                "atr_signal": "9",
            },
            {"timestamp_utc": "", "regime_label": "ignored"},
            {
                "timestamp_utc": ENTRY_TS,
                "regime_label": "bull",
                "risk_label": "good_atr",
                "entry_score": "2",
                "ma200_signal": "1",
                "mfi_signal": "1",
                "atr_signal": "1",
            },
            {
                "timestamp_utc": EXIT_TS,
                "regime_label": "bear",
                "risk_label": "bad_atr",
                "entry_score": "-1",
                "ma200_signal": "-1",
                "mfi_signal": "-1",
                "atr_signal": "-1",
            },
        ]
        regime_index = inspector.build_regime_index(regime_rows)

        self.assertEqual(len(regime_index), 2)
        self.assertIs(regime_index[inspector.ts_key(ENTRY_TS)], regime_rows[2])

        short_trade = dict(sample_trade())
        short_trade["side"] = "short"
        missing_trade = dict(
            sample_trade(),
            entry_timestamp_utc="2026-02-01T00:00:00+00:00",
            exit_timestamp_utc="bad",
        )
        bear_at_entry_index = inspector.build_regime_index(
            [
                dict(regime_rows[3], timestamp_utc=ENTRY_TS),
                dict(regime_rows[2], timestamp_utc=EXIT_TS),
            ]
        )
        cases = {
            "long_aligned_flip": inspector.extract_regime_features(sample_trade(), regime_index),
            "short_counter_flip": inspector.extract_regime_features(short_trade, regime_index),
            "short_aligned_flip": inspector.extract_regime_features(short_trade, bear_at_entry_index),
            "missing": inspector.extract_regime_features(missing_trade, regime_index),
        }

        self.assertEqual(canonical_sha256(cases), S4_REGIME_CASES_SHA256)
        self.assertEqual(cases["long_aligned_flip"]["regime_aligned"], 1)
        self.assertEqual(cases["short_counter_flip"]["regime_aligned"], -1)
        self.assertEqual(cases["short_aligned_flip"]["regime_aligned"], 1)
        self.assertEqual(cases["short_aligned_flip"]["risk_good_at_entry"], 0)
        self.assertEqual(cases["missing"]["has_entry_regime_context"], 0)
        self.assertEqual(cases["missing"]["has_exit_regime_context"], 0)
        self.assertEqual(cases["missing"]["regime_changed_during_trade"], 0)

    def test_s4_time_and_trade_id_formats(self) -> None:
        cases = [
            ("2026-01-01T01:00:00+01:00", "20260101_000000", "2026-01-01 00:00:00 UTC"),
            ("2026-01-01T00:00:00", "20260101_000000", "2026-01-01 00:00:00 UTC"),
            ("bad", "UNKNOWN_TIME", ""),
            (None, "UNKNOWN_TIME", ""),
        ]
        for value, expected_compact, expected_chart in cases:
            with self.subTest(value=value):
                self.assertEqual(inspector.compact_trade_time(value), expected_compact)
                self.assertEqual(inspector.chart_time(value), expected_chart)

        self.assertEqual(
            inspector.build_trade_id(
                {"entry_timestamp_utc": "bad", "side": "", "symbol": ""}
            ),
            "T_UNKNOWN_TIME_UNKNOWN_SIDE_BTCUSDT",
        )
        self.assertEqual(
            inspector.build_trade_id(sample_trade()),
            "T_20260101_000000_LONG_BTCUSDT",
        )

    def test_s4_trade_family_precedence_matrix(self) -> None:
        inputs = {
            "exit_risk_trap": {
                "side": "long",
                "entry_regime_label": "bull",
                "entry_risk_label": "bad_atr",
                "root_cause": "early_exit",
                "regime_changed_during_trade": 1,
                "regime_aligned": 1,
            },
            "exit_after_regime_flip": {
                "side": "long",
                "entry_regime_label": "bull",
                "entry_risk_label": "good_atr",
                "root_cause": "early_exit",
                "regime_changed_during_trade": 1,
                "regime_aligned": 1,
            },
            "aligned_good_risk": {
                "side": "short",
                "entry_regime_label": "bear",
                "entry_risk_label": "good_atr",
                "root_cause": "entry_timing",
                "regime_changed_during_trade": 0,
                "regime_aligned": 1,
            },
            "chop_context": {
                "side": "long",
                "entry_regime_label": "chop",
                "entry_risk_label": "bad_atr",
                "root_cause": "entry_timing",
                "regime_changed_during_trade": 0,
                "regime_aligned": -1,
            },
            "counter_regime": {
                "side": "short",
                "entry_regime_label": "bull",
                "entry_risk_label": "bad_atr",
                "root_cause": "entry_timing",
                "regime_changed_during_trade": 0,
                "regime_aligned": -1,
            },
            "general": {},
        }
        cases = {name: inspector.build_trade_family(row) for name, row in inputs.items()}

        self.assertEqual(canonical_sha256(cases), S4_TRADE_FAMILY_CASES_SHA256)
        for expected_group, result in cases.items():
            with self.subTest(expected_group=expected_group):
                self.assertEqual(result["trade_family_group"], expected_group)
        self.assertEqual(
            cases["general"]["trade_family"],
            "unknown_side_unknown_regime_unknown_risk_unknown_cause_neutral_regime",
        )

    def test_s4_build_rows_preserves_input_identity_and_order(self) -> None:
        long_trade = sample_trade()
        short_trade = dict(sample_trade(), side="short", exit_price=98.0, pnl=2.0, pnl_pct=0.02)
        audit_rows = sample_audit_rows() + [
            {
                "event": "ENTRY_ACCEPTED",
                "timestamp_utc": ENTRY_TS,
                "side": "short",
                "reason": "short_signal",
                "position_before": "FLAT",
                "position_after": "SHORT",
            }
        ]
        timestamps, prices = sample_market_path()
        label_map = {
            inspector.build_trade_id(long_trade): "alpha",
            inspector.build_trade_id(short_trade): "beta",
        }
        rows = inspector.build_rows(
            [long_trade, short_trade],
            audit_rows,
            sample_regime_index(),
            timestamps,
            prices,
            label_map,
        )

        self.assertEqual([row["trade_index"] for row in rows], [1, 2])
        self.assertEqual([row["side"] for row in rows], ["long", "short"])
        self.assertEqual([row["human_label"] for row in rows], ["alpha", "beta"])
        self.assertEqual([row["entry_audit_reason"] for row in rows], ["signal", "short_signal"])
        self.assertEqual([len(row) for row in rows], [127, 127])

        summary = [
            {
                "trade_index": row["trade_index"],
                "trade_id": row["trade_id"],
                "human_label": row["human_label"],
                "side": row["side"],
                "has_entry_audit": row["has_entry_audit"],
                "entry_audit_reason": row["entry_audit_reason"],
                "regime_aligned": row["regime_aligned"],
                "trade_family": row["trade_family"],
                "trade_family_group": row["trade_family_group"],
                "field_order_sha256": canonical_sha256(list(row), sort_keys=False),
                "semantic_sha256": canonical_sha256(row),
            }
            for row in rows
        ]
        self.assertEqual(canonical_sha256(summary), S4_MULTI_ROW_SUMMARY_SHA256)
        self.assertEqual(
            {item["field_order_sha256"] for item in summary},
            {EXPECTED_FIELD_ORDER_SHA256},
        )

    def test_s5_human_label_list_contract(self) -> None:
        for name in [
            "load_human_labels",
            "load_label_registry",
            "save_label_registry",
            "assign_human_labels",
        ]:
            with self.subTest(reexport=name):
                self.assertIs(getattr(inspector, name), getattr(label_registry, name))

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            labels_path = root / "labels.txt"
            labels_path.write_text("# fixture\n\nAlpha\nBETA\n", encoding="utf-8")
            self.assertEqual(inspector.load_human_labels(labels_path), ["alpha", "beta"])

            missing_path = root / "missing.txt"
            with self.assertRaisesRegex(FileNotFoundError, r"Missing human label list:"):
                inspector.load_human_labels(missing_path)

            invalid_cases = [
                ("grün\n", r"Non-ASCII label: grün"),
                ("abcdefghi\n", r"Label too long: abcdefghi"),
                ("two words\n", r"Label too long: two words"),
                ("a b\n", r"Label contains space: a b"),
                ("Alpha\nalpha\n", r"Duplicate label: alpha"),
                ("# only comments\n\n", r"No labels loaded from:"),
            ]
            for content, expected_error in invalid_cases:
                with self.subTest(content=content):
                    labels_path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, expected_error):
                        inspector.load_human_labels(labels_path)

    def test_s5_label_registry_bytes_and_assignment_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            missing_path = root / "missing.csv"
            self.assertEqual(inspector.load_label_registry(missing_path), {})

            input_path = root / "input.csv"
            input_path.write_bytes(
                b"trade_id,human_label\r\n"
                b"T2,BETA\r\n"
                b",alpha\r\n"
                b"T3,\r\n"
                b"T2,GAMMA\r\n"
                b"T1,Alpha\r\n"
            )
            self.assertEqual(
                inspector.load_label_registry(input_path),
                {"T2": "gamma", "T1": "alpha"},
            )

            output_path = root / "nested" / "registry.csv"
            inspector.save_label_registry(output_path, {"T2": "beta", "T1": "alpha"})
            output_bytes = output_path.read_bytes()
            self.assertEqual(output_bytes, b"trade_id,human_label\r\nT1,alpha\r\nT2,beta\r\n")
            self.assertEqual(hashlib.sha256(output_bytes).hexdigest(), S5_REGISTRY_SHA256)

            empty_path = root / "empty.csv"
            inspector.save_label_registry(empty_path, {})
            empty_bytes = empty_path.read_bytes()
            self.assertEqual(empty_bytes, b"trade_id,human_label\r\n")
            self.assertEqual(hashlib.sha256(empty_bytes).hexdigest(), S5_EMPTY_REGISTRY_SHA256)

            trades = [
                dict(sample_trade(), side="long", entry_timestamp_utc="2026-01-01T00:00:00+00:00"),
                dict(sample_trade(), side="short", entry_timestamp_utc="2026-01-01T00:00:00+00:00"),
                dict(sample_trade(), side="long", entry_timestamp_utc="2026-01-01T00:01:00+00:00"),
            ]
            trade_ids = [inspector.build_trade_id(trade) for trade in trades]
            assigned = inspector.assign_human_labels(trades, ["beta"], {trade_ids[1]: "beta"})
            self.assertEqual(
                assigned,
                {
                    trade_ids[0]: "auto_label_000002",
                    trade_ids[1]: "beta",
                    trade_ids[2]: "auto_label_000005",
                },
            )
            self.assertEqual(canonical_sha256(assigned), S5_ASSIGNMENT_SHA256)

            with self.assertRaisesRegex(ValueError, r"Label registry contains duplicate labels"):
                inspector.assign_human_labels(
                    trades,
                    ["alpha", "beta"],
                    {trade_ids[0]: "alpha", trade_ids[1]: "alpha"},
                )

    def test_s5_csv_writer_bytes_and_partial_failure_contract(self) -> None:
        self.assertIs(inspector.write_csv_rows, csv_persistence.write_csv_rows)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            empty_path = root / "nested" / "empty.csv"
            inspector.write_csv_rows(empty_path, [])
            self.assertTrue(empty_path.parent.is_dir())
            self.assertEqual(empty_path.read_bytes(), b"")
            self.assertEqual(
                hashlib.sha256(empty_path.read_bytes()).hexdigest(),
                hashlib.sha256(b"").hexdigest(),
            )

            rows_path = root / "rows.csv"
            rows_path.write_text("stale", encoding="utf-8")
            inspector.write_csv_rows(rows_path, [{"b": "B1", "a": "A1"}, {"b": "B2"}])
            rows_bytes = rows_path.read_bytes()
            self.assertEqual(rows_bytes, b"b,a\r\nB1,A1\r\nB2,\r\n")
            self.assertEqual(hashlib.sha256(rows_bytes).hexdigest(), S5_CSV_ROWS_SHA256)

            partial_path = root / "partial.csv"
            with self.assertRaisesRegex(ValueError, r"dict contains fields not in fieldnames: 'b'"):
                inspector.write_csv_rows(partial_path, [{"a": "1"}, {"a": "2", "b": "3"}])
            partial_bytes = partial_path.read_bytes()
            self.assertEqual(partial_bytes, b"a\r\n1\r\n")
            self.assertEqual(hashlib.sha256(partial_bytes).hexdigest(), S5_PARTIAL_CSV_SHA256)

    def test_s5c_raw_ml_csv_127_field_bytes_parent_overwrite_and_stdout_contract(self) -> None:
        self.assertIs(inspector.export_ml_csv, raw_ml_csv.export_ml_csv)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_path = root / "nested" / "ml.csv"
            self.assertFalse(output_path.parent.exists())

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inspector.export_ml_csv([build_sample_row()], output_path)

            self.assertTrue(output_path.parent.is_dir())
            output_bytes = output_path.read_bytes()
            header = output_bytes.split(b"\r\n", 1)[0]
            self.assertEqual(len(header.split(b",")), 127)
            self.assertEqual(hashlib.sha256(header).hexdigest(), S5_RAW_ML_HEADER_SHA256)
            self.assertEqual(hashlib.sha256(output_bytes).hexdigest(), S5_RAW_ML_CSV_SHA256)
            self.assertEqual(
                output.getvalue(),
                f"ML CSV exported: {output_path}\nrows: 1\n",
            )

            output_path.write_text("stale", encoding="utf-8")
            overwrite_output = io.StringIO()
            with contextlib.redirect_stdout(overwrite_output):
                inspector.export_ml_csv([build_sample_row()], output_path)
            self.assertEqual(hashlib.sha256(output_path.read_bytes()).hexdigest(), S5_RAW_ML_CSV_SHA256)
            self.assertEqual(
                overwrite_output.getvalue(),
                f"ML CSV exported: {output_path}\nrows: 1\n",
            )

    def test_s5c_raw_ml_csv_first_row_schema_missing_field_and_partial_failure_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            rows_path = root / "rows.csv"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                inspector.export_ml_csv(rows=[{"b": "B1", "a": "A1"}, {"b": "B2"}], output_path=rows_path)

            rows_bytes = rows_path.read_bytes()
            self.assertEqual(rows_bytes, b"b,a\r\nB1,A1\r\nB2,\r\n")
            self.assertEqual(hashlib.sha256(rows_bytes).hexdigest(), S5_CSV_ROWS_SHA256)
            self.assertEqual(
                output.getvalue(),
                f"ML CSV exported: {rows_path}\nrows: 2\n",
            )

            partial_path = root / "partial.csv"
            partial_output = io.StringIO()
            with self.assertRaisesRegex(ValueError, r"dict contains fields not in fieldnames: 'b'"):
                with contextlib.redirect_stdout(partial_output):
                    inspector.export_ml_csv(
                        rows=[{"a": "1"}, {"a": "2", "b": "3"}],
                        output_path=partial_path,
                    )
            partial_bytes = partial_path.read_bytes()
            self.assertEqual(partial_bytes, b"a\r\n1\r\n")
            self.assertEqual(hashlib.sha256(partial_bytes).hexdigest(), S5_PARTIAL_CSV_SHA256)
            self.assertEqual(partial_output.getvalue(), "")

    def test_s5c_raw_ml_csv_empty_failure_parent_absence_and_existing_file_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            empty_path = root / "empty" / "ml.csv"
            empty_output = io.StringIO()
            with self.assertRaisesRegex(ValueError, r"^No trades to export\.$"):
                with contextlib.redirect_stdout(empty_output):
                    inspector.export_ml_csv([], empty_path)
            self.assertTrue(empty_path.parent.is_dir())
            self.assertFalse(empty_path.exists())
            self.assertEqual(empty_output.getvalue(), "")

            existing_path = root / "existing" / "ml.csv"
            existing_path.parent.mkdir(parents=True)
            existing_path.write_bytes(b"stale")
            existing_output = io.StringIO()
            with self.assertRaisesRegex(ValueError, r"^No trades to export\.$"):
                with contextlib.redirect_stdout(existing_output):
                    inspector.export_ml_csv([], existing_path)
            self.assertEqual(existing_path.read_bytes(), b"stale")
            self.assertEqual(existing_output.getvalue(), "")

    def test_s5d_aggregate_csv_complete_artifact_manifest_ordering_and_output_contract(self) -> None:
        for name in (
            "avg",
            "group_rows",
            "group_stats",
            "parse_cause_weights",
            "compute_root_cause_attribution",
            "export_root_cause_attribution_csv",
            "aggregate_group_rows",
            "aggregate_top_improvement_rows",
            "export_aggregate_csvs",
        ):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(aggregate_csv, name))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "aggregate"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_aggregate_csvs(s5d_aggregate_rows(), output_dir)

            paths = sorted(output_dir.glob("*.csv"))
            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths
            }
            self.assertEqual(artifact_hashes, S5D_AGGREGATE_ARTIFACT_SHA256)
            self.assertEqual(canonical_sha256(artifact_hashes), S5D_AGGREGATE_MANIFEST_SHA256)

            expected_stdout = (
                f"Aggregate CSV export directory: {output_dir}\n"
                "files:\n"
                + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_hashes))
            )
            self.assertEqual(stdout.getvalue(), expected_stdout)
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "aggregate_top_improvement_candidates.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                self.assertEqual(
                    [row["trade_id"] for row in csv.DictReader(handle)],
                    ["T-C", "T-A", "T-B"],
                )
            with (output_dir / "aggregate_by_root_cause.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                self.assertEqual(
                    [row["group"] for row in csv.DictReader(handle)],
                    ["entry_quality", "early_exit"],
                )
            with (output_dir / "aggregate_root_cause_attribution.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                self.assertEqual(
                    [row["root_cause"] for row in csv.DictReader(handle)],
                    ["early_exit", "regime_mismatch", "entry_quality"],
                )

    def test_s5d_aggregate_csv_empty_input_artifact_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "empty" / "aggregate"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_aggregate_csvs([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            expected_hashes = {
                name: hashlib.sha256(b"").hexdigest()
                for name in S5D_AGGREGATE_ARTIFACT_SHA256
            }
            expected_hashes["aggregate_global_summary.csv"] = S5D_EMPTY_GLOBAL_SUMMARY_SHA256
            self.assertEqual(artifact_hashes, expected_hashes)
            self.assertEqual(canonical_sha256(artifact_hashes), S5D_EMPTY_MANIFEST_SHA256)

            expected_stdout = (
                f"Aggregate CSV export directory: {output_dir}\n"
                "files:\n"
                + "".join(f"- {output_dir / name}\n" for name in sorted(artifact_hashes))
            )
            self.assertEqual(stdout.getvalue(), expected_stdout)
            self.assertEqual(stderr.getvalue(), "")

    def test_s5d_aggregate_csv_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "aggregate"
            output_dir.mkdir(parents=True)
            summary_path = output_dir / "aggregate_global_summary.csv"
            summary_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_aggregate_csvs(s5d_aggregate_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(summary_path.read_bytes()).hexdigest(),
                S5D_AGGREGATE_ARTIFACT_SHA256[summary_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")

            listed_names = sorted([*S5D_AGGREGATE_ARTIFACT_SHA256, foreign_path.name])
            expected_stdout = (
                f"Aggregate CSV export directory: {output_dir}\n"
                "files:\n"
                + "".join(f"- {output_dir / name}\n" for name in listed_names)
            )
            self.assertEqual(stdout.getvalue(), expected_stdout)
            self.assertEqual(stderr.getvalue(), "")

    def test_s5e_ml_dataset_complete_artifact_split_and_output_contract(self) -> None:
        for name in (
            "print_kv",
            "add_ml_targets",
            "dataset_split_from_trade_id",
            "build_ml_dataset_rows",
            "evaluate_split_quality",
            "print_split_quality",
            "export_ml_dataset",
        ):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(ml_dataset, name))

        self.assertEqual(inspector.dataset_split_from_trade_id("A"), "train")
        self.assertEqual(inspector.dataset_split_from_trade_id("K"), "validation")
        self.assertEqual(inspector.dataset_split_from_trade_id("Z"), "test")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "dataset"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_ml_dataset(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5E_ML_DATASET_ARTIFACT_SHA256)
            self.assertEqual(canonical_sha256(artifact_hashes), S5E_ML_DATASET_MANIFEST_SHA256)

            split_quality = {
                "split_quality_status": "PASS",
                "split_quality_warnings": "dataset_too_small_for_reliable_ml",
                "rows_total": 3,
                "rows_train": 1,
                "rows_validation": 1,
                "rows_test": 1,
                "train_share": 1 / 3,
                "validation_share": 1 / 3,
                "test_share": 1 / 3,
            }
            self.assertEqual(
                stdout.getvalue(),
                s5e_expected_stdout(output_dir, list(artifact_hashes), split_quality),
            )
            self.assertEqual(stderr.getvalue(), "")

            expected_ids = {
                "trade_dataset_v4a.csv": ["A", "K", "Z"],
                "trade_dataset_v4a_train.csv": ["A"],
                "trade_dataset_v4a_validation.csv": ["K"],
                "trade_dataset_v4a_test.csv": ["Z"],
            }
            for name, trade_ids in expected_ids.items():
                with self.subTest(artifact=name):
                    with (output_dir / name).open("r", encoding="utf-8", newline="") as handle:
                        rows = list(csv.DictReader(handle))
                    self.assertEqual([row["trade_id"] for row in rows], trade_ids)
                    self.assertEqual(
                        [row["ml_split"] for row in rows],
                        [inspector.dataset_split_from_trade_id(trade_id) for trade_id in trade_ids],
                    )

            with (output_dir / "trade_dataset_v4a_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(len(manifest), 1)
            self.assertEqual(manifest[0]["ml_dataset_version"], "v4a")
            self.assertEqual(manifest[0]["split_quality_status"], "PASS")
            self.assertEqual(manifest[0]["rows_train"], "1")
            self.assertEqual(manifest[0]["rows_validation"], "1")
            self.assertEqual(manifest[0]["rows_test"], "1")

    def test_s5e_ml_dataset_empty_input_artifact_and_warning_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "empty" / "dataset"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_ml_dataset([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            expected_hashes = {
                name: hashlib.sha256(b"").hexdigest()
                for name in S5E_ML_DATASET_ARTIFACT_SHA256
            }
            expected_hashes["trade_dataset_v4a_manifest.csv"] = S5E_EMPTY_ML_MANIFEST_CSV_SHA256
            self.assertEqual(artifact_hashes, expected_hashes)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5E_EMPTY_ML_DATASET_MANIFEST_SHA256,
            )

            split_quality = {
                "split_quality_status": "WARN",
                "split_quality_warnings": (
                    "dataset_too_small_for_reliable_ml|empty_train_split|"
                    "empty_validation_split|empty_test_split"
                ),
                "rows_total": 0,
                "rows_train": 0,
                "rows_validation": 0,
                "rows_test": 0,
                "train_share": 0.0,
                "validation_share": 0.0,
                "test_share": 0.0,
            }
            self.assertEqual(
                stdout.getvalue(),
                s5e_expected_stdout(output_dir, list(artifact_hashes), split_quality),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5e_ml_dataset_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "dataset"
            output_dir.mkdir(parents=True)
            all_path = output_dir / "trade_dataset_v4a.csv"
            all_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_ml_dataset(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(all_path.read_bytes()).hexdigest(),
                S5E_ML_DATASET_ARTIFACT_SHA256[all_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")

            split_quality = {
                "split_quality_status": "PASS",
                "split_quality_warnings": "dataset_too_small_for_reliable_ml",
                "rows_total": 3,
                "rows_train": 1,
                "rows_validation": 1,
                "rows_test": 1,
                "train_share": 1 / 3,
                "validation_share": 1 / 3,
                "test_share": 1 / 3,
            }
            listed_names = [*S5E_ML_DATASET_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5e_expected_stdout(output_dir, listed_names, split_quality),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5f_feature_catalog_encoding_and_missing_value_contract(self) -> None:
        for name in (
            "NON_FEATURE_COLUMNS",
            "TARGET_COLUMNS",
            "is_number_like",
            "build_category_maps",
            "build_feature_catalog",
            "build_model_ready_rows",
            "export_feature_preparation",
        ):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(feature_preparation, name))

        self.assertFalse(inspector.is_number_like(None))
        self.assertFalse(inspector.is_number_like(""))
        self.assertTrue(inspector.is_number_like("1e3"))
        self.assertTrue(inspector.is_number_like("nan"))
        self.assertFalse(inspector.is_number_like("not-a-number"))

        rows = [
            {
                "trade_id": "T1",
                "human_label": "one",
                "ml_split": "train",
                "target_winner": 1,
                "flags": "excluded",
                "numeric": "2.5",
                "sparse_numeric": "",
                "category": "beta",
                "empty_all": "",
            },
            {
                "trade_id": "T2",
                "human_label": "two",
                "ml_split": "validation",
                "target_winner": 0,
                "flags": "excluded",
                "numeric": "",
                "sparse_numeric": "3",
                "category": "alpha",
                "empty_all": "",
                "late_only": "ignored",
            },
            {
                "trade_id": "T3",
                "human_label": "three",
                "ml_split": "test",
                "target_winner": 0,
                "flags": "excluded",
                "numeric": None,
                "sparse_numeric": 4,
                "category": "",
                "empty_all": "",
            },
        ]

        catalog, category_maps = inspector.build_feature_catalog(rows)
        self.assertEqual(
            catalog,
            [
                {
                    "feature_name": "category",
                    "feature_type": "categorical_label_encoded",
                    "encoded_name": "category_encoded",
                    "category_count": 2,
                    "include_for_model": 1,
                },
                {
                    "feature_name": "numeric",
                    "feature_type": "numeric",
                    "encoded_name": "numeric",
                    "category_count": 0,
                    "include_for_model": 1,
                },
                {
                    "feature_name": "sparse_numeric",
                    "feature_type": "numeric",
                    "encoded_name": "sparse_numeric",
                    "category_count": 0,
                    "include_for_model": 1,
                },
            ],
        )
        self.assertEqual(category_maps, {"category": {"alpha": 0, "beta": 1}})

        model_rows, model_catalog = inspector.build_model_ready_rows(rows)
        self.assertEqual(model_catalog, catalog)
        self.assertEqual(
            [
                (
                    row["numeric"],
                    row["sparse_numeric"],
                    row["category_encoded"],
                )
                for row in model_rows
            ],
            [(2.5, 0.0, 1), (0.0, 3.0, 0), (0.0, 4.0, -1)],
        )
        self.assertNotIn("late_only", model_rows[0])
        self.assertNotIn("empty_all", model_rows[0])
        self.assertNotIn("flags", model_rows[0])
        self.assertEqual(
            list(model_rows[0]),
            ["trade_id", "human_label", "ml_split"]
            + sorted(inspector.TARGET_COLUMNS)
            + ["category_encoded", "numeric", "sparse_numeric"],
        )

    def test_s5f_feature_preparation_complete_artifact_schema_split_and_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-preparation"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_preparation(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5F_FEATURE_PREPARATION_ARTIFACT_SHA256)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5F_FEATURE_PREPARATION_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5f_expected_stdout(output_dir, list(artifact_hashes)),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "trade_dataset_v4b_feature_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(
                manifest,
                [{
                    "ml_dataset_version": "v4b",
                    "rows_total": "3",
                    "feature_count": "112",
                    "numeric_feature_count": "90",
                    "categorical_feature_count": "22",
                    "target_count": "16",
                    "purpose": "feature_importance_preparation",
                    "model_training": "not_performed",
                }],
            )

            with (output_dir / "trade_dataset_v4b_feature_catalog.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                catalog = list(csv.DictReader(handle))
            self.assertEqual(len(catalog), 112)
            self.assertEqual(
                [row["encoded_name"] for row in catalog],
                sorted(row["encoded_name"] for row in catalog),
            )

            expected_ids = {
                "trade_dataset_v4b_model_ready.csv": [("A", "train"), ("K", "validation"), ("Z", "test")],
                "trade_dataset_v4b_model_ready_train.csv": [("A", "train")],
                "trade_dataset_v4b_model_ready_validation.csv": [("K", "validation")],
                "trade_dataset_v4b_model_ready_test.csv": [("Z", "test")],
            }
            for name, expected in expected_ids.items():
                with self.subTest(artifact=name):
                    with (output_dir / name).open("r", encoding="utf-8", newline="") as handle:
                        model_rows = list(csv.DictReader(handle))
                    self.assertEqual(
                        [(row["trade_id"], row["ml_split"]) for row in model_rows],
                        expected,
                    )
                    self.assertEqual(len(model_rows[0]), 131)
                    self.assertEqual(
                        list(model_rows[0])[:19],
                        ["trade_id", "human_label", "ml_split"] + sorted(inspector.TARGET_COLUMNS),
                    )

    def test_s5f_feature_preparation_empty_artifact_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "empty" / "feature-preparation"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_preparation([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            expected_hashes = {
                name: hashlib.sha256(b"").hexdigest()
                for name in S5F_FEATURE_PREPARATION_ARTIFACT_SHA256
            }
            expected_hashes["trade_dataset_v4b_feature_manifest.csv"] = (
                S5F_EMPTY_FEATURE_MANIFEST_CSV_SHA256
            )
            self.assertEqual(artifact_hashes, expected_hashes)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5F_EMPTY_FEATURE_PREPARATION_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5f_expected_stdout(output_dir, list(artifact_hashes)),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5f_feature_preparation_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-preparation"
            output_dir.mkdir(parents=True)
            model_path = output_dir / "trade_dataset_v4b_model_ready.csv"
            model_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_preparation(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(model_path.read_bytes()).hexdigest(),
                S5F_FEATURE_PREPARATION_ARTIFACT_SHA256[model_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")
            listed_names = [*S5F_FEATURE_PREPARATION_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5f_expected_stdout(output_dir, listed_names),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5g_leakage_rule_precedence_safe_ids_and_order_contract(self) -> None:
        for name in (
            "HIGH_LEAKAGE_PREFIXES",
            "HIGH_LEAKAGE_EXACT",
            "MEDIUM_LEAKAGE_EXACT",
            "SAFE_ID_COLUMNS",
            "audit_feature_leakage",
            "export_leakage_audit_dataset",
        ):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(leakage_audit, name))

        model_ready_rows = [{
            "trade_id": "T1",
            "human_label": "one",
            "ml_split": "train",
            "target_winner": 1,
            "cf_return_probe": 0.1,
            "pnl": 2.0,
            "duration_sec": 60,
            "entry_price": 100.0,
            "custom_encoded": 2,
        }]

        report, allowed, blocked = inspector.audit_feature_leakage(model_ready_rows)
        self.assertEqual(
            report,
            [
                {
                    "feature_name": "target_winner",
                    "risk_level": "HIGH",
                    "reason": "target_or_future_information",
                    "allowed_for_training": 0,
                },
                {
                    "feature_name": "cf_return_probe",
                    "risk_level": "HIGH",
                    "reason": "target_or_future_information",
                    "allowed_for_training": 0,
                },
                {
                    "feature_name": "pnl",
                    "risk_level": "HIGH",
                    "reason": "post_trade_outcome_or_diagnosis",
                    "allowed_for_training": 0,
                },
                {
                    "feature_name": "duration_sec",
                    "risk_level": "MEDIUM",
                    "reason": "exit_or_in_trade_information",
                    "allowed_for_training": 0,
                },
                {
                    "feature_name": "entry_price",
                    "risk_level": "LOW",
                    "reason": "entry_or_static_feature",
                    "allowed_for_training": 1,
                },
                {
                    "feature_name": "custom_encoded",
                    "risk_level": "LOW",
                    "reason": "entry_or_static_feature",
                    "allowed_for_training": 1,
                },
            ],
        )
        self.assertEqual(allowed, ["entry_price", "custom_encoded"])
        self.assertEqual(blocked, ["target_winner", "cf_return_probe", "pnl", "duration_sec"])
        self.assertEqual(inspector.audit_feature_leakage([]), ([], [], []))

    def test_s5g_leakage_audit_complete_artifact_partition_manifest_and_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "leakage-audit"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_leakage_audit_dataset(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5G_LEAKAGE_AUDIT_ARTIFACT_SHA256)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5G_LEAKAGE_AUDIT_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5g_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    allowed=32,
                    blocked=96,
                    high=86,
                    medium=10,
                    low=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "trade_dataset_v4c_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(
                manifest,
                [{
                    "ml_dataset_version": "v4c",
                    "rows_total": "3",
                    "total_features_audited": "128",
                    "allowed_features": "32",
                    "target_columns": "16",
                    "blocked_features": "96",
                    "high_risk_leakage_features": "86",
                    "medium_risk_leakage_features": "10",
                    "low_risk_features": "32",
                    "high_risk_features_allowed_for_training": "0",
                    "leakage_score": "268",
                    "audit_status": "PASS",
                    "purpose": "dataset_leakage_audit",
                }],
            )

            with (output_dir / "trade_dataset_v4c_leakage_report.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                leakage_report = list(csv.DictReader(handle))
            self.assertEqual(len(leakage_report), 128)
            self.assertEqual(
                {
                    risk: sum(1 for row in leakage_report if row["risk_level"] == risk)
                    for risk in ("HIGH", "MEDIUM", "LOW")
                },
                {"HIGH": 86, "MEDIUM": 10, "LOW": 32},
            )
            self.assertTrue(all(row["allowed_for_training"] == "0" for row in leakage_report if row["risk_level"] != "LOW"))
            self.assertTrue(all(row["allowed_for_training"] == "1" for row in leakage_report if row["risk_level"] == "LOW"))

            expected_shapes = {
                "trade_dataset_v4c_model_ready.csv": 131,
                "trade_dataset_v4c_training_features.csv": 35,
                "trade_dataset_v4c_targets.csv": 19,
                "trade_dataset_v4c_blocked_features.csv": 99,
            }
            for name, column_count in expected_shapes.items():
                with self.subTest(artifact=name):
                    with (output_dir / name).open("r", encoding="utf-8", newline="") as handle:
                        artifact_rows = list(csv.DictReader(handle))
                    self.assertEqual(len(artifact_rows), 3)
                    self.assertEqual(len(artifact_rows[0]), column_count)
                    self.assertEqual(
                        [(row["trade_id"], row["ml_split"]) for row in artifact_rows],
                        [("A", "train"), ("K", "validation"), ("Z", "test")],
                    )

    def test_s5g_leakage_audit_empty_artifact_and_pass_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "empty" / "leakage-audit"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_leakage_audit_dataset([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            expected_hashes = {
                name: hashlib.sha256(b"").hexdigest()
                for name in S5G_LEAKAGE_AUDIT_ARTIFACT_SHA256
            }
            expected_hashes["trade_dataset_v4c_manifest.csv"] = (
                S5G_EMPTY_LEAKAGE_MANIFEST_CSV_SHA256
            )
            self.assertEqual(artifact_hashes, expected_hashes)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5G_EMPTY_LEAKAGE_AUDIT_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5g_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    allowed=0,
                    blocked=0,
                    high=0,
                    medium=0,
                    low=0,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5g_leakage_audit_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "leakage-audit"
            output_dir.mkdir(parents=True)
            report_path = output_dir / "trade_dataset_v4c_leakage_report.csv"
            report_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_leakage_audit_dataset(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(report_path.read_bytes()).hexdigest(),
                S5G_LEAKAGE_AUDIT_ARTIFACT_SHA256[report_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")
            listed_names = [*S5G_LEAKAGE_AUDIT_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5g_expected_stdout(
                    output_dir,
                    listed_names,
                    allowed=32,
                    blocked=96,
                    high=86,
                    medium=10,
                    low=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5h_pearson_join_ranking_tie_and_degenerate_contract(self) -> None:
        for name in ("pearson_abs", "feature_importance_rows", "export_feature_importance"):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(feature_importance, name))

        self.assertEqual(inspector.pearson_abs([], []), 0.0)
        self.assertEqual(inspector.pearson_abs([1.0], [1.0]), 0.0)
        self.assertEqual(inspector.pearson_abs([1.0, 2.0], [1.0]), 0.0)
        self.assertEqual(inspector.pearson_abs([7.0, 7.0], [1.0, 2.0]), 0.0)
        self.assertAlmostEqual(inspector.pearson_abs([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]), 1.0)
        self.assertAlmostEqual(inspector.pearson_abs([1.0, 2.0, 3.0], [3.0, 2.0, 1.0]), 1.0)

        training_rows = [
            {"trade_id": "A", "human_label": "a", "ml_split": "train", "first": 1, "second": 3, "constant": 7},
            {"trade_id": "B", "human_label": "b", "ml_split": "train", "first": 2, "second": 2, "constant": 7},
            {"trade_id": "C", "human_label": "c", "ml_split": "test", "first": 3, "second": 1, "constant": 7},
            {"trade_id": "UNMATCHED", "human_label": "d", "ml_split": "test", "first": 100, "second": 100, "constant": 7},
        ]
        target_rows = [
            {"trade_id": "A", "target": 1},
            {"trade_id": "B", "target": 2},
            {"trade_id": "C", "target": 3},
        ]

        importance = inspector.feature_importance_rows(training_rows, target_rows, "target")
        self.assertEqual([row["feature_name"] for row in importance], ["first", "second", "constant"])
        self.assertEqual([row["rows_used"] for row in importance], [3, 3, 3])
        self.assertTrue(all(row["target_column"] == "target" for row in importance))
        self.assertTrue(all(row["method"] == "absolute_pearson_correlation" for row in importance))
        self.assertAlmostEqual(importance[0]["importance_score"], 1.0)
        self.assertAlmostEqual(importance[1]["importance_score"], 1.0)
        self.assertEqual(importance[2]["importance_score"], 0.0)
        self.assertEqual(inspector.feature_importance_rows([], target_rows, "target"), [])

    def test_s5h_feature_importance_complete_artifacts_targets_manifest_and_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-importance"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_importance(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5H_FEATURE_IMPORTANCE_ARTIFACT_SHA256)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5H_FEATURE_IMPORTANCE_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5h_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_feature_importance",
                    rows_total=3,
                    allowed_features=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "feature_importance_v5_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(
                manifest,
                [{
                    "engine_version": "v5",
                    "rows_total": "3",
                    "allowed_features": "32",
                    "targets_evaluated": "9",
                    "method": "absolute_pearson_correlation",
                    "model_training": "not_performed",
                    "feature_importance_status": "WARN",
                    "feature_importance_warning": "dataset_too_small_for_reliable_feature_importance",
                }],
            )

            with (output_dir / "feature_importance_v5.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                combined = list(csv.DictReader(handle))
            expected_targets = [
                "target_winner",
                "target_loser",
                "target_quality_good",
                "target_quality_bad",
                "target_opportunity_loss_high",
                "target_exit_efficiency_high",
                "target_pnl_pct",
                "target_future_return_24h_pct",
                "target_future_return_72h_pct",
            ]
            self.assertEqual(len(combined), 288)
            self.assertEqual(
                list(dict.fromkeys(row["target_column"] for row in combined)),
                expected_targets,
            )
            self.assertEqual(
                {target: sum(1 for row in combined if row["target_column"] == target) for target in expected_targets},
                {target: 32 for target in expected_targets},
            )
            for target in expected_targets:
                with self.subTest(target=target):
                    with (output_dir / f"feature_importance_v5_{target}.csv").open(
                        "r", encoding="utf-8", newline=""
                    ) as handle:
                        target_rows = list(csv.DictReader(handle))
                    self.assertEqual(len(target_rows), 32)
                    self.assertTrue(all(row["target_column"] == target for row in target_rows))

    def test_s5h_feature_importance_empty_artifact_and_warn_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "empty" / "feature-importance"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_importance([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            expected_hashes = {
                name: hashlib.sha256(b"").hexdigest()
                for name in S5H_FEATURE_IMPORTANCE_ARTIFACT_SHA256
            }
            expected_hashes["feature_importance_v5_manifest.csv"] = (
                S5H_EMPTY_FEATURE_IMPORTANCE_MANIFEST_CSV_SHA256
            )
            self.assertEqual(artifact_hashes, expected_hashes)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5H_EMPTY_FEATURE_IMPORTANCE_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5h_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_feature_importance",
                    rows_total=0,
                    allowed_features=0,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5h_feature_importance_exact_30_row_pass_boundary(self) -> None:
        base = s5e_ml_dataset_rows()[0]
        rows = []
        for index in range(30):
            row = dict(base)
            row["trade_id"] = f"BOUNDARY-{index:02d}"
            row["human_label"] = f"boundary-{index:02d}"
            rows.append(row)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-importance"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_importance(rows, output_dir)

            with (output_dir / "feature_importance_v5_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(manifest[0]["rows_total"], "30")
            self.assertEqual(manifest[0]["feature_importance_status"], "PASS")
            self.assertEqual(manifest[0]["feature_importance_warning"], "none")
            self.assertIn("feature_importance_status: PASS\n", stdout.getvalue())
            self.assertIn("feature_importance_warning: none\n", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

    def test_s5h_feature_importance_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-importance"
            output_dir.mkdir(parents=True)
            combined_path = output_dir / "feature_importance_v5.csv"
            combined_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_importance(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(combined_path.read_bytes()).hexdigest(),
                S5H_FEATURE_IMPORTANCE_ARTIFACT_SHA256[combined_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")
            listed_names = [*S5H_FEATURE_IMPORTANCE_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5h_expected_stdout(
                    output_dir,
                    listed_names,
                    status="WARN",
                    warning="dataset_too_small_for_reliable_feature_importance",
                    rows_total=3,
                    allowed_features=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5i_statistics_and_stability_class_boundaries(self) -> None:
        for name in ("median", "std", "stability_class", "export_feature_stability"):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(feature_stability, name))

        self.assertEqual(inspector.median([]), 0.0)
        self.assertEqual(inspector.median([3.0]), 3.0)
        self.assertEqual(inspector.median([3.0, 1.0, 2.0]), 2.0)
        self.assertEqual(inspector.median([4.0, 1.0, 3.0, 2.0]), 2.5)

        self.assertEqual(inspector.std([]), 0.0)
        self.assertEqual(inspector.std([3.0]), 0.0)
        self.assertAlmostEqual(inspector.std([1.0, 3.0]), 2.0 ** 0.5)
        self.assertAlmostEqual(inspector.std([1.0, 2.0, 3.0]), 1.0)

        cases = [
            (-1.0, "unstable"),
            (0.0, "unstable"),
            (24.999, "unstable"),
            (25.0, "weak"),
            (49.999, "weak"),
            (50.0, "moderate"),
            (74.999, "moderate"),
            (75.0, "stable"),
            (89.999, "stable"),
            (90.0, "elite"),
            (100.0, "elite"),
            (101.0, "elite"),
        ]
        for score, expected in cases:
            with self.subTest(score=score):
                self.assertEqual(inspector.stability_class(score), expected)

    def test_s5i_feature_stability_complete_artifact_matrix_manifest_and_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-stability"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_stability(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5I_FEATURE_STABILITY_ARTIFACT_SHA256)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5I_FEATURE_STABILITY_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5i_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_stability",
                    rows_total=3,
                    features_analyzed=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "feature_stability_v5c_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(
                manifest,
                [{
                    "engine_version": "v5c",
                    "rows_total": "3",
                    "features_analyzed": "32",
                    "targets_analyzed": "9",
                    "elite_features": "0",
                    "stable_features": "0",
                    "moderate_features": "0",
                    "weak_features": "10",
                    "unstable_features": "22",
                    "stability_status": "WARN",
                    "stability_warning": "dataset_too_small_for_reliable_stability",
                    "method": "multi_target_absolute_pearson_stability",
                }],
            )

            with (output_dir / "feature_stability_v5c.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                stability_rows = list(csv.DictReader(handle))
            self.assertEqual(len(stability_rows), 32)
            self.assertEqual(
                list(stability_rows[0]),
                [
                    "feature_name",
                    "importance_mean",
                    "importance_median",
                    "importance_std",
                    "rank_mean",
                    "rank_std",
                    "target_count",
                    "top10_count",
                    "top20_count",
                    "stability_score",
                    "stability_class",
                ],
            )
            self.assertEqual(len({row["feature_name"] for row in stability_rows}), 32)
            self.assertTrue(all(row["target_count"] == "9" for row in stability_rows))
            self.assertEqual(sum(int(row["top10_count"]) for row in stability_rows), 90)
            self.assertEqual(sum(int(row["top20_count"]) for row in stability_rows), 180)
            self.assertEqual(
                [float(row["stability_score"]) for row in stability_rows],
                sorted(
                    [float(row["stability_score"]) for row in stability_rows],
                    reverse=True,
                ),
            )

            with (output_dir / "feature_stability_v5c_target_matrix.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                matrix_rows = list(csv.DictReader(handle))
            self.assertEqual(len(matrix_rows), 32)
            self.assertEqual(
                [row["feature_name"] for row in matrix_rows],
                sorted(row["feature_name"] for row in matrix_rows),
            )
            targets = [
                "target_winner",
                "target_loser",
                "target_quality_good",
                "target_quality_bad",
                "target_opportunity_loss_high",
                "target_exit_efficiency_high",
                "target_pnl_pct",
                "target_future_return_24h_pct",
                "target_future_return_72h_pct",
            ]
            expected_matrix_columns = ["feature_name"]
            for target in targets:
                expected_matrix_columns.extend([target, f"{target}_rank"])
            self.assertEqual(list(matrix_rows[0]), expected_matrix_columns)

    def test_s5i_feature_stability_empty_artifact_and_warn_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-stability"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_stability([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(set(artifact_hashes), set(S5I_FEATURE_STABILITY_ARTIFACT_SHA256))
            self.assertEqual(
                artifact_hashes["feature_stability_v5c_manifest.csv"],
                S5I_EMPTY_FEATURE_STABILITY_MANIFEST_CSV_SHA256,
            )
            self.assertEqual(
                artifact_hashes["feature_stability_v5c.csv"],
                hashlib.sha256(b"").hexdigest(),
            )
            self.assertEqual(
                artifact_hashes["feature_stability_v5c_target_matrix.csv"],
                hashlib.sha256(b"").hexdigest(),
            )
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5I_EMPTY_FEATURE_STABILITY_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5i_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_stability",
                    rows_total=0,
                    features_analyzed=0,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "feature_stability_v5c_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(manifest[0]["features_analyzed"], "0")
            self.assertEqual(manifest[0]["targets_analyzed"], "9")
            self.assertEqual(manifest[0]["stability_status"], "WARN")
            self.assertEqual(
                manifest[0]["stability_warning"],
                "dataset_too_small_for_reliable_stability",
            )

    def test_s5i_feature_stability_exact_30_row_pass_boundary(self) -> None:
        base = s5e_ml_dataset_rows()[0]
        rows = []
        for index in range(30):
            row = dict(base)
            row["trade_id"] = f"BOUNDARY-{index:02d}"
            row["human_label"] = f"boundary-{index:02d}"
            rows.append(row)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-stability"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_stability(rows, output_dir)

            with (output_dir / "feature_stability_v5c_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(manifest[0]["rows_total"], "30")
            self.assertEqual(manifest[0]["stability_status"], "PASS")
            self.assertEqual(manifest[0]["stability_warning"], "none")
            self.assertIn("stability_status: PASS\n", stdout.getvalue())
            self.assertIn("stability_warning: none\n", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

    def test_s5i_feature_stability_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-stability"
            output_dir.mkdir(parents=True)
            stability_path = output_dir / "feature_stability_v5c.csv"
            stability_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_feature_stability(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(stability_path.read_bytes()).hexdigest(),
                S5I_FEATURE_STABILITY_ARTIFACT_SHA256[stability_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")
            listed_names = [*S5I_FEATURE_STABILITY_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5i_expected_stdout(
                    output_dir,
                    listed_names,
                    status="WARN",
                    warning="dataset_too_small_for_reliable_stability",
                    rows_total=3,
                    features_analyzed=32,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5j_signal_group_scoring_support_reliability_and_pair_contract(self) -> None:
        for name in (
            "safe_rate",
            "discover_signal_groups",
            "classify_signal_support",
            "classify_signal_reliability",
            "discover_pair_groups",
            "export_predictive_signal_discovery",
        ):
            with self.subTest(binding=name):
                self.assertIs(getattr(inspector, name), getattr(feature_discovery, name))

        self.assertEqual(inspector.safe_rate(3.0, 2.0), 1.5)
        self.assertEqual(inspector.safe_rate(3.0, 0.0), 0.0)

        support_cases = [
            (0, "VERY_LOW"),
            (2, "VERY_LOW"),
            (3, "LOW"),
            (9, "LOW"),
            (10, "MEDIUM"),
            (29, "MEDIUM"),
            (30, "HIGH"),
        ]
        for count, expected in support_cases:
            with self.subTest(count=count):
                self.assertEqual(inspector.classify_signal_support(count), expected)

        reliability_cases = [
            ((29, 30, "PROMISING"), (0, "NOT_ACTIONABLE", "DATASET_TOO_SMALL", 30)),
            ((30, 0, "PROMISING"), (30, "NOT_ACTIONABLE", "HIGH", 30)),
            ((301, 30, "PROMISING"), (70, "ACTIONABLE_CANDIDATE", "LOW", 30)),
            ((101, 10, "WATCH"), (40, "WATCH_ONLY", "MEDIUM", 30)),
            ((100, 10, "WATCH"), (50, "WATCH_ONLY", "MEDIUM", 30)),
            ((30, 3, "PROMISING"), (50, "WATCH_ONLY", "MEDIUM", 30)),
        ]
        for args, expected in reliability_cases:
            with self.subTest(args=args):
                self.assertEqual(inspector.classify_signal_reliability(*args), expected)

        rows = []
        for index in range(3):
            rows.append({
                "signal": "A",
                "pair": "X",
                "is_winner": 1,
                "pnl": 10.0,
                "pnl_pct": 0.1,
                "opportunity_loss_24h_pct": 0.0,
                "exit_efficiency_24h_pct": 1.0,
            })
            rows.append({
                "signal": "B",
                "pair": "Y",
                "is_winner": 0,
                "pnl": -10.0,
                "pnl_pct": -0.1,
                "opportunity_loss_24h_pct": 1.0,
                "exit_efficiency_24h_pct": 0.0,
            })

        groups = inspector.discover_signal_groups(rows, "signal")
        self.assertEqual([row["group"] for row in groups], ["A", "B"])
        self.assertEqual([row["discovery_status"] for row in groups], ["PROMISING", "WEAK"])
        self.assertEqual([row["discovery_score"] for row in groups], [100.0, 10.5])
        self.assertTrue(all(row["support_class"] == "LOW" for row in groups))
        self.assertTrue(all(row["reliability_score"] == 0 for row in groups))
        self.assertTrue(all(row["warning_level"] == "DATASET_TOO_SMALL" for row in groups))

        pairs = inspector.discover_pair_groups(rows, "signal", "pair")
        self.assertEqual([row["group"] for row in pairs], ["A__X", "B__Y"])
        self.assertTrue(all(row["group_key"] == "signal__pair" for row in pairs))
        self.assertTrue(all("signal__pair" not in row for row in rows))

    def test_s5j_feature_discovery_complete_artifacts_manifest_and_output_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-discovery"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_predictive_signal_discovery(s5e_ml_dataset_rows(), output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(artifact_hashes, S5J_FEATURE_DISCOVERY_ARTIFACT_SHA256)
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5J_FEATURE_DISCOVERY_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5j_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_signal_discovery",
                    rows_total=3,
                    groups_evaluated=16,
                    promising=0,
                    watch=0,
                    low_support=0,
                    not_actionable=16,
                    watch_only=0,
                    actionable=0,
                    high_warning=16,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

            with (output_dir / "predictive_signal_discovery_v6_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(
                manifest,
                [{
                    "engine_version": "v6a",
                    "rows_total": "3",
                    "groups_evaluated": "16",
                    "promising_groups": "0",
                    "watch_groups": "0",
                    "low_support_groups": "0",
                    "not_actionable_groups": "16",
                    "watch_only_groups": "0",
                    "actionable_candidate_groups": "0",
                    "high_warning_groups": "16",
                    "minimum_required_support": "30",
                    "discovery_status": "WARN",
                    "discovery_warning": "dataset_too_small_for_reliable_signal_discovery",
                    "method": "group_edge_vs_global_baseline_with_reliability_layer",
                }],
            )

            with (output_dir / "predictive_signal_discovery_v6_all.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                all_rows = list(csv.DictReader(handle))
            with (output_dir / "predictive_signal_discovery_v6_top.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                top_rows = list(csv.DictReader(handle))
            self.assertEqual(len(all_rows), 16)
            self.assertEqual(top_rows, all_rows)
            self.assertEqual(
                [float(row["discovery_score"]) for row in all_rows],
                sorted(
                    [float(row["discovery_score"]) for row in all_rows],
                    reverse=True,
                ),
            )
            self.assertTrue(all(row["support_class"] == "LOW" for row in all_rows))
            self.assertTrue(all(row["reliability_class"] == "NOT_ACTIONABLE" for row in all_rows))
            self.assertTrue(all(row["warning_level"] == "DATASET_TOO_SMALL" for row in all_rows))

    def test_s5j_feature_discovery_empty_artifact_and_warn_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-discovery"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_predictive_signal_discovery([], output_dir)

            artifact_hashes = {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output_dir.glob("*.csv"))
            }
            self.assertEqual(set(artifact_hashes), set(S5J_FEATURE_DISCOVERY_ARTIFACT_SHA256))
            self.assertEqual(
                artifact_hashes["predictive_signal_discovery_v6_manifest.csv"],
                S5J_EMPTY_FEATURE_DISCOVERY_MANIFEST_CSV_SHA256,
            )
            for name, digest in artifact_hashes.items():
                if name != "predictive_signal_discovery_v6_manifest.csv":
                    self.assertEqual(digest, hashlib.sha256(b"").hexdigest())
            self.assertEqual(
                canonical_sha256(artifact_hashes),
                S5J_EMPTY_FEATURE_DISCOVERY_MANIFEST_SHA256,
            )
            self.assertEqual(
                stdout.getvalue(),
                s5j_expected_stdout(
                    output_dir,
                    list(artifact_hashes),
                    status="WARN",
                    warning="dataset_too_small_for_reliable_signal_discovery",
                    rows_total=0,
                    groups_evaluated=0,
                    promising=0,
                    watch=0,
                    low_support=0,
                    not_actionable=0,
                    watch_only=0,
                    actionable=0,
                    high_warning=0,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s5j_feature_discovery_exact_30_row_pass_and_top_50_boundary(self) -> None:
        base = s5e_ml_dataset_rows()[0]
        group_keys = [
            "entry_regime_label",
            "entry_risk_label",
            "regime_aligned",
            "risk_good_at_entry",
            "entry_score_at_entry",
            "entry_atr_signal",
            "entry_ma200_signal",
            "entry_mfi_signal",
            "trade_family_group",
            "trade_family",
        ]
        rows = []
        for index in range(30):
            row = dict(base)
            row["trade_id"] = f"BOUNDARY-{index:02d}"
            for key in group_keys:
                row[key] = f"{key}-{index:02d}"
            rows.append(row)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-discovery"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_predictive_signal_discovery(rows, output_dir)

            with (output_dir / "predictive_signal_discovery_v6_manifest.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                manifest = list(csv.DictReader(handle))
            self.assertEqual(manifest[0]["rows_total"], "30")
            self.assertEqual(manifest[0]["groups_evaluated"], "480")
            self.assertEqual(manifest[0]["low_support_groups"], "480")
            self.assertEqual(manifest[0]["not_actionable_groups"], "480")
            self.assertEqual(manifest[0]["high_warning_groups"], "480")
            self.assertEqual(manifest[0]["discovery_status"], "PASS")
            self.assertEqual(manifest[0]["discovery_warning"], "none")

            with (output_dir / "predictive_signal_discovery_v6_all.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                all_rows = list(csv.DictReader(handle))
            with (output_dir / "predictive_signal_discovery_v6_top.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                top_rows = list(csv.DictReader(handle))
            self.assertEqual(len(all_rows), 480)
            self.assertEqual(len(top_rows), 50)
            self.assertEqual(top_rows, all_rows[:50])
            self.assertIn("discovery_status: PASS\n", stdout.getvalue())
            self.assertIn("discovery_warning: none\n", stdout.getvalue())
            self.assertEqual(stderr.getvalue(), "")

    def test_s5j_feature_discovery_overwrite_and_foreign_csv_listing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "feature-discovery"
            output_dir.mkdir(parents=True)
            all_path = output_dir / "predictive_signal_discovery_v6_all.csv"
            all_path.write_bytes(b"stale")
            foreign_path = output_dir / "foreign.csv"
            foreign_path.write_bytes(b"foreign")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                inspector.export_predictive_signal_discovery(s5e_ml_dataset_rows(), output_dir)

            self.assertEqual(
                hashlib.sha256(all_path.read_bytes()).hexdigest(),
                S5J_FEATURE_DISCOVERY_ARTIFACT_SHA256[all_path.name],
            )
            self.assertEqual(foreign_path.read_bytes(), b"foreign")
            listed_names = [*S5J_FEATURE_DISCOVERY_ARTIFACT_SHA256, foreign_path.name]
            self.assertEqual(
                stdout.getvalue(),
                s5j_expected_stdout(
                    output_dir,
                    listed_names,
                    status="WARN",
                    warning="dataset_too_small_for_reliable_signal_discovery",
                    rows_total=3,
                    groups_evaluated=16,
                    promising=0,
                    watch=0,
                    low_support=0,
                    not_actionable=16,
                    watch_only=0,
                    actionable=0,
                    high_warning=16,
                ),
            )
            self.assertEqual(stderr.getvalue(), "")

    def test_s3_long_path_and_diagnosis_snapshot(self) -> None:
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(sample_trade(), timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["long"])
        self.assertEqual(snapshot["quality"]["score"], 80)
        self.assertEqual(snapshot["path"]["mfe_pct"], 0.05)
        self.assertEqual(snapshot["diagnosis"]["root_cause"], "early_exit")
        self.assertEqual(snapshot["confidence"]["priority"], "HIGH")

    def test_s3_short_path_and_diagnosis_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade.update({"side": "short", "exit_price": 98.0})
        timestamps, prices = sample_short_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["short"])
        self.assertEqual(inspector.trade_pnl_from_price("short", 100.0, 95.0), 5.0)
        self.assertEqual(snapshot["path"]["best_price_during_trade"], 95.0)
        self.assertEqual(snapshot["path"]["worst_price_during_trade"], 100.0)
        self.assertEqual(snapshot["path"]["mfe_pct"], 0.05)

    def test_s3_missing_path_snapshot(self) -> None:
        snapshot = build_s3_snapshot(sample_trade(), [], [])

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["missing_path"])
        self.assertEqual(snapshot["path"]["path_available"], 0)
        self.assertEqual(snapshot["confidence"]["diagnosis_reliability"], 60)
        for label in inspector.FUTURE_WINDOWS_MIN:
            self.assertEqual(snapshot["counterfactuals"][f"counterfactual_available_{label}"], 0)

    def test_s3_zero_pnl_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade.update({"exit_price": 100.0, "pnl": 0.0, "pnl_pct": 0.0})
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["zero_pnl"])
        self.assertEqual(snapshot["quality_flags"], ["flat_trade"])
        self.assertEqual(snapshot["quality"]["score"], 60)
        self.assertEqual(snapshot["quality"]["band"], "acceptable")
        self.assertEqual(snapshot["counterfactuals"]["exit_efficiency_24h_pct"], 0.0)
        self.assertEqual(snapshot["counterfactuals"]["opportunity_loss_24h_pct"], 0.08)

    def test_s3_invalid_duration_snapshot(self) -> None:
        trade = dict(sample_trade())
        trade["duration_sec"] = -1
        timestamps, prices = sample_market_path()
        snapshot = build_s3_snapshot(trade, timestamps, prices)

        self.assertEqual(s3_snapshot_sha256(snapshot), S3_SCENARIO_SHA256["invalid_duration"])
        self.assertEqual(snapshot["quality_flags"], ["negative_duration", "very_short_trade"])
        self.assertEqual(snapshot["quality"]["score"], 20)
        self.assertEqual(snapshot["quality"]["band"], "bad")
        self.assertEqual(snapshot["quality"]["negatives"], ["invalid_duration"])

    def test_s3_score_and_direction_boundaries(self) -> None:
        self.assertIs(inspector.FUTURE_WINDOWS_MIN, path_diagnosis.FUTURE_WINDOWS_MIN)
        for name in [
            "quality_flags",
            "score_band",
            "signed_diagnosis",
            "trade_pnl_from_price",
            "calculate_trade_path",
            "calculate_counterfactuals",
            "compute_quality_score",
            "interpretation_flags",
            "compute_diagnosis",
            "compute_confidence_layer",
        ]:
            with self.subTest(reexport=name):
                self.assertIs(getattr(inspector, name), getattr(path_diagnosis, name))

        cases = [
            (39, "bad", -1),
            (40, "weak", 0),
            (59, "weak", 0),
            (60, "acceptable", 0),
            (74, "acceptable", 0),
            (75, "good", 1),
            (89, "good", 1),
            (90, "excellent", 1),
        ]
        for score, expected_band, expected_diagnosis in cases:
            with self.subTest(score=score):
                self.assertEqual(inspector.score_band(score), expected_band)
                self.assertEqual(inspector.signed_diagnosis(score), expected_diagnosis)

        self.assertEqual(inspector.trade_pnl_from_price("long", 100.0, 105.0), 5.0)
        self.assertEqual(inspector.trade_pnl_from_price("short", 100.0, 95.0), 5.0)
        self.assertEqual(inspector.trade_pnl_from_price("unknown", 100.0, 105.0), 0.0)

    def test_missing_market_path_remains_explicitly_unavailable(self) -> None:
        trade = sample_trade()
        path = inspector.calculate_trade_path(trade, [], [])
        counterfactuals = inspector.calculate_counterfactuals(trade, [], [])

        self.assertEqual(path["path_available"], 0)
        self.assertEqual(path["bars_held"], 0)
        for label in inspector.FUTURE_WINDOWS_MIN:
            self.assertEqual(counterfactuals[f"counterfactual_available_{label}"], 0)
            self.assertEqual(counterfactuals[f"cf_return_{label}_pct"], 0.0)

    def test_archive_intake_fails_closed_on_bad_json_and_count_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir)
            (archive_dir / "trades_l1.jsonl").write_text('{"id": 1}\nnot-json\n', encoding="utf-8")
            (archive_dir / "execution_audit.jsonl").write_text('{"event": "ENTRY_ACCEPTED"}\n', encoding="utf-8")
            (archive_dir / "l1_paper.log").write_text("", encoding="utf-8")
            metadata = {
                "archive_id": "fixture",
                "archive_path": str(archive_dir),
                "created_at": "2026-01-01T00:00:00+00:00",
                "source_device": "X1",
                "run_type": "characterization",
                "strategy_profile": "fixture",
                "market_symbol": "BTCUSDT",
                "market_csv": "fixture.csv",
                "seeds_5m_csv": "fixture.csv",
                "max_ticks": 1,
                "tick_offset": 0,
                "decision_tick_seconds": 60,
                "start_time_utc": ENTRY_TS,
                "end_time_utc": EXIT_TS,
                "trade_count": 2,
                "audit_event_count": 1,
                "status": "validated",
                "notes": "hermetic characterization fixture",
            }
            (archive_dir / "archive_metadata.json").write_text(
                json.dumps(metadata, sort_keys=True),
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = inspector.run_archive_intake_validation(SimpleNamespace(archive_dir=str(archive_dir)))

            self.assertEqual(result, 1)
            self.assertIn("ARCHIVE_INTAKE: FAIL", output.getvalue())
            self.assertIn("trades_l1.jsonl bad JSON lines: 1", output.getvalue())
            self.assertIn("metadata trade_count mismatch", output.getvalue())

            ordered_diagnostics = [
                line
                for line in output.getvalue().splitlines()
                if line.startswith(("CHECK warnings:", "WARNING:", "ARCHIVE_INTAKE:", "ERROR:"))
            ]
            self.assertEqual(
                ordered_diagnostics,
                [
                    "CHECK warnings: 5",
                    "WARNING: optional file missing: trade_lifecycle_snapshots.csv",
                    "WARNING: optional file missing: monitor_status.json",
                    "WARNING: optional file missing: runtime_control.json",
                    "WARNING: optional file missing: loss_cluster_state.json",
                    "WARNING: optional file missing: trades_l1_auto_analysis.csv",
                    "ARCHIVE_INTAKE: FAIL",
                    "ERROR: trades_l1.jsonl bad JSON lines: 1",
                    "ERROR: metadata trade_count mismatch: metadata=2 actual=1",
                ],
            )

    def test_archive_intake_complete_fixture_passes_without_warnings(self) -> None:
        self.assertIs(inspector.count_valid_jsonl, intake.count_valid_jsonl)
        self.assertIs(inspector.run_archive_intake_validation, intake.run_archive_intake_validation)

        with tempfile.TemporaryDirectory() as temp_dir:
            archive_dir = Path(temp_dir)
            trades = [{"id": 1}, {"id": 2}]
            audit_rows = [{"event": "ENTRY_ACCEPTED"}, {"event": "EXIT_EXECUTED"}]

            (archive_dir / "trades_l1.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in trades),
                encoding="utf-8",
            )
            (archive_dir / "execution_audit.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in audit_rows),
                encoding="utf-8",
            )
            (archive_dir / "l1_paper.log").write_text("", encoding="utf-8")

            for name in [
                "trade_lifecycle_snapshots.csv",
                "monitor_status.json",
                "runtime_control.json",
                "loss_cluster_state.json",
                "trades_l1_auto_analysis.csv",
            ]:
                (archive_dir / name).write_text("", encoding="utf-8")

            metadata = {
                "archive_id": "fixture-pass",
                "archive_path": str(archive_dir),
                "created_at": "2026-01-01T00:00:00+00:00",
                "source_device": "X1",
                "run_type": "characterization",
                "strategy_profile": "fixture",
                "market_symbol": "BTCUSDT",
                "market_csv": "fixture.csv",
                "seeds_5m_csv": "fixture.csv",
                "max_ticks": 2,
                "tick_offset": 0,
                "decision_tick_seconds": 60,
                "start_time_utc": ENTRY_TS,
                "end_time_utc": EXIT_TS,
                "trade_count": len(trades),
                "audit_event_count": len(audit_rows),
                "status": "validated",
                "notes": "complete hermetic characterization fixture",
            }
            (archive_dir / "archive_metadata.json").write_text(
                json.dumps(metadata, sort_keys=True),
                encoding="utf-8",
            )

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = inspector.run_archive_intake_validation(SimpleNamespace(archive_dir=str(archive_dir)))

            self.assertEqual(result, 0)
            self.assertEqual(
                output.getvalue(),
                "\n".join(
                    [
                        "TRADE INSPECTOR V7I ARCHIVE INTAKE VALIDATION",
                        f"archive_dir: {archive_dir}",
                        "",
                        "CHECK required_files: PASS",
                        "CHECK archive_metadata_json: PASS",
                        "CHECK archive_id: fixture-pass",
                        "CHECK trades_valid_jsonl: 2",
                        "CHECK trades_bad_jsonl: 0",
                        "CHECK audit_valid_jsonl: 2",
                        "CHECK audit_bad_jsonl: 0",
                        "CHECK warnings: 0",
                        "",
                        "ARCHIVE_INTAKE: PASS",
                        "",
                    ]
                ),
            )

    def test_summary_cli_is_hermetic_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_dir = root / "archive"
            archive_dir.mkdir()

            (archive_dir / "trades_l1.jsonl").write_text(
                json.dumps(sample_trade(), sort_keys=True) + "\n",
                encoding="utf-8",
            )
            (archive_dir / "execution_audit.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in sample_audit_rows()),
                encoding="utf-8",
            )
            (archive_dir / "l1_paper.log").write_text(
                " ".join(
                    [
                        "event=regime_snapshot",
                        f"timestamp_utc={ENTRY_TS}",
                        "regime_label=bull",
                        "risk_label=good_atr",
                        "entry_score=2",
                        "ma200_signal=1",
                        "mfi_signal=1",
                        "atr_signal=1",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            market_path = root / "market.csv"
            timestamps, prices = sample_market_path()
            with market_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "close"])
                writer.writeheader()
                writer.writerows(
                    {"timestamp_utc": timestamp, "close": price}
                    for timestamp, price in zip(timestamps, prices)
                )

            label_list = root / "labels.txt"
            label_list.write_text("alpha\n", encoding="utf-8")
            label_registry = root / "registry.csv"

            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            command = [
                sys.executable,
                str(SCRIPT_PATH),
                "--archive-dir",
                str(archive_dir),
                "--market-csv",
                str(market_path),
                "--label-list",
                str(label_list),
                "--label-registry",
                str(label_registry),
                "--summary",
            ]

            first = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            second = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stderr, "")
            self.assertEqual(first.stdout, second.stdout)
            self.assertIn("TRADE INSPECTOR V6", first.stdout)
            self.assertIn("TRADE INSPECTOR SUMMARY", first.stdout)
            self.assertIn("trades: 1", first.stdout)
            self.assertIn("winners: 1", first.stdout)
            self.assertIn("total_pnl: 2.0", first.stdout)


if __name__ == "__main__":
    unittest.main()
