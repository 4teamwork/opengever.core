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

.. _listing-names:

Über den Parameter ``name`` wird der Typ der Auflistung bestimmt.
Aktuell werden folgende Auflistungen unterstützt:

- ``dispositions``: Angebote
- ``dossiers``: Dossiers
- ``dossiertemplates``: Dossiervorlagen
- ``documents``: Dokumente
- ``workspaces``: Arbeitsräume
- ``workspace_folders``: Arbeitsraum Ordner
- ``workspace_meetings``: Teamraum Meetings
- ``tasks``: Aufgaben
- ``todos``: Teamraum ToDos
- ``todo_lists``: Teamraum ToDo-Listen
- ``proposals``: Anträge
- ``contacts``: Lokale Kontakte
- ``repository_folders``: Ordnungspositionen
- ``tasktemplates``: Standardabläufe
- ``tasktemplate_folders``: Aufgabenvorlagen
- ``template_folders``: Vorlagenordner
- ``folder_contents``: Alle Inhalte innerhalb des Objektes


Für jede Auflistung können verschiedene Felder (Parameter ``columns``) abgefragt
werden. Folgende Felder stehen zur Verfügung:

- ``@type``: Inhaltstyp
- ``approval_state``: Genehmigungs-Status
- ``blocked_local_roles``: Ob Berechtigungen von übergeordneten Ordnern übernommen werden.
- ``bumblebee_checksum``: SHA-256 Checksumme
- ``changed``: Änderungsdatum
- ``checked_out_fullname``: Anzeigename des Benutzers, der das Dokument ausgechecked hat
- ``checked_out``: Benutzername des Benutzers, der das Dokument ausgechecked hat
- ``is_completed``: Zeigt an ob eine Aufgabe oder ein Todo erledigt ist.
- ``containing_dossier``: Titel des Hauptdossier in dem das Element enthalten ist
- ``containing_subdossier``: Titel des Subdossiers in dem das Dokument enthalten ist
- ``created``: Erstelldatum
- ``creator``: Ersteller
- ``creator_fullname``: Ersteller (Anzeigename)
- ``deadline``: Aufgabenfrist
- ``delivery_date``: Ausgangsdatum
- ``description``: Beschreibung
- ``document_author``: Dokumentauthor
- ``document_date``: Dokumentdatum
- ``document_type``: Dokumenttyp
- ``document_type_label``: Dokumenttyp (Anzeigewert)
- ``dossier_type``: Dossiertyp
- ``dossier_type_label``: Dossiertyp (Anzeigewert)
- ``dossier_review_state``: Der Status des Dossiers selbst oder des Dossiers, in dem sich der aktuelle Inhalt befindet.
- ``email``: E-Mail Adresse
- ``end``: Enddatum des Dossiers
- ``external_reference``: Externe Referenz für Dossiers oder Fremdzeichen für Dokumente
- ``file_extension``: Datei-Endung
- ``filename``: Dateiname
- ``filesize``: Dateigrösse
- ``firstname``: Vorname
- ``has_sametype_children``: Ob es Objekte vom selben Inhaltstyp enthält.
- ``is_subdossier``: Ob das Dossier ein Subdossier ist.
- ``is_sutask``: Ob die Aufgabe eine Unteraufgabe ist.
- ``issuer_fullname``: Auftraggeber (Anzeigename)
- ``issuer``: Auftraggeber (Benutzername)
- ``id``: ID des Inhalts
- ``keywords``: Schlagwörter
- ``lastname``: Nachname
- ``mimetype``: Mimetype
- ``modified``: Modifikationsdatum
- ``participants``: Beteiligte
- ``participation_roles``: Beteiligungsrollen
- ``participations``: Beteiligungen
- ``progress``: Fortschritt für Dossiers, welche das Checklist-Feature verwenden
- ``pdf_url``: URL für Vorschau-PDF
- ``phone_office``: Telefonnummer
- ``preview_url``: URL für Vorschau
- ``public_trial``: Öffentlichkeitsstatus
- ``receipt_date``: Eingangsdatum
- ``reference_number``: Aktenzeichen
- ``reference``: Aktenzeichen
- ``relative_path``: Pfad
- ``responsible_fullname``: Federführung oder Auftragnehmer (Anzeigename)
- ``responsible``: Federführung (Benutzername)
- ``retention_expiration``: Ablauf der Aufbewahrungsfrist
- ``review_state_label``: Status (Anzeigewert)
- ``review_state``: Status
- ``sequence_number``: Laufnummer
- ``sequence_type``: Ablauftyp
- ``start``: Startdatum des Dossiers
- ``task_type``: Aufgaben-Typ
- ``thumbnail_url``: URL für Vorschaubild
- ``title``: Titel
- ``trashed``: Ob das Objekt im Papierkorb ist
- ``type``: Inhaltstyp
- ``UID``: UID des Objektes
- ``watchers``: Liste von Beobachtern des Objekts (Benutzernamen)

Weitere dynamische Felder sind gemäss :ref:`benutzerdefinierte Felder <listing-property_sheets>` verfügbar.

Je nach Auflistungstyp und Inhalt sind bestimmte Felder nicht verfügbar. In diesem
Fall wird der Wert ``none`` zurückgegeben. So haben Dossiers bspw. keinen Dateinamen,
siehe Tabelle:


.. table::

    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    | Feld                     | Document | Dossier | Arbeitsraume | Arbeitsraum Ordner | Aufgabe |  ToDo   | Anträge | Kontakte | Standardabläufe | Aufgabenvorlagen | Dossiervorlagen | Meetings | Ordnungsposition | RIS-Anträge | Vorlagenordner | Angebote |
    +==========================+==========+=========+==============+====================+=========+=========+=========+==========+=================+==================+=================+==========+==================+=============+================+==========+
    |``@type``                 |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |   ja     |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``blocked_local_roles``   |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |        ja        |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``bumblebee_checksum``    |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``changed``               |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |        ja       |         ja       |       ja        |    ja    |        ja        |      ja     |      nein      |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``checked_out``           |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``checked_out_fullname``  |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``is_completed``          |   nein   |   nein  |     nein     |        nein        |   ja    |   ja    |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``containing_dossier``    |    ja    |    ja   |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``containing_subdossier`` |    ja    |    ja   |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``created``               |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``creator``               |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``creator_fullname``      |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |       nein       |      ja     |      nein      |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``deadline``              |   nein   |   nein  |     nein     |        nein        |   ja    |   ja    |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``delivery_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``description``           |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``document_author``       |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``document_date``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``document_type``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``dossier_type``          |    nein  |   ja    |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       ja        |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``dossier_review_state``  |    ja    |   ja    |     nein     |        nein        |  ja     |  nein   |  ja     |   ja     |       ja        |       ja         |       ja        |   ja     |       nein       |     ja      |      ja        |   ja     |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``end``                   |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |    ja    |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``external_reference``    |    ja    |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``file_extension``        |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``filename``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``filesize``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``has_sametype_children`` |   nein   |    ja   |      ja      |         ja         |   ja    |  nein   |  nein   |   nein   |       nein      |       nein       |       ja        |   nein   |        ja        |     nein    |       ja       |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``issuer_fullname``       |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``is_subdossier``         |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       ja        |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``is_subtask``            |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``keywords``              |    ja    |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       ja        |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``mimetype``              |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``modified``              |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``participants``          |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``participation_roles``   |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``participations``        |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``pdf_url``               |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``preview_url``           |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``progress``              |    nein  |   ja    |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``public_trial``          |    ja    |   ja    |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |        ja        |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``receipt_date``          |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``reference``             |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |    ja    |        ja        |      ja     |       ja       |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``reference_number``      |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |   ja     |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``relative_path``         |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |    ja    |       nein      |       nein       |       ja        |   nein   |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``responsible``           |   nein   |    ja   |     nein     |        nein        |   ja    |   ja    |   ja    |   nein   |       nein      |        ja        |       nein      |    ja    |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``responsible_fullname``  |   nein   |    ja   |     nein     |        nein        |   ja    |   ja    |   ja    |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |      ja     |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``review_state``          |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |        ja       |        ja        |       nein      |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``review_state_label``    |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |      ja     |      nein      |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``sequence_number``       |    ja    |    ja   |      ja      |         ja         |   ja    |  nein   |   ja    |   nein   |       nein      |       nein       |       ja        |    ja    |       nein       |      ja     |      nein      |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``sequence_type``         |   nein   |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |        ja        |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``start``                 |   nein   |    ja   |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       ja        |    ja    |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``task_type``             |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |  nein   |   nein   |       nein      |        ja        |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``thumbnail_url``         |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``title``                 |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``trashed``               |    ja    |   nein  |     nein     |        nein        |  nein   |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |    ja    |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``type``                  |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``UID``                   |    ja    |    ja   |      ja      |         ja         |   ja    |   ja    |   ja    |    ja    |        ja       |        ja        |       ja        |    ja    |        ja        |      ja     |       ja       |    ja    |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+
    |``watchers``              |   nein   |   nein  |     nein     |        nein        |   ja    |  nein   |  nein   |   nein   |       nein      |       nein       |       nein      |   nein   |       nein       |     nein    |      nein      |   nein   |
    +--------------------------+----------+---------+--------------+--------------------+---------+---------+---------+----------+-----------------+------------------+-----------------+----------+------------------+-------------+----------------+----------+

.. _listing-property_sheets:

Benutzerdefinierte Felder:
--------------------------

Falls :ref:`benutzerdefinierte Felder <propertysheets>` definiert sind, stehen
mit dem Endpoint ``@listing-custom-fields`` weitere, dynamische Felder zur
Verfügung. Der Endpoint kann z.B. dafür benutzt werden um in einem Filtermenü
sichtbare Spalten darzustellen. Er leifert ``title``, ``type`` und ``name``
zurück. Der ``name`` kann für den Parameter ``columns`` des ``@listing``
Endpoints verwendet werden.

  .. sourcecode:: http

    GET /@listing-custom-fields HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "documents": {
            "properties": {
                "buul_custom_field_boolean": {
                    "name": "buul_custom_field_boolean",
                    "title": "J/N",
                    "type": "boolean",
                    "widget": null
                },
                "choice_custom_field_string": {
                    "name": "choice_custom_field_string",
                    "title": "Auswahl",
                    "type": "string",
                    "widget": null
                },
                "num_custom_field_int": {
                    "name": "num_custom_field_int",
                    "title": "Zahl",
                    "type": "integer",
                    "widget": null
                },
                "textline_custom_field_string": {
                    "name": "textline_custom_field_string",
                    "title": "Zeile Text",
                    "type": "string",
                    "widget": null
                },
                "date_custom_field_date": {
                    "name": "date_custom_field_date",
                    "title": "Datum",
                    "type": "string",
                    "widget": "date"
                }
            }
        }
    }


Optionale Parameter:
--------------------

- ``b_start``: Das erste zurückzugebende Element
- ``b_size``: Die maximale Anzahl der zurückzugebenden Elemente
- ``sort_on``: Sortierung nach einem indexierten Feld
- ``sort_order``: Sortierreihenfolge: ``ascending`` (aufsteigend) oder ``descending`` (absteigend)
- ``sort_first``: Sortiert die Resultate in zwei Gruppen. Jede Gruppe wird anschließend gem. ``sort_on`` sortiert.
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


Bestimmte Inhalte zuerst sortieren:
-----------------------------------
Die Resultate können in zwei Gruppen aufgeteilt und anschließend sortiert werden. So können z.B. in einer Auflistung alle Ordner zuoberst angezeigt werden.

Alle Inhalte welche zuerst angezeigt werden sollen bilden eine Gruppe, alle restlichen Inhalte bilden eine zweite Gruppe. Momentan werden nur folgende Felder als `sort_first` unterstütz:

- ``portal_type``


**Beispiel: Alle Dossiers zuoberst. Jede Gruppe wird nach Titel sortiert**

  .. sourcecode:: http

    GET /@listing?sort_first.portal_type:record:list=opengever.dossier.businesscasedossier&sort_on=sortable_title HTTP/1.1
    Accept: application/json


**Beispiel: Alle Dokumente und Mails zuoberst**

  .. sourcecode:: http

    GET /@listing?sort_first.portal_type:record:list=opengever.document.document&sort_first.portal_type:record:list=ftw.mail.mail& HTTP/1.1
    Accept: application/json


Auflistung User
===============
Mit dem Endpoint ``@ogds-user-listing`` können Benutzer aus dem ogds aufgelistet werden.
Dieser Endpoint liefern inhaltlich die gleiche Struktur wie der ``@listing`` Endpoint, unterstütz
aber nur ein Subset der Parameter. Im Moment ist es nicht möglich die
``columns`` anzugeben, sondern es werden immer alle vom Modell
untertstützten Attribute zurückgegeben.

Das ``last_login`` Attribut ist nur für Administratoren und Manager sichtbar.


Beispiel: Auflistung aller Benutzer:

  .. sourcecode:: http

    GET /@ogds-user-listing?b_size=1 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/@ogds-user-listing",
      "batching": {
        "@id": "http://localhost:8080/fd/@ogds-user-listing?b_size=1",
        "first": "http://localhost:8080/fd/@ogds-user-listing?b_start=0&b_size=1",
        "last": "http://localhost:8080/fd/@ogds-user-listing?b_start=24&b_size=1",
        "next": "http://localhost:8080/fd/@ogds-user-listing?b_start=1&b_size=1"
      },
      "items": [
        {
          "@id": "http://localhost:8080/fd/@ogds-users/sandro.ackermann",
          "@type": "virtual.ogds.user",
          "active": true,
          "department": null,
          "directorate": null,
          "email": "sandro.ackermann@example.com",
          "email2": null,
          "firstname": "Sandro",
          "job_title": "Gesch\u00e4ftsf\u00fchrer",
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
Im Moment sind ein Filter nach Status (``filters.state``), ein Filter nach dem Zeitpunkt des letzten Logins ``filters.last_login`` und ein filter nach Gruppenmitgliedschaft ``filters.groupid`` implementiert.

Mit ``filters.state:record:list`` können die gewünschten Status angegeben werden:

- ``active``: aktive Benutzer/Teams
- ``inactive``: inaktive Benutzer/Teams

**Beispiel: Filtern nach Benutzer mit Datum des letzten Logins zwischen dem 27.5.2020 und 2.6.2020**

  .. sourcecode:: http

    GET /@ogds-user-listing?filters.last_login:record:list=2020-05-27%20TO%202020-06-02 HTTP/1.1
    Accept: application/json

**Beispiel: Filtern nach Benutzer mit Datum des letzten Logins nach dem 27.5.2020**

  .. sourcecode:: http

    GET /@ogds-user-listing?filters.last_login:record:list=2020-05-27%20TO%20* HTTP/1.1
    Accept: application/json

**Beispiel: Filtern nach Benutzer welche Teil der Gruppe test-group sind**

  .. sourcecode:: http

    GET /@ogds-user-listing?filters.groupid:record:test-group HTTP/1.1
    Accept: application/json

Auflistung Teams
================
Mit dem Endpoint ``@team-listing`` können Teams aus dem ogds aufgelistet werden.
Dieser Endpoint liefern inhaltlich die gleiche Struktur wie der ``@listing`` Endpoint, unterstütz
aber nur ein Subset der Parameter. Im Moment ist es nicht möglich die
``columns`` anzugeben, sondern es werden immer alle vom Modell
untertstützten Attribute zurückgegeben.

Dieser Endpoint steht nur auf Stufe PloneSite zur Verfügung.

Beispiel: Auflistung aller Teams:

  .. sourcecode:: http

    GET /@team-listing?b_size=1 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/@ogds-user-listing",
      "batching": {
        "@id": "http://localhost:8080/fd/@team-listing?b_size=1",
        "first": "http://localhost:8080/fd/@team-listing?b_start=0&b_size=1",
        "last": "http://localhost:8080/fd/@team-listing?b_start=24&b_size=1",
        "next": "http://localhost:8080/fd/@team-listing?b_start=1&b_size=1"
      },
      "items": [
        {
          "@id": "http://localhost:8081/fd/@teams/427",
          "@type": "virtual.ogds.team",
          "active": true,
          "groupid": "test-group",
          "org_unit_id": "stv",
          "org_unit_title": "Steuerverwaltung",
          "team_id": 427,
          "title": "Test Team"
        },
      ],
      "items_total": 25
    }


Filtern:
--------

Status:
~~~~~~~
Folgende Statusfilter stehen zur Verfügung:

- ``active``: aktive Gruppen
- ``inactive``: inaktive Gruppen


**Beispiel: Nur aktive Teams abfragen**

  .. sourcecode:: http

    GET /@team-listing?filters.state:record:list=active HTTP/1.1
    Accept: application/json


**Beispiel: Aktive und inaktive Teams abfragen**

  .. sourcecode:: http

    GET /@team-listing?filters.state:record:list=active&filters.state:record:list=inactive HTTP/1.1
    Accept: application/json


Auflistung der OGDS-Gruppen
===========================

Mit dem Endpoint ``@ogds-group-listing`` können Gruppen aus dem ogds aufgelistet werden.
Dieser Endpoint liefern inhaltlich die gleiche Struktur wie der ``@listing`` Endpoint, unterstütz
aber nur ein Subset der Parameter. Im Moment ist es nicht möglich die
``columns`` anzugeben, sondern es werden immer alle vom Modell
untertstützten Attribute zurückgegeben.

Beispiel: Auflistung aller Gruppen:

  .. sourcecode:: http

    GET /@ogds-group-listing?b_size=1 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:8080/fd/@ogds-group-listing",
      "b_size": 25,
      "b_start": 0,
      "items": [
        {
          "@id": "http://localhost:8080/fd/@ogds-groups/test-group",
          "@type": "virtual.ogds.group",
          "active": true,
          "groupid": "test-group",
          "groupurl": "http://localhost:8080/fd/@groups/test-group",
          "is_local": false,
          "title": "Test Group"
        }
      ],
      "items_total": 1
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

Status:
~~~~~~~
Folgende Statusfilter stehen zur Verfügung:

- ``active``: aktive Gruppen
- ``inactive``: inaktive Gruppen


**Beispiel: Nur aktive Gruppen abfragen**

  .. sourcecode:: http

    GET /@ogds-group-listing?filters.state:record:list=active HTTP/1.1
    Accept: application/json


Lokale Gruppen:
~~~~~~~~~~~~~~~

**Beispiel: Nur lokale Gruppen abfragen**

  .. sourcecode:: http

    GET /@ogds-group-listing?filters.is_local:record:boolean=True HTTP/1.1
    Accept: application/json

Zugriff auf die Plone Gruppe:
-----------------------------
Eine OGDS-Gruppe kann nicht manipuliert werden und enthält auch nicht alle Metadaten welche in Plone zur Verfügung stehen. Dafür sind Abfragen gegen den OGDS-Endpoint sehr schnell. Benötigt man jedoch zusätzliche Gruppeninformationen oder möchte lokale Gruppen ändern, muss der ``@groups`` Endpoint von Plone verwendet werden. Dieser stellt mehr Metadaten für Gruppen zur Verfügung und bietet auch einen POST, PATCH und DELETE Endpoint zum Ändern von lokalen Gruppen an. Der ``@groups`` Endpoint wird im Kapitel :ref:`users` genauer beschrieben.

Eine serialisierte OGDS-Gruppe stellt, für den einfacheren Zugriff auf die Plone-Gruppe, im Attribut ``groupurl`` die URL zur Plone-Ressource zur Verfügung.
