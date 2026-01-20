# LIVE DESIGN — L1-C ACCEPTANCE CHECKLIST
Projekt: Sniper-Bot  
Phase: L1-C — Intent Fusion mit 5m Timing Core  
Datum: 2026-01-20  
Status: VERBINDLICH (Design-Freeze-Dokument)

---

## Zweck dieses Dokuments

Dieses Dokument definiert die **verbindlichen Abnahmekriterien** für L1-C.

Es legt fest:
- was L1-C **ist**,
- was L1-C **nicht ist**,
- welche Invarianten dauerhaft gelten,
- welche Tests Pflicht sind,
- welche Änderungen ab jetzt **verboten** sind.

Nach Abnahme gilt: **L1-C ist eingefroren.**

---

## Scope von L1-C (verbindlich)

L1-C umfasst **ausschließlich**:

- Deterministische Fusion von:
  - 1m Intent (BUY/SELL/HOLD)
  - 5m Timing Vote (long/short/none, strength)

- Policy:

  1m BUY + 5m long (strength ≥ thresh)  → BUY  
  1m SELL + 5m short (strength ≥ thresh) → SELL  
  sonst → HOLD

- Keine Execution  
- Keine Order-Logik  
- Keine Performance-Optimierung  
- Keine Marktaggregation  

L1-C ist eine **reine Entscheidungs-Gate-Phase**.

---

## Architektur-Invarianten

Die folgenden Dateien bilden den **fixierten Kern von L1-C**:

- `live_l1/core/timing_5m.py`
- `live_l1/core/intent_fusion.py`
- `live_l1/core/loop.py` (nur Integration, keine Policy-Änderung)
- `tools/l1c_smoke_test.py`

Invarianten:

1. Richtung kommt **nur aus dem Seed**:
   - CSV-Spalte `direction` oder
   - `comb_json['dir']`

2. Score bestimmt **nur strength**, niemals die Richtung.

3. `compute_5m_timing_vote(...)`:
   - akzeptiert `**kwargs`
   - ignoriert unbekannte Parameter deterministisch

4. `merge_intent_with_5m_vote(...)` implementiert exakt Policy v1.

5. Kein Teil von L1-C liest Marktpreise oder Kerzen.

---

## Seed-Invarianten

Für alle 5m-Seeds gilt verbindlich:

- Richtung wird **nicht** aus dem Score-Vorzeichen abgeleitet.  
- Richtung wird **nicht** implizit geraten.  
- Wenn weder CSV-`direction` noch `comb_json['dir']` existiert:  
  → direction = `"long"` (Default, explizit dokumentiert)

Verboten:

- direction aus Gewichten ableiten  
- direction aus Score-Sign ableiten  
- direction dynamisch ändern  

---

## Pflicht-Tests für Abnahme

Die folgenden Tests sind **zwingend vor jedem Merge**, der L1-C betrifft:

### 1. Deterministischer Smoke-Test

Befehl:

```bash
python3 tools/l1c_smoke_test.py
