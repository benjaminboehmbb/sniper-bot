# L2_PREMORTEM_RISKS_FINAL

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: FINAL – Pre-Mortem (codefrei)
Datum: 2026-01-11

Zweck:
Dieses Dokument beschreibt bewusst die wichtigsten Fehlerszenarien (Pre-Mortem)
für L2, bevor irgendeine Implementierung erfolgt.
Ziel ist nicht Optimierung, sondern maximale Fehlerprävention
und klare Stop-Entscheidungen unter Stress.

Keine Implementierung, kein Code, keine Tests.

================================================================
0. Grundannahme des Pre-Mortem
================================================================

Annahme:
„L2 ist gescheitert oder hat ein unerwünschtes Risiko erzeugt.“

Frage:
Was sind die wahrscheinlichsten Ursachen – und wie müssen wir reagieren,
ohne im Betrieb zu improvisieren?

================================================================
1. Risiko 1: L2 greift unbeabsichtigt in L1 ein
================================================================

Beschreibung:
- L2 schreibt direkt oder indirekt in L1-Pfade
- L2 verändert L1-Config, ENV oder State
- L2 beeinflusst L1-Loop-Verhalten

Woran würden wir es merken:
- Unerwartete Änderungen in L1-Logs oder States
- L1-Verhalten ändert sich ohne erklärbaren Grund
- L1 reagiert anders bei Restart

Korrekte Reaktion:
- SOFORT STOPP von L2
- Keine Reparatur im Betrieb
- Analyse außerhalb des Live-Systems
- Rückkehr zu reinem L1-Betrieb

================================================================
2. Risiko 2: L2 läuft weiter trotz L1-Alarm
================================================================

Beschreibung:
- live_l1_alert.flag existiert
- L2 trifft trotzdem Entscheidungen
- L2 wird nicht deaktiviert

Woran würden wir es merken:
- Audit-Logs von L2 nach Auftreten eines Alarms
- Entscheidungen mit gleichzeitigem Alarm-Zeitstempel

Korrekte Reaktion:
- L2 sofort deaktivieren
- Alarmursache zuerst analysieren
- Keine Bewertung von L2-Entscheidungen
- Kein Fix, bevor Ursache klar dokumentiert ist

================================================================
3. Risiko 3: L2-Entscheidungen sind nicht reproduzierbar
================================================================

Beschreibung:
- Gleiche Inputs führen zu unterschiedlichen Entscheidungen
- Fehlende oder implizite Annahmen
- Zeit- oder Zustandsabhängigkeiten außerhalb des Contracts

Woran würden wir es merken:
- Audit-Replay liefert abweichende Ergebnisse
- Entscheidung kann nicht eindeutig erklärt werden

Korrekte Reaktion:
- L2 sofort stoppen
- Reproduzierbarkeit herstellen, bevor weitergemacht wird
- Keine Übergangslösungen oder Heuristiken

================================================================
4. Risiko 4: Scope-Leak (L2 wird „schlauer“ als erlaubt)
================================================================

Beschreibung:
- Neue Heuristiken schleichen sich ein
- L2 beginnt zu „bewerten“, statt nur zu prüfen
- Implizite Optimierungslogik entsteht

Woran würden wir es merken:
- Entscheidungen lassen sich nicht mehr rein binär erklären
- Begründungen werden vage oder probabilistisch
- Diskussionen über Performance tauchen auf

Korrekte Reaktion:
- STOPP der Implementierung
- Rückkehr zum Mandat
- Scope neu klären, nicht erweitern

================================================================
5. Risiko 5: Operative Unsicherheit unter Stress
================================================================

Beschreibung:
- Unter Zeitdruck werden Regeln „weich“
- Stop-Kriterien werden ignoriert
- Fixes im laufenden Betrieb

Woran würden wir es merken:
- „Nur schnell testen“-Gedanken
- Ad-hoc-Änderungen ohne Dokumentation
- Abweichung von Checklisten

Korrekte Reaktion:
- Arbeit pausieren
- Status-Snapshot lesen
- Nächste Schritte nur nach Ruhephase entscheiden

================================================================
6. Zentrale Leitregel
================================================================

Bei JEDEM der oben genannten Risiken gilt:

- STOP > FIX
- Analyse > Aktion
- Dokumentation > Intuition
- L1-Sicherheit > L2-Fortschritt

================================================================
7. Zweck dieses Dokuments
================================================================

Dieses Dokument dient:
- als mentale Sicherheitsleine
- als Entscheidungsanker unter Stress
- zur Vermeidung von Live-Improvisation

Es ersetzt keine Logs
und trifft keine operativen Entscheidungen.

ENDE
