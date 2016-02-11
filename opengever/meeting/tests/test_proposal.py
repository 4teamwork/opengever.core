from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from plone import api
from zExceptions import Unauthorized
import transaction


class TestProposalViewsDisabled(FunctionalTestCase):

    def setUp(self):
        super(TestProposalViewsDisabled, self).setUp()
        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier').within(self.repo_folder))

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
        self.repo = create(Builder('repository_root'))
        self.repo_folder = create(Builder('repository')
                                  .within(self.repo)
                                  .titled(u'Stuff'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo_folder)
                              .titled(u'D\xf6ssier'))

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
    def test_dossier_title_is_default_value_for_proposal_title(self, browser):
        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')

        self.assertEqual(u'D\xf6ssier', browser.find('Title').value)

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
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'Publish in': u'B\xe4rner Zeitung',
            'Disclose to': u'Hansj\xf6rg',
            'Copy for attention': u'P\xe4tra',
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
        self.assertEqual(u'possible', model.legal_basis)
        self.assertEqual(u'Lorem ips\xfcm', model.proposed_action)
        self.assertEqual(u'My pr\xf6posal', model.initial_position)
        self.assertEqual(u'B\xe4rner Zeitung', model.publish_in)
        self.assertEqual(u'Hansj\xf6rg', model.disclose_to)
        self.assertEqual(u'P\xe4tra', model.copy_for_attention)
        self.assertEqual(u'P\xe4tra', model.copy_for_attention)
        self.assertEqual(u'Stuff', model.repository_folder_title)
        self.assertEqual(u'en', model.language)

        self.assertEqual(['a', 'proposal', 'my', 'proposal'],
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
            'Legal basis': u'not possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'Publish in': u'B\xe4rner Zeitung',
            'Disclose to': u'Hansj\xf6rg',
            'Copy for attention': u'P\xe4tra',
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
        self.assertEqual(u'not possible', model.legal_basis)
        self.assertEqual(u'My pr\xf6posal', model.initial_position)
        self.assertEqual(u'Lorem ips\xfcm', model.proposed_action)

    @browsing
    def test_proposal_language_field_with_multiple_languages(self, browser):
        """Create and update proposal with multiple languages.

        Test that form displays language selection widget and updates/sets
        repository_folder_title for the chosen language.

        """
        committee = create(Builder('committee_model'))
        self.repo_folder.title_fr = u'Stoffe'

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.use_combined_language_codes = True
        lang_tool.addSupportedLanguage('de-ch')
        lang_tool.addSupportedLanguage('fr-ch')
        lang_tool.addSupportedLanguage('en')
        transaction.commit()

        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': str(committee.committee_id),
            'Language': 'fr'
            })
        browser.css('#form-buttons-save').first.click()

        proposal = browser.context.load_model()
        self.assertIn('Item created',
                      browser.css('.portalMessage.info dd').text)
        self.assertEqual(u'fr', proposal.language)
        self.assertEqual(u'Stoffe', proposal.repository_folder_title)

        browser.visit(browser.context, view='edit')
        browser.fill({
            'Language': 'de'
            })
        browser.css('#form-buttons-save').first.click()

        proposal = browser.context.load_model()
        self.assertIn('Changes saved',
                      browser.css('.portalMessage.info dd').text)
        self.assertEqual(u'de', proposal.language)
        self.assertEqual(u'Stuff', proposal.repository_folder_title)

    @browsing
    def test_edit_view_availability_for_proposal(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model()))

        # can edit pending proposal
        browser.login().open(proposal)
        self.assertEqual(['Edit'], browser.css('#content-views li').text)

        browser.open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        # cannot edit submitted proposal
        browser.open(proposal)
        self.assertEqual([], browser.css('#content-views li').text)
        with self.assertRaises(Unauthorized):
            browser.open(proposal, view='edit')

    @browsing
    def test_edit_view_availability_for_submitted_proposal(self, browser):
        self.grant("Administrator")
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        # can edit submitted SubmittedProposal
        submitted_proposal = api.portal.get().restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))
        browser.login().open(submitted_proposal)
        self.assertEqual(['Edit', 'Sharing'],
                         browser.css('#content-views li').text)

        proposal_model = submitted_proposal.load_model()
        proposal_model.workflow_state = 'decided'
        transaction.commit()

        # cannot edit decided SubmittedProposal
        browser.open(submitted_proposal)
        self.assertEqual(['Sharing'],
                         browser.css('#content-views li').text)
        with self.assertRaises(Unauthorized):
            browser.open(submitted_proposal, view='edit')

    @browsing
    def test_regression_proposal_submission_with_mails(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_dummy_message())
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .relate_to(mail))

        browser.login().open(proposal)
        browser.open(proposal, view='tabbedview_view-overview')
        browser.find('Submit').click()

        # submitted proposal created
        self.assertEqual(1, len(committee.listFolderContents()))
        submitted_proposal = committee.listFolderContents()[0]

        submitted_mail = submitted_proposal.get_documents()[0]
        self.assertSubmittedDocumentCreated(proposal, mail, submitted_mail)

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

        self.assertSubmittedDocumentCreated(proposal, document, submitted_document)

    @browsing
    def test_dossier_reference_number_is_set_on_creation(self, browser):
        committee = create(Builder('committee_model'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('A Document'))

        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        self.search_for_document(browser, document)
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'form.widgets.relatedItems:list': True,
        })
        browser.find('Save').click()

        self.assertEqual(
            u'Client1 1 / 1',
            browser.context.load_model().dossier_reference_number)

    @browsing
    def test_proposal_stores_reference_number_of_main_dossier(self, browser):
        committee = create(Builder('committee_model'))
        subdossier = create(Builder('dossier').within(self.dossier))
        document = create(Builder('document')
                          .within(subdossier)
                          .titled('A Document'))

        browser.login()
        browser.open(subdossier, view='++add++opengever.meeting.proposal')
        self.search_for_document(browser, document)
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'form.widgets.relatedItems:list': True,
        })
        browser.find('Save').click()

        self.assertEqual(
            u'Client1 1 / 1',
            browser.context.load_model().dossier_reference_number)

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

    @browsing
    def test_submitted_proposal_can_be_rejected(self, browser):
        self.grant('CommitteeGroupMember', 'Contributor', 'Editor')
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('A Document'))

        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model())
                          .relate_to(document))

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        submitted_path = proposal.load_model().submitted_physical_path.encode('utf-8')
        self.assertIsNotNone(self.portal.unrestrictedTraverse(submitted_path))

        submitted_proposal = proposal.load_model().resolve_sumitted_proposal()
        browser.open(submitted_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()

        with self.assertRaises(KeyError):
            self.portal.unrestrictedTraverse(submitted_path)
        self.assertEqual([u"The proposal has been rejected successfully"],
                         info_messages())
        self.assertEqual(Proposal.STATE_PENDING, proposal.get_state())

        proposal_model = proposal.load_model()
        self.assertIsNone(proposal_model.submitted_physical_path)
        self.assertIsNone(proposal_model.submitted_int_id)
        self.assertIsNone(proposal_model.submitted_admin_unit_id)

        for record in proposal_model.history_records:
            self.assertIsNone(
                record.submitted_document,
                "reference to submitted document on {} should be removed".format(
                    record))

    def test_is_submission_allowed(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model()))

        self.assertFalse(proposal.is_submit_additional_documents_allowed())
        proposal.execute_transition('pending-submitted')
        self.assertTrue(proposal.is_submit_additional_documents_allowed())

        # these transitions are not exposed on the proposal side
        proposal_model = proposal.load_model()
        proposal_model.execute_transition('submitted-scheduled')
        self.assertTrue(proposal.is_submit_additional_documents_allowed())

        proposal_model.execute_transition('scheduled-decided')
        self.assertFalse(proposal.is_submit_additional_documents_allowed())

    def test_submit_additional_document_creates_new_document(self):
        committee = create(Builder('committee').titled('My committee'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'A Document')
                          .with_dummy_content())
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .as_submitted()
                          .having(committee=committee.load_model()))

        proposal.submit_additional_document(document)
        submitted_proposal = api.portal.get().restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))
        docs = submitted_proposal.listFolderContents()
        self.assertEqual(1, len(docs))
        submitted_document = docs.pop()

        self.assertEqual(document.Title(), submitted_document.Title())
        self.assertEqual(document.file.filename,
                         submitted_document.file.filename)

        self.assertSubmittedDocumentCreated(proposal, document, submitted_document)

    def test_submit_new_document_version_updates_submitted_document(self):
        committee = create(Builder('committee').titled('My committee'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'A Document')
                          .with_dummy_content())
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .relate_to(document)
                          .as_submitted())

        submitted_proposal = api.portal.get().restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))
        docs = submitted_proposal.get_documents()
        submitted_document = docs.pop()
        self.assertEqual(0, submitted_document.get_current_version())

        # create some new document versions
        repository = api.portal.get_tool('portal_repository')
        repository.save(document)
        repository.save(document)
        proposal.submit_additional_document(document)

        self.assertEqual(1, submitted_document.get_current_version())

    def test_attributes_sort_order_for_proposal(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        attributes = proposal.get_overview_attributes()
        self.assertEqual(
            [u'label_title',
             u'label_committee',
             u'label_legal_basis',
             u'label_initial_position',
             u'label_proposed_action',
             u'label_decision',
             u'label_publish_in',
             u'label_disclose_to',
             u'label_copy_for_attention',
             u'label_workflow_state',
             u'label_decision_number'],
            [attribute.get('label') for attribute in attributes],
            )

    def test_attributes_sort_order_for_submitted_proposal(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        submitted_proposal = api.portal.get().restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))

        attributes = submitted_proposal.get_overview_attributes()
        self.assertEqual(
            [u'label_title',
             u'label_committee',
             u'label_legal_basis',
             u'label_initial_position',
             u'label_proposed_action',
             u'label_considerations',
             u'label_discussion',
             u'label_decision',
             u'label_publish_in',
             u'label_disclose_to',
             u'label_copy_for_attention',
             u'label_workflow_state',
             u'label_decision_number'],
            [attribute.get('label') for attribute in attributes],
            )

    def assertSubmittedDocumentCreated(self, proposal, document, submitted_document):
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal, document)
        self.assertIsNotNone(submitted_document_model)
        self.assertEqual(Oguid.for_object(submitted_document),
                         submitted_document_model.submitted_oguid)
        self.assertEqual(0, submitted_document_model.submitted_version)
        self.assertEqual(proposal.load_model(),
                         submitted_document_model.proposal)
