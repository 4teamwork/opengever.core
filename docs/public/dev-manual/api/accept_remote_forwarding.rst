.. _accept-remote-forwarding:

Remote-Weiterleitung akzeptieren
================================

Der ``@accept-remote-forwarding`` Endpoint auf Dossiers erlaubt es, eine mandantenübergreifende Weiterleitung im Eingangskorb abzulegen. Optional kann die Weiterleitung einem Dossier zugewiesen werden (es wird eine Aufgabenkopie im angegebenen Dossier erstellt).

Die Remote-Weiterleitung wird über den Parameter ``forwarding_oguid`` im JSON Body angegeben (die Weiterleitung *muss* sich auf einem anderen Mandanten befinden), und optional kann im Parameter ``dossier_oguid`` das Dossier angeben werden, dem die Weiterleitung zugewiesen werden soll und im Parameter ``text`` kann ein Kommentar zum Akzeptieren der Aufgabe angegeben werden.

Im untenstehenden Beispiel ist ``fd`` der Remote-Mandant, und der Benutzer, hugo.boss, will auf seinem lokalen Mandanten, ``rk``, eine Weiterleitung akzeptieren, und eine Kopie der Weiterleitung im ``dossier-17`` auf seinem Mandanten erstellen. Die Weiterleitung ist durch die *forwarding_oguid* ``fd:12345`` identifiziert.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /rk/eingangskorb/@accept-remote-forwarding HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
         "dossier_oguid": "rk:12345",
         "forwarding_oguid": "fd:12345",
         "text": "Ich akzeptiere diese Weiterleitung in meinem Dossier"
       }

Die Response enthält das serialisierte Objekt (die soeben erstellte lokale Aufgabenkopie), so wie sie für einen regulären GET request aussehen würde:

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://.../dossier-17/task-42",
        "@type": "opengever.task.task",
        "oguid": "rk:1451484829",
        "...": "...",
        "predecessor": "fd:1451484827",
        "responses": [
          {"...": "..."},
          {
            "@id": "http://.../dossier-17/task-42/@responses/1598198218402585",
            "...": "...",
            "text": "Ich akzeptiere diese Aufgabe via Kopie in meinem Dossier",
            "transition": "task-transition-open-in-progress"
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
        "review_state": "task-state-in-progress"
      }
