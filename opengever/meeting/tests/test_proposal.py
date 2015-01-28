from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.proposal import Proposal
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from zExceptions import Unauthorized


class TestProposalViewsDisabled(FunctionalTestCase):

    def setUp(self):
        super(TestProposalViewsDisabled, self).setUp()
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        self.dossier = create(Builder('dossier').within(folder))

    @browsing
    def test_add_form_is_disabled(self, browser):
        browser.login()
        with self.assertRaises(Unauthorized):
            browser.open(self.dossier,
                         view='++add++opengever.meeting.proposal')

    @browsing
    def test_edit_form_is_disabled(self, browser):
        proposal = create(Builder('proposal').within(self.dossier))

        with self.assertRaises(Unauthorized):
            browser.login().visit(proposal, view='edit')


class TestProposal(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestProposal, self).setUp()
        root = create(Builder('repository_root'))
        folder = create(Builder('repository').within(root))
        self.dossier = create(Builder('dossier').within(folder))

    def test_proposal_can_be_added(self):
        proposal = create(Builder('proposal').within(self.dossier))
        self.assertEqual('proposal-1', proposal.getId())

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)

    def search_for_document(self, browser, document):
        """Relation-widget, search for one document."""

        title = document.Title()
        browser.fill(
            {'form.widgets.relatedItems.widgets.query': title}).submit()

    @browsing
    def test_proposal_can_be_created_in_browser(self, browser):
        committee = create(Builder('committee_model'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('A Document'))

        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')

        self.search_for_document(browser, document)

        browser.fill({
            'Title': u'A pr\xf6posal',
            'Proposal': u'My pr\xf6posal',
            'Committee': str(committee.committee_id),
            'form.widgets.relatedItems:list': True,
            })
        browser.css('#form-buttons-save').first.click()
        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)

        proposal = browser.context
        self.assertEqual('proposal-1', proposal.getId())
        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(document, proposal.relatedItems[0].to_object)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual(u'A pr\xf6posal', model.title)
        self.assertEqual(u'My pr\xf6posal', model.initial_position)

        self.assertEqual(['a', 'pr\xc3\xb6posal', 'my', 'pr\xc3\xb6posal'],
                         index_data_for(proposal)['SearchableText'])

    @browsing
    def test_proposal_can_be_edited_in_browser(self, browser):
        committee = create(Builder('committee_model'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'A Document'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal'))

        browser.login().visit(proposal, view='edit')
        form = browser.css('#content-core form').first
        self.assertEqual(u'My Proposal', form.find_field('Title').value)

        self.search_for_document(browser, document)

        browser.fill({
            'Title': u'A pr\xf6posal',
            'Proposal': u'My pr\xf6posal',
            'Committee': str(committee.committee_id),
            'form.widgets.relatedItems:list': True,
            })

        browser.css('#form-buttons-save').first.click()
        self.assertIn('Changes saved',
                      browser.css('.portalMessage.info dd').text)

        proposal = browser.context
        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(document, proposal.relatedItems[0].to_object)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual(u'A pr\xf6posal', model.title)
        self.assertEqual(u'My pr\xf6posal', model.initial_position)

    @browsing
    def test_proposal_submission_works_correctly(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'A Document')
                          .with_dummy_content())
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .relate_to(document))

        self.assertSequenceEqual([], committee.listFolderContents())

        browser.login().open(proposal)

        browser.open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        proposal_model = proposal.load_model()

        # submitted proposal created
        self.assertEqual(1, len(committee.listFolderContents()))
        submitted_proposal = committee.listFolderContents()[0]

        # model synced
        self.assertEqual(proposal_model, submitted_proposal.load_model())
        self.assertEqual(Oguid.for_object(submitted_proposal),
                         proposal_model.submitted_oguid)
        self.assertEqual('submitted', proposal_model.workflow_state)

        # document copied
        self.assertEqual(1, len(submitted_proposal.get_documents()))
        submitted_document = submitted_proposal.get_documents()[0]
        self.assertEqual(document.Title(), submitted_document.Title())
        self.assertEqual(document.file.filename,
                         submitted_document.file.filename)

    @browsing
    def test_proposal_can_be_submitted(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model()))

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        self.assertEqual(Proposal.STATE_SUBMITTED, proposal.get_state())
