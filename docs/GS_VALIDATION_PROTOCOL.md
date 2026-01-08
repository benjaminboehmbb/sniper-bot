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

