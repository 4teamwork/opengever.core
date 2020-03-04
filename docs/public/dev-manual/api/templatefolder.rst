.. _templatefolder:

Dokumente ab Vorlage erstellen
==============================

In einem Dosser kann über den Endpoint ``@document-from-template`` ein neues
Dokument ab Vorlage erstellt werden.

Der Endpoint steht auf einem Dossier zur Verfügung. Der Endpoint ist mit der
Berechtigung ``opengever.document: Add document`` geschützt, kann also verwendet
werden wenn der Benutzer Dokumente hinzufügen kann.

Der Endpoint erwartet zwei Parameter:

- ``template`` das zu verwendende template aus dem Vokabular ``opengever.dossier.DocumentTemplatesVocabulary``
- ``title`` Titel des zu erstellenden Dokumentes


**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/dossier-23/@document-from-template HTTP/1.1
       Accept: application/json

       {
        "template": {"token": "1234567890"},
        "title": "Document title"
       }


Als Reponse wird die JSON-Repräsentation des neu erstellen Dokuments geliefert,
siehe :ref:`Inhaltstypen <content-types>`.
