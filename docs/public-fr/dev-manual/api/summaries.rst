.. _summaries:

Listes succinctes
-----------------

Les entrées dans les listes succinctes de conteneurs ("Folders") contiennent par défaut les champs ``@id``, ``@type``, ``title``, ``description`` et ``review_state``.

La liste de champs souhaitée peut toutefois être personnalisée pour contenir des métadonnées spécifiques via le paramètre ``metadata_fields``.

Les champs actuellement supportés pour les listes succinctes sont les suivants:

- ``@type`` (Type de contenu)
- ``created`` (Date de création)
- ``creator`` (Créateur)
- ``description`` (Description)
- ``filename`` (Nom du fichier, s'il s'agit d'un document)
- ``filesize`` (Taille du fichiers'il s'agit d'un document)
- ``mimetype`` (type de fichier, s'il s'agit d'un document)
- ``modified`` (Date de la dernière modification)
- ``review_state`` (Workflow-Status ID)
- ``review_state_label`` (Nom du Workflow-Status)
- ``title`` (Titre)

Le paramètre de string de requête ``metadata_fields`` peut être utilisé pour diriger les listes succinctes sur des requêtes ``GET``..

.. note::
    Les listes succinctes de résultats de recherche de l'Endpoint ``@search`` Utilisent le même mécanisme (``metdata_fields``).


Exemple basé sur une requête ``GET``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. http:get:: /(path)?metadata_fields=(fieldlist)

   Fournit les attributs de l'objet défini sous `path` avec les champs données dans `fieldlist` des listes succinctes des enfants (``items``).

   **Exemple de request**:

   .. sourcecode:: http

      GET /ordnungssystem/direction/dossier-23?metadata_fields:list=filesize&metadata_fields:list=filename HTTP/1.1
      Accept: application/json

   **Exemple de response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": "https://example.org/ordnungssystem/direction/dossier-23",
        "@type": "opengever.dossier.businesscasedossier",
        "title": "Un Dossier d'affaire",

        "...": "",

        "items": [
          {
            "@id": "https://example.org/ordnungssystem/direction/dossier-23/document-259",
            "@type": "opengever.document.document"
            "review_state": "document_state_draft"
            "description": "..."
            "title": "..."
            "filesize": 42560,
            "filename": "présentation.docx",


          },
          {
            "@id": "https://example.org/ordnungssystem/direction/dossier-23/document-260",
            "@type": "opengever.document.document"
            "review_state": "document_state_draft"
            "description": "..."
            "title": "..."
            "filesize": 73536,
            "filename": "candidature.docx",
          }
        ],
        "parent": {
          "@id": "https://example.org/ordnungssystem/direction",
          "@type": "opengever.document.document"
          "review_state": "document_state_draft"
          "description": "..."
          "title": "..."
          "filesize": null,
          "filename": null,
        },

        "...": ""

      }


.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_get_custom_summary.py
