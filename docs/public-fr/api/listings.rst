.. listings:

Listings
========

L'Endpoint ``@listing`` permet de créer de listes tabulées contenant les champs `Titre`, `Date de modification` et `Taille de fichier`:

  .. sourcecode:: http

    GET /ordnungssystem/direction/dossier-23/@listing?name=documents&columns:list=title&columns:list=modified&columns:list=filesize HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/direction/dossier-23/@listing?name=documents&columns%3Alist=title&columns%3Alist=modified&columns%3Alist=filesize",
      "b_size": 25,
      "b_start": 0,
      "items": [
        {
          "@id": "http://localhost:8080/fd//ordnungssystem/direction/dossier-23/document-59",
          "filesize": 12303,
          "modified": "2019-03-11T13:50:14+00:00",
          "title": "Une lettre"
        },
        {
          "@id": "http://localhost:8080/fd//ordnungssystem/direction/dossier-23/document-54",
          "filesize": 8574,
          "modified": "2019-03-11T12:32:24+00:00",
          "title": "Un Dossier"
        }
      ],
      "items_total": 2
    }

Le type de listing est déterminé par l'intermédiaire du paramètre ``name``. Couramment,  les listings suivants sont supportés:

- ``dossiers``: Dossiers
- ``documents``: Documents
- ``workspaces``: Espaces de travail
- ``workspace_folders``: Dossier d'espace de travail
- ``tasks``: Tâches
- ``todos``: ToDos teamraum
- ``proposals``: Requêtes
- ``contacts``: Contacts locaux


Pour chaque listing, il es possible de récupérer différents champs. Voici la liste complète des champs disponibles:

- ``bumblebee_checksum``: Checksum SHA-256
- ``changed``: Date de modification
- ``checked_out``: Nom d'utilisateur de la personne qui a effectué le check-out sur le document
- ``checked_out_fullname``: Nom complet de la personne qui a effectué le check-out sur le document
- ``completed``: Indique si la tâche a été complétée.
- ``containing_dossier``: Titre du dossier principal contenant l'élément.
- ``containing_subdossier``: Titre du sous-dossier contenant l'élément.
- ``created``: Date de création
- ``creator``: Créateur
- ``deadline``: Délai pour la tâche
- ``delivery_date``: Date de sortie
- ``description``: Description
- ``document_author``: Auteur du document
- ``document_date``: Date du document
- ``document_type``: Type de document
- ``end``: Date de fin du dossier
- ``file_extension``: Extension du fichier
- ``filename``: Nom de fichier
- ``filesize``: Taille de fichier
- ``has_sametype_children``: Indique s'il contient des objets du même type de contenu.
- ``issuer_fullname``: Mandant (nom complet)
- ``issuer``: Mandataire (nom d'utilisateur)
- ``is_subdossier``: Indique s'il s'agit d'un sous-dossier.
- ``is_sutask``: Indique s'il s'agit d'une sous-tâche.
- ``keywords``: Mots-clés
- ``mimetype``: Mimetype
- ``modified``: Date de modification
- ``pdf_url``: URL le l'aperçu PDF
- ``preview_url``: URL pour l'aperçu
- ``receipt_date``: Date d'entrée
- ``reference``: Référence
- ``reference_number``: No de dossier
- ``relative_path``: Chemin
- ``responsible``: Responsable (nom d'utilisateur)
- ``responsible_fullname``: Responsable (nom complet)
- ``review_state``: État
- ``review_state_label``: État (Valeur d'affichage)
- ``sequence_number``: No de séquence
- ``start``: Date de début du dossier
- ``task_type``: Type de tâche
- ``thumbnail_url``: URL pour la vignette d'aperçu
- ``title``: Titre
- ``type``: Type de contenu
- ``@type``: Type de contenu
- ``UID``: UID de l'objet
- ``firstname``: Prénom
- ``lastname``: Nom
- ``email``: Adresse e-mail
- ``phone_office``: No de téléphone

Selon les types de listing et contenu, certains champs de sont pas disponibles. Dans ces cas, la valeur ``none`` est retournée. Dans ce sens, les dossiers n'ont p.ex. pas de nom de fichier. 

Table de référence:


.. table::

    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    | Feld                     | Document | Dossier | Esp. de trav. | Dossier esp. trav. |  Tâche  |  ToDo   | Requêtes | Contacts |
    +==========================+==========+=========+===============+====================+=========+=========+==========+==========+
    |``bumblebee_checksum``    |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``changed``               |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``checked_out``           |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``checked_out_fullname``  |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``completed``             |   non    |   non   |      non      |        non         |   oui   |   oui   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``containing_dossier``    |   oui    |   oui   |      non      |        non         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``containing_subdossier`` |   oui    |   oui   |      non      |        non         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``created``               |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``creator``               |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``deadline``              |   non    |   non   |      non      |        non         |   oui   |   oui   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``delivery_date``         |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``description``           |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``document_author``       |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``document_date``         |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``document_type``         |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``end``                   |   non    |   oui   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``file_extension``        |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``filename``              |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``filesize``              |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``has_sametype_children`` |   non    |   oui   |      oui      |        oui         |   oui   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``issuer_fullname``       |   non    |   non   |      non      |        non         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``is_subdossier``         |   non    |   oui   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``is_subtask``            |   non    |   non   |      non      |        non         |   oui   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``keywords``              |   oui    |   oui   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``mimetype``              |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``modified``              |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``pdf_url``               |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``preview_url``           |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``receipt_date``          |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``reference``             |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``reference_number``      |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``relative_path``         |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``responsible``           |   non    |   oui   |      non      |        non         |   oui   |   oui   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``responsible_fullname``  |   non    |   oui   |      non      |        non         |   oui   |   oui   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``review_state``          |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``review_state_label``    |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``sequence_number``       |   oui    |   oui   |      oui      |        oui         |   oui   |   non   |   oui    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``start``                 |   non    |   oui   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``task_type``             |   non    |   non   |      non      |        non         |   oui   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``thumbnail_url``         |   oui    |   non   |      non      |        non         |   non   |   non   |   non    |   non    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``title``                 |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``type``                  |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``@type``                 |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+
    |``UID``                   |   oui    |   oui   |      oui      |        oui         |   oui   |   oui   |   oui    |   oui    |
    +--------------------------+----------+---------+---------------+--------------------+---------+---------+----------+----------+


Paramètres optionnels:
----------------------

- ``b_start``: Le premier élément à retourner
- ``b_size``: Le nombre maximal d'éléments à retourner
- ``sort_on``: Tri selon un champ indexé
- ``sort_order``: Séquence de tri: ``ascending`` (croissant) oder ``descending`` (décroissant)
- ``search``: Filtrage selon un terme de recherche arbitraire
- ``columns``: Liste des champs à retourner.
- ``filters``: Limitation selon une valeur spécifique d'un champ
- ``depth``: Limitation de la profondeur maximale de chemin (relatif au contexte):

  - ``1``: Uniquement les enfants situés directement sous le contexte. 
  - ``2``: enfants directs, et leurs enfants directs. 
  - etc.
- ``facets``: Pour les champs retournant des facettes plages de valeurs.


**Exemple: Tri selon la date de modification, documents les plus récents en premier:**

  .. sourcecode:: http

    GET /ordnungssystem/direction/dossier-23/@listing?name=documents&sort_on=changed&sort_order=descending HTTP/1.1
    Accept: application/json



**Exemple: Filtrer par dossier clôturés et archivés:**

  .. sourcecode:: http

    GET /ordnungssystem/direction/dossier-23/@listing?name=documents&sort_on=modified&filters.review_state:record:list=dossier-state-resolved&filters.review_state:record:list=dossier-state-archived HTTP/1.1
    Accept: application/json

**Exemple: Filtrer par dossiers ayant une date de début située entr les 20.08.2018 et 20.09.2019:**

  .. sourcecode:: http

    GET /ordnungssystem/direction/dossier-23/@listing?name=documents&sort_on=modified&filters.start:record=2018-08-20TO2018-09-20 HTTP/1.1
    Accept: application/json

**Exemple: Également rertourner les plages de valeurs du créateur:**

  .. sourcecode:: http

    GET /ordnungssystem/direction/dossier-23/@listing?name=documents&facets:list=creator HTTP/1.1
    Accept: application/json
