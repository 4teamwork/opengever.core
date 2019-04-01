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

   .. py:attribute:: responsibles

       :Datentyp: ``List``
       :Pflichtfeld: Ja :required:`(*)`

   .. py:attribute:: title

       :Datentyp: ``TextLine``
       :Pflichtfeld: Ja :required:`(*)`

   .. py:attribute:: issuer

       :Datentyp: ``Choice``
       :Pflichtfeld: Ja :required:`(*)`

   .. py:attribute:: deadline

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
       :Pflichtfeld: Ja :required:`(*)`


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
