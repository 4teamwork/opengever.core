.. _config_checks:

Konfigurations Checks
=====================

Über den ``/@config-checks`` Endpoint können Manager überprüfen, ob das Deployment korrekt konfiguriert ist.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@config-checks HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/@config-checks",
          "errors": []
      }
