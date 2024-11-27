Berechtigungsreports
====================

Der ``@role-assignment-reports`` bietet Funktionen für die Auflistung, das Erstellen und das Löschen von Berechtigungsreports. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung und ist mit einer Berechtigung geschützt: ``opengever.api.ManageRoleAssignmentReports``
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
            "principal_id": "robert.ziegler",
            "report_id": "report_2",
            "state": "in progress"
          },
          {
            "@id": "http://localhost:8080/fd/@role-assignment-reports/report_1",
            "modified": "2020-04-03T01:34:27+00:00",
            "principal_type": "group",
            "principal_id": "afi_benutzer",
            "report_id": "report_1",
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
        "referenced_roles": [
          {
            "id": "Contributor",
            "title": "Hinzufügen"
          },
          {
            "id": "Reviewer",
            "title": "Veröffentlichen"
          },
          {
            "id": "Editor",
            "title": "Bearbeiten"
          },
          {
            "id": "Reader",
            "title": "Ansehen"
          }
        ],
        "items": [
          {
            "UID": "ea02348a43fd4c9ebcf86f0a1f739923",
            "roles": [
              "Editor"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/bevoelkerung-und-sicherheit/einwohnerkontrolle/dossier-1/dossier-2",
            "title": "Aktuelle Situation"
          },
          {
            "UID": "63bf84e9e07b4702abaf3bd78ca45326",
            "roles": [
              "Contributor",
              "Reader"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/fuehrung/interne-organisation/planung-und-organisatorisches/dossier-3",
            "title": "Wichtige Information"
          },
          {
            "UID": "3761453132dc4ced9b0a758c3b978802",
            "roles": [
              "Contributor",
              "Reviewer",
              "Editor"
            ],
            "url": "http://localhost:8080/fd/ordnungssystem/bevoelkerung-und-sicherheit/einbuergerungen",
            "title": "Einbürgerungen"
          }
        ],
        "items_total": 3,
        "modified": "2020-04-03T01:34:27+00:00",
        "principal_type": "group",
        "principal_id": "afi_benutzer",
        "report_id": "report_1",
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
         "principal_id": "robert.ziegler"
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
        "principal_id": "robert.ziegler",
        "report_id": "report_7",
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

Berechtigungsreport-Abfrage
---------------------------

Mittels eines GET-Requests können die Daten für einen spezifischen Berechtigungsreport abgerufen werden, der für die Darstellung im neuen UI benötigt wird. Der Endpoint unterstützt verschiedene Filterkriterien, um gezielte Berichte zu erstellen

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@role-assignment-report HTTP/1.1
       Accept: application/json

       {
         "principal_ids":["hugo.boss"]
         "include_memberships": true,
         "root": "abca20b04af54d2cbb2816545333e555"
       }

**Beispiel-Response**:

   .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
          "@id": "http://localhost:8081/fd/@role-assignment-report?b_size=25&b_start=0&filters.principal_id:record:list=hugo.boss&filters.root:record=abca20b04af54d2cbb2816545333e555&filters.include_memberships:record:boolean=true",
          "items": [
            {
                "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1",
                "@type": "opengever.dossier.businesscasedossier",
                "UID": "createtreatydossiers000000000001",
                "description": "Alle aktuellen Vertr\xe4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.",
                "is_leafnode": null,
                "reference": "Client1 1.1 / 1",
                "review_state": "dossier-state-active",
                "role_Contributor": [],
                "role_DossierManager": [],
                "role_Editor": [],
                "role_Publisher": [],
                "role_Reader": [],
                "role_Reviewer": [],
                "role_Role Manager": [],
                "role_TaskResponsible": ["regular_user"],
                "title": "Vertr\xe4ge mit der kantonalen Finanzverwaltung"
            },
            {
                "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-17",
                "@type": "opengever.dossier.businesscasedossier",
                "UID": "createprotecteddossiers000000003",
                "description": "Schl\xe4cht",
                "is_leafnode": null,
                "reference": "Client1 1.1 / 11",
                "review_state": "dossier-state-active",
                "role_Contributor": [],
                "role_DossierManager": [],
                "role_Editor": [],
                "role_Publisher": [],
                "role_Reader": [],
                "role_Reviewer": [],
                "role_Role Manager": [],
                "role_TaskResponsible": ["regular_user"],
                "title": "Zu allem \xdcbel"
            },
            {
                "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-5",
                "@type": "opengever.dossier.businesscasedossier",
                "UID": "createexpireddossier000000000001",
                "description": "Abgeschlossene Vertr\xe4ge vor 2000.",
                "is_leafnode": null,
                "reference": "Client1 1.1 / 2",
                "review_state": "dossier-state-resolved",
                "role_Contributor": [],
                "role_DossierManager": [],
                "role_Editor": [],
                "role_Publisher": [],
                "role_Reader": [],
                "role_Reviewer": [],
                "role_Role Manager": [],
                "role_TaskResponsible": ["regular_user"],
                "title": "Abgeschlossene Vertr\xe4ge"
            },
            {
                "@id": "http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-6",
                "@type": "opengever.dossier.businesscasedossier",
                "UID": "createinactivedossier00000000001",
                "description": "Inaktive Vertr\xe4ge von 2016.",
                "is_leafnode": null,
                "reference": "Client1 1.1 / 3",
                "review_state": "dossier-state-inactive",
                "role_Contributor": [],
                "role_DossierManager": [],
                "role_Editor": [],
                "role_Publisher": [],
                "role_Reader": [],
                "role_Reviewer": [],
                "role_Role Manager": [],
                "role_TaskResponsible": ["regular_user"],
                "title": "Inaktive Vertr\xe4ge"
            }
          ],
        "items_total": 4,
        "referenced_roles": [
            {"id": "Reader", "title": "Read"},
            {"id": "Contributor", "title": "Add dossiers"},
            {"id": "Editor", "title": "Edit dossiers"},
            {"id": "Reviewer", "title": "Resolve dossiers"},
            {"id": "Publisher", "title": "Reactivate dossiers"},
            {"id": "DossierManager", "title": "Manage dossiers"},
            {"id": "TaskResponsible", "title": "Task responsible"},
            {"id": "Role Manager", "title": "Role manager"}]
        }


Paginierung
~~~~~~~~~~~
Die Paginierung funktioniert gleich wie bei anderen Auflistungen auch (siehe :ref:`Kapitel Paginierung <batching>`).
