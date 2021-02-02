.. _api-changelog:

API Changelog
=============


2021.3.0 (unreleased)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^

- tasktemplates: interactive users for the `issuer` and `responsible` are now stored in the actors format: `interactive_actor:current_user` / `interactive_actor:responsible` and can now be looked up through the `@actors` endpoint.
- tasktemplates: The `responsible_client` field will no longer be used to identify interactive users for the responsible field. It will be `None` for interactive users. The `resopnsible_field` will contain all the necessary information to identify an interactive actor.
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

.. disqus::
