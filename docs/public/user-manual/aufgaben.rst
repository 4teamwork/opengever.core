.. _kapitel-aufgaben:

Mit Aufgaben arbeiten
=====================

Eine Aufgabe erstellen
----------------------

Es gibt im Wesentlichen zwei Möglichkeiten, um eine Aufgabe zu erstellen:

-  Auf Stufe Dossier oder Subdossier rufen Sie mit *Hinzufügen →
   Aufgabe* die Erfassungsmaske auf.

   |img-aufgaben-1|

-  Wählen Sie in der Dokumentenliste eines oder mehrere Dokumente (mit
   der Taste :kbd:`Ctrl-Taste`) aus und klicken Sie auf *Aufgabe erstellen*.

   |img-aufgaben-2|

Die Aufgabenmaske ist in die beiden Reiter *Allgemein* und *Erweitert*
gegliedert. Der jeweils aktive Reiter ist grau hinterlegt.
Obligatorische Felder sind jeweils mit einem roten Quadrat markiert.

Reiter Allgemein
~~~~~~~~~~~~~~~~

|img-aufgaben-3|

1. **Titel:** Inhaltliche Beschreibung der Aufgabe

2. **Auftragsgeber:** Diejenige Person, die den Auftrag erteilt.
   Standardmässig wird die an OneGov GEVER angemeldete Person
   vorgeschlagen.

3. **Auftragstyp:** Mit dem Auftragstyp wird angegeben, was vom
   Auftragnehmer erwartet wird. In OneGov GEVER werden standardmässig
   sechs Auftragstypen unterschieden:

    - Zur Kenntnisnahme [#FN1]_

    - Zur direkten Erledigung [#FN1]_

    - Zum Bericht / Antrag

    - Zur Genehmigung

    - Zur Prüfung / Korrektur

    - Zur Stellungnahme

    .. [#FN1] Vom Auftraggeber wird keine Antwort erwartet, die überprüft
      werden muss; daher kann bei diesen beiden Auftragstypen die Aufgabe
      durch den Auftragnehmer abgeschlossen werden.

4. **Auftragnehmer:** Diejenige Person, die den Auftrag erledigen soll.

   Bei Mehrmandanteninstallationen von OneGov GEVER
   kann hier zusätzlich der entsprechende Zielmandant ausgewählt werden
   (sog. mandantenübergreifende Zusammenarbeit).

5. **Zu erledigen bis:** Frist, bis wann der Auftrag erfüllt sein soll.
   Als Vorschlag wird das aktuelle Datum +5 Tage gesetzt.

6. **Beschreibung:** Bei Bedarf kann im Beschreibungsfeld der Auftrag
   detailliert beschrieben werden.

7. **Verweise:** Dokumente, die in Zusammenhang mit der Aufgabe stehen,
   können durch Hinzufügen oder durch direkte Texteingabe verknüpft
   werden.

   Wurde die Aufgabe über eine Vorauswahl von Dokumenten über den Reiter
   *Dokumente* erzeugt, sind die ausgewählten Dokumente bereits als
   Verweise aufgeführt.

Reiter Erweitert
~~~~~~~~~~~~~~~~

|img-aufgaben-4|

Mit Ausnahme des Erledigungsdatums sind die Felder auf die
Leistungserfassung ausgerichtet.

Das Erledigungsdatum wird mit der Aktion *Erledigen* automatisch
gesetzt.

.. note::
   Nach dem Speichern erhält die Aufgabe den Status *offen*.
   Im Status *offen* kann der Auftraggeber die Felder der Aufgabe noch bearbeiten
   (z.B. die Frist), später nicht mehr. Ausserdem können Aufgaben im Status
   *offen* vom Auftraggeber noch storniert werden, danach ist dies nicht mehr
   möglich.

.. _aufgabe-detailansicht:

Detailansicht einer Aufgabe
---------------------------

Die Detailansicht zu einer Aufgabe ist so aufgebaut, dass der Benutzer auf
einen Blick eine Übersicht über alle wesentlichen Informationen erhalten kann.

|img-aufgaben-5|

Konkret sind die folgenden Informationsblöcke enthalten:

1. **Aufgabentitel**: Inhaltliche Beschreibung der Aufgabe

2. **Reiter Übersicht und Dokumente**: Über die beiden Reiter *Übersicht* und
   *Dokumente* kann zwischen unterschiedlichen Ansichten zur Aufgabe hin-
   und hergewechselt werden. Der Reiter *Dokumente* listet alle Dokumente auf,
   die mit der Aufgabe verknüpft worden sind.

3. **Eigenschaften**: Hier werden alle relevanten Informationen zur Aufgabe
   angezeigt, u.a. auch deren aktueller Status ("offen", "in Arbeit",
   "erledigt", "abgeschlossen").

4. **Antwortmöglichkeiten**: Über mehrere Buttons können zwischen verschiedenen
   Antworten zur Aufgabe gewählt werden.

5. **Verlauf**: Der Aufgabenverlauf listet alle Aktivitäten auf, die in
   Verbindung mit dieser Aufgabe bisher statt gefunden haben. Dabei wird die
   letzte (jüngste) Aktivität zu oberst dargestellt.

6. **Haupt- und Unteraufgaben**: Falls die Aufgabe weitere Unteraufgaben
   enthält, werden diese in diesem Bereich dargestellt. Umgekehrt wird hier
   auch die zugehörige Hauptaufgabe angezeigt, falls es sich bei der Aufgabe
   um eine Unteraufgabe handelt.

Eine Unteraufgabe erstellen
---------------------------

Zu einer Aufgabe können beliebig viele Unteraufgaben eröffnet werden.
Zuvor muss jedoch die Hauptaufgabe akzeptiert werden. Klicken Sie auf
Stufe Aufgabe *Hinzufügen → Unteraufgabe*.

|img-aufgaben-6|

Hierauf öffnet sich ein Formular, analog zu demjenigen der Aufgabe. Die
Unteraufgabe wird in der Hauptaufgabe dargestellt (siehe
:ref:`aufgabe-detailansicht`).

Mit Klick gelangt man direkt auf die Unteraufgabe. Die Hauptaufgabe wird
in der Unteraufgabe ebenfalls dargestellt:

|img-aufgaben-7|

Übersicht über den typischen Aufgabenworkflow
---------------------------------------------

Nach dem Speichern ist eine Aufgabe im Status *Offen*.

**Typische Reihenfolge der Aufgabenerledigung:**

-   Auftragsgeber erstellt eine Aufgabe: Status Offen

-   Auftragnehmer akzeptiert die Aufgabe: Status In Arbeit

-   Auftragnehmer erledigt die Aufgabe: Status Erledigt

-   Auftraggeber schliesst die Aufgabe ab: Status Abgeschlossen

.. note::
   Bei den Auftragstypen "Zur Kenntnisnahme" sowie "Zur direkten Erledigung"
   ist der Workflow abgekürzt, da der Auftraggeber in diesen Fällen keine
   Antwort erwartet, die überprüft werden muss.

   - "Zur Kenntnisnahme": Diese Aufgabe kann ohne Akzeptieren direkt
     abgeschlossen werden.

   - "Zur direkten Erledigung": Diese Aufgabe kann nach dem Akzeptieren direkt
     abgeschlossen werden.

   Mitarbeitende, die Zugriff auf den Eingangskorb haben, können zusätzliche
   Aufgabenaktionen auslösen, auch wenn sie nicht Auftragnehmer sind.

**Spezialfälle:**

-   Auftragnehmer lehnt eine Aufgabe ab: Status Zurückgewiesen

-   Auftraggeber storniert eine Aufgabe: Status Storniert

-   Auftragsgeber öffnet eine Aufgabe nochmals, nachdem sie bereits
    erledigt war oder zurückgewiesen worden ist: Status Offen

-   Auftraggeber weist Aufgabe neuer Person zu: Status Offen

Eine empfangene Aufgabe als Verantwortlicher bearbeiten
-------------------------------------------------------

Nach der Erstellung befindet sich eine Aufgabe im Status *Offen*. Der
Aufgabe beigefügte Dokumente befinden sich unter dem Reiter *Dokumente*;
gleichzeitig werden sie unter dem Titel "Dokumente" aufgelistet:

|img-aufgaben-8|

Aufgabe akzeptieren
~~~~~~~~~~~~~~~~~~~

Mit *Aktionen → Aufgabe akzeptieren* übernimmt der Auftragnehmer die
Aufgabe. Bei Bedarf kann ein Kommentar hinzugefügt werden. Der Status wechselt
nun von *Offen* auf *In Arbeit*.

|img-aufgaben-8b|

Aufgabe ablehnen
~~~~~~~~~~~~~~~~

Wird die Aufgabe abgelehnt (z.B. wegen Ferien) wechselt der Status auf
"Abgelehnt".

|img-aufgaben-22|
|img-aufgaben-23|

Der Auftraggeber hat die Möglichkeit, die Aufgabe wieder zu öffnen und
einem neuen Sachbearbeiter zuzuweisen.

Aufgabe neu zuweisen
~~~~~~~~~~~~~~~~~~~~

Eine Aufgabe kann auch einem anderen Sachbearbeiter bzw. einer anderen
Sachbearbeiterin zugewiesen werden. Wählen Sie dazu *Aktionen → Neu
zuweisen*. Diese Möglichkeit besteht auch im späteren
Arbeitsverlauf.

|img-aufgaben-24|

In der neuen Maske kann die Person ausgewählt werden, welcher die Aufgabe
zugewiesen werden soll. Im Kommentar-Feld können bei Bedarf noch weitere Inputs
gegeben werden. Die Aktion mit "Zuweisen" abschliessen.

|img-aufgaben-25|

In der Detailansicht der Aufgabe kann die Neuzuweisung des Auftragnehmers
nachträglich unten im Verlauf nachvollzogen werden.

|img-aufgaben-26|


Mit den Aufgaben verknüpfte Dokumente (Verweise) bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mit den Aufgaben verknüpfte Dokumente können direkt aus der Aufgabe
heraus bearbeitet werden. Fahren Sie unter dem Reiter *Dokumente* über den
Titel, um das referenzierte Dokument auszuchecken und zu bearbeiten. Die
Änderungen werden nach dem Einchecken als neue Version gespeichert.

|img-aufgaben-12|

Dokumente in einer Aufgabe
~~~~~~~~~~~~~~~~~~~~~~~~~~

Dokument hinzufügen
^^^^^^^^^^^^^^^^^^^

Mit *Hinzufügen → Dokument* kann eine Datei aus dem Filesystem
importiert werden.

|img-aufgaben-13|

Neu hinzugefügte Dokumente werden sowohl unter dem Reiter *Dokumente*
der Aufgabe angezeigt als auch unter der Rubrik "Dokumente" und in der
Auflistung der Antworten. Gleichzeitig werden sie automatisch in die
Dokumentenliste des betreffenden Dossiers gelegt.

Auf bestehendes Dokument verweisen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Eine bereits in OneGov GEVER vorhandene Datei kann beim Erledigen im
Feld *Verweise* referenziert werden. (Siehe nächster Schritt)

Aufgabe erledigen
~~~~~~~~~~~~~~~~~

Wählen Sie *Erledigen*.

|img-aufgaben-16|

Falls Sie auf ein im Dossier befindliches Dokument verweisen möchten,
ist dies im Feld Verweis möglich. Ein Antworttext ist fakultativ. Je nach
Aufgabenstellung kann ein Auftrag auch nur durch eine Antwort erledigt werden.

|img-aufgaben-17|

Nach dem Speichern wechselt der Aufgabenstatus auf *Erledigt*. Soll der Antwort
nochmals etwas hinzugefügt werden, kann die Aufgabe mit
*Aktion → Überarbeiten* wieder in den Status *In Arbeit* gesetzt werden.

|img-aufgaben-18|

Erledigte Aufgabe abschliessen oder überarbeiten
------------------------------------------------

Ist der Auftraggeber mit der Aufgabenerledigung zufrieden, schliesst er
die Aufgabe mit *Aktionen → Abschliessen* ab (siehe Bild oben). Fakultativ kann
im Antwortfeld ein Text eingegeben werden.

|img-aufgaben-19|

Mit dem Speichern wird automatisch das Erledigungsdatum gesetzt, und der Status
der Aufgabe wechselt auf *Abgeschlossen*. Ist die Aufgabe einmal im Status
*Abgeschlossen* kann sie nicht mehr bearbeitet werden.

|img-aufgaben-20|

Soll die vom Auftragnehmer erledigte Aufgabe nochmals überarbeitet
werden, kann der Auftraggeber, statt die Aufgabe abzuschliessen, mit der
Aktion *Überarbeiten* wieder in den Status *In Bearbeitung setzen*.

Auflistung von Statusänderungen, Antworten und Dokumenten
---------------------------------------------------------

Statusänderungen, Antworttexte und hinzugefügte Dateien werden im
unteren Teil der Aufgabenmaske aufgelistet. Dadurch kann der ganze
Verlauf nachvollzogen werden. Die neueste Antwort befindet sich dabei
immer zuoberst.

|img-aufgaben-21|

Mandantenübergreifende Zusammenarbeit
-------------------------------------

Eine mandantenübergreifende Aufgabe erstellen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Das Erstellen einer mandantenübergreifenden Aufgabe unterscheidet sich
nur wenig von einer Aufgabe, die von jemandem innerhalb desselben
Mandanten erledigt werden soll. Zur Kennzeichnung einer
mandantenübergreifenden Aufgabe wird das Icon verwendet.

|image174|

Im folgenden Beispiel geht es um eine verwaltungsinterne Vernehmlassung
des Amts für Raumplanung.

-  Erstellen Sie eine Aufgabe und verknüpfen Sie sie mit denjenigen
   Dokumenten, die der Auftragnehmer zur Bearbeitung der Aufgabe
   benötigt. Alle anderen Dokumente im Dossier bleiben für den
   Auftragnehmer unsichtbar.

-  Wählen Sie im Feld *Mandant des Auftragnehmers* das entsprechende
   Kürzel (z.B. SKA-ARCH).

-  Als Auftragnehmer wird im Normalfall der Eingangskorb des zuständigen
   Mandanten eingetragen (z.B. *Eingangskorb SKA-ARCH*). Gegebenenfalls
   kann aber auch der zuständige Sachbearbeiter gewählt
   werden.

   |image175|

-  Wenn Sie den Eingangskorb als Auftragnehmer gewählt haben, gelangt
   die Aufgabe in den Eingangskorb des betreffenden Mandanten (Reiter
   *Erhaltene Aufgaben*). Personen mit Sekretariatsrechten
   können die Aufgabe vom Eingangskorb aus der zuständigen Person
   zuweisen.

-  Haben Sie einen Sachbearbeiter gewählt, wird der Auftrag unter dem
   Reiter *Übersicht/Meine Aufgaben* angezeigt.

Mandantenübergreifende Aufgaben bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In OneGov GEVER werden bei mandantenübergreifenden Aufgaben Dossiers
nicht automatisch kopiert, sondern andere Amtsstellen an Dossiers
beteiligt. Das heisst: Die beteiligten Amtsstellen erhalten Einsichts-
und Bearbeitungsrechte direkt im Dossier des Auftraggebers. Beim
Auftragnehmer entsteht nur eine Aufgabe, aber kein Dossier. Deshalb
erscheint eine Aufgabe aus einem anderen Mandanten nicht in der
Dossierliste, sondern unter *Übersicht / Meine Aufgaben* bzw. *Alle
Aufgaben* oder im Eingangskorb des Mandanten, wenn die Aufgabe noch
keinem konkreten Sachbearbeiter zugewiesen wurde. Für die Bearbeitung
bietet OneGov GEVER die Möglichkeit, Aufgaben aus anderen Mandanten
direkt im Dossier des Auftraggebers oder in einem Dossier auf dem
eigenen Mandanten zu bearbeiten.

Öffnen, Zuweisen und Akzeptieren einer mandantenübergreifenden Aufgabe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| Falls erforderlich, wird die Aufgabe aus dem Eingangskorb heraus dem
  verantwortlichen Sachbearbeiter durch die Aktion *Neu zuweisen*
  zugeteilt. Dies ist nur mit den entsprechenden Rechten (Sekretariat,
  Leitung, Sachbearbeiter mit zentraler Aufgabenliste) möglich.
| |image176|

Die nun personalisierte Aufgabe kann unter dem Reiter *Übersicht / Meine
Aufgaben* durch Anklicken des Titels geöffnet werden.

Nun wird man automatisch auf den Mandanten des Auftraggebers
weitergeleitet, indem im Browser ein neuer Tab geöffnet wird. Der
Auftragnehmer sieht nur diejenigen Dokumente des Dossiers, auf die in
der Aufgabe verwiesen wurde. Auch das Ordnungssystem ist nur reduziert
sichtbar. Damit die Übersicht gewahrt bleibt, wird der "Gastmandant"
verblasst dargestellt.

|image177|

|image178|

Klicken Sie auf *Aktionen → Akzeptieren*.

OneGov GEVER schlägt Ihnen nun drei Möglichkeiten vor, wie Sie die
Aufgabe bearbeiten können:\ |image179|

1. direkt im Dossier des Auftraggebers

2. in einem bereits bestehenden Dossier in Ihrem Mandanten ablegen

3. in einem neuen Dossier in Ihrem Mandanten ablegen

|image180|

Direkt im Dossier des Auftraggebers bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Klicken Sie beim Akzeptieren der Aufgabe auf die Option *direkt im
Dossier des Auftraggebers bearbeiten*.\ |image181|

Nun werden Sie automatisch auf den Mandanten des Auftraggebers
weitergeleitet, indem im Browser ein neuer Tab geöffnet wird. Sie sehen
nur diejenigen Dokumente, auf die in der Aufgabe verwiesen wurde. Das
Ordnungssystem wird reduziert und verblasst dargestellt (siehe
Abschnitt 7.7.2).

Die Aufgabe kann nun auf dieselbe Weise wie eine mandanteninterne
Aufgabe bearbeitet werden. Dokumente können durch Auschecken /
Einchecken direkt bearbeitet oder durch Heraufladen aus dem Filesystem
hinzugefügt werden.

Abgeschlossene Aufgaben und deren Inhalte bleiben für den Auftragnehmer
(und für alle, die im Eingangskorb des betreffenden Mandanten berechtigt
sind) sichtbar, bis das Dossier beim Auftraggeber archiviert (d.h. dem
Archiv abgeliefert) wird.

Aufgabe in einem bestehenden Dossier im eigenen Mandanten bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Klicken Sie beim Akzeptieren der Aufgabe auf die Option *in einem
bestehenden Dossier auf Mandant x bearbeiten.* und klicken Sie *Weiter*.

|image182|

Wählen Sie das Zieldossier durch direkte Texteingabe oder durch Anzeigen
des Ordnungssystems mit dem Button *Hinzufügen* aus. Bei der Ansicht des
Ordnungssystems werden nur die Dossiers angezeigt, die sich noch in
Bearbeitung befinden.\ |image183|

Mit dem Speichern wird die Aufgabe samt den angehängten Dokumenten in
das gewählte Dossier kopiert. Dokumente, die mit der Aufgabe
herunterkopiert werden, erhalten bei der Version automatisch den
Kommentar "Dokument von Aufgabe kopiert (Aufgabe akzeptiert)". In der
kopierten Aufgabe wird auf die ursprüngliche Aufgabe im Dossier des
Auftraggebers verwiesen.

|image184|

Im Dossier des Auftraggebers wird ebenfalls auf die kopierte Aufgabe des
Auftragnehmers hingewiesen. Der Status der ursprünglichen und der
kopierten Aufgabe wird immer automatisch synchronisiert.

|image185|

Die Aufgabe wird nun im eigenen Dossier bearbeitet, indem beispielsweise
dem Dossier neue Dokumente hinzugefügt werden oder ein mitgeschicktes
Dokument bearbeitet wird.

.. note::
   Bearbeitet der Auftragnehmer vom Auftraggeber mitgesendete Dokumente, so
   handelt es sich dabei um **Kopien**, die dem Auftraggeber bei der
   Auftragserledigung erneut übermittelt werden müssen.

| Beim Erledigen der Aufgabe kann aus der Auflistung der Dokumente
  ausgewählt werden, welche Dateien dem Auftraggeber übermittelt werden
  sollen. Die gewählten Dateien werden dem Auftraggeber als Kopien an
  die Aufgabe gehängt und ins Dossier gelegt.
| Alle Dokumente, die der Auftragnehmer zurücksendet, erscheinen beim
  Auftraggeber mit der Vorsilbe ***AW: (Antwort)***. Auf Ebene Version
  erhalten diese Dokumente automatisch den Kommentar "Dokument von
  Aufgabe kopiert (Aufgabe erledigt)".\ |image188|

Aufgabe in einem neuen Dossier im eigenen Mandanten bearbeiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Klicken Sie beim Akzeptieren der Aufgabe auf die Option *in einem neuen
Dossier auf Mandant x bearbeiten* und klicken Sie *Weiter*.

|image189|

Wählen Sie die Ordnungsposition, unter der das Dossier erstellt werden
soll, durch die direkte Texteingabe oder durch Anzeigen des
Ordnungssystems mit dem Button *Hinzufügen* aus. Hinweis: Falls auf der
gewählten Ordnungsposition mehrere Dossiertypen (z.B. Geschäftsdossier
und Falldossier) hinterlegt sind, werden Sie in einem Zwischenschritt
nach dem Dossiertyp gefragt.\ |image190|

|image191|

Im nächsten Schritt wird das Dossier unter der gewünschten Position
angelegt. Dabei wird automatisch der Titel des Dossiers des
Auftraggebers übernommen. Dieser kann bei Bedarf geändert werden.

Gleichzeitig wird die Aufgabe samt den angehängten Dokumenten in das neu
angelegte Dossier kopiert. Dokumente, die mit der Aufgabe
herunterkopiert werden, erhalten bei der Version automatisch den
Kommentar "Dokument von Aufgabe kopiert (Aufgabe akzeptiert)". In dieser
kopierten Aufgabe wird auf die ursprüngliche Aufgabe im Dossier des
Auftraggebers verwiesen.

Auch im Dossier des Auftraggebers wird auf die kopierte Aufgabe des
Auftragnehmers hingewiesen. Der Status der ursprünglichen und der
kopierten Aufgabe wird immer synchronisiert.\ |image192|\ |image193|

Die Aufgabe wird nun im eigenen Dossier bearbeitet, indem beispielsweise
dem Dossier neue Dokumente hinzugefügt werden oder ein mitgeschicktes
Dokument bearbeitet wird. |image194|

|image195|

| Beim Erledigen der Aufgabe kann aus der Auflistung der Dokumente
  ausgewählt werden, welche Dateien dem Auftraggeber übermittelt werden
  sollen. Die gewählten Dateien werden dem Auftraggeber als Kopien an
  die Aufgabe gehängt und ins Dossier gelegt.
| Alle Dokumente, die der Auftragnehmer zurücksendet, erscheinen beim
  Auftraggeber mit der Vorsilbe ***AW:** (Antwort)*. Auf Ebene Version
  erhalten diese Dokumente automatisch den Kommentar "Dokument von
  Aufgabe kopiert (Aufgabe erledigt)".\ |image196|

Spezialfall mandantenübergreifende Zur Kenntnisnahme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Soll beispielsweise ein RRB (Regierungsratsbeschluss) einem
Direktionssekretariat oder einer Amtsstelle zur Kenntnisnahme übergeben
werden, geht man wie folgt vor:

-  Der Auftraggeber erstellt mit dem entsprechenden Dokument eine
   Aufgabe vom Typ "Zur Kenntnisnahme" zuhanden des betreffenden
   Mandanten.

|image197|

|image198|

-  Der Auftragnehmer öffnet die Aufgabe im Eingangskorb (bzw. weist sie
   dem zuständigen Sachbearbeiter zu, der die Aufgabe anschliessend
   unter *Meine Aufgaben* findet).

|image199|

-  Mit der Aktion *Abschliessen* wird die Aufgabe im Mandanten des
   Auftraggebers automatisch abgeschlossen\ |image200|

-  Im nächsten Schritt hat der Auftragnehmer die Möglichkeit, Dokumente
   anzuklicken, die in ein eigenes Dossier kopiert werden
   sollen.\ |image201|

-  Mit *Weiter* gelangt man zur Auswahl des Zieldossiers (direkte
   Texteingabe oder Auswahl mit *Hinzufügen*).\ |image202|

-  Nach dem Speichern werden die angeklickten Dokumente ins Zieldossier
   kopiert. Die Aufgabe wird beim Aufgabentyp "Zur Kenntnisnahme" nicht
   mitkopiert.\ |image203|

Spezialfall Delegieren
^^^^^^^^^^^^^^^^^^^^^^

Mit der Funktion Delegieren kann eine Aufgabe mit wenig Aufwand gleich
mehreren Adressaten zugestellt werden, sowohl mandantenintern als auch
mandantenextern. Ein möglicher Anwendungsfall ist eine Vernehmlassung.

Vorgehen:

-  Erstellen Sie zunächst eine Aufgabe mit den Dokumenten, die im
   nächsten Schritt an andere Stellen weitergegeben werden sollen.
   Akzeptieren Sie diese Aufgabe (die Funktion Delegieren steht erst
   dann zur Verfügung).

   |image204|

-  Wählen Sie durch Texteingabe alle Adressaten aus, an welche die
   Aufgabe gerichtet werden soll und klicken Sie die Dokumente an, die
   der Aufgabe mitgegeben werden sollen.


   Klicken Sie auf *Weiter*.

   |image205|

.. note::
   Achtung: Die Dokumente werden beim Anhängen an die Aufgabe nicht
   kopiert; es handelt sich dabei lediglich um einen Link auf dasselbe
   Dokument!

|image208|

-  Passen Sie bei Bedarf den Aufgabentitel und das Datum an und
   speichern Sie.

-  Nach dem Speichern werden unter der ursprünglich erstellten
   Hauptaufgabe so viele Unteraufgaben erzeugt wie Sie Adressaten
   eingegeben haben. Die Unteraufgabe ist auf der Hauptaufgabe
   ersichtlich (und umgekehrt). Sollen noch mehr Adressaten hinzugefügt
   werden, kann das Delegieren beliebig oft wiederholt
   werden.\ |image209|

.. note::
   Wurde eine Delegation mandantenübergreifend erstellt, hat der Empfänger
   die Möglichkeit, die Aufgabe direkt im Dossier des Auftraggebers oder in
   einem eigenen Dossier zu bearbeiten (analog zu einer anderen
   mandantenübergreifenden Aufgabe).

   Wird die Aufgabe direkt im Dossier des Auftraggebers bearbeitet, ist zu
   beachten, dass ein mitgesendetes Dokument unter Umständen heruntergeladen
   werden muss, damit nicht alle mit demselben Dokument arbeiten (z.B. bei
   Stellungnahmen, die von verschiedenen Amtsstellen eintreffen sollten).

   Die Hauptaufgabe kann erst erledigt und abgeschlossen werden, wenn alle
   Unteraufgaben abgeschlossen sind.

Aufgaben überwachen (Pendenzenkontrolle)
----------------------------------------

Unter der Komponente Übersicht werden die persönlichen Aufgaben sowie
diejenigen des ganzen Amtes aufgelistet. Dies ermöglicht eine
persönliche und eine zentrale Pendenzenkontrolle. Mandantenübergreifende
Aufgaben sind mit einem speziellen Icon versehen: |image212|

.. note::
   Die Spalte *Mandant* gibt an, in welchem Mandanten eine Aufgabe und damit
   das zugehörige Dossier gespeichert ist. Wurde eine Aufgabe aus einem
   anderen Mandanten in ein eigenes Dossier kopiert, so wird unter der Spalte
   *Mandant* der eigene Mandant angegeben, weil die Aufgabe hier gespeichert
   ist. In der Spalte *Mandant* wird also nur dann ein anderer Mandant
   angegeben, wenn sich zur betreffenden Aufgabe kein Dossier im eigenen
   Mandanten befindet.

Persönliche Aufgabenkontrolle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Reiter *Meine Aufgaben* und *Erteilte Aufgaben* unter der
Arbeitskomponente Übersicht dienen der persönlichen,
dossierübergreifenden Aufgabenübersicht. Mit einem Klick auf den Titel
öffnet sich die Aufgabe. Der Breadcrumb-Pfad verweist auf das Dossier,
zu dem die Aufgabe gehört und auf die Position im Ordnungssystem, unter
der das Dossier abgelegt ist.

Der Reiter *Meine Aufgaben* listet die mir zugewiesenen Aufgaben auf.
Darunter können sich auch Aufgaben aus anderen Mandanten befinden, d.h.
Aufgaben, zu denen im eigenen Mandanten kein Dossier besteht. In diesem
Fall ist unter der Spalte Mandant ein fremder Mandant eingetragen.

Standardmässig werden nur die pendenten Aufgaben angezeigt: Status
*Offen*, *In Arbeit*, *Erledigt*, *Abgelehnt*. Sollen auch die
abgeschlossenen und stornierten Aufgaben angezeigt werden, muss beim
Status *Alle* gewählt werden.\ |image215|

Unter dem Reiter *Erteilte Aufgaben* sind die Aufgaben zu finden, die
ich anderen Personen zugewiesen habe. Hier sind naturgemäss nur Aufgaben
zu finden, die (zusammen mit den Dossiers) im eigenen Mandanten
gespeichert sind. Die Auftragnehmer können jedoch anderen Mandanten
angehören.

|image216|

Es bestehen folgende Auswertungsmöglichkeiten: Ausgewählte Aufgaben
können als PDF oder in eine Excel-Tabelle exportiert werden. Die
Auswertung muss für *Meine Aufgaben* und *Erteilte Aufgaben* separat
vorgenommen werden. Zu den Sortierungsmöglichkeiten siehe
:ref:`Spalten sortieren <label-spalten-sortieren>`.

|image217|

Zentrale Aufgabenkontrolle
~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Reiter *Alle Aufgaben* und *Alle erteilten Aufgaben* unter der
Anwendungskomponente Übersicht listen sämtliche Aufgaben und Aufträge
aller Mitarbeiter/innen eines Mandanten auf. Diese Darstellung erlaubt
eine Übersicht über alle offenen und abgeschlossenen Aufgaben bzw.
Aufträge einer Verwaltungsstelle. Der Zugriff auf die zentrale
Aufgabenkontrolle ist nur mit spezieller Berechtigung möglich;
standardmässig wird sie dem Sekretariat und der Leitung zugeteilt.

-  **Reiter** *Alle Aufgaben* **(alle Aufgaben, deren Auftragnehmer
   Personen aus dem eigenen Mandanten sind):** Der Reiter *Alle
   Aufgaben* listet die zu erledigenden Aufgaben sämtlicher
   Mitarbeiter/innen des jeweiligen Mandanten auf. Darunter können sich
   auch Aufgaben aus anderen Mandanten befinden, d.h. Aufgaben, zu denen
   im eigenen Mandanten kein Dossier besteht. Dies ist dadurch
   ersichtlich, dass in der Spalte "Mandant" ein anderer als der eigene
   aufgelistet ist.

|image218|

-  **Reiter** *Alle erteilten Aufgaben* **(alle Aufgaben, deren
   Auftraggeber Personen aus dem eigenen Mandanten sind):** Der Reiter
   *Alle erteilten Aufgaben* listet jene Aufgaben auf, die
   Mitarbeiter/innen des Amts intern oder an eine andere Amtsstelle
   erteilt haben. Unter diesem Reiter gibt es deshalb nur Aufgaben, die
   (zusammen mit den Dossiers) im eigenen Mandanten gespeichert sind.
   Die Auftragnehmer können jedoch anderen Mandanten angehören.

|image219|

-  Bei der zentralen Pendenzenliste bestehen folgende
   Auswertungsmöglichkeiten:

-  Ausdruck einer ausgewählten Menge von Aufgaben als PDF oder Export
   nach Microsoft Excel. Die Auswertung muss für "Alle Aufgaben" und
   "Alle erteilten Aufgaben" separat vorgenommen werden.

    |image220|\ |image221|

-  Personen, die berechtigt sind, alle Aufgaben einer Amtsstelle zu
   sehen, steht die Aktion *Pendenzenliste* zur Verfügung. Mit Klick auf
   diese Aktion wird automatisch eine Liste aller pendenten Aufgaben
   (erhaltene und erteilte) im PDF-Format erstellt.

Aufgaben stellvertretend bearbeiten
-----------------------------------

Personen, die berechtigt sind, alle Aufgaben einer Amtsstelle zu sehen,
können Aufgaben stellvertretend für ihre Mitarbeiter bearbeiten. Dabei
können Sie Aktionen stellvertretend für Mitarbeiter durchführen.

Es kann z.B. eine Sekretärin stellvertretend für einen abwesenden
Sachbearbeiter eine Aufgabe erledigen.

Ab dem Release 3.0 werden Aktionen welche nur aufgrund der
Stellvertreter-Berechtigung zur Verfügung stehen, in einem separaten
Dropdown dargestellt. Dies soll eine unbewusste Stellvertretung bei
Aufgaben verhindern.

|image222|

.. |img-aufgaben-1| image:: img/media/img-aufgaben-1.png
.. |img-aufgaben-2| image:: img/media/img-aufgaben-2.png
.. |img-aufgaben-3| image:: img/media/img-aufgaben-3.png
.. |img-aufgaben-4| image:: img/media/img-aufgaben-4.png
.. |img-aufgaben-5| image:: img/media/img-aufgaben-5.png
.. |img-aufgaben-6| image:: img/media/img-aufgaben-6.png
.. |img-aufgaben-7| image:: img/media/img-aufgaben-7.png
.. |img-aufgaben-8| image:: img/media/img-aufgaben-8.png
.. |img-aufgaben-8b| image:: img/media/img-aufgaben-8b.png
.. |img-aufgaben-9| image:: img/media/img-aufgaben-9.png
.. |img-aufgaben-10| image:: img/media/img-aufgaben-10.png
.. |img-aufgaben-11| image:: img/media/img-aufgaben-11.png
.. |img-aufgaben-12| image:: img/media/img-aufgaben-12.png
.. |img-aufgaben-13| image:: img/media/img-aufgaben-13.png
.. |img-aufgaben-14| image:: img/media/img-aufgaben-14.png
.. |img-aufgaben-15| image:: img/media/img-aufgaben-15.png
.. |img-aufgaben-16| image:: img/media/img-aufgaben-16.png
.. |img-aufgaben-17| image:: img/media/img-aufgaben-17.png
.. |img-aufgaben-18| image:: img/media/img-aufgaben-18.png
.. |img-aufgaben-19| image:: img/media/img-aufgaben-19.png
.. |img-aufgaben-20| image:: img/media/img-aufgaben-20.png
.. |img-aufgaben-21| image:: img/media/img-aufgaben-21.png
.. |img-aufgaben-22| image:: img/media/img-aufgaben-22.png
.. |img-aufgaben-23| image:: img/media/img-aufgaben-23.png
.. |img-aufgaben-24| image:: img/media/img-aufgaben-24.png
.. |img-aufgaben-25| image:: img/media/img-aufgaben-25.png
.. |img-aufgaben-26| image:: img/media/img-aufgaben-26.png


.. |image138| image:: img/media/image134.png
.. |image139| image:: img/media/image135.png
.. |image140| image:: img/media/image136.png
.. |image141| image:: img/media/image137.png
.. |image146| image:: img/media/image142.png
   :width: 0.33333in
   :height: 0.33333in
.. |image147| image:: img/media/image143.png
   :width: 0.26042in
   :height: 0.30208in
.. |image148| image:: img/media/image143.png
   :width: 0.26042in
   :height: 0.30208in
.. |image149| image:: img/media/image143.png
   :width: 0.26042in
   :height: 0.30208in
.. |image150| image:: img/media/image144.png
   :width: 6.23611in
.. |image152| image:: img/media/image145.png
   :width: 0.31250in
   :height: 0.28125in
.. |image153| image:: img/media/image145.png
   :width: 0.31250in
   :height: 0.28125in
.. |image154| image:: img/media/image145.png
   :width: 0.31250in
   :height: 0.28125in
.. |image155| image:: img/media/image145.png
   :width: 0.31250in
   :height: 0.28125in
.. |image156| image:: img/media/image146.png
   :width: 6.25694in
.. |image157| image:: img/media/image147.png
   :width: 6.12153in
.. |image158| image:: img/media/image148.png
   :width: 5.62153in
.. |image159| image:: img/media/image149.png
   :width: 2.45347in
   :height: 0.50764in
.. |image160| image:: img/media/image150.png
   :width: 2.45833in
.. |image161| image:: img/media/image151.png
   :width: 5.87153in
.. |image162| image:: img/media/image152.png
   :width: 6.25694in
.. |image163| image:: img/media/image153.png
   :width: 6.12500in
.. |image164| image:: img/media/image154.png
   :width: 5.87083in
.. |image165| image:: img/media/image155.png
   :width: 6.12153in
.. |image166| image:: img/media/image156.png
   :width: 6.25694in
.. |image167| image:: img/media/image157.png
   :width: 2.49306in
.. |image168| image:: img/media/image158.png
   :width: 6.25694in
.. |image169| image:: img/media/image159.png
   :width: 6.24653in
.. |image170| image:: img/media/image160.png
   :width: 6.25694in
.. |image171| image:: img/media/image161.png
   :width: 2.41667in
.. |image172| image:: img/media/image162.png
   :width: 6.25694in
.. |image173| image:: img/media/image163.png
   :width: 6.25694in
   :height: 6.11111in
.. |image174| image:: img/media/image164.png
   :width: 0.25694in
.. |image175| image:: img/media/image165.png
   :width: 6.12500in
.. |image176| image:: img/media/image166.png
   :width: 6.12153in
.. |image177| image:: img/media/image167.png
   :width: 6.12500in
.. |image178| image:: img/media/image168.png
   :width: 6.00000in
.. |image179| image:: img/media/image169.png
   :width: 6.25694in
.. |image180| image:: img/media/image170.png
   :width: 5.74653in
.. |image181| image:: img/media/image171.png
   :width: 6.25000in
.. |image182| image:: img/media/image172.png
   :width: 6.25000in
.. |image183| image:: img/media/image173.png
   :width: 6.25694in
.. |image184| image:: img/media/image174.png
   :width: 6.00000in
.. |image185| image:: img/media/image175.png
   :width: 6.25694in
.. |image186| image:: img/media/image176.png
   :width: 6.23611in
.. |image187| image:: img/media/image177.png
   :width: 0.65625in
.. |image188| image:: img/media/image178.png
   :width: 5.87500in
.. |image189| image:: img/media/image179.png
   :width: 6.00000in
.. |image190| image:: img/media/image180.png
   :width: 5.87153in
.. |image191| image:: img/media/image181.png
   :width: 6.12153in
.. |image192| image:: img/media/image182.png
   :width: 6.27083in
.. |image193| image:: img/media/image183.png
   :width: 6.25000in
.. |image194| image:: img/media/image177.png
   :width: 0.71875in
.. |image195| image:: img/media/image176.png
   :width: 6.23611in
.. |image196| image:: img/media/image184.png
   :width: 5.98472in
.. |image197| image:: img/media/image185.png
   :width: 6.25000in
.. |image198| image:: img/media/image186.png
   :width: 6.25000in
   :height: 2.66667in
.. |image199| image:: img/media/image187.png
   :width: 5.87500in
.. |image200| image:: img/media/image188.png
   :width: 6.25694in
.. |image201| image:: img/media/image189.png
   :width: 6.25694in
.. |image202| image:: img/media/image190.png
   :width: 6.25694in
.. |image203| image:: img/media/image191.png
   :width: 6.25556in
.. |image204| image:: img/media/image192.png
   :width: 6.25694in
.. |image205| image:: img/media/image193.png
   :width: 6.12153in
.. |image206| image:: img/media/image177.png
   :width: 0.70833in
.. |image207| image:: img/media/image194.png
   :width: 6.23611in
.. |image208| image:: img/media/image195.png
   :width: 5.99653in
.. |image209| image:: img/media/image196.png
   :width: 6.25694in
.. |image210| image:: img/media/image177.png
   :width: 0.72847in
.. |image211| image:: img/media/image197.png
   :width: 6.23611in
.. |image212| image:: img/media/image164.png
   :width: 0.20833in
   :height: 0.18750in
.. |image213| image:: img/media/image198.png
   :width: 6.23611in
.. |image214| image:: img/media/image177.png
   :width: 0.68750in
.. |image215| image:: img/media/image199.png
   :width: 6.25694in
.. |image216| image:: img/media/image200.png
   :width: 6.25694in
.. |image217| image:: img/media/image201.png
   :width: 6.25694in
.. |image218| image:: img/media/image202.png
   :width: 5.99792in
.. |image219| image:: img/media/image203.png
   :width: 6.11111in
.. |image220| image:: img/media/image204.png
   :width: 5.87500in
.. |image221| image:: img/media/image205.png
   :width: 5.12500in
.. |image222| image:: img/media/image206.png

.. disqus::
