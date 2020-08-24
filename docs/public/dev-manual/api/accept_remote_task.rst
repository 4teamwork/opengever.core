.. _accept_remote_task:

Remote-Task akzeptieren
=======================

Der ``@accept-remote-task`` Endpoint auf Dossiers erlaubt es, eine mandantenübergreifende Aufgbe in dieses Dossier zu akzeptieren (es wird eine Kopie der Aufgabe im Dossier erstellt, auf welchem der Endpoint aufgerufen wird).

Der Remote-Task wird über den Parameter ``task_oguid`` im JSON Body angegeben (der Task *muss* sich auf einem anderen Mandanten befinden), und optional kann im Parameter ``text`` ein Kommentar zum Akzeptieren der Aufgabe angegeben werden.

Im untenstehenden Beispiel ist ``fd`` der Remote-Mandant, und der Benutzer, hugo.boss, will auf seinem lokalen Mandanten, ``rk``, eine Aufgabe auf dem ``fd`` akzeptieren, und eine Kopie der Aufgabe im ``dossier-17`` auf seinem Mandanten erstellen. Die Aufgabe ist durch die *task_oguid* ``fd:12345`` identifiziert.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /rk/dossier-17/@accept-remote-task HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
         "task_oguid": "fd:12345",
         "text": "Ich akzeptiere diese Aufgabe via Kopie in meinem Dossier"
       }

Die Response enthält das serialisierte Objekt (die soeben erstellte lokale Aufgabenkopie), so wie sie für einen regulären GET request aussehen würde:

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json

      {
        "@id": "http://.../dossier-17/task-42",
        "@type": "opengever.task.task",
        "oguid": "plone:1451484829",
        "...": "...",
        "predecessor": "plone:1451484827",
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
