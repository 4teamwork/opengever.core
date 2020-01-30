.. _journal:

Entrées dans l'historique
=========================

L'Endpoint ``@journal`` traite les entrés dans l'historique.

Attention: Il n'est pas possible de modifier les entrées dans l'historique après leur enregistrement.


Ajouter une entrée dans l'historique:
-------------------------------------
Une nouvelle entrée est générée à l'aide d'une requête POST. Body doit contenir l'attribut ``comment``.

**Paramètres:**

Obligatoire:

``comment``: ``String``
   Titre de l'entrée.

Optionnels:

``category``: ``String``
   Catégorie d'historique. La liste de valeurs supportées peut être récupérée via l'Endpoint `@vocabularies/opengever.journal.manual_entry_categories`.

``related_documents``: ``String[]``
   URLs pointant sur des documents GEVER. 


**Exemple de Request**:

   .. sourcecode:: http

       POST /dossier-1/@journal HTTP/1.1
       Accept: application/json

       {
         "comment": "Dossier archivé avec un outil externe",
         "category": "phone-call",
         "related_documents": [
           "http://localhost:8080/fd/ordnungssystem/fuehrung/kommunikation/allgemeines/dossier-1/document-1",
           "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-14/document-33"
         ]
       }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Consulter des entrées dans l'historique:
----------------------------------------
Une Request GET retourne l'historique d'un contenu.

**Exemple de Request**:

   .. sourcecode:: http

       GET /dossier-1/@journal HTTP/1.1
       Accept: application/json

**Exemple de Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "items": [
        {
          "actor_fullname": "zopemaster",
          "actor_id": "zopemaster",
          "comments": "Je suis une nouvelle entrée dans l'historique",
          "time": "2019-04-15T14:00:48+00:00",
          "title": "Entrée manuelle: Entretien téléphonique"
        },
        {
          "actor_fullname": "zopemaster",
          "actor_id": "zopemaster",
          "comments": "Je suis une nouvelle entrée dans l'historique",
          "time": "2019-04-15T13:59:21+00:00",
          "title": "Entrée manuelle: Entretien téléphonique"
        }
      ],
      "items_total": 2
    }


.. note::
        Les résultats de recherche sont **paginés** lorsque le nombre de résultats retournés dépasse la taille de page définie (25 par défaut). Voir :doc:`batching` pour plus de détails concernant l'utilisation de résultats paginés.
