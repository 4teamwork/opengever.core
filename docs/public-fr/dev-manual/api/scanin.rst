.. _scanin:

Scan-In
=======

L'Endpoint ``/@scan-in`` permet d'uploader des documents vers OneGov GEVER depuis un scanner.

Cette méthode se distingue d'un upload normal par l'absence du contexte d'utilisateur authentifié, utilisant un utilisateur défini dans un paramètre à la place. Cela offre l'avantage de pouvoir traiter le scanner en tant qu'utilisateur service générique, sans devoir authentifier les utilisateurs respectifs dans OneGov GEVER.

Les documents sont soit déposés dans la boîte de réception ou dans le référentiel personnel. Dans le référentiel personnel, les documents sont déposés dans un dossier nommé "entrée scanner". Si ce dossier n'existe pas, il est créé.

Les données sont transmises en tant que `multipart/form-data`, par l'intermédiaire d'une Request POST.

+-------------+------------------------------------------------------------------------------------------------------------------+
|  Paramètre  |                                                   Description                                                    |
+=============+==================================================================================================================+
| userid      | Nom du user pour lequel le document doit être transmis.                                                          |
+-------------+------------------------------------------------------------------------------------------------------------------+
| destination | Emplacement vers lesquels le document doit être transmis. ``inbox`` pour la boîte de réception, ``private``      |
|             | le référentiel personnel.                                                                                        |
+-------------+------------------------------------------------------------------------------------------------------------------+
| org_unit    | Titre ou ID de l'unité d'organisation. Uniquement nécessaire au en cas de multiples boîtes de réception.         |
+-------------+------------------------------------------------------------------------------------------------------------------+


Exemple: Upload d'un document vers le référentiel personnel de l'utilisateur hugo.boss.

.. sourcecode:: http

  POST /gever/@scan-in HTTP/1.1
  Authorization: [AUTH_DATA]
  Accept: application/json
  Content-Type: multipart/form-data; boundary=------------------------b3e801e2d0fb0cc9
  Content-Length: [NUMBER_OF_BYTES_IN_ENTIRE_REQUEST_BODY]

  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="userid"

  hugo.boss
  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="destination"

  private
  --------------------------b3e801e2d0fb0cc9
  Content-Disposition: form-data; name="file"; filename="helloworld.pdf"
  Content-Type: application/octet-stream

  [FILE_DATA]
