Aufgaben
========

Auch Aufgaben können via REST API bedient werden. Die Erstellung einer Aufgabe erfolgt wie bei anderen Inhalten (siehe Kapitel :ref:`operations`) via POST request:


**Beispiel-Request**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.task.task",
        "title": "Bitte Dokument reviewen",
        "responsible": "john.doe",
        "issuer": "john.doe",
        "responsible_client": "afi",
        "task_type": "direct-execution"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5",
        "@type": "opengever.task.task",
        "...": "..."
      }


Bearbeitung bzw. Statusänderungen
---------------------------------


Die Bearbeitung einer Aufgabe via Patch Request ist limitiert und nur möglich solange sich die Aufgabe im Status `offen` befindet. Im weiteren Verlauf einer Aufgabe werden diese auschliesslich via Statusänderungen bearbeitet. Dies geschieht über den ``@workflow`` Endpoint mit entsprechender Transition ID als zusätzlicher Parameter.

Ein GET Request auf den @workflow endpoint listet mögiche Transitions auf:

**Beispiel-Request**:

   .. sourcecode:: http

      GET /(path)/@workflow HTTP/1.1
      Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@workflow",
        "history": [],
        "transitions": [
          {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@workflow/task-transition-modify-deadline",
          "title": "Frist ändern"
          },
          {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@workflow/task-transition-open-in-progress",
          "title": "Akzeptieren"
          },
          {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@workflow/task-transition-reassign",
          "title": "Neu zuweisen"
          }
        ]
      }


Eine Transition wird dann folgendermassen ausgeführt:

**Beispiel-Request**:

   .. sourcecode:: http

      POST /(path)/@workflow/task-transition-open-in-progress HTTP/1.1
      Accept: application/json

      {
        "text": "Ok, wird gemacht!"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "action": "task-transition-open-in-progress",
        "actor": "philippe.gross",
        "comments": "",
        "review_state": "task-state-in-progress",
        "time": "2019-01-24T16:12:12+00:00",
        "title": "In Arbeit"
      }



Folgend sind die möglichen Statusänderungen kurz dokumentiert:


Akzeptieren
~~~~~~~~~~~

Transition IDs:
 - ``task-transition-open-in-progress``

Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Frist verlängern
~~~~~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-modify-deadline``

Zusätzliche Metadaten:

   .. py:attribute:: new_deadline

       :Datentyp: ``Date``
       :Pflichtfeld: Ja :required:`(*)`

   .. py:attribute:: text

       :Datentyp: ``Text``


Neu zuweisen
~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-reassign``

Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``

   .. py:attribute:: responsible

       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`


   .. py:attribute:: responsible_client

       :Datentyp: ``Choice``
       :Pflichtfeld: Nur wenn ``responsible`` den Client nicht bereits enthält. :required:`(*)`

Hinweis:

Das Attribut ``responsible`` kann einen kombinierten Wert im Format ``responsible_client:responsible`` enthalten. Z.b. ``fd:hans.muster`` oder ``team:musterteam``. Wird das Feld ``responsible`` mit einem kombinierten Wert befüllt, muss das Feld ``responsible_client`` nicht mehr mitgeschickt werden.

Erledigen
~~~~~~~~~

Transition IDs:
 - ``task-transition-in-progress-resolved``
 - ``task-transition-open-resolved``

Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``

   .. py:attribute:: approved_documents

       :Datentyp: ``Text``

Der Parameter ``approved_documents`` (optional) wird nur unterstützt für Aufgaben des Typs "Zur Genehmigung" (task_type `approval``). Mit diesem Parameter kann eine Liste von UIDs der genehmigten Dokumente mitgegeben werden, welche beim Abschluss der Aufgabe durch den authentisierten User genehmigt werden. Diese Dokumente müssen sich entweder in der Aufgabe befinden, oder mit einem Verweis von der Aufgabe referenziert sein.


Überarbeiten
~~~~~~~~~~~~

Transition IDs:
 - `task-transition-resolved-in-progress`

Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Abschliessen
~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-resolved-tested-and-closed``
 - ``task-transition-in-progress-tested-and-closed``
 - ``task-transition-open-tested-and-closed``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Abbrechen
~~~~~~~~~

Transition IDs:
 - ``task-transition-open-cancelled``
 - ``task-transition-in-progress-cancelled``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Ablehnen
~~~~~~~~~

Transition IDs:
 - ``task-transition-open-rejected``
 - ``task-transition-in-progress-cancelled``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Wieder eröffnen
~~~~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-cancelled-open``
 - ``task-transition-rejected-open``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Delegieren
~~~~~~~~~~

Transition IDs:
 - ``task-transition-delegate``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``

   .. py:attribute:: responsibles

       :Datentyp: ``ChoiceList``
       :Pflichtfeld: Ja :required:`(*)`

   .. py:attribute:: documents

       :Datentyp: ``Choice``

Des weiteren stehen auch die Statuswechsel für sequentielle Aufgaben zur Verfügung:


Überspringen
~~~~~~~~~~~~

Transition IDs:
 - ``task-transition-planned-skipped``
 - ``task-transition-rejected-skipped``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


Öffnen
~~~~~~

Transition IDs:
 - ``task-transition-planned-open``


Zusätzliche Metadaten:

   .. py:attribute:: text

       :Datentyp: ``Text``


.. _label-auto_close_task:

Aufgabe schliessen
------------------
Je nach Aufgabentyp und aktuellem Status müssen unterschiedliche Transitionen ausgeführt werden, um eine Aufgabe abzuschliessen oder abzubrechen.

Der Endpoint ``@close-task`` kann verwendet werden, um eine Aufgabe direkt zu schliessen, unabhängig davon, in welchem Status sie sich aktuell befindet.
„Schliessen“ bedeutet in diesem Kontext, dass sich die Aufgabe anschliessend in einem der folgenden Stati befindet:

- Abgebrochen
- Abgeschlossen

Ob eine Aufgabe abgebrochen oder abgeschlossen wird, hängt vom aktuellen Status und Typ der Aufgabe ab. Grundsätzlich gilt:

- Eine Aufgabe, die in Bearbeitung ist, wird abgeschlossen
- Eine Aufgabe, die noch nicht begonnen wurde, wird abgebrochen

Wichtig: Beim Schliessen einer Aufgabe wird stets der zugrunde liegende Workflow berücksichtigt.
Erfordert der Abschluss einer Aufgabe mehrere Transitionen, werden diese automatisch in der korrekten Reihenfolge ausgeführt.


**Beispiel-Request**:

   .. sourcecode:: http

      POST /task-1/@close-task HTTP/1.1
      Accept: application/json
      Content-Type: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Aufgabe übertragen
------------------

Sowohl Auftraggeber, als auch Auftragnehmer können mit dem ``@transfer-task`` Endpoint gewechselt werden. Dabei wird überprüft, ob ``old_userid`` der User-ID des Auftraggebers und/oder des Auftragnehmers entspricht. Ist dies der Fall, wird der Benutzer mit der User-ID ``new_userid`` als Auftraggeber und/oder Auftragnehmer gesetzt. Benachrichtigungen, die normalerweise bei einer Änderung ausgelöst werden, werden unterdrückt. Dieser Endpoint wird mit einer Berechtigung beschützt: ``opengever.api.TransferAssignment``
Die Berechtigung ist standardmässig den Rollen `Administrator` und `Manager` zugewiesen.


**Beispiel-Request**:

   .. sourcecode:: http

      POST /task-1/@transfer-task HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "old_userid": "john.doe",
        "new_userid": "robert.ziegler"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Aufgabe kommentieren
--------------------

Eine Aufgabe kann über den `@responses` Endpoint kommentiert werden:


Kommentar hinzufügen
~~~~~~~~~~~~~~~~~~~~

Ein POST Request auf den `@responses` Endpoint erstellt einen Kommentar mit dem aktuellen Benutzer.

**Beispiel-Request**:

   .. sourcecode:: http

      POST http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@responses HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Bitte rasch anschauen. Danke.",
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@responses/1569875801956269",
        "added_objects": [],
        "changes": [],
        "created": "2019-05-21T13:57:42+00:00",
        "creator": {
          "title": "Meier Peter",
          "token": "peter.meier"
        },
        "mimetype": "",
        "modified": null,
        "modifier": null,
        "related_items": [],
        "rendered_text": "",
        "response_id": 1569875801956269,
        "response_type": "comment",
        "successor_oguid": "",
        "text": "Bitte rasch anschauen. Danke.",
        "transition": "task-commented"
      }


Kommentar bearbeiten
~~~~~~~~~~~~~~~~~~~~

Ein PATCH Request auf eine Antwort vom Typ Kommentar ändert den Kommentar.

**Beispiel-Request**:

   .. sourcecode:: http

      PATCH http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@responses/1569875801956269 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "text": "Hat sich erledigt.",
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 Created
      Content-Type: application/json


Kommentar löschen
~~~~~~~~~~~~~~~~~

Ein DELETE Request auf eine Antwort vom Typ Kommentar löscht den Kommentar.

**Beispiel-Request**:

   .. sourcecode:: http

      DELETE http://example.org/ordnungssystem/fuehrung/dossier-1/task-5/@responses/1569875801956269 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content


Aufgabenverlauf
---------------
Der Verlauf einer Aufgabe ist in der GET Repräsentation einer Aufgaben unter dem Attribut ``responses`` enthalten.


**Beispiel-Response auf ein GET Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5",
        "@type": "opengever.task.task",
        "UID": "3a551f6e3b62421da029dfceb71656e6",
        "oguid": "fd:12345",
        "items": [],
        "responses": [
          {
            "response_id": 1
            "response_type": "default"
            "added_objects": [],
            "changes": [],
            "creator": "zopemaster",
            "created": "2019-05-21T13:57:42+00:00",
            "date_of_completion": null,
            "modified": null,
            "modifier": null,
            "related_items": [],
            "reminder_option": null,
            "text": "Lorem ipsum.",
            "transition": "task-commented"
          },
          {
            "response_id": 2
            "response_type": "default"
            "added_objects": [],
            "changes": [],
            "creator": "zopemaster",
            "created": "2019-05-21T14:02:01+00:00",
            "date_of_completion": null,
            "modified": null,
            "modifier": null,
            "related_items": [],
            "text": "Suspendisse faucibus, nunc et pellentesque egestas.",
            "transition": "task-transition-open-in-progress"
          },
        ]
        "responsible": "david.erni",
        "...": "...",
      }

Übergeordnetes Dossier
----------------------
Angaben zum übergeordneten Dossier einer Aufgabe ist in der GET Repräsentation der Aufgaben unter dem Attribut ``containing_dossier`` enthalten. Dies ist auch bei Unteraufgaben und Weiterleitungen im Eingangskorb der Fall.


**Beispiel-Response auf ein GET Request**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Accept: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-5",
        "@type": "opengever.task.task",
        "UID": "3a551f6e3b62421da029dfceb71656e6",
        "oguid": "fd:12345",
        "...": "...",
        "containing_dossier": {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1",
          "title": "Ein Dossier mit Tasks",
        },
        "...": "...",
      }


.. _tasktree:

Aufgabenhierarchie
-------------------
Zu einer Aufgabe kann die Aufgabenhierarchie bestehend aus Hauptaufgabe und allen Unteraufgaben abgefragt werden.
Dazu steht ein spezifischer Endpoint `@tasktree` zur Verfügung. Die Aufgaben werden nach Erstelldatum sortiert zurückgeliefert. Bei sequenziellen Aufgabenabläufen werden die Aufgaben nach Aufgabenfolge sortiert.

**Beispiel-Request**:

   .. sourcecode:: http

      GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-1/@tasktree HTTP/1.1
      Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-1/@tasktree",
        "children":             [
          {
            "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-1",
            "@type": "opengever.task.task",
            "children": [
              {
                "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-1/task-2",
                "@type": "opengever.task.task",
                "UID": "4b8b9fa59b9c4a9a9ef0555a9bbb49bf",
                "children": [],
                "review_state": "task-state-resolved",
                "is_task_addable": false
                "is_task_addable_before": false
                "title": "Eine Unteraufgabe"
              },
            ],
            "review_state": "task-state-in-progress",
            "is_task_addable": true
            "is_task_addable_before": false
            "title": "Eine Aufgabe"
          }
        ],
      }

Die Aufgabenhierarchie kann auch direkt über den GET-Request eines Tasks mittels Expansion angefordert werden.

  .. sourcecode:: http

     GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-1?expand=tasktree HTTP/1.1
     Accept: application/json

Für sequenzielle Aufgabenabläufe steht zusätzlich das Feld ``is_task_addable_before`` zur Verfügung.


Ursprüngliche Aufgabe
---------------------
Bei mandantenübergreifenden Aufgaben kann bei einer Aufgabe die ursprüngliche Aufgabe
(Vorgänger) abgefragt werden. Dazu steht ein spezifischer Endpoint `@predecessor` zur Verfügung.

**Beispiel-Request**:

   .. sourcecode:: http

      GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-2/@predecessor HTTP/1.1
      Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-2/@predecessor",
        "item": {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-1",
          "@type": "opengever.task.task",
          "oguid": "fd:1234",
          "review_state": "task-state-in-progress",
          "task_id": 1234,
          "task_type": "Zum Bericht / Antrag",
          "title": "Eine Aufgabe"
        }
      }

Die ursprüngliche Aufgabe kann auch direkt über den GET-Request eines Tasks mittels Expansion angefordert werden.

  .. sourcecode:: http

     GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-2?expand=predecessor HTTP/1.1
     Accept: application/json


Kopierte Aufgabe
----------------
Bei mandantenübergreifenden Aufgaben können bei einer Aufgabe die kopierten Aufgaben
(Nachfolger) abgefragt werden. Dazu steht ein spezifischer Endpoint `@successors` zur Verfügung.

**Beispiel-Request**:

   .. sourcecode:: http

      GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-1/@successors HTTP/1.1
      Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-1/@successors",
        "items": [{
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1/task-2",
          "@type": "opengever.task.task",
          "oguid": "fd:2345",
          "review_state": "task-state-in-progress",
          "task_id": 2345,
          "task_type": "Zum Bericht / Antrag",
          "title": "Eine Aufgabe"
        }]
      }

Die kopierten Aufgaben können auch direkt über den GET-Request eines Tasks mittels Expansion angefordert werden.

  .. sourcecode:: http

     GET http://example.org/ordnungssystem/fuehrung/dossier-1/task-1?expand=successors HTTP/1.1
     Accept: application/json



Aufgabenliste einer sequenziellen Aufgabe erweitern
---------------------------------------------------
Bei sequenziellen Aufgaben ist die Position von Aufgaben relevant. Wird die Aufgabenliste von einer sequenziellen Aufgabe erweitert, kann über den Parameter ``position`` die Position der neuen Aufgabe bestimmt werden.

Wird keine Position angegeben, wird die Aufgabe am Ende der Aufgabenliste hinzugefügt.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /(container) HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "@type": "opengever.task.task",
        "title": "Bitte Dokument reviewen",
        "position": 4,
        "...": "...",
      }

Der Parameter steht nur für Aufgaben innerhalb einer sequenziellen Aufgabe zur Verfügung.

Dokumente automatisch als Verweis der nächsten Aufgabe hinzufügen
-----------------------------------------------------------------
Bei Transitionen, welche automatisch das Öffnen der nächsten Aufgabe zur Folge haben (sequentiellen Aufgaben), kann über den Boolean-Parameter ``pass_documents_to_next_task`` gesteuert werden, ob alle Dokumente der aktuellen Aufgabe automatisch als Verweis in der nächsten Aufgabe hinzugefügt werden sollen:

Wird der Parameter nicht verwendet, werden keine Dokumente automatisch als Verweis eingetragen.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /(path)/@workflow/task-transition-open-resolved HTTP/1.1
      Accept: application/json

      {
        "text": "Ok, wird gemacht!",
        "pass_documents_to_next_task": "true"
      }
