# BTC-L1 G10-B D1 Partial Decisions V1

**DOCUMENT_STATUS=DRAFT_NOT_BINDING**

Datum der Ausarbeitung (UTC): 2026-09-16

Repository-Stand der Ausarbeitung: `fcc96713c9552731b940ca7aa67eabf381adc468`, Branch `main`, Index und Arbeitsverzeichnis sauber, keine untracked Dateien vor dieser Ablage

Maschinenlesbare Begleitdatei: `docs/review/evidence/BTC_L1_G10B_D1_PARTIAL_DECISIONS_V1_2026-09-16.json`

---

## 1. Status, Umfang und Abgrenzung

### 1.1 Status

Dieses Dokument ist **DRAFT_NOT_BINDING**. Es konsolidiert vier bereits erteilte Teilannahmen zur offenen Definition **D1** des angenommenen Integrationsvertrags sowie die dazugehörigen Grenzen, ausdrücklich nicht angenommenen technischen Vorschläge und offenen Aufgaben.

Der Status **DRAFT_NOT_BINDING** betrifft **diese Konsolidierung**. Er hebt die dokumentierten früheren Teilannahmen **nicht** auf; diese behalten den Status, den ihre jeweilige Freigabe ihnen gegeben hat.

Ausdrücklich gilt:

- **keine** neue formale Annahme dieser Konsolidierung;
- **D1 insgesamt bleibt offen**;
- **keine** Erfüllung der Bindungen **B1 bis B14**;
- **keine** Manifestbindung dieses Dokuments;
- **keine** Implementierungs-, Test-, Qualifikations- oder Laufgenehmigung.

Bestehende Vertragsdateien werden durch dieses Dokument **nicht** geändert. Erforderliche spätere Vertragsänderungen werden hier ausschließlich **dokumentiert**, nicht vollzogen.

### 1.2 Unverändert gültige angenommene Regeln

Unverändert und hier **nicht erneut zur Genehmigung gestellt**: die Festlegungen **P01 bis P07** des Parser-/Numeric-Contracts; **K01 bis K08** sowie sämtliche Serialisierungs-, Schema-, Gate-, Pfad-, Fresh-State- und Abschlussregeln des Output-/Runtime-Contracts; sämtliche Berechnungs-, Kosten-, Sizing-, Settlement-, Metrik- und Bootstrap-Regeln der Evaluator-Klarstellung; die Abschnitte 2 bis 8 des Field-/Helper-Contracts; die Selektions-Gates der Preregistration; die Entscheidungen **D4 bis D17** des Integrationsvertrags einschliesslich der Bindungsstufen BIND-0 bis BIND-4 sowie der Runtime-Datei- und Importbindung nach dessen Abschnitt 10; der angenommene Teilbefund und Geltungsbereichsvorschlag des D2-Dokuments. **V-19 bleibt zurueckgestellt. B1 bis B14 bleiben offen. D2 und D3 bleiben offen** und werden durch dieses Dokument nicht bearbeitet.

---

## 2. Quellenlage und Belegverfahren

Alle vier Teilannahmen wurden **ausschliesslich im Verlauf einer Arbeitssitzung** erteilt. In den versionierten Vertragsunterlagen des Repositoriums existiert fuer **keine** von ihnen ein Nachweis; der Integrationsvertrag fuehrt D1 unveraendert als offene Auflage. Versionierung ersetzt keine Quellenverifikation; umgekehrt ersetzt das Fehlen einer versionierten Fassung nicht die erteilte Freigabe.

Je Teilannahme werden drei Stufen unterschieden:

| Stufe | Bedeutung |
| --- | --- |
| **(a) Originale Nutzerfreigabe** | Die Freigabenachricht des Nutzers, im Sitzungsverlauf im Wortlaut vorhanden |
| **(b) Bestaetigungsantwort** | Die darauf folgende Antwort, die den Annahmeumfang bestaetigt |
| **(c) Unabhaengige Verifikation** | Pruefung der Stufe (a) durch eine von der Sitzung unabhaengige Instanz |

**Prueffgrenze der unabhaengigen Instanz.** Der unabhaengigen Pruefinstanz lagen die Original-Freigaben nach Stufe (a) **nicht direkt vor**. Daraus folgt **weder** eine Widerlegung der Annahmen **noch** ein Beweis ihrer Originaltreue. **Stufe (c) ist fuer alle vier Teilannahmen nicht erbracht.**

Stufe (a) war bei der Erstellung dieses Dokuments verfuegbar; die nachstehenden Zitate sind exakte Uebernahmen aus den Freigabenachrichten und keine Rekonstruktionen. Es werden keine Zeitangaben und keine Quellenkennungen erfunden. Wird dieses Dokument spaeter ausserhalb jener Sitzung weiterverarbeitet, ist der Sitzungsverlauf die einzige Quelle der Stufe (a) und muesste mitgefuehrt werden.

---

## 3. Historische Bearbeitungsaufzeichnung

Eine vorhergehende, inhaltlich kuerzere Fassung dieser Konsolidierung wurde unabhaengig geprueft. Das Ergebnis jener Pruefung lautete **REVISE_BEFORE_DOCUMENTATION** und bezieht sich **ausschliesslich auf jenen frueheren Entwurf**.

| Finding jener Pruefung | Vorgenommene Korrektur in dieser Fassung |
| --- | --- |
| Annahmebelege unklar dargestellt | Abschnitt 2 mit dreistufiger Unterscheidung je Teilannahme; Prueffgrenze der unabhaengigen Instanz ausdruecklich dokumentiert; woertliche Zitate nur aus tatsaechlich verfuegbaren Originalnachrichten |
| E3 verkuerzt wiedergegeben | Abschnitt 6 vollstaendig und eigenstaendig ausformuliert; unbestimmter Verweis auf einen Abschnitt der Vorfassung durch die ausformulierte Fehlerregeltabelle ersetzt |
| Offene Aufgaben falsch kategorisiert | Abschnitt 9 neu gegliedert; Bootstrap-Fenster, EXTENSION-Module und native Bibliotheken als eigenstaendige offene Bereiche; Nachweisluecken werden nicht zu Vertragsentscheidungen umetikettiert |
| Architekturabhaengige Qualifikation zu pauschal | Qualifikation von Ausloesezeitpunkt und Abdeckung des `exec`-Auditereignisses nur noch **bedingt** gefuehrt; eigener kontrollierter Aufruf und zusaetzliche Auditbeobachtung bleiben getrennte Ansaetze |
| E2-Faelle nicht im Dokument definiert | Abschnitt 5 enthaelt die fuenf Falldefinitionen mit erforderlichem Beleg und angenommener Folge |

**Fuer die vorliegende korrigierte Fassung wird keine positive unabhaengige Nachpruefung behauptet.** Eine solche Nachpruefung ist nicht erfolgt.

---

## 4. Begrenzte D1-Umfangspraezisierung

### 4.1 Angenommener Inhalt, woertlich aus der Originalfreigabe

> „D1 verlangt einen nachvollziehbaren Nachweis der Herkunft und Identität des tatsächlich ausgeführten Python-Codes sowie der tatsächlich geladenen dynamischen Abhängigkeiten innerhalb des bereits vertraglich erfassten Umfangs.
> Die Prüfung muss die gemessenen Identitäten belastbar mit den jeweiligen Ausführungs- und Ladeereignissen verbinden. Ein Dateipfad, eine Inode oder ein nachträglich erhobener Dateihash allein ersetzt diese Verbindung nicht.
> Vorhandene Cachedateien sind hinsichtlich ihres Einflusses auf den tatsächlich ausgeführten Code zu bewerten. Bloße Dokumentation ihrer Existenz und Hashes genügt nicht.
> Eine allgemeine Zusicherung unveränderlicher Prozessspeicherinhalte oder die Abwehr beliebiger privilegierter Systemeingriffe wird durch diese Präzisierung nicht zusätzlich verlangt.
> Bestehende Modul-, Import-, Quellen- und Runtime-Bindungen bleiben unverändert. Fehlende Nachweise für bereits erfasste Bestandteile werden durch diese Präzisierung weder optional noch erfüllt.
> Es wird kein bestimmtes technisches Verfahren vorgeschrieben: weder fs-verity noch ausschließlich C-basierte Sollwerteinlesung, Ladeverhinderung oder ein zusätzlicher Prüfprozess.
> Die Ergebnisfreigabe bleibt vom vollständigen Abschluss aller erforderlichen Prüfungen abhängig. Das Verhältnis zwischen Ereignisfenster, späten Ladeereignissen und completion.json ist noch konkret auszuarbeiten. Ein vorhandener Abschlussdatensatz allein beweist keine bislang ungeprüfte Ereignisabdeckung.
> Diese Entscheidung schließt D1 nicht. Sie erfüllt keine der Bindungen B1–B14 und erteilt keine Implementierungs-, Test-, Qualifikations-, Manifest-, Commit-, Push- oder Laufgenehmigung."

### 4.2 Belegstufen

**(a)** Originale Nutzerfreigabe vorhanden, oben woertlich wiedergegeben. **(b)** Bestaetigungsantwort vorhanden; sie enthaelt zwei Klarstellungen: der zuvor vorgeschlagene Beschlusssatz „nur zum Ladeereignis" ist **nicht** angenommen worden, und der Wegfall der allgemeinen Speicherzusicherung entscheidet **nicht** vorab, womit die Bindung der gemessenen Bytes an das Ladeereignis hergestellt wird. **(c)** nicht erbracht.

### 4.3 Betroffene Vertragsstelle und dokumentarische Ergaenzung

Betroffen sind der operative Satz in Abschnitt 10 des Integrationsvertrags („Grenzen der Abdeckung"), der Eintrag D1 in dessen Abschnitt 14 und dessen Abschnitt 20.6.

Erforderliche Ergaenzung: Eintrag der Praezisierung bei D1 in den Abschnitten 14 und 20.6, nach dem in jenen Dokumenten verwendeten Verfahren der zeitlichen Einordnung, ohne den Entwurfswortlaut der Abschnitte vor Abschnitt 20 umzuschreiben.

**Weiterhin fehlend:** saemtliche Nachweise. Die Praezisierung ist eine Umfangsbestimmung.

---

## 5. E2 — Cachebewertung

### 5.1 Angenommene Grundregel, woertlich aus der Originalfreigabe

> „Der Einfluss vorhandener Cachedateien auf den tatsächlich ausgeführten Code muss nachvollziehbar bewertet werden. Zusätzlich muss der ausgeführte Code mit dem vertrauenswürdig abgeleiteten und gebundenen Sollobjekt übereinstimmen.
> Cachezustand und Ausführungsbefund sind getrennt zu behandeln. Existenz, Dateihash, passender Cache-Header oder fehlender Cache reichen jeweils allein nicht als positiver Ausführungsnachweis.
> Die Fälle 1–3 können bei vollständig erbrachten Nachweisen positiv bewertet werden. Eine festgestellte Abweichung des ausgeführten Codeobjekts vom gebundenen Sollobjekt nach Fall 4 führt zum technischen Abbruch mit IDENTITY_MISMATCH. Bei unzureichendem Nachweis nach Fall 5 erfolgt keine Ergebnisfreigabe."

Ebenfalls woertlich Bestandteil derselben Freigabe:

> „‚Fehlender' und ‚unpassender' Sollwert dürfen nicht pauschal unter MANIFEST_INCOMPLETE zusammengefasst werden.
> Fehlende Pflichtangabe, verletzte Bindung und gescheiterte Belegerhebung sind getrennte Sachverhalte.
> Die konkrete Codezuordnung für Fall 5 bleibt offen. Die Aussage ‚kein angenommener Code trägt Fall 5(b)' wird durch diese Freigabe nicht verbindlich übernommen. Keine neuen Fehlercodes einführen.
> Keine Pflicht zum Löschen, Neuerzeugen oder Verbieten von Caches. Das konkrete Schema für den getrennten Ausführungsbefund bleibt eine gesondert anzunehmende Ergänzung."

### 5.2 Belegstufen

**(a)** vorhanden. **(b)** Bestaetigungsantwort vorhanden. **(c)** nicht erbracht.

### 5.3 Falldefinitionen, erforderlicher Beleg, angenommene Folge

| Fall | Definition | Erforderlicher Beleg | Angenommene Folge |
| --- | --- | --- | --- |
| **1** | Cache fehlt; Ausfuehrung erfolgt aus der Quelle | Belegte Feststellung, dass kein Cache gelesen wurde, **und** eigenstaendiger Vergleich des ausgefuehrten Codeobjekts mit dem gebundenen Sollobjekt | Positiv nur bei beiden Belegen. „Kein Cacheeinfluss" beantwortet die Ausfuehrungsfrage nicht; ein fehlender Cache ist kein Nachweis eines korrekten Laufs |
| **2** | Cache ist veraltet oder wird abgelehnt; Quellfallback erfolgt | Zusaetzlich der Beleg, dass die Ablehnung tatsaechlich stattfand | Positiv nur bei vollstaendigen Belegen. Der Cachezustand wird ausgewiesen, ist fuer sich kein Befund |
| **3** | Cache wird verwendet; ausgefuehrtes Codeobjekt entspricht dem Soll | Nachweis der tatsaechlichen Cachenutzung **und** Uebereinstimmung des ausgefuehrten Codeobjekts mit dem gebundenen Sollobjekt | Positiv nur bei beiden Belegen |
| **4** | Cache wird verwendet; ausgefuehrtes Codeobjekt weicht vom Soll ab | Nachweis der tatsaechlichen Cachenutzung und Vergleich des ausgefuehrten Codeobjekts mit dem gebundenen Sollobjekt, wobei eine Abweichung festgestellt wird | **Technischer Abbruch mit `IDENTITY_MISMATCH`**, keine Ergebnisfreigabe |
| **5** | Cacheeinfluss oder ausgefuehrtes Codeobjekt sind nicht ausreichend nachweisbar | — | **Keine Ergebnisfreigabe.** Die konkrete Codezuordnung bleibt **offen**; fehlende Pflichtangabe, verletzte Bindung und gescheiterte Belegerhebung bleiben getrennte Sachverhalte |

**Ausdruecklich festgehalten.** Ein Code-Digest belegt eine Codeabweichung, **nicht** die Cachenutzung und **nicht** die Cacheverursachung. Cachezustand und Ausfuehrungsbefund bleiben getrennt. Es bestehen **keine** Pflichten zur Loeschung, Neuerzeugung oder zum Verbot von Caches. **Keine neuen Fehlercodes.**

### 5.4 Betroffene Vertragsstelle und dokumentarische Ergaenzung

Betroffen sind die Importlisten-Felder `cached_path`, `cached_exists` und `cached_sha256` aus Abschnitt 10 des Integrationsvertrags, wo sie bisher als reine Dokumentationsfelder gefuehrt werden, ferner die Fehlercodemenge und die Schemaergaenzungen jenes Vertrags.

Erforderliche Ergaenzung: Aufnahme der Grundregel und der fuenf Faelle; Kennzeichnung der getrennten Ausweisung des Ausfuehrungsbefunds als **noch nicht angenommene** Schemaergaenzung; Vermerk der offenen Fall-5-Zuordnung.

**Weiterhin fehlend:** Schema des Ausfuehrungsbefunds; Fall-5-Codezuordnung; saemtliche Belegerhebungsverfahren, die nicht qualifiziert sind.

---

## 6. E3 — Rollen, Empfang, Siegel, Abschluss, Status, Freigabe

### 6.1 Umfang der Annahme, woertlich aus der Originalfreigabe

> „Ich nehme den zuletzt vorgelegten ‚E3 — Konsolidierter Entwurf, korrigierte Fassung' als E3-Verfahrensfestlegung im folgenden begrenzten Umfang an."

Die Freigabe zaehlt die angenommenen Bestandteile einzeln auf: Rollenaufteilung zwischen Evaluator E und Abschlussprozess A; fortlaufender Empfang und Prozessueberwachung; Sequenz-, Siegel-, Lese- und Abschlussregeln; Trennung technischer Gueltigkeit vom wirtschaftlichen Ergebnis; Statusableitung und Metrikfreigabe; Veroeffentlichungspunkt von `completion.json`; vorgesehene aeussere Rueckgabewertzuordnung; Trennung vorab gebundener Regeln von spaeterer Ist-Evidenz. Ferner woertlich:

> „Damit sind A als geplante Komponente, die Ereignisspur als geplantes Artefakt und die Übertragung der Abschlussverantwortung auf A grundsätzlich angenommen. Die erforderliche Dokumentation dieser Änderungen in den Vertragsunterlagen steht noch aus."

**(a)** vorhanden. **(b)** Bestaetigungsantwort vorhanden, ergaenzt um eine redaktionelle Berichtigung: „Vier Lesezustaende" wurde an beiden Fundstellen durch „Fuenf Lesezustaende" ersetzt. **(c)** nicht erbracht.

### 6.2 Rollen

**E** fuehrt den Lauf durch — BIND-3-Startpruefungen, Strom, Ledger, Reconciliation, Kennzahlen, Gates, `.partial`-Schreiben, Veroeffentlichung der fachlichen Ergebnisartefakte in der angenommenen Umbenennungsreihenfolge — und sendet fortlaufend die Ereignisspur. **E schreibt keinen Abschlussnachweis.**

**A** wird vor E gestartet, besitzt den Empfangskanal, ueberwacht E, prueft Spur und Artefakte, leitet den Abschlussstatus ab und veroeffentlicht **als einzige Instanz** `completion.json`.

### 6.3 Kanal und Deskriptoren

A erzeugt den Kanal und behaelt das Leseende. Genau das Schreibende wird fuer E auf eine vereinbarte Deskriptornummer abgebildet; nur fuer diese eine Nummer wird das Close-on-exec-Flag aufgehoben. Close-on-exec wirkt erst beim `exec` und verhindert die Deskriptorkopie durch `fork` **nicht**; daher schliesst das Kind nach `fork` das Leseende und alle uebrigen ererbten Deskriptoren vor dem `exec`, und A schliesst seine eigene Kopie des Schreibendes unmittelbar nach dem Start von E. Erst dann kann ein Stromende eintreten.

### 6.4 Fortlaufender Empfang und Lesezustaende

**A leert den Kanal fortlaufend, waehrend E laeuft**, und erkennt die Beendigung im selben Warteschritt; **ein blockierendes Warten auf E bei unbeachtetem Empfangskanal findet nicht statt.** Leseende und Prozessdeskriptor liegen in derselben Bereitschaftsabfrage. Das **Leseende wird nichtblockierend gefuehrt**; eine feste Kanalkapazitaet oder Puffergroesse wird nicht vorausgesetzt.

**Zugelassene Alternativen.** Threads oder asynchrone Laufzeiten sind zulaessige Alternativen zur beschriebenen gemeinsamen Bereitschaftsabfrage. Keine dieser Moeglichkeiten wird durch dieses Dokument implementiert oder qualifiziert. Der fortlaufende Empfang und die Abschlussbedingungen dieses Abschnitts bleiben in jedem Fall verpflichtend.

**Fuenf getrennte Lesezustaende:**

| Zustand | Behandlung |
| --- | --- |
| Bytes gelesen | weiterverarbeiten |
| tatsaechliches EOF | Empfangsende feststellen |
| `EAGAIN` beziehungsweise `EWOULDBLOCK` | erneut auf Bereitschaft warten, kein Empfangsende |
| `EINTR` | Lesevorgang wiederholen; gilt **weder als EOF noch als gelesener Datensatz** |
| sonstiger Fehler | kein positiver Abschluss |

**EOF ersetzt weder die Siegelpruefung noch die Pruefung des Prozessstatus.**

### 6.5 Sequenz, Siegel, Abschluss des Empfangs

Nutzdatensaetze tragen die Folgenummern **1 bis n**. Es gibt **genau ein Siegel**; es traegt die **Folgenummer n+1**, enthaelt die **deklarierte Anzahl n** und einen Aggregathash **ausschliesslich ueber die Nutzdatensaetze 1 bis n**; das Siegel selbst geht in diesen Hash **nicht** ein.

**A berechnet den Aggregathash unabhaengig nach.** Ein positiver Abschluss ist ausgeschlossen bei: falscher deklarierter Anzahl; abweichendem Aggregathash; fehlenden, doppelten, ruecklaeufigen oder anderweitig ungueltigen Folgenummern; einem zweiten Siegel; **jedem Datensatz nach dem Siegel**.

**Reihenfolge des Empfangsabschlusses.** A erfasst **zuerst den Beendigungsstatus von E selbst**, liest **danach** bis zum **tatsaechlichen EOF** und stellt fest, dass die Nutzfolge lueckenlos 1 bis n ist, genau ein Siegel mit Folgenummer n+1 vorliegt, dessen Anzahl gleich n ist, der nachberechnete Aggregathash uebereinstimmt und nach dem Siegel kein Datensatz eingetroffen ist.

**Transportkonsistenz ersetzt keine Ereignisvollstaendigkeit.** Ein Siegel mit Folgenummer 1 und Anzahl 0 — der Fall **n = 0** — ist transportseitig gueltig, erfuellt aber **fuer sich keinen E1-Nachweis**: eine leere Spur kann ebenso bedeuten, dass der Erfassungsmechanismus nichts erzeugt hat. Die Bewertung gegen eine erwartete Mindestereignismenge gehoert zu E1 und bleibt offen.

### 6.6 Beendigungsstatus von E

Ein positiver Abschluss verlangt die **regulaere Beendigung von E mit dem angenommenen Erfolgsrueckgabewert, von A selbst beobachtet**. Eine Signalbeendigung schliesst ihn aus, auch bei formal einwandfreiem Siegel. Der intern beobachtete Status von E wird getrennt aufgezeichnet und nicht in die Statuszuordnung von A ueberfuehrt.

### 6.7 Technische Gueltigkeit vor wirtschaftlicher Aussage

Die angenommenen Vorabpruefungen bleiben an ihren Zeitpunkten und werden weder ersetzt noch abgeschwaecht: **BIND-3 beim Start**, **bestandene Reconciliation vor den Kennzahlen**, saemtliche Integritaets- und Erfassungsnachweise. `integrity.status` ist **keine** wirtschaftliche Gate-Komponente, bleibt aber nach angenommener Definition technische Voraussetzung.

### 6.8 Wirtschaftliche Statusableitung

Erst nach bestandenen technischen Pruefungen, allein aus dem angenommenen Schema, ohne Neuberechnung von Kennzahlen und ohne Aenderung von Gate-Regeln:

1. **Zuerst Vollstaendigkeitspruefung der erforderlichen Gate-Menge je Szenario.** Fehlende Gates duerfen **nicht** durch eine Konjunktion ueber die verbliebenen Eintraege verdeckt werden.
2. Konjunktion ueber alle Gate-Eintraege mit `status = PASS` je Szenario und Vergleich mit `scenarios.<S>.all_gates_pass`; Wurzelkonjunktion aus `NOMINAL` und `STRESS` und Vergleich mit dem Wurzelwert. `integrity.status` geht nicht ein.
3. Pruefung von `control_evidence.all_pass` gegen seine drei Einzelstatus.
4. Die als `NOT_REQUIRED` gefuehrten Stressobjekte `cagr`, `calmar` und `bootstrap_lcb95` **erhalten keine zusaetzlichen Gates** und gehen nicht ein.

**Zuordnung:** alle erforderlichen Gates bestanden ergibt `COMPLETED_PASS`; mindestens eines verfehlt ergibt `COMPLETED_FAIL`. Ein **unvollstaendiges oder widerspruechliches** Ergebnis ist **kein** wirtschaftliches `COMPLETED_FAIL`, sondern ein technischer Befund ohne wirtschaftlichen Status. Ein neues Entscheidungswort in `result.json` ist nicht erforderlich.

### 6.9 Veroeffentlichung und Metrikfreigabe

Maßgeblicher Veroeffentlichungspunkt ist die **erfolgreiche einmalige Umbenennung von `completion.json.partial` nach `completion.json`**.

`metrics_released=true` setzt **saemtliche** erforderlichen technischen Pruefungen voraus: Integritaet, Erfassung, Ladespur, Protokoll nach den Abschnitten 6.3 bis 6.6, Reconciliation und Artefaktpruefung. Ein wirtschaftlich verfehltes Gate verhindert die Metrikfreigabe bei technisch gueltigem Lauf **nicht**: **`COMPLETED_PASS` und `COMPLETED_FAIL` koennen beide `metrics_released=true` tragen.** Technische Fehler duerfen **nicht** als `COMPLETED_FAIL` erscheinen.

**Ergebnisdateien allein bewirken keine Freigabe:** eine final benannte `result.json` ohne Abschlussnachweis ist nach angenommener Regel keine Freigabe. Die **nachgelagerte Pruefung des fertigen Laufs bleibt erforderlich**.

### 6.10 Aeussere Rueckgabewerte

| Wert | Bedeutung |
| --- | --- |
| `0` | **beide** wirtschaftlichen Ausgaenge, `COMPLETED_PASS` und `COMPLETED_FAIL` |
| `2` | `TECHNICAL_ERROR` **mit geschriebenem Abschlussnachweis** |
| `3` | unvollstaendiger Lauf **ohne Abschlussnachweis** |

Diese Zuordnung gilt fuer den **gesamten Evaluator-Aufruf**, den A abschliesst, und beschreibt den vorgesehenen kontrollierten Abschluss. **Bei gewaltsamer Beendigung von A wird kein bestimmter Rueckgabewert garantiert.** Eine wirtschaftliche Unterscheidung durch neue Codes findet nicht statt.

### 6.11 Vorabbindung gegenueber Ist-Evidenz

BIND-2 bindet vorab: Identitaet von A, die Protokoll- und Pruefregeln nach den Abschnitten 6.3 bis 6.6 und 6.8 sowie den Pruefungsumfang von A. Die tatsaechlichen Bytes und Hashes der Ereignisspur entstehen erst im Lauf und werden wie beobachtete BIND-1b-Werte gefuehrt, **nie** als BIND-2-Sollwert. Damit besteht keine zyklische oder zeitlich unmoegliche Bindung.

### 6.12 Fehlerregeln

| Fall | Angenommene Folge |
| --- | --- |
| Signalbeendigung von E | Kein positiver Abschluss. Ein `TECHNICAL_ERROR`-Abschluss ist **nur** moeglich, wenn die dafuer erforderlichen Fehler- und Abschlussartefakte tatsaechlich vorliegen; sonst unvollstaendiger Lauf ohne gueltigen Abschlussnachweis. **Keine pauschale `TECHNICAL_ERROR`-Zuordnung** |
| Fehlendes Siegel, zweites Siegel, Datensatz nach dem Siegel | Kein positiver Abschluss; keine pauschale `TECHNICAL_ERROR`-Zuordnung |
| Falsche Anzahl, abweichender Aggregathash, ungueltige Folgenummer | Kein positiver Abschluss |
| Lesefehler ausser `EAGAIN`, `EWOULDBLOCK` und `EINTR` | Kein positiver Abschluss |
| Unvollstaendige Ereigniserfassung | Kein positiver Abschluss; gesonderte E1-Voraussetzung |
| Unvollstaendige oder widerspruechliche Gate-Menge | Technischer Befund, **kein** `COMPLETED_FAIL` |
| Fehler von A **vor** der Veroeffentlichung | Kein `completion.json`; eine liegengebliebene `completion.json.partial` zaehlt zum Verzeichnisinhalt und macht den Lauf nach angenommener Regel ungueltig; keine Freigabe |
| Veroeffentlichung **nachweislich gescheitert** | Kein Ersatzname, nichts ueberschrieben, nichts entfernt; Lauf unvollstaendig; keine Freigabe |
| Veroeffentlichung **nachweislich erfolgreich**, A faellt danach aus | `completion.json` steht; **weder automatisch gueltig noch automatisch ungueltig**; es gelten unveraendert saemtliche angenommenen Abschluss- und Integritaetsbedingungen des fertigen Laufs |
| Ausgang der Veroeffentlichung **ungewiss** | **Keine** automatische Wiederholung, **keine** Aussage ueber die Dateiexistenz; Feststellung allein durch die nachgelagerte Pruefung des tatsaechlichen Verzeichnisinhalts |

Es wird **keine** neue Fehlercodezuordnung und **keine** Schemafestlegung getroffen.

### 6.13 Konflikte mit bestehenden Vertragsstellen

| Gegenstand | Bestehende Stelle | Erforderliche Aenderung |
| --- | --- | --- |
| Geplante Komponente **A** | Abschnitt 2 des Integrationsvertrags: „Keine weiteren Module und keine weiteren Artefakte." | Ausdrueckliche Vertragsaenderung |
| Geplante **Ereignisspur** | dieselbe Stelle | Ausdrueckliche Vertragsaenderung |
| **Uebergang der Abschlussverantwortung** | Modultabelle in Abschnitt 2, wonach der Baustein `artifacts` den Abschlussnachweis verantwortet; reservierte Abschlussnamen und Rueckgabewerte „des Evaluators" in Abschnitt 7 | Schreiber von `completion.json` wechselt von E zu A; Rueckgabewerte als Werte des Gesamtaufrufs zu lesen |
| **Identitaet von A** | BIND-2; B1 bis B14 enthalten kein solches Feld | Zusaetzliches Bindungsfeld |

---

## 7. E1 — Mengenregel Z/R/O, Wegpflicht, Wiederholungen

### 7.1 Angenommener Inhalt, woertlich aus der Originalfreigabe

> „Z bezeichnet die vorab festgelegte zulässige SOURCE-Modulmenge innerhalb des festgelegten Geltungsbereichs. R bezeichnet die daraus abgeleitete, zwingend erwartete Modulmenge. O bezeichnet die aus geprüften Ausführungsnachweisen beobachtete Menge.
> Z, R und ihre Herleitungsregeln sind vor dem Lauf in BIND-2 zu binden. Keine nachträgliche Anpassung von R an die beobachteten Ergebnisse. Für einen technisch gültigen Abschluss gilt R ⊆ O ⊆ Z.
> Jede relevante SOURCE-Modulausführung im festgelegten Geltungsbereich muss den vorgeschriebenen kontrollierten Ladeweg verwenden und einen gültigen Nachweis besitzen. Dies gilt auch für nur bedingt benötigte zulässige Module. Wiederholungen sind einzelne Ausführungsereignisse; die Mengenbildung darf fehlende Ereignisnachweise nicht verdecken."

Ebenfalls woertlich Bestandteil derselben Freigabe:

> „Eine Startprüfung der Importliste beweist nicht bereits O ⊆ Z für den gesamten späteren Ablauf. Dafür ist der entsprechende Laufnachweis weiterhin erforderlich.
> Andere Finder oder Loader müssen nicht generell abwesend sein. Nachzuweisen ist, dass relevante Ausführungen innerhalb des festgelegten SOURCE-Geltungsbereichs keinen unzulässigen Ersatzweg nehmen. Daraus folgt keine neue Regel für andere Modularten.
> Diese Regeln beweisen weder die Vollständigkeit von O noch die durchgehende Wirksamkeit der Erfassung. Ihre Durchsetzung bleibt offener Bestandteil von E1."

### 7.2 Belegstufen

**(a)** vorhanden. **(b)** Bestaetigungsantwort vorhanden, einschliesslich der dort uebernommenen Ruecknahme zweier frueherer Aussagen: „O ⊆ Z ist bereits durchgesetzt" und der Forderung nach genereller Abwesenheit weiterer Finder oder Loader. **(c)** nicht erbracht.

### 7.3 Betroffene Vertragsstelle und dokumentarische Ergaenzung

Betroffen sind die Import-Allowlist und die Importliste aus Abschnitt 10 des Integrationsvertrags sowie BIND-2 und die BIND-3-Startpruefung.

Erforderliche Ergaenzung: Aufnahme der Begriffe Z, R und O mit ihren Herleitungsregeln; der Relation R ⊆ O ⊆ Z als Bedingung technischer Gueltigkeit; der Wegpflicht; der Einzelnachweispflicht fuer Wiederholungen, nebst dem Vermerk, dass die angenommene Importliste eine Zustandsliste **je Modulname** ist und Wiederholungen nicht fuehren kann.

**Weiterhin fehlend:** Belegung von Z und R; Vollstaendigkeit von O; durchgehende Wirksamkeit; Durchsetzungsnachweis der Wegpflicht; Startzustand und Aktivierungszeitpunkt.

---

## 8. Ausdruecklich nicht angenommene technische Vorschlaege

| Gegenstand | Status |
| --- | --- |
| Kontrollierter SOURCE-Loader | bevorzugter Entwurfsansatz, **VORSCHLAG_NICHT_ANGENOMMEN** |
| Aufrufdatensatz des Loaders und dessen Felder | Schema-Vorschlaege, **nicht angenommen**. Ein Beginnvermerk bezeichnet den **Aufrufversuch**, nicht einen nachgewiesenen Beginn des Modulrumpfs |
| Nachweis ueber den eigenen kontrollierten Aufruf | begrenzter Teilentwurf, **nicht angenommen**; belegt ausschliesslich Aufrufe dieses Loaders und erfordert **kein** Auditereignis |
| Zusaetzliche Auditbeobachtung des `exec`-Ereignisses | **getrennter**, nicht angenommener Ansatz; **nicht** Voraussetzung des kontrollierten Loaders |
| Threadlokale Stapelkorrelation von Ankuendigung und Ereignis | **verworfen**; bleibt verworfen |
| Interpreter- und Startprofil des Evaluators | **nicht angenommen**; die Aufloesung des Evaluatorpakets bei gleichzeitiger Isolation ist ungeklaert |

---

## 9. Berichtete Umgebungsbefunde

Die folgenden Befunde sind Bestandsaufnahmen. Sie sind **keine** Runtime-Bindung, **keine** Kompatibilitaetspruefung und **keine** Qualifikation.

- Gefunden: CPython 3.12.3 unter `/usr/bin/python3.12`, 8020928 Bytes, SHA256 `e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f`; `/usr/bin/python3` ist ein symbolischer Link darauf.
- Im untersuchten Umfang wurde **keine** Projekt-`.venv` und keine `pyvenv.cfg` vorgefunden.
- Es existiert **keine** verbindliche evaluatorbezogene Versionsauswahl; die Anforderungsdatei des Repositoriums ist nach angenommener Vertragsregel eine Entwicklungsvorgabe und kein Lock.
- In `/usr/bin/python3.12` wurde **kein direkter libpython-`DT_NEEDED`-Verweis** gefunden; die `DT_NEEDED`-Eintraege sind `libm.so.6`, `libz.so.1`, `libexpat.so.1` und `libc.so.6`; `DT_RPATH` und `DT_RUNPATH` fehlen. Daraus folgt keine Aussage ueber transitive oder spaeter dynamisch geladene Bibliotheken.

---

## 10. Offene Aufgaben

### 10.1 Erforderliche Entwurfsentscheidungen

1. Befundzuordnung fuer E2-Fall 5, getrennt nach fehlender Pflichtangabe, verletzter Bindung und gescheiterter Belegerhebung.
2. Schema des getrennten Ausfuehrungsbefunds sowie Schema der Ereignisspur und des Aufrufdatensatzes.
3. Bindungsfeld fuer die Identitaet von A in BIND-2.
4. Herleitungsregeln und Geltungsbereich fuer Z und R.
5. Aufloesung des Evaluatorpakets beim Start sowie Interpreter- und Startprofil fuer E und fuer A.
6. Wahl des Nachweisverfahrens fuer die Ereignisabdeckung; ob ueberhaupt ein Auditereignis verwendet wird, ist offen.

### 10.2 Ausstehende Dokumentationsaufgaben

Die Rollen- und Verantwortungsaenderungen nach Abschnitt 6.13 sind **bereits angenommen**. Ihre Aufnahme in die Vertragsunterlagen ist eine **ausstehende Dokumentationsaufgabe** und **keine** erneut zu treffende Architekturentscheidung. Die konkreten Schema- und Bindungsfelder bleiben davon unberuehrt und gesondert offen; sie sind unter Abschnitt 10.1 gefuehrt.

### 10.3 Eigenstaendige offene E1- und D1-Bereiche

Die folgenden Punkte sind **Nachweisluecken**, keine Vertragsentscheidungen:

- **Bootstrap-Fenster** vor Aktivierung des kontrollierten Ladewegs;
- **EXTENSION-Module**;
- **native Bibliotheken**, einschliesslich der Trennung von Ladeereignis, gemeldetem Pfad und Identitaet der geladenen Bytes;
- **vollstaendige Ereigniserfassung**, also die Vollstaendigkeit von O;
- **durchgehende Wirksamkeit** des kontrollierten Ladewegs ueber ein Intervall statt ueber Zeitpunkte;
- **Durchsetzung der Wegpflicht**;
- **fehlende Quellenbindungen** fuer Standardbibliothek, Evaluator und Drittanbieter.

### 10.4 Fehlende konkrete Bindungen

**B3** Python-Identitaet des Erzeugerlaufs, **B5** Interpreter, **B6** Decimal-Backend, **B7** NumPy, **B8** Evaluator-Quellen, **B9** Import-Abschluss, **B10** Dependency-Lock sowie **B11 bis B14** unveraendert. Zusaetzlich fehlt im angenommenen Manifestschema eine **Wurzelkennung fuer die Standardbibliothek**.

Festgehalten: eine Kopplungsentscheidung zwischen B5 und B3 ist **nicht** erforderlich. Keine angenommene Vertragsstelle verlangt Identitaetsgleichheit oder eine Ableitung, und BIND-3 vergleicht die Selbstauskunft der Evaluierungsumgebung gegen **BIND-2**.

### 10.5 Fehlende Implementierung und Qualifikationsnachweise

Evaluatorpaket, kontrollierter Loader und Komponente A sind nicht vorhanden. Anschliessend zu qualifizieren waeren:

- Reproduzierbarkeit der Sollwertableitung;
- Kanaleigenschaften, Deskriptorbehandlung sowie Verlaesslichkeit von Statuserfassung und EOF;
- Nummerierungs- und Siegeldisziplin unter Abbruch, einschliesslich der unabhaengigen Nachberechnung des Aggregathashes;
- Vollstaendigkeitspruefung der erforderlichen Gate-Menge;
- Qualifikation von A;
- Rueckwirkungsfreiheit gegen die BIND-0-Vergleichswerte;
- **bedingt:** Ausloesezeitpunkt und Abdeckung des `exec`-Auditereignisses, **nur** falls ein spaeter gewaehltes Nachweisverfahren dieses Ereignis verwendet. Der eigene kontrollierte Aufruf benoetigt es nicht.

### 10.6 Nicht erneut als offen gefuehrt

Die vier Umfangsentscheidungen selbst sind getroffen: D1-Praezisierung, E2-Umfang, E3-Verfahren sowie E1-Mengen- und Wegregel. Ihre **Dokumentation**, ihre **Umsetzung** und ihre **Nachweise** bleiben offen; eine angenommene Regel ist kein erbrachter Nachweis.

---

## 11. Quellen- und Beleggrenzen

1. **Stufe (c) fehlt durchgehend.** Fuer alle vier Teilannahmen ist keine von der Arbeitssitzung unabhaengige Verifikation der Original-Freigaben erbracht. Der unabhaengigen Pruefinstanz lagen sie nicht direkt vor; daraus folgt weder Widerlegung noch Bestaetigung.
2. **Keine versionierte Fassung der Teilannahmen.** Keine der vier Teilannahmen ist bislang in den Vertragsunterlagen dokumentiert; der Integrationsvertrag fuehrt D1 unveraendert als offene Auflage. Dies ist eine Dokumentationsluecke, keine Annahmeluecke.
3. **Stufe (a) war bei Erstellung verfuegbar**, weshalb woertlich zitiert und nichts rekonstruiert wurde. Ausserhalb jener Sitzung ist der Sitzungsverlauf die einzige Quelle der Stufe (a).
4. **Fuer die Umgebungsbefunde nach Abschnitt 9 besteht keine Beleglucke**; sie wurden erhoben und protokolliert, tragen jedoch ausdruecklich keine Bindung.

---

## 12. Abschluss

Dieses Dokument ist **DRAFT_NOT_BINDING**. Es begruendet keine neue Annahme. **D1 bleibt offen.** **E2, E3 und die E1-Mengen- und Wegregel behalten ihren bestaetigten Umfang.** **D2, D3, B1 bis B14 und X1 bleiben unberuehrt.** Aus diesem Dokument folgt keine Implementierungs-, Test-, Qualifikations-, Manifest-, Selektions-, Staging-, Commit-, Push- oder Ausfuehrungsfreigabe.
