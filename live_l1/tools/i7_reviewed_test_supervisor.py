#!/usr/bin/env python3
"""Minimal supervisor for the reviewed I7 preparation test module.

This tool provides ordinary engineering evidence for file-exact, reviewed
test code. It does not protect against deliberately malicious test code and
does not grant I7, release, live, or production authority.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGET_MODULE = "tests.live_l1.test_i7_file_exact_preparation"
TARGET_FILE = PROJECT_ROOT / "tests/live_l1/test_i7_file_exact_preparation.py"
DEFAULT_TIMEOUT_SECONDS = 180.0

EXPECTED_TEST_METHODS = (
    "test_01_manifest_schema_and_exact_types",
    "test_02_package_relative_alias_and_missing_local_imports",
    "test_03_dynamic_import_constructions_fail_closed",
    "test_04_forbidden_alias_and_census_partition",
    "test_05_replay_pinning_traversal_hash_malformed_and_old_artifacts",
    "test_06_pre_post_roles_sequence_and_distinctness",
    "test_07_observer_contract_run_hash_and_preowned_invariants",
    "test_08_cleanup_binding_and_tmp_confinement",
    "test_09_contract_schema_duplicate_path_and_symlink_boundaries",
    "test_10_contract_hardlink_mode_owner_hash_and_permission_boundaries",
    "test_11_capability_ids_and_counts_are_derived_not_asserted",
    "test_12_timeout_group_reap_preservation_diff_and_attestation",
)

PINNED_FILES = {
    "config/pee/IU4_I7_FILE_EXACT_GATES_V1.json":
        "7eea67c93ecd70fbecd043daea7a74c5ce07548c08b4546c4fe477f6c0de50a5",
    "config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json":
        "12228780102d62dee3f0982507642b648e9defc6edc095739df6e38fa8dbf62d",
    "live_l1/__init__.py":
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "live_l1/tools/i7_file_exact_harness.py":
        "c0c48f31c9af4484667048987587d769abe30933f3625a1a4064d55f986e1967",
    "live_l1/tools/i7_file_exact_observer.py":
        "0e427702d48dd8dba2a657a41d6b33e8cfe88441e42dad205b11f67aa68d7bca",
    "live_l1/tools/i7_staged_synthetic_replay.py":
        "7b7a51185c00c8322e1b4bcdb86703b2d07f309eb9b8e84f81a4394e35e9c8cd",
    "tests/live_l1/__init__.py":
        "6e07d0dd2cea69b640c5a06402ab0ae7417fdd15dea6f1a6d89c66ad81fc6070",
    "tests/live_l1/test_i7_file_exact_preparation.py":
        "3a12f70485bec0c19d2b874853582a958e8be7872ff22dc9ff8c8f55bcd9be6e",
}

SUPERVISOR_PATHS = (
    "/live_l1/tools/i7_reviewed_test_supervisor.py",
    "/tests/live_l1/test_i7_reviewed_test_supervisor.py",
)

SUMMARY_RE = re.compile(r"^Ran (\d+) tests? in [^\n]+$", re.MULTILINE)


class SupervisorError(RuntimeError):
    """Raised when reviewed-test supervision fails closed."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pinned_hashes() -> dict[str, str]:
    return {
        relative: _sha256_file(PROJECT_ROOT / relative)
        for relative in sorted(PINNED_FILES)
    }


def verify_pinned_files() -> dict[str, str]:
    actual = pinned_hashes()
    mismatches = {
        path: {"expected": PINNED_FILES[path], "actual": digest}
        for path, digest in actual.items()
        if digest != PINNED_FILES[path]
    }
    if mismatches:
        raise SupervisorError(
            "pinned file mismatch: "
            + json.dumps(mismatches, sort_keys=True, separators=(",", ":"))
        )
    return actual


def discovered_test_methods() -> tuple[str, ...]:
    tree = ast.parse(TARGET_FILE.read_bytes(), filename=str(TARGET_FILE))
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name.startswith("test_"):
                    names.append(child.name)
    return tuple(names)


def verify_static_manifest() -> tuple[str, ...]:
    actual = discovered_test_methods()
    if actual != EXPECTED_TEST_METHODS:
        raise SupervisorError(
            "test manifest mismatch: "
            + json.dumps(
                {"expected": EXPECTED_TEST_METHODS, "actual": actual},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    return actual


def repository_status() -> bytes:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    result = subprocess.run(
        [
            "git",
            "--no-optional-locks",
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise SupervisorError(
            "git status failed: " + result.stderr.decode("utf-8", "replace")
        )
    return result.stdout


def temporary_git_directory(root: Path) -> Path:
    git_directory = root / "git"
    (git_directory / "info").mkdir(parents=True)
    (git_directory / "objects/info").mkdir(parents=True)
    (git_directory / "refs").mkdir()

    actual_git_directory = Path(subprocess.check_output(
        ["git", "--no-optional-locks", "rev-parse", "--absolute-git-dir"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        text=True,
    ).strip())
    head = subprocess.check_output(
        ["git", "--no-optional-locks", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        text=True,
    ).strip()
    shutil.copyfile(actual_git_directory / "index", git_directory / "index")
    (git_directory / "HEAD").write_text(head + "\n", encoding="ascii")
    (git_directory / "config").write_text(
        "[core]\n\trepositoryformatversion = 0\n\tbare = false\n"
        "\tfilemode = true\n\tworktree = " + json.dumps(str(PROJECT_ROOT)) + "\n",
        encoding="utf-8",
    )
    (git_directory / "objects/info/alternates").write_text(
        str(actual_git_directory / "objects") + "\n", encoding="utf-8"
    )
    existing_excludes = actual_git_directory / "info/exclude"
    payload = existing_excludes.read_bytes() if existing_excludes.exists() else b""
    separator = b"" if not payload or payload.endswith(b"\n") else b"\n"
    (git_directory / "info/exclude").write_bytes(
        payload + separator
        + ("\n".join(SUPERVISOR_PATHS) + "\n").encode("utf-8")
    )
    return git_directory


def child_environment(git_directory: Path) -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "PYTHONHOME",
        "PYTHONINSPECT",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
    ):
        environment.pop(name, None)
    for name in tuple(environment):
        if name == "GIT_CONFIG_COUNT" or name.startswith((
            "GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_",
        )):
            environment.pop(name)
    environment.update(
        {
            "GIT_DIR": str(git_directory),
            "GIT_WORK_TREE": str(PROJECT_ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "PYTHONNOUSERSITE": "1",
        }
    )
    return environment


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1.0)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait(timeout=1.0)


def parse_success(stdout: bytes, stderr: bytes) -> int:
    combined = (
        stdout.decode("utf-8", "replace")
        + "\n"
        + stderr.decode("utf-8", "replace")
    )
    matches = SUMMARY_RE.findall(combined)
    if len(matches) != 1:
        raise SupervisorError("missing or ambiguous unittest summary")
    count = int(matches[0])
    if count != len(EXPECTED_TEST_METHODS):
        raise SupervisorError(
            f"test count mismatch: expected {len(EXPECTED_TEST_METHODS)}, got {count}"
        )
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    if not lines or lines[-1] != "OK":
        raise SupervisorError("unittest terminal result is not exact OK")
    return count


def run_supervised(timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> dict[str, object]:
    if timeout_seconds <= 0:
        raise SupervisorError("timeout must be positive")

    methods = verify_static_manifest()
    before_hashes = verify_pinned_files()
    before_status = repository_status()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="i7-reviewed-supervisor-", dir="/tmp") as name:
        git_directory = temporary_git_directory(Path(name))
        process = subprocess.Popen(
            [sys.executable, "-B", "-m", "unittest", "-v", TARGET_MODULE],
            cwd=PROJECT_ROOT,
            env=child_environment(git_directory),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_process_group(process)
            stdout, stderr = process.communicate()
    duration = time.monotonic() - started

    after_hashes = pinned_hashes()
    after_status = repository_status()
    if after_hashes != before_hashes:
        raise SupervisorError("pinned files changed during test execution")
    if after_status != before_status:
        raise SupervisorError("repository status changed during test execution")
    if timed_out:
        raise SupervisorError(f"test process timed out after {timeout_seconds:g}s")
    if process.returncode != 0:
        output = (stdout + b"\n" + stderr).decode("utf-8", "replace")
        traceback_offset = output.rfind("Traceback (most recent call last):")
        diagnostic = output[traceback_offset:traceback_offset + 4000]
        raise SupervisorError(
            f"test process failed with return code {process.returncode}: {diagnostic}"
        )

    count = parse_success(stdout, stderr)
    return {
        "artifact_type": "I7_REVIEWED_TEST_SUPERVISOR_RESULT",
        "schema_version": 1,
        "threat_model": "REVIEWED_TEST_CODE",
        "module": TARGET_MODULE,
        "methods": list(methods),
        "count": count,
        "return_code": process.returncode,
        "duration_seconds": round(duration, 6),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "repository_status_sha256": hashlib.sha256(before_status).hexdigest(),
        "pinned_files": before_hashes,
        "authority": "ENGINEERING_EVIDENCE_ONLY",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    arguments = parser.parse_args(argv)
    try:
        result = run_supervised(arguments.timeout_seconds)
    except SupervisorError as error:
        print(f"I7_REVIEWED_TEST_SUPERVISOR: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("I7_REVIEWED_TEST_SUPERVISOR: PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
