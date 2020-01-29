JSON Web Tokens (JWT)
---------------------

L'API REST inclut un plugin permettant d'émettre des `JSON Web Tokens <https://en.wikipedia.org/wiki/JSON_Web_Token>`_ .

L'authentification basée sur des tokens est particulièrement bien adaptée pour la connexion d'applications tierces à l'API, permettant d'éviter à devoir stocker les détails de connexion d'un utilisateur dans l'application.

Émettre
^^^^^^^

Un token est émis à l'aide d'une Request POST sur l'Endpoint ``@login``. Le Body de la Request doit contenir les détails de connexion de l'utilisateur pour lequel le token doit être émis:

.. sourcecode:: http

  POST /@login HTTP/1.1
  Accept: application/json
  Content-Type: application/json

  {
      "login": "admin",
      "password": "admin"
  }

Le serveur répond avec un objet JSON contenant le token:

.. literalinclude:: examples/login.json
   :language: http

Utiliser
^^^^^^^^

Le token peut désormais être utilisé pour toutes les Requests subséquentes. Pour cela, il faut définir un header ``Authorization`` avec la méthode d'authentification ``Bearer`` ainsi que le token:

.. sourcecode:: http

  GET /Plone HTTP/1.1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
  Accept: application/json

Renouveler
^^^^^^^^^^

Par défaut, le token expire après 12 heures et doit donc être renouvelé auparavant. Pour renouveler le token, il est possible d'effectuer une Request ``POST`` sur l'Endpoint ``@login-renew``:

.. sourcecode:: http

    POST /@login-renew HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

Le serveur répond avec un objet JSON contenant le nouveau token:

.. literalinclude:: examples/login_renew.json
   :language: http


Invalider
^^^^^^^^^

L'Endpoint ``@logout`` permet d'invalider un token. Pour cela, les tokens doivent être persistants côté serveur. Dans la configuration standard, le tokens ne sont pas persistants et ne peuvent donc pas être activement invalidés. Si la possibilité d'émettre des tokens activement invalidables s'avère nécessaire, nous pouvons configurer cela pour vous.

La Request de log-ou peut être lancée en spécifiant le token existant dans le header ``Authorization``:

.. sourcecode:: http

    POST /@logout HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

Si l'invalidation a eu lieu avec succès, le serveur retourne une Response ``204`` vide:

.. literalinclude:: examples/logout.json
   :language: http

.. disqus::
