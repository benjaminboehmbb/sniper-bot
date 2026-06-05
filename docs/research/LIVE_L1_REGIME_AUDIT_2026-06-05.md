# LIVE L1 REGIME AUDIT
Date: 2026-06-05

## Ziel

Audit des aktuell produktiven Regime-Systems im Live-L1-Pfad.

Untersucht wurden:

- live_l1/core/regime_detector.py
- regime_v1
- regime_v2
- allow_long
- allow_short
- Regime-Datenfluss

---

## Befund 1: regime_detector.py ist nicht das eigentliche Regime-System

Datei:

live_l1/core/regime_detector.py

Ergebnis:

Das Modul dient ausschließlich:

- Monitoring
- Logging
- Diagnose

Es beeinflusst keine Handelsentscheidungen.

Expliziter Hinweis im Code:

"This module must not change trading decisions."

---

## Befund 2: Produktive Regime-Logik stammt aus den Datensätzen

Live-L1 liest folgende Felder aus den vorbereiteten Datensätzen:

- regime_v1
- regime_v2
- allow_long
- allow_short

Die Handelslogik berechnet diese Felder aktuell nicht selbst.

---

## Befund 3: regime_v1 Definition

Quelle:

scripts/post_gs_h3_build_eth_signals_regime_gs_compat.py

Definition:

bull:
- close > ma200
- ma200_slope(1440) > 0

bear:
- close < ma200
- ma200_slope(1440) < 0

side:
- alle übrigen Fälle

Formel:

regime_v1 =
MA200-Lage
+
MA200-Steigung über 1440 Minuten

---

## Befund 4: allow_long / allow_short

Definition:

allow_long:

- regime_v1 >= 0
- ADX >= 15

allow_short:

- regime_v1 == -1
- ADX >= 20

Damit existiert ein asymmetrisches Markt-Gate.

Short-Einstiege werden restriktiver behandelt als Long-Einstiege.

---

## Befund 5: regime_v2

Quelle:

tools/build_regime_v2_from_v1.py

Regime v2 ist kein neues Marktmodell.

Es handelt sich um einen Stabilitätsfilter für regime_v1.

Eigenschaften:

- Mindestdauer neuer Regime:
  720 Bars
  (= 12 Stunden auf 1m Daten)

Optional:

- keine direkten bull/bear Wechsel
- Wechsel müssen über side erfolgen

Ziel:

- weniger Regime-Flattern
- stabilere Gates
- höhere Reproduzierbarkeit

---

## Bewertung

Das Regime-System basiert aktuell auf:

1. MA200 Lage
2. MA200 1-Tages-Slope
3. ADX Filter
4. Regime-Stabilisierung (v2)

Das System ist deutlich robuster als ein reines MA200-Regime.

---

## Offene Produktionsbaustelle

Aktuell werden regime_v1, regime_v2, allow_long und allow_short aus vorbereiteten Datensätzen gelesen.

Für einen vollständig autonomen Live-Betrieb muss diese Logik zukünftig online berechnet werden.

Offener Punkt:

P1 - Online Regime & Gate Builder

Derzeit keine unmittelbare Entwicklungspriorität.

---

## Audit-Status

LIVE-L1 REGIME AUDIT

Status: BESTANDEN

Kritische Fehler:
- keine gefunden

Dokumentationsgewinn:
- Herkunft und Definition von regime_v1 identifiziert
- Herkunft und Definition von regime_v2 identifiziert
- Gate-Logik vollständig rekonstruiert
- Datenfluss nachvollzogen
