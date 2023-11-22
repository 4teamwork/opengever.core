.. _complete_successor_task:

Successor-Task abschliessen
===========================

Der ``@complete-successor-task`` Endpoint auf Aufgaben erlaubt es, eine mandantenübergreifende Nachfolgeaufgabe abzuschliessen.

Durch das Abschliessen der Nachfolgeaufgabe wird das Backend auch die Vorgänger-Aufgabe auf dem Remote-Mandanten abschliessen, und ggf. die angegebenen Dokumente an die Vorgängeraufgabe zurück übermitteln.

Dokumente, welche zurück übermittelt werden sollen, können über den Parameter ``documents`` angegeben werden. Dieser Parameter erlaubt die Referenzierung von Dokumenten (im selben Dossier wie die Nachfolgeaufgabe) über IntId (``1423795951``), OGUID (``rk:1423795951``), Pfad (``/ordnungssystem/dossier-17/document-23``) oder URL (``https://example.com/ordnungssystem/dossier-17/document-23``).

Optional kann im Parameter ``text`` ein Kommentar zum Abschliessen der Aufgabe angegeben werden.

Im untenstehenden Beispiel ist ``fd`` der Remote-Mandant, und der Benutzer, hugo.boss, will auf seinem lokalen Mandanten, ``rk``, die Aufgabe ``task-42`` abschliessen.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /rk/task-42/@complete-successor-task HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
         "transition": "task-transition-in-progress-resolved",
         "documents": [1423795951],
         "text": "Ich schliesse diese Aufgabe ab."
       }

Die Response enthält das serialisierte Objekt (die soeben abgeschlossene Nachfolgeaufgabe), so wie sie für einen regulären GET request aussehen würde:

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://.../dossier-17/task-42",
        "@type": "opengever.task.task",
        "oguid": "plone:2118709190",
        "...": "...",
        "predecessor": "plone:2118709189",
        "responses": [
          {"...": "..."},
          {
            "@id": "http://.../dossier-17/task-42/@responses/1598221249104420",
            "...": "...",
            "added_objects": [
              {
                "@id": "http://.../dossier-17/task-42/document-77",
                "@type": "opengever.document.document",
                "UID": "c99df05a4bbe473ead5e2356f5a4f8b4",
                "checked_out": "",
                "description": "",
                "file_extension": ".docx",
                "is_leafnode": null,
                "review_state": "document-state-draft",
                "title": "Statement in response to inquiry"
              }
            ],
            "text": "Ich schliesse diese Aufgabe ab.",
            "transition": "task-transition-in-progress-resolved"
          }
        ],
        "responsible": {
          "title": "Ratskanzlei: Boss Hugo (hugo.boss)",
          "token": "rk:hugo.boss"
        },
        "responsible_client": {
          "title": "Ratskanzlei",
          "token": "rk"
        },
        "review_state": "task-state-resolved"
      }
