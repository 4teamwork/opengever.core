.. _templatefolder:

Dokumente ab Vorlage erstellen
==============================

In einem Dossier oder einer Aufgabe kann über den Endpoint ``@document-from-template`` ein neues
Dokument ab Vorlage erstellt werden.

Der Endpoint steht auf Dossiers und Aufgaben zur Verfügung und ist mit der
Berechtigung ``opengever.document: Add document`` geschützt. Er kann also nur verwendet
werden, wenn der Benutzer Dokumente hinzufügen kann.

Der Endpoint erwartet zwei Parameter:

- ``template``: Das zu verwendende Template aus dem Vokabular ``opengever.dossier.DocumentTemplatesVocabulary``
- ``title``: Der Titel des zu erstellenden Dokumentes


**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/dossier-23/@document-from-template HTTP/1.1
       Accept: application/json

       {
        "template": {"token": "1234567890"},
        "title": "Document title"
       }


Als Response wird die JSON-Repräsentation des neu erstellten Dokuments geliefert,
siehe :ref:`Inhaltstypen <content-types>`.
