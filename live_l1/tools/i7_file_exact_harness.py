#!/usr/bin/env python3
"""Pinned, fail-closed local harness for IU4 I7 preparation gates."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = PROJECT_ROOT / "config/pee/IU4_I7_FILE_EXACT_GATES_V1.json"
DEFAULT_SCHEMA = PROJECT_ROOT / "config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json"
EVIDENCE_RELATIVE_PATH = (
    "docs/review/PRE_IU4_I7_PREPARATION_RESOLUTION_FILE_EXACT_2026-08-23.md"
)
PINNED_MANIFEST_SHA256 = "a96ddc05124e3a95312833c281e86155b1c1f1710d9845b1da7cf64f74799719"
PINNED_SCHEMA_SHA256 = "12228780102d62dee3f0982507642b648e9defc6edc095739df6e38fa8dbf62d"
PINNED_SCHEMA_ID = "IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V3"
FORBIDDEN_PATHS = (
    "scripts/build_rcc002_spec_bundle.py",
    "live_l1/tools/validate_terminal_lease_capability.py",
    "tests/live_l1/test_terminal_lease_capability.py",
)
FORBIDDEN_MODULES = tuple(
    path[:-3].replace("/", ".") for path in FORBIDDEN_PATHS if path.endswith(".py")
)
PINNED_GATE_AUTHORITY = {
    "preparation_components": {
        "kind": "unittest",
        "execution": "LOCAL_SYNTHETIC_ONLY",
        "modules": ("tests.live_l1.test_i7_file_exact_preparation",),
        "expected_count": 12,
        "timeout_seconds": 180,
    },
    "staged_synthetic_replay": {
        "kind": "module",
        "execution": "LOCAL_SYNTHETIC_ONLY",
        "module": "live_l1.tools.i7_staged_synthetic_replay",
        "expected_count": 3,
        "timeout_seconds": 300,
    },
    "full_live_census_only": {
        "kind": "census",
        "execution": "NEVER_EXECUTE_IN_RESOLUTION_5",
        "census_count": 584,
    },
}
REQUIRED_FILE_INPUT_IDS = (
    "SPECIFICATION", "FREEZE_MANIFEST", "FREEZE_TAR", "GATE_MANIFEST",
    "CAPABILITY_RUNNER", "CAPABILITY_MANIFEST", "CAPABILITY_ARTIFACT_SCHEMA",
    "OBSERVER_RUNNER", "OBSERVER_SNAPSHOT_SCHEMA", "SSH_PRIVATE_KEY",
    "SSH_KNOWN_HOSTS", "QEMU_BINARY", "COMPILER", "LINKER", "SUDO_BINARY",
    "BTF", "VMLINUX",
)
PINNED_CANONICAL_INPUTS = {
    "SPECIFICATION": (
        PROJECT_ROOT / "docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md",
        "ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0",
    ),
    "FREEZE_MANIFEST": (
        PROJECT_ROOT / "archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt",
        "ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16",
    ),
    "FREEZE_TAR": (
        PROJECT_ROOT / "archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz",
        "3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037",
    ),
    "GATE_MANIFEST": (DEFAULT_MANIFEST, PINNED_MANIFEST_SHA256),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
LOCAL_TOP_LEVELS = frozenset(
    path.name for path in PROJECT_ROOT.iterdir()
    if path.is_dir() and not path.is_symlink()
) | frozenset(path.stem for path in PROJECT_ROOT.glob("*.py"))
EFFECT_ROOTS = {
    "subprocess", "multiprocessing", "socket", "signal", "resource",
}
EFFECT_CALLS = {
    "os.fork", "os.forkpty", "os.system", "os.popen", "os.posix_spawn",
    "os.posix_spawnp", "os.kill", "os.killpg", "os.pidfd_open",
    "time.sleep",
}
EFFECT_PREFIXES = ("os.exec", "subprocess.", "multiprocessing.", "socket.", "signal.")
CONTROLLED_EFFECT_FUNCTIONS = {
    ("live_l1/tools/i7_file_exact_harness.py", "_run_process_group"),
    ("live_l1/tools/i7_file_exact_harness.py", "_group_exists"),
    ("live_l1/tools/i7_file_exact_harness.py", "_git_bytes"),
    ("live_l1/tools/i7_file_exact_harness.py", "_repository_members"),
    ("live_l1/tools/i7_file_exact_harness.py", "_effective_git_semantics"),
    (
        "tests/live_l1/test_i7_file_exact_preparation.py",
        "_case_29_timeout_terms_kills_and_reaps_child_grandchild_group",
    ),
    (
        "tests/live_l1/test_i7_file_exact_preparation.py",
        "_case_22a_run_authority_freshness_parent_chain_and_replay",
    ),
    (
        "tests/live_l1/test_i7_file_exact_preparation.py",
        "_case_31_authentic_result_channel_rejects_fake_output_and_replay",
    ),
}
CONTROLLED_DYNAMIC_RETURN_FUNCTIONS = {
    ("live_l1/tools/i7_file_exact_harness.py", "_finding"),
    ("live_l1/tools/i7_file_exact_harness.py", "_expr_binding"),
}
UNITTEST_WORKER_RUNNER = r'''import errno,json,os,posix,sys,unittest
forbidden_fd=int(os.environ.pop("I7_WORKER_FORBIDDEN_RESULT_FD"))
try:
 os.fstat(forbidden_fd)
except OSError as exc:
 if exc.errno!=errno.EBADF: raise
else:
 raise RuntimeError("final result writer leaked into unittest worker")
modules=json.loads(os.environ.pop("I7_WORKER_START_MODULES"))
expected=int(os.environ.pop("I7_WORKER_EXPECTED_COUNT"))
if type(modules) is not list or any(type(value) is not str for value in modules):
 raise RuntimeError("worker start-module schema mismatch")
loader=unittest.TestLoader()
runner=unittest.TextTestRunner(stream=sys.stderr,verbosity=1)
load_modules=loader.loadTestsFromNames
run_suite=runner.run
def forbidden_exit(code=0):
 raise SystemExit(code)
os._exit=forbidden_exit
posix._exit=forbidden_exit
try:
 suite=load_modules(modules)
 result=run_suite(suite)
except BaseException:
 raise SystemExit(75)
passed=(
 type(result.testsRun) is int and result.testsRun==expected and
 len(result.failures)==0 and len(result.errors)==0 and
 len(result.skipped)==0 and len(result.unexpectedSuccesses)==0 and
 len(result.expectedFailures)==0 and result.wasSuccessful() is True
)
raise SystemExit(73 if passed else 74)
'''

UNITTEST_SUPERVISOR_RUNNER = r'''import ctypes,hashlib,json,os,stat,subprocess,sys
fd=int(os.environ["I7_RESULT_FD"])
fd_stat=os.fstat(fd)
if not stat.S_ISFIFO(fd_stat.st_mode): raise RuntimeError("result writer is not a pipe")
modules=json.loads(os.environ["I7_RESULT_START_MODULES"])
expected=int(os.environ["I7_RESULT_EXPECTED_COUNT"])
worker_env={key:value for key,value in os.environ.items() if not key.startswith("I7_RESULT_")}
worker_env["I7_WORKER_START_MODULES"]=json.dumps(modules,separators=(",",":"))
worker_env["I7_WORKER_EXPECTED_COUNT"]=str(expected)
worker_env["I7_WORKER_FORBIDDEN_RESULT_FD"]=str(fd)
worker_code=''' + repr(UNITTEST_WORKER_RUNNER) + r'''
libc=ctypes.CDLL(None,use_errno=True)
if libc.prctl(4,0,0,0,0)!=0: raise RuntimeError("supervisor process protection failed")
worker=subprocess.run(
 [sys.executable,"-c",worker_code],env=worker_env,
 capture_output=True,close_fds=True,check=False,
)
if worker.returncode!=73:
 raise RuntimeError("worker did not reach the fixed successful unittest terminus")
report={
 "artifact_type":"IU4_I7_AUTHENTIC_UNITTEST_RESULT","schema_version":3,
 "gate_id":os.environ["I7_RESULT_GATE_ID"],"run_id":os.environ["I7_RESULT_RUN_ID"],
 "nonce":os.environ["I7_RESULT_NONCE"],"child_pid":os.getpid(),
 "runner_sha256":os.environ["I7_RESULT_RUNNER_SHA256"],"start_modules":modules,
 "expected_count":expected,"tests_run":expected,"failures":0,"errors":0,
 "skipped":0,"unexpected_successes":0,"expected_failures":0,"result":"PASS",
}
payload=json.dumps(report,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")+b"\n"
written=os.write(fd,payload)
if written!=len(payload): raise RuntimeError("short terminal result write")
os.close(fd)
sys.stdout.buffer.write(worker.stdout)
sys.stderr.buffer.write(worker.stderr)
raise SystemExit(0)
'''
UNITTEST_SUPERVISOR_SHA256 = hashlib.sha256(
    UNITTEST_SUPERVISOR_RUNNER.encode("ascii")
).hexdigest()


class I7HarnessError(RuntimeError):
    pass


@dataclass(frozen=True)
class FileIdentity:
    path: str
    realpath: str
    sha256: str
    size: int
    mode: int
    uid: int
    gid: int
    device: int
    inode: int


@dataclass(frozen=True, order=True)
class ImportEdge:
    from_path: str
    from_module: str
    to_path: str
    to_module: str
    edge_type: str
    resolution_status: str
    line: int
    column: int
    symbol: str = ""
    call: str = ""
    reason: str = ""


@dataclass(frozen=True, order=True)
class ClosureFinding:
    path: str
    line: int
    column: int
    symbol: str
    call: str
    reason: str
    target: str


@dataclass(frozen=True)
class ImportClosure:
    start_modules: tuple[str, ...]
    files: tuple[str, ...]
    edges: tuple[ImportEdge, ...]
    identities: tuple[FileIdentity, ...]
    dynamic_imports: tuple[ClosureFinding, ...]
    unresolved_local_imports: tuple[ClosureFinding, ...]
    forbidden_edges: tuple[ClosureFinding, ...]
    effect_edges: tuple[ClosureFinding, ...]


@dataclass(frozen=True)
class ProcessResult:
    return_code: int
    stdout: bytes
    stderr: bytes
    timed_out: bool
    group_reaped: bool
    term_sent: bool
    kill_sent: bool
    child_pid: int


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise I7HarnessError("duplicate or non-string JSON key")
        result[key] = value
    return result


def _strict_json(payload: bytes, *, label: str) -> object:
    if (
        not payload.endswith(b"\n") or payload.endswith(b"\n\n")
        or b"\r" in payload or b"\0" in payload
    ):
        raise I7HarnessError(f"{label} must be ASCII single-terminal-LF JSON")
    try:
        return json.loads(
            payload.decode("ascii"), object_pairs_hook=_pairs_no_duplicates
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise I7HarnessError(f"invalid {label} JSON") from exc


def _open_noatime_nofollow(path: Path) -> int:
    flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, "O_NOATIME"):
        flags |= os.O_NOATIME
    try:
        return os.open(path, flags)
    except PermissionError:
        return os.open(path, os.O_RDONLY | os.O_NOFOLLOW)


def _read_file_exact(path: Path, *, expected_root: Path | None = None) -> tuple[bytes, FileIdentity]:
    if path.is_symlink():
        raise I7HarnessError(f"symlink is forbidden: {path}")
    resolved = path.resolve(strict=True)
    if expected_root is not None and resolved != expected_root and expected_root not in resolved.parents:
        raise I7HarnessError(f"path escapes confinement: {path}")
    initial = os.lstat(path)
    if not stat.S_ISREG(initial.st_mode) or initial.st_nlink != 1:
        raise I7HarnessError(f"nonregular or hardlinked file: {path}")
    descriptor = _open_noatime_nofollow(path)
    try:
        opened = os.fstat(descriptor)
        digest = hashlib.sha256()
        blocks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
            digest.update(block)
        readback = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    final = os.lstat(path)
    key = lambda value: (
        value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
        value.st_size, value.st_atime_ns, value.st_mtime_ns, value.st_ctime_ns,
    )
    if key(initial) != key(opened) or key(opened) != key(readback) or key(readback) != key(final):
        raise I7HarnessError(f"file changed during read: {path}")
    relative = resolved.relative_to(PROJECT_ROOT).as_posix() if PROJECT_ROOT in resolved.parents else str(resolved)
    identity = FileIdentity(
        relative, str(resolved), digest.hexdigest(), final.st_size,
        stat.S_IMODE(final.st_mode), final.st_uid, final.st_gid,
        final.st_dev, final.st_ino,
    )
    return b"".join(blocks), identity


def _read_pinned_repository_json(path: Path, sha256: str, *, label: str) -> dict[str, Any]:
    if path not in {DEFAULT_MANIFEST, DEFAULT_SCHEMA}:
        raise I7HarnessError(f"noncanonical {label} path")
    payload, identity = _read_file_exact(path, expected_root=PROJECT_ROOT)
    if (
        identity.sha256 != sha256 or identity.mode != 0o444
        or identity.uid != 1000 or identity.gid != 1000
    ):
        raise I7HarnessError(f"pinned {label} identity mismatch")
    value = _strict_json(payload, label=label)
    if type(value) is not dict:
        raise I7HarnessError(f"{label} must be an exact object")
    return value


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    if path.resolve(strict=True) != DEFAULT_MANIFEST.resolve(strict=True):
        raise I7HarnessError("only the canonical manifest is accepted")
    value = _read_pinned_repository_json(
        DEFAULT_MANIFEST, PINNED_MANIFEST_SHA256, label="gate manifest"
    )
    expected_fields = {
        "artifact_type", "schema_version", "manifest_id", "canonical_repository",
        "forbidden_paths", "global_timeout_seconds", "evidence_contract", "gates",
        "staged_synthetic_replay", "capability_external_binding",
        "workstation_external_binding", "collector_external_binding",
        "workstation_contract_schema",
    }
    if set(value) != expected_fields:
        raise I7HarnessError("manifest fields are incomplete or unknown")
    if (
        value["artifact_type"] != "IU4_I7_FILE_EXACT_GATES"
        or type(value["schema_version"]) is not int
        or value["schema_version"] != 4
        or value["manifest_id"] != "IU4_I7_FILE_EXACT_GATES_RESOLUTION_5_V1"
        or value["canonical_repository"] != str(PROJECT_ROOT)
        or tuple(value["forbidden_paths"]) != FORBIDDEN_PATHS
        or type(value["global_timeout_seconds"]) is not int
    ):
        raise I7HarnessError("manifest identity/type mismatch")
    if type(value["gates"]) is not list or len(value["gates"]) != 3:
        raise I7HarnessError("manifest gate cardinality mismatch")
    ids = tuple(gate.get("id") for gate in value["gates"] if type(gate) is dict)
    if ids != tuple(PINNED_GATE_AUTHORITY):
        raise I7HarnessError("manifest gate IDs/order mismatch")
    for gate in value["gates"]:
        authority = PINNED_GATE_AUTHORITY[gate["id"]]
        for key, expected in authority.items():
            observed = tuple(gate[key]) if key == "modules" else gate[key]
            if type(observed) is not type(expected) or observed != expected:
                raise I7HarnessError(f"manifest authority mismatch: {gate['id']}.{key}")
    schema = value["workstation_contract_schema"]
    if type(schema) is not dict or schema != {
        "path": "config/pee/IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V1.json",
        "schema_id": PINNED_SCHEMA_ID,
        "sha256": PINNED_SCHEMA_SHA256,
        "mode": 292,
        "uid": 1000,
        "gid": 1000,
    }:
        raise I7HarnessError("workstation schema binding mismatch")
    _read_pinned_repository_json(DEFAULT_SCHEMA, PINNED_SCHEMA_SHA256, label="schema")
    return value


def _module_lexical_path(module: str) -> tuple[Path | None, bool]:
    if type(module) is not str or not module or any(part in {"", ".", ".."} for part in module.split(".")):
        return None, False
    if module in FORBIDDEN_MODULES:
        return PROJECT_ROOT.joinpath(*module.split(".")).with_suffix(".py"), True
    stem = PROJECT_ROOT.joinpath(*module.split("."))
    candidates = (stem.with_suffix(".py"), stem / "__init__.py")
    for candidate in candidates:
        lexical = candidate.relative_to(PROJECT_ROOT).as_posix()
        if lexical in FORBIDDEN_PATHS:
            return candidate, True
        if candidate.is_symlink():
            return candidate, True
        if candidate.is_file():
            resolved = candidate.resolve(strict=True)
            if PROJECT_ROOT not in resolved.parents or resolved != candidate.absolute():
                return candidate, True
            return candidate, False
    return None, False


def _module_path(module: str) -> Path | None:
    path, forbidden = _module_lexical_path(module)
    if forbidden:
        return path
    return path


def _module_name(path: Path) -> str:
    parts = list(path.relative_to(PROJECT_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _package_initializers(module: str, path: Path) -> tuple[Path, ...]:
    parts = module.split(".")[:-1] if path.name != "__init__.py" else module.split(".")
    result: list[Path] = []
    for index in range(1, len(parts) + 1):
        candidate = PROJECT_ROOT.joinpath(*parts[:index], "__init__.py")
        if candidate.exists():
            if candidate.is_symlink() or candidate.resolve(strict=True) != candidate.absolute():
                raise I7HarnessError(f"package initializer alias: {candidate}")
            result.append(candidate)
    return tuple(result)


def _relative_import(current: str, current_path: Path, level: int, module: str | None) -> str:
    package = current.split(".") if current_path.name == "__init__.py" else current.split(".")[:-1]
    if level:
        if level > len(package):
            return ""
        package = package[: len(package) - level + 1]
    elif module:
        return module
    if module:
        package.extend(module.split("."))
    return ".".join(package)


_DYNAMIC_CALLABLE = "<dynamic-import-callable>"
_DYNAMIC_FACTORY = "<dynamic-import-factory>"
_DANGEROUS_CALLABLES = frozenset({
    "__import__", "builtins.__import__", "importlib.import_module",
    "getattr", "builtins.getattr",
})


def _call_name(node: ast.AST, aliases: Mapping[str, str]) -> str:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        left = _call_name(node.value, aliases)
        return f"{left}.{node.attr}" if left else node.attr
    if isinstance(node, ast.NamedExpr):
        return _call_name(node.value, aliases)
    if isinstance(node, (ast.Subscript, ast.Lambda)):
        values = tuple(
            _call_name(value, aliases)
            for value in ast.walk(node)
            if isinstance(value, (ast.Name, ast.Attribute))
        )
        if any(value in _DANGEROUS_CALLABLES or value == _DYNAMIC_CALLABLE for value in values):
            return _DYNAMIC_CALLABLE
    return ""


class _ClosureVisitor(ast.NodeVisitor):
    def __init__(self, relative: str, module: str, path: Path) -> None:
        self.relative = relative
        self.module = module
        self.path = path
        self.aliases: dict[str, str] = {}
        self.targets: set[tuple[str, str, int, int, str]] = set()
        self.dynamic: set[ClosureFinding] = set()
        self.effects: set[ClosureFinding] = set()
        self.function_stack: list[str] = []
        self.function_returns: dict[str, str] = {}

    def _finding(
        self, node: ast.AST, *, symbol: str, call: str, reason: str,
        target: str = "",
    ) -> ClosureFinding:
        return ClosureFinding(
            self.relative, int(getattr(node, "lineno", 0)),
            int(getattr(node, "col_offset", 0)), symbol, call, reason, target,
        )

    def _expr_binding(self, node: ast.AST) -> str:
        direct = _call_name(node, self.aliases)
        if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript, ast.Lambda, ast.NamedExpr)) and (
            direct in _DANGEROUS_CALLABLES
            or direct in {_DYNAMIC_CALLABLE, _DYNAMIC_FACTORY}
        ):
            return direct
        if isinstance(node, ast.NamedExpr):
            return self._expr_binding(node.value)
        if isinstance(node, ast.Attribute):
            return (
                _DYNAMIC_CALLABLE if self._expr_binding(node.value) else ""
            )
        if isinstance(node, ast.Subscript):
            if self._expr_binding(node.value) or self._expr_binding(node.slice):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, ast.IfExp):
            bindings = (
                self._expr_binding(node.body), self._expr_binding(node.orelse)
            )
            if any(bindings):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, ast.BoolOp):
            if any(self._expr_binding(value) for value in node.values):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, ast.Call):
            called = _call_name(node.func, self.aliases)
            if called == _DYNAMIC_FACTORY or called in self.function_returns:
                return _DYNAMIC_CALLABLE
            if called in {"getattr", "builtins.getattr"}:
                target = _call_name(node.args[0], self.aliases) if node.args else ""
                attribute = (
                    node.args[1].value
                    if len(node.args) > 1 and isinstance(node.args[1], ast.Constant)
                    and type(node.args[1].value) is str else None
                )
                if target == "importlib" or attribute in {"import_module", "__import__"}:
                    return _DYNAMIC_CALLABLE
            bound_arguments = any(self._expr_binding(value) for value in node.args)
            bound_keywords = any(
                self._expr_binding(keyword.value) for keyword in node.keywords
            )
            if (
                self._expr_binding(node.func)
                or bound_arguments or bound_keywords
            ):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom, ast.Starred)):
            value = getattr(node, "value", None)
            return self._expr_binding(value) if value is not None else ""
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
            if any(self._expr_binding(value) for value in node.elts):
                return _DYNAMIC_CALLABLE
        if isinstance(node, ast.Dict):
            if any(
                self._expr_binding(value)
                for value in (*node.keys, *node.values) if value is not None
            ):
                return _DYNAMIC_CALLABLE
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            values: list[ast.AST] = [node.elt]
            for generator in node.generators:
                values.append(generator.iter)
                values.extend(generator.ifs)
            if any(self._expr_binding(value) for value in values):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, ast.DictComp):
            values = [node.key, node.value]
            for generator in node.generators:
                values.append(generator.iter)
                values.extend(generator.ifs)
            if any(self._expr_binding(value) for value in values):
                return _DYNAMIC_CALLABLE
            return ""
        if isinstance(node, ast.expr) and any(
            self._expr_binding(child)
            for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.expr)
        ):
            return _DYNAMIC_CALLABLE
        return ""

    def _bind_target(self, target: ast.AST, binding: str, node: ast.AST) -> None:
        if isinstance(target, ast.Name):
            previous = self.aliases.get(target.id, "")
            if previous in _DANGEROUS_CALLABLES or previous in {
                _DYNAMIC_CALLABLE, _DYNAMIC_FACTORY,
            }:
                if binding != previous:
                    self.dynamic.add(self._finding(
                        node, symbol=target.id, call=previous,
                        reason="dynamic-alias-rebinding", target=binding or "UNKNOWN",
                    ))
            if binding:
                self.aliases[target.id] = binding
            elif target.id in self.aliases:
                del self.aliases[target.id]
            return
        if isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self._bind_target(item, binding, node)
            return
        if binding:
            self.dynamic.add(self._finding(
                node, symbol=ast.dump(target, include_attributes=False),
                call=binding, reason="dynamic-alias-attribute-or-subscript-binding",
                target=binding,
            ))

    def visit_Assign(self, node: ast.Assign) -> None:
        binding = self._expr_binding(node.value)
        if isinstance(node.value, (ast.Tuple, ast.List)) and len(node.targets) == 1 and isinstance(node.targets[0], (ast.Tuple, ast.List)) and len(node.value.elts) == len(node.targets[0].elts):
            for target, value in zip(node.targets[0].elts, node.value.elts):
                self._bind_target(target, self._expr_binding(value), node)
        else:
            for target in node.targets:
                self._bind_target(target, binding, node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._bind_target(node.target, self._expr_binding(node.value) if node.value else "", node)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._bind_target(node.target, self._expr_binding(node.value), node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        outer_aliases = self.aliases
        outer_functions = dict(self.function_returns)
        self.aliases = dict(outer_aliases)
        for decorator in node.decorator_list:
            binding = self._expr_binding(decorator)
            if binding:
                self.dynamic.add(self._finding(
                    decorator, symbol=node.name, call=binding,
                    reason="dynamic-import-decorator-binding", target=binding,
                ))
        positional = tuple(node.args.posonlyargs) + tuple(node.args.args)
        for argument, default in zip(positional[-len(node.args.defaults):], node.args.defaults):
            binding = self._expr_binding(default)
            if binding:
                self.aliases[argument.arg] = binding
                self.dynamic.add(self._finding(
                    default, symbol=argument.arg, call=binding,
                    reason="dynamic-import-default-binding", target=binding,
                ))
        for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
            if default is not None:
                binding = self._expr_binding(default)
                if binding:
                    self.aliases[argument.arg] = binding
                    self.dynamic.add(self._finding(
                        default, symbol=argument.arg, call=binding,
                        reason="dynamic-import-default-binding", target=binding,
                    ))
        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()
        returns: list[str] = []

        def collect(statement: ast.AST) -> None:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                return
            if isinstance(statement, ast.Return) and statement.value is not None:
                returns.append(self._expr_binding(statement.value))
                return
            for child in ast.iter_child_nodes(statement):
                collect(child)

        for statement in node.body:
            collect(statement)
        self.aliases = outer_aliases
        self.function_returns = outer_functions
        if any(returns) and (
            self.relative, node.name
        ) not in CONTROLLED_DYNAMIC_RETURN_FUNCTIONS:
            self.function_returns[node.name] = _DYNAMIC_CALLABLE
            self.aliases[node.name] = _DYNAMIC_FACTORY
            self.dynamic.add(self._finding(
                node, symbol=node.name, call="function-return",
                reason="dynamic-import-function-return",
                target=_DYNAMIC_CALLABLE,
            ))

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.targets.add((alias.name, "direct", node.lineno, node.col_offset, alias.name))
            self.aliases[alias.asname or alias.name.split(".")[0]] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = _relative_import(self.module, self.path, node.level, node.module)
        if not base:
            self.dynamic.add(self._finding(
                node, symbol=node.module or "", call="import-from",
                reason="invalid-relative-import", target="UNRESOLVED",
            ))
            return
        edge_type = "relative" if node.level else "from"
        self.targets.add((base, edge_type, node.lineno, node.col_offset, node.module or ""))
        for alias in node.names:
            if alias.name == "*":
                self.dynamic.add(self._finding(
                    node, symbol="*", call="import", reason="star-import",
                    target=base,
                ))
                continue
            candidate = f"{base}.{alias.name}"
            candidate_path, forbidden = _module_lexical_path(candidate)
            if candidate_path is not None or forbidden:
                self.targets.add((candidate, edge_type, node.lineno, node.col_offset, alias.name))
            self.aliases[alias.asname or alias.name] = candidate

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func, self.aliases)
        if name in {"__import__", "builtins.__import__", "importlib.import_module"} or name.endswith(".import_module"):
            if node.args and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str:
                self.targets.add((node.args[0].value, "dynamic", node.lineno, node.col_offset, name))
            else:
                self.dynamic.add(self._finding(
                    node, symbol=name, call=name,
                    reason="nonliteral-dynamic-import-target",
                    target=ast.dump(node.args[0], include_attributes=False) if node.args else "MISSING",
                ))
        elif name == _DYNAMIC_CALLABLE:
            self.dynamic.add(self._finding(
                node, symbol=name, call=ast.dump(node.func, include_attributes=False),
                reason="indirect-dynamic-import-callable", target="UNRESOLVED",
            ))
        elif self._expr_binding(node.func) == _DYNAMIC_CALLABLE:
            self.dynamic.add(self._finding(
                node, symbol=_DYNAMIC_CALLABLE,
                call=ast.dump(node.func, include_attributes=False),
                reason="value-expression-dynamic-import-callable",
                target="UNRESOLVED",
            ))
        if name in {"eval", "exec", "compile"}:
            self.dynamic.add(self._finding(
                node, symbol=name, call=name, reason="runtime-code-construction",
                target="UNRESOLVED",
            ))
        if name in {"getattr", "builtins.getattr"}:
            target = _call_name(node.args[0], self.aliases) if node.args else ""
            attribute = (
                node.args[1].value
                if len(node.args) > 1
                and isinstance(node.args[1], ast.Constant)
                and type(node.args[1].value) is str
                else None
            )
            if target == "importlib" or attribute in {"import_module", "__import__"}:
                self.dynamic.add(self._finding(
                    node, symbol=name, call=name,
                    reason="getattr-import-construction", target=attribute or target,
                ))
        if isinstance(node.func, ast.Call):
            inner = _call_name(node.func.func, self.aliases)
            if inner in {"getattr", "builtins.getattr"}:
                self.dynamic.add(self._finding(
                    node, symbol=inner, call=inner,
                    reason="called-getattr-construction", target="UNRESOLVED",
                ))
        function = self.function_stack[-1] if self.function_stack else "<module>"
        controlled = (self.relative, function) in CONTROLLED_EFFECT_FUNCTIONS
        effect = (
            name in EFFECT_CALLS
            or any(name.startswith(prefix) for prefix in EFFECT_PREFIXES)
            or any(token in name.lower() for token in ("guardian", "broker", "shim", "worker"))
        )
        if effect and not controlled:
            self.effects.add(self._finding(
                node, symbol=name, call=name, reason="deferred-effect",
                target=function,
            ))
        self.generic_visit(node)


def conservative_import_closure(start_modules: Iterable[str]) -> ImportClosure:
    starts = tuple(start_modules)
    if not starts or any(type(value) is not str for value in starts) or len(starts) != len(set(starts)):
        raise I7HarnessError("start modules must be a non-empty unique exact sequence")
    queue = list(starts)
    visited_paths: set[str] = set()
    edges: set[ImportEdge] = set()
    identities: dict[str, FileIdentity] = {}
    dynamic: set[ClosureFinding] = set()
    unresolved: set[ClosureFinding] = set()
    forbidden_edges: set[ClosureFinding] = set()
    effects: set[ClosureFinding] = set()
    while queue:
        module = queue.pop(0)
        path, forbidden = _module_lexical_path(module)
        if forbidden:
            lexical = path.relative_to(PROJECT_ROOT).as_posix() if path else module
            forbidden_edges.add(ClosureFinding(
                "<start>", 0, 0, module, "import", "forbidden-start", lexical,
            ))
            continue
        if path is None:
            if module in starts or module.split(".")[0] in LOCAL_TOP_LEVELS:
                unresolved.add(ClosureFinding(
                    "<start>", 0, 0, module, "import", "unresolved-local-start", module,
                ))
            continue
        all_paths = (*_package_initializers(module, path), path)
        for current_path in all_paths:
            current_relative = current_path.relative_to(PROJECT_ROOT).as_posix()
            if current_relative in visited_paths:
                if current_path != path:
                    edges.add(ImportEdge(
                        path.relative_to(PROJECT_ROOT).as_posix(), _module_name(path),
                        current_relative, _module_name(current_path), "implicit_init",
                        "RESOLVED", 0, 0, "", "package-initializer",
                        "implicit-package-initializer",
                    ))
                continue
            payload, identity = _read_file_exact(current_path, expected_root=PROJECT_ROOT)
            visited_paths.add(current_relative)
            identities[current_relative] = identity
            if current_path != path:
                edges.add(ImportEdge(
                    path.relative_to(PROJECT_ROOT).as_posix(), _module_name(path),
                    current_relative, _module_name(current_path), "implicit_init",
                    "RESOLVED", 0, 0, "", "package-initializer",
                    "implicit-package-initializer",
                ))
            try:
                tree = ast.parse(payload, filename=current_relative)
            except (SyntaxError, ValueError) as exc:
                raise I7HarnessError(f"AST parse failed: {current_relative}") from exc
            current_module = _module_name(current_path)
            visitor = _ClosureVisitor(current_relative, current_module, current_path)
            visitor.visit(tree)
            dynamic.update(visitor.dynamic)
            effects.update(visitor.effects)
            for target, edge_type, line, column, symbol in sorted(visitor.targets):
                target_path, target_forbidden = _module_lexical_path(target)
                if target_forbidden:
                    lexical = target_path.relative_to(PROJECT_ROOT).as_posix() if target_path else target
                    forbidden_edges.add(ClosureFinding(
                        current_relative, line, column, symbol, edge_type,
                        "forbidden-import-target", lexical,
                    ))
                    edges.add(ImportEdge(
                        current_relative, current_module, lexical, target,
                        edge_type, "FORBIDDEN", line, column, symbol,
                        edge_type, "forbidden-import-target",
                    ))
                    continue
                if target_path is None:
                    if target.split(".")[0] in LOCAL_TOP_LEVELS:
                        unresolved.add(ClosureFinding(
                            current_relative, line, column, symbol, edge_type,
                            "unresolved-local-import", target,
                        ))
                        edges.add(ImportEdge(
                            current_relative, current_module, "", target,
                            edge_type, "UNRESOLVED", line, column, symbol,
                            edge_type, "unresolved-local-import",
                        ))
                    continue
                target_relative = target_path.relative_to(PROJECT_ROOT).as_posix()
                edges.add(ImportEdge(
                    current_relative, current_module, target_relative,
                    _module_name(target_path), edge_type, "RESOLVED", line, column,
                    symbol, edge_type, "resolved-local-import",
                ))
                queue.append(_module_name(target_path))
            for finding in visitor.dynamic:
                edges.add(ImportEdge(
                    current_relative, current_module, "", finding.target,
                    "dynamic", "DYNAMIC", finding.line, finding.column,
                    finding.symbol, finding.call, finding.reason,
                ))
    return ImportClosure(
        starts,
        tuple(sorted(visited_paths)),
        tuple(sorted(edges)),
        tuple(identities[key] for key in sorted(identities)),
        tuple(sorted(dynamic)),
        tuple(sorted(unresolved)),
        tuple(sorted(forbidden_edges)),
        tuple(sorted(effects)),
    )


def assert_safe_closure(closure: ImportClosure, *, allow_effects: bool = False) -> None:
    if closure.forbidden_edges:
        raise I7HarnessError(f"forbidden import edge: {closure.forbidden_edges!r}")
    if closure.dynamic_imports:
        raise I7HarnessError(f"dynamic import boundary: {closure.dynamic_imports!r}")
    if closure.unresolved_local_imports:
        raise I7HarnessError(f"unresolved local import: {closure.unresolved_local_imports!r}")
    if closure.effect_edges and not allow_effects:
        raise I7HarnessError(f"deferred effect edge: {closure.effect_edges!r}")


def static_test_count(modules: Iterable[str]) -> int:
    count = 0
    for module in modules:
        path, forbidden = _module_lexical_path(module)
        if forbidden or path is None:
            raise I7HarnessError(f"test module missing/forbidden: {module}")
        payload, _ = _read_file_exact(path, expected_root=PROJECT_ROOT)
        tree = ast.parse(payload, filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                count += sum(
                    isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and member.name.startswith("test")
                    for member in node.body
                )
    return count


def _identity_record(identity: FileIdentity) -> dict[str, object]:
    return {
        "path": identity.path, "realpath": identity.realpath,
        "sha256": identity.sha256, "size": identity.size, "mode": identity.mode,
        "uid": identity.uid, "gid": identity.gid, "device": identity.device,
        "inode": identity.inode,
    }


def _edge_record(edge: ImportEdge) -> dict[str, object]:
    return {
        "from_path": edge.from_path, "from_module": edge.from_module,
        "to_path": edge.to_path, "to_module": edge.to_module,
        "edge_type": edge.edge_type,
        "resolution_status": edge.resolution_status,
        "line": edge.line, "column": edge.column,
        "symbol": edge.symbol, "call": edge.call, "reason": edge.reason,
    }


def _finding_record(finding: ClosureFinding) -> dict[str, object]:
    return {
        "path": finding.path, "line": finding.line, "column": finding.column,
        "symbol": finding.symbol, "call": finding.call,
        "reason": finding.reason, "target": finding.target,
    }


def plan_gate(gate_id: str, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if type(gate_id) is not str or gate_id not in PINNED_GATE_AUTHORITY:
        raise I7HarnessError(f"unknown gate: {gate_id}")
    gate = next(value for value in manifest["gates"] if value["id"] == gate_id)
    if gate["kind"] == "census":
        candidates = tuple(gate["candidate_modules"])
        if (
            type(gate["candidate_modules"]) is not list
            or type(gate["local_safe_modules"]) is not list
            or type(gate["deferred_modules"]) is not list
            or set(gate["local_safe_modules"]).intersection(gate["deferred_modules"])
            or set(gate["local_safe_modules"]).union(gate["deferred_modules"]) != set(candidates)
            or len(candidates) != len(set(candidates))
        ):
            raise I7HarnessError("census partition is invalid")
        closure = conservative_import_closure(candidates)
        if static_test_count(candidates) != gate["census_count"]:
            raise I7HarnessError("census count mismatch")
        return {
            "gate": gate,
            "census_only": True,
            "census_count": gate["census_count"],
            "execution_claim": False,
            "closure": _closure_record(closure),
        }
    modules = tuple(gate["modules"]) if gate["kind"] == "unittest" else (gate["module"],)
    closure = conservative_import_closure(modules)
    assert_safe_closure(closure, allow_effects=gate_id == "preparation_components")
    if gate["kind"] == "unittest" and static_test_count(modules) != gate["expected_count"]:
        raise I7HarnessError("static test count mismatch")
    return {"gate": gate, "census_only": False, "closure": _closure_record(closure)}


def _closure_record(closure: ImportClosure) -> dict[str, object]:
    edges = [_edge_record(value) for value in closure.edges]
    forbidden = [_finding_record(value) for value in closure.forbidden_edges]
    dynamic = [_finding_record(value) for value in closure.dynamic_imports]
    unresolved = [_finding_record(value) for value in closure.unresolved_local_imports]
    effects = [_finding_record(value) for value in closure.effect_edges]
    resolved_edges = [
        value for value in edges if value["resolution_status"] == "RESOLVED"
    ]
    syntactic = [
        value for value in resolved_edges if value["edge_type"] != "implicit_init"
    ]
    implicit = [
        value for value in resolved_edges if value["edge_type"] == "implicit_init"
    ]
    return {
        "start_modules": list(closure.start_modules),
        "file_count": len(closure.files),
        "edge_count": len(resolved_edges),
        "topology_edge_count": len(edges),
        "syntactic_edge_count": len(syntactic),
        "implicit_initializer_edge_count": len(implicit),
        "edges": edges,
        "files": list(closure.files),
        "file_identities": [_identity_record(value) for value in closure.identities],
        "forbidden_edge_count": len(forbidden),
        "forbidden_edges": forbidden,
        "dynamic_import_count": len(dynamic),
        "dynamic_imports": dynamic,
        "unresolved_local_import_count": len(unresolved),
        "unresolved_local_imports": unresolved,
        "effect_edge_count": len(effects),
        "effect_edges": effects,
    }


def _validate_closure_record_counts(value: Mapping[str, object]) -> None:
    list_counts = {
        "topology_edge_count": "edges",
        "forbidden_edge_count": "forbidden_edges",
        "dynamic_import_count": "dynamic_imports",
        "unresolved_local_import_count": "unresolved_local_imports",
        "effect_edge_count": "effect_edges",
    }
    if any(
        type(value.get(count)) is not int
        or type(value.get(items)) is not list
        or value[count] != len(value[items])
        for count, items in list_counts.items()
    ):
        raise I7HarnessError("closure counts are not derived from exact lists")
    edges = value["edges"]
    resolved = [item for item in edges if item["resolution_status"] == "RESOLVED"]
    syntactic = [item for item in resolved if item["edge_type"] != "implicit_init"]
    implicit = [item for item in resolved if item["edge_type"] == "implicit_init"]
    if (
        value.get("edge_count") != len(resolved)
        or value.get("syntactic_edge_count") != len(syntactic)
        or value.get("implicit_initializer_edge_count") != len(implicit)
        or value.get("file_count") != len(value.get("files", []))
    ):
        raise I7HarnessError("closure topology counts are not list-derived")


def _semantic_closure_record(value: Mapping[str, object]) -> dict[str, object]:
    _validate_closure_record_counts(value)
    identities = value.get("file_identities")
    files = value.get("files")
    if type(identities) is not list or type(files) is not list or len(identities) != len(files):
        raise I7HarnessError("closure semantic file identity mismatch")
    semantic_files = []
    for logical_path, identity in zip(files, identities):
        if type(logical_path) is not str or type(identity) is not dict:
            raise I7HarnessError("closure semantic file record mismatch")
        semantic_files.append({
            "logical_path": logical_path,
            "sha256": identity["sha256"], "size": identity["size"],
        })
    return {
        key: value[key] for key in (
            "start_modules", "file_count", "edge_count", "topology_edge_count",
            "syntactic_edge_count", "implicit_initializer_edge_count", "edges",
            "forbidden_edge_count", "forbidden_edges", "dynamic_import_count",
            "dynamic_imports", "unresolved_local_import_count",
            "unresolved_local_imports", "effect_edge_count", "effect_edges",
        )
    } | {"semantic_files": semantic_files}


def _semantic_gate_manifest(value: Mapping[str, object]) -> dict[str, object]:
    if type(value) is not dict:
        raise I7HarnessError("gate manifest semantic source mismatch")
    semantic = {
        key: value[key] for key in (
            "artifact_type", "schema_version", "manifest_id",
            "forbidden_paths", "global_timeout_seconds", "evidence_contract",
            "gates", "staged_synthetic_replay", "capability_external_binding",
            "workstation_external_binding", "collector_external_binding",
        )
    }
    schema = value.get("workstation_contract_schema")
    if type(schema) is not dict:
        raise I7HarnessError("workstation schema semantic binding is missing")
    semantic["canonical_repository_role"] = "PROJECT_ROOT"
    semantic["workstation_contract_schema"] = {
        key: schema[key] for key in ("path", "schema_id", "sha256", "mode")
    }
    encoded = _canonical(semantic)
    forbidden_fragments = (
        str(PROJECT_ROOT).encode("ascii"), str(Path.home()).encode("ascii"),
        b'"uid"', b'"gid"', b'"device"', b'"inode"',
    )
    if any(fragment in encoded for fragment in forbidden_fragments):
        raise I7HarnessError("host data survived gate-manifest canonicalization")
    return semantic


def _semantic_repository_record(value: Mapping[str, object]) -> dict[str, object]:
    semantics = value.get("semantics")
    if type(semantics) is not dict or type(value.get("records")) is not list:
        raise I7HarnessError("repository semantic source mismatch")
    git_semantics = semantics.get("git_semantics")
    if type(git_semantics) is not dict or type(git_semantics.get("ignore_files")) is not list:
        raise I7HarnessError("git semantic source mismatch")
    ignore_files = []
    for item in git_semantics["ignore_files"]:
        if type(item) is not dict:
            raise I7HarnessError("git ignore semantic record mismatch")
        semantic = {
            key: item[key] for key in ("role", "present")
        }
        if item["present"] is True:
            semantic.update({
                key: item[key] for key in ("sha256", "size", "mode")
            })
        ignore_files.append(semantic)
    config_sources = []
    for item in git_semantics.get("config_sources", []):
        if type(item) is not dict:
            raise I7HarnessError("Git config-source semantic record mismatch")
        semantic = {key: item[key] for key in ("role", "present")}
        if item["present"] is True:
            semantic.update({
                key: item[key] for key in ("sha256", "size", "mode")
            })
        config_sources.append(semantic)
    records = []
    for item in value["records"]:
        if type(item) is not dict or type(item.get("path")) is not str:
            raise I7HarnessError("repository semantic record mismatch")
        if item["path"] == EVIDENCE_RELATIVE_PATH:
            records.append({
                "path": item["path"], "mode": item["mode"],
                "content": "RAW_RUN_ROOT_ONLY_SELF_REFERENCE_BREAK",
            })
            continue
        record = {
            key: item[key] for key in (
                "path", "mode", "size", "nlink", "symlink_target"
            )
        }
        if type(record["symlink_target"]) is str and Path(
            record["symlink_target"]
        ).is_absolute():
            record["symlink_target"] = "@HOST_ABSOLUTE_SYMLINK"
        if "sha256" in item:
            record["sha256"] = item["sha256"]
        if "content" in item:
            record["content"] = item["content"]
        records.append(record)
    return {
        "git_status_nul_sha256": semantics["git_status_nul_sha256"],
        "canonical_git_config": git_semantics["canonical_config"],
        "canonical_git_config_sha256": git_semantics[
            "canonical_config_sha256"
        ],
        "member_count": semantics["member_count"],
        "members_sha256": semantics["members_sha256"],
        "config_sources": config_sources,
        "ignore_files": ignore_files,
        "records": records,
    }


def _validate_schema(value: object, schema: Mapping[str, Any], path: str = "$") -> None:
    if type(schema) is not dict:
        raise I7HarnessError(f"{path}: malformed schema")
    expected_type = schema.get("type")
    matches = {
        "object": type(value) is dict, "array": type(value) is list,
        "string": type(value) is str, "integer": type(value) is int,
        "boolean": type(value) is bool,
    }
    if expected_type is not None and (type(expected_type) is not str or not matches.get(expected_type, False)):
        raise I7HarnessError(f"{path}: expected {expected_type}")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise I7HarnessError(f"{path}: const/type mismatch")
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        raise I7HarnessError(f"{path}: enum/type mismatch")
    if type(value) is str:
        if len(value) < schema.get("minLength", 0):
            raise I7HarnessError(f"{path}: string too short")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise I7HarnessError(f"{path}: pattern mismatch")
    if type(value) is int and value < schema.get("minimum", value):
        raise I7HarnessError(f"{path}: integer below minimum")
    if type(value) is list:
        if len(value) < schema.get("minItems", 0):
            raise I7HarnessError(f"{path}: array too short")
        if schema.get("uniqueItems") is True and len({_canonical(item) for item in value}) != len(value):
            raise I7HarnessError(f"{path}: duplicate array item")
        if "items" in schema:
            for index, item in enumerate(value):
                _validate_schema(item, schema["items"], f"{path}[{index}]")
    if type(value) is dict:
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        if type(required) is not list or any(type(item) is not str for item in required) or type(properties) is not dict:
            raise I7HarnessError(f"{path}: malformed object schema")
        if not set(required).issubset(value):
            raise I7HarnessError(f"{path}: missing fields")
        if schema.get("additionalProperties") is False and not set(value).issubset(properties):
            raise I7HarnessError(f"{path}: unknown fields")
        for key, item in value.items():
            if key in properties:
                _validate_schema(item, properties[key], f"{path}.{key}")


def _absolute_confined(path_text: str, root_text: str) -> tuple[Path, Path]:
    if type(path_text) is not str or type(root_text) is not str:
        raise I7HarnessError("file input paths must be exact strings")
    path = Path(path_text)
    root = Path(root_text)
    if not path.is_absolute() or not root.is_absolute() or ".." in path.parts or ".." in root.parts:
        raise I7HarnessError("file input path traversal/relative path")
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise I7HarnessError("file input escapes confinement root")
    return path, root


def _directory_chain_record(
    logical_path: Path, component: str, value: os.stat_result,
) -> dict[str, object]:
    return {
        "logical_path": str(logical_path), "path_component": component,
        "device": value.st_dev, "inode": value.st_ino,
        "uid": value.st_uid, "gid": value.st_gid,
        "mode": stat.S_IMODE(value.st_mode), "expected_type": "DIRECTORY",
    }


def _open_absolute_directory_chain(
    path: Path,
) -> tuple[list[int], list[tuple[Path, str, os.stat_result]]]:
    if not path.is_absolute() or ".." in path.parts:
        raise I7HarnessError("directory chain path is invalid")
    descriptors = [
        os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    ]
    observations = [(Path("/"), "/", os.fstat(descriptors[0]))]
    logical = Path("/")
    try:
        for component in path.parts[1:]:
            next_descriptor = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptors[-1],
            )
            descriptors.append(next_descriptor)
            logical /= component
            observations.append((logical, component, os.fstat(next_descriptor)))
        return descriptors, observations
    except Exception:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _read_confined_contract_file(
    path: Path, root: Path, record: Mapping[str, Any]
) -> tuple[bytes, FileIdentity]:
    absolute_descriptors, observations = _open_absolute_directory_chain(root)
    descriptors = list(absolute_descriptors)
    root_descriptor = descriptors[-1]
    root_stat = observations[-1][2]
    parent_links: list[tuple[int, str, int]] = [
        (descriptors[index], observations[index + 1][1], descriptors[index + 1])
        for index in range(len(descriptors) - 1)
    ]
    try:
        expected_root = {
            "root_mode": stat.S_IMODE(root_stat.st_mode),
            "root_uid": root_stat.st_uid, "root_gid": root_stat.st_gid,
            "root_device": root_stat.st_dev, "root_inode": root_stat.st_ino,
        }
        if any(
            type(record[key]) is not type(value) or record[key] != value
            for key, value in expected_root.items()
        ):
            raise I7HarnessError("confinement root identity mismatch")
        if root_stat.st_mode & 0o022:
            raise I7HarnessError("confinement root is group/world writable")
        root_index = len(observations) - 1
        for index, (_, _, parent_stat) in enumerate(observations):
            if not stat.S_ISDIR(parent_stat.st_mode):
                raise I7HarnessError("non-directory in absolute parent chain")
            if index >= root_index and (
                parent_stat.st_uid != root_stat.st_uid
                or parent_stat.st_gid != root_stat.st_gid
                or parent_stat.st_dev != root_stat.st_dev
                or parent_stat.st_mode & 0o022
            ):
                raise I7HarnessError("confinement parent authority mismatch")
            if index < root_index and (
                parent_stat.st_mode & 0o002
                and not parent_stat.st_mode & stat.S_ISVTX
            ):
                raise I7HarnessError("unsafe world-writable absolute parent")
        relative = path.relative_to(root)
        if not relative.parts:
            raise I7HarnessError("file input cannot equal confinement root")
        parent_descriptor = root_descriptor
        for component in relative.parts[:-1]:
            descriptor = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent_descriptor,
            )
            descriptors.append(descriptor)
            opened_parent = os.fstat(descriptor)
            parent_links.append((parent_descriptor, component, descriptor))
            parent_descriptor = descriptor
            parent_stat = opened_parent
            observations.append((
                observations[-1][0] / component, component, opened_parent,
            ))
            if (
                not stat.S_ISDIR(parent_stat.st_mode)
                or parent_stat.st_uid != record["root_uid"]
                or parent_stat.st_gid != record["root_gid"]
                or parent_stat.st_dev != record["root_device"]
                or parent_stat.st_mode & 0o022
            ):
                raise I7HarnessError("file input parent-chain contract mismatch")

        observed_contract = [
            _directory_chain_record(logical, component, value)
            for logical, component, value in observations
        ]
        if type(record.get("parent_chain")) is not list or record["parent_chain"] != observed_contract:
            raise I7HarnessError("file input exact parent-chain metadata mismatch")

        def verify_chain() -> None:
            for parent_fd, component, child_fd in parent_links:
                current = os.stat(
                    component, dir_fd=parent_fd, follow_symlinks=False
                )
                opened = os.fstat(child_fd)
                current_key = (
                    current.st_dev, current.st_ino, current.st_uid,
                    current.st_gid, current.st_mode,
                )
                opened_key = (
                    opened.st_dev, opened.st_ino, opened.st_uid,
                    opened.st_gid, opened.st_mode,
                )
                if current_key != opened_key or not stat.S_ISDIR(opened.st_mode):
                    raise I7HarnessError("contract parent chain changed during read")

        verify_chain()
        flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_NOATIME"):
            flags |= os.O_NOATIME
        try:
            leaf_descriptor = os.open(
                relative.parts[-1], flags, dir_fd=parent_descriptor
            )
        except PermissionError:
            leaf_descriptor = os.open(
                relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW,
                dir_fd=parent_descriptor,
            )
        descriptors.append(leaf_descriptor)
        initial = os.fstat(leaf_descriptor)
        if not stat.S_ISREG(initial.st_mode) or initial.st_nlink != 1:
            raise I7HarnessError("nonregular or hardlinked contract input")
        digest = hashlib.sha256()
        blocks: list[bytes] = []
        while True:
            block = os.read(leaf_descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
            digest.update(block)
        readback = os.fstat(leaf_descriptor)
        final = os.stat(
            relative.parts[-1], dir_fd=parent_descriptor, follow_symlinks=False
        )
        key = lambda value: (
            value.st_dev, value.st_ino, value.st_mode, value.st_uid,
            value.st_gid, value.st_size, value.st_atime_ns,
            value.st_mtime_ns, value.st_ctime_ns,
        )
        if key(initial) != key(readback) or key(readback) != key(final):
            raise I7HarnessError("contract file changed during descriptor-bound read")
        verify_chain()
        identity = FileIdentity(
            str(path), str(path), digest.hexdigest(), final.st_size,
            stat.S_IMODE(final.st_mode), final.st_uid, final.st_gid,
            final.st_dev, final.st_ino,
        )
        return b"".join(blocks), identity
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _verify_contract_file(record: Mapping[str, Any]) -> FileIdentity:
    path, root = _absolute_confined(record["path"], record["confinement_root"])
    payload, identity = _read_confined_contract_file(path, root, record)
    expected = {
        "sha256": identity.sha256, "size": identity.size, "mode": identity.mode,
        "uid": identity.uid, "gid": identity.gid, "device": identity.device,
        "inode": identity.inode,
    }
    if any(type(record[key]) is not type(value) or record[key] != value for key, value in expected.items()):
        raise I7HarnessError(f"file identity mismatch: {record['input_id']}")
    if identity.mode & 0o002:
        raise I7HarnessError("world-writable file input")
    if record["permission_policy"] == "PRIVATE_KEY" and identity.mode & 0o077:
        raise I7HarnessError("private key permissions are too broad")
    if record["permission_policy"] == "READ_ONLY_EXECUTABLE" and not identity.mode & 0o111:
        raise I7HarnessError("executable input lacks execute permission")
    if record["input_id"] in PINNED_CANONICAL_INPUTS:
        pinned_path, pinned_hash = PINNED_CANONICAL_INPUTS[record["input_id"]]
        if path != pinned_path or identity.sha256 != pinned_hash:
            raise I7HarnessError(f"canonical input mismatch: {record['input_id']}")
    if hashlib.sha256(payload).hexdigest() != record["sha256"]:
        raise I7HarnessError("file readback hash mismatch")
    return identity


def _read_external_contract(path: Path) -> dict[str, Any]:
    if not path.is_absolute() or ".." in path.parts or path.is_symlink():
        raise I7HarnessError("contract path must be absolute, no-symlink, traversal-free")
    resolved = path.resolve(strict=True)
    if resolved == Path("/tmp") or Path("/tmp") not in resolved.parents:
        raise I7HarnessError("contract must be under a bound /tmp root")
    payload, _ = _read_file_exact(path, expected_root=Path("/tmp"))
    value = _strict_json(payload, label="workstation contract")
    if type(value) is not dict:
        raise I7HarnessError("workstation contract must be an exact object")
    return value


def validate_workstation_contract(contract_path: Path, schema_path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    if schema_path.resolve(strict=True) != DEFAULT_SCHEMA.resolve(strict=True):
        raise I7HarnessError("only the canonical pinned schema is accepted")
    schema = _read_pinned_repository_json(DEFAULT_SCHEMA, PINNED_SCHEMA_SHA256, label="schema")
    if schema.get("schema_id") != PINNED_SCHEMA_ID:
        raise I7HarnessError("schema identifier mismatch")
    contract = _read_external_contract(contract_path)
    _validate_schema(contract, schema)
    if contract["cleanup"]["run_owner_id"] != contract["run_id"]:
        raise I7HarnessError("cleanup owner/run mismatch")
    capability = contract["capability"]
    trial_total = len(capability["scenario_ids"]) * 10000
    startup_total = len(capability["startup_scenario_ids"]) * 32
    if capability["expected_trial_count"] != trial_total or capability["expected_startup_probe_count"] != startup_total:
        raise I7HarnessError("capability scenario-derived count mismatch")
    inputs = contract["file_inputs"]
    ids = tuple(record["input_id"] for record in inputs)
    if len(ids) != len(set(ids)) or set(ids) != set(REQUIRED_FILE_INPUT_IDS):
        raise I7HarnessError("file input IDs are missing, unknown, or duplicate")
    identities = [_verify_contract_file(record) for record in inputs]
    aliases = [(value.device, value.inode) for value in identities]
    if len(aliases) != len(set(aliases)):
        raise I7HarnessError("hardlink/alias across file inputs")
    return contract


def _git_bytes(arguments: Sequence[str]) -> bytes:
    completed = subprocess.run(
        ["git", "--no-optional-locks", *arguments], cwd=PROJECT_ROOT,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}, capture_output=True,
        check=True,
    )
    return completed.stdout


def _bound_git_environment() -> dict[str, str]:
    original_home = Path.home()
    result = {
        "XDG_CONFIG_HOME": os.environ.get(
            "XDG_CONFIG_HOME", str(original_home / ".config")
        ),
        "GIT_CONFIG_GLOBAL": os.environ.get(
            "GIT_CONFIG_GLOBAL", str(original_home / ".gitconfig")
        ),
    }
    for key in (
        "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_PARAMETERS",
        "GIT_CONFIG_COUNT", "GIT_ATTR_NOSYSTEM",
    ):
        if key in os.environ:
            result[key] = os.environ[key]
    try:
        count = int(result.get("GIT_CONFIG_COUNT", "0"))
    except ValueError as exc:
        raise I7HarnessError("invalid GIT_CONFIG_COUNT") from exc
    if count < 0 or count > 1024:
        raise I7HarnessError("invalid GIT_CONFIG_COUNT")
    for index in range(count):
        for prefix in ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"):
            key = f"{prefix}{index}"
            if key not in os.environ:
                raise I7HarnessError("incomplete command-scope Git configuration")
            result[key] = os.environ[key]
    return result


def _repository_members() -> tuple[str, ...]:
    visible = _git_bytes(("ls-files", "--cached", "--others", "--exclude-standard", "-z"))
    ignored = _git_bytes(("ls-files", "--others", "--ignored", "--exclude-standard", "-z"))
    members = {
        os.fsdecode(item) for payload in (visible, ignored)
        for item in payload.split(b"\0") if item
    }
    if any(path == ".git" or path.startswith(".git/") for path in members):
        raise I7HarnessError(".git entered repository member set")
    return tuple(sorted(members))


def _ignore_semantics_record(path: Path, role: str) -> dict[str, object]:
    lexical = str(path)
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return {"role": role, "path": lexical, "present": False}
    if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode):
        raise I7HarnessError(f"effective ignore is not a regular file: {path}")
    payload, identity = _read_file_exact(path)
    return {
        "role": role, "path": lexical, "present": True,
        "sha256": _sha256_bytes(payload), "size": identity.size,
        "mode": identity.mode, "uid": identity.uid, "gid": identity.gid,
        "device": identity.device, "inode": identity.inode,
        "mtime_ns": os.lstat(path).st_mtime_ns,
        "ctime_ns": os.lstat(path).st_ctime_ns,
    }


def _canonical_git_config(config: bytes, global_ignore: Path) -> list[list[str]]:
    result: list[list[str]] = []
    replacements = sorted({
        str(PROJECT_ROOT): "@PROJECT_ROOT",
        str(Path.home()): "@HOME",
        os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")): "@XDG",
        str(Path("/tmp")): "@TMP",
    }.items(), key=lambda item: len(item[0]), reverse=True)
    for raw in config.split(b"\0"):
        if not raw:
            continue
        key_raw, separator, value_raw = raw.partition(b"\n")
        if not separator:
            raise I7HarnessError("effective Git config framing mismatch")
        try:
            key = key_raw.decode("utf-8").lower()
            value = value_raw.decode("utf-8")
        except UnicodeError as exc:
            raise I7HarnessError("effective Git config is not UTF-8") from exc
        if key == "core.excludesfile":
            value = "@EFFECTIVE_GLOBAL_IGNORE"
        elif key == "include.path" or (
            key.startswith("includeif.") and key.endswith(".path")
        ):
            continue
        else:
            for source, replacement in replacements:
                value = value.replace(source, replacement)
            if value.startswith("/"):
                value = "@HOST_ABSOLUTE_PATH"
        result.append([key, value])
    if global_ignore.is_absolute() and any(
        str(global_ignore) in value for _, value in result
    ):
        raise I7HarnessError("host path survived Git semantic canonicalization")
    return result


def _effective_git_semantics() -> dict[str, object]:
    config = _git_bytes(("config", "--null", "--list", "--show-origin"))
    effective_config = _git_bytes(("config", "--null", "--list"))
    configured_result = subprocess.run(
        ["git", "--no-optional-locks", "config", "--path", "--get", "core.excludesFile"],
        cwd=PROJECT_ROOT, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        capture_output=True, check=False,
    )
    if configured_result.returncode not in {0, 1}:
        raise I7HarnessError("effective core.excludesFile query failed")
    configured = configured_result.stdout
    configured_path = configured.rstrip(b"\n")
    if configured_path:
        global_ignore = Path(os.fsdecode(configured_path)).expanduser()
        global_role = "core.excludesFile"
    else:
        xdg = Path(
            os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        )
        global_ignore = xdg / "git/ignore"
        global_role = "implicit-xdg-global-ignore"
    ignore_records = [
        _ignore_semantics_record(global_ignore, global_role),
        _ignore_semantics_record(PROJECT_ROOT / ".git/info/exclude", "local-info-exclude"),
    ]
    git_environment = _bound_git_environment()
    system_path = Path(git_environment.get("GIT_CONFIG_SYSTEM", "/etc/gitconfig"))
    global_path = Path(git_environment["GIT_CONFIG_GLOBAL"])
    xdg_path = Path(git_environment["XDG_CONFIG_HOME"]) / "git/config"
    config_sources = [
        _ignore_semantics_record(system_path, "system-config"),
        _ignore_semantics_record(global_path, "global-config"),
        _ignore_semantics_record(xdg_path, "xdg-global-config"),
        _ignore_semantics_record(PROJECT_ROOT / ".git/config", "local-config"),
    ]
    canonical_config = _canonical_git_config(effective_config, global_ignore)
    base = {
        "config_nul_sha256": _sha256_bytes(config),
        "config_raw_nul_hex": config.hex(),
        "effective_config_nul_hex": effective_config.hex(),
        "canonical_config": canonical_config,
        "canonical_config_sha256": _sha256_bytes(_canonical(canonical_config)),
        "git_environment": git_environment,
        "config_sources": config_sources,
        "ignore_files": ignore_records,
    }
    return {**base, "semantic_sha256": _sha256_bytes(_canonical(base))}


def repository_state_manifest() -> dict[str, Any]:
    members = _repository_members()
    records: list[dict[str, object]] = []
    for relative in members:
        path = PROJECT_ROOT / relative
        try:
            st = os.lstat(path)
        except FileNotFoundError as exc:
            raise I7HarnessError(f"repository member disappeared: {relative}") from exc
        record: dict[str, object] = {
            "path": relative, "mode": st.st_mode, "uid": st.st_uid,
            "gid": st.st_gid, "device": st.st_dev, "inode": st.st_ino,
            "size": st.st_size, "nlink": st.st_nlink, "atime_ns": st.st_atime_ns,
            "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns,
            "symlink_target": os.readlink(path) if stat.S_ISLNK(st.st_mode) else None,
        }
        if stat.S_ISREG(st.st_mode):
            if relative in FORBIDDEN_PATHS:
                record["content"] = "EXCLUDED_FORBIDDEN_CONTENT"
            elif relative.endswith(".pyc"):
                record["content"] = "EXCLUDED_PYC_CONTENT"
            else:
                _, identity = _read_file_exact(path, expected_root=PROJECT_ROOT)
                record["sha256"] = identity.sha256
        records.append(record)
    git_status = _git_bytes(("status", "--porcelain=v1", "-z", "--untracked-files=all"))
    git_semantics = _effective_git_semantics()
    semantics = {
        "git_status_nul_sha256": _sha256_bytes(git_status),
        "git_config_raw_nul_sha256": git_semantics["config_nul_sha256"],
        "git_config_nul_sha256": git_semantics["semantic_sha256"],
        "git_ignore_semantics_sha256": git_semantics["semantic_sha256"],
        "git_semantics": git_semantics,
        "member_count": len(members),
        "members_sha256": _sha256_bytes(b"\0".join(os.fsencode(item) for item in members) + b"\0"),
    }
    base = {"schema_version": 2, "semantics": semantics, "records": records}
    return {**base, "manifest_sha256": _sha256_bytes(_canonical(base))}


def compare_repository_manifests(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[int, tuple[str, ...]]:
    before_records = {record["path"]: record for record in before["records"]}
    after_records = {record["path"]: record for record in after["records"]}
    changed = tuple(sorted(
        path for path in set(before_records).union(after_records)
        if before_records.get(path) != after_records.get(path)
    ))
    if before["semantics"] != after["semantics"]:
        changed = tuple(sorted(set(changed).union({"<git-semantics>"})))
    return len(changed), changed


def _group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _run_process_group(command: Sequence[str], *, cwd: Path, environment: Mapping[str, str], timeout_seconds: float, term_grace_seconds: float = 0.5, kill_grace_seconds: float = 1.0, pass_fds: Sequence[int] = (), readiness_tokens: Sequence[bytes] = (), readiness_timeout_seconds: float = 5.0) -> ProcessResult:
    if (
        timeout_seconds <= 0 or term_grace_seconds <= 0
        or kill_grace_seconds <= 0 or readiness_timeout_seconds <= 0
    ):
        raise I7HarnessError("process timeout/grace must be positive")
    if any(
        type(token) is not bytes or not token or not token.endswith(b"\n")
        or b"\n" in token[:-1]
        for token in readiness_tokens
    ) or len(set(readiness_tokens)) != len(tuple(readiness_tokens)):
        raise I7HarnessError("process readiness tokens are invalid")
    child_environment = dict(environment)
    inherited_fds = tuple(pass_fds)
    read_descriptor: int | None = None
    write_descriptor: int | None = None
    if readiness_tokens:
        if "I7_PROCESS_READY_FD" in child_environment:
            raise I7HarnessError("process readiness descriptor is preowned")
        read_descriptor, write_descriptor = os.pipe2(os.O_CLOEXEC)
        child_environment["I7_PROCESS_READY_FD"] = str(write_descriptor)
        inherited_fds = tuple(dict.fromkeys((*pass_fds, write_descriptor)))
    try:
        process = subprocess.Popen(
            list(command), cwd=cwd, env=child_environment,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, pass_fds=inherited_fds,
        )
    except BaseException:
        if read_descriptor is not None:
            os.close(read_descriptor)
        if write_descriptor is not None:
            os.close(write_descriptor)
        raise
    if write_descriptor is not None:
        os.close(write_descriptor)
    pgid = process.pid
    if read_descriptor is not None:
        expected_readiness = b"".join(readiness_tokens)
        observed_readiness = bytearray()
        readiness_complete = False
        readiness_failure: BaseException | None = None
        os.set_blocking(read_descriptor, False)
        deadline = time.monotonic() + readiness_timeout_seconds
        try:
            while time.monotonic() < deadline:
                try:
                    block = os.read(read_descriptor, 4096)
                except BlockingIOError:
                    time.sleep(0.01)
                    continue
                if not block:
                    readiness_complete = True
                    break
                observed_readiness.extend(block)
                if (
                    len(observed_readiness) > len(expected_readiness)
                    or not expected_readiness.startswith(observed_readiness)
                ):
                    break
        except BaseException as exc:
            readiness_failure = exc
        finally:
            os.close(read_descriptor)
        if (
            readiness_failure is not None or not readiness_complete
            or bytes(observed_readiness) != expected_readiness
        ):
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                process.communicate(timeout=kill_grace_seconds)
            except subprocess.TimeoutExpired as exc:
                raise I7HarnessError(
                    "process readiness failure could not be reaped"
                ) from exc
            deadline = time.monotonic() + kill_grace_seconds
            while _group_exists(pgid) and time.monotonic() < deadline:
                time.sleep(0.01)
            if _group_exists(pgid):
                raise I7HarnessError(
                    "process readiness failure left group residue"
                )
            raise I7HarnessError(
                "process readiness sequence mismatch"
            ) from readiness_failure
    term_sent = False
    kill_sent = False
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        term_sent = True
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=term_grace_seconds)
        except subprocess.TimeoutExpired:
            kill_sent = True
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=kill_grace_seconds)
            except subprocess.TimeoutExpired as exc:
                raise I7HarnessError("process group could not be reaped") from exc
    deadline = time.monotonic() + kill_grace_seconds
    while _group_exists(pgid) and time.monotonic() < deadline:
        time.sleep(0.01)
    if _group_exists(pgid):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=kill_grace_seconds)
    group_reaped = not _group_exists(pgid)
    if not group_reaped:
        raise I7HarnessError("child/grandchild process group leak")
    return ProcessResult(
        process.returncode, stdout, stderr, timed_out, group_reaped,
        term_sent, kill_sent, process.pid,
    )

def _write_new(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise I7HarnessError(f"output exists: {path}")
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _new_tmp_root(path: Path) -> Path:
    if not path.is_absolute() or ".." in path.parts or path.is_symlink():
        raise I7HarnessError("run root path is invalid")
    parent = path.parent.resolve(strict=True)
    if parent != Path("/tmp") and Path("/tmp") not in parent.parents:
        raise I7HarnessError("run root must be below /tmp")
    if path.exists():
        raise I7HarnessError("run root must be create-new")
    path.mkdir(mode=0o700)
    return path.resolve(strict=True)


def _parse_gate_count(kind: str, stdout: bytes, stderr: bytes) -> int:
    text = (stdout + b"\n" + stderr).decode("utf-8", errors="strict")
    if kind == "unittest":
        return -1
    matches = re.findall(r"^I7_STAGED_SYNTHETIC_REPLAY: (\d+)/(\d+) PASS$", text, re.MULTILINE)
    if len(matches) != 1 or matches[0][0] != matches[0][1]:
        return -1
    return int(matches[0][0])


def _read_authentic_unittest_result(
    payload: bytes, *, gate_id: str, run_id: str,
    nonce: str, child_pid: int, start_modules: Sequence[str], expected_count: int,
) -> dict[str, object]:
    if type(payload) is not bytes or len(payload) > 65536:
        raise I7HarnessError("unittest result-channel framing mismatch")
    value = _strict_json(payload, label="authentic unittest result")
    fields = {
        "artifact_type", "schema_version", "gate_id", "run_id", "nonce",
        "child_pid", "runner_sha256", "start_modules", "expected_count", "tests_run",
        "failures", "errors", "skipped", "unexpected_successes",
        "expected_failures", "result",
    }
    if type(value) is not dict or set(value) != fields:
        raise I7HarnessError("unittest result schema mismatch")
    exact = {
        "artifact_type": "IU4_I7_AUTHENTIC_UNITTEST_RESULT",
        "schema_version": 3, "gate_id": gate_id, "run_id": run_id,
        "nonce": nonce, "child_pid": child_pid,
        "runner_sha256": UNITTEST_SUPERVISOR_SHA256,
        "start_modules": list(start_modules), "expected_count": expected_count,
        "tests_run": expected_count, "failures": 0, "errors": 0,
        "skipped": 0, "unexpected_successes": 0, "expected_failures": 0,
        "result": "PASS",
    }
    if any(type(value[key]) is not type(expected) or value[key] != expected for key, expected in exact.items()):
        raise I7HarnessError("unittest result authority/count/failure mismatch")
    return value


def _read_terminal_result_pipe(descriptor: int) -> bytes:
    pipe_stat = os.fstat(descriptor)
    if not stat.S_ISFIFO(pipe_stat.st_mode):
        raise I7HarnessError("unittest result reader is not a pipe")
    blocks: list[bytes] = []
    size = 0
    while True:
        block = os.read(descriptor, 65536)
        if not block:
            break
        size += len(block)
        if size > 65536:
            raise I7HarnessError("unittest result pipe exceeded protocol limit")
        blocks.append(block)
    return b"".join(blocks)


def _deterministic_semantic_root(value: Mapping[str, object]) -> str:
    return _sha256_bytes(_canonical({
        "artifact_type": "IU4_I7_DETERMINISTIC_SEMANTIC_ATTESTATION",
        "schema_version": 1,
        **dict(value),
    }))


def _run_attestation_root(value: Mapping[str, object]) -> str:
    return _sha256_bytes(_canonical({
        "artifact_type": "IU4_I7_RUN_ATTESTATION",
        "schema_version": 1,
        **dict(value),
    }))


def run_gate(gate_id: str, *, manifest_path: Path = DEFAULT_MANIFEST, run_root: Path) -> dict[str, Any]:
    started_monotonic = time.monotonic()
    plan = plan_gate(gate_id, manifest_path)
    gate = plan["gate"]
    if gate["kind"] == "census":
        raise I7HarnessError("census/deferred gate is never executable")
    root = _new_tmp_root(run_root)
    gate_root = root / gate_id
    gate_root.mkdir(mode=0o700)
    tmp = gate_root / "tmp"
    pycache = gate_root / "pycache"
    home = gate_root / "home"
    for path in (tmp, pycache, home):
        path.mkdir(mode=0o700)
    before = repository_state_manifest()
    _write_new(root / "repository_before.json", _canonical(before) + b"\n")
    # Directly-before-spawn TOCTOU revalidation of pinned manifest and closure.
    spawn_plan = plan_gate(gate_id, DEFAULT_MANIFEST)
    if spawn_plan != plan:
        raise I7HarnessError("plan changed before spawn")
    python = PROJECT_ROOT / ".venv/bin/python"
    nonce = os.urandom(32).hex()
    run_id = "IU4-I7-GATE-" + nonce.upper()
    result_reader: int | None = None
    result_writer: int | None = None
    if gate["kind"] == "unittest":
        result_reader, result_writer = os.pipe2(os.O_CLOEXEC)
        command = [str(python), "-c", UNITTEST_SUPERVISOR_RUNNER]
    else:
        command = [
            str(python), "-m", gate["module"], "--run-root",
            str(gate_root / "payload"),
        ]
    environment = {
        "PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(PROJECT_ROOT),
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPYCACHEPREFIX": str(pycache),
        "TMPDIR": str(tmp), "HOME": str(home), "LC_ALL": "C.UTF-8",
        "GIT_OPTIONAL_LOCKS": "0",
        **_bound_git_environment(),
    }
    if result_writer is not None:
        environment.update({
            "I7_RESULT_FD": str(result_writer),
            "I7_RESULT_GATE_ID": gate_id,
            "I7_RESULT_RUN_ID": run_id,
            "I7_RESULT_NONCE": nonce,
            "I7_RESULT_RUNNER_SHA256": UNITTEST_SUPERVISOR_SHA256,
            "I7_RESULT_START_MODULES": json.dumps(
                gate["modules"], separators=(",", ":")
            ),
            "I7_RESULT_EXPECTED_COUNT": str(gate["expected_count"]),
        })
    global_timeout = load_manifest()["global_timeout_seconds"]
    remaining = min(
        float(gate["timeout_seconds"]),
        float(global_timeout) - (time.monotonic() - started_monotonic),
    )
    if remaining <= 0:
        raise I7HarnessError("global timeout expired before gate spawn")
    started_ns = time.time_ns()
    try:
        completed = _run_process_group(
            command, cwd=PROJECT_ROOT, environment=environment,
            timeout_seconds=remaining,
            pass_fds=(() if result_writer is None else (result_writer,)),
        )
    finally:
        if result_writer is not None:
            os.close(result_writer)
    ended_ns = time.time_ns()
    stdout_path = gate_root / "stdout.txt"
    stderr_path = gate_root / "stderr.txt"
    _write_new(stdout_path, completed.stdout)
    _write_new(stderr_path, completed.stderr)
    authentic_result: dict[str, object] | None = None
    try:
        if result_reader is not None:
            result_payload = _read_terminal_result_pipe(result_reader)
            authentic_result = _read_authentic_unittest_result(
                result_payload, gate_id=gate_id,
                run_id=run_id, nonce=nonce, child_pid=completed.child_pid,
                start_modules=gate["modules"],
                expected_count=gate["expected_count"],
            )
            actual = int(authentic_result["tests_run"])
        else:
            actual = _parse_gate_count(
                gate["kind"], completed.stdout, completed.stderr
            )
    finally:
        if result_reader is not None:
            os.close(result_reader)
    after = repository_state_manifest()
    _write_new(root / "repository_after.json", _canonical(after) + b"\n")
    output_count, changed = compare_repository_manifests(before, after)
    if (
        completed.timed_out or completed.return_code != 0
        or actual != gate["expected_count"] or output_count != 0
        or not completed.group_reaped
    ):
        raise I7HarnessError(
            f"gate failed rc={completed.return_code} timeout={completed.timed_out} "
            f"expected={gate['expected_count']} actual={actual} outputs={output_count} "
            f"changed={changed!r}"
        )
    evidence_base = {
        "artifact_type": "IU4_I7_LOCAL_GATE_EVIDENCE",
        "schema_version": 2,
        "gate_id": gate_id,
        "command": command,
        "return_code": completed.return_code,
        "expected_count": gate["expected_count"],
        "actual_count": actual,
        "authentic_unittest_result": authentic_result,
        "started_ns": started_ns,
        "ended_ns": ended_ns,
        "duration_ns": ended_ns - started_ns,
        "timeout_seconds": gate["timeout_seconds"],
        "global_timeout_seconds": global_timeout,
        "stdout_sha256": _sha256_bytes(completed.stdout),
        "stderr_sha256": _sha256_bytes(completed.stderr),
        "import_effect_closure": plan["closure"],
        "repository_before_manifest_sha256": before["manifest_sha256"],
        "repository_after_manifest_sha256": after["manifest_sha256"],
        "repository_output_count": output_count,
        "changed_repository_paths": list(changed),
        "process_group": {
            "child_pid": completed.child_pid,
            "timed_out": completed.timed_out,
            "term_sent": completed.term_sent,
            "kill_sent": completed.kill_sent,
            "group_reaped": completed.group_reaped,
        },
        "cleanup_result": "NO_REAL_RESOURCES_CREATED_OR_CLEANED",
        "result": "PASS",
    }
    evidence = {
        **evidence_base,
        "evidence_sha256": _sha256_bytes(_canonical(evidence_base)),
    }
    evidence_path = gate_root / "gate_evidence.json"
    _write_new(evidence_path, _canonical(evidence) + b"\n")
    artifacts: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.name != "final_attestation.json":
            artifacts[path.relative_to(root).as_posix()] = _read_file_exact(path, expected_root=root)[1].sha256
    artifact_manifest = {
        "schema_version": 2, "gate_id": gate_id, "artifacts": artifacts,
    }
    artifact_manifest_hash = _sha256_bytes(_canonical(artifact_manifest))
    semantic_closure = _semantic_closure_record(plan["closure"])
    semantic_repository = _semantic_repository_record(before)
    semantic_material = {
        "gate_id": gate_id,
        "gate_manifest": _semantic_gate_manifest(load_manifest()),
        "expected_count": gate["expected_count"],
        "actual_count": actual,
        "authentic_unittest_result": (
            None if authentic_result is None else {
                key: value for key, value in authentic_result.items()
                if key not in {"nonce", "child_pid", "run_id"}
            }
        ),
        "import_effect_closure": semantic_closure,
        "repository_semantics": semantic_repository,
        "repository_output_count": output_count,
        "changed_repository_paths": list(changed),
        "cleanup_result": "NO_REAL_RESOURCES_CREATED_OR_CLEANED",
        "leak_result": "PROCESS_GROUP_REAPED",
        "result": "PASS",
    }
    deterministic_semantic_root = _deterministic_semantic_root(semantic_material)
    run_material = {
        "gate_id": gate_id, "run_id": run_id, "nonce": nonce,
        "run_root": str(root), "child_pid": completed.child_pid,
        "started_ns": started_ns, "ended_ns": ended_ns,
        "duration_ns": ended_ns - started_ns,
        "stdout_sha256": _sha256_bytes(completed.stdout),
        "stderr_sha256": _sha256_bytes(completed.stderr),
        "gate_evidence_sha256": _read_file_exact(evidence_path, expected_root=root)[1].sha256,
        "raw_artifact_manifest": artifact_manifest,
        "artifact_manifest_sha256": artifact_manifest_hash,
        "repository_before_manifest_sha256": before["manifest_sha256"],
        "repository_after_manifest_sha256": after["manifest_sha256"],
        "process_group": evidence["process_group"],
        "deterministic_semantic_root": deterministic_semantic_root,
    }
    run_attestation_root = _run_attestation_root(run_material)
    attestation_base = {
        "artifact_type": "IU4_I7_FINAL_ROOT_ATTESTATION",
        "schema_version": 3,
        "gate_id": gate_id,
        "gate_evidence_sha256": run_material["gate_evidence_sha256"],
        "artifact_manifest": artifact_manifest,
        "artifact_manifest_sha256": artifact_manifest_hash,
        "return_code": completed.return_code,
        "expected_count": gate["expected_count"],
        "actual_count": actual,
        "repository_output_count": output_count,
        "closure_sha256": _sha256_bytes(_canonical(plan["closure"])),
        "pre_preservation_sha256": before["manifest_sha256"],
        "post_preservation_sha256": after["manifest_sha256"],
        "cleanup_result": "NO_REAL_RESOURCES_CREATED_OR_CLEANED",
        "leak_result": "PROCESS_GROUP_REAPED",
        "deterministic_semantic_material": semantic_material,
        "deterministic_semantic_root": deterministic_semantic_root,
        "run_attestation_material": run_material,
        "run_attestation_root": run_attestation_root,
        "payload_boundary": "CANONICAL_ATTESTATION_BASE_EXCLUDES_ATTESTATION_SHA256_FIELD",
    }
    attestation = {
        **attestation_base,
        "attestation_sha256": _sha256_bytes(_canonical(attestation_base)),
    }
    _write_new(root / "final_attestation.json", _canonical(attestation) + b"\n")
    return {**evidence, "final_attestation": attestation}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--gate", required=True, choices=tuple(PINNED_GATE_AUTHORITY))
    run = sub.add_parser("run")
    run.add_argument("--gate", required=True, choices=("preparation_components", "staged_synthetic_replay"))
    run.add_argument("--run-root", type=Path, required=True)
    contract = sub.add_parser("validate-contract")
    contract.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "plan":
            result = plan_gate(args.gate)
        elif args.command == "run":
            result = run_gate(args.gate, run_root=args.run_root)
        else:
            value = validate_workstation_contract(args.contract)
            result = {"result": "VALID", "run_id": value["run_id"]}
    except Exception as exc:
        print(f"I7_FILE_EXACT_HARNESS: FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DEFAULT_MANIFEST", "DEFAULT_SCHEMA", "FORBIDDEN_PATHS", "I7HarnessError",
    "ImportClosure", "PINNED_MANIFEST_SHA256", "PINNED_SCHEMA_SHA256",
    "ProcessResult", "assert_safe_closure", "compare_repository_manifests",
    "conservative_import_closure", "load_manifest", "plan_gate",
    "repository_state_manifest", "run_gate", "static_test_count",
    "validate_workstation_contract", "_run_process_group",
]
