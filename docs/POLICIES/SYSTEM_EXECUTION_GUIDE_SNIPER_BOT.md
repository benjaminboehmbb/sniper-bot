# System & Execution Guide — Sniper-Bot

**Quelle:** *Python for Algorithmic Trading – From Idea to Cloud Deployment* (Yves Hilpisch)  
**Zweck:** Leitlinie für Systemarchitektur, Backtesting-Integration, Paper-Trading
und Live-Execution im Sniper-Bot-Projekt.

**Abgrenzung:**  
Dieses Dokument regelt **HOW** (Umsetzung & Betrieb).  
Forschungs- und Validierungsregeln sind in **AFML_ALIGNMENT_SNIPER_BOT.md** verbindlich geregelt.  
Bei Konflikten gilt **AFML** vorrangig.

---

## Grundprinzip (verbindlich)

> System- und Execution-Qualität entscheidet über Überlebensfähigkeit im Live-Betrieb.  
> Architektur, Logging und State-Management sind **keine Optimierungsdetails**, sondern Pflicht.

---

## 1. Zielarchitektur (verbindlich)

### 1.1 Schichtenmodell
Der Sniper-Bot folgt strikt einer Schichtenarchitektur:

- **Data Layer**
  - Rohdaten, Normalisierung, Feature-Berechnung
  - Zeitstempel strikt UTC, monoton
- **Strategy Layer**
  - Signale, Filter, Kombinatorik
  - Keine I/O-Logik
- **Execution Layer**
  - Order-Erstellung, Sizing, Slippage, Fees
  - Keine Strategie-Entscheidungen
- **Monitoring & State**
  - Logs, Health-Checks, Kill-Switches
  - Read-only für Strategien

**Regel:** Keine Querverweise zwischen den Schichten.

---

## 2. Backtesting-Integration

### 2.1 Event-Driven vs. Vectorized
- **Event-Driven:** bevorzugt für Realismus, State-Handling, Live-Nähe
- **Vectorized:** erlaubt für schnelle Vorselektion (Research), nie als finale Validierung

**Regel:**  
Finale Aussagen über Robustheit **nur** aus event-driven Simulationen.

---

### 2.2 Determinismus & Reproduzierbarkeit
- Feste Seeds (wo relevant)
- Versionierte Daten
- Klare Run-IDs
- Kein impliziter globaler State

**Regel:** Jeder Run muss reproduzierbar sein oder verworfen werden.

---

## 3. Paper-Trading (L1)

### 3.1 Ziel
- Validierung von Execution, Latenz, State-Drift
- **Nicht** Performance-Maximierung

### 3.2 Pflichtbestandteile
- Realistische Fees
- Konservative Slippage
- Order-Rejections
- Positions- & Kapital-Tracking
- Kill-Switch-Logik

**Regel:**  
Ein System, das Paper-Trading nicht stabil übersteht, geht **niemals** live.

---

## 4. Live-Execution (L2+)

### 4.1 Trennung der Umgebungen
- Research ≠ Backtest ≠ Paper ≠ Live
- Eigene Configs & Logs je Umgebung

### 4.2 Schutzmechanismen (verbindlich)
- Max Drawdown Guards
- Trade-Frequenz-Limits
- Heartbeat / Watchdog
- Manueller Kill-Switch

**Regel:** Sicherheit schlägt Rendite.

---

## 5. Logging & Observability

### 5.1 Logging-Grundsätze
- Append-only Logs
- Strukturierte Logs (Zeit, Level, Kategorie, State-ID)
- Keine stillen Fehler

### 5.2 State-Management
- Explizite State-Files (z. B. JSONL)
- Kein impliziter In-Memory-State ohne Persistenz

**Regel:**  
Was nicht geloggt ist, ist nicht passiert.

---

## 6. Deployment (bewusst minimal)

### 6.1 Grundsätze
- Keine Cloud-Optimierung vor stabiler L1-Phase
- Lokale Reproduzierbarkeit vor Skalierung
- Einfache Start-/Stop-Prozesse

### 6.2 Nicht-Ziele (vorerst)
- Auto-Scaling
- Hochverfügbarkeits-Cluster
- Multi-Asset-Live-Trading

---

## 7. Explizite No-Gos

- Backtests ohne sauberes State-Handling
- Live-Betrieb ohne Paper-Phase
- Execution-Logik in Strategien
- „Schnelle Fixes“ ohne Dokumentation

---

## Abschlussregel

> Ein Trading-System scheitert selten an der Strategie,  
> sondern fast immer an **Execution, State oder Monitoring**.

---

**Dokumentenstatus:** FINAL  
**Änderungen:** Nur mit expliziter Begründung und Versionsupdate erlaubt.
