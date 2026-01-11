LIVE_DESIGN_L2_MANDATE_SCOPE_AND_ENTRY_CRITERIA

Projekt: Sniper-Bot
Phase: Übergang L1 → L2
Status: verbindliches Mandat
Scope: Definition & Freigabe
Kein Code, keine Umsetzung, keine Optimierung

================================================================
0) Zweck & Mandatscharakter
================================================================
Dieses Dokument definiert das formale Mandat
für den Übergang von L1 (Paper Trading)
zu L2 (erweiterter Betrieb / kontrollierte Erweiterung).

Es erlaubt:
- die inhaltliche Abgrenzung von L2
- die Definition von Eintrittskriterien
- die klare Trennung von Betrieb und Entwicklung

Dieses Dokument ist KEINE Implementierungsanweisung.

================================================================
1) Voraussetzungen für L2 (Eintrittskriterien)
================================================================
Ein Übergang zu L2 ist NUR zulässig, wenn:

- L1 Exit & Review-Protokoll abgeschlossen ist
- formale Entscheidung „L1 FREIGEGEBEN“ vorliegt
- alle L1-Dokumente eingefroren bleiben
- kein offener L1-B oder L1-D Defekt existiert

Ohne vollständige Erfüllung:
→ L2 NICHT erlaubt

================================================================
2) Abgrenzung L1 vs. L2 (klar & verbindlich)
================================================================

L1 (abgeschlossen):
- reiner Paper-Betrieb
- HOLD-only oder strikt begrenzte Aktionen
- Fokus: Stabilität, Observability, Restart-Sicherheit
- keine Performance-Diskussion

L2 (Mandatsfähig):
- kontrollierte Erweiterung des Betriebs
- klar begrenzte neue Fähigkeiten
- weiterhin defensive Architektur
- jede Erweiterung explizit dokumentiert

================================================================
3) Erlaubter Scope von L2
================================================================
L2 DARF umfassen (grundsätzlich, nicht automatisch):

- Erweiterung der Policy über HOLD hinaus
- kontrollierte Intent-Typen (z.B. BUY/SELL unter strengen Guards)
- erweiterte Guards & Kill-Regeln
- feinere Health-Checks
- erweiterte Monitoring-Logik

Jeder Punkt erfordert ein separates L2-Design-Dokument.

================================================================
4) Explizit verbotener Scope in L2
================================================================
Auch in L2 weiterhin VERBOTEN:

- Strategie-Optimierung
- K-Exploration (K3–K12)
- ML / adaptive Systeme
- Performance-Ziele (ROI, Winrate, Sharpe)
- Vergleich mit GS-Ergebnissen
- automatische Selbstheilung
- unkontrollierte Live-Rechte

================================================================
5) L2-Designpflichten (vor Umsetzung)
================================================================
Vor JEGLICHER Umsetzung in L2 MUSS existieren:

- klar benanntes L2-Teilmandat
- neues, separates Design-Dokument
- explizite Guards & Abbruchbedingungen
- Rückfallstrategie auf L1-Niveau
- klare Observability-Anforderungen

Ohne diese Punkte:
→ keine Umsetzung erlaubt

================================================================
6) Übergangsregeln L1 → L2
================================================================
- L1-Code bleibt unverändert
- L1-Betrieb wird nicht „weitergebaut“
- L2 beginnt in separatem Kontext
- Rückkehr zu L1 jederzeit möglich
- keine stillen Übergänge

================================================================
7) Stop-Regeln innerhalb von L2
================================================================
Ein L2-Versuch MUSS sofort gestoppt werden bei:

- Verletzung von L1-Invarianten
- nicht erklärbarem Verhalten
- unvollständiger Observability
- impliziter Erweiterung ohne Mandat

Stop bedeutet:
- kein „Fix im Betrieb“
- Analyse außerhalb des Systems

================================================================
8) Mandatsentscheidung
================================================================
Dieses Dokument erlaubt:

[ ] Antrag auf L2-Start
[ ] Definition konkreter L2-Teilmandate
[ ] Vorbereitung (nur Design, kein Code)

Dieses Dokument erlaubt NICHT:
- automatische Umsetzung
- stillen Phasenwechsel

================================================================
9) Dokumentationspflicht
================================================================
Für jeden L2-Schritt MUSS dokumentiert sein:

- welches Teilmandat aktiv ist
- welcher Scope erlaubt ist
- welche Guards gelten
- wie der Abbruch erfolgt

================================================================
10) Zentrale Invariante
================================================================
L2 ist keine Optimierungsphase,
sondern eine kontrollierte Erweiterung
eines bereits stabilen Systems.

Stabilität schlägt Funktionsgewinn.

================================================================
11) Abschluss
================================================================
Mit diesem Mandat ist L2
inhaltlich abgegrenzt und vorbereitet.

Eine Umsetzung erfordert
ein separates, explizites L2-Design.

ENDE L2 MANDAT
