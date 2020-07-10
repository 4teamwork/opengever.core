.. _authentication:

Authentisierung
===============

Die REST API verwendet Plone PAS (Pluggable Authentication System) für die
Authentisierung.

Das bedeutet, dass jede Authentisierungsmethode, die von einem installierten
PAS Plugin unterstützt wird, grundsätzlich auch mit der REST API funktioniert.

  Die genauen Details zu den installierten Authentisierungs-Plugins und deren
  Konfiguration sind je nach Kunde und Bedürfnissen unterschiedlich. Bei
  Fragen oder Änderungswünschen zu Ihrer Konfiguration wenden Sie sich bitte
  an unseren Support.

Im folgenden sind die Authentisierungsmethoden beschrieben, welche
von OneGov GEVER unterstützt werden.


.. toctree::
   :maxdepth: 1

   basic_auth
   oauth2_token_auth
   jwt
   logout

.. disqus::
