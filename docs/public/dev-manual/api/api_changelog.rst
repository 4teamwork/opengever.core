.. _api-changelog:

API Changelog
=============

2021.22.0 (unreleased)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

Other Changes
^^^^^^^^^^^^^


2021.21.0 (2021-10-20)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- task-transition-delegate now expects UIDs for the documents parameter.

Other Changes
^^^^^^^^^^^^^
- ``@webactions``: Support activation and deactivation of context webactions (see :ref:`docs <webactions>`).


2021.20.0 (2021-10-06)
----------------------

Other Changes
^^^^^^^^^^^^^
- Add new endpoint ``@accessible-workspaces`` (see :ref:`docs <accessible-workspaces>`)

2021.19.0 (2021-09-21)
----------------------

Other Changes
^^^^^^^^^^^^^
- ``@propertysheets``: Add ``allow_unmapped`` to ``default_from_member`` options.


2021.18.0 (2021-09-10)
----------------------

Other Changes
^^^^^^^^^^^^^

- ``@propertysheets``: Add support for defaults from Member properties
- ``@propertysheets``: Add support for default TALES expressions
- ``@propertysheets``: Add support for default factories
- ``@propertysheets``: Add support for static defaults
- Add new endpoint ``@reactivate-local-group`` (see :ref:`docs <reactivate-local-group>`)
- Propertysheets: ``multiple_choice`` fields are now supported.
- Prevent changing ``file`` of ``opengever.document.document`` to a non-docx file if it is inside an ``opengever.meeting.proposal``.
- Prevent setting ``file`` to ``null`` for ``opengever.document.document`` if it is inside an ``opengever.meeting.proposal``.
- Include checkout collaborators and file modification time in document serialization.
- Include checkout collaborators, file modification time, lock time and lock timeout in document status.
- ``@complete-successor-task``: Prevent transferring checked out documents when completing successor tasks.


2021.17.0 (2021-08-30)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- ``@share-content``: Rename attributes ``users_to`` and ``users_cc`` to ``actors_to`` and ``actors_cc``.

Other Changes
^^^^^^^^^^^^^

- ``@workflow``: Transition ``task-transition-in-progress-resolved`` now accepts ``approved_documents`` transition parameter.
- ``@share-content``: Support groups.
- ``actual-workspace-members``: Include group users and add ``include_groups`` parameter to include groups.
- ``@listing``: Add ``approval_state`` column
- Include ``committee`` in proposal serialization.
- Include ``proposal``, ``meeting``, ``submitted_proposal`` and ``submitted_with`` in document serialization.
- New ``@reference-numbers`` endpoint for administrators (see :ref:`docs <reference-numbers>`).
- Include ``@type``, ``active``, ``portrait_url``,  ``representatives`` and ``respresents`` in ``@actors`` endpoint.


2021.16.0 (2021-08-12)
----------------------

Other Changes
^^^^^^^^^^^^^

- Allow deleting repository folders over the REST-API.


2021.15.0 (2021-07-30)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- ``@teams`` and ``@team-listing``: Moved to plone site root.
- ``@teams``: Supports adding (POST) and updating (PATCH).
- ``@role-assignments``: Return a fixed list of roles at the key ``referenced_roles``.
- ``@trash``: Always return error message if content is not trashable.


Other Changes
^^^^^^^^^^^^^

- Add new endpoint ``@unlink-workspace`` (see :ref:`docs <linked-workspaces>`)
- Almost all content type serializers provide additional key ``sequence_number``.
- Add new endpoint ``@accept-remote-forwarding`` (see :ref:`docs <accept-remote-forwarding>`)
- ``@workflow``: Add ``transition_response`` if it exists.
- Fix ``@versions`` for documents that do not have an initial version yet (lazy initial version).


2021.14.0 (2021-07-16)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- ``@move``: Restrict moving of documents via API according to the same rules as in the classic UI.
- ``@listing``: Add ``sequence_type`` as allowed field (see :ref:`docs <listings>`).

Other Changes
^^^^^^^^^^^^^

- ``@config`` endpoint extended with current admin_unit information.
- ``@trigger-task-template``: Support overriding the deadline for each task (see :ref:`trigger_task_template` for updated examples).
- ``@navigation``: Add ``review_state`` and ``include_context`` parameters (see :ref:`docs <navigation>`)
- Added ``@submit-additional-documents`` endpoint. (see :ref:`docs <submit-additional-documents>`)


2021.13.0 (2021-06-25)
----------------------

Other Changes
^^^^^^^^^^^^^

- Return specific error messages when quota gets exceeded in the private repository.
- Add support for the ``stats`` component to the ``@solrsearch`` endpoint.
- ``@watchers``: The endpoint is now also available for documents. (see :ref:`docs <watchers>`)
- `@trash` and `@untrash` endpoints now also work for WorkspaceFolders.
- Trashed workspace documents and folders can be deleted. (see :ref:`docs <trash>`)
- Prevent changing the ``is_private`` field of existing tasks.


2021.11.0 (2021-05-28)
----------------------

Other Changes
^^^^^^^^^^^^^

- Add ``primary_repository`` information to the ``@config`` endpoint.
- ``@listing``: Fix filtering on values containing spaces.
- Dossier and document serialization provides now an additional attribute ``back_references_relatedDossiers`` and ``back_references_relatedItems``.
- ``@globalindex``: Include ``containing_subdossier``, ``review_state_label`` and ``sequence_number`` in task serialization. (see :ref:`docs <globalindex>`)
- ``@extract-attachments`` endpoint now also works for mails in a workspace.
- Update ``@upload-structure`` endpoint to also control for possible duplicates. (see :ref:`docs <upload-structure>`)
- ``linked-workspaces``: Add field ``workspaces_without_view_permission`` (see :ref:`docs <get-linked-workspaces>`)


2021.10.0 (2021-05-12)
----------------------

Other Changes
^^^^^^^^^^^^^

- The ``@participations`` endpoint now prevents removing the last ``WorkspaceAdmin`` from a workspace.
- Added ``@listing-custom-fields`` endpoint and allow retrieving custom properties in ``@listing``. (see :ref:`docs <listing-property_sheets>`)
- Added ``@upload-structure`` endpoint. (see :ref:`docs <upload-structure>`)


2021.9.0 (2021-04-29)
---------------------

Other Changes
^^^^^^^^^^^^^

- Task serialization now also returns is_remote_task and responsible_admin_unit_url.
- New ``@version`` that returns the historical versions of a document.


2021.8.0 (2021-04-15)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- Deserialization: Years before 1900 will now get rejected for date and datetime fields.


2021.7.0 (2021-04-01)
---------------------

Other Changes
^^^^^^^^^^^^^

- ``@workflow/task-transition-delegate``: Allow to set ``informed_principals``.
- ``@solrsearch``: Add ``group_by_type`` parameter (see :ref:`group-by-type`)
- ``@listing``: Add ``repository_folders`` and ``template_folders`` listing (see :ref:`docs <listing-names>`)
- ``@listing`` endpoint whitelists the ``id`` field.
- The endpoint ``@trigger-task-template`` supports overriding ``title`` and ``text`` for each task (see :ref:`trigger_task_template` for updated examples).


2021.6.0 (2021-03-18)
---------------------

Other Changes
^^^^^^^^^^^^^

- Add ``containing_subdossier_url`` to the document serializer.


2021.5.0 (2021-03-04)
---------------------

Other Changes
^^^^^^^^^^^^^

- Add new endpoint ``@oneoffixx-templates`` to provide oneoffixx templates over the restapi
- Add new endpoint ``@document_from_oneoffixx`` to add a document from a oneoffixx template
- Add ``breadcrumbs`` option to the ``@solrsearch`` endpoint, only available for small batch sizes (max. 50 items).

Breaking Changes
^^^^^^^^^^^^^^^^

- The ``@sharing`` endpoint now returns a batched result set if using the ``search`` param. If using the endpoint with the ``search`` param, it will rename the items key from ``entries`` to the key ``items`` which is the expected key for items in a batched response.


2021.4.1 (2021-02-25)
---------------------

Other Changes
^^^^^^^^^^^^^

- Add ``creator`` to the document serializer.


2021.4.0 (2021-02-18)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- Rename the attribute ``is_admin_menu_visible`` from the ``@config`` endpoint to ``is_admin``.
- (De-)serialization of choice fields for ``custom_properties`` has been changed to support a nested object containing token and title for each term (see :ref:`propertysheets` for updated examples).


Other Changes
^^^^^^^^^^^^^

- Add ``is_inbox_user`` attribute to the ``@config`` endpoint.
- A new endpoint ``@save-document-as-pdf`` is added (see :ref:`save-document-as-pdf`).


2021.3.0 (2021-02-03)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- tasktemplates: interactive users for the ``issuer`` and ``responsible`` are now stored in the actors format: ``interactive_actor:current_user`` / ``interactive_actor:responsible`` and can now be looked up through the ``@actors`` endpoint.
- tasktemplates: The ``responsible_client`` field will no longer be used to identify interactive users for the responsible field. It will be ``None`` for interactive users. The ``responsible_field`` will contain all the necessary information to identify an interactive actor.
- ``@create-linked-workspace``, ``@link-to-workspace``: Only available if dossier is open.
- ``@notifications``: Only badge notifications are returned (see :ref:`docs <notifications>`).
- ``@tasktree``: Sequential tasks are now sorted on ``getObjPositionInParent`` (see :ref:`docs <tasktree>`).


Other Changes
^^^^^^^^^^^^^

- The field ``blocked_local_roles`` is now included in the serialization of documents and repository folders.
- ``@listing``: Add ``blocked_local_roles`` as allowed field (see :ref:`docs <listings>`).
- Add support for english: new field ``title_en`` is returned wherever appropriate (``@schema``, ``@types`` and simple GET for diverse content types) when English is enabled for the deployment.
- ``@journal``: Include ``related_documents`` in journal entry serialization (see :ref:`docs <journal>`).
- The fields ``checked_out`` and ``file_extension`` are now included in the summary serialization of documents and mails.
- The field ``custom_properties`` is now included in the ``@schema`` endpoint for Documents and Mails (see :ref:`content-types`).
- ``@tasktree``: Attributes ``is_task_addable_in_main_task`` and ``is_task_addable_before`` added (see :ref:`docs <tasktree>`).
- ``@notifications``: request method POST is added to mark all notifications as read (see :ref:`docs <mark-notifications-as-read>`).


2021.2.0 (2021-01-20)
---------------------

Other Changes
^^^^^^^^^^^^^

- A new endpoint ``@white-labeling-settings`` is added (see :ref:`white-labeling-settings`).
- ``@config``: New feature flag ``hubspot`` added (see :ref:`config`).
- Documents and Mails now support serialization and deserialization of ``custom_properties`` (see :ref:`propertysheets`).
- A new endpoint ``@propertysheets`` is added (see :ref:`propertysheets`).


2021.1.0 (2021-01-06)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- ``@schema``, ``@types``: Only return ``title_de`` / ``title_fr`` fields if corresponding language is enabled in deployment (see :ref:`translated-titles`).

- Serialization: Only serialize values for ``title_de`` / ``title_fr`` fields if corresponding language is enabled in deployment (see :ref:`translated-titles`; applies to Dossiers, Repositoryfolders, and Inboxes).
