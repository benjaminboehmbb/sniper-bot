# EXIT TEST LOG – KOMPAKT

## Regeln
- 1 Änderung pro Run
- Bewertung ab 200k Ticks
- Full Reset vor jedem Run

## Kritische Fixes
- Position Handoff Fix → alte Runs ungültig
- Run Hygiene Fix → Logs verfälschten Ergebnisse
- Full Reset Pflicht

## Finaler Exit
- TP/SL: 5% / 2%
- LONG: 1x <= -1
- SHORT: 2x >= +2

---

## Verworfene Ansätze (kurz)
- 2x >= ±4 → schwach
- RSI / RSI+MFI → kein stabiler Effekt
- OR-Logik → zu viel Quantität
- 3x >= ±4 → zu restriktiv
- ADX hart → Undertrading
- ATR == 0 → keine Trades
- ATR != -1 → zu restriktiv

---

## Basisstrategie
Entry:
- 2x >= ±3 + ma200 + MFI
- Score: rsi + bollinger + stoch + cci

Problem:
- stabil bis 1M
- bricht bei 3M → Overtrading + DD

---

## Cooldown (180)
- reduziert Overtrading
- löst DD-Problem nicht

---

## ATR Hybrid (erste Version)
- ATR schlecht: 3x
- ATR normal: 2x

Ergebnis:
- Risiko gut
- aber zu wenig Edge bei 1M

---

## Entwicklungsschritte (entscheidend)

### 1. Cooldown 120
→ leichte Verbesserung, kein Durchbruch

---

### 2. Lockerung ATR schlecht (LONG)
→ mehr Trades, bessere Performance

---

### 3. Lockerung beidseitig (2x / 2x)
→ bester 200k-Run
→ aber 1M Run zeigt:
- DD zu hoch
- PF fällt
→ zu aggressiv

---

### 4. ATR differenziert (FINAL BASIS)
- ATR schlecht: 2x >= ±3
- ATR normal: 3x >= ±3

→ großer Fortschritt

---

### 5. Score 4 Test
- führt zu Undertrading
→ verworfen

---

### 6. FINALER KANDIDAT
👉 Kombination aus:

- ATR differenziert:
  - schlecht: 2x >= ±3
  - normal: 3x >= ±3
- dynamischer Cooldown:
  - normal: 120
  - schlecht: 200

---

## Ergebnisse (entscheidend)

### 200k Runs

| Offset | Return | PF   | DD    | Trades |
|--------|--------|------|-------|--------|
| 1M     | 6.95%  | 1.77 | 1.96% | 113    |
| 0      | 44.29% | 2.37 | 5.13% | 149    |
| 500k   | 11.04% | 4.52 | 0.75% | 134    |

👉 vollständig bestanden

---

### 500k Run @ 1.5M (kritisch)
- Return: 53%
- PF: 1.39 ❗
- DD: 30% ❗

→ zeigt:
**Regime-/DD-Problem auf langen Fenstern weiterhin vorhanden**

---

## Zentrale Erkenntnis

- Score ist **nicht** das Problem
- Entry-Logik ist **gut**
- Exit ist **stabil**

👉 Problem liegt in:
**Regime-Steuerung + Frequenzkontrolle über lange Zeiträume**

---

## Aktueller Status

```text
System funktioniert auf 200k sauber
System kippt auf 500k+ wegen DD


## 500k @ Offset 1,500,000 – Fail-Ursache

### Kernproblem
Die Strategie gewinnt oft, aber die Verluste sind zu groß.

- Wins: 106
- Losses: 45
- Avg Win: 92.36
- Avg Loss: -199.88

=> ein durchschnittlicher Verlust ist ca. 2.16x so groß wie ein durchschnittlicher Gewinn.

### Warum PF fast kaputt ist
- Sum Wins: 9,789.73
- Sum Losses: -8,994.75
- PF: 1.0884

=> Viele Gewinne werden fast vollständig von wenigen/zu großen Verlusten aufgefressen.

### Long/Short
Beide Seiten sind schwach:

- LONG PF: 1.0762
- SHORT PF: 1.0961

=> Kein einzelnes Seitenproblem. Gesamtlogik ist in diesem Fenster schwach.

### Exit Reasons
- CLOSE_LONG: 80
- CLOSE_SHORT: 64
- SL_SHORT: 4
- SL_LONG: 3

=> Das Problem sind nicht viele SL-Treffer.  
=> Problem sind große negative Signal-Exits und akkumulierte Verlustphasen.

### Wichtigste Erkenntnis
Das Loss-Cluster-Gate greift zu spät.

Es blockiert erst nach Verlusthäufung, aber verhindert nicht:
- große Einzelverluste
- zu spätes Schließen schlechter Trades
- Marktphasen mit schwacher Edge

### Konsequenz
Nicht Entry weiter optimieren.

Nächster sinnvoller Test:
Exit-/Risikologik verbessern, ohne Entry zu ändern.

Beste nächste Änderung:
Loss-Schutz prüfen.

Aber: Nicht sofort ändern, erst prüfen:
Welche Exit-Reason erzeugt die großen Verluste? also SL von 0.02 auf 0.015 geändert


## RUN – Loss-Cluster-Gate + SL 1.5% – 200k @ Offset 1,000,000

### Setup
- Datenbasis: `data/l1_full_run.csv`
- Run-Länge: 200,000 Ticks
- Offset: 1,000,000
- Entry: ATR-differenziert + MA200 + MFI
- Exit:
  - LONG: 1x <= -1
  - SHORT: 2x >= +2
- TP/SL:
  - TP: 5%
  - SL: **1.5% (neu, vorher 2%)**
- Zusatzlogik: Loss-Cluster-Gate
  - 5 Verluste aus letzten 10 Trades → 25 Entry-Block

---

### Ergebnis
| Kennzahl | Wert |
|---|---:|
| Startkapital | 10,000.00 |
| Endkapital | 10,396.72 |
| Gewinn | 396.72 |
| Return | 3.97% |
| Trades | 79 |
| Winrate | 70.89% |
| Profit Factor | 1.5045 |
| Avg PnL | 5.0218 |
| Avg Duration | 2,160.76 sec |
| Max Drawdown | 213.70 |
| Max Drawdown % | 2.03% |
| Sharpe-like | 1.3083 |

---

### Einordnung

Der Run bestätigt die Wirkung der SL-Anpassung.

- Trade-Anzahl unverändert → Entry bleibt stabil
- Winrate stabil → keine Verschlechterung der Signalqualität
- Profit Factor leicht reduziert → erwarteter Effekt durch früheres Stoppen
- Drawdown weiterhin sehr niedrig → Risiko stabil kontrolliert

---

### Vergleich zur vorherigen Version (SL 2%)

| Kennzahl | SL 2% | SL 1.5% |
|---|---:|---:|
| PF | 1.64 | 1.50 |
| DD | ~2.0% | ~2.0% |
| Trades | 79 | 79 |
| Return | 4.62% | 3.97% |

👉 Interpretation:
- Weniger Gewinn pro Trade (früheres Stoppen)
- Dafür bessere Kontrolle potenzieller großer Verluste

---

### Zentrale Erkenntnis

Die Anpassung wirkt genau wie beabsichtigt:

- Reduktion von Loss-Spikes
- Stabilisierung der Risikostruktur
- Keine Veränderung der Entry-Logik

👉 Grundlage für robuste Long-Runs verbessert

---

### Bewertung

- Risiko: sehr gut
- Stabilität: hoch
- Profitabilität: gut
- Systemverhalten: kontrolliert und konsistent

---

### Entscheidung

✅ SL = 1.5% bleibt aktiv  
✅ Loss-Cluster-Gate bleibt aktiv  
❌ keine weiteren Änderungen

---

### Nächster Schritt

Validierung im kritischen Fenster:

→ **500k @ Offset 1,500,000**

Ziel:
- PF deutlich > 1.3
- Drawdown signifikant reduziert gegenüber vorherigem Fail (~39%)

---

### Archiv

```bash
cp live_logs/trades_l1.jsonl live_logs/archive/trades_loss_cluster_SL15_200k_offset_1000000.jsonl
cp live_logs/trades_l1_auto_analysis.csv live_logs/archive/analysis_loss_cluster_SL15_200k_offset_1000000.csv


## RUN – Loss-Cluster-Gate + SL 1.5% – 500k @ Offset 1,500,000

### Setup
- Datenbasis: `data/l1_full_run.csv`
- Run-Länge: 500,000 Ticks
- Offset: 1,500,000
- Entry: ATR-differenziert + MA200 + MFI
- Exit:
  - LONG: 1x <= -1
  - SHORT: 2x >= +2
- TP/SL:
  - TP: 5%
  - SL: 1.5%
- Zusatzlogik: Loss-Cluster-Gate (5/10 → 25 Block)

---

### Ergebnis
| Kennzahl | Wert |
|---|---:|
| Startkapital | 10,000.00 |
| Endkapital | 11,187.57 |
| Gewinn | 1,187.57 |
| Return | 11.88% |
| Trades | 151 |
| Winrate | 70.20% |
| Profit Factor | 1.1345 |
| Avg PnL | 7.8647 |
| Avg Duration | 1,983.97 sec |
| Max Drawdown | 3,812.45 |
| Max Drawdown % | 33.08% |
| Sharpe-like | 1.0737 |

---

### Vergleich zum vorherigen Fail (SL 2%)

| Kennzahl | SL 2% | SL 1.5% |
|---|---:|---:|
| PF | 1.088 | 1.134 |
| DD | 38.9% | 33.1% |
| Return | 7.95% | 11.88% |
| Trades | 151 | 151 |

---

### Einordnung

Die SL-Anpassung wirkt, aber **nicht ausreichend**:

**Verbesserungen:**
- PF leicht gestiegen
- Return deutlich gestiegen
- DD reduziert (~ -6%)

**Problem bleibt:**
- DD weiterhin viel zu hoch (>30%)
- PF weiterhin zu niedrig (~1.13)
- Trades unverändert hoch → Aktivität weiterhin zu groß in schlechten Phasen

---

### Zentrale Erkenntnis

👉 Das Problem ist NICHT nur die Größe der Verluste  
👉 Das Problem ist die **Frequenz schlechter Trades in bestimmten Marktphasen**

- SL reduziert Schaden pro Trade  
- aber verhindert nicht:
  - Serien schlechter Trades
  - lange Drawdown-Phasen

---

### Fazit

❌ System weiterhin **nicht robust**  
❌ Loss-Cluster + SL reicht nicht aus  

👉 Verbesserung vorhanden, aber strukturelles Problem ungelöst

---

### Nächste Richtung (klar)

Du brauchst jetzt **präventive Aktivitätskontrolle**, nicht nur:
- reaktives Gate (Loss-Cluster)
- oder kleinere Verluste (SL)

---

### Konkrete nächste sinnvolle Maßnahme

👉 **Entry-Frequenz reduzieren in schlechten Phasen**

Ansatz:
- strengere Bedingungen bei schwachem Markt
- oder dynamischer Cooldown / Aktivitätsfilter

Beispiel (noch nicht implementieren):
- höhere Score-Anforderung bei schlechtem ATR
- zusätzlicher Filter (z. B. ADX oder Trendstärke)

---

### Entscheidung

❌ Keine weiteren Runs mit aktueller Logik sinnvoll  
👉 erst strukturelle Verbesserung notwendig

---

### Archiv

```bash
cp live_logs/trades_l1.jsonl live_logs/archive/trades_loss_cluster_SL15_500k_offset_1500000.jsonl
cp live_logs/trades_l1_auto_analysis.csv live_logs/archive/analysis_loss_cluster_SL15_500k_offset_1500000.csv


## RUN – Loss-Cluster-Gate + SL 1.5% + ATR-strict – 200k @ Offset 1,000,000

### Setup
- Datenbasis: `data/l1_full_run.csv`
- Run-Laenge: 200,000 Ticks
- Offset: 1,000,000
- Entry:
  - MA200 + MFI Filter
  - ATR normal: 3x >= +/-3
  - ATR schlecht: 3x >= +/-4
- Exit unveraendert:
  - LONG: 1x <= -1
  - SHORT: 2x >= +2
- TP/SL:
  - TP: 5%
  - SL: 1.5%
- Zusatzlogik:
  - Loss-Cluster-Gate aktiv
  - 5 Verluste aus 10 Trades -> 25 Entry-Block

---

### Ergebnis
| Kennzahl | Wert |
|---|---:|
| Startkapital | 10,000.00 |
| Endkapital | 10,288.48 |
| Gewinn | 288.48 |
| Return | 2.88% |
| Trades | 18 |
| Winrate | 83.33% |
| Profit Factor | 6.4185 |
| Avg PnL | 16.0267 |
| Avg Duration | 2,143.33 sec |
| Max Drawdown | 38.27 |
| Max Drawdown % | 0.37% |
| Sharpe-like | 3.1360 |

---

### Einordnung
Der ATR-strict-Filter wirkt stark risikoreduzierend.

- Profit Factor extrem verbessert
- Drawdown nahezu eliminiert
- Winrate deutlich verbessert
- Trade-Anzahl stark reduziert

Der Run ist qualitativ sehr stark, aber deutlich restriktiver als die vorherige Variante.

---

### Vergleich zur vorherigen SL-1.5%-Variante

| Kennzahl | SL 1.5% | SL 1.5% + ATR-strict |
|---|---:|---:|
| Return | 3.97% | 2.88% |
| Trades | 79 | 18 |
| Winrate | 70.89% | 83.33% |
| PF | 1.5045 | 6.4185 |
| DD | 2.03% | 0.37% |

---

### Bewertung
- Risiko: exzellent
- Drawdown: exzellent
- Signalqualitaet: sehr hoch
- Aktivitaet: sehr niedrig
- Profitabilitaet: gut, aber durch starke Filterung begrenzt

---

### Entscheidung
Der Test ist bestanden.

ATR-strict bleibt als Kandidat aktiv, muss aber im kritischen Long-Run geprueft werden:

→ 500k @ Offset 1,500,000

Nur dort zeigt sich, ob der Filter den bisherigen Drawdown-Fail wirklich behebt.
### Archiv
```bash
mkdir -p live_logs/archive

cp live_logs/trades_l1.jsonl live_logs/archive/trades_loss_cluster_SL15_ATRstrict_200k_offset_1000000.jsonl
cp live_logs/trades_l1_auto_analysis.csv live_logs/archive/analysis_loss_cluster_SL15_ATRstrict_200k_offset_1000000.csv







