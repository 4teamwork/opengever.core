.. _recently_touched:

Documents récemment  édités
===========================

L'Endpoint ``@recently-touched`` retourne les informations utilisées pour le rendu du menu concernant les documents récemment édités, et ne peut être appelé que pour l'utilisateur courant.

L'URL est construite de la manière suivante:

``http://example.org/fd/@recently-touched/peter.mueller``


Listing:
--------
Les documents récemment édités par l'utilisateur courant peuvent être listés à l'aide d'une Request GET. La Response contient un Dictionary avec 2 listes distinctes:

- ``"checked_out"`` - Les documents actuellement en check-out chez l'utilisateur (tous).
- ``"recently_touched"`` - Les documents les plus récemment édités par l'utilisateur.
  Les documents se trouvant actuellement en check-out ne sont *pas* listés une seconde fois ici. La longueur de cette liste est limitée à un nombre maximal (10 par défaut).

**Exemple de Request**:

   .. sourcecode:: http

       GET /@recently-touched/peter.mueller HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "checked_out": [
          {
            "icon_class": "icon-dokument_word is-checked-out-by-current-user",
            "description": "Wichtige Dokumentation",
            "last_touched": "2018-05-31T15:40:23+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/direction/gemeinderecht/dossier-25/document-197",
            "@type": "opengever.document.document",
            "title": "Directives sur la protection des données",
            "review_state": "Directives sur la protection des données.docx",
          },
          {
            "icon_class": "icon-dokument_excel is-checked-out-by-current-user",
            "description": "",
            "last_touched": "2018-05-31T15:40:01+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/direction/gemeinderecht/dossier-25/document-191",
            "@type": "opengever.document.document",
            "title": "Bilanz Muster AG 2018",
            "review_state": "Directives sur la protection des données.docx",
          }
        ],
        "recently_touched": [
          {
            "icon_class": "icon-dokument_powerpoint is-checked-out",
            "description": "",
            "last_touched": "2018-05-31T15:35:38+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/direction/gemeinderecht/dossier-18/document-229",
            "@type": "opengever.document.document",
            "title": "Pra\u0308sentation - Firmenprofil Muster AG",
            "review_state": "Directives sur la protection des données.docx",
          },
          {
            "...": ""
          },
          {
            "icon_class": "icon-dokument_word",
            "description": "",
            "last_touched": "2018-05-31T15:34:42+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/direction/gemeinderecht/dossier-18/document-236",
            "@type": "opengever.document.document",
            "title": "Anfrage Drei"
            "review_state": "Directives sur la protection des données.docx",
          }
        ]
      }

La représentation des documents correspond à la :ref:`Représentation sommaire de contenus <summaries>`, telle qu'elle est aussi utilisée dans d'autres champs. Elle supporte également le paramètre ``metadata_fields``, Permettant de récupérer des champs additionnels.
