# Strategy Realism Guide — Sniper-Bot

**Quelle:** *Quantitative Trading – How to Build Your Own Algorithmic Trading Business*  
(Ernest P. Chan)

**Zweck:** Sicherstellung, dass alle Strategien im Sniper-Bot
ökonomisch realistisch, handelbar und langfristig überlebensfähig sind.

**Abgrenzung:**  
Dieses Dokument ergänzt AFML-, ML- und System-Policies.
Bei Konflikten gelten:
AFML → Strategy Realism → ML → System.

---

## Grundprinzip (verbindlich)

> Eine einfache, robuste Strategie mit realistischen Annahmen
> schlägt jede komplexe Strategie mit idealisierten Backtests.

---

## 1. Strategietypen — realistische Präferenz

### Bevorzugt
- Mean Reversion (mit klaren Grenzen)
- Regime-abhängige Trendstrategien
- Volatilitätsbasierte Filter
- Low-Turnover-Ansätze

### Nur eingeschränkt
- Hochfrequente Signale
- Intraday-Scalping
- Stark korrelierte Multi-Filter-Setups

### Nicht erlaubt
- Strategien mit extrem hohem Turnover
- Strategien ohne Kosten-/Slippage-Resistenz
- „Curve-Fit“-Strategien mit vielen Freiheitsgraden

---

## 2. Kosten, Slippage, Turnover (verbindlich)

- Jede Strategie wird **mit konservativen Kosten** bewertet
- Turnover ist ein zentrales Risikomaß
- Performance **nach Kosten** ist die einzige relevante Metrik

**Regel:**  
Eine Strategie, die nur ohne Kosten funktioniert, ist wertlos.

---

## 3. Robustheitsanforderungen

- Stabilität über Marktregime
- Keine Abhängigkeit von Einzeljahren
- Keine extreme Sensitivität auf Parameter

**Regel:**  
Robustheit schlägt maximale Rendite.

---

## 4. Erwartungsmanagement

- Keine exponentiellen Wachstumsannahmen
- Keine „Verdopplungs“-Narrative
- Fokus auf Kapitalerhalt + stetiges Wachstum

---

## 5. Explizite No-Gos

- Strategien mit unrealistischen Fills
- Nutzung von illiquiden Marktphasen
- Überoptimierung auf Sharpe oder CAGR
- Annahmen institutioneller Ausführungsqualität

---

## Abschlussregel

> Wenn eine Strategie in der Realität schwer erklärbar,
> schwer ausführbar oder psychologisch nicht haltbar ist,
> gehört sie nicht in den Sniper-Bot.

---

**Dokumentenstatus:** FINAL  
**Änderungen:** Nur mit expliziter Begründung und Versionsupdate erlaubt.
