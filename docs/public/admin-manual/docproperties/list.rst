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

Doc-Properties Sitzung Antrag/Traktandum:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.meeting.decision_number`` - Beschlussnummer des Traktandums
- ``ogg.meeting.agenda_item_number`` - Nummer des Traktandums in dieser Sitzung
- ``ogg.meeting.proposal_title`` - Titel des Antrags
- ``ogg.meeting.proposal_description`` - Beschreibung des Antrags
- ``ogg.meeting.proposal_state`` - Status des Antrags

Neu kann beim Erstellen eines Dokumentes ab Vorlage ein Empfänger angegeben werden. Dies setzt jedoch voraus, dass das neue SQL-basierte Kontaktmodul verwendet wird. Von diesem Empfänger werden die folgenden Doc-Properties geschrieben:

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

Doc-Properties Empfänger Adresse/Tel./E-Mail/URL:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.address.street``
- ``ogg.recipient.address.zip_code``
- ``ogg.recipient.address.city``
- ``ogg.recipient.address.country``
- ``ogg.recipient.phone.number``
- ``ogg.recipient.email.address``
- ``ogg.recipient.url.url``

Die folgenden Doc-Properties sind deprecated, und sollten deshalb nicht mehr verwendet werden:

- ``Dossier.ReferenceNumber`` – Aktenzeichen des Dossiers, welches das Dokument
  enthält
- ``Document.ReferenceNumber`` – Aktenzeichen des Dokuments
- ``Document.SequenceNumber`` – Laufnummer des Dokuments
- ``User.FullName`` – Vor- und Nachname des angemeldeten Benutzers
- ``Dossier.Title`` – Titel des Dossiers, welches das Dokument enthält
- ``User.ID`` – Benutzerkennung des angemeldeten Benutzers

.. disqus::
