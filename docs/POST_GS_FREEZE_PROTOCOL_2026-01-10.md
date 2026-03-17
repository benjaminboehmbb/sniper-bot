# POST-GS FREEZE PROTOKOLL  
**Projekt:** Sniper-Bot  
**Phase:** Post-Gold-Standard (Post-GS)  
**Datum:** 2026-01-10  
**Status:** VERBINDLICH / READ-ONLY

---

## 1. Zweck des Freeze-Protokolls

Dieses Dokument definiert verbindlich, welche Projektbestandteile nach Abschluss der Post-GS-Phase **eingefroren** sind und **nicht mehr verändert** werden dürfen.

Ziel ist:
- Vermeidung von Regressionen
- Sicherstellung der Reproduzierbarkeit
- Klare Trennung zwischen **validiertem Fundament** und zukünftigen Entwicklungsphasen

---

## 2. Eingefrorene Kernkomponenten (READ-ONLY)

### 2.1 Trading-Engine

Folgende Datei ist **vollständig eingefroren**:


#engine/simtraderGS.py

Regeln:
- Keine Code-Änderungen
- Keine Parameter-Anpassungen
- Keine Reformatierungen
- Keine Refactorings

Änderungen sind **nur** nach expliziter Aufhebung dieses Protokolls zulässig.

---

### 2.2 Gold-Standard Strategien


#strategies/GS/LONG_FINAL_CANONICAL/
#strategies/GS/SHORT_FINAL/


Regeln:
- Keine neuen Strategien
- Keine Gewichtungsänderungen
- Keine Neuselektion
- Keine erneute Auswertung

Diese Ordner repräsentieren den **finalen GS-Zustand**.

---

### 2.3 GS-Daten (Preis + Signale)


#data/btcusdt_1m_2026-01-07/simtraderGS/
#data/ethusdt_1m_postGS/simtraderGS/



Regeln:
- Keine Neuaggregation
- Keine Signalanpassungen
- Keine Regime-Neuberechnung
- Keine Datenbereinigung

Diese Daten sind **kanonisch**.

---

## 3. Eingefrorene Ergebnisordner


#results/GS/
#results/POST_GS/



Regeln:
- Keine Überschreibung bestehender CSVs
- Keine Neuberechnung
- Nur Archivierung oder Kopie erlaubt

---

## 4. Erlaubte Operationen nach Freeze

Erlaubt sind ausschließlich:

- **Lesender Zugriff** (Analyse, Dokumentation)
- **Archivierung** (Verschieben in Archive)
- **Kopieren** für neue Entwicklungszweige
- **Meta-Auswertungen**, die keine Daten verändern

---

## 5. Explizit verbotene Operationen

Nicht erlaubt sind:

- Änderung von `simtraderGS.py`
- Neuberechnung von GS- oder Post-GS-Ergebnissen
- Vermischung von GS/Post-GS-Daten mit neuen Runs
- „Kleine Fixes“ oder „nur kurz testen“

Jede dieser Aktionen stellt einen **Protokollbruch** dar.

---

## 6. Aufhebung des Freeze

Eine Aufhebung dieses Freeze-Protokolls ist **nur zulässig**, wenn:

1. Ein neues Projektziel definiert wurde  
2. Ein neues Dokument erstellt wurde (`FREEZE_LIFT_*.md`)  
3. Der alte Zustand archiviert wurde  

Ohne diese drei Punkte bleibt der Freeze verbindlich.

---

## 7. Verbindlicher Status

Mit Erstellung dieses Dokuments gilt:

- Der **GS- und Post-GS-Zustand ist abgeschlossen**
- Alle zukünftigen Arbeiten bauen **kopierend**, nicht verändernd darauf auf
- Der Projektzustand ist **langfristig reproduzierbar**

---
