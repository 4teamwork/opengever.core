.. _api-changelog:

API Changelog
=============

2021.7.0 (unreleased)
---------------------

Other Changes
^^^^^^^^^^^^^

- Task serialization now also returns is_remote_task.
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
