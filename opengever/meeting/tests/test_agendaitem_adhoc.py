from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from plone.protect import createToken


class TestWordAgendaItem(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

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
            u'Ad hoc agenda item R\xfccktritt',
            document_link_html)
        self.assertIn(
            ad_hoc_document.absolute_url() + '/tooltip',
            document_link_html)

    @browsing
    def test_cant_create_adhoc_when_no_access_to_meeting_dossier(self, browser):
        with self.login(self.administrator):
            # Let committee_responsible have no access to meeting_dossier
            self.meeting_dossier.__ac_local_roles_block__ = True
            self.meeting_dossier.reindexObjectSecurity()

        self.login(self.committee_responsible, browser)
        browser.open(self.meeting, view='agenda_items/schedule_text',
                     data={'title': u'Fail',
                           '_authenticator': createToken()})
        self.assertEquals(
            {u'messages': [
                {u'messageTitle': u'Error',
                 u'message': u'Insufficient privileges to add a document '
                              'to the meeting dossier.',
                 u'messageClass': u'error'}],
             u'proceed': False},
            browser.json)

    @browsing
    def test_edit_ad_hoc_document_possible_when_scheduled(self, browser):
        self.login(self.committee_responsible, browser)

        agenda_item = self.meeting.model.schedule_ad_hoc(u'ad-hoc')

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
        agenda_item = self.meeting.model.schedule_ad_hoc(u'ad-hoc')

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
        agenda_item = self.meeting.model.schedule_ad_hoc(u'ad-hoc')

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
    def test_decision_number_for_adhoc_agenda_item(self, browser):
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

        browser.open(browser.json['items'][0]['decide_link'])
        browser.open(self.meeting, view='agenda_items/list')
        self.assertDictContainsSubset(
            {'title': u'Tisch Traktandum',
             'decision_number': 1},
            browser.json['items'][0])
