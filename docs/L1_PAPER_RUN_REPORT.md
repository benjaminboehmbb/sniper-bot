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

## Status

L1-F: COMPLETE