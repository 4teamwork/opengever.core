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

Ein PATCH Request auf eine Kommentar-Ressource ändert den Kommentar.

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
        "...": "...",
        "containing_dossier": {
          "@id": "http://example.org/ordnungssystem/fuehrung/dossier-1",
          "title": "Ein Dossier mit Tasks",
        },
        "...": "...",
      }
