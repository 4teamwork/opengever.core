.. _reminders:

Rappels de tâches
=================

L'Endpoint ``@reminder`` traite les rappels pour les tâches. Tout utilisateur peut activer ses propres notifications pour chaque tâche.


Sélectionner un rappel:
-----------------------
Un rappel pour l'utilisateur courant peut être sélectionnée à l'aide d'une Request GET.

**Exemple de Request**:

   .. sourcecode:: http

       GET /task-1/@reminder HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK

       {
        "@id": "http://example.onegovgever.ch/ordnungssystem/dossier-20/task-1/@reminder",
        "option_type": "one_day_before",
        "option_title": "One day before deadline",
        "params": {}
       }

Au cas où aucun rappel n'a été défini pour l'utilisateur courant, l'Endpoint retourne l'erreur 404 Not Found:

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 404 Not Found

       {
          "message": "Resource not found: http://example.onegovgever.ch/ordnungssystem/dossier-20/task-1/@reminder",
          "type": "NotFound"
       }

Ajouter un rappel:
------------------
Une Request POST est utilisée pour créer un nouveau rappel. Le body doit contenir l'attribut ``option_type``. Si l'attribut contient une valeur qui n'est pas acceptable, une liste des valeurs supportées est retournée. 


**Exemple de Request**:

   .. sourcecode:: http

       POST /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "one_day_before"
       }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Certains types de rappels requièrent des paramètres additionnels. Ceux-ci peuvent être récupérés de la sous-classe respective. Les paramètres sont donnés en tant que Dictionary, dans la propriété 'params'. 


**Exemple de Request**:

   .. sourcecode:: http

       POST /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "on_date",
        "params": {
            "date": "2019-12-30"
           }
       }


Mettre à jour un rappel:
------------------------
Un rappel existant peut être modifié à l'aide d'une Request PATCH.


**Exemple de Request**:

   .. sourcecode:: http

       PATCH /task-1/@reminder HTTP/1.1
       Accept: application/json

       {
        "option_type": "same_day"
       }


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content


Ôter un rappel:
---------------
Un rappel existant peut être effacé par l'intermédiaire d'une Request DELETE:


**Exemple de Request**:

   .. sourcecode:: http

       DELETE /task-1/@reminder HTTP/1.1
       Accept: application/json


**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
