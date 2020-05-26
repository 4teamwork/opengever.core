Sharing
=======

Die lokalen Rollen können mit dem ``@sharing`` Endpoint abgefragt werden. Um die lokalen Rollen aufzulisten, wenn man keine Berechtigungen zum Bearbeiten hat, muss man den Parameter `ignore_permissions=True` setzen.

**Beispiel-Request**:

    GET /ordnungssystem/fuehrung/dossier-23/@sharing?ignore_permissions=True HTTP/1.1
    Accept: application/json


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Accept: application/json

      {
        "available_roles": [
            {
                "id": "Reader",
                "title": "Lesen"
            },
            {
                "id": "Contributor",
                "title": "Hinzufügen"
            }
        ],
        "entries": [
            {
                "automatic_roles": {
                    "Contributor": false,
                    "Reader": false
                },
                "computed_roles": {
                    "Contributor": "acquired",
                    "Reader": "acquired"
                },
                "disabled": false,
                "id": "og_demo-ftw_users",
                "login": null,
                "ogds_summary": {
                    "@id": "http://localhost:8080/fd/kontakte/@ogds-groups/og_demo-ftw_users",
                    "@type": "virtual.ogds.group",
                    "active": true,
                    "groupid": "og_demo-ftw_users",
                    "title": null
                },
                "roles": {
                    "Contributor": false,
                    "Reader": false
                },
                "title": "og_demo-ftw_users",
                "type": "group",
                "url": "http://localhost:8080/fd/@@list_groupmembers?group=og_demo-ftw_users"
            }
        ],
        "inherit": true
      }
