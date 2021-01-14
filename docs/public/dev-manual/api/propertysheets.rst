.. _propertysheets:

Property Sheets (Benutzerdefinierte Felder)
===========================================

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
``opengever.propertysheets.PropertySheetAssignmentsVocabulary`` stammen. Zudem
müssen Assignments eindeutig sein, mehrere Property Sheets dem gleichen
Assignment-Slot zuzuweisen ist im Moment nicht unterstützt.


**Beispiel-Request**:

.. sourcecode:: http

  POST http://localhost:8080/fd/@propertysheets/question HTTP/1.1
  Accept: application/json

  {
    "fields": {
      "yesorno": {
        "field_type": "bool",
        "title": "Y/N",
        "description": "yes or no",
        "required": true
      }
    },
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
