# X1 State-Research S15A STEP18-Stdout-Pfadseparator-Normalisierung

Datum: 2026-08-15

Status: PASS

Basis-Commit: `c4fa5d6dc6a70961d09dc4bedd9c278011075de6`

Branch: `codex/x1-state-research-s15-step19-threshold-fine-characterization-2026-08-15`

Ziel: `tests/state_research/test_step18_writer_chain_characterization.py`

## Anlass und Autorisierung

Die S15-Gesamtkohorte zeigte unter dem verpflichtenden WSL-nativen Lauf einen einzelnen bestehenden Fehler. Die zwei erwarteten STEP18-Stdout-Fingerprints kodierten Windows-Backslashes, während `pathlib.Path` unter WSL POSIX-Slashes ausgibt. Alle neun im selben Test geprüften CSV-Fingerprints stimmten bereits exakt.

S15A wurde am 2026-08-15 ausdrücklich freigegeben. Die Freigabe umfasst ausschließlich eine plattformneutrale Testnormalisierung; Änderungen an produktiven STEP18-Skripten oder deren tatsächlichem Stdout waren nicht autorisiert.

## Änderung

Der bereits vorhandene Helper `_normalized_slashes()` wird nun auch auf `core_result.stdout` und `cluster_result.stdout` angewendet, unmittelbar bevor deren SHA-256-Fingerprints berechnet werden.

Die kanonischen erwarteten POSIX-Fingerprints lauten:

- Core-Stdout: `a5b8162b0f5180547232b5dc612409356ab210ad3953e53a64a7dbb8dd6f0c14`
- Cluster-Stdout: `1572efed45b7ad613311ddffe40d1d41dd3f53e72f97664c6c69ffa2e73343fb`

Die Normalisierung ersetzt ausschließlich `\\` durch `/`. Inhalt, Zeilenfolge, Zeilenanzahl, Dateinamen und sonstige Zeichen bleiben Teil des Fingerprints.

## Unveränderte Grenzen

- `scripts/state_research/build_step18_core_pipeline.py` blieb unverändert, SHA-256 `57a819ed2fb04f075e059b5dc60cf4fba3b2c284b4b27e0120f30e01512fcf98`.
- `scripts/state_research/analyze_step18_clusters.py` blieb unverändert, SHA-256 `65918c7346b1819862dc17db2124768f0de6c8ca45daa93b0a846a4cbc80c5a3`.
- Sämtliche neun CSV-Fingerprints blieben unverändert.
- Keine realen Research-Inputs wurden gelesen oder verändert.
- `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet.
- IU4 ENFORCED, Live-L1, Exchange und Live blieben gesperrt.

Test-SHA-256 nach S15A: `b690716a1365b7be2aace2dda4b6d6f05f227f48f699c1d0329475480701ebd4`.

## Verifikation

Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Fokussiertes STEP18-Writer-Chain-Gate: 11/11 PASS
- Fokussiertes S15-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 68/68 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS

## Ergebnis

Der STEP18-Stdout-Vertrag wird nun auf Windows und WSL semantisch identisch geprüft, ohne produktiven Code oder tatsächliche Ausgabe zu verändern. Der S15-Kohortenblocker ist beseitigt.

## Exakter nächster Schritt

S15 und S15A gemeinsam stagen und committen. Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S16-STEP19-THRESHOLD-FINE-ENTRYPOINT-EINKAPSELUNG**.
