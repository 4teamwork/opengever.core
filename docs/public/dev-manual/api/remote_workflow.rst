.. _remote_workflow:

Remote Workflow-Transitionen
============================

Der ``@remote-workflow`` Endpoint erlaubt es, eine Workflow-Transition mandantenübergreifend auszulösen.

Der Aufruf erfolgt genau gleich wie ein Aufrauf des :ref:`regulären @workflow Endpoints <workflow>`, mit dem einzigen Unterschied, dass das Objekt über eine ``remote_oguid`` (im JSON body des Requests) spezifiziert wird, statt über den Pfad auf welchem der Endpoint aufgerufen wird.

Das über die ``remote_oguid`` identifizierte Objekt *muss* sich auf einem anderen Mandant befinden, und muss von einem Typ sein, dessen OGUID im GlobalIndex indexiert ist (dies sind zur Zeit nur Aufgaben).

Das Backend bestimmt dann den entsprechenden Mandanten, leitet den Request an diesen weiter (im Security-Kontext des Benutzers), und leitet die Response wieder an den Client zurück. Wenn der Benutzer auf dem remote-Mandanten die nötigen Berechtigungen hat, wird dadurch die entsprechende Workflow-Transition durchgeführt.

Im untenstehenden Beispiel ist ``fd`` der Remote-Mandant, und der Benutzer will via seinem lokalen Mandanten, ``rk``, eine Aufgabe auf dem ``fd`` akzeptieren. Diese Aufgabe ist durch die *remote_oguid* ``fd:12345`` identifiziert.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /rk/@remote-workflow/task-transition-open-in-progress HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
         "remote_oguid": "fd:12345",
         "text": "Ich akzeptiere diese Aufgabe"
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "action": "task-transition-open-in-progress",
        "actor": "hugo.boss",
        "comments": "",
        "review_state": "task-state-in-progress",
        "time": "2020-08-17T13:28:04+00:00",
        "title": "In Arbeit"
      }
