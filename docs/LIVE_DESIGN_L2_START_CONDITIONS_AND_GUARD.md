# LIVE_DESIGN_L2_START_CONDITIONS_AND_GUARD.md

## Zweck

Dieses Dokument definiert die formalen Startbedingungen für L2 sowie die harten Guard-Regeln,
die sicherstellen, dass L2 erst nach einem stabilen L1-Betrieb und ohne Risikoausweitung
begonnen wird.

---

## 1. Bezugssystem

Projekt: Sniper-Bot  
Phase: Übergang L1 → L2  
Referenz-Commit L1: 32a45e5  
Betriebsmodus: L1 Paper Trading  
Health-Monitoring: aktiv (l1_health_check.py via cron)

---

## 2. Beobachtungsfenster (verbindlich)

Mindestdauer:
- ≥ 48 Stunden ununterbrochener Betrieb

Während des gesamten Beobachtungsfensters gilt:
- keine Code-Änderungen an L1
- keine Konfigurationsänderungen
- keine manuellen Eingriffe
- kein geplanter Shutdown

Erfolgskriterium:
- 0 ungeklärte Alarme
- ggf. auftretende Alarme sind erklärbar, dokumentiert und nicht systemisch

---

## 3. Eintrittskriterien für L2

L2 darf erst gestartet werden, wenn alle folgenden Punkte erfüllt sind:

1. Beobachtungsfenster ≥ 48 h erfolgreich abgeschlossen
2. live_l1_alert.flag war nicht dauerhaft vorhanden
3. L1-Health-Check gilt als stabil
4. Keine offenen oder bekannten L1-Probleme
5. L2-Mandat ist FINAL definiert

---

## 4. Erlaubter Arbeitsumfang in L2 (Startphase)

Erlaubt:
- Implementierung einer Entscheidungsfreigabe-Logik (ALLOW / BLOCK)
- Bewertung bestehender GS-Strategien
- Read-only-Zugriff auf:
  - GS-Artefakte
  - Live-Marktdaten
  - L1-States

Nicht erlaubt:
- Order-Ausführung
- neue Signale
- neue Heuristiken
- Performance-Optimierung
- Auto-Handel

---

## 5. Abbruch- und Rückfallregeln

L2 ist sofort zu stoppen, wenn:
- live_l1_alert.flag erscheint
- Entscheidungsoutput nicht reproduzierbar ist
- Inkonsistenzen zwischen GS-Referenz und Live-Bewertung auftreten
- L1-Stabilität in Frage steht

Rückfall:
- sofortige Rückkehr zu reinem L1-Betrieb
- keine Weiterarbeit an L2
- Ursache nur dokumentieren, nicht beheben

---

## 6. Status

Dokumentstatus: FINAL  
Änderungen: nur nach Review erlaubt  
L2-Implementierung: noch nicht gestartet

---
ENDE
