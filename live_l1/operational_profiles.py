#!/usr/bin/env python3
# live_l1/operational_profiles.py
# P20B Operational profile configuration.
# ASCII-only.

from __future__ import annotations

import os


PROFILE_DEVELOPMENT = "DEVELOPMENT"
PROFILE_PAPER = "PAPER"
PROFILE_PRODUCTION = "PRODUCTION"
PROFILE_RECOVERY = "RECOVERY"


ALLOWED_PROFILES = {
    PROFILE_DEVELOPMENT,
    PROFILE_PAPER,
    PROFILE_PRODUCTION,
    PROFILE_RECOVERY,
}


PROFILE_CONFIGS = {
    PROFILE_DEVELOPMENT: {
        "startup_validation_required": False,
        "reconciliation_required": False,
        "monitoring_required": False,
        "recovery_required": False,
    },
    PROFILE_PAPER: {
        "startup_validation_required": True,
        "reconciliation_required": True,
        "monitoring_required": True,
        "recovery_required": False,
    },
    PROFILE_PRODUCTION: {
        "startup_validation_required": True,
        "reconciliation_required": True,
        "monitoring_required": True,
        "recovery_required": True,
    },
    PROFILE_RECOVERY: {
        "startup_validation_required": True,
        "reconciliation_required": True,
        "monitoring_required": True,
        "recovery_required": True,
    },
}


def get_operational_profile() -> str:
    profile = str(
        os.environ.get(
            "L1_OPERATIONAL_PROFILE",
            PROFILE_PAPER,
        )
    ).strip().upper()

    if profile not in ALLOWED_PROFILES:
        return PROFILE_PAPER

    return profile


def get_profile_config() -> dict:
    profile = get_operational_profile()
    return dict(PROFILE_CONFIGS[profile])


def profile_summary() -> dict:
    profile = get_operational_profile()

    return {
        "profile": profile,
        **PROFILE_CONFIGS[profile],
    }
