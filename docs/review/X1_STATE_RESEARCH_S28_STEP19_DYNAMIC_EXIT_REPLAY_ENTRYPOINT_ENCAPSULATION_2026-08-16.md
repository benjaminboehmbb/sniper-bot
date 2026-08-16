# X1 State-Research S28 STEP19-Dynamic-Exit-Replay-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS

Basis-Commit: `a69d051032646b87a073b65752613ed14795001e`

Branch: `codex/x1-state-research-s28-step19-dynamic-exit-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step19_dynamic_exit_replay.py`

## Zweck und Grenzen

S28 beseitigt ausschließlich die Ausführung beim Import. Der in S27 charakterisierte Top-Level-Ablauf wurde unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Es wurden keine Inputs, Konfigurationen, Schwellen, Streak-Regeln, Zeitfenster, PnL-Annahmen, Kennzahlen, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Quell- und Laufzeitidentität

- S27-Baseline-SHA-256: `f13c4366b15cc59ce7db9329d269a17aa9aa9d09a04e343e7f35de0f029a3bb9`
- S28-SHA-256: `c7b95427b3b7e3ca52b840011cb30949d8ca17f64f48b9417a7c325e3a1a7fa1`
- Umfang S27 → S28: 76 → 82 Zeilen
- S27-Top-Level-Laufzeitbody und S28-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `729083ca5488e5710533e1497950e4de493c6145ba7cfb4aabb3253ef7560a50`

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Der AST-Fingerprint bindet den vollständigen verschobenen Laufzeitbody einschließlich Reads, Konfigurationsraster, Triggerberechnung, Replay-PnL, Kennzahlen und Stdout.

## Neuer Entrypoint-Vertrag

Das Modul definiert genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step19_dynamic_exit_replay.py
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null Pandas-Replay-Berechnung,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar. Ein Import startet keinen Research-Lauf.

## Vollständig erhaltener S27-Vertrag

Alle neun S27-Verträge bleiben im direkten Lauf erhalten:

1. feste Read-Reihenfolge Trades-Auto-CSV, danach Passive-Shadow-CSV,
2. feste UTC-Konvertierungsreihenfolge Entry, Exit, Shadow,
3. vier Konfigurationen in der Reihenfolge `(0.50,3)`, `(0.50,5)`, `(0.60,3)`, `(0.60,5)`,
4. inklusive Lebenszeitfenster und Missing-Window-Skip,
5. keine Sortierung; Streak-Berechnung in bestehender Snapshot-Reihenfolge,
6. strikt `shadow_risk_score > threshold` und Streak-Reset bei Wahrheitswertwechsel,
7. konservatives `replay_pnl = 0.0` bei Trigger,
8. identische Kennzahlen, Formatierung und Erfolgs-Stdout,
9. identische Missing-Input- und No-Matched-Windows-Fehlerpfade.

Der Erfolgs-Stdout-SHA-256 bleibt `a8c1b354dc05d20484944afda1a9fe50641e82bb63acd478669987d58b9cfcc2`.

Es gibt weiterhin keine Writer, keine Pfadparametrisierung, keine Sortierung und keine Reparatur des leeren-DataFrame-Fehlers. S28 autorisiert oder verändert keine wissenschaftliche Exit-Regel.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step19_dynamic_exit_replay_characterization.py` umfasst nun zehn Prüfungen. Die neun S27-Prüfungen wurden an den `main()`-Body angepasst und unverändert erhalten. Hinzugekommen ist:

10. stiller, nichtmutierender Import ohne Reads, Berechnung, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None`,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S27-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `ba11119dcb49c501e1852302835d6b3d0caa5c6ced33fb03a7f1cf41c3e21900`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S28-Gate: 10/10 PASS
- Gesamte State-Research-Testkohorte: 129/129 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S27 → S28: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step19_dynamic_exit_replay.py` ist import-sicher, ohne seinen charakterisierten Direktlauf zu verändern. Trigger, Replay-PnL, Kennzahlen, Erfolgs-Stdout und bestehende Fehlerpfade bleiben vollständig gebunden.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S29-STEP20C-LIVE-REPLAY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step20C_live_replay.py`. Es ist mit 94 Zeilen gemeinsam der kleinste verbleibende historische STEP19B- bis STEP20E-Import-Zeit-Ausführer und steht im bestehenden Provenienz-Inventar vor dem gleich langen STEP20-Position-Sizing-Replay. Zunächst werden Inputs, Zeitfenster, Exposure-/PnL-Semantik, Kennzahlen, Output-CSV, Nichtmutation und Fehlerpfade ausschließlich synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
