# RCC-002 C2 Review Lineage Investigation

## Dokumentmetadaten

| Feld | Wert |
|---|---|
| Dokumentklasse | Governance-Untersuchungsdokument (offen, nicht abgeschlossen) |
| Dokument-ID | `RCC-002-C2-INVESTIGATION` |
| Titel | Review Lineage Investigation — RCC-002 Finding C2 (Bundle-Hash-Diskrepanz) |
| Version | 1.0.0 |
| Datum | 2026-07-25 |
| Status | Offen — Untersuchung nicht abgeschlossen; keine Ursache festgestellt |
| Speicherort im Repository | `docs/review/RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md` |
| Dateiname | `RCC_002_C2_REVIEW_LINEAGE_INVESTIGATION_2026-07-25.md` |
| Abhängigkeiten | `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`; `RCC_002_SCR_006_FINDINGS_2026-07-24.md`; `RCC_002_AIR_002_FINDINGS_2026-07-24.md`; `RCC_002_C1_SCIENTIFIC_CONSISTENCY_REVIEW_2026-07-25.md` (Prüfung F) |
| Referenziert durch | `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` §6; jeder künftige Architecture Integrity Re-Review, Editorial Pass oder Internal Certification, die auf der SCR-006/AIR-002-Freigabekette aufbauen wollen |
| Autoritative Sprache | Deutsch für normative Erläuterung; englische Feld- und Konstantennamen wie im Quellmaterial |

Dieses Dokument stellt **keine** Ursachenklärung dar. Es sammelt den
gesicherten Faktenstand, benennt offene Fragen und kennzeichnet mögliche
Ursachen ausdrücklich als ungeprüfte Hypothesen. Es darf nicht als
Nachweis eines bestimmten Ursachenzusammenhangs zitiert werden.

---

## 1. Problemdefinition

`RCC-002-SCR-006` und `RCC-002-AIR-002` referenzieren in ihren eigenen
Dokumentmetadaten einen Paket-SHA-256 für
`RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`, der von dem
tatsächlich im Repository vorliegenden, unabhängig mehrfach nachgemessenen
SHA-256 dieser Datei abweicht. Zeilen- und Bytezahl weichen ebenfalls
jeweils um genau 1 voneinander ab. Damit ist derzeit nicht verifizierbar,
dass sich die in `RCC-002-SCR-006` und `RCC-002-AIR-002` dokumentierten
PASSED-Urteile auf exakt die Bytes beziehen, die aktuell im Repository
liegen.

---

## 2. Bekannte Hashwerte

| Quelle | Zeilen | Bytes | SHA-256 |
|---|---:|---:|---|
| Tatsächliche Datei `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` (mehrfach unabhängig gemessen: `sha256sum`, `wc`, byte-exakter Generator-Round-Trip) | 13776 | 485064 | `5aae1bd7107ace3baf1de8178349169249b387756fe406598a8a7fad1ed190b2` |
| In `RCC_002_SCR_006_FINDINGS_2026-07-24.md`, Abschnitt „Dokumentmetadaten“, referenzierter Paket-SHA-256 | 13777 (dort „Paketzeilen“ genannt) | 485065 (dort „Paketbytes“ genannt) | `33aac77fe96147c8d81e8683db470f50780159b7168e1139214592f7fd6e26c5` |
| In `RCC_002_AIR_002_FINDINGS_2026-07-24.md`, Abschnitt „Dokumentmetadaten“, referenzierter Paket-SHA-256 | nicht separat angegeben | nicht separat angegeben | `33aac77fe96147c8d81e8683db470f50780159b7168e1139214592f7fd6e26c5` (identisch zu SCR-006) |

Delta: +1 Zeile, +1 Byte zwischen der tatsächlichen Datei und dem in
SCR-006/AIR-002 referenzierten Stand; vollständig unterschiedlicher
SHA-256 (wie bei jeder Byteänderung durch die Hashfunktion erwartet).

---

## 3. Betroffene Reviews

| Review | Ergebnis laut eigenem Dokument | Bezug auf welchen Hash |
|---|---|---|
| `RCC-002-SCR-006` | Bestanden | `33aac77f…` |
| `RCC-002-AIR-002` | Bestanden, referenziert SCR-006 als Voraussetzung („genau dasselbe Paket“) | `33aac77f…` |
| `RCC-002-C1-SCR` (2026-07-25, unabhängig von diesem Dokument) | Bestanden mit Minor Findings | tatsächliche Datei `5aae1bd7…`, nicht `33aac77f…` |

Editorial Pass und Internal Certification des alten Bundles sind in den
vorliegenden Unterlagen nicht als durchgeführt dokumentiert und daher von
dieser Untersuchung nicht zusätzlich betroffen.

---

## 4. Bekannte Fakten

1. Die Datei `docs/review/RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md`
   ist ausschließlich im Git-Commit `e2e1d022e37bc871d5024d79cf9484c3a1ee9df1`
   („Add RCC-002 corrected specification bundle“, Autor Benjamin Boehm,
   2026-07-24 11:56:24 +0200) enthalten — als vollständige Neuanlage
   (13776 Insertions, keine Änderung eines bestehenden Blobs). Es existiert
   im Git-Verlauf kein weiterer Commit, der diese Datei berührt
   (verifiziert über `git log --all -- <Datei>`).
2. `RCC_002_SCR_006_FINDINGS_2026-07-24.md` und
   `RCC_002_AIR_002_FINDINGS_2026-07-24.md` sind **nicht** im selben
   Commit enthalten wie die Bundle-Datei. Beide sind ausschließlich im
   Commit `2092d9c42b580668905f8f7934bb066549bd3d73` („Freeze RCC-002
   specification package before Editorial Pass“, derselbe Autor,
   2026-07-24 **11:53:26** +0200 — drei Minuten **vor** `e2e1d02`)
   enthalten, ebenfalls als vollständige Neuanlage. Dieser frühere Commit
   enthält die Bundle-Datei selbst nicht.
3. Damit wurden die beiden Reviewbefunde, deren Metadaten den Hash
   `33aac77f…` referenzieren, chronologisch **vor** der Bundle-Datei
   committet, die im Repository heute als „das geprüfte Paket“ vorliegt.
   Dies ist eine verifizierte Tatsache (Commit-Zeitstempel und
   -Reihenfolge), keine Interpretation ihrer Ursache.
4. `docs/specifications/` (die sieben kanonischen Einzeldokumente) war zu
   keinem Zeitpunkt im Git-Verlauf dieses Repositories committet
   (`git log --all -- docs/specifications/` liefert keine Treffer).
5. Ein Bundle-Generator existierte vor dem 2026-07-25 nicht auffindbar im
   Repository (siehe `RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md`
   §5).
6. Die im alten Bundle eingebettete Datei-Tabelle (Zeilen 9–17 der Datei)
   ist intern konsistent mit dem im selben Bundle eingebetteten Inhalt der
   sieben Einzeldokumente (verifiziert per Extraktion und Hash-Vergleich
   im Rahmen der C1-Korrektur).
7. Das Delta zwischen der tatsächlichen Datei und dem SCR-006/AIR-002-
   referenzierten Stand beträgt exakt 1 Zeile und 1 Byte.

---

## 5. Offene Fragen

1. Existiert eine historische Fassung von
   `RCC_002_SCR_005_CORRECTED_FULL_SPEC_BUNDLE_2026-07-24.md` mit SHA-256
   `33aac77f…` irgendwo außerhalb des Git-Verlaufs (lokale Sicherung,
   Editor-Backup, Chat-/Sitzungsprotokoll der Erzeugung, Zwischenablage
   eines Reviewsystems) — insbesondere aus dem Dreiminutenfenster
   zwischen 11:53:26 und 11:56:24 am 2026-07-24, oder davor?
2. Wurde der in SCR-006/AIR-002 referenzierte Hash tatsächlich gegen eine
   zum Zeitpunkt 11:53:26 vorliegende Datei berechnet, oder wurde er
   manuell übertragen, abgetippt oder aus einem Zwischenschritt kopiert?
3. Ist das 1-Byte/1-Zeilen-Delta mit einer einzelnen, lokalisierbaren
   Byteposition erklärbar (z. B. Vorhandensein/Fehlen eines
   abschließenden Zeilenumbruchs am Dateiende), oder verteilt es sich auf
   mehrere Stellen im Dokument?
4. Was geschah konkret in den drei Minuten zwischen dem Commit
   `2092d9c` (11:53:26, enthält nur die beiden Reviewbefunde) und dem
   Commit `e2e1d02` (11:56:24, enthält erstmals die Bundle-Datei)? Wurde
   die Bundle-Datei in diesem Fenster neu erzeugt, umbenannt, oder aus
   einem bereits vorher existierenden, aber nicht committeten Stand
   übernommen?
5. Warum benennt der Commit `2092d9c` sich „Freeze RCC-002 specification
   package before Editorial Pass“, obwohl das darin referenzierte Paket
   (die Bundle-Datei) zu diesem Zeitpunkt nicht Teil des Commits und damit
   nicht Teil des versionierten „eingefrorenen“ Zustands ist?

---

## 6. Ausdrücklich als Hypothese gekennzeichnete mögliche Ursachen

Die folgenden Punkte sind **ungeprüfte Hypothesen**, keine Feststellungen.
Keiner dieser Punkte ist durch Evidenz belegt; sie dienen ausschließlich
der Eingrenzung der nächsten Untersuchungsschritte.

- **Hypothese H1 (Whitespace/Zeilenende):** Zwischen der Erstellung der
  SCR-006/AIR-002-Befunde (spätestens 11:53:26) und dem Commit der
  Bundle-Datei (11:56:24) könnte ein zusätzlicher abschließender
  Zeilenumbruch (oder eine vergleichbare einzelne Whitespace-Differenz)
  entfernt oder hinzugefügt worden sein. Diese Hypothese ist mit dem
  beobachteten Delta von genau +1 Zeile/+1 Byte formal vereinbar, aber
  nicht bestätigt.
- **Hypothese H2 (manuelle Hash-Übertragung):** Der referenzierte Hash
  könnte bei der Erstellung von SCR-006/AIR-002 fehlerhaft übertragen
  worden sein (Tippfehler, falsches Kopierziel), ohne dass die
  zugrunde liegende Datei selbst abweicht. Gegen diese Hypothese spricht,
  dass auch Zeilen- und Bytezahl abweichen, nicht nur der Hash — ein
  reiner Tippfehler im Hash allein würde dieses Muster nicht erklären.
- **Hypothese H3 (Reihenfolge-/Prozessartefakt):** Die verifizierte
  Tatsache, dass die Bundle-Datei selbst erst drei Minuten **nach** den
  beiden Reviewbefunden committet wurde (Abschnitt 4, Fakten 1–3), lässt
  offen, ob zum Zeitpunkt 11:53:26 überhaupt bereits eine finale,
  committingfähige Bundle-Datei vorlag, gegen die SCR-006/AIR-002 geprüft
  haben könnten, oder ob der Review gegen einen Zwischenstand
  (Arbeitskopie, Vorschau, nicht committeter Entwurf) erfolgte, der sich
  vor dem Commit um genau 1 Byte verändert hat. Diese Hypothese ist durch
  die Commit-Reihenfolge **nahegelegt**, aber nicht bewiesen — die
  Commit-Reihenfolge zeigt nur, *wann* welche Datei versioniert wurde,
  nicht *was* zum Zeitpunkt der Reviewerstellung tatsächlich vorlag.

Keine dieser drei Hypothesen ist gegenüber den anderen als erwiesen zu
behandeln, solange keine der in Abschnitt 7 genannten Evidenzen vorliegt.
Hypothese H3 ist durch die in Abschnitt 4 dokumentierte Commit-Reihenfolge
stärker mit den bekannten Fakten verknüpft als H1 und H2, was sie nicht zu
einer bestätigten Ursache macht, sondern lediglich zum naheliegendsten
nächsten Untersuchungsstrang.

---

## 7. Benötigte Evidenz

Um die Ursache einzugrenzen oder festzustellen, werden mindestens
benötigt:

1. Eine byte-exakte Kopie der Datei, wie sie zum Zeitpunkt der
   SCR-006/AIR-002-Durchführung tatsächlich vorlag (falls auffindbar),
   zur direkten Verifikation ihres SHA-256 gegen `33aac77f…`.
2. Falls 1. nicht auffindbar: jedes verfügbare Protokoll oder jede
   Aufzeichnung des Erzeugungsprozesses von SCR-006/AIR-002, das den
   tatsächlich verwendeten Prüfbefehl und dessen Eingabe zeigt.
3. Zeitstempel-Metadaten (Dateisystem, Sitzungsprotokoll) zur Klärung der
   in Abschnitt 5, Frage 4 gestellten zeitlichen Reihenfolge.
4. Ein byteweiser Vergleich (falls 1. beschafft werden kann) zur exakten
   Lokalisierung der abweichenden Bytes.

---

## 8. Ausschlusskriterien

Folgende, zunächst naheliegende Erklärungen sind bereits geprüft und
**ausgeschlossen**:

- **Fehler bei der Hash-Berechnung im Rahmen dieser Untersuchung:** Der
  tatsächliche Hash der Datei wurde mehrfach unabhängig mit
  unterschiedlichen Methoden reproduziert (`sha256sum`, Python
  `hashlib.sha256`, byte-exakter Generator-Round-Trip-Test) und ist in
  allen Fällen identisch (`5aae1bd7…`). Ein Messfehler auf dieser Seite
  ist ausgeschlossen.
- **Fehlerhafte Extraktion der sieben Einzeldokumente als Ursache des
  Deltas:** Die interne Datei-Tabelle des alten Bundles selbst (dessen
  eigene Angaben zu Zeilen/Bytes/SHA-256 je Einzeldokument) stimmt exakt
  mit dem im selben Bundle eingebetteten Inhalt überein. Das Delta liegt
  nicht in der Extraktionsmethode, sondern in der Diskrepanz zwischen der
  Bundle-Datei als Ganzes und dem SCR-006/AIR-002-Wert.
- **Nachträgliche Veränderung durch die C1-Korrektur:** Der alte Bundle
  wurde im Rahmen der C1-Korrektur nachweislich nicht verändert (vor und
  nach der C1-Korrektur identischer SHA-256 `5aae1bd7…`, mehrfach
  geprüft).

---

## 9. Entscheidungskriterien

Für den Abschluss dieser Untersuchung gilt:

| Ergebnis der Untersuchung | Konsequenz |
|---|---|
| Historische Fassung mit Hash `33aac77f…` wird gefunden und unterscheidet sich von der aktuellen Fassung nur durch eine nicht-normative Whitespace-/Zeilenende-Differenz | SCR-006/AIR-002 gelten inhaltlich als weiterhin gültig für die aktuelle Fassung; SCR-006/AIR-002 werden um einen Hash-Korrekturvermerk ergänzt; Architecture Integrity Re-Review der C1-Korrektur kann wie geplant fortgesetzt werden. |
| Historische Fassung mit Hash `33aac77f…` wird gefunden und unterscheidet sich inhaltlich (normativer Text) von der aktuellen Fassung | SCR-006 und AIR-002 gelten als **nicht gültig** für die aktuelle Fassung; ein vollständiger, nicht fokussierter Re-Review beider Stufen gegen die aktuelle Fassung ist erforderlich, bevor die C1-Korrektur oder irgendein nachfolgendes Gate weiterverfolgt wird. |
| Keine historische Fassung mit Hash `33aac77f…` ist auffindbar und auch keine sonstige Evidenz (Protokoll, Aufzeichnung) klärt die Diskrepanz | SCR-006 und AIR-002 gelten als **nicht verifizierbar** für die aktuelle Fassung; dieselbe Konsequenz wie im vorherigen Fall — vollständiger Re-Review beider Stufen erforderlich. |

In allen drei Fällen bleiben Architecture Integrity Review, Editorial
Pass, Internal Certification und alle nachfolgenden Gates bis zum
Abschluss dieser Untersuchung gesperrt (siehe
`RCC_002_C1_CORRECTED_BUNDLE_MANIFEST_2026-07-25.md` §6).

---

## 10. Empfohlene Untersuchungsschritte

1. Gezielte Suche nach einer historischen Fassung des alten Bundles
   außerhalb des aktuellen Git-Commits (lokale Editor-Backups,
   Sitzungsprotokolle, Zwischenablagen der Reviewerzeugung).
2. Falls gefunden: SHA-256 dieser Fassung berechnen und gegen `33aac77f…`
   prüfen; bei Übereinstimmung byteweisen Diff gegen die aktuelle Fassung
   bilden und nach Abschnitt 9 klassifizieren.
3. Falls nicht auffindbar: mit dem Autor/Verantwortlichen der
   ursprünglichen SCR-006/AIR-002-Erzeugung klären, ob eine Aufzeichnung
   des tatsächlich verwendeten Prüfbefehls und dessen Eingabe existiert.
4. Unabhängig vom Ergebnis: `RCC_002_SCR_006_FINDINGS_2026-07-24.md` und
   `RCC_002_AIR_002_FINDINGS_2026-07-24.md` um einen datierten
   Korrektur- oder Bestätigungsvermerk ergänzen, sobald diese
   Untersuchung ein Ergebnis nach Abschnitt 9 liefert.
5. Dieses Dokument nach Abschluss der Untersuchung mit dem tatsächlichen
   Ergebnis aktualisieren und den Status von „Offen“ auf „Abgeschlossen“
   setzen.

Bis zur Durchführung dieser Schritte bleibt der Status dieses Dokuments
**Offen**, und keine der in Abschnitt 6 genannten Hypothesen darf als
Tatsache behandelt werden.
