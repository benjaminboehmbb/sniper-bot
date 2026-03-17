# LIVE DESIGN — L0 FAILURE MODES & KILL SWITCHES
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: VERBINDLICH (L0)

---

## Grundprinzip

Bei Unsicherheit gilt:
STOP > WAIT > EXIT > SHUTDOWN

Kein Auto-Recovery.
Kein Retry.
Keine Optimierung.

---

## Failure-Mode-Klassen

### FM-1 — Datenintegrität

Beispiele:
- fehlende Kerzen
- NaN / Inf
- ungültige Signalwerte
- Zeitstempel nicht monoton

Reaktion:
- keine neuen Trades
- Status: DEGRADED

---

### FM-2 — Entscheidungsanomalien

Beispiele:
- widersprüchliche Intents
- extreme Entscheidungsfrequenz
- ungültige Richtungswechsel

Reaktion:
- Order blockieren
- Anomaly Counter erhöhen
- bei Schwelle: GLOBAL PAUSE

---

### FM-3 — Execution-Fehler

Beispiele:
- Order-Reject
- Timeout
- Partial Fill
- Rate-Limit

Reaktion:
- sofortiges Stop-Trading
- manuelles Reset erforderlich

---

### FM-4 — Systemische Ressourcen

Beispiele:
- CPU/RAM-Limit
- Clock Drift
- Prozess hängt
- Disk voll

Reaktion:
- Process Kill
- Safe Shutdown
- kein Auto-Restart

---

### FM-5 — Regelverletzung

Beispiele:
- Tagesverlust überschritten
- Trade-Limit überschritten
- Guard deaktiviert

Reaktion:
- Hard Kill-Switch
- explizite Freigabe notwendig

---

## Kill-Switch-Hierarchie

- KS-1: Soft Kill (keine neuen Orders)
- KS-2: Hard Kill (Trading-Loop stop)
- KS-3: Emergency Kill (Process Exit)

Ein Kill-Level darf nicht automatisch sinken.

---

## Verbotenes Verhalten

- Auto-Recovery
- Retry-Logik
- dynamische Limits
- Silent Fail
- Fehlerheuristik
