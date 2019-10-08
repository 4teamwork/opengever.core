.. _config:

Konfiguration
=============

Über den ``/@config`` Endpoint können diverse Konfigurationsoptionen des
GEVER-Mandanten abgefragt werden.

**Beispiel-Request**:

   .. sourcecode:: http

       GET /@config HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

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


Konfigurationsoptionen
----------------------

max_repositoryfolder_levels
    Maximale Verschachtelungstiefe von Ordnungspositionen

max_dossier_levels
    Maximale Verschachtelungstiefe von Dossiers

features
    Optional aktivierbare Features:

    activity
        Benachrichtigungen

    contacts
        Erweitertes Kontaktmodul

    doc_properties
        Hinzufügen von DocProperties bei aus Vorlagen erstellen Word-Dokumenten

    dossier_templates
        Dossiervorlagen

    ech0147_export
        eCH-0039/eCH-0147 Export von Dossiers und Dokumenten

    ech0147_import
        eCH-0039/eCH-0147 Import von Dossiers und Dokumenten

    meetings
        Sitzungs- und Protokollverwaltung (SPV)

    officeatwork
        Unterstützung für Officeatwork Vorlagen

    officeconnector_attach
        Versand von E-Mails über Outlook

    officeconnector_checkout
        Checkout und Checkin von Dokumenten über Office Connector

    preview
        Dokumentvorschau

    preview_open_pdf_in_new_window
        PDF in der Dokumentvorschau werden in einem neuen Fenster geöffnet

    repositoryfolder_documents_tab
        Dokumente-Tab bei Ordnungspositionen

    repositoryfolder_tasks_tab
        Aufgaben-Tab bei Ordnungspositionen

    solr
        Suche über Apache Solr

    word_meetings
        Sitzungs- und Protokollverwaltung auf Basis von Word-Dokumenten

    workspace
        Arbeitsräume

sharing_configuration

    white_list_prefix
        regex Muster für Gruppen die in der Freigabe angezeigt werden sollen

    black_list_prefix
        regex Muster für Gruppen die in der Freigabe nicht angezeigt werden sollen

user_settings

    notify_inbox_actions
        Einstellung um Eingangskorb-Benachrichtigungen zu aktivieren bzw. deaktivieren.

    notify_own_actions
        Einstellung um Benachrichtigung für eigene Aktionen zu aktivieren bzw. deaktivieren.

    seen_tours
        Gesehene Hilfe-Touren
