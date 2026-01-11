LIVE_DESIGN_L1_MINIMAL_DAILY_ROUTINE_30S

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: verbindlich
Zweck: Minimaler täglicher Operator-Check (≤30 Sekunden)

============================================================
GRUNDSATZ
============================================================
Kein Lesen. Kein Analysieren. Nur Prüfen, ob Alarm vorliegt.

Wenn kein Alarm:
→ nichts tun.

============================================================
TÄGLICHE ROUTINE (≤30s)
============================================================

1) Existiert ein L1-ALERT seit dem letzten Arbeitstag?
   - ja → L1 stoppen, prüfen
   - nein → weiter

2) Letzter Log-Eintrag vorhanden?
   - ja → weiter
   - nein → L1 stoppen

3) Letzter Status = OK?
   - ja → fertig
   - nein → L1 stoppen

============================================================
ENDE
============================================================
Wenn alle drei Punkte OK:
→ L1 gilt als stabil für heute.
