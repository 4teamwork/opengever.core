HTTP Basic Auth
---------------

Pour la HTTP Basic Auth, un Header ``Authorization`` doit être défini dans la Request:

.. sourcecode:: http

  GET /ordnungssystem HTTP/1.1
  Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
  Accept: application/json

Les HTTP Client libraires du langage de programmation utilisé offrent usuellement des fonctions d'aide pour générer ce header basé sur les nom et mot de passe.

**Exemple de code (Python)**: Créer une session et définir les headers

.. literalinclude:: ../examples/example_session.py

.. disqus::
