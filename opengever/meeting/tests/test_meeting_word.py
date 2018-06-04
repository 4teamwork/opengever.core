from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import localized_datetime
from pyquery import PyQuery


ZIP_EXPORT_ACTION_LABEL = 'Export as Zip'


class TestWordMeeting(IntegrationTestCase):
    features = ('meeting',)

    @browsing
    def test_add_meeting_and_dossier(self, browser):
        self.login(self.committee_responsible, browser)
        committee_model = self.committee.load_model()
        previous_meetings = len(committee_model.meetings)

        # create meeting
        browser.open(self.committee, view='add-meeting')
        browser.fill({
            'Title': u'M\xe4\xe4hting',
            'Start': '01.01.2010 10:00',
            'End': '01.01.2010 11:00',
            'Location': 'Somewhere',
        }).submit()

        # create dossier
        browser.find('Save').click()

        # back to meeting page
        self.assertEqual(
            [u'The meeting and its dossier were created successfully'],
            info_messages())

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1#meetings',
            browser.url)

        committee_model = self.committee.load_model()
        self.assertEqual(previous_meetings + 1, len(committee_model.meetings))
        meeting = committee_model.meetings[-1]

        self.assertEqual(localized_datetime(2010, 1, 1, 10), meeting.start)
        self.assertEqual(localized_datetime(2010, 1, 1, 11), meeting.end)
        self.assertEqual('Somewhere', meeting.location)
        dossier = meeting.dossier_oguid.resolve_object()
        self.assertIsNotNone(dossier)
        self.assertEquals(u'M\xe4\xe4hting', dossier.title)
        self.assertIsNotNone(meeting.modified)

    @browsing
    def test_meeting_title_is_used_as_site_title_and_heading(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting.absolute_url())

        self.assertEquals(
            [u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            browser.css('h1').text)
        self.assertEquals(
            u'9. Sitzung der Rechnungspr\xfcfungskommission \u2014 Plone site',
            browser.css('title').first.text)

    @browsing
    def test_regression_add_meeting_without_end_date_does_not_fail(self, browser):
        self.login(self.committee_responsible, browser)
        committee_model = self.committee.load_model()
        previous_meetings = len(committee_model.meetings)

        # create meeting
        browser.open(self.committee, view='add-meeting')
        browser.fill({
            'Start': '01.01.2010 10:00',
            'End': '',
            'Location': u'B\xe4rn',
        }).submit()
        # create dossier
        browser.find('Save').click()

        committee_model = self.committee.load_model()
        self.assertEqual(previous_meetings + 1, len(committee_model.meetings))
        meeting = committee_model.meetings[-1]
        self.assertIsNone(meeting.end)

    def test_meeting_link(self):
        self.login(self.committee_responsible)

        link = PyQuery(self.meeting.model.get_link())[0]

        self.assertEqual(
            'http://nohost/plone/opengever-meeting-committeecontainer/committee-1/meeting-1/view',
            link.get('href'))
        self.assertEqual('contenttype-opengever-meeting-meeting', link.get('class'))
        self.assertEqual(u'9. Sitzung der Rechnungspr\xfcfungskommission',
                         link.get('title'))
        self.assertEqual(u'9. Sitzung der Rechnungspr\xfcfungskommission',
                         link.text)

    @browsing
    def test_zipexport_action_in_action_menu(self, browser):
        """When the word-meeting feature is enabled, the zipexport action is
        available in Plone's actions menu.
        """
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertIn(ZIP_EXPORT_ACTION_LABEL, editbar.menu_options('Actions'))

    @browsing
    def test_zipexport_action_not_available_on_non_meeting_content(self, browser):
        """The zipexport action should not be available on non-meeting content.
        If it does appear, it might by another action with the same name.
        """
        self.login(self.manager, browser)
        browser.open(self.committee)
        self.assertNotIn(ZIP_EXPORT_ACTION_LABEL, editbar.menu_options('Actions'))

    @browsing
    def test_cancel_meeting(self, browser):
        self.login(self.committee_responsible, browser)
        self.assertEquals(u'pending', self.meeting.model.workflow_state)
        browser.open(self.meeting)
        editbar.menu_option('Actions', 'Cancel').click()

        self.assertEquals(u'cancelled', self.meeting.model.workflow_state)

    @browsing
    def test_meeting_with_agenda_items_cannot_be_cancelled(self, browser):
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        browser.open(self.meeting)
        editbar.menu_option('Actions', 'Cancel').click()

        self.assertDictContainsSubset({
            'message': "The meeting already has agenda items and can't "
                       "be cancelled",
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_reopen_closed_meeting(self, browser):
        self.login(self.committee_responsible, browser)
        self.assertEquals(u'closed', self.decided_meeting.model.workflow_state)
        browser.open(self.decided_meeting)
        editbar.menu_option('Actions', 'Reopen').click()
        self.assertEquals(u'held', self.decided_meeting.model.workflow_state)

    @browsing
    def test_closing_meeting_the_first_time_regenerates_the_protocol(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.meeting.model
        # Make sure there is already a protocol generated:
        model.update_protocol_document()
        self.assertEquals(0, model.protocol_document.generated_version)

        # When closing the meeting, we should end up with a new version
        browser.open(self.meeting)
        self.assertEquals(
            ['Closing the meeting the first time will automatically'
             ' (re-)create the protocol.',
             'Are you sure you want to close this meeting?'],
            browser.css('#confirm_close_meeting p').text)
        model.close()
        self.assertEquals(1, model.protocol_document.generated_version)
        self.assertEquals(u'closed', model.workflow_state)

    @browsing
    def test_re_closing_meeting_regenerates_the_protocol(self, browser):
        self.login(self.committee_responsible, browser)
        model = self.meeting.model
        # Closing the meeting generates and unlocks the protocol:
        model.close()
        self.assertEquals(0, model.protocol_document.generated_version)

        # The user may have made changes to the protocol now.
        # Reopen the protocol:
        model.execute_transition('closed-held')
        self.assertEquals(0, model.protocol_document.generated_version)

        # Re-closing the meeting must not regenerate the protocol because
        # it would potentially overwrite user-changes.
        browser.open(self.meeting)
        self.assertEquals(
            ['Closing the meeting will not update the protocol automatically.'
             '\nMake sure to transfer your changes or recreate the protocol.',
             'Are you sure you want to close this meeting?'],
            browser.css('#confirm_close_meeting p').text)
        model.close()
        self.assertEquals(0, model.protocol_document.generated_version)

    @browsing
    def test_closing_meeting_with_undecided_items_is_not_allowed(self, browser):
        """The user must decide all agenda items before the meeting can be closed.
        """
        self.login(self.committee_responsible, browser)
        self.schedule_proposal(self.meeting, self.submitted_word_proposal)
        self.assertEquals(u'pending', self.meeting.model.workflow_state)

        browser.open(self.meeting)
        editbar.menu_option('Actions', 'Close meeting').click()
        self.assertEquals(
            {u'messages': [
                {u'messageTitle': u'Error',
                 u'message': u'The meeting cannot be closed because it'
                 u' has undecided agenda items.',
                 u'messageClass': u'error'}],
             u'proceed': False},
            browser.json)

        self.assertEquals(u'pending', self.meeting.model.workflow_state)

    def test_is_editable_for_pending_meeting(self):
        with self.login(self.administrator):
            meeting = self.meeting.model
            self.assertEquals('pending', meeting.get_state().title)
            self.assertTrue(meeting.is_editable())

        with self.login(self.committee_responsible):
            self.assertTrue(meeting.is_editable())

        with self.login(self.meeting_user):
            self.assertFalse(meeting.is_editable())

    def test_is_editable_for_decided_meeting(self):
        with self.login(self.administrator):
            meeting = self.decided_meeting.model
            self.assertEquals('closed', meeting.get_state().title)
            self.assertFalse(meeting.is_editable())

        with self.login(self.committee_responsible):
            self.assertFalse(meeting.is_editable())

        with self.login(self.meeting_user):
            self.assertFalse(
                meeting.is_editable())

    def test_get_undecided_agenda_items(self):
        self.login(self.committee_responsible)
        meeting = self.meeting.model
        self.schedule_paragraph(meeting, u'A-Gesch\xe4fte')
        item1 = self.schedule_proposal(meeting, self.submitted_word_proposal)
        item2 = self.schedule_ad_hoc(meeting, u'Ad-Hoc Agenda Item')

        self.assertEquals([item1, item2], meeting.get_undecided_agenda_items())
        item1.decide()
        self.assertEquals([item2], meeting.get_undecided_agenda_items())
        item2.decide()
        self.assertEquals([], meeting.get_undecided_agenda_items())
