#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import live_l1.tools.i7_file_exact_harness as harness
import live_l1.tools.i7_file_exact_observer as observer
import live_l1.tools.i7_staged_synthetic_replay as replay


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HEX64 = "a" * 64
CONTRACT_ID = observer.SNAPSHOT_CONTRACT_ID
RUN_NONCE = "0" * 64
RUN_ROOT_DEVICE = 1
RUN_ROOT_INODE = 11
RUN_SENTINEL_DEVICE = 1
RUN_SENTINEL_INODE = 12
AUTHORITY_CREATED_NS = time.time_ns() - 1_000_000_000
RUN_ID = observer.derive_run_id(
    RUN_NONCE, root_device=RUN_ROOT_DEVICE, root_inode=RUN_ROOT_INODE,
    sentinel_device=RUN_SENTINEL_DEVICE,
    sentinel_inode=RUN_SENTINEL_INODE,
)


def _authority() -> dict[str, object]:
    base = {
        "artifact_type": "IU4_I7_OBSERVER_RUN_AUTHORITY",
        "schema_version": 1, "contract_id": CONTRACT_ID,
        "nonce": RUN_NONCE, "run_id": RUN_ID,
        "created_at_ns": AUTHORITY_CREATED_NS,
        "root_device": RUN_ROOT_DEVICE, "root_inode": RUN_ROOT_INODE,
        "root_uid": os.getuid(),
        "root_gid": os.getgid(), "root_mode": 0o700,
        "sentinel_device": RUN_SENTINEL_DEVICE,
        "sentinel_inode": RUN_SENTINEL_INODE,
        "sentinel_uid": os.getuid(), "sentinel_gid": os.getgid(),
        "sentinel_mode": 0o600,
    }
    return {**base, "authority_sha256": observer._sha256(base)}


def _write(path: Path, payload: bytes, mode: int = 0o644) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    path.chmod(mode)
    return path


def _resources(
    *, owner: str | None = None, fingerprint: str = HEX64
) -> dict[str, list[dict[str, object]]]:
    value = {kind: [] for kind in observer.RESOURCE_KINDS}
    value["processes"] = [{
        "resource_type": "processes",
        "stable_id": "process-001",
        "fingerprint": fingerprint,
        "owner_run_id": owner,
    }]
    return value


def _snapshot(
    role: str,
    sequence: int,
    captured_at_ns: int,
    resources: dict[str, list[dict[str, object]]],
    *,
    run_id: str = RUN_ID,
    contract_id: str = CONTRACT_ID,
) -> dict[str, object]:
    return observer.bind_snapshot({
        "artifact_type": "IU4_I7_OBSERVER_SNAPSHOT",
        "schema_version": 2,
        "contract_id": contract_id,
        "run_id": run_id,
        "role": role,
        "sequence": sequence,
        "captured_at_ns": captured_at_ns,
        "observer_sha256": HEX64,
        "observer_ok": True,
        "resources": resources,
    })


def _file_record(
    input_id: str, path: Path, policy: str, *, confinement_root: Path | None = None
) -> dict[str, object]:
    st = os.lstat(path)
    root = confinement_root or (
        PROJECT_ROOT if PROJECT_ROOT in path.parents else path.parent
    )
    root_st = os.lstat(root)
    parent_chain = []
    logical = Path("/")
    root_anchor = os.lstat(logical)
    parent_chain.append(harness._directory_chain_record(
        logical, "/", root_anchor,
    ))
    for component in path.parent.parts[1:]:
        logical /= component
        parent_chain.append(harness._directory_chain_record(
            logical, component, os.lstat(logical),
        ))
    return {
        "input_id": input_id,
        "path": str(path),
        "confinement_root": str(root),
        "root_mode": stat.S_IMODE(root_st.st_mode),
        "root_uid": root_st.st_uid, "root_gid": root_st.st_gid,
        "root_device": root_st.st_dev, "root_inode": root_st.st_ino,
        "parent_chain": parent_chain,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": st.st_size,
        "mode": stat.S_IMODE(st.st_mode),
        "uid": st.st_uid,
        "gid": st.st_gid,
        "device": st.st_dev,
        "inode": st.st_ino,
        "permission_policy": policy,
    }


def _contract(root: Path) -> tuple[dict[str, object], dict[str, Path]]:
    canonical = {
        "SPECIFICATION": PROJECT_ROOT / "docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md",
        "FREEZE_MANIFEST": PROJECT_ROOT / "archive/IU4_I2_FREEZE_20260820/FREEZE_MANIFEST.txt",
        "FREEZE_TAR": PROJECT_ROOT / "archive/IU4_I2_FREEZE_20260820/IU4_I2_PRESERVATION_20260820.tar.gz",
        "GATE_MANIFEST": harness.DEFAULT_MANIFEST,
    }
    paths = dict(canonical)
    executable = {
        "CAPABILITY_RUNNER", "OBSERVER_RUNNER", "QEMU_BINARY", "COMPILER",
        "LINKER", "SUDO_BINARY",
    }
    for input_id in harness.REQUIRED_FILE_INPUT_IDS:
        if input_id in paths:
            continue
        mode = 0o600 if input_id == "SSH_PRIVATE_KEY" else (0o700 if input_id in executable else 0o644)
        paths[input_id] = _write(
            root / "inputs" / input_id.lower(),
            f"synthetic-{input_id}\n".encode("ascii"),
            mode,
        )
    records = []
    for input_id in harness.REQUIRED_FILE_INPUT_IDS:
        policy = (
            "PRIVATE_KEY" if input_id == "SSH_PRIVATE_KEY"
            else "READ_ONLY_EXECUTABLE" if input_id in executable
            else "READ_ONLY"
        )
        records.append(_file_record(input_id, paths[input_id], policy))
    return ({
        "artifact_type": "IU4_I7_WORKSTATION_RUN_CONTRACT",
        "schema_version": 3,
        "schema_id": harness.PINNED_SCHEMA_ID,
        "run_id": RUN_ID,
        "canonical_repository": str(PROJECT_ROOT),
        "host": {
            "host_id": "SYNTHETIC-DISPOSABLE-HOST",
            "human_authority_id": "SYNTHETIC-NONOPERATIVE-AUTHORITY",
            "disposable_host": True,
            "kernel_release": "synthetic",
            "kernel_build_id": "synthetic",
            "architecture": "x86_64",
            "boot_id": "synthetic",
            "clock_boottime_resolution_ns": 1,
            "active_lsm": ["bpf", "yama"],
            "bpffs_mount": "/synthetic/bpffs",
            "cgroup_v2_mount": "/synthetic/cgroup",
            "pid_namespace": "pid:[synthetic]",
            "mount_namespace": "mnt:[synthetic]",
            "user_namespace": "user:[synthetic]",
            "network_namespace": "net:[synthetic]",
            "yama_initial_scope": 1,
        },
        "guest": {
            "vm_id": "SYNTHETIC-DISPOSABLE-VM",
            "human_authority_id": "SYNTHETIC-NONOPERATIVE-AUTHORITY",
            "qemu_version": "synthetic",
            "qmp_socket": "/tmp/synthetic/qmp.sock",
            "guest_repo_readonly_path": "/synthetic/readonly",
            "ssh_host": "127.0.0.1",
            "ssh_port": 2222,
            "ssh_user": "synthetic",
            "restore_authority_id": "SYNTHETIC-RESTORE",
            "discard_authority_id": "SYNTHETIC-DISCARD",
            "reboot_authority_id": "SYNTHETIC-REBOOT",
            "suspend_authority_id": "SYNTHETIC-SUSPEND",
        },
        "privileges": {
            "human_authority_id": "SYNTHETIC-NONOPERATIVE-AUTHORITY",
            "expected_uid": os.getuid(),
            "expected_gid": os.getgid(),
            "allowed_commands": ["synthetic-noop"],
            "yama_restore_command": "synthetic-noop",
            "bpf_authority_id": "SYNTHETIC-BPF",
            "lsm_authority_id": "SYNTHETIC-LSM",
            "cgroup_authority_id": "SYNTHETIC-CGROUP",
            "namespace_authority_id": "SYNTHETIC-NS",
        },
        "capability": {
            "scenario_ids": ["SCENARIO_A", "SCENARIO_B"],
            "trials_per_scenario": 10000,
            "expected_trial_count": 20000,
            "startup_scenario_ids": ["STARTUP_A", "STARTUP_B"],
            "startup_probes_per_scenario": 32,
            "expected_startup_probe_count": 64,
            "per_scenario_timeout_seconds": 300,
            "global_timeout_seconds": 3600,
        },
        "observer": {
            "contract_id": CONTRACT_ID,
            "run_id_derivation": "SHA256_CANONICAL_CONTRACT_NONCE_ROOT_SENTINEL_IDENTITY_V2",
            "runroot_create_new": True,
            "runroot_max_age_ns": 3600000000000,
            "human_authority_id": "SYNTHETIC-OBSERVER",
            "independent_from_harness": True,
            "required_resource_kinds": list(observer.RESOURCE_KINDS),
        },
        "cleanup": {
            "run_owner_id": RUN_ID,
            "evidence_before_cleanup": True,
            "run_owned_only": True,
            "zero_residue_required": True,
            "preexisting_state_identical": True,
            "no_retry_same_session": True,
            "host_discard_on_restore_failure": True,
            "vm_discard_on_restore_failure": True,
        },
        "file_inputs": records,
        "stop_conditions": [
            "IDENTITY_MISMATCH", "IMPORT_OR_EFFECT_CLOSURE_MISMATCH",
            "COUNT_MISMATCH", "FAILURE_ERROR_OR_SKIP", "TIMEOUT",
            "OBSERVER_FAILURE", "RUN_OWNED_RESIDUE",
            "PREEXISTING_STATE_CHANGED", "YAMA_RESTORE_FAILURE",
            "QMP_SSH_OR_GUEST_FAILURE",
            "BPF_LSM_CGROUP_OR_NAMESPACE_MISMATCH",
            "UNAUTHORIZED_NETWORK_OR_CREDENTIAL_ACCESS",
        ],
    }, paths)


def _write_contract(root: Path, value: object) -> Path:
    return _write(
        root / "contract.json",
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n",
    )


class ManifestAndImportTests(unittest.TestCase):
    def _case_01_canonical_manifest_and_schema_are_hash_pinned(self) -> None:
        value = harness.load_manifest()
        self.assertEqual(value["manifest_id"], "IU4_I7_FILE_EXACT_GATES_RESOLUTION_5_V1")
        self.assertEqual(hashlib.sha256(harness.DEFAULT_MANIFEST.read_bytes()).hexdigest(), harness.PINNED_MANIFEST_SHA256)

    def _case_02_noncanonical_manifest_and_schema_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            other = _write(Path(name) / "manifest.json", harness.DEFAULT_MANIFEST.read_bytes())
            with self.assertRaises(harness.I7HarnessError):
                harness.load_manifest(other)
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(other, other)

    def _case_03_duplicate_json_keys_and_nonterminal_lf_are_rejected(self) -> None:
        with self.assertRaises(harness.I7HarnessError):
            harness._strict_json(b'{"a":1,"a":2}\n', label="test")
        with self.assertRaises(harness.I7HarnessError):
            harness._strict_json(b'{"a":1}', label="test")

    def _case_04_schema_missing_unknown_and_bool_as_int_fail_closed(self) -> None:
        schema = {"type": "object", "additionalProperties": False, "required": ["n"], "properties": {"n": {"type": "integer"}}}
        for value in ({}, {"n": 1, "x": 2}, {"n": True}):
            with self.subTest(value=value), self.assertRaises(harness.I7HarnessError):
                harness._validate_schema(value, schema)

    def _closure(self, files: dict[str, str], start: str) -> harness.ImportClosure:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            for relative, text in files.items():
                _write(root / relative, text.encode("ascii"))
            with mock.patch.object(harness, "PROJECT_ROOT", root), mock.patch.object(harness, "LOCAL_TOP_LEVELS", frozenset({"pkg"})):
                return harness.conservative_import_closure([start])

    def _case_05_implicit_package_initializers_are_included(self) -> None:
        closure = self._closure({"pkg/__init__.py": "VALUE=1\n", "pkg/mod.py": "X=1\n"}, "pkg.mod")
        self.assertEqual(set(closure.files), {"pkg/__init__.py", "pkg/mod.py"})

    def _case_06_missing_local_import_is_unresolved(self) -> None:
        closure = self._closure({"pkg/__init__.py": "\n", "pkg/mod.py": "import pkg.missing\n"}, "pkg.mod")
        self.assertTrue(closure.unresolved_local_imports)
        with self.assertRaises(harness.I7HarnessError):
            harness.assert_safe_closure(closure)

    def _case_07_relative_from_and_alias_imports_are_resolved(self) -> None:
        closure = self._closure({
            "pkg/__init__.py": "\n", "pkg/a.py": "X=1\n",
            "pkg/sub/__init__.py": "\n", "pkg/sub/mod.py": "from .. import a as alias\n",
        }, "pkg.sub.mod")
        self.assertIn("pkg/a.py", closure.files)
        self.assertFalse(closure.unresolved_local_imports)

    def _case_08_nonliteral_importlib_alias_is_dynamic(self) -> None:
        closure = self._closure({"pkg/__init__.py": "\n", "pkg/mod.py": "import importlib as il\nname='pkg.a'\nil.import_module(name)\n"}, "pkg.mod")
        self.assertTrue(closure.dynamic_imports)

    def _case_09_nonliteral_dunder_import_is_dynamic(self) -> None:
        closure = self._closure({"pkg/__init__.py": "\n", "pkg/mod.py": "name='pkg.a'\n__import__(name)\n"}, "pkg.mod")
        self.assertTrue(closure.dynamic_imports)

    def _case_10_getattr_import_construction_is_dynamic(self) -> None:
        closure = self._closure({"pkg/__init__.py": "\n", "pkg/mod.py": "import importlib\ngetattr(importlib,'import_module')('pkg.a')\n"}, "pkg.mod")
        self.assertTrue(closure.dynamic_imports)

    def _case_10a_assignment_alias_chains_rebinding_and_bindings_fail_closed(self) -> None:
        variants = {
            "importlib-assignment": "import importlib\nname='pkg.a'\nloader=importlib.import_module\nloader(name)\n",
            "dunder-assignment": "name='pkg.a'\nloader=__import__\nloader(name)\n",
            "getattr-assignment": "import importlib\nname='pkg.a'\ng=getattr\nloader=g(importlib,'import_module')\nloader(name)\n",
            "multistage": "import importlib\nname='pkg.a'\na=importlib.import_module\nb=a\nc=b\nc(name)\n",
            "rebind": "import importlib\nloader=importlib.import_module\nloader=object()\n",
            "named-expr": "import importlib\nname='pkg.a'\n(loader:=importlib.import_module)(name)\n",
            "unpacking": "import importlib\nname='pkg.a'\n(loader,other)=(importlib.import_module,object)\nloader(name)\n",
            "lambda": "import importlib\nname='pkg.a'\nloader=(lambda: importlib.import_module)()\nloader(name)\n",
            "default": "import importlib\nname='pkg.a'\ndef f(loader=importlib.import_module):\n loader(name)\n",
            "closure": "import importlib\nname='pkg.a'\nloader=importlib.import_module\ndef f():\n loader(name)\n",
            "subscript": "import importlib\nname='pkg.a'\nholder=[importlib.import_module]\nholder[0](name)\n",
            "named-factory-return": "import importlib\nname='pkg.a'\ndef factory():\n return importlib.import_module\nloader=factory()\nloader(name)\n",
            "if-expression": "import importlib\nname='pkg.a'\ncondition=object()\nloader=importlib.import_module if condition else print\nloader(name)\n",
            "bool-expression": "import importlib\nname='pkg.a'\nloader=object() and importlib.import_module\nloader(name)\n",
            "nested-value-expression": "import importlib\nname='pkg.a'\ndef factory():\n return importlib.import_module\ncondition=object()\nloader=(factory() if condition else (object() and importlib.import_module))\nloader(name)\n",
            "factory-alias-rebinding": "import importlib\nname='pkg.a'\ndef factory():\n return importlib.import_module\nother=factory\nloader=other()\nloader=print\n",
            "generator-next": "import importlib\nname='pkg.a'\nloader=next(x for x in [importlib.import_module])\nloader(name)\n",
            "list-comprehension": "import importlib\nname='pkg.a'\nloader=[x for x in [importlib.import_module]][0]\nloader(name)\n",
            "set-comprehension-iterator": "import importlib\nname='pkg.a'\nloader=next(iter({x for x in [importlib.import_module]}))\nloader(name)\n",
            "dict-comprehension": "import importlib\nname='pkg.a'\nloader={0:x for x in [importlib.import_module]}[0]\nloader(name)\n",
            "simple-namespace": "import importlib\nfrom types import SimpleNamespace\nname='pkg.a'\nloader=SimpleNamespace(loader=importlib.import_module).loader\nloader(name)\n",
            "partial": "import importlib\nfrom functools import partial\nname='pkg.a'\nloader=partial(importlib.import_module)\nloader(name)\n",
            "operator-itemgetter": "import importlib\nfrom operator import itemgetter\nname='pkg.a'\nloader=itemgetter(0)([importlib.import_module])\nloader(name)\n",
            "map-iterator": "import importlib\nname='pkg.a'\nloader=next(map(lambda x:x,[importlib.import_module]))\nloader(name)\n",
            "unknown-call-nested-return": "import importlib\nname='pkg.a'\ndef outer(value):\n def inner():\n  return value\n return inner()\nloader=outer(importlib.import_module)\nloader(name)\n",
            "async-method-return": "import importlib\nclass C:\n async def loader(self):\n  return importlib.import_module\n",
            "branch-join": "import importlib\nname='pkg.a'\nif object():\n loader=importlib.import_module\nelse:\n loader=print\nloader(name)\n",
            "decorator": "import importlib\ndef passthrough(value):\n return value\n@passthrough(importlib.import_module)\ndef target():\n pass\n",
        }
        for label, source in variants.items():
            closure = self._closure(
                {"pkg/__init__.py": "\n", "pkg/mod.py": source}, "pkg.mod"
            )
            with self.subTest(label=label):
                self.assertTrue(closure.dynamic_imports)
                with self.assertRaises(harness.I7HarnessError):
                    harness.assert_safe_closure(closure)
        harmless = {
            "safe-factory": "def factory():\n return print\nloader=factory()\nloader('ok')\n",
            "safe-if-expression": "condition=True\nloader=print if condition else len\nloader('ok')\n",
            "safe-bool-expression": "loader=object() and print\n",
            "safe-nested": "condition=True\ndef factory():\n return print\nloader=(factory() if condition else (object() and len))\n",
            "safe-generator": "loader=next(x for x in [print])\nloader('ok')\n",
            "safe-namespace": "from types import SimpleNamespace\nloader=SimpleNamespace(loader=print).loader\nloader('ok')\n",
            "safe-comprehensions": "values=[x for x in [len]]\nlookup={0:x for x in values}\n",
        }
        for label, source in harmless.items():
            closure = self._closure(
                {"pkg/__init__.py": "\n", "pkg/mod.py": source}, "pkg.mod"
            )
            with self.subTest(label=label):
                self.assertFalse(closure.dynamic_imports)

    def _case_11_forbidden_module_and_symlink_alias_are_rejected_without_read(self) -> None:
        closure = harness.conservative_import_closure(["live_l1.tools.validate_terminal_lease_capability"])
        self.assertTrue(closure.forbidden_edges)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            _write(root / "pkg/__init__.py", b"\n")
            target = _write(root / "target.py", b"SECRET\n")
            (root / "pkg/alias.py").symlink_to(target)
            with mock.patch.object(harness, "PROJECT_ROOT", root), mock.patch.object(harness, "LOCAL_TOP_LEVELS", frozenset({"pkg"})):
                aliased = harness.conservative_import_closure(["pkg.alias"])
            self.assertTrue(aliased.forbidden_edges)

    def _case_12_census_is_partitioned_and_never_executable(self) -> None:
        value = harness.load_manifest()
        census = value["gates"][2]
        self.assertEqual(set(census["candidate_modules"]), set(census["deferred_modules"]))
        self.assertEqual(census["local_safe_modules"], [])
        with self.assertRaises(harness.I7HarnessError):
            harness.run_gate("full_live_census_only", run_root=Path("/tmp/never-created"))

    def test_01_manifest_schema_and_exact_types(self) -> None:
        self._case_01_canonical_manifest_and_schema_are_hash_pinned()
        self._case_02_noncanonical_manifest_and_schema_paths_are_rejected()
        self._case_03_duplicate_json_keys_and_nonterminal_lf_are_rejected()
        self._case_04_schema_missing_unknown_and_bool_as_int_fail_closed()

    def test_02_package_relative_alias_and_missing_local_imports(self) -> None:
        self._case_05_implicit_package_initializers_are_included()
        self._case_06_missing_local_import_is_unresolved()
        self._case_07_relative_from_and_alias_imports_are_resolved()

    def test_03_dynamic_import_constructions_fail_closed(self) -> None:
        self._case_08_nonliteral_importlib_alias_is_dynamic()
        self._case_09_nonliteral_dunder_import_is_dynamic()
        self._case_10_getattr_import_construction_is_dynamic()
        self._case_10a_assignment_alias_chains_rebinding_and_bindings_fail_closed()

    def test_04_forbidden_alias_and_census_partition(self) -> None:
        self._case_11_forbidden_module_and_symlink_alias_are_rejected_without_read()
        self._case_12_census_is_partitioned_and_never_executable()


class ReplayTests(unittest.TestCase):
    def _case_13_three_pinned_stages_pass_and_s3_blocks_continuation(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            result = replay.run_staged_replay(run_root=Path(name) / "run")
        self.assertEqual(tuple(result["stage_ids"]), replay.STAGE_IDS)
        self.assertTrue(result["stages"][2]["observed"]["continuation_blocked"])

    def _case_14_stage_ids_have_no_path_authority_and_old_roots_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            with self.assertRaises(replay.I7StagedReplayError):
                replay._stage_output(root, -1)
            with self.assertRaises(replay.I7StagedReplayError):
                replay.run_staged_replay(run_root=root)

    def _case_15_input_hash_mismatch_fails_before_replay(self) -> None:
        original = replay.INPUT_BINDINGS["fixture"]["sha256"]
        with mock.patch.dict(replay.INPUT_BINDINGS["fixture"], {"sha256": "0" * 64}):
            with self.assertRaises(replay.I7StagedReplayError):
                replay._validate_fixture()
        self.assertEqual(replay.INPUT_BINDINGS["fixture"]["sha256"], original)

    def _case_16_malformed_fixture_with_matching_hash_still_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            payload = b"timestamp_utc,open\nmalformed,row\n"
            _write(root / "fixture.txt", payload)
            binding = {"path": "fixture.txt", "sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload), "lines": 2, "encoding": "ascii", "schema_id": "bad"}
            with mock.patch.object(replay, "PROJECT_ROOT", root), mock.patch.dict(replay.INPUT_BINDINGS, {"fixture": binding}):
                with self.assertRaises(replay.I7StagedReplayError):
                    replay._validate_fixture()

    def _case_16a_matching_hash_replay_json_exact_schema_and_cross_bindings(self) -> None:
        variants: list[tuple[str, dict[str, object], dict[str, object]]] = []
        profile = dict(replay.PROFILE_EXACT)
        changed = dict(profile); changed["UNKNOWN"] = "x"
        variants.append(("profile-unknown", changed, replay.POLICY_EXACT))
        changed = dict(profile); changed.pop("PEE_MODE")
        variants.append(("profile-missing", changed, replay.POLICY_EXACT))
        changed = dict(profile); changed["PEE_SCHEMA_VERSION"] = 1
        variants.append(("profile-wrong-type", changed, replay.POLICY_EXACT))
        changed = dict(profile); changed["PEE_MIN_QUANTITY"] = "0.0000001"
        variants.append(("profile-cross-binding", changed, replay.POLICY_EXACT))
        policy = json.loads(json.dumps(replay.POLICY_EXACT))
        changed_policy = json.loads(json.dumps(policy)); changed_policy["policy"]["extra"] = 1
        variants.append(("policy-nested-unknown", profile, changed_policy))
        changed_policy = json.loads(json.dumps(policy)); changed_policy["policy"]["max_entries_per_rolling_window"] = 1000001
        variants.append(("policy-cross-binding", profile, changed_policy))
        for label, profile_value, policy_value in variants:
            with tempfile.TemporaryDirectory(dir="/tmp") as name:
                root = Path(name)
                bindings = {}
                for input_name, value in (("profile", profile_value), ("policy", policy_value)):
                    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
                    _write(root / f"{input_name}.json", payload)
                    bindings[input_name] = {
                        "path": f"{input_name}.json",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "size": len(payload), "lines": 1, "encoding": "ascii",
                        "schema_id": replay.INPUT_BINDINGS[input_name]["schema_id"],
                    }
                with mock.patch.object(replay, "PROJECT_ROOT", root), mock.patch.dict(replay.INPUT_BINDINGS, bindings):
                    with self.subTest(label=label), self.assertRaises(replay.I7StagedReplayError):
                        replay._validate_json_inputs()

    def test_05_replay_pinning_traversal_hash_malformed_and_old_artifacts(self) -> None:
        self._case_13_three_pinned_stages_pass_and_s3_blocks_continuation()
        self._case_14_stage_ids_have_no_path_authority_and_old_roots_fail()
        self._case_15_input_hash_mismatch_fails_before_replay()
        self._case_16_malformed_fixture_with_matching_hash_still_fails()
        self._case_16a_matching_hash_replay_json_exact_schema_and_cross_bindings()


class ObserverTests(unittest.TestCase):
    def _case_17_distinct_pre_post_with_identical_preexisting_state_pass(self) -> None:
        pre = _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources())
        post = _snapshot("POST", 1, AUTHORITY_CREATED_NS + 2, _resources())
        result = observer.evaluate_cleanup(pre, post, authority=_authority())
        self.assertEqual(result["cleanup_result"], "PASS")

    def _case_18_identical_role_or_sequence_replay_is_rejected(self) -> None:
        pre = _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources())
        for bad in (pre, _snapshot("PRE", 1, AUTHORITY_CREATED_NS + 2, _resources()), _snapshot("POST", 0, AUTHORITY_CREATED_NS + 2, _resources())):
            with self.subTest(bad=bad["role"]), self.assertRaises(observer.I7ObserverError):
                observer.evaluate_cleanup(pre, bad, authority=_authority())

    def _case_19_wrong_contract_run_and_snapshot_hash_are_rejected(self) -> None:
        pre = _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources())
        variants = [dict(pre), _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources(), run_id="IU4-I7-OTHER"), _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources(), contract_id="OTHER")]
        variants[0]["snapshot_sha256"] = "0" * 64
        for value in variants:
            with self.assertRaises(observer.I7ObserverError):
                observer.validate_snapshot(value, authority=_authority(), expected_role="PRE", expected_sequence=0)

    def _case_20_disappearing_run_owned_prestate_is_rejected(self) -> None:
        pre = _snapshot("PRE", 0, AUTHORITY_CREATED_NS + 1, _resources(owner=RUN_ID))
        post = _snapshot("POST", 1, AUTHORITY_CREATED_NS + 2, {kind: [] for kind in observer.RESOURCE_KINDS})
        with self.assertRaises(observer.I7ObserverError):
            observer.evaluate_cleanup(pre, post, authority=_authority())

    def _case_21_cleanup_target_binds_type_id_fingerprint_owner_snapshot_and_operation(self) -> None:
        source = _snapshot("POST", 1, AUTHORITY_CREATED_NS + 2, _resources(owner=RUN_ID))
        target = {
            "resource_type": "processes", "stable_id": "process-001",
            "fingerprint": HEX64, "owner_run_id": RUN_ID,
            "source_snapshot_hash": source["snapshot_sha256"],
            "operation": "TERM_THEN_KILL_REAP",
        }
        plan = {"artifact_type": "IU4_I7_CLEANUP_PLAN", "schema_version": 2, "contract_id": CONTRACT_ID, "run_id": RUN_ID, "source_snapshot_hash": source["snapshot_sha256"], "targets": [target]}
        self.assertEqual(observer.validate_cleanup_plan(plan, source_snapshot=source, authority=_authority()), (("processes", "process-001"),))
        for key, bad in (("fingerprint", "0" * 64), ("operation", "RM_RF"), ("source_snapshot_hash", "0" * 64)):
            changed = json.loads(json.dumps(plan))
            changed["targets"][0][key] = bad
            with self.assertRaises(observer.I7ObserverError):
                observer.validate_cleanup_plan(changed, source_snapshot=source, authority=_authority())

    def _case_22_observer_inputs_cannot_escape_bound_tmp_root(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name, tempfile.TemporaryDirectory(dir="/tmp") as other:
            root = Path(name)
            outside = _write(Path(other) / "snapshot.json", b"{}\n")
            with self.assertRaises(observer.I7ObserverError):
                observer._confined_input(root, outside)

    def _case_22a_run_authority_freshness_parent_chain_and_replay(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            parent = Path(name)
            run_root = parent / "run"
            authority = observer.create_run_root(run_root)
            self.assertEqual(authority["run_id"], observer.derive_run_id(
                authority["nonce"], root_device=authority["root_device"],
                root_inode=authority["root_inode"],
                sentinel_device=authority["sentinel_device"],
                sentinel_inode=authority["sentinel_inode"],
            ))
            bound = observer._bound_tmp_root(run_root)
            self.assertEqual(
                (bound.path, bound.authority["run_id"]),
                (run_root, authority["run_id"]),
            )
            self.assertTrue(
                (run_root / observer.RUN_IN_PROGRESS_FILE).is_file()
            )
            for field in ("root_inode", "sentinel_inode"):
                tampered = dict(authority)
                tampered[field] = int(tampered[field]) + 1
                tampered_base = dict(tampered); tampered_base.pop("authority_sha256")
                tampered["authority_sha256"] = observer._sha256(tampered_base)
                with self.subTest(field=field), self.assertRaises(observer.I7ObserverError):
                    observer._validate_authority(tampered)
            pre = _snapshot(
                "PRE", 0, authority["created_at_ns"] + 1, _resources(),
                run_id=authority["run_id"],
            )
            post = _snapshot(
                "POST", 1, authority["created_at_ns"] + 2, _resources(),
                run_id=authority["run_id"],
            )
            self.assertEqual(
                observer.evaluate_cleanup(pre, post, authority=authority)["cleanup_result"],
                "PASS",
            )
            with self.assertRaises(observer.I7ObserverError):
                observer.evaluate_cleanup(pre, post, authority=authority)
            too_early = _snapshot(
                "PRE", 0, authority["created_at_ns"] - 1, _resources(),
                run_id=authority["run_id"],
            )
            with self.assertRaises(observer.I7ObserverError):
                observer.validate_snapshot(
                    too_early, authority=authority,
                    expected_role="PRE", expected_sequence=0,
                )
            with self.assertRaises(FileExistsError):
                observer.create_run_root(run_root)
            bound.close()
            with self.assertRaises(observer.I7ObserverError):
                observer._bound_tmp_root(run_root)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            parent = Path(name)
            run_root = parent / "run"
            authority = observer.create_run_root(run_root)
            stale = dict(authority); stale["created_at_ns"] = 1
            stale_base = dict(stale); stale_base.pop("authority_sha256")
            stale["authority_sha256"] = observer._sha256(stale_base)
            _write(
                run_root / observer.RUN_AUTHORITY_FILE,
                json.dumps(stale, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n",
                0o600,
            )
            with self.assertRaises(observer.I7ObserverError):
                observer._bound_tmp_root(run_root)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            real = root / "real"; real.mkdir(mode=0o700)
            target = _write(real / "snapshot.json", b"{}\n", 0o600)
            alias = root / "alias"; alias.symlink_to(real)
            with self.assertRaises((OSError, observer.I7ObserverError)):
                observer._confined_input(root, alias / target.name)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name)
            parent = base / "parent"; parent.mkdir(mode=0o700)
            descriptors, components = observer._open_absolute_directory(parent)
            try:
                parent.rename(base / "old-parent")
                parent.mkdir(mode=0o700)
                with self.assertRaises(observer.I7ObserverError):
                    observer._verify_absolute_directory_chain(
                        descriptors, components,
                    )
            finally:
                for descriptor in reversed(descriptors):
                    os.close(descriptor)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            run_root = Path(name) / "run"
            observer.create_run_root(run_root)
            child_code = (
                "import os,time;from pathlib import Path;"
                "from live_l1.tools import i7_file_exact_observer as o;"
                f"b=o._bound_tmp_root(Path({str(run_root)!r}));"
                "print('BOUND',flush=True);time.sleep(60)"
            )
            environment = {
                **os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPYCACHEPREFIX": str(Path(name) / "pycache"),
                "TMPDIR": name, "HOME": name,
                "PYTHONPATH": str(PROJECT_ROOT),
            }
            process = subprocess.Popen(
                [sys.executable, "-c", child_code], cwd=PROJECT_ROOT,
                env=environment, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, start_new_session=True,
            )
            try:
                self.assertEqual(process.stdout.readline().strip(), "BOUND")
                with self.assertRaises(observer.I7ObserverError):
                    observer._bound_tmp_root(run_root)
            finally:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stderr is not None:
                    process.stderr.close()
            with self.assertRaises(observer.I7ObserverError):
                observer._bound_tmp_root(run_root)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            parent = Path(name)
            run_root = parent / "run"
            observer.create_run_root(run_root)
            bound = observer._bound_tmp_root(run_root)
            _write(run_root / "pre.json", b"{}\n", 0o600)
            run_root.rename(parent / "old-run")
            run_root.mkdir(mode=0o700)
            try:
                with self.assertRaises(observer.I7ObserverError):
                    observer._read_json(bound, run_root / "pre.json")
            finally:
                bound.close()
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            run_root = Path(name) / "run"
            observer.create_run_root(run_root)
            bound = observer._bound_tmp_root(run_root)
            observer._write_new(
                bound, run_root / "result.json", {"result": "PASS"}
            )
            bound.close()
            self.assertFalse((run_root / observer.RUN_COMPLETED_FILE).exists())
            with self.assertRaises(observer.I7ObserverError):
                observer._bound_tmp_root(run_root)

    def test_06_pre_post_roles_sequence_and_distinctness(self) -> None:
        self._case_17_distinct_pre_post_with_identical_preexisting_state_pass()
        self._case_18_identical_role_or_sequence_replay_is_rejected()

    def test_07_observer_contract_run_hash_and_preowned_invariants(self) -> None:
        self._case_19_wrong_contract_run_and_snapshot_hash_are_rejected()
        self._case_20_disappearing_run_owned_prestate_is_rejected()

    def test_08_cleanup_binding_and_tmp_confinement(self) -> None:
        self._case_21_cleanup_target_binds_type_id_fingerprint_owner_snapshot_and_operation()
        self._case_22_observer_inputs_cannot_escape_bound_tmp_root()
        self._case_22a_run_authority_freshness_parent_chain_and_replay()


class WorkstationContractTests(unittest.TestCase):
    def _case_23_complete_synthetic_contract_validates_file_exactly(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, _ = _contract(root)
            result = harness.validate_workstation_contract(_write_contract(root, value))
        self.assertEqual(result["capability"]["expected_trial_count"], 20000)

    def _case_24_duplicate_contract_keys_and_alternate_schema_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            duplicate = _write(root / "duplicate.json", b'{"a":1,"a":2}\n')
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(duplicate)
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(duplicate, duplicate)

    def _case_25_contract_path_traversal_and_symlink_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, paths = _contract(root)
            record = next(item for item in value["file_inputs"] if item["input_id"] == "CAPABILITY_RUNNER")
            record["path"] = str(root / "inputs" / ".." / paths["CAPABILITY_RUNNER"].name)
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))

    def _case_25a_parent_symlinks_inside_outside_nested_and_swap_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name)
            confined = base / "confined"; confined.mkdir(mode=0o700)
            inside = confined / "inside"; inside.mkdir(mode=0o700)
            outside = base / "outside"; outside.mkdir(mode=0o700)
            _write(inside / "file", b"inside\n", 0o600)
            _write(outside / "file", b"outside\n", 0o600)
            for label, target in (("inside", inside), ("outside", outside)):
                alias = confined / f"alias-{label}"; alias.symlink_to(target)
                record = _file_record(
                    "CAPABILITY_RUNNER", alias / "file", "READ_ONLY",
                    confinement_root=confined,
                )
                with self.subTest(label=label), self.assertRaises((OSError, harness.I7HarnessError)):
                    harness._verify_contract_file(record)
            nested = confined / "nested"; nested.mkdir(mode=0o700)
            nested_alias = nested / "alias"; nested_alias.symlink_to(inside)
            record = _file_record(
                "CAPABILITY_RUNNER", nested_alias / "file", "READ_ONLY",
                confinement_root=confined,
            )
            with self.assertRaises((OSError, harness.I7HarnessError)):
                harness._verify_contract_file(record)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name); confined = base / "confined"; confined.mkdir(mode=0o700)
            nested = confined / "nested"; nested.mkdir(mode=0o700)
            leaf = _write(nested / "file", b"bound\n", 0o600)
            outside = base / "outside"; outside.mkdir(mode=0o700)
            _write(outside / "file", b"other\n", 0o600)
            record = _file_record(
                "CAPABILITY_RUNNER", leaf, "READ_ONLY", confinement_root=confined
            )
            real_open = os.open
            swapped = [False]
            def swapping_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
                descriptor = real_open(path, flags, *args, **kwargs)
                if path == "nested" and kwargs.get("dir_fd") is not None and not swapped[0]:
                    swapped[0] = True
                    os.rename(nested, confined / "moved")
                    nested.symlink_to(outside)
                return descriptor
            with mock.patch.object(harness.os, "open", side_effect=swapping_open):
                with self.assertRaises(harness.I7HarnessError):
                    harness._verify_contract_file(record)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            base = Path(name); confined = base / "confined"; confined.mkdir(mode=0o700)
            leaf = _write(confined / "file", b"old-root\n", 0o600)
            record = _file_record(
                "CAPABILITY_RUNNER", leaf, "READ_ONLY",
                confinement_root=confined,
            )
            real_chain = harness._open_absolute_directory_chain
            swapped = [False]

            def swapping_root(path: Path) -> tuple[list[int], list[tuple[Path, str, os.stat_result]]]:
                result = real_chain(path)
                if path == confined and not swapped[0]:
                    swapped[0] = True
                    confined.rename(base / "old-confined")
                    confined.mkdir(mode=0o700)
                    _write(confined / "file", b"new-root\n", 0o600)
                return result

            with mock.patch.object(
                harness, "_open_absolute_directory_chain",
                side_effect=swapping_root,
            ), self.assertRaises(harness.I7HarnessError):
                harness._verify_contract_file(record)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, paths = _contract(root)
            record = next(item for item in value["file_inputs"] if item["input_id"] == "CAPABILITY_RUNNER")
            alias = root / "alias"
            alias.symlink_to(paths["CAPABILITY_RUNNER"])
            record["path"] = str(alias)
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))

    def _case_26_contract_hardlink_alias_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, paths = _contract(root)
            alias = root / "hardlink"
            os.link(paths["CAPABILITY_RUNNER"], alias)
            record = next(item for item in value["file_inputs"] if item["input_id"] == "OBSERVER_RUNNER")
            record.update(_file_record("OBSERVER_RUNNER", alias, "READ_ONLY_EXECUTABLE"))
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))

    def _case_27_contract_mode_owner_hash_and_permission_mismatches_fail(self) -> None:
        for field, replacement in (("sha256", "0" * 64), ("uid", 999999), ("mode", 0)):
            with tempfile.TemporaryDirectory(dir="/tmp") as name:
                root = Path(name)
                value, _ = _contract(root)
                record = next(item for item in value["file_inputs"] if item["input_id"] == "CAPABILITY_MANIFEST")
                record[field] = replacement
                with self.subTest(field=field), self.assertRaises(harness.I7HarnessError):
                    harness.validate_workstation_contract(_write_contract(root, value))
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, paths = _contract(root)
            paths["CAPABILITY_MANIFEST"].chmod(0o666)
            record = next(item for item in value["file_inputs"] if item["input_id"] == "CAPABILITY_MANIFEST")
            record.update(_file_record("CAPABILITY_MANIFEST", paths["CAPABILITY_MANIFEST"], "READ_ONLY"))
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))

    def _case_27a_parent_root_owner_mode_contract_fails(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name) / "inputs"; root.mkdir(mode=0o700)
            leaf = _write(root / "file", b"x\n", 0o600)
            record = _file_record(
                "CAPABILITY_RUNNER", leaf, "READ_ONLY", confinement_root=root
            )
            record["root_uid"] = int(record["root_uid"]) + 1
            with self.assertRaises(harness.I7HarnessError):
                harness._verify_contract_file(record)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name) / "inputs"; root.mkdir(mode=0o700)
            nested = root / "nested"; nested.mkdir(mode=0o700)
            leaf = _write(nested / "file", b"x\n", 0o600)
            record = _file_record(
                "CAPABILITY_RUNNER", leaf, "READ_ONLY", confinement_root=root
            )
            record["parent_chain"][-1]["inode"] = int(
                record["parent_chain"][-1]["inode"]
            ) + 1
            with self.assertRaises(harness.I7HarnessError):
                harness._verify_contract_file(record)
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name) / "inputs"; root.mkdir(mode=0o777)
            root.chmod(0o777)
            leaf = _write(root / "file", b"x\n", 0o600)
            record = _file_record(
                "CAPABILITY_RUNNER", leaf, "READ_ONLY", confinement_root=root
            )
            with self.assertRaises(harness.I7HarnessError):
                harness._verify_contract_file(record)

    def _case_28_scenario_ids_are_unique_and_totals_are_derived_from_ids(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, _ = _contract(root)
            value["capability"]["scenario_ids"] = ["SCENARIO_A", "SCENARIO_A"]
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))

    def test_09_contract_schema_duplicate_path_and_symlink_boundaries(self) -> None:
        self._case_23_complete_synthetic_contract_validates_file_exactly()
        self._case_24_duplicate_contract_keys_and_alternate_schema_fail()
        self._case_25_contract_path_traversal_and_symlink_fail()
        self._case_25a_parent_symlinks_inside_outside_nested_and_swap_fail()

    def test_10_contract_hardlink_mode_owner_hash_and_permission_boundaries(self) -> None:
        self._case_26_contract_hardlink_alias_fails()
        self._case_27_contract_mode_owner_hash_and_permission_mismatches_fail()
        self._case_27a_parent_root_owner_mode_contract_fails()

    def test_11_capability_ids_and_counts_are_derived_not_asserted(self) -> None:
        self._case_28_scenario_ids_are_unique_and_totals_are_derived_from_ids()
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            value, _ = _contract(root)
            value["capability"]["expected_startup_probe_count"] = 32
            with self.assertRaises(harness.I7HarnessError):
                harness.validate_workstation_contract(_write_contract(root, value))


class ProcessAndEvidenceTests(unittest.TestCase):
    def _case_29_timeout_terms_kills_and_reaps_child_grandchild_group(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            root = Path(name)
            pidfile = root / "pids"
            grandchild = (
                "import os,signal,time;"
                "ready_fd=int(os.environ['I7_PROCESS_READY_FD']);"
                "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                "os.write(ready_fd,b'GRANDCHILD_READY\\n');"
                "os.close(ready_fd);time.sleep(60)"
            )
            child = (
                "import os,signal,subprocess,sys,time;"
                "ready_fd=int(os.environ['I7_PROCESS_READY_FD']);"
                "signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                "os.write(ready_fd,b'CHILD_READY\\n');"
                f"p=subprocess.Popen([sys.executable,'-c',{grandchild!r}],"
                "pass_fds=(ready_fd,));"
                "os.close(ready_fd);"
                f"open({str(pidfile)!r},'w').write(str(os.getpid())+' '+str(p.pid));"
                "time.sleep(60)"
            )
            result = harness._run_process_group(
                [sys.executable, "-c", child], cwd=root,
                environment={"PATH": os.environ.get("PATH", "")},
                timeout_seconds=0.3, term_grace_seconds=0.2,
                kill_grace_seconds=2.0,
                readiness_tokens=(
                    b"CHILD_READY\n", b"GRANDCHILD_READY\n",
                ),
                readiness_timeout_seconds=5.0,
            )
            self.assertTrue(result.timed_out)
            self.assertTrue(result.term_sent)
            self.assertTrue(result.kill_sent)
            self.assertTrue(result.group_reaped)
            pids = [int(value) for value in pidfile.read_text().split()]
            time.sleep(0.05)
            for pid in pids:
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def _case_30_repository_diff_counts_byte_metadata_membership_and_attestation_binding(self) -> None:
        semantics = {"git_status_nul_sha256": HEX64, "git_config_nul_sha256": HEX64, "member_count": 1, "members_sha256": HEX64}
        before = {"semantics": semantics, "records": [{"path": "u", "sha256": HEX64, "mode": 0o644}]}
        after_bytes = {"semantics": semantics, "records": [{"path": "u", "sha256": "b" * 64, "mode": 0o644}]}
        after_meta = {"semantics": semantics, "records": [{"path": "u", "sha256": HEX64, "mode": 0o600}]}
        self.assertEqual(harness.compare_repository_manifests(before, after_bytes), (1, ("u",)))
        self.assertEqual(harness.compare_repository_manifests(before, after_meta), (1, ("u",)))
        base = {"gate": "g", "artifacts": {"stdout": HEX64}, "repository_output_count": 0}
        binding = hashlib.sha256(harness._canonical(base)).hexdigest()
        changed = {**base, "repository_output_count": 1}
        self.assertNotEqual(binding, hashlib.sha256(harness._canonical(changed)).hexdigest())

    def _case_31_authentic_result_channel_rejects_fake_output_and_replay(self) -> None:
        fake_outputs = (
            b"Ran 12 tests in 0.001s\n",
            b"foreign text\nRan 12 tests in 0.001s\n",
            b"Ran 12 tests in 0.001s\nOK\nRan 12 tests in 0.001s\nOK\n",
            b"OK\n",
        )
        for payload in fake_outputs:
            with self.subTest(payload=payload):
                self.assertEqual(harness._parse_gate_count("unittest", payload, b""), -1)
        expected = {
            "artifact_type": "IU4_I7_AUTHENTIC_UNITTEST_RESULT",
            "schema_version": 3, "gate_id": "preparation_components",
            "run_id": "IU4-I7-GATE-" + "A" * 64, "nonce": "a" * 64,
            "child_pid": 1234,
            "runner_sha256": harness.UNITTEST_SUPERVISOR_SHA256,
            "start_modules": ["tests.live_l1.test_i7_file_exact_preparation"],
            "expected_count": 12, "tests_run": 12, "failures": 0,
            "errors": 0, "skipped": 0, "unexpected_successes": 0,
            "expected_failures": 0, "result": "PASS",
        }
        for label, mutation in (
            ("valid", {}), ("nonce", {"nonce": "b" * 64}),
            ("pid", {"child_pid": 999}), ("gate", {"gate_id": "other"}),
            ("count", {"tests_run": 0}), ("skip", {"skipped": 1}),
        ):
            value = {**expected, **mutation}
            payload = json.dumps(
                value, sort_keys=True, separators=(",", ":")
            ).encode("ascii") + b"\n"
            arguments = {
                "gate_id": "preparation_components",
                "run_id": expected["run_id"], "nonce": expected["nonce"],
                "child_pid": 1234, "start_modules": expected["start_modules"],
                "expected_count": 12,
            }
            if label == "valid":
                observed = harness._read_authentic_unittest_result(
                    payload, **arguments,
                )
                self.assertEqual(observed["tests_run"], 12)
            else:
                with self.subTest(label=label), self.assertRaises(harness.I7HarnessError):
                    harness._read_authentic_unittest_result(payload, **arguments)

        valid = json.dumps(
            expected, sort_keys=True, separators=(",", ":")
        ).encode("ascii") + b"\n"
        adversarial = {
            "first-write-plus-rewrite": b"foreign\n" + valid,
            "duplicate-writes": valid + valid,
            "partial-writer": valid[: len(valid) // 2],
            "foreign-prefix": b"foreign" + valid,
            "result-replay": valid.replace(b'"nonce":"' + b"a" * 64, b'"nonce":"' + b"b" * 64),
            "duplicate-json-key": valid.replace(
                b'"errors":0,', b'"errors":0,"errors":0,', 1
            ),
            "no-terminal-lf": valid[:-1],
            "extra-terminal-lf": valid + b"\n",
            "oversized": b"{" + b" " * 65536 + b"}\n",
        }
        for label, payload in adversarial.items():
            with self.subTest(label=label), self.assertRaises(harness.I7HarnessError):
                harness._read_authentic_unittest_result(
                    payload, gate_id="preparation_components",
                    run_id=expected["run_id"], nonce=expected["nonce"],
                    child_pid=1234, start_modules=expected["start_modules"],
                    expected_count=12,
                )
        reader, writer = os.pipe2(os.O_CLOEXEC)
        duplicate = os.dup(writer)
        try:
            for operation in (
                lambda: os.lseek(writer, 0, os.SEEK_SET),
                lambda: os.ftruncate(writer, 0),
            ):
                with self.assertRaises(OSError):
                    operation()
            os.write(writer, valid)
            os.write(duplicate, valid)
            os.close(writer); writer = -1
            os.close(duplicate); duplicate = -1
            payload = harness._read_terminal_result_pipe(reader)
            with self.assertRaises(harness.I7HarnessError):
                harness._read_authentic_unittest_result(
                    payload, gate_id="preparation_components",
                    run_id=expected["run_id"], nonce=expected["nonce"],
                    child_pid=1234, start_modules=expected["start_modules"],
                    expected_count=12,
                )
        finally:
            if writer >= 0:
                os.close(writer)
            if duplicate >= 0:
                os.close(duplicate)
            os.close(reader)
        self.assertIn("close_fds=True", harness.UNITTEST_SUPERVISOR_RUNNER)
        self.assertNotIn("json.loads(worker.stdout", harness.UNITTEST_SUPERVISOR_RUNNER)
        self.assertNotIn("I7_RESULT_FD", harness.UNITTEST_WORKER_RUNNER)
        self.assertIn(
            "final result writer leaked into unittest worker",
            harness.UNITTEST_WORKER_RUNNER,
        )
        attacks = {
            "fake-json-os-exit-zero": (
                "import os\nprint('{\"tests_run\":1}')\nos._exit(0)\n"
            ),
            "system-exit-zero": "raise SystemExit(0)\n",
            "system-exit-pass-code": "raise SystemExit(73)\n",
            "stdout-stderr-spoof": (
                "import sys\nprint('{\"result\":\"PASS\"}')\n"
                "sys.stderr.write('Ran 1 test\\nOK\\n')\n"
            ),
            "rc-zero-without-tests": "VALUE=1\n",
            "duplicate-json": (
                "import os\nprint('{\"a\":1,\"a\":1}')\nos._exit(0)\n"
            ),
            "fd-and-environment-attack": (
                "import os\n"
                "[os.environ.pop(k,None) for k in list(os.environ) "
                "if k.startswith('I7_')]\n"
                "for fd in range(3,256):\n"
                " try: os.write(fd,b'{\\\"result\\\":\\\"PASS\\\"}\\n')\n"
                " except OSError: pass\n"
                "os._exit(0)\n"
            ),
            "monkeypatch-runner": (
                "import os,unittest\n"
                "unittest.TextTestRunner.run=lambda *a,**k: object()\n"
                "os._exit(0)\n"
            ),
        }
        for label, source in attacks.items():
            with self.subTest(supervisor_attack=label), tempfile.TemporaryDirectory(
                dir="/tmp"
            ) as name:
                root = Path(name)
                module = f"attack_{label.replace('-', '_')}"
                _write(root / f"{module}.py", source.encode("ascii"))
                reader, writer = os.pipe2(os.O_CLOEXEC)
                environment = {
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONPATH": os.pathsep.join((str(root), str(PROJECT_ROOT))),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONPYCACHEPREFIX": str(root / "pycache"),
                    "TMPDIR": name, "HOME": name, "LC_ALL": "C.UTF-8",
                    "I7_RESULT_FD": str(writer),
                    "I7_RESULT_GATE_ID": "adversarial",
                    "I7_RESULT_RUN_ID": "IU4-I7-GATE-" + "A" * 64,
                    "I7_RESULT_NONCE": "a" * 64,
                    "I7_RESULT_RUNNER_SHA256": harness.UNITTEST_SUPERVISOR_SHA256,
                    "I7_RESULT_START_MODULES": json.dumps([module]),
                    "I7_RESULT_EXPECTED_COUNT": "1",
                }
                try:
                    observed = harness._run_process_group(
                        [sys.executable, "-c", harness.UNITTEST_SUPERVISOR_RUNNER],
                        cwd=root, environment=environment, timeout_seconds=5,
                        pass_fds=(writer,),
                    )
                finally:
                    os.close(writer)
                try:
                    terminal = harness._read_terminal_result_pipe(reader)
                finally:
                    os.close(reader)
                self.assertNotEqual(observed.return_code, 0)
                self.assertEqual(terminal, b"")
                self.assertTrue(observed.group_reaped)

    def _case_32_git_ignore_semantics_closure_topology_and_dual_roots(self) -> None:
        normal = harness._git_bytes(("status", "--porcelain=v1", "-z", "--untracked-files=all"))
        git_binding = harness._bound_git_environment()
        with tempfile.TemporaryDirectory(dir="/tmp") as name:
            with mock.patch.dict(os.environ, {"HOME": name}, clear=False):
                os.environ.pop("XDG_CONFIG_HOME", None)
                os.environ.pop("GIT_CONFIG_GLOBAL", None)
                unbound = harness._git_bytes((
                    "status", "--porcelain=v1", "-z", "--untracked-files=all",
                ))
            with mock.patch.dict(
                os.environ, {"HOME": name, **git_binding}, clear=False,
            ):
                isolated = harness._git_bytes(("status", "--porcelain=v1", "-z", "--untracked-files=all"))
                semantics = harness._effective_git_semantics()
        home_scoped_entry = b"?? .claude/settings.local.json\0"
        normal_records = [x for x in normal.split(b"\0") if x]
        isolated_records = [x for x in isolated.split(b"\0") if x]
        unbound_records = [x for x in unbound.split(b"\0") if x]
        self.assertEqual(normal, isolated)
        self.assertNotIn(home_scoped_entry, normal)
        self.assertNotIn(home_scoped_entry, isolated)
        self.assertEqual(unbound.count(home_scoped_entry), 1)
        self.assertEqual(
            unbound.replace(home_scoped_entry, b"", 1),
            normal,
        )
        self.assertEqual(len(unbound_records), len(normal_records) + 1)
        self.assertEqual(len(unbound_records), len(isolated_records) + 1)
        self.assertTrue(semantics["ignore_files"])
        self.assertEqual(
            {item["role"] for item in semantics["config_sources"]},
            {"system-config", "global-config", "xdg-global-config", "local-config"},
        )
        plan = harness.plan_gate("preparation_components")
        closure = plan["closure"]
        self.assertEqual(closure["topology_edge_count"], len(closure["edges"]))
        self.assertEqual(closure["forbidden_edge_count"], len(closure["forbidden_edges"]))
        self.assertEqual(closure["dynamic_import_count"], len(closure["dynamic_imports"]))
        self.assertEqual(closure["unresolved_local_import_count"], len(closure["unresolved_local_imports"]))
        self.assertEqual(closure["effect_edge_count"], len(closure["effect_edges"]))
        replay_closure = harness.plan_gate("staged_synthetic_replay")["closure"]
        self.assertEqual(
            (closure["file_count"], closure["edge_count"],
             closure["syntactic_edge_count"], closure["implicit_initializer_edge_count"]),
            (6, 7, 3, 4),
        )
        self.assertEqual(
            (replay_closure["file_count"], replay_closure["edge_count"],
             replay_closure["syntactic_edge_count"], replay_closure["implicit_initializer_edge_count"]),
            (2, 1, 0, 1),
        )
        evidence_text = (
            PROJECT_ROOT / "docs/review/PRE_IU4_I7_PREPARATION_RESOLUTION_FILE_EXACT_2026-08-23.md"
        ).read_text(encoding="utf-8")
        for label, expected_closure in (
            ("PREPARATION", closure), ("REPLAY", replay_closure),
        ):
            begin = f"<!-- BEGIN_{label}_CLOSURE_RECORD_JSON -->\n"
            end = f"\n<!-- END_{label}_CLOSURE_RECORD_JSON -->"
            payload = evidence_text.split(begin, 1)[1].split(end, 1)[0]
            reconstructed = json.loads(payload)
            self.assertEqual(
                reconstructed,
                harness._semantic_closure_record(expected_closure),
            )

        semantic_closure = harness._semantic_closure_record(closure)
        raw_repository = {
            "semantics": {
                "git_status_nul_sha256": HEX64,
                "git_config_raw_nul_sha256": "b" * 64,
                "member_count": 1, "members_sha256": "c" * 64,
                "git_semantics": {
                    "canonical_config": [["core.filemode", "true"]],
                    "canonical_config_sha256": "f" * 64,
                    "config_sources": [{
                        "role": "global-config", "present": True,
                        "path": "/host/global", "sha256": "a" * 64,
                        "size": 4, "mode": 0o644, "uid": 1, "gid": 1,
                        "device": 1, "inode": 1, "mtime_ns": 1,
                        "ctime_ns": 1,
                    }],
                    "ignore_files": [{
                        "role": "implicit-xdg-global-ignore", "present": True,
                        "path": "/host/a", "sha256": "d" * 64, "size": 4,
                        "mode": 0o644, "uid": 1, "gid": 1, "device": 1,
                        "inode": 1, "mtime_ns": 1, "ctime_ns": 1,
                    }],
                },
            },
            "records": [{
                "path": "logical.py", "mode": stat.S_IFREG | 0o644,
                "uid": 1, "gid": 1, "device": 1, "inode": 1,
                "size": 4, "nlink": 1, "atime_ns": 1, "mtime_ns": 1,
                "ctime_ns": 1, "symlink_target": None, "sha256": "e" * 64,
            }],
        }
        metadata_variant = json.loads(json.dumps(raw_repository))
        metadata_variant["semantics"]["git_semantics"]["ignore_files"][0].update({
            "path": "/other/host", "device": 99, "inode": 99,
            "mtime_ns": 99, "ctime_ns": 99,
        })
        metadata_variant["semantics"]["git_semantics"]["config_sources"][0].update({
            "path": "/other/config-origin", "uid": 99, "gid": 99,
            "device": 99, "inode": 99, "mtime_ns": 99, "ctime_ns": 99,
        })
        metadata_variant["records"][0].update({
            "uid": 99, "gid": 99, "device": 99, "inode": 99,
            "atime_ns": 99, "mtime_ns": 99, "ctime_ns": 99,
        })
        repository_a = harness._semantic_repository_record(raw_repository)
        repository_b = harness._semantic_repository_record(metadata_variant)
        self.assertEqual(repository_a, repository_b)
        evidence_record = json.loads(json.dumps(raw_repository))
        evidence_record["records"][0]["path"] = harness.EVIDENCE_RELATIVE_PATH
        evidence_variant = json.loads(json.dumps(evidence_record))
        evidence_variant["records"][0].update({
            "sha256": "0" * 64, "size": 999999,
        })
        self.assertEqual(
            harness._semantic_repository_record(evidence_record),
            harness._semantic_repository_record(evidence_variant),
        )
        semantic = {
            "gate_id": "g", "count": 12, "closure": semantic_closure,
            "repository": repository_a, "result": "PASS",
        }
        root_a = harness._deterministic_semantic_root(semantic)
        root_b = harness._deterministic_semantic_root({
            **semantic, "repository": repository_b,
        })
        self.assertEqual(root_a, root_b)
        semantic_text = harness._canonical(semantic).decode("ascii")
        for forbidden in ("/tmp", "/home/", '"uid"', '"gid"', '"device"', '"inode"'):
            self.assertNotIn(forbidden, semantic_text)
        raw_manifest = harness.load_manifest()
        host_variant = json.loads(json.dumps(raw_manifest))
        host_variant["canonical_repository"] = "/different/checkout"
        host_variant["workstation_contract_schema"].update({
            "uid": 77, "gid": 88,
        })
        canonical_manifest = harness._semantic_gate_manifest(raw_manifest)
        self.assertEqual(
            canonical_manifest,
            harness._semantic_gate_manifest(host_variant),
        )
        self.assertNotIn(
            "/home/", harness._canonical(canonical_manifest).decode("ascii")
        )
        run_a = harness._run_attestation_root({
            "semantic": root_a, "nonce": "a", "run_root": "/tmp/a",
            "device": 1, "inode": 1, "raw": HEX64,
        })
        run_b = harness._run_attestation_root({
            "semantic": root_b, "nonce": "b", "run_root": "/tmp/b",
            "device": 2, "inode": 2, "raw": HEX64,
        })
        self.assertNotEqual(run_a, run_b)
        tampered_semantic = {**semantic, "count": 11}
        tampered_semantic_root = harness._deterministic_semantic_root(
            tampered_semantic
        )
        self.assertNotEqual(root_a, tampered_semantic_root)
        self.assertNotEqual(
            run_a,
            harness._run_attestation_root({
                "semantic": tampered_semantic_root, "nonce": "a",
                "run_root": "/tmp/a", "device": 1, "inode": 1,
                "raw": HEX64,
            }),
        )
        tampered_closure = json.loads(json.dumps(semantic))
        tampered_closure["closure"]["edges"] = []
        self.assertNotEqual(root_a, harness._deterministic_semantic_root(tampered_closure))
        count_tamper = json.loads(json.dumps(closure))
        count_tamper["edge_count"] += 1
        with self.assertRaises(harness.I7HarnessError):
            harness._semantic_closure_record(count_tamper)
        preservation_tamper = json.loads(json.dumps(semantic))
        preservation_tamper["repository"]["records"][0]["sha256"] = "0" * 64
        self.assertNotEqual(
            root_a, harness._deterministic_semantic_root(preservation_tamper)
        )
        ignore_tamper = json.loads(json.dumps(semantic))
        ignore_tamper["repository"]["ignore_files"][0]["sha256"] = "0" * 64
        self.assertNotEqual(
            root_a, harness._deterministic_semantic_root(ignore_tamper)
        )
        gate_tamper = json.loads(json.dumps(canonical_manifest))
        gate_tamper["evidence_contract"]["process_group_per_gate"] = False
        self.assertNotEqual(
            harness._deterministic_semantic_root({"manifest": canonical_manifest}),
            harness._deterministic_semantic_root({"manifest": gate_tamper}),
        )
        self.assertNotEqual(
            run_a,
            harness._run_attestation_root({
                "semantic": root_a, "nonce": "a", "run_root": "/tmp/a",
                "device": 1, "inode": 1, "raw": "b" * 64,
            }),
        )

    def test_12_timeout_group_reap_preservation_diff_and_attestation(self) -> None:
        self._case_29_timeout_terms_kills_and_reaps_child_grandchild_group()
        self._case_30_repository_diff_counts_byte_metadata_membership_and_attestation_binding()
        self._case_31_authentic_result_channel_rejects_fake_output_and_replay()
        self._case_32_git_ignore_semantics_closure_topology_and_dual_roots()


if __name__ == "__main__":
    unittest.main()
