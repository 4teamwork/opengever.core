from DateTime import DateTime
from datetime import datetime
from ftw.testing import freeze
from opengever.base.archeologist import Archeologist
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from plone import api
from plone.namedfile.file import NamedBlobFile
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter


class TestCMFEditionsModifiers(IntegrationTestCase):

    JOURNAL_KEY = 'ftw.journal.journal_entries_annotations_key'

    def create_version(self, document):
        manager = getMultiAdapter(
            (self.document, self.portal.REQUEST), ICheckinCheckoutManager)
        manager.checkout()

        self.document.file = NamedBlobFile(
            data='New content', filename=u'test.txt')

        manager.checkin()

    def test_ftw_journal_is_not_versioned(self):
        self.login(self.regular_user)

        self.create_version(self.document)

        versioner = Versioner(self.document)
        shadow_history = versioner.get_history_metadata()
        self.assertEquals(2, len(shadow_history))

        for version_number in range(len(shadow_history)):
            historic_obj = versioner.retrieve(version_number)
            historic_annotations = IAnnotations(historic_obj)
            self.assertNotIn(self.JOURNAL_KEY, historic_annotations)

    def test_ftw_journal_is_not_versioned_archeologist(self):
        """This test confirms that the Archeologist's view of the historic
        annotations is consistent with CMFEdition's APIs.
        """
        self.login(self.regular_user)

        self.create_version(self.document)

        repo_tool = api.portal.get_tool('portal_repository')
        shadow_history = repo_tool.getHistoryMetadata(self.document)
        self.assertEquals(2, len(shadow_history))

        for version_number in range(len(shadow_history)):
            archeologist = Archeologist(
                self.document, repo_tool.retrieve(
                    self.document, selector=version_number))

            archived_obj = archeologist.excavate()
            archived_ann = IAnnotations(archived_obj)
            self.assertNotIn(self.JOURNAL_KEY, archived_ann)

    def test_ftw_journal_still_present_on_working_copy(self):
        self.login(self.regular_user)

        self.create_version(self.document)

        versioner = Versioner(self.document)
        shadow_history = versioner.get_history_metadata()
        self.assertEquals(2, len(shadow_history))

        ann = IAnnotations(self.document)
        self.assertIn(self.JOURNAL_KEY, ann)
        self.assertEqual(3, len(ann[self.JOURNAL_KEY]))

    def test_ftw_journal_doesnt_get_purged_on_revert(self):
        self.login(self.regular_user)

        self.create_version(self.document)

        previous_journal = list(IAnnotations(self.document)[self.JOURNAL_KEY])
        self.assertEqual(3, len(previous_journal))

        manager = getMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)

        with freeze(datetime(2015, 01, 28, 12, 00)):
            manager.revert_to_version(1)

        journal = list(IAnnotations(self.document)[self.JOURNAL_KEY])
        self.assertEqual(4, len(journal))

        self.assertEqual(previous_journal, journal[:3])

        expected_entry = {'action': {
            'visible': True,
            'type': 'Reverted document file',
            'title': u'label_document_file_reverted'},
            'comments': '',
            'actor': 'kathi.barfuss',
            'time': DateTime('2015/01/28 12:00:00 GMT+1')}
        self.assertEqual(expected_entry, journal[-1])
