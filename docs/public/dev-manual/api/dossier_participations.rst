Beteiligungen
=============

Der ``@participations`` Endpoint behandelt Dossierbeteiligungen.


Auflistung
----------

Ein Beteiligter kann in verschiedenen Rollen an einem Dossier beteiligt sein. Mittels eines GET-Requests können alle Beteiligten eines Dossiers und ihre Rollen abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /dossier-1/@participations HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json


      {
        "@id": "https://example.org/ordnungssystem/fuehrung/dossier-1/@participations",
        "available_roles": [
          {
            "title": "Kenntnisnahme",
            "token": "regard"
          },
          {
            "title": "Mitwirkung",
            "token": "participation"
          },
          {
            "title": "Schlusszeichnung",
            "token": "final-drawing"
          }
        ],
        "items": [
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-1/@participations/rolf.ziegler",
            "participant_id": "rolf.ziegler",
            "participant_title": "Ziegler Rolf (rolf.ziegler)",
            "roles": [
              "regard",
              "participation"
            ]
          },
          {
            "@id": "https://example.org/ordnungssystem/fuehrung/dossier-1/@participations/contact:james-bond",
            "participant_id": "contact:james-bond",
            "participant_title": "Bond James (james@example.com)",
            "roles": [
              "final-drawing"
            ]
          }
        ],
        "items_total": 2
      }


Beteiligungen als erweiterbare Komponente
-----------------------------------------

Die Beteilgungen können als Kompomente eines Dossiers direkt über den ``expand``-Parameter eingebettet werden, so dass keine zusätzliche Abfrage nötig ist.

**Beispiel-Request**:

  .. sourcecode:: http

    GET /dossier-1?expand=participations HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "https://example.org/ordnungssystem/fuehrung/dossier-1?expand=participations",
      "@components": {
        "participations": {
          "@id": "https://example.org/ordnungssystem/fuehrung/dossier-1/@participations",
          "available_roles": ["..."],
          "items": ["..."],
          "items_total": 2
        }
      },
      "...": "..."
    }


Beteiligung hinzufügen
----------------------

Eine Beteiligung kann mittels POST-Requests hinzugefügt werden.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/@participations HTTP/1.1
       Accept: application/json

       {
         "participant_id": "peter.mueller"
         "roles": ["regard"]
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Rollen einer Beteiligung bearbeiten
-----------------------------------

Rollen einer Beteiligung können mittels PATCH-Requests bearbeitet werden.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/@participations/rolf.ziegler HTTP/1.1
       Accept: application/json

       {
         "roles": ["regard", "final-drawing"]
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Beteiligung entfernen
---------------------

Mittels DELETE-Requests kann eine Beteiligung wieder entfernt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /dossier-1/@participations/rolf.ziegler HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).
