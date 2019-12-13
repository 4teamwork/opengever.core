.. _trash:

Corbeille
=========

Déplacer des documents vers la corbeille
----------------------------------------

Les documents peuvent être déplacés vers la corbeille via l'Endpoint ``/@trash``.

**Exemple de Request**:

   .. sourcecode:: http

       POST /ordnungssystem/direction/dossier-23/document-8/@trash HTTP/1.1
       Accept: application/json

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null

Les documents en check-out ou se trouvant dans un dossier clôturé ne peuvent pas être déplacés vers la corbeille.


Restaurer des documents
-----------------------

Les documents se trouvant dans la corbeille peuvent être restaurés via l'Endpoint ``/@untrash``.

**Exemple de Request**:

   .. sourcecode:: http

       POST /ordnungssystem/direction/dossier-23/document-8/@untrash HTTP/1.1
       Accept: application/json

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content

      null
