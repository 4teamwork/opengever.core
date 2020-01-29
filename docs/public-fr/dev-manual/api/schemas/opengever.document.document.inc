.. py:class:: opengever.document.document

    Inhaltstyp 'Dokument'



   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: file

       :Feldname: :field-title:`Datei`
       :Datentyp: ``NamedBlobFile``
       
       
       :Beschreibung: Datei, die zu einem Dossier hinzugefügt wird
       


   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       


   .. py:attribute:: classification

       :Feldname: :field-title:`Klassifikation`
       :Datentyp: ``Choice``
       
       :Default: "unprotected"
       :Beschreibung: Grad, in dem die Unterlagen vor unberechtigter Einsicht geschützt werden müssen.
       :Wertebereich: ["unprotected", "confidential", "classified"]


   .. py:attribute:: privacy_layer

       :Feldname: :field-title:`Datenschutz`
       :Datentyp: ``Choice``
       
       :Default: "privacy_layer_no"
       :Beschreibung: Markierung, die angibt, ob die Unterlagen besonders schützenswerte Personendaten oder Persönlichkeitsprofile gemäss Datenschutzrecht enthalten.
       :Wertebereich: ["privacy_layer_no", "privacy_layer_yes"]


   .. py:attribute:: public_trial

       :Feldname: :field-title:`Öffentlichkeitsstatus`
       :Datentyp: ``Choice``
       
       :Default: "unchecked"
       :Beschreibung: Angabe, ob die Unterlagen gemäss Öffentlichkeitsgesetz zugänglich sind oder nicht.
       :Wertebereich: ["unchecked", "public", "limited-public", "private"]


   .. py:attribute:: public_trial_statement

       :Feldname: :field-title:`Bearbeitungsinformation`
       :Datentyp: ``Text``
       
       :Default: ""
       :Beschreibung: Datum Gesuch, Gesuchsteller, Datum Entscheid, Verweis auf GEVER-Gesuchdossier
       


   .. py:attribute:: relatedItems

       :Feldname: :field-title:`Verwandte Dokumente`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       


   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       :Default: null
       
       


   .. py:attribute:: keywords

       :Feldname: :field-title:`Schlagwörter`
       :Datentyp: ``Tuple``
       
       
       :Beschreibung: Schlagwörter zur Umschreibung eines Dokuments. Nicht zu verwechseln mit der Ordnungsposition. <br>ACHTUNG: Beachten Sie bei der Verwendung von Schlagwörter die Datenschutzvorgaben (z.B. keine Eigennamen).
       


   .. py:attribute:: foreign_reference

       :Feldname: :field-title:`Fremdzeichen`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Referenz auf das entsprechende Dossier des Absenders
       


   .. py:attribute:: document_date

       :Feldname: :field-title:`Dokumentdatum`
       :Datentyp: ``Date``
       
       :Default: <Aktuelles Datum>
       :Beschreibung: Datum des Dokuments
       


   .. py:attribute:: receipt_date

       :Feldname: :field-title:`Eingangsdatum`
       :Datentyp: ``Date``
       
       
       :Beschreibung: Datum, an dem das Dokument über den Korrespondenzweg angekommen ist
       


   .. py:attribute:: delivery_date

       :Feldname: :field-title:`Ausgangsdatum`
       :Datentyp: ``Date``
       
       
       :Beschreibung: Datum, an dem das Dokument über den Korrespondenzweg versandt worden ist
       


   .. py:attribute:: document_type

       :Feldname: :field-title:`Dokumenttyp`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: ["contract", "directive", "offer", "protocol", "question", "regulations", "report", "request"]


   .. py:attribute:: document_author

       :Feldname: :field-title:`Autor`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Nachname Vorname oder ein Benutzerkürzel (wird automatisch nach Nachname Vorname aufgelöst)
       


   .. py:attribute:: preserved_as_paper

       :Feldname: :field-title:`In Papierform aufbewahrt`
       :Datentyp: ``Bool``
       
       :Default: true
       :Beschreibung: In Papierform aufbewahrt
       


   .. py:attribute:: archival_file

       :Feldname: :field-title:`Archivdatei`
       :Datentyp: ``NamedBlobFile``
       
       
       :Beschreibung: Archivtaugliche Version der Originaldatei
       


   .. py:attribute:: archival_file_state

       :Feldname: :field-title:`Status Archivdatei`
       :Datentyp: ``Int``
       
       
       
       
