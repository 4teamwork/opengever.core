Kurzreferenz OneGov GEVER: Administration
=========================================

Release 3 / Version 1.0 / 23.02.2016

Dokumentvorlagen
================

DocProperties 
-------------

Mit DocProperties können ausgewählte Metadaten aus Dossiers von OneGov GEVER direkt in Worddokumenten übernommen 
werden. Die folgenden Metadaten werden von OneGov GEVER-beim Öffnen von Worddokumenten automatisch weitergegeben:

- *Dossier.ReferenceNumber* – Aktenzeichen des Dossiers, welches das Dokument enthält

- *Document.ReferenceNumber* – Aktenzeichen des Dokuments

-	*Document.SequenceNumber* – Laufnummer des Dokuments

-	*User.FullName* – Vor- und Nachname des angemeldeten Benutzers

-	*Dossier.Title* – Titel des Dossiers, welches das Dokument enthält

-	*User.ID* – Benutzerkennung des angemeldeten Benutzers

DocProperties in Vorlagen verwenden
-----------------------------------

Damit DocProperties in Worddokumenten verwendet werden können, muss in einem ersten Schritt die entsprechende 
Wordvorlage, die in OneGov GEVER über den Menüpunkt Vorlagen abgelegt ist, vorbereitet werden:

1)	Wählen Sie die Wordvorlage im Vorlagenbereich von OneGov GEVER aus, und öffnen Sie das Dokument zur Bearbeitung (Auschecken und bearbeiten).

2)	Begeben Sie sich in Word auf Datei > Eigenschaften > Erweiterte Eigenschaften > Anpassen.

3)	Geben Sie den Namen der gewünschten DocProperty im Feld Name ein.

4)	Als “Wert” kann vorerst ein Leerschlag (Space) eingefügt werden. Dieser wird bei der Erstellung eines neuen Dokuments ab Vorlage automatisch mit dem aktuellen Metadatenwert überschrieben. 

5)	Die so erstellte DocProperty kann nun über das Feld Hinzufügen den Eigenschaften hinzugefügt werden.
 
6)	Die so erstellten DocProperties sind nun in den Eigenschaften ersichtlich.

7)	Wenn alle gewünschten DocProperties erstellt wurden, mit OK abschliessen. 
 
  Für die Erarbeitung einer neuen Vorlage können auch bestehende Vorlagen überarbeitet werden. So müssen 
  nicht alle DocProperties jedes Mal manuell neu erstellt werden, sondern werden mitkopiert.

Sind alle benötigten DocProperties in der Wordvorlage definiert, können sie nun nach Belieben im Haupttext 
verwendet werden.

Dies geschieht in Word wie folgt:

1)	Die gewünschte Stelle, an der die DocProperty eingefügt werden soll, markieren. 

2)	Den Menüpunkt Einfügen auswählen.

3)	Unter Schnellbausteine die Option Feld auswählen.

4)	Feldname auswählen = DocProperty. 

5)	Gewünschte Eigenschaft auswählen.

6)	Die Option “Feldfunktionen” auswählen.

7)	Ausgewähltes DocProperty in Anführungs - und Schlusszeichen setzen.

8)	Mit “OK” bestätigen.

Die DocProperty ist eingefügt und kann in Word mit Doppelklick > Rechtsklick > Feldfunktion ein an 
der gewünschten Position im Dokument angezeigt und überprüft werden.

DocProperties in Worddokumenten automatisch aktualisieren
---------------------------------------------------------

Wird über OneGov GEVER ein Worddokument zur Bearbeitung geöffnet, zeigt Word standardmässig 
nicht die von OneGov GEVER mitgegebenen Metadaten an. Dies kann manuell erwirkt werden, indem der 
ganze Word-Inhalt markiert und die Funktion Felder aktualisieren aufgerufen wird.

Damit dies von Word automatisch bei jedem Öffnen gemacht wird, muss ein Makro hinterlegt werden. 
Dies muss einmalig in Word gemacht werden, nicht für jede Wordvorlage!

1)	Begeben Sie sich bitte im Word auf Datei > Optionen > Menüband anpassen.

2)	Aktivieren Sie die “Entwicklertools” durch Setzen eines Häkchens in den Hauptregisterkarten aus.

3)	Bestätigen Sie die Änderung mit “OK”.

4)	Sind die “Entwicklertools” dem Menüband hinzugefügt, wählen Sie diese Menü bitte aus.

5)	Begeben Sie sich auf den Menüpunkt “Makros”

6)	Vergeben Sie den Makronamen “AutoOpen”.

7)	Erstellen Sie das Makro über Erstellen. Bei der Option Makros in können "Alle aktiven Dokumentvorlagen und Dokumenten" ausgewählt werden. Damit wird sichergestellt, dass das Makro in allen Dokumenten automatisch verfügbar ist.

8)	Den Code (siehe Tabelle) können Sie dem Feld Normal - NewMacros (Code) hinzufügen.
 
9)	Nachdem Sie den Code eingefügt haben, speichern Sie die Einstellungen ab.

.. sourcecode:: vb

  Sub AutoOpen()
  '
  ' UpdateDocprops Makro
  ' http://www.gmayor.com/installing_macro.htm                    
  '                                                 
  '
  Dim oStory As Range
  For Each oStory In ActiveDocument.StoryRanges
    oStory.Fields.Update
    If oStory.StoryType <> wdMainTextStory Then
      While Not (oStory.NextStoryRange Is Nothing)
        Set oStory = oStory.NextStoryRange
        oStory.Fields.Update
      Wend
    End If
  Next oStory
  Set oStory = Nothing

  End Sub

Nun werden in neu geöffneten Worddokumenten automatisch die DocProperties aktualisiert.

.. |docprops-3| image:: _static/img/kurzref_adm_docprops_3.png
.. |docprops-4| image:: _static/img/kurzref_adm_docprops_4.png
.. |docprops-5| image:: _static/img/kurzref_adm_docprops_5.png
.. |docprops-6| image:: _static/img/kurzref_adm_docprops_6.png
.. |docprops-7| image:: _static/img/kurzref_adm_docprops_7.png
.. |docprops-8| image:: _static/img/kurzref_adm_docprops_8.png
.. |docprops-9| image:: _static/img/kurzref_adm_docprops_9.png
.. |docprops-10| image:: _static/img/kurzref_adm_docprops_10.png
.. |docprops-11| image:: _static/img/kurzref_adm_docprops_11.png
.. |docprops-12| image:: _static/img/kurzref_adm_docprops_12.png
.. |docprops-13| image:: _static/img/kurzref_adm_docprops_13.png
.. |docprops-14| image:: _static/img/kurzref_adm_docprops_14.png
.. |docprops-15| image:: _static/img/kurzref_adm_docprops_15.png


