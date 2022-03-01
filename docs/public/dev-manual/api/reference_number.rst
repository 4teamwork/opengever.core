.. _reference_number:

Aktenzeichen
============

Über den ``@reference-number`` Endpoint kann Details über das Aktenzeichen und seine Komponenten eines beliebigen Inhalts abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/@reference-number",
        "parts": {
            "document": ["14"],
            "dossier": ["1"],
            "repository": ["1", "1"],
            "repositoryroot": [""],
            "site": ["Client1"],
        },
        "reference_number": "Client1 1.1 / 1 / 14",
        "sortable_reference_number": "client00000001 00000001.00000001 / 00000001 / 00000014"
      }


Das Aktenzeichen kann beim Abfragen eines Inhaltes über den ``expand``-Parameter eingebettet werden,
so dass keine zusätzliche Abfrage nötig ist.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem?expand=reference-number HTTP/1.1
       Accept: application/json
