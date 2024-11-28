Berechtigungsreports
====================

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
