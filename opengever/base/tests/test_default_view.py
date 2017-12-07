from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestOGDefaultView(IntegrationTestCase):

    @browsing
    def tests_default_view_does_not_show_help_messages(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.task, view='view')
        self.assertEquals([], browser.css('.formHelp'))
