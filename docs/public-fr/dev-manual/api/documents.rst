Documents
=========

Il faut également réspécter le cycle Checkin/Checkout pour éditer un document via la REST-API.

La séquence suivante est prévue:

    1. :ref:`Checkout <label-api_checkout>`
    #. :ref:`Lock <label-api_lock>`
    #. :ref:`Download <label-api_download>`
    #. :ref:`Upload <label-api_upload>`
    #. :ref:`Unlock <label-api_unlock>`
    #. :ref:`Checkin <label-api_checkin>`

On peut interrompre ce Workflow en annulatn le checkout via le :ref:`@cancelcheckout <label-api_cancelcheckout>` endpoint.

On peut lister les versions d'un document avec le :ref:`@history <label-api_history>` Endpoint.

.. _label-api_checkout:

Checkout - Faire le checkout d'un document
------------------------------------------
Le checkout d'un document se fait via le ``@checkout`` endpoint.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@checkout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 204 No Content

Darf ein Dokument vom aktuellen Benutzer nicht ausgecheckt werden, so wird mit dem Status ``403 Forbidden`` geantwortet.

  .. sourcecode:: http

    POST /ordnungssystem/fuehrung/dossier-23/document-123/@checkout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 403 Forbidden
    Content-Type: application/json

    {
        "error": {
            "message": "Checkout is not allowed.",
            "type": "Forbidden"
        }
    }


Lock
----
Pour éviter que le document ne puisse être modifié par d'autres utilisateurs, il doit être verouillé par un Lock.

.. _label-api_lock:

Lock erstellen
~~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@lock HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 600,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }

Les verrous ont normalement un Timeout de 600 secondes et doivent ensuite être renouvelés. Il faut donc soit renouveler le verrou périodiquement, soit utiliser un timeout plus élevé:

Renouveler un verrou
~~~~~~~~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@refresh-lock HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 600,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }


Vérouiller avec un timeout personalisé
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@lock HTTP/1.1
    Accept: application/json

    {
        "timeout": 86400
    }


  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "creator": "peter.meier",
      "locked": true,
      "name": "plone.locking.stealable",
      "stealable": true,
      "time": 1477076400.0,
      "timeout": 86400,
      "token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"
    }


.. _label-api_unlock:

Enlever un verrou
~~~~~~~~~~~~~~~~~

Un verrou existant peut être enlevé vie le ``@unlock`` endpoint.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@unlock HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "locked": false,
        "stealable": true
    }


.. _label-api_upload:

Actualiser le fichier
---------------------
La REST API supporte le TUS Protocol pour l'upload d'un fichier. Une documentation détaillée se trouve dans la `documentation de plone.restapi <https://plonerestapi.readthedocs.io/en/latest/tusupload.html>`_.

Voici un exemple de comment actualiser le fichier d'un document existant.

Créer l'URL pour l'upload:

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@tus-replace HTTP/1.1
    Accept: application/json
    Tus-Resumable: 1.0.0
    Upload-Length: 8
    Upload-Metadata: filename dGVzdC50eHQ=,content-type dGV4dC9wbGFpbg==


  .. sourcecode:: http

    HTTP/1.1 201 created
    Content-Type: application/json
    location: ordnungssystem/ressourcen-und-support/personal/personalrekrutierung/dossier-4/document-2/@tus-upload/6cdfc5ddd1844e8cbca32721c4b17b84


Uploader le fichier:

  .. sourcecode:: http

      PATCH /ordnungssystem/dossier-23/document-123/@tus-upload/6cdfc5ddd1844e8cbca32721c4b17b84 HTTP/1.1
      Accept: application/json
      Tus-Resumable: 1.0.0
      Upload-Offset: 0
      Content-Type: application/offset+octet-stream

      test data

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json


.. _label-api_checkin:

Checkin - Faire le checkin d'un document
----------------------------------------
Le checkin d'un document se fait via le ``@checkin`` Endpoint, ce qui crée automatiquement une nouvelle version du document.

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@checkin HTTP/1.1
    Accept: application/json

    {
        "comment": "Kapitel 3 - 6 korrigiert."
    }

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json


.. _label-api_cancelcheckout:

Cancel checkout - Annuler le checkout
-------------------------------------

Le checkout d'un document peut être annulé avec le ``@cancelcheckout`` Endpoint.

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/document-123/@cancelcheckout HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 204 No Content


.. _label-api_history:

Lister les Versions
-------------------

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/document-123/@history HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    [
        {
            "@id": "/ordnungssystem/dossier-23/document-123/@history/1",
            "action": "Bearbeitet",
            "actor": {
                "@id": "http://localhost:8080/fd/@users/peter.meier ",
                "fullname": "Peter Meier",
                "id": "peter.meier",
                "username": "peter.meier"
            },
            "comments": null,
            "may_revert": true,
            "time": "2019-03-27T10:50:59.196843",
            "transition_title": "Bearbeitet",
            "type": "versioning",
            "version": 1
        },
        {
            "@id": "/ordnungssystem/dossier-23/document-123/@history/0",
            "action": "Bearbeitet",
            "actor": {
                "@id": "http://localhost:8080/fd/@users/hugo.boss",
                "fullname": "Hugo Boss",
                "id": "hugo.boss",
                "username": "hugo.boss"
            },
            "comments": "Dokument erstellt (Initialversion)",
            "may_revert": true,
            "time": "2019-03-27T09:19:25",
            "transition_title": "Bearbeitet",
            "type": "versioning",
            "version": 0
        }
    ]
