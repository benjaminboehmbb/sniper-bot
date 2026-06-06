# P46 RUNTIME TIMING SIGNAL WIRING AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit how live_l1/core/loop.py wires runtime signals into compute_5m_timing_vote after P45 produced only none votes.

## Background

P44 isolated tests confirmed polarity-aware timing works when rsi_signal and stoch_signal are passed explicitly.

P45 runtime validation produced 100 none votes, suggesting runtime signal kwargs may not be passed into compute_5m_timing_vote.

## Target File

live_l1/core/loop.py

## Relevant Source Context

### Context 1

```text
11: import uuid
12: from datetime import datetime, timezone
13: from dataclasses import dataclass
14: from pathlib import Path
15: 
16: from live_l1.logs.logger import L1Logger
17: from live_l1.io.market import CSVMarketFeed
18: from live_l1.io.valid import validate_runtime_config
19: from live_l1.state.state_store import load_or_init_state, persist_state
20: from live_l1.state.state_validation import validate_loaded_state
21: from live_l1.guards.guards import evaluate_guards
22: from live_l1.core.clock import TickClock
23: from live_l1.core.feature_snapshot import build_feature_snapshot
24: from live_l1.core.regime_detector import detect_regime
25: from live_l1.core.intent import compute_1m_intent_raw
26: from live_l1.core.timing_5m import compute_5m_timing_vote
27: from live_l1.core.intent_fusion import fuse_intent_with_5m_timing
28: from live_l1.core.execution import apply_paper_execution
29: from live_l1.tools.recover_runtime_state import recover_runtime_state
30: from live_l1.tools.reconcile_runtime_state import run_reconciliation
31: from live_l1.tools.startup_validator import validate_startup
32: from live_l1.meta_state.meta_state_shadow import build_meta_state_shadow
33: from live_l1.meta_state.meta_state_runtime import resolve_position_multiplier
34: 
35: 
36: @dataclass(frozen=True)
37: class RuntimeConfig:
38:     repo_root: str
39:     log_path: str
40:     state_dir: str
41:     symbol: str
```

### Context 2

```text
14: from pathlib import Path
15: 
16: from live_l1.logs.logger import L1Logger
17: from live_l1.io.market import CSVMarketFeed
18: from live_l1.io.valid import validate_runtime_config
19: from live_l1.state.state_store import load_or_init_state, persist_state
20: from live_l1.state.state_validation import validate_loaded_state
21: from live_l1.guards.guards import evaluate_guards
22: from live_l1.core.clock import TickClock
23: from live_l1.core.feature_snapshot import build_feature_snapshot
24: from live_l1.core.regime_detector import detect_regime
25: from live_l1.core.intent import compute_1m_intent_raw
26: from live_l1.core.timing_5m import compute_5m_timing_vote
27: from live_l1.core.intent_fusion import fuse_intent_with_5m_timing
28: from live_l1.core.execution import apply_paper_execution
29: from live_l1.tools.recover_runtime_state import recover_runtime_state
30: from live_l1.tools.reconcile_runtime_state import run_reconciliation
31: from live_l1.tools.startup_validator import validate_startup
32: from live_l1.meta_state.meta_state_shadow import build_meta_state_shadow
33: from live_l1.meta_state.meta_state_runtime import resolve_position_multiplier
34: 
35: 
36: @dataclass(frozen=True)
37: class RuntimeConfig:
38:     repo_root: str
39:     log_path: str
40:     state_dir: str
41:     symbol: str
42:     gate_mode: str
43:     fee_roundtrip: float
44:     decision_tick_seconds: float
```

### Context 3

```text
344:     state,
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
```

### Context 4

```text
345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
```

### Context 5

```text
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
```

### Context 6

```text
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
```

### Context 7

```text
350:     if position not in ("LONG", "SHORT"):
351:         return
352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")
357:         + features.signal("bollinger_signal")
358:         + features.signal("stoch_signal")
359:         + features.signal("cci_signal")
360:     )
361: 
362:     atr_sig = int(features.signal("atr_signal"))
363:     atr_quality = "bad_atr" if atr_sig == -1 else "good_atr"
364: 
365:     regime_label = str(getattr(regime, "label", regime)).strip().lower()
366: 
367:     risk_level, risk_name, reason = _passive_shadow_risk_from_context(
368:         side=side,
369:         regime=regime_label,
370:         atr_quality=atr_quality,
371:         current_score=current_score,
372:     )
373:     risk_components = _passive_shadow_risk_components(
374:         side=side,
375:         regime=regime_label,
376:         atr_quality=atr_quality,
377:         current_score=current_score,
378:     )
379: 
380:     out_path = os.path.join(repo_root, "live_logs", "passive_shadow_risk_snapshots.csv")
```

### Context 8

```text
855:             try:
856:                 snapshot = market.next_snapshot()
857:             except StopIteration:
858:                 log.log(
859:                     category="L1",
860:                     event="system_stop",
861:                     severity="INFO",
862:                     system_state_id=state.system_state_id,
863:                     fields={"reason": "market_feed_exhausted", "tick": tick.tick_id},
864:                 )
865:                 return 0
866: 
867:             features = build_feature_snapshot(snapshot)
868:             regime = detect_regime(features)
869: 
870:             current_position = "FLAT"
871:             if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
872:                 current_position = str(state.s2_position.position).strip().upper()
873: 
874:             intent_1m_raw, forced = compute_1m_intent_raw(
875:                 cfg=cfg,
876:                 tick_id=tick.tick_id,
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
```

### Context 9

```text
869: 
870:             current_position = "FLAT"
871:             if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
872:                 current_position = str(state.s2_position.position).strip().upper()
873: 
874:             intent_1m_raw, forced = compute_1m_intent_raw(
875:                 cfg=cfg,
876:                 tick_id=tick.tick_id,
877:                 features=features,
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:             )
887: 
888:             fused = fuse_intent_with_5m_timing(
889:                 intent_1m_raw=intent_1m_raw,
890:                 vote_5m_direction=vote_v1.direction,
891:                 vote_5m_strength=vote_v1.strength,
892:                 vote_5m_seed_id=vote_v1.seed_id,
893:                 thresh=cfg.thresh_5m,
894:                 allow_long=int(features.allow_long),
895:                 allow_short=int(features.allow_short),
896:                 current_position=current_position,
897:             )
898: 
899:             log.log(
```

### Context 10

```text
878:                 current_position=current_position,
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:             )
887: 
888:             fused = fuse_intent_with_5m_timing(
889:                 intent_1m_raw=intent_1m_raw,
890:                 vote_5m_direction=vote_v1.direction,
891:                 vote_5m_strength=vote_v1.strength,
892:                 vote_5m_seed_id=vote_v1.seed_id,
893:                 thresh=cfg.thresh_5m,
894:                 allow_long=int(features.allow_long),
895:                 allow_short=int(features.allow_short),
896:                 current_position=current_position,
897:             )
898: 
899:             log.log(
900:                 category="L1",
901:                 event="clock_tick",
902:                 severity="INFO",
903:                 system_state_id=state.system_state_id,
904:                 fields={
905:                     "tick": tick.tick_id,
906:                     "tick_started_utc": tick.tick_started_utc,
907:                     "decision_tick_seconds": cfg.decision_tick_seconds,
908:                 },
```

### Context 11

```text
879:             )
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:             )
887: 
888:             fused = fuse_intent_with_5m_timing(
889:                 intent_1m_raw=intent_1m_raw,
890:                 vote_5m_direction=vote_v1.direction,
891:                 vote_5m_strength=vote_v1.strength,
892:                 vote_5m_seed_id=vote_v1.seed_id,
893:                 thresh=cfg.thresh_5m,
894:                 allow_long=int(features.allow_long),
895:                 allow_short=int(features.allow_short),
896:                 current_position=current_position,
897:             )
898: 
899:             log.log(
900:                 category="L1",
901:                 event="clock_tick",
902:                 severity="INFO",
903:                 system_state_id=state.system_state_id,
904:                 fields={
905:                     "tick": tick.tick_id,
906:                     "tick_started_utc": tick.tick_started_utc,
907:                     "decision_tick_seconds": cfg.decision_tick_seconds,
908:                 },
909:             )
```

### Context 12

```text
880: 
881:             vote_v1 = compute_5m_timing_vote(
882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
883:                 thresh=cfg.thresh_5m,
884:                 symbol=cfg.symbol,
885:                 now_utc=tick.tick_started_utc,
886:             )
887: 
888:             fused = fuse_intent_with_5m_timing(
889:                 intent_1m_raw=intent_1m_raw,
890:                 vote_5m_direction=vote_v1.direction,
891:                 vote_5m_strength=vote_v1.strength,
892:                 vote_5m_seed_id=vote_v1.seed_id,
893:                 thresh=cfg.thresh_5m,
894:                 allow_long=int(features.allow_long),
895:                 allow_short=int(features.allow_short),
896:                 current_position=current_position,
897:             )
898: 
899:             log.log(
900:                 category="L1",
901:                 event="clock_tick",
902:                 severity="INFO",
903:                 system_state_id=state.system_state_id,
904:                 fields={
905:                     "tick": tick.tick_id,
906:                     "tick_started_utc": tick.tick_started_utc,
907:                     "decision_tick_seconds": cfg.decision_tick_seconds,
908:                 },
909:             )
910: 
```

### Context 13

```text
936:                     "timestamp_utc": features.timestamp_utc,
937:                     "regime_label": regime.label,
938:                     "risk_label": regime.risk_label,
939:                     "ma200_signal": regime.ma200_signal,
940:                     "atr_signal": regime.atr_signal,
941:                     "mfi_signal": regime.mfi_signal,
942:                     "entry_score": regime.score,
943:                 },
944:             )
945: 
946:             log.log(
947:                 category="L3",
948:                 event="intent_fused",
949:                 severity="INFO",
950:                 system_state_id=state.system_state_id,
951:                 intent_id=fused.intent_id,
952:                 fields={
953:                     "tick": tick.tick_id,
954:                     "allow_long": int(features.allow_long),
955:                     "allow_short": int(features.allow_short),
956:                     "intent_1m_raw": intent_1m_raw,
957:                     "intent_final": fused.intent_final,
958:                     "reason_code": fused.reason_code,
959:                     "current_position": fused.current_position,
960:                     "test_forced_intent": int(forced),
961:                     "thresh": cfg.thresh_5m,
962:                     "vote_5m_direction": vote_v1.direction,
963:                     "vote_5m_seed_id": str(vote_v1.seed_id),
964:                     "vote_5m_strength": float(vote_v1.strength),
965:                 },
966:             )
```

### Context 14

```text
950:                 system_state_id=state.system_state_id,
951:                 intent_id=fused.intent_id,
952:                 fields={
953:                     "tick": tick.tick_id,
954:                     "allow_long": int(features.allow_long),
955:                     "allow_short": int(features.allow_short),
956:                     "intent_1m_raw": intent_1m_raw,
957:                     "intent_final": fused.intent_final,
958:                     "reason_code": fused.reason_code,
959:                     "current_position": fused.current_position,
960:                     "test_forced_intent": int(forced),
961:                     "thresh": cfg.thresh_5m,
962:                     "vote_5m_direction": vote_v1.direction,
963:                     "vote_5m_seed_id": str(vote_v1.seed_id),
964:                     "vote_5m_strength": float(vote_v1.strength),
965:                 },
966:             )
967: 
968:             _append_trade_lifecycle_snapshot(
969:                 repo_root=repo_root,
970:                 tick_id=tick.tick_id,
971:                 timestamp_utc=str(features.timestamp_utc),
972:                 snapshot_id=str(features.snapshot_id),
973:                 state=state,
974:                 features=features,
975:                 regime=regime,
976:             )
977: 
978:             _append_passive_shadow_risk_snapshot(
979:                 repo_root=repo_root,
980:                 tick_id=tick.tick_id,
```

### Context 15

```text
951:                 intent_id=fused.intent_id,
952:                 fields={
953:                     "tick": tick.tick_id,
954:                     "allow_long": int(features.allow_long),
955:                     "allow_short": int(features.allow_short),
956:                     "intent_1m_raw": intent_1m_raw,
957:                     "intent_final": fused.intent_final,
958:                     "reason_code": fused.reason_code,
959:                     "current_position": fused.current_position,
960:                     "test_forced_intent": int(forced),
961:                     "thresh": cfg.thresh_5m,
962:                     "vote_5m_direction": vote_v1.direction,
963:                     "vote_5m_seed_id": str(vote_v1.seed_id),
964:                     "vote_5m_strength": float(vote_v1.strength),
965:                 },
966:             )
967: 
968:             _append_trade_lifecycle_snapshot(
969:                 repo_root=repo_root,
970:                 tick_id=tick.tick_id,
971:                 timestamp_utc=str(features.timestamp_utc),
972:                 snapshot_id=str(features.snapshot_id),
973:                 state=state,
974:                 features=features,
975:                 regime=regime,
976:             )
977: 
978:             _append_passive_shadow_risk_snapshot(
979:                 repo_root=repo_root,
980:                 tick_id=tick.tick_id,
981:                 timestamp_utc=str(features.timestamp_utc),
```

### Context 16

```text
952:                 fields={
953:                     "tick": tick.tick_id,
954:                     "allow_long": int(features.allow_long),
955:                     "allow_short": int(features.allow_short),
956:                     "intent_1m_raw": intent_1m_raw,
957:                     "intent_final": fused.intent_final,
958:                     "reason_code": fused.reason_code,
959:                     "current_position": fused.current_position,
960:                     "test_forced_intent": int(forced),
961:                     "thresh": cfg.thresh_5m,
962:                     "vote_5m_direction": vote_v1.direction,
963:                     "vote_5m_seed_id": str(vote_v1.seed_id),
964:                     "vote_5m_strength": float(vote_v1.strength),
965:                 },
966:             )
967: 
968:             _append_trade_lifecycle_snapshot(
969:                 repo_root=repo_root,
970:                 tick_id=tick.tick_id,
971:                 timestamp_utc=str(features.timestamp_utc),
972:                 snapshot_id=str(features.snapshot_id),
973:                 state=state,
974:                 features=features,
975:                 regime=regime,
976:             )
977: 
978:             _append_passive_shadow_risk_snapshot(
979:                 repo_root=repo_root,
980:                 tick_id=tick.tick_id,
981:                 timestamp_utc=str(features.timestamp_utc),
982:                 snapshot_id=str(features.snapshot_id),
```

## Preliminary Assessment

- If compute_5m_timing_vote is called without rsi_signal/stoch_signal kwargs, polarity-aware timing will correctly return none.
- The audit output should identify the exact call site and available feature signal access pattern.
- No code changes are introduced in P46.

## Required Next Step

Review call-site output and design the wiring fix before patching.

## Result

Status: PASS
