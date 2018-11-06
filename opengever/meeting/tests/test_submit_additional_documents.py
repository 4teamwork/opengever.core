from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.base.transport import Transporter
from opengever.meeting.exceptions import NoSubmittedDocument
from opengever.meeting.model import SubmittedDocument
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
from plone.namedfile.file import NamedBlobFile


class TestSubmitAdditionalDocumentsIntegration(IntegrationTestCase):

    features = (
        'meeting',
    )

    @browsing
    def test_update_existing_document_without_permission_on_committee_is_possible(self, browser):
        self.login(self.dossier_responsible, browser)
        self.document.file = NamedBlobFile(data='New', filename=u'test.docx')
        api.portal.get_tool('portal_repository').save(self.document)
        browser.open(self.proposal, view='tabbedview_view-overview')
        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()
        expected_messages = [u'A new submitted version of document Vertr\xe4gsentwurf has been created.']
        self.assertSequenceEqual(expected_messages, info_messages())

    @browsing
    def test_do_not_show_link_to_update_outdated_document_on_submitted_proposal_view(self, browser):
        self.login(self.meeting_user, browser)
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        api.portal.get_tool('portal_repository').save(self.document)
        browser.open(self.proposal, view='tabbedview_view-overview')
        self.assertEqual(
            ['Update document in proposal'],
            browser.css('a.proposal-outdated').text,
            'The outdated link should be visible on a proposal',
        )
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertEqual(
            [u'Vertr\xe4ge', u'Vertr\xe4gsentwurf'],
            browser.css('.document_link').text,
            'Attachment and proposal document should be available in the submittedproposal listing',
        )
        self.assertEqual(
            [],
            browser.css('a.proposal-outdated'),
            'The outdated link should not be visible on a submitted proposal',
        )

    def test_cannot_submit_new_document_versions_outside_proposals(self):
        self.login(self.regular_user)
        url_tool = api.portal.get_tool(name="portal_url")
        physical_path = '/'.join(url_tool.getRelativeContentPath(self.document))
        with self.assertRaises(NoSubmittedDocument):
            Transporter().transport_to(
                self.document,
                get_current_admin_unit().id(),
                physical_path,
                view='update-submitted-document',
            )

    def test_database_entry_is_deleted_when_removing_submitted_proposal(self):
        self.login(self.manager)
        submitted_document = self.submitted_proposal.get_documents()[0]
        self.assertIsNotNone(SubmittedDocument.query.get_by_target(submitted_document))
        # Submitted proposals are locked with an unstealable lock
        ILockable(submitted_document).clear_locks()
        api.content.delete(submitted_document)
        self.assertIsNone(SubmittedDocument.query.get_by_target(submitted_document))

    def test_database_entry_is_deleted_when_removing_proposal(self):
        self.login(self.manager)
        oguid = Oguid.for_object(self.document)
        self.assertIsNotNone(SubmittedDocument.query.get_by_source(self.proposal, self.document))
        api.content.delete(self.document)
        proposal_model = self.proposal.load_model()
        self.assertIsNone(
            SubmittedDocument.query
            .filter(SubmittedDocument.oguid == oguid)
            .filter(SubmittedDocument.proposal == proposal_model)
            .first(),
        )

    @browsing
    def test_submit_new_document_to_proposal_on_document_view(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.subdocument)
        browser.find('Submit additional document').click()
        browser.fill({'Proposal': self.proposal})
        browser.find('Submit Attachments').click()
        self.assertSubmittedDocumentCreated(self.proposal, self.subdocument)
        self.assertEqual(
            [u'Additional document \xdcbersicht der Vertr\xe4ge von 2016 has been submitted successfully.'],
            info_messages(),
        )

    @browsing
    def test_submit_new_document_to_proposal_on_proposal_view(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.subdocument})
        browser.find('Submit Attachments').click()
        self.assertSubmittedDocumentCreated(self.proposal, self.subdocument)
        self.assertEqual(
            [u'Additional document \xdcbersicht der Vertr\xe4ge von 2016 has been submitted successfully.'],
            info_messages(),
        )

    @browsing
    def test_update_existing_document_version_on_proposal_view(self, browser):
        self.login(self.meeting_user, browser)
        # create some new document versions
        repository = api.portal.get_tool('portal_repository')
        self.subdocument.file = NamedBlobFile(data='New', filename=u'test.txt')
        repository.save(self.subdocument)
        repository.save(self.subdocument)
        browser.open(self.proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.subdocument})
        browser.find('Submit Attachments').click()
        self.assertSubmittedDocumentCreated(self.proposal, self.subdocument, submitted_version=2)
        self.assertEqual(
            [u'Additional document \xdcbersicht der Vertr\xe4ge von 2016 has been submitted successfully.'],
            info_messages(),
        )

    @browsing
    def test_preselecting_document_if_url_in_request(self, browser):
        self.login(self.meeting_user, browser)
        document_path = '/'.join(self.subdocument.getPhysicalPath())
        browser.open(self.proposal, view="submit_additional_documents?document_path={}".format(document_path))
        browser.find('Submit Attachments').click()
        self.assertSubmittedDocumentCreated(self.proposal, self.subdocument)
        self.assertEqual(
            [u'Additional document \xdcbersicht der Vertr\xe4ge von 2016 has been submitted successfully.'],
            info_messages(),
        )

    @browsing
    def test_update_existing_document_version_by_clicking_on_update_link(self, browser):
        self.login(self.meeting_user, browser)
        self.document.file = NamedBlobFile(data='New', filename=u'test.txt')
        api.portal.get_tool('portal_repository').save(self.document)
        browser.open(self.proposal, view='tabbedview_view-overview')
        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()
        self.assertEqual(
            [u'A new submitted version of document Vertr\xe4gsentwurf has been created.'],
            info_messages(),
        )

    @browsing
    def test_do_not_show_link_if_document_is_not_outdated(self, browser):
        self.login(self.meeting_user, browser)
        browser.open(self.proposal, view='tabbedview_view-overview')
        self.assertIsNone(browser.find('Update document in proposal'))

    @browsing
    def test_submit_new_document_to_proposal_without_permission_on_committee_is_possible(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.subdocument)
        browser.find('Submit additional document').click()
        browser.fill({'Proposal': self.proposal})
        browser.find('Submit Attachments').click()
        with self.login(self.meeting_user):
            self.assertSubmittedDocumentCreated(self.proposal, self.subdocument)
        self.assertEqual(
            [u'Additional document \xdcbersicht der Vertr\xe4ge von 2016 has been submitted successfully.'],
            info_messages(),
        )
