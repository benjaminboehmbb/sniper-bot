# P36 LIVE L1 TIMING V2 MIGRATION REVIEW

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Review all references required before migrating Live L1 from 5m timing seed v1 to explicit-direction seed v2.

## Search Patterns

- btcusdt_5m_long_timing_core_v1.csv
- btcusdt_5m_timing_core_v2.csv
- seeds_5m_csv
- L1_SEEDS_5M_CSV
- compute_5m_timing_vote

## Matches

```text
live_l1/core/loop.py:26: from live_l1.core.timing_5m import compute_5m_timing_vote
live_l1/core/loop.py:51:     seeds_5m_csv: str
live_l1/core/loop.py:205:         seeds_5m_csv=os.environ.get(
live_l1/core/loop.py:207:             "seeds/5m/btcusdt_5m_long_timing_core_v1.csv",
live_l1/core/loop.py:748:         seeds_5m_csv=str(cfg.seeds_5m_csv),
live_l1/core/loop.py:826:                 "seeds_5m_csv": cfg.seeds_5m_csv,
live_l1/core/loop.py:881:             vote_v1 = compute_5m_timing_vote(
live_l1/core/loop.py:882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
live_l1/core/timing_5m.py:172: def compute_5m_timing_vote(
live_l1/core/timing_5m.py:224:     vote = compute_5m_timing_vote(
live_l1/core/timing_5m_v2.py:43: def compute_5m_timing_vote_v2(
live_l1/io/valid.py:26:         "seeds_5m_csv",
live_l1/io/valid.py:42:     seeds_5m_csv = str(cfg.seeds_5m_csv).strip()
live_l1/io/valid.py:54:     if not seeds_5m_csv:
live_l1/io/valid.py:55:         raise ValueError("seeds_5m_csv must not be empty")
live_l1/io/valid.py:75:     if os.path.isabs(seeds_5m_csv):
live_l1/io/valid.py:76:         seeds_path = seeds_5m_csv
live_l1/io/valid.py:78:         seeds_path = os.path.join(repo_root, seeds_5m_csv)
live_l1/io/valid.py:81:         raise ValueError(f"seeds_5m_csv not found: {seeds_path}")
live_l1/tools/monitor_runtime.py:220:     seeds_5m_csv: str,
live_l1/tools/monitor_runtime.py:251:         seeds_5m_csv=seeds_5m_csv,
live_l1/tools/monitor_runtime.py:415:     parser.add_argument("--seeds-5m-csv", default="seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
live_l1/tools/monitor_runtime.py:431:         seeds_5m_csv=args.seeds_5m_csv,
live_l1/tools/operational_health_report.py:66:     parser.add_argument("--seeds-5m-csv", default="seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
live_l1/tools/operational_health_report.py:84:         seeds_5m_csv=args.seeds_5m_csv,
live_l1/tools/safe_launch.py:37:     parser.add_argument("--seeds-5m-csv", default=os.environ.get("SEEDS_5M_CSV", "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"))
live_l1/tools/safe_launch.py:68:             seeds_5m_csv=args.seeds_5m_csv,
live_l1/tools/startup_validator.py:60:     seeds_5m_csv: str,
live_l1/tools/startup_validator.py:66:     seeds_path = repo_root / seeds_5m_csv
live_l1/tools/startup_validator.py:118:         default=os.environ.get("SEEDS_5M_CSV", "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"),
live_l1/tools/startup_validator.py:126:         seeds_5m_csv=args.seeds_5m_csv,
live_l1/tools/startup_validator.py:133:     print("seeds_5m_csv:", args.seeds_5m_csv)
live_l1/tools/test_monitor_failure_injection.py:48:         str(PROJECT_ROOT / "seeds" / "5m" / "btcusdt_5m_long_timing_core_v1.csv"),
scripts/run_live_l1_paper.py:137:     if args.seeds_5m_csv:
scripts/run_live_l1_paper.py:138:         os.environ["SEEDS_5M_CSV"] = args.seeds_5m_csv
tools/l1c_smoke_test.py:32: DEFAULT_LONG_SEEDS = "seeds/5m/btcusdt_5m_long_timing_core_v1.csv"
tools/p30_audit_5m_timing_bias.py:13: SEEDS = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
tools/p32_create_5m_timing_seed_v2.py:10: SRC = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
tools/p32_create_5m_timing_seed_v2.py:11: OUT = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
tools/p35_timing_bias_regression_audit.py:14: from live_l1.core.timing_5m import compute_5m_timing_vote
tools/p35_timing_bias_regression_audit.py:16: V1 = Path("seeds/5m/btcusdt_5m_long_timing_core_v1.csv")
tools/p35_timing_bias_regression_audit.py:17: V2 = Path("seeds/5m/btcusdt_5m_timing_core_v2.csv")
tools/p35_timing_bias_regression_audit.py:22:     vote = compute_5m_timing_vote(
tools/p36_timing_v2_migration_review.py:10:     "btcusdt_5m_long_timing_core_v1.csv",
tools/p36_timing_v2_migration_review.py:11:     "btcusdt_5m_timing_core_v2.csv",
tools/p36_timing_v2_migration_review.py:12:     "seeds_5m_csv",
tools/p36_timing_v2_migration_review.py:13:     "L1_SEEDS_5M_CSV",
tools/p36_timing_v2_migration_review.py:14:     "compute_5m_timing_vote",
tools/test_p34_strict_timing_direction.py:13: from live_l1.core.timing_5m import compute_5m_timing_vote
tools/test_p34_strict_timing_direction.py:25:         vote = compute_5m_timing_vote(
tools/test_timing_5m_v2_minimal.py:15:     compute_5m_timing_vote_v2,
tools/test_timing_5m_v2_minimal.py:40:     vote = compute_5m_timing_vote_v2(
tools/test_timing_5m_v2_minimal.py:63:     vote = compute_5m_timing_vote_v2(
tools/test_timing_5m_v2_minimal.py:86:     vote = compute_5m_timing_vote_v2(
docs/5M_TIMING_CORE_LONG.md:40: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/L1_5M_TIMING_INTEGRATION_DESIGN.md:20: - seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/L1_5M_TIMING_INTEGRATION_DESIGN.md:44: - Fuer LONG: evaluiere alle Seeds aus btcusdt_5m_long_timing_core_v1.csv
docs/LIVE_DESIGN_L1C_ACCEPTANCE_CHECKLIST.md:64: 3. `compute_5m_timing_vote(...)`:
docs/LIVE_DESIGN_L1D_TIMING_CORE_V2.md:50: TimingVote = compute_5m_timing_vote_v2(
docs/inventory/P25B_CANDIDATE_CONTENT_INSPECTION_2026-06-06.md:348: - compute_5m_timing_vote_v2
docs/inventory/P25B_CANDIDATE_CONTENT_INSPECTION_2026-06-06.md:434:     compute_5m_timing_vote_v2,
docs/review/P26_LIVE_L1_ARCHITECTURE_DEPENDENCY_REVIEW_2026-06-06.md:180: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/review/P26_LIVE_L1_ARCHITECTURE_DEPENDENCY_REVIEW_2026-06-06.md:197: -> compute_5m_timing_vote
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:17: path: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:87: 172: def compute_5m_timing_vote(
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:102: 224:     vote = compute_5m_timing_vote(
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:117: 26: from live_l1.core.timing_5m import compute_5m_timing_vote
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:119: 51:     seeds_5m_csv: str
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:122: 205:         seeds_5m_csv=os.environ.get(
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:123: 207:             "seeds/5m/btcusdt_5m_long_timing_core_v1.csv",
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:126: 748:         seeds_5m_csv=str(cfg.seeds_5m_csv),
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:127: 826:                 "seeds_5m_csv": cfg.seeds_5m_csv,
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:128: 881:             vote_v1 = compute_5m_timing_vote(
docs/review/P30_5M_TIMING_LAYER_BIAS_AUDIT_2026-06-06.md:129: 882:                 seeds_csv=os.path.join(repo_root, cfg.seeds_5m_csv),
docs/review/P31_5M_TIMING_DIRECTION_MODEL_DESIGN_2026-06-06.md:27: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/review/P31_5M_TIMING_DIRECTION_MODEL_DESIGN_2026-06-06.md:135: compute_5m_timing_vote should:
docs/review/P31_5M_TIMING_DIRECTION_MODEL_DESIGN_2026-06-06.md:169: seeds/5m/btcusdt_5m_timing_core_v2.csv
docs/review/P31_5M_TIMING_DIRECTION_MODEL_DESIGN_2026-06-06.md:183: seeds/5m/btcusdt_5m_timing_core_v2.csv
docs/review/P32_5M_TIMING_SEED_V2_CREATION_2026-06-06.md:13: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/review/P32_5M_TIMING_SEED_V2_CREATION_2026-06-06.md:17: seeds/5m/btcusdt_5m_timing_core_v2.csv
docs/review/P35_TIMING_BIAS_REGRESSION_AUDIT_2026-06-06.md:13: v1_seed: seeds/5m/btcusdt_5m_long_timing_core_v1.csv
docs/review/P35_TIMING_BIAS_REGRESSION_AUDIT_2026-06-06.md:15: v2_seed: seeds/5m/btcusdt_5m_timing_core_v2.csv
```

## Current Migration Assessment

The default runtime path must be checked in live_l1/core/loop.py.

The v2 seed file exists and is tracked in Git.

Runtime migration should only change the default seed path from v1 to v2 if no other hidden runtime references exist.

## Required Before P37

- Confirm v1 references are documentation-only or legacy.
- Confirm active runtime default still points to v1 or environment override.
- Confirm v2 seed file is tracked.
- Do not add short seeds in this migration step.

## P36 Result

Status: PASS
