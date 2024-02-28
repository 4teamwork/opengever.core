from copy import deepcopy
from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.converters import to_iso8601
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testing import freeze
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.move_items import DossierMovabiliyChecker
from opengever.dossier.move_items import DossierTemplateMovabilityChecker
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.helpers import solr_data_for
from plone import api
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from requests_toolbelt.utils import formdata
from zExceptions import Forbidden
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

    def test_moving_dossier_respects_maximum_dossier_depth(self):
        self.login(self.manager)
        empty_dossier_title = self.empty_dossier.title.encode("utf-8")
        self.assert_contains(self.leaf_repofolder, [empty_dossier_title])
        self.assert_does_not_contain(self.resolvable_subdossier, [empty_dossier_title])
        self.move_items([self.empty_dossier],
                        source=self.leaf_repofolder,
                        target=self.resolvable_subdossier)
        self.assert_contains(self.leaf_repofolder, [empty_dossier_title])
        self.assert_does_not_contain(self.resolvable_subdossier, [empty_dossier_title])

    @browsing
    def test_moving_dossier_containing_subdossier_respects_maximum_dossier_depth(self, browser):
        self.login(self.manager, browser)
        resolvable_dossier_title = self.resolvable_dossier.title.encode("utf-8")
        self.assert_contains(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_does_not_contain(self.empty_dossier, [resolvable_dossier_title])
        self.move_items([self.resolvable_dossier],
                        source=self.leaf_repofolder,
                        target=self.empty_dossier)
        self.assert_contains(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_does_not_contain(self.empty_dossier, [resolvable_dossier_title])

        api.portal.set_registry_record(
            name='maximum_dossier_depth',
            value=2,
            interface=IDossierContainerTypes
        )

        self.move_items([self.resolvable_dossier],
                        source=self.leaf_repofolder,
                        target=self.empty_dossier)
        self.assert_does_not_contain(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_contains(self.empty_dossier, [resolvable_dossier_title])

    @browsing
    def test_moving_dossier_respects_containing_repository_subdossier_restriction_property(self, browser):
        self.login(self.manager, browser)
        resolvable_dossier_title = self.resolvable_dossier.title.encode("utf-8")
        self.assert_contains(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_does_not_contain(self.empty_dossier, [resolvable_dossier_title])
        self.move_items([self.resolvable_dossier],
                        source=self.leaf_repofolder,
                        target=self.empty_dossier)
        self.assert_contains(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_does_not_contain(self.empty_dossier, [resolvable_dossier_title])

        self.leaf_repofolder.respect_max_subdossier_depth_restriction = False

        self.move_items([self.resolvable_dossier],
                        source=self.leaf_repofolder,
                        target=self.empty_dossier)
        self.assert_does_not_contain(self.leaf_repofolder, [resolvable_dossier_title])
        self.assert_contains(self.empty_dossier, [resolvable_dossier_title])

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

    def test_reader_cannot_move_items(self):
        self.login(self.manager)

        self.subsubdossier.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.subsubdossier).add_or_update_assignment(
            SharingRoleAssignment(self.regular_user.getId(),
                                  ['Reader', 'Contributor'],
                                  self.subsubdossier))

        self.assertFalse(api.user.has_permission(
            "Copy or Move", user=self.regular_user, obj=self.subsubdossier))
        self.assertFalse(api.user.has_permission(
            "Copy or Move", user=self.regular_user, obj=self.subsubdocument))

        doc_title = self.subsubdocument.title.encode("utf-8")
        self.assert_contains(self.subsubdossier, [doc_title])
        self.assert_does_not_contain(self.empty_dossier, [doc_title])

        with self.login(self.regular_user):
            self.move_items([self.subsubdocument],
                            source=self.subsubdossier,
                            target=self.empty_dossier)

        self.assert_contains(self.subsubdossier, [doc_title])
        self.assert_does_not_contain(self.empty_dossier, [doc_title])

    def test_move_items_to_valid_target(self):
        """ Test integration of move_items method
        """
        self.login(self.manager)
        subsubdossier_title = self.subsubdossier.title.encode("utf-8")
        doc_title = self.subdocument.title.encode("utf-8")
        self.assert_contains(self.subdossier, [doc_title, subsubdossier_title])
        self.assert_does_not_contain(self.empty_dossier,
                                     [doc_title, subsubdossier_title])

        self.move_items([self.subdocument, self.subsubdossier],
                        source=self.subdossier,
                        target=self.empty_dossier)

        self.assert_does_not_contain(
            self.subdossier, [doc_title, subsubdossier_title])
        self.assert_contains(self.empty_dossier, [doc_title, subsubdossier_title])

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


class TestMoveItemsUpdatesIndexAndMetadata(SolrIntegrationTestCase, MoveItemsHelper):

    MOVE_TIME = datetime(2018, 4, 30, 0, 0, tzinfo=pytz.UTC)

    common_unchanged_metadata = [
        'bumblebee_checksum',
        'changed',
        'checked_out',
        'cmf_uid',
        'contactid',
        'created',
        'Creator',
        'css_icon_class',
        'delivery_date',
        'Description',
        'document_author',
        'document_date',
        'email',
        'email2',
        'end',
        'exclude_from_nav',
        'file_extension',
        'filename',
        'filesize',
        'firstname',
        'getContentType',
        'getIcon',
        'getId',
        'gever_doc_uid',
        'has_sametype_children',
        'id',
        'in_response_to',
        'is_folderish',
        'is_subtask',
        'lastname',
        'phone_office',
        'portal_type',
        'preselected',
        'public_trial',
        'receipt_date',
        'responsible',
        'retention_expiration',
        'review_state',
        'sequence_number',
        'start',
        'Subject',
        'task_type',
        'Title',
        'title_de',
        'title_en',
        'title_fr',
        'trashed',
        'Type',
        'UID',
    ]

    common_unchanged_indexdata = [
        'after_resolve_jobs_pending',
        'blocked_local_roles',
        'changed',
        'checked_out',
        'cmf_uid',
        'contactid',
        'created',
        'Creator',
        'delivery_date',
        'document_date',
        'document_type',
        'email',
        'end',
        'external_reference',
        'file_extension',
        'filesize',
        'firstname',
        'getId',
        'getObjPositionInParent',
        'hide_member_details',
        'id',
        'is_folderish',
        'is_subtask',
        'lastname',
        'object_provides',
        'phone_office',
        'portal_type',
        'public_trial',
        'receipt_date',
        'responsible',
        'retention_expiration',
        'review_state',
        'sequence_number',
        'sortable_title',
        'start',
        'start',
        'Subject',
        'task_type',
        'Title',
        'trashed',
        'Type',
        'UID',
    ]

    common_unchanged_solrdata = [
        u'changed',
        u'created',
        u'Creator',
        u'Description',
        u'getIcon',
        u'getObjSize',
        u'id',
        u'is_folderish',
        u'language',
        u'object_provides',
        u'portal_type',
        u'public_trial',
        u'review_state',
        u'sequence_number',
        u'sequence_number_string',
        u'sortable_title',
        u'Title',
        u'trashed',
        u'UID',
    ]

    # Updating language specific fields is a bit unpredictable as the detected
    # language may vary. We therefore ignore these fields.
    ignored_solrdata = [
        u'_language_',
        u'Description_de',
        u'Description_en',
        u'Description_fr',
        u'Description_general',
        u'SearchableText_de',
        u'SearchableText_en',
        u'SearchableText_fr',
        u'SearchableText_general',
        u'Title_de',
        u'Title_en',
        u'Title_fr',
        u'Title_general',
    ]

    def remove_ignored_solrdata(self, data):
        for ignored in self.ignored_solrdata:
            if ignored in data:
                del data[ignored]

    @browsing
    def test_move_document_metadata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_metadata = self.get_catalog_metadata(self.subdocument)

        with freeze(self.MOVE_TIME):
            ZOPE_MOVE_TIME = DateTime()

            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.subdocument, ),
                                source=self.subdossier,
                                target=self.empty_dossier)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_metadata = self.get_catalog_metadata(moved)

        # We expect some of the metadata to get modified during pasting
        modified_metadata = {
            'listCreators': (self.dossier_responsible.id, self.regular_user.id),
            'modified': ZOPE_MOVE_TIME,
            'reference': 'Client1 1.1 / 4 / 22',
        }

        unchanged_metadata = [
            'is_subdossier',
        ]
        unchanged_metadata += self.common_unchanged_metadata

        # Make sure no metadata key is in both lists of unchanged and modified metadata
        self.assertTrue(set(unchanged_metadata).isdisjoint(modified_metadata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_metadata = deepcopy(modified_metadata)
        expected_metadata.update({key: initial_metadata[key] for key in unchanged_metadata})

        # Make sure fields expected to change really did
        for key, value in modified_metadata.items():
            self.assertNotEqual(
                initial_metadata[key], value,
                "Expected {} to have changed during move".format(key))

        # Make sure that the developer thinks about whether a newly added metadata
        # column should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_metadata.keys(),
            initial_metadata.keys(),
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
    def test_move_document_solrdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        # ensure pos in parent changes by creating content in target dossier
        create(Builder('document').within(self.empty_dossier))
        self.commit_solr()

        initial_solrdata = solr_data_for(self.subdocument)
        self.remove_ignored_solrdata(initial_solrdata)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.subdocument, ),
                                source=self.subdossier,
                                target=self.empty_dossier)
                self.commit_solr()

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_solrdata = solr_data_for(moved)
        self.remove_ignored_solrdata(moved_solrdata)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = to_iso8601(self.MOVE_TIME).replace(".000Z", "Z")
        modified_solrdata = {
            '_version_': moved_solrdata['_version_'],
            'containing_dossier': self.empty_dossier.Title(),
            'containing_subdossier': '',
            'getObjPositionInParent': 1,
            'metadata': 'Client1 1.1 / 4 / 22 Wichtig Subkeyword',
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'path_depth': 6,
            'path_parent': moved.absolute_url_path(),
            'reference': 'Client1 1.1 / 4 / 22',
            'sortable_reference': 'client00000001 00000001.00000001 / 00000004 / 00000022',
        }

        unchanged_solrdata = [
            u'allowedRolesAndUsers',
            u'bumblebee_checksum',
            u'checked_out',
            u'document_date',
            u'file_extension',
            u'filename',
            u'filesize',
            u'related_items',
            u'Subject',
            u'is_locked_by_copy_to_workspace',
        ]

        unchanged_solrdata += self.common_unchanged_solrdata

        # Make sure no key is in both lists of unchanged and modified data
        self.assertTrue(set(unchanged_solrdata).isdisjoint(modified_solrdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_solrdata = deepcopy(modified_solrdata)
        expected_solrdata.update({key: initial_solrdata[key] for key in unchanged_solrdata})

        # Make sure that the developer thinks about whether a newly added
        # solr index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_solrdata.keys(),
            initial_solrdata.keys(),
            msg="A new solr index was added, please add it to 'unchanged_solrdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_solrdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_solrdata.items():
            self.assertNotEqual(
                initial_solrdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_solrdata, moved_solrdata)

        # Make sure the solrdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            self.commit_solr()
            reindexed_moved_solrdata = solr_data_for(moved)
            self.remove_ignored_solrdata(reindexed_moved_solrdata)

        # Some index data is not up to date, but does not have to be
        # Other data should be up to date but is not.
        not_up_to_date = ['_version_']
        for key in not_up_to_date:
            self.assertNotEqual(moved_solrdata.pop(key),
                                reindexed_moved_solrdata.pop(key))

        self.assertDictEqual(moved_solrdata, reindexed_moved_solrdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_document_indexdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_indexdata = self.get_catalog_indexdata(self.subdocument)

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
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'reference': 'Client1 1.1 / 4 / 22',
        }

        unchanged_indexdata = [
            'allowedRolesAndUsers',
            'is_subdossier',
        ]
        unchanged_indexdata += self.common_unchanged_indexdata

        # Make sure no index is in both lists of unchanged and modified indexdata
        self.assertTrue(set(unchanged_indexdata).isdisjoint(modified_indexdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_indexdata = deepcopy(modified_indexdata)
        expected_indexdata.update({key: initial_indexdata[key] for key in unchanged_indexdata})

        # Make sure that the developer thinks about whether a newly added
        # index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_indexdata.keys(),
            initial_indexdata.keys(),
            msg="A new index was added, please add it to 'unchanged_indexdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_indexdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_indexdata.items():
            self.assertNotEqual(
                initial_indexdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_indexdata, moved_indexdata)

        # Make sure the indexdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            reindexed_moved_indexdata = self.get_catalog_indexdata(moved)

        self.assertDictEqual(moved_indexdata, reindexed_moved_indexdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_mail_metadata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_metadata = self.get_catalog_metadata(self.mail_eml)

        with freeze(self.MOVE_TIME):
            ZOPE_MOVE_TIME = DateTime()

            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.mail_eml, ),
                                source=self.dossier,
                                target=self.empty_dossier)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_metadata = self.get_catalog_metadata(moved)

        # We expect some of the metadata to get modified during pasting
        modified_metadata = {
            'listCreators': (self.dossier_responsible.id, self.regular_user.id),
            'modified': ZOPE_MOVE_TIME,
            'reference': 'Client1 1.1 / 4 / 29',
        }

        unchanged_metadata = [
            'is_subdossier',
        ]
        unchanged_metadata += self.common_unchanged_metadata

        # Make sure no metadata key is in both lists of unchanged and modified metadata
        self.assertTrue(set(unchanged_metadata).isdisjoint(modified_metadata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_metadata = deepcopy(modified_metadata)
        expected_metadata.update({key: initial_metadata[key] for key in unchanged_metadata})

        # Make sure fields expected to change really did
        for key, value in modified_metadata.items():
            self.assertNotEqual(
                initial_metadata[key], value,
                "Expected {} to have changed during move".format(key))

        # Make sure that the developer thinks about whether a newly added metadata
        # column should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_metadata.keys(),
            initial_metadata.keys(),
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
    def test_move_mail_solrdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_solrdata = solr_data_for(self.mail_eml)
        self.remove_ignored_solrdata(initial_solrdata)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.subdossier2) as children:
                self.move_items((self.mail_eml, ),
                                source=self.dossier,
                                target=self.subdossier2)
                self.commit_solr()

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_solrdata = solr_data_for(moved)
        self.remove_ignored_solrdata(moved_solrdata)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = to_iso8601(self.MOVE_TIME).replace(".000Z", "Z")
        modified_solrdata = {
            '_version_': moved_solrdata['_version_'],
            'containing_subdossier': u'2015',
            'getObjPositionInParent': 0,
            'metadata': 'Client1 1.1 / 1.2 / 29',
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'path_depth': 7,
            'path_parent': moved.absolute_url_path(),
            'reference': 'Client1 1.1 / 1.2 / 29',
            'sortable_reference': 'client00000001 00000001.00000001 / 00000001.00000002 / 00000029',
        }

        unchanged_solrdata = [
            u'allowedRolesAndUsers',
            u'bumblebee_checksum',
            u'checked_out',
            u'containing_dossier',
            u'document_date',
            u'document_author',
            u'file_extension',
            u'filename',
            u'filesize',
            u'receipt_date',
            u'is_locked_by_copy_to_workspace',
        ]

        unchanged_solrdata += self.common_unchanged_solrdata

        # Make sure no key is in both lists of unchanged and modified data
        self.assertTrue(set(unchanged_solrdata).isdisjoint(modified_solrdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_solrdata = deepcopy(modified_solrdata)
        expected_solrdata.update({key: initial_solrdata[key] for key in unchanged_solrdata})

        # Make sure that the developer thinks about whether a newly added
        # solr index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_solrdata.keys(),
            initial_solrdata.keys(),
            msg="A new solr index was added, please add it to 'unchanged_solrdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_solrdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_solrdata.items():
            self.assertNotEqual(
                initial_solrdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_solrdata, moved_solrdata)

        # Make sure the solrdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            self.commit_solr()
            reindexed_moved_solrdata = solr_data_for(moved)
            self.remove_ignored_solrdata(reindexed_moved_solrdata)

        # Some index data is not up to date, but does not have to be
        # Other data should be up to date but is not.
        not_up_to_date = ['_version_']
        for key in not_up_to_date:
            self.assertNotEqual(moved_solrdata.pop(key),
                                reindexed_moved_solrdata.pop(key))

        self.assertDictEqual(moved_solrdata, reindexed_moved_solrdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_mail_indexdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_indexdata = self.get_catalog_indexdata(self.mail_eml)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.empty_dossier) as children:
                self.move_items((self.mail_eml, ),
                                source=self.dossier,
                                target=self.empty_dossier)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_indexdata = self.get_catalog_indexdata(moved)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = self.dateindex_value_from_datetime(self.MOVE_TIME)
        modified_indexdata = {
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'reference': 'Client1 1.1 / 4 / 29',
        }

        unchanged_indexdata = [
            'allowedRolesAndUsers',
            'is_subdossier',
        ]
        unchanged_indexdata += self.common_unchanged_indexdata

        # Make sure no index is in both lists of unchanged and modified indexdata
        self.assertTrue(set(unchanged_indexdata).isdisjoint(modified_indexdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_indexdata = deepcopy(modified_indexdata)
        expected_indexdata.update({key: initial_indexdata[key] for key in unchanged_indexdata})

        # Make sure that the developer thinks about whether a newly added
        # index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_indexdata.keys(),
            initial_indexdata.keys(),
            msg="A new index was added, please add it to 'unchanged_indexdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_indexdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_indexdata.items():
            self.assertNotEqual(
                initial_indexdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_indexdata, moved_indexdata)

        # Make sure the indexdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            reindexed_moved_indexdata = self.get_catalog_indexdata(moved)

        self.assertDictEqual(moved_indexdata, reindexed_moved_indexdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_dossier_metadata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_metadata = self.get_catalog_metadata(self.subsubdossier)

        with freeze(self.MOVE_TIME):
            ZOPE_MOVE_TIME = DateTime()

            with self.observe_children(self.empty_repofolder) as children:
                self.move_items((self.subsubdossier, ),
                                source=self.subdossier,
                                target=self.empty_repofolder)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_metadata = self.get_catalog_metadata(moved)

        # We expect some of the metadata to get modified during pasting
        modified_metadata = {
            'is_subdossier': False,
            'listCreators': (self.dossier_responsible.id, self.regular_user.id),
            'modified': ZOPE_MOVE_TIME,
            'reference': 'Client1 2 / 1',
        }

        unchanged_metadata = []
        unchanged_metadata += self.common_unchanged_metadata

        # Make sure no metadata key is in both lists of unchanged and modified metadata
        self.assertTrue(set(unchanged_metadata).isdisjoint(modified_metadata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_metadata = deepcopy(modified_metadata)
        expected_metadata.update({key: initial_metadata[key] for key in unchanged_metadata})

        # Make sure fields expected to change really did
        for key, value in modified_metadata.items():
            self.assertNotEqual(
                initial_metadata[key], value,
                "Expected {} to have changed during move".format(key))

        # Make sure that the developer thinks about whether a newly added metadata
        # column should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_metadata.keys(),
            initial_metadata.keys(),
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
    def test_move_dossier_solrdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_solrdata = solr_data_for(self.subsubdossier)
        self.remove_ignored_solrdata(initial_solrdata)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.empty_repofolder) as children:
                self.move_items((self.subsubdossier, ),
                                source=self.subdossier,
                                target=self.empty_repofolder)
                self.commit_solr()

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_solrdata = solr_data_for(moved)
        self.remove_ignored_solrdata(moved_solrdata)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = to_iso8601(self.MOVE_TIME).replace(".000Z", "Z")
        modified_solrdata = {
            '_version_': moved_solrdata['_version_'],
            'allowedRolesAndUsers': [
                u'Administrator',
                u'Contributor',
                u'Editor',
                u'LimitedAdmin',
                u'Manager',
                u'Reader',
                u'TaskResponsible',
                u'user:%s' % self.archivist.getId(),
                u'user:fa_users'],
            'containing_dossier': moved.Title(),
            'is_subdossier': False,
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'path_depth': 4,
            'path_parent': moved.absolute_url_path(),
            'reference': 'Client1 2 / 1',
            'sortable_reference': 'client00000001 00000002 / 00000001',
            'touched': paste_time_index,
        }

        unchanged_solrdata = [
            u'blocked_local_roles',
            u'containing_subdossier',
            u'has_sametype_children',
            u'start',
            u'Subject',
        ]
        unchanged_solrdata += self.common_unchanged_solrdata

        # Make sure no key is in both lists of unchanged and modified data
        self.assertTrue(set(unchanged_solrdata).isdisjoint(modified_solrdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_solrdata = deepcopy(modified_solrdata)
        expected_solrdata.update({key: initial_solrdata[key] for key in unchanged_solrdata})

        # Make sure that the developer thinks about whether a newly added
        # solr index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_solrdata.keys(),
            initial_solrdata.keys(),
            msg="A new solr index was added, please add it to 'unchanged_solrdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_solrdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_solrdata.items():
            self.assertNotEqual(
                initial_solrdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_solrdata, moved_solrdata)

        # Make sure the solrdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            self.commit_solr()
            reindexed_moved_solrdata = solr_data_for(moved)
        self.remove_ignored_solrdata(reindexed_moved_solrdata)

        # Some index data is not up to date, but does not have to be
        # Other data should be up to date but is not.
        not_up_to_date = ['_version_']
        for key in not_up_to_date:
            self.assertNotEqual(moved_solrdata.pop(key),
                                reindexed_moved_solrdata.pop(key))

        self.assertDictEqual(moved_solrdata, reindexed_moved_solrdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")

    @browsing
    def test_move_dossier_indexdata_update(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        initial_indexdata = self.get_catalog_indexdata(self.subsubdossier)

        with freeze(self.MOVE_TIME):
            with self.observe_children(self.empty_repofolder) as children:
                self.move_items((self.subsubdossier, ),
                                source=self.subdossier,
                                target=self.empty_repofolder)

        self.assertEqual(1, len(children['added']))
        moved = children['added'].pop()
        moved_indexdata = self.get_catalog_indexdata(moved)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = self.dateindex_value_from_datetime(self.MOVE_TIME)

        modified_indexdata = {
            'allowedRolesAndUsers': [
                u'Administrator',
                u'Contributor',
                u'Editor',
                u'LimitedAdmin',
                u'Manager',
                u'Reader',
                u'TaskResponsible',
                u'user:%s' % self.archivist.getId(),
                u'user:fa_users'],
            'is_subdossier': 0,
            'modified': paste_time_index,
            'path': moved.absolute_url_path(),
            'reference': 'Client1 2 / 1',
        }

        unchanged_indexdata = []
        unchanged_indexdata += self.common_unchanged_indexdata

        # Make sure no index is in both lists of unchanged and modified indexdata
        self.assertTrue(set(unchanged_indexdata).isdisjoint(modified_indexdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified indexdata")

        expected_indexdata = deepcopy(modified_indexdata)
        expected_indexdata.update({key: initial_indexdata[key] for key in unchanged_indexdata})

        # Make sure that the developer thinks about whether a newly added
        # index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_indexdata.keys(),
            initial_indexdata.keys(),
            msg="A new index was added, please add it to 'unchanged_indexdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_indexdata' otherwise")

        # Make sure fields expected to change really did
        for key, value in modified_indexdata.items():
            self.assertNotEqual(
                initial_indexdata[key], value,
                "Expected {} to have changed during move".format(key))

        self.assertDictEqual(expected_indexdata, moved_indexdata)

        # Make sure the indexdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.MOVE_TIME):
            moved.reindexObject()
            reindexed_moved_indexdata = self.get_catalog_indexdata(moved)

        self.assertDictEqual(moved_indexdata, reindexed_moved_indexdata,
                             msg="Some indexdata was not up to date after "
                                 "a move operation")


class TestContainingDossierAndSubdossierIndexWhenMovingItem(SolrIntegrationTestCase, MoveItemsHelper):

    def test_indexes_are_updated_when_document_moved_from_dossier_to_dossier(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.document)
        self.assert_solr_field_value('',
                                     'containing_subdossier', self.document)

        with self.observe_children(self.empty_dossier) as children:
            self.move_items([self.document],
                            source=self.dossier,
                            target=self.empty_dossier)
        self.commit_solr()

        document, = children.get('added')
        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', document)
        self.assert_solr_field_value('',
                                     'containing_subdossier', document)

    def test_indexes_are_updated_when_document_moved_from_subdossier_to_subdossier(self):
        self.login(self.regular_user)
        empty_subdossier = create(Builder("dossier").titled(u"destination").within(self.empty_dossier))

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdocument)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', self.subdocument)

        with self.observe_children(empty_subdossier) as children:
            self.move_items([self.subdocument],
                            source=self.subdossier,
                            target=empty_subdossier)
        self.commit_solr()

        document, = children.get('added')
        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', document)
        self.assert_solr_field_value(empty_subdossier.Title(),
                                     'containing_subdossier', document)

    def test_indexes_are_updated_when_document_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.meeting_dossier.Title(),
                                     'containing_dossier', self.meeting_document)
        self.assert_solr_field_value('',
                                     'containing_subdossier', self.meeting_document)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.meeting_document],
                            source=self.meeting_dossier,
                            target=self.subdossier)
        self.commit_solr()

        document, = children.get('added')
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', document)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', document)

    def test_indexes_are_updated_when_document_moved_from_subdossier_to_dossier(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdocument)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', self.subdocument)

        with self.observe_children(self.meeting_dossier) as children:
            self.move_items([self.subdocument],
                            source=self.subdossier,
                            target=self.meeting_dossier)
        self.commit_solr()

        document, = children.get('added')
        self.assert_solr_field_value('',
                                     'containing_subdossier', document)
        self.assert_solr_field_value(self.meeting_dossier.Title(),
                                     'containing_dossier', document)

    def test_indexes_are_updated_when_task_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.meeting_dossier.Title(),
                                     'containing_dossier', self.meeting_task)
        self.assert_solr_field_value('', 'containing_subdossier', self.meeting_task)

        self.assert_solr_field_value(self.meeting_dossier.Title(),
                                     'containing_dossier', self.meeting_subtask)
        self.assert_solr_field_value('', 'containing_subdossier', self.meeting_subtask)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.meeting_task],
                            source=self.meeting_dossier,
                            target=self.subdossier)
        self.commit_solr()

        task, = children.get('added')
        subtask = api.content.find(task, depth=1)[0].getObject()
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', task)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', task)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', subtask)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', subtask)

    def test_indexes_are_updated_when_mail_moved_from_dossier_to_subdossier(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.mail_eml)
        self.assert_solr_field_value('',
                                     'containing_subdossier', self.mail_eml)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.mail_eml],
                            source=self.dossier,
                            target=self.subdossier)
        self.commit_solr()

        mail, = children.get('added')
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', mail)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', mail)

    def test_indexes_are_updated_when_subdossier_is_moved_into_repofolder(self):
        self.login(self.regular_user)

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdocument)
        self.assert_solr_field_value(self.subdossier.Title(),
                                     'containing_subdossier', self.subdocument)

        self.assert_solr_field_value(1, 'is_subdossier', self.subdossier)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subdossier)

        self.assert_solr_field_value(1, 'is_subdossier', self.subsubdossier)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subsubdossier)

        with self.observe_children(self.empty_repofolder) as children:
            self.move_items([self.subdossier],
                            source=self.dossier,
                            target=self.empty_repofolder)
        self.commit_solr()

        dossier, = children.get('added')
        subdossier = dossier.get_subdossiers()[0].getObject()
        document = api.content.find(context=dossier,
                                    portal_type="opengever.document.document",
                                    depth=1)[0].getObject()
        self.commit_solr()

        self.assert_solr_field_value(0, 'is_subdossier', dossier)
        self.assert_solr_field_value(dossier.Title(),
                                     'containing_dossier', dossier)

        self.assert_solr_field_value(1, 'is_subdossier', subdossier)
        self.assert_solr_field_value(dossier.Title(),
                                     'containing_dossier', subdossier)

        self.assert_solr_field_value('', 'containing_subdossier', document)
        self.assert_solr_field_value(dossier.Title(),
                                     'containing_dossier', document)

    def test_indexes_are_updated_when_subsubdossier_is_moved_into_repofolder(self):
        self.login(self.regular_user)
        subsubdocument = create(Builder("document").titled(u"subsubdocument")
                                .within(self.subsubdossier))
        self.commit_solr()

        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', subsubdocument)
        self.assert_solr_field_value(self.subsubdossier.Title(),
                                     'containing_subdossier', subsubdocument)

        self.assert_solr_field_value(1, 'is_subdossier', self.subsubdossier)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', self.subsubdossier)

        with self.observe_children(self.empty_repofolder) as children:
            self.move_items([self.subsubdossier],
                            source=self.dossier,
                            target=self.empty_repofolder)

        dossier, = children.get('added')
        document = api.content.find(context=dossier,
                                    portal_type="opengever.document.document",
                                    depth=1)[0].getObject()
        self.commit_solr()

        self.assert_solr_field_value(0, 'is_subdossier', dossier)
        self.assert_solr_field_value(dossier.Title(),
                                     'containing_dossier', dossier)

        self.assert_solr_field_value('', 'containing_subdossier', document)
        self.assert_solr_field_value(dossier.Title(),
                                     'containing_dossier', document)

    def test_indexes_are_updated_when_dossier_is_moved_into_dossier(self):
        self.login(self.regular_user)
        document = create(Builder("document").titled(u"document").within(self.empty_dossier))
        self.commit_solr()

        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', document)
        self.assert_solr_field_value('', 'containing_subdossier', document)

        self.assert_solr_field_value(0, 'is_subdossier', self.empty_dossier)
        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', self.empty_dossier)

        with self.observe_children(self.dossier) as children:
            self.move_items([self.empty_dossier],
                            source=self.leaf_repofolder,
                            target=self.dossier)
        self.commit_solr()

        dossier, = children.get('added')
        document = api.content.find(context=dossier, depth=1)[0].getObject()

        self.assert_solr_field_value(1, 'is_subdossier', dossier)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', dossier)

        self.assert_solr_field_value(dossier.Title(),
                                     'containing_subdossier', document)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', document)

    def test_indexes_are_updated_when_dossier_is_moved_into_subsubdossier(self):
        self.login(self.regular_user)
        api.portal.set_registry_record(
            "opengever.dossier.interfaces.IDossierContainerTypes.maximum_dossier_depth", 2)
        document = create(Builder("document").titled(u"document").within(self.empty_dossier))
        self.commit_solr()

        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', document)
        self.assert_solr_field_value('',
                                     'containing_subdossier', document)

        self.assert_solr_field_value(0, 'is_subdossier', self.empty_dossier)
        self.assert_solr_field_value(self.empty_dossier.Title(),
                                     'containing_dossier', self.empty_dossier)

        with self.observe_children(self.subdossier) as children:
            self.move_items([self.empty_dossier],
                            source=self.leaf_repofolder,
                            target=self.subdossier)
        self.commit_solr()

        dossier, = children.get('added')
        document = api.content.find(context=dossier, depth=1)[0].getObject()

        self.assert_solr_field_value(1, 'is_subdossier', dossier)
        self.assert_solr_field_value(self.dossier.Title(),
                                     'containing_dossier', dossier)

        self.assert_solr_field_value(dossier.Title(),
                                     'containing_subdossier', document)
        self.assert_solr_field_value(self.dossier.Title(),
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

        browser.open(src, payload, view='move_items')

        if not browser.url.endswith('move_items'):
            # Might have been redirected because of an error
            return

        browser.fill({'Destination': target})
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_redirects_to_context_and_show_statusmessage_when_obj_cant_be_found(self, browser):
        self.login(self.regular_user, browser)
        self.move_items(
            browser, src=self.dossier,
            obj='/invalid/path', target=self.empty_dossier)

        self.assertEqual(self.dossier.absolute_url(), browser.url)
        self.assertEqual(
            "The selected objects can't be found, please try again.",
            error_messages()[0])

    @browsing
    def test_document_inside_a_task_is_not_movable(self, browser):
        self.login(self.regular_user, browser)
        self.move_items(
            browser, src=self.task,
            obj=self.taskdocument, target=self.empty_dossier)

        self.assertEqual(
            'Document {} is inside a task and therefore not movable. Please move the task instead.'.format(self.taskdocument.title),
            error_messages()[0])
        self.assertIn(self.taskdocument, self.task.objectValues())
        self.assertNotIn(self.taskdocument, self.empty_dossier.objectValues())

    @browsing
    def test_mail_inside_a_task_is_not_movable(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail').titled('Good news').within(self.task))
        self.move_items(browser, src=self.task, obj=mail, target=self.empty_dossier)

        self.assertEqual('Document {} is inside a task and therefore not movable. Please move the task'
                         ' instead.'.format(mail.title), error_messages()[0])
        self.assertIn(mail, self.task.objectValues())
        self.assertNotIn(mail, self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_a_proposal_is_not_movable(self, browser):
        self.login(self.regular_user, browser)
        self.activate_feature('meeting')
        self.move_items(
            browser, src=self.proposal,
            obj=self.proposaldocument, target=self.empty_dossier)

        self.assertEqual(
            'Document {} is inside a proposal and therefore not movable. Please move the proposal instead.'.format(self.proposaldocument.title),
            error_messages()[0])
        self.assertIn(self.proposaldocument, self.proposal.objectValues())
        self.assertNotIn(self.proposaldocument, self.empty_dossier.objectValues())

    @browsing
    def test_document_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager, browser)
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
        self.login(self.dossier_manager, browser)
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
        self.login(self.dossier_manager, browser)
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
        self.login(self.dossier_manager, browser)
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
        self.login(self.regular_user, browser)
        task_intid = getUtility(IIntIds).getId(self.subtask)
        self.move_items(
            browser, src=self.task,
            task=self.subtask, target=self.empty_dossier)
        subtask = getUtility(IIntIds).getObject(task_intid)
        self.assertIn(subtask, self.empty_dossier.objectValues())

    @browsing
    def test_move_items_within_templatefolder_is_possible(self, browser):
        self.login(self.administrator, browser)
        doc_intid = getUtility(IIntIds).getId(self.dossiertemplatedocument)

        self.move_items(browser, src=self.dossiertemplate,
                        obj=self.dossiertemplatedocument, target=self.subdossiertemplate)
        doc = getUtility(IIntIds).getObject(doc_intid)

        self.assertIn(doc, self.subdossiertemplate.objectValues())

    @browsing
    def test_cannot_move_template_document_to_template_dossier(self, browser):
        self.login(self.administrator, browser)

        self.move_items(browser, src=self.templates,
                        obj=self.normal_template, target=self.dossiertemplate)

        self.assertEqual(
            [u'Document T\xc3\xb6mpl\xc3\xb6te Normal is a template document '
             u'and hence cannot be moved into a template dossier.'],
            error_messages())
        self.assertIn(self.normal_template,
                      self.templates.objectValues())
        self.assertNotIn(self.normal_template,
                         self.dossiertemplate.objectValues())

    @browsing
    def test_cannot_move_document_from_dossiertemplate_to_template_folder(self, browser):
        self.login(self.administrator, browser)

        self.move_items(browser, src=self.dossiertemplate,
                        obj=self.dossiertemplatedocument, target=self.templates)
        self.assertEqual(
            [u'Document Werkst\xe4tte is in a dossier template and hence '
             u'cannot be made into a template document.'],
            error_messages())
        self.assertIn(self.dossiertemplatedocument,
                      self.dossiertemplate.objectValues())
        self.assertNotIn(self.dossiertemplatedocument,
                         self.templates.objectValues())

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
        self.assertEquals('Reference number: Client1 1.1 / 4',
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
        self.assertEquals('Reference number: Client1 1.1 / 4',
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
        self.assertEquals('Reference number: Client1 1.1 / 4',
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

        self.assertEquals('Reference number: Client1 2 / 1',
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
        self.assertEquals('Reference number: Client1 1.1 / 4',
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
            [u'1. F\xfchrung', u'2. Rechnungspr\xfcfungskommission', 'drittes-repo'],
            selectables)


class TestReferenceNumberUpdateOnMove(IntegrationTestCase):

    @browsing
    def test_dossier_and_subdossier_reference_number_is_up_to_date(self, browser):
        self.login(self.dossier_responsible, browser)

        catalog = api.portal.get_tool('portal_catalog')
        api.content.move(source=self.dossier,target=self.empty_repofolder)

        dossier = self.empty_repofolder.listFolderContents()[0]
        brains = catalog(path='/'.join(dossier.getPhysicalPath()),
                         portal_type='opengever.dossier.businesscasedossier')

        self.assertItemsEqual(
            ['Client1 2 / 1',
             'Client1 2 / 1.1',
             'Client1 2 / 1.2',
             'Client1 2 / 1.1.1'],
            [brain.reference for brain in brains])


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
        self.assertEqual('/plone/ordnungssystem/fuhrung|1. F\xc3\xbchrung', browser.contents)

        browser.open(u'?'.join((autocomplete_url, u'q="{}"'.format(self.leaf_repofolder.title_or_id().replace("-", " ")))))
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen|1.1. Vertr\xc3\xa4ge und Vereinbarungen',
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

        browser.open(u'?'.join((autocomplete_url, u'q="{}"'.format(self.dossier.title_or_id()))))
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

        browser.open(u'?'.join((autocomplete_url, u'q="{}"'.format(self.inactive_dossier.title_or_id()))))
        self.assertEqual('', browser.contents)

        browser.open(u'?'.join((autocomplete_url, u'q="{}"'.format(self.expired_dossier.title_or_id()))))
        self.assertEqual('', browser.contents)


class TestMoveItem(IntegrationTestCase):

    def move_item(self, browser, src, target):
        browser.open(src, view='move_item')
        browser.fill({'Destination': target})
        browser.css('#form-buttons-button_submit').first.click()

    @browsing
    def test_move_document(self, browser):
        self.login(self.regular_user, browser)
        doc_title = self.document.title.encode('utf-8')
        self.assertIn(doc_title, [a.Title for a in self.dossier.getFolderContents()])

        self.move_item(browser, self.document, self.empty_dossier)
        self.assertIn(doc_title, [a.Title for a in self.empty_dossier.getFolderContents()])
        self.assertNotIn(doc_title, [a.Title for a in self.dossier.getFolderContents()])
        assert_message(u'{} was moved.'.format(doc_title.decode('utf-8')))

    @browsing
    def test_move_task(self, browser):
        self.login(self.regular_user, browser)
        task_title = self.task.title.encode('utf-8')
        self.assertIn(task_title, [a.Title for a in self.dossier.getFolderContents()])

        self.move_item(browser, self.task, self.empty_dossier)
        self.assertIn(task_title, [a.Title for a in self.empty_dossier.getFolderContents()])
        self.assertNotIn(task_title, [a.Title for a in self.dossier.getFolderContents()])
        assert_message(u'{} was moved.'.format(task_title.decode('utf-8')))

    @browsing
    def test_checked_out_document_is_not_movable(self, browser):
        self.login(self.regular_user, browser)
        self.checkout_document(self.document)
        doc_title = self.document.title.encode('utf-8')
        self.assertIn(doc_title, [a.Title for a in self.dossier.getFolderContents()])
        self.move_item(browser, self.document, self.empty_dossier)
        self.assertIn(doc_title, [a.Title for a in self.dossier.getFolderContents()])
        self.assertNotIn(doc_title, [a.Title for a in self.empty_dossier.getFolderContents()])
        assert_message(u'Failed to move {}.'.format(doc_title.decode('utf-8')))

    @browsing
    def test_move_document_in_templates(self, browser):
        self.login(self.administrator, browser)
        doc_title = self.dossiertemplatedocument.title.encode('utf-8')
        self.assertIn(doc_title, [a.Title for a in self.dossiertemplate.getFolderContents()])
        self.move_item(browser, self.dossiertemplatedocument, self.subdossiertemplate)
        self.assertIn(doc_title, [a.Title for a in self.subdossiertemplate.getFolderContents()])
        self.assertNotIn(doc_title, [a.Title for a in self.dossiertemplate.getFolderContents()])
        assert_message(u'{} was moved.'.format(doc_title.decode('utf-8')))


class TestDossierMovabilityChecker(IntegrationTestCase):

    def test_dossier_structure_depth(self):
        self.login(self.manager)
        self.assertEqual(3, DossierMovabiliyChecker(
            self.dossier).dossier_structure_depth())
        self.assertEqual(2, DossierMovabiliyChecker(
            self.subdossier).dossier_structure_depth())
        self.assertEqual(1, DossierMovabiliyChecker(
            self.subsubdossier).dossier_structure_depth())

    def test_raises_when_dossier_depth_would_be_exceeded(self):
        self.login(self.manager)

        # Only one subdossier level allowed.
        self.assertEqual(1, api.portal.get_registry_record(
            name='maximum_dossier_depth',
            interface=IDossierContainerTypes
            ))

        # empty_dossier can only be moved to main dossier, or a dossier that
        # already contains a subdossier on the same level
        with self.assertRaises(Forbidden):
            DossierMovabiliyChecker(self.empty_dossier).validate_movement(
                self.subsubdossier)

        # Allowed even though this will exceed the max nesting depth, because
        # self.subsubdossier already exists on the same level
        DossierMovabiliyChecker(self.empty_dossier).validate_movement(
            self.subdossier)

        DossierMovabiliyChecker(self.empty_dossier).validate_movement(
            self.dossier)

        # self.subdossier contains a subsubdossier, hence cannot be moved into
        # a dossier
        with self.assertRaises(Forbidden):
            DossierMovabiliyChecker(self.subdossier).validate_movement(
                self.empty_dossier)

        DossierMovabiliyChecker(self.subsubdossier).validate_movement(
            self.empty_dossier)

        # a dossier containing a subdossier can even be moved to a place
        # where it would exceed the max nesting depth by 2, if another
        # subdossier in this main dossier already violates the max nesting
        # depth by 2.
        DossierMovabiliyChecker(self.resolvable_dossier).validate_movement(
            self.dossier)

        # two subdossier levels allowed.
        api.portal.set_registry_record(
            name='maximum_dossier_depth',
            value=2,
            interface=IDossierContainerTypes
            )

        # empty_dossier can be moved to a subdossier but not to a subsubdossier
        with self.assertRaises(Forbidden):
            DossierMovabiliyChecker(self.empty_dossier).validate_movement(
                self.subsubdossier)

        DossierMovabiliyChecker(self.empty_dossier).validate_movement(
            self.subdossier)

        # a dossier containing a subdossier can be moved into a main dossier
        DossierMovabiliyChecker(self.subdossier).validate_movement(
            self.empty_dossier)


class TestDossierTemplateMovabilityChecker(IntegrationTestCase):

    def test_raises_when_dossiertemplate_depth_would_be_exceeded_and_flag_enabled(self):
        self.login(self.administrator)

        empty_dossiertemplate = create(Builder('dossiertemplate')
                                       .within(self.templates))

        subsubdossiertemplate = create(Builder('dossiertemplate')
                                       .within(self.subdossiertemplate))

        api.portal.set_registry_record('respect_max_depth', True,
                                       interface=IDossierTemplateSettings)

        # Two subdossier level allowed
        api.portal.set_registry_record(name='maximum_dossier_depth', value=2,
                                       interface=IDossierContainerTypes)

        # Cannot move self.dossiertemplate into empty_dossiertemplate
        with self.assertRaises(Forbidden):
            DossierTemplateMovabilityChecker(self.dossiertemplate).validate_movement(
                empty_dossiertemplate)

        DossierTemplateMovabilityChecker(self.subdossiertemplate).validate_movement(
            empty_dossiertemplate)

        # Cannot move empty_dossiertemplate into subsubdossiertemplate
        with self.assertRaises(Forbidden):
            DossierTemplateMovabilityChecker(empty_dossiertemplate).validate_movement(
                subsubdossiertemplate)

        DossierTemplateMovabilityChecker(empty_dossiertemplate).validate_movement(
            self.subdossiertemplate)

        api.portal.set_registry_record('respect_max_depth', False,
                                       interface=IDossierTemplateSettings)

        # Can move self.dossiertemplate into empty_dossiertemplate
        DossierTemplateMovabilityChecker(self.dossiertemplate).validate_movement(
            empty_dossiertemplate)
        # Can move empty_dossiertemplate into subsubdossiertemplate
        DossierTemplateMovabilityChecker(empty_dossiertemplate).validate_movement(
            subsubdossiertemplate)
