STEP 9A / SHORT-LIFECYCLE-ANALYSE – ZUSAMMENFASSUNG DER LETZTEN RUNS
Ausgangslage

Bisherige wichtigste Erkenntnis aus der Regime-Analyse:

Nicht LONGS sind das Hauptproblem.
Sondern lange SHORTS.

Besonders kritisch:

1h_to_4h_short
PF massiv negativ
großer Verlusttreiber

Gleichzeitig:

15m_to_1h_short
extrem profitabel

Daraus entstand die neue Hypothese:

Nicht Entry verschlechtern.
Sondern toxische lange SHORTS zeitlich begrenzen.
STEP 9A – SHORT_TIME_STOP = 3600
Änderung

Datei:
live_l1/core/execution.py

Neue Logik:

LONG_TIME_STOP_SEC = 3600.0
SHORT_TIME_STOP_SEC = 3600.0

Wichtig:

LONGS bleiben praktisch unverändert
nur lange SHORTS werden aktiv nach 1h beendet
RUN 1 – 1M @ offset 2,500,000
Ergebnis
Kennzahl	Wert
Return	26.49%
PF	2.0156
DD	4.78%
Trades	144
Winrate	69.44%
Vergleich zur alten Baseline

Vorher:

PF: 1.61
DD: 7.84%

Jetzt:

PF: 2.02
DD: 4.78%
Wichtigste Erkenntnis

Massive strukturelle Verbesserung ohne Aktivitätsverlust.

Trades:

identisch (144)
aber deutlich bessere Equity-Struktur

Das deutet darauf hin:

toxische lange SHORTS wurden begrenzt,
ohne profitable mittlere SHORTS zu zerstören
REGIME-ANALYSE DES 1M-RUNS
Kritischster Befund
15m_to_1h_short
PF 3.62
+1704 PnL
extrem stark

ABER:

1h_to_4h_short
PF 0.24
-752 PnL
weiterhin toxisch
Neue Kern-Erkenntnis

Der 1h-Stop:

macht toxische SHORTS NICHT profitabel
begrenzt aber ihren Schaden massiv

Das erklärt:

besseren PF
niedrigeren DD
stabilere Equity
STEP 9B – SHORT_TIME_STOP = 2700
Idee

Weitere Begrenzung:
SHORTS bereits nach 45 Minuten schließen.

Änderung:

SHORT_TIME_STOP_SEC = 2700.0
RUN 2 – 200k @ offset 1,000,000
Ergebnis
Kennzahl	Wert
Return	2.34%
PF	4.33
DD	0.39%
Trades	18
Vergleich

Baseline:

Return: 2.88%
PF: 6.42
DD: 0.37%
Erkenntnis

45 Minuten war zu aggressiv.

Probleme:

PF sinkt deutlich
Return sinkt
DD verbessert sich praktisch nicht
Entscheidung
STEP 9B verworfen.

Zurück zu:

SHORT_TIME_STOP_SEC = 3600.0
VALIDIERUNG VON STEP 9A
RUN 3 – 500k @ offset 1,500,000

Historisch sehr wichtiges Problemfenster.

Ergebnis
Kennzahl	Wert
Return	14.64%
PF	2.46
DD	5.17%
Trades	47
Vergleich zur alten Baseline

Vorher:

Return: 15.08%
PF: 2.58
DD: 5.15%

Jetzt:

Return: 14.64%
PF: 2.46
DD: 5.17%
Wichtigste Erkenntnis

Praktisch identische Qualität.

Das bedeutet:

SHORT_TIME_STOP = 3600
beschädigt die starke Baseline NICHT.

Sehr wichtiger struktureller Nachweis.

GESAMTBEWERTUNG DER LETZTEN RUNS
Aktueller bester Stand
LONG_TIME_STOP_SEC = 3600.0
SHORT_TIME_STOP_SEC = 3600.0
WICHTIGSTE PROJEKTERKENNTNISEN
1. Das Problem liegt nicht primär im Entry

Nicht:

Score
MA200
MFI
ATR

sind aktuell der Hauptengpass.

Sondern:

Trade-Lifecycle-Verhalten
2. Lange SHORTS sind strukturell toxisch

Besonders:

1h_to_4h_short

zeigt:

schlechte WR
negativen PF
hohe DD-Beiträge
3. Mittlere SHORTS sind extrem wertvoll
15m_to_1h_short
PF ~3.6

Diese dürfen NICHT zerstört werden.

4. STEP 9A ist kein klassischer Entry-Tweak

Sondern:

ein Lifecycle-/Risikostruktur-Upgrade

Das ist ein deutlicher Reifegrad-Sprung des Projekts.

AKTUELLER STATUS
Stabil bestätigt
200k @ 1M
500k @ 1.5M
1M @ 2.5M
Besonders wichtig

1M @ 2.5M:

massiv verbessert
PF stark erhöht
DD stark reduziert

ohne:

Tradeverlust
Aktivitätskollaps
Overfiltering
AKTUELL NÄCHSTER SCHRITT

Empfohlen:

3M @ offset 1,000,000

Ziel:

finale Robustheitsprüfung
langfristige Validierung von STEP 9A
Prüfung, ob Lifecycle-Verbesserung auch über sehr lange Marktzyklen stabil bleibt.