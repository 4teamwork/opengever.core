Documents générés
=================

Les documents générés sont composés sur la base d’une multitude de modèles. Ce chapitre a pour but de donner un aperçu sur la méthode de création de ces documents.

Ordre du jour / Procès-verbal
-----------------------------

Les procès-verbaux sont composés d’une zone de début, d’une section de contenus (points à l’ordre du jour) et d’une zone de fin. La zone de début contient les métadonnées de la commission et de la séance en question, ainsi que, dans la plupart des cas, l’ordre du jour. La section de contenus est formée d’une liste d’objets à traiter et de leurs détails respectifs. La zone de fin est prévue pour les signatures des responsables du déroulement de la séance.

Les points à l’ordre du jour se distinguent en 2 catégories : intertitres et objets de discussion. Les intertitres servent à créer des sections pour regrouper les objets de discussion et ne contiennent que du texte. Leur format est défini dans le modèle d’intertitre. Les objets de discussion sont composés, à leur tour d’une section de début, du contenu du document de requête/décision et d’une section de fin.

La structure du document de procès-verbal peut être visuellement résumée comme suit ::

|img-products-1|

Les modèles marqués d’un astérisque sont optionnels.

**Important**
Avant l’assemblage du document complet, les métadonnées sont insérées dans les différents modèles à l’intermédiaire d’un système de traitement pour modèles de documents Word (Nommé Sablon, utilisant le langage de programmation Ruby). Lors de la composition les pieds de page des documents de requête/décision sont ignorés. C’est donc le modèle de début de procès-verbal qui va déterminer l’apparence des styles, ainsi que des en-têtes et pieds de page du document final.

Extrait du procès-verbal
------------------------

Des extraits de procès-verbal sont générés à base d’une section de début d’extrait, du document de décision et d’une section de fin. Les métadonnées de la commission, de la séance en question et de l’objet délibéré sont typiquement insérées dans la section de début. Dans la zone de fin, on retrouve usuellement les signatures des responsables pour le déroulement de la séance entière.

La structure du document d’extrait de procès-verbal peut être visuellement résumé comme suit ::

|img-products-2|

Le modèle marqué d’astérisque est optionnel.

**Important**
Avant l’assemblage du document complet, les métadonnées sont insérées dans les différents modèles à l’aide de Sablon, ignorant les en-têtes et pieds de page des documents de requête et de la section de fin. Les styles, en-têtes et pieds de page doivent donc être définis au niveau de la section de début, selon la charte graphique établie au sein de l’organisation. 


.. |img-products-1| image:: ../img/media/img-products-1.png
.. |img-products-2| image:: ../img/media/img-products-2.png