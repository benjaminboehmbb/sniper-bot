## GS Contract v1 – Validation Status (frozen)

Stand: 2026-01-XX

### Core
- `engine/simtraderGS.py` ist der **Goldstandard**.
- Trading-Contract (Entry, Exit, Return, Index-Advance, Fee-Handling) ist **eingefroren**.
- Jede Aenderung am Core ist **verboten**, solange nicht alle GS-Validierungen erneut bestanden werden.

### Harte Invarianten
1. **Contract-SANITY**
   - Tool: `tools/gs_long_short_diagnostics.py`
   - Bedingung:  
     `SANITY (fee=0): DIAG vs BASE match == True`
   - Muss fuer **LONG und SHORT** gelten.
   - Verglichen werden mindestens: `roi`, `num_trades`.

2. **Determinismus**
   - Mehrfache Aufrufe von `evaluate_strategy()` mit identischem Input
     muessen bit-identische Ergebnisse liefern.

3. **Smoke Suite**
   - Tool: `tools/gs_smoke_suite.py`
   - Erwartung:  
     `[ok] GS SMOKE SUITE: ALL PASS`
   - Prueft:
     - Contract-Vollstaendigkeit
     - Determinismus
     - Fee-Monotonie
     - Regime-Gate-Effect und -Neutrality

### Regime v1 (Policy Layer)
- Regime v1 wird **ausschliesslich extern** als Wrapper-Gate angewandt.
- Regime beeinflusst **nur**, ob Trades erlaubt sind (`allow_long / allow_short`).
- Keine Aenderung an:
  - Entry-/Exit-Logik
  - Returns
  - Fees
  - Index-Advance
- Gate-Neutralitaet ist verpflichtend:
  - Gate deaktiviert ⇒ Ergebnisse **bit-identisch** zum ungefilterten Run.

### Konsequenz
- Schlaegt **eine** dieser Pruefungen fehl:
  - GS gilt als **invalid**
  - Alle Folgeanalysen sind **ungueltig**



## Regression Gate (mandatory)

**Ziel:**  
Sicherstellen, dass `engine/simtraderGS.py` und alle Policy-/Regime-Anbindungen
contract-treu, deterministisch und unverändert korrekt sind.

**Pflicht vor JEDEM Analyse- oder Policy-Run:**

```bash
python3 tools/gs_regression_gate.py \
  --csv data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1.csv \
  --rows 200000 \
  --offset 0 \
  --fee 0.0004 \
  --regime_col regime_v1

-> erwartetes ergebnis: 
[ok] Determinism PASS
[ok] Fee wiring PASS
[ok] Regime gate PASS
[ok] Policy check PASS
[ok] GS REGRESSION GATE: ALL PASS

bei FAIL sofort abbrechen!!!
nur bei ALL PASS darf weitergearbeitet werden!!!


## Run Guard (mandatory wrapper)

Vor JEDEM Run (Policy-Runner, WF, K-Runs) wird zuerst der Run-Guard ausgeführt.
Er kombiniert Input-Preflight + Regression-Gate und bricht bei Fehlern sofort ab.

```bash
python3 tools/gs_run_guard.py \
  --csv data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1.csv \
  --rows 200000 \
  --offset 0 \
  --fee 0.0004 \
  --require_signals rsi,macd,ma200 \
  --regime_cols regime_v1 \
  --regime_col regime_v1
