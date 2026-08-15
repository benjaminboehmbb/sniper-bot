from __future__ import annotations

import ast
import contextlib
import hashlib
import io
from pathlib import Path
import runpy
import sys
from types import ModuleType
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "state_research" / "analyze_step18_predictive_power.py"
SOURCE_SHA256 = "e32bd3d6545d92d210e317bf9f6db43aa353238f265108cd8b1c558c1b213751"
FIXTURE_STDOUT_SHA256 = "7a50a1c59d6541da387a6939600f075a48a3b23cd37fbb5eaf25d3f0787987f5"
INPUT_PATH = "live_logs/passive_shadow_risk_snapshots.csv"
METRIC_COLUMNS = (
    "shadow_risk_score",
    "regime_mismatch_score",
    "atr_stress_score",
    "adverse_score_pressure",
)


def _source() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _tree() -> ast.Module:
    return ast.parse(_source(), filename=str(SCRIPT_PATH))


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


class _FixtureSeries:
    def __init__(self, column: str) -> None:
        self._column = column

    def describe(self) -> str:
        return f"describe:{self._column}"


class _FixtureFrame:
    def __getitem__(self, column: str) -> _FixtureSeries:
        return _FixtureSeries(column)


def _pandas_fixture(read_csv: object) -> ModuleType:
    module = ModuleType("pandas")
    module.read_csv = read_csv  # type: ignore[attr-defined]
    return module


class AnalyzeStep18PredictivePowerCharacterizationTests(unittest.TestCase):
    def test_source_identity_is_bound(self) -> None:
        raw = SCRIPT_PATH.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual(len(raw.decode("utf-8").splitlines()), 27)

    def test_entry_point_is_contained_behind_main_guard(self) -> None:
        tree = _tree()
        main_guards = [node for node in tree.body if _is_main_guard(node)]
        main_functions = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "main"
        ]
        self.assertEqual(len(main_guards), 1)
        self.assertEqual(len(main_functions), 1)
        self.assertEqual(main_functions[0].args.posonlyargs, [])
        self.assertEqual(main_functions[0].args.args, [])
        self.assertEqual(main_functions[0].args.kwonlyargs, [])
        self.assertIsNone(main_functions[0].args.vararg)
        self.assertIsNone(main_functions[0].args.kwarg)
        self.assertEqual(len(main_guards[0].body), 1)
        guard_call = main_guards[0].body[0]
        self.assertIsInstance(guard_call, ast.Expr)
        self.assertIsInstance(guard_call.value, ast.Call)
        self.assertIsInstance(guard_call.value.func, ast.Name)
        self.assertEqual(guard_call.value.func.id, "main")
        self.assertEqual(guard_call.value.args, [])
        self.assertEqual(guard_call.value.keywords, [])

        read_calls = [
            node
            for node in ast.walk(main_functions[0])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pd"
            and node.func.attr == "read_csv"
        ]
        self.assertEqual(len(read_calls), 1)
        all_read_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pd"
            and node.func.attr == "read_csv"
        ]
        self.assertEqual(len(all_read_calls), 1)
        self.assertEqual(len(read_calls[0].args), 1)
        self.assertIsInstance(read_calls[0].args[0], ast.Constant)
        self.assertEqual(read_calls[0].args[0].value, INPUT_PATH)

    def test_metric_column_order_is_bound(self) -> None:
        cols_assignments = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "cols" for target in node.targets)
        ]
        self.assertEqual(len(cols_assignments), 1)
        value = cols_assignments[0].value
        self.assertIsInstance(value, (ast.List, ast.Tuple))
        self.assertEqual(tuple(ast.literal_eval(value)), METRIC_COLUMNS)

    def test_script_has_no_file_writer_calls(self) -> None:
        writer_attributes = {
            "mkdir",
            "open",
            "to_csv",
            "to_excel",
            "to_feather",
            "to_json",
            "to_parquet",
            "write_bytes",
            "write_text",
        }
        attribute_calls = {
            node.func.attr
            for node in ast.walk(_tree())
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        builtin_open_calls = [
            node
            for node in ast.walk(_tree())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        ]
        self.assertFalse(attribute_calls & writer_attributes)
        self.assertEqual(builtin_open_calls, [])

    def test_fixture_execution_reads_only_the_bound_input(self) -> None:
        observed_paths: list[str] = []

        def read_csv(path: str) -> _FixtureFrame:
            observed_paths.append(path)
            return _FixtureFrame()

        stdout = io.StringIO()
        with mock.patch.dict(sys.modules, {"pandas": _pandas_fixture(read_csv)}):
            with contextlib.redirect_stdout(stdout):
                runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

        self.assertEqual(observed_paths, [INPUT_PATH])
        expected_lines = ["", "---- STEP18 DISTRIBUTIONS ----", ""]
        for column in METRIC_COLUMNS:
            expected_lines.extend((column, f"describe:{column}", ""))
        expected_lines.append("DONE")
        expected_stdout = "\n".join(expected_lines) + "\n"
        self.assertEqual(stdout.getvalue(), expected_stdout)
        self.assertEqual(
            hashlib.sha256(stdout.getvalue().encode("utf-8")).hexdigest(),
            FIXTURE_STDOUT_SHA256,
        )

    def test_import_path_has_no_input_read_or_stdout(self) -> None:
        def read_csv(path: str) -> _FixtureFrame:
            raise AssertionError(f"import attempted to read {path}")

        stdout = io.StringIO()
        with mock.patch.dict(sys.modules, {"pandas": _pandas_fixture(read_csv)}):
            with contextlib.redirect_stdout(stdout):
                namespace = runpy.run_path(
                    str(SCRIPT_PATH),
                    run_name="step18_predictive_power_import_probe",
                )

        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("main", namespace)
        self.assertTrue(callable(namespace["main"]))

    def test_missing_input_fails_closed_before_stdout(self) -> None:
        def read_csv(path: str) -> _FixtureFrame:
            raise FileNotFoundError(path)

        stdout = io.StringIO()
        with mock.patch.dict(sys.modules, {"pandas": _pandas_fixture(read_csv)}):
            with contextlib.redirect_stdout(stdout):
                with self.assertRaisesRegex(FileNotFoundError, INPUT_PATH):
                    runpy.run_path(str(SCRIPT_PATH), run_name="__main__")

        self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
