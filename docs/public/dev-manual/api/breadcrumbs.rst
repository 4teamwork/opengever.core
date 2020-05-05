.. _breadcrumbs:

Breadcrumbs
===========

Über den ``@breadcrumbs`` Endpoint können die Breadcrumbs eines beliebigen Inhalts abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22/@breadcrumbs HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/document-22/@breadcrumbs",
          "items": [
              {
                  "@id": "http://localhost:8080/fd/ordnungssystem",
                  "@type": "opengever.repository.repositoryroot"
                  "description": "",
                  "is_leafnode": null,
                  "review_state": "repositoryroot-state-active",
                  "title": "Ordnungssystem",
              },
              {
                  "@id": "http://localhost:8080/fd/ordnungssystem/fuhrung",
                  "@type": "opengever.repository.repositoryfolder"
                  "description": "Alles zum Thema F\\u00fchrung.",
                  "is_leafnode": false,
                  "review_state": "repositoryfolder-state-active",
                  "title": "1. F\\u00fchrung",
              },
              {
                  "@id": "http://localhost:8080/fd/ordnungssystem/fuhrung/vertrage-und-vereinbarungen",
                  "@type": "opengever.repository.repositoryfolder"
                  "description": "",
                  "is_leafnode": true,
                  "review_state": "repositoryfolder-state-active",
                  "title": "1.1. Vertr\\u00e4ge und Vereinbarungen",
              },
              {
                  "@id": "http://localhost:8080/fd/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1",
                  "@type": "opengever.dossier.businesscasedossier"
                  "description": "Alle aktuellen Vertr\\u00e4ge mit der kantonalen Finanzverwaltung sind hier abzulegen. Vertr\\u00e4ge vor 2016 geh\\u00f6ren ins Archiv.",
                  "is_leafnode": null,
                  "is_subdossier": false,
                  "review_state": "dossier-state-active",
                  "title": "Vertr\\u00e4ge mit der kantonalen Finanzverwaltung",
              }, {
                  "@id": "http://localhost:8080/fd/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2",
                  "@type": "opengever.dossier.businesscasedossier"
                  "description": "",
                  "is_leafnode": null,
                  "is_subdossier": true,
                  "review_state": "dossier-state-active",
                  "title": "2016",
              }
          ],
      }


Die Breadcrumbs können beim Abfragen eines Inhaltes über den ``expand``-Parameter eingebettet werden,
so dass keine zusätzliche Abfrage nötig ist.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem?expand=breadcrumbs HTTP/1.1
       Accept: application/json
