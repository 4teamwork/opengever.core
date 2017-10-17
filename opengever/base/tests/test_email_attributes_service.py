from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestEmailAttributesService(IntegrationTestCase):

    @browsing
    def test_service_is_available_for_inbox(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox,
                     view='attributes',
                     headers={'Accept': 'application/json'})
        self.assertEquals({}, browser.json)
