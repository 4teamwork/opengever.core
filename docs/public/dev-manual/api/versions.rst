Versionen
=========

Der ``@versions`` Endpoint liefert ähnliche Information wie der ``@history`` Endpoint (siehe `plone.restapi Dokumentation <https://plonerestapi.readthedocs.io/en/latest/history.html>`_.) aber eingeschränkt nur auf Versionen, ohne historische Statusveränderunginformationen. Dieser Endpoint is performanter als der ``@history`` Endpoint.

Versionen Auflistung:
---------------------
Mittels eines GET Request können die Versionen eines Dokuments aufgelistet werden. Dieser Endpoint ist paginiert.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem/dossier-23/document-123/@versions HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/dossier-23/document-123/@versions",
        "items": [
            {
                "@id": "http://example.org/ordnungssystem/dossier-23/document-123/@versions/2",
                "actor": {
                    "@id": "http://example.org/ordnungssystem/@actors/niklaus.johner",
                    "identifier": "niklaus.johner",
                },
                "comments": "",
                "may_revert": true,
                "time": "2021-04-14T11:31:10.205146",
                "version": 2
            },
            {
                "@id": "http://example.org/ordnungssystem/dossier-23/document-123/@versions/1",
                "...": "..."
            }
        ],
        "items_total": 3
      }


Spezifische Version:
--------------------

Die Daten einer spezifischen Version können mit der Versionsnummer als zusätzliches Pfad-Argument abgefragt werden:

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem/dossier-23/document-123/@versions/1 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "/ordnungssystem/dossier-23/document-123",
        "@type": "opengever.document.document",
        "UID": "cf8bcd04db1443e7a83bee77ff169476",
        "current_version_id": 2,
        "version": "1",
        "...": "..."
      }
