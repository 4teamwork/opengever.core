from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestOGDefaultView(FunctionalTestCase):

    @browsing
    def tests_default_view_does_not_show_help_messages(self, browser):
        task = create(Builder('task'))
        browser.login().open(task, view='view')

        self.assertEquals([], browser.css('.formHelp'))
