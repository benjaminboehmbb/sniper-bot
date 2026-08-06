# LIVE PAPER ECONOMICS PROFILE — TECHNICAL EVIDENCE V1

- **Prüfdatum:** 2026-08-06
- **Prüfbasis:** Git-Commit `43c7022`
- **Branch:** `codex/pee-wip-recovery-2026-08-06`
- **Profil:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- **Fingerprint:** `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`
- **Ergebnis:** technische Pflichtprüfungen 1–7 bestanden; Punkt 8 bleibt vor einer Exchange- oder Live-Nutzung offen.

## Ausgeführte Prüfungen

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_economics_profile_candidate

Ergebnis: 9 Tests, OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ergebnis: 70 Tests, OK
```

`git diff --check` war ohne Befund.

## Abgleich mit den Pflichtprüfungen

| Nr. | Pflichtprüfung | Status | Nachweis |
|---:|---|---|---|
| 1 | Striktes Laden und stabiler Fingerprint | BESTANDEN | Exakte Profil-ID, `SHADOW`, Readiness und Fingerprint werden geprüft. |
| 2 | LONG-/SHORT-Sizing innerhalb Risk- und Notional-Cap | BESTANDEN | Beide Seiten werden mit dem Kandidatenprofil autorisiert und gegen beide Caps geprüft. |
| 3 | Höhere Kosten verbessern weder Quantity noch Netto-PnL | BESTANDEN | Doppelgebühren und 20 bps Slippage je Seite werden gegen die Baseline verglichen. |
| 4 | Quantity-, Mindestmengen- und Mindestnotional-Grenzen | BESTANDEN | Zero-Quantity, `min_quantity` und `min_notional_quote` werden getrennt abgelehnt. |
| 5 | Daily-Loss-, Fee- und Drawdown-Grenzen sperren nur Entries | BESTANDEN | Exakte Kandidatengrenzen liefern stabile Reason Codes; `exit_allowed` bleibt wahr. |
| 6 | UTC-Tageswechsel und Neustart ohne Doppelbuchung | BESTANDEN | Unterbrochenes Settlement wird einmalig recovered; zweiter Recovery-Lauf ist leer; Tageszähler wechseln korrekt. |
| 7 | Stresslauf mit mindestens 20 bps und doppelten Gebühren | BESTANDEN | Als Testkonfiguration ausgeführt, nicht als zweites Betriebsprofil gespeichert. |
| 8 | Aktuelle Exchange-Regeln neu binden | OFFEN | Keine Zielbörse und keine Exchange-/Live-Freigabe vorhanden; vor einer solchen Nutzung zwingend nachzuholen. |

## Aussagegrenzen

- Das Profil bleibt ein fachlich noch nicht angenommenes `SHADOW`-Profil.
- Der aktive L1-Loop wurde nicht verändert.
- Es gab keine Exchange-Anbindung, keine echten Orders und keine Live-Freigabe.
- Die technische Prüfung ersetzt weder die menschliche Profilentscheidung noch die getrennte Freigabe späterer Integrationsstufen.
