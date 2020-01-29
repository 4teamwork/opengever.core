Liste des ProriétéDocs disponibles
----------------------------------

Avec des ProriétéDocs de Microsoft Word (DocProperties en anglais), certaines métadonnées peuvent être directement reprises dans des documents au format Microsoft Word. Dans le cadre de la release 3.10, la sélection de métadonnées mises à disposition par OneGov GEVER (identifiées par le préfixe «ogg»)a été largement étendue. Les métadonnées suivantes sont reprises automatiquement depuis OneGov GEVER lors de l’ouverture de documents Word.

ProriétéDocs de l’utilisateur courant:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

ProriétéDocs d’un Dossier:
~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.dossier.title`` - titre du dossier dont provient le document
- ``ogg.dossier.reference_number`` - référence du dossier dont provient le document
- ``ogg.dossier.sequence_number`` - numéro courant du dossier
- ``ogg.dossier.external_reference`` - référence externe spécifiée pour le dossier

ProriétéDocs d’un Document:
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.document.title`` - titre du document
- ``ogg.document.reference_number`` - numéro de référence du document
- ``ogg.document.sequence_number`` - numéro courant du document
- ``ogg.document.document_author`` - auteur du document
- ``ogg.document.document_date``
- ``ogg.document.document_type`` - type du document
- ``ogg.document.reception_date``
- ``ogg.document.delivery_date``
- ``ogg.document.version_number``
- ``ogg.document.document.creator.user.*`` - Doc-Properties des Benutzers, der das Dokument erstellt hat. Es werden die gleichen Doc-Property-Information wie beim aktuellen Benutzer verwendet, siehe `ProriétéDocs de l’utilisateur courant:`_

ProriétéDocs de séances, requêtes / objets de discussion:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.meeting.decision_number`` - numéro de décision de l'objet de discussion
- ``ogg.meeting.agenda_item_number`` - numéro de l’objet de discussion dans le cadre de la session courante
- ``ogg.meeting.agenda_item_number_raw`` - numéro brut de l’objet de discussion dans le cadre de la session courante (non formaté)
- ``ogg.meeting.proposal_title`` - titre de la requête
- ``ogg.meeting.proposal_description`` - description de la requête
- ``ogg.meeting.proposal_state`` - statut de la requête

.. note::
    Les ProriétéDocs suivantes exigent une configuration spécifique avant d’être utilisables:

ProriétéDocs pour tous les types de destinataires:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.contact.title`` - nom de l’organisation / nom composé de la personne
- ``ogg.recipient.contact.description``

ProriétéDocs de destinataires de type personne:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.person.salutation``
- ``ogg.recipient.person.firstname``
- ``ogg.recipient.person.lastname``
- ``ogg.recipient.person.academic_title``

ProriétéDocs de destinataires de type organisation:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.organization.name``

ProriétéDocs relation organisationnelle du destinataire:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.orgrole.function``
- ``ogg.recipient.orgrole.department``
- ``ogg.recipient.orgrole.description``

ProriétéDocs pour les coordonnées du destinataire (Adresse/Tel./E-Mail/URL):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``ogg.recipient.address.street``
- ``ogg.recipient.address.zip_code``
- ``ogg.recipient.address.city``
- ``ogg.recipient.address.country``
- ``ogg.recipient.phone.number``
- ``ogg.recipient.email.address``
- ``ogg.recipient.url.url``

Ces ProriétéDocs sont obsolètes et ne doivent plus être utilisées:

- ``Dossier.ReferenceNumber`` – référence du dossier qui contient le document
- ``Document.ReferenceNumber`` – référence du document
- ``Document.SequenceNumber`` – numéro courant du document
- ``User.FullName`` – prénom et nom de famille de l’utilisateur
- ``Dossier.Title`` – titre du dossier qui contient le document
- ``User.ID`` – identification de l’utilisateur inscrit

.. disqus::
