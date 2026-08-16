# X1 State-Research S34 STEP20D-Sensitivity-Entrypoint-Einkapselung

Datum: 2026-08-16

Status: PASS / PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE

Basis-Commit: `7227afe3995a7cdaf39447accd5c550304d91ca6`

Branch: `codex/x1-state-research-s34-step20d-sensitivity-entrypoint-encapsulation-2026-08-16`

Ziel: `scripts/state_research/analyze_step20D_sensitivity.py`

## Zweck und Grenzen

S34 beseitigt ausschließlich die Ausführung beim Import. Der in S33 charakterisierte Top-Level-Laufzeitbody wurde vollständig und unverändert in ein parameterloses `main() -> None` verschoben und mit `if __name__ == "__main__": main()` abgeschirmt.

Die bestehende `get_multiplier(risks, m030, m050, m070)`-Definition lag innerhalb der früheren Laufzeitsequenz nach den CSV-Reads und UTC-Konvertierungen. Sie wurde deshalb als lokaler Bestandteil AST-identisch mit in `main()` verschoben. `START_CAPITAL` und das feste D1-D3-`configs`-Raster bleiben unveränderte Modulkonstanten.

Es wurden keine Inputs, Zeitkonvertierungen, Trade-/Side-Matches, Fenster, Streaks, Schwellen, Multiplikatoren, PnL-Berechnungen, Statistiken, Rundungen, Stdout-Zeilen oder Fehlerbehandlungen verändert. Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

STEP20D v1 bleibt ein methodisch optimistischer Proof of Concept. Der finale Multiplikator wird rückwirkend auf das vollständige Trade-PnL angewendet; die technische Einkapselung macht diesen Ansatz weder live-akkurat noch produktionsgeeignet.

## Quell- und Laufzeitidentität

- S33-Baseline-SHA-256: `49f37fe4d47e3205e4f6b1eb57cc67330fe2a81258f18d832aa3b849268e7636`
- S34-SHA-256: `cb7436bb731e8cf868473d9224a7ce1246b25986600bf45a4086de33699500f8`
- Umfang S33 → S34: 97 → 103 Zeilen
- S33-Top-Level-Laufzeitbody und S34-`main()`-Body AST-identisch: PASS
- Laufzeit-AST-SHA-256: `e251282b73fa308f9bfe80fb71d4422e66850a39da60db43a201f1338810a59a`

Der AST-Fingerprint bindet die vollständige frühere Laufzeitsequenz ab dem ersten Trades-Read einschließlich aller fünf UTC-Konvertierungen, der lokalen `get_multiplier`-Definition, Headerausgabe, D1-D3-Schleife, Trade-Schleife, Merge-/Streak-Semantik, Kennzahlen und Ergebniszeilen. Die sechs zusätzlichen Quellzeilen entstehen ausschließlich durch Funktionskopf, Einrückungsstruktur, Main-Guard und notwendige Leerzeilen.

## Neuer Entrypoint-Vertrag

Das Modul definiert auf Modulebene genau einen parameterlosen Einstiegspunkt:

```text
main() -> None
```

Der Main-Guard ruft `main()` ohne Argumente auf. Der direkte historische Offline-Aufruf bleibt unverändert:

```text
python scripts/state_research/analyze_step20D_sensitivity.py
```

`get_multiplier` wird erst innerhalb eines `main()`-Laufs definiert und ist nach einem reinen Import nicht als ungebundener Replay-Zwischenzustand exponiert.

## Neuer Import-Sicherheitsvertrag

Ein Import beziehungsweise `runpy.run_path` mit einem Namen ungleich `__main__` erzeugt:

- null CSV-Lesezugriffe,
- null UTC-Konvertierungen,
- null Trade-/Snapshot-Matches,
- null Streak- oder Multiplikatorberechnungen,
- null Stdout,
- null Stderr,
- null Dateien,
- null Verzeichnisse.

Der Einstiegspunkt `main` ist anschließend explizit aufrufbar. Die lokale Hilfsfunktion `get_multiplier` ist vor einem solchen Aufruf nicht im Modul-Namespace vorhanden.

## Vollständig erhaltener S33-Vertrag

Alle zehn S33-Verträge bleiben im direkten Lauf erhalten:

1. Quellkonstanten `START_CAPITAL = 10000.0` und das feste D1-D3-Raster sowie genau eine Streak-Hilfsfunktion innerhalb der Laufzeitsequenz.
2. feste Read-Reihenfolge Trades, Lifecycle, Shadow und feste fünfteilige UTC-Konvertierungsreihenfolge mit `utc=True`.
3. strikt exklusive Schwellen `>0.30`, `>0.50`, `>0.70`, drei konsekutive Treffer und monotoner `min`-Multiplikator.
4. exaktes Entry-/case-insensitives Side-Matching, inklusives Shadow-Fenster, Default `1.0` und `merge_asof(nearest, tolerance=2min)` mit `fillna(0.0)`.
5. rückwirkendes Scaled PnL, festes Row-Schema, Equity, Peak, Max Drawdown, Gewinner-/Verliererfilter und Profit Factor.
6. identischer Stdout-Header, Formatpräzision, D1-D3- sowie Multiplikatorzähler-Reihenfolge und weiterhin kein Writer.
7. identischer synthetischer Erfolgs-Stdout und vollständige Input-/Dateisystem-Nichtmutation.
8. identische `FileNotFoundError`-Pfade für alle drei fehlenden Inputs in fester Read-Reihenfolge vor Stdout.
9. identischer Empty-Trades-`KeyError` nach alleiniger Headerausgabe und ohne Mutation.
10. identischer `DateParseError` für den ersten ungültigen Trade-Entry-Zeitstempel vor Stdout und ohne Mutation.

Die gebundenen synthetischen Ergebniszeilen bleiben:

```text
D1,14.00,1.3500,0.0036,1,1,1,0,1
D2,25.00,1.4167,0.0050,0,1,1,1,1
D3,50.00,1.8333,0.0050,0,1,1,0,2
```

## Aktualisiertes Charakterisierungsgate

`tests/state_research/test_step20d_sensitivity_characterization.py` umfasst nun elf Prüfungen. Die zehn S33-Prüfungen wurden an den `main()`-Body und die lokale `get_multiplier`-Definition angepasst und vollständig erhalten. Hinzugekommen ist:

11. stiller, nichtmutierender Import ohne Reads, Konvertierungen, Berechnungen, Stdout, Stderr, Dateien oder Verzeichnisse.

Zusätzlich bindet das Strukturgate:

- genau ein parameterloses `main() -> None` auf Modulebene,
- genau einen Main-Guard mit parameterlosem `main()`-Aufruf,
- keine Top-Level-Reads oder Top-Level-Ausführungscalls,
- genau eine lokale `get_multiplier`-Definition,
- AST-Identität des vollständigen S33-Laufzeitbodys mit dem neuen `main()`-Body.

Gate-Test-SHA-256: `4ff0f80d39576c59e51e9a5a29697038bb0d36fbe85cdb1897cd4f5e8c32e216`

## Verifikation

Test-Runtime: Python 3.14.4 mit der ausschließlich aus dem lokalen Pip-Cache unter `/tmp` bereitgestellten NumPy-2.3.5-/Pandas-3.0.1-Schicht.

- Fokussiertes S34-Gate: 11/11 PASS
- Gesamte State-Research-Testkohorte: 163/163 PASS
- Bestehende Regression-Suite: 170/170 PASS
- Laufzeit-AST-Identität S33 → S34: PASS
- `git diff --check`: PASS
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

`analyze_step20D_sensitivity.py` ist import-sicher, ohne seinen charakterisierten historischen Offline-Direktlauf zu verändern. Das feste Raster, Streaks, Matches, rückwirkendes PnL, Kennzahlen, Stdout und bestehende Fehlerpfade bleiben vollständig gebunden. Der fachliche Status bleibt `PROOF OF CONCEPT ONLY / NOT LIVE ACCURATE`; Live-L1, Exchange und Live bleiben gesperrt.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S35-STEP19B-THRESHOLD-SWEEP-CHARAKTERISIERUNGSGATE** für `scripts/state_research/analyze_step19B_threshold_sweep.py`. Zunächst werden Inputs, Schwellenraster, Block-/PnL-Semantik, Kennzahlen, Writer/Stdout, Nichtmutation und Fehlerpfade ausschließlich statisch und mit synthetischen temporären CSVs gebunden; erst danach darf eine Entrypoint-Einkapselung erwogen werden.
