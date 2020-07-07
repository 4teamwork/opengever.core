.. _workspace_responsible:

Teamraum Besitzer
=================

Der Besitzer eines Teamraums ist standardmässig der Benutzer, welcher den Teamraum erstellt hat.

Besitzer ändern
---------------

Ein Benutzer kann mittels POST-Requests als neuer Besitzer eines Teamraums festgelegt werden.

**Beispiel-Request**:

.. sourcecode:: http

   POST /workspaces/workspace/@change-responsible HTTP/1.1
   Accept: application/json

   {
     "userid": "peter.mueller"
   }

**Beispiel-Response**:

.. sourcecode:: http

   HTTP/1.1 204 No content

Nur Administratoren eines Teamraums können den Besitzer eines Teamraums ändern.
