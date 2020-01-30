.. _usersettings:

Personnalisation
================

l'Endpoint ``/@user-settings`` à la racine du client/département permet de définir ou ajuster les réglages personnels des utilisateurs.


Séléction (GET)
---------------

.. http:get:: /@user-settings

   Retourne les réglages de l'utilisateur courant. Si aucune personnalisation n'a eu lieu, ce sont les valeurs par défaut du client/département qui sont retournés.

   **Request**:

   .. sourcecode:: http

      GET /@user-settings HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "notify_inbox_actions": true,
        "notify_own_actions": true,
        "seen_tours": [
          "gever.introduction",
          "gever.release-2019.3"
        ]
      }


Modifiaction des réglages (PATCH)
---------------------------------

.. http:patch:: /@user-settings

   Les réglages de l'utilisateur courant peuvent être modifiés via une Request PATCH.
   
   **Request**:

   .. sourcecode:: http

      PATCH /@user-settings HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "notify_own_actions": true,
        "seen_tours": ["gever.introduction", "gever.release-2019.3"]
      }


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json

Il est aussi possible de récupérer la représentation en tant que Response, de la même manière que pour les autres Requests PATCH, en spécifiant un Header ``Prefer`` avec pour valeur ``return=representation``.
