.. _navigation:

Navigation
==========

Tout arbre de navigation du client/département GEVER peut être récupéré via l'Endpoint ``/@navigation``.

Par défaut, c'est l'arbre du plan de classement qui est retourné. 

**Exemple de Request**:

   .. sourcecode:: http

       GET /@navigation HTTP/1.1
       Accept: application/json

**Exemple de Response**:

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
                                  "text": "9.5.0. Général",
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
                                  "text": "9.5.1. Informatique",
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
                                  "text": "9.5.2. Téléphonie",
                                  "uid": "9da54abbd5f4406f837a976fc20670a7",
                                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict/telefonie"
                              }
                          ],
                          "text": "9.5. ICT",
                          "uid": "2cc58378c6bd4be985d4c7fe1d1067fb",
                          "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support/ict"
                      }
                  ],
                  "text": "9. Ressources et support",
                  "uid": "c4ef803020d145c8a282ee65a081d00c",
                  "url": "http://localhost:8080/fd/ordnungssystem/ressourcen-und-support"
              }
          ]
      }

Pour de systèmes de classement multiples, c'est celui correspondant au contexte URL courant qui est retourné.

Lors de la Request, la navigation peut être intégré via le paramètre ``expand``, de manière à ce qu'aucune requête additionnelle  ne soit nécessaire.

**Exemple de Request**:

   .. sourcecode:: http

       GET /ordnungssystem?expand=navigation HTTP/1.1
       Accept: application/json

Pour un arbre de navigation personnalisé, il est possible d'utiliser les paramètres `root_interface` et `content_interfaces`.

L'arbre de navigation d'un espace de travail peut être récupéré comme suit:

**Exemple de Request**:

   .. sourcecode:: http

       GET /@navigation?root_interface=opengever.workspace.interfaces.IWorkspace&content_interfaces=opengever.workspace.interfaces.IWorkspaceFolder HTTP/1.1
       Accept: application/json

**Exemple de Response**:

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

Le paramètre `include_root` permet d'ajouter un objet Root dans l'arbre de navigation.

**Exemple de Request**:

   .. sourcecode:: http

       GET /@navigation?include_root=true&root_provides=opengever.workspace.interfaces.IWorkspace&content_provides=opengever.workspace.interfaces.IWorkspaceFolder HTTP/1.1
       Accept: application/json

**Exemple de Response**:

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
