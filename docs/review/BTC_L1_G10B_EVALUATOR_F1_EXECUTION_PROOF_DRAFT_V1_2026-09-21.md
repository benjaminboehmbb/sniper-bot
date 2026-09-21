# BTC-L1 G10-B — F1-Ausführungsnachweis: Dokumentationsentwurf

**Dokumentdatum:** 2026-09-21.
**Dokumentstatus:** VORSCHLAG_NICHT_ANGENOMMEN.

Die unabhängige Prüfung erteilte APPROVE_FOR_DOCUMENTATION unter einer Quellenkorrektur. Der nachfolgende Hauptteil enthält deren präzisierte Umsetzung in §5.2 und §10 sowie die zugehörigen Quellen in §11. Für den exakten korrigierten Wortlaut und diesen Dokumentationsrahmen wird keine neue unabhängige Prüfung behauptet.

Der Hauptteil wird als Textstand vor seiner Repository-Ablage unverändert dokumentiert. Seine abschließenden Angaben „Keine unabhängige Prüfung, keine Dokumentationsfreigabe, keine Dokumentanlage“ beziehen sich auf die korrigierte Textfassung vor dieser Ablage; sie widerrufen nicht das bedingte Urteil zur geprüften Vorfassung.

Die Ablage dokumentiert einen Vorschlag. Sie bewirkt keine formale Annahme, keine Implementierungs- oder Ausführungsfreigabe. F1 ist nicht erbracht; O bleibt nicht ableitbar; D1 bleibt offen. X1 und das bekannte Fragment bleiben unberührt.

---

# F1-Ausführungsnachweis — konsolidierter Entwurf

**Status: VORSCHLAG_NICHT_ANGENOMMEN. F1 ist nicht erbracht. D1 bleibt offen.**

## §1 Drei Beobachtungsebenen

| Ebene | Inhalt | Wer stellt sie fest |
| --- | --- | --- |
| **O1** | Das Interpreterereignis ist **tatsächlich eingetreten** | niemand direkt; nur erschliessbar |
| **O2** | Der Callback hat daraus einen Datensatz **tatsächlich erzeugt und an den Sendepfad übergeben** | E, intern |
| **O3** | Der Datensatz ist bei A **vollständig, formgültig und innerhalb der gesiegelten Spur angekommen** | **A**, eigenständig |

**A sieht ausschliesslich O3.** Unter den Geltungsbedingungen gilt O3 ⇒ O2 ⇒ O1. **Die Umkehrung gilt nicht:** aus ¬O3 folgt **weder** ¬O2 **noch** ¬O1. Jede Regel, die aus dem Fehlen eines Datensatzes auf das Nichteintreten eines Interpreterereignisses schliessen will, ist unzulässig.

**Die erfolgreiche Rückkehr des Übergabeaufrufs ist nicht Bestandteil von O2 und folgt nicht aus O3.** Ein Datensatz kann bei A bereits vollständig angekommen sein, während der Übergabeaufruf danach eine Ausnahme auslöst oder der Sender vor seiner Erfolgsbestätigung abbricht. **Eine erfolgreich zurückgekehrte Übergabe ist keine Zustellung (O3); eine Zustellung ist umgekehrt kein Beleg einer erfolgreich zurückgekehrten Übergabe.**

## §2 Nachweisgegenstand

| Kennung | Aussage |
| --- | --- |
| **A1** | Der Loader hat für `(module, attempt)` einen Aufruf mit dem geprüften Objekt **C** angesetzt |
| **A2** | Der Interpreter ist **tatsächlich in die Ausführung genau des Objekts C eingetreten** |
| **A3** | Die Ausführung von C wurde **regulär vollständig** beendet |
| **A4** | Die Ausführung von C wurde **nach Eintritt** durch eine propagierende Ausnahme beendet |
| **A0** | Der Aufruf schlug fehl, **bevor** der Interpreter in die Ausführung von C eintrat |

> **F1 ist genau dann für einen Versuch erfüllt, wenn A2 auf Ebene O3 positiv belegt ist** — für dasjenige Objekt, dessen Identität festgestellt wurde, nicht für ein digestgleiches anderes Objekt. **F1 verlangt A2; ein eigenständiger A4-Nachweis ist nicht Bestandteil von F1.**

**Präzisierungen:**

- **A1 erfüllt F1 nicht.**
- **A0 hat eigene Beweislast.** A0 darf **nur** festgestellt werden, wenn ein Fehler vor Eintritt **gesondert belegt** ist und die Erfassung für diesen Versuch nach §6.4 als ungestört ausgewiesen ist. **Das Fehlen eines Eintrittsdatensatzes belegt A0 nicht.**
- **A3 impliziert A2 nur unter Geltungsbedingungen** — gestützt auf `exec()`: „If it is a code object, it is **simply executed**", Rückgabe `None`:

| Kennung | Geltungsbedingung |
| --- | --- |
| **G1** | Der Loader hat **tatsächlich** den vorgesehenen `exec`-Aufruf mit **genau C** ausgeführt — statisch zu qualifizierende Eigenschaft des Loaderquelltexts, **keine** Laufzeitbeobachtung |
| **G2** | C gehört zur **gebundenen zulässigen Codeobjektklasse**: aus Modulquelltext mit `mode='exec'` übersetzt, `co_freevars` leer, keine Generator-, Coroutine- oder Async-Generator-Kennung in `co_flags`. **Ausserhalb dieser Klasse wird die Folgerung nicht behauptet** |
| **G3** | Modulsemantik: ein einziges echtes `dict` als `globals`, kein getrenntes `locals`, `closure=None` |

- **A4 impliziert A2.**
- **Der Ausgang steuert F1 nicht.**
- **`PY_RETURN` ist nicht der abgeschlossene Aufruf.** Es liegt „**immediately before** the return" der Modulrahmen-Ausführung und belegt nicht, dass der umgebende `exec`-Aufruf erfolgreich zurückgekehrt ist. Diese Aussage trägt allein der Ausgangsdatensatz des Loaders, unter G1–G3.

## §3 Was der kontrollierte Ladeweg ohne Zusatzmechanismus trägt

| Schritt | Aussage | Stütze |
| --- | --- | --- |
| Quellbyte-Identität | Loader liest die Bytes selbst, vergleicht SHA256 gegen gebundenen `file_sha256` | bestehendes §10-Feld |
| Übersetzung | `compile(source, filename, 'exec', flags, dont_inherit=True, optimize=<gebunden>)` | `compile()`-Signatur |
| Vergleich gegen Soll | CODEID-1 über C gegen den vorab gebundenen Sollwert | §5 |
| Unveränderlichkeit zwischen Prüfung und Aufruf | „Code objects are **immutable** and contain **no references (directly or indirectly) to mutable objects**"; `replace()` liefert eine **Kopie** | Datenmodell |
| Aufruf genau dieses Objekts | `exec(C, module.__dict__)` | `source_to_code` |
| **A3 ⇒ A2 unter G1–G3** | reguläre Rückkehr belegt Eintritt | `exec()` |

**Die verbleibende Lücke:** `exec()` liefert bei Erfolg `None`, bei Fehlschlag eine Ausnahme. **Es gibt kein Rückgabesignal, das A0 von A4 trennt.** Nur hierfür wird ein Zusatzmechanismus eingeführt.

## §4 Bevorzugter Kandidat — Variante L, rein lokal

### 4.1 Wahl und Begründung

**Armierung:** `sys.monitoring.set_local_events(TOOL, C, PY_START | PY_RETURN)` — beide Ereignisse gehören zur dokumentierten Menge der lokalen Ereignisse. `PY_UNWIND` wird **nicht** armiert.

| Grund | Beleg |
| --- | --- |
| `PY_UNWIND` ist **nicht lokal aktivierbar** | Es steht unter „Other events": „not necessarily tied to a specific location … **cannot be individually disabled**" |
| **F1 benötigt `PY_UNWIND` nicht** | F1 ist A2; A2 trägt `PY_START`: „Start of a Python function (occurs **immediately after the call**, the callee's frame will be on the stack)" |
| `PY_RETURN` dient der **Kohärenzprüfung**, nicht F1 | „occurs **immediately before the return**" |
| Bindung über **das Objekt selbst** | Der Callback erhält `code: CodeType`. Keine zeitliche Korrelation; **keine Rückkehr zur verworfenen Audit-Stapelkorrelation** |
| Enger Instrumentierungsumfang | `set_local_events` wirkt auf **genau dieses Codeobjekt** |
| Keine Rückkopplung durch den Callback | „Events are suspended in callback functions and their callees for the tool that registered that callback." **Zugleich Abdeckungsgrenze, §6.5** |
| Werkzeugkollision erkennbar | `use_tool_id` „Raises a `ValueError` if _tool_id_ is in use" |

**Callback-Signaturen, je Ereignis verschieden:**

| Ereignis | Dokumentierte Signatur | In Variante L |
| --- | --- | --- |
| `PY_START` | `func(code: CodeType, instruction_offset: int) -> object` | **ja, lokal** |
| `PY_RETURN` | `func(code: CodeType, instruction_offset: int, retval: object) -> object` | **ja, lokal** |
| `PY_UNWIND` | `func(code: CodeType, instruction_offset: int, exception: BaseException) -> object` | **nein** (nur Option G) |

Der Callback gibt **niemals `DISABLE`** zurück. `retval` und `exception` werden **nicht** in die Spur übernommen.

### 4.2 Option G — ausdrücklich global, nicht Teil des bevorzugten Ablaufs

Für einen **positiven** A4-Beleg ist `PY_UNWIND` **nur global** aktivierbar: `set_events(TOOL, PY_UNWIND)` mit Filterung auf `code is C`.

| Eigenschaft | Feststellung |
| --- | --- |
| Beschreibung | **Dies ist eine globale Aktivierung**, nicht eine ausschliesslich lokale Instrumentierung |
| Umfang | Der Callback wird für Abwicklungen von Python-Rahmen gerufen — **soweit die dokumentierten Abdeckungsgrenzen reichen: erst nach der Armierung, ausschliesslich für Python-Rahmen und nicht innerhalb des Aufrufbaums des eigenen Callbacks, weil Ereignisse dort für das eigene Werkzeug suspendiert sind.** Die weitere Einschränkung entsteht erst durch die Filterung im Callback |
| **Keine vollständige globale Erfassung** | Keine Aussage über EXTENSION-Module, C-Rahmen, native Ladevorgänge oder das Bootstrap-Fenster vor Armierung |
| Abschaltbarkeit | „cannot be individually disabled via `DISABLE`" |
| Kosten | prozessweite Kosten, breiter Instrumentierungsabdruck; **nicht qualifiziert** |
| Eigene Voraussetzungen | Option G trüge einen zusätzlichen Abwicklungsnachweis **nur unter ihren eigenen, hier nicht ausgearbeiteten Voraussetzungen** |
| Empfehlung | **Nicht Teil des bevorzugten Ablaufs, nicht ausgewählt.** Offene Entscheidung F-i |

**Ohne Option G bleibt die spezifische Aussage A4 ohne gesonderten Nachweis offen. Variante L benötigt sie nicht, weil F1 den Eintrittsnachweis A2 verlangt und nicht zusätzlich einen Abwicklungsnachweis.**

### 4.3 Ablauf

| Nr. | Handlung | Erzeuger |
| --- | --- | --- |
| 1 | `use_tool_id(TOOL, "<gebundener Name>")`; `register_callback` für `PY_START` und `PY_RETURN`; alle vom Sendepfad benötigten Module **vorher** importieren | E |
| 2 | Quellbytes lesen, SHA256 gegen gebundenen `file_sha256` vergleichen; Abweichung ⇒ Abbruch **ohne Übersetzung** | E-Loader |
| 3 | `C = compile(bytes, filename=<gebunden>, mode='exec', flags=<gebunden>, dont_inherit=True, optimize=<gebunden>)` | E-Loader |
| 4 | **Klassenprüfung G2** | E-Loader |
| 5 | **Dateinamensprüfung**: `C.co_filename` und der Wert **jedes über `co_consts` rekursiv erreichbaren Codeobjekts** gegen den gebundenen Wert | E-Loader |
| 6 | `code_digest = CODEID-1(C)` **vor jeder Armierung**; gegen `code_digest_soll` vergleichen | E-Loader |
| 7 | `params_digest` bilden und vergleichen | E-Loader |
| 8 | Abweichung in 2, 4, 5, 6 oder 7 ⇒ **technischer Abbruch `IDENTITY_MISMATCH`; C wird nicht ausgeführt** | E-Loader |
| 9 | Eintrag in das **Ausführungsregister** (§6.1): starke Referenz auf C, `(module, attempt)`, `observed_count = 0`; `attempts_registered` erhöhen | E-Loader |
| 10 | `set_local_events(TOOL, C, PY_START \| PY_RETURN)` | E-Loader |
| 11 | Datensatz `phase="start"` senden | E-Loader |
| 12 | `exec(C, module.__dict__)` innerhalb von `exec_module(module)` | E-Loader |
| 13 | Callback: **zuerst `callback_invocations` erhöhen**; Registereintrag über **linearen `is`-Vergleich** auflösen; Datensatz erzeugen; an den Sendepfad übergeben; **erst nach erfolgreich zurückgekehrter Übergabe** `observed_count` des betroffenen Versuchs erhöhen; `None` zurückgeben | Callback |
| 14 | Ausgangsdatensatz `normal_return` / `exception` senden, **mit dem erreichten `observed_count`** | E-Loader |
| 15 | Aktivmarkierung aufheben; **lokale Ereignisse bleiben armiert**; starke Referenz bleibt bestehen | E-Loader |
| 16 | Vor dem Siegel **genau einen** `capture_status`-Datensatz senden (§6.4) | E |
| 17 | A prüft Transport, Folgen, Kohärenz und Erfassungsdeklaration | A |

## §5 Identität und Sollvergleich

### 5.1 Drei Begriffe, die nicht ineinander übergehen

| Begriff | Was er aussagt | Was er **nicht** aussagt |
| --- | --- | --- |
| **Gleichheit der gewählten serialisierten Darstellung** | die von CODEID-1 erfassten Eigenschaften stimmen überein | nichts über Eigenschaften, die die Darstellung **auslässt** |
| **Digestvergleich** | **Die Digestwerte der beiden Darstellungen stimmen überein. Dies wird unter der zugrunde gelegten kryptografischen Kollisionsannahme als Vergleichsnachweis verwendet; mathematische Darstellungsgleichheit oder Objektidentität wird dadurch nicht bewiesen.** | keine bewiesene Darstellungsgleichheit, keine Objektidentität, keine Ausführung |
| **Objektidentität** | es ist **dasselbe Objekt** | keine Aussage über seine Ausführung ohne §4 |

### 5.2 CODEID-1 — Vorschlag, ausdrücklich unvollständig

**Erfasst** (dokumentierte Attribute, typunterscheidend kodiert): `co_name`, `co_qualname`, `co_argcount`, `co_posonlyargcount`, `co_kwonlyargcount`, `co_nlocals`, `co_varnames`, `co_cellvars`, `co_freevars`, `co_code`, `co_consts` (rekursiv; verschachtelte Codeobjekte wiederum als CODEID-1), `co_names`, `co_firstlineno`, `co_stacksize`, `co_flags`.

| Gegenstand | Behandlung |
| --- | --- |
| `co_name`, `co_nlocals` | aufgenommen; `co_nlocals` wird **nicht** als aus `co_varnames` ableitbar unterstellt |
| `co_code` | gewöhnliche Attributform, **nicht** die adaptive Rohform |
| `co_lnotab` | ausgeschlossen: „Deprecated since version 3.12 … may be removed in Python 3.15" |
| `co_positions()`, `co_lines()` | **Methoden**, keine Attribute; Aufnahme **offen** (F-c) |
| `co_linetable`, `co_exceptiontable` | In der Python-3.12-Sprachreferenz nicht als Attribute aufgeführt. PEP 626 beschreibt co_linetable ausdrücklich; dessen Format ist dort als undurchsichtig, nicht spezifiziert und ohne Vorankündigung veränderbar bezeichnet. Die C-API-Dokumentation führt exceptiontable als Parameter von PyUnstable_Code_New und kennzeichnet diese API als instabil und versionsabhängig. Eine dokumentierte C-API-Parameterliste ist keine Spezifikation des Python-Attributs oder seines Binärformats. Aufnahme und Kodierung bleiben versionsbezogen auszuarbeiten; bei Ausschluss sind Zeilenzuordnung und Ausnahmebehandlungstabelle durch diese Felder nicht im Digest abgedeckt. Offen (F-c). |
| `co_filename` | **nicht im Digest.** Ein separat gemeldeter Compile-Parameter ist **keine** Prüfung des Attributs; deshalb Schritt 5 des Ablaufs über C **und alle rekursiv erreichbaren** Codeobjekte |
| Typkodierung | **offene Ausarbeitung**; mindestens müssen `1`, `1.0`, `True`, `"1"` verschiedene Darstellungen erhalten |
| `marshal` | nicht als Sollgrundlage: „not compatible between Python versions, even if the version of the format is the same" |

> **Solange Attributumfang und kanonische Kodierung offen sind, ist CODEID-1 ein Vorschlag und keine vollständige Vergleichsvorschrift.**

### 5.3 Nichtzirkularität

`code_digest_soll` entsteht in einem **getrennten Ableitungsvorgang vor dem Lauf**, ausschliesslich aus gebundenen Quellbytes und gebundenen Übersetzungsparametern, und wird in BIND-2 festgeschrieben; er liest keinen Istwert dieses Laufs. **A kann die Sollseite unabhängig nachvollziehen**, die **Istseite nicht**, weil C nur im Prozess von E existiert. **Keine neue B3/B5-Gleichheitsanforderung.**

## §6 Zuordnung, Folgen, Fehlerrichtung

### 6.1 Ausführungsregister — Objektidentität, nicht Schlüsselgleichheit

| Festlegung | Begründung |
| --- | --- |
| **Liste von Einträgen** mit je einer **starken Referenz** auf das Codeobjekt | verhindert Einsammeln und Wiederverwendung einer Objektkennung |
| Auflösung durch **linearen Durchlauf mit `is`** gegen das übergebene `code`-Argument | **Hash- oder schlüsselbasierter Zugriff ist ausgeschlossen.** Die Dokumentation sagt **nicht**, dass Codeobjekte nach Identität verglichen und gehasht werden; ein Schlüsselvergleich stützte sich auf nicht zugesicherte Semantik. `is` stellt Identität tatsächlich fest |
| Keine numerische Objektkennung als Schlüssel | Kennungsgleichheit wird hier nicht als Identitätsnachweis verwendet |

**Voraussetzung V-1, nachzuweisen:** je Codeobjekt ist höchstens ein Versuch gleichzeitig aktiv. **`sys.modules` und ein angenommener einsträngiger Ablauf beweisen das nicht.**

### 6.2 Ereignisfolgen

**Anzahlen je Versuch:** genau ein `start`; genau ein Ausgang; **höchstens ein** `py_start`; **höchstens ein** `py_return`.
**Reihenfolge nach `seq`:** `start` < `py_start` < `py_return` < Ausgang.

| Nr. | Folge | Einordnung | Aussage und Grenze |
| --- | --- | --- | --- |
| **M1** | `start`, `py_start`, `py_return`, `normal_return` | **zulässiges Muster** | **A2 und A3 belegt.** F1 erfüllt, sofern K, D und §6.4 erfüllt sind |
| **M2** | `start`, `py_start`, `exception` | **zulässiges Muster** | **A2 belegt** und ein **berichteter Ausnahmeausgang des Aufrufers** festgestellt. **Das fehlende `py_return` beweist für sich keine Abwicklung des Modulrahmens** — es ist ebenso mit ausgefallener oder zeitweise unterbrochener Erfassung, Callbackfehler oder Datensatzverlust vereinbar; **P-8 bleibt offen**. **Die spezifische Aussage A4 bleibt ohne gesonderten Nachweis offen und wird aus diesem Muster nicht erschlossen.** F1 bleibt davon unberührt, weil F1 A2 verlangt |
| **M3** | `start`, `py_start`, `py_return`, `exception` | **zulässiges Muster, kein Protokollverstoss** | **A2 belegt** — F1 kann erfüllt sein, sofern K, D und §6.4 erfüllt sind. **Offen bleiben A3 und A4 zugleich:** `PY_RETURN` liegt *vor* der Rückkehr des Modulrahmens und belegt weder dessen tatsächlichen Abschluss noch die erfolgreiche Rückkehr des umgebenden `exec`-Aufrufs; der Ausnahmeausgang kann nach diesem Ereignis entstanden sein. **Verwertbarkeitsgrenze:** die Folge ist ebenso mit einem Erfassungsfehler vereinbar, etwa einem fälschlich erzeugten oder fälschlich zugeordneten `py_return`; ihre Verwertung setzt deshalb H1–H4 und V-1 voraus. **Für den Laufabschluss gelten die bestehenden E3-, Gate- und Abschlussregeln unverändert; hier wird keine neue Abschlussregel eingeführt** |
| **M4** | `start`, `exception` ohne `py_start` | **zulässiges Muster** | **Kein positiver Eintrittsnachweis; Ursache ungeklärt.** Vereinbar mit Fehler vor Eintritt, ausgefallener Erfassung, Callbackfehler oder Datensatzverlust. **A0 nur bei gesondert belegtem Fehler vor Eintritt.** Zustand `ungeklärt` |
| **M5** | `start`, `normal_return` ohne `py_start` | **unzulässig** | Widerspruch unter G1–G3 ⇒ **`inkonsistent`** |
| **M6** | `start`, `py_start`, `normal_return` ohne `py_return` | **unzulässig** | `PY_RETURN` war lokal armiert ⇒ **`inkonsistent`** |
| **M7** | Beobachtungsdatensatz **nach** dem Ausgang | **unzulässig** | Reihenfolgeverstoss ⇒ **`inkonsistent`** |
| **M8** | zwei `py_start` oder zwei `py_return` | **unzulässig** | Anzahlverstoss ⇒ **`inkonsistent`** |
| **M9** | `py_return` ohne vorangehendes `py_start` | **unzulässig** | Reihenfolgeverstoss ⇒ **`inkonsistent`** |
| **M10** | Beobachtungsdatensatz ohne zugehörigen `start` | **unzulässig** | **`inkonsistent`**; zusätzlich Befund nach M12 |
| **M11** | Ausgang fehlt in gesiegelter Spur | **unzulässig** | K1 verletzt ⇒ **`inkonsistent`** |
| **M12** | Callback trifft ein Codeobjekt **ohne aktiven Registereintrag** | **eigener Befund** | Datensatz `unregistered_entry`: Eintritt in ein armiertes Objekt ausserhalb des kontrollierten Wegs. **Kein positiver Abschluss** |
| **M13** | Abweichung eines Identitätsfelds innerhalb eines Versuchs | **unzulässig** | Paarverstoss ⇒ **`inkonsistent`** |
| **M-X** | **Auffangregel** | **unzulässig** | **Jede Kombination, Anzahl oder Reihenfolge, die nicht ausdrücklich unter M1 bis M4 oder M12 zugelassen ist, gilt als Verstoss: Versuch `inkonsistent`, kein positiver Abschluss. Unerwähnte Folgen sind nicht stillschweigend zulässig** |

**Trennung zweier Begriffe:** „zulässiges Muster" heisst **nicht** „positiver Abschluss". Die Zulässigkeit eines Musters sagt nichts über den Laufabschluss; umgekehrt schliesst jeder Protokollverstoss einen positiven Abschluss aus. **In keinem Muster wird ein Versuch aus V entfernt.**

### 6.3 Callback- und Übertragungsfehler

| Ereignis | Behandlung |
| --- | --- |
| Der Callback wirft eine Ausnahme | **Vorgesehen ist, dass keine Ausnahme aus dem Callback entweicht:** interner Abfang, `capture_degraded` setzen, `callback_errors` erhöhen, `None` zurückgeben. **Das Abfangen und Protokollieren ist eine beabsichtigte Fehlerbehandlung, deren Ausnahmslosigkeit nicht nachgewiesen ist**; wie der Interpreter eine dennoch entweichende Ausnahme behandelt, ist in der konsultierten Dokumentation nicht beschrieben (**P-4**, spätere Qualifikation) |
| Der Sendepfad scheitert | Behandlung nach der bestehenden Schreibdisziplin von E; zusätzlich `send_failures` erhöhen und `capture_degraded` setzen |
| Der Übergabeaufruf scheitert **nach** vollständiger Übertragung | Möglich: A hat den Datensatz bereits vollständig empfangen, der Sender bestätigt ihn aber nicht. **Erkennbar allein als Zählerabweichung nach §6.4, nicht als Verlust** |
| Abweichung zwischen deklarierten und empfangenen Datensätzen | Erkennung **nicht** über eine Folgenlücke, sondern über den Zählerabgleich §6.4. **Sperrend; die Ursache bleibt zunächst offen** |
| Ein Erfassungsfehler bleibt E selbst verborgen | **Keine Erkennung.** Ausdrücklich offen |

### 6.4 Positive Erfassungsdeklaration

#### 6.4.1 Zählerdefinitionen

| Zähler | Erhöht durch | Fehlgeschlagene Versuche | Bei A zu vergleichen mit | `unregistered_entry` |
| --- | --- | --- | --- | --- |
| `callback_invocations` | **jeden Eintritt in den Callback**, als erste Handlung vor Registerauflösung und Datensatzerzeugung | **ja** — gezählt wird der Eintritt, unabhängig vom Ausgang | der Summe aus zugestellten Beobachtungsdatensätzen und `unregistered_entries` (siehe H4) | **mitgezählt** |
| `observed_count` (je Versuch) | **jede erfolgreich zurückgekehrte Übergabe** eines Beobachtungsdatensatzes an den Sendepfad für **genau diesen** `(module, attempt)` | **nein** — gescheiterte Erzeugung oder gescheiterte Übergabe erhöht ihn **nicht** | der Zahl der bei A **zugestellten** Beobachtungsdatensätze (`py_start`, `py_return`) mit genau diesem `(module, attempt)` | **ausgenommen** — ein `unregistered_entry` hat keinen Versuch und geht in **kein** `observed_count` ein |
| `unregistered_entries` | jede erfolgreich zurückgekehrte Übergabe eines `unregistered_entry`-Datensatzes | nein | der Zahl der bei A zugestellten `unregistered_entry`-Datensätze | **eigener Zähler** |
| `callback_errors` | jede im Callback abgefangene Ausnahme, einschliesslich Fehlern bei Registerauflösung und Datensatzerzeugung | ja | — (muss 0 sein) | mitgezählt, soweit betroffen |
| `send_failures` | jeder **fehlgeschlagene** Übergabeversuch an den Sendepfad | ja | — (muss 0 sein) | mitgezählt, soweit betroffen |
| `attempts_registered` | jede Registrierung eines Versuchs im Ausführungsregister (Schritt 9) | — | der Zahl der bei A zugestellten `start`-Datensätze | — |

> **`observed_count` erfasst ausschliesslich senderseitig bestätigte Übergaben**, also Übergabeaufrufe, die erfolgreich zurückgekehrt sind. **Er ist weder mit O2 noch mit O3 deckungsgleich:** er ist eine senderseitig bestätigte Teilmenge von O2 und sagt nichts über die Zustellung. **Bei einem späten Fehler — Ausnahme nach vollständiger Übertragung oder Abbruch vor der Erfolgsbestätigung — kann A mehr vollständige Datensätze empfangen haben, als der Sender bestätigt hat.** Eine Differenz in **beide** Richtungen ist deshalb **zunächst eine Inkonsistenz zwischen Senderdeklaration und Empfangsbefund** und **beweist keinen Datensatzverlust**.

#### 6.4.2 Bedingungen

| Kennung | Bedingung |
| --- | --- |
| **H1** | Für **jeden** Versuch: das im Ausgangsdatensatz geführte `observed_count` ist gleich der Zahl der bei A zugestellten Beobachtungsdatensätze dieses `(module, attempt)`. **Jede Ungleichheit — in beide Richtungen — ist eine Inkonsistenz zwischen Senderdeklaration und Empfangsbefund und macht den Versuch `inkonsistent`; sie ist für sich kein Nachweis eines Datensatzverlusts** |
| **H2** | Genau **ein** `capture_status`-Datensatz liegt vor, unmittelbar vor dem Siegel, mit: Werkzeugkennung und ‑name, der über `get_local_events` **zurückgelesenen** armierten Ereignismenge je armiertem Objekt, Zahl armierter Objekte, `callback_invocations`, `callback_errors`, `send_failures`, `unregistered_entries`, `attempts_registered`, `capture_degraded`. **Fehlt dieser Datensatz, ist F1 für keinen Versuch erfüllt** |
| **H3** | `capture_degraded` ist falsch, `callback_errors = 0`, `send_failures = 0` |
| **H4** | Die eigenen Zählungen von A stimmen mit den Deklarationen überein: zugestellte `start`-Datensätze = `attempts_registered`; zugestellte `unregistered_entry`-Datensätze = `unregistered_entries`; und **unter H3** gilt `callback_invocations` = Summe aller `observed_count` + `unregistered_entries`. **Jede Abweichung ⇒ H4 nicht erfüllt; sie ist eine Inkonsistenz zwischen Deklaration und Empfangsbefund, kein bewiesener Verlust** |

#### 6.4.3 Wirkung — mit ihren Grenzen im selben Absatz

Unter H1–H4 wird Schweigen zu „nicht nachgewiesen" statt zu „in Ordnung": eine abgebrochene, nie armierte oder erkennbar gestörte Erfassung erzeugt keinen Positivbefund, weil der positive Befund einen **vorhandenen und stimmigen** Statusdatensatz voraussetzt. **Diese Wirkung ist jedoch von vornherein begrenzt.** Ein stimmiger Statusdatensatz und eine abschliessende `get_local_events`-Abfrage bestätigen **nicht**, dass das Werkzeug während des gesamten relevanten Zeitraums **ununterbrochen aktiv** war; eine zwischenzeitliche Deaktivierung mit späterer Wiederaktivierung wäre durch die Endabfrage allein **nicht nachgewiesen** (**P-8**). Der Statusdatensatz ist zudem selbst eine Erklärung von E; ein durchgängig unzutreffender Bericht wird durch diese Prüfungen nicht aufgedeckt. **Der `capture_status`-Datensatz ist daher eine zusätzliche Konsistenzprüfung unter den bereits genannten Voraussetzungen und kein Ersatz für den Nachweis ihrer Einhaltung.**

**Begrenzte Aussage zur Fehlerrichtung:** Unter H1–H4, G1–G3, V-1 und den Mustern aus §6.2 führt ein **erkanntes** Erfassungsversagen zu `ungeklärt` oder `inkonsistent`, niemals zu `nachgewiesen_ausgeführt`. **Für ein unerkanntes Versagen wird keine Garantie behauptet; aus Konsistenzprüfungen allein folgt keine allgemeine Garantie.**

### 6.5 Abdeckungsgrenze aus der Ereignisunterdrückung

PEP 669: „**Events are suspended in callback functions and their callees for the tool that registered that callback.**" Das verhindert Rückkopplung — und bedeutet zugleich: **eine Ausführung eines armierten Codeobjekts innerhalb des Aufrufbaums des eigenen Callbacks würde für dieses Werkzeug nicht gemeldet.** Vorgeschlagene Massnahme: der Callback löst **keine Importe** aus; alle vom Sendepfad benötigten Module werden vor der Armierung geladen. **Qualifikationsbedingung, kein Nachweis; keine Abwehrarchitektur.**

### 6.6 Bereits geregelte Fälle, unverändert

| Fall | Folge |
| --- | --- |
| Wiederholungen | eigenes `attempt`, eigene Folge; **V bleibt vollständig** |
| Prozessabbruch von E | Signalbeendigung schliesst den positiven Abschluss aus; unvollständige Folgen ⇒ `inkonsistent` |
| Unvollständige Spur | K3 verletzt ⇒ **sämtliche** Versuche `inkonsistent` |
| Ungeklärter Einzelversuch | Bleibt in V. **Ein nachgewiesener Versuch desselben Moduls verdeckt ihn nicht.** `R ⊆ O ⊆ Z` prüft, ob jede erforderliche Modulidentität durch **mindestens eine** nachgewiesene Ausführung vertreten ist, und **ersetzt den Einzelnachweis nicht** — auch nicht für Module ausserhalb von R |

## §7 Cachebefund

| Feststellung | Zulässige Meldung |
| --- | --- |
| Der kontrollierte Loader hat für dieses Modul **keine** Bytecode-Cachedatei konsultiert | `cache_consulted_by_loader = false`. **Belegt Nichtnutzung auf diesem Weg und sagt nichts über Vorhandensein oder Nichtvorhandensein einer Cachedatei** |
| Präsenz **zusätzlich belegt** (etwa über die bestehenden §10-Felder) und nicht konsultiert | `cache_state = "present_unused"` |
| Abwesenheit **belegt** | `cache_state = "absent"` |
| Präsenz weder belegt noch widerlegt | **`cache_state = "unknown"`** |

**Keine zusätzliche Cache-Suche, keine Löschung, keine Neuerzeugung, kein Verbot. E2-Regeln unverändert; keine neuen Fehlercodes.**

## §8 Erforderliche Anpassungen — sämtlich neue Vorschläge

### 8.1 Spurprotokoll

| Gegenstand | Bestehender Stand | **Neuer Vorschlag** |
| --- | --- | --- |
| `phase` | `{"start","normal_return","exception"}` | erweitern um `"py_start"`, `"py_return"`; in Option G zusätzlich `"py_unwind"` |
| Paarregeln 3.4.1 | genau ein `start`, genau ein Ausgang | ersetzen durch §6.2 **einschliesslich der Auffangregel M-X** |
| `instruction_offset` | nicht vorhanden | Ganzzahl ≥ 0, Pflichtfeld **nur** bei Beobachtungsphasen |
| `observed_count` | nicht vorhanden | Ganzzahl ≥ 0, Pflichtfeld **nur** im Ausgangsdatensatz, Definition nach §6.4.1 |
| `cache_consulted_by_loader` | nicht vorhanden | Boolean, Pflichtfeld im `exec_record` |
| `kind` | vier Werte | ergänzen um `"capture_status"` und `"unregistered_entry"` |
| Bedingung F in 4.4 | offen formuliert | F1 erfüllt, wenn für `(module, attempt)` ein zugestellter `py_start`-Datensatz mit bestätigter Objektidentität vorliegt, **und** H1–H4 erfüllt sind, **und** keine Verletzung nach §6.2 vorliegt |
| Abschnitt 12 | Liste | um §9.4 erweitern |

### 8.2 BIND-2

`execution_proof.variant` (L oder G) · `execution_proof.tool_id` / `.tool_name` · `execution_proof.local_event_set` · `codeid.rule` mit Attributliste, Ausschlüssen und Typkodierung · `code_class.admissible_flags` (G2) · `compile_params.<modul>` · `code_digest_soll.<modul>` · `runtime.python.monitoring_available` als Bedingung an **B5**.

### 8.3 Vertragsstellen

Abschnitt 10 „Grenzen der Abdeckung" erhält ein **benanntes Kandidatenverfahren** und bleibt bis zur Qualifikation offen. Die Importliste ist eine Zustandsliste je Modulname und kann Wiederholungen nicht führen; der Einzelnachweis liegt allein in der Spur. **Bestehende Vertragsdokumente bleiben unverändert.**

**Nicht vorgeschlagen:** keine neue B3/B5-Gleichheitsanforderung; keine pauschale Audit-Hook-Pflicht; kein Cacheverbot; keine Speicherintegritäts- oder Angreiferabwehrarchitektur; keine Änderung der E1-, E2-, E3- oder wirtschaftlichen Regeln; kein neues kryptografisches Verfahren.

## §9 Alternativen, Reichweite, offene Punkte

### 9.1 Alternativen — nur unterscheidende Gründe

**Zuerst die Grenzen, die für den bevorzugten Kandidaten ebenso gelten** und deshalb keine Alternative disqualifizieren: CPython-Spezifik; Abhängigkeit von der unbelegten Voraussetzung, dass das Ereignis für einen über `exec` ausgeführten Modulrumpf ausgelöst wird; grundsätzliche Abschaltbarkeit durch im Prozess laufenden Code — auch `sys.monitoring` kennt `free_tool_id` und `set_events`; Fehlen einer unabhängigen Beobachtung durch A.

| Alternative | **Unterscheidender** Grund | Punkt **zu ihren Gunsten**, offengelegt |
| --- | --- | --- |
| `sys.settrace` | dokumentiert **thread-spezifisch**; **kein** dokumentierter Weg, Ereignisse **je Codeobjekt** zu armieren; dokumentierte **stille Abschaltung**: „If there is any error occurred in the trace function, **it will be unset**"; belegt nach PEP 669 zusätzlich eine Werkzeugkennung | **Das `'call'`-Ereignis deckt den Modulrumpf ausdrücklicher ab**: „A function is called (**or some other code block entered**)" gegenüber „Start of a Python function". Auf dieser Achse dokumentarisch besser gestützt; bei F-a zu berücksichtigen |
| `sys.setprofile` | „it does not make sense to use this in the presence of multiple threads"; keine Armierung je Codeobjekt; Rückgabewert wird nicht verwendet | deckt Aufruf und Rückkehr auch bei gesetzter Ausnahme ab |
| `exec`-Auditereignis | **Positionsgrund:** trägt „the code object as the argument", wird **beim Aufruf** ausgelöst ⇒ belegt **A1**, nicht A2 | ohne Versionsbedingung verfügbar; bleibt als **ergänzender** A1-Beleg möglich. **Keine pauschale Audit-Hook-Forderung** |
| `dict`-Unterklasse als `globals` | `exec()` verlangt „a dictionary (**and not a subclass of dictionary**)" | — |
| Quelltextinstrumentierung | zerstört die Quellbyte-Identität | wäre unabhängig von Interpreterereignissen |
| `marshal`-Digest als Soll | „not compatible between Python versions, even if the version of the format is the same" | kompakt und vollständig innerhalb **einer** gebundenen Version |
| Threadlokale Stapelkorrelation | **bleibt verworfen** | — |

### 9.2 Reichweite

| Bereich | Stand |
| --- | --- |
| SOURCE-Modulrümpfe im kontrollierten Ladeweg | **adressiert**, vorbehaltlich §9.3 und §9.4 |
| Bootstrap-Fenster | **offen**; alles vor der Armierung ist unerfasst |
| Cache-Nutzung | **berührt, nicht gelöst** (§7); E2 unverändert |
| EXTENSION-Module | **offen**; kein Python-Codeobjekt |
| Native Ladebindungen | **offen** |
| Vollständigkeit des kontrollierten Ladewegs / Wegpflicht | **offen.** `unregistered_entry` erkennt Eintritte in **armierte** Objekte ausserhalb des Wegs; **nicht** die Ausführung eines nie armierten Objekts |
| Vollständigkeit von O | **offen** |
| **Abwicklungsnachweis A4** | **offen.** Variante L erschliesst A4 nicht; Option G ist nicht ausgewählt |

**D1 wird nicht stillschweigend verengt.**

### 9.3 Vorausgesetzte, noch unbelegte Eigenschaften

| Kennung | Voraussetzung |
| --- | --- |
| **P-1** | `PY_START` wird für einen über `exec(C, ns)` ausgeführten **Modulrumpf** ausgelöst. Die Dokumentation spricht von „Python function". **Unbelegt; fällt P-1 aus, trägt der gesamte Kandidat nicht** |
| **P-2** | `PY_RETURN` wird für denselben Rahmen ausgelöst (Grundlage der Widerspruchsregel M6) |
| **P-3** | `co_code` liefert unter Spezialisierung **und** unter aktiver Instrumentierung denselben Wert wie vor der Armierung |
| **P-4** | Verhalten bei einer Ausnahme **im** Callback sowie die Ausnahmslosigkeit des vorgesehenen Abfangs — **nicht dokumentiert, nicht nachgewiesen** |
| **P-5** | V-1: höchstens ein aktiver Versuch je Codeobjekt |
| **P-6** | G1: der Loader ruft tatsächlich den vorgesehenen `exec` mit genau C |
| **P-7** | Kein Modul aus Z schaltet das Werkzeug ab oder gibt es frei |
| **P-8** | **Ununterbrochene Armierung und Aktivität des Werkzeugs über den gesamten relevanten Zeitraum.** Die abschliessende `get_local_events`-Abfrage belegt sie **nicht**; dies gehört zum bereits benannten offenen Bereich „durchgehende Wirksamkeit über ein Intervall statt über Zeitpunkte" |

### 9.4 Offene Entscheidungen und spätere Qualifikation

| Nr. | Offene Entscheidung |
| --- | --- |
| F-a | **Versionsbedingung.** `sys.monitoring` ist „Added in version 3.12". **B5 ist offen; hier wird keine Laufzeit ausgewählt.** Ob B5 diese Bedingung aufnimmt oder ein Ersatzweg zugelassen wird — unter Berücksichtigung des in §9.1 offengelegten Punktes zugunsten von `settrace` |
| F-b | Werkzeugkennung und ‑name; Verhalten bei belegter Kennung |
| F-c | **Attributumfang und Typkodierung von CODEID-1**, insbesondere `co_linetable`, `co_exceptiontable`, `co_positions()`, `co_lines()` |
| F-d | Armierung nach dem Versuch beibehalten (hier vorgeschlagen) oder löschen |
| F-e | Ob A die Sollableitung selbst durchführen darf — ein Interpreterlauf in A, der eigener Freigabe bedarf |
| F-f | Nachweisweg für V-1 |
| F-g | Führung von `unregistered_entry` und `capture_status` im Schema |
| F-h | Genaue Feldmenge und Wertebereiche von `capture_status` |
| F-i | **Ob Option G** überhaupt in Betracht kommt — hier **nicht** vorgeschlagen und **nicht ausgewählt**; ein Abwicklungsnachweis bliebe an ihre eigenen, hier nicht ausgearbeiteten Voraussetzungen gebunden |

**Spätere Runtime-Qualifikation:** P-1 bis P-8; Reproduzierbarkeit von CODEID-1 zwischen Ableitung und Lauf; Wirksamkeit der Ereignissuspendierung für den Sendepfad; Vollständigkeit der Dateinamensprüfung über verschachtelte Codeobjekte; Verhalten der gesamten Kette unter Abbruch einschliesslich Siegeldisziplin; Rückwirkungsfreiheit der Armierung gegenüber den BIND-0-Vergleichswerten; **Zählerdisziplin nach §6.4.1 unter Last und unter Abbruch, einschliesslich des Verhaltens bei Fehlern zwischen Callback-Eintritt, Datensatzerzeugung, Übergabe und Rückkehr des Übergabeaufrufs**.

## §10 Einordnung der Aussagen

| Kategorie | Inhalt |
| --- | --- |
| **Durch Primärquellen gestützt** | Ereignisklassifikation (lokale Ereignisse vs. „Other events" mit `PY_UNWIND`); Signaturen `PY_START(code, offset)`, `PY_RETURN(code, offset, retval)`, `PY_UNWIND(code, offset, exception)`; `set_local_events` / `set_events` / `use_tool_id` mit ihren `ValueError`-Bedingungen; Ereignissuspendierung im Callback; „Local events add to global events, but do not mask them"; Unveränderlichkeit der Codeobjekte und `replace()` als Kopie; Attributliste einschliesslich `co_name` und `co_nlocals`; `co_lnotab` deprecated; co_linetable/co_exceptiontable in der Python-3.12-Sprachreferenz nicht als Attribute aufgeführt; co_linetable in PEP 626 beschrieben, sein Format ausdrücklich nicht spezifiziert und veränderbar; exceptiontable als Parameter der instabilen, versionsabhängigen C-API dokumentiert; `exec()`-Semantik und das `dict`-Erfordernis; `compile()`-Signatur; `exec(code, module.__dict__)` aus `importlib`; `settrace`-Eigenschaften; `marshal`-Versionsabhängigkeit |
| **Vorgeschlagene Architekturentscheidungen** | Variante L; getrennte, nicht ausgewählte Option G; Ausführungsregister mit starken Referenzen und `is`-Vergleich; CODEID-1 als unvollständiger Vorschlag; getrennte `co_filename`-Prüfung; Codeobjektklasse G2; Zählerdefinitionen §6.4.1 und Bedingungen H1–H4; Musterkatalog §6.2 mit Auffangregel M-X; `cache_consulted_by_loader`; die Protokoll- und BIND-2-Ergänzungen aus §8 |
| **Vorausgesetzt, noch unbelegt** | **P-1 bis P-8**, insbesondere P-1 (Auslösung für einen über `exec` ausgeführten Modulrumpf), P-2 (Grundlage von M6), P-4 (undokumentiertes Callback-Fehlerverhalten), P-5/V-1 (Eindeutigkeit der Registerauflösung) und **P-8 (ununterbrochene Aktivität)** |
| **Spätere Runtime-Qualifikation** | Die Liste am Ende von §9.4. **Keine dieser Prüfungen ist durchgeführt** |

## §11 Primärquellen

| Quelle | Adresse |
| --- | --- |
| sys.monitoring | https://docs.python.org/3/library/sys.monitoring.html |
| PEP 669 | https://peps.python.org/pep-0669/ |
| Datenmodell — Code objects | https://docs.python.org/3/reference/datamodel.html |
| Built-in Functions — compile, exec | https://docs.python.org/3/library/functions.html |
| importlib | https://docs.python.org/3/library/importlib.html |
| sys — settrace, setprofile, addaudithook, audit | https://docs.python.org/3/library/sys.html |
| marshal | https://docs.python.org/3/library/marshal.html |
| PEP 626 — The co_linetable attribute | https://peps.python.org/pep-0626/#the-co-linetable-attribute |
| Python 3.12 C API — Code Objects | https://docs.python.org/3.12/c-api/code.html |

---

**Status: VORSCHLAG_NICHT_ANGENOMMEN. F1 ist nicht erbracht; O bleibt nicht ableitbar. D1 bleibt offen. Keine unabhängige Prüfung, keine Dokumentationsfreigabe, keine Dokumentanlage. X1 und das bekannte Fragment bleiben unberührt.**
