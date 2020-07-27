.. _notifications:

Benachrichtigungen
==================

Der ``@notifications`` Endpoint stellt Funktionen für die Benachrichtigungen zur Verfügung. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung und erwartet eine Einschränkung auf einen Benutzer via Benutzer-ID. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/@notifications/peter.mueller``


Auflistung:
-----------
Mittels eines GET-Request können Benachrichtigungen des Benutzers abgefragt werden.


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@notifications/peter.mueller HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "@id": "http://nohost/plone/@notifications/kathi.barfuss/3",
              "actor_id": "robert.ziegler",
              "actor_label": "Ziegler Robert",
              "created": "2018-10-16T00:00:00+00:00",
              "label": "Task opened",
              "link": "http://nohost/plone/@@resolve_notification?notification_id=3",
              "notification_id": 3,
              "oguid": "plone:1016273300",
              "read": false,
              "summary": "New task opened by Ziegler Robert",
              "title": "Important task"
          },
          {
              "@id": "http://nohost/plone/@notifications/kathi.barfuss/1",
              "actor_id": "robert.ziegler",
              "actor_label": "Ziegler Robert",
              "created": "2017-10-16T00:00:00+00:00",
              "label": "Task opened",
              "link": "http://nohost/plone/@@resolve_notification?notification_id=1",
              "notification_id": 1,
              "oguid": "plone:1016273300",
              "read": true,
              "summary": "New task opened by Ziegler Robert",
              "title": "Important task"
          }
      ]


Einzelne Benachrichtigung:
--------------------------
Eine einzelne Benarchrichtigung kann durch hinzufügen der Benachrichtigungs-ID abgefragt werden:


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@notifications/peter.mueller/3 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://nohost/plone/@notifications/kathi.barfuss/3",
          "actor_id": "robert.ziegler",
          "actor_label": "Ziegler Robert",
          "created": "2018-10-16T00:00:00+00:00",
          "label": "Task opened",
          "link": "http://nohost/plone/@@resolve_notification?notification_id=3",
          "notification_id": 3,
          "oguid": "plone:1016273300",
          "read": false,
          "summary": "New task opened by Ziegler Robert",
          "title": "Important task"
      }


Benachrichtigung als gelesen markieren
--------------------------------------
Durch einen PATCH-Request kann eine Benachrichtigung als gelesen markiert werden:


**Beispiel-Request**:

   .. sourcecode:: http

       PATCH /@notifications/peter.mueller/3 HTTP/1.1
       Accept: application/json

       {
        "read": true
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Benachrichtigungen unterdrücken
-------------------------------
Viele Aktionen lösen Benachrichtigungen aus, beispielsweise das Kommentieren einer Aufgabe. Um Benachrichtigungen zu unterdrücken, kann der ``X-GEVER-SuppressNotifications``-Header mitgeschickt werden. Akzeptiert werden folgende Werte (case insensitive): ``yes, y, true, t, 1``


**Beispiel-Request**:

   .. sourcecode:: http

      POST /task-1/@responses HTTP/1.1
      Accept: application/json
      Content-Type: application/json
      X-GEVER-SuppressNotifications: true

      {
        "text": "Bitte rasch anschauen. Danke.",
      }
