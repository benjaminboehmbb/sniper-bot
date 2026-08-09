# Pre-IU-4 X1 Replay Dataset Evidence — 2026-08-09

## Status

**10,000-TICK X1 EVIDENCE CHAIN PASSED; EXECUTION-EXIT PARITY BLOCKED**

Branch: `codex/pre-iu4-x1-replay-dataset-2026-08-09`

Runner commit: `da8e3cab0af344623ad68d64180c2f93f40bb258`

IU-4 ENFORCED, Exchange, and Live remained locked. No Workstation, network,
exchange adapter, or active L1 startup path was used.

## Dataset and scope

- source: `price_data_with_signals_regime.csv`;
- complete source SHA-256:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- bounded slice: first 10,000 valid one-minute rows;
- interval: `2017-08-17T04:00:00Z` through `2017-08-24T02:39:00Z`;
- normalized slice SHA-256:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`;
- economics profile: `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`;
- throttle profile: `PEE_RATE_X1_REPLAY_OBSERVATION_001`.

The throttle profile is explicitly calibration-only and operationally
unapproved. Its high numeric limits only prevent the uncalibrated throttle
from distorting this observation run. It is not deployable and must never be
treated as a Live policy.

## Verified results

The established IU-3 SHADOW loop completed all 10,000 ticks with return code
zero. It produced 18 legacy transitions (`9 OPEN_LONG`, `9 CLOSE_LONG`), nine
PEE observations, zero sidecar issues, and exact integrated/sidecar observation
ID parity.

The IU-4 replay input and isolated dry-run completed all 10,000 records:

- replay intents: `9 BUY`, `9,991 HOLD`;
- outcomes: `1 OPEN_LONG`, `9,999 NOOP`, `0 REJECTED`;
- NOOP reasons: `9,991 PEE_IU4_HOLD`, `8 PEE_IU4_ALREADY_POSITIONED`;
- simulated atomic transactions: `1`;
- source atomic transaction sequence remained `0`;
- all 14 receipt chain/non-interference checks passed;
- tick sequence was exactly `1..10000`;
- replay-to-outcome source intent ID parity passed;
- source snapshot, WAL, and L1 log remained unchanged;
- all canonical manifest/evidence/receipt fingerprints revalidated.

Key whole-file hashes:

- IU-3 manifest:
  `39aed5315f069e01cf14051a92e702fe05a3f4b4bc371523c42914d82b451665`;
- L1 source log:
  `e794b01150fd10833f74a26ae3be3fd6ee40f36f972d3cda79865336f8e9a8b6`;
- replay JSONL:
  `0c033ff9bfad81ab2d36d87490068b07fb919e9525c1c59e1e11db910f828464`;
- replay input manifest:
  `ed172c723e34c318591f23964920df9f116c418520b4ba41454fc58c9914df74`;
- replay evidence:
  `c187779e15c13357525a77f10a866392b293667d5e45104e27b3a9cd880ef683`;
- pipeline receipt:
  `c5ca4fe3dc1669a20ff3463f7a6216d4fc1958443787fe034697c93a982408ba`;
- top-level run manifest:
  `ec19bd68ea04158fc064efad19df5e28e2a24094c181812918042100423d2425`.

## Discovered blocker

This is a valid intent replay, but not yet a complete legacy execution replay.
The input builder currently derives replay records from final intent events.
The nine legacy `CLOSE_LONG` actions in this dataset were autonomous time-stop
executions and are not represented as `SELL` intents. Therefore the isolated
IU-4 state stays LONG after the first entry, and the eight later BUY intents
correctly become `PEE_IU4_ALREADY_POSITIONED` NOOP outcomes.

The run must not be used as evidence of full legacy/IU-4 transition parity.
Before restart-scale or Workstation full-history replay, the replay contract
must represent and bind autonomous exit executions without converting ordinary
HOLD intents into exits.

## Verification

```text
tests.live_l1.test_run_paper_iu4_x1_replay_dataset
Ran 3 tests — OK

tests/live_l1 full suite
Ran 242 tests — OK

tests/regression full suite
Ran 170 tests — OK
```

The dataset run completed with exit code zero. Independent post-run SHA-256,
fingerprint, strict tick sequence, and replay/outcome ID checks all passed.

## Next gate

`IU4-AUTONOME-EXITS-REPLAY-VERTRAG FREIGEBEN`

That gate must extend the replay input contract and tests for autonomous
`CLOSE_LONG` execution events. Restart replay and Workstation full history
remain deferred until this parity blocker is closed.
