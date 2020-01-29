.. _notifications:

Notifications
=============

L'Endpoint ``@notifications`` propose des fonctions concernant les notifications. L'Endpoint est uniquement disponible au niveau PloneSite et requiert la limitation à un utilisateur via l'ID utilisateur. L'URL se construit comme suit:

``http://example.org/fd/@notifications/peter.mueller``


Listing:
--------
Les notifications de l'utilisateur peuvent être récupérées à l'aide d'une Request GET.


**Exemple de Request**:

   .. sourcecode:: http

       GET /@notifications/peter.mueller HTTP/1.1
       Accept: application/json


**Exemple de Response**:

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
              "read": true,
              "summary": "New task opened by Ziegler Robert",
              "title": "Important task"
          }
      ]


Notification individuelle:
--------------------------
Il est possible de consulter une notification individuelle via l'ID de notification:

**Exemple de Request**:

   .. sourcecode:: http

       GET /@notifications/peter.mueller/3 HTTP/1.1
       Accept: application/json


**Exemple de Response**:

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
          "read": false,
          "summary": "New task opened by Ziegler Robert",
          "title": "Important task"
      }


Marquer une notification comme lue
----------------------------------
Une notification peut être marquée comme lue à l'aide d'une Request PATCH:

**Exemple de Request**:

   .. sourcecode:: http

       PATCH /@notifications/peter.mueller/3 HTTP/1.1
       Accept: application/json

       {
        "read": true
       }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
