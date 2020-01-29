sérialisation
=============

Dans la REST API, il est nécessaire sérialiser et désérialiser  le contenu de et vers JSON à plusieurs endroits. 

Fondamentalement, le format de la sérialisation (Lecture de l'API) est le même que pour la désérialisation (Écriture via l'API).

Types primitifs
---------------

Les types de données primitifs qui ont une représentation équivalente dans JSON, tels que les integers ou strings, sont directement traduits entre Python et JSON. Un string Python de GEVER est donc retourné comme un string JSON et vice-versa.

Date / Heure
------------

Comme JSON n'offre pas de support natif pour les datetimes, les datetimes Python/Zope sont sérialisées en strings `ISO 8601 <https://de.wikipedia.org/wiki/ISO_8601>`. La zone horaire utilisée lors de la sérialisation est toujours UTC et non pas l'heure locale.

============================================================================== ======================================
Python                                                                         JSON
============================================================================== ======================================
``time(19, 45, 55)``                                                           ``'19:45:55'``
``date(2015, 11, 23)``                                                         ``'2015-11-23'``
``datetime(2015, 11, 23, 19, 45, 55, tzinfo=pytz.timezone('Europe/Zurich'))``  ``'2015-11-23T18:45:55+00:00'``
``DateTime('2018/08/09 13:43:27.261730 GMT+2')``                               ``'2018-08-09T11:43:58+00:00'``
============================================================================== ======================================





Fichiers
--------

.. _label-api_download:

Download (sérialisation)
^^^^^^^^^^^^^^^^^^^^^^^^

Pour le téléchargement de fichiers, il faut sérialiser un file field pour un mapping. Celui-ci contiendra toutes les métadonnées concernant le fichier (mais pas le document) ainsi qu'un lien pour le téléchargement:

.. code:: json

      {
        "@id": "http://example.org/dossier/mydoc",
        "@type": "opengever.document.document",
        "title": "My document",
        "...": "",
        "file": {
          "content-type": "application/pdf",
          "download": "http://example.org/dossier/mydoc/@@download/file",
          "filename": "file.pdf",
          "size": 74429
        }
      }


l'URL de la propriété ``download`` affiche la download view standard sur Plone. Cela signifie que le client peut effectuer une requête ``GET`` sur cette URL pour télécharger le ficher. Toutefois, le header ``Accept`` ne peut ici plus être défini comme ``application/json`` (comme normalement sur une requête d'API), mais le MIME-Type du fichier à récupérer (selon la propriété ``content-type``).


Upload (Desérialisation)
^^^^^^^^^^^^^^^^^^^^^^^^^

Pour les champs fichier, le client doit envoyer le fichier et ses métadonnées en tant que mapping, semblable au mapping pour un téléchargement. Le mapping doit inclure les données encode en base64 dans la propriété ``Data``, ainsi que les métadonnées restantes dans les propriétés suivantes:


- ``data`` - le contenu du ficher, encodée en base64
- ``encoding`` - le type d'encodage utilisé, donc ``base64``
- ``content-type`` - le MIME-Type du fichier
- ``filename`` - le nom de fichier, y compris son extension

.. code:: json

      {
        "@type": "opengever.document.document",
        "title": "My file",
        "...": "",
        "file": {
            "data": "TG9yZW0gSXBzdW0uCg==",
            "encoding": "base64",
            "filename": "lorem.txt",
            "content-type": "text/plain"}
      }


Références
----------

Sérialisation
^^^^^^^^^^^^^

Les références sont sérialisées en une représentation sommaire des objets référencés:

.. code:: json

    {
      "...": "",
      "relatedItems": [
        {
          "@id": "http://example.org/dossier/doc1",
          "@type": "opengever.document.document",
          "title": "Document 1",
          "description": "Description"
        }
      ]
    }

La liste de références est sérialisée en une liste JSON simple.

Désérialisation
^^^^^^^^^^^^^^^

Diverses méthodes sont disponibles pour créer une références lors de la création ou la mise à jour d'objets. L'un des identifiants ci-dessous peut être utilisé pour identifier clairement la cible référencée.  

======================================= ======================================
Type                                     Exemple
======================================= ======================================
UID                                     ``'9b6a4eadb9074dde97d86171bb332ae9'``
IntId                                   ``123456``
Pfad                                    ``'/dossier/doc1'``
URL                                     ``'http://example.org/dossier/doc1'``
======================================= ======================================

.. disqus::
