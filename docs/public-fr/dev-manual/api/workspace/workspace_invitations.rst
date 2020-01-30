.. _workspace_invitations:

Invitations teamraum
====================

L'Endpoint ``@my-workspace-invitations`` gère les invitations propres à l'utilisateur tandis que les invitations sont gérées par ``@workspace-invitations``.


Récupérer toutes les invitations:
---------------------------------
Une Request GET sur l'Enpoint retourne toutes les invitations courantes.

**Exemple de Request**:

   .. sourcecode:: http

       GET /@my-workspace-invitations HTTP/1.1
       Accept: application/json

**Exemple de Response**:


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
          "title": "Projet Redesign"
          "created": "2019-03-11T13:50:14+00:00"
        }
      ]
    }


Accepter une invitation
-----------------------
Une Request POST sur l'Enpoint de l'invitation permet de l'accepter. 

L'URL est assemblée de la manière suivante:
``gever-url/@workspace-invitation/{invitation_id}/accept``

En retour, on obtient l'espace de travail pour lequel l'invitation a été acceptée. de.

**Exemple de Request**:

   .. sourcecode:: http

       POST /@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/accept HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id":"http://localhost:8080/fd/workspaces/workspace-13",
      "@type":"opengever.workspace.workspace",
      "...": "..."
    }


Décliner une invitation:
------------------------
In inviation peut être déclinée via une Request POST sur l'Endpoint de l'invitation.

L'URL est assemblée de la manière suivante:
``gever-url/@workspace-invitation/{invitation_id}/decline``


**Exemple de Request**:

   .. sourcecode:: http

       POST /@workspace-invitations/95423bc5e6254eaea8fe2492c4140175/decline HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

