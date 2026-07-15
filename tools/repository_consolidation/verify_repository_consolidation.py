#!/usr/bin/env python3
# tools/repository_consolidation/verify_repository_consolidation.py
# ASCII-only
#
# Repository Consolidation governance/verification tool (RC-SPEC-011, RC-IU-005).
# This is governance tooling, not production/trading runtime code. It must never be
# imported by, and must never import, anything within run_engine.main's own active
# import closure.
#
# Deterministic, stdlib-only, directly executable.
# Exit code 0: all checks PASS. Exit code 1: at least one check FAILED.

import ast
import os
import subprocess
import sys

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(TOOL_DIR))

ENTRY_MODULE = "run_engine.main"
ENTRY_PATH = "run_engine/main.py"

EXPECTED_ACTIVE_MODULES = {
    "run_engine.main",
    "run_engine.core.loop",
    "run_engine.core.state",
    "run_engine.core.regime",
    "run_engine.core.strategy",
    "run_engine.core.position",
    "run_engine.core.risk",
    "run_engine.core.execution",
    "run_engine.core.execution.executor",
    "run_engine.core.performance",
    "run_engine.core.pnl",
    "run_engine.core.trade_lifecycle",
    "run_engine.core.canonical_state",
    "run_engine.core.canonical_enforcer",
}

RETAIN_DEFERRED_PATHS = {
    "run_engine/core/config.py",
    "run_engine/runtime/recovery.py",
    "run_engine/runtime/snapshot.py",
    "run_engine/runtime/state_memory.py",
}

EXPECTED_TRACKED_RUN_ENGINE_FILES = {
    "run_engine/main.py",
    "run_engine/core/loop.py",
    "run_engine/core/state.py",
    "run_engine/core/regime.py",
    "run_engine/core/strategy.py",
    "run_engine/core/position.py",
    "run_engine/core/risk.py",
    "run_engine/core/execution/__init__.py",
    "run_engine/core/execution/executor.py",
    "run_engine/core/performance.py",
    "run_engine/core/pnl.py",
    "run_engine/core/trade_lifecycle.py",
    "run_engine/core/canonical_state.py",
    "run_engine/core/canonical_enforcer.py",
    "run_engine/core/config.py",
    "run_engine/runtime/recovery.py",
    "run_engine/runtime/snapshot.py",
    "run_engine/runtime/state_memory.py",
}

ARCHIVED_OLD_PATHS = [
    "run_engine/execution/executor.py",
    "run_engine/runtime/performance_analytics.py",
    "run_engine/runtime/pnl_engine.py",
    "run_engine/runtime/position_state.py",
    "run_engine/runtime/risk.py",
    "run_engine/runtime/strategy_selector.py",
    "run_engine/runtime/regime_execution_gate.py",
    "run_engine/core/position_sizing.py",
    "run_engine/runtime/regime_stability.py",
    "run_engine/core/decision.py",
    "run_engine/core/equity_stabilizer.py",
    "run_engine/core/state_modulation.py",
    "run_engine/execution/adapter.py",
    "run_engine/execution/safety.py",
    "run_engine/feedback/tracker.py",
    "run_engine/logging/logger.py",
    "run_engine/runtime/strategy_memory.py",
    "run_engine/runtime/strategy_weights.py",
    "run_engine/core/features.py",
]

ARCHIVE_ROOT = "archive/REPOSITORY_CONSOLIDATION_2026-07-14"
ARCHIVED_COMPONENTS = ARCHIVED_OLD_PATHS + ["run_engine/runtime/memory.json"]

IGNORE_PATHS = [
    "_chat_handover",
    "claude_final_p1031_review",
    "claude_p1031_patch",
    "claude_p1_03b_review",
    "codex_p1_03_review",
    "review_packages",
    "_sgf017_context",
    "_ssi_context",
    "backups",
    "live_logs",
    "outputs",
    "runtime_runs",
    "engine/regime_classifier.py",
]

NON_NORMATIVE_DIR_NAMES = [
    "archive",
    "_chat_handover",
    "claude_final_p1031_review",
    "claude_p1031_patch",
    "claude_p1_03b_review",
    "codex_p1_03_review",
    "review_packages",
    "_sgf017_context",
    "_ssi_context",
    "backups",
]

results = []


def record(name, passed, detail):
    results.append((name, passed, detail))


def abspath(*parts):
    return os.path.join(REPO_ROOT, *parts)


def module_name_for(rel_path):
    mod = rel_path[:-3] if rel_path.endswith(".py") else rel_path
    mod = mod.replace("/", ".").replace(os.sep, ".")
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]
    return mod


def discover_run_engine_modules():
    root = abspath("run_engine")
    modules = {}
    is_pkg_init = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REPO_ROOT).replace(os.sep, "/")
            mod = module_name_for(rel)
            modules[mod] = rel
            is_pkg_init[mod] = fn == "__init__.py"
    return modules, is_pkg_init


def parse_imports(path, mod, is_pkg_init):
    full = abspath(path)
    src = open(full, encoding="utf-8").read()
    tree = ast.parse(src, filename=full)
    deps = set()
    dynamic = []
    own_base = mod.split(".")[:-1] if not is_pkg_init.get(mod) else mod.split(".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                pkg_parts = own_base[: len(own_base) - (node.level - 1)] if node.level > 1 else own_base
                resolved = ".".join(pkg_parts + [node.module]) if node.module else ".".join(pkg_parts)
                deps.add(resolved)
            elif node.module:
                deps.add(node.module)
        elif isinstance(node, ast.Call):
            fname = ""
            if isinstance(node.func, ast.Name):
                fname = node.func.id
            elif isinstance(node.func, ast.Attribute):
                fname = node.func.attr
            if fname in ("import_module", "__import__"):
                dynamic.append(mod)
    return deps, dynamic


def build_graph():
    modules, is_pkg_init = discover_run_engine_modules()
    edges = {}
    dynamic_all = []
    for mod, rel in modules.items():
        deps, dynamic = parse_imports(rel, mod, is_pkg_init)
        edges[mod] = deps
        dynamic_all.extend(dynamic)
    return modules, edges, dynamic_all


def closure_from_entry(modules, edges):
    reached = set()
    frontier = [ENTRY_MODULE]
    while frontier:
        cur = frontier.pop()
        if cur in reached:
            continue
        reached.add(cur)
        for dep in edges.get(cur, set()):
            if dep in modules and dep not in reached:
                frontier.append(dep)
    return reached


def detect_cycle(modules, edges):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {m: WHITE for m in modules}

    def dfs(node, stack):
        color[node] = GRAY
        stack.append(node)
        for dep in edges.get(node, set()):
            if dep not in modules:
                continue
            if color[dep] == GRAY:
                return stack[stack.index(dep):] + [dep]
            if color[dep] == WHITE:
                cyc = dfs(dep, stack)
                if cyc:
                    return cyc
        stack.pop()
        color[node] = BLACK
        return None

    for m in modules:
        if color[m] == WHITE:
            cyc = dfs(m, [])
            if cyc:
                return cyc
    return None


def git_ls_files(path):
    try:
        out = subprocess.run(
            ["git", "ls-files", "--", path],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
        return [l for l in out.stdout.splitlines() if l.strip()]
    except Exception as exc:
        return None if exc else []


def git_check_ignore(path):
    proc = subprocess.run(
        ["git", "check-ignore", "-q", "--", path],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return proc.returncode == 0


def main():
    modules, edges, dynamic_all = build_graph()
    active_closure = closure_from_entry(modules, edges)

    # 1. Canonical Entry Point
    entry_exists = os.path.isfile(abspath(ENTRY_PATH))
    entry_in_closure = ENTRY_MODULE in active_closure
    record(
        "01_canonical_entry_point",
        entry_exists and entry_in_closure,
        "run_engine.main exists at {0} and is its own closure root".format(ENTRY_PATH),
    )

    # 2. AST-based active import closure (mechanism itself; success if no exception raised)
    record("02_ast_import_closure_computed", True,
           "{0} total run_engine modules discovered, closure computed".format(len(modules)))

    # 3. Expected active module set == 14
    active_ok = active_closure == EXPECTED_ACTIVE_MODULES
    record(
        "03_active_module_set_exact",
        active_ok,
        "expected {0} active modules, found {1}: {2}".format(
            len(EXPECTED_ACTIVE_MODULES), len(active_closure),
            "match" if active_ok else sorted(active_closure ^ EXPECTED_ACTIVE_MODULES),
        ),
    )

    # 4. RETAIN-Deferred components: exactly 4, still unreached
    retain_deferred_modules = {module_name_for(p) for p in RETAIN_DEFERRED_PATHS}
    retain_present = all(os.path.isfile(abspath(p)) for p in RETAIN_DEFERRED_PATHS)
    retain_unreached = retain_deferred_modules.isdisjoint(active_closure)
    record(
        "04_retain_deferred_components",
        retain_present and retain_unreached and len(RETAIN_DEFERRED_PATHS) == 4,
        "4 RETAIN-Deferred paths present={0}, unreached={1}".format(retain_present, retain_unreached),
    )

    # 5. No imports from archive/, scratch, review, backup, or local-context areas
    forbidden_import_hits = []
    for mod, deps in edges.items():
        for dep in deps:
            for bad in NON_NORMATIVE_DIR_NAMES:
                if dep == bad or dep.startswith(bad + "."):
                    forbidden_import_hits.append((mod, dep))
    record(
        "05_no_imports_from_non_normative_areas",
        len(forbidden_import_hits) == 0,
        "forbidden import edges: {0}".format(forbidden_import_hits),
    )

    # 6. No archived module remains at its original path
    stale_originals = [p for p in ARCHIVED_OLD_PATHS if os.path.isfile(abspath(p))]
    record(
        "06_no_archived_module_at_original_path",
        len(stale_originals) == 0,
        "files still present at old path: {0}".format(stale_originals),
    )

    # 7. All 20 ARCHIVE components present at the specified archive target
    missing_archived = [
        p for p in ARCHIVED_COMPONENTS
        if not os.path.isfile(abspath(ARCHIVE_ROOT, p))
    ]
    record(
        "07_all_archive_components_present_at_target",
        len(missing_archived) == 0 and len(ARCHIVED_COMPONENTS) == 20,
        "missing at archive target: {0}".format(missing_archived),
    )

    # 8. Archive not reachable from run_engine.main
    archive_reachable = any(
        edges.get(m, set()) and any(d.startswith("archive") for d in edges.get(m, set()))
        for m in active_closure
    )
    record(
        "08_archive_not_reachable_from_entry",
        not archive_reachable,
        "archive reachability check on closure: reachable={0}".format(archive_reachable),
    )

    # 9. No active namespace collision for Executor
    executor_modules = [m for m in active_closure if m.endswith(".executor")]
    record(
        "09_no_executor_namespace_collision",
        len(executor_modules) == 1,
        "active Executor modules: {0}".format(executor_modules),
    )

    # 10. No competing active Computational Authority from known alternative paths
    active_class_names = {}
    duplicate_names = []
    for mod in active_closure:
        rel = modules.get(mod)
        if not rel:
            continue
        full = abspath(rel)
        try:
            tree = ast.parse(open(full, encoding="utf-8").read(), filename=full)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name in active_class_names and active_class_names[node.name] != mod:
                    duplicate_names.append((node.name, active_class_names[node.name], mod))
                active_class_names[node.name] = mod
    record(
        "10_no_competing_active_computational_authority",
        len(duplicate_names) == 0,
        "duplicate active class names: {0}".format(duplicate_names),
    )

    # 11. No tracked generated artifacts in log/output/run/backup boundaries
    tracked_generated = []
    for d in ["live_logs", "outputs", "runtime_runs", "backups"]:
        files = git_ls_files(d)
        if files:
            tracked_generated.extend(files)
    record(
        "11_no_tracked_generated_artifacts",
        len(tracked_generated) == 0,
        "tracked files under generated-artifact directories: {0}".format(tracked_generated[:10]),
    )

    # 12. memory.json not in active tree
    memory_json_gone = not os.path.isfile(abspath("run_engine/runtime/memory.json"))
    record(
        "12_memory_json_not_in_active_tree",
        memory_json_gone,
        "run_engine/runtime/memory.json present={0}".format(not memory_json_gone),
    )

    # 13. IGNORE paths actually ignored
    not_ignored = [p for p in IGNORE_PATHS if os.path.exists(abspath(p)) and not git_check_ignore(p)]
    record(
        "13_ignore_paths_ignored",
        len(not_ignored) == 0,
        "paths not correctly ignored: {0}".format(not_ignored),
    )

    # 14. No unauthorized root-level Python artifacts in normative scope
    tracked_run_engine = git_ls_files("run_engine")
    unauthorized = None
    if tracked_run_engine is not None:
        unauthorized = sorted(set(tracked_run_engine) - EXPECTED_TRACKED_RUN_ENGINE_FILES)
    record(
        "14_no_unauthorized_root_level_artifacts",
        tracked_run_engine is not None and len(unauthorized) == 0,
        "unauthorized tracked run_engine/ files: {0}".format(unauthorized),
    )

    # 15. Active runtime file list matches certified baseline
    tracked_set = set(tracked_run_engine) if tracked_run_engine is not None else set()
    baseline_ok = tracked_set == EXPECTED_TRACKED_RUN_ENGINE_FILES
    record(
        "15_active_runtime_file_list_matches_baseline",
        baseline_ok,
        "tracked run_engine/ file set matches expected 18-file RETAIN baseline: {0}".format(baseline_ok),
    )

    # 16. Import cycles in active closure
    cycle = detect_cycle(modules, edges)
    record(
        "16_no_import_cycles",
        cycle is None,
        "cycle found: {0}".format(cycle) if cycle else "no cycle found",
    )

    # Dynamic-import guard (supports checks 5/8/10 above; not separately numbered)
    record(
        "17_no_dynamic_imports_masking_static_analysis",
        len(dynamic_all) == 0,
        "modules using importlib/__import__: {0}".format(dynamic_all),
    )

    # Machine-readable summary
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    print("REPOSITORY_CONSOLIDATION_VERIFICATION_SUMMARY")
    for name, ok, detail in results:
        print("{0}\t{1}\t{2}".format(name, "PASS" if ok else "FAIL", detail))
    print("TOTAL\t{0}/{1} PASS".format(len(passed), len(results)))

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
