.. _substitutes:

Stellvertreter
==============

Mit dem ``@my-substitutes`` Endpoint können für den aktuellen Benutzer Stellvertreter aufgelistet, hinzugefügt und gelöscht werden. Mit dem ``@substitutes`` Endpoint  können für einen beliebigen Benutzer Stellvertreter aufgelistet werden. Die Endpoints stehen nur auf Stufe PloneSite zur Verfügung.


Eigene Stellvertreter auflisten:
--------------------------------
Mittels eines GET Request können Stellvertretungen des aktuellen Benutzers abgefragt werden. Es werden alle, also global über den ganzen Mandanten-Verbund, zurückgegeben.


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@my-substitutes HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8081/fd/@my-substitutes",
          "items": [
              {
                  "@id": "http://localhost:8081/fd/@my-substitutes/peter.mueller",
                  "@type": "virtual.ogds.substitute",
                  "substitution_id": 3,
                  "substitute_userid": "peter.mueller",
                  "userid": "kathi.barfuss"
              },
              {
                  "@id": "http://localhost:8081/fd/@my-substitutes/nicole.kohler",
                  "@type": "virtual.ogds.substitute",
                  "substitution_id": 3,
                  "substitute_userid": "nicole.kohler",
                  "userid": "kathi.barfuss"
              },
          ],
          "items_total": 2
      }

Stellvertreter eines Benutzers auflisten:
-----------------------------------------
Mittels eines GET Request können Stellvertretungen eines Benutzers abgefragt werden. Dabei wird die User-ID des Benutzers als Pfad-Parameter erwartet. Es werden alle, also global über den ganzen Mandanten-Verbund, zurückgegeben.



**Beispiel-Request**:

   .. sourcecode:: http

       GET /@substitutes/kathi.barfuss HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8081/fd/@substitutes/kathi.barfuss",
          "items": [
              {
                  "@id": "http://localhost:8081/fd/@substitutes/peter.mueller",
                  "@type": "virtual.ogds.substitute",
                  "substitution_id": 3,
                  "substitute_userid": "peter.mueller",
                  "userid": "kathi.barfuss"
              },
              {
                  "@id": "http://localhost:8081/fd/@substitutes/nicole.kohler",
                  "@type": "virtual.ogds.substitute",
                  "substitution_id": 3,
                  "substitute_userid": "nicole.kohler",
                  "userid": "kathi.barfuss"
              },
          ],
          "items_total": 2
      }


Stellvertretung hinzufügen:
---------------------------
Eine Stellvertretung des aktuellen Benutzers kann mittels POST Request hinzugefügt werden. Dabei wird die User-ID als Parameter erwartet.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /@my-substitutes HTTP/1.1
       Accept: application/json

       {
        "userid": "peter.mueller"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Stellvertretung entfernen:
--------------------------
Eine bestehende Stellvertretung des aktuelllen Benutzers kann mittels DELETE Request wieder gelöscht werden. Als Pfad-Parameter wird die User-ID der Stellvertretung erwartet.


**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /@my-substitutes/peter.mueller HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
