.. _navigation:

Navigation
==========

Über den ``/@navigation`` Endpoint kann ein beliebiger Navigationsbaum des GEVER-Mandanten abgefragt werden.

Standardmässig wird der Ordnungssystem-Baum zurückgegeben.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@navigation HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/ordnungssystem/@navigation",
          "tree": [
              {
                  "@type": "opengever.repository.repositoryfolder",
                  "active": true,
                  "current": false,
                  "current_tree": false,
                  "description": "",
                  "nodes": [
                      {
                          "@type": "opengever.repository.repositoryfolder",
                          "active": true,
                          "current": false,
                          "current_tree": false,
                          "description": "",
                          "nodes": [
                              {
                                  "@type": "opengever.repository.repositoryfolder",
                                  "active": true,
                                  "current": false,
                                  "current_tree": false,
                                  "description": "",
                                  "nodes": [],
                                  "text": "9.5.0. Allgemeines",
                                  "uid": "103f443655c64b01b9cec25b09f6192a",
                                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict/allgemeines"
                              },
                              {
                                  "@type": "opengever.repository.repositoryfolder",
                                  "active": true,
                                  "current": false,
                                  "current_tree": false,
                                  "description": "",
                                  "nodes": [],
                                  "text": "9.5.1. Informatik",
                                  "uid": "c68e1ebba5204d67b1c38e20aebfba7e",
                                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict/informatik"
                              },
                              {
                                  "@type": "opengever.repository.repositoryfolder",
                                  "active": true,
                                  "current": false,
                                  "current_tree": false,
                                  "description": "",
                                  "nodes": [],
                                  "text": "9.5.2. Telefonie",
                                  "uid": "9da54abbd5f4406f837a976fc20670a7",
                                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict/telefonie"
                              }
                          ],
                          "text": "9.5. ICT",
                          "uid": "2cc58378c6bd4be985d4c7fe1d1067fb",
                          "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict"
                      }
                  ],
                  "text": "9. Ressourcen und Support",
                  "uid": "c4ef803020d145c8a282ee65a081d00c",
                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support"
              }
          ]
      }

Bei mehreren Ordnungssystemen wird jeweils das dem URL-Kontext entsprechende zurückgegeben.

Die Navigation kann beim Abfragen eines Inhaltes über den ``expand``-Parameter eingebettet werden,
so dass keinezusätzliche Abfrage nötig ist.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /ordnungssystem?expand=navigation HTTP/1.1
       Accept: application/json

Für einen personalisierten Navigationsbaum können die Parameter `root_interface` und `content_interfaces` verwendet werden.

Ein Navigationsbaum eines Arbeitsraumes kann wie folgt abgefragt werden:


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@navigation?root_interface=opengever.workspace.interfaces.IWorkspace&content_interfaces=opengever.workspace.interfaces.IWorkspaceFolder HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@navigation",
          "tree": [
              {
                  "active": true,
                  "current": false,
                  "current_tree": false,
                  "description": "",
                  "nodes": [],
                  "text": "",
                  "uid": "8dee9268d10f4b2db742fb52ebefdd03",
                  "url": "http://localhost:8080/fd/workspaces/workspace-1/folder-1"
              }
          ]
      }

Über den Parameter `include_root` kann das Root-Objekt im Navigationsbaum hinzugefügt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@navigation?include_root=true&root_provides=opengever.workspace.interfaces.IWorkspace&content_provides=opengever.workspace.interfaces.IWorkspaceFolder HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/workspaces/workspace-1/@navigation",
          "tree": [
              {
                  "active": true,
                  "current": false,
                  "current_tree": false,
                  "description": "",
                  "nodes": [
                      {
                          "active": true,
                          "current": false,
                          "current_tree": false,
                          "description": "",
                          "nodes": [],
                          "text": "",
                          "uid": "8dee9268d10f4b2db742fb52ebefdd03",
                          "url": "http://localhost:8080/fd/workspaces/workspace-1/folder-1"
                      }
                  ],
                  "text": "",
                  "uid": "f93938316a524fa5ac59f3b98506b47c",
                  "url": "http://localhost:8080/fd/workspaces/workspace-1"
              }
          ]
      }
