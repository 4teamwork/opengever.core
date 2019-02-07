from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.meeting.tests.pages import meeting_view
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline
from plone import api
import pytz


class TestMeetingView(IntegrationTestCase):
    features = ('meeting',)

    @browsing
    def test_displays_correct_edit_bar_actions(self, browser):
        expected_menu = ['Export as Zip', 'Properties', 'Close meeting', 'Cancel']
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        self.assertEquals(expected_menu, editbar.menu_options('Actions'))

    @browsing
    def test_displays_correct_edit_bar_actions_for_manager(self, browser):
        expected_menu = ['Debug docxcompose', 'Download protocol json',
                         'Export as Zip', 'Properties', 'Sharing',
                         'Policy...', 'Close meeting', 'Cancel']
        self.login(self.manager, browser)
        browser.open(self.meeting)

        self.assertItemsEqual(expected_menu, editbar.menu_options('Actions'))

    @browsing
    def test_meeting_metadata_is_visible(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)

        self.maxDiff = None
        self.assertEquals(
            [('State:', 'Pending'),
             ('Start:', 'Sep 12, 2016 05:30 PM'),
             ('End:', 'Sep 12, 2016 07:00 PM'),
             ('Presidency:', u'Sch\xf6ller Heidrun'),
             ('Secretary:', u'Secretary C\xf6mmittee'),
             ('Location:', u'B\xfcren an der Aare'),
             ('Meeting dossier:', 'Sitzungsdossier 9/2017')],
            byline.text_items())

    @browsing
    def test_meeting_dossier_link(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        browser.click_on('Sitzungsdossier 9/2017')
        self.assertEquals(self.meeting_dossier.absolute_url(), browser.url)

    @browsing
    def test_agenda_items_list_document(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting)
        docnode = browser.css('.meeting-document.agenda-item-list-doc').first
        self.assertFalse(docnode.css('div.document-label a'))
        self.assertEquals('Agenda item list', docnode.css('.document-label').first.text)
        self.assertEquals('Not yet generated.', docnode.css('.document-modified').first.text)
        self.assertTrue(docnode.css('.action.generate'))
        self.assertFalse(docnode.css('.action.download'))

        with freeze(datetime(2016, 9, 2, 10, 15, 1, tzinfo=pytz.UTC)) as clock:
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.agenda-item-list-doc').first
            self.assertTrue(docnode.css('div.document-label a'))
            self.assertEquals('Agenda item list', docnode.css('.document-label').first.text)
            self.assertEquals('Modified at Sep 02, 2016 12:15 PM', docnode.css('.document-modified').first.text)
            self.assertTrue(docnode.css('.action.generate'))
            self.assertTrue(docnode.css('.action.download'))

            self.assertEquals(self.meeting.model.agendaitem_list_document.get_download_url(),
                              docnode.css('.action.download').first.attrib['href'])

            clock.forward(hours=1)
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.agenda-item-list-doc').first
            self.assertEquals('Modified at Sep 02, 2016 01:15 PM', docnode.css('.document-modified').first.text)

    @browsing
    def test_protocol_document(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.meeting)
        docnode = browser.css('.meeting-document.protocol-doc').first
        self.assertFalse(docnode.css('div.document-label a'))
        self.assertEquals('Pre-protocol', docnode.css('.document-label').first.text)
        self.assertEquals('Not yet generated.', docnode.css('.document-modified').first.text)
        self.assertTrue(docnode.css('.action.generate'))
        self.assertFalse(docnode.css('.action.download'))

        with freeze(datetime(2016, 9, 2, 10, 15, 1, tzinfo=pytz.UTC)) as clock:
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.protocol-doc').first
            self.assertTrue(docnode.css('div.document-label a'))
            self.assertEquals('Pre-protocol', docnode.css('.document-label').first.text)
            self.assertEquals('Modified at Sep 02, 2016 12:15 PM', docnode.css('.document-modified').first.text)
            self.assertTrue(docnode.css('.action.generate'))
            self.assertTrue(docnode.css('.action.download'))

            self.assertEquals(self.meeting.model.protocol_document.get_download_url(),
                              docnode.css('.action.download').first.attrib['href'])

            clock.forward(hours=1)
            docnode.css('.action.generate').first.click()
            docnode = browser.css('.meeting-document.protocol-doc').first
            self.assertEquals('Modified at Sep 02, 2016 01:15 PM', docnode.css('.document-modified').first.text)

            self.meeting.model.workflow_state = self.meeting.model.STATE_HELD.name
            browser.reload()
            docnode = browser.css('.meeting-document.protocol-doc').first
            self.assertEquals('Protocol', docnode.css('.document-label').first.text)

    @browsing
    def test_close_transition_closes_meeting(self, browser):
        self.login(self.committee_responsible, browser)
        self.assertEquals('pending', self.meeting.model.get_state().name)
        browser.open(self.meeting)
        editbar.menu_option('Actions', 'Close meeting').click()
        self.assertEquals('closed', self.meeting.model.get_state().name)

    @browsing
    def test_meeting_member_cannot_return_excerpt(self, browser):
        with self.login(self.committee_responsible, browser):
            agenda_item = self.schedule_proposal(self.meeting,
                                                 self.submitted_proposal)
            agenda_item.decide()
            agenda_item.generate_excerpt(title='The Excerpt')
            browser.open(self.meeting, view='agenda_items/list')
            self.assertIn('return_link', browser.json['items'][0]['excerpts'][0])

        self.login(self.meeting_user, browser)
        browser.open(self.meeting, view='agenda_items/list')
        self.assertNotIn('return_link', browser.json['items'][0]['excerpts'][0])

    @browsing
    def test_participants(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertEquals(
            [{'fullname': u'Sch\xf6ller Heidrun', 'role': 'Presidency', 'email': '', 'present': False},
             {'fullname': 'Wendler Jens', 'role': '', 'email': '', 'present': True},
             {'fullname': u'W\xf6lfl Gerda', 'role': '', 'email': '', 'present': True}],
            meeting_view.participants())

    def test_get_closing_infos(self):
        """The get_close_meeting_render_infos provides infos for rendering.

        Components:
        - Disabled close-meeting transition action (when not yet ready).
        - Enabled close-meeting transition action.
        - Repoen-meeting transition action.
        """

        self.maxDiff = None
        self.login(self.committee_responsible)
        view = self.meeting.restrictedTraverse('view')

        self.assertEquals(
            {'is_closed': False,
             'close_url': self.get_meeting_transition_url('pending-closed'),
             'cancel_url': self.get_meeting_transition_url('pending-cancelled'),
             'reopen_url': None},
            view.get_closing_infos())

        self.meeting.model.workflow_state = self.meeting.model.STATE_HELD.name
        self.assertEquals(
            {'is_closed': False,
             'close_url': self.get_meeting_transition_url('held-closed'),
             'cancel_url': None,
             'reopen_url': None},
            view.get_closing_infos())

        self.meeting.model.workflow_state = self.meeting.model.STATE_CLOSED.name
        self.assertEquals(
            {'is_closed': True,
             'close_url': None,
             'cancel_url': None,
             'reopen_url': self.get_meeting_transition_url('closed-held')},
            view.get_closing_infos())

    @browsing
    def test_zip_export_is_available_for_committee_member(self, browser):
        self.login(self.meeting_user, browser=browser)
        browser.open(self.meeting, view='export-meeting-zip')

        self.assertEquals('application/zip', browser.headers.get('content-type'))
        self.assertEquals(
            'attachment; filename="9. Sitzung der Rechnungsprufungskommission.zip"',
            browser.headers.get('content-disposition'))

    def get_meeting_transition_url(self, transition_name):
        transition_controller = self.meeting.model.workflow.transition_controller
        return transition_controller.url_for(self.meeting,
                                             self.meeting.model,
                                             transition_name)

    @browsing
    def test_all_proposal_templates_are_listed(self, browser):
        self.login(self.committee_responsible, browser=browser)
        browser.open(self.meeting)
        self.assertEquals(
            [{'': '',
              'Zuletzt bearbeitet': '31.08.2016',
              'Titel': 'Freitext Traktandum',
              'Ersteller': 'nicole.kohler'},
             {'': '',
              'Zuletzt bearbeitet': '31.08.2016',
              'Titel': u'Geb\xfchren',
              'Ersteller': 'nicole.kohler'},
             {'': '',
              'Zuletzt bearbeitet': '31.08.2016',
              'Titel': 'Wiederkehrendes Traktandum',
              'Ersteller': 'nicole.kohler'}],
            browser.css('#ad-hoc-agenda-item-proposal-templates').first.dicts()
        )

    @browsing
    def test_default_template_is_checked(self, browser):
        self.login(self.committee_responsible, browser=browser)
        browser.open(self.meeting)
        selected_templates = [
            template
            for template in browser.css('#ad-hoc-agenda-item-proposal-templates input[name=selected_ad_hoc_agenda_item_template]')
            if template.checked
        ]
        assert 1 == len(selected_templates)
        selected_template_id = selected_templates[0].value
        self.assertEquals(self.committee.get_ad_hoc_template().getId(),
                          selected_template_id)

    @browsing
    def test_no_options_displayed_if_only_one_ad_hoc_template_available(self, browser):
        self.login(self.committee_responsible, browser=browser)
        self.assertFalse(self.committee.allowed_ad_hoc_agenda_item_templates)

        browser.open(self.committee, view='edit')
        browser.fill({'Allowed ad-hoc agenda item templates': u'Geb\xfchren'}).save()
        statusmessages.assert_no_error_messages()

        browser.open(self.meeting)
        self.assertEquals(
            0,
            len(browser.css('#ad-hoc-agenda-item-proposal-templates')))

    @browsing
    def test_displays_error_view_when_no_view_permissions_on_meeting_dossier(self, browser):
        self.login(self.meeting_user, browser=browser)

        browser.open(self.meeting)
        self.assertEqual(0, len(browser.css(".meeting-permission-error-title")))
        self.assertFalse(0, len(browser.css(".meeting-permission-error-error")))

        api.content.disable_roles_acquisition(self.meeting_dossier)

        browser.open(self.meeting)
        self.assertEqual(browser.css(".meeting-permission-error-title").first.text,
                         'Insufficient privileges on meeting dossier')
        self.assertEqual(browser.css(".meeting-permission-error-message").first.text,
                         'User does not have permission to view the meeting dossier:')

    @browsing
    def test_displays_error_view_when_no_edit_permissions_on_meeting_dossier(self, browser):
        self.login(self.committee_responsible, browser=browser)

        browser.open(self.meeting)
        self.assertEqual(0, len(browser.css(".meeting-permission-error-title")))
        self.assertFalse(0, len(browser.css(".meeting-permission-error-error")))

        api.content.disable_roles_acquisition(self.meeting_dossier)

        browser.open(self.meeting)
        self.assertEqual(browser.css(".meeting-permission-error-title").first.text,
                         'Insufficient privileges on meeting dossier')
        self.assertEqual(browser.css(".meeting-permission-error-message").first.text,
                         'User does not have permission to edit the meeting dossier:')
