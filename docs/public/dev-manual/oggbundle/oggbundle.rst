.. _kapitel-oggbundle-main:

===============================
OneGov GEVER Bundle (OGGBundle)
===============================

Das Zwischenformat für den Export von Daten aus OS-Laufwerk und dem
Import in OneGov GEVER wird als OneGov GEVER Bundle (**OGGBundle**)
bezeichnet.

Das Bundle kann als "virtuelles Verzeichnis" verstanden werden: Es folgt
einer Verzeichnisstruktur, welche nach einem bestimmten Muster aufgebaut
ist, und alle nötigen Informationen des Exports enthält. Das Bundle kann
somit für sehr kleine Datenmengen als ZIP-Datei mit der Endung
**.oggbundle** (z.B. **testinhalte.oggbundle**) abgeliefert werden, oder
auch als Verzeichnis mit der Endung **.oggbundle** auf einem Server
hinterlegt oder gemountet werden. Der konkrete Transportmechanismus ist
nicht Teil dieser Spezifikation, und kann dem Anwendungszweck gemäss
gewählt werden.

Alle Pfad-Angaben in einem Bundle sind relativ zum root des Bundles.

Das Bundle besteht aus einer Sammlung von JSON-Dateien, deren Inhalt
einem bestimmten Schema folgen muss, und einem Unterverzeichnis
**files/** welches die Dateien für Dokumente (Primärdaten) enthält.

Ein Bundle beinhaltet eine Datei pro zu importierendem Inhaltstyp. Darin
müssen die jeweiligen Inhalte flach (ohne Verschachtelung) im
JSON-Format gespeichert werden. Für jede solche Datei wird ein
`*JSON-Schema* <http://json-schema.org/>`__ zur Verfügung gestellt,
welches den Aufbau der JSON-Datei genau beschreibt und mit dem die
Inhalte vor einem Import validiert werden müssen. Die folgenden
Abschnitte beschreiben die im Moment unterstützten Inhaltstypen und die
damit assoziierten Dateien im Bundle.

|img-image-1|

Inhalt:
-------
.. contents::

Konfiguration und Bundle-Metadaten
----------------------------------

metadata.json
~~~~~~~~~~~~~

Diese Datei beinhaltet Metadaten über das Bundle, z.B. den
Erstellungszeitpunkt und Ersteller des Bundles oder den Verwendungszweck
(optional).

configuration.json
~~~~~~~~~~~~~~~~~~

Diese Datei beinhaltet die Konfiguration des Mandanten, insbesondere
auch die zur Validierung der Inhalte benötigten Wertebereiche, welche
für gewisse Felder pro Mandant konfigurierbar sind.

Daten für Inhaltstypen
----------------------

reporoots.json
~~~~~~~~~~~~~~

Diese Datei beinhaltet ein oder mehrere Ordnungssystem-Wurzeln.

repofolders.json
~~~~~~~~~~~~~~~~

Diese Datei beinhaltet die einzelnen Ordnungspositionen, die in den
Ordnungssystem-Wurzeln abgelegt werden.

dossiers.json
~~~~~~~~~~~~~

Diese Datei beinhaltet Dossiers und Subdossiers, diese können in den
Ordnungspositionen abgelegt werden.

documents.json
~~~~~~~~~~~~~~

Diese Datei beinhaltet die Metadaten der Dokumente. Die Binärdateien
werden im Ordner **files/** zur Verfügung gestellt und müssen mit einem
zum Bundle relativen Pfad referenziert werden. Die Metadaten beinhalten
unter anderem auch den Dateinamen, der Dateiname der Datei auf dem
Filesystem wird nicht verwendet, sondern von den Metadaten
überschrieben.

Siehe untenstehende Erläuterungen im Abschnitt **files/** zu Details
bezüglich den Dateipfaden.

files/
~~~~~~

Dieser Ordner beinhaltet die Primärdateien der Dokumente. Ob die Dateien
flach abgelegt werden, oder in weitere Unterordner verschachtelt werden
ist nicht vorgegeben - die Strukturierung dieses Verzeichnisses ist dem
Lieferanten des Bundle überlassen. Die Dateinamen müssen jedoch
normalisiert werden um Inkompatibilitäten zu vermeiden, die Aufgrund
unterschiedlicher Zeichensätzen in unterschiedlichen Umgebungen
entstehen können. Wir empfehlen ein einfaches Schema mit aufsteigender
Nummerierung wie z.B. **file\_00123.pdf**.

Der tatsächlich in OneGov GEVER verwendete Titel / Dateiname wird
gesteuert über das Attribut **title** in den im **documents.json**
gelieferten Metadaten: Im Attribut **title** soll der ursprüngliche
Dateiname, inklusive Dateiendung geliefert werden. In OneGov GEVER wird
der Titel des Dokuments dann von diesem Attribut abgeleitet, indem die
Dateiendung entfernt wird. Die Dateiendung selbst hingegen wird zur
Bestimmung des Inhaltstyps (MIME-Type) verwendet.

Folgende Dateitypen sind in OGGBundles nicht erlaubt:

-  **.msg**

-  **.exe**

-  **.dll**

Pfade / Dateinamen dürfen nur alphanumerische Zeichen, Unterstrich und
Bindestrich enthalten (**[0-9][a-zA-Z][-\_]**). Alle Pfade sind
case-sensitive, und dürfen eine maximale Länge von 255 Zeichen nicht
überschreiten. Die Pfade sind als UNIX-Pfade relativ zum root des
Bundles anzugeben (getrennt mit Forward-Slash).

Abbildung von Verschachtelung (containment)
-------------------------------------------

Da die Daten in den JSON-Dateien nicht verschachtelt abgelegt werden,
ist es nötig diese Verschachtelung während dem Import aufzulösen. Diese
Verschachtelung wird mittels global eindeutiger ID (GUID) und einem
Pointer von Children auf das enthaltende Parent abgebildet. Dazu hat
muss jedes Objekt über eine GUID verfügen. Diese muss im Attribut
**guid** gespeichert werden. Die Verschachtelung wird mittels einer
Referenz auf das Parent hergestellt, dazu muss jedes Objekt, das ein
Parent besitzt, das Attribut **parent\_guid** definieren, und damit auf
das Parent referenzieren.

Siehe auch Abschnitt “\ **Geschäftsregeln**\ ” für Angaben, welche
Inhaltstypen wie verschachtelt werden dürfen.

Berechtigungen
--------------

Berechtigungen werden in OneGov GEVER standardmässig auf die Children
vererbt. Es ist auf den Stufen Ordnungssystem, Ordnungsposition und
Dossier erlaubt die Berechtigungen zu setzen, wobei Berechtigungen auf
Stufe Dossier die Ausnahme sein sollten.

Die Berechtigungen können granular für die folgenden Rollen vergeben
werden:

-  read Lesen

-  add Dossiers hinzufügen

-  edit Dossiers bearbeiten

-  close Dossiers abschliessen

-  reactivate Dossiers reaktivieren

Zusätzlich kann mit einem **block\_inheritance** Flag spezifiziert
werden, ob die Vererbung der Berechtigungen auf dieser Stufe
unterbrochen werden soll. Dies führt dazu, dass ab dieser Stufe nur die
explizit definierten Zugriffsberechtigungen gültig sind, und keine
Berechtigungen mehr via Vererbung vom Parent übernommen werden.

Berechtigungen werden an einen oder mehrere “Principals” vergeben, dies
entspricht einem Benutzer oder einer Gruppe.

Setzen von Werten
-----------------

Defaultwerte werden nur nur gesetzt, falls die entsprechenden Attribute
im gelieferten JSON nicht vorhanden sind.

Setzen des Workflow-Status
--------------------------

Für Objekte mit einem Workflow kann über das Property review\_state
angegeben werden, in welchem Status das Objekt erstellt werden kann.

Die vollständige Liste der gültigen Workflow-States ist im Schema der
entsprechenden Objekte definiert.

Ordnungssysteme
~~~~~~~~~~~~~~~
+-------------------------------+---------+
| repositoryroot-state-active   | Aktiv   |
+-------------------------------+---------+

Initial-Zustand: repositoryroot-state-active

Ordnungspositionen
~~~~~~~~~~~~~~~~~~
+---------------------------------+---------+
| repositoryfolder-state-active   | Aktiv   |
+---------------------------------+---------+

Initial-Zustand: repositoryfolder-state-active

Dossiers
~~~~~~~~
+--------------------------+------------------+
| dossier-state-active     | In Bearbeitung   |
+==========================+==================+
| dossier-state-resolved   | Abgeschlossen    |
+--------------------------+------------------+

Initial-Zustand: dossier-state-active

Um ein Dossier im abgeschlossenen Zustand abzuliefern, wird daher der
review\_state auf den entsprechenden Wert gesetzt:

...

"review\_state": "dossier-state-resolved",

...

Wenn ein Dossier im abgeschlossenen Zustand abgeliefert wird, MUSS jedes
darin enthaltene Subdossier ebenfalls den Status dossier-state-resolved
haben. Das Erfüllen der Regeln zu “losen Blättern” und Datumsbereichen
hingegen ist empfohlen, wird aber für den Import nicht strikt verlangt
(wird protokolliert, aber “as-is” importiert).

Dokumente
~~~~~~~~~
+------------------------+----------------------+
| document-state-draft   | (Standard-Zustand)   |
+------------------------+----------------------+

Initial-Zustand: document-state-draft

Zusätzliche Validierung
-----------------------

Schema
~~~~~~

-  Die GUID eines jeden eingelesenen Objektes muss zwingend eindeutig
       sein.

-  Das Aktenzeichen eines Dossiers/Dokumentes muss zwingend eindeutig
       sein, ebenso die Positionsnummer einer Ordnungsposition.

-  Date und DateTime Felder müssen gemäss `*RFC 3339* <http://www.ietf.org/rfc/rfc3339.txt>`__ formatiert werden.

Geschäftsregeln
~~~~~~~~~~~~~~~

Die folgenden Geschäftsregeln gelten in OneGov GEVER:

-  Die Konfigurationsvariable **maximum\_repository\_depth** und
       **maximum\_dossier\_depth** definieren wie tief
       Ordnungspositionen und Dossiers ineinander verschachtelt werden
       dürfen.

-  Abgeschlossene Dossiers:

   -  Abgeschlossene Dossiers dürfen keine offenen Subdossiers
          enthalten.

   -  Ist ein Dossier abgeschlossen und hat Subdossiers, so müssen alle
          Dokumente einem Subdossier zugeordnet werden, das Hauptdossier
          darf keine ihm direkt zugeordneten Dokumente enthalten (“keine
          losen Blätter”).

   -  Das Enddatum eines abgeschlossenen Dossiers muss immer grösser
          oder gleich dem Enddatum aller seiner Subdossiers, und grösser
          oder gleich dem Dokumentdatum eines enthaltenen Dokumentes
          sein.

-  Eine Ordnungsposition kann nur entweder Dossiers oder weitere
       Ordnungspositionen enthalten, nie Objekte beider Inhaltstypen
       gleichzeitig. Dossiers dürfen dementsprechend nur in Leaf-Nodes
       (Rubriken) des Ordnungssystems enthalten sein.

-  Bei den folgenden Feldern ist die Auswahlmöglichkeit durch den Parent
       eingeschränkt:

   -  custody\_period (Archivische Schutzfrist)

   -  archival\_value (Archivwürdigkeit)

   -  classification (Klassifikation)

   -  privacy\_layer (Datenschutzstufe)

   -  retention\_period (Aufbewahrungsdauer) - *Je nach Konfiguration ist diese Regel auch nicht aktiv*

    Einschränken bedeutet in diesem Zusammenhang, dass die Liste der zur
    Verfügung stehenden Elemente gemäss JSON-Schema Definition auf das
    vom Parent ausgewählte Element und alle Folge-Elemente reduziert
    wird.

Aktenzeichen und Laufnummern
----------------------------

In OneGov GEVER werden Aktenzeichen geführt, und auf den Ebenen Dossier
und Dokument dargestellt. Das Darstellungsformat des Aktenzeichens
(Gruppierung, Trennzeichen) ist pro Mandant konfigurierbar, und die
einzelnen Bestandteile werden unabhängig vom formatierten String separat
gespeichert.

| Ein Beispiel für das Aktenzeichen eines Dokumentes in GEVER sieht wie
  folgt aus:
| **FD 0.7.1.1 / 5.3 / 54**

Die einzelnen Komponenten stehen hier für folgendes:

-  **FD** - ein pro Mandant konfigurierbares Kürzel das im Aktenzeichen
       verwendet wird

-  **0.7.1.1** - die Nummer der Ordnungsposition. Zusammengesetzt aus
       den Einzelkomponenten (**0**, **7**, **1**, und **1**) welche
       lokal auf den entsprechenden Ordnungspositionen geführt werden /
       gespeichert sind. Separiert durch ein konfigurierbares
       Trennzeichen (Standardmässig Punkt).

-  **5** - die Nummer des Dossiers innerhalb der Rubrik (aufsteigender
       Zähler pro Rubrik)

-  **3** - die Nummer eines Subdossiers innerhalb des Dossiers, falls
       Subdossiers existieren

-  **54** - die global eindeutige Laufnummer des Dokuments (auch ohne
       den Rest des Aktenzeichens eindeutig)

Die Aktenzeichen für Dossiers/Subdossiers lassen den letzten Teil
(Laufnummer des Dokuments) weg.

Abgrenzungen
------------

-  Es können vorerst nur die erwähnten Inhaltstypen importiert werden,
       nicht alle in OneGov GEVER verfügbaren Typen.

-  Dokument-Versionen können nicht importiert werden.

-  Mails können beim automatischen import nicht verlustlos von *\*.msg*
       nach *\*.eml* konvertiert werden, daher müssen diese Vorgängig
       nach \*.eml konvertiert werden.

-  Es kann nicht überprüft werden, ob die Rechte “sinnvoll” gesetzt sind
       (optimale Nutzung des Vererbungsmechanismus, keine Redundanzen).
       Eine allfällige Vereinfachung der Berechtigungen muss vor einem
       Import der Daten nach OneGov GEVER durchgeführt werden.

.. |img-image-1| image:: img/image1.png
