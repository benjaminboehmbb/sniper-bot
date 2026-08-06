# LIVE PAPER ECONOMICS PROFILE PROPOSAL V1

**Profil-ID:** `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`  
**Status:** KANDIDAT — fachliche Freigabe ausstehend  
**Betriebsmodus:** ausschließlich `SHADOW`  
**Live-/Produktionsfreigabe:** NEIN  
**Ziel:** konservative, reproduzierbare Paper-Baseline für BTCUSDT

**Kanonischer Konfigurations-Fingerprint:**
`ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`

## 1. Abgrenzung

Dieses Profil ist keine Anlageempfehlung und keine Konfiguration für echte
Orders. Es legt synthetische Paper-Annahmen fest, damit PEE V1 deterministisch
getestet werden kann. Das Repository benennt keine Zielbörse. Gebühren,
Slippage und Ordergrenzen sind deshalb bewusst nicht als aktuelle Werte einer
bestimmten Börse dargestellt.

Eine spätere Exchange-Anbindung muss Instrumentgrenzen und Gebühren neu aus
der autoritativen Schnittstelle der gewählten Börse beziehen. Offizielle
Börsendokumentation beschreibt Quantity-, Notional- und Preisgrenzen als
Instrumentdaten und weist darauf hin, dass einzelne Grenzen geändert werden
können. Beispiel: [Bybit Instruments Info](https://bybit-exchange.github.io/docs/v5/market/instrument).

## 2. Vorgeschlagene Baseline

| Feld | Wert | Begründung |
|---|---:|---|
| `quote_currency` | `USDT` | entspricht dem untersuchten Symbol BTCUSDT |
| `starting_equity_quote` | `10000` | gut lesbare Paper-Ausgangsbasis |
| `risk_per_trade_rate` | `0.0025` | maximal 0,25 % modelliertes Risiko je Trade |
| `max_position_notional_rate` | `0.10` | höchstens 10 % der realisierten Equity als Notional |
| `entry_fee_rate` | `0.001` | synthetische konservative Gebühr von 10 bps |
| `exit_fee_rate` | `0.001` | identische konservative Exit-Gebühr |
| `entry_slippage_bps` | `5` | adverse deterministische Entry-Slippage |
| `exit_slippage_bps` | `8` | höhere adverse Exit-Annahme |
| `quantity_step` | `0.000001` BTC | interne Paper-Granularität, immer abrunden |
| `min_quantity` | `0.00001` BTC | zusätzliche Mindestmenge |
| `min_notional_quote` | `10` USDT | konservative Paper-Mindestgröße |
| `max_daily_loss_rate` | `0.01` | neue Entries ab 1 % realisiertem Tagesverlust sperren |
| `max_daily_fee_rate` | `0.0025` | neue Entries ab 0,25 % Tagesgebühren sperren |
| `max_realized_drawdown_rate` | `0.05` | neue Entries ab 5 % realisiertem Drawdown sperren |
| `reference_stop_rate` | `0.015` | nur Shadow-Fallback; nicht für Enforced zulässig |

## 3. Verbindliche Semantik des Kandidaten

- Keine Hebelwirkung; maximal 1x Notional-Bezug.
- Maximal eine offene Position im bestehenden L1-Zustandsmodell.
- Quantity wird mit `Decimal` berechnet und immer nach unten auf
  `quantity_step` gerundet.
- Gebühren werden pro Ausführungsseite berechnet.
- Slippage wird über adverse Fill-Preise genau einmal berücksichtigt.
- Unrealisierte Gewinne erhöhen das verfügbare Risikobudget nicht.
- Fehlende oder widersprüchliche Account-, Position- oder Konfigurationsdaten
  sperren neue Entries.
- Exits dürfen durch eine Entry-Sperre nicht blockiert werden.

## 4. Tageswechsel und Drawdown

- Tagesgrenze: `00:00:00 UTC`.
- Referenz für Tagesverlust und Tagesgebühren ist die realisierte Equity zu
  Beginn des UTC-Tages.
- Beim Tageswechsel werden nur Tagesverlust und Tagesgebühren zurückgesetzt.
- Equity und realisierte High-Water-Mark bleiben erhalten.
- Der 5-%-Drawdown wird gegen die realisierte High-Water-Mark berechnet und
  niemals durch den Tageswechsel zurückgesetzt.
- Ein Neustart darf Tageszähler nicht doppelt zurücksetzen oder Trades doppelt
  verbuchen.

## 5. Stop-Regel

PEE bestimmt keinen fachlichen Stop. Für Enforced Paper Trading muss der
Referenz-Stop aus der bestehenden, separat freigegebenen Stop-Logik stammen.
`PEE_REFERENCE_STOP_RATE=0.015` ist ausschließlich ein klar markierter
Shadow-Fallback für Vergleichsläufe. IU-4 darf diesen Wert nicht still als neue
Trading-Regel übernehmen.

## 6. Pflichtprüfungen vor einer Freigabe

1. JSON-Profil lädt strikt und erzeugt einen stabilen Fingerprint.
2. Long- und Short-Sizing verletzen weder Risikobudget noch Notional-Cap.
3. Höhere Gebühren oder Slippage verbessern niemals Netto-PnL oder Quantity.
4. Mindestmenge und Mindestnotional sperren zu kleine Entries.
5. Tagesverlust-, Gebühren- und Drawdown-Grenzen sperren nur neue Entries.
6. Tageswechsel und Neustart werden ohne Doppelbuchung getestet.
7. Ein Stresslauf verwendet mindestens 20 bps Slippage je Seite und doppelte
   Gebühren; er ist ein Test, kein zweites Betriebsprofil.
8. Vor Exchange- oder Live-Nutzung werden aktuelle Instrumentfilter,
   Gebühren, Orderarten und Rundungsregeln neu gebunden und geprüft.

## 7. Entscheidung

Dieser Vorschlag darf nach bestandener technischer Prüfung entweder:

- als Paper-Profil angenommen,
- mit exakt benannten Zahlen korrigiert oder
- vollständig verworfen werden.

Ohne ausdrückliche Annahme bleibt `PEE_MODE=SHADOW`. Das Profil autorisiert
weder IU-4-Enforcement noch Live-Trading.
