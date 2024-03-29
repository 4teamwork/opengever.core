Liste der verfügbaren DocProperties
-----------------------------------

Mit DocProperties können ausgewählte Metadaten aus Dossiers von OneGov GEVER
direkt in Worddokumenten übernommen werden. Die Metadaten wurden im Rahmen des
Releases 3.10 starkt ausgebaut und mit dem Präfix ``ogg`` versehen.
Die folgenden Metadaten werden von OneGov GEVER beim Öffnen von Worddokumenten automatisch weitergegeben:

Doc-Properties aktueller Benutzer:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``ogg.user.userid``
- ``ogg.user.title``
- ``ogg.user.firstname``
- ``ogg.user.lastname``
- ``ogg.user.department``
- ``ogg.user.department_abbr``
- ``ogg.user.directorate``
- ``ogg.user.directorate_abbr``
- ``ogg.user.email``
- ``ogg.user.email2``
- ``ogg.user.url``
- ``ogg.user.phone_office``
- ``ogg.user.phone_fax``
- ``ogg.user.phone_mobile``
- ``ogg.user.salutation``
- ``ogg.user.description``
- ``ogg.user.address1``
- ``ogg.user.address2``
- ``ogg.user.zip_code``
- ``ogg.user.city``
- ``ogg.user.country``

Doc-Properties Dossier:
~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.dossier.title`` - Titel des Dossiers, welches das Dokument enthält
- ``ogg.dossier.reference_number`` - Aktenzeichen des Dossiers, welches das Dokument enthält
- ``ogg.dossier.sequence_number`` - Laufnummer des Dossiers
- ``ogg.dossier.external_reference`` - Externe Referenz, welches das Dokument enthält

Doc-Properties Dokument:
~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.document.title`` - Titel des Dokumentes
- ``ogg.document.reference_number`` - Aktenzeichen des Dokuments
- ``ogg.document.sequence_number`` - Laufnummer des Dokuments
- ``ogg.document.document_author``
- ``ogg.document.document_date``
- ``ogg.document.document_type`` - Dokumenttyp des Dokuments
- ``ogg.document.reception_date``
- ``ogg.document.delivery_date``
- ``ogg.document.version_number``
- ``ogg.document.document.creator.user.*`` - Doc-Properties des Benutzers, der das Dokument erstellt hat. Es werden die gleichen Doc-Property-Information wie beim aktuellen Benutzer verwendet, siehe `Doc-Properties aktueller Benutzer:`_


Doc-Properties Custom Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Custom Properties von Dossiers und Dokumenten können auch als DocProperties verwendet werden. Welche genau zur Verfügung stehen, muss konfiguriert werden.

- ``ogg.document.cp.*`` - * muss mit Name des Custom Property ersetzt werden
- ``ogg.dossier.cp.*`` - * muss mit Name des Custom Property ersetzt werden

Doc-Properties Sitzung Antrag/Traktandum:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.meeting.decision_number`` - Beschlussnummer des Traktandums
- ``ogg.meeting.agenda_item_number`` - Nummer des Traktandums in dieser Sitzung
- ``ogg.meeting.agenda_item_number_raw`` - Nummer des Traktandums in dieser Sitzung (unformattiert)
- ``ogg.meeting.proposal_title`` - Titel des Antrags
- ``ogg.meeting.proposal_description`` - Beschreibung des Antrags
- ``ogg.meeting.proposal_state`` - Status des Antrags


.. note::
    Bei folgenden DocProperties muss eine spezifische Konfiguration vorgenommen
    werden, damit diese eingesetzt werden können.

Doc-Properties alle Empfänger:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.contact.title`` - Name der Organisation / zusammengesetzter Name der Person
- ``ogg.recipient.contact.description``

Doc-Properties Empfänger Person:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.person.salutation``
- ``ogg.recipient.person.firstname``
- ``ogg.recipient.person.lastname``
- ``ogg.recipient.person.academic_title``

Doc-Properties Empfänger Organisation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.organization.name``

Doc-Properties Empfänger Organisationsbeziehung:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.orgrole.function``
- ``ogg.recipient.orgrole.department``
- ``ogg.recipient.orgrole.description``

Doc-Properties Empfänger Adresse/Tel./E-Mail/URL/Geschlecht/Geburtsdatum:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.address.street``
- ``ogg.recipient.address.zip_code``
- ``ogg.recipient.address.city``
- ``ogg.recipient.address.country``
- ``ogg.recipient.phone.number``
- ``ogg.recipient.email.address``
- ``ogg.recipient.url.url``
- ``ogg.recipient.person.sex``
- ``ogg.recipient.person.date_of_birth``

Doc-Properties alle Absender:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.sender.contact.title`` - Name der Organisation / zusammengesetzter Name der Person
- ``ogg.sender.contact.description``

Doc-Properties Absender Person:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.sender.person.salutation``
- ``ogg.sender.person.firstname``
- ``ogg.sender.person.lastname``
- ``ogg.sender.person.academic_title``

Doc-Properties Absender Organisation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.sender.organization.name``

Doc-Properties Absender Organisationsbeziehung:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.sender.orgrole.function``
- ``ogg.sender.orgrole.department``
- ``ogg.sender.orgrole.description``

Doc-Properties Absender Adresse/Tel./E-Mail/URL/Geschlecht/Geburtsdatum:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.sender.address.street``
- ``ogg.sender.address.zip_code``
- ``ogg.sender.address.city``
- ``ogg.sender.address.country``
- ``ogg.sender.phone.number``
- ``ogg.sender.email.address``
- ``ogg.sender.url.url``
- ``ogg.sender.person.sex``
- ``ogg.sender.person.date_of_birth``

Doc-Properties alle Beteiligungen:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bei den Beteiligungen muss ``*role*` mit der Rolle ersetzt werden, beispielsweise mit ``final-drawing``.

- ``ogg.*role*.contact.title`` - Name der Organisation / zusammengesetzter Name der Person
- ``ogg.*role*.contact.description``

Doc-Properties Beteiligungen Person:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.*role*.person.salutation``
- ``ogg.*role*.person.firstname``
- ``ogg.*role*.person.lastname``
- ``ogg.*role*.person.academic_title``

Doc-Properties Beteiligungen Organisation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.*role*.organization.name``

Doc-Properties Beteiligungen Organisationsbeziehung:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.*role*.orgrole.function``
- ``ogg.*role*.orgrole.department``
- ``ogg.*role*.orgrole.description``

Doc-Properties Beteiligungen Adresse/Tel./E-Mail/URL/Geschlecht/Geburtsdatum:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.*role*.address.street``
- ``ogg.*role*.address.zip_code``
- ``ogg.*role*.address.city``
- ``ogg.*role*.address.country``
- ``ogg.*role*.phone.number``
- ``ogg.*role*.email.address``
- ``ogg.*role*.url.url``
- ``ogg.*role*.person.sex``
- ``ogg.*role*.person.date_of_birth``

Die folgenden Doc-Properties sind deprecated, und sollten deshalb nicht mehr verwendet werden:

- ``Dossier.ReferenceNumber`` – Aktenzeichen des Dossiers, welches das Dokument
  enthält
- ``Document.ReferenceNumber`` – Aktenzeichen des Dokuments
- ``Document.SequenceNumber`` – Laufnummer des Dokuments
- ``User.FullName`` – Vor- und Nachname des angemeldeten Benutzers
- ``Dossier.Title`` – Titel des Dossiers, welches das Dokument enthält
- ``User.ID`` – Benutzerkennung des angemeldeten Benutzers
