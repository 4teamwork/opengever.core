.. _favorites:

Favoriten
=========

Der ``@favorites`` endpoint bietet alle Funktion für die Auflistung und Bearbeitung der globalen Favoriten welche pro Benutzer aber über einen kompletten GEVER Verbund zentral verwaltet werden. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung und erwartet eine Einschränkung auf einen Benutzer via Benutzer-ID. Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/@favorites/peter.mueller``


Auflistung:
-----------
Mittels eines GET Request können Favoriten des Benutzers abgefragt werden. Dabei werden alle, also global über den ganzen Mandanten-Verbundes, zurückgegeben.


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@favorites/peter.mueller HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "@id": "http://localhost:8080/fd/@favorites/peter.mueller/3",
              "favorite_id": 3,
              "filename": "Richtlinien Gesetzesentwuerfe.docx",
              "icon_class": "icon-dokument_word",
              "is_leafnode": null,
              "oguid": "fd:68398212",
              "title": "Richtlinien Gesetzesentwürfe",
              "portal_type": "opengever.document.document",
              "position": 1,
              "review_state": "document-state-draft",
              "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
          }
          ,
          {
              "@id": "http://localhost:8080/fd/@favorites/peter.mueller/57",
              "favorite_id": 57,
              "filename": null,
              "icon_class": "contenttype-opengever-dossier-businesscasedossier",
              "is_leafnode": null,
              "is_subdossier": false,
              "oguid": "fd:68336212",
              "title": "Anfragen 2018",
              "portal_type": "opengever.dossier.businesscasedossier",
              "position": 2,
              "review_state": "dossier-state-active",
              "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68336212"
          }
      ]

Favorit hinzufügen:
-------------------
Ein Favorit für ein beliebiges Objekt kann mittels POST Request hinzugefügt werden. Dabei wird die Oguid als ``oguid`` Parameter oder die UID als ``uid`` Parameter erwartet.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /@favorites/peter.mueller HTTP/1.1
       Accept: application/json

       {
        "oguid": "fd:68398212"
       }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: http://localhost:8080/fd/@favorites/peter.mueller/20

      {
          "@id": "http://localhost:8080/fd/@favorites/peter.mueller/20",
          "favorite_id": 20,
          "filename": "Anfrage 2018.docx",
          "icon_class": "icon-dokument_word",
          "is_leafnode": null,
          "oguid": "fd:68398212",
          "title": "Anfrage 2018",
          "portal_type": "opengever.document.document",
          "position": 1,
          "review_state": "document-state-draft",
          "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
      }



Favorit bearbeiten:
-------------------
Ein bestehender Favorit kann mittels PATCH Request überarbeitet werden. Es werden nur die Parameter `title` und `position` beachtet. Wird der Titel eines Favoriten verändert, so wird automatisch auch das flag `is_title_personalized` aktiviert.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/@favorites/{userid}/{favoriten-id}``


**Beispiel-Request**:

   .. sourcecode:: http

       PATCH /@favorites/peter.mueller/20 HTTP/1.1
       Accept: application/json

       {
        "title": "Weekly Document",
        "position": 35
       }


Ein erfolgreicher Patch-Request wird standardmässig mit einer 204 No content Response beantwortet.

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Es ist aber möglich bei einem PATCH request die Objekt-Repräsentation als Response zuerhalten, hierzu muss ein ``Prefer`` Header mit dem Wert ``return=representation`` gesetzt werden.

**Beispiel-Response mit Prefer Header**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/@favorites/peter.mueller/20",
          "favorite_id": 20,
          "filename": "Weekly Document.docx",
          "icon_class": "icon-dokument_word",
          "is_leafnode": null,
          "oguid": "fd:68398212",
          "title": "Weekly Document",
          "portal_type": "opengever.document.document",
          "position": 35,
          "review_state": "document-state-draft",
          "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
      }



Favorit entfernen:
------------------
Ein bestehender Favorit kann mittels DELETE Request auf die entsprechender URL gelöscht werden.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/@favorites/{userid}/{favoriten-id}``


**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /@favorites/peter.mueller/20 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
