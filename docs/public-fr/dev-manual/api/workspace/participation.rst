.. _participation:

Participations teamraum
=======================

L'Endpoint ``@participations`` gère les participations teamraum.


Récupérer une participation:
----------------------------
Une Request GET retourne toutes les participations ains que les invitations actives pour un contenu.

**Exemple de Request**:

   .. sourcecode:: http

       GET /workspace-1/@participations HTTP/1.1
       Accept: application/json

**Exemple de Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "items": [
        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/users/max.muster",
          "@type": "virtual.participations.user",
          "inviter_fullname": null,
          "is_editable": false,
          "participant_fullname": "Max Muster (max.muster)",
          "readable_role": "Responsable",
          "role": "WorkspaceOwner",
          "token": "max.muster",
          "participation_type": "user",
          "readable_participation_type": "User",
        },
        {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc300",
          "@type": "virtual.participations.invitation",
          "inviter_fullname": "Max Muster (max.muster)",
          "is_editable": true,
          "participant_fullname": "Petra Fröhlich (petra.frohlich)",
          "readable_role": "Invité",
          "role": "WorkspaceGuest",
          "token": "3a8bfcb1b6294edfb60e2a43717fc300",
          "participation_type": "invitation",
          "readable_participation_type": "Invitation",
        }
      ]
    }


Récupérer une participation unique:
-----------------------------------
En effectuant une Request GET sur la ressource donnée, il est possible de récupérer les participations et invitations de celle-ci.

**Exemple de Request**:

   .. sourcecode:: http

       GET /workspaces/workspace-1/@participations/users/max.muster HTTP/1.1
       Accept: application/json

**Exemple de Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/users/max.muster",
      "@type": "virtual.participations.user",
      "inviter_fullname": null,
      "is_editable": false,
      "participant_fullname": "Max Muster (max.muster)",
      "readable_role": "Federführung",
      "role": "WorkspaceOwner",
      "token": "max.muster",
      "participation_type": "user",
      "readable_participation_type": "User",
    }


Effacer des participations:
---------------------------
Une Request DELETE sur l'`@id` d'une participation ou invitation efface celle-ci. 

L'URL est composée comme suit:
``gever-url/workspaces/workspace/@participations/{participation_type}/{token}``

**Exemple de Request**:

   .. sourcecode:: http

       DELETE /workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc300 HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Ajouter des participations (Inviter un utilisateur):
----------------------------------------------------
Il est uniquement possible d'ajouter une participation via une invitation. L'utilisateur invité doit d'abord confirmer sa participation avant d'être effectivement autorisé.

L'invitation est lancée via une Request POST sur l'Endpoint `@participation/invitations`.


**Paramètres:**

Obligatoire:

``userid``: ``String``
   ID de l'utilisateur à inviter

``role``: ``String``
   Rôle dans l'espace de travail

**Exemple de Request**:

   .. sourcecode:: http

       POST /workspaces/workspace-1/@participations/invitations/ HTTP/1.1
       Accept: application/json

       {
         "userid": "maria.meier",
         "role": "WorkspaceMember",
       }

**Exemple de Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc301",
          "@type": "virtual.participations.invitation",
          "inviter_fullname": "Max Muster (max.muster)",
          "is_editable": true,
          "participant_fullname": "Maria Meier (maria.meier)",
          "readable_role": "Membre d'équipe",
          "role": "WorkspaceMember",
          "token": "3a8bfcb1b6294edfb60e2a43717fc301",
          "participation_type": "invitation",
          "readable_participation_type": "Invitation",
    }


Modifier des participations:
----------------------------
Aussi bien les participations que les invitations peuvent être modifiées via une Request PATCH sur la ressource pertinente.

**Paramètres:**

Obligatoire:

``role``: ``String``
   Rôle dans l'espace de travail

**Exemple de Request**:

   .. sourcecode:: http

       POST /workspaces/workspace-1/@participations/invitations/3a8bfcb1b6294edfb60e2a43717fc301 HTTP/1.1
       Accept: application/json

       {
         "role": "WorkspaceAdmin",
       }

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
