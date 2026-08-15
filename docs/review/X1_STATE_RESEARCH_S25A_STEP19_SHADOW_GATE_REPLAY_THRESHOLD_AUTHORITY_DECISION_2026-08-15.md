# X1 State-Research S25A STEP19-Shadow-Gate-Replay-Schwellenauthority-Entscheidung

Datum: 2026-08-15

Status: PASS (FACHLICHE ENTSCHEIDUNG) / REPARATUR NOCH NICHT AUTORISIERT

Basis-Commit: `9cd311ad9f58cf1a993af2647be7421433978c83`

Branch: `codex/x1-state-research-s25a-step19-shadow-gate-replay-threshold-authority-decision-2026-08-15`

Ziel: `scripts/state_research/analyze_step19_shadow_gate_replay.py`

## Zweck und Grenzen

S25A entscheidet den in S25 offengelegten fachlichen Konflikt zwischen dem definierten Raster `THRESHOLDS` und dem tatsächlich verwendeten, aber ungebundenen Singularnamen `THRESHOLD`. Die Entscheidung basiert ausschließlich auf Repository-Verträgen und bestehenden Research-Berichten. Das Zielskript wird in S25A nicht verändert und nicht ausgeführt.

Reale Research-Inputs wurden weder gelesen noch verändert. `scripts/build_rcc002_spec_bundle.py` wurde nicht gelesen, verändert, gestaged oder committet. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt. Eine Entrypoint-Einkapselung ist ausdrücklich nicht Bestandteil dieser Stufe.

## Fachliche Evidenz

1. `scripts/state_research/analyze_step19_threshold_sweep.py` besitzt bereits das vollständige Raster `[0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]` und verantwortet die rasterförmige Schwellenanalyse.
2. `analyze_step19_shadow_gate_replay.py` verwendet im ausführbaren Pfad ausschließlich den Singularnamen `THRESHOLD`, druckt einen einzelnen `threshold:`-Wert und besitzt genau zwei feste, nicht schwellenqualifizierte Outputpfade.
3. Ein Rasterlauf im Replay-Skript würde die bestehende Sweep-Zuständigkeit duplizieren und die festen CSVs pro Schwelle überschreiben oder eine neue Outputstruktur erfordern.
4. `scripts/state_research/analyze_step19_blocked_winners.py` verwendet zwar historisch `0.40`, dokumentiert diese Zahl aber nicht als autoritative Replay-Schwelle.
5. `docs/research/STATE_RESEARCH_FINAL_STATUS.md` bewertet das STEP19 Entry Gate wegen Future-Information-Leakage als `REJECTED` und friert die direkte Trading-Integration ein. Die Ergebnisse dürfen nur als Monitoring, Diagnostik und Research weiterverwendet werden.
6. Die Point-in-time-Anforderung aus `docs/POLICIES/backtest_integrity_policy.md` schließt aus, aus dem abgelehnten Leak-behafteten Resultat stillschweigend einen produktiven Default abzuleiten.

## Autoritative Entscheidung

### 1. Vertragsrolle

`analyze_step19_shadow_gate_replay.py` bleibt ein **detaillierter Einzel-Schwellen-Replay für ausschließlich offline ausgeführte Diagnostik**. Das Skript darf das vorhandene Raster nicht selbst iterieren.

Die Rasteranalyse verbleibt bei `analyze_step19_threshold_sweep.py`. Ein späterer dateischreibender Raster-Exporter wäre ein eigenständiges Werkzeug mit eigenem Vertrag und eigener Freigabe, nicht eine Nebenwirkung dieses Replay-Skripts.

### 2. Schwellenauthority

Es gibt **keine autorisierte numerische Defaultschwelle** für den Replay.

- `0.40` wird nicht als Default autorisiert.
- Keine andere Zahl aus dem vorhandenen Raster wird als Default autorisiert.
- Das gesamte Raster wird nicht zum Replay-Vertrag erklärt.
- Ein später reparierter Replay muss die einzelne Schwelle pro Aufruf explizit erhalten und darf keinen stillen Fallback besitzen.

Die explizit übergebene Schwelle ist ein diagnostischer Szenarioparameter, keine wissenschaftlich validierte Trading-Regel. Sie darf keine Live-, Exchange-, Live-L1- oder IU4-Freigabe implizieren.

### 3. Outputbenennung

Für genau einen expliziten Schwellenwert pro Aufruf bleiben die bestehenden Outputnamen autoritativ:

- `reports/step18/step19_shadow_gate_replay_trades.csv`
- `reports/step18/step19_shadow_gate_replay_kept_trades.csv`

Es werden in diesem Skript **keine Raster-Outputs** benannt, weil Rasterausführung nicht zu seinem Vertrag gehört. Falls zukünftig ein separater dateischreibender Raster-Exporter fachlich freigegeben wird, müssen dessen Artefakte den Schwellenwert eindeutig im Dateinamen oder in einem manifestierten partitionssicheren Schema tragen; die beiden Replay-Dateien dürfen nicht pro Rasterpunkt überschrieben werden.

### 4. Reparaturgrenze

S25A autorisiert noch keine Codeänderung. Eine spätere Reparaturspezifikation muss mindestens binden:

- genau einen erforderlichen, expliziten Schwellenparameter pro Aufruf,
- keinen Default und keinen impliziten Zugriff auf `THRESHOLDS`,
- Validierung als endlicher Wert im geschlossenen Intervall `[0.0, 1.0]`,
- unveränderte Einzel-Replay-Semantik und Writer-Reihenfolge,
- ausschließlich synthetische Verifikation,
- fail-closed Verhalten bei fehlender oder ungültiger Schwelle,
- keine Entrypoint-Einkapselung vor abgeschlossener Reparatur und erneutem Charakterisierungsgate.

## Nicht autorisiert

S25A autorisiert nicht:

- eine konkrete Schwelle als wissenschaftlich oder produktiv gültig,
- die Verwendung realer Research-Inputs,
- eine Rasterausführung oder neue Rasterdateien in diesem Skript,
- eine Trading-, IU4-, Live-L1-, Exchange- oder Live-Integration,
- die Reparatur des leeren-Match-Pfads,
- die Erzeugung fehlender Outputverzeichnisse,
- eine Entrypoint-Einkapselung.

## Verifikation

Vollständige Test-Runtime: Python 3.12.13, NumPy 2.3.5, Pandas 3.0.1.

- Bestehendes fokussiertes S25-Gate: 8/8 PASS
- Gesamte State-Research-Testkohorte: 113/113 PASS
- Bestehende Regression-Suite: 170/170 PASS
- `git diff --check`: PASS
- Zielskript verändert: 0 Bytes
- Reale Research-Inputs gelesen oder verändert: 0
- `scripts/build_rcc002_spec_bundle.py` gelesen, verändert, gestaged oder committet: 0

## Ergebnis

Der fachliche Konflikt ist aufgelöst: Der Shadow-Gate-Replay ist ein Einzel-Schwellen-Diagnosewerkzeug, aber das Repository besitzt keine autoritative numerische Schwelle. Deshalb muss die Schwelle später explizit und ohne Default bereitgestellt werden. Das Raster bleibt ausschließlich beim bestehenden Sweep-Werkzeug; die festen Replay-Outputnamen bleiben unverändert.

## Exakter nächster Schritt

Nach der Branch-Integration folgt **X1-STATE-RESEARCH-S25B-STEP19-SHADOW-GATE-REPLAY-REPARATURSPEZIFIKATION**. S25B muss den fail-closed Vertrag für genau einen erforderlichen expliziten Schwellenparameter, dessen Validierung und die synthetische Verifikation spezifizieren, ohne das Zielskript zu ändern. Eine Entrypoint-Einkapselung bleibt bis nach implementierter Reparatur und erneuter Charakterisierung unzulässig.
