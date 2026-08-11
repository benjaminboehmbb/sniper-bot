# LIVE PAPER ECONOMICS — IU-3 SHADOW EVIDENCE V1

- **Prüfdatum:** 2026-08-06
- **Implementierungscommit:** `32acfe4`
- **Geprüfte Evidenzbasis:** Git-Commit `50e7921`
- **Branch:** `codex/pee-wip-recovery-2026-08-06`
- **Profil-ID:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- **Profil-Fingerprint:** `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`
- **Freigabestufe:** IU-3 SHADOW
- **IU-4-/Live-Freigabe:** NEIN

## Implementierter Umfang

- Der aktive L1-Loop lädt PEE-Einstellungen einmal beim Start.
- Der SHADOW-Bridge werden ausschließlich skalare Kopien von Position, Intent,
  Preis, Tick-, Snapshot- und Intent-ID übergeben. Sie erhält keinen mutierbaren
  L1-State.
- Ein hypothetischer FLAT-zu-BUY/SELL-Entry erzeugt vor der Legacy-Execution
  eine PEE-Autorisierung oder einen stabilen Ablehnungsgrund.
- Nach der unveränderten Legacy-Execution wird ein separates
  `paper_economics_shadow`-Auditereignis mit Legacy-Paritätscode geschrieben.
- Berechnungs-, Bridge- oder Logging-Fehler im SHADOW-Pfad können die
  Legacy-Execution nicht blockieren.
- `PEE_MODE=OFF` erzeugt weder SHADOW-Datensätze noch zusätzliche
  SHADOW-Startfelder.

## IU-3-Abnahmekriterien

| Kriterium | Status | Nachweis |
|---|---|---|
| Intent-, Entry- und Exit-Trigger bleiben identisch | BESTANDEN | Ein realer Zwei-Tick-L1-Test vergleicht OFF gegen SHADOW: identische Legacy-Eventfolge, identische Fused Intents, `OPEN_LONG`, `CLOSE_LONG` und identische Execution-Felder. |
| Jeder hypothetische Entry hat Quote oder stabilen Ablehnungsgrund | BESTANDEN | LONG-/SHORT-, Mindestnotional-, ungültige Preis-, ungültige Config- und unerwartete Fehlerpfade sind getestet. |
| SHADOW verändert weder S2/S4 noch Legacy-Trade | BESTANDEN | Die Bridge erhält keinen State; der OFF-/SHADOW-Loopvergleich bestätigt identische persistierte Positionsfelder und Execution-Ergebnisse. |
| Profil-ID, Modellversion und Fingerprint sind in jedem gültigen SHADOW-Datensatz | BESTANDEN | Start- und Entry-Auditfelder werden gegen die angenommene Profilidentität und den exakten Fingerprint geprüft. |

## Ausgeführte Prüfungen

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ergebnis: 76 Tests, OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m py_compile \
  live_l1/core/loop.py \
  live_l1/core/paper_economics_shadow_runtime.py

Ergebnis: OK
```

`git diff --check` war ohne Befund.

## Unveränderte Grenzen

- Legacy-Quantity bleibt `1.0`; PEE-Quantity ist nur hypothetisch.
- Es gibt keine PEE-Wirkung auf S2, S4, Guard-Entscheidungen oder Trade-PnL.
- Es gibt kein IU-4-Enforcement, keine Exchange-Anbindung und keine echten
  Orders.
- Ein historischer oder langer Workstation-SHADOW-Lauf ist nicht Teil dieses
  kleinen Integrationsnachweises und benötigt einen vorhandenen, eindeutig
  gebundenen Datensatz.
