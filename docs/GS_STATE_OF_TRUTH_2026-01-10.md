# GS State of Truth — Sniper-Bot (simtraderGS)
Datum: 2026-01-10  
Status: Gold-Standard-Fundament FINAL (frozen), reproduzierbar

---

## 1) Verbindliche Grundsaetze

- Qualitaet vor Schnelligkeit
- Kein Informationsverlust
- Saubere, deterministische, reproduzierbare Gold-Standard-Pipeline
- Strikte Schrittfolge je K:
  Seeds -> Smoke -> Analyse -> Gate -> Entscheidung -> naechstes K
- Kein ML, kein Live, keine Experimente in dieser Phase (nur Fundament & Struktur)

---

## 2) Engine / Contract (frozen)

**Engine**
- Datei: `engine/simtraderGS.py`
- Entrypoint: `evaluate_strategy(price_df, comb, direction) -> Dict`

**Determinismus**
- Wiederholungen liefern identische Ergebnisse (geprueft)

**Regime-Gate**
- aktiv, asymmetrisch (allow_long / allow_short)
- Fallback: `regime_v1 in {+1, 0, -1}`

**Fee-Modell (extern)**
- `roi_fee = roi - fee * num_trades`
- fee (roundtrip): `0.0004`

---

## 3) Datenbasis (fix)

Instrument: BTCUSDT  
Zeiteinheit: 1-Minute

Fixe Preis-CSV (GS, ueberall identisch):
- `data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv`

Analyse-Fenster (immer identisch):
- rows: `200000`
- offsets: `0, 500000, 1000000, 1500000`

---

## 4) K-Endpunkt / Signale (fix)

K12 ist der strukturelle Endpunkt (12 Signale insgesamt).  
Keine weiteren K-Level moeglich ohne neue Signale.

Die 12 Kurzkeys (GS-Contract):
- `adx, atr, bollinger, cci, ema50, ma200, macd, mfi, obv, roc, rsi, stoch`

Wichtig:
- `comb` enthaelt Kurzkeys (nicht *_signal)
- interne Signale werden ausschliesslich aus *_signal-Spalten gelesen (Mapping liegt in simtraderGS)

---

## 5) FINAL-Artefakte (autoritativ, niemals ueberschreiben)

### 5.1 LONG
Historisch eingefroren (nicht mehr anfassen):
- `strategies/GS/LONG_FINAL/`

Canonical FINAL (GS-konform, autoritativ fuer Struktur):
- `strategies/GS/LONG_FINAL_CANONICAL/strategies_GS_k12_long_FINAL_CANONICAL_2026-01-10_08-35-40.csv`

Canonical Results (N=1, Offsets/Fee/Rows fix):
- `results/GS/k12_long/strategy_results_GS_k12_long_FULL_CANONICAL_2026-01-10_08-35-40.csv`

### 5.2 SHORT
FINAL (frozen):
- `strategies/GS/SHORT_FINAL/strategies_GS_k12_short_FINAL_2026-01-09_18-32-16.csv`

Canonical Results (N=1, Offsets/Fee/Rows fix):
- `results/GS/k12_short/strategy_results_GS_k12_short_FULL_CANONICAL_2026-01-10_08-44-32.csv`

---

## 6) Meta-Vergleich (read-only, abgeschlossen)

Meta-Report (mit Deltas):
- `results/GS/meta/meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_2026-01-10_08-48-36.csv`
- `results/GS/meta/meta_compare_GS_k12_LONG_CANONICAL_vs_SHORT_FINAL_2026-01-10_08-48-36.md`

Kernaussagen (aus Meta):
- Struktur: LONG und SHORT sind bitgenau identisch (12/12, gleiche Keys/Gewichte)
- Performance (im GS-Fenster): LONG ist leicht robuster (roi_fee_p25/mean besser)
- Trade-Last: SHORT handelt mehr (hoeherer Fee-Druck)

---

## 7) Aktive Ordnerstruktur (nach Cleanup)

Aktiver GS-Kern:
- `engine/simtraderGS.py`
- `data/.../btcusdt_1m_price_2017_2025_...ASYMGATE.csv`
- `strategies/GS/LONG_FINAL_CANONICAL/`
- `strategies/GS/SHORT_FINAL/`
- `results/GS/k12_long/` (nur FULL_CANONICAL)
- `results/GS/k12_short/` (nur FULL_CANONICAL)
- `results/GS/meta/`

Archiv:
- `archive/GS_2026-01-10/` (Strategien/Results/Legacy, reversibel, kein Delete)

---

## 8) Naechster geplanter Ablauf

1) Freeze-Checkliste (Git/Unveraenderlichkeit/Read-only Gate)
2) Regime-Analyse-Vertiefung (read-only)
3) Erst danach: weitere Strukturarbeit (nur nach Entscheidung)

---

## 9) Regeln fuer weiteres Arbeiten (verbindlich)

- Keine Skripte duerfen auf FINAL schreiben.
- Jede neue Analyse erzeugt neue Outputs mit Timestamp.
- Keine Parallelversionen von Skripten mit Suffix; aktive Namen bleiben stabil.
- Ausfuehrungen ausschliesslich in WSL; Git Bash nur fuer Git.

