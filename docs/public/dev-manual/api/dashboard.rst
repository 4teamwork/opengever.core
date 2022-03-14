.. _dashboard:

Dashboard Konfiguration
=======================

Über den ``/@dashboard-settings`` Endpoint kann die aktuelle Konfiguration des Dashboards abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@dashboard-settings HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "cards": [
              {
                  "id": "newest_gever_notifications",
                  "componentName": "NewestGeverNotificationsCard"
              },
              {
                  "id": "recently_touched_items"
                  "componentName": "RecentlyTouchedItemsCard"
              },
              {
                  "id": "my_dossiers"
                  "componentName": "DossiersCard"
              }
          ]
      }
