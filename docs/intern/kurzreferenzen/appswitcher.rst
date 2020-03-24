.. _appswitcher:

App-Switcher im neuen Frontend
==============================
Jeder Mandant und jeder Teamraum repräsetiert eine eigene Applikation. Der Benutzer kann über den App-Switcher oben links im neuen UI zwischen diesen Applikationen wechseln.

Das UI erhält vom Backend im ``@config``-Endpoint eine ``apps_url``. Anschließend führt das UI einen GET Request auf die URL aus und erhält eine Liste von möglichen Applikationen zurück. Die Anwendungen werden anhand der erhaltenen Konfiguration für den Benutzer angezeigt.

Unsere GEVER-Installationen beziehen die Apps vom `neuen Portal Ianus <https://github.com/4teamwork/ianus>`_.

Installation
------------
Development
~~~~~~~~~~~
Wird GEVER im Development-Modus ausgeführt, wird ein Set von Entwickler-Applikationen im Appswitcher angezeigt. Die Applikationen sind statisch.

`developmentApps.js <https://github.com/4teamwork/gever-ui/blob/master/src/apps/service/developmentApps.js>`_

Eine weitere Konfiguration ist nicht nötig.

Produktion
~~~~~~~~~~
Folgende Schritte sind für ein produktives Deployment notwendig:

1. das neue Portal Ianus muss installiert sein
2. alle zur Verfügung stehenden Applikationen müssen im Ianus erfasst sein
3. die ``apps_url`` muss auf den Ianus Endpoint ``/api/apps`` zeigen

Apps-Konfiguration im Inaus
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Das `neue Portal Ianus <https://github.com/4teamwork/ianus>`_ stellt unter ``/api/apps`` einen Endpoint für Applikationen zur Verfügung. Der Endpoint kann im GEVER als ``apps_url`` verwendet werden.

Alle zur Verfügung stehenden Mandanten oder Applikationen müssen im Ianus manuell unter **Applications** erfasst werden. Folgende Konfigurationen sind bisher möglich:

**GEVER**

- Titel: ``OneGov GEVER``
- Subtitle: ``4teamwork``
- URL: ``URL zur Applikation oder Mandanten: www.example.com/fd``
- Farbe: ``#03A9F4``
- Icon: `appGever.svg <https://github.com/4teamwork/gever-ui/blob/master/src/assets/icons/appGever.svg>`_
- Typ: ``gever``

**Teamraum**

- Titel: ``Teamraum``
- Subtitle: ``4teamwork``
- URL: ``URL zur Applikation: www.example.com/tr``
- Farbe: ``#3F51B5``
- Icon: `appWorkspaces.svg <https://github.com/4teamwork/gever-ui/blob/master/src/assets/icons/appWorkspaces.svg>`_
- Typ: ``teamraum``

Natürlich können die Konfigurationen individuell an den Kunden und an die Umgebung frei angepasst werden.

``apps_url`` im GEVER konfigurieren
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Für ein produktives Deployment muss die ``apps_url`` über eine Umgebungsvariable gesetzt werden

``export APPS_ENDPOINT_URL=http://example.com/portal/api/apps``

Die URL muss eine Liste von Anwendungen zurückgeben.

In einem produktiven Deployment setzten wir die URL auf das neue Portal: ``www.example.com/portal/api/apps``


Edge Cases
----------
Wenn keine ``apps_url`` in einem produktiven Deployment gesetzt wurde, wird standardmässig ein Set von Standard-Applikationen im Appswitcher angezeigt. Die Applikationen sind statisch unter `defaultApps.js <https://github.com/4teamwork/gever-ui/blob/master/src/apps/service/defaultApps.js>`_ zu finden.

Wenn also ein GEVER mit nur einem Mandanten betrieben wird, müssen keine Apps speziell erfasst oder konfiguriert werden.
