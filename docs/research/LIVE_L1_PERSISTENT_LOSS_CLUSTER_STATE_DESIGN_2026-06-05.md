# LIVE L1 Persistent Loss Cluster State Design - 2026-06-05

## Ziel

Der Loss Cluster Gate State soll Neustarts ueberleben.

Aktuell ist der State nur im Speicher vorhanden:

- recent_closed_trade_pnls
- pause_entries_remaining

Nach einem Prozessneustart geht dieser Zustand verloren.

## Aktuelle Logik

Loss Cluster Parameter:

- Lookback: 10 geschlossene Trades
- Trigger: 5 Verluste innerhalb der letzten 10 Trades
- Pause: 35 Entry-Versuche

Aktuelles Verhalten:

Wenn 5 von 10 zuletzt geschlossenen Trades negativ sind, werden die naechsten 35 Entry-Versuche blockiert.

## Problem

Der Loss Cluster State ist aktuell nicht persistent.

Bei Neustart gehen verloren:

- bisherige PnL-Historie des Loss Gates
- verbleibende Entry-Pause

Dadurch kann der Bot nach Neustart sofort wieder Entries erlauben, obwohl vorher eine Verlustserie aktiv war.

## Ziel-Datei

Persistenter State:

live_state/loss_cluster_state.json

## Geplantes JSON-Schema

{
  "version": 1,
  "recent_closed_trade_pnls": [],
  "pause_entries_remaining": 0,
  "updated_utc": ""
}

## Ladeverhalten

Beim ersten Zugriff auf das Loss Cluster Gate:

1. Datei existiert:
   - JSON laden
   - Werte validieren
   - ungueltige Werte defensiv ignorieren

2. Datei existiert nicht:
   - State mit Defaults initialisieren

## Schreibverhalten

State wird geschrieben nach:

1. geschlossenem Trade
2. reduziertem pause_entries_remaining durch blockierten Entry

## Sicherheitsregeln

- Keine Entry-/Exit-Logik aendern
- Keine Trade-Ausfuehrung aendern
- Keine PnL-Berechnung aendern
- Nur Loss-Gate-State persistieren
- Bei defekter JSON-Datei fallback auf sicheren Default-State
- Keine Exception darf den Trading-Loop stoppen

## Testanforderungen

Mini-Test 1:

- Loss Gate State speichern
- Datei existiert
- JSON enthaelt erwartete Keys

Mini-Test 2:

- State laden
- pause_entries_remaining bleibt nach Neustart erhalten

Mini-Test 3:

- defekte JSON-Datei
- kein Crash
- Default-State wird verwendet

## Entscheidung

Persistenter Loss Cluster State ist sinnvoll.

Grund:

Der Loss Cluster Gate ist ein Schutzmechanismus. Dieser Schutz soll nicht durch einen Prozessneustart verloren gehen.

