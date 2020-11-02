.. _dossier_from_template:

Geschäftsdossier ab Vorlage erstellen
=====================================

In einer Ordnungsposition kann über den Endpoint ``@dossier-from-template`` ein neues
Geschäftsdossier ab Vorlage erstellt werden.

Der Endpoint erwartet mindestens folgende Parameter:

- ``template``: Das zu verwendende Template aus dem Vokabular ``opengever.dossier.DossierTemplatesVocabulary``
- ``responsible``: Der Federführende des zu erstellenden Dossiers
- ``title``: Der Titel des zu erstellenden Dossiers

Zusätzlich können auch die anderen Felder des :ref:`label-dossier-schema`-Schemas gesetzt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /ordnungssystem/fuehrung/@dossier-from-template HTTP/1.1
       Accept: application/json

       {
        "template": {"token": "1234567890"},
        "description": "Dossier description"
        "responsible": "rolf.ziegler",
        "title": "Dossier title"
       }


Als Response wird die JSON-Repräsentation des neu erstellten Dossiers geliefert,
siehe :ref:`Inhaltstypen <content-types>`.
