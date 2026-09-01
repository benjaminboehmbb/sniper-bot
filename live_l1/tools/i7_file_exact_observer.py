#!/usr/bin/env python3
"""Pure fail-closed evaluator for independently collected I7 snapshots.

The module performs no process, kernel, BPF, VM, QMP, SSH, or cleanup action.
It validates already-collected files below one bound fresh ``/tmp`` run root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import time
from pathlib import Path
from typing import Any, Iterable, Mapping


SNAPSHOT_CONTRACT_ID = "IU4_I7_OBSERVER_SNAPSHOT_V2"
SNAPSHOT_SCHEMA_VERSION = 2
PRE_SEQUENCE = 0
POST_SEQUENCE = 1
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^IU4-I7-RUN-[0-9A-F]{64}$")
NONCE_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_AUTHORITY_FILE = ".i7-run-authority.json"
RUN_IN_PROGRESS_FILE = ".i7-run-consume-in-progress.json"
RUN_COMPLETED_FILE = ".i7-run-completed.json"
MAX_RUNROOT_AGE_NS = 60 * 60 * 1_000_000_000
MAX_CLOCK_SKEW_NS = 5 * 1_000_000_000
RESOURCE_KINDS = (
    "processes", "fds", "sockets", "namespaces", "cgroups", "bpf",
    "qemu", "qmp", "ssh", "guest", "tmp",
)
ALLOWED_CLEANUP_OPERATIONS = (
    "TERM_THEN_KILL_REAP", "CLOSE", "UNLINK_RUN_OWNED",
)
_CONSUMED_COMPARISONS: set[tuple[str, str, str]] = set()


class I7ObserverError(RuntimeError):
    pass


class _BoundTmpRoot:
    def __init__(
        self, path: Path, authority: dict[str, Any],
        descriptors: list[int], components: tuple[str, ...],
        root_stat: os.stat_result, consumption: dict[str, Any],
    ) -> None:
        self.path = path
        self.authority = authority
        self.descriptors = descriptors
        self.components = components
        self.root_stat = root_stat
        self.consumption = consumption
        self.closed = False

    @property
    def root_descriptor(self) -> int:
        if self.closed:
            raise I7ObserverError("bound run root is closed")
        return self.descriptors[-1]

    def verify(self) -> None:
        if self.closed:
            raise I7ObserverError("bound run root is closed")
        _verify_absolute_directory_chain(self.descriptors, self.components)
        observed = os.fstat(self.root_descriptor)
        expected = self.root_stat
        if (
            observed.st_dev, observed.st_ino, observed.st_uid,
            observed.st_gid, observed.st_mode,
        ) != (
            expected.st_dev, expected.st_ino, expected.st_uid,
            expected.st_gid, expected.st_mode,
        ):
            raise I7ObserverError("bound run-root descriptor changed")

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            for descriptor in reversed(self.descriptors):
                os.close(descriptor)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def derive_run_id(
    nonce: str, *, root_device: int, root_inode: int,
    sentinel_device: int, sentinel_inode: int,
) -> str:
    if type(nonce) is not str or not NONCE_RE.fullmatch(nonce):
        raise I7ObserverError("run nonce is invalid")
    identities = (root_device, root_inode, sentinel_device, sentinel_inode)
    if any(type(value) is not int or value < 0 for value in identities) or (
        root_inode < 1 or sentinel_inode < 1
    ):
        raise I7ObserverError("run root/sentinel identity is invalid")
    payload = _canonical({
        "contract_id": SNAPSHOT_CONTRACT_ID, "nonce": nonce,
        "root_device": root_device, "root_inode": root_inode,
        "sentinel_device": sentinel_device, "sentinel_inode": sentinel_inode,
    })
    return "IU4-I7-RUN-" + hashlib.sha256(payload).hexdigest().upper()


def _validate_authority(authority: object) -> dict[str, Any]:
    fields = {
        "artifact_type", "schema_version", "contract_id", "nonce", "run_id",
        "created_at_ns", "root_device", "root_inode", "root_uid", "root_gid",
        "root_mode", "sentinel_device", "sentinel_inode", "sentinel_uid",
        "sentinel_gid", "sentinel_mode", "authority_sha256",
    }
    if type(authority) is not dict or set(authority) != fields:
        raise I7ObserverError("run authority schema mismatch")
    base = dict(authority)
    observed = base.pop("authority_sha256")
    if (
        authority["artifact_type"] != "IU4_I7_OBSERVER_RUN_AUTHORITY"
        or type(authority["schema_version"]) is not int
        or authority["schema_version"] != 1
        or authority["contract_id"] != SNAPSHOT_CONTRACT_ID
        or type(authority["nonce"]) is not str
        or derive_run_id(
            authority["nonce"], root_device=authority["root_device"],
            root_inode=authority["root_inode"],
            sentinel_device=authority["sentinel_device"],
            sentinel_inode=authority["sentinel_inode"],
        ) != authority["run_id"]
        or not RUN_ID_RE.fullmatch(str(authority["run_id"]))
        or type(authority["created_at_ns"]) is not int
        or authority["created_at_ns"] <= 0
        or any(type(authority[key]) is not int for key in (
            "root_device", "root_inode", "root_uid", "root_gid", "root_mode"
            , "sentinel_device", "sentinel_inode", "sentinel_uid",
            "sentinel_gid", "sentinel_mode"
        ))
        or type(observed) is not str or not SHA256_RE.fullmatch(observed)
        or _sha256(base) != observed
    ):
        raise I7ObserverError("run authority identity/hash mismatch")
    return dict(authority)


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            raise I7ObserverError("duplicate or non-string JSON key")
        result[key] = value
    return result


def _strict_json_bytes(payload: bytes) -> object:
    if (
        not payload.endswith(b"\n")
        or payload.endswith(b"\n\n")
        or b"\r" in payload
        or b"\0" in payload
    ):
        raise I7ObserverError("JSON must be ASCII, single-terminal-LF, CR/NUL-free")
    try:
        return json.loads(
            payload.decode("ascii"), object_pairs_hook=_pairs_no_duplicates
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise I7ObserverError("invalid strict JSON") from exc


def bind_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    if type(snapshot) is not dict:
        raise I7ObserverError("snapshot must be an exact object")
    base = dict(snapshot)
    base.pop("snapshot_sha256", None)
    return {**base, "snapshot_sha256": _sha256(base)}


def _exact_text(value: object, field: str) -> str:
    if type(value) is not str or not value:
        raise I7ObserverError(f"invalid {field}")
    return value


def validate_snapshot(
    snapshot: object,
    *,
    authority: object,
    expected_role: str,
    expected_sequence: int,
) -> dict[str, Any]:
    bound_authority = _validate_authority(authority)
    if type(snapshot) is not dict:
        raise I7ObserverError("snapshot must be an exact object")
    expected_fields = {
        "artifact_type", "schema_version", "contract_id", "run_id", "role",
        "sequence", "captured_at_ns", "observer_sha256", "observer_ok",
        "resources", "snapshot_sha256",
    }
    if set(snapshot) != expected_fields:
        raise I7ObserverError("snapshot fields are incomplete or unknown")
    if snapshot["artifact_type"] != "IU4_I7_OBSERVER_SNAPSHOT":
        raise I7ObserverError("snapshot artifact type mismatch")
    if (
        type(snapshot["schema_version"]) is not int
        or snapshot["schema_version"] != SNAPSHOT_SCHEMA_VERSION
    ):
        raise I7ObserverError("snapshot schema mismatch")
    if (
        snapshot["contract_id"] != SNAPSHOT_CONTRACT_ID
        or snapshot["run_id"] != bound_authority["run_id"]
    ):
        raise I7ObserverError("snapshot contract/run mismatch")
    if type(snapshot["role"]) is not str or snapshot["role"] != expected_role:
        raise I7ObserverError("snapshot role mismatch")
    if (
        type(snapshot["sequence"]) is not int
        or snapshot["sequence"] != expected_sequence
    ):
        raise I7ObserverError("snapshot sequence mismatch")
    if (
        type(snapshot["captured_at_ns"]) is not int
        or snapshot["captured_at_ns"] < bound_authority["created_at_ns"]
        or snapshot["captured_at_ns"] - bound_authority["created_at_ns"] > MAX_RUNROOT_AGE_NS
        or snapshot["captured_at_ns"] > time.time_ns() + MAX_CLOCK_SKEW_NS
    ):
        raise I7ObserverError("snapshot capture is outside authority/freshness order")
    if snapshot["observer_ok"] is not True:
        raise I7ObserverError("observer failure invalidates the run")
    if not SHA256_RE.fullmatch(
        _exact_text(snapshot["observer_sha256"], "observer_sha256")
    ):
        raise I7ObserverError("observer_sha256 is not SHA-256")
    if not SHA256_RE.fullmatch(
        _exact_text(snapshot["snapshot_sha256"], "snapshot_sha256")
    ):
        raise I7ObserverError("snapshot_sha256 is not SHA-256")
    resources = snapshot["resources"]
    if type(resources) is not dict or tuple(resources) != RESOURCE_KINDS:
        raise I7ObserverError("resource kinds or order mismatch")
    normalized: dict[str, tuple[dict[str, object], ...]] = {}
    global_ids: set[tuple[str, str]] = set()
    for kind in RESOURCE_KINDS:
        values = resources[kind]
        if type(values) is not list:
            raise I7ObserverError(f"{kind} inventory must be a list")
        records: list[dict[str, object]] = []
        for value in values:
            if type(value) is not dict or set(value) != {
                "resource_type", "stable_id", "fingerprint", "owner_run_id"
            }:
                raise I7ObserverError(f"invalid {kind} inventory record")
            if value["resource_type"] != kind:
                raise I7ObserverError(f"resource type mismatch for {kind}")
            stable_id = _exact_text(value["stable_id"], "stable_id")
            fingerprint = _exact_text(value["fingerprint"], "fingerprint")
            owner = value["owner_run_id"]
            if not SHA256_RE.fullmatch(fingerprint):
                raise I7ObserverError(f"invalid {kind} fingerprint")
            if owner is not None and (
                type(owner) is not str or not RUN_ID_RE.fullmatch(owner)
            ):
                raise I7ObserverError(f"invalid {kind} owner_run_id")
            identity = (kind, stable_id)
            if identity in global_ids:
                raise I7ObserverError(f"duplicate {kind} stable_id")
            global_ids.add(identity)
            records.append(dict(value))
        if records != sorted(records, key=lambda item: str(item["stable_id"])):
            raise I7ObserverError(f"{kind} inventory is not sorted")
        normalized[kind] = tuple(records)
    base = dict(snapshot)
    observed_hash = base.pop("snapshot_sha256")
    if _sha256(base) != observed_hash:
        raise I7ObserverError("snapshot hash mismatch")
    return {**dict(snapshot), "resources": normalized}


def evaluate_cleanup(
    before: object,
    after: object,
    *,
    authority: object,
) -> dict[str, Any]:
    bound_authority = _validate_authority(authority)
    run_id = bound_authority["run_id"]
    pre = validate_snapshot(
        before,
        authority=bound_authority,
        expected_role="PRE",
        expected_sequence=PRE_SEQUENCE,
    )
    post = validate_snapshot(
        after,
        authority=bound_authority,
        expected_role="POST",
        expected_sequence=POST_SEQUENCE,
    )
    if pre["snapshot_sha256"] == post["snapshot_sha256"]:
        raise I7ObserverError("PRE and POST snapshots must be distinct")
    if post["captured_at_ns"] <= pre["captured_at_ns"]:
        raise I7ObserverError("POST capture must be later than PRE")
    if pre["observer_sha256"] != post["observer_sha256"]:
        raise I7ObserverError("observer identity changed during run")
    findings: list[str] = []
    for kind in RESOURCE_KINDS:
        pre_values = pre["resources"][kind]
        post_values = post["resources"][kind]
        pre_owned = tuple(v for v in pre_values if v["owner_run_id"] == run_id)
        if pre_owned:
            findings.append(f"RUN_OWNED_PRESENT_IN_PRE:{kind}:{len(pre_owned)}")
        preexisting = tuple(v for v in pre_values if v["owner_run_id"] is None)
        post_preexisting = tuple(v for v in post_values if v["owner_run_id"] is None)
        post_owned = tuple(v for v in post_values if v["owner_run_id"] == run_id)
        foreign_owned = tuple(
            v for v in post_values if v["owner_run_id"] not in {None, run_id}
        )
        if preexisting != post_preexisting:
            findings.append(f"PREEXISTING_CHANGED:{kind}")
        if post_owned:
            findings.append(f"RUN_OWNED_RESIDUE:{kind}:{len(post_owned)}")
        if foreign_owned:
            findings.append(f"FOREIGN_OWNER_PRESENT:{kind}:{len(foreign_owned)}")
    if findings:
        raise I7ObserverError(";".join(findings))
    consumption = (
        bound_authority["authority_sha256"], pre["snapshot_sha256"],
        post["snapshot_sha256"],
    )
    if consumption in _CONSUMED_COMPARISONS:
        raise I7ObserverError("authority/snapshot comparison was already consumed")
    _CONSUMED_COMPARISONS.add(consumption)
    result_base = {
        "artifact_type": "IU4_I7_OBSERVER_COMPARISON",
        "schema_version": 2,
        "contract_id": SNAPSHOT_CONTRACT_ID,
        "run_id": run_id,
        "pre_snapshot_sha256": pre["snapshot_sha256"],
        "post_snapshot_sha256": post["snapshot_sha256"],
        "observer_sha256": pre["observer_sha256"],
        "preexisting_state_identical": True,
        "run_owned_residue_count": 0,
        "cleanup_result": "PASS",
    }
    return {**result_base, "result_sha256": _sha256(result_base)}


def validate_cleanup_plan(
    plan: object,
    *,
    source_snapshot: object,
    authority: object,
) -> tuple[tuple[str, str], ...]:
    bound_authority = _validate_authority(authority)
    run_id = bound_authority["run_id"]
    source = validate_snapshot(
        source_snapshot,
        authority=bound_authority,
        expected_role="POST",
        expected_sequence=POST_SEQUENCE,
    )
    if type(plan) is not dict or set(plan) != {
        "artifact_type", "schema_version", "contract_id", "run_id",
        "source_snapshot_hash", "targets",
    }:
        raise I7ObserverError("cleanup plan fields are incomplete or unknown")
    if (
        plan["artifact_type"] != "IU4_I7_CLEANUP_PLAN"
        or type(plan["schema_version"]) is not int
        or plan["schema_version"] != 2
    ):
        raise I7ObserverError("cleanup plan schema mismatch")
    if plan["contract_id"] != SNAPSHOT_CONTRACT_ID or plan["run_id"] != run_id:
        raise I7ObserverError("cleanup plan contract/run mismatch")
    if plan["source_snapshot_hash"] != source["snapshot_sha256"]:
        raise I7ObserverError("cleanup source snapshot mismatch")
    if type(plan["targets"]) is not list:
        raise I7ObserverError("cleanup targets must be a list")
    inventory = {
        (kind, str(record["stable_id"])): record
        for kind in RESOURCE_KINDS
        for record in source["resources"][kind]
    }
    seen: set[tuple[str, str]] = set()
    for target in plan["targets"]:
        if type(target) is not dict or set(target) != {
            "resource_type", "stable_id", "fingerprint", "owner_run_id",
            "source_snapshot_hash", "operation",
        }:
            raise I7ObserverError("invalid cleanup target")
        resource_type = target["resource_type"]
        stable_id = target["stable_id"]
        if type(resource_type) is not str or type(stable_id) is not str:
            raise I7ObserverError("cleanup target identity is invalid")
        key = (resource_type, stable_id)
        if key in seen:
            raise I7ObserverError("duplicate cleanup target")
        seen.add(key)
        record = inventory.get(key)
        if record is None or record["owner_run_id"] != run_id:
            raise I7ObserverError("cleanup may target only bound run-owned resources")
        if (
            target["owner_run_id"] != run_id
            or target["fingerprint"] != record["fingerprint"]
        ):
            raise I7ObserverError("cleanup target owner/fingerprint mismatch")
        if target["source_snapshot_hash"] != source["snapshot_sha256"]:
            raise I7ObserverError("cleanup target snapshot mismatch")
        if target["operation"] not in ALLOWED_CLEANUP_OPERATIONS:
            raise I7ObserverError("cleanup operation is not allowed")
    return tuple(sorted(seen))


def _open_absolute_directory(path: Path) -> tuple[list[int], tuple[str, ...]]:
    descriptors = [
        os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    ]
    components: list[str] = []
    try:
        for component in path.parts[1:]:
            next_descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=descriptors[-1],
            )
            descriptors.append(next_descriptor)
            components.append(component)
        return descriptors, tuple(components)
    except Exception:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _verify_absolute_directory_chain(
    descriptors: list[int], components: tuple[str, ...],
) -> None:
    if len(descriptors) != len(components) + 1:
        raise I7ObserverError("absolute descriptor-chain cardinality mismatch")
    for index, component in enumerate(components):
        linked = os.stat(
            component, dir_fd=descriptors[index], follow_symlinks=False
        )
        opened = os.fstat(descriptors[index + 1])
        if (
            linked.st_dev, linked.st_ino, linked.st_uid, linked.st_gid,
            linked.st_mode,
        ) != (
            opened.st_dev, opened.st_ino, opened.st_uid, opened.st_gid,
            opened.st_mode,
        ) or not stat.S_ISDIR(opened.st_mode):
            raise I7ObserverError("absolute parent chain changed during use")


def create_run_root(path: Path) -> dict[str, Any]:
    if not path.is_absolute() or ".." in path.parts or path == Path("/tmp"):
        raise I7ObserverError("run root path is invalid")
    if Path("/tmp") not in path.parents:
        raise I7ObserverError("run root must be below /tmp")
    parent_descriptors, parent_components = _open_absolute_directory(path.parent)
    parent_descriptor = parent_descriptors[-1]
    try:
        _verify_absolute_directory_chain(parent_descriptors, parent_components)
        os.mkdir(path.name, mode=0o700, dir_fd=parent_descriptor)
        root_descriptor = os.open(
            path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent_descriptor,
        )
    except Exception:
        for value in reversed(parent_descriptors):
            os.close(value)
        raise
    try:
        root_stat = os.fstat(root_descriptor)
        root_link = os.stat(
            path.name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        root_key = lambda value: (
            value.st_dev, value.st_ino, value.st_uid, value.st_gid,
            value.st_mode,
        )
        if (
            root_key(root_stat) != root_key(root_link)
            or not stat.S_ISDIR(root_stat.st_mode)
            or root_stat.st_uid != os.getuid()
            or root_stat.st_gid != os.getgid()
            or stat.S_IMODE(root_stat.st_mode) != 0o700
        ):
            raise I7ObserverError("create-new run root identity/mode mismatch")
        descriptor = os.open(
            RUN_AUTHORITY_FILE,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=root_descriptor,
        )
        sentinel_stat = os.fstat(descriptor)
        nonce = os.urandom(32).hex()
        base = {
            "artifact_type": "IU4_I7_OBSERVER_RUN_AUTHORITY",
            "schema_version": 1, "contract_id": SNAPSHOT_CONTRACT_ID,
            "nonce": nonce, "run_id": derive_run_id(
                nonce, root_device=root_stat.st_dev,
                root_inode=root_stat.st_ino,
                sentinel_device=sentinel_stat.st_dev,
                sentinel_inode=sentinel_stat.st_ino,
            ),
            "created_at_ns": time.time_ns(), "root_device": root_stat.st_dev,
            "root_inode": root_stat.st_ino, "root_uid": root_stat.st_uid,
            "root_gid": root_stat.st_gid,
            "root_mode": stat.S_IMODE(root_stat.st_mode),
            "sentinel_device": sentinel_stat.st_dev,
            "sentinel_inode": sentinel_stat.st_ino,
            "sentinel_uid": sentinel_stat.st_uid,
            "sentinel_gid": sentinel_stat.st_gid,
            "sentinel_mode": stat.S_IMODE(sentinel_stat.st_mode),
        }
        authority = {**base, "authority_sha256": _sha256(base)}
        try:
            payload = _canonical(authority) + b"\n"
            if os.write(descriptor, payload) != len(payload):
                raise I7ObserverError("short run-authority write")
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        sentinel_after = os.stat(
            RUN_AUTHORITY_FILE, dir_fd=root_descriptor, follow_symlinks=False
        )
        root_after = os.stat(
            path.name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            root_key(root_after) != root_key(root_stat)
            or sentinel_after.st_dev != sentinel_stat.st_dev
            or sentinel_after.st_ino != sentinel_stat.st_ino
            or sentinel_after.st_uid != os.getuid()
            or sentinel_after.st_gid != os.getgid()
            or sentinel_after.st_nlink != 1
            or stat.S_IMODE(sentinel_after.st_mode) != 0o600
        ):
            raise I7ObserverError("run root/sentinel changed during creation")
        os.fsync(root_descriptor)
        _verify_absolute_directory_chain(parent_descriptors, parent_components)
        os.fsync(parent_descriptor)
        return authority
    finally:
        os.close(root_descriptor)
        for value in reversed(parent_descriptors):
            os.close(value)


def _bound_tmp_root(path: Path) -> _BoundTmpRoot:
    if not path.is_absolute() or ".." in path.parts:
        raise I7ObserverError("run root path is invalid")
    if path == Path("/tmp") or Path("/tmp") not in path.parents:
        raise I7ObserverError("run root must be an existing child of /tmp")
    descriptors, parent_components = _open_absolute_directory(path.parent)
    parent_descriptor = descriptors[-1]
    try:
        _verify_absolute_directory_chain(descriptors, parent_components)
        root_descriptor = os.open(
            path.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
            dir_fd=parent_descriptor,
        )
        descriptors.append(root_descriptor)
    except Exception:
        for value in reversed(descriptors):
            os.close(value)
        raise
    try:
        st = os.fstat(root_descriptor)
        root_link_before = os.stat(
            path.name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        if (
            not stat.S_ISDIR(st.st_mode)
            or st.st_uid != os.getuid() or st.st_gid != os.getgid()
            or stat.S_IMODE(st.st_mode) != 0o700
            or (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
            != (root_link_before.st_dev, root_link_before.st_ino,
                root_link_before.st_uid, root_link_before.st_gid,
                root_link_before.st_mode)
        ):
            raise I7ObserverError("run root ownership/mode mismatch")
        for sentinel in (RUN_IN_PROGRESS_FILE, RUN_COMPLETED_FILE):
            try:
                os.stat(sentinel, dir_fd=root_descriptor, follow_symlinks=False)
            except FileNotFoundError:
                continue
            raise I7ObserverError("run root was already consumed")
        try:
            consume_descriptor = os.open(
                RUN_IN_PROGRESS_FILE,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600, dir_fd=root_descriptor,
            )
        except FileExistsError as exc:
            raise I7ObserverError("run root is already being consumed") from exc
        consume_stat = os.fstat(consume_descriptor)
        consumption_base = {
            "artifact_type": "IU4_I7_OBSERVER_CONSUMPTION",
            "schema_version": 1, "state": "IN_PROGRESS",
            "consumption_nonce": os.urandom(32).hex(),
            "started_at_ns": time.time_ns(),
            "root_device": st.st_dev, "root_inode": st.st_ino,
            "consume_device": consume_stat.st_dev,
            "consume_inode": consume_stat.st_ino,
        }
        consumption = {
            **consumption_base,
            "consumption_sha256": _sha256(consumption_base),
        }
        try:
            consume_payload = _canonical(consumption) + b"\n"
            if os.write(consume_descriptor, consume_payload) != len(consume_payload):
                raise I7ObserverError("short in-progress consumption write")
            os.fsync(consume_descriptor)
        finally:
            os.close(consume_descriptor)
        consume_link = os.stat(
            RUN_IN_PROGRESS_FILE, dir_fd=root_descriptor,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(consume_link.st_mode)
            or consume_link.st_nlink != 1
            or stat.S_IMODE(consume_link.st_mode) != 0o600
            or consume_link.st_uid != os.getuid()
            or consume_link.st_gid != os.getgid()
            or (consume_link.st_dev, consume_link.st_ino)
            != (consume_stat.st_dev, consume_stat.st_ino)
        ):
            raise I7ObserverError("in-progress consumption identity mismatch")
        os.fsync(root_descriptor)
        _verify_absolute_directory_chain(
            descriptors, parent_components + (path.name,)
        )
        authority_descriptor = os.open(
            RUN_AUTHORITY_FILE, os.O_RDONLY | os.O_NOFOLLOW,
            dir_fd=root_descriptor,
        )
        try:
            authority_stat = os.fstat(authority_descriptor)
            payload = b""
            while True:
                block = os.read(authority_descriptor, 65536)
                if not block:
                    break
                payload += block
            authority_after = os.fstat(authority_descriptor)
        finally:
            os.close(authority_descriptor)
        root_link_after = os.stat(
            path.name, dir_fd=parent_descriptor, follow_symlinks=False
        )
        _verify_absolute_directory_chain(
            descriptors, parent_components + (path.name,)
        )
        authority_link = os.stat(
            RUN_AUTHORITY_FILE, dir_fd=root_descriptor, follow_symlinks=False
        )
    except Exception:
        for value in reversed(descriptors):
            os.close(value)
        raise
    if (
        not stat.S_ISDIR(st.st_mode)
        or st.st_uid != os.getuid()
        or st.st_gid != os.getgid()
        or stat.S_IMODE(st.st_mode) != 0o700
        or (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
        != (root_link_before.st_dev, root_link_before.st_ino,
            root_link_before.st_uid, root_link_before.st_gid,
            root_link_before.st_mode)
        or (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
        != (root_link_after.st_dev, root_link_after.st_ino,
            root_link_after.st_uid, root_link_after.st_gid,
            root_link_after.st_mode)
    ):
        for value in reversed(descriptors):
            os.close(value)
        raise I7ObserverError("run root ownership/mode mismatch")
    if (
        not stat.S_ISREG(authority_stat.st_mode) or authority_stat.st_nlink != 1
        or stat.S_IMODE(authority_stat.st_mode) != 0o600
        or authority_stat.st_uid != os.getuid()
        or authority_stat.st_gid != os.getgid()
        or authority_stat.st_dev != authority_after.st_dev
        or authority_stat.st_ino != authority_after.st_ino
        or authority_stat.st_size != authority_after.st_size
        or (authority_stat.st_dev, authority_stat.st_ino, authority_stat.st_mode)
        != (authority_link.st_dev, authority_link.st_ino, authority_link.st_mode)
    ):
        for value in reversed(descriptors):
            os.close(value)
        raise I7ObserverError("run authority file identity mismatch")
    try:
        authority = _validate_authority(_strict_json_bytes(payload))
    except Exception:
        for value in reversed(descriptors):
            os.close(value)
        raise
    if any(authority[key] != expected for key, expected in {
        "root_device": st.st_dev, "root_inode": st.st_ino,
        "root_uid": st.st_uid, "root_gid": st.st_gid,
        "root_mode": stat.S_IMODE(st.st_mode),
        "sentinel_device": authority_stat.st_dev,
        "sentinel_inode": authority_stat.st_ino,
        "sentinel_uid": authority_stat.st_uid,
        "sentinel_gid": authority_stat.st_gid,
        "sentinel_mode": stat.S_IMODE(authority_stat.st_mode),
    }.items()):
        for value in reversed(descriptors):
            os.close(value)
        raise I7ObserverError("run authority/root binding mismatch")
    age = time.time_ns() - authority["created_at_ns"]
    if age < -5_000_000_000 or age > MAX_RUNROOT_AGE_NS:
        for value in reversed(descriptors):
            os.close(value)
        raise I7ObserverError("run root freshness window failed")
    return _BoundTmpRoot(
        path, authority, descriptors, parent_components + (path.name,),
        st, consumption,
    )


def _open_below_root(root: Path, path: Path, *, leaf_flags: int) -> tuple[int, list[int]]:
    if not path.is_absolute() or ".." in path.parts:
        raise I7ObserverError("observer input path is invalid")
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise I7ObserverError("observer input escapes run root")
    if not relative.parts:
        raise I7ObserverError("observer input cannot equal run root")
    descriptors, absolute_components = _open_absolute_directory(root)
    root_descriptor = descriptors[-1]
    parent = root_descriptor
    try:
        _verify_absolute_directory_chain(descriptors, absolute_components)
        for component in relative.parts[:-1]:
            descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent,
            )
            descriptors.append(descriptor)
            parent = descriptor
            st = os.fstat(descriptor)
            if st.st_uid != os.getuid() or st.st_mode & 0o077:
                raise I7ObserverError("observer parent-chain ownership/mode mismatch")
        if leaf_flags & os.O_CREAT:
            leaf = os.open(
                relative.parts[-1], leaf_flags | os.O_NOFOLLOW,
                0o600, dir_fd=parent,
            )
        else:
            leaf = os.open(
                relative.parts[-1], leaf_flags | os.O_NOFOLLOW,
                dir_fd=parent,
            )
        descriptors.append(leaf)
        return leaf, descriptors
    except Exception:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _open_below_bound(
    bound: _BoundTmpRoot, path: Path, *, leaf_flags: int,
) -> tuple[int, list[int]]:
    if not path.is_absolute() or ".." in path.parts:
        raise I7ObserverError("observer input path is invalid")
    try:
        relative = path.relative_to(bound.path)
    except ValueError as exc:
        raise I7ObserverError("observer input escapes run root") from exc
    if not relative.parts:
        raise I7ObserverError("observer input cannot equal run root")
    bound.verify()
    descriptors = [os.dup(value) for value in bound.descriptors]
    parent = descriptors[-1]
    try:
        for component in relative.parts[:-1]:
            descriptor = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent,
            )
            descriptors.append(descriptor)
            parent = descriptor
            st = os.fstat(descriptor)
            if st.st_uid != os.getuid() or st.st_mode & 0o077:
                raise I7ObserverError(
                    "observer parent-chain ownership/mode mismatch"
                )
        if leaf_flags & os.O_CREAT:
            leaf = os.open(
                relative.parts[-1], leaf_flags | os.O_NOFOLLOW,
                0o600, dir_fd=parent,
            )
        else:
            leaf = os.open(
                relative.parts[-1], leaf_flags | os.O_NOFOLLOW,
                dir_fd=parent,
            )
        descriptors.append(leaf)
        bound.verify()
        return leaf, descriptors
    except Exception:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _verify_open_chain(root: Path, path: Path, descriptors: list[int]) -> None:
    relative = path.relative_to(root)
    absolute_count = len(root.parts)
    absolute_components = tuple(root.parts[1:])
    _verify_absolute_directory_chain(
        descriptors[:absolute_count], absolute_components,
    )
    for index, component in enumerate(relative.parts):
        observed = os.stat(
            component,
            dir_fd=descriptors[absolute_count - 1 + index],
            follow_symlinks=False,
        )
        opened = os.fstat(descriptors[absolute_count + index])
        if (
            observed.st_dev, observed.st_ino, observed.st_mode
        ) != (
            opened.st_dev, opened.st_ino, opened.st_mode
        ):
            raise I7ObserverError("observer parent/leaf chain changed during use")


def _confined_input(root: Path, path: Path) -> Path:
    descriptor, descriptors = _open_below_root(root, path, leaf_flags=os.O_RDONLY)
    try:
        st = os.fstat(descriptor)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise I7ObserverError("observer input must be a non-aliased regular file")
        _verify_open_chain(root, path, descriptors)
    finally:
        for value in reversed(descriptors):
            os.close(value)
    return path


def _read_json(root: Path | _BoundTmpRoot, path: Path) -> object:
    flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, "O_NOATIME"):
        flags |= os.O_NOATIME
    root_path = root.path if isinstance(root, _BoundTmpRoot) else root
    descriptor, descriptors = (
        _open_below_bound(root, path, leaf_flags=flags)
        if isinstance(root, _BoundTmpRoot)
        else _open_below_root(root, path, leaf_flags=flags)
    )
    try:
        before = os.fstat(descriptor)
        blocks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        after = os.fstat(descriptor)
        _verify_open_chain(root_path, path, descriptors)
        if isinstance(root, _BoundTmpRoot):
            root.verify()
    finally:
        for value in reversed(descriptors):
            os.close(value)
    identity = lambda value: (
        value.st_dev, value.st_ino, value.st_mode, value.st_size
    )
    if identity(before) != identity(after) or not stat.S_ISREG(after.st_mode) or after.st_nlink != 1:
        raise I7ObserverError("observer input changed during read")
    return _strict_json_bytes(b"".join(blocks))


def _write_new(root: Path | _BoundTmpRoot, path: Path, value: object) -> None:
    if not path.is_absolute() or ".." in path.parts:
        raise I7ObserverError("observer output path is invalid")
    payload = _canonical(value) + b"\n"
    root_path = root.path if isinstance(root, _BoundTmpRoot) else root
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor, descriptors = (
        _open_below_bound(root, path, leaf_flags=flags)
        if isinstance(root, _BoundTmpRoot)
        else _open_below_root(root, path, leaf_flags=flags)
    )
    try:
        if os.write(descriptor, payload) != len(payload):
            raise I7ObserverError("short observer output write")
        os.fsync(descriptor)
        _verify_open_chain(root_path, path, descriptors)
        if isinstance(root, _BoundTmpRoot):
            root.verify()
    finally:
        for value in reversed(descriptors):
            os.close(value)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--run-root", type=Path, required=True)
    evaluate = commands.add_parser("evaluate")
    evaluate.add_argument("--run-root", type=Path, required=True)
    evaluate.add_argument("--before", type=Path, required=True)
    evaluate.add_argument("--after", type=Path, required=True)
    evaluate.add_argument("--cleanup-plan", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "init":
            authority = create_run_root(args.run_root)
            print(json.dumps(authority, sort_keys=True, separators=(",", ":")))
            return 0
        bound = _bound_tmp_root(args.run_root)
        try:
            authority = bound.authority
            before = _read_json(bound, args.before)
            after = _read_json(bound, args.after)
            plan = _read_json(bound, args.cleanup_plan)
            validate_cleanup_plan(
                plan, source_snapshot=after, authority=authority,
            )
            result = evaluate_cleanup(
                before, after, authority=authority,
            )
            _write_new(bound, args.output, result)
            _write_new(bound, bound.path / RUN_COMPLETED_FILE, {
                "artifact_type": "IU4_I7_OBSERVER_RUN_COMPLETED",
                "schema_version": 1, "state": "COMPLETED",
                "authority_sha256": authority["authority_sha256"],
                "consumption_sha256": bound.consumption[
                    "consumption_sha256"
                ],
                "result_sha256": result["result_sha256"],
                "completed_at_ns": time.time_ns(),
            })
            os.fsync(bound.root_descriptor)
            bound.verify()
        finally:
            bound.close()
    except (OSError, UnicodeError, I7ObserverError) as exc:
        print(f"I7_OBSERVER: FAIL: {exc}")
        return 1
    print("I7_OBSERVER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ALLOWED_CLEANUP_OPERATIONS", "I7ObserverError", "POST_SEQUENCE",
    "PRE_SEQUENCE", "RESOURCE_KINDS", "SNAPSHOT_CONTRACT_ID",
    "bind_snapshot", "create_run_root", "derive_run_id", "evaluate_cleanup",
    "validate_cleanup_plan", "validate_snapshot",
]
