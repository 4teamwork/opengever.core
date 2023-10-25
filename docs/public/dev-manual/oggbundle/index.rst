.. _kapitel-oggbundle:

=================================
Specification of format OGGBundle
=================================

This document describes the specification of the data interface for migrating data from a third party repository into OneGov GEVER.

Changelog:

+---------------+--------------+-------------+--------------------------------------------------------+
| **Version**   | **Date**     | **Author**  | **Comment**                                            |
+===============+==============+=============+========================================================+
| 1.3           | 20.06.2022   | PG          | Added: Creator                                         |
+---------------+--------------+-------------+--------------------------------------------------------+
| 1.2           | 16.06.2022   | PG          | Import of OGDS users                                   |
+---------------+--------------+-------------+--------------------------------------------------------+
| 1.1           | 10.08.2020   | LG          | Import of workspaces                                   |
+---------------+--------------+-------------+--------------------------------------------------------+
| 1.0           | 16.10.2017   | LG, PG      | Referencing existing content via file number           |
+---------------+--------------+-------------+--------------------------------------------------------+
| 0.1.3         | 10.02.2017   | LG          | Added: Setting the workflow status                     |
+---------------+--------------+-------------+--------------------------------------------------------+
| 0.1.2         | 16.01.2017   | LG          | JSON schemas referenced                                |
+---------------+--------------+-------------+--------------------------------------------------------+
| 0.1.1         | 12.01.2017   | LG          | Not allowed file formats defined                       |
+---------------+--------------+-------------+--------------------------------------------------------+
| 0.1           | 26.11.2016   | LG, DE      | Initial draft                                          |
+---------------+--------------+-------------+--------------------------------------------------------+

Status: in progress

The interface described here is used for the one-time import of a repository, its filing positions, dossiers/subdossiers and documents/mails into OneGov GEVER. The migration takes place from a JSON-based intermediate format. This must correspond to a valid schema and the data it contains must comply with the business rules applicable in OneGov GEVER.

Importable content types
------------------------

+------------------------------+-------------+
| **Repositories**             | Yes         |
+------------------------------+-------------+
| **Repository folders**       | Yes         |
+------------------------------+-------------+
| **Workspace roots**          | Yes         |
+------------------------------+-------------+
| **Workspaces**               | Yes         |
+------------------------------+-------------+
| **Workspace folders**        | Yes         |
+------------------------------+-------------+
| **Dossiers**                 | Yes         |
+------------------------------+-------------+
| **Documents**                | Yes         |
+------------------------------+-------------+
| **Mails**                    | Yes         |
+------------------------------+-------------+
| **OGDS Users**               | Yes         |
+------------------------------+-------------+
| Contacts                     | No \*       |
+------------------------------+-------------+
| Org units                    | No          |
+------------------------------+-------------+
| Meetings                     | No          |
+------------------------------+-------------+
| Tasks / forwardings          | No          |
+------------------------------+-------------+

\* *"Contacts" in this context refers to a special content type in OneGov GEVER that can be used to enter address data directly in GEVER that is not kept in other systems such as AD. Users from AD, on the other hand, will also be imported into OneGov GEVER, but directly from AD, not as part of the intermediate format*.


Content:
--------
.. contents::

OneGov GEVER Bundle (OGGBundle)
-------------------------------

The intermediate format for exporting data from a third party repository and importing it into OneGov GEVER is called the OneGov GEVER Bundle (**OGGBundle**).

The bundle can be understood as a "virtual directory": It follows a directory structure, which is built according to a certain pattern, and contains all the necessary information of the export. The bundle can thus be delivered for very small amounts of data as a ZIP file with the extension **.oggbundle** (e.g. **testinhalte.oggbundle**), or it can also be deposited or mounted on a server as a directory with the extension **.oggbundle**. The specific transport mechanism is not part of this specification, and can be chosen according to the application purpose.

All path specifications in a bundle are relative to the root of the bundle.

The bundle consists of a collection of JSON files whose contents must follow a specific schema, and a subdirectory :ref:`files/ <files>` which contains the files for documents (primary data).

----

A bundle contains one file per content type to be imported. In it, the respective content must be stored flat (without nesting) in JSON format. For each such file, a `JSON schema <http://json-schema.org/>`__ is provided, which precisely describes the structure of the JSON file and with which the content must be validated before an import. The following sections describe the content types currently supported and the associated files in the bundle.

|img-image-1|

Configuration and bundle metadata
---------------------------------

metadata.json
~~~~~~~~~~~~~

This file contains metadata about the bundle, e.g. the creation date and creator of the bundle or the intended use (optional).

configuration.json
~~~~~~~~~~~~~~~~~~

This file contains the configuration of the client, especially the value ranges needed to validate the contents, which are configurable for certain fields per client.

JSON schema: :ref:`configuration.schema.json <configuration_schema_json>`

Data for content types
----------------------

reporoots.json
~~~~~~~~~~~~~~

This file contains one or more classification system (repository) roots.

JSON Schema: :ref:`reporoots.schema.json <reporoots_schema_json>`

repofolders.json
~~~~~~~~~~~~~~~~

This file contains the individual repository folders that are stored in the repository root.

JSON Schema: :ref:`repofolders.schema.json <repofolders_schema_json>`

workspaceroots.json
~~~~~~~~~~~~~~~~~~~

This file contains a workspace root.

If a workspace root already exists on the installation into which an OGGBundle with workspaces is imported, this file can be omitted. During the import, it is then assumed that exactly one workspace root already exists and the workspaces are imported into this workspace root.

In this case, the workspace must not have a ``parent_guid`` set.

JSON Schema: :ref:`workspaceroots.schema.json <workspaceroots_schema_json>`

workspaces.json
~~~~~~~~~~~~~~~

This file contains one or more workspaces.

The workspaces are assigned to a workspace root via the ``parent_guid``, which is also included in the bundle.

Alternatively, the ``parent_guid`` for workspaces, and the definition of a workspace root in the ``workspaceroots.json`` can be omitted - the workspaces will then be imported into an already existing workspace root.

JSON schema: :ref:`workspaces.schema.json <workspaces_schema_json>`

workspacefolders.json
~~~~~~~~~~~~~~~~~~~~~

This file contains one or more workspaces folders.

JSON Schema: :ref:`workspacefolders.schema.json <workspacefolders_schema_json>`

dossiers.json
~~~~~~~~~~~~~

This file contains dossiers and subdossiers, these can be stored in the repository folder (classification items).

JSON schema: :ref:`dossiers.schema.json <dossiers_schema_json>`

documents.json
~~~~~~~~~~~~~~

This file contains the metadata of the documents. The binary files are provided in the **files/** folder and must be referenced with a path relative to the bundle. The metadata includes, among other things, the file name. The file name of the file on the file system is not used, but is overwritten by the metadata.

See the explanation below in the section :ref:`files/ <files>` for details regarding file paths.

JSON Schema: :ref:`documents.schema.json <documents_schema_json>`

.. _files:

ogds_users.json
~~~~~~~~~~~~~~~~

This file contains the users to be imported into the OGDS. As a rule, these are former, no longer active users who can be imported in this way.

The value ``guid`` must correspond to the ``userid``.

JSON schema: :ref:`ogds_users.schema.json <ogds_users_schema_json>`


files/
~~~~~~

This folder contains the primary files of the documents. Whether the files are stored flat, or nested in further subfolders is not specified - the structuring of this directory is left to the supplier of the bundle. However, the file names must be normalised to avoid incompatibilities that can arise due to different character sets in different environments. We recommend a simple scheme with ascending numbering such as **file\_00123.pdf**.

The actual title / file name used in OneGov GEVER is controlled by the **title** attribute in the metadata supplied in **documents.json**: In the **title** attribute, the original file name, including file extension, should be supplied. In OneGov GEVER, the title of the document is then derived from this attribute by removing the file extension. The file extension itself, on the other hand, is used to determine the content type (MIME type).

The following file types are not allowed in OGGBundles:

- **.exe**

- **.dll**

Paths / file names may only contain alphanumeric characters, underscore and hyphen (**[0-9][a-zA-Z][-\_]**). All paths are case-sensitive, and must not exceed a maximum length of 255 characters. The paths are to be specified as UNIX paths relative to the root of the bundle (separated with forward slash).

Mapping of nesting (containment)
--------------------------------

The hierarchical relationship between objects is mapped using parent pointers.


parent_guid
~~~~~~~~~~~

Since the data in the JSON files is not stored in a nested manner, it is necessary to resolve this nesting during the import. This nesting is mapped by means of a globally unique ID (GUID) and a pointer from children to the containing parent. For this purpose, each object must have a GUID. This must be stored in the attribute **guid**. The nesting is established by means of a reference to the parent. For this purpose, each object that has a parent must define the attribute **parent\_guid** and thus reference the parent:

.. code::

  {
  "guid": "7777-0000-0000-0000",
  ...
  },
  {
  "guid": "9999-0000-0000-0000",
  "parent_guid": "7777-0000-0000-0000",
  ...
  }

It is also possible to reference an object as a parent via the ``parent_guid`` that is already in the system due to a previous import. This parent item then does not have to be supplied in the bundle (but may be, as long as the GUID remains the same).

If both an item with a specific GUID is delivered in the bundle and there is also an item with an identical GUID already in the system, the item from the bundle is ignored and skipped (so no metadata of the already existing item is updated either).

This means that if two bundles are imported one after the other, of which the second contains *additional* data, only the difference is imported (objects with GUIDs that did not yet exist in the first bundle). However, this requires that the GUIDs of objects that are to be recognised as "equal" / "already exist" do not change (otherwise the objects will be imported again and will therefore exist twice).


parent_reference
~~~~~~~~~~~~~~~~

As an alternative to the GUID, the reference number of an object can also be used as a unique reference to the parent. The use of the reference number as a parent pointer allows already existing objects to be referenced via their unique reference number, thus enabling partial imports. For example, it is possible to import documents into an existing dossier by referencing this dossier via its reference number.

If the reference number is used for referencing, the attribute **parent\_reference** (instead of **parent\_guid**) must be set. The file number in this attribute is expected to be a nested array of integers that map the individual components of the file number (without formatting). Example: `[[1, 3, 5], [472, 9]` corresponds to the reference number `1.3.5 / 472.9` (position 1.3.5, dossier 472, subdossier 9):

.. code::

  {
  "guid": "9999-0000-0000",
  "parent_reference": [[1, 3, 5], [472, 9],
  ...
  }


See also section :ref:`Business rules <business_rules>` for details of which content types may be nested and how.

Permissions
-----------

Permissions are inherited by default to children in OneGov GEVER. It is permitted to set permissions at the level of the repositoryroot, repositoryfolder and dossier, whereby permissions at the level of the dossier should be the exception.

The possible permissions are basically dependent on the respective content type. The permitted values can be taken from the JSON schema for the type. For most GEVER content, however, the controllable permissions are identical - the exception being workspace content.

Permissions are set by specifying a mapping according to the schema in the ``_permissions`` property of the item.

Example:

.. code::

  {
  "guid": "9999-0000-0000-0000",
  ...

    "_permissions": {
      "read": [
        "all_users"
      ],
      "add": [
        "privileged_users"
      ],
      "edit": [
        "privileged_users"
      ],
      "close": [
        "admin_users"
      ],
      "reactivate": [
        "admin_users"
      ]
    }
  }

Permissions can be assigned granularly for the following roles:

- ``read`` (read)

- ``add`` (add dossiers)

- ``edit`` (edit dossiers)

- ``close`` (close dossiers)

- ``reactivate`` (reactivate dossiers)

- ``manage_dossiers`` (manage dossiers)

In addition, a **block\_inheritance** flag can be used to specify whether the inheritance of permissions should be interrupted at this level. This means that from this level onwards, only the explicitly defined access authorizations are valid and no authorizations are taken over from the parent via inheritance:

.. code::

  "_permissions": {
    "block_inheritance": true,
    ...
  }

Permissions are assigned to one or more "principals", this corresponds to a user or a group.

--------------

For **workspaces** there are separate roles which can be set at different levels.

The following roles can be assigned at the workspace root level:

- ``workspaces_creator`` (create workspaces)
- ``workspaces_user`` (list workspaces)

At the level of a single workspace or a workspace folder, the following roles can be assigned:

- ``workspace_admin`` (admin)
- ``workspace_member`` (member)
- ``workspace_guest`` (guest)

**Participations in workspaces are mapped via local roles. To import a user's participation in a workspace, it is therefore sufficient to express the type of participation via a corresponding local role assignment in the ``_permissions`` property.**


Setting values
--------------

Default values are only set if the corresponding attributes are not available in the supplied JSON.

Setting the workflow status
---------------------------

For objects with a workflow, the property ``review_state`` can be used to specify in which state the object can be created.

The complete list of valid workflow states is defined in the schema of the corresponding objects.

Repositories
~~~~~~~~~~~~
| 

+-----------------------------------+---------+
| ``repositoryroot-state-active``   | Active  |
+-----------------------------------+---------+

Initial state: ``repositoryroot-state-active``

JSON Schema: :ref:`reporoots.schema.json <reporoots_schema_json>`

Repositoryfolders
~~~~~~~~~~~~~~~~~
| 

+-------------------------------------+---------+
| ``repositoryfolder-state-active``   | Active  |
+-------------------------------------+---------+

Initial state: ``repositoryfolder-state-active``

JSON Schema: :ref:`repofolders.schema.json <repofolders_schema_json>`

Dossiers
~~~~~~~~
| 

+------------------------------+------------------+
| ``dossier-state-active``     | Active           |
+------------------------------+------------------+
| ``dossier-state-resolved``   | Resolved         |
+------------------------------+------------------+

Initial state: ``dossier-state-active``

Therefore, to deliver a dossier in the completed state, the
``review_state`` is set to the appropriate value:

  ...

  "``review_state``: ``dossier-state-resolved``,

  ...

When a dossier is delivered in the resolved state, each contained subdossier MUST also have the status ``dossier-state-resolved``. Fulfilment of the rules on ``loose sheets`` and date ranges, on the other hand, is recommended but not strictly required for import (will be logged but imported ``as-is``).

JSON Schema: :ref:`dossiers.schema.json <dossiers_schema_json>`

Documents
~~~~~~~~~
| 

+----------------------------+----------------------+
| ``document-state-draft``   | (default state)      |
+----------------------------+----------------------+

Inital state: ``document-state-draft``

JSON Schema: :ref:`documents.schema.json <documents_schema_json>`


Creator
-------

The creator of an object can be set for all contents with the property ``_creator``. The corresponding journal entries are also recorded in the name of the creator of the respective object.


Redirects to previous URL paths
-------------------------------
In order to ensure that old links to the original path of a document or dossier still work, the original paths can be specified under the key ``_old_paths``. This way, the old URLs lead to the newly created object with a redirect.


Additional validation
---------------------

Schema
~~~~~~

- The GUID of each imported object must be unique.

- The reference number of a dossier/document must be unique, also the position number of an item.

- Date and DateTime fields must be formatted according to `RFC 3339 <http://www.ietf.org/rfc/rfc3339.txt>`__.

.. _business_rules:

Business Rules
~~~~~~~~~~~~~~~

The following business rules apply in OneGov GEVER:

- The configuration variable **maximum\_repository\_depth** and **maximum\_dossier\_depth** define how deep folder items and dossiers may be nested within each other.

- Closed dossiers:

   - Closed dossiers may not contain open subdossiers.

   - If a dossier is closed and has subdossiers, all documents must be assigned to a subdossier, the main dossier must not contain any documents directly assigned to it ("no loose sheets").

   - The end date of a resolved dossier must always be greater than or equal to the end date of all its subdossiers, and greater than or equal to the document date of a contained document.

- A repositoryfolder can only contain either dossiers or further repositoryfolders, never objects of both content types at the same time. Accordingly, dossiers may only be contained in leaf nodes of the repository.

- For the following fields, the choice is restricted by the parent:

   - ``custody_period``

   - ``archival_value``

   - ``classification``

   - ``privacy_layer``

   - ``retention_period`` - *Depending on the configuration, this rule may not be active*.

   Restricting in this context means that the list of available
   available elements according to the JSON schema definition to the element
   selected by the parent and all subsequent elements is reduced.

Reference and sequence numbers
------------------------------

In OneGov GEVER, reference numbers are kept and displayed on the dossier and document levels. The display format of the reference number (grouping, separator) is configurable per client and the individual components are stored separately, independent of the formatted string.

| An example of the reference number of a document in GEVER looks as follows:
| **FD 0.7.1.1 / 5.3 / 54**

The individual components here stand for the following:

- **FD** - an abbreviation that can be configured per client and is used in the reference number.

- **0.7.1.1** - the number of the repositoryfolder. Composed of the individual components (**0**, **7**, **1**, and **1**) which are managed / stored locally on the corresponding repositoryfolders. Separated by a configurable separator (point by default).

- **5** - the number of the dossier within the leaf repositoryfolder (ascending counter per heading).

- **3** - the number of a subdossier within the dossier, if subdossiers exist.

- **54** - the globally unique sequence number of the document (also unique without the rest of the reference number).

The reference numbers for dossiers/subdossiers leave out the last part
(sequence number of the document).

Delimitations
-------------

- For the time being, only the mentioned content types can be imported, not all types available in OneGov GEVER.

- Document versions cannot be imported.

- Mails cannot be converted losslessly from *\*.msg* to *\*.eml* during automatic import, so they must first be converted to \*.eml.

- It cannot be checked whether the rights are set "sensibly" (optimal use of the inheritance mechanism, no redundancies). Any simplification of the permissions must be carried out before importing the data into OneGov GEVER.

.. |img-image-1| image:: img/image1.png

.. _chapter-oggbundle-appendix:

Appendix
--------

Schemas
~~~~~~~


The JSON schemas that define the structure of the JSON files for the metadata are stored here:

.. _configuration_schema_json:

:download:`configuration.schema.json <data/configuration.schema.json>`

.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: data/configuration.schema.json
       :language: json

----------

.. _documents_schema_json:

:download:`documents.schema.json <../../../../opengever/bundle/schemas/documents.schema.json>`

.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/documents.schema.json
       :language: json

----------

.. _dossiers_schema_json:

:download:`dossiers.schema.json <../../../../opengever/bundle/schemas/dossiers.schema.json>`

.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/dossiers.schema.json
       :language: json

----------

.. _repofolders_schema_json:

:download:`repofolders.schema.json <../../../../opengever/bundle/schemas/repofolders.schema.json>`

.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/repofolders.schema.json
       :language: json

----------

.. _reporoots_schema_json:

:download:`reporoots.schema.json <../../../../opengever/bundle/schemas/reporoots.schema.json>`


.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/reporoots.schema.json
       :language: json

----------

.. _workspaceroots_schema_json:

:download:`workspaceroots.schema.json <../../../../opengever/bundle/schemas/workspaceroots.schema.json>`


.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/workspaceroots.schema.json
       :language: json

----------

.. _workspaces_schema_json:

:download:`workspaces.schema.json <../../../../opengever/bundle/schemas/workspaces.schema.json>`


.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/workspaces.schema.json
       :language: json

----------

.. _workspacefolders_schema_json:

:download:`workspacefolders.schema.json <../../../../opengever/bundle/schemas/workspacefolders.schema.json>`


.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/workspacefolders.schema.json
       :language: json

----------

.. _ogds_users_schema_json:

:download:`ogds_users.schema.json <../../../../opengever/bundle/schemas/ogds_users.schema.json>`


.. container:: collapsible

    .. container:: header

       Schema anzeigen

    .. literalinclude:: ../../../../opengever/bundle/schemas/ogds_users.schema.json
       :language: json


==================
Generate OGGBundle
==================

With ``bin/create-bundle`` a ``OGGBundle`` can be generated from a data directory or an Excel file containing a classification system.

The following applies to creating a bundle from a filesystem:

- If ``--repo-nesting-depth`` is set, the script will generate a ``OGGBundle`` for a complete ``repository``. In this case, the ``source_dir`` in the ``OGGBundle`` is mapped as a ``reporoot``, and all directories that have a nesting depth less than ``--repo-nesting-depth`` are mapped as ``repofolders``. Other directories as ``dossiers`` and files as ``documents``.

- If ``--repo-nesting-depth`` is not set (``--repo-nesting-depth=-1``), then the script generates a ``OGGBundle`` for a partial import. In this case the ``source_dir`` is not mapped in the ``OGGBundle``, all contained directories are mapped as ``dossiers`` and files as ``documents``. The folder location or dossier into which the ``OGGBundle`` is to be imported must be specified with ``--import-repository-references`` and optionally ``--import-dossier-reference``.

Only certain arguments are allowed for creating a bundle from Excel. In addition, dossiers and documents cannot be created,
as the Excel only contains the repository.

With ``bin/create-bundle --help`` a complete list of possible arguments can be displayed.

Metadata
---------

The creation date of a file is used as ``document_date`` in the corresponding OGG object and the modification date of the file is used as the modification date.
