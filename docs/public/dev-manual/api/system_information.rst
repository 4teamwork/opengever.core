.. _system_information:

System Informationen
====================

Über den ``/@system_information`` Endpoint können Informationen über das System abgeholt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@system_information HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "...": "..."
      }
