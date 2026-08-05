"""RCC002_S8_FIELD_OWNERSHIP_V1 - the canonical S8 field ownership and
leakage registry.

Transcribed verbatim, in normative document order, from
``docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md``
SS7.9.1 ("Kanonische Feld-Eigentums- und Leakage-Registry"). This is the
single normative source for which stage owns a field and what leakage
class it carries; no other module in ``rcc002.s8`` may hardcode a
field's owner stage or leakage class independently of this registry
(Reproducibility and Manifest Specification SS8.7/SS8.8: the Data
Pipeline Specification owns the logical stage/view contract).

``FIELD_REGISTRY_SHA256`` is derived mechanically (RCC_JSON_CANONICALIZATION_V1
of ``FIELD_REGISTRY_GROUPS`` as a plain list-of-dicts), never hardcoded; a
focused test independently re-extracts SS7.9.1 from the specification file
and asserts byte-for-byte equality with the constants below.
"""

from __future__ import annotations

from rcc002.s8.canonical import canonical_sha256
from rcc002.s8.reason_codes import FieldRegistryError

FIELD_REGISTRY_ID = "RCC002_S8_FIELD_OWNERSHIP_V1"
FIELD_REGISTRY_VERSION = "1.0.0"

FIELD_REGISTRY_GROUPS = (
    {
        "field_owner_stage": "S0_SOURCE",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "source_snapshot_id", "provider", "market_type", "symbol", "interval",
        ),
    },
    {
        "field_owner_stage": "S1_NORMALIZED",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "source_row_id", "open_time", "close_time", "open", "high", "low", "close",
            "volume",
        ),
    },
    {
        "field_owner_stage": "S2_VALIDATED",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "market_segment_id", "quality_is_observed", "quality_is_synthetic",
            "quality_has_source_conflict", "quality_gap_before", "quality_gap_after",
            "quality_timestamp_valid", "quality_ohlc_valid", "quality_volume_valid",
            "quality_market_values_valid", "quality_status", "quality_reason_codes",
            "quality_rule_version", "quality_gate_pass",
        ),
    },
    {
        "field_owner_stage": "S3_INDICATORS",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "indicator_profile_id", "indicator_profile_version", "indicator_schema_id",
            "indicator_schema_version", "indicator_schema_ref", "indicator_segment_id",
            "sma_close_200", "sma_close_200_valid", "sma_close_200_warmup_complete",
            "sma_close_200_reason_codes", "ema_close_50", "ema_close_50_valid",
            "ema_close_50_warmup_complete", "ema_close_50_reason_codes", "rsi_wilder_14",
            "rsi_wilder_14_valid", "rsi_wilder_14_warmup_complete",
            "rsi_wilder_14_reason_codes", "macd_line_12_26", "macd_line_12_26_valid",
            "macd_line_12_26_warmup_complete", "macd_line_12_26_reason_codes",
            "macd_signal_line_12_26_9", "macd_signal_line_12_26_9_valid",
            "macd_signal_line_12_26_9_warmup_complete",
            "macd_signal_line_12_26_9_reason_codes", "macd_hist_12_26_9",
            "macd_hist_12_26_9_valid", "macd_hist_12_26_9_warmup_complete",
            "macd_hist_12_26_9_reason_codes", "bb_mid_20", "bb_mid_20_valid",
            "bb_mid_20_warmup_complete", "bb_mid_20_reason_codes", "bb_upper_20_2",
            "bb_upper_20_2_valid", "bb_upper_20_2_warmup_complete",
            "bb_upper_20_2_reason_codes", "bb_lower_20_2", "bb_lower_20_2_valid",
            "bb_lower_20_2_warmup_complete", "bb_lower_20_2_reason_codes", "bb_width_20_2",
            "bb_width_20_2_valid", "bb_width_20_2_warmup_complete",
            "bb_width_20_2_reason_codes", "stoch_k_14", "stoch_k_14_valid",
            "stoch_k_14_warmup_complete", "stoch_k_14_reason_codes", "true_range",
            "true_range_valid", "true_range_warmup_complete", "true_range_reason_codes",
            "atr_wilder_14", "atr_wilder_14_valid", "atr_wilder_14_warmup_complete",
            "atr_wilder_14_reason_codes", "roc_close_12_pct", "roc_close_12_pct_valid",
            "roc_close_12_pct_warmup_complete", "roc_close_12_pct_reason_codes", "obv",
            "obv_valid", "obv_warmup_complete", "obv_reason_codes", "typical_price",
            "typical_price_valid", "typical_price_warmup_complete",
            "typical_price_reason_codes", "cci_20", "cci_20_valid", "cci_20_warmup_complete",
            "cci_20_reason_codes", "mfi_14", "mfi_14_valid", "mfi_14_warmup_complete",
            "mfi_14_reason_codes", "plus_di_14", "plus_di_14_valid",
            "plus_di_14_warmup_complete", "plus_di_14_reason_codes", "minus_di_14",
            "minus_di_14_valid", "minus_di_14_warmup_complete", "minus_di_14_reason_codes",
            "dx_14", "dx_14_valid", "dx_14_warmup_complete", "dx_14_reason_codes",
            "adx_wilder_14", "adx_wilder_14_valid", "adx_wilder_14_warmup_complete",
            "adx_wilder_14_reason_codes",
        ),
    },
    {
        "field_owner_stage": "S4_SIGNALS",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "signal_profile_id", "signal_profile_version", "signal_schema_id",
            "signal_schema_version", "signal_schema_ref", "sig_rsi_mr_d",
            "sig_rsi_mr_d_valid", "sig_rsi_mr_d_reason_codes", "sig_macd_momentum_d",
            "sig_macd_momentum_d_valid", "sig_macd_momentum_d_reason_codes",
            "sig_bollinger_mr_d", "sig_bollinger_mr_d_valid",
            "sig_bollinger_mr_d_reason_codes", "sig_stoch_mr_d", "sig_stoch_mr_d_valid",
            "sig_stoch_mr_d_reason_codes", "sig_cci_mr_d", "sig_cci_mr_d_valid",
            "sig_cci_mr_d_reason_codes", "sig_mfi_mr_d", "sig_mfi_mr_d_valid",
            "sig_mfi_mr_d_reason_codes", "sig_obv_momentum_d", "sig_obv_momentum_d_valid",
            "sig_obv_momentum_d_reason_codes", "sig_roc_momentum_d",
            "sig_roc_momentum_d_valid", "sig_roc_momentum_d_reason_codes",
            "state_ma200_trend_d", "state_ma200_trend_d_valid",
            "state_ma200_trend_d_reason_codes", "state_ema50_trend_d",
            "state_ema50_trend_d_valid", "state_ema50_trend_d_reason_codes",
            "state_atr_relative_d", "state_atr_relative_d_valid",
            "state_atr_relative_d_reason_codes", "state_adx_strength_d",
            "state_adx_strength_d_valid", "state_adx_strength_d_reason_codes",
            "score_rsi_mr_c", "score_rsi_mr_c_valid", "score_rsi_mr_c_reason_codes",
            "score_macd_momentum_c", "score_macd_momentum_c_valid",
            "score_macd_momentum_c_reason_codes", "score_bollinger_mr_c",
            "score_bollinger_mr_c_valid", "score_bollinger_mr_c_reason_codes",
            "score_stoch_mr_c", "score_stoch_mr_c_valid", "score_stoch_mr_c_reason_codes",
            "score_cci_mr_c", "score_cci_mr_c_valid", "score_cci_mr_c_reason_codes",
            "score_mfi_mr_c", "score_mfi_mr_c_valid", "score_mfi_mr_c_reason_codes",
            "score_obv_momentum_c", "score_obv_momentum_c_valid",
            "score_obv_momentum_c_reason_codes", "score_roc_momentum_c",
            "score_roc_momentum_c_valid", "score_roc_momentum_c_reason_codes",
            "score_ma200_trend_c", "score_ma200_trend_c_valid",
            "score_ma200_trend_c_reason_codes", "score_ema50_trend_c",
            "score_ema50_trend_c_valid", "score_ema50_trend_c_reason_codes",
            "score_atr_relative_c", "score_atr_relative_c_valid",
            "score_atr_relative_c_reason_codes", "score_adx_strength_c",
            "score_adx_strength_c_valid", "score_adx_strength_c_reason_codes",
        ),
    },
    {
        "field_owner_stage": "S5_REGIMES",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "regime_raw", "regime_effective", "regime_candidate", "regime_candidate_count",
            "regime_transition_flag", "regime_transition_from", "regime_transition_to",
            "ma200_slope_1440_pct", "trend_strength", "trend_strength_valid",
            "trend_strength_reason_codes", "volatility_relative", "volatility_relative_valid",
            "volatility_relative_reason_codes", "regime_model_id", "regime_model_version",
            "regime_schema_id", "regime_schema_version", "regime_schema_ref", "regime_valid",
            "regime_reason_codes",
        ),
    },
    {
        "field_owner_stage": "S6_GATES",
        "leakage_class": "POINT_IN_TIME",
        "fields": (
            "allow_long", "allow_short", "data_gate_pass", "gate_state",
            "gate_reason_codes_long", "gate_reason_codes_short", "gate_profile_id",
            "gate_profile_version", "gate_schema_id", "gate_schema_version",
            "gate_schema_ref", "gate_valid", "gate_evaluated_at",
        ),
    },
    {
        "field_owner_stage": "S7_LABELS",
        "leakage_class": "FUTURE_OUTCOME",
        "fields": (
            "label_profile_id", "label_profile_version", "label_schema_id",
            "label_schema_version", "label_schema_ref", "horizon_registry_id",
            "horizon_registry_version", "cost_profile_id", "cost_profile_version",
            "barrier_profile_id", "barrier_profile_version",
            "label_reason_code_registry_version", "label_numeric_profile_id",
            "label_numeric_profile_version", "label_horizon_bars_h001",
            "label_available_at_h001", "fwd_cc_valid_h001", "fwd_cc_reason_codes_h001",
            "fwd_cc_label_segment_id_h001", "fwd_cc_long_ret_h001", "fwd_cc_short_ret_h001",
            "fwd_cc_log_ret_h001", "fwd_cc_short_log_ret_h001", "fwd_noc_valid_h001",
            "fwd_noc_reason_codes_h001", "fwd_noc_label_segment_id_h001",
            "fwd_noc_long_ret_h001", "fwd_noc_short_ret_h001",
            "fwd_noc_long_net_proxy_fee_rt_0004_h001",
            "fwd_noc_short_net_proxy_fee_rt_0004_h001", "fwd_excursion_valid_h001",
            "fwd_excursion_reason_codes_h001", "fwd_excursion_label_segment_id_h001",
            "fwd_long_mfe_h001", "fwd_long_mae_h001", "fwd_short_mfe_h001",
            "fwd_short_mae_h001", "fwd_long_mfe_first_bar_h001",
            "fwd_long_mae_first_bar_h001", "fwd_short_mfe_first_bar_h001",
            "fwd_short_mae_first_bar_h001", "label_cc_direction_valid_h001",
            "label_cc_direction_reason_codes_h001", "label_cc_direction_segment_id_h001",
            "label_cc_long_direction_h001", "label_cc_short_direction_h001",
            "label_noc_direction_valid_h001", "label_noc_direction_reason_codes_h001",
            "label_noc_direction_segment_id_h001", "label_noc_long_direction_h001",
            "label_noc_short_direction_h001",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h001",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h001", "barrier_valid_h001",
            "barrier_reason_codes_h001", "barrier_label_segment_id_h001",
            "barrier_long_outcome_tp050_sl020_h001", "barrier_short_outcome_tp050_sl020_h001",
            "barrier_long_first_hit_bar_tp050_sl020_h001",
            "barrier_short_first_hit_bar_tp050_sl020_h001",
            "barrier_long_first_hit_time_tp050_sl020_h001",
            "barrier_short_first_hit_time_tp050_sl020_h001", "label_horizon_bars_h005",
            "label_available_at_h005", "fwd_cc_valid_h005", "fwd_cc_reason_codes_h005",
            "fwd_cc_label_segment_id_h005", "fwd_cc_long_ret_h005", "fwd_cc_short_ret_h005",
            "fwd_cc_log_ret_h005", "fwd_cc_short_log_ret_h005", "fwd_noc_valid_h005",
            "fwd_noc_reason_codes_h005", "fwd_noc_label_segment_id_h005",
            "fwd_noc_long_ret_h005", "fwd_noc_short_ret_h005",
            "fwd_noc_long_net_proxy_fee_rt_0004_h005",
            "fwd_noc_short_net_proxy_fee_rt_0004_h005", "fwd_excursion_valid_h005",
            "fwd_excursion_reason_codes_h005", "fwd_excursion_label_segment_id_h005",
            "fwd_long_mfe_h005", "fwd_long_mae_h005", "fwd_short_mfe_h005",
            "fwd_short_mae_h005", "fwd_long_mfe_first_bar_h005",
            "fwd_long_mae_first_bar_h005", "fwd_short_mfe_first_bar_h005",
            "fwd_short_mae_first_bar_h005", "label_cc_direction_valid_h005",
            "label_cc_direction_reason_codes_h005", "label_cc_direction_segment_id_h005",
            "label_cc_long_direction_h005", "label_cc_short_direction_h005",
            "label_noc_direction_valid_h005", "label_noc_direction_reason_codes_h005",
            "label_noc_direction_segment_id_h005", "label_noc_long_direction_h005",
            "label_noc_short_direction_h005",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h005",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h005", "barrier_valid_h005",
            "barrier_reason_codes_h005", "barrier_label_segment_id_h005",
            "barrier_long_outcome_tp050_sl020_h005", "barrier_short_outcome_tp050_sl020_h005",
            "barrier_long_first_hit_bar_tp050_sl020_h005",
            "barrier_short_first_hit_bar_tp050_sl020_h005",
            "barrier_long_first_hit_time_tp050_sl020_h005",
            "barrier_short_first_hit_time_tp050_sl020_h005", "label_horizon_bars_h015",
            "label_available_at_h015", "fwd_cc_valid_h015", "fwd_cc_reason_codes_h015",
            "fwd_cc_label_segment_id_h015", "fwd_cc_long_ret_h015", "fwd_cc_short_ret_h015",
            "fwd_cc_log_ret_h015", "fwd_cc_short_log_ret_h015", "fwd_noc_valid_h015",
            "fwd_noc_reason_codes_h015", "fwd_noc_label_segment_id_h015",
            "fwd_noc_long_ret_h015", "fwd_noc_short_ret_h015",
            "fwd_noc_long_net_proxy_fee_rt_0004_h015",
            "fwd_noc_short_net_proxy_fee_rt_0004_h015", "fwd_excursion_valid_h015",
            "fwd_excursion_reason_codes_h015", "fwd_excursion_label_segment_id_h015",
            "fwd_long_mfe_h015", "fwd_long_mae_h015", "fwd_short_mfe_h015",
            "fwd_short_mae_h015", "fwd_long_mfe_first_bar_h015",
            "fwd_long_mae_first_bar_h015", "fwd_short_mfe_first_bar_h015",
            "fwd_short_mae_first_bar_h015", "label_cc_direction_valid_h015",
            "label_cc_direction_reason_codes_h015", "label_cc_direction_segment_id_h015",
            "label_cc_long_direction_h015", "label_cc_short_direction_h015",
            "label_noc_direction_valid_h015", "label_noc_direction_reason_codes_h015",
            "label_noc_direction_segment_id_h015", "label_noc_long_direction_h015",
            "label_noc_short_direction_h015",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h015",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h015", "barrier_valid_h015",
            "barrier_reason_codes_h015", "barrier_label_segment_id_h015",
            "barrier_long_outcome_tp050_sl020_h015", "barrier_short_outcome_tp050_sl020_h015",
            "barrier_long_first_hit_bar_tp050_sl020_h015",
            "barrier_short_first_hit_bar_tp050_sl020_h015",
            "barrier_long_first_hit_time_tp050_sl020_h015",
            "barrier_short_first_hit_time_tp050_sl020_h015", "label_horizon_bars_h060",
            "label_available_at_h060", "fwd_cc_valid_h060", "fwd_cc_reason_codes_h060",
            "fwd_cc_label_segment_id_h060", "fwd_cc_long_ret_h060", "fwd_cc_short_ret_h060",
            "fwd_cc_log_ret_h060", "fwd_cc_short_log_ret_h060", "fwd_noc_valid_h060",
            "fwd_noc_reason_codes_h060", "fwd_noc_label_segment_id_h060",
            "fwd_noc_long_ret_h060", "fwd_noc_short_ret_h060",
            "fwd_noc_long_net_proxy_fee_rt_0004_h060",
            "fwd_noc_short_net_proxy_fee_rt_0004_h060", "fwd_excursion_valid_h060",
            "fwd_excursion_reason_codes_h060", "fwd_excursion_label_segment_id_h060",
            "fwd_long_mfe_h060", "fwd_long_mae_h060", "fwd_short_mfe_h060",
            "fwd_short_mae_h060", "fwd_long_mfe_first_bar_h060",
            "fwd_long_mae_first_bar_h060", "fwd_short_mfe_first_bar_h060",
            "fwd_short_mae_first_bar_h060", "label_cc_direction_valid_h060",
            "label_cc_direction_reason_codes_h060", "label_cc_direction_segment_id_h060",
            "label_cc_long_direction_h060", "label_cc_short_direction_h060",
            "label_noc_direction_valid_h060", "label_noc_direction_reason_codes_h060",
            "label_noc_direction_segment_id_h060", "label_noc_long_direction_h060",
            "label_noc_short_direction_h060",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h060",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h060", "barrier_valid_h060",
            "barrier_reason_codes_h060", "barrier_label_segment_id_h060",
            "barrier_long_outcome_tp050_sl020_h060", "barrier_short_outcome_tp050_sl020_h060",
            "barrier_long_first_hit_bar_tp050_sl020_h060",
            "barrier_short_first_hit_bar_tp050_sl020_h060",
            "barrier_long_first_hit_time_tp050_sl020_h060",
            "barrier_short_first_hit_time_tp050_sl020_h060", "label_horizon_bars_h240",
            "label_available_at_h240", "fwd_cc_valid_h240", "fwd_cc_reason_codes_h240",
            "fwd_cc_label_segment_id_h240", "fwd_cc_long_ret_h240", "fwd_cc_short_ret_h240",
            "fwd_cc_log_ret_h240", "fwd_cc_short_log_ret_h240", "fwd_noc_valid_h240",
            "fwd_noc_reason_codes_h240", "fwd_noc_label_segment_id_h240",
            "fwd_noc_long_ret_h240", "fwd_noc_short_ret_h240",
            "fwd_noc_long_net_proxy_fee_rt_0004_h240",
            "fwd_noc_short_net_proxy_fee_rt_0004_h240", "fwd_excursion_valid_h240",
            "fwd_excursion_reason_codes_h240", "fwd_excursion_label_segment_id_h240",
            "fwd_long_mfe_h240", "fwd_long_mae_h240", "fwd_short_mfe_h240",
            "fwd_short_mae_h240", "fwd_long_mfe_first_bar_h240",
            "fwd_long_mae_first_bar_h240", "fwd_short_mfe_first_bar_h240",
            "fwd_short_mae_first_bar_h240", "label_cc_direction_valid_h240",
            "label_cc_direction_reason_codes_h240", "label_cc_direction_segment_id_h240",
            "label_cc_long_direction_h240", "label_cc_short_direction_h240",
            "label_noc_direction_valid_h240", "label_noc_direction_reason_codes_h240",
            "label_noc_direction_segment_id_h240", "label_noc_long_direction_h240",
            "label_noc_short_direction_h240",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h240",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h240", "barrier_valid_h240",
            "barrier_reason_codes_h240", "barrier_label_segment_id_h240",
            "barrier_long_outcome_tp050_sl020_h240", "barrier_short_outcome_tp050_sl020_h240",
            "barrier_long_first_hit_bar_tp050_sl020_h240",
            "barrier_short_first_hit_bar_tp050_sl020_h240",
            "barrier_long_first_hit_time_tp050_sl020_h240",
            "barrier_short_first_hit_time_tp050_sl020_h240", "label_horizon_bars_h1440",
            "label_available_at_h1440", "fwd_cc_valid_h1440", "fwd_cc_reason_codes_h1440",
            "fwd_cc_label_segment_id_h1440", "fwd_cc_long_ret_h1440",
            "fwd_cc_short_ret_h1440", "fwd_cc_log_ret_h1440", "fwd_cc_short_log_ret_h1440",
            "fwd_noc_valid_h1440", "fwd_noc_reason_codes_h1440",
            "fwd_noc_label_segment_id_h1440", "fwd_noc_long_ret_h1440",
            "fwd_noc_short_ret_h1440", "fwd_noc_long_net_proxy_fee_rt_0004_h1440",
            "fwd_noc_short_net_proxy_fee_rt_0004_h1440", "fwd_excursion_valid_h1440",
            "fwd_excursion_reason_codes_h1440", "fwd_excursion_label_segment_id_h1440",
            "fwd_long_mfe_h1440", "fwd_long_mae_h1440", "fwd_short_mfe_h1440",
            "fwd_short_mae_h1440", "fwd_long_mfe_first_bar_h1440",
            "fwd_long_mae_first_bar_h1440", "fwd_short_mfe_first_bar_h1440",
            "fwd_short_mae_first_bar_h1440", "label_cc_direction_valid_h1440",
            "label_cc_direction_reason_codes_h1440", "label_cc_direction_segment_id_h1440",
            "label_cc_long_direction_h1440", "label_cc_short_direction_h1440",
            "label_noc_direction_valid_h1440", "label_noc_direction_reason_codes_h1440",
            "label_noc_direction_segment_id_h1440", "label_noc_long_direction_h1440",
            "label_noc_short_direction_h1440",
            "label_noc_long_net_proxy_fee_rt_0004_direction_h1440",
            "label_noc_short_net_proxy_fee_rt_0004_direction_h1440", "barrier_valid_h1440",
            "barrier_reason_codes_h1440", "barrier_label_segment_id_h1440",
            "barrier_long_outcome_tp050_sl020_h1440",
            "barrier_short_outcome_tp050_sl020_h1440",
            "barrier_long_first_hit_bar_tp050_sl020_h1440",
            "barrier_short_first_hit_bar_tp050_sl020_h1440",
            "barrier_long_first_hit_time_tp050_sl020_h1440",
            "barrier_short_first_hit_time_tp050_sl020_h1440",
        ),
    },
    {
        "field_owner_stage": "S0_SOURCE",
        "leakage_class": "PROVENANCE_METADATA",
        "fields": (
            "retrieved_at_utc", "source_file_name", "source_byte_sha256", "source_revision",
            "source_format", "source_location", "license_or_terms_ref",
        ),
    },
    {
        "field_owner_stage": "S8_EXPORT",
        "leakage_class": "AUDIT_METADATA",
        "fields": (
            "manifest_schema_id", "manifest_schema_version", "manifest_schema_ref",
            "manifest_type", "manifest_id", "created_at_utc", "dataset_id",
            "dataset_artifact_set_id", "build_id", "run_id", "artifact_id", "relative_path",
            "media_type", "schema_id", "schema_version", "schema_ref",
            "schema_fingerprint_sha256", "field_registry_sha256", "view_allowlist_sha256",
            "byte_sha256", "semantic_sha256", "physical_layout_sha256", "publication_status",
        ),
    },
)

FIELD_REGISTRY: dict[str, object] = {
    "field_registry_id": FIELD_REGISTRY_ID,
    "field_registry_version": FIELD_REGISTRY_VERSION,
    "groups": [
        {
            "field_owner_stage": group["field_owner_stage"],
            "leakage_class": group["leakage_class"],
            "fields": list(group["fields"]),
        }
        for group in FIELD_REGISTRY_GROUPS
    ],
}

# Derived, not independently normative: one (owner_stage, leakage_class) per
# field name, mechanically resolved from FIELD_REGISTRY_GROUPS. A field
# appearing in more than one group is a registry defect and fails closed.
FIELD_OWNER_STAGE: dict[str, str] = {}
FIELD_LEAKAGE_CLASS: dict[str, str] = {}
for _group in FIELD_REGISTRY_GROUPS:
    for _field in _group["fields"]:
        if _field in FIELD_OWNER_STAGE:
            raise FieldRegistryError(
                f"field {_field!r} has more than one registry entry"
            )
        FIELD_OWNER_STAGE[_field] = _group["field_owner_stage"]
        FIELD_LEAKAGE_CLASS[_field] = _group["leakage_class"]
del _group, _field

FIELD_REGISTRY_SHA256 = canonical_sha256(FIELD_REGISTRY)


def resolve_field(field_name: str) -> tuple[str, str]:
    """Return (field_owner_stage, leakage_class) for a registered field.

    Raises ``FieldRegistryError`` for any field absent from the registry
    (fail-closed: an unknown field never silently resolves).
    """
    if not isinstance(field_name, str) or not field_name:
        raise FieldRegistryError("field_name must be a non-empty string")
    if field_name not in FIELD_OWNER_STAGE:
        raise FieldRegistryError(f"unregistered field: {field_name!r}")
    return FIELD_OWNER_STAGE[field_name], FIELD_LEAKAGE_CLASS[field_name]


__all__ = [
    "FIELD_LEAKAGE_CLASS",
    "FIELD_OWNER_STAGE",
    "FIELD_REGISTRY",
    "FIELD_REGISTRY_GROUPS",
    "FIELD_REGISTRY_ID",
    "FIELD_REGISTRY_SHA256",
    "FIELD_REGISTRY_VERSION",
    "resolve_field",
]
