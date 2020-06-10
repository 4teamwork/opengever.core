.. listing_stats:

Statistik zu Auflistungen
=========================

Mit dem ``@listing-stats`` Endpoint können Statistiken zu Auflistungen unter :ref:`listings` abgefragt werden. Spezifische Statistiken können mit dem ``queries`` Parameter abgefragt werden.


**Beispiel-Request**:

  .. sourcecode:: http

    GET /dossier-1/@listing-stats HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/dossier-1/@listing-stats",
      "facet_pivot": {
        "listing_name": [
          {
            "field": "listing_name",
            "value": "dossiers",
            "count": 10
          },
          {
            "field": "listing_name",
            "value": "documents",
            "count": 5
          },
          {
            "field": "listing_name",
            "value": "proposals",
            "count": 0
          },
          "..."
        ]
      }
    }


**Beispiel-Request mit queries**:

  .. sourcecode:: http

    GET /dossier-1/@listing-stats?queries=responsible:hugo.boss&queries=depth:1 HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/dossier-1/@listing-stats",
      "facet_pivot": {
        "listing_name": [
          {
            "field": "listing_name",
            "value": "dossiers",
            "count": 10,
            "queries": {"responsible:hugo.boss": 1,
                        "depth:1": 4}
          },
          {
            "field": "listing_name",
            "value": "documents",
            "count": 5,
            "queries": {"responsible:hugo.boss": 0,
                        "depth:1": 2}
          },
          "..."
        ]
      }
    }



Statistik als erweiterbare Komponente
-------------------------------------
Die Statistiken können als Kompomente einer Ressource direkt über den ``expand``-Parameter eingebettet werden.

**Beispiel-Request**:

  .. sourcecode:: http

    GET /dossier-1?expand=listing-stats HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/dossier-1?expand=listing-stats",
      "@components": {
        "listingstats": {
          "@id": "http://localhost:8080/fd/ordnungssystem/dossier-1/@listing-stats",
          "facet_pivot": { "...": "..." }
        }
      },
      "...": "..."
    }
