.. _error_log:

Error Log
=========

Der `@error-log` Endpoint ermöglicht es, Fehlermeldungen vom Backend abzurufen.

GET
---

Ruft die Fehlermeldungen vom Backend ab.

**Request**

.. code-block:: http

  GET /@error-log HTTP/1.1
  Host: example.com
  Authorization: Bearer <JWT>

**Response**

.. code-block:: json

  {
      "items": [
          {
              "id": "error-1",
              "type": "SystemError",
              "value": "Ein unerwarteter Fehler ist aufgetreten",
              "time": "2023-06-01T12:00:00Z",
              "tb_html": "<p>...</p>",
              "req_html": "<p>...</p>",
              "userid": "john.doe"
          },
          {
              "id": "error-2",
              "type": "ValidationError",
              "value": "Ungültige Eingabedaten",
              "time": "2023-06-02T12:00:00Z",
              "tb_html": "<p>...</p>",
              "req_html": "<p>...</p>",
              "userid": "jane.doe"
          }
      ],
      "items_total": 2
  }

**Beschreibung**

Der `@error-log` Endpoint liefert eine Liste von Fehlermeldungen im JSON-Format zurück. Die Antwort enthält eine Liste von Fehlereinträgen, die jeweils aus folgenden Feldern bestehen:

- `id`: Die eindeutige Kennung der Fehlermeldung.
- `type`: Der Typ des Fehlers (z.B. `SystemError`, `ValidationError`).
- `value`: Eine kurze Beschreibung des Fehlers.
- `time`: Der Zeitpunkt, zu dem der Fehler aufgetreten ist.
- `tb_html`: Ein HTML-Format des Tracebacks, falls verfügbar.
- `req_html`: Ein HTML-Format des Requests, falls verfügbar.
- `userid`: Der Benutzer, der den Fehler verursacht hat.

**Permissions**

Weil die Logs sensitive Informationen beinhalten, steht das Error-Log nur Administratoren zur Verfügung.
