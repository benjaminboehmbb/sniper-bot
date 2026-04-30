from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import math


ALLOWED_REGIMES = {
    "UP_TREND",
    "DOWN_TREND",
    "SIDEWAYS",
    "CRISIS",
    "UNCLASSIFIED",
}


@dataclass(frozen=True)
class RegimeThresholds:
    ret_30_bull: float = 0.08
    ret_30_bear: float = -0.08
    ret_90_bull: float = 0.20
    ret_90_bear: float = -0.20
    high_vol: float = 0.90
    low_efficiency: float = 0.28
    high_efficiency: float = 0.45
    crisis_drawdown: float = -0.30
    crisis_ret_30: float = -0.15


@dataclass(frozen=True)
class RegimeFeatureSnapshot:
    ret_7d: Optional[float]
    ret_30d: Optional[float]
    ret_90d: Optional[float]
    vol_30d: Optional[float]
    eff_30d: Optional[float]
    drawdown_180d: Optional[float]
    trend_score_30d: Optional[float]
    trend_score_90d: Optional[float]

    def as_dict(self) -> Dict[str, Optional[float]]:
        return asdict(self)


@dataclass(frozen=True)
class RegimeDetectionResult:
    timestamp_utc: str
    raw_regime: str
    feature_snapshot: RegimeFeatureSnapshot
    rule_reason: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "timestamp_utc": self.timestamp_utc,
            "raw_regime": self.raw_regime,
            "feature_snapshot": self.feature_snapshot.as_dict(),
            "rule_reason": self.rule_reason,
        }


class RegimeDetector:
    """
    Deterministic regime detector for live operation.

    Input:
    - timestamp_utc: ISO string
    - close_history: list of closes in chronological order
      Expected: at least ~181 daily closes for full feature set

    Output:
    - RegimeDetectionResult
    """

    def __init__(self, thresholds: Optional[RegimeThresholds] = None) -> None:
        self.thresholds = thresholds or RegimeThresholds()

    def detect(self, timestamp_utc: str, close_history: List[float]) -> RegimeDetectionResult:
        closes = self._sanitize_close_history(close_history)
        features = self._build_feature_snapshot(closes)
        raw_regime, rule_reason = self._classify(features)

        return RegimeDetectionResult(
            timestamp_utc=timestamp_utc,
            raw_regime=raw_regime,
            feature_snapshot=features,
            rule_reason=rule_reason,
        )

    def _sanitize_close_history(self, close_history: List[float]) -> List[float]:
        if not isinstance(close_history, list):
            raise TypeError("close_history must be a list[float].")

        cleaned: List[float] = []
        for idx, value in enumerate(close_history):
            if value is None:
                continue
            try:
                x = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid close value at index {idx}: {value}") from exc

            if not math.isfinite(x):
                raise ValueError(f"Non-finite close value at index {idx}: {value}")
            if x <= 0.0:
                raise ValueError(f"Non-positive close value at index {idx}: {value}")

            cleaned.append(x)

        if len(cleaned) < 30:
            raise ValueError(
                "close_history too short. Need at least 30 daily closes for regime detection."
            )

        return cleaned

    def _build_feature_snapshot(self, closes: List[float]) -> RegimeFeatureSnapshot:
        ret_7d = self._pct_change(closes, 7)
        ret_30d = self._pct_change(closes, 30)
        ret_90d = self._pct_change(closes, 90)

        daily_returns = self._daily_returns(closes)
        vol_30d = self._annualized_vol(daily_returns, 30)
        eff_30d = self._efficiency_ratio(closes, 30)
        drawdown_180d = self._drawdown_from_rolling_peak(closes, 180)
        trend_score_30d = self._trend_score(closes, 30)
        trend_score_90d = self._trend_score(closes, 90)

        return RegimeFeatureSnapshot(
            ret_7d=ret_7d,
            ret_30d=ret_30d,
            ret_90d=ret_90d,
            vol_30d=vol_30d,
            eff_30d=eff_30d,
            drawdown_180d=drawdown_180d,
            trend_score_30d=trend_score_30d,
            trend_score_90d=trend_score_90d,
        )

    def _classify(self, f: RegimeFeatureSnapshot) -> tuple[str, str]:
        th = self.thresholds

        required = [f.ret_30d, f.ret_90d, f.vol_30d, f.eff_30d]
        if any(v is None for v in required):
            return "UNCLASSIFIED", "missing_required_features"

        ret_30d = float(f.ret_30d)
        ret_90d = float(f.ret_90d)
        vol_30d = float(f.vol_30d)
        eff_30d = float(f.eff_30d)
        drawdown_180d = 0.0 if f.drawdown_180d is None else float(f.drawdown_180d)

        if drawdown_180d <= th.crisis_drawdown and ret_30d <= th.crisis_ret_30:
            return "CRISIS", "drawdown_180d<=crisis_drawdown and ret_30d<=crisis_ret_30"

        if ret_90d >= th.ret_90_bull and eff_30d >= th.high_efficiency:
            return "UP_TREND", "ret_90d>=ret_90_bull and eff_30d>=high_efficiency"

        if ret_90d <= th.ret_90_bear and eff_30d >= th.high_efficiency:
            return "DOWN_TREND", "ret_90d<=ret_90_bear and eff_30d>=high_efficiency"

        if abs(ret_30d) <= th.ret_30_bull and eff_30d <= th.low_efficiency:
            return "SIDEWAYS", "abs(ret_30d)<=ret_30_bull and eff_30d<=low_efficiency"

        if abs(ret_30d) <= th.ret_30_bull and vol_30d < th.high_vol:
            return "SIDEWAYS", "abs(ret_30d)<=ret_30_bull and vol_30d<high_vol"

        if ret_30d > 0.0 and eff_30d >= th.low_efficiency:
            return "UP_TREND", "ret_30d>0 and eff_30d>=low_efficiency"

        if ret_30d < 0.0 and eff_30d >= th.low_efficiency:
            return "DOWN_TREND", "ret_30d<0 and eff_30d>=low_efficiency"

        return "UNCLASSIFIED", "no_rule_matched"

    def _pct_change(self, closes: List[float], lookback: int) -> Optional[float]:
        if len(closes) <= lookback:
            return None
        start = closes[-(lookback + 1)]
        end = closes[-1]
        return (end / start) - 1.0

    def _daily_returns(self, closes: List[float]) -> List[float]:
        out: List[float] = []
        for i in range(1, len(closes)):
            out.append((closes[i] / closes[i - 1]) - 1.0)
        return out

    def _annualized_vol(self, daily_returns: List[float], window: int) -> Optional[float]:
        if len(daily_returns) < window:
            return None
        sample = daily_returns[-window:]
        mean = sum(sample) / len(sample)
        var = sum((x - mean) ** 2 for x in sample) / len(sample)
        std = math.sqrt(var)
        return std * math.sqrt(365.0)

    def _efficiency_ratio(self, closes: List[float], window: int) -> Optional[float]:
        if len(closes) <= window:
            return None

        window_closes = closes[-(window + 1):]
        net_move = abs(window_closes[-1] - window_closes[0])

        total_move = 0.0
        for i in range(1, len(window_closes)):
            total_move += abs(window_closes[i] - window_closes[i - 1])

        if total_move <= 0.0:
            return 0.0

        er = net_move / total_move
        if er < 0.0:
            return 0.0
        if er > 1.0:
            return 1.0
        return er

    def _drawdown_from_rolling_peak(self, closes: List[float], window: int) -> Optional[float]:
        if len(closes) < 2:
            return None

        lookback = closes[-window:] if len(closes) >= window else closes
        peak = max(lookback)
        if peak <= 0.0:
            return None
        return (closes[-1] / peak) - 1.0

    def _trend_score(self, closes: List[float], window: int) -> Optional[float]:
        if len(closes) <= window:
            return None

        ret_component = self._pct_change(closes, window)
        if ret_component is None:
            return None

        ema_fast = self._ema(closes, max(3, window // 3))
        ema_slow = self._ema(closes, max(5, window))

        if ema_fast is None or ema_slow is None or ema_slow == 0.0:
            return None

        ema_component = (ema_fast / ema_slow) - 1.0
        return 0.7 * ret_component + 0.3 * ema_component

    def _ema(self, values: List[float], span: int) -> Optional[float]:
        if not values:
            return None
        if span <= 1:
            return values[-1]

        alpha = 2.0 / (span + 1.0)
        ema = values[0]
        for x in values[1:]:
            ema = alpha * x + (1.0 - alpha) * ema
        return ema


def detect_regime_from_daily_closes(
    timestamp_utc: str,
    close_history: List[float],
    thresholds: Optional[RegimeThresholds] = None,
) -> Dict[str, object]:
    detector = RegimeDetector(thresholds=thresholds)
    result = detector.detect(timestamp_utc=timestamp_utc, close_history=close_history)
    return result.as_dict()