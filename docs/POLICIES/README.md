# Sniper-Bot — Policy Index

Dieses Verzeichnis enthält verbindliche Design- und Entscheidungsrichtlinien
für das Sniper-Bot-Projekt.


## Policies
Siehe `docs/POLICIES/README.md` für den Index aller verbindlichen Policies.


## Aktive Policies

1. **AFML Alignment**  
   Quelle: *Advances in Financial Machine Learning* (Marcos López de Prado)  
   Datei: `AFML_ALIGNMENT_SNIPER_BOT.md`  
   Geltungsbereich:  
   - Research-Design  
   - Backtesting-Integrität  
   - Overfitting-Vermeidung  
   - GS → L1 Entscheidungslogik


2. **ML Usage Guide**  
   Quelle: *Machine Learning for Algorithmic Trading* (Stefan Jansen)  
   Datei: `ML4T_USAGE_GUIDE_SNIPER_BOT.md`  
   Geltungsbereich:  
   - Einsatz von ML-Modellen  
   - Feature Engineering  
   - Meta-Modelle & Regime-Logik


3. **System & Execution Guide**  
   Quelle: *Python for Algorithmic Trading* (Yves Hilpisch)  
   Datei: `SYSTEM_EXECUTION_GUIDE_SNIPER_BOT.md`  
   Geltungsbereich:  
   - Systemarchitektur  
   - Backtesting-Integration  
   - Paper- & Live-Execution


4. **Strategy Realism Guide**  
   Quelle: *Quantitative Trading* (Ernest P. Chan)  
   Datei: `STRATEGY_REALISM_GUIDE_SNIPER_BOT.md`  
   Geltungsbereich:  
   - Strategie-Realismus (Kosten/Slippage/Turnover)  
   - Robustheit & Handelbarkeit  
   - Schutz vor Over-Engineering und unrealistischen Annahmen
## Timeframes (verbindlich)

Aktive Analyse-Timeframes im Projekt:

- 1m  (Primary Baseline, GS-Fundament)
- 5m  (Secondary Baseline, eingefuehrt 2026-01-19 nach validiertem Transfer-Test)

Regeln:
- Beide Timeframes unterliegen identischen GS-Policies.
- Jeder Timeframe hat eigene Seeds, eigene Baselines, eigene K3–K12 Pfade.
- Timeframe-Transfers muessen immer ueber Smoke-Baselines validiert werden (1m vs 5m Vergleich).

