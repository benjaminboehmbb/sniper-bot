# BTC-L1 G10-B D2 Static Configuration Evidence V1

**DOCUMENT_STATUS=APPROVED_FOR_ADOPTION**

Die formale Annahme ist in Abschnitt 16 aufgezeichnet. Alle Abschnitte vor Abschnitt 16 sind im Wortlaut des geprüften Entwurfsstands belassen; ihre Entwurfs-, Vorschlags- und Offen-Vermerke werden durch Abschnitt 16 zeitlich eingeordnet und nicht umgeschrieben.

Datum der Ausarbeitung (UTC): 2026-09-15

Datum der Annahme (UTC): 2026-09-15

Repository-Stand der Ausarbeitung: `81df16686349c8e920981298cddb3e3ca0c9adea`, Branch `main`, Arbeitsverzeichnis sauber, keine untracked Dateien

Gebundener Quellcommit für alle Quellenaussagen: `3c5927127a03de13d8c80a720f5c8b97a2a36789`

Maschinenlesbare Begleitdatei: `docs/review/evidence/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.json`

---

## 1. Status, Umfang und Abgrenzung

### 1.1 Status

Dieses Dokument ist **DRAFT_NOT_BINDING**. Es enthält einen **begrenzten statischen Teilnachweis** zur offenen Definition **D2** des angenommenen Integrationsvertrags sowie einen **nicht angenommenen Vorschlag** für den Geltungsbereich von D2. Es ist **keine** formale Annahme, **keine** vollständige Schließung von D2, **keine** Qualifikation und **keine** Implementierungs-, Test-, Manifest-, Selektions-, Staging-, Commit-, Push- oder Ausführungsfreigabe.

Autorisiert ist ausschließlich die Erstellung dieser beiden Entwurfsdateien. Aus dieser Erstellungsberechtigung folgt keine weitere Freigabe. Dieser Bericht ist **noch nicht als Manifestnachweis gebunden**.

**Statuszuordnung nach der Annahme.** Die beiden vorstehenden Absätze beschreiben den geprüften Entwurfsstand und werden durch Abschnitt 16 zeitlich eingeordnet, nicht umgeschrieben. Der aktuelle Status ist **APPROVED_FOR_ADOPTION**: formal angenommen sind der dokumentierte statische Teilbefund nach Abschnitt 9 einschließlich seiner Quellenbindungen nach den Abschnitten 4 und 14, der korrigierten Zähleinheiten nach Abschnitt 5, der Schlüsseltabelle nach Abschnitt 6 und der ausdrücklich beschriebenen methodischen Grenzen nach Abschnitt 3.2, sowie die ausformulierte Abgrenzung des D2-Geltungsbereichs nach Abschnitt 10. **Nicht** angenommen und **nicht** geschlossen sind: die vollständige Schließung von D2; die Manifestbindung dieses Berichts; die Einführung eines noch nicht angenommenen Manifestfelds; die Schließung anderer offener Zuordnungen oder Bindungen. Aus der Annahme folgt **keine** Implementierungs-, Qualifikations-, Test- oder Ausführungsfreigabe.

### 1.2 Unverändert gültige angenommene Regeln

Unverändert und hier **nicht erneut zur Genehmigung gestellt**: die Festlegungen **P01 bis P07** des Parser-/Numeric-Contracts; **K01 bis K08** sowie sämtliche Serialisierungs-, Schema-, Gate-, Pfad-, Fresh-State- und Abschlussregeln des Output-/Runtime-Contracts; sämtliche Berechnungs-, Kosten-, Sizing-, Settlement-, Metrik- und Bootstrap-Regeln der Evaluator-Klarstellung; die Abschnitte 2 bis 8 des Field-/Helper-Contracts; die Selektions-Gates der Preregistration; die Entscheidungen **D4 bis D17** des Integrationsvertrags einschließlich der Bindungsstufen BIND-0 bis BIND-4, der Variablengruppen A und B nach dessen Abschnitt 9 sowie der Runtime-Datei- und Importbindung nach dessen Abschnitt 10. **V-19 bleibt zurückgestellt.** **B1 bis B14 bleiben offen.** **D1 und D3 bleiben offen** und werden durch dieses Dokument nicht bearbeitet.

Dieses Dokument ändert keine Vertragsregel, keine Berechnungsregel und kein Gate.

---

## 2. Präziser Geltungsbereich des Teilnachweises

Gegenstand ist die **Repository-Konfiguration am gebundenen Quellcommit** `3c5927127a03de13d8c80a720f5c8b97a2a36789`: die Vollständigkeit der Menge derjenigen Konfigurationsschlüssel, die im gebundenen Repository-Code gelesen werden, einschließlich statisch auflösbarer indirekter Weitergaben des Umgebungsobjekts.

**Ableitung des Umfangs.** Der geprüfte Umfang leitet sich aus dem Einstiegspunkt ab, nicht aus einer vorgegebenen Dateiliste: Ausgangspunkt ist der gebundene Runner `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` am gebundenen Quellcommit. Von dort wurde der **statisch ermittelte transitive Importgraph des Repository-Codes** gebildet — absolute, relative, mehrzeilige, aliasierte und Importe auf Funktions- und Klassenebene —, einschließlich der **Paketinitialisierungsdateien** und einschließlich aller statisch auflösbaren **Weitergaben des Umgebungsobjekts** über die tatsächliche Argument-Parameter-Zuordnung.

**Die Dateimenge ist ein Ergebnis, kein vorgegebenes Bestehenskriterium.** Die namentliche Datei- und Hashliste in Abschnitt 4 **dokumentiert das Ergebnis** dieser Ableitung; sie bestimmt nicht, welche Quellen geprüft werden müssen. Die ermittelte Anzahl von 45 Quelldateien ist ein Ergebnis und kein Sollwert; eine abweichende Anzahl wäre kein Fehler, sondern ein abweichendes Ergebnis.

**Nicht Gegenstand dieses Dokuments:** die tatsächlichen Werte und Zustände der Schlüssel (siehe Abschnitt 12); Einflüsse von Interpreter, Standardbibliothek und Drittanbieter-Abhängigkeiten (siehe Abschnitt 12); jede Aussage darüber, welche Module und Dateien ein späterer Prozess tatsächlich auflöst und lädt (dies ist D1 und bleibt offen).

---

## 3. Tatsächlich verwendete Analysemethode und ihre Grenzen

### 3.1 Methode

Alle historischen Quellen wurden ausschließlich über `git show` und `git cat-file blob` am gebundenen Quellcommit gelesen. Das Parsen erfolgte mit dem Standardbibliotheksmodul `ast` **ausschließlich im Speicher**. Es fand **kein** Import, **keine** Ausführung, **keine** Übersetzung des gelesenen Codes in Codeobjekte und **kein** Aufruf von Funktionen des gelesenen Codes statt. Es wurde keine Hilfs-, Temporär- oder Bytecode-Datei erzeugt.

**Importgraph.** Voller AST-Durchlauf über alle Verschachtelungsebenen jeder `.py`-Datei unter `live_l1` (78 Dateien am gebundenen Commit). Erfasst wurden `ast.Import` und `ast.ImportFrom` einschließlich mehrzeiliger Klammerform und `as`-Alias; relative Importe wurden über `level` und Paketkontext aufgelöst, wobei `__init__.py` als Paket selbst behandelt wurde. Ergebnisoffene Fixpunkt-Iteration: Kanten wurden ausschließlich **aus bereits erreichbaren** Modulen verfolgt; ein Import in einem nicht erreichbaren Modul macht sein Ziel nicht erreichbar. Zusätzlich erfasst: `__import__`, `importlib`, `import_module`, `find_spec`, `module_from_spec`, `exec_module`, `reload`, `load_module`, `find_module`, `pkgutil.iter_modules`, `walk_packages`, `exec`, `eval`, `compile` sowie Zugriffe auf `sys.modules`, `sys.meta_path`, `sys.path_hooks`, `sys.path_importer_cache` und `sys.path`.

**Umgebungszugriffe.** Erkennung der Ursprünge über `os.environ` und `os.environb` als Attribut auf jeden im jeweiligen Modul auf `os` gebundenen Namen, über `os.getenv` sowie über `from os import environ | environb | getenv` einschließlich `as`-Alias. Jede gefundene syntaktische Referenz wurde in eine **geschlossene Rollenmenge** klassifiziert: Methodenaufruf, Subscript (lesend und schreibend unterschieden), Mitgliedschaftstest, Iteration, Attributreferenz, Argumentübergabe, Zuweisung an einen Namen, Zuweisung an ein Objektattribut, Ablage in einem Container-Literal, Rückgabe, Parameter-Vorgabewert, Aufruf des Objekts selbst. Unklassifizierte Rollen wären als offen ausgewiesen worden.

**Weitergabeverfolgung.** Für jede Argumentübergabe wurde das Ziel aufgelöst — modulintern über die Funktionstabelle, modulübergreifend über die Importtabelle — und die **tatsächliche Argument-Parameter-Zuordnung** gebildet: nach Position über `posonlyargs` und `args`, nach Schlüsselwort über den Schlüsselwortnamen, mit gesonderter Behandlung von `*args` und `**kwargs`. Die Zuordnung erfolgte **namensunabhängig**. Der empfangende Parameter wurde zum Träger; alle seine Referenzen wurden erneut klassifiziert und weiterverfolgt, bis zum Fixpunkt.

**Schlüsselauflösung.** Stringliterale, modulweite Stringkonstanten, Schlüssel modulweiter Dict-Literale sowie indirekte Zugriffe über Hilfsfunktionen mit `key`- bzw. `name`-Parameter, aufgelöst über deren Aufrufstellen.

### 3.2 Grenzen der Methode

1. Die Analyse ist statisch. Sie deckt den Modulgraphen des festgelegten Quellbestands, nicht die Ausführung.
2. **Statische Erreichbarkeit unter Sollbedingungen ist kein Nachweis tatsächlicher historischer Ausführung.** Alle Erreichbarkeitsaussagen dieses Dokuments stehen unter den Sollwerten der Gruppen A und B und unter dem Vorbehalt, dass kein früherer Abbruch eintrat; sie sagen nichts darüber, welcher Codepfad im zertifizierten Erzeugerlauf tatsächlich durchlaufen wurde.
3. Die Erkennung der Ursprünge ist namensbasiert. Sie setzt voraus, dass das Umgebungsobjekt an seinem Ursprung als `os.environ`, `os.environb`, `os.getenv` oder über einen `from os import`-Alias benannt wird.
4. Ein fehlender Werkzeugtreffer ist ein Negativbefund der Suche und **kein Abwesenheitsbeweis**.
5. Re-Exporte und `__all__`-Ketten wurden nicht verfolgt; sie erweitern den Namensraum, nicht die Modulmenge.
6. Laden über C-Ebene, über einen ausgetauschten Lader oder über Mechanismen jenseits der in 3.1 genannten Formen ist von dieser Methode grundsätzlich nicht erfasst.
7. `sys.path`-Änderungen verändern, welche Datei einen Modulnamen trägt. Sie lassen die Modulmenge **des hier analysierten Graphen** unverändert; eine Aussage über tatsächlich aufgelöste und geladene Module eines späteren Prozesses folgt daraus **nicht**. Diese Frage ist D1 und bleibt offen.
8. Der Befund ist ein Auswertungsergebnis. Die angenommenen Verträge verlangen für D2 eine **statische Bestätigung** (Integrationsvertrag Abschnitt 9: „in der Qualifikation statisch zu bestätigen"); eine formale Verifikation wird von keinem angenommenen Vertrag verlangt und wird hier weder behauptet noch als neue Verpflichtung eingeführt.

---

## 4. Ergebnisliste: 45 Quelldateien mit Pfad, Bytes und SHA256

Ergebnis der Ableitung nach Abschnitt 2, am gebundenen Quellcommit `3c5927127a03de13d8c80a720f5c8b97a2a36789`. Pfade sind repository-relativ. Bytes und SHA256 beziehen sich auf den Blob-Inhalt am gebundenen Commit.

| Pfad | Bytes | SHA256 |
| --- | --- | --- |
| `live_l1/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/core/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/core/clock.py` | 2739 | `48b6a38936c1d624a41f25b1117ab64833d38fb44814fb6ff765712f9b074627` |
| `live_l1/core/execution.py` | 31600 | `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3` |
| `live_l1/core/feature_snapshot.py` | 3090 | `a6b5438212506d44427da96aa29ed95afcfb43313ef982fcc8f0c349f15d8097` |
| `live_l1/core/intent.py` | 8358 | `e052a11a04d1ae9b7d831e9d52175ee7fa8e212745ef43b22b94844a82ee4ece` |
| `live_l1/core/intent_fusion.py` | 7079 | `2b04f91c2273b7a9db941396d36e93b719edf3536e5e4e2a331ba5d169327114` |
| `live_l1/core/loop.py` | 50554 | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` |
| `live_l1/core/paper_economics.py` | 24974 | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` |
| `live_l1/core/paper_economics_shadow.py` | 16049 | `11efbde48db3026fb232c4f2a9e9b0aec347176c59293112d9fe68ddc8d4572c` |
| `live_l1/core/paper_economics_shadow_runtime.py` | 6101 | `8dbdf1ec0190e96bdb75697d1ffb25bd87784194150f674bb7e3317df6073a45` |
| `live_l1/core/paper_entry_throttle.py` | 26549 | `ad5447d88a2c35c9a71a5495c61c8f08fa844daf60e79d4a872234e88037df75` |
| `live_l1/core/paper_entry_throttle_profile.py` | 6559 | `9c07c23dd559aaddad640f269dd6394590c16cfbb7df439112a5c0dc0d0d5d87` |
| `live_l1/core/paper_iu4_adapter.py` | 24824 | `d65525f31746d1edf30bf1ffc7f84a845f97b3f4120904c9910b741bc8c76a7b` |
| `live_l1/core/paper_iu4_shadow_observation_gate.py` | 36377 | `ed4e75fad664c68b91950e9c09e873823ebe3eb0b0062f85806daa09ce661350` |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | 15298 | `f81045347e82b981bd721bf1c4bbe0133feb8a36146f6440358983cac2ad6d4e` |
| `live_l1/core/paper_iu4_startup_gate.py` | 37668 | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` |
| `live_l1/core/regime_detector.py` | 1425 | `278a7991bab6a7ecba030fb41d5d9122d9cb9417164da6d1bd91ac350c28ff54` |
| `live_l1/core/timing_5m.py` | 6761 | `59fd03511b9eb39d21f85a8bdca9ed57763924ab761ccf14866388f0fbfcdbf5` |
| `live_l1/guards/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/guards/guards.py` | 2872 | `e849ae12c790c41a01f649b26591881fcd105fa617af079becd3081557a1131f` |
| `live_l1/io/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/io/market.py` | 6118 | `014bbf7328c4bd354fb8a254979ef463670e49557c5ed89e5628a3b35dc8cd0e` |
| `live_l1/io/valid.py` | 3957 | `0f8c5af733269c76a93b112eff757c08f918676239196294c0bc7b02f2080d4b` |
| `live_l1/logs/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/logs/logger.py` | 2628 | `cbfb29708bc81bbf7f2d524abe10a21382213973f897038bc8c315bad1323cfd` |
| `live_l1/meta_state/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/meta_state/meta_state_runtime.py` | 406 | `da17467a9830464f70a508af8774be3acb1f644ca8423b97ff93300c9a0528b0` |
| `live_l1/meta_state/meta_state_shadow.py` | 1196 | `c2133dea056d29bc8d639943a8a754e6f39b0c91e131dba0923e69faa60379fa` |
| `live_l1/operational_profiles.py` | 1733 | `397080acebf83c2af4ecb4608183551665724fcb19e983442dcc15543b9d3704` |
| `live_l1/state/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `live_l1/state/iu4_lifecycle_ledger.py` | 18211 | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` |
| `live_l1/state/loss_cluster.py` | 18475 | `4ce7d59f64a67de94ffc6f1d03ff4e6c8a7a590802abb003b311cd0d56cc3e55` |
| `live_l1/state/models.py` | 5000 | `b9bc3b9a598fefeef83a2905432daf924ccf54e9701f313e2af99a6a8e833f53` |
| `live_l1/state/paper_artifacts.py` | 57620 | `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946` |
| `live_l1/state/paper_atomic_coordinator.py` | 262786 | `b8ce5ba89016cac8e34ee2646f3bf9746b2909fa3b7c9e1ef6c74557c3aaffcb` |
| `live_l1/state/persist.py` | 618 | `cc4c5f7e98905ffe2631330a1f03005a0897fdb43ad46a0b92191cc1cac2c274` |
| `live_l1/state/state_store.py` | 20999 | `b742131ba8af8e9c34157244de5cd743a045b7ae985dd4b502486e71fd2011c9` |
| `live_l1/state/state_validation.py` | 8224 | `5f0b0dc637c79339cea23e7a5676f8925c2b8ece1fb5151ece24854170a73778` |
| `live_l1/tools/reconcile_runtime_state.py` | 10799 | `8c9ecd43df1979e14af05640066a5a637690e0e3506106aeee3d17d504ab9222` |
| `live_l1/tools/recover_runtime_state.py` | 2994 | `9d164920de9c8e7518e71689805ce4493e5fb6f5b00802694d8ad53fe98a0c2c` |
| `live_l1/tools/replay_execution_state.py` | 3832 | `89284a7432aac82e6bb14a158c5a5b3c418fe8151a453b9fb684e90c82e9c874` |
| `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` | 7502 | `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292` |
| `live_l1/tools/safe_launch.py` | 7164 | `cb90bd49b36de56e8ad95e9b24febb23baa0513b1ec51e7402f63a5efd6ec652` |
| `live_l1/tools/startup_validator.py` | 3811 | `93f5cc2119887ae8dfa5a9ac5441a96de6dda4e0ac49ba4cce7dbe82cacd2017` |

**Konsistenzhinweis.** Die in Abschnitt 18 des angenommenen Integrationsvertrags per SHA256 gebundenen Dateien, die in dieser Ergebnisliste enthalten sind — `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`, `live_l1/core/loop.py`, `live_l1/core/execution.py`, `live_l1/core/paper_economics.py`, `live_l1/state/paper_artifacts.py`, `live_l1/logs/logger.py`, `live_l1/io/market.py` — tragen hier dieselben Werte.

**Ergänzende Ergebnisse der Graphbildung.** Die Ergebnisliste umfasst 21 Module mit mindestens einer ausgehenden `live_l1`-Importkante und 24 Module ohne eine solche Kante; `live_l1.tools` ist am gebundenen Commit ein Namespace-Paket ohne Initialisierungsdatei und erscheint deshalb nicht als Datei. Im gesamten Teilbaum `live_l1` wurde **kein** relativer Import gefunden. In der Ergebnisliste wurde **kein** dynamischer Importaufruf und **kein** Zugriff auf `sys.modules`, `sys.meta_path` oder `sys.path_hooks` gefunden; `sys.path`-Änderungen bestehen in `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py:24`, `live_l1/tools/safe_launch.py:15,16`, `live_l1/tools/reconcile_runtime_state.py:16,17` und `live_l1/tools/recover_runtime_state.py:13,14`. Nicht-`live_l1`-Importe auf Funktionsebene bestehen in `live_l1/core/loop.py:676` (`import json`), `live_l1/core/loop.py:713` (`import pandas`) und `live_l1/core/timing_5m.py:46` (`import ast`). Die drei Einstiegspunkte `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py:13`, `live_l1/tools/safe_launch.py:39` und `live_l1/tools/startup_validator.py:109` sind parameterlos (`def main() -> int:`).

---

## 5. Korrigierte, gegengeprüfte Zählung

### 5.1 Definition der Zähleinheiten

Gezählt werden **syntaktische Referenzen** im AST der 45 Quelldateien aus Abschnitt 4 — nicht Schlüssel, nicht Zeilen, nicht Laufzeitereignisse. Eine Referenz ist ein einzelner AST-Knoten, der das Umgebungsobjekt benennt.

| Einheit | Definition | Wert |
| --- | --- | --- |
| **Direkte Referenzen** | jeder AST-Knoten, der das Umgebungsobjekt unmittelbar über `os.environ` benennt | **39** |
| davon **Lesezugriffe** | Leserolle: Methodenaufruf `get`, lesendes Subscript, Mitgliedschaftstest, Iteration | **35** |
| davon **direkte Weitergaben** | Argumentübergabe an eine auflösbare Funktion | **3** |
| davon **Schreibzugriffe** | Schreibrolle | **1** |
| **Weitergaben aus Trägerparametern** | Argumentübergaben, die einen Trägerparameter benennen, nicht `os.environ` | **9** |
| **Weitergabestellen insgesamt** | direkte Weitergaben plus Weitergaben aus Trägerparametern | **12** |
| **Trägerbindungen** | Parameter, die das Umgebungsobjekt über die tatsächliche Argument-Parameter-Zuordnung empfangen; Einheit ist das Paar (Funktion, Parameter), nicht die Aufrufstelle | **5** |
| **Nicht auflösbare Weitergabepfade** | — | **0** |

Prüfidentität: 35 + 3 + 1 = 39. Prüfidentität: 3 + 9 = 12.

### 5.2 Ausdrückliche Erklärung der Überschneidung

Die **12 Weitergabestellen sind keine zusätzliche, von den 39 direkten Referenzen disjunkte Kategorie**. Die drei direkten Weitergaben sind bereits unter den 39 direkten Referenzen enthalten; lediglich die neun Weitergaben aus Trägerparametern liegen außerhalb der 39, weil sie einen Parameter und nicht `os.environ` benennen. Eine Addition von 39 und 12 wäre eine Doppelzählung.

Weitere abgeleitete Summen — namentlich eine Gesamtzahl der Trägerreferenzen, eine Gesamtzahl der Lesezugriffsstellen oder eine Gesamtzahl aller umgebungstragenden Referenzen — sind **nicht unabhängig bestätigt** und werden in dieses Dokument **nicht übernommen**. Sie sind für die Aussage dieses Teilnachweises nicht erforderlich.

### 5.3 Auflösung im Einzelnen

**Die drei direkten Weitergaben** (in den 39 enthalten):

| Stelle | Ziel | Zuordnung |
| --- | --- | --- |
| `live_l1/core/loop.py:876` | `load_runtime_shadow_settings` | Position 0 |
| `live_l1/tools/safe_launch.py:138` | `evaluate_iu4_shadow_runtime_gate` | Schlüsselwort |
| `live_l1/tools/safe_launch.py:164` | `evaluate_iu4_shadow_observation_gate` | Schlüsselwort |

**Die neun Weitergaben aus Trägerparametern** (nicht in den 39 enthalten): drei an `load_shadow_settings` in `live_l1/core/paper_economics_shadow_runtime.py:49`, `live_l1/core/paper_iu4_shadow_runtime_gate.py:272` und `live_l1/core/paper_iu4_shadow_observation_gate.py:853`; sechs an `_text` in `live_l1/core/paper_iu4_shadow_runtime_gate.py:233, 248, 291, 298, 299, 300`.

**Die fünf Trägerbindungen:** `load_runtime_shadow_settings.environment`, `evaluate_iu4_shadow_runtime_gate.environment`, `evaluate_iu4_shadow_observation_gate.environment`, `load_shadow_settings.environment`, `_text.environment`. Dass alle fünf Zielparameter `environment` heißen, ist ein Ergebnis der namensunabhängigen Zuordnung, nicht ihre Voraussetzung.

**Der einzige Schreibzugriff:** `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py:26`, `os.environ.update`.

### 5.4 Enumerierte Null-Befunde je Rolle

Jede der folgenden Klassen ist ein Zweig der geschlossenen Rollenmenge aus Abschnitt 3.1. Keine Referenz fiel in diese Zweige: Zuweisung an einen Namen; Zuweisung an ein Objektattribut; Ablage in einem Dict-, List-, Tuple- oder Set-Literal; Rückgabe des Umgebungsobjekts aus einer Funktion; Verwendung als Parameter-Vorgabewert; Zugriff aus einer verschachtelten Funktion auf einen Umgebungsträger; Übergabe über `*args` oder `**kwargs`; Argumentübergabe an ein nicht auflösbares Ziel; Attributreferenz außerhalb der klassifizierten Lesemethoden. Ferner wurde kein `from os import environ | environb | getenv`-Alias, keine `os.environb`-Referenz und kein `os.getenv`-Aufruf gefunden.

Diese Null-Befunde sind Ergebnisse einer Enumeration innerhalb der geprüften Rollenmenge. Sie sind **keine allgemeine Abwesenheitsbehauptung** (Abschnitt 3.2, Punkte 3, 4 und 6).

---

## 6. Vollständige Tabelle aller 39 Gruppe-B-Schlüssel

Die Spalte **Vorgabewert** nennt den **exakten Code-Vorgabewert des gebundenen Quellstands**. Relative Pfade sind Code-Vorgabewerte und **keine historischen Laufpfade**; die tatsächlich verwendeten Pfade sind Gegenstand von BIND-1b und B2 und in diesem Dokument unbekannt. Die Spalte **Erreichbarkeit** gilt unter den Sollwerten der Gruppen A und B und unter dem Vorbehalt, dass kein früherer Abbruch eintrat; sie ist nach Abschnitt 3.2 Punkt 2 **kein Nachweis tatsächlicher historischer Ausführung**.

| Nr. | Schlüssel | Quellstelle | Zugriffsweg | Erreichbarkeit | Vorgabewert | Nachgeschalteter Ersatz |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `L1_RESUME_AFTER_SNAPSHOT_ID` | `live_l1/io/market.py:181` | `os.environ.get` direkt, in `CSVMarketFeed.__init__` | erreicht; Konstruktion `live_l1/core/loop.py:972` | `""` | keiner |
| 2 | `L1_AUDIT_LOG_PATH` | `live_l1/tools/safe_launch.py:46` | `os.environ.get` direkt, `argparse`-Vorgabe | erreicht bei jedem Aufruf von `main()`, vor jeder Verzweigung | `"live_logs/execution_audit.jsonl"` | keiner |
| 2 | `L1_AUDIT_LOG_PATH` | `live_l1/core/loop.py:174` | `os.environ.get` direkt | erreicht nur bei `L1_STARTUP_RECOVERY` **und** `L1_STARTUP_RECONCILIATION_GATE` wahr | `os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl")` | keiner |
| 2 | `L1_AUDIT_LOG_PATH` | `live_l1/core/loop.py:212` | `os.environ.get` direkt | erreicht nur bei `L1_STARTUP_RECOVERY` wahr | `os.path.join(cfg.repo_root, "live_logs", "execution_audit.jsonl")` | keiner |
| 2 | `L1_AUDIT_LOG_PATH` | `live_l1/core/execution.py:300` | `os.environ.get` direkt, in `_resolve_audit_log_path` | erreicht auf dem Audit-Schreibpfad | `""` | `"live_logs/execution_audit.jsonl"` bei leerem Wert (`live_l1/core/execution.py:303`) |
| 3 | `L1_TRADE_LOG_PATH` | `live_l1/tools/safe_launch.py:48` | `os.environ.get` direkt, `argparse`-Vorgabe | erreicht wie Nr. 2 an `safe_launch.py:46` | `"live_logs/trades_l1.jsonl"` | keiner |
| 3 | `L1_TRADE_LOG_PATH` | `live_l1/core/loop.py:186` | `os.environ.get` direkt | erreicht wie Nr. 2 an `loop.py:174` | `os.path.join(cfg.repo_root, "live_logs", "trades_l1.jsonl")` | keiner |
| 3 | `L1_TRADE_LOG_PATH` | `live_l1/core/execution.py:319` | `os.environ.get` direkt, in `_resolve_trade_log_path` | erreicht **nur**, wenn kein Pfadargument übergeben wurde; die vorgelagerte Bedingung `live_l1/core/execution.py:316` prüft `trade_log_path` auf `None` beziehungsweise leeren Inhalt und kehrt andernfalls vor der Umgebungsabfrage zurück | `""` | `"live_logs/trades_l1.jsonl"` bei leerem Wert (`live_l1/core/execution.py:323`) |
| 4 | `L1_S2_POSITION_PATH` | `live_l1/tools/safe_launch.py:47` | `os.environ.get` direkt, `argparse`-Vorgabe | erreicht wie Nr. 2 an `safe_launch.py:46` | `"live_state/s2_position.jsonl"` | keiner |
| 4 | `L1_S2_POSITION_PATH` | `live_l1/core/loop.py:182` | `os.environ.get` direkt | erreicht wie Nr. 2 an `loop.py:174` | `os.path.join(cfg.repo_root, "live_state", "s2_position.jsonl")` | keiner |
| 5 | `L1_LOSS_CLUSTER_STATE_PATH` | `live_l1/tools/safe_launch.py:49` | `os.environ.get` direkt, `argparse`-Vorgabe | erreicht wie Nr. 2 an `safe_launch.py:46` | `"live_state/loss_cluster_state.json"` | keiner |
| 5 | `L1_LOSS_CLUSTER_STATE_PATH` | `live_l1/core/loop.py:178` | `os.environ.get` direkt | erreicht wie Nr. 2 an `loop.py:174` | `os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json")` | keiner |
| 5 | `L1_LOSS_CLUSTER_STATE_PATH` | `live_l1/core/loop.py:216` | `os.environ.get` direkt | erreicht wie Nr. 2 an `loop.py:212` | `os.path.join(cfg.repo_root, "live_state", "loss_cluster_state.json")` | keiner |
| 5 | `L1_LOSS_CLUSTER_STATE_PATH` | `live_l1/core/execution.py:84` | `os.environ.get` direkt, in `_loss_gate_state_path` | erreicht | `"live_state/loss_cluster_state.json"` | derselbe Wert über den `or`-Ausdruck derselben Zeile |
| 6 | `L1_LOG_PATH` | `live_l1/core/loop.py:268` | `os.environ.get` direkt, in `load_runtime_config`, gerufen `live_l1/core/loop.py:874` | erreicht | `os.path.join(repo_root, "live_logs", "l1_paper.log")` | keiner |
| 7 | `L1_TRADES_WINDOW_HOURS` | `live_l1/core/loop.py:281` | `_env_int(key, default)` mit `os.environ.get` in `live_l1/core/loop.py:150` | erreicht wie Nr. 6 | `6` | keiner |
| 8 | `L1_TEST_FORCE_BUY_EVERY` | `live_l1/core/loop.py:283` | `_env_int`, `live_l1/core/loop.py:150` | erreicht wie Nr. 6 | `10` | keiner |
| 9 | `L1_TEST_FORCE_SELL_EVERY` | `live_l1/core/loop.py:284` | `_env_int`, `live_l1/core/loop.py:150` | erreicht wie Nr. 6 | `15` | keiner |
| 10 | `L1_TEST_FORCE_WARMUP_TICKS` | `live_l1/core/loop.py:285` | `_env_int`, `live_l1/core/loop.py:150` | erreicht wie Nr. 6 | `0` | keiner |
| 11 | `L1_REQUIRE_WSL` | `live_l1/core/loop.py:932` | `_env_bool(key, default)` mit `os.environ.get` in `live_l1/core/loop.py:143` | erreicht, sofern die IU4-Zweige `live_l1/core/loop.py:880-926` nicht vorher zurückspringen; bei `L1_IU4_MODE=OFF` und `L1_IU4_SHADOW_OBSERVATION_ENABLED=0` tritt kein Rücksprung ein | `True` | keiner |
| 12 | `L1_SIGNAL_WEIGHTS_JSON` | `live_l1/core/intent.py:51` | `os.environ.get` direkt, in `_load_l1_signal_weights`, gerufen `live_l1/core/intent.py:72` aus `_normalize_score`, gerufen `live_l1/core/intent.py:247` | erreicht je Tick, sofern `tick_id > cfg.test_force_warmup_ticks` und `cfg.test_force_intents` falsch | `""` | keiner |
| 13 | `L1_INTENT_DEBUG` | `live_l1/core/intent.py:142` | `os.environ.get` direkt, in `_debug_enabled`, gerufen `live_l1/core/intent.py:155` aus `_debug_log_line`, gerufen an `live_l1/core/intent.py:197, 216, 227, 237, 287` | erreicht je Tick über `live_l1/core/intent.py:287`; die Aufrufe an `197, 216, 227, 237` liegen in unter den Sollwerten nicht genommenen Zweigen | `""` | keiner |
| 14 | `L1_IU4_APPROVED_THROTTLE_PROFILE` | Konstante `live_l1/core/paper_iu4_shadow_runtime_gate.py:29`; Lesestelle `live_l1/core/paper_iu4_shadow_runtime_gate.py:147`; Aufruf `live_l1/core/paper_iu4_shadow_runtime_gate.py:248` | `_text(environment, name)` über die Trägerkette ab `live_l1/tools/safe_launch.py:138` | **nicht erreicht**; Rücksprung `live_l1/core/paper_iu4_shadow_runtime_gate.py:233-234` bei `L1_IU4_MODE` gleich `MODE_OFF` | `""` | keiner |
| 15 | `L1_IU4_REPOSITORY_COMMIT` | Konstante `live_l1/core/paper_iu4_shadow_runtime_gate.py:32`; Lesestelle `:147`; Aufruf `:291` | wie Nr. 14 | **nicht erreicht** wie Nr. 14 | `""` | keiner |
| 16 | `L1_IU4_ATOMIC_STATE_DIRECTORY` | Konstante `live_l1/core/paper_iu4_shadow_runtime_gate.py:28`; Lesestelle `:147`; Aufruf `:298` | wie Nr. 14 | **nicht erreicht** wie Nr. 14 | `""` | keiner |
| 17 | `L1_IU4_COORDINATOR_ID` | Konstante `live_l1/core/paper_iu4_shadow_runtime_gate.py:30`; Lesestelle `:147`; Aufruf `:299` | wie Nr. 14 | **nicht erreicht** wie Nr. 14 | `""` | keiner |
| 18 | `L1_IU4_SYMBOL` | Konstante `live_l1/core/paper_iu4_shadow_runtime_gate.py:31`; Lesestelle `:147`; Aufruf `:300` | wie Nr. 14 | **nicht erreicht** wie Nr. 14 | `""` | keiner |
| 19 | `L1_IU4_SHADOW_OBSERVATION_MAX_RECORDS` | Konstante `live_l1/core/paper_iu4_shadow_observation_gate.py:37`; Lesestelle `live_l1/core/paper_iu4_shadow_observation_gate.py:792` | `environment.get` über die Trägerkette ab `live_l1/tools/safe_launch.py:164` | **nicht erreicht**; Rücksprung `live_l1/core/paper_iu4_shadow_observation_gate.py:784-785` bei Wert `"0"` | `""` | keiner |
| 20 | `L1_IU4_SHADOW_OBSERVATION_EVIDENCE_PATH` | Konstante `live_l1/core/paper_iu4_shadow_observation_gate.py:36`; Lesestelle `:806` | wie Nr. 19 | **nicht erreicht** wie Nr. 19 | `""` | keiner |
| 21 | `L1_IU4_SHADOW_OBSERVATION_WORK_DIRECTORY` | Konstante `live_l1/core/paper_iu4_shadow_observation_gate.py:38`; Lesestelle `:836` | wie Nr. 19 | **nicht erreicht** wie Nr. 19 | `""` | keiner |
| 22 | `PEE_SCHEMA_VERSION` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:49`; Lesestellen `live_l1/core/paper_economics_shadow.py:187` und `:199` | Trägerkette zu `load_shadow_settings` über drei Wege: `live_l1/core/loop.py:876` nach `live_l1/core/paper_economics_shadow_runtime.py:49`; `live_l1/tools/safe_launch.py:138` nach `live_l1/core/paper_iu4_shadow_runtime_gate.py:272`; `live_l1/tools/safe_launch.py:164` nach `live_l1/core/paper_iu4_shadow_observation_gate.py:853` | **nicht erreicht**; Rücksprung `live_l1/core/paper_economics_shadow.py:166-173` bei `PEE_MODE` gleich `MODE_OFF`; die Wege zwei und drei sind zusätzlich bereits durch `L1_IU4_MODE=OFF` beziehungsweise `L1_IU4_SHADOW_OBSERVATION_ENABLED=0` vorher abgeschnitten | an `:187` `""`; an `:199` **kein Vorgabewert** (Subscript) | keiner |
| 23 | `PEE_ECONOMICS_MODEL_VERSION` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:50`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 24 | `PEE_ECONOMICS_PROFILE_ID` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:51`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 25 | `PEE_QUOTE_CURRENCY` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:52`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 26 | `PEE_STARTING_EQUITY_QUOTE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:53`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 27 | `PEE_RISK_PER_TRADE_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:54`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 28 | `PEE_MAX_POSITION_NOTIONAL_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:55`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 29 | `PEE_ENTRY_FEE_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:56`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 30 | `PEE_EXIT_FEE_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:57`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 31 | `PEE_ENTRY_SLIPPAGE_BPS` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:58`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 32 | `PEE_EXIT_SLIPPAGE_BPS` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:59`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 33 | `PEE_QUANTITY_STEP` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:60`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 34 | `PEE_MIN_QUANTITY` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:61`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 35 | `PEE_MIN_NOTIONAL_QUOTE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:62`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 36 | `PEE_MAX_DAILY_LOSS_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:63`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 37 | `PEE_MAX_DAILY_FEE_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:64`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 38 | `PEE_MAX_REALIZED_DRAWDOWN_RATE` | Dict-Schlüssel `live_l1/core/paper_economics_shadow.py:65`; Lesestellen `:187`, `:199` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:199` kein Vorgabewert | keiner |
| 39 | `PEE_REFERENCE_STOP_RATE` | Konstante `live_l1/core/paper_economics_shadow.py:67`; Lesestellen `:187` und `:206` | wie Nr. 22 | **nicht erreicht** wie Nr. 22 | an `:187` `""`; an `:206` **kein Vorgabewert** (Subscript) | keiner |

**Zum Fehlen eines Vorgabewerts bei Subscript-Zugriffen.** Die Zugriffe `environment[source]` (`live_l1/core/paper_economics_shadow.py:199`) und `environment[REFERENCE_STOP_RATE_ENV]` (`:206`) besitzen keinen Vorgabewert, weil sie als Subscript geschrieben sind. **Daraus folgt nicht, dass der jeweilige Schlüssel tatsächlich fehlt** und auch nicht, dass ein Fehlen zu einem Ausnahmefall führen müsste: die vorgelagerte Fehlendprüfung `live_l1/core/paper_economics_shadow.py:184-196` bricht die Verarbeitung vor diesen Zugriffen mit einem eigenen Grundcode ab, wenn ein erforderlicher Schlüssel leer oder ungesetzt ist. Die Angabe „kein Vorgabewert" ist eine Aussage über die Schreibweise des Zugriffs, nicht über den Zustand der Variablen.

**Zählung.** Die Schlüssel Nr. 1 bis 13 liegen auf dem Kontrollfluss unter den Sollwerten; die Schlüssel Nr. 14 bis 39 sind unter den Sollwerten **nicht erreicht**. Beide Aussagen stehen unter Abschnitt 3.2 Punkt 2.

---

## 7. Randbefund zur Gruppe A

Von den 23 Schlüsseln der Gruppe A werden 20 in den 45 Quelldateien gelesen. Die drei Schlüssel `PYTHONDONTWRITEBYTECODE`, `PYTHONHASHSEED` und `TZ` werden von keiner dieser Dateien **gelesen**; sie erscheinen ausschließlich im einzigen Schreibzugriff `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py:26`. Diese drei Schlüssel sind **Bestandteil der Gruppe A** und richten sich an Interpreter und Standardbibliothek. Über ihre Wirkung wird hier nichts ausgesagt; die Wirkungsfrage gehört zu D1 und bleibt offen.

Randbefund ohne Lesecharakter: `live_l1/core/paper_iu4_shadow_runtime_gate.py:164` und `:177` erzeugen mit `subprocess.run` einen Kindprozess ohne `env=`-Argument und würden damit die vollständige Prozessumgebung weitergeben. Beide Stellen liegen in `_git_head`, gerufen `live_l1/core/paper_iu4_shadow_runtime_gate.py:290`, also nach dem Rücksprung `:233-234`, und sind unter den Sollwerten nicht erreicht.

---

## 8. Review-Aufzeichnung

### 8.1 Herkunft und Empfehlung

Es liegen **zwei Gegenprüfungen** vor. Ihre Herkunft: **vom Nutzer übergebene Antigravity-Berichte**. Beide empfehlen **`ACCEPTABLE_AS_SCOPED_EVIDENCE`** — jeweils **für ihren eigenen Prüfungsumfang**. Eine stärkere, weitergehende oder zusätzliche Prüfung wird hiermit **nicht** behauptet. Beide Gegenprüfungen benennen eigene Analysegrenzen.

**Zuordnung nach tatsächlichem Prüfungsinhalt, ergänzt durch den Korrekturvermerk in Abschnitt 17.** Die beiden Gegenprüfungen sind nach ihrem Inhalt eindeutig unterscheidbar:

| Kennung | Prüfungsinhalt | Ergebnis | Aufzeichnung |
| --- | --- | --- | --- |
| **GP-1** | Gegenprüfung der statischen Analyse einschließlich der Zählkorrekturen; Bestätigung der Dateimenge und der Trägerbindungen | keine offenen Findings; `ACCEPTABLE_AS_SCOPED_EVIDENCE` für diesen Umfang | Abschnitt 8.2 |
| **GP-2** | **gezielte** Gegenprüfung der Vorgabewerte und der Erreichbarkeitsbedingungen der Tabelle in Abschnitt 6 | **keine Findings**; `ACCEPTABLE_AS_SCOPED_EVIDENCE` für diesen Umfang | Abschnitt 8.3 |

Getrennt davon und **nicht** als weitere Gegenprüfung zu zählen: die **anschließende unabhängige Dokumentprüfung** mit **keinen Findings** und der Empfehlung **`APPROVE_FOR_FORMAL_ADOPTION`**; sie ist in Abschnitt 16.3 aufgezeichnet. Insgesamt sind damit drei Prüfungen dokumentiert: zwei Gegenprüfungen in diesem Abschnitt und eine Dokumentprüfung in Abschnitt 16.3. Keine Prüfung wird doppelt aufgenommen, und es wird keine zusätzliche Prüfung angenommen.

### 8.2 GP-1: Gegenprüfung der statischen Analyse, übernommene Korrekturen

**Prüfungsinhalt von GP-1:** die statische Analyse einschließlich der Zählwerte, der Dateimenge und der Trägerbindungen.

Aus der ersten Gegenprüfung wurden zwei Zählkorrekturen übernommen: die Zahl der direkten Lesezugriffe (35 statt zuvor berichteter 33, wodurch die Prüfidentität 35 + 3 + 1 = 39 erfüllt ist) und die Zahl der Weitergabestellen (3 direkte plus 9 aus Trägerparametern gleich 12, statt zuvor berichteter 13). Ferner wurde die ausdrückliche Klarstellung übernommen, dass die Weitergabestellen keine von den 39 direkten Referenzen disjunkte Kategorie bilden (Abschnitt 5.2). Die 45-Dateien-Menge und die fünf Trägerbindungen wurden bestätigt.

### 8.3 GP-2: Gezielte Gegenprüfung der Vorgabewerte und der Erreichbarkeit, übernommene Präzisierungen

**Prüfungsinhalt von GP-2:** die exakten Code-Vorgabewerte je Quellstelle und die Erreichbarkeitsbedingungen der Tabelle in Abschnitt 6. **Ergebnis: keine Findings**, Empfehlung `ACCEPTABLE_AS_SCOPED_EVIDENCE` für diesen Umfang. Die nachstehenden Präzisierungen sind das Ergebnis dieser Prüfung; zwei von ihnen betreffen unmittelbar einen Vorgabewert (`environment[source]`) und eine Erreichbarkeitsbedingung (`live_l1/core/execution.py:319` über `:316`). Eine weitergehende unabhängige Prüfung wird damit **nicht** behauptet.

- **Statische Erreichbarkeit unter Sollbedingungen ist kein Nachweis tatsächlicher historischer Ausführung.** Aufgenommen als Abschnitt 3.2 Punkt 2 und als Vorbehalt der Erreichbarkeitsspalte in Abschnitt 6.
- **`live_l1/core/execution.py:319`** bleibt insbesondere vom **fehlenden übergebenen Pfadargument** abhängig; die vorgelagerte Bedingung `live_l1/core/execution.py:316` entscheidet darüber. Aufgenommen in die Zeile zu Schlüssel Nr. 3.
- **`environment[source]` hat keinen Vorgabewert; daraus folgt nicht, dass der Schlüssel tatsächlich fehlt.** Aufgenommen als Erläuterung im Anschluss an die Tabelle in Abschnitt 6.
- Allgemeine Aussagen der Art, die Prüfung belege „zweifelsfrei" das Fehlen sämtlicher verdeckter oder unauflösbarer Zugriffe, werden **nicht übernommen**. Sie folgen aus einer statischen Analyse nicht.

### 8.4 Nicht gegengeprüfte Teile — ÜBERHOLT, siehe Abschnitt 17

**Dieser Unterabschnitt ist überholt.** Der nachstehende Vermerk beschrieb den Prüfungsinhalt von GP-2 **unzutreffend**: die exakten Code-Vorgabewerte je Quellstelle und die Erreichbarkeitsbedingungen der Tabelle in Abschnitt 6 **waren** Gegenstand von GP-2 und sind dort **ohne Findings** gegengeprüft. Es verbleibt insoweit **kein** offener Prüfteil. Der Wortlaut wird nach der Konvention dieses Dokuments nicht gelöscht, sondern durch diesen Vermerk und durch Abschnitt 17 berichtigt und zeitlich eingeordnet. Es wird **keine** weitergehende unabhängige Prüfung behauptet und **keine** zusätzliche Prüfung angenommen.

Überholter Wortlaut des Entwurfsstands: „Nicht Gegenstand der übergebenen Gegenprüfungen waren die exakten Code-Vorgabewerte je Quellstelle und die Erreichbarkeitsbedingungen der Tabelle in Abschnitt 6. Erforderlich hierfür wäre deren Nachlesung gegen den gebundenen Quellcommit. Dies ist ein benannter offener Prüfteil und **keine** allgemeine Wiederholungspflicht."

---

## 9. Abschließender begrenzter Teilbefund

**In den konkret geprüften Quellen, Zugriffsformen und Weitergabepfaden wurde keine zusätzliche Gruppe-B-Schlüsselanforderung festgestellt.** Alle gefundenen Zugriffsschlüssel waren statisch auflösbar; es trat kein Schlüssel außerhalb der Gruppen A und B auf; es blieb kein nicht auflösbarer Weitergabepfad.

Dieser Teilbefund ist **keine allgemeine Abwesenheitsbehauptung**. Er gilt ausschließlich im Umfang nach Abschnitt 2, mit den Grenzen nach Abschnitt 3.2 und unter den Vorbehalten nach Abschnitt 8.3. Er ist **keine** Schließung von D2, **keine** formale Annahme und **keine** Qualifikation.

**Statuszuordnung nach der Annahme, siehe Abschnitt 16.** Der vorstehende Absatz beschreibt den geprüften Entwurfsstand und wird zeitlich eingeordnet, nicht umgeschrieben. Der Teilbefund selbst ist durch Abschnitt 16 **als begrenzter statischer Teilnachweis formal angenommen**; der Befund ist damit angenommen, nicht selbst ein Annahmeakt. Unverändert gültig bleiben die drei Negativaussagen des Absatzes in ihrer Sache: der Teilbefund bleibt **keine allgemeine Abwesenheitsbehauptung**, er bleibt **keine Schließung von D2** und er bleibt **keine Qualifikation**.

---

## 10. Geltungsbereich von D2 — durch Abschnitt 16 ANGENOMMEN

**Statuszuordnung nach der Annahme, siehe Abschnitt 16.** Die Abschnittsüberschrift trug im geprüften Entwurfsstand den Vermerk `VORSCHLAG_NICHT_ANGENOMMEN`, und der nachfolgende Einleitungssatz bezeichnete den Blocktext als nicht angenommenen Vorschlag. Beide Vermerke beschreiben den **Entwurfsstand vor der Annahme** und werden hier zeitlich eingeordnet und erläutert, nicht sachlich umgeschrieben. Der **Wortlaut des Blocktextes selbst ist unverändert**. Der aktuelle Status dieses Geltungsbereichs ist **ANGENOMMEN**.

Historischer Einleitungssatz des Entwurfsstands, zeitlich eingeordnet: „Der folgende Text ist ein **nicht angenommener Vorschlag**". Dieser Satz gilt ab der Annahme nach Abschnitt 16 nicht mehr für den Status, sondern beschreibt den Stand der Ausarbeitung.

Angenommener Wortlaut, unverändert:

> **Umfang.** D2 betrifft die Vollständigkeit der Menge derjenigen Konfigurationsschlüssel, die im gebundenen Repository-Code gelesen werden, einschließlich statisch auflösbarer indirekter Weitergaben des Umgebungsobjekts.
> Der zu prüfende Umfang leitet sich aus dem Einstiegspunkt ab: vom gebundenen Runner `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` am Quellcommit `3c5927127a03de13d8c80a720f5c8b97a2a36789` über den statisch ermittelten transitiven Repository-Importgraphen — absolute, relative, mehrzeilige, aliasierte und Funktionsebenen-Kanten —, einschließlich der Paketinitialisierungsdateien und aller statisch auflösbaren Weitergabepfade über die tatsächliche Argument-Parameter-Zuordnung.
> Die namentliche Datei- und Hashliste dokumentiert das Ergebnis dieser Ableitung; sie bestimmt nicht, welche Quellen zu prüfen sind. Eine bestimmte Dateizahl ist kein Bestehenskriterium.
> **Werte.** Zustände und Werte dieser Schlüssel sind nicht Gegenstand von D2; sie bleiben B4 und die Sollzustände nach Abschnitt 9 des Integrationsvertrags.
> **Nichtentlastung.** Einflüsse von Interpreter, Standardbibliothek und Drittanbieter-Abhängigkeiten werden durch diese Abgrenzung nicht entlastet. Sie sind dort nachzuweisen, wo die Abschnitte 10 und 11 des Integrationsvertrags, BIND-1b, BIND-2 sowie die Preregistration dies verlangen. Ein Nachweis gilt nur als erbracht, wenn er einer benannten Vertragsstelle und einem benannten Datensatz zugeordnet ist; „anderweitig abgedeckt" ohne solche Zuordnung ist kein Nachweis.

Es wird **keine** neue Verpflichtung zu formaler Verifikation eingeführt. Der angenommene Integrationsvertrag verlangt in Abschnitt 9 eine **statische Bestätigung**; dieses Dokument ist ein Beitrag dazu und selbst noch nicht als Nachweis gebunden.

---

## 11. Was zur dokumentierten Schließung von D2 noch fehlt

**Statuszuordnung nach der Annahme, siehe Abschnitt 16.** Punkt 1 dieser Liste ist durch Abschnitt 16 **erfüllt**; die Punkte 2 bis 5 bleiben **offen**. Die Liste wird nicht umgeschrieben, sondern durch diesen Vermerk eingeordnet. **D2 insgesamt bleibt offen.**

**Berichtigte Statuszuordnung, siehe Abschnitt 17.** Die vorstehende Zuordnung ist für die Punkte 3 und 4 **überholt**. Der berichtigte Stand:

| Punkt | Berichtigter Status |
| --- | --- |
| 1 | **erfüllt** durch Abschnitt 16 |
| 2 | **offen** — Bindung dieses Berichts als Nachweis und die erforderliche Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags |
| 3 | **dokumentationsseitig erfüllt** durch die Tabelle in Abschnitt 6, die je Schlüssel und je Quellstelle den exakten Code-Vorgabewert samt nachgeschaltetem Ersatz aufzählt. Die **Aufzählung** fehlt nicht. Offen bleibt allein die **Bindung** dieser Werte in einem gebundenen Datensatz; diese geht in Punkt 2 auf, soweit sie über diesen Bericht erfolgt |
| 4 | **erfüllt** — die Vorgabewerte und Erreichbarkeitsbedingungen sind durch GP-2 ohne Findings gegengeprüft (Abschnitt 8.3); Abschnitt 8.4 ist insoweit überholt |
| 5 | **offen** — Entscheidung über die in Abschnitt 12 geführten offenen Zuordnungen |

**Erfüllungszeitpunkte, ausdrücklich getrennt und unverschoben.** Die Bindungspflicht aus Punkt 2 behält den vertraglich bestimmten Zeitpunkt: erforderliche Bindungen müssen **vor der Beobachtung historischer Selektionskennzahlen** erfüllt sein (Integrationsvertrag Abschnitte 15 und 20.6). Die zusätzliche Auflage der Preregistration, konfigurationsbezogene Werte einschließlich der expliziten Vorgabewerte im **Candidate-Freeze-Datensatz** festzuschreiben, ist zeitlich **nachgelagert** — nach `FINAL_CANDIDATE_SELECTED` und vor T0 — und **ersetzt oder verzögert die vorgenannte Bindungspflicht nicht**. Getrennt zu halten sind ferner: die **dokumentierten Code-Vorgaben** des gebundenen Quellstands nach Abschnitt 6, die **konkreten Laufwerte** der Umgebung (B4, unbekannt) und die jeweils dafür bestimmten Bindungszeitpunkte. Ein dokumentierter Code-Vorgabewert ist kein Laufwert und ersetzt keinen.

**D2 insgesamt bleibt offen.** Verbleibend sind die Punkte 2 und 5.

1. Annahme des Geltungsbereichs nach Abschnitt 10. — **erfüllt durch Abschnitt 16.**
2. Bindung dieses Berichts als Nachweis mit Identität — Berichtskennung, Pfad, Bytes und SHA256 — und Prüfung dieser Bindung beim Start, entsprechend dem Vorgehen bei der Helper-Qualifikation nach Abschnitt 11 des Integrationsvertrags. Dies erfordert eine Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags, die die Menge der Ergänzungen schließt.
3. Aufzählung der expliziten Vorgabewerte je Schlüssel und je Quellstelle entsprechend der Anforderung „configuration files, environment allowlist, and explicit defaults" der Preregistration.
4. Nachlesung der in Abschnitt 8.4 benannten, noch nicht gegengeprüften Teile.
5. Entscheidung über die in Abschnitt 12 geführten offenen Zuordnungen.

---

## 12. Getrennt weitergeführte offene Punkte

Die folgenden Punkte werden durch dieses Dokument **nicht** berührt, nicht abgeschwächt und nicht als abgedeckt dargestellt.

| Gegenstand | Vorhandene übergeordnete Pflicht | Fehlende konkrete Ausgestaltung beziehungsweise offener Wert |
| --- | --- | --- |
| Tatsächliche Zustände und Werte der Gruppe-B-Schlüssel | Integrationsvertrag Abschnitt 9 (Zustände `GESETZT` mit Wert, `LEER`, `UNGESETZT`; Sollzustände; „Launcher-Standardwerte sind zu keinem Zeitpunkt Belegquelle für historische Artefaktpfade"); offene Bindung **B4** | Werte unbekannt; nicht erhoben und durch dieses Dokument nicht erhoben |
| Drittanbieter-Abhängigkeit `pandas`, bedingt geladen in `live_l1/core/loop.py:713` | Preregistration: Kandidatenidentität bindet unter anderem „dependency lock"; Candidate Freeze verlangt „Python and dependency identities" und „Any missing or implicit value blocks Candidate Freeze"; Integrationsvertrag Abschnitt 10 `dependency_lock.installed_distributions` mit `name`, `version` und `record_sha256` „je Distribution" | Schema und zuständiger Datensatz für die Abhängigkeitsidentitäten **des Erzeugerlaufs**: BIND-1b nennt die „Python-Identität des Laufs", nicht eine Distributionsliste; Abschnitt 10 ist auf die Evaluierungsumgebung bezogen. Tatsächliche Paket- und Laufidentitäten unbekannt (**B3**, **B10**). **Keine vollständige Regelungslücke.** |
| Umgebungsvariablen von Interpreter und Standardbibliothek, etwa `PATH`, `PYTHONPATH`, `PYTHONHOME`, `PYTHONWARNINGS`, `PYTHONUTF8`, `PYTHONIOENCODING`, `PYTHONMALLOC`, `LANG` und `LC_*`, `HOME`, `TMPDIR` | Preregistration, Candidate Freeze: „configuration files, environment allowlist, and explicit defaults" mit „Any missing or implicit value blocks Candidate Freeze" | Die Allowlist in Abschnitt 9 des Integrationsvertrags enumeriert nur die Gruppen A und B; eine Zuordnung dieser Schlüssel fehlt. **Keine vollständige Regelungslücke.** |
| Umwelteinflüsse, die ein Paket-Dateihash nicht erfasst und die nicht als Umgebungsvariable darstellbar sind | soweit als Umgebungsvariable darstellbar: Preregistration wie vorstehend | Für den nicht als Variable darstellbaren Anteil ist keine zuständige Stelle benennbar. Wird als **offene Zuordnungslücke** geführt und nicht durch eine erfundene Zuordnung geschlossen. |
| **D1** — Nachweis des tatsächlich geladenen beziehungsweise ausgeführten Bytecodes und der tatsächlich geladenen dynamischen Abhängigkeiten | Integrationsvertrag Abschnitt 10 (operativer Satz), Abschnitt 14, Abschnitt 20.6 | unverändert **offen**; durch dieses Dokument nicht bearbeitet |
| **D3** — Decimal-Signalflaggen unmittelbar vor einem getrappten Signal | Integrationsvertrag Abschnitt 3, Abschnitt 7.3, Abschnitt 14, Abschnitt 20.6 | unverändert **offen**; durch dieses Dokument nicht bearbeitet |
| **B1 bis B14** | Integrationsvertrag Abschnitt 15 | unverändert **offen**; Werte bleiben `null` |
| **V-19** | Field-/Helper-Contract Abschnitt 9.3; Integrationsvertrag Abschnitt 1.3 und Abschnitt 8 | unverändert **zurückgestellt** |

---

## 13. JSON-/Markdown-Bindung

Die maschinenlesbare Begleitdatei `docs/review/evidence/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.json` enthält im Feld `contract_text` den **vollständigen** Text dieser Markdown-Datei einschließlich Titel, Quellenabschnitten und abschließendem Zeilenumbruch.

Geltungsbereich der Text- und Hashfelder:

- `markdown_bytes` ist die Bytezahl der **vollständigen Bytes dieser Markdown-Datei**.
- `markdown_sha256` ist der SHA256 derselben vollständigen Bytes.
- `contract_text_sha256` ist der SHA256 der **UTF-8-Kodierung von `contract_text`** und bezieht sich damit auf **dieselben** Bytes.
- Beide Hashwerte sind daher identisch; ihre Gleichheit ist der Nachweis der vollständigen und unveränderten Einbettung.
- Die JSON-Datei enthält **keinen Hash ihrer selbst** und keine zyklische Hashbindung.
- Die JSON-Datei ist strikt gültiges JSON **ohne** `NaN`- und **ohne** `Infinity`-Literale, ohne doppelte Schlüssel.
- Die Felder mit dem Präfix `reviewed_` im Annahmedatensatz halten die **geprüften Ausgangsidentitäten** des Entwurfsstands fest und beziehen sich ausdrücklich **nicht** auf den aktuellen Stand; maßgeblich für den aktuellen Stand sind `markdown_bytes`, `markdown_sha256` und `contract_text_sha256`.

Diese Markdown-Datei wird als UTF-8 mit LF-Zeilenenden und abschließendem LF geführt.

---

## 14. Quellenidentitäten

**Gebundener Quellcommit:** `3c5927127a03de13d8c80a720f5c8b97a2a36789`

Die 45 geprüften Quelldateien mit Bytes und SHA256 sind in Abschnitt 4 aufgeführt.

**Angenommene Vertragspaare, vor der Erstellung dieses Entwurfs auf unveränderte Bytes geprüft:**

| Dokument | Markdown SHA256 | JSON SHA256 |
| --- | --- | --- |
| `BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07` | `628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e` | `21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a` |
| `BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08` | `7962f6d9dbd66b9c6e3ea3a66b46b60ac765821deabd7f00ed8b1536daaa6b53` | `90b99bac40c7f640ba2df69e6f97a750e25b0762f83a8c6fc973184a3189e830` |
| `BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08` | `c7776c3ceac5939e3936b429e562830af9f0e90667a65405a0ba5f44a44ab5ff` | `6d9dbd65a9e16042d95719016e9d0259b0b20eb2ca609674950012769918ef3c` |
| `BTC_L1_G10B_OUTPUT_RUNTIME_CONTRACT_V1_2026-09-09` | `e57c1970c30982db3fb8de9dc21e4c24378ff2747c64f7c207ef181c9627e7a9` | `ae518b6a05a30651bd064a9d82c3141db62ddb4c299897d3f9224218bcbe7f26` |
| `BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10` | `6f59d74ee7e2163f47ded5f6427114397ffe11e0db2a8dbc3c8a3dc3b64234cc` | `53a0928e6835480b1422b555313cd4b05f49608e627fde1a4ef33789bfe00828` |
| `BTC_L1_G10B_EVALUATOR_INTEGRATION_CONTRACT_V1_2026-09-11` | `12e2284cb65ce9b31ea39e03391dc543b3fbc7f88ef681ebb7ddf958c7837024` | `b66cbfd5d794fc15c37f40cff2ab7fd5cfc6d454d57d1fd2ffa687d575fcc54c` |

---

## 15. Schlussvermerk

**Zeitliche Einordnung.** Dieser Abschnitt beschreibt den geprüften Entwurfsstand und wird durch Abschnitt 16 zeitlich eingeordnet, nicht umgeschrieben. Der aktuelle Dokumentstatus ist **APPROVED_FOR_ADOPTION**; die formale Annahme und ihre Reichweite ergeben sich allein aus Abschnitt 16 und dem Statusvermerk im Dokumentkopf. Unverändert gültig bleiben in der Sache: **D2 ist nicht geschlossen**, **D1** und **D3** bleiben offen, **B1 bis B14** bleiben offen, **V-19** bleibt zurückgestellt, und aus diesem Dokument folgt keine Implementierungs-, Qualifikations-, Test- oder Ausführungsfreigabe.

Dieses Dokument ist **DRAFT_NOT_BINDING**. Der Teilbefund nach Abschnitt 9 ist begrenzt und im Umfang nach Abschnitt 2 mit den Grenzen nach Abschnitt 3.2 zu lesen. Der Geltungsbereichsvorschlag nach Abschnitt 10 ist **nicht angenommen**. **D2 ist nicht geschlossen.** **D1** und **D3** bleiben offen und wurden nicht bearbeitet. **B1 bis B14** bleiben offen. **V-19** bleibt zurückgestellt. **P01 bis P07**, **K01 bis K08**, **D4 bis D17**, sämtliche Berechnungsregeln und die Selektions-Gates bleiben unverändert und stehen nicht erneut zur Genehmigung.

Autorisiert ist ausschließlich die Erstellung dieser beiden Entwurfsdateien. Aus ihr folgt **keine** formale Annahme und **keine** Implementierungs-, Qualifikations-, Test-, Kandidatenmanifest-, Selektions-, Staging-, Commit-, Push-, Synchronisierungs- oder Market-Run-Freigabe. Kein historischer Final-OOS-Anspruch, kein prospektiver Startzeitpunkt und keine Paper-Trading- oder Live-Kapital-Freigabe folgen aus diesem Entwurf.

---

## 16. Formale Annahmeaufzeichnung

Datum der Annahme (UTC): **2026-09-15**, aufgezeichnet um `2026-09-15T18:32:01Z`.

### 16.1 Annahmeautorität und Gegenstand

Die Annahme beruht auf einer **ausdrücklichen Nutzerfreigabe in der laufenden Konversation**. Angenommen werden genau zwei Gegenstände:

1. **Der dokumentierte statische Teilbefund** nach Abschnitt 9 einschließlich seiner Quellenbindungen nach Abschnitt 4 (45 Quelldateien mit Pfad, Bytes und SHA256) und Abschnitt 14, der korrigierten Zähleinheiten nach Abschnitt 5 einschließlich der Überschneidungserklärung nach Abschnitt 5.2 und der ausgeschlossenen abgeleiteten Summen, der vollständigen Schlüsseltabelle nach Abschnitt 6 einschließlich der Vorgabewerte, Erreichbarkeitsbedingungen und der Erläuterung zu Subscript-Zugriffen, sowie der **ausdrücklich beschriebenen methodischen Grenzen** nach Abschnitt 3.2.
2. **Die ausformulierte Abgrenzung des D2-Geltungsbereichs** nach Abschnitt 10: Ableitung des Umfangs vom gebundenen Runner am gebundenen Quellcommit; die Datei- und Hashliste als **Ergebnis** und nicht als Bestehenskriterium; die **Trennung der tatsächlichen Werte** als B4 und Sollzustände nach Abschnitt 9 des Integrationsvertrags; die **Nichtentlastung** verbleibender Runtime-, Dependency- und Erzeugerlaufanforderungen einschließlich der Regel, dass ein Nachweis nur als erbracht gilt, wenn er einer benannten Vertragsstelle und einem benannten Datensatz zugeordnet ist.

Technische Aussagen, Quellenlisten, Zählwerte, Vorgabewerte, Erreichbarkeitsbedingungen und Methodengrenzen sind **unverändert**. Diese Aufzeichnung ergänzt ausschließlich den Annahmevermerk und die Statuszuordnung.

### 16.2 Geprüft angenommene Ausgangsidentitäten

Angenommen wurden genau die geprüften Bytes des Entwurfsstands:

| Datei | Bytes | SHA256 |
| --- | --- | --- |
| `docs/review/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.md` | 46812 | `89710d52f4bfabab9e3f624ea4b1340a2081e1e8f9d6f806d3b1f270b01babf4` |
| `docs/review/evidence/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.json` | 120814 | `d34acd465a1718fb83d889dba3e2c57151181bd7358542094557317810e4ea01` |

Beide Werte wurden unmittelbar vor dieser Aufzeichnung erneut nachgerechnet und stimmten überein. Durch die Aufnahme dieses Abschnitts ändern sich die Bytes und Hashes beider Dateien; die in der JSON-Begleitdatei geführten Felder `markdown_sha256`, `contract_text_sha256` und `markdown_bytes` beziehen sich stets auf den **aktuellen** Markdown-Stand, während die Felder mit dem Präfix `reviewed_` die oben genannten **geprüften Ausgangsidentitäten** festhalten.

### 16.3 Review-Grundlage

Die vom Nutzer übergebene **unabhängige Dokumentprüfung** empfiehlt **`APPROVE_FOR_FORMAL_ADOPTION`** und meldet **keine Findings**. Sie bestätigt die unveränderten Ausgangsidentitäten nach Abschnitt 16.2 und die im Dokument bereits vorhandenen Werte.

**Klarstellung zur Formulierung „Zählwerte wurden repariert".** Diese Formulierung wird **nicht** als eine während der Leseprüfung erfolgte Dateiänderung übernommen. Es fand **keine** Änderung der Dateien während der Dokumentprüfung statt: der Review meldet **unveränderte Ausgangshashes** und **bestätigte vorhandene Werte**. Die Zählkorrekturen sind zuvor und außerhalb dieser Dokumentprüfung in den Entwurfsstand eingearbeitet worden und in Abschnitt 8.2 aufgezeichnet.

Die beiden in Abschnitt 8 aufgezeichneten Gegenprüfungen mit der Empfehlung `ACCEPTABLE_AS_SCOPED_EVIDENCE` für ihren jeweiligen Prüfungsumfang bleiben unverändert aufgezeichnet. Eine stärkere oder zusätzliche Prüfung wird nicht behauptet; die in Abschnitt 8.4 benannten, nicht gegengeprüften Teile bleiben als solche geführt.

### 16.4 Statuszuordnung gegenüber den historischen Vermerken

| Gegenstand | Status nach dieser Annahme |
| --- | --- |
| Statischer Teilbefund nach Abschnitt 9 mit Abschnitten 3.2, 4, 5, 6, 14 | **ANGENOMMEN** als begrenzter statischer Teilnachweis |
| Geltungsbereich von D2 nach Abschnitt 10 | **ANGENOMMEN** |
| Punkt 1 der Liste in Abschnitt 11 | **ERFÜLLT** durch diesen Abschnitt |
| Punkte 2 bis 5 der Liste in Abschnitt 11 | **OFFEN** |
| **D2 insgesamt** | **OFFEN**, nicht geschlossen |
| Manifestbindung dieses Berichts | **NICHT ERFOLGT**; kein Manifestfeld eingeführt |
| Offene Zuordnungen nach Abschnitt 12 | **OFFEN**, unverändert |
| D1, D3 | **OFFEN**, unverändert, nicht bearbeitet |
| B1 bis B14 | **OFFEN**, Werte bleiben `null` |
| V-19 | **ZURÜCKGESTELLT**, unverändert |
| P01 bis P07, K01 bis K08, D4 bis D17, Berechnungsregeln, Selektions-Gates | **UNVERÄNDERT**, nicht erneut zur Genehmigung gestellt |
| Entwurfs-, Vorschlags- und Offen-Vermerke in den Abschnitten 1.1, 9, 10, 11 und 15 | beschreiben den geprüften Entwurfsstand; zeitlich eingeordnet, nicht umgeschrieben |

### 16.5 Verbleibende Auflagen

**Berichtigung, siehe Abschnitt 17.** Die nachstehende Liste ist in zwei Punkten überholt: die „Aufzählung der expliziten Vorgabewerte je Schlüssel und je Quellstelle" ist dokumentationsseitig durch Abschnitt 6 erfüllt, und die „Nachlesung der nicht gegengeprüften Teile nach Abschnitt 8.4" ist durch GP-2 erledigt. Die Liste wird nicht umgeschrieben; die formale Annahme nach diesem Abschnitt 16 bleibt unverändert erhalten. Verbleibend sind die Bindung dieses Berichts einschließlich der Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags sowie die offenen Zuordnungen nach Abschnitt 12 dieses Dokuments.

Ausdrücklich **nicht** geschlossen und **nicht** angenommen werden:

- die **vollständige Schließung von D2**; hierfür fehlen die Punkte 2 bis 5 nach Abschnitt 11;
- die **Manifestbindung dieses Berichts** sowie jede Einführung eines noch nicht angenommenen Manifestfelds; eine Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags ist hierfür Voraussetzung;
- die Aufzählung der **expliziten Vorgabewerte je Schlüssel und je Quellstelle** nach der Preregistration-Anforderung;
- die **Nachlesung der nicht gegengeprüften Teile** nach Abschnitt 8.4;
- sämtliche **offenen Zuordnungen** nach Abschnitt 12, namentlich B4, die Erzeugerlauf-Abhängigkeitsidentitäten einschließlich `pandas` (B3, B10), die Umgebungsvariablen von Interpreter und Standardbibliothek sowie die nicht als Umgebungsvariable darstellbaren Umwelteinflüsse;
- **D1**, **D3** und **B1 bis B14**;
- sämtliche Implementierungs-, Qualifikations-, Test-, Manifest-, Selektions-, Staging-, Commit-, Push-, Synchronisierungs- und Market-Run-Schritte.

Es wird **keine neue Verpflichtung zu formaler Verifikation** eingeführt. Die vertraglich bestimmten Zeitpunkte bleiben unverändert: erforderliche Bindungen und Qualifikationen müssen jeweils **vor** dem Schritt erfüllt sein, den der Vertrag dafür bestimmt, insbesondere vor der Beobachtung historischer Selektionskennzahlen.

### 16.6 Reichweite der Annahme

Diese Annahme betrifft ausschließlich die beiden in Abschnitt 16.1 bezeichneten Gegenstände und deren Aufzeichnung in genau diesen beiden Dateien. Die zwölf Dateien der sechs angenommenen Vertragspaare bleiben **unverändert**; sie wurden vor und nach dieser Aufzeichnung geprüft. Es erfolgte **kein** Staging, **kein** Commit, **kein** Push und **keine** Synchronisierung; beide Dateien bleiben untracked.

```json
{
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "date_utc": "2026-09-15",
  "recorded_at_utc": "2026-09-15T18:32:01Z",
  "decision": "FORMALLY_ACCEPT_SCOPED_STATIC_D2_EVIDENCE_AND_D2_SCOPE_DEFINITION",
  "document_status": "APPROVED_FOR_ADOPTION",
  "accepted_objects": [
    "statischer Teilbefund nach Abschnitt 9 mit Quellenbindungen, Zaehleinheiten, Schluesseltabelle und Methodengrenzen",
    "Abgrenzung des D2-Geltungsbereichs nach Abschnitt 10"
  ],
  "review_recommendation": "APPROVE_FOR_FORMAL_ADOPTION",
  "review_findings": 0,
  "review_source": "INDEPENDENT_DOCUMENT_REVIEW_REPORTED_BY_USER",
  "review_reported_unchanged_input_hashes": true,
  "review_did_not_modify_files": true,
  "count_repair_during_review_claim_rejected": true,
  "scoped_evidence_reviews_recorded": 2,
  "scoped_evidence_recommendation": "ACCEPTABLE_AS_SCOPED_EVIDENCE",
  "reviewed_markdown_sha256": "89710d52f4bfabab9e3f624ea4b1340a2081e1e8f9d6f806d3b1f270b01babf4",
  "reviewed_markdown_bytes": 46812,
  "reviewed_json_sha256": "d34acd465a1718fb83d889dba3e2c57151181bd7358542094557317810e4ea01",
  "reviewed_json_bytes": 120814,
  "technical_content_changed": false,
  "predecessor_documents_changed": false,
  "d2_closed": false,
  "manifest_binding_of_this_report": false,
  "new_manifest_field_introduced": false,
  "new_formal_verification_duty": false,
  "not_closed": [
    "vollstaendige Schliessung von D2",
    "Manifestbindung dieses Berichts",
    "explizite Vorgabewerte je Schluessel und Quellstelle nach Preregistration",
    "Nachlesung der nicht gegengeprueften Teile nach Abschnitt 8.4",
    "offene Zuordnungen nach Abschnitt 12 einschliesslich B4, B3, B10",
    "D1",
    "D3",
    "B1 bis B14"
  ],
  "deferred_unchanged": "V-19",
  "unchanged_accepted_rules": [
    "P01 bis P07",
    "K01 bis K08",
    "D4 bis D17",
    "Berechnungsregeln",
    "Selektions-Gates"
  ],
  "implementation_authorized": false,
  "qualification_authorized": false,
  "test_execution_authorized": false,
  "evaluation_authorized": false,
  "candidate_manifest_authorized": false,
  "selection_authorized": false,
  "staging_authorized": false,
  "commit_authorized": false,
  "push_authorized": false,
  "synchronization_authorized": false,
  "market_run_authorized": false
}
```

---

## 17. Governance-Korrekturvermerk

Datum (UTC): **2026-09-15**, aufgezeichnet um `2026-09-15T18:44:46Z`, also **nach** der Annahmeaufzeichnung in Abschnitt 16 (`2026-09-15T18:32:01Z`).

### 17.1 Gegenstand und Reichweite

Diese Korrektur betrifft **ausschließlich** die Review- und Restpunktedokumentation. Sie ändert **keine** Quellenliste, **keine** fachliche Tabelle, **keinen** Vorgabewert, **keine** Erreichbarkeitsregel, **keinen** Zählwert und **keine** Methodengrenze. Sie ist **keine neue Annahme**; die formale Annahme nach Abschnitt 16 bleibt in Gegenstand und Reichweite **unverändert erhalten**. Die zwölf Dateien der sechs angenommenen Vertragspaare bleiben unverändert. **D2 bleibt insgesamt offen.** **D1**, **D3**, **B1 bis B14** und **V-19** behalten ihren bisherigen Status.

### 17.2 Berichtigter Sachverhalt und Chronologie

Der Fehler lag in der **Beschreibung** einer bereits vorhandenen Gegenprüfung, nicht in einer fehlenden Prüfung. **GP-2 lag bereits vor der Erstellung dieses Dokuments vor**: ihre Ergebnisse sind die in Abschnitt 8.3 aufgezeichneten Präzisierungen, und sie waren bei der Erstellung bereits in Abschnitt 3.2 Punkt 2, in die Zeile zu Schlüssel Nr. 3 und in die Erläuterung zu Subscript-Zugriffen im Anschluss an die Tabelle in Abschnitt 6 eingearbeitet. Abschnitt 8.4 beschrieb den Prüfungsinhalt von GP-2 gleichwohl als nicht gegengeprüft; das war eine **Fehlbeschreibung**.

Es wird **keine** rückdatierte Aufzeichnung vorgenommen, **keine** veränderte Chronologie behauptet und **keine** zusätzliche oder dritte Gegenprüfung erfunden. Die Zählung der Gegenprüfungen bleibt bei **zwei**; die anschließende Dokumentprüfung ist davon getrennt in Abschnitt 16.3 geführt.

### 17.3 Berichtigte Zuordnung der aufgezeichneten Prüfungen

| Kennung | Prüfungsinhalt | Ergebnis | Aufzeichnung |
| --- | --- | --- | --- |
| **GP-1** | statische Analyse einschließlich Zählkorrekturen; Dateimenge und Trägerbindungen bestätigt | keine offenen Findings; `ACCEPTABLE_AS_SCOPED_EVIDENCE` | Abschnitt 8.2 |
| **GP-2** | gezielt: Vorgabewerte je Quellstelle und Erreichbarkeitsbedingungen der Tabelle in Abschnitt 6 | **keine Findings**; `ACCEPTABLE_AS_SCOPED_EVIDENCE` | Abschnitt 8.3 |
| **DP-1** | anschließende unabhängige Dokumentprüfung | **keine Findings**; `APPROVE_FOR_FORMAL_ADOPTION` | Abschnitt 16.3 |

Zwei Gegenprüfungen, eine Dokumentprüfung, insgesamt drei aufgezeichnete Prüfungen. Keine Prüfung ist doppelt aufgenommen.

### 17.4 Berichtigte Stellen

1. Abschnitt 8.1 — Zuordnung der beiden Gegenprüfungen nach tatsächlichem Prüfungsinhalt (GP-1, GP-2) und Abgrenzung zur Dokumentprüfung in Abschnitt 16.3.
2. Abschnitt 8.2 — Überschrift und Vorsatz benennen den Prüfungsinhalt von GP-1.
3. Abschnitt 8.3 — Überschrift und Vorsatz benennen den Prüfungsinhalt und das Ergebnis von GP-2.
4. Abschnitt 8.4 — als **überholt** gekennzeichnet; der überholte Wortlaut bleibt zitiert und eingeordnet.
5. Abschnitt 11 — berichtigte Statuszuordnung der Punkte 1 bis 5 und ausdrückliche Trennung der Erfüllungszeitpunkte.
6. Abschnitt 16.5 — Berichtigungsvermerk zu zwei überholten Einträgen; die formale Annahme bleibt unverändert.
7. Abschnitt 17 — dieser Vermerk.
8. JSON-Begleitdatei — `review_record` nach GP-1/GP-2 zugeordnet, der überholte Vermerk als solcher gekennzeichnet, Restpunkteliste und Annahme-Restliste berichtigt, Korrekturvermerk aufgenommen, Einbettung und Hashfelder nachgeführt.

### 17.5 Bereinigte Restpunkteliste zur dokumentierten Schließung von D2

| Nr. | Restpunkt | Status |
| --- | --- | --- |
| 1 | Annahme des Geltungsbereichs nach Abschnitt 10 | **erfüllt** durch Abschnitt 16 |
| 2 | Bindung dieses Berichts als Nachweis mit Identität und Prüfung dieser Bindung beim Start; erfordert die Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags | **offen** |
| 3 | Aufzählung der expliziten Vorgabewerte je Schlüssel und je Quellstelle | **dokumentationsseitig erfüllt** durch Abschnitt 6; die verbleibende Bindungspflicht geht in Punkt 2 auf |
| 4 | Gegenprüfung der Vorgabewerte und Erreichbarkeitsbedingungen | **erfüllt** durch GP-2, ohne Findings |
| 5 | Entscheidung über die offenen Zuordnungen nach Abschnitt 12 | **offen** |

**Verbleibend sind die Punkte 2 und 5. D2 ist nicht geschlossen.**

### 17.6 Identitäten des korrigierten Ausgangsstands

Der durch diese Korrektur ersetzte Stand — der in Abschnitt 16 angenommene und anschließend um die Annahmeaufzeichnung ergänzte Stand — trug:

| Datei | Bytes | SHA256 |
| --- | --- | --- |
| `docs/review/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.md` | 59710 | `e4d767ba1a6e62fdcc08525c16711f3239d935ba69b631de455f67c2cc94e288` |
| `docs/review/evidence/BTC_L1_G10B_D2_STATIC_CONFIGURATION_EVIDENCE_V1_2026-09-15.json` | 139643 | `a53a78f816a8386925353b7e4c6cfac177ad42ec62b4fa43f00abcb2eeee56b9` |

Die in Abschnitt 16.2 geführten `reviewed_`-Identitäten des geprüften Entwurfsstands bleiben unverändert und beziehen sich weiterhin auf den dort genannten Stand. Durch diese Korrektur ändern sich die Bytes und Hashes beider Dateien; maßgeblich für den aktuellen Stand bleiben `markdown_bytes`, `markdown_sha256` und `contract_text_sha256` der JSON-Begleitdatei.

```json
{
  "correction_type": "GOVERNANCE_REVIEW_AND_REMAINING_ITEMS_DOCUMENTATION_ONLY",
  "date_utc": "2026-09-15",
  "recorded_at_utc": "2026-09-15T18:44:46Z",
  "after_adoption_recorded_at_utc": "2026-09-15T18:32:01Z",
  "new_acceptance": false,
  "existing_formal_adoption_preserved": true,
  "technical_content_changed": false,
  "predecessor_documents_changed": false,
  "backdating": false,
  "additional_review_invented": false,
  "cross_checks_recorded": 2,
  "document_reviews_recorded": 1,
  "gp2_predates_document_creation": true,
  "section_8_4_superseded": true,
  "d2_closed": false,
  "remaining_closure_items": [
    "Bindung dieses Berichts als Nachweis einschliesslich der Entscheidung zur Abschlussklausel in Abschnitt 12 des Integrationsvertrags",
    "Entscheidung ueber die offenen Zuordnungen nach Abschnitt 12 dieses Dokuments"
  ],
  "binding_timing_unchanged": "Erforderliche Bindungen muessen vor der Beobachtung historischer Selektionskennzahlen erfuellt sein; die nachgelagerte Candidate-Freeze-Auflage ersetzt oder verzoegert diese Pflicht nicht.",
  "d1_d3_b1_b14_v19_status_unchanged": true
}
```
