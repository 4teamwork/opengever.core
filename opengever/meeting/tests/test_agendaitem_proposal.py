from ftw.testbrowser import browsing
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.meeting.model.proposal import Proposal
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashed
from plone import api
from plone.protect import createToken
from plone.protect.utils import addTokenToUrl
from plone.uuid.interfaces import IUUID


class TestProposalAgendaItem(IntegrationTestCase):

    features = (
        '!officeconnector-checkout',
        'meeting',
    )

    @browsing
    def test_decide_proposal_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        browser.open(self.agenda_item_url(agenda_item, 'decide'),
                     data={'_authenticator': createToken()})

        self.assertEquals('decided', agenda_item.workflow_state)
        self.assertEquals([{u'message': u'Agenda Item decided.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_schedule_submitted_proposal_changes_proposal_workflow_state(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_proposal)

        self.assert_workflow_state('proposal-state-scheduled', self.proposal)

    @browsing
    def test_decide_proposal_agenda_item_generates_numbers(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)

        browser.open(self.agenda_item_url(agenda_item, 'decide'),
                     data={'_authenticator': createToken()})

        self.assertEqual(2, agenda_item.decision_number)
        self.assertEqual(2, self.meeting.model.meeting_number)

    @browsing
    def test_proposal_is_decided_only_when_excerpt_is_returned(self, browser):
        self.login(self.committee_responsible, browser)
        self.assertEqual(Proposal.STATE_SUBMITTED, self.submitted_proposal.get_state())

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        self.assertEqual(Proposal.STATE_SCHEDULED, self.submitted_proposal.get_state())

        browser.open(self.agenda_item_url(agenda_item, 'decide'),
                     data={'_authenticator': createToken()})
        self.assertEqual(Proposal.STATE_SCHEDULED, self.submitted_proposal.get_state())

        browser.open(self.meeting, view='agenda_items/list')
        generate_excerpt_link = browser.json['items'][0]['generate_excerpt_link']
        browser.open(generate_excerpt_link, send_authenticator=True,
                     data={'excerpt_title': 'Excerption \xc3\x84nderungen'})
        self.assertEqual(Proposal.STATE_SCHEDULED, self.submitted_proposal.get_state())

        browser.open(self.meeting, view='agenda_items/list')
        return_excerpt_link = browser.json[u"items"][0]['excerpts'][0]['return_link']
        browser.open(return_excerpt_link, send_authenticator=True)
        self.assertEqual(Proposal.STATE_DECIDED, self.submitted_proposal.get_state())

    @browsing
    def test_delete_agenda_item_does_not_trash_proposal_document(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_proposal(
            self.meeting, self.submitted_proposal)
        document = agenda_item.resolve_document()

        browser.open(self.agenda_item_url(agenda_item, 'delete'))

        self.assertEquals([{u'message': u'Agenda Item Successfully deleted',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))
        self.assertFalse(ITrashed.providedBy(document))

    @browsing
    def test_proposal_document_in_meeting_item_data(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting,
                               self.submitted_proposal)
        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]

        document_link_html = item_data.get('document_link')
        self.assertIn(
            u'Vertr\xe4ge',
            document_link_html)
        document = self.submitted_proposal.get_proposal_document()
        self.assertIn(document.absolute_url() + '/tooltip', document_link_html)

    @browsing
    def test_edit_document_possible_when_item_proposed(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertDictContainsSubset(
            {'document_checked_out': False,
             'edit_document_button': {
                 'visible': True,
                 'active': True,
                 'url': self.agenda_item_url(agenda_item, 'edit_document')}},
            item_data)

    @browsing
    def test_edit_document_possible_when_i_have_checked_it_out(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        proposal_document = self.submitted_proposal.get_proposal_document()
        self.checkout_document(proposal_document)

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertDictContainsSubset(
            {'document_checked_out': True,
             'edit_document_button': {
                 'visible': True,
                 'active': True,
                 'url': self.agenda_item_url(agenda_item, 'edit_document')}},
            item_data)
        self.assertTrue(
            api.user.has_permission('WebDAV Lock items',
                                    obj=proposal_document),
            'Should be able to lock documents after checkout.')

    @browsing
    def test_edit_document_not_possible_when_sb_else_checked_it_out(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)

        with self.login(self.administrator):
            self.checkout_document(
                self.submitted_proposal.get_proposal_document())

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertDictContainsSubset(
            {'document_checked_out': True,
             'edit_document_button': {
                 'visible': True,
                 'active': False,
                 'url': self.agenda_item_url(agenda_item, 'edit_document')}},
            item_data)

    @browsing
    def test_edit_document_possible_when_agenda_item_in_revision(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        agenda_item.reopen()

        proposal_document = self.submitted_proposal.get_proposal_document()
        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertDictContainsSubset(
            {'document_checked_out': False,
             'edit_document_button': {
                 'visible': True,
                 'active': True,
                 'url': self.agenda_item_url(agenda_item, 'edit_document')}},
            item_data)
        self.assertTrue(
            api.user.has_permission('WebDAV Lock items',
                                    obj=proposal_document),
            'Should be able to lock documents after checkout.')

    @browsing
    def test_edit_document_checks_out_and_provides_OC_url(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        document = self.submitted_proposal.get_proposal_document()

        self.assertIsNone(self.get_checkout_manager(document).get_checked_out_by())
        browser.open(
            self.agenda_item_url(agenda_item, 'edit_document'),
            send_authenticator=True)

        self.assertEquals(
            {u'proceed': True,
             u'officeConnectorURL': u'{}/external_edit'.format(
                 document.absolute_url())},
            browser.json)
        self.assertEquals(self.committee_responsible.getId(),
                          self.get_checkout_manager(document).get_checked_out_by())
        self.assertTrue(
            api.user.has_permission('WebDAV Lock items',
                                    obj=document),
            'Should be able to lock documents after checkout.')

    @browsing
    def test_decide_agenda_item_checks_in_documents(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)

        document = self.submitted_proposal.get_proposal_document()
        self.checkout_document(document)
        self.assertEqual(self.committee_responsible.getId(),
                         self.get_checkout_manager(document).get_checked_out_by())

        proposal_model = self.submitted_proposal.load_model()
        self.assertEquals(proposal_model.STATE_SCHEDULED, proposal_model.get_state())

        browser.open(
            self.agenda_item_url(agenda_item, 'decide'),
            send_authenticator=True)
        expected_messages = {
            u'redirectUrl': u'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1',
            u'messages': [{u'messageTitle': u'Information', u'message': u'Agenda Item decided.', u'messageClass': u'info'}],
        }
        self.assertEquals(expected_messages, browser.json)

        self.assertEquals(proposal_model.STATE_SCHEDULED, proposal_model.get_state())
        self.assertIsNone(self.get_checkout_manager(document).get_checked_out_by())

    @browsing
    def test_decide_agenda_item_disallowed_when_doc_checked_out(self, browser):
        """When an agenda items' proposal document is checkout by someone else,
        deciding the document is not allowed, since the system should not
        check in the documents checked out by other users.
        """

        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)

        self.login(self.administrator, browser)
        document = self.submitted_proposal.get_proposal_document()
        self.checkout_document(document)
        self.assertEqual(self.administrator.getId(),
                         self.get_checkout_manager(document).get_checked_out_by())

        self.login(self.committee_responsible, browser)
        proposal_model = self.submitted_proposal.load_model()
        self.assertEquals(proposal_model.STATE_SCHEDULED, proposal_model.get_state())

        browser.open(
            self.agenda_item_url(agenda_item, 'decide'),
            send_authenticator=True)
        expected_messages = {
            u'messages': [{
                u'messageTitle': u'Error',
                u'message': u'Cannot decide agenda item: someone else has checked out the document.',
                u'messageClass': u'error',
            }],
            u'proceed': False,
        }
        self.assertEquals(expected_messages, browser.json)

        self.assertEquals(proposal_model.STATE_SCHEDULED, proposal_model.get_state())
        self.assertEqual(self.administrator.getId(),
                         self.get_checkout_manager(document).get_checked_out_by())

    @browsing
    def test_create_excerpt(self, browser):
        """When creating an excerpt of an agenda item, it should copy the
        proposal document into the meeting dossier for further editing.
        """
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        self.assertEquals(self.meeting.model.STATE_HELD,
                          self.meeting.model.get_state())

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]

        # The generate excerpt link is available on decided agenda items.
        self.assertDictContainsSubset(
            {'generate_excerpt_link': self.agenda_item_url(agenda_item, 'generate_excerpt'),
             'generate_excerpt_default_title': u'Excerpt Vertr\xe4ge'},
            item_data)

        # Create an excerpt.
        with self.observe_children(self.meeting_dossier) as children:
            browser.open(
                item_data['generate_excerpt_link'],
                data={'excerpt_title': 'Excerption \xc3\x84nderungen'},
                send_authenticator=True)

        # Generating the excerpt is confirmed with a status message.
        self.assertEquals(
            {u'proceed': True,
             u'messages': [
                 {u'messageTitle': u'Information',
                  u'message': u'Excerpt was created successfully.',
                  u'messageClass': u'info'}]},
            browser.json)

        # The excerpt was created in the meeting dossier and contains the exact
        # original document.
        self.assertEquals(1, len(children['added']))
        excerpt_document, = children['added']
        self.assertEquals('Excerption \xc3\x84nderungen',
                          excerpt_document.Title())
        self.assertIsInstance(excerpt_document.title, unicode)
        self.assertIsNotNone(excerpt_document.file.data)
        self.assertEquals(u'Excerption Aenderungen.docx',
                          excerpt_document.file.filename)

    @browsing
    def test_cannot_create_excerpt_when_meeting_closed(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        self.decide_agendaitem_generate_and_return_excerpt(agenda_item)
        self.meeting.model.execute_transition('held-closed')
        self.assertEquals(self.meeting.model.STATE_CLOSED,
                          self.meeting.model.get_state())

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'generate_excerpt'))

    @browsing
    def test_cannot_create_excerpt_when_item_not_decided(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        with browser.expect_http_error(code=403):
            browser.open(
                self.agenda_item_url(agenda_item, 'generate_excerpt'),
                data={'excerpt_title': u'foo'})

    @browsing
    def test_error_when_no_access_to_meeting_dossier(self, browser):
        with self.login(self.administrator):
            RoleAssignmentManager(self.committee_container).add_or_update_assignment(
                SharingRoleAssignment(self.regular_user.getId(), ['Reader']))
            RoleAssignmentManager(self.committee).add_or_update_assignment(
                SharingRoleAssignment(self.regular_user.getId(),
                                      ['CommitteeResponsible', 'Editor']))

            # Let regular_user have no access to meeting_dossier
            self.meeting_dossier.__ac_local_roles_block__ = True

            agenda_item = self.schedule_proposal(self.meeting,
                                                 self.submitted_proposal)
            agenda_item.decide()

        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            browser.open(
                self.agenda_item_url(agenda_item, 'generate_excerpt'),
                data={'excerpt_title': 'Excerption \xc3\x84nderungen'})
            expected_messages = {
                u'messages': [{
                    u'messageTitle': u'Error',
                    u'message': u'Insufficient privileges to add a document to the meeting dossier.',
                    u'messageClass': u'error',
                }],
            }
            self.assertEquals(expected_messages, browser.json)

    @browsing
    def test_excerpts_listed_in_meeting_item_data(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertFalse(item_data.get('excerpts'))

        excerpt = agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')
        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        excerpt_links = item_data.get('excerpts', None)

        self.assertEquals(1, len(excerpt_links))
        self.assertIn(
            'href="{}"'.format(excerpt.absolute_url()),
            excerpt_links[0]['link'])

    @browsing
    def test_decision_number_in_meeting_item_data(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)

        browser.open(self.meeting, view='agenda_items/list')
        self.assertDictContainsSubset(
            {'title': u'Vertr&auml;ge',
             'decision_number': None},
            browser.json['items'][0])

        agenda_item.decide()
        browser.reload()
        self.assertDictContainsSubset(
            {'title': u'Vertr&auml;ge',
             'decision_number': '2016 / 2'},
            browser.json['items'][0])

    @browsing
    def test_can_return_excerpts_to_proposer(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        excerpt = agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')

        self.assertIsNone(agenda_item.proposal.excerpt_document)
        self.assertIsNone(agenda_item.proposal.submitted_excerpt_document)

        # temporarily block access to dossier
        self.dossier.__ac_local_roles_block__ = True
        with browser.expect_unauthorized():
            browser.open(self.dossier)

        return_excerpt_url = addTokenToUrl(self.meeting.model.get_url(
            view='agenda_items/{}/return_excerpt?document={}'.format(
                agenda_item.agenda_item_id, IUUID(excerpt))))

        browser.open(return_excerpt_url)
        self.assertEqual(
            u'Excerpt was returned to proposer.',
            browser.json['messages'][0]['message'])

        self.assertIsNotNone(agenda_item.proposal.excerpt_document)
        self.assertIsNotNone(agenda_item.proposal.submitted_excerpt_document)
        self.assertEqual(
            excerpt,
            agenda_item.proposal.submitted_excerpt_document.resolve_document())

    @browsing
    def test_agenda_item_create_task_url(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        excerpt_doc = agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')
        browser.open(self.meeting, view='agenda_items/list')
        agenda_item_data = browser.json['items'][0]
        excerpt_data = agenda_item_data['excerpts'][0]

        expected_url = (
            self.meeting_dossier.absolute_url() +
            '/++add++opengever.task.task?paths:list=' +
            '/'.join(excerpt_doc.getPhysicalPath()) +
            '&_authenticator=........')

        self.assertEquals(
            expected_url.split('&_authenticator')[0],
            excerpt_data['create_task_url'].split('&_authenticator')[0])

    @browsing
    def test_agendaitem_with_excerpts_has_documents(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_proposal(self.meeting,
                                             self.submitted_proposal)
        agenda_item.decide()
        agenda_item.generate_excerpt(title='Excerpt \xc3\x84nderungen')

        browser.open(self.meeting, view='agenda_items/list')
        agenda_item_data = browser.json['items'][0]
        self.assertTrue(agenda_item_data.get('has_documents'))
