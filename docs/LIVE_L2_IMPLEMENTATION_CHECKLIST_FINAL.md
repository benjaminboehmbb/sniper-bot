# LIVE_L2_IMPLEMENTATION_CHECKLIST_FINAL

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: FINAL – Implementierungs-Checkliste (codefrei)
Datum: 2026-01-11

Zweck:
Diese Checkliste definiert die vollständigen, verbindlichen Schritte zur
Implementierung von L2 (ALLOW/BLOCK-Entscheidungsfreigabe) nach erfolgreichem
L1-Exit. Sie ist stop-orientiert, codefrei und garantiert, dass L1 unangetastet
bleibt. Ziel ist ein einziger sauberer L2-Implementierungs-Commit.

----------------------------------------------------------------
A. Vorbedingungen & Gates (NICHT überspringen)
----------------------------------------------------------------
1. Gate A1: L1 Exit & Review abgeschlossen; Entscheidung „L1 FREIGEGEBEN“ dokumentiert.
2. Gate A2: Beobachtungsfenster ≥ 48h stabiler L1-Betrieb ohne ungeklärte Alarme.
3. Gate A3: GS FINAL Strategien READ-ONLY (keine Änderungen an Pfad/Format/Inhalt).
4. Gate A4: L2-Mandat, Startbedingungen/Guards, Minimal-Architektur, Decision-Matrix FINAL.
5. Gate A5: Keine parallelen Änderungen an L1 (Code oder Config) während L2-Arbeit.

----------------------------------------------------------------
B. Repo-Struktur & Isolation
----------------------------------------------------------------
6. L2-namespace festlegen (eigener Ordner/Namespace).
7. Isolation: L2 schreibt nirgendwo in L1-Pfade; L2 liest L1 ausschließlich read-only.
8. Artefakte trennen:
   - Inputs: GS FINAL Strategien, Markt-Snapshot/Fenster, Regime-Labels, L1-Health/States.
   - Outputs: L2-Decision-Records (append-only).
9. Konfiguration: L2-Config strikt getrennt von L1 (keine ENV-Kollisionen).

----------------------------------------------------------------
C. Datenverträge (Inputs)
----------------------------------------------------------------
10. Strategie-Contract:
    - Eindeutige Strategie-ID und Hash zur Integritätsprüfung.
    - Quelle ausschließlich GS FINAL (LONG/SHORT).
11. Markt-Contract:
    - Minimale Felder (UTC-Zeit, Preis, Fenster-ID).
    - Identisches Zeitverständnis wie L1 (keine Transformation).
12. Regime-Contract:
    - Quelle, gültige Labels, zeitliche Gültigkeit, Snapshot-Synchronität.
13. L1-State/Health-Contract:
    - Read-only: Alarm-Flag und ausgewählte States (z. B. Risk-Status).
14. Zeitbasis:
    - Einheitlich UTC, monoton, für alle Inputs/Outputs.

----------------------------------------------------------------
D. Schnittstellen (nicht-invasiv)
----------------------------------------------------------------
15. I-Read (L1→L2): L2 darf L1 nur lesen (Logs/States/Alarm-Flag).
16. I-Write (L2→L1): Keine Writes; optional eigene Decision-Outputs (ignorierbar durch L1).
17. Operator-Control: L2 start/stop unabhängig von L1; Deaktivierung = Outputs ignorieren.

----------------------------------------------------------------
E. Entscheidungslogik (Decision-Matrix)
----------------------------------------------------------------
18. Dimensionen:
    D1 Regime-Konsistenz
    D2 Marktkontext-Konsistenz
    D3 Betriebsstabilität (L1-Health)
    D4 Strategische Integrität (GS unverändert)
19. Binäre Regel:
    ALLOW nur wenn D1–D4 erfüllt sind; sonst BLOCK.
20. Default-Sicherheit:
    Bei Unsicherheit immer BLOCK (fail-closed).
21. Begründungspflicht:
    Jede BLOCK-Entscheidung enthält Dimension(en) und Reason-Codes.

----------------------------------------------------------------
F. Guards & Abbruchregeln
----------------------------------------------------------------
22. Guard F1: L1-Alarm erscheint → L2 sofort deaktivieren (Outputs ignorieren).
23. Guard F2: Fehlende/inkonsistente Inputs → BLOCK.
24. Guard F3: Nicht reproduzierbare Outputs → STOP L2 (kein Fix im Betrieb).
25. Guard F4: Scope-Verletzung (neue Heuristiken/Signale) → STOP, zurück ins Design.

----------------------------------------------------------------
G. Logging & Audit
----------------------------------------------------------------
26. Append-only Audit-Record (Pflichtfelder):
    - timestamp_utc
    - decision (ALLOW/BLOCK)
    - strategy_id, strategy_hash
    - dimension_results (D1–D4 + reason codes)
    - input_refs (snapshot/regime/l1_state ids)
    - l2_version (commit hash)
27. Determinismus:
    Alle Reproduktionsreferenzen im Record enthalten.
28. ASCII-only:
    Konsistent mit bestehender Toolchain.

----------------------------------------------------------------
H. Testplan (vor Aktivierung)
----------------------------------------------------------------
29. T0 Offline-Replay: Wiederholungen liefern identische Entscheidungen.
30. T1 GS-Integrität: Strategie-Hashes unverändert vor/nach L2-Läufen.
31. T2 L1-Unberührtheit: L1 läuft unverändert weiter (keine Side-Effects).
32. T3 Alarm-Pfad: Simulierter Alarm → L2 deaktiviert sich.
33. T4 Missing-Inputs: Fehlende Inputs → BLOCK mit korrekter Begründung.

----------------------------------------------------------------
I. Rollout (ein Commit)
----------------------------------------------------------------
34. Modus I1 Dry-Run: L2 loggt Entscheidungen; keine Kopplung.
35. Modus I2 Optionaler Konsum: L1 kann Decision lesen, bleibt autonom.
36. Dokumentation: Mandat/Architektur/Matrix unverändert; nur Implementationsdetails ergänzen.

----------------------------------------------------------------
J. Stop-Kriterien
----------------------------------------------------------------
37. S1 Unerklärliches Verhalten.
38. S2 Unvollständige Observability.
39. S3 Scope-Verletzung.
→ STOP, Ursachen dokumentieren, keine Live-Fixes.

----------------------------------------------------------------
K. Abschluss
----------------------------------------------------------------
40. Single-Commit-Regel: Alle L2-Änderungen in einem sauberen Commit.
41. Tagging: Commit eindeutig als „L2-Implementierung (Initial)“.
42. Review: Checkliste vollständig abgehakt, dann erst Aktivierung erwägen.

ENDE
