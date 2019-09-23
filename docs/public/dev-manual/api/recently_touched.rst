.. _recently_touched:

Kürzlich bearbeitete Dokumente
==============================

Der ``@recently-touched`` Endpoint liefert die Informationen zurück, um das
Menu für die kürzlich bearbeiteten Dokumente zu rendern.

Der Endpoint erwartet als Pfad-Argument die ID des Benutzers, und darf
standardmässig nur für den eigenen (aktuell eingeloggten) Benutzer aufgerufen
werden.

Die URL setzt sich somit folgendermassen zusammen:

``http://example.org/fd/@recently-touched/peter.mueller``


Auflistung:
-----------
Mittels eines GET Request können die kürzlich bearbeiteten Dokumente des
aktuellen Benutzers aufgelistet werden. Die Antwort ist ein Dictionary mit
zwei separaten Listen:

- ``"checked_out"`` - die aktuell ausgecheckten Dokumente des Benutzers (alle)
- ``"recently_touched"`` - die kürzlich bearbeiteten Dokumente des Benutzers.
  Dokumente, die zur Zeit ausgecheckt sind, werden in dieser Liste *nicht* noch
  einmal aufgeführt. Diese Liste ist limitiert (default: 10) auf eine
  maximale Anzahl.


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@recently-touched/peter.mueller HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "checked_out": [
          {
            "icon_class": "icon-dokument_word is-checked-out-by-current-user",
            "last_touched": "2018-05-31T15:40:23+02:00",
            "target_url": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-25/document-197",
            "title": "Datenschutzrichtlinien Muster AG",
            "filename": "Datenschutzrichtlinien Muster AG.docx",
            "checked_out": "peter.muster"
          },
          {
            "icon_class": "icon-dokument_excel is-checked-out-by-current-user",
            "last_touched": "2018-05-31T15:40:01+02:00",
            "target_url": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-25/document-191",
            "title": "Bilanz Muster AG 2018",
            "filename": "Bilanz Muster AG 2018.xlsx",
            "checked_out": "peter.muster"
          }
        ],
        "recently_touched": [
          {
            "icon_class": "icon-dokument_powerpoint is-checked-out",
            "last_touched": "2018-05-31T15:35:38+02:00",
            "target_url": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-18/document-229",
            "title": "Pra\u0308sentation - Firmenprofil Muster AG",
            "filename": "Praesentation - Firmenprofil Muster AG.ppt",
            "checked_out": "anderer.user"
          },
          {
            "...": ""
          },
          {
            "icon_class": "icon-dokument_word",
            "last_touched": "2018-05-31T15:34:42+02:00",
            "target_url": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-18/document-236",
            "title": "Anfrage Drei"
            "filename": "Anfrage Drei.docx",
            "checked_out": ""
          }
        ]
      }
