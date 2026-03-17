# LIVE DESIGN — L1-C TIMING CORE v1
Projekt: Sniper-Bot  
Phase: L1-C  
Datum: 2026-01-20  
Status: VERBINDLICH (Design-Referenz)

---

## Zweck

Dieses Dokument beschreibt den 5m Timing Core v1 in L1-C.

Der Timing Core v1 ist ein:

- deterministisches  
- seed-basiertes  
- nicht lernendes  
- nicht datenaggregierendes  

Gate zur Bestätigung von 1m-Intents.

Er entscheidet **nicht selbst**, sondern filtert fremde Intents.

---

## Was das Modul IST

- liest statische Seed-CSV  
- wählt deterministisch den besten Seed  
- liefert:

  - direction ∈ {long, short, none}  
  - strength ∈ [0,1]  
  - seed_id  

- enthält **keine Marktlogik**  
- enthält **keine Aggregation**  
- enthält **keine Optimierung**

Zentrale Datei:



