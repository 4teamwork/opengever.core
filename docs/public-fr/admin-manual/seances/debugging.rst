Débogage de modèles Sablon
--------------------------

Pour le débogage, les modèles types de contenus Plone Views suivants sont à la disposition:

- «modèle Sablon»: ``fill_meeting_template`` insère des données de test dans le modèle Sablon. Cela permet de rapidement identifier des problèmes liés au formatage pour la syntaxe de la librairie sablon.

- «séance»: ``download_protocol_json`` permet de récupérer le fichier JSON qui est utilisé pour la génération du document à partir du modèle Sablon.

- «séance»: ``debug_docxcompose`` permet de télécharger séparément les fichiers «docx» qui seront assemblés en un document de procès-verbal dans au format .zip. Cela facilite l’analyse de problèmes potentiels avec docxcompose.

- «objet de discussion»: ``debug_excerpt_docxcompose`` permet de télécharger séparément les fichiers «docx» qui seront assemblés en un extrait de procès-verbal au format .zip. Cela facilite l’ analyse de problèmes potentiels avec docxcompose. l’URL contient l’ID de l’objet de discussion ainsi que les autres actions qui y sont liées, comme p. ex: ``meeting-X/agenda_items/YZ/debug_excerpt_docxcompose``.

.. disqus::
