#!/usr/bin/env python3
# live_l1/core/regime_v2_builder.py
# Source of Truth:
# tools/build_regime_v2_from_v1.py

from __future__ import annotations

import numpy as np


DEFAULT_MIN_STATE_BARS = 720


def build_regime_v2(
    regime_v1,
    min_state_bars: int = DEFAULT_MIN_STATE_BARS,
    no_direct_flip: bool = False,
):
    v1 = np.asarray(regime_v1, dtype=float)

    if v1.size == 0:
        return np.array([], dtype=np.int8)

    vv = np.where(v1 > 0, 1, np.where(v1 < 0, -1, 0)).astype(np.int8)

    v2 = np.empty(vv.size, dtype=np.int8)

    current = int(vv[0])
    v2[0] = current

    cand = current
    cand_len = 0

    for i in range(1, vv.size):
        x = int(vv[i])

        if x == current:
            cand = current
            cand_len = 0
            v2[i] = current
            continue

        if x != cand:
            cand = x
            cand_len = 1
        else:
            cand_len += 1

        if cand_len >= min_state_bars:

            if (
                no_direct_flip
                and (
                    (current == 1 and cand == -1)
                    or (current == -1 and cand == 1)
                )
            ):
                cand = current
                cand_len = 0
                v2[i] = current
            else:
                current = cand
                cand_len = 0
                v2[i] = current
        else:
            v2[i] = current

    return v2
