# P28H TIME-STOP EXECUTION AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Audit repeated or invalid time-stop close events in live_logs/l1_paper.log.

## Summary

time_stop_anomalies: 36

final_reconstructed_position: FLAT

## Time Stop Counts

- SHORT_TIME_STOP_HIT: 63
- LONG_TIME_STOP_HIT: 39

## Time Stop Position Before/After Counts

- reason=SHORT_TIME_STOP_HIT position_before=SHORT position_after=FLAT: 63
- reason=LONG_TIME_STOP_HIT position_before=LONG position_after=FLAT: 39

## Action/Reason Counts Relevant To Time Stops

- action=CLOSE_SHORT reason=SHORT_TIME_STOP_HIT: 63
- action=CLOSE_LONG reason=LONG_TIME_STOP_HIT: 39

## Anomaly Samples

### Anomaly 1

type: repeated_or_invalid_long_time_stop_close

tick: 5

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:29.673934Z seq=28 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-387c115d743f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=4
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:29.905181Z seq=35 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-17d4f0c699df action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=5
```

### Anomaly 2

type: repeated_or_invalid_long_time_stop_close

tick: 6

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:29.905181Z seq=35 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-17d4f0c699df action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=5
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:30.905679Z seq=42 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e796c14cc9c7 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=6
```

### Anomaly 3

type: repeated_or_invalid_long_time_stop_close

tick: 7

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:30.905679Z seq=42 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e796c14cc9c7 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=6
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:31.905254Z seq=49 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1c8745f86f2c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=7
```

### Anomaly 4

type: repeated_or_invalid_long_time_stop_close

tick: 8

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:31.905254Z seq=49 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1c8745f86f2c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=7
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:32.934071Z seq=56 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-be6541723117 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=8
```

### Anomaly 5

type: repeated_or_invalid_long_time_stop_close

tick: 9

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:32.934071Z seq=56 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-be6541723117 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=8
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:33.937140Z seq=63 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-18fbeae96669 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=9
```

### Anomaly 6

type: repeated_or_invalid_long_time_stop_close

tick: 10

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:33.937140Z seq=63 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-18fbeae96669 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=9
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:34.935672Z seq=70 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1b38ba7e1a95 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=10
```

### Anomaly 7

type: repeated_or_invalid_long_time_stop_close

tick: 11

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:34.935672Z seq=70 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-1b38ba7e1a95 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=10
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:35.941628Z seq=77 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8c7f6168cca6 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=11
```

### Anomaly 8

type: repeated_or_invalid_long_time_stop_close

tick: 12

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:35.941628Z seq=77 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8c7f6168cca6 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=11
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:36.955358Z seq=84 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6fcc2e2ba079 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=12
```

### Anomaly 9

type: repeated_or_invalid_long_time_stop_close

tick: 13

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:36.955358Z seq=84 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6fcc2e2ba079 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=12
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:38.025359Z seq=91 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-f546c0c5039d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=13
```

### Anomaly 10

type: repeated_or_invalid_long_time_stop_close

tick: 14

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:38.025359Z seq=91 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-f546c0c5039d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=13
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:39.002866Z seq=98 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12892cadce9a action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=14
```

### Anomaly 11

type: repeated_or_invalid_long_time_stop_close

tick: 15

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:39.002866Z seq=98 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12892cadce9a action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=14
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:40.000229Z seq=105 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12e55dbee39d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=15
```

### Anomaly 12

type: repeated_or_invalid_long_time_stop_close

tick: 16

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:40.000229Z seq=105 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-12e55dbee39d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=15
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:41.025483Z seq=112 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8daf0f39facf action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=16
```

### Anomaly 13

type: repeated_or_invalid_long_time_stop_close

tick: 17

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:41.025483Z seq=112 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-8daf0f39facf action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=16
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:42.058387Z seq=119 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6117fcf42142 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=17
```

### Anomaly 14

type: repeated_or_invalid_long_time_stop_close

tick: 18

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:42.058387Z seq=119 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6117fcf42142 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=17
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:43.055808Z seq=126 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e2f64bce90c5 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=18
```

### Anomaly 15

type: repeated_or_invalid_long_time_stop_close

tick: 19

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:43.055808Z seq=126 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-e2f64bce90c5 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=18
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:44.051845Z seq=133 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d1954b765d0c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=19
```

### Anomaly 16

type: repeated_or_invalid_long_time_stop_close

tick: 20

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:44.051845Z seq=133 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d1954b765d0c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=19
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:45.075750Z seq=140 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40bc11fc679c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=20
```

### Anomaly 17

type: repeated_or_invalid_long_time_stop_close

tick: 21

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:45.075750Z seq=140 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40bc11fc679c action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=20
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:46.055452Z seq=147 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6e28b886d88f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=21
```

### Anomaly 18

type: repeated_or_invalid_long_time_stop_close

tick: 22

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:46.055452Z seq=147 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-6e28b886d88f action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=21
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:47.091504Z seq=154 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-88a0830176d1 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=22
```

### Anomaly 19

type: repeated_or_invalid_long_time_stop_close

tick: 23

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:47.091504Z seq=154 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-88a0830176d1 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=22
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:48.074789Z seq=161 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-5c664a8811db action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=23
```

### Anomaly 20

type: repeated_or_invalid_long_time_stop_close

tick: 24

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:48.074789Z seq=161 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-5c664a8811db action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=23
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:49.068267Z seq=168 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d2d083ced291 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=24
```

### Anomaly 21

type: repeated_or_invalid_long_time_stop_close

tick: 25

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:49.068267Z seq=168 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-d2d083ced291 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=24
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:48.921335Z seq=175 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-ada7e5fbb1e9 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=25
```

### Anomaly 22

type: repeated_or_invalid_long_time_stop_close

tick: 26

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:48.921335Z seq=175 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-ada7e5fbb1e9 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=25
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:49.899677Z seq=182 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-a70fa0154510 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=26
```

### Anomaly 23

type: repeated_or_invalid_long_time_stop_close

tick: 27

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:49.899677Z seq=182 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-a70fa0154510 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=26
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:50.920058Z seq=189 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-ffc810511a1b action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=27
```

### Anomaly 24

type: repeated_or_invalid_long_time_stop_close

tick: 28

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:50.920058Z seq=189 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-ffc810511a1b action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=27
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:51.930194Z seq=196 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40ff7a734be3 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=28
```

### Anomaly 25

type: repeated_or_invalid_long_time_stop_close

tick: 29

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:51.930194Z seq=196 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-40ff7a734be3 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=28
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:52.922469Z seq=203 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-23d01fbb2244 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=29
```

### Anomaly 26

type: repeated_or_invalid_long_time_stop_close

tick: 30

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:52.922469Z seq=203 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-23d01fbb2244 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=29
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:53.931915Z seq=210 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-4b38fc4263d3 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=30
```

### Anomaly 27

type: repeated_or_invalid_long_time_stop_close

tick: 31

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:53.931915Z seq=210 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-4b38fc4263d3 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=30
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:54.907887Z seq=217 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-04513f8a9a1e action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=31
```

### Anomaly 28

type: repeated_or_invalid_long_time_stop_close

tick: 32

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:54.907887Z seq=217 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-04513f8a9a1e action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=31
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:55.936970Z seq=224 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-433e7c5740fe action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=32
```

### Anomaly 29

type: repeated_or_invalid_long_time_stop_close

tick: 33

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:55.936970Z seq=224 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-433e7c5740fe action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=32
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:56.943600Z seq=231 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-24bd4ed65cc9 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=33
```

### Anomaly 30

type: repeated_or_invalid_long_time_stop_close

tick: 34

actual_reconstructed_position: FLAT

position_before_log: LONG

position_after_log: FLAT

last_open_line:

```text
timestamp_utc=2026-06-05T14:46:27.853255Z seq=21 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-aaa03633ede0 action=OPEN_LONG entry_price=106081.61 entry_timestamp_utc=2025-11-10_05:56:00+00:00 executed=1 position_after=LONG position_before=FLAT reason=BUY_FROM_FLAT side_after=long tick=3
```

last_close_line:

```text
timestamp_utc=2026-06-05T14:46:56.943600Z seq=231 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-24bd4ed65cc9 action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=33
```

anomaly_line:

```text
timestamp_utc=2026-06-05T14:46:57.941639Z seq=238 category=L5 event=execution severity=INFO system_state_id=L1P-111ed6321d0 intent_id=IN-766b675cc69d action=CLOSE_LONG entry_price= entry_timestamp_utc= executed=1 position_after=FLAT position_before=LONG reason=LONG_TIME_STOP_HIT side_after= tick=34
```

## Interpretation

Time-stop close anomalies were detected by sequential reconstruction.

The log reports position_before as LONG/SHORT while the reconstructed stream state is already FLAT.

This suggests either repeated time-stop close emission after a position has already closed, or a reconstruction/state-source mismatch.

Next step: inspect live_l1/core/execution.py time-stop branch before patching.

## Result

Status: PASS
