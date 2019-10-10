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
            "description": "Wichtige Dokumentation",
            "last_touched": "2018-05-31T15:40:23+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-25/document-197",
            "@type": "opengever.document.document",
            "title": "Datenschutzrichtlinien Muster AG",
            "review_state": "Datenschutzrichtlinien Muster AG.docx",
          },
          {
            "icon_class": "icon-dokument_excel is-checked-out-by-current-user",
            "description": "",
            "last_touched": "2018-05-31T15:40:01+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-25/document-191",
            "@type": "opengever.document.document",
            "title": "Bilanz Muster AG 2018",
            "review_state": "Datenschutzrichtlinien Muster AG.docx",
          }
        ],
        "recently_touched": [
          {
            "icon_class": "icon-dokument_powerpoint is-checked-out",
            "description": "",
            "last_touched": "2018-05-31T15:35:38+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-18/document-229",
            "@type": "opengever.document.document",
            "title": "Pra\u0308sentation - Firmenprofil Muster AG",
            "review_state": "Datenschutzrichtlinien Muster AG.docx",
          },
          {
            "...": ""
          },
          {
            "icon_class": "icon-dokument_word",
            "description": "",
            "last_touched": "2018-05-31T15:34:42+02:00",
            "@id": "http://localhost:8080/fd/ordnungssystem/fuehrung/gemeinderecht/dossier-18/document-236",
            "@type": "opengever.document.document",
            "title": "Anfrage Drei"
            "review_state": "Datenschutzrichtlinien Muster AG.docx",
          }
        ]
      }


Die Repräsentation der Dokumente entspricht der :ref:`Summary Repräsentation von Inhalten <summaries>`, wie sie auch in anderen Feldern zum Einsatz kommt. Dabei wird auch der Parmater ``metadata_fields`` unterstützt, welches es erlaubt zusätzliche Felder abzufragen.
