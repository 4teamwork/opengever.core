Rollenzuweisungs-Berichte
=========================

Der ``@role-assignment-reports`` bietet Funktionen für die Auflistung, das Erstellen und das Löschen von Rollenzuweisungs-Berichten. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung und ist mit einer Berechtigung geschützt: ``opengever.api.ManageRoleAssignmentReports``
Die Berechtigung ist standardmässig den Rollen `Administrator` und `Manager` zugewiesen.


Auflistung
----------

Mittels eines GET-Requests können alle Berichte abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@role-assignment-reports HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "items": [
          {
            "@id": "http://localhost:8080/fd/@role-assignment-reports/report_2",
            "modified": "2020-07-08T14:17:30+00:00",
            "principal_type": "user",
            "principalid": "robert.ziegler",
            "reportid": "report_2",
            "state": "in progress"
          },
          {
            "@id": "http://localhost:8080/fd/@role-assignment-reports/report_1",
            "modified": "2020-04-03T01:34:27+00:00",
            "principal_type": "group",
            "principalid": "afi_benutzer",
            "reportid": "report_1",
            "state": "ready"
          }
        ],
        "items_total": 2
      }

Mittels eines GET-Requests können auch einzelne Berichte abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@role-assignment-reports/report_1 HTTP/1.1
       Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/@role-assignment-reports/report_1",
        "items": [
          {
            "UID": "ea02348a43fd4c9ebcf86f0a1f739923",
            "roles": [
              "Editor"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/bevoelkerung-und-sicherheit/einwohnerkontrolle/dossier-1/dossier-2"
          },
          {
            "UID": "63bf84e9e07b4702abaf3bd78ca45326",
            "roles": [
              "Contributor",
              "Reader"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/fuehrung/interne-organisation/planung-und-organisatorisches/dossier-3"
          },
          {
            "UID": "3761453132dc4ced9b0a758c3b978802",
            "roles": [
              "Contributor",
              "Reviewer",
              "Editor"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/bevoelkerung-und-sicherheit/einbuergerungen"
          }
        ],
        "items_total": 3,
        "modified": "2020-04-03T01:34:27+00:00",
        "principal_type": "group",
        "principalid": "afi_benutzer",
        "reportid": "report_1",
        "state": "ready"
      }


Bericht erstellen
---------------------

Ein Bericht kann mittels POST-Requests angefordert werden. Danach erscheint der Bericht im Status ``in progress``. In einem Nightly-Job werden die Rollenzuweisungen zusammengetragen und der Bericht damit ergänzt. Sobald dies erledigt ist, wird der Status auf ``ready`` gesetzt. Berichte können für Benutzer und für Gruppen angefordert werden.


**Beispiel-Request**:

   .. sourcecode:: http

       POST /@role-assignment-reports HTTP/1.1
       Accept: application/json

       {
         "principalid": "robert.ziegler"
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://localhost:8080/fd/@role-assignment-reports/report_7",
        "items": [],
        "items_total": 0,
        "modified": "2020-07-13T11:43:18+00:00",
        "principal_type": "user",
        "principalid": "robert.ziegler",
        "reportid": "report_7",
        "state": "in progress"
      }


Bericht löschen
--------------------

Mittels DELETE-Requests kann ein Bericht gelöscht werden.

**Beispiel-Request**:

   .. sourcecode:: http

       DELETE /@role-assignment-reports/report_0 HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).
