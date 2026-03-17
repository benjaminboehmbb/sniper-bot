# LIVE DESIGN — L1-A OPERATIONAL GOALS & METRICS
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH (L1)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die **konkreten betrieblichen Ziele**
und **zulässigen Metriken** für L1 (Paper Trading).

Es bewertet **ausschließlich Systembetrieb**,
nicht Strategiequalität und nicht Performance.

---

## Grundsatz

In L1 wird **Stabilität gemessen, nicht Erfolg**.

Jede Metrik dient der Frage:
„Ist das System kontrollierbar, erklärbar und sicher?“

---

## Primäre Betriebsziele (verbindlich)

### G1 — Ablaufstabilität
- Live-Loop läuft kontinuierlich
- keine unerklärten Stops
- keine Schritt-Überspringungen

### G2 — Guard-Wirksamkeit
- Guards greifen deterministisch
- Kill-Switch-Level verhalten sich monoton
- keine Umgehung oder Abschwächung

### G3 — State-Integrität
- State-Übergänge konsistent
- Persistenz korrekt
- Neustart reproduzierbar

### G4 — Beobachtbarkeit
- jede Entscheidung erklärbar
- jede Order rückverfolgbar
- jede Blockierung sichtbar

### G5 — Manuelle Kontrollierbarkeit
- jederzeitiger manueller Stop möglich
- klarer Systemstatus erkennbar
- kein „Zombie-Zustand“

---

## Zulässige Metriken (Betrieb)

### Loop & Timing
- Decision-Ticks pro Stunde
- verpasste Ticks (Count)
- Loop-Dauer (min / max)

### Guards & Kill-Switches
- Anzahl Guard-Trigger
- Kill-Level-Wechsel (Zeit + Ursache)
- Dauer von Pausen / Cooldowns

### State
- Anzahl State-Persistenzen
- Restart-Erfolge / -Fehlschläge
- erkannte Inkonsistenzen (Count)

### Datenqualität
- data_valid false (Count / Dauer)
- Zeitstempel-Abweichungen
- fehlende Snapshots

### Health
- Heartbeat-Ausfälle
- Resource-Warnungen
- ungeplante Prozess-Enden

---

## Verbotene Metriken (explizit)

Die folgenden Metriken dürfen in L1 **nicht erhoben oder diskutiert** werden:

- ROI
- Winrate
- Sharpe
- Drawdown
- Profit / Loss
- Trade-Qualität
- Vergleich mit GS-Ergebnissen
- Ranking von Strategien

---

## Zielerreichung (qualitativ)

L1 gilt als **erfolgreich**, wenn:

- keine ungeklärten Abbrüche auftreten
- Guards erwartungsgemäß auslösen
- State jederzeit konsistent bleibt
- Logs eine vollständige Erklärung erlauben

L1 gilt als **nicht erfolgreich**, wenn:

- Entscheidungen nicht rekonstruierbar sind
- Guards versagen oder umgangen werden
- State nach Restart inkonsistent ist
- Kill-Switches nicht zuverlässig greifen

---

## Abbruchlogik

L1 ist sofort zu beenden bei:

- nicht erklärbarem Systemverhalten
- mehrfachen Guard-Fehlfunktionen
- State-Korruption
- manueller Entscheidung

Abbruch ist ein valides Ergebnis.

---

## Zentrale Invariante

Wenn ein beobachtetes Verhalten
nur durch Strategie- oder Performance-Argumente
gerechtfertigt wird,
ist L1 fehlgeschlagen.

---

## Abschluss

Diese Ziele und Metriken definieren,
wann L1 sinnvoll ist
und wann es abgebrochen werden muss.

Alle weiterführenden Analysen
sind ausdrücklich ausgeschlossen.
