# BTC-L1 G10-B — Ereignisspur-Protokoll E → A

**Datum:** 2026-09-16

**Status: VORSCHLAG_NICHT_ANGENOMMEN**

**Gegenstand:** nicht bindender Protokoll- und Schemaentwurf für die Ereignisspur zwischen Evaluator E und Abschlusskomponente A.

**Unabhängige Prüfung:** `APPROVE_FOR_DOCUMENTATION`, keine Findings im geprüften Umfang. Die Einstufung betrifft ausschliesslich die Dokumentierbarkeit als nicht bindender Vorschlag. **Keine Runtime-Qualifikation, keine formale Annahme, keine Implementierungs- oder Ausführungsfreigabe.**

**Prüfgegenstand:** Der geprüfte Gegenstand war der im Verlauf ausgegebene Chattext des konsolidierten Entwurfs. **Es wird keine Prüfung einer Repository-Datei und keine Prüfung einer Dateiidentität behauptet.** **Der hier neu hinzukommende Dokumentkopf wurde nicht unabhängig geprüft.**

**Reichweite:** Dieses Dokument ersetzt keinen früheren Entwurf und nimmt keinen früheren Entwurf formal an. Bestehende E3-Abschlussregeln und wirtschaftliche Regeln bleiben unverändert. **D1 bleibt offen.**

---

## 1. Bestehende Vorgaben gegenüber neuen Vorschlägen

### 1.1 Unverändert übernommen (begrenzt angenommene E3-Regeln)

| Nr. | Regel |
| --- | --- |
| B-1 | Fortlaufender Empfang durch A während E läuft |
| B-2 | Nutzdatensätze mit Folgenummern **1 bis n** |
| B-3 | **Genau ein** Siegel mit Folgenummer **n+1** |
| B-4 | Das Siegel enthält die Anzahl **n** und einen Aggregathash **ausschliesslich über die Nutzdatensätze** |
| B-5 | A berechnet Anzahl und Hash **unabhängig** nach |
| B-6 | **Kein Datensatz nach dem Siegel** |
| B-7 | Prozessende und tatsächliches EOF werden **unabhängig** festgestellt |
| B-8 | **Transportkonsistenz beweist keine Ereignisvollständigkeit** |
| B-9 | **n = 0 ist für sich kein E1-Nachweis** |

### 1.2 Bereits vorhandene Serialisierungskonvention, wiederverwendet

Der Integrationsvertrag legt für JSONL-Artefakte fest: „genau ein Objekt, Schlüssel sortiert, `ensure_ascii`, Trennzeichen Komma und Doppelpunkt ohne Leerzeichen, Zeilenende LF", und für Aggregathashes die Bildung über „die UTF-8-Bytes aller so gebildeten Zeilen". **Das Protokoll übernimmt diese Konvention unverändert.**

### 1.3 Neue Festlegungen — sämtlich Vorschläge

Alles in den Abschnitten 2 bis 7 ist **neue Gestaltungswahl** und **nicht angenommen**, soweit nicht ausdrücklich als bestehende Vorgabe gekennzeichnet.

### 1.4 Drei Ebenen, strikt getrennt

| Ebene | Was das Protokoll leistet |
| --- | --- |
| Transportkonsistenz | vollständig adressiert |
| Laufzuordnung | eine Nachrichtenart trägt die `run_id`; die Prüfung erfolgt dateisystemseitig nach dem Laufzuordnungsentwurf |
| Ausführungsidentität | **nicht adressiert.** Das Protokoll transportiert Felder; es erzeugt **keine** Erfassungsfähigkeit. Offene SOURCE-, EXTENSION-, Bootstrap-, Cache- und native Ladefragen bleiben offen |

---

## 2. Nachrichtenformat und Hashgrundlage

### 2.1 Bevorzugtes Format — JSON Lines

Eine Nachricht = die UTF-8-Bytes **genau eines JSON-Objekts**, gefolgt von **genau einem LF** (`0x0A`).

**Begründung:** identisch zur bereits angenommenen JSONL-Konvention; A und E teilen eine fixierte, byte-genaue Serialisierungsdisziplin; keine zweite Formatfamilie.

### 2.2 Festlegungen im Einzelnen

| Gegenstand | Festlegung |
| --- | --- |
| Protokollversion | Feld `proto` im **Header-Datensatz** (Folgenummer 1). Genau **ein** gebundener Wert, **keine Aushandlung**. Abweichung ⇒ ungültig |
| Nachrichtenabgrenzung | Zerlegung ausschliesslich an `0x0A`. Innerhalb einer Nachricht darf `0x0A` nicht vorkommen; Zeilenumbrüche in Zeichenketten werden als `\n` escaped |
| Kodierung | UTF-8 mit `ensure_ascii`. **Invariante:** jedes übertragene Byte liegt in `0x20`–`0x7E`, ausser dem abschliessenden `0x0A`. Jedes andere Byte ist ein Transportverstoss |
| Schlüsselreihenfolge | aufsteigend sortiert |
| Trennzeichen | Komma und Doppelpunkt **ohne Leerzeichen** |
| Zulässige Typen | Zeichenkette, **Ganzzahl**, Boolean, `null`, Array von Zeichenketten. **Keine Gleitkommazahlen**, keine über die Definition hinausgehenden verschachtelten Objekte |
| Zahlenform | nur Ganzzahlen ohne führendes `+`, ohne führende Nullen, ohne Exponent, ohne Dezimalpunkt; keine `NaN`- oder `Infinity`-Literale |
| Booleans in Zahlenfeldern | **unzulässig.** Ein numerisches Pflichtfeld akzeptiert **keinen** Boolean. A prüft den Typ ausdrücklich |
| Pflichtfelder | je Nachrichtenart in Abschnitt 3 abschliessend aufgezählt |
| Optionale Felder | **keine.** Geschlossene Feldmenge je Art |
| Unbekannte Felder | **unzulässig.** Fortentwicklung erfolgt über `proto` |
| Doppelte Feldnamen | **unzulässig** auf jeder Ebene. A verwendet einen Parser, der Doppelungen **meldet** |
| Ungültige Kodierung | nicht dekodierbare Bytefolge oder Byte ausserhalb der Invariante ⇒ ungültig |

### 2.3 Aufteilung über Lese- und Schreibaufrufe

Eine Nachricht kann über beliebig viele Aufrufe verteilt oder mit anderen zusammen übertragen werden. **Die Rahmung erfolgt ausschliesslich über `0x0A`.**

- **E** schreibt nach der bereits beschriebenen Disziplin: Schleife bis zur vollständigen Übertragung, `EINTR`-Wiederholung, keine erneute Sendung bereits bestätigter Bytes.
- **A** puffert bis zum nächsten `0x0A`, verarbeitet genau eine Nachricht und behält **nur** den angefangenen Rest im Speicher.

### 2.4 Grössenbegrenzungen — vorab zu bindende Parameter

Es werden **keine Zahlenwerte vorgeschlagen**.

| Parameter | Bedeutung |
| --- | --- |
| `L1_TRACE_MAX_MESSAGE_BYTES` | Höchstlänge einer Nachricht **einschliesslich** `0x0A` |
| `L1_TRACE_MAX_RECORDS` | Höchstwert für n |
| `L1_TRACE_MAX_TOTAL_BYTES` | Höchstlänge des gesamten Stroms einschliesslich Siegel |

Überschreitung ist ein **Transportverstoss**; es gilt der **Fehlerpfad nach 5.3**.

### 2.5 Hashgrundlage — genau bestimmt

Sei **B_i** die **tatsächlich übertragene, vollständige Bytefolge** des Nutzdatensatzes mit Folgenummer *i*, **einschliesslich des abschliessenden `0x0A`**.

> **AGG = SHA256( B_1 ‖ B_2 ‖ … ‖ B_n )**
>
> Verkettung in **aufsteigender Folgenummer**, **ohne** zusätzliche Trennzeichen, **ohne** Längenpräfixe, **ohne** Auslassung des jeweiligen `0x0A`.

| Gegenstand | Festlegung |
| --- | --- |
| Was eingeht | die übertragenen Rohbytes jedes Nutzdatensatzes samt Zeilentrenner |
| Was **nicht** eingeht | die Bytes des **Siegels** |
| Keine Neuserialisierung | A hasht die **empfangenen** Bytes, **nicht** ein neu serialisiertes Objekt |
| Reihenfolge | Folgenummern müssen lückenlos 1…n sein; Sortierreihenfolge = Empfangsreihenfolge. **A prüft beides** |

**Das Siegel berechnet seinen eigenen Aggregathash nicht mit.**

### 2.6 Abgrenzung zum Hash der gespeicherten Spurdatei

| Grösse | Abgedeckter Byteumfang |
| --- | --- |
| AGG (im Siegel) | `B_1 ‖ … ‖ B_n` |
| SHA256 der gespeicherten Spurdatei | die Bytes, die **tatsächlich in der Datei stehen** |

> **AGG und der Spurdateihash decken unterschiedliche Byteumfänge ab und dürfen nicht gleichgesetzt werden.**
>
> Die Formel „Nutzdaten **plus** Siegel" beschreibt den **vollständigen gültigen Fall**. Sie gilt **nicht** für jeden Diagnosefall: bei abgebrochener oder unvollständiger Speicherung deckt der Dateihash nur die tatsächlich geschriebenen Bytes ab.

### 2.7 Wertebereiche und Beziehungen der Zahlenfelder

| Feld | Bereich und Beziehung |
| --- | --- |
| `seq` bei Nutzdatensätzen | Ganzzahl, `1 ≤ seq ≤ n`, lückenlos und aufsteigend, beginnend bei 1 |
| `seq` beim Siegel | Ganzzahl, **`seq = n + 1`**, wobei n die von A gezählte Anzahl der Nutzdatensätze ist |
| `seq` Obergrenze | `seq ≤ L1_TRACE_MAX_RECORDS + 1` |
| `count` | Ganzzahl, **`1 ≤ count ≤ L1_TRACE_MAX_RECORDS`**; Untergrenze 1 wegen der Headerpflicht nach 3.2; muss der eigenen Zählung von A gleichen |
| `attempt` | Ganzzahl, `attempt ≥ 1`, **je Modul lückenlos aufsteigend beginnend bei 1**, `attempt ≤ L1_TRACE_MAX_RECORDS` |

**Die numerischen Felder sind Pflichtfelder vom Typ Ganzzahl, jeweils nach Massgabe der Nachrichtenart, in der sie auftreten** (Abschnitt 3). Ein Boolean ist dort unzulässig (2.2).

### 2.8 Prüfung der Serialisierungsform durch A

| Schritt | Handlung |
| --- | --- |
| 1 | Empfangene Zeile ohne das abschliessende `0x0A` merken — das sind die **Originalbytes** |
| 2 | Zeile parsen; dabei doppelte Schlüssel melden, Typen und Wertebereiche prüfen |
| 3 | Das geparste Objekt **erneut serialisieren** mit sortierten Schlüsseln, `ensure_ascii` und Trennzeichen ohne Leerzeichen |
| 4 | Die Vergleichsserialisierung **byte-für-byte** gegen die Originalbytes prüfen. Abweichung ⇒ Formverstoss, Nachricht ungültig |

> **Die Vergleichsserialisierung dient ausschliesslich der Formprüfung. Die Hashbildung nach 2.5 erfolgt ausschliesslich über die empfangenen Originalbytes; die Vergleichsserialisierung ersetzt sie nicht.**

---

## 3. Nachrichtenarten

### 3.1 Gemeinsames Grundschema

| Feld | Typ | Bedeutung |
| --- | --- | --- |
| `seq` | Ganzzahl ≥ 1 | Folgenummer; **zählt Nachrichten**, nicht Ausführungsversuche |
| `kind` | Zeichenkette aus `{"header","run_binding","exec_record","seal"}` | Nachrichtenart |

### 3.2 `header` — Folgenummer 1, genau einmal, verpflichtend

| Feld | Typ | Bedeutung | Erzeuger | Wann bekannt | Was A unabhängig prüft | Trägt |
| --- | --- | --- | --- | --- | --- | --- |
| `seq` | Ganzzahl | muss **1** sein | E | Sendezeitpunkt | Wert 1; erste Nachricht | neue Gestaltungswahl |
| `kind` | Zeichenkette | `"header"` | E | Sendezeitpunkt | Wert und Position | neue Gestaltungswahl |
| `proto` | Zeichenkette | gebundene Protokollversion | E | vorab gebunden | Gleichheit mit dem in BIND-2 gebundenen Wert | neue Gestaltungswahl |
| `producer` | Zeichenkette | fester Kennstring des sendenden Bausteins | E | vorab gebunden | Gleichheit mit dem gebundenen Wert | neue Gestaltungswahl |

**Mindestumfang:** da der Header ein Nutzdatensatz ist, hat eine gültige Spur dieses Protokolls **n ≥ 1** (siehe 4.6).

### 3.3 `run_binding` — höchstens einmal, nicht zwingend an zweiter Stelle

| Feld | Typ | Bedeutung | Erzeuger | Wann bekannt | Was A unabhängig prüft | Trägt |
| --- | --- | --- | --- | --- | --- | --- |
| `seq` | Ganzzahl ≥ 2 | Folgenummer | E | Sendezeitpunkt | Lückenlosigkeit | B-2 |
| `kind` | Zeichenkette | `"run_binding"` | E | Sendezeitpunkt | Wert; **höchstens einer** | neue Gestaltungswahl |
| `run_id` | Zeichenkette | **ein einzelner Pfadbestandteil** | `run_context` in E | unmittelbar nach erfolgreicher exklusiver Anlage | Namensform, danach die dateisystemseitigen Prüfungen des Laufzuordnungsentwurfs | bestehende Vorgabe + neue Gestaltungswahl |

**Ereignisse vor Vorliegen einer `run_id` gehen nicht verloren** — sie sind reguläre Nutzdatensätze mit kleinerer Folgenummer. Bei fehlender oder ungültiger Zuordnung gelten die **Veröffentlichungssperren** unverändert.

### 3.4 `exec_record` — berichtetes Ausführungsereignis

**Verbindliche Vorbemerkung:** die Felder sind **Transportfelder**. Ihre Existenz ist **kein Nachweis**, dass das Ereignis zuverlässig erfasst werden kann.

| Feld | Typ | Bedeutung | Erzeuger | Wann bekannt | Was A unabhängig prüft | Trägt |
| --- | --- | --- | --- | --- | --- | --- |
| `seq` | Ganzzahl ≥ 2 | **Nachrichten**-Folgenummer | E | Sendezeitpunkt | Lückenlosigkeit | B-2 |
| `kind` | Zeichenkette | `"exec_record"` | E | Sendezeitpunkt | Wert | neue Gestaltungswahl |
| `module` | Zeichenkette | Modulname | Loader in E | vor dem Aufruf | Form; Zugehörigkeit zu **Z** | neue Gestaltungswahl; Erfassung offen |
| `attempt` | Ganzzahl ≥ 1 | Versuchsnummer je Modul; mit `module` identifiziert sie **einen Ausführungsversuch** | Loader | vor dem Aufruf | je Modul lückenlos ab 1; Paarbildung nach 3.4.1 | neue Gestaltungswahl |
| `phase` | Zeichenkette aus `{"start","normal_return","exception"}` | `start` = Aufrufversuch; `normal_return` und `exception` = **zwei verschiedene Ausgänge desselben Aufrufs** | Loader | `start` vor, Ausgang nach dem Aufruf | Paarregeln nach 3.4.1 | neue Gestaltungswahl |
| `source_path` | Zeichenkette | Quellpfad wie an den Übersetzer übergeben | Loader | vor dem Aufruf | Übereinstimmung mit der gebundenen Quellenmenge | neue Gestaltungswahl; Erfassung offen |
| `source_sha256` | Zeichenkette, 64 Hexziffern klein | SHA256 der gelesenen Quellbytes; Darstellung und Ableitung festgelegt | Loader | vor dem Aufruf | Gleichheit mit dem gebundenen `file_sha256` | bestehendes §10-Feld als Sollwert |
| `code_digest` | Zeichenkette, 64 Hexziffern klein | Digest des erzeugten Codeobjekts; Darstellung festgelegt, **Ableitungsvorschrift noch zu binden** | Loader | vor dem Aufruf | Gleichheit mit dem in BIND-2 gebundenen Sollwert | neue Gestaltungswahl; Ableitung offen |
| `params_digest` | Zeichenkette, 64 Hexziffern klein | Digest der Übersetzungsparameter; Darstellung festgelegt, **Ableitungsvorschrift noch zu binden** | Loader | vor dem Aufruf | Gleichheit mit dem gebundenen Parametersatz | neue Gestaltungswahl; Ableitung offen |
| `cache_state` | Zeichenkette aus `{"absent","present_unused","present_used","unknown"}` | Cachezustand beziehungsweise Cachebefund | Loader | vor dem Aufruf | Verträglichkeit mit der angenommenen E2-Regel | E2 bestehend; Wertemenge neu |

**`phase="start"` bezeichnet den Aufrufversuch, nicht einen nachgewiesenen Beginn des Modulrumpfs.**

#### 3.4.1 Paarregeln eines Ausführungsversuchs

| Regel | Festlegung |
| --- | --- |
| Identifikation | Ein Ausführungsversuch wird durch das Paar **`(module, attempt)`** identifiziert, nicht durch `seq` |
| Zwei Nachrichten je Versuch | `start` und der zugehörige Ausgang verwenden **denselben** `attempt` und denselben `module` |
| Nummerierung | `attempt` ist je Modul **lückenlos aufsteigend ab 1** |
| Übereinstimmende Identitätsfelder | `module`, `attempt`, `source_path`, `source_sha256`, `code_digest`, `params_digest`, `cache_state` müssen im Paar **identisch** sein. Abweichend sind ausschliesslich `seq` und `phase` |
| Ungültig | Ausgang ohne vorausgehenden `start` mit gleichem Paar; **zwei `start`** für dasselbe Paar; **mehr als ein Ausgang**; Abweichung eines Identitätsfelds |
| Reihenfolge | Der `start` eines Paares muss eine kleinere `seq` haben als sein Ausgang |

### 3.5 `seal` — Folgenummer n+1, genau einmal, letzte Nachricht

| Feld | Typ | Bedeutung | Erzeuger | Wann bekannt | Was A unabhängig prüft | Trägt |
| --- | --- | --- | --- | --- | --- | --- |
| `seq` | Ganzzahl | muss **n+1** sein | E | Siegelzeitpunkt | Gleichheit mit der eigenen Zählung + 1 | B-3 |
| `kind` | Zeichenkette | `"seal"` | E | Siegelzeitpunkt | Wert; **genau ein** Siegel | B-3 |
| `count` | Ganzzahl ≥ 1 | deklariertes **n** | E | Siegelzeitpunkt | Gleichheit mit der eigenen Zählung | B-4 |
| `agg_sha256` | Zeichenkette, 64 Hexziffern klein | **AGG** nach 2.5 | E | Siegelzeitpunkt | **unabhängige Nachberechnung** | B-4, B-5 |

### 3.6 Kein zusätzliches Fehlertelegramm

**Nicht vorgeschlagen.** A benötigt für die Abschlussentscheidung den **Beendigungsstatus** von E und den **Artefaktbestand**; beides liegt A ohnehin vor. Die Ursache eines technischen Fehlers ist durch die vertraglich vorgesehene Fehlerdatei und die gebundene Standardfehlerausgabe abgedeckt. **Diagnoseausgaben und tatsächlicher Prozessstatus bleiben vom Protokoll getrennt.**

---

## 4. Folgenummern, Versuche, Mengen, Siegel

### 4.1 Was zu den Nutzdatensätzen zählt

> **Nutzdatensätze 1…n sind sämtliche Nachrichten ausser dem Siegel** — einschliesslich `header` und `run_binding`.

Ausserhalb steht ausschliesslich das Siegel, aus dem strukturellen Grund, dass es seinen eigenen Hash nicht enthalten kann.

### 4.2 Vier Ebenen, streng getrennt

| Ebene | Definition | Bemerkung |
| --- | --- | --- |
| Nachrichten | alle Datensätze 1…n, gezählt über `seq` | Transportebene |
| V — Liste berichteter Versuche | alle Paare `(module, attempt)` aus `exec_record`-Datensätzen, **einschliesslich Wiederholungen und beider Ausgangsarten** | **vollständig; es wird kein Versuch entfernt** |
| Versuchszustand | je Versuch einer aus `{inkonsistent, ungeklärt, nachgewiesen_ausgeführt}` nach 4.4 | Bewertungsebene |
| O — für E1 verwertbare Menge | Menge der **Modulidentitäten** der Versuche im Zustand `nachgewiesen_ausgeführt` | Ausführungsebene; **heute nicht ableitbar** |

**`header` und `run_binding` sind keine Ausführungsereignisse** und tragen weder zu V noch zu O bei.

### 4.3 Wiederholungen und Vergleichbarkeit

- **V bleibt vollständig erhalten**: jeder Versuch hat ein eigenes `attempt` und ein eigenes Nachrichtenpaar. **Kein Versuch wird aus der Spur oder aus V entfernt.**
- **O ist eine Menge vergleichbarer Modulidentitäten**, damit die Vergleiche **R ⊆ O ⊆ Z** gebildet werden können.
- Die Bildung von O aus V **verdichtet** Versuche desselben Moduls zu einer Modulidentität. **Sie löscht nichts**: V und die Einzelversuche bleiben daneben vollständig erhalten und prüfbar.

### 4.4 Versuchszustände und Ableitung von O

| Gruppe | Bedingung | Folge bei Verletzung |
| --- | --- | --- |
| K — Konsistenz | (K1) genau ein `start` und genau ein Ausgang mit gleichem `(module, attempt)`; (K2) sämtliche Identitätsfelder nach 3.4.1 stimmen im Paar überein; (K3) die gesamte Spur ist transportkonsistent, gesiegelt und bis zum tatsächlichen EOF ohne Nachtrag | Zustand **`inkonsistent`** |
| D — Digestbindung | (D1) `source_sha256` stimmt mit dem gebundenen Quellhash überein; (D2) `code_digest` stimmt mit dem in BIND-2 gebundenen Sollwert überein; (D3) `params_digest` stimmt mit dem gebundenen Parametersatz überein | Zustand **`ungeklärt`** |
| F — Erfassungsnachweis | **(F1) Für diesen konkreten Versuch liegt ein geeigneter, nachgewiesener Erfassungsmechanismus vor, der die tatsächliche Ausführung des zugeordneten Modulcodes positiv nachweist. Die blosse Verfügbarkeit des Mechanismus oder ein negatives beziehungsweise unbestimmtes Ergebnis erfüllt F1 nicht.** | Zustand **`ungeklärt`** |

**Bedingung D — ohne Ausweichmöglichkeit.** Ist die Ableitungsvorschrift für `code_digest` oder `params_digest` **nicht gebunden** oder aus anderem Grund **nicht prüfbar**, so ist der jeweilige Vergleich **nicht erfüllt**. **Eine fehlende Bindung oder fehlende Prüfbarkeit bedeutet „Nachweis nicht erfüllt"; sie erlaubt nicht, den Vergleich auszulassen.**

**Zustandszuweisung:** `nachgewiesen_ausgeführt` **nur**, wenn K, D **und** F erfüllt sind. Andernfalls `inkonsistent` (bei Verletzung von K) beziehungsweise `ungeklärt`.

**Gegenwärtige Lage, ausdrücklich:** Bedingung **F1 ist nicht erfüllt** — ein geeigneter Erfassungsmechanismus ist nicht nachgewiesen. Die Erfassung bleibt eine **offene Voraussetzung innerhalb des definierten D1-Erfassungsumfangs**; das Protokoll behauptet **keine** bereits vorhandene Fähigkeit. Daraus folgt:

> **O ist gegenwärtig nicht ableitbar. A darf keinen erfüllten E1-Nachweis ableiten.** Nachrichtenpaar, passende Digestwerte und gültiges Siegel **allein** ergeben **keinen** Nachweis tatsächlicher Ausführung.

**Umgang mit ungeklärten Versuchen:**

> Ungeklärte Versuche bleiben vollständig in V erhalten. Die Mengenbedingung R ⊆ O prüft, ob jede erforderliche Modulidentität durch mindestens eine nachgewiesene Ausführung vertreten ist. Sie beweist nicht, dass sämtliche einzelnen Ausführungsversuche dieses Moduls geklärt sind. Ein nachgewiesener Versuch darf einen weiteren ungeklärten Versuch desselben Moduls nicht verdecken. Solange ein für den definierten Erfassungsumfang relevanter Versuch ungeklärt bleibt, darf kein vollständiger E1-Nachweis behauptet werden. Dies gilt auch für relevante Versuche von Modulen ausserhalb von R. Die Zulässigkeitsprüfung gegenüber Z bleibt zusätzlich erforderlich.

### 4.5 Ausgangsarten und ihre Beweiskraft

| Ausgang | Bedeutung | Was er **nicht** beweist |
| --- | --- | --- |
| `normal_return` | Der Aufruf kehrte regulär zurück | nicht für sich allein, dass der Modulrumpf vollständig oder überhaupt ausgeführt wurde |
| `exception` | Der Aufruf endete mit einer Ausnahme | **weder**, dass kein Modulcode ausgeführt wurde, **noch** für sich allein, dass Modulcode ausgeführt wurde. Modulcode kann bereits gelaufen sein, bevor die Ausnahme entstand |

**Der Ausgang steuert die Zugehörigkeit zu O nicht.** Über sie entscheiden allein K, D und F. **Tatsächlich nachgewiesene Ausführungen bleiben unabhängig von ihrem Ausgang im Erfassungsumfang.**

**Kein pauschaler Gesamtfehler:** ein `exception`-Ausgang bedeutet **nicht** automatisch einen wirtschaftlichen oder technischen Gesamtfehler des Laufs.

**Fehlender Ausgang:** ein `start` ohne Ausgang in einer gesiegelten Spur verletzt **K1**; der Versuch erhält `inkonsistent` und bleibt in V erhalten.

### 4.6 Abgrenzung der n-Aussagen

| Aussage | Geltungsbereich |
| --- | --- |
| B-9: „n = 0 ist für sich kein E1-Nachweis" | **allgemeine E3-Aussage** zum leeren Nutzdatenstrom. Unverändert gültig |
| Zusätzlich in diesem Protokollvorschlag: Headerpflicht | **n ≥ 1.** Ein Siegel mit `count = 0` ist in diesem Protokoll **ungültig** |

Die Headerpflicht ist eine **zusätzliche Protokollbeschränkung**, keine Änderung der E3-Grundlage. **Auch ein gültiger Header ohne jedes Ausführungsereignis — n = 1 — beweist E1 nicht.**

### 4.7 Wann E das Siegel senden darf

E sendet das Siegel als **letzte Protokollhandlung**, nachdem die letzte Handlung innerhalb des **definierten Erfassungsumfangs** abgeschlossen ist und bevor eine weitere Handlung erfolgt, die ein Ereignis innerhalb dieses Umfangs erzeugen könnte.

**Grenze:** beim Herunterfahren des Interpreters können weitere Ausführungen stattfinden. Ob sie zum Erfassungsumfang gehören, ist **eine offene Entscheidung**.

> **Weder das Siegel noch ein erfolgreicher Exitcode beweisen für sich, dass danach keine relevanten Ereignisse mehr stattgefunden haben.**

Der Siegelzeitpunkt ist eine **erklärte Umfangsgrenze**, kein Nachweis, und **darf nicht als stillschweigende Verengung des D1-Erfassungsumfangs verwendet werden**.

---

## 5. Sender- und Empfängerablauf

### 5.1 Senderablauf E

| Schritt | Handlung |
| --- | --- |
| 1 | Header als Datensatz 1 senden |
| 2 | Laufend `exec_record`-Paare mit fortlaufender Nachrichten-Folgenummer senden |
| 3 | Nach erfolgreicher exklusiver Anlage des Laufverzeichnisses **einmal** `run_binding` senden |
| 4 | Am Siegelzeitpunkt nach 4.7 das Siegel senden |
| 5 | Danach **nichts mehr** auf den Kanal schreiben |

### 5.2 Regulärer Empfangsablauf A

| Zustand | Übergang |
| --- | --- |
| `INIT` | Kanal eingerichtet, E gestartet |
| `EMPFANGEND` | Datensätze werden gerahmt, nach 2.8 geprüft, gezählt, in die laufende Hashbildung aufgenommen und in die Spurdatei geschrieben |
| `SIEGEL_GESEHEN` | gültiges Siegel empfangen; weitere Bytes sind ab hier ein Verstoss. **Dieser Zustand bestätigt für sich noch keine vollständige gültige Spur** |
| `EOF_ERREICHT` | **tatsächliches EOF** festgestellt; Leseende aus der Bereitschaftsabfrage entfernt und geschlossen |
| `STATUS_BEKANNT` | Beendigungsstatus von E **ausschliesslich über das `Popen`-Objekt** festgestellt |
| `BEWERTUNG` | Transportbefund, Laufzuordnung, Artefakt-, Integritäts- und Gate-Prüfungen, abschliessender Verzeichnisvergleich |
| `ENTSCHIEDEN` | Abschluss nach den bestehenden E3-Regeln |

`EOF_ERREICHT` und `STATUS_BEKANNT` sind **unabhängig** (**B-7**). Die Bewertung beginnt erst, wenn **beide** vorliegen.

### 5.3 Fehlerpfad FP — Grössenüberschreitung, Lesefehler, Schreibfehler der Spurdatei

| Nr. | Festlegung |
| --- | --- |
| FP-1 | A setzt den Zustand **`TRANSPORTVERSTOSS`**. Unumkehrbar; ein positiver Abschluss kann danach **nicht** mehr entstehen |
| FP-2 | **Verwerfmodus:** solange das Lesen möglich ist, liest A weiter und **verwirft** die Bytes — ohne Rahmung, Prüfung, Hashbildung, Speicherung. Zweck: E soll nicht an einem vollen Kanal blockieren |
| FP-3 | **Auch im Verwerfmodus bleiben Bereitschaftsbehandlung und Prozessbeobachtung aktiv.** A kehrt nach jedem Lesevorgang in die Bereitschaftsabfrage zurück |
| FP-4 | **`EAGAIN` beziehungsweise `EWOULDBLOCK` sind kein EOF** und führen **nicht** zu einer beschäftigten Warteschleife: A wartet erneut auf Bereitschaft |
| FP-5 | Bei **tatsächlich beobachtetem EOF** wird das Leseende **aus der Bereitschaftsabfrage entfernt und geschlossen** |
| FP-6 | Bei **endgültigem Lesefehler** schliesst A das Leseende selbst. **Ein selbst geschlossenes Leseende ist kein beobachtetes EOF.** Welche Folge das Schliessen für E hat, hängt von den **Deskriptor- und Signalbedingungen** ab; hält ein weiteres Leseende den Kanal offen, folgt daraus **keine** bestimmte Wirkung für E. Es wird keine Wirkung unterstellt |
| FP-7 | A beobachtet den Kindprozess **ausschliesslich über das `Popen`-Objekt**; kein zweiter Abholweg |
| FP-8 | **Im Verwerfmodus wird kein späterer `run_binding`-Datensatz mehr ausgewertet.** Eine fehlende oder nicht mehr hinreichend abgesicherte Laufzuordnung **darf nicht nachträglich als vorhanden angenommen werden** |
| FP-9 | **Keine Timeout-, Signal-, Wiederholungs- oder garantierte Beendigungsstrategie** |

**Abschlussentscheidung nach FP:**

| Voraussetzung | Festlegung |
| --- | --- |
| Positiver Abschluss | **ausgeschlossen** |
| `TECHNICAL_ERROR`-Abschluss | erst **nach festgestelltem Prozessende** und **nach den übrigen erforderlichen Prüfungen**. **Die Ausnahme vom EOF-Erfordernis ersetzt die Feststellung des Prozessendes nicht** |
| Andernfalls | **unvollständiger Aufruf ohne `completion.json`** |

---

## 6. Fehlerfälle

| Fall | Transportbefund | Kanal- und Prozessbehandlung | Auswirkung auf Laufzuordnung und Versuchszustände | Abschluss nach E3 |
| --- | --- | --- | --- | --- |
| Kein Siegel bis EOF | Spur unvollständig | regulär: EOF beobachtet, Leseende geschlossen | K3 verletzt: alle Versuche `inkonsistent`; Zuordnung nur bei vollständig gespeichertem `run_binding` | kein positiver Abschluss; `TECHNICAL_ERROR` nur bei zugeordneter Ablage **und** Fehlerartefakten, sonst unvollständig |
| Mehr als ein Siegel | Verstoss gegen B-3 | FP | K3 verletzt | wie vor |
| Siegel zu früh | Verstoss | FP | K3 verletzt | wie vor |
| Lücke, Wiederholung oder Rücksprung der Folgenummern | Verstoss gegen B-2 | FP | K3 verletzt | wie vor |
| `count` ≠ eigene Zählung | Verstoss gegen B-4/B-5 | regulär bis EOF | K3 verletzt | wie vor |
| `agg_sha256` ≠ Nachberechnung | Verstoss gegen B-4/B-5 | regulär bis EOF | K3 verletzt | wie vor |
| `count = 0` | in diesem Protokoll ungültig | FP | K3 verletzt | wie vor |
| Unvollständige Nachricht bei EOF | Verstoss | EOF beobachtet | K3 verletzt | wie vor |
| Bytes oder Nachrichten nach dem Siegel | Verstoss gegen B-6 | FP | K3 verletzt | wie vor |
| `run_binding` mehrfach | Verstoss | FP | **Zuordnung ungültig** | keine `completion.json` in einem unzugeordneten Verzeichnis |
| `run_id` unzulässig geformt | Nachricht ungültig | FP | Zuordnung ungültig | wie vor |
| `proto` oder `producer` abweichend | Header ungültig | FP | gesamte Spur nicht verwertbar | kein positiver Abschluss |
| Unbekannte `kind`, unbekanntes Feld, doppelter Schlüssel, Boolean in Zahlenfeld, Gleitkommazahl, ungültige Zahlenform, Wertebereichsverletzung, Formverstoss, Byte ausserhalb der Invariante | Nachricht ungültig | FP | K3 verletzt | kein positiver Abschluss |
| Paarverstoss nach 3.4.1 | Nachrichten inkonsistent | regulär bis EOF | betroffener Versuch `inkonsistent`; bleibt in V | kein positiver Abschluss |
| `start` ohne Ausgang in gesiegelter Spur | Inkonsistenz | regulär | Versuch `inkonsistent`; bleibt in V | kein positiver Abschluss |
| Ausgang `exception` | **kein** Transportbefund | regulär | Versuch bleibt in V; Zustand folgt **allein** aus K, D und F. **Kein automatischer Gesamtfehler** | Bewertung nach den übrigen Prüfungen |
| Digestvergleich nicht bindbar oder nicht prüfbar | kein Transportbefund | regulär | Versuch **`ungeklärt`**; bleibt vollständig in V. **Ein anderer, nachgewiesener Versuch desselben Moduls verdeckt ihn nicht.** Solange er für den definierten Erfassungsumfang relevant ist, darf **kein vollständiger E1-Nachweis** behauptet werden | kein erfüllter E1-Nachweis |
| Kein positiver Erfassungsnachweis (F1) | kein Transportbefund | regulär | **alle** Versuche höchstens `ungeklärt`; **O nicht ableitbar** | kein erfüllter E1-Nachweis |
| Grössenüberschreitung | Verstoss | FP-1 bis FP-9 | K3 verletzt; **kein späteres `run_binding`** | kein positiver Abschluss |
| Lesefehler ausser `EAGAIN`/`EWOULDBLOCK`/`EINTR` | Verstoss | FP-1, FP-3, FP-6 bis FP-9; kein beobachtetes EOF | K3 verletzt; **kein späteres `run_binding`** | kein positiver Abschluss |
| Schreibfehler auf der Spurdatei | geprüfte Spur nicht ablegbar | FP-1 bis FP-9 | K3 verletzt; **kein späteres `run_binding`** | kein positiver Abschluss |
| Prozessende vor Verarbeitung bereits gepufferter Nachrichten | **kein Befund** | A liest und prüft weiter bis zum tatsächlichen EOF | — | **Entscheidung vertagt** |
| Regulärer Nichterfolgsstatus von E | Transport kann fehlerfrei sein | regulär | Versuchszustände unberührt | kein positiver Abschluss |
| Signalbeendigung von E | Transport kann fehlerfrei sein | regulär | Versuchszustände unberührt | kein positiver Abschluss |

**Kein Fehler wird automatisch einem `TECHNICAL_ERROR`-Abschluss gleichgesetzt.** Ohne zuverlässig zugeordnete Ablage oder ohne die vorgeschriebenen Fehlerartefakte bleibt der Aufruf **unvollständig ohne `completion.json`**. **Ein technischer Fehlerstatus ist kein bestandener wirtschaftlicher Lauf.** A berechnet keine fachlichen Kennzahlen neu.

---

## 7. Verhältnis zur gespeicherten Ereignisspur

### 7.1 Zwei getrennte Eigenschaften

| Eigenschaft | Wert | Bedeutung |
| --- | --- | --- |
| `storage_extent` | `all_received` | **alle** empfangenen Bytes wurden in die Datei geschrieben |
| `storage_extent` | `partial` | ein Teil der empfangenen Bytes wurde **nicht** geschrieben |
| `validation` | `valid` | Rahmung, Form, Schema, Folgenummern, Anzahl **und** AGG bestanden, **und** das tatsächliche EOF wurde beobachtet, **ohne** Bytes nach dem Siegel |
| `validation` | `invalid` | mindestens eine dieser Prüfungen ist fehlgeschlagen |
| `validation` | `undetermined` | die Prüfungen konnten nicht abgeschlossen werden |

**Beide Eigenschaften sind unabhängig.** Eine vollständig gespeicherte, aber ungültige Datei ist `all_received` mit `invalid` und darf **nicht** als blosses Präfix bezeichnet werden. **Ein geprüftes Siegel vor dem EOF genügt nicht** zur Bestätigung einer vollständigen gültigen Spur.

### 7.2 Drei Grössen, getrennt

| Grösse | Definition |
| --- | --- |
| Übertragener Strom | die Bytes, die über den Kanal ankamen |
| Geprüfte Spur | der Strom, nachdem sämtliche Prüfungen bestanden wurden — also nur bei `validation=valid` |
| Gespeicherte Spurdatei | die abgelegte Datei. **Bytezahl und SHA256 beziehen sich immer auf die tatsächlich gespeicherte Datei** |

### 7.3 Ablage und Ressourcenbegrenzung

| Frage | Festlegung |
| --- | --- |
| Was speichert A | die **empfangenen Bytes unverändert**, byte-für-byte. Keine Neuserialisierung, Normalisierung oder Umsortierung |
| Erzeuger | **A** |
| Ablage | das gebundene **Diagnoseverzeichnis**; die Datei wird **vor** dem Start von E geöffnet |
| Verhalten vor Laufzuordnung | die Datei ist bereits offen; alle Datensätze vor `run_binding` werden regulär geschrieben |
| Kein Verschieben | die Spur bleibt im Diagnoseverzeichnis |
| Pufferung | **keine unbeschränkte Pufferung**; im Speicher bleibt nur die angefangene Nachricht |

| Ereignis | Folge |
| --- | --- |
| `MAX_MESSAGE_BYTES` überschritten, bevor ein `0x0A` eintrifft | Transportverstoss, FP |
| `MAX_RECORDS` oder `MAX_TOTAL_BYTES` überschritten | Transportverstoss, FP |
| Speicherplatz erschöpft oder sonstiger Schreibfehler | FP; `storage_extent=partial` |

**Es wird keine Laufzeit- oder Beendigungsgarantie eingeführt.** Die Grössengrenzen begrenzen definierte Grössen; **eine Garantie gegen jede Endlosschleife oder jede Ressourcenerschöpfung wird nicht behauptet**, und die technische Wirksamkeit der beschriebenen Massnahmen ist **nicht durch Tests nachgewiesen**.

### 7.4 Bereits empfangene, aber nicht mehr gespeicherte Bytes

| Lage | Behandlung |
| --- | --- |
| Vor dem Fehler geschrieben | verbleiben in der Datei |
| Empfangen, aber nicht mehr geschrieben | **werden verworfen**; kein nachträglicher Ablageversuch. `storage_extent=partial` |
| Im Verwerfmodus gelesen | **werden nicht gespeichert**, gehen in keine Prüfung ein. `storage_extent=partial` |

**In keinem dieser Fälle entsteht eine geprüfte Spur, und in keinem entsteht ein positiver Abschluss.**

### 7.5 Verbindung zum Abschlussnachweis — neu, ausdrücklich nicht bestehend

Die angenommene Artefaktliste führt **relative Pfade ohne `..`** und muss dem Verzeichnisinhalt des Laufverzeichnisses entsprechen. Eine Datei ausserhalb ist darin **nicht** unterbringbar. **Eine bestehende Zulässigkeit einer externen Referenz wird nicht behauptet.** **Die Spur bleibt nach diesem Entwurf unter der gebundenen Diagnosewurzel; diese Ablageregel bleibt unverändert.**

| Teilfeld | Typ | Inhalt | Status |
| --- | --- | --- | --- |
| `trace_reference.location_id` | Zeichenkette | Bezeichner relativ zur gebundenen Diagnosewurzel, ohne `..`, ohne absoluten Pfad | vorab gebundene Ablageregel; Wert zur Laufzeit |
| `trace_reference.bytes` | Ganzzahl ≥ 0 | **tatsächliche** Bytezahl der gespeicherten Datei | Laufzeitwert |
| `trace_reference.sha256` | Zeichenkette, 64 Hexziffern | SHA256 der **gespeicherten Datei** — nicht AGG | Laufzeitwert |
| `trace_reference.storage_extent` | Zeichenkette aus `{"all_received","partial"}` | Speicherumfang nach 7.1 | Laufzeitwert |
| `trace_reference.validation` | Zeichenkette aus `{"valid","invalid","undetermined"}` | Validierungsbefund nach 7.1 | Laufzeitwert |
| `trace_reference.run_binding_stored` | Boolean | ob der `run_binding`-Datensatz **vollständig gespeichert** wurde | Laufzeitwert |
| `trace_reference.run_id` | Zeichenkette oder `null` | die `run_id`, **nur** wenn `run_binding_stored` wahr **und** die Zuordnung dateisystemseitig geprüft ist | Laufzeitwert |

#### 7.5.1 Referenzregel

| Abschlussart | Referenz zulässig? | Bedingung |
| --- | --- | --- |
| `COMPLETED_PASS` / `COMPLETED_FAIL` | ja, und nur dann | `storage_extent="all_received"` **und** `validation="valid"` **und** `run_binding_stored` wahr **und** dateisystemseitig geprüfte Laufzuordnung |
| `TECHNICAL_ERROR` | ja, auch bei unvollständiger oder ungültiger Diagnosespur, sofern der Abschluss nach den E3-Regeln zulässig ist | `storage_extent` und `validation` werden **wahrheitsgemäss** eingetragen; die Referenz ist eine **Diagnoseangabe** |
| Unvollständiger Aufruf ohne `completion.json` | entfällt | es entsteht kein Abschlussnachweis |

> **Ein Verweis auf eine unvollständige oder ungültige Diagnosespur ist kein positiver Ausführungsnachweis.**

#### 7.5.2 Zuordnung der Spur zum Lauf

Die Aussage „die Spur enthält `run_binding`" gilt **nur**, wenn dieser Datensatz **tatsächlich vollständig gespeichert** wurde. **Bei Fehlern zwischen Empfang und Speicherung darf seine Anwesenheit nicht unterstellt werden.** Die Übereinstimmung der `run_id` ist eine **festgehaltene Übereinstimmung, kein unabhängiger Nachweis**. **Ohne zuverlässig belegte Laufzuordnung bleibt `completion.json` gesperrt.**

---

## 8. Synthetische Beispiele

**Rein synthetisch, keine Testnachweise.** Keine berechneten Hashwerte.

```
{"kind":"header","proto":"<PLATZHALTER_PROTO_VERSION>","producer":"<PLATZHALTER_PRODUCER_ID>","seq":1}
{"attempt":1,"cache_state":"unknown","code_digest":"<PLATZHALTER_HEX64>","kind":"exec_record","module":"<PLATZHALTER_MODUL_A>","params_digest":"<PLATZHALTER_HEX64>","phase":"start","seq":2,"source_path":"<PLATZHALTER_PFAD_A>","source_sha256":"<PLATZHALTER_HEX64>"}
{"attempt":1,"cache_state":"unknown","code_digest":"<PLATZHALTER_HEX64>","kind":"exec_record","module":"<PLATZHALTER_MODUL_A>","params_digest":"<PLATZHALTER_HEX64>","phase":"normal_return","seq":3,"source_path":"<PLATZHALTER_PFAD_A>","source_sha256":"<PLATZHALTER_HEX64>"}
{"kind":"run_binding","run_id":"<PLATZHALTER_RUN_ID>","seq":4}
{"attempt":2,"cache_state":"unknown","code_digest":"<PLATZHALTER_HEX64>","kind":"exec_record","module":"<PLATZHALTER_MODUL_A>","params_digest":"<PLATZHALTER_HEX64>","phase":"start","seq":5,"source_path":"<PLATZHALTER_PFAD_A>","source_sha256":"<PLATZHALTER_HEX64>"}
{"attempt":2,"cache_state":"unknown","code_digest":"<PLATZHALTER_HEX64>","kind":"exec_record","module":"<PLATZHALTER_MODUL_A>","params_digest":"<PLATZHALTER_HEX64>","phase":"exception","seq":6,"source_path":"<PLATZHALTER_PFAD_A>","source_sha256":"<PLATZHALTER_HEX64>"}
{"agg_sha256":"<PLATZHALTER_HEX64>","count":6,"kind":"seal","seq":7}
```

| Beobachtung | Auslegung |
| --- | --- |
| Schlüssel sortiert, keine Leerzeichen | Formvorgabe nach 2.2 und 2.8 |
| `run_binding` an vierter Stelle | die Zuordnungsnachricht ist **nicht** die erste; frühere Ereignisse bleiben erhalten |
| Sechs Nachrichten bilden **zwei** Versuche | **`seq` zählt Nachrichten, nicht Versuche** |
| Versuch `(MODUL_A, 1)` endet `normal_return` | K1/K2 erfüllt; Zustand hängt zusätzlich von **D** und **F** ab |
| Versuch `(MODUL_A, 2)` endet `exception` | K1/K2 ebenfalls erfüllt; der Ausgang schliesst den Versuch **nicht** aus O aus |
| Angenommen, Versuch 1 wäre nachgewiesen, Versuch 2 bliebe ungeklärt | Die Modulidentität von `MODUL_A` wäre dann in O vertreten, und `R ⊆ O` könnte für dieses Modul erfüllt sein. **Das beweist nicht, dass sämtliche Einzelversuche dieses Moduls geklärt sind.** Versuch 2 bleibt ungeklärt und wird durch Versuch 1 **nicht verdeckt**; solange er für den definierten Erfassungsumfang relevant ist, darf **kein vollständiger E1-Nachweis** behauptet werden |
| Beide Versuche bleiben in **V** | **Keiner wird entfernt.** Solange **F1** nicht positiv erfüllt ist, sind beide höchstens `ungeklärt` und **O ist nicht ableitbar** |
| Siegel mit `count` 6, `seq` 7 | AGG umfasst die sechs ersten Zeilen einschliesslich Zeilentrenner, **nicht** die Siegelzeile |

---

## 9. Erforderliche Vertragsanpassungen

| Gegenstand | Bestehende Grundlage | Erforderliche Anpassung |
| --- | --- | --- |
| Ereignisspur als Artefakt | Abschnitt 2: „Keine weiteren Module und keine weiteren Artefakte" | Aufnahme der Spur und ihrer Ablage — bereits als E3-Vertragsänderung benannt |
| Spurdatei im Diagnoseverzeichnis | keine | neue Gestaltungswahl; Einordnung offen |
| `trace_reference` in `completion.json` | Abschnitt 7.6 führt eine geschlossene Feldmenge | **Schemaergänzung**, neu; keine Aufnahme in die Artefaktliste; einschliesslich Referenzregel 7.5.1 |
| Artefaktliste und Prüfung des fertigen Laufs | gelistete Menge = Verzeichnisinhalt ohne `completion.json` | **unverändert**, da `trace_reference` kein Listeneintrag ist; Vereinbarkeit ausdrücklich zu bestätigen |
| Diagnosewurzel und Namensregel | keine | vorab zu bindende Ablageregeln |
| Protokollversion, Feldmengen, Wertemengen, Wertebereiche | keine | Schemaergänzung, in BIND-2 zu binden |
| Die drei Grössenparameter | keine | vorab zu binden, **keine Werte vorgeschlagen** |
| Ableitungsvorschriften für `code_digest` und `params_digest` | keine | in BIND-2 zu binden. Solange sie fehlen, ist Bedingung D **nicht erfüllt** |
| Erfassungsmechanismus (F1) | keine | **offen**; ohne positiven Nachweis ist O nicht ableitbar |
| Erfassungsumfang und Siegelzeitpunkt | keine | **offene Entscheidung** |
| Serialisierungskonvention | Abschnitt 7.1 und Abschnitt 10 | **keine** — unverändert übernommen |
| `run_id`, exklusive Anlage, Fresh-State | Abschnitt 7, BIND-3 | **keine** |
| E3-Abschlussregeln, wirtschaftliche Regeln | angenommen | **keine** |

**Keine pauschale BIND-1b-Zuordnung. Keine B3/B5-Kopplung. Keine Rückkehr zur verworfenen Audit-Stapelkorrelation** — die Zuordnung von Ereignis zu Aufruf erfolgt über `(module, attempt)`, nicht durch zeitliche Korrelation.

---

## 10. Offene Entscheidungen

| Nr. | Entscheidung |
| --- | --- |
| E-a | Erfassungsumfang beim Herunterfahren und daraus folgender Siegelzeitpunkt |
| E-b | Ableitungsvorschriften für `code_digest` und `params_digest` |
| E-c | Werte der drei Grössenparameter |
| E-d | Gebundene Werte für `proto` und `producer` |
| E-e | Diagnosewurzel, Namensregel, Aufnahme von `trace_reference`, Referenzregel 7.5.1 |
| E-f | Einordnung von Spur und Spurdatei gegenüber „Keine weiteren Module und keine weiteren Artefakte" |
| E-g | Ob `cache_state`-Werte über `"unknown"` hinaus belegbar sind — Gegenstand der E2-Regel, hier nicht entschieden |
| E-h | Welcher Erfassungsmechanismus F1 erfüllen soll — **nicht** Gegenstand dieses Protokollvorschlags |

---

## 11. Verbleibende logische Lücken

| Lücke | Beschreibung |
| --- | --- |
| Erfassungsfähigkeit (F1) | Ein geeigneter Mechanismus mit **positivem** Ausführungsnachweis ist **nicht nachgewiesen**. Deshalb ist **O gegenwärtig nicht ableitbar** und **kein erfüllter E1-Nachweis** möglich. F1 bleibt ein offener Nachweis **innerhalb des definierten D1-Erfassungsumfangs**; eine darüber hinausgehende universelle Sicherheitsanforderung wird daraus nicht abgeleitet |
| Beweiskraft der Ausgänge | `normal_return` beweist für sich keine Ausführung; `exception` beweist weder Ausführung noch Nichtausführung |
| Mengeninklusion gegenüber Einzelversuchen | **R ⊆ O** prüft, ob jede erforderliche Modulidentität durch **mindestens eine** nachgewiesene Ausführung vertreten ist. **Sie beweist nicht, dass sämtliche Einzelversuche dieses Moduls geklärt sind.** Ein nachgewiesener Versuch verdeckt keinen weiteren ungeklärten Versuch desselben Moduls. Solange ein für den definierten Erfassungsumfang relevanter Versuch ungeklärt bleibt — **auch bei Modulen ausserhalb von R** —, darf kein vollständiger E1-Nachweis behauptet werden. Die Zulässigkeitsprüfung gegenüber **Z** bleibt zusätzlich erforderlich |
| Ereignisvollständigkeit | Transportkonsistenz beweist sie nicht (**B-8**) |
| Siegelgrenze | Weder Siegel noch Exitcode beweisen, dass danach keine relevanten Ereignisse stattfanden |
| n = 1 | Ein gültiger Header ohne Ausführungsereignisse beweist E1 nicht |
| Nachrichtenherkunft | Ohne wirksame Begrenzung der Weitergabe des Schreibzugriffs lässt sich aus dem Kanal allein keine Beschränkung auf den ursprünglichen E-Prozess oder dessen Prozessbaum ableiten |
| Laufzuordnung | Die dateisystemseitigen Grenzen und die organisatorischen Betriebsannahmen des Laufzuordnungsentwurfs gelten unverändert |
| Kein beobachtetes EOF nach FP-6 | Ein selbst geschlossenes Leseende belegt kein Stromende |
| Wirkung des Schliessens auf E | Hängt von Deskriptor- und Signalbedingungen ab und wird **nicht** unterstellt |
| Technische Wirksamkeit | Die beschriebenen Massnahmen sind **nicht durch Tests nachgewiesen**; es wird **keine Garantie gegen jede Endlosschleife oder Ressourcenerschöpfung** behauptet |

---

## 12. Spätere Implementierungs- und Qualifikationsnachweise

Byte-genaue Reproduzierbarkeit der Serialisierung und der Vergleichsserialisierung nach 2.8 auf der gebundenen Laufzeit; Erkennung doppelter Schlüssel durch den von A verwendeten Parser; ausdrückliche Typprüfung gegen Booleans in Zahlenfeldern; Einhaltung der Schreibdisziplin durch E; korrekte Zählung und AGG-Bildung unter Abbruch; Wirksamkeit der drei Grössengrenzen; Verhalten des Fehlerpfads FP einschliesslich Bereitschaftsbehandlung im Verwerfmodus und korrekter Trennung von beobachtetem EOF und Selbstschliessen; Verhalten bei erschöpftem Speicherplatz und korrekte Belegung von `storage_extent` und `validation`; Reproduzierbarkeit von `code_digest` und `params_digest` nach gebundener Vorschrift; Einhaltung der Paarregeln nach 3.4.1 durch den kontrollierten Loader; korrekte Belegung von `run_binding_stored`.

---

**Status: VORSCHLAG_NICHT_ANGENOMMEN.** Keine formale Annahme, keine Runtime-Auswahl, keine Ablage- oder Ausführungsfreigabe. Bestehende E3-Abschlussregeln, wirtschaftliche Regeln, Headerpflicht und n ≥ 1, Zahlen- und Boolean-Prüfung, Hashbildung über Originalbytes, Vergleichsserialisierung ausschliesslich zur Formprüfung, frühe Ereignisse vor `run_binding`, Fehlerpfad FP, getrennte Speicher- und Validierungszustände sowie die Referenzregel bleiben unverändert. Frühere Entwürfe werden durch dieses Dokument weder ersetzt noch formal angenommen. **D1 bleibt offen; X1 und das bekannte Fragment bleiben unberührt.**
