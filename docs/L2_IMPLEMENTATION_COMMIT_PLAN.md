# L2_IMPLEMENTATION_COMMIT_PLAN

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: FINAL – Implementierungsplan (codefrei)
Datum: 2026-01-11

Zweck:
Dieses Dokument definiert die exakte, schrittweise Reihenfolge
für die Implementierung von L2 in einem einzigen sauberen Commit.
Es verhindert Scope-Leaks, Improvisation und Fixes im Betrieb.

Keine Implementierung, kein Code, keine Tests.

================================================================
0. Grundregeln (verbindlich)
================================================================

- L2 wird in genau EINEM Commit implementiert.
- L1-Code und L1-Config bleiben unverändert.
- Bei Unsicherheit gilt: STOP.
- Kein Schritt darf übersprungen werden.
- Jeder Schritt hat ein klares Stop-Kriterium.

================================================================
1. Vorbereitung (vor dem Commit)
================================================================

1.1 Status prüfen
- STATUS_SNAPSHOT_2026-01-11_L1-L2.md lesen
- L1-Beobachtungsfenster abgeschlossen?
- Formale Entscheidung „L1 FREIGEGEBEN“ liegt vor?

Stop-Kriterium:
- Wenn eine Antwort „Nein“ ist → Arbeit abbrechen.

----------------------------------------------------------------
1.2 Dokumente verifizieren
- L2-Mandat FINAL
- L2 Start Conditions & Guards FINAL
- L2 Minimal-Architektur FINAL
- L2 Decision-Matrix FINAL
- L2 File & Interface Map FINAL
- L2 Pre-Mortem FINAL

Stop-Kriterium:
- Fehlendes oder unfertiges Dokument → abbrechen.

================================================================
2. Repo-Struktur anlegen
================================================================

2.1 L2 Namespace erstellen
- Neuer Ordner/Namespace für L2
- Keine Abhängigkeiten zu L1-Write-Pfaden

Erwartetes Ergebnis:
- Leere, saubere Struktur
- Keine Seiteneffekte

Stop-Kriterium:
- Unsicherheit über Trennung zu L1 → abbrechen.

================================================================
3. Datenverträge fixieren
================================================================

3.1 Strategie-Identifikation
- Mechanismus zur stabilen strategy_id-Erkennung
- strategy_hash nur aus GS FINAL Inhalten

Erwartetes Ergebnis:
- Strategie eindeutig identifizierbar
- Integrität prüfbar

Stop-Kriterium:
- Mehrdeutige IDs oder instabile Hashes → abbrechen.

----------------------------------------------------------------
3.2 Input-Schnittstellen definieren
- Markt-Snapshot-Reader (read-only)
- Regime-Reader (read-only)
- L1-Health/State-Reader (read-only)

Erwartetes Ergebnis:
- Inputs klar getrennt
- Kein Write-Zugriff auf L1

Stop-Kriterium:
- Notwendigkeit eines Write-Zugriffs → abbrechen.

================================================================
4. Entscheidungslogik implementieren
================================================================

4.1 Dimensionen D1–D4
- Jede Dimension isoliert prüfbar
- Ergebnis: true/false + reason code

Erwartetes Ergebnis:
- Vollständig binäre Entscheidungsbasis

Stop-Kriterium:
- Gewichtungen, Scores oder Heuristiken → abbrechen.

----------------------------------------------------------------
4.2 Decision Aggregation
- ALLOW nur wenn D1–D4 true
- Default BLOCK

Erwartetes Ergebnis:
- Deterministische Entscheidung

Stop-Kriterium:
- Mehrdeutige Entscheidungsfälle → abbrechen.

================================================================
5. Guards & Stoppsicherheit
================================================================

5.1 L1-Alarm-Guard
- Alarm-Flag prüfen
- Bei Alarm: L2 deaktivieren (fail-closed)

Erwartetes Ergebnis:
- Keine Entscheidungen bei Alarm

Stop-Kriterium:
- L2 produziert Output trotz Alarm → abbrechen.

----------------------------------------------------------------
5.2 Reproduzierbarkeits-Guard
- Identische Inputs → identische Outputs

Erwartetes Ergebnis:
- Audit-Replay möglich

Stop-Kriterium:
- Nicht reproduzierbare Entscheidung → abbrechen.

================================================================
6. Logging & Audit
================================================================

6.1 Audit-Record erzeugen
- Append-only
- Vollständiges Schema gemäß Design

Erwartetes Ergebnis:
- Jede Entscheidung nachvollziehbar

Stop-Kriterium:
- Fehlende Felder oder implizite Annahmen → abbrechen.

----------------------------------------------------------------
6.2 Optional: Latest Decision Pointer
- Überschreibbar
- Kein Audit-Ersatz

Erwartetes Ergebnis:
- Bequemer Zugriff ohne Kopplung

Stop-Kriterium:
- Verwechslung mit Audit-Log → abbrechen.

================================================================
7. Interne Validierung (ohne Live-Kopplung)
================================================================

7.1 Offline-Replay
- Gleiche Inputs mehrfach prüfen

Erwartetes Ergebnis:
- Identische Outputs

Stop-Kriterium:
- Abweichungen → abbrechen.

----------------------------------------------------------------
7.2 L1-Unberührtheit prüfen
- L1 läuft parallel unverändert

Erwartetes Ergebnis:
- Keine L1-Seiteneffekte

Stop-Kriterium:
- Jegliche L1-Veränderung → abbrechen.

================================================================
8. Commit & Abschluss
================================================================

8.1 Single Commit erstellen
- Alle L2-Dateien in einem Commit
- Klarer Commit-Text: „L2 implementation (initial)“

8.2 Post-Commit Pause
- Keine sofortige Aktivierung
- Beobachtung, Dokumentation

================================================================
9. Zentrale Leitregel
================================================================

Wenn während irgendeines Schrittes der Gedanke entsteht:
„Das könnten wir schnell fixen …“

→ Arbeit sofort stoppen.
→ Pre-Mortem lesen.
→ Entscheidung vertagen.

ENDE
