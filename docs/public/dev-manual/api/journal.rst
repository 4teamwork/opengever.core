.. _journal:

Journal-Einträge
================

Der ``@journal`` Endpoint behandelt Journaleinträge.

Achtung: Ein nachträgliches Bearbeiten von bestehenden Journaleinträgen ist nicht möglich.


Journaleintrag hinzufügen:
--------------------------
Mit einem POST Request wird ein neuer Journaleintrag erzeugt. Im Body wird das Attribut ``comment`` erwartet.

**Parameter:**

Pflicht:

``comment``: ``String``
   Titel des Journaleintrages.

Optional:

``category``: ``String``
   Journal-Kategory. Mögliche Werte können über den endpoint `@vocabularies/opengever.journal.manual_entry_categories` abgeholt werden.

``related_documents``: ``String[]``
   URLs zu Gever-Dokumenten


**Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/@journal HTTP/1.1
       Accept: application/json

       {
         "comment": "Dossier mit externem Tool archiviert",
         "category": "phone-call",
         "related_documents": [
           "http://localhost:8080/fd/ordnungssystem/fuehrung/kommunikation/allgemeines/dossier-1/document-1",
           "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-14/document-33"
         ]
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content
