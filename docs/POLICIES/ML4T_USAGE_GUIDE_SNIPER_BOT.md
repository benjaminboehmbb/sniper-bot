# ML Usage Guide — Sniper-Bot

**Quelle:** *Machine Learning for Algorithmic Trading* (Stefan Jansen)  
**Zweck:** Praktische Leitlinie für den kontrollierten Einsatz von Machine Learning
im Sniper-Bot-Projekt unter Einhaltung der AFML-Policy.

**Abgrenzung:**  
Dieses Dokument ergänzt die AFML-Alignment-Policy.  
Bei Konflikten gilt **AFML_ALIGNMENT_SNIPER_BOT.md** vorrangig.

---

## Grundprinzip (verbindlich)

> Machine Learning ist im Sniper-Bot ein **Werkzeug zur Verfeinerung**,
> nicht zur Entdeckung von Alpha ohne theoretische Grundlage.

ML darf **nur** eingesetzt werden, wenn:
- die Datenpipeline stabil ist
- das Signalproblem klar definiert ist
- Overfitting-Risiken explizit adressiert sind

---

## 1. Erlaubte Einsatzbereiche von ML

### 1.1 Feature-Bewertung & Selektion
**Zweck:**
- Relevanz bestehender Signale quantifizieren
- Redundanzen erkennen
- Stabilität über Zeitfenster prüfen

**Erlaubt:**
- Tree-based Feature Importance
- Permutation Importance
- SHAP (nur explorativ)

**Nicht erlaubt:**
- Feature Discovery ohne ökonomische Begründung

---

### 1.2 Signal-Filter & Meta-Modelle
**Zweck:**
- Entscheidung *Trade ja/nein*
- Qualitätsfilter auf bestehende Strategien

**Erlaubt:**
- Binary Classifier (Trade / No Trade)
- Meta-Labeling auf bestehenden Signalen

**Nicht erlaubt:**
- ML als alleinige Entry-Logik
- Blackbox-Entries ohne erklärbare Struktur

---

### 1.3 Regime- & Kontextmodelle
**Zweck:**
- Marktphasen klassifizieren
- Strategien kontextabhängig aktivieren/deaktivieren

**Erlaubt:**
- Regime-Classifier (Bull/Bear/Sideways)
- Volatilitäts- oder Liquiditätskontext

**Nicht erlaubt:**
- Dynamisches Umschalten ohne Stabilitätsprüfung

---

## 2. Modellklassen — klare Präferenz

### Bevorzugt (robust, interpretierbar)
- Random Forest
- Gradient Boosting (XGBoost, LightGBM)
- Regularisierte lineare Modelle

### Nur eingeschränkt
- Neural Networks (MLP)
- LSTM / RNN

### Aktuell ausgeschlossen
- Reinforcement Learning
- GANs
- End-to-End Deep Learning
- AutoML ohne Kontrolle

---

## 3. Trainings- & Evaluationsregeln (verbindlich)

- Keine klassischen K-Fold-CVs
- Zeitbasierte Splits zwingend
- Keine Hyperparameter-Optimierung ohne Out-of-Sample-Gates
- Performance immer relativ zu:
  - No-ML-Baseline
  - einfachen heuristischen Filtern

---

## 4. Backtesting & Integration

- ML-Modelle dürfen **nicht** auf GS-Freeze-Daten trainiert werden
- Training, Evaluation und Einsatz strikt getrennt
- Ergebnisse werden **niemals** isoliert bewertet,
  sondern immer im Gesamtsystem (Drawdown, Stability, Failure Risk)

---

## 5. Explizite No-Gos (verbindlich)

- ML vor klarer Signaldefinition
- ML zur Rendite-Maximierung ohne Robustheitsmetriken
- Komplexere Modelle ohne signifikanten Mehrwert
- Optimierung auf Sharpe oder Return allein

---

## 6. Roadmap-Einordnung

| Phase | ML-Einsatz |
|-----|-----------|
| GS | ❌ nicht erlaubt |
| L1 (Paper) | ⚠️ explorativ |
| L2 (Live Prep) | ✅ selektiv |
| L3+ | ✅ erweitert |

---

## Abschlussregel

> Wenn ein ML-Modell nicht erklären kann,
> **warum** es eine Entscheidung trifft,
> ist es im Sniper-Bot nicht produktionsreif.

---

**Dokumentenstatus:** FINAL  
**Änderungen:** Nur mit expliziter Begründung und Versionsupdate erlaubt.
