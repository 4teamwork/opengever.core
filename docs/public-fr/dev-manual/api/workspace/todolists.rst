.. _todolists:

Listes de ToDos
===============

Les listes de ToDos servent comme moyen de regroupement de ToDos. Elles peuvent être créées, lues, modifiées et effacées via des :ref:`operations` REST. Pour l'effacement, il est à noter que seules les listes vides peuvent être effacées.

Séquence
--------
La séquence des ``items`` retournée lors d'une Request GET d'un teamraum correspond au tri actuel des contenus.

**Exemple de Request**:


   .. sourcecode:: http

      GET workspaces/workspace-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@type": "opengever.workspace.workspace",
        "title": "Projekt XY",
        "id": "workspace-1"
        "responsible": "john.doe",
        "items": [
            {
              "@id": "workspaces/workspace-1/todolist-6",
              "@type": "opengever.workspace.todolist",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Allgemeine Projektinformationen"
            },
            {
              "@id": "workspaces/workspace-1/todolist-10",
              "@type": "opengever.workspace.todolist",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Konzept Phase"
            },
            {
              "@id": "workspaces/workspace-1/todolist-2",
              "@type": "opengever.workspace.todolist",
              "description": "",
              "review_state": "opengever_workspace_todolist--STATUS--active",
              "title": "Externe Abklärungen"
            }
        ]
      }


Modifier l'ordre
~~~~~~~~~~~~~~~~
Le tri de listes de ToDos au niveau teamraum peut être modifié au moyen d'une Request PATCH en utilisant le paramètre ``ordering``et la Key ``obj_id`` pour indiquer quelle liste doit être réordonnée. La key ``delta`` accepte les valeurs ``top``, ``bottom`` ou en entier positif ou négatif pour le déplacement d'une liste evrs le haut ou bas.

Il est recommandé d'utiliser la Key ``subset_ids`` pour ne modifier qu'un lot restreint de ressources, p.ex. toutes les listes de ToDos. De plus, l'utiisation de ``subset_ids`` assure un comportement d'erreurs correct lors de traitements quasi concurrents. Pour plus d'informations concernant le tri d'objets se trouve dans la `documentation plone.restapi <https://plonerestapi.readthedocs.io/en/latest/content.html?highlight=position#reordering-sub-resources>`_.

**Exemple de Request**:

   .. sourcecode:: http

      GET workspaces/workspace-1 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "ordering": {
          "obj_id": "todolist-1",
          "delta": "2",
          "subset_ids": ["todolist-1", "todolist-2", "todolist-3", "todolist-4"]
        }

      }



**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Déplacer des ToDos dans une liste
---------------------------------
Pour déplacer des ToDos individuels au sein d'une liste, il suffit d'envoyer une Request POST à l'Endpoint ``@move`` de l'objet-cible. L'objet à déplacer doit être spécifié dans le Request-Body, via la Key ``source``. Il peut être spécifié par son URL, chemin, UID ou intid.

**Exemple de Request**:


   .. sourcecode:: http

      POST workspaces/workspace-1/todolist-4/@move HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "source": "http://nohost/plone/workspaces/workspace-3/todo-1323"
      }



**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
