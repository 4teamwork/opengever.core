.. _listings:

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
      "facets": {},
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
- ``todos``: Teamraum ToDos
- ``proposals``: Anträge
- ``contacts``: Lokale Kontakte


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
- ``issuer``: Auftraggeber (Benutzername)
- ``is_subdossier``: Ob das Dossier ein Subdossier ist.
- ``is_sutask``: Ob die Aufgabe eine Unteraufgabe ist.
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
- ``UID``: UID des Objektes
- ``firstname``: Vorname
- ``lastname``: Nachname
- ``email``: E-Mail Adresse
- ``phone_office``: Telefonnummer

Je nach Auflistungstyp und Inhalt sind bestimmte Felder nicht verfügbar. In diesem
Fall wird der Wert ``none`` zurückgegeben. So haben Dossiers bspw. keinen Dateinamen,
siehe Tabelle:


.. table::

    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    | Feld                     | Document | Dossier | Arbeitsraume | Arbeitsraum Ordner | Aufgabe |  ToDo   | Anträge | Kontakte |
    +==========================+==========+=========+==============+====================+=========+=========+=========+==========+
    |``bumblebee_checksum``    |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``changed``               |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``checked_out``           |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``checked_out_fullname``  |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``completed``             |   nein   |   nein  |     nein     |        nein        |   ja    |   ja    |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``containing_dossier``    |    ja    |    ja   |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``containing_subdossier`` |    ja    |    ja   |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``created``               |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``creator``               |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``deadline``              |   nein   |   nein  |     nein     |        nein        |   ja    |   ja    |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``delivery_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``description``           |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``document_author``       |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``document_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``document_type``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``end``                   |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``file_extension``        |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``filename``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``filesize``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``has_sametype_children`` |   nein   |    ja   |      ja      |         ja         |   ja    |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``issuer_fullname``       |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``is_subdossier``         |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``is_subtask``            |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``keywords``              |    ja    |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``mimetype``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``modified``              |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``pdf_url``               |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``preview_url``           |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``receipt_date``          |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``reference``             |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``reference_number``      |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``relative_path``         |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``responsible``           |   nein   |    ja   |     nein     |        nein        |   ja    |   ja    |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``responsible_fullname``  |   nein   |    ja   |     nein     |        nein        |   ja    |   ja    |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``review_state``          |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``review_state_label``    |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``sequence_number``       |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``start``                 |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``task_type``             |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``thumbnail_url``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``title``                 |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``type``                  |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``@type``                 |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+
    |``UID``                   |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+


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
- ``facets``: Für diese Felder auch die Facetten Wertebereichen liefern.


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

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&sort_on=modified&filters.start:record=2018-08-20TO2018-09-20 HTTP/1.1
    Accept: application/json

**Beispiel: Werte-Bereiche von Ersteller auch liefern**

  .. sourcecode:: http

    GET /ordnungssystem/fuehrung/dossier-23/@listing?name=documents&facets:list=creator HTTP/1.1
    Accept: application/json


Auflistungen User und Teams
===========================

Mit den Endpoints ``@ogds-user-listing`` und ``@team-listing`` können Benutzer und
Teams aus dem ogds aufgelistet werden. Diese beiden Endpoints liefern
inhaltlich die gleiche Struktur wie der ``@listing`` Endpoint, unterstützen
aber nur ein Subset der Parameter. Im Moment ist es nicht möglich die
``columns`` anzugeben, sondern es werden immer alle vom vom Modell
untertstützten Attribute zurückgegeben. Des weiteren ist der ``depth``
Paremeter nicht implementiert, ``facets`` werden ebenfalls nicht unterstützt.
Dies weil die Datenquelle eine SQL-Datenbank und nicht Solr ist.
Das ``last_login`` Attribut ist nur für Administratoren und Manager sichtbar.


Beispiel: Auflistung aller Benutzer:

  .. sourcecode:: http

    GET /kontakte/kontakte/@ogds-user-listing?b_size=1 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/kontakte/@ogds-user-listing",
      "batching": {
        "@id": "http://localhost:8080/fd/kontakte/@ogds-user-listing?b_size=1",
        "first": "http://localhost:8080/fd/kontakte/@ogds-user-listing?b_start=0&b_size=1",
        "last": "http://localhost:8080/fd/kontakte/@ogds-user-listing?b_start=24&b_size=1",
        "next": "http://localhost:8080/fd/kontakte/@ogds-user-listing?b_start=1&b_size=1"
      },
      "items": [
        {
          "@id": "http://localhost:8080/fd/kontakte/@ogds-users/sandro.ackermann",
          "@type": "virtual.ogds.user",
          "active": true,
          "department": null,
          "directorate": null,
          "email": "sandro.ackermann@example.com",
          "email2": null,
          "firstname": "Sandro",
          "lastname": "Ackermann",
          "last_login": "2020-05-31",
          "phone_office": null,
          "phone_mobile": null,
          "phone_fax": null,
          "title": "Ackermann Sandro",
          "userid": "sandro.ackermann"
        },
      ],
      "items_total": 25
    }


Optionale Parameter:
--------------------
Folgende Parameter werden im Moment unterstützt:

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente
- ``sort_on``: Sortierung nach einem indexierten Feld
- ``sort_order``: Sortierreihenfolge: ``ascending`` (aufsteigend) oder ``descending`` (absteigend)
- ``search``: Filterung nach einem beliebigen Suchbegriff
- ``filters``: Einschränkung nach einem bestimmten Wert eines Feldes


Filtern:
--------
Im Moment ist für beide Endpoinst ein Filter nach Status (aktiv/inaktiv) und ein Filter nach dem Zeitpunkt des letzten Logins implementiert.

Mit ``filters.state:record:list`` können die gewünschten Status angegeben werden:

- ``active``: aktive Benutzer/Teams
- ``inactive``: inaktive Benutzer/Teams


**Beispiel: Nur aktive Teams abfragen**

  .. sourcecode:: http

    GET /kontakte/@team-listing?filters.state:record:list=active HTTP/1.1
    Accept: application/json


**Beispiel: Aktive und inaktive Teams abfragen**

  .. sourcecode:: http

    GET /kontakte/@team-listing?filters.state:record:list=active&filters.state:record:list=inactive HTTP/1.1
    Accept: application/json

Mit ``filters.last_login:record:list`` kann nach dem Zeitpunkt des letzten Logins gefiltert werden:


**Beispiel: Filtern nach Benutzer mit Datum des letzten Logins zwischen dem 27.5.2020 und 2.6.2020**

  .. sourcecode:: http

    GET /kontakte/@ogds-user-listing?filters.last_login:record:list=2020-05-27%20TO%202020-06-02 HTTP/1.1
    Accept: application/json

