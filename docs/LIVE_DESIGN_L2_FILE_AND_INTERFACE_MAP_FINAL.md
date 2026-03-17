# LIVE_DESIGN_L2_FILE_AND_INTERFACE_MAP_FINAL

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: FINAL – Design-Addendum (codefrei)
Datum: 2026-01-11

Zweck:
Dieses Dokument definiert die exakten Datei-, Pfad- und Schnittstellen-
Zuordnungen für L2. Es dient als verbindlicher Bauplan, um L2 in einem
einzigen sauberen Commit zu implementieren, ohne L1 zu berühren.
Keine Implementierung, kein Code, keine Optimierung.

----------------------------------------------------------------
0. Grundprinzipien (verbindlich)
----------------------------------------------------------------
- L2 ist vollständig read-only gegenüber L1 und GS.
- L2 erzeugt ausschließlich eigene, append-only Outputs.
- L2 ist jederzeit deaktivierbar, ohne Seiteneffekte.
- L1 bleibt autonom und funktionsfähig ohne L2.

----------------------------------------------------------------
1. Input-Quellen (READ-ONLY)
----------------------------------------------------------------

1.1 GS Strategien (FINAL)
Pfad:
- strategies/GS/LONG_FINAL_CANONICAL/
- strategies/GS/SHORT_FINAL/

Erwartete Inhalte:
- eine Strategie pro Datei
- eindeutige strategy_id (implizit oder explizit)
- deterministischer Inhalt (keine Zufälligkeit)

Verwendung in L2:
- Identifikation der zu bewertenden Strategie
- Berechnung eines stabilen strategy_hash zur Integritätsprüfung

----------------------------------------------------------------
1.2 Markt-Snapshot / Marktfenster
Quelle:
- identisch zur L1-Marktquelle (keine Transformation)
- Zugriff ausschließlich read-only

Minimal benötigte Felder:
- timestamp_utc (ISO-Format, UTC)
- price (float)
- snapshot_id oder window_id

Zeitbasis:
- UTC, monoton steigend

----------------------------------------------------------------
1.3 Regime-Information
Quelle:
- GS-kompatible Regime-Labels (z. B. regime_v1)
- identische Quelle wie in GS/L1-Umfeld

Minimal benötigte Felder:
- timestamp_utc
- regime_label (z. B. +1 / -1 oder ENUM)
- regime_id (optional)

Regeln:
- Regime muss zeitlich zum Markt-Snapshot passen
- fehlendes oder inkonsistentes Regime ⇒ BLOCK

----------------------------------------------------------------
1.4 L1 Betriebszustand & Health
Quellen (read-only):
- live_l1_alert.flag
- ausgewählte L1-State-Dateien (z. B. Risk-State)

Verwendung:
- Prüfung der Betriebsstabilität (D3)
- Kein Schreiben, kein Löschen, kein Reset

Regel:
- Existenz oder Inhalt eines Alarm-Flags ⇒ L2 deaktivieren

----------------------------------------------------------------
2. Output-Artefakte (L2-eigenständig)
----------------------------------------------------------------

2.1 L2 Decision Audit Log
Pfad (Beispiel):
- l2_logs/decision_audit.jsonl

Eigenschaften:
- append-only
- keine Überschreibung
- keine Abhängigkeit von L1

Record-Schema (verbindlich):
- timestamp_utc
- decision: ALLOW | BLOCK
- strategy_id
- strategy_hash
- dimension_results:
  - D1_regime_consistent: true/false
  - D2_market_context_consistent: true/false
  - D3_l1_stable: true/false
  - D4_strategy_integrity_ok: true/false
- reasons: [string, ...]
- input_refs:
  - snapshot_id / window_id
  - regime_id (optional)
  - l1_state_ref (optional)
- l2_version (commit hash)

----------------------------------------------------------------
2.2 Optional: Latest Decision Pointer
Pfad (optional):
- l2_state/latest_decision.json

Eigenschaften:
- überschreibbar
- rein optional
- L1 kann diese Datei lesen oder ignorieren

Inhalt:
- Verweis auf letzte Entscheidung
- kein Audit-Ersatz (Audit bleibt JSONL)

----------------------------------------------------------------
3. Schnittstellen-Definition
----------------------------------------------------------------

3.1 L1 → L2
- ausschließlich read-only
- keine direkten Funktionsaufrufe
- kein Blocking-Verhalten

3.2 L2 → L1
- keine verpflichtende Kopplung
- L1 darf L2-Ausgaben ignorieren
- kein Rückkanal, keine Steuerung

----------------------------------------------------------------
4. Fail-Closed & Abbruchregeln
----------------------------------------------------------------
- Fehlender Input ⇒ BLOCK
- Inkonsistenter Input ⇒ BLOCK
- L1 Alarm ⇒ sofortige Deaktivierung von L2
- Nicht reproduzierbare Entscheidung ⇒ STOP L2

Deaktivierung bedeutet:
- L1 läuft unverändert weiter
- L2-Ausgaben werden ignoriert
- Ursache wird dokumentiert, nicht behoben

----------------------------------------------------------------
5. Explizite Nicht-Ziele
----------------------------------------------------------------
L2 macht NICHT:
- neue Signale berechnen
- Strategien verändern
- Performance bewerten
- Kapital allokieren
- Trades ausführen
- Guards von L1 überschreiben

----------------------------------------------------------------
6. Status
----------------------------------------------------------------
Dokumentstatus: FINAL
Änderungen: nur nach Review erlaubt
Implementierung: noch nicht begonnen

ENDE
