from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestTaskTemplateFolderByline(IntegrationTestCase):

    @browsing
    def test_shows_sequence_type(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.tasktemplatefolder)

        self.assertEquals(
            ['Type: Parallel'],
            browser.css('.documentByLine .sequence_type').text)
