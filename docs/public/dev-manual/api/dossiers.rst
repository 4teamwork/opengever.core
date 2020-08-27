.. _dossiers:

Dossiers
========

Dossiers können über die REST-API gem. Kapitel :ref:`operations` bedient werden. Zusätzlich stehen folgende Funktionen für Dossiers zur Verfügung.


Dossier übertragen
------------------

Der Dossier-Verantwortliche kann über den Endpoint ``@transfer-dossier`` an eine neue Person übertragen werden. Dabei wird überprüft, ob ``old_userid`` der aktuelle Dossier-Verantwortliche ist. Ist dies der Fall, wird der Benutzer mit der User-ID ``new_userid`` als neuer Verantwortlicher gesetzt.
Benachrichtigungen, die normalerweise bei einer Änderung ausgelöst werden, werden unterdrückt. Dieser Endpoint wird mit einer Berechtigung geschützt: ``opengever.api.TransferAssignment``
Die Berechtigung ist standardmässig den Rollen `Administrator` und `Manager` zugewiesen.

Standardmässig werden auch Subossiers, welche explizit auf den früheren Benutzer gesetzt waren, auf den neuen Verantwortlichen übertragen.

**Beispiel-Request**:

   .. sourcecode:: http

      POST /dossier-1/@transfer-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "old_userid": "john.doe",
        "new_userid": "robert.ziegler"
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content

Übertragen von Subdossiers unterbinden
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Über die Option ``recursive`` kann gesteuert werden, ob Subdossiers auch übertragen werden sollen, oder nicht.

Standardmässig ist diese Option aktiviert.


**Beispiel-Request**:

   .. sourcecode:: http

      POST /dossier-1/@transfer-dossier HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "old_userid": "john.doe",
        "new_userid": "robert.ziegler",
        "recursive": false
      }


**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No content
