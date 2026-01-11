LIVE_DESIGN_L1_ALARM_FLAG_SCHEMA_FINAL

Projekt: Sniper-Bot
Phase: L1 operativ (Paper Trading)
Status: FINAL / EINGEFROREN
Zweck: Stabiles, maschinen- und menschenlesbares Alarm-Flag
Scope: read-only, einmaliges Schreiben pro Alarm

================================================================
0) Zweck & Einsatz
================================================================
Dieses Schema definiert das exakte Format der Datei
`live_l1_alert.flag`.

- Die Datei existiert NUR im Alarmfall.
- Nicht-Existenz bedeutet OK.
- Kein Überschreiben durch andere Prozesse.
- Keine Interpretation durch den Core.

================================================================
1) Datei-Eigenschaften
================================================================
- Format: JSON (eine einzelne JSON-Objektdatei)
- Encoding: UTF-8, ASCII-only
- Schreibvorgang: atomar (ein Write)
- Lebensdauer: bis manuell gelöscht

================================================================
2) Pflichtfelder (verbindlich)
================================================================
Alle Felder sind PFLICHT.

- status           : string   (immer "ALERT")
- reason           : string   (maschinell, kurz)
- category         : string   (A–F, siehe Kriterien)
- system_state_id  : string   (falls bekannt, sonst "unknown")
- timestamp_utc    : string   (ISO-8601, UTC)
- action           : string   (immer "STOP_RECOMMENDED")
- source           : string   (immer "l1_health_check")

================================================================
3) optionale Felder (erlaubt, nicht verpflichtend)
================================================================
- details          : object   (kleine Zusatzinfos, flach)
- host             : string   (Hostname)
- script_version   : string   (z. B. Git-Commit oder Tag)

Keine weiteren Felder zulässig.

================================================================
4) Wertebereiche & Regeln
================================================================
status:
- MUSS exakt "ALERT" sein

reason:
- snake_case
- max. 64 Zeichen
- Beispiele:
  - missing_system_start
  - incomplete_tick_missing_state_persisted
  - state_s2_position_not_flat
  - log_stale_no_recent_entries

category:
- MUSS einer der folgenden Werte sein:
  - A_LOG_INTEGRITY
  - B_STATE_INVARIANTS
  - C_KILL_LOGIC
  - D_TIME_RHYTHM
  - E_PERSISTENCE
  - F_TRACEABILITY

timestamp_utc:
- Format: YYYY-MM-DDTHH:MM:SSZ
- UTC, keine Millisekunden

action:
- MUSS exakt "STOP_RECOMMENDED" sein

source:
- MUSS exakt "l1_health_check"

================================================================
5) Beispiel (gültig)
================================================================
{
  "status": "ALERT",
  "reason": "state_s2_position_not_flat",
  "category": "B_STATE_INVARIANTS",
  "system_state_id": "L1P-98efd20990ed",
  "timestamp_utc": "2026-01-11T08:14:22Z",
  "action": "STOP_RECOMMENDED",
  "source": "l1_health_check",
  "details": {
    "position": "LONG",
    "size": 0.01
  }
}

================================================================
6) Semantik (verbindlich)
================================================================
- Existenz der Datei = ALARM
- Inhalt dient der Diagnose, nicht der Entscheidung
- Es gibt keinen OK-Status als Datei

================================================================
7) Freeze-Hinweis
================================================================
Dieses Schema ist eingefroren.
Änderungen nur mit neuem Mandat und neuem Dokument.

================================================================
ENDE L1 ALARM FLAG SCHEMA FINAL
