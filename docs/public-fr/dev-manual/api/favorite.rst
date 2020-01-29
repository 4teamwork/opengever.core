.. _favorites:

Favoris
=======

L'Endpoint ``@favorites`` offre toutes les fonctionnalités pour lister et traiter les favoris globaux, qui sont gérés individuellement par utilisateur mais cela comme un groupement GEVER de manière centralisée. L'Endpoint est uniquement disponible au niveau PloneSite et requiert une limitation par utilisateur via son ID. L'URL est composée de la manière suivante:

``http://example.org/fd/@favorites/peter.mueller``


Listing:
--------
par l'intermédiaire d'une Request GET, il est possible de lister les favoris d'un utilisateur. La requête est globale à travers tous les clients/départements du groupement.

**Exemple de Request**:

   .. sourcecode:: http

       GET /@favorites/peter.mueller HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      [
          {
              "@id": "http://localhost:8080/fd/@favorites/peter.mueller/3",
              "favorite_id": 3,
              "icon_class": "icon-dokument_word",
              "oguid": "fd:68398212",
              "title": "Lignes directrices projets de lois",
              "portal_type": "opengever.document.document",
              "position": 1,
              "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
          }
          ,
          {
              "@id": "http://localhost:8080/fd/@favorites/peter.mueller/57",
              "favorite_id": 57,
              "icon_class": "contenttype-opengever-dossier-businesscasedossier",
              "oguid": "fd:68336212",
              "title": "Requêtes 2020",
              "portal_type": "opengever.dossier.businesscasedossier",
              "position": 2,
              "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68336212"
          }
      ]

Ajouter un favori:
------------------

Il est possible d'ajouter un favori pour n'importe quel objet par l'intermédiaire d'une Request POST. Lors cette dernière il faut fournir l'OGUID en tant que paramètre ``oguid`` ou l'UID en tant que paramètre ``uid``.


**Exemple de Request**:

   .. sourcecode:: http

       POST /@favorites/peter.mueller HTTP/1.1
       Accept: application/json

       {
        "oguid": "fd:68398212"
       }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: http://localhost:8080/fd/@favorites/peter.mueller/20

      {
          "@id": "http://localhost:8080/fd/@favorites/peter.mueller/20",
          "favorite_id": 20,
          "icon_class": "icon-dokument_word",
          "oguid": "fd:68398212",
          "title": "Anfrage 2018",
          "portal_type": "opengever.document.document",
          "position": 1,
          "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
      }



Modifier un favori:
-------------------

Un favori existant peut être modifié par l'intermédiaire d'une Request POST. Seul les paramètres `title` et `position` y sont pris en compte.  Lorsque le titre d'un favori est modifié, le flag `is_title_personalized` est automatiquement activé.

L'URL est construite de la manière suivante:
``gever-url/@favorites/{userid}/{id-favoris}``


**Exemple de Request**:

   .. sourcecode:: http

       PATCH /@favorites/peter.mueller/20 HTTP/1.1
       Accept: application/json

       {
        "title": "Weekly Document",
        "position": 35
       }


Une Request PATCH retourne `204 No content Response` par défaut.

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


IL est toutefois possible de recevoir une représentation d'objet comme Response en retour d'une Request PATCH. Pour cela, un faut spécifier un Header ``Prefer`` ayant pour valeur ``return=representation``.

**Exemple de Response avec Header Prefer**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/@favorites/peter.mueller/20",
          "favorite_id": 20,
          "icon_class": "icon-dokument_word",
          "oguid": "fd:68398212",
          "title": "Weekly Document",
          "portal_type": "opengever.document.document",
          "position": 35,
          "target_url": "http://localhost:8080/fd/resolve_oguid/fd:68398212"
      }



Supprimer un favori:
--------------------

Un favori existant peut être supprimé par une Request DELETE sur l'url pertinente. 

L'URL est construite de la manière suivante:
``gever-url/@favorites/{userid}/{favoriten-id}``


**Exemple de Request**:

   .. sourcecode:: http

       DELETE /@favorites/peter.mueller/20 HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
