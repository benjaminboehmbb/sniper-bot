# V12B AUTOMATIC EXPERIMENT GENERATOR - COMPLETED

Date: 2026-06-20

## Objective

Convert V12A research campaigns into concrete experiment specifications.

## Architectural Position

Archive

to Trade Inspector

to V9 Research Intelligence

to V10 Validation Orchestrator

to V11 Automated Learning

to V12A Research Campaign Manager

to V12B Automatic Experiment Generator

## Input

- v12a_research_campaigns.csv

## Outputs

- v12b_experiment_specs.csv
- v12b_experiment_manifest.csv
- V12B_AUTOMATIC_EXPERIMENT_GENERATOR_REPORT_YYYY-MM-DD.md

## Guardrails

V12B is specification-only.

It does not:

- change strategy logic
- run replay
- start runtime
- trade live
- modify existing databases

## Result

Smoke test completed successfully.

V12B generated experiment specifications from V12A research campaigns.

## Status

Completed.
