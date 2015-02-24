from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
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
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        self.dossier = create(Builder('dossier').within(folder))
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
            .having(committee=self.committee.load_model()))
        if attach_document:
            builder = builder.relate_to(self.document)

        proposal = create(builder)
        proposal.execute_transition('pending-submitted')
        self.assertTrue(proposal.is_submit_additional_documents_allowed())
        transaction.commit()
        return proposal

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

    def test_database_entry_is_deleted_when_removing_target_document(self):
        self.grant('Manager')
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=self.committee.load_model())
                          .relate_to(self.document))
        submitted_proposal = create(
            Builder('submitted_proposal').submitting(proposal))
        submitted_document = submitted_proposal.get_documents()[0]

        self.assertIsNotNone(
            SubmittedDocument.query.get_by_target(submitted_document))

        api.content.delete(submitted_document)

        self.assertIsNone(
            SubmittedDocument.query.get_by_target(submitted_document))

    def test_database_entry_is_deleted_when_removing_source_document(self):
        self.grant('Manager')
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=self.committee.load_model())
                          .relate_to(self.document))
        create(Builder('submitted_proposal').submitting(proposal))

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
        browser.find('Submit Document').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully'],
            info_messages())

    @browsing
    def test_submit_new_document_to_proposal_on_proposal_view(self, browser):
        proposal = self.setup_proposal()

        browser.login().visit(proposal)
        browser.find('Submit additional documents').click()
        browser.fill({'Documents': self.document})
        browser.find('Submit Documents').click()

        self.assertSubmittedDocumentCreated(proposal, self.document)
        self.assertSequenceEqual(
            ['Additional document A Document has been submitted successfully'],
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
        browser.fill({'Documents': self.document})
        browser.find('Submit Documents').click()

        self.assertSubmittedDocumentCreated(
            proposal, self.document, submitted_version=2)
        self.assertSequenceEqual(
            ['A new submitted version of document A Document has been created'],
            info_messages())

    def assertSubmittedDocumentCreated(self, proposal, document,
                                       submitted_version=0):
        portal = api.portal.get()
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal, document)
        submitted_document = portal.restrictedTraverse(
            submitted_document_model.submitted_physical_path.encode('utf-8'))
        self.assertIsNotNone(submitted_document_model)
        self.assertEqual(Oguid.for_object(submitted_document),
                         submitted_document_model.submitted_oguid)
        self.assertEqual(submitted_version,
                         submitted_document_model.submitted_version)
        self.assertEqual(proposal.load_model(),
                         submitted_document_model.proposal)
