from copy import deepcopy
from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from requests_toolbelt.utils import formdata
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import pytz


class MoveItemsHelper(object):

    def move_items(self, items, source=None, target=None):
        paths = u";;".join(["/".join(i.getPhysicalPath()) for i in items])
        self.request['paths'] = paths
        self.request['form.widgets.request_paths'] = paths
        self.request['form.widgets.destination_folder'] = "/".join(
            target.getPhysicalPath())

        view = source.restrictedTraverse('move_items')
        form = view.form(source, self.request)
        form.updateWidgets()
        form.widgets['destination_folder'].value = target
        form.widgets['request_paths'].value = paths

        form.handle_submit(form, object)


class TestMoveItems(IntegrationTestCase, MoveItemsHelper):

    def test_cant_move_items_to_invalid_target(self):
        self.login(self.manager)
        bad_target = create(Builder("repository"))
        task_title = self.task.title.encode("utf-8")
        self.assert_contains(self.dossier, [task_title])
        self.assert_does_not_contain(bad_target, [task_title])
        self.move_items([self.task], source=self.dossier, target=bad_target)
        self.assert_contains(self.dossier, [task_title])
        self.assert_does_not_contain(bad_target, [task_title])

    def test_render_documents_tab_when_no_items_are_selected(self):
        self.login(self.regular_user)
        view = self.dossier.restrictedTraverse('move_items')
        self.assertEquals("%s#documents" % self.dossier.absolute_url(), view())

    def test_render_orig_template_when_no_items_are_selected(self):
        self.login(self.regular_user)
        view = self.dossier.restrictedTraverse('move_items')
        self.request.form[
            'orig_template'] = "%s#dossiers" % self.dossier.absolute_url()
        self.assertEquals("%s#dossiers" % self.dossier.absolute_url(), view())

    def test_move_items_to_valid_target(self):
        """ Test integration of move_items method
        """
        self.login(self.manager)
        subdossier_title = self.subdossier.title.encode("utf-8")
        doc_title = self.document.title.encode("utf-8")
        self.assert_contains(self.dossier, [doc_title, subdossier_title])
        self.assert_does_not_contain(self.empty_dossier,
                                     [doc_title, subdossier_title])

        self.move_items([self.document, self.subdossier],
                        source=self.dossier,
                        target=self.empty_dossier)

        self.assert_does_not_contain(
            self.dossier, [doc_title, subdossier_title])
        self.assert_contains(self.empty_dossier, [doc_title, subdossier_title])

    def test_only_open_items_appear_in_destination_widget(self):
        self.login(self.dossier_manager)

        self.request['paths'] = '/'.join(self.dossier.getPhysicalPath())

        uids = self.get_uids_from_tree_widget()

        self.assertIn(IUUID(self.empty_dossier), uids,
                      "Active dossier not found as target in move items")

        self.assertNotIn(IUUID(self.expired_dossier), uids,
                         "Closed dossier found as target in move items")

    def get_uids_from_tree_widget(self):
        view = self.branch_repofolder.restrictedTraverse('move_items')
        form = view.form(self.branch_repofolder, self.request)
        form.updateWidgets()

        catalog = getToolByName(self.portal, 'portal_catalog')
        widget = form.widgets['destination_folder']
        query_result = catalog(widget.bound_source.navigation_tree_query)

        return [item.UID for item in query_result]

    def assert_contains(self, container, items):
        for item in items:
            self.assertIn(item,
                          [a.Title for a in container.getFolderContents()])

    def assert_does_not_contain(self, container, items):
        for item in items:
            self.assertNotIn(item,
                             [a.Title for a in container.getFolderContents()])


class TestMoveItemsUpdatesIndexAndMetadata(IntegrationTestCase, MoveItemsHelper):

    MOVE_TIME = datetime(2018, 4, 30, 0, 0, tzinfo=pytz.UTC)

    @browsing
    def test_move_document_metadata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        subdocument_metadata = self.get_catalog_metadata(self.subdocument)

        with freeze(self.MOVE_TIME):
            ZOPE_MOVE_TIME = DateTime()

            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.subdocument, ),
                                source=self.subdossier,
                                target=self.empty_dossier)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_metadata = self.get_catalog_metadata(moved)

        ZOPE_MOVE_TIME_STR = ZOPE_MOVE_TIME.toZone(DateTime().localZone()).ISO()

        # We expect some of the metadata to get modified during pasting
        modified_metadata = {'UID': moved.UID(),
                             # creator
                             'listCreators': ('robert.ziegler', 'kathi.barfuss'),
                             # dates
                             'start': self.MOVE_TIME.date(),  # acquisition is responsible here
                             'modified': ZOPE_MOVE_TIME,
                             'ModificationDate': ZOPE_MOVE_TIME_STR,
                             'Date': ZOPE_MOVE_TIME_STR,
                             # containing dossier and subdossier
                             'reference': 'Client1 1.1 / 4 / 22',
                             'containing_dossier': self.empty_dossier.Title(),
                             'containing_subdossier': '',
                             }

        unchanged_metadata = ['id',
                              'getId',
                              'sequence_number',
                              'Creator',
                              'created',
                              'CreationDate',
                              'changed',
                              'Title',
                              'filename',
                              'Description',
                              'EffectiveDate',
                              'ExpirationDate',
                              'Subject',
                              'Type',
                              'assigned_client',
                              'author_name',
                              'bumblebee_checksum',
                              'checked_out',
                              'cmf_uid',
                              'commentators',
                              'contactid',
                              'css_icon_class',
                              'date_of_completion',
                              'deadline',
                              'delivery_date',
                              'document_author',
                              'document_date',
                              'effective',
                              'email',
                              'email2',
                              'end',
                              'exclude_from_nav',
                              'expires',
                              'file_extension',
                              'filesize',
                              'firstname',
                              'getContentType',
                              'getIcon',
                              'getObjSize',
                              'getRemoteUrl',
                              'has_sametype_children',
                              'in_response_to',
                              'is_folderish',
                              'is_subtask',
                              'issuer',
                              'last_comment_date',
                              'lastname',
                              'location',
                              'meta_type',
                              'phone_office',
                              'portal_type',
                              'predecessor',
                              'preselected',
                              'public_trial',
                              'receipt_date',
                              'responsible',
                              'retention_expiration',
                              'review_state',
                              'task_type',
                              'title_de',
                              'title_fr',
                              'total_comments',
                              'trashed']

        # Make sure no metadata key is in both lists of unchanged and modified metadata
        self.assertTrue(set(unchanged_metadata).isdisjoint(modified_metadata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_metadata = deepcopy(modified_metadata)
        expected_metadata.update({key: subdocument_metadata[key] for key in unchanged_metadata})

        # Make sure that the developer thinks about whether a newly added metadata
        # column should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_metadata.keys(),
            subdocument_metadata.keys(),
            msg="A new metadata column was added, please add it to "
                "'unchanged_metadata' if it should not be modified during "
                "copy/paste of a document, or to 'modified_metadata' otherwise")

        self.assertDictEqual(expected_metadata, moved_metadata)

        # Make sure the metadata was up to date
        # we freeze to the move time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
        reindexed_moved_metadata = self.get_catalog_metadata(moved)

        # Everything up to date
        self.assertDictEqual(moved_metadata, reindexed_moved_metadata,
                             msg="Some metadata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_document_indexdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        subdocument_indexdata = self.get_catalog_indexdata(self.subdocument)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.subdocument, ),
                                source=self.subdossier,
                                target=self.empty_dossier)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_indexdata = self.get_catalog_indexdata(moved)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = self.dateindex_value_from_datetime(self.MOVE_TIME)
        modified_indexdata = {
            'UID': moved.UID(),
            'path': moved.absolute_url_path(),

            # dates
            'modified': paste_time_index,
            'Date': paste_time_index,
            # 'start': paste_time_index,

            # containing dossier and subdossier
            'containing_dossier': self.empty_dossier.Title(),
            'containing_subdossier': '',
            # 'reference': 'Client1 1.1 / 4 / 41', # reference should be updated
        }

        unchanged_indexdata = ['id',
                               'getId',
                               'reference',
                               'sequence_number',
                               'is_subdossier',
                               'Title',
                               'sortable_title',
                               'SearchableText',
                               'changed',
                               'start',
                               'Creator',
                               'Description',
                               'Subject',
                               'Type',
                               'after_resolve_jobs_pending',
                               'allowedRolesAndUsers',
                               'assigned_client',
                               'blocked_local_roles',
                               'checked_out',
                               'client_id',
                               'cmf_uid',
                               'commentators',
                               'contactid',
                               'created',
                               'date_of_completion',
                               'deadline',
                               'delivery_date',
                               'document_author',
                               'document_date',
                               'document_type',
                               'effective',
                               'effectiveRange',
                               'email',
                               'end',
                               'expires',
                               'external_reference',
                               'file_extension',
                               'filesize',
                               'firstname',
                               'getObjPositionInParent',
                               'getRawRelatedItems',
                               'in_reply_to',
                               'is_default_page',
                               'is_folderish',
                               'is_subtask',
                               'issuer',
                               'lastname',
                               'meta_type',
                               'object_provides',
                               'phone_office',
                               'portal_type',
                               'predecessor',
                               'public_trial',
                               'receipt_date',
                               'responsible',
                               'retention_expiration',
                               'review_state',
                               'sortable_author',
                               'task_type',
                               'total_comments',
                               'trashed']

        # Make sure no index is in both lists of unchanged and modified indexdata
        self.assertTrue(set(unchanged_indexdata).isdisjoint(modified_indexdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_indexdata = deepcopy(modified_indexdata)
        expected_indexdata.update({key: subdocument_indexdata[key] for key in unchanged_indexdata})

        # Make sure that the developer thinks about whether a newly added
        # index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_indexdata.keys(),
            subdocument_indexdata.keys(),
            msg="A new index was added, please add it to 'unchanged_indexdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_indexdata' otherwise")

        self.assertDictEqual(expected_indexdata, moved_indexdata)

        # Make sure the indexdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            reindexed_moved_indexdata = self.get_catalog_indexdata(moved)

        # Some index data is not up to date, but does not have to be
        # such as "is_subdossier".
        # Other data should be up to date but is not. For example the SearchableText
        # is not reindexed on purpose for efficiency, but it actually changes
        # because the reference number changes...
        not_up_to_date = ['SearchableText', 'is_subdossier', 'reference', 'start']
        for key in not_up_to_date:
            self.assertNotEqual(moved_indexdata.pop(key),
                                reindexed_moved_indexdata.pop(key))

        self.assertDictEqual(moved_indexdata, reindexed_moved_indexdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")


class TestContainingDossierAndSubdossierIndexWhenMovingItem(IntegrationTestCase, MoveItemsHelper):

    def test_indexes_are_updated_when_document_moved_from_dossier_to_dossier(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.document)
        self.assert_index_and_metadata('',
                                       'containing_subdossier', self.document)

        with self.observe_children(self.empty_dossier) as children:
            self.move_items([self.document],
                            source=self.dossier,
                            target=self.empty_dossier)

        document, = children.get('added')
        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', document)
        self.assert_index_and_metadata('',
                                       'containing_subdossier', document)

    def test_indexes_are_updated_when_document_moved_from_subdossier_to_subdossier(self):
        self.login(self.regular_user)
        empty_subdossier = create(Builder("dossier").titled(u"destination").within(self.empty_dossier))

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subdocument)
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', self.subdocument)

        with self.observe_children(empty_subdossier) as children:
            self.move_items([self.subdocument],
                            source=self.subdossier,
                            target=empty_subdossier)

        document, = children.get('added')
        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', document)
        self.assert_index_and_metadata(empty_subdossier.Title(),
                                       'containing_subdossier', document)

    def test_indexes_are_updated_when_document_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.meeting_dossier.Title(),
                                       'containing_dossier', self.meeting_document)
        self.assert_index_and_metadata('',
                                       'containing_subdossier', self.meeting_document)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.meeting_document],
                            source=self.meeting_dossier,
                            target=self.subdossier)

        document, = children.get('added')
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', document)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', document)

    def test_indexes_are_updated_when_document_moved_from_subdossier_to_dossier(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subdocument)
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', self.subdocument)

        with self.observe_children(self.meeting_dossier) as children:
            self.move_items([self.subdocument],
                            source=self.subdossier,
                            target=self.meeting_dossier)

        document, = children.get('added')
        self.assert_index_and_metadata('',
                                       'containing_subdossier', document)
        self.assert_index_and_metadata(self.meeting_dossier.Title(),
                                       'containing_dossier', document)

    def test_indexes_are_updated_when_task_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.meeting_dossier.Title(),
                                       'containing_dossier', self.meeting_task)
        self.assert_index_and_metadata('', 'containing_subdossier', self.meeting_task)

        self.assert_index_and_metadata(self.meeting_dossier.Title(),
                                       'containing_dossier', self.meeting_subtask)
        self.assert_index_and_metadata('', 'containing_subdossier', self.meeting_subtask)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.meeting_task],
                            source=self.meeting_dossier,
                            target=self.subdossier)

        task, = children.get('added')
        subtask = api.content.find(task, depth=1)[0].getObject()
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', task)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', task)
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', subtask)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', subtask)

    def test_indexes_are_updated_when_mail_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.mail_eml)
        self.assert_index_and_metadata('',
                                       'containing_subdossier', self.mail_eml)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.mail_eml],
                            source=self.dossier,
                            target=self.subdossier)

        mail, = children.get('added')
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', mail)
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', mail)

    def test_indexes_are_updated_when_subdossier_is_moved_into_repofolder(self):
        self.login(self.regular_user)

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subdocument)
        self.assert_index_and_metadata(self.subdossier.Title(),
                                       'containing_subdossier', self.subdocument)

        self.assert_index_value(1, 'is_subdossier', self.subdossier)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subdossier)

        self.assert_index_value(1, 'is_subdossier', self.subsubdossier)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subsubdossier)

        with self.observe_children(self.empty_repofolder) as children:
            self.move_items([self.subdossier],
                            source=self.dossier,
                            target=self.empty_repofolder)

        dossier, = children.get('added')
        subdossier = dossier.get_subdossiers()[0].getObject()
        document = api.content.find(context=dossier,
                                    portal_type="opengever.document.document",
                                    depth=1)[0].getObject()

        self.assert_index_value(0, 'is_subdossier', dossier)
        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_dossier', dossier)

        self.assert_index_value(1, 'is_subdossier', subdossier)
        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_dossier', subdossier)

        self.assert_index_and_metadata('', 'containing_subdossier', document)
        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_dossier', document)

    def test_indexes_are_updated_when_subsubdossier_is_moved_into_repofolder(self):
        self.login(self.regular_user)
        subsubdocument = create(Builder("document").titled(u"subsubdocument")
                                .within(self.subsubdossier))

        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', subsubdocument)
        self.assert_index_and_metadata(self.subsubdossier.Title(),
                                       'containing_subdossier', subsubdocument)

        self.assert_index_value(1, 'is_subdossier', self.subsubdossier)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', self.subsubdossier)

        with self.observe_children(self.empty_repofolder) as children:
            self.move_items([self.subsubdossier],
                            source=self.dossier,
                            target=self.empty_repofolder)

        dossier, = children.get('added')
        document = api.content.find(context=dossier,
                                    portal_type="opengever.document.document",
                                    depth=1)[0].getObject()

        self.assert_index_value(0, 'is_subdossier', dossier)
        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_dossier', dossier)

        self.assert_index_and_metadata('', 'containing_subdossier', document)
        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_dossier', document)

    def test_indexes_are_updated_when_dossier_is_moved_into_dossier(self):
        self.login(self.regular_user)
        document = create(Builder("document").titled(u"document").within(self.empty_dossier))

        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', document)
        self.assert_index_and_metadata('', 'containing_subdossier', document)

        self.assert_index_value(0, 'is_subdossier', self.empty_dossier)
        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', self.empty_dossier)

        with self.observe_children(self.dossier) as children:
            self.move_items([self.empty_dossier],
                            source=self.leaf_repofolder,
                            target=self.dossier)

        dossier, = children.get('added')
        document = api.content.find(context=dossier, depth=1)[0].getObject()

        self.assert_index_value(1, 'is_subdossier', dossier)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', dossier)

        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_subdossier', document)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', document)

    def test_indexes_are_updated_when_dossier_is_moved_into_subsubdossier(self):
        self.login(self.regular_user)
        api.portal.set_registry_record(
            "opengever.dossier.interfaces.IDossierContainerTypes.maximum_dossier_depth", 2)
        document = create(Builder("document").titled(u"document").within(self.empty_dossier))

        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', document)
        self.assert_index_and_metadata('',
                                       'containing_subdossier', document)

        self.assert_index_value(0, 'is_subdossier', self.empty_dossier)
        self.assert_index_and_metadata(self.empty_dossier.Title(),
                                       'containing_dossier', self.empty_dossier)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.empty_dossier],
                            source=self.leaf_repofolder,
                            target=self.subdossier)

        dossier, = children.get('added')
        document = api.content.find(context=dossier, depth=1)[0].getObject()

        self.assert_index_value(1, 'is_subdossier', dossier)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', dossier)

        self.assert_index_and_metadata(dossier.Title(),
                                       'containing_subdossier', document)
        self.assert_index_and_metadata(self.dossier.Title(),
                                       'containing_dossier', document)


class TestMoveItemsWithTestbrowser(IntegrationTestCase):

    def move_items(self, browser, src, obj=None, task=None, target=None):
        path = None
        task_ids = None

        if isinstance(obj, basestring):
            path = obj
        elif obj is not None:
            path = '/'.join(obj.getPhysicalPath())

        if task:
            task_ids = task.get_sql_object().task_id

        payload = {}
        if task_ids:
            payload['task_ids'] = task_ids
        if path:
            payload['paths:list'] = [path]

        browser.login().open(src, payload, view='move_items')

        if not browser.url.endswith('move_items'):
            # Might have been redirected because of an error
            return

        browser.fill({'Destination': target})
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_redirects_to_context_and_show_statusmessage_when_obj_cant_be_found(self, browser):
        self.login(self.regular_user)
        self.move_items(
            browser, src=self.dossier,
            obj='/invalid/path', target=self.empty_dossier)

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual(
            "The selected objects can't be found, please try it again.",
            error_messages()[0])

    @browsing
    def test_document_inside_a_task_is_not_movable(self, browser):
        self.login(self.regular_user)
        self.move_items(
            browser, src=self.task,
            obj=self.taskdocument, target=self.empty_dossier)

        self.assertEqual(
            'Document {} is inside a task and therefore not movable. Move the task instead'.format(self.taskdocument.title),
            error_messages()[0])
        self.assertIn(self.taskdocument, self.task.objectValues())
        self.assertNotIn(self.taskdocument, self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.expired_dossier,
            obj=self.expired_document, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.expired_document,
                      self.expired_dossier.objectValues())
        self.assertNotIn(self.expired_document,
                         self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_inactive_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.inactive_dossier,
            obj=self.inactive_document, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.inactive_document,
                      self.inactive_dossier.objectValues())
        self.assertNotIn(self.inactive_document,
                         self.empty_dossier.objectValues())

    @browsing
    def test_task_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.move_items(
            browser, src=self.expired_dossier,
            task=self.expired_task, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.expired_task, self.expired_dossier.objectValues())
        self.assertNotIn(self.expired_task, self.empty_dossier.objectValues())

    @browsing
    def test_mail_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.move_items(
            browser, src=self.dossier,
            obj=self.mail_eml, target=self.empty_dossier)

        self.assertEqual(
            ['Can only move objects from open dossiers!'],
            error_messages())
        self.assertIn(self.mail_eml, self.dossier.objectValues())
        self.assertNotIn(self.mail_eml, self.empty_dossier.objectValues())

    @browsing
    def test_task_are_handled_correctly(self, browser):
        self.login(self.regular_user)
        task_intid = getUtility(IIntIds).getId(self.subtask)
        self.move_items(
            browser, src=self.task,
            task=self.subtask, target=self.empty_dossier)
        subtask = getUtility(IIntIds).getObject(task_intid)
        self.assertIn(subtask, self.empty_dossier.objectValues())

    @browsing
    def test_move_items_within_templatefolder_is_possible(self, browser):
        self.login(self.regular_user, browser)
        # if the template folders are not in a valid root, this does not work
        # No idea why it used to work in the functional test?
        templatefolder = create(Builder('templatefolder').within(self.repository_root))
        subtemplatefolder = create(
            Builder('templatefolder').within(templatefolder))
        document = create(Builder('document').within(templatefolder))
        self.move_items(browser, src=templatefolder,
                        obj=document, target=subtemplatefolder)
        self.assertIn(document, subtemplatefolder.objectValues())

    @browsing
    def test_paste_action_not_visible_for_closed_dossiers(self, browser):
        self.login(self.dossier_manager, browser)
        paths = ['/'.join(self.document.getPhysicalPath())]
        browser.open(
            self.dossier, {'paths:list': paths}, view='copy_items')

        browser.open(self.empty_dossier)
        self.assertIsNotNone(
            browser.find('Paste'),
            'Paste should be visible for open dossiers')

        browser.open(self.expired_dossier)
        self.assertIsNone(
            browser.find('Paste'),
            'Paste should not be visible for resolved dossiers')

    @browsing
    def test_copy_then_move(self, browser):
        self.login(self.regular_user, browser)

        # Copy the document
        paths = ['/'.join(self.document.getPhysicalPath())]
        browser.open(
            self.empty_dossier, {'paths:list': paths}, view='copy_items')

        # Move the same document we copied before
        browser.open(
            self.empty_dossier, {'paths:list': paths}, view='move_items')
        browser.fill({'Destination': self.dossier})

        # Should not cause our check in is_pasting_allowed view to fail
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_reference_number_is_not_reset_when_moving_to_same_parent(self, browser):
        """When a dossier is select to be moved but the target is the current
        parent, the dossier will not actually change the location.
        In this case the reference number should not be changed.
        """
        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.empty_dossier)

        self.move_items(browser,
                        obj=self.empty_dossier,
                        src=self.leaf_repofolder,
                        target=self.leaf_repofolder)
        assert_no_error_messages()

        # transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Moving to the current parent should not change'
                          ' the reference number because the location does'
                          ' not change.')

    @browsing
    def test_reference_number_is_recycled_when_moving_dossier_back(self, browser):
        """When a dossier is moved back to a repository where it was before,
        the original reference number should be recycled.
        """
        self.login(self.regular_user, browser)
        browser.open(self.empty_dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number. Test fixture changed?')
        dossier_intid = getUtility(IIntIds).getId(self.empty_dossier)

        # Move to other_repository
        self.move_items(browser, obj=self.empty_dossier,
                        src=self.leaf_repofolder, target=self.empty_repofolder)
        assert_no_error_messages()

        # transaction.begin()  # sync
        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)

        self.assertEquals('Reference Number: Client1 2 / 1',
                          browser.css('.reference_number').first.text,
                          'Unexpected reference number after moving.')

        # Move back to source_repo
        self.move_items(browser,
                        obj=dossier,
                        src=self.empty_repofolder,
                        target=self.leaf_repofolder)
        assert_no_error_messages()

        dossier = getUtility(IIntIds).getObject(dossier_intid)
        browser.open(dossier)
        self.assertEquals('Reference Number: Client1 1.1 / 4',
                          browser.css('.reference_number').first.text,
                          'When moving back, the old reference_number should be'
                          ' recycled.')

    @browsing
    def test_reference_widgets_content_is_sorted(self, browser):
        self.login(self.dossier_responsible, browser)

        repo = create(Builder('repository')
                      .having(title_de=u'drittes repo')
                      .within(self.repository_root))

        self.repository_root.moveObjectsUp(repo.id)
        self.repository_root.moveObjectsUp(repo.id)

        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '@@move_items',
            '++widget++form.widgets.destination_folder',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({
                'href': '/'.join(self.repository_root.getPhysicalPath()),
                'rel': 0,
            }),
        )

        selectables = browser.css('li.selectable').text

        self.assertEquals(
            ['fuhrung', 'rechnungsprufungskommission', 'drittes-repo'],
            selectables)


class TestMoveItemsWithTestbrowserSolr(SolrIntegrationTestCase):

    @browsing
    def test_move_target_autocomplete_widget_does_not_list_repo_roots(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.repository_root.title_or_id()))))
        self.assertEqual('', browser.contents)

    @browsing
    def test_move_target_autocomplete_widget_lists_repofolders(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.branch_repofolder.title_or_id()))))
        self.assertEqual('/plone/ordnungssystem/fuhrung|fuhrung', browser.contents)

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.leaf_repofolder.title_or_id().replace("-", " ")))))
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen|vertrage-und-vereinbarungen',
            browser.contents,
        )

    @browsing
    def test_move_target_autocomplete_widget_does_not_list_inactive_repo_folders(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.inactive_repofolder.title_or_id()))))
        self.assertEqual('', browser.contents)

    @browsing
    def test_move_target_autocomplete_widget_lists_open_dossiers(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.dossier.title_or_id()))))
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'
            '|Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
            browser.contents,
        )

    @browsing
    def test_move_target_autocomplete_widget_does_not_list_closed_dossiers(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.inactive_dossier.title_or_id()))))
        self.assertEqual('', browser.contents)

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.expired_dossier.title_or_id()))))
        self.assertEqual('', browser.contents)
