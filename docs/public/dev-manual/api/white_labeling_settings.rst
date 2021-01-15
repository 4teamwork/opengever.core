.. _white-labeling-settings:

White Labeling
==============
Der ``@white-labeling-settings`` Endpoint liefert eine Übersicht über die White Labeling Konfiguration. Der Endpoint steht nur auf Stufe PloneSite zur Verfügung.


**Beispiel-Request**:

   .. sourcecode:: http

       GET /@white-labeling-settings HTTP/1.1
       Accept: application/json

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

        {
          "@id": "http://localhost:8080/fd/@white-labeling-settings",
          "custom_support_markup": {
            "de": "<div>Support in der Schweiz</div>",
            "en": "<div>Soutien en France</div>",
            "fr": "<div>Support in the United Kingdom</div>",
          },
          "logo": {
            "src": "data:image/png;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
          },
          "show_created_by": true,
          "themes": {
            "light": {
              "appbarcolor": "#ee03d3",
              "primary": "#55ff00"
            }
          }
        }


