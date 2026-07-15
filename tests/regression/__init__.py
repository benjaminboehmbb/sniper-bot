"""TD-005 Automated Regression Test Suite.

Realizes the accepted TD-005 Implementation Specification V1.1
(docs/architecture/implementation/TD_005_AUTOMATED_REGRESSION_TEST_SUITE_IMPLEMENTATION_SPECIFICATION_V1_2026-07-14.md).

This package never modifies active run_engine/ runtime semantics and never
reads active Run Engine state through any channel other than
observation.NonInterferenceObserver (TD005-IU-009, TD005-II-004, TD005-II-011).
"""
