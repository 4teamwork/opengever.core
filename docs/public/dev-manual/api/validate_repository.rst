.. _validate_repository:

Ordnungssystem validierung
==========================

Mit dem ``@validate-repository`` Endpoint kann eine Ordnungssystem als Excel Datei validiert werden. Wenn das Ordnungssystem valid ist wird mit "200 OK" geantwortet, sonst mit "400 BadRequest".

**Beispiel-Request**:

   .. sourcecode:: http

       POST /@validate-repository HTTP/1.1
       Content-Type: application/json
       Accept: application/json

       {
        "file": {
            "filename": "ordnungssystem.xlsx",
            "data": "UEsDBBQABgAIAAAAIQD1WTWAcQEAAJwFAAATAAgCW0...==",
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
       }

**Beispiel-Response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Type: application/json

      {
        "additional_metadata": {},
        "message": "missing_parent_position",
        "translated_message": "Parent position 0.0 for 0.0.0 does not exist!",
        "type": "BadRequest"
      }
