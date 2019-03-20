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


Für jede Auflistung können verschiedene Felder (Parameter ``columns``) abgefragt
werden. Folgende Felder stehen zur Verfügung:

- ``@type``: Inhaltstyp
- ``bumblebee_checksum``: SHA-256 Checksumme
- ``checked_out``: Benutzername des Benutzers, der das Dokument ausgechecked hat
- ``checked_out_fullname``: Anzeigename des Benutzers, der das Dokument ausgechecked hat
- ``containing_dossier``: Titel des Hauptdossier in dem das Element enthalten ist
- ``containing_subdossier``: Titel des Subdossiers in dem das Dokument enthalten ist
- ``created``: Erstelldatum
- ``creator``: Ersteller
- ``description``: Beschreibung
- ``delivery_date``: Ausgangsdatum
- ``document_author``: Dokumentauthor
- ``document_date``: Dokumentdatum
- ``end``: Enddatum des Dossiers
- ``mimetype``: Mimetype
- ``modified``: Modifikationsdatum
- ``changed``: Änderungsdatum
- ``receipt_date``: Eingangsdatum
- ``reference``: Referenz
- ``reference_number``: Aktenzeichen
- ``relative_path``: Pfad
- ``responsible``: Federführung (Benutzername)
- ``responsible_fullname``: Federführung (Anzeigename)
- ``review_state``: Status
- ``review_state_label``: Status (Anzeigewert)
- ``sequence_number``: Laufnummer
- ``start``: Startdatum des Dossiers
- ``thumbnail_url``: URL für Vorschaubild
- ``pdf_url``: URL für Vorschau-PDF
- ``title``: Titel
- ``filesize``: Dateigrösse
- ``filename``: Dateiname

Je nach Auflistungstyp und Inhalt sind bestimmte Felder nicht verfügbar. In diesem
Fall wird der Wert ``none`` zurückgegeben. So haben Dossiers bspw. keinen Dateinamen.


Optionale Parameter:
--------------------

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente
- ``sort_on``: Sortierung nach einem indexierten Feld
- ``sort_order``: Sortierreihenfolge: ``ascending`` (aufsteigend) oder ``descending`` (absteigend)
- ``search``: Filterung nach einem beliebigen Suchbegriff
- ``columns``: Liste der Felder, die zurückgegeben werden sollen.
- ``filters``: Einschränkung nach einem bestimmten Wert eines Feldes


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
