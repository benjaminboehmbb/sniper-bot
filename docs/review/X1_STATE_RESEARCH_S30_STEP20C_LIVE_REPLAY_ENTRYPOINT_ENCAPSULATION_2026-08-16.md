# X1 State-Research S30 STEP20C-Live-Replay-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / HISTORISCHES MODELL WEITERHIN NOT VALIDATED

Basis-Commit: `6986f666393e18aa77188ada636ed8c675aaafa3`

Branch: `codex/x1-state-research-s30-step20c-live-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step20C_live_replay.py`

## Zweck und Grenzen

S30 beseitigt ausschließlich die Ausführung beim Import. Der in S29 charakterisierte Top-Level-Ablauf wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. Die bestehende `calc_stats(pnl_col)`-Definition ist Bestandteil des verschobenen Laufzeitbodys und liegt nun lokal in `main()`.

Es wurden keine Inputs, Zeitfilter, Snapshot-Auswahl, Multiplikatoren, PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen, Writer oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

Die historische Bezeichnung „LIVE-COMPATIBLE“ und diese technische Einkapselung ändern den dokumentierten Status `NOT VALIDATED` nicht und stellen keine Live- oder Produktionsfreigabe dar.

## Quell- und Laufzeitidentität

- S29-Baseline-SHA-256: `7c3f1488c565fad9c3cd72f401ce747d63e9ecfe4af982552271a09c0f3e2841`
- S30-SHA-256: `8c344af52182788fb57a3791e17ad5fa690b1000bae2b757b50b6f4ec88d2b40`
- Umfang S29 → S30: 94 → 100 Zeilen
- S29-Top-Level-Laufzeitbody und S30-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `d14480e22d3095bb5c22b7aa3bac1d540a7a20946fdfe8997bc44203cdbba7c2`

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Der AST-Fingerprint bindet den vollständigen verschobenen Body einschließlich der lokalen `calc_stats`-Definition, beider Funktionsaufrufe, sämtlicher Ausgaben und des Writers.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step20C_live_replay.py
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null Snapshot-Zuordnung,
- null Statistikberechnung,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar. `calc_stats` wird erst während eines `main()`-Laufs lokal definiert; ein Import startet oder exponiert keinen Replay-Zwischenzustand.

## Vollständig erhaltener S29-Vertrag

Alle elf S29-Verträge bleiben im direkten Lauf erhalten:

1. feste Read-Reihenfolge Trades-Auto-CSV, danach Passive-Shadow-CSV,
2. feste UTC-Konvertierungsreihenfolge Entry, danach Shadow,
3. entry-inklusive Auswahl `timestamp_utc <= entry_timestamp_utc`,
4. `.tail(1)` auf bestehender CSV-Reihenfolge ohne Timestamp-Sortierung,
5. Missing-Snapshot-Skip und anschließende Sortierung nach `trade_index`,
6. Multiplikatorgrenzen `<=0.30 → 1.00`, `<=0.50 → 0.50`, sonst `0.25`,
7. Scaled PnL als `original_pnl * multiplier`,
8. globale DataFrame-Semantik innerhalb der lokalen `calc_stats`-Closure und identische Kennzahlen,
9. identischer Stdout- und CSV-Erfolgsvertrag,
10. identische Missing-Input- und No-Eligible-Snapshot-Fehlerpfade,
11. identischer Missing-Output-Directory-`OSError` nach Statistiken und vor `written:`.

Der Erfolgs-Stdout-SHA-256 bleibt `f6278aafabf111b4ec3b39ad4f6cd67f6f594258284c8f9af8680f21aa0abad6`.

Die in S29 dokumentierten historischen Spezifikationsabweichungen bleiben unverändert: kein `avg_pnl` und kein `trade_count` im Statistik-Dictionary. `reports/step18` wird weiterhin nicht automatisch erzeugt.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step20c_live_replay_characterization.py` umfasst nun zwölf Prüfungen. Die elf S29-Prüfungen wurden an den `main()`-Body und die lokale `calc_stats`-Definition angepasst und unverändert erhalten. Hinzugekommen ist:

12. stiller, nichtmutierender Import ohne Reads, Berechnung, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S29-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `ce79fbc079461dfe80101c36453df6921d357b3cedf01a427fcfb913df6c2174`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S30-Gate: 12/12 PASS
- Gesamte State-Research-Testkohorte: 141/141 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S29 → S30: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step20C_live_replay.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Snapshot-Auswahl, Multiplikatoren, Statistiken, CSV, Stdout und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `NOT VALIDATED`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S31-STEP20-POSITION-SIZING-REPLAY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step20_position_sizing_replay.py`. Es ist mit 94 Zeilen der kleinste verbleibende historische STEP19B- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden Inputs, Trade-Lifetime-Risiko, Multiplikator-/PnL-Semantik, Kennzahlen, Output-CSV, Nichtmutation und Fehlerpfade ausschließlich synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
