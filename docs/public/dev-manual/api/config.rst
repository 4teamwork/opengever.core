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
          "admin_unit": "fd",
          "application_type": "gever",
          "apps_url": "https://dev.onegovgever.ch/portal/api/apps",
          "bumblebee_app_id": "gever_dev",
          "bumblebee_notifications_url": "ws://bumblebee.local/notifications",
          "cas_url": "https://dev.onegovgever.ch/portal/cas",
          "current_user": {
              "@id": "http://localhost:8080/fd/@users/john.doe",
              "description": null,
              "email": "john.doe@example.org",
              "fullname": "Doe John",
              "home_page": null,
              "id": "john.doe",
              "location": null,
              "portrait": null,
              "roles": [
                "Member",
                "WorkspacesUser",
                "WorkspacesCreator"
              ],
              "roles_and_principals": [
                "principal:john.doe",
                "Member",
                "WorkspacesUser",
                "WorkspacesCreator",
                "Authenticated",
                "principal:AuthenticatedUsers",
                "principal:og_demo-ftw_users",
                "Anonymous"
              ],
              "username": "john.doe"
          },
          "document_preserved_as_paper_default": true,
          "features": {
              "activity": true,
              "archival_file_conversion": false,
              "archival_file_conversion_blacklist": [],
              "changed_for_end_date": true,
              "contacts": false,
              "disposition_disregard_retention_period": false,
              "disposition_transport_filesystem": false,
              "disposition_transport_ftps": false,
              "doc_properties": true,
              "dossier_templates": true,
              "ech0147_export": true,
              "ech0147_import": true,
              "favorites": true,
              "gever_ui_enabled": false,
              "hubspot": false,
              "journal_pdf": false,
              "meetings": true,
              "officeatwork": true,
              "officeconnector_attach": true,
              "officeconnector_checkout": true,
              "oneoffixx": false,
              "optional_task_permissions_revoking": false,
              "preview": true,
              "preview_auto_refresh": false,
              "preview_open_pdf_in_new_window": false,
              "private_tasks": true,
              "purge_trash": false,
              "repositoryfolder_documents_tab": true,
              "repositoryfolder_proposals_tab": true,
              "repositoryfolder_tasks_tab": true,
              "resolver_name": "strict",
              "sablon_date_format": "%d.%m.%Y",
              "solr": true,
              "tasks_pdf": false,
              "workspace": false,
              "workspace_client": false,
              "workspace_meetings": false,
              "workspace_todo": false,
          },
          "gever_colorization": "#37C35A",
          "inbox_folder_url": "https://dev.onegovgever.ch/fd/eingangskorb/eingangskorb_afi",
          "is_admin": false,
          "is_inbox_user": false,
          "is_propertysheets_manager": false,
          "is_emm_environment": false,
          "max_dossier_levels": 5,
          "max_repositoryfolder_levels": 3,
          "nightly_jobs": {
              "end_time": "5:00:00",
              "start_time": "1:00:00"
          },
          "oneoffixx_settings": {
              "cache_timeout": 2592000,
              "double_encode_bug": true,
              "fake_sid": "",
              "scope": "oo_V1WebApi"
          },
          "org_unit": "afi",
          "p7m_extension_replacement": "eml",
          "portal_url": "https://dev.onegovgever.ch/portal",
          "private_folder_url": "http://localhost:8080/fd/private/john.doe",
          "recently_touched_limit": 10,
          "root_url": "http://localhost:8080/fd",
          "sharing_configuration": {
              "black_list_prefix": "^$",
              "white_list_prefix": "^.+"
          },
          "user_settings": {
              "notify_inbox_actions": true,
              "notify_own_actions": false,
              "seen_tours": [
                  "introduction"
              ]
          },
          "usersnap_api_key": "",
          "version": "2020.4.0.dev0"
      }


Konfigurationsoptionen
----------------------

application_type
  Applikationstyp, entweder "gever" oder "teamraum"

apps_url

  URL für die Abfrage der verfügbaren Applikationen

cas_url

  CAS server URL

bumblebee_notifications_url

    Websocket URL, um Änderungen über Vorschaubilder zu erhalten

features
    Optional aktivierbare Features:

    activity
        Benachrichtigungen

    archival_file_conversion
        Dateien beim Dossierabschluss zusätzlich nach PDF-A konvertieren für Archivierung

    changed_for_end_date
        "changed" als Enddatum für Dossiers verwenden

    contacts
        Erweitertes Kontaktmodul

    disposition_disregard_retention_period
        Aufbewahrungsdauer beim Erstellen von Angeboten ignorieren

    disposition_transport_filesystem
        Das SIP Packet bei der Aussonderung zusätzlich über das Dateisystem ausliefern

    doc_properties
        Hinzufügen von DocProperties bei aus Vorlagen erstellten Word-Dokumenten

    dossier_templates
        Dossier Vorlagen

    ech0147_export
        eCH-0039/eCH-0147 Export von Dossiers und Dokumenten

    ech0147_import
        eCH-0039/eCH-0147 Import von Dossiers und Dokumenten

    favorites
        Favoriten

    gever_ui_enabled
        Neue Benutzeroberfläche aktiviert

    hubspot
        Einbindung von HubSpot Chat in der neuen Benutzeroberfläche

    journal_pdf
        Journal PDF erstellen beim Abschliessen eines Dossiers

    meetings
        Sitzungs- und Protokollverwaltung (SPV)

    officeatwork
        Unterstützung für Officeatwork Vorlagen

    officeconnector_attach
        Versand von E-Mails über Outlook

    officeconnector_checkout
        Checkout und Checkin von Dokumenten über Office Connector

    oneoffixx
        Unterstützung für Oneoffixx Vorlagen

    optional_task_permissions_revoking
        Berechtigungsentzug Optional bei Aufgaben

    preview
        Dokumentvorschau

    preview_open_pdf_in_new_window
        PDF in der Dokumentvorschau werden in einem neuen Fenster geöffnet

    private_tasks
        Private Aufgaben

    purge_trash
        Papierkorb leeren beim Dossierabschluss

    repositoryfolder_documents_tab
        Dokumente-Tab bei Ordnungspositionen darstellen

    repositoryfolder_proposals_tab
        Anträge-Tab bei Ordnungspositionen darstellen

    repositoryfolder_tasks_tab
        Aufgaben-Tab bei Ordnungspositionen darstellen

    resolver_name
        Resolver welcher beim Dossierabschluss verwendet wird

    sablon_date_format
        Datum Formatierung Spezifikation für Sablon Vorlagen

    solr
        Suche über Apache Solr

    tasks_pdf
        Aufgaben PDF erstellen beim Abschliessen eines Dossier

    workspace
        Arbeitsräume

    workspace_client
        Integration von GEVER mit einem Teamraum

    workspace_meetings
        Meetings in einem Teamraum

    workspace_todo
        ToDo's und ToDo-Listen in einem Teamraum


gever_colorization
    Rahmen Farbe

max_repositoryfolder_levels
    Maximale Verschachtelungstiefe von Ordnungspositionen

max_dossier_levels
    Maximale Verschachtelungstiefe von Dossiers

nightly_jobs

    start_time
        Startzeit für NightlyJobs

    end_time
        Endzeit für NightlyJobs

p7m_extension_replacement
    Dateiendung die beim Download von Mails anstatt p7m verwendet wird.

portal_url
    URL des Portals

sharing_configuration

    white_list_prefix
        regex Muster für Gruppen die in der Freigabe angezeigt werden sollen

    black_list_prefix
        regex Muster für Gruppen die in der Freigabe nicht angezeigt werden sollen

recently_touched_limit

    Anzahl Objekte im "Zuletzt bearbeitet" Menu

user_settings

    notify_inbox_actions
        Einstellung um Eingangskorb-Benachrichtigungen zu aktivieren bzw. deaktivieren.

    notify_own_actions
        Einstellung um Benachrichtigung für eigene Aktionen zu aktivieren bzw. deaktivieren.

    seen_tours
        Gesehene Hilfe-Touren

usersnap_api_key

    API Schlüssel für Usersnap Integration im neuen Frontend

has_dossier_propertysheet_registered
    Gibt an, ob dieses Deployment eigene Propertysheets für Dossiers definiert oder nicht.
