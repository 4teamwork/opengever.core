.. _role_inheritance:

Droits sur les dossiers
=======================

De base, les dossiers teamraum disopsent du même profil de droits que la teamraum elle-même. Les droits peuvent toutefois être explicitement supprimés et réassignés. Pour cela, on fait appel à l'Endpoint ``@role-inheritance``.

Vérifier l'état d'héritage:
---------------------------
Une Request GET sur l'Endpoint ``@role-inheritance`` retourne si l'héritage est actuellement interrompu ou non. 


**Exemple de Request**:

   .. sourcecode:: http

       GET /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

**Exemple de Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": false
    }

Vererbung unterbrechen:
-----------------------
L'héritage de rôles peut être interrompu avec une Request POST.

Lorsque l'héritage est interrompu, les droits existants sont recopiés sur le dossier. 

**Exemple de Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": true,
       }

**Exemple de Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true
    }


Hériter des droits:
-------------------
Si l'héritage des droits de l'objet parent doit être rétabli, la Request POST suivante est utilisée.

ATTENTION: Les droits locaux seront intégralement effacés et ne peuvent plus être réstaurés. 

**Exemple de Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": false,
       }

**Exemple de Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true
    }
