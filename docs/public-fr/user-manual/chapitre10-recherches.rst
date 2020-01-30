.. _label-recherches:

Recherches et filtres
=====================

Types de recherches
-------------------

Trois types de recherches sont disponibles:

- Recherche simple (live search)

- Recherche avancée

- Filtres

Avec les recherches simples et avancées, on cherche:

- Les champs texte de tous les objets (dossiers, documents, tâches)

- Aussi bien que le contenu des fichiers (recherche en plein texte).

Avec la recherche avec les filtres (par exemple dans un dossier), les objets
(dossiers, documents ou tâches) seront sélectionnés d’une liste. Le terme entré
cherche ensuite tous les objets en plein texte et livre le résultat directement dans la liste.

Règles et opérateurs pour les trois types de recherches
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Aucune différence n’est faite entre les majuscules et les minuscules.

- Les termes de la recherche seront toujours enchainés avec AND, cela veut dire
  qu’on peut entrer plusieurs termes de recherche. Il est seulement nécessaire de
  laisser un espace vide entre les termes et non pas des caractères spéciaux.
  Les résultats qui contiennent tous les termes de la recherche seront ensuite affichés.

- ``*`` (*astérisque*) fait office de fantôme pour aucun ou alors pour plusieurs symboles
  quelconques. Il ne peut cependant se trouver qu’après le mot de début et non pas
  au début d’un terme de recherche. Exemple du terme de recherche « portemanteau »:
  en cherchant ``porte*`` le terme sera trouvé, par contre en cherchant ``*manteau`` le terme
  de recherche ne sera pas trouvé.

- ``?`` (*point d‘interrogation*) fait office de fantôme pour un signe unique quelconque.

- ``-`` (*moins*): En plaçant un signe moins devant un terme (par exemple : ``documents –test``),
  des résultats de recherche s’affichent ; dans ces résultats, le terme exclu n’apparait
  pas mais les termes restants, oui.

- ``"`` (*guillemet*): En inscrivant des guillemets (exemple: ``"Ordonnance de police"``),
  la recherche se fera d’après le terme de recherche exact. Aucun autre opérateur ne doit
  figurer dans les guillemets.

Recherche simple
----------------

Pour une recherche simple, il existe deux façons de faire:

a) Recherche au moyen de l’entrée des débuts des mots.

b) Recherche au moyen de l’entrée des termes de recherche exacts.

Recherche au moyen de l’entrée des débuts des mots (recherche immédiate, recherche à la volée)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le terme de la recherche peut directement être tapé dans le champ de saisie de la recherche.
Les dix premiers résultats de recherches seront proposés *on the fly* (à la volée), cela signifie
qu’ils apparaissent dans une liste en-dessous du champ de recherche. Déjà au moment
de la saisie du terme de la recherche, le système met automatiquement une troncation à droite. (``*``)
En cliquant sur *Montrer tous* les éléments, la liste complète s’affiche, c’est-à-dire que tous
les termes commençant par le mot ou la partie de mot entré ont été trouvés.

Exemple: Recherche d’après le début du mot.

|img-recherches-1|

Le système insère automatiquement un astérisque (``*``) et trouve tous les mots qui
commence par pende. Dans le cas où le résultat de la recherche est un document,
l’aperçu correspondant sera aussi affiché (avec le module Recherche Visuelle activé).

|img-recherches-2|

La liste des résultats de la recherche est généralement classée par ordre de pertinence.
Les résultats peuvent également être triés par date ou par ordre alphabétique dans la fenêtre
de résultat de recherche. Pour cela, les options respectives doivent simplement être sélectionnées.

|img-recherches-3|

De plus, il y a la possibilité de filtrer les résultats en restreignant le choix
des types de contenu ou la plage de temps des dates de constitutions.

.. note::
  En saisissant des fragments de mots, seul le début des mots est pris en compte.

  Exemple: La saisie de ``porte`` a pour résultat ``porte``, ``portemonnaie``,  mais pas ``rapporte``.

Recherche au moyen de l’entrée des termes de recherche exacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Si on écrit dans le champ de recherche de la recherche immédiate le terme exact
souhaité, on doit finalement presser la touche :kbd:`Enter` ou appuyer sur le bouton *Recherche*.
Dans ce cas, seuls les résultats qui contiennent le terme exact sont listés. La liste
de résultats est par conséquent plus courte.

Recherche avancée
-----------------

Pour accéder à la recherche avancée, deux possibilités sont offertes: l’utilisateur
peut d'une part cliquer sur *Recherche avancée dans l'onglet de recherche en haut à droite*.

|img-recherches-4|

Ou alors l’utilisateur est déjà sur la page des résultats de recherche et, depuis
là, il peut aussi se tourner vers la *recherche avancée*:

|img-recherches-5|

Sur le masque de la *Recherche avancée*, des champs de recherches spécifiques par
type d’objets sont disponibles, par exemple le statut pour l’objet Dossier ou l’auteur
pour l’objet Document. Sur un masque, les champs peuvent être complétés et combinés.
La recherche est ainsi plus précise et le nombre de résultats s'en trouve diminué.

|img-recherches-6|

Tuyau: En cliquant avec la molette de la souris sur le lien Recherche avancée,
un formulaire de recherche s’ouvre dans un nouvel onglet. On peut ainsi mener une
recherche sans que l’aperçu actuel de OneGov GEVER ne doive être quitté.

|img-recherches-7|

.. note::
   Lorsque OneGov GEVER est installé avec plusieurs mandants, il faut faire attention
   à ce que la recherche des tâches ne touche qu’aux tâches qui sont enregistrées pour
   un seul et même mandant, c’est-à-dire celles qui sont disponibles dans
   le dossier de ce mandant.

Enregistrer des recherches
~~~~~~~~~~~~~~~~~~~~~~~~~~

Des recherches effectuées peuvent être enregistrées comme marque-page et être
à nouveau utilisées par la suite. Au moment d’appeler à nouveau l’URL, les résultats
mis à jour sont affichés.

Ainsi, il est par exemple possible de constituer une recherche d’après les dossiers
ouverts de l’année 2017 (statuts, date de début) dans la recherche avancée et
de l’enregistrer comme marque-page. Ce marque-page peut toujours être réutilisé.

|img-recherches-8|

L’URL qui est affiché après avoir cliqué en-haut sur Recherche contient
les paramètres de recherche enregistrés et peut être enregistré comme marque-page dans le browser.

|img-recherches-9|

Filtres
-------

Un champ filtre est à chaque fois disponible avec les listes de dossiers, documents ou tâches.
En entrant un terme de recherche dans le champ filtre, les objets qui contiennent
ce terme dans leur titre ou dans d’autres de leurs métadonnées seront mis en évidence
dans la liste affichée au-dessous. La recherche par filtre est très efficace et utile.
Avec le filtre – quasiment un tri – on obtient en règle générale une quantité de résultats gérable.

Dans le système de classement, chaque position et resp. les dossiers joints
qui s’y trouvent peuvent être filtrés. En cliquant sur la position à chercher,
le champ filtre apparait à la bonne page sous la barre bleue.

Exemple (cf. capture d’écran ci-dessous):

Filtrez dans la position du système de classement *6.0. Aménagement du territoire*
d’après Action. On arrive de suite, au moyen de la fonction filtre, aux dossiers
souhaités qui contiennent le terme Action dans leur titre.

|img-recherches-10|

Tous les tableaux peuvent également être filtrés sous l’onglet *Sommaire*.
On peut ainsi faire un choix dans ses propres dossiers, documents et tâches
aussi bien que dans toutes les tâches du mandant selon les autorisations ; de la sorte,
on accède très vite au contenu souhaité.

|img-recherches-11|

Le système fait toujours automatiquement une troncation à droite du mot ou de
la partie du mot entré/e. Les résultats apparaissent tout de suite. Une entrée
éventuelle au moyen de la touche :kbd:`Enter` ne change rien.

Au moment de filtrer les listes de dossiers et de tâches, les champs texte
des métadonnées (titre, description, mots-clés, commentaire) aussi bien que
le champ *Responsable* sont explorés. Au moment de filtrer les listes de documents,
les champs textes des métadonnées aussi bien que le plein texte des documents seront explorés.

.. note::
   La recherche par filtre n’est pas possible dans l’onglet Sommaire ou dans l’onglet
   *Info* où aucun tableau n’est classé.

.. |img-recherches-1| image:: ../_static/img/img-recherches-1.png
.. |img-recherches-2| image:: ../_static/img/img-recherches-2.png
.. |img-recherches-3| image:: ../_static/img/img-recherches-3.png
.. |img-recherches-4| image:: ../_static/img/img-recherches-4.png
.. |img-recherches-5| image:: ../_static/img/img-recherches-5.png
.. |img-recherches-6| image:: ../_static/img/img-recherches-6.png
.. |img-recherches-7| image:: ../_static/img/img-recherches-7.png
.. |img-recherches-8| image:: ../_static/img/img-recherches-8.png
.. |img-recherches-9| image:: ../_static/img/img-recherches-9.png
.. |img-recherches-10| image:: ../_static/img/img-recherches-10.png
.. |img-recherches-11| image:: ../_static/img/img-recherches-11.png
