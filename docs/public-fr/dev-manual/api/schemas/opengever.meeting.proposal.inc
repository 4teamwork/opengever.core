.. py:class:: opengever.meeting.proposal

    Inhaltstyp 'Antrag'



   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       
       :Default: ""
       
       


   .. py:attribute:: description

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       
       
       


   .. py:attribute:: issuer

       :Feldname: :field-title:`Antragssteller`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       :Wertebereich: <User-ID eines gültigen Antragsstellers>


   .. py:attribute:: date_of_submission

       :Feldname: :field-title:``
       :Datentyp: ``Date``
       
       
       :Beschreibung: Eingereicht am
       


   .. py:attribute:: language

       :Feldname: :field-title:`Sprache`
       :Datentyp: ``Choice``
       
       :Default: <User-spezifischer Default>
       
       :Wertebereich: <Ein gültiger Sprach-Code (de, en, fr...)>


   .. py:attribute:: committee_oguid

       :Feldname: :field-title:`Gremium`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       :Wertebereich: <OGUID eines Committees>


   .. py:attribute:: relatedItems

       :Feldname: :field-title:`Beilagen`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       


   .. py:attribute:: predecessor_proposal

       :Feldname: :field-title:`Vorgängiger Antrag`
       :Datentyp: ``RelationChoice``
       
       
       
       :Wertebereich: <UID eines Antrags>


   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       
