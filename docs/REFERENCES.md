# Sniper-Bot – Reference Literature & Design Alignment

## Zweck dieses Dokuments

Dieses Dokument definiert die **maßgeblichen Referenzwerke** für den Aufbau, die Bewertung und die Weiterentwicklung des Sniper-Bot-Projekts.

Die Bücher dienen **nicht** als Rezept- oder Strategiequellen, sondern als:
- konzeptionelle Leitplanken,
- Qualitäts- und Robustheitsreferenzen,
- Begründungsbasis für Design- und Architekturentscheidungen.

Wichtig:
> Kein Buch erzeugt per se einen „Edge“.  
> Alle Inhalte werden **kritisch geprüft**, **konkret operationalisiert** und nur dann übernommen, wenn sie mit den GS-Prinzipien (Reproduzierbarkeit, Robustheit, Realismus) vereinbar sind.

---

## Kategorie A – Kernreferenzen (verbindlich / GS-relevant)

Diese Werke gelten als **Standard-Referenzen** für Architektur, Backtesting-Integrität und ML-Hygiene.

### 1. Yves Hilpisch – *Python for Algorithmic Trading*
**Rolle im Projekt:** Architektur & Systemdesign

**Relevanz für Sniper-Bot:**
- End-to-End-Sicht: Idee → Daten → Backtest → Strategie → Deployment
- Saubere Trennung von:
  - Data Ingestion
  - Signal/Strategy Logic
  - Execution & Accounting
- Event-basierte Backtesting-Denke als Grundlage für Live-Nähe

**Abgeleitete Prinzipien (Policy-relevant):**
- Klare Modulgrenzen (kein „Spaghetti-Backtest“)
- Explizite Zeit- und Entscheidungsreihenfolge
- Backtests müssen strukturell live-fähig sein

---

### 2. Ernest P. Chan – *Quantitative Trading* / *Algorithmic Trading*
**Rolle im Projekt:** Realismus- & Risiko-Referenz

**Relevanz für Sniper-Bot:**
- Fokus auf typische Fehlerquellen:
  - Look-ahead Bias
  - Data Snooping
  - Unterschätzte Transaktionskosten
- Betonung einfacher, robuster Strategien statt komplexer Overfitting-Modelle

**Abgeleitete Prinzipien:**
- Backtest ≠ Live → Abweichungen sind normal und müssen erklärbar sein
- Transaktionskosten & Slippage sind Pflichtbestandteile
- Performance ohne robuste OOS-Bestätigung ist wertlos

---

### 3. Marcos López de Prado – *Advances in Financial Machine Learning*
**Rolle im Projekt:** Methodische Absicherung & ML-Hygiene

**Relevanz für Sniper-Bot:**
- Formale Behandlung von Overfitting in Finanzzeitreihen
- Konzepte wie:
  - Purged Cross-Validation
  - Embargo
  - Deflated Sharpe Ratio
- Klare Trennung zwischen Signalqualität und Backtest-Glück

**Abgeleitete Prinzipien:**
- Jede datengetriebene Selektion ist potenziell überfit
- Cross-Validation für Finanzdaten ist **nicht optional**
- ML-Modelle werden nur akzeptiert, wenn Leakage systematisch ausgeschlossen ist

---

### 4. Stefan Jansen – *Machine Learning for Algorithmic Trading*
**Rolle im Projekt:** ML-Workflow & Research-Standard

**Relevanz für Sniper-Bot:**
- End-to-End ML4T-Workflow:
  - Daten → Features → Labels → Modell → Strategie → Backtest
- Umfassende Behandlung von:
  - Feature Engineering
  - Zeitreihen-CV (Purging/Embargo)
  - Modellvergleich & Diagnose
- Klare Warnungen vor überzogenen ML-Erwartungen

**Abgeleitete Prinzipien:**
- ML ist ein Werkzeug, kein Ersatz für Marktverständnis, ML-Komponenten dürfen nur eingeführt werden, wenn ein regelbasierter GS-Baseline-Ansatz existiert, gegen den sie gemessen werden.
- Feature-Qualität ist wichtiger als Modell-Komplexität
- ML-Strategien müssen denselben GS-Gates unterliegen wie regelbasierte Strategien

---

## Kategorie B – Ergänzende Referenzen (optional, später)

Diese Werke können später hinzugezogen werden, sind aber **nicht Teil des aktuellen Kernfundaments**.

### Statistische & Portfolio-Theorie
- Samit Ahlawat – *Statistical Quantitative Methods in Finance*  
  → relevant für spätere Portfolio- und Risk-Modelle

### Generative & Research-Automation
- Stefan Jansen – *Generative AI for Trading for Asset Management*  
  → relevant für Phase B (Research-Automatisierung, Analyse-Unterstützung)

---

## Kategorie C – Explizit nicht als Referenz zugelassen

Die folgenden Literaturtypen gelten **nicht** als Referenz für den Sniper-Bot:

- „Cheat Codes“, „Ultimate Profit“, „Beginner Bot“-Literatur
- Bücher mit Marketing-Fokus statt methodischer Absicherung
- Werke ohne klare Behandlung von:
  - Overfitting
  - Backtest-Bias
  - Transaktionskosten
  - OOS-Validierung

Begründung:
> Diese Inhalte erhöhen das Risiko systematischer Fehlannahmen und widersprechen dem GS-Qualitätsanspruch.

---

## Grundsatz für Implementierungen

Kein Konzept aus einem Referenzwerk wird übernommen, ohne dass:
1. der konkrete Nutzen für den Sniper-Bot benannt ist,
2. ein klarer Implementierungs- oder Prüfpunkt definiert ist,
3. die Kompatibilität mit bestehenden GS-Komponenten geprüft wurde.

Bücher liefern **Begründungen**, nicht **Autorität**.

---

## Status

Dieses Dokument wird versioniert gepflegt und bei:
- Architektur-Änderungen
- Einführung neuer Modellklassen
- Übergang zu Live-Stufen (L1+)
- Gültig für: GS-Phase (Pre-Live), Stand Architektur 2026-01

aktualisiert.

Letzte Aktualisierung: 2026-01
