# PROJECT STATE AFTER POST-GS  
**Projekt:** Sniper-Bot  
**Datum:** 2026-01-10  
**Status:** VERBINDLICHER REFERENZPUNKT

---

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt den **finalen, validierten Projektzustand** nach Abschluss des Gold-Standards (GS) und der vollständigen Post-GS-Validierungsphase (H1–H5).

Es dient als:
- Referenz für zukünftige Entwicklungsphasen
- Schutz vor impliziten Annahmen
- Einstiegspunkt für neue Chats, neue Maschinen oder zukünftige Erweiterungen

---

## 2. Was ist bewiesen (Status: JA)

Die folgenden Eigenschaften gelten als **nachgewiesen**:

### 2.1 Systemische Robustheit
- GS-Fundament ist stabil
- Keine strukturellen Artefakte
- Erwartungskonformes Verhalten unter Stress

### 2.2 Kosten- & Execution-Tauglichkeit
- Realistische Fees und Slippage führen nicht zum Systemkollaps
- Schadenbegrenzung durch Regime-Controller wirksam
- Keine Null-Trade- oder Exploit-Effekte

### 2.3 Übertragbarkeit
- Zeitframe-Transfer (1m → 5m/15m) tragfähig
- Asset-Transfer (BTC → ETH) technisch und statistisch valide
- Keine Annahme universeller Symmetrie

### 2.4 Regime-Controller
- Entry-Gate (`allow_long == 1`) wirkt defensiv
- Reduziert Risiko in ungünstigen Marktphasen
- Optimiert nicht, sondern stabilisiert

---

## 3. Was ist bewusst NICHT bewiesen (Status: NEIN)

Folgende Punkte sind **explizit offen** und gelten als **nicht untersucht**:

- Optimale Parametrisierung
- Maximale Rendite
- Multi-Asset-Portfolios
- Short-Side-Optimierung
- Machine Learning / Adaptive Modelle
- Live-Order-Execution

Diese Punkte erfordern **eigene Projektphasen**.

---

## 4. Was ist verboten ohne neues Mandat

Ohne explizite Neudefinition des Projektziels sind **nicht erlaubt**:

- Änderungen an `simtraderGS.py`
- Neuberechnung von GS- oder Post-GS-Ergebnissen
- Vermischung von GS/Post-GS mit neuen Experimenten
- „Kleine Anpassungen“ oder implizite Optimierungen

Jede dieser Aktionen stellt einen **Bruch des Projektzustands** dar.

---

## 5. Aktueller Projektmodus

**Modus:**  
> *Validiertes Fundament – bereit für Live-Design*

Das Projekt befindet sich **nicht mehr** in der Forschungs- oder Explorationsphase.

---

## 6. Zulässige nächste Phasen (Auswahl)

Die folgenden Phasen sind **prinzipiell zulässig**, aber **noch nicht gestartet**:

- Live-Design L0 (Architektur, Guardrails)
- Live-Design L1 (Paper Trading)
- Risiko- & Kapitalmanagement
- Monitoring- & Fail-Safe-Design

Der Start jeder Phase erfordert:
- eigenes Ziel
- eigenes Dokument
- klare Abbruchkriterien

---

## 7. Verbindlicher Status

Mit diesem Dokument gilt:

- Der Projektzustand ist **klar definiert**
- Alle künftigen Arbeiten müssen sich explizit darauf beziehen
- Rückschritte oder implizite Änderungen sind ausgeschlossen

---
#jetzt (11.1.26) test beobachtungszeitraum 48h
L1 OBSERVATION WINDOW STARTED
Start (UTC): 2026-01-11T08:45:00Z
Duration: 48h
Reference Commit: 32a45e5
Mode: L1 Paper Trading
Rules: No code changes, react only on live_l1_alert.flag
Success Criteria: 0 unexplained alerts
