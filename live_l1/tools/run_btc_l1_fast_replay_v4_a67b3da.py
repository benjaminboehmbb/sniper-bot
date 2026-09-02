#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import sys
import time


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--seed-rel", required=True)
    p.add_argument("--max-ticks", type=int, required=True)
    p.add_argument("--semantic-out", required=True)
    args = p.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    os.chdir(repo)
    sys.path.insert(0, str(repo))

    os.environ.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "TZ": "UTC",

            "L1_OPERATIONAL_PROFILE": "PAPER",
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",

            "L1_IU4_MODE": "OFF",
            "L1_IU4_SHADOW_OBSERVATION_ENABLED": "0",
            "PEE_MODE": "OFF",

            "L1_MARKET_CSV_PATH": args.data,
            "SEEDS_5M_CSV": args.seed_rel,

            "L1_SYMBOL": "BTCUSDT",
            "L1_GATE_MODE": "auto",
            "L1_FEE_ROUNDTRIP": "0.0004",
            "L1_DECISION_TICK_SECONDS": "0",
            "THRESH_5M": "0.60",

            "L1_TIMING_V2_SHADOW": "0",
            "L1_TIMING_V2_HISTORY_LEN": "3",
            "L1_TEST_FORCE_INTENTS": "0",

            "L1_TP_PCT": "0.05",
            "L1_SL_PCT": "0.015",
            "L1_LONG_TIME_STOP_SEC": "3600",
            "L1_SHORT_TIME_STOP_SEC": "3600",
        }
    )

    import live_l1.core.loop as loop

    from live_l1.logs.logger import (
        _ALLOWED_SEVERITY,
        _kv_escape,
    )

    from live_l1.state.state_store import (
        persist_state as canonical_persist_state,
    )

    # Critical V4 rule:
    # DO NOT PATCH compute_5m_timing_vote.
    original_timing = loop.compute_5m_timing_vote

    semantic_fh = open(
        args.semantic_out,
        "w",
        encoding="utf-8",
        buffering=1024 * 1024,
    )

    semantic_digest = hashlib.sha256()

    stats = {
        "events": 0,
        "persist_calls": 0,
        "logger_emitted": 0,
        "logger_suppressed": 0,
    }

    latest = {
        "state": None,
        "state_dir": None,
    }

    original_persist = loop.persist_state

    class FastReplayLoggerV4:
        def __init__(self, log_path: str):
            self.log_path = log_path

            os.makedirs(
                os.path.dirname(log_path),
                exist_ok=True,
            )

            self._fh = open(
                log_path,
                "a",
                encoding="utf-8",
                buffering=1,
            )

        def close(self):
            if self._fh is not None:
                self._fh.flush()
                self._fh.close()
                self._fh = None

        def log(
            self,
            *,
            category,
            event,
            severity,
            system_state_id,
            intent_id=None,
            fields=None,
        ):
            sev = str(severity).upper().strip()

            if sev not in _ALLOWED_SEVERITY:
                sev = "INFO"

            # Exact semantic representation matching the Golden parser.
            # Exclude only process/run identity:
            # - logger wall-clock timestamp is never constructed here
            # - seq is not semantic
            # - system_state_id / intent_id are run-specific
            # - tick_started_utc is TickClock wall time
            parts = [
                "category=" + _kv_escape(category),
                "event=" + _kv_escape(event),
                "severity=" + sev,
            ]

            if fields:
                for key in sorted(fields):
                    if key == "tick_started_utc":
                        continue

                    parts.append(
                        _kv_escape(key)
                        + "="
                        + _kv_escape(fields[key])
                    )

            canonical = " ".join(parts) + "\n"

            semantic_fh.write(canonical)
            semantic_digest.update(
                canonical.encode("utf-8")
            )

            stats["events"] += 1

            ev = str(event).strip()

            # Physical logger retains only control/error events.
            keep = (
                ev in {
                    "system_start",
                    "system_stop",
                    "recovery_checked",
                }
                or sev in {
                    "WARN",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                }
            )

            if keep:
                stats["logger_emitted"] += 1
                self._fh.write(canonical)
            else:
                stats["logger_suppressed"] += 1

    def ram_persist(state_dir, state):
        latest["state"] = state
        latest["state_dir"] = state_dir
        stats["persist_calls"] += 1

    loop.L1Logger = FastReplayLoggerV4
    loop.persist_state = ram_persist

    # Fail closed if anyone accidentally changed the timing binding.
    if loop.compute_5m_timing_vote is not original_timing:
        print("FAIL: TIMING_FUNCTION_PATCHED")
        return 90

    import live_l1.tools.safe_launch as safe_launch

    old_argv = list(sys.argv)

    sys.argv = [
        "safe_launch.py",
        "--repo-root",
        str(repo),
        "--max-ticks",
        str(args.max_ticks),
        "--max-run-seconds",
        "0",
        "--market-csv-path",
        args.data,
        "--seeds-5m-csv",
        args.seed_rel,
        "--require-wsl",
        "1",
    ]

    start = time.monotonic()

    try:
        rc = safe_launch.main()

        if rc is None:
            rc = 0

        rc = int(rc)

    except SystemExit as exc:
        rc = int(exc.code or 0)

    finally:
        sys.argv = old_argv

    duration = time.monotonic() - start

    semantic_fh.flush()
    semantic_fh.close()

    if rc != 0:
        print(f"FAST_REPLAY_RUNTIME_RC={rc}")
        return rc

    if latest["state"] is None:
        print("FAIL: FINAL_STATE_NOT_CAPTURED")
        return 91

    if stats["persist_calls"] != args.max_ticks:
        print(
            "FAIL: PERSIST_CALL_COUNT "
            f"{stats['persist_calls']} != {args.max_ticks}"
        )
        return 92

    # Persist final S2/S4 through the untouched canonical serializer.
    canonical_persist_state(
        latest["state_dir"],
        latest["state"],
    )

    if loop.compute_5m_timing_vote is not original_timing:
        print("FAIL: TIMING_FUNCTION_CHANGED_DURING_RUN")
        return 93

    print(f"FAST_REPLAY_RUNTIME_RC={rc}")
    print(f"FAST_REPLAY_DURATION_SECONDS={duration:.6f}")
    print(f"SEMANTIC_EVENT_COUNT={stats['events']}")
    print(
        "SEMANTIC_EVENT_SHA256="
        + semantic_digest.hexdigest()
    )
    print(
        "CANONICAL_PERSIST_CALLS_SUPPRESSED="
        + str(stats["persist_calls"])
    )
    print("CANONICAL_FINAL_PERSIST_CALLS=1")
    print(
        "LOGGER_CALLS_EMITTED="
        + str(stats["logger_emitted"])
    )
    print(
        "LOGGER_CALLS_SUPPRESSED="
        + str(stats["logger_suppressed"])
    )
    print("TIMING_OPTIMIZATION=NONE")
    print("TIMING_FUNCTION_UNTOUCHED=PASS")
    print("FAST_REPLAY_V4_ENGINE=PASS")

    loop.persist_state = original_persist

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
