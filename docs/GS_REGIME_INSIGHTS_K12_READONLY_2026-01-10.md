# GS Regime Insights — K12 Canonical (READ-ONLY)
Projekt: Sniper-Bot — Gold-Standard (simtraderGS)  
Datum: 2026-01-10  
Status: READ-ONLY Analyse (kein Re-Run, keine Code-Aenderungen)

---

## Zweck
Diese Datei fasst **strukturierte, datenbasierte Einsichten** zur Regime-Wirkung
des **kanonischen K12-Stacks** zusammen. Grundlage sind **ausschliesslich**
die vorhandenen Canonical Results (LONG/SHORT), identische Offsets und das
fixe Fee-Modell.  
**Keine Empfehlungen zur Code-Aenderung, keine neuen Runs.**

---

## Grundlagen (fix)
- Instrument: BTCUSDT (1m)
- Fenster: 200 000 Rows
- Offsets: 0 / 500k / 1 000k / 1 500k
- Fee (roundtrip): 0.0004
- Regime-Gate: aktiv, asymmetrisch (`allow_long` / `allow_short`)
- K-Endpunkt: K12 (12/12 Signale, ungewichtet, Kurzkeys)

---

## 1) Offset-Stabilitaet (Worst/Best Case)

### LONG (Canonical)
- **Worst Case:** Offset 0 (deutlich negativer `roi_fee`)
- **Stabilisierung:** Offsets 500k und 1M
- **Best Case:** Offset 1.5M (geringster negativer `roi_fee`)

**Interpretation:**  
Der LONG-Stack reagiert empfindlich auf fruehe Marktphasen im Sample,
stabilisiert sich jedoch in spaeteren Fenstern. Das deutet auf
**Trend-Fortsetzungs- und Mean-Reversion-Phasen** hin, in denen LONG
strukturbedingt besser traegt.

### SHORT (Canonical)
- **Worst Case:** Offset 0 (ebenfalls deutlich negativ)
- **Best Case:** Offset 500k
- **Schwaecher:** Offsets 1M und 1.5M (relativ hoehere Verluste nach Fee)

**Interpretation:**  
SHORT profitiert kurzfristig von bestimmten Phasen, verliert aber
strukturell in spaeteren Fenstern an Effizienz.

---

## 2) Robustheit (p25 / mean)

### Beobachtung
- **LONG:** besseres `roi_fee_p25` und `roi_fee_mean`
- **SHORT:** leicht schlechtere Robustheit in beiden Kennzahlen

### Bedeutung
- LONG ist **robuster gegen unguenstige Zeitfenster**
- SHORT ist **sensitiver** gegen Phasenwechsel und akkumuliert
  mehr Fee-Druck

**Schlussfolgerung (deskriptiv):**  
Bei identischer Struktur ist LONG der **robustere Default** im GS-Fenster.

---

## 3) Trade-Last vs Fee-Druck

### Beobachtung
- **SHORT** hat signifikant **mehr Trades**
- **LONG** handelt weniger bei aehnlicher Signalstruktur

### Wirkung
- Hoehere Trade-Last -> hoeherer kumulativer Fee-Abzug
- SHORT wird dadurch strukturell benachteiligt, selbst wenn
  Roh-ROI vergleichbar waere

**Schlussfolgerung:**  
SHORT benoetigt **staerkere Regime-Filterung**, um nicht durch Fees
dominiert zu werden.

---

## 4) Regime-Sensitivitaet (Hypothesen, keine Implementierung)

> Hinweis: Dies sind **Hypothesen**, keine Ableitungen fuer Code-Aenderungen.

### Bull-Markt / Aufwaertstrend
- LONG profitiert strukturell
- SHORT erhoeht Trade-Last ohne ausreichende Kompensation

**Erwartung:** LONG priorisieren, SHORT stark drosseln

### Bear-Markt / Abwaertstrend
- SHORT kann kurzfristig tragen
- Risiko: hohe Aktivitaet + Fees

**Erwartung:** SHORT nur selektiv, starke Gate-Bedingungen notwendig

### Seitwaerts / Chop
- Beide Seiten problematisch
- Fee-Druck dominiert

**Erwartung:** Aktivitaet beider Seiten reduzieren

---

## 5) Implikationen fuer spaetere Phasen (nur konzeptionell)

Ohne Umsetzung:
- Regime-Gewichtung (LONG/SHORT) ist **entscheidender** als weitere
  Signalverfeinerung im K12-Endpunkt.
- Fee-Sensitivitaet muss im Live-Betrieb explizit beruecksichtigt werden.
- K12 ist ein **Struktur-Endpunkt**, kein Performance-Endpunkt.

---

## 6) Grenzen dieser Analyse

- Keine zeitpunktgenaue Regime-Zuordnung (kein Re-Run).
- Keine Segmentierung innerhalb der Fenster.
- Keine Optimierungsaussagen.

Diese Analyse dient ausschliesslich der **Einordnung und Dokumentation**.

---

## Fazit (in einem Satz)

Der kanonische K12-Stack ist strukturell konsistent; **LONG ist robuster und fee-effizienter**, waehrend **SHORT stark regime- und fee-sensitiv** ist — die Qualitaet kuenftiger Ergebnisse haengt primär von **Regime-Steuerung**, nicht von weiterer Struktur-Erhoehung ab.

---
