.. _reference-numbers:

Ordnungspositionsnummer
=======================

Ordnungspositionsnummer können von Administratoren auf Stufe Ordnungssystem und Ordnungspositionen mit dem ``@reference-numbers`` Endpoint verwaltet werden.

Eine GET-Request liefert eine Liste von den Ordnungspositionsnummer, welche auf dem Kontext verwendet werden.

  .. sourcecode:: http

    GET /@reference-numbers HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    [
        {
            "active": true,
            "prefix": "1",
            "title": "Führung"
        },
        {
            "active": true,
            "prefix": "2",
            "title": "Rechnungsprüfungskommission"
        },
        {
            "active": false,
            "prefix": "3",
            "title": "Spinnännetzregistrar"
        }
    ]

DELETE erlaubt eine nicht mehr verwendete Ordnungspositionsnummer freizugeben:

  .. sourcecode:: http

    DELETE /@reference-numbers/3 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 204 No Content
    Content-Type: application/json
