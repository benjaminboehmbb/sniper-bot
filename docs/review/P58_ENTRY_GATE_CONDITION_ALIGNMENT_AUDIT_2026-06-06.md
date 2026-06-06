# P58 ENTRY GATE CONDITION ALIGNMENT AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Check whether score sequences align with ma200/mfi/atr entry conditions in the P49 segment.

## Segment

live_logs/review_segments/p49_after_timing_signal_wiring_segment.log

## Rows

100

## Condition Counts

- sell_core_ok: 17
- buy_score_ok: 2

## Example Rows

- idx=65 score=-1 last3=[-1, -1, -1] ma200=-1 mfi=-1 atr=1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=66 score=-1 last3=[-1, -1, -1] ma200=-1 mfi=-1 atr=1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=67 score=-1 last3=[-1, -1, -1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=68 score=-1 last3=[-1, -1, -1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=69 score=-1 last3=[-1, -1, -1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=70 score=0 last3=[-1, -1, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=71 score=0 last3=[-1, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=72 score=0 last3=[0, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=73 score=0 last3=[0, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=74 score=0 last3=[0, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=75 score=0 last3=[0, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=76 score=0 last3=[0, 0, 0] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=none
- idx=77 score=1 last3=[0, 0, 1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=long
- idx=78 score=1 last3=[0, 1, 1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=long
- idx=79 score=1 last3=[1, 1, 1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=long
- idx=80 score=-1 last3=[1, 1, -1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=81 score=-1 last3=[1, -1, -1] ma200=-1 mfi=-1 atr=-1 buy_score_ok=False sell_score_ok=False buy_core_ok=False sell_core_ok=True intent_1m_raw=HOLD vote_5m_direction=short
- idx=87 score=4 last3=[4, 4, 4] ma200=-1 mfi=1 atr=-1 buy_score_ok=True sell_score_ok=False buy_core_ok=False sell_core_ok=False intent_1m_raw=HOLD vote_5m_direction=long
- idx=88 score=4 last3=[4, 4, 4] ma200=-1 mfi=1 atr=-1 buy_score_ok=True sell_score_ok=False buy_core_ok=False sell_core_ok=False intent_1m_raw=HOLD vote_5m_direction=long

## Interpretation

If score sequence conditions occur but full entry conditions remain zero, ma200/mfi alignment is the blocker.

## Result

Status: PASS
