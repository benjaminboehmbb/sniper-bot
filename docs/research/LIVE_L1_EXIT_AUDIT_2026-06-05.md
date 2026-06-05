# LIVE L1 EXIT AUDIT
Date: 2026-06-05

## Ziel

Audit des produktiven Exit-Systems von Live-L1.

Untersucht:

- Exit-Logik in intent.py
- Execution-Pfad in execution.py
- TP/SL
- Time Stop
- Signal-Exits
- Reale Exit-Verteilung aus Trades

---

## Aktuelle Exit-Architektur

Exit-Reihenfolge:

1. TP/SL
2. Time Stop
3. Signal Exit

Damit besitzen risikobegrenzende Mechanismen Vorrang vor Signal-Exits.

---

## Entry-Logik (Referenz)

LONG Entry:

- ma200_signal = +1
- mfi_signal = +1
- 3x Score >= +3
- bei ATR=-1: 3x Score >= +4

SHORT Entry:

- ma200_signal = -1
- mfi_signal = -1
- 3x Score <= -3
- bei ATR=-1: 3x Score <= -4

---

## Exit-Logik

LONG Exit:

- 1x Score <= -1

Code:

    _last_n_all_le(1, -1)

Resultat:

- sofortiger SELL
- CLOSE_LONG

---

SHORT Exit:

- 2x Score >= +2

Code:

    _last_n_all_ge(2, 2)

Resultat:

- BUY
- CLOSE_SHORT

---

## Asymmetrische Exit-Struktur

Aktuelle Strategie:

LONG:

- schneller Exit

SHORT:

- stärkere Gegenbestätigung erforderlich

Bewertung:

Bewusst asymmetrisch.

Passt zum historischen Commit:

BEST_STATE rsi_mfi long_exit_-1 short_exit_2x pf_1.85 dd_0.054

---

## TP/SL

Aktuelle Werte:

TP:

- 5.0 %

SL:

- 1.5 %

Bewertung:

Dokumentiert und konsistent zum aktuellen Code.

---

## Time Stop

LONG:

- 3600 Sekunden

SHORT:

- 3600 Sekunden

Entspricht:

- 60 Minuten

---

## Reale Exit-Verteilung

Auswertung:

556 Trades

Verteilung:

CLOSE_LONG: 322

CLOSE_SHORT: 154

SHORT_TIME_STOP: 63

SL_LONG: 8

SL_SHORT: 7

LONG_TIME_STOP: 2

---

## Interpretation

Signal-Exits:

322 + 154 = 476 Trades

Anteil:

476 / 556

= 85.6 %

Damit werden die meisten Trades durch die Score-Logik beendet.

---

## Take Profit Analyse

TP_LONG:

0

TP_SHORT:

0

Interpretation:

TP 5 % wurde im untersuchten Datensatz praktisch nicht erreicht.

TP wirkt aktuell hauptsächlich als Sicherheitsmechanismus.

Die tatsächliche Exit-Steuerung erfolgt über die Signal-Logik.

---

## Stop Loss Analyse

SL_LONG:

8

SL_SHORT:

7

Gesamt:

15 Trades

Anteil:

15 / 556

= 2.7 %

Interpretation:

SL greift selten.

---

## Time Stop Analyse

SHORT_TIME_STOP:

63

LONG_TIME_STOP:

2

Interpretation:

Short-Positionen bleiben deutlich häufiger länger offen.

Der Short Time Stop besitzt reale operative Bedeutung.

Der Long Time Stop spielt aktuell nahezu keine Rolle.

---

## Gesamtbewertung

Die Exit-Engine wird primär gesteuert durch:

1. Score-basierte Signal-Exits
2. Short Time Stop
3. Stop Loss

TP spielt aktuell praktisch keine Rolle.

Die aktuelle Exit-Struktur entspricht dem dokumentierten BEST_STATE-Ansatz.

---

## Verbesserungsmöglichkeiten

P1

TP-Effektivität untersuchen.

Aktuell praktisch keine TP-Ausführungen.

---

P2

Analyse der hohen Short-Time-Stop-Anteile.

Warum laufen Shorts häufiger bis 60 Minuten?

---

P3

TP/SL/Time Stop zentral konfigurierbar machen.

Aktuell hardcoded.

---

## Audit-Fazit

LIVE_L1_EXIT_AUDIT_2026-06-05

Status: BESTANDEN

Kritische Fehler:

- keine gefunden

Wichtigste Erkenntnis:

Die Live-L1 Strategie ist nicht TP-getrieben.

Die Strategie wird überwiegend durch die Score-basierte Exit-Logik gesteuert.
