# BTC-L1 G10-B Field and Helper Contract V1

**Status: APPROVED_FOR_ADOPTION**

Die formale Annahme ist in Abschnitt 12 aufgezeichnet. Alle Abschnitte vor Abschnitt 12 sind im Wortlaut des geprueften Entwurfs belassen; ihre Entwurfs- und Vorschlagsformulierungen werden durch Abschnitt 12 zeitlich eingeordnet und nicht umgeschrieben.

Datum der Ausarbeitung (UTC): 2026-09-10

Repository-Stand der Ausarbeitung: `ea7f5b32d6b481147bb780f6c9319f7ea37faf87`, Branch `main`, Arbeitsverzeichnis sauber

Gebundener Quellcommit fuer alle Quellenaussagen: `3c5927127a03de13d8c80a720f5c8b97a2a36789`

Maschinenlesbare Begleitdatei: `docs/review/evidence/BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10.json`

---

## 1. Status, Umfang und Abgrenzung

### 1.1 Status

Dieser Entwurf ist **DRAFT_NOT_BINDING**. Saemtliche hier mit einer `V-`Kennung versehenen Festlegungen sind **unverbindliche Vorschlaege** und **nicht formal angenommen**. Der Entwurf ist keine Implementierungs-, Test-, Manifest-, Selektions-, Commit-, Push- oder Ausfuehrungsfreigabe und behauptet **keine vollstaendige Implementierungsbereitschaft**.

### 1.2 Umfang

Der Entwurf konsolidiert genau zwei der in den bereits angenommenen Vertraegen ausdruecklich offen gelassenen Restpunkte:

1. die verbleibenden **Feldgrammatiken** des semantischen Ereignisstroms;
2. die verbleibenden **Fehler- und Veto-Abgrenzungen** an der Schnittstelle zur Economics-Hilfsfunktion `authorize_entry`.

Nicht Gegenstand dieses Entwurfs sind: Berechnungsregeln, Kostenmodell, Sizing, Settlement-Formeln, kanonische Equity-Akkumulation, Bootstrap, Kennzahlendefinitionen, Gates, Ausgabeschemata und Abschlussregeln. Diese bleiben unveraendert.

### 1.3 Abgrenzung zu den bereits angenommenen Vertraegen

Unveraendert gueltig und hier **nicht erneut zur Genehmigung gestellt**:

- **P01** — akzeptierte UTC-Zeitstempelgrammatik mit Kalender- und Uhrzeitvalidierung; Annahme fehlender oder durchweg nulliger Bruchteile; Ablehnung jeder von Null verschiedenen Bruchziffer ohne Kuerzung.
- **P02** — leerer `reference_price_text` ausschliesslich auf gueltigem semantischem NOOP mit `executed = 0`, mit Auditaufzeichnung, Klassifikation `EMPTY_REFERENCE_ON_SEMANTIC_NOOP` und Rohursache `UNKNOWN`, und nur wenn saemtliche uebrigen Integritaetspruefungen bestanden sind. Nichtleere syntaktisch ungueltige, nichtendliche oder nichtpositive Referenztexte werden abgelehnt, auch auf NOOP-Ticks. Ausgefuehrte OPEN- und CLOSE-Ereignisse verlangen einen gueltigen Referenztext unabhaengig von einem wirtschaftlichen Veto. Kein Rueckgriff auf das Float-Feld `price` als Ersatz.
- **P03 bis P07** — Dezimalkontext-Parameter, Signalflaggen-Initialisierung, Trap-Einstellungen einschliesslich `FloatOperation`, `Underflow`, `Subnormal`, `Clamped` sowie der lokale NumPy-Fehlerzustand fuer die Bootstrap-Sequenz.
- **K01 bis K08** und saemtliche Festlegungen des Output-/Runtime-Vertrags: Serialisierung, Trade- und Veto-Schemata, Controls-, Audit- und Reconciliation-Felder, Result-Schema, Gates, **Pfadstruktur, Fresh-State- und Abschlussregeln**.
- Die angenommene Stromregel: je vollstaendigem Tick genau ein `market_snapshot` gefolgt von genau einer `execution`, Zwischenereignisse zulaessig; Pruefung der manifestgebundenen Erst- und Letzt-Ticks und der **lueckenlosen Nachfolgerfolge**, nicht bloss steigender Kennungen; Ablehnung doppelter, fehlender, verwaister oder unvollstaendiger Paare sowie inkonsistenter Kombinationen aus `action`, `executed`, Position und Seite; finale semantische Position `FLAT` am Stromende.
- Die angenommenen wirtschaftlichen Kontrollen: `daily_loss_rate >= 0.01`, `daily_fee_rate >= 0.0025`, `realized_drawdown_rate >= 0.05` sperren neue wirtschaftliche Entries in **beiden** Szenarien; Exits bleiben stets erlaubt; hoechstens eine offene Position; Ablehnung ungueltiger und nichtpositiver Kontobasen sowie von Zeitregression.
- Die angenommene Veto-Semantik: ein Veto eroeffnet keine wirtschaftliche Position, verursacht keine hypothetische Gebuehr und erzeugt keinen hypothetischen oder Null-PnL-Trade; sein spaeterer semantischer Exit vervollstaendigt das Veto-Paar; je Szenario gilt `563 = wirtschaftlich geschlossene Trades + vollstaendige Veto-Paare`.
- Die angenommene technische Fehlerregel: Float64-Konversionsfehler und nichtendliche Ergebnisse fuehren zu `TECHNICAL_ERROR` mit `metrics_released = false`; ein `result.json` wird erst nach allen Integritaets- und Reconciliation-Pruefungen freigegeben.

Historische DRAFT-Formulierungen in den angenommenen Dokumenten setzen deren spaetere Annahmeaufzeichnungen **nicht** ausser Kraft.

### 1.4 Redaktionelle Konventionen dieses Entwurfs

- **Decimal-Wert 0** bezeichnet stets den numerischen Dezimalwert null.
- **`quote=None`** bezeichnet stets das nicht gesetzte Quote-Attribut eines strukturell gueltigen Rueckgabeobjekts.
- Das **literale Token `null`** bezeichnet stets eine Zeichenkette mit genau diesem Inhalt im Ereignisstrom.
- Diese drei Bedeutungen werden nirgends vermischt.
- "Quote fehlt" bedeutet bei einem strukturell gueltigen Rueckgabeobjekt genau `quote=None`. Ein **fehlendes Pflichtattribut** des Rueckgabeobjekts ist demgegenueber ein **Strukturfehler** und kein `quote=None`.

---

## 2. Grammatikblock und Feldzuordnung

Alle Regeln gelten als **Ganzstringpruefung** ueber reines ASCII. Kein Trimmen, kein Kuerzen, kein generisches Entkommen, keine Reparatur eines Tokens in die Gueltigkeit hinein.

### 2.1 Zeichenklassen und Basissymbole

```
DIGIT     := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
NZDIGIT   := "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
UPPER     := "A" ... "Z"
UINT      := "0" | NZDIGIT DIGIT*
FRAC      := DIGIT* NZDIGIT
EXP       := "e" ( "+" | "-" ) DIGIT DIGIT+
EMPTY     := ""
```

`EXP` verlangt ein explizites Vorzeichen und mindestens **zwei** Exponentenziffern.

### 2.2 Feldgrammatiken

```
TICK            := NZDIGIT DIGIT*

SNAPSHOT_ID     := "CSV-" DIGIT DIGIT DIGIT DIGIT DIGIT DIGIT DIGIT DIGIT

INT_TOKEN       := "0" | "-"? NZDIGIT DIGIT*

FLOAT_LEX       := "nan"
                 | "-"? "inf"
                 | "-"? UINT "." DIGIT+ EXP?
                 | "-"? UINT EXP

ENTRY_PRICE_LEX := EMPTY | FLOAT_LEX

REF             := EMPTY
                 | "0" "." FRAC
                 | NZDIGIT DIGIT* ( "." FRAC )?

SIDE_AFTER      := EMPTY | "long" | "short"

REASON          := UPPER ( UPPER | DIGIT | "_" )*
```

### 2.3 Feldzuordnung, vorgesehene Leerwerte, Konvertierungsverfahren

| Feld | Ereignis | Grammatik | Leerwert vorgesehen | Konvertierung nach bestandener Ganzstringpruefung | V-ID |
| --- | --- | --- | --- | --- | --- |
| `tick` | beide | `TICK` | nein | Ganzzahl aus den Dezimalziffern des gesamten Tokens. Keine Float-Zwischenstufe. | V-01 |
| `snapshot_id` | `market_snapshot` | `SNAPSHOT_ID` | nein | Ganzzahl aus den acht Ziffern nach dem Praefix `CSV-`. | V-02 |
| `allow_long`, `allow_short`, `regime_v2` | `market_snapshot` | `INT_TOKEN` | nein | Ganzzahl aus dem gesamten Token einschliesslich eines etwaigen fuehrenden Minuszeichens. Keine Float-Zwischenstufe. | V-09 |
| `price` | `market_snapshot` | `FLOAT_LEX` | nein | Float-Konvertierung des vollstaendigen Tokens; danach Endlichkeits- und Kanonizitaetspruefung nach Abschnitt 3.4. | V-04 |
| `reference_price_text` | `market_snapshot` | `REF` | ja, ausschliesslich unter P02 | Bei nichtleerem Token Dezimalkonstruktion aus dem gesamten Token; Ergebnis muss endlich und groesser als der Decimal-Wert 0 sein. | V-08 |
| `timestamp_utc` | `market_snapshot` | akzeptierte UTC-Grammatik nach P01 | nein | unveraendert nach P01. | — |
| `symbol` | `market_snapshot` | OFFEN, siehe Abschnitt 9.1 | — | — | — |
| `action` | `execution` | geschlossene Menge `OPEN_LONG`, `OPEN_SHORT`, `CLOSE_LONG`, `CLOSE_SHORT`, `NOOP` | nein | Zeichenkette unveraendert. | V-12 |
| `executed` | `execution` | genau `0` oder genau `1` | nein | Ganzzahl. | V-12 |
| `position_before`, `position_after` | `execution` | geschlossene Menge `FLAT`, `LONG`, `SHORT` | nein | Zeichenkette unveraendert. | V-12 |
| `side_after` | `execution` | `SIDE_AFTER` | ja, bei `position_after = FLAT` | Zeichenkette unveraendert. | V-12 |
| `entry_price` | `execution` | `ENTRY_PRICE_LEX` | ja, zustandsabhaengig | siehe Abschnitt 3.4; bei leerem Token entfaellt jede Konvertierung. | V-04, V-07 |
| `entry_timestamp_utc` | `execution` | akzeptierte UTC-Grammatik nach P01 | ja, zustandsabhaengig | unveraendert nach P01. | — |
| `reason` | `execution` | `REASON` und geschlossene Wertemenge nach Abschnitt 4 | nein | Zeichenkette unveraendert. | V-10 |

### 2.4 Strukturelle Eigenschaft der Ereigniszeilen

Beide interpretierten Ereignistypen tragen je **neun** Feldschluessel, die im Erzeuger als Literale definiert sind; die Feldreihenfolge ist deterministisch aufsteigend nach Schluesselnamen. Ein fehlender Schluessel ist daher stets ein Befund ueber Beschaedigung oder Trunkierung und niemals ein zulaessiger Zustand.

**Feldverteilung ueber die Ereignistypen.** Das `market_snapshot` traegt `tick`, `snapshot_id`, `timestamp_utc`, `symbol`, `price`, `reference_price_text`, `allow_long`, `allow_short`, `regime_v2`. Die `execution` traegt `tick`, `action`, `executed`, `position_before`, `position_after`, `side_after`, `entry_price`, `entry_timestamp_utc`, `reason`. Insbesondere besitzt das `market_snapshot` selbst **weder `action` noch `executed`**.

---

## 3. Pruef- und Diagnosereihenfolge

### 3.1 Reihenfolge

Je Ereignis, je Feld, in dieser festen Reihenfolge. Die Reihenfolge ist so gewaehlt, dass jede vorgesehene Diagnose auch tatsaechlich erreichbar bleibt.

**a) Schluesselpraesenz.** Alle neun Schluessel des jeweiligen Ereignistyps muessen vorhanden sein. Ein fehlender Schluessel fuehrt zum technischen Abbruch.

**b) Unterscheidung fehlend, leer, literales `null`.** Vor jeder Grammatikpruefung werden drei Zustaende getrennt festgestellt: fehlender Schluessel aus Schritt a; Token der Laenge null; Token mit dem exakten Inhalt `null`.

**c) Literales Token `null`.** Ein Token mit dem exakten Inhalt `null` erhaelt **unmittelbar** eine eigene Diagnose und fuehrt zum technischen Abbruch. Es wird weder als fehlendes Feld noch als Leerwert noch als blosser Grammatikverstoss behandelt. Dies ist eine Diagnosezuordnung, **keine Ausnahme und keine Toleranz**. Belegt: der Logger bildet einen nicht gesetzten Feldwert auf die leere Zeichenkette ab und **niemals** auf `null`; ein literales `null` stammt daher zwingend aus dem Rohtext eines durchgereichten Textfeldes. (V-11)

**d) Vorgesehene Leerwerte.** Nur die in Abschnitt 2.3 als vorgesehen markierten Felder duerfen leer sein. Fuer diese entfallen im Leerfall Grammatikpruefung, Konvertierung und Wertpruefungen. Die zustandsabhaengigen Bedingungen bleiben zwingend; soweit eine Bedingung von der Snapshot-/Execution-Zuordnung abhaengt, wird sie erst in Schritt f nach Abschnitt 3.6 entschieden. Ein leerer Token in einem nicht dafuer vorgesehenen Feld fuehrt zum technischen Abbruch.

**e) Nichtleere regulaere Token.** Ganzstringpruefung gegen die zugeordnete Grammatik, anschliessend die vorgeschriebene Konvertierung und die Wertpruefungen: Endlichkeit bei Float-Feldern; Endlichkeit und Wert groesser als der Decimal-Wert 0 bei nichtleerem `reference_price_text`.

**f) Kanonizitaet, Zuordnung und feldeuebergreifende Pruefungen.** Kanonizitaetspruefung bei Float-Feldern; bei `reference_price_text` ist die Kanonform bereits durch die Grammatik `REF` erzwungen. Danach die vollstaendige Snapshot-/Execution-Zuordnung des Ticks und darauf aufbauend: Kreuztabelle nach Abschnitt 4; Zustandskontinuitaet; Leerheitsbiimplikation fuer `entry_price`; Vergleich des `snapshot_id`-Index gegen `tick`; die zuordnungsabhaengigen Regeln fuer `reference_price_text` und `price` nach Abschnitt 3.6; die aktionsabhaengigen Preisvergleiche nach Abschnitt 3.6.

### 3.2 Einheitliche Fehlerreaktion

Jeder Verstoss in einem der Schritte a bis f fuehrt zum Abbruch des Laufs **vor** jeder Kennzahlenfreigabe. Keine Toleranz, kein Epsilon, keine Reparatur, keine Ersatzwerte, kein Ueberspringen eines Ereignisses. Der Abbruch wird als technischer Fehler gefuehrt, nicht als wirtschaftliches Ergebnis.

### 3.3 Tick- und Snapshot-Kennung

- `tick` erfuellt `TICK`; Rekonstruktion ausschliesslich ueber Ganzzahl-Parsen des vollstaendigen Tokens nach bestandener Ganzstringpruefung, **nie** ueber eine Float-Zwischenstufe. Die tolerante Reader-Konvertierung des CSV-Lesers ist eine Eingabekonvertierung und **kein** Log-Parser. (V-01)
- `snapshot_id` erfuellt `SNAPSHOT_ID`. Jede andere Form, einschliesslich einer Kennung mit dem Praefix `DUMMY-`, ist ein Fehler. Belegt: der gebundene Loop konstruiert ausschliesslich den CSV-Feed; der Stub-Feed mit dem Praefix `DUMMY-` ist aus ihm nicht erreichbar. (V-02)
- **Zusaetzlicher Vergleich:** Fuer jedes `market_snapshot` ist der als Ganzzahl gelesene achtstellige Anteil von `snapshot_id` **gleich** dem `tick`-Wert desselben Ereignisses. (V-03)

**Beweiskraft ausdruecklich begrenzt:** Die Gleichheit schliesst einen positiven Zaehlerversatz aus. Sie belegt **nicht**, dass die Resume-Umgebungsvariable leer war — ungueltige, nicht `CSV-`-praefigierte oder nichtpositive Werte bewirken ebenfalls keinen Vorlauf — und sie belegt **keinen** vollstaendig frischen Gesamtzustand. Die ausdrueckliche Bindung der Prozessumgebung bleibt offen (Abschnitt 9.2).

### 3.4 Float-Felder: Grammatik, Konvertierung, Endlichkeit, Kanonizitaet

Vier getrennte, nacheinander durchlaufene Schritte. Keiner impliziert einen anderen. Anwendbar auf `price` sowie auf **nichtleere** `entry_price`-Token. (V-04)

| Schritt | Vollstaendige Definition |
| --- | --- |
| **F1 — lexikalische Zulassung** | Ganzstringpruefung gegen `FLOAT_LEX` beziehungsweise `ENTRY_PRICE_LEX`. F1 prueft **ausschliesslich die Grammatik** und trifft keine Wertaussage. `FLOAT_LEX` ist eine **echte Obermenge** der tatsaechlich emittierten Zeichenketten: sie laesst auch nichtkanonische Schreibweisen wie `1.50`, `1.0e+16` oder `0.10` zu und ist deshalb keine exakte Beschreibung der Emissionsform. |
| **Konvertierung** | Nach bestandener F1 wird der **vollstaendige** Token in einen Python-`float` konvertiert. Ein Konvertierungsfehler fuehrt zum **technischen Abbruch**. Es wird nichts abgeschnitten, ergaenzt oder umgeschrieben. |
| **F2 — Endlichkeit** | F2 prueft ausdruecklich die **Endlichkeit des konvertierten Wertes**, nicht die Form des Tokens. Ein nichtendlicher konvertierter Wert fuehrt zum technischen Abbruch — unabhaengig davon, ob das Token eine der ausgeschriebenen Sonderschreibweisen war oder ein regulaer geschriebenes numerisches Token, das bei der Konvertierung ueberlaeuft. Der blosse Ausschluss der drei ausgeschriebenen Schreibweisen `nan`, `inf`, `-inf` genuegt nicht und ist F2 nicht gleichwertig. |
| **F3 — Kanonizitaet** | F3 prueft nach bestandener F2 exakt die Zeichengleichheit von `str(konvertierter_float)` mit dem Originaltoken. Damit wird die kanonische Emissionsform vollstaendig geprueft, ohne die Regeln der Darstellungsroutine aufzuzaehlen. |

**Keine Reparatur und keine Zusatzrundung** in irgendeinem dieser Schritte.

**Leere `entry_price`-Token:** Fuer den vorgesehenen leeren Token entfallen Float-Konvertierung, F2 und F3 vollstaendig. Die zustandsabhaengige Pruefung nach Abschnitt 3.5 bleibt zwingend.

`reference_price_text` ist von F1 bis F3 **nicht** erfasst; fuer dieses Feld gelten die Grammatik `REF`, die Dezimalkonstruktion sowie die Endlichkeits- und Positivitaetspruefung.

### 3.5 Zustandsabhaengige Leerheit von `entry_price`

Der `entry_price`-Token ist **genau dann** leer, wenn `position_after` den Wert `FLAT` traegt. Bei `position_after` gleich `LONG` oder `SHORT` ist er nichtleer, endlich und groesser null. (V-07)

Belegt: die Zuruecksetzung auf `FLAT` setzt Position und Einstiegspreis gemeinsam zurueck; alle Schliessungsrueckgaben fuehren `position_after = "FLAT"` mit nicht gesetztem Einstiegspreis; alle NOOP-Rueckgaben reichen den gespeicherten Wert zur unveraenderten Position durch.

### 3.6 Referenzpreis und aktionsabhaengige Preispruefungen

**Zuordnungsabhaengigkeit, vorangestellt.** Die Felder `reference_price_text` und `price` gehoeren zum `market_snapshot`. Die Felder `action` und `executed` gehoeren zur `execution`. Das `market_snapshot` besitzt diese beiden Felder nicht. Jede in diesem Abschnitt formulierte Bedingung, die sich auf ein semantisches NOOP oder auf `executed` bezieht, meint daher stets die **der `execution` desselben Ticks zugeordnete** Aktion und Ausfuehrungsmarkierung. Solche Pruefungen werden erst **nach vollstaendiger Snapshot-/Execution-Zuordnung** entschieden, also in Schritt f der Reihenfolge aus Abschnitt 3.1, und niemals allein aus dem `market_snapshot` heraus.

**Referenzpreis, unveraenderte P02-Bedingungen.** Ein leerer `reference_price_text` ist ausschliesslich dann zulaessig, wenn die zugeordnete `execution` desselben Ticks ein gueltiges semantisches NOOP mit `executed = 0` ist, mit Auditaufzeichnung, Klassifikation `EMPTY_REFERENCE_ON_SEMANTIC_NOOP` und Rohursache `UNKNOWN`, und nur wenn saemtliche uebrigen Integritaetspruefungen bestanden sind. Nichtleere ungueltige, nichtendliche oder nichtpositive Referenztexte werden abgelehnt, auch auf NOOP-Ticks. Ticks, deren zugeordnete `execution` ein ausgefuehrtes OPEN oder CLOSE ist, verlangen einen gueltigen Referenztext unabhaengig von einem wirtschaftlichen Veto. Kein Rueckgriff auf `price` als Ersatz. **Diese Bedingungen sind bereits angenommen und werden hier nicht veraendert.**

**Zusaetzliche vorgeschlagene Kanonform.** Ein nichtleerer `reference_price_text` muss `REF` erfuellen. Ein Token, das zwar eine gueltige Dezimalzahl darstellt, aber nicht dieser Kanonform entspricht — etwa `1.50`, `+1.5`, `0`, `1e3`, `.5`, `01.5` —, ist ein Fehler. Belegt: die Normalisierung im Erzeuger ist exponentfrei, erzwingt Positivitaet und entfernt abschliessende Fraktionsnullen sowie einen abschliessenden Punkt; der gebundene Erzeuger kann die genannten Formen nicht ausgeben. (V-08)

**Wertzustaende des Float-Metadatenfeldes `price`.** (V-05)

| Wertzustand von `price` | Vorgeschlagene Zulassungsregel |
| --- | --- |
| positiv endlich | zulaessig auf jedem Tick |
| **positiv null** | zulaessig **ausschliesslich**, wenn alle folgenden Bedingungen gleichzeitig erfuellt sind: die zugeordnete `execution` desselben Ticks ist ein gueltiges semantisches `NOOP` mit `executed = 0`; `reference_price_text` desselben Snapshots ist leer; saemtliche uebrigen Integritaetspruefungen dieses Ticks sind bestanden. Die Ursache des leeren Referenzwerts wird als `UNKNOWN` gefuehrt. In jedem anderen Fall — insbesondere bei nichtleerem `reference_price_text` sowie bei jeder zugeordneten `execution` mit `executed = 1` — Abbruch. |
| negativ null | Abbruch auf jedem Tick |
| negativ endlich | Abbruch auf jedem Tick |
| nichtendlich | durch F2 ausgeschlossen; Abbruch |

**Abgrenzung, ausdruecklich:** Diese Zulassung des Float-Metadatenfeldes `price` ist eine **zusaetzliche vorgeschlagene Regel**. Sie **folgt nicht bereits aus P02**. P02 regelt daneben ausschliesslich den leeren Referenztext und saemtliche dafuer geltenden Integritaetsbedingungen und bleibt unveraendert.

**Was der Abbruch nicht beweist:** Die Ablehnung von negativ null und negativ endlichen Werten ist eine vorgeschlagene Zulassungsentscheidung, **keine bewiesene Manipulation** und kein Beweis verschiedener Quellzellen. `price` und `reference_price_text` stammen aus derselben Eingabezelle, ihre Konverter haben jedoch verschiedene Darstellungsbereiche: eine hinreichend kleine positive Dezimalzahl kann bei der Float-Konvertierung auf Null runden, waehrend die Dezimalkonvertierung endlich und positiv bleibt. Rein statische Beschreibung; keine Ausfuehrung, keine Plattformqualifikation behauptet. Auch die Ursache eines positiv-null-Wertes bleibt unbestimmt, da dieser Wert zugleich der Vorgabewert bei fehlender, leerer oder unparsebarer Zelle ist.

**Aktionsabhaengige Preisvergleiche.** (V-06)

| Aktionsklasse der zugeordneten `execution` | Vorgeschriebener Vergleich |
| --- | --- |
| `OPEN_LONG`, `OPEN_SHORT` | Die aus `price` und aus dem neuen `entry_price` desselben Ticks konvertierten endlichen Float-Werte werden **ohne Toleranz** auf Gleichheit geprueft. Beide Felder werden im Erzeuger aus demselben Float gespeist. |
| `NOOP` mit offener Position | Die gespeicherten Entry-Metadaten werden auf Konsistenz geprueft und **nicht ueberschrieben**. Der aktuelle Marktpreis wird **nicht** mit dem historischen Einstiegspreis gleichgesetzt; ein Gleichheitsvergleich ist unzulaessig. |
| `CLOSE_LONG`, `CLOSE_SHORT` | Geprueft wird, dass `entry_price` und `entry_timestamp_utc` geleert sind. Kein Preisvergleich gegen geleerte Felder. |
| alle Klassen | **Kein** Gleichheitsvergleich zwischen dem exakten Dezimal-Referenzwert aus `reference_price_text` und dem gerundeten Float aus `price`. |

### 3.7 Ganzzahlige Metadatenfelder

`allow_long`, `allow_short` und `regime_v2` muessen `INT_TOKEN` erfuellen: entweder `0`, oder ein optionales Minuszeichen vor einer positiven Ganzzahl ohne fuehrende Nullen. **Keine** Beschraenkung auf die Menge aus `0` und `1`. Es wird **kein** zusaetzlicher Audit-Zaehler vorausgesetzt und **keine** Wertebereichspruefung eingefuehrt. (V-09)

**Charakter der Regel:** `INT_TOKEN` ist eine **lexikalische Zulassung**. Sie ist ausdruecklich **kein** Beweis, dass jeder passende Token aus dem gebundenen Erzeugungsweg heraus tatsaechlich erzeugbar waere; der dortige Float-Zwischenschritt hat einen begrenzten Wertebereich und erhaelt nicht jede Ganzzahl exakt. Es werden hierzu keine Grenzwerte, Berechnungen oder Tests ergaenzt.

**Vorgabewert-Ambiguitaet:** Nicht konvertierbare Eingaben fallen im Erzeuger auf einen Vorgabewert zurueck — `1` bei `allow_long` und `allow_short`, `0` bei `regime_v2`. Diese Werte bleiben daher **ursaechlich unbestimmt**.

**Ausdruecklich nicht behauptet** wird eine vollstaendige Entscheidungsirrelevanz dieser Werte. Zulaessige Quellwerte und vollstaendige Entscheidungsirrelevanz sind verschiedene Aussagen; Letztere wird hier nicht belegt.

### 3.8 Aktionsabhaengige Zustands-, Seiten- und Metadatenpruefung

Je Ausfuehrungsereignis gilt genau eine Zeile. (V-12)

| `action` | `executed` | `position_before` | `position_after` | `side_after` | Entry-Metadaten |
| --- | --- | --- | --- | --- | --- |
| `OPEN_LONG` | `1` | `FLAT` | `LONG` | `long` | neu gesetzt |
| `OPEN_SHORT` | `1` | `FLAT` | `SHORT` | `short` | neu gesetzt |
| `CLOSE_LONG` | `1` | `LONG` | `FLAT` | leer | geleert |
| `CLOSE_SHORT` | `1` | `SHORT` | `FLAT` | leer | geleert |
| `NOOP` | `0` | ein `p` aus `FLAT`, `LONG`, `SHORT` | dasselbe `p` | passend zur erhaltenen Position | unveraendert erhalten, nicht ueberschreiben |

**Bestimmung der geschlossenen Handelsseite.** Bei `CLOSE_LONG` ist die geschlossene Handelsseite `LONG`, bei `CLOSE_SHORT` ist sie `SHORT`. Sie wird aus der **Aktion** und der **gespeicherten offenen Paarung** bestimmt. **Beim Schliessen darf die geschlossene Handelsseite nicht mit dem bereits geleerten `side_after` gleichgesetzt werden.**

**Abgrenzung:** Angenommen sind die Zustandsuebergaenge selbst, die `side_after`-Wertemenge, die `executed`-Belegung, das Leeren der Entry-Metadaten beim Schliessen und die Nichtueberschreibung der NOOP-Metadaten. **Neu ist ausschliesslich** die ausdrueckliche Ableitungsregel fuer die geschlossene Handelsseite.

---

## 4. Vollstaendige `reason`-Kreuztabelle

Geschlossene Wertemenge von zwanzig Werten. Jeder andere Wert ist ein Fehler. (V-10)

| `reason` | `action` | `executed` | `position_before` | `position_after` |
| --- | --- | --- | --- | --- |
| `TP_LONG_HIT` | `CLOSE_LONG` | `1` | `LONG` | `FLAT` |
| `SL_LONG_HIT` | `CLOSE_LONG` | `1` | `LONG` | `FLAT` |
| `TP_SHORT_HIT` | `CLOSE_SHORT` | `1` | `SHORT` | `FLAT` |
| `SL_SHORT_HIT` | `CLOSE_SHORT` | `1` | `SHORT` | `FLAT` |
| `LONG_TIME_STOP_HIT` | `CLOSE_LONG` | `1` | `LONG` | `FLAT` |
| `SHORT_TIME_STOP_HIT` | `CLOSE_SHORT` | `1` | `SHORT` | `FLAT` |
| `HOLD_NO_EXECUTION` | `NOOP` | `0` | ein `p` aus `FLAT`, `LONG`, `SHORT` | dasselbe `p` |
| `BUY_FROM_FLAT` | `OPEN_LONG` | `1` | `FLAT` | `LONG` |
| `BUY_ALREADY_LONG` | `NOOP` | `0` | `LONG` | `LONG` |
| `BUY_CLOSES_SHORT` | `CLOSE_SHORT` | `1` | `SHORT` | `FLAT` |
| `SELL_FROM_FLAT` | `OPEN_SHORT` | `1` | `FLAT` | `SHORT` |
| `SELL_ALREADY_SHORT` | `NOOP` | `0` | `SHORT` | `SHORT` |
| `SELL_CLOSES_LONG` | `CLOSE_LONG` | `1` | `LONG` | `FLAT` |
| `UNKNOWN_INTENT` | `NOOP` | `0` | ein `p` aus `FLAT`, `LONG`, `SHORT` | dasselbe `p` |
| `LOSS_CLUSTER_GATE_BLOCKED_ENTRY` | `NOOP` | `0` | `FLAT` | `FLAT` |
| `GUARD_GATE_CLOSED` | `NOOP` | `0` | `FLAT` | `FLAT` |
| `GUARD_KILL_LEVEL_HARD` | `NOOP` | `0` | `FLAT` | `FLAT` |
| `GUARD_KILL_LEVEL_EMERGENCY` | `NOOP` | `0` | `FLAT` | `FLAT` |
| `GUARD_INVALID_GATE_MODE` | `NOOP` | `0` | `FLAT` | `FLAT` |
| `GUARD_EXECUTION_BLOCKED` | `NOOP` | `0` | `FLAT` | `FLAT` |

### 4.1 Nebenbedingungen der Kreuzpruefung

- Saemtliche Zeilen mit `action = CLOSE_LONG` oder `action = CLOSE_SHORT`: zusaetzlich `side_after` leer, `entry_price` leer, `entry_timestamp_utc` leer. Die Anzahl dieser Tabellenzeilen ist nicht mit der Anzahl der Quell-Rueckgabestellen zu verwechseln; die Quellenuebersicht in Abschnitt 8.1 fuehrt sechs Rueckgabestellen mit Schliessungsaktion auf, aus denen mehr als sechs `reason`-Werte hervorgehen.
- `BUY_FROM_FLAT`: `side_after` gleich `long`, Entry-Metadaten neu gesetzt. `SELL_FROM_FLAT`: `side_after` gleich `short`, Entry-Metadaten neu gesetzt.
- `BUY_ALREADY_LONG`: `side_after` gleich `long`. `SELL_ALREADY_SHORT`: `side_after` gleich `short`.
- `HOLD_NO_EXECUTION` und `UNKNOWN_INTENT`: `side_after` wird unveraendert aus dem Zustand durchgereicht und muss zur erhaltenen Position passen.
- `LOSS_CLUSTER_GATE_BLOCKED_ENTRY`: `side_after` leer, `entry_price` leer, `entry_timestamp_utc` leer. Beide Aufrufstellen im Erzeuger uebergeben die Position `FLAT`.
- Die fuenf `GUARD_`-Zeilen: `side_after` wird unveraendert aus dem Zustand gelesen; der Erzeuger erzwingt dort **keine** Leerheit. Erwartet wird bei `FLAT` der leere Wert; eine Abweichung ist ein Zustandsbefund, kein Grammatikverstoss. Die Position ist stets `FLAT`, weil die Ersetzung durch die Guard-Entscheidung nur bei Eintrittskandidaten erfolgt, was `FLAT` voraussetzt.

### 4.2 Geltungsklarstellungen

Die `GUARD_`-Werte sind **zulaessige Quellwerte** und werden **nicht allein wegen ihres Praefixes abgelehnt**; sie unterliegen derselben Kreuzpruefung wie alle uebrigen Werte. Ein durch die Legacy-Schicht blockiertes `NOOP` ist **kein** wirtschaftliches Veto — dies ist bereits angenommen und bleibt unveraendert. Es wird **keine** zusaetzliche Auswertung anderer Ereigniskategorien eingefuehrt.

**Abgrenzung:** Angenommen ist die Ablehnung inkonsistenter Kombinationen aus `action`, `executed`, Position und Seite. **Neu** sind allein die geschlossene Wertemenge und diese explizite Kombinationszuordnung.

---

## 5. Vorgeschlagene Reihenfolge von Integritaetspruefung, wirtschaftlichen Kontrollen und Helper-Aufruf

(V-13)

### 5.1 Logischer Vorrang

Ein gueltiges Kontrollveto verhindert `ENTRY_ACCEPTED` **unabhaengig** vom Ergebnis der Economics-Hilfsfunktion. Ein positives Helper-Ergebnis belegt ausschliesslich die Zustimmung dieser Hilfsfunktion und ersetzt **keine** Kontrolle.

### 5.2 Vorgeschlagene zeitliche Ausfuehrungsreihenfolge

Je semantischem OPEN und je Szenario:

1. **Strom- und Paarungspruefung** des Ticks einschliesslich der aktionsabhaengigen Zustands-, Seiten- und Metadatenpruefung nach Abschnitt 3.8 und der Kreuztabelle nach Abschnitt 4.
2. **Referenzpreispruefung** des OPEN-Snapshots nach den unveraenderten P02-Bedingungen und der Kanonform nach Abschnitt 3.6, mit Umwandlung in einen Dezimalwert.
3. **Feld- und Metadatenpruefungen** nach den Abschnitten 3.3 bis 3.7.
4. **Fortschreibung des Buchhaltungszustands** aus gebuchten Betraegen und Pruefung der Kontobasen nach Abschnitt 7.4.
5. **Kontrollpruefung.** Bei erfuelltem Limit — `daily_loss_rate >= 0.01`, `daily_fee_rate >= 0.0025` oder `realized_drawdown_rate >= 0.05` — ergeht `ENTRY_VETOED`; die Schritte 6 und 7 entfallen.
6. **Nur ohne Kontrollveto:** Sizing-Eingaben als Dezimalwerte bilden und die Quote erstellen.
7. **Klassifikation** des Rueckgabeobjekts nach Abschnitt 6.

**Die Schritte 1 bis 3 duerfen durch ein Kontrollveto nicht uebersprungen werden.** Ein Kontrollveto verlangt umgekehrt **nicht** die Berechnung einer anschliessend verworfenen wirtschaftlichen Quote.

### 5.3 Abgrenzung

Die Nichtumgehung der Kontrollen ist bereits angenommen und wird hier nicht erneut zur Genehmigung gestellt. **Neu ist allein die konkrete Reihenfolge und Integration.** Der Vorschlag aendert keine Berechnungsregel. Er stellt die Verwendung der Economics-Hilfsfunktionen **nicht** als beschlossen dar: deren Wiederverwendung setzt nach den angenommenen Vertraegen eine Qualifikation gegen die genehmigten Regeln voraus, und die Helper-Integration ist ausdruecklich als offene Auflage gefuehrt.

---

## 6. Vollstaendige `EntryAuthorization`-Zuordnung

(V-14, V-15, V-16, V-17)

### 6.1 Geltungsbereich und Struktur

Diese Zuordnung gilt **ausschliesslich** fuer ein von `authorize_entry` zurueckgegebenes `EntryAuthorization`-Objekt. Es besitzt **fuenf** Felder:

```
allowed      : bool
reason_code  : str
findings     : tuple[str, ...]
quantity     : Decimal
quote        : Optional[EntryEconomicsQuote]
```

Vorgeschlagene Struktur-, Typ- und Endlichkeitspruefungen, vor jeder Mengen- oder Codeauswertung:

| Feld | Pruefung |
| --- | --- |
| `allowed` | ist tatsaechlich ein Wahrheitswert vom Typ `bool` |
| `reason_code` | ist eine Zeichenkette vom Typ `str` |
| `findings` | ist ein Tupel, dessen saemtliche Elemente Zeichenketten sind |
| `quantity` | ist ein `Decimal` und endlich |
| `quote` | ist entweder `quote=None` oder ein `EntryEconomicsQuote`, dessen fuer die Auswertung erforderliche Felder vorhanden, vom erwarteten Typ und gueltig sind — insbesondere `quantity`, `entry_notional_quote`, `modeled_stop_loss_quote`, `risk_budget_quote`, `notional_cap_quote` |

**Saemtliche Mengenpruefungen erfolgen erst nach bestandener Typ- und Endlichkeitspruefung.**

Ein **fehlendes Pflichtattribut** des Rueckgabeobjekts ist ein **Strukturfehler** und faellt unter die Auffangregel; er ist **nicht** mit `quote=None` gleichzusetzen.

Zur wirtschaftlichen Klassifikation werden **keine Meldungstexte aus `findings` ausgewertet**; `findings` wird ausschliesslich strukturell geprueft. Die **Ablagezuordnung** protokollierter `findings`-Inhalte — ob, wo und in welchem Artefakt sie festgehalten werden — ist durch die angenommenen Ausgabeschemata nicht festgelegt und bleibt hiermit ausdruecklich **OFFEN**; dieser Entwurf fuehrt dafuer **kein** zusaetzliches Pflichtfeld und **kein** zusaetzliches Audit-Artefakt ein.

### 6.2 Code-Mengen

```
CODES_ERFOLG       = { PEE_AUTHORIZED }

CODES_VETO         = { PEE_QUANTITY_ZERO,
                       PEE_QUANTITY_BELOW_MIN,
                       PEE_NOTIONAL_BELOW_MIN }

CODES_GRENZE       = { PEE_RISK_LIMIT_EXCEEDED,
                       PEE_NOTIONAL_LIMIT_EXCEEDED }

CODES_QUOTE_FEHLER = { PEE_CONFIG_INVALID,
                       PEE_INPUT_INVALID,
                       PEE_INPUT_FLOAT_NOT_ALLOWED,
                       PEE_SIDE_INVALID,
                       PEE_PHASE_INVALID,
                       PEE_STOP_DIRECTION_INVALID }
```

### 6.3 Pruefreihenfolge der Quelle

Die Codes sind durch die Reihenfolge der Pruefungen im Erzeuger **wechselseitig ausschliessend und geordnet**:

```
1. quote.quantity <= Decimal 0                              -> PEE_QUANTITY_ZERO
2. quote.quantity < config.min_quantity                     -> PEE_QUANTITY_BELOW_MIN
3. quote.entry_notional_quote < config.min_notional_quote   -> PEE_NOTIONAL_BELOW_MIN
4. quote.modeled_stop_loss_quote > quote.risk_budget_quote  -> PEE_RISK_LIMIT_EXCEEDED
5. quote.entry_notional_quote > quote.notional_cap_quote    -> PEE_NOTIONAL_LIMIT_EXCEEDED
6. sonst                                                    -> PEE_AUTHORIZED
```

### 6.4 Vollstaendige Zuordnung

| Fall | `allowed` | `quote` | `reason_code` | `findings` | Mengen- und Reihenfolgeinvarianten | Reaktion |
| --- | --- | --- | --- | --- | --- | --- |
| **Erfolgsfall** | `True` | gesetzt und gueltig | aus `CODES_ERFOLG` | leeres Tupel, genau 0 Eintraege | `quantity` stimmt mit `quote.quantity` ueberein und ist groesser als der Decimal-Wert 0. Zusaetzlich: `quote.quantity >= config.min_quantity`; `quote.entry_notional_quote >= config.min_notional_quote`; `quote.modeled_stop_loss_quote <= quote.risk_budget_quote`; `quote.entry_notional_quote <= quote.notional_cap_quote` | Helper-Zustimmung. `ENTRY_ACCEPTED` erst nach saemtlichen vorgeschriebenen Kontrollen nach Abschnitt 5 |
| **`PEE_QUANTITY_ZERO`** | `False` | gesetzt | `PEE_QUANTITY_ZERO` | genau 1 Eintrag | `quantity` ist der Decimal-Wert 0 und `quote.quantity` ist der Decimal-Wert 0. Belegt: die Abrundungsfunktion validiert ihre Eingangsmenge als nichtnegativ und liefert bei einem Ergebnis von null exakt den Decimal-Wert 0, weshalb die Bedingung `quote.quantity <= Decimal 0` gleichbedeutend mit Gleichheit zum Decimal-Wert 0 ist | wirtschaftliches Veto |
| **`PEE_QUANTITY_BELOW_MIN`** | `False` | gesetzt | `PEE_QUANTITY_BELOW_MIN` | genau 1 Eintrag | `quantity` stimmt mit `quote.quantity` ueberein. Reihenfolgeinvariante: `quote.quantity` groesser als der Decimal-Wert 0 — sonst haette Pruefung 1 gegriffen — und `quote.quantity < config.min_quantity` | wirtschaftliches Veto |
| **`PEE_NOTIONAL_BELOW_MIN`** | `False` | gesetzt | `PEE_NOTIONAL_BELOW_MIN` | genau 1 Eintrag | `quantity` stimmt mit `quote.quantity` ueberein. Reihenfolgeinvariante: `quote.quantity` groesser als der Decimal-Wert 0; `quote.quantity >= config.min_quantity`; `quote.entry_notional_quote < config.min_notional_quote` | wirtschaftliches Veto |
| **`PEE_RISK_LIMIT_EXCEEDED`** | `False` | gesetzt | `PEE_RISK_LIMIT_EXCEEDED` | genau 1 Eintrag | `quantity` stimmt mit `quote.quantity` ueberein. Reihenfolgeinvariante: Pruefungen 1 bis 3 nicht erfuellt; `quote.modeled_stop_loss_quote > quote.risk_budget_quote` | vorgeschlagener technischer Abbruch, kein Veto |
| **`PEE_NOTIONAL_LIMIT_EXCEEDED`** | `False` | gesetzt | `PEE_NOTIONAL_LIMIT_EXCEEDED` | genau 1 Eintrag | `quantity` stimmt mit `quote.quantity` ueberein. Reihenfolgeinvariante: Pruefungen 1 bis 4 nicht erfuellt; `quote.entry_notional_quote > quote.notional_cap_quote` | vorgeschlagener technischer Abbruch, kein Veto |
| **Quote-Erstellungsfehler** | `False` | `quote=None` | aus `CODES_QUOTE_FEHLER` | genau 1 Eintrag | `quantity` ist der Decimal-Wert 0; es existiert keine Quote, daher findet kein Mengenabgleich statt | vorgeschlagener technischer Abbruch, kein Veto; bewiesene Ursache unbestimmt |
| **Auffangregel** | beliebig | beliebig | beliebig | beliebig | jede Rueckgabe, die nicht genau eine der vorstehenden Zeilen vollstaendig erfuellt, einschliesslich aller dort genannten Struktur-, Mengen- und Reihenfolgebedingungen | vorgeschlagener technischer Abbruch mit dem vorgeschlagenen neuen Code `HELPER_RESULT_UNCLASSIFIED` |

### 6.5 Reichweite der Auffangregel

Die Auffangregel ist **abschliessend**. Sie erfasst unter anderem: verletzte Struktur-, Typ- oder Endlichkeitspruefungen aus Abschnitt 6.1; ein fehlendes Pflichtattribut des Rueckgabeobjekts; ein `findings`-Tupel mit abweichender Elementzahl gegenueber der jeweiligen Zeile; unbekannte oder kuenftig ergaenzte `reason_code`-Werte; verletzte Mengenkonsistenz in jeder Zeile, etwa `quantity` ungleich `quote.quantity` in einem Veto- oder Grenzfall, ein von der Vorgabe abweichender Mengenwert bei `PEE_QUANTITY_ZERO` oder bei einem Quote-Erstellungsfehler, eine nicht positive Menge im Erfolgsfall; verletzte Reihenfolgeinvarianten, etwa `PEE_NOTIONAL_BELOW_MIN` bei gleichzeitig unterschrittener Mindestmenge; `allowed = True` mit `quote=None` oder mit einem von `PEE_AUTHORIZED` abweichenden Code; `allowed = False` mit gesetzter Quote und einem Code aus `CODES_QUOTE_FEHLER`; `allowed = False` mit `quote=None` und einem Code aus `CODES_VETO` oder `CODES_GRENZE`; Rueckgaben, die mehrere Zeilen zugleich erfuellen. Die Aufzaehlung ist beispielhaft, die Regel selbst abschliessend.

### 6.6 Begruendung der Klassifikation der Grenzueberschreitungen

`PEE_RISK_LIMIT_EXCEEDED` und `PEE_NOTIONAL_LIMIT_EXCEEDED` sind unter **exakter** Arithmetik unerreichbar: die Menge ist das Minimum aus Risiko- und Notionalmenge und wird anschliessend abwaerts gerundet. Erreichbar sind sie nur ueber Rundung, insbesondere in der Abrundungsfunktion, in der die Division vor der Abrundung selbst gerundet wird. Dies ist eine **Ableitung, kein ausgefuehrter Test**; die Runtime-Qualifikation steht aus. Bestehende Fehlercodes werden nicht umbenannt.

### 6.7 Begruendung der Klassifikation der Quote-Erstellungsfehler

Diese sechs Codes entstehen dadurch, dass die Quote-Erstellung eine Vorbedingung verletzt und die Hilfsfunktion die Ausnahme in `allowed = False` mit `quote=None` umwandelt. **Fehlerreaktion und bewiesene Ursache bleiben getrennt:** eine verletzte Vorbedingung belegt fuer sich **keinen** Programmierfehler des Evaluators — eine nichtpositive Equity kann auch ein wirtschaftlich erreichter Kontozustand sein. Die Ursache wird als unbestimmt gefuehrt.

**Bekannte Codeueberdeckung, hiermit nicht aufgeloest:** Ein wirtschaftlich degenerierter modellierter Stop-Verlust je Einheit fuehrt im Erzeuger zum selben Code wie echte Eingabefehler. Da die Reaktion in beiden Auslegungen identisch ist — technischer Abbruch —, wird **keine** zusaetzliche Berechnungskette zur Ursachenunterscheidung als Vertragsvoraussetzung eingefuehrt (siehe Abschnitt 9.3, zurueckgestellte Erweiterung).

---

## 7. Getrennte Behandlung ausserhalb der `EntryAuthorization`-Rueckgabe

Die folgenden Faelle liefern **kein** `EntryAuthorization`. Sie duerfen **nicht** wegen fehlender `allowed`- oder `quote`-Felder unter die Auffangregel aus Abschnitt 6 fallen.

### 7.1 Propagierende Ausnahmen aus der Quote-Erstellung

Ausnahmen, die keine Helper-Ausnahme sind — insbesondere Dezimal-Trap-Bedingungen aus den angenommenen Einstellungen P05 und P06 —, werden vom Auffangblock der Hilfsfunktion **nicht** gefangen und propagieren. Reaktion: technischer Abbruch mit Signalnamen und Rechenphase.

**Abgrenzung technischer Signalbehandlung von neuen Fehlercodes:** Dass Dezimal-Trap-Bedingungen Fehler sind, ist bereits angenommen (P06); ebenso der lokale NumPy-Fehlerzustand fuer die Bootstrap-Sequenz (P07) und die dort abweichende Behandlung des Unterlaufs. Diese Signalbehandlung wird hier **nicht** veraendert und ist keine neue Festlegung. Neu und vorgeschlagen ist ausschliesslich der Code `HELPER_RESULT_UNCLASSIFIED` aus Abschnitt 6 sowie der Code `ECONOMIC_LEDGER_INCONSISTENCY` aus Abschnitt 7.5.

### 7.2 Konfigurationskonstruktion

Die Validierung des Economics-Profils erfolgt bei der Konstruktion und damit **vor** jedem Aufruf der Autorisierungsfunktion. Eine dort geworfene Ausnahme fuehrt zum technischen Abbruch vor jeder Kennzahl.

### 7.3 Settlement

Die Settlement-Funktion besitzt **kein** Abfangen. Fingerprint-Abweichung, eine Menge kleiner oder gleich dem Decimal-Wert 0, nichtpositive Equity oder nichtpositiver Hoechststand sowie ein Hoechststand unterhalb der Equity propagieren unmittelbar. Reaktion: technischer Abbruch.

**Fingerprint-Abweichung.** (V-21) Sie belegt eine **Identitaetsinkonsistenz** zwischen dem in der Quote gespeicherten Fingerprint und der beim Settlement uebergebenen Konfiguration. Eine Vermischung des nominalen und des Stress-Szenarios ist eine **moegliche, nicht die einzige** Ursache. Angenommen sind getrennte Konten, Sizing- und Veto-Entscheidungen je Szenario; neu sind Reaktion und Ursachenformulierung.

### 7.4 Nichtpositive Kontobasen in drei getrennten Phasen

(V-18) Die grundsaetzliche Ablehnung ungueltiger und nichtpositiver Kontobasen sowie von Zeitregression ist **bereits angenommen**. Neu sind allein die Phasen-, Code- und Integrationszuordnung:

| Phase | Quellverhalten | Vorgeschlagene Reaktion |
| --- | --- | --- |
| **Quote-Erstellung** | Die Ausnahme wird von der Autorisierungsfunktion in `allowed = False` mit `quote=None` umgewandelt | Behandlung nach der Zeile Quote-Erstellungsfehler in Abschnitt 6.4 |
| **Settlement** | Die Ausnahme propagiert unveraendert; es existiert kein Abfangen | technischer Abbruch nach Abschnitt 7.3 |
| **Evaluator-eigener Ledger** | Keine gebundene Quelle; die Pruefung ist vollstaendig evaluator-eigen | Pruefung der Tagesstart-Equity und des realisierten Hoechststands vor jeder Ratenbildung, damit keine Division mit nichtpositivem Nenner stattfindet |

### 7.5 Evaluator-eigene Ledger-Pruefungen

(V-20) Die Kontrolle "hoechstens eine offene Position" wird **im wirtschaftlichen Ledger jedes Szenarios** durchgesetzt: eine akzeptierte Eroeffnung ist nur zulaessig, wenn in diesem Szenario keine wirtschaftliche Position offen ist. Ein Verstoss fuehrt zum technischen Abbruch unter dem vorgeschlagenen Code `ECONOMIC_LEDGER_INCONSISTENCY`. Die semantische Positionskette nach Abschnitt 3.8 ist zusaetzliche Evidenz, aber **nicht** der einzige moegliche Nachweis einer korrekten wirtschaftlichen Implementierung.

Belegt: das Economics-Modul fuehrt keinen Positionszustand; weder die Autorisierungs- noch die Settlement-Funktion kann diese Kontrolle leisten.

Angenommen sind "hoechstens eine offene Position" und die getrennten wirtschaftlichen Konten je Szenario. Neu sind **Durchsetzungsort** und der vorgeschlagene Code.

---

## 8. Quellenbindungen

Alle Quellenaussagen dieses Entwurfs beruhen ausschliesslich auf lesenden Zugriffen auf den gebundenen Quellcommit.

**Gebundener Quellcommit:** `3c5927127a03de13d8c80a720f5c8b97a2a36789`

### 8.1 Quelldateien mit ausdruecklicher Hash-Bindung in den angenommenen Vertraegen

Alle SHA256-Werte wurden am gebundenen Commit nachgerechnet und stimmen mit den in den angenommenen Vertraegen dokumentierten Bindungen ueberein.

| Pfad | SHA256 | In diesem Entwurf herangezogene Stellen |
| --- | --- | --- |
| `live_l1/io/market.py` | `014bbf7328c4bd354fb8a254979ef463670e49557c5ed89e5628a3b35dc8cd0e` | 37-46 Ganzzahlkonvertierung; 49-58 Float-Konvertierung; 61-64 Textnormalisierung; 67-82 kanonischer positiver Dezimaltext; 85-86 Snapshot-Kennung; 89-102 Kennungs-Parsen fuer Resume; 105-121 Snapshot-Datenstruktur; 123-153 Stub-Feed mit Praefix `DUMMY-`; 168-187 Feed-Konstruktion und Umgebungs-Resume; 189-202 Vorlauf; 208-238 Snapshot-Erzeugung |
| `live_l1/core/loop.py` | `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058` | 17 Feed-Import; 71-76 Guard-Codeabbildung; 79-100 blockierte Ausfuehrungsentscheidung; 102-140 Guard-Wrapper und Eintrittskandidat; 972-976 Feed-Konstruktion; 1029 Schleifenbedingung; 1040 Tickerzeugung; 1043-1052 Feed-Erschoepfung; 1110-1126 `market_snapshot`; 1199-1206 Ausfuehrungsaufruf; 1242-1257 `execution`; 1288-1305 Zustandsfortschreibung und Persistenz |
| `live_l1/logs/logger.py` | `cbfb29708bc81bbf7f2d524abe10a21382213973f897038bc8c315bad1323cfd` | 30-37 Feldescaping und Abbildung nicht gesetzter Werte auf die leere Zeichenkette; 56-97 Zeilenaufbau und deterministische Feldreihenfolge |
| `live_l1/core/execution.py` | `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3` | 54-62 Entscheidungsdatenstruktur; 208-228 Loss-Cluster-Eintrittspruefung; 230-296 Normalisierung, sichere Konvertierungen, Attributsicherung, Ruecksetzung auf `FLAT`; 500-517 blockierte Eintrittsentscheidung; 602-611, 645-654, 694-703, 741-750, 842-851, 931-940 sechs Rueckgabestellen mit Schliessungsaktion; 752-762, 803-812, 892-901, 942-951 NOOP-Rueckgaben; 767-772, 856-861 Aufrufstellen der blockierten Eintrittsentscheidung; 791-800, 880-889 Eroeffnungsrueckgaben |
| `live_l1/core/paper_economics.py` | `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae` | 33-48 Codekonstanten; 51-57 Ausnahmeklasse; 60-91 Dezimalkonvertierung; 94-111 Positivitaets- und Nichtnegativitaetspruefungen; 149-155 Seitenvalidierung; 180-290 Profilvalidierung; 317-325 Fingerprint; 354-360 `EntryAuthorization`; 436-443 Abrundung auf den Mengenschritt; 446-542 Quote-Erstellung; 545-619 Autorisierung einschliesslich Fehler-, Ablehnungs- und Erfolgsrueckgaben; 622-715 Settlement |
| `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` | `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292` | 26-58 gebundene Prozessumgebung; 120-188 semantische Ereignisserialisierung mit sortierten Feldern; 248-257 Abschlusspruefungen des Laufs |

### 8.2 Weitere am selben Commit gelesene Quelldateien

Diese Dateien sind ueber den gebundenen Commit vollstaendig identifiziert, in den angenommenen Vertraegen jedoch nicht zusaetzlich einzeln per SHA256 aufgefuehrt.

| Pfad | Herangezogene Stellen |
| --- | --- |
| `live_l1/core/clock.py` | 40 Kommentar zur Trennung von Tickerzeugung und Feed; 46-57 Initialisierung; 75-99 Tickvergabe mit Vorabinkrement |
| `live_l1/core/feature_snapshot.py` | 88-112 Durchreichen der Snapshot-Felder |
| `live_l1/guards/guards.py` | 70-97 Guard-Auswertung und vollstaendige Rueckgabemenge |
| `live_l1/core/intent_fusion.py` | 91-103 Normalisierung der Gate-Felder |
| `live_l1/state/state_store.py` | 91-171 Zustandsinitialisierung und -laden |

### 8.3 Bestehende Vertragsdateien

Diese acht Dateien wurden vor und nach der Erstellung dieses Entwurfs auf unveraenderten Inhalt geprueft. Repository-Stand: `ea7f5b32d6b481147bb780f6c9319f7ea37faf87`.

| Pfad | SHA256 |
| --- | --- |
| `docs/review/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.md` | `628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e` |
| `docs/review/evidence/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.json` | `21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a` |
| `docs/review/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.md` | `7962f6d9dbd66b9c6e3ea3a66b46b60ac765821deabd7f00ed8b1536daaa6b53` |
| `docs/review/evidence/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.json` | `90b99bac40c7f640ba2df69e6f97a750e25b0762f83a8c6fc973184a3189e830` |
| `docs/review/BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08.md` | `c7776c3ceac5939e3936b429e562830af9f0e90667a65405a0ba5f44a44ab5ff` |
| `docs/review/evidence/BTC_L1_G10B_PARSER_NUMERIC_CONTRACT_V1_2026-09-08.json` | `6d9dbd65a9e16042d95719016e9d0259b0b20eb2ca609674950012769918ef3c` |
| `docs/review/BTC_L1_G10B_OUTPUT_RUNTIME_CONTRACT_V1_2026-09-09.md` | `e57c1970c30982db3fb8de9dc21e4c24378ff2747c64f7c207ef181c9627e7a9` |
| `docs/review/evidence/BTC_L1_G10B_OUTPUT_RUNTIME_CONTRACT_V1_2026-09-09.json` | `ae518b6a05a30651bd064a9d82c3141db62ddb4c299897d3f9224218bcbe7f26` |

Keine dieser Dateien wurde veraendert.

---

## 9. Offene Vertragsbindungen und zurueckgestellte Erweiterungen

### 9.1 Weiterhin offene Feldgrammatiken

| Gegenstand | Stand |
| --- | --- |
| `symbol` im `market_snapshot` | **OFFEN.** Der Wert wird aus der Laufkonfiguration uebernommen und unveraendert durchgereicht. Es wird hier keine Grammatik improvisiert. |

Alle uebrigen Felder der beiden interpretierten Ereignistypen sind in Abschnitt 2.3 zugeordnet.

### 9.2 Weiterhin offene konkrete Bindungen

Hier werden **keine Werte erfunden**.

| Bindung | Stand |
| --- | --- |
| Konkreter `run_id`-Wert des Laufs | offen; entsteht erst beim autorisierten Lauf |
| Konkrete Eingabedateiidentitaeten des Evaluators, insbesondere Pfad und Pruefsumme des semantischen Stream-Laufartefakts | offen |
| Konkrete Evidenzartefakte des Laufs und ihre Pruefsummen | offen |
| Runtime-Identitaeten: Python-, NumPy-, Plattform- und Implementierungsidentitaet | offen; vor Beobachtung neuer Selektionskennzahlen zu binden |
| Dependency-Lock und Evaluator-Identitaet | offen |
| `expected_first_tick` und `expected_last_tick` als Vertragsbindung | offen. Quellenseitig belegt ist lediglich, dass der Loop-Tick bei 1 beginnt; daraus wird hier keine Bindung abgeleitet. Bereits gebunden und unberuehrt: erwartete Tickzahl, erwartete Ereigniszahl, erwartete semantische Tradezahl, erwarteter Stream-Hash |
| Bindung der Prozessumgebung, insbesondere der Resume-Umgebungsvariablen | offen; der Vergleich aus Abschnitt 3.3 ersetzt diese Bindung nicht |
| Helper-Integration und Qualifikation wiederverwendeter Hilfsfunktionen | offen; Abschnitt 5 schlaegt eine Reihenfolge vor, entscheidet aber nicht ueber die Verwendung |
| Ablagezuordnung protokollierter `findings`-Inhalte | offen; siehe Abschnitt 6.1. Dieser Entwurf fuehrt dafuer kein Pflichtfeld und kein Audit-Artefakt ein |
| Synthetische Qualifikation; die Fixtures der angenommenen Vertraege | offen, NICHT AUSGEFUEHRT |
| Vollstaendiges Kandidatenmanifest vor historischer Selektionsauswertung | offen |
| Historische Trade-Normalisierung | offengelegte Provenienzluecke; kein Ersatzalgorithmus |

**Unveraendert bereits angenommen und hier nicht wieder geoeffnet:** die Pfadstruktur `/home/workstation/jobs/btc-l1-fast-replay-v4-cert-20260902/evaluator_results/<run_id>/`, die Fresh-State-Regeln (exklusive Neuanlage, keine Ueberschreibung, keine Wiederverwendung, Teilartefakte als `.partial`, nach Abbruch nur ein neuer Lauf) sowie die Abschlussregeln um `completion.json`, `result.json`, `metrics_released` und die Statuswerte.

### 9.3 Zurueckgestellte Erweiterungen

Keine dieser Positionen ist Voraussetzung fuer den notwendigen Restvertrag. Keine wird ohne ausdrueckliche Entscheidung zu einem Pflichtfeld, einer Auditpflicht oder einer Abbruchbedingung des angenommenen Ausgabevertrags. Die bestehenden Pruefungen von Ereignisstrom, Zustandskontinuitaet und zulaessigen Quellwerten bleiben davon unberuehrt.

| Gegenstand | Anmerkung |
| --- | --- |
| Zusaetzliche Abbruchregel bei `GUARD_`-Werten im `reason`-Feld | zurueckgestellt; aus dem bestehenden Vertrag folgt keine Abbruchpflicht. Die Werte bleiben ueber Abschnitt 4 als zulaessige Quellwerte erfasst |
| Tickweise Auswertung des Guard-Grundes aus der Zustandsfortschreibungs-Ereigniskategorie | zurueckgestellt; Beobachtbarkeitszusatz |
| Explizite Pruefung der Unerreichbarkeit der Guard-Zweige | zurueckgestellt; Beobachtbarkeitszusatz |
| Audit-Klassifikation fuer nicht-binaere Gate-Werte | zurueckgestellt; Abschnitt 3.7 setzt ausdruecklich keinen Audit-Zaehler voraus |
| Zusaetzlicher Auditzaehler fuer Loss-Cluster-Blockaden | zurueckgestellt; Beobachtbarkeitszusatz |
| Uebergabe ausschliesslich von Dezimalinstanzen an die Economics-Hilfsfunktionen | zurueckgestellt; eine moegliche Integrationsvariante, nicht die einzige |
| Vorberechnung des modellierten Stop-Verlusts je Einheit zur Ursachenunterscheidung (V-19) | **zurueckgestellt**; die Reaktion ist in beiden Auslegungen der technische Abbruch. Es wird keine zweite Berechnungskette als Vertragsvoraussetzung eingefuehrt. Die angenommene Stop-Abbildung in ihrer festgelegten Reihenfolge bleibt unveraendert |

---

## 10. JSON-/Markdown-Bindung

Die maschinenlesbare Begleitdatei `docs/review/evidence/BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10.json` enthaelt im Feld `contract_text` den **vollstaendigen** Text dieser Markdown-Datei einschliesslich Titel, Quellenabschnitten und abschliessendem Zeilenumbruch.

Geltungsbereich der Hashfelder:

- `markdown_sha256` ist der SHA256 der **vollstaendigen Bytes dieser Markdown-Datei**.
- `contract_text_sha256` ist der SHA256 der **UTF-8-Kodierung von `contract_text`** und bezieht sich damit auf **dieselben** vollstaendigen Markdown-Bytes.
- Beide Werte sind daher identisch. Ihre Gleichheit ist der Nachweis der vollstaendigen und unveraenderten Einbettung.
- Die JSON-Datei enthaelt **keinen Hash ihrer selbst** und keinen zyklischen Hash.

Diese Markdown-Datei wird als UTF-8 mit LF-Zeilenenden und abschliessendem LF gefuehrt.

---

## 11. Schlussvermerk

Dieser Entwurf ist **DRAFT_NOT_BINDING**. Er behauptet **keine vollstaendige Implementierungsbereitschaft**. Saemtliche `V-`Festlegungen sind unverbindliche Vorschlaege. Bereits angenommene Pfadstruktur, P01 bis P07, K01 bis K08, Output- und Runtime-Festlegungen sowie saemtliche Berechnungsregeln bleiben unveraendert und stehen nicht erneut zur Genehmigung. Keine formale Annahme, keine Implementierungs-, Test-, Manifest-, Selektions-, Commit-, Push- oder Ausfuehrungsfreigabe folgt aus diesem Entwurf.

Die Erstellungsberechtigung dieser beiden Dateien beschraenkt sich auf die Ablage dieses unverbindlichen Entwurfs. Aus ihr folgt keine Annahme-, Implementierungs-, Test-, Manifest-, Commit-, Push- oder Market-Run-Freigabe.

---

## 12. Formale Annahmeaufzeichnung

Datum der Annahme (UTC): **2026-09-11**, aufgezeichnet um `2026-09-11T05:08:07Z`.

### 12.1 Annahmeautoritaet und Gegenstand

Die Annahme beruht auf einer **ausdruecklichen Nutzerfreigabe in der laufenden Konversation**. Angenommen werden die in den Abschnitten 2 bis 8 konkret ausgearbeiteten Vertragsfestlegungen: Grammatikblock und Feldzuordnung, Pruef- und Diagnosereihenfolge, `reason`-Kreuztabelle mit Nebenbedingungen, die vorgeschlagene Reihenfolge von Integritaetspruefung, wirtschaftlichen Kontrollen und Helper-Aufruf, die `EntryAuthorization`-Zuordnung mit Typ-, Mengen- und Reihenfolgeinvarianten sowie Auffangregel, die getrennte Behandlung ausserhalb der `EntryAuthorization`-Rueckgabe und die Quellenbindungen.

Technische Regeltexte, Grammatiken, Tabellen, Berechnungsregeln und Quellenbindungen sind **unveraendert**. Diese Aufzeichnung ergaenzt ausschliesslich den Annahmevermerk.

### 12.2 Geprueft angenommene Ausgangsidentitaeten

Angenommen wurden genau die geprueften Bytes des Entwurfsstands:

| Datei | Bytes | SHA256 |
| --- | --- | --- |
| `docs/review/BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10.md` | 52590 | `da3de2967a2aa0810d45ea2d65c2341069cdf4d68e541dcdcbfb93325c8cfccc` |
| `docs/review/evidence/BTC_L1_G10B_FIELD_HELPER_CONTRACT_V1_2026-09-10.json` | 60383 | `9590c9e7424a34c6fa6e25fde9658e772dec085b4d914bca50640aaa3f27a519` |

Beide Werte wurden unmittelbar vor dieser Aufzeichnung erneut nachgerechnet und stimmten ueberein. Durch die Aufnahme dieses Abschnitts aendern sich die Bytes und Hashes beider Dateien; die in der JSON-Begleitdatei gefuehrten Felder `markdown_sha256`, `contract_text_sha256` und `markdown_bytes` beziehen sich stets auf den **aktuellen** Markdown-Stand, waehrend die hier und im JSON gefuehrten Felder mit dem Praefix `reviewed_` die oben genannten **geprueften Ausgangsidentitaeten** festhalten.

### 12.3 Review-Empfehlung

Die vom Nutzer berichtete Antigravity-Workstation-Pruefung lautete **APPROVE_FOR_FORMAL_ADOPTION**.

### 12.4 Begrenzter fachlicher Geltungsbereich

Ausdruecklich **nicht** geschlossen und **nicht** angenommen werden:

- die weiterhin offene Grammatik fuer `symbol` nach Abschnitt 9.1;
- die offenen konkreten Runtime-, Dependency-, Eingabe- und Evidenzbindungen nach Abschnitt 9.2;
- die offene Ablagezuordnung protokollierter `findings`-Inhalte nach den Abschnitten 6.1 und 9.2;
- die tatsaechliche Verwendung der Economics-Hilfsfunktionen und deren Qualifikation;
- saemtliche zurueckgestellten Erweiterungen nach Abschnitt 9.3 einschliesslich V-19;
- Implementierungs-, Qualifikations-, Manifest- und Ausfuehrungsschritte jeder Art.

Die acht bestehenden angenommenen Vertragsdateien nach Abschnitt 8.3 bleiben unveraendert; sie wurden vor und nach dieser Aufzeichnung geprueft.

### 12.5 Praezisierung einer frueheren Aussage zur Grammatikabdeckung

Eine fruehere Formulierung von einer "lueckenlosen" Grammatikabdeckung wird hiermit praezisiert: Bestaetigt und angenommen sind die **konkret definierten Teilvertragsregeln** dieses Dokuments. `symbol` sowie die weiteren in Abschnitt 9 ausdruecklich offen gefuehrten Bindungen bleiben **offen**. Eine vollstaendige Abdeckung aller Felder und Bindungen wird nicht behauptet.

Die in Abschnitt 1.1 und Abschnitt 11 enthaltenen Entwurfsformulierungen sowie saemtliche Kennzeichnungen mit dem Praefix `V-` beschreiben den **geprueften Entwurfsstand**. Sie werden durch diese Aufzeichnung zeitlich eingeordnet und nicht umgeschrieben; die formale Annahme ergibt sich allein aus diesem Abschnitt 12 und dem Statusvermerk im Dokumentkopf.

### 12.6 Abweichung im unabhaengigen Review, ehrlich festgehalten

Die Antigravity-Pruefung war **entgegen ihrem urspruenglichen Bericht nicht vollstaendig lesend**. Ausgefuehrt wurden:

```
git checkout 3c5927127a03de13d8c80a720f5c8b97a2a36789
git checkout main
```

Beide Wechsel sind im HEAD-Reflog belegt:

| Zeitpunkt | Reflog-Eintrag |
| --- | --- |
| `2026-09-10 21:47:12 +0200` (= `2026-09-10T19:47:12Z`) | `checkout: moving from main to 3c5927127a03de13d8c80a720f5c8b97a2a36789` |
| `2026-09-10 21:54:35 +0200` (= `2026-09-10T19:54:35Z`) | `checkout: moving from 3c5927127a03de13d8c80a720f5c8b97a2a36789 to main` |

Die nachfolgende unabhaengige Lesepruefung durch Claude bestaetigte:

- den erwarteten HEAD `ea7f5b32d6b481147bb780f6c9319f7ea37faf87` und den Branch `main`;
- unveraenderte Inhalte aller acht angenommenen Vertragsdateien;
- unveraenderte Entwurfshashes und konsistente JSON-/Markdown-Bindungen;
- aktuell **keinen** post-checkout-Hook, kein gesetztes `core.hooksPath`, keine ausfuehrbaren Nicht-Sample-Hooks und keine Filter-, fsmonitor- oder Alias-Konfiguration, die beim Checkout ein externes Programm starten wuerde.

**Grenzen dieses Befundes, ausdruecklich:**

- Der heutige Hook- und Dateizustand **beweist nicht** den vollstaendigen frueheren Ablauf.
- Fuer den frueheren Antigravity-Vorgang sind die pauschalen Aussagen `NO_REPOSITORY_CODE_EXECUTION` und `NO_MARKET_RUN` **nicht belegt** und werden hier **nicht** ausgegeben.
- Es liegt zugleich **kein Nachweis eines Market Runs** vor. Fehlende Nachweise duerfen ebenso wenig als **bewiesene Datenexposition** ausgegeben werden.
- Waehrend des Fensters vom `2026-09-10T19:47:12Z` bis `2026-09-10T19:54:35Z` waren die acht angenommenen Vertragsdateien nicht im Arbeitsbaum vorhanden. Ihre Inhalte sind nach der Rueckkehr auf `main` nachweislich unveraendert.
- Diese formale Dokumentannahme **beseitigt oder genehmigt den damaligen Verstoss nicht rueckwirkend**.
- Es wird **keine** nachtraegliche Bescheinigung einer vollstaendig lesenden Review-Durchfuehrung erteilt.

### 12.7 Reichweite der Annahme

Diese Annahme betrifft ausschliesslich die fachlichen Vertragsfestlegungen dieses Dokuments und deren Aufzeichnung in genau diesen beiden Dateien. Aus ihr folgt **keine** Implementierungs-, Qualifikations-, Test-, Kandidatenmanifest-, Selektions-, Staging-, Commit-, Push-, Synchronisierungs- oder Market-Run-Freigabe. Die bereits angenommenen Vertraege P01 bis P07, K01 bis K08, die Output- und Runtime-Festlegungen einschliesslich Pfadstruktur, Fresh-State- und Abschlussregeln sowie saemtliche Berechnungsregeln bleiben unveraendert und stehen nicht erneut zur Genehmigung.

```json
{
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "date_utc": "2026-09-11",
  "decision": "FORMALLY_ACCEPT_REVIEWED_FIELD_AND_HELPER_CONTRACT",
  "document_status": "APPROVED_FOR_ADOPTION",
  "review_recommendation": "APPROVE_FOR_FORMAL_ADOPTION",
  "review_source": "ANTIGRAVITY_WORKSTATION_REVIEW_REPORTED_BY_USER",
  "reviewed_markdown_sha256": "da3de2967a2aa0810d45ea2d65c2341069cdf4d68e541dcdcbfb93325c8cfccc",
  "reviewed_markdown_bytes": 52590,
  "reviewed_json_sha256": "9590c9e7424a34c6fa6e25fde9658e772dec085b4d914bca50640aaa3f27a519",
  "reviewed_json_bytes": 60383,
  "technical_contract_and_calculation_rules_changed": false,
  "scope": "Annahme der konkret ausgearbeiteten Feld- und Helper-Vertragsfestlegungen und Aufzeichnung dieser Annahme in genau diesen zwei Dateien",
  "not_closed": [
    "symbol-Grammatik",
    "konkrete Runtime-, Dependency-, Eingabe- und Evidenzbindungen",
    "Ablagezuordnung protokollierter findings-Inhalte",
    "tatsaechliche Helper-Verwendung und deren Qualifikation",
    "zurueckgestellte Erweiterungen einschliesslich V-19",
    "Implementierungs-, Qualifikations-, Manifest- und Ausfuehrungsschritte"
  ],
  "review_conduct_deviation": "Der Antigravity-Review war entgegen seinem Bericht nicht vollstaendig lesend; zwei Checkouts sind im HEAD-Reflog belegt. Die Annahme heilt diesen Verstoss nicht rueckwirkend.",
  "no_retroactive_read_only_certification": true,
  "no_repository_code_execution_claim_supported": false,
  "no_market_run_claim_supported": false,
  "market_run_evidence_found": false,
  "data_exposure_proven": false,
  "implementation_authorized": false,
  "qualification_authorized": false,
  "test_execution_authorized": false,
  "candidate_manifest_authorized": false,
  "selection_authorized": false,
  "staging_authorized": false,
  "commit_authorized": false,
  "push_authorized": false,
  "market_run_authorized": false
}
```
