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

Aktualisieren eines ausstehenden Signierungsauftrags
----------------------------------------------------
Der Endpoint ``@update-pending-signing-job`` dient dazu, die Listen der Signierenden ("signers") und Bearbeitenden ("editors") eines ausstehenden Signierungsauftrags zu aktualisieren. Dies ermöglicht es einem externen Signierungsdienst, Änderungen in GEVER vorzunehmen und die betroffenen Personen entsprechend anzupassen.

    **Beispiel-Request**:

    .. code-block:: http

        PATCH /@update-pending-signing-job HTTP/1.1
        Content-Type: application/json
        Authorization: Bearer <access_token>

        {
            "access_token": "12345",
            "signature_data": {
                "editors": ["new-editor@example.com"]
                "signatures": [{
                    "email": "foo@example.com",
                    "status": "signed",
                    "signed_at": "2025-01-28T15:00:00.000Z",
                }]
            }
        }

- ``access_token``: Das beim Start des Signaturprozesses generierte Token.
- ``signature_data`` (erforderlich): Ein Objekt, das die zu aktualisierenden Felder enthält.
  - ``editors`` (optional): Eine Liste von E-Mail-Adressen der neuen Bearbeitenden. Wenn nicht angegeben, bleibt die Liste der Bearbeitenden unverändert.
  - ``signatures`` (optional): Eine Liste von Signierenden und deren Signierungs-Status.

**Hinweise**

- Die Aktualisierung gilt nur für ausstehende Signierungsaufträge und hat keine Auswirkungen auf bereits abgeschlossene Vorgänge.

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

Informationen über die Signaturen abrufen
-----------------------------------------
Ein GET-Request auf ein Dokument stellt verschiedene Informationen zu einem aktuellen Signierungs-Auftrag oder zu bereits signierten Versionen zur Verfügung:

  .. sourcecode:: http

    GET /ordnungssystem/dossier-23/document-21 HTTP/1.1
    Accept: application/json

  .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "@id": "/ordnungssystem/dossier-23/document-21",
        "...": "...",
        "pending_signing_job": {
            "created": "2024-02-18T15:45:00",
            "userid": "foo.bar",
            "version": 4,
            "editors": [
                {
                    "email": "bar.foo@example.com",
                    "userid": "bar.foo"
                }
            ],
            "signatures": [
                {
                    "email": "bar.foo@example.com",
                    "signed_at": "2025-01-28T15:00:00.000Z",
                    "status": "signed",
                    "userid": "bar.foo"
                }
            ],
            "job_id": "1",
            "redirect_url": "redirect@example.com"
        },
        "signatures_by_version": {
            "1": {
                "id": "abc-123",
                "version": 1,
                "created": "2024-02-18T15:45:00",
                "signatories": [
                    {
                        "email": "bar@example.com",
                        "userid": "bar.example"
                        "signed_at": "2025-01-28T15:00:00.000Z"
                    },
                    {
                        "email": "foor@example.com",
                        "userid": ""
                        "signed_at": "2025-01-30T15:00:00.000Z"
                    }
                ]
            }
        }
    }

**Wichtige:**

Die Version eines aktuellen Signierungs-Auftrages (``pending_signing_job``) zeigt an, welche Version von den Benutzern signiert wird.
Wenn alle Benutzer das Dokument signiert haben, wird eine neue Version vom Dokument mit dem signierten Dokument erstellt.
Die Versionen unter den ``signatures_by_version`` zeigt an, welche Versionen effektiv die signierten Daten enthalten.
