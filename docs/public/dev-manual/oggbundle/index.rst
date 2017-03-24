.. _kapitel-oggbundle:

====================================
Spezifikation Importformat OGGBundle
====================================

Diese Dokument beschreibt die Spezifikation der Datenschnittstelle zur
Migration eines Mandanten aus dem OS-Laufwerk in den zugehörigen
GEVER-Mandanten.

Changelog:

+---------------+--------------+-------------+-----------------------------------------+
| **Version**   | **Datum**    | **Autor**   | **Kommentar**                           |
+===============+==============+=============+=========================================+
| 0.1.3         | 10.02.2017   | LG          | Ergänzt: Setzen des Workflow-Status     |
+---------------+--------------+-------------+-----------------------------------------+
| 0.1.2         | 16.01.2017   | LG          | JSON-Schemas referenziert               |
+---------------+--------------+-------------+-----------------------------------------+
| 0.1.1         | 12.01.2017   | LG          | Nicht erlaubte Dateiformate definiert   |
+---------------+--------------+-------------+-----------------------------------------+
| 0.1           | 26.11.2016   | LG, DE      | Initialer Entwurf                       |
+---------------+--------------+-------------+-----------------------------------------+

Status: In Arbeit

Die hier beschriebene Schnittstelle dient dem einmaligen Import eines
Ordnungssystems, seiner Ordnungspositionen, Dossiers/Subdossiers und
Dokumente/Mails nach OneGov GEVER. Die Migration findet ab einem
JSON-basierten Zwischenformat statt. Dieses muss einem validen Schema
entsprechen, und die darin enthaltenen Daten müssen die in OneGov GEVER
geltenden Geschäftsregeln erfüllen.

**Zu migrierende Inhaltstypen:**


+------------------------------+-------------+
| **Ordnungssysteme**          | Ja          |
+==============================+=============+
| **Ordnungspositionen**       | Ja          |
+------------------------------+-------------+
| **Dossiers**                 | Ja          |
+------------------------------+-------------+
| **Dokumente**                | Ja          |
+------------------------------+-------------+
| **Mails**                    | Ja          |
+------------------------------+-------------+
| Kontakte                     | Nein \*     |
+------------------------------+-------------+
| Organisationseinheiten       | Nein \*\*   |
+------------------------------+-------------+
| Sitzungen                    | Nein        |
+------------------------------+-------------+
| Aufgaben / Weiterleitungen   | Nein        |
+------------------------------+-------------+

\* *“Kontakte” bezeichnet in diesem Zusammenhang einen speziellen
Inhaltstyp in OneGov GEVER, mit welchem Adressdaten direkt in GEVER
erfasst werden können, welche nicht in anderen Systemen wie z.B. AD
geführt werden. Benutzer aus dem AD werden hingegen in OneGov GEVER auch
importiert werden, allerdings direkt aus dem AD, nicht als Teil des
Zwischenformats*

\*\* *Details wie die mit Organisationseinheiten verknüpften
Berechtigungen aus OS-Laufwerk genau migriert werden müssen noch geklärt
werden. Die Organisationseinheiten selbst müssen jedoch nicht migriert
werden.*

Inhalt:

.. toctree::
   :maxdepth: 2

   oggbundle.rst
   anhang.rst
