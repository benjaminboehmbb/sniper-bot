# X1 State-Research S32 STEP20-Position-Sizing-Replay-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / VALIDATED RESEARCH RESULT / NOT LIVE COMPATIBLE

Basis-Commit: `87d6af016d71fb577a406a1e10c26280c028a643`

Branch: `codex/x1-state-research-s32-step20-position-sizing-replay-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step20_position_sizing_replay.py`

## Zweck und Grenzen

S32 beseitigt ausschließlich die Ausführung beim Import. Der in S31 charakterisierte Top-Level-Ablauf wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt. Die bestehende `stats(pnl_col)`-Definition ist Bestandteil des verschobenen Laufzeitbodys und liegt nun lokal in `main()`.

Es wurden keine Inputs, Trade-Lifetime-Fenster, Mean-Risk-Berechnungen, Multiplikatoren, PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen, Writer oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP20A bleibt ein `VALIDATED RESEARCH RESULT`, verwendet aber Future-Information und bleibt `NOT LIVE COMPATIBLE`. Die technische Einkapselung ändert diesen fachlichen Status nicht.

## Quell- und Laufzeitidentität

- S31-Baseline-SHA-256: `b185c681497db4c83ea929b5fc8701d3e0d5fd37f097257c18dfafea9655e185`
- S32-SHA-256: `487138d9e7f51ac398160b88c482e6a5230a92d4d3e03ff185b8bdb6d4e55a08`
- Umfang S31 → S32: 94 → 100 Zeilen
- S31-Top-Level-Laufzeitbody und S32-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `59e60750a2498d7676e78409e5bc8901396698baca0232790c805c9101517baf`

Die sechs zusätzlichen Zeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen. Der AST-Fingerprint bindet den vollständigen verschobenen Body einschließlich der lokalen `stats`-Definition, beider Statistikaufrufe, sämtlicher Ausgaben und des Writers.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step20_position_sizing_replay.py
```

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null Trade-Lifetime-Aggregation,
- null Statistikberechnung,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar. `stats` wird erst während eines `main()`-Laufs lokal definiert; ein Import startet oder exponiert keinen Replay-Zwischenzustand.

## Vollständig erhaltener S31-Vertrag

Alle zehn S31-Verträge bleiben im direkten Lauf erhalten:

1. feste Read-Reihenfolge Trades-Auto-CSV, danach Passive-Shadow-CSV,
2. feste UTC-Konvertierungsreihenfolge Entry, Exit, Shadow,
3. an Entry und Exit inklusives Trade-Lifetime-Fenster,
4. Mean Shadow Risk über das vollständige Fenster und Missing-Window-Skip,
5. anschließende Sortierung nach `trade_index`,
6. Multiplikatorgrenzen `<=0.30 → 1.00`, `<=0.50 → 0.50`, sonst `0.25`,
7. Scaled PnL als `original_pnl * multiplier`,
8. globale DataFrame-Semantik innerhalb der lokalen `stats`-Closure und identische Float-Kennzahlen,
9. identischer Stdout- und CSV-Erfolgsvertrag,
10. identische Missing-Input-, No-Matched-Window- und Missing-Output-Directory-Fehlerpfade.

Der Erfolgs-Stdout-SHA-256 bleibt `fa6029394588f7cd1384cea648b661a1c60b191ff0f55576f4fcfbd0c11dbe01`.

`reports/step18` wird weiterhin nicht automatisch erzeugt. Die native Float-Grenzsemantik bleibt unverändert; es wurde weder gerundet noch eine Toleranz eingeführt.

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step20_position_sizing_replay_characterization.py` umfasst nun elf Prüfungen. Die zehn S31-Prüfungen wurden an den `main()`-Body und die lokale `stats`-Definition angepasst und unverändert erhalten. Hinzugekommen ist:

11. stiller, nichtmutierender Import ohne Reads, Aggregation, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- AST-Identität des vollständigen S31-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `6d2cd35efaa6ee856b8dc9f1c19124c019b0cf65020bdb893701d6b2927d6379`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S32-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 152/152 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S31 → S32: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step20_position_sizing_replay.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Trade-Lifetime-Risiko, Multiplikatoren, Statistiken, CSV, Stdout und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `NOT LIVE COMPATIBLE`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S33-STEP20D-SENSITIVITY-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step20D_sensitivity.py`. Es ist mit 97 Zeilen der kleinste verbleibende historische STEP19B- bis STEP20E-Import-Zeit-Ausführer. Zunächst werden Inputs, Streak-Zuordnung, Konfigurationsraster, Multiplikator-/PnL-Semantik, Kennzahlen, Stdout, Nichtmutation und Fehlerpfade ausschließlich synthetisch gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
