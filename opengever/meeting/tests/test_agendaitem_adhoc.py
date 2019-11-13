from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from opengever.trash.trash import ITrashed
from plone import api
from plone.protect import createToken
import pytz


class TestAdHocAgendaItem(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_decide_ad_hoc_agenda_item(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, 'Gugus')

        browser.open(self.agenda_item_url(agenda_item, 'decide'),
                     data={'_authenticator': createToken()})

        self.assertEquals('decided', agenda_item.workflow_state)
        self.assertEquals([{u'message': u'Agenda Item decided.',
                            u'messageClass': u'info',
                            u'messageTitle': u'Information'}],
                          browser.json.get('messages'))

    @browsing
    def test_decide_ad_hoc_agenda_item_generates_numbers(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, 'Gugus')

        browser.open(self.agenda_item_url(agenda_item, 'decide'),
                     data={'_authenticator': createToken()})

        self.assertEqual(2, agenda_item.decision_number)
        self.assertEqual(2, self.meeting.model.meeting_number)

    @browsing
    def test_ad_hoc_document_is_created_from_template(self, browser):
        self.login(self.committee_responsible, browser)

        with self.observe_children(self.meeting_dossier) as children:
            self.schedule_ad_hoc(self.meeting, u'R\xfccktritt')

        self.assertEqual(1, len(children['added']))
        ad_hoc_document = children['added'].pop()

        self.assertEqual(
            ad_hoc_document.file.data,
            self.proposal_template.file.data,
            "Expected agenda item document to be a copy of proposal template.")

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]

        document_link_html = item_data.get('document_link')
        self.assertIn(
            u'R\xfccktritt',
            document_link_html)
        self.assertIn(
            ad_hoc_document.absolute_url() + '/tooltip',
            document_link_html)

    @browsing
    def test_document_is_trashed_when_ad_hoc_agenda_item_is_deleted(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')
        document = agenda_item.resolve_document()

        browser.open(
            self.meeting,
            view='agenda_items/{}/delete'.format(agenda_item.agenda_item_id),
            send_authenticator=True)

        self.assertTrue(ITrashed.providedBy(document))

    @browsing
    def test_cant_create_adhoc_when_no_access_to_meeting_dossier(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='agenda_items/schedule_text',
                     data={'title': u'Fail',
                           '_authenticator': createToken()})
        self.assertEquals(
            {u'messages': [
                {u'messageTitle': u'Information',
                 u'message': u'Text successfully added.',
                 u'messageClass': u'info'}],
             u'proceed': True},
            browser.json)

        with self.login(self.administrator):
            # Let committee_responsible have no access to meeting_dossier
            self.meeting_dossier.__ac_local_roles_block__ = True
            self.meeting_dossier.reindexObjectSecurity()

        self.login(self.committee_responsible, browser)
        with browser.expect_http_error(code=403):
            browser.open(self.meeting, view='agenda_items/schedule_text',
                         data={'title': u'Fail',
                               '_authenticator': createToken()})
            self.assertEquals(
                {u'messages': [
                    {u'messageTitle': u'Error',
                     u'message': u'Insufficient privileges to add a document '
                                  'to the meeting dossier.',
                     u'messageClass': u'error'}]},
                browser.json)

    @browsing
    def test_edit_ad_hoc_document_possible_when_scheduled(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')

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
    def test_edit_ad_hoc_document_possible_when_i_have_checked_it_out(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')

        document = agenda_item.resolve_document()
        self.checkout_document(document)

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
            api.user.has_permission('WebDAV Lock items', obj=document),
            'Should be able to lock documents after checkout.')

    @browsing
    def test_edit_ad_hoc_document_not_possible_when_sb_else_checked_it_out(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')

        with self.login(self.administrator):
            self.checkout_document(agenda_item.resolve_document())

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
    def test_schedule_adhoc_agenda_item(self, browser):
        with freeze(datetime(2016, 10, 16, 0, 0, tzinfo=pytz.utc)):
            self.login(self.committee_responsible, browser)
            browser.open(self.meeting, view='agenda_items/schedule_text',
                         data={'title': u'Tisch Traktandum',
                               '_authenticator': createToken()})
            self.assertDictContainsSubset({'proceed': True}, browser.json)

            browser.open(self.meeting, view='agenda_items/list')
            self.assertDictContainsSubset(
                {'title': u'Tisch Traktandum',
                 'decision_number': None},
                browser.json['items'][0])

    @browsing
    def test_decision_number_for_adhoc_agenda_item(self, browser):
        with freeze(datetime(2016, 10, 16, 0, 0, tzinfo=pytz.utc)):
            self.login(self.committee_responsible, browser)
            agenda_item = self.schedule_ad_hoc(self.meeting, u'Tisch Traktandum')

            browser.open(self.meeting, view='agenda_items/list')
            self.assertDictContainsSubset(
                {'title': u'Tisch Traktandum',
                 'decision_number': None},
                browser.json['items'][0])

            browser.open(browser.json['items'][0]['decide_link'])
            browser.open(self.meeting, view='agenda_items/list')

            self.assertEqual(u'2016 / 2', agenda_item.get_decision_number())

    @browsing
    def test_create_ad_hoc_agenda_item_excerpt(self, browser):
        """When creating an excerpt of an agenda item, it should copy the
        proposal document into the meeting dossier for further editing.
        """
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')
        agenda_item.decide()

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][-1]

        # The generate excerpt link is available on decided agenda items.
        self.assertDictContainsSubset(
            {'generate_excerpt_link':
             self.agenda_item_url(agenda_item, 'generate_excerpt')},
            item_data)

        # Create an excerpt.
        with self.observe_children(self.meeting_dossier) as children:
            browser.open(
                item_data['generate_excerpt_link'],
                data={'excerpt_title': u'Excerpt ad-hoc'},
                send_authenticator=True)

        # Generating the excerpt is confirmed with a status message.
        self.assertEquals(
            {u'proceed': True,
             u'messages': [
                 {u'messageTitle': u'Information',
                  u'message': u'Excerpt was created successfully.',
                  u'messageClass': u'info'}]},
            browser.json)

        # The excerpt was created in the meeting dossier
        self.assertEquals(1, len(children['added']))
        excerpt_document, = children['added']
        self.assertEquals(u'Excerpt ad-hoc', excerpt_document.Title())

    @browsing
    def test_cannot_create_ad_hoc_excerpt_when_meeting_closed(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')
        agenda_item.decide()
        self.meeting.model.execute_transition('held-closed')
        self.assertEquals(self.meeting.model.STATE_CLOSED,
                          self.meeting.model.get_state())

        with browser.expect_http_error(code=403):
            browser.open(self.agenda_item_url(agenda_item, 'generate_excerpt'))

    @browsing
    def test_cannot_create_excerpt_when_item_not_decided(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')

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

            agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')
            agenda_item.decide()

        self.login(self.regular_user, browser)
        with browser.expect_http_error(code=403):
            browser.open(
                self.agenda_item_url(agenda_item, 'generate_excerpt'),
                data={'excerpt_title': 'Excerption \xc3\x84nderungen'})
            self.assertEquals(
                {u'messages': [
                    {u'messageTitle': u'Error',
                     u'message': u'Insufficient privileges to add a document '
                     u'to the meeting dossier.',
                     u'messageClass': u'error'}]},
                browser.json)

    @browsing
    def test_excerpts_listed_in_meeting_ad_hoc_item_data(self, browser):
        self.login(self.committee_responsible, browser)
        agenda_item = self.schedule_ad_hoc(self.meeting, u'ad-hoc')
        agenda_item.decide()

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        self.assertFalse(item_data.get('excerpts'))

        excerpt = agenda_item.generate_excerpt(title=u'Excerpt ad-hoc')

        browser.open(self.meeting, view='agenda_items/list')
        item_data = browser.json['items'][0]
        excerpt_links = item_data.get('excerpts', None)

        self.assertEquals(1, len(excerpt_links))
        self.assertIn(
            'href="{}"'.format(excerpt.absolute_url()),
            excerpt_links[0]['link'])
