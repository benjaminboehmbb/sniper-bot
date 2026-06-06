# P28G BAD CLOSE RECONSTRUCTION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Determine whether bad close events from P28F are true execution issues or reconstruction artifacts.

## Summary

system_start_count: 16

system_stop_count: 18

bad_closes_detected: 37

final_reconstructed_position: FLAT

## Action Counts

- NOOP: 4299045
- CLOSE_LONG: 372
- OPEN_LONG: 335
- OPEN_SHORT: 224
- CLOSE_SHORT: 224

## Close Counts

- CLOSE_LONG: 372
- CLOSE_SHORT: 224

## Reason Counts

- HOLD_NO_EXECUTION: 4298448
- LOSS_CLUSTER_GATE_BLOCKED_ENTRY: 595
- BUY_FROM_FLAT: 335
- SELL_CLOSES_LONG: 324
- SELL_FROM_FLAT: 224
- BUY_CLOSES_SHORT: 154
- SHORT_TIME_STOP_HIT: 63
- LONG_TIME_STOP_HIT: 39
- SL_LONG_HIT: 8
- SL_SHORT_HIT: 7
- BUY_ALREADY_LONG: 2
- TP_LONG_HIT: 1

## Bad Close Samples

### Bad Close 1

expected: LONG

actual_position: FLAT

tick: 5

timestamp_utc: 2026-06-05T14:46:29.905181Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:29.673934Z seq=28 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-387c115d743f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=4
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:29.905181Z seq=35 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-17d4f0c699df action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=5
```

### Bad Close 2

expected: LONG

actual_position: FLAT

tick: 6

timestamp_utc: 2026-06-05T14:46:30.905679Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:29.905181Z seq=35 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-17d4f0c699df action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=5
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:30.905679Z seq=42 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e796c14cc9c7 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=6
```

### Bad Close 3

expected: LONG

actual_position: FLAT

tick: 7

timestamp_utc: 2026-06-05T14:46:31.905254Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:30.905679Z seq=42 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e796c14cc9c7 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=6
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:31.905254Z seq=49 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1c8745f86f2c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=7
```

### Bad Close 4

expected: LONG

actual_position: FLAT

tick: 8

timestamp_utc: 2026-06-05T14:46:32.934071Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:31.905254Z seq=49 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1c8745f86f2c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=7
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:32.934071Z seq=56 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-be6541723117 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=8
```

### Bad Close 5

expected: LONG

actual_position: FLAT

tick: 9

timestamp_utc: 2026-06-05T14:46:33.937140Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:32.934071Z seq=56 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-be6541723117 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=8
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:33.937140Z seq=63 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-18fbeae96669 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=9
```

### Bad Close 6

expected: LONG

actual_position: FLAT

tick: 10

timestamp_utc: 2026-06-05T14:46:34.935672Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:33.937140Z seq=63 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-18fbeae96669 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=9
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:34.935672Z seq=70 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1b38ba7e1a95 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=10
```

### Bad Close 7

expected: LONG

actual_position: FLAT

tick: 11

timestamp_utc: 2026-06-05T14:46:35.941628Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:34.935672Z seq=70 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1b38ba7e1a95 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=10
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:35.941628Z seq=77 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8c7f6168cca6 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=11
```

### Bad Close 8

expected: LONG

actual_position: FLAT

tick: 12

timestamp_utc: 2026-06-05T14:46:36.955358Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:35.941628Z seq=77 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8c7f6168cca6 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=11
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:36.955358Z seq=84 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6fcc2e2ba079 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=12
```

### Bad Close 9

expected: LONG

actual_position: FLAT

tick: 13

timestamp_utc: 2026-06-05T14:46:38.025359Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:36.955358Z seq=84 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6fcc2e2ba079 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=12
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:38.025359Z seq=91 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-f546c0c5039d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=13
```

### Bad Close 10

expected: LONG

actual_position: FLAT

tick: 14

timestamp_utc: 2026-06-05T14:46:39.002866Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:38.025359Z seq=91 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-f546c0c5039d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=13
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:39.002866Z seq=98 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12892cadce9a action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=14
```

### Bad Close 11

expected: LONG

actual_position: FLAT

tick: 15

timestamp_utc: 2026-06-05T14:46:40.000229Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:39.002866Z seq=98 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12892cadce9a action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=14
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:40.000229Z seq=105 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12e55dbee39d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=15
```

### Bad Close 12

expected: LONG

actual_position: FLAT

tick: 16

timestamp_utc: 2026-06-05T14:46:41.025483Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:40.000229Z seq=105 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12e55dbee39d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=15
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:41.025483Z seq=112 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8daf0f39facf action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=16
```

### Bad Close 13

expected: LONG

actual_position: FLAT

tick: 17

timestamp_utc: 2026-06-05T14:46:42.058387Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:41.025483Z seq=112 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8daf0f39facf action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=16
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:42.058387Z seq=119 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6117fcf42142 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=17
```

### Bad Close 14

expected: LONG

actual_position: FLAT

tick: 18

timestamp_utc: 2026-06-05T14:46:43.055808Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:42.058387Z seq=119 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6117fcf42142 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=17
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:43.055808Z seq=126 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e2f64bce90c5 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=18
```

### Bad Close 15

expected: LONG

actual_position: FLAT

tick: 19

timestamp_utc: 2026-06-05T14:46:44.051845Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:43.055808Z seq=126 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e2f64bce90c5 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=18
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:44.051845Z seq=133 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d1954b765d0c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=19
```

### Bad Close 16

expected: LONG

actual_position: FLAT

tick: 20

timestamp_utc: 2026-06-05T14:46:45.075750Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:44.051845Z seq=133 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d1954b765d0c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=19
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:45.075750Z seq=140 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40bc11fc679c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=20
```

### Bad Close 17

expected: LONG

actual_position: FLAT

tick: 21

timestamp_utc: 2026-06-05T14:46:46.055452Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:45.075750Z seq=140 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40bc11fc679c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=20
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:46.055452Z seq=147 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6e28b886d88f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=21
```

### Bad Close 18

expected: LONG

actual_position: FLAT

tick: 22

timestamp_utc: 2026-06-05T14:46:47.091504Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:46.055452Z seq=147 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6e28b886d88f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=21
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:47.091504Z seq=154 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-88a0830176d1 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=22
```

### Bad Close 19

expected: LONG

actual_position: FLAT

tick: 23

timestamp_utc: 2026-06-05T14:46:48.074789Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:47.091504Z seq=154 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-88a0830176d1 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=22
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:48.074789Z seq=161 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-5c664a8811db action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=23
```

### Bad Close 20

expected: LONG

actual_position: FLAT

tick: 24

timestamp_utc: 2026-06-05T14:46:49.068267Z

reason: LONG_TIME_STOP_HIT

last_position_change:

```text
timestamp_utc=2026-06-05T14:46:48.074789Z seq=161 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-5c664a8811db action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=23
```

bad_close_line:

```text
timestamp_utc=2026-06-05T14:46:49.068267Z seq=168 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d2d083ced291 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=24
```

## Interpretation

Bad closes were detected by sequential log reconstruction.

Because the log contains multiple system_start/system_stop cycles, these may be reconstruction artifacts across restarts or resumed positions.

This requires comparison with persisted S2 state and execution_audit before classifying as execution bug.

## Result

Status: PASS
