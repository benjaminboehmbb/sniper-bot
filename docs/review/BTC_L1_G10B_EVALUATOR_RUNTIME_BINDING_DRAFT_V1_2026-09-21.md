BTC-L1 G10-B — Evaluator Runtime Binding Draft
Konsolidierte Prüffassung, 2026-09-21

STATUS:
VORSCHLAG_NICHT_ANGENOMMEN.
D1 bleibt offen.
F1 ist nicht erbracht.
O bleibt nicht vollständig ableitbar.
Keine konkrete Runtime-Auswahl.
Keine formale Annahme dieses Entwurfs.
Keine Implementierungs-, Build-, Installations-, Test-, Qualifikations-, Runtime- oder Ausführungsfreigabe.

Dieser Text konsolidiert die Runtime-Binding-Ersatzfassung und die nachfolgenden Restkorrekturen. Er ist noch keine Repository-Datei. Die Konsolidierung vereinheitlicht Begriffe und beseitigt insbesondere folgende Überdehnungen:
- Offene Bootstrap-Abdeckung bedeutet nicht, dass A währenddessen keinerlei Prozess- oder Kanalereignisse beobachten könnte.
- pyvenv.cfg.home bezeichnet einen Bezug zur Basisinstallation und ersetzt keine Bindung einer konkreten Interpreterdatei.
- Die Identität von A ist für die Verlässlichkeit seiner Nachweisprüfung relevant.
- Unter -S wird die automatische site-Initialisierung unterdrückt; daraus folgt kein allgemeines Verbot ausdrücklicher späterer Imports.

0. STATUS, QUELLEN UND BELEGREICHWEITE

0.1 Kennzeichnung

[AV] Angenommene Vertragsvorgabe.
Grundlage ist die in B, §20, aufgezeichnete formale Annahme vom 2026-09-15. Sie umfasst die konkret ausformulierten neuen Vertragsfestlegungen der Abschnitte 2–12 und die Entscheidungen D4–D17.
Nicht geschlossen werden dadurch D1–D3 und die konkreten Bindungswerte B1–B14. V-19 bleibt zurückgestellt.
Die Annahme erteilt keine Implementierungs-, Qualifikations-, Test- oder Ausführungsfreigabe.

[AT] Bereits erteilte D1-Teilannahme, wie in A konsolidiert.
Betroffen sind D1-Umfangspräzisierung, E2, E3 sowie E1-Mengen- und Wegregel.
A berichtet die ursprünglichen Freigaben und Bestätigungen. Die unabhängige Verifikation der Originalfreigaben, Stufe (c), ist nicht erbracht.
Ihre Übernahme in die Vertragsunterlagen bleibt offen. Diese Dokumentations- und Verifikationslücken heben die berichteten Teilannahmen nicht auf.

[EW] Aussage eines früheren, nicht angenommenen Entwurfs.
Dies betrifft C–G sowie ausdrücklich nicht angenommene Vorschläge innerhalb A und B.

[NV] Neuer Vorschlag dieses Runtime-Binding-Entwurfs.

[BO] Berichteter Beobachtungsbefund mit Quellen- und Zeitbezug.
Er ist keine hier neu durchgeführte Live-Prüfung.

[OA] Organisatorische Voraussetzung, deren technische Durchsetzung nicht behauptet wird.

[OF] Offene Entscheidung, Ausarbeitung oder Qualifikation.

Externe Dokumentationsaussagen sind technische Quellenbefunde. Sie werden dadurch nicht zu angenommenen Projektregeln.

0.2 Annahmestatus von B

Der übermittelte Quellenbericht nennt für B:

- Dokumentkopf:
  DOCUMENT_STATUS=APPROVED_FOR_ADOPTION.
  Zusätzlich steht ausdrücklich, dass die formale Annahme in §20 aufgezeichnet ist und ältere Entwurfsformulierungen zeitlich eingeordnet werden.

- §1.1, Statuszuordnung:
  Die konkret ausformulierten neuen Vertragsfestlegungen einschließlich D4–D17 sind formal angenommen.
  D1–D3 bleiben offene Definitions- und Qualifikationsauflagen.
  B1–B14 bleiben offene konkrete Bindungen mit null-Werten.
  Daraus folgt keine Implementierungs- oder Auswertungsfreigabe.

- §20.1:
  Annahme aufgrund ausdrücklicher Nutzerfreigabe in der damaligen Konversation.
  Erfasst sind die konkret ausformulierten Regelungen der Abschnitte 2–12.

- §20.5:
  Abschnitte 2–12 und D4–D17: angenommen.
  D1–D3: offen.
  B1–B14: offen.
  V-19: zurückgestellt.
  Bestehende Berechnungsregeln und wirtschaftliche Gates: unverändert.

- §20.6 und §20.7:
  Keine Schließung fehlender Verfahren oder Nachweise und keine Freigabe zur Implementierung, Qualifikation, Auswertung oder Ausführung.

Die Begleit-JSON enthält:
decision = FORMALLY_ACCEPT_REVIEWED_EVALUATOR_INTEGRATION_CONTRACT
authority = EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION
accepted_decisions = D4_THROUGH_D17
date_utc = 2026-09-15
recorded_at_utc = 2026-09-15T16:03:52Z
implementation_authorized = false
qualification_authorized = false
evaluation_authorized = false

Die unabhängige Prüfung wird in B als vom Nutzer berichtet geführt:
review_source = INDEPENDENT_REVIEW_REPORTED_BY_USER
review_recommendation = APPROVE_FOR_FORMAL_ADOPTION
additional_full_rereview_claimed = false

Damit beruht die Einordnung als angenommen nicht allein auf dem Etikett APPROVED_FOR_ADOPTION, sondern auf der ausdrücklichen Annahmeaufzeichnung. Eine eigene Direktprüfung der damaligen Konversation wird hier nicht behauptet.

0.3 Annahmestatus von A

A trägt DOCUMENT_STATUS=DRAFT_NOT_BINDING.

Nach dem übermittelten Quellenbericht erläutert A:
- Dieser Status betrifft die Konsolidierung.
- Vier bereits erteilte Teilannahmen werden dokumentiert.
- Deren Status wird nicht aufgehoben.
- Stufe (a): ursprüngliche Nutzerfreigabe.
- Stufe (b): darauf folgende Bestätigung.
- Stufe (c): unabhängige Verifikation von (a).
- Stufe (c) ist für alle vier Teilannahmen nicht erbracht.
- Das Fehlen einer versionierten Vertragsfassung ersetzt nicht die erteilte Freigabe.
- Die vier Umfangsentscheidungen selbst sind getroffen; Dokumentation in den Vertragsunterlagen, Umsetzung und Nachweise bleiben offen.

A begründet keine neue Annahme und schließt D1 nicht.

0.4 Gebundene Quellenidentitäten

Alle Markdown-Pfade liegen unter docs/review/.

A:
BTC_L1_G10B_D1_PARTIAL_DECISIONS_V1_2026-09-16.md
33308 Bytes
SHA256 d6d003e1e5224bed11fb0092150d7f96575f8c74b7f0e2d393b76e272ff57091

B:
BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.md
94915 Bytes
SHA256 12e2284cb65ce9b31ea39e03391dc543b3fbc7f88ef681ebb7ddf958c7837024

C:
BTC_L1_G10B_EVALUATOR_PACKAGING_DRAFT_V1_2026-09-16.md
29228 Bytes
SHA256 aa10f1c33710abc5b90c27d8dd28e83f0d9e6eb50ba32be5dd8ced984b46695c

D:
BTC_L1_G10B_EVALUATOR_START_PROFILE_DRAFT_V1_2026-09-16.md
31931 Bytes
SHA256 3f1bd6a7cdb82c1652ab5f9426b4c15f28b20022d630dd36ee8a02b4782c78f4

E:
BTC_L1_G10B_EVALUATOR_RUN_DIRECTORY_BINDING_DRAFT_V1_2026-09-16.md
16926 Bytes
SHA256 9418dee2ba2ce0102ef7bcfc7dcb098668462e3c2bc4295c32fea414a0eae163

F:
BTC_L1_G10B_EVALUATOR_TRACE_PROTOCOL_DRAFT_V1_2026-09-16.md
45059 Bytes
SHA256 c06525785858ed131eac57dce5076c23a3c8b9f3aec06eb317c6a1ffd201c260

G:
BTC_L1_G10B_EVALUATOR_F1_EXECUTION_PROOF_DRAFT_V1_2026-09-21.md
39090 Bytes
SHA256 c2612fa5b91bb3cc273c8b0eede64b7a43035ae8fcb660949a3dc923d579df3c

J-A:
docs/review/evidence/BTC_L1_G10B_D1_PARTIAL_DECISIONS_V1_2026-09-16.json
62446 Bytes
SHA256 e3c049f0178b8d80552d55a2a124cdf65955a63dc04107345a5fa26a76d8863e

J-B:
docs/review/evidence/BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11.json
117990 Bytes
SHA256 b66cbfd5d794fc15c37f40cff2ab7fd5cfc6d454d57d1fd2ffa687d575fcc54c

Diese Identitäten wurden in den übermittelten lesenden Workstation-Berichten als geprüft gemeldet. Im letzten gezielten Durchgang wurden A, B und beide JSON-Identitäten erneut bestätigt; für C–G wird auf die vorhergehenden Prüfungen zurückgegriffen.

1. BERICHTETER REPOSITORY- UND INVENTARSTAND

1.1 Repository

[BO, Workstation-Berichte vom 2026-09-21]

Repository:
/home/workstation/jobs/btc-l1-fast-replay-v4-cert-20260902/repo

Branch:
main

HEAD:
8e3fd31b865039fea16187d836af39111988a0cc

Genau ein Parent:
8f9754ad1fe3b93f4fe916fe9403d33db6da1572

Index und getrackte Dateien unverändert.

Genau eine bekannte untracked Ausnahme:
scratch/test_hatch/pyproject.toml

Reguläre Datei, kein Symlink, 55 Bytes.
SHA256:
0d74d90c368d363c9520341fe82ddcf13c3e9e9ae55a36370f06eb629e2ee2f0

Das Arbeitsverzeichnis ist deshalb nicht vollständig sauber.

Das Fragment wurde nur hinsichtlich Typ, Größe und Hash geprüft. Sein Inhalt wurde nicht untersucht. Es gehört nicht zur operativen Konfiguration. Seine Herkunft wird nicht zugeschrieben. Es bleibt unverändert und wird weder entfernt noch gestagt, committet oder ignoriert.

Der zuletzt historisch bestätigte Remote-main entspricht dem genannten HEAD. Für diese Entwurfsphase wurde keine neue Remote-Prüfung durchgeführt.

X1 unter /home/benja/projects/sniper-bot blieb unberührt.

1.2 Paketierungsbestand

[BO]

Im untersuchten Repository-Wurzelverzeichnis wurden keine operative pyproject.toml, setup.py, setup.cfg, MANIFEST.in, poetry.lock, uv.lock, pdm.lock, Pipfile, .python-version, runtime.txt, tox.ini, noxfile.py oder Dockerfile vorgefunden.

In der geprüften Liste von 2117 getrackten Dateien wurden keine entsprechenden CI- oder Container-Rezepte gefunden.

requirements.txt enthält Entwicklungspins, unter anderem numpy==2.3.3 und pandas==2.3.3.
SHA256:
38a3bf4150f101355bd4517712f736b65dbd327f9a2302db8486fff9f772e51c

Die Einordnung dieser Datei als Entwicklungsvorgabe und nicht als Evaluator-Lock folgt aus B/§10 [AV].

requirements-rcc002-review.txt gehört zum RCC-002-Kontext.
SHA256:
756cc9e506ae4ee1a6f6c0507088b5cfc0dc8ba350fb2d2d46f1ffa72033adb6

Die Venv-Suche war auf Tiefe 4 begrenzt und ließ mehrere große Verzeichnisbäume aus. Sie beweist keine globale Abwesenheit einer virtuellen Umgebung. Auch ein gebundener Wheelhouse-Bestand wurde nur im untersuchten Umfang nicht vorgefunden.

1.3 Vorgeschlagene Auswahl von 21 Quelldateien

Die explizite Hatchling-Auswahl aus C bleibt [EW].

Vorhanden:
- live_l1/__init__.py
- live_l1/core/__init__.py
- live_l1/core/paper_economics.py

Die beiden __init__.py-Dateien sind leer.
SHA256 jeweils:
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

paper_economics.py:
24974 Bytes
SHA256:
a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae

Die 18 geplanten Evaluatordateien fehlen laut Bericht:

live_l1/tools/g10b_evaluator/__init__.py
live_l1/tools/g10b_evaluator/__main__.py
live_l1/tools/g10b_evaluator/run_context.py
live_l1/tools/g10b_evaluator/stream_reader.py
live_l1/tools/g10b_evaluator/event_parser.py
live_l1/tools/g10b_evaluator/field_grammar.py
live_l1/tools/g10b_evaluator/semantic_ledger.py
live_l1/tools/g10b_evaluator/numeric_context.py
live_l1/tools/g10b_evaluator/scenario_config.py
live_l1/tools/g10b_evaluator/stop_mapping.py
live_l1/tools/g10b_evaluator/scenario_account.py
live_l1/tools/g10b_evaluator/helper_gateway.py
live_l1/tools/g10b_evaluator/reconciliation.py
live_l1/tools/g10b_evaluator/metrics.py
live_l1/tools/g10b_evaluator/bootstrap.py
live_l1/tools/g10b_evaluator/gates.py
live_l1/tools/g10b_evaluator/artifacts.py
live_l1/tools/g10b_evaluator/errors.py

live_l1/tools/__init__.py fehlt; live_l1.tools darf nach dem Paketierungsentwurf Namespace-Paket sein.

Eine zusätzliche packages-Deklaration wird nicht allein wegen dieses Namespace-Anteils gefordert. Die explizite Auswahl bleibt maßgeblich.

Der vorgesehene vollständige Evaluator-Build ist mit den fehlenden Dateien nicht gegeben. Es wird weder ein erfolgreicher Build noch eine Installation behauptet.

1.4 Hostbeobachtungen und historische Hinweise

[BO, übermittelter Bericht vom 2026-09-21]

- Ubuntu 24.04.3 LTS.
- Kernel: Linux 6.6.87.2-microsoft-standard-WSL2.
- Architektur: x86_64.
- /usr/bin/python3 verweist auf python3.12.
- /usr/bin/python3.12:
  8020928 Bytes,
  SHA256 e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f.
- /usr/lib/python3.12 wurde vorgefunden.
- libpython3.12.so-Dateien wurden vorgefunden.
- Loaderpfad /lib64/ld-linux-x86-64.so.2 mit berichtetem Symlinkziel.
- libc.so.6 wurde mit 2129424 Bytes vorgefunden.
- Im aufgelisteten Verzeichnis /usr/lib/locale wurde C.utf8 gesehen.
- /usr/share/zoneinfo wurde vorgefunden.
- /usr/lib/python3/dist-packages und /usr/local/lib/python3.12/dist-packages wurden vorgefunden.
- An diesen geprüften Paketorten wurde NumPy nicht gefunden.

Der ältere Bericht in A/§9 bezeichnet den Interpreter als CPython 3.12.3 und enthält ELF-Befunde. Der aktuell berichtete gleiche Dateihash ist keine neue Ausführung zur Versionsbestimmung und keine neue vollständige ELF- oder Ladeprüfung.

Historische X1-Dokumente nennen andere Python- und NumPy-Versionen. Sie begründen keine Evaluator-Auswahl.

Aus dem Locale-Verzeichnislisting folgt keine vollständige Liste nutzbarer Locales. Insbesondere wurde die tatsächliche Akzeptanz eines späteren Locale-Werts nicht geprüft.

2. GETRENNTE RUNTIME-ROLLEN

R1 — äußerer Aufrufer von A.
[EW aus D]
Richtet Diagnosekanäle und Deskriptoren 0, 1 und 2 von A vor dessen Interpreterstart ein und bestimmt Startbefehl, Arbeitsverzeichnis und Umgebung.
Keine Interpretergleichheit mit einer anderen Rolle erforderlich.

R2 — Interpreter von A.
Rollenaufteilung und alleinige Veröffentlichung von completion.json beruhen auf E3 [AT]; konkrete Start- und Transportgestaltung bleibt [EW].
Benötigt eine eigene Interpreter-, Komponenten- und Abhängigkeitsidentität.
Muss R3 nicht gleichen.

R3 — Interpreter und virtuelle Umgebung von E.
Führt Evaluatorverarbeitung, BIND-3 und Artefakterzeugung durch.
BIND-3 ist [AV]; die vorgeschlagene isolierte Start- und Installationsgestaltung ist [EW].
Benötigt eigene Interpreter-, Venv-, Distributions- und Ladebindungen.

R4 — Build-Umgebung des E-Wheels.
Bindet Build-Frontend, Backend, benötigte Build-Abhängigkeiten und Eingabeartefakte [NV].
Keine pauschale Gleichheit mit R3.

Zwischen erzeugtem Wheel und R3 sind getrennt zu prüfen:
- kompatible Wheel-Tags;
- Sprach- und API-Kompatibilität des enthaltenen Codes;
- eine etwaige Requires-Python-Angabe;
- kompatible und gebundene Abhängigkeiten.

Ein passender Wheel-Tag beweist die übrigen Eigenschaften nicht. Ein py3-none-any-Wheel wurde noch nicht erzeugt oder geprüft.

R5 — vorgelagerte Sollableitung für BIND-2.
Leitet vorgesehene CODEID-1-Sollwerte aus gebundenen Quellbytes und Übersetzungsparametern ab [EW].
Die für diese Ableitung relevanten Compiler-, Codeobjekt- und Kodierungseigenschaften sind begründet zu binden [NV/OF].
Gleiche Interpreterartefakte wie bei R3 sind ein konservativer möglicher Vorschlag, aber keine bereits beschlossene allgemeine Gleichheitspflicht.

R6 — spätere Qualifikationsumgebung.
Der Bezug erfolgt je Qualifikationsgegenstand:
- E-/F1-Befunde zu R3;
- A-/Abschlussbefunde zu R2;
- Buildbefunde zu R4;
- Installationsbefunde zum Installationsverfahren und Ziel;
- Helper-Qualifikation zu den von B/§11 geforderten Identitäten [AV].

Keine pauschale Gleichheit der gesamten Qualifikationsumgebung mit E.

Es entsteht keine allgemeine Kopplung zwischen historischem Erzeugerlauf B3 und Evaluator-Runtime B5.

Nichtzirkularität:
Die Sollableitung muss vorgelagert aus den gebundenen Quellen und Parametern erfolgen. Eine Übernahme des zu prüfenden Istwerts ist kein Sollnachweis. Interpretergleichheit allein beweist Nichtzirkularität nicht.

3. INTERPRETERIDENTITÄT

3.1 Bindungs- und Beobachtungsebenen

[NV, soweit nicht ausdrücklich bestehendes Vertragsfeld]

Für A und E getrennt behandeln:
- Implementierung;
- vollständige Version einschließlich Patchstand;
- Bezugsquelle und Lieferweg;
- tatsächlich verwendete Interpreterdatei;
- SHA256, Dateigröße und aufgelöster Pfad;
- Startpfad und Symlink-/Kopie-Beziehung;
- gegebenenfalls gemeinsame Python-Bibliothek;
- Architektur, ABI, SOABI und Extension-Suffix;
- relevante Buildvarianten und Konfigurationsartefakte;
- Startoptionen und Übersetzungsparameter;
- tatsächliche Prozesspräfixe;
- Standardbibliothek und native Abhängigkeiten.

B/§10 sieht Interpreterpfad und Dateihash sowie bedingt eine gemeinsame Python-Bibliothek vor [AV]. Die konkreten Werte bleiben offen.

Dateibindung, Bezugsquelle und spätere Versions-Selbstauskunft bleiben getrennt. Selbstauskünfte ersetzen keine Dateibindung.

3.2 Statische Belege und spätere Prozesswerte

Dateien, Hashes, Symlinks, Paketmetadaten und tatsächlich vorhandene Build-Unterlagen können statisch untersucht werden.

Makefile, pyconfig.h und generierte Konfigurationsdateien können relevante Angaben tragen. Ihre Zuordnung zur konkreten Installation muss belegt werden; die bloße Existenz irgendeiner solchen Datei genügt nicht.

Dateinamen vorhandener Extension-Module beweisen nicht allein die ABI des verwendeten Interpreters.

Tatsächlich wirksame Präfixe, sys.path, sys.implementation, cache_tag und geladene Komponenten sind von statischen Angaben zu unterscheiden. Ihre Erhebung durch Interpreterausführung ist erst Gegenstand einer späteren Freigabe.

3.3 Versions- und Buildbezug

Die vollständige Versions- und Artefaktbindung wird aus dem begrenzten Geltungsbereich der Qualifikation begründet. Gleiche Versionszeichenketten garantieren keine vollständige Artefaktgleichheit.

Relevante Varianten werden auf ihren konkreten Einfluss geprüft:
- Debug-Build;
- Free-Threaded-Build;
- GIL-Konfiguration;
- threadlokaler Bytecode;
- weitere nachweisrelevante Build- oder Startkonfiguration.

-X presite ist ab Python 3.13 für Debug-Builds dokumentiert. Es wird nicht als allgemeine Bootstrap-Eigenschaft oder als ausgewählter Mechanismus verwendet.

-X tlbc ist ab Python 3.14 für Builds mit --disable-gil dokumentiert. Sein Vorhandensein beweist weder einen bestimmten co_code-Wert noch P-3.

-X gil ist versions- und buildabhängig; insbesondere ist gil=0 auf entsprechend konfigurierte Builds beschränkt. Kein Wert wird ausgewählt.

Die von CODEID-1 betroffenen Übersetzungsparameter, insbesondere filename, mode, flags, dont_inherit und optimize, bleiben von bloßen Interpreterversionsangaben getrennt.

CPU-Architektur bestimmt nicht sämtliche numerisch relevanten CPU-Eigenschaften. Eine etwaige NumPy-Auswahl unterschiedlicher CPU-Codepfade bleibt ein begrenzter Qualifikationspunkt. Eine vollständige CPU-Gleichheitspflicht wird nicht eingeführt.

4. A-RUNTIME

[EW aus D]
A ist als separate, möglichst stdlib-basierte Einzeldatei vorgesehen.
Startprofil: -I -B -S.
A gehört nicht in das E-Wheel.

[NV]
Getrennt zu binden sind:
- Interpreter von A;
- A-Datei mit Pfad, Größe und Hash;
- relevante Standardbibliotheks- und native Komponenten;
- Startoptionen, Umgebung und Diagnoseeinrichtung.

Die bisher benannte direkte stdlib-Nutzung umfasst os, subprocess, selectors beziehungsweise select, hashlib, json und sys.

Diese Liste ist kein vollständiger Importabschluss.

Getrennt bleiben:
- direkte Python-Imports;
- transitive Python-Imports;
- eingebaute und eingefrorene Module;
- dynamische Extension-Module;
- deren native Abhängigkeiten.

Für _socket besteht bisher kein benannter direkter Bedarf. Daraus folgt kein Nachweis, dass es transitiv nie geladen wird.

Für SHA256 wird ohne konkrete Build- und Ladebelege kein bestimmtes hashlib-Backend behauptet. Insbesondere ist „_hashlib/OpenSSL bereits im Interpreter“ kein belastbarer allgemeiner Befund.

-S unterdrückt die automatische site-Initialisierung. Es verhindert nicht allgemein spätere ausdrückliche Imports und entscheidet nicht allein über die Verwendung einer Venv.
Die Präfixinitialisierung ist versionsabhängig; ab Python 3.14 wird die Venv-Präfixsetzung während der Pfadinitialisierung vorgenommen.

R1 muss die vorgesehenen Diagnosekanäle bereits vor dem A-Interpreterstart einrichten [EW]. Eine Umleitung allein beweist keine vollständige oder erfolgreiche Speicherung.

Die eigene Hash- oder Versionsmeldung von A ist kein unabhängiger Nachweis des von A ausgeführten Codes.

Der Nachweis der A-Identität bleibt auszuarbeiten [OF]. Er ist für die Verlässlichkeit der Abschluss- und Nachweisprüfung relevant. Eine erfolgreiche E-Prüfung ersetzt ihn nicht.

5. E-RUNTIME UND VIRTUELLE UMGEBUNG

[EW]
E soll aus einer nicht editierbaren Wheel-Installation in einer isolierten virtuellen Umgebung laufen.
Kein Import des ungeprüften Checkout-Baums.
Keine Repository-.pth-Übernahme.
Kein Benutzer-Site-Zugriff.

Startprofil:
Interpreter der E-Venv, -I -B -m live_l1.tools.g10b_evaluator.
Die vertragliche Aufrufform enthält --manifest und --results-root [AV].
--trace-fd ist weiterhin ein nicht angenommener Erweiterungsvorschlag [EW].

E erhält kein -S, damit regulär installierte Pakete über site-packages erreichbar bleiben [EW].

[NV]
include-system-site-packages=false ist zu binden und später zu prüfen.

pyvenv.cfg wird als vollständige Datei mit Pfad, Größe und SHA256 sowie ihrer semantischen Auswertung behandelt. Die Beschreibung von home und include-system-site-packages in der Dokumentation ist kein abschließender Zwei-Schlüssel-Katalog.

Unterscheidbar bleiben:
- der an den Prozessstart übergebene Interpreterpfad;
- die aufgelöste tatsächlich gestartete Datei;
- deren Hash;
- die Basisinstallation und der zugehörige Basisinterpreter;
- Kopie oder Symlink;
- Venv-Pfad und Site-Packages-Pfade;
- sys.prefix, sys.exec_prefix, sys.base_prefix und sys.base_exec_prefix.

pyvenv.cfg.home stellt einen Bezug zur Basisinstallation her. Der Wert identifiziert nicht allein eine konkrete ausführbare Datei und ersetzt deren Pfad-/Hashbindung nicht.

-I enthält -E, -P und -s, aber nicht -S.
Die automatische site-Verarbeitung bleibt für E relevant.

Bei unverändertem regulärem site-Ablauf wird usercustomize unter -s nicht automatisch importiert. Ausdrückliche andere Imports und manipulierender Bootstrap-Code sind davon getrennte Wege.

sitecustomize bleibt relevant.
Ein passender ImportError kann dokumentiert ignoriert werden; aus dieser Sonderbehandlung folgt keine allgemeine Zusicherung erfolgreichen Fortsetzens bei beliebigen Ausnahmen.

.pth-Dateien können ausführbare Importzeilen enthalten.
Vorgeschlagen wird ein geschlossener, gebundener Bestand mit Pfad, Größe und Hash. Unerwartete Dateien sind gesondert zu behandeln.
Der tatsächlich relevante Suchumfang ist versions- und installationsbezogen zu bestimmen; keine pauschale Annahme genau vier vorhandener Verzeichnisse.

[OA]
Interpreter- und Installationsbäume sollen während des relevanten Zeitraums gegen unzulässige Änderungen geschützt sein. Verantwortliche, Zeitraum und Betriebsregeln sind noch zu konkretisieren. Eine universelle technische Durchsetzung oder vollständige TOCTOU-Abwehr wird nicht behauptet.

6. SYS.PATH, STARTPHASEN UND BOOTSTRAP

6.1 Pfadvergleich

[NV/OF]
Eine geordnete sys.path-Bindung wird vorgeschlagen. Die Vergleichssemantik ist noch festzulegen.

Getrennt:
- ursprüngliche Zeichenketten und Reihenfolge;
- Normalisierung;
- Symlinkauflösung;
- Existenz und Dateityp;
- zulässige Archive;
- erwartete, aber nicht vorhandene Pfade.

Python kann einen erwarteten ZIP-Pfad aufnehmen, obwohl das Archiv fehlt. Eine Liste ausschließlich existierender Realpfade wäre deshalb kein ungeprüft passendes Modell.

Eine Pfadliste allein beweist weder die Abwesenheit zusätzlicher Import-Hooks noch die vollständige bisherige Importgeschichte. Auch aus fehlendem Arbeitsverzeichniseintrag und fehlender Repository-.pth folgt kein vollständiger Checkout-Ausschluss.

Umgekehrt wird keine generelle Abwesenheit aller zusätzlichen Finder oder Loader gefordert. Entscheidend bleiben zulässige Wege und ihre Abdeckung.

6.2 Prozessbezogene Phasen

Die folgende Einteilung ist [NV]. Sie beschreibt Prüfzeitpunkte, ohne bereits einen vollständigen Kontrollmechanismus festzulegen.

Ph-0 — vor A-Start.
Akteur: R1.
Mögliche äußere Prüfungen von A-Datei, Interpreter, Umgebung, Rechten und Diagnoseeinrichtung.
Umfang und Nachweisweg bleiben [OF].

Ph-1 — Initialisierung von A.
Zwischen Start des A-Interpreters und Beginn des eigenen A-Codes.
-S unterdrückt die automatische site-Initialisierung; Interpreter- und Pfadinitialisierung bleiben.
Bootstrap-Intervall I-A.
Eine vollständige positive Erfassung der in diesem Intervall ausgeführten oder geladenen Identitäten ist nicht ausgearbeitet.

Ph-2 — A läuft, E ist noch nicht gestartet.
A kann vorgesehene statische Eigenschaften der E-Umgebung prüfen.
Mögliche Gegenstände: Interpreterdatei, pyvenv.cfg, installierter Bestand, .pth-Dateien und Laufwurzel.
Umfang [NV], Vollständigkeit [OF].
Solche Prüfungen können zum Unterlassen des E-Starts führen. Sie beobachten keine spätere Bootstrap-Ausführung.

Ph-3 — Initialisierung von E.
Zwischen Start des E-Interpreters und Beginn des festzulegenden eigenen Evaluator-Einstiegscodes.
Enthält Pfadinitialisierung und die vorgesehene site-Verarbeitung.
Bootstrap-Intervall I-E.
Die genaue Eintrittsmarke und Abdeckung bleiben [OF].

A läuft währenddessen bereits. Prozesszustand, Diagnosekanäle oder ein frühes Kanalende können beobachtbar sein. Daraus folgt jedoch kein vollständiger Identitäts- und Ausführungsnachweis für alle während I-E geladenen oder ausgeführten Komponenten.

Ph-4 — E-eigene Startprüfungen vor fachlicher Verarbeitung.
Hier liegt BIND-3 [AV].
Geprüft werden die vorgesehenen Identitäten und Bindungen sowie gegebenenfalls ergänzende Prozessbeobachtungen.
Diese Phase liegt nach dem betreffenden Bootstrap-Intervall und verhindert keine dort bereits erfolgte Ausführung.

Ph-5 — fachlicher Lauf und Abschluss.
BIND-4 [AV], E3-Prozess-/Kanalbeobachtung [AT], vorgeschlagene Spurverarbeitung [EW], Artefaktprüfung und Abschluss durch A.

6.3 Grenzen

Keine nachträgliche Prüfung schließt rückwirkend I-A oder I-E.

R1 kann vor A-Start Artefakte prüfen; A kann erst nach Beginn seines eigenen Codes eigene Prüfungen durchführen.
Die Zuordnung zwischen statisch geprüften Bytes und tatsächlich ausgeführtem oder geladenem Inhalt bleibt ein eigener Nachweisgegenstand.

Bootstrap-, Nachlade- und Shutdown-Abdeckung bleiben offen.
Die organisatorischen Voraussetzungen für unveränderte Dateien und eindeutige Pfade ersetzen keinen vollständigen technischen Nachweis.

7. BUILD, INSTALLATION UND PYTHON-ABHÄNGIGKEITEN

7.1 Build-Umgebung

[NV]
Zu binden sind:
- Build-Frontend;
- Hatchling-Version und Backend-Artefakt;
- tatsächlich erforderliche direkte und transitive Build-Abhängigkeiten;
- einschlägige Konfiguration;
- Eingabedateien;
- gebundener Artefaktbestand und Bezugsweg.

Eine ungebundene Netzwerkauflösung ist nicht vorgesehen.
Ein vollständiger Offline- beziehungsweise Wheelhouse-Bestand ist noch nicht gebunden.

Build-Werkzeuge gehören nicht automatisch zur E-Runtime.

Im vorangehenden Bericht wurde Hatchling 1.32.4, veröffentlicht am 2026-09-20, mit Requires-Python>=3.10 als zeitbezogene Referenz genannt. Dies ist keine Auswahl.
Auch berichtete direkte Abhängigkeiten ersetzen weder die Prüfung konkreter Artefaktmetadaten noch den vollständigen transitiven Abschluss.

7.2 Wheel und Installation

[NV]
Wheel-Dateiname, Größe und SHA256 sind gesondert zu binden.

Drei Ebenen bleiben getrennt:
- ausgewählte Projektquellen;
- erzeugter Wheel-Inhalt einschließlich Distributionsmetadaten;
- installierte Dateien.

Die vorgeschlagenen 21 Quelldateien sind keine Behauptung, das gesamte Wheel einschließlich Metadaten enthalte genau 21 Dateien.

WHEEL, METADATA und RECORD gehören zum Wheel-Metadatenbestand.
Die konkreten Metadaten und Tags sind erst am später erzeugten Artefakt prüfbar.

Wheel-RECORD und installationsseitiges RECORD sind getrennt zu behandeln.
Das installationsseitige RECORD kann bei der Installation verändert oder erzeugt werden.

RECORD ist kein unabhängiger Herkunfts- oder Ausführungsnachweis.
Die Wheel-Spezifikation und die allgemeine Installationsspezifikation haben unterschiedliche Anforderungen; deren jeweilige Ausnahmen sind zu beachten.

Nach der allgemeinen Installationsspezifikation können Hash- und/oder Größenfelder für jede Datei leer sein. Bei .pyc und RECORD selbst ist dies üblich. Ein leeres Feld ist kein erfolgreicher Prüfwert.

C sieht strengere Projektprüfungen für RECORD, INSTALLER und den zugelassenen Metadatenbestand vor [EW]. Diese Anforderungen werden nicht allein durch die allgemeine Spezifikation begründet.

direct_url.json ist an den Installationsweg gebunden. Seine Erwartung muss zusammen mit diesem Weg festgelegt werden.
REQUESTED ist als werkzeugspezifische Zusatzdatei gesondert zu behandeln.

Installeridentität, Installationsverfahren und zulässige zusätzliche Metadaten bleiben offen.

Eine Liste installierter Distributionen erfasst nicht automatisch alle importierbaren Dateien. Nicht registrierte Dateien und Dateimanifeste bleiben gesonderte Gegenstände.

7.3 NumPy

Keine konkrete NumPy-Version wird ausgewählt.

Der Entwicklungspin numpy==2.3.3 ist kein Evaluator-Lock [AV].
Die Python-Unterstützungsspanne dieses Pins wurde in den Berichten nicht verifiziert.

Die als Referenz gelesenen NumPy-2.5.0-Release-Notes nennen Python 3.12–3.14. Daraus folgt weder eine Auswahl noch die Eignung eines konkreten Wheels für den späteren Host.

NEP 29 beziehungsweise SPEC 0 sind Unterstützungsleitlinien und kein Artefakt-Kompatibilitätsnachweis.

[NV]
Zu binden:
- konkrete Distribution und Version;
- Bezugsquelle;
- Wheel-Datei und Hash;
- Interpreter-, ABI- und Plattform-Tags;
- relevante METADATA-Angaben;
- installierte .dist-info;
- installierter Dateibestand;
- tatsächlich erforderliche transitive Python-Abhängigkeiten.

Importname und Distributionsname bleiben unterschiedliche Identitäten, auch wenn beide numpy lauten.

Versionsangabe, Wheel-Identität, installierte Datei und tatsächliche Ladung dürfen nicht gleichgesetzt werden.

8. NATIVE ABHÄNGIGKEITEN

8.1 Getrennte Nachweisbereiche

N-SRC:
SOURCE-Modulausführung mit R, O und Z sowie Einzelnachweisen je Versuch.

N-EXT:
Identität und Herkunft tatsächlich geladener Extension-Module.

N-LIB:
Identität und Herkunft tatsächlich geladener nativer Bibliotheken.

Die native Initialisierung und Ausführung eines Extension-Moduls wird nicht durch den vorgeschlagenen F1-Nachweis für SOURCE-Codeobjekte vollständig abgedeckt.

Eine Lücke in N-EXT oder N-LIB lässt D1 offen. Daraus folgt nicht, dass sich die SOURCE-Menge O um native Bibliotheken erweitert oder ihr Nachweis automatisch unvollständig wäre.

8.2 Umfang

[OF/NV]
Gesondert zu behandeln:
- Extension-Dateien;
- direkt und transitiv geladene Shared Libraries;
- BLAS/LAPACK;
- dynamischer Loader;
- libc und weitere relevante Systembibliotheken;
- absolute Ladepfade;
- Dateihashes;
- Herkunft und Paketquellen;
- Lade- und gegebenenfalls Entladezeitpunkte;
- Bindung der gemeldeten Dateien an die tatsächlich geladenen Inhalte.

Die Wurzelkennung numpy.libs in B ist eine vorgesehene Dateimanifeststruktur [AV]. Sie beweist nicht, welche BLAS- oder sonstige Bibliothek tatsächlich geladen wird.

Statische ELF-Abhängigkeiten und installierte Dateien sind Inventarbefunde. Sie werden erst durch eine ausdrückliche Bindung zu Sollwerten und beweisen für sich keinen tatsächlichen Ladeverlauf.

Ein einzelner später Prozess-Snapshot beweist ohne zusätzlichen Abdeckungsnachweis nicht die vollständige Ladegeschichte.

8.3 Loader und Umgebung

Die dokumentierte Linux/glibc-Suche nach Bibliotheksnamen hängt unter anderem von RPATH/RUNPATH, Umgebung, Loader-Cache, Standardpfaden und dem konkreten Ladefall ab. Die Geltung von RUNPATH für direkte gegenüber transitiven Abhängigkeiten ist zu beachten.

Das Nichtsetzen von LD_LIBRARY_PATH im vorgesehenen geschlossenen E-Umgebungssatz entfernt diesen Umwelteinfluss für den entsprechend gestarteten Prozess. Es beseitigt nicht sämtliche anderen Such- oder Ladewege und ist keine allgemeine Loader-Garantie.

LD_DEBUG und LD_AUDIT werden nicht als Mechanismus ausgewählt und nicht ohne eigenen Abdeckungsnachweis als ausreichend behandelt.

8.4 Befundarten und Grenze

Getrennt:
- positiv erkannte unzulässige Ladung;
- fehlende oder unvollständige Erfassung.

Bei unvollständiger Erfassung können vorhandene Einzelbefunde bestehen bleiben; die vollständige Zulässigkeit aller Ladungen ist damit nicht bewiesen.

Die E1-/E3-Regeln zur Ereignisspur werden nicht ungeprüft auf sämtliche native Ladeereignisse übertragen.

D1 betrifft einen begrenzten Identitäts- und Herkunftsnachweis. Es wird keine universelle Speicherintegrität oder Abwehr beliebiger privilegierter Manipulation verlangt.

Bootstrap-, Nachlade- und Shutdown-Fenster bleiben offen. Kein nativer Erfassungsmechanismus ist implementiert oder qualifiziert.

9. BETRIEBSSYSTEM, PLATTFORM UND DATEISYSTEM

[NV]
Distribution und Versionsstand werden zunächst als Kontext aufgezeichnet. Keine pauschale harte Bindung jedes Hostmerkmals.

Architektur ist für Artefaktauswahl und ABI relevant und soll gebunden werden. Zusätzliche CPU-Einflüsse sind nach konkreter Bedeutung zu qualifizieren.

Loader und libc sollen als konkrete Artefakte mit Rollenbezug zu A beziehungsweise E behandelt werden. Derselbe Host beweist keine identischen Artefakte beider Prozesse.

Eine Kernel-Mindestbedingung wird nur aus tatsächlich benötigten Funktionen abgeleitet. Für die vorgesehene pidfd_open-Nutzung ist die dokumentierte Linux-Unterstützung relevant; eine Kernelversionsgleichheit wird nicht gefordert.

Dateisystemfähigkeiten:
Nicht die bloße Existenz von os.supports_dir_fd, os.supports_fd und os.supports_follow_symlinks ist entscheidend, sondern die jeweilige benötigte Funktion und Argumentform.

Aus E/§8.2 wurden insbesondere folgende Verwendungen berichtet:
- os.mkdir mit dir_fd;
- os.open mit dir_fd sowie O_DIRECTORY und O_NOFOLLOW;
- os.stat mit dir_fd;
- os.stat mit follow_symlinks=False;
- os.rename mit src_dir_fd und dst_dir_fd;
- os.listdir mit einem Verzeichnisdeskriptor als path.

Dieser Umfang ist gegen die tatsächlich gewählte A-Implementierung abzugleichen. Er wird nicht als bereits qualifiziert oder als automatisch vollständiger API-Abschluss behandelt.

NotImplementedError betrifft bestimmte nicht unterstützte Verwendungen. Eine fehlende Mitgliedschaft beim bloßen Prüfen einer Unterstützungsmenge löst ihn nicht von selbst aus.
Weitere Fehler, etwa OSError aufgrund von Rechten, Deskriptorzuständen oder Dateisystembedingungen, bleiben möglich.

Keine Probe wurde durchgeführt.

Locale-Verfügbarkeit und Namensakzeptanz bleiben vor Auswahl nachzuweisen.
Ein Verzeichnislisting ersetzt weder die Erfassung möglicher Locale-Archive noch eine spätere Prüfung des gewählten Werts.

Vorhandene Zeitzonendateien beweisen keine bestimmte aktive Prozesszeitzone.
Native Paketquellen sind aufzuzeichnen; ihre Herkunftsangabe ersetzt keine Dateibindung.

10. UMGEBUNG UND DETERMINISMUS

[EW aus D]
Der vorgeschlagene geschlossene Umgebungsvariablensatz für E enthält ausschließlich LC_ALL.

L1_EVAL_LC_ALL ist ein Bindungsparameter, keine zusätzliche weitergereichte Umgebungsvariable. Sein Wert ist offen.

Eine in D vorgesehene leere Umgebung ist eine vorab auszuwählende und zu qualifizierende Alternative. Sie ist kein automatischer Rückfall bei Verletzung eines bereits gebundenen Locale-Werts.

-I ignoriert PYTHON*-Umgebungsvariablen.
Eine Bindung über PYTHONUTF8 oder PYTHONHASHSEED wird unter diesem Startprofil nicht als wirksam vorgeschlagen.

[NV/OF]
-X utf8 wird als mögliche zusätzliche Startoption für A und E vorgeschlagen. Ohne Annahme ändern sich die bisherigen Startprofile nicht.

Die tatsächlich wirksamen Kodierungen und die Wechselwirkung mit der Locale müssen versionsbezogen behandelt werden. Explizite UTF-8-Serialisierung der Spur ist von allgemeinen Prozess- und Diagnosekodierungen zu unterscheiden.

Für den betrachteten normalen CPython-Kommandozeilenstart mit -I ist kein dokumentierter Kommandozeilenparameter zum Festlegen eines konkreten Hash-Seeds zugrunde gelegt.
Dies ist keine Aussage über sämtliche Einbettungs- oder programmatischen Konfigurationsmöglichkeiten.

-I wird nicht abgeschwächt.
Zunächst bleibt zu prüfen, ob ein vertraglich relevantes Ergebnis überhaupt einen festen Hash-Seed benötigt. Ein zufälliger Seed allein ist kein nachgewiesener Determinismusfehler.

TZ ist nicht im geschlossenen E-Satz enthalten.
UTC-Formatvorgaben für Vertragszeitstempel bleiben [AV]. Daraus wird keine pauschale Aussage über die gesamte Prozesszeitzone abgeleitet.

Native Thread-/BLAS-Einstellungen:
Im berichteten Suchumfang wurden keine einschlägigen Bindungen gefunden.
Eine Erweiterung des Umgebungssatzes wird ohne konkrete Notwendigkeit nicht vorgeschlagen.

Der betrachtete NumPy-Einsatz unter P07 umfasst die vertragliche Bootstrap-Verarbeitung. Ob native Threadzahl oder CPU-Codepfadauswahl relevante Ergebnisse beeinflussen, bleibt gegebenenfalls zu qualifizieren.

Der bestehende NumPy-Fehlerzustand unter P07 bleibt unverändert:
invalid=raise
divide=raise
over=raise
under=ignore

Decimal-Kontext, Berechnungsregeln und wirtschaftliche Gates werden nicht geändert.

Technische Determinismusanforderungen, vorhandene wirtschaftliche Regeln, mögliche Konfigurationen und offene Qualifikationen bleiben getrennt.

11. ANSCHLUSS AN F1 UND CODEID-1

11.1 Versionsbezug

sys.monitoring ist ab Python 3.12 dokumentiert.
Dies begründet eine Untergrenze für die betrachtete Variante L, aber keine konkrete Runtime-Auswahl und keine Qualifikation.

PY_START, PY_RETURN und die benötigten lokalen Monitoring-Schnittstellen sind für die betrachteten Python-Versionen dokumentiert. Ihre konkrete Eignung für den vorgesehenen Modulrumpf bleibt P-1 bis P-8 unterworfen.

Keine vollständige Gleichheit der Ereignislisten verschiedener Minor-Versionen wird behauptet.

free_tool_id:
Vor Python 3.14 deaktivierte dieser Aufruf Ereignisse und Callbacks nicht automatisch.
Ab Python 3.14 ruft er vor Freigabe clear_tool_id auf.
Dieser belegte Unterschied liegt zwischen Minor-Versionen. Er beweist keine konkrete Patchstandänderung und keine dauerhaft aktive Erfassung auf älteren Versionen.

11.2 Bevorzugte Variante L

[EW aus G]
Lokale Armierung:
PY_START | PY_RETURN.

Kein PY_UNWIND in Variante L.
Option G mit globalem PY_UNWIND bleibt nicht ausgewählt.

PY_START soll den positiven Eintrittsnachweis A2 tragen.
PY_RETURN dient der Kohärenzprüfung.

Zuordnung über starke Referenzen und linearen is-Vergleich.
Kein Rückgriff auf die verworfene threadlokale Audit-Stapelkorrelation.
Der Callback soll nicht DISABLE zurückgeben.

F-d bleibt offen:
Armierung nach einem Versuch beibehalten oder löschen ist nicht entschieden.

11.3 Nachweisgegenstände und Beobachtungsebenen

A1: Loader setzte den Aufruf mit C an.
A2: Interpreter trat tatsächlich in genau C ein.
A3: regulärer vollständiger Abschluss dieses Rahmens.
A4: Beendigung nach Eintritt durch propagierende Ausnahme.
A0: Fehler vor Eintritt.

F1 verlangt einen positiven A2-Nachweis auf O3 für genau C.
Kein eigenständiger A4-Nachweis wird durch Variante L gefordert.
Ein fehlendes Ereignis beweist A0 nicht.
Ein fehlendes PY_RETURN beweist A4 nicht.

O1: tatsächliches Interpreterereignis.
O2: Callback erzeugte und übergab den Datensatz an den Sendepfad.
O2 verlangt keine erfolgreiche Rückkehr dieses Übergabeaufrufs.
O3: A empfing den Datensatz vollständig, formgültig und innerhalb der gesiegelten Spur.

Nur unter den festgelegten Voraussetzungen:
O3 ⇒ O2 ⇒ O1.
Keine Umkehrung.
Erfolgreiche Übergaberückkehr und Zustellung sind unterschiedliche Tatsachen.

11.4 CODEID-1

[EW/OF]
CODEID-1 bleibt unvollständig.
Vorgesehen ist eine vorgelagerte Sollableitung aus gebundenen Quellbytes und Übersetzungsparametern.

Digestgleichheit wird unter kryptografischer Kollisionsannahme verwendet.
Sie beweist weder mathematische Darstellungsgleichheit noch Objektidentität oder tatsächliche Ausführung.

co_filename wird getrennt rekursiv an C und den über co_consts erreichbaren Codeobjekten geprüft.

G sieht Digestbildung vor Armierung vor. Das ist ein Entwurfsschritt, keine bereits angenommene neue Reihenfolgeregel.

CODEID-1 ist kein festgelegtes marshal-Verfahren.
Aussagen über Versionsinkompatibilität des marshal-Formats beweisen keine allgemeine R5=R3-Pflicht für eine andere Kodierung.

Erforderlich ist eine begründete Bindung der relevanten Compiler-, Codeobjekt- und Kodierungseigenschaften. Der genaue Umfang bleibt offen.

F-c:
- Die Python-3.12-Sprachreferenz führt co_linetable und co_exceptiontable nicht als dokumentierte Attribute.
- Daraus folgt nicht, dass diese Attribute in CPython fehlen.
- PEP 626 beschreibt co_linetable, legt aber kein stabiles, versionsübergreifendes Kodierungsformat fest.
- exceptiontable erscheint als Parameter der versionsabhängigen instabilen C-API.
- Daraus entsteht keine stabile Sprachgarantie für CODEID-1.
- Aufnahme und Typkodierung bleiben offen.

11.5 Offene Voraussetzungen

P-1:
PY_START für den über exec(C, ns) ausgeführten Modulrumpf.

P-2:
PY_RETURN für denselben Rahmen.

P-3:
Der benötigte co_code-Wert unter Spezialisierung und Instrumentierung.

P-4:
Verhalten bei Monitoring-Callback-Ausnahmen und Tragfähigkeit des vorgesehenen Abfangs.

P-5:
V-1 — höchstens ein aktiver Versuch je Codeobjekt.

P-6:
Tatsächlicher Aufruf des vorgesehenen exec mit genau C.

P-7:
Kein Modul aus Z schaltet das Werkzeug ab oder gibt es frei.

P-8:
Ununterbrochene Armierung und Aktivität im relevanten Intervall.

P-1 bis P-4 sind durch die hier herangezogenen Dokumentationsaussagen nicht hinreichend für den konkreten Nachweis belegt. Alle acht Voraussetzungen bleiben offen.

Eine Endabfrage beweist keine durchgehende Armierung.

Weitere Entscheidungen:
F-a Versionsbedingung.
F-b Werkzeugkennung und -name.
F-c CODEID-1-Attributumfang und Typkodierung.
F-d Armierung nach dem Versuch.
F-e mögliche Sollableitung durch A.
F-f Nachweisweg für V-1.
F-g Schemaführung von unregistered_entry und capture_status.
F-h Feldmenge und Wertebereiche von capture_status.
F-i etwaige Betrachtung von Option G.

11.6 Zähler und Berichte

[EW aus G]
callback_invocations zählt Callback-Eintritte.
observed_count zählt je Versuch nur erfolgreich zurückgekehrte Übergabeaufrufe.
unregistered_entries wird gesondert geführt.
callback_errors und send_failures müssen für einen positiven Nachweis null sein.
attempts_registered zählt registrierte Versuche.

Abweichungen sind sperrende Inkonsistenzen, beweisen aber für sich keinen bestimmten Datensatzverlust.
capture_status ist eine Erklärung von E und kein unabhängiger Intervallnachweis.

Keine dieser Eigenschaften wurde in dieser Phase getestet.

12. NACHWEISEBENEN UND VORGESCHLAGENE FELDBEZÜGE

12.1 Getrennte Ebenen

N1 — Vorab gebundener Sollwert.
Belegt die Erwartung, nicht deren Erfüllung.

N2 — Build-Artefakt.
Belegt den untersuchten Archivinhalt, nicht den installierten Zustand.

N3 — Installierte Datei.
Belegt Bytes an einem Ort und Zeitpunkt, nicht deren tatsächliche Verwendung.

N4 — Beobachtete Runtime.
Belegt einen Beobachtungszustand, nicht automatisch das ganze Intervall.

N5 — Importdatensatz.
Belegt die gemeldete Modul-/Dateizuordnung, nicht allein das ausgeführte Codeobjekt.

N6 — Positiver F1-Nachweis.
Soll unter seinen Voraussetzungen A2 für genau C belegen; nicht automatisch alle weiteren Versuche oder die Vollständigkeit von O.

N7 — Geladenes Extension-Modul.
Gesonderter Nachweisweg offen.

N8 — Geladene native Bibliothek.
Gesonderter Nachweisweg offen.

N9 — Von A empfangene Spur.
Belegt Transport- und Inhaltsbefunde nach den jeweiligen Voraussetzungen, keine eigenständige Beobachtung aller berichteten Ereignisse durch A.

N10 — Qualifikationsbefund.
Gilt innerhalb seines gebundenen Umfangs. Übertragung auf andere Artefakte erfordert eine begründete Geltungsprüfung.

12.2 SOURCE-Mengen und Cachegrenzen

[AT]
Z ist die zulässige SOURCE-Modulmenge.
R ist die vorab abgeleitete erforderliche Menge.
O ist die positiv nachgewiesene Menge ausgeführter SOURCE-Modulidentitäten.

Ziel:
R ⊆ O ⊆ Z.

Jeder Versuch bleibt einzeln relevant.
Ein positiver Versuch verdeckt keinen ungeklärten oder fehlgeschlagenen anderen Versuch.

Quellidentität, Übersetzungsparameter, Codeidentität und tatsächliche Ausführung bleiben getrennt.

Cache-Präsenz, Cache-Nutzung und Codeidentität bleiben getrennt.
-B verhindert automatische .pyc-Schreibvorgänge beim Import, nicht deren Lesen.
Kein pauschales Cacheverbot.
Keine pauschale Audit-Hook-Pflicht.

12.3 Feldbezüge

[NV, kein operatives Schema]

A:
- a.runtime für Interpreterartefakte und relevante Konfiguration;
- a.component für A-Datei;
- a.start_options;
- rollenbezogene Standardbibliotheks-, Loader- und native Artefaktverweise.

E:
- e.runtime für tatsächlich gestarteten Interpreter und relevante Konfiguration;
- e.venv für Basisbezug, Verknüpfungsart und pyvenv.cfg;
- e.start_options;
- e.sys_path_expected mit noch festzulegender Vergleichssemantik;
- e.pth_files;
- e.sitecustomize_state;
- rollenbezogene Standardbibliotheks-, Loader- und native Artefaktverweise.

Für Standardbibliotheksverzeichnisse sind Wurzelkennungen und zugehörige Dateimanifeste zu unterscheiden. Ein Verzeichnisname ist kein pauschaler Hash seiner Inhalte.

Gemeinsame Artefaktverweise sind zulässig, wenn die betreffende Identität übereinstimmt. Eine gemeinsame Basis ist keine Pflicht.
Bytegleiche Dateien an unterschiedlichen Orten bedeuten nicht automatisch dieselbe Pfad- oder Ladeidentität.

execution_proof- und codeid-Felder bleiben an die offenen Vorschläge aus G gebunden.

Bestehende Vertragsfelder werden nicht umgedeutet.
Die endgültige Schemaführung und die notwendigen Vertragsänderungen bleiben offen.

13. FEHLER- UND ABSCHLUSSFOLGEN

13.1 Bestehende und neue Regeln trennen

E-Interpreterabweichung:
BIND-3 vergleicht beim Evaluator-Start die gebundenen Identitäten [AV].
Die vorgesehene Abweichungsdiagnose ist IDENTITY_MISMATCH mit expected und observed.
Dies betrifft E und findet nach E-Start statt.

A-Identitätsabweichung:
Eine entsprechende vollständige Bindungs- und Vergleichsregel ist noch auszuarbeiten [NV/OF].
R1 könnte statische Befunde vor A-Start erheben; A-eigene Beobachtungen sind erst nach Beginn seines Codes möglich.
E-BIND-3 ist kein Ersatznachweis für A.

Abweichende pyvenv.cfg:
Neues Feld und Vergleichsregel vorgeschlagen; nicht bereits durch bloße Existenz von BIND-3 angenommen.

Ungebundene zusätzliche Distribution:
Geschlossener Bestand und dessen Fehlerregel vorgeschlagen.
MANIFEST_INCOMPLETE bei fehlenden Pflichtangaben ist nicht automatisch dieselbe Regel wie der Umgang mit zusätzlichem Bestand.

Wheel-/RECORD-Abweichung:
Die konkreten Prüfungen aus C sind Entwurfsvorschläge. Nicht als bereits vollständig angenommene Installationsprüfung darstellen.

Unzulässiger sys.path, unerwartete .pth oder sichtbare System-Site:
Vergleichsregeln und zulässiger Bestand bleiben zu binden.
Eine Feststellung nach E-Start verhindert keine bereits erfolgte Bootstrap-Ausführung.

Locale-Abweichung:
Vergleichs- und Fehlerregel offen.
Keine automatische Änderung der gebundenen Umgebung.

Fehlendes sys.monitoring:
Mit Variante L unvereinbar.
Eine konkrete technische Startfehlerregel ist noch auszuarbeiten.

Positiv erkannte unzulässige native Ladung:
Konkreter technischer Befund; Erfassung und genaue Fehlerbehandlung offen.

Unvollständige native Erfassung:
Keine Vollständigkeitsbehauptung und kein positiver gesamter D1-Nachweis.
Nicht mit einem wirtschaftlichen Fail gleichsetzen.

Diese Befunde können je nach Gegenstand vor dem betreffenden Prozessstart, während der Initialisierung, bei BIND-3, im Lauf oder im Abschluss auftreten. Die Phase ist keine Zusicherung, dass alle Fehler dort erkennbar wären.

13.2 Abschlussgrenzen

[AT beziehungsweise konkretisierende EW]

A startet vor E, empfängt die Spur fortlaufend und bleibt alleiniger Reaper von E.

A unterscheidet Prozessende und tatsächliches EOF:
- EOF vor Prozessende führt nicht zu Busy-Waiting; der betreffende Lesedeskriptor wird aus der Bereitschaftsüberwachung genommen.
- Prozessende vor EOF erfordert vollständiges Drain bis zum tatsächlichen EOF.

A bleibt alleiniger Herausgeber von completion.json.
E erzeugt Replay-, Reconciliation-, Metrik-, Gate- und Artefaktdaten.
A berechnet wirtschaftliche Metriken nicht neu.

Reguläres E-Ende ist notwendig, aber nicht hinreichend.
Signalbeendigung erlaubt keinen positiven Abschluss.
Wirtschaftlich valider Pass und wirtschaftlich valider Fail bleiben von technischen Fehlern getrennt.

Keine pauschale neue Berechtigung zum Veröffentlichen von TECHNICAL_ERROR.
Die bestehenden Voraussetzungen für zugeordnete Ablage und erforderliche Fehlerartefakte bleiben maßgeblich.

Bei ungeklärter Laufverzeichniszuordnung keine completion.json [EW aus E].
Ungewisse Veröffentlichungszustände werden nicht automatisch wiederholt.

Die Identität und Verlässlichkeit von A sind für seine Prüfung und Veröffentlichung relevant. Offene A-Bindungen werden weder durch E-Selbstauskünfte noch durch den bloßen Empfang einer Spur geschlossen.

13.3 Anschluss an Laufverzeichnis und Spur

[EW aus E und F]

A erzeugt unter einer gebundenen Basis eine frische eindeutige Wurzel.
E erhält --results-root und erzeugt darunter ein UUIDv4-Laufverzeichnis.

Verzeichnisdeskriptoren sowie O_DIRECTORY und O_NOFOLLOW dienen den jeweils festgelegten Prüfungen. Stabile Vorfahren, fremde Schreiber und Umbenennungen bleiben organisatorische Gegenstände; keine vollständige TOCTOU-Abwehr wird behauptet.

Die Weitergabe des vorgesehenen Schreibdeskriptors bleibt auf den definierten Prozessweg begrenzt. Keine Weitergabe über Nebenkanäle.
Eine Nonce ist kein Ersatz für Schreibzugriffsschutz.

Die Spur bleibt ein Vorschlag mit UTF-8-JSONL und LF-Rahmung, geschlossenen Feldern, lückenloser Sequenz, Pflicht-Header, Siegel und Aggregathash über die tatsächlichen Payloadbytes.
Kein Datensatz nach dem Siegel.
A liest bis zum echten EOF.

Grenzen für Nachrichtengröße, Anzahl und Gesamtbytes bleiben zu binden.
Ein gültiger Transport ersetzt keinen positiven F1-Erfassungsnachweis.
Der vorgeschlagene begrenzte Fehler-/Verwerfmodus erhält Prozess- und EOF-Beobachtung.
Eine trace_reference in completion.json bleibt Vorschlag.

14. ENTSCHEIDUNGSREGISTER

Die folgenden Punkte benennen Entscheidungen und Nachweise, keine bereits erteilten Freigaben.

RB-01 — konkrete Evaluator-Runtime B5.
Offen.
Auswahlkriterien:
passende CPython-/Monitoring-Eigenschaften, Wartungs- und Bezugsweg, identifizierbare Artefakte, kompatible NumPy-Wheels, benötigte A-/E-Schnittstellen und Durchführbarkeit der Qualifikation.
Keine Auswahl allein nach Neuheit oder lokaler Verfügbarkeit.
Wirkung: Voraussetzung der konkreten Sollableitung und Qualifikation.

RB-02 — Monitoring-Untergrenze.
Python mindestens 3.12 für die betrachtete Variante L vorgeschlagen.
Keine Aussage über erfolgreiche P-1/P-2-Qualifikation.

RB-03 — vollständige Versions- und Artefaktbindung.
Vorgeschlagen.
Begründung: begrenzter Geltungsbereich der Qualifikation.
Konkrete Werte offen.

RB-04 — Sollableitung R5.
Relevante Compiler-, Codeobjekt- und Kodierungseigenschaften binden.
Keine beschlossene allgemeine R5=R3-Identität.
Umfang abhängig von F-c und Übersetzungsparametern.
Nichtzirkularität zusätzlich erforderlich.

RB-05 — Interpreterdateien und gemeinsame Python-Bibliotheken.
Bestehende E-Felder vorhanden, Werte offen.
Startpfad, tatsächlich gestartete Datei, Basisbezug und bedingte Shared-Library-Bindung unterscheiden.
A-Bezug gesondert behandeln.

RB-06 — pyvenv.cfg.
Vollständige Dateibindung und semantische Auswertung vorgeschlagen.
Konkretes Schema und Werte offen.

RB-07 — sys.path.
Geordnete Bindung mit Vergleichssemantik vorgeschlagen.
Rohwerte, Normalisierung, Symlinks, Archive und nicht vorhandene erwartete Pfade unterscheiden.
Kein vollständiger Importwegbeweis allein durch diese Liste.

RB-08 — .pth und Customize-Zustand.
Geschlossener Bestand und Zustandsbindung vorgeschlagen.
Bootstrap-Abdeckung offen.

RB-09 — Standardbibliothekswurzeln.
Rollenbezogene Wurzelkennungen und zugehörige Dateimanifeste für A und E vorgeschlagen.
Keine Gleichheitspflicht.

RB-10 — libc und Loader.
Konkrete rollenbezogene Artefaktbindungen vorgeschlagen.
Transitive und tatsächliche Ladeabdeckung offen.

RB-11 — ABI, SOABI, Extension-Suffix, cache_tag und Buildvarianten.
Relevante statische Artefakte und tatsächliche Prozesswerte unterscheiden.
Genauer Bindungsumfang und Werte offen.

RB-12 — NumPy-Version und Artefakte.
Keine Auswahl.
Kompatibilität und transitive Abhängigkeiten anhand der später gewählten Artefakte prüfen.

RB-13 — Dependency-Lock und gebundener Artefaktbestand.
Konkreter Bestand, Beschaffungsweg und Installeridentität offen.
Keine ungebundene Netzwerkauflösung.

RB-14 — Build-Werkzeuge und Build-Abhängigkeiten.
Frontend, Backend und tatsächlicher transitiver Abschluss zu binden.
Nicht automatisch Teil der E-Runtime.

RB-15 — Build-/Runtime-Kompatibilität.
Tags, Sprache/APIs, Requires-Python und Abhängigkeiten getrennt prüfen.
Kein fertiges Wheel oder Kompatibilitätsnachweis vorhanden.

RB-16 — RECORD-Ebenen und .dist-info-Bestand.
Wheel- und Installationsbestand getrennt prüfen.
Strengere Projektanforderungen noch nicht angenommen.

RB-17 — Installationsweg und direct_url.json.
Gemeinsam festzulegen.
Weitere Installer-Zusatzdateien einschließlich REQUESTED ausdrücklich behandeln.

RB-18 — L1_EVAL_LC_ALL.
Wert offen.
Leere Umgebung nur als vorher ausgewählte und qualifizierte Alternative.
Keine automatische Laufzeitänderung.

RB-19 — UTF-8-Modus.
-X utf8 für A und E als neuer Startprofilvorschlag.
Ohne Annahme keine Änderung der bisherigen Startprofile.

RB-20 — Hash-Seed.
Kein fester Seed ausgewählt.
Keine Abschwächung von -I.
Zunächst Relevanz für vertragliche Ergebnisse klären.

RB-21 — native Thread-/BLAS-Einstellungen.
Keine Erweiterung des geschlossenen Umgebungssatzes ohne nachgewiesenen Bedarf.
Etwaige Ergebnisrelevanz später qualifizieren.

RB-22 — Identität und Start von A.
Eigene Komponenten-, Interpreter- und Abhängigkeitsbindungen erforderlich auszuarbeiten.
Keine Gleichsetzung mit E-Nachweisen.

RB-23 — --trace-fd.
Vorgeschlagene Änderung der Aufrufform.
Noch nicht vertraglich vollzogen.

RB-24 — --results-root und Pfadstruktur.
Vorgeschlagene Präzisierungen aus E bleiben offen.
Keine stillschweigende Änderung von B.

RB-25 — Betriebsvoraussetzungen.
Verantwortliche, Zeitraum und Regeln für Änderbarkeit, fremde Schreiber und stabile Zuordnung konkretisieren.
Organisatorische Voraussetzungen nicht als technisch bewiesen darstellen.

RB-26 — Dateisystemfähigkeiten.
Jede benötigte Funktion mit ihrer Argumentform qualifizieren.
Unterstützungsmengen allein sind kein vollständiger Funktionsnachweis.
Betriebsfehler bleiben möglich.
Wirkung: Laufzuordnung und Abschlussverfahren.

RB-27 — N-EXT.
Nachweisweg offen.
Wirkung: D1-Abdeckung der Extension-Module; keine Erweiterung von O.

RB-28 — N-LIB.
Nachweisweg offen.
Bootstrap, Nachladen und Shutdown ausdrücklich berücksichtigen.
Wirkung: D1-Abdeckung nativer Bibliotheken.

RB-29 — P-1 bis P-8.
Unverändert offen.
Keine Runtime-Tests in dieser Phase.

RB-30 — F-a bis F-i.
Unverändert offen.
Insbesondere F-c und F-d nicht vorentscheiden.

RB-31 — prozessbezogene Phasen und Bootstrap-Intervalle.
Ph-0 bis Ph-5 sowie I-A und I-E als Beschreibungsmodell vorgeschlagen.
Keine Behauptung vollständiger Beobachtung in den Bootstrap-Intervallen.
Prozess-/Kanalbeobachtung durch A davon unterscheiden.

RB-32 — Umgang mit A-Identitätsabweichungen.
Prüfakteur, Zeitpunkt, Vergleichsregel und Abschlussfolgen offen.
R1 kann vor A-Start statisch prüfen; A selbst erst nach Beginn seines Codes.
BIND-3 von E ersetzt dies nicht.
Wirkung: Verlässlichkeit der A-Prüfung und des Abschlusses, damit auch der von A bestätigten Nachweise.

15. QUELLEN

Die folgenden Primärquellen dienen der fachlichen Begründung beziehungsweise späteren versionsbezogenen Prüfung. Sie ersetzen weder gebundene Artefakte noch Laufzeitqualifikation.

Python Monitoring:
https://docs.python.org/3.12/library/sys.monitoring.html
https://docs.python.org/3.13/library/sys.monitoring.html
https://docs.python.org/3.14/library/sys.monitoring.html
https://peps.python.org/pep-0669/

Python Codeobjekte und Übersetzung:
https://docs.python.org/3.12/reference/datamodel.html
https://docs.python.org/3.14/library/functions.html
https://docs.python.org/3.14/library/importlib.html
https://docs.python.org/3.14/library/marshal.html
https://peps.python.org/pep-0626/#the-co-linetable-attribute
https://docs.python.org/3.12/c-api/code.html

Python Start, Venv und Konfiguration:
https://docs.python.org/3.14/using/cmdline.html
https://docs.python.org/3.14/library/site.html
https://docs.python.org/3.14/library/sys_path_init.html
https://docs.python.org/3.14/library/venv.html
https://docs.python.org/3.14/library/sysconfig.html
https://docs.python.org/3.14/library/os.html
https://docs.python.org/3.14/library/hashlib.html
https://devguide.python.org/versions/

Packaging:
https://packaging.python.org/en/latest/specifications/binary-distribution-format/
https://packaging.python.org/en/latest/specifications/recording-installed-packages/
https://packaging.python.org/en/latest/specifications/direct-url/
https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
https://hatch.pypa.io/latest/config/build/
https://pypi.org/project/hatchling/1.32.4/

NumPy:
https://numpy.org/doc/stable/release/2.5.0-notes.html
https://numpy.org/neps/nep-0029-deprecation_policy.html

Linux:
https://man7.org/linux/man-pages/man8/ld.so.8.html
https://man7.org/linux/man-pages/man1/locale.1.html
https://man7.org/linux/man-pages/man7/locale.7.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html

Versionsabhängige Aussagen gelten nur im jeweils belegten Umfang.
Aktuelle Dokumentation eines Minor-Zweigs ist keine eingefrorene Beschreibung jedes früheren Patch-Artefakts.

Offene Quellen-/Qualifikationspunkte:
- konkrete Evaluator-Versionen und Artefakte;
- genaue NumPy-2.3.3-Kompatibilität, falls dieser Kandidat überhaupt weiter betrachtet wird;
- vollständiger Build- und Runtime-Abhängigkeitsabschluss;
- tatsächliche Locale-Akzeptanz;
- vollständige native Ladeerfassung;
- sämtliche ausdrücklich offenen F1-Voraussetzungen.

16. ARBEITSUMFANG UND SCHLUSSSTATUS

Die übermittelten Workstation-Berichte melden für die Entwurfsarbeit:
- keine Änderung getrackter Dateien;
- keine Veränderung des bekannten Fragments;
- keine neue Dokumentdatei;
- keine Git-Remote-Abfrage;
- keinen Python-/Evaluatorlauf;
- keinen Build, keine Installation, keine Tests und keine Runtime-Qualifikation.

Ein früherer rein textverarbeitender awk-Einsatz wurde ausdrücklich offengelegt. Die damalige pauschale Aussage, kein sonstiger Sprachinterpreter sei verwendet worden, wurde berichtigt.
Dieser Einsatz wird nicht nachträglich autorisiert und nicht mit einem Python- oder Evaluatorlauf gleichgesetzt.
Die späteren Korrekturdurchgänge melden keinen awk-Einsatz.

Die Befehlslisten in AGENTS.md und CLAUDE.md wurden nicht als pauschale Pflicht zur Ausführung sämtlicher dort aufgeführter Befehle behandelt.

Die hier berichteten Prüfungen sind keine durch diesen Antigravity-Prüfauftrag bereits erbrachte unabhängige Verifikation.

SCHLUSSSTATUS:
VORSCHLAG_NICHT_ANGENOMMEN.
Keine neue formale Annahme.
D1 bleibt offen.
F1 ist nicht erbracht.
O bleibt nicht vollständig ableitbar.
B5 und die übrigen konkreten Bindungen bleiben offen.
Keine Runtime-Auswahl.
Keine Implementierungs-, Build-, Installations-, Test-, Qualifikations-, Runtime- oder Ausführungsfreigabe.
D2, D3, X1 und wirtschaftliche Regeln werden nicht wieder geöffnet.
Das bekannte Fragment bleibt unberührt.
