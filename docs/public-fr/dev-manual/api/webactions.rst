.. _webactions:

Webactions
==========

L'Endpoint ``/@webactions`` à la racine du client/département permet de gérer les WebActions dans GEVER.

.. contents::

Ces Webactions peuvent par exemple être p.ex. être enregistrées pour ou par des applications tierces (pour autant que les :ref:`droits <webactions-mgmt-permissions>` nécéssaires soient donnés), Afin de permettre une intégration sans faille dans GEVER. Avec les Webactions, des liens et icônes peuvent être directement intégrés à certains endroits dans GEVER, par l'intermédiaire desquels les utilisateurs peuvent ensuite déclencher des actions dans l'application tierce.

.. _webactions-mgmt-permissions:

Droits pour la gestion de Webactions
------------------------------------

Afin de pouvoir gérer les Webactions via l'API REST, il faut disposer de la permission ``opengever.webactions: Manage own WebActions``. Par défaut, celle-ci est assignée au rôle ``WebActionManager`` dans GEVER.

Les utilisateurs ayant ces droits peuvent créer de nouvelles Webactions et gérer celles qu'ils ont eux-mêmes créés (lister, modifier, effacer).


Créer (POST)
------------

.. http:post:: /@webactions


   Créé une nouvelle Webaction ayant les données fournies dans le Body (JSON).

   **Request**:

   .. sourcecode:: http

      POST /@webactions HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global"
      }

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: http://demo.onegovgever.ch/@webactions/0

      {
        "@id": "http://demo.onegovgever.ch/@webactions/0",
        "action_id": 0,
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global",
        "created": "2019-12-31T17:45:00",
        "modified": "2019-12-31T17:45:00",
        "owner": "webaction.manager"
      }

.. table::

    +------------------+------------------------------------------------------------------+
    | Status Code      | Description                                                      |
    +==================+==================================================================+
    | 201 Created      | WebAction créée avec succès. Représentation dans Response-Body,  |
    |                  | URL de l'action créée dans le Header ``Location``.               |
    +------------------+------------------------------------------------------------------+
    | 400 Bad Request  | Erreur lors de la validation du schéma, ou autre erreur côté     |
    |                  | client. Details dans Response-Body.                              |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Échec de l'authentification ou de l'autorisation                 |
    +------------------+------------------------------------------------------------------+

Cet exemple décrit les données minimales pour créer une Webaction. Pour plus de détails concernant les champs supportés, voir `Propriétés des Webactions`_.

La Response content la représentation de la Webaction dans le body, y-compris celles du serveur des métadonnées attribuées lors de la création (voir `Métadonnées attribuées par le serveur`_).

Le Header ``Location`` contient l'url canonique (préférée) de l'action qui vient d'être créée et qui peut être utilisée pour d'autres Requests.

Sélectionner (GET)
------------------

.. http:get:: /@webactions/(action_id)

   Sélectionne la Webaction avec l'``action_id`` correspondante.

   **Request**:

   .. sourcecode:: http

      GET /@webactions/0 HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/@webactions/0",
        "action_id": 0,
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global",
        "created": "2019-12-31T17:45:00",
        "modified": "2019-12-31T17:45:00",
        "owner": "webaction.manager"
      }

.. table::

    +------------------+------------------------------------------------------------------+
    | Status Code      | Description                                                      |
    +==================+==================================================================+
    | 200 OK           | Répondu à la request avec succès                                 |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Echec de l'authentification ou autorisation                      |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | La Webaction avec l'id ``action_id`` n'a pas pu être trouvée.    |
    +------------------+------------------------------------------------------------------+


Lister (GET)
------------


.. http:get:: /@webactions

   Liste les Webactions créées par cet utilisateur.

   **Request**:

   .. sourcecode:: http

      GET /@webactions HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/@webactions",
        "items": [
          {
            "@id": "http://demo.onegovgever.ch/@webactions/0",
            "action_id": 0,
            "title": "Open in ExternalApp 0",
            "target_url": "http://example.org/endpoint0",
            "display": "actions-menu",
            "mode": "self",
            "order": 0,
            "scope": "global",
            "created": "2019-12-31T17:45:00",
            "modified": "2019-12-31T17:45:00",
            "owner": "some.user",
          },
          {
            "@id": "http://demo.onegovgever.ch/@webactions/1",
            "action_id": 1,
            "title": "Open in ExternalApp 1",
            "target_url": "http://example.org/endpoint1",
            "display": "title-buttons",
            "mode": "self",
            "order": 0,
            "scope": "global",
            "created": "2019-12-31T17:46:00",
            "modified": "2019-12-31T17:46:00",
            "owner": "webaction.manager",
          }
        ]
      }

.. table::

    +------------------+------------------------------------------------------------------+
    | Status Code      | Description                                                      |
    +==================+==================================================================+
    | 200 OK           | Répondu à la request avec succès                                 |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Échec de l'authentification ou autorisation                      |
    +------------------+------------------------------------------------------------------+



Modifier (PATCH)
----------------


.. http:patch:: /@webactions/(action_id)

   Met a jour la Webaction identifiée par ``action_id`` avec les données fournies dans le Body (JSON).

   **Request**:

   .. sourcecode:: http

      PATCH /@webactions/0 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "title": "New title"
      }


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json

.. table::

    +------------------+------------------------------------------------------------------+
    | Status Code      | Description                                                      |
    +==================+==================================================================+
    | 204 No Content   | Webaction mise à jour avec succès                                |
    +------------------+------------------------------------------------------------------+
    | 400 Bad Request  | Erreur lors de la validation du Schema ou autre erreur côté      |
    |                  | côté client. Details dans Response-Body.                         |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Echec de l'authentification ou autorisation                      |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | La Webaction avec l'id ``action_id`` n'a pas pu être trouvée.    |
    +------------------+------------------------------------------------------------------+



Effacer (DELETE)
----------------


.. http:delete:: /@webactions/(action_id)

   Efface la Webaction identifiée par ``action_id``.

   **Request**:

   .. sourcecode:: http

      DELETE /@webactions/0 HTTP/1.1
      Accept: application/json


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json

.. table::

    +------------------+------------------------------------------------------------------+
    | Status Code      | Description                                                      |
    +==================+==================================================================+
    | 204 No Content   | Webaction effacée avec succès                                    |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Échec de l'authentification ou autorisation                      |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | La Webaction avec l'id ``action_id`` n'a pas pu être trouvée.    |
    +------------------+------------------------------------------------------------------+


.. _webactions-fields:

Propriétés des Webactions
-------------------------

Ci-dessous, un listing de tous les champs supportés par les Webactions, y-compris avec leur type et description.

+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| Champ           | Typ                             | Description                                                                 |
+=================+=================================+=============================================================================+
| ``title``       | String, obligatoire             | Titre de la Webaction                                                       |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``unique_name`` | String, optional                | Nom unique de la Webaction contrôlé par son créateur                        |
|                 |                                 | (voir :ref:`Nom unique <webactions-unique-name>` ).                         |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``target_url``  | String, obligatoire             | URL cible de l'Endpoint dans l'application tierce.                          |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``enabled``     | Boolean, optionnel              | Peut être utilisé pour temporairement activer une Webaction, p. ex. lorsque |
|                 |                                 | aucune valeur n'est définie, l'action est tout de même traitée comme active |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``icon_name``   | String, obligatoire (selon cas) | Classe CSS Font-Awesome (p.ex. ``fa-folder``)                               |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``icon_data``   | String, obligatoire (selon cas) | Data URI avec Icône, Encodée en Base64.                                     |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``display``     | Choice, obligatoire             | :ref:`Emplacement d'affichage <webactions-display>` de la Webaction         |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``mode``        | Choice, obligatoire             | Fenêtre-Cible: Détermine comment le lien sera ouvert.                       |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``order``       | Integer, 0-100, obligatoire     | Assistance au tri pour définir l'ordre des Webactions enregistrées          |
|                 |                                 | 0 indique la 1ère position, 100 bedeutet la dernière.                       |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``scope``       | Choice, obligatoire             | définit pour quels objets la Webaction est disponible.                      |
|                 |                                 | Aussi voir :ref:`scope <webactions-scope>`.                                 |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``types``       | Liste de Strings, optional      | Liste de types de contenus d'objets pour lesquels une Webaction est         |
|                 |                                 | fondamentalement proposée. Exemple ``opengever.document.document``,         |
|                 |                                 | selon :ref:`Listing des types de contenus <content-types>` dans la doc.     |
|                 |                                 | Lorsqu'aucun type n'est proposé, tous les types correspondent.              |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``groups``      | Liste de Strings, optionnel     | Liste des noms d'utilisateur (IDs, selon LDAP). Lorsque configuré, le user  |
|                 |                                 | doit être membre dans au moins un de ces groupes pour que la Webaction soit |
|                 |                                 | proposée.                                                                   |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``permissions`` | Liste de Strings, optional      | liste de droits. Lorsuqe configuré, l'utilisateur nécessite au moins un     |
|                 |                                 | droit pour que la Webaction soit proposée. Voir aussi                       |
|                 |                                 | :ref:`Actions dépendantes des droits <webactions-permissions>`.             |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+
| ``comment``     | String, optional                | Texte libre pour commentaires.                                              |
+-----------------+---------------------------------+-----------------------------------------------------------------------------+


.. _webactions-mode:

Fenêtre-Cible
-------------

Par l'intermédiaire du champ ``mode``, il est possible de définir la manière dont un lien est ouvert.

Valeurs autorisées:

+---------------+------------------------------------------------------------------+
| Valeur        | Description                                                      |
+===============+==================================================================+
| ``self``      | La cible est directement ouverte dans l'onglet de GEVER. Utile   |
|               | pour un sceénario de redirection où l'utilisateur retourne à sa  |
|               | position initiale à la fin.                                      |
+---------------+------------------------------------------------------------------+
| ``blank``     | La cible est ouverte dans un nouvel onglet.                      |
+---------------+------------------------------------------------------------------+
| ``modal``     | Pas encore implémentée. La cible est ouverte dans une fenêtre    |
|               | modale                                                           |
+---------------+------------------------------------------------------------------+

.. _webactions-scope:

Scope
-----

Le champ ``scope`` permet de définir pour quels objets une Webaction est proposée.

+---------------+---------------------------------------------------------------------+
| Valeur        | Description                                                         |
+===============+=====================================================================+
| ``global``    | La Webaction est fondamentallement prposée pour tous les objets.    |
+---------------+---------------------------------------------------------------------+
| ``context``   | Pas encore implémenté.                                              |
+---------------+---------------------------------------------------------------------+
| ``recursive`` | Pas encore implémenté.                                              |
+---------------+---------------------------------------------------------------------+


.. _webactions-server-metadata:

Métadonnées attribuées par le serveur
-------------------------------------

+---------------+-------------+-------------------------------------------------------------------+
| Champ         | Type        | Description                                                       |
+===============+=============+===================================================================+
| ``action_id`` | Integer     | Identifiant unique de la Webaction enregistrée par client         |
+---------------+-------------+-------------------------------------------------------------------+
| ``created``   | Timestamp   | Zeitpunkt der Erstellung der Webaction                            |
+---------------+-------------+-------------------------------------------------------------------+
| ``modified``  | Timestamp   | Zeitpunkt der letzten Modifikation der Webaction                  |
+---------------+-------------+-------------------------------------------------------------------+
| ``owner``     | String      | Benutzer-ID des Erstellers der Webaction                          |
+---------------+-------------+-------------------------------------------------------------------+

.. _webactions-display:

Emplacement d'affichage
-----------------------

Les Webactions peuvent être affichés en différents endroits.

Selon l'emplacement d'affichage, il est soit obligatoire, soit possible, soit impossible d'indiquer une icône. Cela est validé par l'API et un message d'erreur indique respectivement lorsque cette condition n'est pas remplie.

Une icône peut être donnée soit via son nom (``icon_name``) ou une Data URI (Encodée en Base64, ``icon_data``). Au cas où une icône est donnée, seul un de ces deux champs peut être défini.

Les emplacements d'affichage suivants sont autorisés en tant que valeurs pour le champ ``display``:

+--------------------+---------------+------------------------------------------------------------------+
| Lieu               | Icône         | Description                                                      |
+====================+===============+==================================================================+
| ``action-buttons`` | Optionnel     | La Webaction est affichée dans la liste d'actions pour les       |
|                    |               | tâches, documents et autres contenus. Cela fonctionne pour les   |
|                    |               | types de contenus qui font appel à cette liste d'actions (dont   |
|                    |               | les tâches, les transferts, les requêtes et les documents).      |
+--------------------+---------------+------------------------------------------------------------------+
| ``actions-menu``   | Aucune        | La Webaction est affichée dans le menu "Actions".                |
+--------------------+---------------+------------------------------------------------------------------+
| ``add-menu``       | Obligatoire   | La Webaction est affichée dans le menu "Ajouter".                |
+--------------------+---------------+------------------------------------------------------------------+
| ``title-buttons``  | Obligatoire   | La Webaction est affichée en tant qu'icône à côté du titre.      |
|                    |               | Le titre de la Webaction est utilisé comme Tooltip.              |
+--------------------+---------------+------------------------------------------------------------------+
| ``user-menu``      | Aucune        | La Webaction est affichée dans le menu utilisateur.              |
+--------------------+---------------+------------------------------------------------------------------+

.. _webactions-permissions:

Actions dépendantes des droits
------------------------------

Les actions peuvent être limitées de telle manière qu’elles ne s'affichent que lorsqu'un utilisateur dispose d'au moins un des droits indiqués dans le contexte donné.

Les valeurs suivantes peuvent être utilisées pour le champ ``permissions``:

+---------------------+---------------------------------------------------------------------+
| Droit               | Description                                                         |
+=====================+=====================================================================+
| ``edit``            | L'utilisateur a le droit de modifier le contenu.                    |
+---------------------+---------------------------------------------------------------------+
| ``add:TYPE``        | L'utilisateur a le droit d'ajouter un nouveau contenu du type       |
|                     | spécifié. P.ex. ``add:opengever.dossier.businesscasedossier`` pour  |
|                     | l'ajout d'un dossier d'affaire. La liste actuelle                   |
|                     | :ref:`Liste de types <content-types>` est disponible dans           |
|                     | la documentation REST-API                                           |
+---------------------+---------------------------------------------------------------------+
| ``trash``           | L'utilisateur peut déplacer des contenus vers la corbeille.         |
+---------------------+---------------------------------------------------------------------+
| ``untrash``         | L'utilisateur peut restaurer des contenus depuis la corbeille.      |
+---------------------+---------------------------------------------------------------------+
| ``manage-security`` | L'utilisateur peut assigner des rôles à d'autres utilisateurs.      |
+---------------------+---------------------------------------------------------------------+

.. _webactions-unique-name:

Nom unique
----------

Le champ optionnel ``unique_name`` permet d'assurer qu'une Webaction ne soit pas accidentellement créée plusieurs fois.

Ce champ peut être défini comem un string arbitraire par le client qui créé une Webaction, définissant clairement celle-ci du point de vue du client. Lorsque disponible, le serveur ne valide la Webaction plus que par l'existence de ce nom, et refuse autrement la création ou la mise à jour de la Webaction.

Au cas où un ``unique_name`` est donnée mais existe déjà, le serveur retourne l'erreur``400 Bad Request``:


**Response**:

.. sourcecode:: http

   HTTP/1.1 400 Bad Request
   Content-Type: application/json

   {
     "type": "BadRequest",
     "message": "[('unique_name', ActionAlreadyExists(\"An action with the unique_name u'existing-unique-name' already exists\",))]"
   }
