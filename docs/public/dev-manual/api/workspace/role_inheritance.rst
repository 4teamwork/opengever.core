.. _role_inheritance:

Ordnerberechtigungen
====================

Teamraum-Ordner besitzen grundsätzlich die gleichen Rechte, wie der Teamraum selbst. Die Berechtigungen können jedoch explizit unterbrochen und neu gesetzt werden. Dazu wird der ``@role-inheritance`` Endpoint verwendet.

Vererbungsstatus überprüfen:
----------------------------
Ein GET Request auf den ``@role-inheritance`` Endpoint gibt zurück, ob die Vererbung momentan unterbrochen ist oder nicht:

**Beispiel-Request**:

   .. sourcecode:: http

       GET /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": false
    }

Vererbung unterbrechen:
-----------------------
Mit einem POST Request kann die Rollenvererbung unterbrochen werden.

Wird eine Vererbung unterbrochen, wird der aktuelle Benutzer als neuen und einzigen Admin hinzugefügt.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": true
       }

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true
    }


Vererbung unterbrechen mit Rollen-Kopie
---------------------------------------
Mit der Option `copy_roles` auf dem @role-inheritance Endpoint werden bestehende Berechtigungen nach dem Unterbrechen der
Vererbung automatisch kopiert.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": true,
         "copy_roles": true
       }

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true,
    }

Berechtigungen vererben:
------------------------
Sollen die Berechtigungen wieder vom übergeordneten Objekt vererbt werden, wird ein folgender POST Request verwendet.

ACHTUNG: Lokale Berechtigungen werden dadurch komplett gelöscht und können nicht mehr wiederhergestellt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": false,
       }

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true
    }
