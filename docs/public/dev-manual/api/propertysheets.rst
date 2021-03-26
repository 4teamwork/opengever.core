.. _propertysheets:

Benutzerdefinierte Felder
=========================

Das Bearbeiten der Schemas für Benutzerdefinierte Felder und
Serialisieren/Deserialisieren auf Inhalten verwendet die folgenden Begriffe:

- ``Property Sheet``: Ein Property Sheet definiert ein Schema. Dieses Schema
                      wird zur Validierung der Custom Properties verwendet.
- ``Assignment Slot``: Ein Assignment Slot definiert einen Steckplatz dem
                       maximal ein Property Sheet zugewiesen werden kann.
- ``Assignment``: Ein Assignment ist die Zuweisung eines Property Sheets an
                  einen Assignment Slot. Ein Property Sheet kann mehrere
                  Assignments haben.
- ``Custom Properties``: Custom Properties sind die konkreten Daten auf den
                         Inhaltsobjekten. Custom Properties werden gegen ihr
                         zugehöriges Property Sheet validiert.

Mittels Property Sheets ist es möglich benutzerdefinierte Schemata mit einem
oder mehreren Feldern zu definieren damit zusätzliche Properties in GEVER
strukturiert erfasst werden können.

Im Moment ist das Definieren der zusätzlichen Property Sheets einem ``Manager``
vorbehalten. Hierzu steht der Service-Endpoint ``@propertysheets`` zur
Verfügung. Folgende Aufrufe sind möglich:

Eine Liste aller bestehender Property Sheets:

.. sourcecode:: http

  GET /@propertysheets HTTP/1.1


Schema eines Property Sheets:

.. sourcecode:: http

  GET /@propertysheets/<property_sheet_name> HTTP/1.1


Hinzufügen eines neuen Property Sheets oder Überschreiben eines bestehenden
Property Sheets:

.. sourcecode:: http

  POST /@propertysheets/<property_sheet_name> HTTP/1.1


Löschen eines bestehenden Property Sheets:

.. sourcecode:: http

  DELETE /@propertysheets/<property_sheet_name> HTTP/1.1


Neue Property Sheets erstellen
------------------------------

Neue Property Sheets können mittels POST Request hinzugefügt werden. Im Moment
sind keine Inkrementellen Updates der Sheets mittels ``PATCH`` unterstützt.
Ein Sheet kann immer nur als gesamte Einheit gespeichert werden. Existiert
schon ein Sheet mit dem verwendeten Namen, so wird dieses überschrieben.

Zum Erstellen eines Property Sheets muss man die gewünschten Felder und
Assignments angeben.

Der JSON-Attributname des einzelnen Feldes wird als Feld-identifier verwendet.
Einzelne Felder werden in folgendem Format erwartet:

- ``field_type``: Der Feldtyp, folgende Typen sind unterstützt:

  - ``bool``
  - ``choice``
  - ``int``
  - ``text``
  - ``textline``

- ``title``: Der Titel des Feldes
- ``description``: Die Beschreibung des Feldes
- ``required``: Ob das Feld erforderlich ist
- ``values``: Auswahlmöglichkeiten für das Feld, nur für ``choice`` Feldtyp

Die für das Assigmnet verwendeten Assignment-Slots müssen aus dem Vokabular
``opengever.propertysheets.PropertySheetAssignmentsVocabulary`` stammen. Ein
Spezialfall ist dabei der Default-Slot ``IDocument.default`` bzw.
``IDossier.default``, welcher unabhängig vom Dokument- oder Dossiertyp Feld
immer dargestellt wird.

Zudem müssen Assignments
eindeutig sein, mehrere Property Sheets dem gleichen Assignment-Slot zuzuweisen
ist im Moment nicht unterstützt.


**Beispiel-Request**:

.. sourcecode:: http

  POST http://localhost:8080/fd/@propertysheets/question HTTP/1.1
  Accept: application/json

  {
    "fields": [
      {
        "name": "yesorno",
        "field_type": "bool",
        "title": "Y/N",
        "description": "yes or no",
        "required": true
      }
    ],
    "assignments": ["IDocumentMetadata.document_type.question"]
  }


**Beispiel-Response**:

.. sourcecode:: http

  HTTP/1.1 201 Created
  Content-Type: application/json+schema
  Location: /@propertysheets/question

  {
      "assignments": ["IDocumentMetadata.document_type.question"],
      "fieldsets": [
          {
              "behavior": "plone",
              "fields": ["yesorno"],
              "id": "default",
              "title": "Default"
          }
      ],
      "properties": {
          "yesorno": {
              "description": "yes or no",
              "factory": "Yes/No",
              "title": "Y/N",
              "type": "boolean"
          }
      },
      "required": ["yesorno"],
      "title": "question",
      "type": "object"
  }


Serialisierung/Deserialisierung von Custom Properties
-----------------------------------------------------

Im Moment sind Custom Properties auf Dokumenten, Mails und Dossiers unterstützt.
Die Auswahl des zu validierenden Property Sheets basiert auf dem Wert des Feldes
`document_type` bzw. `dossier_type`. Ausnahme ist dabei der Default-Slot
``IDocument.default`` bzw. ``IDossier.default`` welcher unabhängig des Typen
Feldwertes immer dargestellt wird.
Ist für den Assignment-Slot
``IDocumentMetadata.document_type.<document_type_value>`` ein Property Sheet
registriert, so werden Feldwerte dieses Property Sheets validiert. Hat das
Property Sheet also obligatorische Felder, so müssen die Custom Properties
zwingend Daten für dieses Property Sheet beinhalten. Serialisierung und
Deserialisierung der Custom Properties basiert auf folgendem Format:


.. sourcecode:: json

  {
      "custom_properties": {
          "<assignment_slot_name>": {
              "<property_sheet_field_name>": "<field value>"
      }
  }


Es werden immer alle einmal gespeicherten Custom Properties serialisiert und
ausgegeben, unabhängig vom Wert des Feldes ``document_type``.

.. sourcecode:: http

  GET /ordnungssystem/dossier-23/document-123 HTTP/1.1
  Accept: application/json

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
      "@id": "/ordnungssystem/dossier-23/document-123",
      "custom_properties": {
          "IDocumentMetadata.document_type.question": {
              "yesorno": false
          },
          "IDocumentMetadata.document_type.protocol": {
              "location": "Dammweg 9",
              "responsible": "Hans Muster",
              "protocol_type": {
                  "title": "Kurzprotokoll",
                  "token": "Kurzprotokoll"
              }
          }
      },
      "...": "..."
  }


Beim Speichern der Custom Properties können Properties für alle erlaubten
Assigmnet-Slots angegeben werden. Es werden immer alle angegebenen Custom
Properties validiert. Das Speichern erfolg kumulativ, wenn man ein Subset
der möglichen Assignment-Slots verwendet, werden die Custom Propterties anderer
Slots nicht überschrieben.

  .. sourcecode:: http

    PATCH /ordnungssystem/dossier-23/document-123 HTTP/1.1
    Accept: application/json

    {
        "custom_properties": {
            "IDocumentMetadata.document_type.protocol": {
                "location": "Dammweg 9",
                "responsible": "Hans Muster",
                "protocol_type": {
                    "title": "Kurzprotokoll",
                    "token": "Kurzprotokoll"
                }
            }
        }
    }

  .. sourcecode:: http

    HTTP/1.1 204 No content
    Content-Type: application/json
