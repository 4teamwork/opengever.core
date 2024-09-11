Signieren von Dokumenten
========================

Dokumente können über den Workflow signiert werden. Diese Funktionalität setzt voraus, dass das Sign-Feature aktiviert und korrekt konfiguriert ist.

Nachdem das Feature aktiviert ist, stehen zwei neue Transitionen zur Verfügung, die es erlauben, Dokumente zu signieren:

- **Finalisieren und signieren**: Diese Transition finalisiert das Dokument und signiert es anschliessend.
- **Signieren**: Diese Transition signiert ein bereits finalisiertes Dokument.

Beispiel
--------

Um ein Dokument über den Workflow zu signieren, kann die Transition ``document-transition-draft-signing`` verwendet werden.

   **Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/document-1/@workflow/document-transition-draft-signing HTTP/1.1
       Accept: application/json
       Content-Type: application/json

Der Request löst den Signaturprozess für das Dokument aus.

Im Rahmen des Signaturprozesses wird ein Access-Token generiert, der dem externen Signaturservice übergeben wird. Dieses Token muss im späteren Request zur Rückführung der signierten PDF-Datei wiederverwendet werden.

Hochladen der signierten PDF-Datei
----------------------------------

Nachdem das Dokument signiert wurde, kann es über den Endpoint ``@upload-signed-pdf`` hochgeladen werden.

Der Endpoint löst eine interne Workflow-Transition auf dem Dokument aus, die automatisch eine neue Version des Dokuments mit den signierten PDF-Daten erstellt. Als Ersteller dieser neuen Version wird der Benutzer verwendet, der den Signaturprozess initiiert hat.

   **Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-1/document-1/@upload-signed-pdf HTTP/1.1
       Accept: application/json
       Content-Type: application/json

       {
           "access_token": "<token>",
           "signed_pdf_data": "<base64-pdf-data>"
       }

**Parameter:**

- ``access_token``: Das beim Start des Signaturprozesses generierte Token.
- ``signed_pdf_data``: Die signierten PDF-Daten im Base64-Format, die der externe Service nach der Signatur erzeugt hat.

Sobald das Dokument erfolgreich durch den externen Signaturservice signiert wurde, wird das Dokument in den Status **Signiert** versetzt.
