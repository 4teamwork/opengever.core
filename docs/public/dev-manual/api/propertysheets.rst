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

Das Erstellen, Bearbeiten oder Löschen von Property Sheets über die API benötigt die Rolle ``PropertySheetsManager``. Das Auflisten / Anzeigen (GET) ist Benutzern mit Leseberechtigung erlaubt.

Zur Verwaltung von Property Sheets steht der Service-Endpoint ``@propertysheets`` zur Verfügung. Folgende Aufrufe sind möglich:

Eine Liste aller bestehender Property Sheets:

.. sourcecode:: http

  GET /@propertysheets HTTP/1.1


Auslesen der Definition eines Property Sheets:

.. sourcecode:: http

  GET /@propertysheets/<property_sheet_name> HTTP/1.1


Hinzufügen eines neuen Property Sheets:

.. sourcecode:: http

  POST /@propertysheets/<property_sheet_name> HTTP/1.1


Mutieren eines bestehenden Property Sheets:

.. sourcecode:: http

  PATCH /@propertysheets/<property_sheet_name> HTTP/1.1


Löschen eines bestehenden Property Sheets:

.. sourcecode:: http

  DELETE /@propertysheets/<property_sheet_name> HTTP/1.1


Neue Property Sheets erstellen
------------------------------

Neue Property Sheets können mittels POST Request hinzugefügt werden.
Ein Sheet kann immer nur als gesamte Einheit gespeichert werden. Existiert
schon ein Sheet mit dem verwendeten Namen, so wird dieses überschrieben.

Zum Erstellen eines Property Sheets muss man die gewünschten Felder und
Assignments angeben.

Der JSON-Attributname des einzelnen Feldes wird als Feld-identifier verwendet.
Einzelne Felder werden in folgendem Format erwartet:

- ``field_type``: Der Feldtyp, folgende Typen sind unterstützt:

  - ``bool``
  - ``choice``
  - ``date``
  - ``multiple_choice``
  - ``int``
  - ``text``
  - ``textline``

- ``title``: Der Titel des Feldes
- ``description``: Die Beschreibung des Feldes
- ``required``: Ob das Feld erforderlich ist
- ``values``: Auswahlmöglichkeiten für das Feld, nur für ``choice`` Feldtyp
- ``default``: Ein statischer Default-Wert

Es existieren noch weitere Möglichkeiten, Defaults anzugeben. Details dazu sind
im Abschnitt :ref:`Default-Werte <propertysheet-default-values>` beschrieben.

Die für das Assignment verwendeten Assignment-Slots müssen aus dem Vokabular
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
      "assignments": [
          "IDocumentMetadata.document_type.question"
      ],
      "fields": [
          {
              "description": "yes or no",
              "field_type": "bool",
              "name": "yesorno",
              "required": true,
              "title": "Y/N"
          }
      ],
      "id": "question"
  }

.. _propertysheet-default-values:

Default-Werte
-------------

Feld-Definitionen für alle Typen unterstützen folgende Optionen, um Default-Werte
bestimmen zu können. Diese Optionen schliessen sich gegenseitig aus, es kann
immer nur eine dieser Optionen angegeben werden

- ``default``: Ein statischer Default-Wert
- ``default_factory``: Bestimmen des Defaults mittels einer default factory Funktion
- ``default_expression``: Bestimmen des Defaults mittels einer TALES expression
- ``default_from_member``: Bestimmen des Defaults mittels eines Properties auf dem Member / User

Optionen für dynamische Default-Werte (alle Optionen ausser ``default``)
können aus Sicherheitsgründen nur von Benutzern mit der Rolle ``Manager`` gesetzt werden - die Rolle ``PropertySheetsManager`` reicht nicht.


``default``
^^^^^^^^^^^

Diese Option erwartet einen statischen Wert, welcher als default für das Feld
verwendet wird. Der Typ des Werts muss dem Feld-Typ entsprechen.

**Beispiel**:

.. sourcecode:: json

    {
      "name": "language",
      "title": "Language",
      "field_type": "text",
      "default": "en"
    }

``default_factory``
^^^^^^^^^^^^^^^^^^^

Diese Option aktzeptiert einen String, der einen dottedname zu einer default
factory enthält (eine Python Funktion, die dynamisch einen Default-Wert
zurückgibt).

**Beispiel**:

.. sourcecode:: json

    {
      "name": "language",
      "title": "Language",
      "field_type": "text",
      "default_factory": "opengever.document.example.language_default_factory"
    }



``default_expression``
^^^^^^^^^^^^^^^^^^^^^^

Diese Option aktzeptiert einen String, der eine gültige
`TALES Expression <https://zope.readthedocs.io/en/latest/zopebook/AppendixC.html#tales-overview>`_
enthält, welche dynamisch ausgewertet wird um einen Default-Wert zu bestimmen.

Der ExpressionContext in dem die Expression ausgewertet wird, enthält die
üblichen Namen. Allerdings sind aufgrund einer Limitierung zur Zeit der
aktuelle Kontext und der enthaltende Folder nicht verfügbar. ``here`` und
``object`` sind daher ``None``, und der ``folder`` ist auf das Portal gesetzt.

**Beispiel**:

.. sourcecode:: json

    {
      "name": "userid",
      "title": "User ID",
      "field_type": "text",
      "default_expression": "member/getId"
    }

``default_from_member``
^^^^^^^^^^^^^^^^^^^^^^^

Diese Option aktzeptiert ein JSON Objekt mit mindestens einem key ``property``
das definiert, von welchem Property auf dem eingeloggten Member (~= User) der
Default-Wert bestimmt werden soll. Wenn LDAP-Properties via dem LDAPUserFolder
Schema entsprechend gemappt sind, können auch diese als Default-Werte verwendet
werden.

Optional unterstützt ``default_from_member`` auch die Angabe eines Mappings,
und eines Fallback-Wertes der Verwendet wird wenn das Property nicht gefunden
werden kann, oder einen Wert zurückgibt der Falsy ist.

Wenn ein Mapping verwendet wird, kann über den Parameter ``allow_unmapped``
gesteuert werden, ob Rückgabewerte erlaubt sind, die nicht im Mapping vorkommen:

- ``allow_unmapped = False (default)``: Werte, die nicht im Mapping vorkommen, sind nicht erlaubt. Für solche Werte wird stattdessen das ``fallback`` verwendet.

- ``allow_unmapped = True``: Werte, die nicht im Mapping vorkommen, werden 1:1 als default zurückgegeben.


**Beispiel**:

.. sourcecode:: json

    {
      "name": "userid",
      "title": "User ID",
      "field_type": "text",
      "default_from_member": {
        "property": "username",
        "fallback": "<No username found>",
        "mapping": {
          "p.mueller": "peter.mueller",
          "h.meier": "hans.meier"
        }
      }
    }


Existierende Property Sheets mutieren (PATCH)
---------------------------------------------

Existierende Property Sheets können über einen ``PATCH`` request mutiert werden. Die PATCH-Semantik besagt grundsätzlich, dass Feldwerte, welche im Request nicht mitgeschickt werden, so belassen werden wie sie sind. Für Propertysheets gilt dies für die äusserste Ebene, nicht aber für verschachtelte Ebenen.

Das heisst, wenn entweder der ``assignments`` Key oder der ``fields`` Key weggelassen werden, behalten diese den vorherigen Wert. Wird aber ein ``fields`` Key mitgeschickt, und enthält weniger Felder als zuvor, werden diese fehlenden Felder *gelöscht*.

Beim Aktualisieren von einzelnen Feldern muss vom Client daher immer die komplette Feld-Liste, wie sie neu aussehen soll, mitgeschickt werden.

Es ist dementsprechend auch nicht möglich, ein Feld umzubenennen. Das Feld kann aber entfernt , und unter einem anderen Namen hinzugefügt werden. Dies führt aber dazu, dass Daten, welche auf Dossiers oder Dokumenten unter dem alten Feldnamen bereits erfasst wurden, verloren gehen und nicht dem neuen Feld zugeordnet sind.

Beispiel für einen PATCH-Request:


**Beispiel-Request**:

.. sourcecode:: http

  PATCH http://localhost:8080/fd/@propertysheets/question HTTP/1.1
  Accept: application/json
  Content-Type: application/json

  {
    "assignments": ["IDocument.default"]
  }

(Ändert die Assignments auf `["IDocument.default"]`. Die Felder werden so belassen wie zuvor.)


**Beispiel-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
      "assignments": [
          "IDocument.default"
      ],
      "fields": [
          {
              "description": "yes or no",
              "field_type": "bool",
              "name": "yesorno",
              "required": true,
              "title": "Y/N"
          }
      ],
      "id": "question"
  }

(Die Response auf PATCH Requests enthält die komplette, neue Definition des Propertysheets.)

Das Ändern von :ref:`dynamischen Defaults <propertysheet-default-values>` ist nur für Benutzer mit der ``Manager``-Rolle erlaubt. Wenn jedoch ein dynamischer default für ein Feld bereits existiert, dann kann dieser in einem PATCH request auch von einem Benutzer mit der Rolle ``PropertySheetsManager`` mitgeschickt werden (um ihn zu erhalten), sofern der dynamische Default nicht geändert wird.


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


Schemas für Propertysheets
--------------------------

JSON Schemas für existierende Propertysheets können über den ``@schema`` Endpoint abgerufen werden. Dazu wird ein ``GET`` Request auf ``@schema/virtual.propertysheet.<sheet_id>`` ausgeführt, wobei ``sheet_id`` die ID / der Name des entsprechenden Sheets ist.

Beispiel (für ein Sheet mit der ID ``question``)

.. sourcecode:: http

  GET /@schema/virtual.propertysheet.question HTTP/1.1
  Accept: application/json

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json+schema

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


Schema für Propertysheet-Definitionen
-------------------------------------

Das JSON Schema für eine Propertysheet-Definition kann über den ``@propertysheet-metaschema`` Endpoint abgerufen werden:

.. sourcecode:: http

  GET /@propertysheet-metaschema HTTP/1.1
  Accept: application/json

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json+schema

  {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "title": "Propertysheet Meta Schema",
      "additionalProperties": false,
      "properties": {
          "id": {
              "type": "string",
              "title": "ID",
              "maxLength": 32,
              "description": "ID dieses Property Sheets",
              "additionalProperties": false,
              "pattern": "^[a-z_0-9]*$"
          },
          "fields": {
              "type": "array",
              "title": "Felder",
              "description": "Felder",
              "additionalProperties": false,
              "items": {
                  "required": [
                      "name",
                      "field_type"
                  ],
                  "type": "object",
                  "properties": {
                      "name": {
                          "pattern": "^[a-z_0-9]*$",
                          "maxLength": 32,
                          "type": "string",
                          "description": "Name (Alphanumerisch, nur Kleinbuchstaben)",
                          "title": "Name"
                      },
                      "field_type": {
                          "description": "Datentyp für dieses Feld",
                          "title": "Feld-Typ",
                          "enum": [
                              "int",
                              "multiple_choice",
                              "choice",
                              "bool",
                              "text",
                              "date",
                              "textline"
                          ],
                          "choices": [
                              [
                                  "int",
                                  "Integer"
                              ],
                              [
                                  "multiple_choice",
                                  "Multiple Choice"
                              ],
                              [
                                  "choice",
                                  "Choice"
                              ],
                              [
                                  "bool",
                                  "Yes/No"
                              ],
                              [
                                  "text",
                                  "Text"
                              ],
                              [
                                  "date",
                                  "Date"
                              ],
                              [
                                  "textline",
                                  "Text line (String)"
                              ]
                          ],
                          "enumNames": [
                              "Integer",
                              "Multiple Choice",
                              "Choice",
                              "Yes/No",
                              "Text",
                              "Date",
                              "Text line (String)"
                          ],
                          "type": "string"
                      },
                      "title": {
                          "title": "Titel",
                          "type": "string",
                          "description": "Titel",
                          "maxLength": 48
                      },
                      "description": {
                          "title": "Beschreibung",
                          "type": "string",
                          "description": "Beschreibung",
                          "maxLength": 128
                      },
                      "required": {
                          "type": "boolean",
                          "description": "Angabe, ob Benutzer dieses Feld zwingend ausfüllen müssen",
                          "title": "Pflichtfeld"
                      },
                      "default": {
                          "type": [
                              "integer",
                              "array",
                              "boolean",
                              "string"
                          ],
                          "description": "Default-Wert für dieses Feld",
                          "title": "Default"
                      },
                      "values": {
                          "uniqueItems": false,
                          "items": {
                              "title": "",
                              "type": "string",
                              "factory": "Text line (String)",
                              "description": ""
                          },
                          "type": "array",
                          "description": "Liste der erlaubten Werte für das Feld",
                          "title": "Wertebereich"
                      }
                  }
              },
              "uniqueItems": false
          },
          "assignments": {
              "type": "array",
              "title": "Slots",
              "description": "Für welche Arten von Inhalten dieses Property Sheet verfügbar sein soll",
              "additionalProperties": false,
              "items": {
                  "type": "string",
                  "enum": [
                      "IDocument.default",
                      "IDocumentMetadata.document_type.question",
                      "IDocumentMetadata.document_type.request",
                      "IDocumentMetadata.document_type.report",
                      "IDocumentMetadata.document_type.offer",
                      "IDocumentMetadata.document_type.protocol",
                      "IDocumentMetadata.document_type.regulations",
                      "IDocumentMetadata.document_type.contract",
                      "IDocumentMetadata.document_type.directive",
                      "IDossier.default",
                      "IDossier.dossier_type.businesscase"
                  ],
                  "enumNames": [
                      "Dokument",
                      "Dokument (Typ: Anfrage)",
                      "Dokument (Typ: Antrag)",
                      "Dokument (Typ: Bericht)",
                      "Dokument (Typ: Offerte)",
                      "Dokument (Typ: Protokoll)",
                      "Dokument (Typ: Reglement)",
                      "Dokument (Typ: Vertrag)",
                      "Dokument (Typ: Weisung)",
                      "Dossier",
                      "Dossier (Typ: Geschäftsfall)"
                  ],
                  "choices": [
                      [
                          "IDocument.default",
                          "Dokument"
                      ],
                      [
                          "IDocumentMetadata.document_type.question",
                          "Dokument (Typ: Anfrage)"
                      ],
                      [
                          "IDocumentMetadata.document_type.request",
                          "Dokument (Typ: Antrag)"
                      ],
                      [
                          "IDocumentMetadata.document_type.report",
                          "Dokument (Typ: Bericht)"
                      ],
                      [
                          "IDocumentMetadata.document_type.offer",
                          "Dokument (Typ: Offerte)"
                      ],
                      [
                          "IDocumentMetadata.document_type.protocol",
                          "Dokument (Typ: Protokoll)"
                      ],
                      [
                          "IDocumentMetadata.document_type.regulations",
                          "Dokument (Typ: Reglement)"
                      ],
                      [
                          "IDocumentMetadata.document_type.contract",
                          "Dokument (Typ: Vertrag)"
                      ],
                      [
                          "IDocumentMetadata.document_type.directive",
                          "Dokument (Typ: Weisung)"
                      ],
                      [
                          "IDossier.default",
                          "Dossier"
                      ],
                      [
                          "IDossier.dossier_type.businesscase",
                          "Dossier (Typ: Geschäftsfall)"
                      ]
                  ]
              },
              "uniqueItems": true
          }
      },
      "required": [
          "fields"
      ],
      "field_order": [
          "id",
          "fields",
          "assignments"
      ]
  }
