.. _webactions:

Webactions
==========

Der ``/@webactions`` Endpoint auf dem Root des Mandanten ermöglicht das
Verwalten von sogenannten WebActions in GEVER.

.. contents::

Solche Webaktionen können z.B. für oder von Drittanwendungen (mit den nötigen
:ref:`Berechtigungen <webactions-mgmt-permissions>`) registriert werden, um
eine möglichst nahtlose Integration in GEVER zu erreichen. Mit Webaktionen
können Knöpfe, Links und Icons direkt an gewissen Stellen in GEVER platziert
werden, mit welchen der Benutzer dann Aktionen in der Drittanwendung
auslösen kann.


.. _webactions-mgmt-permissions:

Berechtigungen für das Verwalten von Webaktionen
------------------------------------------------

Für das Verwalten von Webaktionen über die REST API wird die permission
``opengever.webactions: Manage own WebActions`` benötigt. Diese ist in GEVER
standardmässig der Rolle ``WebActionManager`` zugewiesen.

Benutzer mit dieser Berechtigungen dürfen neue Webaktionen erstellen, und
solche die sie selbst erstellt haben verwalten (auflisten, aktualisieren,
löschen).


Erstellen (POST)
----------------

.. http:post:: /@webactions

   Erstellt eine neue Webaktion mit den im Body (JSON) angegebenen Daten.

   **Request**:

   .. sourcecode:: http

      POST /@webactions HTTP/1.1
      Accept: application/json
      Content-Type: application/json
      
      {
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global"
      }

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 201 Created
      Content-Type: application/json
      Location: http://demo.onegovgever.ch/@webactions/0

      {
        "@id": "http://demo.onegovgever.ch/@webactions/0",
        "action_id": 0,
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global",
        "created": "2019-12-31T17:45:00",
        "modified": "2019-12-31T17:45:00",
        "owner": "webaction.manager"
      }

.. table::
    :widths: 25 75

    +------------------+------------------------------------------------------------------+
    | Status Code      | Beschreibung                                                     |
    +==================+==================================================================+
    | 201 Created      | WebAction erfolgreich erstellt. Repräsentation im Response-Body, |
    |                  | URL der erstellten Action im ``Location`` Header.                |
    +------------------+------------------------------------------------------------------+
    | 400 Bad Request  | Fehler bei der Schema-Validierung, oder anderer Client-seitiger  |
    |                  | Fehler. Details im Response-Body.                                |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Authentisierung oder Autorisierung fehlgeschlagen.               |
    +------------------+------------------------------------------------------------------+

Dieses Beispiel beschreibt die minimalen Angaben um eine Webaktion zu erstellen.
Für Details über alle unterstützten Felder, siehe `Eigenschaften von Webaktionen`_.

Die Response enthält die Repräsentation der Webaktion im Body, inklusive der
vom Server bei der Erstellung vergebenen Metadaten (siehe `Vom Server vergebene Metadaten`_).

Der ``Location`` Header enthält die kanonische URL der soeben erstellen
Webaktion, welche für weitere Requests verwendet werden kann.


Auslesen (GET)
--------------

.. http:get:: /@webactions/(action_id)

   Liest die Webaktion mit der entsprechenden ``action_id`` aus.

   **Request**:

   .. sourcecode:: http

      GET /@webactions/0 HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/@webactions/0",
        "action_id": 0,
        "title": "Open in ExternalApp",
        "target_url": "http://example.org/endpoint",
        "display": "actions-menu",
        "mode": "self",
        "order": 0,
        "scope": "global",
        "created": "2019-12-31T17:45:00",
        "modified": "2019-12-31T17:45:00",
        "owner": "webaction.manager"
      }

.. table::
    :widths: 25 75

    +------------------+------------------------------------------------------------------+
    | Status Code      | Beschreibung                                                     |
    +==================+==================================================================+
    | 200 OK           | Request erfolgreich beantwortet                                  |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Authentisierung oder Autorisierung fehlgeschlagen.               |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | WebAction mit dieser ``action_id`` konnte nicht gefunden werden. |
    +------------------+------------------------------------------------------------------+


Auflisten (GET)
---------------


.. http:get:: /@webactions

   Listet die von diesem Benutzer erstellten Webaktionen auf.

   **Request**:

   .. sourcecode:: http

      GET /@webactions HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/@webactions",
        "items": [
          {
            "@id": "http://demo.onegovgever.ch/@webactions/0",
            "action_id": 0,
            "title": "Open in ExternalApp 0",
            "target_url": "http://example.org/endpoint0",
            "display": "actions-menu",
            "mode": "self",
            "order": 0,
            "scope": "global",
            "created": "2019-12-31T17:45:00",
            "modified": "2019-12-31T17:45:00",
            "owner": "some.user",
          },
          {
            "@id": "http://demo.onegovgever.ch/@webactions/1",
            "action_id": 1,
            "title": "Open in ExternalApp 1",
            "target_url": "http://example.org/endpoint1",
            "display": "title-buttons",
            "mode": "self",
            "order": 0,
            "scope": "global",
            "created": "2019-12-31T17:46:00",
            "modified": "2019-12-31T17:46:00",
            "owner": "webaction.manager",
          }
        ]
      }

.. table::
    :widths: 25 75

    +------------------+------------------------------------------------------------------+
    | Status Code      | Beschreibung                                                     |
    +==================+==================================================================+
    | 200 OK           | Request erfolgreich beantwortet                                  |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Authentisierung oder Autorisierung fehlgeschlagen.               |
    +------------------+------------------------------------------------------------------+



Aktualisieren (PATCH)
---------------------


.. http:patch:: /@webactions/(action_id)

   Aktualisiert die durch ``action_id`` identifizierte Webaktion mit den
   im Body (JSON) mitgegebenen Daten.

   **Request**:

   .. sourcecode:: http

      PATCH /@webactions/0 HTTP/1.1
      Accept: application/json
      Content-Type: application/json

      {
        "title": "New title"
      }


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json

.. table::
    :widths: 25 75

    +------------------+------------------------------------------------------------------+
    | Status Code      | Beschreibung                                                     |
    +==================+==================================================================+
    | 204 No Content   | WebAction erfolgreich aktualisiert.                              |
    +------------------+------------------------------------------------------------------+
    | 400 Bad Request  | Fehler bei der Schema-Validierung, oder anderer Client-seitiger  |
    |                  | Fehler. Details im Response-Body.                                |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Authentisierung oder Autorisierung fehlgeschlagen.               |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | WebAction mit dieser ``action_id`` konnte nicht gefunden werden. |
    +------------------+------------------------------------------------------------------+



Löschen (DELETE)
----------------


.. http:delete:: /@webactions/(action_id)

   Löscht die durch die ``action_id`` identifizierte Webaktion.

   **Request**:

   .. sourcecode:: http

      DELETE /@webactions/0 HTTP/1.1
      Accept: application/json


   **Response**:

   .. sourcecode:: http

      HTTP/1.1 204 No Content
      Content-Type: application/json

.. table::
    :widths: 25 75

    +------------------+------------------------------------------------------------------+
    | Status Code      | Beschreibung                                                     |
    +==================+==================================================================+
    | 204 No Content   | WebAction erfolgreich gelöscht.                                  |
    +------------------+------------------------------------------------------------------+
    | 401 Unauthorized | Authentisierung oder Autorisierung fehlgeschlagen.               |
    +------------------+------------------------------------------------------------------+
    | 404 Not Found    | WebAction mit dieser ``action_id`` konnte nicht gefunden werden. |
    +------------------+------------------------------------------------------------------+


.. _webactions-fields:

Eigenschaften von Webaktionen
-----------------------------

Folgend ist eine Auflistung aller von Webaktionen unterstützten Felder und deren Typ und Bedeutung.

+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| Feld            | Typ                           | Beschreibung                                                                |
+=================+===============================+=============================================================================+
| ``title``       | String, obligatorisch         | Titel der Webaktion                                                         |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``unique_name`` | String, optional              | Eindeutiger, vom Ersteller der Webaktion kontrollierter Name                |
|                 |                               | (siehe :ref:`Eindeutiger Name <webactions-unique-name>` )                   |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``target_url``  | String, obligatorisch         | Ziel-URL auf den Endpoint der Drittanwendung                                |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``enabled``     | Boolean, optional             | Kann verwendet werden, um registrierte WebActions temporär zu deaktivieren. |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``icon_name``   | String, bedingt obligatorisch | Font-Awesome CSS-Klasse (z.B. ``fa-folder``)                                |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``icon_data``   | String, bedingt obligatorisch | Data URI mit Icon, Base64 codiert                                           |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``display``     | Choice, obligatorisch         | :ref:`Darstellungsort <webactions-display>` der Webaktion.                  |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``mode``        | Choice, obligatorisch         | Zielfenster: bestimmt wie der Link geöffnet wird.                           |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``order``       | Integer, 0-100, obligatorisch | Sortierhilfe um die Reihenfolge der registrieren Webaktionen bestimmen zu   |
|                 |                               | können. 0 bedeutet zuvorderst, 100 bedeutet zuhinterst.                     |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``scope``       | Choice, obligatorisch         | Bestimmt, bei welchen Objekten die Webaktion angeboten wird. Siehe          |
|                 |                               | :ref:`scope <webactions-scope>`.                                            |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``types``       | Liste von Strings, optional   | Eine Liste von Inhaltstypen von Objekten, für welche die Webaktion          |
|                 |                               | grundsätzlich angeboten wird. Beispiel ``opengever.document.document``,     |
|                 |                               | gemäss :ref:`Auflistung der Inhaltstypen <content-types>` in der            |
|                 |                               | Dokumentation. Wenn keine Typen angegeben werden, treffen alle Typen zu.    |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``groups``      | Liste von Strings, optional   | Liste von Benutzergruppen (IDs, gemäss LDAP). Wenn konfiguriert muss der    |
|                 |                               | Benutzer mindestens in einer dieser Gruppen sein damit die Webaktion        |
|                 |                               | angeboten wird.                                                             |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``permissions`` | Liste von Strings, optional   | Liste von Berechtigungen. Wenn konfiguriert muss der Benutzer mindestens    |
|                 |                               | eine Berechtigung haben damit die Webaktion angeboten wird. Siehe           |
|                 |                               | :ref:`Berechtigungsabhängige Aktionen <webactions-permissions>`.            |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+
| ``comment``     | String, optional              | Freitext für Bemerkungen.                                                   |
+-----------------+-------------------------------+-----------------------------------------------------------------------------+


.. _webactions-mode:

Zielfenster
-----------

Über das Feld ``mode`` kann gesteuert werden, wie der Link geöffnet wird.

Erlaubte Werte:

+---------------+------------------------------------------------------------------+
| Wert          | Beschreibung                                                     |
+===============+==================================================================+
| ``self``      | Das Ziel wird direkt im Tab von GEVER geöffnet. Sinnvoll für ein |
|               | Redirect-Szenario bei dem der Benutzer am Schluss wieder         |
|               | zurückgeleitet wird.                                             |
+---------------+------------------------------------------------------------------+
| ``blank``     | Das Ziel wird in einem neuen Tab geöffnet.                       |
+---------------+------------------------------------------------------------------+
| ``modal``     | Noch nicht implementiert. Das Ziel wird in einem Modal geöffnet. |
+---------------+------------------------------------------------------------------+

.. _webactions-scope:

Scope
-----

Über das Feld ``scope`` kann gesteuert werden, bei welchen Objekten die
Webaktion angeboten wird.

+---------------+---------------------------------------------------------------------+
| Wert          | Beschreibung                                                        |
+===============+=====================================================================+
| ``global``    | Die Webaktion wird grundsätzlich bei allen Objekten angeboten.      |
+---------------+---------------------------------------------------------------------+
| ``context``   | Noch nicht implementiert.                                           |
+---------------+---------------------------------------------------------------------+
| ``recursive`` | Noch nicht implementiert.                                           |
+---------------+---------------------------------------------------------------------+


.. _webactions-server-metadata:

Vom Server vergebene Metadaten
------------------------------

+---------------+-------------+-------------------------------------------------------------------+
| Feld          | Typ         | Beschreibung                                                      |
+===============+=============+===================================================================+
| ``action_id`` | Integer     | Pro Mandant eindeutige Identifikation der registrierten Webaktion |
+---------------+-------------+-------------------------------------------------------------------+
| ``created``   | Zeitstempel | Zeitpunkt der Erstellung der Webaktion                            |
+---------------+-------------+-------------------------------------------------------------------+
| ``modified``  | Zeitstempel | Zeitpunkt der letzten Modifikation der Webaktion                  |
+---------------+-------------+-------------------------------------------------------------------+
| ``owner``     | String      | Benutzer-ID des Erstellers der Webaktion                          |
+---------------+-------------+-------------------------------------------------------------------+

.. _webactions-display:

Darstellungsorte
----------------

Die Webaktionen können an verschiedenen Orten dargestellt werden.

Abhängig vom Darstellungsort ist die Angabe eines Icons entweder erlaubt,
notwendig oder nicht erlaubt. Dies wird von der API validiert, und eine
entsprechende Fehlermeldung (Im JSON-Body der Response, Status-Code 400) weist
darauf hin, wenn diese Einschränkung nicht erfüllt ist.

Ein Icon kann entweder via Name (``icon_name``) oder einer Data URI
(Base64 codiert, ``icon_data``) angegeben werden. Falls ein Icon angegeben
wird, darf aber nur eines dieser beiden Felder gesetzt sein, nicht beide.

Folgende Darstellungsorte sind als Werte für das Feld ``display`` erlaubt:

+--------------------+---------------+------------------------------------------------------------------+
| Darstellungsort    | Icon          | Beschreibung                                                     |
+====================+===============+==================================================================+
| ``action-buttons`` | optional      | Die Webaktion wird in der Aktionenliste von Aufgaben, Dokumenten |
|                    |               | und anderen Inhalten mit einer Aktionsliste dargestellt.         |
|                    |               | Dies funktioniert für Inhaltstypen die eine solche Aktionsliste  |
|                    |               | darstellen (im Moment Aufgaben, Weiterleitungen, Anträge,        |
|                    |               | Dokumente).                                                      |
+--------------------+---------------+------------------------------------------------------------------+
| ``actions-menu``   | keines        | Die Webaktion wird im Menu «Aktionen» angezeigt.                 |
+--------------------+---------------+------------------------------------------------------------------+
| ``add-menu``       | obligatorisch | Die Webaktion wird im Menu «Hinzufügen» angezeigt.               |
+--------------------+---------------+------------------------------------------------------------------+
| ``title-buttons``  | obligatorisch | Die Webaktion wird als Icon neben der Überschrift dargestellt.   |
|                    |               | Der Titel der Webaktion wird als Tooltip verwendet.              |
+--------------------+---------------+------------------------------------------------------------------+
| ``user-menu``      | keines        | Die Webaktion wird im Benutzermenu dargestellt.                  |
+--------------------+---------------+------------------------------------------------------------------+

.. _webactions-permissions:

Berechtigungsabhängige Aktionen
-------------------------------

Aktionen können eingeschränkt werden, so dass sie nur dann angezeigt werden,
wenn der Benutzer mindestens eine der angegebenen Berechtigungen auf dem
entsprechenden Kontext besitzt.

Folgende Werte können für das Feld ``permissions`` angegeben werden:

+---------------------+---------------------------------------------------------------------+
| Berechtigung        | Beschreibung                                                        |
+=====================+=====================================================================+
| ``edit``            | Der Benutzer darf den Inhalt bearbeiten.                            |
+---------------------+---------------------------------------------------------------------+
| ``add:TYP``         | Der Benutzer darf einen neuen Inhalt des angegeben Typs hinzufügen. |
|                     | z.B. ``add:opengever.dossier.businesscasedossier`` für das          |
|                     | Hinzufügen eines Geschäftsdossiers. Die aktuelle                    |
|                     | :ref:`Liste von Typen <content-types>` ist der                      |
|                     | REST-API-Dokumentation zu entnehmen                                 |
+---------------------+---------------------------------------------------------------------+
| ``trash``           | Der Benutzer darf Inhalt in den Papierkorb verschieben.             |
+---------------------+---------------------------------------------------------------------+
| ``untrash``         | Der Benutzer darf Inhalt aus dem Papierkorb wiederherstellen.       |
+---------------------+---------------------------------------------------------------------+
| ``manage-security`` | Der Benutzer darf anderen Benutzern Rollen verteilen.               |
+---------------------+---------------------------------------------------------------------+

.. _webactions-unique-name:

Eindeutiger Name
----------------

Das optionale Feld ``unique_name`` kann verwendet werden, um sicherzustellen,
dass eine Webaktion nicht aus versehen mehrmals erstellt wird.

Dieses Feld kann vom Client, der eine Webaktion erstellt, auf einen beliebigen
String gesetzt werden der die Webaktion aus Sicht des Clients eindeutig
bezeichnet. Wenn vorhanden, validiert der Server dann dass nur eine einzige
Aktion mit diesem Namen existiert, und verweigert sonst das Erstellen oder
Aktualisieren einer Aktion.

Im Fall dass ein ``unique_name`` angegeben wird und bereits existiert,
antwortet der Server mit ``400 Bad Request``:


**Response**:

.. sourcecode:: http

   HTTP/1.1 400 Bad Request
   Content-Type: application/json

   {
     "type": "BadRequest",
     "message": "[('unique_name', ActionAlreadyExists(\"An action with the unique_name u'existing-unique-name' already exists\",))]"
   }