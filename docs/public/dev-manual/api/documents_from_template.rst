Dokumente aus Vorlagen
======================

Gever unterstützt diverse Vorlagensysteme.

OneOffix
========

Das OneOffixx Vorlagensystem muss korrekt angebunden werden und das Feauture ``oneoffixx`` muss aktiviert sein.

Erstellen eines Dokuments von einer OneOffixx Vorlage
-----------------------------------------------------

Ein Dokument aus einer OneOffixx Vorlage wird in zwei Schritten erstellt. In einem ersten Schritt wird das Dokument mit allen Metadaten und einen Verweis auf eine OneOffixx-Vorlage über ein ``POST`` auf den ``@document_from_oneoffixx`` Endpoint erstellt. Der Endpoint unterstützt alle Metadaten, die ein normales Dokument auch unterstützt.

**Beispiel-Request:**

  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@document_from_oneoffixx HTTP/1.1
    Accept: application/json

    {
    "document": {"title": "My OneOffixx Document"},
     "template_id": "xyz"
    }


Als Antwort erhält der Konsument eine Office-Connector URL welche im Browser aufgerufen werden kann. Der Office-Connector öffnet nun die vorher referenzierte Vorlage.

**Beispiel-Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://nohost/plone/ordnungssystem/dossier-23/document-44",
        "url": "oc:token"
      }

OneOffixx Vorlagen auflisten
----------------------------

OneOffixx Vorlagen, Gruppen und Favoriten können über den Endpoint `@oneoffixx-templates` abgefragt werden:


**Beispiel-Request:**

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/@oneoffixx-templates HTTP/1.1
    Accept: application/json

**Beispiel-Response:**

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "favorites": [
            {
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "filename": "3 Example Word file.docx",
                "template_id": "2574d08d-95ea-4639-beab-3103fe4c3bc7",
                "title": "3 Example Word file"
            }
        ],
        "groups": [
            {
                "group_id": "c2ddc01a-befd-4e0d-b15f-f67025f532be",
                "templates": ["2574d08d-95ea-4639-beab-3103fe4c3bc7"],
                "title": "Word templates"
            },
            {
                "group_id": "c2ddc01a-befd-4e0d-b15f-f67025f532bf",
                "templates": ["2574d08d-95ea-4639-beab-3103fe4c3bc8"],
                "title": "Excel templates"
            },
            {
                "group_id": "c2ddc01a-befd-4e0d-b15f-f67025f532c0",
                "templates": ["2574d08d-95ea-4639-beab-3103fe4c3bc9"],
                "title": "Powerpoint template folder"
            }
        ],
        "templates": [
            {
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "filename": "3 Example Word file.docx",
                "template_id": "2574d08d-95ea-4639-beab-3103fe4c3bc7",
                "title": "3 Example Word file"
            },
            {
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "filename": "2 Example Excel file.xlsx",
                "template_id": "2574d08d-95ea-4639-beab-3103fe4c3bc8",
                "title": "2 Example Excel file"
            },
            {
                "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "filename": "1 Example Powerpoint presentation.pptx",
                "template_id": "2574d08d-95ea-4639-beab-3103fe4c3bc9",
                "title": "1 Example Powerpoint presentation"
            }
        ]
      }
