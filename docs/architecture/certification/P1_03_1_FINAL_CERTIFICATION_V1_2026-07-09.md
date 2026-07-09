Create a new certification document:

docs/architecture/certification/P1_03_1_FINAL_CERTIFICATION_V1_2026-07-09.md

Purpose:
Officially close P1-03.1.

Include:

1. Scope
- Explicit entry basis handoff
- Removal of execution["entry_price"] mutation
- Explicit PnLEngine ownership
- Quantity validation hardening
- Removal of legacy update_pre_trade()

2. Implemented files
- run_engine/core/loop.py
- run_engine/core/pnl.py
- run_engine/core/position.py
- run_engine/core/trade_lifecycle.py

3. Validation summary
- compileall PASS
- Technical verification PASS
- End-to-end validation PASS
- LONG scenario PASS
- SHORT scenario PASS
- Partial Close PASS
- Full Close PASS
- Quantity validation PASS

4. Independent Reviews

Codex
- Technical implementation review completed
- Findings resolved or dispositioned

Claude
Final Verdict:
PASS WITH MINOR FINDINGS

State that:
- No Critical findings remain.
- No Major findings remain.
- Remaining findings are tracked in the Architecture Technical Debt Register.

5. Certification

State:

P1-03.1 is scientifically, architecturally and technically approved.

The implementation satisfies the Phase-1 acceptance criteria.

P1-03.1 is officially closed.

Development is approved to continue with P1-04.

Do not modify any other document.
Do not commit.
Do not push.