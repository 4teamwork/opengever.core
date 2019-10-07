.. _reminders:

Aufgaben-Erinnerungen
=====================

Der ``@reminder`` Endpoint behandelt Erinnerungen für Aufgabe. Jeder Benutzer kann für jede Aufgabe eine eigene Erinnerung setzten.


Erinnerung auslesen:
--------------------
Mit einem GET Request kann eine bestehende Erinnerung für den aktuellen Benutzer ausgelesen werden:


**Beispiel-Request**:

   .. sourcecode:: http

       GET /task-1/@reminder HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK

       {
        "@id": "http://example.onegovgever.ch/ordnungssystem/dossier-20/task-1/@reminder",
        "option_type": "one_day_before",
        "params": {}
       }

Falls für den aktuellen Benutzer keine Erinnerung gesetzt ist, antwortet der Endpoint mit 404 Not Found:

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found

       {
          "message": "Resource not found: http://example.onegovgever.ch/ordnungssystem/dossier-20/task-1/@reminder",
          "type": "NotFound"
       }

Erinnerung setzten:
-------------------
Mit einem POST Request wird eine neue Erinnerung gesetzt. Als Body wird das Attribut ``option_type`` erwartet.
Wenn das Attribut einen Wert enthält, welcher nicht zulässig ist, wird eine Liste mit gültigen Werten zurückgegeben.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "one_day_before"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Für gewisse Reminder-Typen sind zusätzliche Parameter erforderlich. Diese
können der entsprechenden Reminder-Subklasse entnommen werden. Parameter
werden als Dictionary im 'params' property angegeben:

**Beispiel-Request**:

   .. sourcecode:: http

       POST /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "on_date",
        "params": {
            "date": "2019-12-30"
           }
       }


Erinnerung aktualisieren:
-------------------------
Eine bestehende Erinnerung kann durch einen PATCH Request aktualisiert werden.


**Beispiel-Request**:

   .. sourcecode:: http

       PATCH /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "same_day"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Erinnerung entfernen:
---------------------
Eine bestehende Erinnerung kann durch einen DELETE Request gelöscht werden:


**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /task-1/@reminder HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
