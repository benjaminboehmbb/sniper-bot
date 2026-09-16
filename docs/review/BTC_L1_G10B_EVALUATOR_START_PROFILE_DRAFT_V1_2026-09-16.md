# Startarchitektur A und E — konsolidierter Entwurf, revidierte Fassung

**Status: VORSCHLAG_NICHT_ANGENOMMEN.** Keine formale Annahme. Keine Runtime-Auswahl, keine Ausführungs-, Build- oder Installationsfreigabe. A und E sind nicht implementiert. Kein vollständiges Spurschema.

Das Urteil der unabhängigen Prüfung zur Vorfassung lautete `REVISE_BEFORE_DOCUMENTATION`. Nach Einarbeitung der dort verlangten Korrekturen bewertete die unabhängige Nachprüfung die Findings als behoben und sprach **`APPROVE_FOR_DOCUMENTATION` unter zwei textlichen Korrekturauflagen** aus. Diese beiden Auflagen sind in der vorliegenden Fassung eingearbeitet. **Für die so geänderte Fassung wird keine neue unabhängige Prüfung behauptet.** Eine später versehentlich ohne Prüftext gesendete Anfrage führte zu einem Prüfungsabbruch; dieser enthält keine neue Sachbewertung und wird hier nicht als Befund geführt.

---

## 1. Arbeitsgrundlage

| Prüfung | Erwartet | Beobachtet | Ergebnis |
| --- | --- | --- | --- |
| Branch | `main` | `main` | ✓ |
| HEAD | `2e3fb0dc8e6903501dcfbd48831e9c0a9fa46c43` | identisch | ✓ |
| Parent | `d49a563748a50695afd3ede3f3380ad4c390be41`, genau einer | identisch, Anzahl 1 | ✓ |
| Index und getrackte Dateien | unverändert | leer | ✓ |
| Untracked | ausschließlich `scratch/test_hatch/pyproject.toml` | genau diese Datei | ✓ |
| Fragment | 55 Bytes, `0d74d90c…e2ee2f0` | identisch | ✓ |

Diese Werte sind der zuletzt berichtete Prüfstand; für die vorliegende reine Textkorrektur wurde keine neue Repository-Prüfung durchgeführt. Das Fragment bleibt unberührt. Die bestehenden D1-, Integrations- und Paketierungsdokumente bleiben unverändert; E3-Regeln, Paketierung und wirtschaftliche Regeln werden nicht neu verhandelt.

**Primärquellen mit Versionsbezug.** Python 3.12: Kommandozeilenoptionen, `site`, `subprocess`, `os`. Python 3.9 und 3.12: Versionshinweise zu `os.pidfd_open` und `os.PIDFD_NONBLOCK`. Python 3.14: `sys.path`-Initialisierung. Linux-Handbuch: `wait(2)`, `pidfd_open(2)`. **Referenzversionen sind keine Runtime-Auswahl.**

---

## 2. Statusauswertung

### 2.1 Alleinige Zuständigkeit und dekodierter Wert

Das `Popen`-Objekt bleibt **allein** für die Statusabholung zuständig. Ausgewertet wird ausschließlich dessen bereits dekodierter `returncode`. Die 3.12-Dokumentation beschreibt: initial `None`, gesetzt durch `poll()`, `wait()` oder `communicate()`; „A `None` value indicates that the process hadn't yet terminated at the time of the last method call"; „A negative value `-N` indicates that the child was terminated by signal `N` (POSIX only)".

| Wert | Bedeutung | Behandlung durch A |
| --- | --- | --- |
| `None` | noch kein festgestellter Endstatus | weiter empfangen, weiter beobachten |
| negativ, `-N` | Signalbeendigung durch Signal `N` | kein positiver Abschluss; `N` unverändert aufzeichnen |
| nichtnegativ | regulärer Exitcode | Einordnung nach 2.4 |

**`os.WIFSIGNALED`, `os.WTERMSIG` und `os.waitstatus_to_exitcode` werden auf diesen Wert nicht angewandt** — er ist bereits dekodiert. Würden rohe Wartewerte zusätzlich benötigt, wäre deren Beschaffung gesondert zu begründen; **ein konkurrierender Abholweg wird nicht eingeführt.**

### 2.2 Ausnahme beim Start — präzisierte Feststellung

**Feststellung:** „Der `Popen`-Konstruktor liefert kein erfolgreich erzeugtes `Popen`-Objekt an A zurück; A hat daraus keinen regulär auszuwertenden `returncode`."

Ausdrücklich **nicht** abgeleitet wird daraus:

- dass **nie ein Kindprozess entstanden** war — ein Fehler kann nach der Kindprozesserzeugung und vor dem erfolgreichen Programmstart auftreten;
- dass ein Evaluatorstart **erfolgreich** war;
- dass ein Beginn beliebigen Kindcodes **bewiesen ausgeblieben** ist.

**A schließt in diesem Fall seine eigenen Pipe-Enden** — Leseende und Schreibende — selbst. Unterbleibt das, bleibt ein Schreibende offen und es tritt kein EOF ein.

### 2.3 Drei getrennte Sachverhalte

| Sachverhalt | Feststellbar aus | Nicht feststellbar daraus |
| --- | --- | --- |
| **Ausnahme beim Start** | kein `Popen`-Objekt, kein auswertbarer `returncode` | nichts über Kindprozessentstehung oder Evaluatorcode |
| **Beobachtetes Prozessende** | `returncode` ist nicht `None` | **nicht**, ob Evaluatorcode begonnen hatte |
| **Nachgewiesener Beginn des Evaluatorcodes** | ausschließlich aus der Ereignisspur | **nicht** aus einem Exitcode |

Zwischen dem `exec` und dem ersten Evaluatorbefehl liegen Interpreter-Bootstrap, `site`-Verarbeitung und Paketauflösung.

### 2.4 E-Prozessstatus gegenüber äußeren Rückgabewerten von A

Beides wird getrennt geführt. Der **E-Prozessstatus** ist ein von A beobachteter Ist-Wert. Die **äußeren Rückgabewerte** folgen der angenommenen E3-Zuordnung und beziehen sich auf den **Gesamtaufruf**: `0` für beide wirtschaftlichen Ausgänge, `2` für `TECHNICAL_ERROR` mit geschriebenem Abschlussnachweis, `3` für einen unvollständigen Lauf ohne Abschlussnachweis. Bei gewaltsamer Beendigung von A wird kein bestimmter Rückgabewert garantiert.

Eine **reguläre Beendigung von E mit Nichterfolgsstatus** schließt einen positiven Abschluss aus und wird nicht mit einer Signalbeendigung vermengt.

---

## 3. Prozessdeskriptor: Voraussetzungen und Fehlerablauf

### 3.1 Versionsangaben

| Angabe | Stand |
| --- | --- |
| `os.pidfd_open` | in **Python 3.9** eingeführt; die 3.9-Versionshinweise nennen „Exposed the Linux-specific `os.pidfd_open()` … and `os.P_PIDFD` … for process management with file descriptors" |
| `os.PIDFD_NONBLOCK` | in **Python 3.12** hinzugefügt |
| `os.P_PIDFD` | für das gewählte Modell **ohne** `waitid` keine zusätzliche Voraussetzung |
| Kernelseite | `pidfd_open(2)` nennt als HISTORY „Linux 5.3" |

### 3.2 Voraussetzungen für ein bereits beendetes, noch abfragbares Kind

`wait(2)` hält fest: ist die Behandlung von `SIGCHLD` ausdrücklich auf `SIG_IGN` gesetzt oder ist `SA_NOCLDWAIT` gesetzt, „then children that terminate do not become zombies".

| Voraussetzung | Zuordnung |
| --- | --- |
| `SIGCHLD` **nicht** ausdrücklich auf `SIG_IGN` | Bestandteil der **Startvereinbarung**; der Aufrufer startet A nicht mit einer solchen Behandlung |
| **kein** `SA_NOCLDWAIT` | ebenso |
| **keine anderweitige Statusabholung** | **Verantwortung von A**: allein das `Popen`-Objekt holt ab; A richtet keinen selbst abholenden `SIGCHLD`-Handler ein |

**Keine ungeprüfte Erfüllung wird behauptet.**

### 3.3 Ersatzablauf bei gescheitertem Erwerb

Lage: der Start war erfolgreich, `os.pidfd_open` scheitert.

| Phase | Festlegung |
| --- | --- |
| **vor EOF** | A wartet auf Bereitschaft **des Leseendes** mit **endlicher Weckspanne** und ruft bei jedem Wecken `proc.poll()` auf. Der Empfang läuft fortlaufend weiter |
| **nach festgestelltem EOF** | das Leseende wird aus der Abfrage entfernt und geschlossen. Danach wird **ausschließlich über dasselbe `Popen`-Objekt** auf das Prozessende gewartet. **Blockierendes `wait()` ist hier zulässig**, weil kein weiterer Kanal mehr zu bedienen ist |
| **Prozessende vor EOF** | A **empfängt weiter**. Ein festgestelltes Prozessende **ersetzt EOF nicht** |
| **Ressourcen** | ein nicht erworbener Deskriptor ist nicht zu schließen; ein erworbener wird auf **jedem** Pfad geschlossen |
| **Abgrenzung** | die Weckspanne ist ein Abfrageintervall, **keine Frist für E**. Es wird **keine Laufzeit- oder Beendigungsgarantie** behauptet und keine Zeitgrenze als angenommen ausgegeben |

Der einzige Unterschied zur bevorzugten Variante ist die Art des Weckens.

---

## 4. Deskriptorlebenszyklus

### 4.1 Gezielte Übergabe

**`pass_fds` genügt.** Die 3.12-Dokumentation vermerkt: „Providing any _pass_fds_ forces _close_fds_ to be `True`." Außer `0`, `1`, `2` und dem benannten Deskriptor werden alle übrigen vor der Ausführung geschlossen. **Ein vorgelagertes allgemeines Vererbbarsetzen in A entfällt.**

### 4.2 Eigentümer und Schließen

| Lage | Leseende | Schreibende in A | Schreibende in E |
| --- | --- | --- | --- |
| vor dem Start | A | A | — |
| nach erfolgreichem Start | A behält es bis EOF | **A schließt seine Kopie unmittelbar** | bleibt in E offen |
| **kein `Popen`-Objekt zurückgeliefert** | **A schließt es selbst** | **A schließt es selbst** | unbestimmt, siehe 2.2 |
| nach festgestelltem EOF | **A entfernt es aus der Abfrage und schließt es** | bereits geschlossen | Verantwortung von E |

### 4.3 Präzisierungen

- Der übergebene Schreibdeskriptor **bleibt nach dem `exec` in E offen**; das ist beabsichtigt.
- **Ein später in E gesetztes Close-on-exec verhindert keine Kopien durch `fork`**; es wirkt erst beim nächsten `exec`. Ob E den Deskriptor weitergibt, liegt in E's Verantwortung und ist eine offene Anforderung an E.
- **EOF-Voraussetzung:** solange **noch ein Schreibende offen gehalten wird** — gleich von welchem Prozess —, bleibt EOF aus.

### 4.4 Schreibdisziplin in E

**Blockierendes Schreiben allein garantiert keine vollständigen Datensätze.**

| Fall | Erforderliche Behandlung |
| --- | --- |
| **Teilübertragung** | der Schreibaufruf kann weniger Bytes übertragen als angefordert; E schreibt in einer Schleife weiter, bis der **gesamte** Datensatz übertragen ist |
| **`EINTR` / Signalbehandlung** | Ein durch `EINTR` unterbrochener Schreibaufruf darf wiederholt werden, sofern der Signalhandler keine Ausnahme auslöst. Bei `os.write` übernimmt Python seit Version 3.5 diese Wiederholung automatisch, wenn der Handler keine Ausnahme auslöst. Gibt ein Schreibaufruf eine positive Zahl übertragener Bytes zurück, wird ausschließlich mit den verbleibenden Bytes fortgesetzt; bereits bestätigte Bytes werden nicht erneut gesendet. Ausnahmen eines Signalhandlers und eine Signalbeendigung sind keine gewöhnlichen Wiederholungsfälle und dürfen nicht als erfolgreicher Schreibabschluss behandelt werden. |
| **Schreibfehler** | insbesondere ein geschlossenes Leseende ist ein definierter Zustand mit eigener Behandlung; er darf nicht stillschweigend zu einem abgeschnittenen Datensatz führen |
| **Abgrenzung** | die Erkennung unvollständiger Datensätze auf Protokollebene gehört zum **noch nicht ausgearbeiteten Spurschema** |

---

## 5. Startvereinbarung

### 5.1 Bedarfsanalyse von A

| Aufgabe von A | Benannte Schnittstellen | Erkennbarer Umgebungsbedarf |
| --- | --- | --- |
| Kanal anlegen, Modus setzen, lesen, schließen | `os.pipe`, `os.set_blocking`, `os.read`, `os.close` | keiner |
| E starten | `subprocess.Popen` mit `shell=False`, absolutem Programmpfad, `pass_fds`, `env`, `cwd` | **kein `PATH`** — absoluter Programmpfad, keine Shell |
| Bereitschaft überwachen | `selectors` beziehungsweise `select`, `os.pidfd_open` | keiner |
| Aggregathash unabhängig nachberechnen | `hashlib` | keiner |
| Artefakte lesen, Abschluss schreiben und umbenennen | `os`, Datei-Ein- und -Ausgabe, `json`, `os.rename` | **kein `TMPDIR`** — keine Temporärdateien; die Abschlussdatei entsteht nach den angenommenen Regeln als `.partial` im Laufverzeichnis |
| Argumente und Rückgabewert | `sys` | keiner |

**Nicht benötigt und wegzulassen:** `PATH`, `HOME`, `TMPDIR`, `SHELL`, `USER` sowie sämtliche `PYTHON*`-Variablen, die unter `-I` ohnehin ignoriert werden.

Zu berücksichtigen ist der Einfluss des Gebietsschemas: Die Umgebungsvariablen `LC_ALL`, `LC_CTYPE` und `LANG` sind keine `PYTHON*`-Variablen und werden durch `-E` beziehungsweise `-I` nicht ignoriert. Daraus folgt keine Pflicht, alle drei zu setzen. Der Vorschlag in Abschnitt 5.2 sieht ausschließlich `LC_ALL` vor; `LC_CTYPE` und `LANG` bleiben ungesetzt. Der konkrete `LC_ALL`-Wert und das daraus zusammen mit der gebundenen Laufzeit resultierende Kodierungsverhalten bleiben zu qualifizieren. `L1_EVAL_LC_ALL` bezeichnet dabei einen Bindungsparameter, keine zusätzlich zu setzende Umgebungsvariable.

### 5.2 Bevorzugte Umgebungsmenge

| Variable | Rolle | Wert |
| --- | --- | --- |
| `LC_ALL` | legt das Gebietsschema für A und E deterministisch fest | **Bindungsparameter `L1_EVAL_LC_ALL`** — der konkrete Wert wird hier **nicht festgelegt und nicht erfunden**; er ist gegen die später gebundene Laufzeit zu bestimmen und zu qualifizieren |

Alle übrigen Variablen werden **nicht** gesetzt; die Menge ist geschlossen. **Falls sich bei der späteren Qualifikation zeigt, dass kein geeigneter Wert verfügbar ist, ist stattdessen die leere Umgebung zu wählen und das dann geltende Standardverhalten ausdrücklich zu qualifizieren.** Es werden keine installierten Gebietsschemata behauptet. Die Entwurfsentscheidung über die **Struktur** der Menge ist von der **Runtime-Qualifikation** getrennt; Letztere ist nicht erbracht.

### 5.3 Arbeitsverzeichnis

| Prozess | Festlegung |
| --- | --- |
| **A** | ein gebundenes, absolutes Arbeitsverzeichnis, unabhängig vom Verzeichnis des Aufrufers; vom Aufrufer gesetzt |
| **E** | ein gebundenes, absolutes Arbeitsverzeichnis, von A über `cwd=` gesetzt |

Sämtliche Eingabepfade werden absolut übergeben.

### 5.4 Standarddeskriptoren — Zuständigkeiten

| Deskriptor | A | Wer richtet ein | E | Wer richtet ein |
| --- | --- | --- | --- | --- |
| `0` | Nullgerät | **äußerer Aufrufer**, vor dem Interpreterstart von A | Nullgerät | **A**, vor dem Start von E |
| `1` | gebundene Senke | **äußerer Aufrufer**, vor dem Interpreterstart von A | gebundene Senke | **A**, vor dem Start von E, über `stdout=` übergeben |
| `2` | gebundene Senke, **getrennt** von `1` | **äußerer Aufrufer**, vor dem Interpreterstart von A | gebundene Senke, **getrennt** von `1` | **A**, vor dem Start von E, über `stderr=` übergeben |

**Ablauf.**

1. Der **äußere Aufrufer** richtet `0`, `1` und `2` von A **vor** dessen Interpreterstart ein.
2. **A übernimmt diese bereits eingerichteten Standarddeskriptoren** und richtet für sich selbst nichts mehr ein. Damit sind auch **frühe Ausgaben von A** — vor dem Start von E und vor jeder Prüfung — erfasst.
3. **A öffnet die beiden vorgesehenen Senken für E vor dessen Start** und übergibt sie ausdrücklich.
4. **Scheitert bereits die Einrichtung der A-Senken, wird A nicht gestartet.** Dieser Fehler bleibt Aufgabe des Aufrufers und ist kein Zustand innerhalb von A.

**Keine unbeobachteten Röhren:** `stdout=PIPE` oder `stderr=PIPE` ohne begleitendes Leeren wird nicht vorgeschlagen; die 3.12-Dokumentation weist auf die Blockierungsgefahr hin. Die Trennung von `1` und `2` für E ist erforderlich, weil die angenommenen Abschlussregeln mehrere Diagnosen ausdrücklich der Standardfehlerausgabe zuweisen.

**Eine Umleitung belegt keine vollständige oder erfolgreiche Speicherung.** Schreibfehler auf einer Senke — etwa erschöpfter Speicherplatz oder ein Ein-/Ausgabefehler — können Ausgaben ganz oder teilweise verlieren. Eine solche Garantie wird nicht formuliert.

### 5.5 Die vier Senken

**Es werden genau vier Senken vorgesehen** — `1` und `2` für A, `1` und `2` für E — **und keine weiteren.**

| Frage | Festlegung |
| --- | --- |
| **Erzeuger** | die beiden A-Senken der **äußere Aufrufer**; die beiden E-Senken **A** |
| **Ablage** | ein **gebundenes Diagnoseverzeichnis**, als Parameter geführt. **Nicht** das Laufverzeichnis: dieses existiert zum Zeitpunkt der Einrichtung noch nicht |
| **Verhalten vor Vorliegen einer `run_id`** | die A-Senken sind ab dem Interpreterstart von A offen, die E-Senken ab dem Start von E. Frühe Ausgaben — insbesondere die nach den Abschlussregeln vorgesehenen Diagnosen bei fehlgeschlagener Verzeichnisanlage — werden dadurch erfasst, **soweit die Speicherung gelingt** |
| **Verhältnis zur Artefaktmenge** | **keine** Laufartefakte. Die angenommene Artefaktliste des Abschlussnachweises bezieht sich auf den Inhalt des Laufverzeichnisses; diese Dateien liegen außerhalb und gehen nicht in die Hashliste des Laufs ein. **Ihre Einordnung gegenüber der Regel „Keine weiteren Module und keine weiteren Artefakte" bleibt eine offene Vertragsfrage** |

**Eine vorab gebundene Ausgabesenke ist kein vorab bekannter Inhaltsnachweis.** Gebunden werden Pfad und Einrichtung, nicht der Inhalt.

### 5.6 Dateiform von A und Interpreteroptionen — getrennte Wirkungen

| Aussage | Stand |
| --- | --- |
| Die **Einzeldatei** vermeidet den Bedarf an **eigenen, separat aufzulösenden A-Nebenmodulen** | zutreffend; das ist ihr Zweck |
| Sie verhindert **für sich** weder Nebenmodulimporte noch die `site`-Verarbeitung | zutreffend; die Dateiform allein bewirkt beides nicht |
| **`-S`** unterbindet den **automatischen Import von `site`** und damit die Verarbeitung von `site`-Pfaden und `.pth`-Dateien | Wirkung der Option, nicht der Dateiform |
| **`-I`** verhindert unter anderem das automatische Voranstellen des **Skript- beziehungsweise Arbeitsverzeichnisses** | Wirkung der Option |
| **Standardbibliothek**, sonstige wirksame Pfadinitialisierung und **native Abhängigkeiten** bleiben relevant | unverändert; sie werden von keiner der beiden Maßnahmen erfasst |

**Es wird keine pauschale Unabhängigkeit von sämtlichen Pfadkonfigurationsmechanismen behauptet.**

---

## 6. Optionen und Präfixe

**A: `-I -B -S`. E: `-I -B`.**

`-I` ist **nicht** die einzige Möglichkeit, Interpretervariablen zu ignorieren — `-E` allein bewirkt dies bereits. `-I` wird gewählt, weil es drei Wirkungen geschlossen zusammenfasst: `PYTHON*`-Variablen ignorieren wie `-E`, keinen potenziell unsicheren Pfad voranstellen wie `-P`, das Benutzer-`site-packages` auslassen wie `-s`. Der Vorteil ist Geschlossenheit, nicht Exklusivität.

`-B` unterbindet neue Bytecode-Schreibvorgänge und trifft **keine** Cache-Aussage; Cache-Lesen bleibt Gegenstand der angenommenen E2-Regel.

`-S` für A, weil A keine `site-packages` benötigt; **nicht** für E, weil im vorgeschlagenen Präfixmodell erst `site` die `site-packages` hinzufügt.

### 6.1 Virtuelle Umgebung unter `-S` — versionsabhängig

| Version | Verhalten |
| --- | --- |
| **3.12** | die `site`-Dokumentation beschreibt, dass bei vorhandener `pyvenv.cfg` eine Ebene über `sys.executable` die Werte `sys.prefix` und `sys.exec_prefix` auf dieses Verzeichnis gesetzt werden, während die Basispräfixe stets die realen bleiben. Das geschieht **innerhalb von `site`** — und `site` wird durch `-S` nicht importiert |
| **3.14** | „Changed in version 3.14: `sys.prefix` and `sys.exec_prefix` are now set to the `pyvenv.cfg` directory during the path initialization. This was previously done by `site`, therefore affected by `-S`." |

**Folge:** auf einer 3.12-artigen Laufzeit erhielte A unter `-S` die Präfixe der Basisinstallation, E die der Umgebung; auf einer 3.14-artigen Laufzeit beide die der Umgebung. **Hier wird keine Laufzeit ausgewählt.**

### 6.2 Fünf getrennte Größen

**Aufrufpfad** — entscheidet über das Auffinden einer `pyvenv.cfg`. **Binärziel** — die aufgelöste Interpreterdatei; der in Abschnitt 10 des Integrationsvertrags gebundene Wert. **Basispräfixe** — stets die realen Präfixe der Installation. **Tatsächliche Prozesspräfixe** — je Prozess, abhängig von Optionen und Version. **Tatsächlich verwendete Modulpfade** — der aufgelöste Suchpfad und die je Modul geladenen Dateien.

**Gleicher Aufrufpfad und gleicher Binärinhalt garantieren keine gleichen Prozesspräfixe**, sobald sich die Startoptionen unterscheiden.

---

## 7. Empfang, EOF und Prozessende

**Bestehende Vorgabe aus der begrenzten E3-Annahme:** fortlaufender Empfang während E läuft; kein blockierendes Warten bei unbeachtetem Kanal; eigene Feststellung des E-Endstatus; Weiterlesen bis zum **tatsächlichen EOF**. **Neu ist allein die Umsetzung.**

### 7.1 Lesezustände

| Zustand | Behandlung |
| --- | --- |
| Bytes gelesen | weiterverarbeiten |
| **tatsächliches EOF** | Empfangsende feststellen; **das Leseende wird aus der Bereitschaftsabfrage entfernt und geschlossen** |
| `EAGAIN` beziehungsweise `EWOULDBLOCK` | erneut auf Bereitschaft warten |
| `EINTR` | wiederholen; weder EOF noch gelesener Datensatz |
| sonstiger Fehler | kein positiver Abschluss |

**Begründung für das Entfernen und Schließen:** ein registriertes Leseende, für das bereits EOF festgestellt wurde, meldet dauerhaft Bereitschaft und würde die Abfrageschleife ohne Erkenntnisgewinn beschäftigen. **Eine zwingend endlose Laufzeit wird daraus nicht behauptet** — es geht um eine unnötige Schleife, nicht um einen bewiesenen Stillstand. Dasselbe gilt im bevorzugten Ablauf: **bereits erledigte Bereitschaftsquellen werden nicht dauerhaft weiter abgefragt.**

### 7.2 Reihenfolge von EOF und Prozessende

**Beide können in beliebiger Reihenfolge eintreten und werden unabhängig erfasst.**

| Lage | Verhalten von A |
| --- | --- |
| **Prozessende vor EOF** | **A empfängt weiter** bis zum tatsächlichen EOF. **Ein festgestelltes Prozessende ersetzt EOF nicht** |
| **EOF vor Prozessende, bevorzugter Ablauf** | Leseende entfernt und geschlossen; der Prozessdeskriptor bleibt als einzige Bereitschaftsquelle, bis das Ende festgestellt ist |
| **EOF vor Prozessende, Ersatzablauf ohne Prozessdeskriptor** | Leseende entfernt und geschlossen; danach **blockierendes Warten über dasselbe `Popen`-Objekt**, zulässig, weil kein weiterer Kanal mehr zu bedienen ist |

**Es wird keine Laufzeit- oder Beendigungsgarantie ergänzt.**

---

## 8. Laufverzeichnis: Zuordnung und Veröffentlichungssperre

### 8.1 Drei getrennte Fragen

| Frage | Gegenstand | Zuständiger Regelungsbereich |
| --- | --- | --- |
| **Laufzuordnung** | welches Verzeichnis zu **dieser** Ausführung gehört | **neu**; nicht aus E1 abgeleitet |
| **Ausführungsidentität** | welcher Code tatsächlich geladen und ausgeführt wurde | D1 und E1 |
| **Abschlussvoraussetzungen** | was erfüllt sein muss, bevor A veröffentlichen darf | angenommene E3-Regeln |

**Die Laufzuordnungslücke wird nicht ohne vertragliche Herleitung mit E1 gleichgesetzt.** Sie ist ein eigener, hier benannter Punkt; sie wirkt auf die Abschlussvoraussetzungen und ist von der Ausführungsidentität zu unterscheiden.

### 8.2 Prüfungen und ihre Aussagekraft

| Prüfung | Inhalt | Aussagekraft |
| --- | --- | --- |
| **a) Zulässige Lage** | die gemeldete Kennung ist ein einzelner Namensbestandteil ohne Trennzeichen und ohne `..`; der aufgelöste Pfad ist unmittelbares Kind der von A übergebenen Ergebniswurzel und trägt genau diese Kennung | belegt **nur die Lage** |
| **b) Vorabliste** | A erstellt **vor** dem Start von E eine rein lesende Auflistung der unmittelbaren Einträge der Ergebniswurzel; der später gemeldete Name muss dort **fehlen** | belegt **nur**, dass der gemeldete Name **bei der Vorprüfung nicht vorhanden war**. **Sie beweist keine Anlage durch genau den gestarteten E-Prozess** |
| **c) Bezugskonsistenz** | A öffnet das Verzeichnis **einmal** und führt alle weiteren Prüfungen sowie die Veröffentlichung auf **diesen einen Verzeichnisbezug** aus | bindet Prüfung und Veröffentlichung an dasselbe Verzeichnisobjekt. **Bezugskonsistenz, nicht Angreiferabwehr.** Die konkrete Schnittstellenform ist gegen die gebundene Laufzeit zu bestätigen |

**Die Prüfungen a bis c reichen allein nicht zur Freigabe der Veröffentlichung.**

### 8.3 Sperre der Veröffentlichung

- **Solange die Zuordnung zur aktuellen Ausführung ungeklärt bleibt, veröffentlicht A in diesem unzugeordneten Verzeichnis keine `completion.json`.**
- Der Vorschlag, `completion.json` trotzdem technisch zu veröffentlichen und sie lediglich nicht als vollständigen Abschluss zu werten, wird **ausdrücklich nicht übernommen**.
- In dieser Lage bleibt der Aufruf **unvollständig ohne Abschlussnachweis**; der äußere Rückgabewert folgt der bestehenden E3-Regel, soweit A regulär abschließen kann.
- Ein **`TECHNICAL_ERROR`-Abschluss bleibt nur bei zuverlässig zugeordneter Ablage und tatsächlich vorhandenen vorgeschriebenen Fehlerartefakten möglich.**
- **Es wird kein Abschlussnachweis vorgetäuscht**, wenn erforderliche Artefakte oder eine zugeordnete Ablage fehlen.

**Die konkrete Schließung der Zuordnungslücke bleibt ein benannter Ausarbeitungspunkt.** Innerhalb dieser Korrektur wird dafür **keine neue Architektur erfunden** und **keine Angreiferabwehrpflicht** eingeführt.

### 8.4 Unveränderte Zuständigkeit

**Die exklusive Anlage des Laufverzeichnisses durch `run_context` bleibt bestehende Vorgabe.** A übernimmt diese Aufgabe nicht, weder ausdrücklich noch stillschweigend; A legt weder die Ergebniswurzel noch das Laufverzeichnis an.

### 8.5 Laufkennung und frühe Ereignisse

Relevante Ereignisse können **vor** der Anlage des Laufverzeichnisses entstehen; die angenommenen Regeln sehen ausdrücklich den Fall vor, dass nichts geschrieben wird und Ursache sowie Kennung auf die Standardfehlerausgabe gehen. Die Idee, der **erste** Datensatz trage stets Kennung und Verzeichnis, ist als unbedingte Regel **nicht haltbar**. **Relevante Ereignisse dürfen nicht allein wegen der Nachrichtenreihenfolge aus der Erfassung fallen.** Vorgeschlagen wird ein **eigener Kennungsdatensatz**, sobald die Kennung besteht; die Ausgestaltung gehört zum noch nicht ausgearbeiteten Spurschema.

---

## 9. Abschluss — bestehende E3-Regeln, nur angewandt

Folgenummern 1 bis n; **genau ein Siegel** mit Nummer n+1, deklarierter Anzahl n und Aggregathash ausschließlich über 1 bis n; **unabhängige Nachberechnung** durch A; kein Datensatz nach dem Siegel; **Transportkonsistenz ersetzt keine Ereignisvollständigkeit**, der Fall n = 0 erfüllt für sich keinen E1-Nachweis; **vollständige Artefakt-, Integritäts- und Gate-Konsistenzprüfung** einschließlich der Vollständigkeitsprüfung der Gate-Menge **vor** jeder Konjunktion; **keine Neuberechnung fachlicher Kennzahlen durch A**; **technische Fehler getrennt vom wirtschaftlichen `COMPLETED_FAIL`**; `metrics_released=true` nur bei sämtlichen bestandenen technischen Prüfungen, wobei ein verfehltes Gate die Metrikfreigabe bei technisch gültigem Lauf nicht verhindert; **alleinige Veröffentlichung durch A** über die einmalige Umbenennung; **keine automatische Wiederholung** bei ungewissem Ausgang; äußere Rückgabewerte nach 2.4.

**Die abschließende Freigabe erfolgt erst nach allen erforderlichen Prüfungen** — einschließlich der geklärten Laufzuordnung nach Abschnitt 8.

---

## 10. Status der Zuordnungen

**Keine pauschale BIND-1b-Zuordnung.** Ist-Evidenz ist nicht automatisch einer bestehenden Bindungsstufe zugeordnet.

| Laufzeitwert | Zuordnung |
| --- | --- |
| `run_id` und Laufverzeichnis | keine bestehende Bindungsstufe benennbar; offen |
| Ereignisspur mit Bytes und Hashes | keine bestehende Bindungsstufe benennbar; offen |
| Beobachteter `returncode` von E | keine bestehende Bindungsstufe benennbar; offen |
| Tatsächliche Prozesspräfixe und aufgelöste Modulpfade | Abschnitt 10 sieht Selbstauskünfte und Dateibindungen vor; die Zuordnung der **Ist**-Werte ist offen |
| Artefaktidentitäten des Laufs | die angenommenen Abschlussregeln verlangen eine Artefaktliste mit Pfad, Bytes und SHA256; insoweit besteht eine Vorgabe |
| Inhalt der vier Senken nach 5.5 | keine bestehende Bindungsstufe; offen |

**A und die Ereignisspur sind nach der begrenzten E3-Annahme bereits grundsätzlich als geplante Komponente beziehungsweise geplantes Artefakt angenommen**, ebenso die Übertragung der Abschlussverantwortung auf A. **Davon getrennt** steht die Anpassung älterer Vertragsstellen aus.

**Die angenommenen Empfangs- und Abschlussanforderungen sind Vorgabe**, nicht „keine Vorgabe". Neu sind allein die konkrete Umsetzung, die benannten Schnittstellen und die noch nicht angenommenen Schemafelder.

---

## 11. Bestehende Vorgabe, neuer Vorschlag, spätere Qualifikation

| Gegenstand | Bestehende Vorgabe | Neuer Vorschlag | Später zu qualifizieren oder zu binden |
| --- | --- | --- | --- |
| Statusauswertung | E3: eigene Feststellung des Endstatus | ausschließlich dekodierter `returncode`; alleinige Zuständigkeit des `Popen`-Objekts | — |
| Ausnahme beim Start | — | Feststellung nach 2.2, ohne Schluss auf Kindprozessentstehung | — |
| Prozessdeskriptor | — | Bereitschaftssignal; Ersatzablauf nach 3.3 | Verfügbarkeit nach Kernel- und Python-Version |
| `SIGCHLD`-Bedingungen | — | Startvereinbarung und Verantwortung von A | Feststellung im konkreten Lauf |
| Deskriptorübergabe | — | `pass_fds`; Schließregeln nach 4.2 | Weitervererbung durch E offen |
| Schreibdisziplin in E | — | Teilübertragung, `EINTR`-Behandlung, Schreibfehler nach 4.4 | Protokollebene im Spurschema |
| Umgebung von A und E | — | geschlossene Menge mit `LC_ALL` als Bindungsparameter | konkreter Wert und Kodierungsverhalten |
| Arbeitsverzeichnis | — | gebunden und absolut für A und E | — |
| Standarddeskriptoren | Diagnosen auf der Standardfehlerausgabe | Aufrufer richtet A's `0`, `1`, `2` ein; A richtet E's ein; genau vier Senken | Speicherung ist nicht garantiert; Einordnung gegenüber §2 offen |
| EOF-Behandlung | E3: Lesen bis zum tatsächlichen EOF | Entfernen und Schließen des Leseendes; Ablauf nach 7.2 | — |
| Kanalbenennung für E | Aufrufform ohne solches Argument; keine Umgebungsvariablen | `--trace-fd <ganzzahl>` | **Vertragsänderung** an der Aufrufform |
| Laufzuordnung | exklusive Anlage durch `run_context` | Prüfungen a, b, c; **Veröffentlichungssperre** nach 8.3 | Schließung der Zuordnungslücke — benannter Ausarbeitungspunkt |
| Laufkennung | — | eigener Kennungsdatensatz, nicht zwingend der erste | Spurschema |
| Optionen und Präfixe | Abschnitt 10 bindet das Binärziel | A `-I -B -S`, E `-I -B`; je Prozess eigene Präfixe erheben | versionsabhängige Wirkung nach 6.1; **B5** |
| A und Ereignisspur | nach E3 grundsätzlich angenommen | — | Anpassung älterer Vertragsstellen |
| Identität von A | — | binden | kein Feld in B1 bis B14 |
| **B6**, **B7**, **B8**, **B9**, **B10** | offen | — | fehlende Bindungen |

**Verbleibende Nachweislücken:** Bootstrap von A und von E; Vollständigkeit von O; durchgehende Wirksamkeit des kontrollierten Ladewegs; Durchsetzung der Wegpflicht; EXTENSION-Module; native Ladebindungen; Weitervererbung von Schreibdeskriptoren durch E; **Laufzuordnung nach 8.2 b**.

**Keine Zirkelschlüsse:** die eigene Hashmeldung von A beweist nicht die Herkunft des von A ausgeführten Codes; ein erfolgreicher Start oder ein vorhandenes `completion.json` beweist keine vollständige Ereignisabdeckung. Keine Speicherintegritäts- oder Angreiferabwehrpflicht, keine B3/B5-Kopplung, keine Rückkehr zur verworfenen Audit-Stapelkorrelation.

---

## 12. Bearbeitungsverlauf der unabhängigen Prüfung

| Stufe | Ergebnis | Reichweite |
| --- | --- | --- |
| Prüfung der Vorfassung | `REVISE_BEFORE_DOCUMENTATION` | vier Findings zu EOF und Prozessende, frühen Ausgaben von A, Dateiform und Optionen sowie Veröffentlichung bei ungeklärter Laufzuordnung |
| Einarbeitung | Findings behoben | Abschnitte 2.2, 2.3, 4.2, 5.4, 5.5, 5.6, 7.1, 7.2, 8.1 bis 8.3 |
| Nachprüfung | **`APPROVE_FOR_DOCUMENTATION` unter zwei textlichen Korrekturauflagen** | Auflagen zu Abschnitt 5.1 (Gebietsschema) und Abschnitt 4.4 (`EINTR` beim Schreiben) |
| Vorliegende Fassung | beide Auflagen eingearbeitet | **keine neue unabhängige Prüfung dieser Fassung** |

Zusätzlich zu den vier Findings wurde die Aussage zur Popen-Startausnahme präzisiert. Diese Änderung war kein fünftes Finding der damaligen unabhängigen Prüfung.

Eine später versehentlich ohne Prüftext gesendete Anfrage führte zu einem Prüfungsabbruch; dieser enthält **keine neue Sachbewertung** und wird nicht als Befund geführt.

---

**Status: VORSCHLAG_NICHT_ANGENOMMEN. D1 bleibt offen. X1 und das bekannte Fragment bleiben unberührt.** Die vier begrenzten D1-Teilannahmen, die Paketierung und die wirtschaftlichen Regeln bestehen unverändert fort.
