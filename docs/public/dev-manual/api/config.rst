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
          "features": {
              "activity": true,
              "contacts": false,
              "doc_properties": true,
              "dossier_templates": true,
              "ech0147_export": true,
              "ech0147_import": true,
              "meetings": true,
              "officeatwork": true,
              "officeconnector_attach": false,
              "officeconnector_checkout": true,
              "preview": false,
              "preview_open_pdf_in_new_window": false,
              "repositoryfolder_documents_tab": true,
              "repositoryfolder_tasks_tab": true,
              "solr": true,
              "word_meetings": false,
              "workspace": false
          },
          "max_dossier_levels": 2,
          "max_repositoryfolder_levels": 3
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
