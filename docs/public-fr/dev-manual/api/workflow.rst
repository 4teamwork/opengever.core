.. _workflow:

Workflow
========

Beaucoup de :ref:`types de contenus <content-types>` ont un workflow associé dans GEVER (p.ex. position, dossier, tâches, ...).

Le **Workflow-State** courant d'un objet est, pour des raisons de simplicité
``review_state`` est contenu directment dans une représentation d'objet :ref:`GET <content-get>`.

.. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
       "@context": "http://www.w3.org/ns/hydra/context.jsonld",
       "@id": "https://example.org/dossier-15",
       "@type": "opengever.dossier.businesscasedossier",
       "...": "...",
       "review_state": "dossier-state-active"
    }

L'Endpoint ``@workflow`` est utilisée pour les aspects de Workflows restants:


.. http:get:: /(path)/@workflow

   Retourne les informations de workflow pour l'objet adressé dans `path`.

   Les informations de workflow contiennent la **Workflow-History** (qui inclut aussi le Workflow-State) ainsi que toutes les **transitions workflow** possibles. 

   **Exemple de Request**:

   .. sourcecode:: http

       GET /dossier-15/@workflow HTTP/1.1
       Accept: application/json

   **Exemple de Response**:

   .. literalinclude:: examples/workflow_get.json
      :language: http

   Ce dossier se trouve actuellement dans l'état clôturé. (``dossier-state-resolved``, dernière entrée dans la Workflow-History).

   De par ce Workflow-State, la seule transition possible est la réouverture du dossier (``dossier-transition-reactivate``). Cette transition peut être déclenchée par une Request ``POST`` sur l'URL respective:

.. http:post:: /(path)/@workflow/(transition)

   Exécute la Workflow-Transition `transition` sur l'objet adressé dans `path`.

   **Exemple de Request**:

   .. sourcecode:: http

       POST /dossier-15/@workflow/dossier-transition-reactivate HTTP/1.1
       Accept: application/json

   **Exemple de Response**:

   .. literalinclude:: examples/workflow_post.json
      :language: http

.. disqus::