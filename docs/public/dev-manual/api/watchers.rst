Beobachter
==========

Der ``@watchers`` Endpoint dient dazu, für Aufgaben und Weiterleitungen Beobachter zu registrieren.


Auflistung
----------

Ein Beobachter kann verschiedene Rollen haben, beispielsweise die Rollen Auftraggeber (``task_issuer``), Auftragnehmer (``task_responsible``) oder Beobachter (``regular_watcher``). Mittels eines GET-Requests können alle Beobachter und alle Rollen einer Aufgabe abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /task-1/@watchers HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/task-1/@watchers",
        "referenced_users": [
          {
            "@id": "https://example.org/@users/peter.mueller",
            "id": "peter.mueller",
            "fullname": "Mueller Peter"
          },
          {
            "@id": "https://example.org/@users/rolf.ziegler",
            "id": "rolf.ziegler",
            "fullname": "Ziegler Rolf"
          }
        ],
        "referenced_watcher_roles": [
          {
            "id": "regular_watcher",
            "title": "Beobachter"
          },
          {
            "id": "task_issuer",
            "title": "Auftraggeber"
          },
          {
            "id": "task_responsible",
            "title": "Auftragnehmer"
          },
        ],
        "watchers_and_roles": {
          "peter.mueller": [
            "task_issuer"
          ],
          "rolf.ziegler": [
            "regular_watcher",
            "task_responsible"
          ]
        }
      }


Beobachter als erweiterbare Komponente
--------------------------------------

Die Beobachter können als Kompomente einer Aufgabe direkt über den ``expand``-Parameter eingebettet werden, so dass keine zusätzliche Abfrage nötig ist.

**Beispiel-Request**:

  .. sourcecode:: http

    GET /task-1?expand=watchers HTTP/1.1
    Accept: application/json

**Beispiel-Response**:

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/task-1?expand=watchers",
      "@components": {
        "watchers": {
          "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23/task-1/@listing-stats",
          "referenced_users": ["..."],
          "referenced_watcher_roles": ["..."],
          "watchers_and_roles": { "...": "..." }
        }
      },
      "...": "..."
    }


Beobachter hinzufügen
---------------------

Ein Benutzer kann mittels POST-Requests als Beobachter mit der Rolle ``regular_watcher`` bei einer Aufgabe registriert werden.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /task-1/@watchers HTTP/1.1
       Accept: application/json

       {
         "userid": "peter.mueller"
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Beobachter entfernen
--------------------

Mittels DELETE-Requests kann die Rolle ``regular_watcher`` eines Beobachters von einer Aufgabe wieder entfernt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /task-1/@watchers HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Liste von möglichen Beobachtern
-------------------------------
Der ``@possible-watchers``-Endpoint liefert eine Liste von Benutzern welche als Beobachter für den aktuellen Kontext hinzugefügt werden können.

Weil es üblich ist, dass man sich selbst als Beobachter hinzufügen möchte, wird der eigene Benutzer in der Sortierreihenfolge immer zuoberst dargestellt. Alle restlichen Benutzer werden nach Name und Vorname sortiert. Der eigene Benutzer sowie alle anderen Benutzer werden nur dann angezeigt, wenn diese noch keine Beobachter-Rolle besitzen.

**Beispiel-Request:**


  .. sourcecode:: http

    GET /task-1/@possible-watchers HTTP/1.1
    Accept: application/json


**Beispiel-Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "/task-1/@possible-watchers",
        "items": [
          {
            "title": "Mueller Peter (peter.mueller)",
            "token": "peter.mueller"
          },
          {
            "title": "Ziegler Rolf (rolf.ziegler)",
            "token": "rolf.ziegler"
          },
          { "...": "..." },
        ],
        "items_total": 17
      }

Resultate filtern
~~~~~~~~~~~~~~~~~
Mit dem ``query``-Parameter können die Resultate gefiltert werden. Es werden die Felder:

- Vorname
- Nachname
- E-Mail
- Userid

beim filtern berücksichtigt.

**Beispiel-Request:**


  .. sourcecode:: http

    GET /task-1/@possible-watchers?query=Peter HTTP/1.1
    Accept: application/json


**Beispiel-Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "/task-1/@possible-watchers",
        "items": [
          {
            "title": "Mueller Peter (peter.mueller)",
            "token": "peter.mueller"
          }
        ],
        "items_total": 1
      }

Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).
