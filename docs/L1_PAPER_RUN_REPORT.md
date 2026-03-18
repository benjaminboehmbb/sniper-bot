# L1 PAPER RUN REPORT – L1-F (Execution Validation)

## Context
System: Sniper-Bot L1 Paper Trading  
Phase: L1-F Execution Validation  
Environment: WSL (AR15 / G15)  
Mode: Real (no TEST_BYPASS)

---

## Setup

- 1m intent generation active
- 5m timing vote active (seed: C02_rsi_stoch_08)
- Guards active
- Execution layer active (L5)
- TEST overrides disabled

---

## Run Configuration

- max_ticks: 200
- state_dir reset before run
- log file reset before run

Commands used:


rm -rf live_state
mkdir -p live_state
rm -f live_logs/l1_paper.log
python3 -m scripts.run_live_l1_paper --max-ticks 200


---

## Observations

### Entry Behavior

- At least one real trade executed:


action=OPEN_LONG
position_before=FLAT
position_after=LONG
tick=127


- Execution confirmed:
  - executed=1
  - correct state transition

---

### Post-Entry Behavior

- From tick ~127 to tick 200:


position_before=LONG
position_after=LONG
reason=HOLD_NO_EXECUTION


- No exit triggered during observed window

---

## Interpretation

- Entry pipeline works end-to-end:
  - L3 intent → guards → L5 execution → logging

- State persistence is stable:
  - Position remains consistent across ticks

- No unintended executions observed

- Exit logic is functional (verified in TEST mode),
  but not triggered in this specific real-data window

---

## Conclusion

L1-F (Execution Validation) is successfully completed.

Validated:
- OPEN_LONG (real)
- CLOSE_LONG (test mode)
- Position lifecycle
- Execution logging
- State consistency

Not yet observed in real mode:
- CLOSE_LONG

---

## Next Steps

- Run extended paper simulation (e.g., 1000+ ticks)
- Observe real exit behavior
- Proceed to L1-G (continuous observation phase)

---


## L1-G Observation Update (2026-03-18)

Extended real paper run showed:

- real OPEN_LONG observed
- no real CLOSE_LONG observed in the tested window
- multiple SELL raw intents occurred
- these SELL intents were converted to HOLD before execution

Observed pattern:
- intent_1m_raw=SELL
- intent_final=HOLD
- reason_code=GATE_BLOCK_SHORT
- frequently allow_long=1 and allow_short=0
- 5m vote remained long

Interpretation:
- execution layer is not the blocker
- real exits are currently suppressed by upstream gate/fusion logic
- this creates effective long-only holding behavior in the observed window

Conclusion:
L1-G observation confirms a system-level behavior:
exit starvation caused by gate/fusion policy, not by L5 execution failure.


## L1-H Update (2026-03-18) - Exit Policy A++

A++ was implemented and verified in real mode.

Policy:
- BUY remains gated by long permission / long confirmation
- SELL is allowed as EXIT from an existing LONG position
- exit is no longer blocked by long-biased 5m vote

Observed real behavior:
- OPEN_LONG occurred multiple times
- CLOSE_LONG occurred multiple times
- reason_code observed: EXIT_LONG_ON_1M_SELL
- execution observed: SELL_CLOSES_LONG

Conclusion:
Exit starvation issue is resolved for LONG positions.
Entry gating and exit handling are now decoupled.


## L1-I Update (2026-03-18) - Symmetric SHORT Exit

L1-I was implemented and verified in real mode.

Policy:
- BUY can close an existing SHORT position
- SELL can close an existing LONG position
- exit handling is now symmetric across both sides

Observed real behavior:
- OPEN_SHORT observed multiple times
- reason_code observed: EXIT_SHORT_ON_1M_BUY
- execution observed: BUY_CLOSES_SHORT
- CLOSE_SHORT observed multiple times

Conclusion:
Symmetric exit handling is now verified in real mode.
Entry gating and exit handling are fully decoupled for both LONG and SHORT.