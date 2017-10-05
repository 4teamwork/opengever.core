from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.testing import IntegrationTestCase


ZIP_EXPORT_ACTION_LABEL = 'Export as Zip'


class TestWordMeeting(IntegrationTestCase):
    features = ('meeting', 'word-meeting')

    @browsing
    def test_excerpts_section_no_longer_in_sidebar(self, browser):
        """The sablon-based excerpts no longer work with word files.
        Therefore the word-meeting feature flag should remove the excerpt
        generation section from the metadata sidebar in the meeting view.
        """
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertFalse(browser.css('.sidebar .excerpts'))

    @browsing
    def test_zipexport_action_in_action_menu(self, browser):
        """When the word-meeting feature is enabled, the zipexport action is
        available in Plone's actions menu.
        """
        self.login(self.committee_responsible, browser)
        browser.open(self.meeting)
        self.assertIn(ZIP_EXPORT_ACTION_LABEL, editbar.menu_options('Actions'))

    @browsing
    def test_zipexport_action_not_in_action_menu_without_word_feature(self, browser):
        """The zipexport action should not be available in the actions menu
        when the word-meeting feature is not enabled.
        In this case the action is available in the sidebar.
        """
        self.deactivate_feature('word-meeting')
        self.login(self.manager, browser)
        browser.open(self.meeting)
        self.assertNotIn(ZIP_EXPORT_ACTION_LABEL, editbar.menu_options('Actions'))

    @browsing
    def test_zipexport_action_not_available_on_non_meeting_content(self, browser):
        """The zipexport action should not be available on non-meeting content.
        If it does appear, it might by another action with the same name.
        """
        self.login(self.manager, browser)
        browser.open(self.committee)
        self.assertNotIn(ZIP_EXPORT_ACTION_LABEL, editbar.menu_options('Actions'))

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
            [
                'Close all proposals.',
                'Generate excerpts for all proposals.',
                'Update or create the protocol.',
            ],
            browser.css('#confirm_close_meeting > ul > li').text)
        model.close()
        self.assertEquals(1, model.protocol_document.generated_version)

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
            [
                'Close all proposals.',
                'Generate excerpts for all proposals.',
                # 'Update or create the protocol.',
            ],
            browser.css('#confirm_close_meeting > ul > li').text)
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
