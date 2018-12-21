from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase


class TestRegressionPloneformMacros(IntegrationTestCase):

    def setUp(self):
        super(TestRegressionPloneformMacros, self).setUp()

    @browsing
    def test_error_messages_are_displayed_for_form_groups(self, browser):
        self.login(self.regular_user, browser=browser)

        # make sure that only title is required
        # ensure that our assumption is correct, otherwise the regression
        # test won't work correctly
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'foo'})
        browser.find('Save').click()
        self.assertEqual(['Item created'], info_messages())

        # actually test that group-errors are displayed correctly
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        # fill invalid
        browser.fill({'Title': 'foo', 'Opening Date': 'invalid'})
        browser.find('Save').click()
        self.assertEqual([], info_messages())
        self.assertEqual(['There were some errors.'], error_messages())
