# LIVE DESIGN — L1-D RESTART & RECOVERY PROTOCOL
Projekt: Sniper-Bot
Datum: 2026-01-10
Status: VERBINDLICH (L1)

---

## Zweck dieses Dokuments

Dieses Dokument definiert das verbindliche Verfahren
für Stop, Restart und Recovery im Paper Trading (L1).

Ziel ist ein deterministisches, nachvollziehbares
und manuell kontrolliertes Wiederanlaufverhalten.

Kein automatisches Recovery ist erlaubt.

---

## Grundsatz

Restart ist ein kontrollierter Neustart,
keine Fehlerkorrektur.

Bei Unsicherheit gilt:
STOP → ANALYSE → ENTSCHEIDUNG → RESTART

---

## Zulässige Restart-Auslöser

Ein Restart darf NUR erfolgen bei:

- explizitem manuellem Stop
- Kill-Level == HARD
- Kill-Level == EMERGENCY
- geplantem Wartungsfenster
- reproduzierbarem Systemfehler

Automatische Restarts sind verboten.

---

## Vorbedingungen für einen Restart (Pflicht)

Vor jedem Restart MUSS bestätigt sein:

- Ursache des Stops identifiziert
- relevante Logs gesichert
- Kill-Level bekannt
- letzter State-Zeitpunkt dokumentiert
- keine offenen Intents

Wenn eine Bedingung nicht erfüllt ist → KEIN Restart.

---

## Restart-Sequenz (verbindlich)

### Schritt 1 — Systemstillstand

- Trading-Loop gestoppt
- keine neuen Snapshots verarbeiten
- keine Orders senden

---

### Schritt 2 — State-Prüfung

- lade persistierten Position State (S2)
- lade persistierten Risk State (S4)
- prüfe Konsistenz
- validiere Kill-Level

Inkonsistenz → kein Restart.

---

### Schritt 3 — Umgebung prüfen

- Uhrzeit & Zeitsynchronisation prüfen
- Ressourcenstatus prüfen
- Konfigurationsversion prüfen
- Logging aktiv bestätigen

Abweichung → kein Restart.

---

### Schritt 4 — Manuelle Freigabe

- explizite Entscheidung zum Restart
- dokumentierter Zeitpunkt
- dokumentierter Verantwortlicher

Ohne Freigabe → kein Restart.

---

### Schritt 5 — Restart

- Systemstart
- Initialisierung gemäß L0-E
- Kill-Level unverändert übernehmen
- Warte auf validen Market Snapshot

Kein Trading vor vollständigem Abschluss.

---

## Verhalten nach Restart

- keine sofortige Order
- normale Guard-Prüfung
- Cooldowns bleiben aktiv
- keine Kill-Level-Reduktion

Restart ist kein Reset.

---

## Verbotene Recovery-Praktiken

- Auto-Restart
- Kill-Level-Reset
- State-Manipulation
- Guard-Deaktivierung
- „Schneller Neustart ohne Analyse“

---

## Logging-Pflichten

Jeder Restart MUSS loggen:

- Restart-Grund
- vorheriges Kill-Level
- geladenen State-Zeitpunkt
- Konfigurations-Hash
- manuelle Freigabe

Kein Restart ohne vollständiges Log.

---

## Erfolgskriterium (L1-D)

L1-D gilt als erfüllt, wenn:

- jeder Restart reproduzierbar erklärbar ist
- kein unerwartetes Trading nach Restart erfolgt
- State konsistent bleibt
- Kill-Level korrekt fortgeführt wird

---

## Zentrale Invariante

Ein Restart darf niemals
Risiken verschleiern oder zurücksetzen.

---

## Abschluss

Dieses Protokoll stellt sicher,
dass Restart ein kontrollierter Prozess ist
und kein versteckter Reset.

Ohne dieses Protokoll
ist Paper Trading unzulässig.
