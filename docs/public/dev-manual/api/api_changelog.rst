.. _api-changelog:

API Changelog
=============

2022.21.0 (unreleased)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

Other Changes
^^^^^^^^^^^^^


2022.19.0 (2022-09-28)
----------------------

Other Changes
^^^^^^^^^^^^^
- ``@participation``: Sort dossier participations by ``participant_title``.
- Include title in private folder serialization.
- Current participants are now filtered out in ``@possible-participations`` endpoint.

2022.18.0 (2022-09-13)
----------------------

Other Changes
^^^^^^^^^^^^^
- ``@linked-workspace-invitations``: New endpoint to invite users from GEVER into a workspace.

2022.17.0 (2022-08-30)
----------------------

No api changes in this release

2022.16.0 (2022-08-17)
----------------------

Other Changes
^^^^^^^^^^^^^

- ``@ogds-user-listing``: Add ``job_title`` field.

2022.15.0 (2022-08-03)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^

Other Changes
^^^^^^^^^^^^^
- ``@unlink-workspace``: Add field ``deactivate_workspace``. (see :ref:`unlink-workspace`)
- ``@document-from-template`` now also supports a ``sender`` parameter when KuB is active.

2022.14.0 (2022-07-20)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@journal``: Rename `comments` attribute for GET @journal entries to `comment` which is the expected naming in the POST request

Other Changes
^^^^^^^^^^^^^
- ``@journal``: Returns a new attribute ``category`` for journal-entries.
- ``@journal``: Returns a new attribute ``is_editable`` for journal-entries.
- ``@journal``: Provides PATCH for manual journal entries (only available for new manual journal entries).
- ``@journal``: Provides removing of manual journal entries with DELETE method (only available for new manual journal entries).
- ``@journal``: Returns the ``@id`` and ``id`` of a journal-entry.
- ``@journal``: Properly deserializes category values provided by the vocabulary. We can now send category with ``{ 'token': 'information' }``.
- ``@journal``: POST and PATCH support setting the ``time`` field.

2022.13.0 (2022-07-07)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@solrsearch``: The Solr query parser has been switched from Lucene to eDisMax. The ``q`` and ``q.raw`` parameters now behave identically and both expect a query in eDisMax syntax.

Other Changes
^^^^^^^^^^^^^
- ``@journal``: Provides filtering and searching.
- ``@participations``: Add field ``primary_participation_roles``. (see :ref:`dossier-participations`)
- ``@participations``: Improve error messages for DELETE endpoint.
- Include additional_ui_attributes in KuB entity serialization.
- ``@actors``: Also handle groupids with group prefix.

2022.12.0 (2022-06-21)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@responses``: Responses can no longer be edited if they are not of type comment.
- ``@actual-workspace-members`` endpoint is replaced by the ``@workspace-content-members``. (see :ref:`docs <workspace_content_members>`)

Other Changes
^^^^^^^^^^^^^
- ``@responses``: Add DELETE endpoint.
- ``@responses``: Set modifier and modified in PATCH endpoint.
- ``@ogds-user-listing`` now supports filtering by group membership.
- ``@share-content``: Add `notify_all` param to share content with all authorized participants.
- A new endpoint ``@attendees-presence-states`` is added (see :ref:`docs <attendees_presence_states>`).

2022.11.0 (2022-05-24)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@config`` endpoint does not return ``usersnap_api_key`` anymore.

Other Changes
^^^^^^^^^^^^^
- A new ``@ogds-sync`` endpoint allows to start an OGDS synchronisation.

2022.10.0 (2022-05-11)
----------------------

Other Changes
^^^^^^^^^^^^^
- A new endpoint ``@ui-actions`` is added (see :ref:`ui_actions`).

2022.9.0 (2022-04-26)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@tasktree``: Endpoint does no longer return the ``is_task_addable_in_main_task`` but provides a ``is_task_addable`` and ``is_task_addable_before`` attribute for each item.
- No longer allow to change task responsible via PATCH request.

Other Changes
^^^^^^^^^^^^^
- ``@tus-upload``: Only clean up file system data after successful commit.
- ``@tus-upload``: Allow uploading a file if the document has no file yet.

2022.8.0 (2022-04-12)
---------------------

Other Changes
^^^^^^^^^^^^^
- ``@copy-document-from-workspace``: Error responses now include ``translated_message``.
- Add new endpoint ``@task-template-structure``.
- Add new endpoint ``@process`` (see :ref:`process`).

2022.7.0 (2022-03-29)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@kub``: A 404 error is returned if a contact cannot be resolved.

Other Changes
^^^^^^^^^^^^^
- ``@external-activities``: ``notification_recipients`` now also accepts group IDs.
- ``@external-activities``: Privileged users may now create notifications for other users (see :ref:`external-activities`)
- ``@config``: Add ``workspace_creation_restricted`` feature flag.

2022.6.0 (2022-03-15)
---------------------

Other Changes
^^^^^^^^^^^^^
- ``@navigation``: Return translated title in node ``text``.
- ``@role-assignment-reports``: Handle group prefix in principalid.
- ``@config``: Add ``dossier_checklist`` feature flag.
- ``@participations`` endpoint now also support adding a list of participants. (see :ref:`participation`)
- Add new endpoint ``@linked-workspace-participations``. (see :ref:`linked-workspaces`)
- ``@dashboard-settings``: Add new endpoint to fetch the current dashboard settings.

2022.5.0 (2022-03-01)
---------------------

Other Changes
^^^^^^^^^^^^^
- ``@white-labeling-settings``: Add field ``dossier_type_colors``. (see :ref:`white-labeling-settings`)
- ``@navigation``: Include dossier_type in response.
- ``@breadcrumbs`` GET: Include dossier_type in response.
- Serialization: Include dossier_type in JSON summary for dossiers.
- ``@favorites`` GET: Include dossier_type in response.
- Add new endpoint ``@remove-dossier-reference``
- ``@unlink-workspace``: Allow unlinking workspaces even if the dossier is closed.
- ``@reference-number``: Add new endpoint and expansion parameter to serialize reference number formatted, sortable and raw.


2022.4.0 (2022-02-16)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- Dossiers: The ``comments`` field has been dropped, and dossiers now support multiple comments via ``responses``.

Other Changes
^^^^^^^^^^^^^
- ``@globalsources``: The ``all_users_and_groups`` source returns now also inactive users.


2022.3.0 (2022-02-02)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@solrsearch:``: Change ``path_parent`` filter query to no longer expect physical paths but relative paths instead.

Other Changes
^^^^^^^^^^^^^
- ``@solrsearch``: The results can now be filtered by ``@id_parent`` or ``url_parent``.
- ``@actors``: Add ``full_representation`` parameter. (see :ref:`docs <actors>`)


2022.2.0 (2022-01-19)
---------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- ``@propertysheets``: Change error serialization format for PATCH and POST (to be more frontend-friendly).
- ``@propertysheets/<sheet_id>``: GET and POST responses now return the same JSON format as accepted by POST as input, not the JSON schemas anymore. The JSON schemas can now be retrieved from the ``@schema`` endpoint (see change below).


Other Changes
^^^^^^^^^^^^^
- ``@propertysheets``: Add PATCH support.
- ``@propertysheets``: Add ``id`` and ``@type`` to sheet listing.
- ``@schema``: JSON Schemas for propertysheets can now be retrieved with ``GET /@schema/virtual.propertysheet.<sheet_id>``
- ``@propertysheet-metaschema``: New endpoint to retrieve schema for propertysheet definitions.


2022.1.0 (2022-01-04)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- Workspace serialization does no longer return the key `responsible_fullname`.
- Support recipient in ``@document-from-template`` endpoint when KuB feature is enabled.
- Contact feature in the ``@config`` endpoint is now one of ``plone``, ``sql`` and ``kub``.

Other Changes
^^^^^^^^^^^^^
- ``@config``: added new property ``multiple_dossier_types`` which will be set to true if there is more than one dossier type available.
- ``@solrsearch`` and ``@listing``: ``dossier_type`` is added as a new solr index and whitelisted in the ``@listing`` endpoint.
- Propertysheets: ``date`` fields are now supported.
- ``@listing-custom-fields`` endpoint contains now also the widget information.
- ``@solrsearch``: The results can now be filtered by its ``@id``.
- ``@solrsearch``: Allow POST requests against the endpoint. This allows us to get around the length-limit of GET requests.
- ``@config``: Add ``is_propertysheets_manager`` key to indicate whether user is allowed to manage property sheets.
- ``@propertysheets``: Management of property sheets is now also allowed for ``PropertySheetsManager`` role.
- ``@solrsearch``: Now supports facetting custom property fields.
- Add new endpoint ``@external-activities`` (see :ref:`docs <external-activities>`)
- Include sip_delivery_status in the disposition serialization.
- Disposition serialization contains now responses.
- ``@xhr-upload``: new endpoint to upload documents as a multipart/form-data xhr request.
- Include is_completed in sql task serialization.
- ``@listing``: Add retention_expiration column.
- New endpoints ``@my-substitutes`` and ``@substitutes`` are added (see :ref:`substitutes`).
- A new endpoint ``@out-of-office`` is added (see :ref:`out-of-office`).
- Include is_absent in actors serialization.
- A new endpoint ``@substitutions`` is added (see :ref:`get-substitutions`).
- Include email address in workspace and workspace folder serialization.
- ``@listing``: Add document_type_label column.
- ``@listing``: Add dossier_type_label column.

2021.24.0 (2021-11-30)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- @complete-successor-task: ``documents`` payload: Now requires relative paths to the siteroot instead physical paths. The physical path is for internal use only.
- Error message and response status code for ForbiddenByQuota errors have changed.

Other Changes
^^^^^^^^^^^^^
- @complete-successor-task: ``documents`` payload: now also resolves document references by @id.
- @reminders now returns 204 NoContent when no reminder is set.
- Added API support for dispositions objects.
- Added ``@kub`` endpoint to resolve KuB entities by their ID.

2021.23.0 (2021-11-17)
----------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- Some error messages have been renamed, but the format how an error is returned stays the same, only the response now usually contains a translated error message and may contain additional metadata.
- Toggling a Workspace Todos review state from active to completed and back can be done thorugh the newly introduced `@toggle` endpiont for todos.
- Workspace Todos do no longer provide a completed-field. Completing a todo is now done through a workflow transition.
- The ``completed`` field in the ``@listing`` is now longer supported, use the ``is_completed`` field instead.

Other Changes
^^^^^^^^^^^^^
- ``@listing``: Add ``todo_lists`` and ``dispositions`` listing (see :ref:`docs <listing-names>`)
- Tasks provides an additional attribute ``is_completed``.
- Patch request now returns translated values and error messages.


2021.22.0 (2021-11-03)
----------------------

Other Changes
^^^^^^^^^^^^^
- Add additional PATCH endpoint ``public-trial-status``.
- ``@workflow``: Sequential task transitions now accepts ``pass_documents_to_next_task`` transition parameter.


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
