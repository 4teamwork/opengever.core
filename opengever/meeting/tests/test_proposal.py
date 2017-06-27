from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.statusmessages import assert_message
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.core.testing import activate_meeting_word_implementation
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.proposal import IProposal
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from zExceptions import Unauthorized
import transaction


class TestProposalViewsDisabled(FunctionalTestCase):

    def setUp(self):
        super(TestProposalViewsDisabled, self).setUp()
        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier')
                              .titled(u'Dossier A')
                              .within(self.repo_folder))

    @browsing
    def test_add_form_is_disabled(self, browser):
        browser.login()
        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            # with browser.expect_unauthorized():
            browser.open(self.dossier,
                         view='++add++opengever.meeting.proposal')

    @browsing
    def test_edit_form_is_disabled(self, browser):
        proposal = create(Builder('proposal').within(self.dossier))

        # XXX This causes an infinite redirection loop between edit and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
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

    @browsing
    def test_dossier_title_is_default_value_for_proposal_title(self, browser):
        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')

        self.assertEqual(u'D\xf6ssier', browser.find('Title').value)

    @browsing
    def test_proposal_can_be_created_in_browser_and_strips_whitespace(self, browser):
        committee = create(Builder('committee_model'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('A Document'))

        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')

        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': str(committee.committee_id),
            'Legal basis': u'<div>possible</div>',
            'Initial position': u'<div>My pr\xf6posal</div>',
            'Proposed action': u'<div>Lorem ips\xfcm</div>',
            'Decision draft': u'<div>Project allowed.</div>',
            'Publish in': u'<div>B\xe4rner Zeitung</div>',
            'Disclose to': u'<div>Hansj\xf6rg</div>',
            'Copy for attention': u'<div>   &nbsp; \n  &nbsp;</div>',
            'Attachments': [document],
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
        self.assertEqual(TEST_USER_ID, model.creator)
        self.assertEqual(u'A pr\xf6posal', model.title)
        self.assertEqual(u'<div>possible</div>', model.legal_basis)
        self.assertEqual(u'<div>Lorem ips\xfcm</div>', model.proposed_action)
        self.assertEqual(u'<div>My pr\xf6posal</div>', model.initial_position)
        self.assertEqual(u'<div>Project allowed.</div>', model.decision_draft)
        self.assertEqual(u'<div>B\xe4rner Zeitung</div>', model.publish_in)
        self.assertEqual(u'<div>Hansj\xf6rg</div>', model.disclose_to)
        self.assertEqual(u'<div></div>', model.copy_for_attention)
        self.assertEqual(u'Stuff', model.repository_folder_title)
        self.assertEqual(u'en', model.language)

        self.assertTrue(set(['a', 'proposal', 'my', 'proposal']).issubset(set(
                            index_data_for(proposal)['SearchableText'])))

    @browsing
    def test_proposal_can_be_edited_in_browser_and_strips_whitespace(self, browser):
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

        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'<div>not possible</div>',
            'Initial position': u'<div>My pr\xf6posal</div>',
            'Proposed action': u'<div>&nbsp; do it  \r </div>',
            'Committee': str(committee.committee_id),
            'Publish in': u'<div>B\xe4rner Zeitung</div>',
            'Disclose to': u'<div>Hansj\xf6rg</div>',
            'Copy for attention': u'<div>P\xe4tra</div>',
            'Attachments': [document],
            })

        browser.css('#form-buttons-save').first.click()
        self.assertIn('Changes saved',
                      browser.css('.portalMessage.info dd').text)

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'A pr\xf6posal'],
             ['Committee', ''],
             ['Meeting', ''],
             ['Legal basis', 'not possible'],
             ['Initial position', u'My pr\xf6posal'],
             ['Proposed action', 'do it'],
             ['Decision draft', ''],
             ['Decision', ''],
             ['Publish in', u'B\xe4rner Zeitung'],
             ['Disclose to', u'Hansj\xf6rg'],
             ['Copy for attention', u'P\xe4tra'],
             ['State', 'Pending'],
             ['Decision number', ''],
             ['Attachments', 'A Document']],
            browser.css('table.listing').first.lists())

        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(document, proposal.relatedItems[0].to_object)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual(u'A pr\xf6posal', model.title)
        self.assertEqual(u'<div>not possible</div>', model.legal_basis)
        self.assertEqual(u'<div>My pr\xf6posal</div>', model.initial_position)
        self.assertEqual(u'<div>do it</div>', model.proposed_action)

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
    def test_dossier_link_rendering_for_proposal(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())
        submitted_proposal = proposal.load_model().submitted_oguid.resolve_object()

        browser.login().open(submitted_proposal,
                             view='tabbedview_view-overview')

        self.assertIsNotNone(browser.find(u'D\xf6ssier'))
        self.assertEqual(self.dossier.absolute_url(),
                         browser.find(u'D\xf6ssier').get('href'))

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
        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
        # with browser.expect_unauthorized():
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
        self.assertEqual(['Edit'],
                         browser.css('#content-views li').text)

        proposal_model = submitted_proposal.load_model()
        proposal_model.workflow_state = 'decided'
        transaction.commit()

        # cannot edit decided SubmittedProposal
        browser.open(submitted_proposal)
        self.assertEqual([],
                         browser.css('#content-views li').text)
        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
        # with browser.expect_unauthorized():
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

    def test_proposal_paths_remain_in_sync_when_dossier_is_moved(self):
        committee = create(Builder('committee').titled('My committee'))
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_dummy_message())
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .relate_to(mail))
        new_repo_folder = create(Builder('repository')
                                 .within(self.repo)
                                 .titled(u'New'))

        moved_dossier = api.content.move(
            source=self.dossier, target=new_repo_folder)
        moved_proposal = moved_dossier['proposal-1']
        model = moved_proposal.load_model()
        self.assertEqual(
            'ordnungssystem/new/dossier-1/proposal-1',
            model.physical_path)
        self.assertEqual(u'New', model.repository_folder_title)
        self.assertEqual(u'Client1 2', model.dossier_reference_number)

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

        self.assertEqual(['Proposal successfully submitted.'], info_messages())

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

        # document should have custom lock message
        browser.open(submitted_document)
        self.assertEqual(
            ['This document has been submitted as a copy of A Document and '
             'cannot be edited directly.'],
            info_messages())
        self.assertEqual(
            document.absolute_url(),
            browser.css('.portalMessage.info a').first.get('href'))

    @browsing
    def test_dossier_reference_number_is_set_on_creation(self, browser):
        committee = create(Builder('committee_model'))
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled('A Document'))

        browser.login()
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'Attachments': [document],
        })
        browser.find('Save').click()

        self.assertEqual(
            u'Client1 1 / 1',
            browser.context.load_model().dossier_reference_number)

    @browsing
    def test_proposal_stores_reference_number_of_main_dossier(self, browser):
        committee = create(Builder('committee_model'))
        subdossier = create(Builder('dossier')
                            .titled(u'Sub A')
                            .within(self.dossier))
        document = create(Builder('document')
                          .within(subdossier)
                          .titled('A Document'))

        browser.login()
        browser.open(subdossier, view='++add++opengever.meeting.proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(committee.committee_id),
            'Attachments': [document],
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

        self.assertEqual(Proposal.STATE_PENDING, proposal.get_state())
        self.assertEqual('proposal-state-active',
                         api.content.get_state(proposal))

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        self.assertEqual(Proposal.STATE_SUBMITTED, proposal.get_state())
        self.assertEqual('proposal-state-submitted',
                         api.content.get_state(proposal))

    @browsing
    def test_proposal_can_be_cancelled(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model()))

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-cancelled').first.click()

        self.assertEqual(Proposal.STATE_CANCELLED, proposal.get_state())

    @browsing
    def test_proposal_can_be_reactivated(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model())
                          .as_cancelled())

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#cancelled-pending').first.click()

        self.assertEqual(Proposal.STATE_PENDING, proposal.get_state())

    @browsing
    def test_proposal_can_not_be_submitted_when_committee_is_inactive(self, browser):
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model()))

        committee.load_model().deactivate()
        transaction.commit()

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()

        self.assertEqual(
            [u'The selected committeee has been deactivated, the proposal '
             'could not been submitted.'], error_messages())
        self.assertEqual(proposal.absolute_url(), browser.url)
        self.assertEqual(Proposal.STATE_PENDING, proposal.load_model().get_state())

    @browsing
    def test_proposal_can_be_submitted_without_permission_on_commitee(self, browser):
        document = create(Builder('document').within(self.dossier))
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model(),
                                  relatedItems=[document]))


        self.login_as_user_without_committee_permission(browser, committee)

        browser.visit(proposal, view='tabbedview_view-overview')
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

        self.assertEqual('proposal-state-submitted', api.content.get_state(proposal))
        submitted_proposal = proposal.load_model().resolve_submitted_proposal()
        browser.open(submitted_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()
        self.assertEqual('proposal-state-active', api.content.get_state(proposal))

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

    def test_copying_proposals_is_prevented(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model()))

        copied_dossier = api.content.copy(
            source=self.dossier, target=self.repo_folder)
        self.assertItemsEqual([], copied_dossier.getFolderContents())

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

    def test_submit_additional_document_creates_new_locked_document(self):
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

        # submitted document should be locked by custom lock
        lockable = ILockable(submitted_document)
        self.assertTrue(lockable.locked())
        self.assertTrue(lockable.can_safely_unlock(MEETING_SUBMITTED_LOCK))

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

    def test_submit_document_updates_proposal_attachements(self):
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

        self.assertEqual(0, len(IProposal(proposal).relatedItems))

        proposal.submit_additional_document(document)

        self.assertEqual(
            [document],
            [item.to_object for item in IProposal(proposal).relatedItems])

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
             u'label_meeting',
             u'label_legal_basis',
             u'label_initial_position',
             u'label_proposed_action',
             u'label_decision_draft',
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
             u'label_dossier',
             u'label_meeting',
             u'label_legal_basis',
             u'label_initial_position',
             u'label_proposed_action',
             u'label_considerations',
             u'label_discussion',
             u'label_decision_draft',
             u'label_decision',
             u'label_publish_in',
             u'label_disclose_to',
             u'label_copy_for_attention',
             u'label_workflow_state',
             u'label_decision_number'],
            [attribute.get('label') for attribute in attributes],
            )

    def test_get_meeting_link_returns_empty_string_if_not_scheduled(self):
        proposal = create(Builder('proposal_model'))

        self.assertEqual('', proposal.get_meeting_link())

    def test_get_meeting_link_returns_link_if_scheduled(self):
        admin_unit = create(Builder('admin_unit'))
        proposal = create(Builder('proposal_model'))
        committee = create(Builder('committee_model')
                           .having(admin_unit_id=admin_unit.unit_id))
        meeting = create(Builder('meeting').having(committee=committee))
        create(Builder('agenda_item').having(meeting=meeting, proposal=proposal))

        self.assertEqual(
            proposal.get_meeting_link(),
            meeting.get_link(),
            "The method should return the meeting link.")

    def test_get_containing_dossier_for_submitted_proposal_if_on_same_admin_unit(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        submitted_proposal = proposal.load_model().resolve_submitted_proposal()

        self.assertEqual(
            self.dossier, submitted_proposal.get_containing_dossier())

    def test_get_none_for_containing_dossier_if_submitted_proposal_is_not_on_same_admin_unit(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        model = proposal.load_model()
        submitted_proposal = model.resolve_submitted_proposal()

        model.admin_unit_id = u'client2'

        self.assertIsNone(submitted_proposal.get_containing_dossier())

    @browsing
    def test_get_link_to_dossier_for_submitted_proposal(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        submitted_proposal = proposal.load_model().resolve_submitted_proposal()

        browser.open_html(submitted_proposal.get_dossier_link())

        self.assertEqual(
            self.dossier.title,
            browser.css('a').first.get('title'))

        self.assertEqual(
            self.dossier.absolute_url(),
            browser.css('a').first.get('href'))

    def test_get_link_returns_fallback_message_if_proposal_is_not_on_same_admin_unit(self):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'My Proposal')
                          .having(committee=committee.load_model())
                          .as_submitted())

        model = proposal.load_model()

        submitted_proposal = proposal.load_model().resolve_submitted_proposal()

        model.admin_unit_id = u'client2'

        self.assertEqual(
            u'label_dossier_not_available', submitted_proposal.get_dossier_link())

    @browsing
    def test_proposal_title_is_displayed_xss_safe(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'<p>qux</p>')
                          .having(committee=committee.load_model()))

        browser.login().open(proposal, view='tabbedview_view-overview')

        self.assertEqual('&lt;p&gt;qux&lt;/p&gt;',
                         browser.css('.listing td').first.innerHTML)

    @browsing
    def test_proposal_cannot_change_state_when_documents_checked_out(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .titled(u'<p>qux</p>')
                          .having(committee=committee.load_model()))
        create(Builder('document').within(proposal).checked_out())

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')
        assert_message('Cannot change the state because the proposal'
                       ' contains checked out documents.')

    def assertSubmittedDocumentCreated(self, proposal, document, submitted_document):
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal, document)
        self.assertIsNotNone(submitted_document_model)
        self.assertEqual(Oguid.for_object(submitted_document),
                         submitted_document_model.submitted_oguid)
        self.assertEqual(0, submitted_document_model.submitted_version)
        self.assertEqual(proposal.load_model(),
                         submitted_document_model.proposal)

    def login_as_user_without_committee_permission(self, browser, committee):
        create(Builder('user').named('Hugo', 'Boss'))
        api.user.grant_roles(username=u'hugo.boss',
                             obj=self.dossier,
                             roles=['Contributor', 'Editor', 'Reader'])
        transaction.commit()
        browser.login(username='hugo.boss')
        with browser.expect_unauthorized():
            browser.open(committee)

    @browsing
    def test_nonword_fields_visible_in_addform(self, browser):
        """When the "word implementation" feature is not enabled,
        the "old" trix fields should be visible.
        """
        create(Builder('committee_model').having(title=u'Baukomission'))
        create(Builder('proposaltemplate').titled(u'Baugesuch')
               .within(create(Builder('templatefolder').titled(u'Vorlagen'))))
        dossier = create(
            Builder('dossier').titled(u'D\xf6ssier')
            .within(create(Builder('repository').titled(u'Stuff')
                           .within(create(Builder('repository_root'))))))

        browser.login().open(dossier)
        factoriesmenu.add('Proposal')
        expected = ('Legal basis',
                    'Initial position',
                    'Proposed action',
                    'Decision draft',
                    'Publish in',
                    'Disclose to',
                    'Copy for attention')
        missing = tuple(set(expected) - set(browser.forms['form'].field_labels))
        self.assertEquals((), missing)
        self.assertNotIn('File', browser.forms['form'].field_labels)


class TestProposalWithWord(FunctionalTestCase):

    def setUp(self):
        super(TestProposalWithWord, self).setUp()
        activate_meeting_word_implementation()

    @browsing
    def test_creating_proposal_from_proposal_template(self, browser):
        create(Builder('committee_model').having(title=u'Baukomission'))
        create(Builder('proposaltemplate').titled(u'Baugesuch')
               .attach_file_containing('Word Content', u'file.docx')
               .within(create(Builder('templatefolder').titled(u'Vorlagen'))))
        dossier = create(
            Builder('dossier').titled(u'D\xf6ssier')
            .within(create(Builder('repository').titled(u'Stuff')
                           .within(create(Builder('repository_root'))))))

        browser.login().open(dossier)
        factoriesmenu.add('Proposal')
        browser.fill({'Title': u'Baugesuch Kreuzachkreisel',
                      'Committee': u'Baukomission',
                      'Proposal template': 'Baugesuch'}).save()
        statusmessages.assert_no_error_messages()

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'Baugesuch Kreuzachkreisel'],
             ['Committee', ''],
             ['Meeting', ''],
             ['Proposal document',
              'Proposal document Baugesuch Kreuzachkreisel'],
             ['State', 'Pending'],
             ['Decision number', '']],
            browser.css('table.listing').first.lists())

        browser.click_on('Proposal document Baugesuch Kreuzachkreisel')
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertDictContainsSubset(
            {'Title': u'Proposal document Baugesuch Kreuzachkreisel'},
            dict(browser.css('table.listing').first.lists()))

        self.assertEquals(
            'Word Content',
            proposal.get_proposal_document().file.open().read())

    @browsing
    def test_proposal_document_is_visible_on_submitted_proposal(self, browser):
        committee = create(Builder('committee').titled('My committee'))
        repo, repo_folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(repo_folder)
                         .titled(u'An important dossier'))
        proposal = create(Builder('proposal')
                          .titled(u'An important proposal')
                          .within(dossier)
                          .having(committee=committee.load_model()))
        submitted_proposal = create(Builder('submitted_proposal')
                                    .submitting(proposal))
        transaction.commit()

        browser.login().open(submitted_proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'An important proposal'],
             ['Committee', 'My committee'],
             ['Dossier', 'An important dossier'],
             ['Meeting', ''],
             ['Proposal document',
              'Proposal document An important proposal'],
             ['State', 'Submitted'],
             ['Decision number', '']],
            browser.css('table.listing').first.lists())

    @browsing
    def test_visible_fields_in_addform(self, browser):
        """When the "word implementation" feature is enabled,
        the "old" trix fields should disappear.
        """
        create(Builder('committee_model').having(title=u'Baukomission'))
        create(Builder('proposaltemplate').titled(u'Baugesuch')
               .within(create(Builder('templatefolder').titled(u'Vorlagen'))))
        dossier = create(
            Builder('dossier').titled(u'D\xf6ssier')
            .within(create(Builder('repository').titled(u'Stuff')
                           .within(create(Builder('repository_root'))))))

        browser.login().open(dossier)
        factoriesmenu.add('Proposal')
        hidden = ('Legal basis',
                  'Initial position',
                  'Proposed action',
                  'Decision draft',
                  'Publish in',
                  'Disclose to',
                  'Copy for attention')
        missing = tuple(set(hidden) - set(browser.forms['form'].field_labels))
        self.assertItemsEqual(hidden, missing)

    @browsing
    def test_word_proposal_can_be_submitted(self, browser):
        repo, repo_folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(repo_folder))
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .with_proposal_file('Fake proposal file body')
                          .having(title='Mach doch',
                                  committee=committee.load_model()))

        self.assertEqual(Proposal.STATE_PENDING, proposal.get_state())
        self.assertEqual('proposal-state-active',
                         api.content.get_state(proposal))

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()
        self.assertEqual(['Proposal successfully submitted.'], info_messages())
        self.assertEqual(Proposal.STATE_SUBMITTED, proposal.get_state())
        self.assertEqual('proposal-state-submitted',
                         api.content.get_state(proposal))

        submitted_proposal = proposal.load_model().resolve_submitted_proposal()
        self.assertEquals(
            'Fake proposal file body',
            submitted_proposal.get_proposal_document().file.open().read())

    @browsing
    def test_document_of_submitted_proposal_cannot_be_edited(self, browser):
        repo, repo_folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(repo_folder))
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .with_proposal_file('Fake proposal file body')
                          .having(title='Mach doch',
                                  committee=committee.load_model()))

        browser.login().open(proposal.get_proposal_document(), view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable.')

        browser.login().open(proposal, view='tabbedview_view-overview')
        browser.css('#pending-submitted').first.click()
        self.assertEqual(['Proposal successfully submitted.'], info_messages())

        with browser.expect_unauthorized():
            browser.open(proposal.get_proposal_document(), view='edit')

        submitted_proposal = proposal.load_model().resolve_submitted_proposal()
        browser.open(submitted_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()

        browser.login().open(proposal.get_proposal_document(), view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable again.')

    @browsing
    def test_prevent_trashing_proposal_document(self, browser):
        repo, repo_folder = create(Builder('repository_tree'))
        dossier = create(Builder('dossier').within(repo_folder))
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model()))
        self.assertFalse(
            api.user.has_permission('opengever.trash: Trash content',
                                    obj=proposal.get_proposal_document()),
            'The proposal document should not be trashable.')
