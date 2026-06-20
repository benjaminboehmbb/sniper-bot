# Common Library Refactor (V9-V12)

Date: 2026-06-20

## Objective

Eliminate duplicated helper implementations across the complete
Trade Inspector pipeline (V9-V12) and replace them with a shared
Common Library.

## Scope

Shared modules:

- tools/trade_inspector/common/io.py
- tools/trade_inspector/common/utils.py
- tools/trade_inspector/common/ids.py
- tools/trade_inspector/common/__init__.py

Refactored modules:

### V9

- build_v9a_evidence_scoring.py
- build_v9b_evidence_stability.py
- build_v9c_strategy_opportunity_scoring.py
- build_v9d_cross_archive_consistency.py
- build_v9e_evidence_conflict_engine.py
- build_v9f_experiment_portfolio_optimizer.py
- build_v9g_research_decision_engine.py

### V10

- build_v10a_validation_planner.py
- build_v10b_validation_specification_generator.py
- build_v10c_validation_execution_scheduler.py
- build_v10d_validation_runner.py
- build_v10e_replay_validation_engine.py
- build_v10f_replay_execution_engine.py

### V11

- build_v11a_replay_result_evaluator.py
- build_v11b_validation_evidence_updater.py
- build_v11c_research_knowledge_base.py
- build_v11d_knowledge_consistency_engine.py
- build_v11e_knowledge_evolution_tracker.py
- build_v11f_hypothesis_prioritization_engine.py
- build_v11g_autonomous_learning_loop.py

### V12

- build_v12a_research_campaign_manager.py
- build_v12b_automatic_experiment_generator.py
- build_v12c_resource_runtime_planner.py
- build_v12d_campaign_executor.py
- build_v12e_cross_campaign_analyzer.py
- build_v12f_research_memory.py
- build_v12g_autonomous_research_director.py

## Compatibility fixes

The migration required several compatibility improvements:

- clamp() default parameters restored
- write_csv() unified fieldname interface
- pick() supports both:

  pick(row, "a", "b")

and legacy form:

  pick(row, ["a","b"])

- unified helper imports
- centralized CSV handling
- centralized utility functions

## Validation

Completed successfully:

- py_compile
- --help verification for every module
- V9 pipeline smoke test
- V10 pipeline smoke test
- V11 pipeline smoke test
- V12 pipeline smoke test

All completed successfully.

## Result

The complete V9-V12 Trade Inspector now shares a single Common Library.

Benefits:

- substantially less duplicated code
- easier maintenance
- consistent helper behavior
- improved long-term extensibility
- reduced future bug surface

Status:

COMPLETE
