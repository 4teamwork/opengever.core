from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.base.oguid import Oguid
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.meeting.model import Committee
from opengever.meeting.model import Proposal
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.proposal import IProposal
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
from zExceptions import Unauthorized


class TestProposalViewsDisabled(IntegrationTestCase):

    @browsing
    def test_add_form_is_disabled(self, browser):
        self.login(self.manager, browser)
        # This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            # with browser.expect_unauthorized():
            browser.open(self.dossier,
                         view='++add++opengever.meeting.proposal')

    @browsing
    def test_edit_form_is_disabled(self, browser):
        self.login(self.manager, browser)
        # This causes an infinite redirection loop between edit and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.visit(self.draft_proposal, view='edit')


class TestProposal(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_dossier_title_is_default_value_for_proposal_title(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        self.assertEqual(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                         browser.find('Title').value)

    @browsing
    def test_proposal_can_be_created_in_browser_and_strips_whitespace(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': str(self.committee_id),
            'Legal basis': u'<div>possible</div>',
            'Initial position': u'<div>My pr\xf6posal</div>',
            'Proposed action': u'<div>Lorem ips\xfcm</div>',
            'Decision draft': u'<div>Project allowed.</div>',
            'Publish in': u'<div>B\xe4rner Zeitung</div>',
            'Disclose to': u'<div>Hansj\xf6rg</div>',
            'Copy for attention': u'<div>   &nbsp; \n  &nbsp;</div>',
            'Attachments': [self.document],
        }).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')

        proposal = browser.context
        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(self.document, proposal.relatedItems[0].to_object)
        self.assertEqual(u'A pr\xf6posal', proposal.title)
        self.assertEqual(u'<div>possible</div>', proposal.legal_basis)
        self.assertEqual(u'<div>Lorem ips\xfcm</div>', proposal.proposed_action)
        self.assertEqual(u'<div>My pr\xf6posal</div>', proposal.initial_position)
        self.assertEqual(u'<div>Project allowed.</div>', proposal.decision_draft)
        self.assertEqual(u'<div>B\xe4rner Zeitung</div>', proposal.publish_in)
        self.assertEqual(u'<div>Hansj\xf6rg</div>', proposal.disclose_to)
        self.assertEqual(u'<div></div>', proposal.copy_for_attention)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual('robert.ziegler', model.creator)
        self.assertEqual(u'Vertr\xe4ge und Vereinbarungen',
                         model.repository_folder_title)
        self.assertEqual(u'en', model.language)

        self.assertTrue(set(['a', 'proposal', 'my', 'proposal']).issubset(set(
                            index_data_for(proposal)['SearchableText'])))

        self.assertEqual(u'Client1 1.1 / 1', model.dossier_reference_number)

    @browsing
    def test_create_proposal_in_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.subdossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'possible',
            'Initial position': u'My pr\xf6posal',
            'Proposed action': u'Lorem ips\xfcm',
            'Committee': str(self.committee_id)}).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')

        proposal = browser.context
        model = proposal.load_model()

        self.assertEqual(u'Client1 1.1 / 1', model.dossier_reference_number,
                         'Even when a proposal is created in a subdossier,'
                         ' its dossier_reference_number should be the'
                         ' reference number of the main dossier.')

    @browsing
    def test_proposal_can_be_edited_in_browser_and_strips_whitespace(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.draft_proposal)
        editbar.contentview('Edit').click()
        self.assertEqual(u'Antrag f\xfcr Kreiselbau',
                         browser.find('Title').value)

        browser.fill({
            'Title': u'A pr\xf6posal',
            'Legal basis': u'<div>not possible</div>',
            'Initial position': u'<div>My pr\xf6posal</div>',
            'Proposed action': u'<div>&nbsp; do it  \r </div>',
            'Committee': str(self.committee_id),
            'Publish in': u'<div>B\xe4rner Zeitung</div>',
            'Disclose to': u'<div>Hansj\xf6rg</div>',
            'Copy for attention': u'<div>P\xe4tra</div>',
            'Attachments': [self.document]}).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Changes saved')

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'A pr\xf6posal'],
             ['Committee', u'Rechnungspr\xfcfungskommission'],
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
             ['Attachments', u'Vertr\xe4gsentwurf']],
            browser.css('table.listing').first.lists())

        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(self.document, proposal.relatedItems[0].to_object)
        self.assertEqual(u'A pr\xf6posal', proposal.title)
        self.assertEqual(u'<div>not possible</div>', proposal.legal_basis)
        self.assertEqual(u'<div>My pr\xf6posal</div>', proposal.initial_position)
        self.assertEqual(u'<div>do it</div>', proposal.proposed_action)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)

    @browsing
    def test_proposal_language_field_with_multiple_languages(self, browser):
        """Test that changing the proposal language changes the indexed
        repository folder title.
        """
        self.login(self.dossier_responsible, browser)
        self.enable_languages()

        proposal = self.draft_proposal.load_model()
        self.assertEquals('de', proposal.language)
        self.assertEqual(u'Vertr\xe4ge und Vereinbarungen',
                         proposal.repository_folder_title)

        browser.open(self.draft_proposal, view='edit')
        browser.fill({'Language': 'fr'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('fr', proposal.language)
        self.assertEqual(u'Contrats et accords',
                         proposal.repository_folder_title)

    @browsing
    def test_dossier_link_rendering_for_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.find(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .get('href'))

    @browsing
    def test_proposal_edit_allowed_when_unsubmitted(self, browser):
        self.login(self.administrator, browser)
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)
        browser.open(self.draft_proposal)
        self.assertIn('Edit', editbar.contentviews())
        browser.open(self.draft_proposal, view='edit')

    @browsing
    def test_proposal_edit_not_allowed_when_submitted(self, browser):
        self.login(self.administrator, browser)
        self.assert_workflow_state('proposal-state-submitted', self.proposal)
        browser.open(self.proposal)
        self.assertNotIn('Edit', editbar.contentviews())
        with browser.expect_unauthorized():
            browser.open(self.proposal, view='edit')

    @browsing
    def test_submitted_proposal_edit_allowed_when_submitted(self, browser):
        self.login(self.administrator, browser)
        proposal_model = self.submitted_proposal.load_model()
        self.assertEquals('submitted', proposal_model.workflow_state)
        browser.open(self.submitted_proposal)
        self.assertIn('Edit', editbar.contentviews())
        browser.open(self.submitted_proposal, view='edit')

    @browsing
    def test_submitted_proposal_edit_not_allowed_when_decided(self, browser):
        self.login(self.administrator, browser)
        proposal_model = self.submitted_proposal.load_model()
        proposal_model.workflow_state = 'decided'
        browser.open(self.submitted_proposal)
        self.assertNotIn('Edit', editbar.contentviews())
        with browser.expect_unauthorized():
            browser.open(self.submitted_proposal, view='edit')

    @browsing
    def test_regression_proposal_submission_with_mails(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_related_items(self.draft_proposal, [self.mail])
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')

        self.login(self.committee_responsible)
        # submitted proposal created
        model = self.draft_proposal.load_model()
        submitted_path = model.submitted_physical_path.encode('utf-8')
        submitted_proposal = self.portal.restrictedTraverse(submitted_path)

        submitted_mail = submitted_proposal.get_documents()[0]
        self.assertSubmittedDocumentCreated(self.draft_proposal,
                                            self.mail,
                                            submitted_mail)

    def test_proposal_paths_remain_in_sync_when_dossier_is_moved(self):
        self.login(self.dossier_responsible)
        model = self.draft_proposal.load_model()
        self.assertEqual(u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                         u'/dossier-1/proposal-2', model.physical_path)
        self.assertEqual(u'Vertr\xe4ge und Vereinbarungen',
                         model.repository_folder_title)
        self.assertEqual(u'Client1 1.1 / 1',
                         model.dossier_reference_number)

        api.content.move(source=self.dossier,
                         target=self.empty_repofolder)
        self.assertEqual(u'ordnungssystem/rechnungsprufungskommission'
                         u'/dossier-1/proposal-2', model.physical_path)
        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         model.repository_folder_title)
        # XXX is this correct??
        self.assertEqual(u'Client1 2',
                         model.dossier_reference_number)

    @browsing
    def test_proposal_submission_works_correctly(self, browser):
        self.login(self.dossier_responsible, browser)
        self.add_related_item(self.draft_proposal, self.document)
        proposal_model = self.draft_proposal.load_model()
        self.assertIsNone(proposal_model.submitted_physical_path)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Proposal successfully submitted.')

        self.assertEqual(Proposal.STATE_SUBMITTED, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-submitted', self.draft_proposal)

        # submitted proposal created
        self.login(self.committee_responsible, browser)
        self.assertEqual(u'opengever-meeting-committeecontainer'
                         u'/committee-2/submitted-proposal-2',
                         proposal_model.submitted_physical_path)
        submitted_proposal = self.portal.restrictedTraverse(
            proposal_model.submitted_physical_path.encode('utf-8'))
        self.assertEqual(self.empty_committee,
                         aq_parent(aq_inner(submitted_proposal)))

        # model synced
        self.assertEqual(proposal_model, submitted_proposal.load_model())
        self.assertEqual(Oguid.for_object(submitted_proposal),
                         proposal_model.submitted_oguid)
        self.assertEqual('submitted', proposal_model.workflow_state)

        # document copied
        self.assertEqual(1, len(submitted_proposal.get_documents()))
        submitted_document = submitted_proposal.get_documents()[0]
        self.assertEqual(self.document.Title(), submitted_document.Title())
        self.assertEqual(self.document.file.filename,
                         submitted_document.file.filename)

        self.assertSubmittedDocumentCreated(
            self.draft_proposal, self.document, submitted_document)

        # document should have custom lock message
        browser.open(submitted_document)
        statusmessages.assert_message(
            u'This document has been submitted as a copy of Vertr\xe4gsentwurf and '
            u'cannot be edited directly.')
        self.assertEqual(
            self.document.absolute_url(),
            browser.css('.portalMessage.info a').first.get('href'))

    @browsing
    def test_proposal_can_be_cancelled(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Cancel')
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Proposal cancelled successfully.')

        self.assertEqual(Proposal.STATE_CANCELLED, self.draft_proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.draft_proposal)

    @browsing
    def test_proposal_can_be_reactivated(self, browser):
        self.login(self.dossier_responsible, browser)
        self.draft_proposal.execute_transition('pending-cancelled')
        self.assertEqual(Proposal.STATE_CANCELLED, self.draft_proposal.get_state())

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Reactivate')
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())

    @browsing
    def test_proposal_can_not_be_submitted_when_committee_is_inactive(self, browser):
        self.login(self.committee_responsible)
        self.empty_committee.load_model().deactivate()
        self.assertEqual(Committee.STATE_INACTIVE,
                         self.empty_committee.load_model().get_state())

        self.login(self.dossier_responsible, browser)
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')

        statusmessages.assert_message(
            u'The selected committeee has been deactivated, the proposal '
            u'could not been submitted.')
        self.assertEqual(self.draft_proposal.absolute_url(), browser.url)
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())

    @browsing
    def test_proposal_can_be_submitted_without_permission_on_commitee(self, browser):
        self.login(self.dossier_responsible, browser)
        # https://github.com/4teamwork/opengever.ftw/issues/41
        self.assertFalse(getSecurityManager().checkPermission(
            'View', self.draft_proposal.get_committee()))
        self.assertEqual(Proposal.STATE_PENDING, self.draft_proposal.get_state())
        browser.visit(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on('Submit')
        self.assertEqual(Proposal.STATE_SUBMITTED, self.draft_proposal.get_state())

    @browsing
    def test_submitted_proposal_can_be_rejected(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.proposal.load_model()
        self.assertEqual(
            'opengever-meeting-committeecontainer/committee-1/submitted-proposal-1',
            model.submitted_physical_path)
        self.assertEqual(Proposal.STATE_SUBMITTED, self.proposal.get_state())
        self.assert_workflow_state('proposal-state-submitted', self.proposal)

        browser.visit(self.submitted_proposal, view='tabbedview_view-overview')
        browser.click_on('Reject')
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message(u'The proposal has been rejected successfully')

        self.assertIsNone(model.submitted_physical_path)
        self.assertIsNone(model.submitted_int_id)
        self.assertIsNone(model.submitted_admin_unit_id)
        self.assertEqual(Proposal.STATE_PENDING, self.proposal.get_state())
        self.assert_workflow_state('proposal-state-active', self.proposal)
        with self.assertRaises(KeyError):
            self.submitted_proposal

    def test_copying_proposals_is_prevented(self):
        self.login(self.administrator)
        create(Builder('proposal')
               .within(self.empty_dossier)
               .titled(u'My Proposal')
               .having(committee=self.committee.load_model()))

        copied_dossier = api.content.copy(
            source=self.empty_dossier, target=self.empty_repofolder)
        self.assertItemsEqual([], copied_dossier.getFolderContents())

    def test_is_submission_allowed(self):
        self.login(self.administrator)
        self.assertFalse(self.draft_proposal.is_submit_additional_documents_allowed())

        self.assertTrue(self.proposal.is_submit_additional_documents_allowed())

        # these transitions are not exposed on the proposal side
        proposal_model = self.proposal.load_model()
        proposal_model.execute_transition('submitted-scheduled')
        self.assertTrue(self.proposal.is_submit_additional_documents_allowed())

        proposal_model.execute_transition('scheduled-decided')
        self.assertFalse(self.proposal.is_submit_additional_documents_allowed())

    def test_submit_additional_document(self):
        self.login(self.administrator)
        ori_document = self.subdocument
        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(ori_document)

        self.assertEquals(1, len(children['added']))
        submitted_document, = children['added']
        self.assertEqual(ori_document.Title(), submitted_document.Title())
        self.assertEqual(ori_document.file.filename, submitted_document.file.filename)

        self.assertSubmittedDocumentCreated(
            self.proposal, ori_document, submitted_document)

        # submitted document should be locked by custom lock
        lockable = ILockable(submitted_document)
        self.assertTrue(lockable.locked())
        self.assertFalse(lockable.can_safely_unlock(MEETING_SUBMITTED_LOCK))

    def test_submit_new_document_version_updates_submitted_document(self):
        self.login(self.administrator)
        ori_document = self.subdocument
        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(ori_document)

        self.assertEquals(1, len(children['added']))
        submitted_document, = children['added']

        self.assertEqual(0, submitted_document.get_current_version())

        # create some new document versions
        with self.login(self.dossier_responsible):
            repository = api.portal.get_tool('portal_repository')
            repository.save(ori_document)
            repository.save(ori_document)
            self.proposal.submit_additional_document(ori_document)

        self.assertEqual(1, submitted_document.get_current_version())

    def test_submit_document_updates_proposal_attachements(self):
        self.login(self.administrator)
        self.draft_proposal.execute_transition('pending-submitted')
        self.assertEqual(0, len(IProposal(self.draft_proposal).relatedItems))

        self.draft_proposal.submit_additional_document(self.document)
        self.assertEqual(
            [self.document],
            [item.to_object for item in IProposal(self.draft_proposal).relatedItems])

    def test_attributes_sort_order_for_proposal(self):
        self.login(self.dossier_responsible)
        attributes = self.proposal.get_overview_attributes()
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
            [attribute.get('label') for attribute in attributes])

    def test_attributes_sort_order_for_submitted_proposal(self):
        self.login(self.committee_responsible)
        attributes = self.submitted_proposal.get_overview_attributes()
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
        self.login(self.administrator)
        model = self.draft_proposal.load_model()
        self.assertEqual('', model.get_meeting_link())

    def test_get_meeting_link_returns_link_if_scheduled(self):
        self.login(self.committee_responsible)
        proposal_model = self.proposal.load_model()
        create(Builder('agenda_item').having(
            meeting=self.meeting.model,
            proposal=proposal_model))
        self.assertEqual(
            proposal_model.get_meeting_link(),
            self.meeting.model.get_link(),
            "The method should return the meeting link.")

    def test_get_containing_dossier_for_submitted_proposal_if_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.assertEqual(self.dossier,
                         self.submitted_proposal.get_containing_dossier())

    def test_get_none_for_containing_dossier_if_submitted_proposal_is_not_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.proposal.load_model().admin_unit_id = u'another-client'
        self.assertIsNone(self.submitted_proposal.get_containing_dossier())

    @browsing
    def test_get_link_to_dossier_for_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open_html(self.submitted_proposal.get_dossier_link())
        self.assertEqual(
            self.dossier.title,
            browser.css('a').first.get('title'))
        self.assertEqual(
            self.dossier.absolute_url(),
            browser.css('a').first.get('href'))

    def test_get_link_returns_fallback_message_if_proposal_is_not_on_same_admin_unit(self):
        self.login(self.committee_responsible)
        self.proposal.load_model().admin_unit_id = u'another-client'
        self.assertEqual(
            u'label_dossier_not_available',
            self.submitted_proposal.get_dossier_link())

    @browsing
    def test_proposal_title_is_displayed_xss_safe(self, browser):
        self.login(self.dossier_responsible, browser)
        self.proposal.title = u'<p>qux</p>'
        browser.open(self.proposal, view='tabbedview_view-overview')
        self.assertEqual('&lt;p&gt;qux&lt;/p&gt;',
                         browser.css('.listing td').first.innerHTML)

    @browsing
    def test_nonword_fields_visible_in_proposal_addform(self, browser):
        """When the "word implementation" feature is not enabled,
        the "old" trix fields should be visible.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
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

    def assertSubmittedDocumentCreated(self, proposal, document, submitted_document):
        submitted_document_model = SubmittedDocument.query.get_by_source(
            proposal, document)
        self.assertIsNotNone(submitted_document_model)
        self.assertEqual(Oguid.for_object(submitted_document),
                         submitted_document_model.submitted_oguid)
        self.assertEqual(0, submitted_document_model.submitted_version)
        self.assertEqual(proposal.load_model(),
                         submitted_document_model.proposal)
