.. _operations:

Opérations
==========

les opérations possibles sur l'API sont mappées sur des verbes HTTP.


======= ============ ==========================================================
Verbe   URL          Opération
======= ============ ==========================================================
GET     /{path}      Retourne les attributs d'un objet
POST    /{container} Créé un nouvel objet dans le container respectif
PATCH   /{path}      Actualise les attributs individuels d'un objet
======= ============ ==========================================================


.. _content-get:

Lire les contenus (GET)
-----------------------

La requête GET sur l'URL d'un objet permet de sélectionner les données (Métadonnées aussi bien que données primaires) d'un objet. 

Dans la situation où l'objet est de type "folder" (un conteneur), il existe également un attribut particulier, ``items``, qui contient un ^listing sommaire des sous-objets <summaries>` qui y sont contenus (enfants directs)


.. http:get:: /(path)

   Retourne les attributs de l'objet actuel dans `path`.

   **Exemple de Request**:

   .. sourcecode:: http

      GET /ordnungssystem/direction/dossier-23 HTTP/1.1
      Accept: application/json

   **Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": "https://example.org/ordnungssystem/direction/dossier-23",
        "@type": "opengever.dossier.businesscasedossier",
        "UID": "66395be6595b4db29a3282749ed50302",
        "archival_value": "not archival worthy",
        "archival_value_annotation": null,
        "classification": "unprotected",
        "comments": null,
        "container_location": null,
        "container_type": null,
        "created": "2016-01-08T10:51:40+00:00",
        "custody_period": 30,
        "date_of_cassation": null,
        "date_of_submission": null,
        "description": "",
        "end": null,
        "filing_prefix": null,
        "former_reference_number": null,
        "keywords": [],
        "items": [
          {
            "@id": "https://example.org/ordnungssystem/direction/dossier-23/document-259",
            "@type": "opengever.document.document",
            "description": null,
            "title": "Un Document"
          },
          {
            "@id": "https://example.org/ordnungssystem/direction/dossier-23/document-260",
            "@type": "opengever.document.document",
            "description": null,
            "title": "Un autre document"
          }
        ],
        "modified": "2016-01-19T11:15:22+00:00",
        "number_of_containers": null,
        "parent": {
          "@id": "https://example.org/ordnungssystem/direction",
          "@type": "opengever.repository.repositoryfolder",
          "description": null,
          "title": "Direction"
        },
        "privacy_layer": "privacy_layer_no",
        "public_trial": "unchecked",
        "public_trial_statement": null,
        "reference_number": null,
        "relatedDossier": null,
        "responsible": "john.doe",
        "retention_period": 5,
        "retention_period_annotation": null,
        "review_state": "dossier-state-active",
        "start": "2016-01-08",
        "temporary_former_reference_number": null,
        "title": "Un dossier d'affaires"
      }

.. container:: collapsible

    .. container:: header

       **Code-Beispiel (Python)**

    .. literalinclude:: examples/example_get.py


.. _content-post:

Créer des contenus (POST)
-------------------------

Pour créer un nouvel objet, il faut soumettre une Request ``POST`` sur le Container qui doit le contenir. L'ID de l'objet est déterminé par le système et ne doit pas être spécifié. 

.. http:post:: /(container)

   Créé un nouvel objet dans `container`.

   **Exemple de Request**:

   .. sourcecode:: http

      POST /ordnungssystem/direction HTTP/1.1
      Accept: application/json

      {
        "@type": "opengever.dossier.businesscasedossier",
        "title": "Un nouveu dossier d'affaire",
        "responsible": "john.doe",
        "custody_period": 30,
        "archival_value": "unchecked",
        "retention_period": 5
      }

   **Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: https://example.org/ordnungssystem/direction/dossier-24

      null

L'URL de l'objet nouvellement créé est retourné dans le header ``Location`` de la Response.

.. container:: collapsible

    .. container:: header

       **Exemple de code (Python)**

    .. literalinclude:: examples/example_post.py


.. _content-patch:

Modifier des contenus (PATCH)
-----------------------------

Pour modifier un ou plusieurs attributs d'un objet, il faut utiliser la Request ``PATCH``.


.. http:patch:: /(path)

   Met à jour un ou plusieurs attributs de l'objet dans `path`.

   **Exemple de Request**:

   .. sourcecode:: http

      PATCH /ordnungssystem/direction/dossier-24 HTTP/1.1
      Accept: application/json

      {
        "title": "Un Dossier renommé"
      }

   **Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null

.. container:: collapsible

    .. container:: header

       **Exemple de code (Python)**

    .. literalinclude:: examples/example_patch.py

.. disqus::
