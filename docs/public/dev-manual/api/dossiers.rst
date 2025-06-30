.. _dossiers:

Dossiers
========

Dossiers können über die REST-API gem. Kapitel :ref:`operations` bedient werden. Zusätzlich stehen folgende Funktionen für Dossiers zur Verfügung.


Dossier übertragen
------------------

Der Dossier-Verantwortliche kann über den Endpoint ``@transfer-dossier`` an eine neue Person übertragen werden. Dabei wird überprüft, ob ``old_userid`` der aktuelle Dossier-Verantwortliche ist. Ist dies der Fall, wird der Benutzer mit der User-ID ``new_userid`` als neuer Verantwortlicher gesetzt.
Benachrichtigungen, die normalerweise bei einer Änderung ausgelöst werden, werden unterdrückt. Dieser Endpoint wird mit einer Berechtigung geschützt: ``opengever.api.TransferAssignment``
Die Berechtigung ist standardmässig den Rollen `Administrator` und `Manager` zugewiesen.

Standardmässig werden auch Subossiers, welche explizit auf den früheren Benutzer gesetzt waren, auf den neuen Verantwortlichen übertragen.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /dossier-1/@transfer-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "old_userid": "john.doe",
        "new_userid": "robert.ziegler"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Übertragen von Subdossiers unterbinden
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Über die Option ``recursive`` kann gesteuert werden, ob Subdossiers auch übertragen werden sollen, oder nicht.

Standardmässig ist diese Option aktiviert.


**Beispiel-Request**:

   .. sourcecode:: http

      POST /dossier-1/@transfer-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "old_userid": "john.doe",
        "new_userid": "robert.ziegler",
        "recursive": false
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Dossier erstellen samt Beteiligungen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Über den ``participations`` Parameter lassen sich Beteiligungen direkt bei der Dossiererstellung miterstellen.
Unterstützt werden dabei die Referenz von bestehenden Kontakten/Benutzern anhand der Kontakt ID im Key
``participant_id``, wie auch die Angabe von Kontaktinformationen. Dabei findet eine Prüfung statt ob dieserr bereits
existiert oder neu erstellt werden muss.


**Beispiel-Request mit participant_id**:

   .. sourcecode:: http

      POST /position-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
         "@type": "opengever.dossier.businesscasedossier",
         "title": "Test 123",
         "responsible": "hugo.boss",
         "participations": [
            {
               "participant_id": "person:6fbef39e-4ad7-50d9-a96c-c0a68a2cf6e6",
               "roles": ["regard", "participation"]
            }
         ]
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


**Beispiel-Request mit Kontaktangaben**:

   .. sourcecode:: http

      POST /position-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
         "@type": "opengever.dossier.businesscasedossier",
         "title": "Test 123",
         "responsible": "hugo.boss",
         "participations": [
            {
               "type": "person",
               "firstName": "Hans",
               "officialName": "Muster",
               "thirdPartyId": "756. XXXX. XXXX. XX",
               "roles": ["regard"]
            }
         ]
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Dossier abschliessen und dabei automatisch alle offenen Aufgaben schliessen
---------------------------------------------------------------------------
Ein Dossier kann über den Workflow abgeschlossen werden. Der Abschluss ist jedoch nur möglich, wenn alle enthaltenen Aufgaben entweder abgeschlossen oder abgebrochen sind. Um diesen Vorgang zu erleichtern, unterstützt der Dossier-Workflow eine Option zum automatischen Schliessen offener Aufgaben.

Wird versucht, ein Dossier mit noch offenen Aufgaben abzuschliessen, ohne diese Option zu nutzen, enthält die Antwort eine entsprechende Fehlermeldung:


**Beispiel-Request**:

   .. sourcecode:: http

      POST /(path)/@workflow/dossier-transition-resolve HTTP/1.1
      Accept: application/json


**Beispiel-Response**:

  .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
         "error": {
            "errors": [
                  "Es sind nicht alle Aufgaben abgeschlossen"
            ],
            "has_not_closed_tasks": true,
            "message": "",
            "type": "PreconditionsViolated"
         }
      }

Um alle offenen Aufgaben beim Dossier-Abschluss automatisch zu schliessen, kann der Parameter ``auto_close_tasks``  mitgegeben werden:


**Beispiel-Request**:

   .. sourcecode:: http

      POST /(path)/@workflow/dossier-transition-resolve HTTP/1.1
      Accept: application/json

      {
        "auto_close_tasks": "true"
      }