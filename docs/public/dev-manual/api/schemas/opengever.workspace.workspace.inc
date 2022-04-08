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
       
       
       
       
