#!/usr/bin/env python3
"""File-exact E1 TerminalLeaseCapabilityProfileV14 runner.

This module has no repository imports and no default paths.  It is executable
only under a later one-shot mandate with independently accepted E2 and E3
inputs.  Any ambiguity is terminal and same-session retry is forbidden.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
from pathlib import Path
import stat
import subprocess
import sys
import time
from typing import Any, Iterable, Iterator, Mapping, Sequence


CANONICAL_REPOSITORY = "/home/benja/projects/sniper-bot"
CAPABILITY_RUNNER_PATH = "/home/benja/projects/sniper-bot/live_l1/tools/run_terminal_lease_capability_v14.py"
CAPABILITY_MANIFEST_PATH = "/home/benja/projects/sniper-bot/config/pee/IU4_I7_E1_TERMINAL_LEASE_CAPABILITY_MANIFEST_V1.json"
CAPABILITY_ARTIFACT_SCHEMA_PATH = "/home/benja/projects/sniper-bot/config/pee/IU4_I7_E1_TERMINAL_LEASE_CAPABILITY_ARTIFACT_SCHEMA_V1.json"
SPECIFICATION_PATH = "/home/benja/projects/sniper-bot/docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md"
SPECIFICATION_SHA256 = "ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0"
MANIFEST_SHA256 = "2564a05b89b93a4d124bd273388ff3d1dc9587defb095689bbd99c1991d6e2c9"
ARTIFACT_SCHEMA_SHA256 = "e48c3ff0c626d8e9f103b45871148b9bec7b5f1b60313973a98d4103691bacc6"
SCM_MAX_FD = 253
PROTOCOL = "IU4_I7_E1_E3_OBSERVER_PROTOCOL_V1"
GIT_EXECUTABLE = "/usr/bin/git"
GIT_OBJECT_ID_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
AMBIGUOUS_GIT_BINDING_KEYS = frozenset((
    "blob", "blob_sha1", "git_blob_sha1", "commit", "commit_sha",
    "commit_sha1", "git_commit_sha1",
))

SCENARIO_IDS = (
    "CAP_BPF_LSM_SOCKET_GUARD_INTEGRITY_MATRIX", "CAP_BROKER_FAILURE_MATRIX",
    "CAP_CHANNEL_RIGHTS_FREEZE_MATRIX", "CAP_CHILD_STOP_PHASE_MATRIX",
    "CAP_CLOSE_FSM_FAULT_MATRIX", "CAP_CONTROL_WORD_MEMFD_INTEGRITY_MATRIX",
    "CAP_ENVIRONMENT_RESOURCE_ENVELOPE_MATRIX", "CAP_EXTERNAL_ENDPOINT_ACQUISITION_MATRIX",
    "CAP_GUARDIAN_FAILURE_MATRIX", "CAP_LEASE_RENEWAL_LINEARIZATION_MATRIX",
    "CAP_LISTENER_HANDOFF_AUTHORITY_MATRIX", "CAP_LIVENESS_PIPE_IO_DENIAL_MATRIX",
    "CAP_MEMORY_POST_READY_MUTATION_DENIAL_MATRIX", "CAP_NOMINAL_PROFILE_BASELINE",
    "CAP_PIDFD_ESCALATION_MATRIX", "CAP_PLATFORM_EQUIVALENCE_REJECTION_MATRIX",
    "CAP_POST_OPEN_TASK_FD_DENIAL_MATRIX", "CAP_PRIVILEGE_PTRACE_BOUNDARY_MATRIX",
    "CAP_REQUEST_TID_NOTIFICATION_SIGNAL_MATRIX", "CAP_RUNTIME_PHASE_TRANSITION_AUTHORITY_MATRIX",
    "CAP_SHIM_STALL", "CAP_SIGNAL_ENVELOPE_MUTATION_DENIAL_MATRIX",
    "CAP_TERMINAL_GAP_RECOVERY_MATRIX", "CAP_WORKER_REQUEST_AUTHORITY_MATRIX",
)
STARTUP_SCENARIO_IDS = (
    "STARTUP_BROKER_STALL_OR_DEATH", "STARTUP_CHANNEL_RIGHTS_FREEZE_MATRIX",
    "STARTUP_CLOSE_BOUNDARY_FAULT_MATRIX", "STARTUP_GUARDIAN_SIGSTOP",
    "STARTUP_LISTENER_HANDOFF_FAULT_MATRIX", "STARTUP_LIVENESS_PIPE_IO_DENIAL_MATRIX",
    "STARTUP_MEMFD_SEAL_BOOTSTRAP_MATRIX", "STARTUP_NOMINAL_PROFILE_BASELINE",
    "STARTUP_ORDERLY_CLOSE_RENEWAL_RACE", "STARTUP_PHASE_TRANSITION_AUTHORITY_MATRIX",
    "STARTUP_PIDFD_ALL_FAIL_LIVENESS_HUP", "STARTUP_PIDFD_SELF_FAIL_GUARDIAN_SUCCESS",
    "STARTUP_PIDFD_SELF_GUARDIAN_FAIL_BROKER_SUCCESS", "STARTUP_PIDFD_SELF_SUCCESS",
    "STARTUP_POST_READY_TASK_FD_DENIAL_MATRIX", "STARTUP_REQUEST_TID_POST_NOTIFICATION_STOP",
    "STARTUP_RUNTIME_ENDPOINT_ACQUISITION_RACE", "STARTUP_SHIM_STALL",
    "STARTUP_SIGNAL_LISTENER_RECEIVE_FAULT_MATRIX", "STARTUP_TRIP_ALL_PIDFD_FAIL_MAX_CONTENTION",
)
FORBIDDEN_PATHS = (
    "live_l1/tools/validate_terminal_lease_capability.py",
    "tests/live_l1/test_terminal_lease_capability.py",
    "scripts/build_rcc002_spec_bundle.py",
)
TOP_MANIFEST_KEYS = frozenset((
    "artifact_type", "schema_version", "manifest_id", "canonical_repository",
    "specification_path", "specification_sha256", "profile_id", "human_decision_id",
    "ordering", "parameter_variants", "trial_semantics", "startup_relation",
    "scenario_ids", "startup_scenario_ids", "scenarios", "startup_scenarios",
    "common_profile", "artifact_contract", "forbidden_paths", "ownership",
    "execution_boundary",
))
CAPABILITY_RECORD_KEYS = frozenset((
    "scenario_id", "specification_anchor", "dimensions", "variant_order",
    "trials_per_bound_variant", "trial_offset_rule", "required_observations",
    "pass_predicate",
))
STARTUP_RECORD_KEYS = frozenset((
    "scenario_id", "specification_anchor", "dimensions", "variant_order",
    "probes_per_bound_variant", "phase_offset_rule", "required_observations",
    "pass_predicate",
))
CONTRACT_KEYS = frozenset((
    "artifact_type", "schema_version", "schema_id", "run_id", "canonical_repository",
    "host", "guest", "privileges", "capability", "observer", "cleanup",
    "file_inputs", "stop_conditions",
))
REQUEST_KEYS = frozenset((
    "protocol", "run_id", "kind", "scenario_id", "variant_id",
    "dimension_bindings", "record_index", "offset_us", "required_observations",
    "pass_predicate", "profile_fingerprint", "platform_fingerprint",
))
RESPONSE_KEYS = frozenset((
    "protocol", "run_id", "kind", "scenario_id", "variant_id", "record",
    "observer_attestation", "cleanup_attestation", "raw_entries",
))
OBSERVER_ATTESTATION_KEYS = frozenset((
    "observer_id", "observer_sha256", "independent_process",
    "independent_owner", "complete_kernel_timestamps", "snapshot_root",
))
CLEANUP_ATTESTATION_KEYS = frozenset((
    "run_owned_only", "zero_residue", "preexisting_bytes_identical",
    "preexisting_metadata_identical", "same_session_retry_count",
    "cleanup_root",
))
RAW_ENTRY_KEYS = frozenset((
    "logical_path", "sha256", "size", "mode", "uid", "gid",
))
OUTCOME_VECTOR_KEYS = frozenset((
    "syscall", "cas", "signal", "queue", "references", "phase", "open",
    "residue",
))
KERNEL_TIMESTAMP_KEYS = frozenset((
    'clock', 'injection_ns', 'kernel_accept_ns', 'trip_cas_ns',
    'fatal_action_ns', 'terminal_ns',
))
KERNEL_TIMESTAMP_VALUE_KEYS = (
    'injection_ns', 'kernel_accept_ns', 'trip_cas_ns', 'fatal_action_ns',
    'terminal_ns',
)
KERNEL_SIGNAL_GENERATION_BUDGET_NS = 25_000_000
BROKER_TRIP_CAS_MAX_NS = 5_000_000
GUARDIAN_TRIP_DISPATCH_MAX_NS = 5_000_000
FAILSTOP_MAX_NS = 100_000_000
E2_DECISION_KEYS = frozenset((
    "artifact_type", "schema_version", "decision_id", "acceptance_task_id",
    "reviewer_owner_id", "status", "scope", "accepted_host",
    "accepted_guest", "accepted_privileges", "subject_fingerprint",
    "organizational_separation", "authority_grants",
))
E3_DECISION_KEYS = frozenset((
    "artifact_type", "schema_version", "decision_id", "acceptance_task_id",
    "reviewer_owner_id", "collector_author_id", "collector_evidence_owner_id",
    "status", "scope", "observer_runner_sha256",
    "observer_snapshot_schema_sha256", "protocol",
    "organizational_separation", "authority_grants",
))
E2_SEPARATION_KEYS = frozenset((
    "from_e1_authoring", "from_e1_correction", "from_e1_evidence",
    "from_e1_acceptance",
))
E3_SEPARATION_KEYS = frozenset((
    "collector_author_from_evidence_owner",
    "collector_author_from_acceptance_owner",
    "collector_evidence_owner_from_acceptance_owner",
    "not_reused_as_e1_or_e2",
))
DECISION_AUTHORITY_KEYS = frozenset((
    "test", "evidence", "e1_acceptance", "execution", "live", "exchange",
))
EXECUTION_MANDATE_KEYS = frozenset((
    "artifact_type", "schema_version", "mandate_id", "issuance_task_id",
    "issuer_owner_id", "mandate_path", "status", "scope", "one_shot",
    "same_session_retry",
    "valid_from_unix_ns", "expires_at_unix_ns", "run_id", "command_argv",
    "run_root", "identities", "prerequisite_decisions", "host", "guest",
    "privileges", "timeouts", "stop_conditions", "cleanup",
    "authority_grants",
))
EXECUTION_IDENTITY_KEYS = frozenset((
    "canonical_repository", "contract_path", "contract_schema_id",
    "capability_runner_path", "capability_runner_sha256",
    "specification_path", "specification_sha256", "manifest_path",
    "manifest_sha256", "artifact_schema_path", "artifact_schema_sha256",
))
EXECUTION_DECISION_KEYS = frozenset((
    "e2_path", "e2_sha256", "e2_decision_id", "e3_path", "e3_sha256",
    "e3_decision_id",
))
EXECUTION_AUTHORITY_KEYS = frozenset((
    "test", "evidence", "e1_acceptance", "execution", "live", "exchange",
    "staging", "commit", "push",
))
EXECUTION_TIMEOUT_KEYS = frozenset(("per_scenario_timeout_seconds",))
HOST_COORDINATE_KEYS = frozenset((
    "host_id", "human_authority_id", "disposable_host", "kernel_release",
    "kernel_build_id", "architecture", "boot_id",
    "clock_boottime_resolution_ns", "active_lsm", "bpffs_mount",
    "cgroup_v2_mount", "pid_namespace", "mount_namespace",
    "user_namespace", "network_namespace", "yama_initial_scope",
))
GUEST_COORDINATE_KEYS = frozenset((
    "vm_id", "human_authority_id", "qemu_version", "qmp_socket",
    "guest_repo_readonly_path", "ssh_host", "ssh_port", "ssh_user",
    "restore_authority_id", "discard_authority_id", "reboot_authority_id",
    "suspend_authority_id",
))
PRIVILEGE_COORDINATE_KEYS = frozenset((
    "human_authority_id", "expected_uid", "expected_gid", "allowed_commands",
    "yama_restore_command", "bpf_authority_id", "lsm_authority_id",
    "cgroup_authority_id", "namespace_authority_id",
))
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_execution_mandate_consumed = False


class E1Error(RuntimeError):
    pass


def _reject_duplicates(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise E1Error(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(token: str) -> Any:
    raise E1Error(f"non-standard JSON numeric constant forbidden: {token}")


def _strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    _regular_file(path)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or not raw.endswith(b"\n"):
        raise E1Error(f"noncanonical UTF-8/LF input: {path}")
    try:
        value = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise E1Error(f"invalid strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise E1Error(f"root is not an object: {path}")
    return value, raw


def _canonical(value: Any) -> bytes:
    try:
        rendered = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise E1Error("value is not canonical JSON") from exc
    return (rendered + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob_id(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def _git_read_only(arguments: Sequence[str]) -> bytes:
    environment = {
        "PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_NO_LAZY_FETCH": "1", "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        completed = subprocess.run(
            [GIT_EXECUTABLE, "--no-optional-locks", "-C", CANONICAL_REPOSITORY,
             *arguments],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False, timeout=10,
            cwd=CANONICAL_REPOSITORY, env=environment,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise E1Error("local Git identity lookup failed") from exc
    if completed.returncode != 0:
        raise E1Error("local Git identity lookup rejected the bound object")
    return completed.stdout


def _verify_git_binding(item: Mapping[str, Any], path: Path, raw: bytes,
                        info: os.stat_result) -> None:
    ambiguous = AMBIGUOUS_GIT_BINDING_KEYS.intersection(item)
    if ambiguous:
        raise E1Error(f"ambiguous Git binding fields: {sorted(ambiguous)}")
    git_blob = item.get("git_blob")
    git_commit = item.get("git_commit")
    if (not isinstance(git_blob, str)
            or GIT_OBJECT_ID_PATTERN.fullmatch(git_blob) is None):
        raise E1Error(f"file input {item.get('input_id')} git_blob binding invalid")
    if (not isinstance(git_commit, str)
            or GIT_OBJECT_ID_PATTERN.fullmatch(git_commit) is None):
        raise E1Error(f"file input {item.get('input_id')} git_commit binding invalid")
    actual_blob = _git_blob_id(raw)
    if git_blob != actual_blob:
        raise E1Error(f"file input {item.get('input_id')} Git blob mismatch")
    repository = Path(CANONICAL_REPOSITORY)
    try:
        relative_path = path.relative_to(repository)
    except ValueError as exc:
        raise E1Error(f"Git-bound file is outside canonical repository: {path}") from exc
    if not relative_path.parts or any(part in ("", ".", "..") for part in relative_path.parts):
        raise E1Error(f"noncanonical Git-bound repository path: {path}")
    object_type = _git_read_only(["cat-file", "-t", git_commit])
    if object_type != b"commit\n":
        raise E1Error(f"file input {item.get('input_id')} Git commit binding is not a commit")
    relative_text = relative_path.as_posix()
    tree_entry = _git_read_only([
        "ls-tree", "-z", "--full-tree", git_commit, "--", relative_text,
    ])
    if not tree_entry.endswith(b"\0") or tree_entry.count(b"\0") != 1:
        raise E1Error(f"file input {item.get('input_id')} Git path is absent or ambiguous")
    try:
        metadata, bound_path = tree_entry[:-1].split(b"\t", 1)
        git_mode, object_kind, tree_blob = metadata.decode("ascii").split(" ")
        decoded_path = bound_path.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise E1Error(f"file input {item.get('input_id')} Git tree entry invalid") from exc
    expected_mode = "100755" if stat.S_IMODE(info.st_mode) & 0o111 else "100644"
    if (git_mode != expected_mode or object_kind != "blob"
            or tree_blob != git_blob or decoded_path != relative_text):
        raise E1Error(f"file input {item.get('input_id')} Git commit/path/blob mismatch")


def _regular_file(path: Path) -> os.stat_result:
    if not path.is_absolute():
        raise E1Error(f"relative path forbidden: {path}")
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current = current / component
        info = os.lstat(current)
        if stat.S_ISLNK(info.st_mode):
            raise E1Error(f"symlink forbidden: {current}")
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise E1Error(f"regular single-link file required: {path}")
    return info


def _verify_new_run_root(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute() or path.anchor != "/":
        raise E1Error(f"relative run root forbidden: {raw_path}")
    if raw_path != str(path) or any(
            component in ("", ".", "..") for component in path.parts[1:]):
        raise E1Error(f"noncanonical run root forbidden: {raw_path}")
    try:
        if os.path.lexists(raw_path):
            raise E1Error("run root must be new and absent")
        current = Path(path.anchor)
        info = os.lstat(current)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise E1Error("run-root filesystem root is not a real directory")
        for component in path.parent.parts[1:]:
            current = current / component
            info = os.lstat(current)
            if stat.S_ISLNK(info.st_mode):
                raise E1Error(f"run-root parent symlink forbidden: {current}")
            if not stat.S_ISDIR(info.st_mode):
                raise E1Error(f"run-root parent is not a directory: {current}")
    except OSError as exc:
        raise E1Error("run-root parent-chain verification failed") from exc
    return path


def _exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    actual = frozenset(value)
    if actual != expected:
        raise E1Error(f"{label} keys mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}")


def _required_identity(value: Mapping[str, Any], key: str, label: str) -> str:
    identity = value.get(key)
    if not isinstance(identity, str) or not identity:
        raise E1Error(f"{label} {key} is not a bound nonempty identity")
    return identity


def _require_closed_flags(value: Any, keys: frozenset[str], expected: bool,
                          label: str) -> None:
    if not isinstance(value, dict):
        raise E1Error(f"{label} is not an object")
    _exact_keys(value, keys, label)
    if any(value[key] is not expected for key in keys):
        raise E1Error(f"{label} does not match its fail-closed values")


def _contains_forbidden_path(value: Any) -> bool:
    forbidden = set(FORBIDDEN_PATHS)
    forbidden.update(str(Path(CANONICAL_REPOSITORY) / path)
                     for path in FORBIDDEN_PATHS)
    if isinstance(value, str):
        return value in forbidden
    if isinstance(value, list):
        return any(_contains_forbidden_path(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_forbidden_path(key)
                   or _contains_forbidden_path(item)
                   for key, item in value.items())
    return False


def _validate_e2_coordinates(contract: Mapping[str, Any]) -> None:
    host = contract.get("host")
    guest = contract.get("guest")
    privileges = contract.get("privileges")
    if not isinstance(host, dict) or not isinstance(guest, dict) or not isinstance(privileges, dict):
        raise E1Error("E2 host/guest/privileges coordinates are not objects")
    _exact_keys(host, HOST_COORDINATE_KEYS, "E2 host coordinates")
    _exact_keys(guest, GUEST_COORDINATE_KEYS, "E2 guest coordinates")
    _exact_keys(privileges, PRIVILEGE_COORDINATE_KEYS, "E2 privilege coordinates")
    for key in HOST_COORDINATE_KEYS - {
        "disposable_host", "clock_boottime_resolution_ns", "active_lsm",
        "yama_initial_scope",
    }:
        _required_identity(host, key, "E2 host coordinates")
    if host["disposable_host"] is not True:
        raise E1Error("E2 host is not explicitly disposable")
    if (not isinstance(host["clock_boottime_resolution_ns"], int)
            or isinstance(host["clock_boottime_resolution_ns"], bool)
            or host["clock_boottime_resolution_ns"] < 1):
        raise E1Error("E2 host clock resolution is invalid")
    if (not isinstance(host["yama_initial_scope"], int)
            or isinstance(host["yama_initial_scope"], bool)
            or host["yama_initial_scope"] < 0):
        raise E1Error("E2 host Yama scope is invalid")
    active_lsm = host["active_lsm"]
    if (not isinstance(active_lsm, list) or not active_lsm
            or any(not isinstance(item, str) or not item for item in active_lsm)
            or len(active_lsm) != len(set(active_lsm))):
        raise E1Error("E2 host active-LSM coordinates are invalid")
    for key in GUEST_COORDINATE_KEYS - {"ssh_port"}:
        _required_identity(guest, key, "E2 guest coordinates")
    if guest["ssh_host"] not in {"127.0.0.1", "::1"}:
        raise E1Error("E2 guest SSH host is not loopback-bound")
    if (not isinstance(guest["ssh_port"], int)
            or isinstance(guest["ssh_port"], bool) or guest["ssh_port"] < 1):
        raise E1Error("E2 guest SSH port is invalid")
    for key in PRIVILEGE_COORDINATE_KEYS - {
        "expected_uid", "expected_gid", "allowed_commands",
    }:
        _required_identity(privileges, key, "E2 privilege coordinates")
    for key in ("expected_uid", "expected_gid"):
        if (not isinstance(privileges[key], int)
                or isinstance(privileges[key], bool) or privileges[key] < 0):
            raise E1Error(f"E2 privilege {key} is invalid")
    commands = privileges["allowed_commands"]
    if (not isinstance(commands, list) or not commands
            or any(not isinstance(item, str) or not item for item in commands)
            or len(commands) != len(set(commands))):
        raise E1Error("E2 allowed-command authority is invalid")


def _validate_prerequisite_decisions(
    contract: Mapping[str, Any], e2: Mapping[str, Any],
    e3: Mapping[str, Any], observer_runner_sha256: str,
    observer_snapshot_schema_sha256: str,
) -> None:
    _exact_keys(e2, E2_DECISION_KEYS, "E2 acceptance decision")
    _exact_keys(e3, E3_DECISION_KEYS, "E3 acceptance decision")
    e2_schema_version = e2.get("schema_version")
    e3_schema_version = e3.get("schema_version")
    if type(e2_schema_version) is not int or e2_schema_version != 1:
        raise E1Error("E2 acceptance schema version mismatch")
    if type(e3_schema_version) is not int or e3_schema_version != 1:
        raise E1Error("E3 acceptance schema version mismatch")
    _validate_e2_coordinates(contract)
    e2_fixed = {
        "artifact_type": "IU4_I7_E2_DISPOSABLE_WORKSTATION_ACCEPTANCE_DECISION",
        "schema_version": 1,
        "status": "ACCEPTED",
        "scope": "E2_REAL_DISPOSABLE_WORKSTATION_VM_SSH_PRIVILEGE_COORDINATES_AND_HUMAN_AUTHORITY",
    }
    e3_fixed = {
        "artifact_type": "IU4_I7_E3_INDEPENDENT_COLLECTOR_ACCEPTANCE_DECISION",
        "schema_version": 1,
        "status": "ACCEPTED",
        "scope": "E3_INDEPENDENT_PROCESS_KERNEL_BPF_VM_COLLECTOR",
        "protocol": PROTOCOL,
    }
    if any(e2.get(key) != expected for key, expected in e2_fixed.items()):
        raise E1Error("E2 acceptance identity, scope or status mismatch")
    if any(e3.get(key) != expected for key, expected in e3_fixed.items()):
        raise E1Error("E3 acceptance identity, scope, protocol or status mismatch")
    e2_decision_id = _required_identity(e2, "decision_id", "E2 acceptance")
    e2_task_id = _required_identity(e2, "acceptance_task_id", "E2 acceptance")
    e2_owner_id = _required_identity(e2, "reviewer_owner_id", "E2 acceptance")
    e3_decision_id = _required_identity(e3, "decision_id", "E3 acceptance")
    e3_task_id = _required_identity(e3, "acceptance_task_id", "E3 acceptance")
    e3_owner_id = _required_identity(e3, "reviewer_owner_id", "E3 acceptance")
    e3_author_id = _required_identity(e3, "collector_author_id", "E3 acceptance")
    e3_evidence_id = _required_identity(
        e3, "collector_evidence_owner_id", "E3 acceptance",
    )
    if e2_decision_id == e3_decision_id:
        raise E1Error("E2/E3 decision identities are not separate")
    if e2_task_id == e3_task_id:
        raise E1Error("E2/E3 acceptance task identities are not separate")
    if e2_owner_id == e3_owner_id:
        raise E1Error("E2/E3 acceptance owner identities are not separate")
    if e2_owner_id in {e3_author_id, e3_evidence_id}:
        raise E1Error("E2 acceptance owner is reused by E3 author or evidence")
    if len({e3_owner_id, e3_author_id, e3_evidence_id}) != 3:
        raise E1Error("E3 author, evidence and acceptance identities are not separate")
    _require_closed_flags(
        e2.get("organizational_separation"), E2_SEPARATION_KEYS, True,
        "E2 organizational separation",
    )
    _require_closed_flags(
        e3.get("organizational_separation"), E3_SEPARATION_KEYS, True,
        "E3 organizational separation",
    )
    _require_closed_flags(
        e2.get("authority_grants"), DECISION_AUTHORITY_KEYS, False,
        "E2 forbidden authority grants",
    )
    _require_closed_flags(
        e3.get("authority_grants"), DECISION_AUTHORITY_KEYS, False,
        "E3 forbidden authority grants",
    )
    subject: dict[str, Any] = {}
    for contract_key, decision_key in (
        ("host", "accepted_host"), ("guest", "accepted_guest"),
        ("privileges", "accepted_privileges"),
    ):
        contract_value = contract.get(contract_key)
        accepted_value = e2.get(decision_key)
        if (not isinstance(contract_value, dict) or not contract_value
                or not isinstance(accepted_value, dict) or not accepted_value):
            raise E1Error(f"E2 accepted {contract_key} coordinates are missing")
        if _canonical(contract_value) != _canonical(accepted_value):
            raise E1Error(f"E2 accepted {contract_key} coordinates mismatch")
        subject[contract_key] = contract_value
    subject_fingerprint = e2.get("subject_fingerprint")
    if (not isinstance(subject_fingerprint, str)
            or SHA256_PATTERN.fullmatch(subject_fingerprint) is None
            or subject_fingerprint != _sha256(_canonical(subject))):
        raise E1Error("E2 host/guest/privileges fingerprint mismatch")
    for field, actual in (
        ("observer_runner_sha256", observer_runner_sha256),
        ("observer_snapshot_schema_sha256", observer_snapshot_schema_sha256),
    ):
        bound = e3.get(field)
        if (not isinstance(bound, str)
                or SHA256_PATTERN.fullmatch(bound) is None or bound != actual):
            raise E1Error(f"E3 {field} binding mismatch")
    if _contains_forbidden_path(e2) or _contains_forbidden_path(e3):
        raise E1Error("E2/E3 acceptance decision reuses a forbidden path")


def _consume_execution_mandate(
    mandate: Mapping[str, Any], mandate_path_value: str,
    contract: Mapping[str, Any],
    contract_path: Path, run_root: Path, raw_argv: Sequence[str],
    runner_sha256: str, file_inputs: Mapping[str, Mapping[str, Any]],
    e2_path: Path, e2: Mapping[str, Any], e3_path: Path,
    e3: Mapping[str, Any],
) -> None:
    global _execution_mandate_consumed
    if _execution_mandate_consumed:
        raise E1Error("E1 execution mandate already consumed in this session")
    _exact_keys(mandate, EXECUTION_MANDATE_KEYS, "E1 execution mandate")
    mandate_schema_version = mandate.get("schema_version")
    if type(mandate_schema_version) is not int or mandate_schema_version != 1:
        raise E1Error("E1 execution mandate schema version mismatch")
    one_shot = mandate.get("one_shot")
    if type(one_shot) is not bool or one_shot is not True:
        raise E1Error("E1 execution mandate one-shot binding mismatch")
    same_session_retry = mandate.get("same_session_retry")
    if type(same_session_retry) is not bool or same_session_retry is not False:
        raise E1Error("E1 execution mandate same-session retry binding mismatch")
    mandate_path = mandate.get("mandate_path")
    if (not isinstance(mandate_path, str) or not mandate_path
            or mandate_path != mandate_path_value):
        raise E1Error("E1 execution mandate raw self-path binding mismatch")
    fixed = {
        "artifact_type": "IU4_I7_E1_ONE_SHOT_EXECUTION_MANDATE",
        "schema_version": 1,
        "status": "AUTHORIZED",
        "scope": "E1_SINGLE_LOCAL_CAPABILITY_RUN",
        "one_shot": True,
        "same_session_retry": False,
    }
    if any(mandate.get(key) != expected for key, expected in fixed.items()):
        raise E1Error("E1 execution mandate identity, status or one-shot scope mismatch")
    mandate_id = _required_identity(mandate, "mandate_id", "E1 execution mandate")
    issuance_task_id = _required_identity(
        mandate, "issuance_task_id", "E1 execution mandate",
    )
    issuer_owner_id = _required_identity(
        mandate, "issuer_owner_id", "E1 execution mandate",
    )
    if len({mandate_id, issuance_task_id, issuer_owner_id}) != 3:
        raise E1Error("E1 execution mandate identities are not unique")
    e2_owner_id = _required_identity(e2, "reviewer_owner_id", "E2 acceptance")
    e3_owner_id = _required_identity(e3, "reviewer_owner_id", "E3 acceptance")
    e3_author_id = _required_identity(e3, "collector_author_id", "E3 acceptance")
    e3_evidence_id = _required_identity(
        e3, "collector_evidence_owner_id", "E3 acceptance",
    )
    if issuer_owner_id in {
        e2_owner_id, e3_owner_id, e3_author_id, e3_evidence_id,
    }:
        raise E1Error("E1 mandate issuer reuses an E2/E3 owner identity")
    valid_from = mandate.get("valid_from_unix_ns")
    expires_at = mandate.get("expires_at_unix_ns")
    if (not isinstance(valid_from, int) or isinstance(valid_from, bool)
            or not isinstance(expires_at, int) or isinstance(expires_at, bool)
            or valid_from < 0 or expires_at <= valid_from):
        raise E1Error("E1 execution mandate validity interval is invalid")
    now = time.time_ns()
    if now < valid_from or now > expires_at:
        raise E1Error("E1 execution mandate is not currently valid")
    run_id = contract.get("run_id")
    if not isinstance(run_id, str) or not run_id or mandate.get("run_id") != run_id:
        raise E1Error("E1 execution mandate run identity mismatch")
    if mandate.get("run_root") != str(run_root):
        raise E1Error("E1 execution mandate raw run-root binding mismatch")
    expected_arguments = [
        "--contract", str(contract_path),
        "--manifest", CAPABILITY_MANIFEST_PATH,
        "--artifact-schema", CAPABILITY_ARTIFACT_SCHEMA_PATH,
        "--run-root", str(run_root),
    ]
    expected_command = ["/usr/bin/python3", "-I", CAPABILITY_RUNNER_PATH,
                        *expected_arguments]
    try:
        process_command_raw = Path("/proc/self/cmdline").read_bytes()
        if (not process_command_raw.endswith(b"\0")
                or process_command_raw.count(b"\0") != len(expected_command)):
            raise E1Error("actual process command framing mismatch")
        process_command = [
            field.decode("utf-8")
            for field in process_command_raw[:-1].split(b"\0")
        ]
    except (OSError, UnicodeDecodeError) as exc:
        raise E1Error("actual process command identity unavailable") from exc
    if (list(raw_argv) != expected_arguments
            or process_command != expected_command
            or mandate.get("command_argv") != expected_command):
        raise E1Error("E1 execution mandate command binding mismatch")
    identities = mandate.get("identities")
    if not isinstance(identities, dict):
        raise E1Error("E1 execution mandate identities are not an object")
    _exact_keys(identities, EXECUTION_IDENTITY_KEYS,
                "E1 execution mandate identities")
    expected_identities = {
        "canonical_repository": CANONICAL_REPOSITORY,
        "contract_path": str(contract_path),
        "contract_schema_id": contract.get("schema_id"),
        "capability_runner_path": CAPABILITY_RUNNER_PATH,
        "capability_runner_sha256": runner_sha256,
        "specification_path": SPECIFICATION_PATH,
        "specification_sha256": SPECIFICATION_SHA256,
        "manifest_path": CAPABILITY_MANIFEST_PATH,
        "manifest_sha256": MANIFEST_SHA256,
        "artifact_schema_path": CAPABILITY_ARTIFACT_SCHEMA_PATH,
        "artifact_schema_sha256": ARTIFACT_SCHEMA_SHA256,
    }
    if _canonical(identities) != _canonical(expected_identities):
        raise E1Error("E1 execution mandate artifact identities mismatch")
    decisions = mandate.get("prerequisite_decisions")
    if not isinstance(decisions, dict):
        raise E1Error("E1 execution mandate prerequisite decisions are not an object")
    _exact_keys(decisions, EXECUTION_DECISION_KEYS,
                "E1 execution mandate prerequisite decisions")
    expected_decisions = {
        "e2_path": str(e2_path),
        "e2_sha256": file_inputs["E2_ACCEPTANCE_DECISION"].get("sha256"),
        "e2_decision_id": e2.get("decision_id"),
        "e3_path": str(e3_path),
        "e3_sha256": file_inputs["E3_ACCEPTANCE_DECISION"].get("sha256"),
        "e3_decision_id": e3.get("decision_id"),
    }
    if _canonical(decisions) != _canonical(expected_decisions):
        raise E1Error("E1 execution mandate prerequisite decision binding mismatch")
    for key in ("host", "guest", "privileges", "stop_conditions", "cleanup"):
        value = mandate.get(key)
        contract_value = contract.get(key)
        if (not isinstance(value, dict) or not isinstance(contract_value, dict)
                or _canonical(value) != _canonical(contract_value)):
            raise E1Error(f"E1 execution mandate {key} binding mismatch")
    capability = contract.get("capability")
    timeout = (capability.get("per_scenario_timeout_seconds")
               if isinstance(capability, dict) else None)
    if (not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1):
        raise E1Error("effective per-scenario timeout is invalid")
    timeouts = mandate.get("timeouts")
    if not isinstance(timeouts, dict):
        raise E1Error("E1 execution mandate timeouts are not an object")
    _exact_keys(timeouts, EXECUTION_TIMEOUT_KEYS,
                "E1 execution mandate timeouts")
    mandate_timeout = timeouts["per_scenario_timeout_seconds"]
    if type(mandate_timeout) is not int or mandate_timeout < 1:
        raise E1Error("E1 execution mandate timeout value is invalid")
    if mandate_timeout != timeout:
        raise E1Error("E1 execution mandate timeout binding mismatch")
    authorities = mandate.get("authority_grants")
    if not isinstance(authorities, dict):
        raise E1Error("E1 execution mandate authority grants are not an object")
    _exact_keys(authorities, EXECUTION_AUTHORITY_KEYS,
                "E1 execution mandate authority grants")
    if authorities["execution"] is not True or any(
        authorities[key] is not False
        for key in EXECUTION_AUTHORITY_KEYS - {"execution"}
    ):
        raise E1Error("E1 execution mandate authority boundary mismatch")
    if _contains_forbidden_path(mandate):
        raise E1Error("E1 execution mandate reuses a forbidden path")
    _execution_mandate_consumed = True


SCHEMA_KEYWORDS = frozenset((
    "$schema", "$id", "$ref", "$defs", "title", "type", "const", "enum",
    "pattern", "minimum", "maximum", "minLength", "minProperties", "minItems", "maxItems",
    "items", "properties", "required", "additionalProperties",
))
SCHEMA_TYPES = frozenset(("object", "array", "string", "integer", "number",
                          "boolean", "null"))


def _check_schema_node(node: Any, location: str = "$") -> None:
    if not isinstance(node, dict):
        raise E1Error(f"artifact schema node is not an object: {location}")
    unknown = frozenset(node) - SCHEMA_KEYWORDS
    if unknown:
        raise E1Error(f"unsupported artifact schema keywords at {location}: {sorted(unknown)}")
    if "$ref" in node:
        if frozenset(node) != frozenset(("$ref",)):
            raise E1Error(f"ambiguous artifact schema $ref siblings at {location}")
        reference = node["$ref"]
        prefix = "#/$defs/"
        if (not isinstance(reference, str) or not reference.startswith(prefix)
                or not reference[len(prefix):] or "/" in reference[len(prefix):]):
            raise E1Error(f"external or unsupported artifact schema reference at {location}")
        return
    for annotation in ("$schema", "$id", "title"):
        if annotation in node and not isinstance(node[annotation], str):
            raise E1Error(f"artifact schema {annotation} is not a string at {location}")
    type_value = node.get("type")
    if type_value is not None:
        type_names = [type_value] if isinstance(type_value, str) else type_value
        if (not isinstance(type_names, list) or not type_names
                or any(not isinstance(name, str) or name not in SCHEMA_TYPES
                       for name in type_names)
                or len(type_names) != len(set(type_names))):
            raise E1Error(f"unsupported or ambiguous artifact schema type at {location}")
    enum_value = node.get("enum")
    if enum_value is not None and (not isinstance(enum_value, list) or not enum_value):
        raise E1Error(f"artifact schema enum is invalid at {location}")
    pattern = node.get("pattern")
    if pattern is not None:
        if not isinstance(pattern, str):
            raise E1Error(f"artifact schema pattern is not a string at {location}")
        try:
            re.compile(pattern)
        except re.error as exc:
            raise E1Error(f"artifact schema pattern is invalid at {location}: {exc}") from exc
    for keyword in ("minimum", "maximum"):
        value = node.get(keyword)
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)):
            raise E1Error(f"artifact schema {keyword} is not numeric at {location}")
    for keyword in ("minLength", "minProperties", "minItems", "maxItems"):
        value = node.get(keyword)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            raise E1Error(f"artifact schema {keyword} is invalid at {location}")
    if ("minimum" in node and "maximum" in node
            and node["minimum"] > node["maximum"]):
        raise E1Error(f"artifact schema numeric bounds are inverted at {location}")
    if ("minItems" in node and "maxItems" in node
            and node["minItems"] > node["maxItems"]):
        raise E1Error(f"artifact schema array bounds are inverted at {location}")
    properties = node.get("properties")
    if properties is not None:
        if not isinstance(properties, dict):
            raise E1Error(f"artifact schema properties is not an object at {location}")
        for name, child in properties.items():
            _check_schema_node(child, f"{location}.properties.{name}")
    required = node.get("required")
    if required is not None:
        if (not isinstance(required, list)
                or any(not isinstance(name, str) for name in required)
                or len(required) != len(set(required))):
            raise E1Error(f"artifact schema required is invalid at {location}")
    additional = node.get("additionalProperties")
    if additional is not None and not isinstance(additional, bool):
        _check_schema_node(additional, f"{location}.additionalProperties")
    items = node.get("items")
    if items is not None:
        _check_schema_node(items, f"{location}.items")
    definitions = node.get("$defs")
    if definitions is not None:
        if not isinstance(definitions, dict) or not definitions:
            raise E1Error(f"artifact schema $defs is invalid at {location}")
        for name, child in definitions.items():
            _check_schema_node(child, f"{location}.$defs.{name}")


def _schema_type_matches(value: Any, type_name: str) -> bool:
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "null":
        return value is None
    raise E1Error(f"unsupported artifact schema type: {type_name}")


def _resolve_schema_reference(root_schema: Mapping[str, Any], reference: str) -> Mapping[str, Any]:
    name = reference[len("#/$defs/"):]
    definitions = root_schema.get("$defs")
    if not isinstance(definitions, dict) or name not in definitions:
        raise E1Error(f"unresolved artifact schema reference: {reference}")
    target = definitions[name]
    if not isinstance(target, dict):
        raise E1Error(f"artifact schema reference is not an object: {reference}")
    return target


def _validate_schema_instance(
    value: Any, node: Mapping[str, Any], root_schema: Mapping[str, Any],
    location: str = "$", reference_stack: tuple[str, ...] = (),
) -> None:
    if "$ref" in node:
        reference = str(node["$ref"])
        if reference in reference_stack:
            raise E1Error(f"cyclic artifact schema reference: {reference}")
        _validate_schema_instance(
            value, _resolve_schema_reference(root_schema, reference), root_schema,
            location, reference_stack + (reference,),
        )
        return
    type_value = node.get("type")
    if type_value is not None:
        type_names = [type_value] if isinstance(type_value, str) else type_value
        if not any(_schema_type_matches(value, name) for name in type_names):
            raise E1Error(f"artifact result type mismatch at {location}")
    if "const" in node and value != node["const"]:
        raise E1Error(f"artifact result const mismatch at {location}")
    if "enum" in node and value not in node["enum"]:
        raise E1Error(f"artifact result enum mismatch at {location}")
    if isinstance(value, str):
        if "pattern" in node and re.search(node["pattern"], value) is None:
            raise E1Error(f"artifact result pattern mismatch at {location}")
        if "minLength" in node and len(value) < node["minLength"]:
            raise E1Error(f"artifact result string is too short at {location}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in node and value < node["minimum"]:
            raise E1Error(f"artifact result is below minimum at {location}")
        if "maximum" in node and value > node["maximum"]:
            raise E1Error(f"artifact result is above maximum at {location}")
    if isinstance(value, list):
        if "minItems" in node and len(value) < node["minItems"]:
            raise E1Error(f"artifact result array is too short at {location}")
        if "maxItems" in node and len(value) > node["maxItems"]:
            raise E1Error(f"artifact result array is too long at {location}")
        if "items" in node:
            for index, item in enumerate(value):
                _validate_schema_instance(
                    item, node["items"], root_schema, f"{location}[{index}]",
                    reference_stack,
                )
    if isinstance(value, dict):
        if "minProperties" in node and len(value) < node["minProperties"]:
            raise E1Error(f"artifact result object has too few properties at {location}")
        properties = node.get("properties", {})
        required = node.get("required", [])
        missing = [name for name in required if name not in value]
        if missing:
            raise E1Error(f"artifact result required fields missing at {location}: {missing}")
        additional = node.get("additionalProperties", True)
        for name, item in value.items():
            if name in properties:
                child = properties[name]
            elif additional is False:
                raise E1Error(f"artifact result additional field at {location}: {name}")
            elif additional is True:
                continue
            else:
                child = additional
            _validate_schema_instance(
                item, child, root_schema, f"{location}.{name}", reference_stack,
            )


def _validate_result_schema(result: Mapping[str, Any],
                            schema: Mapping[str, Any]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise E1Error("artifact schema draft identity mismatch")
    _check_schema_node(schema)
    _validate_schema_instance(result, schema, schema)


def _input_map(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    values = contract.get("file_inputs")
    if not isinstance(values, list):
        raise E1Error("contract file_inputs must be an array")
    result: dict[str, Mapping[str, Any]] = {}
    for item in values:
        if not isinstance(item, dict) or not isinstance(item.get("input_id"), str):
            raise E1Error("invalid file input")
        key = item["input_id"]
        if key in result:
            raise E1Error(f"duplicate file input: {key}")
        result[key] = item
    return result


def _verify_file_input(item: Mapping[str, Any], expected_path: Path | None = None,
                       expected_sha: str | None = None,
                       require_git_binding: bool = False,
                       require_canonical_raw_path: bool = False) -> Path:
    path_value = item.get("path")
    if not isinstance(path_value, str):
        raise E1Error("file input path missing")
    if require_canonical_raw_path:
        components = path_value.split("/")
        if (not path_value or "\0" in path_value or len(components) < 2
                or components[0] != ""
                or any(component in ("", ".", "..")
                       for component in components[1:])):
            raise E1Error(f"file input raw path is not canonical: {path_value}")
    if expected_path is not None and path_value != str(expected_path):
        raise E1Error(f"file input raw path mismatch: {path_value}")
    path = Path(path_value)
    info = _regular_file(path)
    if expected_path is not None and path != expected_path:
        raise E1Error(f"file input path mismatch: {path}")
    raw = path.read_bytes()
    actual_sha = _sha256(raw)
    if item.get("sha256") != actual_sha:
        raise E1Error(f"file input {item.get('input_id')} sha256 mismatch")
    for field, actual in (("size", len(raw)),
                          ("mode", stat.S_IMODE(info.st_mode)), ("uid", info.st_uid),
                          ("gid", info.st_gid), ("device", info.st_dev),
                          ("inode", info.st_ino)):
        claimed_value = item.get(field)
        if type(claimed_value) is not int:
            raise E1Error(f"file input {item.get('input_id')} {field} must be an integer")
        if claimed_value != actual:
            raise E1Error(f"file input {item.get('input_id')} {field} mismatch")
    if expected_sha is not None and actual_sha != expected_sha:
        raise E1Error(f"pinned SHA-256 mismatch: {path}")
    if require_git_binding:
        _verify_git_binding(item, path, raw, info)
    return path


def _dimension_values(dimension: Mapping[str, Any]) -> tuple[str | int, ...]:
    name = dimension.get("name")
    if not isinstance(name, str) or not name:
        raise E1Error("dimension name missing")
    has_values = "values" in dimension
    has_range = "range" in dimension
    if has_values == has_range:
        raise E1Error(f"dimension {name} must have exactly one values/range binding")
    if has_values:
        values = dimension["values"]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise E1Error(f"dimension {name} values invalid")
        return tuple(sorted(values, key=lambda v: str(v).encode("utf-8")))
    range_value = dimension["range"]
    if range_value != {"first": 1, "last_symbol": "SCM_MAX_FD", "step": 1,
                       "materialize_before_fingerprint": True}:
        raise E1Error(f"unbound range in dimension {name}")
    return tuple(range(1, SCM_MAX_FD + 1))


def _binding_applicable(scenario_id: str, binding: Mapping[str, str | int]) -> bool:
    if scenario_id in {"CAP_CLOSE_FSM_FAULT_MATRIX", "STARTUP_CLOSE_BOUNDARY_FAULT_MATRIX"}:
        approval = binding["approval_receiver"]
        broker_approval = binding["message"] == "TerminalBrokerCloseCommitApprovalV2"
        return approval in ({"GUARDIAN", "SHIM"} if broker_approval else {"NOT_APPLICABLE"})
    if scenario_id == "CAP_PIDFD_ESCALATION_MATRIX":
        return ((binding["path"] == "SELF_SUCCESS" and binding["returned_error"] == "NOT_APPLICABLE")
                or (binding["path"] != "SELF_SUCCESS" and binding["returned_error"] != "NOT_APPLICABLE"))
    return True


def _variants(record: Mapping[str, Any]) -> Iterator[tuple[str, dict[str, str | int]]]:
    dimensions = record.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise E1Error(f"missing dimensions: {record.get('scenario_id')}")
    ordered = sorted(dimensions, key=lambda d: str(d.get("name", "")).encode("utf-8"))
    names = [str(d["name"]) for d in ordered]
    if len(names) != len(set(names)):
        raise E1Error(f"duplicate dimension: {record.get('scenario_id')}")
    for product in itertools.product(*(_dimension_values(d) for d in ordered)):
        binding = dict(zip(names, product))
        if not _binding_applicable(str(record["scenario_id"]), binding):
            continue
        suffix = ",".join(f"{name}={binding[name]}" for name in names)
        yield f"{record['scenario_id']}::{suffix}", binding


def _variant_count(record: Mapping[str, Any]) -> int:
    return sum(1 for _ in _variants(record))


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    _exact_keys(manifest, TOP_MANIFEST_KEYS, "manifest")
    fixed = {
        "artifact_type": "IU4_I7_E1_TERMINAL_LEASE_CAPABILITY_MANIFEST",
        "schema_version": 1,
        "manifest_id": "IU4_I7_E1_TERMINAL_LEASE_CAPABILITY_MANIFEST_V1",
        "canonical_repository": CANONICAL_REPOSITORY,
        "specification_sha256": SPECIFICATION_SHA256,
        "profile_id": "TerminalLeaseCapabilityProfileV14",
        "human_decision_id": "E1_SCENARIO_UNIVERSE_HUMAN_DECISION_2026_09_01",
        "ordering": "BYTEWISE_ASCENDING",
        "parameter_variants": "ONE_ID_WITH_BOUND_MATRIX",
        "trial_semantics": "10000_PER_BOUND_VARIANT",
        "startup_relation": "INDEPENDENT_SET",
    }
    for key, expected in fixed.items():
        if manifest.get(key) != expected:
            raise E1Error(f"manifest {key} mismatch")
    if tuple(manifest.get("scenario_ids", ())) != SCENARIO_IDS:
        raise E1Error("closed capability ID set/order mismatch")
    if tuple(manifest.get("startup_scenario_ids", ())) != STARTUP_SCENARIO_IDS:
        raise E1Error("closed startup ID set/order mismatch")
    if manifest.get("forbidden_paths") != list(FORBIDDEN_PATHS):
        raise E1Error("forbidden paths mismatch")
    for key, ids, record_keys, count_key, count in (
        ("scenarios", SCENARIO_IDS, CAPABILITY_RECORD_KEYS, "trials_per_bound_variant", 10000),
        ("startup_scenarios", STARTUP_SCENARIO_IDS, STARTUP_RECORD_KEYS, "probes_per_bound_variant", 32),
    ):
        records = manifest.get(key)
        if not isinstance(records, list) or tuple(r.get("scenario_id") for r in records) != ids:
            raise E1Error(f"{key} record closure/order mismatch")
        for record in records:
            if not isinstance(record, dict):
                raise E1Error(f"invalid record in {key}")
            _exact_keys(record, record_keys, f"record {record.get('scenario_id')}")
            if record[count_key] != count or not record["required_observations"] or not record["pass_predicate"]:
                raise E1Error(f"record semantics mismatch: {record['scenario_id']}")
            if _variant_count(record) < 1:
                raise E1Error(f"empty matrix: {record['scenario_id']}")


def _validate_contract(contract: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    _exact_keys(contract, CONTRACT_KEYS, "contract")
    if contract.get("artifact_type") != "IU4_I7_WORKSTATION_RUN_CONTRACT" or contract.get("schema_version") != 3:
        raise E1Error("workstation contract identity mismatch")
    if contract.get("schema_id") != "IU4_I7_WORKSTATION_RUN_CONTRACT_SCHEMA_V3" or contract.get("canonical_repository") != CANONICAL_REPOSITORY:
        raise E1Error("workstation contract schema/repository mismatch")
    cap = contract.get("capability")
    if not isinstance(cap, dict):
        raise E1Error("contract capability object missing")
    if cap.get("scenario_ids") != list(SCENARIO_IDS) or cap.get("startup_scenario_ids") != list(STARTUP_SCENARIO_IDS):
        raise E1Error("contract scenario closure mismatch")
    trials_per_scenario = cap.get("trials_per_scenario")
    if type(trials_per_scenario) is not int or trials_per_scenario != 10000:
        raise E1Error("contract capability trial count mismatch")
    startup_probes_per_scenario = cap.get("startup_probes_per_scenario")
    if (type(startup_probes_per_scenario) is not int
            or startup_probes_per_scenario != 32):
        raise E1Error("contract startup probe count mismatch")
    cap_variants = sum(_variant_count(r) for r in manifest["scenarios"])
    startup_variants = sum(_variant_count(r) for r in manifest["startup_scenarios"])
    expected_trial_count = cap.get("expected_trial_count")
    if (type(expected_trial_count) is not int
            or expected_trial_count != cap_variants * 10000):
        raise E1Error("capability count mismatch: ID-count substitution is forbidden")
    expected_startup_probe_count = cap.get("expected_startup_probe_count")
    if (type(expected_startup_probe_count) is not int
            or expected_startup_probe_count != startup_variants * 32):
        raise E1Error("startup count mismatch: ID-count substitution is forbidden")
    observer = contract.get("observer")
    cleanup = contract.get("cleanup")
    if not isinstance(observer, dict) or observer.get("independent_from_harness") is not True:
        raise E1Error("independent observer binding missing")
    required_cleanup = {"run_owned_only": True, "zero_residue_required": True,
                        "preexisting_state_identical": True, "no_retry_same_session": True}
    if not isinstance(cleanup, dict):
        raise E1Error("cleanup fail-closed binding missing")
    run_owned_only = cleanup.get("run_owned_only")
    if type(run_owned_only) is not bool or run_owned_only is not True:
        raise E1Error("cleanup run-owned-only binding missing")
    zero_residue_required = cleanup.get("zero_residue_required")
    if type(zero_residue_required) is not bool or zero_residue_required is not True:
        raise E1Error("cleanup zero-residue binding missing")
    preexisting_state_identical = cleanup.get("preexisting_state_identical")
    if (type(preexisting_state_identical) is not bool
            or preexisting_state_identical is not True):
        raise E1Error("cleanup preexisting-state binding missing")
    no_retry_same_session = cleanup.get("no_retry_same_session")
    if type(no_retry_same_session) is not bool or no_retry_same_session is not True:
        raise E1Error("cleanup no-retry same-session binding missing")
    if any(cleanup.get(k) != v for k, v in required_cleanup.items()):
        raise E1Error("cleanup fail-closed binding missing")
    return _input_map(contract)


def _write_new(path: Path, payload: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise E1Error(f"short write: {path}")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--artifact-schema", required=True)
    parser.add_argument("--run-root", required=True)
    return parser.parse_args(argv)


def _observer_call(observer: Path, contract_path: Path, request: Mapping[str, Any],
                   request_path: Path, output_path: Path, timeout: int) -> Mapping[str, Any]:
    _write_new(request_path, _canonical(request))
    command = [str(observer), "--e1-contract", str(contract_path),
               "--e1-request", str(request_path), "--e1-output", str(output_path)]
    environment = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False, timeout=timeout,
            cwd=CANONICAL_REPOSITORY, env=environment, start_new_session=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise E1Error(f"observer timeout after {timeout}s") from exc
    if completed.returncode != 0:
        raise E1Error(
            f"observer failure rc={completed.returncode} elapsed={time.monotonic()-started:.6f}s"
        )
    response, _ = _strict_json(output_path)
    _exact_keys(response, RESPONSE_KEYS, "observer response")
    for key in ("protocol", "run_id", "kind", "scenario_id", "variant_id"):
        if response.get(key) != request.get(key):
            raise E1Error(f"observer response {key} mismatch")
    return response


def _validate_record(record: Mapping[str, Any], kind: str, index: int,
                     offset: int, expected_environment_fingerprint: str) -> None:
    common = {
        "injected_fault", "boundary", "expected", "actual", "kernel_timestamps",
        "observer_reference", "sentinel_reference", "environment_fingerprint",
        "raw_record_sha256", "status", "retry_count",
    }
    if kind == "CAPABILITY":
        expected = common | {"trial_index", "trip_offset_us"}
        index_key, offset_key = "trial_index", "trip_offset_us"
    else:
        expected = common | {"phase_index", "phase_offset_us"}
        index_key, offset_key = "phase_index", "phase_offset_us"
    _exact_keys(record, frozenset(expected), f"{kind} record")
    index_value = record.get(index_key)
    offset_value = record.get(offset_key)
    if type(index_value) is not int or type(offset_value) is not int:
        raise E1Error(f"{kind} record index/offset types invalid")
    if index_value != index or offset_value != offset:
        raise E1Error(f"{kind} record index/offset mismatch")
    for key in ("injected_fault", "boundary"):
        value = record.get(key)
        if not isinstance(value, str) or not value:
            raise E1Error(f"{kind} record invalid {key}")
    timestamps = record.get('kernel_timestamps')
    if not isinstance(timestamps, dict):
        raise E1Error(f'{kind} record kernel_timestamps is not an object')
    _exact_keys(
        timestamps, KERNEL_TIMESTAMP_KEYS,
        f'{kind} record kernel_timestamps',
    )
    if timestamps.get('clock') != 'CLOCK_BOOTTIME':
        raise E1Error(f'{kind} record kernel_timestamps clock mismatch')
    timestamp_values: list[int] = []
    for timestamp_name in KERNEL_TIMESTAMP_VALUE_KEYS:
        timestamp_value = timestamps.get(timestamp_name)
        if (not isinstance(timestamp_value, int)
                or isinstance(timestamp_value, bool)
                or timestamp_value < 0):
            raise E1Error(
                f'{kind} record invalid kernel timestamp {timestamp_name}'
            )
        timestamp_values.append(timestamp_value)
    if timestamp_values[0] <= 0:
        raise E1Error(f'{kind} record kernel timestamps are unmeasured')
    if any(earlier > later for earlier, later in zip(
            timestamp_values, timestamp_values[1:])):
        raise E1Error(f'{kind} record kernel timestamps are not ordered')
    if timestamp_values[-1] <= timestamp_values[0]:
        raise E1Error(f'{kind} record kernel timestamps are degenerate')
    if (timestamps['kernel_accept_ns'] - timestamps['injection_ns']
            > KERNEL_SIGNAL_GENERATION_BUDGET_NS):
        raise E1Error(f'{kind} record exceeds kernel signal generation budget')
    if (timestamps['trip_cas_ns'] - timestamps['kernel_accept_ns']
            > BROKER_TRIP_CAS_MAX_NS):
        raise E1Error(f'{kind} record exceeds broker Trip-CAS maximum')
    if (timestamps['fatal_action_ns'] - timestamps['trip_cas_ns']
            > GUARDIAN_TRIP_DISPATCH_MAX_NS):
        raise E1Error(f'{kind} record exceeds Guardian Trip-dispatch maximum')
    if timestamp_values[-1] - timestamp_values[0] > FAILSTOP_MAX_NS:
        raise E1Error(f'{kind} record exceeds failstop maximum')
    outcomes: dict[str, Mapping[str, Any]] = {}
    for outcome_name in ("expected", "actual"):
        outcome = record.get(outcome_name)
        if not isinstance(outcome, dict):
            raise E1Error(f"{kind} record {outcome_name} is not an object")
        _exact_keys(
            outcome, OUTCOME_VECTOR_KEYS,
            f"{kind} record {outcome_name} outcome vector",
        )
        if any(not isinstance(value, str) or not value
               for value in outcome.values()):
            raise E1Error(
                f"{kind} record {outcome_name} contains an empty outcome"
            )
        outcomes[outcome_name] = outcome
    if _canonical(outcomes["expected"]) != _canonical(outcomes["actual"]):
        raise E1Error(f"{kind} record expected/actual outcome mismatch")
    retry_count = record.get("retry_count")
    if type(retry_count) is not int or retry_count != 0:
        raise E1Error(f"{kind} record is not a first-attempt PASS")
    if record.get("status") != "PASS":
        raise E1Error(f"{kind} record is not a first-attempt PASS")
    for key in ("observer_reference", "sentinel_reference",
                "environment_fingerprint", "raw_record_sha256"):
        value = record.get(key)
        if (not isinstance(value, str)
                or SHA256_PATTERN.fullmatch(value) is None):
            raise E1Error(f"{kind} record invalid {key}")
    if record["environment_fingerprint"] != expected_environment_fingerprint:
        raise E1Error(f"{kind} record environment fingerprint mismatch")


def _validate_raw_entries(
    entries: Sequence[Any], run_root: Path, seen_paths: set[str],
    raw_record_sha256: str,
) -> list[Mapping[str, Any]]:
    validated: list[Mapping[str, Any]] = []
    response_paths: set[str] = set()
    matching_record_entries = 0
    for entry in entries:
        if not isinstance(entry, dict):
            raise E1Error("raw artifact entry is not an object")
        _exact_keys(entry, RAW_ENTRY_KEYS, "raw artifact entry")
        logical_path = entry.get("logical_path")
        if not isinstance(logical_path, str):
            raise E1Error("raw artifact logical_path is not a string")
        components = logical_path.split("/")
        if (not logical_path or logical_path.startswith("/")
                or "\\" in logical_path or "\0" in logical_path
                or any(component in ("", ".", "..")
                       for component in components)):
            raise E1Error(
                f"raw artifact logical_path is not canonical: {logical_path}"
            )
        if logical_path in response_paths or logical_path in seen_paths:
            raise E1Error(f"duplicate raw artifact logical_path: {logical_path}")
        relative_path = Path(logical_path)
        artifact_path = run_root / relative_path
        try:
            artifact_path.relative_to(run_root)
        except ValueError as exc:
            raise E1Error("raw artifact escapes the bound run root") from exc
        info = _regular_file(artifact_path)
        raw = artifact_path.read_bytes()
        actual_sha256 = _sha256(raw)
        claimed_sha256 = entry.get("sha256")
        if (not isinstance(claimed_sha256, str)
                or SHA256_PATTERN.fullmatch(claimed_sha256) is None
                or claimed_sha256 != actual_sha256):
            raise E1Error(f"raw artifact SHA-256 mismatch: {logical_path}")
        for field, actual in (
            ("size", len(raw)), ("mode", stat.S_IMODE(info.st_mode)),
            ("uid", info.st_uid), ("gid", info.st_gid),
        ):
            claimed = entry.get(field)
            if (not isinstance(claimed, int) or isinstance(claimed, bool)
                    or claimed != actual):
                raise E1Error(f"raw artifact {field} mismatch: {logical_path}")
        if actual_sha256 == raw_record_sha256:
            matching_record_entries += 1
        response_paths.add(logical_path)
        seen_paths.add(logical_path)
        validated.append(entry)
    if matching_record_entries != 1:
        raise E1Error(
            "record raw_record_sha256 does not bind exactly one current raw artifact"
        )
    return validated


def _attestation_ok(
    observer: Mapping[str, Any], cleanup: Mapping[str, Any],
    expected_observer_sha: str,
) -> None:
    _exact_keys(observer, OBSERVER_ATTESTATION_KEYS, "observer attestation")
    _exact_keys(cleanup, CLEANUP_ATTESTATION_KEYS, "cleanup attestation")
    observer_id = observer.get("observer_id")
    if not isinstance(observer_id, str) or not observer_id:
        raise E1Error("observer attestation has invalid observer_id")
    for key in ("observer_sha256", "snapshot_root"):
        value = observer.get(key)
        if (not isinstance(value, str)
                or SHA256_PATTERN.fullmatch(value) is None):
            raise E1Error(f"observer attestation has invalid {key}")
    if observer["observer_sha256"] != expected_observer_sha:
        raise E1Error("observer attestation SHA-256 mismatch")
    required_observer = {
        "independent_process": True, "independent_owner": True,
        "complete_kernel_timestamps": True,
    }
    required_cleanup = {
        "run_owned_only": True, "zero_residue": True,
        "preexisting_bytes_identical": True,
        "preexisting_metadata_identical": True, "same_session_retry_count": 0,
    }
    if any(observer.get(k) is not v for k, v in required_observer.items()):
        raise E1Error("observer independence/timestamp attestation failed")
    if any(cleanup.get(k) is not v for k, v in required_cleanup.items()
           if isinstance(v, bool)):
        raise E1Error("cleanup/restoration attestation failed")
    retry_count = cleanup.get("same_session_retry_count")
    if type(retry_count) is not int or retry_count != 0:
        raise E1Error("cleanup same-session retry attestation failed")
    cleanup_root = cleanup.get("cleanup_root")
    if (not isinstance(cleanup_root, str)
            or SHA256_PATTERN.fullmatch(cleanup_root) is None):
        raise E1Error("cleanup attestation has invalid cleanup_root")


def _root_for(values: Iterable[Any]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(_canonical(value))
    return digest.hexdigest()


def _run_record_series(
    *, kind: str, record: Mapping[str, Any], variant_id: str,
    binding: Mapping[str, str | int], record_count: int, run_id: str,
    profile_fingerprint: str, platform_fingerprint: str, observer: Path,
    contract_path: Path, output_directory: Path, run_root: Path,
    seen_raw_paths: set[str], timeout: int, expected_observer_sha: str,
    attestation_binding: dict[str, Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    records: list[Mapping[str, Any]] = []
    raw_entries: list[Mapping[str, Any]] = []
    for index in range(record_count):
        offset = index if kind == "CAPABILITY" else (index * 10000) // 32
        stem = f"{index:05d}"
        request_path = output_directory / f"request-{stem}.json"
        output_path = output_directory / f"response-{stem}.json"
        request = {
            "protocol": PROTOCOL, "run_id": run_id, "kind": kind,
            "scenario_id": record["scenario_id"], "variant_id": variant_id,
            "dimension_bindings": dict(binding), "record_index": index,
            "offset_us": offset,
            "required_observations": record["required_observations"],
            "pass_predicate": record["pass_predicate"],
            "profile_fingerprint": profile_fingerprint,
            "platform_fingerprint": platform_fingerprint,
        }
        _exact_keys(request, REQUEST_KEYS, "observer request")
        response = _observer_call(observer, contract_path, request, request_path,
                                  output_path, timeout)
        response_record = response.get("record")
        obs = response.get("observer_attestation")
        cleanup = response.get("cleanup_attestation")
        entries = response.get("raw_entries")
        if not isinstance(response_record, dict) or not isinstance(obs, dict) or not isinstance(cleanup, dict) or not isinstance(entries, list):
            raise E1Error("observer response payload types invalid")
        _validate_record(
            response_record, kind, index, offset, profile_fingerprint,
        )
        _attestation_ok(obs, cleanup, expected_observer_sha)
        if response_record["observer_reference"] != obs["snapshot_root"]:
            raise E1Error("record observer reference mismatch")
        if response_record["sentinel_reference"] != cleanup["cleanup_root"]:
            raise E1Error("record sentinel reference mismatch")
        if not attestation_binding:
            attestation_binding["observer"] = obs
            attestation_binding["cleanup"] = cleanup
        elif (_canonical(obs) != _canonical(attestation_binding["observer"])
              or _canonical(cleanup)
              != _canonical(attestation_binding["cleanup"])):
            raise E1Error("observer or cleanup identity drift")
        validated_entries = _validate_raw_entries(
            entries, run_root, seen_raw_paths,
            str(response_record["raw_record_sha256"]),
        )
        records.append(response_record)
        raw_entries.extend(validated_entries)
    return records, raw_entries


def _execute(
    contract: Mapping[str, Any], manifest: Mapping[str, Any], contract_path: Path,
    observer: Path, run_root: Path, contract_sha: str, runner_sha: str,
    manifest_sha: str, schema_sha: str, observer_sha: str,
    identities: Mapping[str, Any],
) -> Mapping[str, Any]:
    run_id = str(contract["run_id"])
    platform_fingerprint = _sha256(_canonical({
        "host": contract["host"], "guest": contract["guest"],
        "privileges": contract["privileges"],
    }))
    profile_fingerprint = _sha256(_canonical({
        "common_profile": manifest["common_profile"],
        "platform_fingerprint": platform_fingerprint,
    }))
    timeout = int(contract["capability"]["per_scenario_timeout_seconds"])
    capability_root = run_root / "capability"
    startup_root = run_root / "startup"
    observer_root = run_root / "observer"
    for directory in (capability_root, startup_root, observer_root):
        directory.mkdir(mode=0o700)
    capability_results: list[Mapping[str, Any]] = []
    startup_results: list[Mapping[str, Any]] = []
    all_raw_entries: list[Mapping[str, Any]] = []
    seen_raw_paths: set[str] = set()
    attestation_binding: dict[str, Mapping[str, Any]] = {}
    for kind, records, root, sample_count, destination in (
        ("CAPABILITY", manifest["scenarios"], capability_root, 10000, capability_results),
        ("STARTUP", manifest["startup_scenarios"], startup_root, 32, startup_results),
    ):
        for scenario in records:
            variant_results: list[Mapping[str, Any]] = []
            scenario_directory = root / scenario["scenario_id"]
            scenario_directory.mkdir(mode=0o700)
            for variant_number, (variant_id, binding) in enumerate(_variants(scenario)):
                variant_directory = scenario_directory / f"{variant_number:08d}"
                variant_directory.mkdir(mode=0o700)
                series, entries = _run_record_series(
                    kind=kind, record=scenario, variant_id=variant_id,
                    binding=binding, record_count=sample_count, run_id=run_id,
                    profile_fingerprint=profile_fingerprint,
                    platform_fingerprint=platform_fingerprint, observer=observer,
                    contract_path=contract_path, output_directory=variant_directory,
                    run_root=run_root, seen_raw_paths=seen_raw_paths,
                    timeout=timeout, expected_observer_sha=observer_sha,
                    attestation_binding=attestation_binding,
                )
                all_raw_entries.extend(entries)
                variant_result = {
                    "variant_id": variant_id, "dimension_bindings": dict(binding),
                    ("expected_trial_count" if kind == "CAPABILITY" else "expected_probe_count"): sample_count,
                    ("trials" if kind == "CAPABILITY" else "probes"): series,
                    "status": "PASS", "variant_root": _root_for(series),
                }
                variant_results.append(variant_result)
            destination.append({
                "scenario_id": scenario["scenario_id"],
                "variant_count": len(variant_results), "variants": variant_results,
                "status": "PASS", "scenario_root": _root_for(variant_results),
            })
    final_observer = attestation_binding.get("observer")
    final_cleanup = attestation_binding.get("cleanup")
    if final_observer is None or final_cleanup is None:
        raise E1Error("empty execution is forbidden")
    raw_manifest = {
        "canonical_serialization": "UTF8_LF_SORTED_KEYS_NO_BOM",
        "entries": all_raw_entries, "manifest_root": _root_for(all_raw_entries),
    }
    ordered_variant_roots = [
        variant["variant_root"]
        for scenario_result in capability_results
        for variant in scenario_result["variants"]
    ]
    ordered_variant_roots.extend(
        variant["variant_root"]
        for scenario_result in startup_results
        for variant in scenario_result["variants"]
    )
    semantic_root = _root_for((
        manifest, profile_fingerprint, platform_fingerprint,
        ordered_variant_roots,
    ))
    run_root_hash = _root_for((semantic_root, raw_manifest, final_observer,
                               final_cleanup, identities))
    return {
        "artifact_type": "IU4_I7_E1_TERMINAL_LEASE_CAPABILITY_RESULT",
        "schema_version": 1, "run_id": run_id,
        "contract_sha256": contract_sha, "runner_sha256": runner_sha,
        "manifest_sha256": manifest_sha, "artifact_schema_sha256": schema_sha,
        "specification_sha256": SPECIFICATION_SHA256,
        "profile_fingerprint": profile_fingerprint,
        "platform_fingerprint": platform_fingerprint,
        "scenario_results": capability_results,
        "startup_scenario_results": startup_results,
        "raw_artifact_manifest": raw_manifest,
        "observer_attestation": final_observer,
        "cleanup_attestation": final_cleanup,
        "semantic_root": semantic_root, "run_attestation_root": run_root_hash,
        "final_status": "PASS",
    }


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(raw_argv)
    if args.manifest != CAPABILITY_MANIFEST_PATH:
        raise E1Error("manifest path is not the exact canonical CAPABILITY_MANIFEST path")
    if args.artifact_schema != CAPABILITY_ARTIFACT_SCHEMA_PATH:
        raise E1Error("artifact schema path is not the exact canonical CAPABILITY_ARTIFACT_SCHEMA path")
    own_path = Path(__file__)
    if not own_path.is_absolute():
        own_path = Path.cwd() / own_path
    if own_path != Path(CAPABILITY_RUNNER_PATH):
        raise E1Error("runner path is not the exact canonical CAPABILITY_RUNNER path")
    _regular_file(own_path)
    runner_sha = _sha256(own_path.read_bytes())
    contract_path = Path(args.contract)
    manifest_path = Path(args.manifest)
    schema_path = Path(args.artifact_schema)
    run_root = _verify_new_run_root(args.run_root)
    for value in (contract_path, manifest_path, schema_path, run_root):
        if not value.is_absolute():
            raise E1Error(f"absolute path required: {value}")
    contract_info = _regular_file(contract_path)
    contract_mode = stat.S_IMODE(contract_info.st_mode)
    if ((contract_mode & 0o444) == 0
            or (contract_mode & 0o222) != 0):
        raise E1Error("contract must be read-only and readable")
    contract, contract_raw = _strict_json(contract_path)
    manifest, manifest_raw = _strict_json(manifest_path)
    schema, schema_raw = _strict_json(schema_path)
    if _sha256(manifest_raw) != MANIFEST_SHA256 or _sha256(schema_raw) != ARTIFACT_SCHEMA_SHA256:
        raise E1Error("manifest/schema file-exact identity mismatch")
    _validate_manifest(manifest)
    file_inputs = _validate_contract(contract, manifest)
    required = {"SPECIFICATION", "CAPABILITY_RUNNER", "CAPABILITY_MANIFEST",
                "CAPABILITY_ARTIFACT_SCHEMA", "OBSERVER_RUNNER",
                "OBSERVER_SNAPSHOT_SCHEMA", "E2_ACCEPTANCE_DECISION",
                "E3_ACCEPTANCE_DECISION", "E1_EXECUTION_MANDATE", "BTF",
                "VMLINUX"}
    if not required.issubset(file_inputs):
        raise E1Error(f"required file inputs missing: {sorted(required-set(file_inputs))}")
    for expected_role, expected_path in (
        ("CAPABILITY_RUNNER", CAPABILITY_RUNNER_PATH),
        ("CAPABILITY_MANIFEST", CAPABILITY_MANIFEST_PATH),
        ("CAPABILITY_ARTIFACT_SCHEMA", CAPABILITY_ARTIFACT_SCHEMA_PATH),
    ):
        matching_roles = [
            role for role, item in file_inputs.items()
            if item.get("path") == expected_path
        ]
        if matching_roles != [expected_role]:
            raise E1Error(
                f"canonical E1 artifact path has non-unique role binding: {expected_path}"
            )
        canonical_path = Path(expected_path)
        for role, item in file_inputs.items():
            if role == expected_role:
                continue
            candidate_value = item.get("path")
            if not isinstance(candidate_value, str):
                raise E1Error(f"file input {role} path missing during alias check")
            candidate_path = Path(candidate_value)
            if not candidate_path.is_absolute():
                candidate_path = Path(CANONICAL_REPOSITORY) / candidate_path
            try:
                aliases_artifact = os.path.samefile(candidate_path, canonical_path)
            except (OSError, ValueError) as exc:
                raise E1Error(
                    f"file input {role} identity unavailable during alias check"
                ) from exc
            if aliases_artifact:
                raise E1Error(
                    f"canonical E1 artifact has alternative role alias: {role}"
                )
    for role in file_inputs:
        alternative_e2 = (role != "E2_ACCEPTANCE_DECISION"
                          and role.startswith("E2_")
                          and ("ACCEPTANCE" in role or "DECISION" in role))
        alternative_e3 = (role != "E3_ACCEPTANCE_DECISION"
                          and role.startswith("E3_")
                          and ("ACCEPTANCE" in role or "DECISION" in role))
        alternative_mandate = (
            role != "E1_EXECUTION_MANDATE"
            and (role == "EXECUTION_MANDATE"
                 or role.startswith("E1_EXECUTION_MANDATE")
                 or role.endswith("_EXECUTION_MANDATE"))
        )
        if alternative_e2 or alternative_e3 or alternative_mandate:
            raise E1Error(f"alternative decision or mandate role forbidden: {role}")
    for item in file_inputs.values():
        path_text = str(item.get("path", ""))
        if any(path_text == str(Path(CANONICAL_REPOSITORY) / forbidden)
               for forbidden in FORBIDDEN_PATHS):
            raise E1Error("forbidden source bound as input")
    _verify_file_input(file_inputs["SPECIFICATION"], expected_path=Path(SPECIFICATION_PATH),
                       expected_sha=SPECIFICATION_SHA256)
    _verify_file_input(
        file_inputs["CAPABILITY_RUNNER"], expected_path=Path(CAPABILITY_RUNNER_PATH),
        require_git_binding=True,
    )
    _verify_file_input(file_inputs["CAPABILITY_MANIFEST"], expected_path=manifest_path,
                       expected_sha=MANIFEST_SHA256, require_git_binding=True)
    _verify_file_input(file_inputs["CAPABILITY_ARTIFACT_SCHEMA"], expected_path=schema_path,
                       expected_sha=ARTIFACT_SCHEMA_SHA256,
                       require_git_binding=True)
    observer_path = _verify_file_input(file_inputs["OBSERVER_RUNNER"])
    _verify_file_input(file_inputs["OBSERVER_SNAPSHOT_SCHEMA"])
    if file_inputs["OBSERVER_RUNNER"].get("permission_policy") != "READ_ONLY_EXECUTABLE":
        raise E1Error("observer is not bound READ_ONLY_EXECUTABLE")
    e2_decision_path = _verify_file_input(file_inputs["E2_ACCEPTANCE_DECISION"])
    e3_decision_path = _verify_file_input(file_inputs["E3_ACCEPTANCE_DECISION"])
    for expected_role, decision_path in (
        ("E2_ACCEPTANCE_DECISION", e2_decision_path),
        ("E3_ACCEPTANCE_DECISION", e3_decision_path),
    ):
        matching_roles: list[str] = []
        for role, item in file_inputs.items():
            candidate_value = item.get("path")
            if not isinstance(candidate_value, str):
                raise E1Error(
                    f"file input {role} path missing during decision alias check"
                )
            candidate_path = Path(candidate_value)
            if not candidate_path.is_absolute():
                candidate_path = Path(CANONICAL_REPOSITORY) / candidate_path
            try:
                aliases_decision = os.path.samefile(candidate_path, decision_path)
            except (OSError, ValueError) as exc:
                raise E1Error(
                    f"file input {role} identity unavailable during decision alias check"
                ) from exc
            if aliases_decision:
                matching_roles.append(role)
        if matching_roles != [expected_role]:
            raise E1Error(
                f"E2/E3 acceptance decision has non-unique role binding: {expected_role}"
            )
    execution_mandate_input = file_inputs["E1_EXECUTION_MANDATE"]
    execution_mandate_path_value = execution_mandate_input.get("path")
    execution_mandate_path = _verify_file_input(
        execution_mandate_input, require_canonical_raw_path=True,
    )
    if not isinstance(execution_mandate_path_value, str):
        raise E1Error("E1 execution mandate raw path is not a string")
    mandate_matching_roles: list[str] = []
    for role, item in file_inputs.items():
        candidate_value = item.get("path")
        if not isinstance(candidate_value, str):
            raise E1Error(
                f"file input {role} path missing during mandate alias check"
            )
        candidate_path = Path(candidate_value)
        if not candidate_path.is_absolute():
            candidate_path = Path(CANONICAL_REPOSITORY) / candidate_path
        try:
            aliases_mandate = os.path.samefile(
                candidate_path, execution_mandate_path,
            )
        except (OSError, ValueError) as exc:
            raise E1Error(
                f"file input {role} identity unavailable during mandate alias check"
            ) from exc
        if aliases_mandate:
            mandate_matching_roles.append(role)
    if mandate_matching_roles != ["E1_EXECUTION_MANDATE"]:
        raise E1Error("E1 execution mandate has non-unique role binding")
    if e2_decision_path == e3_decision_path:
        raise E1Error("E2/E3 acceptance decision paths are not separate")
    decision_paths = {str(e2_decision_path), str(e3_decision_path)}
    if any(role not in {"E2_ACCEPTANCE_DECISION", "E3_ACCEPTANCE_DECISION"}
           and str(item.get("path", "")) in decision_paths
           for role, item in file_inputs.items()):
        raise E1Error("E2/E3 acceptance decision path has an alternative role")
    if any(role != "E1_EXECUTION_MANDATE"
           and str(item.get("path", "")) == str(execution_mandate_path)
           for role, item in file_inputs.items()):
        raise E1Error("E1 execution mandate path has an alternative role")
    e2_decision, _ = _strict_json(e2_decision_path)
    e3_decision, _ = _strict_json(e3_decision_path)
    execution_mandate, _ = _strict_json(execution_mandate_path)
    _validate_prerequisite_decisions(
        contract, e2_decision, e3_decision,
        str(file_inputs["OBSERVER_RUNNER"]["sha256"]),
        str(file_inputs["OBSERVER_SNAPSHOT_SCHEMA"]["sha256"]),
    )
    _consume_execution_mandate(
        execution_mandate, execution_mandate_path_value, contract,
        contract_path, run_root, raw_argv,
        runner_sha, file_inputs, e2_decision_path, e2_decision,
        e3_decision_path, e3_decision,
    )
    _verify_new_run_root(args.run_root)
    run_root.mkdir(mode=0o700, parents=False)
    contract_sha = _sha256(contract_raw)
    _write_new(run_root / "contract.json", contract_raw)
    _write_new(run_root / "materialized_manifest.json", _canonical(manifest))
    identities = {
        "contract_sha256": contract_sha, "runner_sha256": runner_sha,
        "manifest_sha256": MANIFEST_SHA256,
        "artifact_schema_sha256": ARTIFACT_SCHEMA_SHA256,
        "specification_sha256": SPECIFICATION_SHA256,
    }
    _write_new(run_root / "identities.json", _canonical(identities))
    result = _execute(contract, manifest, contract_path, observer_path, run_root,
                      contract_sha, runner_sha, MANIFEST_SHA256,
                      ARTIFACT_SCHEMA_SHA256,
                      str(file_inputs["OBSERVER_RUNNER"]["sha256"]),
                      identities)
    _validate_result_schema(result, schema)
    _write_new(run_root / "raw_artifact_manifest.json",
               _canonical(result["raw_artifact_manifest"]))
    _write_new(run_root / "result.json", _canonical(result))
    print("E1_TERMINAL_LEASE_CAPABILITY_RESULT: PASS")
    print(f"RUN_ATTESTATION_ROOT: {result['run_attestation_root']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except E1Error as exc:
        print(f"E1_TERMINAL_LEASE_CAPABILITY_RESULT: FAIL\n{exc}", file=sys.stderr)
        raise SystemExit(2)
