.. _close_remote_task:

Remote-Task "Zur Kentnissnahme" abschliessen
============================================

Der ``@close-remote-task`` Endpoint ermöglicht den Abschluss einer mandantenübergreifende Aufgabe vom Type "zur Kentnissnahme" abzuschliessen und dabei gewisse an die Aufgabe angehängte Dokumente in den eigenen Mandanten zu kopieren.

Im untenstehenden Beispiel ist ``fd`` der Remote-Mandant, und der Benutzer, hugo.boss, will die Aufgabe abschliessen und dabei zwei Dokumente auf seinem lokalen Mandanten ``rk`` kopieren.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /rk/@accept-remote-task HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
         "task_oguid": "fd:12345",
         "dossier_uid": "9823u409823094",
         "document_oguids": ["fd:34567", "fd:45678",],
         "text": "Ist ok!"
       }

Der Endpoint antwortet mit dem StatusCode 201.
