.. py:class:: opengever.task.task

    Inhaltstyp 'Aufgabe'



   .. py:attribute:: title

       :Feldname: :field-title:`Titel`
       :Datentyp: ``TextLine``
       :Pflichtfeld: Ja :required:`(*)`
       
       :Beschreibung: Der Name der Aufgabe
       


   .. py:attribute:: issuer

       :Feldname: :field-title:`Auftraggeber`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       
       :Wertebereich: <User-ID eines gültigen Auftraggebers>


   .. py:attribute:: task_type

       :Feldname: :field-title:`Auftragstyp`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       :Beschreibung: Wählen Sie den Auftragstyp
       :Wertebereich: ["approval", "comment", "correction", "direct-execution", "information", "report"]


   .. py:attribute:: responsible_client

       :Feldname: :field-title:`Mandant des Auftragnehmers`
       :Datentyp: ``Choice``
       
       :Default: <Kein Default> :small-comment:`(Obwohl dieses Feld im User-Interface nicht erscheint (vom System automatisch gesetzt wird), muss es über die REST API angegeben werden)`
       :Beschreibung: Wählen Sie zuerst den Mandanten des Auftragnehmers, anschliessend den Auftragnehmer.
       :Wertebereich: <Gültige Org-Unit-ID>


   .. py:attribute:: responsible

       :Feldname: :field-title:`Auftragnehmer`
       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`
       
       :Beschreibung: Wählen Sie die verantwortlichen Personen aus.
       :Wertebereich: <User-ID eines gültigen Auftragnehmers>


   .. py:attribute:: informed_principals

       :Feldname: :field-title:`Info an`
       :Datentyp: ``List``
       
       :Default: []
       :Beschreibung: Die ausgewählten Benutzer und Gruppen werden über die Erstellung dieser Aufgabe benachrichtigt.
       


   .. py:attribute:: is_private

       :Feldname: :field-title:`Persönliche Aufgabe`
       :Datentyp: ``Bool``
       
       :Default: false
       :Beschreibung: Eingangskorb-Stellvertreter Berechtigung für diese Aufgabe deaktivieren
       


   .. py:attribute:: revoke_permissions

       :Feldname: :field-title:`Berechtigungen nach Abschluss entziehen`
       :Datentyp: ``Bool``
       
       :Default: true
       :Beschreibung: Berechtigungen für den Auftragnehmer und dessen Stellvertretung nach Abschluss oder Neuzuweisung der Aufgabe entziehen.
       


   .. py:attribute:: deadline

       :Feldname: :field-title:`Zu erledigen bis`
       :Datentyp: ``Date``
       
       :Default: <Aktuelles Datum + 5 Tage> :small-comment:`(konfigurierbarer Default)`
       :Beschreibung: Tragen Sie ein Datum ein, bis wann die Aufgabe erledigt werden muss
       


   .. py:attribute:: date_of_completion

       :Feldname: :field-title:`Erledigungsdatum`
       :Datentyp: ``Date``
       
       
       :Beschreibung: Das Datum an dem die Aufgabe beendet wurde
       


   .. py:attribute:: text

       :Feldname: :field-title:`Beschreibung`
       :Datentyp: ``Text``
       
       
       :Beschreibung: Geben Sie eine detaillierte Arbeitsanweisung oder einen Kommentar ein
       


   .. py:attribute:: relatedItems

       :Feldname: :field-title:`Verweise`
       :Datentyp: ``RelationList``
       
       :Default: []
       
       


   .. py:attribute:: expectedStartOfWork

       :Feldname: :field-title:`Beginn der Arbeit`
       :Datentyp: ``Date``
       
       
       
       


   .. py:attribute:: expectedDuration

       :Feldname: :field-title:`Geschätzte Dauer (h)`
       :Datentyp: ``Float``
       
       
       :Beschreibung: Dauer in h
       


   .. py:attribute:: expectedCost

       :Feldname: :field-title:`Geschätzte Kosten (CHF)`
       :Datentyp: ``Float``
       
       
       :Beschreibung: Kosten in CHF
       


   .. py:attribute:: effectiveDuration

       :Feldname: :field-title:`Effektive Dauer (h)`
       :Datentyp: ``Float``
       
       
       :Beschreibung: Dauer in h
       


   .. py:attribute:: effectiveCost

       :Feldname: :field-title:`Effektive Kosten (CHF)`
       :Datentyp: ``Float``
       
       
       :Beschreibung: Kosten in CHF
       


   .. py:attribute:: predecessor

       :Feldname: :field-title:`Vorgänger`
       :Datentyp: ``TextLine``
       
       
       
       


   .. py:attribute:: changed

       :Feldname: :field-title:`Zuletzt verändert`
       :Datentyp: ``Datetime``
       
       
       
       
