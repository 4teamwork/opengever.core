Changelog
=========

Versions are of the form MAJOR.MINOR.PATCH. Each MINOR release (MAJOR.MINOR.0) includes changes from all previous MINOR releases. Changes in PATCH releases (PATCH version > 0) are backports and are not included in following MINOR and MAJOR releases. Such entries will therefore usually appear more than once in the changelog. Note that this convention is only held starting on 2021-08-06.

.. You should *NOT* be adding new change log entries to this file.
   Create a file in the changes directory instead. Use the issue/ticket number
   as filename and add one of .feature, .bugfix, .other as extension to signify
   the change type (e.g. 6968.feature).

.. towncrier release notes start

2024.15.1 (2024-10-22)
----------------------

New features:


- Implement new teamraum document state: opengever_workspace_document--STATUS--final. [ran] [TI-21]


Bug fixes:


- Fix logging when installing upgrades with upgrade command. [buchi] [GH-8056]
- Bump ftw.solr to version 2.13.3 which fixes issues running the solr zopectl command in Docker deployments. [buchi] [GH-8063]
- Bump ftw.catalogdoctor to version 1.2.1 which fixes issues running the zopectl command in Docker deployments. [buchi] [GH-8064]
- Allow downloading checked-out documents with no modifications and only an initial version. [buchi] [TI-675]
- Fix login for newly registered teamraum users when using OGDS authentication. [buchi] [TI-932]
- Bump ftw.pdfgenerator to version 1.6.11 which fixes 'no line to end' errors with table environments. [buchi] [TI-1119]
- Fix creating nested parallel task template containing a sequential template. [elioschmutz] [TI-1300]


Other changes:


- Allow configuring the mail host through environment variables. [buchi] [GH-7921]
- Run cron jobs in Docker deployments within a time window to avoid high load peaks on servers with multiple deployments. [buchi] [GH-8058]
- Bump Solr to version 8.11.4. [buchi] [GH-8065]
- Allow to submit no dossiers within a disposition. [elioschmutz] [TI-942]
- Add "Dossier ID" to solr fields. [ran] [TI-1103]
- Add support for setting local roles by groupname in additon to group ids when importing repositories from Excel. [buchi] [TI-1116]
- Remove the linked workspace from the target dossier when copying. [amo] [TI-1263]


2024.15.0 (2024-10-22)
----------------------

- Brown bag release


2024.14.0 (2024-09-24)
----------------------

New features:


- Add configuration option to filter possible group watchers. [elioschmutz] [TI-1222]
- Implements the document sign process. [elioschmutz] [TI-659]


Bug fixes:


- Fix unicode error when syncing users. [elioschmutz] [TI-1024]
- Make determining Solr facet labels more robust. [lgraf] [TI-1210]
- Fixes a bug where it was no longer possible to add watchers in teamraum. [elioschmutz] [TI-1221]


Other changes:


- Exclude inactive (users / group users) from teamraum participation excel export. [amo] [TI-1086]
- Make assignment reports available for teamraum [TI-115](https://4teamwork.atlassian.net/browse/TI-115) [TI-115]
- Extends document workflow with basic sign states and transitions. [elioschmutz] [TI-659]
- Add option to regenerate bundle schemas on bundle import [TI-948](https://4teamwork.atlassian.net/browse/TI-948) [TI-948]


2024.13.0 (2024-09-09)
----------------------

New features:


- Add 'dossier_review_state' solr index which provides the review state of the current dossier or the closest parent dossier. [elioschmutz] [TI-479]


Bug fixes:


- Persist content stats log file in Docker deployments. [buchi] [GH-8029]
- Bump ftw.contentstats to version 1.4.1 which fixes arg parsing in console command. [buchi] [GH-8033]
- Fix copying documents when deployed with Docker. [buchi] [TI-1009]
- Make System Messages available in Teamraum. [ran] [TI-1046]
- Fixes bug that throws error when documents with special characters in their name are downloaded. [pre] [TI-953]
- Fix an issue where changing remote task state was not possible if the remote task have had a deleted comment. [elioschmutz] [TI-992]


Other changes:


- Disable colorization if env variable has an empty value. [buchi] [GH-8025]
- Disable Z2 access log in Docker deployments. [buchi] [GH-8030]
- Resolve invitation error when user dose not exists any more. [amo] [TI-1036]
- Grant view permissions to users informed_principals on task, dossier and related documents. [amo] [TI-114]
- Adjust table columns widths to allow enough space for dates. Slightly decrease "Asigned person" column to increase date columns. [ran] [TI-309]
- Add sign feature flag. [elioschmutz] [TI-658]
- Enhance person docprops with nationality field. [amo] [TI-691-1]
- Add new document property 'ogg.document.classification' to store the information in office documents. [pre] [TI-892]
- Include user stats as a new content stats provider. [elioschmutz] [TI-911]
- Add the todos related to the agenda items to the pdf export [pre] [TI-917]


2024.12.0 (2024-08-23)
----------------------

Bug fixes:


- Fix setting CAS server URL on setup. [lgraf] [OPS-97]
- Fix handling of single special chars in search queries. [buchi] [TI-336]


Other changes:


- Fix cancellation of nested tasks by making them recursive. [ran] [TI-546]
- Add office connector check feature flag. [amo] [TI-571]
- Provide workspace participation export action on workspace folders. [amo] [TI-672]
- Enhance the IKUBSettings interface by adding new fields that allow the integration of customFields into the Docprops. [amo] [TI-691]
- Provide new field `guests` on IWorkspaceMeetingSchema. [amo] [TI-918]
- Improve workspace users vocabulary to properly handle no longer available users for restricted workspaces [amo] [TI-922]


2024.11.0 (2024-07-30)
----------------------

Bug fixes:


- Fix Redis requirement for Docker image. [buchi] [GH-7995]
- Fix migration.log handler which was broken in releae 2024.6.0. [buchi] [GH-8003]
- Modify Tabbed (proposals_tab) logic to show / hide based on alt and new SPV.[amo] [TI-777]


Other changes:


- Bump ftw.casauth to version 1.7.1 which allows using an internal CAS server url for ticket validation and configuration through env variables. [buchi] [GH-8002]
- Exclude inactive users and groups for non-managers in Sharing tab. [amo] [TI-296]
- Fix french translation for limiting dossier depth. [ran]
  (https://4teamwork.atlassian.net/browse/TI-596) [TI-596]
- Expose the serialized source dossier if possible when using the "@dossier-transfer" endpoint. [elioschmutz] [TI-706]
- Create journal entry in the target dossier after dossier transfer. [amo] [TI-709]
- Create journal entry in the source dossier after dossier transfer. [amo] [TI-710]


2024.10.0 (2024-07-15)
----------------------

New features:


- Add @error-log endpoint to get the most recent backend errors (feature-flagged). [elioschmutz] [TI-330]
- Groups and teams can be added and removed as watchers [elioschmutz] [TI-407]
- The @possible-watchers endpoint always includes all possible watchers without removing already watching actors [elioschmutz] [TI-407-2]
- Add support for participations in dossier creation api requests. [phgross] [TI-438]


Bug fixes:


- Respect new file mimetype when retrieve a file from teamraum as a new version. [elioschmutz] [TI-366]
- A user can now add itself as a regular watcher even if he is already watching by anoter watcher role [elioschmutz] [TI-407]
- Fix document_date when uploading mails with DnD, use mail header date. [amo] [TI-458]
- Deactivate the edit ui-action for ris proposals. [jch] [TI-472]
- Introduce sequence number in the SIP name. [phgross] [TI-528]


Other changes:


- Introduce redis. [elioschmutz] [TI-330]
- Add new Field responsible to Disposition.[amo] [TI-362]
- The "POST @watcher" endpoint requires an "actor_id" an no longer a "userid" [elioschmutz] [TI-407]
- Remove deprecated 'referenced_users' property from 'GET @watcher' endpoint [elioschmutz] [TI-407-2]
- Introduce oneoffixx filetype selection. [phgross] [TI-569]
- Include group users in workspace participant Excel export and ensure unique user listing. [amo] [TI-669]
- Include workspace title in participant export file name. [amo] [TI-670]


2024.9.0 (2024-06-13)
---------------------

Bug fixes:


- Temporarily pass a dummy filename to oneoffixx, to support at least word templates. [phgross] [TI-456]
- Fix opening subtask in nested tasktemplates contiaining skipped tasks [elioschmutz] [TI-485]
- Properly start and close parent tasks within a nested task template structure. [elioschmutz] [TI-485-2]
- Provide ui-action to export workspace users by adding a new permission.[amo] [TI-506]


Other changes:


- Enhance Workspace member Vocabulary so we can get meeting users even if they removed from workspace. [amo] [TI-116]
- Improve solr performance, no longer using WordDelimiterGraphFilter on querying. [phgross] [TI-293]
- Handel invitation from inactive user [amo] [TI-328]
- Add support for linking workspaces by username/groupname. [buchi] [TI-399]
- Improve performance when searching for a responsible in tasks and forwardings. [elioschmutz] [TI-402]
- Add the IProposalLikeContent interface to list all old and new proposals. [jch] [TI-426]
- Add ris proposal context action to create tasks [jch] [TI-472]
- Add System messages permissions [amo] [TI-482]
- Superfluous link in invitation mail was removed [lorenzrychener] [TI-56]
- Replace the IP-based PAS plugin for authenticating requests from other admin units with a token-based one. [buchi] [TI-61]
- Changed French translation for canceling a dossier with open tasks[amo] [TI-85]
- Add feature-flag to disable the classic ui [elioschmutz] [TI-88]


2024.8.0 (2024-05-21)
---------------------

New features:


- Add full_content mode for GET /@dossier-transfers. [lgraf] [CA-6591]
- Provide User excel export for admin user [amo] [TI-13]
- Provide user Excel export for workspace participants [amo] [TI-156]
- Implement /@perform-dossier-transfer endpoint. [buchi] [TI-161]
- Disposition: Include stats about document count and cumulative file size. [lgraf] [TI-2]
- Add progress-index for dossiers with checklists. [elioschmutz] [TI-3]
- Remove oneoffixx template selection. [phgross] [TI-7]


Other changes:


- Provide additional information on user listing for admin users [amo] [TI-13]
- Enhance Repository Root Excel Export by adding folder UID and relative path [amo] [TI-131]
- Remove cropped title from task activities [amo] [TI-144]
- Add ris_proposals listing entry. [blu] [TI-152]
- Provide Docproperty information in system information template  [amo] [TI-317]
- Allow Manager to list or fetch any dossier transfer. [lgraf] [TI-5a]
- Add ris_base_url to config endpoint. [jch] [TI-71]
- Provide keywords on the new created Document from template [amo] [TI-89]


2024.7.0 (2024-04-23)
---------------------

New features:


- Add System Message SQL Model and Provide CRUD operation. [amo] [CA-1852]


Bug fixes:


- Fix OGDS listing date filters to also work on Oracle. [lgraf] [CA-6163]
- Fix lookup of user in WOPI operations if username and userid are not equal. [buchi] [CA-6237]
- Bump ftw.recipe.solr to version 1.3.9 which fixes remote streaming with Solr 8.11.3 [buchi] [GH-7922]
- Bump ftw.solr to version 2.13.2 which fixes argument parsing of the zopectl command when run with Docker. [buchi] [GH-7923]


Other changes:


- Disallow all download and share related actions for guests in restricted workspaces. [elioschmutz] [CA-6417]
- Do not render error page for BadRequest and Forbidden errors. [buchi] [CA-6417b]
- Add zopectl command for setting up a new deployment. [buchi] [CA-6863]
- Add zopectl command to run upgrade steps. [buchi] [CA-6863a]
- Bump ftw.contentstats to version 1.4.0 which adds support for Docker. [buchi] [GH-7024]


2024.6.0 (2024-03-22)
---------------------

New features:


- Adds the option in the workspace to restrict the possibility of printing and downloading content for guests. [KunzS85] [CA-6417]


Bug fixes:


- Fix argument parsing of create_service_user command. [buchi] [CA-6435a]
- Fix argument parsing of import command. [buchi] [CA-6435b]


Other changes:


- Change location of migration.log to log directory. [buchi] [CA-6435c]
- Make '/app/var/log' and '/app/var/instance' writeable inside Docker container. [buchi] [CA-6435d]
- Improve performance of Solr reindexing using data import handler for large indexes. [buchi] [CA-6790]


2024.5.0 (2024-03-07)
---------------------

New features:


- Add flag to the dossier serialization to know whether the dossier will be processed in the nightly jobs or not [KunzS85] [CA-5855]
- Add checkbox on repository folders to disable max subdossier depth restriction [elioschmutz] [CA-6447]
- Add new content-type opengever.ris.proposal. [deiferni] [HG-4265]


Bug fixes:


- Handle the setting of the pending jobs flag when a dossier is reopened [KunzS85] [CA-5855]
- Fix OGDS sync log in Docker container. [buchi] [CA-6435]
- Don't let rejected tasks prevent the dossier from being closed. [lgraf] [CA-6451]


Other changes:


- Use username in title of Users sources. [njohner] [CA-6237]
- Include responsible_actor in tasktree response. [amo] [CA-6280]
- Add Open Document types (.odt, .ods, .odp) to document types editable with OfficeConnector. [njohner] [CA-6292]
- Add support for ZCML package includes in Docker container. [buchi] [CA-6435]


2024.4.0 (2024-02-23)
---------------------

New features:


- Add 'external_reference' field to workspace todo [KunzS85] [CA-6482]
- Add `POST /@dossier-transfers` endpoint. [lgraf] [CA-6589]
- Add `GET /@dossier-transfers` endpoint. [lgraf] [CA-6590-1]
- Add `DELETE /@dossier-transfers/<id>` endpoint. [lgraf] [CA-6590-2]


Other changes:


- Add support for running cron jobs inside Docker container. [buchi] [CA-6435]
- Add support for permissions when creating bundle from Excel. [buchi] [CA-6436]
- Extension of the is_convertabe method for suppressing the conversion to PDF in case of missing file extension [KunzS85] [CA-6496]


2024.3.0 (2024-02-09)
---------------------

New features:


- Add new vocabulary: opengever.ogds.base.all_other_admin_units. [elioschmutz] [CA-6592]
- Add new vocabulary: opengever.ogds.base.all_admin_units. [elioschmutz] [CA-6592-2]
- Include getObjPositionInParent in serialization for documents/mails. [deiferni] [HG-4035-1]


Bug fixes:


- Fix mapping of names to principal ids in bundle import. [buchi] [CA-6435]
- Fix upgrade step that touches modified timestamp. [lgraf] [CA-6552]


Other changes:


- Use ogds-sync service for syncing users and groups. [buchi] [CA-6237a]
- Reporting view: Use filter query to filter by paths. [lgraf] [CA-6577]
- Update Docker image to Alpine 3.18 and include backports of security fixes for various dependencies. [buchi] [GH-7889]
- Bump versions of various dependencies to include latest security fixes. [buchi] [GH-7890]


2024.2.0 (2024-01-24)
---------------------

New features:


- Add related_todo_list field to workspace agenda items. [elioschmutz] [CA-6152]
- Make documents/mails in dossiers orderable by API clients. [deiferni] [HG-4035]


Bug fixes:


- Nested task templates: Also pass docs to subtasks that get started. [lgraf] [CA-6450]
- Also update modification date when updating changed timestamp. [lgraf] [CA-6552]
- Fix performance when checking if a workspace folder can be trashed. [buchi] [CA-6605]
- Fix search for participations with umlauts. [elioschmutz] [CA-6649]
- Fix Docker image: remove ZCML include of ftw.tika in Docker image. [buchi] [GH-7875]


2024.1.0 (2024-01-11)
---------------------

New features:


- Add new @globalsource ``all_contacts`` which returns active and inactive contacts. [elioschmutz] [CA-6490]


Bug fixes:


- Properly revoke temporary inbox permissions when working with forwardings. [elioschmutz] [CA-6354]
- Properly set predefined dossier template local roles on dossiers creating by templates. [elioschmutz] [CA-6493]
- Improve reporting view performance for path based queries. [phgross] [CA-6542]


Other changes:


- Include bumblebee_checksum in document status. [elioschmutz] [CA-5913]
- Support usernames and groupnames in the sharing API. [phgross] [CA-6237-6]
- Update KUB api from v1 to v2. [elioschmutz] [CA-6490]
- Bump ftw.mail to version 2.8.0. [buchi] [GH-7867]


2023.15.1 (2023-12-19)
----------------------

Bug fixes:


- Fix unicode error in disposition csv export. [phgross] [CA-6401]
- Fix service user id in keys for GEVER fixture. [deiferni] [HG-4272]


2023.15.0 (2023-12-13)
----------------------

New features:


- Extend dispositon SIP package with csv exports. [phgross] [CA-6302]


Bug fixes:


- Fix webactions provider for setups where the userid and user name are different. [phgross] [CA-6237]
- Add username fallback for @ogds-users endpoint and user-details view. [phgross] [CA-6237-4]
- Only skip enddate validation when it will be set over archive form. [njohner] [CA-6279]
- Properly set state of deeply nested task template folders. [elioschmutz] [CA-6355]
- Properly open deeply nested tasks. [elioschmutz] [CA-6355-2]
- Fix configuring Solr base URL in Docker container. [buchi] [CA-6418]
- Make max dossier depth restriction less strict. [phgross] [CA-6440]
- Fix Unicode error in `@accessible-workspaces` endpoint. [lgraf] [CA-6464]
- Fixes the sharing tab for subdossiers created by a dossier from template. [elioschmutz] [CA-6499]


Other changes:


- Base64 encode a literal occurence of EICAR Test-File. [lgraf] [CA-5703]
- Blacklist uploaded file formats based on extension instead of mimetype. [lgraf] [CA-5703-1]
- GeverSerializeToJsonSummary will always return the UID [elioschmutz] [CA-6151]
- The dossiers responsible field supports now also usernames not just userids. [phgross] [CA-6237]
- The ``@actors`` endpoint now returns an additional property ``login_name`` which should be used for display of usernames and groupnames. [buchi] [CA-6237-1]
- Task responsible and issuer field supports now also usernames not just userids. [phgross] [CA-6237-2]
- The ``@ogds-users`` and ``@ogds-groups`` endpoints now include `groupname` and `username` for groups and users. [buchi] [CA-6237-3]
- Massively speed up download of file version. [njohner] [CA-6272]
- Add option to skip generation of httpd.conf on startup of httpd container. [buchi] [CA-6418]


2023.14.0 (2023-11-09)
----------------------

New features:


- Add support for viewing documents with Office Connector. [buchi] [CA-5815]
- Add feature granting Role Manager role to dossiers responsibles. [njohner] [CA-6155]
- Archivists are granted view permissions on offered dossiers. [njohner] [CA-6167]
- Add transferring office field to dispositions to overwrite the AktenbildnerName. [njohner] [CA-6281]


Bug fixes:


- Fix ech-0147 import if using consecutive whitespaces in filenames. [elioschmutz] [CA-6194]
- Respect local dossier depth when uploading a dossier structure. [elioschmutz] [CA-6215]
- Fix dossier details for dossier with custom property with a list as value. [njohner] [CA-6217]
- Make sure docproperty values are written to the initial version when creating a document from template. [phgross] [CA-6253]
- Fix attaching documents from different parents to mails. [njohner] [CA-6262]
- Improve livesearch for terms getting split during analysis (hyphens, alphanumeric, etc.). [njohner] [CA-6339]


Other changes:


- Fix @@warmup view for Teamraum and PloneSites owned by anonymous. [njohner] [CA-5695]
- all_users_and_groups global source now also returns inactive groups. [njohner] [CA-6132]
- Use lenient dossier resolver by default for newly created policies. [njohner] [CA-6219]
- OGDS user and group labels display name instead of ID. [njohner] [CA-6237]
- Whitelist the location field for the @listing endpoint. [elioschmutz] [CA-6250]
- Add method marking unconverted documents as skipped in meeting Zip. [njohner] [CA-6285]


2023.13.0 (2023-09-21)
----------------------

New features:


- Add a response object for created, closed and reopened todos [elioschmutz] [CA-5099]
- Activate zip_export action for workspace folders. [elioschmutz] [CA-5554]
- Add new solr index `is_locked_by_copy_to_workspace` and provide it in all necessary api endpoints [elioschmutz] [CA-5563]
- Add is_current_user_responsible flag to task api serialization. [phgross] [CA-6021]
- Bundle import: Map principal names to ids in local roles. [lgraf] [CA-6039]


Bug fixes:


- Disposition: Fix UnicodeError in removal protocol download. [lgraf] [CA-6141]
- Include only dossiers with posotive appraisal in the SIP package. [phgross] [CA-6168]


2023.12.0 (2023-09-08)
----------------------

New features:


- Introduce header and footer configuration for meeting minutes. [phgross] [CA-1971]
- Add support for manual journal entries in OGG bundles. [njohner] [CA-5758]
- Add bundle import support for private roots. [lgraf] [CA-6039-2]
- Bundle content creation: Add support for setting 'id' of created objects. [lgraf] [CA-6039-3]
- Add bundle import support for templatefolders. [lgraf] [CA-6039-4]
- Add bundle import support for inboxes and inbox containers. [lgraf] [CA-6039-5]
- Policyless bundle import: Add support for creating initial content. [lgraf] [CA-6039-6]
- Getting @linked-workspaces on subdossier returns workspaces linked to main dossier. [njohner] [CA-6104]


Bug fixes:


- Fix title updating of sub repositoryfolder when prefix changes. [phgross] [CA-5949]
- Allow copying dossiers containing locked excerpt documents. [njohner] [CA-5991]
- Show lifecycle fields in schema display mode. [phgross] [CA-6037]
- Policyless deployments: Fix link to bundle import view. [lgraf] [CA-6039-1]
- Do not display create_disposition action on subdossier listings. [njohner] [CA-6061]
- Fix extraction of attachments from mails in closed tasks. [njohner] [CA-6128]
- Improve solr-indexing for words combined with underscores. [phgross] [CA-6136]


Other changes:


- Add gever-ui docker-compose file to policytemplates. [njohner] [CA-5602]
- Add endpoint to check if OC attach mail can be filed. [lgraf] [CA-5662]
- Read OGDS sync timestamp from OGDS instead of ZODB, as the new OGDS sync service only sets it in OGDS. [buchi] [CA-5766]
- Add disposition sequence number to SIP folder name. [njohner] [CA-5857]
- Enable GEVER UI registry feature by default. [lgraf] [CA-6039]
- Add extract_attachments context action for mails. [njohner] [CA-6128]


2023.11.0 (2023-06-29)
----------------------

New features:


- Allow to configure an upload mimetype blacklist. [elioschmutz] [CA-4999]
- @tus-upload can directly set a custom document_date. [elioschmutz] [CA-5001]
- Introduce new @system-information endpoint. [elioschmutz] [CA-5543]
- Expose "dossier_participation_roles" in the @system-information endpoint. [elioschmutz] [CA-5543-2]
- Expose "property_sheets" in the @system-information endpoint. [elioschmutz] [CA-5543-3]
- Hide copy, move and edit items actions for workspace guests on document listings. [njohner] [CA-5929]


Bug fixes:


- Fix member default gettter for propertysheet fields. [phgross] [CA-4911]
- Fix accepting task when dossier contains inactive subdossiers. [njohner] [CA-5897]
- Handle users without E-mail address in @share-content endpoint. [njohner] [CA-5912]
- Sort unread notifications first in @notifications endpoint. [njohner] [CA-5959]
- Adjust french translation in invitation mail title. [phgross] [CA-5963]


Other changes:


- Massively improve performance of @recently-touched endpoint. [njohner] [CA-5921]
- Avoid ever getting the searchableText from solr. [njohner] [CA-5921_2]
- Bump ftw.solr to version 2.13.1 to get fix of maintenance commands and warning for searches not specifying the fl parameter. [njohner] [CA-5921_3]
- Improve performance of @notifications endpoint. [njohner] [CA-5939]


2023.10.0 (2023-06-14)
----------------------

New features:


- Dossier templates can reference document templates. [elioschmutz] [CA-4519]
- Whitelist the related_items field for the @listing endpoint. [elioschmutz] [CA-4519-2]
- @listing-stats: Allow POST requests against the endpoint. [elioschmutz] [CA-4519-3]
- Index document and task related items in solr. [njohner] [CA-5463]
- Log removed manual journal entries for todos with a new journal entry. [elioschmutz] [CA-5578]


Bug fixes:


- Fix releasing unused reference numbers in the reference number manager. [elioschmutz] [CA-5692]
- Fix portrait removal for users with mail address as userid. [phgross] [CA-5831]
- Improve search behavior for english and french content. [phgross] [CA-5898]


Other changes:


- @listing-stats: No longer escapes querie-chars to allow complex queries . [elioschmutz] [CA-4519-3]
- Always pull latest docker images for testing. [njohner] [CA-5463]
- Improve logging of nightly maintenance jobs. [njohner] [CA-5702]


2023.9.0 (2023-05-30)
---------------------

Bug fixes:


- Fix ech0147 import if there are umlauts in the filenames. [elioschmutz] [CA-5673]
- Add/modify/delete manual journal entry will updated the touched-date. [elioschmutz] [CA-5735]
- Docker: add missing zcml include for ftw.slacker. [buchi] [CA-5766]
- Fix ech0160 when submitting disposition if there are umlauts in a repository title. [elioschmutz] [CA-5850]


Other changes:


- Speed-up upgrade steps reindexing workspace documents'workflow. [njohner] [CA-5556]
- Docker: patch z3c.autoinclude to improve container startup time. [buchi] [CA-5766]
- Implement IGroupIntrospection for OGDS auth plugin. [buchi] [CA-5766a]


2023.8.0 (2023-05-05)
---------------------

New features:


- Add workspace document urls in document serialization. [phgross] [CA-5562]


Bug fixes:


- Handle review_state missmatch between successor/predecessor pairs gracefully. [phgross] [CA-5363]
- Hide and skip inactive users in the @watchers endpoints. [phgross] [CA-5400]
- Support date custom fields in ech0160 export. [njohner] [CA-5697]


Other changes:


- Reindex maybe not properly indexed files. [elioschmutz] [CA-5726]


2023.7.0 (2023-04-19)
---------------------

New features:


- Add @validate-repository endpoint. [njohner] [CA-5609]


Other changes:


- @navigation endpoint excludes trashed items. [elioschmutz] [CA-5584]
- Register workspaces as a main_dossiers for the main-dossier expansion. [elioschmutz] [CA-5584-2]
- Speed up excel exports of repositories. [phgross] [CA-5643]


2023.6.2 (2023-04-13)
---------------------

Bug fixes:


- Change history order in the disposition removal protocol. [phgross]
- Fix docproperty collector for custom_properties with a list as value. [phgross]


2023.6.1 (2023-04-12)
---------------------

Bug fixes:


- Fix handling of trailing wildcard in query preprocessing. [njohner]
- Escape invalid characters in the sheet title of disposition exports. [phgross]


Other changes:


- Bump ftw.solr to Python 3 compatible version. [lgraf]


2023.6.0 (2023-04-10)
---------------------

New features:


- Add @solrlivesearch endpoint and improve solr configuration. [njohner]
- Use Bcc when sharing content in Teamraum with all participants. [njohner]
- Handle extra address lines in address block. [njohner]


Bug fixes:


- Handle long dossier and subdossier titles in task sync. [njohner]
- Bump ftw.mail to version 2.7.7 to improve attachment filename extraction. [njohner]
- Make sure to register @ogds-sync file logger only once. [njohner]
- Fix workspace invitation redirects for already accepted invitations. [phgross]
- Prevent document finalization if document is referenced by a pending approval task. [phgross]


Other changes:


- Cast datetime values to date objects for customproperty date fields. [elioschmutz]


2023.5.0 (2023-03-23)
---------------------

New features:


- Default task deadline calculation will ignore weekends. [elioschmutz]
- Add duplicate-strategies to the @globalindex endpoint. [elioschmutz]


Bug fixes:


- Fix various issues arising when the ContactFolder is missing. [njohner]
- Empty subdossiers can be deleted even if the main dossier is linked with a workspace. [elioschmutz]


Other changes:


- ogcore docker image: Send ftw.upgrade's stats log to /dev/null [lgraf]
- Refine the workspace-client to improve debugging. [elioschmutz]


2023.4.0 (2023-03-09)
---------------------

Bug fixes:


- Fix translating the title for pdfs created by the @save-minutes-as-pdf API endpoint. [elioschmutz]
- Fix @tasktree for users lacking view permission on main task. [njohner]
- Fix OGDS sync logging of modified group memberships. [njohner]


2023.3.0 (2023-02-22)
---------------------

New features:


- Allow to define a custom dossier resolution precondition. [njohner]
- Allow to define a custom dossier resolution after transition hook. [njohner]


Bug fixes:


- Fix ordering of subtasks in @tasktree endpoint for nested task processes. [njohner]
- Handle missing resources when deleting a workspace member. [njohner]
- Clean-up resources and subscriptions when an object is deleted. [njohner]
- Reindex the reference number of mails during move operations. [njohner]
- Show specific error page when invitations are no longer valid. [phgross]
- Handle broken references when generating the meeting minutes PDF. [njohner]
- Fix LDAP properties plugin upgrade step to work in deployments without LDAP. [lgraf]


Other changes:


- Harmonize naming of Excel export columns. [lgraf]
- Remove deprecated journal and task pdf marker interfaces. [njohner]


2023.2.0 (2023-02-09)
---------------------

New features:


- Add new @save-minutes-as-pdf API endpoint. [njohner]
- Include KuB person sex and date of birth in person docproperties. [tinagerber]
- Add participations docproperties when creating document from template. [tinagerber]
- Add touched date index for workspaces. [elioschmutz]


Bug fixes:


- Fix check to prevent anonymous users from viewing member portraits. [lgraf]
- Bump ftw.mail version to fix issue with cropped attachment filenames. [lgraf]


Other changes:


- Bump versions for ftw.bumblebee, ftw.casauth and ftw.usermigration. [lgraf]
- Policyless deployment works without the ldap plugin. [elioschmutz]
- Bump ftw.structlog to get support for logging to Fluentd. [lgraf]
- Provides a "WWW-Authenticate" response header for unauthorized requests to the @scan-in endpoint. [elioschmutz]


2023.1.0 (2023-01-11)
---------------------

New features:


- Allow to revive bumblebee preview for document versions. [tinagerber]
- Also list inherited roles in repository excel export. [njohner]
- Editors can delete empty dossiers in the active or inactive states [elioschmutz]
- Implement config check for the ldap authentication plugin order [elioschmutz]
- Add a new endpoint: @config-checks to validate the current deployment. [elioschmutz]
- Only prevent reopening a document if the referencing task is for approval. [njohner]
- Bump docxcompose to get support for updating multiline Content Controls. [lgraf]
- Add support for providing formatted address blocks as DocProperties. [lgraf]


Bug fixes:


- Add upgrade step that fixes order of IPropertiesPlugin PAS plugins. [lgraf]
- Fix permission check for revive_bumblebee_preview action. [tinagerber]
- Disallow anonymous access to member portraits. [lgraf]
- Fix task listing export to excel and PDF for Oracle. [njohner]


Other changes:


- Bump ftw.testing and ftw.keywordwidget to most recent version. [phgross]
- Bump ftw.testbrowser to most recent version. [lgraf]
- Avoid creating journal entries during contact migration. [njohner]
- Remove legacy SQL contacts implementation. [lgraf]
- Membership docproperties now take the address, phone number, URL and Email directly from the membership. [njohner]


2022.24.1 (2022-12-07)
----------------------

Bug fixes:


- Disable lock check in @tus-upload endpoint again. [tinagerber]


2022.24.0 (2022-12-07)
----------------------

New features:


- No longer grant permission to task responsible to add content to the dossier. [njohner]
- Provide custom properties of documents and dossiers as docproperties. [tinagerber]
- Introduce a new option hide_members_for_guests on workspaces. [phgross]


Bug fixes:


- Make OGDS sync case-insensitive in regard to user IDs. [lgraf]
- Revoke roles when objects are removed from a task's related items.


Other changes:


- Remove various unneeded catalog indexes and metadata columns. [tinagerber]
- Remove 'comments' field for dossier templates. [lgraf]
- Also allow to deliver mails back to the predecessor task. [njohner]
- SchemaMigration: Add create_index_if_not_exists() helper method. [lgraf]
- Use create_index_if_not_exists() for recent upgrade steps that create indexes. [lgraf]


2022.23.0 (2022-11-24)
----------------------

New features:


- Add ``@@oc_checkout`` view that redirects to oc: checkout URL. [lgraf]


Bug fixes:


- Fix unicode error when disposing a disposition on admin unit with umlaut in title. [lgraf]
- Use disposition creator's fullname in eCH0160 'ablieferndeStelle' field. [lgraf]
- Fix workspace invitations portal redirects. [phgross]
- Bump ftw.mail to fix mails with cropped attachment titles. [phgross]
- Fix user lookup by email for workspace invitation mail. [tinagerber]
- Sequential tasks: Only allow subtasks to be started when parent is in progress. [lgraf]


Other changes:


- Bump docxcompose to handle document language when updating datefields. [njohner]
- Re-enable forbidding tus-replace when document is locked by another user. [njohner]


2022.22.0 (2022-11-09)
----------------------

New features:


- Add ability to notify users when they're added to a workspace with the @participations endpoint. [tinagerber]


Bug fixes:


- Update changed field and ark document as recently touched when copying documents as new version from workspace. [tinagerber]
- Fix sorting in OGDSUserListing when members of a group are listed. [njohner]
- Return an 'active'-flag for available roles in in the ``@participations`` endpoint. [elioschmutz]


Other changes:


- Add template_folder_url to the @config endpoint. [elioschmutz]
- @solrsearch provieds filters for -@id_parent and -url_parent to exclude path parents. [elioschmutz]
- Add support for canceling checkout with Office Connector. [buchi]
- Add `@prepare-copy-dossier-to-workspace` endpoint to prepare copying a subdossier to a workspace.
- @copy-document-to-workspace: Also allow copying documents to workspace folders.
- API Docs: Add CAS authentication documentation. [lgraf]
- No longer escape custom_invitation_mail_content in teamraum invitation mail. [tinagerber]


2022.21.0 (2022-10-26)
----------------------

New features:


- Be more lenient about when and by whom tasks can be modified. [njohner]
- Modifying a task's relatedItems or text now creates a response and activity. [njohner]
- Allow editors to modify open and refused forwardings. [njohner]
- Support external_reference in dossier excel report. [tinagerber]


Bug fixes:


- Improve performance of @globalindex endpoint. [tinagerber]


Other changes:


- Clean-up activity translations. [njohner]
- No longer cache kub label mapping for an hour, use If-Modified-Since header instead. [tinagerber]


2022.20.0 (2022-10-12)
----------------------

New features:


- Allow cancellation of tasks in progress. [tinagerber]
- Include KuB organization phone number in membership docproperties. [lgraf]
- Include extra address lines from KuB contacts in DocProperties. [lgraf]


Bug fixes:


- Include house number in `*.address.street` DocProperties for KuB entities. [lgraf]
- OGDS auth plugin: Fix how we access RowProxy results from SQLAlchemy. [lgraf]
- Consider time zone when determining the end date of a dossier. [tinagerber]
- Bump docxcompose to fix bug where placeholder values for empty/absent docproperties weren't always updated. [lgraf]


Other changes:


- Add users.object_sid column to OGDS. [lgraf]
- Expose `objectSid` property via OGDS auth plugin. [lgraf]
- Add `display_name` column to OGDS user model. [lgraf]
- OGDS auth plugin: Use OGDS `display_name` as the `fullname` member property. [lgraf]
- Add `organization` column to OGDS user model. [lgraf]


2022.19.0 (2022-09-28)
----------------------

New features:


- Implement OGDS authentication plugin. [lgraf]
- Add username and external_id columns to user model. [tinagerber]
- Add groupname and external_id columns to group model. [tinagerber]
- Improve links of workspace invitation email template. [elioschmutz]


Bug fixes:


- Sort dossier participants by participant_title in @participations endpoint. [tinagerber]
- Current participants are now filtered out in @possible-participations endpoint. [njohner]
- Fix attaching documents for external users. [tinagerber]
- Use client own preserved_as_paper default when transporting documents. [phgross]
- Remove group memberships in ogds sync when ldap group is deactivated. [tinagerber]


Other changes:


- Make max dossier depth restriction less strict. [lgraf]
- Optimize KuBContactActor. [tinagerber]
- Include title in private folder serialization. [tinagerber]


2022.18.0 (2022-09-13)
----------------------

New features:


- Allow to invite users to a workspace through the workspace-client from GEVER. [elioschmutz]


Bug fixes:


- Do no longer show previous of older document versions if the new version is not convertable. [elioschmutz]


Other changes:


- Remove IRestrictedDossier behavior and addable_dossier_types field. [tinagerber]
- Adjust journal entry title of manual entries. [tinagerber]
- Setup test environment for workspace client e2e tests [elioschmutz]


2022.17.0 (2022-08-30)
----------------------

Bug fixes:


- Handle deleted dossiers in NightlyDossierJournalPDF. [njohner]
- Fix updating a custom property value when the previous value contained an umlaut. [elioschmutz]
- Fix user lookup by email for inbound mail. [lgraf]


Other changes:


- Remove nightly jobs feature flag. [tinagerber]
- Add support for meetings migration and deactivation. [njohner]
- Allow admins and workspace admins to modify and delete their own workspace participations. [tinagerber]
- Improve performance of visible users and groups filter. [buchi]


2022.16.0 (2022-08-17)
----------------------

New features:


- Add `title` field to OGDS user model. [lgraf]
- Add `job_title` field to `@ogds-user-listing` endpoint. [lgraf]


Bug fixes:


- Fix excel export if multiple customfields with same name are configured. [phgross]


Other changes:


- Switch `@recently-touched` endpoint to Solr. [lgraf]
- Only save custom properties defaults of active and default slots. [njohner]
- Policytemplate: Always configure ALL shared service URLs. [lgraf]


2022.15.0 (2022-08-03)
----------------------

New features:


- Add parameter to deactivate the workspace in the @unlink-workspace endpoint. [tinagerber]
- Index containing_dossier for document templates. [tinagerber]
- Add sender docproperties when creating document from template. [njohner]
- Add new review state for documents: document-state-final [njohner]


Bug fixes:


- Fix indexing of containing_dossier and containing_subdossier for documents in dossier templates. [tinagerber]
- Fix column width in latex subdossier listings. [phgross]
- Support foreign zip codes in document properties. [tinagerber]


Other changes:


- Use same labels in role assignment reports as in sharing view. [njohner]


2022.14.0 (2022-07-20)
----------------------

New features:


- Include links to related items in the teamraum meetings pdf. [phgross]
- Add DELETE method for @journal endpoint (only available for new manual journal entries) . [elioschmutz]
- Add PATCH method for @journal endpoint (only available for new manual journal entries) . [elioschmutz]
- Add `category` attribute for serialized @journal entry items (only available for new manual journal entries) . [elioschmutz]
- Allow setting and modifying time in manual journal entries. [njohner]


Bug fixes:


- Improve perfomance in KuB contact source. [phgross]
- Bump docxcompose to fix issues with headers and footers for documents with sections. [njohner]
- No longer sync groups with names containing non-ascii characters into the OGDS. [tinagerber]


Other changes:


- Optimize performance of groups API. [buchi]
- Allow to recreate deleted local groups. [buchi]
- Allow responsible to directly close tasks for direct execution. [njohner]
- Bump ftw.upgrade to handle dead brains in security updates. [njohner]
- Enable all languages by default for Teamraum policies. [njohner]
- Add checkin comment in DocumenVersionCreatedActivity description. [njohner]
- Optimize resolve GUID section in bundle import. [buchi]
- Rename action to restore a document version. [tinagerber]
- Bump ftw.solr to 2.12.0 to minimize the ZODB locking time. [njohner]
- Refactor journal entry handling implementation . [elioschmutz]
- Properly deserialize vocabulary values in @journal endpoint. [elioschmutz]
- Rename `comments` attribute for GET @journal entries to `comment` which is the expected naming in the POST request. [elioschmutz]
- Set Accept-Language header when requesting KuB. [tinagerber]
- Bump alembic, psycopg2, SQLAlchemy-Utils and pytz to more recent versions. [buchi]


2022.13.0 (2022-07-07)
----------------------

New features:


- Set creator during bundle import and use creator as journal entry actor. [phgross]
- Enabled zipexport for workspaces and workspacefolders. [phgross]
- - Use language specific analyzers for indexing and switch to eDisMax query parser. [buchi]
- Allow saving journal entry comments as HTML structure. [tinagerber]
- The @journal endpoint can now be filtered and searched. [elioschmutz]
- Add primary_participation_roles to registry. [tinagerber]
- Add new @transfer-number endpoint to update a disposition's transfer number. [njohner]
- Add additional_ui_attributes to registry. [tinagerber]


Bug fixes:


- Also check folders to which one has no access when removing workspace participations. [tinagerber]
- Hide teams in user details view if contact folder does not exist. [tinagerber]
- Also handle groupids with group prefix in @actors endpoint. [tinagerber]


Other changes:


- Improve error messages when removing workpace participation fails. [tinagerber]
- Remove contact folder from policy template. [tinagerber]
- - Bump Solr version to 8.11.2. [buchi]
- Drastically improve performance of reactivation for highly nested dossiers. [njohner]


2022.12.0 (2022-06-21)
----------------------

New features:


- Sort group users by last name and allow filtering users by group membership in ogdsuserlisting. [njohner]
- Allow current value in single or multiple choice fields. [njohner]
- Support importing dossier participations in bundle import. [phgross]
- Add param ``notify_all`` to share content with all authorized participants in @share-content endpoint. [tinagerber]
- Add DELETE @responses API endpoint. [tinagerber]
- Add modified and modifier field to response schema. [tinagerber]
- Add chair, secretary and attendees presence state to workspace meeting. [tinagerber]


Bug fixes:


- Fix workspace member vocabularies for workspace folders and other contents. [njohner]
- Fix multiple choice field validation for custom properties. [njohner]
- No longer clear task permissions when protecting a dossier. [phgross]
- Fix search by mailaddress in workspace invitations and mail-in. [phgross]
- Order AllGroupsSource groups by title. [elioschmutz]


Other changes:


- Bump ftw.bumblebee to version 3.10.0 which allows to configure the bumblebee API prefix. [buchi]


2022.11.0 (2022-05-24)
----------------------

New features:


- Only allow moving template documents to TemplateFolders. [njohner]
- Only allow moving documents in DossierTemplates to DossierTemplates. [njohner]
- Excel export: Remove limit of 1000 items. [elioschmutz]
- Excel export: Items to export can be addressed by a listing-name and filters. [elioschmutz]
- Add disposition setting, to only attach the original file if conversion is missing. [phgross]


Other changes:


- Incresed listing performance when listing objects with empty fields. [elioschmutz]
- Remove usersnap settings. [njohner]


2022.10.0 (2022-05-11)
----------------------

New features:


- Excel export: Support additional columns and custom properties. [lgraf]
- Add @ui-actions endpoint. [tinagerber]
- Allow to move dossiertemplates and tasktemplatefolders. [tinagerber]
- Reader cannot copy or move items anymore. [njohner]
- Do not copy creator and creation date when transporting task documents. [njohner]
- Return creator in task serialization. [njohner]
- Allow workspace admins to delete workspaces. [tinagerber]


Bug fixes:


- Correctly set content type in tus-upload. [njohner]
- Fix contentType problem when copying mails with teamraum connect. [phgross]
- Fix moving an object with the api where not all path elements are accessible. [phgross]
- Handle inactive users in the @accessible-workspaces endpoint. [njohner]
- Fix possible watchers query to work for Oracle databases as well. [tinagerber]


Other changes:


- Improve performance when renaming dossiers. [buchi]
- LimitedAdmin can no longer set local roles (sharing and dossier protection). [njohner]
- Remove flaky test. [njohner]


2022.9.0 (2022-04-26)
---------------------

New features:


- When changing the task responsible, the previous responsible's permissions are no longer revoked, but only when the task is completed. [tinagerber]
- No longer allow to change task responsible via PATCH request. [tinagerber]
- @process endpoint also accepts a deadline for task folders. [elioschmutz]
- Add support for nested task process in the sequence handling. [phgross]
- `@tasktree` endpoint properly handles nested tasks by adding a `is_task_addable` and `is_task_addable_before` attribute for each item. [elioschmutz]
- Include protect-dossier role assignments, in the role-assignment reports. [phgross]


Bug fixes:


- Local roles are correctly set and revoked when accepting and closing a team task. [tinagerber]
- Allow uploading a file with @tus-upload endpoint if the document has no file yet. [tinagerber]
- TUS upload: Only clean up file system data after successful commit. [lgraf]
- Make automatic closing of a main task fail safer. [phgross]


Other changes:


- Bump SQLAlchemy to latest 1.3 version. [phgross]
- Increase meeting zip export poll timeout to 5 minutes. [tinagerber]
- Translate error message when trying to copy a checked-out document. [njohner]


2022.8.0 (2022-04-12)
---------------------

New features:


- Add response to parent task when subtask is closed or cancelled. [tinagerber]
- Add support for trashing TR documents after retrieving them back to GEVER. [lgraf]
- Show list_workspaces action also for subdossiers. [tinagerber]
- Added new `@process` endpoint. [njohner]
- @task-template-structure endpoint returns the absolute deadline for tasktemplates. [elioschmutz]
- @task-template-structure endpoint returns the `is_private` attribute for tasktemplates with a static value of False. [elioschmutz]
- Add a new endpoint @task-template-structure [elioschmutz]


Bug fixes:


- Fix deleting workspace participations of inactive users. [phgross]
- Fix reference_prefixes update mechanism for removed documents. [phgross]


Other changes:


- Improve policy templates LDAP base OU. [njohner]


2022.7.0 (2022-03-29)
---------------------

New features:


- Allow privileged users to notify others via `@external-activities` endpoint. [lgraf]
- Also accept group IDs in ``@external-activities`` notification_recipients. [lgraf]
- Add task transition from closed to in progress for administrators. [phgross]
- Add support for nested TaskTemplateFolders. [njohner]
- Add feature flag for link_to workspace action. [tinagerber]
- Add feature flag to restrict workspace creation in UI. [tinagerber]
- Add label for NullActor. [tinagerber]
- Improve error handling when interacting with KuB. [tinagerber]
- Add gever_url field to workspaces, documents and mails. [tinagerber]
- Improve docker / docker compose support for testserver. [jone]


Bug fixes:


- NotificationDispatcher: Only return failed notification as not_dispatched. [lgraf]
- Allow deleting dossier participations of unknown contacts. [tinagerber]
- Fix removing of inbox mail. [njohner]
- Fix docx upload validator, make docx mandatory only for the proposal document. [phgross]
- Allow Administrator and LimitedAdmin to export repository as excel. [njohner]


Other changes:


- Bump ftw.upgrade to version 3.3.0 to enable exclusive usage of instance0 during updates. [njohner]
- Add a new global permission "opengever.workspace: Access all users and groups". [elioschmutz]
- Implements view protection for users and groups in teamraum. [elioschmutz]
- Improve error handling for workflow transitions over the API. [njohner]
- Add inactive user to testing fixture. [njohner]
- Allow normal users to revive bumblebee previews in Teamraum. [njohner]


2022.6.0 (2022-03-15)
---------------------

New features:


- Add checklist feature flag. [tinagerber]
- Add new @linked-workspace-participations endpoint. [njohner]
- Add configuration option for dashboard cards. [phgross]


Bug fixes:


- Allow all documents of a linked workspace to be copied to a dossier. [tinagerber]
- Fix IntIdMaintenanceJobContextManagerMixin obj_to_key if there is no registered intid. [elioschmutz]
- Handle errors in nightly jobs. [tinagerber]
- Fix getting OneOffixx favorites for templates that are not whitelisted. [buchi]
- Add labels to OneOffixx templates whitelist. [buchi]
- Handle group prefix in principalid in @role-assignment-reports endpoint. [tinagerber]
- Add translated title fields to Solr schema. [lgraf]
- Add translated title support to OGSolrDocument. [lgraf]
- Use translated titles in `@navigation` endpoint. [lgraf]


Other changes:


- Support adding a list of participants in @participations endpoint. [njohner]


2022.5.0 (2022-03-01)
---------------------

New features:


- Allow admins to delete deactivated workspaces. [tinagerber]
- Add dossier_type_colors whitelabeling setting. [tinagebrer]
- GET `@favorites`: Include dossier_type in response. [lgraf]
- Serialization: Include dossier_type in JSON summary for dossiers. [lgraf]
- `@navigation`: Include dossier_type in response. [lgraf]
- Add checklist field to dossier and dossiertemplate. [tinagerber]
- Add `@reference-number` API endpoint and expansion for plone site and dexterity content. [deiferni]


Bug fixes:


- Allow unlinking workspaces even if the workspace is deactivated or dossier is closed. [tinagerber]
- Default value acquisition: Skip intermediate objects missing attribute. [lgraf]
- NightlyWorkflowSecurityUpdater: Gracefully skip objs that can't be resolved. [lgraf]
- Reindex 'filename' when creating a new document version. [lgraf]
- Properly handle the BCC address in teamraum if sending documents by email. [elioschmutz]


Other changes:


- Switch `@navigation` endpoint to Solr queries. [lgraf]


2022.4.0 (2022-02-16)
---------------------

New features:


- Remove propagation and restriction of ILifecycle and IClassification fields. [njohner]
- Replace dossier comments field with IResponseSupported behavior. [tinagerber]
- Add custom fields to dossier details pdf. [tinagerber]
- Add comments to dossier details pdf. [tinagerber]


Bug fixes:


- Don't attempt to transport custom properties across admin units. [lgraf]
- Custom properties: Don't prematurely make returned values json_compatible(). [lgraf]
- Custom properties: Fix rendering z3c.form widgets in display mode for date fields. [lgraf]
- Fix setting static defaults for propertysheet date fields. [lgraf]
- Include inactive users in the all_users_and_groups source. [phgross]
- Suppress creation of todo completion activities during upgrades to avoid failing upgrades. [lgraf]
- Fix content-sharing for multiple recipients and cc recipients. [phgross]
- Fix dossierdetails for dossier with SQL participations. [njohner]


Other changes:


- Avoid unnecessary security updates when adding new content or renaming existing content. [buchi]
- Optimize warmup: reduce warmup time and memory consumption after warmup. [buchi]
- Set security related HTTP headers. [buchi]


2022.3.0 (2022-02-02)
---------------------

New features:


- Actor portrait_url respects the IActorSettings to choose the portrait_url from plone or the portal. [elioschmutz]
- Add parameter to include full representation in @actors endpoint. [tinagerber]
- Add browser view and zopectl command to show nightly jobs stats. [tinagerber]
- The @solrsearch results can now be filtered by ``@id_parent`` or ``url_parent``. [elioschmutz]
- Testserver now automatically isolates on startup. [jone]


Bug fixes:


- Include documents inside task and proposals in the ech0160 export. [phgross]


Other changes:


- Use relative paths for the @solrsearch path_parent filter query. [elioschmutz]
- Make error serialization for `@propertysheets` more frontend-friendly. [lgraf]
- Improve memory usage for upgrade steps using nightly maintenance jobs. [njohner]
- Bump ftw.upgrade to improve memory and upgrade duration management. [njohner]
- Return fullname and userid as term title in ActualWorkspaceMemberSource. [tinagerber]


2022.2.0 (2022-01-19)
---------------------

New features:


- - Expose dossier_type_label column in @listing endpoint. [elioschmutz]
- Add @propertysheet-metaschema endpoint. [lgraf]
- Expose propertysheet JSON schemas under `@schema` endpoint. [lgraf]
- GET @propertysheets: Return same format as POST, instead of JSON schema. [lgraf]
- Add some extra info to `@propertysheets` listing. [lgraf]
- Add PATCH support for `@propertysheets` endpoint. [lgraf]
- Add LimitedAdmin role. [tinagerber]
- Docker support for testserver. [jone]


Bug fixes:


- Drop related items when copying document to workspace. [njohner]
- Disallow edit with office online for trashed documents. [njohner]
- Correctly handle missing excerpt suffix template when creating protocol excerpt. [njohner]
- Correctly handle error when trying to move proposal document. [njohner]


Other changes:


- Avoid reporting normal API exceptions in sentry. [njohner]
- Drop workspace administrator group from policy templates and setup. [njohner]


2022.1.0 (2022-01-04)
---------------------

New features:


- Add responsible field to the workspace schema. [phgross]
- Add @xhr-upload endpoint to upload documents with a multipart/form-data xhr request. [elioschmutz]
- Expose retention_expiration column in @listing endpoint. [tinagerber]
- Add API Support for the disposition history. [phgross]
- Provide disposition actions in the @actions endpoint. [phgross]
- Add @my-substitutes, @subtitutes and @out-of-office API endpoints. [tinagerber]
- Add @subtitution API endpoint. [tinagerber]
- Include email address in workspace and workspace folder serialization. [tinagerber]
- Add support for KuB contacts in document-from-template endpoint. [njohner]
- Inbound mail: Add support for sender address aliases [lgraf]
- Add @kub endpoint. [njohner]
- Include custom properties in the eCH-0160 export. [phgross]
- Add support for custom property facets to `@solrsearch` endpoint. [lgraf]
- Add 'dossier_type' index to solr [elioschmutz]
- Allow 'dossier_type' in the '@listing' endpoint [elioschmutz]
- Add a new property 'multiple_dossier_types' to the '@config' endpoint. [elioschmutz]
- Expose document_type_label column in @listing endpoint. [tinagerber]
- Add new customfield type date.
- Make sure customproperty default values are initialized, when content is created. [phgross]
- Allow POST requests against the @solrsearch endpoint. [elioschmutz]
- The @solrsearch results can now be filtered by its ``@id``. [elioschmutz]
- Add `@external-activities` endpoint to allow creating activities via API. [lgraf]
- Extend KuBContactSource with ogds users. [njohner]


Bug fixes:


- Fix @groups patch endpoint. [tinagerber]
- Bump docxcompose to 1.3.4 to fix IndexError on custom styled bullet points. [lgraf]
- Include is_completed in sql task serialization. [tinagerber]
- Fix soft-delete for inbox documents.
- Fix propagation of values for restricted vocabularies and reindex retention_expiration when necessary. [njohner]
- Fix task overview in old ui for tasks created by task delegation. [elioschmutz]
- Task delegation does no longer set an unwanted documents-property on the subtask. [elioschmutz]
- Fix file upload into subdossiers which exceed the current max dossier depth. [phgross]
- Document serializer respects the file_extension of the currently requested version [elioschmutz]
- Fix batching issues in sharing view. [njohner]
- Restrict check whether meeting is reopenable to meetings from same period. [njohner]
- Fix copy document from workspace as new version when gever document is trashed. [njohner]
- Bump ftw.recipe.solr to version 1.3.6 and use custom Solr distribution containing Log4j 2.17.0. Mitigation for CVE-2021-44228, CVE-2021-45046 and CVE-2021-45105. [buchi]
- Fix task syncing when deadline is modified twice by same user. [njohner]
- Fix save PDF under for workspace documents. [njohner]


Other changes:


- Improve translations of the disposition module. [njohner]
- Add PropertySheetsManager role and custom permission. [lgraf]
- Notification settings: Change internal name of "general" tab. [lgraf]
- Remove value propagation of archival_value and custody_period. [njohner]
- Improve teamraum meeting PDF style. [njohner]
- Only create journal PDF for main dossiers (all entries in one file). [lgraf]
- Create journal PDF when dossier is offered (instead of resolved) [lgraf]
- Use the newly available resolve endpoint to fetch a Kub entity. [phgross]


2021.24.1 (2021-12-01)
----------------------

Bug fixes:


- Fix sending notification mails from or to users with long mail addresses. [phgross]


2021.24.0 (2021-11-30)
----------------------

New features:


- Use Gever API error handling for ForbiddenByQuota errors. [tinagerber]
- Improve API support for disposition objects. [phgross]
- Add closed state for workspace meetings. [tinagerber]
- Add KUB configuration and client. [phgross, njohner]
- Add KuB participations. [phgross, njohner]
- Handle KuB contacts and participations in classic UI. [njohner]
- Support KuB participations in listing endpoint. [njohner]


Bug fixes:


- Fix repositoryfolder addable types constraints, make dispositions always addable. [phgross]
- @reminders does not raise anymore when no reminder is set. [njohner]
- Fix create-policy command. [njohner]
- @complete-successor-task: 'documents' payload now uses relative paths instead the physical path to resolve references  [elioschmutz]
- Include documents manually added to submitted proposal in meeting Zip and protocol data. [njohner]
- Make WOPI discovery requests more robust and fail safe. [phgross]


Other changes:


- Remove ftw.tika dependency and uninstall tika profile. [phgross]
- Split upgrade with high memory consumption into two. [deiferni]
- @complete-successor-task: 'documents' payload also accepts urls [elioschmutz]


2021.23.3 (2021-11-25)
----------------------

Other changes:


- Split upgrade with high memory consumption into two. [deiferni]


2021.23.2 (2021-11-22)
----------------------

Bug fixes:


- Include documents manually added to submitted proposal in meeting Zip and protocol data. [njohner]


2021.23.1 (2021-11-19)
----------------------

No significant changes.


2021.23.0 (2021-11-17)
----------------------

New features:


- Add flags to office connector url for attach action. [tinagerber]
- Support dispositions in the @listing endpoint. [phgross]


Bug fixes:


- Update local roles after moving document when creating forwarding. [njohner]
- Fix storing document in bumblebee during copy-paste. [njohner]
- Make workspace meeting start and end timezone aware. [njohner]
- Make sure preferred language is used for API PATCH requests. [phgross]


Other changes:


- Implement completing workspace todos with a new two state workflow. [elioschmutz]
- Introduce '@toggle' endpoint for workspace todos. [elioschmutz]
- Add new listing for the '@listing' endpoint: todo_lists [elioschmutz]
- Remove hardlimit of 500 todos per workspace. [elioschmutz]
- Persist missing preserved_as_paper and IClassification fields default values. [njohner]
- Add is_completed solr index and provide the field in the listing endpoint. [phgross]
- Improve description of read/write access for dossier protection. [njohner]
- Extend API error representation. [phgross]


2021.22.2 (2021-12-02)
----------------------

Bug fixes:


- Fix file upload into subdossiers which exceed the current max dossier depth. [phgross]


2021.22.1 (2021-12-02)
----------------------

Bug fixes:


- Fix sending notification mails from or to users with long mail addresses. [phgross]


2021.22.0 (2021-11-03)
----------------------

New features:


- Automatically pass documents from one sequential task to the next if desirded. [njohner]
- Add additional public-trial-status PATCH endpoint for documents. [phgross]
- Allow to include subtasks in task reports. [tinagerber]


Bug fixes:


- Fix copying an object with the api where not all path elements are accessible. [phgross]
- Add minimal support to Actor for SQLContacts. [phgross]
- Fix UnicodeEncodeError. [tinagerber]
- Add validation of the end date for meetings. [tinagerber]
- Fix UnicodeEncodeError in ogds sync. [tinagerber]


2021.21.0 (2021-10-20)
----------------------

New features:


- Implement webactions with scope context. [tinagerber]
- Add redirect support for old paths to bundle import. [phgross]
- Make workspace invitation mail content customizable. [phgross]


Bug fixes:


- Correct IDs for ContactFolders, InboxContainers, Inboxes, CommitteeContainers and TemplateFolders created over the API. [njohner]
- Do not bypass NameFromTitle for subtasks created when delegating a task. [njohner]
- Strip outlooks AD information in mails document_author extraction. [phgross]
- Fix accepting remote forwarding in new dossier without response text. [njohner]
- Reindex reference and searchable text when moving documents and dossiers. [njohner]
- Also update sortable_reference and SearchableText when reference_prefix has changed. [phgross]


Other changes:


- Enable nightly jobs. [njohner]
- Use UIDs as tokens for documents when delegating a task. [njohner]
- Add application/msonenote to OC editable types. [njohner]


2021.20.0 (2021-10-06)
----------------------

New features:


- Add new endpoint @accessible-workspaces. [tinagerber]
- Add permission to protect lifecycle and classification fields. [tinagerber]


Bug fixes:


- Filter non-documentish types for document-to-document relations. [lgraf]
- Skip duplicate users with different capitalization during ogds sync. [phgross]
- Do not create DocumenVersionCreatedActivity when cancelling checkout. [njohner]
- Fix handling of unicode actor ids. [buchi]
- Truncate too long filenames when updating favorites. [deiferni]
- Bump Products.LDAPMultiPlugins to version 1.15.post4 which fixes case-insensitivity in filtering by group base DN. [buchi]


Other changes:


- Implement e2e testserver ogds isolation. [elioschmutz]
- Include document version in Office Connector metadata. [buchi]
- Add checkbox to purge solr when deploying Gever. [njohner]


2021.19.0 (2021-09-21)
----------------------

New features:


- Add responsible_org_unit field to repository folders. [njohner]
- Automatically close main task when all subtasks in a sequential or parallel task are in a final state. [tinagerber]


Bug fixes:


- Moving a dossier over the API now respects the maximum dossier depth. [njohner]
- Fix ++widget++ traversal when form contains custom properties. [lgraf]
- Transform default *value* to *token* in custom property schemas. [lgraf]
- Propertysheets: Avoid 'RequiredMissing' for empty multiple_choice fields [lgraf]
- Improve performance for SQL API endpoints, which uses the SQLHypermediaBatch. [phgross]
- Fix actor represents URL for teams. [buchi]
- Remove immediate_view for proposals, fixes protocol approval proposal creation. [phgross]
- Fix actors endpoint for the SystemActor. [phgross]


Other changes:


- Redirect to workspace if the invitation link refers to an already accepted invitation. [tinagerber]
- Make import of repository excel files more robust. [njohner]
- Enable nightly jobs in policy templates. [njohner]
- NightlyJobRunner: Update a timestamp on PloneSite when executing jobs. [lgraf]
- OGDS sync: Add helper to determine if sync happened in last 24h. [lgraf]


2021.18.0 (2021-09-10)
----------------------

New features:


- Add new customfield type multiple_choice.
- - Include checkout collaborators and file modification time in document serialization. [buchi]
- - Include checkout collaborators, file modification time, lock time and lock timeout in document status. [buchi]
- Add nightly maintenance jobs. [njohner]
- Property sheets: Add support for static as well as dynamic default values. [lgraf]
- Add @reactivate-local-group endpoint. [tinagerber]


Bug fixes:


- Sanitize document_author after extracting from mail header. [deiferni]
- Prevent non-docx and empty files in a PATCH request to a proposal document. [deiferni]
- Prevent transferring checked out documents when completing successor tasks. [deiferni]
- No longer allow adding a repository folder to a repository folder when the repository folder is deactivated. [tinagerber]
- Avoid workflow update for all documents, in the FixSharingPermissions upgradestep. [phgross]
- Allow editing of a document with Office Online even if the document is not locked. [tinagerber]
- Fix changing bucket being iterated in size during relation catalog cleanup. [deiferni]
- Add support for unicode userids in ogds-users and ogds-user-listing endpoints. [njohner]
- Update local roles when dossier protection is revoked. [tinagerber]
- Reindex responsible when accepting a team task. [njohner]
- Use portal title as WOPI BreadcrumbBrandName. [phgross]


Other changes:


- Drop validation requiring a file or `preserved_as_paper` to be `True`. [deiferni]
- - Allow check-in for collaborators if lock expired. [buchi]
- Remove value restriction for the custody_period field. [tinagerber]


2021.17.0 (2021-08-30)
----------------------

New features:


- Include @type, active,  portrait_url, representatives and respresents in @actors endpoint. [buchi]
- Add support for groups in @share-content endpoint. [tinagerber]
- Include group users and groups in @actual-workspace-members endpoint. [tinagerber]
- Add new @reference-numbers endpoint. [njohner]
- Add approval_state Solr field and corresponding Plone indexer. [lgraf]
- API: Allow for approving documents when resolving a task. [lgraf]
- Include committee in proposal serialization. [tinagerber]
- Include proposal, meeting, submitted_proposal and submitted_with in document serialization. [tinagerber]
- Agenda item attachments of submitted proposals can be reordered. [elioschmutz]


Bug fixes:


- Dossier protection works properly over the REST-API.
- Show copy document to workspace action also in subdossiers. [phgross]
- Fix updating document title in favorites when document title is changed via API. [deiferni]
- Remove `@@` prefix from links to personal preferences browser view. [deiferni]
- Fix handling of relations when an object is deleted. [njohner]


Other changes:


- Reindex missing changed dates in Solr. [njohner]
- Bump ftw.solr to 2.9.5 to allow unrestrictedSearch. [njohner]
- Allow Reader to revive bumblebee previews. [deiferni]
- Always redirect to notification resource in `@@resolve_oguid` if user has permission to view. [deiferni]
- Revert merge of upgrade reindexing reference and sortable_reference. [njohner]
- Add new actions category: ui_context_actions with a new action: `protect_dossier`. [elioschmutz]
- Expose `is_protected` in the dossier serializer. [elioschmutz]
- Bump docxcompose to version 1.3.3. [njohner]
- Change workspace daily digest notification defaults. [deiferni]
- Rename label for "Reference prefix" to "Repository number" (en, de, fr) [lgraf]


2021.16.0 (2021-08-12)
----------------------

New features:


- Allow deleting repository folders over the REST-API. [njohner]
- Add document approvals storage and API endpoints. [phgross]
- Add sequence_number to all API object serializers. [phgross]


Bug fixes:


- Extract attachments from mail inside submitted proposal into parent. [njohner]
- Update ftw.mail to fix issues with message/rfc822 attachments. [njohner]
- Favorite positions get updated correctly when trashing / deleting an object. [njohner]
- Fix returning translated title in solrsearch and listing endpoints. [njohner]
- Update OneNote Mimetype. [njohner]
- Fix setting reminder over accept form. [njohner]


Other changes:


- Update sharing permissions. [njohner]
- Bump ftw.solr to version 2.9.4 to improve listing performance. [njohner]


2021.15.0 (2021-07-30)
----------------------

New features:


- Add @accept-remote-forwarding endpoint. [tinagerber]
- Add transition extender for forwarding-transition-refuse transition. [tinagerber]
- Support adding and updating teams via API. [phgross]
- Add new API endpoint @globalsources. [phgross]
- Add excel roleassignment-report download view. [phgross]


Bug fixes:


- Return a fixed and sorted list of referenced_roles in the @role-assignments endpoint. [phgross]
- Always return error message in @trash endpoint if content is not trashable. [tinagerber]
- Fix ``@versions`` for documents that do not have an initial version yet (lazy initial version). [deiferni]
- Fix downloading lazy initial versions for documents. [deiferni]
- Fix storing transition text when accepting forwarding. [deiferni]


Other changes:


- Remove ftw.tika dependency from the policytemplate.
- Improve policy templates for Teamraum deployments. [njohner]


2021.14.0 (2021-07-16)
----------------------

New features:


- Add sequence_type solr index for tasktemplatefolders and add field to @listing endpoint. [tinagerber]
- Add proposal excel export. [tinagerber]
- Add @submit-additional-documents endpoint. [njohner]
- Allow overriding task and subtask deadline in `@trigger-task-template` endpoint. [tinagerber]
- Include information about the curren admin_unit in the config endpoint. [phgross]
- Allow authenticated users to access vocabularies via API. [phgross]
- Add review_state and include_context parameters to @navigation endpoint. [tinagerber]
- Provide field unspecific mail download view. [phgross]


Bug fixes:


- Return a placeholder pdf instead of an image if a pdf is not digitally available. [tinagerber]
- Fix removing a profile-image with a PATCH request to the `@users/<userid>` endpiont. [elioschmutz]
- Do not allow to move documents via API if they are inside a task, proposal or closed dossier. [tinagerber]
- Clean up workspace workflow. [tinagerber]
- Prevent documents from being moved from repository or inbox to the templates or private root via API. [tinagerber]
- ContactsSource falls back to `ogds_user` type if no type is explicitly given. [elioschmutz]


Other changes:


- - Minor optimization of mail attachment code. [njohner]
- Remove document watchers feature flag. [tinagerber]
- Add OneOffixx "Funktionsvorlagen" to the whitelisted template types. [phgross]
- Add script to create service users. [deiferni]


2021.13.2 (2021-07-19)
----------------------

Bug fixes:


- Fix selecting all items for solr based listings in the classical UI. [deiferni]


2021.13.1 (2021-07-01)
----------------------

Bug fixes:


- Fix resolving a subdossier when filing_number feature is enabled. [phgross]


2021.13.0 (2021-06-25)
----------------------

New features:


- Support returning results for the solr stats component in the `@solrsearch` endpoint. [deiferni]
- Add watcher functionalities for document changes. [tinagerber]
- Add userid migration for UserSettings, NotificationSetting, Favorite, recently touched objects, task reminders, task templates, meetings and proposals. [deiferni]
- Support dossier resolving, incl. assignment of the filing number via API. [phgross]
- Allow trashing and untrashing WorkspaceFolders. [njohner]
- Allow deleting WorkspaceFolders and Mails. [njohner]
- Only allow deleting workspace folders, documents and mails when trashed. [njohner]


Bug fixes:


- Cleanup mail workflow_history for mails created before 2016. [phgross]
- Fix persisting default values when creating objects over the API. [njohner]
- Add language code parameter to office online edit link. [phgross]
- Improve error handling when quota limit gets exceeded on API requests. [phgross]
- Fix solr indexing of customproperties assigned to a specific dossier_type. [phgross]
- Fix sending additional files to pdflatex service (e.g. header logos). [deiferni]
- Allow to reassign tasks in all non final states. [tinagerber]
- Prevent changing the is_private field of existing tasks via API. [phgross]


Other changes:


- Upgrade steps merged to shorten upgrade runtime. [phgross]
- Disable mail unwrapping for inbound mails. [njohner]


2021.12.1 (2021-06-15)
----------------------

Bug fixes:


- Bump ftw.casauth to version 1.4.1 which includes a fix for authenticating the wrong user if an invalid ticket was supplied. [buchi]


2021.12.0 (2021-06-10)
----------------------

New features:


- Add virusscan validation upon file download and upload. [njohner]
- Add move_item action for tasks. [tinagerber]
- Add reference_number_addendum field to repository root and use it in reference number. [tinagerber]
- Allow to move contents from an old repository root to a new one. [elioschmutz]
- Add description to task report and link title to task. [tinagerber]


Bug fixes:


- Fix SQLHypermediaBatch for undefined sort orders.
- Add skip state to the list of finished task states. [phgross]
- Ensure consistent inbox placeful workflow assignment. [deiferni]
- Fix deleting agenda_items when document is already trashed.
- Fix reference number generation and indexing when moving dossiers, containing subdossiers. [phgross]
- Fix copy workspace document into a higher classified gever dossier. [elioschmutz]
- Fixed moving dossier with a tasktemplate process. [phgross]


Other changes:


- The `path_parent` field query of the `@solrsearch` endpoint properly resolves paths relative to the virtual host url and joins multiple `path_parent` field queries with an OR operator. [elioschmutz]
- Bump ftw.casauth to version 1.4.0 which provides support for cookie based authentication using REST API. [buchi]
- Customize @login endpoint by adding support for cookie based authentication. [buchi]


2021.11.1 (2021-05-28)
----------------------

Other changes:


- Fixed changelog for release 2021.11.0 [elioschmutz]


2021.11.0 (2021-05-28)
----------------------

New features:


- Add primary_repository URL to the @config endpoint.
- Include backreference list in dossier and documents api serialization. [phgross]
- Check for possible duplicate documents in @upload-structure endpoint. [njohner]


Bug fixes:


- Automatically assign placeful workflow policies when workspace root, private root and inbox are created. [deiferni]
- Fix filtering on values containing spaces in @listing endpoint. [tinagerber]
- Fix a problem in relation deserializer when not all path elements are accessible. [phgross]
- Attachment extraction now also works for mails in a workspace. [tinagerber]
- Fix closing remote task without copying any documents to a dossier. [elioschmutz]


Other changes:


- Add `workspaces_without_view_permission` attribute to @linked-workspaces endpoint. [tinagerber]
- Include `containing_subdossier`, `review_state_label` and `sequence_number` in task model serialization. [tinagerber]


2021.10.0 (2021-05-12)
----------------------

New features:


- Add `@listing-custom-fields` endpoint and allow retrieving custom properties in `@listing`. [deiferni]
- Added close-remote-task endpoint, for closing remote tasks of type `information`. [phgross]
- Add @upload-structure endpoint. [njohner]


Bug fixes:


- Bundle import: Skip configuration import if not exists. [phgross]
- Transfer workspace link to parent dossier when moving dossier into another dossier. [phgross]
- Fix permanently delete workspace documents. [elioschmutz]
- Handle no template for paragraphs in DebugDocxCompose view. [njohner]


Other changes:


- Prevent adding property sheets with conflicting field names. [deiferni]
- Don't allow removing last workspace admin role. [deiferni]
- Improve archival file conversion job management when resolving dossiers. [njohner]
- Remove value restriction for the archival_value field. [phgross]


2021.9.0 (2021-04-29)
---------------------

New features:


- Add policyless deployment. [lgraf]
- Add TTW bundle import. [lgraf]
- Add support for configuration import via bundle. [lgraf]
- Add new @versions endpoint for documents. [njohner]


Bug fixes:


- Fix searching for group descriptions with umlauts in search terms.
- Planned tasks can now be opened manually when necessary. [njohner]
- Fix `@history` endpoint when no history exists. [deiferni]
- API: Reject years before 1900 for date and datetime fields. [lgraf]
- Fix in-progress to close transition (API), for multi adminunit tasks. [phgross]


Other changes:


- Allow meetings to be reopened by a Manager. [deiferni]
- No longer include `meetings.json` metadata file in ZIP download of original files. [deiferni]
- Bump ftw.zopemaster to version 1.4.0 which provides support for TLS 1.2. [buchi]
- Bump docxcompose to version 1.3.2 which handles DocProperties in a case-insensitive manner. [buchi]
- Fix policygenerator for GEVER policies. [njohner, phgross]
- Switch GEVER-UI setting to a overall admin_unit setting.
- Bump ftw.solr to 2.9.3 and reindex documents with missing searchable text. [njohner]
- Bump psutil version for compatibility with BigSur. [njohner]
- Open Office Online in new tab. [buchi]
- Add is_remote_task and responsible_admin_unit_url to task serialization. [njohner]


2021.8.0 (2021-04-15)
---------------------

- Remove daterange restriction in spv meeting end date. [elioschmutz]
- Add attendees solr index for workspace meetings. [tinagerber]
- Fix broken task template responsibles [elioschmutz]
- Provide dossier_reference_number mergefield value also for ad-hoc proposals. [phgross]
- Fix plone site deletion by skipping certain event handlers. [njohner]
- Properly reset the responsible watcher if a user accepts a task assigned to a team. [elioschmutz]
- Add dossier_type field for dossiertemplates. [phgross]
- Index custom properties in searchable text. [buchi]
- Index custom properties in Solr dynamic fields. [buchi]


2021.7.0 (2021-04-01)
---------------------

- When delegating tasks via API, informed_principals can be set. [tinagerber]
- Add a new field `attendees` for workspace meetings. [elioschmutz]
- Dispatch notification for documents added to tasks. [lgraf]
- Introduce a new field dossier_type and customproperty slots for dossiers. [phgross]
- Add ICal export view and download action for workspace meetings. [phgross]
- Introduce customproperties default slots which is enabled for every document. [phgross]
- No longer fail during deployment if ldap is not in authentication plugins. [njohner]
- Add id field to the @listing endpoint. [elioschmutz]
- Add action to download meeting minutes as PDF. [buchi]
- Allow overriding task and subtask title and text in `@trigger-task-template` endpoint. [deiferni]
- Implement group_by_type parameter in @solrsearch endpoint. [tinagerber]
- Add repository_folders and template_folders to @listing endpoint. [tinagerber]
- Fix oc_checkout endpoint to work with shadow documents that don't have a content-type. [buchi]


2021.6.0 (2021-03-18)
---------------------

- Remove Disqus from the documentation. [njohner]
- Exclude opengever.workspace.meetingagendaitem from search results. [njohner]
- Index agenda items in the workspace meeting searchable text. [njohner]
- Show add_task_from_document action also for documents within tasks. [tinagerber]
- Add containing_subdossier_url to document serializer. [tinagerber]
- Implement a new content-type: opengever.workspace.meetingagendaitem. [elioschmutz]
- Create initial version upon checkin. [njohner]
- Add edit_items folder action. [tinagerber]
- Update .gitignore of policytemplates for deployment on CentOS 8. [njohner]
- Change p7m extension to eml (or extension configured in the registry) in mail download. [njohner]
- Fixed automatic start of a next task inside a sequential task process. [phgross]
- Only show "add task to process" link, if next task is not yet started. [phgross]
- Fix adding sequential task process on first position. [phgross]
- Filter out folder_delete folder button in @actions on repofolders. [njohner]
- Filter out trash and untrash folder buttons in @actions on repository root and folders. [njohner]
- Don't resolve or deactivate a dossier if it has linked workspaces without view permission. [elioschmutz]
- Reset value of NamedFileWidget in DocumentAddForm when validation fails. [njohner]
- When filtering by responsible in globalindex also return tasks assigned to a team the responsible belongs to. [buchi]


2021.5.2 (2021-04-20)
---------------------

- Fix in-progress to close transition (API), for multi adminunit tasks. [phgross]
- Add is_remote_task and responsible_admin_unit_url to task serialization. [njohner]


2021.5.1 (2021-03-09)
---------------------

- Fix tabbedview's upload container position for latest chrome versions. [phgross]


2021.5.0 (2021-03-04)
---------------------

- Fix support in TransitionExtender for RelationChoice fields. [phgross]
- Allow any authenticated users to use the REST API. [phgross]
- The @sharing endpoint now returns a batched result set if using the search param.  [elioschmutz]
- Cleanup conditionals protecting for changed date not set yet. [njohner]
- Use changed instead of modified in date range calculation for SIP packages. [njohner]
- Include mails in SIP package. [njohner]
- Fix creating documents from docugate over the restapi in private, inbox and workspace areas. [elioschmutz]
- Fix rejecting submitted proposal containing mail with extracted trashed attachment. [njohner]
- Add create_task_from_proposal action. [tinagerber]
- Implement GET @oneoffixx-templates to provide oneoffixx templates over the restapi. [elioschmutz]
- Implement POST @document_from_oneoffixx endpoint to create a document from a oneoffixx template. [elioschmutz]
- Also set title_en and title_fr for meetings in policy templates. [njohner]
- Extend solrsearch endpoint, with breadcrumbs information option. [phgross]


2021.4.2 (2021-03-09)
---------------------

- Fix tabbedview's upload container position for latest chrome versions. [phgross]


2021.4.1 (2021-02-25)
---------------------

- Add creator to the document serializer. [elioschmutz]

2021.4.0 (2021-02-18)
---------------------

- No longer show warning about failed notification deliveries if recipient user doesn't have an email address. [lgraf]
- Adapt policy templates for ianus portal. [njohner]
- Fix inbox document overview for managers. [lgraf]
- Always set APPS_ENDPOINT_URL and handle sablon, msg_convert and pdflatex as services in policy templates. [njohner]
- Add 'is_inbox_user' attribute to the @config endpoint [elioschmutz]
- Rename the attribute 'is_admin_menu_visible' from the @config endpoint to 'is_admin'. [elioschmutz]
- Fix custom property choice field (de-)serialization. [deiferni]
- Bump ftw.casauth to 1.3.1. [lgraf]
- Add @save-document-as-pdf API endpoint. [tinagerber]
- Only allow to save a document as pdf if document isn't checked out. [tinagerber]
- Update Plone to version 4.3.20. [buchi]
- Add icons for CAD file types. [buchi]
- Set SameSite=Lax flag for session authentication cookie. [buchi]
- Add support for Docugate templates. [buchi]
- Add sortable_reference solr index. [njohner]
- Rename object and set creator after copying with REST API. [buchi]


2021.3.0 (2021-02-03)
---------------------

- Interactive task template users are now handled as actors. [elioschmutz]
- Adding tasktemplates over the restapi properly separates the responsible user and client. [elioschmutz]
- Include path in the data submitted by the Solr update chain. [sebastianmanger]
- Fix wrapping of keywords in keywordwidget. [njohner]
- Harmonize translations for document sent and received dates. [lgraf]
- Add a new solr-index 'is_folderish'. [elioschmutz]
- Do not escape boolean filters in solr endpoints. [tinagerber]
- Include blocked_local_roles in serialization of dossiers and repofolders. [tinagerber]
- Index blocked_local_roles in solr and allow field in @listing endpoint. [tinagerber]
- Only allow to create linked workspace and link to workspace if dossier is open. [tinagerber]
- Add link_to_workspace folder action. [tinagerber]
- Implement custom properties in classic UI, currently available for documents and mails. [deiferni]
- Return only badge notifications in @notifications endpoint. [tinagerber]
- Only show create_proposal action on dossiers. [tinagerber]
- Enable Usersnap by default in SaaS policy template. [lgraf]
- Add English support for translated titles. [njohner]
- Return related_documents in journal endpoint. [tinagerber]
- Include checked_out and file_extension in summary serialization of documents and mails. [tinagerber]
- Respect active languages languages in WorkspaceRoot and PrivateRoot forms. [njohner]
- List informed principals in TaskAddedActivity description. [njohner]
- Fix deactivating committees with canceled meetings. [deiferni]
- Include custom properties in JSON schema for documents and mails in the `@schema` endpoint. [deiferni]
- Index getObjPositionInParent for sequential tasks and sort them on getObjPositionInParent in @tasktree endpoint. [tinagerber]
- Add is_task_addable_in_main_task and is_task_addable_before attributes to @tasktree endpoint. [tinagerber]
- Implement POST @notifications endpoint to mark all notifications as read. [tinagerber]


2021.2.0 (2021-01-20)
---------------------

- Clean up English translations. [lgraf]
- Add new API endpoint @white-labeling-settings. [tinagerber]
- Add relatedItems field to todo. [tinagerber]
- Add HubSpot feature flag. [tinagerber]
- Implement serialization and deserialization of custom properties via API, currently available for documents and mails. [deiferni]
- Bump docxcompose to version 1.3.1 to add support for dateformats. [njohner]
- Change key for agenda item list document to "documents" in zip export. [njohner]
- Bump ftw.solr to 2.9.2 to fix a bug with setting document_type back to None. [njohner]
- No longer allow to trash document templates. [tinagerber]
- Initialize English translations. [lgraf]
- Add getObjPositionInParent and preselected field to listing endpoint. [elioschmutz]
- Fix workflow transitions for tasktemplatefolders and tasktemplates over the restapi. [elioschmutz]
- Add 'en-us' as supported language in example content. [lgraf]
- Implement API to create, list and delete property sheet schema definitions. [deiferni]
- Implement storage for property sheet schemas in plone-site annotations. [deiferni]
- Fix loading next batch in gallery view. [buchi]


2021.1.0 (2021-01-06)
---------------------

- Introduces a new solr-index 'getObjPositionInParent' for tasktemplates, todolists and todos. [elioschmutz]
- Prevent attempts to edit locked documents in Office Online. [tinagerber]
- Add feature flag for workspace meetings. [tinagerber]
- Do not allow to modify the participations of a dossier via @participations endpoint if dossier cannot be modified. [tinagerber]
- Fix unicode error in meeting overview. [njohner]
- Disable grouping on Subject column. [njohner]
- Add invitation_group_dn to teamraum policy template. [njohner]
- Actions for document templates are properly configured. [elioschmutz]
- Add unlock file action. [tinagerber]
- Allow removal of copied_to_workspace locks via the @unlock API endpoint by users other than the creator. [tinagerber]
- Add @lock expansion. [tinagerber]
- Bump ftw.solr to 2.9.1 to fix a bug with indexing of SearchableText. [njohner]
- Add solr functional tests. [njohner]
- Allow downloading and sending a document checked out by another user. [elioschmutz]
- Adding a subtask to a sequential task through the restapi respects the `position` parameter [elioschmutz]
- Fix keyword filter for keywords that contain spaces. [tinagerber]
- Fix deletion of favorites when object is removed or trashed. [njohner]
- Add @assign-to-dossier rest-api endpoint to assign a forwarding to a dossier [elioschmutz]
- Add public_trial field to listing endpoint. [tinagerber]
- Add feature flag for todos. [tinagerber]
- Only expose translated title fields for active languages in schema and serialization via API. [deiferni]
- No longer zip-export empty tasks, prevent creation of empty folders in such cases. [deiferni]
- Add sequence_type to task serializer. [tinagerber]
- Fix only rendering allowed proposal templates when proposal add form is opened from documents tab. [deiferni]
- Add OGDS sync for local groups. [buchi]
- Fix type of file contentType on eCH0147 import. [buchi]
- Implement faceting for OGDS based listings in general and for the globalindex endpoint in particular. [buchi]
- Setup placeful workflow for workspace root in default content. [buchi]


2020.15.1 (2020-12-03) does not include 2020.14.6
-------------------------------------------------

- Added a field to the solr sync chain so that PDF documents can be displayed in RIS [sebastianmanger]


2020.15.0 (2020-12-03) does not include 2020.14.6
-------------------------------------------------

- Support transferring documents from workspace back to GEVER as new version. [lgraf]
- Add @teamraum-solrsearch endpoint to search on a connected teamraum deployment. [tinagerber]
- Add @link-to-workspace endpoint to link a dossier to an existing workspace. [tinagerber]
- Set linked dossier oguid as external_reference for linked workspaces. [tinagerber]
- Mark dossiers with an interface as soon as they are linked to a workspace. [tinagerber]
- Ignore locking mail when making a copy via Teamraum Connect. [njohner]
- Allow locking document when making a copy via Teamraum Connect. [njohner]


2020.14.6 (2021-01-08)
----------------------

- Do not update touched date of children when moving an object. [njohner]


2020.14.5 (2020-12-03)
----------------------

- Added a field to the solr sync chain so that PDF documents can be displayed in RIS [sebastianmanger]


2020.14.4 (2020-12-01)
----------------------

- Correct upgrade: fix only subscription on ToDos of current admin unit. [njohner]


2020.14.3 (2020-12-01)
----------------------

- Correct bug with watchers being wrongfully added to ToDos. [njohner]


2020.14.2 (2020-11-24)
----------------------

- Fix StatelessScriptUpdateProcessor for documents. [Kevin Bieri]


2020.14.1 (2020-11-20)
----------------------

- Fix persistence bug in linked documents storage. [lgraf]
- Cast value of issuer to actor label in listing and search endpoints. [tinagerber]
- Translate proposal review states. [tinagerber]


2020.14.0 (2020-11-19)
----------------------

- Provide a StatelessScriptUpdateProcessor to sync solr documents to a remote solr. [Kevin Bieri]
- Prevent documents from being copied to workspace when checked out. [lgraf]
- Link documents copied via Teamraum Connect. [lgraf]
- Use a dedicated endpoint to upload document copy to workspace. [lgraf]
- No longer exclude trashed documents in @listing-stats endpoint. [tinagerber]
- Add @notification-settings API endpoint. [tinagerber]
- Use UID instead of intId as token in DocumentTemplatesVocabulary. [elioschmutz]
- Add simple support for meetings in a multi-admin-unit cluster. [deiferni]
- A closed dossier does no longer provide the `move_items` and `move_proposal_items` folder button actions [elioschmutz]
- Disable action to move document within a closed dossier. [elioschmutz]
- Fix an encoding error on the local contacts tab. [deiferni]
- Prevent notification mails being bounced due to blacklisted URL in comment. [deiferni]
- Enhance policy generator with some more defaults for SaaS GEVER. [deiferni]
- Add support for using the msgconvert service instead of a locally installed msgconvert. [buchi]
- Add support for using the sablon service instead of a locally installed sablon. [buchi]
- Add support for using the pdflatex service instead of a locally installed pdflatex. [buchi]
- Add GEVER_COLORIZATION to the configuration endpoint. [2e12]
- Add flag to disregard retention period when creating a disposition. [deiferni]
- Optimize OGDS Sync. [buchi]
- Fix getting group members from AD in OGDS sync if group contains more than 1500 members. [buchi]


2020.13.0 (2020-11-05)
----------------------

- Convert bytestring values for IOpengeverBase.description field to unicode instead of raising an error. [elioschmutz]
- Fix resolving subdossiers when Teamraum Connect feature is enabled. [lgraf]
- Fix the Workspace `@participations` endpoint for NullActors. [njohner]
- Delete old upgrade steps up to and including 2018.5.7. [njohner]
- Add monkey-patch to track out of sync modified. [deiferni]
- Agenda-item attachments are now ordered based on the position in the relationField. [elioschmutz]
- Remove the limit for facets returned in the listing API endpoint. [Kevin Bieri]
- `@actions` endpoint also returns available webactions. [elioschmutz]
- Use oguid instead of intId as token in DossierTemplatesVocabulary. [tinagerber]
- Use UID instead of intId as token in DossierTemplatesVocabulary. [tinagerber, elioschmutz]
- `@@task_report`-view supports task lookup by the ressource-id through the `tasks` parameter. [elioschmutz]
- Ensure `document_author` and `SearchableText` indices are dropped from catalog. [deiferni]
- Add @actors endpoint allowing retrieve the data for actor IDs. [njohner]
- Extend @config endpoint with application type. [tinagerber]
- Journalize creation of linked workspace and copying documents to and from it. [njohner]
- Disable write actions during readonly mode. [lgraf]
- Custom error page: Also log ReadOnlyError culprit traceback to error log (if available). [lgraf]
- Avoid ftw.casauth write-on-read (last login times) during login. [lgraf]
- Expose bumblebee notifications url in the config endpoint. [Kevin Bieri]
- Bump ftw.tabbedview to 4.2.1 to get fix for empty action lists. [lgraf]
- Add workspacemeetings to @listing endpoint. [tinagerber]
- Fix order of labels for participations field in the listing endpoint. [njohner]
- Add script to toggle read-only mode in zope.conf. [buchi]


2020.12.0 (2020-10-22)
----------------------

- Make is_in_readonly_mode() slightly more robust. [lgraf]
- Show traceback on ReadOnlyError page to all users, not just managers. [lgraf]
- Don't create journal entry when downloading file copy in readonly mode. [lgraf]
- Create Bumblebee user salt on login. [lgraf]
- Patch several login-related events to allow login during readonly mode. [lgraf]
- Implement `sort_first` parameter in the `@listing` endpoint. [elioschmutz]
- Add workspace meeting content type. [tinagerber]
- Add optional support for WriteOnRead tracing in ReadOnlyError page. [lgraf]
- Add videoconferencing URL to workspaces. [deiferni]
- Add a new listing field: creator_fullname. [elioschmutz]
- Add a new listing: `folder_contents` to the @listing endpoint. [elioschmutz]
- Use custom error page for ReadOnlyErrors. [lgraf]
- Disable GZip compression in p.a.caching. [lgraf]
- Add viewlet that shows a message to indicate readonly mode. [lgraf]
- Add is_readonly flag for @config endpoint and @@gever_state view. [lgraf]
- Add @dossier-from-template endpoint. [tinagerber]
- Activate the groups plugin for source_groups. [elioschmutz]
- Add @possible-participants endpoint. [tinagerber]
- Add support for participations in listing endpoint. [njohner]
- Also provide main_dossier for dossiertemplates [elioschmutz]
- Allow assigning groups as participants to a Teamraum [elioschmutz]
- Add external_reference field to solr, reindex objects with values. [deiferni]
- Provide empty MS Office templates for new deployments. [2e12]
- Fix mimetype for quickupload with custom mimetypes. [buchi]


2020.11.1 (2020-10-09)
----------------------

- Add and index PHVS specific fields in solr. [njohner]


2020.11.0 (2020-10-07)
----------------------

- GET @groups endpoint is now available with the `opengever.api.ManageGroups` permission. [elioschmutz]
- Bump docxcompose to 1.3.0 to support updating complex properties with no existing value. [deiferni]
- @ogds-users, @ogds-groups, @ogds-user-listing and @ogds-group-listing are now registered on the plone siteroot instead the contact-folder. [elioschmutz]
- Add dossiertemplates, tasktemplates and tasktemplatefolders to @listing endpoint. [tinagerber]
- No longer prevent adding documents with doc-property update issues. [deiferni]
- Add tasktemplates and tasktemplatefolders to @listing endpoint. [tinagerber]
- Bump `ftw.catalogdoctor` to `1.2.0` which provides fixes for additional health problems. [deiferni]
- Prevent setting invalid reference prefix number via API. [deiferni]
- Remove IDossier baseclass from IDossierTemplate to fix API for dossier templates. [njohner]
- Customize the group_data serializer to return summarized users instead of only userids. [elioschmutz]
- Extend the ogds-group serializer with a `groupurl` property. [elioschmutz]
- Implement new api endpoint @ogds-group-listing. [elioschmutz]
- Add @participations API endpoint for dossiers to CRUD participations. [tinagerber]
- Do not allow to add multiple participations for one contact. [tinagerber]
- Don't resolve or deactivate a dossier if it is linked to an active workspace. [tinagerber]
- Provides the IVocabularyTokenized interface for elephant vocabularies. [elioschmutz]
- Customize @groups endpoints to handle OGDS. [njohner]
- Add Cadwork mimetypes and enable editing with Office Connector. [buchi]


2020.10.0 (2020-09-25)
----------------------

- Bump plone.restapi to 6.14.0 to get fix for bytestring ordering. [deiferni]
- Fix `status` API endpoint for mails. [deiferni]
- Do not allow to manage security in deactivated workspaces. [tinagerber]
- API change: Add current_user to @config endpoint and remove userid, user_fullname and user_email. [tinagerber]
- Fix globalindex endpoint for undefined sort orders. [njohner]
- Fix ogds listing endpoints for undefined sort orders. [njohner]
- Populate filename for favorites where previous upgrades failed. [deiferni]
- Add move item action. [tinagerber]
- Not only documents, but also mails in tasks and proposals may not be moved. [tinagerber]
- Include is_subdossier and review_state in @navigation endpoint nodes. [elioschmutz]
- Order groups and teams in User serializer by title. [elioschmutz]
- Do not allow @tus-replace if document is not checked out by current user. [buchi]
- Fix workspace workflows: Allow to create new document versions and to trash documents again. [buchi]
- Add missing translations for dossier export. [2e12]
- Replace Chatlio in docs with HubSpot Chat. [2e12]


2020.9.0 (2020-09-10)
---------------------

- Bump ftw.monitor to get bin/dump-perf-metrics script. [lgraf]
- Correctly handle query strings for oguid on remote admin units in ResolveOGUIDView. [njohner]
- Add @successors and @predecessor expansion for tasks. [deiferni]
- Don't show workspace actions for non-open dossiers or when the user can only view. [deiferni]
- Add @share-content endpoint to share content in workspace. [tinagerber]
- Add @actual-workspace-members endpoint. [tinagerber]
- Add support for transferring inter-admin-unit tasks. [lgraf]
- Fix resolving favorites that don't exist. [tinagerber]
- Prevent deadlock when reassigning inter-admin-unit tasks. [lgraf]
- Preserves the query string for the redirect_to_parent_dossier view. [elioschmutz]
- Preserves the query string for the redirect_to_main_dossier view. [elioschmutz]
- Adjust the policy generator for easier policy generation. [elioschmutz]
- Provide create_forwarding action in API for documents in inboxes. [deiferni]
- Allow to query by token in @querysources API endpoint. [deiferni]
- Fix escaping solr literal queries. [deiferni]
- Consider cookie when figuring out current orgunit in AllUsersInboxesAndTeamsSource. [deiferni]
- Fix forwarding requiring task_type in API, fix forwarding task_type translations. [deiferni]
- Add @type to @globalindex items, figure out portal type from task type. [deiferni]
- Add option to deactivate a workspace. [buchi]


2020.8.1 (2020-09-07)
---------------------

- Revert adding missing value for public_trial_statement. [njohner]


2020.8.0 (2020-08-26)
---------------------

- Filter out owner role in role assignment reports. [tinagerber]
- Fix translated review state for meeting content. [lgraf]
- Bring @resolve-oguid error responses in line with REST API style. [lgraf]
- Introduce POST @complete-successor-task on tasks. [lgraf]
- Introduce POST @accept-remote-task endpoint for dossiers. [lgraf]
- Introduce POST @remote-workflow endpoint. [lgraf]
- Role Assignment Reports: Ensure stable sort order for report items. [lgraf]
- Fix dossier template description, ensure unicode. [deiferni]
- Add policy template for teamraum policies. [njohner]
- Fix filtering with exclusion filters if the field has a mapping. [tinagerber]
- Make the portal_url configurable through the portal_registry. [elioschmutz]
- Include OGUID in all API content GET responses. [lgraf]
- Reindex modified containers after bundle import. [njohner]
- Extend the @config endpoint with the current inbox_folder_url. [elioschmutz]
- Complement @role-assignment-reports responses with type, principal label, title and referenced roles. [tinagerber]
- Add another nesting level to simple saas policy templates. [deiferni]
- Add missing inboxes for multi orgunit setups in the examplecontent fd profile and testing fixture [elioschmutz]
- Fix WOPI version if object is a ghost. [buchi]
- Implement WOPI proof key validation. [buchi]


2020.7.0 (2020-08-12)
---------------------

- Add support for importing teamraum bundles. [lgraf]
- Also reindex searchable text of dossier when migrating responsible user. [njohner]
- Use filing_no field in advanced search form. [njohner]
- Reindex SearchableText when filing number is set. [njohner]
- Bump `ftw.solr` to treat docs with no `created` field as out of sync. [deiferni]
- Handle search queries in GlobalIndexGet endpoint. [njohner]
- Add @resolve-oguid endpoint. [deiferni]
- Include oguid in @notifications endpoint. [deiferni]
- Extend @globalindex endpoint, avoid duplicate tasks, add batching information. [deiferni]
- Add upgrade to fix docs only partially indexed in solr. [deiferni]
- Extend @config with admin-unit and org-unit. [njohner]
- Add mail-in address and inbox_id to inbox serializer. [njohner]


2020.6.0 (2020-07-29)
---------------------

- Improve policy creation. [tinagerber]
- Always return @id in navigation endpoint when not expanding. [njohner]
- Allow deletion of documents only if they are in the trash. [tinagerber]
- Add portal_url to configuration endpoint and view. [njohner]
- Fix transitions via @workflow service when executing user has no permission in target state. [tinagerber, deiferni]
- Fix id normalization when setting up a repository. [tinagerber]
- Fix createContentInContainer to respect behaviors. [njohner]
- Add watchers solr field and indexers, currently for tasks only. [deiferni]
- Allow workspace members to trash, untrash and delete documents in workspaces. [tinagerber]
- Handle wildcard in date filters in listing endpoint. [njohner]
- Handle multiple content interfaces in @navigation endpoint. [njohner]
- Handle errors in solrsearch endpoint. [njohner]
- Enhance WOPI implementation for Office 365 support. [buchi]


2020.5.0 (2020-07-14)
---------------------

- Change french translation of private root. [tinagerber]
- Add @role-assignment-reports endpoint to list, add and delete role assignment reports. [tinagerber]
- Nullify text docproperties in word files when updating instead of deleting them. [deiferni]
- Overwrite logout API endpoint to also expire the user's cookies. [njohner]
- Translate activities in @notifications endpoint. [njohner]
- Fix contact workflow state variable name. [deiferni]
- Fix contact folder workflow state variable name. [deiferni]
- Expose the current logged in users'email address in the @config endpoint. [elioschmutz]
- Improve design and content of workspace invitation e-mail. [mbaechtold]
- Fix filtering on values containing spaces in listing endpoint. [njohner]
- Add question for `administrator_group` to the policy template. [mbaechtold]
- Add teaser viewlet to promote the new frontend. [tinagerber, njohner]
- Fix loading of more items in contenttree widget for toplevel items. [buchi]
- Add UserSnap API key to registry. [njohner]


2020.4.1 (2020-07-09)
---------------------

- Fix update mail filename upgrade step. [njohner]


2020.4.0 (2020-07-02)
---------------------

- Improve check if solr has started to prevent an issue during the testserver startup. [sebastianmanger]
- Make creating favorites more robust in case of workflow issues. [deiferni]
- Improve response history for (automatically) opened subtasks in sequential task templates. [mbaechtold]
- Fix contenttree.js so that it is also supported by IE. [njohner]
- Expose the url to the user's private folder in the `@config` API endpoint. Serves as feature flag too. [mbaechtold]
- Also allow replacing concrete responsibles with interactive responsibles when triggering task templates. [deiferni]
- Remove cross-tab logout functionality. [lgraf]
- Add @@logout view to clear Plone session and redirect to CAS logout if necessary. [lgraf]
- Introduce a new property `touched` on dossiers. [mbaechtold]
- Add support for metadata_fields in OpengeverRealContentListingObject. [njohner]
- Fix linking to proposal/submitted proposal from documents in various places. [deiferni]
- Fix sort order within task template folder. [mbaechtold]
- Fix deadline of task templates no longer shown in tabular listing. [mbaechtold]
- Fix permission issue with resolving subtask of tasktemplates. [njohner]
- Add API expansion `main-dossier`. [mbaechtold]
- Make "populate_filename_column_in_favorites" UpgradeStep more robust. [lgraf]
- Disable the searchbox on the tabbed view which lists the versions of a document. [mbaechtold]
- Include additional data in @responses GET for proposal responses. [njohner]
- Include additional data in Proposal GET API endpoint. [njohner]
- Allow `trashed` as field in @listing endpoint. [tinagerber]
- Add API endpoint `@trigger-task-template` to create tasks in a dossier from a template. [deiferni]
- Extend the @favorites endpoint to let it return already resolved favorites. [elioschmutz]
- Use correct response type for proposal comment responses. [njohner]
- Add expandable endpoint @tasktree for getting task hierarchy. [buchi]
- Also normalise filename of original_message when present. [tinagerber]


2020.3.0 (2020-06-18)
---------------------

- Bump setuptools to 44.1.1 and zc.buildout to 2.13.3. [tinagerber]
- Update translations of error messages when moving objects. [tinagerber]
- Allow filtering for empty strings in @listing endpoint. [tinagerber]
- Allow negation of a filter query in @listing endpoint. [tinagerber]
- Implement batching for the @solrsearch endpoint. [elioschmutz]
- Fix contact query sources for contacts without an E-mail. [njohner]
- Make available the delete action for templates. [mbaechtold]
- Drop import_stamp column from user model. [tinagerber]
- Define a set of columns that get synchronized in user and group model. [tinagerber]
- Handle depth filter in solrsearch endpoint. [njohner]
- Add OGDSGroupActor class. [njohner]
- Explicitly log to sentry for two `ftw.solr` modules we want to monitor well at the moment. [deiferni]
- Add @transfer-task endpoint to change issuer and responsible of a task. [tinagerber]
- Add possibility to suppress notification with X-GEVER-SuppressNotifications header. [tinagerber]
- Add @assigned-users endpoint to get all active users of the client. [tinagerber]
- Set Reply-To header from mails sent on behalf of users. [lgraf]
- Avoid sending mails with From-Addresses other than our own. [lgraf]
- Fix bug with setting issuer and informed_principals on forwardings. [njohner]
- Allow notifying users and groups when creating a new task. [njohner]
- Add last login information to user. [tinagerber]
- Bump ftw.casauth to 1.3.0 to handle login similar to PlonePAS in @caslogin endpoint. [tinagerber]
- Enable API endpoint `@document-from-template` for tasks. [mbaechtold]
- Support combined notation for task responsible in workflow transitions. [elioschmutz]
- Bump docxcompose to 1.1.2 to fix issues with external image references and drawing properties. [buchi]
- Always use configured solr port in tests. [2e12]
- Fix translations of task types in API GET. [2e12]
- Allow customizing group dn for invitations. [buchi]


2020.3.0rc4 (2020-06-05)
------------------------

- Move the ogds groups import logger more up in the script to make debugging easier. [elioschmutz]
- Add `bumblebee_app_id` to the `@config` API endpoint. [mbaechtold]
- @teams: Order team members by last name. [lgraf]
- @ogds-groups: Order group members by last name. [lgraf]
- Bump ftw.solr to 2.8.6 to get logging improvements and filter helpers. [lgraf]
- Support placeholders in the target url of the webactions. [mbaechtold]
- Fix the upgradestep to merge notification settings from release 2020.3.0rc2 to use it's own configruation copy to not depend on future adjustments. [elioschmutz]
- Add @extract-attachments endpoint to extract mail attachments. [njohner]
- Only allow to extract each mail attachment once. [njohner]
- Do not allow deleting mail attachments anymore. [njohner]
- Rename @team API endpoint to @teams. [tinagerber]
- Avoid object lookup in DocumentLinkWidget for Solr documents and catalog brains. [buchi]
- Improve contenttree widget in handling a large amount of items. [buchi]
- Rename @ogds-user API endpoint to @ogds-users. [tinagerber]
- Update ftw.testing to version 1.20.2. This improves the performance of the testserver significantly. [buchi]
- Rename `users` attribute of @teams endpoint to `items`. [tinagerber]
- Add batching for ogds team and group serializer. [tinagerber]
- Extend @sharing endpoint with ogds_summary. [tinagerber]
- Add @ogds-groups API endpoint. [tinagerber]
- Implement custom RoleAssignmentManager based local role migration for ftw.usermigration. [deiferni]
- Fix batching in OGDSListingBaseService, properly use SQLHypermediaBatch. [deiferni]
- Remove various unneeded catalog indexes and metadata columns. [buchi,elioschmutz,mbaechtold]
- Use Solr to get documents and dossier navigation in dossier overview. [buchi]


2020.3.0rc3 (2020-05-22)
------------------------

- Assign permission to role "ServiceKeyUser". [mbaechtold]
- Bump ftw.structlog to 1.3.0 to get SQL query time and view name logging. [lgraf]
- Notify added watchers. [tinagerber]
- Limit query to current repository in RepositoryPathSourceBinder. [njohner]
- Improve performance of the subdossier tree (on the dossier overview tab). [mbaechtold]
- Truncate overflow in keyword and other selection choices. [2e12]
- Improve performance while determining repositoryfolder emptiness. [mbaechtold]
- Improve performance while determining leaf nodes. [mbaechtold]
- Add watcher role to task notification setting tab. [tinagerber]
- The widget used to select users or groups while protecting a business dossier now respects the sharing configuration. [mbaechtold]
- Fix an issue where solr facet labels have not been transformed correctly. [elioschmutz]
- Skip unknown attributes in POST @invitation endpoint. [elioschmutz]
- Add watchers, resources and subscriptions to tasks and forwarding in fixtures. [tinagerber]
- Fix activity bug when creating tasks with tasktemplates. [tinagerber]
- Add basic support for xlsx sources to bundle factory. [deiferni]
- Add new filename column to Favorites. [njohner]
- Implement @possible-watchers endpoint. [elioschmutz]
- Fix dossier link in chrome. [2e12]
- Add `is_admin_menu_visible` to the `@config` API endpoint. [mbaechtold]
- Watchers GET API: Also include info about referenced_users and referenced_watcher_roles. [tinagerber]
- Fix @solrsearch endpoint default sort order. [elioschmutz]
- Bump ftw.bumblebee to 3.9.0 which provides functionality for indexing checksums after bundle import. [buchi]


2020.3.0rc2 (2020-05-07)
------------------------

- Drop sorting by sortable_author for solr and avoid handling sorting parameters as fields. [deiferni]
- Add live chat to online documentation. [njohner]
- Bump ftw.monitor and ftw.contentstats to get performance metrics. [lgraf]
- Merge notification settings for tasks. [elioschmutz]
- Add more metadata to response of favorites endpoint (`review_state`, `is_subdossier` and `is_leafnode`). [mbaechtold]
- Improve performance when resolving large dossiers. [deiferni]
- Add attributes `review_state`, `is_subdossier` and `is_leafnode` to the search results returned by `@solrsearch` and `@livesearch`. [mbaechtold]
- Add attribute `is_subdossier` to the children for GET requests to the API. [mbaechtold]
- Add is_subdossier to catalog metadata. [deiferni]
- Add @watchers endpoint for tasks and inbox forwardings. [tinagerber]
- Fix show proposal templates corresponding to the committee. [2e12]
- Add Bumblebee auto refresh feature to policy template. [2e12]
- Task GET API: Also include info about containing dossier. [mbaechtold]
- Enhance the API endpoint `@breadcrumbs` with more attributes. [mbaechtold]
- Add key `is_leafnode` to the API endpoint `@navigation`. [mbaechtold]
- Fix `task_type_helper` to respect the current language for the ram-cache. [elioschmutz]
- Always use Solr for tabbedview listings. [buchi]
- Enable Solr by default. [buchi]
- Fix exclusion of search root when using Solr. [buchi]
- Add retention_expiration to Solr schema. [buchi]
- Add support for date range queries using Solr. [buchi]
- Add support for contact lookup by email2 using Solr. [buchi]
- Fix title format in OGDS UsersContactsInboxesSource using Solr. [buchi]
- Fix indexing of documents in Solr integration tests. [buchi]
- Avoid filtering or sorting on fields that do not exist in Solr. [buchi]
- Implement pagination for Solr based listings. [buchi]
- Fix bug in table source of trashed documents when using solr. [njohner]
- Fix bug in search view not respecting batch size when solr is deactivated and change default batch size with Solr to 25. [njohner]
- Extend the ftw.mail.mail workflow with teamraum specific roles. [elioschmutz]
- Extend the `meeting.json`, which will be generated for an exported meeting, with a `agenda_item_list` property which contains a link to the agenda item list document. [elioschmutz]
- Add @allowed-roles-and-principals API endpoint (callable on every context) to get the information which roles, groups or users are allowed to view an object. [tinagerber]
- Extend @users endpoint with roles_and_principals. [tinagerber]


2020.3.0rc1 (2020-04-09)
------------------------

- Fix solr indexing bug when creating a document from a template. [njohner]


2020.2.6 (2020-06-09)
---------------------

- Add special handling for signed/multipart message attachments. [deiferni]
- Bump ftw.mail to 2.7.0 for signed/multipart handling. [deiferni]
- Fix p7m attachment extraction from mails. [deiferni]
- Bump ftw.mail to 2.6.2 to get improved email header decoding. [mbaechtold]


2020.2.5 (2020-05-06)
---------------------

- Bump ftw.solr to 2.8.5 to ensure solr maintenance scripts are run as system user. [njohner]


2020.2.4 (2020-05-04)
---------------------

- Bump docxcompose to 1.1.1 for non-ascii binary_type docproperty fix. [deiferni]
- Bump docxcompose to 1.1.0 for header/footer docproperty support. [deiferni]


2020.2.3 (2020-04-04)
---------------------

- Revert always using the `mail_from` for notifications, this breaks customers auto-reply use case. [deiferni]


2020.2.2 (2020-04-03)
---------------------

- Do not show OC checkout and edit buttons when user is in EMM environment. [njohner]
- Prevent documents being edited in Office Online from getting opened in OfficeConnector. [lgraf]
- Add @listing-stats API endpoint to get statistical data from folderish content. [elioschmutz]
- Fix public documentation build. [elioschmutz]


2020.2.1 (2020-03-27)
---------------------

- Backdate AddHiddenFlagToAdminAndOrgUnit upgrade step. [njohner]


2020.2.0 (2020-03-24)
---------------------

- Prevent attempts to edit exclusively checked out documents in Office Online. [lgraf]
- Do not allow to choose inbox of hidden OrgUnit as responsible in forwardings. [njohner]
- Change container title format in task activities. [njohner]
- Disable OfficeOnline action on docs in resolved or inactive dossiers. [lgraf]
- Add hidden flag to OrgUnits and AdminUnits. [njohner]
- Disallow choosing hidden orgunits as responsible_client in tasks and forwardings. [njohner]
- Do not display hidden orgunits in orgunit selector. [njohner]
- Disable regular checkout and edit actions for documents currently being edited in Office Online. [lgraf]
- Add 'Edit in Office Online' file action button in classic UI. [lgraf]
- OfficeOnline: Show specific message for collaborative checkouts. [lgraf]
- Document GET API: Also include info about collaborative checkouts. [lgraf]
- Also return @id in globalindex endpoint. [njohner]
- Extend the document serialization with `checked_out_fullname`. [elioschmutz]
- Add a new profile to setup a cas auth plugin for the ianus portal. [elioschmutz]
- Return actual data in TeamGet and UserGet. [njohner]
- Fix encoding issue in query-source `query` parameter. [deiferni]
- Do no longer send activity mails from the current user due to spam issues when the user's email address does not match the portal domain. [elioschmutz]
- OfficeOnline: Use collaborative checkout / checkins. [lgraf]
- Add list workspaces action for new frontend. [njohner]
- Add additional fields to @user-listing endpoint. [njohner]
- Add ogds user listing via @user-listing endpoint. [deiferni]
- Add ogds team listing via @team-listing endpoint. [deiferni]


2020.2.0rc1 (2020-03-11)
------------------------

- Extend the @config endpoint with an `apps_url` attribute. [elioschmutz]
- Extend policytemplates to use the single thread setup. [elioschmutz]
- Extend policytemplates with workspace deployment. [elioschmutz]
- Extend policytemplates with gever-ui activation. [elioschmutz]
- Add API service to create document from template. [deiferni]
- Restrict `geverui` cookie to admin unit. [elioschmutz]
- Extend the opengever deployment directive with workspace roles. [elioschmutz]
- Add API endpoint to copy documents from a workspace. [njohner]
- Add API endpoint to list documents in linked workspace. [njohner]
- Allow copying mails to linked workspace. [njohner]
- Set seen_tours for all users in test fixture. [njohner]
- Add support for Office Online aka WOPI. [buchi]


2020.1.0 (2020-02-26) does not include 2019.6.4
-----------------------------------------------

- Add smoke tests for rewrite rules and VHost configs. [lgraf]
- Add container title to task activities. [njohner]
- Set document_date and changed in bundle factory. [njohner]
- Handle changed and modified in ogg bundles. [njohner]
- Allow Administrators to add new keywords. [njohner]
- Implement @copy-document-to-workspace endpoint. [elioschmutz]
- Assign correct role Reader to reader_group. [deiferni]
- Allow administrators to deactivate dossiers. [njohner]
- Add permission and role to use the workspace Client. [njohner]
- Add french titles for initial content in the policytemplate. [phgross]
- Enable the solr flag in the policytemplate. [phgross]
- Implement @linked-workspaces endpoint. [elioschmutz]
- Implement @create-linked-workspace endpoint. [elioschmutz]


2020.1.0rc2 (2020-02-11)
------------------------

- Use Teamraum in mail header for invitations. [njohner]
- Integrate related workspaces to dossiers. [elioschmutz]
- Implement the teamraum client authentication flow. [elioschmutz]
- Implement the workspace client to make requests to a teamraum from GEVER. [elioschmutz]
- Implement the workspace client authentication flow. [elioschmutz]
- Handle deployments with no repository in navigation endpoint. [njohner]
- Only return create_task in actions endpoint on dossiers and tasks. [njohner]
- Fix JS ordering issue again. [njohner]
- Add documentation for sharing endpoint. [njohner]
- Always request UID from solr, as it is needed for snippets. [njohner]
- Speed up validation of dossier resolution preconditions. [njohner]
- Generally disallow to move proposals outside of its main dossier. [elioschmutz]
- Add tabbedview move action for proposals. [elioschmutz]


2020.1.0rc1 (2020-01-30)
------------------------

- Fix JS ordering issue: define overlayhelpers.js position. [njohner]
- Add French API and admin documentations. [njohner]
- Fix volatile related proposal documents. [elioschmutz]
- Add a button to create a task from a proposal. [elioschmutz]
- Allow to unlock and edit submitted documents in a submitted proposal. [elioschmutz]
- Add new_document_from_task file_action. [lgraf]
- Implement PossibleWorkspaceFolderParticipantsVocabulary to get all possible workspace folder participants. [elioschmutz]
- Implement GET, PATCH and POST @participations endpoint for workspace folders. [elioschmutz]
- Implement @role-inheritance serivce endpoint for workspace folders. [deiferni]
- Include permissions.zcml of Products.CMFEditions. [lgraf]
- Add action to create new invitations to workspaces. [deiferni]
- Return creator of workspace in GET, make sure he is a WorkspaceAdministrator upon workspace creation. Get rid of WorkspaceOwner role. [deiferni]
- Allow invitations to external users through E-mails. [njohner]
- Update invitation and participation GET json response format. [deiferni]
- Add missing french translation for example repository root. [elioschmutz]
- Always use API for OfficeConnector. [njohner]
- Refactor solrsearch and listing endpoints. [njohner]
- Add tests for solrsearch and listing endpoints. [njohner]
- Split invitations from participations endpoints. [njohner]
- Make and enforce unicode for webaction owner and groups. [njohner]
- Implement testing against a real Solr. [lgraf]
- Sharing on workspace folders should always show workspace users. [njohner]
- Replace @participations endpoint with @invitations endpoint accepting slightly different parameters. [deiferni]


2019.6.4 (2020-04-02)
---------------------

- Bump ftw.solr version to 2.8.4 to get update of modified index. [njohner]
- Bump ftw.solr version to 2.8.2 to get fix for millisecond rounding error. [njohner]
- Fix solr complex search pattern configuration. [deiferni]


2019.6.3 (2020-02-06)
---------------------

- Bump ftw.solr to 2.8.1 for to_iso8601 fix for years before 1900. [deiferni]
- Handle path depth when filtering a table. [njohner]


2019.6.2 (2020-01-29)
---------------------

- Add upgrade step to correct public_trial_statement type. [njohner]


2019.6.1 (2020-01-26)
---------------------

- Add 'filing_no' field to Solr schema. [lgraf]
- Fix to reassign a task to a new inbox group. [elioschmutz]
- When tearing down test layer, wait for solr to be torn down properly. [siegy]
- Configure Solr replication handler. [buchi]


2019.6.0 (2020-01-09)
---------------------

- Update Solr to version 8.4.0. [buchi]


2019.5.0 (2019-12-10)
---------------------

- Bump ftw.solr to 2.8.0 to get support for uploading blobs. [lgraf]
- Add custom IWarmupPerformer to also warm up GEVER's trashed index. [lgraf]


2019.5.0rc1 (2019-12-03)
------------------------

- Make Period a proper plone content type. Migrate old SQL base periods. [deiferni]
- Restrict available users in sharing on workspaces and workspace folders. [njohner]
- Correct styling bug fix in tabbedview after showing bumblebee tooltip. [njohner]


2019.4.2 (2019-11-29)
---------------------

- Register virtual host monster on site setup for testserver [bierik]
- Catch oneoffixx api calls failures and show statusmessage instead. [phgross]
- Fix setting agenda item description. [deiferni]
- Fix automatic start of additionally added sequential tasks. [phgross]
- Fix styling bug in tabbedview after showing bumblebee tooltip. [njohner]
- Only show workspace notification tab when feature is activated. [njohner]
- Fix response text for responsible changes to the same user. [phgross]
- Do not manipulate the persisten journal list on @history get. [phgross]
- Fix authorization handling when fetching the template_group_id. [phgross]
- Do not add document modified journal entry when saving file with OC RESTAPI. [njohner]
- Do not manipulate the persistent journal list on @journal get. [phgross]


2019.4.1 (2019-11-26)
---------------------

- Update French translations. [njohner]
- Update oneoffixx intergration to latest API changes. [phgross]


2019.4.0 (2019-11-22)
---------------------

- Pin ftw.monitor to 1.0.0. [lgraf]
- Allow teams as task responsible when delegating a task. [phgross]
- Fix contentlisting and API summary for documents inside tasks. [phgross]
- Also return facet labels in solrsearch endpoint. [njohner]
- Fix fallback to default sorting index in listing endpoint. [njohner]
- Display returned documents in the task-resolved history entry. [phgross]
- Fixes is already done check in multi admin unit tasks completion. [phgross]
- Fix @history patch endpoint to correctly revert to older document version. [njohner]
- Fix unicode error in @listing endpoint filters. [lgraf]
- Fix document serialization for older document versions. [phgross]
- Add main dossier count to contentstats. [njohner]
- No longer add journal entry for document file modification. [njohner]
- Revoke permissions for former responsible, when task gets rejected. [phgross]
- Use BaseResponse for proposal history to add API support. [njohner]
- Update oneoffixx integration with the latest oneoffixx api changes. [phgross]


2019.4.0rc5 (2019-11-13)
------------------------

- Bump ftw.keywordwidget to 2.1.2 to fix race condition when adding new keywords. [lgraf]
- Fix an issue with non-ASCII characters in proposal doc-properties. [deiferni]
- Add trash_document and untrash_document file_actions. [lgraf]
- Bump plone.restapi to 5.0.3 to get fix for filtering vocabs by non-ASCII titles. [lgraf]
- Add document creator metadata to available docproperties. [deiferni]
- Update the usersettings-serializer: A pure plone user has always seen all screens. [elioschmutz]
- Support combined notation for task responsible. [phgross]
- Fix an issue with todo(-list) ids not being stored as bytestring. [deiferni]
- Disallow mail upload as documents via API. [phgross]
- Update Products.LDAPUserFolder from 2.28.post2 to 2.28.post3. [elioschmutz]
- Extend dossier serializer with `is_subdossier`. [elioschmutz]
- Add @globalindex API endpoint. [phgross]
- Add proposals to @listing endpoint. [njohner]
- Remove catalog support for @listing endpoint. [elioschmutz]
- Moved reminder options vocabulary to globaly registered vocabulary. [phgross]
- Add a user action to switch to the new gever-ui. [elioschmutz]
- Add support for contacts to the @listing endpoint. [phgross]


2019.4.0rc4 (2019-10-22)
------------------------

- Preserve query string in the resolve notification view. [phgross]
- Add UID to listing endpoints supported fields. [phgross]
- Allow adding favorites by UID parameter via favorites endpoint. [phgross]
- Add UID to listing endpoints supported fields. [phgross]
- Allow adding favorites with UID parameter via favorites endpoint. [phgross]
- Bump ftw.keywordwidget version to fix missing titles on terms. [njohner]
- Allow text field in task deadline modification through API. [njohner]
- Make `issuer` filterable in the @lising endpoint. [elioschmutz]
- Implement absolute reminder dates in the reminder-selector. [elioschmutz]
- Fix mail deserialization for mails uploaded through tus-upload. [njohner]
- Downpin ftw.recipe.solr to 1.2.1 to have log4j configuration valid for solr < 7.4.X [deiferni]
- Use plone.restapi summary serialization in the recently-touched endpoint. [phgross]
- document_report: Add support for pseudo-relative paths. [lgraf]
- pdf-dossier-listing: Add support for pseudo-relative paths. [lgraf]
- dossier_report: Add support for pseudo-relative paths. [lgraf]
- zip_selected view: Add support for pseudo-relative paths. [lgraf]
- Fix a problem in the watcher handling when reassigning a task to the same user but a different org unit. [phgross]
- Support the bundle-import of mails in the msg format. [phgross]
- Add API endpoints for user-setings and add additional setting seen_tours. [phgross]
- Support the bundle-import of mails in the msg format. [phgross]
- Add API endpoints for user-setings and add additional setting seen_tours. [phgross]
- Extend @solrsearch endpoint by adding various useful information like item count, attributes from contentlisting objects, facets and snippets. [buchi]


2019.4.0rc3 (2019-10-02)
------------------------

- Add GET implementation for @reminder endpoint. [lgraf]
- Add new reminder type ReminderOnDate (backend only). [lgraf]
- Fix an issue with agenda item template ids not being stored as ascii. [deiferni]
- Bump ftw.bumblebee to 3.8.0 for p7m support. [deiferni]
- Add support for multipart/signed a.k.a. \*.p7m mails. [deiferni]
- Add documentation for the cancelcheckout endpoint. [njohner]
- Downgrade solr to 7.3.1.
- Bump plone.restapi to 4.5.1. [phgross]
- Use persistent-mapping for recently touched entries. [phgross]
- Harmonize datetimes in recently-touched endpoint. [phgross]
- Set proposal plone workflow state when submitted proposal state changes. Refactor remote calls so that there is only one request per state change. [deiferni]
- Render discreet workflow transition buttons and show warning/info messages on proposal overview when proposal document is checked out or committee has been deactivated.
- Bump ftw.solr to 2.7.0 to get console scripts for maintenance tasks. [deiferni]
- Validate task deadline modification through the rest-api if the user uses the same deadline as already set on the task. [elioschmutz]
- Bump ftw.solr to 2.6.2 to get fix for avoiding atomic updates with null-documents. [lgraf]
- Add example contentent for workspaces. [elioschmutz]
- Bump docxcompose to version 1.0.2. [njohner]
- Bump ftw.zipexport to include a bugfix to avoid doubled subfolders. [phgross]
- Change task specific response implementation to the new base response implementation. [elioschmutz]
- Handle creation of new proposals over the REST-API. [njohner]
- Introduce plone proposal workflow, provide api support for proposal workflow transitions. [deiferni]
- Always raise when viewlet rendering errors occur during development. [deiferni]
- Rename label and values of the privacy layer field. [phgross]
- Add configuration possibility, to blacklist mimetypes from archival conversion. [phgross]
- Do no longer render `None` value in document description. [elioschmutz]
- Integrate ToDos in GEVER-Notification-System. [njohner]
- Prevent copy / paste of checked out documents. [njohner]
- Add is_subdossier and is_subtask to listing endpoint. [njohner]
- Correctly handle inactive groups in the sharing view. [njohner]
- Drop custom model forms for proposals and create proposal model via event handler. [deiferni]
- Track changes in response objects for todo-types. [elioschmutz]
- Include original files in ech0160 SIP export even when archival_file exists. [njohner]
- Add filename and checked_out fields to recently-touched endpoint. [njohner]


2019.4.0rc2 (2019-08-21)
------------------------

- Introduce `IBaseProposal` class, `ISubmittedProposal` no longer inherits from `IProposal`. [deiferni]
- Move remaining proposal model fields to plone content type. [deiferni]
- Implement FTPSTransport for uploading SIPs to FTPS server. [lgraf]
- Display keywords in Mail overview. [njohner]
- Bump ftw.keywordwidget to 2.1.0 to use async mode of keyword widgets for document and dossier keywords. [njohner]
- Fix an issue where it was no longer possible to modify a workspace as a workspace owner. [elioschmutz]
- Fix workspace participation restapi to handle new payload format for post and patch requests due to the new plone.restapi. [elioschmutz]
- Add response support for ToDos. [phgross]
- Update workflow security for opengever_workspace workflow to fix permission on existing workspaces. [elioschmutz]
- Remove userid from the users fullname in all teamraum sources. [phgross]
- Move task reminders of responsibles to the successor, when accepting a multi admin unit task. [phgross]
- Bump ftw.tabbedview version to 4.1.3 [njohner]
- Add OGGBundle factory to create bundles from filesystem folders. [njohner]


2019.4.0rc1 (2019-08-08)
------------------------

- Implement SIP delivery via FilesystemTransport. [lgraf]
- Disallow deleting repository folders and roots except from the RepositoryDeleter. [njohner]
- Expose document actions in @actions endpoint in separate file_actions category. [njohner, deiferni]
- Nightly jobs: Add short -f option as alias for --force. [lgraf]
- Nightly jobs: Don't require ftw.raven when running locally [lgraf]
- Fix team actor profile_url for foreign users. [phgross]
- Include actor_id and actor_label in @notifications endpoint responses. [lgraf]
- Improve SIP package generation and download. [phgross]
- Fix qa tests. [lgraf]
- Disable properties action for teams. [deiferni]
- Add source vocabularies for workspace invitations and todo responsibles. [njohner]
- Add hard limit for number of todos in single workspace. [njohner]
- Enable c.indexing during tests, but patch it to not defer operations. [lgraf]
- Add teamraum todolist content-type. [phgross]
- Add teamraum todo content-type. [elioschmutz]
- Fix creation and handling for subtasks of sequential tasks. [phgross]
- Disable collective.indexing during bundle import. [buchi]
- Fix upgrade step that adds linguistic index for task principal. [lgraf]
- Add ftw.catalogdoctor to dependencies. [deiferni]
- Fix exception formatter patch when there is no plone site. [deiferni]
- @listing endpoint: Exclude searchroot from Solr results. [lgraf]
- Avoid reindexing 'created' during IObjectCopiedEvent to fix copy & pasting with Solr. [lgraf]
- Allow Readers, Member and Managers to access users information for all users. [phgross]
- @listing endpoint: Add support for filtering by relative path depth. [lgraf]
- Update plone.restapi to latest release. [phgross]
- Add optional facet values and counts search to listing endpoint. [njohner]
- Add POST restapi endpint @mworkspace-invitations/{id}/{action}. [elioschmutz]
- Add Solr support to testserver. [jone]
- Add GET restapi endpint @my-workspace-invitations. [elioschmutz]
- Allow range queries on deadline in listing endpoint. [njohner]
- Update and improve documentation for checked-out documents. [phgross, njohner]
- Add fields available in listing endpoint for each type to documentation. [njohner]
- Bump sablon to 0.3.1 and nokogiri to 1.9.1. [deiferni]
- Add restapi @participations endpoint to handle participations. [elioschmutz]
- Add per user configuration to deactivate inbox notifications. [njohner]
- Add linguistic index on task principal column for oracle backends. [phgross]
- Register ChoiceFieldDeserializer using overrides instead of configure ZCML. [lgraf]
- Update Creator, created and Date when copy/pasting an object. [njohner]
- Docs: Add tasks to documented content types. [lgraf]
- Add per user configuration to activate notifications for own actions. [njohner]
- Update ftw.solr to version 2.5.0 which allows near realtime searching. [buchi]
- Update Solr to version 8.1.1. [buchi]


2019.3.4 (2019-09-25)
---------------------

- Fix unicode error in listing endpoint. [njohner]


2019.3.3 (2019-09-11)
---------------------

- Bump docxcompose to version 1.0.2. [njohner]


2019.3.2 (2019-08-27) does not include 2019.2.7
-----------------------------------------------


- Handle special characters in link to advanced search. [njohner]
- Add new registry field to switch between changed and document_date for dossier end date calculation. [njohner]


2019.3.1 (2019-08-27) does not include 2019.2.7
-----------------------------------------------

- Bump ftw.solr to 2.6.1 to get fix path_depth handling. [phgross]
- Bump ftw.solr to 2.6.0 to get fix for metadata getting overwritten by extract handler. [lgraf]
- Bump ftw.bumblebee to 3.7.3 to get fix for indexing checksum in ftw.solr. [lgraf]
- Bump docxcompose version to 1.0.1 [njohner]


2019.3.0 (2019-06-17) does not include 2019.2.6 and 2019.2.7
------------------------------------------------------------

- Fix encoding issue in OGDSUpdater's error logging. [lgraf]
- Provides support for some additional metadata on the search endpoint. [phgross]
- Include file_extension in API representation of documents. [phgross]
- Translate keyword-filter label. [phgross]
- Support searching on group description in sharing form. [phgross]
- Add CMFEditions modifier that prevents journals from being versioned. [lgraf]
- Forbid transitions linked to dossier offer process through RESTAPI. [njohner]
- Add an ftw.tesbrowser widget for filling responsible(s) in the tests. [Rotonen]
- Only allow dossier transitions that are possible on the main dossier. [njohner]
- Prefix agendaitem decision numbers and meeting number by correct period title. [njohner]
- Handle dossier activation through RESTAPI. [njohner]
- Sort BlockedLocalRolesList on reference number. [njohner]
- Improve error message when trying to delete a referenced document. [njohner]
- Handle dossier deactivation through RESTAPI. [njohner]
- Fix bug with resolving a reopened dossier. [njohner]
- Update documentation for SaaS deployment update. [njohner]
- Correctly handle dossier reactivation through RESTAPI. [njohner]
- Extend listing endpoint fields with file_extension and document_type. [phgross]
- Extend task API serialization with responses data. [phgross]
- Fix livesearch endpoint when using Solr. [buchi]


2019.2.7 (2019-09-11)
---------------------

- Bump docxcompose to version 1.0.2. [njohner]


2019.2.6 (2019-08-27)
---------------------

- Bump docxcompose version to 1.0.1 [njohner]
- Handle special characters in link to advanced search. [njohner]
- Add new registry field to switch between changed and document_date for dossier end date calculation. [njohner]


2019.2.5 (2019-06-07)
---------------------

- Archiving form: Make sure dossier resolution preconditions are validated and handled. [lgraf]


2019.2.4 (2019-06-07)
---------------------

- Do not sync deadline modifications to forwarding predecessors. [phgross]


2019.2.3 (2019-06-04)
---------------------

- Drop no longer working oneoffixx upgrade. [deiferni]


2019.2.2 (2019-05-27)
---------------------

- Fix revoke_permission field and validation in the fowarding forms. [phgross]
- Hide byline for the teams. [phgross]
- Cleanup/fix oneoffix upgradesteps and make dicstorage upgrades more failsafe. [phgross]
- Add french translation for spv documentation. [andresoberhaensli, njohner]
- Add french translation for task documentation. [andresoberhaensli, njohner]
- Allow viewing closed meeting when meeting dossier is closed. [njohner]


2019.2.1 (2019-05-21)
---------------------

- Show filters also on no contents page in document listings. [phgross]
- Make subject column non-sortable in storred dictstorage settings. [phgross]


2019.2.0 (2019-05-16)
---------------------

- Use the new split off registry configuration in the Oneoffixx API client. [Rotonen]
- Fix parent-link styling in the userdetails view. [phgross]
- Use smaller or equal in time window checking for nightly runner. [njohner]
- Nightly jobs: Also log exceptions to logfile, not just Sentry. [lgraf]
- Also update empty doc properties. [buchi]
- Set 90px as a minimum instead of fixed height for description-like widgets. [lgraf]
- Fix resolving of multi-adminunit tasks. [phgross]
- Fix the setting of the content-type for Oneoffixx templates. [Rotonen]
- Concistently use "déroulement standard" for tasktemplates in French. [njohner]
- Update and add missing French translations. [njohner, andresoberhaensli]
- Update favorite-icon after cancel a document checkout. [phgross]
- Fix has_children indexer which lead to duplicate brains. [njohner, phgross]
- Add a configurable scope for Oneoffixx OAuth2 grant requests. [Rotonen]
- Trash: Update and reindex modification date when trashing documents. [lgraf]
- Respect tabbedview settings when generating a document excel export. [phgross]
- Add file_extension indexer for mails. [phgross]
- Fix upgrade step adding document_type index to not update the metadata. [njohner]
- Log nightly job output to a dedicated, self-rotating logfile. [lgraf]
- Add flag to force execution of nightly jobs. [njohner]
- Fix task activity tests. [njohner]
- Implement nightly job to perform jobs after dossier resolution. [lgraf]
- Bump plone.restapi to 3.9.0. [phgross]
- Improve the styling of the tabbedview keyword filter. [phgross]
- Adapt task reassign activity message. [njohner]
- Queue each document archival conversion only once in a single request. [njohner]
- Do not fire task delegate activity twice. [njohner]
- Do not allow sorting on Keywords in dossier and document listings. [njohner]
- Also update content controls when updating doc properties. [buchi]
- Include userid and fullname of current user in @config endpoint. [buchi]
- Include preserved_as_paper_default in the @config endpoint and view. [Rotonen]
- Pass context and orgunit as parameters to webactions. [njohner]
- Implement resolving dossiers recursively via REST API. [lgraf]
- Extend @listing endpoint with `workspace_folders`-listing. [elioschmutz]
- Allow members to access plone vocabularies through restapi. [elioschmutz]
- Workspaces do no longer inherit from dossiers. [elioschmutz]
- Optimise local roles security reindexing in tasks. [Rotonen]
- Add keywords-filter for document listings. [njohner]
- Add has_sametype_children metadata column. [njohner]
- Display the `changed` date instead the `modified` date for meeting-protocols. [elioschmutz]
- Show dossier from template action also when adding dossier disallowed. [njohner]
- Improve task restriction query, so that it works also on oracle backends. [phgross]
- Add restapi @journal endpoint to get journal entries. [elioschmutz]
- Omit the `revoke_permissions` field instead of only hiding it. [phgross]
- Fix issue on task creation when is_private feature is disabled. [phgross]
- Add webaction forms (add and edit) and management view. [njohner]
- Fix solr error during copy/paste of word document. [njohner]
- Allow non-member contributors to use the REST API. [Rotonen]
- Add nightly job runner. [njohner]
- Add document_type index. [njohner]
- Avoid object lookup for filesize and filename in @listing endpoint. [buchi]
- Add archival file management view on dossier level. [njohner]
- Show archival file state on documents overview for managers. [njohner]
- Fix tests failing due to timezone leading to date shift. [njohner]
- Display user chosen Favorites as a Oneoffixx template group. [Rotonen]
- Add a filter to the Oneoffixx template selection wizard. [Rotonen]
- Use user chosen favorites as the default Oneoffixx template group. [Rotonen]
- Display user chosen Favorites as an Oneoffixx template group. [Rotonen]
- Include filename in the livesearch endpoint results. [phgross]
- Prevent tasks from being created as private or switched to private when feature is not enabled. [Rotonen, phgross]
- Bump ftw.mail to 2.6.0 to get error logging on inbound mail failures. [lgraf]
- Add the ability to mark all notifications as read from the notifications menu. [Rotonen]
- Do not mark notifications as read when opening the notifications menu. [Rotonen]
- Handle complex URLs as titles on journal PDF exports. [Rotonen]
- Add documentation for documents endpoints (checkin/out, locking, versions) [phgross]
- Move translation overrides for ftw.mail from og.mail to og.base. [lgraf]
- Add solrsearch REST API endpoint. [phgross]
- Add webactions in user menu. [njohner]
- Add webaction action-buttons for documents, tasks and proposals. [njohner]
- Add webaction actions-menu items. [njohner]
- Add webaction title-buttons. [njohner]
- Add WebActionsProvider. [njohner]
- Add mapping between public and gever permissions. [njohner]
- Disable CSRF protect on webaction api post requests. [njohner]
- Warn the user on overviews and overlays of trashed mails or documents. [Rotonen]
- Include `include_root` parameter to `@navigation` endpoint to include the root object to the tree. [elioschmutz]
- Include `root_interface` and `content_interfaces` parameter to `@navigation` endpoint to customize the navigation items [elioschmutz]
- Include `@type`, `current` and `current_tree` property to `@navigation`-items. [elioschmutz]
- Add webaction in the add-menu of folderish content types. [njohner]
- Update plone.rest api to 3.7.2. [mathias.leimgruber]
- Respect tabbedview settings when generating an task or dossier excel export. [phgross]
- Exclusively handle templates on Committee and not on CommitteeContainer anymore. [njohner]
- Extend @listing endpoint with `tasks`-listing. [elioschmutz]
- Add option not to revoke permissions associated with a task when closing it. [njohner]
- Respect the local roles and the inheritance thereof of dossier templates. [Rotonen]
- Add restapi @journal endpoint to add journal entries. [elioschmutz]
- Fix performance issue with search root exclusion in tabbed view listings. [lgraf]
- Do not list auto-generated documents as recently touched. [njohner]
- Standardize french and german translation of "attachments" in meetings. [njohner]
- Do not list resolved tasks as pending in the 'My Tasks' tab. [Rotonen]
- Make attachments for `direct-execution` tasks editable by the responsible. [phgross]
- Make reject to skip transition only available for tasks part of a sequence. [phgross]
- Allow reassigning tasks to other org- and adminunits. [phgross]
- Update SaaS deployments documentation. [njohner]
- Adapt footer to new 4teamwork website. [njohner]
- Extend @listing endpoint with `workspaces`-listing. [elioschmutz]
- Add sharing white and black list prefix to config endpoint/view. [njohner]
- Move personal bar customization into opengever.base. [njohner]
- Unify Bumblebee URLs on REST API for document vs. document on a listing. [Rotonen]
- Make sure all workflow IDs are unique. [njohner]
- Add button to create protocol approval proposal from meeting. [njohner]
- Add support for filters in listing endpoint. [buchi]
- Add french translation for documentation. [andresoberhaensli]


2019.1.4 (2019-04-11)
---------------------

- Fix performance issue with search root exclusion in tabbed view listings. [lgraf, buchi]
- Fix creation of scaneingang dossier in the scan-in endpoint. [phgross]


2019.1.3 (2019-03-25)
---------------------

- Fix performance issue with search root exclusion in tabbed view listings. [lgraf]
- Fix upgrade step that reindexes object_provides for PDFs so it performs better. [lgraf]


2019.1.2 (2019-03-07)
---------------------

- Add a file extension column to document listings. [Rotonen]
- Make sure task and journal PDFs object_provides index is up to date after resolving a dossier. [njohner]
- Readd Office template files into Office Connector editable MIME types. [Rotonen]
- Make sure end date is reindexed when resolving/reactivating a dossier. [njohner]
- Readd Office macro files into Office Connector editable MIME types. [Rotonen]
- Complete French translations of repository in examplecontent. [andresoberhaensli]


2019.1.1 (2019-02-26)
---------------------

- Hide system-actor in the my-notification listing. [phgross]
- Add `*.vsdx` to the base list of OC-editable types. [lgraf]
- Fix handling of valid terms in repository tree xlsx file. [njohner]
- Handle translations for block_inheritance in repository xlsx file. [njohner]
- Set default language for dossier overdue activity. [njohner]
- Fix display issue for livesearch rsults. [deiferni]


2019.1.0 (2019-02-19)
---------------------

- Lock dossier subtree during resolve transition. [lgraf]
- Prevent dossiers from being resolved twice. [lgraf]
- Fix subject-filter for personal overview. [elioschmutz]
- Handle empty responsible field when assigning task. [njohner]
- Add date string localization for sablon data. [njohner]
- Fixed the REST API scan-in end point for organization units with non-ASCII in their titles. [Rotonen]
- Set default language for task reminders. [njohner]
- Add a three-tier mechanism for mapping MIME types to Office Connector. [Rotonen]
- Suppress deletion events when filtering objects from copied subtrees. [lgraf]
- Avoid infinite loops when looking for parent dossiers. [lgraf]
- Make sure favorite button is in front of the watermark header. [njohner]
- Fix mail for task added activity with multiline comment. [njohner]
- Skip creation of the tasks pdf on resolve for dossiers without tasks. [phgross]
- Give View permission to Editors on mails. [njohner]
- Clear role assignments on contained object after forwarding creation. [njohner]
- Add custom sortable_title indexer to avoid cropping of content titles. [njohner]
- Testserver: add support for custom fixtures. [jone]
- Reindex and store additionally supported bumblebee documents. [elioschmutz]
- Fix scrubbing the server version out of the HTTP response headers. [Rotonen]
- Make sure docproperties gets updated when updating an agendaitem list or a protocol. [phgross]
- Fix order issue when deleting a favorite.  [phgross]
- Add document tooltip to inbox document listing. [njohner]
- Add a template tab for OneOffixx. [Rotonen]
- Fix logo upload in the theme control-panel. [phgross]
- Solr TabbedView filters: Also include non-wildcarded terms in query. [lgraf]
- Prevent deactivating dossiers with undeactivatable subdossiers. [Rotonen]
- Add an unrestricted search option to get_subdossiers(). [Rotonen]
- Better label the Oneoffixx template selection dropdown default value. [Rotonen]
- Notifications: Defer sending mails until end of transaction. [lgraf]
- Make the Oneoffixx timeout configurable via the registry. [Rotonen]
- Update change-date properly if meeting documents have been updated. [elioschmutz]
- Update unmatching label for modification dates for meeting documents. [elioschmutz]
- Fix broken .xls mimetypes-registry entry. [elioschmutz]
- Implement WebActions storage and REST API. [lgraf]
- Fix changing task to or from private via edit form. [deiferni]
- Fix creating private tasks by mistake. [deiferni]
- Add keywords-filter for dossier listings. [elioschmutz]
- Fix restapi /@types endpiont for all portal-types. [elioschmutz]
- Add simple cache invalidation mechanism for javascript included in templates. [deiferni]
- Fix handling of initial version when saving a document as PDF. [njohner]
- Include agenda item description in TOC json. [deiferni]
- Fix bug in paragraph agendaitem item_number display. [njohner]
- Group fields in Committee edit forms. [njohner]
- Scrub Bobo Call Interface data out of the HTTP response headers. [Rotonen]
- Scrub the server version out of the HTTP response headers. [Rotonen]
- Fix bug in excerpt overview when user has no permissions on meeting. [njohner]
- Avoid naming conflicts in meeting zipexport. [njohner]
- Fix bug in meeting zip export with documents without files. [njohner]
- Do not show closed dossiers in the move target autocomplete widget. [Rotonen]
- Copy local roles depending on assignment cause during copy/paste. [njohner]
- Potentially fix an issue with duplicated catalog enries during paste. [deiferni]
- Change wording of info for inactiv close meeting button. [njohner]
- Avoid truncating committee responsible group token while normalizing. [deiferni]
- Provide a testserver for GEVER. [jone]
- Prevent tasks from being copied. [lgraf]
- Implement filtering and notifications for overdue dossiers [elioschmutz]
- ResolveOGUIDView: Preserve query string. [lgraf]
- Bump docxcompose to 1.0.0a16 to fix updating docproperties. [deiferni]
- Resolve mail author to fullname when it is a userid. [njohner]
- Remove deprecated docprops from templates and tests. [njohner]
- Add Impersonator role and "ftw.tokenauth: Impersonate user" permission. [njohner]
- Bump ftw.structlog to get new client_ip field and referrer logging fixes. [lgraf]
- Skip sablon template validation during setup of development system. [njohner]
- Refactor solr LiveSearchReplyView to use a template. [njohner]
- Include portal_type in @favorites endpoint response. [lgraf]
- Supply date format locale settings for fr-ch. [lgraf]
- Add meeting error view displayed when user has permission issues. [njohner]
- Also hide re-risen Unauthorized tracebacks for non-manager users. [Rotonen]
- Kill the theme functional test layer. [Rotonen]
- Kill the theme integration test layer. [Rotonen]
- Merge the plonetheme.teamraum gever profile into opengever.core. [Rotonen]
- Merge the plonetheme.teamraum default profile into opengever.core. [Rotonen]
- Merge the plonetheme.teamraum bumblebee profile to opengever.core. [Rotonen]
- Set the default publisher encoding to UTF-8 to match production in tests. [Rotonen]
- Bump ftw.testbrowser to 1.30.0 to respect content encodings in tests. [Rotonen]
- Use the correct message factory in the Oneoffixx form. [Rotonen]
- Add choice fields as possible first form elements for the autofocus seek. [Rotonen]
- Add two new TOC types for periods. [njohner]
- Bump ftw.pdfgenerator to version 1.6.3. [njohner]
- Provide solr for local development. [njohner]
- Fix an improper super call in meeting activities. [Rotonen]
- Move meeting activity actor_link fetching to meeting activity helpers. [Rotonen]
- Fix flaky loading of document preview with tooltip. [Kevin Bieri]
- Remove unused get_conversion_status view. [njohner]
- Correctly update containing_dossier and containing_subdossier indexes. [njohner]
- Also show participants with expired membership in meeting participants-tab. [njohner]
- Change remaining "zurücksenden" to "ablegen". [njohner]
- Also expand teams, like groups, on keyword widgets. [Rotonen]
- Translate z3c.formwidget.query (nothing). [njohner]
- Add buttons for managers to get the toc json for meeting periods. [njohner]
- Add absent members to the meeting protocolData. [njohner]
- Provide both formatted and unformatted agenda item numbers. [Rotonen]
- Store agenda item numbers as integers. [Rotonen]
- Add description field to paragraph add form. [njohner]
- Fix bug in disposition ech0160 folder model. [njohner]
- Port disposition tests to integration layer. [njohner]
- Add support for simple language codes in request language negotiation [lgraf]
- Fix typo in favorite error message. [njohner]
- Add feature flagged support to use the RESTAPI for everything in OC. [Rotonen]
- Only display .docx files as possible proposal documents. [Rotonen]
- Render mail descriptions as intelligent text on the Bumblebee overlay. [Rotonen]
- Render mail descriptions as intelligent text on the mail overview. [Rotonen]
- Render document descriptions as intelligent text on the Bumblebee overlay. [Rotonen]
- Render document descriptions as intelligent text on the document overview. [Rotonen]
- Remove the now-unnecessary js files from the favorites template. [Rotonen]
- Include preview URL and thumbnail URL in document serialization. [buchi]
- Rename preview/thumbnail columns in listing endpoint to preview_url/thumbnail_url. [buchi]


2018.5.7 (2019-01-08)
---------------------

- Make sure a failure to update DocProperties doesn't prevent checkin/checkout or moving of documents. [lgraf]
- Fix invalid end dates of resolved subdossiers when resolving main dossier. [njohner]
- Fixed attaching mails to mail via Office Connector. [Rotonen]
- Remove plonetheme.teamraum upgradesteps. [phgross]


2018.5.6 (2018-12-17)
---------------------

- Bump docxcompose to 1.0.0a15 for bugfixes. [deiferni]
- Set changed date on ObjectAdded instead of ObjectCreatedEvent. [phgross]
- Invalidate cached zip export app. [deiferni]


2018.5.5 (2018-12-10)
---------------------

- Fix task revoking permissions on close/reassign. [phgross]
- Fix an issue with missing zip after concurrent demand callback requests. [deiferni]
- Fix an issue with task permissions and proposal visibility. [deiferni]


2018.5.4 (2018-12-06)
---------------------

- Add missing changed index to solr and fix tabbedview helper fallback. [phgross]
- Bump docxcompose to 1.0.0a14 for better handling of referenced parts. [deiferni]
- Fix filesize, filename and file extension upgradestep for deployments using solr. [phgross]
- Fix an issue with meeting template titles. [deiferni]


2018.5.3 (2018-11-29)
---------------------

- Bump ftw.bumblebee to 3.7.1 to get fix to avoid calculating all indexed on document update. [lgraf]


2018.5.2 (2018-11-28)
---------------------

- Fix bug in favorites to support objects with long titles. [njohner]
- Return review_state ID in API summaries and introduce a new review_state_label attribute instead. [phgross]
- Fix quotation error and missing translations for task and dossier PDFs. [njohner]
- Make ReindexTaskPrincipalsInGlobalindex upgradestep more robust. [phgross]
- Show one line of each title and description in livesearch result. [njohner]


2018.5.1 (2018-11-23)
---------------------

- Update the changed date upgrade step. [jone]


2018.5.0 (2018-11-23)
---------------------

- Open notifications for resources on a foreign admin_unit in a new tab/window. [phgross]
- Fix bug in Windows8/10 and IE11/Edge: Select a task-reminder option will now properly stop spinning. [elioschmutz]
- Show the task-reminder selector spinner directly and not only on long-requests to remove complexity. [elioschmutz]
- Set \emergencystretch to 3em in latex templates. [njohner]
- Respect private_task feature flag also in forwarding forms. [phgross]
- Update schemas in API documentation to include "changed". [njohner]
- Ignore unauthorized traversal request in the response forms. [phgross]
- Don't display the reminder selector on tasks where it would not work. [Rotonen]
- Translate status message type in forms. [njohner]
- Skip check that tasks and documents are in a subdossier when resolving a subdossier. [njohner]
- Add Open XML Visio mimetypes. [deiferni]
- Bump ftw.bumblebee to 3.7.0 for new derived secrets for the demand endpoint. [deiferni]
- Fix issue when returning an excerpt to an already decided proposal. [njohner]
- Fix data in Task PDF when resolving a dossier. [njohner]
- Make save as pdf button colored green. [deiferni]
- Only show proposal notification settings when meeting feature is enabled. [deiferni]
- Use opaque_id instead of get parameter in SavePDFDocumentUnder. [njohner]
- Display group label in teamdetails instead of group title. [njohner]
- Prevent shadow documents from being relatable. [Rotonen]
- Do not open keywordwidget when autofocusing the first form field. [phgross]
- Add reference numbers to protected items admin view links. [Rotonen]
- Sort repository excel exports by reference number. [Rotonen]
- Allow managers to deactivate a dossier. [njohner]
- Bump ftw.contentstats to get disk usage logging. [lgraf]
- Whitelist "recently touched" data structures from CSRF write protection. [lgraf]
- Bump docxcompose to 1.0.0a13 to get a numberig restart bugfix. [deiferni]
- Make the changed field a python datetime. [njohner]
- Fix Officeconnector permission checks for task documents tab actions. [Rotonen]
- Ensure clamped down enough permissions on shadow documents. [Rotonen]
- Include relative_path to dexterity item and folder serialization [elioschmutz]
- Include bumblebee_checksum to dexterity item serialization [elioschmutz]
- Include bumblebee-checksum into @listing endpoint [elioschmutz]
- Drop verbose logging for ObjectTouched events. [lgraf]
- Fix an issue when creating meetings from a template. [deiferni]
- Added indices and metadata for filesize, filename and file extension. [Rotonen]
- Add action to save a document's PDF as a separate document. [njohner]
- Fix normalizing filename for zip export. [deiferni]
- Fix rendering issue in search view. [deiferni]
- Fix rendering issue in livesearch reply view. [deiferni]
- Fix JS ordering issue: define modernizr.js position. [phgross]
- Bump docxcompose to 1.0.0a12 to get a bugfix for sections in word. [deiferni]
- Extend example-content with evil objects containing javascript. [elioschmutz]
- Escape description of document_added description object. [elioschmutz]
- Use plone.protect class of confirm-action view. [elioschmutz]
- Don't html-escape description for JSON data. [deiferni]
- Introduce custom exception for errors in processing sablon templates. [njohner]
- Assign correct roles in development content. [deiferni]
- Place successor proposal button next to workflow buttons. [Kevin Bieri]
- Remove document tooltip on touch devices. [Kevin Bieri]
- Respect ISharingConfiguration black- and white_list_prefix for selectable groups in add-team form. [elioschmutz]
- Restrict selectable orgunits on add-team form to orgunits of the current adminunit only. [elioschmutz]
- Update ftw.tabbedview to 4.1.2. [Kevin Bieri]
- Sanitize eCH-0147 imports. [Rotonen]
- Fix dispatching notifications while recording a TaskReminderActivity. [elioschmutz]
- Prefill task-reminder select field on task response form. [elioschmutz]
- Use the same template for default notifiaction email like the daily-digest template. [elioschmutz]
- Update cached docprops on docprops updates. [Rotonen]
- Make sure our Diazo theme doesn't drop data-base-url attribute. [lgraf]
- Bump Plone version to 4.3.18. [Rotonen, lgraf]
- Fix bug with document showroom for sablon and proposal templates. [njohner]
- Restrict TaskQueries according to the task principals. [phgross]
- Bump ftw.solr to 2.3.0 to get patched (optimized) reindexObjectSecurity(). [lgraf]
- Implement asynchronous meeting zip generation, with PDFs from the new demand endpoint. [deiferni, lgraf]
- Add new icon for private folder. [njohner]
- Allow pasting templates into template folders. [Rotonen]
- Fix circular imports after using generate_remind_notifications_zopectl_handler entrypoint. [elioschmutz]
- Map gever_admins to the administrator_group in example content. [njohner]
- Style live search to match other dropdown menus. [njohner]
- OGGBundle: Fix encoding issue with UNC filepaths containing non-ASCII characters. [lgraf]
- Send notification dispatch exceptions to Raven. [Rotonen]
- Do not present the paste UI to users without 'Copy or Move' on the target. [Rotonen]
- Disallow agency-support for private tasks. [elioschmutz]
- Update task-added activity summary for private tasks. [elioschmutz]
- Add is_private field for tasks. [elioschmutz]
- Vendor opengever.ogds.models into the opengever.core codebase. [Rotonen]
- Add GET and PATCH endpoints for notifications. [elioschmutz]
- Add "changed" field, metadata and index. [njohner]
- Add trashing of protocol excerpts. [njohner]
- Display title for NullObject in meeting template selection. [njohner]
- Fix styling of favorite button. [njohner]
- Update the checksum when deleting attachments from E-mails. [njohner]
- return fullname of responsible in dossier GET. [njohner]
- Revoke temporary roles also when closing direct-execution tasks. [phgross]
- Add the GUI for task-reminders. [elioschmutz]
- Add new docproperty ogg.dossier.external_reference. [njohner]
- Exclude searchroots from subdossier listings. [Rotonen, lgraf]
- Add filters (active and all) to membership listing. [njohner]
- Do not add a task-reminder activity if task is finished. [elioschmutz]
- Add restapi endpoints to add and delete task-reminders. [elioschmutz]
- Remove leftover checkout and edit, and cancel actions for sablon and proposal templates. [njohner]
- Do not include paragraphs in comittee table of contents. [njohner]
- Add TaskReminder to handle reminders in annotations and sql. [elioschmutz]
- Allow users to retry creating a file from a Oneoffixx template. [Rotonen]
- Add TaskReminderActivity object. [elioschmutz]
- Make paragraph templates deletable. [Rotonen]
- Add ReminderSetting SQL Model. [elioschmutz]
- Add task-reminder activity settings. [elioschmutz]
- Preserve proposal document title for proposal documents of submitted proposals. [Rotonen]
- Support adding tasks via REST API. [phgross]
- Reindex issuer of all proposals. [phgross]
- Correct info messages in meetings. [njohner]
- Add proposal tabs to repository folders. [Rotonen]
- Fix global scoped "show more" links for SOLR livesearch [Rotonen]
- Only set proposal to decided when excerpt has been generated and returned. [njohner]
- Add actions pointing to the meeting and protocol debug views. [njohner]
- Fix bug with document without file in a dossiertemplate. [njohner]
- Prevent replacing files on proposal templates with non-.docx files via quickupload. [Rotonen]
- Add an upgrade step to fix broken-by-broken-protocol-excerpt journal entries on dossiers. [Rotonen]
- Do not list documents within dossiertemplates when creating a document from template. [njohner]
- Correct width of subdossier table in dossier details pdf. [njohner]
- Do not set document date during check-in or cancel. [njohner]
- Add Activity settings for Dispositions. [njohner]
- Add creation and modification date to document overview. [njohner]
- Disallow grouping tasks by the checkbox column in list views. [Rotonen]
- Add feature to generate a task listing pdf when resolving a dossier. [njohner]
- Set adhoc agendaitem filename to title without prefixing it. [njohner]
- Disallow dossier from template when adding businesscasedossier is disallowed. [njohner]
- Change wording for "Return Excerpt" from "zurücksenden" to "ablegen". [njohner]
- Add modification and creation date column to document listings. [njohner]
- Disallow replacing the file on proposal documents with a non-.docx file. [Rotonen]
- Disallow removing the file from proposal documents. [Rotonen]
- Bump lxml to 4.1.1. [Rotonen]
- Add REST API endpoint for livesearch. [maethu]


2018.4.10 (2018-11-14)
----------------------

- Task performance improvements: avoid reindexObjectSecurity twice. [phgross]
- Task performance improvements: avoid reindexObjectSecurity for not affected documents. [phgross]
- Bump ftw.solr to 2.3.1 to get reindexObjectSecurity fix. [lgraf]


2018.4.9 (2018-11-06)
---------------------

- Fix favourite edit action and display pencil. [deiferni]
- Disable buttons during save request in sharing form and improve error handling. [phgross]


2018.4.8 (2018-10-19)
---------------------

- Sharing form: do not show search results multiple times. [phgross]
- Sharing form: fix removal of all role assignments. [phgross]
- Fix parent reference number fetching for repository roots. [Rotonen]
- Fix sharing-form local_roles inheritance fallback and skip it for administators and managers. [phgross]


2018.4.7 (2018-10-05)
---------------------

- Revoke temporary roles also when closing direct-execution tasks. [phgross]


2018.4.6 (2018-10-01)
---------------------

- Fix bumblebee overlay link for not yet created initial version. [phgross]
- Only allow adding meeting templates, when meeting feature is enabled. [phgross]
- Ignore Tika exceptions during indexing in Solr. [buchi]


2018.4.5 (2018-09-24)
---------------------

- Fix task path queries for oracle backends. [phgross]
- Fix activity queries for oracle backends. [phgross]
- Split search terms at non-alphanumeric characters. [buchi]
- Bump Lucene version used in Solr to 7.3.1. [buchi]


2018.4.4 (2018-09-17)
---------------------

- Fix groubmembers overlay for groupids with spaces. [phgross]
- Add missing mimetype for wmf files. [phgross]
- Fix solr checked-in indexing problems. [phgross]
- Fix tree portlet header styling for IE11. [Kevin Bieri]
- Fix batching links on the solr search. [phgross]
- Register bmp as editable by officeconnector. [phgross]
- Fix global scoped "show more" links for SOLR livesearch [Rotonen]


2018.4.3 (2018-09-04)
---------------------

- Scale down size for logo wrapper, to have more space for personal menues. [phgross]
- Fix an encoding issue in an upgrade by no using model code. [deiferni]
- Fix double escaping of agendaitem title in meeting overview. [njohner]
- Fix handling of unidirectional by reference tasks in a sequential process. [phgross]


2018.4.2 (2018-08-30)
---------------------

- Make upgrade step 20180619143343 deferrable: Use of CMFEditions getHistory causes massive amounts of savepoints. [lgraf]
- Simplify agenda item titles for folder names for meeting zip exports. [Rotonen]
- Display native language of each language on proposal edit forms. [Rotonen]


2018.4.1 (2018-08-30)
---------------------

- Revoke roles for former responsible when reassigning a task. [phgross]
- Fix notification when removing a proposal from a meeting schedule. [njohner]
- Pin ftw.table to 1.20.0, to fix a concurrency bug in tables. [njohner]
- Fix issue when commenting on a not submitted proposal. [phgross]
- Fix IE bug on the notification settings page. [phgross]
- Fix sharing view on committecontainer. [phgross]
- Fix missing favorite-id on toggle-link if toggling favorite from repository-tree. [elioschmutz]
- Fix broken favorites state if toggling state in the repository-tree. [elioschmutz]
- Extend meeting zip-export with sort_order and gever_id. [phgross]


2018.4.0 (2018-08-20)
---------------------

- Fix dropdown JS registration. [phgross]
- CSRF logging: Filter list of registered objects so only offending objects are logged in sentry [lgraf]
- Fix bug where reactivate transition action is not visible for adminsitrators. [phgross]
- Avoid fireing ObjectModifiedEvents multiple times, on task transitions. [phgross]
- Make sure widgets properly return persisted missing values for optional fields with default values [lgraf]
- Mark tasks text field no longer as the primary field. [phgross]
- Fix oc loading icon since fontawesome update. [Kevin Bieri]
- Fix inline-cell-icons since fontawesome update. [Kevin Bieri]
- Fix response description for older rejected tasks. [phgross]
- Sharing views: Show userdetails also in an overlay. [phgross]
- Show assignments info button only on rows with automatic roles. [phgross]
- Fix sharing form for IE 11. [phgross]
- Fix display of None on the bumblebee document overlay adapter as a document date. [Rotonen]
- Fix pdf conversion for mails when resolving a dossier (ArchivalFileConverter). [njohner]
- Only show create proposal button if meeting feature is enabled. [njohner]
- Add action to switch to new GEVER UI. [njohner]
- Add generic view to retrieve the value of a setting. [njohner]
- Exclude PreconditionFailed from Error log. [njohner]
- Lock oder of avaialbe roles in sharing endpoint. [phgross]
- Fix archival_file and public_trial checks on documents overview. [phgross]
- Add placeful workflow policy for inbox-area. Let inbox users edit and checkout documents but not the inbox itself. [phgross]
- Fix base URL for contentish objects. [njohner]
- Bump Chameleon to 3.3 in order to fix edge case in exception handler causing recursion. [lgraf]
- Fix styling of plone wizard. [Kevin Bieri]
- Fix styling of multiline tree portlet tab headers. [Kevin Bieri]
- Move excerpts to the file info box on proposal overviews. [Rotonen]
- Bump plone.restapi to 3.4.1 version. [phgross]
- Only prefill dossier_manager as a form level default (instead of schema level). [lgraf]
- Make sure dossier manager field is set when protecting a dossier. [njohner]
- Fix officeconnector issue when invoked from url with trailing view name. [njohner]
- Sort excerpts by title. [Rotonen]
- Task forms: Drop unnecessary distinction between single/multi org unit setups. [lgraf]
- Add the document UUID to the OC document payloads. [Rotonen]
- Add eTag adapter for the clipboard. [phgross]
- Fix styling of dossier manager field, when a group is selected.[phgross]
- Update fontawesome to version 5.2. [Kevin Bieri]
- Add missing icon in Activity settings. [njohner]
- Resolve interactive users already on the select-responsibles step. [phgross]
- Revoke local roles for responsible and agency when finishing a task. [phgross]
- Allow administrators to export the repository as excel file. [njohner]
- Document generated meeting documents. [tarnap]
- Hide create proposal action on inboxes document listing tab. [phgross]
- Add RoleAssignment manager layer including a new sharing form. [phgross]
- Fix teamraum styles import / export for right logo. [tarnap]
- Bump ftw.upgrade for deferrable upgrade support. [deiferni]
- Create initial version with the original document creator as the principal. [lgraf]
- Improve usability of proposal add form. [elioschmutz]
- Add role assignments management view. [phgross]
- Add REST API endpoint for creating bumblebee sessions. [buchi]
- Bump ftw.casauth to 1.2.0 which provides a `@caslogin` endpoint. [buchi]
- Customize `@navigation` endpoint to return repository tree. [buchi]
- Make lock info visible even when a document can be safely unlocked. [njohner]
- Make `@config` endpoint accessible for anonymous on every context. [buchi]
- Return root and CAS URL in `@config` endpoint. [buchi]
- Improve form for submitting and updating additional documents. [tarnap]
- Fix Styling of TabbedView buttons in dossier document listing. [njohner]
- Bump ftw.tokenauth to 1.1.0 which provides support for impersonation. [buchi]
- Adjust table styling for small screens for the activity-settings view. [elioschmutz]
- Update german translation for "committeee responsible" used within the activity settings tab. [elioschmutz]
- Make sure selecting at least one task template is required. [phgross]
- Add meeting templates. [tarnap]
- Remove opengever.pdfconverter. [elioschmutz]
- Fix unicode error on edit an agendaitem. [elioschmutz]
- Adjust activity mail subject to a more generic text. [elioschmutz]
- Do no longer record `document submitted` activity while submitting a proposal with attachments. [elioschmutz]
- New filename normalizer to more closely match document and E-mail titles. [njohner]
- Install CustomEvent and Promise polyfill. [Kevin Bieri]
- Uninstall webcomponents polyfill. [Kevin Bieri]
- Update favorite-icon after checking-out or checking-in a document. [elioschmutz]
- Add microsoft publisher mimetype icon. [Kevin Bieri]
- Fix styling of the update submitted documents action in proposals overview. [phgross]
- Improve error messages in the eCH-0147 import. [phgross]
- Remove logout step displaying the documents checked out. [tarnap]
- Fix issue where empty version comments caused version tab to fail. [lgraf]
- Add webcomponents-bundle which contains ie11 polyfills. The polyfills where included in trix.js. This file have been removed in commit c40bf4e. [elioschmutz]
- Add skipped task icon. [Kevin Bieri]
- Trigger proposal rejected activity before unregister watchers. [elioschmutz]
- Fix an issue when submitting previously rejected proposals with mail attachments. [deiferni]
- Generate bin/docxcompose script to locally compose two or more word-files. [deiferni]
- Correct info message showed when regenerating agendaitem list. [njohner]
- Make remove button unavailable for private dossier. [njohner]
- Introduce generic header dropdown button. [Kevin Bieri]
- Build missing french translations for opengever.meeting. [elioschmutz]
- Hide Excerpts field in SubmittedProposal edit form. [njohner]
- Remove deprecated sablon fields from documenation. [tarnap]
- Format task template comments in detail view. [tarnap]
- Open task report: Fix condition to report admin-unit local tasks only. [lgraf]
- Fix unicode error in versions tab comments. [lgraf]
- Display the checkin comment on bumblebee overlays. [Rotonen]
- Fix a bug with modern emojis while rendering task responses. [deiferni]
- Ensure creator sets get to the paster upon pasting content. [Rotonen]
- Improve Checkout/Edit button labels. [njohner]
- Indicate change of responsible in response when task is rejected. [njohner]
- Also make active committee vocabularies sorted by title. [Rotonen]
- Sort user groups. [Rotonen]
- Add MS publisher to the list of OfficeConnector editables. [tarnap]
- Add csv, wav, wmf and xml to the mimetypes for file icons. [tarnap]
- Display the comment in a title attribute in case it gets truncated. [tarnap]
- Add an action button to dossiers for adding a proposal. [Rotonen]
- Optionalize 'related document or template' for proposals. [Rotonen]
- Add a no value option to the table radio widget when it's not required. [Rotonen]
- Extend activity icons for proposal activities. [elioschmutz]
- Implement proposal notifications. [elioschmutz]
- Register watchers for proposals. [elioschmutz]
- Implement tabs for personal activity-settings view. [elioschmutz]
- Add new notification roles for proposal activities. [elioschmutz]
- Fix triggering TaskTemplateFolders with inboxes as task responsibles. [njohner]
- Open successor task when predecessor is skipped or closed. [njohner]
- Theme: Remove diazo rule that duplicated some JS scripts. [lgraf]
- Fix an issue with excerpts title not being unicode. [deiferni]
- Extend subtask listing with link to add a task to sequential process. [phgross]
- Add description field to Proposals and Agendaitems. [njohner]
- Make protocol editable even if meeting is open. [njohner]
- Include Dossier Doc-Properties for Documents inside Proposals and Tasks. [njohner]
- Make sure members folders (private roots) get persisted default values. [lgraf]
- Make proposal title defaultFactory more robust. [lgraf]
- Fix default value persistence for title and description fields. [lgraf]
- Ensure default values get set by patching DX DefaultAddForm.create(). [lgraf]
- Add issuer-attribute to the proposal content-type. [elioschmutz]
- Allow to use all proposal templates for ad-hoc agenda items. [tarnap]
- Add support for properties to get_persisted_value_for_field() helper. [lgraf]
- Update ftw.mobilenavigation to fix Unicode error. [tarnap]
- Fix sorting of deeply nester repository folders. [tarnap]
- Add fr-ch translations to vdex files. [tarnap]
- Document generation of policies in internal docs. [tarnap]
- Add registry field to customize date format for sablon templates. [njohner]
- Remove no longer used plonetheme.teamraum uninstall profile since it's integrated into opengever.core. [elioschmutz]
- Add the ability to export repositories as excel files. [Rotonen]
- Autosize columns on excel exports. [Rotonen]
- Disallow reopen tasks in closed dossiers. [elioschmutz]
- Implement recently touched menu that lists checked out documents and recently touched objects. [lgraf]
- Comment transitions for proposals. [njohner]
- Comment action for proposals. [njohner]
- Sort the entries of the reference browser widget. [tarnap]
- Drop non-word meeting feature. [deiferni]
- Improve the validation of "preserved as paper" for related documents. [tarnap]
- Display flyup menues above the selected list items. [tarnap]
- Make error messages for unmovable documents more granular. [tarnap]
- Omit parentheses if no abbreviation for directorate or department available. [tarnap]
- Allow attaching documents of sibling proposals to proposals. [Rotonen]
- Add today to the data passed to the sablon template. [tarnap]
- Display a tooltip for the favorite action. [tarnap]
- Display keywords in the document overview. [tarnap]
- Make document mimetype lookups case insensitive. [Rotonen]
- Add new task state "skipped". [njohner]
- Reset task responsible to the task issuer upon task rejection. [Rotonen]
- Do not apply the current date to meeting titles. [Rotonen]
- Rename cancelled task in German from "storniert" to "abgebrochen" .
- Make tasktemplates sortable. [njohner]
- Only send notifications for open tasks when triggering a tasktemplatefolder. [phgross]
- Bump ftw.datepicker to get JS fix for language format selection. [lgraf]
- Fix stuck tabbedview spinner on firefox. [Kevin Bieri]
- Normalize query strings of template filter. [Kevin Bieri]
- Improve error handling on the @scan-in API endpoint. [Rotonen]
- Fix missing translation for committee filter. [tarnap]
- Do not allow to reactivate deleted documents. [njohner]
- Fix resolving multi admin unit tasks when subtasks for original task exist. [tarnap]
- Bumblebee bugfix: no longer defer preview for new documents. [deiferni]
- Display dossier resolve properties in the config view. [tarnap]
- Add a tasktemplatefolder to GEVER examplecontent. [phgross]
- Integrate plonetheme.teamraum. [deiferni]
- Make external reference clickable in dossiers. [njohner]
- Fix handling of decomposed unicode (aka NFD, NFKD) in Solr. [buchi]


2018.3.7 (2018-09-18)
---------------------

- Restrict availability of the delete button. [njohner]


2018.3.6 (2018-08-02)
---------------------

- Bump docxcompose. [phgross]
- Increase size of the favorites plone_uid column. [phgross]
- Fix physical_path schema migration for oracle backends. [phgross]


2018.3.5 (2018-06-20)
---------------------

- Include original_message data in mail API GET requests. [phgross]
- Fix updating mail title via API. [phgross]
- Fix exporting meetings with proposals with related mails. [tarnap]


2018.3.4 (2018-06-07)
---------------------

- Bumped ftw.recipe.solr to fix permission issues. [deiferni]


2018.3.3 (2018-06-06)
---------------------

- Fix unicode error on proposal listings. [phgross]


2018.3.2 (2018-06-01)
---------------------

- Team add portal action permissions: Administrators to add. [Rotonen]


2018.3.1 (2018-05-23)
---------------------

- Fix favorites-migration: skip no longer existing repo-favorites. [phgross]


2018.3.0 (2018-05-22)
---------------------

- Bump ftw.pdfgenerator to 1.6.1 to get encoding fix. [lgraf]
- Distinguish icons for docs checked out by current user vs. someone else. [lgraf]
- Allow Editors and Administrators to delete tasktemplates. [phgross]
- Fix NotificationMailer for TaskReassigned activities. [phgross]
- Customize insufficient privileges error page. [phgross]
- No longer require a paragraph template for committee containers. [deiferni]
- Fix autocomplete for relation list widgets when solr is enabled. [deiferni]
- Add responsible and issuer to notification mail for TaskAdded activities. [phgross]
- Fetch archivist group members from ogds. [phgross]
- Fix content displayed in the templatefolder's gallery view. [phgross]
- Add Subject index to solr. [phgross]
- Add new task transition in-progress to cancel. [phgross]
- Set document date of generated journal pdfs to dossier end-date. [deiferni]
- Make sure IE 11 does not cache favorites fetch requets. [phgross]
- Enable favorites feature by default. [phgross]
- Fix sorting of membership listing. [deiferni]
- Skip plonesite removals in ObjectRemovedEvent handler, to fix plonesite removal. [phgross]
- Add view to get the Connect XML for OneOffixx. [njohner]
- Show group title in the sharing view. [phgross]
- No longer show unsortable columns as sortable, bump ftw.tabbedview to 4.1.1. [deiferni]
- Add debug views for agenda_items and docxcompose. [deiferni]
- Fix API get request on private dossiers. [phgross]
- Add service to create office connector JWT for oneoffixx action. [njohner]
- Fix favorite etag adapter for webdav requests. [phgross]
- Fix get_css_class helper for task objects. [phgross]
- Switch repository favorites to new implementation. [elioschmutz]
- Fix path filterd Solr searches. [phgross]
- Implement bumblebee's auto refresh functionality. [siegy]
- Add bumblebee auto refresh feature flag. [deiferni]
- Fix dates for transported objects. [phgross]
- Implement a view for the manger to see the current config. [Rotonen]
- Fix content displayed in the inbox' bumblebee documents gallery. [tarnap]
- OGDS sync: Fix handling of missing user after updating python-ldap. [lgraf]
- Allow '\uf04a' in task text. [tarnap]
- Make office connector mimetype checks case insensitive. [tarnap]
- Display sablon template validation status. [tarnap]
- Update dependencies. [lgraf]
- Fix i18n domain in the types xml of the filing profile. [phgross]
- Drop unused pinnings. [lgraf]
- Grant team add and edit permissions to Adminstrators. [Rotonen]
- Add form to create a document from a oneoffix template. [njohner]
- Add is_checked_out icon-addition. [phgross]
- Omit search keywords from advanced search on site search prefill. [Rotonen]
- Prefix tasks in zip exports. [Rotonen]
- Allow REST API request for all members. [phgross]
- Bump ftw.tokenauth version to 1.0.1 [lgraf]
- Fix transport of dates across admin units. [Rotonen]
- OGIP32: Add favorites frontend. [mathias.leimgruber]
- Make sure bumblebee checksum gets calculated for docs created via REST API. [lgraf]
- Break activity details out per paragraph. [Rotonen]
- Delete shadowed documents when resolving a dossier [njohner]
- Moved the secretary selection in a meeting from the participants view to the metadata edit form and made it a keyword widget. [Rotonen]
- Require confirmation to cancel document checkouts [njohner]
- Implement bumblebee tooltip backdrop. [Kevin Bieri]
- Add favorite API endpoints. [phgross]
- Add favorite SQL-Model. [phgross]
- Enhance resolve_oguid view, to support other views. [phgross]
- Change label of "checkout/edit" button to "checkout and edit" [njohner]
- Only allow updating a documents file if the document is checked-out by the current user. [buchi]
- Convert .msg mails to .eml when created through REST API. [buchi]
- Include email address in dossier serialization. [buchi]


2018.2.5 (2018-05-18)
---------------------

- Fix an issue where the physical_path value could be too long. [deiferni]


2018.2.4 (2018-05-01)
---------------------

- Bump docxcompose to 1.0.0a9 to fix zero numbering and num_ids mapping error. [deiferni]


2018.2.3 (2018-04-26)
---------------------

- Bump docxcompose to 1.0.0a8 to fix a bug while merging numbered documents. [deiferni]


2018.2.2 (2018-04-25)
---------------------

- Bump ftw.datepicker to 1.3.2 [lgraf]


2018.2.1 (2018-04-12)
---------------------

- Fix logout worker when using SSO. [Kevin Bieri]
- Fix datetime picker when adding a new meeting. [phgross]


2018.2.0 (2018-04-04)
---------------------

- AdvancedSearch: Fix user sources for dossier responsible, task issuer and doc checked_out. [lgraf]
- Fix displaying quickupload uploadbox for template folders. [deiferni]
- Introduce new permisssion to protect scan to inboxes. [phgross]
- Homogenize eCH-0147 import/export action titles. [lgraf]
- Update object security when objects are moved (account for changes in placeful workflow). [lgraf]
- Disallow force-checkin for mutli-checkin action (table action) [njohner]
- Make sure to warn users before they can force-checkin a document [njohner]
- Add checkin button for force-checkin in the document actions [njohner]
- Only allow to add contacts when IContactSettings.is_feature_enabled is disabled [njohner]
- Implemented a JavaScript filter field for choosing templates. [Rotonen]
- Add filter to proposal and dossier from template addform. [deiferni]
- Add cancelled workflow state for meeting. [deiferni]
- Cleanup leftovers from ICreatorAware interface in index [njohner]
- Update policy template to set flags for new features [njohner]
- Add French translations of the Ordnungssystem in the example content [njohner]
- Update ftw.datepicker to version 1.3.0. [mathias.leimgruber]
- Temporarily disable upgrade step to fix broken references until we're sure it's safe. [lgraf]
- Improve input position for the transfer number. [phgross]
- Install and integrate ftw.tokenauth. [lgraf]
- Avoid checking out the document via the redirector on an OC reauth. [Rotonen]
- Make sure to URLEncode links to the list_groupmember view in sharing views. [lgraf]
- Ensure correct dossier reference numbers for proposals after a dossier move operation. [Rotonen]
- Implement related document icon. [Kevin Bieri]
- No longer duplicate members with special role in protocol JSON data. [deiferni]
- Change action names for meeting agenda items. [njohner]
- Order agenda item attachements alphabetically. [njohner]
- Sort related dossiers alphabetically in dossier overview. [njohner]


2018.1.5 (2018-05-18)
---------------------

- Fix an issue where the physical_path value could be too long. [deiferni]


2018.1.4 (2018-03-06)
---------------------

- Detect and fix broken references to ICreatorAware in the relation catalog. [deiferni]
- Remove all uses of enableHTTPCompression in GEVER. [lgraf]
- Fix NotificationDefault hook. [phgross]
- Fix deleting agenda items for non-word agenda items. [deiferni]
- Improve checking for truthy dates in sablon template data. [deiferni]
- Fix REST API @move endpoint: Do not require delete permission when moving objects. [buchi]
- Add REST API endpoint for querying configuration settings. [buchi]
- Make sure notification-default for the forwarding-added kind exists. [phgross]
- Fix reference number in REST API GET. [buchi]
- Add reference number to REST API summary. [buchi]
- Include 'is_leafnode' in serialization of repository folder. [buchi]


2018.1.3 (2018-02-20)
---------------------

- Bump ftw.solr version to get fix for security filter and indexing of invalid dates. [lgraf, buchi]
- Digest: Set request language based on site wide preferred language. [lgraf]
- Disable "Drop unused sequences" upgrade step because it failed on TEST. [lgraf]
- Fix period ToC downloads on IE 11 and Edge. [bierik]
- Downgrade cx-Oracle to avoid potentially broken version. [deiferni]
- Fix an issue with bumblebee preview not being renderend upon ECH0147 import. [deiferni]
- Add Creator to Solr schema. [buchi]
- Store DocValues in boolean fields. [buchi]
- Bump plone.app.contentlisting to 1.0.7 to fix getting review_state of content without workflow. [buchi]
- Bump docxcompose to 1.0.0a6 to fix a bug with renumbering of bullets [buchi]


2018.1.2 (2018-02-19)
---------------------

- Bump plonetheme.teamraum to 3.21.3 (includes Mac Office icons). [lgraf]
- Include solr-conf files in data_files so they get installed into the egg. [lgraf]
- Add some minimal logging for send_digest handler. [lgraf]
- Fix bin/mtest output encoding. [lgraf]
- Bump ftw.tabbedview to 4.1.0 to fix filter clearing in IE. [lgraf]
- Improve Tabbedview filter in Solr, e.g. allow filtering by reference number. [buchi]


2018.1.1 (2018-02-15)
---------------------

- Pin ftw.solr to 2.0.0.


2018.1.0 (2018-02-15)
---------------------

- Fix tracking table creation for oracle. [deiferni]
- Use subject instead of summary as default mail title. [deiferni]
- Fix repository favorites cache key generation for Anonymous users. [lgraf]
- Update plone.restapi to 1.1.0 and plone.rest to 1.0.0. [buchi]
- Bump Products.LDAPMultiPlugins to 1.15.post3 to handle commas in CNs. [lgraf]
- Content stats: Add custom GEVERPortalTypesProvider that sums up docs and mails. [lgraf]
- User details view: URLEncode groupid's in links to group members. [lgraf]
- Include favorites cache key in page cache key. [Kevin Bieri]
- Content stats: Avoid producing empty string key in mimetypes stats. [lgraf]
- Prevent navigation tree from getting favorites multiple times. [Kevin Bieri]
- Fix bumblebee for .bmp and .ini files. [deiferni]
- Fix select2 value dropdowns, which has been hidden by the exposator. [phgross]
- Combine similar transitions to one in the activity settings page. [phgross]
- SPV: Rename "abgeschlossene Sitzungen" to "vergangene Sitzungen". [tarnap]
- SPV: Sort memberships by member's last name. [tarnap]
- Fix logout overlay when used with cross tab logout. [Kevin Bieri]
- Sort attachments for proposal and submitted proposal alphabetically. [Rotonen]
- Upgrades: Introduce system-wide tracking of schema migrations. [jone]
- Implement TOC generate loader. [Bieri Kevin]
- OGIP 17: Use tabbedview as default view for WorkspaceFolder + Fix two display issues [mathias.leimgruber]
- OGIP 17: Implement internal invitations for Workspaces. [mathias.leimgruber]
- Improve description for committee group label. [deiferni]
- Ensure bumblebee overlay view download links point to the correct version. [Rotonen]
- Add keynote, numbers and pages mimetypes [njohner]
- Checkout/Edit only for office connector supported file formats supported [njohner]
- Disallow access on foreign private folders for Administrator and allow access to MemberAreaAdministrators instead. [phgross]
- Make teams available as tasktemplate responsibles. [phgross]
- Fix JWT authentication for users from the Zope root acl_users. [Rotonen]
- Fix bumblebee preview in ECH0147 import. [deiferni]
- Disable outdated checkout/edit action and move checkout cancel action [njohner]
- Make teams available when reassigning an open task or forwarding. [phgross]
- Support teams as forwarding responsibles. [phgross]
- Prefix the reference numbers on private dossiers with a P. [Rotonen]
- Fix attaching to email from documents within forwardings within the inbox. [Rotonen]
- Task globalindex: set the created time in sql from the Plone object. [jone]
- Allow administrator and template editors to remove a tasktemplatefolder. [phgross]
- Add tasks tab to repository folder. [jone]
- Add documents tab to repository folder. [jone]
- OGIP 17: Implement invitation storage for workspace invitations. [mathias.leimgruber]
- Add an additional batching_container for tabbedview-listings at the end of the table. [elioschmutz]
- SPV: Add json file containing the meetings metadata to zip export. [tarnap]
- SPV: Add ad hoc agenda items to zip export. [tarnap]
- Add DocProperty ogg.document.version_number.  [njohner]
- OGIP 17: Add workspace workflows and add workspace support to document workflow. [jone]
- OGIP 17: Introduce workspace specific sources used in Tasks [mathias.leimgruber]
- Fix broken advanced search js initialization. [deiferni]
- Tidy up XML files in default profile [raphael-s]
- Use index to sort the committees by title. [tarnap]
- Sort tabbed view by column only if column exists. [tarnap]
- Trigger SQL task synchronisation when changing task state. [phgross]
- Change msg2mime transform to use msgconvert executable from $PATH instead of shipping our own wrapper script. [lgraf]
- Add action to revive bumblebee previews. [elioschmutz]
- Add partial reindex optimization for trashing and untrashing objects. [elioschmutz]
- OGIP 17: Implement sequence_number and NameFromTitle behavior for Workspace. [mathias.leimgruber]
- OGIP 17: Add tabbedviews for opengever.workspace types. [mathias.leimgruber]
- Prepare HTML structure for dossier title alignment. [Kevin Bieri]
- Display document mimetype icon on livesearch results. [Kevin Bieri]
- Save current treeportlet index in localstorage. [Kevin Bieri]
- Fix autofocus on forms with keywordwidget.[Kevin Bieri]
- Implement cross tab logout mechanism. [Kevin Bieri]
- Add filename and filesize in bumblebee overlay. [njohner]
- OGIP 17: Add workspace folder content type [raphael-s]
- Fix plonesite removal. [phgross]
- Fix required input validation for the recipients field, when delegating a task. [phgross]
- OGIP 17: Add workspace content type [raphael-s]
- Fix active field in the team edit form. [phgross]
- Bump ftw.bumblebee to skip checksum calculation for unsupported mimetypes. [deiferni]
- Fix dossier responsible widget, in the DossierAddFormView step, when accepting a task.  [phgross]
- OGIP 17: Add workspace root content type [raphael-s]
- Fix force-checkin for administrators. [phgross]
- Implement workspace module basics [raphael-s]
- Allow to add proposal documents to tasks. [tarnap]
- Improve Office Connector testing. [Rotonen]
- SPV: Make title and dossier column wider and remove invalid sorting options in meetings tab. [tarnap]
- Integrate Solr into search form, live search and tabbedview filter. [buchi]
- Add option to get a custom field list in REST API summaries. [buchi]
- Add REST API endpoints for trashing/untrashing documents [buchi]


2017.7.8 (2018-01-23)
---------------------

- SPV: Add header and suffix sablon for templates for the agenda items in protocols. [tarnap]
- Use excerpt header template as excerpt master document. [deiferni]


2017.7.7 (2018-01-12)
---------------------

- Upgrade docxcompose version pinning. [tarnap]
- Fix listing groups for committees. [deiferni]
- Fix listing the members of an empty group. [tarnap]
- Trigger SQL task synchronisation when changing task state. [phgross]


2017.7.6 (2018-01-08)
---------------------

- Fix notification counter, count only badge notifications. [phgross]


2017.7.5 (2018-01-02)
---------------------

- Bump docxcompose version to 1.0.0a4. [phgross]
- Enable edit border for committee members on meeting view. [phgross]
- Fix pre-filling committee group id in edit form. [deiferni]


2017.7.4 (2017-12-09)
---------------------

- Bump ftw.recipe.deployment version.


2017.7.3 (2017-12-08)
---------------------

- Ignore ContainerModifiedEvents on ObjectModified event handlers. [phgross]


2017.7.2 (2017-12-01)
---------------------

- Add debug view to download docxcompose raw files.


2017.7.1 (2017-11-30)
---------------------

- Remove ZIP export action on plonesite. [phgross]
- Fix manual journal entry link on documents journal. [phgross]
- Make sure PDF Preview link is only available for documents not for mails. [phgross]
- Don't display nochange/remove radio buttons for file in document add-form. [deiferni]
- Fix an issue when delegating to inboxes. [deiferni]


2017.7.0 (2017-11-28)
---------------------

- Extend OGGBundle with the DossierManager role. [elioschmutz]
- SPV word: Add default content. [tarnap]
- OGDS sync: handle multivalued group titles. [phgross]
- Increase group title length. [phgross]
- Fix bux when accepting a multi admin unit team task with option participate. [phgross]
- Fix an untranslated OC error message. [Rotonen]
- Fix bug for unknown mimetypes [njohner]
- Use latest ruby (2.4.2) and nokogiri (1.8.1) [siegy22]
- Show icons in BlockedLocalRolesList. [njohner]
- Fix bug when accepting a multiadmin unit team task. [phgross]
- Ensure new versions are created when doc-properties change. [deiferni]
- Make cassation_date field accessible only to manager. [njohner]
- Use empty mimetype icon for empty document content types. [Kevin Bieri]
- Pin ftw.keywordwidget to 1.4.2 to fix a term-lookup error. [elioschmutz]
- Add mimetype for MS OneNote. [phgross]
- Only show subdossier tab on dossiers where the max depth allows to add subdossiers.  [phgross]
- Correct field description for responsible person/entity when forwarding documents [njohner]
- SPV-word: Fix renaming agenda items in meeting view. [tarnap]
- Don't remove doc-properties for excerpts, use correct document as master. [deiferni]
- Extend repository-import excel with new dossier-manager role. [elioschmutz]
- Add a tabbed view for Administrators and Managers to reporoot - repofolder - dossier for listing child dossiers with blocked local roles. [Rotonen]
- Add group title option to the OGDS Synchronisation. [phgross]
- Add missing default value for dossier protection fields. [elioschmutz]
- Show filterlist also on empty tabbedview listings. [phgross]
- Fix redirection when creating new sablon templates. [tarnap]
- Use localstorage for tracking expanded tree uids instead of cookie. [Kevin Bieri]
- Remove deactivate action for private dossiers. [tarnap]
- SPV: Sort meetings by date. [tarnap]
- SPV: Add concluded meetings to committee overview and reorder the blocks in the columns. [tarnap]
- Fix syncing the submitted proposal title to sql. [deiferni]
- SPV: Fix member links in committee overview. [tarnap]
- Add date of submission to proposals. [deiferni]
- SPV: Make the considerations field a trix field. [tarnap]
- Handle inconsistent local roles on protected dossiers with a warning message. [elioschmutz]
- Add new field dossier_manager to the IProtectDossier behavior to set the dossier-manager manually. [elisochmutz]
- Fix agenda items rendering on non-word meeting. [deiferni]
- Add special keywordwidget template for users and groups, showing an icon and links the groups. [elioschmutz]
- Add the "Protect dossier" functionality to a dossier. [elioschmutz]
- Make notification badge a separate channel. [phgross]
- Allow administrator and owner to delete objects in private folders. [tarnap]
- Set excel file name to dossier title when creating a disposition report. [njohner]
- SPV word: Remove fields which are intended for no word version. [tarnap]
- Add personal notification settings support. [phgross]
- SPV word: Add links to proposal and meeting in document overview. [tarnap]
- Add proper responsible for fixture objects. [elioschmutz]
- Add optional header and suffix templates for protocol excerpts. [tarnap]
- Also display exceptions on agenda item list to users. [deiferni]
- Make sure response changes are persistent. [phgross]
- SPV word: redesign agenda items in meeting view. [jone]
- Add new role DossierManager with the related permission "opengever.dossier: Protect dossier" [elioschmutz]
- Make responsible change, when accepting a team task visible in the response. [phgross]
- Prevent editing agenda item list when meeting has been held. [deiferni]
- Allow proposal listings to be filtered by proposal title. [deiferni]
- Allow proposal listings to be sorted by title. [deiferni]
- Keep meeting-dossier and meeting title in sync, only allow editing of meeting title. [deiferni]
- Support importing toplevel documents from eCH-0147 message. [buchi]


2017.6.8 (2018-02-15)
---------------------

- Fix malformed version URL on documents. [Rotonen]


2017.6.7 (2018-01-04)
---------------------

- Fix dossier responsible widget, in the DossierAddFormView step, when accepting a task.  [phgross]


2017.6.6 (2017-11-30)
---------------------

- Fix an issue when delegating to inboxes. [deiferni]
- Remove ZIP export action on plonesite. [phgross]
- Fix manual journal entry link on documents journal. [phgross]
- Make sure PDF Preview link is only available for documents not for mails. [phgross]
- Only show subdossier tab on dossiers where the max depth allows to add subdossiers.  [phgross]
- Ensure new versions are created when doc-properties change. [deiferni]
- Don't display nochange/remove radio buttons for file in document add-form. [deiferni]


2017.6.5 (2017-11-22)
---------------------

- Fix OGMail searchable text extender. [elioschmutz]
- Update bumblebee checksum when modifying document doc properties. [deiferni]
- Don't escape description in overview twice for dossier templates. [deiferni]
- Fix textfilter in sqlsource table listings for oracle backends. [phgross]
- Exclude the latest version in the bumblebee versioning warning logic. [Rotonen]


2017.6.4 (2017-11-09)
---------------------

- Fix agenda items rendering on non-word meeting. [deiferni]


2017.6.3 (2017-11-07)
---------------------

- Pin plone.restapi to 1.0a23. [deiferni]
- Make sure `plone.rest` directives are loaded when used. [deiferni]


2017.6.2 (2017-11-07)
---------------------

- Fix catalog index name in upgrade step. [deiferni]
- Automatically update versions.cfg when releasing with zest.releaser. [deiferni]


2017.6.1 (2017-11-02)
---------------------

- Prevent upgrade to committee container roles to run for all documents. [deiferni]


2017.6.0 (2017-10-27)
---------------------

- Sort entries in committee vocabulary by committee title. [tarnap]
- Skip documents without a file in eCH-0147 exports. [phgross]
- Include mails in eCH-0147 exports. [phgross]
- LDAP sync: skip referral's on each ldap search, also for the user import. [phgross]
- OGGBundle: Do intermediate commits every 1000 items by default. [lgraf]
- Handle spaces inside groups ids during repository import correctly. [phgross]
- SPV word: Remove link to proposal excerpt document if no view permission. [tarnap]
- Avoid id conflicts when setting up a repository. [phgross]
- Remove the broken and unused fillingnumber-adjustment view to get rid of the grokked
  dependency collective.z3cform.datagridfield. [elioschmutz]
- Reenable action "move items" for inbox. [tarnap]
- Fix batch-handling in the showroom overlay for the search-view. [elioschmutz]
- SPV word: update meeting view with new design. [jone]
- OGGBundle: Fix tracking of item counts (actual vs. raw). [lgraf]
- OGGBundle: Support delta imports using GUID. [lgraf]
- OGGBundle: Validate parent_reference early for existence. [lgraf]
- Fix handling of disabled or no longer assigned users in the autocomplete sources.  [phgross]
- Add indexer for bundle GUIDs and create index upon bundle import. [lgraf]
- Fix missing response-variable due to ungrok opengever.document. [elioschmutz]
- Ungrok opengever.core. [elioschmutz]
- Ungrok opengever.meeting. [elioschmutz]
- Removes groked plone.directives. [elioschmutz]
- Remove bcc from email attributes in send as attachment action if the dossier is resolved. [tarnap]
- Ungrok opengever.policytemplates. [elioschmutz]
- Ungrok opengever.base. [elioschmutz]
- SPV word: prevent reader user from returning excerpts. [jone]
- SPV word: remove double excerpt entry when word feature activated. [tarnap]
- Fix send as attachment action by providing a default service. [tarnap]
- SPV word: always show excerpts in meeting view. [jone]
- Extract bumblebee preview generation into standalone component. [jone]
- Do not render document link without View permission. [jone]
- Optimise reindexing for document checkout/checkin cycles. [Rotonen]
- Add dossiertemplates configuration flag `respect_dossier_depth`. [phgross]
- Refactor JSON schema generation and dumping, add tests. [lgraf]
- Ungrok opengever.dossier. [elioschmutz]
- Ungrok opengever.document. [elioschmutz]
- SPV word: Selectable proposal templates can be configured per committee. [jone]
- Ungrok opengever.task. [elioschmutz]
- Ungrok opengever.officeatwork. [elioschmutz]
- SPV: Let CommitteeMember only have read-access on meeting view. [jone]
- SPV: Remove link to dossier in listings when user has no view permission on the dossier. [tarnap]
- SPV: Fix ad hoc agenda item template label translation. [tarnap]
- SPV: Meeting end date is not set when start date is selected. [tarnap]
- SPV word: Protect proposal transitions to require modify permission. [jone]
- SPV word: Update document- and mail-workflow to support committee roles. [jone]
- SPV: Update and fix proposal tabs. [jone]
- Link and prefix task responsibles and issuers with an icon in tasklistings. [phgross]
- List also team-tasks in team member's MyTask tab of the personal overview. [phgross]
- Fix default_documents_as_links default value for opengever.mail. [elioschmutz]
- Fix responsible_client default value for tasktemplates. [phgross]
- SPV word: Do not automatically decide agenda items when closing meetings. [jone]
- SPV word: Prevent meetings with undecided agenda items from closing. [jone]
- SPV word: In proposal forms, move the title to the top. [jone]
- SPV word: Update proposal workflow translations to be consistent capitalized. [jone]
- SPV word: Fix protocol zip export. [tarnap]
- Create missing SQL sequences. [jone]
- Ungrok opengever.inbox. [elioschmutz]
- SPV word: Provide meeting doc properties in proposal documents and excerpts. [jone]
- Bundle import: Fix deactivation of LDAP plugin during import. [lgraf]
- SPV word: Register excerpt relations properly in the relation catalog. [jone]
- Update Plone version to 4.3.15. [lgraf]
- SPV: Fix proposal history. [tarnap]
- SPV: Fix deleting ad-hoc agenda items. [tarnap]
- SPV word: Display other participants in meeting view. [tarnap]
- SPV word: Introduce successor proposals. [jone]
- Ungrok proposal add form. [jone]
- Reworked initial version creation: do not create a initial version until the file will be changed. [phgross]
- SPV word: Add protocol header and suffix templates. [tarnap]
- SPV word: Improve visual feedback when scheduling text or paragraph. [jone]
- SPV word: Remove proposal document's title prefix. [tarnap]
- SPV word: Hide excerpt template from form when word feature enabled. [tarnap]
- SPV word: Remove "Ad-hoc" from the GUI. [tarnap]
- Fix private folder creation for userids containing dashes. [phgross]
- SPV word: Set "remove" and "delete" translations correctly. [tarnap]
- SPV word: trash documents of removed ad hoc agenda items. [tarnap]
- SPV word: Represent paragraphs in the generated protocol. [jone]
- SPV word: Allow to set custom excerpt titles. [tarnap]
- Add new tab teams to contactfolder. [phgross]
- Add add and edit forms for teams. [phgross]
- Lawgiver: Ignore ftw.usermigration permission. [lgraf]
- SPV word: Add proposal documents to meeting ZIP export. [jone]
- SPV word: Prefix decision numbers with year. [jone]
- SPV: Fix dialog text when closing a meeting. [jone]
- Fix caching problems in JSON responses with IE 11. [jone]
- SPV word: Add workflow transition for reopening meetings. [jone]
- SPV word: Move workflow transitions to actions menu in meeting view. [jone]
- SPV word: Move meeting status in meeting view. [jone]
- SPV word: Move ZIP-export action to actions menu. [jone]
- Fix ordering in bumblebee gallery. [jone]
- SPV word: Add new meeting edit form and move edit action to editbar. [jone]
- SPV word: Add excerpts for ad-hoc agenda items. [deiferni]
- Update plone.restapi to 1.0a21 which provides support for locking [buchi]
- Add @scan-in REST API endpoint for uploading scanned documents. [buchi]


2017.5.1 (2017-09-19)
---------------------

- Fix is_subdossier replacement upgradestep, reindex all objects. [phgross]
- Register an is_subdossier indexer for dossiertemplates. [phgross]
- Add missing french translations. [phgross]

2017.5.0 (2017-09-14)
---------------------

- Format line breaks and links in the dossier overview comment and description box. [phgross]
- OGGBundle: Fix title encoding in constructor section. [phgross]
- Display decision number in proposal listings. [deiferni]
- Fixed custom sort for catalog listings. [phgross]
- Format line breaks and links in task responses. [phgross]
- Bump ftw.recipe.deployment to 1.3.0 in order to get log rotation for ftw.structlog logfiles. [lgraf]
- SPV word: Add functionality to return an excerpt to the proposer. [deiferni]
- Fix shared default value for excerpt lists. [deiferni]
- Fixed bumblebee-overlay pdf link generation, when filename contains umlaut. [phgross]
- Generate agenda item lists as documents. [Rotonen]
- Replace is_subdossier FieldIndex with an BooleanIndex. [phgross]
- Add content stats provider for file mimetypes. [lgraf]
- Implement "checked in vs. checked out docs" content stats provider. [lgraf]
- Include and integrate ftw.contentstats in GEVER. [lgraf]
- Add ftw.structlog as a dependency to opengever.core. [lgraf]
- SPV word: add support for ad-hoc agenda items, add configurable ad-hoc agenda item. [deiferni]
- Add configuration option to hide the mail preview tab. [phgross]
- Update ftw.keywordwidget to 1.3.6: Fix a bug while adding new keywords. [mathias.leimgruber]
- Add proposal filter to committee. [deiferni]
- Hide contact field in the manual journal entry form, when contact feature is disabled. [phgross]
- Only show membership edit links for CommitteeResponsibles. [deiferni]
- Fix Drag'n'Drop replacing for documents inside a resolved task. [phgross]
- Bundle import: Fix tree portlet assignment to repo roots. [lgraf]
- Fix an issue with conflicting css classes breaking a link. [deiferni]
- Fix textfilter for sql table listings when using oracle backends. [phgross]
- Word meeting: Show decision number in meeting view. [jone]
- Add lawgiver workflows for committee and committee-container. [deiferni]
- Add a file action button for extracting mail attachments. [Rotonen]
- Add upgrade step which fixes potential missing titles on opengever.private.root objects. [mathias.leimgruber]
- Point footer source-code link to 4teamwork/opengever.core, drop link to CI. [deiferni]
- Filter results for disabled OrgUnits in all sources. [mathias.leimgruber]
- Install ftw.tika if necessary. [mathias.leimgruber]
- Ungrok opengever.latex. [elioschmutz]
- Add a CI script to check incoming python files for pyflakes issues. [Rotonen]
- Update ftw.zipexport to include empty folders. [elioschmutz]
- Word meeting: update styling and placement of meeting view components. [jone]
- Breadcrumb viewlet rework. Extend crumbs with icons and group the repository part. [phgross]
- Add bin/test-cached helper script to execute a chached test-run. [deiferni]
- Ungrok opengever.ogds.base [lgraf]
- Add external_reference field and index [tarnap]
- Show mimetype-icon of proposaltemplate in bumblebee-listing. [elioschmutz]
- Add add bumblebee gallery view for sablontemplate. [elioschmutz]
- SPV word: fix a unicode error when creating proposals from a template. [deiferni]
- SPV word: merge multiple word files into one protocol. [deiferni]
- Add add bumblebee gallery view for proposaltemplate. [elioschmutz]
- Word meeting: Improve edit-document-button behavior in meeting view. [jone]
- Fix typo in contact detail view. [elioschmutz]
- Remove separate bumblebee fetch-views since they are no longer necessary because we no longer use grok. [elioschmutz]
- Implement custom error page. [mathias.leimgruber]
- Bundle import: Also log progress and RSS during post-processing. [lgraf]
- Word meeting: List excerpts per agenda item in meeting view. [jone]
- Word meeting: Replace excerpt generation with new word implementation. [jone]
- Word meeting: Automatically checkin document when deciding an agenda item. [jone]
- Word meeting: Update submitted proposal workflow: let group members checkout documents. [jone]
- Fix error in earliest_possible_end_date if there are date and datetime objects to process. [elioschmutz]
- Fix change workflow on remote tasks if the successor has no write-permission on the remote task does no longer fail with unauthorized. [elioschmutz]
- Do no more send None as text while syncing tasks if there is no text. [elioschmutz]
- Fix leaking reference in RestrictedVocabularyFactory. [lgraf]
- Use get_download_view_name in oc_attach restapi view to download original_message file if available. [elioschmutz]
- Use get_file-method in send_document method to use original_message file data if available. [elioschmutz]
- Refactoring: Add new method get_download_view_name for mail and documents. [elioschmutz]
- Refactoring: Use mail get_file method to receive either the original_message or the message field. [elioschmutz]
- Reindex is_subdossier-index after moving the dossier. [elioschmutz]
- Improve warning when opening an old version of a document. [tarnap]
- Highlight search terms after fetching new search results per ajax. [elioschmutz]
- Fix broken remove-condition-checker if backreferences were deleted. [elioschmutz]
- Fix broken overview-listing if backreferences were deleted. [elioschmutz]
- Fix encoding error when syncing proposals with SQL. [jone]
- Remove "Properties"-action on personal overview. [elioschmutz]
- Ungrok opengever.advancedsearch. [phgross]
- Fix showroom overlay within an activated exposator. [elioschmutz]
- Fix ArchiveForm when resolving a Dossier. [phgross]
- Allow sort by member-name on memberhips-listing view. [elioschmutz]
- Extend tabbedview with sqlsource: Implement sorting by sqlalchemy columns instead only by string. [elioschmutz]
- Allow remove templatefolder content. [elioschmutz]
- Handle unknown asynchronous tooltip response. [Kevin Bieri]
- Move language selector into the user menu (dropdown) - Implemented in plonetheme.teamraum. [mathias.leimgruber]
- Only the Manager can access the folder_contents on the plone root. [mathias.leimgruber]
- Ensure we append the originating dossier's mail in address as BCC to OfficeConnector multiattach payloads. [Rotonen]
- Add an attributes REST endpoint to dossiers. [Rotonen]
- Update ftw.keyowordwidget to 1.3.3, to fix a problem while select/search new keywords. [mathias.leimgruber]
- Sort meeting participants alphabetically in meeting-view. [elioschmutz]
- Upgrade ftw.zopemaster which uses the new ftw.slacker for slack notifications. [elioschmutz]
- Refactor the function: earliest_possible_end_date. [elioschmutz]
- Remove unused projectdossier contenttype. [elioschmutz]
- Upgrade plone.app.jquery from 1.7.2.1 to 1.11.2. [elioschmutz]
- Word meeting: quick edit proposal file in meeting view. [jone]
- Word meeting: show proposal files in meeting view. [jone]
- Reworked contact syncer functionality, to improve speed with bulk insert and updates. [phgross]
- Format line breaks in task descriptions. [tarnap]
- SPV word: checkout proposal document after creating proposal. [jone]
- Implement REST API endpoints for document checkout/checkin. [buchi]
- Implement eCH-0147/eCH-0039 import and export [buchi]


2017.4.1 (2017-08-14)
---------------------

- Bundle import: Reduce memory high-water-mark by periodically re-setting the
  Plone site using setSite(), and garbage collecting the cPickleCache. [lgraf]
- Bundle import: Also log progress and RSS during post-processing. [lgraf]
- Fix leaking reference in RestrictedVocabularyFactory. [lgraf]
- Fixed bug in search when sorting on relevance. [phgross]
- Bundle import: Fix logging in case of disallowed subobject type. [lgraf]
- Bundle import: Don't unnecessarily keep references to persistent objects
  over the lifetime of the entire import. This lets the garbage collector
  do its job, and reduces growth of memory usage during import. [lgraf]
- Bundle import: Display current memory usage (RSS) in progress logger. [lgraf]


2017.4.0 (2017-07-26)
---------------------

- Fixed OGDS group sync, when lookup_groups_base is not defined. [phgross]
- Export msg in OGmail zip represenation if the original_message is available. [mathias.leimgruber]
- Add original_message support to bundle import. [phgross]
- Rename current orgunit cookie, to invalidate existing cookies. [phgross]
- Move handlebar templates to template files. [jone]
- Disable reference number column in the document listing of the inbox. [phgross]
- Enable \*.msg download for all download copy links. [phgross]
- Fix mail download: Convert LF to CRLF only for EML mails. [phgross]
- Fix: remove ftw.showroom CSS on fresh installations too. [jone]
- Define cookie path when setting the current orgunit id in the cookie. [phgross]
- Make sure unicode is stored in proposal sql. [jone]
- Fix unicode error in committee group vocabulary. [jone]
- Add version of downloaded file to journal's entry. [tarnap]
- Allow to copy-paste single documents. [tarnap]
- Enable secure flag for cookies. [phgross]
- Always download MSG file if avaiable. [mathias.leimgruber]
- Move data for the history of a proposal from SQL to their corresponding plone-objects Proposal/SubmittedProposal. [deiferni]
- Remove dossier inheritance of templatefolder [elioschmutz]
- Move data for most text-fields of Proposal (SQL) to their corresponding plone-objects Proposal/SubmittedProposal. [deiferni]
- Introduce versioning for Proposal/SubmittedProposal. [deiferni]
- Cleanup rolemap, don't redefine plone roles. [deiferni]
- Use OGMail original_message-file for bumblebee-conversion if available. [elioschmutz]
- Amend the OfficeConnector javascript to refresh the page based on the lock status. [Rotonen]
- Add the document lock status to the document status end point. [Rotonen]


2017.3.2 (2017-07-21)
---------------------

- Add upgradestep to cleanup no longer existing interfaces from zc.relation catalog. [phgross]


2017.3.1 (2017-07-18)
---------------------

- Expand current subdossier in subdossier tree. [Kevin Bieri]
- Ignore LocalRolesModified events in repositoryfolder ModifiedEvent subscribers. [phgross]
- Do not sync comments to a predecessor forwarding. [phgross]
- Fixed translation for portal message type, when adding a DX object. [phgross]


2017.3.0 (2017-07-12)
---------------------

- List only documents as related_documents in the documents overview. [phgross]
- Disable the displaymenu-item in contentmenu for all types. [phgross]
- Fix datetime converter when input is empty. [deiferni]
- Fix UnicodeEncodeError in task listings. [phgross]
- Make sure that remote task state changes are synced to globalindex. [phgross]
- Expand just the selected item in the subdossier tree. [Kevin Bieri]
- Added missing cancel button for the manual journal entry form. [phgross]
- XSS: Escape html for manual journal entries' comment. [tarnap]
- Fix filetree scroll position of current item. [Kevin Bieri]
- Fix an issue where creating a dossier from template ended in an exception. [elioschmutz]
- Allow move items in the documents tab within the templatefolder. [elioschmutz]
- XSS: Escape html for Dossier title on task listing. [mathias.leimgruber]
- XSS: Escape html for the breadcrumbs part for get_link on tasks. [mathias.leimgruber]
- Fix meeting TOC, correctly limit TOC to committee. [deiferni]
- Change Member fullname to `Lastname Firstname` instead of `Firstname Lastname` to be consistent with Actor/Contact et cetera. [deiferni]
- Sort meeting participants alphabetically. [deiferni]
- Use officeconnector to edit a newly created document from template. [tarnap]
- Add bumblebee gallery view for related-documents tab on tasks. [elioschmutz]
- List bidirectionally related documents in the document's overview. [tarnap]
- Implement and enable redirector etag adapter. [phgross]
- Add reference column to document listings. [tarnap]
- Do not display templates without an assigned file in the CreateDocumentFromTemplate form. [tarnap]
- Add dossier and subdossier link in task listings. [elioschmutz]
- Fix PrivateFolders Title encoding. [phgross]
- Show userid instead of E-Mail address on all sources (except EMailSource). [mathias.leimgruber]
- Mark inactive repository folders in navigation tree. [Kevin Bieri]
- Fix "leave GEVER" on logout overlay. [mathias.leimgruber]
- Disbale swfobject.js - no longer load Flash Fallback for multiuploads. [mathias.leimgruber]
- Fix schema migration EnlargeProfileidInMigrationTrackingTable for oracle backend. [phgross]
- Add missing contacts only sources, used by customer special dossiers. [phgross]
- Reset journal after copy a document. [mathias.leimgruber]
- Switch back to the orginal plone.formwidget.autocomplete package from our fork. [phgross]
- Fix task assign form: Only users and the inbox of the current user is selectable. [mathias.leimgruber]
- Fix for OGIP 15: no longer make a deepcopy of the payload. [mathias.leimgruber]
- Render subdossier tree collapsed initially. [Kevin Bieri]
- Implement and enable the org unit selector etag adapter. [phgross]
- Hard-code base profiles to be installed for every deployment. [deiferni]
- Add api_group deployment configuration option. [deiferni]
- Improve visual search on customer request. [Kevin Bieri]
- Merge Generic Setup profiles into a new opengever.core:default profile. [phgross]
- Replace the AutocompleteField(Multi)Widget with the KeywordWidget. This makes the AutocompleteWidget obsolete. [mathias.leimgruber]
- Respect lookup_groups_base during OGDS group sync. [phgross]
- Use our own forks of Products.LDAPUserFolder and Products.LDAPMultiPlugins. [phgross]
- Fix Subject link on dossier overview. [mathias.leimgruber]
- Fix tasktemplate view by adding a missing </table> tag. [mathias.leimgruber]
- Install ftw.copymovepatches for better move performance. [mathias.leimgruber]
- Use latest ftw.datepicker for all datetime widgets. [mathias.leimgruber]
- Make `resolving` a dossier customizable and provide two implementations (strict and lenient). [deiferni]
- Replace changed_security with elevated_privileges. [deiferni]
- Implement tracebackify decorator for better errorhandling/debugging remote requests. [mathias.leimgruber]
- Implement safe_call decorator for better errhandling/debugging remove requests. [mathias.leimgruber]
- Refactor SQL models, move Query classes to query module. [deiferni]
- Link keywords on dossier overview. [mathias.leimgruber]
- Fix checkout behavior of already checked out documents. [Kevin Bieri]
- Make sure that pasting is allowed before pasting. [deiferni]
- Remove an unused creator behaviour from the codebase. [Rotonen]
- Keep \*.msg file after conversion and store message source for mails. [deiferni]
- Fix string type in bundle loader [buchi]
- Fix translation for the Open as PDF action. [phgross]
- OGGBundle: Do not initialize the mail title for mails with a title given. [phgross]
- Fix addable types constrain for repository folders in API calls [buchi]
- Cache addable types constrains for repository folders per request [buchi]
- Fix typo in dossier SearchableTextExtender, which results in a empty SearchableText if IFilingNumber behavior was activated. [mathias.leimgruber]
- Display attachments on mail overviews. [Rotonen]
- Allow the same Users to edit Tasktemplatefolders in active state as in inactice state. [mathias.leimgruber]
- Make sure local roles of committees are stored as byte strings [buchi]
- Use CreatEmailCommand to create email upon mail-in. [deiferni]
- Fix typo in method name: resolve_sumitted_proposal -> resolve_submitted_proposal. [mathias.leimgruber]
- Use chameleon as the templating engine for better performance. [Rotonen]
- Respect `maximum_dossier_depth` registry record in DefaultConstrainTypeDecider [mathias.leimgruber]
- Handle require_login error where came_from_did not exist. [jone]
- Inter-Admin-Unit Requests: Extract response body into the local namespace so
  Sentry can log it as a local in case of failure. [lgraf]
- Word meeting: replace proposal textfields with a document. [jone]
- OGIP 15: Implement adding multiple task with the add form. [mathias.leimgruber]


2017.2.5 (2017-07-04)
---------------------

- Add missing french translation. [phgross]
- Include missing permission definitions from Products.CMFCore. [phgross]


2017.2.4 (2017-06-14)
---------------------

- Added french translations [j-sposato, phgross]


2017.2.3 (2017-05-26)
---------------------

- Fix task-commented schema upgrade and make it both mysql and psql-compatible. [deiferni]
- Fix get_retention_expiration_date on dossier. retention_period may be a unicode. [mathias.leimgruber]


2017.2.2 (2017-05-22)
---------------------

- Fix translation for the Open as PDF action. [phgross]


2017.2.1 (2017-05-11)
---------------------

- Make sure `plone.rest` directives are loaded when used. [deiferni]


2017.2.0 (2017-05-11)
---------------------

- Improve view permissions (ported from 4.15.5). [jone]
- Do not sync task workflow changes to forwarding predecessors. [phgross]
- Tests: Manage monkey patching of PDFCONVERTER_AVAILABLE through a context manager. [lgraf]
- Remove no longer used ftw.treeview dependency. [phgross]
- Improve help text for task responsible selection. [lgraf]
- Fix mail downloads by demanding a context to be passed into DC helpers. [Rotonen]
- Always render a task link for administrators or managers. [phgross]
- Improve help text for task responsible selection. [lgraf]

- Make OC multiattach behave more gracefully for long URLs:

  - Relax length limit from 500 to 2000 bytes for browsers other than IE11
  - Inform user via JS alert when they exceed the length limit

  [Rotonen]

- Avoid unauthorized redirect loops. [jone]
- Add an aggregated per dossier attach to email event on OC attach actions. [Rotonen]
- Added a document status JSON REST endpoint [Rotonen]
- Fix some common i18n issues:

  - Homogenize full stops at the end of sentences.
  - Remove trailing spaces
  - Remove trailing colons appearing only in source or translation
  - Homogenize use of punctuation marks in french translations (no space before colon / question marks)

  [lgraf]

- Fix manipulating the tag config of the keywordwidget in the dossier template form. [mathias.leimgruber]
- Add missing trash-tab in template folder. [elioschmutz]
- Fix refusing a multi-adminunit forwarding. [elioschmutz]
- Meeting: add proposal template tab to templates folder. [jone]
- Support simple css colornames in the colorization viewlet. [phgross]
- Dossierdetails PDF: Fix indentation of dossier metadata table. [lgraf]
- Move the attach to email action to second position, after the copy action. [elioschmutz]
- OGGBundle import: Make sure persistent changes that re-enable LDAP are
  always committed. [lgraf]
- Handle oc-attaching of mails. [phgross]
- Meeting: add new "Proposal Template" FTI. [jone]
- OGGBundle import: Don't use a separate ZODB connection to issue sequence
  numbers in order to avoid conflict errors. [lgraf]
- Implement a more generic gridstatestorage adapter. [elioschmutz]
- Bundle import: Don't commit "before post-processing". [lgraf]
- Allow get prefills for the CompleteSuccessorTaskForm. [elioschmutz]
- Fix sortorder of repository favorites in the treeportlet.
- Make sure GEVER specific customizations works during bundle import. [phgross]
- Unify file action button logic. [Rotonen]
- Replaced disposition tabbedview with a simple browserview. [phgross]
- Refactor: Use ZCML for registering reference number adapters for consistency. [jone]
- Also whitelist 'customlogoright' for unauthenticated access. [lgraf]
- Fix translation for the journal pdf title. [phgross]
- Add the document title to the OC attach payloads. [Rotonen]
- Skip comment for Document Sent entries in the dossiers journal pdf representation. [phgross]
- Make (all) PDF views customizable by having them dynamically provide their
  request layers instead of hardcoding them. [lgraf]
- Meeting: add a "Word implementation" feature flag. [jone]
- Implement task comment syncing between predecessor successor pairs [elioschmutz]
- Fix scrollbar of tree view portlet. [Kevin Bieri]
- Add state filters to user listings. [deiferni]
- Fix UnicodeDecodeError if uploading a .msg email with an umlaut in the filename
  to a dossier. [elioschmutz]
- Add a new checkbox on a repository-folder to choose if a user is allowed
  to add businesscase-dossiers or not. [elioschmutz]
- Add api-link to footer viewlet. [elioschmutz]
- Adjust title and label of dossiers journal PDF representation. [phgross]
- Improve title and TeX template for removal protocol. [phgross]
- Enable keywordswidget for IDocumentMetadata behavior.  [elioschmutz]
- Add functionality to comment a task. [elioschmutz]
- Refactor: Use SQLFormSupport class for: Meeting and Member [elioschmutz]
- Add OC multiattach functionality to tabbed view document listings. [Rotonen]
- Refactor OC payloads to have a list of documents instead of just one. [Rotonen]


2017.1.1 (2017-03-27)
---------------------

- Make conttenttype fix upgrade step more robust. [deiferni]


2017.1.0 (2017-03-24)
---------------------

- Fix tooltip overlay links and simplify OfficeConnector JS. [Rotonen]
- Make sure qtip tooltips are destroyed on hide. [Rotonen]
- Make sure checkout link on document tooltip is only displayed for editable
  documents (e.g., not on documents in resolved dossiers). [lgraf]
- Disposition overview: Differs beetween singular/plural on
  the dossier(s) label. [phgross]
- Limit creating initial versions to documents. [deiferni]
- Protect dispose transition with a guard, that checks if any of the dossier
  has to be archived. [phgross]
- Add new transition to directly close a disposition, without any dossiers to
  archive, after appraisal. [phgross]
- Prefill responsible user for templatefolders. [elioschmutz]
- Task listing PDF: Use AdminUnit abbreviation instead of title in order to
  avoid nasty overflows caused by long admin unit titles. [lgraf]
- Get rid of unnecessary column label in extract attachments view. [lgraf]
- Allow private dossiers to be resolved. [lgraf]
- Escape dossiertemplate title_help field on display. [elioschmutz]
- Fix the common-fieldset translation in the add/edit-form if using the
  ITranslatedTitle behavior in combination with a
  dossier-type (i.e. the templatefolder). [elioschmutz]
- Fixed contenttype encoding for archival files. [phgross]
- Add missing field description for predefined_keywords
  and restrcit_keywords. [elioschmutz]
- Disable grouping for checkbox columns in tables. [elioschmutz]
- Show Keywords on dossier overview tab. [mathias.leimgruber]
- Hide columns "public trial", "receipt date" and "delivery date" from the
  documents tab in private dossiers. [jone]
- Add a journal event for attaching documents to emails via OfficeConnector. [Rotonen]
- Hide newest tasks box for private dossiers overview tabbedview view because
  it's not possible to add tasks in private dossiers. [elioschmutz]
- Fixed role guards for dossier's offer transition. [phgross]
- Make return transitions from offered state not available
  as transition actions. [phgross]
- Allow only archivists and managers to finalize the appraisal. [phgross]
- Disallow readers to see dispositions. [phgross]
- Remove unused tasktemplate table draggable column. [elioschmutz]
- Add the mail-in address of the parent dossier of a document as a BCC field to
  OfficeConnector email attach action payloads when said dossier is open. [Rotonen]
- Reset end date when reactivating a resolved or activating
  an inactive dossier. [phgross]
- Implement quota for private folder. [jone]
- Add restriction possibility for dossier templates on a
  specific repositoryfolder. [phgross]
- The document redirector now handles newstyle OC URLs. [Rotonen]
- Set preserved as paper to false for generated journal pdfs. [phgross]
- Disposition overview: Fix tooltips for appraisal buttons. [phgross]
- Disposition overview: Hide subtitles (active or inactive dossiers)
  when list is empty. [phgross]
- Fix missing table-column width for checkbox column. [elioschmutz]
- OGGBundle: Add support to map local role principal names during
  import based on ingestion settings. [lgraf]
- Display archival value in the repositoryfolder byline. [phgross]
- LDAP util: Skip referrals that are supposed to be hunted by client-chasing. [lgraf]
- Extend searchable text with dossier keywords. [deiferni]
- OfficeConnector now gets given the latest working copy of a file instead of
  the latest checked in copy of a file. [Rotonen]
- Update ftw.keywordwidget from 1.1.1 to 1.1.2 to fix an ie11 issue. [elioschmutz]
- Add scaffolding to OC checkout payloads in anticipation of plone.api direct
  file uploads. [Rotonen]
- Improve disposal of inactive dossiers: [phgross]

  - Set end date to current date when deactivating a dossier.
  - Display inactive dossiers in a separate listing on the disposition overview.
  - Preappraisal: Handle inactive dossier always as not archival worthy.

- Protect dossier destruction with a separate permission 'Destroy Dossier'. [phgross]
- OGGBundle: Don't reindex during pipeline.
  Have reindexing only happen once per object instead at the end of the
  pipeline. [lgraf]
- Fix updating the proposal attachement-list after submitting
  a new document. [elioschmutz]
- OGGBundle import: Validate max nesting depth for repositoryfolders
  and dossiers. Failure to validate will be logged in validation report,
  but otherwise doesn't affect import. [lgraf]
- Fix an error when creating a SIP export of documents without a file. [phgross]
- Remove an unnecessary JSON parse step from OfficeConnector JS. [Rotonen]
- OGGBundle reports: Include summary sheet containing import duration,
  time of import and bundle name. [lgraf]
- Add 'mock OfficeConnector' tests for attach and direct checkin APIs [Rotonen]
- A new API endpoint for OfficeConnector direct checkin payloads [Rotonen]
- Issue newstyle OfficeConnector URLs for direct checkins [Rotonen]
- A new API endpoint for OfficeConnector attach payloads [Rotonen]
- Issue newstyle OfficeConnector URLs for attaching to email [Rotonen]
- Fix OfficeConnector URLs for IE11 [Rotonen]
- Implement several display improvements for the Dossier note overlay
  according to the feedback of @phabegger. Check #2624 for details. [mathias.leimgruber]
- Compare strings in the dossier-comments-overlay newline
  encoding insensitive. [elioschmutz]
- Improve removal protocol title. [phgross]
- Hide 'Date of completion'-field on tasks add-form. [elioschmutz]
- Introduce new feature: SPV Zip-Export. [mathias.leimgruber]
- Disallow closing dispositions for archivists. [phgross]
- Make dossiers collabsible and hide them by default on the
  disposition overview. [phgross]
- List repositories alphabetically on the disposition overview. [phgross]
- Display archival value of repositories on the disposition overview. [phgross]
- Fix an error if the user tries to unlock a referencenumber in the
  referenceprefix manager which is still in use.
  The user will see an error status-message instead
  the full error-traceback. [elioschmutz]
- Allow add root content only for managers. [elioschmutz]
- Fix newstyle OfficeConnector URL support for file tooltips and Bumblebee
  overlays. [Rotonen]
- Rename portal-type opengever.dossier.templatedossier to
  opengever.dossier.templatefolder. [elioschmutz]
- Reindex SearchableText after changing the comment
  thru the overlay. [mathias.leimgruber]
- Adjust german translation for dossier template. [elioschmutz]
- Rename dossiertemplate wizard button from "save" to "continue". [elioschmutz]
- OGGBundle reports: Implement XLSX validation report. [lgraf]
- OGGBundle reports: Also store raw JSON data for errors and stats. [lgraf]
- FileLoader: Add support for loading files from UNC paths. [lgraf]
- Rename translation for "Dossier with template" and reorder it in
  the factories-menu. [elioschmutz]
- Introduce new feature: Restrict Keywords for DossierTemplates. [mathias.leimgruber]
- Introduce new feature: Predefined Keywords for DossierTemplates. [mathias.leimgruber]
- Introduce new feature: Use ftw.keywordwidget for Dossier and
  DossierTemplate Keywords. [mathias.leimgruber]
- OGGBundle pipeline: Implement basic reports for imported objects. After
  a bundle import, a quick ASCII summary and a much more detailed XLSX
  report will be generated. [lgraf]
- Fix send_documents view on the inbox.
  Allows the functionality to save sent files in the dossier
  only for IDossierMarker-types. [elioschmutz]
- Use a request layer instead of monkey patch to disable automatic creation
  of initial versions. [lgraf]
- Do intermediate commits during creation of initial versions. This addresses
  a performance issue where the time to write initial versions increases
  exponentially with the number of previous initial versions created in the
  same transaction. [lgraf]
- Defer creation of initial versions to end of pipeline by creating a
  dedicated section for post-processing steps. [lgraf]
- OGGBundle pipeline: Fix suppression of automatically created initial
  versions by moving the disabled-initial-version section after the
  resolveguid one. [lgraf]
- Add a title_help field for dossiertemplates. [elioschmutz]
- Fix label translation and improve readability of the values in appraisal
  column in the excel export of a disposition. [phgross]
- OGGBundle test assets: Add some tests and assets to test/demonstrate
  behavior in case of business rule violations. [lgraf]
- OGGBundle schemas: Restrict allowed workflow states even further.
  We don't currently support migration to most of non-active states, so
  let's not advertise them. [lgraf]
- Add tests for Sphinx docs builds. [lgraf]
- Fix error on agendaItemController update. [Kevin Bieri]
- OGGBundle schemas: Include enums for valid review_states. [lgraf]
- OGGBundle import: Implement setting workflow state for imported objects. [lgraf]
- Add review state column and state filter to disposition listings. [phgross]
- Fix holey bumblebee fallback svg icon. [Kevin Bieri]
- Fix rendering of new agenda points in IE11. [Kevin Bieri]


4.15.7 (2017-09-25)
-------------------

- OGDS update: Truncate purely descriptive user fields. [lgraf]
- Include ftw.usermigration and implement additional user migrations:

  - OGDS User references
  - Plone Tasks
  - Private Folders
  - Checked out documents
  - Repository favorites

  [lgraf]


4.15.6 (2017-05-09)
-------------------

- Allow upgrades-api access through command line tool. [jone]


4.15.5 (2017-05-09)
-------------------

- Improve view permissions. [jone]


4.15.4 (2017-03-20)
-------------------

- Allow private dossiers to be resolved.
  [lgraf]

- Fix permission issue if user tries to trash a document in a private dossier.
  [elioschmutz]

- Allow certain z3c forms to be prefilled via GET requests. This is required
  after the introduction of Products.PloneHotfix20160830.
  [lgraf]

- Include Hotfixes in development and test buildouts.
  [lgraf]


4.15.3 (2017-03-13)
-------------------

- Make containing_dossier indexer more defensive in order to account for an
  odd corner case during upgrades.
  [lgraf]


4.15.2 (2017-03-09)
-------------------

- No longer set incorrect contentType for drag-drop uploaded mails. [deiferni]

- Make sure the breadcrumb title tooltip only gets loaded if a data-uid attribute is present.
  [mathias.leimgruber]

- Fix off-by-one bumblebee preview image for document versions. [deiferni]

- Caching: enable tabbedview etag value. [jone]

- Translate missing "open detail view" in bumblebee-overlay.
  [elioschmutz]

- Allow `Administrator` to view and edit private dossiers and private
  folders.
  [deiferni]


4.15.1 (2017-02-07)
-------------------

- Update footer links. [jone]

- Fixed retention period calculation for dossiers closed at the first of january.
  [phgross]


4.15.0 (2017-02-07)
-------------------

- Introduce new feature: Direct edit dossier comments/note thru
  a link in the byline (Opens overlay).
  [mathias.leimgruber]

- Fix broken link and missing translation for add participation label.
  [deiferni]

- Load ZCML of plone.rest before using plone:service directive.
  [lgraf]

- Modified opengever.document to conditionally use the new Office Connector
  functionality.
  [Rotonen]

- Added the preliminary release of the opengever.officeconnector subproduct,
  which only provides the attach-to-outlook functionality for now.
  [Rotonen]

- Change pre appraisal handling and allow appraisal per repository.
  [phgross]

- Remove breadcrumb_title from metadata.
  [mathias.leimgruber]

- Disable LDAP during OGGBundle import to avoid costly LDAP lookups.
  [lgraf]

- Fixed SIP package name, include disposition transfer number if exists.
  [phgross]

- Fix sorting for documents in template dossier "documents" tab.
  [lgraf]

- Remove ftw.footer, replace with static footer viewlet. [jone]

- OGGBundle pipeline: Implement setting of local roles and blocking
  of local role inheritance.
  [lgraf]

- OGGBundle pipeline: Assign nav tree portlets for imported repo roots.
  [lgraf]

- OGGBundle loader: Strip extension for title if necessary.
  [lgraf]

- OGGBundle constructor: Support setting local reference number part
  for dossiers (when provided by JSON item).
  [lgraf]

- Include REST API in mainline GEVER:

  - Introduces a new role APIUser
  - By default, only the Manager and APIUser roles have the "plone.restapi: Use REST API" permission
  - The APIUser role isn't assigned to any users or groups by default

  [lgraf]

- Add notifications support for dispositions.
  [phgross]

- Adjust dossiers retention expiration calculation.
  [phgross]

- Disallow record manager to archive a disposition.
  [phgross]

- Disallow archivist to dispose a disposition.
  [phgross]

- Display dossiers grouped by repository on the disposition overview.
  [phgross]

- Hide dossiers offer and archive transition from the action menu.
  [phgross]

- Make transfer number only editable for archivists and managers.
  [phgross]

- Make sure reference number sorters also support sorting
  repofolder-only numbers (i.e., no dossier/document parts).
  [lgraf]

- Extend OGGBundle fileloader to handle mails correctly.
  [lgraf]

- Add dossiertemplate tabbedview views.
  [elioschmutz]

- Install collective.indexing.
  [mathias.leimgruber]

- Protect date of cassation and submission with a separate edit permission.
  Only managers should be allowed to edit those dates.
  [phgross]

- Install and configure plone.app.caching. [jone]

- Add doc-property ogg.document.document_type for documents.
  [deiferni]

- Limit document selection when creating a manual journal entry.
  Only documents inside the dossier are selectable.
  [phgross]

- Make sure DossierPathSourceBinder limits selectable objects also for
  the autocomplete widget.
  [phgross]

- Include organization name in org-role addresses.
  [deiferni]

- Show expired filter for managers and record managers only and hide it on
  subdossier listings.
  [phgross]

- Use the DeactivatedCatalogIndexing contextmanager while generating dossiers from
  a dossiertemplate to improve the performance.
  [elioschmutz]

- Patch CMFCatalogAware object to improve performance.
  [elioschmutz]


4.14.1 (2016-12-15)
-------------------

- Add get_filename method to documents and mails.
  [deiferni]

- Adjustments for the dossiertemplates:

  - Protect dossiertemplate wizard with opengever.dossier: Add businesscasedossier permission.
  - Remove workflow for DossierTemplate.
  - Hide DossierTemplate from navigation.
  - Remove unused skip_defaults_fields for ObjectCreatorCommands.

  [elioschmutz]

- Creates successor-tasks of forwardings with a default task type.
  [phgross]

- Display former contact id in the byline of contacts.
  [phgross]

- Implement basic pipeline for OGGBundle import.
  [deiferni, lgraf]

- Improved and reworked closing mechanism of `for information`
  multi-adminunit tasks.
  [phgross]


4.14.0 (2016-12-12)
-------------------

- Add new refuse transition to disposition workflow.
  [phgross]

- Fixed select_all selection for ProxyTabbedViews as the document listings.
  [phgross]

- Fixed schemamigration AddOrgRoleParticipations for deployments with MySQL
  backend.
  [phgross]

- Refactor CreateDocumentCommand and CreateEmailCommand.
  [elioschmutz]

- Enable dossier templates for local development ( examplecontent)
  [elioschmutz]

- Add sample dossiertemplate to examplecontent.
  [elioschmutz]

- Create recursively documents and subdossiers when adding a dossier from template
  [elioschmutz]

- Enable zip exports for tasks
  [Rotonen]

- Hide private root from breadcrumbs.
  [deiferni]

- Prevent that too long proposal titles can be entered on meeting view.
  [deiferni]

- Ensure consistent collective.quickupload configuration across all
  our installations.
  [deiferni]

- Make sure that items of a TOC are sorted as well.
  [deiferni]

- Use ftw.zipexport events for journalizing Dossier zip exports per originating
  Dossier, Per Document
  [Rotonen]

- Add a wizard to add a dossier from a dossiertemplate.
  [elioschmutz]

- Add entry point to run OGGBundle import from console via
  bin/instance import <path_to_oggbundle>
  [lgraf]

- Add folder-factory actions to add a dossier from a dossiertemplate in a repository-folder.
  [elioschmutz]

- Add a whitelisted schema generator for dossiertemplates to avoid duplicate
  schema-definitions
  [elioschmutz]

- Add removal protocol PDF export for dispositions.
  [phgross]

- Replace INameFromTitle behavior with adapter for repository roots.
  [deiferni]

- Add separate permission "Download SIP Package".
  [phgross]

- Add missing i18n_domain entries into subproduct configure.zcml files in
  order to squelch UserWarning messages bleeding into test output.
  [Rotonen]

- Block log levels DEBUG and INFO from bleeding into test output.
  [Rotonen]

- Add new role Archivist and let them see dispositions and offered and
  archived dossiers.
  [phgross]

- Unprotect all buckets when unprotecting a btree.
  [phgross]

- Add templatefolder-tab for displaying dossiertemplates.
  [elioschmutz]

- Make disposition title editable, but prefill it with a default value.
  [phgross]

- Replace reference field with a transfer_number field on disposition schema.
  [phgross]

- Add initial dossiertemplate type.
  [elioschmutz]

- Switch schema dumps to JSON schema.
  [lgraf]

- Update task workflow, allow "Contributor" to "Access contents information" of a task.
  This is necessary to allow editing of related documents when documents inside a task
  are referenced from a second task in the same dossier.
  [deiferni]

- Add attachment information of documents attached to proposals to procotol json.
  [deiferni]

- Use correct dossier byline for meeting dossiers.
  [deiferni]

- Added excel export functionality to document listings
  [Rotonen]

- Add dossier resolving jobs:

  - Trigger archival_file conversion.
  - Purge the trash of the dossier.
  - Generate a PDF representation of the dossiers journal and file as a regular document in the dossier.

  [phgross]

- Added eCH-0160 model and export functionality.
  [phgross]

- Register OGDefaultView for all contenttypes, to hide the form
  helpers in tasks detailview.
  [phgross]


4.13.0 (2016-11-14)
-------------------

- Fix setting of default values for quickuploaded documents.
  [lgraf]

- Fix public_trial being hidden on document views after visiting a dossier.
  [Rotonen]

- Update collective quickupload to 1.9.0 to prevent construction of partial files.
  [deiferni]

- Fix dossier links in proposal overviews.
  [Rotonen]

- Provide repository based table of contents for all agenda items of a period
  per committee.
  [deiferni]

- Use flat buttons in tasks and proposals actionmenu.
  [Kevin Bieri]

- Added an issuing org_unit column to excel exports of tasks
  [Rotonen]

- Provide alphabetical table of contents for all agenda items of a period
  per committee.
  [deiferni]

- Add a new setting for opening links to PDF files in new tabs/windows
  [Rotonen]

- Simplified the German locale string for opengever.document help_document_date.
  [Rotonen]

- Fixed manual journal entry creation when users are selected as contacts.
  [phgross]


4.12.0 (2016-11-03)
-------------------

- Fix document preview size
  [Kevin Bieri]

- LDAPSearch utility: Also respect _extra_user_filter property during OGDS sync.
  [lgraf]

- Make period start/end date required.
  [deiferni]

- Add a tab to list all periods of a committee.
  [deiferni]

- Fix filterbox for journal entries:
  Filtering now also works properly for comments and actor fields.
  [lgraf]

- Copy participations whenever a dossier is copied.
  [deiferni]

- Add participations box implementation to dossier overview for the new
  contact implementation.
  [phgross]

- Show statusmessage and redirect back to document when calling a checkin
  view without selecting documents.
  [phgross]


4.11.0 (2016-10-19)
-------------------

- Show warning message when adding a repositoryfolder to a leafnode
  which already contains dossiers.
  [phgross]

- Check allowedContentTypes before pasting objects from clipboard
  to avoid pasting dossier into branch nodes.
  [phgross]

- Use ftw.tabbedview 3.5.4 to fix issue with duplicate history-entries.
  The user no longer has to press the browser-back button twice on
  tabbed-views.
  [deiferni]

- Readd prepoverlay.js, was removed by mistake.
  [phgross]

- Purge reference number mapping when dossiers are pasted.
  [deiferni]

- Fix extracting attachments for mails in inboxes.
  [deiferni]

- Fix bumblebee download view delivering wrong file for checked out documents.
  [deiferni]

- Use ooxml_docprops force mode to overwrite properties of a wrong type.
  [deiferni]

- Add bumblebee-flag option to policytemplates.
  [phgross]

- Fix XSS vulnerability in proposal overview.
  [phgross]

- Fix sorting in the journal listing.
  [phgross]

- SchemaDumper: Include max_length for Stringish field types.
  [lgraf]

- Add new functionality "Private Dossier, a private area for every user to
  create his private dossiers and store and edit private documents there.
  [phgross]

- Group related persons by active state in the organization detail view.
  [phgross]

- Sort participations alphabetically on participants title.
  [phgross]

- Change Person label to `Name Surname` instead of `Surname Name`.
  [phgross]

- Implement SQLSchemaDumper and also dump schemas for common SQL types.
  [lgraf]

- Improve performance of person listing, using eager loading strategy.
  [phgross]

- Add department field to org-role.
  [deiferni]

- Make mailaddress, url and phone_number required.
  [phgross]

- Added contact syncer functionality to add and update contact objects
  with data from an external database.
  [elioschmutz, phgross]

- Add loading option to Controller
  [Kevin Bieri]

- Load trix lazily.

  - Update handlebars to v4.0.5

  [Kevin Bieri]

- Add field to specify recipient to document-from-template form.
  The recipient's doc-properties will be written to the created file.
  [deiferni]

- Don't fire save_reference_number_prefix() handler twice. IObjectAddedEvent
  inherits from IObjectMovedEvent, so registering it on IObjectMovedEvent
  is enough.
  [lgraf]

- Enable task-templates for meeting-dossiers.
  [deiferni]

- Fix policytemplate when creating a policy with disabled meeting feature
  and without any templates.
  [phgross]

- Setup: Keep track of reference number to path mappings *per repository root*.
  [lgraf]

- Enable sql-participation for ogds-users in dossiers.
  [deiferni]

- Display former_contact_id in the contact selection field and make it searchable.
  [phgross]

- Add country field to contact addresses.
  [deiferni]

- Add POC officeatwork integration endpoints to GEVER.
  [deiferni]

- Add new form to add a manual journal entry.
  [phgross]

- Add new column former contact id to the contact listings.
  [phgross]

- Include OrgRole participations in organizations and persons participation listing.
  [phgross]

- Prevent creating participations for inactive contacts.
  [phgross]

- Link mail addresses and URLs in contact detail views.
  [phgross]

- Whitelist @login, @logout and @login-renew REST API endpoints for anonymous
  access on Plone site root.
  [lgraf]

- Patch transmogrify.dexterity's schema updater so it correctly sets default
  values, using our own `determine_default_value` function to determine the
  default, and `get_persisted_value_for_field` to avoid any __getattr__
  fallbacks.
  [lgraf]

- Add specific byline for persons and organizations.
  [phgross]

- Add active flag for contacts, including a separate
  column and an active statefilter on contactlistings.
  [phgross]

- Add participations for OrgRoles.
  Update model and particpation-forms to work with both, Contacts and OrgRoles.
  [deiferni]

- List participating dossiers on organization and person detail view.
  [phgross]

- [showroom] Support ftw.showroom 1.2.2 version
  [Kevin Bieri]

- Set and persist Dexterity default values:
  This is a massive overhaul that fixes the behavior around
  DX default and missing values. See PR #2118 for details.
  [lgraf]

- Display contacts URLs in the person and organization detail views.
  [phgross]

- Fix bumblebee fallback image on document overview
  [Kevin Bieri]

- Sort related persons and organizations alphabetically in contact detail views.
  [phgross]

- Add organizations column to the person listing.
  [phgross]

- Remove public_trial column from example XLSX repository sheet.
  [lgraf]

- Added participation tab and forms (add, edit, remove) using the new
  contact implementation.
  [phgross]

- Disable local tab on contactfolder when contact feature is enabled.
  [phgross]

- Move bumblebee installation script to opengever.maintenance.
  [phgross]

- Add history model for the new sql contacts.
  Add history tables for contacts (persons and organizations), addresses,
  phonenumbers, mailaddressens and urls.
  [deiferni]


4.10.6 (2016-09-12)
-------------------

- Introduce new event ObjectBeforeCheckIn to make sure all file modifications
  are done before the file gets versioned and bumblebee storing is triggered.
  [phgross]


4.10.5 (2016-09-06)
-------------------

- Fixed permission declaration for the documents tooltip view.
  [phgross]

- Fixed showroom identifier of preview thumbnails in search template.
  [phgross]


4.10.4 (2016-08-31)
-------------------

- Fix hint for local changes.
  [Kevin Bieri]


4.10.3 (2016-08-31)
-------------------

- Fix performance issues for trix in IE11.

  - Update trix to 0.9.9
  - Throttle `trix-update` event

  [Kevin Bieri]


4.10.2 (2016-08-30)
-------------------

- Fix wrong pin position when trix content has been changed.
  [Kevin Bieri]


4.10.1 (2016-08-29)
-------------------

- [showroom] Fix document overview on searchpage
  [Kevin Bieri]


4.10.0 (2016-08-23)
-------------------

- Fix/update script for bumblebee activation.
  Add feature to calculate bumblebee checksums for archived documents.
  [deiferni]

- Fix showroom CSS loading order
  [Kevin Bieri]

- Fix UnicodeDecodeError in contentlisting render_link method.
  [phgross]

- Fix a bug where a proposal would "disappear" when moving its parent dossier.
  [deiferni]

- Conditionally display iframe for bumblebee document preview
  [Kevin Bieri]

- Improve bumblebee integration in the search results page:

  - Change document link to document overview.
  - Display document tooltip on document links.

  [phgross]

- Deactivate 'Authentication' capability for LDAP plugin during setup for
  production deployments.
  In production, auth will always be performed by CAS portal.
  [lgraf]

- Document Tooltip:

  - Add label to the thumbnail link.
  - Link breadcrumbs in document tooltip.
  - Improve tooltip position.

  [phgross]

- Link dossier title in bumblebee overlay.
  [phgross]

- Add new tabs `Persons` and `Organizations` to the contactfolder tabbedview.
  [phgross]

- Display download_copy link in the tooltip also on mails.
  [phgross]

- Make tabbedview filter on sqltables listings case insensitive.
  [phgross]

- Fix security-issue to cross-delete and update agendaitems.
  [elioschmutz]

- Fix issue with wrong document-number: Move showroom hidden-link
  outside the tooltip-trigger div.
  [phgross]

- Add an email-form for opengever contacts.
  [elioschmutz]

- Fix sticky heading in order to a refactoring of the baseclass.
  [elioschmutz]

- Fix FileOrPaperValidator in case where the file gets removed in the edit form.
  [phgross]

- Add first version of the organization view and
  link persons and organizations in the listings.
  [phgross]

- Fix Title for Commitee and Proposal.
  Return utf-8 instead of unicode, as required by plone.
  [deiferni]

- Link preview-thumbnail in the document tooltip to the bumblebee overlay.
  [phgross]

- Show pdf icon for preview link in document versions tab.
  [deiferni]

- Bump lxml to 3.3.1 and get rid of lxml import warnings and openpyxl user warnings.
  [deiferni]

- Change document linking to document overview, instead of the
  bumblebee overlay.
  [phgross]

- Use qtip2 library for document preview tooltip

  - Load tooltip data asynchronously.

  [phgross, Kevin Bieri]

- Adjust overlay according to customer feedback
  Add link to document title in overlay
  Trigger close when clicking on the backdrop of the overlay
  [Kevin Bieri]

- Add a journal entry when downloading pdf files from bumblebee.
  [deiferni]

- Add edit- and add-form for a person.
  [elioschmutz]

- Let bumblebee take precedence over pdfconverter.
  Don't consider pdfconverter being available when bumblebee feature is enabled.
  [deiferni]

- Add participation model for contacts.
  [deiferni]

- Drop duplicated description and contact_type columns on Organization
  and Person model.
  [phgross]

- Add first simple version of the person view.
  [phgross]

- Display a hint in livesearch results view when the query could
  not be processed.
  [deiferni]

- Make transition required for the addresponse view.
  [deiferni]

- Create example contacts and organizations when setting up a
  gever with examplecontent.
  [phgross]

- Don't store documents that are not digitally available in bumblebee.
  [deiferni]

- Don't allow protocols for a meeting to be generated twice.
  [deiferni]

- Configure offset for showroom overlay.
  [deiferni]

- Include preview thumbnail in the document tooltip.
  [phgross]

- Whitelist '@@health-check' view on site root.
  [lgraf]

- CSRF: Whitelist context portlet assignment annotations.
  [lgraf]

- Also provide the meeting location in JSON data for protocols.
  [deiferni]

- Add SQL Model for new contact implementation.
  [phgross]

- Fix bumblebee-overlay current item and next/prev in search view.
  The textlink and the image overlay will now open the same showroom item.
  That means, the counter will show the correct current number.
  If you press the next/prev button, it will jump automatically to
  the next search entry.
  [elioschmutz]

- Improve document overview functions layout.
  [elioschmutz]

- Bumblebee integration for tasks and SPV.
  [phgross]

- Reworked and centralized the document link generation using the
  IContentListing adapter.
  [phgross]

- Catch up with refactoring of ftw.bumblebee.
  [deiferni]

- Implement bumblebee overlay for the versions-tab.
  [elioschmutz]


4.9.3 (2016-07-19)
------------------

- Addded french translations.
  [phgross]


4.9.2 (2016-07-07)
------------------

- Fix scrollspy auto scrolling.
  [Kevin Bieri]


4.9.1 (2016-07-01)
------------------

- Add BTree consistency check to the CleanupRelationsCatalog upgradestep and
  fix the BTree if necessary.
  [phgross]


4.9.0 (2016-06-28)
------------------

- Add gallery-view for trash-tab.
  [elioschmutz]

- Adjust decision in TranslatedTitleBrain if the the language specific title
  should be used or not. It checks now if the portal_type supports TranslatedTitle,
  by making a lookup in the fti with the help of the brain's portal_type.
  [phgross]

- Add helper script to generate JSON files for component import
  into Weblate.
  [lgraf]

- Remove i18n markup for strings in opengever.setup:
  We're never going to translate those.
  [lgraf]

- Remove empty help texts (field descriptions that were i18nized
  but never got translated).
  [lgraf]

- Fixed bumblebee overlay browse functionality for the document extjs listing.
  [phgross]

- Use non self-closing br tags in trix transform.
  [deiferni]

- Increase maximum string length in sentry extra data for errors reported
  by trix2sablon.
  [deiferni]

- Fixed textfilter in the documents gallery view.
  [phgross]

- No longer hide `Open as PDF` link in the bumblebee overlay for mails.
  [phgross]

- Implement sticky trix editor toolbars.
  [Kevin Bieri]

- Fixed icon tooltip in document listings.
  [phgross]

- Adjust registered bumblebee-events.
  The bumblebee events changed. So we have to change this in opengever.core too.
  [elioschmutz]

- Fixed translation of the bumblebee gallery/list icons.
  [phgross]

- Getting default with AQ: Change lookup order so that we first
  try to properly adapt the context to the schema interface.
  [lgraf]

- Reworked the trigger tasktemplatefolder form:
  Replaced old custom form with a z3c wizard-form and allow to attach documents.
  [phgross]

- Strip elements that are not supported by Sablon from trix-input.
  Also log to sentry when this happens. We don't expect markup to
  be stripped since the markup generated by trix should always be
  supported by Sablon.
  [deiferni]

- Disallow closing or deactivating a dossier which contains active proposals.
  [phgross]

- Remove fallback-image for mails because bumblebee supports .eml mimetiype now.
  [elioschmutz]

- Make sure references to spinner.gif are absolute URLs.
  [lgraf]

- Add lock-info and checkout-info viewlets to bumblebee-overlay.
  [elioschmutz]

- Lock excerpts in the dossiers and sync updates to the
  excerpt in a meeting/submitted proposal to the excerpt copy
  in the dossier.
  [deiferni]

- Simplify protocol download button in meeting view.
  Only download the exisiting protocol without regenerating it with sablon.
  [phgross]

- Fix error: AttributeError: 'DocumentsProxy' object has no attribute 'select_all'.
  [elioschmutz]

- Fix public_trial indexer.
  (Adapt object to behavior interface before accessing attribute)
  [lgraf]

- Lock submitted documents after proposal submission.
  [deiferni]

- Fix links to checkin actions from overlay.
  [deiferni]

- Fix bumblebeeability check for documents that are not digitally available.
  [deiferni]

- Update bumblebee when documents are checked in and reverted
  to a previous version.
  [deiferni]

- Display repositoryfolder description above the byline.
  [phgross]

- Change background color of download confirmation dialog to partial transparent black.
  [Kevin Bieri, phgross]

- Fix document overview.
  [Kevin Bieri]

- Fixed textfiltering for task listings on PostgreSQL.
  [phgross]

- Prevent updating bumblebee checksum for checked out documents.
  This no longer updates the preview pdf and thumbnails for checked
  out documents and prevents that other users can see the working
  copy.
  [deiferni]

- Added new attribute decision_draft to proposal, which allows to
  prefill the agendaitem's decision.
  [phgross]

- Add support for single showroom items.
  [Kevin Bieri]

- Fixed label for the pending statefilter on task listings.
  [phgross]

- Mark mails as IBumblebeeable.
  [elioschmutz]

- Strip whitespace when saving proposals or a protocol.
  [deiferni]

- Added new tab "My Proposals" to the personal overview.
  [phgross]

- Show correct total document size in the showroom overlay if opening files
  from the list-view.
  [elioschmutz]

- Fix: Add GeverTabbedviewDictStorage adapter to handle bumblebee proxy views.
  Normally, the tabbedview is storing the last state (i.e. sorting) per user per tab.
  Since bumblebee requires a proxy view to determine if the list or the gallery should be
  rendered, the mechanism to store and get the state was broken.
  [elioschmutz]

- Initialize the showroom correctly for dynamically loaded items in the search-view.
  [elioschmutz]

- Reindex documents after adding ftw.bumblebee.interfaces.IBumblebeeable to
  make sure object_provides is up to date.
  [deiferni]

- Boost bumblebee overlay performance by omitting diazo and improving
  template condition expressions with nocall:.
  [deiferni]

- Dont quote advanced parameters twice.
  Fixes a bug where certain terms would not be found.
  [deiferni]

- Add bumblebeeoverlay for documents on the overview tab.
  [elioschmutz]

- Use global pagesize parameter for batchsize in gallery-view.
  [elioschmutz]

- Make proposals cancellable.
  Add model workflow to cancel/reactivate proposals.
  Add statefilter for a dossiers proposals tab to only display
  active proposals.
  [deiferni]

- Enables to replace a checked out document by Drag'n'Drop.
  [phgross]

- Redirect to meeting tab when a meeting has been created.
  [deiferni]

- Decouple default values for fields from any forms (as much as possible).
  This is necessary groundwork for later changes that will make sure that
  default values also get set during programmatic content creation.
  [lgraf]

- Refactor opengever.tabbedview:

  - Provide better base classes for tabs
  - Expose base classes in opengever.tabbedview instead of a submodule
  - Provide support for state filters in all tabs with minimal effort
  - remove duplicate/dead code
  - drop unused clients-listing

  [deiferni]

- Log CSRF incidents to Sentry (if possible).
  [lgraf]

- Add committee model workflow, to allow de- or reactivating a committee.
  [phgross]

- Bumblebee: Implement gallery preview image fallback.
  [Kevin Bieri]

- Update Bumblebee integration for API v3 support.
  [phgross]

- Add batching for the bumblebee gallery-view.
  [elioschmutz]

- Fix tests for GeverJSONSummarySerializer: The `member` attribute
  has been renamed to `items` in plone/plone.restapi#107.
  [lgraf]

- Add 'open as pdf' link in the bumblebee overlay.
  [elioschmutz]

- Add Visual Search (Bumblebee) integration using ftw.bumblebee.

  This new feature can be toggled with a feature flag.
  We introduces two new dependencies, ftw.bumblebee to provide the base
  integration and for communicating with the bumblebee service and
  ftw.showroom display the overlay.

  The initial integration also adds the following UI components:

  - A gallery with small preview-thumbnails for documents of a dossier
  - A large preview thumbnail on the document overview
  - Small preview-thumbnails for search-results
  - An overlay to read the document that opens when clicking on
    one of the aforementioned thumbnails and a document in a document
    listing (tab)

  [elioschmutz, Kevin Bieri, deiferni]

- Fix sample protocol template control structures.
  [deiferni]


4.8.1 (2016-05-03)
------------------

- Update trix to 0.9.6
  [Kevin Bieri]


4.8.0 (2016-05-02)
------------------

- Only show active sub-dossiers in dossier navigation.
  [deiferni]

- Clean up our monkey patches.
  [lgraf]

- Fix bug in redirect when no templatedossier is found.
  [phgross]

- Create and update proposals and documents with elevated privileges,
  when submitting proposal, add or update submitted documents or
  copy back excerpt documents.
  [phgross]

- Exclude email from sablon variable fullname and add a email variable instead.
  Note: The sablontemplates have to be updated after installing this release,
  when the email is still needed in the protocoll.
  [phgross]

- Enable zip-export for personal overview.
  [deiferni]

- Reworked XLSReporter using the openpyxl library instead of xlwt, to support
  xlsx creation.
  [phgross]

- TranslatedTitleBrain: Also use Missing.Value as indicator that a brain
  has no translated title, and should therefore return the regular title.
  [lgraf]

- Make default value for IDossier.start a defaultFactory instead
  of a form level default.
  [lgraf]

- REST API: Customize summary representation to include

  - Translated 'title' for objects with ITranslatedTitleSupport
  - The object's portal_type

 [lgraf]

- Meeting: Rename button to create paragraphs to "insert".
  [deiferni]

- Fix an issue with importing no_client_id_grouped_by_three formatted
  repositories.
  [deiferni]

- Fix wrong from/to column labels in meeting overviews.
  [deiferni]

- Meeting Protocol:

  - Also provide the role for the meetings presidency and secretary in the JSON data.
  - Add presidency and secretary role to the example protocol sablon template.
  - Harmonize format of all participants (members, presidency, secretary).

  Note: The Sablontemplates have to be updated after installing this release!
  [phgross]

- Language Tool: Enable request content negotiation.
  [lgraf]

- Fixes sitetitle for wrapper objects.
  [phgross]

- No longer attempt to parse temporary excel files while creating repositories.
  [deiferni]

- Redirect to the members listingtab after adding a new member instead of the members detailview.
  [phgross]

- Various updates to API documentation.
  [lgraf]

- Remove unused fallback method for TranslatedTitleBrain (it has never worked so far).
  [elioschmutz]

- Fix broken TranslatedTitleBrain. It has to return utf-8 instead of unicode.
  [elioschmutz]

- Only groups where the user is a member are available to select when creating/editing committees.
  [elioschmutz]

- Fix examplecontent repositories.
  [deiferni]


4.7.4 (2016-03-23)
------------------

- No longer set start-page for documents generated as protocol excerpts.
  [deiferni]


4.7.3 (2016-03-17)
------------------

- Optimize `user_is_allowed_to_view()`.
  [buchi]

- meeting: Allow blank end date for meetings
  [Kevin Bieri]

- Show email addresses of participant in a meeting or a meeting protocol.
  [elioschmutz]

- Add API documentation (Sphinx).
  [lgraf]


4.7.2 (2016-03-10)
------------------

- Keep existing date on a protocol instead of creating a new one.
  [Kevin Bieri]

- Fix timezone mess in datetimepicker.
  [Kevin Bieri]


4.7.1 (2016-03-10)
------------------

- Implement sorter for 'no_client_id_grouped_by_three' reference number formatter.
  [lgraf]

- Activate "remove GEVER content" by default for new policies.
  [deiferni]


4.7.0 (2016-03-07)
------------------

- Add no_client_id_grouped_by_three reference number formatter.
  [deiferni]

- Make sure IRedirector JS redirects aren't unconditionally trigged when the
  user is on the @@confirm-action view.
  [lgraf]

- Meeting: Implement hint for conflicts while saving a protocol.
  [Kevin Bieri]

- Improve agenda-item workflow, allow decided agenda-items to be re-opened for
  revision. Also update excerpts when the agenda-item is revised.
  [phgross, deiferni]

- Add a fix for links from Microsoft Office applications.
  The fix hacks around office's behavior to resolve links prior to opening
  a browser. This lead to an "insufficient privileges" page being displayed if
  the user was already logged in. The fix attempts to traverse to the came_from
  url that is available to the require_login script, and if the url is traversable
  redirects to that location.
  [deiferni]

- Update locking message for locked protocols.
  [elioschmutz]

- Add a link to update an outdated document from the proposal view.
  [elioschmutz]

- Prevent creating a mail-copy in the dossier when sending documents
  from a closed dossiers.
  [elioschmutz]

- Add a custom handler to force a page reload (and thus force a
  redirect to the login form) when tabbed-view requests are redirected to
  the gever portal.
  [deiferni]

- Fix an issue where tabs on the plone site were visible as anonymous under
  certain circumstances.
  [deiferni]

- Add trix customizations to prevent accepting unsupported content.
  We don't support links, quotes, code-blocks and file uploads of any kind.
  [deiferni]

- Avoid infinite loops in find_parent_dossier() and set_default_with_acquisition()
  if context is not acquisition wrapped.
  [lgraf]

- Add an editable title to meeting objects.
  The user can set the title for a meeting manually now. Per default,
  the title will be the name of the committee and the date.
  [elioschmutz]

- Disable editing of decided agenda-items in protocol view.
  [elioschmutz]

- Avoid infinite loop in BasicReferenceNumber.get_parent_numbers() if context
  is not acquisition wrapped.
  [lgraf]

- Fixes an issue with broken db-migrations.
  Don't load proposal model in upgrade steps but use sqlalchemy expression
  api for database access.
  [deiferni]

- Activate notification-center by default.
  [elioschmutz]

- Add link in meetingoverview from unscheduled proposals to their corresponding submitted proposals.
  [elioschmutz]

- Introduce [api] extra that pulls in plone.restapi (and plone.rest).
  [lgraf]

- Change title and filename for generated excerpts.
  Old title format: Protocolexcerpt-[meetingtitle, meetingdate]
  New title format: [excerpttitle] - [meetingtitle, meetingdate].
  [elioschmutz]

- Add skip_defaults_fields for CreateGeneratedDocumentCommand.
  Fix the issue, where the object-title was always the document-title.
  [elioschmutz]

- Add link from submitted proposal to dossier if it's in the same admin-unit.
  [elioschmutz]

- Setup upgrade-step directories for all default profiles. [jone]

- Add link from proposal to meeting.
  [elioschmutz]

- Add attributes for proposal view.

  - publish_in
  - disclose_to
  - copy_for_attention

  Add additional attributes for submitted proposal view:

  - considerations
  - discussion

  [elioschmutz]

- Add link from proposal to committee.
  [elioschmutz]

- Adjust french translation 'En modification' to eCH-0039-standard 'En cours de traitement'
  [elioschmutz]

- Adjust proposaloverview view.
  Moves the document listing into the attributes-table, to gain more
  space for the table.
  [elioschmutz]

- Adjust proposal tabbedview tab.

  - Remove unused rows: 'initial_position' and 'proposed_action'
  - Add referencenumber row
  - Add meeting row: link to the related meeting if the proposal is scheduled

  [elioschmutz]

- Make a proposal's repository-folder title available as variable
  for sablon templates.
  [deiferni]

- Use autoselect for proposals add and edit view.
  [Kevin Bieri]

- Add upgrade-step to update feedback link in footer (if necessary).
  [lgraf]

- Prevent saving the protocol when it is locked by another user.
  [deiferni]

- Rename "Kommission" to more generic "Gremium"
  [elioschmutz]

- Display versions tab for sablon templates.
  [deiferni]

- Translate "Standort" to "Sitzungsort" for Meetings.
  [elioschmutz]

- Change translation for label_publish_in
  [elioschmutz]

- Update policy templates: Creates meeting portlet if enable_meeting_feature
  is true.
  [elioschmutz]

- Recycle reference numbers. When moving an object back to a previous
  parent, the previous reference number is recycled.
  [jone]

- Remove "reference_number" from catalog metadata.
  [jone]

- Prevent that the protocol form can overwrite a newer version of the protocol.
  If concurrent modifications occur we don't offer conflict resolution as of yet but
  leave the submitted form open to allow the user to take manual action.
  [deiferni]


4.6.3 (2016-01-25)
------------------

- Reduce complexity for traversing the scrollspy navigation tree.
  [Kevin Bieri]

- Add migration for trix, convert fields from markdown to html.
  [deiferni]

- Exclude non visible fields from the scrollspy navigation.
  [Kevin Bieri]

- Introduce IDuringSetup marker interface to flag a request that
  happens during GEVER setup.
  [lgraf]

- Refactor sequence number generation in order to reduce conflicts
  in content creation requests and to ensure uniqueness.
  [jone]

- Update link to feedback forum in example content and policy template footers.
  [lgraf]

- Update policy templates to include casauth plugin.
  [elioschmutz]

- Use searchable dropdown widget for adding a membership
  [Kevin Bieri]

- Display an additional column for the meeting state in the meeting overview.
  [Kevin Bieri]

- Displays hint that no documents have been generated yet.
  [Kevin Bieri]

- Update policy templates to include default committee container and initial templates.
  [deiferni]

- Transform trix input to safe_html to prevent XSS vulerability.
  Implemented for protocol page and trix widgets.
  [deiferni]

- Introduce request method on controller to pass a validator for ajax requests.
  Only show notify messages when the response does not contain a redirect statement.
  [Kevin Bieri]

- Update LDAP path in policy templates.
  [deiferni]

- meeting: Use trix as editor in proposals.
  [Kevin Bieri, deiferni]

- meeting: Use trix as editor in protocol.
  [Kevin Bieri]

- Fix opengever.meeting upgrade to 4600 for MySQL. Delete a foreign key before
  its corresponding column is removed.
  [deiferni]

- Don't create savepoints in 46xx upgrade steps - MySQL implicitly commits
  savepoints as soon as a DDL statement is emitted (similar to Oracle).
  That means we can't reliably use savepoints in upgrade paths that contain
  upgrades involving DDL.
  [lgraf]

- Remove modified_seconds index and refactor tree portlet to use default
  modified index.
  [jone]

- ZEM download: Include filename of doc in metadata by
  registering a callback for Products.ExternalEditor that
  adds the filename to the metadata during ZEM generation.
  [lgraf]

- Refactor registration of additional mimetypes.
  [lgraf]

- Change CMFEdition IDs to uuid4 instead of auto-increment.
  This reduces conflict errors.
  [jone]


4.6.2 (2015-12-22)
------------------

- Add french translation for "My portal" action.
  [lgraf]

- Show hint for unsaved local changes while editing the protocol.
  [Kevin Bieri]

- Don't use current date when editing meeting participants but the meeting's date.
  [deiferni]

- Fix an encoding issue while editing memberships.
  [deiferni]

- Show diffrent buttons for deleting or unscheduling agenda items
  [Kevin Bieri]

- Make sure that decision numbers are available when rendering excerpts.
  [deiferni]

- Don't generate decision numbers for paragraphs.
  [deiferni]

- Fixed missing `responsible` parameters in synced responses when reassigning a multi AdminUnit task.
  [phgross]

- Cluster URL: Add heuristic to determine the correct cluster base URL
  for both single- and multi-admin-unit setups.
  [lgraf]

- Make `my-portal` action use @@gever_state/gever_portal_url
  [lgraf]

- Add a `gever_state` view with traversable helper methods for use in TAL
  expressions and templates.
  [lgraf]

- Introduce the concept of a GEVER portal URL.
  [lgraf]

- Introduce the concept of a base URL for the GEVER cluster.
  [lgraf]

- Only build URL to CAS server once during setup, after that fetch it
  from the plugin when used as a base to build other URLs.
  [lgraf]


4.6.1 (2015-12-16)
------------------

- Use bootstrap datetimepicker for selecting date and time for meetings.
  [Kevin Bieri]

- Include ftw.profilehook, when required.
  [deiferni]

- Fix an issue with setting-up translated content with transmogrifiers schemaupdater.
  [deiferni]

- Fix an issue with repo-folders not stored persistently on committee after create.
  [deiferni]


4.6.0 (2015-12-11)
------------------

multilingual support
~~~~~~~~~~~~~~~~~~~~

- Added support for bilingual titles in the repositorysystem and the main elements.
  [phgross]


opengever.meeting
~~~~~~~~~~~~~~~~~

- Add periods to committees. A period represents a timespan similar to a fiscal year.

    - Display the current period on committee overview.
    - Add a wizard to close the current and create its successor.
    - Add a wizard that creates an initial period upon committee creation.
    - Each meeting is assigned a meeting number when the meeting is closed. The meeting number
      is unique per period and committee.
    - Each agenda-item is assigned a decision number when its meeting is closed. The decision
      number is unique per period and committee.

  [deiferni]

- Link committees to a repository folder and link meetings to meeting-dossiers:

    - Add a new content-type, meeting-dossier.
    - Link dossier and meeting creation, automatically create a meeting-dossier
      when a meeting is created.
    - Automatically generate Protocols into the meeting's dossier.
    - Use dossier title as default title for new proposals.

  [deiferni]

- Refactor and improve planning and holding meetings:

    - Implement clientside processing for meeting view (Controller Pattern).
    - Display date in metadata section.
    - Set all active members of a committee as meeting participants by default.
    - Add an option to decide a single agenda_item.
    - Make sure protocol exists and is updated when closing a meeting.
    - Add confirm-dialog when closing meetings.
    - Simplify meeting workflow, drop state `held`.
    - Add protocol start-page setting to meetings and include this configuration
      in JSON for documents generated by sablon.
    - Include missing items in protocol navigation.
    - Extend agenda items in protocol view with numbers.
    - Remove pre-protocols, they are now the same as protocols.
    - Remove edit restrictions, let meetings be editable until they are closed.
    - Also display a members role in a meeting's protocol.
    - Add locking support for meetings.
    - Lock protocol documents while a meeting is not closed.
    - Save dossier's reference number on proposal and display it on protocol
      form and protocol word.

  [Kevin Bieri, phgross, deiferni]

- Add permissons for meetings.

    - Add 'add Member' permission.
    - Add permissions to Committee and CommitteeContainer workflows.
    - Protect views with correct permissions instead of just View.
    - Add configurable group to committees and set local roles on a committee for that group.
    - Cleanup owner from rolemap.xml.
    - Add own role for commitee-group-members.

  [deiferni]

- Make meeting datetime columns timezone aware.
  The following columns are affected:

    - Meeting.start
    - Meeting.end
    - ProposalHistory.created

  [deiferni]

- Allow rejecting proposals from a committee. It is possible to enter an optional comment.
  [deiferni]

- No longer allow adding content to proposals.
  Add excerpt to proposal's dossier instead.
  [deiferni]

- Link meeting from meeting-dossier overview.
  [deiferni]

- Fix member edit link and refactor generating breadcrumbs for models.
  [deiferni]

- Introduce wrapper objects for members and memberships to eliminate
  traversal hacks.
  [deiferni]

- No longer show wrapper objects in pathbar.
  [deiferni]

- Fixed get_parent_dossier getter for document inside a proposal.
  [phgross]

- Remove expired locks before creating new locks to avoid integrity-errors
  during database flushes.
  [deiferni]

- Introduce a wrapper object for meetings and use it as context. So the
  traversal-hack on every meeting view can be eliminated.
  [phgross]

- Add additional columns publish_in, disclose_to and copy_for_attention
  to proposals, protocols and protocol excerpts.
  [deiferni]

- Also provide information to sablon templates whether an agenda item
  is a paragraph.
  [deiferni]

- Add a view to fill sablon-templates with sample meeting-data.
  [deiferni]


CSRF
~~~~

- Include plone4.csrffixes in order to get back on the "Plone Way" to use
  automatic CSRF protection with Plone 4. This allows use to drop some of
  our custom handling of certain cases:

    - Transforming responses with uncommon charsets
    - Our own way of marking objects for safe writes
    - Unprotecting writes to _dav_writelocks
    - Handling context portlet assignments

  [lgraf]


opengever.activity
~~~~~~~~~~~~~~~~~~

- Make sure only the new responsible gets notified by mail, when a
  task gets reassigned.
  [phgross]


miscellaneous
~~~~~~~~~~~~~

- Adjust footer links (Release-Informationen, Quellcode).
  [phgross]

- Disallow access to views on the portal root for anonymous except of login
  form and password reset.
  [buchi]

- Move plone-group creation in OrgUnitBuilder to opengever.core.
  [deiferni]

- Remove leftover related_items catalog metadata.
  [deiferni]

- Merge changes made on `minimal` repository configuration to the `municipality` one.
  [phgross]

- Let OGMail inherit from ftw.mail.mail.Mail.
  [deiferni]

- Add submodule opengever.locking which add locking support for sqlobjects.
  [phgross]

- Prevent a silently ignored key error in our PAS IAuthenticationPlugin
  for internal requests.
  [lgraf]

- No longer create RelationValue manually, this is now done by ftw.builder.
  [deiferni]


4.5.8 (2015-11-25)
------------------

- Fixes activity upgradestep for mysql. Drop foreign key first before droping
  the column when using mysql as OGDS backend.
  [phgross]

- Extend whitelist for anonymous access on siteroot.
  [lgraf, phgross]

- ResponseTransporter: fix de- and encoding of deadline changes.
  [phgross]

- Make sure reassign a task over the edit form creates a response and record an activity.
  [phgross]

- Eliminate duplicate notification, about a task acceptance, when creating a successor.
  [phgross]


4.5.7 (2015-11-03)
------------------

- Disallow access to views on the portal root for anonymous except of login
  form and password reset.
  [buchi]

- Make sure only the new responsible gets notified by mail, when a
  task gets reassigned.
  [phgross]

- Revert review_state checks when accepting or assigning a task/forwarding.
  [phgross]

- Fixed issue in Tasks `by_container` query, with similar dossier-ids.
  [phgross]

- Notification viewlet: Fix javascript for sites with disabled activity feature.
  [phgross]

- Rework notification viewlet:

    - Reimplement viewlet functionality clientside
    - Display all notifications and add endless scrolling
    - Mark notifications as read when opening the dropdown.

  [phgross]

- Notification center: Register actor as watcher instead of every single user.
  [phgross]

- Notifications: Store subscription role, on each resource <-> watcher relation.
  Do allow a fine-grained configuration for the dispatchers.
  [phgross]

- VersionsTab: Use getHistoryMetadata() instead of getHistory() to avoid
  fetching the actual versioned objects and hence improve performance.
  [lgraf]

- Extend logging of task SQL synchronisation, with tasks modification date.
  [phgross]


4.5.6 (2015-09-17)
------------------

- CSRF: unprotect initializing annotations and sequence numbers.
  [deiferni]

- Fixed bug in retention_period:
  The RetentionPeriodValidator respect the is_restricted flag now.
  [phgross]


4.5.5 (2015-09-15)
------------------

- Add NullResponseDescription fallback for responses without a transition.
  This makes the use of the ResponseDescriptions (ResponseViewlet etc.) more robust.
  [phgross]

- Fix duplicate activity recordings when a forwarding gets reassigned.
  [phgross]

- Fix Upgrade-Step that updates lexicon: The affected indexes need to be
  cleared first before rebuilding them, otherwise the lexicon might not get
  updated properly.
  [lgraf]

- Add logging to the task SQL synchronisation.
  [phgross]

- Also log object oids in csrf logs.
  [deiferni]

- Use supertabular* to render multi-page tables instead of longtable to
  fix an issue with tables breaking pages too late.
  [deiferni]

- Hide foreign part of predecessor/successor pairs in the opentaskreport listings.
  [phgross]

- Validate task title length.
  [deiferni]


4.5.4 (2015-09-08)
------------------

- No longer allow reverting document versions while documents are checked out.
  [deiferni]

- CSRF: Add view to enable and disable CSRF tracing monkey patches.
  [lgraf]

- Add debug view to trigger a plone.protect confirmation dialog.
  [lgraf]


4.5.3 (2015-09-01)
------------------

- Add detailed logging for CSRF incidents.
  [lgraf]

- Fix missing journal entry due to CSRF when downloading copy or
  pdf-preview of a document from document overview.
  [deiferni]


4.5.2 (2015-08-27)
------------------

- Disable csrf protection for CreateSuccesorForwardingView.
  [phgross]

- Make mail upgradesteps (to4500, to4501) more defensive.
  [phgross]

- ReferenceNumberPrefixAdpater: Fix conditions for lazily initialising
  PersistentMappings in annotations.
  [lgraf]


4.5.1 (2015-08-19)
------------------

- Notification mail: hide "display" label for activities without a description.
  [phgross]

- Make sure to create an RFC2047 compliant From: or To: header when sending mails.
  (By avoiding encoded-words in angle-addr or addr-spec).
  [lgraf

- Fix layout and styling in notification mail also for microsoft outlook.
  [phgross]

- Drop limitation of notifications and make notification viewlet scrollable instead.
  [phgross]

- Notification viewlet: added tooltip to the "mark as read" link.
  [phgross]

- Notification viewlet: sort notification chronologic, newest at the top.
  [phgross]

- My Notification: disable sorting for type, title and actor column.
  [phgross]

- Fixed order in dossiers factory menu.
  [phgross]

- No longer use plone's text/x-html-safe for simple markup fragments, use
  escape_html instead.
  No longer inherit from DisplayForm in task-overview, use grok.View instead.
  [deiferni]

- Fixed lookup for active TaskTemplateFolders.
  [phgross]

- Display my notification tab also for regular users.
  [phgross]

- Don't show paste action for closed dossiers.
  [deiferni]

- MyNotifications: Make `resolve_notification_link` not mix unicode and str
  in string formatting by explicitly decoding the URL from ascii.
  [lgraf]

- Use `UnicodeCoercingText` type for all previous `Text` columns.
  This makes sure we always get `unicode` back from Text columns,
  whether the backend is Oracle, PostgreSQL or MySQL.
  Depends on opengever.ogds.models >= 2.3.1.
  [lgraf]

- Use an admin-unit's public url to generate urls to resolve notifications.
  [deiferni]

- Reintroduce a monkey patch for NamedDataConverter.toFieldValue after
  pinning down plone.formwidget.namedfile back to 1.0.7. The patch ensures
  hat mime-types sent by the browser are ignored.
  [deiferni]

- Fix ftw.mail.inbound.createMailInContainer monkey patch so it
  sets message.contentType to unicode, not str (see ftw.mail#33).
  [lgraf]

- Improve notification center's error_handling.
  Catch exception during dispatching a notification separately.
  [phgross]

- No longer generate reference numbers for templatedossiers.
  Also Cleanup old generated reference numbers.
  [deiferni]

- No longer display an empty tab 'additional' on the forwarding edit page.
  [deiferni]

- Fix an issue with the open taks report action, make sure it displayed again.
  [deiferni]

- Disable inline validation.
  [phgross]

- Use correct geometry setup for landscape pdfs.
  [deiferni]

- Dossier WF: Allow 'Copy or Move' for Dossiers in closed states:
  This is necessary to be able to copy documents from closed dossiers.
  [lgraf]

- Fixed translation of PDF Preview button in document's tooltip.
  [phgross]

- Made Document's tooltip edit_direct link CSRF safe, adding the authentication token.
  [phgross]

- Fixed gever customization of sharing view, for updateSharingInfo.
  [phgross]

- Tasktemplate form: Redirects back to dossier and show statusmessage
  if no active tasktemplatefolders are registered.
  [phgross]

- Advanced search: Fix translation for filing no help text.
  [lgraf]

- Only show pending states on dossier overview.
  [deiferni]


4.5.0 (2015-08-03)
------------------

- Add CreatorMigrator that migrates creators for Dexterity objects.
  (to be used with ftw.usermigration).
  [lgraf]

- Added activity support for tasktemplates.
  [phgross]

- Use datetime formatter to display deadline label.
  [deiferni]

- Add upgrade-step to fix 'document_author' and 'title' for mails with
  incorrectly decoded header values.
  [lgraf]

- Move submitted with proposals list to its own document overview
  table row.
  [deiferni]

- Add authentication token also to the file and pdf version download link.
  [phgross]

- Prefix actor link with an icon in the participants listing.
  [phgross]

- Fix missing mail icon in mail edit view/properties view.
  [deiferni]

- Show context mimetype icon in custom no_download namedfile widget
  mode templates.
  [deiferni]

- Documents Tab: Make sure link text in "containing subdossier" column
  is HTML escaped.
  [lgraf]

- Documents Tab: Make sure document_author is HTML escaped.
  [lgraf]

- Added upgradestep wich cleanup no longer existing interfaces from the zc.relation
  catalog's interfaces_flattened mapping, to avoid pickling erros (see #1091).
  [phgross]

- Adapt SchemaMigration.is_oracle() check so it also recognizes the
  'oracle+cx_oracle' dialect.
  [lgraf]

- Make sure we always get unicode from SQLAlchemy for columns values by
  setting the `coerce_to_unicode` parameter for the cx_Oracle dialect.
  Necessary for SQLAlchemy >= 0.9.2
  See http://docs.sqlalchemy.org/en/latest/dialects/oracle.html#unicode)
  [lgraf]

- OGDS Updater: Fix some unicode errors while logging.
  [lgraf]

- Delay expensive plone upgrade that installs plone lexicon using I18N
  Case normalizer.
  [deiferni]

- Fix activity upgrade steps, don't rely on potentially dangerous imports
  from model but duplicate necessary information.
  [deiferni]

- Make `author_cache_key` also discriminate on hostname.
  This is required because this cache key is used to cache generated
  URLs, which are dependent on the hostname that is used to access the
  system (might be localhost + SSH tunnel).
  [lgraf]

- Only display link to proposal for documents in repositories.
  [deiferni]

- Show statusmessage after successfully submitting a proposal.
  [phgross]

- Autosizing textareas in the add and edit form of proposals.
  [phgross]

- OGDS Sync: Clear memberships from groups_users association table before
  importing them, so that memberships from groups that have been deleted in
  LDAP get removed from OGDS. Also deactivate groups that have been removed
  from LDAP (includes upgrade-step for new `active` column on `Group` model
  in og.ogds.models).
  [lgraf]

- Drop `ogds_log_file` product config option and instead log
  to a file with a fixed path in var/log/ogds-update.log, and
  make sure that file is rotated.
  [lgraf]

- Add `PathFinder` helper class to provide various Zope2 Instance
  related paths that are otherwise cumbersone to access.
  [lgraf]

- Make sure to always set OGDS sync logger to INFO level.
  Previously this was only guaranteed if product-config entry
  for the `ogds_log_file` was present in zope.conf.
  [lgraf]

- Drop unused opengever.ogds.base.sections.
  (Legacy transmogrifier-based OGDS synchronization).
  [lgraf]

- Update reference number of contained objects when referencenumber prefix changes.
  [phgross]

- Improve content and styling of the notification mail.
  [phgross]

- OGDSUpdater: Enforce uniqueness of user and group IDs on application side.
  [lgraf]

- Add internationalization support to the activity model.

  - Implement translatable activity columns with the help of SQLAlchemy i18n.
  - Added new attribute label to the Activity Model.
  - Correclty translate the tasktype in activity description.

  [phgross]

- Adjust document_date handling:

  - Update document_date to current date during checkin
  - Update document_date to version's creation_date when reverting to a version.

  [phgross]

- Make sure OGDS sync doesn't fail on user- or group IDs that are too long.
  Simply skip them and log a warning.
  [lgraf]

- Implement a versions tab for documents.
  (Superseeds the previously used history viewlet)
  [lgraf]

- Fixed path limitation of the catalog query in save_reference_number_prefix subscriber.
  [phgross]

- Fix invalid variable name in policy template.
  (Reference to setup.setup....)
  [lgraf]

- Improve the representation of the searchresults and the searchform.
  [phgross]

- Add debug helpers to assist in debugging plone.protect issues.
  [lgraf]

- Improve exception handling.
  Remove bare excepts and only catch Exception when possible. Also make sure to
  always re-raise ConflictError.
  [deiferni]

- Add support for extracting nested mails.
  Also refactor extraction of attachments from mails.
  [deiferni]

- Fix an issue with journal entries when deleting attachments from mails.
  [deiferni]

- Fixed ComponentLookupError in CancelDocument view, when mails are selected,
  show error statusmessage instead.
  [phgross]

- Show public_trial edit-form link also for documents inside tasks.
  [phgross]

- Set mail filename from title when creating/updating mails.
  The mail filename is now always set automatically as a normalized form of title.
  [deiferni]

- Set focus on first form field.
  [phgross]

- Add additional reference box in the dossier overview.
  [phgross]

- No longer overwrite mail metadata when it is already set.
  [deiferni]

- Fixed message type (warning) when resubmitting an already submitted document.
  [phgross]

- Optimize error handling of the NotificationCenter, show statusmessage
  instead of abort request.
  [phgross]

- Sort available templates alphabetically when creating a document from template.
  [deiferni]

- No longer link templates on the view that creates documents from templates.
  [deiferni]

- Use checkbox widget to select addable dossier types on a repository folder.
  [deiferni]

- Display a link to the containing subdossier on a dossier's document tab.
  [deiferni]

- Bump plone.formwidget.namedfile and remove corresponding monkeypatch in order
  to get changes from https://github.com/plone/plone.formwidget.namedfile/pull/9
  [lgraf]

- Add macro enabled office mimetypes to MTR.
  [lgraf]

- Update versions of opengever.core dependencies.
  [lgraf]

- TransitionControllers: Rebuild special handling for administrators,
  move agency check for administrators to each transition guard.
  [phgross]

- Add regression test for task type translations.
  [lgraf]

- Activity: Prevent generating duplicated activities when:

  - Reassigning tasks
  - Adding subtasks (Plone action-menu)
  - Delegating tasks (Workflow)
  - Modifying a deadline

  [deiferni]

- Migrate activity schema, use text for summary column.
  [deiferni]

- Prevent that tasks/forwardings can be accepted/assigned twice.
  This problem occurred with tasks/forwardings distributed over two (or more) admin-units.
  [deiferni]

- Allow deadline modification also for issuing_org_unit agency members.
  [phgross]

- Monkey patch http_server.compute_timezone_for_log in order to fix
  DST bug in timezone calculation for Z2 logs.
  [lgraf]

- No longer display emtpy tab 'additional' on forwarding add page.
  [deiferni]

- Fix MeetingListing: default sort_index, disalbe sorting for time columns.
  [phgross]

- Include collective.usernamelogger in core dependencies.
  [lgraf]

- Make task default deadline timedelta configurable per installation.
  [phgross]

- Remove unused copy-related-documents-to-inbox view.
  [deiferni]

- Task overview: Hide responsible info in subtask, maintask, successor and predecessor
  listing.
  [phgross]

- Update to Plone 4.3.2 and Dexterity 2.x.

  - Update imports for Plone 4.3.x compatibility.
  - Include dexterity extra requires (grok, relations).
  - Upate or rework views and javascript for Plone 4.3.x compatibility.
  - Fix CSRF protection exception for context annotations.
  - Replace test.cfg with 4.3 cfg.
  - Add plone.app.dexterity behavior IBasic to contactfolder.
  - Cleanup collective.js.jqueryui javascripts in registry, because upgradestep does not work correctly.
  - Cleanup no longer existing css files in css_registry.
  - Don't use grok-style template dir conventions for non grok templates.
  - Remove DexterityContent.__getattr__ monkey patch, this was a backport
    from Dexterity 2.x and has now been addressed with the upgrade to DX 2.
    (Includes regression test)

  [lgraf, phgross]


4.4.2 (2015-07-08)
------------------

- Fixed UnicodeEncodeError in state_label getter of tasks.
  [phgross]

- Fix Inbox Overview: Fix error while rendering overview. Also refactor
  boxes for inbox/dossier overview, introduce generic macro and mixin, remove inheritance.
  [deiferni]


4.4.1 (2015-06-09)
------------------

- CSRF: Allow _dav_writelocks to be initialized on context.
  [lgraf]

- Also assign navigation portlet to 'kontakte' in example content.
  Change navigation toplevel to 1. Also include hooks to setup navigation in policy template.
  [deiferni]

- Made reverting files to version link CSRF safe, adding the authentication token.
  [phgross]

- Only display the org-unit selector when multiple org-units are available.
  [deiferni]

- No longer use reserved names as column names. Also make sure this does not happen
  again in the future.
  [deiferni]

- Fix a typo in an opengever.activity models column name.
  [deiferni]

- Use short language codes "DE" and "FR" in language selector.
  [deiferni]

- Display a nested dossier-navigation on the dossier overview page. Display the navigation
  starting at the current dossier's root dossier. Don't display the navigation when no
  subdossiers are available.
  [deiferni]


4.4.0 (2015-06-01)
------------------

- SqlTableSource: Wrap `sort_on` with a ColumnClause when extending
  query with ordering in order to allow SQLAlchemy to properly
  quote column identifiers depending on the dialect (see #957).
  [lgraf]

- Meeting SchemaMigrations: Made some upgrades Oracle compatible.
  [phgross]

- Unify definition of of auto-incrementing SQL columns.
  Add explicit Sequence to enable of auto-increment for oracle. Also make
  server-side tables/sequences consistent with other model definitions for
  Postgres.
  [deiferni]

- Drop Owner from the workflows of the following content-types: document, contact, dossier,
  templatedossier, forwarding, inbox, mail, repository, repositoryroot, task.
  [deiferni]

- Fixed ResponseDescription when adding mails to a task.
  [phgross]

- Reworked object copy and paste functionality.

  - Made paste action CSRF safe.
  - Use default id format for copied objects.
  - Don't journalize automatically renamed objects during copy & paste process.
  - Replaced existing plone clipboard functionality with our own implementation.
  - Also prefix copied mails with "copy of" (same as documents).

  [phgross]

- Fixed activity timestamps(created) storing/using timezone aware datetime's.
  [phgross]

- Disable copy action in task listings.
  [phgross]

- Enable doc-properties for examplecontent and add example template file with doc-properties.
  [deiferni]

- Disable CSRF protection for remote requests.
  [phgross]

- Made dispatchers configurable per installation.
  [phgross]

- Migrate templatedossiers classes from Container to custom DossierContainer subclass.
  [deiferni]

- Restrict allowed dossier meeting content in ConstrainTypesDecider.
  [deiferni]

- Add initial policy template support and a simple SAAS policy template.
  [deiferni]

- Made featureflags (activity, meeting) more robust.
  [phgross]

- Fixed sql task synchronisation when task gets moved.
  [phgross]

- Redirect to documents tab instead of trash tab, after trashing documents.
  [phgross]

- Disallow deactivating a dossier which contains not closed tasks.
  [phgross]

- Implement scrollspy.
  [Kevin Bieri]

- Re-designed protocol view.
  [Kevin Bieri]

- Fixed wrongly displayed document_actions in task overview.
  [phgross]

- Fix upgrades for PostgreSQL/MySQL:

  - Fix opengever.policy.base upgrades, limit created tables to installed package.
  - Add idempotent MySQL implementations for creating/dropping indices and dropping tables.
  - Drop unnecessary/broken statements from migrations.
  - Drop a temporary table after the migration is finished.

  [deiferni]

- Fixed userdetails icons for group listings.
  [phgross]

- Also manage meeting permissions in dossier workflows.
  [deiferni]

- Re-designed meeting view.
  [Kevin Bieri]

- NotificationViewlet: Display message when no unread notifications exist.
  [phgross]

- Move MyNotifications listing to the PersonalOverview.
  [phgross]

- Notifications: added some missing translations.
  [phgross]

- Fix displaying agenda-item numbers. Make number optional and don't
  display it when no number is set (i.e. for paragraphs).
  [deiferni]

- Initalize annotations during object creation, to avoid CSRF messages on
  first object access.
  [phgross]

- Move empty template profiles from setup to examplecontent. Create reusable
  Municipality content profile with initial meeting content.
  [phgross, deiferni]

- Include ftw.footer and add content for the examplecontent profile.
  [phgross]

- Display submitted-to proposals (and document version) on document overview.
  Include a link that allows updating outdated documents.
  [deiferni]

- Add form to manually generate custom excerpts and store them in a dossier.
  [deiferni]

- Add markdown support to sablon files, update dependecies to most recent sablon release.
  [deiferni]

- Remove outdated gever styles (moved to plonetheme.teamraum).
  [Kevin Bieri]

- CSRF: Also allow writes to context portlet assignments.
  [lgraf]

- CSRF: Detect redirect loops on @@confirm-action view and
  break them if necessary.
  [lgraf]

- CSRF: Rollback transaction on @@confirm-action view to avoid
  creating redirect loops.
  [lgraf]

- Expanded/Collapsed triangle style for helptext-trigger.
  [Kevin Bieri]

- Add and update french and german translations.
  [phgross]

- Treeportlet: extend caching parameters with current language code.
  [phgross]

- Implement meeting closing:

  - Added automatic generation of excerpts for every scheduled proposal.
  - Copy back the excerpt to the original proposal.
  - Create Proposalhistory entry when decided.
  - Add excerpt box to the ProposalOverview.
  - Update proposal states during closing a meeting.
  - Show decision in ProposalOverview.
  - Made Proposal's Agendaitem backref a One-To-One relation.

  [phgross]

- Made MeetingTransition's CSRF safe.
  [phgross]

- Made documents and mails addable in proposals.
  [phgross]

- Activate statefilter also in subdossiers listings.
  [phgross]

- Fixed french translations
  [phgross]

- Add sablon-template tab on template dossiers.
  [deiferni]

- No longer show sablon templates in navigation.
  [deiferni]

- Fix downloading protocol-previews in safari.
  [deiferni]

- Fix downloading sablong templates in template dossier.
  [deiferni]

- Optimize member and membership view:

  - Added Membership listing to MemberView.
  - Added Edit functionality for Memberships.
  - Added Remove functionality for Memberships.
  - Order Memberships on date_from date by default.
  - Add memberhip_id column to membership table.

  [phgross]

- Extend meeting type views with corresponding watermark icon.
  [phgross]

- Extend meeting type links with corresponding icon.
  [phgross]

- Make sablon templates configurable on commitee-container. The following
  templates are available: Pre-protocol, protocol and excerpt.
  [deiferni]

- Made different SchemaMigration Upgradesteps more robust.
  [phgross]

- Customize CSRF confirmation page and add German translations.
  [lgraf]

- Added translations for the SearchBoxViewlet placeholder.
  [phgross]

- CSRF: always allow object annotations to be written.
  [jone, deiferni]

- Fix icons for the treeporlet favorite functionality.
  [phgross]

- Made DeactivatedFKConstraint compatible with newer alembic versions.
  [phgross]

- Fix submitting proposals that reference mails.
  [deiferni]

- Meeting: add editing protocols, creating/downloading/updating protocol documents.
  [deiferni]

- Examplecontent profile: Add french to the supported language.
  [phgross]

- Customize LanguageSelector viewlet to display it as a menu.
  [phgross]

- Fixed actor for all task activities.
  [phgross]

- Add initial notification support:

  - Added NotificationCenter including SQL representations for activitities, notifications, resource and watchers.
  - Added a feature flag to disable/enable notifications
  - Added notification viewlet which contains a badge icon and lists unread notifications
  - Added notifications overview with a MyNotification tab
  - Add mail notification dispatcher.

  [phgross]

- Implement migrating participants in DossierMigrator.
  [lgraf]

- Add DictstorageMigrator that migrates user IDs in dictstorage keys (in SQL).
  (to be used with ftw.usermigration).
  [lgraf]

- Add OGDSMigrator that migrates users and inbox groups in OGDS SQL tables
  (to be used with ftw.usermigration).
  [lgraf]

- Do not show resolved tasks as overdue.
  [phgross]

- Add DossierMigrator that migrates dossier responsibles (to be used
  with ftw.usermigration).
  [lgraf]

- Meeting: disable navigation portlet for commitee-container when installing
  example profile.
  [deiferni]

- Meeting: only allow documents in dossiers to be submitted as additional documents.
  [deiferni]

- Meeting: add missing translations for meeting/membership add menu.
  [deiferni]

- Meeting: add missing translations for submitting additional documents.
  [deiferni]

- Meeting: don't allow overlapping committee-memberships.
  [deiferni]

- Meeting: allow editing initial position in pre-protocol.
  [deiferni]

- Meeting: integrate sablon document template processor for Word:
    - Integrate subprocess calls to sablon
    - Add pre-protocol download
    - Add pre-protocol document generation in dossiers
    - Add pre-protocol document updates for documents in dossiers

  [deiferni]

- Refactor document creation: reduce code duplication by extracting class
  to create documents and set default values properly.
  [deiferni]

- Meeting: add legal basis field to proposals, submitted proposals and
  pre-protocols.
  [deiferni]

- Refactor: add command to create documents. Use this command for
  quickupload-adapter, when creating-documents from template and when extracting
  documents from emails.
  [deiferni]

- Drop all SQL-tables during dev-setup, not only those defined in metadata.
  [deiferni]


4.3.0 (2015-03-20)
------------------

- Automatic CSRF protection with plone.protect 3.
  [jone]


4.2.1 (2015-03-17)
------------------

- SchemaMigration: Use IdempotentOperations only when executing migrations for MySQL.
  Also make sure that IdempotentOperations always keeps database metadata up to date.
  [deiferni]

- Upgrade: fix meeting upgrade to 4200, also migrate data, not only schema.
  [deiferni]

- Upgrade: add oracle/postgres implementation for upgrade to 4203.
  [deiferni]

- Upgrade: fix meeting upgrade to 4214, use sqlalchemy expression api as table definition
  instead of metadata.
  [deiferni]

- Upgrade: fix meeting upgrate to 4208, correctly create unique constraints.

- Fix an issue with event handlers while deleting a plone-site.
  [deiferni]

- Update translation for forwarding-transition-reassign transition.
  [phgross]

- Disable Remove GEVER content for inactive or resolved dossiers.
  [phgross]

- SchemaMigration: Make sure transaction is marked as changed even if it
  only contains DDL statements. See zope/sqlalchemy/README.txt#L145-L164
  [lgraf]

- SchemaMigration: Fix tracking table creation for DBs supporting transactional DDL:

  If the tracking table is created for the first time, it's not visible in
  metadata until the transaction has been committed.

  Therefore we need to have a method that tries to fetch an existing tracking
  table and return it, or if it doesn't exist yet, creates it and then
  returns the created table. In order to keep a reference to the tracking table
  across several SchemaMigration upgrade steps, a module global is used.

  Returning the table created by op.create_table requires alembic >= 0.7.0.
  [lgraf]

- Rename UniqueConstraints names of the SubmittedDocument table,
  because of oracle's limitation to 30 chars.
  [phgross]

- Drop three date/time fields in favour of two datetime fields.
  [deiferni, phgross]


4.2.0 (2015-03-12)
------------------

- Fixed date_of_completion display in task overview.
  [phgross]

- Use checkbox widget to select participations roles.
  This fixes an issue with ie10 and ie11 where no selection could be made.
  [deiferni]

- Keep predecessor's issuing_org_unit for successor tasks.
  [phgross]

- Replaced committees listing tab with a committes overview listing.
  [phgross]

- Switch to PostgreSQL for local development.
  [lgraf]

- Only assign 'Remove GEVER content' permission to manager by default.
  [lgraf]

- Protect 'remove_confirmation' view with 'Remove GEVER content' permission.
  [lgraf]

- Rewrite Redirector adapter to use cookies instead of sessions.
  Accessing sessions causes the transaction to be a write.
  [jone]

- Added committee overview tab.
  [phgross]

- Fixed `only_active` membership query.
  [phgross]

- Style protocol view in opengever.meeting.
  Implement sticky headings and autosize textareas.
  [Kevin Bieri]

- Meeting listing improvements:
    - Disable selection links for listings without checkbox column.
    - Extend proposal listing columns.
    - Fixed sorting and filtering for proposal and submittedproposal listings.
    - Fixed sorting and filtering for comitteecontainer tabs.
    - Fixed sorting and filtering for committee tabs.

- Task workflow: Make workflow also manage add permissions for mails,
  the same way it does for documents. In particular, this avoids mails
  being addable in tasks in state 'tested-and-closed'.
  [lgraf]

- Livesearch: Dropped unused icon <img> tag.
  [phgross]

- Style meeting form.
  Add agendaitem sorting implementation.
  [deiferni, Kevin Bieri]

- Wrap checks in is_pasting_allowed in a try..except for safety.
  [lgraf]

- Make sure response descriptions are always unicode.
  [lgraf]

- Add ftw.testbrowser widget for our customized AutocompleteWidget.
  [lgraf]

- Only show "Paste" action if objects in clipboard are in allowed addable
  types of target container.
  [lgraf]

- XlsSource: Handle values that are already a valid term for vocabulary fields.
  [lgraf]

- XlsSource: Raise KeyError if a value can't be found in the translation mapping
  for fields with a vocabulary, instead of just setting the translated value anyway.
  [lgraf]

- XlsSource: Add some more alternate spellings for archival_value mapping.
  [lgraf]

- Move items: handle twice submitted forms or invalid selected paths.
  [phgross]

- Fix and rework dossier deactivation and activation.
  [phgross]

- Add initial meeting support.
    - Add Proposal content type (proxies) and model.
    - Add feature flag, disable meeting feature by default.
    - Add Committee content type (proxy) and model.
    - Add custom forms to create/edit proxy-supported entities.
    - Add custom workflow implementation (no plone workflow).
    - Add a context manager to temporarily change the security context.
    - Add meeting model and forms.
    - Add schedule meeting action to committee.
    - Add scheduling of proposals as agenda items.
    - Add better committee page displaying meetings and submitted proposals.
    - Add custom content-views viewlet to display correct edit links for models.
    - Add custom pathbar viewlet which can display sql-models.
    - Add paragraph and custom text agenda items.
    - Make agenda items deletable.
    - Add a form to create a pre-protocols for meetings.
    - Disable edit-bar for model add-forms.
    - Add forms for Members and their Memberships in Committees.
    - Add tab to committees listing all memberships.
    - Add cancel buttons and form labels.
    - Add tabs to committee container for committees and members.
    - Allow submission of additional documents to already submitted proposals.
    - Log proposal history and display changes on the proposal overview.

  [deiferni]

- Dossier workflow: Also allow Administrator role to activate deactivated
  dossiers.
  [lgraf]

- OrgUnitSelector: Fix fallback logic:

  Build intersection of current admin units' org units and
  user's org units. If some of the user's org units are in the
  current admin unit, use the first of those as the fallback.

  Otherwise we're in an inter-admin unit operation, default to
  current admin unit's first org unit.
  [lgraf]

- CookieStorage: Extend max age of cookies to 30 days (was
  "end of browser session" before).
  [lgraf]

- OrgUnitSelector: Store selected OrgUnit after determining fallback.
  [lgraf]

- Rewrite advancedsearch to fix an issue with invalid requests to the search view.
  It is now allowed to filter by min or max value instead of just by date ranges
  (min and max) when querying for dates.
  [deiferni]

- Fix an issue with username/contacts-name based sorting in tabbedviews.
  [deiferni]

- Update german translations for opengever.meeting.
  [phabegger]


4.1.0 (2014-12-18)
------------------

- Made the AddPublicTrialColumn more robust.
  [phgross]

- Dropped no longer used document state journalization.
  [phgross]

- Disable docproperty updating in YearfolderStorer process.
  [phgross]

- Improved repository deletion (it's now possible without folder_contents view):
    - Revoke list folder contents permission on repository.
    - Add repository delete action and confirmation view.
    - Adjust global role mapping for delete objects permission.
    - Adjust delete objects permission for repositories.
    - Revoke delete objects permission for dossiers.
    - Added monkeypatch for _verifyObjectPaste to allow moving content without
      delete objects permission.

  [phgross]

- Implements content removal functionality for documentish objects:
    - Add new permission `Remove GEVER content`.
    - Added new document workflow state `document-state-removed`.
    - Added new mail workflow state `mail-state-removed`.
    - Add new action `Remove` to trash tab and add remove confirmation view.
    - Added journalization for document removing and restoring.

  [phgross]

- Rewrite gever setup.
    - Introduce two zcml directives to configure deployments and ldap profiles.
    - Simplify deloyment form, remove multi-client configuration options.
    - Update branding, add onegovgever logo.
    - Add custom setuphandlers for local roles, initial repository and document templates.
    - Configure development options and add environment variable to enable them easily.

  [deiferni]

- Disable nested inboxes.
  [deiferni]


4.0.6 (2014-12-09)
------------------

- Implement pessimistic connection invalidation (MySQL only):
  Check every connection that has been checked out from pool, and
  invalidate it if it's stale.
  [lgraf]

- Reworked OrgUnit Selector:
    - Store current unit to regular cookie instead of using the session_data_manager.
    - Differentiate between users_units (selectable) and admin_unit's org_unit
      (current org_unit).
    - Change current org_unit functionality, the current orgunit has to be
      part of the current admin_unit.

  [phgross]

- Made schemamigrations to 4.0.x release oracle compatible.
  [phgross]

- Fixed transporting task with the OGDS Transporter beetwen different admin_units.
  [phgross]


4.0.5 (2014-11-25)
------------------

- Extract attachments view: Fixed contenttype helper when lookup via filename.
  [phgross]


4.0.4 (2014-11-13)
------------------

- Extract attachments view: fixed icon display in attachment listing.
  [phgross]

- Disable paste action for mails.
  [phgross]

- Set proper Content-Type header in responses from LDAP control panel views.
  [lgraf]

- Fix Unicode handling in OGDSUpdater.
  [lgraf]

4.0.3 (2014-11-10)
------------------

- Dossier responsible field: use current admin unit's user, instead of only
  current orgunit's one.
  [phgross]

- Forwarding Transitioncontroller: Fixed assign_to_dossier check.
  [phgross]

- Add new type Inbox Container.
  [phgross]

- Task byline: Use adminUnit abbreviation instead of label for sequence_number display.
  [phgross]


4.0.2 (2014-11-03)
------------------

- Fixed version download, when download confirmation is deactivated.
  [phgross]

- Fixed UnicodeEncodeError in task link generation.
  [phgross]


4.0.1 (2014-10-27)
------------------

- Harmonize column lengths of groupid and userid columns.
  [phgross]


4.0.0 (2014-10-26)
------------------

- Changes to OGDS [phgross, deiferni]:

  - Replace `ContactInformation` utility with a service implemetation, available as `ogds_service`.
  - Update to latest `opengever.ogds.models` version.

  - Fixed encoding issues in the `EmailContactsAndUsersVocabularyFactory`.


- Replace Clients with OrgUnit/AdminUnit [phgross, deiferni]:

  - Remove one-to-one relationships of `PloneSite` and `Client` by introducting `AdminUnit` and `OrgUnit`.
  - An `AdminUnit` corresponds to one `PloneSite`.
  - An `AdminUnit` has a one-to-many relationship to `OrgUnit`.
  - Add utility functions to access the current `OrgUnit` and `AdminUnit`.
  - Add org-unit selector to switch between the user`s assigned org-units.
  - The oguid now consists of admin-unit-id and IntId.
  - Admin_unit intern `remote_requests` uses now unrestricted traversing.
  - Above changes concern the following functionality:

    - Sharing View
    - OGDS-Vocabularies
    - Default of task `responsible_client`
    - Cross plone-site request authentication
    - Cross plone-site wizards
    - PloneSite referencenumberpart is the admin_unit's abbreviation.


- Setup [phgross, deiferni]:

  - Make sure that inflator content-creation runs after gever setup.
  - Test that we correctly override ftw.inflator setuphandler configuration.
  - Create admin units and org units from generic setup profile.


- Inbox/Forwarding [phgross, deiferni]:

  - Use globalindex as data-source for task-listings (Overview, AssignedTasks, IssuedTasks).
  - Fix forwarding immediate view, use `issued_inbox_tasks` tab.
  - Assign forwarding to dossier: reset issuer to current inbox.
  - Accept task, edit in new dossier: Set default dossier title only for tasks but not for forwardings.
  - Inbox now ontains multiple Inboxes, one for each `OrgUnit`:

    - Allow nested inboxes.
    - Map inboxes and Orgunits with `ResponsibleOrgUnit` behavior.
    - Add redirecting to current subinbox.
    - Allow multiple yearfolders per inbox, one for each `OrgUnit`.

  - Disable statefilter for yearfolder's `ClosedForwardings` listing.
  - Rework `InboxTransitionController` guards.


- Tasks [phgross, deiferni]:

  - Refactor syncing tasks from plone to globalindex.
  - Use globalindex as data-source for task-listings (PersonalOverview).
  - Globalindex:

    - Introduce a specific query class for `Task`.
    - Make some task fields required.
    - Add containing_subdossier column.
    - Migrate data for issuing_org_unit.
    - Use integer sequence numbers.

  - Refactored display of task responses:

    - Include response descriptions.
    - Add permission-check for edit and delete actions.
    - Add response entry for task creation.

  - Add action menu viewlet:

    - Display transitions as buttons.
    - Display agency actions in a separate dropdown.

  - Drop old no longer used CopyDocumentsToRemoteClient functionality.
  - Enable Drag'n'drop upload for tasks.
  - Rework Task-Transition controller guards.
  - Replace modify-deadline and delegate actions with a task transition.
  - Display icon on task overview when task is overdue.
  - Add task-type to searchable text.
  - Improve Task-Form styling and Usability
  - Add specific icon and watermark-icons for subtasks.


- Actor [phgross, deiferni]:

  - Add Actor to handle entities collaborating with tasks.
  - Actors can be one of the following:

    - User (OGDS or Plone)
    - Inbox
    - Contact
    - NullActor


- Test Refactoring [phgross, deiferni]:

  - Replace some mock-tests with functional tests.
  - Add sql-builders.
  - Add meta-builder for test-fixtures.
  - Setup default fixture for all functional tests.


- Migration [phgross, deiferni]:

  - Add `SchemaMigration` base class for sql-database migrations.
  - Add db-migration for recent changes to `opengever.ogds.models`.
  - Add db-migration for changes to `opengever.globalindex`.


- OGDS synchronization [lgraf]:

  - LDAP util: When querying for schema, deal with servers that don't support
    listing all operational attributes (RFC 3673).
  - OGDS sync: Unify OGDS synchronization so there's a single function
    that does the sync and that can be called from anywhere.
  - OGDS sync: Add a `bin/instance sync_ogds` zopectl command that
    can be used from a cron job.

- Additional Improvements:

  - Simplify LaTex listing adapters and include base-class.
    [phgross, deiferni]

  - Remove `ClientId` viewlet.
    [phgross, deiferni]

  - Remove `GlobalindexMaintenanceView` and `OpengeverView`.
    [phgross, deiferni]

  - Improve responsive design.
    [phgross, deiferni]

  - Display user-name in personal overview title.
    [phgross, deiferni]

  - Use correct content-type when returning 'OK' responses.
    [phgross, deiferni]

  - Sort groupmembers by label for groupmembers list.
    [phgross, deiferni]

  - Add contact-service for local contacts.
    [phgross, deiferni]

  - Refactor tree portlet.

      - Performance improvements.
      - Use JavaScript tree API for building the tree.
      - Add repository favorites.
      - Add expand store for favorites.

    [jone, phgross]

  - Update DocProperties when documents are moved/pasted and checked-in/checked out.
    Create a journal entry when modifying/initializing DocProperties.
    [deiferni]

  - Display a warning message in the download confirmation overlay when no file is available.
    [deiferni]

  - Fix an issue with z3c.form inline validation.
    [deiferni]

  - Reactivate statefilter for Dossiers.
    [phgross]

  - Added option to checkin documents without comment.
    [lknoepfel, deiferni]

  - Fix missing file in initial template versions.
    [deiferni]

  - Also display `pdf-tasks-listing` and `task-report` actions for inbox task-listings.
    [deiferni]

  - Fix an issue with autocompleting assignee/issuer while creating forwardings.
    [deiferni]

  - List all users in advanced-search when searching for dossiers.
    [deiferni]

  - Added option to disable download confirmation.
    [lknoepfel]

  - Add separate profile with the gever specific mimetypes.
    This fixes the mimetype icons bug.
    [phgross]

  - Fix an issue while deactivating dossiers with already closed subdossiers.
    [deiferni]

  - Fix issue when uploading files with firefox over the Document AddForm.
    Added temporary monkeypatch to ignore mimetypes sent by the browser.
    [phgross]

  - Fix an unicode issue while syncing document filename and title.
    [deiferni]

  - Fix an issue with filtering for dossier-participants.
    [deiferni]

  - Made checkbox column not sortable, to avoid CatalogError's.
    [phgross]

  - Fixed move items functionality for moving tasks.
    [phgross]

  - Security fixes: avoid injecting javascript (XSS) using safe_html transforms.
    [phgross]


3.4.2 (2014-11-25)
------------------

- Dropped prevent_deletion handler.
  [phgross]

- Fixed mail download for mails with already CRLF.
  [phgross]

- Mail Download: Convert LF to CRLF, to avoid displaing problems in MS Outlook.
  [phgross]

- Set content-type correctly for ok_response in inter-client functionalities.
  [deiferni]

- Make reference_prefix_manager deal properly with already deleted objects.
  [phgross]

- Use `ftw.profilehook` instead of setuphandlers.
  [deiferni]


3.4.1 (2014-09-03)
------------------

- Monkey patch ftw.mail.inbound.createMailInContainer because
  `preserved_as_paper` has a schema level default, its default
  value doesn't get set correctly, so we set explicitely after setting
  the defaults.
  [lgraf]

- Mail preview tab: fixed bug in mimetype lookup for attachments with
  a wrong mimetype.
  [phgross]


3.4.0 (2014-08-28)
------------------

- General fixes:

  - Fixed translation for filing_number column in dossier listings.
    [phgross]
  - Also check for not supplied mails, when check if dossier could be resolved.
    [phgross]
  - Fixed unicode decode bug in task overview.
    [lknoepfel]
  - OGQuickUploadCapableFileFactory: Set default values before adding content to container.
    (Prevents values set by handlers on ObjectAddedEvent to be overwritten again).
    [lgraf]
  - Fix issue with `prevent_deletion` subscriber not being able to acquire membership_tool
    because of broken acquisition during Plone site deletion.
    [lgraf]
  - Customize plone.dexterity default view for all dexterity content in
    order to be able to omit specific fields, and remove previous customizations.
    [lgraf]


- Changes to document metadata:

  - Document metadata: Refactor behaviors to be a package with separate modules.
    [lgraf]
  - Monkey patch DexterityContent.__getattr__.
    This is required to support dynamic lookup of schema-level default values for
    fields in behaviors. It basically is a backport of this Dexterity 2.x fix:
    https://github.com/plone/plone.dexterity/commit/dd491480b869bbe21ee50ef413c263705af7b170
    [lgraf]
  - Refactored document overview.
    [lgraf]
  - Implement document metadata behavior for mail (incl. upgrade step and init event).
    [mathias.leimgruber]
  - Show classification infos on document overview tab.
    [mathias.leimgruber]
  - Customized document default view in order to render `file`
    field in NO_DOWNLOAD_DISPLAY_MODE.
    [lgraf]
  - Changed German wording for value `unchecked` for both public_trial and archival_value:
    "Noch nicht geprüft" -> "Nicht geprüft"
    [lgraf]
  - Change german wording for descriptions of `public_trial` and `public_trial_statement`
    [lgraf]
  - Added `regulations` and `directive` options to `document_type` vocabulary.
    [lgraf]


- Changes to journaling:

  - Fix double journal entries using quickupload.
    [mathias.leimgruber]
  - Journalize any changes to `public_trial` field.
    [lgraf]
  - Journal: Listen on IBaseDocument instead of IDocumentSchema - mails are now also
    considered documentish and should be treated equally.
    [lgraf]
  - Journalize AttachmentsDeleted event.
    [lgraf]
  - Create initial journal entry for mails.
    [lgraf]


- Changes related to mail content type:

  - Implement tabbedview for ftw.mail.mail content (Preview / Journal / Info).
    [mathias.leimgruber]
  - Use IDocumentNameFromTitle behavior from document also for mail.
    [mathias.leimgruber]
  - Use document byline also on mail.
    [mathias.leimgruber]
  - Add classification behavior to mail.
    [mathias.leimgruber]
  - Add overview tab for mail (shows some basic metadata).
    [mathias.leimgruber]
  - File a copy of the mail in the dossier by default when sending documents from GEVER.
    [lgraf]
  - Hide duplicate mail title in mail preview tab.
    [lgraf]
  - Add plone.app.lockingbehavior to ftw.mail.mail FTI.
    [lgraf]
  - Add 'Edit Metadata' action to ftw.mail.mail FTI.
    [lgraf]
  - Override ftw.mail default view with our customized dexterity default view.
    [lgraf]
  - Make FileOrPaperValidator consider mails properly (always digitally available).
    [lgraf]
  - Disable the editable border for the extract attachments view.
    [lgraf]
  - Improved wording of German translations in extract attachments view.
    [lgraf]
  - Added new mail event `AttachmentsDeleted`.
    [lgraf]
  - Mail overview: display the original message including a download link.
    [phgross]
  - Reword status message after sending documents by e-mail.
    [lgraf]
  - Use the same customized download view we use for documents for mails as well.
    [lgraf]
  - Don't encode attached mails when sending documents as email.
    [lgraf]
  - Always set `digitally_available` to `True` upon mail creation.
    [lgraf]

- Changes related to public_trial field:

  - Added limited-public option for public_trial field.
    [lknoepfel]
  - Vocabulary for public_trial is no longer a restricted vocab. It behaves like a regular one.
    [mathias.leimgruber]
  - Added public_trial index and metadata field.
    [lknoepfel]
  - Added public_trial column to document tab.
    [lknoepfel, phgross]
  - Allow public trial state to also be modified in closed dossier states.
    [mathias.leimgruber]
  - Add an IClassificationSettings registry record with `public_trial_default_value`.
    [lgraf]
  - Make default value adapter for `public_trial` use the configurable default
    value from IClassificationSettings registry record.
  - Reword German translations for public_trial_statement label and description.
    [lgraf]
  - Don't show public trial edit form for template dossiers.
    [lgraf]
  - Remove `public_trial` field from repository byline.
    [lgraf]
  - Omit `public_trial` and `public_trial_statement` fields from dossier and
    repository folder default views.
    [lgraf]
  - Disable public_trial edit_form when parents dossier is inactive.
    [phgross]
  - Added public_trial_statement field to the public_trial edit form.
    [phgross]


3.3.2 (2014-08-08)
------------------

- Fixed seralization error in responsetransporter, when changes containing date's.
  [phgross]


3.3.1 (2014-07-28)
------------------

- Made logout overlay easier to customize.
  [phgross]

- AdvancedSearch: Fixed bug which renders the wrong widget for first request.
  [phgross]

- Search type filter: limit types to main types.
  [phgross]

- Overwrite searchbox viewlet and javascript.
  So there is always a advanced search link.
  [Julian Infanger]

- Breadcrumb: Replace Home label with curent client label.
  [phgross]

- Disable edit-bar for the advancedsearch form.
  [phgross]

- Dropped no longer used attach remote document action.
  [phgross]

- Moved time column in journal tab to the far left.
  [lknoepfel]

- Fixed bug where quickupload didn't remove the active class.
  [lknoepfel]

- Renamed german version of move-items-button.
  [lknoepfel]

- Initialized opengever.sharing version. Moved prepoverlay initialization to opengever.base.
  [lknopfel]

- Added download copy in tooltip.
  [lknoepfel]

- Display document mimetype icons in ContentTreeWidget.
  [phgross]

- Use existing styles for table in tasktemplate view.
  [Julian Infanger]

- Changed default placeholder for searchbox.
  [Julian Infanger]

- Removed unused yearfolder workflow.
  [lknoepfel]

- Fixed table display in add-tasktemplate form.
  [phgross]

- Fixed widget definition for date fields in tasks edit form.
  [phgross]

- Added viewlet to colorize special pages as dev, test, ...
  [Julian Infanger]

- Fixed outdated profile versions for og.base:default and og.examplecontent:default.
  [lgraf]

- Added repository.csv to xlsx script.
  [lknoepfel]

- Changed format of examplecontent excel to xlsx.
  [lknoepfel]

- Dossierdetails: Fixed label for the Dossier end.
  [phgross]

- Added reviewer role on admin groups.
  This role ensures that admins can see the menu bar.
  [lknoepfel]

- Inbox: Removed icon from byline.
  [Julian Infanger]

- Refactored some hard to change test data.
  [lgraf]

- PDF Listings: Made repository_title getter reference formatter independent.
  [phgross]


3.3 (2014-06-05)
----------------

- Added initial implementation for setting DocProperties when creating
  a document from template.
  [lgraf]

- Fixed zipexport-enable upgrade step to match the new registry entry.
  With ftw.zipexport 1.2.0 the registry name changes which brakes our upgrade step.
  [lknoepfel]

- Added responsible org field on repositoryfolder.
  [lknoepfel]

- Treeportlet: Enable scrolling in the portlet and scroll down to selected item.
  [Julian Infanger]

- Changed source for repository import: from csv to xls.
  [lknoepfel]

- Byline: Removed icon from byline.
  [Julian Infanger]

- Fixed interface in dossiers ConstrainTypeDecider.
  [phgross]

- Updated ftw.zipexport registry entry to multi-value field.
  [lknoepfel]

- Added handling for missing document_type in document view.
  This field is hidden on a customer installation.
  [lknoepfel]

- Dossierdetails PDF: Fixed doubled encoded repository_path.
  [phgross]

- Dossierdetails PDF: Fixed UnicodeEncodeError in responsible getter.
  [phgross]

- Passing search string from live search to advanced search.
  Using SearchableText from the url as default value in advanced search.
  [lknoepfel]

- Styled document from template form.
  [lknoepfel]

- Setup: Activate navigation portlet on the templatedossier.
  [phgross]

- Allow nested Templatedossiers.
  [phgross]

- Limit query depth in templatedossier listings(documents, trash).
  [phgross]

- Treeportlet: Implement deferred tree rendering.
  [phgross]

- Fixed German translation in logout overlay.
  [pha]

3.2.4 (2014-05-26)
------------------

- Added missing french (and german) translations.
  Fixed i18n domain and translated vdex.
  [lknoepfel]

- Mail view: use sprite icons in the attachments list.
  [phgross]

- Implemented cache invalidation for TreeView portlet cache.
  [lgraf]

- Update og.mail tests according to changes in ftw.mail.
  (See https://github.com/4teamwork/ftw.mail/pull/17)

- Fixed typo in test_overview.py.
  [lknoepfel]

- Moved create repository script from opengever.zug package.
  [lknoepfel]

- Replaced ext-js function 'remove' with pure js version in advancedsearch.
  [lknoepfel]

- Fixed backref name of the groups_user join table.
  [phgross]

- Task overview: Hide client prefix in issuer value for a one client setup.
  [phgross]


3.2.3 (2014-04-01)
------------------

- Hide standard ftw.mail mail-in viewlet (we display the mail address in
  the byline).
  [lgraf]

- Removed og.mail IMailSettings registry interface (now done in ftw.mail).
  Added upgrade step to migrate settings to ftw.mail's IMailSettings and
  remove old og.mail IMailSettings.
  [lgraf]

- Provide an IntIdResolver adpater to generate Dossier Mail-In addresses
  based on IntIds, and use it instead of the old implementation.
  [lgraf]

- Removed IMailInAddress behavior. Not needed any more with ftw.mail 2.0.
  [lgraf]

- Replaced hardcoded workflow names with constants.
  [lknoepfel]

- Updated move destination widget to hide closed dossiers.
  [lknoepfel]

- Added french translation by I. Anthenien.
  [lknoepfel]

- ldap_util: Make check for user object classes case-insensitive.
  [lgraf]

- Added french translation by I. Anthenien.
  [lknoepfel]


3.2.2 (2014-03-11)
------------------

- Don't hard code reference formatter in tabbed view custom sorter. Look it up
  from IReferenceNumberSettings instead.
  [lgraf]

- Fixed missing role and available expression in reference prefix manager.
  [lknoepfel]

- Added NoClientIdDotted reference number formatter.
  [lknoepfel]

- Personal Overview: Raise Unauthorized for unauthenticated users instead of
  hardcoded redirect to login form.
  This is required for Single-Sign-On with SPNEGO plugin to work.
  [lgraf]

- Use always logged in user as responsible of a subdossier.
  [lknoepfel]

- Remove obsolete dependency on transmogrify.sqlinserter.
  [lgraf]


3.2.1 (2014-01-23)
------------------

- Implement custom sort functions for both 'dotted' and 'grouped_by_three'
  reference formatters.
  [lgraf]

- Add requirement for a custom sort function to IReferenceFormatter interface
  [lgraf]

- Remove 4teamwork-ldap/ldap_plugin.xml from .gitignore and check it in
  (with placeholder credentials).
  [lgraf]

- Configure LDAP credentials from JSON file.
  [lgraf]

- Fix raising of exceptions and logging in msg2mime transform.
  [lgraf]

3.2 (2013-12-15)
----------------

- Increase task_principals.principal column length to 255.
  [lgraf]

- Logout overlay: use absolute url to redirect to the logout view.
  [phgross]

- Add destructive class to logout button in logout overlay.
  [Julian Infanger]

- Add specific byline for the PloneSite(Personal overview).
  [phgross]

- Adjusted seperator of the `grouped_by_three` formatter.
  [phgross]

- Corrected message after resolving a subdossier.
  [phgross]

- Override livesearch_reply.py to provide correct advanced search link.
  [lgraf]

- Hide paste action for template dossier and contact folder.
  [lgraf]

- Activate selction controlls for the `my documents` Tab.
  [phgross]

- Advancedsearch: Dropped reference number solution.
  [phgross]

- OGDS Listing: Display empty string for users without a name or firstname.
  [phgross]

- OGDS updater: Make check for AD user IDs more robust.
  [lgraf]

- DefaultDocumentIndexer: Store transform cache on context.file._blob, not context.file.
  (NamedFileInstances are not recreated when updating file contents)
  [lgraf]

- LDAP util: Make sure we still deal with multivaluedness for non-user
  objects (fix for bug introduced in 1daa9ba).
  [lgraf]

- LDAP import: Deal with Active Directory nested groups.
  [lgraf]

- OGDS updater: Consider all possible member attribute names when getting members from a group.
  [lgraf]

- LDAP util: Consider all possible objectClasses when searching for groups.
  [lgraf]

- LDAP util: Only apply schema mapping to user objects.
  [lgraf]

- DefaultDocumentIndexer: Catch any exceptions raised by transforms and log them.
  [lgraf]

- OGDS updater: Deactivate is_ldap_reachable check. It's unnecessary and broken.
  [lgraf]

- Modify indexer for documents so that it queries for our own IDocumentIndexer adapter,
  allowing us to choose to index original documents or their preview PDF, depdending on
  opengever.pdfconverter being installed or not.
  [lgraf]

- OGDS updater: fullname field is already single-valued, don't try to treat it like a list.
  [lgraf]

- Moved docucomposer in own package.
  [lknoepfel]

- LDAP util: Only use PagedResults controls if the server advertises to support them.
  [lgraf]

- LDAP util: When checking if attributes are multivalued, store results in a cache.
  This prevents us from hitting the schema more often than necessary, and, as a side
  effect, causes warnings about attributes not declared in schemata to be printed
  only once.
  [lgraf]

- LDAP util: Added method to list all objectClasses defined in schema.
  [lgraf]

- LDAP import: groupid may be in 'cn' or 'fullname' attribute.
  Handle both cases gracefully.
  [lgraf]

- Updated i18n-build with the option to build only one subpackage.
  [lknoepfel]

- Fixed unicode encoding bug in search for autocomplete of ContactsVocabulary.
  [lknoepfel]

- Disabled illogical actions in template dossier.
  [lknoepfel]

- Restricted reference prefix manager to repository and repositoryroot.
  [lknoepfel]


3.1.4 (2014-02-18)
------------------

- Removed DocuComposer actions from opengever.dossier:default profile.
  [lgraf]


3.1.3 (2014-02-06)
------------------

- Remove remaining traces of `related_items` index.
  Backport of 9d1064d.
  [lgraf]

- Dossier resolving: Fixed `its_all_closed` check, for nested subtasks.
  [phgross]

- Document tooltip helper: Fixed link for the icon.
  [phgross]

- Fixed load order issue when setting tagged values to omit the changeNote
  field from the IVersionable behavior.
  Backport of d8438c8.
  [lgraf]

- OGDS Updater: Gracefully skip users outside users_base referenced in groups.
  Backport of 2d862bd.
  [lgraf]

- Removed related_items index and RelatedTasks tab.
  [lknoepfel]


3.1.2 (2013-12-02)
------------------

- Issued inbox task: fixed listing query, to search the complete client.
  [phgross]

- Inbox overview: List only active tasks and forwardings.
  [phgross]

- Inbox overview: Only list current part of a predecessor/successor couple.
  [phgross]


3.1.1 (2013-10-23)
------------------

- Fixed CleanupReferencePrefixMapping upgradestep
  (works now for reference to no longer existing objects):
  [phgross]


3.1 (2013-10-23)
----------------

- Update reference prefix manager to the new version of adapters.
  [lknoepfel]

- Fixed client setup: use system user instead of hardcoded username.
  [lknoepfel]

- Fixed redirect when creating a subtask.
  [phgross]

- Integrate ftw.zipexport.
  [lknoepfel]

- Reworked forwarding refuse and reassign functionality.
  [phgross]

- Reworked inbox tabs.
  [phgross]

- Activate reporting actions (dossier and tasks) for every user.
  [phgross]

- Dossiercover: Implements breadcrumb cropping and adjust fonz size.
  [phgross]

- Dropped inbox_group agency for tasks in a oneclient setup.
  [phgross]

- Task workflow: Documents inside a task, aren't editable when the dossier is closed.
  [phgross]

- Reworked document_author resolution and displaying value in listings.
  [phgross]

- Fixed permissions problems when copying dossiers.
  [lgraf]

- LDAP import: Use the respective property from LDAPUserFolder to determine which is the
  UID attribute.
  [lgraf]

- LDAP util: Make determining multi-valuedness of attributes more robust
  in case of broken LDAP schemas.
  [lgraf]

- LDAP util: Get user object classes from LDAPUserFolder instead of hardcoding them.
  [lgraf]

- Added modify deadline form and functionality.
  [phgross]

- Removed client prefixes in single client setups.
  [lknoepfel]

- Use ftw.builder instead of our own builder implementation.
  [phgross]


3.0.1 (2013-10-21)
------------------

- LDAP import: If server doesn't support page controls, fall back to issuing
  search request without them.
  [lgraf]


3.0 (2013-08-14)
----------------

- Make exposator work for both izug.basetheme and plonetheme.teamraum.
  [Julian Infanger]

- Fixed imports in the processInputs monkeypatch.
  [phgross]

- Dossier overview: only list active subdossiers.
  [phgross]

- Rewrote LDAP synchronisation in pure Python instead of Transmogrifier.
  [lgraf]

- Removed development LDAP configuration for now.
  [lgraf]

- Fix import of HAVE_BLOBS from plone.namedfile.
  [lgraf]

- Repository Setup: Moved config and blueprints from zugpolicy.base in to core.
  [phgross]

- Dossier: Fixed start- and end-date validation in edit forms.
  [phgross]

- Task: Adjust workflow, so that documents inside a task, aren't editable
  when the dossier is closed.
  [phgross]

- AdvancedSearch: Added special description for the portal types field
  in a multiclientsetup.
  [phgross]

- Added filter_pattern option to LDAPSource blueprint.
  If set, only imports users whose email address match `filter_pattern`.
  [lgraf]

- Rebuild OpengeverContentListing registration.
  Use additional interface instead of overrides.zcml
  [phgross]

- Monkey patch plone.dexterity.content.Container.__ac_permissions__ in order
  to declare sane permissions for manage_pasteObjects.
  [lgraf]

- Added bin/build-translations script to opengever.core buildout.
  [lgraf]

- Added bin/i18n-build script to opengever.core buildout.
  [lgraf]

- Made sure PDF Preview link in doc tooltip is only displayed when
  PDF preview rendering is available.
  [lgraf]

- Lay out date range fields in advanced search form side by side.
  Note: This requires the "Init og.advancedsearch profile version" upgrade
  step from opengever.base to be run first!
  [lgraf]

- Removed description texts for advanced search dossier date range fields.
  This is being done in order to avoid layouting issues.

- Extract attachments: Set digitially_available allways to true.
  [phgross]
