.. _out-of-office:

Abwesenheit
===========

Mit dem ``@out-of-office`` Endpoint können für den aktuellen Benutzer eine Abwesenheit angezeigt und angepasst werden. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung.


Abwesenheit anzeigen:
---------------------
Mittels eines GET Request kann die Abwesenheit des aktuellen Benutzers angezeigt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@out-of-office HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8081/fd/@out-of-office",
          "absent": true,
          "absent_from": "2021-12-08",
          "absent_to": "2021-12-15"
      }


Abwesenheit editieren:
----------------------
Die Abwesenheit des aktuellen Benutzers kann mittels PATCH Request editiert werden.

**Beispiel-Request**:

   .. sourcecode:: http

       PATCH /@out-of-office HTTP/1.1
       Accept: application/json

       {
        "absent_to": "2021-12-22"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Gleich wie bei anderen PATCH Requests ist es auch hier möglich, die Repräsentation als Response zu erhalten, hierzu muss ein ``Prefer`` Header mit dem Wert ``return=representation`` gesetzt werden.
