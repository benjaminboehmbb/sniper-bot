from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import runpy
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_RESEARCH_DIR = REPO_ROOT / "scripts" / "state_research"

SCRIPTS = {
    "predictive": STATE_RESEARCH_DIR / "analyze_step18_predictive_power.py",
    "buckets": STATE_RESEARCH_DIR / "analyze_step18_buckets.py",
    "lifetime": STATE_RESEARCH_DIR / "analyze_step18_trade_lifetime.py",
    "core": STATE_RESEARCH_DIR / "build_step18_core_pipeline.py",
    "clusters": STATE_RESEARCH_DIR / "analyze_step18_clusters.py",
}

SOURCE_SHA256 = {
    "predictive": "e32bd3d6545d92d210e317bf9f6db43aa353238f265108cd8b1c558c1b213751",
    "buckets": "89fe1b9cdd1c28027c07775b4e2520a077b0206becf31782b21cff8d882f64ec",
    "lifetime": "1f9b0d69bff434a84ad8a45243b241ec77dc24412b553645840701dfd02e2af1",
    "core": "57a819ed2fb04f075e059b5dc60cf4fba3b2c284b4b27e0120f30e01512fcf98",
    "clusters": "65918c7346b1819862dc17db2124768f0de6c8ca45daa93b0a846a4cbc80c5a3",
}

SOURCE_LINES = {
    "predictive": 27,
    "buckets": 55,
    "lifetime": 64,
    "core": 141,
    "clusters": 86,
}

EXPECTED_READS = {
    "predictive": ("live_logs/passive_shadow_risk_snapshots.csv",),
    "buckets": (
        "live_logs/trades_l1_auto_analysis.csv",
        "live_logs/passive_shadow_risk_snapshots.csv",
    ),
    "lifetime": (
        "live_logs/trades_l1_auto_analysis.csv",
        "live_logs/passive_shadow_risk_snapshots.csv",
    ),
    "core": ("live_logs/passive_shadow_risk_snapshots.csv",),
    "clusters": ("reports/step18/step18_core_metrics.csv",),
}

EXPECTED_WRITES = {
    "predictive": 0,
    "buckets": 0,
    "lifetime": 0,
    "core": 5,
    "clusters": 4,
}

FULL_RUNTIME_AVAILABLE = importlib.util.find_spec("pandas") is not None


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


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


def _main_function(tree: ast.Module) -> ast.FunctionDef:
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(functions) != 1:
        raise AssertionError(f"expected one main function, found {len(functions)}")
    return functions[0]


def _path_constants(tree: ast.Module) -> dict[str, str]:
    constants: dict[str, str] = {}
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "Path"
            and len(node.value.args) == 1
            and isinstance(node.value.args[0], ast.Constant)
            and isinstance(node.value.args[0].value, str)
        ):
            continue
        constants[node.targets[0].id] = node.value.args[0].value
    return constants


def _read_paths(tree: ast.Module) -> tuple[str, ...]:
    constants = _path_constants(tree)
    reads: list[str] = []
    for node in ast.walk(_main_function(tree)):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pd"
            and node.func.attr == "read_csv"
            and len(node.args) == 1
        ):
            continue
        argument = node.args[0]
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
            reads.append(argument.value)
        elif isinstance(argument, ast.Name) and argument.id in constants:
            reads.append(constants[argument.id])
        else:
            raise AssertionError(f"unresolved read_csv argument: {ast.dump(argument)}")
    return tuple(reads)


def _filesystem_manifest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _directories(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_dir()
    }


class Step18EntrypointConsolidationReviewTests(unittest.TestCase):
    def test_five_source_identities_are_bound(self) -> None:
        self.assertEqual(set(SCRIPTS), set(SOURCE_SHA256))
        self.assertEqual(set(SCRIPTS), set(SOURCE_LINES))
        for name, script in SCRIPTS.items():
            with self.subTest(name=name):
                raw = script.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256[name])
                self.assertEqual(len(raw.decode("utf-8").splitlines()), SOURCE_LINES[name])

    def test_all_entrypoints_share_only_the_minimal_main_guard_form(self) -> None:
        for name, script in SCRIPTS.items():
            with self.subTest(name=name):
                tree = _tree(script)
                main_function = _main_function(tree)
                guards = [node for node in tree.body if _is_main_guard(node)]
                self.assertEqual(len(guards), 1)
                self.assertEqual(main_function.args.posonlyargs, [])
                self.assertEqual(main_function.args.args, [])
                self.assertEqual(main_function.args.kwonlyargs, [])
                self.assertIsNone(main_function.args.vararg)
                self.assertIsNone(main_function.args.kwarg)
                self.assertEqual(len(guards[0].body), 1)
                call = guards[0].body[0]
                self.assertIsInstance(call, ast.Expr)
                self.assertIsInstance(call.value, ast.Call)
                self.assertIsInstance(call.value.func, ast.Name)
                self.assertEqual(call.value.func.id, "main")
                self.assertEqual(call.value.args, [])
                self.assertEqual(call.value.keywords, [])

    def test_fixed_input_contracts_remain_distinct(self) -> None:
        for name, script in SCRIPTS.items():
            with self.subTest(name=name):
                self.assertEqual(_read_paths(_tree(script)), EXPECTED_READS[name])

    def test_side_effect_classes_and_only_real_chain_are_bound(self) -> None:
        for name, script in SCRIPTS.items():
            tree = _tree(script)
            main_function = _main_function(tree)
            writes = [
                node
                for node in ast.walk(main_function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "to_csv"
            ]
            mkdirs = [
                node
                for node in ast.walk(main_function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mkdir"
            ]
            with self.subTest(name=name):
                self.assertEqual(len(writes), EXPECTED_WRITES[name])
                self.assertEqual(len(mkdirs), 1 if name == "core" else 0)

        core_strings = {
            node.value
            for node in ast.walk(_tree(SCRIPTS["core"]))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        cluster_input = _path_constants(_tree(SCRIPTS["clusters"]))["INPUT_PATH"]
        self.assertEqual(cluster_input, "reports/step18/step18_core_metrics.csv")
        self.assertIn(Path(cluster_input).name, core_strings)

    def test_no_cross_import_or_common_orchestrator_owner_exists(self) -> None:
        module_stems = {script.stem for script in SCRIPTS.values()}
        for name, script in SCRIPTS.items():
            imported: set[str] = set()
            for node in ast.walk(_tree(script)):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[-1] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[-1])
            with self.subTest(name=name):
                self.assertTrue(imported.isdisjoint(module_stems))

    @unittest.skipUnless(FULL_RUNTIME_AVAILABLE, "pandas fixture runtime required")
    def test_combined_import_probe_is_silent_and_nonmutating(self) -> None:
        with tempfile.TemporaryDirectory(prefix="step18_consolidation_import_") as temp_dir:
            root = Path(temp_dir)
            stdout = io.StringIO()
            stderr = io.StringIO()
            namespaces: dict[str, dict[str, object]] = {}
            previous_cwd = Path.cwd()
            try:
                os.chdir(root)
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    for name, script in SCRIPTS.items():
                        namespaces[name] = runpy.run_path(
                            str(script),
                            run_name=f"_step18_consolidation_{name}",
                        )
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(_filesystem_manifest(root), {})
            self.assertEqual(_directories(root), set())
            for name, namespace in namespaces.items():
                with self.subTest(name=name):
                    self.assertTrue(callable(namespace.get("main")))


if __name__ == "__main__":
    unittest.main()
