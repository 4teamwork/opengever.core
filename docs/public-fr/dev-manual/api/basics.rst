Principes fondamentaux:
=======================

La OneGov GEVER API est une RESTful_ HTTP API.

Celà signifie que des operations sont executées via l'API via des requêtes HTTP, qui sont effectuées par un client HTTP.

  HTTP_ est un protocol de communication entre un client et un serveur, basé sur l'échange de requêtes du client (**Request**) et de réponses du serveur (**Response**).

L'utilisation de l'API fonctionne ainsi: des requêtes, incluant un HTTP-Header spécial qui les désigne comme des API-Requests (pour les distinguer de requêtes d'un browser normal), sont effectuées sur l'URL d'un élément de contenu (objet).

Pour la plupart de ces requêtes, l'utilisateur doit d'abord s'authentifier auprès de l'API, voir
:ref:`authentification <authentication>`.

------


Request
-------

Des requêtes à l'API se composent d'un **HTTP Verb**, d'une
**URL**, de **Request-Heads** ainsi que, pour certains types de requêtes, d'un
**Request-Body** en format JSON.

HTTP Verb
^^^^^^^^^

Il est décrit dans le chapitre :ref:`operations` avec quels verbes HTTP les opérations disponibles sont associées.

URL
^^^

L'URL d'une requête est détérminé par l'objet, sur lequel l'on veut effectuer une opération. Cette URL est en général visible pour l'object correspondant dans la bar d'adresse du navigateur.

.. _basics-headers:

Headers
^^^^^^^

L'API utilise JSON pour la sérialisation de données, que ce soit pour les données reçues ou émises. Il faut donc mettre le HTTP-Header ``Accept: application/json`` dans la requête, pour qu'elle soit transmise à l'API.

**Exemple de requête**:

.. sourcecode:: http

  GET /ordnungssystem HTTP/1.1
  Accept: application/json

Ce Header doit être inclus dans *chaque* requête à l'API, et ne sera plus toujours explicitement indiqué dans les autres exemples.

Body
^^^^

Certains types de requêtes (``POST`` et ``PATCH``) nécessitent des informations supplémentaires, qui sont transmises sous forme de Request-Body en format JSON. La forme exacte que doit prendre le contenu de ce Request-Body est décrit dans le chapitre :ref:`operations`.

------


Response
--------

Lorsque une Response a un Body, ce dernier est toujours un document JSON:

**Exemple de réponse**:

.. sourcecode:: http

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
      "@context": "http://www.w3.org/ns/hydra/context.jsonld",
      "@id": "https://example.org/ordnungssystem/fuehrung/dossier-23",
      "@type": "opengever.dossier.businesscasedossier",
      "title": "Titel des Objekts",
      "review_state": "dossier-state-active",
       "...": "..."
   }

`(Abrégée - les paragraphes suivants contiennent des exemples complets de réponses)`

Les keys préfixée avec un ``@`` ont une signification particulère, et ne correspondent pas à un champ sur ce type de contenu. Il s'agit de métadonnées JSON-LD_
(Linked Data):

============= ================= ===============================================
Key           Signification     Description
============= ================= ===============================================
``@context``  Contexte          A toujours la même valeur, une URI vers le
                                contexte Hydra. Cette key n'est actuellement
                                pas de relevante pour l'API de OneGov GEVER.

``@id``       URL univoqiue     L'URL univoque vers un objet.

``@type``     Type d'object     Le type d'une object. Ce type correspond à l'un
                                des :ref:`content-types` définis ci-dessous et
                                permet au client de savoir à quels champs de
                                quel type s'attendre dans une réponse.
============= ================= ===============================================


Pour les types d'objets qui ont un Workflow, il existe, en plus des attributs JSON-LD listés ci-dessus, une propriété générique ``review_state``, qui contient le Workflow-State (état de l'objet) actuel:

================= ================= ===============================================
Key               Signification     Description
================= ================= ===============================================
``review_state``  Workflow-State    Ce champ contient le Worflow-State actuel si
                                    l'objet possède un Workflow.
================= ================= ===============================================

Voir :ref:`Workflow <workflow>` pour des détails concernant les Workflows.


.. _RESTful: https://fr.wikipedia.org/wiki/Representational_State_Transfer
.. _HTTP: https://fr.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. _JSON-LD: http://json-ld.org/

.. disqus::
