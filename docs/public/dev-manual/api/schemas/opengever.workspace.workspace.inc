.. py:class:: opengever.workspace.workspace

    Inhaltstyp 'Teamraum'



   .. py:attribute:: responsible

       :Feldname: :field-title:`Besitzer`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: <Gültige ID eines Teamraum Teilnehmers>


   .. py:attribute:: videoconferencing_url

       :Feldname: :field-title:`Videokonferenz URL`
       :Datentyp: ``TextLine``
       
       :Default: <IWorkspaceSettings.videoconferencing_base_url + random UUID>
       :Beschreibung: Verwendete URL um eine Videokonferenz für diesen Teamraum zu starten.
       


   .. py:attribute:: external_reference

       :Feldname: :field-title:`Verknüpftes Dossier`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: gever_url

       :Feldname: :field-title:`GEVER URL`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: hide_members_for_guests

       :Feldname: :field-title:`Teamraum-Teilnehmer für Gäste ausblenden`
       :Datentyp: ``Bool``
       
       
       
       


   .. py:attribute:: meeting_template_header

       :Feldname: :field-title:`Kopfzeile von Meeting-Protokollen`
       :Datentyp: ``JSONField``
       
       
       :Beschreibung: Dynamische Textinhalte sind {page_number}, {number_of_pages} und {print_date}, sowie die Bild-Platzhalter {customer_logo} und {workspace_logo}
       


   .. py:attribute:: meeting_template_footer

       :Feldname: :field-title:`Fusszeile von Meeting-Protokollen`
       :Datentyp: ``JSONField``
       
       :Default: {"right": "{page_number}/{number_of_pages}", "center": "", "left": "{print_date}"}
       :Beschreibung: Dynamische Textinhalte sind {page_number}, {number_of_pages} und {print_date}, sowie die Bild-Platzhalter {customer_logo} und {workspace_logo}
       


   .. py:attribute:: workspace_logo

       :Feldname: :field-title:`Teamraum logo`
       :Datentyp: ``NamedImage``
       
       
       :Beschreibung: Kann in Kopf- und Fusszeilen von Protokollen verwendet werden.
       


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
       
       
       
       


   .. py:attribute:: touched

       :Feldname: :field-title:`Änderungsdatum des Objektes oder seines Inhalts`
       :Datentyp: ``Date``
       
       
       
       
