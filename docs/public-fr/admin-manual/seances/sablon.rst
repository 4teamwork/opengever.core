Utiliser des champs de fusion dans des modèles Sablon
-----------------------------------------------------

Dans un modèle, l’itération à travers une liste de valeurs s’effectue à l’aide des valeurs de champs de fusion suivants:

.. code-block:: none

    [<liste>:each(member)]
    ...
    [<liste>:endEach]

où ´´<liste>´´ correspond à une métadonnée du type «liste» (p. ex. ´´participants´´). Le texte entre les deux champs de fusion (évoqué par «...») sera inséré dans le document Word généré après chaque itération de boucle. Pour insérer le contenu d’une métadonnée dans un modèle, il faut placer un signe d’égalité (´´=´´) devant le nom de la métadonnée souhaitée dans le champ de fusion. Par exemple: ´´[=meeting.date]´´ retourne la date de séance à être insérée à la position marquée dans le modèle Word.

De plus, des commentaires qui ne font pas partie des documents Word générés (Procès-verbal, extrait de p.-v., etc.) peuvent être insérés dans le modèle Word. Les commentaires doivent se trouver entre les champs ``comment`` et ``endComment``.

Une documentation (en anglais) de la librairie sablon est disponible sur https://github.com/senny/sablon#conditionals. Des exemples de fichier Sablon peuvent être récupérés sur https://github.com/senny/sablon#examples.

.. disqus::