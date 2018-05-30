from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestSyncExcerpt(IntegrationTestCase):

    features = ('meeting',)

    def setUp(self):
        super(TestSyncExcerpt, self).setUp()

        # XXX OMG - this should be in the fixture somehow, or at least be
        # build-able in fewer lines.
        self.login(self.committee_responsible)

        self.document_in_dossier = self.document
        self.excerpt_in_dossier = create(
            Builder('generated_excerpt')
            .for_document(self.document_in_dossier))
        self.submitted_proposal.load_model().excerpt_document = self.excerpt_in_dossier

        self.document_in_proposal = create(
            Builder('document')
            .with_dummy_content()
            .within(self.submitted_proposal))
        self.excerpt_in_proposal = create(
            Builder('generated_excerpt')
            .for_document(self.document_in_proposal))
        self.submitted_proposal.load_model().submitted_excerpt_document = self.excerpt_in_proposal

    def test_updates_excerpt_in_dossier_after_checkin(self):
        self.assertEqual(None, self.document_in_proposal.get_current_version_id())
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        manager = getMultiAdapter((self.document_in_proposal,
                                   self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.document_in_proposal.update_file(
            'foo bar',
            content_type='text/plain',
            filename=u'example.docx')
        manager.checkin()

        self.assertEqual(1, self.document_in_proposal.get_current_version_id())
        self.assertEqual(1, self.document_in_dossier.get_current_version_id())

    def test_updates_excerpt_in_dossier_after_revert(self):
        self.assertEqual(None, self.document_in_proposal.get_current_version_id())
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        manager = getMultiAdapter((self.document_in_proposal,
                                   self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.document_in_proposal.update_file(
            'foo bar',
            content_type='text/plain',
            filename=u'example.docx')
        manager.checkin()

        manager.revert_to_version(0)
        self.assertEqual(2, self.document_in_proposal.get_current_version_id())
        self.assertEqual(2, self.document_in_dossier.get_current_version_id())

    def test_updates_excerpt_in_dossier_after_modification(self):
        self.assertEqual(None, self.document_in_dossier.get_current_version_id())
        self.document_in_proposal.update_file(
            'foo bar',
            filename=u'example.docx',
            content_type='text/plain')
        notify(ObjectModifiedEvent(self.document_in_proposal))

        self.assertEqual(1, self.document_in_dossier.get_current_version_id())
