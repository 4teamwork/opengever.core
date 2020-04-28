Erlaubte Rollen, Benutzer und Gruppen
=====================================

Der ``@allowed-roles-and-principals`` Endpoint (aufrufbar auf jedem Kontext)
gibt die Information zurück, welche Rollen, Gruppen oder Benutzer
das Objekt ansehen **dürfen** (die Lese-Berechtigung haben).

.. note::
    Der Begriff "principal" steht für "Benutzer oder Gruppe"

Umgekehrt ist in der Response des ``/@users/<user_id>`` Endpoints die
Information enthalten, welche "roles and principals" der User
**tatsächlich** hat (welche globalen Rollen er hat, in welchen Gruppen er ist,
und welches seine Benutzer-ID ist).

Mit diesen beiden Information über ein **Objekt** und den **Benutzer**
kann ein externes System selbstständig die Frage beantworten, ob ein Benutzer
auf ein bestimmtes Objekt in GEVER Lese-Berechtigung haben wird
*(unter der Voraussetzung, dass das externe System diese Informationen zu
geeigneten Zeitpunkten aktualisiert)*.

Wenn ein oder mehrere Strings aus der Liste der tatsächlichen
``roles_and_principals`` des Users in der Liste der
``allowed_roles_and_principals`` vorkommt, hat der Benutzer die
Lese-Berechtigung.


Auslesen der "allowed roles and principals" eines Objekts (GET)
---------------------------------------------------------------

Benötigte Berechtigung: ``opengever.api.ViewAllowedRolesAndPrincipals``


.. http:get:: /(path)/@allowed-roles-and-principals

   Gibt die "allowed roles and principals" auf dem entsprechenden Kontext zurück.

   **Request**:

   .. sourcecode:: http

      GET /dossier-15/@allowed-roles-and-principals HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/dossier-15/@allowed-roles-and-principals",
        "allowed_roles_and_principals": [
          "Administrator",
          "principal:og_demo_examplegroup",
          "principal:john.doe",
          "Manager",
          "Editor",
          "Reader",
          "Contributor",
          "_View_Permission"
        ]
      }

Der  ``@allowed-roles-and-principals`` Endpoint gibt (im
Property ``allowed_roles_and_principals``) eine Liste von Strings zurück, die
angibt welche Rollen, Gruppen oder Benutzer das Objekt ansehen dürfen
(Lese-Berechtigung haben).

Die Bedeutung dieser Liste ist wie folgt:

  - Mit ``principal:`` präfixte Strings sind **User-IDs** oder **Gruppen-IDs**
  - Nicht präfixte Strings sind **Rollen-IDs**

  - Wenn mindestens eine der

    - Globalen Rollen des Benutzers
    - Gruppen des Benutzers
    - oder die User-ID des Benutzers

    in dieser Liste vorkommt, hat der Benutzer die Berechtigung, das Objekt
    zu lesen - sonst nicht.

In diesem Beispiel ist ``og_demo_examplegroup`` eine Gruppe, ``john.doe`` ist
ein User, und die restlichen Einträge sind Rollen.


Auslesen der "roles and principals" eines Users (GET)
-----------------------------------------------------

.. http:get:: /@users/(user_id)

   Gibt die Informationen zum entsprechenden Benutzer aus.

   **Request**:

   .. sourcecode:: http

      GET /@users/john.doe HTTP/1.1
      Accept: application/json

   **Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "@id": "http://demo.onegovgever.ch/@users/john.doe",
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
          "principal:og_demo_examplegroup",
          "Anonymous"
        ],
        "username": "john.doe"
      }


Im Property ``roles_and_principals`` sind die tatsächlichen
"roles and principals" des Users ersichtlich. Auch hier sind die mit ``principal:``
präfixten Einträge entweder Gruppen oder User, die anderen sind Rollen.
