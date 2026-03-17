# L2_IMPLEMENTATION_ENV_CHECKLIST

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: FINAL – Environment & Operative Readiness (codefrei)
Datum: 2026-01-11

Zweck:
Diese Checkliste stellt sicher, dass am L2-Implementierungstag
keine Zeit durch Kontextfehler, falsche Pfade oder Environment-Mix verloren geht.
Sie verhindert unbeabsichtigte Eingriffe in L1 und schützt GS READ-ONLY.
Keine Implementierung, kein Code.

================================================================
0. Harte Gates (vor jeglicher L2-Implementierung)
================================================================

0.1 L1 formal freigegeben?
- [ ] L1 Exit & Review durchgeführt
- [ ] Entscheidung „L1 FREIGEGEBEN“ dokumentiert

0.2 L1 Freeze aktiv?
- [ ] Keine Änderungen an L1 Code
- [ ] Keine Änderungen an L1 Config
- [ ] Keine Änderungen an L1 Pfaden

0.3 GS Freeze aktiv?
- [ ] GS FINAL bleibt READ-ONLY
- [ ] Keine Änderungen an Strategie-Dateien oder Verzeichnissen

Stop-Kriterium:
Wenn irgendein Punkt in 0.x nicht erfüllt ist → keine L2-Arbeit.

================================================================
1. Arbeitsumgebung (Environment) – verbindlich
================================================================

1.1 Gerät / Host
- Gerät: ______________________ (G15 / Workstation)
- Hostname: ____________________
- Datum/Uhrzeit Start: ____________________

1.2 Environment
- [ ] WSL (für Runs/Analyse/Implementierung)
- [ ] Git Bash NUR für Git-Operationen (add/commit/push)

Hinweis:
Kein Wechsel des Environments während laufender Prozesse.

1.3 Python / venv
- venv aktiv: [ ] ja [ ] nein
- Python-Version: ____________________
- requirements vorhanden: [ ] ja [ ] nein

================================================================
2. Repo-Status (vor Änderungen)
================================================================

2.1 Repo Root korrekt?
- Working directory: ____________________

2.2 Git-Status sauber?
- [ ] keine uncommitted changes
- [ ] richtige Branch: ____________________
- [ ] aktueller Stand: git pull origin main durchgeführt

Stop-Kriterium:
Wenn Repo nicht sauber oder falscher Branch → zuerst korrigieren.

================================================================
3. Pfad- und Write-Schutz (kritisch)
================================================================

3.1 Verbotene Write-Zonen (L2 darf hier NICHT schreiben)
- live_l1/...
- scripts/run_live_l1_paper.py (unverändert lassen)
- live_state/...
- live_logs/...
- strategies/GS/... (READ-ONLY)
- engine/simtraderGS.py (READ-ONLY)

3.2 Erlaubte Write-Zonen (L2-eigenständig)
- l2_logs/...
- l2_state/...
- ggf. l2/ (Namespace)

Stop-Kriterium:
Wenn unklar ist, ob ein Pfad write-safe ist → STOP.

================================================================
4. Input-Verfügbarkeit (nur lesen)
================================================================

4.1 GS Strategien verfügbar?
- [ ] strategies/GS/LONG_FINAL_CANONICAL/ vorhanden
- [ ] strategies/GS/SHORT_FINAL/ vorhanden

4.2 Markt-/Snapshot-Quelle bekannt?
- Quelle/Modul: ____________________
- Minimalfelder verfügbar: timestamp_utc, price, snapshot_id/window_id
- [ ] ja [ ] nein

4.3 Regime-Quelle bekannt?
- Quelle/Datei/Modul: ____________________
- Minimalfelder verfügbar: timestamp_utc, regime_label
- [ ] ja [ ] nein

4.4 L1 Health/State read-only verfügbar?
- [ ] live_l1_alert.flag (Pfad bekannt)
- [ ] live_state Dateien (S2/S4) (Pfad bekannt)

Stop-Kriterium:
Wenn irgendein Input nicht eindeutig referenzierbar ist → STOP.

================================================================
5. Output-Verträge (vorher fest)
================================================================

5.1 Audit-Log (append-only)
- Zielpfad: l2_logs/decision_audit.jsonl
- Eigenschaften:
  - [ ] append-only
  - [ ] keine Überschreibung
  - [ ] vollständig reproduzierbar

5.2 Optional: latest decision pointer
- Zielpfad: l2_state/latest_decision.json
- Eigenschaften:
  - [ ] überschreibbar
  - [ ] kein Audit-Ersatz

Stop-Kriterium:
Wenn Audit-Schema nicht vollständig fixiert ist → STOP.

================================================================
6. Fail-Closed / Abbruchregeln (operativ)
================================================================

6.1 Alarm-Regel
- Wenn live_l1_alert.flag erscheint:
  - [ ] L2 sofort deaktivieren
  - [ ] keine weiteren L2-Schritte
  - [ ] Ursache nur dokumentieren

6.2 Reproduzierbarkeit
- Gleiche Inputs müssen gleiche Outputs liefern.
- Abweichung:
  - [ ] STOP
  - [ ] keine Heuristik-/Fix-Workarounds

6.3 Scope-Schutz
- Keine neuen Signale
- Keine neuen Heuristiken
- Keine Performance-Ziele

================================================================
7. Pre-Commit Check (kurz, zwingend)
================================================================

- [ ] Alle neuen Dateien liegen ausschließlich im L2-Namespace
- [ ] Kein Diff in L1-Dateien
- [ ] Kein Diff in GS-Dateien
- [ ] Audit-Log Schema vollständig implementierbar
- [ ] Commit-Plan (L2_IMPLEMENTATION_COMMIT_PLAN.md) wird eingehalten

Stop-Kriterium:
Wenn irgendein Punkt nicht erfüllt ist → nicht committen.

================================================================
8. Commit & Abschluss
================================================================

- [ ] git add . (nur L2-Dateien)
- [ ] git commit -m "L2 implementation (initial)"
- [ ] git push origin main

Nach Commit:
- [ ] keine sofortige Aktivierung unter Stress
- [ ] kurze Review der Diffs
- [ ] Dokumentation aktualisieren (falls vorgesehen)

ENDE
