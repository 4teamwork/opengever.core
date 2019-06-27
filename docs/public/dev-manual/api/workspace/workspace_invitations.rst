.. _workspace_invitations:

Teamraum Einladungen
====================

Der ``@my-workspace-invitations`` Endpoint behandelt eigene Teamraum Einladungen während die Einladungen selbst über den Endpoint ``@workspace-invitations`` gehandabt werden können.


Alle Einladungen abrufen:
-------------------------
Ein GET Request auf den Endpoint gibt alle aktuellen Einladungen zurück.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@my-workspace-invitations HTTP/1.1
       Accept: application/json

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "items": [
        {
          "@id": "http://localhost:8080/fd/@workspace-invitations/95423bc5e6254eaea8fe2492c4140175",
          "@type": "virtual.participations.invitation",
          "accept": "http://localhost:8080/fd/@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/accept",
          "decline": "http://localhost:8080/fd/@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/decline",
          "inviter_fullname": "zopemaster (zopemaster)",
          "title": "Projekt Redesign"
          "created": "2019-03-11T13:50:14+00:00"
        }
      ]
    }


Eine Einladung annehmen:
------------------------
Führen Sie einen entsprechenden POST-Request auf den Endpoint der Einladung aus.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/@workspace-invitation/{invitation_id}/accept``

Als Antwort erhalten Sie den Arbeitsraum, für welchen die Einladung angenommen wurde.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/accept HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id":"http://localhost:8080/fd/workspaces/workspace-13",
      "@type":"opengever.workspace.workspace",
      "...": "..."
    }


Eine Einladung ablehnen:
------------------------
Führen Sie einen entsprechenden POST-Request auf den Endpoint der Einladung aus.

Die URL setzt sich dabei folgendermassen zusammen:
``gever-url/@workspace-invitation/{invitation_id}/decline``


**Beispiel-Request**:

   .. sourcecode:: http

       POST /@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/decline HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

