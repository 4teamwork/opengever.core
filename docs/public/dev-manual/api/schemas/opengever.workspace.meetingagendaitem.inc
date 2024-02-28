.. py:class:: opengever.workspace.meetingagendaitem

    Inhaltstyp 'Traktandum'



   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       


   .. py:attribute:: text

       :Feldname: :field-title:`Text`
       :Datentyp: ``RichText``
       
       
       
       


   .. py:attribute:: decision

       :Feldname: :field-title:`Beschluss`
       :Datentyp: ``RichText``
       
       
       
       


   .. py:attribute:: relatedItems

       :Feldname: :field-title:`Verweise`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       


   .. py:attribute:: related_todo_list

       :Feldname: :field-title:`Verknüpfte To-do-Liste`
       :Datentyp: ``RelationChoice``
       
       
       
       :Wertebereich: <UID einer verknüpften To-do-Liste


   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       
