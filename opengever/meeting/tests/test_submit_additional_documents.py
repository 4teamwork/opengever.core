from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.transport import Transporter
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.exceptions import NoSubmittedDocument
from opengever.meeting.model import SubmittedDocument
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestSubmitAdditionalDocuments(FunctionalTestCase):
    """Functional tests to make sure submitting additional documents for
    proposals works as expected.

    """
    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestSubmitAdditionalDocuments, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.committee = create(Builder('committee').titled('My committee'))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .titled(u'A Document')
                               .with_dummy_content())

    def setup_proposal(self, attach_document=False):
        builder = (
            Builder('proposal')
            .within(self.dossier)
            .titled(u'My Proposal')
            .having(committee=self.committee.load_model())
            .as_submitted())
        if attach_document:
            builder = builder.relate_to(self.document)

        proposal = create(builder)
        self.assertTrue(proposal.is_submit_additional_documents_allowed())
        transaction.commit()
        return proposal

    def login_as_user_without_committee_permission(self, browser):
        create(Builder('user').named('Hugo', 'Boss'))
        api.user.grant_roles(username=u'hugo.boss',
                             obj=self.dossier,
                             roles=['Contributor', 'Editor', 'Reader'])
        transaction.commit()
        browser.login(username='hugo.boss')
        with browser.expect_unauthorized():
            browser.open(self.committee)

    def test_cannot_submit_new_document_versions_outside_proposals(self):
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'Another Document')
                          .with_dummy_content())

        url_tool = api.portal.get_tool(name="portal_url")
        physical_path = '/'.join(url_tool.getRelativeContentPath(document))

        with self.assertRaises(NoSubmittedDocument):
            Transporter().transport_to(
                self.document,
                get_current_admin_unit().id(),
                physical_path,
                view='update-submitted-document')

    def test_database_entry_is_deleted_when_removing_submitted_proposal(self):
        self.grant('Manager')
        proposal, submitted_proposal = create(Builder('proposal')
            .within(self.dossier)
            .having(title='Mach doch',
                    committee=self.committee.load_model())
            .relate_to(self.document)
            .with_submitted())
        submitted_document = submitted_proposal.get_documents()[0]

        self.assertIsNotNone(
            SubmittedDocument.query.get_by_target(submitted_document))

        api.content.delete(submitted_proposal)

        self.assertIsNone(
            SubmittedDocument.query.get_by_target(submitted_document))

    def test_database_entry_is_deleted_when_removing_proposal(self):
        self.grant('Manager')
        proposal, submitted_proposal = create(Builder('proposal')
            .within(self.dossier)
            .having(title='Mach doch',
                    committee=self.committee.load_model())
            .relate_to(self.document)
            .with_submitted())

        self.assertIsNotNone(
            SubmittedDocument.query.get_by_source(proposal, self.document))

        api.content.delete(self.document)

        self.assertIsNone(
            SubmittedDocument.query.get_by_source(proposal, self.document))

    @browsing
    def test_submit_new_document_to_proposal_on_document_view(self, browser):
        proposal = self.setup_proposal()

        browser.login().visit(self.document)
        browser.find('Submit additional document').click()
        browser.fill({'Proposal': proposal})
        browser.find('Submit Attachments').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully.'],
            info_messages())

    @browsing
    def test_submit_new_document_to_proposal_on_proposal_view(self, browser):
        proposal = self.setup_proposal()

        browser.login().visit(proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.document})
        browser.find('Submit Attachments').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully.'],
            info_messages())

    @browsing
    def test_update_existing_document_version_on_proposal_view(self, browser):
        proposal = self.setup_proposal(attach_document=True)

        # create some new document versions
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        repository.save(self.document)
        transaction.commit()

        browser.login().visit(proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Attachments': self.document})
        browser.find('Submit Attachments').click()

        self.assertSubmittedDocumentCreated(
            proposal, self.document, submitted_version=2)
        self.assertSequenceEqual(
            ['A new submitted version of document A Document has been created.'],
            info_messages())

    @browsing
    def test_preselecting_document_if_url_in_request(self, browser):
        proposal = self.setup_proposal()
        document_path = '/'.join(self.document.getPhysicalPath())

        browser.login().visit(
            proposal,
            view="submit_additional_documents?document_path={}".format(document_path))

        browser.find('Submit Attachments').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully.'],
            info_messages(),
            "The document was preselected by the request parameter and should "
            "have been updated without selecting it again.")

    @browsing
    def test_update_existing_document_version_by_clicking_on_update_link(self, browser):
        proposal = self.setup_proposal(attach_document=True)

        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        browser.login().visit(proposal, view='tabbedview_view-overview')

        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()

        self.assertSequenceEqual(
            ['A new submitted version of document A Document has been created.'],
            info_messages())

    @browsing
    def test_do_not_show_link_if_document_is_not_outdated(self, browser):
        proposal = self.setup_proposal(attach_document=True)

        browser.login().visit(proposal, view='tabbedview_view-overview')

        self.assertIsNone(
            browser.find('Update document in proposal'),
            "The link to update the outdated document should not be visible "
            "because there is no new version of the document.")

    @browsing
    def test_do_not_show_link_to_update_outdated_document_on_submitted_proposal_view(self, browser):
        proposal, submitted_proposal = create(Builder('proposal')
            .within(self.dossier)
            .having(title='Mach doch',
                    committee=self.committee.load_model())
            .relate_to(self.document)
            .with_submitted())

        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        browser.login().visit(
            proposal, view='tabbedview_view-overview')

        self.assertEqual(
            ['Update document in proposal'],
            browser.css('a.proposal-outdated').text,
            "The outdated link should be visible on a proposal")

        browser.login().visit(
            submitted_proposal, view='tabbedview_view-overview')

        self.assertEqual(
            ['A Document'],
            browser.css('.document_link').text,
            "The document should be available in the "
            "submittedproposal listing")

        self.assertEqual(
            [], browser.css('a.proposal-outdated'),
            "The outdated link should not be visible on a submitted proposal")

    @browsing
    def test_submit_new_document_to_proposal_without_permission_on_committee_is_possible(self, browser):
        proposal = self.setup_proposal()

        self.login_as_user_without_committee_permission(browser)

        browser.visit(self.document)
        browser.find('Submit additional document').click()
        browser.fill({'Proposal': proposal})
        browser.find('Submit Attachments').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully.'],
            info_messages())

    @browsing
    def test_update_existing_document_without_permission_on_committee_is_possible(self, browser):
        proposal = self.setup_proposal(attach_document=True)
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        self.login_as_user_without_committee_permission(browser)

        browser.visit(proposal, view='tabbedview_view-overview')
        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()

        self.assertSequenceEqual(
            ['A new submitted version of document A Document has been created.'],
            info_messages())
