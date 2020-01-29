.. _config:

Configuration
=============

On peut interroger diverses options de configuration du client GEVER avec l'endpoint ``/@config``.

**Exemple de Request**:

   .. sourcecode:: http

       GET /@config HTTP/1.1
       Accept: application/json

**Exemple de Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
          "@id": "http://localhost:8080/fd/@config",
          "cas_url": "https://cas.server.net/",
          "features": {
              "activity": true,
              "archival_file_conversion": false,
              "changed_for_end_date": true,
              "contacts": false,
              "doc_properties": true,
              "dossier_templates": true,
              "ech0147_export": true,
              "ech0147_import": true,
              "favorites": true,
              "journal_pdf": false,
              "tasks_pdf": false,
              "meetings": true,
              "officeatwork": true,
              "officeconnector_attach": true,
              "officeconnector_checkout": true,
              "oneoffixx": false,
              "preview": false,
              "preview_auto_refresh": false,
              "preview_open_pdf_in_new_window": false,
              "purge_trash": false,
              "repositoryfolder_documents_tab": true,
              "repositoryfolder_tasks_tab": true,
              "resolver_name": "strict",
              "sablon_date_format": "%d.%m.%Y",
              "solr": true,
              "workspace": false
          },
          "max_dossier_levels": 5,
          "max_repositoryfolder_levels": 3,
          "recently_touched_limit": 10,
          "root_url": "http://localhost:8080/fd",
          "sharing_configuration": {
              "black_list_prefix": "^$",
              "white_list_prefix": "^.+"
          },
          "user_settings": {
              "notify_inbox_actions": true,
              "notify_own_actions": false,
              "seen_tours": [],
          },
          "version": "2018.4.0.dev0",
      }


Options de configuration
------------------------

max_repositoryfolder_levels
    Profonduer maximale d'imbrication des numéros de classements

max_dossier_levels
    Profonduer maximale d'imbrication des dossiers

features
    Features optionelles activables:

    activity
        Notifications

    contacts
        Module de contacts étendu

    doc_properties
        Ajout de DocProperties pour les documents word créés à partir de modèles

    dossier_templates
        Modèles de dossiers

    ech0147_export
        eCH-0039/eCH-0147 Export de dossiers et de documents

    ech0147_import
        eCH-0039/eCH-0147 Import de dossiers et de documents

    meetings
        Gestion des séances et procès-verbaux (SPV)

    officeatwork
        Support pour modèles Officeatwork

    officeconnector_attach
        Envoi d'E-Mails avec Outlook

    officeconnector_checkout
        Checkout et Checkin de documents avec Office Connector

    preview
        Aperçu des documents

    preview_open_pdf_in_new_window
        Le PDF dans l'aperçu d'un document et ouvert dans une nouvelle fenêtre.

    repositoryfolder_documents_tab
        Tab des documents sur un numéro de classement

    repositoryfolder_tasks_tab
        Tab des tâches sur un numéro de classement

    solr
        Recherche avec Apache Solr

    workspace
        Teamraum

sharing_configuration

    white_list_prefix
        Motif regex pour détérminer quels groupes sont visible pour le partage.

    black_list_prefix
        Motif regex pour détérminer quels groupes ne sont pas visible pour le partage.

user_settings

    notify_inbox_actions
        Activer ou désactiver les notifications de la boîte de récéption.

    notify_own_actions
        Activer ou désactiver les notifications pour se propres actions.

    seen_tours
        Tours d'aide déjà visionnés
