# RCC-002 S7 Implementation Record

## 1. Ergebnis

Die kanonische RCC-002-S7-Stufe für Forward Returns und Labeling wurde gemäß
dem Implementation Readiness Review vom 30. Juli 2026 implementiert.

Status:

```text
IMPLEMENTED – INDEPENDENTLY APPROVED – CERTIFICATION PREPARED
```

## 2. Implementierte Dateien

Produktionscode:

- `rcc002/s7/__init__.py`
- `rcc002/s7/constants.py`
- `rcc002/s7/formulas.py`
- `rcc002/s7/reason_codes.py`
- `rcc002/s7/schema.py`
- `rcc002/s7/compute.py`
- `rcc002/s7/leakage.py`
- `rcc002/s7/planning.py`

Tests:

- `tests/rcc002/s7/__init__.py`
- `tests/rcc002/s7/_helpers.py`
- `tests/rcc002/s7/test_formulas.py`
- `tests/rcc002/s7/test_reason_codes.py`
- `tests/rcc002/s7/test_schema.py`
- `tests/rcc002/s7/test_compute.py`
- `tests/rcc002/s7/test_golden_fixtures.py`
- `tests/rcc002/s7/test_planning.py`

## 3. Implementierter Umfang

- sechs registrierte Horizonte von 1 bis 1.440 Minuten;
- Close-to-Close- und Next-Open-to-Close-Returns;
- Long-/Short-Log-Returns;
- lineare Fee-Net-Proxys;
- Long-/Short-MFE und -MAE samt ersten Extrem-Offsets;
- Brutto- und Net-Proxy-Direction-Labels ohne Deadband;
- Long-/Short-Barrier-Labels mit Open-Gap-Priorität,
  `AMBIGUOUS_BOTH_HIT` und `TIMEOUT`;
- exakte familienbezogene Validität, Nullsemantik und Reason Codes;
- Tail-, Segment-, Qualitäts-, Synthetic-, Entry-, Exit- und
  Nichtendlichkeitsbehandlung;
- vollständige 302-Feld-S7-Registry und deterministische Expansion;
- S6→S7-Zeilen- und Feldwerterhaltung;
- Trennung der veränderbaren `indicators`- und `signals`-Container;
- bis zu 1.440 Zeilen Forward-Overlap ohne Doppelausgabe;
- inkrementelle Invalidierungsgrenze;
- chronologischer Split-Purge-Test;
- S7-Eigentums- und Leakage-Schutz.

## 4. Verifikation im Implementierungsworkspace

Ausgeführt:

```text
python -m compileall -q rcc002 tests/rcc002
python -m unittest discover -s tests/rcc002/s7 -t .
python -m unittest discover -s tests/rcc002 -t .
```

Ergebnis:

```text
S7:       49 tests – OK
RCC-002: 573 tests – OK
compileall: PASS
```

Die im Zielrepository vorhandenen Regressionstests sind nicht Teil des
hochgeladenen Implementierungseingangspakets. Sie müssen nach Installation
im Zielrepository erneut ausgeführt werden. Der Installationsbefehl führt
dies ausdrücklich aus.

Verifikation nach Installation im Zielrepository:

```text
S7:         49 tests – OK
RCC-002:   573 tests – OK
Regression: 170 tests – OK
compileall: PASS
git diff --check: PASS
```

Performance-Verifikation nach Auflösung von `S7-CLAUDE-002`:

```text
1,500 rows:   0.508 s – 2,954 rows/s
3,500 rows:   1.298 s – 2,696 rows/s
6,000 rows:   2.280 s – 2,632 rows/s
20,000 rows:  7.425 s – 2,694 rows/s
```

Die Messung umfasst `compute_labels()` einschließlich S7-Objektkonstruktion,
nicht jedoch vorgelagerte S6-Erzeugung oder physische Dataset-
Serialisierung. Der Algorithmus verwendet nun horizonweise monotone Deques
für MFE/MAE, Prefix-Indizes für Fenstervalidität und einen Range-Index für
die erste Barrier-Trefferkerze.

## 5. Wesentliche geprüfte Eigenschaften

- exaktes `t+h` für jeden registrierten Horizont;
- bitgenaue lineare Long-/Short-Symmetrie;
- keine implizite neutrale Toleranz;
- erste Bar bei wiederholten Extrema;
- Barrier-TP, Barrier-SL, Open-Gap, Ambiguität und Timeout;
- exakte Treffer auf den Barrieren;
- unvollständiger Tail bleibt als ungültige Originalzeile erhalten;
- Segmentwechsel und fehlende Minuten werden nicht überbrückt;
- Synthetic- und Quality-Failures erzeugen keine gültigen numerischen Werte;
- Qualitäts-, Entry- und Exit-Invalidität bleiben familienlokal;
- serielle und partitionierte Ausführung stimmen exakt überein;
- Änderungen nach `t+h` verändern das Label nicht;
- sämtliche 302 S7-Felder werden aus nicht labelberechtigten Views
  fail-closed ausgeschlossen;
- die S6-Eingangsobjekte werden weder in Werten noch über mutable
  Containerreferenzen verändert.

## 6. Identitäten

```text
label_schema_fingerprint_sha256=
075ef38aac0a5de31eefdee6881139e2f8188e8b1722f7c577e9aaa83cad643a

semantic_build_configuration_sha256=
dcad27744de8fff0f29400d7f825ba89b6a9610f1f690449cdf6575c95bfb7b1
```

## 7. Unabhängige Reviewhistorie

Der erste unabhängige Claude-Review endete mit:

```text
REJECTED – 0 CRITICAL, 2 MAJOR, 1 MINOR, 0 EDITORIAL
```

Alle drei Findings wurden korrigiert. Der vollständige Corrected Re-Review
endete anschließend mit:

```text
APPROVED – 0 CRITICAL, 0 MAJOR, 1 MINOR, 1 EDITORIAL
```

Alle ursprünglichen Findings sind `RESOLVED`. Der neue MINOR-Hinweis zum
unveränderten `COMPONENT_VERSION` wird wegen des aktualisierten
`semantic_build_configuration_sha256` und der vollständigen Paket- und
Source-Identität als nicht blockierende Traceability-Limitation akzeptiert.
Der EDITORIAL-Hinweis zum teilweise geteilten Testhelper ist durch Claudes
vollständig unabhängiges 714-Fälle-Orakel extern abgedeckt.

Gemini im Browser konnte weder das korrigierte ZIP noch das eigens erzeugte
lesbare Source-Review-Bundle verarbeiten und antwortete
`CANNOT_REVIEW_SOURCE_NOT_ACCESSIBLE`. Dieser Vorgang wird als
Tool-/Source-Access-Ausfall dokumentiert und nicht als fachlicher Review
gewertet.

## 8. Verbleibende Schritte

1. finales Zertifizierungspaket installieren und vollständig verifizieren;
2. ausschließlich die zertifizierten S7-Dateien und Reviewartefakte stagen;
3. Commit und Push;
4. BTCUSDT-1m-Vollbuild, Stage-Bericht, Manifest und Reconciliation als
   separaten Dataset-/Produktionsnachweis durchführen.

Die vorhandene unversionierte Datei
`scripts/build_rcc002_spec_bundle.py` gehört ausdrücklich nicht zu diesem
S7-Implementierungsscope und darf nicht versehentlich gestaged werden.
