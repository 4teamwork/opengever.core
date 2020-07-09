.. py:class:: opengever.dossier.businesscasedossier

    Inhaltstyp 'Geschäftsdossier'



   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       


   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       


   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: keywords

       :Feldname: :field-title:`Schlagwörter`
       :Datentyp: ``Tuple``
       
       
       :Beschreibung: Schlagwörter zur Umschreibung eines Dossiers. Nicht zu verwechseln mit der Ordnungsposition. ACHTUNG: Beachten Sie bei der Verwendung von Schlagwörter die Datenschutzvorgaben (z.B. keine Eigennamen).
       


   .. py:attribute:: start

       :Feldname: :field-title:`Beginn`
       :Datentyp: ``Date``
       
       :Default: <Aktuelles Datum>
       
       


   .. py:attribute:: end

       :Feldname: :field-title:`Ende`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: touched

       :Feldname: :field-title:`Änderungsdatum des Dossiers oder seines Inhalts`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: comments

       :Feldname: :field-title:`Kommentar`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: responsible

       :Feldname: :field-title:`Federführend`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       :Wertebereich: <Gültige User-ID>


   .. py:attribute:: external_reference

       :Feldname: :field-title:`Externe Referenz`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: filing_prefix

       :Feldname: :field-title:`Ablage Präfix`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: ["administration", "department", "directorate", "government", "personal"]


   .. py:attribute:: container_type

       :Feldname: :field-title:`Behältnis-Art`
       :Datentyp: ``Choice``
       
       
       :Beschreibung: Art des Behälters, in dem ein Dossier in Papierform abgelegt ist
       :Wertebereich: ["box", "dossier", "folder"]


   .. py:attribute:: number_of_containers

       :Feldname: :field-title:`Anzahl Behältnisse`
       :Datentyp: ``Int``
       
       
       :Beschreibung: Anzahl Behälter, die ein (grosses) Dossier in Papierform enthalten
       


   .. py:attribute:: container_location

       :Feldname: :field-title:`Behältnis-Standort`
       :Datentyp: ``TextLine``
       
       
       :Beschreibung: Standortangabe des Behälters, in dem ein Dossier in Papierform abgelegt ist
       


   .. py:attribute:: relatedDossier

       :Feldname: :field-title:`Verwandte Dossiers`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       


   .. py:attribute:: former_reference_number

       :Feldname: :field-title:`Früheres Aktenzeichen`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: reference_number

       :Feldname: :field-title:`Aktenzeichen`
       :Datentyp: ``TextLine``
       
       
       
       


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
       


   .. py:attribute:: retention_period

       :Feldname: :field-title:`Aufbewahrungsdauer (Jahre)`
       :Datentyp: ``Choice``
       
       :Default: 5
       :Beschreibung: Zeitraum zwischen dem jüngsten Dokumentdatum eines in einem Dossier enthaltenen Dokuments und dem Zeitpunkt, an dem dieses für die Geschäftstätigkeit der Verwaltungseinheit nicht mehr benötigt wird.
       :Wertebereich: [5, 10, 15, 20, 25]


   .. py:attribute:: retention_period_annotation

       :Feldname: :field-title:`Kommentar zur Aufbewahrungsdauer`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: archival_value

       :Feldname: :field-title:`Archivwürdigkeit`
       :Datentyp: ``Choice``
       
       :Default: "unchecked"
       :Beschreibung: Archivwürdigkeit
       :Wertebereich: ["unchecked", "prompt", "archival worthy", "not archival worthy", "archival worthy with sampling"]


   .. py:attribute:: archival_value_annotation

       :Feldname: :field-title:`Kommentar zur Archivwürdigkeit`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: custody_period

       :Feldname: :field-title:`Archivische Schutzfrist (Jahre)`
       :Datentyp: ``Choice``
       
       :Default: 30
       :Beschreibung: Dauer, während der nach der Archivierung die Dokumente vor öffentlicher Einsichtnahme geschützt sind.
       :Wertebereich: [0, 30, 100, 150]


   .. py:attribute:: date_of_cassation

       :Feldname: :field-title:`Kassationsdatum`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: date_of_submission

       :Feldname: :field-title:`Anbietezeitpunkt`
       :Datentyp: ``Date``
       
       
       
       
