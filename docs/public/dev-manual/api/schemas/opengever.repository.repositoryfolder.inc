.. py:class:: opengever.repository.repositoryfolder

    Inhaltstyp 'Ordnungsposition'



   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       :Default: null
       :Beschreibung: Eine kurze Beschreibung des Inhalts.
       


   .. py:attribute:: valid_from

       :Feldname: :field-title:`Gültig ab`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: valid_until

       :Feldname: :field-title:`Gültig bis`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: location

       :Feldname: :field-title:`Standort`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: referenced_activity

       :Feldname: :field-title:`Leistung`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: former_reference

       :Feldname: :field-title:`Früheres Zeichen`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: addable_dossier_types

       :Feldname: :field-title:`Erlaubte Spezialdossiers`
       :Datentyp: ``List``
       
       
       :Beschreibung: Wählen Sie die Spezialdossiers aus, die in dieser Ordnungsposition erlaubt sind.
       


   .. py:attribute:: allow_add_businesscase_dossier

       :Feldname: :field-title:`Hinzufügen von Geschäftsdossiers erlauben`
       :Datentyp: ``Bool``
       
       
       :Beschreibung: Wählen Sie, ob es in dieser Ordnungsposition erlaubt ist, Geschäftsdossiers hinzuzufügen. Ist diese Option deaktiviert, kann der Benutzer nur Dossiers aus einer Vorlage oder Spezialdossiers erstellen.
       


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

       :Feldname: :field-title:`Datenschutzstufe`
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
       


   .. py:attribute:: title_de

       :Feldname: :field-title:`Titel (deutsch)`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: title_fr

       :Feldname: :field-title:`Titel (französisch)`
       :Datentyp: ``TextLine``
       
       
       
       


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
       
       
       
       


   .. py:attribute:: reference_number_prefix

       :Feldname: :field-title:`Präfix des Aktenzeichens`
       :Datentyp: ``TextLine``
       
       :Default: <Höchste auf dieser Ebene vergebene Nummer + 1>
       
       


   .. py:attribute:: addable_dossier_templates

       :Feldname: :field-title:`Erlaubte Dossiervorlagen`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       
