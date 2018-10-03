.. _reminders:

Aufgaben-Erinnerungen
=====================

Der ``@reminder`` Endpoint behandelt Erinnerungen für Aufgabe. Jeder Benutzer kann für jede Aufgabe eine eigene Erinnerung setzten.


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
