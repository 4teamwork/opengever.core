from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestDispositionByline(IntegrationTestCase):

    @browsing
    def test_shows_current_review_state_creation_and_modification_date(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition)

        self.assertEquals(
            ['Created: Aug 31, 2016 09:07 PM',
             'State: In progress',
             'Last modified: Aug 31, 2016 09:07 PM'],
            browser.css('#plone-document-byline li').text)
