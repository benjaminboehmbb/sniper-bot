# BTC-L1 G10-B — Laufverzeichniszuordnung: nicht bindender Entwurf

**Status: VORSCHLAG_NICHT_ANGENOMMEN.** Keine formale Annahme, keine Runtime-Auswahl und keine Implementierungs-, Build-, Installations- oder Ausführungsfreigabe. **D1 bleibt offen.**

Dieses Dokument hält einen vorgeschlagenen Ersatz für Abschnitt 8 des Startprofilentwurfs fest. Es ersetzt oder ändert den gespeicherten Startprofilentwurf und den Integrationsvertrag nicht. Die Nummerierung 8.1 bis 8.11 bleibt für die Zuordnung zum vorgeschlagenen Ersatzabschnitt erhalten.

**Bezugsdokument:** `docs/review/BTC_L1_G10B_EVALUATOR_START_PROFILE_DRAFT_V1_2026-09-16.md`, 31931 Bytes, SHA256 `3f1bd6a7cdb82c1652ab5f9426b4c15f28b20022d630dd36ee8a02b4782c78f4`.

**Prüfungsverlauf:** Die unabhängige Prüfung des Ersatztexts erteilte `APPROVE_FOR_DOCUMENTATION` unter zwei Korrekturauflagen: Berichtigung des Querverweises in P4 von Schritt 8 auf Schritt 9 und Entfernung der unzulässigen Kopplung von Nonce-Geheimhaltung und Deskriptorschutz. Beide Auflagen sind im nachfolgenden Text eingearbeitet. Der anschließende Textvergleich bestätigte diese beiden Änderungen bei ansonsten unverändertem Inhalt. Für die so geänderte Fassung und diesen Dokumentationsrahmen wird keine neue unabhängige Prüfung behauptet. Die Einstufung betrifft ausschließlich die Dokumentierbarkeit als nicht bindender Entwurf.

---

## 8. Laufverzeichnis: Zuordnung, Prüfung und Veröffentlichungssperre

### 8.1 Vier getrennte Eigenschaften

| Nr. | Eigenschaft | Träger | Stand |
| --- | --- | --- | --- |
| **P1** | Zulässige Lage unter der Ergebniswurzel | A prüft | **im vorgeschlagenen Modell** durch 8.2 Schritte 1 bis 4 abgedeckt; nicht implementiert |
| **P2** | Frische, **exklusive** Verzeichnisanlage | **E**, `run_context` | **bestehende Vorgabe.** Das hier vorgeschlagene Verfahren beobachtet sie **nicht unabhängig** und setzt insoweit die Einhaltung der bestehenden E-Vertragspflicht voraus |
| **P3** | Zuordnung zur **konkret gestarteten** Ausführung | A | **im vorgeschlagenen Modell** durch 8.2 abgedeckt, **bedingt durch das Betriebsmodell nach 8.3**; nicht implementiert |
| **P4** | Gleichbleibende Verzeichnisidentität bei Prüfung und Veröffentlichung | A | **im vorgeschlagenen Modell** durch das Öffnen nach 8.2 Schritte 3 und 9, das Festhalten der Kennungen mittels `os.fstat` und den abschließenden Vergleich nach 8.2 Phase III abgedeckt; nicht implementiert |

Die Laufzuordnung ist von der **Ausführungsidentität** (D1, E1) und von den **Abschlussvoraussetzungen** (E3) zu unterscheiden und wird nicht ohne vertragliche Herleitung mit E1 gleichgesetzt.

### 8.2 Zuordnungsverfahren — Vorschlag

**Grundgedanke.** A erzeugt für jeden Aufruf eine eigene, exklusiv angelegte **Laufwurzel** und übergibt deren Pfad als `--results-root`. **A legt damit die Ergebniswurzel an — eine ausdrückliche Änderung gegenüber der früheren Festlegung.** Das Laufverzeichnis `<results_root>/<run_id>/` legt weiterhin ausschließlich `run_context` exklusiv an.

**Phase 0 — Vorbereitung durch A**

| Schritt | Handlung |
| --- | --- |
| 1 | A öffnet die gebundene **Ergebnisbasis** einmal über ihren absoluten Pfad mit `os.open(..., os.O_DIRECTORY \| os.O_NOFOLLOW)` und hält den Deskriptor. **`O_NOFOLLOW` wirkt nur auf die letzte Komponente**; über die vorgelagerten Komponenten wird nichts ausgesagt |
| 2 | A legt die Laufwurzel mit `os.mkdir(<name>, dir_fd=<Ergebnisbasis-fd>)` an; bei bestehendem Namen wird `FileExistsError` ausgelöst. Nicht vorhersagbarer Name, **kein Neuversuch**, bei Kollision Abbruch ohne Start von E |
| 3 | A öffnet die Laufwurzel mit `os.open(<name>, os.O_DIRECTORY \| os.O_NOFOLLOW, dir_fd=<Ergebnisbasis-fd>)` — **ein einzelner Name relativ zu einem festgehaltenen Elterndeskriptor** —, prüft den geöffneten Deskriptor mit `os.fstat` und hält Geräte- und Inode-Kennung fest. **Kein vorgelagerter Eintragstest** |
| 4 | A stellt über `os.listdir(<Laufwurzel-fd>)` fest, dass die Laufwurzel leer ist |
| 5 | A startet E mit `--results-root <Laufwurzel, absolut>` und `--trace-fd <n>`; der Pfad wird an keine andere Stelle übergeben |

**Phase I — Lauf und Empfang**

| Schritt | Akteur | Handlung |
| --- | --- | --- |
| 6 | E, `run_context` | erzeugt `run_id` vor jeder Dateisystemaktion und legt `<results_root>/<run_id>/` exklusiv an — unverändert bestehende Vorgabe |
| 7 | E, `run_context` | sendet unmittelbar nach erfolgreicher Anlage **genau einen** Zuordnungsdatensatz mit der `run_id` als einzelnem Pfadbestandteil; höchstens einer je Spur |
| 8 | A | empfängt fortlaufend bis zum **tatsächlichen EOF** und stellt das Prozessende **unabhängig** fest. Beide Ereignisse können in beliebiger Reihenfolge eintreten; **Prozessende ersetzt weder EOF noch die Auswertung bereits übertragener Nachrichten** |

**Phase II — Prüfungen**

| Schritt | Handlung |
| --- | --- |
| 9 | Zuordnungsprüfung: (a) erster und einziger Zuordnungsdatensatz; (b) einzelner Pfadbestandteil, weder `.` noch `..`, ohne Trennzeichen; (c) A **öffnet den gemeldeten Namen direkt** mit `os.open(<run_id>, os.O_DIRECTORY \| os.O_NOFOLLOW, dir_fd=<Laufwurzel-fd>)` — scheitert das Öffnen, weil der Eintrag kein Verzeichnis oder ein symbolischer Link ist, ist das der Befund; (d) `os.fstat` auf den geöffneten Deskriptor, Kennungen festhalten. Dies ist das **Laufverzeichnis** |
| 10 | Eindeutigkeitsprüfung: `os.listdir(<Laufwurzel-fd>)` enthält **genau einen** Eintrag mit dem gemeldeten Namen. Die Liste dient allein dieser Prüfung, **nicht** der Objektauswahl |
| 11 | **Artefakt-, Integritäts- und Gate-Prüfungen** nach den bestehenden E3-Regeln, relativ zum Laufverzeichnis-Deskriptor |

**Phase III — abschließender Verzeichnisvergleich**

| Schritt | Handlung |
| --- | --- |
| 12 | `os.stat(<run_id>, dir_fd=<Laufwurzel-fd>, follow_symlinks=False)` gegen die in Schritt 9 (d) festgehaltenen Kennungen |
| 13 | `os.stat(<absoluter Laufwurzelpfad>)` gegen die in Schritt 3 festgehaltenen Kennungen — stellt fest, ob der an E übergebene Pfad noch auf dasselbe Objekt auflöst. **Feststellung zu einem Zeitpunkt, keine Ausschaltung konkurrierender Änderungen** |

**Phase IV — Veröffentlichung**

| Schritt | Handlung |
| --- | --- |
| 14 | **Nur bei erfüllten Voraussetzungen** aus Phase II und III: die bestehende einmalige Veröffentlichung, relativ zum Laufverzeichnis-Deskriptor, mit `src_dir_fd` und `dst_dir_fd` |

**Keine fachliche Prüfung wird hinter die Veröffentlichung verschoben.**

**Erforderliche Fähigkeiten, getrennt festzustellen:** `dir_fd`-Parameter für `os.mkdir`, `os.open`, `os.stat`, `os.rename` (`os.supports_dir_fd`); Deskriptor als `path`-Argument für `os.listdir` (`os.supports_fd`); `follow_symlinks=False` für `os.stat` (`os.supports_follow_symlinks`). Eine fehlende Fähigkeit löst `NotImplementedError` aus.

### 8.3 Betriebsmodell — Geltungsbedingung

Die Schlussfolgerungen von 8.2 gelten **ausschließlich** unter diesem Modell:

| Nr. | Regel | Verantwortlich | Durchsetzung |
| --- | --- | --- | --- |
| **BM1** | Jede A-Instanz verwendet ausschließlich ihre eigene Laufwurzel | A | konstruktiv im vorgeschlagenen Modell |
| **BM2** | Während des Aufrufs verändert kein weiterer Schreiber und kein Aufräumprozess die Laufwurzel oder das Laufverzeichnis | Betrieb | **organisatorisch, nicht technisch erzwungen** |
| **BM3** | Keine Wiederverwendung einer Laufwurzel | A | konstruktiv im vorgeschlagenen Modell |
| **BM4** | Kein Verschieben, Umbenennen oder Ersetzen der beteiligten Verzeichnisse während des Aufrufs | Betrieb | **organisatorisch, nicht technisch erzwungen** |
| **BM5** | Ergebnisbasis **und alle ihre Elternpfadkomponenten** werden während des Aufrufs weder umbenannt, ersetzt, umgehängt noch auf ein anderes Ziel geführt | Betrieb | **organisatorisch, nicht technisch erzwungen** |

**Verbindliche Einschränkung.** Das Verfahren darf die Zuordnung **nur unter einem vorab festgelegten und für den betreffenden Aufruf tatsächlich eingerichteten Betriebsmodell** als hinreichend behandeln. Ist eine erforderliche Voraussetzung **nicht hergestellt, ausdrücklich unklar oder erkennbar verletzt**, darf daraus **keine Veröffentlichungsfreigabe** abgeleitet werden.

**Die bloße Nennung von „Betrieb" in diesem Entwurf genügt nicht.** Vor einer späteren Nutzung müssen je Voraussetzung **verantwortliche Stelle, Geltungszeitraum und organisatorische Regel** konkretisiert sein. **BM2, BM4 und BM5 sind nicht erzwungene Annahmen; ein späterer Funktionstest beweist ihre Geltung nicht.**

Drei Ebenen bleiben getrennt: **konstruktive Trennung kooperierender Aufrufe** (BM1, BM3 — Eigenschaft des vorgeschlagenen Modells); **Betriebsannahmen** (BM2, BM4, BM5 — benannt, nicht erzwungen); **technisch erzwungene Zugriffstrennung** (nicht Gegenstand, keine Abwehr gegen privilegierte Akteure).

### 8.4 Reichweite des Spurkanals

**Ohne wirksame Begrenzung der Weitergabe lässt sich aus dem Kanal allein keine Beschränkung auf den ursprünglichen E-Prozess oder dessen Prozessbaum ableiten.** Ein Schreibdeskriptor kann auch an einen nicht verwandten Prozess gelangen.

| Vorgang | Wirkung | Close-on-exec |
| --- | --- | --- |
| Vererbung bei `fork` | Kind erhält eine Kopie | wirkt **nicht**, da erst bei `exec` |
| Explizite Deskriptorübertragung | beliebiger Prozess erhält Schreibzugriff | wirkt **nicht** |

**Vorgeschlagene Pflicht an E:** E gibt den Schreibzugriff auf den Spurkanal **an keinen anderen Prozess** weiter — weder durch Vererbung bei `fork` noch durch explizite Übertragung. Close-on-exec vor eigenen `exec`-Aufrufen ist eine **ergänzende**, keine hinreichende Maßnahme. **Vorgeschlagen, nicht angenommen, nicht qualifiziert.** Es wird keine Überwachungsarchitektur entwickelt.

Kein zusätzlicher Startbezug wird vorgeschlagen. Die Zuordnung stützt sich in diesem Verfahren auf die eigene Laufwurzel, den auf E begrenzten Schreibzugriff und die ausdrücklich genannten Betriebsannahmen. Die Geheimhaltung einer Nonce würde eigene, datenbezogene Weitergabepflichten erfordern; eine Nonce allein ersetzt die Pflicht zum Schutz des Schreibzugriffs nicht. Aus dem Verbot der Deskriptorweitergabe folgt keine Geheimhaltung eines Datenwerts.

### 8.5 Pfadauflösung — drei Situationen

| Situation | Leistung | Offen |
| --- | --- | --- |
| Öffnen eines **einzelnen Namens** relativ zu einem festgehaltenen Elterndeskriptor | nur eine Komponente; `O_NOFOLLOW` wirksam, Elternbezug festgehalten | — |
| **Erstmaliges Öffnen der Ergebnisbasis** über einen mehrteiligen absoluten Pfad | `O_NOFOLLOW` schützt nur die **letzte** Komponente | vorgelagerte Komponenten werden regulär aufgelöst; **keine allgemeine Symlink-Freiheit** |
| **Absoluter Laufwurzelpfad, den E erhält** | — | E löst ihn eigenständig und zu eigener Zeit auf; die Gleichheit mit A's Objekt folgt nicht aus A's Öffnen. Abgedeckt durch **BM5** und feststellbar durch 8.2 Schritt 13 |

### 8.6 Was ausgeschlossen wird — und was nicht

| Gegenstand | Stand |
| --- | --- |
| Verwechslung ordnungsgemäß arbeitender paralleler Aufrufe | unter BM1 und BM3 **im vorgeschlagenen Modell ausgeschlossen** |
| Übernahme eines Verzeichnisses aus einem früheren Aufruf | unter BM2 und BM4 ausgeschlossen. **Ohne sie** könnte ein bestehendes Verzeichnis nachträglich in die Laufwurzel bewegt werden; neu ist dann allein der Eintrag, nicht das Objekt |
| Zusätzliche Fremdeinträge, Namensabweichung | durch 8.2 Schritt 10 **erkennbar** |
| **Einzelner Fremdeintrag mit genau dem gemeldeten Namen** | **nicht erkennbar** |
| Konkurrierende Änderungen an Pfadkomponenten | **nicht ausgeschaltet**; durch 8.2 Schritte 12 und 13 nur **zu einem Zeitpunkt feststellbar** |

### 8.7 Fehlerfälle

| Fall | Was A feststellen kann | Veröffentlichung |
| --- | --- | --- |
| E scheitert vor der Verzeichnisanlage | kein Zuordnungsdatensatz bis zum tatsächlichen EOF; Laufwurzel leer | **nein** |
| Anlage gelingt, Zuordnungsnachricht fehlt | nach vollständigem Empfang: ein Eintrag, kein gemeldeter Name | **nein**; der Eintrag wird nicht übernommen |
| Falsche Zuordnung | Name unzulässig geformt oder Öffnen nach 8.2 Schritt 9 (c) scheitert | **nein** |
| Widersprüchliche oder mehrfache Zuordnung | zweiter Zuordnungsdatensatz, mehr als ein Eintrag oder Namensabweichung | **nein** |
| Bereits vorhandener Name der Laufwurzel | `FileExistsError` in 8.2 Schritt 2 | **nein**; E wird nicht gestartet |
| Bereits vorhandener Name des Laufverzeichnisses in E | bestehende Fresh-State-Regel greift in E; kein Zuordnungsdatensatz | **nein** |
| Gleichzeitige andere Ausführung | unter BM1/BM3 getrennt; ein Fremdeintrag nur nach 8.6 erkennbar | **nein**, sofern erkannt |
| **Prozessende beobachtet, Zuordnung noch nicht verarbeitet** | Prozessende allein ist **kein Befund** | **Entscheidung vertagt**: A empfängt und prüft weiter bis zum tatsächlichen EOF |
| **Nach vollständigem Empfang bis EOF fehlt die Nachricht oder ist ungültig** | abschließendes Empfangsergebnis liegt vor | **nein** |
| Abweichender Verzeichnisbezug nach 8.2 Schritt 12 oder 13 | Kennungsvergleich schlägt fehl | **nein** |
| **Erforderliche Betriebsvoraussetzung nicht hergestellt, unklar oder erkennbar verletzt** | Zustand des Betriebsmodells nach 8.3 | **nein** — keine Freigabe ableitbar |

**Prozessende ersetzt weder EOF noch die Auswertung bereits übertragener Nachrichten.** Eine fehlende Zuordnung wird nicht durch Verzeichnissuche, Vermutung oder Übernahme irgendeines vorhandenen Laufs ersetzt.

### 8.8 Veröffentlichungssperre

- **Solange die Zuordnung zur aktuellen Ausführung ungeklärt bleibt, veröffentlicht A keine `completion.json` in einem unzugeordneten Verzeichnis.**
- **Ist eine erforderliche Betriebsvoraussetzung nicht hergestellt, ausdrücklich unklar oder erkennbar verletzt, wird daraus keine Veröffentlichungsfreigabe abgeleitet.**
- Der Vorschlag, `completion.json` trotzdem technisch zu veröffentlichen und sie lediglich nicht als vollständigen Abschluss zu werten, wird **nicht übernommen**.
- In dieser Lage bleibt der Aufruf **unvollständig ohne Abschlussnachweis**; der äußere Rückgabewert folgt der bestehenden E3-Regel, soweit A regulär abschließen kann.
- Ein **`TECHNICAL_ERROR`-Abschluss bleibt nur bei zuverlässig zugeordneter Ablage und tatsächlich vorhandenen vorgeschriebenen Fehlerartefakten möglich.** **Ein technischer Fehlerstatus ist kein bestandener wirtschaftlicher Lauf.**
- **Es wird kein Abschlussnachweis vorgetäuscht**, wenn erforderliche Artefakte oder eine zugeordnete Ablage fehlen. A berechnet keine fachlichen Kennzahlen neu.

### 8.9 Betroffene Vertragsstellen

| Stelle | Vereinbarkeit |
| --- | --- |
| §2 Aufrufform | vereinbar; **Semantik von `--results-root` anzupassen** |
| §7.1 angenommene Pfadstruktur | **direkt betroffen**; mit Laufwurzel entstünde eine zusätzliche Ebene — **Anpassung erforderlich**, ebenso eine Auffindungsregel für spätere Leser |
| §7 regulärer Weg, Hashliste, Prüfung des fertigen Laufs | vereinbar, wirken innerhalb des Laufverzeichnisses |
| §7.6 `completion.json`, Artefaktliste relativ ohne `..` | vereinbar |
| BIND-3 | vereinbar, unverändert |
| BIND-1a und B1 | enthalten `--results-root` nicht; **keine neue Bindungsstufe**. Die **Ergebnisbasis einschließlich ihrer Elternkomponenten** ist als Startprofilparameter zu binden |

### 8.10 Verbleibende Grenzen

- **Das hier vorgeschlagene Verfahren beobachtet die exklusive Anlage durch `run_context` nicht unabhängig. Es setzt insoweit die Einhaltung der bestehenden E-Vertragspflicht voraus.**
- **Die Eindeutigkeitsprüfung erkennt nicht jede Verletzung von BM2**; ein einzelner, passend benannter Fremdeintrag bliebe unerkannt. **Es wird nicht behauptet, A könne jede Verletzung erkennen.**
- **Ohne die Weitergabepflicht nach 8.4 ist die Nachrichtenherkunft nicht auf den E-Prozess oder dessen Prozessbaum beschränkbar.**
- **Konkurrierende Änderungen an Pfadkomponenten werden nicht ausgeschaltet**; zwischen den Vergleichen und der Veröffentlichung bleibt ein Zeitfenster, das allein durch BM2, BM4 und BM5 abgedeckt ist.
- Keine dieser Grenzen wird als geschlossen ausgegeben; keine zusätzliche Abwehrmaßnahme wird vorgeschlagen.

### 8.11 Laufkennung und frühe Ereignisse

Relevante Ereignisse können **vor** der Anlage des Laufverzeichnisses entstehen; die angenommenen Regeln sehen ausdrücklich den Fall vor, dass nichts geschrieben wird und Ursache sowie Kennung auf die Standardfehlerausgabe gehen. **Relevante Ereignisse dürfen nicht allein wegen der Nachrichtenreihenfolge aus der Erfassung fallen.** Der Zuordnungsdatensatz nach 8.2 Schritt 7 ist deshalb **nicht** zwingend der erste Datensatz der Spur; die weitere Ausgestaltung gehört zum noch nicht ausgearbeiteten Spurschema.
