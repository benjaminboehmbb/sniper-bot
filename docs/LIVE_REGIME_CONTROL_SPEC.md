# LIVE REGIME CONTROL SPEC

## Ziel

Regime-Erkennung fuer den spaeteren Live-Betrieb vorbereiten.

Das Ziel ist nicht, die Baseline sofort zu ersetzen, sondern zu entscheiden:

- wann Baseline aktiv bleibt
- wann SHORT-lastiges Modell sinnvoll sein kann
- wann Risiko reduziert oder Trading pausiert wird

## Aktueller Stand

- Baseline ist stabil
- STEP 5 LONG-TimeStop bleibt aktiv
- Globale Entry-Tweaks wurden verworfen
- SHORT-only ist stark in bestimmten Fenstern, aber nicht universell robust

## Grundprinzip

Keine harte Live-Schaltung ohne Validierung.

Reihenfolge:

1. Regime nur beobachten
2. Regime in Logs speichern
3. Regime nach Runs auswerten
4. erst danach Modell-Switching testen

## Erste Regime-Klassen

### BULL

Merkmale:
- ma200_signal == 1
- bevorzugt LONG

Aktion vorerst:
- Baseline aktiv lassen
- SHORT nicht pauschal deaktivieren

### BEAR

Merkmale:
- ma200_signal == -1
- bevorzugt SHORT

Aktion vorerst:
- Baseline aktiv lassen
- SHORT-Performance getrennt beobachten

### CHOP / UNSICHER

Merkmale:
- widerspruechliche Signale
- viele Richtungswechsel
- schwacher Profit Factor in Auswertung

Aktion vorerst:
- nur beobachten
- spaeter moeglicher Risiko-Reduktionsmodus

### HIGH RISK

Merkmale:
- Loss-Cluster aktiv
- mehrere SL-Treffer
- steigender Drawdown

Aktion vorerst:
- nicht neues Modell aktivieren
- Entry-Pause oder Positionsreduktion spaeter pruefen

## Modell-Idee

### Modell A: Baseline

Default-Modell.
Bleibt Hauptmodell.

### Modell B: SHORT-only

Kein globaler Ersatz.
Nur moeglicher Spezialmodus fuer klar bearische Marktphasen.

### Modell C: Risk-Off

Noch nicht implementiert.
Spaeter fuer schlechte Marktphasen.

## Wechselregeln - NICHT AKTIV

Noch keine automatischen Wechsel.

Geplante Reihenfolge:
1. Regime-Label pro Tick erzeugen
2. Regime-Label pro Trade speichern
3. Performance je Regime analysieren
4. stabile Regeln ableiten
5. Switching nur im Paper-Modus testen

## Mindestanforderungen vor Live-Nutzung

Ein Regime-Switch darf nur aktiviert werden, wenn:

- auf mehreren Offsets getestet
- gegen Baseline verglichen
- kein Drawdown-Anstieg
- keine Trade-Explosion
- deterministisch reproduzierbar
- sauber dokumentiert

## Naechster technischer Schritt

Ein reines Analyse-/Logging-Modul erstellen:

- kein Trading-Eingriff
- kein Entry/Exit-Eingriff
- nur Regime berechnen und loggen

Moeglicher Dateiname:

`live_l1/core/regime_detector.py`

