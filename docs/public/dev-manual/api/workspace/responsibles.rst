.. _workspace_responsible:

Teamraum Besitzer
=================

Der Besitzer eines Teamraums ist standardmässig der Benutzer, welcher den Teamraum erstellt hat.

Besitzer ändern
---------------

Ein Benutzer kann mittels POST-Requests als neuer Besitzer eines Teamraums festgelegt werden.

**Beispiel-Request**:

.. sourcecode:: http

   POST /workspaces/workspace/@change-responsible HTTP/1.1
   Accept: application/json

   {
     "userid": "peter.mueller"
   }

**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 204 No content

Nur Administratoren eines Teamraums können den Besitzer eines Teamraums ändern.

Liste von möglichen Besitzern
-----------------------------

Der ``@possible-responsibles``-Endpoint liefert eine Liste von Benutzern, welche als Besitzer für Teamräume innerhalb
aktuellen Kontextes ausgewählt werden dürfen. Dies umfasst alle Teilnehmer des Teamraums.

Die Einträge werden nach Name und Vorname sortiert.

**Beispiel-Request:**

.. sourcecode:: http

   GET /workspaces/workspace/@possible-responsibles HTTP/1.1
   Accept: application/json


**Beispiel-Response:**

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
    "@id": "/workspaces/workspace/@possible-responsibles",
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

Nur Administratoren eines Teamraums können diese Abfrage durchführen.

Resultate filtern
~~~~~~~~~~~~~~~~~

Mit dem ``query``-Parameter können die Resultate gefiltert werden. Die folgenden Felder werden beim Filtern berücksichtigt:

- Vorname
- Nachname
- E-Mail
- Userid


**Beispiel-Request:**

.. sourcecode:: http

   GET /workspaces/workspace/@possible-responsibles?query=Peter HTTP/1.1
   Accept: application/json


**Beispiel-Response:**

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "@id": "/workspaces/workspace/@possible-responsibles",
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
