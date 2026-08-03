#!/usr/bin/env python3
"""Run the mandatory RCC-002 S8 Track-1 test gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

SCOPE_VERIFIER_PATH = (
    "scripts/rcc002/verify_s8candbcp_gate_scope.py"
)
EXPECTED_SCOPE_VERIFIER_SHA256 = (
    "60e6c8c3a0c3f4dcd0c9ebfebbc22b6515b4dba0597575078cb182c2dc3e5eb3"
)

EXPECTED_MANIFEST_SHA256 = (
    "c2be410babdfb62813b2588a7de2473ae744c35b076c790f331b2113becf7723"
)

POLICY_ID = "RCC002_S8CANDBCP_GATE_POLICY_V1"
EXPECTED_POLICY_PREIMAGE_SHA256 = (
    "27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1"
)

EXPECTED_POLICY_PATH_COUNT = 60
EXPECTED_GOVERNED_MODULE_COUNT = 49
EXPECTED_CURRENT_MODULE_COUNT = 45
EXPECTED_REPLAY_MODULE_COUNT = 2
EXPECTED_AUDIT_MODULE_COUNT = 2
EXPECTED_EXCLUDED_MODULE_COUNT = 11
EXPECTED_EXECUTABLE_MODULE_COUNT = 47

CATEGORY_ORDER = (
    "current_state_modules",
    "historical_replay_adapter_modules",
    "historical_audit_only_modules",
    "excluded_track2_candidate_modules",
)

TEST_ROOT_PATH = "tests/rcc002"
EXCLUDED_TRACK2_DIRECTORY_NAME = "s8"
EXCLUDED_TRACK2_PREFIX = "tests/rcc002/s8/"
PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"


class GateRunnerError(AssertionError):
    """Raised when the mandatory Track-1 gate cannot run safely."""

    def __init__(self, invariant: str, detail: str) -> None:
        super().__init__(f"{invariant}: {detail}")
        self.invariant = invariant
        self.detail = detail


def fail(invariant: str, detail: str) -> None:
    raise GateRunnerError(invariant, detail)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_module_path(path: str) -> None:
    try:
        path.encode("ascii")
    except UnicodeEncodeError as exc:
        fail("module_path_non_ascii", f"{path!r}: {exc}")

    pure = PurePosixPath(path)

    if pure.is_absolute():
        fail("module_path_absolute", path)

    if "\\" in path or ".." in pure.parts:
        fail("module_path_unsafe", path)

    if (
        not path.startswith("tests/rcc002/")
        or not path.endswith(".py")
    ):
        fail("module_path_wrong_shape", path)

    if path == PROTECTED_BUILDER_PATH:
        fail("protected_builder_entered_gate", path)


def load_scope_verifier(repo_root: Path) -> ModuleType:
    verifier_path = repo_root / SCOPE_VERIFIER_PATH

    if not verifier_path.is_file():
        fail(
            "scope_verifier_missing",
            SCOPE_VERIFIER_PATH,
        )

    raw = verifier_path.read_bytes()
    digest = sha256_hex(raw)

    if digest != EXPECTED_SCOPE_VERIFIER_SHA256:
        fail(
            "scope_verifier_digest_mismatch",
            digest,
        )

    module_name = (
        "_rcc002_s8candbcp_gate_scope_verifier"
    )

    if module_name in sys.modules:
        fail(
            "scope_verifier_duplicate_load",
            module_name,
        )

    specification = importlib.util.spec_from_file_location(
        module_name,
        verifier_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        fail(
            "scope_verifier_import_spec_failure",
            SCOPE_VERIFIER_PATH,
        )

    module = importlib.util.module_from_spec(
        specification
    )
    sys.modules[module_name] = module

    try:
        specification.loader.exec_module(module)
    except Exception as exc:
        sys.modules.pop(module_name, None)
        fail(
            "scope_verifier_import_failure",
            f"{type(exc).__name__}: {exc}",
        )

    return module


def reconstruct_policy_preimage(
    scope_result: dict[str, Any],
) -> bytes:
    lines = [f"policy_id={POLICY_ID}"]

    for category in CATEGORY_ORDER:
        value = scope_result.get(category)

        if type(value) is not list:
            fail(
                "scope_result_category_not_list",
                category,
            )

        if not all(type(path) is str for path in value):
            fail(
                "scope_result_category_non_string",
                category,
            )

        paths = tuple(value)

        if len(paths) != len(set(paths)):
            fail(
                "scope_result_category_duplicate",
                category,
            )

        if paths != tuple(sorted(paths)):
            fail(
                "scope_result_category_order",
                category,
            )

        lines.append(f"category={category}")

        for path in paths:
            validate_module_path(path)
            lines.append(f"path={path}")

    try:
        raw = ("\n".join(lines) + "\n").encode("ascii")
    except UnicodeEncodeError as exc:
        fail(
            "policy_preimage_non_ascii",
            str(exc),
        )

    return raw


def validate_scope_result(
    scope_result: Any,
) -> dict[str, tuple[str, ...]]:
    if type(scope_result) is not dict:
        fail(
            "scope_result_not_object",
            type(scope_result).__name__,
        )

    expected_scalar_values = {
        "result": "PASS",
        "policy_id": POLICY_ID,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "policy_preimage_sha256": (
            EXPECTED_POLICY_PREIMAGE_SHA256
        ),
        "policy_preimage_line_count": 65,
        "policy_preimage_byte_count": 2687,
        "policy_path_count": (
            EXPECTED_POLICY_PATH_COUNT
        ),
        "governed_track1_module_count": (
            EXPECTED_GOVERNED_MODULE_COUNT
        ),
        "current_state_module_count": (
            EXPECTED_CURRENT_MODULE_COUNT
        ),
        "historical_replay_adapter_module_count": (
            EXPECTED_REPLAY_MODULE_COUNT
        ),
        "historical_audit_only_module_count": (
            EXPECTED_AUDIT_MODULE_COUNT
        ),
        "excluded_track2_candidate_module_count": (
            EXPECTED_EXCLUDED_MODULE_COUNT
        ),
        "executable_module_count": (
            EXPECTED_EXECUTABLE_MODULE_COUNT
        ),
        "protected_builder_excluded": True,
        "track2_filesystem_access_performed": False,
    }

    for key, expected in expected_scalar_values.items():
        if scope_result.get(key) != expected:
            fail(
                "scope_result_scalar_mismatch",
                f"{key}={scope_result.get(key)!r}",
            )

    categories: dict[str, tuple[str, ...]] = {}

    for category in CATEGORY_ORDER:
        value = scope_result.get(category)

        if type(value) is not list:
            fail(
                "scope_result_category_not_list",
                category,
            )

        paths = tuple(value)

        if not all(type(path) is str for path in paths):
            fail(
                "scope_result_category_non_string",
                category,
            )

        if paths != tuple(sorted(paths)):
            fail(
                "scope_result_category_order",
                category,
            )

        if len(paths) != len(set(paths)):
            fail(
                "scope_result_category_duplicate",
                category,
            )

        for path in paths:
            validate_module_path(path)

        categories[category] = paths

    expected_category_counts = {
        "current_state_modules": (
            EXPECTED_CURRENT_MODULE_COUNT
        ),
        "historical_replay_adapter_modules": (
            EXPECTED_REPLAY_MODULE_COUNT
        ),
        "historical_audit_only_modules": (
            EXPECTED_AUDIT_MODULE_COUNT
        ),
        "excluded_track2_candidate_modules": (
            EXPECTED_EXCLUDED_MODULE_COUNT
        ),
    }

    for category, expected in (
        expected_category_counts.items()
    ):
        actual = len(categories[category])

        if actual != expected:
            fail(
                "scope_result_category_count",
                f"{category}={actual}",
            )

    policy_paths = tuple(
        path
        for category in CATEGORY_ORDER
        for path in categories[category]
    )

    if len(policy_paths) != EXPECTED_POLICY_PATH_COUNT:
        fail(
            "scope_result_policy_count",
            str(len(policy_paths)),
        )

    if len(set(policy_paths)) != (
        EXPECTED_POLICY_PATH_COUNT
    ):
        fail(
            "scope_result_category_overlap",
            "policy paths are not unique",
        )

    governed = (
        categories["current_state_modules"]
        + categories[
            "historical_replay_adapter_modules"
        ]
        + categories[
            "historical_audit_only_modules"
        ]
    )

    executable = (
        categories["current_state_modules"]
        + categories[
            "historical_replay_adapter_modules"
        ]
    )

    if len(governed) != EXPECTED_GOVERNED_MODULE_COUNT:
        fail(
            "scope_result_governed_count",
            str(len(governed)),
        )

    if len(executable) != (
        EXPECTED_EXECUTABLE_MODULE_COUNT
    ):
        fail(
            "scope_result_executable_count",
            str(len(executable)),
        )

    if set(
        categories["historical_audit_only_modules"]
    ) & set(executable):
        fail(
            "audit_only_entered_executable_union",
            "audit/executable overlap",
        )

    if any(
        path.startswith(EXCLUDED_TRACK2_PREFIX)
        for path in governed
    ):
        fail(
            "excluded_path_entered_governed_union",
            "Track-2 path detected",
        )

    if not all(
        path.startswith(EXCLUDED_TRACK2_PREFIX)
        for path in categories[
            "excluded_track2_candidate_modules"
        ]
    ):
        fail(
            "excluded_category_contains_track1_path",
            "non-Track-2 path detected",
        )

    returned_governed = tuple(
        scope_result.get(
            "governed_track1_modules",
            (),
        )
    )
    returned_executable = tuple(
        scope_result.get(
            "executable_modules",
            (),
        )
    )

    if returned_governed != governed:
        fail(
            "scope_result_governed_union_mismatch",
            "returned governed union differs",
        )

    if returned_executable != executable:
        fail(
            "scope_result_executable_union_mismatch",
            "returned executable union differs",
        )

    preimage = reconstruct_policy_preimage(
        scope_result
    )

    if len(preimage.splitlines()) != 65:
        fail(
            "runner_policy_line_count_mismatch",
            str(len(preimage.splitlines())),
        )

    if len(preimage) != 2687:
        fail(
            "runner_policy_byte_count_mismatch",
            str(len(preimage)),
        )

    digest = sha256_hex(preimage)

    if digest != EXPECTED_POLICY_PREIMAGE_SHA256:
        fail(
            "runner_policy_digest_mismatch",
            digest,
        )

    return {
        **categories,
        "governed_track1_modules": governed,
        "executable_modules": executable,
    }


def obtain_scope_authority(
    repo_root: Path,
) -> tuple[
    dict[str, Any],
    dict[str, tuple[str, ...]],
]:
    verifier = load_scope_verifier(repo_root)

    verify_function = getattr(
        verifier,
        "verify_gate_scope",
        None,
    )

    if not callable(verify_function):
        fail(
            "scope_verifier_entrypoint_missing",
            "verify_gate_scope",
        )

    try:
        scope_result = verify_function(repo_root)
    except Exception as exc:
        fail(
            "scope_verification_failed",
            f"{type(exc).__name__}: {exc}",
        )

    categories = validate_scope_result(
        scope_result
    )

    return scope_result, categories


def discover_governed_modules(
    repo_root: Path,
) -> tuple[str, ...]:
    test_root = repo_root / TEST_ROOT_PATH

    if not test_root.is_dir():
        fail(
            "test_root_missing",
            TEST_ROOT_PATH,
        )

    discovered: list[str] = []

    def recurse(
        directory: Path,
        relative_directory: PurePosixPath,
    ) -> None:
        try:
            entries = sorted(
                os.scandir(directory),
                key=lambda entry: entry.name,
            )
        except OSError as exc:
            fail(
                "disk_discovery_scandir_failure",
                f"{directory}: {exc}",
            )

        try:
            for entry in entries:
                name = entry.name

                if (
                    relative_directory
                    == PurePosixPath(TEST_ROOT_PATH)
                    and name
                    == EXCLUDED_TRACK2_DIRECTORY_NAME
                ):
                    continue

                if name == "__pycache__":
                    continue

                relative_path = (
                    relative_directory / name
                )
                relative_text = (
                    relative_path.as_posix()
                )

                if relative_text.startswith(
                    EXCLUDED_TRACK2_PREFIX
                ):
                    fail(
                        "excluded_subtree_reached",
                        relative_text,
                    )

                if entry.is_symlink():
                    fail(
                        "disk_discovery_symlink",
                        relative_text,
                    )

                if entry.is_dir(
                    follow_symlinks=False
                ):
                    recurse(
                        Path(entry.path),
                        relative_path,
                    )
                    continue

                if not entry.is_file(
                    follow_symlinks=False
                ):
                    continue

                if (
                    name.startswith("test_")
                    and name.endswith(".py")
                ):
                    validate_module_path(
                        relative_text
                    )
                    discovered.append(
                        relative_text
                    )
        finally:
            for entry in entries:
                del entry

    recurse(
        test_root,
        PurePosixPath(TEST_ROOT_PATH),
    )

    result = tuple(sorted(discovered))

    if len(result) != len(set(result)):
        fail(
            "disk_discovery_duplicate",
            repr(result),
        )

    return result


def require_discovery_matches_scope(
    discovered: tuple[str, ...],
    governed: tuple[str, ...],
) -> None:
    expected_set = set(governed)
    actual_set = set(discovered)

    missing = tuple(
        sorted(expected_set - actual_set)
    )
    extra = tuple(
        sorted(actual_set - expected_set)
    )

    if len(discovered) != (
        EXPECTED_GOVERNED_MODULE_COUNT
    ):
        fail(
            "disk_discovery_count_mismatch",
            (
                f"actual={len(discovered)}, "
                f"missing={missing}, extra={extra}"
            ),
        )

    if missing or extra:
        fail(
            "disk_discovery_membership_mismatch",
            f"missing={missing}, extra={extra}",
        )


def module_name_from_path(path: str) -> str:
    validate_module_path(path)

    return path[:-3].replace("/", ".")


def load_test_module(
    repo_root: Path,
    path: str,
) -> ModuleType:
    module_name = module_name_from_path(path)
    source_path = repo_root / path

    if not source_path.is_file():
        fail(
            "executable_module_missing",
            path,
        )

    if module_name in sys.modules:
        fail(
            "executable_module_duplicate_load",
            module_name,
        )

    specification = importlib.util.spec_from_file_location(
        module_name,
        source_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        fail(
            "executable_module_import_spec_failure",
            path,
        )

    module = importlib.util.module_from_spec(
        specification
    )
    sys.modules[module_name] = module

    try:
        specification.loader.exec_module(module)
    except Exception as exc:
        sys.modules.pop(module_name, None)
        fail(
            "executable_module_import_failure",
            f"{path}: {type(exc).__name__}: {exc}",
        )

    return module


def build_test_suite(
    repo_root: Path,
    executable_modules: tuple[str, ...],
) -> tuple[unittest.TestSuite, int]:
    if len(executable_modules) != (
        EXPECTED_EXECUTABLE_MODULE_COUNT
    ):
        fail(
            "executable_authority_count_mismatch",
            str(len(executable_modules)),
        )

    suite = unittest.TestSuite()
    loaded_count = 0

    for path in executable_modules:
        module = load_test_module(
            repo_root,
            path,
        )
        module_suite = (
            unittest.defaultTestLoader
            .loadTestsFromModule(module)
        )
        module_test_count = (
            module_suite.countTestCases()
        )

        if module_test_count < 1:
            fail(
                "executable_module_contains_no_tests",
                path,
            )

        suite.addTests(module_suite)
        loaded_count += 1

    if loaded_count != (
        EXPECTED_EXECUTABLE_MODULE_COUNT
    ):
        fail(
            "loader_call_count_mismatch",
            str(loaded_count),
        )

    return suite, loaded_count


def run_gate(
    repo_root: str | os.PathLike[str] | Path = REPO_ROOT,
    *,
    stream: TextIO | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()

    scope_result, categories = (
        obtain_scope_authority(root)
    )

    governed = categories[
        "governed_track1_modules"
    ]
    executable = categories[
        "executable_modules"
    ]

    discovered = discover_governed_modules(root)
    require_discovery_matches_scope(
        discovered,
        governed,
    )

    root_text = str(root)

    if root_text not in sys.path:
        sys.path.insert(0, root_text)

    suite, loaded_count = build_test_suite(
        root,
        executable,
    )

    output_stream = (
        sys.stderr
        if stream is None
        else stream
    )

    runner = unittest.TextTestRunner(
        stream=output_stream,
        verbosity=1,
    )
    result = runner.run(suite)

    report = {
        "result": (
            "PASS"
            if result.wasSuccessful()
            else "FAIL"
        ),
        "policy_id": POLICY_ID,
        "policy_preimage_sha256": (
            scope_result[
                "policy_preimage_sha256"
            ]
        ),
        "discovered_module_count": len(
            discovered
        ),
        "loaded_module_count": loaded_count,
        "current_state_module_count": (
            EXPECTED_CURRENT_MODULE_COUNT
        ),
        "historical_replay_adapter_module_count": (
            EXPECTED_REPLAY_MODULE_COUNT
        ),
        "historical_audit_only_module_count": (
            EXPECTED_AUDIT_MODULE_COUNT
        ),
        "excluded_track2_candidate_module_count": (
            EXPECTED_EXCLUDED_MODULE_COUNT
        ),
        "executable_module_count": (
            EXPECTED_EXECUTABLE_MODULE_COUNT
        ),
        "test_case_count": result.testsRun,
        "failure_count": len(result.failures),
        "error_count": len(result.errors),
        "protected_builder_accessed": False,
        "track2_subtree_children_enumerated": False,
    }

    if not result.wasSuccessful():
        return report

    if loaded_count != (
        EXPECTED_EXECUTABLE_MODULE_COUNT
    ):
        fail(
            "post_run_loader_count_mismatch",
            str(loaded_count),
        )

    return report


def run_scope_only(
    repo_root: str | os.PathLike[str] | Path = REPO_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    scope_result, categories = (
        obtain_scope_authority(root)
    )

    return {
        "result": "PASS",
        "mode": "scope-only",
        "policy_id": POLICY_ID,
        "policy_preimage_sha256": (
            scope_result[
                "policy_preimage_sha256"
            ]
        ),
        "policy_path_count": (
            EXPECTED_POLICY_PATH_COUNT
        ),
        "governed_module_count": len(
            categories[
                "governed_track1_modules"
            ]
        ),
        "executable_module_count": len(
            categories["executable_modules"]
        ),
        "filesystem_discovery_performed": False,
        "test_module_imports_performed": False,
        "track2_filesystem_access_performed": False,
        "protected_builder_accessed": False,
    }


def main(argv: list[str] | None = None) -> int:
    arguments = (
        sys.argv[1:]
        if argv is None
        else argv
    )

    try:
        if arguments == ["--scope-only"]:
            report = run_scope_only(REPO_ROOT)
            print(
                json.dumps(
                    report,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        if arguments:
            fail(
                "unsupported_arguments",
                repr(arguments),
            )

        report = run_gate(REPO_ROOT)

        print(
            json.dumps(
                report,
                indent=2,
                sort_keys=True,
            )
        )

        return (
            0
            if report["result"] == "PASS"
            else 1
        )
    except GateRunnerError as exc:
        print(
            f"FAIL: {exc.invariant}: {exc.detail}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
