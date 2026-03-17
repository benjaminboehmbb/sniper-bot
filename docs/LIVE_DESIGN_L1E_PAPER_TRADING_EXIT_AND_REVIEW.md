# LIVE DESIGN — L1-E PAPER TRADING EXIT & REVIEW
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH (L1)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die verbindlichen Kriterien
für den Abschluss von L1 (Paper Trading)
sowie das strukturierte Review nach Ende der Phase.

L1 endet bewusst und explizit.
Es gibt keinen impliziten Übergang.

---

## Grundsatz

Paper Trading endet,
wenn ausreichend Vertrauen in den Betrieb
oder ausreichend Evidenz für Designmängel vorliegt.

Dauer ist kein Erfolgskriterium.

---

## Zulässige Abschlussarten

### A1 — Regulärer Abschluss
- stabiler Betrieb über repräsentativen Zeitraum
- keine ungeklärten Abbrüche
- Guards und Kill-Switches verhalten sich erwartungsgemäß
- vollständige Observability gegeben

### A2 — Abbruch (Design-Fehler)
- Guard-Fehlfunktion
- nicht erklärbares Verhalten
- State-Inkonsistenz
- Restart-Protokoll nicht einhaltbar

Abbruch ist ein valides Ergebnis.

---

## Abschlusskriterien (verbindlich)

L1 darf abgeschlossen werden, wenn ALLE Punkte erfüllt sind:

- kein ungeklärtes Order-Verhalten
- jeder Kill-Level-Wechsel erklärbar
- State-Persistenz fehlerfrei
- Restarts reproduzierbar
- Logs vollständig und konsistent
- keine verbotenen Metriken erhoben

Wenn ein Punkt nicht erfüllt ist → L1 nicht abgeschlossen.

---

## Review-Protokoll (Pflicht)

Nach Abschluss MUSS erstellt werden:

### Review-Inhalte
- Zusammenfassung des Betriebsverlaufs
- Liste aller Guard-Trigger
- Liste aller Kill-Switch-Ereignisse
- Restart-Historie
- identifizierte Schwachstellen
- bestätigte Stärken des Designs

Keine Performance-Auswertung.

---

## Zulässige Ergebnisse nach Review

Nach L1 sind erlaubt:

- Design-Korrekturen (neue Phase)
- Übergang zu L2 (kontrolliertes Live)
- Entscheidung zur Exploration / Optimierung (neues Mandat)
- bewusster Stopp des Projekts

Nicht erlaubt:
- stillschweigender Übergang
- sofortige Optimierung
- Performance-getriebene Entscheidungen

---

## Dokumentationspflicht

Der Abschluss von L1 MUSS dokumentiert werden in:

- eigenem Abschlussdokument
- mit Datum und Verantwortlichem
- mit expliziter Entscheidung

Ohne Dokumentation gilt L1 als nicht beendet.

---

## Zentrale Invariante

Wenn nach L1 über Strategiequalität
statt über Systemqualität gesprochen wird,
war L1 nicht korrekt durchgeführt.

---

## Abschluss

L1 ist eine Vertrauensphase.
Ihr Wert liegt in Klarheit,
nicht in Ergebnissen.

Erst nach einem sauberen Abschluss
ist jede weitere Phase sinnvoll.
