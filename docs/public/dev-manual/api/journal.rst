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

``category``: ``String`` or ``dict with token``
   Journal-Kategory. Mögliche Werte können über den endpoint `@vocabularies/opengever.journal.manual_entry_categories` abgeholt werden.

``related_documents``: ``String[]``
   URLs zu Gever-Dokumenten

``time``: ``DateTime String``
   Zum Beispiel "2022-07-13T17:28:44+00:00"

**Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/@journal HTTP/1.1
       Accept: application/json

       {
         "comment": "Dossier mit externem Tool archiviert",
         "category": { "token": "phone-call" },
         "related_documents": [
           "http://localhost:8080/fd/ordnungssystem/fuehrung/kommunikation/allgemeines/dossier-1/document-1",
           "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-14/document-33"
         ],
         "time": "2022-07-13T17:28:44+00:00"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Journaleinträge abrufen:
------------------------
Ein GET Request gibt die Journaleinträge eines Inhalts zurück.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /dossier-1/@journal HTTP/1.1
       Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "items": [
        {
          "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-1/@journal/123"
          "id": "123"
          "is_editable": true,
          "actor_fullname": "zopemaster",
          "actor_id": "zopemaster",
          "comment": "Ich bin ein neuer Journaleintrag",
          "category": { "token": "information", "title": "Information" }
          "related_documents": [
            {
              "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-1/document-1",
              "@type": "opengever.document.document",
              "UID": "c99df05a4bbe473ead5e2356f5a4f8b4",
              "checked_out": "robert.ziegler",
              "description": "",
              "file_extension": ".docx"
              "is_leafnode": null,
              "review_state": "document-state-draft",
              "title": "Ein Dokument"
            }
          ],
          "time": "2019-04-15T14:00:48+00:00",
          "title": "Telefongespräch"
        },
        {
          "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-1/@journal/456"
          "id": "456"
          "is_editable": true,
          "actor_fullname": "zopemaster",
          "actor_id": "zopemaster",
          "comment": "Ich bin ein neuer Journaleintrag",
          "category": { "token": "information", "title": "Information" }
          "related_documents": [],
          "time": "2019-04-15T13:59:21+00:00",
          "title": "Telefongespräch"
        }
      ],
      "items_total": 2
    }


.. note::
        Suchresultate werden **paginiert** wenn die Anzahl Resultate die
        voreingestellte Seitengrösse (default: 25) überschreitet. Siehe
        :doc:`batching` zu Details zum Umgang mit paginierten Resultaten.


Optionale Parameter:
--------------------

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente
- ``search``: Filterung nach einem beliebigen Suchbegriff im Titel oder Kommentar
- ``filters``: Einschränkung nach einem bestimmten Wert eines Feldes


**Beispiel: Filtern nach Journal-Kategorie:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@journal?filters.categories:record:list=phone-call HTTP/1.1
    Accept: application/json


**Beispiel: Filtern nach manuellen Journal-Einträgen:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@journal?filters.manual_entries_only:record:boolean=True HTTP/1.1
    Accept: application/json


**Beispiel: Suchen nach Einträgen mit einem Suchbegriff:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@journal?search=Important HTTP/1.1
    Accept: application/json


Manuelle Journaleinträge entfernen:
-----------------------------------
Ein bestehender manueller Journaleintrag kann mittels DELETE Request auf die entsprechender URL gelöscht werden.

Die URL setzt sich dabei folgendermassen zusammen:
``context-url/@journal/{journal-id}``


**Beispiel-Request**:

  .. sourcecode:: http

    DELETE /ordnungssystem/fuehrung/dossier-23/@journal/20 HTTP/1.1
    Accept: application/json


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 204 No Content


Manuelle Journaleinträge bearbeiten:
------------------------------------
Ein bestehender manueller Journaleintrag kann mittels PATCH Request auf die entsprechender URL bearbeitet werden.

**Beispiel-Request**:

  .. sourcecode:: http

    PATCH /ordnungssystem/fuehrung/dossier-23/@journal/20 HTTP/1.1
    Accept: application/json

    {
        "category": "phone-call",
        "comment": "My updated comment"
    }


**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 204 No Content
