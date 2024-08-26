.. py:class:: opengever.workspace.meeting

    Inhaltstyp 'Meeting'



   .. py:attribute:: responsible

       :Feldname: :field-title:`Organisator`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       :Wertebereich: <Gültige User-ID>


   .. py:attribute:: chair

       :Feldname: :field-title:`Sitzungsleitung`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: <Gültige User-ID>


   .. py:attribute:: secretary

       :Feldname: :field-title:`Protokollführung`
       :Datentyp: ``Choice``
       
       
       
       :Wertebereich: <Gültige User-ID>


   .. py:attribute:: start

       :Feldname: :field-title:`Beginn`
       :Datentyp: ``UTCDatetime``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       


   .. py:attribute:: end

       :Feldname: :field-title:`Ende`
       :Datentyp: ``UTCDatetime``
       
       
       
       


   .. py:attribute:: location

       :Feldname: :field-title:`Ort`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: videoconferencing_url

       :Feldname: :field-title:`Video-Call Link`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: attendees

       :Feldname: :field-title:`Teilnehmer`
       :Datentyp: ``List``
       
       :Default: []
       
       


   .. py:attribute:: guests

       :Feldname: :field-title:`Gäste`
       :Datentyp: ``List``
       
       :Default: []
       
       


   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       


   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       
