Recherche
=========

Il est possible re rechercher des contenus dans GEVER à l'aide de l'Endpoint ``/@search``:

.. sourcecode:: http

  GET /plone/@search HTTP/1.1
  Accept: application/json

Par défaut, une recherche est **contextuelle**, ce qui veut dire que seuls les contenus de la ressource sur laquelle ``@search`` a été exécuté seront parcourus. Si ``@search`` est par exemple exécuté sur un dossier, la recherche couvrira tous les objets qui se trouvent dans ce dossier (y compris l'objet lui-même). 

Si ``/@search`` est exécuté à la racine du client GEVER, la recherche sera globale, puisque tous les objets se trouvent directement ou indirectement sous celle-ci.

Les résultats de recherche sont affichés au même format que les contenus dans des objets de type dossier:

.. literalinclude:: examples/search.json
   :language: http

La représentation standard d'un résultat de recherche est un bref résumé des propriétés les plus importantes de l'objet. Pour retourner des attributs additionnels provenant du catalogue de recherche, il faut utiliser le paramètre ``metadata_fields`` décrit plus bas. 

.. note::
        Les résultats de recherche sont **paginés** lorsque le nombre de résultats dépasse la taille de page prévue (25 par défaut). Pour plus de détails concernant la gestion de résultats paginés, voir :doc:`batching`. 


Format de requête
-----------------

Les requêtes (queries) et options de recherche sont transmis à la request en tant que paramètres strings de requête, par l'intermédiaire de ``/@search``:

.. sourcecode:: http

  GET /plone/@search?SearchableText=lorem HTTP/1.1


``SearchableText`` fait référence au soi-disant **index**. Un index est une structure de données maintenant une liste d'informations concernant les objets optimisé pour la recherche. Pour pouvoir chercher sur une propriété ou un attribut d'objet spécifique, un index qui y est spécifique doit exister. 

L'index ``SearchableText`` est l'un des index le plus utilisés et est conçu pour la recherche plein-texte. Cet index contient donc une liste de tous les termes par lesquels l'objet doit être trouvable via la recherche plein-texte:

Titre et description, métadonnées GEVER importantes tel que les Numéros de classement et de dossiers, et pour les documents, le contenu textuel extrait de chaque fichier. 

Autres index utilisés couramment:

================ =============================================================
Index            Description
================ =============================================================
``Title``        Titre
``Description``  Description
``path``         Chemin (p.ex. ``/fd/plandeclassment/general/dossier-27``)
``portal_type``  Type de l'objet, voir :ref:`Types d'objets <content-types>`
``reference``    No de classement (p.ex. ``FD 0.0.0 / 1 / 39``)
``modified``     Date/heure de la dernière modification
================ =============================================================

Une requête de recherche complexe peut être composée à partir d'une combinaison de filtres sur plusieurs indexes. Par exemple, pour ne rechercher que des documents contenant le terme "décision", la requête suivante peut être utilisée:

.. sourcecode:: http

  GET /plone/@search?SearchableText=décision&portal_type=opengever.document.document HTTP/1.1


Métadonnées Additionnelles
--------------------------
Par défaut, les résultats de recherche sont présentés comme un bref résumé des propriétés les plus importantes de l'objet.

Pour inclure des métadonnées additionnelles directement dans les résultats de recherche, celles-ci peuvent être demandées par l'intermédliaire de l'option ``metadata_fields``:

.. sourcecode:: http

  GET /plone/@search?SearchableText=lorem&metadata_fields=modified HTTP/1.1

Pour représenter directement *toutes* les données disponibles dans le catalogue de recherche, il est possibe d'utiliser ``metadata_fields=_all``.

.. note::
   L'utilisation du paramètre ``metadata_fields`` implique une familiarité avec les noms d'index internes et devrait être utilisé après consultation de 4teamwork. Pour la :ref:`liste succincte pour l'utilisation de GET requests <summaries>`, il existe un mécanisme séparé.

   Il existe également les paramètres ``preview_image_url`` et ``preview_pdf_url``, qui ne représentent pas réellement des métadonnées
   

Recherche Solr
--------------
L'Endpoint ``@solrsearch`` est à disposition pour soumettre directement une recherche au service Solr. pour la requête, il faut la syntaxe de l'API SOLR et ses paramètres. L'Endpoint retourne une liste des résultats avec les champs définis par le paramètre ``fl``. Les paramètres suivants sont actuellement supportés par l'Endpoint:



Query
~~~~~
``q``: Expression recherchée

Exemple pour la recherche de "Court":

.. sourcecode:: http

  GET /plone/@solrsearch?q=Court HTTP/1.1

L'expression de recherche peut également être soumise en syntaxe Solr Query avec le paramètre ``q.raw``.

Exemple pour la recherche de "Court" Dans le champ "Title":

.. sourcecode:: http

  GET /plone/@solrsearch?q.raw=Title:Court HTTP/1.1


Filters
~~~~~~~
``fq``: Filtrer selon une valeur spécifique du champ. 

Exemple d'une recherche filtrés selon portal_type uniquement sur les documents et dossiers. 


.. sourcecode:: http

  GET /plone/@solrsearch?fq=portal_type:(opengever.document.document%20OR%20opengever.dossier.businesscasedossier) HTTP/1.1


Fields
~~~~~~
``fl``: Liste des champs qui doivent être retournées. Par défaut, les champs ``@id``, ``@type``, ``title``, ``description`` et ``review_state`` sont retournés.

Exemple pour une recherche retournant UID, Title et numéro de séquence

.. sourcecode:: http

  GET /plone/@solrsearch?q=Court&fl=UID,Title,sequence_number HTTP/1.1


Autres paramètres optionnels:

- ``start``: Le premier élément à retourner
- ``rows``: Le nombre maximal d'éléments à retourner
- ``sort``: Tri selon un champ indexé


Facettes
~~~~~~~~
``facet``: Doit être défini en tant que ``true`` pour que Solr retourne les facettes.
``facet.field``: Champ pour lequel Solr doit retourner des facettes.

Exemple pour une recherche avec des facettes pour ``responsible`` et ``portal_type``:

  .. sourcecode:: http

    GET /plone/@solrsearch?facet=true&facet.field=portal_type&facet.field=responsible HTTP/1.1

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "/plone/@solrsearch?facet=true&facet.field=portal_type&facet.field=responsible",
      "facet_counts": {
        "portal_type": {
          "opengever.document.document": {
            "count": 2
          }
        },
        "responsible": {
          "committee:161": {
            "count": 2,
            "label": "Commission juridique"
          },
          "hugo.boss": {
            "count": 1,
            "label": "Hugo Boss"
          }
        }
      },
      "items": [
        {
          "@id": "/plone/ordnungssystem/direction/dossier-23/document-59",
          "filesize": 12303,
          "modified": "2019-03-11T13:50:14+00:00",
          "title": "Une Lettre"
        },
        {
          "@id": "/plone/ordnungssystem/direction/dossier-23/document-54",
          "filesize": 8574,
          "modified": "2019-03-11T12:32:24+00:00",
          "title": "Un Dossier"
        }
      ],
      "items_total": 2,
      "rows": 25,
      "start": 0
    }

.. disqus::
