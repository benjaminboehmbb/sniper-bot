# LIVE_DESIGN_L2_MINIMAL_ARCHITECTURE.md

## Zweck

Dieses Dokument beschreibt die minimale Architektur von L2.
L2 dient ausschließlich der Entscheidungsfreigabe (ALLOW / BLOCK) für bestehende
GS-Strategien und greift nicht aktiv in den Live-Betrieb ein.

Keine Implementierung, keine Ausführung, kein Auto-Handel.

---

## 1. Positionierung im Gesamtsystem

L2 liegt logisch zwischen:

- L1 (Paper Trading Betrieb, Guards, Persistenz)
- GS (Gold-Standard-Strategien, READ-ONLY)

L2 ist:
- passiv
- advisory
- deterministisch
- rückstandslos deaktivierbar

---

## 2. Eingaben (Inputs)

L2 arbeitet ausschließlich mit READ-ONLY-Daten:

### 2.1 Strategische Inputs
- GS-Strategien (FINAL, READ-ONLY)
  - LONG_FINAL_CANONICAL
  - SHORT_FINAL

### 2.2 Marktkontext
- aktuelle Marktdaten (Snapshot / Fenster)
- Regime-Informationen (aus GS-kompatiblen Labels)

### 2.3 Betriebszustand
- ausgewählte L1-States (z. B. Risk-Status)
- Health-Status von L1 (indirekt, kein Eingriff)

---

## 3. Verarbeitungslogik (konzeptionell)

L2 führt eine rein bewertende Logik aus:

1. Kontextprüfung
   - passt die GS-Strategie zum aktuellen Markt-/Regime-Zustand?

2. Konsistenzprüfung
   - keine Abweichung zwischen GS-Annahmen und Live-Situation

3. Entscheidungsbildung
   - binäre Entscheidung:
     - ALLOW
     - BLOCK

Keine Gewichtung, keine Optimierung, keine Anpassung.

---

## 4. Ausgabe (Output)

L2 erzeugt ausschließlich eine Entscheidungsstruktur:

- Entscheidung: ALLOW oder BLOCK
- Begründung: maschinenlesbar, nachvollziehbar
- Zeitstempel
- Referenz auf Strategie-ID

Die Ausgabe ist:
- nicht bindend
- nicht exekutiv
- vollständig protokollierbar

---

## 5. Schnittstelle zu L1

- L1 kann die L2-Entscheidung berücksichtigen oder ignorieren
- L2 hat keine Möglichkeit:
  - Orders zu platzieren
  - L1 zu stoppen
  - Guards zu überschreiben

L1 bleibt vollständig autonom.

---

## 6. Fehler- und Abbruchprinzip

L2 wird sofort deaktiviert, wenn:
- L1-Alarm ausgelöst wird
- Entscheidungsoutput nicht reproduzierbar ist
- Inkonsistenzen zwischen GS und Live-Kontext auftreten

Deaktivierung bedeutet:
- L1 läuft unverändert weiter
- L2 wird vollständig ignoriert

---

## 7. Bewusste Nicht-Ziele

L2 macht explizit NICHT:
- neue Signale berechnen
- Strategien verändern
- Kapital allokieren
- Performance optimieren
- Auto-Handel durchführen

---

## 8. Status

Dokumentstatus: ENTWURF (konzeptionell)  
Implementierung: nicht begonnen  
Aktivierung: frühestens nach erfolgreichem L1-Beobachtungsfenster (≥ 48 h)

---
ENDE
