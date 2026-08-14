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

from tools.trade_inspector import archive_intake as intake
from tools.trade_inspector import csv_persistence
from tools.trade_inspector import inspect_trades as inspector
from tools.trade_inspector import inspection_primitives as primitives
from tools.trade_inspector import label_registry
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
