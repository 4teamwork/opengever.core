.. _batching:

Pagination
==========

La pagination (aussi appelé *Batching*) désigne la spéparation des résultats en plusieurs pages (lots), pour éviter d'encombrer innutilement le serveur et de maintenir la taille de la réponse sous contrôle.

La représentation de ressources de type collection sont paginée par l'API lorsque le nombre de résultats dépasse la taille de lot (batch-size) choisie (25 par défault).

.. code:: json

    {
      "@id": "http://example.org/dossier/@search",
      "batching": {
        "@id": "http://example.org/dossier/@search?b_size=10&b_start=20",
        "first": "http://example.org/dossier/@search?b_size=10&b_start=0",
        "last": "http://example.org/dossier/@search?b_size=10&b_start=170",
        "prev": "http://example.org/dossier/@search?b_size=10&b_start=10",
        "next": "http://example.org/dossier/@search?b_size=10&b_start=30"
      },
      "items": [
        "..."
      ],
      "items_total": 175,
    }

La taille de lot peut être contrôlée par request avec le Query-String Parameter ``b_size``.

Des liens hypermedia pour la navigation vers les pages sont contenus dans la Top-Level Property ``batching`` lorsque les résultats ont dû être divisés en plusieurs lots.

Si au contraire tous les résultats tiennent sur une page, la Top-Level Property ``batching`` sera absente de la réponse.


Top-level Properties
--------------------

================ ===========================================================
Property         Description
================ ===========================================================
``@id``          URL de base canonique pour la resource correspondante sans
                 aucun paramètre de batching
``items``        Batch contenant les résultats de la page actuelle
``items_total``  Nombre total de résultats
``batching``     Liens hypermedia pour la navigation des batches
================ ===========================================================


Batching links
--------------

Si les résultats sont repartis sur plusieurs pages, la Response-Body contiendra au premier niveau la propriété ``batching``, qui contient des liens hypermedia pour la navigation des batches. Ces liens peuvent être utilisés par le client pour naviguer les pages de résultats:

================ ===========================================================
Attribute        Description
================ ===========================================================
``@id``          Lien vers la page actuelle
``first``        Lien vers la première page
``prev``         Lien vers la page précédente (*si disponible*)
``next``         Lien vers la page suivante (*si disponible*)
``last``         Lien vers la dernière page
================ ===========================================================


Paramètres
----------

La pagination peut être contrôlée à l'aide de deux paramètres (Query-String parameters).
Le paramètre ``b_start`` est utilisé pour adresser une certaine page, alors que ``b_size`` détermine le nombre (maximal) de résultats par page.

================ ===========================================================
Paramètre        Description
================ ===========================================================
``b_size``       Nombre de résultats par page (25 par défaut)
``b_start``      Premier résultat par lequelle la page doit commencer
================ ===========================================================


Exemple complet d'une réponse avec pagination:

.. sourcecode:: http

    GET /dossier/@search?b_size=5&sort_on=path HTTP/1.1
    Accept: application/json


.. literalinclude:: examples/batching.json
   :language: http

.. disqus::
