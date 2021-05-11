.. _upload-structure:

Dossier und Dokumente hochladen
===============================

Der ``@upload-structure`` Endpoint kann verwendet werden um zu überprüfen ob der Upload von Datein möglich ist. Eine Liste von relativen Pfade muss im ``files`` Parameter mitgegeben werden. Der Endpoint berechnet die Struktur von Dossiers und Dokumente welche erstellt werden müsste um die ``files`` Liste in GEVER zu erstellen.
Der Endpoint überprüft auch ob es mögliche Dupplikate für die Dokumente in der ``files`` Liste gibt.


  .. sourcecode:: http

    POST /ordnungssystem/dossier-23/@upload-structure HTTP/1.1
    Accept: application/json

    {
        "files": ["folder/file.txt", "folder/subfolder/mail.msg"]
    }


  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "items": {
            "folder": {
                "@type": "opengever.dossier.businesscasedossier",
                "is_container": true,
                "items": {
                    "file.txt": {
                        "@type": "opengever.document.document",
                        "is_container": false,
                        "relative_path": "folder/file.txt"
                    },
                    "subfolder": {
                        "@type": "opengever.dossier.businesscasedossier",
                        "is_container": true,
                        "items": {
                            "mail.msg": {
                                "@type": "ftw.mail.mail",
                                "is_container": false,
                                "relative_path": "folder/subfolder/mail.msg"
                            }
                        },
                        "relative_path": "folder/subfolder"
                    }
                },
                "relative_path": "folder"
            }
        },
        "items_total": 4,
        "max_container_depth": 2
        "possible_duplicates": {
            "test.docx": [
                {
                    "@id": "/ordnungssystem/dossier-23/dossier-24/document-90",
                    "@type": "opengever.document.document",
                    "filename": "file.txt",
                    "title": "file"
                }
            ]
    }
    }

Wenn die Erstellung dieser Struktur nich möglich wäre, zum Beispiel wegen Berechtigungen, Subdossier Tiefe oder weil im Gewünschtem Kontext keine Dossiers / Dokumente erstellt werden können, dann wird mit ``400 Bad Request`` geantwortet.

  .. sourcecode:: http

    POST /ordnungssystem/@upload-structure HTTP/1.1
    Accept: application/json

    {
        "files": ["file.txt"]
    }


  .. sourcecode:: http

    HTTP/1.1 400 Bad Request
    Content-Type: application/json

    {
        "message": "Some of the objects cannot be added here",
        "type": "BadRequest"
    }

