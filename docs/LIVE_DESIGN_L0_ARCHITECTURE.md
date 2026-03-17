# LIVE DESIGN — L0 ARCHITECTURE
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die verbindliche Architektur der Live-Design-Phase L0.
Es beschreibt Systemgrenzen, Verantwortlichkeiten und Invarianten.
Es enthält **keine Implementierung** und **keine Optimierung**.

GS und Post-GS sind READ-ONLY und werden nicht verändert.

---

## L0-A — Systemgrenzen & Schichten

### Schichtenmodell

- L0: GS Foundation (READ-ONLY)
- L1: Policy / Decision Layer (Design only)
- L2: Live Adapter & Guards (Design only)
- L3: Execution / Exchange (Out of Scope)

### Grundsatz

GS beantwortet: „Was würde passieren?“  
Live beantwortet: „Was darf passieren?“

Diese Ebenen dürfen niemals vermischt werden.

---

## L0-A — Gold-Standard Foundation (READ-ONLY)

### Enthält

- engine/simtraderGS.py (Contract v1)
- GS-Strategien (FINAL / CANONICAL)
- GS- und Post-GS-Daten
- GS- und Post-GS-Ergebnisse

### Garantien

- deterministisch
- zustandslos
- keine Side-Effects
- keine externe Abhängigkeit
- keine Live-Kopplung

### Verbote

- kein Live-Code-Import
- kein Schreiben auf Disk
- keine ENV-Mutation
- keine semantische Wiederverwendung

---

## L0-A — GS Vertrags-Schnittstelle

### Input

- price_df: close + *_signal (-1 / 0 / +1)
- comb: dict[str, float]
- direction: long | short

### Output

- roi
- num_trades
- winrate
- sharpe
- pnl_sum
- avg_trade

Diese Signatur ist unveränderlich.

---

## L0-A — L1 Policy Layer

- übersetzt State → Intent
- trifft keine Order-Entscheidungen
- nutzt GS nur als Referenz
- ruft GS niemals live auf

---

## L0-A — L2 Adapter & Guards

- blockiert, verzögert oder stoppt Orders
- enthält Kill-Switches
- interpretiert keine Signale
- trifft keine Handelsentscheidungen

---

## L0-A — L3 Execution

- Broker / Exchange
- Orderbook
- Slippage
- Partial Fills

Nicht Teil von L0.

---

## Invariante

GS bleibt vollständig unberührt.
Live-Design darf GS nicht verändern, erweitern oder simulieren.
