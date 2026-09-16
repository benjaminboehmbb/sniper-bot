# BTC-L1 G10-B Evaluator Packaging Draft V1

**DOCUMENT_STATUS=DRAFT_NOT_BINDING**

Vorgeschlagener späterer Dateiname: `BTC_L1_G10B_EVALUATOR_PACKAGING_DRAFT_V1_2026-09-16.md`

Datum der Ausarbeitung (UTC): 2026-09-16

Berichteter Repository-Stand der Ausarbeitung: `d49a563748a50695afd3ede3f3380ad4c390be41`, Branch `main`, genau ein Parent `fcc96713c9552731b940ca7aa67eabf381adc468`, keine Änderungen an getrackten Dateien und am Index. Zum Zustand des Arbeitsverzeichnisses siehe Abschnitt 9.

Eine maschinenlesbare Begleitdatei besteht für dieses Dokument **nicht**.

---

## 1. Zweck, begrenzter Umfang und Status

### 1.1 Zweck

Dieses Dokument hält den erarbeiteten Entwurfsstand zur **Paketierung des geplanten Evaluatorpakets** fest: Begründung der gewählten Distributionsform, vollständiger Konfigurationsentwurf, vorgeschlagene Prüfbedingungen sowie die dabei aufgedeckten offenen Bindungen und Vertragspräzisierungen.

### 1.2 Status

Das Dokument ist **DRAFT_NOT_BINDING**. Ausdrücklich gilt:

- **keine** formale Annahme dieses Entwurfs;
- **keine** Backend-Bindung — Hatchling ist ein Vorschlag, seine Version ist nicht gebunden;
- **keine** Runtime-Auswahl und keine bestätigte Python-Kompatibilität;
- **keine** Build-, Installations-, Test- oder Qualifikationsfreigabe;
- **keine** Erfüllung der Bindungen **B1 bis B14**;
- **keine** Manifestbindung;
- **D1 bleibt insgesamt offen.**

**Neu vorgeschlagene Paketierungswerte und zusätzliche Prüfbedingungen dieses Dokuments sind nicht angenommen. Wiedergegebene bestehende Vertragsvorgaben behalten ihren bisherigen Status; Quellenidentitäten und berichtete Prüfbefunde sind davon getrennt.**

### 1.3 Begrenzter Umfang

Gegenstand ist ausschließlich die **Paketierung der Projektdateien** des geplanten Evaluators. **Nicht** Gegenstand sind: die Implementierung der Evaluatormodule; das Interpreter- und Startprofil im Übrigen; die Abschlusskomponente A; die Beschaffung oder Bindung von Drittanbieterdistributionen; wirtschaftliche Regeln, die unverändert bleiben.

### 1.4 Unverändert gültige angenommene Regeln

Unverändert und hier **nicht erneut zur Genehmigung gestellt**: die Festlegungen **P01 bis P07**; **K01 bis K08** sowie sämtliche Serialisierungs-, Schema-, Gate-, Pfad-, Fresh-State- und Abschlussregeln des Output-/Runtime-Contracts; die Berechnungsregeln der Evaluator-Klarstellung; die Abschnitte 2 bis 8 des Field-/Helper-Contracts; die Selektions-Gates der Preregistration; die Entscheidungen **D4 bis D17** des Integrationsvertrags einschließlich der Bindungsstufen BIND-0 bis BIND-4 und der Runtime-Datei- und Importbindung nach dessen Abschnitt 10; der angenommene D2-Teilbefund. **V-19 zurückgestellt. B1 bis B14 offen. D2 und D3 offen.**

Ebenfalls unverändert fortbestehend sind die vier begrenzten D1-Teilannahmen — D1-Umfangspräzisierung, E2-Cachebewertung, E3-Verfahren, E1-Mengen- und Wegregel —, wie sie im D1-Konsolidierungsdokument festgehalten sind.

---

## 2. Quellen und berichtete Prüfstände

### 2.1 Herangezogene Quellen

| Quelle | SHA256 | Prüfstand |
| --- | --- | --- |
| `docs/review/BTC_L1_G10B_D1_PARTIAL_DECISIONS_V1_2026-09-16.md` | `d6d003e1e5224bed11fb0092150d7f96575f8c74b7f0e2d393b76e272ff57091` | bei der Ausarbeitung lesend bestätigt |
| `docs/review/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.md` | `12e2284cb65ce9b31ea39e03391dc543b3fbc7f88ef681ebb7ddf958c7837024` | bei der Ausarbeitung lesend bestätigt |

Herangezogen wurden aus dem Integrationsvertrag insbesondere Abschnitt 2 — Ablage, Aufrufform, Modultabelle, Abschlussregel „Keine weiteren Module und keine weiteren Artefakte" — sowie Abschnitt 10 mit Legacy-Helper-Zeile, Evaluator-Zeile, Dateimanifest, Importliste und Import-Allowlist.

### 2.2 Berichtete Repositoryfeststellungen

Die folgenden Angaben sind **berichtete frühere Feststellungen** und werden hier nicht als neue Prüfungen ausgegeben.

| Gegenstand | Feststellung |
| --- | --- |
| `live_l1/__init__.py` | vorhanden, 0 Bytes |
| `live_l1/core/__init__.py` | vorhanden, 0 Bytes |
| `live_l1/core/paper_economics.py` | vorhanden, 24 974 Bytes, SHA256 `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` — identisch mit dem in Abschnitt 10 des Integrationsvertrags gebundenen Erwartungswert |
| `live_l1/tools/__init__.py` | **nicht vorhanden** — `live_l1.tools` ist ein Namespace-Anteil |
| `live_l1/tools/g10b_evaluator/` | **nicht vorhanden** — geplante Komponente |
| Paketierungskonfiguration **im Repository-Wurzelverzeichnis** | `pyproject.toml`, `setup.py`, `setup.cfg`, `MANIFEST.in` **sämtlich nicht vorhanden**. Das bekannte Konfigurationsfragment unter `scratch/test_hatch/` ist hiervon nicht erfasst und separat in Abschnitt 9 dokumentiert |
| Lizenzartige Dateien | **keine** — weder versioniert noch im Arbeitsverzeichnis |

### 2.3 Externe Primärquellen

Herangezogen wurden die nachstehenden Seiten. Es werden keine Abrufzeitpunkte angegeben, und es wurde für diese Bereinigung keine neue Recherche durchgeführt. **Die dort genannten Versionsstände sind Referenzangaben und begründen keine Runtime- oder Backend-Auswahl.**

- https://docs.python.org/3.12/reference/import.html
- https://hatch.pypa.io/latest/config/build/
- https://hatch.pypa.io/latest/plugins/builder/reference/
- https://hatch.pypa.io/latest/plugins/builder/wheel/
- https://hatch.pypa.io/latest/config/metadata/
- https://packaging.python.org/en/latest/specifications/pyproject-toml/
- https://packaging.python.org/en/latest/specifications/binary-distribution-format/
- https://packaging.python.org/en/latest/specifications/recording-installed-packages/
- https://packaging.python.org/en/latest/specifications/direct-url/
- https://packaging.python.org/en/latest/specifications/entry-points/

---

## 3. Begründung der regulär installierten Projektdistribution

Verglichen wurden **zwei betrachtete Entwurfsvarianten**: **(a)** der gebundene Repository-Checkout, über eine reine Pfad-Konfigurationsdatei auf den Suchpfad gebracht, und **(b)** eine regulär installierte, ausdrücklich begrenzte Distribution ohne Editable-Installation. Eine Evaluatorinstallation besteht nicht.

**Vorgeschlagen wird (b).** Die Begründung ist eng zu fassen:

- Eine ausdrücklich begrenzte Distribution kann die **mitgelieferten Projektdateien auf eine benannte Liste reduzieren**.
- Sie vermeidet die zusätzliche Pfad-Konfigurationsdatei, die andernfalls den **gesamten Repositoriumsbaum** auf den Suchpfad legen würde.
- Der in Abschnitt 10 für `evaluator.roots` verwendete Begriff „Realpfad des Evaluator-Pakets" fügt sich einem festen Installationsort.

**Ausdrücklich nicht behauptet:** eine Installation materialisiert die Import-Allowlist **nicht** und macht die insgesamt erreichbare Modulmenge **nicht** mit der zugelassenen identisch. Sie sagt nichts darüber, was sonst auf dem Suchpfad liegt, welche Auflösung tatsächlich gewählt wird, ob die Wegpflicht eingehalten wird oder ob Ereignisnachweise vollständig sind. **Importauflösung, Wegpflicht und vollständige Ereignisnachweise bleiben eigenständige Anforderungen. Eine Installation ist kein D1-Nachweis.**

### 3.1 Namespace-Regel

`live_l1` ist ein **reguläres** Paket mit Initialisierungsdatei. Nach dem Importsystem wird beim Import eines Untermoduls der Suchpfad des **Elternpakets** verwendet; `sys.path` gilt nur für Top-Level-Importe. `live_l1.tools` wird daher ausschließlich unterhalb von `live_l1.__path__` gesucht. **Zusätzliche `sys.path`-Einträge liefern nicht automatisch weitere `tools`-Anteile**, sobald ein reguläres `live_l1` ausgewählt wurde.

`live_l1.tools` entsteht mangels Initialisierungsdatei als Namespace-Paket; sein Suchpfad wird neu berechnet, wenn sich der des Elternpakets ändert. **Ein einzelner Pfadanteil für `live_l1.tools` ist eine vorgeschlagene, später zu prüfende Bedingung — kein Effekt der Installation.** Es wird **keine** `live_l1/tools/__init__.py` ergänzt.

### 3.2 Legacy-Quellenort, Installationsort und geladenes Objekt

Abschnitt 10 des Integrationsvertrags bindet `legacy.paper_economics.path` mit dem Wert `live_l1/core/paper_economics.py` und dazu einen erwarteten SHA256; die Evaluator-Zeile derselben Tabelle spricht demgegenüber ausdrücklich vom „Realpfad".

Drei Größen bleiben zu unterscheiden: der **Quellenort** — die Datei am gebundenen Quellcommit —, der **Installationsort** — wo die Bytes zur Laufzeit liegen — und das **tatsächlich geladene Objekt**, das die angenommene Importliste über `file_path` als Realpfad und `file_sha256` erfasst.

**Die Lesart, die Legacy-Angabe sei eine Quellen- und Identitätsreferenz und lege nicht den Ausführungsort fest, ist eine vorgeschlagene Präzisierung und nicht angenommen.** Bestehende Vertragsfelder werden hier nicht umgedeutet.

---

## 4. Projekt-Dateiliste

Die Auswahl umfasst **21 Python-Dateien: 3 als vorhanden berichtete und 18 geplante.**

| Modul oder Paket | Quellpfad | Zustand | Installationspfad relativ zu site-packages | Begründende Vertragsstelle |
| --- | --- | --- | --- | --- |
| `live_l1` | `live_l1/__init__.py` | vorhanden, 0 Bytes | `live_l1/__init__.py` | §10 Allowlist-Zeile `live_l1`; `legacy.package_inits` |
| `live_l1.core` | `live_l1/core/__init__.py` | vorhanden, 0 Bytes | `live_l1/core/__init__.py` | §10 Allowlist-Zeile `live_l1.core`; `legacy.package_inits` |
| `live_l1.core.paper_economics` | `live_l1/core/paper_economics.py` | vorhanden | `live_l1/core/paper_economics.py` | §10 Legacy-Helper-Zeile; Allowlist „erlaubter Helper"; §2 einziger Legacy-Import |
| `live_l1.tools` | **keine eigene Datei** — Namespace-Anteil | vorhanden als Verzeichnis ohne Initialisierungsdatei | Verzeichnis `live_l1/tools/` **ohne** `__init__.py` | §10 Allowlist-Zeile `live_l1.tools` |
| `live_l1.tools.g10b_evaluator` | `live_l1/tools/g10b_evaluator/__init__.py` | geplant | `live_l1/tools/g10b_evaluator/__init__.py` | §2 Ablage |
| `…__main__` | `live_l1/tools/g10b_evaluator/__main__.py` | geplant | `live_l1/tools/g10b_evaluator/__main__.py` | §2 Aufrufform |
| `…run_context` | `live_l1/tools/g10b_evaluator/run_context.py` | geplant | `live_l1/tools/g10b_evaluator/run_context.py` | §2 Modultabelle |
| `…stream_reader` | `live_l1/tools/g10b_evaluator/stream_reader.py` | geplant | `live_l1/tools/g10b_evaluator/stream_reader.py` | §2 Modultabelle |
| `…event_parser` | `live_l1/tools/g10b_evaluator/event_parser.py` | geplant | `live_l1/tools/g10b_evaluator/event_parser.py` | §2 Modultabelle |
| `…field_grammar` | `live_l1/tools/g10b_evaluator/field_grammar.py` | geplant | `live_l1/tools/g10b_evaluator/field_grammar.py` | §2 Modultabelle |
| `…semantic_ledger` | `live_l1/tools/g10b_evaluator/semantic_ledger.py` | geplant | `live_l1/tools/g10b_evaluator/semantic_ledger.py` | §2 Modultabelle |
| `…numeric_context` | `live_l1/tools/g10b_evaluator/numeric_context.py` | geplant | `live_l1/tools/g10b_evaluator/numeric_context.py` | §2 Modultabelle |
| `…scenario_config` | `live_l1/tools/g10b_evaluator/scenario_config.py` | geplant | `live_l1/tools/g10b_evaluator/scenario_config.py` | §2 Modultabelle |
| `…stop_mapping` | `live_l1/tools/g10b_evaluator/stop_mapping.py` | geplant | `live_l1/tools/g10b_evaluator/stop_mapping.py` | §2 Modultabelle |
| `…scenario_account` | `live_l1/tools/g10b_evaluator/scenario_account.py` | geplant | `live_l1/tools/g10b_evaluator/scenario_account.py` | §2 Modultabelle |
| `…helper_gateway` | `live_l1/tools/g10b_evaluator/helper_gateway.py` | geplant | `live_l1/tools/g10b_evaluator/helper_gateway.py` | §2 Modultabelle |
| `…reconciliation` | `live_l1/tools/g10b_evaluator/reconciliation.py` | geplant | `live_l1/tools/g10b_evaluator/reconciliation.py` | §2 Modultabelle |
| `…metrics` | `live_l1/tools/g10b_evaluator/metrics.py` | geplant | `live_l1/tools/g10b_evaluator/metrics.py` | §2 Modultabelle, Sammelzeile |
| `…bootstrap` | `live_l1/tools/g10b_evaluator/bootstrap.py` | geplant | `live_l1/tools/g10b_evaluator/bootstrap.py` | §2 Modultabelle, Sammelzeile |
| `…gates` | `live_l1/tools/g10b_evaluator/gates.py` | geplant | `live_l1/tools/g10b_evaluator/gates.py` | §2 Modultabelle, Sammelzeile |
| `…artifacts` | `live_l1/tools/g10b_evaluator/artifacts.py` | geplant | `live_l1/tools/g10b_evaluator/artifacts.py` | §2 Modultabelle |
| `…errors` | `live_l1/tools/g10b_evaluator/errors.py` | geplant | `live_l1/tools/g10b_evaluator/errors.py` | §2 Modultabelle |

**Kennzeichnungen.** `live_l1.tools` besitzt keine eigene Datei und erhält auch keine. Die Dateinamen der geplanten Evaluatormodule sind aus den Modulbezeichnern der §2-Tabelle **abgeleitet**; die Tabelle nennt `metrics`, `bootstrap` und `gates` in **einer** Zeile, und eine konkrete Dateidarstellung ist an keiner Stelle des Vertrags festgelegt. Die drei Dateien sind daher eine **Gestaltungswahl**, keine Vertragsvorschrift.

**Abgrenzung.** Diese Liste ist **weder die vollständige SOURCE-Menge Z noch eine Festlegung von R oder O**. NumPy ist **nicht** Bestandteil dieser Liste. pandas wird nicht übernommen. **A bleibt außerhalb dieser Distribution** und wird nicht stillschweigend in den Evaluator integriert.

---

## 5. Vollständiger Konfigurationsentwurf

Vorgeschlagener Ablageort: `pyproject.toml` im **Repository-Wurzelverzeichnis**, weil die Quellpfade repository-relativ sind und gegen den Projektstamm aufgelöst werden. **Nebenwirkung, ausdrücklich benannt:** das Repository-Wurzelverzeichnis wird dadurch zum Projektstamm eines Build-Werkzeugs. Eine solche Datei existiert dort nicht; ihre Aufnahme ist ein Vorschlag.

```toml
# ENTWURF - VORSCHLAG_NICHT_ANGENOMMEN
# Ablageort (vorgeschlagen): <Repository-Wurzel>/pyproject.toml
# Hatchling ist Vorschlag; Version und Abhaengigkeiten sind NICHT gebunden.

[build-system]
requires = ["hatchling"]          # Version bewusst offen - noch nicht gebunden
build-backend = "hatchling.build"

[project]
name = "btc-l1-g10b-evaluator"    # ENTWURFSWERT, nicht gebunden
version = "0.0.0"                  # ENTWURFSWERT, nicht gebunden
description = "BTC-L1 G10-B evaluator package (draft, not binding)"

# Sachliche Deklaration der bekannten Laufzeitabhaengigkeit.
# KEINE Versionsgrenze: Kompatibilitaetsgrenzen sind nicht ermittelt.
# Die konkrete Versions- und Hashbindung erfolgt im Dependency-Lock (B10).
# Diese Deklaration ist KEINE Erlaubnis zur freien Aufloesung; die spaetere
# Installationsstrategie muss ungebundene Aufloesung verhindern.
dependencies = ["numpy"]

# requires-python: bewusst NICHT gesetzt.
#   Es wird keine Runtime ausgewaehlt; B5 ist offen.
#   Daraus folgt KEINE bestaetigte Python-Kompatibilitaet.

# license-files: bewusst NICHT gesetzt.
#   Im Repository existieren derzeit keine Lizenzdateien. Ob und nach
#   welchen Vorgaben das Backend solche Dateien automatisch aufnimmt,
#   konnte aus der konsultierten Konfigurationsseite nicht belegt werden
#   und ist gegen die spaeter gebundene Backend-Version zu bestimmen.

# Keine Entry Points deklariert. Daraus folgt keine Pflicht zu einer
#   entry_points.txt; eine etwaige werkzeugbedingte leere Datei ist
#   gesondert einzuordnen (siehe Abschnitt 6).

[tool.hatch.build.targets.wheel]
# Ausdrueckliche, datei-genaue Auswahl. Keine rekursive Paketsuche.
# 21 Eintraege: 3 vorhanden, 18 geplant.
only-include = [
  # --- vorhanden am berichteten Arbeitsstand (3) ---
  "live_l1/__init__.py",
  "live_l1/core/__init__.py",
  "live_l1/core/paper_economics.py",
  # --- geplant, existieren nicht (18) ---
  "live_l1/tools/g10b_evaluator/__init__.py",
  "live_l1/tools/g10b_evaluator/__main__.py",
  "live_l1/tools/g10b_evaluator/run_context.py",
  "live_l1/tools/g10b_evaluator/stream_reader.py",
  "live_l1/tools/g10b_evaluator/event_parser.py",
  "live_l1/tools/g10b_evaluator/field_grammar.py",
  "live_l1/tools/g10b_evaluator/semantic_ledger.py",
  "live_l1/tools/g10b_evaluator/numeric_context.py",
  "live_l1/tools/g10b_evaluator/scenario_config.py",
  "live_l1/tools/g10b_evaluator/stop_mapping.py",
  "live_l1/tools/g10b_evaluator/scenario_account.py",
  "live_l1/tools/g10b_evaluator/helper_gateway.py",
  "live_l1/tools/g10b_evaluator/reconciliation.py",
  "live_l1/tools/g10b_evaluator/metrics.py",
  "live_l1/tools/g10b_evaluator/bootstrap.py",
  "live_l1/tools/g10b_evaluator/gates.py",
  "live_l1/tools/g10b_evaluator/artifacts.py",
  "live_l1/tools/g10b_evaluator/errors.py",
]
exclude = [
  "**/__pycache__",
  "**/*.pyc",
]
# Kein "packages", kein "sources", kein "force-include":
#   Pfade sollen unveraendert als live_l1/... im Wheel erscheinen.
#   KEIN Eintrag live_l1/tools/__init__.py - live_l1.tools bleibt ohne
#   Initialisierungsdatei.
# Keine Build-Hooks.
```

### 5.1 Vier getrennte Ebenen

| Ebene | Stand |
| --- | --- |
| **Technische Erzeugung eines Archivs** | Nach der veröffentlichten Builder-Referenz verarbeitet die explizite Dateiauswahl die angegebenen Pfade, indem je Quelle geprüft wird, ob es sich um eine Datei oder ein Verzeichnis handelt; ein Fehler wegen nicht gefundener Pfade ist dort für **erzwungene** Einschlüsse dokumentiert, nicht für die explizite Auswahl. Eine Archiverzeugung trotz fehlender Projektdateien erscheint danach möglich. **Nicht durch Ausführung geprüft; versionsabhängig; keine Garantie aus ungeprüfter Backend-Version** |
| **Vollständigkeit des vorgesehenen Pakets** | **Nicht gegeben.** 18 der 21 gelisteten Dateien existieren nicht |
| **Nutzbarkeit des Evaluators** | **Nicht gegeben.** Ohne `__main__.py` und die Fachmodule ist die Aufrufform aus §2 nicht bedienbar |
| **Qualifikation** | **Nicht erbracht**, für keine Ebene |

Ein etwaiges Archiv enthielte neben den tatsächlich vorhandenen ausgewählten Projektdateien zusätzlich **generierte Metadaten**. **Eine tatsächlich festgestellte Archiv-Inhaltsliste wird nicht behauptet**; es wurde nichts gebaut.

### 5.2 Grenzen des Konfigurationsentwurfs

- Die Konfiguration beschränkt das **Wheel-Ziel**. Ein zusätzlich gebautes Quellarchiv benötigte eine eigene Beschränkung.
- Die Konfiguration bestimmt, was ausgewählt **werden soll**. Dass ein erzeugtes Artefakt genau diese Menge enthält, ist eine **spätere Prüfung** und folgt nicht aus der Konfiguration.
- Zwei Entwurfsentscheidungen sind offen und im Entwurf markiert: das Weglassen von `requires-python` und die Form der NumPy-Deklaration.

### 5.3 NumPy — drei getrennte Ebenen

| Ebene | Gegenstand | Stand |
| --- | --- | --- |
| Abhängigkeitsdeklaration | `dependencies = ["numpy"]` in den Projektmetadaten | im Entwurf gesetzt; sachliche Deklaration **ohne Versionsgrenze**; Kompatibilitätsgrenzen **nicht ermittelt** |
| Versions- und Hashbindung | Dependency-Lock mit exakten Versionen und Hash-Einträgen je Distribution | **offen (B10)**, ebenso die NumPy-Wurzeln (**B7**) |
| Gesteuerte Installation | Beschaffung ausschließlich aus den gebundenen Artefakten | **offen.** Muss ungebundene Auflösung verhindern; das Weglassen bekannter Abhängigkeiten ersetzt diese Steuerung nicht |

NumPy bleibt eine **separate Distribution** und wird nicht in das Evaluator-Wheel aufgenommen. Eine Installationsanweisung wird nicht gegeben.

---

## 6. Prüfbedingungen

Die Bedingungen dieses Abschnitts sind **neu vorgeschlagen und nicht implementiert**; sie sind nicht angenommen. Wiedergegebene bestehende Vertragsvorgaben — insbesondere die angenommene E2-Regel — behalten ihren bisherigen Status. Es wurde kein Prüfskript und kein Build-Hook erstellt.

| Phase | Prüfgegenstand | Vorgeschlagene Bedingung |
| --- | --- | --- |
| Vor dem Build | **Vollständigkeitsprüfung** der Dateiliste | Jeder der 21 gelisteten Pfade existiert; andernfalls **kein Build**. Damit wird die Lücke geschlossen, die aus der nicht fehlerauslösenden Verarbeitung fehlender Pfade entstünde |
| Vor dem Build | Gebundene Quellen | Jede vorhandene Datei bytegleich zur gebundenen Quelle; für den Helper zusätzlich Übereinstimmung mit dem in §10 gebundenen SHA256 |
| Vor dem Build | Backend- und Build-Umgebung | Backend-Version und transitive Build-Abhängigkeiten gebunden — **derzeit nicht gebunden** |
| Am Wheel | Projektdateien | Dateimenge **exakt** gleich der 21er-Liste; kein `live_l1/tools/__init__.py`; keine `__pycache__`- oder `.pyc`-Einträge |
| Am Wheel | `.dist-info/METADATA` | Im Wheel verpflichtend. Feldmenge und Werte gegen den Konfigurationsentwurf; `dependencies` erscheint als deklarierte Abhängigkeit ohne Versionsgrenze |
| Am Wheel | `.dist-info/WHEEL` | Verpflichtend; `Wheel-Version`, `Generator`, `Root-Is-Purelib`, `Tag` gegen die gebundene Build-Umgebung |
| Am Wheel | `.dist-info/RECORD` | Verpflichtend. Prüfung **in beide Richtungen**: jede Zeile gegen die tatsächliche Datei mit **Hash und Größe**, unabhängig neu berechnet; **jede Datei im Archiv ohne Eintrag** ist ein Befund. `RECORD` trägt **keinen Selbsthash** |
| Am Wheel | Lizenzdateien | Derzeit existieren **keine** im Repository. Ob das Backend solche automatisch aufnähme, ist gegen die gebundene Backend-Version zu klären und in die geschlossene Inhaltsliste aufzunehmen. Keine pauschale Zusatzfreigabe; es werden keine Lizenzdateien entfernt |
| Nach Installation | Python-Dateien unter `site-packages` | **Separat** zu prüfende Bytegleichheit zur jeweiligen Wheel-Datei und zur gebundenen Quelle — unabhängig vom RECORD |
| Nach Installation | `METADATA` | **Verpflichtend** vorhanden |
| Nach Installation | `RECORD`, `INSTALLER` | Nach der Spezifikation darf das Installationswerkzeug diese Dateien auslassen. Vorgeschlagen: ihr Vorhandensein **verbindlich fordern** |
| Nach Installation | `entry_points.txt` | **Keine pauschale Pflicht.** Der Entwurf deklariert keine Entry Points. Eine etwaige werkzeugbedingte leere Datei ist **gesondert einzuordnen** und weder pauschal zu fordern noch pauschal zuzulassen |
| Nach Installation | `direct_url.json` | **Normativ an den Anforderungstyp gebunden:** Es **MUSS** erzeugt werden bei Installation aus einer direkten URL-Referenz einschließlich VCS-URL, und es **DARF NICHT** erzeugt werden bei einem anderen Anforderungstyp, also Name plus Versionsangabe. Die konkrete Erwartung hängt vom **später festgelegten Installationsweg** ab und ist mit diesem gemeinsam zu binden |
| Nach Installation | `REQUESTED` | Gilt inzwischen als werkzeugspezifische Erweiterung; in die geschlossene Liste aufzunehmen oder auszuschließen |
| Nach Installation | Installiertes `RECORD` | **Getrennt** vom Wheel-RECORD zu prüfen. Es listet alle installierten Dateien einschließlich des `.dist-info`-Inhalts und des RECORD selbst; Einträge für `.pyc` und für RECORD tragen üblicherweise leeren Hash und leere Größe, `.pyc`-Einträge sind optional. Leere Felder sind spezifikationskonform und **kein** Prüfergebnis |
| Nach Installation | Weitere Dateien im `.dist-info` | **Geschlossene Liste vorab festlegen.** Zusätzliche installerspezifische Dateien werden **nicht pauschal** erlaubt; jede nicht gelistete Datei ist ein Befund |
| Nach Installation | `__pycache__` und `.pyc` | Behandlung **nach der angenommenen E2-Regel**: Cachezustand und Ausführungsbefund getrennt; Existenz und Hash allein sind kein positiver Ausführungsnachweis; ein Code-Digest belegt weder Cachenutzung noch Cacheverursachung |

### 6.1 Rollen

| Rolle | Gegenstand | Stand |
| --- | --- | --- |
| Build-Backend | Vorschlag Hatchling | Version **nicht gebunden** |
| Build-Abhängigkeiten | Inhalt von `[build-system] requires` samt transitivem Abschluss | **nicht gebunden** |
| Installer | Werkzeug, das das Wheel entpackt | **nicht gebunden**; bestimmt Zusatzdateien im installierten `.dist-info` |
| Runtime-Abhängigkeiten | NumPy | über §10-Wurzeln und Dependency-Lock, **nicht** über diese Distribution |

### 6.2 Übergreifender Vorbehalt

**`RECORD` ist kein unabhängiger Herkunfts- und kein Ausführungsnachweis** — es entsteht aus demselben Build wie die Dateien. Auch eine vollständig bestätigte Kette gebundene Quelle → Wheel-Datei → installierte Datei belegt **nicht** die Identität des tatsächlich ausgeführten Codeobjekts. **Bytegleichheit ersetzt keinen D1-Nachweis.**

---

## 7. Offene Bindungen, Vertragspräzisierungen und D1-Nachweise

### 7.1 Offene Bindungen

| Gegenstand | Art |
| --- | --- |
| Backend-Version und transitiver Abschluss der Build-Abhängigkeiten | fehlende Bindung |
| Automatische Lizenzdatei-Aufnahme des Backends | ungeklärt; gegen die gebundene Version zu bestimmen |
| Installationsweg und daran gebundene Erwartung an `direct_url.json` | fehlende Festlegung |
| Geschlossene Liste zulässiger Dateien im installierten `.dist-info` | fehlende Bindung |
| Identität des Installers | fehlende Bindung |
| Distributionsname und Version | Entwurfswerte, nicht gebunden |
| Kompatibilitätsgrenzen für NumPy; `requires-python` | nicht ermittelt |
| Startpfad und `pyvenv.cfg` zusätzlich zur Binäridentität | fehlende Bindung, **B5** |
| `site-packages`-Inhalt einschließlich Pfadkonfigurationsdateien und `sitecustomize` | fehlende Bindung |
| Wurzelkennung für die Standardbibliothek | fehlende Bindung |
| A: Identität und eigener Start | fehlende Bindung |
| **B6**, **B7**, **B8**, **B9**, **B10** | fehlende Bindungen |

### 7.2 Erforderliche Vertragspräzisierungen

| Gegenstand | Betroffene Stelle |
| --- | --- |
| Einordnung der `pyproject.toml` gegenüber „Keine weiteren Module und keine weiteren Artefakte" — eine Konfigurationsdatei ist kein Modul, die Zuordnung ist zu benennen | §2 |
| Basis der Auflösung von `legacy.paper_economics.path` und Verhältnis zum geladenen `file_path` | §10 Legacy-Helper-Zeile |
| Aufnahme von A als Komponente und der Ereignisspur als Artefakt; Übergang der Abschlussverantwortung | §2, §7, §15 |

### 7.3 Verbleibende D1-Nachweislücken

Ausdrücklich **nicht geschlossen**: das Bootstrap-Fenster einschließlich `site`, Pfadkonfigurationsdateien und `sitecustomize`; die tatsächliche Importauflösung und der Ausschluss von Verschattung; die Bedingung eines einzelnen Pfadanteils für `live_l1.tools`; die Durchsetzung der Wegpflicht; die Vollständigkeit von O; die durchgehende Wirksamkeit über das Intervall; EXTENSION-Module einschließlich der kompilierten Anteile von NumPy; native Ladebindungen. Für keinen dieser Punkte wird Erfüllung behauptet.

---

## 8. Unabhängiges Review und seine begrenzte Aussage

Die unabhängige Prüfinstanz **Antigravity** hat abschließend **APPROVE_FOR_DOCUMENTATION** ohne verbleibende Findings im geprüften Umfang festgestellt.

Ein zwischenzeitliches Finding, zusätzlich sei `packages = ["live_l1"]` erforderlich, wurde **ausdrücklich vollständig zurückgezogen**. Die vorhandene explizite Dateiauswahl genügt; eine `packages`-Ergänzung wird **nicht** vorgenommen.

**Reichweite des Reviews, ausdrücklich begrenzt:** es betraf den vorgelegten Konfigurationsentwurf und dessen Prüfbedingungen. Es prüfte **nicht** diesen Dokumenttext als eigenständiges Dokument, **keine** erzeugten Dokumentationsdateien und **keine** Implementierung.

**APPROVE_FOR_DOCUMENTATION ist keine formale Annahme**, keine Backend- oder Runtime-Bindung, keine Build- oder Installationsfreigabe und keine D1-Schließung.

---

## 9. Hinweis zur bekannten lokalen Abweichung

Das Arbeitsverzeichnis ist zum Zeitpunkt der Ausarbeitung **nicht vollständig sauber**. Es besteht genau eine bekannte untracked Datei:

| Pfad | Typ | Größe | SHA256 |
| --- | --- | --- | --- |
| `scratch/test_hatch/pyproject.toml` | reguläre Datei | 55 Bytes | `0d74d90c368d363c9520341fe82ddcf13c3e9e9ae55a36370f06eb629e2ee2f0` |

Es handelt sich um ein **untracked Konfigurationsfragment unbekannter Herkunft**. Sein Inhalt ist unvollständig und syntaktisch nicht wohlgeformt und entspricht nicht dem Konfigurationsentwurf aus Abschnitt 5.

**Die Datei ist nicht Bestandteil des unabhängig geprüften Konfigurationsentwurfs. Laut den Berichten wurde sie im Rahmen der beschriebenen lesenden Untersuchung und Textausarbeitung weder verändert noch ausgeführt. Ihre Herkunft und eine etwaige frühere Verwendung bleiben ungeklärt.**

In dem **begrenzt untersuchten Verzeichnis** wurden **keine Build-Artefakte** gefunden. **Daraus folgt kein Nachweis, dass niemals ein Buildversuch stattgefunden hat.** Es wird **keine Urheberschaft und keine Ausführung vermutet**.

---

## 10. Grenzen

Dieses Dokument ist **DRAFT_NOT_BINDING**. Es begründet **keine** formale Annahme, **keine** Backend- oder Runtime-Auswahl, **keine** Build-, Installations-, Test- oder Qualifikationsfreigabe und **keine** Ausführungsfreigabe jeder Art. Eine erfolgreiche Build-Prüfung wird **nicht** behauptet.

**Neu vorgeschlagene Paketierungswerte und zusätzliche Prüfbedingungen dieses Dokuments sind nicht angenommen. Wiedergegebene bestehende Vertragsvorgaben behalten ihren bisherigen Status; Quellenidentitäten und berichtete Prüfbefunde sind davon getrennt.**

**D1 bleibt offen.** Die vier begrenzten D1-Teilannahmen bestehen unverändert fort. **D2, D3, B1 bis B14, V-19 und X1 bleiben unberührt.** Die wirtschaftlichen Regeln bleiben unverändert.
