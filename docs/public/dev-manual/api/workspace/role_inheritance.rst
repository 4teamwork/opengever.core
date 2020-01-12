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

Wird eine Vererbung unterbrochen, werden initial alle bisherigen Berechtigungen für den Ordner kopiert.

**Beispiel-Request**:

   .. sourcecode:: http

       POST /workspace-1/folder-1/@role-inheritance HTTP/1.1
       Accept: application/json

       {
         "blocked": true,
       }

**Beispiel-Response**:


   .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "blocked": true
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
