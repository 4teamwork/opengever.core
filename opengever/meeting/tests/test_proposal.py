from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from OFS.interfaces import IObjectWillBeRemovedEvent
from opengever.base.oguid import Oguid
from opengever.locking.lock import MEETING_SUBMITTED_LOCK
from opengever.meeting import CLOSED_PROPOSAL_STATES
from opengever.meeting import OPEN_PROPOSAL_STATES
from opengever.meeting import SUBMITTED_PROPOSAL_STATES
from opengever.meeting.command import MIME_DOCX
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from opengever.testing.event_recorder import get_recorded_events
from opengever.testing.event_recorder import register_event_recorder
from plone import api
from plone.locking.interfaces import ILockable
from plone.protect import createToken
from requests_toolbelt.utils import formdata
from StringIO import StringIO
from zc.relation.interfaces import ICatalog
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.component import getUtility
import json


class TestProposalStateGlobals(IntegrationTestCase):

    def test_state_constants_cover_all_states(self):
        self.login(self.manager)
        all_states = OPEN_PROPOSAL_STATES + CLOSED_PROPOSAL_STATES

        wftool = api.portal.get_tool('portal_workflow')
        workflow = wftool.getWorkflowById('opengever_proposal_workflow')
        self.assertItemsEqual(all_states, tuple(workflow.states),
            "Workflow state global definitions and actually available "
            "workflow states are unequal. You probably have added a new state"
            "and now the module globals must be updated.")

    def test_submitted_proposal_states_defined_in_workflow(self):
        wftool = api.portal.get_tool('portal_workflow')
        workflow = wftool.getWorkflowById('opengever_proposal_workflow')

        self.assertTrue(all(state in tuple(workflow.states)
                        for state in SUBMITTED_PROPOSAL_STATES))


class TestProposalViewsDisabled(IntegrationTestCase):

    features = (
        '!meeting',
    )

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


class TestProposalSolr(SolrIntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'meeting',
    )

    @browsing
    def test_proposal_template_field_dependencies(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')

        depends_on = json.loads(browser.css('.tableradio-widget-wrapper').first.get('data-vocabulary-depends-on'))
        committee_input_name = depends_on[0]

        self.assertEqual(1, len(depends_on), 'Only 1 dependency expected.')

        self.assertEqual('form.widgets.committee_oguid', committee_input_name,
                         'You changed the configuration of ProposalAddForm (probably). Please make sure that the field '
                         '"committee_oguid" still exists.')

        self.assertEqual(1, len(browser.css('select[name="{}:list"]'.format(committee_input_name))),
                         'Could not find dependent field {}.'.format(committee_input_name))

    @browsing
    def test_create_proposal_visible_in_dossier_actions_for_regular_user_when_meeting_enabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='tabbedview_view-documents-proxy')
        self.assertEqual(browser.css('.tabbedview-menu-create_proposal').text, ['Create Proposal'])

        self.deactivate_feature('meeting')
        browser.open(self.dossier, view='tabbedview_view-documents-proxy')
        self.assertEqual(browser.css('.tabbedview-menu-create_proposal').text, list())

    @browsing
    def test_creating_proposal_from_tabbedview_sets_attachments(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, view='tabbedview_view-documents-proxy')
        original_template = ('orig_template', '#'.join((self.dossier.absolute_url(), 'documents')), )
        authenticator = ('_authenticator', createToken(), )
        document_14_path = ('paths:list', browser.css('#document-14').first.node.attrib.get('value'), )
        document_35_path = ('paths:list', browser.css('#document-35').first.node.attrib.get('value'), )
        method = ('++add++opengever.meeting.proposal:method', '1', )
        browser.open(
            self.dossier.absolute_url(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode((original_template, authenticator, document_14_path, document_35_path, method, )),
            )
        self.assertEqual(
            [u'Vertr\xe4gsentwurf', 'Feedback zum Vertragsentwurf'],
            browser.css('#form-widgets-relatedItems span.label').text,
            )


class TestProposal(IntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'meeting',
    )

    @browsing
    def test_dossier_title_is_default_value_for_proposal_title(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='++add++opengever.meeting.proposal')
        self.assertEqual(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                         browser.find('Title').value)

    @browsing
    def test_proposal_creation_lists_sibling_proposal_documents_as_attachables(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.meeting.proposal',
            '++widget++form.widgets.relatedItems',
            '@@contenttree-fetch',
            ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
            )
        containers = browser.css('li.navTreeFolderish').text
        selectables = browser.css('li.selectable').text
        self.assertIn(self.proposal.title, containers)
        for document in self.proposal.get_documents():
            self.assertIn(document.title, selectables)

    @browsing
    def test_proposal_document_is_visible_on_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'Vertr\xe4ge'],
             ['Description', u'F\xfcr weitere Bearbeitung bewilligen'],
             ['Dossier', u'Vertr\xe4ge mit der kantonalen Finanzverwaltung'],
             ['Committee', u'Rechnungspr\xfcfungskommission'],
             ['Meeting', ''],
             ['Issuer', 'Ziegler Robert (robert.ziegler)'],
             ['Proposal document', u'Vertr\xe4ge'],
             ['State', 'Submitted'],
             ['Decision number', ''],
             ['Attachments', u'Vertr\xe4gsentwurf'],
             ['Excerpt', '']],
            browser.css('table.listing').first.lists())

    @browsing
    def test_creating_proposal_from_proposal_template(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill(
            {'Title': u'Baugesuch Kreuzachkreisel',
             'Description': u'Ein n\xf6tiger Bau',
             'Committee': u'Rechnungspr\xfcfungskommission',
             'Proposal template': u'Geb\xfchren',
             'Edit after creation': True,
             'Attachments': [self.document]},
             ).save()

        statusmessages.assert_no_error_messages()
        self.assertIn('external_edit', browser.css('.redirector').first.text,
                      'External editor should have been triggered.')

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'Baugesuch Kreuzachkreisel'],
             ['Description', u'Ein n\xf6tiger Bau'],
             ['Committee', u'Rechnungspr\xfcfungskommission'],
             ['Meeting', ''],
             ['Issuer', 'Ziegler Robert (robert.ziegler)'],
             ['Proposal document', 'Baugesuch Kreuzachkreisel'],
             ['State', 'Pending'],
             ['Decision number', ''],
             ['Attachments', u'Vertr\xe4gsentwurf'],
             ['Excerpt', '']],
            browser.css('table.listing').first.lists())
        self.assertEqual(u'en', proposal.language)
        self.assertEqual(self.document, proposal.relatedItems[0].to_object)
        self.assert_workflow_state('proposal-state-active', proposal)

        model = proposal.load_model()
        self.assertEqual(u'Baugesuch Kreuzachkreisel', model.title)
        self.assertEqual(u'Ein n\xf6tiger Bau', model.description)
        self.assertIsNone(model.submitted_title)
        self.assertIsNone(model.submitted_description)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual('robert.ziegler', model.issuer)
        self.assertEqual(u'Vertr\xe4ge und Vereinbarungen',
                         model.repository_folder_title)
        self.assertEqual(u'en', model.language)
        self.assertEqual(u'Client1 1.1 / 1', model.dossier_reference_number)

        self.assertTrue(set(['baugesuch', 'kreuzachkreisel',
                             'ein', 'notiger', 'bau']).issubset(
            set(index_data_for(proposal)['SearchableText'])))

        browser.click_on('Baugesuch Kreuzachkreisel')
        browser.open(browser.context, view='tabbedview_view-overview')
        self.assertDictContainsSubset(
            {'Title': u'Baugesuch Kreuzachkreisel'},
            dict(browser.css('table.listing').first.lists()))

        self.assertEquals(
            self.proposal_template.file.data,
            proposal.get_proposal_document().file.data)

        self.assertFalse(
            is_officeconnector_checkout_feature_enabled(),
            'Office connector checkout feature is now active: this means'
            ' that the document will no longer be checked out in the proposal'
            ' creation wizard and therefore the assertion "document is checked'
            ' out" will therefore fail.')
        self.assertEquals(
            self.dossier_responsible.getId(),
            self.get_checkout_manager(
                proposal.get_proposal_document()).get_checked_out_by())

    @browsing
    def test_proposal_can_be_created_in_browser_from_document(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal document type': 'Existing document',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
        }).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')
        self.assertEqual(
            browser.context.getChildNodes()._data[0].file.data,
            self.document.file.data,
            u'Did not succesfully copy the file over from self.document.',
            )
        self.assert_workflow_state('proposal-state-active', browser.context)

    @browsing
    def test_proposal_cannot_be_created_in_browser_without_document_and_template(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
        }).save()
        expected_errors = [
            'Error There were some errors.',
            'Either a proposal template or a proposal document is required.',
            ]
        self.assertEqual(expected_errors, browser.css('.error').text)

    @browsing
    def test_proposal_cannot_be_created_in_browser_if_false_document_type_is_selected(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Proposal document type': 'Existing document',
            'Proposal template': u'Geb\xfchren',
            'Committee': u'Rechnungspr\xfcfungskommission',
        }).save()
        expected_errors = [
            'Error There were some errors.',
            'Either a proposal template or a proposal document is required.',
            ]
        self.assertEqual(expected_errors, browser.css('.error').text)

        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Proposal document type': 'From template',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
            'Committee': u'Rechnungspr\xfcfungskommission',
        }).save()
        expected_errors = [
            'Error There were some errors.',
            'Either a proposal template or a proposal document is required.',
            ]
        self.assertEqual(expected_errors, browser.css('.error').text)

    @browsing
    def test_proposal_cannot_be_created_in_browser_from_excel_document(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal document type': 'Existing document',
            'Proposal Document': u'/'.join(self.subdocument.getPhysicalPath()),
        }).save()
        expected_errors = [
            'Error There were some errors.',
            'Only .docx files allowed as proposal documents.',
            ]
        self.assertEqual(expected_errors, browser.css('.error').text)

    @browsing
    def test_proposal_cannot_be_created_in_browser_from_old_word_document(self, browser):
        self.login(self.dossier_responsible, browser)
        self.document.file.contentType = 'application/msword'
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal document type': 'Existing document',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
        }).save()
        expected_errors = [
            'Error There were some errors.',
            'Only .docx files allowed as proposal documents.',
            ]
        self.assertEqual(expected_errors, browser.css('.error').text)

    @browsing
    def test_choose_selected_type_for_document(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal document type': 'Existing document',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
            'Proposal template': u'Geb\xfchren',
        }).save()

        self.assertEqual(
            browser.context.getChildNodes()._data[0].file.data,
            self.document.file.data
            )

        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal document type': 'From template',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
            'Proposal template': self.proposal_template.Title(),
        }).save()

        statusmessages.assert_no_error_messages()

        self.assertEqual(
            self.proposal_template.file.data,
            browser.context.getChildNodes()._data[0].file.data)

    @browsing
    def test_create_proposal_in_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.subdossier)
        factoriesmenu.add('Proposal')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Description': u'With a c\xf6mment',
            'Committee': u'Rechnungspr\xfcfungskommission',
            'Proposal template': u'Geb\xfchren',
        }).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')

        proposal = browser.context
        model = proposal.load_model()

        self.assertEqual(u'Client1 1.1 / 1', model.dossier_reference_number,
                         'Even when a proposal is created in a subdossier,'
                         ' its dossier_reference_number should be the'
                         ' reference number of the main dossier.')

    @browsing
    def test_proposal_can_be_edited_in_browser(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.draft_proposal)
        editbar.contentview('Edit').click()
        self.assertEqual(u'Antrag f\xfcr Kreiselbau',
                         browser.find('Title').value)

        browser.fill({
            'Title': u'Another pr\xf6posal',
            'Description': u'With another c\xf6mment',
            'Attachments': [self.document]}).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Changes saved')

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        self.assertEquals(
            [['Title', u'Another pr\xf6posal'],
             ['Description', u'With another c\xf6mment'],
             ['Committee', u'Kommission f\xfcr Verkehr'],
             ['Meeting', ''],
             ['Issuer', 'Ziegler Robert (robert.ziegler)'],
             ['Proposal document', u'Antrag f\xfcr Kreiselbau'],
             ['State', 'Pending'],
             ['Decision number', ''],
             ['Attachments', u'Vertr\xe4gsentwurf'],
             ['Excerpt', '']],
            browser.css('table.listing').first.lists())

        self.assertEqual(1, len(proposal.relatedItems))
        self.assertEqual(self.document, proposal.relatedItems[0].to_object)
        self.assertEqual(u'Another pr\xf6posal', proposal.title)
        self.assertEqual(u'With another c\xf6mment', proposal.description)

        model = proposal.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(proposal), model.oguid)
        self.assertEqual(u'Another pr\xf6posal', proposal.title)
        self.assertEqual(u'With another c\xf6mment', proposal.description)

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
    def test_document_of_draft_proposal_can_be_edited(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_proposal.get_proposal_document()
        browser.open(document, view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable.')

    @browsing
    def test_proposal_document_must_be_docx(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_proposal.get_proposal_document()
        self.checkout_document(document)
        browser.open(document, view='edit')
        browser.fill({'form.widgets.file.action': 'replace', 'File': ('asdf', 'foo.xlsx' 'application/fake')})
        browser.find('Save').click()
        expected_error = ["It's not possible to have non-.docx documents as proposal documents."]
        error = browser.css('#formfield-form-widgets-file .fieldErrorBox').text
        self.assertEqual(error, expected_error)

    @browsing
    def test_proposal_document_cannot_be_removed(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_proposal.get_proposal_document()
        self.checkout_document(document)
        browser.open(document, view='edit')
        browser.fill({'form.widgets.file.action': 'remove'})
        browser.find('Save').click()
        expected_error = ["It's not possible to have no file in proposal documents."]
        error = browser.css('#formfield-form-widgets-file .fieldErrorBox').text
        self.assertEqual(error, expected_error)

    @browsing
    def test_proposal_document_must_be_docx_via_quickupload(self, browser):
        self.login(self.dossier_responsible, browser)
        filename = 'foo.xlsx'
        headers = {
            'X-File-Name': filename,
            'Content-Type': 'application/octet-stream',
            'X-Requested-With': 'XMLHttpRequest',
            }
        fileish = StringIO('foobar')
        proposal_document = self.draft_proposal.get_proposal_document()
        self.checkout_document(proposal_document)
        expected_error = {u'error': u"It's not possible to have non-.docx documents as proposal documents."}
        browser.open(
            proposal_document,
            data={'file': fileish},
            headers=headers,
            view='@@quick_upload_file?qqfile={}'.format(filename),
            )
        fileish.close()
        self.assertEqual(browser.json, expected_error)

    @browsing
    def test_document_of_proposal_cannot_be_edited_when_submitted(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.proposal.get_proposal_document()
        with browser.expect_unauthorized():
            browser.open(document, view='edit')

    @browsing
    def test_document_of_rejected_proposal_can_be_edited(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view='tabbedview_view-overview')
        browser.find('Reject').click()
        browser.fill({'Comment': u'Bitte \xfcberarbeiten'}).submit()

        self.login(self.dossier_responsible, browser)
        document = self.proposal.get_proposal_document()
        browser.open(self.proposal.get_proposal_document(), view='edit')
        browser.open(document, view='edit')
        self.assertEquals('Edit Document', plone.first_heading(),
                          'Document should be editable.')

    @browsing
    def test_proposal_cannot_change_state_when_documents_checked_out(self, browser):
        self.login(self.dossier_responsible, browser)
        document = self.draft_proposal.get_proposal_document()
        self.checkout_document(document)
        self.assertTrue(self.draft_proposal.contains_checked_out_documents())
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        button = browser.find("proposal-transition-submit")
        self.assertFalse(button)

    def test_decide_not_allowed_when_documents_checked_out(self):
        """When deciding the proposal on the proposal model, the proposal
        document must already be checked in.
        This also applies to the current user: the auto-checkin-feature is
        the job of the agenda item controller, not of the proposal model.
        """
        self.login(self.committee_responsible)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        excerpt = agenda_item.generate_excerpt('Foo')

        self.checkout_document(self.submitted_proposal.get_proposal_document())

        model = self.submitted_proposal.load_model()
        with self.assertRaises(ValueError) as cm:
            model.decide(agenda_item, excerpt)

        self.assertEquals(
            'Cannot decide proposal when proposal document is checked out.',
            str(cm.exception))

    @browsing
    def test_regression_proposal_submission_with_mails(self, browser):
        self.login(self.dossier_responsible, browser)
        self.set_related_items(self.draft_proposal, [self.mail_eml])
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-submit")
        browser.click_on("Confirm")

        self.login(self.committee_responsible)
        # submitted proposal created
        self.assertSubmittedDocumentCreated(self.draft_proposal,
                                            self.mail_eml)

    @browsing
    def test_proposal_document_title_is_not_overridden_on_submit(self, browser):
        self.login(self.dossier_responsible, browser)
        changed_title = u'\xc4nderung'
        self.draft_proposal.get_proposal_document().title = changed_title
        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-submit")
        browser.click_on("Confirm")
        self.login(self.committee_responsible)
        # submitted proposal created
        model = self.draft_proposal.load_model()
        submitted_path = model.submitted_physical_path.encode('utf-8')
        submitted_proposal = self.portal.restrictedTraverse(submitted_path)
        self.assertEqual(changed_title, submitted_proposal.get_proposal_document().title)

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
        self.assertEqual(u'Client1 2 / 1',
                         model.dossier_reference_number)

    @browsing
    def test_regression_submitted_proposal_title_synced_on_submission(self, browser):
        """Test a regression for a proposal without attachments."""

        self.login(self.dossier_responsible, browser)
        proposal_model = self.draft_proposal.load_model()

        browser.open(self.draft_proposal, view='tabbedview_view-overview')
        browser.click_on("proposal-transition-submit")
        browser.click_on("Confirm")
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Review state changed successfully.')

        self.assertEqual(u'Antrag f\xfcr Kreiselbau',
                         proposal_model.submitted_title)

    def test_copying_proposals_is_prevented(self):
        self.login(self.administrator)
        create(Builder('proposal')
               .within(self.empty_dossier)
               .titled(u'My Proposal')
               .having(committee=self.committee.load_model()))

        register_event_recorder(IObjectWillBeRemovedEvent)

        copied_dossier = api.content.copy(
            source=self.empty_dossier, target=self.empty_repofolder)
        self.assertItemsEqual([], copied_dossier.getFolderContents())

        self.assertFalse(
            any(IObjectWillBeRemovedEvent.providedBy(event) for
                event in get_recorded_events())
        )

    @browsing
    def test_prevent_trashing_proposal_document(self, browser):
        self.login(self.dossier_responsible, browser)
        self.assertFalse(
            api.user.has_permission(
                'opengever.trash: Trash content',
                obj=self.proposal.get_proposal_document()),
            'The proposal document should not be trashable.')
        self.assertFalse(
            api.user.has_permission(
                'opengever.trash: Trash content',
                obj=self.draft_proposal.get_proposal_document()),
            'The proposal document should not be trashable.')

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

        self.assertSubmittedDocumentCreated(self.proposal, ori_document)

        # submitted document should be locked by custom lock
        lockable = ILockable(submitted_document)
        self.assertTrue(lockable.locked())
        self.assertFalse(lockable.can_safely_unlock(MEETING_SUBMITTED_LOCK))

    @browsing
    def test_unlock_submited_additional_document_will_unlock_but_not_unlink_document(self, browser):
        self.login(self.administrator, browser)

        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(self.subdocument)

        submitted_document, = children['added']
        lockable = ILockable(submitted_document)

        self.assertTrue(lockable.locked())
        self.assertIsNotNone(SubmittedDocument.query.get_by_target(submitted_document))

        browser.visit(submitted_document, view="@@unlock_submitted_document_form")
        browser.find_button_by_label('Unlock').click()

        statusmessages.assert_message('Document has been unlocked')

        self.assertFalse(lockable.locked(), "Submitted document should be unlocked")
        self.assertIsNotNone(
            SubmittedDocument.query.get_by_target(submitted_document),
            "Submitted document should not be unlinked")

    @browsing
    def test_unlock_not_submitted_document_raises_not_found_error(self, browser):
        self.login(self.administrator, browser)

        browser.exception_bubbling = True
        with self.assertRaises(NotFound):
            browser.visit(self.document, view="@@unlock_submitted_document_form")

    @browsing
    def test_unlock_submitted_document_returns_no_content_if_ajax_load_is_true(self, browser):
        self.login(self.administrator, browser)

        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(self.subdocument)

        submitted_document, = children['added']
        lockable = ILockable(submitted_document)

        browser.visit(submitted_document, view="@@unlock_submitted_document_form?ajax_load=true&form.buttons.unlock=true")

        self.assertEqual([''], browser.css('body').text_content())
        self.assertFalse(lockable.locked(), "Submitted document should be unlocked")

    def test_submit_new_document_version_updates_submitted_document(self):
        self.login(self.administrator)
        ori_document = self.subdocument
        with self.observe_children(self.submitted_proposal) as children:
            with self.login(self.dossier_responsible):
                self.proposal.submit_additional_document(ori_document)

        self.assertEquals(1, len(children['added']))
        submitted_document, = children['added']

        self.assertEqual(None, submitted_document.get_current_version_id())

        # create some new document versions
        with self.login(self.dossier_responsible):
            repository = api.portal.get_tool('portal_repository')
            repository.save(ori_document)
            repository.save(ori_document)
            self.proposal.submit_additional_document(ori_document)

        self.assertEqual(1, submitted_document.get_current_version_id())

    def test_submit_document_updates_proposal_attachements(self):
        self.login(self.administrator)
        api.content.transition(
            self.draft_proposal, 'proposal-transition-submit')
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
             u'label_description',
             u'label_committee',
             u'label_meeting',
             u'label_issuer',
             u'proposal_document',
             u'label_workflow_state',
             u'label_decision_number'],
            [attribute.get('label') for attribute in attributes])

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

    def test_generate_excerpt_copies_document_to_target(self):
        self.login(self.administrator)
        self.assertEquals(
            [],
            ISubmittedProposal(self.submitted_proposal).excerpts)

        agenda_item = self.schedule_proposal(self.meeting,
                              self.submitted_proposal)
        agenda_item.decide()

        with self.observe_children(self.meeting_dossier) as children:
            agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')

        self.assertEquals(1, len(children['added']),
                          'An excerpt document should have been added to the'
                          ' meeting dossier.')

        # The document should contain a copy of the proposal document file.
        excerpt_document, = children['added']
        self.assertEquals('Excerpt \xc3\x84nderungen',
                          excerpt_document.Title())
        self.assertEquals(u'Excerpt Aenderungen.docx',
                          excerpt_document.file.filename)
        self.assertEquals(MIME_DOCX, excerpt_document.file.contentType)
        self.assertIsNotNone(excerpt_document.file.data)

        # The excerpt document should be referenced as relation.
        excerpts = ISubmittedProposal(self.submitted_proposal).excerpts
        self.assertEquals(1, len(excerpts))
        relation, = excerpts
        self.assertEquals(excerpt_document, relation.to_object)

        # The relation catalog should have catalogued the new relation.
        self.assertIn(relation,
                      tuple(getUtility(ICatalog).findRelations(
                          {'to_id': relation.to_id})))

    @browsing
    def test_create_successor_proposal(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.proposal, view='tabbedview_view-overview')
        button_label = 'Create successor proposal'

        self.assertEquals('submitted', self.proposal.get_state().title)
        self.assertFalse(browser.find(button_label))

        with self.login(self.committee_responsible):
            agenda_item = self.schedule_proposal(self.meeting, self.submitted_proposal)
            self.assertEquals('scheduled', self.submitted_proposal.get_state().title)

        self.assertEquals('scheduled', self.proposal.get_state().title)
        self.assertFalse(browser.reload().find(button_label))

        with self.login(self.committee_responsible):
            self.decide_agendaitem_generate_and_return_excerpt(agenda_item, 'Excerpt')
            self.assertEquals('decided', self.submitted_proposal.get_state().title)

        self.assertEquals('decided', self.proposal.get_state().title)
        self.assertTrue(browser.reload().find(button_label))

        browser.click_on(button_label)

        self.assertEquals(
            self.proposal.Title().decode('utf-8'),
            browser.find('Title').value)
        self.assertEquals(
            str(self.proposal.get_committee().load_model().oguid),
            browser.find('Committee').value)

        expected_attachements = [rel.to_path for rel in self.proposal.relatedItems]
        expected_attachements.append(self.proposal.get_excerpt().absolute_url_path())
        self.assertItemsEqual(
            expected_attachements,
            [node.value for node in browser.find('Attachments').css('input[type=checkbox]')])

        self.assertIn(
            self.proposal.get_proposal_document().UID(),
            browser.find('Proposal template').options,
            'The proposal document of the predecessor should be selectable'
            ' as proposal template.')

        browser.fill({
            'Title': u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung',
            'Proposal template': self.proposal.get_proposal_document().Title(),
        }).save()
        statusmessages.assert_no_error_messages()

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        expected_listing = [
            ['Title', u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung'],
            ['Description', ''],
            ['Committee', u'Rechnungspr\xfcfungskommission'],
            ['Meeting', ''],
            ['Issuer', 'Ziegler Robert (robert.ziegler)'],
            ['Proposal document', u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung'],
            ['State', 'Pending'],
            ['Decision number', ''],
            ['Predecessor', u'Vertr\xe4ge'],
            ['Attachments', u'Excerpt Vertr\xe4gsentwurf'],
            ['Excerpt', ''],
        ]
        self.assertEqual(expected_listing, browser.css('table.listing').first.lists())

        browser.open(self.proposal, view='tabbedview_view-overview')
        self.assertIn(u'Successor proposal '
                      u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung '
                      u'created by Ziegler Robert (robert.ziegler)',
                      browser.css('.answers .answerBody h3').text)
        expected_listing = [
            ['Title', u'Vertr\xe4ge'],
            ['Description', u'F\xfcr weitere Bearbeitung bewilligen'],
            ['Committee', u'Rechnungspr\xfcfungskommission'],
            ['Meeting', u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['Issuer', 'Ziegler Robert (robert.ziegler)'],
            ['Proposal document', u'Vertr\xe4ge'],
            ['State', 'Decided'],
            ['Decision number', '2016 / 2'],
            ['Successors', u'\xc4nderungen am Personalreglement zur Nachpr\xfcfung'],
            ['Attachments', u'Vertr\xe4gsentwurf'],
            ['Excerpt', 'Excerpt'],
        ]
        self.assertEqual(expected_listing, browser.css('table.listing').first.lists())

    @browsing
    def test_create_protocol_approval_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        self.meeting.model.close()
        browser.open(self.meeting)

        button_label = "Create protocol approval proposal"
        browser.click_on(button_label)

        self.assertEquals(u'Approve protocol ' + self.meeting.get_title(),
                          browser.find('Title').value)

        self.assertEquals(str(self.meeting.model.committee.oguid),
                          browser.find('Committee').value)

        protocol_document = self.meeting.model.protocol_document.resolve_document()
        expected_attachements = [protocol_document.absolute_url_path()]
        self.assertItemsEqual(
            expected_attachements,
            [node.value for node in browser.find('Attachments').css('input[type=checkbox]')])

        browser.fill({
            'Proposal template': self.proposal_template.Title(),
        }).save()

        statusmessages.assert_no_error_messages()

        proposal = browser.context
        browser.open(proposal, view='tabbedview_view-overview')
        expected_listing = [
            ['Title', u'Approve protocol 9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['Description', ''],
            ['Committee', u'Rechnungspr\xfcfungskommission'],
            ['Meeting', ''],
            ['Issuer', u'M\xfcller Fr\xe4nzi (franzi.muller)'],
            ['Proposal document', u'Approve protocol 9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['State', 'Pending'],
            ['Decision number', ''],
            ['Attachments', u'Protocol-9. Sitzung der Rechnungspr\xfcfungskommission'],
            ['Excerpt', ''],
        ]
        self.assertEqual(expected_listing, browser.css('table.listing').first.lists())

    @browsing
    def test_proposal_title_is_displayed_xss_safe(self, browser):
        self.login(self.dossier_responsible, browser)
        self.proposal.title = u'<p>qux</p>'
        browser.open(self.proposal, view='tabbedview_view-overview')
        self.assertEqual('&lt;p&gt;qux&lt;/p&gt;',
                         browser.css('.listing td').first.innerHTML)

    @browsing
    def test_issuer_is_prefilled_with_the_currently_logged_in_user(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')

        field = browser.find_field_by_text('Issuer')
        self.assertEqual(self.committee_responsible.id, field.value)
        self.assertEqual(u'M\xfcller Fr\xe4nzi (franzi.muller)', field.text)

    @browsing
    def test_issuer_can_be_changed(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')

        browser.fill(
            {'Title': u'Baugesuch Kreuzachkreisel',
             'Committee': u'Rechnungspr\xfcfungskommission',
             'Proposal template': u'Geb\xfchren',
             'Edit after creation': False})

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.dossier_responsible.id)
        form.save()

        self.assertEqual(self.dossier_responsible.id, browser.context.issuer)

    @browsing
    def test_issuer_is_not_visible_on_submitted_proposal_edit_form(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.submitted_proposal, view="edit")

        self.assertIsNone(browser.find_field_by_text('Issuer'))

    @browsing
    def test_proposal_shows_native_language_names_on_form(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')
        expected_languages = ['Deutsch', 'English']
        self.assertEqual(expected_languages, browser.css('#form-widgets-language option').text)

    @browsing
    def test_add_form_does_not_list_shadow_documents_as_relatable(self, browser):
        """Dossier responsible has created the shadow document.

        This test ensures he does not get it offered as a relatable document on
        proposals.
        """
        self.login(self.dossier_responsible, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.meeting.proposal',
            '++widget++form.widgets.relatedItems',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [
            '2015',
            '2016',
            '[No Subject]',
            u'Antrag f\xfcr Kreiselbau',
            u'Die B\xfcrgschaft',
            u'Diskr\xe4te Dinge',
            u'Initialvertrag f\xfcr Bearbeitung',
            u'Initialvertrag f\xfcr Bearbeitung',
            'Personaleintritt',
            u're: Diskr\xe4te Dinge',
            u'Vertr\xe4ge',
            u'Vertr\xe4gsentwurf',
            u'Vertragsentwurf \xdcberpr\xfcfen',
            u'Vertragsentw\xfcrfe 2018',
        ]
        self.assertEqual(expected_documents, browser.css('li').text)

    @browsing
    def test_add_form_does_not_list_shadow_documents_as_proposal_documents(self, browser):
        """Dossier responsible has created the shadow document.

        This test ensures he does not get it offered as a proposal document on
        proposals.
        """
        self.login(self.dossier_responsible, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.meeting.proposal',
            '++widget++form.widgets.proposal_document',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [u'Initialvertrag f\xfcr Bearbeitung', u'Vertr\xe4gsentwurf']
        self.assertEqual(expected_documents, browser.css('li').text)

    @browsing
    def test_add_form_does_not_list_non_docx_documents_as_proposal_documents(self, browser):
        self.login(self.regular_user, browser)
        contenttree_url = '/'.join((
            self.dossier.absolute_url(),
            '++add++opengever.meeting.proposal',
            '++widget++form.widgets.proposal_document',
            '@@contenttree-fetch',
        ))
        browser.open(
            contenttree_url,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode({'href': '/'.join(self.dossier.getPhysicalPath()), 'rel': 0}),
        )
        expected_documents = [u'Initialvertrag f\xfcr Bearbeitung', u'Vertr\xe4gsentwurf']
        self.assertEqual(expected_documents, browser.css('li').text)
