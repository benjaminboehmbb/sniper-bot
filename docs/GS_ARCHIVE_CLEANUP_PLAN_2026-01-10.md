# GS Archivierungs- & Cleanup-Plan
Projekt: Sniper-Bot — Gold-Standard (simtraderGS)  
Datum: 2026-01-10  
Status: PLAN (noch keine Ausführung)

---

## 0) Ziel & Grundsätze

**Ziel**
- Ordnung, Nachvollziehbarkeit, Reproduzierbarkeit.
- Reduktion aktiver Artefakte auf den **Gold-Standard-Kern**.
- Keine Informationsverluste, keine stillen Löschungen.

**Grundsätze (verbindlich)**
- Read-only bis zur expliziten Freigabe.
- FINAL-Artefakte werden **niemals** überschrieben.
- Archivierung ist **reversibel** (kein Hard-Delete).
- Eindeutige Namenskonventionen, keine Parallelversionen.

---

## 1) Definition: Was ist „FINAL“ (bleibt aktiv)

### 1.1 Engine / Fundament (fix)
- `engine/simtraderGS.py`  
  → **Gold-Standard**, eingefroren.

### 1.2 Daten (fix)
- `data/btcusdt_1m_2026-01-07/simtraderGS/`
  - `btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv`

### 1.3 Strategien (FINAL)
- LONG:
  - `strategies/GS/LONG_FINAL/` *(historisch, eingefroren)*
  - `strategies/GS/LONG_FINAL_CANONICAL/`
    - `strategies_GS_k12_long_FINAL_CANONICAL_2026-01-10_08-35-40.csv`
- SHORT:
  - `strategies/GS/SHORT_FINAL/`
    - `strategies_GS_k12_short_FINAL_2026-01-09_18-32-16.csv`

### 1.4 Ergebnisse (FINAL / CANONICAL)
- LONG:
  - `results/GS/k12_long/strategy_results_GS_k12_long_FULL_CANONICAL_2026-01-10_08-35-40.csv`
- SHORT:
  - `results/GS/k12_short/strategy_results_GS_k12_short_FULL_CANONICAL_2026-01-10_08-44-32.csv`

### 1.5 Meta
- `results/GS/meta/`
  - `meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_2026-01-10_08-48-36.csv`
  - `meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_2026-01-10_08-48-36.md`

---

## 2) Definition: Was ist „AKTIV“ (bleibt, aber nicht FINAL)

Diese Dateien bleiben **zugreifbar**, sind aber **nicht autoritativ**:

### 2.1 Analyse-Skripte (GS)
- `scripts/analyze_GS_kX_long.py`
- `scripts/analyze_GS_kX_short.py`
- `scripts/build_GS_k12_long_FINAL_CANONICAL.py`
- `scripts/build_GS_k12_short_RESULTS_CANONICAL.py`

### 2.2 Tools (read-only / Meta / Diagnostics)
- `tools/gs_meta_compare_k12_finals.py`
- `tools/gs_long_final_preflight.py`
- `tools/gs_long_short_diagnostics.py`

---

## 3) Definition: Was wird ARCHIVIERT (nicht gelöscht)

### 3.1 Kandidaten & Zwischenstände
- Alle `strategies/GS/kX_*` **außer**:
  - `LONG_FINAL/`
  - `LONG_FINAL_CANONICAL/`
  - `SHORT_FINAL/`

Beispiele:
- `strategies/GS/k3_long/`
- `strategies/GS/k8_long/`
- `strategies/GS/k11_short/`
- Seeds, Top-N, Intermediate-Selektoren.

### 3.2 Ergebnis-Zwischenstände
- Alle `results/GS/kX_*` **außer**:
  - `k12_long/*_FULL_CANONICAL_*`
  - `k12_short/*_FULL_CANONICAL_*`
  - `meta/*`

### 3.3 Alte Experimente / Legacy
- Alle vor-GS oder pre-canonical Artefakte:
  - Alias-/Signal-Mischformen
  - Gewichtete Varianten
  - Alte Analyzer-Versionen
  - Test-Outputs ohne GS-Contract

---

## 4) Archiv-Struktur (verbindlich)

Archiv-Root:
