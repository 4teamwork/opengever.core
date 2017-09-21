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
