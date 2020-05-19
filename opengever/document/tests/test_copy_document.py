from copy import deepcopy
from datetime import datetime
from DateTime import DateTime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from OFS.CopySupport import CopyError
from opengever.testing import IntegrationTestCase
from plone import api
from tzlocal import get_localzone
import pytz


class TestCopyDocuments(IntegrationTestCase):

    COPY_TIME = datetime(2018, 4, 28, 0, 0, tzinfo=pytz.UTC)
    PASTE_TIME = datetime(2018, 4, 30, 0, 0, tzinfo=pytz.UTC)

    def test_copying_a_document_prefixes_title_with_copy_of(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.document, target=self.subdossier)
        self.assertEqual(u'copy of Vertr\xe4gsentwurf', copy.title)

    def test_copying_a_mail_prefixes_title_with_copy_of(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.mail_eml, target=self.subdossier)
        self.assertEqual(u'copy of Die B\xfcrgschaft', copy.title)

    def test_copying_a_mail_does_not_create_versions(self):
        self.login(self.regular_user)
        copy = api.content.copy(source=self.mail_eml, target=self.subdossier)
        new_history = self.portal.portal_repository.getHistory(copy)
        self.assertEqual(len(new_history), 0)

    def test_copying_a_document_does_not_copy_its_versions(self):
        self.login(self.regular_user)

        # Check the original actually has a history
        old_history = self.portal.portal_repository.getHistory(self.document)
        self.assertEqual(len(old_history), 0)
        self.checkout_document(self.document)
        self.checkin_document(self.document)
        old_history = self.portal.portal_repository.getHistory(self.document)
        self.assertEqual(len(old_history), 1)

        cb = self.dossier.manage_copyObjects(self.document.id)
        self.dossier.manage_pasteObjects(cb)
        new_doc = self.dossier['copy_of_document-14']
        new_history = self.portal.portal_repository.getHistory(new_doc)
        self.assertEqual(len(new_history), 0)

    def test_copying_a_checked_out_document_is_forbidden(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        with self.assertRaises(CopyError):
            api.content.copy(source=self.document, target=self.subdossier)

    @browsing
    def test_document_copy_metadata(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        with freeze(self.COPY_TIME):
            data = self.make_path_param(self.subdocument)
            browser.open(self.empty_dossier, view="copy_items", data=data)

        with freeze(self.PASTE_TIME):
            ZOPE_PASTE_TIME = DateTime()

            with self.observe_children(self.empty_dossier) as children:
                browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(1, len(children['added']))
        copy = children['added'].pop()

        original_metadata = self.get_catalog_metadata(self.subdocument)
        copy_metadata = self.get_catalog_metadata(copy)

        ZOPE_PASTE_TIME_STR = ZOPE_PASTE_TIME.toZone(DateTime().localZone()).ISO()

        # We expect some of the metadata to get modified during pasting
        modified_metadata = {'UID': copy.UID(),
                             # sequence numbers and such
                             'sequence_number': 41,
                             'id': 'document-41',
                             'getId': 'document-41',
                             'reference': 'Client1 1.1 / 4 / 41',
                             # creator
                             'listCreators': (self.regular_user.id,),
                             'Creator': self.regular_user.id,
                             # dates
                             'created': ZOPE_PASTE_TIME,
                             'start': self.PASTE_TIME.date(),
                             'modified': ZOPE_PASTE_TIME,
                             'Date': ZOPE_PASTE_TIME_STR,
                             'changed': self.PASTE_TIME,
                             # containing dossier and subdossier
                             'containing_dossier': self.empty_dossier.Title(),
                             'containing_subdossier': '',
                             # title and filename
                             'Title': 'copy of {}'.format(self.subdocument.Title()),
                             'filename': u'copy of {}'.format(self.subdocument.get_filename())}

        unchanged_metadata = ['Description',
                              'ExpirationDate',
                              'Subject', 'Type',
                              'bumblebee_checksum',
                              'checked_out',
                              'cmf_uid',
                              'contactid',
                              'css_icon_class',
                              'date_of_completion',
                              'deadline',
                              'delivery_date',
                              'document_author',
                              'document_date',
                              'email',
                              'email2',
                              'end',
                              'exclude_from_nav',
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
                              'is_subdossier',
                              'is_subtask',
                              'issuer',
                              'lastname',
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
                              'trashed']

        # Make sure no metadata key is in both lists of unchanged and modified metadata
        self.assertTrue(set(unchanged_metadata).isdisjoint(modified_metadata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_metadata = deepcopy(modified_metadata)
        expected_metadata.update({key: original_metadata[key] for key in unchanged_metadata})

        # Make sure that the developer thinks about whether a newly added metadata
        # column should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_metadata.keys(),
            original_metadata.keys(),
            msg="A new metadata column was added, please add it to "
                "'unchanged_metadata' if it should not be modified during "
                "copy/paste of a document, or to 'modified_metadata' otherwise")

        self.assertDictEqual(expected_metadata, copy_metadata)

        # Make sure the metadata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.PASTE_TIME):
            copy.reindexObject()
        reindexed_copy_metadata = self.get_catalog_metadata(copy)

        # Everything is up to date
        self.assertDictEqual(copy_metadata, reindexed_copy_metadata,
                             msg="Some metadata was not up to date after "
                                 "a copy/paste operation")

    @browsing
    def test_document_copy_indexdata(self, browser):
        self.maxDiff = None
        self.login(self.regular_user, browser=browser)

        with freeze(self.COPY_TIME):
            data = self.make_path_param(self.subdocument)
            browser.open(self.empty_dossier, view="copy_items", data=data)

        with freeze(self.PASTE_TIME):
            with self.observe_children(self.empty_dossier) as children:
                browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(1, len(children['added']))
        copy = children['added'].pop()

        original_indexdata = self.get_catalog_indexdata(self.subdocument)
        copy_indexdata = self.get_catalog_indexdata(copy)

        # We expect some of the metadata to get modified during pasting
        paste_time_index = self.dateindex_value_from_datetime(self.PASTE_TIME)
        modified_indexdata = {
            'UID': copy.UID(),
            'path': copy.absolute_url_path(),

            # sequence numbers and such
            'id': 'document-41',
            'getId': 'document-41',
            'reference': 'Client1 1.1 / 4 / 41',
            'sequence_number': 41,

            # creator
            'Creator': self.regular_user.id,

            # title and serchable text
            'Title': ['copy', 'of', 'ubersicht', 'der', 'vertrage', 'von', u'2016'],
            'sortable_title': 'copy of ubersicht der vertrage von 2016',
            'SearchableText': ['copy', 'of', 'ubersicht', 'der', 'vertrage',
                               'von', u'2016', 'client1', u'1', u'1', u'4',
                               u'41', u'41', 'wichtig', 'subkeyword'],

            # dates
            'changed': paste_time_index,
            'modified': paste_time_index,
            'start': paste_time_index,
            'created': paste_time_index,
            'Date': paste_time_index,

            # containing dossier and subdossier
            'containing_dossier': self.empty_dossier.Title(),
            'containing_subdossier': '',
            'is_subdossier': 0,  # acquisition is responsible here
        }

        unchanged_indexdata = ['Description',
                               'Subject',
                               'Type',
                               'after_resolve_jobs_pending',
                               'allowedRolesAndUsers',
                               'blocked_local_roles',
                               'checked_out',
                               'cmf_uid',
                               'contactid',
                               'date_of_completion',
                               'deadline',
                               'delivery_date',
                               'document_author',
                               'document_date',
                               'document_type',
                               'effectiveRange',
                               'email',
                               'end',
                               'external_reference',
                               'file_extension',
                               'filesize',
                               'firstname',
                               'getObjPositionInParent',
                               'is_default_page',
                               'is_folderish',
                               'is_subtask',
                               'issuer',
                               'lastname',
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
                               'trashed']

        # Make sure no index is in both lists of unchanged and modified indexdata
        self.assertTrue(set(unchanged_indexdata).isdisjoint(modified_indexdata.keys()),
                        msg="Make sure no key is in both lists of "
                            "unchanged and modified metadata")

        expected_indexdata = deepcopy(modified_indexdata)
        expected_indexdata.update({key: original_indexdata[key] for key in unchanged_indexdata})

        # Make sure that the developer thinks about whether a newly added
        # index should be modified during copy/paste of a document or not.
        self.assertItemsEqual(
            expected_indexdata.keys(),
            original_indexdata.keys(),
            msg="A new index was added, please add it to 'unchanged_indexdata'"
                " if it should not be modified during copy/paste "
                "of a document, or to 'modified_indexdata' otherwise")

        self.assertDictEqual(expected_indexdata, copy_indexdata)

        # Make sure the indexdata was up to date
        # we freeze to the paste time to avoid seeing differences in dates
        # that get modified by indexing (such as modified)
        with freeze(self.PASTE_TIME):
            copy.reindexObject()
        reindexed_copy_indexdata = self.get_catalog_indexdata(copy)

        # Everything is up to date
        self.assertDictEqual(copy_indexdata, reindexed_copy_indexdata,
                             msg="Some indexdata was not up to date after "
                                 "a copy/paste operation")
