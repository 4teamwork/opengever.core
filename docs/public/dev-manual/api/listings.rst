.. listings:

Auflistungen
============

Mit dem ``@listing`` Endpoint können tabellenartige Auflistungen erstellt
werden.

Beispiel: Liste der Dokumente innerhalb eines Dossiers mit den Feldern `Titel`,
`Modifikationsdatum` und `Dateigrösse`:

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&columns:list=title&columns:list=modified&columns:list=filesize HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/dossier-23/@listing?name=documents&columns%3Alist=title&columns%3Alist=modified&columns%3Alist=filesize",
      "b_size": 25,
      "b_start": 0,
      "items": [
        {
          "@id": "http://localhost:8080/fd//ordnungssystem/fuehrung/dossier-23/document-59",
          "filesize": 12303,
          "modified": "2019-03-11T13:50:14+00:00",
          "title": "Ein Brief"
        },
        {
          "@id": "http://localhost:8080/fd//ordnungssystem/fuehrung/dossier-23/document-54",
          "filesize": 8574,
          "modified": "2019-03-11T12:32:24+00:00",
          "title": "Eine Mappe"
        }
      ],
      "items_total": 2
    }

Über den Parameter ``name`` wird der Typ der Auflistung bestimmt.
Aktuell werden folgende Auflistungen unterstützt:

- ``dossiers``: Dossiers
- ``documents``: Dokumente
- ``workspaces``: Arbeitsräume
- ``workspace_folders``: Arbeitsraum Ordner
- ``tasks``: Aufgaben


Für jede Auflistung können verschiedene Felder (Parameter ``columns``) abgefragt
werden. Folgende Felder stehen zur Verfügung:

- ``bumblebee_checksum``: SHA-256 Checksumme
- ``changed``: Änderungsdatum
- ``checked_out``: Benutzername des Benutzers, der das Dokument ausgechecked hat
- ``checked_out_fullname``: Anzeigename des Benutzers, der das Dokument ausgechecked hat
- ``completed``: Zeigt an ob eine Aufgabe erledigt ist.
- ``containing_dossier``: Titel des Hauptdossier in dem das Element enthalten ist
- ``containing_subdossier``: Titel des Subdossiers in dem das Dokument enthalten ist
- ``created``: Erstelldatum
- ``creator``: Ersteller
- ``deadline``: Aufgabenfrist
- ``delivery_date``: Ausgangsdatum
- ``description``: Beschreibung
- ``document_author``: Dokumentauthor
- ``document_date``: Dokumentdatum
- ``document_type``: Dokumenttyp
- ``end``: Enddatum des Dossiers
- ``file_extension``: Datei-Endung
- ``filename``: Dateiname
- ``filesize``: Dateigrösse
- ``has_sametype_children``: Ob es Objekte vom selben Inhaltstyp enthält.
- ``issuer_fullname``: Auftraggeber (Anzeigename)
- ``keywords``: Schlagwörter
- ``mimetype``: Mimetype
- ``modified``: Modifikationsdatum
- ``pdf_url``: URL für Vorschau-PDF
- ``preview_url``: URL für Vorschau
- ``receipt_date``: Eingangsdatum
- ``reference``: Referenz
- ``reference_number``: Aktenzeichen
- ``relative_path``: Pfad
- ``responsible``: Federführung (Benutzername)
- ``responsible_fullname``: Federführung oder Auftragnehmer (Anzeigename)
- ``review_state``: Status
- ``review_state_label``: Status (Anzeigewert)
- ``sequence_number``: Laufnummer
- ``start``: Startdatum des Dossiers
- ``task_type``: Aufgaben-Typ
- ``thumbnail_url``: URL für Vorschaubild
- ``title``: Titel
- ``type``: Inhaltstyp
- ``@type``: Inhaltstyp

Je nach Auflistungstyp und Inhalt sind bestimmte Felder nicht verfügbar. In diesem
Fall wird der Wert ``none`` zurückgegeben. So haben Dossiers bspw. keinen Dateinamen,
siehe Tabelle:


.. table::

    +--------------------------+----------+---------+--------------+--------------------+---------+
    | Feld                     | Document | Dossier | Arbeitsraume | Arbeitsraum Ordner | Aufgabe |
    +==========================+==========+=========+==============+====================+=========+
    |``bumblebee_checksum``    |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``changed``               |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``checked_out``           |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``checked_out_fullname``  |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``completed``             |   nein   |   nein  |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``containing_dossier``    |    ja    |    ja   |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``containing_subdossier`` |    ja    |    ja   |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``created``               |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``creator``               |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``deadline``              |   nein   |   nein  |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``delivery_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``description``           |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``document_author``       |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``document_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``document_type``         |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``end``                   |   nein   |    ja   |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``file_extension``        |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``filename``              |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``filesize``              |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``has_sametype_children`` |   nein   |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``issuer_fullname``       |   nein   |   nein  |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``keywords``              |    ja    |    ja   |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``mimetype``              |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``modified``              |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``pdf_url``               |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``preview_url``           |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``receipt_date``          |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``reference``             |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``reference_number``      |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``relative_path``         |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``responsible``           |   nein   |    ja   |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``responsible_fullname``  |   nein   |    ja   |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``review_state``          |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``review_state_label``    |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``sequence_number``       |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``start``                 |   nein   |    ja   |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``task_type``             |   nein   |   nein  |     nein     |        nein        |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``thumbnail_url``         |    ja    |   nein  |     nein     |        nein        |  nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``title``                 |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``type``                  |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+
    |``@type``                 |    ja    |    ja   |      ja      |         ja         |   ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+



Optionale Parameter:
--------------------

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente
- ``sort_on``: Sortierung nach einem indexierten Feld
- ``sort_order``: Sortierreihenfolge: ``ascending`` (aufsteigend) oder ``descending`` (absteigend)
- ``search``: Filterung nach einem beliebigen Suchbegriff
- ``columns``: Liste der Felder, die zurückgegeben werden sollen.
- ``filters``: Einschränkung nach einem bestimmten Wert eines Feldes
- ``depth``: Limitierung der maximalen Pfadtiefe (relativ zum Kontext):

  - ``1``: Nur die unmittelbaren children unterhalb des Kontexts
  - ``2``: Unmittelbare children, und deren direkte children
  - etc.


**Beispiel: Sortierung nach Änderungsdatum, neuste Dokumente zuerst:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&sort_on=changed&sort_order=descending HTTP/1.1
    Accept: application/json



**Beispiel: Filtern nach abgeschlossenen und archivierten Dossiers:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&sort_on=modified&filters.review_state:record:list=dossier-state-resolved&filters.review_state:record:list=dossier-state-archived HTTP/1.1
    Accept: application/json

**Beispiel: Filtern nach Dossiers mit Startdatum zwischen dem 20.8.2018 und 20.9.2018:**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&sort_on=modified&filters.start:record:=2018-08-20TO2018-09-20 HTTP/1.1
    Accept: application/json
