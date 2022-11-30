.. _operations:

Operationen
============

Die möglichen Operationen auf der API sind auf HTTP Verben gemappt.


======= ============ ==========================================================
Verb    URL          Operation
======= ============ ==========================================================
GET     /{path}      Gibt die Attribute eines Objekts zurück
POST    /{container} Erstellt ein neues Objekt in dem entsprechenden Container
PATCH   /{path}      Aktualisiert einzelne Attribute eines Objekts
======= ============ ==========================================================


.. _content-get:

Inhalte lesen (GET)
-------------------

Mit einem ``GET`` Request auf die URL eines Objekts können die Daten
(Metadaten wie auch Primärdaten) eines Objekts ausgelesen werden.

Im Fall eines Objekts das "folderish" ist (ein Container), gibt es ein
spezielles Attribut ``items``, welches eine
:ref:`summarische Auflistung <summaries>` der Unterobjekte enthält (direkte
children des Objekts).


.. http:get:: /(path)

   Liefert die Attribute des Objekts unter `path` zurück

   **Beispiel-Request**:

   .. sourcecode:: http

      GET /ordnungssystem/fuehrung/dossier-23 HTTP/1.1
      Accept: application/json

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23",
        "@type": "opengever.dossier.businesscasedossier",
        "UID": "66395be6595b4db29a3282749ed50302",
        "archival_value": "not archival worthy",
        "archival_value_annotation": null,
        "classification": "unprotected",
        "container_location": null,
        "container_type": null,
        "created": "2016-01-08T10:51:40+00:00",
        "custody_period": 30,
        "date_of_cassation": null,
        "date_of_submission": null,
        "description": "",
        "end": null,
        "filing_prefix": null,
        "former_reference_number": null,
        "keywords": [],
        "items": [
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/document-259",
            "@type": "opengever.document.document",
            "description": null,
            "is_subdossier": null,
            "title": "Ein Dokument"
          },
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/document-260",
            "@type": "opengever.document.document",
            "description": null,
            "is_subdossier": null,
            "title": "Ein weiteres Dokument"
          }
        ],
        "modified": "2016-01-19T11:15:22+00:00",
        "number_of_containers": null,
        "oguid": "fd:12345",
        "parent": {
          "@id": "https://example.org/ordnungssystem/fuehrung",
          "@type": "opengever.repository.repositoryfolder",
          "description": null,
          "title": "Führung"
        },
        "privacy_layer": "privacy_layer_no",
        "public_trial": "unchecked",
        "public_trial_statement": null,
        "reference_number": null,
        "relatedDossier": null,
        "responsible": "john.doe",
        "retention_period": 5,
        "retention_period_annotation": null,
        "review_state": "dossier-state-active",
        "start": "2016-01-08",
        "temporary_former_reference_number": null,
        "title": "Ein Geschäftsdossier"
      }

.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_get.py


Erweiterbare Komponente (Expansion)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Eine erweiterbare Komponente (auch "Expansion" genannt) ist ein Mechanismus, um in einem GET-Request
einer Ressource weitere Information anzufordern, z.B. die Navigation, Breadcrumbs, etc. Damit kann verhindert
werden, dass ein weiterer Request abgesetzt werden muss, um diese Angaben abzuholen. Weitere Informationen
zu diesem Mechanismus findet man unter https://plonerestapi.readthedocs.io/en/latest/expansion.html.

Die erweiterbaren Komponenten können über den Parameter `expand` in die Response eingebettet werden.

Folgende erweiterbaren Komponente stehen zur Verfügung und sind in den entsprechenden Kapiteln beschrieben:

- :ref:`navigation`
- :ref:`breadcrumbs`
- :ref:`listing_stats`

Eine weitere erweiterbare Komponente erlaubt es, Informationen zum *Hautpdossier* einer Ressource
abzufragen.

**Beispiel-Request**:

.. sourcecode:: http

  GET /ordnungssystem/dossier/subdossier/document?expand=main-dossier HTTP/1.1
  Accept: application/json

**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 200 OK

   {
     "@components": {
       "main-dossier": {
         "@id": "https://example.org/ordnungssystem/dossier",
         "@type": "opengever.dossier.businesscasedossier",
         "description": "",
         "is_leafnode": null,
         "is_subdossier": false,
         "review_state": "dossier-state-active",
         "title": "Gesetzesentwürfe"
       },
     },
     "@id": "https://example.org/ordnungssystem/dossier/subdossier/document?expand=main-dossier",
     "..."
   }

Falls die Frage, welches das Hauptdossier einer Ressource ist, nicht beantwortet werden kann, dann
ist der Wert in der Response nicht definiert.

**Beispiel-Request**:

.. sourcecode:: http

   GET /ordnungssystem?expand=main-dossier HTTP/1.1
   Accept: application/json

**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 200 OK

   {
     "@components": {
       "main-dossier": null,
     },
     "@id": "https://example.org/ordnungssystem?expand=main-dossier",
     "..."
   }


.. _content-post:

Inhalte erstellen (POST)
------------------------

Um ein neues Objekt zu erstellen, muss ein ``POST`` Request auf den Container,
der das Objekt enthalten soll, gemacht werden. Die ID des erstellten Objekts
(z.B. 'document-26') wird vom System selbst mitbestimmt und muss nicht
mitgegeben werden.


.. http:post:: /(container)

   Erstellt ein neues Objekt innerhalb von `container`.

   **Beispiel-Request**:

   .. sourcecode:: http

      POST /ordnungssystem/fuehrung HTTP/1.1
      Accept: application/json

      {
        "@type": "opengever.dossier.businesscasedossier",
        "title": "Ein neues Geschäftsdossier",
        "responsible": "john.doe",
        "custody_period": 30,
        "archival_value": "unchecked",
        "retention_period": 5
      }

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: https://example.org/ordnungssystem/fuehrung/dossier-24

      null

Im ``Location`` Header der Response ist die URL des neu erstellen Objekts zu
finden.

.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_post.py


.. _content-patch:

Inhalte bearbeiten (PATCH)
--------------------------

Um ein oder mehrere Attribute eines Objekts zu aktualisieren, wird ein
``PATCH`` Request verwendet.


.. http:patch:: /(path)

   Aktualisiert ein oder mehrere Attribute des Objekts unter `path`.

   **Beispiel-Request**:

   .. sourcecode:: http

      PATCH /ordnungssystem/fuehrung/dossier-24 HTTP/1.1
      Accept: application/json

      {
        "title": "Ein umbenanntes Dossier"
      }

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null

.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_patch.py


.. _content-delete:

Inhalte löschen (DELETE)
------------------------

Um ein Objekt zu löschen, wird ein ``DELETE`` Request verwendet. Dies ist grundsätzlich
in GEVER verboten und in teamraum erlaubt.


.. http:delete:: /(path)

   Löscht das Objekt unter `path`.

   **Beispiel-Request**:

   .. sourcecode:: http

      DELETE /workspaces/workspace-1/document-24 HTTP/1.1
      Accept: application/json

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null

.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_delete.py
