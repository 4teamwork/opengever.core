Authentification CAS via le portail
===================================

Le protocol CAS et un protocol de Single-Sign-On qui permet de s'authentifier à un client GEVER via le portail.

Processus d'authentification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

L'authentification se déroule en 4 étapes:

1. Authentification au portail avec nom d'utilisateur et mot de passe.
2. Obtention d'un ticket CAS du portail.
3. Echange du ticket CAS contre un JWT (JSON Web Token) éphémère auprès du service en question (client GEVER).
4. Utilisation du JWT pour l'authentification des requêtes suivantes au service.

Authentification au portail
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pour obtenir un ticket CAS, un client doit commencer par s'identifier au portail.
Ceci se fait avec l'endpoint ``/api/login`` du portail:

**Login-Request**:

.. sourcecode:: http

   POST /portal/api/login HTTP/1.1
   Accept: application/json

   {
       "username": "john.doe",
       "password": "secret"
   }


**Login-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json
  Set-Cookie: csrftoken=...; sessionid=...

  {"username":"john.doe","state":"logged_in","invitation_callback":""}

Le client est ensuite authentifié au portail par un Session-Cookie. Le client
HTTP doit donc renvoyer avec les requêtes suivantes les cookies obtenus du portail.

Le portail livre également, en plus du Session-Cookie, un CSRF-Token sous forme de cookie.
Celui-ci doit être extrait par le client et inclus dans les requêtes suivantes au portail
dans le HTTP Header ``X-CSRFToken``.

Le client doit également indiquer l'URL du portail dans le ``Referer`` HTTP
Header, sinon les requêtes seront déclinées par le méchanisme de protection CSRF.

Obtention d'un ticket CAS du portail
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le client peut obtenir un ticket CAS du portail pour le service souhaité
via l'endpoint ``/api/cas/tickets``.

**Ticket-Request**:

.. sourcecode:: http

   POST /portal/api/cas/tickets HTTP/1.1
   Accept: application/json
   Referer: https://apitest.onegovgever.ch/portal
   X-CSRFToken: ypI3LgB7n7HYKMEd64KjHl3EXEye2XTN4p41AFeG9cCkwGv0kWeP8Z87Hssf3d7W

   {
     "service": "http://apitest.onegovgever.ch/"
   }


**Ticket-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "ticket": "ST-12345",
    "service": "http://apitest.onegovgever.ch/"
  }

Le serveur répond avec un ``ticket`` CAS dans le JSON-Body, qui peut ensuite
être échangé auprès du service contre un JWT (voir prochaine étape).

Echange du ticket CAS contre un JWT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le client peut maintenant échanger le ticket CAS contre un JWT (JSON Web Token) éphémère auprès du service en question (client GEVER) via l'endpoint ``@caslogin``.

**Token-Request**:

.. sourcecode:: http

   POST /@caslogin HTTP/1.1
   Accept: application/json

   {
     "ticket": "ST-12345",
     "service": "http://apitest.onegovgever.ch/"
   }


**Token-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "token": "eyJhbGciOiJI..."
  }

Ce JWT peut ensuite être utilisé par le client pour authentifier les requêtes suivantes
directement auprès du service.

Requêtes API au service authentifiées avec le JWT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le client authentifie toutes les requêtes utlérieures à l'API du service
en incluant le JWT obtenu comme Bearer Token dane le HTTP Header
``Authorization``:

**API-Request**:

.. sourcecode:: http

   GET / HTTP/1.1
   Accept: application/json
   Authorization: Bearer eyJhbGciOiJI...


**API-Response**:

.. sourcecode:: http

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "https://apitest.onegovgever.ch/",
    "...": "..."
  }

Implémentation conseillée  pour un client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Les étapes décrites ci-dessus représentent le cas le plus simple,
d'un client qui veut s'authentifier une seule fois.

Une certaine logique pour actualiser régulièrement le JWT doit être
implémentée pour un client qui veut continuellement exectuer des requêtes
authentifiées.

Au lieu d'essayer de prédire l'expiration du JWT, le client devrait s'attendre
à ce que n'importe quelle requête puisse échouer à cause d'un JWT plus valable.
Il devrait alors obtenir un nouveau Token avant de réessayer la requête en question.

Voici un exemple d'implémentation d'un tel client en Python:


.. container:: collapsible

    .. container:: header

       **Exemple de client (Python)**

    .. literalinclude:: examples/portal-cas-example.py
