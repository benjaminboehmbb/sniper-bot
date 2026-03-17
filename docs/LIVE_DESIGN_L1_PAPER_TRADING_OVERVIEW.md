# LIVE DESIGN — L1 PAPER TRADING OVERVIEW
Projekt: Sniper-Bot  
Datum: 2026-01-10  
Status: DESIGN-DEFINITION (L1)

---

## Zweck dieser Phase

L1 (Paper Trading) dient der Überprüfung,
ob das in L0 definierte Live-Design
unter realen Zeit- und Datenbedingungen
stabil, kontrollierbar und erklärbar arbeitet.

L1 ist KEINE Optimierungsphase
und KEIN Leistungsnachweis.

---

## Grundsatz

Paper Trading prüft das System,
nicht die Strategie.

Erfolgskriterium ist Stabilität,
nicht Profitabilität.

---

## Was L1 explizit testet

### Systemverhalten
- vollständiger Live-Loop gemäß L0-E
- korrekte Reihenfolge aller Schritte
- deterministisches Flow-Verhalten

### Guards & Kill-Switches
- Auslösung unter realen Bedingungen
- monotones Kill-Level-Verhalten
- manuelle Notabschaltung

### State-Integrität
- saubere State-Übergänge
- Persistenz von S2 und S4
- konsistenter Neustart nach Stop

### Datenrealität
- reale Marktfeeds
- reale Zeit
- Datenlücken und Jitter
- Signalstabilität

---

## Was L1 ausdrücklich NICHT testet

- Profitabilität
- Renditevergleiche
- GS-Parität auf Zahlenebene
- Strategieauswahl
- Parameteranpassung
- Clustering oder Ranking
- K-Optimierung (K3–K12)

Diese Themen sind in L1 verboten.

---

## Zulässige Outputs von L1

- Logs (vollständig, erklärend)
- Guard-Trigger-Statistiken
- Kill-Switch-Häufigkeiten
- Laufzeit- und Stabilitätsmetriken
- qualitative Beobachtungen

Nicht zulässig:
- ROI-Auswertungen
- Winrate-Statistiken
- Performance-Rankings

---

## Abbruchkriterien (verbindlich)

L1 MUSS abgebrochen werden bei:

- nicht erklärbarem Order-Verhalten
- Guard-Fehlfunktion
- inkonsistentem State
- fehlgeschlagenem Restart
- Health-Instabilität
- manueller Entscheidung

Abbruch ist ein valides Ergebnis.

---

## Dauer & Umfang (nicht festgelegt)

- keine Mindestlaufzeit
- kein Erfolgs-Zeitpunkt
- Fortsetzung nur bei stabiler Beobachtung

L1 endet nicht automatisch.

---

## Übergang nach L1

Nach erfolgreichem Abschluss von L1 sind möglich:

- Review & Konsolidierung
- Designanpassungen (neue Phase)
- Übergang zu L2 (kontrolliertes Live)
- neues Mandat: Exploration / Optimierung

Kein automatischer Übergang.

---

## Zentrale Invariante

Wenn eine Beobachtung nur
durch Simulationsergebnisse erklärbar ist,
ist L1 fehlgeschlagen.

---

## Abschluss

L1 ist ein Sicherheits- und Vertrauensaufbau.
Erst danach ist jede weitere Phase sinnvoll.

Strategische oder statistische Optimierung
ist bewusst nachgelagert.
