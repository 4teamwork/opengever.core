.. _content-types:

Inhaltstypen
============

.. contents::
   :local:
   :backlinks: none


.. _translated-titles:

Übersetzte Titel
----------------

Die Felder für übersetzte Titel der Inhalte sind der Vollständigkeit halber
in der Dokumentation alle aufgeführt. Je nach konfigurierter Sprache auf den
Systemen stehen sie aber nicht alle zur Verfügung. Betroffen davon sind die
Felder ``title_de`` und ``title_fr``. Eine Abfrage auf den ``@schema`` Endpoint
liefert die aktuell gültigen Schemas eines Deployments.
Das Erstellen und Modifizieren von Inhalten mittels ``POST`` oder ``PATCH``
erlaubt immer alle übersetzten Felder.


Schemas
-------

.. role:: required
.. role:: field-title
.. role:: small-comment


Ordnungssystem
^^^^^^^^^^^^^^^^

.. include:: schemas/opengever.repository.repositoryroot.inc

--------------------


Ordnungsposition
^^^^^^^^^^^^^^^^

.. include:: schemas/opengever.repository.repositoryfolder.inc

--------------------


.. _label-dossier-schema:

Geschäftsdossier
^^^^^^^^^^^^^^^^

.. include:: schemas/opengever.dossier.businesscasedossier.inc

--------------------



Dokument
^^^^^^^^

.. include:: schemas/opengever.document.document.inc

--------------------



Mail
^^^^

.. include:: schemas/ftw.mail.mail.inc

--------------------



Kontakt
^^^^^^^

.. include:: schemas/opengever.contact.contact.inc

--------------------



Aufgabe
^^^^^^^

.. include:: schemas/opengever.task.task.inc



Anträge
^^^^^^^

.. include:: schemas/opengever.meeting.proposal.inc


Teamraum-Root
^^^^^^^^^^^^^

.. include:: schemas/opengever.workspace.root.inc


Teamraum
^^^^^^^^

.. include:: schemas/opengever.workspace.workspace.inc


Teamraum-Ordner
^^^^^^^^^^^^^^^

.. include:: schemas/opengever.workspace.folder.inc

--------------------

.. disqus::
