#!/usr/bin/env python3
# live_l1/state/state_store.py
# L1 state store with minimal JSONL resume loading for L1-D recovery.
# ASCII-only.

from __future__ import annotations

import errno
import json
import os
import stat
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

from live_l1.state.models import PositionStateS2, RiskStateS4
from live_l1.state.persist import _atomic_append_jsonl


S2Position = PositionStateS2
S4Risk = RiskStateS4


@dataclass
class L1State:
    system_state_id: str
    is_running: bool
    s2_position: S2Position
    s4_risk: S4Risk
    last_snapshot_id: str
    last_timestamp_utc: str
    last_tick_id: int


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        return int(float(s))
    except Exception:
        return default


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _read_last_jsonl_record(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        return {}

    last_good: Dict[str, Any] = {}

    with open(path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                last_good = obj

    return last_good


def _build_default_position() -> S2Position:
    s2 = S2Position(
        symbol="BTCUSDT",
        position="FLAT",
        size=0.0,
        entry_price=None,
    )
    setattr(s2, "entry_timestamp_utc", "")
    setattr(s2, "position_size", 0.0)
    setattr(s2, "last_intent_id", "")
    setattr(s2, "snapshot_id", "")
    setattr(s2, "side", "")
    return s2


def _build_default_risk() -> S4Risk:
    s4 = S4Risk(
        kill_level="NONE",
        cooldown_until_utc=None,
    )
    setattr(s4, "trades_6h", 0)
    setattr(s4, "trades_today", 0)
    setattr(s4, "last_trade_timestamp_utc", "")
    return s4


def load_or_init_state(state_dir: str, system_state_id: str) -> L1State:
    os.makedirs(state_dir, exist_ok=True)

    s2_path = os.path.join(state_dir, "s2_position.jsonl")
    s4_path = os.path.join(state_dir, "s4_risk.jsonl")

    s2_last = _read_last_jsonl_record(s2_path)
    s4_last = _read_last_jsonl_record(s4_path)

    s2 = _build_default_position()
    s4 = _build_default_risk()

    loaded_system_state_id = system_state_id

    if s2_last:
        loaded_system_state_id = _safe_text(s2_last.get("system_state_id"), loaded_system_state_id)

        s2.symbol = _safe_text(s2_last.get("symbol"), "BTCUSDT")
        s2.position = _safe_text(s2_last.get("position"), "FLAT").upper()
        s2.size = float(_safe_float(s2_last.get("size"), 0.0) or 0.0)
        s2.entry_price = _safe_float(s2_last.get("entry_price"), None)

        setattr(s2, "entry_timestamp_utc", _safe_text(s2_last.get("entry_timestamp_utc"), ""))
        setattr(s2, "position_size", float(_safe_float(s2_last.get("position_size"), s2.size) or 0.0))
        setattr(s2, "last_intent_id", _safe_text(s2_last.get("last_intent_id"), ""))
        setattr(s2, "snapshot_id", _safe_text(s2_last.get("snapshot_id"), ""))

        loaded_side = _safe_text(s2_last.get("side"), "")
        if loaded_side == "":
            if s2.position == "LONG":
                loaded_side = "long"
            elif s2.position == "SHORT":
                loaded_side = "short"
        setattr(s2, "side", loaded_side)

    if s4_last:
        loaded_system_state_id = _safe_text(s4_last.get("system_state_id"), loaded_system_state_id)

        s4.kill_level = _safe_text(s4_last.get("kill_level"), "NONE").upper()
        s4.cooldown_until_utc = s4_last.get("cooldown_until_utc", None)

        setattr(s4, "trades_6h", _safe_int(s4_last.get("trades_6h"), 0))
        setattr(s4, "trades_today", _safe_int(s4_last.get("trades_today"), 0))
        setattr(s4, "last_trade_timestamp_utc", _safe_text(s4_last.get("last_trade_timestamp_utc"), ""))

    last_snapshot_id = ""
    last_timestamp_utc = ""
    last_tick_id = 0

    if s2_last:
        last_snapshot_id = _safe_text(s2_last.get("last_snapshot_id"), _safe_text(s2_last.get("snapshot_id"), ""))
        last_timestamp_utc = _safe_text(s2_last.get("last_timestamp_utc"), "")
        last_tick_id = _safe_int(s2_last.get("last_tick_id"), 0)

    return L1State(
        system_state_id=loaded_system_state_id,
        is_running=True,
        s2_position=s2,
        s4_risk=s4,
        last_snapshot_id=last_snapshot_id,
        last_timestamp_utc=last_timestamp_utc,
        last_tick_id=last_tick_id,
    )


def persist_state(state_dir: str, state: L1State) -> None:
    os.makedirs(state_dir, exist_ok=True)

    s2_path = os.path.join(state_dir, "s2_position.jsonl")
    s4_path = os.path.join(state_dir, "s4_risk.jsonl")

    s2_position_size = _safe_float(getattr(state.s2_position, "position_size", getattr(state.s2_position, "size", 0.0)), 0.0)
    s2_entry_timestamp_utc = _safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), "")
    s2_last_intent_id = _safe_text(getattr(state.s2_position, "last_intent_id", ""), "")
    s2_snapshot_id = _safe_text(getattr(state.s2_position, "snapshot_id", ""), "")
    s2_side = _safe_text(getattr(state.s2_position, "side", ""), "")

    s4_trades_6h = _safe_int(getattr(state.s4_risk, "trades_6h", 0), 0)
    s4_trades_today = _safe_int(getattr(state.s4_risk, "trades_today", 0), 0)
    s4_last_trade_timestamp_utc = _safe_text(getattr(state.s4_risk, "last_trade_timestamp_utc", ""), "")

    _atomic_append_jsonl(
        s2_path,
        {
            "schema_version": 1,
            "system_state_id": state.system_state_id,
            "symbol": state.s2_position.symbol,
            "position": state.s2_position.position,
            "side": s2_side,
            "size": state.s2_position.size,
            "entry_price": state.s2_position.entry_price,
            "entry_timestamp_utc": s2_entry_timestamp_utc,
            "position_size": s2_position_size,
            "last_intent_id": s2_last_intent_id,
            "snapshot_id": s2_snapshot_id,
            "last_snapshot_id": _safe_text(state.last_snapshot_id, ""),
            "last_timestamp_utc": _safe_text(state.last_timestamp_utc, ""),
            "last_tick_id": _safe_int(state.last_tick_id, 0),
        },
    )

    _atomic_append_jsonl(
        s4_path,
        {
            "schema_version": 1,
            "system_state_id": state.system_state_id,
            "kill_level": state.s4_risk.kill_level,
            "cooldown_until_utc": state.s4_risk.cooldown_until_utc,
            "trades_6h": s4_trades_6h,
            "trades_today": s4_trades_today,
            "last_trade_timestamp_utc": s4_last_trade_timestamp_utc,
        },
    )


def _canonical_projection_bytes(record: Dict[str, Any]) -> bytes:
    if type(record) is not dict:
        raise ValueError("Legacy safety projection must be an exact dict")
    try:
        return json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii") + b"\n"
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError("Legacy safety projection is not canonical JSON") from exc


@dataclass(frozen=True)
class _LegacyProjectionBoundary:
    """Held descriptor chain for one absolute compatibility artifact address."""

    directory_fd: int
    basename: str
    candidate: str
    descriptors: tuple[int, ...]
    edges: tuple[tuple[int, str, int, int], ...]

    def revalidate(self) -> None:
        for parent_fd, name, expected_device, expected_inode in self.edges:
            try:
                linked = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except OSError as exc:
                raise ValueError(
                    "Legacy safety projection parent identity changed"
                ) from exc
            if (
                not stat.S_ISDIR(linked.st_mode)
                or (linked.st_dev, linked.st_ino)
                != (expected_device, expected_inode)
            ):
                raise ValueError(
                    "Legacy safety projection parent identity changed"
                )

    def close(self, *, primary_active: bool = False) -> None:
        _cleanup_projection_descriptors(
            reversed(self.descriptors),
            primary_active=primary_active,
            message="Legacy safety projection boundary cleanup failed",
        )


def _cleanup_projection_descriptors(
    descriptors: Any, *, primary_active: bool, message: str
) -> None:
    """Attempt every close and never replace an already active primary error."""

    first_error: BaseException | None = None
    for descriptor in descriptors:
        try:
            os.close(descriptor)
        except BaseException as exc:
            if first_error is None:
                first_error = exc
    if first_error is not None and not primary_active:
        raise ValueError(message) from first_error


def _close_projection_descriptor(
    descriptor: int, *, primary_active: bool, message: str
) -> None:
    _cleanup_projection_descriptors(
        (descriptor,), primary_active=primary_active, message=message
    )


def _open_projection_parent(
    path: str | os.PathLike[str], *, create: bool
) -> _LegacyProjectionBoundary:
    """Resolve an absolute projection parent without following symlinks."""

    candidate = os.fspath(path)
    if (
        type(candidate) is not str
        or not candidate.startswith("/")
        or candidate == "/"
        or candidate.endswith("/")
        or "\x00" in candidate
        or os.path.abspath(candidate) != candidate
    ):
        raise ValueError("Legacy safety projection path must be canonical absolute")
    components = candidate.split("/")[1:]
    if not components or any(component in {"", ".", ".."} for component in components):
        raise ValueError("Legacy safety projection path is unsafe")
    directory = os.open(
        "/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW
    )
    descriptors = [directory]
    edges: list[tuple[int, str, int, int]] = []
    try:
        for component in components[:-1]:
            try:
                child = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=directory,
                )
            except FileNotFoundError:
                if not create:
                    raise ValueError(
                        "Legacy safety projection parent does not exist"
                    )
                os.mkdir(component, 0o700, dir_fd=directory)
                child = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=directory,
                )
            except OSError as exc:
                if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                    raise ValueError(
                        "Legacy safety projection parent is unsafe"
                    ) from exc
                raise
            info = os.fstat(child)
            if not stat.S_ISDIR(info.st_mode):
                _close_projection_descriptor(
                    child,
                    primary_active=True,
                    message="Legacy safety projection parent cleanup failed",
                )
                raise ValueError("Legacy safety projection parent is unsafe")
            edges.append((directory, component, info.st_dev, info.st_ino))
            descriptors.append(child)
            directory = child
        boundary = _LegacyProjectionBoundary(
            directory_fd=directory,
            basename=components[-1],
            candidate=candidate,
            descriptors=tuple(descriptors),
            edges=tuple(edges),
        )
        boundary.revalidate()
        return boundary
    except BaseException:
        _cleanup_projection_descriptors(
            reversed(descriptors),
            primary_active=True,
            message="Legacy safety projection parent cleanup failed",
        )
        raise


def _projection_target_identity(
    info: os.stat_result,
) -> tuple[int, int, int, int]:
    return (
        info.st_dev,
        info.st_ino,
        stat.S_IFMT(info.st_mode),
        info.st_size,
    )


def _stat_projection_target(
    directory: int,
    basename: str,
) -> tuple[int, int, int, int]:
    try:
        info = os.stat(basename, dir_fd=directory, follow_symlinks=False)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("Legacy safety projection target is unsafe") from exc
        raise
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Legacy safety projection must be a regular file")
    return _projection_target_identity(info)


def _verify_projection_target(
    directory: int,
    basename: str,
    expected_identity: tuple[int, int, int, int],
) -> None:
    if _stat_projection_target(directory, basename) != expected_identity:
        raise ValueError("Legacy safety projection target identity changed")


def _read_projection_bytes(
    directory: int,
    basename: str,
    *,
    expected_identity: tuple[int, int, int, int] | None = None,
) -> tuple[bytes, tuple[int, int, int, int]]:
    linked_before = _stat_projection_target(directory, basename)
    if expected_identity is not None and linked_before != expected_identity:
        raise ValueError("Legacy safety projection target identity changed")
    try:
        descriptor = os.open(
            basename,
            os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
            dir_fd=directory,
        )
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("Legacy safety projection target is unsafe") from exc
        raise
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("Legacy safety projection must be a regular file")
        before_identity = _projection_target_identity(before)
        if before_identity != linked_before:
            raise ValueError("Legacy safety projection target identity changed")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                raw = b"".join(chunks)
                after = os.fstat(descriptor)
                after_identity = _projection_target_identity(after)
                if (
                    before_identity != after_identity
                    or len(raw) != after.st_size
                ):
                    raise ValueError(
                        "Legacy safety projection changed during readback"
                    )
                _verify_projection_target(
                    directory, basename, after_identity
                )
                return raw, after_identity
            chunks.append(chunk)
    finally:
        _close_projection_descriptor(
            descriptor,
            primary_active=sys.exc_info()[0] is not None,
            message="Legacy safety projection read cleanup failed",
        )


def read_legacy_safety_projection(path: str | os.PathLike[str]) -> Dict[str, Any]:
    """Read an explicit non-authoritative I6 compatibility projection.

    This helper never participates in ``load_or_init_state`` and therefore
    cannot become a Legacy or ENFORCED recovery authority.
    """

    boundary = _open_projection_parent(path, create=False)
    try:
        boundary.revalidate()
        raw, target_identity = _read_projection_bytes(
            boundary.directory_fd, boundary.basename
        )
        boundary.revalidate()
        _verify_projection_target(
            boundary.directory_fd, boundary.basename, target_identity
        )
    except OSError as exc:
        raise ValueError("Legacy safety projection is unreadable") from exc
    finally:
        boundary.close(primary_active=sys.exc_info()[0] is not None)
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Legacy safety projection is unreadable") from exc
    if type(value) is not dict or raw != _canonical_projection_bytes(value):
        raise ValueError("Legacy safety projection bytes are not canonical")
    return value


def write_legacy_safety_projection(
    path: str | os.PathLike[str],
    record: Dict[str, Any],
) -> None:
    """Durably create an I6 projection, or accept an identical replay."""

    data = _canonical_projection_bytes(record)
    boundary = _open_projection_parent(path, create=True)
    try:
        boundary.revalidate()
        try:
            existing, target_identity = _read_projection_bytes(
                boundary.directory_fd, boundary.basename
            )
        except FileNotFoundError:
            descriptor = os.open(
                boundary.basename,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW,
                0o600,
                dir_fd=boundary.directory_fd,
            )
            try:
                created_before = os.fstat(descriptor)
                if not stat.S_ISREG(created_before.st_mode):
                    raise ValueError("Legacy safety projection target is unsafe")
                created_before_identity = _projection_target_identity(
                    created_before
                )
                _verify_projection_target(
                    boundary.directory_fd,
                    boundary.basename,
                    created_before_identity,
                )
                offset = 0
                while offset < len(data):
                    written = os.write(descriptor, data[offset:])
                    if written <= 0:
                        raise OSError("short projection write")
                    offset += written
                os.fsync(descriptor)
                created_after = os.fstat(descriptor)
                if (
                    _projection_target_identity(created_after)[:3]
                    != created_before_identity[:3]
                    or created_after.st_size != len(data)
                ):
                    raise ValueError(
                        "Legacy safety projection changed during publication"
                    )
                target_identity = _projection_target_identity(created_after)
                _verify_projection_target(
                    boundary.directory_fd,
                    boundary.basename,
                    target_identity,
                )
            finally:
                _close_projection_descriptor(
                    descriptor,
                    primary_active=sys.exc_info()[0] is not None,
                    message="Legacy safety projection write cleanup failed",
                )
        else:
            if existing != data:
                raise ValueError("Legacy safety projection replay conflicts")
            boundary.revalidate()
            _verify_projection_target(
                boundary.directory_fd,
                boundary.basename,
                target_identity,
            )
            return
        os.fsync(boundary.directory_fd)
        boundary.revalidate()
        _verify_projection_target(
            boundary.directory_fd,
            boundary.basename,
            target_identity,
        )
        readback, readback_identity = _read_projection_bytes(
            boundary.directory_fd,
            boundary.basename,
            expected_identity=target_identity,
        )
        boundary.revalidate()
        _verify_projection_target(
            boundary.directory_fd,
            boundary.basename,
            target_identity,
        )
        if readback_identity != target_identity or readback != data:
            raise ValueError("Legacy safety projection readback mismatch")
        try:
            observed = json.loads(readback.decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("Legacy safety projection readback mismatch") from exc
        if type(observed) is not dict or observed != record:
            raise ValueError("Legacy safety projection readback mismatch")
    finally:
        boundary.close(primary_active=sys.exc_info()[0] is not None)
