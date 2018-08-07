OneGov GEVER Release 2.5
========================

Features
--------

|img-release-notes-2.5-1|

In früheren Releases von OneGov GEVER ist es immer wieder vorgekommen, dass Benutzer
eine Datei aus Versehen heruntergeladen haben, statt sie mit dem External Editor
zu bearbeiten, und so wurden von ihnen gemachte Änderungen nicht in OneGov GEVER gespeichert.
Die beiden Aktionen "Herunterladen" und "Bearbeiten" sind wesentlich deutlicher gekennzeichnet,
um den Benutzern die Unterscheidung der beiden Vorgänge zu erleichtern.

Am prominentesten ist diese Änderung in der Übersicht eines Dokuments zu sehen.
Wo vorher ein einzelner Link je nach Status des Dokuments und den Berechtigungen
des Benutzers unterschiedliche Funktionen wahrnahm (PDF Vorschau öffnen, Datei
auschecken und mit External Editor bearbeiten oder Datei herunterladen), sind
diese Funktionen nun durch getrennte Links aufrufbar.

|img-release-notes-2.5-2|

Wählt der Benutzer in dieser Ansicht “Kopie herunterladen”, wird er mittels eines
Hinweisfensters nochmals darauf hingewiesen, dass er dabei ist, die Datei herunterzuladen
und Änderungen demnach nicht in OneGov GEVER gespeichert werden.

Besseres Feedback von Aktions-Buttons
-------------------------------------

|img-release-notes-2.5-3|

Um dem Benutzer besseres Feedback zu geben, dass eine Aktion in Arbeit ist, wird
beim Speichern oder anderweitigen Operationen, welche Daten verändern, der entsprechende
Button nach dem Klicken ausgegraut dargestellt, und ist nicht mehr ein zweites
Mal klickbar. So wird auch verhindert, dass ein ungeduldiger Benutzer, der erneut
auf den Button klickt, einen zweiten Inhalt erstellt.

Navigierbare Baumstruktur für Verweise zwischen Dokumenten
----------------------------------------------------------

|img-release-notes-2.5-4|

Aus Performance-Gründen konnten im Auswahlfeld für Verweise zwischen Dokumenten
bisher zu referenzierende Dokumente nur über ein Autocomplete-Suchfeld eingegeben
werden - zumindest ein Teil des Dokumentnamens musste also bekannt sein.

Im OneGov GEVER Release 2.5 wird nun zusätzlich zu diesem Feld auch eine navigierbare
Baumstruktur dargestellt, analog zu den Verweisen zwischen Dossiers. So ist es nun
möglich, ein Dokument sowohl über eine Autocomplete-Suche wie auch über den navigierbaren
Baum auszuwählen. Zum einen muss so der Name des Dokuments nicht bekannt sein, es
reicht zu wissen in welchem Dossier es sich befindet. Zum anderen ist durch das
dargestellte Icon auch sofort klar, von welchem Format das referenzierte Dokument ist.

Abschliessen einer Aufgabe durch mehr als einen Benutzer
--------------------------------------------------------

Der Workflow von Aufgaben wurde folgendermassen angepasst: Statt wie bisher nur
der Auftraggeber ist neu auch die Eingangskorb-Gruppe des jeweiligen
Auftraggeber-Mandanten berechtigt, die Aufgabe abzuschliessen.

Dies erlaubt der Gruppe von Benutzern, welche den Eingangskorb eines Mandanten
verwalten, auch eine Stellvertreter-Funktion für andere Benutzer ihres Mandanten
wahrzunehmen. Dies ist zum Beispiel hilfreich bei Ferienabwesenheiten oder wenn
ein Benutzer ein Amt verlässt, aber noch Auftraggeber von
Aufgaben ist, die er noch nicht abgeschlossen hat.

Vereinfachtes Bearbeiten von Metadaten
--------------------------------------

|img-release-notes-2.5-5|

Um die Metadaten eines Dokuments zu bearbeiten, war es bisher erforderlich, dieses
Dokument im Dokumenten-Reiter auszuwählen, um auf die Übersicht zu gelangen, und
dort die Aktion “Metadaten bearbeiten” zu wählen. Da die bisherigen Erfahrungen zeigen,
dass dies eine der häufigsten Aktionen ist, welche die Benutzer durchführen, wurde dieser
Vorgang erheblich vereinfacht und ist nun mit wenigen Klicks erreichbar.

Bewegt der Benutzer den Mauszeiger über das Icon eines Dokuments im Dokumenten-Reiter,
so erscheint ein Tooltip mit den wichtigsten Informationen zum Dokument und der Möglichkeit,
drei der häufigsten Aktionen direkt durchzuführen: Metadaten bearbeiten, PDF Vorschau
anzeigen und das Dokument auschecken und bearbeiten.

Status-Filter für Dossiers
--------------------------

|img-release-notes-2.5-6|

Um das tägliche Arbeiten mit OneGov GEVER zu erleichtern und effizienter zu gestalten,
wurde für die Dossier-Reiter auf Ordnungssystemen und Ordnungspositionen ein
Status-Filter umgesetzt, ähnlich dem Filter, den es bereits für Aufgaben gibt.

Dieser Filter stellt standardmässig nur aktive Dossiers dar, also Dossiers, die
sich im Status “offen” befinden. Wird dieser Filter auf “Alle” geändert, werden
auch Dossiers im Status “abgeschlossen” oder “storniert” dargestellt.

Dieses Feature trägt dem Umstand Rechnung, dass in der täglichen Arbeit mit
OneGov GEVER vorwiegend mit aktiven Dossiers gearbeitet wird. Sollte aber der
Zugriff auf ein abgeschlossenes oder storniertes Dossier nötig sein, ist dieses
einfach durch Umschalten des Filters erreichbar.

Periodische Konvertierung fehlender PDFs
----------------------------------------

Da aus verschiedenen Gründen beim Rendern einer PDF-Vorschau für ein Dokument
eine Störung auftreten kann (PDF Rendition Service nicht erreichbar oder überlastet,
Netzwerkverbindung, ...), ist es möglich dass für gewisse Dokumente keine PDF-Vorschau
existiert. Aus diesem Grund wurde ein Mechanismus entwickelt, der periodisch Dokumente
überprüft, die keine PDF-Vorschau haben, und die Erzeugung eines PDFs
wenn nötig nachholt. Um einen externen PDF Rendition Service nicht mit Anfragen
zu überlasten, werden Konvertierungsaufträge gestaffelt aufgegeben.

Verbesserte Darstellung des History-Viewlets
--------------------------------------------

|img-release-notes-2.5-7|

Im Zusammenhang mit der Anpassung der Dokumenten-Übersicht um die Aktionen
“Dokument herunterladen” und “Dokument auschecken und bearbeiten” klarer voneinander
zu trennen wurde auch das History-Viewlet zum Anzeigen der Versionen angepasst.

Die Aktion zum Herunterladen eines Dokuments ist nun unmissverständlich als “Kopie herunterladen”
gekennzeichnet und mit einem entsprechenden Icon versehen. Auch erscheint nach dem
Klick auf “Kopie herunterladen” derselbe Warnhinweis wie beim
Herunterladen einer Kopie über die Dokumenten-Übersicht.

Optimierungen am Layout des Dossier-Deckblatts
----------------------------------------------

Die Darstellung des automatisch generierten PDF-Deckblatts für Dossiers wurde angepasst.
Es wird eine kleinere Schriftgrösse verwendet um den verfügbaren Platz effizienter
nutzen zu können, und dargestellter Text wie Titel oder Beschreibung werden falls
nötig gekürzt, um sicherzustellen, dass das Deckblatt nur eine einzige Seite umfasst.
Muss der Text gekürzt werden, wird dies mit einer Ellipse (…) angedeutet.

Neues TabbedView Menü
---------------------

|img-release-notes-2.5-8|

Für alle Tabellenansichten wurde ein Einstellungsmenü implementiert, welches über
das Schraubenschlüssel-Symbol rechts erreichbar ist.

Das Menü erlaubt es zum einen, die Tabellenkonfiguration für einen Reiter zurückzusetzen,
um die Standard-Einstellungen bezüglich der Tabellenspalten, Sortierung und
Gruppierung wiederherzustellen. Zum anderen enthält es die Option, den aktuellen Reiter
als Standard-Reiter zu definieren. Damit ist es möglich, zu definieren welcher Reiter
beim Aufrufen eines bestimmten Kontexts als erstes dargestellt wird.


Datei-Download in der Maske “Metadaten bearbeiten” unterbunden
--------------------------------------------------------------

Bisher war es möglich, über die Maske “Metadaten bearbeiten” die aktuelle Arbeitskopie
eines Dokuments herunterzuladen. Aus Datenschutzgründen wurde dies im Release 2.5 unterbunden.
So ist es Benutzern möglich, über längere Zeit an einem Entwurf eines Dokuments
zu arbeiten, dessen Stand zwar auf dem Server gespeichert wird, aber für andere
Benutzer nicht einsehbar ist, bis er eingecheckt wird.

Aus Aufgaben referenzierte Dokumente als E-Mail versenden
---------------------------------------------------------

Bei der Aktion “Als E-Mail versenden” wurden bisher nur Dokumente zum Anhängen
als Attachment angeboten, die direkt im entsprechenden Dossier abgelegt sind.
Neu ist es auch möglich, Dokumente anzuhängen, die mittels einer
mandantenübergreifenden Aufgabe in das Dossier kopiert wurden.

Anpassungen beim Abschliessen von mandantenübergreifenden Aufgaben
------------------------------------------------------------------

Der Mechanismus zum Abschliessen einer aus einer Weiterleitung
entstandenen Aufgabe wurde überarbeitet:

Wird eine mandantenübergreifende Weiterleitung akzeptiert und damit in den
Eingangskorb des Auftragnehmers kopiert, wird bei dieser Weiterleitung der
Auftraggeber auf dem Eingangskorb des Auftragnehmer-Mandanten angepasst.

Ein Beispiel:

- Mandantenübergreifende Weiterleitung, Auftraggeber: Amt 1/Eingangskorb, Auftragnehmer Amt 2/Eingangskorb

- Eingangskorb Amt 2 Benutzer akzeptiert die Aufgabe

- Weiterleitung im Amt 1 wird abgelegt.

- Weiterleitung wird in den Amt 2 kopiert, NEU: dabei wird der Auftraggeber von Amt 1/Eingangskorb nach Amt 2/Eingangskorb geändert.

- Die restlichen Vorgänge bleiben bestehen.

PDF-Generierung: Änderung der Hinweis-Meldung zur besseren Verständlichkeit
---------------------------------------------------------------------------

Die Meldung, die erscheint, wenn für ein Dokument noch keine PDF-Vorschau erzeugt
wurde, wurde angepasst. Neu lautet die Meldung: “Das Erstellen des PDF nimmt einige Sekunden in Anspruch”

E-Mails mit Aufgaben versenden
------------------------------

Bisher war es bei mandantenübergreifendenen Aufgaben nur möglich, Dokumente
anzuhängen. Neu ist es auch möglich, E-Mails als Anhänge zu Aufgaben zu versenden.

Bugfixes
--------

- Darstellung des Dokument-Tooltips auf einem fremden Mandanten wurde korrigiert.

- Ein durch “Metadaten bearbeiten” ausgestelltes Lock verhindert neu das Auschecken und Bearbeiten eines Dokuments.

- Korrektur eines Fehlers der Darstellung von Umlauten in Mails.

- Korrektur eines Fehlers, der es unter bestimmten Umständen erlaubte eine zu
  tiefe Verschachtelung von Subdossiers zu erreichen.

- Korrektur eines Fehlers beim Abgleichen des OGDS-Caches.

- Korrektur eines Fehlers beim Abschliessen eines Dossiers mit einer Ablagenummer, aber ohne Ablagepräfix.

- Korrektur eines Unicode-Fehlers beim Verschieben von Objekten.

- Korrektur eines Fehlers der es unter bestimmten Umständen ermöglichte,
  eine mandantenübergreifende Aufgabe doppelt zu akzeptieren.

- Korrektur eines Fehlers beim Speichern der Tabellenkonfiguration von Tabs.

.. |img-release-notes-2.5-1| image:: ../../_static/img/img-release-notes-2.5-1.png
.. |img-release-notes-2.5-2| image:: ../../_static/img/img-release-notes-2.5-2.png
.. |img-release-notes-2.5-3| image:: ../../_static/img/img-release-notes-2.5-3.png
.. |img-release-notes-2.5-4| image:: ../../_static/img/img-release-notes-2.5-4.png
.. |img-release-notes-2.5-5| image:: ../../_static/img/img-release-notes-2.5-5.png
.. |img-release-notes-2.5-6| image:: ../../_static/img/img-release-notes-2.5-6.png
.. |img-release-notes-2.5-7| image:: ../../_static/img/img-release-notes-2.5-7.png
.. |img-release-notes-2.5-8| image:: ../../_static/img/img-release-notes-2.5-8.png

.. disqus::
