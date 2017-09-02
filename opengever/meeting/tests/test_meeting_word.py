from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


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
