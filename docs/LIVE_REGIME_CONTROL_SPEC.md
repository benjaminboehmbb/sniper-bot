# LIVE REGIME CONTROL (V1)

## Ziel
- Marktphase erkennen
- passendes Modell aktivieren
- stabile Wechsel erkennen
- alles dokumentieren

---

## Grundlogik

Pro Tick:

1. Regime berechnen
2. Regime glätten (kein direktes Umschalten)
3. wenn stabil -> Wechsel bestätigen
4. Modell wechseln
5. alles loggen

---

## Regime (V1)

- UP_TREND
- DOWN_TREND
- SIDEWAYS
- CRISIS
- UNCLASSIFIED

---

## Regeln

- Wechsel nur nach mehreren Bestätigungen (kein Flattern)
- immer nur 1 aktives Modell
- offener Trade bleibt beim ursprünglichen Modell
- neues Modell gilt nur für neue Trades

---

## Logs

- regime_detection.jsonl
- model_switches.jsonl
- model_activity.jsonl

---

## Nächster Schritt

Implementieren:

live_l1/core/regime_detector.py