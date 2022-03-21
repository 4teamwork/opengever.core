.. _external-activities:

Externe Aktivitäten
===================

Externe Systeme können, mit den notwendigen Berechtigungen, Benachrichtigungen für Benutzer erzeugen.


Externe Aktivität erzeugen (POST)
---------------------------------

.. http:post:: /@external-activities

   Erzeugt eine externe Aktivität und damit eine Benachrichtigung an die angegebenen Benutzer oder Gruppen.

   Beim Aufrufen einer solchen Benachrichtigung wird der Empfänger zu der in ``resource_url`` angegebenen URL weitergeleitet.

   Die in ``notification_recipients`` angegebene Liste muss IDs von Benutzern und/oder Gruppen enthalten, an welche eine Benachrichtigung ausgelöst werden soll.


   .. note::

      API-Benutzer mit normalen Berechtigungen dürfen ausschliesslich Benachrichtigungen **an ihren eigenen Benutzer auslösen** (Schutz vor Missbrauch).

      Dieser Anwendungsfall setzt dementsprechend voraus, dass die externe Applikation als vertrauenswürdig eingestuft wurde, und GEVER so konfiguriert ist, von dieser Applikation Requests im *Kontext des Benutzers* zu erlauben (Impersonation).

      API-Benutzer mit der Rolle ``PrivilegedNotificationDispatcher`` dürfen hingegen Benachrichtigungen an **beliebige Benutzer** auslösen, insbesondere indirekt via Angabe von Gruppen.

      Dieser Anwendungsfall bedingt einen Service-Account für die externe Applikation, welchem die ``PrivilegedNotificationDispatcher`` Rolle zugewiesen wird. Die Anmeldung erfolgt in diesem fall nicht im Kontext des Benutzers, sondern regulär mit dem Service-Account.


   **Request**:

   .. sourcecode:: http

      POST /@external-activities HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
          "notification_recipients": ["john.doe"],
          "resource_url": "https://external.example.org/",
          "title": {
              "de": "Ein Ereignis ist eingetreten",
              "en": "An event happened"
          },
          "label": {
              "de": "...",
              "en": "..."
          },
          "summary": {
              "de": "...",
              "en": "..."
          },
          "description": {
              "de": "...",
              "en": "..."
          }
      }

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
          "activity": {
              "actor_id": "__system__",
              "actor_label": "System",
              "created": "2021-12-09T10:16:00+00:00",
              "label": "...",
              "summary": "...",
              "title": "..."
          }
      }
