# REPOSITORY USAGE AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Summary

Python files scanned: 238

- ACTIVE_CORE: 33
- ACTIVE_OR_ANALYSIS_ENGINE: 3
- ACTIVE_TOOL_OR_ENTRYPOINT: 12
- LIVE_ENTRYPOINT_REVIEW: 1
- RESEARCH_ARCHIVE_CANDIDATE: 43
- RESEARCH_OR_BATCH_SCRIPT_REVIEW: 105
- STANDALONE_TOOL_REVIEW: 38
- TEST_TOOL: 3

## Classification Details

### ACTIVE_CORE

- live_l1/__init__.py | imported_by=15
- live_l1/core/__init__.py | imported_by=8
- live_l1/core/clock.py | imported_by=1
- live_l1/core/execution.py | imported_by=1
- live_l1/core/feature_snapshot.py | imported_by=3
- live_l1/core/gate_builder.py | imported_by=0
- live_l1/core/intent.py | imported_by=2
- live_l1/core/intent_fusion.py | imported_by=2
- live_l1/core/loop.py | imported_by=2
- live_l1/core/regime_builder.py | imported_by=0
- live_l1/core/regime_detector.py | imported_by=1
- live_l1/core/regime_v2_builder.py | imported_by=0
- live_l1/core/signal_builder.py | imported_by=0
- live_l1/core/timing_5m.py | imported_by=1
- live_l1/core/timing_5m_v2.py | imported_by=1
- live_l1/guards/__init__.py | imported_by=1
- live_l1/guards/cost_guards.py | imported_by=0
- live_l1/guards/guards.py | imported_by=1
- live_l1/io/__init__.py | imported_by=2
- live_l1/io/market.py | imported_by=2
- live_l1/io/valid.py | imported_by=1
- live_l1/io/validate.py | imported_by=0
- live_l1/logs/__init__.py | imported_by=1
- live_l1/logs/logger.py | imported_by=1
- live_l1/meta_state/__init__.py | imported_by=2
- live_l1/meta_state/meta_state_runtime.py | imported_by=1
- live_l1/meta_state/meta_state_shadow.py | imported_by=2
- live_l1/operational_profiles.py | imported_by=2
- live_l1/state/__init__.py | imported_by=2
- live_l1/state/models.py | imported_by=1
- live_l1/state/persist.py | imported_by=1
- live_l1/state/state_store.py | imported_by=1
- live_l1/state/state_validation.py | imported_by=1

### ACTIVE_OR_ANALYSIS_ENGINE

- engine/__init__.py | imported_by=21
- engine/simtraderGS.py | imported_by=8
- engine/validators.py | imported_by=0

### ACTIVE_TOOL_OR_ENTRYPOINT

- live_l1/tools/create_runtime_backup.py | imported_by=0
- live_l1/tools/monitor_runtime.py | imported_by=0
- live_l1/tools/monitor_summary.py | imported_by=0
- live_l1/tools/operational_health_report.py | imported_by=0
- live_l1/tools/reconcile_runtime_state.py | imported_by=4
- live_l1/tools/recover_runtime_state.py | imported_by=1
- live_l1/tools/replay_execution_state.py | imported_by=4
- live_l1/tools/runtime_control_loop.py | imported_by=0
- live_l1/tools/safe_launch.py | imported_by=0
- live_l1/tools/startup_validator.py | imported_by=4
- live_l1/tools/validate_runtime_backup.py | imported_by=0
- live_l1/tools/validate_runtime_schema.py | imported_by=0

### LIVE_ENTRYPOINT_REVIEW

- scripts/run_live_l1_paper.py | imported_by=0

### RESEARCH_ARCHIVE_CANDIDATE

- scripts/state_research/analyze_continuous_meta_state_score.py | imported_by=0
- scripts/state_research/analyze_degradation_acceleration.py | imported_by=0
- scripts/state_research/analyze_meta_state_scoring.py | imported_by=0
- scripts/state_research/analyze_passive_shadow_risk.py | imported_by=0
- scripts/state_research/analyze_passive_shadow_risk_v2.py | imported_by=0
- scripts/state_research/analyze_pre_toxic_transitions.py | imported_by=0
- scripts/state_research/analyze_recovery_probability.py | imported_by=0
- scripts/state_research/analyze_recovery_transitions.py | imported_by=0
- scripts/state_research/analyze_safe_collapse_patterns.py | imported_by=0
- scripts/state_research/analyze_shadow_persistence.py | imported_by=0
- scripts/state_research/analyze_snapshot_meta_state_score.py | imported_by=0
- scripts/state_research/analyze_state_factor_strength.py | imported_by=0
- scripts/state_research/analyze_step18_buckets.py | imported_by=0
- scripts/state_research/analyze_step18_clusters.py | imported_by=0
- scripts/state_research/analyze_step18_predictive_power.py | imported_by=0
- scripts/state_research/analyze_step18_trade_lifetime.py | imported_by=0
- scripts/state_research/analyze_step19B_real_exit_replay.py | imported_by=0
- scripts/state_research/analyze_step19B_threshold_sweep.py | imported_by=0
- scripts/state_research/analyze_step19_blocked_trades.py | imported_by=0
- scripts/state_research/analyze_step19_blocked_winners.py | imported_by=0
- scripts/state_research/analyze_step19_dynamic_exit_replay.py | imported_by=0
- scripts/state_research/analyze_step19_entry_gate.py | imported_by=0
- scripts/state_research/analyze_step19_gate_quality.py | imported_by=0
- scripts/state_research/analyze_step19_risk_escalation.py | imported_by=0
- scripts/state_research/analyze_step19_shadow_gate.py | imported_by=0
- scripts/state_research/analyze_step19_shadow_gate_replay.py | imported_by=0
- scripts/state_research/analyze_step19_threshold_fine.py | imported_by=0
- scripts/state_research/analyze_step19_threshold_sweep.py | imported_by=0
- scripts/state_research/analyze_step20C_live_replay.py | imported_by=0
- scripts/state_research/analyze_step20D_dynamic_exposure_scaling.py | imported_by=0
- scripts/state_research/analyze_step20D_sensitivity.py | imported_by=0
- scripts/state_research/analyze_step20E_true_dynamic_exposure_replay.py | imported_by=0
- scripts/state_research/analyze_step20_position_sizing_replay.py | imported_by=0
- scripts/state_research/analyze_transition_momentum.py | imported_by=0
- scripts/state_research/build_step18_core_pipeline.py | imported_by=0
- scripts/state_research/simulate_adaptive_position_sizing.py | imported_by=0
- scripts/state_research/simulate_adaptive_position_sizing_variants.py | imported_by=0
- scripts/state_research/simulate_confirmed_toxic_exit.py | imported_by=0
- scripts/state_research/simulate_safe_collapse_exit.py | imported_by=0
- scripts/state_research/simulate_safe_collapse_partial_exit.py | imported_by=0
- scripts/state_research/simulate_shadow_gates.py | imported_by=0
- scripts/state_research/simulate_shadow_gates_no_lookahead.py | imported_by=0
- scripts/state_research/simulate_toxic_dominance_exit.py | imported_by=0

### RESEARCH_OR_BATCH_SCRIPT_REVIEW

- scripts/__init__.py | imported_by=0
- scripts/analyze_GS_k10_long.py | imported_by=0
- scripts/analyze_GS_k10_short.py | imported_by=0
- scripts/analyze_GS_k11_long.py | imported_by=0
- scripts/analyze_GS_k11_short.py | imported_by=0
- scripts/analyze_GS_k12_long.py | imported_by=0
- scripts/analyze_GS_k12_long_CANONICAL.py | imported_by=0
- scripts/analyze_GS_k12_short.py | imported_by=0
- scripts/analyze_GS_k3_long.py | imported_by=0
- scripts/analyze_GS_k3_long_weighted.py | imported_by=0
- scripts/analyze_GS_k3_short.py | imported_by=0
- scripts/analyze_GS_k4_long.py | imported_by=0
- scripts/analyze_GS_k4_short.py | imported_by=0
- scripts/analyze_GS_k5_long.py | imported_by=0
- scripts/analyze_GS_k5_short.py | imported_by=0
- scripts/analyze_GS_k6_short.py | imported_by=0
- scripts/analyze_GS_k7_long.py | imported_by=0
- scripts/analyze_GS_k7_short.py | imported_by=0
- scripts/analyze_GS_k8_long.py | imported_by=0
- scripts/analyze_GS_k8_short.py | imported_by=0
- scripts/analyze_GS_k9_long.py | imported_by=0
- scripts/analyze_GS_k9_short.py | imported_by=0
- scripts/analyze_btc_regimes.py | imported_by=0
- scripts/analyze_collapse_recovery_patterns.py | imported_by=0
- scripts/analyze_health_future_outcomes.py | imported_by=0
- scripts/analyze_health_momentum.py | imported_by=0
- scripts/analyze_loop_persistence.py | imported_by=0
- scripts/analyze_recovery_triggers.py | imported_by=0
- scripts/analyze_regime_mobility.py | imported_by=0
- scripts/analyze_regime_transitions.py | imported_by=0
- scripts/analyze_regimes.py | imported_by=0
- scripts/analyze_state_mobility.py | imported_by=0
- scripts/analyze_state_paths.py | imported_by=0
- scripts/analyze_state_transitions.py | imported_by=0
- scripts/analyze_strategy_by_regime.py | imported_by=0
- scripts/analyze_structure_false_positives.py | imported_by=0
- scripts/analyze_structure_overlay_warning_power.py | imported_by=0
- scripts/analyze_trade_lifecycle.py | imported_by=0
- scripts/analyze_transition_persistence.py | imported_by=0
- scripts/analyze_transition_timing.py | imported_by=0
- scripts/apply_structure_labels_to_lifecycle.py | imported_by=0
- scripts/build_GS_k12_long_FINAL_CANONICAL.py | imported_by=0
- scripts/build_GS_k12_short_RESULTS_CANONICAL.py | imported_by=0
- scripts/build_market_phase_segments.py | imported_by=0
- scripts/build_meta_structure_model.py | imported_by=0
- scripts/build_recovery_probability_engine.py | imported_by=0
- scripts/build_regime_compatibility_matrix.py | imported_by=0
- scripts/build_regime_native_segments.py | imported_by=0
- scripts/build_shadow_risk_engine.py | imported_by=0
- scripts/build_state_transition_graph.py | imported_by=0
- scripts/build_structural_stability_ranking.py | imported_by=0
- scripts/build_time_weighted_toxic_persistence.py | imported_by=0
- scripts/build_toxic_persistence_model.py | imported_by=0
- scripts/build_trade_health_model.py | imported_by=0
- scripts/classify_trade_states.py | imported_by=0
- scripts/download_btcusdt_1m_binance_bulk.py | imported_by=0
- scripts/generate_GS_k10_long_from_k9_seeds.py | imported_by=0
- scripts/generate_GS_k10_short_from_k9_seeds.py | imported_by=0
- scripts/generate_GS_k11_long_from_k10_seeds.py | imported_by=0
- scripts/generate_GS_k11_short_from_k10_seeds.py | imported_by=0
- scripts/generate_GS_k12_long_from_k11_seeds.py | imported_by=0
- scripts/generate_GS_k12_short_from_k11_seeds.py | imported_by=0
- scripts/generate_GS_k3_long_weighted.py | imported_by=0
- scripts/generate_GS_k3_short.py | imported_by=0
- scripts/generate_GS_k4_long_from_k3_weighted.py | imported_by=0
- scripts/generate_GS_k4_short_from_k3_seeds.py | imported_by=0
- scripts/generate_GS_k5_long_from_k4_seeds.py | imported_by=0
- scripts/generate_GS_k5_short_from_k4_seeds.py | imported_by=0
- scripts/generate_GS_k6_short_from_k5_seeds.py | imported_by=0
- scripts/generate_GS_k7_long_from_k6_seeds.py | imported_by=0
- scripts/generate_GS_k7_short_from_k6_seeds.py | imported_by=0
- scripts/generate_GS_k8_long_from_k7_seeds.py | imported_by=0
- scripts/generate_GS_k8_short_from_k7_seeds.py | imported_by=0
- scripts/generate_GS_k9_long_from_k8_seeds.py | imported_by=0
- scripts/generate_GS_k9_short_from_k8_seeds.py | imported_by=0
- scripts/generate_combinations_universal.py | imported_by=0
- scripts/pipeline_orchestrator.py | imported_by=0
- scripts/post_gs_h1_fee_cost_sensitivity.py | imported_by=0
- scripts/post_gs_h2_timeframe_transfer.py | imported_by=0
- scripts/post_gs_h3_asset_transfer_run.py | imported_by=0
- scripts/post_gs_h3_build_eth_1m_gs_compat.py | imported_by=0
- scripts/post_gs_h3_build_eth_signals_regime_gs_compat.py | imported_by=0
- scripts/post_gs_h3_fix_eth_rawonly_timestamps.py | imported_by=0
- scripts/post_gs_h4_regime_controller_run.py | imported_by=0
- scripts/post_gs_h5_execution_realism_run.py | imported_by=0
- scripts/select_GS_k10_long_top250_for_k11_seeds.py | imported_by=0
- scripts/select_GS_k10_short_top66_for_k11_seeds.py | imported_by=0
- scripts/select_GS_k11_long_top250_for_k12_seeds.py | imported_by=0
- scripts/select_GS_k12_long_TOP250_CANONICAL.py | imported_by=0
- scripts/select_GS_k12_long_top250_FINAL.py | imported_by=0
- scripts/select_GS_k3_short_top300_for_k4_seeds.py | imported_by=0
- scripts/select_GS_k4_long_top300_for_k5_seeds.py | imported_by=0
- scripts/select_GS_k4_short_top300_for_k5_seeds.py | imported_by=0
- scripts/select_GS_k5_long_top250_for_k6_seeds.py | imported_by=0
- scripts/select_GS_k5_short_top300_for_k6_seeds.py | imported_by=0
- scripts/select_GS_k6_short_top300_for_k7_seeds.py | imported_by=0
- scripts/select_GS_k7_long_top250_for_k8_seeds.py | imported_by=0
- scripts/select_GS_k7_short_top300_for_k8_seeds.py | imported_by=0
- scripts/select_GS_k8_long_top250_for_k9_seeds.py | imported_by=0
- scripts/select_GS_k8_short_top300_for_k9_seeds.py | imported_by=0
- scripts/select_GS_k9_long_top250_for_k10_seeds.py | imported_by=0
- scripts/select_GS_k9_short_top198_for_k10_seeds.py | imported_by=0
- scripts/summarize_state_graph_quality.py | imported_by=0
- scripts/tune_shadow_risk_precision.py | imported_by=0
- scripts/validate_trade_health_against_results.py | imported_by=0

### STANDALONE_TOOL_REVIEW

- tools/__init__.py | imported_by=0
- tools/add_inverted_short_signals.py | imported_by=0
- tools/add_regime.py | imported_by=0
- tools/analyze_equity_gate_candidates.py | imported_by=0
- tools/analyze_trades.py | imported_by=0
- tools/build_gs_5m_from_1m.py | imported_by=0
- tools/build_regime_v2_from_v1.py | imported_by=0
- tools/compare_fusion_modes_2026-06-05.py | imported_by=0
- tools/compare_runs.py | imported_by=0
- tools/compare_trade_analyses.py | imported_by=0
- tools/download_binance_1min.py | imported_by=0
- tools/downsample_1m_to_tfs.py | imported_by=0
- tools/fill_price_1m_gaps.py | imported_by=0
- tools/fix_5m_short_seeds_add_dir.py | imported_by=0
- tools/gs_build_asymmetric_gate.py | imported_by=0
- tools/gs_checklist_runner.py | imported_by=0
- tools/gs_input_preflight.py | imported_by=0
- tools/gs_long_final_preflight.py | imported_by=0
- tools/gs_long_short_diagnostics.py | imported_by=0
- tools/gs_meta_compare_k12_finals.py | imported_by=0
- tools/gs_policy_entry_runner.py | imported_by=0
- tools/gs_policy_hold_runner.py | imported_by=0
- tools/gs_regime_quality_report.py | imported_by=0
- tools/gs_regression_gate.py | imported_by=0
- tools/gs_run_guard.py | imported_by=0
- tools/gs_run_with_manifest.py | imported_by=0
- tools/gs_short_diagnostics.py | imported_by=0
- tools/gs_smoke_suite.py | imported_by=0
- tools/l1_health_check.py | imported_by=0
- tools/l1c_fusion_stats.py | imported_by=0
- tools/l1c_smoke_test.py | imported_by=0
- tools/l1d_resume_test.py | imported_by=0
- tools/l1e_log_summary.py | imported_by=0
- tools/repository_usage_audit.py | imported_by=0
- tools/summarize_top_strategies.py | imported_by=0
- tools/test_timing_5m_v2_minimal.py | imported_by=0
- tools/validate_price_1min.py | imported_by=0
- tools/validate_trades.py | imported_by=0

### TEST_TOOL

- live_l1/tools/test_monitor_failure_injection.py | imported_by=0
- live_l1/tools/test_operational_profiles.py | imported_by=0
- live_l1/tools/test_unattended_operation.py | imported_by=0

## Notes

This audit is a static import and path classification scan.
It does not prove that a standalone script is unused.
Archive decisions require an additional manual review.
