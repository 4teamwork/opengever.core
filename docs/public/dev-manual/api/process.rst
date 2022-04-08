.. _process:

Prozess erstellen
=================

In einem Dossier kann mit dem Endpoint ``@process`` ein Prozess erstellt werden. Die Daten um ein Prozess zu erstellen können zum Beispiel von einem Standardablauf kommen.

Der Endpoint erwartet folgende Parameter:

- ``related_documents``: Optionale Verweise auf Dokumente/Mails
- ``start_immediately``: Erste Aufgabe nach Erstellung sofort starten
- ``process``: Daten des zu erstellenden Prozesses. Dies ist ein verschateltes Objekt, welches die Struktur des Prozesses abbildet. Es beinhaltet zwei Typen von Objekten:
  - Aufgaben Behälter. Benötigt ein ``title``, ``sequence_type`` (entweder ``parallel`` oder ``sequential``) und ``items`` (eine Liste von Aufgaben oder Aufgaben Behälter).
  - Aufgaben (Schema analog Aufgaben-Schema.)

Beim Erstellen werden aus Aufgaben Behälter neue Aufgaben mit Typ "zur direkten Erledigung" erstellt und der aktuelle Benutzer als Auftraggeber und Auftragnehmer hinzugefügt. Diese Aufgaben werden dann automatisch abgeschlossen wenn alle Unteraufgaben abgeschlossen sind.

**Beispiel-Request**:

   .. sourcecode:: http

        POST /ordnungssystem/fuehrung/dossier-23/@trigger-task-template HTTP/1.1
        Accept: application/json


        {
            "related_documents": [
                {
                    "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/dossier-23/document-23515"
                }
            ],
            "start_immediately": true,
            "process": {
                "title": "New employee",
                "text": "A new employee arrives.",
                "sequence_type": "sequential",
                "items": [
                    {
                        "title": "Assign userid",
                        "responsible": "fa:hugo.noss",
                        "issuer": "john.doe",
                        "deadline": "2022-03-01",
                        "task_type": "direct-execution",
                        "is_private": false,
                    },
                    {
                        "title": "Training",
                        "sequence_type": "parallel",
                        "items": [
                            {
                                "title": "Present Gever",
                                "responsible": "fa:john.doe",
                                "issuer": "hans.mueller",
                                "deadline": "2022-03-10",
                                "task_type": "direct-execution",
                                "is_private": false,
                            },
                            {
                                "title": "Present Teamraum",
                                "responsible": "fa:hugo.boss",
                                "issuer": "hans.mueller",
                                "deadline": "2022-03-12",
                                "task_type": "direct-execution",
                                "is_private": false,
                            },
                        ]
                    }
                ]
            }
        }

Als Response wird die JSON-Repräsentation der neu erstellten Aufgabe geliefert,
siehe :ref:`Inhaltstypen <content-types>`.


Interaktive Auftragnehmer
-------------------------

Interaktiven Benutzer sind als Auftragnehmer und Auftraggeber unterstützt. Es gibt dabei folgende Möglichkeiten:

- ``interactive_actor:current_user``: Der aktuelle Benutzer
- ``interactive_actor:responsible``:  Die Federführende Person des Dossiers, in dem die Aufgabe erstellt wird
