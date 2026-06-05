# LIVE L1 TP Effectiveness Analysis - 2026-06-05

## Ziel

Analyse der tatsächlichen Wirksamkeit des aktuellen Take-Profit-Mechanismus im Live-L1-System.

## Datengrundlage

Datei:

live_logs/trades_l1.jsonl

Ausgewertete Trades:

556

## Exit-Verteilung

CLOSE_LONG: 322

CLOSE_SHORT: 154

SHORT_TIME_STOP: 63

SL_LONG: 8

SL_SHORT: 7

LONG_TIME_STOP: 2

TP_LONG: 0

TP_SHORT: 0

## Aktuelle Produktionsparameter

TP:

5.0 %

SL:

1.5 %

LONG_TIME_STOP_SEC:

3600

SHORT_TIME_STOP_SEC:

3600

## Ergebnis

Während der ausgewerteten Historie wurde kein einziger Trade über den Take-Profit beendet.

TP_LONG:

0

TP_SHORT:

0

Die tatsächliche Exit-Kontrolle erfolgt nahezu vollständig über:

- CLOSE_LONG
- CLOSE_SHORT

sowie in geringerem Umfang über:

- LONG_TIME_STOP
- SHORT_TIME_STOP
- SL_LONG
- SL_SHORT

## Interpretation

Der aktuelle TP-Wert von 5 % besitzt im aktuellen Live-L1-System praktisch keine operative Wirkung.

Positionen werden in der Regel bereits vorher durch die Signal-Exit-Logik geschlossen.

Der Take-Profit wirkt aktuell lediglich als zusätzliches Sicherheitsnetz.

## Entscheidung

Keine Änderung der Produktionsparameter.

TP bleibt unverändert auf:

5.0 %

Begründung:

- Keine Hinweise auf Fehlfunktion
- Keine Hinweise auf negativen Einfluss
- Keine ausreichende Datenbasis für eine sofortige Anpassung

## Mögliche spätere Untersuchungen

Separate Replay-Tests mit:

- TP = 1 %
- TP = 2 %
- TP = 3 %

Ziel:

Prüfen, ob kleinere TP-Werte die Gesamtperformance verbessern oder verschlechtern.

Diese Untersuchungen sind aktuell nicht priorisiert.

## Fazit

Der aktuelle TP-Mechanismus funktioniert technisch korrekt.

Die Analyse zeigt jedoch, dass der Wert von 5 % im aktuellen Live-L1-System faktisch nicht erreicht wird und deshalb derzeit keinen wesentlichen Einfluss auf die Exit-Verteilung besitzt.

