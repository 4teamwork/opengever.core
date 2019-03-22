DocProperties in Vorlagen verwenden
-----------------------------------

Damit DocProperties in Worddokumenten verwendet werden können, muss in einem
ersten Schritt die entsprechende Wordvorlage, die in OneGov GEVER über den
Menüpunkt Vorlagen abgelegt ist, vorbereitet werden:


Hinzufügen in Eigenschaften
~~~~~~~~~~~~~~~~~~~~~~~~~~~


1. Wählen Sie die Wordvorlage im Vorlagenbereich von OneGov GEVER aus, und
   öffnen Sie das Dokument zur Bearbeitung (Auschecken und bearbeiten).

2. Begeben Sie sich in Word auf Datei > Eigenschaften > Erweiterte
   Eigenschaften > Anpassen.

3. Geben Sie den Namen der gewünschten DocProperty im Feld Name ein.

4. Als “Wert” kann vorerst ein Leerschlag (Space) eingefügt werden. Dieser
   wird bei der Erstellung eines neuen Dokuments ab Vorlage automatisch mit
   dem aktuellen Metadatenwert überschrieben.

5. Die so erstellte DocProperty kann nun über das Feld Hinzufügen den
   Eigenschaften hinzugefügt werden.

   |docprops-3|

6. Die so erstellten DocProperties sind nun in den Eigenschaften ersichtlich.

7. Wenn alle gewünschten DocProperties erstellt wurden, mit OK abschliessen.

   |docprops-4|


.. admonition:: Vorlagen kopieren

   Für die Erarbeitung einer neuen Vorlage können auch bestehende Vorlagen
   überarbeitet werden. So müssen nicht alle DocProperties jedes Mal manuell neu erstellt werden, sondern werden mitkopiert.


Hinzufügen in Haupttext
~~~~~~~~~~~~~~~~~~~~~~~


Sind alle benötigten DocProperties in der Wordvorlage definiert, können sie
nun nach Belieben im Haupttext verwendet werden.

Dies geschieht in Word wie folgt:

1. Die gewünschte Stelle, an der die DocProperty eingefügt werden soll,
   markieren.

   |docprops-5|

2. Den Menüpunkt Einfügen auswählen.

3. Unter Schnellbausteine die Option Feld auswählen.

   |docprops-6|

4. In der Kategorie „Dokument-Information“ anwählen und dann den Feldnamen „DocProperty“ auswählen.

   |docprops-7|

5. Unter „Optionen“ die gewünschte Eigenschaft (welche oben unter Punkt 1.1. hinzugefügt wurde) hinzufügen und mit „OK“ bestätigen.

   |docprops-8|

6. Mit “OK” bestätigen.


Datumsformat anpassen
~~~~~~~~~~~~~~~~~~~~~

Wenn ein Datum DocProperty eingefügt wird z.B. ogg.document.document_date kann das Datumsformat nach Einfügen des DocProperty nachträglich angepasst werden. Dazu kann mit Doppelklick > Rechtsklick > Feldfunktion ein auf die gewünschten Position im Dokument geklickt und gemäss Printscreen unten das Datumsformat angepasst werden:

|docprops-9|

.. note::
    Bei der Funktion *Dokument aus Vorlage erstellen* wird technisch gesehen nur
    ein Dokument kopiert, daher muss das Format .docx und nicht .dotx für die
    Vorlage verwendet werden.


.. |docprops-3| image:: ../_static/img/kurzref_adm_docprops_3.png
.. |docprops-4| image:: ../_static/img/kurzref_adm_docprops_4.png
.. |docprops-5| image:: ../_static/img/kurzref_adm_docprops_5.png
.. |docprops-6| image:: ../_static/img/kurzref_adm_docprops_6.png
.. |docprops-7| image:: ../_static/img/kurzref_adm_docprops_7.png
.. |docprops-8| image:: ../_static/img/kurzref_adm_docprops_8.png
.. |docprops-9| image:: ../_static/img/kurzref_adm_docprops_9.png

.. disqus::
