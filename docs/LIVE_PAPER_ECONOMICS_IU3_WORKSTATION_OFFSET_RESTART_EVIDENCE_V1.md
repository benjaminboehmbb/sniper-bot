# LIVE PAPER ECONOMICS — IU-3 WORKSTATION OFFSET/RESTART/FULL-HISTORY EVIDENCE V1

- **Prüfdatum:** 2026-08-07
- **Branch:** `codex/pee-wip-recovery-2026-08-06`
- **Offset-Runner-Commit:** `7893aca276802b547af8c2b07d47d4ac6d469e53`
- **Restart-Runner-Commit:** `ab060bd50670786a228b69418b96c9a580313d9a`
- **Ausführung:** Workstation, WSL Ubuntu, 32 CPUs, 61 GiB RAM
- **Freigabestufe:** IU-3 SHADOW
- **IU-4-/Live-Freigabe:** NEIN

## Identitätsbindung

- **Quelldatensatz-SHA-256:**
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`
- **Quelldateigröße:** `446578512` Bytes
- **Workstation-Datensatz:**
  `/home/workstation/datasets/sniper-bot/price_data_with_signals_regime.sha256-2896badb.csv`
- **Profil-ID:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- **Profil-Fingerprint:**
  `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`
- **Profil-Datei-SHA-256:**
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`
- **Seed-SHA-256:**
  `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`

Quelle und Zielkopie wurden vor der Ausführung bytegenau per SHA-256 und
Dateigröße abgeglichen.

## Offset-Kampagne

Fünf disjunkte Läufe zu je 200.000 gültigen Datensätzen decken insgesamt
1.000.000 Execution-Events ab.

| Gültiger Offset | Zeitraum (UTC) | Transitions | OPEN/CLOSE | Observations | Issues | ID-Parität |
|---:|---|---:|---:|---:|---:|---|
| 0 | 2017-08-17 04:00 – 2018-01-03 10:23 | 60 | 30/30 | 115 | 0 | JA |
| 200.000 | 2018-01-03 10:24 – 2018-05-23 20:08 | 40 | 20/20 | 69 | 0 | JA |
| 400.000 | 2018-05-23 20:09 – 2018-10-10 12:50 | 56 | 28/28 | 68 | 0 | JA |
| 600.000 | 2018-10-10 12:51 – 2019-02-26 20:40 | 40 | 20/20 | 71 | 0 | JA |
| 800.000 | 2019-02-26 20:41 – 2019-07-16 11:01 | 78 | 39/39 | 39 | 0 | JA |

Alle fünf Prozesse endeten mit Return Code 0. Die aktiven Observation-IDs
stimmen in jedem Lauf exakt mit den integrierten Sidecar-IDs überein.

| Offset | Market-SHA-256 | Sidecar Report-ID |
|---:|---|---|
| 0 | `0b38752473c3082fc20c206ee35b0fd2f0f2e26a6b1426501bc74a667f5d4d6f` | `7f666f57bd827811c4dda66539496232aabebea53ca822a94f1641a4f99cdcd7` |
| 200.000 | `8a37c1f8383b2b76e645b8e9832729a2e2acb85219415306108763e60c9624ef` | `26323c50bfa2435977b561cb8aaba0b316ffd5ae2abfb17bd7f8184216360405` |
| 400.000 | `990458e8170fb6dd788a2f55947557991001f7d979f5af86f476849b379db6ec` | `ca66ac28783e711a078305a65a2ec5d752ac65c84a4bb0d54d28907b1bc0e06c` |
| 600.000 | `64b5c595ef7d9575b08f0085a1f33d882a19bc5bffb356a68c3c15bac482ca2c` | `3b76ebceeb4f46385daa5a7e63df069beabcccde6c81caf7d694038e3771afdd` |
| 800.000 | `68852cb7b92ffb9596ac3df278f532f1fa09bce0a03b756f51012583deff44df` | `303b00dbeac0d0424ab62fcb4b5fd6c6fed044739b4695d978bf22ae50b48509` |

## Offset-400.000-Restart-Gate

Der 200.000er Lauf wurde nach exakt 100.000 Ticks beendet und aus demselben
State-Verzeichnis mit aktivierter Startup-Recovery und Reconciliation-Gate
fortgesetzt.

| Kriterium | Ergebnis |
|---|---|
| Return Codes beider Segmente | 0 / 0 |
| System-State-IDs | `L1P-92b2efb0af4` / `L1P-218d49a1d2c` |
| IDs voneinander verschieden | JA |
| Recovery-Modus | `resume` |
| Erwarteter/beobachteter Resume-Snapshot | `CSV-00100000` / `CSV-00100000` |
| Erwarteter/beobachteter Final-Snapshot | `CSV-00200000` / `CSV-00200000` |
| Startup-Recovery angewendet | 1 |
| S2-/S4-Datensätze | 200.000 / 200.000 |
| Malformed-State-Zeilen | 0 |
| Execution-Events / Transitions | 200.000 / 56 |
| OPEN_LONG / CLOSE_LONG | 28 / 28 |
| Sidecar Observations / Issues | 68 / 0 |
| Aktive IDs = Sidecar-IDs | JA |

- **Market-SHA-256:**
  `990458e8170fb6dd788a2f55947557991001f7d979f5af86f476849b379db6ec`
- **L1-/Stdout-SHA-256:**
  `d1e55d76eb01da22b219bd885aab5d6a97d43727638ea9ea816954f36bed16a6`
- **S2-SHA-256:**
  `5e9b9f8f9820cf14e762e6eae604fe31568f038c6ace8d617bd70b072be18ad6`
- **S4-SHA-256:**
  `85094085fef454589f1a0be4bfd69f1dc0514523a513968164dbe0cd8ec5a138`
- **Sidecar Report-ID:**
  `9aae6177e451af54929948245c82df66b7c60d282523049e57a5af403842cadd`
- **Sidecar-Report-SHA-256:**
  `3ee1ce77b5e8951dbb9763df50da7536606fcf19e0ec030edab0d006fbe4e5e0`

## Vollständiger Historienlauf

Der abschließende Einzelprozess deckt alle `1042658` gültigen Datensätze in
einem zusammenhängenden L1-SHADOW-Lauf ab.

| Kriterium | Ergebnis |
|---|---|
| Source-ID | `PEE-IU3-WS-FULL-HISTORY-1042658-20260807` |
| Git-Commit | `ab060bd50670786a228b69418b96c9a580313d9a` |
| Laufzeit (UTC) | 2026-08-07 08:16:47 – 11:48:00 |
| Return Code | 0 |
| Zeitraum der Marktdaten (UTC) | 2017-08-17 04:00 – 2019-08-15 01:59 |
| Gescannte / gültige / ungültige Zeilen | 1.048.200 / 1.042.658 / 5.542 |
| Execution-Events / Transitions | 1.042.658 / 222 |
| OPEN_LONG / CLOSE_LONG | 111 / 111 |
| L1-Logzeilen | 7.299.006 |
| Sidecar Observations / Issues | 397 / 0 |
| Aktive IDs = Sidecar-IDs | JA |

- **Market-SHA-256:**
  `902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a`
- **L1-/Stdout-SHA-256:**
  `2fb2a5c5dd62a697dbb35247916aad86b2fe61243b17d9b084bbaa0d94d45ccd`
- **S2-SHA-256:**
  `9561db973fba378760a41972cb2ba21fd9629dfccdeb019d00468dec0a1d304c`
- **S4-SHA-256:**
  `76313f0a6f6bc3db0a98ebf3e3c1c689f36849d735cf7e35ade9a028247b1ad7`
- **Sidecar Report-ID:**
  `99b89db1ac43c866d229f0e877fd4e7a61b556818a3ba91116fc30a55798112b`
- **Sidecar-Report-SHA-256:**
  `cffa36672c049c4d5a9faa654963416c6800d6070bf3c894e7c82dbf424e327b`

Alle sechs Ausgabedateien wurden nach Laufende unabhängig erneut gehasht und
stimmten exakt mit den Manifestwerten überein.

## Ablage und Aufräumregel

Die Workstation-Manifeste und Sidecar-Reports bleiben unter
`/home/workstation/runs/sniper-bot/` erhalten. Große Rohartefakte wie der
normalisierte Marktslice, L1-/Stdout-Logs sowie S2-/S4-Zeilen wurden nach der
SHA-256-Dokumentation entfernt, weil sie vollständig reproduzierbar sind. Alle
sieben Manifeste und Sidecar-Reports blieben erhalten. Der gebundene
Quelldatensatz bleibt im separaten Dataset-Verzeichnis erhalten.

Das Workstation-Hauptprojekt wurde auf den geprüften Restart-Commit
`ab060bd50670786a228b69418b96c9a580313d9a` vereinheitlicht. Die temporäre
zweite Projektkopie, die Transfer-Bundles und der abgeschlossene
Kampagnen-Starter wurden anschließend entfernt.

## Ergebnis und Aussagegrenzen

- **Offset-Gate:** PASS
- **Restart-/Resume-Gate:** PASS
- **Full-History-Gate:** PASS
- **Vollständige historische Abdeckung:** 1.042.658 gültige Datensätze
- **Kumuliertes Validierungsvolumen:** 2.242.658 Execution-Events einschließlich
  überlappender Restart- und Offset-Prüfungen
- **Sidecar Issues:** 0 in allen sieben Läufen
- Die Ergebnisse autorisieren ausschließlich IU-3 SHADOW.
- Es gibt kein IU-4-Enforcement, keine Exchange-Anbindung und keine echten
  Orders.
