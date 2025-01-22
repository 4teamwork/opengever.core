.. _workflow:

Workflow
========

In GEVER haben viele :ref:`Inhaltstypen <content-types>` einen assozierten Workflow (z.B.
Ordnungspositionen, Dossiers, Aufgaben, ...).

Der aktuelle **Workflow-State** eines Objekts ist der Einfachheit halber als
``review_state`` direkt in der :ref:`GET <content-get>` Repreäsentation
eines Objekts enthalten:

.. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
       "@context": "http://www.w3.org/ns/hydra/context.jsonld",
       "@id": "https://example.org/dossier-15",
       "@type": "opengever.dossier.businesscasedossier",
       "...": "...",
       "review_state": "dossier-state-active"
    }


Für die restlichen Aspekte des Workflows eines Objekts wird der ``@workflow``
Endpoint verwendet:


.. http:get:: /(path)/@workflow

   Liefert die Workflow-Informationen zu dem durch `path` addressierten Objekt
   zurück.

   Die Workflow-Informationen enthalten die **Workflow-History** (und darin
   enthalten, der aktuelle Workflow-State) und die für dieses Objekt möglichen
   **Workflow-Transitionen**.

   **Beispiel-Request**:

   .. sourcecode:: http

       GET /dossier-15/@workflow HTTP/1.1
       Accept: application/json

   **Beispiel-Response**:

   .. literalinclude:: examples/workflow_get.json
      :language: http

   Dieses Dossier befindet sich zur Zeit im Status abgeschlossen (
   ``dossier-state-resolved``, letzter Eintrag in der Workflow-History).

   In diesem Beispiel ist die einzig von diesem Workflow-State ausgehende
   Transition, das Dossier wiederzueröffnen
   (``dossier-transition-reactivate``). Diese Transition kann ausgeführt
   werden, indem ein ``POST`` Request auf die entsprechende URL durchgeführt
   wird:

.. http:post:: /(path)/@workflow/(transition)

   Führt für das durch `path` addressierte Objekt die Workflow-Transition
   `transition` durch.

   **Beispiel-Request**:

   .. sourcecode:: http

       POST /dossier-15/@workflow/dossier-transition-reactivate HTTP/1.1
       Accept: application/json

   **Beispiel-Response**:

   .. literalinclude:: examples/workflow_post.json
      :language: http


Workflow-Schema
~~~~~~~~~~~~~~~

Gewisse Workflow Transitions, wie bspw. der Dossier-Abschluss, erwarten je nach Konfiguration weiter Angaben. Diese Schemas können mit einem Request auf den zusätzlichen API Endpoint ``@workflow-schema`` abgefragt werden. Mit dem Rückgabewert kann ein entsprechendes Formular generiert werden.

Workflow-Informationen für Massen-Transitionen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Dieser Endpoint liefert Informationen über die Workflow-Transitionen, die einem bestimmten Objekt zugeordnet sind.

Diese Information ist notwendig, um Massen-Transitionen in einer Benutzeroberfläche zu ermöglichen. Das UI kann anhand eines bestimmten Referenztyps (z. B. des ersten Objekts einer Liste) eine einheitliche Liste von Transitionen für alle Objekte dieser Auflistung anzeigen.

   **Beispiel-Request**:

   .. sourcecode:: http

       GET .../dossier-1/@workflow-bulk-transition HTTP/1.1
       Accept: application/json

   **Beispiel-Antwort:**

   .. sourcecode:: http

       HTTP/1.1 200 OK
       Content-Type: application/json

       {
         "@id": ".../dossier-1/@workflow-bulk-transition",
         "transitions": [
           {
             "source_state_id": "dossier-state-active",
             "target_state_id": "dossier-state-resolved",
             "transition_id": "dossier-transition-resolve",
             "workflow_id": "opengever_dossier_workflow"
           },
           {
             "source_state_id": "dossier-state-resolved",
             "target_state_id": "dossier-state-active",
             "transition_id": "dossier-transition-reactivate",
             "workflow_id": "opengever_dossier_workflow"
           }
         ]
       }
