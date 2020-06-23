.. _trigger_task_template:

Standardabläufe auslösen
========================

In einem Dossier kann mit dem Endpoint ``@trigger-task-template`` ein
bestehender Standardablauf ausgelöst werden.

Der Endpoint erwartet folgende Parameter:

- ``tasktemplatefolder``: Das zu verwendende Template aus dem Vokabular ``opengever.dossier.DocumentTemplatesVocabulary``
- ``tasktemplates``: zu verwendende Aufgabenvorlagen und optional Auftragnehmer der zu erstellenden Aufgabe
- ``related_documents``: Optionale Verweise auf Dokumente/Mails
- ``start_immediately``: Erste Aufgabe nach Erstellung sofort starten


**Beispiel-Request**:

   .. sourcecode:: http

        POST /ordnungssystem/fuehrung/dossier-23/@trigger-task-template HTTP/1.1
        Accept: application/json

        {
            "tasktemplatefolder": "67a25fc941354568950439f08f7af3ed",
            "tasktemplates": [
                {
                    "@id": "http://localhost:8080/fd/vorlagen/tasktemplatefolder-1/tasktemplate-1",
                    "responsible": "stv:david.erni"
                }
            ],
            "related_documents": [
                {
                    "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/dossier-23/document-23515"
                }
            ],
            "start_immediately": true
        }


Als Response wird die JSON-Repräsentation der neu erstellten Aufgabe geliefert,
siehe :ref:`Inhaltstypen <content-types>`.
