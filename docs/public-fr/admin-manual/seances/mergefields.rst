Seriendruckfelder
-----------------

Pour chaque commission, il est possible de définir les modèles Word suivants:

- Invitations à la séance / Ordre du jour
- Procès-verbal
- Extrait de Procès-verbal

Ces modèles sont utilisés par le module de gestion de séances et procès-verbaux et automatisent la génération des documents respectifs pour une séance. Pour réaliser cela, les modèles utilisent des chemps de fusion pour intégrer des données dans les documents générés à partir des modèles.

Les nouveaux champs pouvent être insérés via l'onglet ``Insérer`` » ``Quickpart`` » ``Champ...`` pour ensuite utiliser les champs de type ChampFusion dans la boîte de dialogue ainsi ouverte:

.. image:: ../img/media/word_mergefield.png

Les champs de fusion suivants peuvent être utilisés par défaut:

Métadonnées générales:
~~~~~~~~~~~~~~~~~~~~~~

- ``document.generated``

  date de génération du document (string)

Métadonnées de séance:
~~~~~~~~~~~~~~~~~~~~~~

- ``mandant.name``

  Nom du client ou département OneGov GEVER courant (string)

- ``protocol.type``

  type de protocole („procès-verbal“, „extrait de procès-verbal“)

- ``committee.name``

  nom de l’organe ou de la commission (string)

- ``meeting.date``

  date de la séance (date)

- ``meeting.location``

  lieu de la séance (string)

- ``meeting.start_time``

  date du début séance (heure)

- ``meeting.end_time``

  date de fin de séance (heure)

- ``meeting.number``

  numéro de séance (string). Débute toujours avec „1“ au commencement d’une nouvelle période de séances (usuellement une année civile). OneGov GEVER n’attribue un numéro de séance que lorsqu’un premier objet de discussion a été clôturé.

- ``participants.presidency``

  président de la séance (participant)

- ``participants.secretary``

  secrétaire de la séance (participant)

- ``participants.other``

  liste de tous les participants de la séance (Liste de participant). Une itération à travers cette liste est typiquement utilisée pour afficher les noms de tous les participants.

- ``participants.members``

  liste de tous les autres participants / invités (string)

- ``participants.absentees``

  Lliste de tous les participants excusés (Liste de participant). Une itération à travers cette liste est typiquement utilisée pour afficher les noms de tous les absents.

- ``agenda_items``

  liste des objets de discussion (liste de AgendaItem)

.. _Sitzungsteilnehmer:

Métadonnées de participant à une séance:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``member.firstname``

  prénom d’un participant (string). Dans ce contexte «member» est une variable courante utilisée pour l’itération à travers de tous les éléments de participants.members.

- ``member.lastname``

  nom de famille d’un participant (string). Dans ce contexte «member» est une variable courante utilisée pour l’itération à travers de tous les éléments de participants.members.

- ``member.fullname``

  nom complet d’un participant (string). Dans ce contexte «member» est une variable courante utilisée pour l’itération à travers de tous les éléments de participants.members.

- ``member.role``

  rôle défini d’un participant dans le courant d’une séance (string). Dans ce contexte «member» est une variable courante utilisée pour l’itération à travers de tous les éléments de participants.members.

- ``member.email``

  adresse E-Mail d’un participant (string).


Métadonnées d’objets de discussion (AgendaItem):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``repository_folder_title``

  titre de la position taxonomique de l’objet de délibération en question (string). Suivant la langue définie de la requête le titre allemand ou français y est retourné.

- ``title``

  titre de la requête (string).

- ``description``

  déscritpon de la requête (String).

- ``number``

  numéro de l’objet de délibération (débute à „1“ pour chaque séance)

- ``dossier_reference_number``

  référence du dossier (string). Ce numéro est attribué automatiquement par la gestion des séances et procès-verbaux, en commençant la numérotation avec „1“ au début d’une période de séances (typiquement une année civile)

- ``decision_number``

  Beschlussnummer (String). Diese Nummer wird von der Sitzungs- und
  Protokollverwaltung automatisch vergeben, wobei die Nummerierung jeweils
  bei Anfang einer neuen Sitzungsperiode (üblicherweise ein Kalendarjahr)
  wieder bei 1 beginnt.

- ``is_paragraph``

  indique s’il s’agit d’un paragraphe ou non (boolean)

- ``attachments``

  liste de pièces jointes à la requête (liste d’Attachments)


Métadonnées de pièces jointes (Attachment):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``title``

  titre du document (string)

- ``filename``

  nom du fichier (string)


Métadonnées de tables des matières:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``group_title``

  Titel/Name des Elementes nach dem das Inhaltsverzeichnis gruppiert wurde. Entweder der erste Buchstabe des Antrags/Traktandums oder der Name der Ordnungsposition (Text).

- ``contents``

  Liste aller der Inhaltsverzeichnis-Elemente aller Traktanden/Anträge (Liste von Inhaltsverzeichnis-Elementen, siehe unten)


Metadaten zu einem Inhaltsverzeichnis-Element:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``title``

  titre de la requête / de l’objet de discussion (string)

- ``dossier_reference_number``

  référence du dossier d’une requête (string)

- ``repository_folder_title``

  titre de la position taxonomique d’une requête (string)

- ``decision_number``

  numéro de la décision d’une requête / d’un objet de discussion

- ``has_proposal``

  indique si l’objet de discussion est lié à une requête ou non (boolean)

- ``meeting_date``

  date de la séance pendant laquelle la requête / l’objet de discussion est traité(e)

- ``meeting_start_page_number``

  numéro de la première page de la séance rapporté (integer)

.. disqus::
