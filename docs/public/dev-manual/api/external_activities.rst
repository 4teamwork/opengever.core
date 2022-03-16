.. _external-activities:

Externe Aktivitäten
===================

Externe Systeme können, mit den notwendigen Berechtigungen, Benachrichtigungen für Benutzer erzeugen.


Externe Aktivität erzeugen (POST)
---------------------------------

.. http:post:: /@external-activities

   Erzeugt eine externe Aktivität und damit eine Benachrichtigung an den angegebenen Benutzer.

   Die in ``notification_recipients`` angegebene Liste muss genau dem Benutzer entsprechen, mit welchem der Request authentisiert ist. Es ist also nicht erlaubt, Benachrichtigungen an andere Benutzer auszulösen, sondern nur an sich selbst.

   **Ausnahme**: Benutzer mit der Rolle ``PrivilegedNotificationDispatcher`` dürfen auch Benachrichtigungen an andere Benutzer als sich selbst auslösen.

   Dies setzt dementsprechend voraus, dass die externe Applikation als vertrauenswürdig eingestuft wurde, und GEVER so konfiguriert ist, von dieser Applikation Requests im Kontext des Benutzers zu erlauben.

   Beim Aufrufen einer solchen Benachrichtigung wird der Benutzer zu der in ``resource_url`` angegebenen URL weitergeleitet.

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
