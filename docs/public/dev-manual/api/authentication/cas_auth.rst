CAS Authentisierung via Portal
==============================

Das CAS-Protokoll ist ein Single-Sign-On Protokoll, das es erlaubt, sich via
Portal an den GEVER-Mandanten zu authentisieren.

Authentisierungs-Flow
^^^^^^^^^^^^^^^^^^^^^

Der Prozess umfasst vier Schritte:

1. Authentisieren am Portal mit Benutzername und Passwort
2. Beziehen eines CAS-Tickets vom Portal
3. Einlösen des CAS-Tickets gegen ein kurzlebiges Token (JWT) beim Service (GEVER-Mandant)
4. Verwenden des Tokens um die folgenden Requests an den Service zu authentisieren

Authentisieren am Portal
^^^^^^^^^^^^^^^^^^^^^^^^

Um ein CAS-Ticket zu beziehen, muss sich ein Client zuerst am Portal anmelden.
Dies geschieht über den ``/api/login`` Endpoint auf dem Portal:

**Login-Request**:

.. sourcecode:: http

   POST /portal/api/login HTTP/1.1
   Accept: application/json

   {
       "username": "john.doe",
       "password": "secret"
   }


**Login-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json
  Set-Cookie: csrftoken=...; sessionid=...

  {"username":"john.doe","state":"logged_in","invitation_callback":""}

Der Client ist danach über ein Session-Cookie am Portal angemeldet. Der
HTTP-Client muss dementsprechend vom Server erhaltene Cookies bei folgenden
Requests auch wieder mitschicken.

Zusätzlich zum Session-Cookie sendet das Portal auch ein CSRF-Token als
Cookie - dieses muss vom Client ausgelesen, und in folgenden Requests an das
Portal im ``X-CSRFToken`` HTTP Header mitgeschickt werden.

Der Client muss in folgenden Requests an das Portal auch den ``Referer`` HTTP
Header setzen (auf die Portal-URL), sonst wird der Request vom CSRF-Protection
Mechanismus abgelehnt.

CAS-Ticket vom Portal beziehen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Der Client kann vom Portal über den ``/api/cas/tickets`` Endpoint nun ein
CAS-Ticket für den gewünschten Service beziehen:


**Ticket-Request**:

.. sourcecode:: http

   POST /portal/api/cas/tickets HTTP/1.1
   Accept: application/json
   Referer: https://apitest.onegovgever.ch/portal
   X-CSRFToken: ypI3LgB7n7HYKMEd64KjHl3EXEye2XTN4p41AFeG9cCkwGv0kWeP8Z87Hssf3d7W

   {
     "service": "http://apitest.onegovgever.ch/"
   }


**Ticket-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "ticket": "ST-12345",
    "service": "http://apitest.onegovgever.ch/"
  }

Der Server antwortet mit einen CAS ``ticket`` im JSON-Body, welches im nächsten
Schritt vom Client bei dem Service gegen ein JWT Token eingelöst wird.


Einlösen des CAS-Tickets gegen ein JWT Token
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Der Client kann nun das erhaltene CAS-Ticket beim Service (einem GEVER-Mandanten)
über den ``@caslogin`` Endpoint gegen ein kurzlebiges JWT Token eintauschen:

**Token-Request**:

.. sourcecode:: http

   POST /@caslogin HTTP/1.1
   Accept: application/json

   {
     "ticket": "ST-12345",
     "service": "http://apitest.onegovgever.ch/"
   }


**Token-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "token": "eyJhbGciOiJI..."
  }

Dieses JWT Token kann vom Client nun für folgende Requests verwendet werden,
um die Requests direkt am Service zu authentisieren.


API-Requests an den Service mit Token authentisieren
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Für alle folgenden API-Requests an den Service authentisiert der Client diese
nun, indem er das erhaltene JWT Token als Bearer Token im ``Authorization``
HTTP Header setzt:

**API-Request**:

.. sourcecode:: http

   GET / HTTP/1.1
   Accept: application/json
   Authorization: Bearer eyJhbGciOiJI...


**API-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "https://apitest.onegovgever.ch/",
    "...": "..."
  }

Empfohlene Client-Implementierung
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die oben beschriebenen Schritte stellen den einfachen Fall dar, dass sich ein
Client genau einmal authentisieren soll.

Für einen Client, der kontinuierlich authentisierte Requests durchführen soll,
muss eine gewisse Logik implementiert werden um das Token regelmässig zu
erneuern.


Der Client sollte, statt versuchen die Ablaufzeit des Tokens vorherzusagen,
damit rechnen dass jeder Request aufgrund eines abgelaufenen Tokens scheitern
kann. In diesem Fall soll er ein neues Token beziehen, und den Request
mit dem neuen Token wiederholen.

Eine Beispiel-Implementation in Python für einen kontinuierlich
authentisierenden Client:


.. container:: collapsible

    .. container:: header

       **Beispiel-Client (Python)**

    .. literalinclude:: examples/portal-cas-example.py
