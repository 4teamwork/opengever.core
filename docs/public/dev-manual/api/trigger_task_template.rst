.. _trigger_task_template:

Standardabläufe auslösen (deprecated, wurde mit :ref:`@process <process>`. ersetzt)
===================================================================================

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


Interaktive Auftragnehmer
-------------------------

Bei jeder ausgewählten Aufgabenvorlage kann der Auftragnehmer überschrieben
werden. Der Auftragnehmer kann durch einen interaktiven Benutzer ersetzt
werden. Es gibt dabei folgende Möglichkeiten:

- ``interactive_actor:current_user``: Der aktuelle Benutzer
- ``interactive_actor:responsible``:  Die Federführende Person des Dossiers, in dem die Aufgabe erstellt wird


**Beispiel-Request**:

   .. sourcecode:: http

        POST /ordnungssystem/fuehrung/dossier-23/@trigger-task-template HTTP/1.1
        Accept: application/json

        {
            "tasktemplatefolder": "67a25fc941354568950439f08f7af3ed",
            "tasktemplates": [
                {
                    "@id": "http://localhost:8080/fd/vorlagen/tasktemplatefolder-1/tasktemplate-1",
                    "responsible": "interactive_actor:current_user"
                }
            ],
            "start_immediately": false
        }


Titel, Beschreibung und Frist setzen
------------------------------------

Sowohl für die Hauptaufgabe wie auch für jede der ausgewählten Aufgabenvorlage
kann Titel, Beschreibung und Frist der Aufgabe überschrieben werden. Dafür stehen
folgende Felder zur Verfügung:

- ``title``: Setzt den Titel der Aufgabe (Default: Titel der Vorlage)
- ``text``:  Setzt die Beschreibung der Aufgabe (Default: Beschreibung
  der Vorlage, oder Leer für die Hauptaufgabe)
- ``deadline``: Setzt die Frist der Aufgabe (Default: Frist der Vorlage)


**Beispiel-Request**:

   .. sourcecode:: http

        POST /ordnungssystem/fuehrung/dossier-23/@trigger-task-template HTTP/1.1
        Accept: application/json

        {
            "tasktemplatefolder": "67a25fc941354568950439f08f7af3ed",
            "title": "Meine Aufgabe",
            "text": "Bitte sofort erledigen!",
            "tasktemplates": [
                {
                    "@id": "http://localhost:8080/fd/vorlagen/tasktemplatefolder-1/tasktemplate-1",
                    "deadline": "2025-12-10",
                    "responsible": "stv:david.erni",
                    "title": "Unteraufgabe",
                    "text": "Noch schneller erledigen!"
                }
            ],
            "related_documents": [
                {
                    "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/dossier-23/document-23515"
                }
            ],

            "start_immediately": true
        }

Struktur der Standardabläufe anzeigen
=====================================
Über den Endpint ``@task-template-structure`` kann die Struktur des Templatefolders angezeigt werden.



   **Beispiel-Request**:

   .. sourcecode:: http

      GET /vorlagen/tasktemplate-1/@task-template-structure HTTP/1.1
      Accept: application/json

   **Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "/vorlagen/tasktemplate-1/@task-template-structure",
        "@type": "opengever.tasktemplates.tasktemplatefolder",
        "UID": "fc1a5fd76afa41f4962f2660887c601c",
        "items": [
            {
                "@id": "/vorlagen/tasktemplate-1/aufgabe-2",
                "@type": "opengever.tasktemplates.tasktemplate",
                "UID": "480d0557a3ac43f0be76aa7f2a597aa6",
                "...": "..."
            },
            {
                "@id": "/vorlagen/tasktemplate-1/aufgabe-1",
                "@type": "opengever.tasktemplates.tasktemplate",
                "UID": "1c1752e49f024e4682cb632e40f6d78c",
                "...": "..."
            },
            {
                "@id": "/vorlagen/tasktemplate-1/@task-template-structure",
                "@type": "opengever.tasktemplates.tasktemplatefolder",
                "UID": "4a8ea261042949efb3abc3e706abf62c",
                "items": [
                    {
                        "@id": "/vorlagen/tasktemplate-1/aufgabengruppe-1-parallel/aufgabe-in-gruppe-1",
                        "@type": "opengever.tasktemplates.tasktemplate",
                        "UID": "54a26da5992148ce90f68a428817b065",
                        "...": "..."
                    },
                    {
                        "@id": "/vorlagen/tasktemplate-1/aufgabengruppe-1-parallel/aufgabe-in-gruppe-2",
                        "@type": "opengever.tasktemplates.tasktemplate",
                        "UID": "9090d410f9114628a2edcadaade2dc08",
                        "...": "..."
                    }
                ],
                "items_total": 2,
                "...": "..."
            }
        ],
        "items_total": 3,
        "...": "..."
      }
