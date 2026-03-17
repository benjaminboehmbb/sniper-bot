# AFML-Alignment-Checkliste — Sniper-Bot

**Quelle:** *Advances in Financial Machine Learning* (Marcos López de Prado)  
**Zweck:** Formale Absicherung des Sniper-Bot-Designs gegen Overfitting, falsche Backtests und unsaubere Forschungslogik.  
**Prinzip:** Dieses Dokument ist **verbindlich**. Abweichungen müssen explizit begründet werden.

---

## Statuscodes
- **OK** = bereits korrekt umgesetzt
- **SPÄTER** = bewusst geplant, aktuell nicht erforderlich
- **FEHLT** = sollte ergänzt werden (konkret benannt)

---

## A. Meta-Strategie & Forschungsprozess

1. **Meta-Strategie statt Einzelsuche**  
   **AFML:** Kapitel 1 (Meta-Strategy Paradigm)  
   **Regel:** Wert entsteht durch eine reproduzierbare Pipeline, nicht durch einzelne Strategien.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** K-Stufen (K3–K12), Seed-Expansion, Factory-Denken vorhanden.

2. **Strikte Trennung: Research / Evaluation / Betrieb**  
   **AFML:** Kapitel 1, 11  
   **Regel:** Backtests sind kein Research-Werkzeug.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** GS → L1 → Live klar getrennt.

3. **Reproduzierbarkeit vor Performance**  
   **AFML:** Kapitel 1, 11  
   **Regel:** Ohne reproduzierbaren Prozess ist jede Rendite wertlos.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** Versionierung, Freeze-Policies, deterministische Runs.

---

## B. Daten, Labels, Samples

4. **Nicht-IID-Samples explizit berücksichtigen**  
   **AFML:** Kapitel 4  
   **Regel:** Überlappende Trades verzerren Statistik ohne Gewichtung.  
   **Sniper-Bot Status:** SPÄTER  
   **Kommentar:** Relevant bei ML-/Meta-Label-Layer.

5. **Label-Design ist ein Modellentscheid**  
   **AFML:** Kapitel 3 (Triple-Barrier, Meta-Labeling)  
   **Regel:** Labels definieren das Lernproblem stärker als Algorithmen.  
   **Sniper-Bot Status:** SPÄTER  
   **Kommentar:** Erst relevant bei probabilistischen Entries.

6. **Keine zeitlichen Leaks**  
   **AFML:** Kapitel 2, 7  
   **Regel:** Kein Feature darf implizit Zukunftsinformation enthalten.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** Saubere 1m-Daten, UTC, klare Time-Index-Logik.

---

## C. Cross-Validation & Overfitting

7. **K-Fold-CV ist für Finanzdaten ungeeignet**  
   **AFML:** Kapitel 7  
   **Regel:** Purging + Embargo sind Pflicht.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** Kein klassisches CV eingesetzt.

8. **Backtest-Overfitting ist unvermeidbar, aber messbar**  
   **AFML:** Kapitel 11–12  
   **Regel:** Jeder Backtest ist überfit – entscheidend ist das Ausmaß.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** Quantile-Gates, konservative Metriken.

9. **Multiple-Testing-Risiko explizit einpreisen**  
   **AFML:** Kapitel 11  
   **Regel:** Viele Versuche ⇒ hohe False-Discovery-Rate.  
   **Sniper-Bot Status:** OK  
   **Kommentar:** Systematische K-Expansion statt Cherry-Picking.

---

## D. Bewertung & Metriken

10. **Sharpe Ratio ist nicht ausreichend**  
    **AFML:** Kapitel 14–15  
    **Regel:** Failure-Probability, Drawdown, Runs sind entscheidend.  
    **Sniper-Bot Status:** OK  
    **Kommentar:** Fokus auf p25, MaxDD, Robustheit.

11. **Robuste Quantile schlagen Mittelwerte**  
    **AFML:** Kapitel 14  
    **Regel:** Entscheidungen auf konservativen Quantilen treffen.  
    **Sniper-Bot Status:** OK  
    **Kommentar:** p25 als zentrales Gate.

12. **Backtests sind Hypothesen, keine Prognosen**  
    **AFML:** Kapitel 11  
    **Regel:** Historische Simulation ist kein Zukunftsversprechen.  
    **Sniper-Bot Status:** OK  
    **Kommentar:** Verpflichtende Paper-Trading-Phase.

---

## E. Risiko, Sizing, Allokation

13. **Signal und Positionsgröße strikt trennen**  
    **AFML:** Kapitel 10  
    **Regel:** Ein Signal bestimmt Richtung, nicht Kapital.  
    **Sniper-Bot Status:** SPÄTER  
    **Kommentar:** Relevant für L2/L3 (dynamisches Sizing).

14. **Robuste Allokation statt Optimierung**  
    **AFML:** Kapitel 16  
    **Regel:** Out-of-sample-Stabilität schlägt In-Sample-Optimalität.  
    **Sniper-Bot Status:** SPÄTER  
    **Kommentar:** Relevant bei Portfolio mehrerer Strategien.

---

## F. Grundsatz (verbindlich)

> **Overfitting ist kein technischer Fehler, sondern ein Prozessfehler.**  
> Jede Design-Entscheidung im Sniper-Bot muss begründen können,  
> **welches Overfitting-Risiko sie reduziert.**

---

**Dokumentenstatus:** FINAL  
**Änderungen:** Nur mit expliziter Begründung und Versionsupdate erlaubt.
