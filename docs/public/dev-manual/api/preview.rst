.. _preview:

Vorschau
========

Für das Herunterladen von Vorschaubildern und -dokumenten wird ein Cookie benötigt.
Dieses kann mit dem ``@preview-session`` Endpoint erstellt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /@preview-session HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 OK
      Set-Cookie: bumblebee-gever_dev="eyJzYWx0IjogImE1MDAxMzZkNDZkYzRiZDc5ZDI2ZjdlNzVhM2UyNGUzIn0%3D--28011d89ecc6f79149b57f9e3c91505ad33cc0b9"; Path=/
