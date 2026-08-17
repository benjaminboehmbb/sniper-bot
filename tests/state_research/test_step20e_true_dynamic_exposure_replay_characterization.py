from __future__ import annotations

import ast
import contextlib
import csv
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "state_research" / "analyze_step20E_true_dynamic_exposure_replay.py"

TRADES_INPUT = Path("live_logs/trades_l1_auto_analysis.csv")
LIFECYCLE_INPUT = Path("live_logs/trade_lifecycle_snapshots.csv")
SHADOW_INPUT = Path("live_logs/passive_shadow_risk_snapshots.csv")
OUTPUT = Path("reports/step18/step20E_true_dynamic_exposure_replay.csv")

SOURCE_SHA256 = "2d9e3eb1e32745661cfcbea8e840c0916465c579345da4b8a5e018570aa0ff08"
SOURCE_LINES = 178
RUNTIME_AST_SHA256 = "4400afd463d3d071c888484b01823bc4869d46cdfdf7001de696bd629155ef4d"
START_CAPITAL = 10000.0

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None

TRADES_ROWS = (
    {"trade_index": "4", "entry_timestamp_utc": "2026-01-01T00:30:00Z", "exit_timestamp_utc": "2026-01-01T00:32:00Z", "exit_price": "99", "side": "SHORT", "pnl": "-20"},
    {"trade_index": "1", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "exit_timestamp_utc": "2026-01-01T00:02:00Z", "exit_price": "104", "side": "LONG", "pnl": "100"},
    {"trade_index": "3", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "exit_timestamp_utc": "2026-01-01T00:22:00Z", "exit_price": "96", "side": "LONG", "pnl": "40"},
    {"trade_index": "2", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "exit_timestamp_utc": "2026-01-01T00:12:00Z", "exit_price": "96", "side": "SHORT", "pnl": "-80"},
)

LIFECYCLE_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "long", "entry_price": "100", "current_price": "101"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "LONG", "entry_price": "100", "current_price": "102"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "entry_timestamp_utc": "2026-01-01T00:00:00Z", "side": "Long", "entry_price": "100", "current_price": "103"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "short", "entry_price": "100", "current_price": "99"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "SHORT", "entry_price": "100", "current_price": "98"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "entry_timestamp_utc": "2026-01-01T00:10:00Z", "side": "Short", "entry_price": "100", "current_price": "97"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "long", "entry_price": "100", "current_price": "99"},
    {"timestamp_utc": "2026-01-01T00:21:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "LONG", "entry_price": "100", "current_price": "98"},
    {"timestamp_utc": "2026-01-01T00:22:00Z", "entry_timestamp_utc": "2026-01-01T00:20:00Z", "side": "Long", "entry_price": "100", "current_price": "97"},
)

SHADOW_ROWS = (
    {"timestamp_utc": "2026-01-01T00:00:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:01:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:02:00Z", "shadow_risk_score": "0.31"},
    {"timestamp_utc": "2026-01-01T00:10:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:11:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:12:00Z", "shadow_risk_score": "0.51"},
    {"timestamp_utc": "2026-01-01T00:20:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:21:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:22:00Z", "shadow_risk_score": "0.71"},
    {"timestamp_utc": "2026-01-01T00:30:00Z", "shadow_risk_score": "0.90"},
)


def _tree() -> ast.Module:
    return ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))


def _is_main_guard(node: ast.AST) -> bool:
    if not isinstance(node, ast.If):
        return False
    test = node.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def _main_function() -> ast.FunctionDef:
    functions = [
        node
        for node in _tree().body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one main function, found {len(functions)}")
    return functions[0]


def _runtime_ast_sha256() -> str:
    runtime_module = ast.Module(body=_main_function().body, type_ignores=[])
    payload = ast.dump(runtime_module, include_attributes=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _function(name: str) -> ast.FunctionDef:
    functions = [
        node
        for node in _main_function().body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one {name} function, found {len(functions)}")
    return functions[0]


def _trade_loop() -> ast.For:
    loops = [
        node
        for node in _main_function().body
        if isinstance(node, ast.For)
        and isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Attribute)
        and node.iter.func.attr == "iterrows"
    ]
    if len(loops) != 1:
        raise AssertionError(f"expected one trade loop, found {len(loops)}")
    return loops[0]


def _write_csv(path: Path, rows: tuple[dict[str, str], ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_header(path: Path, fieldnames: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fieldnames).writeheader()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _manifest(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(root.rglob("*")) if path.is_file()}


def _directories(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()}


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run([sys.executable, str(SCRIPT)], cwd=root, check=False, capture_output=True, text=True)
    completed.stdout = completed.stdout.replace("\r\n", "\n")
    completed.stderr = completed.stderr.replace("\r\n", "\n")
    return completed


class Step20ETrueDynamicExposureReplayCharacterizationTests(unittest.TestCase):
    maxDiff = None

    def test_source_identity_constant_functions_and_encapsulated_executor_are_bound(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES)
        tree = _tree()
        assignments = {
            target.id: ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance((target := node.targets[0]), ast.Name)
            and target.id == "START_CAPITAL"
        }
        self.assertEqual(assignments, {"START_CAPITAL": START_CAPITAL})
        self.assertEqual([node.name for node in tree.body if isinstance(node, ast.FunctionDef)], ["main"])
        main_function = _main_function()
        self.assertEqual(
            [node.name for node in main_function.body if isinstance(node, ast.FunctionDef)],
            ["update_multiplier", "stats"],
        )
        self.assertIsInstance(main_function.returns, ast.Constant)
        self.assertIsNone(main_function.returns.value)
        self.assertEqual(main_function.args.posonlyargs, [])
        self.assertEqual(main_function.args.args, [])
        self.assertEqual(main_function.args.kwonlyargs, [])
        self.assertIsNone(main_function.args.vararg)
        self.assertIsNone(main_function.args.kwarg)

        guards = [node for node in tree.body if _is_main_guard(node)]
        self.assertEqual(len(guards), 1)
        self.assertEqual(len(guards[0].body), 1)
        guard_call = guards[0].body[0]
        self.assertIsInstance(guard_call, ast.Expr)
        self.assertIsInstance(guard_call.value, ast.Call)
        self.assertIsInstance(guard_call.value.func, ast.Name)
        self.assertEqual(guard_call.value.func.id, "main")
        self.assertEqual(guard_call.value.args, [])
        self.assertEqual(guard_call.value.keywords, [])
        self.assertEqual(_runtime_ast_sha256(), RUNTIME_AST_SHA256)

        top_level_reads = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "read_csv"
        ]
        top_level_calls = [
            node
            for node in tree.body
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
        ]
        self.assertEqual(top_level_reads, [])
        self.assertEqual(top_level_calls, [])

    def test_fixed_read_and_timestamp_conversion_order_are_bound(self) -> None:
        body = _main_function().body
        reads = [ast.literal_eval(node.value.args[0]) for node in body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "read_csv"]
        self.assertEqual(reads, [TRADES_INPUT.as_posix(), LIFECYCLE_INPUT.as_posix(), SHADOW_INPUT.as_posix()])
        conversions = [ast.literal_eval(node.value.args[0].slice) for node in body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "to_datetime" and isinstance(node.value.args[0], ast.Subscript)]
        self.assertEqual(conversions, ["entry_timestamp_utc", "exit_timestamp_utc", "timestamp_utc", "entry_timestamp_utc", "timestamp_utc"])
        utc_keywords = [node.value.keywords for node in body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "to_datetime"]
        self.assertTrue(all(len(keywords) == 1 and keywords[0].arg == "utc" and ast.literal_eval(keywords[0].value) is True for keywords in utc_keywords))

    def test_update_multiplier_strict_streak_reset_and_monotonic_levels_are_bound(self) -> None:
        function = _function("update_multiplier")
        namespace: dict[str, object] = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])), str(SCRIPT), "exec"), namespace)
        update = namespace["update_multiplier"]
        state = (0, 0, 0, 1.0)
        for risk in [0.31, 0.31, 0.31]:
            state = update(risk, *state)
        self.assertEqual(state, (3, 0, 0, 0.5))
        state = (0, 0, 0, 1.0)
        for risk in [0.51, 0.51, 0.51]:
            state = update(risk, *state)
        self.assertEqual(state, (3, 3, 0, 0.25))
        state = (0, 0, 0, 1.0)
        for risk in [0.71, 0.71, 0.71]:
            state = update(risk, *state)
        self.assertEqual(state, (3, 3, 3, 0.1))
        self.assertEqual(update(0.30, 2, 2, 2, 0.1), (0, 0, 0, 0.1))
        source = ast.unparse(function)
        self.assertIn("risk > 0.3", source)
        self.assertIn("risk > 0.5", source)
        self.assertIn("risk > 0.7", source)
        self.assertEqual(source.count("new_mult = min(new_mult,"), 3)

    def test_trade_match_inclusive_window_merge_and_default_contract_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("life['entry_timestamp_utc'] == entry_ts", source)
        self.assertIn("life['side'].astype(str).str.lower() == side", source)
        self.assertIn("shadow['timestamp_utc'] >= entry_ts", source)
        self.assertIn("shadow['timestamp_utc'] <= exit_ts", source)
        self.assertIn("if len(life_trade) == 0 or len(shadow_trade) == 0", source)
        self.assertIn("replay_pnl = original_pnl", source)
        self.assertIn("reductions = 0", source)
        self.assertIn("final_mult = 1.0", source)
        merge = next(node for node in ast.walk(_trade_loop()) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "merge_asof")
        self.assertEqual({keyword.arg: ast.unparse(keyword.value) for keyword in merge.keywords}, {"on": "'timestamp_utc'", "direction": "'nearest'", "tolerance": "pd.Timedelta('2min')"})
        self.assertIn("merged['shadow_risk_score'] = merged['shadow_risk_score'].fillna(0.0)", source)

    def test_segment_update_order_final_segment_reductions_and_row_schema_are_bound(self) -> None:
        source = ast.unparse(_trade_loop())
        self.assertIn("entry_price = float(merged.iloc[0]['entry_price'])", source)
        self.assertIn("prev_price = entry_price", source)
        self.assertIn("current_mult = 1.0", source)
        self.assertIn("segment_pnl = (price - prev_price) * current_mult", source)
        self.assertIn("segment_pnl = (prev_price - price) * current_mult", source)
        self.assertLess(source.index("replay_pnl += segment_pnl"), source.index("update_multiplier("))
        self.assertLess(source.index("prev_price = price"), source.index("update_multiplier("))
        self.assertIn("if current_mult < old_mult:", source)
        self.assertIn("reductions += 1", source)
        self.assertIn("final_exit_price = float(trade['exit_price'])", source)
        self.assertIn("final_segment_pnl = (final_exit_price - prev_price) * current_mult", source)
        self.assertIn("final_segment_pnl = (prev_price - final_exit_price) * current_mult", source)
        self.assertIn("replay_pnl += final_segment_pnl", source)
        self.assertNotIn("position_size", source)
        append_call = next(node for node in ast.walk(_trade_loop()) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append")
        row = append_call.args[0]
        self.assertEqual([ast.literal_eval(key) for key in row.keys], ["trade_index", "side", "original_pnl", "replay_pnl", "reductions", "final_multiplier"])
        self.assertIn("df = pd.DataFrame(rows).sort_values('trade_index')", ast.unparse(_tree()))

    def test_stats_stdout_distributions_and_writer_contract_are_bound(self) -> None:
        tree = _tree()
        body = _main_function().body
        function = _function("stats")
        source = ast.unparse(function)
        self.assertEqual([argument.arg for argument in function.args.args], ["pnl_col"])
        for fragment in ["START_CAPITAL + df[pnl_col].cumsum()", "peak = equity.cummax()", "dd_abs = peak - equity", "wins = df[df[pnl_col] > 0]", "losses = df[df[pnl_col] < 0]", "pf = gp / gl if gl > 0 else float('inf')"]:
            self.assertIn(fragment, source)
        returned = next(node.value for node in function.body if isinstance(node, ast.Return))
        self.assertEqual([ast.literal_eval(key) for key in returned.keys], ["final_equity", "total_pnl", "return_pct", "winrate", "profit_factor", "max_drawdown_abs", "max_drawdown_pct"])
        all_source = ast.unparse(tree)
        self.assertIn("df['final_multiplier'].value_counts().sort_index()", all_source)
        self.assertIn("df['reductions'].value_counts().sort_index()", all_source)
        out_node = next(node for node in body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "out" for target in node.targets))
        self.assertEqual(ast.literal_eval(out_node.value), OUTPUT.as_posix())
        write = next(node.value for node in body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "to_csv")
        self.assertEqual(ast.unparse(write.args[0]), "out")
        self.assertEqual([(keyword.arg, ast.literal_eval(keyword.value)) for keyword in write.keywords], [("index", False)])
        self.assertEqual([node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "mkdir"], [])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_import_is_silent_and_has_no_filesystem_side_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20e_true_dynamic_exposure_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    namespace = runpy.run_path(
                        str(SCRIPT),
                        run_name="_step20e_true_dynamic_exposure_import",
                    )
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(_manifest(root), {})
            self.assertEqual(_directories(root), set())
            self.assertTrue(callable(namespace.get("main")))
            self.assertNotIn("update_multiplier", namespace)
            self.assertNotIn("stats", namespace)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_successful_fixture_stdout_csv_and_input_nonmutation_are_bound(self) -> None:
        expected_stdout = (
            "\n---- STEP20E TRUE DYNAMIC EXPOSURE REPLAY ----\ntrades: 4\n\n"
            "ORIGINAL\nfinal_equity: 10040.0\ntotal_pnl: 40.0\nreturn_pct: 0.004\nwinrate: 0.5\nprofit_factor: 1.4\nmax_drawdown_abs: 80.0\nmax_drawdown_pct: 0.0079\n\n"
            "STEP20E\nfinal_equity: 9983.65\ntotal_pnl: -16.35\nreturn_pct: -0.0016\nwinrate: 0.5\nprofit_factor: 0.2922\nmax_drawdown_abs: 23.1\nmax_drawdown_pct: 0.0023\n\n"
            "FINAL MULTIPLIER DISTRIBUTION\nfinal_multiplier\n0.10    1\n0.25    1\n0.50    1\n1.00    1\nName: count, dtype: int64\n\n"
            "REDUCTIONS\nreductions\n0    1\n1    3\nName: count, dtype: int64\n\n"
            f"written: {OUTPUT.as_posix()}\n"
        )
        with tempfile.TemporaryDirectory(prefix="step20e_success_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            (root / OUTPUT.parent).mkdir(parents=True)
            before = _manifest(root)
            result = _run(root)
            after = _manifest(root)
            rows = _read_csv(root / OUTPUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_stdout)
        self.assertEqual({path: after[path] for path in before}, before)
        self.assertEqual([row["trade_index"] for row in rows], ["1", "2", "3", "4"])
        self.assertEqual([row["replay_pnl"] for row in rows], ["3.5", "3.25", "-3.1", "-20.0"])
        self.assertEqual([row["reductions"] for row in rows], ["1", "1", "1", "0"])
        self.assertEqual([row["final_multiplier"] for row in rows], ["0.5", "0.25", "0.1", "1.0"])

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_inputs_fail_closed_in_fixed_read_order(self) -> None:
        stages = (((), TRADES_INPUT), (((TRADES_INPUT, TRADES_ROWS),), LIFECYCLE_INPUT), (((TRADES_INPUT, TRADES_ROWS), (LIFECYCLE_INPUT, LIFECYCLE_ROWS)), SHADOW_INPUT))
        for provided, missing in stages:
            with self.subTest(missing=missing.as_posix()):
                with tempfile.TemporaryDirectory(prefix="step20e_missing_") as temp_dir:
                    root = Path(temp_dir)
                    for path, rows in provided:
                        _write_csv(root / path, rows)
                    before = _manifest(root)
                    dirs = _directories(root)
                    result = _run(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("FileNotFoundError", result.stderr)
                    self.assertIn(missing.as_posix(), result.stderr.replace("\\", "/"))
                    self.assertEqual(_manifest(root), before)
                    self.assertEqual(_directories(root), dirs)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_empty_trades_fail_before_stdout_and_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20e_empty_") as temp_dir:
            root = Path(temp_dir)
            _write_header(root / TRADES_INPUT, tuple(TRADES_ROWS[0]))
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("KeyError", result.stderr)
            self.assertIn("trade_index", result.stderr)
            self.assertEqual(_manifest(root), before)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_missing_output_directory_fails_after_stats_before_written_line(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step20e_missing_output_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, TRADES_ROWS)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stdout.startswith("\n---- STEP20E TRUE DYNAMIC EXPOSURE REPLAY ----\n"))
            self.assertIn("REDUCTIONS", result.stdout)
            self.assertNotIn("written:", result.stdout)
            self.assertIn("OSError", result.stderr)
            self.assertEqual(_manifest(root), before)

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_malformed_first_timestamp_fails_before_stdout_and_without_mutation(self) -> None:
        malformed = tuple(dict(row) for row in TRADES_ROWS)
        malformed[0]["entry_timestamp_utc"] = "not-a-timestamp"
        with tempfile.TemporaryDirectory(prefix="step20e_bad_time_") as temp_dir:
            root = Path(temp_dir)
            _write_csv(root / TRADES_INPUT, malformed)
            _write_csv(root / LIFECYCLE_INPUT, LIFECYCLE_ROWS)
            _write_csv(root / SHADOW_INPUT, SHADOW_ROWS)
            before = _manifest(root)
            result = _run(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("DateParseError", result.stderr)
            self.assertIn("not-a-timestamp", result.stderr)
            self.assertEqual(_manifest(root), before)


if __name__ == "__main__":
    unittest.main()
